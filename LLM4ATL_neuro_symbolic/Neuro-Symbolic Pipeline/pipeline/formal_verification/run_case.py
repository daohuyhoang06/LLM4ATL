#!/usr/bin/env python3
"""Run the formal-verification path for one ATL case study.

This script intentionally does not run the LLM pipeline or ATL_Tests. It only
performs:

    ATL transformation -> ATL2TM TransformationModel.ecore -> eFinder

The ATL2TM runtime creates a fresh work/output directory for the selected
case. eFinder then imports the matching external OCL profile and searches
``Sem AND Pre AND NOT Post_i``.

Examples (run from this directory or from the repository root)::

    python run_case.py --list
    python run_case.py --case Class2Interface_All
    python run_case.py --case Class2Interface_All --check Interface::InterfaceRetainsOperationsAndParameters
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


FORMAL_DIR = Path(__file__).resolve().parent
PIPELINE_DIR = FORMAL_DIR.parent
REPO_DIR = PIPELINE_DIR.parent.parent
MAPPING_FILE = PIPELINE_DIR / "mapping.json"
ATL_DIR = PIPELINE_DIR / "mtl_snippet" / "ATLAS_transformation_language" / "responses" / "ast2atl"
ATL2TM_ATL = FORMAL_DIR / "atl" / "transformations" / "ATL2TM.atl"
ATL2TM_RUNTIME = REPO_DIR / "ATL_Verification_Runtime"
ATL_TESTS = REPO_DIR / "ATL_Tests"
EFINDER_DIR = REPO_DIR / "efinder_validator"
EFINDER_CHECK = EFINDER_DIR / "efinder_check.py"
DEFAULT_OUTPUT = FORMAL_DIR / "output"


class Atl2TmUnsupported(RuntimeError):
    """The ATL2TM model contains an explicit unsupported-feature marker."""


def atl2tm_unsupported_markers(ecore: Path) -> list[str]:
    text = ecore.read_text(encoding="utf-8")
    markers = re.findall(r"__ATL2TM_UNSUPPORTED_[A-Z0-9_]+__", text)
    return list(dict.fromkeys(markers))


def write_atl2tm_status(case: str, output_ecore: Path, markers: list[str],
                        *, phase: str = "atl2tm-output-check",
                        detail: str | None = None) -> Path:
    result = output_ecore.parent / f"{case}_ATL2TM.result.json"
    result.write_text(json.dumps({
        "backend": "atl2tm",
        "status": "ATL2TM_UNSUPPORTED_FEATURE",
        "phase": phase,
        "ecore": str(output_ecore.resolve()),
        "features": markers,
        "detail": detail or "ATL2TM generated unsupported-feature marker(s); eFinder was not started."
    }, indent=2) + "\n", encoding="utf-8")
    return result


def load_cases() -> dict[str, list[str]]:
    with MAPPING_FILE.open(encoding="utf-8") as stream:
        mapping = json.load(stream)
    if not isinstance(mapping, dict):
        raise ValueError(f"mapping must be a JSON object: {MAPPING_FILE}")
    return mapping


def maven_command() -> str:
    configured = os.environ.get("MAVEN_CMD")
    if configured:
        return configured
    return "mvn.cmd" if os.name == "nt" else "mvn"


def maven_environment() -> dict[str, str]:
    """Give Maven's nested ATL compiler access to Windows' certificate store."""
    environment = os.environ.copy()
    if os.name == "nt":
        options = environment.get("MAVEN_OPTS", "")
        if "trustStoreType" not in options:
            options = (options + " "
                       + "-Djavax.net.ssl.trustStoreType=Windows-ROOT"
                       + " -Djavax.net.ssl.trustStore=NONE").strip()
            environment["MAVEN_OPTS"] = options
    return environment


def quoted_exec_arg(value: Path) -> str:
    """Quote one path for Maven Exec's ``exec.args`` property."""
    return '"' + str(value.resolve()).replace('"', '\\"') + '"'


def resolve_case(case: str, mapping: dict[str, list[str]]) -> tuple[Path, Path, Path]:
    if case not in mapping:
        available = ", ".join(sorted(mapping))
        raise ValueError(f"unknown case {case!r}; available cases: {available}")
    metamodels = mapping[case]
    if len(metamodels) != 2:
        raise ValueError(f"case {case} must have exactly source and target Ecore paths")

    atl = ATL_DIR / f"{case}.atl"
    source = PIPELINE_DIR / metamodels[0]
    target = PIPELINE_DIR / metamodels[1]
    for path in (atl, source, target, ATL2TM_ATL):
        if not path.is_file():
            raise FileNotFoundError(f"required formal-verification input not found: {path}")
    return atl, source, target


def run_atl2tm(case: str, atl: Path, source: Path, target: Path,
               output_ecore: Path, work_dir: Path) -> None:
    """Invoke ATL2TMRunnerMain through the runtime Maven project."""
    work_dir.mkdir(parents=True, exist_ok=True)
    output_ecore.parent.mkdir(parents=True, exist_ok=True)
    exec_args = " ".join(quoted_exec_arg(path) for path in (
        atl, source, target, ATL2TM_ATL, work_dir, output_ecore
    ))
    command = [
        maven_command(),
        "-q",
        "-f", str((ATL2TM_RUNTIME / "pom.xml").resolve()),
        "exec:java",
        f"-Datl.compiler.project={ATL_TESTS.resolve()}",
        f"-Dexec.args={exec_args}",
    ]
    print("[1/2] ATL -> ATL2TM", flush=True)
    print("      input :", atl, flush=True)
    print("      output:", output_ecore, flush=True)
    completed = subprocess.run(
        command, cwd=ATL2TM_RUNTIME, env=maven_environment(), text=True,
        capture_output=True
    )
    if completed.stdout:
        print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n")
    if completed.stderr:
        print(completed.stderr, end="" if completed.stderr.endswith("\n") else "\n",
              file=sys.stderr)
    runner_output = (completed.stdout or "") + "\n" + (completed.stderr or "")
    # Maven Exec may translate the Java process' exit code 3 to 1. The runner
    # result token, not Maven's wrapper exit value, is the reliable signal.
    if completed.returncode != 0 and "RESULT:UNSUPPORTED" in runner_output:
        features = ["RECURSIVE_HELPER"] if "Recursive ATL helper" in runner_output else ["RUNNER_REPORTED_FEATURE"]
        reason = next((line.strip() for line in (completed.stderr or "").splitlines()
                       if line.strip()), "ATL2TM runner reported an unsupported feature.")
        result = write_atl2tm_status(
            case, output_ecore, features,
            phase="atl2tm-runner",
            detail=reason + " eFinder was not started."
        )
        raise Atl2TmUnsupported(
            "unsupported ATL2TM feature(s): " + ", ".join(features)
            + f"; eFinder skipped; report: {result}"
        )
    if completed.returncode != 0 or not output_ecore.is_file():
        raise RuntimeError(
            "ATL2TM failed or did not create the output Ecore "
            f"(exit={completed.returncode}): {output_ecore}"
        )
    markers = atl2tm_unsupported_markers(output_ecore)
    if markers:
        result = write_atl2tm_status(case, output_ecore, markers)
        raise Atl2TmUnsupported(
            "unsupported ATL2TM feature(s): " + ", ".join(markers)
            + f"; eFinder skipped; report: {result}"
        )


def run_efinder(case: str, atl2tm_ecore: Path, constraints: Path,
                out_dir: Path, check: str | None, scope: int,
                reference_scope: int, timeout_ms: int) -> int:
    if not EFINDER_CHECK.is_file():
        raise FileNotFoundError(f"eFinder wrapper not found: {EFINDER_CHECK}")
    if not constraints.exists():
        raise FileNotFoundError(f"constraint profile not found: {constraints}")

    command = [
        sys.executable,
        str(EFINDER_CHECK),
        str(atl2tm_ecore),
        "--constraints", str(constraints),
        "--out-dir", str(out_dir),
        "--scope", str(scope),
        "--reference-scope", str(reference_scope),
        "--timeout-ms", str(timeout_ms),
    ]
    if check:
        command.extend(["--check", check])
    else:
        command.append("--check-all")

    print("[2/2] ATL2TM -> eFinder", flush=True)
    print("      profile:", constraints, flush=True)
    print("      result :", out_dir, flush=True)
    completed = subprocess.run(command, cwd=EFINDER_DIR, text=True)
    return completed.returncode


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", help="case-study name from pipeline/mapping.json")
    parser.add_argument("--list", action="store_true", help="list available case studies")
    parser.add_argument("--atl", type=Path,
                        help="override the generated ATL file for the selected case")
    parser.add_argument("--source", type=Path, help="override source Ecore")
    parser.add_argument("--target", type=Path, help="override target Ecore")
    checks = parser.add_mutually_exclusive_group()
    checks.add_argument("--check", metavar="EClass::constraint",
                        help="run one target postcondition")
    checks.add_argument("--check-all", action="store_true",
                        help="run all target postconditions in the profile (default)")
    parser.add_argument("--constraints", type=Path,
                        help="override the external OCL profile directory/file")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help="formal-verification output directory")
    parser.add_argument("--scope", type=int, default=3)
    parser.add_argument("--reference-scope", type=int, default=6)
    parser.add_argument("--timeout-ms", type=int, default=300_000)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    mapping = load_cases()
    if args.list:
        for case in sorted(mapping):
            print(case)
        return 0
    if not args.case:
        raise ValueError("--case is required unless --list is used")
    if args.scope < 1 or args.reference_scope < 0 or args.timeout_ms < 1:
        raise ValueError("scope >= 1, reference-scope >= 0, timeout-ms >= 1 are required")

    default_atl, default_source, default_target = resolve_case(args.case, mapping)
    atl = (args.atl or default_atl).resolve()
    source = (args.source or default_source).resolve()
    target = (args.target or default_target).resolve()
    for path in (atl, source, target):
        if not path.is_file():
            raise FileNotFoundError(f"input file not found: {path}")

    case_output = args.output.resolve() / args.case
    output_ecore = case_output / f"{args.case}_ATL2TM.ecore"
    work_dir = case_output / "atl2tm-work"
    constraints = (args.constraints or (FORMAL_DIR / "constraints" / args.case)).resolve()
    efinder_output = case_output / "efinder"

    run_atl2tm(args.case, atl, source, target, output_ecore, work_dir)
    return run_efinder(
        args.case, output_ecore, constraints, efinder_output, args.check,
        args.scope, args.reference_scope, args.timeout_ms
    )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Atl2TmUnsupported as error:
        print(f"ATL2TM_UNSUPPORTED_FEATURE: {error}", file=sys.stderr)
        raise SystemExit(3)
    except (FileNotFoundError, RuntimeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)

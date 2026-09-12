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
from dataclasses import dataclass
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


class Atl2TmExecutionError(RuntimeError):
    """ATL2TM failed with a concise message and a path to the full log."""


@dataclass(frozen=True)
class Layer3Result:
    """Machine-readable outcome consumed by the LLM pipeline.

    ``COUNTEREXAMPLE`` is the only non-success outcome which should be sent
    back to the LLM for another attempt.  The other outcomes mean that the
    formal backend could not provide a sound verdict for this candidate.
    """

    status: str
    detail: str
    feedback: str = ""
    report: Path | None = None


EFINDER_STOP_STATUSES = {
    "UNSUPPORTED_FEATURE",
    "INVALID_TRANSLATION",
    "OCL_PARSE_ERROR",
    "EFINDER_TRANSLATION_ERROR",
    "SOLVER_ERROR",
    "RUNTIME_DEPENDENCY_ERROR",
    "ERROR",
}


def atl2tm_unsupported_markers(ecore: Path) -> list[str]:
    text = ecore.read_text(encoding="utf-8")
    markers = re.findall(r"__ATL2TM_UNSUPPORTED_[A-Z0-9_]+__", text)
    return list(dict.fromkeys(markers))


def describe_atl2tm_features(features: list[str]) -> str:
    """Convert backend marker names into a stable user-facing diagnostic."""
    descriptions = {
        "LAZY_RULE": "ATL2TM chưa hỗ trợ lazy rule",
        "RECURSIVE_HELPER": "ATL2TM chưa hỗ trợ helper đệ quy",
        "__ATL2TM_UNSUPPORTED_FEATURE__RULE_CALL__":
            "ATL2TM chưa hỗ trợ gọi rule qua thisModule (lazy/called rule)",
        "__ATL2TM_UNSUPPORTED_FEATURE__RESOLVE_TEMP__":
            "ATL2TM chưa hỗ trợ resolveTemp",
        "__ATL2TM_UNSUPPORTED_FEATURE__HELPER_ATTRIBUTE__":
            "ATL2TM chưa hỗ trợ thuộc tính helper dạng này",
        "__ATL2TM_UNSUPPORTED_EXPRESSION__":
            "ATL2TM chưa hỗ trợ một biểu thức ATL/OCL",
        "RUNNER_REPORTED_FEATURE": "ATL2TM báo có cấu trúc chưa được hỗ trợ",
    }
    return "; ".join(descriptions.get(feature, feature) for feature in features)


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
               output_ecore: Path, work_dir: Path, *, verbose: bool = True) -> None:
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
        # ATLModelLoader's public signature uses ATL's compile API (IModel).
        # Keep that API available to the Maven exec launcher.
        "-Dexec.classpathScope=compile",
        f"-Datl.compiler.project={ATL_TESTS.resolve()}",
        f"-Dexec.args={exec_args}",
    ]
    if verbose:
        print("[1/2] ATL -> ATL2TM", flush=True)
        print("      input :", atl, flush=True)
        print("      output:", output_ecore, flush=True)
    completed = subprocess.run(
        command, cwd=ATL2TM_RUNTIME, env=maven_environment(), text=True,
        capture_output=True
    )
    if verbose and completed.stdout:
        print(completed.stdout, end="" if completed.stdout.endswith("\n") else "\n")
    if verbose and completed.stderr:
        print(completed.stderr, end="" if completed.stderr.endswith("\n") else "\n",
              file=sys.stderr)
    runner_output = (completed.stdout or "") + "\n" + (completed.stderr or "")
    # Maven Exec may translate the Java process' exit code 3 to 1. The runner
    # result token, not Maven's wrapper exit value, is the reliable signal.
    if completed.returncode != 0 and "RESULT:UNSUPPORTED" in runner_output:
        lower_output = runner_output.lower()
        if "lazy rule" in lower_output:
            features = ["LAZY_RULE"]
        elif "recursive atl helper" in lower_output:
            features = ["RECURSIVE_HELPER"]
        else:
            features = ["RUNNER_REPORTED_FEATURE"]
        detail = (
            describe_atl2tm_features(features)
            + "; Layer 3 đã dừng, eFinder không được chạy."
        )
        result = write_atl2tm_status(
            case, output_ecore, features,
            phase="atl2tm-runner",
            detail=detail,
        )
        raise Atl2TmUnsupported(detail)
    if completed.returncode != 0 or not output_ecore.is_file():
        log_path = output_ecore.with_suffix(".atl2tm.log")
        log_path.write_text(runner_output, encoding="utf-8", errors="replace")
        raise Atl2TmExecutionError(
            _summarize_atl2tm_failure(runner_output, log_path)
        )
    markers = atl2tm_unsupported_markers(output_ecore)
    if markers:
        result = write_atl2tm_status(case, output_ecore, markers)
        raise Atl2TmUnsupported(
            describe_atl2tm_features(markers)
            + "; Layer 3 đã dừng, eFinder không được chạy."
        )


def _summarize_atl2tm_failure(output: str, log_path: Path) -> str:
    """Turn an ATL VM stack trace into actionable pipeline feedback.

    The complete Maven/Java output remains available in ``log_path``; this
    function deliberately keeps normal pipeline output to one useful sentence.
    """
    missing_atl = re.search(r"ATL file not found:\s*([^\r\n]+)", output)
    if missing_atl:
        summary = (
            "Không tìm thấy ATL đầu vào '"
            + Path(missing_atl.group(1).strip()).name
            + "'. Hãy tạo hoặc lưu ATL trước khi chạy Layer 3."
        )
    elif "Unable to access elements on OclUndefined" in output:
        rule = re.search(r"local variables:.*?r=IN!([A-Za-z_][A-Za-z0-9_]*)", output)
        rule_name = rule.group(1) if rule else "một rule"
        summary = (
            f"ATL2TM không đọc được out-pattern của rule '{rule_name}'. "
            "Kiểm tra phần 'to' của rule và tránh dùng ATL/OCL keyword làm tên biến."
        )
    elif "ATL parsing failed" in output or "ATLParseException" in output:
        summary = "ATL đầu vào không parse được. Kiểm tra cú pháp và các identifier reserved."
    else:
        exception = re.search(r"(?:Exception|Error):\s*([^\r\n]+)", output)
        summary = (
            "ATL2TM thực thi thất bại: "
            + (exception.group(1).strip() if exception else "không tạo được Ecore đầu ra")
        )

    return f"{summary} Chi tiết trong {log_path.name}."


def run_efinder(case: str, atl2tm_ecore: Path, constraints: Path,
                out_dir: Path, check: str | None, scope: int,
                reference_scope: int, timeout_ms: int, *, verbose: bool = True) -> int:
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

    if verbose:
        print("[2/2] ATL2TM -> eFinder", flush=True)
        print("      profile:", constraints, flush=True)
        print("      result :", out_dir, flush=True)
    completed = subprocess.run(
        command, cwd=EFINDER_DIR, text=True,
        capture_output=not verbose,
    )
    return completed.returncode


def _postcondition_text(constraints: Path, check: str) -> str:
    """Return the relevant OCL property as useful, bounded LLM feedback."""
    if "::" not in check or not constraints.is_dir():
        return ""
    context, name = check.split("::", 1)
    pattern = re.compile(
        rf"(?ms)^\s*context\s+{re.escape(context)}\s+"
        rf"inv\s+{re.escape(name)}\s*:\s*(.*?)(?=^\s*(?:context|global)\s+|\Z)"
    )
    for profile in sorted(constraints.glob("*.ocl")):
        match = pattern.search(profile.read_text(encoding="utf-8"))
        if match:
            # Avoid growing the next LLM prompt without bound if a profile is
            # later extended with a large explanatory comment.
            expression = match.group(1).strip()
            return expression[:2_000]
    return ""


def _counterexample_feedback(checks: list[dict], constraints: Path) -> str:
    lines = [
        "LAYER 3 FORMAL VERIFICATION FAILED: eFinder found a bounded "
        "counterexample for the generated ATL.",
        "The checked formula is Sem AND Pre AND NOT Post_i. Repair the AST "
        "so the generated ATL satisfies every property below; return JSON only.",
    ]
    for result in checks:
        check = str(result.get("check", "unknown constraint"))
        lines.append(f"- Violated postcondition `{check}`.")
        property_text = _postcondition_text(constraints, check)
        if property_text:
            lines.append(f"  Required OCL: {property_text}")
        witness = result.get("counterexample_file")
        if witness:
            witness_path = Path(str(witness))
            try:
                witness_text = witness_path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                witness_text = ""
            if witness_text:
                # The XMI is the most actionable part of a SAT result, but a
                # malformed/very large witness must not consume the whole
                # retry prompt. Keep the complete path above for inspection.
                limit = 12_000
                truncated = len(witness_text) > limit
                lines.append("  Counterexample XMI (use this witness to repair the AST):")
                lines.append("```xml")
                lines.append(witness_text[:limit])
                if truncated:
                    lines.append("<!-- witness truncated by pipeline -->")
                lines.append("```")
            else:
                lines.append("  Counterexample XMI is unavailable to the pipeline.")
        detail = str(result.get("detail", "")).strip()
        if detail:
            lines.append(f"  Verifier detail: {detail[:1_000]}")
    return "\n".join(lines)


def verify_atl_for_pipeline(
        case: str, atl: Path, source: Path, target: Path, *,
        output_root: Path, scope: int = 3, reference_scope: int = 6,
        timeout_ms: int = 300_000, verbose: bool = False,
) -> Layer3Result:
    """Run ATL2TM then eFinder and normalize their outcomes for Layer 3.

    The CLI remains available for manual use.  This entry point is deliberately
    non-throwing for expected verifier outcomes, so callers never mistake an
    unsupported formal feature for an LLM-correctable transformation error.
    """
    case_output = output_root.resolve() / case
    output_ecore = case_output / f"{case}_ATL2TM.ecore"
    work_dir = case_output / "atl2tm-work"
    constraints = (FORMAL_DIR / "constraints" / case).resolve()
    efinder_output = case_output / "efinder"

    if not constraints.is_dir():
        return Layer3Result(
            "LAYER3_CONFIGURATION_ERROR",
            f"LAYER3_CONFIG_ERROR: Không tìm thấy bộ ràng buộc formal cho {case}. "
            "Layer 3 đã dừng; LLM không được retry.",
        )

    try:
        if verbose:
            print("[Layer 3] Đang chuyển ATL -> ATL2TM...", flush=True)
        run_atl2tm(case, atl, source, target, output_ecore, work_dir, verbose=verbose)
        if verbose:
            print("[Layer 3] Đã tạo ATL -> ATL2TM thành công.", flush=True)
    except Atl2TmUnsupported as error:
        report = output_ecore.parent / f"{case}_ATL2TM.result.json"
        if not report.is_file():
            report = write_atl2tm_status(
                case,
                output_ecore,
                ["ATL2TM_UNSUPPORTED_FEATURE"],
                phase="atl2tm-runner",
                detail=str(error),
            )
        return Layer3Result(
            "ATL2TM_UNSUPPORTED_FEATURE",
            str(error),
            report=report,
        )
    except Atl2TmExecutionError as error:
        return Layer3Result(
            "ATL2TM_ERROR",
            "ATL2TM_ERROR: " + str(error)
            + " Layer 3 đã dừng; LLM không được retry.",
        )
    except (FileNotFoundError, RuntimeError) as error:
        return Layer3Result(
            "ATL2TM_ERROR",
            "ATL2TM_ERROR: Không thể hoàn thành chuyển ATL -> ATL2TM. "
            "Layer 3 đã dừng; LLM không được retry.",
        )

    try:
        if verbose:
            print("[Layer 3] Đang chạy eFinder...", flush=True)
        exit_code = run_efinder(
            case, output_ecore, constraints, efinder_output, None, scope,
            reference_scope, timeout_ms, verbose=verbose,
        )
    except (FileNotFoundError, RuntimeError) as error:
        return Layer3Result(
            "EFINDER_ERROR",
            "EFINDER_ERROR: Không thể khởi động eFinder. "
            "Layer 3 đã dừng; LLM không được retry.",
        )

    report = efinder_output / f"{output_ecore.stem}.all.result.json"
    if exit_code != 0 or not report.is_file():
        return Layer3Result(
            "EFINDER_ERROR",
            f"EFINDER_ERROR: eFinder không tạo được kết quả kiểm tra (exit={exit_code}). "
            "Layer 3 đã dừng; LLM không được retry.",
            report=report if report.is_file() else None,
        )
    try:
        summary = json.loads(report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return Layer3Result(
            "EFINDER_ERROR",
            "EFINDER_ERROR: Kết quả eFinder không đọc được. "
            "Layer 3 đã dừng; LLM không được retry.",
            report=report,
        )

    checks = summary.get("checks", [])
    if summary.get("status") != "BATCH_COMPLETED" or not isinstance(checks, list) or not checks:
        return Layer3Result(
            "EFINDER_NO_CHECKS",
            f"EFINDER_NO_CHECKS: eFinder không tìm thấy postcondition cần kiểm tra "
            f"(status={summary.get('status')!r}). Layer 3 đã dừng; LLM không được retry.",
            report=report,
        )

    stopped = [item for item in checks if item.get("status") in EFINDER_STOP_STATUSES]
    if stopped:
        unsupported = [item for item in stopped if item.get("status") == "UNSUPPORTED_FEATURE"]
        diagnostics = []
        for item in stopped:
            check_name = str(item.get("check", "unknown constraint"))
            status = str(item.get("status", "ERROR"))
            detail = str(item.get("detail", "")).strip()
            if detail:
                diagnostics.append(f"{check_name}: {detail[:1_000]}")
            else:
                diagnostics.append(f"{check_name} ({status})")
        if unsupported:
            message = "eFinder chưa hỗ trợ feature trong ràng buộc: " + "; ".join(diagnostics)
            status = "EFINDER_UNSUPPORTED_FEATURE"
        else:
            message = "eFinder không thể kiểm tra an toàn: " + "; ".join(diagnostics)
            status = "EFINDER_UNSUPPORTED_OR_ERROR"
        return Layer3Result(
            status,
            message + ". Layer 3 đã dừng; LLM không được retry.",
            report=report,
        )

    counterexamples = [item for item in checks if item.get("status") == "SAT"]
    if counterexamples:
        return Layer3Result(
            "COUNTEREXAMPLE",
            "eFinder found " + str(len(counterexamples))
            + " bounded counterexample(s); the LLM will receive the violated postcondition(s).",
            feedback=_counterexample_feedback(counterexamples, constraints),
            report=report,
        )

    unexpected = [item for item in checks if item.get("status") != "UNSAT"]
    if unexpected:
        statuses = ", ".join(
            f"{item.get('check', 'unknown')}={item.get('status', 'missing')}"
            for item in unexpected
        )
        return Layer3Result(
            "EFINDER_ERROR",
            "EFINDER_ERROR: eFinder trả về trạng thái không nhận diện được: " + statuses
            + ". Layer 3 đã dừng; LLM không được retry.",
            report=report,
        )

    return Layer3Result(
        "VERIFIED",
        f"eFinder found no bounded counterexample for {len(checks)} postcondition(s).",
        report=report,
    )


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

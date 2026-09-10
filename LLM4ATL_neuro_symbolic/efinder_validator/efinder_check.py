#!/usr/bin/env python3
"""Run the packaged headless EFinder counterexample backend.

The wrapper invokes the Equinox product assembled by the local Tycho build.
No Eclipse IDE installation or manually managed JAR classpath is required.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from xml.etree import ElementTree

HERE = Path(__file__).resolve().parent
DEFAULT_OUT = HERE / "output"
PRODUCT_DIR = (HERE / "runtime" / "headless-product" / "target" / "products"
               / "org.llm4atl.efinder.headless")
PROVENANCE_SOURCE = "urn:llm4atl:provenance"
ECORE_SOURCE = "http://www.eclipse.org/emf/2002/Ecore"


def result_paths(ecore: Path, check: str, out_dir: Path) -> tuple[Path, Path]:
    context, constraint = check.split("::", 1)
    stem = f"{ecore.stem}__{context}__{constraint}"
    return out_dir / f"{stem}.result.json", out_dir / f"{stem}.counterexample.xmi"


def default_launcher() -> Path:
    if sys.platform.startswith("win"):
        return PRODUCT_DIR / "win32" / "win32" / "x86_64" / "efinder-validator.exe"
    if sys.platform == "darwin":
        return PRODUCT_DIR / "macosx" / "cocoa" / "x86_64" / "efinder-validator"
    return PRODUCT_DIR / "linux" / "gtk" / "x86_64" / "efinder-validator"


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _annotation(classifier, source: str):
    return next((node for node in classifier if _local_name(node.tag) == "eAnnotations"
                 and node.get("source") == source), None)


def _detail(annotation, key: str) -> str:
    if annotation is None:
        return ""
    for node in annotation:
        if _local_name(node.tag) == "details" and node.get("key") == key:
            return node.get("value", "")
    return ""


def discover_checks(ecore: Path) -> list[str]:
    """Return ATL2TM target postconditions, or all plain Ecore constraints."""
    root = ElementTree.parse(ecore).getroot()
    classifiers = [node for node in root.iter() if _local_name(node.tag) == "eClassifiers"]
    atl2tm = any(_annotation(node, PROVENANCE_SOURCE) is not None for node in classifiers)
    checks: list[str] = []
    for classifier in classifiers:
        name = classifier.get("name")
        if not name:
            continue
        provenance = _annotation(classifier, PROVENANCE_SOURCE)
        ecore_annotation = _annotation(classifier, ECORE_SOURCE)
        if atl2tm:
            names = _detail(provenance, "postConstraints").split()
        else:
            names = _detail(ecore_annotation, "constraints").split()
        checks.extend(f"{name}::{constraint}" for constraint in names)
    return checks


def accepted_status(status: str) -> bool:
    return status in {
        "SAT", "UNSAT", "UNSUPPORTED_FEATURE", "INVALID_TRANSLATION",
        "OCL_PARSE_ERROR", "EFINDER_TRANSLATION_ERROR", "SOLVER_ERROR",
        "RUNTIME_DEPENDENCY_ERROR"
    }


def run_one(args, check: str) -> tuple[dict, int]:
    result_json, witness_xmi = result_paths(args.ecore, check, args.out_dir)
    # Never mistake a result from an earlier invocation for the current run.
    result_json.unlink(missing_ok=True)
    witness_xmi.unlink(missing_ok=True)
    java_args = [
        "--ecore", str(args.ecore.resolve()),
        "--check", check,
        "--out-dir", str(args.out_dir.resolve()),
        "--result-json", str(result_json.resolve()),
        "--scope", str(args.scope),
        "--reference-scope", str(args.reference_scope),
        "--timeout-ms", str(args.timeout_ms),
    ]
    command = [str(args.launcher), "-nosplash"] + java_args
    if args.console_log:
        command.insert(1, "-consoleLog")
    completed = subprocess.run(command, text=True, capture_output=True,
                               cwd=args.launcher.parent)
    if result_json.is_file():
        result = json.loads(result_json.read_text(encoding="utf-8"))
        if args.console_log and (completed.stdout or completed.stderr):
            print((completed.stdout + "\n" + completed.stderr).strip(), file=sys.stderr)
        return result, 0 if accepted_status(result.get("status", "")) else 1

    detail = (completed.stdout + "\n" + completed.stderr).strip()
    result = {
        "backend": "efinder",
        "status": "ERROR",
        "ecore": str(args.ecore),
        "check": check,
        "detail": detail[-4000:],
    }
    return result, completed.returncode or 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ecore", type=Path, help="ATL2TM-generated .ecore transformation model")
    checks = parser.add_mutually_exclusive_group(required=True)
    checks.add_argument("--check", metavar="EClass::constraint",
                        help="one Pivot OCL constraint to negate and search")
    checks.add_argument("--check-all", action="store_true",
                        help="check every ATL2TM target postConstraint")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--scope", type=int, default=3, help="maximum instances per EClass")
    parser.add_argument("--reference-scope", type=int, default=6,
                        help="maximum links per EReference")
    parser.add_argument("--timeout-ms", type=int, default=300_000)
    parser.add_argument("--launcher", type=Path, default=default_launcher(),
                        help="path to the packaged EFinder product launcher")
    parser.add_argument("--console-log", action="store_true",
                        help="show Maven/Java diagnostics")
    args = parser.parse_args(argv)

    if not args.ecore.is_file():
        parser.error(f"not found: {args.ecore}")
    if args.scope < 1 or args.reference_scope < 0 or args.timeout_ms < 1:
        parser.error("scope >= 1, reference-scope >= 0, and timeout-ms >= 1 are required")
    if not args.launcher.is_file():
        parser.error("headless EFinder product not found: " + str(args.launcher)
                     + "; build it first with: cd runtime; "
                     + "$target=(Resolve-Path .\\target-platform\\efinder-headless.target).Path; "
                     + "mvn.cmd -f pom.xml \"-Definder.headless.target=$target\" package -DskipTests")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    if not args.check_all:
        if "::" not in args.check or not all(args.check.split("::", 1)):
            parser.error("--check must be EClass::constraint")
        result, returncode = run_one(args, args.check)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return returncode

    discovered = discover_checks(args.ecore)
    if not discovered:
        summary = {
            "backend": "efinder",
            "status": "NO_POSTCONSTRAINTS",
            "ecore": str(args.ecore.resolve()),
            "checks": [],
            "detail": "No target postConstraints were found in the ATL2TM provenance annotation"
        }
    else:
        results = []
        for check in discovered:
            result, _ = run_one(args, check)
            results.append(result)
        statuses = {}
        for result in results:
            status = result.get("status", "ERROR")
            statuses[status] = statuses.get(status, 0) + 1
        summary = {
            "backend": "efinder",
            "status": "BATCH_COMPLETED",
            "verification_formula": "Sem AND Pre AND NOT Post_i",
            "ecore": str(args.ecore.resolve()),
            "checks": results,
            "counts": statuses,
        }
    aggregate = args.out_dir / f"{args.ecore.stem}.all.result.json"
    aggregate.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

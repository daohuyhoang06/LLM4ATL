#!/usr/bin/env python3
"""Run the packaged headless EFinder counterexample backend.

The wrapper invokes the Equinox product assembled by the local Tycho build.
No Eclipse IDE installation or manually managed JAR classpath is required.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from xml.etree import ElementTree

HERE = Path(__file__).resolve().parent
DEFAULT_OUT = HERE / "output"
PRODUCT_DIR = (HERE / "runtime" / "headless-product" / "target" / "products"
               / "org.llm4atl.efinder.headless")
PROVENANCE_SOURCE = "urn:llm4atl:provenance"
ECORE_SOURCE = "http://www.eclipse.org/emf/2002/Ecore"
EXTERNAL_INVARIANT = re.compile(
    r"(?ms)^\s*context\s+(?:[A-Za-z_][A-Za-z0-9_]*::)?([A-Za-z_][A-Za-z0-9_]*)"
    r"\s+inv\s+([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*?)(?=^\s*(?:context|global)\s+|\Z)"
)
EXTERNAL_GLOBAL_INVARIANT = re.compile(
    r"(?ms)^\s*global\s+inv\s+([A-Za-z_][A-Za-z0-9_]*)\s*:\s*"
    r"(.*?)(?=^\s*(?:context|global)\s+|\Z)"
)


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


def _external_checks(location: Path) -> list[str]:
    """Return ``EClass::invariant`` entries declared in one OCL file/folder."""
    files = sorted(location.rglob("*.ocl")) if location.is_dir() else [location]
    if not files:
        raise ValueError(f"no .ocl files found in constraints path: {location}")
    checks: list[str] = []
    for file in files:
        if not file.is_file() or file.suffix.lower() != ".ocl":
            raise ValueError(f"constraints input must be an .ocl file or folder: {file}")
        text = file.read_text(encoding="utf-8")
        matches = list(EXTERNAL_INVARIANT.finditer(text))
        global_matches = list(EXTERNAL_GLOBAL_INVARIANT.finditer(text))
        if global_matches and file.name.lower() != "source-pre.ocl":
            raise ValueError("global invariants are allowed only in source-pre.ocl: " + str(file))
        if not matches and not global_matches:
            raise ValueError("no supported 'context <EClass> inv <name>:' or 'global inv <name>:' declaration in " + str(file))
        # source-pre.ocl constrains the premise only; it must never become a
        # selectable Post_i query for --check-all.
        if file.name.lower() != "source-pre.ocl":
            checks.extend(f"{match.group(1)}::{match.group(2)}" for match in matches)
    return checks


def discover_checks(ecore: Path, constraints: Path | None = None) -> list[str]:
    """Return selectable checks, including optional external target OCL."""
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
            # Schema-v2 transformation models persist role-qualified names
            # (for example Step__target). Keep the CLI/profile vocabulary on
            # the original metamodel name, which provenance preserves.
            name = _detail(provenance, "originalName") or name
        else:
            names = _detail(ecore_annotation, "constraints").split()
        checks.extend(f"{name}::{constraint}" for constraint in names)
    if constraints is not None:
        checks.extend(_external_checks(constraints))
    unsupported = set(discover_unsupported_primitive_multiplicities(ecore))
    return [check for check in dict.fromkeys(checks) if check not in unsupported]


def discover_unsupported_primitive_multiplicities(ecore: Path) -> list[str]:
    """Return primitive target-multiplicity checks intentionally skipped.

    New ATL2TM models advertise these in provenance.  The EAttribute scan also
    recognizes older generated models, whose primitive multiplicities were
    still present in ``postConstraints``.
    """
    root = ElementTree.parse(ecore).getroot()
    checks: list[str] = []
    for classifier in (node for node in root.iter()
                       if _local_name(node.tag) == "eClassifiers"):
        provenance = _annotation(classifier, PROVENANCE_SOURCE)
        if _detail(provenance, "origin") != "target":
            continue
        context = _detail(provenance, "originalName") or classifier.get("name", "")
        if not context:
            continue
        names = set(_detail(provenance,
                            "unsupportedPrimitiveTargetMultiplicityConstraints").split())
        post_constraints = set(_detail(provenance, "postConstraints").split())
        for feature in classifier:
            if _local_name(feature.tag) != "eStructuralFeatures":
                continue
            feature_type = (feature.get("xsi:type")
                            or feature.get("{http://www.w3.org/2001/XMLSchema-instance}type", ""))
            if not feature_type.endswith("EAttribute"):
                continue
            feature_name = feature.get("name", "")
            constraint = f"targetMultiplicity_{context}_{feature_name}"
            if constraint in post_constraints:
                names.add(constraint)
        checks.extend(f"{context}::{name}" for name in names)
    return list(dict.fromkeys(checks))


def accepted_status(status: str) -> bool:
    return status in {
        "SAT", "UNSAT", "UNSUPPORTED_FEATURE", "INVALID_TRANSLATION",
        "OCL_PARSE_ERROR", "EFINDER_TRANSLATION_ERROR", "SOLVER_ERROR",
        "RUNTIME_DEPENDENCY_ERROR"
    }


def _wait_for_result_file(result_json: Path, timeout_seconds: float = 10.0) -> bool:
    """Wait for the Eclipse launcher child to finish writing its result.

    On Windows the packaged launcher can return before its Java child has
    flushed ``--result-json``. Without this small synchronization window the
    wrapper incorrectly reports a successful eFinder query as ``ERROR``.
    """
    deadline = time.monotonic() + timeout_seconds
    while not result_json.is_file() and time.monotonic() < deadline:
        time.sleep(0.1)
    return result_json.is_file()


def _result_from_launcher_output(output: str) -> dict | None:
    """Recover the Java result when Equinox exits before flushing its file.

    The Windows launcher occasionally returns while the child has already
    printed its JSON result but has not yet completed ``--result-json``. Look
    for the last decodable object carrying a machine-readable status instead
    of turning a valid SAT/UNSAT result into a spurious ERROR.
    """
    decoder = json.JSONDecoder()
    candidates: list[dict] = []
    for index, char in enumerate(output):
        if char != "{":
            continue
        try:
            value, _ = decoder.raw_decode(output, index)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and isinstance(value.get("status"), str):
            candidates.append(value)
    return candidates[-1] if candidates else None


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
    if args.constraints is not None:
        java_args.extend(["--constraints", str(args.constraints.resolve())])
    command = [str(args.launcher), "-nosplash"] + java_args
    if args.console_log:
        command.insert(1, "-consoleLog")
    completed = subprocess.run(command, text=True, capture_output=True,
                               cwd=args.launcher.parent)
    _wait_for_result_file(result_json)
    if result_json.is_file():
        raw_result = result_json.read_text(encoding="utf-8")
        try:
            result = json.loads(raw_result)
        except json.JSONDecodeError as error:
            # Older EFinder builds may write backend diagnostics containing
            # raw control characters into the JSON detail field. Preserve the
            # useful classification instead of crashing the batch wrapper.
            diagnostic = raw_result
            unsupported = "not supported" in diagnostic.lower()
            result = {
                "backend": "efinder",
                "status": "UNSUPPORTED_FEATURE" if unsupported
                         else "EFINDER_TRANSLATION_ERROR",
                "ecore": str(args.ecore),
                "check": check,
                "detail": (
                    "Malformed backend result JSON at character "
                    + str(error.pos) + "; raw diagnostic: "
                    + diagnostic[-4000:]
                ),
            }
        if args.console_log and (completed.stdout or completed.stderr):
            print((completed.stdout + "\n" + completed.stderr).strip(), file=sys.stderr)
        return result, 0 if accepted_status(result.get("status", "")) else 1

    launcher_result = _result_from_launcher_output(
        (completed.stdout or "") + "\n" + (completed.stderr or "")
    )
    if launcher_result is not None:
        launcher_result.setdefault("backend", "efinder")
        launcher_result.setdefault("ecore", str(args.ecore))
        launcher_result.setdefault("check", check)
        if args.console_log:
            print("Recovered eFinder result from launcher output.", file=sys.stderr)
        return launcher_result, 0 if accepted_status(launcher_result.get("status", "")) else 1

    detail = (completed.stdout + "\n" + completed.stderr).strip()
    result = {
        "backend": "efinder",
        "status": "ERROR",
        "ecore": str(args.ecore),
        "check": check,
        "detail": detail[-4000:],
    }
    return result, completed.returncode or 1


def skipped_primitive_multiplicity_result(args, check: str) -> tuple[dict, int]:
    """Persist an explicit result instead of sending an unsound query to USE."""
    result_json, witness_xmi = result_paths(args.ecore, check, args.out_dir)
    result_json.unlink(missing_ok=True)
    witness_xmi.unlink(missing_ok=True)
    result = {
        "backend": "efinder",
        "status": "UNSUPPORTED_FEATURE",
        "ecore": str(args.ecore.resolve()),
        "check": check,
        "detail": (
            "Primitive EAttribute target multiplicity is skipped: "
            "the EFinder/USE backend cannot soundly represent an unbound "
            "primitive value. Reference-valued target multiplicities remain supported."
        ),
    }
    result_json.write_text(json.dumps(result) + "\n", encoding="utf-8")
    return result, 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ecore", type=Path, help="ATL2TM-generated .ecore transformation model")
    checks = parser.add_mutually_exclusive_group(required=True)
    checks.add_argument("--check", metavar="EClass::constraint",
                        help="one Pivot OCL constraint to negate and search")
    checks.add_argument("--check-all", action="store_true",
                        help="check every ATL2TM target postConstraint (including --constraints)")
    parser.add_argument("--constraints", type=Path,
                        help="an .ocl file or folder of target-post.ocl and optional source-pre.ocl constraints")
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
    if args.constraints is not None and not args.constraints.exists():
        parser.error(f"constraints path not found: {args.constraints}")
    if args.scope < 1 or args.reference_scope < 0 or args.timeout_ms < 1:
        parser.error("scope >= 1, reference-scope >= 0, and timeout-ms >= 1 are required")
    if not args.launcher.is_file():
        parser.error("headless EFinder product not found: " + str(args.launcher)
                     + "; build it first with: cd runtime; "
                     + "$target=(Resolve-Path .\\target-platform\\efinder-headless.target).Path; "
                     + "mvn.cmd -f pom.xml \"-Definder.headless.target=$target\" package -DskipTests")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    unsupported_primitive_checks = set(
        discover_unsupported_primitive_multiplicities(args.ecore))
    if not args.check_all:
        if "::" not in args.check or not all(args.check.split("::", 1)):
            parser.error("--check must be EClass::constraint")
        result, returncode = (skipped_primitive_multiplicity_result(args, args.check)
                              if args.check in unsupported_primitive_checks
                              else run_one(args, args.check))
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return returncode

    try:
        discovered = discover_checks(args.ecore, args.constraints)
    except ValueError as error:
        parser.error(str(error))
    if not discovered:
        summary = {
            "backend": "efinder",
            "status": "NO_POSTCONSTRAINTS",
            "ecore": str(args.ecore.resolve()),
            "checks": [],
            "skipped_checks": sorted(unsupported_primitive_checks),
            "detail": (
                "No supported target postConstraints were found in the "
                "ATL2TM provenance annotation"
            ),
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
            # Primitive target-multiplicity checks are intentionally not sent
            # to EFinder.  They must not turn an otherwise supported batch
            # into UNSUPPORTED_FEATURE, but remain visible in the report.
            "skipped_checks": sorted(unsupported_primitive_checks),
        }
    aggregate = args.out_dir / f"{args.ecore.stem}.all.result.json"
    aggregate.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

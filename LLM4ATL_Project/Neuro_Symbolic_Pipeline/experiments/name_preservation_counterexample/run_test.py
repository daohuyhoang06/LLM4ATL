#!/usr/bin/env python3
"""Run the focused Layer-3 counterexample test for NamePreservation."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
PIPELINE_DIR = HERE.parent.parent
PROJECT_DIR = PIPELINE_DIR.parent
PARSER_DIR = PROJECT_DIR / "ATL_Parser"
FORMAL_RUNNER = PIPELINE_DIR / "pipeline" / "formal_verification" / "run_case.py"

CASE = "Document2Report_All"
CHECK = "Document::NamePreservation"
ATL = HERE / "atl" / "wrong_name_binding.atl"
BASELINE = HERE.parent / "layer3_semantic_faults" / "atl" / "baseline.atl"
MISSING_OUTPUT = (HERE.parent / "layer3_semantic_faults" / "edge_cases"
                  / "atl" / "T1_missing_all_outputs.atl")
CONSTRAINTS = HERE / "constraints" / "direct"
RESULTS = HERE / "results"
CASE_OUTPUT = RESULTS / CASE


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if completed.returncode != 0:
        sys.stderr.write(completed.stdout)
        sys.stderr.write(completed.stderr)
        raise RuntimeError(
            f"command failed ({completed.returncode}): {' '.join(command)}"
        )
    return completed


def check_syntax() -> None:
    maven = "mvn.cmd" if os.name == "nt" else "mvn"
    completed = run([
        maven,
        "-q",
        "test",
        "-Dtest=com.example.atlparser.AtlParserTest",
        f"-Datl.test.resources.dir={ATL.parent}",
    ], PARSER_DIR)
    if "OK: wrong_name_binding.atl" not in completed.stdout:
        raise RuntimeError("ATL parser did not report the mutant as valid")


def run_layer3(atl: Path, output: Path) -> tuple[Path, dict]:
    run([
        sys.executable,
        str(FORMAL_RUNNER),
        "--case", CASE,
        "--atl", str(atl),
        "--constraints", str(CONSTRAINTS),
        "--output", str(output),
        "--check", CHECK,
        "--scope", "3",
        "--reference-scope", "6",
        "--timeout-ms", "180000",
    ], PIPELINE_DIR)

    matches = list((output / CASE / "efinder").glob(
        "*__Document__NamePreservation.result.json"
    ))
    if len(matches) != 1:
        raise RuntimeError(f"expected one result JSON, found: {matches}")
    result = json.loads(matches[0].read_text(encoding="utf-8"))
    return matches[0], result


def check_hot_binding() -> Path:
    generated = CASE_OUTPUT / f"{CASE}_ATL2TM.ecore"
    text = generated.read_text(encoding="utf-8")
    expected = "self.r.title = self.d.author"
    if expected not in text:
        raise RuntimeError(f"HOT did not generate expected binding: {expected}")
    return generated


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    check_syntax()
    result_path, result = run_layer3(ATL, RESULTS)
    generated = check_hot_binding()

    if result.get("status") != "SAT":
        raise RuntimeError(
            "expected SAT/counterexample for NamePreservation, got "
            f"{result.get('status')!r}"
        )
    witness = result.get("counterexample_file")
    if not witness or not Path(witness).is_file():
        raise RuntimeError(f"SAT result has no counterexample file: {witness!r}")

    statuses = {"wrong_binding": result["status"]}
    for label, atl, expected in (
        ("baseline", BASELINE, "UNSAT"),
        ("missing_output", MISSING_OUTPUT, "SAT"),
    ):
        _, checked = run_layer3(atl, RESULTS / label)
        statuses[label] = checked.get("status")
        if checked.get("status") != expected:
            raise RuntimeError(f"{label}: expected {expected}, got {checked.get('status')}")

    summary = {
        "case": CASE,
        "check": CHECK,
        "formula": "Sem AND Pre AND NOT Inv_i",
        "hot_binding": "self.r.title = self.d.author",
        "status": result["status"],
        "regression_statuses": statuses,
        "counterexample_file": witness,
        "generated_transformation_model": str(generated),
        "result_file": str(result_path),
    }
    summary_path = RESULTS / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"PASS: {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

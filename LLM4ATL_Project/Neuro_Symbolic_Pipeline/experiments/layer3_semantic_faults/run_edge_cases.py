#!/usr/bin/env python3
"""Reproduce T1 vacuity and T4 balanced-duplication false negatives."""
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
EDGE_DIR = HERE / "edge_cases"
ATL_DIR = EDGE_DIR / "atl"
RESULTS_DIR = HERE / "results"
CASE = "Document2Report_All"
CHECKS = {
    "Report::E1NamePreservation",
    "Report::E2MappingCompleteness",
    "Report::E3MappingCardinality",
}
CASES = {
    "T1_missing_all_outputs": EDGE_DIR / "constraints" / "T1",
    "T4_balanced_duplication": EDGE_DIR / "constraints" / "T4",
}


def run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True)
    if completed.returncode != 0:
        sys.stderr.write(completed.stdout)
        sys.stderr.write(completed.stderr)
        raise RuntimeError(f"command failed ({completed.returncode}): {' '.join(command)}")
    return completed


def check_syntax() -> dict[str, str]:
    maven = "mvn.cmd" if os.name == "nt" else "mvn"
    completed = run([
        maven,
        "-q",
        "test",
        "-Dtest=com.example.atlparser.AtlParserTest",
        f"-Datl.test.resources.dir={ATL_DIR}",
    ], PARSER_DIR)
    return {
        line.removeprefix("OK: ").strip(): "PASS"
        for line in completed.stdout.splitlines()
        if line.startswith("OK: ")
    }


def check_case(name: str, constraints: Path) -> tuple[dict[str, str], str]:
    output = RESULTS_DIR / f"edge-{name}"
    completed = run([
        sys.executable,
        str(FORMAL_RUNNER),
        "--case", CASE,
        "--atl", str(ATL_DIR / f"{name}.atl"),
        "--constraints", str(constraints),
        "--output", str(output),
        "--scope", "3",
        "--reference-scope", "6",
        "--timeout-ms", "180000",
    ], PIPELINE_DIR)
    report_path = output / CASE / "efinder" / f"{CASE}_ATL2TM.all.result.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    statuses = {
        item["check"]: item["status"]
        for item in report["checks"]
        if item["check"] in CHECKS
    }
    expected = {check: "UNSAT" for check in CHECKS}
    if statuses != expected:
        raise RuntimeError(f"unexpected edge-case statuses for {name}: {statuses}")
    atl2tm = "RESULT:OK" if "RESULT:OK" in completed.stdout else "ERROR"
    return statuses, atl2tm


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    syntax = check_syntax()
    layer3: dict[str, dict[str, str]] = {}
    atl2tm: dict[str, str] = {}
    for name, constraints in CASES.items():
        statuses, conversion = check_case(name, constraints)
        layer3[name] = statuses
        atl2tm[f"{name}.atl"] = conversion
    summary = {
        "case": CASE,
        "formula": "Sem AND Pre AND NOT Post_i",
        "bounds": {"scope": 3, "reference_scope": 6},
        "syntax": syntax,
        "atl2tm": atl2tm,
        "layer3": layer3,
        "interpretation": {
            "T1_missing_all_outputs": "false negative caused by target-context vacuity",
            "T4_balanced_duplication": "E3 false negative caused by equal aggregate counts",
        },
    }
    summary_path = RESULTS_DIR / "edge-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"REPRODUCED: edge-case report written to {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

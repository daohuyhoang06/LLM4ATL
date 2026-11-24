#!/usr/bin/env python3
"""Reproduce the Layer-3 semantic-fault experiment for E1, E2, and E3."""
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
ATL_DIR = HERE / "atl"
RESULTS_DIR = HERE / "results"
CASE = "Document2Report_All"

OBLIGATIONS = {
    "E1": "Report::E1NamePreservation",
    "E2": "Report::E2MappingCompleteness",
    "E3": "Report::E3MappingCardinality",
}
MUTANTS = {
    "E1": ATL_DIR / "E1_wrong_attribute.atl",
    "E2": ATL_DIR / "E2_missing_target.atl",
    "E3": ATL_DIR / "E3_extra_target.atl",
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
    statuses: dict[str, str] = {}
    for line in completed.stdout.splitlines():
        if line.startswith("OK: "):
            statuses[line.removeprefix("OK: ").strip()] = "PASS"
    expected = {"baseline.atl", *(path.name for path in MUTANTS.values())}
    if statuses.keys() != expected:
        raise RuntimeError(f"parser did not accept every fixture: {statuses}")
    return statuses


def formal_command(atl: Path, output: Path, check: str | None = None) -> list[str]:
    command = [
        sys.executable,
        str(FORMAL_RUNNER),
        "--case", CASE,
        "--atl", str(atl),
        "--output", str(output),
        "--scope", "3",
        "--reference-scope", "6",
        "--timeout-ms", "180000",
    ]
    if check:
        command.extend(["--check", check])
    return command


def read_single_result(output: Path, check: str) -> str:
    context, name = check.split("::", 1)
    pattern = f"*__{context}__{name}.result.json"
    matches = list((output / CASE / "efinder").glob(pattern))
    if len(matches) != 1:
        raise RuntimeError(f"expected one result matching {pattern}, found {matches}")
    return str(json.loads(matches[0].read_text(encoding="utf-8"))["status"])


def check_layer3() -> tuple[dict[str, dict[str, str]], dict[str, str]]:
    baseline_output = RESULTS_DIR / "baseline"
    baseline_run = run(formal_command(ATL_DIR / "baseline.atl", baseline_output), PIPELINE_DIR)
    baseline_report = baseline_output / CASE / "efinder" / f"{CASE}_ATL2TM.all.result.json"
    report = json.loads(baseline_report.read_text(encoding="utf-8"))
    selected = set(OBLIGATIONS.values())
    baseline = {
        item["check"]: item["status"]
        for item in report["checks"]
        if item["check"] in selected
    }
    if baseline != {check: "UNSAT" for check in selected}:
        raise RuntimeError(f"baseline did not satisfy all semantic obligations: {baseline}")

    atl2tm = {"baseline.atl": "RESULT:OK" if "RESULT:OK" in baseline_run.stdout else "ERROR"}
    layer3: dict[str, dict[str, str]] = {"baseline": baseline}
    for fault, atl in MUTANTS.items():
        output = RESULTS_DIR / fault
        completed = run(formal_command(atl, output, OBLIGATIONS[fault]), PIPELINE_DIR)
        status = read_single_result(output, OBLIGATIONS[fault])
        layer3[atl.stem] = {OBLIGATIONS[fault]: status}
        atl2tm[atl.name] = "RESULT:OK" if "RESULT:OK" in completed.stdout else "ERROR"
        if status != "SAT":
            raise RuntimeError(f"{fault} was not detected: status={status}")
    return layer3, atl2tm


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    syntax = check_syntax()
    layer3, atl2tm = check_layer3()
    summary = {
        "case": CASE,
        "formula": "Sem AND Pre AND NOT Post_i",
        "bounds": {"scope": 3, "reference_scope": 6},
        "syntax": syntax,
        "atl2tm": atl2tm,
        "layer3": layer3,
    }
    summary_path = RESULTS_DIR / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"PASS: reproducible report written to {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

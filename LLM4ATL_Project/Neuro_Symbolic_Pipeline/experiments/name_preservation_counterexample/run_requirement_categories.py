#!/usr/bin/env python3
"""Check five source-target requirement categories without invoking an LLM."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
PIPELINE_DIR = HERE.parent.parent
FORMAL_RUNNER = PIPELINE_DIR / "pipeline" / "formal_verification" / "run_case.py"
BASELINE = HERE.parent / "layer3_semantic_faults" / "atl" / "baseline.atl"
RESULTS = HERE / "results" / "requirement_categories"
CASE = "Document2Report_All"
RESULT_LABELS = {
    "binding_correctness": "binding",
    "mapping_completeness": "complete",
    "mapping_cardinality": "cardinal",
    "relationship_preservation": "relation",
    "mapping_conditions": "condition",
}

CASES = (
    ("binding_correctness", HERE / "atl" / "wrong_name_binding.atl",
     HERE / "constraints" / "direct", "Document::NamePreservation", BASELINE),
    ("mapping_completeness", HERE / "atl" / "missing_document_mapping.atl",
     HERE / "constraints" / "mapping-requirements",
     "Document::MappingCompleteness", BASELINE),
    ("mapping_cardinality", HERE / "atl" / "duplicate_document_mapping.atl",
     HERE / "constraints" / "mapping-requirements",
     "Document::MappingCardinality", BASELINE),
    ("relationship_preservation", HERE / "atl" / "broken_sections_relationship.atl",
     HERE / "constraints" / "mapping-requirements",
     "Document::RelationshipPreservation", BASELINE),
    ("mapping_conditions", HERE / "atl" / "ignored_mapping_condition.atl",
     HERE / "constraints" / "mapping-condition", "Document::MappingCondition",
     HERE / "atl" / "conditional_document_mapping.atl"),
)


def run_check(label: str, atl: Path, constraints: Path, check: str) -> dict:
    output = RESULTS / label
    command = [
        sys.executable, str(FORMAL_RUNNER), "--case", CASE,
        "--atl", str(atl), "--constraints", str(constraints),
        "--output", str(output), "--check", check,
        "--scope", "3", "--reference-scope", "6",
        "--timeout-ms", "180000",
    ]
    completed = subprocess.run(command, cwd=PIPELINE_DIR, text=True,
                               capture_output=True)
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout + completed.stderr)
    context, invariant = check.split("::", 1)
    matches = list((output / CASE / "efinder").glob(
        f"*__{context}__{invariant}.result.json"
    ))
    if len(matches) != 1:
        raise RuntimeError(f"{label}: expected one result, found {matches}")
    for attempt in range(600):
        try:
            result = json.loads(matches[0].read_text(encoding="utf-8"))
            break
        except FileNotFoundError:
            if attempt == 599:
                raise
            time.sleep(0.1)
    result["result_file"] = str(matches[0])
    return result


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    summary = {"case": CASE, "formula": "Sem AND Pre AND NOT Inv_i",
               "scope": 3, "reference_scope": 6, "categories": {}}
    for category, faulty, constraints, check, correct in CASES:
        result_label = RESULT_LABELS[category]
        print(f"[{category}] faulty ATL", flush=True)
        faulty_result = run_check(result_label + "_fault", faulty, constraints, check)
        print(f"  {faulty_result.get('status')}", flush=True)
        print(f"[{category}] correct ATL", flush=True)
        correct_result = run_check(result_label + "_ok", correct, constraints, check)
        print(f"  {correct_result.get('status')}", flush=True)
        summary["categories"][category] = {
            "check": check,
            "faulty_atl": str(faulty),
            "faulty_status": faulty_result.get("status"),
            "counterexample_file": faulty_result.get("counterexample_file"),
            "correct_atl": str(correct),
            "correct_status": correct_result.get("status"),
        }
        if faulty_result.get("status") != "SAT":
            raise RuntimeError(f"{category}: faulty ATL did not produce SAT")
        if correct_result.get("status") != "UNSAT":
            raise RuntimeError(f"{category}: correct ATL did not produce UNSAT")

    summary_path = RESULTS / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)
    print(f"PASS: {summary_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

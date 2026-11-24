#!/usr/bin/env python3
"""Run one source-target invariant for each Layer-3-supported table task."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PIPELINE = HERE.parent.parent
RUN_CASE = PIPELINE / "pipeline" / "formal_verification" / "run_case.py"
ATL_DIR = PIPELINE / "output" / "final_responses" / "atl"
RESULTS = HERE / "results"
CHECKS = {
    "Class2Interface_All": "Class::ClassMapsToNamedInterface",
    "Document2Report_All": "Document::NamePreservation",
    "Item2Product_All": "Item::ItemMapsToProductWithStockStatus",
    "FamiliesToPersons_All": "Member::MemberMapsToPersonByGender",
    "AmaltheaToAscet_All": "ComponentContainer::ContainerMapsTasksToModule",
    "PetriNet2Grafcet_All": "PetriNet::PetriNetMapsToNamedGrafcet",
    "Grafcet2PetriNet_All": "Grafcet::GrafcetMapsToNamedPetriNet",
    "DSL2KM3_All": "DomainModel::DomainModelMapsToNamedPackage",
}


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    summary = {}
    for case, check in CHECKS.items():
        command = [sys.executable, str(RUN_CASE), "--case", case,
                   "--atl", str(ATL_DIR / f"{case}.atl"),
                   "--check", check, "--output", str(RESULTS),
                   "--scope", "3", "--reference-scope", "6",
                   "--timeout-ms", "180000"]
        print(f"[{case}] {check}", flush=True)
        completed = subprocess.run(command, cwd=PIPELINE, text=True,
                                   capture_output=True)
        context, name = check.split("::", 1)
        result_path = RESULTS / case / "efinder" / (
            f"{case}_ATL2TM__{context}__{name}.result.json")
        result = (json.loads(result_path.read_text(encoding="utf-8"))
                  if result_path.is_file() else {})
        summary[case] = {
            "check": check,
            "status": result.get("status", "ERROR"),
            "returncode": completed.returncode,
            "result_file": str(result_path) if result_path.is_file() else None,
            "counterexample_file": result.get("counterexample_file"),
            "detail": result.get("detail"),
        }
        if completed.returncode and not result_path.is_file():
            summary[case]["detail"] = (completed.stdout + completed.stderr)[-3000:]
        print(f"  {summary[case]['status']}", flush=True)
        (RESULTS / "summary.json").write_text(
            json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return 0 if all(v["status"] in {"SAT", "UNSAT"} for v in summary.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())

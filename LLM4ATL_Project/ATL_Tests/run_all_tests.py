#!/usr/bin/env python3
"""
Reads atl_parser_chrf_results.csv, runs JUnit tests for each (LLM, Strategy, File)
combination where Parsed=True, then outputs:
  1. atl_test_results.csv       - full results with test_pass column
  2. atl_pass_rate_summary.csv  - pass rate per LLM x Strategy combination

Logic: test_pass = True  only if  Parsed=True AND JUnit test passes
       test_pass = False if Parsed=False OR JUnit test fails/errors
"""

import csv
import os
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

PROJECT_DIR = Path(__file__).resolve().parent
REPO_DIR = PROJECT_DIR.parent
PIPELINE_PROJECT_DIR = REPO_DIR / "Neuro_Symbolic_Pipeline"
OUTPUT_DIR = PIPELINE_PROJECT_DIR / "output"
if not OUTPUT_DIR.exists():
    OUTPUT_DIR = PIPELINE_PROJECT_DIR / "ouput"
AST_RESPONSE_DIR = OUTPUT_DIR / "final_responses" / "atl"
ATL_SRC_DIR = PROJECT_DIR / "src" / "main" / "atl"
INPUT_CSV = REPO_DIR / "ATL_Parser" / "atl_parser_chrf_results.csv"
OUTPUT_CSV = PROJECT_DIR / "atl_test_results.csv"
SUMMARY_CSV = PROJECT_DIR / "atl_pass_rate_summary.csv"

# Mapping from ATL file base name to JUnit test class (fully qualified)
FILE_TO_TEST = {
    "AmaltheaToAscet_All":  "org.example.AmaltheaToAscetAllExecutionTest",
    "BibTeX2DocBook_All":   "org.example.BibTeX2DocBookAllExecutionTest",
    "CPL2SPL_All":          "org.example.CPL2SPLAllExecutionTest",
    "Class2Interface_All":  "org.example.Class2InterfaceAllExecutionTest",
    "DSL2KM3_All":          "org.example.DSL2KM3AllExecutionTest",
    "Document2Report_All":  "org.example.Document2ReportAllExecutionTest",
    "FamiliesToPersons_All":"org.example.FamiliesToPersonsAllExecutionTest",
    "Grafcet2PetriNet_All": "org.example.Grafcet2PetriNetAllExecutionTest",
    "IEEE1471_2_MoDAF_All": "org.example.IEEE1471_2_MoDAFAllExecutionTest",
    "Item2Product_All":     "org.example.Item2ProductAllExecutionTest",
    "Make2Ant_All":         "org.example.Make2AntAllExecutionTest",
    "NetworkToGraph_All":   "org.example.NetworkToGraphAllExecutionTest",
    "PetriNet2Grafcet_All": "org.example.PetriNet2GrafcetAllExecutionTest",
    "User2Account_All":     "org.example.User2AccountAllExecutionTest",
    "XML2DSL_All":          "org.example.XML2DSLAllExecutionTest",
}


def run_test(test_class: str) -> bool:
    """Run a single Maven test class. Returns True if the test passes."""
    mvn_cmd = "mvn.cmd" if os.name == "nt" else "mvn"
    cmd = [mvn_cmd, "test", f"-Dtest={test_class}", "-pl", ".", "-q", "--batch-mode"]
    try:
        result = subprocess.run(
            cmd,
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=120,
            shell=False,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"    TIMEOUT for {test_class}")
        return False
    except Exception as e:
        print(f"    ERROR running {test_class}: {e}")
        return False


def copy_atl(file_name: str) -> tuple[bool, Path | None]:
    """Copy ATL file from final_responses/atl to src/main/atl/."""
    src = AST_RESPONSE_DIR / f"{file_name}.atl"
    dst = ATL_SRC_DIR / f"{file_name}.atl"
    if not src.exists():
        print(f"    WARNING: ATL source not found: {src}")
        return False, None

    backup_path = None
    if dst.exists():
        backup_dir = Path(tempfile.mkdtemp(prefix="atl_tests_backup_"))
        backup_path = backup_dir / dst.name
        shutil.copy2(dst, backup_path)

    shutil.copy2(src, dst)
    return True, backup_path


def cleanup_atl(file_name: str, backup_path: Path | None):
    """Restore or remove the copied ATL file after testing."""
    dst = ATL_SRC_DIR / f"{file_name}.atl"
    if backup_path is not None and backup_path.exists():
        shutil.copy2(backup_path, dst)
        shutil.rmtree(backup_path.parent, ignore_errors=True)
    elif dst.exists():
        dst.unlink()


def write_summary_csv(results):
    """Generate pass rate summary CSV grouped by LLM and Strategy."""
    # Collect stats: (LLM, Strategy) -> {passed, total}
    stats = defaultdict(lambda: {"passed": 0, "total": 0})
    for r in results:
        key = (r["LLM"], r["Strategy"])
        stats[key]["total"] += 1
        if r["test_pass"] == "True":
            stats[key]["passed"] += 1

    # Sort by LLM then Strategy
    sorted_keys = sorted(stats.keys())

    with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["LLM", "Strategy", "total", "passed", "failed", "pass_rate"])
        for llm, strategy in sorted_keys:
            s = stats[(llm, strategy)]
            failed = s["total"] - s["passed"]
            rate = s["passed"] / s["total"] * 100 if s["total"] > 0 else 0.0
            writer.writerow([llm, strategy, s["total"], s["passed"], failed, f"{rate:.1f}%"])

    print(f"\nPass rate summary written to: {SUMMARY_CSV}")


def main():
    # Read input CSV
    with INPUT_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    total = len(rows)
    results = []

    print(f"Processing {total} combinations...")
    print("=" * 70)

    for i, row in enumerate(rows):
        llm = row["LLM"]
        strategy = row["Strategy"]
        file_name = row["File"]
        parsed = row["Parsed"].strip() == "True"

        print(f"[{i+1}/{total}] {llm} | {strategy} | {file_name} | Parsed={parsed}")

        # Determine test_pass
        if file_name not in FILE_TO_TEST:
            test_pass = "False"
            print(f"    -> False (no test class mapping)")
        elif not parsed:
            test_pass = "False"
            print(f"    -> False (parser failed)")
        else:
            # Parsed=True and test class exists: run the test
            copied, backup_path = copy_atl(file_name)
            if not copied:
                test_pass = "False"
                print(f"    -> False (ATL file not found)")
            else:
                test_class = FILE_TO_TEST[file_name]
                print(f"    Running test: {test_class} ...")
                passed = run_test(test_class)
                test_pass = "True" if passed else "False"
                print(f"    -> {test_pass}")
                cleanup_atl(file_name, backup_path)

        result_row = dict(row)
        result_row["test_pass"] = test_pass
        results.append(result_row)

    # Write output CSV
    fieldnames = list(rows[0].keys()) + ["test_pass"]
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    pass_count = sum(1 for r in results if r["test_pass"] == "True")
    fail_count = sum(1 for r in results if r["test_pass"] == "False")
    print(f"  Total:    {total}")
    print(f"  Passed:   {pass_count}")
    print(f"  Failed:   {fail_count}")
    print(f"\nResults written to: {OUTPUT_CSV}")

    # Write pass rate summary
    write_summary_csv(results)


if __name__ == "__main__":
    main()

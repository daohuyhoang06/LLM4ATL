#!/usr/bin/env python3
"""Evaluate ATL files from the direct ast2atl response folder.

This script reads:
- Neuro-Symbolic Pipeline/pipeline/mtl_snippet/ATLAS_transformation_language/responses/ast2atl/*.atl
- Neuro-Symbolic Pipeline/pipeline/mtl_snippet/ATLAS_transformation_language/references/*.atl

It writes:
- atl_parser_chrf_results.csv
- atl_parsed_rate.csv
- atl_chrf_similarity.csv
"""

from __future__ import annotations

import csv
import os
import shutil
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path

try:
    from fastchrf import aggregate_chrf
    FASTCHRF_AVAILABLE = True
except ImportError:
    FASTCHRF_AVAILABLE = False


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent
PIPELINE_DIR = REPO_DIR / "Neuro-Symbolic Pipeline" / "pipeline"
AST_RESPONSE_DIR = PIPELINE_DIR / "mtl_snippet" / "ATLAS_transformation_language" / "responses" / "ast2atl"
ATL_REFERENCES_DIR = PIPELINE_DIR / "mtl_snippet" / "ATLAS_transformation_language" / "references"
# Keep the default parser unit-test fixtures separate from generated ATL
# variants. The evaluator temporarily replaces these files and restores them.
TEST_RESOURCES_DIR = SCRIPT_DIR / "src" / "test" / "resources" / "other_references"

MERGED_CSV = SCRIPT_DIR / "atl_parser_chrf_results.csv"
PARSED_CSV = SCRIPT_DIR / "atl_parsed_rate.csv"
CHRF_CSV = SCRIPT_DIR / "atl_chrf_similarity.csv"

LLM_LABEL = "ast2atl"
STRATEGY_LABEL = "direct"


def get_response_files() -> list[Path]:
    return sorted(AST_RESPONSE_DIR.glob("*.atl"))


def get_reference_files() -> dict[str, Path]:
    refs: dict[str, Path] = {}
    if ATL_REFERENCES_DIR.exists():
        for path in ATL_REFERENCES_DIR.glob("*.atl"):
            refs[path.stem] = path
    return refs


def _copy_resource_files(files: list[Path]) -> tuple[Path, list[tuple[Path, Path | None]]]:
    backup_dir = Path(tempfile.mkdtemp(prefix="atl_parser_backup_"))
    restored: list[tuple[Path, Path | None]] = []

    TEST_RESOURCES_DIR.mkdir(parents=True, exist_ok=True)
    for src in files:
        dst = TEST_RESOURCES_DIR / src.name
        backup = None
        if dst.exists():
            backup = backup_dir / dst.name
            shutil.copy2(dst, backup)
        shutil.copy2(src, dst)
        restored.append((dst, backup))

    return backup_dir, restored


def _restore_resource_files(restore_plan: list[tuple[Path, Path | None]], backup_dir: Path) -> None:
    for dst, backup in restore_plan:
        if backup and backup.exists():
            shutil.copy2(backup, dst)
        elif dst.exists():
            dst.unlink()

    shutil.rmtree(backup_dir, ignore_errors=True)


def _run_parser_test(files: list[Path]) -> dict[str, tuple[bool, int]]:
    """Run AtlParserTest once against all response files and parse its output."""
    backup_dir, restore_plan = _copy_resource_files(files)
    try:
        mvn_cmd = "mvn.cmd" if os.name == "nt" else "mvn"
        result = subprocess.run(
            [mvn_cmd, "-q", "test", "-Dtest=com.example.atlparser.AtlParserTest"],
            cwd=SCRIPT_DIR,
            capture_output=True,
            text=True,
            timeout=240,
            shell=False,
        )

        parsed_map: dict[str, tuple[bool, int]] = {}
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("OK: "):
                file_name = line.removeprefix("OK: ").removesuffix(".atl").strip()
                parsed_map[file_name] = (True, 0)
            elif line.startswith("FAIL: "):
                payload = line.removeprefix("FAIL: ").strip()
                file_name, rest = payload.split(" (", 1)
                problem_count = int(rest.split()[0])
                parsed_map[file_name.removesuffix(".atl")] = (False, problem_count)

        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr)

        return parsed_map
    finally:
        _restore_resource_files(restore_plan, backup_dir)


def _chrf_score(generated: str, reference: str) -> float:
    if not FASTCHRF_AVAILABLE:
        raise RuntimeError("fastchrf is not installed")
    return float(aggregate_chrf([[generated]], [[reference]])[0][0])


def generate_reports() -> None:
    files = get_response_files()
    if not files:
        print(f"Error: no ATL files found in {AST_RESPONSE_DIR}")
        return

    references = get_reference_files()
    parsed_map = _run_parser_test(files)

    merged_rows = []
    parsed_rows = []
    chrf_rows = []

    for path in files:
        stem = path.stem
        parsed, problem_count = parsed_map.get(stem, (False, -1))
        ref_path = references.get(stem)
        if ref_path is None:
            print(f"Warning: no reference found for {path.name}")
            continue

        generated = path.read_text(encoding="utf-8")
        reference = ref_path.read_text(encoding="utf-8")
        chrf = round(_chrf_score(generated, reference), 4)

        merged_rows.append({
            "LLM": LLM_LABEL,
            "Strategy": STRATEGY_LABEL,
            "File": stem,
            "Parsed": parsed,
            "ProblemCount": problem_count,
            "CHRF_Score": chrf,
        })
        parsed_rows.append({
            "LLM": LLM_LABEL,
            "Strategy": STRATEGY_LABEL,
            "File": stem,
            "Parsed": parsed,
            "ProblemCount": problem_count,
        })
        chrf_rows.append({
            "LLM": LLM_LABEL,
            "Strategy": STRATEGY_LABEL,
            "File": stem,
            "CHRF_Score": chrf,
        })

    with MERGED_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["LLM", "Strategy", "File", "Parsed", "ProblemCount", "CHRF_Score"])
        writer.writeheader()
        writer.writerows(merged_rows)

    with PARSED_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["LLM", "Strategy", "File", "Parsed", "ProblemCount"])
        writer.writeheader()
        writer.writerows(parsed_rows)

    with CHRF_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["LLM", "Strategy", "File", "CHRF_Score"])
        writer.writeheader()
        writer.writerows(chrf_rows)

    total = len(merged_rows)
    parsed_count = sum(1 for row in merged_rows if row["Parsed"])
    mean_chrf = sum(float(row["CHRF_Score"]) for row in merged_rows) / total if total else 0.0

    print(f"\nCSV: {MERGED_CSV}")
    print(f"Files: {total}")
    print(f"Parsed: {parsed_count}/{total}")
    print(f"Mean ChrF: {mean_chrf:.4f}")


if __name__ == "__main__":
    generate_reports()

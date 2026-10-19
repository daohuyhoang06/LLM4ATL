#!/usr/bin/env python3
"""
Archive the initial experimental traces and artifacts for SOICT 2026 Submission 2052.
This script copies all raw outputs, parser/test reports, generated transformations,
and verification logs into an immutable replication package folder.
"""

import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_PROJECT = ROOT / "LLM4ATL_Project"
DEST_PKG = ROOT / "replication_package_soict2052"
RAW_TRACES = DEST_PKG / "raw_traces"

def win_path(p: Path) -> str:
    path_str = str(p.resolve())
    if os.name == 'nt' and not path_str.startswith('\\\\?\\'):
        return '\\\\?\\' + path_str
    return path_str

def copy_file_safe(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(win_path(src), win_path(dst))

def copy_folder_safe(src: Path, dst: Path):
    if not src.exists():
        print(f"Warning: Source folder {src} does not exist.")
        return
    for item in src.rglob('*'):
        if item.is_file():
            rel = item.relative_to(src)
            target = dst / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(win_path(item), win_path(target))
            except Exception as e:
                print(f"Error copying {item}: {e}")
    print(f"Copied directory {src} -> {dst}")

def copy_files(src_dir: Path, dst_dir: Path, glob_pattern: str):
    if not src_dir.exists():
        print(f"Warning: Source folder {src_dir} does not exist.")
        return
    dst_dir.mkdir(parents=True, exist_ok=True)
    for f in src_dir.glob(glob_pattern):
        if f.is_file():
            copy_file_safe(f, dst_dir / f.name)
            print(f"Copied file {f.name} -> {dst_dir}")

def main():
    print(f"Creating SOICT 2052 Replication Package at: {DEST_PKG}")

    # 1. ATL Parser CSVs
    copy_files(SRC_PROJECT / "ATL_Parser", RAW_TRACES / "atl_parser", "atl_*.csv")

    # 2. ATL Tests CSVs
    copy_files(SRC_PROJECT / "ATL_Tests", RAW_TRACES / "atl_tests", "atl_*.csv")

    # 3. Neuro-Symbolic Pipeline Outputs (final responses and formal verification)
    pipeline_output = SRC_PROJECT / "Neuro_Symbolic_Pipeline" / "ouput"
    if not pipeline_output.exists():
        pipeline_output = SRC_PROJECT / "Neuro_Symbolic_Pipeline" / "output"

    copy_folder_safe(pipeline_output / "final_responses", RAW_TRACES / "neuro_symbolic_pipeline" / "final_responses")
    copy_folder_safe(pipeline_output / "formal_verification", RAW_TRACES / "neuro_symbolic_pipeline" / "formal_verification")

    # 4. Prompting Baselines responses
    prompting_responses = SRC_PROJECT / "Prompting_Strategies" / "n8n-docker" / "mtl_snippets" / "ATLAS_transformation_language" / "responses" / "gemini-3-5-flash"
    copy_folder_safe(prompting_responses, RAW_TRACES / "prompting_baselines" / "gemini-3-5-flash")

    # 5. Reference transformations
    references = SRC_PROJECT / "Prompting_Strategies" / "n8n-docker" / "mtl_snippets" / "ATLAS_transformation_language" / "references"
    copy_folder_safe(references, RAW_TRACES / "references")

    print("\nAll raw traces and artifacts successfully archived into replication package.")

if __name__ == "__main__":
    main()

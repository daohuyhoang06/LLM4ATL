#!/usr/bin/env python3
"""Calculate ATL PPLs (parser problems per reference line of code)."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def atl_loc(path: Path) -> int:
    """Count non-empty, non-comment ATL reference lines (``--`` comments)."""
    count = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        code = line.split("--", 1)[0].strip()
        if code:
            count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute PPLs = parser ProblemCount / reference ATL LoC."
    )
    parser.add_argument("--input", required=True, type=Path, help="Parser-result CSV")
    parser.add_argument(
        "--references", required=True, type=Path, help="Directory containing reference *.atl files"
    )
    parser.add_argument("--output", required=True, type=Path, help="Output PPL CSV")
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"Input CSV not found: {args.input}")
    if not args.references.is_dir():
        parser.error(f"Reference directory not found: {args.references}")

    with args.input.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    output_rows: list[dict[str, object]] = []
    total_problems = 0
    total_loc = 0

    for row in rows:
        file_name = row["File"]
        reference = args.references / f"{file_name}.atl"
        if not reference.is_file():
            print(f"WARNING: reference not found for {file_name}: {reference}")
            continue

        loc = atl_loc(reference)
        problems = int(row["ProblemCount"])
        ppls = problems / loc if loc else 0.0
        total_problems += problems
        total_loc += loc

        output_rows.append(
            {
                "LLM": row["LLM"],
                "Strategy": row["Strategy"],
                "File": file_name,
                "Parsed": row["Parsed"],
                "ProblemCount": problems,
                "ReferenceLoC": loc,
                "PPLs": f"{ppls:.8f}",
            }
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "LLM",
                "Strategy",
                "File",
                "Parsed",
                "ProblemCount",
                "ReferenceLoC",
                "PPLs",
            ],
        )
        writer.writeheader()
        writer.writerows(output_rows)

    weighted_ppls = total_problems / total_loc if total_loc else 0.0
    mean_ppls = (
        sum(float(row["PPLs"]) for row in output_rows) / len(output_rows)
        if output_rows
        else 0.0
    )
    print(f"Wrote {len(output_rows)} rows to {args.output}")
    print(f"Mean PPLs: {mean_ppls:.8f}")
    print(f"Weighted PPLs (total problems / total reference LoC): {weighted_ppls:.8f}")


if __name__ == "__main__":
    main()

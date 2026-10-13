"""Assemble the ATL2TM HOT from categorized fragments in original order."""

from __future__ import annotations

import argparse
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "ATL2TM.generated.atl"
PARTS = (
    "ATL2TM.header.atlpart",
    "common/CommonStrings.atlpart",
    "common/OclRendering.atlpart",
    "common/HelperInlining.atlpart",
    "common/SourceTypeAnalysis.atlpart",
    "steps/Step1_CopyMetamodel.atlpart",
    "steps/Step2_TraceAndBindings.atlpart",
    "steps/Step3_TargetCreation.atlpart",
    "steps/Step4_RuleMutex.atlpart",
    "extensions/LazyRules.atlpart",
    "extensions/ResolveTemp.atlpart",
    "extensions/Provenance.atlpart",
)
MARKER = re.compile(rb"(?m)^-- @hot-atl2tm-part (\d{4})\r?\n")


def assemble() -> bytes:
    pieces: dict[int, bytes] = {}
    for part in PARTS:
        path = ROOT / part
        data = path.read_bytes()
        markers = list(MARKER.finditer(data))
        if not markers or markers[0].start() != 0:
            raise ValueError(f"Missing first part marker in {path}")
        for index, marker in enumerate(markers):
            number = int(marker.group(1))
            if number in pieces:
                raise ValueError(f"Duplicate part number {number:04d}")
            end = markers[index + 1].start() if index + 1 < len(markers) else len(data)
            pieces[number] = data[marker.end():end]
    if set(pieces) != set(range(len(pieces))):
        raise ValueError("Missing or nonconsecutive part numbers")
    return b"".join(pieces[number] for number in sorted(pieces))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = assemble()
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_bytes() != generated:
            raise SystemExit("Generated ATL is stale; run hot-atl2tm/build.py")
        print("Generated ATL matches the fragments")
    elif not OUTPUT.is_file() or OUTPUT.read_bytes() != generated:
        OUTPUT.write_bytes(generated)
        print(f"Generated {OUTPUT} ({len(generated)} bytes)")
    else:
        print("Generated ATL is current")


if __name__ == "__main__":
    main()

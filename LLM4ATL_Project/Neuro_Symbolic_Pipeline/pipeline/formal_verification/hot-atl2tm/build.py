"""Assemble the ATL2TM module from functional fragments in original order."""

from __future__ import annotations

import argparse
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT.parent / "ATL2TM.atl"
PARTS = (
    "ATL2TM.header.atlpart",
    "common/CommonStrings.atlpart",
    "common/HelperInlining.atlpart",
    "common/OclRendering.atlpart",
    "common/SourceAnnotations.atlpart",
    "common/SourceTypeAnalysis.atlpart",
    "common/TargetConstraints.atlpart",
    "common/RootModel.atlpart",
    "steps/Step1_CopyMetamodel.atlpart",
    "steps/Step2_MatchingAndBindings.atlpart",
    "steps/Step2_ImplicitResolution.atlpart",
    "steps/Step2_FrameConditions.atlpart",
    "steps/Step2_TraceStructure.atlpart",
    "steps/Step2_TraceAnnotations.atlpart",
    "steps/Step3_TargetCreation.atlpart",
    "steps/Step4_RuleMutex.atlpart",
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


def build(*, check: bool = False) -> bool:
    """Write the generated ATL if needed; return whether it was already current."""
    generated = assemble()
    current = OUTPUT.is_file() and OUTPUT.read_bytes() == generated
    if check and not current:
        raise SystemExit("ATL2TM.atl is stale; run hot-atl2tm/build.py")
    if not check and not current:
        OUTPUT.write_bytes(generated)
        print(f"Generated {OUTPUT}")
    return current


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if ATL2TM.atl is stale")
    args = parser.parse_args()
    build(check=args.check)
    if args.check:
        print("ATL2TM.atl matches the fragments")


if __name__ == "__main__":
    main()

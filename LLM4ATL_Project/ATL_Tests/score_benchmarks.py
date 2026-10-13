"""Score the two reference-free benchmarks after their JUnit execution tests.

UML->Java: class names and (owning class, field name, field type) only.
SysMLv2->AAS: shell/submodel names and Entity/Property hierarchy, names,
and qualifier types only. This is *partial* Structural F1, not full paper F1.
"""

import argparse
import csv
from collections import Counter
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
RES = ROOT / "src/main/resources"
XSI_TYPE = "{http://www.w3.org/2001/XMLSchema-instance}type"


def local(tag):
    return tag.rsplit("}", 1)[-1]


def java_oracle(path):
    facts = Counter()
    owner = None
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        found = re.search(r"\b(class|interface|enum)\s+(\w+)", line)
        if found:
            owner = found.group(2) if found.group(1) != "enum" else None
            if owner:
                facts[("class", owner)] += 1
            continue
        if line.strip() == "}":
            owner = None
            continue
        if owner:
            field = re.match(r"\s*(?:(?:public|private|protected|static|final)\s+)*([\w.<>\[\], ?]+?)\s+(\w+)\s*;", line)
            if field:
                facts[("field", owner, field.group(2), field.group(1).strip())] += 1
    return facts


def java_output(path):
    facts = Counter()
    root = ET.parse(path).getroot()
    for cls in root.iter():
        if local(cls.tag) not in {"classes", "Class"}:
            continue
        name = cls.get("name") or ""
        facts[("class", name)] += 1
        for field in cls:
            if local(field.tag) == "fields":
                facts[("field", name, field.get("name") or "", field.get("typeName") or "")] += 1
    return facts


def aas_facts(path):
    facts = Counter()
    root = ET.parse(path).getroot()
    for shell in root.iter():
        if local(shell.tag) != "assetadministrationshells":
            continue
        shell_name = shell.get("idShort") or ""
        facts[("shell", shell_name)] += 1
        for submodel in shell:
            if local(submodel.tag) != "submodel":
                continue
            submodel_name = submodel.get("idShort") or ""
            facts[("submodel", shell_name, submodel_name)] += 1

            def descend(parent, ancestors):
                for elem in parent:
                    if local(elem.tag) != "submodelelement":
                        continue
                    kind = (elem.get(XSI_TYPE) or local(elem.tag)).split(":")[-1]
                    if kind == "RelationshipElement":
                        continue  # fixture adapter omits connection/typing semantics
                    name = elem.get("idShort") or ""
                    qualifier = next((q.get("type") or "" for q in elem if local(q.tag) == "qualifier"), "")
                    location = (*ancestors, name)
                    facts[("element", shell_name, submodel_name, *location, kind, qualifier)] += 1
                    descend(elem, location)

            descend(submodel, ())
    return facts


def score(predicted, expected):
    match = sum((predicted & expected).values())
    p = match / sum(predicted.values()) if predicted else 0.0
    r = match / sum(expected.values()) if expected else 0.0
    return p, r, (2 * p * r / (p + r) if p + r else 0.0), match


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=["uml2java", "sysml2aas"], required=True)
    args = parser.parse_args()
    inputs = RES / "models" / ("uml2java" if args.case == "uml2java" else "sysml2aas/xmi")
    oracle_dir = RES / "oracles" / args.case
    result_dir = ROOT / "target/benchmark-results" / args.case
    rows = []
    for source in sorted(inputs.glob("*.xmi")):
        output = result_dir / source.name
        if args.case == "uml2java":
            oracle = oracle_dir / f"{source.stem}_cleanOracle.java"
            expected = java_oracle(oracle)
            parse_output = java_output
        else:
            oracle = oracle_dir / f"{source.stem}.aas"
            expected = aas_facts(oracle)
            parse_output = aas_facts
        executed = output.is_file()
        predicted = parse_output(output) if executed else Counter()
        precision, recall, f1, match = score(predicted, expected)
        scorable = bool(expected)
        rows.append({"case": source.stem, "executed": executed, "scorable": scorable, "matched": match,
                     "predicted": sum(predicted.values()), "oracle": sum(expected.values()),
                     "precision": f"{precision:.4f}" if scorable else "",
                     "recall": f"{recall:.4f}" if scorable else "",
                     "structural_f1_partial": f"{f1:.4f}" if scorable else ""})
    if len(rows) != 10:
        raise ValueError(f"Expected 10 inputs, found {len(rows)}")
    result_dir.mkdir(parents=True, exist_ok=True)
    report = result_dir / "scores.csv"
    with report.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    scored = [float(row["structural_f1_partial"]) for row in rows if row["scorable"]]
    print(f"{sum(row['executed'] for row in rows)}/10 executed; "
          f"{len(scored)}/10 scorable; mean partial Structural F1 "
          f"{sum(scored) / len(scored):.4f}; {report}")


if __name__ == "__main__":
    main()

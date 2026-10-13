"""Build small, reproducible EMF XMI fixtures from the ten textual SysML samples.

This is a deliberately limited adapter, not a general SysML v2 parser. It keeps
named packages, definitions, usages and their lexical nesting. Imports, aliases,
typing, redefinitions, connections and sequencing are not represented. Never
use these fixtures to claim full semantic coverage of the original examples.
"""

from pathlib import Path
import re
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent / "src/main/resources/models/sysml2aas"
SYSML = "https://www.omg.org/spec/SysML/20240201"
XMI = "http://www.omg.org/XMI"
XSI = "http://www.w3.org/2001/XMLSchema-instance"
ET.register_namespace("sysml", SYSML)
ET.register_namespace("xmi", XMI)
ET.register_namespace("xsi", XSI)

KINDS = {
    "part": "Part", "port": "Port", "interface": "Interface",
    "item": "Item", "occurrence": "Occurrence", "attribute": "Attribute",
}


def declaration(fragment):
    fragment = fragment.strip()
    package = re.match(r"package\s+(?:'([^']+)'|([\w-]+))", fragment)
    if package:
        return "Package", package.group(1) or package.group(2)
    definition = re.search(r"\b(part|port|interface|item|occurrence|attribute)\s+def\s+([\w-]+)", fragment)
    if definition:
        return KINDS[definition.group(1)] + "Definition", definition.group(2)
    message = re.match(r"(?:then\s+)?message\s+([\w-]+)", fragment)
    if message:
        return "FlowConnectionUsage", message.group(1)
    if re.match(r"first\s+\w+\s+then\s+\w+", fragment):
        return "SuccessionAsUsage", ""
    port_end = re.match(r"end\s+([\w-]+)\s*:", fragment)
    if port_end:
        return "PortUsage", port_end.group(1)
    redefined = re.search(r"\b(part|port|item)\s+:>>\s*([\w-]+)", fragment)
    if redefined:
        return KINDS[redefined.group(1)] + "Usage", redefined.group(2)
    unnamed = re.search(r"\binterface\s*:\s*\w+\s+connect", fragment)
    if unnamed:
        return "InterfaceUsage", ""
    event = re.search(r"\bevent\s+occurrence\s+([\w-]+)", fragment)
    if event:
        return "EventOccurrenceUsage", event.group(1)
    usage = re.search(r"\b(part|port|interface|item|occurrence|attribute)\s+(?:redefines\s+)?([\w-]+)", fragment)
    if usage:
        return KINDS[usage.group(1)] + "Usage", usage.group(2)
    return None


def convert(source: Path, target: Path):
    text = source.read_text(encoding="utf-8-sig")
    text = re.sub(r"//[^\n]*", "", text)
    stack = []
    root = None
    serial = 0
    tokens = re.split(r"([{};])", text)
    for index, fragment in enumerate(tokens):
        if fragment == "}":
            if stack:
                stack.pop()
        elif fragment == "{":
            # Previous declaration was already pushed below.
            continue
        elif fragment == ";":
            continue
        else:
            parsed = declaration(fragment)
            if not parsed:
                continue
            kind, name = parsed
            serial += 1
            attrs = {"elementId": f"{source.stem}-{serial}"}
            if name:
                attrs["declaredName"] = name
            if kind == "Package" and root is None:
                root = ET.Element(f"{{{SYSML}}}Package", attrs)
                node = root
            elif stack:
                relation = ET.SubElement(stack[-1], "ownedRelationship", {
                    f"{{{XSI}}}type": "sysml:FeatureMembership",
                    "elementId": f"{source.stem}-membership-{serial}",
                })
                node = ET.SubElement(relation, "ownedRelatedElement", {
                    f"{{{XSI}}}type": f"sysml:{kind}", **attrs,
                })
            else:
                continue
            # A declaration with a body is a lexical parent. Semicolon-only
            # declarations must not remain on the stack.
            next_token = tokens[index + 1] if index + 1 < len(tokens) else ""
            if next_token == "{":
                stack.append(node)
            elif kind == "Package" and not stack:
                stack.append(node)
    if root is None:
        raise ValueError(f"No package in {source}")
    ET.indent(root)
    target.write_bytes(ET.tostring(root, encoding="utf-8", xml_declaration=True))


if __name__ == "__main__":
    output = BASE / "xmi"
    output.mkdir(exist_ok=True)
    for path in sorted((BASE / "source").glob("*.sysml")):
        convert(path, output / f"{path.stem}.xmi")
        print(path.name)

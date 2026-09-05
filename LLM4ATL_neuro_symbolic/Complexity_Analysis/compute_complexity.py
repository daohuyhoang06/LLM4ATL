#!/usr/bin/env python3
"""
Per-script complexity features for canonical reference transformations (47 scripts).

Conservative McCabe-style metric per rule/helper/routine/mapping body:
  mccabe_body = 1 + (# explicit control-flow tokens in that body)

Counted tokens (after stripping strings/comments):
  if, else if / elseif / elif, while, for, switch, case, default
Reactions additionally: with (guard clause)

NOT counted: and, or, select, exists, iterate, collection operators.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import List, Optional, Tuple

OUTPUT_DIR = Path(__file__).resolve().parent
REPO_ROOT = Path(__file__).resolve().parents[1]
MTL_ROOT = REPO_ROOT / "LLM4ATL_neuro_symbolic"

# --- paths ---
ATL_REF = MTL_ROOT / "ATL_Tests/src/main/resources/referenceATL"
ATL_MODELS = MTL_ROOT / "ATL_Tests/src/main/resources/models"
REACTIONS_REF = MTL_ROOT / (
    "Workflows/n8n-docker/mtl_snippets/reactions_language/references"
)
ETL_REF = MTL_ROOT / "Workflows/n8n-docker/mtl_snippets/ETL_language/references"
QVTO_REF = MTL_ROOT / "Workflows/n8n-docker/mtl_snippets/QVTO_language/references"

# Conservative control-flow regex (word boundaries; no bare 'and'/'or')
CONTROL_FLOW_RE = re.compile(
    r"(?P<t>"
    r"\bif\b|"
    r"\belse\s+if\b|"
    r"\belseif\b|"
    r"\belif\b|"
    r"\bwhile\b|"
    r"\bfor\b|"
    r"\bswitch\b|"
    r"\bcase\b|"
    r"\bdefault\b"
    r")",
    re.IGNORECASE,
)
REACTIONS_WITH_RE = re.compile(r"\bwith\b", re.IGNORECASE)


def strip_sl_strings(s: str) -> str:
    """Remove '...' and \"...\" substrings (best-effort, nested quotes not handled)."""
    out = []
    i = 0
    while i < len(s):
        c = s[i]
        if c in "'\"":
            q = c
            i += 1
            while i < len(s) and s[i] != q:
                if s[i] == "\\" and i + 1 < len(s):
                    i += 2
                    continue
                i += 1
            i += 1  # skip closing quote
            out.append(" ")
            continue
        out.append(c)
        i += 1
    return "".join(out)


def strip_atl_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        if "--" in line:
            line = line.split("--")[0]
        if line.strip():
            lines.append(line)
    return "\n".join(lines)


def strip_reactions_comments(text: str) -> str:
    out_lines = []
    for line in text.splitlines():
        if "//" in line:
            line = line.split("//")[0]
        if line.strip():
            out_lines.append(line)
    return "\n".join(out_lines)


def strip_etl_comments(text: str) -> str:
    return strip_reactions_comments(text)  # // style


def strip_qvto_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("//"):
            continue
        if "//" in line:
            line = line.split("//")[0]
        if line.strip():
            lines.append(line)
    return "\n".join(lines)


def mccabe_increment(text: str, extra_with: bool = False) -> int:
    """Base 1 + control-flow token count on cleaned text."""
    t = strip_sl_strings(text)
    n = len(CONTROL_FLOW_RE.findall(t))
    if extra_with:
        n += len(REACTIONS_WITH_RE.findall(t))
    return 1 + n


def match_brace(s: str, open_idx: int) -> Optional[Tuple[str, int]]:
    """Return (inner content, index after closing brace) for '{' at open_idx."""
    if open_idx >= len(s) or s[open_idx] != "{":
        return None
    depth = 0
    i = open_idx
    while i < len(s):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return s[open_idx + 1 : i], i + 1
        i += 1
    return None


# --- ATL ---
ATL_RULE_HEAD = re.compile(
    r"(?m)^\s*(?:lazy\s+)?rule\s+(\w+)\s*\{"
)
ATL_HELPER_HEAD = re.compile(r"(?m)^\s*helper\s+")


def extract_atl_bodies(clean: str) -> List[str]:
    bodies: List[str] = []
    # Rules: find '{', brace-match
    for m in ATL_RULE_HEAD.finditer(clean):
        open_brace = m.end() - 1
        got = match_brace(clean, open_brace)
        if got:
            inner, _ = got
            bodies.append(inner)
    # Helpers: split by lines starting with helper (after module/create stripped)
    lines = clean.splitlines()
    blocks: List[str] = []
    cur: List[str] = []
    for line in lines:
        if re.match(r"^\s*helper\s+", line):
            if cur:
                blocks.append("\n".join(cur))
            cur = [line]
        else:
            if cur:
                cur.append(line)
    if cur:
        blocks.append("\n".join(cur))
    for b in blocks:
        bodies.append(b)
    return bodies


def analyze_atl(path: Path) -> Tuple[int, int, int, float]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    clean = strip_atl_comments(raw)
    loc = len(clean.splitlines())
    n_rules = len(ATL_RULE_HEAD.findall(clean))
    # helpers: blocks starting with helper
    n_helpers = len(re.findall(r"(?m)^\s*helper\s+", clean))
    bodies = extract_atl_bodies(clean)
    if not bodies:
        # fallback: whole file
        bodies = [clean]
    mccabe = sum(mccabe_increment(b, extra_with=False) for b in bodies)
    return loc, n_rules, n_helpers, float(mccabe)


# --- Reactions ---
RE_REACTION = re.compile(r"(?m)^\s*reaction\s+(\w+)\s*\{")
RE_ROUTINE = re.compile(r"(?m)^\s*routine\s+(\w+)\s*\(")


def extract_reactions_bodies(clean: str) -> List[str]:
    bodies: List[str] = []
    for m in RE_REACTION.finditer(clean):
        ob = m.end() - 1
        got = match_brace(clean, ob)
        if got:
            inner, _ = got
            bodies.append(inner)
    for m in RE_ROUTINE.finditer(clean):
        ob = clean.find("{", m.end())
        if ob == -1:
            continue
        got = match_brace(clean, ob)
        if got:
            inner, _ = got
            bodies.append(inner)
    return bodies


def analyze_reactions(path: Path) -> Tuple[int, int, int, float]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    clean = strip_reactions_comments(raw)
    loc = len(clean.splitlines())
    n_rules = len(RE_REACTION.findall(clean))
    n_helpers = len(RE_ROUTINE.findall(clean))
    bodies = extract_reactions_bodies(clean)
    if not bodies:
        bodies = [clean]
    mccabe = sum(mccabe_increment(b, extra_with=True) for b in bodies)
    return loc, n_rules, n_helpers, float(mccabe)


# --- ETL ---
# Rule name and `transform` may be on separate lines (see OO2DB.etl).


def _etl_rule_open_brace(clean: str, rule_match: re.Match) -> Optional[int]:
    """Index of opening `{` for an ETL rule (after `transform` ...)."""
    sub = clean[rule_match.start() :]
    bi = sub.find("{")
    if bi == -1:
        return None
    if "transform" not in sub[:bi]:
        return None
    return rule_match.start() + bi


def extract_etl_rule_bodies(clean: str) -> List[str]:
    bodies: List[str] = []
    for m in re.finditer(r"(?m)^\s*rule\s+(\w+)\b", clean):
        ob = _etl_rule_open_brace(clean, m)
        if ob is None:
            continue
        got = match_brace(clean, ob)
        if got:
            bodies.append(got[0])
    return bodies


ETL_OPERATION_RE = re.compile(r"(?m)^\s*operation\s+")


def extract_etl_operation_bodies(clean: str) -> List[str]:
    bodies: List[str] = []
    for m in ETL_OPERATION_RE.finditer(clean):
        ob = clean.find("{", m.end())
        if ob == -1:
            continue
        got = match_brace(clean, ob)
        if got:
            bodies.append(got[0])
    return bodies


def analyze_etl(path: Path) -> Tuple[int, int, int, float]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    clean = strip_etl_comments(raw)
    loc = len(clean.splitlines())
    n_rules = len(re.findall(r"(?m)^\s*rule\s+(\w+)\b", clean))
    n_helpers = len(ETL_OPERATION_RE.findall(clean))
    rule_bodies = extract_etl_rule_bodies(clean)
    op_bodies = extract_etl_operation_bodies(clean)
    bodies = rule_bodies + op_bodies
    if not bodies:
        bodies = [clean]
    mccabe = sum(mccabe_increment(b, extra_with=False) for b in bodies)
    return loc, n_rules, n_helpers, float(mccabe)


# --- QVTo ---
QVTO_MAPPING = re.compile(r"(?m)^\s*mapping\s+")
QVTO_HELPER = re.compile(r"(?m)^\s*helper\s+")


def extract_qvto_mapping_bodies(clean: str) -> List[str]:
    bodies: List[str] = []
    for m in re.finditer(r"(?m)^\s*mapping\s+", clean):
        ob = clean.find("{", m.end())
        if ob == -1:
            continue
        got = match_brace(clean, ob)
        if got:
            bodies.append(got[0])
    return bodies


def extract_qvto_constructor_bodies(clean: str) -> List[str]:
    bodies: List[str] = []
    for m in re.finditer(r"(?m)^\s*constructor\s+", clean):
        ob = clean.find("{", m.end())
        if ob == -1:
            continue
        got = match_brace(clean, ob)
        if got:
            bodies.append(got[0])
    return bodies


def extract_qvto_main_bodies(clean: str) -> List[str]:
    bodies: List[str] = []
    for m in re.finditer(r"(?m)^\s*main\s*\(\s*\)\s*\{", clean):
        ob = m.end() - 1
        got = match_brace(clean, ob)
        if got:
            bodies.append(got[0])
    return bodies


def extract_qvto_helper_bodies(clean: str) -> List[str]:
    bodies: List[str] = []
    for m in re.finditer(r"(?m)^\s*helper\s+", clean):
        ob = clean.find("{", m.end())
        if ob == -1:
            continue
        got = match_brace(clean, ob)
        if got:
            bodies.append(got[0])
    return bodies


def analyze_qvto(path: Path) -> Tuple[int, int, int, float]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    clean = strip_qvto_comments(raw)
    loc = len(clean.splitlines())
    n_map = len(re.findall(r"(?m)^\s*mapping\s+", clean))
    n_ctor = len(re.findall(r"(?m)^\s*constructor\s+", clean))
    n_main = len(re.findall(r"(?m)^\s*main\s*\(\s*\)\s*\{", clean))
    n_help = len(re.findall(r"(?m)^\s*helper\s+", clean))
    # n_rules = QVTo "units" (mapping/constructor/main); helpers separate
    n_rules = n_map + n_ctor + n_main
    bodies = (
        extract_qvto_main_bodies(clean)
        + extract_qvto_constructor_bodies(clean)
        + extract_qvto_mapping_bodies(clean)
        + extract_qvto_helper_bodies(clean)
    )
    if not bodies:
        bodies = [clean]
    mccabe = sum(mccabe_increment(b, extra_with=False) for b in bodies)
    return loc, n_rules, n_help, float(mccabe)


# --- ATL metamodel / model artifact count (recoverable) ---
ATL_STEM_TO_INPUT = {
    "AmaltheaToAscet_All": 1,
    "BibTeX2DocBook_All": 1,
    "CPL2SPL_All": 1,
    "Class2Interface_All": 1,
    "DSL2KM3_All": 1,
    "Document2Report_All": 1,
    "FamiliesToPersons_All": 1,
    "Grafcet2PetriNet_All": 1,
    "IEEE1471_2_MoDAF_All": 1,
    "Item2Product_All": 1,
    "Make2Ant_All": 1,
    "NetworkToGraph_All": 1,
    "PetriNet2Grafcet_All": 1,
    "User2Account_All": 1,
    "XML2DSL_All": 1,
}


def n_mm_for_script(mtl: str, script_stem: str) -> float:
    if mtl == "atl":
        return float(ATL_STEM_TO_INPUT.get(script_stem, 1))
    return float("nan")


def main() -> None:
    rows: List[dict] = []

    for p in sorted(ATL_REF.glob("*.atl")):
        stem = p.stem
        loc, nr, nh, mc = analyze_atl(p)
        rows.append(
            {
                "mtl": "atl",
                "script_name": p.name,
                "script_key": stem,
                "loc": loc,
                "n_rules": nr,
                "n_helpers": nh,
                "n_mm_artifacts": n_mm_for_script("atl", stem),
                "mccabe": mc,
            }
        )

    for p in sorted(REACTIONS_REF.glob("*.reactions")):
        stem = p.stem
        loc, nr, nh, mc = analyze_reactions(p)
        rows.append(
            {
                "mtl": "reactions",
                "script_name": p.name,
                "script_key": stem,
                "loc": loc,
                "n_rules": nr,
                "n_helpers": nh,
                "n_mm_artifacts": float("nan"),
                "mccabe": mc,
            }
        )

    for p in sorted(ETL_REF.glob("*.etl")):
        if p.parent.name == "other_references":
            continue
        stem = p.stem
        loc, nr, nh, mc = analyze_etl(p)
        rows.append(
            {
                "mtl": "etl",
                "script_name": p.name,
                "script_key": stem,
                "loc": loc,
                "n_rules": nr,
                "n_helpers": nh,
                "n_mm_artifacts": float("nan"),
                "mccabe": mc,
            }
        )

    for p in sorted(QVTO_REF.glob("*.qvto")):
        if p.parent.name == "other_references":
            continue
        stem = p.stem
        loc, nr, nh, mc = analyze_qvto(p)
        rows.append(
            {
                "mtl": "qvto",
                "script_name": p.name,
                "script_key": stem,
                "loc": loc,
                "n_rules": nr,
                "n_helpers": nh,
                "n_mm_artifacts": float("nan"),
                "mccabe": mc,
            }
        )

    out = OUTPUT_DIR / "complexity_features.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "mtl",
                "script_name",
                "script_key",
                "loc",
                "n_rules",
                "n_helpers",
                "n_mm_artifacts",
                "mccabe",
            ],
        )
        w.writeheader()
        for r in rows:
            rr = r.copy()
            for k in ("n_mm_artifacts", "mccabe"):
                v = rr[k]
                if isinstance(v, float) and v != v:  # NaN
                    rr[k] = ""
                elif k == "n_mm_artifacts" and rr[k] == "":
                    pass
            w.writerow(
                {
                    "mtl": rr["mtl"],
                    "script_name": rr["script_name"],
                    "script_key": rr["script_key"],
                    "loc": rr["loc"],
                    "n_rules": rr["n_rules"],
                    "n_helpers": rr["n_helpers"],
                    "n_mm_artifacts": ""
                    if (isinstance(rr["n_mm_artifacts"], float) and rr["n_mm_artifacts"] != rr["n_mm_artifacts"])
                    else rr["n_mm_artifacts"],
                    "mccabe": rr["mccabe"],
                }
            )

    print(f"Wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()

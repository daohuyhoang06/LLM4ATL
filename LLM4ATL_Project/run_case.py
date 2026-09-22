#!/usr/bin/env python3
"""run_case.py -- run the whole pipeline for ONE case, end to end, with a clear
report of what each stage produced or failed with.  Does not touch the existing
code; it re-uses the pipeline's checker modules and ast2atl generator.

Stages
  1. INPUTS   locate the NL spec + the two .ecore metamodels for the case
  2. LLM      build the prompt, call Gemini, run the 3 in-pipeline check layers
              (0 JSON syntax, 1 Pydantic schema, 2 semantic/Ecore) with retries;
              on success save  Neuro_Symbolic_Pipeline/ouput/final_responses/atl_ast/<case>.json
  3. AST2ATL  atl_ast/<case>.json  ->  ouput/final_responses/atl/<case>.atl
  4. PARSER   ATL_Parser: syntax check the .atl        (RESULT:OK:0 / RESULT:FAIL:n)
  5. TESTS    ATL_Tests: run the JUnit execution test for the case

(Formal verification is separate: ../use_validator/mv_check.py runs the USE
Model Validator on a .use + .properties pair produced by other tooling.)

Usage
  python3 run_case.py                         # case 1 = FamiliesToPersons_All
  python3 run_case.py --case Class2Interface_All
  python3 run_case.py --case 2 --force        # 2nd case, re-ask the LLM
  python3 run_case.py --list
  python3 run_case.py --skip-llm --skip-tests # reuse existing AST json, no maven tests
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent
PIPELINE_PROJECT_DIR = REPO / "Neuro_Symbolic_Pipeline"
PIPE = PIPELINE_PROJECT_DIR / "pipeline"
INPUT_DIR = PIPELINE_PROJECT_DIR / "input"
OUTPUT_DIR = PIPELINE_PROJECT_DIR / "output"
if not OUTPUT_DIR.exists():
    OUTPUT_DIR = PIPELINE_PROJECT_DIR / "ouput"
PROMPTS = INPUT_DIR / "prompts" / "user_prompts"
AST_DIR = OUTPUT_DIR / "final_responses" / "atl_ast"
ATL_DIR = OUTPUT_DIR / "final_responses" / "atl"
ATL_PARSER = REPO / "ATL_Parser"
ATL_TESTS = REPO / "ATL_Tests"

# case 1 first, then a stable order; every key must exist in mapping.json
CASES = [
    "FamiliesToPersons_All", "Class2Interface_All", "Document2Report_All",
    "Item2Product_All", "User2Account_All", "NetworkToGraph_All",
    "AmaltheaToAscet_All", "BibTeX2DocBook_All", "XML2DSL_All",
    "PetriNet2Grafcet_All", "Grafcet2PetriNet_All", "DSL2KM3_All",
    "IEEE1471_2_MoDAF_All", "Make2Ant_All", "CPL2SPL_All",
]
FILE_TO_TEST = {c: f"org.example.{c.replace('_All','')}AllExecutionTest" for c in CASES}
FILE_TO_TEST["IEEE1471_2_MoDAF_All"] = "org.example.IEEE1471_2_MoDAFAllExecutionTest"

MVN = "mvn.cmd" if sys.platform == "win32" else "mvn"

C_OK, C_BAD, C_SKIP, C_END = "\033[32m", "\033[31m", "\033[33m", "\033[0m"


def hdr(txt: str):
    print(f"\n{'='*72}\n{txt}\n{'='*72}")


def tag(ok):  # ok in {True, False, None}
    return f"{C_OK}PASS{C_END}" if ok else (f"{C_SKIP}SKIP{C_END}" if ok is None else f"{C_BAD}FAIL{C_END}")


# --------------------------------------------------------------------------- #
#  stage 1: inputs                                                            #
# --------------------------------------------------------------------------- #
def stage_inputs(case: str):
    hdr(f"STAGE 1  INPUTS  ({case})")
    with (INPUT_DIR / "mapping.json").open(encoding="utf-8") as f:
        mapping = json.load(f)
    spec = PROMPTS / f"{case}.txt"
    if not spec.exists():
        sys.exit(f"no NL spec: {spec}")
    ecores = []
    for mapped_path in mapping.get(case, []):
        path = Path(mapped_path)
        if path.parts and path.parts[0].lower() == "atl_model":
            path = Path(*path.parts[1:])
        ecores.append(INPUT_DIR / "ATL_metamodel" / path)
    missing = [e for e in ecores if not e.exists()]
    if not ecores or missing:
        sys.exit(f"missing metamodels for {case}: {missing or 'none in mapping.json'}")
    print(f"  NL spec      : {spec}")
    print(f"                 \"{spec.read_text(encoding='utf-8').strip().splitlines()[0][:80]}...\"")
    for e in ecores:
        print(f"  metamodel    : {e}   ({e.stat().st_size} bytes)")
    return spec, ecores


# --------------------------------------------------------------------------- #
#  stage 2: LLM + 3 check layers  (logic mirrors main.py, own reporting)      #
# --------------------------------------------------------------------------- #
def stage_llm(case, spec: Path, ecores, args):
    hdr(f"STAGE 2  LLM + 3 CHECK LAYERS  ({case})")
    out_json = AST_DIR / f"{case}.json"

    if args.skip_llm:
        if out_json.exists():
            print(f"  {tag(None)}  --skip-llm, reusing {out_json}")
            return out_json, None
        sys.exit(f"--skip-llm but {out_json} does not exist; run without it first")

    if out_json.exists() and not args.force:
        print(f"  {tag(None)}  {out_json} already exists (use --force to re-ask the LLM)")
        return out_json, None
    if args.force and out_json.exists():
        out_json.unlink()

    sys.path.insert(0, str(PIPELINE_PROJECT_DIR))
    sys.path.insert(0, str(PIPELINE_PROJECT_DIR / "common"))
    from pipeline.structural_checking.schema.atl_ast import Module  # noqa: E402
    from config.ablation_config import AblationConfig              # noqa: E402
    from pipeline.static_analysis.ecore_registry import ATLEcoreRegistry  # noqa: E402
    from pipeline.static_analysis.type_environment import TypeEnvironment  # noqa: E402
    from pipeline.static_analysis.atl_semantic_checker import ATLSemanticChecker  # noqa: E402
    from pipeline.static_analysis.errors import SemanticError       # noqa: E402
    from pydantic import ValidationError                    # noqa: E402
    try:
        import google.generativeai as genai
    except ImportError:
        sys.exit("pip install google-generativeai python-dotenv  (or run with --skip-llm)")
    from dotenv import load_dotenv                          # noqa: E402
    import os

    load_dotenv(PIPELINE_PROJECT_DIR / ".env")
    key = os.getenv("GEMINI_API_KEY")
    if not key or key.startswith("your_"):
        sys.exit(f"set GEMINI_API_KEY in {PIPELINE_PROJECT_DIR/'.env'}")
    genai.configure(api_key=key)
    model = genai.GenerativeModel(args.model)
    ablation = AblationConfig.from_env()

    sys_prompt = (INPUT_DIR / "prompts" / "system_prompt.txt").read_text(encoding="utf-8").replace(
        "<INSERT_SCHEMA_HERE>", json.dumps(Module.model_json_schema(), indent=2))
    model_text = "\n\n".join(e.read_text(encoding="utf-8") for e in ecores)
    spec_text = spec.read_text(encoding="utf-8")

    def build(err):
        p = (f"{sys_prompt}\n\n=== ECORE MODELS ===\n{model_text}\n\n"
             f"=== TRANSFORMATION REQUEST ===\n{spec_text}")
        if err:
            p += f"\n\n=== PREVIOUS ATTEMPT FAILED WITH VALIDATION ERROR ===\nFix:\n{err}"
        return p

    def unfence(t):
        t = t.strip()
        for pre in ("```json", "```"):
            if t.startswith(pre):
                t = t[len(pre):]
        return t[:-3].strip() if t.endswith("```") else t.strip()

    err, data = "", None
    for attempt in range(args.retries + 1):
        print(f"\n  -- attempt {attempt+1}/{args.retries+1} --")
        try:
            print("  calling Gemini ...")
            raw = unfence(model.generate_content(build(err)).text)

            data = json.loads(raw)
            print(f"  Layer 0 JSON syntax     : {tag(True)}")

            ast_obj = Module(**data)
            print(f"  Layer 1 Pydantic schema : {tag(True)}")

            if ablation.is_enabled("enable_layer2_semantic"):
                reg = ATLEcoreRegistry([str(e) for e in ecores])
                ATLSemanticChecker.check_module(ast_obj, TypeEnvironment(registry=reg), ablation)
                print(f"  Layer 2 semantic/Ecore  : {tag(True)}")
            else:
                print(f"  Layer 2 semantic/Ecore  : {tag(None)} (disabled)")

            AST_DIR.mkdir(parents=True, exist_ok=True)
            out_json.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"\n  {tag(True)}  saved AST -> {out_json}")
            return out_json, None
        except json.JSONDecodeError as e:
            err = f"JSONDecodeError: {e}\nReturn valid JSON only, no prose."
            print(f"  Layer 0 JSON syntax     : {tag(False)}\n    {err.splitlines()[0]}")
        except ValidationError as e:
            err = str(e)
            print(f"  Layer 1 Pydantic schema : {tag(False)}  ({e.error_count()} errors)")
            print("    " + "\n    ".join(err.splitlines()[:8]))
        except SemanticError as e:
            err = f"SemanticError: {e}"
            print(f"  Layer 2 semantic/Ecore  : {tag(False)}\n    {e}")
        except Exception as e:                                    # API / quota / network
            print(f"  {tag(False)}  API/system error: {str(e).splitlines()[0]}")
            return None, f"llm error: {str(e).splitlines()[0]}"
        if attempt < args.retries:
            time.sleep(8)

    if data is not None:
        out_json.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\n  {tag(False)}  no clean AST after {args.retries+1} attempts; last draft saved -> {out_json}")
    return (out_json if data is not None else None), f"unfixed after {args.retries+1} attempts"


# --------------------------------------------------------------------------- #
#  stage 3: AST JSON -> ATL text                                              #
# --------------------------------------------------------------------------- #
def stage_ast2atl(case, ast_json: Path):
    hdr(f"STAGE 3  AST -> ATL  ({case})")
    sys.path.insert(0, str(PIPELINE_PROJECT_DIR))
    sys.path.insert(0, str(PIPELINE_PROJECT_DIR / "common"))
    from pipeline.formal_verification import ast2atl             # noqa: E402
    ATL_DIR.mkdir(parents=True, exist_ok=True)
    out_atl = ATL_DIR / f"{case}.atl"
    try:
        code = ast2atl.ATLGenerator(json.loads(ast_json.read_text(encoding="utf-8"))).generate()
        out_atl.write_text(code, encoding="utf-8")
        print(f"  {tag(True)}  {out_atl}  ({len(code.splitlines())} lines)")
        print("  --- first 15 lines ---")
        print("\n".join("    " + l for l in code.splitlines()[:15]))
        return out_atl, None
    except Exception as e:
        print(f"  {tag(False)}  ast2atl failed: {e}")
        return None, f"ast2atl: {e}"


# --------------------------------------------------------------------------- #
#  stage 4: ATL_Parser (syntax)                                               #
# --------------------------------------------------------------------------- #
def stage_parser(case, atl: Path, args):
    """Run ATL_Parser's JUnit AtlParserTest against a temp dir holding only this
    one .atl (a space-free path -- the repo path contains 'Neuro-Symbolic
    Pipeline').  Prints 'OK: <file>' or 'FAIL: <file> (n errors)' + the problems."""
    hdr(f"STAGE 4  ATL_Parser (syntax)  ({case})")
    if args.skip_parser:
        print(f"  {tag(None)}  --skip-parser")
        return None, None
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="atlparser_"))
    shutil.copy2(atl, tmp / f"{case}.atl")
    cmd = [MVN, "-q", "-B", "test", "-Dtest=com.example.atlparser.AtlParserTest",
           f"-Datl.test.resources.dir={tmp}", "-pl", "."]
    print("  $", " ".join(cmd))
    r = subprocess.run(cmd, cwd=ATL_PARSER, capture_output=True, text=True, timeout=900)
    out = r.stdout + r.stderr
    verdict = next((l.strip() for l in out.splitlines()
                    if l.strip().startswith(("OK:", "FAIL:"))), None)
    ok = r.returncode == 0 and (verdict or "").startswith("OK:")
    print(f"  {tag(ok)}  {verdict or f'(mvn exit {r.returncode}, no OK/FAIL line)'}")
    if not ok:
        for l in out.splitlines():
            s = l.strip()
            if s.startswith("- ") or "syntax error" in s.lower() or "line " in s.lower():
                print("    " + s)
    shutil.rmtree(tmp, ignore_errors=True)
    return ok, None if ok else (verdict or f"parser mvn exit {r.returncode}")


# --------------------------------------------------------------------------- #
#  stage 5: ATL_Tests (execution + output-model assertions)                   #
# --------------------------------------------------------------------------- #
def stage_tests(case, atl: Path, args):
    hdr(f"STAGE 5  ATL_Tests (execution)  ({case})")
    if args.skip_tests:
        print(f"  {tag(None)}  --skip-tests")
        return None, None
    test_class = FILE_TO_TEST.get(case)
    if not test_class:
        print(f"  {tag(None)}  no JUnit test mapped for {case}")
        return None, None

    dst = ATL_TESTS / "src" / "main" / "atl" / f"{case}.atl"
    backup = dst.read_bytes() if dst.exists() else None
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(atl, dst)
    try:
        cmd = [MVN, "-q", "-B", "test", f"-Dtest={test_class}", "-pl", "."]
        print("  $", " ".join(cmd))
        r = subprocess.run(cmd, cwd=ATL_TESTS, capture_output=True, text=True, timeout=600)
        ok = r.returncode == 0
        print(f"  {tag(ok)}  mvn exit {r.returncode}")
        if not ok:
            rep = ATL_TESTS / "target" / "surefire-reports" / f"{test_class}.txt"
            if rep.exists():
                print("  --- surefire report (head) ---")
                print("\n".join("    " + l for l in rep.read_text().splitlines()[:25]))
            else:
                print("\n".join("    " + l for l in (r.stdout + r.stderr).splitlines()[-20:]))
        return ok, None if ok else f"tests: mvn exit {r.returncode}"
    finally:
        if backup is not None:
            dst.write_bytes(backup)
        elif dst.exists():
            dst.unlink()


# --------------------------------------------------------------------------- #
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--case", default="1", help="case name or 1-based index (default 1 = FamiliesToPersons_All)")
    ap.add_argument("--list", action="store_true", help="print the numbered case list and exit")
    ap.add_argument("--force", action="store_true", help="re-ask the LLM even if the AST json exists")
    ap.add_argument("--retries", type=int, default=3, help="LLM auto-fix retries (default 3)")
    ap.add_argument("--model", default="gemini-3.5-flash")
    ap.add_argument("--skip-llm", action="store_true")
    ap.add_argument("--skip-parser", action="store_true")
    ap.add_argument("--skip-tests", action="store_true")
    a = ap.parse_args(argv)

    if a.list:
        for i, c in enumerate(CASES, 1):
            print(f"  {i:2d}  {c}")
        return 0

    case = CASES[int(a.case) - 1] if a.case.isdigit() else a.case
    if case not in CASES:
        sys.exit(f"unknown case {case!r}; --list to see them")

    summary: dict[str, object] = {}
    spec, ecores = stage_inputs(case)

    ast_json, e2 = stage_llm(case, spec, ecores, a)
    summary["2 LLM+3 layers"] = None if (ast_json and e2 is None) else False
    if ast_json is None:
        _print_summary(case, summary)
        return 1

    atl, e3 = stage_ast2atl(case, ast_json)
    summary["3 AST->ATL"] = e3 is None
    if atl is None:
        _print_summary(case, summary)
        return 1

    summary["4 ATL_Parser"], _ = stage_parser(case, atl, a)
    summary["5 ATL_Tests"], _ = stage_tests(case, atl, a)

    _print_summary(case, summary)
    return 0 if all(v is not False for v in summary.values()) else 1


def _print_summary(case, summary):
    hdr(f"SUMMARY  ({case})")
    for k, v in summary.items():
        print(f"  {k:18s} {tag(v)}")


if __name__ == "__main__":
    raise SystemExit(main())

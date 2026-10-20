#!/usr/bin/env python3
"""
Iterative Prompting Baseline Runner with Parser Feedback.

This script implements an iterative refinement baseline with a fair generation budget
(default: 5 retries, matching the proposed neuro-symbolic pipeline).
It processes cases sequentially using SELECTED_CASES (same as Neuro_Symbolic_Pipeline/main.py),
skips already generated cases to avoid exhausting LLM quota, and captures ATL parser feedback.

Directory: LLM4ATL_Project/Prompting_Strategies/
Outputs:   LLM4ATL_Project/Prompting_Strategies/output/<strategy>/

Usage:
    python run_iterative_prompting.py
    python run_iterative_prompting.py --strategy few_shot
    python run_iterative_prompting.py --strategy grammar
    python run_iterative_prompting.py --strategy few_shots_AND_grammar
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Fix Windows console UTF-8 encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

# ==============================================================================
# CONFIGURATION & SELECTED CASES (Identical to Neuro_Symbolic_Pipeline/main.py)
# ==============================================================================
# You can comment/uncomment any case here to control which ones to run:
SELECTED_CASES = [
    "Class2Interface_All",
    "Document2Report_All",
    "Item2Product_All",
    "User2Account_All",
    "NetworkToGraph_All",
    "FamiliesToPersons_All",
    "AmaltheaToAscet_All",
    "BibTeX2DocBook_All",
    "XML2DSL_All",
    "PetriNet2Grafcet_All",
    "Grafcet2PetriNet_All",
    "DSL2KM3_All",
    "IEEE1471_2_MoDAF_All",
    "Make2Ant_All",
    "CPL2SPL_All"

]

# Default maximum repair attempts (Attempt 0 = initial, Attempt 1-5 = retries)
DEFAULT_MAX_RETRIES = 5

# Delay between LLM calls to prevent 429 Rate Limits
DELAY_BETWEEN_CALLS_SEC = 5

# ==============================================================================
# PATH SETUP & ENVIRONMENT
# ==============================================================================
STRATEGIES_DIR = Path(__file__).resolve().parent
PROJECT_DIR = STRATEGIES_DIR.parent
PIPELINE_DIR = PROJECT_DIR / "Neuro_Symbolic_Pipeline"
PARSER_DIR = PROJECT_DIR / "ATL_Parser"

from dotenv import load_dotenv
load_dotenv(STRATEGIES_DIR / ".env", override=True)
load_dotenv(PIPELINE_DIR / ".env", override=False)
load_dotenv(PROJECT_DIR / ".env", override=False)

sys.path.insert(0, str(PIPELINE_DIR))
try:
    from pipeline.generation.llm_client import create_llm_client, LLMConfigurationError
    LLM_CLIENT = create_llm_client()
except Exception as e:
    print(f"[Warning] Failed to import pipeline LLM_CLIENT ({e}).")
    LLM_CLIENT = None

N8N_DIR = STRATEGIES_DIR / "n8n-docker"
MODELS_DIR = N8N_DIR / "models"
MAPPING_FILE = MODELS_DIR / "mapping.json"
PROMPTS_DIR = N8N_DIR / "mtl_snippets" / "ATLAS_transformation_language" / "prompts" / "additional_prompts"
FEW_SHOT_FILE = N8N_DIR / "few_shot_examples" / "atl" / "Examples.txt"
GRAMMAR_FILE = N8N_DIR / "grammar" / "atl" / "EBNF.txt"

SYSTEM_MESSAGE = """You are an expert developer for the **ATLAS Transformation Language (ATL)** (model transformation DSL).
Your job is to translate the user’s natural-language specification into a complete, syntactically valid .atl file.

Rules  
1. Follow the ATL grammar exactly (module header, create section, matched/called rules, helpers, OCL expressions, etc.). 
2. Use the module, transformation, and rule names provided by the user whenever they are specified.  
3. If a name is missing, invent a concise, CamelCase name that matches the intent.
5. Do not wrap it in Markdown fences, and do not add commentary,
   explanations, or blank lines beyond what the language requires."""


def load_mapping() -> dict[str, list[str]]:
    with open(MAPPING_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def build_initial_prompt(task_name: str, strategy: str, mapping: dict[str, list[str]]) -> str:
    task_prompt_file = PROMPTS_DIR / f"{task_name}.txt"
    if not task_prompt_file.exists():
        raise FileNotFoundError(f"Task prompt not found: {task_prompt_file}")
    task_prompt = task_prompt_file.read_text(encoding="utf-8").strip()

    model_relative_paths = mapping.get(task_name, [])
    concatenated_models = []
    for rel_p in model_relative_paths:
        m_file = MODELS_DIR / rel_p
        if not m_file.exists():
            raise FileNotFoundError(f"Metamodel file not found: {m_file}")
        concatenated_models.append(m_file.read_text(encoding="utf-8").strip())
    concatenated_models_str = "\n\n".join(concatenated_models)

    prompt = (
        f"{task_prompt}\n\n"
        f"-- End of request.\n"
        f"Here are the models:\n"
        f"{concatenated_models_str}\n\n"
        f'The models are located here:\n'
        f'"http://vitruv.tools/methodologisttemplate/[modelname]"\n'
    )

    if strategy in ("few_shot", "few_shots_AND_grammar") and FEW_SHOT_FILE.exists():
        examples = FEW_SHOT_FILE.read_text(encoding="utf-8").strip()
        prompt += f"\nHere are some examples as guideline:\n{examples}\n"

    if strategy in ("grammar", "few_shots_AND_grammar") and GRAMMAR_FILE.exists():
        grammar = GRAMMAR_FILE.read_text(encoding="utf-8").strip()
        prompt += f"\nHere is the grammar of the Language:\n{grammar}\n"

    return prompt


def build_repair_prompt(previous_code: str, error_details: list[str]) -> str:
    errors_str = "\n".join(f"  - {err}" for err in error_details)
    return (
        f"The previous ATL code failed with the following syntax error(s) reported by the ATL parser:\n"
        f"{errors_str}\n\n"
        f"Here is your previous ATL code:\n"
        f"```atl\n{previous_code}\n```\n\n"
        f"Please fix all errors and return ONLY the complete, syntactically valid .atl file. "
        f"Follow all ATL grammar rules strictly. Do not include markdown code fences or commentary."
    )


def clean_atl_code(raw_text: str) -> str:
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def check_atl_syntax(task_name: str, atl_code: str) -> tuple[bool, int, list[str]]:
    """
    Parses a single ATL candidate using a dedicated temp folder.
    Returns: (is_parsed, problem_count, list_of_error_descriptions)
    """
    temp_dir = Path(tempfile.mkdtemp(prefix=f"atl_eval_{task_name}_"))
    try:
        test_file = temp_dir / f"{task_name}.atl"
        test_file.write_text(atl_code, encoding="utf-8")

        mvn_cmd = "mvn.cmd" if os.name == "nt" else "mvn"
        result = subprocess.run(
            [
                mvn_cmd,
                "-q",
                "test",
                "-Dtest=com.example.atlparser.AtlParserTest",
                f"-Datl.test.resources.dir={temp_dir}"
            ],
            cwd=PARSER_DIR,
            capture_output=True,
            text=True,
            timeout=120,
            shell=False,
        )

        stdout = result.stdout
        is_parsed = False
        problem_count = 0
        errors = []

        for line in stdout.splitlines():
            line_s = line.strip()
            if line_s.startswith(f"OK: {task_name}.atl"):
                is_parsed = True
                problem_count = 0
                break
            elif line_s.startswith(f"FAIL: {task_name}.atl"):
                is_parsed = False
                payload = line_s.removeprefix(f"FAIL: {task_name}.atl").strip()
                if "(" in payload:
                    try:
                        problem_count = int(payload.split("(")[1].split()[0])
                    except Exception:
                        problem_count = 1
            elif line_s.startswith("- ") and "Problem@" in line_s:
                # Extract clean error description
                # Example: - org.eclipse.m2m.atl.common.Problem.Problem@xxx (severity: error, location: 1:14, description: ...)
                match = re.search(r"location:\s*([^,]+),\s*description:\s*(.+)\)", line_s)
                if match:
                    loc, desc = match.group(1), match.group(2)
                    errors.append(f"At {loc}: {desc}")
                else:
                    errors.append(line_s[2:].strip())

        if not is_parsed and problem_count == 0 and result.returncode != 0:
            problem_count = max(len(errors), 1)

        return is_parsed, problem_count, errors

    except subprocess.TimeoutExpired:
        return False, 1, ["ATL parser execution timed out (exceeded 120s)"]
    except Exception as e:
        return False, 1, [f"Parser runner exception: {e}"]
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def call_llm(prompt: str, instructions: str = SYSTEM_MESSAGE) -> str:
    if LLM_CLIENT is not None:
        return LLM_CLIENT.generate(prompt=prompt, instructions=instructions)
    raise RuntimeError("LLM_CLIENT is not initialized. Check your .env file.")


def process_single_task(task_name: str, strategy: str, mapping: dict[str, list[str]], max_retries: int, output_dir: Path, traces_dir: Path):
    final_atl_path = output_dir / f"{task_name}.atl"
    final_trace_path = traces_dir / f"{task_name}_trace.json"

    # Skip if already exists
    if final_atl_path.exists() and final_trace_path.exists():
        print(f"\n--- Skipping: {task_name} (already exists in output) ---")
        return

    print(f"\n" + "=" * 70)
    print(f" Processing Task: {task_name} | Strategy: {strategy}")
    print("=" * 70)

    task_trace = {
        "task": task_name,
        "strategy": strategy,
        "max_retries": max_retries,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "attempts": [],
        "final_status": "PENDING",
        "total_attempts": 0,
    }

    # Attempt 0: Initial Generation
    print(f"[*] [Attempt 0] Generating initial ATL code ... ", end="", flush=True)
    t0 = time.time()
    try:
        initial_prompt = build_initial_prompt(task_name, strategy, mapping)
        raw_code = call_llm(initial_prompt, SYSTEM_MESSAGE)
        clean_code = clean_atl_code(raw_code)
    except Exception as e:
        print(f"\n[Error] LLM generation failed for {task_name}: {e}")
        return

    elapsed = time.time() - t0
    print(f"done ({elapsed:.1f}s)")

    # Check Attempt 0
    print(f"[*] [Attempt 0] Checking with ATL Parser ... ", end="", flush=True)
    is_parsed, prob_count, errors = check_atl_syntax(task_name, clean_code)
    if is_parsed:
        print(f"PASS (0 problems!)")
    else:
        print(f"FAIL ({prob_count} problems)")

    task_trace["attempts"].append({
        "attempt": 0,
        "prompt": initial_prompt,
        "code": clean_code,
        "elapsed_seconds": elapsed,
        "parsed": is_parsed,
        "problem_count": prob_count,
        "errors": errors,
    })
    task_trace["total_attempts"] = 1

    current_code = clean_code
    current_errors = errors

    # Repair Loop: Attempt 1 to max_retries
    if not is_parsed:
        for retry in range(1, max_retries + 1):
            time.sleep(DELAY_BETWEEN_CALLS_SEC)
            print(f"[*] [Repair Attempt {retry}/{max_retries}] Sending feedback to LLM ... ", end="", flush=True)
            t0 = time.time()
            repair_prompt = build_repair_prompt(current_code, current_errors)

            try:
                raw_code = call_llm(repair_prompt, SYSTEM_MESSAGE)
                current_code = clean_atl_code(raw_code)
            except Exception as e:
                print(f"\n[Error] LLM repair failed at attempt {retry}: {e}")
                break

            elapsed = time.time() - t0
            print(f"done ({elapsed:.1f}s)")

            # Check repaired code
            print(f"[*] [Repair Attempt {retry}] Checking with ATL Parser ... ", end="", flush=True)
            is_parsed, prob_count, current_errors = check_atl_syntax(task_name, current_code)

            task_trace["attempts"].append({
                "attempt": retry,
                "prompt": repair_prompt,
                "code": current_code,
                "elapsed_seconds": elapsed,
                "parsed": is_parsed,
                "problem_count": prob_count,
                "errors": current_errors,
            })
            task_trace["total_attempts"] += 1

            if is_parsed:
                print(f"FIXED! (Parsed cleanly with 0 problems)")
                break
            else:
                print(f"FAIL ({prob_count} problems remaining)")

    # Finalize task
    task_trace["final_status"] = "PARSED" if is_parsed else "MAX_RETRIES_REACHED"
    task_trace["final_code"] = current_code

    # Save final ATL
    final_atl_path.write_text(current_code, encoding="utf-8")
    # Save trace JSON
    final_trace_path.write_text(json.dumps(task_trace, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"[Done] Result saved: {final_atl_path.name} | Status: {task_trace['final_status']} | Total attempts: {task_trace['total_attempts']}")


def main():
    parser = argparse.ArgumentParser(description="Run Iterative Prompting Baseline with ATL Parser Feedback")
    parser.add_argument(
        "--strategy",
        type=str,
        default="only_prompt",
        choices=["only_prompt", "few_shot", "grammar", "few_shots_AND_grammar"],
        help="Prompting strategy to run (default: only_prompt)",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=DEFAULT_MAX_RETRIES,
        help=f"Maximum repair attempts (default: {DEFAULT_MAX_RETRIES})",
    )
    args = parser.parse_args()

    mapping = load_mapping()

    output_dir = STRATEGIES_DIR / "output" / args.strategy
    traces_dir = output_dir / "traces"
    output_dir.mkdir(parents=True, exist_ok=True)
    traces_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 80)
    print(f" ITERATIVE PROMPTING BASELINE RUNNER")
    print(f" Strategy: {args.strategy} | Default Retries: {args.max_retries}")
    print(f" Target Cases ({len(SELECTED_CASES)}): {', '.join(SELECTED_CASES)}")
    print("=" * 80)

    for task_name in SELECTED_CASES:
        process_single_task(task_name, args.strategy, mapping, args.max_retries, output_dir, traces_dir)
        time.sleep(DELAY_BETWEEN_CALLS_SEC)

    print("\n" + "=" * 80)
    print(f" ALL SELECTED CASES COMPLETED FOR STRATEGY: {args.strategy}")
    print(f" Output folder: {output_dir}")
    print("=" * 80)


if __name__ == "__main__":
    main()

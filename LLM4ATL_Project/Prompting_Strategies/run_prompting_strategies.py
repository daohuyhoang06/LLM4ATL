#!/usr/bin/env python3
"""Run each ATL prompting strategy once per task and record comparable metrics.

Each task makes exactly one LLM request. Generated ATL files are saved to
``output/<strategy>/`` and aggregate per-task metrics are written to that
strategy's ``run_summary.json``.

Usage:
    python run_prompting_strategies.py
    python run_prompting_strategies.py --strategy few_shot
    python run_prompting_strategies.py --strategy grammar
    python run_prompting_strategies.py --strategy few_shots_AND_grammar
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

SELECTED_CASES = [
    "Class2Interface_All", "Document2Report_All", "Item2Product_All",
    "User2Account_All", "NetworkToGraph_All", "FamiliesToPersons_All",
    "AmaltheaToAscet_All", "BibTeX2DocBook_All", "XML2DSL_All",
    "PetriNet2Grafcet_All", "Grafcet2PetriNet_All", "DSL2KM3_All",
    "IEEE1471_2_MoDAF_All", "Make2Ant_All", "CPL2SPL_All",
]

# A short pause avoids rate limiting between separate task requests.
DELAY_BETWEEN_TASKS_SEC = 5


def current_timestamp() -> str:
    """Return an ISO-8601 timestamp with the local UTC offset."""
    return datetime.now().astimezone().isoformat(timespec="seconds")

STRATEGIES_DIR = Path(__file__).resolve().parent
PROJECT_DIR = STRATEGIES_DIR.parent
PIPELINE_DIR = PROJECT_DIR / "Neuro_Symbolic_Pipeline"

from dotenv import load_dotenv

# Load configuration from the least to the most specific scope.  Pipeline
# credentials must override any stale values inherited from the terminal;
# a strategy-local .env, when present, can intentionally override Pipeline.
load_dotenv(PROJECT_DIR / ".env", override=False)
load_dotenv(PIPELINE_DIR / ".env", override=True)
load_dotenv(STRATEGIES_DIR / ".env", override=True)

sys.path.insert(0, str(PIPELINE_DIR))
try:
    from pipeline.generation.llm_client import create_llm_client

    LLM_CLIENT = create_llm_client()
except Exception as error:
    print(f"[Warning] Failed to initialize the LLM client ({error}).")
    LLM_CLIENT = None

N8N_DIR = STRATEGIES_DIR / "n8n-docker"
MODELS_DIR = N8N_DIR / "models"
MAPPING_FILE = MODELS_DIR / "mapping.json"
# This directory contains the complete, project-specific set of 15 prompts.
PROMPTS_DIR = N8N_DIR / "mtl_snippets" / "ATLAS_transformation_language" / "prompts" / "additional_prompts"
FEW_SHOT_FILE = N8N_DIR / "few_shot_examples" / "atl" / "Examples.txt"
GRAMMAR_FILE = N8N_DIR / "grammar" / "atl" / "EBNF.txt"

SYSTEM_MESSAGE = """You are an expert developer for the **ATLAS Transformation Language (ATL)** (model transformation DSL).
Your job is to translate the user’s natural-language specification into a complete, syntactically valid .atl file.

Rules
1. Follow the ATL grammar exactly (module header, create section, matched/called rules, helpers, OCL expressions, etc.).
2. Use the module, transformation, and rule names provided by the user whenever they are specified.
3. If a name is missing, invent a concise, CamelCase name that matches the intent.
5. Do **not** wrap it in Markdown fences, and do **not** add commentary,
   explanations, or blank lines beyond what the language requires."""


def load_mapping() -> dict[str, list[str]]:
    return json.loads(MAPPING_FILE.read_text(encoding="utf-8"))


def build_initial_prompt(task_name: str, strategy: str, mapping: dict[str, list[str]]) -> str:
    task_prompt_file = PROMPTS_DIR / f"{task_name}.txt"
    if not task_prompt_file.exists():
        raise FileNotFoundError(f"Task prompt not found: {task_prompt_file}")

    model_texts = []
    for relative_path in mapping.get(task_name, []):
        model_file = MODELS_DIR / relative_path
        if not model_file.exists():
            raise FileNotFoundError(f"Metamodel file not found: {model_file}")
        model_texts.append(model_file.read_text(encoding="utf-8").strip())

    prompt = (
        f"{task_prompt_file.read_text(encoding='utf-8').strip()}\n\n"
        "-- End of request.\n"
        f"Here are the models:\n{'\n\n'.join(model_texts)}\n\n"
        'The models are located here:\n'
        '"http://vitruv.tools/methodologisttemplate/[modelname]"\n'
    )
    if strategy in {"few_shot", "few_shots_AND_grammar"}:
        prompt += f"\nHere are some examples as guideline:\n{FEW_SHOT_FILE.read_text(encoding='utf-8').strip()}\n"
    if strategy in {"grammar", "few_shots_AND_grammar"}:
        prompt += f"\nHere is the grammar of the Language:\n{GRAMMAR_FILE.read_text(encoding='utf-8').strip()}\n"
    return prompt


def generate_with_metrics(prompt: str) -> tuple[str, dict[str, int | None], float]:
    if LLM_CLIENT is None:
        raise RuntimeError("LLM client is not initialized. Check the .env configuration.")
    started_at = time.perf_counter()
    text, usage = LLM_CLIENT.generate_with_usage(prompt=prompt, instructions=SYSTEM_MESSAGE)
    return text, usage, time.perf_counter() - started_at


def load_previous_results(summary_path: Path) -> dict[str, dict]:
    """Load prior per-task summary entries so skipped outputs retain metrics."""
    if not summary_path.exists():
        return {}
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"[Warning] Existing summary is invalid: {summary_path}")
        return {}
    return {
        entry["task"]: entry
        for entry in summary.get("tasks", [])
        if isinstance(entry, dict) and entry.get("task")
    }


def process_single_task(
    task_name: str,
    strategy: str,
    mapping: dict[str, list[str]],
    output_dir: Path,
    previous_results: dict[str, dict],
    force: bool,
) -> dict:
    """Run one Gemini-equivalent prompting strategy once for one task."""
    print(f"\n{'=' * 70}\nProcessing task: {task_name} | Strategy: {strategy}\n{'=' * 70}")
    final_atl_path = output_dir / f"{task_name}.atl"

    if final_atl_path.exists() and not force:
        print(f"[Skip] Output already exists: {final_atl_path.name}")
        previous = previous_results.get(task_name, {})
        return {
            "task": task_name,
            "strategy": strategy,
            "timestamp": current_timestamp(),
            "generation_count": 0,
            "metrics": previous.get("metrics", {
                "task_elapsed_seconds": 0,
                "input_tokens": None,
                "output_tokens": None,
                "total_tokens": None,
            }),
            "final_status": "SKIPPED_EXISTING",
        }

    task_started_at = time.perf_counter()
    trace = {
        "task": task_name,
        "strategy": strategy,
        "timestamp": current_timestamp(),
        "generation_count": 1,
    }
    try:
        prompt = build_initial_prompt(task_name, strategy, mapping)
        raw_code, usage, llm_elapsed = generate_with_metrics(prompt)
        total_elapsed = time.perf_counter() - task_started_at
        metrics = {
            "task_elapsed_seconds": round(total_elapsed, 3),
            "llm_elapsed_seconds": round(llm_elapsed, 3),
            "input_tokens": usage.get("input_tokens"),
            "output_tokens": usage.get("output_tokens"),
            "total_tokens": usage.get("total_tokens"),
        }
        trace.update({"metrics": metrics, "final_status": "GENERATED"})
        # Match the Gemini n8n workflows: save the model response directly.
        final_atl_path.write_text(raw_code, encoding="utf-8")
        print(
            f"[Metrics] total task: {metrics['task_elapsed_seconds']:.3f}s | "
            f"input tokens: {metrics['input_tokens']} | output tokens: {metrics['output_tokens']}"
        )
        print(f"[Output] Saved: {task_name}.atl")
    except Exception as error:
        metrics = {"task_elapsed_seconds": round(time.perf_counter() - task_started_at, 3), "input_tokens": None, "output_tokens": None}
        trace.update({"metrics": metrics, "final_status": "ERROR", "error": str(error)})
        print(f"[Error] {task_name}: {error}")

    return trace


def main() -> None:
    parser = argparse.ArgumentParser(description="Run each ATL prompting strategy once per task")
    parser.add_argument("--strategy", default="only_prompt", choices=["only_prompt", "few_shot", "grammar", "few_shots_AND_grammar"])
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate tasks even when their .atl output already exists.",
    )
    args = parser.parse_args()

    output_dir = STRATEGIES_DIR / "output" / args.strategy
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "run_summary.json"
    previous_results = load_previous_results(summary_path)
    mapping = load_mapping()

    print(f"{'=' * 80}\nGEMINI PROMPTING STRATEGY RUNNER (one LLM call per task)\nStrategy: {args.strategy}\nTasks ({len(SELECTED_CASES)}): {', '.join(SELECTED_CASES)}\n{'=' * 80}")
    traces = []
    for index, task_name in enumerate(SELECTED_CASES):
        output_already_exists = (output_dir / f"{task_name}.atl").exists() and not args.force
        traces.append(process_single_task(
            task_name, args.strategy, mapping, output_dir, previous_results, args.force
        ))
        if index < len(SELECTED_CASES) - 1 and not output_already_exists:
            time.sleep(DELAY_BETWEEN_TASKS_SEC)

    summary = {
        "strategy": args.strategy,
        "timestamp": current_timestamp(),
        "tasks": [
            {
                "task": trace["task"],
                "status": trace["final_status"],
                "metrics": trace["metrics"],
                **({"error": trace["error"]} if "error" in trace else {}),
            }
            for trace in traces
        ],
    }
    summary["totals"] = {
        "input_tokens": sum(item["metrics"].get("input_tokens") or 0 for item in summary["tasks"]),
        "output_tokens": sum(item["metrics"].get("output_tokens") or 0 for item in summary["tasks"]),
        "total_tokens": sum(item["metrics"].get("total_tokens") or 0 for item in summary["tasks"]),
        "task_elapsed_seconds": round(sum(item["metrics"].get("task_elapsed_seconds") or 0 for item in summary["tasks"]), 3),
        "llm_elapsed_seconds": round(sum(item["metrics"].get("llm_elapsed_seconds") or 0 for item in summary["tasks"]), 3),
    }
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nCompleted {len(traces)} tasks. Summary: {summary_path}")
    print(
        f"Total input tokens: {summary['totals']['input_tokens']} | "
        f"Total output tokens: {summary['totals']['output_tokens']} | "
        f"Total tokens: {summary['totals']['total_tokens']}"
    )


if __name__ == "__main__":
    main()

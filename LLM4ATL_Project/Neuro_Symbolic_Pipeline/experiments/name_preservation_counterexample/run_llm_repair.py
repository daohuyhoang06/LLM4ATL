#!/usr/bin/env python3
"""Send a real NamePreservation SAT witness to the configured pipeline LLM."""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PIPELINE_DIR = HERE.parent.parent
sys.path.insert(0, str(PIPELINE_DIR))

import main  # noqa: E402 - loads the same LLM configuration and prompt as the pipeline
from pipeline.formal_verification import run_case  # noqa: E402
from pipeline.formal_verification.ast2atl import ATLGenerator  # noqa: E402
from pipeline.static_analysis.atl_semantic_checker import ATLSemanticChecker  # noqa: E402
from pipeline.static_analysis.ecore_registry import ATLEcoreRegistry  # noqa: E402
from pipeline.static_analysis.type_environment import TypeEnvironment  # noqa: E402
from pipeline.structural_checking.schema.atl_ast import Module  # noqa: E402


CASE = "Document2Report_All"
CHECK = "Document::NamePreservation"
CONSTRAINTS = HERE / "constraints" / "direct"
OUTPUT = HERE / "results" / "llm_repair"
WRONG_ATL = HERE / "atl" / "wrong_name_binding.atl"


def verify(atl: Path, label: str, source: Path, target: Path) -> dict:
    root = OUTPUT / label
    ecore = root / f"{CASE}_ATL2TM.ecore"
    run_case.run_atl2tm(CASE, atl, source, target, ecore,
                        root / "atl2tm-work", verbose=False)
    efinder_dir = root / "efinder"
    exit_code = run_case.run_efinder(
        CASE, ecore, CONSTRAINTS, efinder_dir, CHECK, 3, 6, 180_000,
        verbose=False,
    )
    matches = list(efinder_dir.glob(f"*__Document__NamePreservation.result.json"))
    if exit_code or len(matches) != 1:
        raise RuntimeError(f"eFinder failed for {label}: exit={exit_code}, results={matches}")
    return json.loads(matches[0].read_text(encoding="utf-8"))


def main_experiment() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    model_paths = [main.resolve_metamodel_path(path)
                   for path in main.mapping[CASE]]
    source, target = model_paths
    prompt_content = (main.PROMPTS_DIR / f"{CASE}.txt").read_text(encoding="utf-8")
    model_content = "".join(path.read_text(encoding="utf-8") + "\n\n"
                            for path in model_paths)

    initial = verify(WRONG_ATL, "initial_wrong_atl", source, target)
    if initial.get("status") != "SAT":
        raise RuntimeError(f"The seeded wrong ATL must produce SAT: {initial}")
    feedback = run_case._counterexample_feedback([initial], CONSTRAINTS)
    (OUTPUT / "feedback_to_llm.txt").write_text(feedback + "\n", encoding="utf-8")
    print("Initial NamePreservation: SAT; feedback saved.", flush=True)

    attempts = []
    for number in range(1, main.MAX_RETRIES + 1):
        attempt_dir = OUTPUT / f"repair_{number}"
        attempt_dir.mkdir(parents=True, exist_ok=True)
        prompt = main.build_prompt(prompt_content, model_content, feedback)
        (attempt_dir / "prompt_to_llm.txt").write_text(prompt, encoding="utf-8")
        print(f"Repair {number}: requesting {main.LLM_CLIENT.provider}/"
              f"{main.LLM_CLIENT.model_name}...", flush=True)
        response, usage = main.LLM_CLIENT.generate_with_usage(
            prompt, instructions=main.system_prompt,
        )
        (attempt_dir / "raw_response.txt").write_text(response, encoding="utf-8")
        record = {"attempt": number, "usage": usage}
        attempts.append(record)
        try:
            data = json.loads(main.extract_json(response))
            ast = Module(**data)
            registry = ATLEcoreRegistry([str(source), str(target)])
            ATLSemanticChecker.check_module(
                ast, TypeEnvironment(registry=registry), main.ABLATION_CONFIG,
            )
            data = ast.model_dump()
            (attempt_dir / "repaired_ast.json").write_text(
                json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
            )
            atl = attempt_dir / "repaired.atl"
            atl.write_text(ATLGenerator(data).generate(), encoding="utf-8")
            result = verify(atl, f"verified_repair_{number}", source, target)
            record["layer3_status"] = result.get("status")
            record["atl_file"] = str(atl)
            print(f"Repair {number}: Layer 3 = {record['layer3_status']}", flush=True)
            if result.get("status") == "UNSAT":
                break
            if result.get("status") == "SAT":
                feedback = run_case._counterexample_feedback([result], CONSTRAINTS)
            else:
                feedback = str(result.get("detail") or result)
        except Exception as error:
            record["error"] = f"{type(error).__name__}: {error}"
            feedback = record["error"]
            print(f"Repair {number}: {feedback}", flush=True)
        (attempt_dir / "feedback_for_next_attempt.txt").write_text(
            feedback + "\n", encoding="utf-8",
        )

    summary = {
        "case": CASE,
        "check": CHECK,
        "provider": main.LLM_CLIENT.provider,
        "model": main.LLM_CLIENT.model_name,
        "initial_status": initial["status"],
        "feedback_file": str(OUTPUT / "feedback_to_llm.txt"),
        "attempts": attempts,
        "repaired": bool(attempts and attempts[-1].get("layer3_status") == "UNSAT"),
    }
    (OUTPUT / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False), flush=True)
    return 0 if summary["repaired"] else 1


if __name__ == "__main__":
    raise SystemExit(main_experiment())

import os
import glob
import json
import time
import sys
import re
from datetime import datetime
from pathlib import Path
# Keep gRPC's repeated TLS handshake diagnostics from flooding the pipeline
# output; the first actionable exception is still reported below.
os.environ.setdefault("GRPC_VERBOSITY", "ERROR")
from pydantic import ValidationError
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent
PIPELINE_DIR = PROJECT_DIR / "pipeline"
from config.ablation_config import AblationConfig
from pipeline.generation.llm_client import LLMConfigurationError, create_llm_client
from pipeline.static_analysis.ecore_registry import ATLEcoreRegistry
from pipeline.static_analysis.type_environment import TypeEnvironment
from pipeline.static_analysis.atl_semantic_checker import ATLSemanticChecker
from pipeline.static_analysis.errors import SemanticError
from pipeline.structural_checking.schema.atl_ast import Module

# Windows PowerShell may expose a cp1252 stream; pipeline diagnostics contain
# Vietnamese text and must not crash before the first stage starts.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)

# Load environment variables from the project directory even when the
# command is launched from the repository root or another working directory.
load_dotenv(PROJECT_DIR / '.env', override=True)
try:
    LLM_CLIENT = create_llm_client()
except LLMConfigurationError as error:
    print(f"[LLM configuration error] {error}")
    sys.exit(1)
ABLATION_CONFIG = AblationConfig.from_env()
ABLATION_RUN_LABEL = os.getenv("ABLATION_RUN_LABEL", "").strip()


def _read_int_env(name, default, minimum):
    """Read a bounded-search setting and fail early with an actionable error."""
    raw = os.getenv(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        value = int(str(raw).strip())
    except ValueError as error:
        raise ValueError(f"{name} must be an integer, got {raw!r}") from error
    if value < minimum:
        raise ValueError(f"{name} must be >= {minimum}, got {value}")
    return value


# Layer 3 bounded-search settings. Override these in .env; a higher
# object scope can substantially increase solver time.
EFINDER_SCOPE = _read_int_env("EFINDER_SCOPE", 3, 1)
EFINDER_REFERENCE_SCOPE = _read_int_env("EFINDER_REFERENCE_SCOPE", 6, 0)
EFINDER_TIMEOUT_MS = _read_int_env("EFINDER_TIMEOUT_MS", 300_000, 1)

# Project paths
INPUT_DIR = PROJECT_DIR / 'input'
PROMPTS_DIR = INPUT_DIR / 'prompts' / 'user_prompts'
METAMODELS_DIR = INPUT_DIR / 'ATL_metamodel'
SYSTEM_PROMPT_PATH = INPUT_DIR / 'prompts' / 'system_prompt.txt'
MAPPING_PATH = INPUT_DIR / 'mapping.json'

# Full runs retain output/. Each ablation must use an isolated output root so
# existing candidates cannot be skipped or overwritten by another condition.
if ABLATION_RUN_LABEL:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", ABLATION_RUN_LABEL):
        raise ValueError(
            "ABLATION_RUN_LABEL may contain only letters, numbers, underscores, "
            "and hyphens, and must begin with a letter or number."
        )
    OUTPUT_DIR = PROJECT_DIR / 'output' / 'ablation' / ABLATION_RUN_LABEL
elif not all((
    ABLATION_CONFIG.enable_layer1_schema,
    ABLATION_CONFIG.enable_layer2_semantic,
    ABLATION_CONFIG.enable_layer3_generation,
)):
    raise ValueError(
        "Set ABLATION_RUN_LABEL (for example, without_l2) whenever a "
        "verification layer is disabled."
    )
else:
    OUTPUT_DIR = PROJECT_DIR / 'output'

FINAL_RESPONSES_DIR = OUTPUT_DIR / 'final_responses'
AST_OUTPUT_DIR = FINAL_RESPONSES_DIR / 'atl_ast'
ATL_OUTPUT_DIR = FINAL_RESPONSES_DIR / 'atl'
FORMAL_VERIFICATION_OUTPUT_DIR = OUTPUT_DIR / 'formal_verification'
LAYER3_OUTPUT_DIR = FORMAL_VERIFICATION_OUTPUT_DIR / 'pipeline_attempts'
CANDIDATES_DIR = FORMAL_VERIFICATION_OUTPUT_DIR / 'candidates'
METRICS_DIR = OUTPUT_DIR / 'metrics'

MAX_RETRIES = 5
RETRY_DELAY_SECONDS = 10

# Existing function names are preserved while the rest of main.py is
# incrementally refactored.
RESPONSES_DIR = AST_OUTPUT_DIR
AST2ATL_DIR = ATL_OUTPUT_DIR

for output_dir in (AST_OUTPUT_DIR, ATL_OUTPUT_DIR, FORMAL_VERIFICATION_OUTPUT_DIR, METRICS_DIR):
    output_dir.mkdir(parents=True, exist_ok=True)

# Load System Prompt
with open(SYSTEM_PROMPT_PATH, 'r', encoding='utf-8') as f:
    system_prompt_template = f.read()

# Load Schema JSON string directly from Pydantic definition
schema_json = json.dumps(
    Module.model_json_schema(),
    ensure_ascii=False,
    separators=(",", ":"),
)
system_prompt = system_prompt_template.replace('<INSERT_SCHEMA_HERE>', schema_json)

# Load Mapping
with open(MAPPING_PATH, 'r', encoding='utf-8') as f:
    mapping = json.load(f)


def resolve_metamodel_path(relative_path):
    """Resolve an old mapping entry against input/ATL_metamodel/."""
    path = Path(relative_path)
    if path.parts and path.parts[0] == 'ATL_model':
        path = Path(*path.parts[1:])
    return METAMODELS_DIR / path

def build_prompt(prompt_content, model_content, validation_error=""):
    """Build the user-level input; system guidance is sent separately."""
    prompt = f"=== ECORE MODELS ===\n{model_content}\n\n=== TRANSFORMATION REQUEST ===\n{prompt_content}"
    if validation_error:
        prompt += ("\n\n=== PREVIOUS ATTEMPT FAILED VALIDATION OR FORMAL VERIFICATION ===\n"
                   "Repair the AST and return JSON only. Details:\n"
                   f"{validation_error}")
    return prompt

def extract_json(response_text):
    text = response_text.strip()
    if text.startswith('```json'):
        text = text[7:]
    elif text.startswith('```'):
        text = text[3:]
    if text.endswith('```'):
        text = text[:-3]
    return text.strip()


def save_last_candidate(basename, data, atl_path=None):
    """Persist the last candidate in the normal AST/ATL output locations."""
    if data is not None:
        Path(RESPONSES_DIR).mkdir(parents=True, exist_ok=True)
        (Path(RESPONSES_DIR) / f'{basename}.json').write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8'
        )
    if atl_path is not None and Path(atl_path).is_file():
        Path(AST2ATL_DIR).mkdir(parents=True, exist_ok=True)
        (Path(AST2ATL_DIR) / f'{basename}.atl').write_text(
            Path(atl_path).read_text(encoding='utf-8'), encoding='utf-8'
        )


def generate_final_atl_from_ast(basename, data):
    """Convert a valid final AST to ATL when Layer 2 exhausts its retries."""
    try:
        from pipeline.formal_verification.ast2atl import ATLGenerator

        atl_code = ATLGenerator(data).generate()
        final_atl = Path(AST2ATL_DIR) / f'{basename}.atl'
        final_atl.parent.mkdir(parents=True, exist_ok=True)
        final_atl.write_text(atl_code, encoding='utf-8')
        return final_atl
    except Exception as error:
        print(f"[{basename}] Could not convert the final AST to ATL: {error}")
        return None


def current_timestamp():
    """Return an ISO-8601 timestamp with the machine's local UTC offset."""
    return datetime.now().astimezone().isoformat(timespec="seconds")


def write_json(path, payload):
    """Write JSON atomically so an interrupted run does not leave a partial trace."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    temporary_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    temporary_path.replace(path)


def read_json(path):
    """Read a JSON metrics file, returning None when it is absent or invalid."""
    path = Path(path)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"[Metrics] Could not read {path}: {error}")
        return None


def summarize_task_trace(trace, task_started_at, final_status, termination_reason):
    """Finalize cumulative token and timing metrics for one testcase."""
    attempts = trace["attempts"]
    task_elapsed_seconds = round(time.perf_counter() - task_started_at, 3)
    retry_sleep_seconds = trace.get("retry_sleep_seconds", 0)

    def total_from_attempts(field):
        return sum(
            attempt.get("llm", {}).get(field) or 0
            for attempt in attempts
        )

    trace["finished_at"] = current_timestamp()
    trace["summary"] = {
        "final_status": final_status,
        "termination_reason": termination_reason,
        "llm_attempts": len(attempts),
        "repair_iterations": max(0, len(attempts) - 1),
        "max_repair_iterations": MAX_RETRIES,
        "repair_limit_exhausted": termination_reason == "REPAIR_LIMIT_EXHAUSTED",
        "task_elapsed_seconds": task_elapsed_seconds,
        "retry_sleep_seconds": retry_sleep_seconds,
        "active_elapsed_seconds": round(
            max(0, task_elapsed_seconds - retry_sleep_seconds), 3
        ),
        "llm_elapsed_seconds": round(sum(
            attempt.get("llm", {}).get("elapsed_seconds") or 0
            for attempt in attempts
        ), 3),
        "input_tokens": total_from_attempts("input_tokens"),
        "output_tokens": total_from_attempts("output_tokens"),
        "total_tokens": total_from_attempts("total_tokens"),
    }
    return trace


def run_layer3(basename, data, model_full_paths, attempt, ablation_config):
    """Generate ATL, translate it with ATL2TM, then query eFinder.

    The generated files are first written to attempt-specific folders. The
    caller promotes the last candidate to the normal output locations even
    when verification stops, so the draft is recoverable for debugging.
    """
    if not ablation_config.is_enabled("enable_layer3_generation"):
        print(f"[{basename}] Skipping formal counterexample check (Layer 3 disabled).")
        return "SKIPPED", "", None

    # Keep attempt-specific Layer 3 artefacts with formal-verification output,
    # separate from the normal LLM response directories.
    candidate_ast_dir = CANDIDATES_DIR / 'atl_ast' / basename
    candidate_atl_dir = CANDIDATES_DIR / 'atl' / basename
    candidate_ast = candidate_ast_dir / f'attempt-{attempt + 1}.json'
    candidate_atl = candidate_atl_dir / f'attempt-{attempt + 1}.atl'
    candidate_ast.parent.mkdir(parents=True, exist_ok=True)
    candidate_atl.parent.mkdir(parents=True, exist_ok=True)
    candidate_ast.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')

    try:
        from pipeline.formal_verification.ast2atl import ATLGenerator
        atl_code = ATLGenerator(
            json.loads(candidate_ast.read_text(encoding='utf-8'))
        ).generate()
        candidate_atl.write_text(atl_code, encoding='utf-8')
    except Exception as error:
        detail = f"ast2atl could not generate ATL from the validated AST: {error}"
        print(f"[{basename}] Layer 3 stopped: AST2ATL_ERROR: Could not generate ATL from the AST.", flush=True)
        return "GENERATION_ERROR", detail, None

    print(f"[{basename}] Generated ATL successfully.", flush=True)
    print(f"[{basename}] Converting ATL -> ATL2TM...", flush=True)

    try:
        from pipeline.formal_verification.run_case import verify_atl_for_pipeline
        result = verify_atl_for_pipeline(
            basename,
            candidate_atl,
            Path(model_full_paths[0]),
            Path(model_full_paths[1]),
            output_root=LAYER3_OUTPUT_DIR / basename / f'attempt-{attempt + 1}',
            scope=EFINDER_SCOPE,
            reference_scope=EFINDER_REFERENCE_SCOPE,
            timeout_ms=EFINDER_TIMEOUT_MS,
        )
    except Exception as error:
        # Import/configuration failures are infrastructure failures. Do not
        # send them to the LLM as if changing the ATL could correct them.
        detail = f"Layer 3 could not be initialized: {error}"
        print(f"[Layer 3] {detail}")
        return "EFINDER_ERROR", detail, None

    if not result.status.startswith("ATL2TM_") \
            and result.status != "LAYER3_CONFIGURATION_ERROR":
        print(f"[{basename}] Generated ATL -> ATL2TM successfully.", flush=True)
        print(f"[{basename}] Running eFinder...", flush=True)

    if result.status == "VERIFIED":
        print(f"[{basename}] Layer 3: PASS - no counterexample found.", flush=True)
        final_atl = Path(AST2ATL_DIR) / f'{basename}.atl'
        final_atl.parent.mkdir(parents=True, exist_ok=True)
        final_atl.write_text(atl_code, encoding='utf-8')
        return "VERIFIED", "", final_atl
    if result.status == "COUNTEREXAMPLE":
        print(f"[{basename}] Layer 3: SAT - counterexample found; sending it to the LLM for repair.", flush=True)
        return "COUNTEREXAMPLE", result.feedback, candidate_atl
    print(f"[{basename}] Layer 3 stopped: {result.detail}", flush=True)
    return result.status, result.detail, candidate_atl

def process_file(prompt_file_path, ablation_config=ABLATION_CONFIG, trace_path=None):
    basename = os.path.splitext(os.path.basename(prompt_file_path))[0]
    task_started_at = time.perf_counter()
    trace = {
        "task": basename,
        "provider": LLM_CLIENT.provider,
        "model": LLM_CLIENT.model_name,
        "started_at": current_timestamp(),
        "max_repair_iterations": MAX_RETRIES,
        "max_llm_attempts": MAX_RETRIES + 1,
        "ablation": {
            "run_label": ABLATION_RUN_LABEL or "full",
            "switches": ablation_config.to_dict(),
        },
        "retry_sleep_seconds": 0,
        "attempts": [],
    }

    def persist_trace():
        if trace_path is not None:
            write_json(trace_path, trace)

    def finish_task(final_status, termination_reason):
        summarize_task_trace(trace, task_started_at, final_status, termination_reason)
        persist_trace()
        return trace
    output_path = os.path.join(RESPONSES_DIR, f"{basename}.json")
    if os.path.exists(output_path):
        print(f"\n--- Skipping: {basename} (file already exists) ---")
        # Do not persist this synthetic zero-metric trace. It must not replace
        # the trace collected when this testcase was actually executed.
        summarize_task_trace(trace, task_started_at, "SKIPPED_EXISTING", "OUTPUT_ALREADY_EXISTS")
        return trace

    print(f"\n--- Processing: {basename} ---")
    
    # Read prompt content
    with open(prompt_file_path, 'r', encoding='utf-8') as f:
        prompt_content = f.read()
        
    # Get models
    model_files = mapping.get(basename)
    if not model_files:
        print(f"[Warning] No model mapping found for {basename}")
        return finish_task("MISSING_INPUT", "MISSING_MODEL_MAPPING")
        
    model_content = ""
    model_full_paths = []
    for rel_path in model_files:
        full_path = resolve_metamodel_path(rel_path)
        if full_path.is_file():
            model_content += full_path.read_text(encoding='utf-8') + "\n\n"
            model_full_paths.append(str(full_path))
        else:
            print(f"[Error] Model file not found: {full_path}")
            
    validation_error = ""
    data = None
    current_atl = None
    last_layer2_data = None
    stopped_by_api_error = False
    
    for attempt in range(MAX_RETRIES + 1):
        attempt_started_at = time.perf_counter()
        attempt_trace = {
            "attempt": attempt + 1,
            "repair_iteration": attempt,
            "attempt_type": "INITIAL_GENERATION" if attempt == 0 else "REPAIR",
            "started_at": current_timestamp(),
            "llm": {
                "status": "NOT_RUN",
                "elapsed_seconds": 0,
                "input_tokens": None,
                "output_tokens": None,
                "total_tokens": None,
            },
            "layers": {
                "layer0_json": {"status": "NOT_RUN"},
                "layer1_schema": {"status": "NOT_RUN"},
                "layer2_semantic": {"status": "NOT_RUN"},
                "layer3_formal": {"status": "NOT_RUN"},
            },
            "outcome": "RUNNING",
        }
        trace["attempts"].append(attempt_trace)

        def finish_attempt(outcome, error=None):
            attempt_trace["outcome"] = outcome
            attempt_trace["finished_at"] = current_timestamp()
            attempt_trace["elapsed_seconds"] = round(
                time.perf_counter() - attempt_started_at, 3
            )
            if error:
                attempt_trace["error"] = str(error)
            persist_trace()

        data = None
        current_atl = None
        if attempt > 0:
            print(f"[{basename}] Starting Auto-Fix iteration ({attempt}/{MAX_RETRIES})...")
            
        full_prompt = build_prompt(prompt_content, model_content, validation_error)
        
        try:
            print(
                f"[{basename}] Sending request to "
                f"{LLM_CLIENT.provider}/{LLM_CLIENT.model_name}..."
            )
            llm_started_at = time.perf_counter()
            try:
                raw_response, usage = LLM_CLIENT.generate_with_usage(
                    full_prompt, instructions=system_prompt
                )
            except Exception:
                attempt_trace["llm"].update({
                    "status": "ERROR",
                    "elapsed_seconds": round(time.perf_counter() - llm_started_at, 3),
                })
                raise
            attempt_trace["llm"].update({
                "status": "SUCCESS",
                "elapsed_seconds": round(time.perf_counter() - llm_started_at, 3),
                "input_tokens": usage.get("input_tokens"),
                "output_tokens": usage.get("output_tokens"),
                "total_tokens": (
                    usage.get("total_tokens")
                    if usage.get("total_tokens") is not None
                    else (
                        (usage.get("input_tokens") or 0)
                        + (usage.get("output_tokens") or 0)
                    )
                ),
            })
            raw_json = extract_json(raw_response)

            # Layer 0: Check basic JSON syntax
            data = json.loads(raw_json)
            attempt_trace["layers"]["layer0_json"]["status"] = "PASS"
            
            # Layer 1: Pydantic Validation
            ast_obj = None
            needs_typed_ast = ablation_config.is_enabled("enable_layer2_semantic")
            if ablation_config.is_enabled("enable_layer1_schema"):
                print(f"[{basename}] Running Pydantic validation (Layer 1)...")
                ast_obj = Module(**data)
                data = ast_obj.model_dump()
                attempt_trace["layers"]["layer1_schema"]["status"] = "PASS"
                print(f"[{basename}] Layer 1: PASS - valid AST.", flush=True)
            elif needs_typed_ast:
                print(
                    f"[{basename}] Layer 1 is disabled; adapting the AST only "
                    "because Layer 2 requires a typed input."
                )
                attempt_trace["layers"]["layer1_schema"]["status"] = "DISABLED"
                try:
                    ast_obj = Module(**data)
                    data = ast_obj.model_dump()
                except ValidationError as error:
                    detail = (
                        "Layer 2 requires a typed ATL AST, but the candidate could "
                        "not be adapted while Layer 1 was disabled. The structural "
                        "diagnostic was not sent to the LLM."
                    )
                    attempt_trace["layers"]["layer2_semantic"].update({
                        "status": "NOT_APPLICABLE",
                        "detail": str(error),
                    })
                    save_last_candidate(basename, data, current_atl)
                    finish_attempt("DOWNSTREAM_INAPPLICABLE", detail)
                    return finish_task(
                        "DOWNSTREAM_INAPPLICABLE",
                        "LAYER2_REQUIRES_TYPED_AST",
                    )
            else:
                print(f"[{basename}] Skipping Pydantic Validation (Layer 1).")
                attempt_trace["layers"]["layer1_schema"]["status"] = "DISABLED"
            
            # Layer 2: Semantic Check
            if ablation_config.is_enabled("enable_layer2_semantic"):
                print(f"[{basename}] Running semantic check (Layer 2)...")
                registry = ATLEcoreRegistry(model_full_paths)
                env = TypeEnvironment(registry=registry)
                ATLSemanticChecker.check_module(ast_obj, env, ablation_config)
                attempt_trace["layers"]["layer2_semantic"]["status"] = "PASS"
                print(f"[{basename}] Layer 2: PASS - valid semantics.", flush=True)
            else:
                print(f"[{basename}] Skipping semantic check (Layer 2).")
                attempt_trace["layers"]["layer2_semantic"]["status"] = "DISABLED"
            
            layer3_status, layer3_feedback, final_atl = run_layer3(
                basename, data, model_full_paths, attempt, ablation_config
            )
            attempt_trace["layers"]["layer3_formal"]["status"] = layer3_status
            if final_atl is not None:
                current_atl = final_atl
            if layer3_status in {"COUNTEREXAMPLE", "GENERATION_ERROR"}:
                if (
                    layer3_status == "GENERATION_ERROR"
                    and not ablation_config.is_enabled("enable_layer1_schema")
                ):
                    save_last_candidate(basename, data, final_atl)
                    finish_attempt("DOWNSTREAM_INAPPLICABLE", layer3_feedback)
                    return finish_task(
                        "DOWNSTREAM_INAPPLICABLE",
                        "AST_TO_ATL_FAILED_WITHOUT_L1",
                    )
                save_last_candidate(basename, data, final_atl)
                validation_error = layer3_feedback
                attempt_trace["repair_trigger"] = layer3_status
                finish_attempt(layer3_status, layer3_feedback)
                print("[Layer 3] Candidate rejected; sending the diagnostic to the LLM for repair.")
                if attempt < MAX_RETRIES:
                    trace["retry_sleep_seconds"] += RETRY_DELAY_SECONDS
                    time.sleep(RETRY_DELAY_SECONDS)
                continue
            if layer3_status not in {"VERIFIED", "SKIPPED"}:
                save_last_candidate(basename, data, final_atl)
                finish_attempt(layer3_status, layer3_feedback)
                print(f"[{basename}] Layer 3 ended with status {layer3_status}; "
                      "the last draft was saved but is not verified.", flush=True)
                return finish_task(layer3_status, "LAYER3_STOPPED")

            if layer3_status == "SKIPPED":
                final_atl = generate_final_atl_from_ast(basename, data)
                if final_atl is None:
                    detail = (
                        "The candidate could not be converted to ATL after formal "
                        "verification was disabled."
                    )
                    save_last_candidate(basename, data, current_atl)
                    finish_attempt("AST2ATL_ERROR", detail)
                    return finish_task("AST2ATL_ERROR", "AST_TO_ATL_FAILED")
                current_atl = final_atl

            output_path = os.path.join(RESPONSES_DIR, f"{basename}.json")
            with open(output_path, 'w', encoding='utf-8') as out_f:
                json.dump(data, out_f, indent=2, ensure_ascii=False)
            finish_attempt(layer3_status)
            print(f"[Success] {basename} passed validation and was saved.")
            termination_reason = (
                "BOUNDED_VERIFICATION_PASSED"
                if layer3_status == "VERIFIED"
                else "LAYER3_SKIPPED"
            )
            return finish_task(layer3_status, termination_reason)
            
        except json.JSONDecodeError as e:
            attempt_trace["layers"]["layer0_json"].update({
                "status": "FAIL",
                "detail": str(e),
            })
            validation_error = f"JSONDecodeError: {str(e)}\n\nNote: Return valid JSON only, without extra text."
            attempt_trace["repair_trigger"] = "JSON_DECODE_ERROR"
            print(f"[JSON syntax error] {str(e)}")
        except ValidationError as e:
            attempt_trace["layers"]["layer1_schema"].update({
                "status": "FAIL",
                "error_count": e.error_count(),
                "detail": str(e),
            })
            save_last_candidate(basename, data, current_atl)
            validation_error = str(e)
            attempt_trace["repair_trigger"] = "LAYER1_VALIDATION_ERROR"
            print(f"[Pydantic Layer 1 error] Found {e.error_count()} structural error(s).")
            print(validation_error)
        except SemanticError as e:
            attempt_trace["layers"]["layer2_semantic"].update({
                "status": "FAIL",
                "detail": str(e),
            })
            save_last_candidate(basename, data, current_atl)
            if data is not None:
                last_layer2_data = data
            validation_error = f"SemanticError: {str(e)}\n\nNote: Repair semantic errors related to the type environment and UML constraints."
            attempt_trace["repair_trigger"] = "LAYER2_SEMANTIC_ERROR"
            print(f"[Semantic Layer 2 error] {str(e)}")
        except Exception as e:
            save_last_candidate(basename, data, current_atl)
            validation_error = f"Unexpected Error: {str(e)}"
            err_str = str(e)
            # Nếu là lỗi do API Key hoặc Rate Limit, in lỗi ngắn gọn và chuyển sang file kế tiếp
            if ("API_KEY" in err_str or "API key" in err_str or "400" in err_str
                    or "429" in err_str or "Quota" in err_str
                    or "CERTIFICATE_VERIFY_FAILED" in err_str
                    or "certificate verify" in err_str.lower()
                    or "SSL_ERROR" in err_str
                    or isinstance(e, TimeoutError)):
                print(f"[API error] {err_str.splitlines()[0] if str(e) else 'API connection error'}")
                attempt_trace["repair_trigger"] = "API_ERROR"
                stopped_by_api_error = True
            else:
                attempt_trace["repair_trigger"] = "SYSTEM_ERROR"
                print(f"[API/system error] {err_str}")

        finish_attempt(attempt_trace.get("repair_trigger", "FAILED"), validation_error)
        if stopped_by_api_error:
            break
            
        # Nghỉ 10 giây tránh Rate Limit
        if attempt < MAX_RETRIES:
            trace["retry_sleep_seconds"] += RETRY_DELAY_SECONDS
            time.sleep(RETRY_DELAY_SECONDS)
            
    if stopped_by_api_error:
        print(f"[Failure] {basename} stopped because the LLM API request failed.")
    else:
        print(f"[Failure] {basename} could not be repaired after {MAX_RETRIES} iteration(s).")
    final_data = data
    final_atl = current_atl
    if final_atl is None and last_layer2_data is not None:
        final_data = last_layer2_data
        final_atl = generate_final_atl_from_ast(basename, final_data)
    if final_data is not None:
        save_last_candidate(basename, final_data, final_atl)
        print("[Pipeline] The last AST/ATL candidate was saved to the normal output locations.")
    if stopped_by_api_error:
        return finish_task("API_ERROR", "API_ERROR")
    return finish_task("REPAIR_LIMIT_EXHAUSTED", "REPAIR_LIMIT_EXHAUSTED")


def is_persisted_task_trace(trace):
    """Return whether a trace represents a testcase result, not an output skip."""
    summary = trace.get("summary", {}) if isinstance(trace, dict) else {}
    return bool(trace.get("task")) and summary.get("final_status") != "SKIPPED_EXISTING"


def load_persisted_task_traces(traces_dir):
    """Load one retained trace per testcase from the incremental trace directory."""
    traces_by_task = {}
    traces_dir = Path(traces_dir)
    if not traces_dir.is_dir():
        return traces_by_task

    for trace_path in sorted(traces_dir.glob("*_trace.json")):
        trace = read_json(trace_path)
        if not isinstance(trace, dict):
            continue
        if is_persisted_task_trace(trace):
            traces_by_task[trace["task"]] = trace
    return traces_by_task


def build_run_summary(run_id, run_started_at, batch_started_at, task_traces, status):
    """Build totals from all retained testcase traces, including earlier batches."""
    tasks = []
    for trace in task_traces:
        task_summary = trace.get("summary", {})
        tasks.append({
            "task": trace.get("task"),
            "status": task_summary.get("final_status"),
            "termination_reason": task_summary.get("termination_reason"),
            "llm_attempts": task_summary.get("llm_attempts", 0),
            "repair_iterations": task_summary.get("repair_iterations", 0),
            "metrics": {
                "task_elapsed_seconds": task_summary.get("task_elapsed_seconds", 0),
                "active_elapsed_seconds": task_summary.get("active_elapsed_seconds", 0),
                "retry_sleep_seconds": task_summary.get("retry_sleep_seconds", 0),
                "llm_elapsed_seconds": task_summary.get("llm_elapsed_seconds", 0),
                "input_tokens": task_summary.get("input_tokens", 0),
                "output_tokens": task_summary.get("output_tokens", 0),
                "total_tokens": task_summary.get("total_tokens", 0),
            },
        })

    executed_tasks = [task for task in tasks if task["llm_attempts"] > 0]
    executed_count = len(executed_tasks)

    def total_metric(metric):
        return sum(task["metrics"].get(metric) or 0 for task in executed_tasks)

    total_task_seconds = total_metric("task_elapsed_seconds")
    total_llm_seconds = total_metric("llm_elapsed_seconds")
    total_llm_attempts = sum(task["llm_attempts"] for task in executed_tasks)
    total_tokens = total_metric("total_tokens")
    summary = {
        "run_id": run_id,
        "status": status,
        "started_at": run_started_at,
        "updated_at": current_timestamp(),
        "provider": LLM_CLIENT.provider,
        "model": LLM_CLIENT.model_name,
        "configuration": {
            "ablation_run_label": ABLATION_RUN_LABEL or "full",
            "ablation_switches": ABLATION_CONFIG.to_dict(),
            "max_repair_iterations": MAX_RETRIES,
            "max_llm_attempts_per_task": MAX_RETRIES + 1,
            "retry_delay_seconds": RETRY_DELAY_SECONDS,
            "efinder_scope": EFINDER_SCOPE,
            "efinder_reference_scope": EFINDER_REFERENCE_SCOPE,
            "efinder_timeout_ms": EFINDER_TIMEOUT_MS,
        },
        "task_count": len(tasks),
        "executed_task_count": executed_count,
        "tasks": tasks,
        "totals": {
            "llm_attempts": total_llm_attempts,
            "input_tokens": total_metric("input_tokens"),
            "output_tokens": total_metric("output_tokens"),
            "total_tokens": total_tokens,
            "task_elapsed_seconds": round(total_task_seconds, 3),
            "active_elapsed_seconds": round(total_metric("active_elapsed_seconds"), 3),
            "retry_sleep_seconds": round(total_metric("retry_sleep_seconds"), 3),
            "llm_elapsed_seconds": round(total_llm_seconds, 3),
            "batch_wall_elapsed_seconds": round(
                time.perf_counter() - batch_started_at, 3
            ),
        },
        "averages": {
            "task_elapsed_seconds": (
                round(total_task_seconds / executed_count, 3)
                if executed_count else None
            ),
            "llm_elapsed_seconds_per_task": (
                round(total_llm_seconds / executed_count, 3)
                if executed_count else None
            ),
            "total_tokens_per_task": (
                round(total_tokens / executed_count, 3)
                if executed_count else None
            ),
            "llm_elapsed_seconds_per_call": (
                round(total_llm_seconds / total_llm_attempts, 3)
                if total_llm_attempts else None
            ),
        },
    }
    if status == "COMPLETED":
        summary["finished_at"] = current_timestamp()
    return summary


def main():
    batch_started_at = time.perf_counter()
    traces_dir = METRICS_DIR / "traces"
    run_summary_path = METRICS_DIR / "run_summary.json"
    existing_summary = read_json(run_summary_path)
    run_started_at = (
        existing_summary.get("started_at")
        if isinstance(existing_summary, dict) and existing_summary.get("started_at")
        else current_timestamp()
    )
    run_id = (
        existing_summary.get("run_id")
        if isinstance(existing_summary, dict) and existing_summary.get("run_id")
        else f"run_{datetime.now().astimezone().strftime('%Y-%m-%d_%H-%M-%S')}"
    )
    # Each trace file is the source of truth. This preserves metrics collected
    # by earlier partial batches and replaces only the testcase run this time.
    task_traces_by_case = load_persisted_task_traces(traces_dir)

    prompt_files = glob.glob(os.path.join(PROMPTS_DIR, "*.txt"))
    if not prompt_files:
        print("No prompt files found in the directory.")
        return
        
    print(f"Found {len(prompt_files)} prompt file(s). Starting batch processing...")
    selected_cases = [
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

    prompt_by_case = {
        os.path.splitext(os.path.basename(p))[0]: p
        for p in prompt_files
    }
    write_json(
        run_summary_path,
        build_run_summary(
            run_id,
            run_started_at,
            batch_started_at,
            list(task_traces_by_case.values()),
            "RUNNING",
        ),
    )
    for case_name in selected_cases:
        prompt_file = prompt_by_case.get(case_name)
        if prompt_file:
            trace_path = traces_dir / f"{case_name}_trace.json"
            task_trace = process_file(prompt_file, trace_path=trace_path)
            task_metrics = task_trace["summary"]
            if is_persisted_task_trace(task_trace):
                task_traces_by_case[case_name] = task_trace
                print(
                    f"[Metrics] {case_name}: "
                    f"task={task_metrics['task_elapsed_seconds']:.3f}s | "
                    f"LLM calls={task_metrics['llm_attempts']} | "
                    f"tokens={task_metrics['total_tokens']}"
                )
            else:
                print(
                    f"[Metrics] {case_name}: existing output was skipped; "
                    "its stored trace and summary entry were left unchanged."
                )
        else:
            print(f"[Warning] Prompt not found for {case_name}")

        running_summary = build_run_summary(
            run_id,
            run_started_at,
            batch_started_at,
            list(task_traces_by_case.values()),
            "RUNNING",
        )
        write_json(run_summary_path, running_summary)

    final_summary = build_run_summary(
        run_id,
        run_started_at,
        batch_started_at,
        list(task_traces_by_case.values()),
        "COMPLETED",
    )
    write_json(run_summary_path, final_summary)
    print(f"\n[Metrics] Run summary: {run_summary_path}")
    print(
        "[Metrics] "
        f"total tokens={final_summary['totals']['total_tokens']} | "
        f"average testcase time="
        f"{final_summary['averages']['task_elapsed_seconds']}s | "
        f"batch wall time={final_summary['totals']['batch_wall_elapsed_seconds']}s"
    )

if __name__ == "__main__":
    main()

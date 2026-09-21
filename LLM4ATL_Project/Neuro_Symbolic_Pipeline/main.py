import os
import glob
import json
import time
import sys
from pathlib import Path
# Keep gRPC's repeated TLS handshake diagnostics from flooding the pipeline
# output; the first actionable exception is still reported below.
os.environ.setdefault("GRPC_VERBOSITY", "ERROR")
from pydantic import ValidationError
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent
PIPELINE_DIR = PROJECT_DIR / "pipeline"
COMMON_DIR = PROJECT_DIR / "common"
CONFIG_DIR = PROJECT_DIR / "config"
STRUCTURAL_CHECKING_DIR = PIPELINE_DIR / "structural_checking"

# Compatibility imports for modules which have not yet been refactored to
# package-qualified imports. New code should import through pipeline/... .
for import_dir in (COMMON_DIR, CONFIG_DIR, STRUCTURAL_CHECKING_DIR):
    import_dir_text = str(import_dir)
    if import_dir_text not in sys.path:
        sys.path.insert(0, import_dir_text)

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
    print(f"[Lỗi cấu hình LLM] {error}")
    sys.exit(1)
ABLATION_CONFIG = AblationConfig.from_env()


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

# The new layout should use output/. The directory currently on disk is named
# ouput/; retain it as a temporary fallback until it is renamed.
OUTPUT_DIR = PROJECT_DIR / 'output'
LEGACY_OUTPUT_DIR = PROJECT_DIR / 'ouput'
if not OUTPUT_DIR.exists() and LEGACY_OUTPUT_DIR.exists():
    OUTPUT_DIR = LEGACY_OUTPUT_DIR

FINAL_RESPONSES_DIR = OUTPUT_DIR / 'final_responses'
AST_OUTPUT_DIR = FINAL_RESPONSES_DIR / 'atl_ast'
ATL_OUTPUT_DIR = FINAL_RESPONSES_DIR / 'atl'
FORMAL_VERIFICATION_OUTPUT_DIR = OUTPUT_DIR / 'formal_verification'
LAYER3_OUTPUT_DIR = FORMAL_VERIFICATION_OUTPUT_DIR / 'pipeline_attempts'
LAYER3_CANDIDATE_DIR = FORMAL_VERIFICATION_OUTPUT_DIR / '.layer3_candidates'

# Existing function names are preserved while the rest of main.py is
# incrementally refactored.
RESPONSES_DIR = AST_OUTPUT_DIR
AST2ATL_DIR = ATL_OUTPUT_DIR

for output_dir in (AST_OUTPUT_DIR, ATL_OUTPUT_DIR, FORMAL_VERIFICATION_OUTPUT_DIR):
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
    candidate_ast_dir = LAYER3_CANDIDATE_DIR / 'ast' / basename
    candidate_atl_dir = LAYER3_CANDIDATE_DIR / 'ast2atl' / basename
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
        print(f"[{basename}] Layer 3 dừng: AST2ATL_ERROR: Không thể tạo ATL từ AST.", flush=True)
        return "GENERATION_ERROR", detail, None

    print(f"[{basename}] Đã tạo ATL thành công.", flush=True)
    print(f"[{basename}] Đang chuyển ATL -> ATL2TM...", flush=True)

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
        print(f"[{basename}] Đã tạo ATL -> ATL2TM thành công.", flush=True)
        print(f"[{basename}] Đang chạy eFinder...", flush=True)

    if result.status == "VERIFIED":
        print(f"[{basename}] Layer 3: PASS - không tìm thấy phản ví dụ.", flush=True)
        final_atl = Path(AST2ATL_DIR) / f'{basename}.atl'
        final_atl.parent.mkdir(parents=True, exist_ok=True)
        final_atl.write_text(atl_code, encoding='utf-8')
        return "VERIFIED", "", final_atl
    if result.status == "COUNTEREXAMPLE":
        print(f"[{basename}] Layer 3: SAT - phát hiện phản ví dụ; gửi cho LLM sửa.", flush=True)
        return "COUNTEREXAMPLE", result.feedback, candidate_atl
    print(f"[{basename}] Layer 3 dừng: {result.detail}", flush=True)
    return result.status, result.detail, candidate_atl

def process_file(prompt_file_path, ablation_config=ABLATION_CONFIG):
    basename = os.path.splitext(os.path.basename(prompt_file_path))[0]
    output_path = os.path.join(RESPONSES_DIR, f"{basename}.json")
    if os.path.exists(output_path):
        print(f"\n--- Bỏ qua: {basename} (File đã tồn tại) ---")
        return

    print(f"\n--- Đang xử lý: {basename} ---")
    
    # Read prompt content
    with open(prompt_file_path, 'r', encoding='utf-8') as f:
        prompt_content = f.read()
        
    # Get models
    model_files = mapping.get(basename)
    if not model_files:
        print(f"[Cảnh báo] Không tìm thấy mapping model cho {basename}")
        return
        
    model_content = ""
    model_full_paths = []
    for rel_path in model_files:
        full_path = resolve_metamodel_path(rel_path)
        if full_path.is_file():
            model_content += full_path.read_text(encoding='utf-8') + "\n\n"
            model_full_paths.append(str(full_path))
        else:
            print(f"[Lỗi] Không tìm thấy file model: {full_path}")
            
    MAX_RETRIES = 5
    validation_error = ""
    data = None
    
    for attempt in range(MAX_RETRIES + 1):
        data = None
        current_atl = None
        if attempt > 0:
            print(f"[{basename}] Bắt đầu lặp Auto-Fix (lần {attempt}/{MAX_RETRIES})...")
            
        full_prompt = build_prompt(prompt_content, model_content, validation_error)
        
        try:
            print(
                f"[{basename}] Đang gửi request tới "
                f"{LLM_CLIENT.provider}/{LLM_CLIENT.model_name}..."
            )
            raw_json = extract_json(
                LLM_CLIENT.generate(full_prompt, instructions=system_prompt)
            )

            # Layer 0: Check basic JSON syntax
            data = json.loads(raw_json)
            
            # Layer 1: Pydantic Validation
            ast_obj = None
            needs_typed_ast = ablation_config.is_enabled("enable_layer2_semantic")
            if ablation_config.is_enabled("enable_layer1_schema"):
                print(f"[{basename}] Đang kiểm tra Pydantic Validation (Layer 1)...")
                ast_obj = Module(**data)
                data = ast_obj.model_dump()
                print(f"[{basename}] Layer 1: PASS - AST hợp lệ.", flush=True)
            elif needs_typed_ast:
                print(f"[{basename}] Layer 1 disabled as a validation gate; building typed AST for downstream checks.")
                ast_obj = Module(**data)
                data = ast_obj.model_dump()
            else:
                print(f"[{basename}] Skipping Pydantic Validation (Layer 1).")
            
            # Layer 2: Semantic Check
            if ablation_config.is_enabled("enable_layer2_semantic"):
                print(f"[{basename}] Đang kiểm tra Ngữ nghĩa (Layer 2)...")
                registry = ATLEcoreRegistry(model_full_paths)
                env = TypeEnvironment(registry=registry)
                ATLSemanticChecker.check_module(ast_obj, env, ablation_config)
                print(f"[{basename}] Layer 2: PASS - ngữ nghĩa hợp lệ.", flush=True)
            else:
                print(f"[{basename}] Skipping semantic check (Layer 2).")
            
            layer3_status, layer3_feedback, final_atl = run_layer3(
                basename, data, model_full_paths, attempt, ablation_config
            )
            if final_atl is not None:
                current_atl = final_atl
            if layer3_status in {"COUNTEREXAMPLE", "GENERATION_ERROR"}:
                save_last_candidate(basename, data, final_atl)
                validation_error = layer3_feedback
                print("[Layer 3] Candidate rejected; sending the diagnostic to the LLM for repair.")
                if attempt < MAX_RETRIES:
                    time.sleep(10)
                continue
            if layer3_status not in {"VERIFIED", "SKIPPED"}:
                save_last_candidate(basename, data, final_atl)
                print(f"[{basename}] Layer 3 kết thúc với trạng thái {layer3_status}; "
                      "bản nháp cuối đã được lưu, chưa được xác nhận.", flush=True)
                return

            output_path = os.path.join(RESPONSES_DIR, f"{basename}.json")
            with open(output_path, 'w', encoding='utf-8') as out_f:
                json.dump(data, out_f, indent=2, ensure_ascii=False)
            print(f"[Thành công] {basename} đã qua kiểm duyệt và được lưu.")
            return
            
        except json.JSONDecodeError as e:
            validation_error = f"JSONDecodeError: {str(e)}\n\nLưu ý: Bạn phải trả về ĐÚNG chuẩn JSON, không chứa text thừa."
            print(f"[Lỗi Cú pháp JSON] {str(e)}")
        except ValidationError as e:
            save_last_candidate(basename, data, current_atl)
            validation_error = str(e)
            print(f"[Lỗi Pydantic Layer 1] Phát hiện {e.error_count()} lỗi cấu trúc.")
            print(validation_error)
        except SemanticError as e:
            save_last_candidate(basename, data, current_atl)
            validation_error = f"SemanticError: {str(e)}\n\nLưu ý: Sửa lỗi ngữ nghĩa liên quan đến Type Environment và UML constraints."
            print(f"[Lỗi Ngữ nghĩa Layer 2] {str(e)}")
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
                print(f"[Lỗi API] {err_str.splitlines()[0] if str(e) else 'Lỗi kết nối API'}")
                break
            print(f"[Lỗi API/Hệ thống] {err_str}")
            
        # Nghỉ 10 giây tránh Rate Limit
        if attempt < MAX_RETRIES:
            time.sleep(10)
            
    print(f"[Thất bại] {basename} không thể sửa lỗi sau {MAX_RETRIES} lần lặp.")
    if data is not None:
        save_last_candidate(basename, data, current_atl)
        print("[Layer 3] The last AST/ATL candidate was saved to the normal output locations.")

def main():
    prompt_files = glob.glob(os.path.join(PROMPTS_DIR, "*.txt"))
    if not prompt_files:
        print("Không tìm thấy file prompt nào trong thư mục!")
        return
        
    print(f"Tìm thấy {len(prompt_files)} file prompt. Bắt đầu xử lý hàng loạt...")
    selected_cases = [
        "IEEE1471_2_MoDAF_All",
        "Make2Ant_All",
        "CPL2SPL_All"
    ]
    prompt_by_case = {
        os.path.splitext(os.path.basename(p))[0]: p
        for p in prompt_files
    }
    for case_name in selected_cases:
        prompt_file = prompt_by_case.get(case_name)
        if prompt_file:
            process_file(prompt_file)
        else:
            print(f"[Warning] Prompt not found for {case_name}")

if __name__ == "__main__":
    main()

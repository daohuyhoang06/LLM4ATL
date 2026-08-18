import os
import glob
import json
import time
import google.generativeai as genai
from pydantic import ValidationError
from dotenv import load_dotenv
from semantic_check.ecore_registry import ATLEcoreRegistry
from semantic_check.type_environment import TypeEnvironment
from semantic_check.atl_semantic_checker import ATLSemanticChecker
from semantic_check.errors import SemanticError

# Load schema
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
schema_dir = os.path.join(current_dir, 'schema')
sys.path.insert(0, schema_dir)
from schema.atl_ast import Module

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY or API_KEY == "your_api_key_here":
    print("Vui lòng cập nhật GEMINI_API_KEY trong file .env")
    sys.exit(1)

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-3.5-flash')

# Paths
BASE_DIR = os.path.abspath(os.path.join(current_dir, '..'))
MODELS_DIR = current_dir
PROMPTS_DIR = os.path.join(MODELS_DIR, 'mtl_snippet', 'ATLAS_transformation_language', 'prompts', 'additional_prompts')
RESPONSES_DIR = os.path.join(MODELS_DIR, 'mtl_snippet', 'ATLAS_transformation_language', 'responses', 'ast')
SYSTEM_PROMPT_PATH = os.path.join(MODELS_DIR, 'system_prompt.txt')
MAPPING_PATH = os.path.join(MODELS_DIR, 'mapping.json')

# Ensure output directory exists
os.makedirs(RESPONSES_DIR, exist_ok=True)

# Load System Prompt
with open(SYSTEM_PROMPT_PATH, 'r', encoding='utf-8') as f:
    system_prompt_template = f.read()

# Load Schema JSON string directly from Pydantic definition
schema_json = json.dumps(Module.model_json_schema(), indent=2)
system_prompt = system_prompt_template.replace('<INSERT_SCHEMA_HERE>', schema_json)

# Load Mapping
with open(MAPPING_PATH, 'r', encoding='utf-8') as f:
    mapping = json.load(f)

def build_prompt(prompt_content, model_content, validation_error=""):
    prompt = f"{system_prompt}\n\n=== ECORE MODELS ===\n{model_content}\n\n=== TRANSFORMATION REQUEST ===\n{prompt_content}"
    if validation_error:
        prompt += f"\n\n=== PREVIOUS ATTEMPT FAILED WITH VALIDATION ERROR ===\nFix the following schema errors:\n{validation_error}"
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

def process_file(prompt_file_path):
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
        full_path = os.path.join(MODELS_DIR, rel_path)
        if os.path.exists(full_path):
            with open(full_path, 'r', encoding='utf-8') as mf:
                model_content += mf.read() + "\n\n"
            model_full_paths.append(full_path)
        else:
            print(f"[Lỗi] Không tìm thấy file model: {full_path}")
            
    MAX_RETRIES = 3
    validation_error = ""
    data = None
    
    for attempt in range(MAX_RETRIES + 1):
        if attempt > 0:
            print(f"[{basename}] Bắt đầu lặp Auto-Fix (lần {attempt}/{MAX_RETRIES})...")
            
        full_prompt = build_prompt(prompt_content, model_content, validation_error)
        
        try:
            print(f"[{basename}] Đang gửi request tới Gemini...")
            # Gửi request lên Gemini API
            response = model.generate_content(full_prompt)
            raw_json = extract_json(response.text)
            
            # Layer 0: Check basic JSON syntax
            data = json.loads(raw_json)
            
            # Layer 1: Pydantic Validation
            print(f"[{basename}] Đang kiểm tra Pydantic Validation (Layer 1)...")
            ast_obj = Module(**data)
            
            # Layer 2: Semantic Check
            print(f"[{basename}] Đang kiểm tra Ngữ nghĩa (Layer 2)...")
            registry = ATLEcoreRegistry(model_full_paths)
            env = TypeEnvironment(registry=registry)
            ATLSemanticChecker.check_module(ast_obj, env)
            
            # Nếu chạy đến đây tức là không bị văng lỗi (Validation Pass)
            output_path = os.path.join(RESPONSES_DIR, f"{basename}.json")
            with open(output_path, 'w', encoding='utf-8') as out_f:
                json.dump(data, out_f, indent=2, ensure_ascii=False)
            print(f"[Thành công] {basename} đã qua kiểm duyệt và được lưu.")
            return # Thoát vòng lặp
            
        except json.JSONDecodeError as e:
            validation_error = f"JSONDecodeError: {str(e)}\n\nLưu ý: Bạn phải trả về ĐÚNG chuẩn JSON, không chứa text thừa."
            print(f"[Lỗi Cú pháp JSON] {str(e)}")
        except ValidationError as e:
            validation_error = str(e)
            print(f"[Lỗi Pydantic Layer 1] Phát hiện {e.error_count()} lỗi cấu trúc.")
        except SemanticError as e:
            validation_error = f"SemanticError: {str(e)}\n\nLưu ý: Sửa lỗi ngữ nghĩa liên quan đến Type Environment và UML constraints."
            print(f"[Lỗi Ngữ nghĩa Layer 2] {str(e)}")
        except Exception as e:
            validation_error = f"Unexpected Error: {str(e)}"
            err_str = str(e)
            # Nếu là lỗi do API Key hoặc Rate Limit, in lỗi ngắn gọn và chuyển sang file kế tiếp
            if "API_KEY" in err_str or "API key" in err_str or "400" in err_str or "429" in err_str or "Quota" in err_str:
                print(f"[Lỗi API] {err_str.splitlines()[0] if str(e) else 'Lỗi kết nối API'}")
                break
            print(f"[Lỗi API/Hệ thống] {err_str}")
            
        # Nghỉ 10 giây tránh Rate Limit
        if attempt < MAX_RETRIES:
            time.sleep(10)
            
    print(f"[Thất bại] {basename} không thể sửa lỗi sau {MAX_RETRIES} lần lặp.")
    if data is not None:
        with open(output_path, 'w', encoding='utf-8') as out_f:
            json.dump(data, out_f, indent=2, ensure_ascii=False)
        print(f"[Đã lưu nháp] Lưu lại bản nháp cuối cùng bị lỗi của {basename}.")

def main():
    prompt_files = glob.glob(os.path.join(PROMPTS_DIR, "*.txt"))
    if not prompt_files:
        print("Không tìm thấy file prompt nào trong thư mục!")
        return
        
    print(f"Tìm thấy {len(prompt_files)} file prompt. Bắt đầu xử lý hàng loạt...")
    selected_cases = [
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

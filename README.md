# Neuro-Symbolic Pipeline for ATL Code Generation

Repository này tập trung vào pipeline neuro-symbolic sinh mã ATL từ đặc tả ngôn ngữ tự nhiên. Các thư mục đang được sử dụng trực tiếp là:

- `LLM4ATL_neuro_symbolic/Neuro-Symbolic Pipeline/`: sinh, kiểm tra AST và chuyển AST sang ATL.
- `LLM4ATL_neuro_symbolic/ATL_Parser/`: kiểm tra cú pháp ATL.
- `LLM4ATL_neuro_symbolic/ATL_Tests/`: chạy ATL trên XMI mẫu và kiểm tra model output bằng JUnit.

Các thư mục còn lại là mã nguồn, thí nghiệm hoặc artifact của bài báo trước đây; chúng được giữ lại để tham khảo và không thuộc luồng chạy chính dưới đây.

## Pipeline chính

```text
Prompt + Ecore metamodel + ATL schema
                 |
                 v
             main.py
       LLM sinh AST JSON
                 |
                 v
      Kiểm tra AST qua 3 lớp
        1. JSON syntax
        2. Schema - Pydantic
        3. Semantic - Ecore/UML
                 |
                PASS
                 |
                 v
            ast2atl.py
          AST JSON -> ATL
                 |
                 v
       ATL_Parser kiểm tra cú pháp
                 |
                 v
       ATL_Tests chạy biến đổi
       và kiểm tra model output
```

AST chỉ được dùng để sinh ATL khi phản hồi LLM hợp lệ về JSON, đúng cấu trúc Pydantic và vượt qua semantic checking dựa trên Ecore.

## Cấu trúc thư mục quan trọng

Từ đây, các đường dẫn trong bảng được tính tương đối từ thư mục `pipeline`:

```text
LLM4ATL_neuro_symbolic/
├── Neuro-Symbolic Pipeline/
│   └── pipeline/                 # Pipeline chính
├── ATL_Parser/                   # Syntax parser cho ATL
└── ATL_Tests/                    # JUnit execution tests
```

| Thành phần                    | Đường dẫn                                                             | Vai trò                                                            |
| ------------------------------- | ------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| Script sinh AST                 | `main.py`                                                               | Đọc prompt, gọi LLM, chạy validation và lưu AST JSON          |
| Prompt hệ thống               | `system_prompt.txt`                                                     | Chỉ dẫn LLM sinh AST JSON theo schema ATL                         |
| Mapping case–metamodel         | `mapping.json`                                                          | Ánh xạ tên case tới các file Ecore cần nạp                   |
| Environment mẫu                | `.env.example`                                                          | Template cấu hình API key và các cờ ablation                   |
| Cấu hình ablation             | `ablation_config.py`                                                    | Bật/tắt các layer kiểm tra qua`.env`                          |
| Schema ATL — Layer 1           | `schema/atl_ast.py`                                                     | Pydantic model cho module, rule, pattern và binding ATL            |
| Schema OCL — Layer 1           | `schema/ocl_ast.py`                                                     | Pydantic model cho biểu thức OCL                                  |
| JSON Schema ATL                 | `schema/atl_schema.json`                                                | JSON Schema tham chiếu cho cấu trúc ATL AST                      |
| Semantic checker ATL — Layer 2 | `semantic_check/atl_semantic_checker.py`                                | Kiểm tra module, rule, pattern, binding và kiểu ATL              |
| Semantic checker OCL — Layer 2 | `semantic_check/ocl_semantic_checker.py`                                | Kiểm tra kiểu và tính hợp lệ ngữ nghĩa của biểu thức OCL |
| Ecore registry — Layer 2       | `semantic_check/ecore_registry.py`                                      | Đọc Ecore và đăng ký package/class/property                   |
| Type environment — Layer 2     | `semantic_check/type_environment.py`                                    | Quản lý scope, biến, helper, rule và kiểu                      |
| Semantic errors — Layer 2      | `semantic_check/errors.py`                                              | Định nghĩa lỗi semantic để LLM auto-fix                       |
| Ecore metamodel                 | `ATL_model/`                                                            | Các metamodel`.ecore` dùng cho Layer 2                          |
| Prompt bài toán               | `mtl_snippet/ATLAS_transformation_language/prompts/additional_prompts/` | Đặc tả các bài toán biến đổi                               |
| AST output                      | `mtl_snippet/ATLAS_transformation_language/responses/ast/`              | AST JSON trung gian                                                 |
| Chuyển AST sang ATL            | `ast2atl.py`                                                            | Sinh`.atl` từ AST JSON                                           |
| ATL output                      | `mtl_snippet/ATLAS_transformation_language/responses/ast2atl/`          | Mã ATL sinh ra                                                     |
| Parser ATL                      | `../../ATL_Parser/`                                                     | Maven module kiểm tra cú pháp ATL                                |
| Test ATL                        | `../../ATL_Tests/`                                                      | Maven/JUnit module chạy ATL và kiểm tra output                   |

## Yêu cầu môi trường

- Python 3.10 trở lên, khuyến nghị Python 3.12.
- Java JDK 17 trở lên.
- Maven 3.8 trở lên.
- Provider, model và API key của LLM được cấu hình trong `.env`.

Kiểm tra nhanh:

```powershell
python --version
java -version
mvn -version
```

## Cài đặt

Từ thư mục gốc repository:

```powershell
cd ".\LLM4ATL_neuro_symbolic\Neuro-Symbolic Pipeline\pipeline"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Mở `.env`, chọn một provider và thay API key tương ứng. Pipeline hỗ trợ `gemini`, `openai` và `claude`; `LLM_MODEL` dùng để chọn model cụ thể.

```dotenv
LLM_PROVIDER=gemini
LLM_MODEL=gemini-3.5-flash
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
ABLATION_ENABLE_LAYER1_SCHEMA=true
ABLATION_ENABLE_LAYER2_SEMANTIC=true
ABLATION_ENABLE_LAYER2_TYPE_CHECK=true
ABLATION_ENABLE_LAYER2_EXISTENCE_CHECK=true
ABLATION_ENABLE_LAYER2_NULL_SAFETY=true
ABLATION_ENABLE_LAYER3_GENERATION=true
EFINDER_SCOPE=8
EFINDER_REFERENCE_SCOPE=8
EFINDER_TIMEOUT_MS=300000
```

Ví dụ chọn OpenAI:

```dotenv
LLM_PROVIDER=openai
LLM_MODEL=gpt-5
OPENAI_API_KEY=your_openai_api_key_here
```

Ví dụ chọn Claude:

```dotenv
LLM_PROVIDER=claude
LLM_MODEL=claude-sonnet-4-6
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

Sau khi đổi provider, chạy lại `python -m pip install -r requirements.txt`, rồi `python main.py`.

Không commit file `.env` chứa API key.

## Chạy pipeline

### 1. Sinh AST JSON

```powershell
python main.py
```

Prompt được đọc từ `mtl_snippet/ATLAS_transformation_language/prompts/additional_prompts/`; AST JSON được ghi vào `responses/ast/`.

### 2. Chuyển AST JSON sang ATL

```powershell
python ast2atl.py
```

Script chuyển toàn bộ `responses/ast/*.json` sang `responses/ast2atl/*.atl`.

## Kiểm tra ATL trực tiếp

### 1. Kiểm tra cú pháp bằng ATL_Parser

Từ thư mục `pipeline`, chạy script Python của module:

```powershell
cd "..\..\ATL_Parser"
python testATLParsedRate.py
```

Script sẽ đọc các file ATL trong `../Neuro-Symbolic Pipeline/pipeline/.../responses/ast2atl/`, gọi ATL parser và tạo các báo cáo CSV trong `ATL_Parser/`. Với file hợp lệ, kết quả parser là:

```text
RESULT:OK:0
```

### 2. Chạy biến đổi bằng ATL_Tests

Chạy script Python của module để tự động lấy kết quả parser, chép từng ATL vào `src/main/atl/`, chạy test tương ứng và tạo báo cáo:

```powershell
cd "..\ATL_Tests"
python run_all_tests.py
```

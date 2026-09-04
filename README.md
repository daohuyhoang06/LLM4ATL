# Neuro-Symbolic Pipeline for ATL Code Generation

Repository này tập trung vào pipeline neuro-symbolic sinh mã ATL từ đặc tả ngôn ngữ tự nhiên. Các thư mục đang được sử dụng trực tiếp là:

- `LLM-based code generation for MTL/LLM-based code generation for MTL/Neuro-Symbolic Pipeline/`: sinh, kiểm tra AST và chuyển AST sang ATL.
- `LLM-based code generation for MTL/LLM-based code generation for MTL/ATL_Parser/`: kiểm tra cú pháp ATL.
- `LLM-based code generation for MTL/LLM-based code generation for MTL/ATL_Tests/`: chạy ATL trên XMI mẫu và kiểm tra model output bằng JUnit.

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
          Chỉ khi PASS
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
LLM-based code generation for MTL/
└── LLM-based code generation for MTL/
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
- API key của LLM cho model được cấu hình trong `main.py`.

Kiểm tra nhanh:

```powershell
python --version
java -version
mvn -version
```

## Cài đặt

Từ thư mục gốc repository:

```powershell
cd ".\LLM-based code generation for MTL\LLM-based code generation for MTL\Neuro-Symbolic Pipeline\pipeline"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Mở `.env`, thay giá trị `your_llm_api_key_here` bằng API key thật. Tên biến `GEMINI_API_KEY` được giữ nguyên vì `main.py` hiện đọc biến này.

```dotenv
GEMINI_API_KEY=your_llm_api_key_here
ABLATION_ENABLE_LAYER1_SCHEMA=true
ABLATION_ENABLE_LAYER2_SEMANTIC=true
ABLATION_ENABLE_LAYER2_TYPE_CHECK=true
ABLATION_ENABLE_LAYER2_EXISTENCE_CHECK=true
ABLATION_ENABLE_LAYER2_NULL_SAFETY=true
ABLATION_ENABLE_LAYER3_GENERATION=true
```

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

Từ thư mục `pipeline`:

```powershell
cd "..\..\ATL_Parser"
mvn -q test
```

Để parse một ATL do pipeline sinh ra, ví dụ `FamiliesToPersons_All.atl`:

```powershell
$atl = (Resolve-Path "..\Neuro-Symbolic Pipeline\pipeline\mtl_snippet\ATLAS_transformation_language\responses\ast2atl\FamiliesToPersons_All.atl").Path
mvn -q exec:java `
  "-Dexec.mainClass=com.example.atlparser.ATLParserMain" `
  "-Dexec.args=$atl"
```

Kết quả cú pháp hợp lệ:

```text
RESULT:OK:0
```

### 2. Chạy biến đổi bằng ATL_Tests

Các test cần ATL cần kiểm tra nằm tại `ATL_Tests/src/main/atl/`. Copy ATL sinh ra vào đây rồi chạy JUnit:

```powershell
cd "..\ATL_Tests"
Copy-Item `
  "..\Neuro-Symbolic Pipeline\pipeline\mtl_snippet\ATLAS_transformation_language\responses\ast2atl\FamiliesToPersons_All.atl" `
  ".\src\main\atl\FamiliesToPersons_All.atl" `
  -Force

mvn -q test "-Dtest=org.example.FamiliesToPersonsAllExecutionTest"
```

Chạy toàn bộ test:

```powershell
mvn -q test
```

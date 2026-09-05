# Tóm tắt bài báo *Employing Classifying Terms for Testing Model Transformations* và hướng áp dụng vào nghiên cứu ATL + LLM

## 1. Mục tiêu chính của bài báo

Bài báo của Gogolla et al. giải quyết một vấn đề trong **model transformation testing**:

> Làm thế nào sinh được một tập nhỏ các input models nhưng vẫn đủ đa dạng và có ý nghĩa để kiểm thử transformation?

Nếu chỉ yêu cầu model finder sinh tất cả model hợp lệ thì sẽ xuất hiện rất nhiều object models gần như giống nhau hoặc đẳng cấu, khiến test suite lớn nhưng không mang thêm nhiều thông tin.

Giải pháp của paper là **Classifying Terms**, dựa trên ý tưởng **Equivalence Partitioning**: chia không gian object models thành các equivalence classes và chọn một representative model cho mỗi class.

---

## 2. Classifying Term là gì?

Một **Classifying Term (CT)** là một biểu thức OCL đóng, được đánh giá trên một object model và trả về một giá trị đặc trưng.

Ví dụ đơn giản:

```ocl
Person.allInstances()->size()
```

Nếu bound cho phép 2–4 `Person`, CT này tạo các class tương ứng:

```text
CT = 2
CT = 3
CT = 4
```

USE Model Validator sẽ chọn một representative cho mỗi equivalence class.

Hai object models có cùng giá trị CT:

```text
ct(M1) = ct(M2)
```

thì được coi là thuộc cùng equivalence class theo tiêu chí đó.

---

## 3. Có thể dùng nhiều Classifying Terms

Paper mở rộng từ một term kiểu Integer sang nhiều term kiểu `Integer` hoặc `Boolean`.

Ví dụ Parenthood:

```ocl
[wGp]
Person.allInstances()->exists(g,p,c |
    g.child->includes(p) and
    p.child->includes(c))

[w2c]
Person.allInstances()->exists(p |
    p.child->size() >= 2)

[w2p]
Person.allInstances()->exists(p |
    p.parent->size() >= 2)
```

Ba Boolean terms về lý thuyết tạo tối đa:

\[
2^3 = 8
\]

equivalence classes.

Tuy nhiên không nhất thiết đủ cả 8 vì một số tổ hợp có thể **không khả thi theo metamodel, OCL constraints hoặc finite bounds**. Trong ví dụ Parenthood của paper chỉ có 5 tổ hợp khả thi.

Vì vậy không nên nói:

> “USE luôn sinh 8 models.”

Mà nên nói:

> **USE sinh một representative model cho mỗi feasible equivalence class.**

---

## 4. USE Model Validator làm gì?

USE Model Validator là **model finder**, không phải transformation engine.

Input của nó gồm đại ý:

```text
UML/class model
+
OCL constraints
+
Classifying Terms
+
finite configuration/bounds
```

Sau đó USE chuyển UML/OCL sang relational logic của Kodkod, tìm nghiệm và chuyển nghiệm trở lại thành object models.

Cơ chế với CT:

```text
Sinh M1
→ lưu vector CT(M1)

Sinh M2
→ bắt CT(M2) khác CT(M1)

Sinh M3
→ bắt CT(M3) khác CT(M1), CT(M2)

...
```

Công thức tổng quát là cấm model mới có cùng toàn bộ vector CT với một model cũ.

Nhờ vậy:

```text
Model space rất lớn
        ↓
Classifying Terms
        ↓
Equivalence classes
        ↓
1 canonical representative / class
```

Paper nói cơ chế Classifying Terms này đã được implement trong USE Model Validator.

---

## 5. Classifying Terms không trực tiếp kiểm tra Transformation T

Điểm này rất quan trọng.

Classifying Terms chủ yếu giải bài toán:

> **Sinh/chọn test inputs như thế nào?**

Nó không phải oracle quyết định:

```text
Transformation đúng hay sai?
```

Paper sau đó đưa Classifying Terms vào **context of Tracts** để thực sự kiểm thử model transformation.

---

## 6. Tracts là gì?

**Tracts** là cơ chế **specification + black-box testing** cho model transformations.

Một transformation có thể được đặc tả bởi nhiều Tracts; mỗi Tract tập trung vào một scenario/use case cụ thể.

Một Tract liên quan đến:

```text
Source metamodel
Target metamodel
Transformation T
Tract test suite
Tract constraints
```

Các constraint đóng vai trò contract/specification của transformation và được biểu diễn bằng OCL.

Paper phân biệt 5 loại constraints:

```text
1. Source general constraints
2. Target general constraints
3. Source Tract constraints
4. Target Tract constraints
5. Source–Target Tract constraints
```

Trong đó **source-target constraints** đặc biệt quan trọng vì chúng mô tả output phải tương ứng với input như thế nào.

Ví dụ:

```text
Proc.title
   ↓ T
Book.title
```

có thể có contract yêu cầu:

```text
Proc.title = Book.title
```

---

## 7. Quan hệ giữa Classifying Terms và Tracts

Đây là ý chính của Section III.

Tracts cần một **test suite gồm source models**.

Trước đó, test suites thường được tạo bằng ASSL, nhưng paper cho rằng cách này khó đảm bảo coverage và có thể khá thủ công/error-prone.

Classifying Terms được dùng để thay thế/giúp bước này:

```text
Classifying Terms
        ↓
USE Model Validator
        ↓
Representative source models
        ↓
Tract Test Suite
```

Paper nói trực tiếp rằng các canonical representative models do USE sinh ra **constitute the test suite of the tract**.

Sau đó:

```text
source model mi
       ↓
Transformation T
       ↓
target model T(mi)
```

và Tract kiểm tra:

```text
mi
→ Source constraints

T(mi)
→ Target constraints

<mi, T(mi)>
→ Source–Target constraints
```

Nếu vi phạm contract → transformation fail trên test case đó.

---

## 8. Ví dụ BibTeX2DocBook trong paper

Paper định nghĩa ba Boolean Classifying Terms trên source:

```text
yearE_EQ_yearP
noManusManumLavat
noSelfEditedPaper
```

Ba terms tạo 8 equivalence classes khả thi trong ví dụ:

```text
000
001
010
011
100
101
110
111
```

USE sinh một source model đại diện cho mỗi class.

Các model đó trở thành **8 test cases của Tract test suite**.

Sau đó transformation:

```text
BibTeX model
      ↓
BibTeX2DocBook
      ↓
DocBook model
```

được chạy trên từng test case.

---

## 9. Further Analysis of Model Transformations

Paper không chỉ classify source models mà còn có thể định nghĩa **Classifying Terms trên target model space**.

Từ đó:

```text
Source class Ci
       ↓ T
Target class Dj
```

Ta có thể phân tích mapping giữa các equivalence classes.

Điều này giúp nghiên cứu các properties như:

```text
coverage
no junk
no confusion
property preservation
```

Ví dụ `onlyNormalBooks` được định nghĩa ở phía target.

Nếu semantics yêu cầu Proceedings phải được chuyển thành edited books thì:

```text
onlyNormalBooks = 1
```

là một loại output không nên xuất hiện.

Nếu transformation sinh ra loại đó thì đó là dấu hiệu **junk output**.

---

## 10. Hạn chế lớn: một representative/class chưa phải proof

Paper không khẳng định:

```text
1 representative PASS
⇒ mọi model trong class đều PASS
```

Điều này chỉ dựa trên giả định equivalence partitioning rằng các model trong cùng class sẽ được transformation xử lý tương tự.

Nếu Classifying Terms chọn chưa đủ tốt:

```text
M1 ∈ C
M2 ∈ C

nhưng

T(M1) → target class D1
T(M2) → target class D2
```

thì class `C` đang quá thô.

Vì thế đây là **systematic testing**, không phải formal proof rằng transformation đúng với mọi possible model.

---

## 11. Section C – nhiều representative trong một class

Paper đề xuất hướng mở rộng:

```text
First-level Classifying Terms
        ↓
main equivalence classes
        ↓
Second-level Classifying Terms
        ↓
nhiều representatives trong cùng class
```

Ví dụ:

```text
Class C
├── model có 1 paper
├── model có 2 papers
└── model có nhiều papers
```

nhờ vậy test suite mạnh hơn.

Tuy nhiên đây chủ yếu là **future-work direction**, chưa phải phần được hoàn thiện đầy đủ trong implementation của paper.

---

## 12. Những gì paper đã implement

Phần cốt lõi:

```text
UML/OCL
+
Classifying Terms
↓
USE Model Validator
↓
representative object models
```

đã được implement.

Paper nói rõ các feature Classifying Terms đã được đưa vào USE Model Validator.

Tuy nhiên:

```text
Automatic generation of CTs
Automatic generation of Tract contracts
LLM integration
LLM repair loop
ATL-specific pipeline
```

**không phải contribution của paper**.

Đây là những thứ nghiên cứu của bạn có thể phát triển thêm.

---

## 13. Hướng áp dụng vào nghiên cứu của bạn

Pipeline hiện tại:

```text
Requirement
+
Source Ecore
+
Target Ecore
        ↓
       LLM
        ↓
     ATL AST
        ↓
Layer 1
Structural Validation
        ↓
Layer 2
Static Semantic Validation
        ↓
Candidate ATL
```

Layer 3 sẽ phát triển từ Gogolla theo hướng:

# Layer 3 — Classifying-Term-Guided Tract-Based Execution Validation

```text
                    Candidate ATL T
                           │
                           ▼
                     ATL Compiler
                   FAIL ────────→ LLM repair
                           │ PASS
                           ▼

Source Ecore
    │
    ▼
Ecore → USE
    │
    ├──────────────┐
    │              │
    ▼              ▼
Classifying     Source/domain
Terms           OCL constraints
    │              │
    └──────┬───────┘
           ▼
     USE Model Validator
           │
           ▼
Representative Source Models
      m1, ..., mn
           │
           ▼
      TRACT TEST SUITE
           │
           ▼
       ATL Engine / VM
           │
   mi ──T──→ T(mi)
           │
           ▼
      Tract Validation
      ├─ source constraints
      ├─ target constraints
      └─ source-target constraints
           │
      PASS / FAIL
           │
         FAIL
           ▼
 Structured Feedback
           │
           ▼
          LLM
           │
        Repair T
           │
           └────→ repeat
```

---

## 14. Vai trò của ATL compiler

Paper không ATL-specific nên không tách compilation thành bước riêng.

Nhưng nghiên cứu ATL-specific nên có:

```text
ATL code
↓
ATL compiler
↓
ASM / executable transformation
```

Nếu compile fail:

```text
không cần USE
không cần test suite
không cần execution
```

mà trả lỗi trực tiếp về LLM.

Điều này đặc biệt quan trọng vì benchmark có thể có transformation:

```text
parse PASS
static validation có thể PASS
ATL compile FAIL
```

Vì vậy compilation nên là **gate đầu tiên của Layer 3**, nhưng không cần trở thành một Layer riêng.

---

## 15. Hai bài toán tự động hóa quan trọng nhất

### A. Automatic Classifying-Term Generation

Paper:

```text
Developer
↓
writes Classifying Terms manually
```

Nghiên cứu của bạn muốn:

```text
Source Ecore
+
ATL AST
        ↓
Automatic CT Generator
        ↓
Classifying Terms
```

Một hướng hợp lý là **transformation-aware Classifying Terms**.

Ví dụ ATL sử dụng:

```atl
s.children->collect(...)
```

thì generator tự tạo scenario:

```text
children empty
children contains one element
children contains multiple elements
```

bằng OCL CTs.

Các pattern có thể derive từ:

```text
EClass matched
EReference navigation
multiplicity
collection operation
guard condition
inheritance
optional reference
attribute comparison
```

Đây có thể trở thành một contribution riêng của nghiên cứu.

---

## 16. Automatic Tract Constraint Generation

Đây là bài toán khó hơn.

Metamodel chỉ cho biết structure:

```text
Source:
Proc.title : String

Target:
Book.title : String
```

Nó không cho biết requirement:

```text
Proc.title = Book.title
```

Do đó không thể đáng tin cậy suy ra Tract contracts chỉ từ hai Ecore.

Cần thêm nguồn specification như:

```text
Natural-language requirement
reference transformation
expected source-target examples
human-defined contract
```

Hướng của nghiên cứu có thể là:

```text
Natural-language transformation specification
+
Source Ecore
+
Target Ecore
        ↓
LLM
        ↓
Candidate Tract/OCL constraints
        ↓
OCL validation
        ↓
validated contracts
```

Nhưng các contracts do LLM sinh **không nên được tin ngay**.

---

## 17. Vấn đề “LLM sinh cả ATL lẫn oracle”

Đây là rủi ro phương pháp luận quan trọng.

Nếu cùng một LLM hiểu requirement sai theo cách X:

```text
LLM
├── sinh ATL sai theo X
└── sinh OCL contract cũng mô tả X
```

thì:

```text
ATL sai
nhưng
Tract test = PASS
```

Vì vậy nếu tự động sinh Tract constraints, nên có verification độc lập cho OCL:

```text
Candidate OCL
    ↓
Syntax validation
    ↓
Static typing against Ecore
    ↓
Satisfiability / model finding
    ↓
Consistency checks
```

Và trong benchmark, nếu có reference transformation hoặc known expected mappings thì nên tận dụng chúng để đánh giá chất lượng oracle.

---

## 18. Vai trò của USE trong pipeline

Có thể ghi nhớ rất ngắn:

```text
USE ≠ ATL executor
USE ≠ Tract oracle
USE ≠ LLM

USE Model Validator
=
systematic source test-model generator
```

Vai trò cụ thể:

```text
Source metamodel
+
constraints
+
Classifying Terms
+
finite bounds
        ↓
USE
        ↓
representative source models
```

Sau đó ATL engine mới chạy transformation.

---

## 19. Vai trò của từng thành phần

| Component | Vai trò |
|---|---|
| LLM | Sinh/sửa ATL |
| Layer 1 | Kiểm tra structural conformance |
| Layer 2 | Kiểm tra static semantics |
| ATL compiler | Kiểm tra transformation có executable không |
| Classifying Terms | Chia input space |
| USE Model Validator | Sinh representative test models |
| Tract test suite | Tập input models dùng để test T |
| ATL Engine | Thực thi transformation |
| Tract constraints | Oracle/contract |
| Feedback generator | Biến lỗi thành thông tin cho LLM |
| LLM repair | Sửa candidate transformation |

---

## 20. Contribution tiềm năng của nghiên cứu

Nếu đi theo hướng này, contribution không đơn giản là “dùng Classifying Terms”.

Paper Gogolla đã có:

```text
Classifying Terms
+
USE
+
Tracts
```

Contribution mới có thể là:

> **A neuro-symbolic pipeline that automatically generates ATL transformations, systematically derives execution test models using Classifying Terms, validates the transformations through Tract-based execution, and feeds detected violations back to the LLM for iterative repair.**

Các điểm mới tiềm năng:

```text
1. LLM → structured ATL AST generation

2. Layered validation:
   structural → static semantic → execution

3. Automatic / transformation-aware
   Classifying Term generation

4. Ecore → USE automation

5. Integration of generated representative models
   with ATL execution

6. Automatic or semi-automatic
   Tract contract generation

7. Structured execution/contract feedback
   → LLM repair loop
```

---

## 21. Cách gọi Layer 3

Nếu sử dụng hướng Gogolla, không nên gọi:

> Formal Execution Verification

vì đây chủ yếu là testing bằng representative models, không chứng minh universal correctness.

Tên phù hợp hơn:

> **Layer 3 — Classifying-Term-Guided Execution Validation**

Nếu có Tracts đầy đủ:

> **Layer 3 — Classifying-Term-Guided Tract-Based Validation**

Hoặc wording paper-friendly hơn:

> **Systematic Execution-Level Validation using Classifying Terms and Tracts**

---

## 22. Pipeline cuối cùng nên hướng tới

```text
      Natural-Language Requirement
              +
      Source / Target Ecore
              │
              ▼
             LLM
              │
              ▼
           ATL AST
              │
       ┌──────▼──────┐
       │   Layer 1   │
       │ Structural  │
       └──────┬──────┘
              │
       ┌──────▼──────┐
       │   Layer 2   │
       │ Static Sem. │
       └──────┬──────┘
              │
              ▼
        ATL Code Generator
              │
              ▼
         ATL Compiler
              │
              ▼

 Source Ecore + ATL AST
              │
              ▼
Transformation-aware
Classifying Term Generation
              │
              ▼
         Ecore → USE
              │
              ▼
      USE Model Validator
              │
              ▼
Representative Source Models
              │
              ▼
       Tract Test Suite
              │
              ▼
       ATL Engine / VM
              │
        mi → T(mi)
              │
              ▼
        Tract Contracts
              │
          PASS / FAIL
              │
             FAIL
              ▼
      Structured Feedback
              │
              ▼
             LLM
              │
           Repair ATL
              │
              └────── loop
```

---

## 23. Chốt lại hướng nghiên cứu

Bài Gogolla cung cấp **nền tảng của Layer 3**:

> Dùng Classifying Terms để chia input space → USE sinh representative test models → đưa chúng thành Tract test suite → chạy transformation T → dùng Tract contracts đánh giá hành vi.

Phần nghiên cứu cần phát triển thêm là:

> **Tự động hóa quá trình này cho ATL do LLM sinh**, đặc biệt là **automatic Classifying-Term generation**, **Ecore↔USE integration**, **ATL execution orchestration**, **Tract/OCL contract acquisition/generation**, và **feedback-guided LLM repair**.

Đây là hướng phát triển tự nhiên từ paper gốc và vẫn có phần đóng góp mới rõ ràng.

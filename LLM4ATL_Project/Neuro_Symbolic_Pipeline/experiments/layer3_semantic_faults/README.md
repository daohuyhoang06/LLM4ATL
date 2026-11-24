# Layer 3 semantic-fault experiment (E1–E3)

Thử nghiệm này chứng minh Layer 3 có thể phát hiện ATL vẫn đúng cú pháp, tham
chiếu đúng kiểu/feature của metamodel, nhưng sai transformation requirements.
Case dùng để thử là `Document2Report_All`.

| Lỗi | Mutant | Requirement obligation | Kỳ vọng |
|---|---|---|---|
| E1 | `title <- d.author` (String → String) | `E1NamePreservation` | SAT/counterexample |
| E2 | bỏ rule tạo target `Section` | `E2MappingCompleteness` | SAT/counterexample |
| E3 | một rule tạo hai `Report` cho mỗi `Document` | `E3MappingCardinality` | SAT/counterexample |

Baseline phải trả về UNSAT cho cả ba obligation. `SAT` có nghĩa eFinder tìm
được mô hình thỏa `Sem AND Pre AND NOT Post_i`, tức là đã phát hiện lỗi semantic.

Ba obligation đã được tích hợp vào profile mặc định tại
`input/constraints/Document2Report_All/target-post.ocl`. Folder `constraints/`
trong experiment là một profile độc lập để tham khảo hoặc tái sử dụng.
ATL2TM cũng sinh invariant `distinct_<rule>_outputs` cho rule có nhiều output,
để solver không thể đồng nhất hai phần tử đích cùng kiểu và bỏ sót E3.

Chạy lại từ `Neuro_Symbolic_Pipeline`:

```powershell
python experiments/layer3_semantic_faults/run_experiment.py
```

Script chạy ATL parser, ATL2TM và eFinder; kết quả chi tiết được ghi vào
`results/` (đã ignore khỏi Git). Kết quả quan sát của lần thử nghiệm hiện tại
nằm trong `observed-results.json`.

## Edge cases T1 và T4

Hai regression case trong `edge_cases/` ghi nhận giới hạn của các obligation
hiện tại:

- T1 (`Missing all outputs`): E1–E3 đều trả `UNSAT` do cả ba invariant có
  `context Report`; khi không có `Report`, chúng đúng vacuous.
- T4 (`Balanced duplication`): một `Document` tạo hai `Report`, một `Document`
  không tạo gì. E3 chỉ so sánh tổng số lượng nên vẫn thấy `2 = 2` và bỏ sót.

Chạy lại hai case này:

```powershell
python experiments/layer3_semantic_faults/run_edge_cases.py
```

Kết quả đã quan sát nằm trong `edge-case-observed-results.json`. `UNSAT` trong
hai edge case này là false negative của postcondition, không phải bằng chứng
transformation đáp ứng mapping requirements.

Giới hạn: đây là bounded verification (`scope=3`, `reference-scope=6`), vì vậy
UNSAT có nghĩa không tìm thấy counterexample trong bound đã chọn, không phải
một chứng minh vô hạn cho mọi input model.

# Một khung làm việc cho việc xác minh chuyển đổi mô hình — A framework for model transformation verification

**Tác giả:** Kevin Lano, T. Clark, S. Kolahdouz-Rahimi
**Năm:** 2015
**Tạp chí:** Formal Aspects of Computing, 27(1), 193-235
**Nguồn:** NotebookLM notebook "model tranformation verification"
**Loại tài liệu:** Bản dịch sát nghĩa (đầy đủ, không tóm tắt) — do AI dịch, kèm chú thích giải nghĩa cho đoạn khó.

---

## A framework for verification of model transformations

**K. Lano, T. Clark, S. Kolahdouz-Rahimi**

Dept. of Informatics, King's College London; Dept. of Informatics, Middlesex University

### Tóm tắt (Abstract)

Một nhiệm vụ xác minh chuyển đổi mô hình (model transformation verification) có thể liên quan đến một số chuyển đổi khác nhau, đến từ một hoặc nhiều trong số rất nhiều ngôn ngữ chuyển đổi mô hình khác nhau, mỗi chuyển đổi có thể có một phong cách chuyển đổi cụ thể, và có một số thuộc tính xác minh khác nhau có thể được xác minh cho mỗi ngôn ngữ và phong cách chuyển đổi. Các chuyển đổi có thể tác động lên nhiều ngôn ngữ mô hình hóa khác nhau. Sự đa dạng này của các ngôn ngữ và thuộc tính cho thấy nhu cầu về một khung làm việc đủ tổng quát cho việc xác minh chuyển đổi mô hình, độc lập với các ngôn ngữ chuyển đổi mô hình cụ thể, và có khả năng hỗ trợ các quy trình hệ thống để xác minh trên nhiều ngôn ngữ, và trên nhiều thuộc tính. Trong bài báo này chúng tôi mô tả các thành phần của một khung làm việc như vậy, và áp dụng khung làm việc này vào một loạt các bài toán xác minh chuyển đổi. Những đóng góp cụ thể của chúng tôi là (i) các kỹ thuật xác minh độc lập với ngôn ngữ dựa trên các khái niệm về *bất biến chuyển đổi* (transformation invariants) và *biến thể* (variants); (ii) các siêu mô hình biểu diễn (representation metamodels) độc lập với ngôn ngữ cho các đặc tả và triển khai chuyển đổi, (iii) các ánh xạ từ những biểu diễn này sang các hình thức luận B và Z3, (iv) việc sử dụng các mẫu chuyển đổi (transformation patterns) để hỗ trợ việc xác minh. Bài báo này có tính mới ở chỗ bao quát một phạm vi rộng các kỹ thuật xác minh khác nhau cho một phạm vi rộng các ngôn ngữ MT (Model Transformation), trong một khung làm việc tích hợp.

> **Giải thích:** Bài báo này giải quyết vấn đề: khi ta viết một "chuyển đổi mô hình" (ví dụ: chuyển một sơ đồ UML thành mã Java, hoặc biến đổi một mô hình này thành mô hình khác), làm sao để *chứng minh* chuyển đổi đó làm đúng như mong muốn (ví dụ: không làm mất thông tin, giữ đúng các ràng buộc, kết quả đúng theo đặc tả)? Có rất nhiều ngôn ngữ để viết chuyển đổi (UML-RSDS, ETL, QVT, GrGen.NET, ATL...) và mỗi ngôn ngữ lại có cách xác minh riêng, gây khó tái sử dụng. Bài báo đề xuất một khung làm việc chung, không phụ thuộc vào một ngôn ngữ chuyển đổi cụ thể nào, để có thể áp dụng các kỹ thuật xác minh (dùng các công cụ chứng minh định lý như B-method, Z3 SMT solver) cho nhiều loại chuyển đổi khác nhau.

**Từ khóa (Keywords):** Model transformation verification; model transformation specification; model transformation engineering.

## 1 Giới thiệu (Introduction)

Việc xác minh chuyển đổi mô hình (Model transformation - MT) là một lĩnh vực tương đối mới, trong đó phần lớn công việc cho đến nay đều đặc thù cho các ngôn ngữ chuyển đổi mô hình cụ thể, hoặc cho các thuộc tính xác minh cụ thể. Những cách tiếp cận như vậy dẫn đến các vấn đề trong các kịch bản mà ở đó các hệ thống bao gồm nhiều chuyển đổi, có thể được định nghĩa bằng các ngôn ngữ khác nhau, cần phải được xác minh. Thêm vào đó, việc tái sử dụng các kỹ thuật xác minh cho các ngôn ngữ chuyển đổi khác nhau bị cản trở bởi bản chất đặc thù theo ngôn ngữ của các kỹ thuật này.

Việc phát triển các chuyển đổi mô hình cho đến nay thường thiếu tính hệ thống, và tập trung vào mức triển khai (implementation level), bỏ qua các đặc tả (specifications). Các phong cách phổ biến trong việc định nghĩa chuyển đổi, sử dụng đệ quy (recursion) và các lời gọi thao tác ngầm định (implicit operation calls), cũng gây cản trở cho việc xác minh.

Trong bài báo này chúng tôi định nghĩa một khung làm việc tổng quát, độc lập với ngôn ngữ, cho việc xác minh chuyển đổi, và một loạt các kỹ thuật xác minh độc lập với ngôn ngữ. Khung làm việc này có thể được áp dụng cho các ngôn ngữ chuyển đổi khác nhau, và có thể sử dụng các công nghệ xác minh khác nhau phù hợp để thiết lập các thuộc tính cụ thể. Khung làm việc cung cấp một tổ chức có hệ thống cho quá trình xác minh chuyển đổi, và định nghĩa một cơ sở ngữ nghĩa thống nhất cho việc xác minh.

Các thành phần của khung làm việc là:

- Các siêu mô hình (Metamodels) để biểu diễn các ngôn ngữ mô hình hóa, các đặc tả chuyển đổi và các triển khai chuyển đổi (Mục 2).
- Các thuộc tính xác minh chuyển đổi được hình thức hóa theo khung làm việc này (Mục 3).
- Các kỹ thuật xác minh độc lập với ngôn ngữ được tích hợp vào khung làm việc (các Mục 4, 5, 7, 8).

Trong các mục 9, 10 và 11 chúng tôi minh họa các khái niệm bằng cách sử dụng các trích đoạn từ ba nghiên cứu tình huống (case studies) xác minh, gồm: (i) một chuyển đổi tinh chỉnh (refinement transformation) (sinh mã Java từ UML) sử dụng UML-RSDS [49]; (ii) một chuyển đổi tái biểu đạt (re-expression transformation) sử dụng ETL [28]; (iii) một chuyển đổi tái cấu trúc (refactoring transformation) (loại bỏ các thuộc tính trùng lặp — attribute clones — khỏi một sơ đồ lớp) sử dụng GrGen.NET [26]. Mục 12 đưa ra một đánh giá và mục 13 so sánh với các công trình liên quan.

## 2 Các siêu mô hình cho chuyển đổi mô hình (Metamodels for model transformations)

Trong mục này chúng tôi định nghĩa các siêu mô hình cho các ngôn ngữ mô hình hóa, các đặc tả và triển khai chuyển đổi, và chỉ ra cách các ngôn ngữ, đặc tả và triển khai cho các chuyển đổi có thể được cho một cách diễn giải toán học hình thức, nhằm hỗ trợ việc xác minh chuyển đổi.

### 2.1 Biểu diễn các ngôn ngữ (Representation of languages)

Các chuyển đổi thao tác trên các mô hình hoặc văn bản tuân theo (conform to) một siêu mô hình hoặc định nghĩa cú pháp nào đó. Có thể có nhiều mô hình đầu vào (nguồn — source) được một chuyển đổi sử dụng, và có thể có nhiều mô hình đầu ra (đích — target). Một chuyển đổi được gọi là *cập nhật tại chỗ* (update-in-place) nếu một mô hình vừa là đầu vào vừa là đầu ra, ngược lại nó là một chuyển đổi *mô hình tách biệt* (separate-models).

Các khái niệm then chốt để mô tả hiệu ứng của các chuyển đổi ở mức cao do đó là *ngôn ngữ* (languages) và các thể hiện (instances) của ngôn ngữ (tức là các mô hình của các ngôn ngữ). Ngôn ngữ có thể được đặc tả theo nhiều cách khác nhau, ví dụ, bằng sơ đồ lớp UML, bằng các định nghĩa cú pháp BNF, v.v. Ở đây chúng tôi sẽ giả định rằng sơ đồ lớp UML được sử dụng, cùng với các ràng buộc OCL. Những thứ này tạo thành *cú pháp cụ thể* (concrete syntax) của các mô tả ngôn ngữ. Ví dụ, Hình 1 cho thấy một ngôn ngữ đơn giản với hai kiểu thực thể (entity types) `A` và `B`, các đặc trưng thuộc tính (attribute features) giá trị nguyên của mỗi kiểu, và một liên kết hai chiều (bidirectional association) giữa chúng. Có một ràng buộc tường minh rằng `a.x > 0` cho mỗi `a : A`, và một ràng buộc ngầm định rằng các vai trò liên kết (association roles) `ar` và `br` là nghịch đảo lẫn nhau (mutually inverse):

```
A→forAll(a | a.x > 0)
```
và
```
A→forAll(a | B→forAll(b | a.br→includes(b) equiv b.ar→includes(a)))
```

Để thuận tiện, trong phần tiếp theo chúng tôi sẽ sử dụng ký hiệu `x : s` để viết tắt cho biểu thức OCL `s→includes(x)`.

*Hình 1. Ví dụ về ngôn ngữ*

Bên cạnh những mô tả như vậy, chúng ta cũng cần một *cú pháp trừu tượng* (abstract syntax) cho các ngôn ngữ, tức là một siêu mô hình cho các ngôn ngữ, và một tương đương toán học của các ngôn ngữ, nhằm định nghĩa các khái niệm về chứng minh (proof) và thỏa mãn (satisfaction) tương đối theo một ngôn ngữ.

Hình 2 cho thấy một siêu mô hình tổng quát (gọi là `M4`) có thể phục vụ trực tiếp hoặc gián tiếp như một siêu mô hình cho một phạm vi rộng các ngôn ngữ mô hình hóa. Siêu mô hình này cũng tự biểu diễn chính nó (self-representative). Các ràng buộc trên `M4` là: (i) `general` là không chu trình (non-cyclic), (ii) `mult1upper = −1` hoặc `mult1lower ≤ mult1upper` và tương tự cho `mult2`, (iii) `type : PrimitiveDataType` kéo theo `mult2upper = 1` và `mult2lower = 1` (không có thuộc tính đa trị), (iv) tên của các kiểu thực thể là duy nhất, (v) tên của các đặc trưng dữ liệu (data features) thuộc cùng một kiểu thực thể là duy nhất. Có thể đặc tả thêm các ràng buộc khác trên các ngôn ngữ mô hình hóa, ví dụ, không cho phép đa kế thừa (no multiple inheritance). Các đầu (ends) `composite` được diễn giải là thực thi việc lan truyền xóa (deletion propagation) từ các đối tượng của thành phần hợp thành (composite) tới các đối tượng được chứa bên trong. Một đầu liên kết (association end) là *bắt buộc* (mandatory) nếu nó có cận dưới (lower bound) ≥ 1.

> **Giải thích:** M4 ở đây là một "siêu-siêu mô hình" (meta-metamodel) rất tối giản, đóng vai trò như một bộ khung chung để mô tả bất kỳ ngôn ngữ mô hình hóa nào (giống như MOF trong UML) — nó định nghĩa các khái niệm cơ bản: kiểu thực thể (entity type, giống class), đặc trưng dữ liệu (data feature, giống thuộc tính/attribute hoặc quan hệ/association), kiểu dữ liệu nguyên thủy, quan hệ kế thừa (general/supertype), và các ràng buộc số lượng (multiplicity, ví dụ 0..1, 1..*). Nhờ có M4, mọi ngôn ngữ mô hình hóa cụ thể (UML, ER, v.v.) đều có thể được biểu diễn dưới dạng một thể hiện (instance) của M4, và từ đó gán cho nó một ngữ nghĩa toán học chặt chẽ để phục vụ việc chứng minh.

*Fig. 2. Siêu mô hình tối giản (M4) cho các ngôn ngữ mô hình hóa*

Ngôn ngữ ví dụ của chúng ta có thể được biểu diễn dưới dạng các phần tử `A : EntityType`, `B : EntityType`, `x : DataFeature`, `y : DataFeature`, `ar : DataFeature`, `br : DataFeature`, `Integer : PrimitiveDataType`, `A.ownedFeatures = {x, br}`, `B.ownedFeatures = {y, ar}`, `x.type = Integer`, `y.type = Integer`, `ar.type = A`, `br.type = B` của một thể hiện của `M4`, cùng với các thể hiện `c1, c2` của một siêu kiểu ràng buộc (constraint metatype) để biểu diễn các ràng buộc.

Siêu mô hình cho các ngôn ngữ, dựa trên `M4`, được thể hiện trong Hình 3.

*Fig. 3. Siêu mô hình ngôn ngữ (Language metamodel)*

Có thể sử dụng nhiều biến thể khác nhau của ngôn ngữ ràng buộc, Hình 4 cho thấy một siêu mô hình khả dĩ cho các biểu thức ràng buộc, được sử dụng trong UML-RSDS [49]. `BinaryExpression`, `BasicExpression`, `UnaryExpression` và `CollectionExpression` đều kế thừa từ `Expression`.

Để hỗ trợ việc xác minh, chúng ta cần có khả năng định nghĩa một lý thuyết chứng minh (proof theory) và lý thuyết mô hình (model theory, theo nghĩa logic) tương ứng với các ngôn ngữ đã cho, do đó chúng ta cần gán một ngôn ngữ và logic bậc nhất (first order) hình thức cho mỗi thể hiện của `M4`. Bảng 1 định nghĩa cách một ngôn ngữ lý thuyết tập hợp bậc nhất hình thức (FOL) `LL` có thể được gán cho các thể hiện `L` của `M4`. Bảng định nghĩa cách các dạng phần tử khác nhau trong siêu mô hình `M4` tương ứng với các phần tử mô hình hóa khái niệm, và cách chúng được hình thức hóa trong lý thuyết tập hợp bậc nhất.

> **Giải thích:** Đây là bước "gán ngữ nghĩa toán học" cho các khái niệm mô hình hóa. Ví dụ một "kiểu thực thể E" (giống class trong UML) được biểu diễn bằng một ký hiệu kiểu (type symbol) `E`, chính là tập hợp mọi thể hiện (đối tượng) của `E`. Một "thuộc tính đơn trị" (single-valued attribute) `att` được biểu diễn như một hàm toán học `att : E → Typ`, ánh xạ mỗi đối tượng thuộc `E` sang một giá trị kiểu `Typ`. Việc này cho phép áp dụng logic bậc nhất (first-order logic) và các công cụ chứng minh định lý (theorem provers) để suy luận chính xác về mô hình.

**Bảng 1. Sự tương ứng giữa M4 và các logic bậc nhất**

| Khái niệm mô hình hóa | Biểu diễn trong M4 | Ngữ nghĩa hình thức |
|---|---|---|
| Kiểu thực thể `E` | Phần tử của `EntityType` | Ký hiệu kiểu `E`, tập hợp các thể hiện của `E` |
| Thực thể cụ thể (concrete entity) | Phần tử của `EntityType` với `isAbstract = false` | kiểu `E` |
| Thực thể trừu tượng (abstract entity) | Phần tử của `EntityType` với `isAbstract = true` | `E = E1 ∪ ... ∪ El` trong đó `E1, ..., El` là tất cả các kiểu con trực tiếp của `E` |
| Kiểu nguyên thủy `T` | Phần tử của `PrimitiveDataType` | Kiểu toán học tương ứng, `Z, B, R, S`, v.v. |
| Thuộc tính đơn trị `att` của `E` với `mult2upper = 1, mult2lower = 1` và `type ∈ PrimitiveDataType` | Phần tử `DataFeature` | Ký hiệu hàm `att : E → Typ′` trong đó `Typ′` biểu diễn `Typ` |
| Vai trò đơn trị (single-valued role) `r` của `E` với đầu đích (target) là kiểu thực thể `E1`, `mult2upper = 1, mult2lower = 1` và `type ∈ EntityType` | Phần tử `DataFeature` | Ký hiệu hàm `r : E → E1` |
| Vai trò đa trị không thứ tự (unordered many-valued role) `r` của `E` với `mult2upper ≠ 1` hoặc `mult2lower ≠ 1` và `isOrdered = false` và kiểu thực thể đích `E1`, `type ∈ EntityType` | Phần tử `DataFeature` | Ký hiệu hàm `r : E → F(E1)` |
| Vai trò đa trị có thứ tự (ordered many-valued role) `r` của `E` với `mult2upper ≠ 1` hoặc `mult2lower ≠ 1` và `isOrdered = true` và kiểu thực thể đích `E1`, `type ∈ EntityType` | Phần tử `DataFeature` | Ký hiệu hàm `r : E → seq(E1)` |
| Siêu kiểu (supertype) `E1` của `E` | Phần tử của `E.general` | `E ⊆ E1` |

Nếu `mult1upper = 1` và `mult1lower = 1` hoặc `mult1lower = 0` (tức là số lượng `0..1` tại đầu nguồn của đặc trưng) đối với một thuộc tính, thì đó là một thuộc tính định danh (duy nhất) (identity/unique attribute), tức là một khóa chính (primary key) theo thuật ngữ dữ liệu quan hệ. Giá trị số lượng `−1` biểu diễn số lượng `∗`. Một biểu thức hoặc là đơn trị (single-valued) (biểu thị một giá trị đơn của kiểu dữ liệu nguyên thủy, hoặc một thể hiện đơn của kiểu thực thể), hoặc là đa trị (many-valued), biểu thị một tập hợp (collection). Các tập hợp theo siêu mô hình này hoặc có thứ tự (giá trị dạng dãy — sequence-valued) hoặc không có thứ tự (giá trị dạng tập hợp — set-valued). Bao (bags) và tập hợp có thứ tự (ordered sets) có thể được định nghĩa theo thuật ngữ của các dãy (sequences). Lưu ý rằng một đầu liên kết tùy chọn (optional association end) (với `mult2lower = 0` và `mult2upper = 1`) được biểu diễn hình thức như một tập hợp (hoặc dãy) có kích thước 0 hoặc 1. Do đó, các phần tử null trong trường hợp này được biểu diễn như các tập hợp rỗng, giống như trong chuẩn OCL [44]. Một kiểu đếm được (denumerable type) `Object OBJ` được đưa vào mỗi `LL` để biểu diễn tập hợp tất cả các tham chiếu đối tượng khả dĩ¹. Một tập hữu hạn `objects ⊆ Object OBJ` biểu diễn tập hợp tất cả các đối tượng đang tồn tại tại bất kỳ thời điểm nào. Mỗi kiểu thực thể `E` có `E ⊆ objects`. Có thể giả định thêm các tiên đề khác nếu cần, ví dụ, rằng các kiểu thực thể khác nhau không liên quan bởi quan hệ kiểu con thì có phạm vi (extent) rời nhau.

Để đơn giản, chúng tôi sẽ không xét đến các trường hợp giá trị biểu thức OCL `invalid` hoặc `null` trong bài báo này, và chúng tôi sẽ hoạt động hoàn toàn trong logic hai giá trị (two-valued logic) cho cả OCL và các biểu diễn logic của nó. Như đã lập luận trong [29], đây là một lựa chọn thực dụng giúp đơn giản hóa đáng kể việc phân tích các đặc tả, và là đủ dùng trong hầu hết các trường hợp. Người viết đặc tả chuyển đổi nên đảm bảo riêng rằng các phép định giá biểu thức không hợp lệ (invalid) không thể xảy ra trong các chuyển đổi của họ, bằng cách sử dụng các điều kiện xác định (definedness conditions) của biểu thức (Mục 5). Thay vì định nghĩa các toán tử như `select` hay `collect` bằng iterator, chúng tôi sẽ cho chúng một định nghĩa toán học thông thường dưới dạng các biểu thức liệt kê tập hợp (set-comprehension). Cuối cùng, tất cả các ký hiệu hàm và ký hiệu vị từ chuẩn cho số, chuỗi và tập hợp đều có thể được suy ra từ `=` và phép thuộc tập hợp (`:` hoặc `∈`).

Chúng tôi sử dụng một số mở rộng nhỏ của OCL. Đối với các kiểu thực thể `E` với một thuộc tính `id` được chỉ định là thuộc tính định danh (khóa chính), ký hiệu viết tắt `E[v]` được đưa vào để biểu diễn `E.allInstances()→select(id = v)→any()`, nếu `v` là đơn trị, và để biểu diễn `E.allInstances()→select(id : v)` nếu `v` có giá trị là một tập hợp. `E.id` biểu thị `E.allInstances()→collect(id)`. Miền hữu hạn các số từ `n` đến `m` (bao gồm cả hai đầu) được ký hiệu là `Integer.subrange(n,m)`. Toán tử `v→subcollections()` cho tập hợp các tập con hữu hạn của một tập hợp `v`. Toán tử `v→isDeleted()` biểu thị rằng đối tượng hoặc tập hợp đối tượng `v` bị xóa khỏi mô hình, tức là `objects→excludes(v)` đối với một đối tượng `v`; nó là nghịch đảo của `oclIsNew` [44]. Các toán tử `s→intersectAll(e)` và `s→unionAll(e)` tạo thành các phép giao và hợp phân tán (distributed intersections and unions), và bao đóng bắc cầu (transitive closure) của một đầu vai trò tự-liên kết đa trị (many-valued self-association role end) `r : E → Set(E)` được định nghĩa² là `x.r→closure() = Integer.subrange(0,E.size)→unionAll(n | x.rn)`.

Các ràng buộc trong phiên bản OCL này được biểu diễn về mặt toán học như các tiên đề lý thuyết tập hợp bậc nhất trong `LL`, cho mỗi ngôn ngữ `L`. Bảng 2 và Bảng 3 cho thấy một số ví dụ về diễn giải ngữ nghĩa của các toán tử logic OCL, các kiểu tập hợp và toán tử. Tổng cộng, chúng tôi đã định nghĩa ngữ nghĩa toán học cho 33 toán tử OCL trên các kiểu không phải tập hợp, và cho 36 toán tử kiểu tập hợp OCL [49].

Ở đây chúng tôi áp dụng ký hiệu lý thuyết tập hợp được sử dụng bởi hình thức luận B AMN [31]. Các tập hợp OCL được biểu diễn như các tập hợp toán học, các dãy (sequences) OCL `s` được biểu diễn như các ánh xạ từ `1..s.size` tới tập hợp các phần tử của chúng. Chuỗi (Strings) cũng được biểu diễn như các dãy số nguyên đại diện cho ký tự, hoặc như một kiểu nguyên thủy. `E[e/x]` biểu thị phép thay thế `e` cho các xuất hiện tự do của `x` trong `E` (tránh việc bắt biến tự do — avoiding free variable capture). `sq↑i` đối với dãy `sq` là dãy con ban đầu của `sq` với miền xác định `1..i`, `sq↓i` là dãy con của các phần tử có chỉ số `> i`.

Đối với ngôn ngữ ví dụ của chúng ta ở Hình 1, ta có một ngôn ngữ lý thuyết tập hợp bậc nhất hình thức tương ứng `LL`, có các ký hiệu kiểu (sort symbols) `(A,B)`, các ký hiệu hàm `(x, y, ar, br)`, và các tiên đề:

```
∀ a : A · x(a) > 0
∀ a : A; b : B · b ∈ br(a) ≡ a ∈ ar(b)
```

Do đó chúng ta có thể thao tác đồng thời với ba góc nhìn tương ứng của một ngôn ngữ: (i) như một tập hợp các kiểu thực thể và các đặc trưng dữ liệu cùng các quan hệ chuyên biệt hóa (specialisation relations) của chúng, được định nghĩa bởi một sơ đồ lớp, với các ràng buộc OCL định nghĩa các hạn chế trên các phần tử này; (ii) như các thể hiện của `M4`, cùng với các biểu diễn cú pháp trừu tượng của các ràng buộc; (iii) như các ngôn ngữ toán học trong lý thuyết tập hợp bậc nhất, cùng với các tiên đề trong những ngôn ngữ này biểu diễn ngữ nghĩa toán học của các ràng buộc.

*(¹ Như trong [11], chúng ta có thể đưa vào một tham chiếu `nullid` trong kiểu này để biểu diễn `null` của OCL. ² Tính không thể định nghĩa được của bao đóng bắc cầu hữu hạn trong phép tính vị từ thuần túy [5] không áp dụng cho lý thuyết tập hợp. `x.r0 = {x}, x.r1 = x.r, x.r2 = x.r.r`, v.v.)*

Giả sử sử dụng một ngôn ngữ kiểu-OCL làm ngôn ngữ ràng buộc, các tập hợp biểu thức hợp lệ về cú pháp `Exp(L)` và các câu (sentences) `Sen(L)` trong ngôn ngữ ràng buộc dựa trên một ngôn ngữ `L` có thể được xác định. `Exp(L)` trong bài báo này biểu thị tập hợp tất cả các biểu thức trong Hình 4 trên `L`. Nó cũng có thể được xem như một tập hợp các biểu thức và công thức của `LL`, thông qua diễn giải ngữ nghĩa biểu thức nêu trên³. Các hạng thức (terms) xuất hiện trong các phần tử của `Exp(L)` và `Sen(L)` luôn dựa trên các tập hợp hữu hạn, tức là, đối với mỗi biểu thức `e→select(x | P), e→forAll(x | P)`, v.v., `e` là hữu hạn.

**Bảng 2. Ánh xạ ngữ nghĩa cho các biểu thức logic và tập hợp OCL**

| Hạng thức OCL `e` | Điều kiện | Ngữ nghĩa `e′` |
|---|---|---|
| `P and Q` | | `P′ ∧ Q′` |
| `P or Q` | | `P′ ∨ Q′` |
| `P implies Q` | | `P′ ⇒ Q′` |
| `e→forAll(x \| P)` | | `∀x : e′ · P′` |
| `e→exists(x \| P)` | | `∃x : e′ · P′` |
| `e→exists1(x \| P)` | | `∃1 x : e′ · P′` |
| `Integer.subrange(a, b)` | `a, b : Integer` | `a′..b′` |
| `Set{e1, ..., en}` | | `{e1′, ..., en′}` |
| `Sequence{e1, ..., en}` | | `[e1′, ..., en′]` |
| `s→size()` | `s` là tập hợp hoặc dãy | lực lượng (cardinality) `card(s′)` |
| `s→subcollections()` | `s` là tập hợp | `F(s′)` |
| `s→at(i)` | `s` là dãy | `s′(i′)` |
| `s→includes(x)` | `s` là tập hợp | `x′ ∈ s′` |
| `s→excludes(x)` | `s` là tập hợp | `x′ ∉ s′` |
| `s→intersection(t)` | `s, t` là tập hợp | `s′ ∩ t′` |
| `s→union(t)` | `s, t` là tập hợp | `s′ ∪ t′` |
| `s→includes(x)` | `s` là dãy | `x′ ∈ ran(s′)` |
| `s→excludes(x)` | `s` là dãy | `x′ ∉ ran(s′)` |
| `s→including(x)` | `s` là tập hợp | `s′ ∪ {x′}` |
| `s→excluding(x)` | `s` là tập hợp | `s′ − {x′}` |
| `s→asSet()` | `s` là tập hợp | `s′` |
| `s→asSet()` | `s` là dãy | `ran(s′)` |
| `s→includesAll(t)` | `s, t` là tập hợp | `t′ ⊆ s′` |
| `s→includesAll(t)` | `s, t` là dãy | `ran(t′) ⊆ ran(s′)` |
| `s→excludesAll(t)` | `s, t` là tập hợp | `s′ ∩ t′ = {}` |
| `s→excludesAll(t)` | `s, t` là dãy | `ran(s′) ∩ ran(t′) = {}` |
| `s→sum()` | `s` là tập hợp | tổng các phần tử của `s′` |
| `s→sum()` | `s` là dãy, `card(s′) = n` | `s′(1) + ... + s′(n)` |
| `s→isUnique(x \| e)` | `s` là tập hợp | `card(s′) = card({e′[v/x] \| v ∈ s′})` |

**Bảng 3. Ánh xạ ngữ nghĩa cho các biểu thức lựa chọn (selection expressions)**

| Hạng thức OCL `e` | Điều kiện | Ngữ nghĩa `e′` |
|---|---|---|
| `objs→select(x \| P)` | `objs` là tập hợp | `{v \| v ∈ objs′ ∧ P′[v/x]}` |
| `objs→reject(x \| P)` | `objs` là tập hợp | `{v \| v ∈ objs′ ∧ ¬P′[v/x]}` |
| `objs→collect(x \| e)` | `objs` là tập hợp/bag | `{e′[v/x] \| v ∈ objs′}` |
| `objs→collect(x \| e)` | `objs` là dãy | `{i ↦ e′[objs′(i)/x] \| i ∈ dom(objs′)}` |
| `objs→intersectAll(x \| e)` | `e` có giá trị tập hợp | `∩ (objs→collect(x \| e))′` |
| `objs→unionAll(x \| e)` | `e` có giá trị tập hợp | `∪ (objs→collect(x \| e))′` |
| `s→subSequence(i, j)` | `s` là dãy | `(s′↑j′)↓(i′ − 1)` |
| `s→insertAt(i, x)` | `s` là dãy | `(s′↑(i′ − 1)) ⌢ [x′] ⌢ (s′↓(i′ − 1))` |
| `s→count(x)` | `s` là dãy | `card(s′ ∼(\|{x′}\|))` |
| `s→indexOf(x)` | `s` là dãy | `min(s′ ∼(\|{x′}\|))` |

Chúng tôi sẽ ký hiệu một ngôn ngữ `L` bằng một siêu mô hình `ΣL` là một thể hiện của `M4`, và một tập hợp các câu (OCL hoặc FOL) `ΓL` trên `ΣL` định nghĩa các hạn chế trên siêu mô hình này: `L = (ΣL, ΓL)`, trong đó `ΓL ⊆ Sen(L)`. Để thuận tiện, chúng tôi viết một siêu mô hình ngôn ngữ `ΣL` dưới dạng văn bản như một *chữ ký (signature)*: một định nghĩa của một bộ `(E1, ..., Ek)` các kiểu thực thể, và của một bộ `(f1, ..., fl)` các đặc trưng dữ liệu (thuộc tính và các đầu vai trò liên kết) trên các kiểu thực thể này, cùng với các ràng buộc ngôn ngữ trên các phần tử này, được bao gồm trong `ΓL`. Chúng tôi thường giả định việc bao gồm các kiểu nguyên thủy chuẩn `Integer`, `Boolean`, `String` và `Real` trong mỗi ngôn ngữ, do đó chúng sẽ không được liệt kê trong `ΣL`.

Siêu lớp (metaclass) `Structure` trong Hình 3 biểu diễn khái niệm về một cấu trúc (structure) hoặc một diễn giải (interpretation) của một ngôn ngữ: các cấu trúc như vậy sẽ có các biểu diễn cụ thể dưới dạng tập hợp và ánh xạ cho mỗi kiểu thực thể và đặc trưng của ngôn ngữ của chúng. Các chuyển đổi mô hình sẽ hoạt động trên các cấu trúc như vậy, chỉnh sửa chúng tại chỗ (in-place) hoặc tạo ra các cấu trúc mới từ dữ liệu của chúng.

Các cấu trúc cho một ngôn ngữ `L` có thể được biểu diễn dưới dạng các bộ `m = ((Em1, ..., Emk), (fm1, ..., fml))` cho ra các diễn giải của mỗi phần tử của `ΣL`:

1. Đối với mỗi kiểu thực thể `Ei` của `L`, `Emi` là một tập hữu hạn (các định danh đối tượng nguyên tử, không xác định cụ thể) biểu diễn phạm vi (extent) `Ei.allInstances()` của `Ei`. Đối với `Ei` trừu tượng, `Emi` là hợp của các phạm vi `Fm` của các kiểu con trực tiếp `F` của `Ei`.
2. Đối với một thuộc tính `fj : Typ` của `Ei`, `fmj` là một ánh xạ kiểu `Emi → Typ′` từ diễn giải kiểu thực thể nguồn của nó tới một miền giá trị cho kiểu đích của nó.
3. Một đầu liên kết đơn trị (số lượng 1) `fj : F` của `Ei` được diễn giải bởi một ánh xạ `fmj : Emi → Fm`.
4. Một đầu liên kết đa trị không thứ tự (tức là không phải số lượng 1) `fj : Set(F)` của `Ei` được diễn giải bởi một ánh xạ `fmj : Emi → F(Fm)`.
5. Một đầu liên kết đa trị có thứ tự `fj : Sequence(F)` của `Ei` được diễn giải bởi một ánh xạ `fmj : Emi → seq(Fm)`.
6. Nếu `E` là kiểu con của `F` thì `Em ⊆ Fm`.

Có một khái niệm về *đẳng cấu cấu trúc* (structure isomorphism) (Phụ lục A): `m ≃ n` nghĩa là các cấu trúc này không thể phân biệt được về mặt ngữ nghĩa bởi các câu của `L`. Một cấu trúc `m` của `L` có thể được xem là một thể hiện của `ΣL`, do đó chúng tôi viết `m : L` để nói rằng `m` là một cấu trúc cho `L`. `Mod(L)` biểu thị tập hợp các cấu trúc cho `L`. Điều này cũng có thể được xem như tập hợp các cấu trúc diễn giải (logic) cho ngôn ngữ toán học `LL`.

Một cấu trúc `m` của `L` được gọi là một *mô hình (ngữ nghĩa)* của `L` nếu nó thỏa mãn tất cả các tiên đề trong `ΓL` (tức là, tất cả các ràng buộc ngôn ngữ ngầm định và tường minh của `L`):

```
∀φ · φ ∈ ΓL ⇒ m |= φ
```

trong đó `|= ⊆ Mod(L) × F(Sen(L))` là quan hệ thỏa mãn (satisfaction relation) của `L` (tương đương của `LL`). Nếu `L = S ∪ T` cho các ngôn ngữ rời nhau `S` và `T`, sự thỏa mãn trên các cặp `(m, n)` các cấu trúc `m` của `S` và `n` của `T` được định nghĩa dựa trên việc diễn giải các phần tử ngôn ngữ `S` trong `m` và các phần tử ngôn ngữ `T` trong `n`: `(m,n) |= φ` cho `φ ∈ Sen(L)`. Tương tự đối với các bộ cấu trúc và ngôn ngữ.

Một quan hệ suy diễn (deduction relation) `⊢ ⊆ F(Sen(L)) × Sen(L)` được cho bởi các quy tắc suy diễn thông thường của logic bậc nhất có đẳng thức cho `LL`. Điều này liên hệ với `|=` bởi thuộc tính *đúng đắn* (soundness):

```
∆ ⊢ φ ⇒ (∀m : Mod(L) · m |= ∆ ⇒ m |= φ)
```

*(³ Trong một ngôn ngữ bậc nhất, các hạng thức (terms), được xây dựng từ các ký hiệu hàm, `+`, `→select`, v.v., được phân biệt với các công thức (formulae) hoặc vị từ (predicates), có toán tử ngoài cùng là một toán tử logic hoặc ký hiệu vị từ, `∈`, `=`, `<`, v.v. Một câu (sentence) là một công thức không có biến tự do.)*

đối với `∆ ⊆ Sen(L), φ ∈ Sen(L)`. Mối quan hệ ngược lại của *tính đầy đủ* (completeness) thường sẽ đúng:

```
(∀m : Mod(L) · m |= ∆ ⇒ m |= φ) ⇒ ∆ ⊢ φ
```

cho `∆ ⊆ Sen(L)` hữu hạn, `φ ∈ Sen(L)`. Chúng tôi thảo luận vấn đề này trong Phụ lục B.

> **Giải thích:** Đoạn này thiết lập nền tảng logic hình thức nghiêm ngặt cho toàn bộ khung xác minh: "thỏa mãn" (`|=`) là quan hệ ngữ nghĩa nói một cấu trúc/mô hình cụ thể có làm đúng một công thức logic hay không; "suy diễn" (`⊢`) là quan hệ cú pháp nói ta có thể *chứng minh* được công thức đó bằng các quy tắc logic hay không. "Đúng đắn" (soundness) nghĩa là mọi thứ chứng minh được thì cũng đúng về ngữ nghĩa (không chứng minh sai); "đầy đủ" (completeness) nghĩa là mọi thứ đúng về ngữ nghĩa thì cũng chứng minh được. Đây là hai tính chất kinh điển cần có để một hệ thống chứng minh đáng tin cậy.

### 2.2 Biểu diễn các chuyển đổi (Representation of transformations)

Ở mức đặc tả, hiệu ứng của một chuyển đổi có thể được đặc trưng bởi một tập hợp các đặc tả ánh xạ (mapping specifications), liên hệ các phần tử mô hình của một hoặc nhiều mô hình tham gia vào chuyển đổi với nhau [25]. Các đặc tả ánh xạ này định nghĩa các mối quan hệ dự kiến mà chuyển đổi cần thiết lập giữa các cấu trúc đầu vào (nguồn) và đầu ra (đích) của chuyển đổi, khi nó kết thúc. Tức là, chúng định nghĩa các hậu điều kiện (postconditions) `Post` của chuyển đổi.

Trong trường hợp các chuyển đổi tại chỗ (in-place), các giá trị ban đầu của các kiểu thực thể và đặc trưng có thể được ký hiệu là `E@pre, f@pre` trong các hậu điều kiện để phân biệt chúng với các giá trị trạng thái sau (post-state).

Ví dụ, một chuyển đổi tại chỗ `τ` trên ngôn ngữ `L` ở Hình 1 có thể được đặc tả bởi một ràng buộc đặc tả ánh xạ `R` trên một mô hình duy nhất (vừa đầu vào vừa đầu ra) `m : L`. `R` đặc tả rằng có các đối tượng `B` tương ứng với mỗi đối tượng `A` ban đầu:

```
A@pre→forAll(a | B→exists(b | b.y = a.x@pre * a.x@pre and a.br→includes(b)))
```

Đây là một hậu điều kiện của chuyển đổi: một vị từ cần đúng khi chuyển đổi kết thúc. Vì cả `A` lẫn `x` đều không bị `τ` cập nhật (tức là, chúng không nằm trong khung ghi — write frame `wr(R)` của `R`, Mục 5), hậu tố `@pre` có thể được lược bỏ, và `R` được viết đơn giản hơn là:

```
A→forAll(a | B→exists(b | b.y = a.x * a.x and a.br→includes(b)))
```

Một tiền điều kiện (precondition) cũng có thể được biểu thị, ví dụ, rằng `B` ban đầu không có thể hiện nào:

```
B = Set{}
```

Chúng tôi điều chỉnh siêu mô hình ánh xạ (mapping metamodel) của [25] để biểu diễn các đặc tả chuyển đổi như vậy (Hình 5).

*Fig. 5. Siêu mô hình đặc tả chuyển đổi (Transformation specification metamodel)*

Trong hình này, `Mapping`, `TransformationSpecification`, `ModelEnd` và `MappingEnd` là các lớp con của `NamedElement`. Các đặc tả chuyển đổi trong các ngôn ngữ chuyển đổi khai báo (declarative transformation languages) có thể được biểu thị trong siêu mô hình này, sử dụng các kỹ thuật trừu tượng hóa như những kỹ thuật được định nghĩa cho TGG (triple graph grammars — văn phạm đồ thị bộ ba) và QVT-R trong [14] và cho ATL trong [13]: những kỹ thuật này biểu thị hiệu ứng dự kiến của các chuyển đổi bằng một siêu mô hình cộng với các ràng buộc OCL mô tả trạng thái sau (poststate) của chuyển đổi. Các chuyển đổi trong các ngôn ngữ lai (hybrid) và mệnh lệnh (imperative) cũng nên được cho các đặc tả tiền điều kiện và hậu điều kiện, để cung cấp cơ sở cho việc xác minh chúng. Đến lượt mình, các biểu diễn hình thức của các đặc tả chuyển đổi có thể được sinh ra từ các biểu diễn trong siêu mô hình này, theo một loạt các hình thức luận như B [36], Z3 [51] hoặc Alloy [2], để hỗ trợ phân tích ngữ nghĩa. Siêu mô hình có thể được mở rộng để bao gồm các quan hệ tổng quát hóa (generalisation relations) giữa các ánh xạ, như trong ETL [28].

Các ràng buộc `rules.relation` biểu thị các hậu điều kiện `Post` của chuyển đổi: tất cả các ràng buộc này cần đúng khi chuyển đổi kết thúc. Thông thường mỗi ràng buộc quan hệ ánh xạ `Cn ∈ Post` có dạng một phép kéo theo (implication) `SCond implies Succ` được lượng hóa toàn thể (forall-quantified) trên các phần tử (các đầu ánh xạ nguồn `s : Si`) của các mô hình nguồn. Các *điều kiện áp dụng* (application conditions) `ACond` của ánh xạ khi đó là `SCond and not(Succ)`, tức là, ánh xạ có thể áp dụng khi các giả định của nó đúng và khi nó chưa được thiết lập. Việc phân tích *tính xác định* (determinacy) và *tính xác định giá trị* (definedness) của các ánh xạ có thể được thực hiện bằng phân tích cú pháp các ràng buộc `relation` của chúng, như được mô tả trong Mục 5.

Các *giả định* (assumptions) biểu thị các tiền điều kiện `Asm` của chuyển đổi. Các *bất biến* (invariants) định nghĩa các thuộc tính `Inv` cần đúng ban đầu, và cần được bảo toàn (preserved) bởi mỗi bước tính toán (computation step) của chuyển đổi: chúng có tác dụng hạn chế các triển khai khả dĩ của chuyển đổi chỉ còn lại những triển khai thực sự duy trì `Inv`. Các hậu điều kiện, tiền điều kiện và bất biến có thể được biểu thị trong hợp rời (disjoint union) của các ngôn ngữ `parameters.language` tham gia vào chuyển đổi, với các phiên bản trạng thái trước (pre-state) của các phần tử ngôn ngữ cũng được sử dụng trong trường hợp các tham số vừa là đầu vào vừa là đầu ra.

Một chuyển đổi `τ` bảo toàn các cấu trúc `p ∈ τ.parameters` có `p.modifiable = false`, ngược lại `τ` có thể thay đổi dữ liệu của một cấu trúc thực tế được cung cấp làm giá trị cho `p`. Nếu một đầu ánh xạ (mapping end) có thể sửa đổi được (modifiable), thì cấu trúc của nó cũng vậy: `modifiable = true implies model.modifiable = true` là một bất biến của `MappingEnd`. Kiểu thực thể của một đầu ánh xạ cũng phải thuộc về ngôn ngữ của đầu mô hình (model end) của đầu ánh xạ đó: `type : model.language.entityTypes` là một bất biến của `MappingEnd`. Các mô hình đích (target models) có `modifiable = true`, các mô hình nguồn (source models) chỉ có thể sửa đổi được nếu chúng đồng thời cũng là mô hình đích.

Các hệ thống chuyển đổi có thể được biểu diễn bằng các sơ đồ hoạt động (activity diagrams) UML, trong đó các chuyển đổi là các nút hoạt động thực thi được (executable activity nodes) và các cấu trúc hoặc mô hình mà chúng thao tác là các nút đối tượng (dữ liệu) (object/data nodes). Ví dụ, Hình 6 cho thấy một phép hợp thành tuần tự (sequential composition) của hai chuyển đổi. Một luồng đối tượng (object flow) từ `τ` tới `n : T` chỉ ra rằng `n` là một tham số có thể sửa đổi của `τ`.

*Fig. 6. Hợp thành tuần tự của các chuyển đổi (Sequential composition of transformations)*

Các triển khai chuyển đổi (transformation implementations) được định nghĩa bởi một *hành vi* (behavior), chẳng hạn như một `Activity` UML, trong đó các thể hiện `RuleImplementation` là các nút hoạt động thực thi được. Mỗi triển khai quy tắc (rule implementation) dành cho một ánh xạ cụ thể, và bản thân nó có một hoạt động hoặc hành vi khác định nghĩa các hành động của nó (Hình 7). Một khái niệm then chốt cho cả các ngôn ngữ chuyển đổi đồ thị (graph-transformation) và chuyển đổi mô hình (model-transformation) là ý tưởng về một *bước tính toán* (computation step) hoặc *bước chuyển đổi* (transformation step): việc áp dụng một quy tắc viết lại (rewrite rule) hoặc quy tắc chuyển đổi cụ thể vào một vị trí khớp (matching location) cụ thể trong một đồ thị hoặc vào (các) phần tử khớp cụ thể trong một mô hình. Điều này cũng được mô hình hóa như một hành vi trong Hình 7: mỗi triển khai quy tắc thường sẽ dựa trên một số phép lặp của bước đó cho ánh xạ mà nó triển khai.

*Fig. 7. Siêu mô hình triển khai chuyển đổi (Transformation implementation metamodel)*

Siêu mô hình này có thể được sử dụng để biểu diễn các quy tắc trong các ngôn ngữ lai hoặc mệnh lệnh, ví dụ, GrGen [26], ATL [24], ETL [25] hoặc Kermeta [17]. Thay vì tạo một siêu mô hình cho mỗi ngôn ngữ chuyển đổi khác nhau (ETL, ATL, GrGen, v.v.), chúng tôi sử dụng siêu mô hình triển khai chung để biểu thị và suy luận về các thuộc tính ở mức triển khai, độc lập với ngôn ngữ. Cần định nghĩa các ánh xạ giữa các ngôn ngữ này và một biểu diễn hành vi tổng quát phù hợp, chúng tôi cho rằng điều này khả thi vì các ngôn ngữ chuyển đổi mô hình có nhiều khía cạnh chung, chẳng hạn như các cơ chế tra cứu (lookup) sử dụng dấu vết (traces). Chúng tôi minh họa cách các ánh xạ như vậy có thể được định nghĩa trong các Mục 10 và 11.

Hành vi của một triển khai `I` của một chuyển đổi `τ` sẽ xác định thứ tự mà các `δ ∈ RuleImplementation` sẽ được thực thi. Mỗi `δ` đến lượt nó có một hành vi nội tại, thường được định nghĩa theo các bước tính toán `δr(ss)` cố gắng thiết lập ánh xạ đặc tả `r = δ.applies` cho các phần tử cụ thể `ss` trong các miền nguồn của ánh xạ. Do đó `δ.computationStep = δr`.

Ví dụ, ràng buộc `R` sẽ có các bước tính toán riêng lẻ `δR(a)` cho `a ∈ A`, mỗi bước tạo ra một `b ∈ B` mới và đặt `b.y = a.x * a.x` và thêm `b` vào `a.br` (và ngầm định thêm `a` vào `b.ar`), do đó thiết lập công thức lượng hóa của `R` cho `a`. Các phép áp dụng ràng buộc `δr(ss)` như vậy là các bước tính toán của cả các triển khai `δ` của một `Cn ∈ Post` cụ thể lẫn của triển khai tổng thể `I` của một chuyển đổi `τ`. Một *tính toán từng phần* (partial computation) của `I` cho `τ` là một dãy hữu hạn `sq` các bước tính toán của `I`, sao cho `sq` có dạng được cho phép bởi hành vi của `I`, và sao cho `Inv` đúng trong các cấu trúc ban đầu `(m1, ..., mq)` được cung cấp làm tham số đầu vào của `τ`, và `Inv` đúng ở trạng thái cuối của `sq` và sau mọi dãy con ban đầu của `sq`.

Một *tính toán hoàn chỉnh* (completed computation) của `I` từ các cấu trúc ban đầu `(m1, ..., mq)` được cung cấp làm giá trị tham số của `τ`, tới các giá trị cấu trúc cuối cùng (terminal) `(n1, ..., nq)` cho các tham số này, sẽ được ký hiệu là:

```
(m1, ..., mq) −→τ,I (n1, ..., nq)
```

Nếu tham số `i` không thể sửa đổi, `ni = mi`. Một tính toán hoàn chỉnh từ `(m1, ..., mq)` tới `(n1, ..., nq)` cho `τ ∈ TransformationSpecification` trong đó `I.specification = τ`, bao gồm một dãy hữu hạn `sq` các bước tính toán của `I`, sao cho `sq` có dạng được cho phép bởi thuật toán triển khai của `I`, `Inv` đúng ban đầu và tại mọi trạng thái trung gian (tức là, sau bất kỳ dãy con ban đầu nào của `sq`), và tại đó không còn bước nào khác được `I` cho phép từ `(n1, ..., nq)`, và sao cho không có dãy con ban đầu ngắn hơn nào của `sq` có thuộc tính này.

Đối với chuyển đổi ví dụ của chúng ta, một tính toán hoàn chỉnh theo triển khai vòng lặp có giới hạn chuẩn (standard bounded loop implementation) của `R` sẽ là một dãy `[δR(a1), ..., δR(ap)]` bao gồm tất cả các bước tính toán cho các `ai ∈ A` khác nhau trong mô hình nguồn, mỗi `ai` được xử lý đúng một lần, theo một thứ tự tùy ý. Một tính toán từng phần sẽ là bất kỳ dãy con ban đầu nào của một dãy như vậy.

Đối với các chuyển đổi đã tồn tại, các bước tính toán và triển khai quy tắc có thể được định nghĩa bằng bất kỳ phương tiện nào có sẵn trong ngôn ngữ chuyển đổi (như trong các nghiên cứu tình huống 2 và 3 dưới đây). Ngược lại, đối với các chuyển đổi mới, các bước, các triển khai quy tắc và triển khai tổng thể có thể được suy ra một cách có hệ thống từ đặc tả chuyển đổi (Mục 8).

Ký hiệu `(m1, ..., mq) −→τ (n1, ..., nq)` nghĩa là có một tính toán hoàn chỉnh `(m1, ..., mq) −→τ,I (n1, ..., nq)` cho một triển khai `I` nào đó của `τ`.

Chúng tôi sử dụng ngôn ngữ hoạt động (activity language) giống chương trình sau đây để mô tả hành vi độc lập với ngôn ngữ của các chuyển đổi lai và mệnh lệnh.

Cú pháp cụ thể BNF của ngôn ngữ này như sau:

```
<statement> ::= <loop statement> | <creation statement> | <conditional statement> | <sequence statement> | <basic statement>

<loop statement> ::= "while" <expression> "do" <statement> "invariant" <expression> "variant" <expression>
                    | "for" <expression> "do" <statement>

<conditional statement> ::= "if" <expression> "then" <statement> "else" <basic statement>

<sequence statement> ::= <statement> ";" <statement>

<creation statement> ::= <identifier> ":" <type name>

<basic statement> ::= <basic expression> ":=" <expression>
                     | "skip"
                     | "return" <expression>
                     | "(" <statement> ")"
                     | <call expression>
```

Điều này định nghĩa một kiểu con `Statement(L)` của `Behavior`, khi dựa trên các biểu thức `Exp(L)` của ngôn ngữ `L`. Ngữ nghĩa của các câu lệnh này được cho bởi toán tử tiền điều kiện yếu nhất (weakest-precondition operator) `[ ] : Statement(L) × Exp(L) → Exp(L)`, sử dụng các định nghĩa chuẩn, như đối với ngôn ngữ Thay thế Tổng quát hóa (Generalised Substitution) của B [31]. Ví dụ (sử dụng ký hiệu toán học chuẩn cho các biểu thức ở vế phải):

```
[obj.f := e]P ≡ P[(f ⊕ {obj ↦ e})/f]     đối với đối tượng đơn obj, đặc trưng ghi được f
[objs.f := e]P ≡ P[(f ⊕ (objs × {e}))/f]  đối với tập hợp objs, f ghi được
[x := e]P ≡ P[e/x]                        đối với biến hoặc kiểu thực thể x
[(x : E ; S)]P ≡ ∀x · x : ObjectOBJ − objects ⇒ [E := E ∪ {x}; objects := objects ∪ {x}; S]P   đối với biến x, kiểu thực thể cụ thể E
[if E then S1 else S2]P ≡ (E ⇒ [S1]P) ∧ (¬E ⇒ [S2]P)
[S1; S2]P ≡ [S1]([S2]P)
[for x : e do S(x)]P ≡ [S(e1)]...[S(en)]P    nếu e = Sequence{e1, ..., en}
[for x : e do S(x)]P ≡ ∧sq∈serial(e)[for x : sq do S(x)]P   trong các trường hợp khác
```

`ObjectOBJ` là một kiểu đếm được của tất cả các tham chiếu đối tượng khả dĩ, `objects` duy trì tập hợp các tham chiếu đối tượng của tất cả các đối tượng đang tồn tại. Trong mệnh đề tạo `x : E`, các cập nhật `F := F ∪ {x}` cho mỗi siêu kiểu `F` của `E` cũng sẽ được bao gồm.

Trong mệnh đề cuối, một phép hội (conjunction) được lấy trên tất cả các cách sắp xếp tuần tự (serialisations) khả dĩ của `e` tại thời điểm bắt đầu vòng lặp: `serial(s) = {sq : 1..s.size → s | ran(sq) = s}` cho một tập hợp `s`. Trong thực tế, một vòng lặp có giới hạn (bounded loop) kiểu này có thể được phân tích bằng cách chỉ ra rằng các `S(x)` riêng lẻ độc lập với thứ tự thực thi đối với các `x` khác nhau, và do đó chỉ cần phân tích một cách sắp xếp tuần tự, vì tất cả đều tương đương về mặt ngữ nghĩa (Mục 8).

Đối với các vòng lặp không có giới hạn (unbounded loops), chúng tôi sử dụng phép suy diễn:

```
(I ∧ E ⇒ [S]I) ∧ (I ∧ ¬E ⇒ P) ∧ (I ∧ E ⇒ v ∈ N) ∧ (∀γ : N · I ∧ E ∧ v = γ ⇒ [S](v < γ)) 
  ⇒ [while E do S invariant I variant v]P
```

> **Giải thích:** Đây là quy tắc chứng minh chuẩn cho vòng lặp `while` dùng "biến thể vòng lặp" (loop variant) `v` — một đại lượng số tự nhiên giảm dần sau mỗi lần lặp — để chứng minh vòng lặp chắc chắn dừng (termination), kết hợp với "bất biến vòng lặp" (loop invariant) `I` — một điều kiện luôn đúng trước và sau mỗi lần lặp — để chứng minh tính đúng đắn của kết quả khi vòng lặp kết thúc.

Đối với các lời gọi thao tác (operation calls), ngữ nghĩa gọi-theo-giá-trị-kết-quả (call-by-value-result) được sử dụng. Trong phần còn lại của bài báo chúng tôi sẽ xem xét các chuyển đổi hoặc là các chuyển đổi *mô hình tách biệt* (separate-models) với một nguồn và một đích: `τ : S → T`, hoặc các chuyển đổi *cập nhật tại chỗ* (update-in-place) trên một mô hình duy nhất: `τ : S → S`. Các kỹ thuật xác minh mà chúng tôi định nghĩa có thể được sử dụng theo cùng cách cho các chuyển đổi với nhiều ngôn ngữ đầu vào và đầu ra.

Đối với các chuyển đổi mô hình tách biệt, để liên hệ các thuộc tính của một mô hình nguồn với những thuộc tính có thể biểu thị được trong một mô hình đích, chúng tôi sử dụng khái niệm *đồng cấu ngôn ngữ* (language morphism) hay diễn giải (interpretation). Đây là một ánh xạ `χ : S → T` từ ngôn ngữ nguồn `S` tới một ngôn ngữ đích `T`, bao gồm một đồng cấu chữ ký (signature morphism) `χ : ΣS → Exp(T)` từ các kiểu thực thể của `S` sang các biểu thức có giá trị tập hợp của `T`, và các đặc trưng của `S` sang các đặc trưng hoặc biểu thức biểu thị các ánh xạ có cùng ngôi (arity) và các kiểu tương ứng của `T`, và các đồng cấu cảm sinh (induced morphisms) `Sen(χ) : Sen(S) → Sen(T)` và `Mod(χ) : Mod(T) → Mod(S)` sử dụng `χ` để diễn giải các câu của `S` thành các câu của `T`, và diễn giải các cấu trúc của `T` thành các cấu trúc cho `S`. `Sen(χ)(φ)` được viết là `χ(φ)` trong phần tiếp theo. Có một phạm trù (category) `LANG` gồm các ngôn ngữ và đồng cấu ngôn ngữ, và một phạm trù `PLANG` gồm các ngôn ngữ và các đồng cấu ngôn ngữ từng phần (partial language morphisms) (trong đó `χ : ΣS ⇾ Exp(T)`).

> **Giải thích:** "Đồng cấu ngôn ngữ" ở đây là một khái niệm mượn từ lý thuyết phạm trù (category theory), dùng để mô tả cách "dịch" các khái niệm của ngôn ngữ mô hình nguồn sang ngôn ngữ mô hình đích một cách có hệ thống — giống như một "từ điển" ánh xạ mỗi kiểu thực thể và thuộc tính bên nguồn sang một biểu thức tương ứng bên đích, để từ đó có thể so sánh/liên hệ các thuộc tính (bất biến, hậu điều kiện...) đã biết đúng trên mô hình nguồn với các thuộc tính cần trên mô hình đích.

## 3 Các thuộc tính xác minh chuyển đổi (Transformation verification properties)

Rất nhiều thuộc tính xác minh đã được đề xuất cho các chuyển đổi mô hình, ví dụ, [14, 36]. Trong mục này chúng tôi hình thức hóa một số thuộc tính then chốt sử dụng khung làm việc của Mục 2, và trong các mục tiếp theo chúng tôi xác định các kỹ thuật và công nghệ để thiết lập các thuộc tính này.

Đối với các chuyển đổi mô hình tách biệt `τ` với một tham số đích có thể sửa đổi `n : T` và một nguồn được bảo toàn `m : S`, các tính toán hoàn chỉnh của `τ` sẽ có dạng

```
(m, n0) −→τ (m, n)
```

trong đó `n0` là một mô hình khởi tạo mặc định thường là cấu trúc `T` rỗng ∅⁴. Chúng tôi nói rằng `n` có thể được sinh ra từ `(m, n0)` bởi `τ` nếu có một tính toán hoàn chỉnh như vậy.

Các thuộc tính đúng đắn (correctness properties) có thể được xem xét hoặc cho một triển khai cụ thể `I` của `τ`, hoặc cho tất cả các triển khai khả dĩ duy trì các bất biến `Inv`.

*Tính đúng đắn cú pháp* (Syntactic correctness) của `τ` có thể được hình thức hóa như sau:

```
(m, n0) |= Asm ∪ ΓS ⇒ n |= ΓT
```

cho mỗi cấu trúc `m` của `S`, trong đó `n : T` có thể được sinh ra từ `(m, n0)` bởi (bất kỳ triển khai nào của) `τ`, và `Asm` là các giả định của `τ`. Tức là, nếu `m` là một mô hình của `S`, bất kỳ cấu trúc `n` nào được sinh ra bởi `τ` từ `m` cần phải là một mô hình của `T`. Nếu giới hạn vào một triển khai cụ thể `I`, tính đúng đắn cú pháp nghĩa là các cấu trúc được sinh ra từ các mô hình của `S` bởi `I` cần phải là các mô hình của `T`.

`τ` được gọi là *bảo toàn ngữ nghĩa* (semantically preserving) tương đối theo một diễn giải ngôn ngữ `χ : S → T` [36] nếu:

```
m |= φ ⇒ n |= χ(φ)
```

cho `n : T` được sinh ra từ `m : S`, `n0 : T` bởi (bất kỳ triển khai nào của) `τ`, và cho `φ ∈ Sen(S)`. Việc bảo toàn có thể chỉ được yêu cầu cho các thuộc tính trong một tập con `Pres` của `Sen(S)`, và/hoặc cho `(m, n0) |= Asm`. Việc bảo toàn ngữ nghĩa bởi một triển khai cụ thể `I` của `τ` được phát biểu tương tự.

`τ` là một *tương đương ngữ nghĩa* (semantic equivalence) nếu `m |= φ ≡ n |= χ(φ)` cho `n ∈ Mod(T)` được sinh ra từ `m ∈ Mod(S)`, `n0` bởi `τ`, và cho `φ ∈ Sen(S)`.⁵

*(⁴ Cấu trúc trong đó mỗi kiểu thực thể của `T` được diễn giải bởi tập rỗng. ⁵ Đồng cấu `χ` sẽ là một *đồng cấu định chế* (institution morphism) [21] nếu `τ` có `Mod(χ)` như một nghịch đảo phải (right inverse), và `τ` là một tương đương ngữ nghĩa.)*

*Tính đúng đắn ngữ nghĩa* (Semantic correctness) của một triển khai `I` của `τ` nghĩa là triển khai này thiết lập được các hậu điều kiện đã đặc tả `Post` của `τ`:

```
(m, n0) |= Asm ⇒ (m, n) |= Post
```

cho `n : T` được sinh ra từ `m : S` và `n0 : T` bởi `I`.

*Bảo toàn ngữ nghĩa mức mô hình* (Model-level semantic preservation) nghĩa là ngữ nghĩa nội tại của các mô hình nguồn được bảo toàn, có thể dưới một diễn giải `ζ`, bởi `τ`. Gọi `semL : Mod(L) → Sem(L)` là các hàm gán ngữ nghĩa cho các mô hình của các ngôn ngữ `L = S`, `L = T`, và `ζ : Sem(S) → Sem(T)`, khi đó việc bảo toàn ngữ nghĩa mức mô hình nghĩa là:

```
ζ(semS(m)) ≈ semT(n)
```

cho một quan hệ tương đương `≈` nào đó trên miền ngữ nghĩa, và trong đó `(m,n0) |= Asm` và `(m,n0) −→τ (m,n)` hoặc `(m,n0) −→τ,I (m,n)`. Điều này cũng có thể được biểu thị tương đương như một thuộc tính sơ đồ giao hoán (commuting-diagram property) [39]. Trong nhiều trường hợp ngữ nghĩa có thể được hình thức hóa trong `LS` và `LT`, do đó việc bảo toàn ngữ nghĩa mức mô hình có thể được quy về việc bảo toàn ngữ nghĩa mức ngôn ngữ tương đối theo một diễn giải `χ` phù hợp, hoặc về việc bảo toàn bất biến của một công thức biểu thị thuộc tính sơ đồ giao hoán. Ví dụ, nếu các mô hình là các máy trạng thái (state machines), tập hợp các vết sự kiện đầu vào (input event traces) của chúng có thể được hình thức hóa trong FOL như các tập hợp các dãy, và việc bảo toàn các tập hợp như vậy bởi `τ` có thể được biểu thị như việc bảo toàn một công thức bất biến `φ` phù hợp. Mục 11 đưa ra một ví dụ về kiểu lập luận này.

Một chuyển đổi `τ` là *hợp lưu* (confluent) nếu với mọi `m : S`, và `n, n′` có thể được sinh ra bởi một tính toán hoàn chỉnh của `τ` từ `(m,n0)`, thì `n ≃ n′`. Tương tự cho các triển khai cụ thể `I` của `τ`.

`τ` (hoặc một triển khai `I` của `τ`) là *dừng* (terminating) nếu với mỗi mô hình `m` của `S`, `(m,n0) |= Asm`, mọi tính toán từng phần của `τ` (`I`) từ `(m,n0)` đều có một tính toán hoàn chỉnh mở rộng nó.

Các hình thức hóa tương tự có thể được đưa ra cho các chuyển đổi cập nhật tại chỗ. Một chuyển đổi `τ` hoạt động trên một mô hình duy nhất của ngôn ngữ `S` có thể được xem là có các tính toán `(m,m) −→τ (m,n)` trong đó chúng ta ngầm giữ lại mô hình ban đầu `m : S` để biểu thị hiệu ứng của chuyển đổi bằng các vị từ liên hệ các giá trị ban đầu của phạm vi (extents) và đặc trưng của kiểu thực thể (được ký hiệu bằng `E@pre` và `f@pre` trong các quan hệ ánh xạ chuyển đổi) với các giá trị cuối cùng của chúng (được ký hiệu bằng `E` và `f`).

*Tính đúng đắn cú pháp* của `τ` như vậy có thể được hình thức hóa như sau:

```
m |= Asm ∪ ΓS ⇒ n |= ΓS
```

cho mỗi cấu trúc `m` của `S`, trong đó `n : S` có thể được sinh ra từ `m` bởi `τ`, và `Asm` là các giả định của `τ`.

*Tính đúng đắn ngữ nghĩa* của một triển khai `I` của `τ` nghĩa là `I` thiết lập được các hậu điều kiện đã đặc tả `Post` của `τ`:

```
m |= Asm ⇒ (m,n) |= Post
```

cho `n : S` được sinh ra từ `m : S` bởi `I`, trong đó các hạng thức trạng thái trước (pre-state terms) trong `Post` được lượng giá trong `m`.

Các định nghĩa về bảo toàn ngữ nghĩa mức mô hình, tính dừng và tính hợp lưu tương tự như đối với trường hợp mô hình tách biệt.

## 4 Các kỹ thuật xác minh chuyển đổi (Transformation verification techniques)

Bốn cách tiếp cận chính, khác biệt nhau, đã được sử dụng hoặc đề xuất cho việc xác minh chuyển đổi mô hình:

1. Phân tích tĩnh (static analysis) bằng phân tích cú pháp văn bản nguồn của chuyển đổi, ví dụ, để xác định các quan hệ phụ thuộc dữ liệu (data-dependency relations) giữa các biến hoặc quy tắc [36].
2. Xây dựng các phản ví dụ (counter-examples) cho các thuộc tính, sử dụng các bộ kiểm tra mô hình (model checkers) hoặc bộ kiểm tra thỏa mãn (satisfaction checkers) [2, 14, 12, 13].
3. Chứng minh các thuộc tính sử dụng các bộ chứng minh định lý tự động hoặc tương tác (automated or interactive theorem-provers) [36, 20].
4. Tổng hợp chuyển đổi đúng-theo-cấu-trúc (correct-by-construction synthesis) từ các đặc tả [45, 38].

Cả 2 và 3 đều có thể liên quan đến việc ánh xạ văn bản chuyển đổi sang một hình thức luận hỗ trợ phân tích ngữ nghĩa: mô hình ngữ nghĩa này được gọi là *mô hình xác minh* (verification model) hoặc *mô hình chuyển đổi* (transformation model) [36]. Bản thân ánh xạ ngữ nghĩa nên là một chuyển đổi bảo toàn ngữ nghĩa hoặc tương đương ngữ nghĩa, theo nghĩa của các đồng cấu ngược định chế (institution co-morphisms) [41].

Khung xác minh của chúng tôi dựa trên việc sử dụng quy trình của Hình 8 để biểu thị một loạt các ngôn ngữ chuyển đổi khác nhau trong các siêu mô hình đặc tả và triển khai chuyển đổi của Mục 2 và sau đó ánh xạ các biểu diễn này sang các hình thức luận xác minh. Cách tiếp cận này có nghĩa là chỉ cần định nghĩa và xác minh một ánh xạ ngữ nghĩa duy nhất cho mỗi hình thức luận đích, thay vì các ánh xạ ngữ nghĩa cho từng ngôn ngữ chuyển đổi khác nhau và từng hình thức luận đích khác nhau.

*Fig. 8. Quy trình xác minh (Verification process)*

Chúng ta có thể phân biệt giữa các hình thức hóa đơn-trạng-thái (single-state formalisations), chỉ định nghĩa một mô hình ngữ nghĩa hình thức của một trạng thái của một chuyển đổi, thường là trạng thái cuối [13], và các cách tiếp cận đa-trạng-thái (multi-state approaches) hình thức hóa các chuỗi thực thi khả dĩ của chuyển đổi [20]. Cách tiếp cận trước có thể được áp dụng để phân tích tính đúng đắn cú pháp và các thuộc tính trạng thái cuối khác, trong khi cách tiếp cận sau có thể được dùng để chứng minh tính bất biến của các thuộc tính, tính dừng và tính hợp lưu.

Phân tích cú pháp thường là cách tiếp cận ít tốn kém tài nguyên nhất, nhưng có thể không thể thiết lập được tất cả các thuộc tính. Phân tích phản ví dụ là một phiên bản kiểm thử (testing) dựa trên đặc tả, và có thể phát hiện lỗi nhưng không thể thiết lập các thuộc tính cho tất cả các trường hợp. Ngược lại, các cách tiếp cận chứng minh có thể, về nguyên tắc, thiết lập được tính đúng đắn của một chuyển đổi cho tất cả các mô hình đầu vào hợp lệ khả dĩ, nhưng những cách tiếp cận như vậy đòi hỏi nỗ lực đáng kể. Cuối cùng, các cách tiếp cận đúng-theo-cấu-trúc có thể đảm bảo tính đúng đắn cho các chuyển đổi được đặc tả sử dụng các dạng quy tắc chuyển đổi bị hạn chế. Chúng cũng có thể đòi hỏi nỗ lực chứng minh để thiết lập rằng các thuộc tính đặc tả cần thiết được thỏa mãn.

Việc chứng minh các thuộc tính xác minh bằng tay hoặc có sự hỗ trợ của công cụ đòi hỏi một tổ chức rõ ràng các bước xác minh và việc phân bổ các bước này cho các công cụ phù hợp. Chúng tôi nhận thấy khái niệm về một vị từ *bất biến chuyển đổi* (transformation invariant) `Inv` có tầm quan trọng then chốt trong việc kết nối các thuộc tính của các tính toán chuyển đổi với các thuộc tính cần thiết của các đặc tả chuyển đổi. Đối với các chuyển đổi cập nhật tại chỗ như tái cấu trúc (refactorings), bất biến chuyển đổi liên hệ các trạng thái trung gian được tạo ra trong quá trình chuyển đổi với trạng thái ban đầu, và hỗ trợ việc chứng minh, bằng quy nạp trên các bước chuyển đổi, rằng một số thuộc tính nhất định được bảo toàn. Việc chứng minh tính dừng cho các chuyển đổi như vậy thường đòi hỏi định nghĩa một hàm *biến thể chuyển đổi* (transformation variant) `Q`: một biểu thức có giá trị nguyên không âm mà giá trị của nó giảm nghiêm ngặt sau mỗi bước chuyển đổi. Tính hợp lưu (confluence) sẽ theo sau nếu điều kiện `Q = 0` chỉ có thể xảy ra ở một trạng thái cuối duy nhất (sai khác đẳng cấu) của chuyển đổi, có thể đạt tới được từ mỗi trạng thái ban đầu đã cho. Đối với các chuyển đổi có mô hình nguồn và đích tách biệt, bất biến chuyển đổi và hậu điều kiện có thể hỗ trợ chứng minh tính đúng đắn cú pháp và bảo toàn ngữ nghĩa bằng cách liên hệ các phần tử đích với các phần tử nguồn mà chúng được suy ra, và sự tương ứng phần tử này, cùng với lý thuyết ngôn ngữ nguồn `ΓS`, cho phép suy diễn các thuộc tính của mô hình đích từ các thuộc tính của mô hình nguồn. Bất biến, cùng với các giả định về trạng thái ban đầu của mô hình đích, đặc biệt hữu ích để chỉ ra tính bảo toàn (conservativeness) của một chuyển đổi: rằng không có phần tử hay thuộc tính thừa nào được tạo ra trong mô hình đích. Để chỉ ra tính đúng đắn ngữ nghĩa của một triển khai cụ thể `I`, chúng tôi suy ra hậu điều kiện `Post` của chuyển đổi từ sự kết hợp của `Inv` và sự kiện rằng ở trạng thái cuối của chuyển đổi, không còn bước tính toán nào khác có thể áp dụng theo hành vi của `I` (và `Q = 0` đối với các chuyển đổi cập nhật tại chỗ).

> **Giải thích:** Đây là "trái tim" phương pháp luận của bài báo. "Bất biến chuyển đổi" (invariant) giống như một điều kiện luôn đúng ở mọi bước trong quá trình chuyển đổi (giống bất biến vòng lặp trong lập trình): nó giúp ta chứng minh từng bước nhỏ không phá vỡ tính đúng đắn. "Biến thể" (variant) là một đại lượng đo "còn bao nhiêu việc phải làm", luôn giảm dần, dùng để chứng minh chuyển đổi chắc chắn kết thúc (không lặp vô hạn). Khi biến thể về 0, đó là lúc chuyển đổi hoàn tất; nếu trạng thái cuối là duy nhất, chuyển đổi có tính hợp lưu (không phụ thuộc thứ tự áp dụng quy tắc).

Bảng 4 tóm tắt cách các thuộc tính cụ thể có thể được suy ra bằng chứng minh thủ công hoặc có công cụ hỗ trợ, sử dụng các bất biến và biến thể chuyển đổi. `Asm0` biểu thị các ràng buộc `Asm` chỉ là các vị từ của `S`. Đối với các chuyển đổi cập nhật tại chỗ, cả `Inv` và `Post` có thể liên hệ các giá trị trạng thái trước `f@pre, E@pre` của các đặc trưng và phạm vi kiểu thực thể với các giá trị trạng thái sau `f`, `E` của chúng.

**Bảng 4. Các kỹ thuật chứng minh cho các thuộc tính xác minh**

| Thuộc tính | Mô hình tách biệt `τ : S → T` | Cập nhật tại chỗ `τ : S → S` |
|---|---|---|
| Bảo toàn ngữ nghĩa của `φ ∈ Pres` | `Asm0, Inv, ΓS, Post, Pres ⊢ χ(φ)` | `Asm@pre, Inv, ΓS, Post, Q = 0, Pres@pre ⊢ χ(φ)` |
| Đúng đắn cú pháp | `Asm0, Inv, ΓS, Post ⊢ φ` cho `φ ∈ ΓT` | `ΓS` là bất biến |
| Đúng đắn ngữ nghĩa | `Asm0, Inv, ΓS`, không còn bước nào áp dụng được `⊢ Post` | `Asm@pre, Inv, ΓS, Q = 0`, không còn bước nào áp dụng được `⊢ Post` |
| Tính dừng | Triển khai sử dụng vòng lặp có giới hạn | `Q` là một biến thể |
| Tính hợp lưu | Độc lập thứ tự áp dụng quy tắc | Trạng thái `Q = 0` duy nhất |
| Bất biến của `Inv` (mỗi bước tính toán `δi(s : Si)`) | `Asm0, Inv, ΓS ⊢ ∀s : Si · ECond ⇒ [δi(s)]Inv` | `Asm@pre, Inv, ΓS ⊢ ∀s : Si · ECond ⇒ [δi(s)]Inv` |

Trong trường hợp cuối cùng, `ECond` là một điều kiện thực thi (execution condition) biểu thị các hạn chế về thời điểm bước tính toán có thể được thực thi trong triển khai `I` của `τ`, ví dụ, nó có thể biểu thị rằng quan hệ của một ánh xạ đứng trước nào đó là đúng. `Inv` cũng phải đúng ở trạng thái ban đầu, dựa trên `Asm0` và `ΓS` đối với các chuyển đổi mô hình tách biệt, và `Inv[v/v@pre]` phải đúng dựa trên `Asm` và `ΓS` đối với các chuyển đổi cập nhật tại chỗ.

Một cách tiếp cận khác để chứng minh tính hợp lưu là lập luận trực tiếp rằng bất kỳ hai bước chuyển đổi khác nhau nào cũng giao hoán với nhau, tức là `[α; β]P ≡ [β; α]P` cho bất kỳ vị từ `P` nào.

Các kỹ thuật chứng minh này có thể được liên hệ với các phát biểu dựa trên mô hình của các thuộc tính xác minh ở Mục 3 thông qua điều kiện đúng đắn (soundness condition) liên hệ `⊢` và `|=`. Ví dụ, đối với tính đúng đắn cú pháp, nếu việc chứng minh dòng 2 của Bảng 4 cho một chuyển đổi mô hình tách biệt `τ` đúng, và `(m,n0) |= Asm ∪ ΓS`, và `(m,n0) −→τ (m,n)` thì `(m,n) |= Asm0 ∪ Inv ∪ ΓS ∪ Post` theo tính bất biến của `Inv`, tính đúng đắn ngữ nghĩa, và việc bảo toàn dữ liệu của `S`, do đó, theo Bảng 4, `(m,n) |= ΓT` và `n |= ΓT`, như yêu cầu.

Việc chứng minh `Inv` là bất biến được thực hiện bằng lập luận quy nạp rằng mỗi bước tính toán của chuyển đổi bảo toàn `Inv`, nếu được thực thi theo thuật toán triển khai chuyển đổi. Thêm vào đó, `Inv` phải đúng ban đầu. Tương tự, thuộc tính biến thể của `Q` có thể được chứng minh bằng cách xét từng trường hợp trên các bước tính toán.

Do đó, sơ đồ tổng quát của việc xác minh dựa trên chứng minh là:

1. Chứng minh tính bất biến của `Inv`, và (nếu cần) thuộc tính biến thể của `Q`.
2. Sử dụng những điều này để suy ra bảo toàn ngữ nghĩa, đúng đắn cú pháp và đúng đắn ngữ nghĩa.
3. Sử dụng phân tích cú pháp hoặc các thuộc tính của `Q` để chỉ ra tính dừng và tính hợp lưu.

Chúng tôi mô tả các kỹ thuật phân tích cú pháp cho khung làm việc của chúng tôi trong Mục 5, các kỹ thuật phản ví dụ trong Mục 6, các kỹ thuật chứng minh trong Mục 7, và các kỹ thuật đúng-theo-cấu-trúc trong Mục 8.

## 5 Phân tích cú pháp các đặc tả và triển khai chuyển đổi (Syntactic analysis of transformation specifications and implementations)

Phân tích cú pháp sử dụng đặc tả hoặc triển khai của một chuyển đổi, được biểu thị trong các siêu mô hình ở Hình 5 và 7, để xác định một cách tĩnh (statically) các thuộc tính của chuyển đổi, chẳng hạn như các điều kiện xác định giá trị (definedness) và xác định duy nhất (determinacy) của các quy tắc chuyển đổi, và các vấn đề liên quan đến ngữ nghĩa của chúng, chẳng hạn như nhu cầu về một triển khai điểm bất động (fixed-point) trong trường hợp các quy tắc có khả năng vừa ghi vừa đọc cùng các kiểu thực thể hoặc đặc trưng trong một mô hình. Một số giới hạn về hiệu năng cũng có thể được ước tính bằng phân tích cú pháp tĩnh [38].

Phân tích cú pháp có lợi thế là không cần ánh xạ sang một hình thức luận bổ sung nào (như B, Z3, v.v.), do đó không phải phụ thuộc vào tính đúng đắn của ánh xạ đó. Trong mục này chúng tôi sẽ xem xét các chuyển đổi được biểu diễn trong các siêu mô hình ở Hình 5 và 7. Bất kể dạng của một chuyển đổi `τ` (tức là, cho dù nó có phải là một chuyển đổi cập nhật tại chỗ hay không), mỗi ràng buộc ánh xạ của nó cần thỏa mãn các thuộc tính sau đây về *tính xác định giá trị* (definedness) và *tính xác định duy nhất* (determinacy).

Đối với mỗi ràng buộc hậu điều kiện, tiền điều kiện và bất biến của một chuyển đổi, điều kiện xác định giá trị là một giả định cần thiết cần đúng trước khi ràng buộc được áp dụng hoặc lượng giá, để việc lượng giá của nó được xác định rõ ràng (well-defined). Các ràng buộc hậu điều kiện thông thường cũng cần thỏa mãn điều kiện về tính xác định duy nhất.

Các ví dụ về các mệnh đề cho hàm xác định giá trị `def : Exp(L) → Exp(L)` được đưa ra trong Bảng 5.

**Bảng 5. Các điều kiện xác định giá trị (definedness) cho các biểu thức**

| Biểu thức ràng buộc `e` | Điều kiện xác định giá trị `def(e)` |
|---|---|
| `a/b` | `b ≠ 0 and def(a) and def(b)` |
| `s→at(ind)` (dãy hoặc chuỗi `s`) | `ind > 0 and ind ≤ s.size and def(s) and def(ind)` |
| `E[v]` (kiểu thực thể `E` có thuộc tính định danh `id`, `v` đơn trị) | `E.id→includes(v) and def(v)` |
| `s→last(), s→first(), s→max(), s→min(), s→any()` | `s.size > 0 and def(s)` |
| `v.sqrt` | `v ≥ 0 and def(v)` |
| `v.log` | `v > 0 and def(v)` |
| `A and B` | `def(A) and def(B)` |
| `A or B` | `def(A) and def(B)` |
| `A implies B` | `def(A) and (A implies def(B))` |
| `E→exists(x \| A)` | `def(E) and E→forAll(x \| def(A))` |
| `E→forAll(x \| A)` | `def(E) and E→forAll(x \| def(A))` |

Các ví dụ về các mệnh đề cho hàm xác định duy nhất `det : Exp(L) → Exp(L)` được đưa ra trong Bảng 6.

**Bảng 6. Các điều kiện xác định duy nhất (determinacy) cho các biểu thức**

| Biểu thức ràng buộc `e` | Điều kiện xác định duy nhất `det(e)` |
|---|---|
| `s→any()` | `s.size = 1 and det(s)` |
| Phép hội theo trường hợp (case-conjunction): `(E1 implies P1) and ... and (En implies Pn)` | Phép hội của `not(Ei and Ej)` với `i ≠ j`, và mỗi `(det(Ei) and (Ei implies det(Pi)))` |
| `A and B` | `det(A) and det(B)` |
| `A or B` | `false` |
| `A implies B` | `det(A) and (A implies det(B))` |
| `E→exists(x \| A)` | `det(E) and E→forAll(x \| det(A))`, thêm vào đó tính độc lập thứ tự của `A` đối với `x : E` |
| `E→forAll(x \| A)` | `det(E) and E→forAll(x \| det(A))` |

Việc phân tích cú pháp tinh vi hơn cho một ràng buộc hậu điều kiện có thể được thực hiện bằng cách xem xét các mối quan hệ phụ thuộc dữ liệu (data-dependency relationships) giữa các phần tử ngôn ngữ mà nó liên hệ.

*Khung ghi* (write frame) `wr(P)` của một công thức `P ∈ Exp(L)` là tập hợp các đặc trưng và kiểu thực thể (tức là các phạm vi kiểu thực thể) mà nó sửa đổi, khi được diễn giải như một hành động (một hành động `stat(P)` để thiết lập `P`, Mục 8). Điều này bao gồm cả việc tạo đối tượng. *Khung đọc* (read frame) `rd(P)` là tập hợp các kiểu thực thể và đặc trưng được đọc trong `P`. Các khung `wr∗(P)` và `rd∗(P)` cho độ chính xác cao hơn bằng cách ghi lại các tập hợp đối tượng (biểu thức biểu thị các thể hiện của kiểu thực thể) mà đặc trưng của chúng được ghi hoặc đọc trong `P`. Bảng 7 đưa ra một số trường hợp định nghĩa của các khung này.

Khi tính `wr(P)` chúng tôi cũng tính đến các đặc trưng và kiểu thực thể phụ thuộc vào các đặc trưng và kiểu thực thể được cập nhật tường minh của `Cn`, chẳng hạn như các đầu liên kết nghịch đảo (inverse association ends). Nếu có một ràng buộc `φ ∈ ΓL` định nghĩa ngầm định một đặc trưng `g` theo đặc trưng `f`, tức là `f ∈ rd(φ)` và `g ∈ wr(φ)`, thì `g` phụ thuộc vào `f`. Đặc biệt, nếu một đầu liên kết `role2` có một đầu đối diện được đặt tên `role1`, thì `role1` phụ thuộc vào `role2` và ngược lại.

**Bảng 7. Định nghĩa các khung đọc và ghi (read and write frames)**

| `P` | `rd(P)` | `wr(P)` | `rd∗(P)` | `wr∗(P)` |
|---|---|---|---|---|
| Biểu thức cơ bản `e` không có lượng từ, các toán tử logic hoặc `obj.f`, `=`, `:`, `E[]`, `→includes`, `→includesAll`, `→excludesAll`, `→excludes`, `→isDeleted` | Tập hợp các đặc trưng và kiểu thực thể của các đối tượng và tên được dùng trong `P` | `{}` | Tập hợp các cặp `(obj, f)` được dùng trong `P`, cộng thêm các tên kiểu thực thể trong `P` | `{}` |
| `e1 : e2.r` | `rd(e1) ∪ rd(e2)` | `{r}` | `rd∗(e1) ∪ rd∗(e2)` | `{(e2, r)}` |
| `e2.r→includes(e1)` (`r` đa trị, `e1, e2` đơn trị) | `rd(e1) ∪ rd(e2)` | `{r}` | `rd∗(e1) ∪ rd∗(e2)` | `{(e2, r)}` |
| `e2.r→excludes(e1)` (`r` đa trị, `e1, e2` đơn trị) | `rd(e1) ∪ rd(e2)` | `{r}` | `rd∗(e1) ∪ rd∗(e2)` | `{(e2, r)}` |
| `e1.f = e2` (`e1` đơn trị) | `rd(e1) ∪ rd(e2)` | `{f}` | `rd∗(e1) ∪ rd∗(e2)` | `{(e1, f)}` |
| `e2.r→includesAll(e1)` (`r, e1` đa trị, `e2` đơn trị) | `rd(e1) ∪ rd(e2)` | `{r}` | `rd∗(e1) ∪ rd∗(e2)` | `{(e2, r)}` |
| `e2.r→excludesAll(e1)` (`r, e1` đa trị, `e2` đơn trị) | `rd(e1) ∪ rd(e2)` | `{r}` | `rd∗(e1) ∪ rd∗(e2)` | `{(e2, r)}` |
| `E[e1]` | `rd(e1) ∪ {E}` | `{}` | `rd∗(e1) ∪ {E}` | `{}` |
| `E→exists(x \| Q)` (`E` kiểu thực thể cụ thể) | `rd(Q)` | `wr(Q) ∪ {E}` | `rd∗(Q)` | `wr∗(Q) ∪ {E}` |
| `E→exists1(x \| Q)` (`E` kiểu thực thể cụ thể) | `rd(Q)` | `wr(Q) ∪ {E}` | `rd∗(Q)` | `wr∗(Q) ∪ {E}` |
| `E→forAll(x \| Q)` | `rd(Q) ∪ {E}` | `wr(Q)` | `rd∗(Q) ∪ {E}` | `wr∗(Q)` |
| `x→isDeleted()` (`x` đơn trị, kiểu thực thể `E`) | `rd(x)` | `{E}` | `rd∗(x)` | `{E}` |
| `C implies Q` | `rd(C) ∪ rd(Q)` | `wr(Q)` | `rd∗(C) ∪ rd∗(Q)` | `wr∗(Q)` |
| `Q and R` | `rd(Q) ∪ rd(R)` | `wr(Q) ∪ wr(R)` | `rd∗(Q) ∪ rd∗(R)` | `wr∗(Q) ∪ wr∗(R)` |

Việc tạo ra một thể hiện `x` của một kiểu thực thể cụ thể `E` cũng thêm `x` vào mỗi siêu kiểu `F` của `E`, và các siêu kiểu này cũng được bao gồm trong các khung ghi của `E→exists(x | Q)` và `E→exists1(x | Q)` trong bảng trên.

Việc xóa một thể hiện `x` của kiểu thực thể `E` bằng `x→isDeleted()` có thể ảnh hưởng đến bất kỳ siêu kiểu nào của `E` và bất kỳ đầu liên kết nào thuộc sở hữu của `E` hoặc các siêu kiểu của nó, và bất kỳ đầu liên kết nào có liên đới (incident) với `E` hoặc với bất kỳ siêu kiểu nào của `E`. Thêm vào đó, nếu các kiểu thực thể `E` và `F` liên hệ với nhau bởi một liên kết là hợp thành (composition) tại đầu `E`, hoặc bởi một liên kết có số lượng bắt buộc (mandatory multiplicity) tại đầu `E`, tức là một số lượng có cận dưới 1 trở lên, thì việc xóa các thể hiện của `E` sẽ ảnh hưởng tới `F` và các đặc trưng, siêu kiểu cùng các liên kết liên đới của nó, một cách đệ quy.

Khung đọc của một lời gọi thao tác `e.op(pars)` là khung đọc của `e` và của `pars` tương ứng với các tham số đầu vào của `op` cùng với khung đọc của hậu điều kiện `Postop` của `op`, không bao gồm các tham số hình thức `v` của `op`. Khung ghi của nó là khung ghi của các tham số thực tương ứng với các đầu ra của `op`, và `wr(Postop) − v`.

`wr(G)` của một tập hợp ràng buộc `G` là hợp của các khung ghi của các ràng buộc, tương tự đối với `rd(G), wr∗(G), rd∗(G)`.

Một ví dụ của các định nghĩa này là `rd(R) = {A, x}`, `wr(R) = {B, y, br, ar}` cho ràng buộc hậu điều kiện `R` của ví dụ ở Hình 1, và `rd∗(R) = {A, (a, x)}`, `wr∗(R) = {B, (b, y), (a, br), (b, ar)}`.

Sử dụng các định nghĩa về khung đọc và khung ghi, chúng ta có thể thực hiện một số phân tích về các ràng buộc và đặc tả chuyển đổi bằng cách sử dụng phân tích phụ thuộc dữ liệu (data-dependency analysis). Phân tích này được sử dụng để (i) xác định các sai sót khả dĩ trong đặc tả cho người phát triển, và (ii) xác định lựa chọn thiết kế và triển khai các ràng buộc và chuyển đổi cho việc triển khai đúng-theo-cấu-trúc, trong Mục 8.

Một thuộc tính quan trọng của một ràng buộc hậu điều kiện `Cn` là các khung đọc và khung ghi của nó rời nhau: `wr(Cn) ∩ rd(Cn) = {}`. Chúng tôi gọi các ràng buộc như vậy là các ràng buộc *kiểu 1* (type 1). Với một số hạn chế thêm, chúng có một triển khai dưới dạng các phép lặp có giới hạn (bounded iterations) trên các kiểu thực thể mô hình nguồn của chúng. Ràng buộc ví dụ `R` của chúng ta thỏa mãn thuộc tính này, mặc dù bản thân chuyển đổi là một chuyển đổi cập nhật tại chỗ.

Đối với các chuyển đổi `τ : S → T`, trong đó `S` và `T` có thể là cùng một ngôn ngữ, dạng tổng quát của các ràng buộc hậu điều kiện đặc tả chuyển đổi `Cn` mà chúng tôi xem xét là các phép kéo theo:

```
Si→forAll(s | SCond implies Tj→exists(t | TCond and Pred))
```

hoặc

```
Si→forAll(s | SCond implies Succ0)
```

trong đó `SCond` là một vị từ chỉ trên các phần tử ngôn ngữ nguồn `S`, `S1, ..., Sn` là các kiểu thực thể của `S` liên quan tới chuyển đổi, `Tj` là kiểu thực thể nào đó của ngôn ngữ đích `T`, `TCond` là một điều kiện chỉ trên các phần tử `T`, ví dụ, để đặc tả các giá trị tường minh cho các thuộc tính của `t`, và `Pred` tham chiếu tới cả `t` và `s` để đặc tả các thuộc tính của `t` và các đối tượng được liên kết (phụ thuộc) khả dĩ theo thuộc tính và các đối tượng được liên kết của `s`. `TCond` không chứa lượng từ, `Pred` có thể chứa thêm các lượng từ `exists` hoặc `forAll` để đặc tả việc tạo/tra cứu các phần tử phụ thuộc (subordinate) của `t`. Nếu `t` cần là duy nhất cho một `s` cho trước, có thể sử dụng thay thế một lượng từ `exists1` (tồn tại duy nhất) trong vế sau (succedent) của ràng buộc. Trong dạng thứ hai, `Succ0` không có lượng từ `exists`, và không tạo ra các phần tử đích nhưng có thể tra cứu các phần tử đã tạo trước đó và sửa đổi chúng.

Có thể sử dụng thêm các lượng từ `forAll` ở mức ngoài cùng của ràng buộc, nếu cần lượng hóa trên nhiều phần tử mô hình nguồn, thay vì trên các phần tử đơn lẻ. Mỗi kiểu thực thể nguồn `Si` được lượng hóa `forAll` ở mức ngoài cùng được gọi là một *miền nguồn* (source domain) của ràng buộc. Các kiểu thực thể ngôn ngữ đích `Tj` là các *miền đích* (target domains) của ràng buộc.

Một dạng ràng buộc bị hạn chế trong đó không có lượng từ `forAll` nào có thể xuất hiện trong `Pred` hoặc `Succ0` được gọi là ràng buộc dạng *hội-kéo-theo* (conjunctive-implicative form) trong [38], nó có những ưu điểm về khả năng hiểu và khả năng phân tích so với các ràng buộc tổng quát (ví dụ, có thể có các lượng từ xen kẽ lồng nhau trong `Pred`).

Triển khai chuẩn (Mục 8) của một hậu điều kiện kiểu 1 `Cn` là một vòng lặp có giới hạn `for s : Si do δi(s)` lặp một bước tính toán `δi(s : Si)` được định nghĩa là `if SCond then stat(Succ)` trong đó `Succ` là vế sau `Succ0` hoặc `Tj→exists(t | TCond and Pred)` của `Cn`, và `stat` được định nghĩa như trong Bảng 10. Chúng tôi giả định rằng các triển khai quy tắc sử dụng các bước `δi` này được dùng để triển khai `Cn` trong phân tích tiếp theo.

Chúng ta có thể phân loại các ràng buộc hậu điều kiện chuyển đổi `Cn` thành nhiều loại, với độ phức tạp tăng dần:

- **Ràng buộc kiểu 0 (Type 0):** không có lượng hóa trên các phần tử ngôn ngữ nguồn, thay vào đó chỉ các cập nhật cho các đối tượng cụ thể được đặc tả. Ví dụ: `Account["33665"].balance = 0` để đặt số dư của một tài khoản cụ thể đã được định danh. Những ràng buộc này được triển khai trực tiếp bởi một `RuleImplementation` có hành vi là `stat(Cn)`.
- **Ràng buộc kiểu 1 với ánh xạ định danh 1-1** (ràng buộc *bảo toàn cấu trúc* — structure-preserving).
- **Ràng buộc kiểu 1 với việc hợp nhất nhiều thể hiện nguồn thành các thể hiện đích đơn**, tức là với ánh xạ định danh nhiều-1.
- **Ràng buộc kiểu 2 (Type 2):** `wr(Cn) ∩ (rd(Pred) ∪ rd(TCond))` khác rỗng, nhưng `wr(Cn) ∩ (rd(SCond) ∪ {Si}) = {}`. Những ràng buộc này thường cần được triển khai bằng một phép lặp điểm bất động (fixpoint iteration) (thay vì một vòng lặp có giới hạn): bước chuyển đổi cơ bản `δi(s)` triển khai một lần áp dụng `Cn` được lặp lại trên bất kỳ phần tử miền nguồn `s` áp dụng được nào cho tới khi không còn phần tử nguồn áp dụng được nào nữa.
- **Ràng buộc kiểu 3 (Type 3):** những ràng buộc này có `wr(Cn) ∩ (rd(SCond) ∪ {Si}) ≠ {}`. Những ràng buộc này cũng cần được triển khai bằng phép lặp điểm bất động, và mỗi bước chuyển đổi `δi(s)` có thể sửa đổi các tập hợp đối tượng nguồn áp dụng được cho các bước tiếp theo, khiến việc chứng minh tính dừng và tính hợp lưu có khả năng khó khăn hơn so với các ràng buộc kiểu 2.

### 5.1 Phân tích các ràng buộc kiểu 1 (Analysis of type 1 constraints)

Đối với các ràng buộc kiểu 1, nhiều thuộc tính xác minh (chẳng hạn tính hợp lưu, đúng đắn ngữ nghĩa và tính dừng) có thể được thiết lập bằng các kiểm tra cú pháp trên ràng buộc để đảm bảo rằng các lần áp dụng khác nhau của việc triển khai ràng buộc không thể can thiệp lẫn nhau về mặt ngữ nghĩa.

Cho một ràng buộc kiểu 1 `Cn`:

```
Si→forAll(s | SCond implies Tj→exists(t | TCond and Pred))
```

các điều kiện sau (*không can thiệp cú pháp nội tại* — internal syntactic non-interference) đảm bảo rằng các lần áp dụng `δi(s1), δi(s2)` của bước tính toán `δi` của `Cn` trên các `s1, s2 : Si` khác nhau, `s1 ≠ s2`, không thể can thiệp vào hiệu ứng của nhau:

Dữ liệu nguồn duy nhất được đọc trong `Cn` phải là dữ liệu có thể điều hướng (navigable) được từ `s`. Không được có tham chiếu tới bất kỳ thuộc tính định danh nào của `Tj` trong vế sau `Succ` của `Cn`, ngoại trừ trong một phép gán giá trị thuộc tính định danh của `s` cho nó: `t.tid = s.sid`. Các cập nhật trong `TCond` và `Pred` cần cục bộ đối với `t` hoặc `s`: chỉ các đặc trưng trực tiếp của `t` hoặc `s` mới được cập nhật. Các cập nhật `t.f = e`, `e : t.f` hoặc `t.f→includesAll(e)` cho các đặc trưng trực tiếp `f` của `t` được cho phép, thêm vào đó `t` có thể được thêm vào một biểu thức có giá trị tập hợp hoặc dãy `e` không phụ thuộc vào `s` hoặc `t`: `t : e`. Tương tự đối với `s`. Việc xóa hoặc loại bỏ các phần tử khỏi tập hợp là không được phép. Các điều kiện này có thể được tổng quát hóa một chút để cho phép các ánh xạ định danh 1-1 từ `Si` sang `Tj`.

Lưu ý rằng `Si` không bằng `Tj` hoặc bất kỳ tổ tiên (ancestor) nào của `Tj`, và không có đặc trưng nào vừa được đọc vừa được ghi trong `Cn` (theo thuộc tính kiểu 1). Các điều kiện tương tự áp dụng cho các ràng buộc có vế sau dạng `Succ0`.

Các điều kiện này ngăn không cho một lần áp dụng `δi(s1)` của `Cn` làm mất hiệu lực của một lần áp dụng trước đó `δi(s2)`, `s1 ≠ s2`, bởi vì các tập hợp `wr∗` của khung ghi của hai lần áp dụng (tức là, của `SCond implies Succ` cho `s1` và `s2`) rời nhau⁶ ngoại trừ các mục dữ liệu chia sẻ có giá trị tập hợp (chẳng hạn bản thân `Tj`), và những mục này được ghi theo cách nhất quán (cả hai lần áp dụng đều thêm phần tử) bởi các lần áp dụng khác nhau. Các ràng buộc như vậy được gọi là các ràng buộc kiểu 1 *cục bộ hóa* (localised).

Triển khai chuẩn của các ràng buộc kiểu 1 là một phép lặp vòng `for` cố định `for s : Si do δi(s)` của các triển khai quy tắc của chúng trên các miền nguồn (Mục 8). Các điều kiện trên đảm bảo rằng việc thực thi các lần áp dụng `δi(s)` riêng lẻ theo bất kỳ thứ tự tuần tự nào bởi triển khai này sẽ đạt được điều kiện logic yêu cầu `Cn` khi tất cả các lần áp dụng đã hoàn thành. Do đó tính đúng đắn ngữ nghĩa và tính dừng đúng cho triển khai chuẩn của các ràng buộc kiểu 1 cục bộ hóa.

Đối với tính hợp lưu của triển khai này, chúng ta cần thêm các điều kiện rằng `Cn` là xác định duy nhất, tức là `det(Cn)` là đúng, và việc thêm phần tử vào bất kỳ dãy nào là không được phép.

**Định lý 1.** Nếu một ràng buộc kiểu 1 `Cn` bị hạn chế về cú pháp như mô tả ở trên, thì triển khai chuẩn của nó là hợp lưu.

**Chứng minh.** Theo tính xác định duy nhất, mỗi lần áp dụng riêng lẻ `δi(s)` của `Cn` có một kết quả duy nhất (sai khác đẳng cấu) từ một trạng thái bắt đầu cụ thể. Hai lần áp dụng `δi(s1)` và `δi(s2)` của `Cn` cho các `s1, s2` khác nhau trong `Si` có các khung `wr∗` rời nhau, ngoại trừ các mục dữ liệu chia sẻ có giá trị tập hợp (chẳng hạn bản thân `Tj`), bởi vì chúng dựa trên các đối tượng `Tj` khác nhau `t1` và `t2` hoặc trên các `s1` và `s2` khác nhau. Do đó hiệu ứng của `δi(s1)` và `δi(s2)` độc lập với nhau trên các khung ghi này. Nếu một biểu thức có giá trị tập hợp `e` được ghi trong `Pred` bởi một công thức `t : e` hoặc `e→includes(t)`, thì đặc trưng được ghi (ngoài cùng) của `e` không được đọc trong `Cn`, nên giá trị của nó không thể ảnh hưởng tới các lần áp dụng của `Cn`. Thứ tự thêm `t1` và `t2` vào `e` không tạo ra khác biệt nào cho giá trị kết quả của nó, do đó các cập nhật như vậy độc lập với thứ tự. Tương tự với việc thêm `s1` hoặc `s2` vào một tập hợp. □

Ví dụ về ràng buộc hậu điều kiện `R` minh họa trường hợp này: các khung `wr∗` rời nhau đối với các lần thực thi bước tính toán của `R` cho các `a1, a2 : A` khác nhau, ngoại trừ tập hợp chỉ-thêm (add-only) được chia sẻ `B`.

Có thể dễ dàng xây dựng các phản ví dụ cho tính hợp lưu khi các điều kiện trên không được thỏa mãn. Nếu các phần tử của `Si` được đơn giản thêm vào một dãy toàn cục:

```
Si→forAll(s | s : Root.instance.slist)
```

cho một kiểu thực thể đơn nhất (singleton) `Root`, với một đầu liên kết có thứ tự `slist : seq(Si)`, thì hai lần thực thi khác nhau của chuyển đổi có thể tạo ra hai thứ tự khác nhau của `slist`. Đây là một ràng buộc kiểu 1 cục bộ hóa, và triển khai vòng `for` chuẩn là đúng đắn về ngữ nghĩa, nhưng không hợp lưu.

Tương tự, nếu ánh xạ các giá trị thuộc tính định danh không phải 1-1, thì cùng một thể hiện `Tj` có thể bị cập nhật bởi các giá trị suy ra từ hai đối tượng nguồn khác nhau, và chỉ có bản cập nhật thứ hai được giữ lại:

```
S1→forAll(s | T1→exists(t | t.id = s.id/2 and t.y = s.x))
```

*(⁶ Mặc dù `(t, f)` cho các đặc trưng `f` của `Tj` có thể xuất hiện trong cả hai khung `wr∗`, `t` biểu thị các đối tượng khác nhau `t1, t2` cho hai lần áp dụng, vì điều kiện trên `tid` và `sid`.)*

trong đó tất cả các thuộc tính có giá trị nguyên. Trong ví dụ này, một đối tượng `T1` `t1` có thể được tạo cho `s1 : S1` với `s1.id = t1.id = 0`, nhưng sau đó lại được *chọn* (vì nguyên tắc 'kiểm tra trước khi thực thi' — check before enforce, Mục 8) làm đối tượng đích khớp với `s2` với `s2.id = 1`. Chỉ có giá trị của `s2.x` được ghi lại trong `t1.y` khi kết thúc.

Ràng buộc này không cục bộ hóa, và là một phản ví dụ cho tính đúng đắn ngữ nghĩa của triển khai chuẩn (vòng lặp có giới hạn) của các ràng buộc kiểu 1: các tính toán hoàn chỉnh của triển khai này không thể thỏa mãn ràng buộc nếu các phần tử `Si` có cùng giá trị `s.id/2` nhưng có giá trị `s.x` khác nhau. Có thể dùng một phép lặp điểm bất động thay thế, nhưng khi đó tính dừng không thể chứng minh được trong những trường hợp như vậy.

Việc gán giá trị cho các đặc trưng của các đối tượng khác ngoài `t` và `s` có thể vi phạm tính hợp lưu và đúng đắn ngữ nghĩa theo cách tương tự, ví dụ:

```
S1→forAll(s | T1→exists(t | t.r = T0["1"] and t.r.att = s.x))
```

Ràng buộc kiểu 1 này không cục bộ hóa, vì `(T0["1"], att)` nằm trong khung `wr∗` của các lần áp dụng khác nhau, và `att` không được sửa đổi bằng cách thêm phần tử, mà bằng phép gán. Một lần nữa, nói chung không có triển khai đúng đắn về ngữ nghĩa nào cho ràng buộc này, và trong thực tế các ràng buộc kiểu 1 không cục bộ hóa nên tránh dùng trong các hậu điều kiện chuyển đổi.

Các kết quả trên áp dụng trực tiếp cho các ràng buộc dạng hội-kéo-theo, nơi các thuộc tính cục bộ của ràng buộc có thể được kiểm tra dễ dàng. Ví dụ, nếu các kiểu thực thể nguồn `S1` và `S2` được ánh xạ tới các kiểu thực thể đích tương ứng `T1` và `T2`, trong đó có các liên kết một-nhiều `r1 : S1 → Set(S2)` và `r2 : T1 → Set(T2)` và các thuộc tính `name : String` duy nhất của mỗi kiểu thực thể:

```
S2→forAll(s | T2→exists(t | t.name = s.name))
S1→forAll(s | T1→exists(t | t.name = s.name and t.r2 = T2[s.r1.name]))
```

Trong ràng buộc thứ hai, biểu thức `T2[s.r1.name]` trả về tất cả các thể hiện `T2` hiện có với một giá trị `name` nằm trong `s.r1.name`. Với điều kiện tất cả các lần áp dụng bước tính toán của ràng buộc thứ nhất được hoàn thành trước khi bất kỳ lần áp dụng nào của bước tính toán của ràng buộc thứ hai được thử, đây là một chuyển đổi đúng đắn về ngữ nghĩa, và triển khai chuẩn của mỗi ràng buộc là hợp lưu, dừng và đúng đắn về ngữ nghĩa theo Định lý 1.

Tuy nhiên, một phong cách đặc tả chuyển đổi thông thường hơn là dạng 'đi xuống theo đệ quy' (recursive descent), trong đó các phần phụ thuộc của một phần tử mô hình nguồn được chuyển đổi cùng với phần tử đó (ví dụ, việc sử dụng mệnh đề `where` trong QVT-R, hoặc ví dụ ở Mục 10). Đối với ví dụ này, phong cách này sẽ dẫn đến một đặc tả có dạng:

```
S1→forAll(s | T1→exists(t | t.name = s.name and 
  s.r1→forAll(s2 | T2→exists(t2 | t2.name = s2.name and t2 : t.r2))))
```

Dạng thay thế này cũng thỏa mãn điều kiện các khung `wr∗` rời nhau, mặc dù có các cập nhật gán không cục bộ (ví dụ, tới `t2.name`), vì do các số lượng liên kết, không thể có hai `t, t′` khác nhau cùng chứa cùng một thể hiện `t2` trong các tập hợp `r2` của chúng, do đó các lần áp dụng của việc triển khai quy tắc duy nhất trên cho các `s, s′` khác nhau sẽ cập nhật các phần rời nhau của mô hình đích và sẽ không can thiệp lẫn nhau. Chúng tôi khuyến nghị rằng những đặc tả như vậy nên được viết lại thành dạng hội-kéo-theo để cải thiện khả năng hiểu và khả năng xác minh của đặc tả. Hiệu năng của việc triển khai cũng có thể cao hơn [38].

Một phân tích tương tự có thể xác định các điều kiện đủ cho tính hợp lưu, tính dừng và tính đúng đắn ngữ nghĩa của các ràng buộc hợp nhất kiểu thực thể và thể hiện kiểu 1 [39].

Các ràng buộc kiểu 1 không thỏa mãn các hạn chế không can thiệp nội tại có thể được phân tích bằng các kỹ thuật dành cho các ràng buộc kiểu 2 và 3 trong các mục tiếp theo.

Việc phân tích tính đúng đắn cú pháp và bảo toàn ngữ nghĩa cho các ràng buộc kiểu 1 có thể đạt được bằng chứng minh nhất quán nội tại trong B (Mục 7). Với mục đích này, việc phát biểu một bất biến `Inv` cho ràng buộc là hữu ích. Thông thường ràng buộc nghịch đảo `Cn∼: Tj→forAll(t | TCond implies Si→exists(s | SCond and Pred))` của một `Cn` dạng hội-kéo-theo sẽ là một bất biến cho các tính toán của `stat(Cn)`, giả sử mô hình đích ban đầu rỗng.

### 5.2 Phân tích các ràng buộc kiểu 2 và kiểu 3 (Analysis of type 2 and type 3 constraints)

Một ràng buộc `Cn` có dạng `Si→forAll(s | SCond implies Tj→exists(t | TCond and Pred))` được gọi là ràng buộc *kiểu 2* nếu `wr(Cn) ∩ (rd(Pred) ∪ rd(TCond))` khác rỗng, nhưng `wr(Cn) ∩ (rd(SCond) ∪ {Si}) = {}`. Điều này có nghĩa là thứ tự áp dụng các bước tính toán `δi(s : Si)` của ràng buộc cho các thể hiện `s : Si` có thể có ý nghĩa quan trọng, và một lần lặp duy nhất qua tập hợp ban đầu các phần tử `Si` trong mô hình nguồn có thể không đủ để thiết lập `Cn`. Thay vào đó có thể cần một phép tính điểm bất động, với các lần lặp của `δi` được lặp lại cho đến khi `Cn` được thiết lập.

Một ràng buộc thuộc *kiểu 3* nếu `Si ∈ wr(Cn)` hoặc `wr(Cn) ∩ rd(SCond) ≠ {}`. Một lần nữa trong trường hợp này cần một phép tính điểm bất động, với độ phức tạp thêm vì tập hợp các đối tượng nguồn đang được ràng buộc xem xét bản thân nó cũng đang thay đổi động.

Một hàm biến thể `Q : S × T → N` trên dữ liệu mô hình nguồn và đích có thể được dùng để thiết lập tính dừng, tính hợp lưu và tính đúng đắn của các ràng buộc kiểu 2 và kiểu 3, và nên được định nghĩa cùng với ràng buộc. `Q` nên có thuộc tính là nó giảm sau mỗi bước tính toán `δi` của ràng buộc, và `Q = 0` khi ràng buộc được thiết lập.

Về mặt hình thức, `Q` là một *hàm biến thể* cho `Cn` nếu:

```
∀ν : N · Q(smodel, tmodel) = ν ∧ s ∈ Si ∧ SCond ∧ ¬(Succ) ∧ ν > 0 ⇒ [stat(Succ)](Q(smodel, tmodel) < ν)
```

và

```
Q(smodel, tmodel) = 0 ≡ {s ∈ Si | SCond ∧ ¬(Succ)} = {}
```

`Succ` viết tắt cho vế phải của ràng buộc `Tj→exists(t | TCond and Pred)`, `smodel` là các biểu thức trong dữ liệu mô hình nguồn, `tmodel` là các biểu thức trong dữ liệu mô hình đích. Việc chứng minh thuộc tính biến thể có thể giả định rằng các bất biến `ΓS` và `Inv` của chuyển đổi đúng. `Q` sẽ được định nghĩa về mặt cú pháp như một biểu thức trong ngôn ngữ hợp `S ∪ T`. Ví dụ, một triển khai điểm bất động của ràng buộc `R` sẽ có một biến thể:

```
A→select(a | not(B→exists(b | b.y = a.x * a.x and b : a.br)))→size()
```

tức là, trong ký hiệu toán học: `card({a ∈ A | ¬(∃b : B · y(b) = x(a) * x(a) ∧ b ∈ br(a))})`. Đại lượng này giảm dần từ `card(A)` tại thời điểm bắt đầu chuyển đổi xuống 0 khi kết thúc.

Triển khai điểm bất động tổng quát của `Cn` có dạng:

```
while not(Cn) do δi(Si→select(s | SCond and not(Succ))→any()) variant Q
```

Thuộc tính hàm biến thể của `Q` thiết lập tính dừng của triển khai điểm bất động của `Cn`: mỗi lần áp dụng `δi` làm giảm nghiêm ngặt `Q`, và `Q ≥ 0`, do đó chỉ có thể có hữu hạn lần áp dụng như vậy. Tính đúng đắn ngữ nghĩa cũng theo đó mà có, vì khi `Q = 0`, không còn thể hiện nào của `Si` vi phạm ràng buộc, tức là `Cn` đúng.

Tính hợp lưu đòi hỏi trạng thái `Q = 0` là duy nhất:

**Định lý 2.** Nếu đối với mỗi trạng thái bắt đầu cụ thể của các mô hình nguồn và đích, có một trạng thái cuối khả dĩ duy nhất (sai khác đẳng cấu) của các mô hình (được sinh ra bằng cách áp dụng bước tính toán ràng buộc `δi` cho các thể hiện của `Si` cho đến khi các điều kiện áp dụng `SCond and not(Succ)` không còn đúng cho bất kỳ `s ∈ Si` nào) trong đó `Q = 0`, thì triển khai điểm bất động của ràng buộc kiểu 2 hoặc kiểu 3 là hợp lưu.

**Chứng minh.** Các trạng thái cuối của chuyển đổi được đặc trưng bởi điều kiện `{s ∈ Si | SCond ∧ ¬(Succ)} = {}`. Nhưng trong các trạng thái như vậy chúng ta cũng có `Q(smodel, tmodel) = 0`. Do đó, có một trạng thái kết thúc duy nhất. □

Việc xác minh thuộc tính hàm biến thể và tính duy nhất của trạng thái `0` của `Q` đòi hỏi chứng minh, ví dụ, bằng chứng minh tinh chỉnh (refinement proof) trong B; tính đúng đắn cú pháp và bảo toàn ngữ nghĩa cũng đòi hỏi chứng minh (Mục 7).

Các mẫu tối ưu hóa 'Thay đệ quy bằng phép lặp' (Replace recursion by iteration) và 'Bỏ qua điều kiện áp dụng phủ định' (Omit negative application conditions) cũng có thể hỗ trợ việc xác minh các ràng buộc kiểu 2 và kiểu 3 `Cn` [38]. Trong trường hợp đầu, phép lặp có giới hạn có thể được dùng thay cho phép lặp điểm bất động, nếu mỗi bước chuyển đổi của `Cn` làm giảm nghiêm ngặt tập hợp các phần tử mô hình có thể khớp với điều kiện áp dụng của `Cn`. Do đó tính dừng đúng trực tiếp, và tính đúng đắn ngữ nghĩa đúng nếu các bước không can thiệp lẫn nhau (cục bộ hóa). Trong trường hợp thứ hai, phép lặp điểm bất động có thể được đơn giản hóa bằng cách loại bỏ việc kiểm tra `not(Succ)`, nếu `SCond` không nhất quán với `Succ`. Tính đúng đắn ngữ nghĩa đúng trực tiếp cho các triển khai như vậy. Một ví dụ về điều này là nghiên cứu tình huống ở Mục 11.

## 6 Phân tích phản ví dụ các đặc tả chuyển đổi (Counter-example analysis of transformation specifications)

Cùng với phân tích cú pháp, việc kiểm tra mô hình (model-checking) hoặc kiểm tra thỏa mãn (satisfaction-checking) các đặc tả chuyển đổi có thể xác định các lỗi trong đặc tả trước khi các dạng phân tích chứng minh tốn nhiều tài nguyên hơn được thử.

Đặc biệt, trong trường hợp một chuyển đổi mô hình tách biệt `τ : S → T`, một lý thuyết `Γτ` hình thức hóa các tiên đề của `ΓS ∪ Asm0 ∪ Inv ∪ Post` trong ngôn ngữ logic hợp `LS∪T` của `S` và `T` biểu thị các điều kiện cần đúng khi chuyển đổi kết thúc. Lý thuyết này cần khả thỏa (satisfiable), nếu không chuyển đổi là bất khả thi. Thêm vào đó, mỗi tiên đề `φ ∈ ΓT` của `T` cần nhất quán với `Γτ`. Các phản ví dụ sẽ xác định các trường hợp tường minh mà tại đó chuyển đổi có thể thất bại trong việc thiết lập `ΓT`, và do đó xác định các lỗi cụ thể trong đặc tả chuyển đổi.

Một số hình thức luận và công cụ có thể được dùng để hỗ trợ phân tích như vậy, ở đây chúng tôi sẽ dùng bộ kiểm tra Z3 SMT [51] cho logic bậc nhất. Điều này còn có thêm một công dụng như một bộ chứng minh định lý: nếu `Γτ ∪ {¬φ}` không khả thỏa, thì `φ` được suy ra từ `Γτ`, do đó tính đúng đắn cú pháp (và tương tự bảo toàn ngữ nghĩa) có thể được chứng minh, về nguyên tắc, sử dụng Z3.

Đối với một chuyển đổi cập nhật tại chỗ `τ : S → S`, `Γτ` hình thức hóa `ΓS ∪ Asm@pre ∪ Inv ∪ Post`, với các tên dữ liệu trạng thái trước `g@pre` được biểu diễn bởi các hằng số mới `g_pre`.

Bảng 8 cho thấy các ví dụ về ánh xạ các biểu thức OCL sang Z3. Bước quan trọng nhất trong phép biên dịch (translation) này là việc biểu thị các lượng từ tồn tại (existential quantifiers) bằng các hàm skolem: trong một công thức `E→forAll(x | Cond implies F→exists(y | Pred))`, lượng từ tồn tại được thay thế bằng một hàm mới `fnew : E → F` không xuất hiện ở bất kỳ phần nào khác của lý thuyết OCL hay Z3, và công thức khi đó được biên dịch thành: `(forall ((x E)) (⇒ Cond′ Pred′[fnew(x)/y]))`.

> **Giải thích:** "Hàm Skolem" (skolemization) là một kỹ thuật kinh điển trong logic bậc nhất để loại bỏ lượng từ tồn tại (`∃`, "tồn tại") bằng cách thay nó bằng một hàm cụ thể phụ thuộc vào các biến lượng từ toàn thể (`∀`) bao quanh nó. Ví dụ câu "với mọi x, tồn tại y sao cho..." được biến đổi thành "với mọi x, gọi y = f(x) là..." — nhờ đó bộ giải SMT như Z3 (một công cụ kiểm tra tính khả thỏa của công thức logic, dùng để tìm phản ví dụ hoặc chứng minh tự động) có thể xử lý công thức hiệu quả hơn.

**Bảng 8. Ánh xạ UML và OCL sang Z3**

| Biểu thức/toán tử OCL `e` | Biểu thức/toán tử Z3 `e′` |
|---|---|
| `Integer` | `Int` |
| `Boolean` | `Bool` |
| `Real` | `Real` |
| Kiểu thực thể `E` | `Sort E` |
| Thuộc tính `att : Typ` thuộc sở hữu của `E` | hàm `att : E → Typ′` |
| Vai trò đơn trị `r` tới `F` thuộc sở hữu của `E` | hàm `r : E → F` |
| Vai trò có giá trị tập hợp `r` tới `F` thuộc sở hữu của `E` | hàm `r : E → List(F)` |
| `implies` | `⇒` |
| `forAll` | `forall` |
| `exists` | Biểu thị bằng phép skolem hóa |
| `first`, `head`, `prepend`, `insert`, `includes` | `memberE` (cho mỗi kiểu thực thể `E`) |
| `Set{}` | `nil` |
| `Set{x1, ..., xn}` | `(insert x1' (... (insert xn' nil) ...))` |

Nói chung, một lượng từ `exists` trong phạm vi của nhiều lượng từ `forAll` được thay thế bằng một hàm mới phụ thuộc vào tất cả các kiểu được lượng hóa `forAll`. Các tập hợp và dãy đều được mô hình hóa dưới dạng danh sách (lists) Z3. Các toán tử cho `select` và `collect` của OCL không được tích hợp sẵn (in-built) trong Z3 và cần được định nghĩa bằng các hàm phụ trợ. Thêm vào đó, các toán tử để kiểm tra thành viên trong một danh sách và để lấy một phần tử danh sách theo chỉ số của nó cần được thêm vào như các hàm phụ trợ. Một cách thay thế cho việc dùng danh sách để mô hình hóa các tập hợp OCL là sử dụng bitset [47], tuy nhiên điều này liên quan đến một mã hóa rất phức tạp và đòi hỏi phải đặt các giới hạn kích thước cho các phạm vi kiểu thực thể và kích thước tập hợp.

Đối với các chuyển đổi mô hình tách biệt, hoặc các chuyển đổi cập nhật tại chỗ trong đó các tập hợp kiểu thực thể và đặc trưng được đọc và được cập nhật rời nhau, ánh xạ từ siêu mô hình ở Hình 5 sang một siêu mô hình cho Z3 thực hiện các phép biên dịch sau:

- Mỗi ngôn ngữ nguồn và đích `L` (hoặc phần ngôn ngữ) được biểu diễn bằng các sort `E` cho mỗi kiểu thực thể `E` của ngôn ngữ, và các ánh xạ dạng `f : E → Typ` cho mỗi đặc trưng thuộc sở hữu `f` của `E`, cùng với các mã hóa Z3 của các ràng buộc của `ΓL` cho các ngôn ngữ nguồn `L`.
- Các giả định `Asm0` trên dữ liệu không bị sửa đổi được mã hóa và bao gồm.
- Mỗi ánh xạ `rule.relation` có dạng `E→forAll(x | SCond implies F→exists(y | PCond))` được mã hóa thành một hàm `taurule : E → F` và một vị từ `∀x : E · SCond′ ⇒ PCond′[taurule(x)/y]`.
- Bất biến biểu thị nghịch đảo của `rule` được mã hóa bởi một hàm `sigmarule : F → E` và một vị từ `∀y : F · SCond′[sigmarule(y)/x] and PCond′[sigmarule(y)/x]`.

Đối với các mục dữ liệu `g` vừa được đọc vừa được cập nhật, trong các chuyển đổi cập nhật tại chỗ, cả giá trị trạng thái trước `g_pre` và giá trị trạng thái sau `g` đều được biểu diễn, và các vị từ trạng thái trước của `Asm@pre` được bao gồm.

Đối với các chuyển đổi mô hình tách biệt, tính nhất quán của lý thuyết kết quả `Γτ` với các ràng buộc riêng lẻ `φ ∈ ΓT` có thể được kiểm tra bằng cách thêm `φ′` vào lý thuyết, các phản ví dụ có thể được tìm kiếm bằng cách thay vào đó thêm `¬φ′`.

Tính đúng đắn cú pháp có thể được chỉ ra bằng cách thêm phủ định của `∧ΓT` cho ngôn ngữ đích `T`, và thiết lập rằng lý thuyết kết quả là không khả thỏa. Bảo toàn ngữ nghĩa của `φ` khi đó có thể được chỉ ra bằng cách thêm `ΓT`, `φ` và phủ định của `χ(φ)` và chỉ ra tính không khả thỏa. Không giống FOL hay B, Z3 không chứa các kỹ thuật chứng minh cho quy nạp không giới hạn (unbounded induction), do đó có thể thất bại trong việc thiết lập các suy luận đúng mà lẽ ra có thể chứng minh được trong FOL hoặc B. Thêm vào đó nó chỉ cung cấp các thủ tục quyết định (decision procedures) cho một số tập con khả quyết (decidable subsets) của logic bậc nhất. Do đó có thể có những tình huống mà Z3 không thể chứng tỏ phản ví dụ cho một lý thuyết, cũng không thể thiết lập tính hợp lệ của nó, và trong những trường hợp này việc phân tích bằng chứng minh trong B hoặc một bộ chứng minh định lý khác sẽ là cần thiết.

Việc ánh xạ từ UML và OCL sang Z3 đã được tự động hóa trong các công cụ UML-RSDS [49]. Giống như trong lý thuyết tập hợp bậc nhất, Z3 không có khái niệm về giá trị chưa xác định (undefined), khác với trong OCL chuẩn. Phép chia trong Z3 là một hàm toàn phần (total function), nhưng giá trị của nó không được xác định cho phép chia cho 0. Người viết đặc tả chuyển đổi nên đảm bảo rằng mọi biểu thức trong một bất biến, giả định hay quan hệ quy tắc chuyển đổi `Cn` có một giá trị xác định, tức là `def(Cn)` đúng, bất cứ khi nào vị từ có thể được lượng giá. Khi lập luận về các chuyển đổi sử dụng Z3, các kết quả chỉ có ý nghĩa đối với các triển khai chuyển đổi thỏa mãn điều kiện này, tức là không có phép lượng giá biểu thức nào cho ra `invalid` của OCL.

Không có biểu diễn Z3 tích hợp sẵn cho chuỗi (strings): những thứ này có thể được mô hình hóa như một sort chưa xác định hoặc như các danh sách số nguyên. Không có biểu diễn trực tiếp cho quan hệ kiểu con (subtyping).

Một ví dụ về việc ánh xạ OCL sang Z3 là ví dụ chuyển đổi của chúng ta ở Hình 1. Lý thuyết Z3 tương ứng là:

```
(declare-sort A)
(declare-sort B)
(declare-fun x (A) Int)
(declare-fun y (B) Int)
(declare-fun br (A) (List B))
(declare-fun ar (B) (List A))
(assert (forall ((a A)) (> (x a) 0)))
(assert (forall ((a A)) (forall ((b B)) (= (memberB b (br a)) (memberA a (ar b))))))
```

Điều này biểu thị lý thuyết của sơ đồ lớp. Đối với hậu điều kiện chuyển đổi, một hàm skolem mới được đưa vào, và một tiên đề cho hậu điều kiện đã skolem hóa:

```
(declare-fun tau1 (A) B)
(assert (forall ((a A))
  (and (= (y (tau1 a)) (* (x a) (x a))) (memberB (tau1 a) (br a)))))
```

Lưu ý rằng điều này không nằm trong một tập con khả quyết của logic bậc nhất, vì nó liên quan đến số học phi tuyến (non-linear arithmetic).

Bất biến được biểu thị bởi:

```
(declare-fun sigma1 (B) A)
(assert (forall ((b B))
  (and (= (y b) (* (x (sigma1 b)) (x (sigma1 b)))) (memberB b (br (sigma1 b))))))
```

Lý thuyết kết hợp này biểu thị trạng thái khi kết thúc của chuyển đổi, và cũng định nghĩa chính xác cách trạng thái cuối của hệ thống nên liên hệ với trạng thái bắt đầu, bằng cách liên hệ các kiểu thực thể và đặc trưng đã sửa đổi `{B, br, ar, y}` với các giá trị không đổi của `{A, x}`.

Phân tích tính nhất quán cho thấy lý thuyết kết hợp này thực sự nhất quán. Nếu chúng ta thêm ràng buộc bổ sung `(not (forall ((b B)) (> (y b) 2)))`, một phản ví dụ cho `B→forAll(b | b.y > 2)` được tìm thấy, trong đó `b` được suy ra từ `a1 : A` với `a1.x = 1`.

Đối với một ngôn ngữ `L`, tính đúng đắn của các suy diễn về `L` trong Z3 đúng, tương đối theo lý thuyết chứng minh FOL của `LL`, và sử dụng ánh xạ trên: Z3 biểu diễn đúng các kiểu dữ liệu toán học Integer, Real của OCL, và Boolean, và tương tự cho các toán tử trên những kiểu này, và cho những tập hợp và toán tử tập hợp OCL có thể được biểu thị trong Z3. Nếu Z3 có thể biểu diễn tất cả các kiểu thực thể và kiểu dữ liệu, đặc trưng và ràng buộc của `L`, trong một lý thuyết Z3 `L′`, thì việc suy diễn (bản dịch `φ′` của) một câu `φ ∈ Sen(L)` trong Z3 từ `L′` kéo theo rằng `φ` có thể suy ra được trong `LL`:

```
⊢Z3,L′ φ′ ⇒ ⊢LL φ
```

Chiều ngược lại không đúng, vì Z3 không đầy đủ (incomplete), ngay cả đối với các tập con khả quyết của lý thuyết tập hợp bậc nhất.

Với điều kiện các ràng buộc của một chuyển đổi `τ` nằm trong một tập con khả quyết của logic bậc nhất, chúng ta có thể đảm bảo rằng đặc tả chuyển đổi của `τ` ở dạng khả quyết nếu chúng ta giới hạn nó vào tập con logic bậc nhất *các sort phân tầng* (stratified sorts). Điều này có nghĩa là các kiểu thực thể được dùng trong chuyển đổi có thể được gán các thứ hạng (rankings) trong `N` sao cho với mỗi liên kết `r` được dùng trong đặc tả chuyển đổi, kiểu thực thể đích của nó có thứ hạng thấp hơn nghiêm ngặt so với kiểu thực thể nguồn của nó. Tuy nhiên một hạn chế như vậy loại trừ các chuyển đổi sử dụng các tự-liên kết (self-associations) và liên kết hai chiều: chỉ các điều hướng đi xuống theo các cây phân cấp hợp thành nghiêm ngặt (strict composition hierarchies) trong các mô hình nguồn và đích mới được cho phép.

## 7 Xác minh dựa trên chứng minh (Proof-based verification)

Các kỹ thuật dựa trên chứng minh để xác minh các thuộc tính đúng đắn của chuyển đổi có hai ưu điểm chính: (i) chúng có thể chứng minh các thuộc tính cho tất cả các trường hợp của một chuyển đổi, tức là, cho các mô hình đầu vào tùy ý và cho một loạt các triển khai khác nhau; (ii) một bản ghi (record) của chứng minh có thể được tạo ra, và chịu sự kiểm tra thêm, nếu cần chứng nhận (certification). Tuy nhiên, các kỹ thuật chứng minh luôn luôn đòi hỏi chuyên môn và tài nguyên con người đáng kể, do bản chất tương tác của các dạng kỹ thuật chứng minh tổng quát nhất, và sự cần thiết phải làm việc cả trong ký hiệu của công cụ chứng minh lẫn trong ký hiệu chuyển đổi.

Chúng tôi đã chọn B AMN làm một hình thức luận phù hợp cho việc xác minh dựa trên chứng minh, B là một hình thức luận trưởng thành, với sự hỗ trợ công cụ tốt, tự động hóa phần lớn các nghĩa vụ chứng minh (proof obligations) đơn giản. Bảng 9 đưa ra một so sánh giữa B với các công cụ xác minh khác. Chúng tôi cung cấp một ánh xạ tự động từ các đặc tả chuyển đổi sang B [49], và ánh xạ này được thiết kế để tạo thuận lợi cho việc hiểu các nghĩa vụ chứng minh B AMN theo thuật ngữ của chuyển đổi đang được xác minh.

Các kiểu thực thể và đặc trưng của các ngôn ngữ tham gia vào một chuyển đổi `τ` được ánh xạ vào B theo Bảng 1. Các biểu thức OCL được ánh xạ một cách có hệ thống vào các biểu thức lý thuyết tập hợp, các Bảng 2 và 3 minh họa ánh xạ này.

Một đặc tả B AMN bao gồm một tập hợp các mô-đun được liên kết, gọi là *máy* (machines). Mỗi máy đóng gói dữ liệu và các thao tác trên dữ liệu đó. Mỗi chuyển đổi được biểu diễn trong một máy B chính duy nhất, cùng với một máy phụ trợ `SystemTypes` chứa các định nghĩa kiểu.

Ánh xạ từ siêu mô hình ở Hình 5 sang một siêu mô hình cho B thực hiện các phép biên dịch sau:

- Mỗi ngôn ngữ nguồn và đích `L` được biểu diễn bằng các tập hợp `es` cho mỗi kiểu thực thể `E` của ngôn ngữ, với `es ⊆ objects`, và các ánh xạ `f : es → Typ` cho mỗi đặc trưng `f` của `E`, cùng với các mã hóa B của các ràng buộc của `ΓL` cho `L` không sửa đổi. Trong các trường hợp một kiểu thực thể hay đặc trưng ngôn ngữ `g` vừa được đọc vừa được ghi bởi chuyển đổi, một bản sao khác biệt về cú pháp `g_pre` được dùng để biểu diễn giá trị ban đầu của `g` lúc bắt đầu chuyển đổi. Một siêu kiểu `F` của kiểu thực thể `E` có bất biến B `es ⊆ fs`. Các kiểu thực thể trừu tượng `E` có bất biến B `es = f1s ∪ ... ∪ fls` trong đó `Fi` là các kiểu con trực tiếp của `E`. Đối với mỗi kiểu thực thể cụ thể `E` của một ngôn ngữ nguồn, có một thao tác `createE` tạo một thể hiện mới của `E` và thêm nó vào `es`. Đối với mỗi đặc trưng dữ liệu `f` của một kiểu thực thể `E` có một thao tác `setf(ex, fx)` đặt `f(ex)` thành `fx`.
- Các giả định `Asm` của chuyển đổi có thể được bao gồm trong bất biến máy (dùng `g_pre` thay cho `g` cho dữ liệu bị ghi bởi chuyển đổi). `Asm` cũng được bao gồm trong các tiền điều kiện của các thao tác ngôn ngữ nguồn `createE` và `setf`.
- Mỗi ánh xạ `rule` được mã hóa như một thao tác với các tham số đầu vào là tên của các đầu không thể sửa đổi của `rule`, và hiệu ứng của nó được suy ra từ `rule.relation` hoặc từ `behavior` của một triển khai của `rule`. Thao tác này biểu diễn các bước tính toán chuyển đổi `δi` của việc triển khai `rule`.
- Các thứ tự của các bước cho các triển khai cụ thể có thể được mã hóa bằng các tiền điều kiện của các thao tác, biểu thị rằng `rule′.relation` cho một hoặc nhiều ánh xạ `rule′` khác đã được thiết lập cho tất cả các phần tử áp dụng được.
- Các vị từ bất biến `Inv` được thêm vào như các bất biến B, dùng `g_pre` để biểu thị các giá trị trạng thái trước `g@pre`.

Khác với ánh xạ sang Z3 được mô tả trong Mục 6, ánh xạ này biểu diễn tường minh các bước tính toán của chuyển đổi, và do đó có thể hỗ trợ việc xác minh rằng những bước này duy trì `Inv` và làm giảm bất kỳ biến thể `Q` nào. Đối với một chuyển đổi mô hình tách biệt `τ : S → T`, bất biến máy biểu thị `ΓS ∪ Asm0 ∪ Inv`. Đối với một chuyển đổi cập nhật tại chỗ `τ : S → S`, bất biến biểu thị `ΓS ∪ Asm@pre ∪ Inv`. Máy biểu diễn chuyển đổi tại bất kỳ trạng thái nào trong quá trình tính toán của nó.

Ánh xạ này phù hợp để hỗ trợ chứng minh tính đúng đắn cú pháp, bảo toàn ngữ nghĩa và đúng đắn ngữ nghĩa bằng cách sử dụng chứng minh nhất quán nội tại trong B; một ánh xạ phức tạp hơn được dùng cho việc chứng minh tính hợp lưu và tính dừng, sử dụng chứng minh tinh chỉnh (refinement proof) [36].

Dạng tổng quát của một máy B `Mτ` biểu diễn một chuyển đổi mô hình tách biệt `τ` với ngôn ngữ nguồn `S` và ngôn ngữ đích `T` là:

```
MACHINE Mt SEES SystemTypes
VARIABLES
  /* các biến cho mỗi kiểu thực thể và đặc trưng của S */
  /* các biến cho mỗi kiểu thực thể và đặc trưng của T */
INVARIANT
  /* các định nghĩa kiểu cho mỗi kiểu thực thể và đặc trưng của S và T */
  GammaS &
  Asm0 & Inv
INITIALISATION
  /* var := {} cho mỗi biến */
OPERATIONS
  /* các thao tác tạo cho các kiểu thực thể của S, bị hạn chế bởi Asm */
  /* các thao tác cập nhật cho các đặc trưng của S, bị hạn chế bởi Asm */
  /* các thao tác biểu diễn các bước chuyển đổi */
END
```

`SystemTypes` định nghĩa kiểu `Object OBJ` và bất kỳ định nghĩa kiểu nào khác cần thiết, ví dụ, của các kiểu liệt kê (enumerated types). Các thao tác để tạo và cập nhật các phần tử `S` được dùng để thiết lập dữ liệu mô hình nguồn của chuyển đổi. Sau đó, các thao tác biểu diễn các bước chuyển đổi được thực hiện.

Nếu `Asm0` bao gồm các công thức lượng hóa toàn thể `∀s : Si · ψ`, thì các công thức đã thể hiện hóa (instantiated) `ψ[sx/s]` được dùng như các hạn chế trên các thao tác tạo `sx : Si` (hoặc các lớp con của `Si`). Tương tự, thao tác `setf(sx, fx)` sửa đổi đặc trưng `f` của `Si` có một tiền điều kiện `ψ[sx/s, fx/s.f]`. Tất cả các thao tác này sẽ bao gồm các tiền điều kiện `Asm1` từ `Asm` chỉ liên quan tới mô hình đích.

Ví dụ, chuyển đổi ở Hình 1 có thể được định nghĩa bằng máy từng phần sau đây:

```
MACHINE Mt SEES SystemTypes
VARIABLES objects, as, x, br, bs, y, ar
INVARIANT
  objects <: Object_OBJ &
  as <: objects & bs <: objects &
  x : as --> INT & br : as --> FIN(bs) &
  y : bs --> INT & ar : bs --> FIN(as) &
  !a.(a : as => x(a) > 0) &
  !a.(a : as => !b.(b : bs => (b : br(a) <=> a : ar(b)))) &
  !b.(b : bs => #a.(a : as & y(b) = x(a)*x(a) & b : br(a)))
INITIALISATION
  objects, as, x, br, bs, y, ar := {}, {}, {}, {}, {}, {}, {}
```

Bất biến biểu thị `ΓS` và các thuộc tính `Inv` của chuyển đổi. `#b.P` là cú pháp B cho `∃b · P`, `!a.P` là cú pháp B cho `∀a · P`. `&` biểu thị phép hội (conjunction), `<:` biểu thị `⊆` và `-->` là `→` (toán tử kiến tạo kiểu hàm toàn phần — total function type constructor). Một tập hợp toàn thể `objects` gồm các đối tượng đang tồn tại được duy trì, đây là tập con của kiểu tĩnh `Object OBJ` được khai báo trong `SystemTypes`. Các xuất hiện của `E@pre` hoặc `f@pre` trong `Inv` hoặc `Post` được diễn giải bởi các biến bổ sung `es_pre, f_pre` có cùng kiểu với `es` và `f`. Chúng được sửa đổi song song với `es` và `f` bởi các thao tác tạo và sửa đổi mô hình nguồn, và không đổi bởi các thao tác cho các bước tính toán chuyển đổi.

Các thao tác biểu diễn các bước tính toán được suy ra từ các triển khai quy tắc `δi` của các ràng buộc `Cn`. Cách tiếp cận mô hình hóa này tạo thuận lợi cho việc xác minh sử dụng phép tính tiền điều kiện yếu nhất (weakest precondition calculation), so với các mã hóa trừu tượng hơn. Nếu `Cn` có dạng `Si→forAll(s | SCond implies Succ)` thì thao tác biểu diễn một bước tính toán `δi` của `Cn` là:

```
delta_i(s) =
  PRE s : sis & SCond & not(Succ) &
      C1 & ... & Cn-1 & def(Succ)
  THEN
    stat'(Succ)
  END
```

trong đó `stat′(P)` mã hóa diễn giải thủ tục `stat(P)` của `P` trong các câu lệnh giống chương trình của B, gọi là *các phép thay thế tổng quát hóa* (generalised substitutions). Những câu lệnh này có cú pháp tương tự với ngôn ngữ lập trình được mô tả ở Mục 2, và dùng cùng ngữ nghĩa tiền điều kiện yếu nhất. B có thêm một dạng câu lệnh `v := e1 ∥ w := e2` của *phép gán song song* (parallel assignment): các phép gán được thực hiện độc lập với thứ tự, với các giá trị của `e1, e2` được gán đồng thời cho `v`, `w`. Câu lệnh `ANY WHERE THEN` của B tương ứng với câu lệnh tạo của chúng ta.

Nếu việc triển khai của `τ` định nghĩa một triển khai quy tắc không chuẩn của `Cn`, việc triển khai này có thể được mã hóa trong B thay cho định nghĩa trên của `delta_i`. Nếu việc triển khai của `τ` yêu cầu rằng tất cả các ràng buộc `C1, ..., Cn−1` được thiết lập trước `Cn`, thứ tự này có thể được mã hóa bằng cách bao gồm `C1, ..., Cn−1` trong các tiền điều kiện của `delta_i`, như trên (x. các điều kiện `ECond` của Mục 4). `not(Succ)` có thể được bỏ qua nếu các điều kiện áp dụng phủ định không được kiểm tra bởi việc triển khai `Cn`.

Đối với ánh xạ sang B, `def(Succ)` bao gồm các kiểm tra rằng các biểu thức số trong `Succ` nằm trong giới hạn kích thước của các kiểu số hữu hạn `NAT` và `INT` của B, và rằng `objects ≠ Object OBJ` trước bất kỳ việc tạo đối tượng mới nào.

Mô hình tính toán của một chuyển đổi `τ` được biểu thị trong `Mτ` do đó trùng khớp với định nghĩa tính toán chuyển đổi được mô tả ở Mục 2: một tính toán của `τ` là một dãy các bước chuyển đổi được thực thi theo một thứ tự không xác định, chỉ bị ràng buộc bởi nhu cầu duy trì `Inv`, và, nếu một triển khai cụ thể `I` được định nghĩa, phải thỏa mãn các hạn chế thứ tự của hành vi của `I`.

Đối với ví dụ ở Hình 1, sử dụng một triển khai điểm bất động, máy B hoàn chỉnh kết quả có:

```
OPERATIONS
create_A(xx) =
  PRE xx : INT & xx > 0 & objects /= Object_OBJ & bs = {}
  THEN
    ANY ax WHERE ax : Object_OBJ - objects
    THEN
      as := as \/ { ax } || objects := objects \/ { ax } ||
      x(ax) := xx ||
      br(ax) := {}
    END
  END;

setx(ax,xx) =
  PRE ax : as & xx : INT & xx > 0 & bs = {}
  THEN
    x(ax) := xx
  END;

r1(ax) =
  PRE ax : as & not( #b.(b : bs & y(b) = x(ax)*x(ax) & b : br(a)) ) &
      objects /= Object_OBJ & x(ax)*x(ax) : INT
  THEN
    ANY b WHERE b : Object_OBJ - objects
    THEN
      bs := bs \/ { b } || objects := objects \/ { b } ||
      y(b) := x(ax)*x(ax) ||
      br(ax) := br(ax) \/ { b } || ar(b) := { ax }
    END
  END
END
```

`r1` định nghĩa bước chuyển đổi của ràng buộc hậu điều kiện. Máy được sinh ra một cách tự động bởi các công cụ UML-RSDS từ đặc tả UML của chuyển đổi⁷. UML-RSDS mã hóa ngữ nghĩa của mọi trường hợp cập nhật liên kết, bao gồm các tình huống với các đầu liên kết nghịch đảo lẫn nhau, như trong ví dụ này (hai phép gán cuối của `r1`).

Sử dụng các máy này, chúng ta có thể xác minh các thuộc tính đúng đắn cú pháp và bảo toàn ngữ nghĩa của một chuyển đổi mô hình, bằng phương tiện chứng minh *nhất quán nội tại* (internal consistency) của máy B biểu diễn chuyển đổi và các siêu mô hình của nó. Tính nhất quán nội tại của một máy B bao gồm các điều kiện logic sau:

- Không gian trạng thái của máy khác rỗng: `∃v · I` trong đó `v` là bộ các biến của máy, và `I` là bất biến của nó.
- Việc khởi tạo thiết lập bất biến: `[Init]I`.
- Mỗi thao tác duy trì bất biến: `Pre ∧ I ⇒ [Code]I` trong đó `Pre` là tiền điều kiện của thao tác, và `Code` là hiệu ứng của nó.

Các máy B ngầm định thỏa mãn *tiên đề khung* (frame axiom) cho các thay đổi trạng thái: các biến `v` không được cập nhật tường minh bởi một thao tác được giả định là không bị sửa đổi bởi thao tác đó. Điều này tương ứng với giả định được đưa ra trong khung làm việc của chúng tôi rằng `v` không bị sửa đổi bởi hoạt động `act` nếu `v ∉ wr(act)`.

Chúng ta có thể tuân theo sơ đồ chứng minh được chỉ ra ở Mục 4 sử dụng B, như sau (đối với các chuyển đổi mô hình tách biệt):

1. Chứng minh nhất quán nội tại của `Mτ` thiết lập rằng `Inv` là một bất biến của chuyển đổi.
2. Bằng cách thêm các tiên đề của `ΓT` vào mệnh đề `INVARIANT`, tính hợp lệ của chúng trong suốt chuyển đổi và ở trạng thái cuối của chuyển đổi có thể được chứng minh bằng chứng minh nhất quán nội tại, thiết lập tính đúng đắn cú pháp.
3. Bằng cách thêm `φ` và `χ(φ)` vào `INVARIANT` của `Mτ`, cho `φ ∈ Pres`, bảo toàn ngữ nghĩa của `φ` có thể được chứng minh bằng chứng minh nhất quán nội tại. Các thao tác tạo và cập nhật để thiết lập mô hình nguồn phải bị hạn chế phù hợp bởi `φ`.
4. Khi chuyển đổi kết thúc, tất cả các điều kiện áp dụng của các quy tắc chuyển đổi đều sai. Suy diễn `(∧¬(ACond)) ⇒ Post` có thể được mã hóa trong mệnh đề `ASSERTIONS` của `Mτ` và được chứng minh sử dụng các bất biến `ΓS ∪ Inv ∪ Asm0`.

Đối với các chuyển đổi cập nhật tại chỗ, việc chứng minh tính dừng, tính hợp lưu và tính đúng đắn ngữ nghĩa cần sử dụng các biến thể `Q` phù hợp cho mỗi ràng buộc, được xem xét dưới đây.

Sử dụng Atelier B phiên bản 4.0, 24 nghĩa vụ chứng minh (proof obligations) cho tính nhất quán nội tại của máy `Mt` trên được sinh ra, trong đó 18 được chứng minh tự động, và phần còn lại có thể được chứng minh tương tác sử dụng công cụ trợ lý chứng minh được cung cấp.

Để chứng minh rằng một độ đo `Q` được giả định là một hàm biến thể thực sự cho một ràng buộc, có thể thực hiện chứng minh tinh chỉnh trong B, với một trừu tượng hóa của máy mô hình chuyển đổi `Mτ` được định nghĩa là `M0τ`:

*(⁷ Trong thực tế, nên tránh dùng tên đặc trưng, biến và kiểu thực thể chỉ có một chữ cái, vì chúng có ý nghĩa đặc biệt trong B AMN.)*

```
MACHINE M0t SEES SystemTypes
VARIABLES /* các biến cho dữ liệu mô hình nguồn */, q
INVARIANT
  /* kiểu của dữ liệu mô hình nguồn */ &
  q : NAT
INITIALISATION
  es, q := {}, 0
OPERATIONS
  /* các thao tác tạo và cập nhật cho mô hình nguồn: chúng đặt q một cách tùy ý trong NAT */
  delta() =
    PRE q > 0
    THEN
      q :: 0..q-1
    END
END
```

`delta` biểu diễn một bước chuyển đổi của ràng buộc mà `q` là biến thể được giả định. Toán tử `q :: s` gán một phần tử không xác định của `s` cho `q`. Mỗi ràng buộc `Ci` có thể có một biến thể tương ứng `qi`, thao tác `delta_i` cho các bước chuyển đổi trừu tượng hóa của `Ci` khi đó có dạng:

```
delta_i() =
  PRE qi > 0 & qk = 0 /* cho k < i */
  THEN
    qi :: 0..qi-1 || qj :: NAT /* cho j > i */
  END
```

trong đó các triển khai ràng buộc của `C1, ..., Ci−1` được thiết kế để dừng trước bất kỳ thực thi nào của `delta_i` và do đó các biến thể của chúng được giả định là 0 trong tiền điều kiện của `delta_i`.

Máy `Mτ` gốc khi đó được dùng để định nghĩa một tinh chỉnh (refinement) của `M0τ`, với quan hệ tinh chỉnh cho một định nghĩa tường minh của các biến thể `qi`. Chứng minh tinh chỉnh khi đó cố gắng xác minh rằng định nghĩa tường minh của mỗi `qi` tuân theo đặc tả trừu tượng, tức là, nó bị giảm nghiêm ngặt bởi mỗi lần thực thi `delta_i`.

Các nghĩa vụ tinh chỉnh trong B là [31]:

- Các bất biến kết hợp `InvA ∧ InvR` của máy trừu tượng và máy tinh chỉnh cùng khả thỏa.
- Việc khởi tạo đã tinh chỉnh `InitR` thiết lập các bất biến: `[InitR]¬[InitA]¬(InvA ∧ InvR)`.
- Mỗi thao tác đã tinh chỉnh `PRE PreR THEN CodeR END` thỏa mãn quan hệ tiền-hậu điều kiện của phiên bản trừu tượng của nó: `InvA ∧ InvR ∧ PreA ⇒ PreR ∧ [CodeR]¬[CodeA]¬(InvA ∧ InvR)`.

Chứng minh tinh chỉnh thường đòi hỏi nhiều công sức thủ công, với phần lớn các nghĩa vụ chứng minh cần chứng minh tương tác.

Để xác minh tính hợp lưu của một chuyển đổi, chỉ cần chỉ ra rằng có một trạng thái duy nhất (sai khác đẳng cấu cấu trúc) mà tại đó tất cả các biến thể `qi` đều có `qi = 0`. Điều này có thể được xác minh trong bản tinh chỉnh bằng cách thêm một mệnh đề `ASSERTIONS` có dạng sơ đồ:

```
ASSERTIONS
  q1 = 0 & ... & qn = 0 => tstate = f(sstate)
```

Mệnh đề này biểu thị rằng trạng thái mô hình đích `tstate` có các giá trị cụ thể theo trạng thái mô hình nguồn `sstate`, khi tất cả các `qi` đều bằng 0.

Các công cụ B sẽ tạo ra các nghĩa vụ chứng minh cho khẳng định này, và sẽ đóng vai trò một trợ lý chứng minh trong việc cấu trúc hóa chứng minh và tự động thực hiện các bước chứng minh thường quy. Một hệ quả xa hơn của việc chứng minh khẳng định này là tính đúng đắn ngữ nghĩa của việc triển khai: rằng ngữ nghĩa mong muốn của các phần tử mô hình đích tương đối theo các phần tử mô hình nguồn cũng đúng khi kết thúc. Một ví dụ về dạng chứng minh tính hợp lưu này được đưa ra trong [39]: trong trường hợp này một chiều (rằng bao đóng bắc cầu được tính toán của một quan hệ `r` luôn là tập con của bao đóng bắc cầu thực sự) của đẳng thức là một phần của bất biến chuyển đổi, và chiều còn lại theo sau từ `Q = 0`.

Các thủ tục trên có thể được dùng như một quy trình tổng quát để chứng minh các thuộc tính `Inv` và `Pres`, và để chứng minh tính dừng, tính đúng đắn ngữ nghĩa và tính hợp lưu, bằng phương tiện các hàm biến thể `Q` phù hợp được giả định. Các kỹ thuật này có thể được tổng quát hóa cho bất kỳ triển khai chuyển đổi nào mà các bước chuyển đổi của nó có thể được *sắp xếp tuần tự* (serialised), tức là, mỗi lần thực thi việc triển khai tương đương với một lần thực thi mà các bước tính toán diễn ra theo một thứ tự tuần tự nghiêm ngặt. Giả định này được đưa ra ngầm định trong mô hình B.

Việc biểu diễn và xác minh các ngôn ngữ chuyển đổi mô hình khai báo khác, chẳng hạn TGG hoặc QVT-R, có thể được thực hiện bằng phương tiện dịch các ngôn ngữ này sang các siêu mô hình của Mục 2. Đối với TGG, có thể tốt hơn nếu kết hợp các thao tác cập nhật mô hình đầu vào và những thao tác biểu thị các bước chuyển đổi, vì một bước chuyển đổi trong TGG liên quan đến việc cập nhật đồng thời các mô hình nguồn, đích và tương ứng (correspondence models).

Các bản ghi chứng minh (proof transcripts) có thể được tạo ra bởi trợ lý chứng minh Atelier B, sau đó có thể được kiểm tra bởi một bộ kiểm tra chứng minh độc lập để đạt được các yêu cầu chứng nhận của các tiêu chuẩn như DO-178C [19]. Giống như với Z3, có thể lập luận rằng bản dịch OCL sang B của chúng tôi biểu diễn chính xác ngữ nghĩa của (phiên bản logic cổ điển của chúng tôi về) OCL, do đó việc chứng minh trong B là đúng đắn tương đối theo suy diễn logic trên các câu OCL trong logic bậc nhất, tuy nhiên các kiểu số `NAT` và `INT` trong B là có giới hạn (bounded), và tương ứng với các số nguyên không dấu và có dấu 32-bit, do đó tính đúng đắn chỉ áp dụng nếu cùng một ý nghĩa được gán cho `Integer` của OCL. Thêm vào đó, kiểu `Real` phải bị loại trừ khỏi các ràng buộc và chuyển đổi để thực hiện phân tích chứng minh hợp lệ trong B. `Object OBJ` là hữu hạn trong B, do đó cần đặt một giới hạn trên tiên nghiệm (a-priori upper bound) cho số lượng đối tượng tối đa.

Kích thước của mô hình hình thức B `Mτ` tuyến tính theo kích thước của chuyển đổi mô hình `τ`, tuy nhiên độ phức tạp của các quy tắc chuyển đổi có ảnh hưởng đáng kể tới nỗ lực chứng minh cần thiết. Các ràng buộc hậu điều kiện sử dụng các lượng từ `forAll` lồng bên trong `exists` trong vế sau của chúng không thể được xác minh hiệu quả, và thay vào đó cần sử dụng dạng hội-kéo-theo. Các thao tác cập nhật đệ quy không thể được biểu diễn. B không phù hợp để thiết lập các thuộc tính khả thỏa khẳng định sự tồn tại của các mô hình thuộc loại nhất định, và các công cụ như Z3, UMLtoCSP [15], Alloy [2] hoặc USE [29] phù hợp hơn cho những việc này.

### 7.1 Các công cụ xác minh chuyển đổi (Transformation verification tools)

Bảng 9 liệt kê một số hình thức luận/công nghệ hiện có có thể được dùng cho việc xác minh chuyển đổi dựa trên chứng minh, và xác định mức độ phù hợp hoặc hạn chế của chúng cho các nhiệm vụ xác minh khác nhau.

Công nghệ toàn diện nhất dường như là B, cũng là công nghệ duy nhất hỗ trợ trực tiếp chứng minh quy nạp trên các bước tính toán. Tuy nhiên, B đòi hỏi chuyên môn đáng kể về logic và lý thuyết tập hợp để sử dụng thành công, vì hầu hết các nhiệm vụ xác minh liên quan đến chứng minh tương tác: chứng minh tự động có thể chỉ giải quyết được một tỷ lệ nhỏ các nghĩa vụ tinh chỉnh nói riêng. B cũng không cung cấp bất kỳ khả năng tìm phản ví dụ nào. Một nhược điểm của nhiều hình thức luận là chúng dựa trên logic bậc nhất hoặc logic quan hệ hai giá trị, trái ngược với logic ba giá trị của OCL được dùng trong UML. Tuy nhiên, độ phức tạp của hệ thống giá trị OCL đầy đủ, liên quan đến cả giá trị `invalid` và `null`, và việc thiếu ngữ nghĩa rõ ràng của nó, có nghĩa là các công cụ cố gắng xử lý OCL đầy đủ nhất thiết phải đưa ra các giả định cụ thể về ngữ nghĩa, có thể không khớp với ý định của người viết đặc tả [11].

Z3 rất phù hợp để chứng minh các thuộc tính trong một trạng thái duy nhất, nhưng các chuyển đổi có thể chỉ có các lý thuyết khả quyết nếu chúng thỏa mãn thuộc tính *phân tầng* (stratification) (tức là, chỉ các điều hướng theo một hướng nhất quán lên hoặc xuống các cây phân cấp hợp thành của các siêu mô hình được sử dụng), và Z3 cũng bị hạn chế bởi khả năng biểu diễn hạn chế của nó đối với OCL, tức là, nó không có biểu diễn trực tiếp cho các toán tử như `select`, `collect`, v.v., trái ngược với B. Hạn chế này cũng áp dụng cho Alloy. Công cụ USE hoạt động trực tiếp trên UML và OCL, do đó thu hẹp khoảng cách ngữ nghĩa giữa hình thức luận phân tích và chuyển đổi đang được phân tích, tuy nhiên USE không có khả năng chứng minh. B thiếu hỗ trợ cho số thực và sử dụng số nguyên có giới hạn, trong khi Z3 thiếu hỗ trợ cho chuỗi và quan hệ kiểu con. HOL-OCL có một biểu diễn toàn diện của OCL, nhưng chứng minh trong HOL-OCL chủ yếu là tương tác.

**Bảng 9. Các công nghệ xác minh cho chuyển đổi mô hình**

| Hình thức luận | Khả năng | Hạn chế |
|---|---|---|
| Alloy [2] | Phân tích ràng buộc; phát hiện phản ví dụ | Không gian tìm kiếm có giới hạn: xây dựng phản ví dụ không đầy đủ. Dùng logic quan hệ. |
| B [36] | Chứng minh (tương tác và tự động) | Chứng minh tinh chỉnh có thể rất tốn thời gian. Dùng logic hai giá trị. |
| UML-RSDS [49] | Phân tích cú pháp, ánh xạ tới B, Z3, USE | Yêu cầu chuyển đổi phải được viết bằng UML-RSDS. Dùng logic 2 giá trị. |
| USE [29] | Xây dựng phản ví dụ | Không gian tìm kiếm có giới hạn. |
| Z3 [51] | Kiểm tra khả thỏa, chứng minh bằng cách phản ví dụ thất bại | Phát hiện phản ví dụ không đầy đủ. Khả năng biểu đạt hạn chế cho OCL. Dùng logic 2 giá trị. |
| HOL-OCL [10] | Chứng minh tương tác và tự động | Ngữ nghĩa đặc thù công cụ cho OCL. |

Do đó, nhìn chung cần có một cách tiếp cận hỗn hợp (heterogeneous) đối với hỗ trợ công cụ xác minh chuyển đổi, với các công nghệ được lựa chọn dựa trên mức độ phù hợp của chúng cho các nhiệm vụ cụ thể.

Một lĩnh vực quan trọng chưa được phát triển trước đây là việc định nghĩa các kỹ thuật chứng minh cho các phép hợp thành (compositions) của các chuyển đổi. Chúng tôi xác định một số quy tắc trong [39]. Đặc biệt, đối với các phép hợp thành tuần tự như Hình 6, tính đúng đắn cú pháp của chuyển đổi hợp thành `τ1; τ2` theo sau từ tính đúng đắn cú pháp của `τ1` và `τ2` riêng biệt, với điều kiện các giả định `Asm2` của `τ2` có thể được đảm bảo khi `τ1` kết thúc, hoặc vì những giả định này và `Asm1` được kéo theo bởi các giả định tổng thể `Asm` của phép hợp thành, và `Asm2` không bị `τ1` làm mất hiệu lực, hoặc vì `τ1` thiết lập `Asm2`. Tương tự, các thuộc tính bảo toàn ngữ nghĩa và tính dừng hợp thành qua phép hợp thành tuần tự. Tuy nhiên, đối với tính hợp lưu của `τ1; τ2`, cần có tính hợp lưu của `τ1`, và thêm vào đó `τ2` cần *bảo toàn đẳng cấu* (isomorphism-preserving): nó ánh xạ các mô hình nguồn đẳng cấu thành các mô hình đích đẳng cấu.

## 8 Các kỹ thuật đúng-theo-cấu-trúc (Correctness by construction techniques)

Nếu các chuyển đổi được đặc tả theo cách khai báo, độc lập nền tảng (platform-independent), sử dụng các hậu điều kiện, tiền điều kiện và bất biến được biểu thị trong siêu mô hình đặc tả chuyển đổi (Hình 5), thì các triển khai độc lập nền tảng (được biểu thị trong siêu mô hình ở Hình 7) có thể được suy ra từ chúng, và với sự tồn tại của các ánh xạ tới các ngôn ngữ chuyển đổi cụ thể, chẳng hạn ETL, ATL, v.v., các triển khai đặc thù nền tảng (platform-specific) khi đó có thể được sinh ra từ các mô hình triển khai này. Những triển khai đặc thù nền tảng này khi đó sẽ đúng-theo-cấu-trúc đối với các đặc tả: chúng sẽ thỏa mãn tính đúng đắn ngữ nghĩa mà không cần chứng minh thêm. Trong UML-RSDS chúng tôi sinh trực tiếp các triển khai Java thực thi được từ các triển khai độc lập nền tảng [38].

Đặc tả chuyển đổi trong siêu mô hình ở Hình 5 đóng vai trò của một *mô hình độc lập tính toán* (Computation-independent model — CIM) theo thuật ngữ phát triển hướng mô hình (model-driven development), tức là, một mô hình không có chi tiết thuật toán tường minh, trong khi triển khai độc lập nền tảng (Hình 7) đóng vai trò của một *mô hình độc lập nền tảng* (Platform-independent model — PIM).

Cơ sở cho việc tổng hợp một triển khai đúng-theo-cấu-trúc của các quy tắc ánh xạ, là định nghĩa của một diễn giải thủ tục, `stat(P)`, cho các vị từ OCL nhất định `P`. `stat` ánh xạ từ các biểu thức trên một ngôn ngữ (hoặc một hợp các ngôn ngữ) `L` sang các hành vi trên `L`: `stat : Exp(L) ⇾ Statement(L)`.

Ý định đằng sau ánh xạ này là `stat(P)` cần thiết lập `P`, giả sử tính xác định giá trị của các biểu thức trong `P`: `def(P) ⇒ [stat(P)]P` cho `P ∈ dom(stat)`.

Hoạt động mức thiết kế `stat(P)` gắn với một vị từ hậu điều kiện đặc tả chuyển đổi `P` được định nghĩa một cách có hệ thống dựa trên cấu trúc của `P`. `stat(P)` có thể được đọc là "Làm cho `P` đúng". Bảng 10 cho thấy một số trường hợp chính của định nghĩa này.

**Bảng 10. Định nghĩa của `stat(P)`**

| `P` | `stat(P)` | Điều kiện |
|---|---|---|
| `x = e` | `x := e` | `x` có thể gán, `x ∉ rd(e)` |
| `e : x` | `x := x→including(e)` | `x` có thể gán, `x` có giá trị tập hợp, `x ∉ rd(e)` |
| `e /: x` | `x := x→excluding(e)` | `x` có thể gán, `x` có giá trị tập hợp, `x ∉ rd(e)` |
| `e <: x` | `x := x→union(e)` | `x` có thể gán, `x` có giá trị tập hợp, `x ∉ rd(e)` |
| `e /<: x` | `x := x − e` | `x` có thể gán, `x` có giá trị tập hợp, `x ∉ rd(e)` |
| `x→isDeleted()` | `E := E→excluding(x)` | với mỗi kiểu thực thể `E` (đối tượng đơn `x`) chứa `x` |
| `obj.op(e)` | `obj.op(e)` | đối tượng đơn `obj` |
| `objs.op(e)` | `for x : objs do x.op(e)` | tập hợp `objs` |
| `P1 and P2` | `stat(P1); stat(P2)` | `wr(P2) ∩ wr(P1) = {}`, `wr(P2) ∩ rd(P1) = {}` |
| `E→exists(x \| x.id = v and P1)` | `if E.id→includes(v) then x := E[v]; stat(P1) else (x : E; stat(x.id = v and P1))` | `E` là kiểu thực thể cụ thể với `E→isUnique(id)` |
| `E→exists(x \| P1)` | `(x : E; stat(P1))` | `E` là kiểu thực thể cụ thể, `P1` không có dạng `x.id = v and P2` cho thuộc tính `id` duy nhất của `E` |
| `e→exists(x \| x.id = v and P1)` | `if e→includes(E[v]) then (x := E[v]; stat(P1)) else skip` | `e` là biểu thức không thể ghi, kiểu phần tử `E`, `E→isUnique(id)` |
| `e→exists(x \| P1)` | `if e→notEmpty() then (x := e→any(); stat(P1)) else skip` | `e` là biểu thức không thể ghi, `e, P1` không có dạng trên |
| `E→exists1(x \| P1)` | `if E→exists(x \| P1) then skip else stat(E→exists(x \| P1))` | `E` là kiểu thực thể cụ thể hoặc biểu thức không thể ghi `e` với kiểu phần tử `E` |
| `E→forAll(x \| P1)` | `for x : E do stat(P1)` | `P` kiểu 1, cục bộ hóa |
| `P1 implies P2` | `if P1 then stat(P2) else skip` | |

Các cập nhật cho các đầu liên kết có thể đòi hỏi thêm các cập nhật khác cho các đầu liên kết nghịch đảo, các cập nhật cho các phạm vi kiểu thực thể hoặc các đặc trưng có thể đòi hỏi thêm các cập nhật cho các đặc trưng dẫn xuất (derived) và các đặc trưng phụ thuộc dữ liệu khác, v.v. Tất cả những cập nhật này đều được bao gồm trong hoạt động `stat`. Đặc biệt, đối với `x→isDeleted()`, `x` được loại bỏ khỏi mọi đầu liên kết mà nó nằm trong đó, và có thể xảy ra thêm các phép xóa theo tầng (cascaded deletions) nếu các đầu này là các đầu bắt buộc/hợp thành.

Các mệnh đề cho `X→exists(x | x.id = v and P1)` kiểm tra sự tồn tại của một `x` với `x.id = v` trước khi tạo một đối tượng như vậy: điều này có ảnh hưởng tới hiệu năng nhưng là cần thiết cho tính đúng đắn: không nên tồn tại hai phần tử `X` khác nhau với cùng giá trị khóa chính. Chiến lược thiết kế này là một trường hợp của nguyên tắc nổi tiếng 'kiểm tra trước khi thực thi' (check before enforce) được dùng trong QVT, ETL, ATL và các ngôn ngữ chuyển đổi khác.

`stat(E→forAll(x | P1))` có các định nghĩa đặc biệt cho các công thức lượng hóa kiểu 2 và kiểu 3, và cho các công thức kiểu 1 không cục bộ hóa, dựa trên phép lặp điểm bất động ([38]).

Khung ghi của `stat(P)` bằng `wr(P)`, khung đọc bao gồm `rd(P)`.

Như một ví dụ về các định nghĩa này, `stat(R)` cho hậu điều kiện của chuyển đổi ở Hình 1 là:

```
for a : A do
  (b : B; b.y := a.x*a.x;
   a.br := a.br \/ { b };
   b.ar := b.ar \/ { a })
```

Việc lựa chọn một PIM phù hợp cho một CIM chuyển đổi dựa trên các quan hệ phụ thuộc dữ liệu của các hậu điều kiện của CIM. Cho tập hợp `Post` các hậu điều kiện của một chuyển đổi `τ`, chúng ta muốn tìm một thứ tự cho các ràng buộc hậu điều kiện sao cho việc hợp thành tuần tự các triển khai 'tự nhiên' `stat(Cn)` của các ràng buộc `Cn ∈ Post` đạt được phép hội `∧Post` của các hậu điều kiện.

Để tìm một thứ tự như vậy chúng ta xem xét các thuộc tính sau của các ràng buộc: một thứ tự phụ thuộc `Cn < Cm` được định nghĩa giữa các ràng buộc khác nhau bởi `wr(Cn) ∩ rd(Cm) ≠ {}`, "`Cm` phụ thuộc vào `Cn`". Một triển khai chuyển đổi với các triển khai quy tắc `ri` của các hậu điều kiện `Ci` (tức là, với mỗi `ri.applies.relation = Ci`) được sắp xếp theo thứ tự `r1, ..., rn` cần thỏa mãn các điều kiện *không can thiệp cú pháp* (syntactic non-interference):

1. Nếu `Ci < Cj`, với `i ≠ j`, thì `i < j`.
2. Nếu `i ≠ j` thì `wr(Ci) ∩ wr(Cj) = {}`.

Cùng nhau, các điều kiện này đảm bảo rằng hành vi `stat(Cj)` của các triển khai `rj` của các ràng buộc sau `Cj` không thể làm mất hiệu lực các ràng buộc trước đó `Ci`, cho `i < j`.

Một triển khai chuyển đổi với thứ tự `r1, ..., rn` của các triển khai quy tắc thỏa mãn *không can thiệp ngữ nghĩa* (semantic non-interference) nếu với `i < j`: `Ci ⇒ [stat(Cj)]Ci`.

Không can thiệp cú pháp kéo theo không can thiệp ngữ nghĩa, nhưng không ngược lại. Nếu thứ tự `r1, ..., rn` thỏa mãn không can thiệp ngữ nghĩa, thì bằng quy nạp có thể chứng minh rằng việc hợp thành tuần tự tương ứng của các triển khai quy tắc thiết lập được phép hội của các `Ci` [38]. Do đó bất kỳ thứ tự không can thiệp ngữ nghĩa nào của các `ri` đều tương đương theo nghĩa này.

Triển khai PIM kết quả do đó có hoạt động `r1; ...; rn` trong đó `ri ∈ RuleImplementation` triển khai `Ci`: `ri.applies.relation = Ci`. Đến lượt mình, mỗi `ri` có `ri.behaviour = stat(Ci)`. Như đã mô tả ở Mục 5, tùy thuộc vào các phụ thuộc dữ liệu nội tại của `Ci`, việc triển khai `stat(Ci)` của nó có thể được định nghĩa như một phép lặp có giới hạn hoặc điểm bất động của các bước chuyển đổi riêng lẻ `δi`. Đối với một ràng buộc kiểu 1 cục bộ hóa `Si→forAll(s | SCond implies Succ)`, điều này dẫn đến một triển khai có dạng `for s : Si do δi(s)` trong đó `δi` có hoạt động `stat(SCond implies Succ)`.

Nếu có thể tìm được một thứ tự cho các ràng buộc `Post` của `τ` thỏa mãn không can thiệp ngữ nghĩa, thì tính đúng đắn ngữ nghĩa do đó đúng cho một triển khai được xây dựng sử dụng thứ tự này. Các thuộc tính về tính dừng và tính hợp lưu có thể được thiết lập bằng phân tích cú pháp các ràng buộc riêng lẻ, đối với các ràng buộc kiểu 1, theo quy trình của Mục 5. Đối với các dạng ràng buộc khác, những thuộc tính này có thể đòi hỏi việc xác minh các biến thể phù hợp (Mục 7). Các thuộc tính đúng đắn cú pháp và bảo toàn ngữ nghĩa có thể cần chứng minh, ví dụ, sử dụng Z3 hoặc B.

### 8.1 Kỹ thuật đảo ngược (reverse-engineering) các triển khai chuyển đổi mô hình

Quy trình trên có thể được áp dụng theo chiều ngược để trừu tượng hóa mã MT hiện có thành các đặc tả khai báo. Một câu lệnh `Code ∈ Statement` có thể được trừu tượng hóa thành một vị từ hậu điều kiện `P` nếu `stat(P) = Code`. Đặc biệt, một phép gán `x := e` được trừu tượng hóa thành `x = e[x@pre/x]` và `Code1; Code2` được trừu tượng hóa thành `P1 and P2` nếu `stat(P1) = Code1`, `stat(P2) = Code2` và `wr(P1) ∩ wr(P2) = {}` và `wr(P2) ∩ rd(P1) = {}`. Tương tự đối với các vòng lặp có giới hạn, điều kiện, v.v. Trong các trường hợp mà các điều kiện phụ thuộc dữ liệu không đúng trong mã, cấu trúc `¬[Code]¬(v′1 = v1 and ... and v′k = vk)` có thể được dùng để trích xuất một đặc tả tiền-hậu điều kiện từ `Code`, trong đó `wr(Code) = {v1, ..., vk}`. Ví dụ, `¬[x := x * 5; x := x + 1]¬(x′ = x)` là `x′ = (x * 5) + 1`, tức là, `x = (x@pre * 5) + 1`.

Nếu `P` có dạng `Si→forAll(s | F(s))` và `rd(P) ∩ wr(P) ≠ {}`, thì `stat(P)` là một phép lặp điểm bất động tổng quát có dạng sơ đồ:

```
while not(P) do
  (select s : Si with not(F(s));
   stat(F(s)))
```

Do đó bất kỳ phép lặp điểm bất động nào có dạng này, nhưng với một phương tiện xác định duy nhất hơn để lặp qua các `s : Si`, sẽ được trừu tượng hóa thành `P`, với điều kiện phép lặp được đảm bảo tiếp cận tất cả các phần tử của `Si`. Mục 10 đưa ra một ví dụ.

Những kỹ thuật này cung cấp một cơ sở để ánh xạ mã MT lai hoặc mệnh lệnh thành các đặc tả MT trong các siêu mô hình của Mục 2.

## 9 Nghiên cứu tình huống 1: Tổng hợp mã Java từ UML (Case study 1: UML to Java code synthesis)

Chúng tôi xem xét một đoạn nhỏ của chuyển đổi tinh chỉnh (refinement transformation) `τ` này, để minh họa cách các kỹ thuật xác minh trên có thể được áp dụng cho các chuyển đổi như vậy. Hình 9 cho thấy các phần của siêu mô hình ngôn ngữ nguồn và đích mà chúng tôi xem xét ở đây.

*Fig. 9. Các siêu mô hình UML và Java*

Lý thuyết `ΓS` của ngôn ngữ UML nguồn bao gồm thuộc tính duy nhất của tên lớp. Các giả định `Asm0` trên mô hình nguồn của chuyển đổi bao gồm việc không có trường hợp đa kế thừa hoặc chu trình kế thừa nào trong mô hình nguồn. `Asm` là `Asm0` cùng với giả định rằng mô hình đích rỗng: `JavaClass = Set{}`, v.v.

Các thuộc tính ngôn ngữ Java cần thiết `ΓT` là tên lớp Java là duy nhất và không có đa kế thừa hay chu trình kế thừa.

Các ánh xạ chuyển đổi (các hậu điều kiện đặc tả `Post` của `τ`) biểu thị các thuộc tính như:

```
(R1): UMLClass→forAll(c | JavaClass→exists(cj | cj.name = c.name and cj.isAbstract = c.isAbstract))
```

và

```
(R2): UMLClass→forAll(c, d | d : c.generalisation.general implies 
       JavaClass[d.name] : JavaClass[c.name].superclass)
```

định nghĩa cách các mô hình UML và Java ở trạng thái sau nên tương ứng với nhau. `JavaClass[s]` biểu thị lớp Java có tên `s`. Đặc tả này được viết sử dụng mẫu 'Ánh xạ đối tượng trước liên kết' (Map objects before links) [38].

Trong `R1` các đầu ánh xạ là `c ∈ UMLClass` không thể sửa đổi từ mô hình đầu vào UML của chuyển đổi, và `cj ∈ JavaClass` (có thể sửa đổi) từ mô hình đầu ra Java. Tương tự `c, d` là các đầu đầu vào của `R2`.

`Inv` biểu thị các thuộc tính bảo toàn (conservativeness) như:

```
(Inv1): JavaClass→forAll(cj | UMLClass→exists(c | c.name = cj.name and c.isAbstract = cj.isAbstract))
```

và

```
(Inv2): JavaClass→forAll(cj, dj | dj : cj.superclass implies 
        UMLClass[dj.name] : UMLClass[cj.name].generalisation.general)
```

là các nghịch đảo của các thuộc tính hậu điều kiện `Post` tương ứng. Đối với chuyển đổi này, ánh xạ diễn giải ngôn ngữ `χ` có thể được định nghĩa như sau:

```
UMLClass ↦ JavaClass
UMLClass::name ↦ JavaClass::name
```

Đây là một đồng cấu ngôn ngữ từng phần, vì các đặc trưng như `general` và `generalisation` không có diễn giải trong ngôn ngữ đích.

Một ví dụ về chứng minh bảo toàn ngữ nghĩa là việc bảo toàn thuộc tính `φ` rằng không có tên lớp nào chứa ký tự khoảng trắng:

```
UMLClass→forAll(c | not(" " : c.name→characters()))
```

Điều này được dịch thành `χ(φ)`:

```
JavaClass→forAll(c | not(" " : c.name→characters()))
```

Bằng cách sử dụng `Inv1` chúng ta có thể suy ra điều này từ thuộc tính gốc `φ` của các lớp UML. Lưu ý rằng chứng minh này độc lập với việc triển khai cụ thể được chọn: bất kỳ triển khai nào duy trì `Inv` cũng sẽ đảm bảo bảo toàn ngữ nghĩa của `φ`.

Một triển khai cụ thể `I` của `τ` với hành vi `stat(R1); stat(R2)` được chọn, thực hiện tất cả các bước tính toán `r1(c)` của `R1` trước bất kỳ bước tính toán `r2(c, d)` nào của `R2`. Triển khai này thỏa mãn thuộc tính không can thiệp ngữ nghĩa của Mục 8 vì `rd(R1) = {UMLClass, UMLClass::name, UMLClass::isAbstract}`, `wr(R1) = {JavaClass, JavaClass::name, JavaClass::isAbstract}`, `rd(R2) = {UMLClass, UMLClass::name, UMLClass::generalisation, JavaClass, Generalization::general}`, `wr(R2) = {JavaClass::superclass}`, do đó `R1 < R2` và `stat(R2)` không can thiệp cú pháp với `R1`.

Bước chuyển đổi cho `R1` là:

```
r1(c : UMLClass)
  (cj : JavaClass; cj.name := c.name; cj.isAbstract := c.isAbstract)
```

và tương tự cho `r2`.

Chúng ta có thể suy ra rằng `Inv` được bảo toàn bởi các lần áp dụng `r1` của `R1`, từ dạng của `R1`: `cj : JavaClass` mới được tạo ra bởi một lần áp dụng `r1(c)` rõ ràng thỏa mãn `Inv1`, và nó không được liên kết với bất kỳ lớp Java nào khác bởi các liên kết `superclass`, do đó `Inv2` được bảo toàn. Ngoài ra, các lần áp dụng `r2` của `R2` bảo toàn `Inv` vì chúng không tạo ra các lớp Java mới, mà chỉ liên kết các thể hiện hiện có theo cách mà `Inv2` được thỏa mãn.

Nếu không có lần áp dụng nào của `R1` hay `R2` còn có thể thực hiện, điều này có nghĩa là kết luận của các ánh xạ này đúng cho tất cả các phần tử mô hình nguồn thỏa mãn các giả định của chúng, tức là, `Post` đúng. Do đó, tính đúng đắn ngữ nghĩa của triển khai `I` đúng (cũng vì đây là triển khai đúng-theo-cấu-trúc).

Tính đúng đắn cú pháp của chuyển đổi (sử dụng triển khai này) nghĩa là nó được đảm bảo tạo ra các chương trình Java hợp lệ về cú pháp, thỏa mãn `ΓT`, từ các mô hình UML hợp lệ thỏa mãn `Asm`. Tính đúng đắn cú pháp theo sau từ `ΓS`, `Asm`, `Post` và `Inv`. Ví dụ, nếu có hai lớp Java khác nhau `cj1, cj2` có cùng tên trong mô hình đích, chúng phải được suy ra từ cùng một lớp UML `c` (theo `Inv1` và tính duy nhất của `name` cho các lớp UML). Nhưng `R1` kéo theo rằng `c` được ánh xạ tới một lớp Java duy nhất có tên `c.name`. Tương tự, nếu có một tình huống đa kế thừa hoặc kế thừa vòng trong mô hình đích Java, theo `Inv2` phải có một tình huống tương ứng về đa kế thừa hoặc kế thừa vòng trong mô hình UML mà nó được suy ra từ đó, mâu thuẫn với `Asm`. Những chứng minh này có thể được hình thức hóa sử dụng chứng minh nhất quán nội tại trong B (thuộc tính phân tầng không đúng cho đặc tả này, do đó một hình thức hóa trong Z3 có thể không hiệu quả cho việc chứng minh).

Tính dừng theo sau từ sự kiện rằng các tính toán của cả `R1` và `R2` đều là các phép lặp có giới hạn, trên `UMLClass` và trên `UMLClass × UMLClass` tương ứng.

Rõ ràng các lần áp dụng của `r1` độc lập với thứ tự, vì các lần áp dụng khác nhau cập nhật các mục dữ liệu hoàn toàn rời nhau. Các lần áp dụng của `r2` có thể can thiệp lẫn nhau, nếu có đa kế thừa trong mô hình UML, ví dụ, các lớp khác nhau `d1` và `d2` trong `c.generalisation.general` nào đó: chỉ một trong hai siêu lớp `d1` hoặc `d2` của `c` có thể được biểu diễn trong mô hình Java. Nhưng `Asm` đảm bảo rằng điều này không thể xảy ra. Do đó tính hợp lưu đúng.

## 10 Nghiên cứu tình huống 2: Tái biểu đạt cây thành đồ thị (Re-expression of trees as graphs)

Ví dụ này được định nghĩa trong ETL ở [28] và minh họa cách các chuyển đổi hiện có có thể được xác minh bằng các kỹ thuật của chúng tôi, bằng cách đảo ngược kỹ thuật (reverse-engineering) triển khai ETL thành một biểu diễn trong các siêu mô hình chuyển đổi của Mục 2. ETL chứa các cơ chế ngôn ngữ điển hình của các ngôn ngữ chuyển đổi lai, chẳng hạn ATL hoặc GrGen, bao gồm việc sử dụng thiết yếu các dấu vết chuyển đổi (transformation traces).

Hình 10 cho thấy các siêu mô hình nguồn `S` (bên trái) và đích `T` (bên phải) của chuyển đổi này.

*Fig. 10. Các siêu mô hình Cây (Tree) và Đồ thị (Graph)*

Mục tiêu của chuyển đổi là tái biểu đạt các cấu trúc cây dưới dạng đồ thị, với các cạnh đồ thị tường minh thay cho các liên kết từ một thể hiện cây tới cha của nó.

Một giả định `Asm0` là không có chu trình nào trong quan hệ `parent`:

```
Tree→forAll(t | t.parent→closure()→excludes(t))
```

Cũng giả định rằng mô hình đích rỗng: `Edge = Set{}` và `Node = Set{}`.

Một thuộc tính cần thiết của `ΓT` là không có cạnh trùng lặp:

```
Edge→forAll(e1 | Edge→forAll(e2 | e1.source = e2.source and e1.target = e2.target implies e1 = e2))
```

Một bất biến `Inv` có thể được phát biểu, biểu thị rằng các nút và cạnh duy nhất trong mô hình đích là những nút/cạnh được suy ra (một cách duy nhất) từ một số phần tử mô hình nguồn:

```
Node→forAll(n | Tree→exists1(t | t.label = n.label))
Edge→forAll(e | Tree→exists1(t | t.parent.size > 0 and e.source.label = t.label 
  and e.target.label = t.parent.label→any()))
```

Chuyển đổi này được triển khai trong [28] bằng cách sử dụng tra cứu dấu vết (trace lookup) và gọi quy tắc ngầm định:

```
rule Tree2Node
  transform t : Tree!Tree
  to n : Graph!Node
{
  n.label := t.label;
  if (t.parent.isDefined())
  {
    var edge := new Graph!Edge;
    edge.source := n;
    edge.target := t.parent.equivalent();
  }
}
```

Biểu thức `obj.equivalent()` tra cứu trong dấu vết chuyển đổi `Trace` để kiểm tra xem `obj` đã được ánh xạ tới một phần tử đích `tobj` chưa, nếu vậy, nó trả về phần tử đó, nếu không nó gọi bất kỳ quy tắc áp dụng được nào (trong trường hợp này, chính `Tree2Node`) để ánh xạ `obj` tới một phần tử đích, sau đó được trả về.

Do đó, ngữ nghĩa của quy tắc trên có thể được biểu thị trong ngôn ngữ hoạt động của siêu mô hình triển khai chuyển đổi của chúng ta như một hành vi:

```
Tree2Node(t : Tree, nout : Node)
  (if (Node.label->contains(t.label))
   then nout := Node[t.label]
   else
     (n : Node;
      n.label := t.label;
      if (t.parent.size > 0)
        (edge : Edge;
         edge.source := n;
         if Trace->exists( tr | tr.source = t.parent->any() )
         then
           edge.target := Trace->select( tr |
             tr.source = t.parent->any() )->collect( target )->any()
         else
           Tree2Node(t.parent->any(),edge.target)
        );
      nout := n
     )
  )
```

Điều này làm cho lời gọi đệ quy ngầm định trong mã ETL trở nên tường minh. Chúng tôi giả định rằng ngữ nghĩa kiểm-tra-trước-khi-thực-thi (check-before-enforce) được dùng cho quy tắc trên, nếu không các nút và cạnh trùng lặp có thể được tạo ra bởi các lời gọi khác nhau của `Tree2Node` hoạt động trên cùng một nhánh cây.

Mã thao tác này tạo thành các bước tính toán cho một hậu điều kiện đặc tả `Post0`:

```
Tree→forAll(t | Node.label→excludes(t.label) implies 
  (t.parent.size = 0 implies Node→exists(n | n.label = t.label)) and 
  (t.parent.size > 0 implies Node→exists(n | n.label = t.label and 
    Edge→exists(edge | edge.source = n and edge.target = Node[t.parent.label]→any()))))
```

Đây là một ràng buộc kiểu 3, với một triển khai dưới dạng phép lặp điểm bất động `stat(Post0)` lặp lại phần thân đã lượng hóa của `Post0` cho đến khi không còn cây nào chưa có nút khớp. Điều này có thể được so sánh với `Tree2Node(t, n)` của ETL, thực hiện các hành động tương ứng cho `t` và tất cả tổ tiên của `t`. Khác với `stat(Post0)`, nó sử dụng một thứ tự lặp cố định, từ con cháu tới cha. `stat(Post0)` cần tính toán ra cùng một mô hình đích như `Tree2Node` được áp dụng cho mỗi nút lá của (các) cây trong mô hình nguồn.

Để xác minh các thuộc tính của những tính toán đệ quy như vậy, có thể dùng quy nạp theo độ sâu lời gọi (induction on call depth). Tức là, giả sử rằng lời gọi `Tree2Node(t.parent→any(), edge.target)` tạo ra một đồ thị mô hình đích đúng đắn cho cấu trúc cây tại và phía trên `t.parent`, chúng ta có thể lập luận rằng `Tree2Node(t, nout)` cũng làm như vậy cho cấu trúc cây tại và phía trên `t`.

Tính dừng có thể được chỉ ra bằng cách lập luận rằng mọi lời gọi của `Tree2Node` đều dừng: bất kỳ chuỗi liên kết `parent` nào cũng phải hữu hạn vì các vòng lặp bị cấm bởi `Asm` và vì các mô hình là hữu hạn.

Tuy nhiên việc triển khai có vẻ quá phức tạp, và để tạo ra một phiên bản được cải thiện và dễ xác minh hơn của chuyển đổi này, chúng ta có thể sử dụng kỹ thuật đúng-theo-cấu-trúc của Mục 8, bắt đầu từ một đặc tả với hai ràng buộc hậu điều kiện sau, `Post1`:

```
Tree→forAll(t | Node→exists(n | n.label = t.label))
```

để liên hệ các cây với các nút, và `Post2`:

```
Tree→forAll(t | t.parent.size > 0 implies 
  Edge→exists1(e | e.source = Node[t.label] and e.target = Node[t.parent.label]→any()))
```

để liên hệ các liên kết `parent` với các cạnh. Cả hai đều là các ràng buộc kiểu 1 cục bộ hóa. Đặc tả mới này là một ví dụ về mẫu đặc tả 'Ánh xạ đối tượng trước liên kết' [38], nên được dùng trong những trường hợp cấu trúc đệ quy như vậy trong siêu mô hình nguồn. Các ràng buộc thỏa mãn thuộc tính không can thiệp cú pháp nếu được sắp xếp theo thứ tự như trên, và cả hai đều thuộc kiểu 1, thỏa mãn không can thiệp cú pháp nội tại, do đó một triển khai đúng đắn ngữ nghĩa, dừng và hợp lưu có thể được tổng hợp tự động là `stat(Post1); stat(Post2)`:

```
for t : Tree do delta1(t);
for t : Tree do delta2(t)
```

trong đó `delta1` là:

```
delta1(t : Tree)
  (n : Node;
   n.label := t.label)
```

và `delta2` là:

```
delta2(t : Tree)
  (if t.parent.size > 0
   then
     if Edge->exists( e | e.source = Node[t.label] and
                          e.target = Node[t.parent.label]->any() )
     then skip
     else
       (e : Edge;
        e.source := Node[t.label];
        e.target := Node[t.parent.label]->any()
       )
  )
```

Trong trường hợp này chúng ta có thể chứng minh rằng các thuộc tính bất biến đúng: sau bất kỳ dãy bước chuyển đổi nào, mỗi nút mô hình đích hiện có phải được suy ra từ đúng một cây mô hình nguồn, và tương tự đối với các cạnh. Các cạnh trùng lặp không thể xảy ra vì `Post` và `Inv` cùng nhau kéo theo rằng hai cạnh `e1` và `e2` có chung nút nguồn và chung nút đích, phải được suy ra từ một cây `t` duy nhất có một cha duy nhất `t1` và (từ hậu điều kiện thứ hai), do đó `e1 = e2`. Do đó tính đúng đắn cú pháp đúng.

## 11 Nghiên cứu tình huống 3: Tái cấu trúc sơ đồ lớp (Refactoring class diagrams)

Chuyển đổi cập nhật tại chỗ này hợp lý hóa một sơ đồ lớp bằng cách loại bỏ các bản sao trùng lặp của thuộc tính khỏi các lớp anh em (sibling classes) [27]. Hình 11 cho thấy siêu mô hình của ngôn ngữ duy nhất của chuyển đổi này.

*(Siêu mô hình gồm: `NamedElement` với thuộc tính `name : String`; `Generalization`, `Entity`, `Property`, `Type` với các liên kết `1`, `0..1`, `*`, các vai trò `generalisation`, `specialisation`, `general`, `specific`, `ownedAttribute`.)*

*Fig. 11. Siêu mô hình sơ đồ lớp cơ bản (Basic class diagram metamodel)*

Có ba quy tắc ánh xạ, trong đó đơn giản nhất là quy tắc 1:

*Kéo lên các thuộc tính chung của tất cả các lớp con trực tiếp:* Nếu tập hợp `g = c.specialisation.specific` của tất cả các lớp con trực tiếp của một lớp `c : Entity` có từ hai phần tử trở lên, và tất cả các lớp trong `g` đều có một thuộc tính sở hữu với cùng tên `n` và kiểu `t`, thì thêm một thuộc tính có tên và kiểu này vào `c`, và loại bỏ các bản sao khỏi mỗi phần tử của `g` (Hình 12).

*Fig. 12. Đặc tả quy tắc 1 (Rule 1 specification)*

Để chứng minh tính đúng đắn cú pháp, các thuộc tính sau cần được thiết lập cho trạng thái kết thúc của chuyển đổi:

1. Đơn kế thừa (single inheritance): `generalisation.size ≤ 1` cho mọi lớp.
2. Không có tên thuộc tính trùng lặp trong các lớp: `allAttributes→isUnique(name)` trong đó `allAttributes` được định nghĩa đệ quy là `allAttributes = ownedAttribute ∪ generalisation.general.allAttributes`.

Những ràng buộc này cũng có thể được giả định như các tiền điều kiện `Asm` của chuyển đổi. Thêm vào đó, có một hậu điều kiện `Post` rằng không nên có trường hợp thuộc tính nào thỏa mãn điều kiện áp dụng của Quy tắc 1 (Hình 12) trong trạng thái kết thúc.

Một thuộc tính bảo toàn ngữ nghĩa mức mô hình là ngữ nghĩa của mô hình đã chuyển đổi phải tương đương với ngữ nghĩa của mô hình nguồn: trong đó ngữ nghĩa là tập hợp các bộ sưu tập đối tượng khả dĩ có thể tồn tại cho các lớp lá `e : Entity` trong mô hình, tức là, nếu:

```
sem(m) = {các cấu hình đối tượng khả dĩ cho các lớp lá của m}
```

thì chúng ta cần chỉ ra `sem(m) = sem(n)`. Điều này có thể được nội tại hóa như bất biến rằng `c.allAttributes` cho mỗi lớp lá `c ∈ Entity` về cơ bản không bị thay đổi bởi các bước chuyển đổi (tên và kiểu được bảo toàn, mặc dù không phải các đối tượng `Property` chính xác), cũng không phải tập hợp các lớp lá; `Equiv1`:

```
Entity→select(e | e.specialisation.size = 0) = Entity@pre→select(e | e.specialisation@pre.size = 0)
```

và `Equiv2`:

```
Entity→forAll(e | e.specialisation.size = 0 implies e.allAttributes ≈ e.allAttributes@pre)
```

trong đó `atts1 ≈ atts2` là `atts1→forAll(p1 | atts2→exists(p2 | p2.name = p1.name and p2.type = p1.type)) and atts2→forAll(p2 | atts1→exists(p1 | p1.name = p2.name and p1.type = p2.type))`.

Triển khai GrGen.NET của quy tắc 1, từ [27], như sau:

```
rule rule1
{
  c : Class ; :SuperOf(c, g1) ; :SuperOf(c, g2) ; g1 : Class
    -:ownedAttribute-> a1 : Property -:type-> t : Type ;
  g2 : Class -:ownedAttribute-> a2 : Property ; :SameAttribute(a1, a2) ;
  negative
  {
    g3 : Class ; :SuperOf(c, g3) ; g1 ;
    negative
    {
      g3 -:ownedAttribute-> a3 : Property ; :SameAttribute(a1, a3) ;
    }
  }
  modify
  c -:ownedAttribute-> a4 : Property -:type-> t ;
  eval
  {
    a4.name = a1.name ;
  }
  exec (RemoveAttributeFromSubclasses(c, a4) ;> [createInverseEdges]) ;
}
```

`Class` được dùng thay cho `Entity` ở đây, để nhất quán với siêu mô hình UML. Trong mệnh đề `exec`, các lần áp dụng `RemoveAttributeFromSubclasses` và `createInverseEdges` được xâu chuỗi tường minh sau quy tắc chính bằng phương tiện gọi hàm.

Việc triển khai quy tắc này có thể được trừu tượng hóa thành siêu mô hình ở Hình 7 theo cách tương tự như ví dụ ETL của Mục 10:

```
rule1(c : Class)
  (if there exist g1, g2, a1, a2, t satisfying
     the guard conditions
   then
     select such g1, g2, a1, a2, t;
     (a4: Property;
      a4.type := t;
      c.ownedAttribute := c.ownedAttribute->including(a4);
      a4._name := a1._name;
      RemoveAttributeFromSubclasses(c,a4))
  )
```

Trong trường hợp này, `createInverseEdges` không có hành động nào cần thực hiện, do đó bị bỏ qua.

Để thiết lập các thuộc tính `Asm` ở trạng thái sau, một kỹ thuật, như đã mô tả ở Mục 4, là chỉ ra rằng chúng là các bất biến của chuyển đổi, tức là, chúng được bảo toàn bởi mỗi bước tính toán chuyển đổi. Chúng ta có thể hoặc chứng minh việc bảo toàn ở mức đặc tả sử dụng các đặc tả (ví dụ, sử dụng một quan hệ ánh xạ dựa trên Hình 12) của các bước, và sau đó chỉ ra tính đúng đắn ngữ nghĩa của các triển khai bước tương đối theo các đặc tả bước, hoặc chứng minh trực tiếp việc bảo toàn cho mỗi triển khai bước.

Đối với triển khai GrGen chúng tôi chọn phương án thứ hai, sử dụng biểu diễn `rule1` của việc triển khai trong siêu mô hình ở Hình 7. Vì mã `rule1` không sửa đổi `generalisation`, thuộc tính `Asm` đầu tiên được bảo toàn một cách hiển nhiên. Đối với thuộc tính thứ hai, thuộc tính mới `a4` với tên `a1.name` được đưa vào `c`, trong mệnh đề `modify`. Tuy nhiên, trong thao tác được gọi `RemoveAttributeFromSubclasses(c, a4)`, bất kỳ thuộc tính nào có cùng tên với `a4` đều bị loại bỏ khỏi mỗi lớp trong `c.specialisation.specific`. Do đó thuộc tính 2 được duy trì, vì `allAttributes` không bị sửa đổi theo cách khác cho bất kỳ lớp nào bởi việc triển khai quy tắc.

Một chứng minh hình thức cho lập luận này có thể được xây dựng bằng cách dịch các triển khai quy tắc GrGen thành các thao tác của một máy B, và biểu thị các thuộc tính như các bất biến của máy này. Chứng minh nhất quán nội tại của máy sẽ bao gồm tính bất biến của các thuộc tính qua các bước chuyển đổi.

Tính dừng theo sau vì số lượng các thể hiện `Property` trong mô hình bị giảm nghiêm ngặt bởi mỗi lần áp dụng quy tắc, tức là, `Property.allInstances()→size()` cho một giới hạn trên cho một biến thể của chuyển đổi.

Khi triển khai kết thúc, `rule1` không thể áp dụng được, tức là, không có trường hợp lớp `c` nào thỏa mãn các điều kiện áp dụng của `rule1`. Nhưng điều này kéo theo rằng không có trường hợp thuộc tính cùng tên và cùng kiểu nào trong tất cả (ít nhất 2) các lớp con trực tiếp của một lớp, như yêu cầu.

Tính hợp lưu không đúng, vì các thứ tự áp dụng khác nhau của một số quy tắc (quy tắc 2 và 3 của [27]) có thể tạo ra các mô hình cuối không đẳng cấu.

Đối với tính đúng đắn ngữ nghĩa mức mô hình, chúng ta có thể chứng minh rằng các vị từ `Equiv1` và `Equiv2` trên là bất biến. Rõ ràng chúng đúng ban đầu, và quy tắc 1 bảo toàn tập hợp các lớp lá và tổng tập hợp các cặp `(name, type)` của các thuộc tính `allAttributes` của chúng. Do đó ngữ nghĩa của mô hình được bảo toàn.

Một ví dụ về một hệ thống chuyển đổi không đồng nhất (heterogeneous) có thể là chuyển đổi của nghiên cứu tình huống 3 tiếp theo sau đó là chuyển đổi của nghiên cứu tình huống 1: tính đúng đắn ngữ nghĩa tổng thể của phép hợp thành tuần tự này sẽ theo sau từ tính đúng đắn của từng chuyển đổi riêng lẻ, và bởi việc thiết lập các tiền điều kiện của chuyển đổi UML-sang-Java bởi chuyển đổi tái cấu trúc. Tương tự, tính dừng tổng thể đúng.

## 12 Đánh giá (Evaluation)

Cách tiếp cận của chúng tôi đã được triển khai sử dụng ngôn ngữ và bộ công cụ UML-RSDS [38, 49]. Các đặc tả chuyển đổi được định nghĩa bằng các trường hợp sử dụng (use cases) UML, với các tiền điều kiện, bất biến và hậu điều kiện, trong khi các thiết kế được định nghĩa sử dụng các hoạt động trong ngôn ngữ câu lệnh được trình bày ở đây. Phân tích cú pháp được thực hiện trên các đặc tả, và những đặc tả này có thể được dịch tự động sang Z3 và B AMN để phân tích ngữ nghĩa. Các thiết kế được sinh ra từ các đặc tả sử dụng cách tiếp cận của Mục 8, mã Java thực thi được tự động tổng hợp từ các thiết kế. Do đó tất cả các bước của quy trình tổng quát ở Hình 8 đã được triển khai, ngoại trừ việc đảo ngược kỹ thuật (reverse-engineering) các chuyển đổi hiện có thành các biểu diễn độc lập với ngôn ngữ. Hiện tại chúng tôi sử dụng một quy trình thủ công để thực hiện bước này, nhưng việc tự động hóa (cho ETL và GrGen) đang được nghiên cứu.

Các kỹ thuật được định nghĩa ở đây đã được áp dụng cho nhiều trường hợp xác minh chuyển đổi. Các ví dụ bao gồm nghiên cứu tình huống tái cấu trúc sơ đồ lớp của [27], việc tính toán bao đóng bắc cầu của một quan hệ [39], một chuyển đổi di trú (migration) quy mô lớn [33], và việc cắt lát (slicing) các máy trạng thái [34]. Ví dụ trong [27] là một chuyển đổi cập nhật tại chỗ phức tạp về mặt ngữ nghĩa (quy tắc đơn giản nhất của nó được thảo luận ở Mục 11). Chúng tôi đã có thể chứng minh tính dừng, tính đúng đắn cú pháp và tính đúng đắn ngữ nghĩa cho triển khai UML-RSDS sử dụng chứng minh thủ công với nỗ lực dưới 1 ngày công. Nghiên cứu tình huống của [39] đã được chứng minh hình thức sử dụng chứng minh trong B để thiết lập tính dừng và tính hợp lưu. Điều này đòi hỏi khoảng 5 ngày công chứng minh tương tác, chủ yếu liên quan đến các nghĩa vụ tinh chỉnh để thiết lập các thuộc tính biến thể cần thiết. Ví dụ trong [33] có 66 kiểu thực thể và đặc trưng, và biểu diễn một bài toán di trú thực tế. Chúng tôi đã có thể xác định các lỗi về bảo toàn ngữ nghĩa và đúng đắn cú pháp trong ánh xạ di trú được đề xuất, và thiết lập tính dừng, tính hợp lưu và tính đúng đắn ngữ nghĩa bằng phân tích cú pháp. Nỗ lực cần thiết là khoảng 3 ngày công. Các thuật toán cắt lát máy trạng thái của [34] tạo thành một phần của một công cụ kỹ thuật phần mềm lớn và phức tạp để cắt lát mô hình. Việc bảo toàn ngữ nghĩa mức mô hình của các thuật toán cắt lát được chỉ ra bằng quy nạp trên các bước chuyển đổi riêng lẻ viết lại các máy trạng thái thành các dạng đơn giản hơn. Điều này liên quan đến khoảng 5 ngày công chứng minh thủ công.

Chúng tôi nhận thấy rằng việc tổ chức các bước chứng minh được mô tả ở Mục 4 nhìn chung rất hiệu quả trong việc thực hiện chứng minh thủ công hoặc có công cụ hỗ trợ: nỗ lực xác minh được chia nhỏ thành việc xác minh riêng biệt các bất biến và biến thể chuyển đổi, tương đối theo một triển khai đã cho, và sau đó xác minh tính đúng đắn cú pháp và ngữ nghĩa cùng bảo toàn ngữ nghĩa sử dụng các bất biến và biến thể này. Việc chứng minh tính đúng đắn cú pháp và bảo toàn ngữ nghĩa trong một số trường hợp có thể được thực hiện độc lập với các triển khai cụ thể bằng cách thay vào đó dựa vào các thuộc tính bất biến. Điều này cho phép tái sử dụng nỗ lực chứng minh, nếu triển khai bị thay đổi, với điều kiện việc triển khai đã sửa đổi cũng duy trì các bất biến.

Bảng 11 cho thấy các ví dụ về mức độ tự động hóa của chứng minh nhất quán nội tại và tinh chỉnh sử dụng B cho một số chuyển đổi. Ngay cả đối với chứng minh nhất quán nội tại, nỗ lực chứng minh cao hơn đối với các chuyển đổi (tính toán bao đóng bắc cầu, và cân bằng cây nhị phân) sử dụng các ràng buộc kiểu 2 hoặc kiểu 3, so với những chuyển đổi chỉ sử dụng các ràng buộc kiểu 1.

**Bảng 11. Mức độ tự động hóa chứng minh B trên các nghiên cứu tình huống**

| Nghiên cứu tình huống | Tổng số nghĩa vụ chứng minh | Chứng minh tự động | Chứng minh tương tác | Tỷ lệ tự động chứng minh |
|---|---|---|---|---|
| Bao đóng bắc cầu (nhất quán nội tại) | 17 | 11 | 6 | 65% |
| Bao đóng bắc cầu (tinh chỉnh) | 48 | 26 | 22 | 54% |
| Cân bằng cây nhị phân (nhất quán nội tại) | 29 | 19 | 10 | 66% |
| Cân bằng cây nhị phân (tinh chỉnh) | 47 | 27 | 20 | 57% |
| UML sang RDB (nhất quán nội tại) | 31 | 26 | 5 | 84% |
| A sang B (nhất quán nội tại) | 24 | 18 | 6 | 75% |

Để giảm thiểu nỗ lực chứng minh cần thiết cho việc xác minh, chúng tôi khuyến nghị kết hợp phân tích cú pháp, kiểm tra thỏa mãn và tổng hợp đúng-theo-cấu-trúc để phát triển các chuyển đổi mới. Điều này đòi hỏi các hạn chế về dạng của đặc tả chuyển đổi, tức là, chúng cần thỏa mãn không can thiệp cú pháp hoặc ngữ nghĩa, nhưng hầu hết các trường hợp thực tế của tinh chỉnh, di trú, tái biểu đạt và các chuyển đổi mô hình tách biệt khác có thể được định nghĩa để thỏa mãn những hạn chế này. Mẫu hội-kéo-theo (Conjunctive-implicative pattern), và các mẫu liên quan, chẳng hạn mẫu Ánh xạ đối tượng trước liên kết, được mô tả trong [38] được khuyến nghị cho việc cấu trúc hóa các đặc tả và triển khai chuyển đổi, nhằm giảm nỗ lực chứng minh. Ngược lại, cấu trúc đi-xuống-theo-đệ-quy, hoặc việc sử dụng gọi quy tắc ngầm định thông qua một cơ chế như `equivalent`/`equivalents` của ETL, làm phức tạp hóa đáng kể việc xác minh.

Ngay cả trong các trường hợp không can thiệp ngữ nghĩa không đúng, như trong nghiên cứu tình huống của Mục 11 (trong đó các lần áp dụng của quy tắc 3 có thể đưa vào các trường hợp lớp mới mà quy tắc 1 có thể áp dụng, và ngược lại), tổng hợp đúng-theo-cấu-trúc vẫn có thể được dùng để sinh ra một triển khai đúng đắn ngữ nghĩa từ đặc tả chuyển đổi [38]. Tuy nhiên, việc chứng minh thuộc tính biến thể cho các hàm biến thể được chỉ định sẽ là cần thiết để đảm bảo tính dừng, và tương tự việc chứng minh sẽ cần thiết để thiết lập tính hợp lưu, nếu nó đúng.

Các hạn chế của cách tiếp cận của chúng tôi là sự phụ thuộc vào việc sắp xếp tuần tự (serialisation) của các triển khai, để thực hiện lập luận tiền điều kiện yếu nhất, và các vấn đề về quy mô gặp phải với các triển khai chuyển đổi mức thấp quy mô lớn, chẳng hạn triển khai Kermeta trong [27], mà chúng tôi đã không thể xác minh được.

## 13 Công trình liên quan (Related work)

Trong [38] chúng tôi đã giới thiệu cách tiếp cận MT đúng-theo-cấu-trúc sử dụng UML-RSDS, và chúng tôi đã mô tả các mẫu thiết kế có thể được dùng để định nghĩa các chuyển đổi mô-đun hóa, hiệu quả và có thể xác minh. Trong [36] một cái nhìn tổng quan về các kỹ thuật xác minh cho UML-RSDS được đưa ra. Trong bài báo hiện tại, chúng tôi cung cấp các nền tảng ngữ nghĩa chi tiết cho việc xác minh MT, không đặc thù cho UML-RSDS, và định nghĩa chi tiết các kỹ thuật xác minh MT độc lập với ngôn ngữ sử dụng phân tích cú pháp, kiểm tra thỏa mãn và chứng minh định lý.

Trong [25], các siêu mô hình cho yêu cầu, đặc tả và thiết kế của các chuyển đổi mô hình được giới thiệu, cùng với một quy trình để phát triển các chuyển đổi sử dụng những ngôn ngữ này. Chúng tôi đi theo cách tiếp cận của [25], và mở rộng điều này để xử lý việc sinh ra các điều kiện xác minh từ các đặc tả chuyển đổi, và việc ánh xạ các đặc tả chuyển đổi sang các hình thức luận xác minh. Trái ngược với cách tiếp cận `transML`, chúng tôi tận dụng nhiều điểm tương đồng giữa các ngôn ngữ MT để định nghĩa một biểu diễn triển khai chuyển đổi độc lập với ngôn ngữ, nhằm tránh sự đa dạng của các siêu mô hình cho từng ngôn ngữ riêng lẻ. Ở đây chúng tôi đã tập trung vào các giai đoạn thiết kế mức cao và thiết kế mức thấp của [25]. Trong công việc tương lai chúng tôi dự định tích hợp các kỹ thuật của bài báo này với các thành phần khác của cách tiếp cận `transML` của [25].

Trong bài báo này chúng tôi chủ yếu sử dụng ý tưởng về một mô hình xác minh hoặc mô hình chuyển đổi để thực hiện phân tích ngữ nghĩa của một chuyển đổi mô hình. Bài báo [32] giới thiệu một trong những nỗ lực đầu tiên sử dụng cách tiếp cận mô hình xác minh: các đặc tả chuyển đổi quan hệ được hình thức hóa trong ngôn ngữ đặc tả B AMN, sau đó được dùng để chứng minh tính đúng đắn cú pháp của các chuyển đổi. Khái niệm mô hình xác minh được mô tả (dưới tên 'mô hình chuyển đổi') trong [8], và nhiều công việc tiếp theo về xác minh chuyển đổi đã sử dụng cách tiếp cận này. Ví dụ, [14] cho thấy cách các đặc tả QVT-R và TGG có thể được ánh xạ sang một mô hình xác minh bao gồm các công thức OCL, nắm bắt ngữ nghĩa của các đặc tả. Mô hình xác minh này khi đó có thể được phân tích sử dụng bất kỳ công cụ OCL nào. Công việc này sau đó đã được mở rộng để xem xét một tập con khai báo của ATL [12, 13]. Trái ngược với cách tiếp cận của chúng tôi, mô hình xác minh của [13] chỉ biểu thị trạng thái sau dự định của chuyển đổi, và không biểu diễn các bước chuyển đổi hay hành vi động của chuyển đổi. Do đó nó ít phù hợp hơn cho việc chứng minh các thuộc tính bất biến, tính dừng hoặc tính hợp lưu. Các thuộc tính dựa trên bất biến như bảo toàn/tương đương ngữ nghĩa mức mô hình dường như đòi hỏi việc mô hình hóa các bước chuyển đổi, chứ không chỉ đơn thuần là các trạng thái kết thúc của một chuyển đổi. Cách tiếp cận của [13] dường như bị giới hạn ở các ràng buộc kiểu 1 theo thuật ngữ của chúng tôi.

Công việc liên quan khác là [9], sử dụng một mô hình xác minh dựa trên logic viết lại (rewriting logic) để phân tích các chuyển đổi kiểu QVT, và [16], ánh xạ ATL sang một mô hình xác minh dựa trên bộ chứng minh định lý Coq. Alloy đã được dùng để phân tích các đặc tả UML và OCL và các chuyển đổi mô hình trong QVT [3, 2]. Alloy cung cấp các khả năng kiểm tra thỏa mãn có giới hạn, nhưng trong một ngôn ngữ quan hệ bị hạn chế, giới hạn các dạng đặc tả chuyển đổi có thể được phân tích. Ví dụ, các tập hợp lồng nhau không thể được biểu diễn. Các phép dịch từ các ngôn ngữ chuyển đổi mô hình sang các hình thức luận khác nhau cũng đã được dùng để thực hiện phân tích tính dừng [50, 46], chứng minh tính đúng đắn cú pháp [23], sinh phản ví dụ [13] và chứng minh bảo toàn ngữ nghĩa [40]. Bảng 12 tóm tắt các cách tiếp cận như vậy. Có thể thấy rằng những cách tiếp cận này chủ yếu xử lý các ngôn ngữ chuyển đổi khai báo, và thường bị giới hạn ở các tập con hạn chế của chúng và ở các thuộc tính xác minh cụ thể.

**Bảng 12. Các cách tiếp cận mô hình xác minh**

| Tác giả | Ngôn ngữ chuyển đổi | Hình thức luận | Phân tích | Ánh xạ | Kết quả |
|---|---|---|---|---|---|
| Asztalos et al. [4] | VMTS | MCDL, MCIL | Tính đúng đắn ngữ nghĩa | Tự động | Chứng minh tự động rằng triển khai đạt được các hậu điều kiện yêu cầu |
| Becker et al. [6, 7] | Chuyển đổi đồ thị | Bộ kiểm tra ký hiệu (symbolic verifier) | Tránh các trạng thái không hợp lệ | Tự động | Chứng minh/phản ví dụ về tính bất biến |
| Boronat et al. [9] | Tập con QVT-R | Maude | Chứng minh bất biến, phản ví dụ | Thủ công | Chứng minh bất biến từng phần, sinh phản ví dụ |
| Buttner et al. [13] | ATL khai báo | OCL, Alloy | Tính đúng đắn cú pháp (phản ví dụ) | Tự động | Sinh phản ví dụ từng phần cho tính đúng đắn cú pháp của ATL khai báo |
| Calegari et al. [16] | Tập con ATL | CIC, Coq | Tính đúng đắn cú pháp | Thủ công | Chứng minh tương tác về tính đúng đắn cú pháp |
| Giese et al. [20] | TGG | Isabelle/HOL | Tương đương ngữ nghĩa mức mô hình | Thủ công | Chứng minh thủ công về tương đương ngữ nghĩa |
| Inaba et al. [23] | Tập con UnCAL + chú thích | Logic đơn điệu (monadic) bậc hai | Tính đúng đắn cú pháp, sinh phản ví dụ | Tự động | Thủ tục quyết định tự động cho tính đúng đắn cú pháp của các chuyển đổi UnCAL hạn chế |
| Massoni et al. [40] | không | Alloy, PVS | Sinh ví dụ, chứng minh | Thủ công, hạn chế | Chứng minh các tái cấu trúc UML đơn giản bảo toàn ngữ nghĩa |
| Rensink et al. [46] | GXL checkVML | Promela, SPIN | Tính bất biến, tính dừng | Tự động | Kiểm tra mô hình có giới hạn |
| GROOVE | Hệ chuyển trạng thái GXL | | Tính bất biến, tính dừng | Tự động | Kiểm tra mô hình có giới hạn |
| Stenzel et al. [48] | QVT-O | KIV | Tính đúng đắn cú pháp, bảo toàn ngữ nghĩa mức mô hình | Thủ công | Chứng minh tương tác về tính đúng đắn cú pháp, bảo toàn ngữ nghĩa mức mô hình |
| Varro et al. [50] | Các chuyển đổi đồ thị với NAC | Mạng Petri (không chính xác) | Tính dừng | Thủ công | Phân tích tính dừng từng phần của các chuyển đổi đồ thị ngữ nghĩa |

Trong bài báo này chúng tôi mở rộng khái niệm mô hình xác minh để bao quát tất cả các thành phần của một ngôn ngữ chuyển đổi thực tế (UML-RSDS), và để bao gồm các ngôn ngữ chuyển đổi mô hình lai và mệnh lệnh. Chúng tôi biểu diễn các chuyển đổi từ nhiều ngôn ngữ chuyển đổi trong một biểu diễn chung và sử dụng các ánh xạ từ những siêu mô hình này của các đặc tả và triển khai chuyển đổi sang các mô hình xác minh trong các hình thức luận khác nhau (như B, Z3, v.v.) để hỗ trợ việc xác minh một loạt các thuộc tính xác minh. Điều này cho phép phân tích các chuyển đổi được biểu thị trong một phạm vi rộng các ngôn ngữ chuyển đổi, và của các hệ thống chuyển đổi liên quan đến nhiều ngôn ngữ chuyển đổi. Trái ngược với [13], biểu diễn của chúng tôi về các chuyển đổi bao gồm các chi tiết hành vi (Hình 7), cho phép chúng tôi biểu diễn các chuyển đổi lai và mệnh lệnh, và lập luận về các lần thực thi chuyển đổi sử dụng quy nạp trên các bước tính toán.

Chúng tôi cũng đã đưa ra các kỹ thuật xác minh độc lập với ngôn ngữ chi tiết, và chúng tôi đã định nghĩa các tiêu chí mà các ánh xạ ngữ nghĩa tới các hình thức luận xác minh nên lý tưởng thỏa mãn, tức là, chúng nên là các đồng cấu ngược định chế (institution comorphisms). Các định chế (institutions) và đồng cấu ngược định chế được dùng làm cơ sở để hỗ trợ việc sử dụng nhiều khung logic trong môi trường HETS [41]. Có thể xây dựng các đồng cấu như vậy dựa trên các ánh xạ của chúng tôi tới Z3 và B AMN, những đồng cấu này thỏa mãn chiều đúng đắn (soundness) của thuộc tính đồng cấu ngược (rằng tính hợp lệ của một thuộc tính đã dịch trong mô hình xác minh kéo theo tính hợp lệ của thuộc tính đó trong biểu diễn OCL/FOL gốc), nhưng không phải chiều ngược lại, do tính không đầy đủ của các hình thức luận Z3 và B.

Tính đúng đắn ngữ nghĩa mức mô hình (còn được gọi là bảo toàn ngữ nghĩa mức mô hình [35]), tức là, việc bảo toàn ngữ nghĩa nội tại của các mô hình bởi một chuyển đổi, được xem xét cụ thể bởi một số công trình. Bài báo [48] xem xét thuộc tính xác minh này cho các chuyển đổi QVT-O, và sử dụng một hình thức luận dựa trên logic động (dynamic logic) để xác minh rằng một số thuộc tính ngữ nghĩa nhất định của các mô hình nguồn được bảo toàn trong các mô hình đích. Cách tiếp cận của chúng tôi có khả năng tạo thuận lợi cho việc xác minh như vậy, vì các vị từ `Post` và `Inv` của một chuyển đổi `τ : S → T` biểu thị chính xác cách một mô hình đích `n` liên hệ với nguồn `m` của nó. Một diễn giải mức ngôn ngữ `χ` cũng biểu thị cách các phần tử ngôn ngữ của `S` có thể biểu đạt được theo `T`. Ánh xạ suy ra `Mod(χ)` của các mô hình hỗ trợ phân tích việc bảo toàn ngữ nghĩa của các thuộc tính mức mô hình tĩnh tương đối theo `χ`, và việc chứng minh hình thức về việc bảo toàn như vậy có thể được thực hiện bằng chứng minh quy nạp sử dụng biểu diễn B của các chuyển đổi, với điều kiện ngữ nghĩa có thể biểu diễn được trong B [39]. Khái niệm về một bất biến chuyển đổi có thể áp dụng cho việc chứng minh bảo toàn ngữ nghĩa mức mô hình, tức là, một bất biến có thể biểu thị rằng bảo toàn ngữ nghĩa đúng cho tất cả các phần tử đích được tạo ra cho tới một giai đoạn trung gian tùy ý của chuyển đổi, hoặc cho tất cả các cấu trúc lại của mô hình đã được thực hiện cho tới thời điểm đó — trong mỗi trường hợp đây là các quy nạp trên các bước chuyển đổi. Một nỗ lực sử dụng lập luận dựa trên bất biến như vậy được thực hiện trong [48], tuy nhiên điều này bị phức tạp hóa bởi phong cách triển khai đi-xuống-theo-đệ-quy được dùng cho chuyển đổi, dẫn đến một bất biến phức tạp và nhiệm vụ chứng minh phức tạp. Cách tiếp cận của [48] dựa vào một cây phân cấp hợp thành nghiêm ngặt trong các mô hình, điều mà chúng tôi không yêu cầu cho lập luận dựa trên bất biến. Bài báo [1] cũng xem xét việc bảo toàn ngữ nghĩa mức mô hình, cho một chuyển đổi sinh mã. Chứng minh không được sử dụng, thay vào đó kiểm tra mô hình được dùng để xác nhận rằng các thuộc tính yêu cầu được bảo toàn cho các mô hình cụ thể. Tương tự, trong [42, 43] việc bảo toàn các thuộc tính ngữ nghĩa trên cơ sở từng mô hình được xác minh bằng cách sử dụng một sự tương ứng cấu trúc (một bisimulation) giữa các mô hình nguồn và đích. Một cách tiếp cận dựa trên bất biến được dùng để xác minh tương đương ngữ nghĩa mức mô hình trong [20], tuy nhiên họ sử dụng chứng minh thủ công trong Isabelle/HOL để chỉ ra tính bất biến của tương đương ngữ nghĩa dưới các bước chuyển đổi, trong khi một hình thức hóa sử dụng B có khả năng tự động hóa nhiều hơn nỗ lực chứng minh.

> **Giải thích:** "Bisimulation" (mô phỏng song song hai chiều) là một khái niệm trong lý thuyết hệ thống chuyển trạng thái, dùng để kiểm tra hai hệ thống (ở đây là mô hình nguồn và mô hình đích của một chuyển đổi) có "hành xử giống hệt nhau" từ góc nhìn bên ngoài hay không, dù cấu trúc bên trong có thể khác nhau. Nếu tồn tại một bisimulation giữa hai mô hình, ta có thể coi chúng tương đương về mặt ngữ nghĩa hành vi.

Đã có nhiều công trình đáng kể về việc hình thức hóa OCL và UML để phân tích ngữ nghĩa [2, 10, 11, 47]. Độ phức tạp của việc mô hình hóa `null` và `invalid` của OCL, cùng với những điểm không nhất quán trong các định nghĩa ngữ nghĩa OCL của các giá trị này, có nghĩa là các hệ thống như [11] phải đưa ra các giả định bổ sung để cung cấp một khung lập luận cho OCL đầy đủ. Thay vào đó, chúng tôi chọn loại bỏ hoàn toàn những giá trị như vậy và làm việc với logic cổ điển, có ưu điểm là không mơ hồ và sự tồn tại của nhiều công cụ chứng minh và phân tích mạnh mẽ. Chúng tôi đồng ý với [11] rằng `invalid` của OCL không nên được dùng cho việc mô hình hóa, nhưng chúng tôi sẽ đi xa hơn và cấm cả việc sử dụng `null`. Bằng cách coi các đầu liên kết có số lượng `0..1` là có giá trị tập hợp (kích thước 0 hoặc 1), một cách xử lý đơn giản và thống nhất cho nhiều thuộc tính cấu trúc dữ liệu có thể được đưa ra, mà không cần kiểm tra giá trị `null`.

OCL ban đầu được dự định như một ngôn ngữ để lượng giá biểu thức logic, để biểu thị các ràng buộc khai báo của các mô hình UML. Tuy nhiên, các ngôn ngữ chuyển đổi như QVT và Kermeta giờ đây sử dụng OCL để định nghĩa các hiệu ứng thực thi được, để cập nhật các mô hình. Việc sử dụng mệnh lệnh của OCL như một ngôn ngữ lập trình đưa ra các vấn đề ngữ nghĩa, ví dụ, một `forAll` hay phép lặp khác nên hành xử như thế nào nếu (về mặt logic) việc lượng giá của nó có thể dừng trước khi tất cả các phần tử được xử lý, trong khi (về mặt mệnh lệnh) một số hành vi hiệu ứng phụ dự định vẫn có thể phát sinh nếu các phần tử bổ sung được xem xét. Chúng tôi loại trừ những trường hợp như vậy bằng cách phân biệt rõ ràng việc sử dụng logic và mệnh lệnh của OCL. Bảng 10 định nghĩa chính xác khi nào một biểu thức `E` được diễn giải theo kiểu mệnh lệnh, tức là, như `stat(E)`. Chúng tôi loại trừ các hiệu ứng phụ khi một biểu thức được dùng theo kiểu logic. Do đó việc lượng giá logic của các iterator có thể được thực hiện hiệu quả hơn. Tuy nhiên, trong một diễn giải mệnh lệnh `stat(E)` của biểu thức `E`, việc tính toán chỉ dừng khi `E` được thiết lập (có thể đòi hỏi phép lặp điểm bất động, v.v.).

Ví dụ, việc lượng giá logic của `s→forAll(x | x.att = v)` có thể trả về `false` ngay khi tìm thấy một `x ∈ s` với `x.att ≠ v`, và không có cập nhật nào được thực hiện. Nhưng `stat(s→forAll(x | x.att = v))` là `for x : s do x.att := v` và luôn lặp hoàn toàn qua tất cả các phần tử của `s`, gán `v` cho `x.att` cho mỗi `x ∈ s`. Các diễn giải logic và mệnh lệnh được liên hệ một cách tự nhiên bởi thuộc tính:

```
def(E) ⇒ [stat(E)]E
```

Mối quan hệ này cũng tạo thành cơ sở cho việc đảo ngược kỹ thuật (reverse-engineering) mã chuyển đổi hiện có trong các ngôn ngữ lai hoặc mệnh lệnh thành các đặc tả.

## Kết luận (Conclusions)

Chúng tôi đã chỉ ra cách một khung làm việc có hệ thống, độc lập với ngôn ngữ và các kỹ thuật cho việc xác minh chuyển đổi mô hình có thể được đưa ra, và chúng tôi đã minh họa việc sử dụng các kỹ thuật này trên các nghiên cứu tình huống tiêu biểu của các loại chuyển đổi khác nhau. Một lợi ích đáng kể của việc mô hình hóa hình thức các đặc tả, triển khai và thuộc tính xác minh chuyển đổi, là việc ánh xạ những thứ này sang các hình thức luận xác minh như B hay Z3 có thể được tự động hóa. Những ánh xạ như vậy đã được tích hợp vào các công cụ UML-RSDS [49].

Chúng tôi đã chỉ ra các vấn đề nảy sinh liên quan đến việc xác minh nếu các triển khai chuyển đổi sử dụng các kỹ thuật như đi-xuống-theo-đệ-quy hoặc gọi quy tắc ngầm định. Do đó chúng tôi khuyến nghị rằng các chuyển đổi nên được cấu trúc theo các mẫu như dạng Hội-kéo-theo và Ánh xạ đối tượng trước liên kết để làm cho việc xác minh khả thi.

## Lời cảm ơn (Acknowledgements)

Richard Paige của Đại học York và Steffen Zschaler của King's College London đã đóng góp vào các ý tưởng được trình bày ở đây. Đặc tả ETL được trình bày ở Mục 10 là của Kolovos et al., và xuất hiện trong [28]. Đặc tả GrGen được trình bày ở Mục 11 là của Pieter Van Gorp và xuất hiện trong [27].

## Tài liệu tham khảo (References)

1. L. Ab Rahim, J. Whittle, *Verifying semantic conformance of state machine-to-Java code generators*, MODELS 2010, LNCS, 2010.
2. K. Anastasakis, B. Bordbar, J. Kuster, *Analysis of Model Transformations via Alloy*, Modevva 2007.
3. K. Anastasakis, B. Bordbar, G. Georg, I. Ray, *On challenges of model transformation from UML to Alloy*, Software Systems Modelling, vol. 9, no. 1, 2010.
4. M. Asztalos, P. Ekler, L. Lengyel, T. Levendovszky, G. Mezei, T. Meszaros, *Automated verification by declarative description of graph rewriting-based model transformations*, MPM 2010.
5. T. Baar, *The definition of transitive closure in OCL: limitations and applications*, EPFL, Switzerland.
6. B. Becker, D. Beyer, H. Giese, F. Klein, D. Schilling, *Symbolic invariant verification for systems with dynamic structural adaption*, ICSE 2006, ACM Press.
7. B. Becker, L. Lambers, J. Dyck, S. Birth, H. Giese, *Iterative development of consistency-preserving rule-based refactorings*, ICMT 2011, LNCS vol. 6707, 2011.
8. J. Bezivin, F. Buttner, M. Gogolla, F. Jouault, I. Kurtev, A. Lindow, *Model Transformations? Transformation Models!*, ATLAS group, University of Nantes, 2006.
9. A. Boronat, R. Heckel, J. Meseguer, *Rewriting logic semantics and verification of model transformations*, FASE 2009, pp. 18–33, 2009.
10. A. Brucker, B. Wolff, *The HOL-OCL book*, Technical report 525, ETH Zurich, 2006.
11. A. Brucker, M. Krieger, B. Wolff, *Extending OCL with null-references*, MODELS 2009 Workshops, LNCS 6002, pp. 261–275, 2010.
12. F. Buttner, J. Cabot, M. Gogolla, *On validation of ATL transformation rules by transformation models*, MoDeVVa 2011.
13. F. Buttner, M. Egea, J. Cabot, M. Gogolla, *Verification of ATL transformations using transformation models and model finders*, ICFEM 2012.
14. J. Cabot, R. Clariso, E. Guerra, J. De Lara, *Verification and Validation of Declarative Model-to-Model Transformations Through Invariants*, Journal of Systems and Software, 2010.
15. J. Cabot, R. Clariso, D. Riera, *UMLtoCSP: a tool for the verification of UML/OCL models using constraint programming*, Automated Software Engineering '07, pp. 547–548, ACM Press, 2007.
16. D. Calegari, C. Luna, N. Szasz, L. Tasistro, *A type-theoretic framework for certified model transformations*, in FM 2011, LNCS vol. 6527, pp. 112–127, 2011.
17. Drey, Z., Faucher, C., Fleurey, F., Mahe, V., Vojtisek, D., *Kermeta Language Reference Manual*, https://www.kermeta.org/docs/KerMeta-Manual.pdf, April, 2009.
18. H. Ehrig, K. Ehrig, C. Ermel, F. Hermann, G. Taentzer, *Information preserving bidirectional model transformations*, FASE 2007, pp. 72–86, 2007.
19. FAA, DO-178C, *Software considerations in airborne systems and equipment certification*, January 2012.
20. H. Giese, S. Glesner, J. Leitner, W. Shafer, R. Wagner, *Towards verified model transformations*, proceedings of 3rd international workshop on model-driven engineering, verification and validation (MODEVVA), 2006.
21. J. Goguen, R. Burstall, *Institutions: abstract model theory for specification and programming*, Journal of the ACM, 39: 95–146, 1992.
22. F. Hermann, H. Ehrig, F. Orejas, K. Czarnecki, Z. Diskin, Y. Xiong, *Correctness of model synchronisation based on Triple Graph Grammars*, MODELS 2011, LNCS vol. 6981, pp. 748–752, Springer-Verlag, 2011.
23. K. Inaba, S. Hidaka, Z. Hu, H. Kato, K. Nakano, *Graph-transformation verification using monadic second-order logic*, PDPP '11, 2011.
24. F. Jouault, I. Kurtev, *Transforming Models with ATL*, in MoDELS 2005, LNCS Vol. 3844, pp. 128–138, Springer-Verlag, 2006.
25. E. Guerra, J. de Lara, D. S. Kolovos, R. F. Paige, O. Marchi dos Santos, *transML: A Family of Languages to Model Model Transformations*, MODELS 2010, pages 106–120, Springer-Verlag, LNCS volume 6394, 2010.
26. E. Jakumeit, S. Buchwald, M. Kroll, *GrGen.NET: the expressive, convenient and fast graph rewrite system*, International Journal on Software Tools for Technology Transfer (STTT), 12: 263–271, 2010.
27. S. Kolahdouz-Rahimi, K. Lano, S. Pillay, J. Troya, P. Van Gorp, *Goal-oriented measurement of model transformation methods*, submitted to Science of Computer Programming, 2012.
28. D. S. Kolovos and R. F. Paige and F. Polack, *The Epsilon Transformation Language*, ICMT, 2008, pp. 46–60.
29. M. Kuhlmann, M. Gogolla, *From UML and OCL to relational logic and back*, MODELS 2012, Springer LNCS, vol. 7590, 2012.
30. J. Kuster, *Definition and validation of model transformations*, SoSyM vol. 5, no. 3, pp. 233–259, 2006.
31. K. Lano, *The B Language and Method*, Springer-Verlag, 1996.
32. K. Lano, *Using B to Verify UML Transformations*, MODEVA 06, 2006.
33. K. Lano, S. Kolahdouz-Rahimi, *Migration case study using UML-RSDS*, TTC 2010, Malaga, Spain, July 2010.
34. K. Lano, S. Kolahdouz-Rahimi, *Slicing techniques for UML models*, Journal of Object Technology, vol. 10, 2011.
35. K. Lano, S. Kolahdouz-Rahimi, I. Poernomo, *Comparative evaluation of model transformation specification approaches*, International Journal of Software Informatics, Vol. 6, Issue 2, 2012.
36. K. Lano, S. Kolahdouz-Rahimi, T. Clark, *Comparison of model transformation verification approaches*, Modevva workshop, MODELS 2012.
37. K. Lano, S. Kolahdouz-Rahimi, *Model-driven development of model transformations*, ICMT 2011, 2011.
38. K. Lano, S. Kolahdouz-Rahimi, *Constraint-based specification of model transformations*, Journal of Systems and Software, to appear, 2012.
39. K. Lano, S. Kolahdouz-Rahimi, T. Clark, *Verification of model transformations*, Dept. of Informatics, King's College London, 2012.
40. T. Massoni, R. Gheyi, P. Borba, *Formal refactoring for UML class diagrams*, 19th Brazilian symposium on Software Engineering, 2005.
41. T. Mossakowski, C. Maeder, K. Luttich, *The Heterogeneous Tool Set*, University of Bremen, Germany, 2012.
42. A. Narayanan, G. Karsai, *Towards verifying model transformations*, GT-VMT 2006, ENTCS, 2006.
43. A. Narayanan, G. Karsai, *Verifying model transformations by structural correspondence*, GT-VMT 2008.
44. OMG, *Object Constraint Language v2.3.1 Specification*, formal/2012-01-02, 2012.
45. I. Poernomo, J. Terrell, *Correct-by-construction Model Transformations from Spanning tree specifications in Coq*, ICFEM 2010.
46. A. Rensink, A. Schmidt, D. Varro, *Model checking graph transformations: A comparison of two approaches*, ICGT 2004, LNCS vol. 3256, 2004.
47. M. Soeken, R. Wille, R. Dreschsler, *Encoding OCL data types for SAT-based verification of UML/OCL models*, University of Bremen, 2012.
48. K. Stenzel, N. Moebius, W. Reif, *Formal verification of QVT transformations for code generation*, MODELS 2011, Springer LNCS vol. 6981, 2011.
49. *UML-RSDS toolset and manual*, http://www.dcs.kcl.ac.uk/staff/kcl/uml2web/, 2013.
50. D. Varro, S. Varro-Gyapay, H. Ehrig, U. Prange, G. Taentzer, *Termination analysis of model transformations by Petri Nets*, ICGT 2006, LNCS vol. 4178, 2006.
51. *Z3 Theorem Prover*, http://research.microsoft.com/en-us/um/redmond/projects/z3/, 2012.

## Phụ lục A: Đẳng cấu cấu trúc (Structure isomorphism)

Như đã mô tả ở Mục 2, một cấu trúc `m` cho một ngôn ngữ `L` có thể được xem là một bộ `((E1m, ..., Ekm), (fm1, ..., fml))` gồm các tập hợp `Eim` các thể hiện của mỗi kiểu thực thể `Ei` của `L`, và các ánh xạ `fmj : Eim → Typ` biểu diễn các giá trị của các đặc trưng dữ liệu của những kiểu thực thể này.

Các cấu trúc được coi là đẳng cấu nếu chúng không thể phân biệt được dựa trên các giá trị đặc trưng. Gọi `hi : Eim → Eim′` là một họ các song ánh (bijections) giữa các tập hợp thể hiện kiểu thực thể cho hai cấu trúc `m` và `m′` của cùng một ngôn ngữ `L`. Khi đó `m` và `m′` là đẳng cấu, `m ≃ m′`, nếu:

1. `hi(x) = x′ ⇒ fmj(x) = fm′j(x′)` cho mỗi đặc trưng thuộc tính `fj` của `Ei`, `x ∈ Eim`.
2. `hi(x) = x′ ⇒ hk(fj(x)) = fm′j(x′)` cho mỗi đặc trưng vai trò đơn trị `fj : Ei → Ek` của `Ei`, `x ∈ Eim`.
3. `hi(x) = x′ ⇒ hk(|fj(x)|) = fm′j(x′)` cho mỗi đặc trưng vai trò có giá trị tập hợp `fj : Ei → Set(Ek)` của `Ei`, `x ∈ Eim`.
4. `hi(x) = x′ ⇒ fj(x); hk = fm′j(x′)` cho mỗi đặc trưng vai trò có giá trị dãy `fj : Ei → Sequence(Ek)` của `Ei`, `x ∈ Eim`.

Điều này có hệ quả là `m` và `m′` thỏa mãn cùng các câu của `Sen(L)`.

> **Giải thích:** "Đẳng cấu cấu trúc" ở đây có nghĩa là hai mô hình cụ thể có thể trông "khác nhau về mặt định danh đối tượng" (ví dụ đối tượng có ID khác nhau) nhưng về bản chất là "giống hệt nhau" nếu ta có thể tìm được một cách ánh xạ song ánh (đổi tên đối tượng) để biến cấu trúc này thành cấu trúc kia mà vẫn giữ nguyên mọi giá trị thuộc tính và liên kết. Đây là lý do vì sao trong suốt bài báo, các khẳng định về tính hợp lưu (confluence) chỉ yêu cầu trạng thái cuối là duy nhất "sai khác đẳng cấu" — tức là duy nhất về bản chất, không nhất thiết duy nhất theo từng định danh đối tượng cụ thể.

## Phụ lục B: Ký hiệu và nền tảng logic (Notations and logical foundations)

Trong bài báo này chúng tôi sử dụng một số ký hiệu hình thức khác nhau: bên trong các chuyển đổi và các ngôn ngữ đầu vào, đầu ra của chúng `L`, chúng tôi sử dụng một ký hiệu kiểu-OCL, ví dụ:

```
A→forAll(a | a.x > 0)
```

Tuy nhiên bằng ánh xạ ngữ nghĩa của một ngôn ngữ `L` sang một ngôn ngữ lý thuyết tập hợp bậc nhất (FOL) `LL`, các ràng buộc như vậy có thể được xem đơn giản là một cú pháp thay thế cho các công thức logic thông thường, ví dụ:

```
∀a : A · x(a) > 0
```

Những ký hiệu thay thế này không có sự phân biệt về ngữ nghĩa. Tương tự chúng tôi coi khái niệm 'mô hình' thông thường của chuyển đổi mô hình, tức là, một thể hiện của một ngôn ngữ mô hình hóa được định nghĩa bởi một siêu mô hình, tương đương với khái niệm FOL về một mô hình toán học và diễn giải cho một lý thuyết FOL. Khác với [5], chúng tôi coi rằng các mô hình ngầm định là vô hạn. Các mô hình có các diễn giải hữu hạn cho tất cả các kiểu thực thể, nhưng phụ thuộc vào lý thuyết tập hợp hữu hạn và cũng phụ thuộc vào các tập hợp vô hạn như các diễn giải của tập hợp số nguyên. Do đó ngay cả cấu trúc `∅` cho một ngôn ngữ cũng là vô hạn. Khái niệm về một cấu trúc, như một diễn giải cho các ký hiệu của một ngôn ngữ mà không nhất thiết thỏa mãn tất cả các ràng buộc ngôn ngữ, cũng được coi là tương đương cho OCL và FOL.

Chúng tôi cũng sử dụng ký hiệu FOL cho lập luận và định nghĩa siêu logic (metalogical).

Định lý Đầy đủ Gödel (Godel Completeness Theorem) đúng cho lý thuyết tập hợp bậc nhất: mọi tập hợp nhất quán các câu của `LL` đều có một mô hình (sẽ là vô hạn, vì mọi mô hình đều chứa một diễn giải của `N`). Do đó nếu một thuộc tính `φ` hợp lệ trong tất cả các mô hình của một lý thuyết nhất quán `ΓL`, nó phải chứng minh được từ `ΓL`.

> **Giải thích:** Định lý đầy đủ Gödel (khác với định lý bất toàn — incompleteness — nổi tiếng hơn của Gödel) nói rằng trong logic bậc nhất, nếu một công thức đúng trong mọi mô hình thỏa mãn một tập tiên đề, thì công thức đó chắc chắn có thể được chứng minh bằng các quy tắc suy diễn hình thức từ tập tiên đề đó — tức là logic bậc nhất "đủ mạnh" để chứng minh mọi điều đúng về mặt ngữ nghĩa.

Z3 và B AMN có các ký hiệu khác biệt cho logic và lý thuyết tập hợp. Chỉ một tập con của các ký hiệu OCL/FOL có thể được biểu thị theo cách tương đương về ngữ nghĩa trong Z3 và B AMN, và chúng tôi đã xác định rõ ràng trong các Mục 6 và 7 nơi những vấn đề này phát sinh. Đối với Z3, các kiểu và toán tử số có thể được coi là tương đương với các dạng OCL/FOL, ví dụ, `Int` của Z3 biểu thị `Integer` của OCL và `Z` của FOL. Cú pháp Z3 `(forall ((a A)) (> (x a) 0))` biểu thị tương đương ràng buộc ví dụ. Tuy nhiên, các tập hợp OCL được mô hình hóa bằng danh sách Z3, do đó các toán tử như `→including()` trên tập hợp cần được mã hóa bằng các biểu thức điều kiện, để tránh nhiều bản sao của các phần tử trong danh sách. Chuỗi được mã hóa như các phần tử nguyên tử hoặc như các danh sách số nguyên. Quan hệ kiểu con không thể được biểu diễn trực tiếp. Quan hệ khả chứng minh (provability) `⊢Z3` trong Z3 bị hạn chế hơn `⊢` cho FOL.

Trong B, sự khác biệt ngữ nghĩa then chốt so với OCL/FOL là tính hữu hạn của `INT` và `Object OBJ`, và việc thiếu biểu diễn cho số thực. Do đó các giá trị số nằm ngoài phạm vi của `INT` không có ký hiệu biểu thị (denotation) trong B AMN và phải tránh dùng trong chuyển đổi đang được phân tích.

Ràng buộc trong ký hiệu B là:

```
!a.(a : A => x(a) > 0)
```

Để đạt được sự hội tụ ngữ nghĩa giữa OCL/FOL và B AMN, có thể sử dụng một lý thuyết tập hợp hữu hạn (finitary set theory) cho cái trước. Trong phiên bản này của lý thuyết tập hợp (lý thuyết tập hợp ZF với tiên đề vô hạn được thay bằng phủ định của nó), tất cả các tập hợp đều hữu hạn. Các mô hình chuẩn của một lý thuyết tập hợp như vậy là những mô hình dựa trên tập hợp `Vω` của các tập hợp hữu hạn di truyền (hereditarily finite sets): do đó bản thân các mô hình vẫn là vô hạn. Tính đầy đủ đúng cho lý thuyết tập hợp hữu hạn.

Trong UML-RSDS chúng tôi sử dụng `int` và `double` trong ngôn ngữ đặc tả để chỉ việc sử dụng các kiểu số có giới hạn. Đối với các thuộc tính và giá trị của những kiểu này, cần thêm các mệnh đề xác định giá trị, ví dụ: `def(e)` bao gồm điều kiện `−2^31 + 2 ≤ e and e ≤ 2^31 − 2` cho các biểu thức `e` mà giá trị của chúng cần nằm trong `int`. Tương tự, trước khi tạo một đối tượng, cần thực hiện một số kiểm tra rằng có đủ tài nguyên để hoàn thành việc tạo đối tượng.


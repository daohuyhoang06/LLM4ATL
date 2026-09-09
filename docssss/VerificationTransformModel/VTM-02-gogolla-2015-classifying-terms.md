# Sử dụng Thuật ngữ Phân loại (Classifying Terms) để Kiểm thử các Chuyển đổi Mô hình — Employing Classifying Terms for Testing Model Transformations

**Tác giả:** Martin Gogolla, Antonio Vallecillo, Loli Burgueño, Frank Hilken
**Năm:** 2015 (MODELS)
**Nguồn:** NotebookLM notebook "model tranformation verification"
**Loại tài liệu:** Bản dịch sát nghĩa (đầy đủ, không tóm tắt) — do AI dịch, kèm chú thích giải nghĩa cho đoạn khó.

---

**Martin Gogolla** — Đại học Bremen, Bremen, Đức — gogolla@informatik.uni-bremen.de

**Antonio Vallecillo** — Đại học Málaga, Málaga, Tây Ban Nha — av@lcc.uma.es

**Loli Burgueño** — Đại học Málaga, Málaga, Tây Ban Nha — loli@lcc.uma.es

**Frank Hilken** — Đại học Bremen, Bremen, Đức — fhilken@informatik.uni-bremen.de

## Tóm tắt (Abstract)

Bài báo này đề xuất một kỹ thuật mới để phát triển các ca kiểm thử (test case) cho các mô hình UML và OCL. Kỹ thuật này dựa trên một phương pháp tự động xây dựng các mô hình đối tượng (object model) cho các mô hình lớp (class model) được bổ sung bởi các ràng buộc OCL. Bằng cách định hướng quá trình xây dựng thông qua cái gọi là "thuật ngữ phân loại" (classifying term), các ca kiểm thử được xây dựng dưới dạng mô hình đối tượng sẽ được phân loại thành các lớp tương đương (equivalence class). Một thuật ngữ phân loại có thể là bất kỳ biểu thức OCL nào trên mô hình lớp, tính toán ra một giá trị đặc trưng (characteristic value) cho một mô hình đối tượng. Từ mỗi lớp tương đương của các mô hình đối tượng có cùng giá trị đặc trưng, một đại diện (representative) được chọn ra. Các ca kiểm thử được xây dựng có sự khác biệt đáng kể với nhau xét theo thuật ngữ phân loại đã chọn. Bằng cách xây dựng một số ít các mô hình đối tượng đa dạng, các thuộc tính của mô hình UML và OCL có thể được khảo sát một cách hiệu quả. Kỹ thuật này được áp dụng để tự động xây dựng các ca kiểm thử mô hình nguồn (source model test case) có liên quan cho các chuyển đổi mô hình (model transformation) giữa một siêu mô hình nguồn (source metamodel) và một siêu mô hình đích (target metamodel).

> **Giải thích:** Bài báo giải quyết bài toán: khi kiểm thử một chương trình "chuyển đổi mô hình" (model transformation — ví dụ chuyển từ mô hình UML sang một định dạng khác), ta cần chọn ra một tập nhỏ các mô hình đầu vào "đại diện" thay vì thử tất cả các mô hình có thể (là vô số hoặc rất nhiều). Ý tưởng cốt lõi: định nghĩa một "thuật ngữ phân loại" — một biểu thức OCL (ngôn ngữ ràng buộc dùng kèm UML) — tính ra một con số hoặc giá trị đúng/sai đặc trưng cho mỗi mô hình đối tượng. Hai mô hình cho cùng giá trị được xem là "tương đương" (thuộc cùng một equivalence class — lớp tương đương), và ta chỉ cần giữ lại một đại diện của mỗi lớp để làm ca kiểm thử.

## I. GIỚI THIỆU (INTRODUCTION)

Khi độ phức tạp của các chuyển đổi mô hình ngày càng tăng, nhu cầu sở hữu các kỹ thuật kiểm thử mạnh mẽ và chính xác hơn cũng ngày càng lớn. Một khía cạnh thiết yếu của việc kiểm thử chuyển đổi mô hình (và nói chung, của kiểm thử phần mềm) là việc lựa chọn các ca kiểm thử hiệu quả [1].

Một cách để đạt được điều này là sử dụng Phân hoạch Tương đương (Equivalence Partitioning), một kỹ thuật kiểm thử phần mềm chia dữ liệu đầu vào của một đơn vị phần mềm thành các phân hoạch (partition) gồm các dữ liệu tương đương, từ đó các ca kiểm thử có thể được suy ra [2]. Khái niệm nền tảng của kỹ thuật này dựa trên việc sử dụng các lớp tương đương (equivalence class), và việc chọn ra một phần tử đại diện từ mỗi lớp. Ưu điểm của phương pháp này là giảm tổng số ca kiểm thử xuống còn một tập hữu hạn các ca kiểm thử khả thi, trong khi vẫn bao phủ tối đa các yêu cầu. Thời gian kiểm thử cũng giảm đáng kể, do số lượng ca kiểm thử ít hơn.

Ý tưởng then chốt của phương pháp này là ta chỉ cần kiểm thử một mô hình đầu vào từ mỗi phân hoạch, vì ta giả định rằng tất cả các mô hình trong một phân hoạch nhất định sẽ được phép biến đổi xử lý theo cùng một cách. Nếu một mô hình thuộc về một phân hoạch có những đặc điểm đáng quan tâm nào đó, ta giả định rằng tất cả các mô hình khác trong phân hoạch đó cũng sẽ có những đặc điểm này, và do đó sẽ hành xử giống nhau. Vì vậy, việc kiểm thử bất kỳ mô hình nào khác trong số đó là không cần thiết. Tương tự, nếu một trong các mô hình trong một phân hoạch không hoạt động đúng, ta giả định rằng không có mô hình nào khác trong phân hoạch đó hoạt động đúng. Một lần nữa, việc kiểm thử thêm bất kỳ mô hình nào trong phân hoạch đó cũng ít có ý nghĩa. Tóm lại, điều này là vì tất cả các mô hình trong một phân hoạch đều tương đương với nhau.

Vấn đề chính là làm thế nào để định nghĩa các lớp tương đương xác định các phân hoạch một cách biểu cảm và linh hoạt, và làm thế nào để tự động chọn ra một phần tử đại diện của mỗi lớp.

Để đạt được điều này, đóng góp của chúng tôi đề xuất một kỹ thuật mới để phát triển các ca kiểm thử cho các mô hình UML và OCL, dựa trên một phương pháp tự động xây dựng các mô hình đối tượng cho các mô hình lớp được bổ sung bởi các ràng buộc OCL. Bằng cách định hướng quá trình xây dựng thông qua cái gọi là thuật ngữ phân loại, các ca kiểm thử được xây dựng dưới dạng mô hình đối tượng được phân loại thành các lớp tương đương. Thuật ngữ phân loại là các biểu thức OCL bất kỳ trên một mô hình lớp, tính toán ra một giá trị đặc trưng cho mỗi mô hình đối tượng. Mỗi lớp tương đương khi đó được định nghĩa bởi tập hợp các mô hình đối tượng có cùng giá trị đặc trưng, và với một mô hình đối tượng đại diện chuẩn tắc (canonical representative). Bằng cách khảo sát các mô hình đối tượng này, một nhà phát triển có thể khám phá các thuộc tính của mô hình lớp và các ràng buộc của nó.

Trong bài báo này, chúng tôi cũng chỉ ra cách thuật ngữ phân loại có thể được sử dụng hiệu quả kết hợp với Tracts [3], một phương pháp đặc tả và kiểm thử hộp đen (black-box testing) cho các chuyển đổi mô hình, cung cấp một cơ chế đúng đắn và thực tiễn cho việc sinh tự động các mô hình kiểm thử phù hợp cho Tracts.

> **Giải thích:** "Tracts" là một khung đặc tả (specification framework) do chính nhóm tác giả này đề xuất trước đó (tài liệu tham khảo [3]), dùng để mô tả "hợp đồng" (contract) cho một phép chuyển đổi mô hình: mô hình đầu vào phải thỏa ràng buộc gì, mô hình đầu ra phải thỏa ràng buộc gì, và quan hệ giữa đầu vào - đầu ra phải thỏa ràng buộc gì. Bài báo này cho thấy "thuật ngữ phân loại" có thể dùng để tự động sinh ra các mô hình kiểm thử cần thiết cho Tracts.

Bài báo này được tổ chức thành 5 phần (section). Sau phần Giới thiệu này, Phần II giới thiệu thuật ngữ phân loại, mô tả cách chúng được đặc tả, và trình bày cơ chế sẵn có để tự động xây dựng các mô hình đối tượng đại diện. Sau đó, Phần III mô tả cách thuật ngữ phân loại có thể được sử dụng trong bối cảnh của Tracts để triển khai việc kiểm thử chuyển đổi mô hình. Phần IV liên hệ công trình của chúng tôi với các phương pháp tương tự khác. Cuối cùng, Phần V kết luận và vạch ra một số hướng công việc tương lai.

## II. THUẬT NGỮ PHÂN LOẠI (CLASSIFYING TERMS)

Thuật ngữ phân loại là một công cụ để khảo sát các thuộc tính của mô hình. Chúng tôi thảo luận các khái niệm nền tảng của chúng và việc hiện thực hóa chúng trong bối cảnh của một công cụ, Môi trường Đặc tả dựa trên UML (UML-based Specification Environment — USE). Các ý tưởng nền tảng, tuy nhiên, có thể được áp dụng trong các công cụ mô hình hóa tương tự khác. USE cho phép người mô hình hóa mô tả một hệ thống bằng một mô hình lớp UML (biểu đồ lớp — class diagram) và các ràng buộc OCL, cùng với các phương tiện mô tả khác như, ví dụ, các máy trạng thái giao thức UML (UML protocol state machine). USE được thiết kế cho việc thẩm định (validation) và kiểm chứng (verification) các mô hình UML. Một nhiệm vụ thẩm định trung tâm là việc tự động xây dựng các mô hình đối tượng (biểu đồ đối tượng — object diagram) cho mô hình lớp bao gồm cả các ràng buộc OCL. Nhiệm vụ này có thể được thực hiện bởi cái gọi là một bộ thẩm định mô hình (model validator) mà (a) chuyển đổi các mô hình UML và OCL thành logic quan hệ (relational logic) [4] của Kodkod [5], (b) phân tích các kết quả logic quan hệ, và (c) chuyển đổi các kết quả trở lại dưới dạng UML. Việc xây dựng mô hình đối tượng được định hướng bởi một cấu hình (configuration) xác định cách các lớp, các liên kết (association), các thuộc tính (attribute) và các kiểu dữ liệu (data type) được lấp đầy (populate). Các giới hạn hữu hạn (finite bound) phải đảm bảo rằng tất cả các phần tử mô hình (lớp, liên kết, thuộc tính và kiểu dữ liệu) được gắn kết trong quá trình thẩm định với các tập hợp hữu hạn.

> **Giải thích:** USE (UML-based Specification Environment) là một công cụ học thuật cho phép vẽ mô hình lớp UML kèm ràng buộc OCL, rồi tự động "giải" ra các thể hiện (instance) cụ thể — gọi là mô hình đối tượng (object model / object diagram) — thỏa mãn các ràng buộc đó. Cơ chế bên dưới là biến đổi bài toán UML/OCL thành bài toán logic quan hệ (relational logic) rồi dùng bộ giải Kodkod (một SAT-based solver) để tìm nghiệm, sau đó dịch ngược nghiệm về dạng UML dễ đọc cho con người.

Ví dụ minh họa trong phần này là một mô tả rất đơn giản về quan hệ Cha-mẹ-Con (Parenthood) như trong Hình 1, với một mô hình lớp UML và các bất biến OCL (OCL invariant) đi kèm. Với một cấu hình phù hợp, bộ thẩm định mô hình có thể tự động xây dựng các mô hình đối tượng như những mô hình trong Hình 2.

*(Hình 1. Ví dụ mô hình lớp UML bao gồm các bất biến OCL. Hình 2. Các mô hình đối tượng ví dụ khác nhau với cấu trúc đẳng cấu một phần.)*

Để giải thích nhu cầu về thuật ngữ phân loại, khái niệm mới trung tâm trong bài báo này, hãy xem xét nhiệm vụ khảo sát mô hình sau đây: với một mô hình lớp cho trước và dưới một cấu hình cụ thể, nhà phát triển muốn duyệt qua (scroll through) tất cả các mô hình đối tượng hợp lệ, tức là cô ấy muốn xem xét không chỉ một mô hình đối tượng đơn lẻ mà là toàn bộ tập hợp của tất cả các mô hình đối tượng hợp lệ. Điều này hiện đang được thực hiện trong phương pháp USE thông qua tùy chọn thẩm định "scrolling" (cuộn) mà liệt kê tất cả các mô hình đối tượng.

**Vấn đề:** Khó khăn chung xuất hiện lúc này là rất nhiều mô hình đối tượng rất giống nhau sẽ được đưa vào xem xét. Nhà phát triển có thể kỳ vọng được thấy các mô hình đối tượng thú vị, khác biệt về mặt cấu trúc. Ví dụ, trong mô hình Parenthood ở trên với một cấu hình yêu cầu chính xác ba đối tượng Person (Người) và hai liên kết Parenthood, hai mô hình đối tượng ở bên phải nhất trong Hình 2 sẽ thường xuất hiện như hai mô hình khác biệt,

*(Hình 3. Các lớp tương đương của mô hình đối tượng xét theo một thuật ngữ phân loại.)*

mặc dù chỉ khác nhau ở tên riêng (first name) của các đối tượng Person ở phía dưới. Tuy nhiên, một phương pháp phát triển có thể cung cấp tùy chọn để ngăn không cho các mô hình đối tượng đẳng cấu (isomorphic) với cùng các mẫu hình Parenthood được trình bày như các mô hình đối tượng riêng biệt, khi duyệt qua tập hợp các mô hình đối tượng hợp lệ.

**Giải pháp:** Để trả lời, phương pháp của chúng tôi trao cho nhà phát triển một tùy chọn tường minh để phát biểu cách hiểu của cô ấy về việc hai mô hình đối tượng là khác nhau. Việc hiện thực hóa kỹ thuật như sau: nhà phát triển đặc tả một biểu thức truy vấn OCL đóng (closed OCL query term), tức là một biểu thức không có biến tự do (free variable), có thể được đánh giá (evaluate) trong một mô hình đối tượng và trả về một giá trị (tạm thời) kiểu số nguyên như một giá trị đặc trưng; trong phương pháp của chúng tôi, biểu thức này được gọi là "thuật ngữ phân loại" (classifying term); mỗi mô hình đối tượng được xây dựng mới phải cho ra một giá trị đặc trưng khác biệt. Như được phác họa trong Hình 3, thuật ngữ phân loại xác định một quan hệ tương đương (equivalence relationship) trên tất cả các mô hình đối tượng. Hai mô hình đối tượng có cùng giá trị đặc trưng thuộc về cùng một lớp tương đương. Phương pháp này quyết định chỉ chọn một đại diện từ mỗi lớp tương đương. Sau này chúng tôi sẽ nới lỏng hạn chế chỉ xét một thuật ngữ phân loại kiểu Integer.

> **Giải thích:** Đây là định nghĩa cốt lõi của bài báo. "Thuật ngữ phân loại" (classifying term) là một biểu thức OCL — không chứa biến tự do, nghĩa là có thể tính ra một giá trị cụ thể ngay khi áp vào một mô hình đối tượng — trả về một con số (hoặc sau này, giá trị đúng/sai). Hai mô hình đối tượng cho ra cùng giá trị này được coi là "tương đương" và chỉ một trong số chúng được giữ lại làm đại diện (representative) trong bộ ca kiểm thử, giúp tránh lãng phí việc kiểm thử nhiều mô hình gần như giống hệt nhau.

**Ví dụ:** Là một trường hợp đơn giản đầu tiên, một thuật ngữ phân loại có thể xác định số lượng đối tượng trong một lớp. Ví dụ, với một cấu hình yêu cầu tối thiểu 2 và tối đa 4 đối tượng Person, thuật ngữ phân loại `Person.allInstances()->size()` sẽ cho ra ba mô hình đối tượng với lần lượt 2, 3, và 4 đối tượng Person.

**Ví dụ:** Hãy tiếp tục với ví dụ và cấu hình Parenthood ở trên với chính xác ba đối tượng Person và hai liên kết Parenthood. Để ngăn hai mô hình đối tượng bên phải nhất từ Hình 2 được trình bày như các mô hình đối tượng khác nhau, nhà phát triển có thể sử dụng thuật ngữ phân loại sau.

```
Person.allInstances()->select(p | Person.allInstances()->exists(c,gc |
p.child->includes(c) and c.child->includes(gc)))->size()
```

Thuật ngữ này đếm số lượng đối tượng Person có một người con (child) và một người cháu (grandchild). Thuật ngữ này đánh giá hai mô hình đối tượng bên phải nhất từ Hình 2 với cùng giá trị 1, và do đó chỉ một mô hình đối tượng sẽ được chọn từ lớp tương đương tương ứng. Thuật ngữ này đánh giá mô hình đối tượng bên trái nhất từ Hình 2 với giá trị 0.

*(Hình 4. Sự tương tác giữa bộ thẩm định mô hình và thuật ngữ phân loại.)*

**Cách xử lý thuật ngữ phân loại:** Bộ thẩm định mô hình USE và một thuật ngữ phân loại phối hợp với nhau như minh họa trong Hình 4: như một bước khởi đầu, mô hình đối tượng đầu tiên được xây dựng; sau đó giá trị value1 của thuật ngữ phân loại trong mô hình đối tượng đầu tiên được lưu lại; tiếp theo, một ràng buộc được thêm vào quá trình thẩm định, cụ thể là ràng buộc `classifyingTerm<>value1`; sử dụng ràng buộc này, mô hình đối tượng thứ hai được tính toán; giá trị value2 của thuật ngữ phân loại trong mô hình đối tượng thứ hai được lưu lại, và một ràng buộc khác được thêm vào quá trình thẩm định `classifyingTerm<>value2`; quy tắc chung là khi tính toán mô hình đối tượng thứ N+1, các giá trị value1, ..., valueN của thuật ngữ phân loại trong các mô hình đối tượng trước đó được sử dụng để phân biệt mô hình đối tượng mới được tính toán với các mô hình đã tìm thấy trước đó; các bước này được lặp lại cho đến khi không tìm thấy mô hình đối tượng mới nào nữa. Trong phương pháp của chúng tôi, các lớp, liên kết, thuộc tính và kiểu dữ liệu phải được lấp đầy bởi các phần tử được xác định bởi các tập hợp hữu hạn, và do đó chỉ tồn tại một số lượng hữu hạn các mô hình đối tượng.

**Ví dụ:** Bây giờ chúng ta xem xét một thuật ngữ phân loại thực tế hơn, sinh ra các mô hình đối tượng khác biệt về mặt cấu trúc. Cấu hình yêu cầu có từ 1 đến 3 đối tượng Person và từ 1 đến 3 liên kết Parenthood. Thuật ngữ phân loại sử dụng các thuộc tính boolean wGp (có ông/bà — with grandparent), w2c (có 2 con — with 2 children) và w2p (có 2 cha/mẹ — with 2 parents).

```
let P=Person.allInstances in let wGp=P->exists(g,p,c |
g.child->includes(p) and p.child->includes(c)) in
let w2c=P->exists(p | p.child->size>=2) in let w2p=P->exists(p | p.parent->size>=2) in
if wGp then 1 else 0 endif + if w2c then 2 else 0 endif + if w2p then 4 else 0 endif
```

Để đạt được càng nhiều tổ hợp càng tốt, ba thuộc tính boolean được xem như các bit trong một biểu diễn số nguyên ba bit. Thuật ngữ phân loại mã hóa biểu diễn này. Các mô hình đối tượng kết quả được trình bày trong Hình 5. Các mô hình đối tượng thể hiện các đặc điểm cấu trúc khác nhau và được trình bày theo thứ tự mà bộ thẩm định mô hình tìm ra chúng. Xin lưu ý rằng trong số 8 tổ hợp khả dĩ của các thuộc tính boolean cơ bản, chỉ có 5 phương án được xét đến. Điều này chủ yếu là do cấu hình đã nêu (1 đến 3 đối tượng, 1 đến 3 liên kết). Ví dụ, phương án (wGp=0, w2c=1, w2p=1) không thể đạt được với tối đa 3 đối tượng, bởi vì việc kết hợp w2c=1 và w2p=1 sẽ dẫn đến nghiệm số 5, trong đó wGp=1 phải đúng; tuy nhiên, phương án (wGp=0, w2c=1, w2p=1) có thể đạt được bằng cách tăng số lượng đối tượng trong cấu hình lên 4 (dẫn đến, ví dụ, p1 với các con {p2,p3} và p3 với các cha/mẹ {p1,p4}).

Như đã đề cập ở trên, việc sử dụng một thuật ngữ phân loại kiểu Integer là một phương án. Nói chung, nhiều hơn một thuật ngữ phân loại có thể được sử dụng. Mỗi thuật ngữ được phép có kiểu Integer hoặc Boolean. Do đó cùng một tập hợp các mô hình đối tượng như trong Hình 5 cũng có thể đạt được bằng cách đặc tả ba thuật ngữ Boolean.

```
[ wGp ] Person.allInstances->exists(g,p,c | g.child->includes(p) and p.child->includes(c))
[ w2c ] Person.allInstances->exists(p | p.child->size>=2)
[ w2p ] Person.allInstances->exists(p | p.parent->size>=2)
```

Ví dụ này minh họa hai khía cạnh mới của thuật ngữ phân loại. Thứ nhất, việc sử dụng nhiều thuật ngữ phân loại trong một quá trình thẩm định là có giá trị. Và thứ hai, khi cho phép nhiều thuật ngữ, ngoài các biểu thức số nguyên, các biểu thức boolean cũng có thể được sử dụng — vốn tự thân chỉ cho phép tối đa hai kết quả. Trong khi đó, với n thuật ngữ phân loại boolean, có thể tìm ra tới 2^n nghiệm khả dĩ. Do đó, định nghĩa của thuật ngữ phân loại được mở rộng để cho phép các tính năng này.

*(Hình 5. Các mô hình đối tượng khác biệt về cấu trúc được xây dựng bởi một thuật ngữ phân loại.)*

Để tìm ra thành công các mô hình đối tượng mới cho một mô hình lớp cho trước cộng với các thuật ngữ phân loại, các giá trị của thuật ngữ phân loại được lưu lại cho mỗi nghiệm. Sử dụng các thuật ngữ phân loại và các giá trị này, các ràng buộc được tạo ra và đưa cho bộ giải cùng với mô hình lớp trong quá trình thẩm định. Nói một cách không hình thức, lược đồ ràng buộc phát biểu rằng: Không tồn tại mô hình đối tượng nào trước đó, mà trong đó việc đánh giá tất cả các thuật ngữ phân loại trong mô hình đối tượng hiện đang được xây dựng bằng với các giá trị đã lưu của các mô hình đối tượng trước đó. Phát biểu này có thể được biểu diễn một cách hình thức như:

```
¬ ∨      ∧        ct = ct[om]
om∈PreviousObjectModels  ct∈ClassifyingTerms
```

trong đó ct là một thuật ngữ phân loại và ct[om] chỉ giá trị đã lưu của thuật ngữ phân loại cụ thể đó trong mô hình đối tượng trước đó om. Với công thức này, ví dụ trên có thể được hiện thực bằng ba thuật ngữ phân loại riêng biệt, và phần chi phí (overhead) dưới dạng phép cộng nhị phân biến mất, mang lại một giải pháp hiệu quả hơn. Tất cả các tính năng được mô tả đã được hiện thực trong bộ thẩm định mô hình USE và có sẵn để tải về¹.

**Ưu điểm của thuật ngữ phân loại:** Thuật ngữ phân loại có thể được sử dụng để khảo sát mô hình lớp nhằm thấy được một số ít các mô hình đối tượng đa dạng thay vì nhiều mô hình tương tự nhau. Trọng tâm khảo sát được xác định bởi người mô hình hóa thông qua các thuật ngữ. Bằng cách khảo sát các mô hình đối tượng đã xây dựng và kiểm tra các thuộc tính của chúng, người mô hình hóa có được cái nhìn sâu sắc về các đặc điểm của mô hình lớp bao gồm các ràng buộc OCL và làm cho chúng trở nên "sống động". Sử dụng các thuật ngữ phân loại boolean, người ta có thể rút ra kết luận về việc các thuộc tính mô hình nào (được biểu diễn dưới dạng thuật ngữ phân loại) được phép đồng thời tồn tại trong một mô hình đối tượng (xem Bảng ở góc dưới bên phải của Hình 5). Do đó người ta có thể phân tích các phụ thuộc giữa các yêu cầu, tương tự như phân tích tính độc lập bất biến (invariant independence) [6], vốn kiểm tra xem một bất biến cho trước có phải là hệ quả logic từ các bất biến khác hay không. Thuật ngữ phân loại có thể sử dụng tất cả các cấu trúc OCL (ví dụ: các liên từ logic và các phép toán tập hợp như forAll, collect, closure hoặc size) được hỗ trợ bởi phép biến đổi sang logic quan hệ, và cho phép biểu đạt các thuộc tính khá tổng quát. Chúng có thể được sử dụng để sinh ra các ca kiểm thử dưới dạng mô hình đối tượng dựa trên ý tưởng xây dựng các lớp tương đương.

¹ http://sourceforge.net/projects/useocl/ (USE và plugin ModelValidator)

## III. SỬ DỤNG THUẬT NGỮ PHÂN LOẠI TRONG BỐI CẢNH CỦA TRACTS

### A. Xây dựng Bộ Ca kiểm thử Tract (Tract Test Suite) bằng Thuật ngữ Phân loại

**Tracts:** Tracts được giới thiệu trong [3] như một cơ chế đặc tả và kiểm thử hộp đen cho các chuyển đổi mô hình. Chúng là một dạng đặc biệt của hợp đồng chuyển đổi mô hình (model transformation contract) [1, 7], đặc biệt phù hợp cho việc đặc tả các chuyển đổi mô hình theo cách mô-đun hóa (modular) và dễ quản lý (tractable). Tracts cung cấp các mảnh đặc tả theo mô-đun, mỗi mảnh tập trung vào một kịch bản chuyển đổi cụ thể. Do đó, mỗi chuyển đổi mô hình có thể được đặc tả

*(Hình 6. Các khối xây dựng của một tract như trong [3].)*

bằng một tập hợp các Tracts, mỗi Tract bao phủ một trường hợp sử dụng (use case) cụ thể — được định nghĩa bởi các mô hình đầu vào và đầu ra cụ thể và cách chúng nên được liên hệ với nhau bởi phép chuyển đổi. Theo cách này, Tracts cho phép phân hoạch toàn bộ không gian đầu vào của phép chuyển đổi thành các đơn vị hành vi nhỏ hơn, tập trung hơn, và định nghĩa các kiểm thử cụ thể cho chúng. Thông thường, những gì các nhà phát triển được kỳ vọng làm với Tracts là xác định các kịch bản đáng quan tâm (mỗi kịch bản được định nghĩa bởi một Tract) và kiểm tra xem phép chuyển đổi có hoạt động như mong đợi trong các kịch bản này hay không. Tracts cũng có sự hỗ trợ công cụ để kiểm tra, theo kiểu hộp đen, rằng một cài đặt (implementation) cho trước hoạt động như mong đợi — tức là nó tôn trọng các ràng buộc của Tracts [8].

Hình 6 mô tả các thành phần chính của phương pháp Tracts: siêu mô hình nguồn và đích, phép chuyển đổi T đang được kiểm thử, và hợp đồng chuyển đổi (transformation contract), bao gồm một bộ ca kiểm thử Tract (Tract test suite) và một tập hợp các ràng buộc Tract (Tract constraint). Tổng cộng, có năm loại ràng buộc khác nhau: các mô hình nguồn và đích bị ràng buộc bởi các ràng buộc chung được thêm vào định nghĩa ngôn ngữ, và Tract áp đặt thêm các ràng buộc Tract nguồn, đích, và nguồn-đích cho một phép chuyển đổi cho trước. Các ràng buộc này đóng vai trò như "hợp đồng" (theo nghĩa thiết kế theo hợp đồng — contract-based design [9]) cho phép chuyển đổi trong một số kịch bản cụ thể, và được biểu đạt bằng các bất biến OCL. Chúng cung cấp đặc tả của phép chuyển đổi.

Nếu ta giả sử một mô hình nguồn m là một phần tử của bộ ca kiểm thử và thỏa mãn siêu mô hình nguồn cũng như các ràng buộc Tract nguồn đã cho, Tract về cơ bản yêu cầu kết quả T(m) của việc áp dụng phép chuyển đổi T phải thỏa mãn siêu mô hình đích và các ràng buộc Tract đích, và bộ đôi <m, T(m)> phải thỏa mãn các ràng buộc Tract nguồn-đích.

**Ví dụ:** Để minh họa Tracts, hãy xem xét một phép chuyển đổi mô hình đơn giản gọi là BibTex2DocBook, chuyển đổi thông tin về kỷ yếu hội nghị (proceedings of conferences, ở định dạng BibTeX) thành thông tin tương ứng được mã hóa ở định dạng DocBook². Các siêu mô hình nguồn và đích mà chúng tôi sử dụng cho phép chuyển đổi này được trình bày trong Hình 7. Bảy tên ràng buộc cũng được thể hiện trong hình. Các ràng buộc này chịu trách nhiệm đặc tả các phát biểu trên các mô hình nguồn (ví dụ: kỷ yếu phải có ít nhất một bài báo; các cá nhân phải có tên duy nhất); và trên các mô hình đích (ví dụ: một cuốn sách phải có hoặc là một biên tập viên hoặc là một tác giả, nhưng không phải cả hai). Các ràng buộc cho mô hình nguồn được trình bày bên dưới.

² http://docbook.org/

*(Hình 7. Các siêu mô hình nguồn và đích.)*

```
context Person inv isAuthorOrEditor: inProc->size() + proc->size() > 0

context InProc inv booktitleOccursAsProcTitle: Proc.allInstances->exists(prc |
prc.title=booktitle)

context Person inv uniqueName: Person.allInstances->isUnique(name)

context Proc inv hasAtLeastOnePaper: InProc.allInstances->exists(pap |
pap.booktitle=title)

context Proc inv uniqueTitle: Proc.allInstances->isUnique(title)

context Proc inv withinProcUniqueTitle: InProc.allInstances->select(pap |
pap.booktitle=title)->forAll(p1,p2 | p1<>p2 implies p1.title<>p2.title)

context InProc inv titleDifferentFromPrcTitle: Proc.allInstances->forAll(p| p.title<>title)
```

Ngoài các ràng buộc trên mô hình nguồn và mô hình đích, tracts còn áp đặt các điều kiện lên mối quan hệ giữa chúng — vì chúng được kỳ vọng sẽ được cài đặt bởi quá trình thực thi của phép chuyển đổi. Trong trường hợp này, lớp Tract dùng để định nghĩa các ràng buộc nguồn-đích cho tract mẫu mà chúng tôi sử dụng (mặc dù thông thường nhiều tract được định nghĩa cho một phép chuyển đổi, mỗi tract tập trung vào các khía cạnh hoặc trường hợp sử dụng cụ thể của phép chuyển đổi, để đơn giản chúng tôi sẽ chỉ xét một tract ở đây). Các điều kiện sau đây là một phần của các ràng buộc nguồn-đích của tract:

```
context t:Tract inv sameSizes: t.file->size() = t.docBook->size() and t.file->forAll( f | t.docBook->exists( db |
f.entry->selectByType(Proc)->size() = db.book->size()))

context prc:Proc inv sameBooks: Book.allInstances->one( bk | prc.title = bk.title and prc.editor->forAll(pE | bk.editor->one(bE|
pE.name = bE.name )))

context pap:InProc inv sameChaptersInBooks: Article.allInstances->one( art | pap.title = art.title and pap.booktitle = art.book.title and pap.author->forAll(aP |
art.author->one(aA | aP.name=aA.name)) )
```

**Bộ ca kiểm thử Tract (Tract Test Suites):** Ngoài các ràng buộc tract nguồn, đích và nguồn-đích, các bộ ca kiểm thử đóng một vai trò thiết yếu trong Tracts. Các mô hình trong bộ ca kiểm thử là các tập đầu vào được định nghĩa trước, thuộc nhiều loại khác nhau, nhằm mục đích vận hành thử (exercise) phép chuyển đổi. Khả năng chọn các mẫu hình cụ thể của mô hình nguồn (những mẫu được định nghĩa cho một bộ ca kiểm thử tract) cung cấp một cơ chế chi tiết (fine-grained) để đặc tả hành vi của phép chuyển đổi, và cho phép người kiểm thử chuyển đổi mô hình tập trung vào các hành vi cụ thể của tract. Lưu ý rằng các bộ ca kiểm thử không chỉ có thể là các mô hình kiểm thử dương tính (positive test model), thỏa mãn các ràng buộc nguồn, mà còn có thể là các mô hình kiểm thử âm tính (negative test model), dùng để biết phép chuyển đổi hành xử như thế nào với chúng.

**Vấn đề:** Cho đến nay, việc sinh ra các bộ ca kiểm thử cho tracts đã được thực hiện bằng ngôn ngữ ASSL (A Snapshot Sequence Language — Ngôn ngữ Chuỗi Ảnh chụp nhanh) [10], được phát triển để sinh ra các biểu đồ đối tượng cho một biểu đồ lớp cho trước theo một cách linh hoạt. ASSL về cơ bản là một ngôn ngữ lập trình mệnh lệnh (imperative) với các tính năng để chọn ngẫu nhiên các giá trị thuộc tính hoặc các đầu liên kết (association end). Mặc dù khá mạnh mẽ, phương pháp này để sinh ra các mô hình nguồn cho mục đích kiểm thử có một số hạn chế. Cụ thể, nó gây khó khăn cho việc chứng minh một số thuộc tính mà bất kỳ bộ ca kiểm thử nào cũng nên thể hiện, chẳng hạn như tính đầy đủ (completeness — liệu tất cả các loại mô hình đầu vào có thể có đã được bao phủ hay chưa?) và tính đúng đắn (correctness — liệu tất cả các mô hình được sinh ra có hợp lệ và đúng đắn hay không?). Nói chung, việc phân tích độ bao phủ (coverage) của bộ ca kiểm thử đối với tract cho trước là một nhiệm vụ hoàn toàn không tầm thường.

**Giải pháp:** Trong bối cảnh này, thuật ngữ phân loại có thể mang lại lợi ích to lớn. Chúng cho phép định hướng quá trình xây dựng các bộ ca kiểm thử bằng cách sử dụng các lớp tương đương xác định các loại mô hình đầu vào của tract. Quy trình xây dựng bộ ca kiểm thử khi đó trở nên đơn giản. Chúng ta bắt đầu bằng cách xác định các loại mô hình mà chúng ta muốn đưa vào bộ ca kiểm thử. Mỗi loại sau đó được đặc tả bởi một thuật ngữ phân loại, đại diện cho lớp tương đương chứa tất cả các mô hình tương đương theo lớp đó, tức là thuộc cùng một loại. Khi các thuật ngữ phân loại đã được định nghĩa cho một Tract, công cụ USE sẽ sinh ra một mô hình đại diện cho mỗi lớp tương đương. Các mô hình chuẩn tắc này tạo thành bộ ca kiểm thử của tract.

**Ví dụ:** Ví dụ, giả sử chúng ta muốn tập trung vào các đặc điểm khác nhau của các mô hình đầu vào của phép chuyển đổi BibTex2DocBook. Thứ nhất, kỷ yếu có hai ngày tháng: năm mà sự kiện hội nghị được tổ chức (yearE) và năm mà kỷ yếu được xuất bản (yearP). Chúng ta muốn có các mô hình đầu vào trong đó hai ngày tháng này trùng nhau ở tất cả các kỷ yếu, và các mô hình đầu vào khác với năm tổ chức sự kiện và năm xuất bản khác nhau. Thứ hai, chúng ta muốn có một số mô hình đầu vào mẫu trong đó hai biên tập viên của kỷ yếu mời nhau có bài báo ở đó; và tương ứng, chúng ta cũng muốn có các mô hình đầu vào trong đó tình huống "có qua có lại" (manus-manum-lavat) này không xảy ra. Cuối cùng, chúng ta muốn có một số mô hình nguồn với kỷ yếu được biên tập bởi một trong các tác giả của các bài báo trong kỷ yếu đó, và các mô hình đầu vào khác không có kỷ yếu "tự biên tập" (self-edited).

> **Giải thích:** "Manus manum lavat" là thành ngữ Latin nghĩa đen "tay này rửa tay kia" (tương đương "có qua có lại"). Ở đây tác giả dùng để chỉ tình huống hai biên tập viên hội nghị "trao đổi qua lại": ông A mời ông B viết bài trong kỷ yếu do A biên tập, và ngược lại B cũng mời A viết bài trong kỷ yếu do B biên tập — một dạng xung đột lợi ích tiềm ẩn mà mô hình kiểm thử muốn phát hiện.

Việc sinh ra các mô hình cho bộ ca kiểm thử để bao phủ tất cả các trường hợp này bằng một phương pháp mệnh lệnh hoặc bằng ASSL thường tẻ nhạt và dễ sai sót. Tuy nhiên, việc sử dụng thuật ngữ phân loại giúp đơn giản hóa đáng kể nhiệm vụ này. Chỉ cần cung cấp ba thuật ngữ Boolean cho bộ thẩm định mô hình là đủ, mỗi thuật ngữ định nghĩa thuật ngữ phân loại xác định đặc điểm mà chúng ta muốn nhận diện trong mô hình. Trong trường hợp này, các thuật ngữ Boolean đó được trình bày bên dưới.

```
[ yearE_EQ_yearP ] Proc.allInstances->forAll(yearE=yearP)

[ noManusManumLavat ] not Person.allInstances->exists(p1,p2 |
p1<>p2 and p1.proc->exists(prc1 | p2.proc->exists(prc2 | prc1<>prc2 and InProc.allInstances->
select(booktitle=prc1.title)-> exists(pap2 | pap2.author->includes(p2) and
InProc.allInstances-> select(booktitle=prc2.title)->
exists(pap1 | pap1.author->includes(p1))))))

[ noSelfEditedPaper ] not Proc.allInstances->exists(prc |
InProc.allInstances->exists(pap | pap.booktitle=prc.title and prc.editor-> intersection(pap.author)->notEmpty))
```

Sử dụng các đặc tả của các thuật ngữ phân loại này, bộ thẩm định mô hình tìm thấy 8 nghiệm, được trình bày trong Hình 8 theo thứ tự mà bộ thẩm định mô hình tìm thấy chúng. Đối với mỗi nghiệm, giá trị của ba thuộc tính (yearE_EQ_yearP, noManusManumLavat, noSelfEditedPaper) được biểu thị trong hình bằng các giá trị số nguyên (0, 1), cho biết liệu nghiệm đó có thỏa mãn điều kiện hay không (1 là có, 0 là không).

Tóm lại, chúng ta đã có thể định nghĩa một tập hợp gồm 8 lớp tương đương đặc trưng cho các loại mô hình đầu vào mà chúng ta quan tâm, và để bộ thẩm định mô hình tìm ra các mô hình đại diện (tức là chuẩn tắc) cho mỗi lớp. Theo cách này, chúng ta đảm bảo rằng các mô hình cấu thành bộ ca kiểm thử của tract bao phủ tất cả các trường hợp đáng quan tâm.

### B. Phân tích Sâu hơn về các Chuyển đổi Mô hình

Do cách mà thuật ngữ phân loại có thể được đặc tả (bằng các thuật ngữ Boolean) để xây dựng các mô hình bộ ca kiểm thử tract, chúng định nghĩa một tập hợp các lớp tương đương tạo thành một phân hoạch (đầy đủ và rời rạc) của không gian mô hình đầu vào của phép chuyển đổi. Điều này hữu ích để chọn các mô hình đầu vào mẫu thuộc các loại khác nhau (mỗi lớp tương đương một mẫu),

*(Hình 8. Tám nghiệm được tìm thấy bởi bộ thẩm định mô hình. Hình 9. Thuật ngữ phân loại cho việc định nghĩa các phân hoạch của không gian nguồn và đích.)*

đảm bảo rằng (a) chúng ta không bỏ sót bất kỳ mô hình đại diện nào từ bất kỳ loại mô hình đáng quan tâm nào (tính đầy đủ — completeness), và (b) không có hai mô hình mẫu nào cùng loại (tính rời rạc — disjointness), như được minh họa trong Hình 9.

Nhưng chúng ta cũng có thể áp dụng ý tưởng phân hoạch một không gian mô hình cho không gian mô hình đích, và đặc trưng hóa các loại mô hình đích đáng quan tâm đối với người mô hình hóa (hoặc đối với người kiểm thử chuyển đổi mô hình). Các lớp tương đương được định nghĩa bởi các thuật ngữ phân loại đích rất hữu ích để kiểm tra một số thuộc tính của phép chuyển đổi. Ví dụ, chúng ta có thể kiểm tra rằng:

- Tất cả các loại mô hình đích đáng quan tâm đều được sinh ra bởi phép chuyển đổi — tức là bao phủ đầy đủ một số phần của không gian mô hình đích.
- Không có mô hình đích thuộc các dạng (loại) nhất định nào được sinh ra vì chúng sẽ là các mô hình đích không hợp lệ — tức là phép chuyển đổi không tạo ra "rác" (junk).
- Không có mô hình đích thuộc các loại nhất định nào được ánh xạ đến cùng một loại mô hình đích khi không nên như vậy — tức là phép chuyển đổi không gây nhầm lẫn khi không nên (hai mô hình không được ánh xạ đến cùng loại đích trừ khi chúng thuộc cùng loại nguồn).

**Ví dụ:** Để minh họa điều này, hãy quay lại phép chuyển đổi BibTeX2DocBook, nơi chúng ta có thể xác định một số loại mô hình đáng quan tâm trong không gian đích.

Ví dụ, chúng ta có thể quan tâm đến một thuộc tính cũng có liên quan trong không gian nguồn, chẳng hạn như các bài báo "tự biên tập" (self edited papers, tức là liệu biên tập viên của một cuốn sách có đồng thời là tác giả của một trong các chương hay không). Chúng ta cũng có thể quan tâm đến các cuốn sách "bình thường" (normal book), tức là những cuốn không phải là tập hợp các bài báo được chọn bởi một biên tập viên, mà thay vào đó tất cả các chương đều do cùng một người viết, tác giả của sách. Cuối cùng, các sách biên tập (edited book) trong đó không tác giả nào viết nhiều hơn một bài báo cũng có thể đáng quan tâm.

Để đặc tả các thuộc tính này và định nghĩa các lớp tương đương phù hợp, chúng ta chỉ cần viết các thuật ngữ phân loại tương ứng:

```
[ noSelfEditedPaper ] not Book.allInstances->exists(b | b.editor->intersection(
b.article.author)->notEmpty() )

[ onlyNormalBooks ] Book.allInstances->forAll(b | b.editor->isEmpty() and b.article->forAll(a | a.author=b.author))

[ noRepeatedAuthors ] Book.allInstances->forAll(b |
b.author->forAll(a | a.article->select(book=b)->size()=1 ) )
```

Ba thuật ngữ phân loại boolean này tạo ra 8 lớp tương đương (8 = 2³) trong không gian mô hình đích. Bây giờ chỉ còn là vấn đề xác định hành vi kỳ vọng của phép chuyển đổi với các mô hình đầu vào từ các lớp tương đương nguồn. Về điều này, có những thuộc tính nên được bảo toàn (ví dụ, noSelfEditedPaper) và những thuộc tính khác không thể xảy ra (ví dụ, do kỷ yếu phải có ít nhất một biên tập viên, không cuốn sách "bình thường" nào có thể được sinh ra bởi phép chuyển đổi).

Về điều này, bộ thẩm định mô hình cũng có thể rất hữu ích để tìm các phản ví dụ (counterexample) cho các tình huống mà về nguyên tắc không nên xảy ra, nhưng lại được cho phép bởi đặc tả của chúng ta vì các thuật ngữ phân loại không được định nghĩa đúng cách.

Với tập hợp các lớp tương đương trong không gian mô hình nguồn và đích, chúng ta có thể thực thi phép chuyển đổi mô hình trên bộ ca kiểm thử và kiểm tra xem các mô hình đầu ra có thuộc về các lớp tương đương phù hợp trong không gian mô hình đích hay không.

Để chứng minh điều đó, chỉ cần phân tích hành vi của phép chuyển đổi mô hình với các mô hình đại diện của mỗi lớp tương đương nguồn. Trong trường hợp này, ánh xạ được thực hiện bởi phép chuyển đổi cho 8 mô hình đại diện của các lớp tương đương (được trình bày trong Hình 8) được mô tả bởi Hình 10.

*(Hình 10. Ánh xạ các lớp tương đương.)*

```
Source          Target
[0,0,0]    →    [0,0,1]
[0,0,1]    →    [0,0,1]
[0,1,0]    →    [0,0,0]
[0,1,1]    →    [0,0,0]
[1,0,0]    →    [1,0,0]
[1,0,1]    →    [1,0,1]
[1,1,0]    →    [1,0,1]
[1,1,1]    →    [1,0,0]
```

Trong bảng này, mỗi lớp tương đương được biểu diễn bởi một bộ [x1, x2, x3] trong đó xi ∈ {0, 1} cho biết liệu mô hình có thỏa mãn điều kiện i của thuật ngữ phân loại tương ứng hay không. Do đó, trong không gian mô hình nguồn, [1, 1, 1] có nghĩa là mô hình thỏa mãn noSelfEditedPaper, noManusManumLavat và yearE_EQ_yearP, trong khi ở không gian mô hình đích, bộ [1, 1, 1] tương ứng với một mô hình thỏa mãn các điều kiện noSelfEditedPaper, onlyNormalBooks và noRepeatedAuthors (theo thứ tự này). Theo cách này chúng ta có thể kiểm tra rằng trên thực tế không có cuốn sách "bình thường" nào được sinh ra. Chúng ta cũng có thể thấy rằng với các mô hình đầu vào này, tất cả các lớp tương đương còn lại mà chúng ta đã định nghĩa cho không gian đích đều đã được đạt tới.

### C. Chọn nhiều hơn Một Mẫu cho mỗi Thuật ngữ Phân loại

Cho đến nay, chúng ta đã có thể kiểm tra rằng hành vi của phép chuyển đổi quả thực đúng như mong đợi đối với các mô hình mẫu đã chọn. Tuy nhiên, điều này không chứng minh rằng phép chuyển đổi sẽ luôn hoạt động đúng. Điều gì sẽ xảy ra nếu bộ thẩm định mô hình đã chọn các mô hình đại diện khác cho các lớp tương đương?

Điều này có thể xảy ra, ví dụ, khi các lớp tương đương không được định nghĩa ở mức độ chi tiết (granularity) phù hợp (dù ở không gian mô hình nguồn hay đích). Trong trường hợp này, hai mô hình đầu vào thuộc cùng một lớp tương đương nguồn sẽ được chuyển đổi thành hai lớp tương đương đích khác nhau.

Đây là lý do tại sao sẽ thú vị nếu yêu cầu bộ thẩm định mô hình sinh ra nhiều hơn một mô hình cho mỗi lớp tương đương. Có một lý do chính đáng khác cho việc đó: chúng ta biết rằng không phải tất cả các loại mô hình đầu vào đều có khả năng xảy ra như nhau trong không gian mô hình nguồn. Do đó, chúng ta có thể chọn nhiều mô hình mẫu hơn cho những lớp tương đương mà chúng ta cho là phổ biến hơn. Theo cách này chúng ta có thể vận hành phép chuyển đổi mô hình theo cách tập trung hơn, và tạo ra một bộ ca kiểm thử phong phú hơn cho tract (và do đó cho phép chuyển đổi).

Để yêu cầu bộ thẩm định mô hình sinh ra nhiều hơn một mô hình đối tượng cho mỗi lớp tương đương, người ta có thể đặc tả thêm các "thuật ngữ phân loại cấp hai" (second-level classifying term), chỉ áp dụng cho các lớp tương đương "cấp một" (first-level) không rỗng. Ví dụ, một thuật ngữ phân loại cấp hai cho mô hình nguồn của ví dụ BibTeX2DocBook có thể là:

```
[ exactlyOnePaperInProc ] Proc.allInstances->forAll(prc | InProc.allInstances->select(pap |
pap.booktitle=prc.title)->size()=1)
```

Thuật ngữ này có thể sinh ra, cho lớp tương đương thứ hai trong Hình 8 (trong đó đối tượng kỷ yếu có hai bài báo), một đại diện khác chỉ có một bài báo trong một kỷ yếu. Việc hoàn thiện chi tiết cho phác thảo này được để lại cho công việc tương lai. Tuy nhiên, theo cách này người ta có thể chọn một cách khai báo (declaratively) một tập hợp các mô hình đầu vào sẽ cấu thành bộ ca kiểm thử của tract, quyết định không chỉ các loại mô hình mà chúng ta quan tâm, mà còn số lượng các mô hình mẫu khác nhau của mỗi loại mà chúng ta muốn.

## IV. CÔNG TRÌNH LIÊN QUAN (RELATED WORK)

Liên quan đến đóng góp của bài báo này, trước hết chúng tôi trình bày các phương pháp liên quan chuyên về việc sinh ra các mô hình đối tượng theo cách (bán) tự động, và sau đó chúng tôi thảo luận công trình liên quan xem xét các phương pháp kiểm thử và kiểm chứng chuyển đổi mô hình.

### A. Sinh Mô hình Đối tượng (Generating Object Models)

Bộ thẩm định mô hình USE, được sử dụng trong công trình này, dựa trên phép biến đổi UML và OCL thành logic quan hệ [11]. Nhiều phương pháp tồn tại để sinh ra các mô hình đối tượng từ các mô hình lớp bằng cách sử dụng các ngôn ngữ và công cụ khác nhau. Một phương pháp khác trong cùng công cụ, USE, là Ngôn ngữ Ảnh chụp nhanh Đặc tả Tự động (Automatic Specification Snapshot Language — ASSL) [10], sử dụng một phương pháp lặp (iterative) để sinh ra một mô hình đối tượng từ một đặc tả cho trước.

Các phương pháp khác dựa trên các nền tảng công nghệ khác nhau như lập trình logic (logic programming) và giải ràng buộc (constraint solving) [12], logic quan hệ và Alloy [13], viết lại thuật ngữ (term rewriting) với Maude [14] hoặc ngữ pháp đồ thị (graph grammar) [15]. Trái ngược với công cụ được sử dụng trong công trình này, các phương pháp đó hoặc không hỗ trợ đầy đủ OCL (ví dụ, các liên kết bậc cao — higher-order association [13], hoặc các định nghĩa phép toán đệ quy — recursive operation definition [12] không được hỗ trợ) hoặc không hỗ trợ kiểm tra cú pháp OCL đầy đủ [14]. Ngoài ra, tính năng tự động duyệt qua nhiều mô hình đối tượng hợp lệ từ một nhiệm vụ kiểm chứng cũng không khả thi trong tất cả các phương pháp trên.

Các phương pháp chứng minh (bán) tự động cho các thuộc tính của lớp UML đã được đề xuất trên cơ sở logic mô tả (description logic) [16], trên cơ sở logic quan hệ và Alloy thuần túy [13] sử dụng một tập con của OCL, và trong [17] tập trung vào các mâu thuẫn mô hình (model inconsistency) bằng cách sử dụng Kodkod. Một sự phân loại các bộ kiểm tra mô hình (model checker) liên quan đến các nhiệm vụ kiểm chứng có thể được tìm thấy trong [18].

Ý tưởng về thuật ngữ phân loại có những điểm tương đồng với việc phân tích tính độc lập bất biến (invariant independence) [6]. Mục tiêu là tìm các bất biến được bao phủ hoàn toàn bởi các bất biến khác hoặc các ràng buộc vốn có của mô hình lớp (ví dụ: các số lượng bội — multiplicity). Mục tiêu này có thể đạt được bằng cách sử dụng các thuật ngữ phân loại boolean, mang lại thông tin chi tiết về các bất biến nào có thể được thỏa mãn độc lập với những bất biến khác.

### B. Kiểm thử và Kiểm chứng Chuyển đổi Mô hình (Testing and Verifying Model Transformations)

Trong lĩnh vực Kỹ thuật Hướng Mô hình (Model-Driven Engineering), việc kiểm thử và phân tích các chuyển đổi mô hình đã là chủ đề của nhiều nghiên cứu (xem, ví dụ, [19, 20]). Về các phương pháp động (dynamic approach), vốn cần đến việc thực thi phép chuyển đổi mô hình và do đó cần các mô hình đầu vào, các tác giả trong [21] và [22] trình bày đóng góp của họ về việc gỡ lỗi (debugging) các chuyển đổi mô hình. Ngoài ra, công trình trong [23] phân tích các dấu vết thực thi (execution trace) giữa các mô hình nguồn và đích để tìm lỗi, và trong [24] một phương pháp sinh mô hình kiểm thử hộp trắng (white-box) để kiểm thử các phép chuyển đổi được đề xuất. Trong bối cảnh này, Tracts [25] là một phương pháp bổ sung, thiết lập các hợp đồng giữa các siêu mô hình nguồn và đích, định nghĩa đặc tả của phép chuyển đổi.

Bên cạnh Tracts, các phương pháp tĩnh (static approach) khác đã được đề xuất, chẳng hạn như [26] cho phép đặc tả các hợp đồng theo cách trực quan (visual), và [27] xem xét sự khác biệt giữa mô hình đầu ra thực tế được sinh ra bởi phép chuyển đổi và mô hình đầu ra kỳ vọng. Phương pháp thứ nhất cũng dựa trên OCL để mang lại cho người dùng khả năng biểu đạt đầy đủ, trong khi phương pháp thứ hai yêu cầu nhà phát triển cung cấp các mô hình đầu ra — điều này không phải lúc nào cũng khả thi, và nếu khả thi, có thể đòi hỏi nhiều thời gian và công sức.

Một phương pháp hướng kiểm thử (test-driven method) [28] cũng được đề xuất trong lĩnh vực chuyển đổi mô hình, theo đó bản thân cài đặt của phép chuyển đổi mô hình được chú thích (annotate) bởi nhà phát triển phép chuyển đổi, loại bỏ nhu cầu về một mô tả đặc tả độc lập. Một giải pháp cho ngôn ngữ QVTo [29] có sẵn và được trình bày trong [30]. Mặc dù đạt được mục tiêu của nó, việc làm cho đặc tả của phép chuyển đổi phụ thuộc vào cài đặt ngăn cản sự tách biệt các mối quan tâm (separation of concerns), điều này càng nghiêm trọng hơn trong lĩnh vực MDE vì không có ngôn ngữ chuyển đổi chuẩn chuyên dụng nào.

Cuối cùng, phân hoạch tương đương (equivalence partitioning) [2] là một kỹ thuật kiểm thử phần mềm giả định rằng các đầu vào của chương trình có thể được chia thành các lớp loại trừ lẫn nhau (mutually exclusive) theo hành vi của chương trình trên các đầu vào đó, và trong một số trường hợp, theo cả đầu ra. Về vấn đề này, công trình trong [1] đề xuất chọn một tập hợp các thuộc tính liên quan cho các mô hình đầu vào, định nghĩa các khoảng giá trị (range) cho mỗi thuộc tính và kiểm tra rằng có ít nhất một thể hiện của mỗi thuộc tính có một giá trị trong mỗi khoảng. Tuy nhiên, đề xuất này kém biểu cảm hơn thuật ngữ phân loại vì chúng không xem xét việc sử dụng OCL, kém linh hoạt hơn và thiếu tính tự động hóa đầy đủ. Trong [31], một cơ chế sinh ca kiểm thử bằng cách phân tích các biểu thức OCL trong siêu mô hình nguồn nhằm phân hoạch không gian mô hình đầu vào đã được trình bày. Đây là một phương pháp có hệ thống tương tự với phương pháp của chúng tôi, nhưng tập trung vào các ràng buộc của mô hình nguồn gốc. Đề xuất của chúng tôi cho phép nhà phát triển phân hoạch không gian mô hình nguồn (và đích) một cách độc lập với các ràng buộc này, theo một cách linh hoạt hơn.

## V. KẾT LUẬN (CONCLUSIONS)

Bài báo này đã giới thiệu thuật ngữ phân loại, một công cụ để khảo sát các mô hình đối tượng trong bối cảnh của một mô hình lớp UML và các ràng buộc OCL đi kèm. Thuật ngữ phân loại cho phép nhà phát triển xây dựng các ca kiểm thử liên quan dưới dạng mô hình đối tượng theo một cách hướng mục tiêu (goal-oriented). Thuật ngữ phân loại xác định các lớp tương đương của ca kiểm thử, việc lựa chọn các đại diện, và việc khảo sát các thuộc tính của mô hình. Tính hữu ích của chúng đã được chứng minh bằng cách sinh ra các mô hình kiểm thử đầu vào cho các chuyển đổi mô hình.

Công trình của chúng tôi có thể được tiếp tục theo nhiều hướng khác nhau. Phép biến đổi sang logic quan hệ có thể được cải thiện và mở rộng, ví dụ, bằng cách xem xét thêm các loại tập hợp (collection kind) khác. Giao diện người dùng hiện tại cho thuật ngữ phân loại còn tối giản, có thể đặt tên cho các thuật ngữ, và những tên này cùng với các giá trị có thể được chỉ ra trong các mô hình đối tượng kết quả. Hạn chế rằng chỉ các thuật ngữ kiểu số nguyên và boolean được sử dụng có thể được nới lỏng, ít nhất các kiểu liệt kê (enumeration) không gây ra vấn đề gì. Sẽ thú vị khi xem xét nhiều hơn một đại diện lớp tương đương bằng cách phân biệt giữa thuật ngữ phân loại cấp một và cấp hai, trong đó các thuật ngữ cấp hai chỉ được áp dụng cho các lớp tương đương cấp một không rỗng. Các nghiên cứu tình huống (case study) lớn hơn nên mang lại nhiều phản hồi hơn về các tính năng và khả năng mở rộng (scalability) của phương pháp. Cuối cùng nhưng không kém phần quan trọng, cần có sự hỗ trợ công cụ riêng cho các chuyển đổi mô hình với các tùy chọn khác nhau cho nguồn và đích.

## LỜI CẢM ƠN (ACKNOWLEDGMENT)

Công trình này được tài trợ một phần bởi Quỹ Nghiên cứu Đức (DFG — German Research Foundation) theo tài trợ GO 454/19-1 và bởi các Dự án Nghiên cứu Tây Ban Nha TIN2011-23795 và TIN2014-52034-R.

## TÀI LIỆU THAM KHẢO (REFERENCES)

[1] B. Baudry, T. Dinh-Trong, J. Mottu, D. Simmonds, R. France, S. Ghosh, F. Fleurey, and Y. Le Traon, "Model transformation testing challenges," in ECMDA WS. on Integration of MDD and Model Driven Testing, 2006.

[2] I. Burnstein, Practical Software Testing. Springer-Verlag, 2003.

[3] M. Gogolla and A. Vallecillo, "Tractable model transformation testing," in Proc. of ECMFA'11, ser. LNCS, no. 6698. Springer, 2011, pp. 221–236.

[4] D. Jackson, Software Abstractions: Logic, Language, and Analysis. MIT Press, 2006.

[5] E. Torlak and D. Jackson, "Kodkod: A Relational Model Finder," in Proc. of TACAS'07, 2007, pp. LNCS 4424, 632–647.

[6] M. Gogolla, M. Kuhlmann, and L. Hamann, "Consistency, independence and consequences in UML and OCL models," in Proc. of TAP'09, ser. LNCS, vol. 5668. Springer, 2009, pp. 90–104.

[7] E. Cariou, R. Marvie, L. Seinturier, and L. Duchien, "OCL for the specification of model transformation contracts," in Proc. of the OCL and Model Driven Engineering Workshop, 2004.

[8] L. Burgueño, M. Wimmer, J. Troya, and A. Vallecillo, "Static Fault Localization in Model Transformations," IEEE Transactions on Software Engineering, vol. 41, no. 5, pp. 490–506, 2015.

[9] B. Meyer, "Applying design by contract," IEEE Computer, vol. 25, no. 10, pp. 40–51, 1992.

[10] M. Gogolla, J. Bohling, and M. Richters, "Validating UML and OCL Models in USE by Automatic Snapshot Generation," Software and Systems Modeling, vol. 4, no. 4, pp. 386–398, 2005.

[11] M. Kuhlmann and M. Gogolla, "From UML and OCL to relational logic and back," in Model Driven Engineering Languages and Systems, ser. LNCS, vol. 7590. Springer, 2012, pp. 415–431.

[12] J. Cabot, R. Clarisó, and D. Riera, "UMLtoCSP: A Tool for the Formal Verification of UML/OCL Models using Constraint Programming," in ASE 2007. ACM, 2007, pp. 547–548.

[13] K. Anastasakis, B. Bordbar, G. Georg, and I. Ray, "On Challenges of Model Transformation from UML to Alloy," Software and System Modeling, vol. 9, no. 1, pp. 69–86, 2010.

[14] M. Roldán and F. Durán, "Dynamic Validation of OCL Constraints with mOdCL," ECEASST, vol. 44, 2011.

[15] K. Ehrig, J. M. Küster, and G. Taentzer, "Generating instance models from meta models," SoSyM, vol. 8, pp. 479–500, 2009.

[16] A. Queralt, A. Artale, D. Calvanese, and E. Teniente, "OCL-Lite: Finite reasoning on UML/OCL conceptual schemas," Data Knowl. Eng., vol. 73, pp. 1–22, 2012.

[17] R. V. D. Straeten, J. P. Puissant, and T. Mens, "Assessing the Kodkod Model Finder for Resolving Model Inconsistencies," in ECMFA, ser. LNCS, vol. 6698. Springer, 2011, pp. 69–84.

[18] S. Gabmeyer, P. Brosch, and M. Seidl, "A Classification of Model Checking-Based Verification Approaches for Software Models," 2013, Proc. of the 1st VOLT Workshop.

[19] Proc. of the AMT WS., ser. CEUR WS. Proc., vol. 1277, 2014.

[20] Proc. of the VOLT WS., ser. CEUR WS. Proc., vol. 1325, 2014.

[21] M. Hibberd, M. Lawley, and K. Raymond, "Forensic debugging of model transformations," in Proc. of MODELS'07, ser. LNCS, vol. 4735. Springer, 2007, pp. 589–604.

[22] M. Wimmer, G. Kappel, J. Schönböck, A. Kusel, W. Retschitzegger, and W. Schwinger, "A Petri Net based debugging environment for QVT Relations," in Proc. of ASE'09, 2009.

[23] V. Aranega, J.-M. Mottu, A. Etien, and J.-L. Dekeyser, "Traceability mechanism for error localization in model transformation," in Proc. of ICSOFT'09, 2009.

[24] C. A. González and J. Cabot, "ATLTest: a white-box test generation approach for atl transformations," in Proc. of MODELS'12, ser. LNCS, vol. 7590. Springer, 2012, pp. 449–464.

[25] A. Vallecillo, M. Gogolla, L. Burgueño, M. Wimmer, and L. Hamann, "Formal specification and testing of model transformations," in Formal Methods for Model-Driven Engineering (SFM). Springer, 2012.

[26] E. Guerra, J. de Lara, M. Wimmer, G. Kappel, A. Kusel, W. Retschitzegger, J. Schönböck, and W. Schwinger, "Automated verification of model transformations based on visual contracts," Autom. Softw. Eng., vol. 20, no. 1, pp. 5–46, 2013.

[27] A. García-Domínguez, D. S. Kolovos, L. M. Rose, R. F. Paige, and I. Medina-Bulo, "EUnit: a unit testing framework for model management tasks," in Proc. of MODELS'11, ser. LNCS, no. 6981. Springer, 2011, pp. 395–409.

[28] P. Giner and V. Pelechano, "Test-driven development of model transformations," in Proc. of MODELS'09, ser. LNCS. Springer, 2009, vol. 5795, pp. 748–752.

[29] OMG, Meta Object Facility (MOF) 2.0 Query/View/Transformation. Version 1.1, Object Management Group, 2011.

[30] A. Ciancone, A. Filieri, and R. Mirandola, "MANTra: Towards model transformation testing," in Proc. of QUATIC'10. IEEE, 2010, pp. 97–105.

[31] C. A. González and J. Cabot, "Test Data Generation for Model Transformations Combining Partition and Constraint Analysis," in Proc. of ICMT'14, ser. LNCS, vol. 8568. Springer, 2014, pp. 25–41.

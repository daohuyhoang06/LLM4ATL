# Xác minh đầy đủ hợp đồng cho ATL bằng thực thi tượng trưng — Full Contract Verification for ATL using Symbolic Execution

**Tác giả:** Bentley James Oakes, Javier Troya, Levi Lúcio, Manuel Wimmer
**Năm:** 2018
**Tạp chí:** Software and Systems Modeling, 17(3), 815-849
**Nguồn:** NotebookLM notebook "model tranformation verification"
**Loại tài liệu:** Bản dịch sát nghĩa (đầy đủ, không tóm tắt) — do AI dịch, kèm chú thích giải nghĩa cho đoạn khó.

---

## Full Contract Verification for ATL using Symbolic Execution

**Bentley James Oakes · Javier Troya · Levi Lúcio · Manuel Wimmer**

*Ngày 28 tháng 6 năm 2016*

Bentley James Oakes — School of Computer Science, McGill University, Canada, E-mail: bentley.oakes@mail.mcgill.ca
Javier Troya — Department of Computing Languages and Systems, Universidad de Sevilla, Spain, E-mail: jtroya@us.es
Levi Lúcio — fortiss GmbH, München, Germany, E-mail: lucio@fortiss.org
Manuel Wimmer — Business Informatics Group, TU Wien, Austria, E-mail: wimmer@big.tuwien.ac.at

### Tóm tắt (Abstract)

Ngôn ngữ chuyển đổi Atlas (Atlas Transformation Language — ATL) hiện là một trong những ngôn ngữ chuyển đổi mô hình được sử dụng nhiều nhất, và đã trở thành một chuẩn thực tế (de-facto standard) trong kỹ nghệ hướng mô hình (model-driven engineering) để triển khai các chuyển đổi mô hình. Đồng thời, cộng đồng cũng nhận thức rõ rằng việc tăng cường các phương pháp xác minh chuyển đổi này một cách toàn diện (exhaustively) sẽ cho phép việc áp dụng kỹ nghệ hướng mô hình vào công nghiệp rộng rãi hơn. Trong vài năm qua đã xuất hiện nhiều đề xuất khác nhau cho việc xác minh các chuyển đổi ATL. Tuy nhiên, phần lớn các kỹ thuật này hoặc dựa trên kiểm thử không toàn diện (non-exhaustive testing), hoặc dựa trên các phương pháp chứng minh cần có sự trợ giúp của con người và/hoặc không đầy đủ (not complete).

Trong bài báo này, chúng tôi mô tả phương pháp của mình để xác minh tĩnh (statically verifying) tập con khai báo (declarative subset) của các chuyển đổi mô hình ATL. Việc xác minh này được thực hiện bằng cách dịch chuyển đổi (bao gồm các đặc trưng như bộ lọc — filters, biểu thức OCL, và các quy tắc lười — lazy rules) sang ngôn ngữ chuyển đổi mô hình DSLTrans của chúng tôi. Vì chúng tôi chỉ xử lý phần khai báo của ATL, và DSLTrans là không đầy đủ Turing (Turing-incomplete), sự thu hẹp về tính biểu đạt (expressivity) này cho phép chúng tôi sử dụng một phương pháp thực thi tượng trưng (symbolic-execution) để sinh ra các biểu diễn của tất cả các mô hình đầu vào khả dĩ cho chuyển đổi. Sau đó chúng tôi xác minh các hợp đồng tiền điều kiện/hậu điều kiện (pre-/post-condition contracts) trên các biểu diễn này, từ đó xác minh chính bản thân chuyển đổi.

> **Giải thích:** Đây là ý tưởng cốt lõi của bài báo. "Thực thi tượng trưng" (symbolic execution) nghĩa là thay vì chạy chương trình/chuyển đổi với các giá trị đầu vào cụ thể (ví dụ một gia đình cụ thể có tên "Smith"), ta chạy nó với các giá trị *tượng trưng* đại diện cho "bất kỳ giá trị nào có thể" — nhờ đó một lần "chạy tượng trưng" có thể bao phủ đồng thời vô số mô hình đầu vào cụ thể. "Turing-incomplete" (không đầy đủ Turing) nghĩa là ngôn ngữ DSLTrans không cho phép vòng lặp không giới hạn hay đệ quy tùy ý, nên mọi chương trình viết bằng nó chắc chắn sẽ dừng (terminate) — đây chính là điều kiện tiên quyết giúp việc liệt kê "tất cả các khả năng thực thi" trở nên khả thi trong hữu hạn bước, thay vì rơi vào bài toán dừng (halting problem) không thể giải được của các ngôn ngữ đầy đủ Turing như ATL với phần mệnh lệnh (imperative).

Kỹ thuật mà chúng tôi trình bày trong bài báo này là toàn diện (exhaustive) đối với tập con của các chuyển đổi mô hình ATL khai báo. Điều này có nghĩa là nếu công cụ chứng minh (prover) chỉ ra rằng một hợp đồng (contract) được thỏa mãn (holds) trên một chuyển đổi, thì cặp tiền điều kiện/hậu điều kiện của hợp đồng đó sẽ đúng cho bất kỳ mô hình đầu vào nào của chuyển đổi đó. Chúng tôi minh họa và khảo sát khả năng ứng dụng của kỹ thuật này bằng cách nghiên cứu một số chuyển đổi mô hình ATL tương đối lớn và phức tạp, bao gồm một chuyển đổi mô hình được phát triển với sự hợp tác của đối tác công nghiệp của chúng tôi. Ngoài ra, chúng tôi cũng trình bày kỹ thuật "cắt lát" (slicing) của mình. Kỹ thuật này chỉ chọn ra những quy tắc trong chuyển đổi DSLTrans cần thiết cho việc chứng minh hợp đồng, nhờ đó giảm thời gian chứng minh.

**Từ khóa (Keywords):** Chuyển đổi mô hình (Model transformation) · ATL · Xác minh hình thức (Formal verification) · Thực thi tượng trưng (Symbolic execution) · Hợp đồng (Contracts) · Tiền điều kiện/Hậu điều kiện (Pre-/Post-conditions)

## 1 Giới thiệu (Introduction)

Các chuyển đổi mô hình đã trở thành phương tiện chính để thao tác mô hình trong kỹ nghệ hướng mô hình [12], vì các chuyển đổi là một sự thỏa hiệp tuyệt vời giữa nền tảng lý thuyết vững chắc và khả năng áp dụng vào các bài toán thực tế [34]. Cụ thể, các chuyển đổi mô hình cho phép xử lý toán học dựa trên nền tảng của đồ thị (graphs) và chuyển đổi đồ thị (graph transformations), và có thể thao tác một cách tự nhiên (natively) trên các khái niệm đặc thù miền (domain-specific) được biểu diễn trong các siêu mô hình (metamodels).

Ví dụ, Ngôn ngữ chuyển đổi Atlas (ATL) [4, 28] đã trở nên nổi bật trong cộng đồng kỹ nghệ hướng mô hình. Sự thành công này là nhờ tính linh hoạt của ATL, sự hỗ trợ các chuẩn siêu mô hình hóa (meta-modelling) chính, khả năng sử dụng dựa trên sự tích hợp công cụ mạnh mẽ với thế giới Eclipse, và một cộng đồng phát triển hỗ trợ tích cực.

Do tầm quan trọng của ATL trong cả lĩnh vực học thuật lẫn công nghiệp, việc xác minh các chuyển đổi ATL có tầm quan trọng hàng đầu. Điều này là vì tính đúng đắn (correctness) của phần mềm được xây dựng bằng các kỹ thuật kỹ nghệ hướng mô hình thường phụ thuộc vào tính đúng đắn của các thao tác được thực hiện bằng các chuyển đổi mô hình. Ngoài ra, có một nhu cầu mạnh mẽ về các công cụ cho phép xây dựng phần mềm đã được xác minh (verified software), đặc biệt trong các ngành công nghiệp nơi các tiêu chuẩn chất lượng và an toàn phải được đáp ứng.

Trong bài báo này chúng tôi giải quyết vấn đề này bằng cách trình bày chi tiết kỹ thuật của chúng tôi để xác minh các hợp đồng tiền điều kiện/hậu điều kiện trực quan (visual pre-/post-condition contracts) trên các chuyển đổi ATL. Một hợp đồng được cho là được thỏa mãn (hold) trên một chuyển đổi nếu nó được thỏa mãn trên các cặp đầu vào-đầu ra của chuyển đổi đó. Nghĩa là, với mọi mô hình đầu vào mà tiền điều kiện của hợp đồng được thỏa mãn, thì hậu điều kiện của hợp đồng cũng được thỏa mãn trong mô hình đầu ra tương ứng được sinh ra bởi việc thực thi chuyển đổi. Các ràng buộc truy vết (traceability constraints) giữa các phần tử của mô hình đầu vào và đầu ra cũng có thể được yêu cầu. Nếu không, hợp đồng không được thỏa mãn, và do đó, chuyển đổi không triển khai đúng hợp đồng.

> **Giải thích:** "Hợp đồng" (contract) ở đây giống khái niệm hợp đồng trong lập trình theo hợp đồng (design by contract): một cặp phát biểu "tiền điều kiện → hậu điều kiện". Ví dụ: "NẾU mô hình đầu vào thỏa mãn điều kiện X (tiền điều kiện) THÌ mô hình đầu ra do chuyển đổi sinh ra phải thỏa mãn điều kiện Y (hậu điều kiện)". Khác với kiểm thử (testing) chỉ thử một vài mô hình đầu vào cụ thể, mục tiêu của bài báo là *chứng minh* rằng quan hệ kéo theo này đúng cho *mọi* mô hình đầu vào có thể có, không có ngoại lệ.

Ví dụ, bài báo này sử dụng làm ví dụ chạy xuyên suốt (running example) một phiên bản mở rộng của chuyển đổi Families-to-Persons nổi tiếng từ ATL zoo [2], trong đó (các) mẹ, (các) cha, (các) con gái và (các) con trai thuộc về một gia đình được dịch thành đàn ông và phụ nữ là thành viên của một cộng đồng. Một hợp đồng khả dĩ sẽ cố gắng khẳng định rằng, đối với bất kỳ mô hình đầu vào nào chứa một gia đình bao gồm một người mẹ và một người con gái, một người đàn ông sẽ được sinh ra trong cộng đồng đầu ra. Chúng ta sẽ kỳ vọng hợp đồng này không được thỏa mãn đối với chuyển đổi Families-to-Persons, bởi vì có thể tồn tại các gia đình chỉ gồm một người mẹ và con gái của bà ấy.

Đóng góp chính của kỹ thuật của chúng tôi là, nếu công cụ chứng minh của chúng tôi chứng tỏ rằng hợp đồng được thỏa mãn, thì nó sẽ được thỏa mãn cho bất kỳ mô hình đầu vào nào được cung cấp cho chuyển đổi mô hình ATL. Do đó chúng tôi có thể đảm bảo rằng người dùng có thể thực thi chuyển đổi mô hình một cách an toàn mà không cần thêm bất kỳ kiểm thử hay kiểm tra thời gian chạy (runtime checking) nào bổ sung, như đã thấy trong các phương pháp xác minh ATL khác (x. Mục 9). Ngôn ngữ hợp đồng của chúng tôi dựa trên các hợp đồng tiền điều kiện/hậu điều kiện, nhưng cũng bao gồm các toán tử logic mệnh đề (propositional logic) để kết hợp các hợp đồng. Mục 5 bao gồm một cuộc thảo luận về các hợp đồng, bao gồm các ví dụ và một bản tóm tắt về tính biểu đạt (expressiveness) của hợp đồng.

Chúng tôi chứng minh các hợp đồng được thỏa mãn hay không bằng cách dịch các chuyển đổi ATL sang các chuyển đổi được định nghĩa trong một ngôn ngữ chuyển đổi mô hình gọi là DSLTrans [10]. Một khung làm việc lý thuyết đã được phát triển cho ngôn ngữ chuyển đổi mô hình DSLTrans, trong đó có thể chứng minh rằng các hợp đồng tiền điều kiện/hậu điều kiện được thỏa mãn cho tất cả các cặp mô hình đầu vào/đầu ra sinh ra từ việc thực thi một chuyển đổi mô hình DSLTrans nhất định, hoặc không được thỏa mãn cho ít nhất một trong các cặp đầu vào/đầu ra đó [32]. Một công cụ chứng minh thuộc tính (property prover) hoàn toàn tự động dựa trên lý thuyết này đã được chứng minh là có thể áp dụng vào các bài toán công nghiệp [44].

Trong bài báo này chúng tôi tập trung vào việc xác minh phần khai báo của ATL, do sự tương đồng với ngôn ngữ chuyển đổi mô hình DSLTrans. Đây là thực hành phổ biến khi sử dụng tập con này của ngôn ngữ cho phần lớn các yêu cầu chuyển đổi. Ngoài ra, việc chỉ sử dụng ATL khai báo thường tạo ra các chuyển đổi mô hình rõ ràng hơn, dễ đọc hơn và dễ bảo trì hơn so với khi phần mệnh lệnh của ngôn ngữ được sử dụng.

Xin lưu ý rằng bài báo này là phần mở rộng của một bài báo được trình bày tại hội nghị MoDELS 2015 [36]. Bên cạnh những cải tiến tăng dần của phương pháp xác minh tổng quát, bài báo này giới thiệu bốn phần mở rộng lớn so với bài báo trước. Thứ nhất, một tiểu mục đáng kể (x. Tiểu mục 4.2.2) đã được thêm vào, giải thích cách các biểu thức Ngôn ngữ ràng buộc đối tượng (Object Constraint Language — OCL) được xử lý trong quá trình chuyển đổi từ ATL sang DSLTrans. Thứ hai, các đặc trưng ATL bổ sung hiện được xem xét trong ánh xạ, cụ thể là các helper và điều kiện (x. Mục 4.1). Thứ ba, việc đánh giá phương pháp đã được cải thiện đáng kể. Cụ thể, chúng tôi hiện cũng so sánh các chuyển đổi được sinh ra bởi HOT với các chuyển đổi xây dựng thủ công trong hai nghiên cứu tình huống (case studies) có độ phức tạp khác nhau. Cuối cùng, thuật toán cắt lát (slicing algorithm) ban đầu được mô tả trong [36] đã được cải tiến thêm và hiện được trình bày chi tiết hơn trong Mục 7.

Cấu trúc trình bày của công trình chúng tôi như sau: Mục 2 giới thiệu ngắn gọn các ngôn ngữ ATL và DSLTrans cùng các cấu trúc liên quan của chúng. Tiếp theo, Mục 3 trình bày chuyển đổi ATL Families-to-Persons mở rộng, mô tả cách nó được thực thi, và trình bày phiên bản DSLTrans tương ứng của nó.

Mục 4 cung cấp một thuật toán mã giả (pseudo-code) và ví dụ thực thi cho chuyển đổi bậc cao (higher-order transformation) tự động dịch các chuyển đổi ATL khai báo thành các đối tác DSLTrans tương đương về mặt ngữ nghĩa (semantically-equivalent) của chúng.

Mục 5 thảo luận về phương pháp chứng minh hợp đồng của chúng tôi. Điều này bao gồm việc tạo ra các hiện vật (artifacts) đại diện cho các lần thực thi chuyển đổi thông qua thực thi tượng trưng, cũng như một mô tả về cách các hợp đồng được chứng minh bằng cách sử dụng các hiện vật này. Một số hợp đồng tiền điều kiện/hậu điều kiện liên quan cho chuyển đổi Families-to-Persons mở rộng cũng được mô tả.

Các kết quả hiệu năng thu được từ việc áp dụng công cụ của chúng tôi cho một số chuyển đổi, bao gồm một chuyển đổi thu được từ đối tác công nghiệp của chúng tôi, được trình bày trong Mục 6. Các kết quả này được thảo luận trong mục đó và cho thấy kỹ thuật của chúng tôi là khả thi. Trong Mục 7, thuật toán cắt lát của chúng tôi được thảo luận, cho phép công cụ chứng minh chỉ chọn những quy tắc cần thiết để chứng minh một hợp đồng cụ thể. Các kết quả trình bày trong mục này minh chứng cho sự giảm thiểu thời gian chứng minh hợp đồng.

Mục 8 khảo sát các chuyển đổi được sinh ra bởi chuyển đổi bậc cao (HOT) của chúng tôi từ mã ATL, so với các phiên bản được xây dựng thủ công trong công trình trước đây của chúng tôi. Cả hai phiên bản của một chuyển đổi sau đó được sử dụng để chứng minh hợp đồng, nhằm khảo sát tính phù hợp của HOT để thay thế việc xây dựng thủ công các chuyển đổi DSLTrans. Cuối cùng, chúng tôi kết thúc bài báo trong các Mục 9 và 10 bằng cách mô tả công trình liên quan và thảo luận về các mối đe dọa đối với tính hợp lệ (threats to validity), kết luận của chúng tôi, và một số suy nghĩ về công việc tương lai.

## 2 Kiến thức nền tảng: ATL và DSLTrans (Preliminaries: ATL and DSLTrans)

Trong mục này, chúng tôi giới thiệu các ngôn ngữ chuyển đổi mô hình được sử dụng trong bài báo này.

### 2.1 ATL

ATL là một ngôn ngữ chuyển đổi mô hình dựa trên văn bản và dựa trên quy tắc (textual rule-based), cung cấp cả các khái niệm ngôn ngữ khai báo lẫn mệnh lệnh. Do đó nó được coi là một ngôn ngữ chuyển đổi mô hình lai (hybrid).

Một chuyển đổi ATL được cấu thành từ một tập hợp các quy tắc chuyển đổi (transformation rules) và các helper. Mỗi quy tắc mô tả cách các phần tử mô hình đích nhất định nên được sinh ra từ các phần tử mô hình nguồn nhất định. Có hai loại quy tắc: quy tắc khớp (matched rules) và quy tắc lười (lazy rules)[^1]. Các quy tắc khớp được engine thực thi ATL tự động thực thi cho mỗi lần khớp trong mô hình nguồn theo các mẫu đầu vào (input patterns) của các quy tắc khớp. Ngược lại, các quy tắc lười phải được gọi tường minh từ một quy tắc khác, điều này cho phép kiểm soát tốt hơn việc thực thi chuyển đổi.

[^1]: Chúng tôi xếp các quy tắc được gọi (called rules) của ATL vào nhóm quy tắc lười.

Ngôn ngữ ràng buộc đối tượng (OCL) được sử dụng xuyên suốt các chuyển đổi ATL như một ngôn ngữ biểu thức. Một helper có thể được xem như một hàm OCL phụ trợ, có thể được sử dụng để tránh việc trùng lặp mã OCL tại các điểm khác nhau trong chuyển đổi ATL.

Các quy tắc chủ yếu được cấu thành từ một mẫu đầu vào (input pattern) và một mẫu đầu ra (output pattern). Mẫu đầu vào được dùng để khớp các phần tử mẫu đầu vào có liên quan đến quy tắc. Mẫu đầu ra chỉ định cách các phần tử mẫu đầu ra được tạo ra từ các phần tử mô hình đầu vào được khớp bởi mẫu đầu vào. Mỗi phần tử mẫu đầu ra có thể có một số ràng buộc (bindings) có thể được sử dụng để khởi tạo giá trị của các phần tử trong mô hình đích.

Xin lưu ý rằng các khởi tạo này được thực hiện trong một giai đoạn thứ hai sau một giai đoạn đầu tiên trong đó tất cả các phần tử đầu ra được tạo ra bởi các quy tắc khớp. Sự phân tách thành hai bước này cho phép việc khởi tạo các giá trị đích độc lập với thứ tự thực thi của các quy tắc, như được giải thích chi tiết trong Mục 3.3.

> **Giải thích:** Đây là điểm mấu chốt của ngữ nghĩa thực thi ATL: việc thực thi được tách làm hai giai đoạn riêng biệt — (1) tạo ra "vỏ" (khung) của các phần tử đầu ra trước, (2) rồi mới điền các thuộc tính/tham chiếu (bindings) vào các phần tử đó. Nhờ tách hai bước này, thứ tự viết các quy tắc trong file ATL không ảnh hưởng đến kết quả cuối cùng — một quy tắc B sau có thể tham chiếu tới phần tử được một quy tắc A tạo ra dù A và B không "biết" thứ tự của nhau.

**Đoạn mã 1 (Listing 1). Trích đoạn chuyển đổi ATL Families-to-Persons**

```
module Families2Persons ; create OUT : Persons from IN : Families ;
rule Country2Community { from c : Families ! Country
to cmm : Persons ! Community ( persons <- c . families->collect (f |f . mothers ) , . . .
)}
rule Mother2Woman { from p : Families ! Parent (p . family . mothers . includes (p ) )
to w : Persons ! Woman ( fullName <- p . firstName + p . family . lastName
)}
```

Trong Đoạn mã 1, chúng tôi đưa ra một trích đoạn tối giản của chuyển đổi Families-to-Persons, được giải thích đầy đủ trong Mục 3. Cụ thể, hai quy tắc khớp được định nghĩa. Quy tắc đầu tiên chuyển đổi các Country (Quốc gia) thành các Community (Cộng đồng), trong khi quy tắc thứ hai tạo ra, cho mỗi thực thể mẹ (mother) trong mô hình nguồn, một thực thể Woman (Phụ nữ) trong mô hình đích. Xin lưu ý rằng quy tắc thứ hai cũng có một bộ lọc (filter) để chọn ra từ tập hợp các Parent (Cha/Mẹ) chỉ những người là mẹ. Các ràng buộc (bindings) được sử dụng, chẳng hạn, để khởi tạo tham chiếu persons của các Community, bằng cách thu thập tất cả các mother từ tất cả các Family (Gia đình) của Country được khớp.

Để biết thêm thông tin về ATL, độc giả quan tâm được tham khảo [28].

### 2.2 DSLTrans

DSLTrans là một engine chuyển đổi mô hình trực quan dựa trên đồ thị và dựa trên quy tắc (visual graph-based and rule-based), có hai thuộc tính quan trọng được đảm bảo theo cấu trúc (enforced by construction): mọi phép tính của nó đều vừa dừng (terminating) vừa hợp lưu (confluent) [10]. Các thuộc tính này bắt nguồn từ việc DSLTrans không cho phép các vòng lặp không giới hạn trong khi thực thi, khiến nó trở thành một ngôn ngữ tính toán không đầy đủ Turing (Turing-incomplete) [10]. Bên cạnh tầm quan trọng hiển nhiên của chúng trong thực tiễn, tính dừng và tính hợp lưu đóng vai trò then chốt trong việc triển khai kỹ thuật xác minh của chúng tôi cho các hợp đồng tiền điều kiện/hậu điều kiện.

> **Giải thích:** "Dừng" (terminating) nghĩa là chuyển đổi luôn kết thúc sau hữu hạn bước, không bao giờ chạy mãi mãi. "Hợp lưu" (confluent) nghĩa là dù các quy tắc được áp dụng theo thứ tự nào (miễn tuân theo ràng buộc về layer), kết quả cuối cùng luôn giống nhau — không có tình trạng "chạy khác thứ tự ra kết quả khác". Hai tính chất này là nền tảng để có thể "liệt kê tất cả các cách thực thi có thể" một cách hữu hạn và xác định, phục vụ cho việc thực thi tượng trưng và chứng minh hợp đồng ở các mục sau.

Các chuyển đổi mô hình được biểu diễn trong DSLTrans dưới dạng các tập hợp quy tắc viết lại đồ thị (graph rewriting rules), có một phần trên (được gọi là MatchModel), một phần dưới (ApplyModel) và, tùy chọn, các điều kiện áp dụng phủ định (negative application conditions). Cấu trúc chính được sử dụng trong việc lập lịch (scheduling) các quy tắc chuyển đổi mô hình trong DSLTrans là một tầng (layer). Mỗi quy tắc chuyển đổi mô hình trong một tầng không thể khớp trên đầu ra của bất kỳ quy tắc nào khác trong cùng tầng đó. Ngoài ra, các quy tắc không thể sửa đổi đồ thị đầu vào trong giai đoạn viết lại (được gọi là thực thi ngoài chỗ — out-place execution). Các tầng được tổ chức tuần tự và mô hình đầu ra thu được từ việc thực thi một tầng nhất định được truyền làm đầu vào cho tầng tiếp theo trong chuỗi.

Một quy tắc DSLTrans có thể khớp trên các phần tử của mô hình đầu vào của chuyển đổi và cũng khớp trên các phần tử đã được sinh ra cho đến thời điểm đó trong mô hình đầu ra. Việc khớp trên các phần tử của mô hình đầu ra của một chuyển đổi được thực hiện bằng cách sử dụng một cấu trúc của DSLTrans gọi là liên kết ngược (backward links). Các liên kết ngược cho phép khớp trên các dấu vết (traces) giữa các phần tử trong mô hình đầu vào và đầu ra của chuyển đổi. Các dấu vết này được engine chuyển đổi DSLTrans xây dựng một cách tường minh trong quá trình thực thi quy tắc.

Ví dụ, chúng tôi minh họa trong Hình 1 một quy tắc trong ngôn ngữ DSLTrans. Khi một quy tắc được thực thi, đồ thị trong MatchModel của quy tắc được tìm kiếm trong mô hình đầu vào của chuyển đổi, cùng với các lớp trong ApplyModel của quy tắc được kết nối với các liên kết ngược. Một ví dụ về liên kết ngược có thể được quan sát trong Hình 1 dưới dạng một đường chấm nối lớp khớp Country và lớp khớp Community. Trong phần viết lại (rewrite) của việc áp dụng quy tắc, các thực thể của các lớp trong ApplyModel của quy tắc không được kết nối với các liên kết ngược, cùng với các quan hệ liền kề của chúng, được tạo ra trong mô hình đầu ra.

*Hình 1. Một ví dụ về quy tắc DSLTrans*

Ví dụ, quy tắc UnionWomanRule trong Hình 1 sẽ khớp trên một phần tử Country được kết nối với một phần tử Family được kết nối với một phần tử Parent. Nếu các phần tử này được tìm thấy trong mô hình đầu vào cùng với các phần tử Community và Woman tương ứng trong mô hình đầu ra, thì một quan hệ persons sẽ được tạo ra giữa các phần tử đầu ra đó.

Mặc dù không có mặt trong quy tắc này, việc sao chép các giá trị thuộc tính đối tượng từ MatchModel sang ApplyModel của các quy tắc cũng là một phần của ngôn ngữ DSLTrans, như được minh họa trong Mục 3.4.

Bên cạnh các cấu trúc được trình bày trong ví dụ ở Hình 1, DSLTrans còn có một số cấu trúc khác: khớp tồn tại (existential matching) cho phép chỉ chọn một kết quả khi một lớp khớp của một quy tắc khớp với mô hình đầu vào, liên kết gián tiếp (indirect links) cho việc khớp bắc cầu (transitive matching) trên các quan hệ chứa (containment relations) trong mô hình đầu vào, và các điều kiện áp dụng phủ định cho phép người thiết kế chuyển đổi chỉ định các điều kiện mà theo đó một quy tắc không nên khớp. Các cấu trúc này hiện không được sử dụng trong phương pháp xác minh của chúng tôi, và độc giả quan tâm được tham khảo [10] để biết thêm thông tin.

## 3 Chuyển đổi Families-to-Persons mở rộng (The Extended Families-to-Persons Transformation)

Làm ví dụ chạy xuyên suốt, chúng tôi trình bày một phiên bản mở rộng của chuyển đổi Families-to-Persons được mô tả trong [36]. Chuyển đổi Families-to-Persons gốc có thể được tìm thấy trong ATL zoo [2], và cũng đã được thảo luận trong một số công trình liên quan về xác minh và kiểm thử [25].

Chúng tôi chọn chuyển đổi Families-to-Persons này làm ví dụ chạy xuyên suốt vì hai lý do. Thứ nhất, nó chuyển đổi các miền (domains) có các khái niệm dễ hiểu đối với bất kỳ ai (x. Mục 3.1). Thứ hai, nó có một mức độ phức tạp nhất định vì sử dụng nhiều đặc trưng có sẵn trong ngôn ngữ ATL (x. Mục 3.2).

### 3.1 Các miền chuyển đổi (Transformation Domains)

Các siêu mô hình đầu vào và đầu ra của chuyển đổi này được thể hiện trong Hình 2. Xin lưu ý rằng các lớp trừu tượng được biểu diễn bằng màu xám và tên in nghiêng, và các quan hệ kế thừa được biểu diễn bằng màu xám.

Siêu mô hình đầu vào, siêu mô hình Families Extended, có lớp Country làm phần tử gốc. Một Country được cấu thành từ các companies (công ty), families (gia đình) và cities (thành phố). Một Family có một lastName (họ), được registeredIn (đăng ký tại) một Neighborhood (khu vực lân cận) và có thể có bất kỳ số lượng mothers và fathers nào, là các Parent, và những người này có thể lần lượt worksIn (làm việc tại) một Company. Nó cũng có thể chứa bất kỳ số lượng sons và daughters nào, là các Child, và mỗi child goesTo (đi học tại) một School. Cả parent và child đều là các Member có một firstName (tên), thuộc về một family và mỗi người trong số họ livesIn (sống tại) một City.

Một City có thể chứa các company, và một Company, đến lượt nó, có thể hiện diện tại (quan hệ isIn) nhiều city khác nhau. Một City được cấu thành từ các neighborhood, và các neighborhood này có thể có các school, nơi một số học sinh được đăng ký. Mỗi School có các Service (dịch vụ), và những dịch vụ này có thể là đặc biệt (special), dành cho những học sinh có nhu cầu đặc biệt, hoặc đơn giản là cung cấp các dịch vụ thông thường (ordinary). Cuối cùng, các country, city, company, neighborhood và school có một thuộc tính name (tên), được kế thừa từ lớp trừu tượng NamedElement.

*Hình 2(a). Siêu mô hình Families Extended*

Siêu mô hình đầu ra, Persons Extended, được thể hiện trong Hình 2(b). Lớp gốc là Community, được cấu thành từ các person, townHall (tòa thị chính) và association (hiệp hội). Một Person có một fullName (họ tên đầy đủ) và có thể là một Man (nam giới) hoặc một Woman (nữ giới). Một Association có một Committee (ủy ban) đưa ra các quyết định. Mỗi TownHall có một danh sách các worker (tất cả những người được tuyển dụng), tổ chức một Committee để đưa ra quyết định, và cũng quản lý một số district (khu vực). Một District có thể chứa một số facility (cơ sở), hoặc thuộc loại SpecialFacility dành cho những người có nhu cầu đặc biệt, hoặc OrdinaryFacility. Mỗi Facility có thể đăng ký một số person làm thành viên (members). Cuối cùng, các association, town hall, committee, district và facility có một thuộc tính name.

*Hình 2(b). Siêu mô hình Persons Extended. Fig. 2 Các siêu mô hình của chuyển đổi Families-to-Persons Extended*

### 3.2 Giải thích chuyển đổi (Transformation Explanation)

Đoạn mã 2 (Listing 2) hiển thị mã ATL cho chuyển đổi mô hình Families-to-Persons Extended, được cấu thành từ 10 quy tắc. Để giải thích tốt hơn về chuyển đổi và ánh xạ sang ngôn ngữ DSLTrans (x. Mục 4.2.1), chúng tôi đã chú thích nhiều dòng trong đoạn mã như sau:

- Ri là viết tắt của quy tắc i (rule i)
- IPEij cho phần tử mẫu đầu vào (in-pattern element) j trong quy tắc i
- Fi cho bộ lọc (filter) của quy tắc i
- OPEij cho phần tử mẫu đầu ra (out-pattern element) j của quy tắc i
- Bijk cho ràng buộc (binding) k trong phần tử mẫu đầu ra đơn giản j của quy tắc i

Trong ATL, phần from của các quy tắc được gọi là mẫu đầu vào (in-pattern) và được cấu thành từ các phần tử mẫu đầu vào và một bộ lọc tùy chọn. Các phần tử mẫu đầu vào này đại diện cho các phần tử từ mô hình đầu vào được khớp bởi quy tắc, miễn là chúng thỏa mãn bộ lọc. Phần to của quy tắc được gọi là mẫu đầu ra (out-pattern) và được cấu thành từ các phần tử mẫu đầu ra đại diện cho các phần tử được tạo ra trong mô hình đầu ra. Chúng chứa các ràng buộc, được sử dụng để khởi tạo các đặc trưng (features) của các phần tử được tạo ra. Đặc trưng được khởi tạo bởi một ràng buộc có thể là một thuộc tính (attribute) hoặc một tham chiếu (reference) đến một phần tử được tạo khác.

Trong Đoạn mã 2, chuyển đổi tạo ra một Community từ mỗi Country, như được chỉ định bởi R1. Sáu ràng buộc của OPE11 được sử dụng để khởi tạo các tham chiếu. Xin lưu ý rằng khi cùng một thuộc tính đại diện cho một tham chiếu được khởi tạo trong nhiều hơn một ràng buộc (thuộc tính persons trong B111, B112, B113 và B114 trong trường hợp của chúng ta), kết quả là hợp (union) của các phần tử được truy xuất trong tất cả các ràng buộc đó.

Bây giờ hãy tập trung vào B115, khởi tạo quan hệ townHalls của Community được tạo ra. Nó gán các city của Country khớp với biểu thức (c.cities). Tuy nhiên, do siêu mô hình đầu ra, quan hệ townHalls của Community được tạo ra trong mô hình đầu ra không thể trỏ đến một City trong mô hình đầu vào. Trên thực tế, những gì quan hệ này thực sự sẽ trỏ đến là phần tử trong mô hình đầu ra được tạo ra từ phần tử City tương ứng của mô hình đầu vào. Do đó, phải có một quy tắc tạo ra thứ gì đó từ các phần tử City.

Trong ví dụ của chúng ta, đó là R6, tạo ra một TownHall từ City được khớp. Do đó, B115 khởi tạo quan hệ townHall của Community được tạo ra trong OPE11 bằng cách tham chiếu đến các phần tử TownHall được tạo ra từ các phần tử City được tham chiếu bởi phần tử Country được khớp trong IPE1. Để làm điều này, ATL sử dụng một cơ chế dấu vết nội bộ (internal trace mechanism), trong đó các tương ứng giữa các phần tử trong mô hình đầu vào và đầu ra được theo dõi.

**Đoạn mã 2 (Listing 2). Chuyển đổi ATL Families-to-Persons Extended**

```
module Families2Persons_Extended ; create OUT : Persons_Extended from IN : Families_Extended ;
rule Country2Community { -- R1
from c : Families ! Country -- IPE11
to cmm : Persons ! Community ( -- OPE11
persons <- c . families->collect (f |f . fathers ) , -- B111
persons <- c . families->collect (f |f . mothers ) , -- B112
persons <- c . families->collect (f |f . sons ) , -- B113
persons <- c . families->collect (f |f . daughters ) , -- B114
townHalls <- c . cities , -- B115
associations <- c . cities->collect (cty | cty . companies -> collect (cmp | Tuple{ct=cty , cm=cmp}) ) -- B116
)}
rule Father2Man { -- R2
from p : Families ! Parent -- IPE21
(p . family . fathers . includes (p ) ) -- F2
to m : Persons ! Man ( -- OPE21
fullName <- p . firstName + p . family . lastName -- B211
)}
rule Mother2Woman { -- R3
from p : Families ! Parent -- IPE31
(p . family . mothers . includes (p ) ) -- F3
to w : Persons ! Woman ( -- OPE31
fullName <- p . firstName + p . family . lastName -- B311
)}
rule Daughter2Woman { -- R4
from ch : Families ! Child -- IPE41
(ch . family . daughters . includes (ch ) ) -- F4
to w : Persons ! Woman ( -- OPE41
fullName <- ch . firstName + ch . family . lastName -- B411
)}
rule Son2Man { -- R5
from ch : Families ! Child -- IPE51
(ch . family . sons . includes (ch ) ) -- F5
to m : Persons ! Man ( -- OPE51
fullName <- ch . firstName + ch . family . lastName -- B511
)}
rule City2TownHall{ -- R6
from c : Families ! City -- IPE61
to th : Persons ! TownHall ( -- OPE61
name <- c . name + ' TownHall ' , -- B611
workers <- c . companies -> collect (cmp | cmp . employees ) -> flatten ( ) -> select (em | em . livesIn=c ) , -- B612
committee <- cmt , -- B613
districts <- c . neighborhoods -- B614
) , cmt : Persons ! Committee ( -- OPE62
name <- c . name + ' TownHall Committee ' -- B621
)}
rule CityCompany2Association{ -- R7
from ct : Families ! City , -- IPE71
cm : Families ! Company -- IPE72
(ct . companies . includes (cm ) ) -- F7
to a : Persons ! Association ( -- OPE71
name <- ct . name + cm . name -- B711
committee <- thisModule . resolveTemp (ct , ' cmt ' ) -- B712
)}
rule Neighborhood2District{ -- R8
from n : Families ! Neighborhood -- IPE81
(Families ! Family . allInstances ( ) -> exists (f |f . registeredIn=n ) ) -- F8
to d : Persons ! District ( -- OPE81
name <- n . name , facilities <- n . schools -> select (sch | sch . ordinary -> notEmpty ( ) ) -> collect (sch | thisModule . CreateOrdinaryFacility (sch ) ) , -- B811
facilities <- n . schools -> select (sch | sch . special -> notEmpty ( ) ) -> collect (sch | thisModule . CreateSpecialFacility (sch ) ) -- B812
)}
lazy rule CreateOrdinaryFacility{ -- R9
from sch : Families ! School -- IPE91
to of : Persons ! OrdinaryFacility ( -- OPE91
name <- ' Ordinary Facility Service for school '
+ sch . name , -- B911
members <- sch . students -- B912
)}
lazy rule CreateSpecialFacility{ -- R10
from sch : Families ! School -- IPE101
to sf : Persons ! SpecialFacility ( -- OPE101
name <- ' Special Facility Service for school ' + sch . name , -- B1011
members <- sch . students -- B1012
)}
```

Để làm rõ hơn, Hình 3 minh họa việc tạo ra một mô hình đầu ra từ một mô hình đầu vào bằng cách áp dụng chuyển đổi Families-to-Persons Extended. Phía bên trái của hình hiển thị một mô hình tuân theo (conforms to) siêu mô hình Families Extended thấy trong Hình 2(a). Phía bên phải của hình trình bày mô hình đầu ra thu được, tuân theo siêu mô hình Persons Extended (x. Hình 2(b)).

Lưu ý rằng các thuộc tính bị bỏ qua trong Hình 3, và các lớp cùng tham chiếu được tô màu để cải thiện khả năng đọc của hình. Các phần tử cũng được gán một định danh (identifier) để chỉ ra chúng thuộc loại nào (ví dụ, Cmp1 là một phần tử thuộc loại Company), và các tham chiếu có cùng màu với phần tử nguồn của chúng. Trong trường hợp các tham chiếu hai chiều (bidirectional references), tham chiếu có màu của cả hai phần tử, nhưng các nhãn mô tả một đầu cụ thể của tham chiếu có màu của phần tử nguồn. Vì mục đích đơn giản hóa và dễ đọc, không phải tất cả các nhãn đều được đưa vào (ví dụ, thiếu các nhãn livesIn), mặc dù hầu hết chúng đều có mặt. Vì các thuộc tính và tham chiếu của các phần tử được tạo ra được khởi tạo bằng các ràng buộc, chúng tôi đã chú thích ràng buộc chịu trách nhiệm khởi tạo mỗi tham chiếu (một lần nữa, các thuộc tính bị bỏ qua) trong mô hình đầu ra.

Phần trung tâm của Hình 3 thể hiện các dấu vết nội bộ được ATL sử dụng để lưu giữ thông tin về việc phần tử nào trong mô hình đầu ra được tạo ra từ phần tử nào trong mô hình đầu vào và quy tắc nào chịu trách nhiệm thực hiện việc đó. Chúng ta có thể thấy rằng các dấu vết cũng lưu giữ thông tin về định danh của các phần tử mẫu đầu vào và phần tử mẫu đầu ra của mỗi quy tắc, điều này đặc biệt hữu ích cho việc triển khai thao tác resolveTemp (x. Mục 3.3).

*Hình 3. Ví dụ thực thi của chuyển đổi Families-to-Persons Extended (sơ đồ mô hình đầu vào, các dấu vết ATL và mô hình đầu ra tương ứng)*

Hình 3 do đó minh họa những gì đã được mô tả trước đó, cụ thể là Comm1 được tạo ra từ Ctry1 bởi R1. Tham chiếu townHalls của nó trỏ đến TH1, được tạo ra bởi R6 từ Cty1, thuộc về Ctry1.cities, và được gán bởi B115.

Cả R2 và R3 đều nhận một Parent làm đầu vào. Ở đây, một bộ lọc được sử dụng để xác định xem Parent đó là cha (R2) hay mẹ (R3). Ví dụ, các parent Par1 và Par2 được chuyển thành một Man với R2, trong khi Par3 được chuyển thành một Woman với R3. Điều tương tự xảy ra với các Child. Các ràng buộc B111 - B114 được sử dụng để khởi tạo tham chiếu person cho Community được tạo ra trong OPE11 cho tất cả các parent và child. Chúng ta thấy rằng một thao tác collect của OCL là cần thiết, vì chúng ta cần truy xuất các phần tử thuộc các loại cụ thể.

B116 cho thấy một trường hợp đặc biệt trong đó toán tử Tuple được sử dụng. Trong trường hợp này, thao tác collect truy xuất các cặp phần tử {City, Company}, và các phần tử đầu ra được tạo ra bởi các cặp này được gán vào tham chiếu associations. Do đó, phải có một quy tắc nhận các cặp này trong mẫu đầu vào. Trong ví dụ của chúng ta, đó là R7, được cấu thành từ IPE71 và IPE72, trong đó F7 đảm bảo rằng Company nằm trong City. Kết quả là, theo ví dụ của chúng ta, Asso1 được tạo ra từ Cty1 và Cmp1.

B612 sử dụng cả hai toán tử collect và select để chỉ chọn ra những employee của các company nằm trong City được khớp (IPE61) mà thực sự sống tại city đó. Trong ví dụ của chúng ta, Par1 và Par3 được chọn, do đó tham chiếu workers của TH1 trỏ đến Wom2 và Man2, được tạo ra từ Par1 và Par3, tương ứng.

Cuối cùng, đáng chú ý là việc sử dụng các quy tắc lười (R9 và R10). Các quy tắc lười chỉ được thực thi khi chúng được gọi từ các quy tắc khác. Điều này có nghĩa là chúng chỉ tạo ra các phần tử khi chúng nhận được các lời gọi.

Trong ví dụ của chúng ta, các quy tắc này được gọi từ R8, và cụ thể là từ các ràng buộc B811 và B812. Hãy tập trung vào ràng buộc B811. R8 tạo ra một District (OPE81) từ một Neighborhood (IPE81) miễn là có ít nhất một Family được đăng ký tại neighborhood đó (F8). Sau đó, để khởi tạo tham chiếu facilities của nó, trong B811 nó chọn ra những school trong Neighborhood có một Service thông thường và thu thập kết quả được tạo ra bởi quy tắc lười CreateOrdinaryFacility.

Quy tắc lười này (R9) nhận làm tham số các school đã được chọn. Nó tạo ra một OrdinaryFacility (OPE91) từ School (IPE91) và khởi tạo tham chiếu members của nó bằng các học sinh của school. Trong Hình 3, chúng tôi biểu diễn một lần thực thi kết hợp của R8 và R9, vì quy tắc sau được thực thi cùng lúc với quy tắc trước do việc gọi nó. Tình huống tương tự xảy ra với R8 và R10.

### 3.3 Ngữ nghĩa ATL và việc thực thi chuyển đổi (ATL Semantics and Transformation Execution)

Ngữ nghĩa của ATL định nghĩa cách một chuyển đổi ATL được thực thi nội bộ. Tuy nhiên, ngôn ngữ ATL đã được mô tả trong cộng đồng theo một cách trực quan và không hình thức, thông qua các định nghĩa về các đặc trưng chính của nó bằng ngôn ngữ tự nhiên [47]. Sự thiếu chặt chẽ trong mô tả này có thể dễ dàng dẫn đến những sự thiếu chính xác và hiểu lầm có thể cản trở việc sử dụng và phân tích đúng đắn ngôn ngữ, cũng như việc phát triển các công cụ đúng đắn và có khả năng tương tác (interoperable). Cách triển khai tham chiếu khác của ATL có sẵn dưới dạng các siêu mô hình cho ngôn ngữ và máy ảo (virtual machine) của nó, cùng với một trình biên dịch từ ngôn ngữ sang máy ảo và một trình thông dịch cho máy ảo. Vấn đề của loại triển khai này là nó không đủ trừu tượng để cung cấp một ngữ nghĩa có ý nghĩa, theo cách độc lập với triển khai (implementation-independent). Do đó, với mục đích sau này mô tả ánh xạ từ ATL sang DSLTrans, mục tiêu của tiểu mục này là giải thích ngữ nghĩa của ATL và cụ thể hóa chúng trong ví dụ chạy xuyên suốt của chúng ta.

Việc thực thi các chuyển đổi ATL được chia thành hai bước chính: tạo phần tử (element creation) và khởi tạo đặc trưng (features initialization). Tuy nhiên, quy trình hai bước này không được thể hiện tường minh trong ATL, và được mô tả ở đây để giảm khoảng cách khái niệm (conceptual delta) giữa ATL và DSLTrans.

Bước đầu tiên của việc thực thi là việc tạo ra các phần tử đích và các liên kết dấu vết (trace links) đã đề cập ở trên, việc tạo ra các liên kết này diễn ra một cách ngầm định và tự động bởi ATL. Trong Hình 3, bước này tạo ra tất cả các phần tử trong mô hình đầu ra (nhưng không thiết lập các tham chiếu hay thuộc tính của chúng) cũng như các liên kết dấu vết được chỉ định trong phần trung tâm của hình. Điều này có nghĩa là các phần tử mẫu đầu vào được lấy từ mô hình đầu vào và các phần tử mẫu đầu ra được tạo ra trong mô hình đầu ra.

Trong bước thứ hai, các đặc trưng của các phần tử được tạo ra trong mô hình đầu ra được thiết lập. Điều này có nghĩa là các ràng buộc được thực thi và giải quyết (resolved). Để khởi tạo các tham chiếu, ATL sử dụng các liên kết dấu vết nội bộ. Mặc dù các tham chiếu được tự động giải quyết như đã giải thích trong mục trước, vẫn tồn tại một thao tác, gọi là thao tác resolveTemp, có thể được sử dụng để giải quyết tường minh các tham chiếu. Nó cho phép trỏ đến bất kỳ phần tử mô hình đích nào được sinh ra từ một (chuỗi) phần tử mẫu đầu vào cho trước. Nó đặc biệt hữu ích (và trên thực tế, cần thiết) khi tham chiếu được chỉ định trong một ràng buộc không phải trỏ đến phần tử mẫu đầu ra đầu tiên được tạo ra trong một quy tắc khác, mà đến bất kỳ phần tử nào trong số các phần tử còn lại.

> **Giải thích:** `resolveTemp` giải quyết một vấn đề: khi một quy tắc tạo ra *nhiều* phần tử đầu ra (ví dụ quy tắc R6 tạo ra cả TownHall lẫn Committee), và một quy tắc khác cần tham chiếu cụ thể đến phần tử thứ hai (Committee) chứ không phải phần tử đầu tiên (TownHall), cơ chế phân giải tham chiếu ngầm định mặc định của ATL không đủ — ta phải gọi tường minh `thisModule.resolveTemp(nguồn, tên_biến_đích)` để "tra cứu" chính xác phần tử đó trong bảng dấu vết (trace).

Trong ví dụ chạy xuyên suốt của chúng ta, B712 chứa một thao tác thuộc loại này. Do đó, một Association chứa một tham chiếu tên là committee phải tham chiếu đến Committee được tạo ra từ City được khớp trong IPE71. Như chúng ta thấy trong R6, mỗi City tạo ra một TownHall và một Committee. Cái sau là cái mà chúng ta muốn được tham chiếu từ B712. Vì nó là phần tử thứ hai được tạo ra trong quy tắc, chúng ta cần thao tác thisModule.resolveTemp(ct,'cmt'), trong đó ct là định danh của IPE71 và cmt là định danh của phần tử mẫu đầu ra tạo ra Committee (OPE62 trong ví dụ của chúng ta).

Như chúng tôi đã nhấn mạnh trong mục trước, thao tác resolveTemp cung cấp lý do để lưu trữ các định danh của các phần tử mẫu đầu vào và phần tử mẫu đầu ra trong các liên kết dấu vết.

### 3.4 Biểu diễn DSLTrans (DSLTrans Representation)

Hình 4 hiển thị chuyển đổi DSLTrans tương ứng với chuyển đổi ATL Families-to-Persons Extended được thể hiện trong Đoạn mã 2. Hãy lưu ý ở đây rằng chúng tôi đã loại bỏ năm quy tắc khỏi hình để cải thiện tính rõ ràng trực quan. Có một đường thẳng đứng chấm màu xanh cho mỗi quy tắc trong số này, ở vị trí mà các quy tắc đã bị loại bỏ. Các quy tắc bị bỏ sót tương tự như những quy tắc bao quanh chúng, và do đó có thể được bỏ qua một cách an toàn trong phần giải thích của chúng tôi.

*Hình 4. Phiên bản DSLTrans của chuyển đổi Families-to-Persons Extended*

Quá trình xây dựng một chuyển đổi DSLTrans từ một chuyển đổi ATL được mô tả trong mục tiếp theo. Hiện tại, xin lưu ý rằng chuyển đổi DSLTrans thu được từ ATL thông qua chuyển đổi bậc cao chỉ bao gồm một quy tắc trên mỗi tầng, nghĩa là tất cả các quy tắc thực thi tuần tự. Điều này là do ngữ nghĩa tuần tự của ATL mà chúng tôi tái tạo trong DSLTrans.

Ngoài ra, xin lưu ý rằng việc sao chép thuộc tính được biểu diễn bằng các mũi tên từ ApplyModel của quy tắc tới MatchModel, chẳng hạn như trong quy tắc Neighborhood2District, nơi District được tạo ra nhận cùng tên với Neighborhood được khớp. Chuỗi ký tự của một thuộc tính của một phần tử được tạo ra cũng có thể được khởi tạo bằng phép nối (concatenation) của một số chuỗi. Ví dụ, trong quy tắc Father2Man, họ tên đầy đủ của Man được tạo ra đến từ việc nối tên của Parent được khớp và họ của Family của người đó. Hoặc nó có thể được gán chuỗi ký tự của một thuộc tính của một phần tử trong MatchModel được nối với một chuỗi cho trước, chẳng hạn như trong quy tắc City2TownHall.

## 4 Ánh xạ ATL vào DSLTrans (Mapping ATL into DSLTrans)

Trong mục này trước tiên chúng tôi trình bày các đặc trưng của phần khai báo của ATL mà chúng tôi xem xét cho việc dịch sang DSLTrans. Sau đó, chúng tôi mô tả ánh xạ giữa các chuyển đổi ATL và các chuyển đổi DSLTrans, nhấn mạnh việc dịch các toán tử OCL được chọn. Cuối cùng, chúng tôi giải thích việc triển khai ánh xạ này.

### 4.1 Tập con ATL được chọn (ATL Subset Selected)

Trong khi phiên bản trình dịch của chúng tôi từ ATL sang DSLTrans được trình bày tại hội nghị MoDELS 2015 [36] xem xét một tập lớn các đặc trưng có sẵn trong phần khai báo của ngôn ngữ ATL, phiên bản hiện tại của chúng tôi xem xét gần như toàn bộ tập đặc trưng. Như thể hiện trong Bảng 1, giờ đây chúng tôi xử lý các helper và điều kiện (conditions). Vì chúng tôi xem xét gần như tất cả các đặc trưng trong phần khai báo của ATL, chúng tôi có thể khẳng định rằng việc triển khai hiện tại của chuyển đổi bậc cao đủ mạnh để có giá trị quan tâm.

Các đặc trưng duy nhất không được xem xét cho việc dịch là khối using và các quy tắc lười duy nhất (unique lazy rules). Khối using hiếm khi được sử dụng trong các chuyển đổi mô hình ATL, vì đây là một cơ chế tùy chọn để khai báo các hằng số cục bộ (local constants) trong các quy tắc ATL. Do đó, cùng một quy tắc có thể được viết mà không sử dụng khối này bằng cách luôn viết nội dung hằng số thay vì định danh hằng số. Một ví dụ về chuyển đổi ATL chứa một khối using và một chuyển đổi tương đương không có khối này có thể được tìm thấy trên trang web của chúng tôi [3].

Đối với các quy tắc lười duy nhất, chúng sẽ yêu cầu logic đặc biệt để được dịch sang DSLTrans. Trong một chuyển đổi ATL, lần đầu tiên một quy tắc lười duy nhất được gọi, với (một tập hợp) tham số cụ thể, nó tạo ra một hoặc nhiều phần tử trong mô hình đầu ra. Những lần sau khi quy tắc được gọi với cùng (các) tham số đó, các phần tử đã được tạo ra trước đó sẽ được truy xuất lại, nhưng không được tạo lại. Việc dịch hành vi này sẽ yêu cầu việc đưa vào một điều kiện ở phía DSLTrans. Tuy nhiên, vì không có sự phân nhánh (branching) hay bất kỳ cơ chế nào để chỉ định điều kiện trong DSLTrans, chúng tôi không dịch các quy tắc lười duy nhất sang DSLTrans. Dù sao, mặc dù các quy tắc lười duy nhất là một đặc trưng mạnh mẽ của ATL, không có nhiều chuyển đổi ATL hiện có [2] sử dụng chúng.

Vì DSLTrans theo mặc định là dừng và hợp lưu, chúng tôi yêu cầu rằng chuyển đổi ATL cũng phải dừng và hợp lưu trước khi nó có thể được dịch sang DSLTrans bằng phương pháp của chúng tôi. Điều này dễ dàng đạt được bằng cách tuân theo một số hướng dẫn và thực hành tốt khi phát triển một chuyển đổi ATL.

Thứ nhất, vì chúng tôi đang sử dụng phần khai báo của ATL, các helper không được sử dụng như các biến toàn cục, vì vậy không có thông tin nào được lưu trữ trong chúng. Thứ hai, chúng ta phải đảm bảo rằng các phép điều hướng (navigations) kết thúc sau một số bước xác định (bằng "bước" chúng tôi muốn nói đến việc duyệt qua một tham chiếu), vì vậy chúng ta phải tránh các helper đệ quy và các quy tắc lười đệ quy. Thứ ba, vì chúng ta đang xử lý các chuyển đổi ngoài chỗ (out-place transformations), chỉ những chuyển đổi ATL được viết với chế độ thực thi mặc định (chứ không phải chế độ được gọi là chế độ tinh chỉnh — refining mode [46,47]) mới có thể được chuyển đổi. Xin lưu ý rằng phần lớn các chuyển đổi ATL hiện tại được viết bằng chế độ thực thi mặc định [2].

Cuối cùng, chúng tôi yêu cầu chuyển đổi ATL không được phát sinh bất kỳ lỗi biên dịch hay lỗi thời gian chạy nào [20]. Các lỗi biên dịch chỉ ra, chẳng hạn, các lỗi trong cú pháp, hoặc việc một phần tử mô hình đích đang được sử dụng làm đầu vào cho một quy tắc. Thật vậy, mô hình đích không thể điều hướng (navigable), và chỉ có thể ghi (writable) [28]. Nếu chúng ta muốn truy cập mô hình đích trong chuyển đổi ATL của mình, chúng ta phải sử dụng tường minh hàm resolveTemp, như đã thấy trong ràng buộc B712 của Đoạn mã 2 và được giải thích trong Mục 3.3. Các lỗi thời gian chạy được phát sinh, ví dụ, khi cùng một phần tử mô hình nguồn đã được sử dụng làm phần tử đầu vào cho hai quy tắc khớp khác nhau.

**Bảng 1. Các đặc trưng của ATL khai báo được xem xét**

| Đặc trưng | Được hỗ trợ | Đặc trưng | Được hỗ trợ | Đặc trưng | Được hỗ trợ | Đặc trưng | Được hỗ trợ |
|---|---|---|---|---|---|---|---|
| Quy tắc khớp (Matched Rules) | ✓ | Bộ lọc (Filters) | ✓ | Quy tắc lười (Lazy Rules) | ✓ | Biểu thức OCL (OCL Expressions) | ✓ |
| Nhiều ràng buộc (Several Bindings) | ✓ | Helper | ✓ | Nhiều phần tử mẫu đầu vào (Several InPatternElements) | ✓ | Điều kiện (Conditions) | ✓ |
| Nhiều phần tử mẫu đầu ra (Several OutPatternElements) | ✓ | Khối using (Using Block) | ✗ | Thao tác ResolveTemp | ✓ | Quy tắc lười duy nhất (Unique Lazy Rules) | ✗ |

Để đảm bảo tất cả các điểm đã đề cập được thỏa mãn, chúng ta có thể sử dụng phương pháp của Troya và Vallecillo [47]. Theo đó, chuyển đổi ATL được dịch sang một miền hình thức (formal domain), Maude [19], nơi các kiểm tra tính dừng và tính hợp lưu có thể được thực hiện dễ dàng.

Cuối cùng, xin lưu ý rằng, trong nguyên mẫu (prototype) hiện tại của chúng tôi, chúng tôi đã sử dụng các phiên bản ATL 3.5 (trong Eclipse Luna) và 3.6 (trong Eclipse Mars).

### 4.2 Ánh xạ giữa ATL và DSLTrans (Mapping between ATL and DSLTrans)

#### 4.2.1 Ngữ nghĩa (Semantics)

Để ánh xạ ATL vào DSLTrans, chúng ta phải biểu diễn tường minh ngữ nghĩa của ATL trong DSLTrans. Điều này bao gồm việc sử dụng các liên kết ngược để làm tường minh trong DSLTrans bước ràng buộc (binding step) vốn được ngầm định hiện diện trong ATL để giải quyết các quan hệ giữa các phần tử được tạo ra trong chuyển đổi. Xin nhắc lại rằng ngữ nghĩa của ATL đã được mô tả trong Mục 3.3.

Để làm rõ, trong phần thảo luận sau đây chúng tôi giải thích ánh xạ này một cách tổng quát và sau đó cụ thể hóa nó cho nghiên cứu tình huống Families-to-Persons Extended được thể hiện trong Đoạn mã 2, để mô tả cách biểu diễn DSLTrans một phần được thể hiện trong Hình 4 được xây dựng. Cụ thể, chúng tôi giải thích cách chuyển đổi từ ATL sang DSLTrans hoạt động, nghĩa là, chúng tôi định nghĩa ngữ nghĩa của nó bằng văn bản. Ngữ nghĩa cho ánh xạ được chia thành hai bước, để phản ánh ngữ nghĩa của ATL.

**Ngữ nghĩa tổng quát cho Bước 1** Trong bước đầu tiên, mỗi quy tắc khớp trong ATL được dịch thành một quy tắc trong DSLTrans. Các quy tắc khớp được engine ATL khớp một cách khai báo, vì vậy chúng không được gọi tường minh từ bất kỳ đâu. Trong DSLTrans, các quy tắc được gán một thứ tự tường minh, vì một quy tắc có thể khớp trên các phần tử đã được tạo ra trong các quy tắc trước đó. Trong trường hợp của chúng ta, các quy tắc DSLTrans tương ứng với các quy tắc khớp là độc lập với nhau. Do đó, thứ tự của chúng không quan trọng, và chúng tôi áp dụng cùng thứ tự như trong chuyển đổi ATL.

MatchModel của các quy tắc này chứa các phần tử xuất hiện trong phần from của các quy tắc ATL tương ứng. Có một phần tử cho mỗi phần tử mẫu đầu vào (IPE) xuất hiện trong quy tắc ATL. Ngoài ra, nếu quy tắc ATL có một bộ lọc, thì một số phần tử và quan hệ khác có thể xuất hiện trong MatchModel để thỏa mãn các điều kiện của bộ lọc. Các hộp đại diện cho thuộc tính cũng có thể xuất hiện bên trong các phần tử của MatchModel, điều này xảy ra khi các thuộc tính như vậy được sử dụng để khởi tạo các thuộc tính trong ApplyModel.

Trong ApplyModel của các quy tắc được tạo ra, có một phần tử cho mỗi phần tử mẫu đầu ra (OPE) được khai báo trong các quy tắc ATL. Thông thường, khi nhiều hơn một OPE được tạo ra trong một quy tắc ATL, thì một số OPE tham chiếu đến các OPE khác. Trong DSLTrans, điều này được chỉ định như một quan hệ giữa các phần tử được tạo ra trong ApplyModel.

Khi có các ràng buộc trong các OPE của các quy tắc ATL đang khởi tạo các thuộc tính (không phải tham chiếu), thì các thuộc tính này xuất hiện trong các phần tử được tạo ra trong ApplyModel trong DSLTrans. Hãy nhớ rằng các ràng buộc như vậy cũng có thể được định nghĩa bằng các helper. Bên cạnh đó, như đã đề cập trước đó, các thuộc tính cũng phải xuất hiện trong các phần tử trong MatchModel nếu giá trị của chúng được sử dụng để khởi tạo các giá trị của các thuộc tính trong phần apply, và các quan hệ được tạo ra giữa chúng.

Cuối cùng, một thuộc tính gọi là ApplyAttribute xuất hiện trong các phần tử được tạo ra trong ApplyModel trong hai trường hợp. Thứ nhất, bất cứ khi nào một giá trị được gán cho bất kỳ thuộc tính nào của phần tử trong ApplyModel. Thứ hai, nếu chuyển đổi DSLTrans sẽ được thực thi bởi engine chuyển đổi, vì chúng cần thiết cho mục đích tối ưu hóa.

ApplyAttribute này, trên thực tế, là cách DSLTrans mô phỏng cơ chế khả năng truy vết (traceability) nội bộ được ATL sử dụng như đã giải thích trong Mục 3.3. Do đó, bất cứ khi nào một ApplyAttribute xuất hiện trong một phần tử được tạo ra, quan hệ của phần tử đó với các phần tử xuất hiện trong MatchModel được lưu trữ trong các dấu vết. Vì việc duy trì các dấu vết này trong DSLTrans tốn kém, các dấu vết chỉ được tạo ra khi có sự hiện diện của một ApplyAttribute. Việc sử dụng các dấu vết này là cần thiết khi sử dụng các liên kết ngược, như được giải thích trong bước tiếp theo.

Xin lưu ý rằng sự hiện diện của các ApplyAttribute trong các quy tắc không được phản ánh trong các mô hình đầu ra được sinh ra. Trên thực tế, tên "ApplyAttribute" là một từ khóa dành riêng (reserved keyword).

**Cụ thể hóa ví dụ chạy xuyên suốt cho Bước 1** Bước đầu tiên này được minh họa trong Hình 4 trong chuỗi các quy tắc đi từ Country2Community đến Neighborhood2District. Có sáu quy tắc trong chuỗi như vậy, và hai quy tắc đã bị bỏ qua, tương ứng với Mother2Woman và Son2Man. Chúng rất giống với các quy tắc Father2Man và Daughter2Woman. Do đó, tám quy tắc này có một ánh xạ trực tiếp với các quy tắc R1 – R8 trong Đoạn mã 2.

Hãy xem xét quy tắc Father2Man. Quy tắc ATL chỉ có một phần tử mẫu đầu vào, IPE21 trong Đoạn mã 2, thuộc loại Parent, và nó cũng chứa một bộ lọc. Trong quy tắc DSLTrans tương ứng, chúng ta có thể thấy rằng phần tử Parent hiện diện, và cũng có một phần tử khác và một số quan hệ. Chúng tương ứng với bộ lọc, như được giải thích trong Mục 4.2.2.

Một số quy tắc như CityCompany2Association, Father2Man, và Daughter2Woman có các phần tử MatchModel chứa các hộp đại diện cho thuộc tính của phần tử. Các thuộc tính này được sử dụng để khởi tạo các thuộc tính mới trong ApplyModel, như được biểu diễn bằng các mũi tên đi vào.

Bây giờ hãy tập trung vào phần mẫu đầu ra. Quy tắc City2TownHall trong Đoạn mã 2 định nghĩa rằng TownHall được tạo ra (OPE61) có một tham chiếu đến Committee được tạo ra (OPE62) thông qua quan hệ committee, như được chỉ định trong B613. Trong quy tắc DSLTrans tương ứng của nó (City2TownHall trong Hình 4), quan hệ committee được tạo ra từ phần tử TownHall đến phần tử Committee.

Các ràng buộc khởi tạo thuộc tính hiện diện trong ví dụ của chúng ta như là B211, B311, B411, B511, B611, B621, B711, B811, B911 và B1011. Xin lưu ý rằng hai ràng buộc cuối cùng nằm trong các quy tắc lười, và sẽ được giải thích trong bước thứ hai của ánh xạ. Việc khởi tạo các ràng buộc như vậy có thể thấy trong các quy tắc Father2Man, Daughter2Woman, City2TownHall, CityCompany2Association và Neighborhood2District trong Hình 4. Xin lưu ý rằng, trong bước đầu tiên này, các ràng buộc khởi tạo tham chiếu bị bỏ qua. Đây sẽ là tất cả các ràng buộc còn lại.

Cuối cùng, thuộc tính ApplyAttribute hiện diện trong tất cả các quy tắc ngoại trừ Country2Community.

**Ngữ nghĩa tổng quát cho Bước 2** Một quy tắc trong DSLTrans được tạo ra cho mỗi ràng buộc khởi tạo giá trị của một tham chiếu trong chuyển đổi ATL. Các ràng buộc như vậy có thể bao gồm các helper, mà nội dung của chúng được xem xét trong việc dịch như thể chúng xuất hiện trực tiếp trong ràng buộc. Một lần nữa, các quy tắc này độc lập với nhau, vì vậy thứ tự không quan trọng. Tuy nhiên, chúng phải đứng sau các quy tắc được tạo ra trong bước đầu tiên để sử dụng đúng cách các liên kết ngược như các phụ thuộc quy tắc (rule dependencies). Chúng tôi gán cho chúng cùng thứ tự như thứ tự của các ràng buộc trong chuyển đổi ATL mà từ đó các quy tắc DSLTrans được tạo ra.

Trong các quy tắc DSLTrans được tạo ra ở bước này, phần bên trái của ràng buộc ATL, là tên của quan hệ đang được giải quyết trong ràng buộc, xuất hiện trong ApplyModel. Các lớp nguồn và đích của quan hệ cũng được đặt trong ApplyModel của các quy tắc. Nếu các lớp nguồn và/hoặc đích của quan hệ là các lớp trừu tượng, ánh xạ của chúng tôi xác định phần tử cụ thể phải được thêm vào, như chúng ta sẽ thấy sau trong ví dụ chạy xuyên suốt của chúng ta. Các phần tử và quan hệ được đặt trong MatchModel của quy tắc được tạo ra là những phần tử xuất hiện ở phần bên phải của ràng buộc. Phần bên phải của các ràng buộc được biểu thị theo các biểu thức OCL, và chúng tôi giải thích chúng trong Mục 4.2.2.

Tất cả các quy tắc được tạo ra trong bước này chứa các liên kết ngược. Như đã đề cập trước đó, chúng cho phép khớp trên các dấu vết giữa các phần tử trong mô hình đầu vào và đầu ra của chuyển đổi. Như đã giải thích trong Mục 2, khi một phần tử trong ApplyModel được liên kết bằng một liên kết ngược với một hoặc nhiều phần tử trong MatchModel, thì phần tử ApplyModel đó không được tạo ra trong mô hình đầu ra, mà thay vào đó tham chiếu đến các phần tử đã được tạo ra trong các quy tắc trước đó. Đây là cách cơ chế dấu vết nội bộ của ATL được mô hình hóa một cách tường minh trong DSLTrans. Tất nhiên, một phần tử trong ApplyModel có thể được liên kết với nhiều hơn một phần tử trong MatchModel bằng các liên kết ngược, và ngược lại (một số liên kết ngược có thể xuất phát từ cùng một phần tử trong MatchModel). Điều này tương đương với những dấu vết trong ATL có nhiều hơn một phần tử nguồn/đích.

Theo giải thích được đưa ra trong bước đầu tiên của ánh xạ, một thuộc tính ApplyAttribute cũng được tạo ra trong các phần tử trong ApplyModel ở bước này. Các quy tắc lười cũng có thể hiện diện trong các ràng buộc ATL đang khởi tạo các quan hệ, vì vậy chúng được xem xét trong bước này. Trong trường hợp này, các phần tử xuất hiện trong quy tắc lười được đưa vào quy tắc DSLTrans được tạo ra từ ràng buộc. Bây giờ, các phần tử được tạo ra trong MatchModel không chỉ là những phần tử xuất hiện ở phần bên phải của ràng buộc, mà còn là những phần tử đóng vai trò là phần tử khớp trong quy tắc lười. Tương tự, các phần tử được tạo ra trong ApplyModel cũng chứa các phần tử và quan hệ được tạo ra trong quy tắc lười.

**Cụ thể hóa ví dụ chạy xuyên suốt cho Bước 2** Các quy tắc được tạo ra ở bước này là tất cả những quy tắc theo sau quy tắc Neighborhood2District trong Hình 4. Xin lưu ý rằng chuyển đổi của chúng tôi gán cho các quy tắc này một tên duy nhất nhưng dài. Để đơn giản hóa, phần giải thích này sẽ chỉ sử dụng phần đầu tiên của tên, cho đến khi chữ cái viết hoa đầu tiên xuất hiện.

Hai quy tắc copersons[...] là các ánh xạ tới các ràng buộc B111 và B114, tương ứng. Hai quy tắc bị bỏ qua tương ứng với các ràng buộc B112 và B113, và chúng rất giống với hai quy tắc được hiển thị. Trong các quy tắc DSLTrans được tạo ra từ các ràng buộc này, phần bên trái của ràng buộc ATL, là tên của quan hệ đang được giải quyết trong ràng buộc, xuất hiện trong ApplyModel. Các lớp nguồn và đích của quan hệ đó cũng được đặt trong ApplyModel của các quy tắc.

Hãy tập trung vào quy tắc copersons[...] đầu tiên. Siêu mô hình trong Hình 2(b) chỉ ra rằng lớp nguồn của quan hệ persons là Community, trong khi lớp đích là Person. Về lớp nguồn, nó cũng là lớp được tạo ra trong chuyển đổi ATL (OPE11 trong ví dụ của chúng ta), vì vậy nó được đưa vào quy tắc DSLTrans một cách trực tiếp. Còn đối với lớp đích, lớp Person là trừu tượng. Tuy nhiên chúng ta có thể biết lớp cụ thể (không trừu tượng) nào kế thừa từ nó nên được chọn. Điều này được giải quyết bằng cách điều hướng biểu thức OCL xuất hiện ở phần bên phải của ràng buộc. B111 truy xuất các phần tử thuộc loại Parent có vai trò fathers. Do đó, theo quy tắc Father2Man, chúng ta biết rằng phần tử đích của quan hệ này phải thuộc loại Man.

Về các phần tử và quan hệ xuất hiện trong MatchModel của quy tắc được tạo ra, chúng là những phần tử xuất hiện ở phần bên phải của ràng buộc. Vì phần bên phải của các ràng buộc được biểu thị theo các biểu thức OCL, chúng tôi giải thích chúng trong Mục 4.2.2.

Ngược lại với hai quy tắc copersons[...], quy tắc tworkers[...] chứa một phần tử thuộc loại Person trong ApplyModel. Quy tắc này là ánh xạ của B612. Trong trường hợp này, phần tử đích của quan hệ workers có thể thuộc loại Man hoặc Woman, và không cần phân biệt. Ràng buộc duy nhất là Person đó phải được tạo ra từ một Parent, như được chỉ ra bởi liên kết ngược của nó.

Để đề cập một ví dụ khác về các liên kết ngược, hãy xem xét lại hai quy tắc copersons[...], trong đó phần tử Community tham chiếu đến Community được tạo ra trong quy tắc Country2Community, vì nó được liên kết với một liên kết ngược với phần tử Country. Tương tự, các phần tử Man và Woman được tạo ra trong các quy tắc Father2Man và Daughter2Woman, tương ứng. Điều này có nghĩa là điều duy nhất được thêm vào trong hai quy tắc này là quan hệ persons, bất cứ khi nào MatchModel được tìm thấy trong mô hình đầu vào.

Trong quy tắc acommittee[...] chúng ta thấy một ví dụ về một phần tử trong ApplyModel có nhiều hơn một liên kết ngược. Nó tương ứng với ràng buộc B712, khởi tạo quan hệ committee. Trong quy tắc DSLTrans, phần tử Association được liên kết ngược với các phần tử Company và City. Thật vậy, một Association được tạo ra từ một Company và một City bởi quy tắc CityCompany2Association. Phần tử Committee được liên kết ngược với City, vì một Committee được tạo ra từ một City trong quy tắc City2TownHall. Ràng buộc B712 thực sự đang giải quyết quan hệ committee bằng cách sử dụng thao tác resolveTemp của ATL đã giải thích trong Mục 3.2.

Cuối cùng, hãy xem một ví dụ về các quy tắc lười được gọi từ một ràng buộc. Trong ví dụ chạy xuyên suốt của chúng ta, có các lời gọi đến các quy tắc lười trong B811 và B812. Quy tắc DSLTrans dfacilities[...] tương ứng với B811, trong khi quy tắc DSLTrans được tạo ra từ B812 rất giống nhau và do đó được bỏ qua trong phần giải thích của chúng tôi.

Trong Đoạn mã 2 chúng ta có thể thấy rằng B811 đang gọi quy tắc lười CreateOrdinaryFacility (R9), tạo ra một phần tử thuộc loại OrdinaryFacility. Nó cũng khởi tạo thuộc tính name của phần tử được tạo ra và quan hệ members. Do đó, tất cả những điều này được đưa vào ApplyModel của quy tắc được tạo ra từ B811.

Về quan hệ members, hãy làm rõ rằng phần tử mới được tạo ra bởi quy tắc lười, OPE91, đóng vai trò là nguồn của nó. Đích được giải quyết bằng biểu thức OCL sch.students, trả về một phần tử thuộc loại Child (x. siêu mô hình trong Hình 2(a)).

#### 4.2.2 Các biểu thức OCL được xử lý (OCL Expressions Handled)

Một trong những thách thức chính khi phân tích một chuyển đổi ATL là xử lý các biểu thức OCL mà nó chứa, do số lượng lớn các khả năng điều hướng mà OCL cung cấp. Mặc dù có một số công trình xử lý việc dịch OCL sang các miền đồ thị [8, 11], DSLTrans có những đặc thù riêng của nó. Vì lý do này, trong mục này chúng tôi giải thích cách các biểu thức OCL được dịch sang DSLTrans bằng cách sử dụng ví dụ chạy xuyên suốt của chúng ta, vì một số toán tử OCL hiện diện. Những toán tử thú vị nhất là những toán tử xử lý các tập hợp (collections).

Trước hết, hãy nhắc lại rằng trong ATL, các biểu thức OCL có thể xuất hiện trong cả bộ lọc lẫn ràng buộc. Ngoài ra, chúng luôn điều hướng mô hình đầu vào, vì mô hình đầu ra chỉ có thể ghi (strictly writable) trong ATL. Trong hai bước của ánh xạ từ ATL sang DSLTrans được giải thích trong Mục 4.2.1, các bộ lọc được dịch trong bước đầu tiên, trong khi các ràng buộc được xem xét trong bước thứ hai. Tuy nhiên, trong cả hai trường hợp, các phần tử và quan hệ xuất hiện trong các biểu thức OCL được đưa vào MatchModel của các quy tắc DSLTrans được tạo ra.

Hãy bắt đầu bằng việc giải thích các phép điều hướng trong bộ lọc, và sau đó thảo luận về những phép điều hướng xuất hiện trong ràng buộc, có thể chứa các lời gọi đến quy tắc lười.

**Các biểu thức OCL trong bộ lọc** Xin nhắc lại rằng các phần tử xuất hiện trong ApplyModel của các quy tắc DSLTrans không có liên kết ngược được tạo ra từ những phần tử trong MatchModel cũng không được kết nối với các liên kết ngược.

Trong bước đầu tiên của ánh xạ (x. Mục 4.2.1), hãy nhớ rằng không có liên kết ngược nào trong các quy tắc được tạo ra. Do đó, các dấu vết được tạo ra giữa các phần tử của MatchModel và ApplyModel bất cứ khi nào ApplyAttribute hiện diện. Tuy nhiên, chúng tôi không muốn các phần tử trong MatchModel được đưa vào do điều kiện bộ lọc được đưa vào các dấu vết như vậy. Đây là lý do tại sao DSLTrans phân biệt trong MatchModel giữa AnyMatchElements và ExistsMatchElements.

AnyMatchElements tương ứng với các phần tử mẫu đầu vào xuất hiện trong các quy tắc ATL và phải được đưa vào các dấu vết được tạo ra. Chúng có ký hiệu ∀ trong biểu diễn đồ họa của chúng. Mặt khác, ExistsMatchElements được sử dụng để phát biểu các điều kiện trên AnyMatchElements, và chúng tôi sử dụng chúng trong việc dịch của mình để chèn các phần tử xuất hiện trong các biểu thức OCL của bộ lọc của chuyển đổi ATL. Chúng có ký hiệu ∃ trong biểu diễn đồ họa của chúng và không được xem xét trong các dấu vết.

Lý do để quyết định có nên đưa vào một ExistsMatchElement hay một AnyMatchElement trong MatchModel là đơn giản, và tùy thuộc vào nội dung của bộ lọc. Nếu chúng ta có một phép điều hướng trong bộ lọc đạt đến một phần tử nhất định, nhưng phần tử này không xuất hiện trong phần khớp của quy tắc ATL (phần from), thì nó được biểu diễn bằng một ExistsMatchElement.

Chúng ta có thể thấy hai ví dụ trong nghiên cứu tình huống chạy xuyên suốt của chúng ta trong Hình 5. Trong bộ lọc của Hình 5(a), chúng ta có thể thấy rằng Parent (biến p) là phần tử thực hiện khớp, và Family (đạt được thông qua tham chiếu family) được sử dụng làm một phần của điều kiện. Còn đối với bộ lọc của Hình 5(b), phần tử được sử dụng làm một phần của điều kiện lại là một Family, trong trường hợp này đạt được bằng cách sử dụng các thao tác allInstances và exists. Như chúng ta thấy trong cả hai trường hợp, tất cả các tham chiếu xuất hiện trong biểu thức OCL của bộ lọc đều được đưa vào.

*Hình 5(a). Quy tắc Father2Man. Hình 5(b). Quy tắc CityCompany2Association. Fig. 5 Các phần tử bộ lọc được dịch thành ExistsMatchElements*

Ngược lại, nếu các phần tử đạt được thông qua các phép điều hướng xuất hiện trong phần khớp của quy tắc ATL, thì AnyMatchElements được tạo ra trong quy tắc DSLTrans. Một ví dụ được thể hiện trong Hình 6.

*Fig. 6 Các phần tử bộ lọc được dịch thành AnyMatchElements: quy tắc CityCompany2Association*

**Các biểu thức OCL trong ràng buộc** Đối với các quy tắc được tạo ra trong bước thứ hai của ánh xạ, phần bên phải của các ràng buộc được đưa vào MatchModel của các quy tắc DSLTrans. Trong các quy tắc này, tất cả các phần tử ApplyModel được kết nối bằng các liên kết ngược với các phần tử trong MatchModel, vì vậy chúng ta không cần đưa vào ExistsMatchElements.

Một lần nữa, các phần tử đạt được thông qua các phép điều hướng (dù có sử dụng các thao tác tập hợp OCL hay không) phải được đưa vào MatchModel. Hình 7 cho thấy hai ví dụ trong đó các toán tử select và collect hiện diện trong hai ràng buộc. Tất cả các tham chiếu được đưa vào cả hai ràng buộc đều được phản ánh trong các MatchModel được tạo ra từ chúng, và tất cả các phần tử đạt được thông qua các tham chiếu đó được biểu diễn bằng AnyMatchElements.

*Hình 7(a). Quy tắc copersons[...]. Hình 7(b). Quy tắc tworkers[...]. Fig. 7 Nội dung ràng buộc được dịch trong MatchModel*

**Các biểu thức OCL trong ràng buộc gọi một quy tắc lười** Chúng tôi đã phát biểu rằng, vì các phần tử có liên kết ngược trong MatchModel của các quy tắc được tạo ra từ các ràng buộc, chúng sẽ được tạo ra dưới dạng AnyMatchElement. Tuy nhiên, có một trường hợp đặc biệt, đó là khi có một lời gọi đến một quy tắc lười trong ràng buộc, như chúng ta có thể thấy trong Hình 8.

Các quy tắc lười có một hoặc nhiều tham số đầu vào (một phần tử thuộc loại School trong trường hợp của chúng ta). Các quy tắc DSLTrans được tạo ra từ các ràng buộc chứa lời gọi đến quy tắc lười sinh ra các phần tử mới, chính là các phần tử được tạo ra từ quy tắc lười. Điều này là vì nội dung của quy tắc lười được xem xét khi tạo ra các quy tắc DSLTrans, như đã giải thích trong Mục 4.2.1. Vì lý do này, quy tắc DSLTrans có thể chứa các phần tử trong MatchModel của nó tham chiếu đến các thuộc tính của (các) phần tử được truyền làm tham số cho quy tắc lười.

Đây là trường hợp, trong ví dụ của chúng ta trong Hình 8, với phần tử Service được liên kết bằng tham chiếu ordinary với phần tử School. Vì không có liên kết ngược nào được kết nối với phần tử này, nó được đưa vào dưới dạng một ExistsMatchElement.

*Fig. 8 Một ràng buộc chứa một lời gọi đến quy tắc lười*

### 4.3 Triển khai (Implementation)

Ánh xạ giữa ATL và DSLTrans đã được triển khai bằng một chuyển đổi bậc cao (higher-order transformation — HOT) được phát triển trong ATL. Đó là HOT ATL2DSLTrans được thể hiện trong Hình 9, được giải thích dưới đây cùng với các đầu vào và đầu ra của nó.

HOT được cấu thành từ ba quy tắc khớp chính để hiện thực hóa ánh xạ hai bước được mô tả trong Mục 4.2.1. Quy tắc đầu tiên khớp một quy tắc khớp của Chuyển đổi ATL được lấy làm đầu vào và tạo ra một quy tắc trong Chuyển đổi DSLTrans được sinh ra làm đầu ra. Như chúng tôi đã đề cập trước đó, trong bước này chúng tôi cũng tạo ra các thuộc tính và điều kiện bộ lọc tương ứng. Để biết liệu một ràng buộc trong Chuyển đổi ATL đang khởi tạo một thuộc tính hay một tham chiếu, chúng ta cần thông tin của Siêu mô hình đầu ra tham gia vào Chuyển đổi ATL. Một số quy tắc lười và quy tắc lười duy nhất để tạo phần tử, quan hệ và thuộc tính được gọi từ quy tắc khớp này. Quy tắc này cũng lưu trữ trong một cấu trúc nội bộ các dấu vết lưu giữ quan hệ giữa các phần tử của MatchModel và ApplyModel của các quy tắc Chuyển đổi DSLTrans được tạo ra, điều này hữu ích để sinh ra các liên kết ngược trong bước thứ hai.

*Fig. 9 Triển khai ánh xạ (ATL2DSLTrans HOT — OCL Types Extracted — ATL Transformation — Input/Output Metamodels — DSLTrans Transformation — OCL Types Extraction HOT)*

Quy tắc khớp chính thứ hai xử lý việc tạo các quy tắc DSLTrans từ các ràng buộc ATL đang khởi tạo các tham chiếu không gọi bất kỳ quy tắc lười nào, và quy tắc thứ ba chuyển đổi những ràng buộc có gọi một quy tắc lười thành các quy tắc DSLTrans. Do đó, chúng nhận làm đầu vào một ràng buộc trong đó một phép điều hướng trên mô hình đầu vào được hiện thực hóa và tạo ra một quy tắc trong Chuyển đổi DSLTrans. Đây là lý do tại sao chúng ta cần Siêu mô hình đầu vào của chuyển đổi làm đầu vào cho HOT.

Hai quy tắc chính này hiện thực hóa bước thứ hai của ánh xạ được mô tả trong Mục 4.2.1. Một lần nữa, các quy tắc này gọi một số helper, quy tắc lười và quy tắc lười duy nhất có sẵn trong HOT ATL2DSLTrans để tạo ra các phần tử xuất hiện trong các quy tắc Chuyển đổi DSLTrans và các quan hệ giữa chúng. Bước cuối cùng trong hai quy tắc này là tạo ra các liên kết ngược giữa các phần tử trong MatchModel và ApplyModel, mà cấu trúc đã đề cập trước đó được sử dụng cho việc này.

Như một đầu vào khác cho HOT ATL2DSLTrans, chúng tôi sử dụng một mô hình trong đó các phép điều hướng OCL xuất hiện trong các bộ lọc và ràng buộc của Chuyển đổi ATL đầu vào được phân tích cú pháp (parsed) (mô hình OCL Types Extracted trong Hình 9). Trong việc phân tích cú pháp này, chúng tôi loại bỏ tất cả các toán tử tập hợp xuất hiện trong các phép điều hướng để thu được các kiểu xuất hiện trong các phép điều hướng đó. Vì ATL không cung cấp bất kỳ sự hỗ trợ hay API nào để thu được tĩnh (statically) các kiểu của một biểu thức OCL, chúng tôi sử dụng một HOT khác, đó là HOT OCL Types Extraction, trả về mô hình với các phép điều hướng OCL đã được phân tích cú pháp. Mô hình này được HOT ATL2DSLTrans sử dụng cho hai mục đích. Thứ nhất, khi tạo ra các phần tử và quan hệ trong MatchModel của một quy tắc DSLTrans tương ứng với bộ lọc của một quy tắc ATL, được hiện thực hóa trong bước đầu tiên của ánh xạ. Thứ hai, để tạo ra các phần tử và quan hệ trong MatchModel của một quy tắc DSLTrans tương ứng với phép điều hướng của một ràng buộc, được hiện thực hóa trong bước thứ hai của ánh xạ.

Lý do để có hai HOT tách biệt là kép. Thứ nhất, kết quả của HOT OCL Types Extraction có thể được sử dụng với một mục đích khác, và thứ hai, chúng tôi giảm độ phức tạp của HOT ATL2DSLTrans.

Tóm lại, mã giả được trình bày trong Hình 10 mô tả, ở mức cao, thuật toán hai bước ánh xạ các chuyển đổi ATL sang các chuyển đổi DSLTrans. Sử dụng cùng ký hiệu như trước trong bài báo (x. Mục 3.2), MR là viết tắt của quy tắc khớp (matched rule), LR cho quy tắc lười (lazy rule), IPE cho phần tử mẫu đầu vào và OPE cho phần tử mẫu đầu ra, và B cho ràng buộc.

**Fig. 10 Tóm tắt thuật toán HOT ATL to DSLTrans (mã giả)**

```
Input: Input MM, Output MM, ATL Trans, OCL Parsed
Output: DSLTrans Transformation
1: for all MR ∈ MatchedRule do  // Bắt đầu Bước 1
2:   Create DSLTrans rule
3:   for all IPE ∈ MR do
4:     Create AnyMatchElement
5:   end for
6:   if MR contains Filter then
7:     [Create ExistsMatchElements]  // Có thể xảy ra hoặc không
8:     Create MatchAssociations
9:   end if
10:  for all OPE ∈ MR do
11:    Create ApplyClass
12:    for all B ∈ OPE do
13:      if B initializes an attribute then
14:        Create ApplyAttribute in ApplyClass
15:        if Attributes from an IPE are used in B then
16:          Create MatchAttribute in MatchElement
17:        end if
18:      end if
19:    end for
20:  end for
21:  Create corresponding ApplyAssociations
22: end for
23: for all MR ∈ MatchedRule do  // Bắt đầu Bước 2
24:  for all OPE ∈ MR do
25:    for all B ∈ OPE do
26:      if B initializes a reference then
27:        Create DSLTrans rule
28:        Create AnyMatchElements with the OCL Exp of B
29:        Create MatchAssociations
30:        Create ApplyElements, for OPE and the type of B
31:        if B invokes a LazyRule (LR) then
32:          for all OPE in LR do
33:            Create ApplyElement
34:          end for
35:        end if
36:        Create corresponding ApplyAssociations
37:      end if
38:      Create corresponding BackwardLinks
39:    end for
40:  end for
41: end for
```

## 5 Công cụ chứng minh hợp đồng (Contract Prover)

Mục này sẽ mô tả hoạt động của công cụ chứng minh hợp đồng của chúng tôi, theo đó các hợp đồng được chứng minh trên tất cả các lần thực thi của một chuyển đổi DSLTrans.

Công cụ chứng minh hợp đồng mà chúng tôi mô tả ở đây là động cơ (engine) của công cụ SyVOLT, hiện có thể được sử dụng để phát triển và xác minh các chuyển đổi DSLTrans trong môi trường Eclipse [1,5,33]. Các ví dụ về hợp đồng mà chúng tôi chứng minh cũng được trình bày, cùng với một cuộc thảo luận ngắn gọn về tính biểu đạt của ngôn ngữ hợp đồng.

### 5.1 Tổng quan về chứng minh hợp đồng (Contract Proving Overview)

Cho một chuyển đổi được viết bằng ngôn ngữ chuyển đổi DSLTrans, kỹ thuật chứng minh hợp đồng của chúng tôi có thể chứng minh liệu các hợp đồng tiền điều kiện/hậu điều kiện sẽ được thỏa mãn hay không được thỏa mãn trên tất cả các lần thực thi của chuyển đổi. Nếu một hợp đồng được thỏa mãn, thì bất cứ khi nào tiền điều kiện của hợp đồng khớp trên một mô hình đầu vào, hậu điều kiện của hợp đồng sẽ khớp trên mô hình đầu ra tương ứng.

*Fig. 11 Một hợp đồng để xác minh rằng hai phần tử Woman và hai phần tử Man được sinh ra từ các Member tương ứng*

Ví dụ, Hình 11 mô tả một hợp đồng cần được chứng minh trên tất cả các lần thực thi chuyển đổi cho chuyển đổi Families-to-Persons mở rộng. Một phát biểu không hình thức cho hợp đồng này là: "một gia đình đầu vào có một người cha, một người mẹ, một người con trai và một người con gái phải luôn luôn sinh ra hai người đàn ông và hai người phụ nữ trong cộng đồng đầu ra". Xin lưu ý rằng chúng tôi sử dụng các liên kết ngược như một phần của ngôn ngữ hợp đồng, trong đó chúng được sử dụng để yêu cầu rằng các phần tử đầu ra phải được sinh ra từ các phần tử đầu vào được gắn kèm, tương tự như việc sử dụng chúng trong các quy tắc DSLTrans. Công cụ chứng minh hợp đồng của chúng tôi sau đó có thể chứng minh liệu hợp đồng này có được thỏa mãn hay không cho tất cả các lần thực thi chuyển đổi, và sinh ra bất kỳ phản ví dụ (counter-examples) nào nếu chúng xảy ra.

*Fig. 12 Một ví dụ về điều kiện đường đi (path condition) đại diện cho việc thực thi ba quy tắc*

Các ví dụ tiếp theo về hợp đồng được tìm thấy trong Mục 5.3.1. Các hợp đồng được chứng minh thông qua một quy trình trước tiên xây dựng một cách tượng trưng tất cả các lần thực thi khả dĩ của chuyển đổi, tạo ra một tập hợp các điều kiện đường đi (path conditions). Mỗi điều kiện đường đi đại diện cho việc thực thi một tập hợp các quy tắc chuyển đổi, bằng cách chứa các phần tử đầu vào và đầu ra được sinh ra bởi việc thực thi các quy tắc chuyển đổi đó.

> **Giải thích:** "Điều kiện đường đi" (path condition) là khái niệm trung tâm của kỹ thuật thực thi tượng trưng trong bài báo này. Thay vì chạy chuyển đổi trên một mô hình đầu vào cụ thể, công cụ sẽ liệt kê tất cả các *tổ hợp quy tắc* có thể thực thi cùng nhau (ví dụ: "chỉ quy tắc A chạy", "cả A và B đều chạy", "không quy tắc nào chạy"...). Mỗi tổ hợp như vậy — một "điều kiện đường đi" — mô tả một *lớp* các mô hình đầu vào/đầu ra có thể có (những phần tử nào chắc chắn xuất hiện trong đầu vào, và những phần tử tương ứng nào chắc chắn xuất hiện trong đầu ra). Vì số lượng tổ hợp quy tắc là hữu hạn (nhờ DSLTrans dừng và không có vòng lặp), tập hợp các điều kiện đường đi này phủ kín (partition — phân hoạch) toàn bộ không gian vô hạn các cặp mô hình đầu vào/đầu ra có thể có, giúp việc kiểm chứng "cho mọi mô hình đầu vào" trở thành việc kiểm tra một số hữu hạn các điều kiện đường đi.

Ví dụ, điều kiện đường đi trong Hình 12 đại diện cho việc thực thi ba quy tắc trong chuyển đổi. Biểu diễn này bao gồm các phần tử đầu vào và đầu ra sẽ hiện diện trong mô hình đầu vào và đầu ra nếu ba quy tắc này thực thi. Tập hợp các điều kiện đường đi được sinh ra bởi công cụ chứng minh do đó sẽ phân hoạch tập hợp các lần thực thi hợp lệ của chuyển đổi, trong đó mỗi lần thực thi là một cặp mô hình đầu vào/đầu ra. Kỹ thuật này lần đầu tiên được đề xuất trong [31] và được trình bày chi tiết hơn trong [32].

Các hợp đồng tiền điều kiện/hậu điều kiện tạo thành một phép kéo theo (implication), cần được kiểm tra cho mỗi điều kiện đường đi được sinh ra bởi thuật toán chứng minh. Nói một cách tổng quát, một hợp đồng được thỏa mãn trên một điều kiện đường đi nếu hoặc là các phần tử tiền điều kiện của hợp đồng không thể được tìm thấy trong điều kiện đường đi đó, hoặc là tiền điều kiện của hợp đồng cùng với hậu điều kiện của nó có thể được tìm thấy trong điều kiện đường đi đó. Hợp đồng không được thỏa mãn trên điều kiện đường đi nếu tiền điều kiện của nó có thể được tìm thấy trong điều kiện đường đi nhưng hậu điều kiện thì không. Cuối cùng, một hợp đồng được thỏa mãn cho một chuyển đổi nếu nó được thỏa mãn trên tất cả các điều kiện đường đi được sinh ra của chuyển đổi đó.

Các hợp đồng được mô tả một cách hình thức trong [32], trong khi cuộc thảo luận sâu rộng về ngôn ngữ hợp đồng được tìm thấy trong luận án tiến sĩ của Gehan Selim [42]. Mục 5.3.1 và Mục 5.4 trình bày thêm các ví dụ hợp đồng, trong khi Mục 5.5 thảo luận ngắn gọn về tính biểu đạt của ngôn ngữ hợp đồng.

### 5.2 Xây dựng điều kiện đường đi (Path Condition Creation)

Như được mô tả trong [33], công cụ chứng minh hợp đồng của chúng tôi xây dựng tất cả các hiện vật (artifacts) được sử dụng cho việc chứng minh hợp đồng thông qua việc khớp và viết lại các đồ thị có kiểu (typed graphs). Do đó, bước đầu tiên cho quy trình chứng minh hợp đồng là tạo ra các nguyên hàm (primitives) khớp và viết lại T-Core từ mỗi quy tắc trong chuyển đổi DSLTrans [45]. Các nguyên hàm chuyển đổi mô hình này là cốt lõi của công cụ chứng minh của chúng tôi, cho phép chúng tôi suy luận về cách các quy tắc có thể chồng chéo lên nhau trong quá trình thực thi chuyển đổi, và thực hiện việc viết lại đồ thị cần thiết cho kỹ thuật của chúng tôi.

Xin lưu ý rằng việc sử dụng cách suy luận về chuyển đổi đang được nghiên cứu dưới dạng đồ thị tường minh này trái ngược với các phương pháp khác trong tài liệu, trong đó các đặc tả chuyển đổi được dịch sang một bộ giải SAT hoặc công cụ chứng minh định lý, và sau đó các cơ chế chứng minh của các công cụ đó được sử dụng. Một cuộc thảo luận sâu hơn về phương pháp của chúng tôi so với các phương pháp trong tài liệu có thể được tìm thấy trong [42].

Để có thể suy luận đầy đủ về tất cả các mô hình đầu vào cho một chuyển đổi, công cụ chứng minh hợp đồng của chúng tôi tạo ra một tập hợp các hiện vật đại diện cho tất cả các lần thực thi khả dĩ của chuyển đổi. Các hiện vật này được tạo ra bằng cách thực thi tượng trưng tất cả các quy tắc trong chuyển đổi, có tính đến sự chồng chéo giữa các quy tắc và các phụ thuộc giữa các quy tắc. Các tổ hợp quy tắc được tạo ra được gọi là các điều kiện đường đi.

Ví dụ, điều kiện đường đi đầu tiên có thể đại diện cho trường hợp không có quy tắc nào trong chuyển đổi thực thi. Điều kiện đường đi tiếp theo là trường hợp chỉ có quy tắc đầu tiên thực thi, điều kiện tiếp theo là trường hợp chỉ có quy tắc thứ hai thực thi, và điều kiện đường đi thứ tư là trường hợp cả hai quy tắc đều thực thi.

Xin lưu ý rằng trong quy trình tạo điều kiện đường đi của chúng tôi, chúng tôi chỉ xem xét một lần thực thi của mỗi quy tắc. Nghĩa là, hoặc một quy tắc không thực thi (và không xuất hiện trong điều kiện đường đi), hoặc chúng tôi giả định rằng nó thực thi một số lần nào đó (và quy tắc đó xuất hiện một lần). Hạn chế này là do sự trừu tượng hóa của chúng tôi, trong đó chúng tôi biểu diễn một cách tượng trưng nhiều lần thực thi của cùng một quy tắc bằng cách quy tắc đó chỉ hiện diện một lần trong mỗi điều kiện đường đi. Sự trừu tượng hóa này là cần thiết cho mục đích phân tích, vì số lượng vô hạn các lần thực thi chuyển đổi phải được bao phủ bởi một số hữu hạn các điều kiện đường đi. Xin lưu ý rằng sự trừu tượng hóa này khả thi là nhờ tính đơn điệu (monotonicity) của một chuyển đổi DSLTrans: một quy tắc chỉ có thể thêm các phần tử vào mô hình đầu ra của một chuyển đổi DSLTrans, nhưng không bao giờ loại bỏ chúng.

> **Giải thích:** Đây là một trừu tượng hóa quan trọng để bài toán trở nên khả thi (tractable). Trên thực tế một quy tắc có thể khớp và chạy nhiều lần trên nhiều vị trí khác nhau trong một mô hình lớn (ví dụ quy tắc "Father2Man" có thể chạy cho hàng trăm ông bố khác nhau). Nhưng để suy luận, ta không cần quan tâm "chạy bao nhiêu lần" mà chỉ cần biết "có chạy hay không" — vì DSLTrans chỉ *thêm* phần tử chứ không bao giờ *xóa* (tính đơn điệu), nên việc một quy tắc chạy 1 lần hay 100 lần không làm thay đổi bản chất tập hợp phần tử nào tồn tại trong đầu ra để phục vụ việc kiểm tra hợp đồng cấu trúc.

Vì chuyển đổi được cấu thành từ các tầng, quy trình thực thi tượng trưng di chuyển qua từng tầng và xác định cách các quy tắc có thể tương tác với nhau. Không giống như việc sinh ra tập hợp lũy thừa (powerset) của tất cả các quy tắc, những tương tác quy tắc này trên thực tế có thể làm giảm số lượng điều kiện đường đi được sinh ra bởi công cụ chứng minh vì một số tổ hợp quy tắc bị chứng minh là không khả thi (infeasible).

Ví dụ, hãy xem xét một quy tắc R1 khớp trên một phần tử A, và một quy tắc R2 khớp trên một phần tử A được kết nối với một phần tử B. Trong quá trình thực thi chuyển đổi, sẽ không thể có việc R2 thực thi mà không có R1 cũng thực thi, vì đồ thị khớp của R1 là một tập con của đồ thị khớp của R2. Do đó, quy tắc R1 bị "bao hàm" (subsumed) bởi quy tắc R2. Công cụ chứng minh của chúng tôi có thể phát hiện các tương tác bao hàm này và giải quyết chúng trong một bước ngay trước khi sinh điều kiện đường đi. Điều này làm giảm số lượng điều kiện đường đi được tạo ra bằng cách không cho phép một số tổ hợp quy tắc nhất định, như được thảo luận thêm trong [44].

Ngoài ra, các quy tắc DSLTrans cũng có thể định nghĩa các liên kết ngược, như đã mô tả cho chuyển đổi Families-to-Persons Extended trong Mục 4.2.1. Hãy nhớ rằng các liên kết ngược này tạo ra các phụ thuộc vào các phần tử được tạo ra bởi các quy tắc trước đó. Cụ thể, các liên kết ngược này yêu cầu rằng phần tử được kết nối trong phần apply của quy tắc phải được tạo ra từ phần tử được kết nối trong phần match của quy tắc, bằng cách khớp trên các liên kết khả năng truy vết được tạo ra trong quá trình thực thi chuyển đổi. Do đó, chức năng này tương tự như bước ràng buộc ngầm định hiện diện trong ATL, như đã thảo luận trong Mục 4.2.1 dưới tiêu đề Ngữ nghĩa tổng quát cho Bước 2. Trong quá trình xây dựng điều kiện đường đi, những phụ thuộc liên kết ngược này ngăn một số quy tắc thực thi, làm giảm thêm số tổ hợp quy tắc khả dĩ.

#### 5.2.1 Các trường hợp tương tác quy tắc (Rule Interaction Cases)

Như đã đề cập, công cụ chứng minh hợp đồng của chúng tôi kết hợp các quy tắc từ các tầng khác nhau trong chuyển đổi để sinh ra các điều kiện đường đi. Mục này giờ đây sẽ tóm tắt ba trường hợp mà trong đó một quy tắc trong một tầng có thể kết hợp với một điều kiện đường đi từ một tầng trước đó. Thông tin này được trình bày để cho người đọc cảm nhận được sự phức tạp đằng sau việc thực thi tượng trưng của các quy tắc này, và hiểu rõ hơn về cách các điều kiện đường đi đại diện cho các lần thực thi của chuyển đổi. Đối với những độc giả quan tâm, một cách xử lý hình thức của các trường hợp này được tìm thấy trong [32].

Xin lưu ý rằng các liên kết ngược được biểu diễn bằng các đường nét đứt dày giữa các phần tử match và apply trong các hình bên dưới. Các liên kết khả năng truy vết cũng đã được thêm vào giữa các phần tử trong các quy tắc, và được biểu diễn bằng các đường liền nét mỏng. Để rõ ràng, chúng tôi bỏ qua các nhãn quan hệ trong các hình.

**Điều kiện đường đi rỗng (Empty Path Condition)** Quy trình sinh điều kiện đường đi bắt đầu với điều kiện đường đi rỗng. Như đã đề cập, điều này đại diện cho tập hợp tất cả các lần thực thi chuyển đổi mà không có quy tắc nào thực thi. Khi các quy tắc được kết hợp với điều kiện đường đi rỗng này, các phần tử match và apply sẽ được đặt vào điều kiện đường đi. Các phần tử này sẽ biểu diễn một cách tượng trưng các phần tử hiện diện trong mô hình đầu vào và đầu ra của các chuyển đổi được đại diện bởi điều kiện đường đi đó.

**Không có phụ thuộc (No Dependencies)** Trong trường hợp đầu tiên cho tương tác quy tắc, quy tắc không chứa liên kết ngược nào. Trong thuật toán sinh điều kiện đường đi, hai điều kiện đường đi khác nhau sẽ được tạo ra. Điều kiện đường đi đầu tiên được tạo ra đại diện cho khả năng quy tắc không thực thi, trong khi điều kiện đường đi kia đại diện cho khả năng quy tắc thực thi.

Một ví dụ về trường hợp này được thể hiện trong Hình 13, trong đó điều kiện đường đi PC được kết hợp với quy tắc Father2Man. Xin lưu ý rằng điều kiện đường đi ví dụ PC đã chứa các phần tử Country và Community, để đại diện cho việc thực thi tượng trưng của quy tắc Country2Community. Hai điều kiện đường đi ở phía bên phải của Hình 13 cho thấy một điều kiện đường đi giống hệt PC, và một điều kiện đường đi cũng chứa các phần tử từ quy tắc Father2Man.

*Hình 13(a). Điều kiện đường đi và quy tắc để kết hợp. Hình 13(b). Hai điều kiện đường đi được tạo ra bởi sự kết hợp. Fig. 13 Ví dụ kết hợp trong đó quy tắc không có phụ thuộc*

**Phụ thuộc không được thỏa mãn (Unsatisfied Dependencies)** Đối với trường hợp thứ hai trong tương tác quy tắc, quy tắc sau chứa các liên kết ngược không thể được tìm thấy trong điều kiện đường đi. Điều này ngụ ý rằng quy tắc không thể thực thi. Điều kiện đường đi cũ được giữ nguyên, và không có điều kiện đường đi mới nào được tạo ra.

Trường hợp này được biểu diễn bởi Hình 14. Xin lưu ý rằng quy tắc cotownHalls[...] chứa các liên kết ngược, yêu cầu một phần tử Community phải được tạo ra bởi một phần tử Country, cũng như một phần tử Townhall phải được tạo ra bởi một phần tử City. Vì liên kết ngược thứ hai này không thể được thỏa mãn bởi các phần tử trong PC, quy tắc cotownHalls[...] không thể thực thi. Do đó, chỉ có điều kiện đường đi PC được giữ lại và không có điều kiện đường đi mới nào được tạo ra.

*Hình 14(a). Điều kiện đường đi và quy tắc để kết hợp. Hình 14(b). Một điều kiện đường đi được tạo ra bởi sự kết hợp. Fig. 14 Ví dụ kết hợp trong đó các phụ thuộc của quy tắc không được thỏa mãn*

**Các phụ thuộc được thỏa mãn (Satisfied dependencies)** Cuối cùng, trường hợp khó nhất là khi các liên kết ngược khớp lên điều kiện đường đi, thông qua các liên kết khả năng truy vết hiện diện. Do đó, quy tắc có thể thực thi hoặc phải thực thi, tùy thuộc vào việc các phần tử trong phần khớp của quy tắc đã tồn tại trong điều kiện đường đi hay chưa. Trong trường hợp này, một điều kiện đường đi mới được tạo ra cho mỗi khả năng về cách quy tắc có thể được khớp lên điều kiện đường đi.

Trong trường hợp thỏa mãn một phần (partial satisfiability), không phải tất cả các phần tử của quy tắc đều có thể được tìm thấy trong PC. Hình 15 cho thấy sự kết hợp của điều kiện đường đi PC với quy tắc coassociations[...]. Xin lưu ý rằng quy tắc này chứa các quan hệ giữa các phần tử Country và City, cũng như giữa các phần tử Country và Company. Tuy nhiên, các quan hệ này không hiện diện trong điều kiện đường đi PC.

Vì các quan hệ này không hiện diện trong PC, điều này chỉ ra rằng có khả năng mô hình đầu vào có thể không chứa các quan hệ này giữa các phần tử này. Do đó, hai điều kiện đường đi được tạo ra. Một điều kiện đường đi đại diện cho trường hợp mô hình đầu vào không cho phép quy tắc coassociations[...] thực thi. Điều kiện đường đi kia được tạo ra sẽ bao gồm các quan hệ này, vì nó đại diện cho trường hợp quy tắc sẽ thực thi trên mô hình đầu vào. Xin lưu ý rằng nếu quy tắc có thể khớp tại nhiều vị trí trên PC, một điều kiện đường đi mới sẽ được tạo ra cho mỗi vị trí.

*Hình 15(a). Điều kiện đường đi và quy tắc để kết hợp. Hình 15(b). Hai điều kiện đường đi được tạo ra bởi sự kết hợp. Fig. 15 Ví dụ kết hợp trong đó các phụ thuộc của quy tắc được thỏa mãn một phần*

Phần bù của trường hợp thỏa mãn một phần là trường hợp thỏa mãn hoàn toàn (total satisfaction). Trong trường hợp này, tất cả các phần tử cần thiết của quy tắc đều hiện diện trong điều kiện đường đi. Do đó, quy tắc phải thực thi cho các lần thực thi chuyển đổi được đại diện bởi điều kiện đường đi đó.

Hình 16 minh họa trường hợp trong đó các phụ thuộc của quy tắc acommittee[...] được thỏa mãn hoàn toàn bởi điều kiện đường đi PC. Xin lưu ý rằng tất cả các liên kết ngược trong quy tắc đều có thể được tìm thấy trong PC, cũng như các quan hệ cần thiết.

Điều kiện đường đi được tạo ra được xây dựng bằng cách kết hợp quy tắc vào (các) vị trí của điều kiện đường đi tại (các) vị trí mà quy tắc khớp. Xin lưu ý rằng trong Hình 16, một quan hệ đã được xây dựng giữa các phần tử Association và Committee. Như với trường hợp thỏa mãn một phần, quy tắc có thể khớp tại nhiều vị trí.

*Hình 16(a). Điều kiện đường đi và quy tắc để kết hợp. Hình 16(b). Một điều kiện đường đi được tạo ra bởi sự kết hợp. Fig. 16 Ví dụ kết hợp trong đó các phụ thuộc của quy tắc được thỏa mãn hoàn toàn*

**Thiết lập thuộc tính (Attribute Setting)** Việc thiết lập các thuộc tính cho các phần tử của quy tắc cũng được thực thi tượng trưng trong việc xây dựng điều kiện đường đi. Về cơ bản, chúng tôi lưu trữ trong điều kiện đường đi các phương trình phát biểu các giá trị cho các thuộc tính như được giả định bởi các quy tắc, và trong các quy tắc tiếp theo chúng tôi kiểm tra tính tương thích giá trị của các phần tử match đang được khớp. Nếu các điều kiện trên các thuộc tính trên phần tử điều kiện đường đi và phần tử quy tắc mâu thuẫn với nhau, không có điều kiện đường đi nào được sinh ra.

Xin lưu ý rằng một bộ giải (solver) khá đơn giản hiện đang được sử dụng, vì kiểu dữ liệu thuộc tính duy nhất có sẵn trong DSLTrans là String. Tuy nhiên, phương pháp của chúng tôi không bị hạn chế quá mức bởi cách tiếp cận này. Từ góc độ thực dụng, chúng tôi lưu ý rằng nghiên cứu tình huống công nghiệp của chúng tôi chỉ thao tác trên các String.

Tổng quát hơn, DSLTrans đã được sử dụng để viết nhiều chuyển đổi hữu ích với các mô hình chỉ có String làm thuộc tính. Điều này là vì DSLTrans chuyên về các bản dịch ngôn ngữ (language translations), như được mô tả trong [34]. Các chuyển đổi mô hình thuộc loại này thường không yêu cầu các phép tính phức tạp trên các thuộc tính và phần lớn công việc được thực hiện bằng việc khớp và viết lại nút (node matching and rewriting). Dữ liệu thuộc tính String phần lớn được sao chép sang mô hình được sinh ra hoặc được nối với dữ liệu String khác.

Một cách giải quyết khả dĩ cho hạn chế chỉ có kiểu String là chuyển đổi các thuộc tính và thao tác không phải String thành String, sao cho chúng có thể được thao tác bởi chuyển đổi. Sau đó, mỗi String đầu ra có thể được đánh giá để sinh ra giá trị theo kiểu ban đầu. Xin lưu ý rằng, sử dụng phương pháp này, không có thao tác nào của các đại số (algebras) khác ngoài đại số String có thể được thực thi bởi engine chuyển đổi.

Một phương pháp toàn diện hơn sẽ là đưa vào các kiểu dữ liệu bổ sung trong chính ngôn ngữ DSLTrans, do đó cho phép thực thi các thao tác của các đại số khác. Tuy nhiên, cần phải rất cẩn thận khi đưa các kiểu dữ liệu mới vào DSLTrans, sao cho các kiểu đó không đưa vào các phép tính không dừng (non-terminating) tiềm ẩn. Điều đó sẽ vô hiệu hóa sự thật rằng tất cả các chuyển đổi DSLTrans đều dừng. Ngoài ra, một bộ giải mạnh mẽ hơn cũng sẽ cần thiết để cho phép xây dựng điều kiện đường đi cho một DSLTrans được mở rộng với các kiểu dữ liệu bổ sung.

*Fig. 17 Một ví dụ về điều kiện đường đi đại diện cho việc thực thi ba quy tắc*

**Phân hoạch các lần thực thi chuyển đổi (Partitioning Transformation Executions)** Tiếp theo cách suy luận này về ba trường hợp tương tác của các quy tắc, tất cả các quy tắc trong chuyển đổi được xem xét và kết hợp thành các điều kiện đường đi. Điều này được thực hiện bằng cách xem xét từng tầng trong chuyển đổi DSLTrans lần lượt.

Đối với tầng đầu tiên, điều kiện đường đi rỗng được kết hợp với mỗi quy tắc. Sau đó, với mỗi tầng tiếp theo n, tập hợp các điều kiện đường đi được sinh ra bởi tầng n-1 được kết hợp với các quy tắc từ tầng n. Ví dụ, điều kiện đường đi được xem xét trong trường hợp thỏa mãn hoàn toàn ở trên sẽ được sinh ra bởi tầng chứa coassociations[...], như trong trường hợp thỏa mãn một phần.

Các điều kiện đường đi kết quả ở cuối quy trình này sẽ đại diện cho tất cả các tập hợp khả thi của các quy tắc có thể thực thi trong chuyển đổi. Do đó, tập hợp vô hạn các lần thực thi chuyển đổi sẽ được phân hoạch bởi tập hợp hữu hạn các điều kiện đường đi [32]. Vì mỗi quy tắc chứa các phần tử match và apply, điều kiện đường đi do đó định nghĩa những phần tử nào hiện diện trong mô hình đầu vào và đầu ra cho phân hoạch đó của các lần thực thi chuyển đổi. Xin lưu ý rằng điều kiện đường đi rỗng, không chứa phần tử nào, khớp với tất cả các lần thực thi chuyển đổi khác không được đại diện bởi một điều kiện đường đi khác.

Ví dụ, Hình 17 biểu diễn một cách tượng trưng việc thực thi ba quy tắc từ chuyển đổi Families-to-Persons mở rộng: Country2Community, Mother2Woman, và copersonsSolveRef[...]Woman. Xin lưu ý rằng phần tử Community được tạo ra từ phần tử Country trong quy tắc Country2Community, và được khớp bởi phụ thuộc liên kết ngược trong quy tắc copersonsSolveRef[...]Woman. Điều kiện đường đi này đại diện cho tất cả các lần thực thi chuyển đổi trong đó ba quy tắc này thực thi, và do đó trình bày các phần tử và quan hệ đầu vào và đầu ra được biết là tồn tại nếu tập hợp các quy tắc này thực thi.

Sự trừu tượng hóa các lần thực thi chuyển đổi bằng các điều kiện đường đi này tạo thành nền tảng cho kỹ thuật chứng minh hợp đồng của chúng tôi, trong đó việc chứng minh các hợp đồng trên tập hợp các điều kiện đường đi được sinh ra cho phép chúng tôi suy luận về cách hợp đồng được thỏa mãn trên các cặp mô hình đầu vào-đầu ra của chuyển đổi.

### 5.3 Quy trình chứng minh hợp đồng (Contract Proving Process)

Vì các điều kiện đường đi được xây dựng thông qua việc suy luận về tương tác của các quy tắc chuyển đổi, cấu trúc của một điều kiện đường đi rất giống với cấu trúc của một quy tắc DSLTrans có một đồ thị match và một đồ thị apply, như thấy trong Hình 17.

Ý nghĩa của một điều kiện đường đi cụ thể là, "nếu các phần tử trong thành phần trên của điều kiện đường đi có trong mô hình đầu vào, thì các phần tử trong thành phần dưới sẽ có trong mô hình đầu ra." Hãy nhớ rằng điều này khớp với ý nghĩa dự định của một hợp đồng: "nếu các phần tử trong tiền điều kiện được tìm thấy trong mô hình đầu vào của chuyển đổi, thì các phần tử hậu điều kiện phải được tìm thấy trong mô hình đầu ra". Do đó, để chứng minh rằng một hợp đồng được thỏa mãn hay không trên một điều kiện đường đi, chỉ cần xem liệu các phần tử trong hợp đồng có thể được khớp lên điều kiện đường đi hay không, như được mô tả trong [32].

Có ba trường hợp để xác định trạng thái của một hợp đồng:

- Nếu tiền điều kiện của hợp đồng, bao gồm cả các liên kết ngược, không khớp với điều kiện đường đi, thì hợp đồng không áp dụng được cho điều kiện đường đi đó.
- Nếu cả tiền điều kiện và hậu điều kiện đều khớp, thì hợp đồng được thỏa mãn trên điều kiện đường đi đó.
- Nếu tiền điều kiện khớp, nhưng hậu điều kiện không khớp, thì hợp đồng không được thỏa mãn trên điều kiện đường đi đó.

Xin lưu ý rằng một hợp đồng có thể được kỳ vọng là không được thỏa mãn trong mọi trường hợp đối với một chuyển đổi. Ví dụ, hãy xem xét hợp đồng DaughterMother, được tái hiện trong Hình 18. Phát biểu không hình thức cho hợp đồng này là "một gia đình có một người mẹ và một người con gái sẽ luôn luôn sinh ra một cộng đồng có một người đàn ông". Dễ dàng thấy rằng một mô hình đầu vào chỉ chứa các phần tử mẹ và con gái không nên sinh ra một người đàn ông trong cộng đồng đích.

Công cụ chứng minh hợp đồng của chúng tôi sau đó sẽ tìm thấy nhiều điều kiện đường đi phản ví dụ khiến hợp đồng không được thỏa mãn, chẳng hạn như điều kiện đường đi trong Hình 17. Xin lưu ý rằng tiền điều kiện của hợp đồng khớp lên thành phần trên của điều kiện đường đi, trong khi phần tử Man trong hậu điều kiện của hợp đồng không thể được tìm thấy trong thành phần dưới của điều kiện đường đi. Do đó, việc hợp đồng này không được thỏa mãn càng đảm bảo rằng chuyển đổi đang hoạt động đúng, vì các con gái và các bà mẹ không bị vô tình chuyển đổi thành đàn ông. Vì kết quả này là kết quả được mong đợi, điều này cho phép người xây dựng chuyển đổi có sự tin tưởng cao hơn vào tính hợp lệ của chuyển đổi.

*Fig. 18 Một hợp đồng để xác minh liệu một phần tử Man có được sinh ra từ một Family chứa một phần tử con gái và một phần tử mẹ hay không - hợp đồng này sẽ không được thỏa mãn*

Nếu một hợp đồng không được thỏa mãn trên chuyển đổi và điều đó không được kỳ vọng trước, thì điều này chỉ ra một lỗi ở hoặc là hợp đồng hoặc là chuyển đổi. Công cụ chứng minh sẽ báo cáo (và tùy chọn vẽ) các điều kiện đường đi mà hợp đồng không được thỏa mãn trên đó. Ngoài ra, một điều kiện đường đi tối thiểu được báo cáo, đại diện cho tổ hợp nhỏ nhất các quy tắc gây ra thất bại. Điều này cho phép người phát triển chuyển đổi xác định những tổ hợp quy tắc mà một lỗi có thể xảy ra, và thay đổi chuyển đổi hoặc hợp đồng cho phù hợp. Xin lưu ý rằng kỹ thuật của chúng tôi chỉ xác định các điều kiện đường đi nơi phát sinh vấn đề. Việc xác định các phần tử gây lỗi và đề xuất sửa chữa hiện chưa được xử lý.

Xin lưu ý rằng, mặc dù tiền điều kiện của hợp đồng DaughterMother không thể được khớp (một cách đẳng cấu — isomorphically) trong điều kiện đường đi trong Hình 17, tiền điều kiện của hợp đồng vẫn được tìm thấy trong điều kiện đường đi đó. Điều này là vì có những mô hình đầu vào được khớp bởi hai quy tắc này, nơi hai phần tử Family riêng biệt thuộc về hai quy tắc tách biệt sẽ khớp trên cùng một thực thể gia đình — hãy nhớ rằng trong DSLTrans các quy tắc có thể khớp trên cùng các phần tử trong mô hình đầu vào. Do đó, quan hệ giữa tiền điều kiện của các hợp đồng và điều kiện đường đi là như vậy: bất kỳ khả năng chồng chéo nào (hoặc sự vắng mặt của nó) giữa các phần tử cùng loại thuộc về hai hoặc nhiều quy tắc khác nhau trong điều kiện đường đi, đều được coi là một khả năng khớp cho tiền điều kiện của hợp đồng.

Quan hệ giữa hợp đồng và điều kiện đường đi do đó mang nhiều thông tin hơn một phép đẳng cấu đồ thị (graph isomorphism) đơn giản. Nó là một phép đồng cấu (homomorphism) hỗn hợp phần toàn ánh/đơn ánh (mixed partial surjective/injective) giữa điều kiện đường đi và các đồ thị có kiểu của hợp đồng: trong khi phép toàn ánh cho phép "quên" rằng hai hoặc nhiều phần tử trong một điều kiện đường đi thuộc về các quy tắc khác nhau, phép đơn ánh đảm bảo rằng các phần tử thuộc cùng một quy tắc trong điều kiện đường đi có một đối tác đẳng cấu trong thuộc tính (property). Các ví dụ thêm, cũng như một sự hình thức hóa của quan hệ này có thể được tìm thấy trong [32].

> **Giải thích:** Đây là một điểm kỹ thuật tinh tế: khi khớp hợp đồng lên một điều kiện đường đi, công cụ không đòi hỏi một phép khớp "1-1 hoàn hảo" (đẳng cấu đồ thị chuẩn) — vì điều kiện đường đi có thể chứa nhiều bản sao của cùng loại phần tử đến từ các quy tắc khác nhau (ví dụ hai phần tử "Family" riêng biệt từ hai quy tắc khác nhau), và trên thực tế có khả năng cả hai phần tử "Family" đó chỉ là MỘT gia đình duy nhất trong mô hình đầu vào thực tế. Do đó phép khớp phải cho phép "gộp" (toàn ánh — surjective, tức nhiều phần tử trong điều kiện đường đi có thể ánh xạ về cùng một phần tử của hợp đồng) trong khi vẫn đảm bảo tính nhất quán nội tại của mỗi quy tắc (đơn ánh — injective).

Trong trường hợp hợp đồng phải suy luận tường minh về số lượng (multiplicity) của các phần tử Family, ngôn ngữ hợp đồng bao gồm logic mệnh đề, như trong Mục 5.3.1.

#### 5.3.1 Các ví dụ hợp đồng khác (Further Contract Examples)

*Fig. 19 Một hợp đồng để xác minh việc xây dựng đúng đắn thuộc tính name trong mô hình đầu ra*

Ngôn ngữ hợp đồng của chúng tôi cũng cho phép suy luận về các thuộc tính của các phần tử trong mô hình. Hình 19 mô tả một hợp đồng xác định liệu họ tên đầy đủ của Person được sinh ra đã được tạo ra đúng đắn từ họ của Family và tên của Member hay chưa.

Các hợp đồng cũng có thể được kết hợp bằng logic mệnh đề và các điểm xoay (pivots) để tăng cường tính biểu đạt của ngôn ngữ hợp đồng [42, 44]. Ví dụ, chúng tôi trình bày một hợp đồng cho chuyển đổi Families-to-Persons gốc trong Hình 20. Hợp đồng này minh họa việc sử dụng logic mệnh đề trong công cụ chứng minh hợp đồng của chúng tôi để tạo thành một phép kéo theo "nếu, thì KHÔNG" giữa hai hợp đồng[^2]. Để phép kết hợp hợp đồng này là đúng, với mỗi điều kiện đường đi mà hợp đồng thứ nhất được thỏa mãn, hợp đồng thứ hai phải KHÔNG được thỏa mãn và các phần tử được đánh dấu bởi các thuộc tính điểm xoay (pivot attributes) phải giống nhau. Phát biểu không hình thức của hợp đồng này là "Nếu một cộng đồng chứa bất kỳ người nào, thì cộng đồng đó không chứa hai (hoặc nhiều hơn) người". Do đó, hợp đồng này biểu đạt các ràng buộc về số lượng của các phần tử, như sẽ được thảo luận thêm trong Mục 5.5.

[^2]: Các liên kết logic giữa các hợp đồng không được biểu diễn bằng đồ họa.

*Hình 20(a). Phần "Nếu". Hình 20(b). Phần "Thì KHÔNG". Fig. 20 Sử dụng logic mệnh đề để biểu đạt các hợp đồng "nếu, thì KHÔNG"*

Xin lưu ý rằng ngôn ngữ hợp đồng mà chúng tôi trình bày trong bài báo này chỉ dựa trên các cấu trúc được tìm thấy trong các siêu mô hình đầu vào và đầu ra, cộng với các liên kết khả năng truy vết. Vì cả ATL và DSLTrans đều thao tác trên các siêu mô hình EMF, ngôn ngữ hợp đồng do đó có thể được sử dụng một cách liền mạch để mô tả các tiền điều kiện/hậu điều kiện mà chúng ta muốn kiểm tra trên cả chuyển đổi ATL lẫn DSLTrans. Sự thật này là một lợi thế lớn cho công trình của chúng tôi: các hợp đồng có thể được biểu đạt chính xác bằng cùng một ngôn ngữ và có cùng ngữ nghĩa cho cả một chuyển đổi ATL và biểu diễn DSLTrans tương đương về mặt ngữ nghĩa của nó.

### 5.4 Kết quả hợp đồng (Contract Results)

Mục này sẽ trình bày chín hợp đồng mà chúng tôi đã tạo ra cho chuyển đổi Families-to-Persons mở rộng, để minh họa tính hữu ích của các hợp đồng cho việc xác minh.

366 điều kiện đường đi đã được tạo ra cho chuyển đổi này, đại diện cho một phân hoạch hữu hạn của tập hợp vô hạn các lần thực thi khả dĩ của chuyển đổi. Sau đó, mỗi trong chín hợp đồng được kiểm tra đối với mỗi điều kiện đường đi. Mỗi hợp đồng được trình bày chi tiết ở đây dưới dạng một bộ ba gồm một phát biểu không hình thức, biểu diễn đồ họa, và số lượng điều kiện đường đi mà hợp đồng thành công hoặc thất bại.

Xin lưu ý rằng ở đây, sự thành công của một hợp đồng có nghĩa là cả tiền điều kiện lẫn hậu điều kiện của hợp đồng (bao gồm cả các liên kết ngược) đều khớp lên điều kiện đường đi, trong khi thất bại có nghĩa là tiền điều kiện khớp, nhưng hậu điều kiện thì không. Ngoài ra, hợp đồng vẫn được thỏa mãn trên các điều kiện đường đi mà tiền điều kiện không khớp, đó là phần còn lại của các điều kiện đường đi.

Nếu hợp đồng không được thỏa mãn trên một số điều kiện đường đi, và do đó không được thỏa mãn trên tất cả các lần thực thi chuyển đổi, một giải thích ngắn gọn sẽ mô tả các tương tác quy tắc ngăn hợp đồng không được thỏa mãn.

Xin lưu ý rằng mục này bao gồm các hợp đồng mà chúng tôi kỳ vọng sẽ thất bại đối với chuyển đổi. Như đã đề cập, các hợp đồng này làm tăng độ tin cậy của chúng tôi vào tính đúng đắn của chuyển đổi, vì công cụ chứng minh sẽ sinh ra các điều kiện đường đi phản ví dụ nơi hợp đồng không được thỏa mãn. Vì điều kiện đường đi đại diện cho việc thực thi một tập hợp cụ thể các quy tắc chuyển đổi, điều này cho phép người dùng suy luận về sự tương tác giữa các quy tắc, và xác định liệu chuyển đổi có bị lỗi hay không.

Xin lưu ý rằng việc phân chia các hợp đồng thành các mục sau đây chủ yếu là để dễ đọc, vì chúng đề cập đến các khu vực khác nhau của siêu mô hình nguồn và đích.

#### 5.4.1 Các hợp đồng Families-to-Persons

**Pos-FourMembers**
Phát biểu: Một Family có một cha, một mẹ, một con trai và một con gái phải luôn luôn sinh ra hai phần tử Man và hai phần tử Woman trong Community đích.
Kết quả kỳ vọng: Được thỏa mãn trên tất cả các điều kiện đường đi
Số điều kiện đường đi thành công: 137
Số điều kiện đường đi thất bại: 0

**Pos-MotherFather**
Phát biểu: Họ tên đầy đủ của một Person được sinh ra được tạo ra đúng đắn từ phép nối tên của Member và họ của Family của người đó
Kết quả kỳ vọng: Được thỏa mãn trên tất cả các điều kiện đường đi
Số điều kiện đường đi thành công: 236
Số điều kiện đường đi thất bại: 0

**Neg-DaughterMother**
Phát biểu: Một Family có một mẹ và một con gái sẽ luôn luôn sinh ra một Community có một người đàn ông
Kết quả kỳ vọng: Không được thỏa mãn trên tất cả các điều kiện đường đi
Số điều kiện đường đi thành công: 178
Số điều kiện đường đi thất bại: 42
Giải thích: Một phần tử Man sẽ không được sinh ra từ một Family toàn là nữ

#### 5.4.2 Các hợp đồng về địa điểm (Location Contracts)

**Pos-TownHallComm**
Phát biểu: Một TownHall và một Committee được tạo ra cho mỗi City, và TownHall được tạo ra phải có Committee được tạo ra làm committee của nó
Kết quả kỳ vọng: Được thỏa mãn trên tất cả các điều kiện đường đi
Số điều kiện đường đi thành công: 352
Số điều kiện đường đi thất bại: 0

**Pos-AssocCity**
Phát biểu: Một Community chứa một City có một Company phải sinh ra một Community có một TownHall và một Committee
Kết quả kỳ vọng: Được thỏa mãn trên tất cả các điều kiện đường đi
Số điều kiện đường đi thành công: 287
Số điều kiện đường đi thất bại: 0

**Pos-ParentCompany**
Phát biểu: Nếu một Parent worksIn một Company, Person được tạo ra từ người đó phải nằm trong workers của TownHall được tạo ra từ City nơi Person đó sống
Kết quả kỳ vọng: Được thỏa mãn trên tất cả các điều kiện đường đi
Số điều kiện đường đi thành công: 222
Số điều kiện đường đi thất bại: 0

**Neg-CountryCity**
Phát biểu: Nếu Country có ít nhất một City, thì ít nhất một Association phải được tạo ra
Kết quả kỳ vọng: Không được thỏa mãn trên tất cả các điều kiện đường đi
Số điều kiện đường đi thành công: 189
Số điều kiện đường đi thất bại: 176
Giải thích: Một Association chỉ được tạo ra nếu có một Company trong City

#### 5.4.3 Các hợp đồng về cơ sở (Facility Contracts)

**Pos-ChildSchool**
Phát biểu: Nếu một Child goesTo một School có một Service đặc biệt, thì một SpecialFacility phải được tạo ra có Person được tạo ra từ Child đó làm members
Kết quả kỳ vọng: Được thỏa mãn trên tất cả các điều kiện đường đi
Số điều kiện đường đi thành công: 168
Số điều kiện đường đi thất bại: 0

**Neg-SchoolOrdFac**
Phát biểu: Một OrdinaryFacility phải được tạo ra từ mỗi School
Kết quả kỳ vọng: Không được thỏa mãn trên tất cả các điều kiện đường đi
Số điều kiện đường đi thành công: 168
Số điều kiện đường đi thất bại: 60
Giải thích: Một School sẽ được chuyển đổi thành một SpecialFacility nếu nó cung cấp một Service đặc biệt

### 5.5 Tính biểu đạt của hợp đồng (Contract Expressiveness)

Mục này sẽ thảo luận ngắn gọn về tính biểu đạt của ngôn ngữ hợp đồng của chúng tôi.

Như đã thấy từ các ví dụ trên, các hợp đồng chứa một tiền điều kiện và một hậu điều kiện, mỗi cái đều chứa một đồ thị có kiểu. [42] chia các hợp đồng khả dĩ thành ba loại: bất biến số lượng (multiplicity invariants), bất biến cú pháp (syntactic invariants), và hợp đồng mẫu (pattern contracts)[^3].

#### 5.5.1 Bất biến số lượng (Multiplicity Invariants)

Các hợp đồng có thể biểu đạt các bất biến số lượng chứa trong siêu mô hình nguồn hoặc đích. Như đã thấy trong Hình 20 ở Mục 5.3.1, logic mệnh đề của ngôn ngữ hợp đồng của chúng tôi cho phép chúng tôi chỉ định rằng chỉ một Person nên được kết nối với một Community trong mô hình đầu ra. Điều này cho phép người dùng đảm bảo rằng các quy tắc không kết hợp để tạo ra nhiều phần tử hơn mong muốn.

Tuy nhiên xin lưu ý rằng, do sự trừu tượng hóa của phương pháp của chúng tôi, các bất biến số lượng này không nghiêm ngặt. Vì chỉ một lần thực thi của mỗi quy tắc được xem xét trong một điều kiện đường đi, công cụ chứng minh của chúng tôi sẽ không sinh ra các điều kiện đường đi trong đó một quy tắc thực thi nhiều lần. Do đó, các hợp đồng về số lượng như hợp đồng trong Hình 20 kiểm tra sự tồn tại của các lần thực thi chuyển đổi trong đó luôn luôn có hai phần tử Person được tạo ra.

#### 5.5.2 Bất biến cú pháp (Syntactic Invariants)

Các hợp đồng bất biến cú pháp kiểm tra liệu điều kiện đường đi có được hình thành tốt (well-formed) đối với cú pháp đầu vào hoặc đầu ra hay không. Một ví dụ về loại hợp đồng này được thể hiện trong Hình 21 cho nghiên cứu tình huống UML-to-Kiltera được mô tả trong Mục 6.1.3. Phát biểu không hình thức cho hợp đồng này là "nếu có một phần tử Inst, thì phần tử Inst đó có cùng tên với một phần tử ProcDef."

*Fig. 21 Một ví dụ về hợp đồng bất biến cú pháp*

[^3]: Ở đây chúng tôi loại trừ các hợp đồng khả năng đạt được của quy tắc (rule reachability contracts), vì công cụ chứng minh hiện nay tự động báo cáo việc một quy tắc không thực thi được.

#### 5.5.3 Hợp đồng mẫu (Pattern Contracts)

Loại hợp đồng cuối cùng được [42] mô tả là các hợp đồng mẫu, liên hệ các phần tử trong mô hình đầu vào với các phần tử trong mô hình đầu ra. Chín hợp đồng được trình bày trong Mục 5.4 cho chuyển đổi Families-to-Persons mở rộng thuộc loại này. Mục đích của những hợp đồng này là cho phép người dùng xác minh rằng nhiều quy tắc đang tương tác theo một cách hợp lệ, điều mà khó có thể xác định được từ việc kiểm tra thủ công các quy tắc.

#### 5.5.4 Hạn chế (Limitations)

Chúng tôi lưu ý rằng ngôn ngữ hợp đồng của chúng tôi cho phép định nghĩa nhiều loại điều kiện cấu trúc khác nhau. Có thể so sánh với [27], nơi các tác giả sử dụng PaMoMo làm nền tảng cho ngôn ngữ hợp đồng của họ. Điều này cho phép các tác giả định nghĩa nhiều loại hợp đồng trực quan để biểu đạt cả các hợp đồng phủ định lẫn khẳng định.

Tuy nhiên, ngôn ngữ hợp đồng của chúng tôi hiện bị hạn chế vì nó chỉ có thể biểu diễn các điều kiện cấu trúc chứ không phải các biểu thức tùy ý. Điều này khiến ngôn ngữ hợp đồng kém mạnh mẽ hơn nhiều so với các ngôn ngữ ràng buộc khác như OCL. Ví dụ, việc triển khai hiện tại của ngôn ngữ hợp đồng của chúng tôi không chứa các toán tử cho tập hợp, hoặc để xử lý các thuộc tính không phải String. Ngoài ra, vì chúng tôi đang biểu diễn một cách trừu tượng các quy tắc thực thi, và số lần mỗi quy tắc thực thi, người dùng phải cẩn thận về định nghĩa của họ về các cấu trúc số lượng. Các hợp đồng cũng không thể được viết để xác thực dữ liệu thực thể (instance data) cho các mô hình đầu vào hoặc đầu ra, chẳng hạn như đảm bảo rằng tất cả tên đầu vào bắt đầu bằng chữ cái viết hoa.

## 6 Kết quả thực nghiệm (Experimental Results)

Trong mục này chúng tôi trình bày một đánh giá về chuyển đổi bậc cao và kỹ thuật chứng minh hợp đồng của chúng tôi. Cụ thể, chúng tôi quan tâm đến các câu hỏi nghiên cứu sau:

- RQ1: Kỹ thuật của chúng tôi có áp dụng được cho các chuyển đổi ATL phức tạp không?
- RQ2: Thời gian và mức sử dụng bộ nhớ của công cụ chứng minh hợp đồng khác nhau như thế nào đối với mỗi nghiên cứu tình huống của chúng tôi?
- RQ3: Với một hợp đồng cụ thể, chúng ta có thể giảm thời gian cần cho việc chứng minh hợp đồng thông qua việc cắt lát chuyển đổi (transformation slicing) hay không?
- RQ4: Phiên bản chuyển đổi được sinh ra bởi chuyển đổi bậc cao của chúng tôi có khác biệt đáng kể so với một chuyển đổi được xây dựng thủ công hay không?

Xin lưu ý rằng RQ1 và RQ2 được thảo luận trực tiếp trong mục này, trong khi RQ3 được khảo sát trong Mục 7 và RQ4 trong Mục 8.

### 6.1 Thiết lập nghiên cứu (Study Setup)

Mục này sẽ mô tả các nghiên cứu tình huống được sử dụng để trả lời các câu hỏi nghiên cứu của chúng tôi.

#### 6.1.1 Các chuyển đổi Families-to-Persons

Một trong những thí nghiệm của chúng tôi cho công trình này là chuyển đổi Families-to-Persons được mô tả trong [36]. Chúng tôi giữ lại chuyển đổi này cho các thí nghiệm của mình, vì nó chứa một số khái niệm thú vị liên quan đến công trình xác minh của chúng tôi. Cụ thể, các quy tắc sinh ra các phần tử trong mô hình đầu ra không tầm thường (non-trivial), vì các phần tử đó có các thuộc tính được thiết lập thông qua việc thao tác các thuộc tính trong mô hình đầu vào. Nghiên cứu tình huống này kiểm tra khả năng của kỹ thuật của chúng tôi trong việc chuyển đổi đúng đắn các quy tắc thiết lập thuộc tính này và sau đó chứng minh các hợp đồng trên các chuyển đổi này.

Ngoài ra, nghiên cứu tình huống này về mặt kỹ thuật rất khó để chứng minh hợp đồng, vì nhiều quy tắc trong chuyển đổi chứa các phần tử trùng lặp, chẳng hạn như phần tử Family. Như đã mô tả trong Mục 5.3, công cụ chứng minh hợp đồng của chúng tôi phải có khả năng thực hiện đúng việc khớp không đẳng cấu (non-isomorphic matching) của hợp đồng lên một điều kiện đường đi. Nghĩa là, nếu có các phần tử tương tự trong hai quy tắc trong điều kiện đường đi, công cụ chứng minh hợp đồng phải giải quyết liệu các phần tử này khớp trên các phần tử riêng biệt trong mô hình đầu vào, hay trên cùng một phần tử.

Chúng tôi cũng đã thực hiện các thí nghiệm trên chuyển đổi Families-to-Persons mở rộng được mô tả trong Mục 3. Mở rộng này tăng số lượng quy tắc ATL từ năm trong chuyển đổi gốc lên mười trong phiên bản mở rộng, làm tăng số lượng quy tắc DSLTrans được sinh ra từ 9 lên 19. Do đó, số lượng điều kiện đường đi được sinh ra bởi công cụ chứng minh của chúng tôi tăng từ 101 lên 366.

Mục đích của việc thử nghiệm trên chuyển đổi này do đó là để khảo sát hiệu năng của công cụ chứng minh thuộc tính của chúng tôi trên một ví dụ chuyển đổi lớn hơn chứa các quy tắc và hợp đồng phức tạp hơn. Xin lưu ý rằng các hợp đồng được chứng minh trên chuyển đổi này được tạo ra bởi một tác giả của bài báo này và không đến từ công trình trước đây.

#### 6.1.2 Chuyển đổi GM-to-AUTOSAR

Một chuyển đổi khác mà chúng tôi khảo sát làm nghiên cứu tình huống là một chuyển đổi công nghiệp được thấy trong công trình chứng minh hợp đồng trước đây của chúng tôi [44]. Chuyển đổi được đề cập nhận làm mô hình đầu vào được định nghĩa trong một siêu mô hình cũ độc quyền (proprietary legacy metamodel) được sử dụng tại General Motors (GM) để phát triển Phần mềm điều khiển phương tiện (Vehicle Control Software). Siêu mô hình đầu ra là chuẩn công nghiệp ô tô AUTOSAR[^4]. Do đó, chuyển đổi này được sử dụng cho mục đích tiến hóa mô hình (model-evolution), di trú các mô hình sang chuẩn mới để có khả năng tương tác tốt hơn với các công cụ.

[^4]: AUTomotive Open System ARchitecture, AUTOSAR.org/

Ý định của chúng tôi với nghiên cứu tình huống này là hai mặt. Thứ nhất, chúng tôi quan tâm đến việc so sánh mức tiêu thụ thời gian và bộ nhớ của ví dụ công nghiệp này với các chuyển đổi khác.

Thứ hai, chúng tôi sẽ so sánh chuyển đổi DSLTrans được sinh ra bởi chuyển đổi bậc cao của chúng tôi, và chuyển đổi được xây dựng thủ công cho công trình trước đó. Những kết quả này sẽ được thảo luận trong bối cảnh RQ4, về việc liệu biểu diễn DSLTrans được sinh ra bởi chuyển đổi bậc cao có đủ hiệu quả để việc xác minh hợp đồng thay thế được phiên bản xây dựng thủ công hay không. Điều này sẽ được thảo luận trong Mục 8.1, cùng với một so sánh ngắn gọn về hai chuyển đổi DSLTrans.

Xin lưu ý rằng [42] thảo luận thêm về nghiên cứu tình huống GM-to-AUTOSAR, bao gồm một mô tả chi tiết về chuyển đổi và các hợp đồng cần được chứng minh.

#### 6.1.3 Chuyển đổi UML-to-Kiltera

Đối với nghiên cứu tình huống cuối cùng của chúng tôi, chúng tôi đã chọn một chuyển đổi để chuyển đổi một tập con của các sơ đồ máy trạng thái UML-RT thành Kiltera, là một "ngôn ngữ cho mô phỏng có thời gian (timed), hướng sự kiện (event-driven), di động (mobile) và phân tán (distributed)". Chuyển đổi được đề xuất trong [39] và được phát triển trong [37]. Trước đây, chúng tôi đã nghiên cứu chuyển đổi này để có được những hiểu biết sâu sắc về quy trình chứng minh hợp đồng [43].

Chúng tôi đưa nghiên cứu tình huống này vào vì những lý do tương tự như chuyển đổi GM-to-AUTOSAR. Vì các quy tắc chuyển đổi trong UML-to-Kiltera chứa một số lượng lớn các phần tử, đặc biệt là các phần tử trùng lặp, chúng tôi quan tâm đến khoản phạt hiệu năng (performance penalty) đối với các bước khớp và viết lại trong quá trình chứng minh hợp đồng. Một hợp đồng cụ thể khá rắc rối đối với quy trình khớp của chúng tôi, như được mô tả trong Mục 7.2.

Ngoài ra, chúng tôi quan tâm đến sự khác biệt giữa chuyển đổi được xây dựng thủ công cho [43], và phiên bản được sinh ra bởi chuyển đổi bậc cao (HOT) của chúng tôi. Cụ thể, một số cải tiến đã được thực hiện đối với chuyển đổi bậc cao để sinh ra đúng chuyển đổi DSLTrans cho nghiên cứu tình huống này, làm tăng khả năng áp dụng của phương pháp của chúng tôi trong việc xác minh các chuyển đổi ATL. Chi tiết thêm về việc so sánh giữa các phiên bản chuyển đổi xây dựng thủ công và do HOT sinh ra được trình bày trong Mục 8.2.

Chi tiết thêm về nghiên cứu tình huống này được trình bày trong [42], bao gồm cả hai siêu mô hình, tất cả các hợp đồng, và cả hai chuyển đổi ATL và DSLTrans. Xin lưu ý rằng một số hợp đồng đã được lược bỏ khỏi công trình hiện tại do một số tương đương chức năng.

### 6.2 Tóm tắt nghiên cứu tình huống (Case Study Summary)

Mục này trình bày ngắn gọn hai bảng so sánh các nghiên cứu tình huống về mặt cấu thành quy tắc ATL của chúng, cũng như một số thước đo cho các siêu mô hình đầu vào và đầu ra của chúng. Bản tóm tắt này được trình bày để hỗ trợ cho khẳng định của chúng tôi rằng kỹ thuật của chúng tôi có thể áp dụng cho nhiều loại chuyển đổi ATL khác nhau. Xin lưu ý rằng các siêu mô hình và chuyển đổi ATL/DSLTrans cho mỗi nghiên cứu tình huống đều có sẵn trên trang web của chúng tôi [3].

Các thước đo về kích thước và độ phức tạp của các siêu mô hình đầu vào và đầu ra cho mỗi chuyển đổi được trình bày trong Bảng 2. Các thước đo này bao gồm số lượng phần tử, quan hệ, và các quan hệ kế thừa hiện diện trong mỗi siêu mô hình.

**Bảng 2. Kích thước các siêu mô hình chuyển đổi**

| Chuyển đổi | Siêu mô hình | Số phần tử (Num. Elements) | Số quan hệ (Num. Assoc.) | Số thuộc tính (Num. Attrib.) | Số quan hệ kế thừa (Inheri. Relations) |
|---|---|---|---|---|---|
| Families-to-Person | Đầu vào | 3 | 5 | 2 | 0 |
| Families-to-Person | Đầu ra | 3 | 1 | 2 | 2 |
| Ext. Families-to-Person | Đầu vào | 11 | 21 | 3 | 7 |
| Ext. Families-to-Person | Đầu ra | 12 | 8 | 2 | 9 |
| GM-to-AUTOSAR | Đầu vào | 6 | 10 | 5 | 0 |
| GM-to-AUTOSAR | Đầu ra | 13 | 8 | 2 | 3 |
| UML-to-Kiltera | Đầu vào | 42 | 51 | 6 | 41 |
| UML-to-Kiltera | Đầu ra | 30 | 41 | 9 | 20 |

Bảng 3 trình bày số lượng quy tắc khớp, quy tắc lười, và helper trong chuyển đổi ATL cho mỗi nghiên cứu tình huống của chúng tôi.

### 6.3 Các thước đo (Measures)

Để trả lời một cách khách quan các câu hỏi nghiên cứu đã định nghĩa của chúng tôi, các thí nghiệm với công cụ chứng minh hợp đồng đã được tiến hành cho tất cả các nghiên cứu tình huống nêu trên. Đối với mỗi nghiên cứu tình huống, sự thành công của công cụ chứng minh hợp đồng của chúng tôi phụ thuộc vào việc liệu các hợp đồng mà chúng tôi đã chỉ ra là được thỏa mãn hay không được thỏa mãn có đúng trên tất cả các điều kiện đường đi hay không (khi thích hợp).

**Bảng 3. Số lượng và phân loại các quy tắc trong mỗi đặc tả ATL**

| Chuyển đổi | Số quy tắc khớp (Num. Matched) | Số quy tắc lười (Num. Lazy) | Số helper (Helpers) |
|---|---|---|---|
| Families-to-Person | 5 | 0 | 0 |
| Ext. Families-to-Person | 8 | 2 | 0 |
| GM-to-AUTOSAR | 3 | 2 | 0 |
| UML-to-Kiltera | 7 | 13 | 3 |

Thông tin sau đây được thu thập trong quá trình chứng minh hợp đồng cho mỗi nghiên cứu tình huống:

- Số lượng quy tắc trong mỗi chuyển đổi
- Số lượng điều kiện đường đi được sinh ra bởi công cụ chứng minh hợp đồng
- Thời gian cần thiết để sinh ra tất cả các điều kiện đường đi
- Số lượng hợp đồng cần được chứng minh trên nghiên cứu tình huống
- Thời gian cần thiết để chứng minh các hợp đồng
- Mức sử dụng bộ nhớ tối đa cần thiết bởi công cụ chứng minh hợp đồng

Xin lưu ý rằng số lượng quy tắc được tìm thấy trong chuyển đổi ATL có thể khác với chuyển đổi DSLTrans được sinh ra bởi chuyển đổi bậc cao. Do đó, cả hai số lượng đều được báo cáo.

Các thí nghiệm được chạy trên một Macbook Air đời 2013 với chip Intel Core i5-4250U và 8 GB RAM, chạy trên Arch Linux và Python 3.5.1. Cả quy trình xây dựng điều kiện đường đi lẫn quy trình chứng minh hợp đồng đều được song song hóa (parallelized) trên bốn luồng. Mỗi thí nghiệm được tiến hành ít nhất năm lần, với kết quả được lấy trung bình. Thông tin thời gian thu được bằng cách sử dụng gói thời gian time của Python. Thông tin bộ nhớ thu được bằng cách sử dụng lệnh /usr/bin/time. Xin lưu ý rằng thông tin sử dụng bộ nhớ cũng sẽ ghi lại chi phí không gian cần thiết cho trình thông dịch Python.

Tất cả các hiện vật được sử dụng cho các thí nghiệm của chúng tôi có thể được tìm thấy trên trang web của chúng tôi [3].

### 6.4 Kết quả (Results)

Bảng 4 cho thấy các kết quả hiệu năng cho việc chứng minh hợp đồng trên các nghiên cứu tình huống của chúng tôi. Bây giờ chúng tôi sẽ thảo luận các kết quả này trong bối cảnh hai câu hỏi nghiên cứu đầu tiên. RQ3 và RQ4 sẽ được thảo luận riêng trong Mục 7 và Mục 8.

#### 6.4.1 RQ1: Khả năng áp dụng của kỹ thuật (Applicability of the Technique)

Để trả lời câu hỏi nghiên cứu đầu tiên của chúng tôi "Kỹ thuật của chúng tôi có áp dụng được cho các chuyển đổi ATL phức tạp không?", chúng tôi đã thử nghiệm công cụ chứng minh hợp đồng của mình trên một số chuyển đổi có kích thước khác nhau, đến từ các miền ứng dụng khác nhau. Các thước đo cho các nghiên cứu tình huống được trình bày trong Mục 6.2.

Đối với mỗi nghiên cứu tình huống, các hợp đồng mà chúng tôi kỳ vọng được thỏa mãn đã được chứng minh thành công trên tất cả các điều kiện đường đi áp dụng được. Đối với các hợp đồng khác, không được thỏa mãn trong mọi trường hợp, các phản ví dụ được sinh ra chỉ ra chính xác tổ hợp quy tắc nơi hợp đồng không được đảm bảo là thỏa mãn. Các phản ví dụ này sau đó được kiểm tra thủ công để đảm bảo tính đúng đắn của chúng.

Ví dụ, chúng tôi đã thử chứng minh hợp đồng DaughterMother trên chuyển đổi Families-to-Person mở rộng, như đã mô tả chi tiết trong Mục 5.3. Công cụ chứng minh hợp đồng của chúng tôi đã chỉ ra đúng đắn rằng đối với các mô hình đầu vào chỉ chứa các phần tử con gái và mẹ, không có sự đảm bảo rằng có một phần tử Man trong mô hình đầu ra. Vì đây là kết quả được kỳ vọng, điều này làm tăng độ tin cậy của chúng tôi vào tính đúng đắn của chuyển đổi.

Sự thành công của công cụ chứng minh hợp đồng của chúng tôi trên các nghiên cứu tình huống này cho phép chúng tôi kết luận rằng chúng tôi có thể áp dụng kỹ thuật của mình cho nhiều loại chuyển đổi ATL phức tạp với các kích thước quy tắc và siêu mô hình khác nhau.

#### 6.4.2 RQ2: Đặc tính thời gian và bộ nhớ (Time and Memory Characteristics)

Để trả lời câu hỏi nghiên cứu thứ hai của chúng tôi, "Thời gian và mức sử dụng bộ nhớ của công cụ chứng minh hợp đồng khác nhau như thế nào đối với mỗi nghiên cứu tình huống của chúng tôi?", chúng tôi tham chiếu đến các kết quả trong Bảng 4 chứa các kết quả hiệu năng của các thí nghiệm của chúng tôi.

**Bảng 4. Kết quả hiệu năng**

| Chuyển đổi | Số quy tắc ATL/DSLTrans | Số điều kiện đường đi được sinh ra | Thời gian sinh ĐKĐĐ (s) | Số hợp đồng được chứng minh | Thời gian chứng minh (s) | Bộ nhớ (MB) |
|---|---|---|---|---|---|---|
| Families-to-Person | 5 / 9 | 101 | 0,24 | 4 | 0,52 | 54 |
| Extended Families-to-Person | 10 / 19 | 366 | 3,89 | 10 | 7,35 | 59 |
| GM-to-AUTOSAR (handbuilt) | 5 / 9 | 13 | 0,18 | 9 | 0,15 | 58 |
| GM-to-AUTOSAR (HOT) | 5 / 9 | 10 | 0,26 | 9 | 0,15 | 60 |
| UML-to-Kiltera | 20 / 17 | 322 | 1,86 | 15 | 11,99 | 55 |

Xin lưu ý rằng mặc dù số lượng điều kiện đường đi được sinh ra chắc chắn phụ thuộc vào số lượng quy tắc DSLTrans trong chuyển đổi, không có một công thức tuyến tính nào có thể được áp dụng. Ví dụ, chuyển đổi Families-to-Persons mở rộng đã sinh ra số lượng điều kiện đường đi gấp ba lần chuyển đổi Families-to-Persons gốc, mặc dù phiên bản mở rộng có số lượng quy tắc gấp khoảng hai lần.

Số lượng điều kiện đường đi chính xác được sinh ra sẽ phụ thuộc vào độ phức tạp của cách các quy tắc có thể kết hợp với nhau, chẳng hạn như số lượng phụ thuộc giữa các quy tắc hoặc thậm chí số lượng phần tử trong mỗi quy tắc. Ngoài ra, vì việc sinh điều kiện đường đi của chúng tôi được triển khai bằng cách sử dụng khớp và viết lại đồ thị, các quy tắc lớn hơn cũng sẽ mất nhiều thời gian hơn để kết hợp, làm tăng thời gian cần cho việc sinh điều kiện đường đi [32].

Thời gian để chứng minh các hợp đồng trên mỗi chuyển đổi cũng phụ thuộc vào một số yếu tố. Tương tự như việc sinh điều kiện đường đi, thời gian cần cho việc chứng minh hợp đồng gần như tỉ lệ thuận với số lượng điều kiện đường đi được sinh ra cho một chuyển đổi, số lượng hợp đồng cần được chứng minh trên chuyển đổi đó, và thành phần của các điều kiện đường đi và các hợp đồng.

Xin lưu ý rằng thời gian chứng minh hợp đồng của chúng tôi khác biệt (và thực sự có thể tệ hơn) so với những gì được báo cáo trong [36] hoặc các công trình trước đây. Điều này chủ yếu là do việc thay thế thuật toán khớp cốt lõi trong công cụ chứng minh. Hãy nhớ rằng việc khớp các hợp đồng lên các điều kiện đường đi là không đẳng cấu, như đã thảo luận trong Mục 5.3. Trước đây công cụ chứng minh của chúng tôi có một bước "khử nhập nhằng" (disambiguation) để tạo ra một cách tường minh tất cả các sự chồng chéo khả dĩ của các quy tắc, sau đó có thể được khớp bằng một bộ khớp đẳng cấu chuẩn. Một thuật toán khớp mới đã được thiết kế để bỏ qua bước này và tính đến các phần tử chồng chéo này. Sự cải tiến thuật toán này cũng có tác dụng phụ là có xu hướng tạo ra nhiều điều kiện đường đi hơn so với các công trình trước đây của chúng tôi.

Chúng tôi lưu ý rằng thuật toán khớp mới này chưa phải là đối tượng của việc tối ưu hóa nặng, và chúng tôi kỳ vọng những cải tiến tốc độ hơn nữa trong tương lai. Cụ thể, chúng tôi lưu ý rằng một hợp đồng cụ thể cho nghiên cứu tình huống UML-to-Kiltera có hiệu năng khớp rất tệ, mất 142 giây để chứng minh. Điều này hoàn toàn là do thuật toán khớp chưa tối ưu hóa của chúng tôi. Cụ thể, hợp đồng chứa một phần tử New được kết nối với bốn phần tử Name. Ngoài ra, cấu trúc này được lặp lại một số lần trong các điều kiện đường đi của chuyển đổi. Vì thuật toán khớp của chúng tôi hiện dựa trên một phương pháp dựa trên quan hệ (association-based), một sự bùng nổ tổ hợp (combinational explosion) xảy ra khi bộ khớp cố gắng trả về tất cả các khớp khả dĩ. Chúng tôi coi hợp đồng này là một trường hợp biên (edge case), và thời gian chứng minh của nó không được đưa vào Bảng 4 vì nó hoàn toàn là hiện vật của thuật toán khớp chưa tối ưu hóa của chúng tôi. Công việc tương lai sẽ cố gắng giải quyết vấn đề triển khai này.

Mức sử dụng bộ nhớ của công cụ chứng minh hợp đồng của chúng tôi phụ thuộc vào số lượng quy tắc DSLTrans trong chuyển đổi, và vào số lượng điều kiện đường đi được tạo ra. Xin lưu ý rằng đối với các chuyển đổi được sử dụng ở đây làm nghiên cứu tình huống, mức sử dụng bộ nhớ của công cụ chứng minh nằm trong khoảng từ 54 đến 60 MB, thấp hơn 10 MB so với chi phí để chạy các script Python.

Nhìn chung, phương pháp chứng minh hợp đồng của chúng tôi giữ trong một ngân sách thời gian và bộ nhớ khiêm tốn. Tất cả các chuyển đổi đều có điều kiện đường đi được sinh ra và có các hợp đồng được chứng minh trong vòng 15 giây và 60 MB bộ nhớ. Thật vậy, ngay cả hợp đồng trường hợp biên cũng có thời gian chứng minh hợp lý là 142 giây. Công việc tương lai sẽ theo đuổi các tối ưu hóa cho kỹ thuật của chúng tôi nhằm chứng minh các hợp đồng trên các chuyển đổi ATL và DSLTrans thậm chí lớn hơn và phức tạp hơn.

## 7 Cắt lát chuyển đổi (Slicing Transformations)

Mục này sẽ mở rộng thuật toán cắt lát được giới thiệu trong [36]. Trái ngược với công trình trước đây, thuật toán này giờ đây đã trở thành một phần tự động của công cụ chứng minh hợp đồng.

Mục đích của thuật toán này là tạo ra tập hợp tối thiểu các quy tắc chuyển đổi cho một hợp đồng cho trước, sao cho khi tập hợp này được thực thi tượng trưng bởi công cụ chứng minh hợp đồng, kết quả đúng đắn được sinh ra. Việc giảm số lượng quy tắc cần được thực thi tượng trưng cho phép giảm đáng kể lượng thời gian cần thiết cho quy trình chứng minh.

Do đó, thuật toán cắt lát này là nỗ lực của chúng tôi để trả lời RQ3: "Với một hợp đồng cụ thể, chúng ta có thể giảm thời gian cần cho việc chứng minh hợp đồng thông qua việc cắt lát chuyển đổi hay không?"

### 7.1 Tổng quan về bộ cắt lát (Slicer Overview)

Có ba bước trong kỹ thuật của chúng tôi để cắt lát chuyển đổi cho một hợp đồng.

Bước đầu tiên là phân rã (decompose) hợp đồng thành các phần tử và quan hệ có kiểu của nó. Thông tin này cho phép thuật toán cắt lát xác định những quy tắc nào cần thiết phải tham gia vào quy trình chứng minh hợp đồng.

Bước thứ hai khảo sát tất cả các quy tắc trong chuyển đổi, và xác định những quy tắc chứa các phần tử cần thiết để hợp đồng khớp lên.

Cuối cùng, bước thứ ba xác định liệu những quy tắc được chọn trong bước thứ hai có yêu cầu các phần tử được tạo ra bởi các quy tắc trước đó hay không. Đây phải là một quy trình lặp (iterative) để cho phép tất cả các quy tắc cần thiết thực thi. Xin lưu ý rằng việc phân tích phụ thuộc này hiện đang được thực hiện rất bảo thủ (conservatively), và công việc tương lai sẽ cố gắng tối ưu hóa quy trình để loại bỏ nhiều quy tắc hơn.

*Fig. 22 Hợp đồng ví dụ cho quy trình cắt lát*

Tất cả những quy tắc không cần thiết cho hợp đồng sẽ bị loại bỏ khỏi chuyển đổi cần được xác minh. Xin lưu ý rằng chuyển đổi mới này có thể nhỏ hơn chuyển đổi gốc, nhưng điều này tùy thuộc vào các phụ thuộc cụ thể giữa hợp đồng và các quy tắc chuyển đổi.

#### 7.1.1 Phân rã hợp đồng và quy tắc (Decomposing Contract and Rules)

Để hỗ trợ thuật toán cắt lát, cần phải xác định những quy tắc nào mà hợp đồng (và các quy tắc khác) yêu cầu để thực thi. Điều này được xác định bằng cách "phân rã" cấu trúc đồ thị có kiểu bên dưới để xác định chính xác những phần tử nào nó khớp trên. Trong việc triển khai hiện tại, các liên kết ngược và các quan hệ giữa các phần tử trong đồ thị được trích xuất, cũng như bất kỳ phần tử nào không được kết nối với các phần tử khác, được gọi là các phần tử cô lập (isolated elements).

Ví dụ, hãy xem xét hợp đồng trong Hình 22. Có hai quan hệ trong tiền điều kiện, mỗi quan hệ được cấu thành từ một phần tử Member được kết nối với một phần tử Family. Một quan hệ có kiểu daughters, trong khi quan hệ kia có kiểu mothers. Ngoài ra, có liên kết ngược kết nối một phần tử trong tiền điều kiện với một phần tử trong hậu điều kiện, thực thi yêu cầu rằng một phần tử Man đã được tạo ra bởi cùng quy tắc đã khớp phần tử Family.

Bước thứ hai của thuật toán cắt lát là khảo sát tất cả các quy tắc trong chuyển đổi. Hãy nhớ rằng các điều kiện đường đi mà hợp đồng khớp lên đã được tạo ra bằng cách kết hợp các quy tắc (x. Mục 5.2). Do đó, để các quan hệ trong hợp đồng xuất hiện trong điều kiện đường đi, một trong những quy tắc chứa quan hệ này phải đã được thực thi tượng trưng.

Mỗi quy tắc được kiểm tra để xác định liệu có các bản sao đẳng cấu của các quan hệ hợp đồng, liên kết ngược, hoặc phần tử cô lập hiện diện trong quy tắc hay không. Nếu có, thì quy tắc đó có thể sinh ra quan hệ hoặc phần tử cần thiết, vì vậy quy tắc được đánh dấu là thiết yếu (crucial) đối với việc chứng minh hợp đồng.

Để làm rõ về các liên kết ngược, hãy nhớ rằng vì các liên kết ngược phải khớp trên các liên kết khả năng truy vết, trong đó một phần tử đầu vào sinh ra một phần tử đầu ra như một phần của cùng quy tắc. Do đó, bước này thành công khi cả hai phần tử được kết nối bởi liên kết ngược đều được tìm thấy trong quy tắc, mặc dù không có liên kết khả năng truy vết tường minh giữa chúng.

Bước thu thập này rất bảo thủ, vì nó bao gồm tất cả các quy tắc chứa bất kỳ quan hệ hợp đồng hoặc phần tử cô lập nào. Tuy nhiên, việc suy luận về hợp đồng như một tập hợp các quan hệ và phần tử cô lập thay vì một đồ thị hoàn chỉnh là đúng đắn. Hãy nhớ rằng trong Mục 5.3, hợp đồng không được khớp một cách đẳng cấu lên điều kiện đường đi, do cấu trúc điều kiện đường đi đại diện cho việc thực thi một tập hợp các quy tắc chuyển đổi. Do đó, các phần tử cần thiết cho hợp đồng có thể bị "tách" giữa nhiều quy tắc trong chuyển đổi, đòi hỏi một phương pháp phân rã.

Xin lưu ý rằng nếu bất kỳ quan hệ, liên kết ngược, hoặc phần tử cô lập nào trong hợp đồng không thể được tìm thấy trong toàn bộ tập hợp các quy tắc chuyển đổi, thì hợp đồng không thể khớp trên bất kỳ điều kiện đường đi nào được sinh ra bởi thuật toán chứng minh. Điều này chỉ ra rằng hoặc là hợp đồng hoặc là chuyển đổi chứa lỗi và phải được sửa.

Bước cuối cùng là suy luận về các quy tắc được đánh dấu là thiết yếu cho việc chứng minh hợp đồng trong bước thứ hai. Các bước phân rã và tìm kiếm được mô tả ở trên được lặp lại cho mỗi quy tắc. Điều này tạo ra một đồ thị phụ thuộc quy tắc (rule-dependency graph) cực kỳ bảo thủ, chỉ ra các quy tắc phải hiện diện trong chuyển đổi để hợp đồng này được chứng minh đúng đắn.

### 7.2 Kết quả và thảo luận (Results and Discussion)

Để đo lường tác động của thuật toán cắt lát đối với việc chứng minh hợp đồng, chúng tôi đã khảo sát ảnh hưởng của việc cắt lát chuyển đổi UML-to-Kiltera. Một số hợp đồng đã được chứng minh trên cả toàn bộ chuyển đổi (được gọi là phiên bản "gốc") lẫn tập con của chuyển đổi được trả về bởi thuật toán cắt lát (phiên bản "đã cắt lát"). Xin lưu ý rằng thời gian cần thiết để thực hiện việc cắt lát bản thân nó là dưới 0,05 giây cho tất cả các hợp đồng.

Các kết quả trong Bảng 5 cho thấy sự giảm thiểu thời gian chứng minh hợp đồng khi việc cắt lát được thực hiện. Chuyển đổi UML-to-Kiltera gốc, ban đầu chứa 17 quy tắc DSLTrans, đã được cắt lát thành các tập con dao động từ 2 đến 15 quy tắc cho mỗi hợp đồng. Xin lưu ý rằng các chuyển đổi đã cắt lát sinh ra nhiều nhất là một nửa số điều kiện đường đi so với chuyển đổi gốc, làm giảm đáng kể cả thời gian xây dựng điều kiện đường đi lẫn thời gian chứng minh hợp đồng. Hơn nữa, kết quả của việc chứng minh hợp đồng là giống hệt nhau cho cả phiên bản bình thường lẫn phiên bản đã cắt lát.

**Bảng 5. Ảnh hưởng của việc cắt lát đối với thời gian chứng minh hợp đồng cho chuyển đổi UML-to-Kiltera**

| Tên | Phiên bản | Số quy tắc | Số ĐKĐĐ | Thời gian xây dựng ĐKĐĐ (s) | Thời gian chứng minh (s) |
|---|---|---|---|---|---|
| PP1 | Original | 17 | 322 | 1,64 | 6,77 |
| PP1 | Sliced | 14 | 161 | 0,93 | 3,26 |
| PP2 | Original | 17 | 322 | 1,80 | 6,63 |
| PP2 | Sliced | 14 | 161 | 0,94 | 3,15 |
| PP3 | Original | 17 | 322 | 1,75 | 141,15 |
| PP3 | Sliced | 14 | 161 | 0,89 | 139,41 |
| PP4 | Original | 17 | 322 | 1,85 | 7,02 |
| PP4 | Sliced | 14 | 161 | 1,01 | 3,42 |
| MM1 | Original | 17 | 322 | 1,47 | 5,29 |
| MM1 | Sliced | 2 | 3 | 0,05 | 0,09 |
| MM2 | Original | 17 | 322 | 1,68 | 7,01 |
| MM2 | Sliced | 8 | 64 | 0,13 | 0,12 |
| MM3 | Original | 17 | 322 | 1,87 | 7,06 |
| MM3 | Sliced | 11 | 64 | 0,55 | 0,62 |
| MM4 | Original | 17 | 322 | 1,84 | 7,00 |
| MM4 | Sliced | 11 | 64 | 0,58 | 0,64 |
| MM5 | Original | 17 | 322 | 1,84 | 7,00 |
| MM5 | Sliced | 12 | 99 | 0,76 | 1,18 |
| MM6 | Original | 17 | 322 | 1,71 | 6,33 |
| MM6 | Sliced | 2 | 3 | 0,04 | 0,08 |
| MM7 | Original | 17 | 322 | 1,55 | 5,65 |
| MM7 | Sliced | 8 | 7 | 0,13 | 0,11 |
| MM8 | Original | 17 | 322 | 1,84 | 6,84 |
| MM8 | Sliced | 12 | 99 | 0,74 | 1,14 |
| MM9 | Original | 17 | 322 | 1,81 | 7,03 |
| MM9 | Sliced | 12 | 99 | 0,77 | 1,13 |
| MM10 | Original | 17 | 322 | 1,47 | 5,29 |
| MM10 | Sliced | 11 | 64 | 0,59 | 0,67 |
| MM11 | Original | 17 | 322 | 1,55 | 5,81 |
| MM11 | Sliced | 12 | 115 | 0,77 | 1,97 |
| SS1 | Original | 17 | 322 | 1,57 | 5,89 |
| SS1 | Sliced | 15 | 112 | 0,28 | 0,74 |

Tuy nhiên, số lượng quy tắc trong lát cắt phụ thuộc vào các phần tử cụ thể liên quan đến hợp đồng và các quy tắc. Ví dụ, việc cắt lát chuyển đổi cho hợp đồng MM6 đã tạo ra một chuyển đổi DSLTrans với 2 quy tắc, trong khi việc cắt lát cho hợp đồng SS1 đã tạo ra một chuyển đổi với 15 quy tắc.

Như đã mô tả trong Mục 6.4.2, thời gian chứng minh cho hợp đồng PP3 là một điểm ngoại lệ (outlier) đáng kể so với các hợp đồng còn lại, ngay cả khi chuyển đổi đã được cắt lát. Như đã đề cập, chúng tôi coi đây là một hiện vật của thuật toán khớp chưa tối ưu hóa của chúng tôi.

Các kết quả này cho thấy việc cắt lát chuyển đổi dựa trên hợp đồng cần chứng minh có thể có tác động lớn đến thời gian chứng minh. Thời gian xây dựng điều kiện đường đi đã giảm từ 43 đến 97 phần trăm, trong khi thời gian chứng minh hợp đồng đã giảm từ 51 đến 98 phần trăm (không tính PP3). Điều này trả lời câu hỏi nghiên cứu của chúng tôi một cách khẳng định.

Ngoài ra, trái ngược với công trình trước đây của chúng tôi trong [36], việc cắt lát này hiện cũng có thể được thực hiện tự động trong quá trình chứng minh hợp đồng. Xin lưu ý rằng việc triển khai hiện tại của bộ cắt lát dựa trên một sự phân rã tương đối đơn giản của các đồ thị hợp đồng và quy tắc, cùng với việc xây dựng một đồ thị phụ thuộc quy tắc bảo thủ. Công việc tương lai sẽ đảm bảo rằng số lượng quy tắc tối thiểu được chọn trong chuyển đổi đã cắt lát.

Chúng tôi lưu ý rằng kỹ thuật cắt lát của chúng tôi có những điểm tương đồng rõ ràng với các công trình xác minh chuyển đổi khác. Ví dụ, [13] so sánh định lượng các phần tử trong "Tracts" (một phiên bản tương tự các hợp đồng của chúng tôi[^5]) với các quy tắc chuyển đổi để gợi ý cho người dùng những quy tắc nào đang khiến Tract thất bại. Tuy nhiên, phương pháp của họ khác với phương pháp của chúng tôi theo hai cách cơ bản. Thứ nhất, phương pháp của [13] tập trung vào việc hướng dẫn người dùng đến các quy tắc có vấn đề[^6]. Phương pháp cắt lát của chúng tôi là một sự tối ưu hóa hiệu năng để giảm số lượng điều kiện đường đi phải được tạo ra. Thứ hai, chuyển đổi đã cắt lát của chúng tôi phải chứa tất cả các quy tắc có thể thay đổi kết quả của việc hợp đồng được thỏa mãn hay không được thỏa mãn trên một chuyển đổi. Chúng tôi không thể chấp nhận một kết quả sai trong việc xác minh của mình như được cho phép trong [13], và do đó tập hợp quy tắc của chúng tôi phải được xây dựng một cách bảo thủ.

[^5]: Công trình liên quan về Tracts được thảo luận chi tiết hơn trong Mục 9.
[^6]: Xin lưu ý rằng sự hướng dẫn này được giải quyết một phần trong công trình của chúng tôi. Khi các điều kiện đường đi không thỏa mãn một hợp đồng, chúng tôi báo cáo điều kiện đường đi đại diện cho số lượng quy tắc tối thiểu. Do đó, chính là sự tương tác của các quy tắc này gây ra việc hợp đồng thất bại.

## 8 Chuyển đổi xây dựng thủ công so với chuyển đổi do HOT sinh ra (Hand-built versus HOT-produced Transformations)

Mục này sẽ khảo sát câu hỏi nghiên cứu cuối cùng của chúng tôi, RQ4, "Phiên bản chuyển đổi được sinh ra bởi chuyển đổi bậc cao của chúng tôi có khác biệt đáng kể so với một chuyển đổi được xây dựng thủ công hay không?" Các nghiên cứu tình huống quan tâm là các chuyển đổi GM-to-AUTOSAR và UML-to-Kiltera. Vì các chuyển đổi DSLTrans được sinh ra trực tiếp từ các chuyển đổi ATL, việc so sánh trực tiếp các chuyển đổi được sinh ra này với các phiên bản xây dựng thủ công được tạo ra bởi các đối tác học thuật của chúng tôi trong công trình trước đây là rất có ý nghĩa. Cụ thể, chúng tôi quan tâm đến khoản phạt hiệu năng do các chuyển đổi không được tối ưu hóa. Nếu khoản phạt này là nhỏ hoặc không tồn tại, thì HOT có thể phục vụ như một sự thay thế tự động cho việc xây dựng chuyển đổi bằng tay.

### 8.1 Chuyển đổi GM-to-AUTOSAR

Như đã thảo luận trong Mục 6.1.2, chuyển đổi này di trú các mô hình từ một siêu mô hình độc quyền của General Motors sang một siêu mô hình chuẩn công nghiệp [44].

#### 8.1.1 Hình dạng chuyển đổi (Transformation Shape)

Vì lý do ngắn gọn, các phiên bản chuyển đổi xây dựng thủ công và do HOT sinh ra sẽ không được trình bày dưới dạng hình vẽ. Thay vào đó, các chuyển đổi được tóm tắt trong Bảng 6 và Bảng 7 bằng cách liệt kê số lượng phần tử match và apply trong mỗi quy tắc. Toàn bộ các chuyển đổi có thể được tìm thấy trên trang web của chúng tôi [3].

**Bảng 6. Cấu trúc chuyển đổi GM-to-AUTOSAR (Xây dựng thủ công)**

| Tầng | Tên quy tắc | Số phần tử Match | Số phần tử Apply |
|---|---|---|---|
| 1 | MapPN2FiveElements | 1 | 5 |
| 1 | MapModule | 3 | 2 |
| 1 | MapPartition | 2 | 1 |
| 2 | ConnECU2VirtDev1 | 2 | 2 |
| 3 | ConnVirtDev2Distrib1 | 3 | 2 |
| 4 | ConnVirtDev2Distrib2 | 2 | 2 |
| 5 | ConnECU2VirtDev2 | 2 | 2 |
| 6 | ConnPPortProto | 5 | 2 |
| 6 | ConnRPortProto | 5 | 2 |
| **Tổng cộng (9 quy tắc)** | | **25** | **20** |

**Bảng 7. Cấu trúc chuyển đổi GM-to-AUTOSAR (HOT)**

| Tầng | Tên quy tắc | Số phần tử Match | Số phần tử Apply |
|---|---|---|---|
| 1 | createComponent | 1 | 2 |
| 2 | initSysTemp | 3 | 6 |
| 3 | initSwc2EcuMap | 3 | 1 |
| 4 | sysMapping | 2 | 2 |
| 5 | compostype | 3 | 2 |
| 6 | mappingcomponent | 2 | 2 |
| 7 | mappingECUinstance | 2 | 2 |
| 8 | pportprototype | 5 | 2 |
| 9 | rportprototype | 5 | 2 |
| **Tổng cộng (9 quy tắc)** | | **26** | **21** |

Xin lưu ý rằng cả phiên bản xây dựng thủ công lẫn phiên bản do HOT sinh ra của chuyển đổi đều có chín quy tắc, và số lượng phần tử match và apply được sinh ra là xấp xỉ tương đương. Điều này chỉ ra rằng HOT đang sinh ra một chuyển đổi có độ phức tạp tương tự với những gì một con người sẽ xây dựng. Tuy nhiên xin lưu ý rằng HOT hiện nay sinh ra một chuyển đổi chứa một quy tắc trên mỗi tầng.

#### 8.1.2 Ảnh hưởng đến việc chứng minh hợp đồng (Effect on Contract Proving)

Câu hỏi nghiên cứu của chúng tôi đặt ra là liệu chuyển đổi do HOT sinh ra có đủ để thay thế chuyển đổi xây dựng thủ công khi chứng minh hợp đồng hay không. Các kết quả sau đây trong Bảng 8 cho thấy sự so sánh giữa việc chứng minh mỗi hợp đồng trên hai phiên bản của chuyển đổi. Xin lưu ý rằng 13 điều kiện đường đi đã được sinh ra cho chuyển đổi GM-to-AUTOSAR xây dựng thủ công, trong khi 10 điều kiện đường đi đã được sinh ra cho phiên bản do HOT sinh ra.

Chúng tôi lưu ý rằng tất cả các hợp đồng đều được chứng minh trong một khoảng thời gian gần như tương đương, và có kết quả tương đương giữa hai phiên bản của chuyển đổi. Các thất bại của hợp đồng đối với M1 và M3 là được kỳ vọng, vì chuyển đổi ATL gốc chứa lỗi [42].

**Bảng 8. Ảnh hưởng của phiên bản GM-to-AUTOSAR đến việc chứng minh hợp đồng**

| Tên | Phiên bản | Số ĐKĐĐ thành công | Số ĐKĐĐ thất bại | Thời gian chứng minh (s) |
|---|---|---|---|---|
| M1 | Hand-built | 4 | 8 | 0,06 |
| M1 | HOT | 4 | 4 | 0,05 |
| M2 | Hand-built | 12 | 0 | 0,05 |
| M2 | HOT | 8 | 0 | 0,05 |
| M3 | Hand-built | 4 | 4 | 0,05 |
| M3 | HOT | 4 | 4 | 0,05 |
| M4 | Hand-built | 8 | 0 | 0,06 |
| M4 | HOT | 8 | 0 | 0,05 |
| M5 | Hand-built | 12 | 0 | 0,06 |
| M5 | HOT | 8 | 0 | 0,05 |
| M6 | Hand-built | 12 | 0 | 0,06 |
| M6 | HOT | 8 | 0 | 0,05 |
| P1 | Hand-built | 6 | 0 | 0,07 |
| P1 | HOT | 4 | 0 | 0,05 |
| P2 | Hand-built | 6 | 0 | 0,07 |
| P2 | HOT | 4 | 0 | 0,07 |
| S1 | Hand-built | 4 | 0 | 0,06 |
| S1 | HOT | 4 | 0 | 0,08 |

### 8.2 Chuyển đổi UML-to-Kiltera

Như đã đề cập trong Mục 6.1.3, chuyển đổi UML-to-Kiltera chuyển đổi các sơ đồ máy trạng thái UML-RT thành ngôn ngữ Kiltera cho mục đích xác minh và mô phỏng. Nó được thảo luận sâu hơn trong [37] và [42].

Các tác giả vui mừng ghi nhận rằng chính xác cùng các quy tắc đã được sinh ra bởi chuyển đổi bậc cao từ mã chuyển đổi ATL. Trên thực tế, tất cả các phần tử và tên đều nhất quán giữa các phiên bản, cho phép chúng tôi tuyên bố rằng các chuyển đổi xây dựng thủ công và do HOT sinh ra là giống hệt nhau về mặt chức năng.

Trái ngược với các nghiên cứu tình huống khác của chúng tôi, cũng đáng chú ý rằng phiên bản DSLTrans của chuyển đổi UML-to-Kiltera chỉ chứa 17 quy tắc so với 20 quy tắc trong phiên bản ATL. Sự khác biệt này là do phiên bản ATL chứa sáu quy tắc lười tầm thường thực hiện việc thiết lập thuộc tính.

### 8.3 Kết luận (Conclusion)

Các kết quả cho cả hai thí nghiệm chỉ ra rằng các chuyển đổi DSLTrans được sinh ra có chất lượng tương đương với các phiên bản xây dựng thủ công. Có một khoản phạt hiệu năng nhỏ đến không tồn tại trong một trường hợp, và trong trường hợp kia các quy tắc được sinh ra giống hệt với phiên bản xây dựng thủ công. Do đó, chúng tôi tin rằng việc sử dụng chuyển đổi bậc cao của chúng tôi như một phần của chuỗi công cụ (toolchain) để xác minh các chuyển đổi ATL là đủ.

## 9 Công trình liên quan (Related Work)

Đã có nhiều công trình sâu rộng về việc xác minh các khía cạnh khác nhau của các chuyển đổi mô hình, ví dụ, x. [6, 40] cho các khảo sát (surveys) trong lĩnh vực này. Liên quan đến đóng góp của bài báo này, chúng tôi tóm tắt các đóng góp trước đây cho việc kiểm tra các loại hợp đồng khác nhau đối với các chuyển đổi mô hình, trong đó các phương pháp cụ thể trải dài từ kiểm thử đến các phương pháp xác minh.

### 9.1 Kiểm thử chuyển đổi mô hình (Model Transformation Testing)

Trong [25, 48] các tác giả mô tả phương pháp của họ trong đó "Tracts" có thể được chỉ định cho các chuyển đổi mô hình. Các tract này định nghĩa một tập hợp các ràng buộc trên các siêu mô hình nguồn và đích, một tập hợp các ràng buộc nguồn-đích, và một bộ kiểm thử tract (tract test suite), nghĩa là, một tập hợp các mô hình nguồn thỏa mãn các ràng buộc nguồn. Công cụ TractsTool đi kèm sau đó có thể tự động chuyển đổi các mô hình nguồn thành siêu mô hình đích, và sau đó xác minh rằng các cặp mô hình nguồn/đích thỏa mãn các ràng buộc. Lợi thế của điều này là phương pháp không đòi hỏi tính toán nặng, vì các kiểm thử có thể được tập trung hẹp theo cách mô-đun hóa.

Bên cạnh phương pháp Tracts, có một số phương pháp khác hỗ trợ việc kiểm thử các chuyển đổi mô hình dựa trên các loại hợp đồng khác nhau như các đoạn mô hình (model fragments) [35], các mẫu đồ thị (graph patterns) [9,27], Ngữ pháp đồ thị bộ ba (Triple Graph Grammars — TGGs) [49], các ngôn ngữ kiểm thử chuyên dụng [22,29], hoặc như được sử dụng trong Tracts, các ràng buộc OCL [17], và thậm chí là sự kết hợp của các phương pháp nêu trên [23]. Trong khi các phương pháp nêu trên sử dụng kiểm thử hộp đen (black-box), cũng có các phương pháp cho phép kiểm thử hộp trắng (white-box) cho các chuyển đổi mô hình như [26].

Trái ngược với các phương pháp kiểm thử, phương pháp được trình bày trong bài báo này cho phép các hợp đồng được chứng minh cho tất cả các lần thực thi chuyển đổi khả dĩ, nghĩa là, cho tất cả các mô hình đầu vào khả dĩ. Tuy nhiên, chúng tôi cũng giữ cùng ý tưởng kéo theo: tiền điều kiện của một thuộc tính đặt các ràng buộc lên các mô hình đầu vào của chuyển đổi, và sau đó, hậu điều kiện định nghĩa các ràng buộc lên mô hình đầu ra.

### 9.2 Xác minh chuyển đổi mô hình (Model Transformation Verification)

Công trình trước đây cũng đề xuất ý tưởng chuyển đổi ATL sang các miền hình thức. Công trình của [47] mô tả một ngữ nghĩa hình thức cho ATL, sao cho các chuyển đổi ATL có thể được biểu đạt trong ngôn ngữ hình thức Maude. Một khi được biểu đạt trong Maude, các thuộc tính sau đó có thể được xác minh trên việc thực thi chuyển đổi này, chẳng hạn như khả năng đạt được (reachability) của các trạng thái cụ thể, hoặc việc không có nhiều hơn một quy tắc được khớp trên mỗi phần tử nguồn. Trong công trình của chúng tôi, chúng tôi dịch chuyển đổi ATL thành ngôn ngữ chuyển đổi DSLTrans để chứng minh các hợp đồng chuyển đổi, điều không nằm trong phạm vi của [47].

Công trình trong [15] tự động dịch các chuyển đổi trong một số ngôn ngữ chuyển đổi (như ATL) sang OCL. Ngoài ra, tương tự như hệ thống của chúng tôi, các bất biến, tiền điều kiện và hậu điều kiện được mô tả theo định dạng đồ thị. Tuy nhiên, trong [15] các điều kiện phản ví dụ cho mỗi thuộc tính được sinh ra. Sau đó một bộ tìm mô hình (model finder) sinh ra một mô hình phản ví dụ khả dĩ, trước khi hệ thống xác định liệu mô hình đó có thể được thỏa mãn hay không. Xin lưu ý rằng do việc tìm kiếm không đầy đủ trong không gian mô hình, bộ tìm mô hình có thể không tìm thấy mọi phản ví dụ. Trái lại, hệ thống của chúng tôi hoạt động bằng cách khớp thuộc tính lên các điều kiện đường đi, thứ trừu tượng hóa tất cả các lần thực thi chuyển đổi khả dĩ. Do đó, công cụ chứng minh thuộc tính của chúng tôi có thể đưa ra một chứng minh mạnh mẽ hơn.

Trong [24] các tác giả kiểm tra các loại thuộc tính chuyển đổi mô hình khác nhau dựa trên OCL và việc sử dụng KodKod, một lần nữa đòi hỏi các cận (bounds) cụ thể cho việc chứng minh thuộc tính. Công trình của Anastasakis và cộng sự [7] dịch các chuyển đổi mô hình QVT sang Alloy để xác minh liệu các khẳng định (assertions) cho trước, nghĩa là, các thuộc tính, có được thỏa mãn cho các chuyển đổi cho trước hay không. Nếu không có mô hình đích nào được tìm thấy bởi Alloy cho một mô hình nguồn cho trước, khẳng định không được thỏa mãn. Vì Alloy cần các cận cho việc tìm kiếm mô hình, các mô hình nằm ngoài các cận cho trước không được tìm thấy. Sự hỗ trợ xác minh chuyển đổi mô hình tương tự dựa trên Alloy được trình bày trong [21], cũng cần các cận cụ thể để thực hiện việc tìm kiếm mô hình.

Bên cạnh các phương pháp xác minh có cận (bounded verification) đã đề cập, có một số phương pháp không có cận (unbounded) sử dụng các công cụ chứng minh định lý để xác minh các chuyển đổi mô hình. Ví dụ, Calegari và cộng sự [16] đề xuất một phương pháp tương tác để xác minh các hợp đồng cho các chuyển đổi ATL dựa trên trợ lý chứng minh Coq. Phương pháp này là không có cận, nhưng đòi hỏi một số hướng dẫn từ người dùng. Một phương pháp khác sử dụng trợ lý chứng minh Coq để đảm bảo tính đúng đắn của các chuyển đổi mô hình được trình bày trong [38]. Tuy nhiên, các tác giả nhắm đến việc tổng hợp (synthesize) các triển khai chuyển đổi từ các đặc tả đúng-theo-cấu-trúc (correct-by-construction) thay vì xác minh các chuyển đổi được phát triển độc lập.

Các phương pháp khác sử dụng công cụ chứng minh định lý để xác minh chuyển đổi mô hình đi xa hơn một bước bằng cách sử dụng các bộ giải SMT hiện đại như được thực hiện trong [14, 18]. Các phương pháp này không đòi hỏi hướng dẫn từ người dùng như đã được yêu cầu trong các phương pháp dựa trên Coq đã đề cập ở trên. Chúng dịch các chuyển đổi ATL cũng như các hợp đồng được biểu đạt trong OCL thành các biểu thức logic bậc nhất và sử dụng Z3 để thực hiện việc chứng minh định lý. So với phương pháp của chúng tôi, các phương pháp này cùng chung tinh thần, nhưng chúng xem xét một tập con nhỏ hơn của ATL so với giải pháp của chúng tôi. Ví dụ, hiện tại chúng không hỗ trợ các quy tắc lười.

Một công trình khác dịch các chuyển đổi ATL cho mục đích phân tích được trình bày trong [41]. Các tác giả lập luận rằng một biểu diễn chuyển đổi đồ thị đại số (algebraic graph transformation) sẽ cho phép các tác vụ xác minh được tăng cường. Tuy nhiên, các tác giả không đi sâu vào khía cạnh này vì họ chủ yếu tập trung vào việc dịch đúng đắn các khái niệm ngôn ngữ ATL sang các khái niệm Henshin. Do đó, họ coi việc khảo sát các tác vụ xác minh cụ thể là công việc tương lai.

Trong [30], các tác giả trình bày một siêu mô hình chuyển đổi tổng quát có thể được sử dụng làm ngôn ngữ trung gian để dịch các ngôn ngữ chuyển đổi mô hình sang biểu diễn này, trước khi các chuyển đổi được dịch vào một miền hình thức để thực hiện phân tích. Các tác giả trình bày một số trường hợp xác minh nơi khung làm việc được đề xuất giúp khai thác các hình thức luận và kỹ thuật xác minh khác nhau. Trong phương pháp của chúng tôi, chúng tôi cũng nhắm đến việc tái sử dụng một hình thức luận xác minh hiện có được cung cấp bởi DSLtrans và chỉ ra cách một tập con đáng kể của ATL có thể được dịch sang DSLtrans để thực hiện việc xác minh hợp đồng.

### 9.3 Tổng kết (Synopsis)

Theo hiểu biết tốt nhất của chúng tôi, trong bài báo này chúng tôi đã trình bày phương pháp duy nhất để chứng minh đầy đủ các thuộc tính được định nghĩa dưới dạng hợp đồng cho các chuyển đổi mô hình được biểu đạt trong ATL khai báo, bao gồm các đặc trưng nâng cao như các quy tắc lười.

## 10 Kết luận (Conclusion)

Mục này sẽ trình bày một cuộc thảo luận ngắn gọn về các mối đe dọa đối với tính hợp lệ, cũng như một số suy nghĩ kết luận về công cụ chứng minh hợp đồng và kỹ thuật của chúng tôi.

### 10.1 Các mối đe dọa đối với tính hợp lệ (Threats to Validity)

Tiểu mục này thảo luận về các mối đe dọa chính đối với tính hợp lệ của công trình của chúng tôi.

Chuyển đổi bậc cao chưa được xác minh một cách hình thức. Do đó, chúng tôi không thể hoàn toàn chắc chắn rằng các chuyển đổi DSLTrans được sinh ra tự động là tương đương trực tiếp với chuyển đổi ATL gốc. Tuy nhiên, có thể đưa ra hai lập luận cho tính đúng đắn của HOT. Thứ nhất là HOT tương đối đơn giản, như đã giải thích trong Mục 4. Nó bao gồm hai bước: trước tiên tạo ra các quy tắc sinh ra các phần tử đầu ra và sau đó tạo ra các quy tắc sinh ra các quan hệ giữa các phần tử đầu ra. Phương pháp hai bước này làm cho ngữ nghĩa của ATL trở nên tường minh, và làm cho các chuyển đổi DSLTrans được sinh ra bởi HOT dễ hiểu cũng như có thể truy vết ngược lại đặc tả ATL gốc của chúng.

Thứ hai, chúng tôi đã so sánh các kết quả chứng minh hợp đồng giữa hai chuyển đổi được tạo ra thủ công, và các chuyển đổi tương ứng được sinh ra bởi chuyển đổi bậc cao của chúng tôi trong Mục 8. Chúng tôi lưu ý rằng một chuyển đổi được sinh ra bởi HOT của chúng tôi hoàn toàn giống hệt (trừ việc sắp xếp lại quy tắc nhỏ) với phiên bản xây dựng thủ công. Ngoài ra, chuyển đổi kia đã được xác minh với thời gian chứng minh tương tự so với phiên bản xây dựng thủ công. Cho công việc tương lai, chúng tôi quan tâm đến việc xác minh chính bản thân chuyển đổi bậc cao bằng cách sử dụng công cụ chứng minh hợp đồng mà chúng tôi trình bày ở đây.

Khả năng mở rộng (scalability) luôn là một vấn đề khi các phương pháp toàn diện (exhaustive) như của chúng tôi được đề xuất. Chúng tôi đã chỉ ra qua các thí nghiệm của mình rằng HOT và công cụ chứng minh hợp đồng có thể chuyển đổi và xác minh các chuyển đổi có kích thước và độ phức tạp hợp lý. Ngoài ra, thuật toán cắt lát được trình bày có khả năng giảm đáng kể thời gian xác minh cho một chuyển đổi phức tạp. Tuy nhiên, cần có nhiều thí nghiệm hơn với các chuyển đổi lớn và các hợp đồng liên quan đến nhiều phần tử để xác nhận các kết quả tích cực của chúng tôi về khả năng sử dụng và khả năng mở rộng của kỹ thuật này.

Vì DSLTrans là một ngôn ngữ tính toán không đầy đủ Turing, nó có tính biểu đạt hạn chế. Điều này có nghĩa là các chuyển đổi ATL sử dụng chế độ tinh chỉnh (refining mode) để hiện thực hóa các chuyển đổi tại chỗ (in-place) hoặc các cấu trúc mệnh lệnh nói chung không thể được dịch sang DSLTrans để được xác minh bằng phương pháp của chúng tôi. Tuy nhiên, kỹ thuật của chúng tôi có thể được sử dụng để xác minh tập con khai báo của ATL trong các chuyển đổi ngoài chỗ sử dụng chế độ mặc định, được sử dụng trong nhiều chuyển đổi hơn nhiều so với chế độ tinh chỉnh. Do đó chúng tôi tự tin rằng kỹ thuật của chúng tôi có thể sử dụng được cho một lớp lớn các bài toán trong thế giới thực.

Cuối cùng, chỉ có kiểu String là có sẵn trong SyVOLT: hạn chế này ngụ ý rằng các chứng minh trong SyVOLT chỉ có thể được xây dựng cho các chuyển đổi mô hình thao tác các thuộc tính thuộc kiểu String. Xin lưu ý rằng đây không phải là hạn chế của chính công cụ chứng minh SyVOLT, mà là hạn chế của tính biểu đạt của ngôn ngữ DSLTrans. Hạn chế này có thể được khắc phục bằng nhiều cách khác nhau, có lẽ bằng cách chuyển đổi các thuộc tính và thao tác không phải String thành String trước khi chuyển đổi và thực hiện thao tác ngược lại sau khi chuyển đổi kết thúc.

### 10.2 Kết luận (Conclusion)

Trong bài báo này, chúng tôi đã mở rộng kỹ thuật mới lạ của mình từ [36] để chứng minh đầy đủ các hợp đồng tiền điều kiện/hậu điều kiện trên các chuyển đổi ATL khai báo. Phương pháp này tập trung xoay quanh việc chuyển đổi các chuyển đổi ATL thành DSLTrans, ngôn ngữ chuyển đổi có tính biểu đạt giảm bớt của chúng tôi. Bộ sinh điều kiện đường đi của chúng tôi sau đó có thể sinh ra một tập hợp các điều kiện đường đi, đại diện cho tất cả các lần thực thi chuyển đổi khả dĩ. Các hợp đồng được chứng minh là được thỏa mãn hoặc không được thỏa mãn trên mỗi điều kiện đường đi, và do đó trên tất cả các lần thực thi chuyển đổi.

Bài báo này cũng đã trình bày một số nghiên cứu tình huống được thiết kế để trả lời bốn câu hỏi nghiên cứu của chúng tôi. Kết quả chỉ ra rằng công cụ chứng minh hợp đồng của chúng tôi áp dụng được cho các chuyển đổi ATL có kích thước và độ phức tạp hợp lý, và các hợp đồng có thể được chứng minh trong một khoảng thời gian và bộ nhớ khả thi. Ngoài ra, chúng tôi cũng đã trình bày chi tiết hơn kỹ thuật "cắt lát" của mình, chỉ chọn ra những quy tắc cần thiết để chứng minh một hợp đồng cụ thể. Điều này dẫn đến sự giảm thiểu đáng kể trong thời gian chứng minh hợp đồng. Cuối cùng, chúng tôi xác định rằng HOT của chúng tôi sinh ra các chuyển đổi phù hợp để thay thế các chuyển đổi xây dựng thủ công trong việc chứng minh hợp đồng.

### 10.3 Công việc tương lai (Future Work)

Công việc tương lai của chúng tôi sẽ cố gắng giải quyết bất kỳ hạn chế nào của công trình này. Cụ thể, chúng tôi hướng tới việc tạo ra một công cụ có thể được sử dụng ngay (off-the-shelf) để chứng minh các thuộc tính về một lớp các chuyển đổi ATL hiện có, một cách hoàn toàn tự động, bằng cách sử dụng ngôn ngữ DSLTrans như một back-end ẩn (hidden back-end). Trọng tâm hiện tại của chúng tôi là tích hợp chuyển đổi bậc cao của chúng tôi vào công cụ SyVOLT [5].

Một mối quan tâm liên tục khác của chúng tôi là các yêu cầu về thời gian và không gian để chứng minh hợp đồng trên các chuyển đổi lớn. Chúng tôi đang khảo sát các cải tiến tốc độ triển khai, chẳng hạn như tối ưu hóa thêm thuật toán khớp của chúng tôi và tinh chỉnh bộ cắt lát chuyển đổi.

## Lời cảm ơn (Acknowledgments)

Các tác giả xin chân thành cảm ơn Gehan Selim và Cláudio Gomes vì những đóng góp của họ cho việc triển khai công cụ chứng minh hợp đồng.

Bentley James Oakes được tài trợ bởi một khoản trợ cấp NSERC, cũng như sự hỗ trợ từ dự án NECSIS, được tài trợ bởi Automotive Partnership Canada.

Công trình của Javier Troya được tài trợ bởi Ủy ban châu Âu (FEDER) và các chương trình R&D&I của Tây Ban Nha và Andalucía theo các khoản tài trợ và dự án BELI (TIN2015-70560-R), THEOS (P10-TIC-5906) và COPAS (P12-TIC-1867).

Cuối cùng, công trình của Manuel Wimmer được tài trợ bởi Christian Doppler Forschungsgesellschaft và BMWFW, Áo.

## Tài liệu tham khảo (References)

1. A Short Introduction to SyVOLT. https://www.youtube.com/watch?v=8PrR5RhPptY
2. ATL Zoo. http://www.eclipse.org/atl/atlTransformations
3. ATL2DSLTrans Artifacts. http://msdl.cs.mcgill.ca/people/levi/files/MODELS2015_SoSyM
4. Atlas Transformation Language – ATL. http://eclipse.org/atl
5. SyVOLT tool. http://msdl.cs.mcgill.ca/people/levi/contractprover
6. Amrani, M., Lúcio, L., Selim, G.M.K., Combemale, B., Dingel, J., Vangheluwe, H., Traon, Y.L., Cordy, J.R.: A Tridimensional Approach for Studying the Formal Verification of Model Transformations. In: Proc. of ICSTW, pp. 921–928 (2012)
7. Anastasakis, K., Bordbar, B., Küster, J.M.: Analysis of Model Transformations via Alloy. In: Proc. of MoDeVVa (2007)
8. Arendt, T., Habel, A., Radke, H., Taentzer, G.: From Core OCL Invariants to Nested Graph Constraints. In: Proc. ICGT, pp. 97–112 (2014). DOI 10.1007/978-3-319-09108-2 7
9. Balogh, A., et al.: Workflow-Driven Tool Integration Using Model Transformations. In: Graph Transformations and Model-Driven Engineering, pp. 224–248 (2010)
10. Barroca, B., Lúcio, L., Amaral, V., Félix, R., Sousa, V.: DSLTrans: A Turing Incomplete Transformation Language. In: Proc. of SLE, pp. 296–305 (2011)
11. Bergmann, G.: Translating OCL to Graph Patterns. In: Proc. of MoDELS, pp. 670–686 (2014). DOI 10.1007/978-3-319-11653-2 41
12. Brambilla, M., Cabot, J., Wimmer, M.: Model-Driven Software Engineering in Practice. Morgan & Claypool Publishers (2012)
13. Burgueno, L., Troya, J., Wimmer, M., Vallecillo, A.: Static Fault Localization in Model Transformations. IEEE Transactions on Software Engineering 41(5), 490–506 (2015)
14. Büttner, F., Egea, M., Cabot, J.: On Verifying ATL Transformations Using 'off-the-shelf' SMT Solvers. In: Proc. of MoDELS, pp. 432–448 (2012). DOI 10.1007/978-3-642-33666-9 28
15. Büttner, F., Egea, M., Guerra, E., De Lara, J.: Checking Model Transformation Refinement. In: Proc. of ICMT, pp. 158–173 (2013)
16. Calegari, D., Luna, C., Szasz, N., Tasistro, A.: A Type-Theoretic Framework for Certified Model Transformations. In: Proc. of SBMF, pp. 112–127 (2010). DOI 10.1007/978-3-642-19829-8 8
17. Cariou, E., Belloir, N., Barbier, F., Djemam, N.: OCL Contracts for the Verification of Model Transformations. ECEASST 24 (2009)
18. Cheng, Z., Monahan, R., Power, J.F.: A Sound Execution Semantics for ATL via Translation Validation. In: Proc. of ICMT, pp. 133–148 (2015). DOI 10.1007/978-3-319-21155-8 11
19. Clavel, M., Durán, F., Eker, S., Lincoln, P., Martí-Oliet, N., Meseguer, J., Talcott, C.: All About Maude - a High-performance Logical Framework: How to Specify, Program and Verify Systems in Rewriting Logic. Springer (2007)
20. Cuadrado, J.S., Guerra, E., de Lara, J.: Uncovering Errors in ATL Model Transformations Using Static Analysis and Constraint Solving. In: Proc. of ISSRE, pp. 34–44 (2014). DOI 10.1109/ISSRE.2014.10
21. Gammaitoni, L., Kelsen, P.: F-Alloy: An Alloy Based Model Transformation Language. In: Proc. of ICMT, pp. 166–180 (2015). DOI 10.1007/978-3-319-21155-8 13
22. García-Domínguez, A., Kolovos, D.S., Rose, L.M., Paige, R.F., Medina-Bulo, I.: EUnit: A Unit Testing Framework for Model Management Tasks. In: Proc. of MoDELS, pp. 395–409 (2011)
23. Giner, P., Pelechano, V.: Test-Driven Development of Model Transformations. In: Proc. of MoDELS, pp. 748–752 (2009)
24. Gogolla, M., Hamann, L., Hilken, F.: Checking Transformation Model Properties with a UML and OCL Model Validator. In: Proc. of VOLT, pp. 16–25 (2014)
25. Gogolla, M., Vallecillo, A.: Tractable Model Transformation Testing. In: Proc. of ECMFA, pp. 221–235 (2011)
26. González, C.A., Cabot, J.: ATLTest: A White-Box Test Generation Approach for ATL Transformations. In: Proc. of MoDELS, pp. 449–464 (2012)
27. Guerra, E., de Lara, J., Wimmer, M., Kappel, G., Kusel, A., Retschitzegger, W., Schönböck, J., Schwinger, W.: Automated Verification of Model Transformations Based on Visual Contracts. Automated Software Engineering 20(1), 5–46 (2013)
28. Jouault, F., Allilaire, F., Bézivin, J., Kurtev, I.: ATL: A Model Transformation Tool. Sci. Comput. Program. 72(1-2), 31–39 (2008)
29. Kolovos, D.S., Paige, R.F., Polack, F.A.: Model Comparison: A Foundation for Model Composition and Model Transformation Testing. In: Proc. of GaMMa, pp. 13–20 (2006)
30. Lano, K., Clark, T., Rahimi, S.K.: A Framework for Model Transformation Verification. Formal Asp. Comput. 27(1), 193–235 (2015). DOI 10.1007/s00165-014-0313-z
31. Lúcio, L., Barroca, B., Amaral, V.: A Technique for Automatic Validation of Model Transformations. In: Proc. of MoDELS, pp. 136–150 (2010)
32. Lúcio, L., Oakes, B., Vangheluwe, H.: A Technique for Symbolically Verifying Properties of Graph-Based Model Transformations. Tech. rep., Technical Report SOCS-TR-2014.1, McGill University (2014)
33. Lúcio, L., Oakes, B.J., Gomes, C., Selim, G.M., Dingel, J., Cordy, J.R., Vangheluwe, H.: SyVOLT: Full Model Transformation Verification Using Contracts. In: Proc. of MoDELS 2015 Demo and Poster Session (2015)
34. Lúcio, Levi and Amrani, Moussa and Dingel, Jürgen and Lambers, Leen and Salay, Rick and Selim, Gehan and Syriani, Eugene and Wimmer, Manuel: Model Transformation Intents and their Properties. Software & Systems Modeling pp. 1–38 (2014). DOI 10.1007/s10270-014-0429-x
35. Mottu, J.M., Baudry, B., Traon, Y.L.: Model Transformation Testing: Oracle Issue. In: Proc. of ICSTW, pp. 105–112 (2008)
36. Oakes, B.J., Troya, J., Lúcio, L., Wimmer, M.: Fully Verifying Transformation Contracts for Declarative ATL. In: Proc. of MoDELS, pp. 256–265 (2015)
37. Paen, E.: Measuring Incrementally Developed Model Transformations Using Change Metrics. Master's thesis, Queen's University (2012)
38. Poernomo, I., Terrell, J.: Correct-by-Construction Model Transformations from Partially Ordered Specifications in Coq. In: Proc. of ICFEM, pp. 56–73 (2010). DOI 10.1007/978-3-642-16901-4 6
39. Posse, E., Dingel, J.: An Executable Formal Semantics for UML-RT. Software & Systems Modeling 15(1), 179–217 (2016). DOI 10.1007/s10270-014-0399-z
40. Rahim, L., Whittle, J.: A Survey of Approaches for Verifying Model Transformations. Software & Systems Modeling 14(2), 1003–1028 (2015). DOI 10.1007/s10270-013-0358-0
41. Richa, E., Borde, E., Pautet, L.: Translating ATL Model Transformations to Algebraic Graph Transformations. In: Proc. of ICMT, pp. 183–198 (2015). DOI 10.1007/978-3-319-21155-8 14
42. Selim, G.M.: Formal Verification of Graph-Based Model Transformations. Ph.D. thesis, Queen's University (2015)
43. Selim, G.M., Cordy, J.R., Dingel, J., Lúcio, L., Oakes, B.J.: Finding and Fixing Bugs in Model Transformations with Formal Verification: An Experience Report. In: Proc. of AMT, pp. 26–35 (2015)
44. Selim, G.M., Lúcio, L., Cordy, J.R., Dingel, J., Oakes, B.J.: Specification and Verification of Graph-Based Model Transformation Properties. In: Proc. of ICGT, pp. 113–129 (2014)
45. Syriani, E., Vangheluwe, H., LaShomb, B.: T-Core: a framework for custom-built model transformation engines. Software & Systems Modeling 14(3), 1215–1243 (2015). DOI 10.1007/s10270-013-0370-4
46. Tisi, M., Martínez, S., Jouault, F., Cabot, J.: Refining Models with Rule-based Model Transformations. Research Report RR-7582, INRIA (2011)
47. Troya, J., Vallecillo, A.: A Rewriting Logic Semantics for ATL. Journal of Object Technology 10(5), 1–29 (2011). DOI 10.5381/jot.2011.10.1.a5
48. Vallecillo, A., Gogolla, M., Burgueno, L., Wimmer, M., Hamann, L.: Formal Specification and Testing of Model Transformations. In: Formal Methods for Model-Driven Engineering, pp. 399–437 (2012)
49. Wieber, M., Anjorin, A., Schürr, A.: On the Usage of TGGs for Automated Model Transformation Testing. In: Proc. of ICMT, pp. 1–16 (2014)

## Tiểu sử tác giả (Author Biographies)

**Bentley James Oakes** là nghiên cứu sinh tiến sĩ (PhD candidate) tại Phòng thí nghiệm Mô hình hóa, Mô phỏng và Thiết kế (Modelling, Simulation, and Design Lab) tại Đại học McGill, Canada. Đề tài tiến sĩ của anh là về việc xác minh các chuyển đổi mô hình trong nhiều lĩnh vực khác nhau bằng cách sử dụng các khung làm việc và công cụ SyVOLT. Các mối quan tâm nghiên cứu khác bao gồm sơ đồ khối nhân quả (causal-block diagrams), các vấn đề về sở hữu trí tuệ trong các mô hình, và trí tuệ nhân tạo. Thông tin thêm về nghiên cứu của anh có thể được tìm thấy tại http://msdl.cs.mcgill.ca/people/bentley/.

**Javier Troya** nhận bằng tiến sĩ năm 2013 từ Đại học Malaga, Tây Ban Nha. Anh hiện là nghiên cứu viên sau tiến sĩ (postdoctoral researcher) tại Khoa Khoa học Máy tính và Ngôn ngữ tại Đại học Seville, Tây Ban Nha. Trước đó, anh đã là nghiên cứu viên sau tiến sĩ tại Nhóm Tin học Kinh doanh (Business Informatics Group — BIG) tại Đại học Công nghệ Vienna trong hơn hai năm. Mối quan tâm nghiên cứu của anh bao gồm mô hình hóa và siêu mô hình hóa, chuyển đổi mô hình, phân tích thuộc tính phi chức năng và kiểm thử biến hình (metamorphic testing). Để biết thêm thông tin, vui lòng truy cập http://www.lsi.us.es/~jtroya.

**Levi Lúcio** hiện là nghiên cứu viên chính thức (staff researcher) và Quản lý dự án (Project Manager) tại fortiss GmbH, Đức. Anh nhận bằng tiến sĩ từ Đại học Geneva, Thụy Sĩ, năm 2008. Nghiên cứu của anh về việc kết nối kỹ nghệ phần mềm và các kỹ thuật hình thức. Một số lĩnh vực quan tâm cụ thể của anh là phát triển hướng mô hình, các ngôn ngữ chuyển đổi mô hình, việc xác minh các chuyển đổi mô hình, tính đúng-theo-cấu-trúc (correctness-by-construction), các mô hình đồng thời (models of concurrency) (đặc biệt là Lưới Petri đại số — Algebraic Petri Nets), tiến hóa mô hình, kiểm thử dựa trên mô hình và xây dựng công cụ. Levi hiện đang phát triển và dẫn dắt các dự án cùng với các công ty hàng không và ô tô để tạo ra các IDE dựa trên các khung làm việc tích hợp liền mạch một loạt các ngôn ngữ đặc thù miền. Các khung làm việc như vậy nhắm đến việc cung cấp đúng ngôn ngữ cho đúng tác vụ mô hình hóa, trong khi cung cấp các dịch vụ xác minh, tinh chỉnh và khả năng truy vết. Một trong những mục tiêu chính của các khung làm việc như vậy là cải thiện các phương tiện sẵn có để chứng nhận (certification) phần mềm quan trọng về an toàn (safety-critical software) bởi các cơ quan có thẩm quyền liên quan.

**Manuel Wimmer** là nghiên cứu viên sau tiến sĩ tại Nhóm Tin học Kinh doanh của TU Wien. Mối quan tâm nghiên cứu của anh bao gồm các nền tảng của kỹ thuật kỹ nghệ mô hình cũng như ứng dụng của chúng trong các lĩnh vực như khả năng tương tác công cụ, hiện đại hóa công cụ mô hình hóa cũ, quản lý phiên bản và tiến hóa mô hình, kỹ thuật đảo ngược và di trú phần mềm, kỹ nghệ web, điện toán đám mây, và sản xuất thông minh. Để biết thêm thông tin về các hoạt động nghiên cứu của anh, vui lòng truy cập http://big.tuwien.ac.at/staff/mwimmer.

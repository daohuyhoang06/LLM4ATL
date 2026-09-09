# gogollaKiểm chứng các phép biến đổi ATL bằng Mô hình biến đổi và Bộ tìm mô hình — Verification of ATL Transformations Using Transformation Models and Model Finders

**Tác giả:** Fabian Büttner, Marina Egea, Jordi Cabot, Martin Gogolla **Năm:** 2012 **Nguồn:** NotebookLM notebook "model tranformation verification" **Loại tài liệu:** Bản dịch sát nghĩa (đầy đủ, không tóm tắt) — do AI dịch, kèm chú thích giải nghĩa cho đoạn khó.

---

tôiFabian Büttner¹, Marina Egea², Jordi Cabot¹, Martin Gogolla³

¹ Nhóm nghiên cứu AtlanMod, INRIA / Ecole des Mines de Nantes ² Bộ phận Nghiên cứu & Đổi mới Atos, Madrid ³ Nhóm Hệ thống Cơ sở dữ liệu, Đại học Bremen

fabian.buettner@inria.fr, marina.egea@atosresearch.eu, jordi.cabot@inria.fr, gogolla@tzi.de

## Tóm tắt (Abstract)

Trong kỹ nghệ phần mềm hướng mô hình (model-driven engineering), các mô hình là những thành phần then chốt của phần mềm cần được xây dựng. Nếu các mô hình được đặc tả tốt, các phép biến đổi (transformation) có thể được sử dụng cho nhiều mục đích khác nhau, ví dụ như để sinh ra mã nguồn cuối cùng. Tuy nhiên, điều quan trọng là các mô hình được sinh ra bởi một phép biến đổi từ các mô hình đầu vào hợp lệ cũng phải hợp lệ, trong đó tính hợp lệ được hiểu là tuân thủ các ràng buộc của siêu mô hình (metamodel), thường được viết bằng OCL. Mô hình biến đổi (transformation model) là một cách để mô tả khái niệm đúng đắn từng phần (partial correctness) theo kiểu Hoare của các phép biến đổi mô hình, chỉ sử dụng các siêu mô hình và ràng buộc. Trong bài báo này, chúng tôi cung cấp một phép dịch tự động từ các phép biến đổi ATL khai báo, dựa trên luật (declarative, rule-based), sang các mô hình biến đổi như vậy, cung cấp một cách mã hóa trực quan và linh hoạt của ATL sang OCL, có thể được dùng để phân tích nhiều tính chất khác nhau của các phép biến đổi. Chúng tôi còn chỉ ra cách các bộ kiểm chứng mô hình (bộ kiểm tra tính thỏa mãn được — satisfiability checker) hiện có cho các siêu mô hình được chú thích bằng OCL có thể được áp dụng để kiểm chứng các phép biến đổi ATL đã được dịch, qua đó cung cấp bằng chứng thực nghiệm cho tính hiệu quả của cách tiếp cận của chúng tôi trong thực tế.

> **Giải thích:** "Hoare-style partial correctness" (đúng đắn từng phần theo kiểu Hoare) là một khái niệm trong lý thuyết kiểm chứng chương trình, xuất phát từ logic Hoare. Nó phát biểu dưới dạng: "Nếu điều kiện đầu vào (tiền điều kiện) đúng, và chương trình kết thúc, thì điều kiện đầu ra (hậu điều kiện) cũng đúng." Gọi là "từng phần" (partial) vì nó không đảm bảo chương trình sẽ luôn kết thúc (terminate) — nó chỉ đảm bảo rằng NẾU chương trình kết thúc thì kết quả là đúng. Áp dụng vào bài báo này: nếu mô hình đầu vào hợp lệ (thỏa các ràng buộc OCL của metamodel đầu vào) và phép biến đổi ATL chạy xong, thì mô hình đầu ra cũng phải hợp lệ (thỏa các ràng buộc OCL của metamodel đầu ra).

**Từ khóa:** Biến đổi mô hình, Kiểm chứng, ATL, OCL

## 1 Giới thiệu (Introduction)

Trong kỹ nghệ phần mềm hướng mô hình (MDE), các mô hình là những thành phần then chốt của phần mềm cần được xây dựng. Về mặt lý tưởng, nếu các mô hình này được đặc tả đủ tốt, các phép biến đổi mô hình có thể được sử dụng cho nhiều mục đích khác nhau, ví dụ, chúng có thể được dùng để cuối cùng sinh ra mã nguồn. Sự phổ biến ngày càng tăng của MDE đã dẫn đến độ phức tạp ngày càng lớn của cả mô hình lẫn phép biến đổi, và điều thiết yếu là các phép biến đổi phải đúng đắn nếu chúng muốn đóng vai trò then chốt của mình. Nếu không, các lỗi do phép biến đổi đưa vào sẽ được lan truyền và có thể sinh ra thêm nhiều lỗi khác ở các bước tiếp theo của MDE.

Công trình của chúng tôi tập trung vào việc kiểm tra tính đúng đắn từng phần (partial correctness) của các phép biến đổi khai báo, dựa trên luật, giữa các siêu mô hình có ràng buộc. Cụ thể hơn, chúng tôi xem xét ngôn ngữ biến đổi ATL \[16\] và các siêu mô hình theo phong cách MOF \[22\] (ví dụ: EMF \[27\], KM3 \[17\]) có sử dụng các ràng buộc OCL \[21,29\] để mô tả chính xác miền của chúng.

> Nghiên cứu này được tài trợ một phần bởi chương trình Nouvelles Équipes của vùng Pays de la Loire (Pháp).

Những thành phần này phổ biến do có sự hỗ trợ công cụ tinh vi (đặc biệt trên nền tảng Eclipse) và vì OCL được sử dụng trong hầu hết các đặc tả của OMG. Các phép biến đổi mô hình có thể được xem như các chương trình hoạt động trên các thực thể (instance) của siêu mô hình. Theo nghĩa này, chúng ta cũng có thể áp dụng khái niệm đúng đắn cổ điển (classical notion of correctness) cho các phép biến đổi mô hình. Trong bài báo này, chúng tôi quan tâm đến khái niệm đúng đắn từng phần theo kiểu Hoare, tức là tính đúng đắn của một phép biến đổi đối với các ràng buộc của các siêu mô hình liên quan. Nói cách khác, chúng tôi quan tâm đến việc liệu mô hình đầu ra được sinh ra bởi một phép biến đổi ATL có hợp lệ hay không, đối với bất kỳ mô hình đầu vào hợp lệ nào.

Trong bài báo này, chúng tôi trình bày một cách tiếp cận kiểm chứng dựa trên các mô hình biến đổi (transformation models). Mô hình biến đổi là một dạng cụ thể của cái thường được gọi là "mô hình vết" (trace model). Cho một phép biến đổi ATL T : MI → MF từ một siêu mô hình đầu vào MI đến một siêu mô hình đầu ra⁴ MF, một mô hình biến đổi MT là một siêu mô hình bao gồm cả MI và MF, cùng với các phần tử mô hình hóa cấu trúc bổ sung và các ràng buộc nhằm nắm bắt ngữ nghĩa thực thi (execution semantics) của T. Theo quan điểm của chúng tôi, cách tiếp cận này mang lại lợi thế vì nó quy giản bài toán kiểm chứng các phép biến đổi dựa trên luật giữa các siêu mô hình có ràng buộc thành bài toán kiểm chứng các siêu mô hình có ràng buộc mà thôi. Theo cách này, về mặt kiểm chứng tự động, chúng ta có thể tái sử dụng các cài đặt và công trình sẵn có cho việc kiểm chứng mô hình, hưởng lợi từ những kết quả mà một cộng đồng rộng lớn đã đạt được trong hơn một thập kỷ.

> **Giải thích:** Ý tưởng cốt lõi của bài báo là: thay vì phải xây dựng một công cụ kiểm chứng riêng cho ngôn ngữ biến đổi ATL (vốn có ngữ nghĩa thực thi phức tạp, mang tính thủ tục), nhóm tác giả "dịch" cả phép biến đổi ATL lẫn hai siêu mô hình đầu vào/đầu ra thành MỘT siêu mô hình duy nhất (transformation model MT) chỉ gồm các lớp, quan hệ và ràng buộc OCL (không còn "hành vi" hay "lệnh" nào cả — thuần túy là mô tả cấu trúc + ràng buộc). Khi đó, việc kiểm tra "phép biến đổi T có đúng không" được quy về việc kiểm tra "siêu mô hình MT có instance nào vi phạm ràng buộc mong muốn hay không" — một bài toán mà các công cụ kiểm chứng OCL/metamodel đã có sẵn (như UML2Alloy) có thể giải quyết ngay, không cần viết công cụ mới.

Phương pháp luận mô hình biến đổi lần đầu tiên được trình bày trong \[12\] và \[7\]. Chúng tôi đã cung cấp một phác thảo đầu tiên về cách áp dụng phương pháp luận này cho ATL trong \[5\]. Trong bài báo này, chúng tôi trình bày một mô tả chính xác về cách tự động sinh ra các mô hình biến đổi từ các phép biến đổi ATL khai báo. Hơn nữa, chúng tôi chỉ ra cách các bộ tìm mô hình (model finder) hiện có cho các siêu mô hình được chú thích OCL có thể được sử dụng "sẵn có" (off-the-shelf) trong việc kiểm chứng thực tế. Chúng tôi sử dụng một phép biến đổi ER-to-Relational (ER2REL) để minh họa cách tiếp cận của mình, vì ví dụ này khá nổi tiếng và "đậm đặc" về mặt khái niệm (nó chỉ chứa một vài lớp nhưng tương đối nhiều ràng buộc). Chúng tôi chỉ ra cách mô hình biến đổi được suy ra bằng thuật toán của mình và cách nó có thể được sử dụng để kiểm chứng hiệu quả phép biến đổi ATL bằng cách sử dụng UML2Alloy \[1\] và Alloy như một công cụ kiểm chứng mô hình có giới hạn (bounded model verification) (mà bản thân Alloy lại dựa trên SAT). Lưu ý rằng, tuy nhiên, phương pháp luận này độc lập với một kỹ thuật kiểm chứng cụ thể nào.

**Tổ chức bài báo.** Mục 2 mô tả ví dụ minh họa xuyên suốt ER2REL. Mục 3 trình bày cách suy ra các mô hình biến đổi cho ATL. Trong Mục 4, chúng tôi trình bày cách UML2Alloy có thể được sử dụng để kiểm chứng ER2REL (dựa trên mô hình biến đổi đã suy ra). Mục 5 đặt đóng góp của chúng tôi trong bối cảnh các công trình liên quan. Chúng tôi kết luận trong Mục 6.

## 2 Ví dụ minh họa xuyên suốt (Running Example)

Chúng tôi đã chọn một phép biến đổi ATL (ER2REL) từ một mô hình dữ liệu Thực thể-Liên kết (Entity-Relationship, ER) đơn giản sang một mô hình dữ liệu quan hệ (relational, REL) đơn giản làm ví dụ minh họa xuyên suốt cho bài báo của mình, vì hai lý do. Thứ nhất, miền này khá nổi tiếng (các kết quả có thể được kiểm chứng dễ dàng). Thứ hai, hầu hết mọi phần tử đều bị ràng buộc bởi một hoặc nhiều bất biến (invariant), bao gồm một số lượng tử phổ dụng (universal quantifier). Điều này khiến việc kiểm chứng phép biến đổi này trở nên khá khó.

> ⁴ Vì lý do ký hiệu học (typographical reasons), chúng tôi sử dụng F (nghĩ đến: "final" — cuối cùng), trong MF, để chỉ đầu ra.

**Hình 1. Các siêu mô hình ER và REL**

*(Sơ đồ lớp mô tả siêu mô hình ER gồm: ERSchema chứa các elements (SchemaElement) là Entity và Relship (quan hệ, viết tắt của Relationship); mỗi Entity/Relship có các attrs (ERAttribute) với name và isKey; Relship có các ends (RelshipEnd) liên kết tới các Entity qua {xor}. Sơ đồ lớp REL gồm: RELSchema chứa relations (Relation), mỗi Relation có attrs (RELAttribute) với name và isKey.)*

```
context ERSchema inv ER_EN: -- tên các phần tử là duy nhất trong schema
  self.elements->forAll(e1,e2 | e1.name=e2.name implies e1=e2)
context Entity inv ER_EAN: -- tên thuộc tính là duy nhất trong entity
  self.attrs->forAll(a1,a2 | a1.name=a2.name implies a1=a2)
context Relship inv ER_RAN: -- tên thuộc tính là duy nhất trong relship
  self.attrs->forAll(a1,a2 | a1.name = a2.name implies a1=a2)
context Entity inv ER_EK: -- entities có một khóa (key)
  self.attrs->exists(a | a.isKey)
context Relship inv ER_RK: -- relships không có khóa
  not attrs->exists(a1 | a1.isKey)
-- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
context RELSchema inv REL_RN: -- tên các relation là duy nhất trong schema
  relations->forall(r1,r2| r1.name=r2.name implies r1=r2)
context Relation inv REL_AN: -- tên thuộc tính là duy nhất trong relation
  self.attrs->forAll(a1,a2 | a1.name=a2.name implies a1=a2)
context Relation inv REL_K: -- relations có một khóa
  self.attrs->exists(a | a.isKey)
context RELSchema inv REL_mult1: self.relations->size() > 0 -- bội số 1..*
context Relation inv REL_mult2: self.schema.isDefined() -- bội số 1..1
context Relation inv REL_mult3: self.relations->size() > 0 -- bội số 1..*
context RELAttribute inv REL_mult4: self.relation.isDefined() -- bội số 1..1
```

**Hình 2. Các ràng buộc OCL cho ER và REL**

Hình 1 mô tả các siêu mô hình ER và REL⁵. Hình 2 cho thấy các ràng buộc OCL tương ứng. Các ràng buộc này đúng như mong đợi: tên phải là duy nhất trong phạm vi tương ứng của chúng, các entity và relation phải có một khóa, các mối liên kết (relationship) không được có khóa. Lưu ý rằng chúng tôi đã mã hóa các ràng buộc về bội số (multiplicity) cho REL thành các ràng buộc OCL tường minh (REL_mult). Chúng tôi chỉ để lại các bội số không hạn chế là 0..1 (đối với các điều hướng có kiểu đối tượng) và 0..∗ (đối với các điều hướng có kiểu tập hợp) trong sơ đồ lớp, vì chúng tôi muốn kiểm chứng tính hợp lệ của ER2REL đối với các bội số này sau, và cần có tên cho các ràng buộc này.

> ⁵ Lưu ý rằng chúng tôi chỉ đơn giản gọi các phần tử của một schema cơ sở dữ liệu ER là các entity (thực thể), relationship (mối liên kết), và relation (quan hệ) thay vì entity type, relationship type, và relation type.

Phép biến đổi ATL mà chúng tôi trình bày trong Hình 3 chỉ chứa các matched rule (luật khớp mẫu), đây là các cấu trúc chính của ATL. Một matched rule bao gồm một mẫu nguồn (source pattern) và một mẫu đích (target pattern). Mẫu nguồn xác định một tập các đối tượng của siêu mô hình nguồn và, tùy chọn, sử dụng một biểu thức OCL làm điều kiện lọc. Mẫu đích xác định một tập các đối tượng của siêu mô hình đích cùng với một tập các phép gán (binding). Các phép gán mô tả việc gán giá trị cho các đặc trưng (feature) (tức là thuộc tính, tham chiếu, và đầu liên kết) của các đối tượng đích. Ngữ nghĩa thực thi của các matched rule có thể được mô tả qua ba bước: Đầu tiên, các mẫu nguồn của tất cả các luật được khớp (match) với các phần tử của mô hình đầu vào. Thứ hai, đối với mỗi mẫu nguồn được khớp, mẫu đích được thực hiện để tạo ra các đối tượng trong mô hình đích. Việc thực thi một phép biến đổi ATL luôn bắt đầu với một mô hình đích rỗng. Ở bước thứ ba, các phép gán của mẫu đích được thực thi. Các phép gán này được thực hiện một cách trực tiếp, với một ngoại lệ duy nhất: một chiến lược giải quyết ngầm định (implicit resolution strategy) được áp dụng như sau, khi gán một giá trị cho một thuộc tính của một đối tượng của mô hình đầu ra (tức là, cho một đối tượng được tạo ra bởi một trong các luật). Nếu giá trị tham chiếu đến một giá trị đối tượng của mô hình nguồn, và đối tượng này đã được khớp bởi một matched rule, thì giá trị đối tượng của phần tử mẫu đích đầu tiên của luật đó sẽ được gán thay thế. Theo mặc định, bộ máy thực thi ATL sẽ báo lỗi nếu không có, hoặc có nhiều hơn một, khớp như vậy tồn tại.

> **Giải thích:** Đây là phần then chốt để hiểu toàn bộ bài báo — cơ chế "resolve" (giải quyết tham chiếu ngầm định) của ATL. Ý tưởng là: khi luật biến đổi gán `relation <- rs` (trong đó `rs` là một đối tượng bên mô hình NGUỒN, ví dụ một Relship), ATL không gán trực tiếp đối tượng `rs` đó (vì nó thuộc kiểu khác, ở phía mô hình nguồn), mà tự động "tra cứu" xem đối tượng `rs` này đã được luật nào khác biến đổi ("khớp") thành đối tượng đích tương ứng chưa (ví dụ luật R2R đã biến `rs` thành một `Relation` mới), rồi gán đối tượng ĐÍCH đó (Relation) vào thuộc tính `relation`. Đây chính là cách ATL cho phép người viết luật "tham chiếu chéo" sang các đối tượng do luật khác sinh ra mà không cần tự tay tra bảng ánh xạ. Nếu có nhiều luật cùng có thể khớp với `rs`, ATL sẽ báo lỗi vì không biết chọn luật nào.

```
module ER2REL;
create OUT : REL from IN : ER;

rule S2S {
  from s : ER!ERSchema
  to t : REL!RELSchema (
    relations <- s.entities->union(s.relships)
  )
}

rule E2R {
  from s : ER!Entity
  to t : REL!Relation (name<-s.name, schema<-s.schema)
}

rule R2R {
  from s : ER!Relship
  to t : REL!Relation (name <-s.name, schema<-s.schema)
}

rule EA2A {
  from att : ER!ERAttribute, ent : ER!Entity (att.entity=ent)
  to t : REL!RELAttribute (name<-att.name, isKey<-att.isKey, relation<-ent)
}

rule RA2A {
  from att : ER!ERAttribute, rs : ER!Relship (att.relship=rs)
  to t : REL!RELAttribute (name<-att.name, isKey<-att.isKey, relation<-rs)
}

rule RA2AK {
  from att : ER!ERAttribute,
       rse : ER!RelshipEnd (att.entity=rse.entity and att.isKey=true)
  to t : REL!RELAttribute
    (name<-att.name, isKey<-att.isKey, relation<-rse.relship)
}
```

**Hình 3. Phiên bản ban đầu của phép biến đổi ATL ER2REL**

Luật đầu tiên S2S ánh xạ các ER schema thành các REL schema, luật thứ hai E2R ánh xạ mỗi entity thành một relation, và luật thứ ba R2R ánh xạ mỗi relationship thành một relation. Ba luật còn lại sinh ra các thuộc tính (attribute) cho các relation. Cả thuộc tính của entity lẫn của relationship đều được ánh xạ thành thuộc tính của relation (các luật EA2A và RA2A). Hơn nữa, các thuộc tính khóa của các entity tham gia cũng được ánh xạ thành thuộc tính của relation (luật RA2AK).

Tiếp theo, để minh họa ngữ nghĩa thực thi của ATL, chúng tôi giải thích cách nó hoạt động, chẳng hạn, đối với luật RA2A. Luật này được áp dụng cho mọi tổ hợp của một thực thể ERAttribute `att` và một thực thể Relship `rs` sao cho điều kiện `att.relship=rs` đúng. Đối với mỗi khớp như vậy, một RELAttribute `t` được tạo ra. Giá trị của các thuộc tính `name` và `isKey` của `t` được sao chép trực tiếp từ `att`. Đối với phép gán của thuộc tính `relation`, chiến lược giải quyết ngầm định của ATL sẽ thay thế giá trị của phần tử mẫu đầu vào `rs` (vốn là một đối tượng của mô hình nguồn) bằng một tham chiếu đến đối tượng Relation đã được tạo ra bởi R2R cho `rs`. Trong trường hợp này, R2R là luật duy nhất có thể được dùng để giải quyết các đối tượng Relation. Tuy nhiên, nói chung, có thể có nhiều luật cho mỗi kiểu.

## 3 Các mô hình biến đổi cho ATL (Transformation Models for ATL)

Các phép biến đổi mô hình có thể được xem như các chương trình hoạt động trên các thực thể của siêu mô hình. Theo nghĩa này, chúng ta cũng có thể áp dụng khái niệm đúng đắn cổ điển cho các phép biến đổi mô hình. Chúng tôi sẽ xem các mô hình đầu vào và đầu ra của một phép biến đổi là hợp lệ khi và chỉ khi chúng tuân thủ các ràng buộc của siêu mô hình tương ứng. Tính đúng đắn từng phần (partial correctness) khi đó phát biểu rằng: nếu phép biến đổi sinh ra một mô hình đầu ra từ một mô hình đầu vào hợp lệ, thì mô hình đầu ra đó cũng hợp lệ. Tính đúng đắn toàn phần (total correctness) mở rộng khái niệm này và phát biểu rằng phép biến đổi sinh ra một đầu ra hợp lệ cho MỌI mô hình đầu vào hợp lệ (tức là, phép biến đổi kết thúc (terminate) đối với mọi mô hình đầu vào hợp lệ và không dừng bất thường với một thông báo lỗi).

Khái niệm mô hình biến đổi MT của một phép biến đổi T : MI → MF của chúng tôi nhắm đến việc hỗ trợ kiểm chứng tính đúng đắn từng phần của T bằng cách sử dụng MT như một đại diện tương đương (equivalent surrogate), như sau. Một mô hình biến đổi MT là một siêu mô hình (tức là, một đặc tả cấu trúc gồm các lớp, các quan hệ liên kết, và các ràng buộc) tích hợp MI và MF cùng với các phần tử mô hình hóa cấu trúc bổ sung nhằm nắm bắt ngữ nghĩa thực thi của T. Một cặp gồm một thực thể MI (gọi là MI) và một thực thể MF (gọi là MF) được liên hệ bởi T khi và chỉ khi tồn tại một thực thể của MT mà phần MI của nó là MI và phần MF của nó là MF. Trong thực tế, chúng tôi muốn nới lỏng tính tương đương này để chỉ đúng đối với những MI mà T kết thúc (terminate). Tuy nhiên, đối với tập con khai báo của ATL mà chúng tôi xem xét, các toán tử OCL helper đệ quy là nguồn duy nhất gây ra tình trạng không kết thúc, vì việc thực thi thực sự của các luật ATL không mang tính đệ quy và không lặp (và cũng có tính xác định — deterministic \[18\]).

> **Giải thích:** Đoạn này định nghĩa hình thức thế nào là một "mô hình biến đổi tương đương". Nói đơn giản: MT được coi là "tương đương" với phép biến đổi T nếu và chỉ nếu, với bất kỳ cặp (mô hình vào MI, mô hình ra MF) nào, "T biến MI thành MF" ⟺ "có một thực thể của MT chứa đúng MI ở phần vào và đúng MF ở phần ra". Nhờ vậy, thay vì phải chạy thử phép biến đổi T để kiểm tra, ta chỉ cần kiểm tra sự tồn tại (hoặc không tồn tại) của một thực thể thỏa mãn MT — đây chính là bài toán mà các bộ tìm mô hình (model finder) như Alloy giải quyết được.

Có được một mô hình biến đổi tương đương như vậy, chúng ta có thể kiểm chứng tính đúng đắn từng phần của T bằng cách sử dụng các bộ tìm mô hình có sẵn (ví dụ, dựa trên SAT solving). Trong phần còn lại của mục này, chúng tôi trình bày cách suy ra nó một cách có hệ thống cho các phép biến đổi ATL. Chúng tôi cung cấp một thuật toán tổng quát cho việc này (Mục 3.1) và thảo luận về tính đúng đắn (validity) của phép dịch của chúng tôi (Mục 3.2).

### 3.1 Một thuật toán để suy ra các mô hình biến đổi cho ATL

Phép dịch của chúng tôi bao phủ một tập con đáng kể của ATL, cụ thể là các matched rule, vốn là "cỗ máy chính" (workhorse) của ATL, dưới dạng được trình bày trong Hình 4. Chúng tôi giả định rằng tất cả các biểu thức và phép gán trong phép biến đổi đều được kiểu hóa (typed) đúng. Chúng tôi hiện chưa hỗ trợ các mở rộng mệnh lệnh (imperative extension), các luật được gọi (called rule) hay luật lười (lazy rule), và chúng tôi không cho phép các toán tử OCL helper đệ quy.

Thuật toán tạo ra MT cho T : MI → MF được trình bày trong Hình 5. Nó gồm bốn bước chính. Kết quả của thuật toán áp dụng cho ER2REL được trình bày trong Hình 6 (các lớp và quan hệ liên kết được sinh ra) và Hình 7 (các ràng buộc được sinh ra). Bước đầu tiên bao gồm việc đưa vào tất cả các phần tử (tức là các lớp, quan hệ liên kết, thuộc tính, ràng buộc) của MI và MF. Bước thứ hai thêm một lớp mới cr cho mỗi luật r trong T (bước 1a; ví dụ, lớp 'S2S' trong Hình 6), kết nối cr với các kiểu của các biến mẫu đầu vào và đầu ra (bước 1b và 1c). Sau đó, nó thêm hai ràng buộc khớp mẫu (matching constraint) đảm bảo rằng chính xác những tổ hợp đối tượng MI được kết nối với một đối tượng cr là những tổ hợp được khớp bởi r (bước 1d và 1e; ví dụ, match_EA2A và match_EA2A_cond trong Hình 7). Đối với mỗi phép gán vào một đối tượng mẫu đích, các ràng buộc gán (binding constraint) tương ứng trên cr được thêm vào (bước 1f; ví dụ, bind_E2R_t_name). Đối với các thuộc tính chưa được gán, một ràng buộc được thêm vào để đảm bảo các thuộc tính này là null (bước 2g). Bước thứ ba xem xét mỗi lớp trong MF và thêm một ràng buộc tạo lập (creation constraint) để đảm bảo rằng mỗi đối tượng MF được tạo ra bởi đúng một luật của T (ví dụ, create_Relation trong Hình 7). Bước thứ tư dành riêng cho những phép biến đổi có các mẫu có khả năng chồng lấp (overlapping pattern) lên nhau. Nhắc lại rằng ATL không cho phép một tổ hợp đối tượng MI được khớp bởi nhiều hơn một luật (bộ máy thực thi sẽ dừng bất thường (abort) trong điều kiện này). Bước thứ tư thêm các ràng buộc loại trừ lẫn nhau (mutual exclusion constraint) tương ứng cho mọi cặp luật có khả năng chồng lấp (ER2REL không chứa các luật như vậy).

Chúng tôi sử dụng một số hàm phụ trợ trong việc mô tả thuật toán để sinh ra các biểu thức OCL cho các ràng buộc phức tạp hơn. Chúng tôi định nghĩa chúng dưới đây. Để tạo ra các quan hệ liên kết kết nối các lớp cr với lớp tương ứng trong MI và MF, chúng tôi giả định rằng −→s và −→o sinh ra các đầu liên kết có thể điều hướng tương ứng cho các biến mẫu s và o (theo góc nhìn của lớp luật), và ←−s và ←−o sinh ra các tên đầu liên kết đối diện duy nhất (theo góc nhìn của lớp tương ứng trong MI và MF). Hơn nữa, chúng tôi sử dụng ký hiệu mũ (hat notation) ẑ để chỉ một biến mới (fresh variable).

> **Giải thích:** Đây là phần cốt lõi kỹ thuật của bài báo — thuật toán dịch một luật ATL thành một tập các lớp và ràng buộc OCL. Ý tưởng trực quan: với mỗi luật ATL `r`, ta tạo ra MỘT LỚP MỚI đại diện cho "một lần thực thi luật r" (đối tượng của lớp này giống như một "biên bản ghi lại" một lần khớp mẫu thành công). Lớp mới này được nối bằng các quan hệ liên kết tới các đối tượng đầu vào (mà nó đã khớp) và các đối tượng đầu ra (mà nó đã tạo ra). Sau đó, các ràng buộc OCL được thêm vào để: (1) đảm bảo lớp "biên bản" này chỉ có đúng các thực thể ứng với các tổ hợp đối tượng đầu vào thực sự thỏa điều kiện lọc của luật (ràng buộc khớp mẫu — matching constraint), (2) đảm bảo giá trị thuộc tính của đối tượng đầu ra đúng bằng biểu thức gán trong luật (ràng buộc gán — binding constraint), (3) đảm bảo mỗi đối tượng đầu ra chỉ được tạo bởi đúng một luật (ràng buộc tạo lập — creation constraint), và (4) đảm bảo không có hai luật nào cùng khớp một tổ hợp đầu vào (ràng buộc loại trừ lẫn nhau). Bốn nhóm ràng buộc này, cộng lại, mô phỏng đầy đủ ngữ nghĩa thực thi của ATL nhưng thuần túy dưới dạng khai báo OCL — không còn "chạy" theo trình tự nữa.

**Hàm phụ trợ matchExpr(r).** Hàm matchExpr(r) mà chúng tôi sử dụng ở bước 1d cho ra một biểu thức OCL kiểu Boolean gồm m biểu thức 'forAll' lồng nhau cho m phần tử mẫu đầu vào của r, sao cho với mỗi tổ hợp đối tượng trong MI khớp với r

```
rule r
  from s1 : t1, . . . , sm : tm (filterExpr)
  to o1 : t'1(prop1,1 ← expr1,1, . . . , prop1,k1 ← expr1,k1),
     ...
     on : t'n(propn,1 ← exprn,1, . . . , propn,kn ← exprn,kn)
```

trong đó mỗi exprj,p có một trong các dạng sau:

- **Dạng I:** propj,p ← exprj,p trong đó exprj,p có kiểu cơ bản (basic type)
- **Dạng II:** propj,p ← o trong đó o là một biến mẫu đầu ra của r
- **Dạng III:** propj,p ← col{o1, . . . , oq} một tập hợp các biến mẫu đầu ra của r
- **Dạng IV:** propj,p ← exprj,p trong đó exprj,p có kiểu t và t tương ứng với một lớp trong MI
- **Dạng V:** propj,p ← exprj,p trong đó exprj,p có kiểu col(t) và t tương ứng với MI

**Hình 4. Các dạng mẫu của matched rule trong ATL hiện được cách ánh xạ của chúng tôi hỗ trợ.**

> **Giải thích:** Năm "dạng" (shape) này phân loại kiểu giá trị mà một phép gán (binding) trong luật ATL có thể trả về, để thuật toán biết cách dịch nó sang OCL. Dạng I là giá trị đơn giản (số, chuỗi, boolean) — không cần "giải quyết" gì thêm. Dạng II/III là khi giá trị gán chính là một biến mẫu đầu ra khác của cùng luật đó (một đối tượng vừa được tạo) — cũng đơn giản, chỉ cần điều hướng. Dạng IV/V là trường hợp khó nhất: giá trị gán là (hoặc là tập hợp của) một đối tượng thuộc mô hình NGUỒN — trường hợp này cần áp dụng cơ chế "resolve" (giải quyết ngầm định) đã mô tả ở Mục 2, để tìm ra đối tượng ĐÍCH tương ứng đã được luật nào đó tạo ra.

Được sinh ra bởi các bước 1a và 1e (các lớp và quan hệ liên kết được sinh ra) và Hình 7 (các ràng buộc được sinh ra). Thuật toán như sau:

```
1. Sao chép tất cả các phần tử mô hình của MI và MF.
2. Đối với mỗi matched rule r trong T, gọi s1 : t1, . . . , sm : tm là các biến mẫu
   đầu vào của r và o1 : t'1, . . . , o1 : t'n là các biến mẫu đầu ra của r. Khi đó:
   (a) Thêm một lớp cr.
   (b) Nếu m = 1 (tức r chỉ có một biến mẫu đầu vào duy nhất), thêm một quan hệ
       liên kết: t1 --(1..1, −→s1)-- cr --(0..1, ←−s1)--
       Ngược lại, nếu m > 1, thêm quan hệ liên kết sau cho mỗi 1 ≤ i ≤ m:
       ti --(1..1, −→si)-- ci --(0..∗, ←−si)--
   (c) Đối với mỗi biến mẫu đầu ra oj : t'j của r với 1 ≤ j ≤ n, thêm một quan hệ
       liên kết: cr --(0..1, ←−oj)-- t'j --(1..1, −→oj)--
   (d) Thêm một ràng buộc: context t1 inv : matchExpr(r).
   (e) Thêm một ràng buộc: context cr inv : filterExpr'
       trong đó filterExpr' = filterExpr[s1 . . . sm]/[self.−→s1 . . . self.−→sm]
       là biểu thức lọc với tất cả các biến mẫu đầu vào được thay thế bằng các
       điều hướng từ đối tượng luật.
   (f) Đối với mỗi phép gán propj,p ← exprj,p vào một biến mẫu đầu ra oj của r
       với 1 ≤ j ≤ n và 1 ≤ p ≤ kn, thêm một ràng buộc:
       context cr inv : self.−→oj.propj,p = resolve[[ expr'j,p ]]
       trong đó expr'j,p = [s1 . . . sm]/[self.−→s1 . . . self.−→sm].
       Nếu exprj,p thuộc Dạng IV, thêm thêm một ràng buộc:
       context cr inv : expr'j,p.isDefined() = resolve[[ expr'j,p ]].isDefined().
       Nếu exprj,p thuộc Dạng V, thêm thêm một ràng buộc:
       context cr inv : expr'j,p→size() = resolve[[ expr'j,p ]]→size().
   (g) Đối với mỗi thuộc tính prop của oj không được gán bởi r, chúng tôi thêm
       một ràng buộc: context cr inv : self.−→oj.prop = null.
3. Đối với mỗi lớp c trong MF, thêm một ràng buộc:
   context c inv : self.←−o1→size() + · · · + self.←−oq→size() = 1
   nếu {o1 : t'1, . . . , oq : t'q} = creators(c). Ngược lại, khi không có creator
   nào cho c, thêm một ràng buộc: context c inv : false.
4. Đối với mỗi cặp luật r, r' trong T có mẫu đầu vào cùng kích thước m và mỗi
   dãy kiểu MI t''1, . . . , t''m, thêm một ràng buộc loại trừ lẫn nhau:
   context t1 inv : mutexExpr(r, r', 〈t''1, . . . , t''m〉)
   nếu r và r' có khả năng chồng lấp trên t''1, . . . t''m. Các luật r và r' chồng
   lấp trên t''1, . . . t''m khi t''i ≤ ti và t''i ≤ t'i đúng với mỗi i sao cho 1 ≤ i ≤ m.
```

**Hình 5. Thuật toán**

exactly một thực thể của cr được kết nối với những đối tượng này. Nó được định nghĩa như sau.

```
matchExpr(r) := t1 → forAll(ŝ1 | t2 → forAll(ŝ2 | . . . tm → forAll(ŝm |
  filterExpr' implies
  cr.allInstances() → one(ẑ | ẑ.−→s1 = ŝ1 and . . . and ẑ.−→sm = ŝm)
) · · · )
```

trong đó filterExpr' = filterExpr\[s1 . . . sm\]/\[ŝ1 . . . ŝm\] là biểu thức lọc của r trong đó các tên biến mẫu được thay thế bằng các tên biến được sử dụng trong phép lặp ở trên.

**Hàm phụ trợ resolve\[\[ expr \]\].** Hàm resolve\[\[ expr \]\] mà chúng tôi sử dụng ở bước 1f là hàm phức tạp nhất. Chúng tôi dùng nó để dịch cơ chế giải quyết ngầm định (implicit resolve mechanism) của ATL sang OCL. Nhắc lại rằng ATL, khi xử lý một phép gán prop ← expr, thay thế mỗi giá trị đối tượng từ MI bằng một giá trị đối tượng từ MF. Để làm điều này, nó sử dụng biến mẫu đầu vào đầu tiên của luật (mẫu đầu vào đơn — unary input pattern) đã khớp với đối tượng tương ứng trong MI. Gọi t là kiểu của expr. Gọi {(x1 : t1, y1 : t'1), . . . , (xq : tq, yq : t'q)} là tập các cặp (xi : ti, yi : t'i) gồm biến mẫu đầu vào duy nhất và biến mẫu đầu ra đầu tiên với t ≤ ti hoặc ti ≤ t, lấy từ tất cả các luật trong T có mẫu đầu vào đơn (unary input pattern). Lưu ý rằng trong tập này chúng tôi xem xét các biến mẫu của nhiều luật khác nhau trong T, do đó chúng tôi ưu tiên sử dụng một chỉ số tối đa khác là q ở đây.

- Đối với Dạng I, II, và III, không cần giải quyết (resolution), vì kết quả hoặc là một kiểu cơ bản hoặc là một giá trị (tập hợp) của MF — nhắc lại rằng chúng tôi đã thay thế tất cả các biến mẫu đích o bằng self.−→o ở bước (2f). Ta có: resolve\[\[ expr \]\] := expr.

- Đối với Dạng IV, chúng tôi phân biệt hai trường hợp. Khi q = 1 (chỉ có một luật duy nhất có thể khớp với kiểu này), thì chúng ta có thể dịch phép giải quyết thành hai bước điều hướng đơn giản⁶ (phép ép kiểu — type cast — có thể được bỏ qua khi expr đã có kiểu đủ cụ thể):

  ```
  resolve[[ expr ]] := expr.oclAsType(t1).←−x1.−→y1.
  ```

  Khi q &gt; 1, thì có nhiều luật tiềm năng có thể được dùng cho bước giải quyết này. Lưu ý rằng không thể có hai luật được áp dụng cùng một lúc (và chúng tôi đảm bảo điều này bằng các ràng buộc loại trừ lẫn nhau), do đó chúng ta có thể dùng toán tử 'any' để chọn ra một:

  ```
  resolve[[ expr ]] := col{expr.oclAsType(t1).←−x1.−→y1,
                            . . . ,
                            expr.oclAsType(tq).←−xq.−→yq} → any(true)
  ```

- Đối với Dạng V, phép dịch tương tự như trường hợp trước, nhưng bây giờ chúng ta phải áp dụng bước giải quyết cho từng phần tử của tập hợp (sử dụng 'collect'). Kết quả trung gian là một Bag (túi) gồm một vài tập hợp rỗng và nhiều nhất một tập hợp không rỗng. Chúng ta biến nó thành một tập hợp phẳng bằng cách dùng 'flatten'.

  ```
  resolve[[ expr ]] := col{ expr → collect(ẑ|ẑ.oclAsType(t1).←−x1.−→y1),
                            . . . ,
                            expr → collect(ẑ|ẑ.oclAsType(tq).←−xq.−→yq)} → flatten()
  ```

> ⁶ Nhắc lại rằng chỉ các matched rule có mẫu đầu vào đơn (unary input pattern) mới được sử dụng ở đây, do đó ←−x1 là một điều hướng có giá trị đối tượng (object-valued navigation), x. bước 2b.

> **Giải thích:** Hàm `resolve` mô phỏng chính xác cơ chế "tự động dò tìm đối tượng đích tương ứng" của ATL đã nêu ở Mục 2. Nếu chỉ có đúng MỘT luật có thể tạo ra đối tượng đích tương ứng với kiểu nguồn đó (q=1), việc "giải quyết" chỉ đơn giản là đi ngược từ đối tượng nguồn, qua quan hệ liên kết ngược ←x1 (về lại "đối tượng biên bản" của luật đó), rồi đi tiếp theo quan hệ liên kết −→y1 để tới đối tượng đích đã được luật đó tạo ra. Nếu có NHIỀU luật khả dĩ (q&gt;1), ta liệt kê tất cả các khả năng thành một tập hợp rồi dùng `any(true)` để "chọn đại một cái" — vì các ràng buộc loại trừ lẫn nhau (mutual exclusion) đã đảm bảo trước rằng trên thực tế, quá trình khớp mẫu, chỉ có nhiều nhất một trong các khả năng đó thực sự tồn tại (những khả năng còn lại sẽ là tập rỗng), nên `any(true)` an toàn để lấy ra giá trị duy nhất khác rỗng.

**Hình 6. Sơ đồ lớp của mô hình biến đổi được sinh ra MER2REL**

*(Sơ đồ mô tả các lớp luật mới được sinh ra: S2S, E2R, R2R, EA2A, RA2A, RA2AK, mỗi lớp được nối bằng các quan hệ liên kết (với các bội số 1 hoặc 0..1 và tên vai trò như s, t, att, ent, rs, rse) tới các lớp gốc của ER (ERSchema, Entity, Relship, ERAttribute, RelshipEnd) và của REL (RELSchema, Relation, RELAttribute).)*

**Hàm phụ trợ creators(c).** Chúng tôi dùng creators(c) để xác định tất cả các vị trí mà một lớp của MF có thể được khởi tạo. Cụ thể hơn, đây là tập tất cả các biến mẫu đầu ra {o1 : t1, . . . , oq : tq} từ tập tất cả các luật của T sao cho tj ≤ c với mỗi j sao cho 1 ≤ j ≤ q.

**Hàm phụ trợ mutexExpr(r, r', 〈t''1, . . . , t''n〉).** Hàm này cho ra một biểu thức loại trừ lẫn nhau cho một cặp luật có khả năng chồng lấp r, r' ở bước 4. Nhắc lại rằng mỗi bộ đối tượng MI chỉ có thể được khớp bởi nhiều nhất một luật, nếu không bộ máy thực thi ATL sẽ dừng bất thường. Gọi s1 : t1, . . . sm : tm và s'1 : t'1, . . . s'm : t'm là các biến mẫu đầu vào của các luật r và r'. Gọi t''1, . . . , t''m là một dãy các kiểu đối tượng MI có khả năng được khớp bởi cả r và r'. Hàm mutexExpr(r, r', 〈t''1, . . . , t''n〉) sinh ra một biểu thức OCL kiểu Boolean phát biểu rằng không tổ hợp thực thể nào của t''1, . . . t''m có thể được kết nối với cả một thực thể cr và một thực thể cr'.

```
mutexExpr(s, s', 〈t''1, . . . , t''n〉) :=
  t''1.allInstances() → forAll(ŝ1| · · ·
    t''m.allInstances() → forAll(ŝm|
      not( cr.allInstances() → exists(ẑ|ẑ.−→s1 = ŝ1 and · · · and ẑ.−→sm = ŝm) and
           cr'.allInstances() → exists(ẑ'|ẑ'.−→s'1 = ŝ1 and · · · and ẑ'.−→s'm = ŝm))
  · · · )
```

### 3.2 Tính đúng đắn của phép dịch (Validity of the Translation)

Như đã nói ở đầu mục này, một mô hình biến đổi MT phải tương đương với T (đối với các phép biến đổi không sử dụng các toán tử helper đệ quy), nhằm sử dụng MT như một đại diện để kiểm chứng tính đúng đắn (từng phần) của T. Nhắc lại rằng chúng tôi đã định nghĩa khái niệm mô hình biến đổi như sau: một cặp gồm một thực thể MI (gọi là MI) và một thực thể MF (gọi là MF) được liên hệ bởi T khi và chỉ khi tồn tại một thực thể của MT mà phần MI của nó là MI và phần MF của nó là MF. Vì cho đến nay chưa có ngữ nghĩa hình thức (formal semantics) cho ATL, chúng tôi phải biện minh cho việc tiên đề hóa (axiomatization) OCL của mình một cách không chính thức. Trong phần sau, chúng tôi xem xét các khía cạnh khác nhau của ngữ nghĩa thực thi của các matched rule trong ATL và đưa ra các lý do vì sao phép dịch của chúng tôi sang các ràng buộc OCL là phù hợp. Để cho ngắn gọn, chúng tôi đơn giản nói "MT trên MI và MF" để phát biểu rằng MT là một thực thể của MT mà phần MI của nó là MI và phần MF của nó là MF.

```
-- Các ràng buộc được sinh ra bởi các bước 2d và 2e: ràng buộc khớp mẫu
context ERSchema inv match_S2S:
  ERSchema.allInstances()->forAll(x1 : ERSchema |
    S2S.allInstances()->one(z : S2S | z.s = x1))

context Entity inv match_E2R:
  Entity.allInstances()->forAll(x1 : Entity |
    E2R.allInstances()->one(z : E2R | z.s = x1))

context Relship inv match_R2R:
  Relship.allInstances()->forAll(x1 : Relship |
    R2R.allInstances()->one(z : R2R | z.s = x1))

context ERAttribute inv match_EA2A:
  ERAttribute.allInstances()->forAll(x1 : ERAttribute |
    Entity.allInstances()->forAll(l_ent : Entity | x1.entity=(l_ent) implies
      EA2A.allInstances()->one(z : EA2A | z.att = x1 and z.ent = l_ent)))
context EA2A inv match_EA2A_cond: self.att.entity = self.ent

context ERAttribute inv match_RA2A:
  ERAttribute.allInstances()->forAll(x1 : ERAttribute |
    Relship.allInstances()->forAll(x2 : Relship | x1.relship=x2 implies
      RA2A.allInstances()->one(z : RA2A | z.att = x1 and z.rs = x2)))
context RA2A inv match_RA2A_cond: self.att.relship = self.rs

context ERAttribute inv match_RA2AK:
  ERAttribute.allInstances()->forAll(x1 : ERAttribute |
    RelshipEnd.allInstances()->forAll(x2 : RelshipEnd | x1.entity=x2.entity and x1.isKey implies
      RA2AK.allInstances()->one(z : RA2AK | z.att = x1 and z.rse = x2)))
context RA2AK inv match_RA2AK_cond: self.att.entity = self.rse.entity and
  self.att.isKey

-- Các ràng buộc được sinh ra bởi bước 2f: ràng buộc gán (binding constraints)
context S2S inv bind_S2S_t_relations: self.t.relations =
  Set{self.s.elements->collect(z|z.oclAsType(Entity).e2r.t),
      self.s.elements->collect(z|z.oclAsType(Relship).r2r.t)}->flatten()

context E2R inv bind_E2R_t_name: self.t.name = self.s.name
context R2R inv bind_R2R_t_name: self.t.name = self.s.name

context EA2A inv bind_EA2A_t_relation: self.t.relation = self.ent.e2r.t
context EA2A inv bind_EA2A_t_name: self.t.name = self.att.name
context EA2A inv bind_EA2A_t_isKey: self.t.isKey = self.att.isKey

context RA2A inv bind_RA2A_t_name: self.t.name = self.att.name
context RA2A inv bind_RA2A_t_relation: self.t.relation = self.rs.r2r.t
context RA2A inv bind_RA2A_t_isKey: self.t.isKey = self.att.isKey

context RA2AK inv bind_RA2AK_t_isKey: self.t.isKey = self.att.isKey
context RA2AK inv bind_RA2AK_t_relation: self.t.relation =
  self.rse.relship.r2r.t
context RA2AK inv bind_RA2AK_t_name: self.t.name = self.att.name

-- Các ràng buộc được sinh ra bởi bước 3: ràng buộc tạo lập (creation constraints)
context RELSchema inv create_RELSchema: self.s2s->size() = 1
context Relation inv create_Relation: self.e2r->size() + self.r2r->size() = 1
context RELAttribute inv create_RELAttribute:
  self.ea2a->size() + self.ra2a->size() + self.ra2ak->size() = 1

-- không có ràng buộc nào được sinh ra bởi bước 4 (ràng buộc loại trừ lẫn nhau)
```

**Hình 7. Các ràng buộc của mô hình biến đổi được sinh ra MER2REL**

**Dừng bất thường (Abnormal termination).** Đối với tập con ATL được xem xét (các matched rule được kiểu hóa đúng, không có mở rộng mệnh lệnh, không có toán tử helper đệ quy), bộ máy thực thi sẽ luôn dừng lại (halt), và chỉ có hai trường hợp dừng bất thường khi áp dụng một phép biến đổi T lên một mô hình đầu vào MI. Trường hợp thứ nhất là khi hai hoặc nhiều luật được áp dụng lên cùng một bộ đối tượng MI. Phép dịch của chúng tôi ngăn chặn điều này bằng các ràng buộc loại trừ lẫn nhau (được sinh ra ở bước 4). Điều kiện dừng bất thường thứ hai là khi một đối tượng MF không thể được giải quyết (resolve) thành một đối tượng MI trong quá trình xử lý các phép gán. Điều kiện này bị loại trừ bởi các ràng buộc được sinh ra ở bước 2f. Do đó, khi T dừng bất thường trên MI, không có thực thể nào của MT hoàn tất (complete) MI.

**Khớp mẫu (Matching).** Các ràng buộc được sinh ra ở bước 2d yêu cầu rằng mỗi bộ đối tượng khớp với mẫu đầu vào của một luật r phải được kết nối với đúng một thực thể của cr. Các bội số 1..1 được sinh ra cho các quan hệ liên kết đầu vào của cr đảm bảo rằng không có thực thể nào khác của cr tồn tại. Do đó, kết hợp với việc MT loại trừ các thực thể MI mà sẽ dẫn đến dừng bất thường do khớp nhiều lần, các ràng buộc khớp mẫu trong MT mã hóa chính xác ngữ nghĩa khớp mẫu của ATL.

**Gán và Giải quyết (Binding and Resolution).** Trong ATL, một đối tượng MF chỉ có thể được tạo ra bởi một luật duy nhất, và chỉ luật đó mới gán các thuộc tính của đối tượng đó. Điều này được phản chiếu một-một bởi các ràng buộc gán mà chúng tôi sinh ra ở bước 2f. Chúng tôi đã biện minh rằng hàm phụ trợ resolve của mình mã hóa chính xác cơ chế giải quyết ngầm định của ATL. Do đó, kết hợp với việc MT loại trừ các thực thể MI sẽ để lại các tham chiếu chưa được giải quyết, các ràng buộc gán trong MT mã hóa chính xác ngữ nghĩa gán của ATL.

**Vấn đề khung (Frame problem).** Cho đến nay, chúng tôi đã biện minh, thông qua các ràng buộc khớp mẫu và gán, rằng một thực thể MT trên MI và MF tồn tại nếu MF = T(MI). Các ràng buộc tạo lập được tạo ra ở bước 3 đảm bảo rằng MT không được chứa bất kỳ đối tượng MF nào không được sinh ra bởi một luật. Hơn nữa, bước 2g đảm bảo rằng các thuộc tính là null trừ khi chúng được gán bởi một luật. Kết hợp lại, điều này hoàn tất sự tương ứng "khi và chỉ khi" giữa T và MT.

> **Giải thích:** "Vấn đề khung" (frame problem) là một thuật ngữ kinh điển trong logic vị từ và trí tuệ nhân tạo, chỉ vấn đề: khi mô tả một hành động thay đổi trạng thái, làm sao biết được NHỮNG GÌ KHÔNG THAY ĐỔI (ngoài những gì hành động đó trực tiếp tác động)? Ở đây, nếu chỉ có các ràng buộc gán (mô tả những thuộc tính ĐƯỢC gán giá trị gì) mà không có thêm ràng buộc "mọi đối tượng MF phải được tạo bởi đúng một luật" (creation constraint) và "mọi thuộc tính không được luật nào gán thì phải là null", thì mô hình biến đổi MT sẽ cho phép các thực thể "thừa" hoặc "lạ" xuất hiện trong MF mà không thực sự tương ứng với việc chạy T — phá vỡ tính tương đương hai chiều mong muốn. Ba nhóm ràng buộc (khớp mẫu + gán + tạo lập) cùng nhau mới đóng kín (khép kín) hoàn toàn ngữ nghĩa của T.

## 4 Sử dụng các bộ tìm mô hình để kiểm chứng các phép biến đổi ATL (Employing Model Finders to Verify ATL Transformations)

Sau khi đã dịch một phép biến đổi ATL T thành một mô hình biến đổi thuần túy cấu trúc MT (tức là, một siêu mô hình gồm các lớp và các thuộc tính của chúng, cùng các ràng buộc), chúng ta có thể sử dụng các bộ tìm mô hình có sẵn (bộ kiểm tra tính thỏa mãn được của mô hình) để kiểm chứng tính đúng đắn từng phần của T đối với các ràng buộc siêu mô hình của MF, bằng cách sử dụng MT.

Cụ thể, chúng ta có thể kiểm tra xem T có thể biến một mô hình đầu vào hợp lệ MI thành một mô hình đầu ra không hợp lệ MF hay không, như sau: gọi coni với 1 ≤ i ≤ n là ràng buộc thứ i của MF. Gọi MFi là một phiên bản đã sửa đổi của MF, đã loại bỏ tất cả các ràng buộc của nó và có thêm một ràng buộc mới negconi là phủ định của coni. Gọi MTi là mô hình biến đổi được xây dựng cho T : MI → MFi. T là đúng đắn đối với coni khi và chỉ khi MTi không có thực thể nào. Nếu một thực thể như vậy tồn tại, thì phần MI của nó là một phản ví dụ (counter example) mà T sinh ra một kết quả không hợp lệ.

> **Giải thích:** Đây là kỹ thuật kiểm chứng cụ thể được áp dụng. Để kiểm tra xem phép biến đổi T có luôn đảm bảo ràng buộc coni (một ràng buộc cụ thể của siêu mô hình đầu ra) hay không, tác giả dùng chiến lược "chứng minh bằng phản chứng" (proof by contradiction) theo kiểu bounded model checking: thay vì hỏi "T có luôn thỏa coni không?" (khó kiểm chứng trực tiếp), ta hỏi ngược lại "có tồn tại một thực thể của MT mà VI PHẠM coni hay không?" (tức là thỏa mãn phủ định ¬coni). Nếu bộ tìm mô hình (như Alloy) tìm thấy MỘT thực thể như vậy, thì thực thể đó chính là một phản ví dụ cụ thể: một mô hình đầu vào hợp lệ mà khi biến đổi qua T sẽ cho ra mô hình đầu ra VI PHẠM ràng buộc coni — nghĩa là T có lỗi. Nếu bộ tìm mô hình không tìm thấy thực thể nào (trong phạm vi giới hạn kích thước đã đặt), ta có bằng chứng (giới hạn) rằng T đúng đắn đối với coni.

### 4.1 Kiểm chứng bằng UML2Alloy

Chúng tôi đã cài đặt phép dịch được trình bày như một phép biến đổi ATL "bậc cao" (higher-order), tức là, một phép biến đổi ATL nhận vào một phép biến đổi ATL (chính là phép biến đổi cần được kiểm chứng, bao gồm cả các siêu mô hình đầu vào và đầu ra) và sinh ra mô hình biến đổi tương ứng. Các siêu mô hình và ràng buộc được biểu diễn về mặt kỹ thuật bằng EMF và OCLinEcore. Sau đó chúng tôi sử dụng bộ tìm mô hình UML2Alloy \[1\] (cùng với một số mã "kết dính" — gluing code) để kiểm tra mô hình biến đổi đã "phủ định" (như đã giải thích ở trên) về tính thỏa mãn được (satisfiability).

> **Giải thích:** "Higher-order transformation" (phép biến đổi bậc cao) trong ATL nghĩa là một phép biến đổi mà đầu vào/đầu ra của nó KHÔNG PHẢI là các mô hình dữ liệu thông thường, mà chính là các phép biến đổi ATL khác (được biểu diễn dưới dạng mô hình, vì ATL cũng có một siêu mô hình riêng để mô tả cú pháp của chính nó). Ở đây, họ viết một phép biến đổi ATL nhận "mô hình của phép biến đổi ER2REL" làm đầu vào, và sinh ra "mô hình của siêu mô hình biến đổi MER2REL" làm đầu ra — tự động hóa hoàn toàn thuật toán ở Mục 3.

UML2Alloy dịch siêu mô hình và các ràng buộc OCL thành một đặc tả cho công cụ Alloy, công cụ này cài đặt việc kiểm chứng có giới hạn (bounded verification) của logic quan hệ (relational logic). Trong đặc tả kết quả, mỗi lớp được biểu diễn như một signature của Alloy, và mỗi ràng buộc OCL được biểu diễn bằng đúng một fact của Alloy có cùng tên với ràng buộc OCL đó. Do đó, chúng ta có thể kiểm tra việc bao hàm ràng buộc (constraint subsumption) một cách dễ dàng bằng cách vô hiệu hóa và phủ định các fact (lần lượt từng cái một) đối với các ràng buộc của MF.

Bảng 1 cho thấy các kết quả kiểm chứng đối với ER2REL. Chúng tôi đã kiểm chứng cả bảy ràng buộc của REL bằng cách sử dụng số lượng đối tượng mỗi lớp tăng dần (số lượng phạm vi tối đa cho mỗi signature phải được chỉ định khi chạy Alloy). Chúng ta có thể thấy rằng một phản ví dụ cho (chỉ) ràng buộc REL_AN có thể được tìm thấy khi sử dụng ít nhất ba đối tượng mỗi lớp. Điều này có nghĩa là tồn tại một thực thể ER hợp lệ được biến đổi thành một thực thể REL không hợp lệ bởi ER2REL. Alloy trình bày phản ví dụ này dưới cả định dạng XML và một ký hiệu đồ họa dạng sơ đồ đối tượng (object-diagram).

Hình 8 mô tả một phản ví dụ như vậy đối với REL_AN: rõ ràng, ER2REL không xử lý đúng các mối liên kết phản thân (reflexive relationship). Trong khi tất cả các tên thuộc tính là duy nhất trong entity và relationship sở hữu chúng ở mô hình đầu vào, phép biến đổi lại sinh ra các tên thuộc tính giống hệt nhau trong cùng một relation ở mô hình đầu ra. Có một số cách để giải quyết vấn đề cụ thể này trong ER2REL. Như một giải pháp, chúng ta có thể sửa đổi luật RA2AK để sử dụng tên của đầu liên kết (relationship end) (thay vì tên thuộc tính khóa) để xác định tên của một thuộc tính khóa ngoại (foreign key attribute). Nhưng trong trường hợp này, chúng ta phải cấm các khóa kết hợp (combined key), nếu không chúng ta sẽ lại vi phạm REL_AN ở vòng kiểm chứng tiếp theo. Như một giải pháp tổng quát hơn, chúng ta có thể giới thiệu các tên định danh (qualified name) cho các khóa ngoại (kết hợp tên của đầu liên kết và tên của thuộc tính khóa). Chúng tôi để cho người đọc quyết định giải pháp nào là phù hợp nhất cho tình huống nào. Thay vào đó, chúng tôi muốn xem lại Hình 8 và nhấn mạnh những lợi ích của các phản ví dụ mà phương pháp của chúng tôi sinh ra: các phản ví dụ trình bày cùng lúc mô hình đầu vào gây lỗi (tiết lộ vấn đề) và một lời giải thích về việc thực thi phép biến đổi (cách các luật biến mô hình đầu vào thành một mô hình đầu ra không hợp lệ). Theo quan điểm của chúng tôi, điều này khiến phương pháp của chúng tôi trở thành một công cụ trực quan và mạnh mẽ cho các nhà phát triển phép biến đổi.

> **Giải thích:** "Reflexive relationship" (mối liên kết phản thân) là một mối liên kết mà một entity liên kết với CHÍNH KIỂU của nó (ví dụ: một Employee "quản lý" một Employee khác — cả hai đầu của mối liên kết đều là Employee). Lỗi mà Alloy tìm ra là: khi một mối liên kết như vậy có hai key attribute cùng tên "x" ở hai đầu liên kết khác nhau (do hai đầu liên kết trỏ tới cùng một Entity), thuật toán biến đổi RA2AK sẽ sinh ra hai RELAttribute cùng tên "x" trong cùng một Relation kết quả — vi phạm ràng buộc REL_AN (tên thuộc tính phải duy nhất trong một relation). Đây là một ví dụ thực tế, cụ thể chứng minh giá trị thực tiễn của phương pháp: công cụ tìm được một lỗi tinh vi mà con người dễ bỏ sót khi thiết kế luật biến đổi.

### 4.2 Khả năng mở rộng (Scalability)

Bảng 1 cũng cung cấp một số hiểu biết về khả năng mở rộng của phương pháp kiểm chứng. Tùy thuộc vào ràng buộc, thời gian kiểm chứng bắt đầu trở nên đáng kể khi vượt quá 100 đối tượng. Tất nhiên, các con số này phụ thuộc rất nhiều vào độ phức tạp của ràng buộc. Trong khi ví dụ ER2REL đơn giản về số lượng lớp và quan hệ liên kết, chúng tôi cho rằng nó có độ phức tạp ràng buộc trên mỗi lớp tương đối cao.

**Bảng 1. Thời gian giải trung bình (tính bằng giây) sử dụng Alloy**

| Obj/Class | Obj/Total | REL_RN | REL_AN† | REL_K | REL_M1 | REL_M2 | REL_M3 | REL_M4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 28 | 0.06 | \* | 0.06 | 0.05 | 0.05 | 0.05 | 0.7 (0.05) |
| 3 | 42 | 0.15 | 0.11 | 0.10 | 0.11 | 0.11 | 0.11 | 0.09 |
| 5 | 70 | 3.12 | 0.51 | 0.70 | 0.40 | 0.21 | 0.52 | 0.20 |
| 7 | 98 | 38.62 | 0.58 | 4.21 | 1.21 | 0.54 | 3.93 | 0.48 |
| 10 | 140 | 543.93 | 1.70 | 136.61 | 4.96 | 1.53 | 17.03 | 1.33 |

*Ràng buộc không được bao hàm (non-subsumed) được đánh dấu bằng †. Phản ví dụ không phát hiện được đánh dấu bằng (*). Tất cả các phép kiểm tra được tiến hành nhiều lần trên một máy tính xách tay văn phòng 2.2 GHz chạy Alloy 4.1, Windows 7, và Java 7.\*

Chúng tôi có thể xác nhận rằng các sơ đồ lớp lớn hơn / tập thực thể lớn hơn không nhất thiết làm tăng thời gian giải, trong khi các ràng buộc khó hơn (nhiều chồng lấp hơn, ít khả năng xử lý hơn — less tractable) thì có. Theo nghĩa này, chúng tôi tin tưởng rằng phương pháp của mình có thể áp dụng được cho các siêu mô hình lớn hơn. Tuy nhiên, đối với việc kiểm chứng các siêu mô hình và phép biến đổi có kích thước công nghiệp (industrial size), chúng tôi kỳ vọng rằng sẽ cần thêm các phương pháp suy nghiệm (heuristics) và chiến lược phân tách mối quan tâm (separation of concerns) (ví dụ, cắt tỉa siêu mô hình — metamodel pruning \[25\]).

**Hình 8. Phản ví dụ: vi phạm REL_AN**

*(Sơ đồ đối tượng mô tả phản ví dụ: một ERAttribute tên "x" (isKey=true) được khớp bởi cả EA2A (qua một Entity) và RA2AK (qua hai RelshipEnd của cùng một Relship phản thân), dẫn đến việc hai RELAttribute cùng tên "x" (isKey=true) được tạo ra trong cùng một Relation — vi phạm ràng buộc REL_AN về tính duy nhất của tên thuộc tính trong một relation.)*

Đối với các công cụ kiểm chứng mô hình đã chọn (UML2Alloy và Alloy), điều quan trọng cần nhấn mạnh lại là các công cụ này chỉ có thể thực hiện kiểm chứng có giới hạn (bounded verification). Do đó, nếu Alloy không thể tìm thấy một phản ví dụ, điều này không có nghĩa là không có phản ví dụ nào tồn tại ngoài phạm vi tìm kiếm cố định (fixed search bound).

## 5 Công trình liên quan (Related Work)

Chúng tôi có thể liên hệ bài báo của mình với một số công trình khác. Có một vài cách tiếp cận giải quyết tính đúng đắn từng phần theo kiểu Hoare của phép biến đổi mô hình đối với các ràng buộc siêu mô hình như tiền điều kiện (precondition) và hậu điều kiện (postcondition) của phép biến đổi. Inaba và cộng sự tự động suy luận sự tuân thủ lược đồ (schema, tức siêu mô hình) cho các phép biến đổi dựa trên ngôn ngữ truy vấn UnCAL, sử dụng bộ giải MONA \[15\]. Khả năng biểu đạt của lược đồ trong cách tiếp cận này hạn chế hơn OCL và chỉ mô tả kiểu hóa của đồ thị (graph). Ví dụ, tính duy nhất của tên, như trong ER và REL, không thể được biểu đạt. Asztalos và cộng sự suy luận các khẳng định (assertion) cho các phép biến đổi mô hình dựa trên biến đổi đồ thị (graph transformation), sử dụng Prolog \[2\]. Họ sử dụng một ngôn ngữ khẳng định dựa trên các mẫu đồ thị (graph pattern), để bắt buộc hoặc tránh các mẫu nhất định trong mô hình, đây là một mô hình tư duy (paradigm) khác với OCL. Rensink sử dụng kiểm tra mô hình không giới hạn (unbounded model checking) cho các tính chất temporal tuyến tính bậc nhất (first-order linear temporal properties) cho các hệ thống biến đổi đồ thị \[24\]. Cùng hướng đó, Lucio và cộng sự ánh xạ các phép biến đổi vào ngôn ngữ DSLTrans, và các tính chất dựa trên mẫu thành một bài toán kiểm tra mô hình (cũng bằng Prolog) \[20\].

Cụ thể hơn, cũng có những cách tiếp cận dịch các phép biến đổi mô hình thành các mô hình biến đổi theo cách tương tự như chúng tôi làm: trong một công trình trước đây, chúng tôi dịch các ngữ pháp đồ thị bộ ba (triple graph grammar) (vốn có ngữ nghĩa thực thi khác với ATL) và kiểm chứng các điều kiện khác nhau như khả năng thực thi được yếu và mạnh (weak and strong executability) \[8\]. Chúng tôi không đề cập đến khả năng thực thi được (executability) mà tập trung vào tính đúng đắn từng phần (mặc dù chúng tôi kỳ vọng rằng khả năng thực thi được cũng có thể được biểu đạt cho ATL, sử dụng một phiên bản được tùy biến của thuật toán chúng tôi). Theo cùng hướng đó, Guerra và cộng sự sử dụng các đặc tả biến đổi dựa trên ngữ pháp đồ thị bộ ba và sinh ra các bất biến OCL để kiểm tra sự thỏa mãn các đặc tả này bởi các mô hình \[14\]. Theo hiểu biết của chúng tôi, chúng tôi là những người duy nhất trình bày một cách tiếp cận kiểm chứng như vậy cho ATL. Bài báo của chúng tôi là công trình kế thừa các kết quả trước đây \[5\]. Trong công trình trước đó, chúng tôi đưa ra một phác thảo đầu tiên về phép dịch, nhưng chưa mô tả cách thực hiện phép dịch thực sự sang OCL, như chúng tôi làm trong đóng góp hiện tại này.

Liên quan đến khái niệm mô hình biến đổi, các công trình của Braga và cộng sự, Cariou và cộng sự, và Gogolla và Vallecillo sử dụng các ràng buộc OCL để tiên đề hóa các tính chất của phép biến đổi mô hình dựa trên luật dưới dạng các hợp đồng biến đổi (transformation contract) (nhưng họ không sinh ra chúng từ một đặc tả biến đổi) \[3,10,13\].

Theo hiểu biết của chúng tôi, chỉ có hai cách tiếp cận khác cho việc kiểm chứng ATL: thứ nhất, Troya và Vallecillo cung cấp một ngữ nghĩa logic viết lại (rewriting logic semantics) cho ATL và sử dụng Maude để mô phỏng và kiểm chứng các phép biến đổi, nhưng không xem xét việc kiểm chứng tính đúng đắn theo kiểu Hoare \[28\]. Thứ hai, gần đây chúng tôi đã trình bày một cách tiếp cận thay thế cho việc kiểm chứng hình thức tính đúng đắn từng phần của ATL sử dụng các bộ giải SMT và một phép dịch trực tiếp của phép biến đổi ATL thành logic bậc nhất (first-order logic) \[6\]. Cách tiếp cận này bổ sung (complementary) cho cách tiếp cận hiện tại của chúng tôi và cho các cách tiếp cận kiểm chứng có giới hạn khác cho ATL: nó suy luận một cách biểu tượng (symbolically) và không yêu cầu giới hạn về phạm vi mô hình, nhưng nó không đầy đủ (incomplete) (không phải mọi tính chất đều có thể được quyết định tự động theo cách này, mặc dù nó là "hoàn chỉnh về mặt bác bỏ" — refutationally complete — trong nhiều trường hợp). Nó có thể được dùng để kiểm chứng một số hàm ý tiền-hậu điều kiện (pre-post-implication), nhưng không phù hợp lắm để tìm phản ví dụ. Hơn nữa, nó xây dựng trên phép dịch OCL sang logic bậc nhất của Egea và Clavel \[11\], vốn chỉ có thể xử lý một tập con của OCL. Trong khi phép tiên đề hóa OCL nhẹ (lightweight) được trình bày trong công trình hiện tại của chúng tôi phù hợp với các bộ tìm mô hình có giới hạn (và có một cách diễn giải trực quan về các phản ví dụ như các mô hình vết — trace model), chúng tôi đã không thể sử dụng các bộ giải SMT để kiểm chứng nó. Sử dụng một phép dịch trực tiếp của ATL+OCL sang FOL \[6\], chúng tôi có thể tự động chứng minh một số hàm ý mong muốn bằng bộ giải định lý Z3 (với cái giá là cách tiếp cận này đòi hỏi một sự mã hóa FOL đầy đủ của ATL và OCL).

Trong bài báo này, chúng tôi sử dụng UML2Alloy \[1\] để thực hiện việc kiểm chứng mô hình thực tế. Cộng đồng đã phát triển một số cách tiếp cận thay thế mạnh mẽ cho việc kiểm chứng hình thức các mô hình có ràng buộc mà chúng tôi cũng có thể sử dụng. Điểm chung của chúng là mô hình được dịch sang một hình thức luận (formalism) có ngữ nghĩa được định nghĩa rõ ràng. Hầu hết các cách tiếp cận sử dụng suy luận tự động trong hình thức luận đích, ví dụ, logic mô tả (description logic) \[23\], logic bậc nhất (first-order logic) \[11\], logic quan hệ (relational logic) \[19\], bài toán thỏa mãn ràng buộc (constraint satisfaction problems) \[9\], hoặc logic mệnh đề (propositional logic) \[26\]. Một số khác, chẳng hạn \[4\], sử dụng chứng minh định lý tương tác (interactive theorem proving). Chúng tôi đã có thể tái tạo lại các kết quả của UML2Alloy bằng cách sử dụng bản mẫu thử nghiệm (prototype) của Kuhlmann và cộng sự \[19\].

## 6 Kết luận và công việc tương lai (Conclusion and Future Work)

Trong bài báo này, chúng tôi đã trình bày một cách tiếp cận giúp việc kiểm chứng các phép biến đổi ATL trở nên dễ dàng hơn, qua đó giúp cải thiện chất lượng của phương pháp luận MDE trong thực tế. Về cốt lõi, nó dựa trên một phép dịch tự động từ ATL sang một mô hình biến đổi, là một siêu mô hình có ràng buộc có thể được sử dụng như một đại diện cho việc kiểm chứng tính đúng đắn từng phần của phép biến đổi đối với các ràng buộc của siêu mô hình đầu vào và đầu ra. Chúng tôi đã trình bày một mô tả chính xác, có thể thực thi được, của phép dịch cho một tập con đáng kể của ATL. Chúng tôi cũng đã chỉ ra cách phương pháp luận này có thể được cài đặt trong thực tế bằng cách sử dụng một phép biến đổi bậc cao của ATL và một bộ kiểm tra tính thỏa mãn được của mô hình có sẵn (UML2Alloy). Theo hiểu biết của chúng tôi, chúng tôi là những người đầu tiên cung cấp một cách tiếp cận tự động như vậy cho việc kiểm chứng tính đúng đắn từng phần đối với ATL.

Chúng tôi muốn nhấn mạnh rằng quá trình kiểm chứng có thể được tự động hóa như một công nghệ "hộp đen" (black box), theo nghĩa là nhà phát triển phép biến đổi chỉ tiếp xúc với các mô hình, trong đó các mô hình biến đổi được sinh ra và các thực thể của chúng có một cách biểu diễn quen thuộc đối với họ.

Trong tương lai, chúng tôi dự định khám phá khả năng của các bộ tìm mô hình khác nhau như là các hệ thống hậu cần (backend) cho cách tiếp cận của mình, nhằm đánh giá xem cái nào phù hợp nhất cho loại kiểm chứng này. Về phần ATL, chúng tôi đã cài đặt một tập con quan trọng của ATL, nhưng chúng tôi sẽ tích hợp (một dạng hạn chế của) các luật lười (lazy rule) như được gọi, vốn có thể được tìm thấy trong nhiều phép biến đổi. Cuối cùng nhưng không kém phần quan trọng, các nghiên cứu điển hình (case study) toàn diện phải mang lại thêm phản hồi về khả năng áp dụng của công trình chúng tôi.

## Tài liệu tham khảo (References)

 1. Anastasakis, K., Bordbar, B., Georg, G., I.Ray: UML2Alloy: A Challenging Model Transformation. In: MoDELS 2007. LNCS, vol. 4735. Springer (2007)
 2. Asztalos, M., Lengyel, L., Levendovszky, T.: Towards Automated, Formal Verification of Model Transformations. In: ICST'2010, Proc. pp. 15–24. IEEE Computer Society (2010)
 3. Braga, C., Menezes, R., Comicio, T., Santos, C., Landim, E.: On the Specification, Verification and Implementation of Model Transformations with Transformation Contracts. In: SBMF 2011. LNCS, vol. 7021. Springer (2011)
 4. Brucker, A.D., Wolff, B.: HOL-OCL: A Formal Proof Environment for UML/OCL. In: FASE 2008. LNCS, vol. 4961. Springer (2008)
 5. Büttner, F., Cabot, J., Gogolla, M.: On Validation of ATL Transformation Rules By Transformation Models. In: MoDeVVa'2011, Proc. ACM Digital Library (2012), DOI 10.1145/2095654.2095666
 6. Büttner, F., Egea, M., Cabot, J.: On verifying ATL transformations using 'off-the-shelf' SMT solvers. In: MoDELS'2012, to appear. LNCS, Springer (2012)
 7. Bézivin, J., Büttner, F., Gogolla, M., Jouault, F., Kurtev, I., Lindow, A.: Model Transformations? Transformation Models! In: MoDELS 2006. LNCS, vol. 4199. Springer (2006)
 8. Cabot, J., Clarisó, R., Guerra, E., de Lara, J.: Verification and validation of declarative model-to-model transformations through invariants. Journal of Systems and Software 83(2), 283–302 (2010)
 9. Cabot, J., Clarisó, R., Riera, D.: UMLtoCSP: a tool for the formal verification of UML/OCL models using constraint programming. In: Automated Software Engineering, ASE 2007, Proc. ACM (2007)
10. Cariou, E., Belloir, N., Barbier, F., Djemam, N.: OCL contracts for the verification of model transformations. Electronic Communications of the EASST 24 (2009)
11. Clavel, M., Egea, M., de Dios, M.A.G.: Checking Unsatisfiability for OCL Constraints. Electronic Communications of the EASST 24, 1–13 (2009)
12. Gogolla, M.: Tales of ER and RE Syntax and Semantics. In: Transformation Techniques in Software Engineering. IBFI (2005), dagstuhl Seminar Proc. 05161
13. Gogolla, M., Vallecillo, A.: Tractable Model Transformation Testing. In: ECMFA 2011. LNCS, vol. 6698. Springer (2011)
14. Guerra, E., de Lara, J., Kolovos, D.S., Paige, R.F.: A Visual Specification Language for Model-to-Model Transformations. In: 2010 IEEE Symposium on Visual Languages and Human-Centric Computing (VL/HCC 2010). pp. 119–126. IEEE Computer Society (2010)
15. Inaba, K., Hidaka, S., Hu, Z., Kato, H., Nakano, K.: Graph-transformation verification using monadic second-order logic. In: ACM SIGPLAN Conference on Principles and Practice of Declarative Programming, PPDP, 2011, Proc. pp. 17–28. ACM (2011)
16. Jouault, F., Allilaire, F., Bézivin, J., Kurtev, I.: ATL: A model transformation tool. Sci. Comput. Program. 72(1-2), 31–39 (2008)
17. Jouault, F., Bézivin, J.: KM3: A DSL for Metamodel Specification. In: Formal Methods for Open Object-Based Distributed Systems, FMOODS 2006, Proc. LNCS, vol. 4037, pp. 171–185 (2006)
18. Jouault, F., Kurtev, I.: Transforming Models with ATL. In: Proc. of the Model Transformations in Practice Workshop at MoDELS 2005 (2005)
19. Kuhlmann, M., Hamann, L., Gogolla, M.: Extensive Validation of OCL Models by Integrating SAT Solving into USE. In: TOOLS 201. LNCS, vol. 6705, pp. 290–306. Springer (2011)
20. Lucio, L., Barroca, B., Amaral, V.: A Technique for Automatic Validation of Model Transformations. In: MODELS 2010, Part I. LNCS, vol. 6394. Springer (2010)
21. OMG: The Object Constraint Language Specification v. 2.2 (Document formal/2010-02-01). Object Management Group, Inc., Internet: http://www.omg.org/spec/OCL/2.2/ (2010)
22. OMG: Meta Object Facility (MOF) Core Specification 2.4.1 (Document formal/2011-08-07). Object Management Group, Inc., Internet: http://www.omg.org (2011)
23. Queralt, A., Rull, G., Teniente, E., Farré, C., Urpí, T.: AuRUS: Automated Reasoning on UML/OCL Schemas. In: ER 2010. LNCS, vol. 6412. Springer (2010)
24. Rensink, A.: Explicit State Model Checking for Graph Grammars. In: Concurrency, Graphs and Models, Essays Dedicated to Ugo Montanari on the Occasion of His 65th Birthday. LNCS, vol. 5065, pp. 114–132. Springer (2008)
25. Sen, S., Moha, N., Baudry, B., Jézéquel, J.M.: Meta-model Pruning. In: MODELS 2009, Proc. LNCS, vol. 5795, pp. 32–46. Springer (2009)
26. Soeken, M., Wille, R., Drechsler, R.: Encoding OCL Data Types for SAT-Based Verification of UML/OCL Models. In: TAP 2011. LNCS, vol. 6706, pp. 152–170. Springer (2011)
27. Steinberg, D., Budinsky, F., Paternostro, M., Merks, E.: EMF: Eclipse Modeling Framework. Addison-Wesley Longman, Amsterdam, 2nd edn. (2008)
28. Troya, J., Vallecillo, A.: A Rewriting Logic Semantics for ATL. Journal of Object Technology 10, 5: 1–29 (2011)
29. Warmer, J.B., Kleppe, A.G.: The Object Constraint Language: Getting Your Models Ready for MDA. Addison-Wesley, 2nd edn. (2003)
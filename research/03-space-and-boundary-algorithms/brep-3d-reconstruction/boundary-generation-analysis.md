# Phân tích sinh boundary mức 2 từ hình học 3D: CBIP, Ying & Lee, hướng chiếu và cắt

- **Câu hỏi nghiên cứu**: các thuật toán B-rep 3D sinh `IfcRelSpaceBoundary` 2nd level như thế nào: ghép cặp, lỗ mở, `CorrespondingBoundary`, internal/external, virtual?
- **Kết luận ngắn**:
  - **CBIP** (Lilis 2017) là thuật toán rõ ràng nhất đã đọc: 4 giai đoạn, **bắt buộc có `IfcSpace` và `IfcSite`** làm đầu vào, sinh đủ `CorrespondingBoundary`, `ParentBoundary`/`InnerBoundary`, internal/external, physical/virtual. Nó tự nhận là **"graph-less"** và chỉ dùng được khi đã có thể tích space.
  - Vì vậy hướng B-rep gồm **hai nửa nối nhau**: ASG (sinh space, xem `ucl-asg-analysis.md`) rồi CBIP (sinh boundary). Hai nửa này cùng nhóm tác giả UCL.
  - **Ying & Lee 2021** mới chỉ đọc được phần tóm tắt: dùng 3 dạng biểu diễn hình học, chịu IFC kém chất lượng, xử lý hình cong, thử trên 2 mô hình lớn; **không biết 3 dạng là gì, kích thước, thời gian**. Phải đọc toàn văn mới đánh giá được.
- **Độ tin cậy**: cao cho CBIP (đọc bản thảo đã sửa, các phần chính); thấp cho Ying & Lee (chỉ tóm tắt).
- **Ngày thực hiện**: 2026-11-10 (claude-02)

## 1. CBIP (Common Boundary Intersection Projection)
Lilis, Giannakis, Rovas (2017), *Automatic generation of second-level space boundary topology from IFC geometry inputs*, Automation in Construction 76, 108–124. Đã đọc bản thảo đã sửa ("CBIP_revised.pdf"; có thể khác bản đăng). [S1]

### Khái niệm
Mọi phần tử là **đa diện** (polyhedron), biểu diễn bằng B-rep (tập đa giác) và **cây BSP** (cắt đa diện bằng phép trong/ngoài). Hàm cắt: `Fins` (phần nằm trong), `Fout` (phần ngoài), `Fcod` (cặp đa giác đồng phẳng, ngược pháp tuyến thuộc hai đa diện khác nhau). Phép tính hình học theo thuật toán BSP-tree của tài liệu [32] của bài.

### 4 giai đoạn
| # | Giai đoạn | Việc |
|---|---|---|
| 1 | Identification (ID) | Phân phần tử IFC thành **Constructions** (tường, sàn… `IfcBuildingElement`), **Openings** (`IfcOpeningElement`), **Volumes** (`IfcSpace` và `IfcSite`) |
| 2 | Boundary Surface Extraction (BSE) + Opening Construction Subtraction (OCS) | Dựng B-rep của từng phần tử; trừ thể tích lỗ mở khỏi tường chứa nó |
| 3 | Common Boundary Intersection (CBI) | Tìm mặt biên chung giữa từng cặp B-rep: loại **Primary** (chung giữa hai thực thể: tường–space, sàn–space, sàn–site…) và **Derived** (phần B-rep còn lại sau khi trừ, gắn với môi trường: space–môi trường, tường–môi trường…) |
| 4 | Boundary Intersection Projection (BIP) | Chiếu mặt chung này lên mặt phẳng của mặt chung kia và ngược lại → các cặp mặt biên mức 2; **ngưỡng độ dày tối đa** do người dùng đặt (demo dùng 1,2 m) |

Đầu ra: 4 loại phần tử mô phỏng — thermal, shading, opening, air (virtual) — gồm ETE/ITE (thermal ngoài/trong), ESE/ISE (shading), EOE/IOE (opening), EAE/IAE (air). [S1]

### Ánh xạ sang IFC4 (`IfcRelSpaceBoundary2ndLevel`)
- Hình học trong `ConnectionGeometry`.
- `InternalOrExternalBoundary`: INTERNAL / EXTERNAL / EXTERNAL_EARTH / EXTERNAL_WATER / EXTERNAL_FIRE / NOTDEFINED (theo bài).
- `PhysicalOrVirtualBoundary`: PHYSICAL cho bề mặt phần tử, VIRTUAL cho mặt ngăn giữa hai space (air element), NOTDEFINED nếu khác.
- `CorrespondingBoundary`: mặt cặp ở phía đối diện (vd #101 ↔ #102).
- Lỗ mở: `InnerBoundary` trên mặt cha, và `ParentBoundary` trên mặt con.
- `RelatedBuildingElement` gắn với phần tử gốc. [S1]

### Yêu cầu đầu vào
- **Bắt buộc**: có ít nhất một `IfcSite` và một `IfcSpace` (Design Transfer View 1.0 của buildingSMART **không** thoả).
- **Bắt buộc**: vật thể cong xuất sang IFC phải là **xấp xỉ đa diện** với pháp tuyến hướng ra ngoài (quy tắc bàn tay phải).
- B-rep phải đầy đủ (không thiếu mặt) và pháp tuyến đúng; cần kiểm tra và sửa nếu phần mềm xuất sai.
- Khuyến nghị: tránh giao thể tích khác không (clash); tránh khe giữa space và phần tử (sinh "space-environment surface" sai); curtain wall phải nằm trọn trong một thể tích opening. Clash không làm thuật toán dừng nhưng làm kết quả kém chính xác. [S1]

### Thử nghiệm
Toà nhà "Technical Services" Đại học Kỹ thuật Crete, 2 tầng, space lồi và lõm: nhận 514 boundary mức 2, trong đó 122 là boundary trong của lỗ mở; ngưỡng độ dày 1,2 m. **Không có thời gian chạy hay kích thước mô hình**; không so với ground truth. [S1]

### CBIP nhận định về các phương pháp graph
Bài viết: các phương pháp khác dùng đồ thị thì **không cần thể tích space** mà suy ra từ B-rep của phần tử bao: (1) van Treeck & Rank 2007: nút là mặt của B-rep, cạnh là cạnh chung giữa mặt; (2) Rose & Bazjanac: nút là mặt biên chung space–phần tử và các phần tử giữa chúng, cạnh là đường truyền nhiệt khả dĩ; (3) Jones et al. 2013: nút là đa giác phần tử "nhìn thấy nhau" theo hệ số hình dạng (view factor). Nhưng chúng **không** nói tới shading ngoài, virtual partition và mặt tiếp đất; còn CBIP có nhưng **không áp dụng được khi thiếu thể tích space**. [S1]
→ Đây là bằng chứng trực tiếp: **graph** (suy ra space) và **CBIP** (cần space) bổ sung nhau; mô tả này cũng cho `TASK-002` một cách phân loại ba biến thể graph.

## 2. Ying & Lee 2021 (chỉ tóm tắt)
*Generating second-level space boundaries from large-scale IFC-compliant building information models using multiple geometry representations*, Automation in Construction 126, 103659, DOI 10.1016/j.autcon.2021.103659. [S2]
- Tuyên bố: tính thông tin hình học và ngữ nghĩa của boundary mức 2 từ **nhiều biểu diễn hình học** của phần tử và space; chịu IFC chưa hoàn hảo; xử lý vật thể cong thường gặp; chạy hiệu quả với mô hình lớn nhờ **3 loại biểu diễn hình học**; thử trên **2 mô hình thực lớn**, boundary "accurate" và sinh "efficiently".
- **Không rõ từ nguồn đã đọc**: 3 loại biểu diễn là gì; kích thước/độ phức tạp của 2 mô hình; thời gian chạy; cách xử lý hình cong; yêu cầu đầu vào; có cần `IfcSpace` không. Cần mua hoặc tải toàn văn (Elsevier). Chưa đọc.

## 3. Hướng chiếu và cắt mức 2 của IFC2SB (so sánh)
IFC2SB sau khi có space (từ graph) làm mức 2 bằng chiếu và cắt (khoảng cách tối đa mặc định 0,41 m phân biệt 2a/2b, ngưỡng góc 95°) và ray tracing để tìm mặt tương ứng. [S3] Gần với BIP của CBIP về ý tưởng "chiếu hai mặt đối diện lên nhau trong ngưỡng độ dày", nhưng không có cây BSP.

## 4. Bài học thiết kế cho dự án (đề xuất của người viết)
- Pipeline **hai nửa** hợp lý: (A) suy ra space (ASG-kiểu hoặc graph-kiểu) → (B) sinh boundary mức 2 bằng chiếu và cắt kiểu CBIP/BIP, vì cả hai bài đều ghi nhận đây là cách chung của họ cho mức 2.
- Tham số ngưỡng độ dày tối đa và độ dày quyết định 2a/2b cần đưa vào `config/` (dung sai).
- Với sân vận động: CBIP buộc xấp xỉ đa diện cho vật cong → số mặt tăng; hiệu năng cây BSP trên nhiều mặt chưa biết.

## Chưa xác minh / việc còn lại
- Toàn văn Ying & Lee 2021 (ba biểu diễn, mô hình, thời gian).
- Toàn văn Rose & Bazjanac, Ladenhauf 2016 (chỉ biết qua bảng so sánh của Fichter và danh mục tham khảo của CBIP).
- Bản đăng chính thức của CBIP có thể khác bản thảo đã sửa.
- Chưa tìm thấy mã nguồn công khai của CBIP hay ASG.

## Nguồn
- [S1] Lilis, Giannakis, Rovas (2017), CBIP: https://discovery.ucl.ac.uk/id/eprint/1546334/1/CBIP_revised.pdf — đã đọc các phần chính (2026-11-10)
- [S2] Ying & Lee (2021): https://pure.uos.ac.kr/en/publications/generating-second-level-space-boundaries-from-large-scale-ifc-com/ — chỉ trang tóm tắt (2026-11-10)
- [S3] Fichter et al. (2021): https://publications.ibpsa.org/proceedings/bs/2021/papers/bs2021_30156.pdf và mã IFC2SB (xem `../graph-topology/ifc2sb-analysis.md`)

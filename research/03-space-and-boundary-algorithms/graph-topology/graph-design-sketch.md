# Phác thảo thiết kế hướng Graph cho dự án

- **Câu hỏi nghiên cứu**: nếu làm hướng Graph, nút và cạnh là gì, tìm vùng kín thế nào, đưa vào `IfcSpace` và boundary ra sao, yếu ở đâu?
- **Kết luận ngắn**: có **hai biến thể**, bằng chứng khác nhau xa. Biến thể A (đồ thị kề mặt 3D, kiểu IFC2SB) **có tiền lệ chạy được**. Biến thể B (đồ thị tường 2D theo từng tầng, "Wall → Graph → Cycle → Space") **chưa tìm thấy công cụ nào làm cho IFC**; về bản chất nó trùng hướng lát cắt mặt bằng (TASK-005), chỉ khác cách tìm miền kín.
- **Độ tin cậy**: biến thể A: trung bình (theo mã và bài báo, chưa chạy). Biến thể B: thấp (thiết kế do mình đề xuất, không có tiền lệ đã đọc). **Phần "Đề xuất" là ý kiến của người viết, không phải kết quả từ nguồn.**
- **Ngày thực hiện**: 2026-11-10 (claude-02)

## 1. Biến thể A — đồ thị kề mặt 3D (có tiền lệ: IFC2SB)
**Nút** = mặt đã tách của mọi phần tử bao; **cạnh** = hai mặt có chung cạnh hình học. Space = thành phần liên thông kín. Chi tiết thuật toán gốc: `ifc2sb-analysis.md` mục 3.

Các bước (khung, theo IFC2SB; bước 0 và 7 là đề xuất cho dự án):
0. *(Đề xuất)* Kiểm tra IFC đầu vào: có `IfcSpace` chưa, hình học phần tử có đọc được không (hướng D trong `approach-critique.md`).
1. Đọc hình học từng `IfcBuildingElement` (tường, sàn, trần, mái, cột, cửa, cửa sổ) bằng IfcOpenShell; lấy các mặt BRep.
2. *(Tuỳ chọn, theo IFC2SB)* Thay hình chi tiết cửa/cửa sổ bằng hình `IfcOpeningElement`; đơn giản hoá curtain wall.
3. *(Tuỳ chọn)* Đóng khe nhỏ: kéo dài/offset mặt vài cm, hoặc dùng dung sai `fuzzy` của phép fuse.
4. Hợp mọi mặt bằng General Fuse (OCCT `BOPAlgo_Builder`), thu được tập mặt không giao nhau trừ ở cạnh chung.
5. Dựng bản đồ cạnh → mặt, lập danh sách kề cho mỗi mặt.
6. Tỉa: mặt "treo", kề sai hướng, cạnh phi-manifold (chọn mặt có góc nhỏ hơn).
7. Tìm thành phần liên thông (DFS/BFS) → mỗi thành phần là một vỏ kín = một `IfcSpace` ứng viên; kiểm tra: không chồng nhau, thể tích > 0, pháp tuyến hướng vào trong.
8. Boundary mức 1 = các mặt của vỏ, gắn `RelatedBuildingElement` bằng nguồn gốc mặt trước khi fuse (cần giữ ánh xạ mặt → phần tử; IFC2SB dùng `oFace`/`cFace` và "rank" xử lý mặt đồng phẳng).
9. Mức 2 = chiếu và cắt mặt đối diện (không dùng graph), ray tracing phân loại 2a/2b, ghép `CorrespondingBoundary`.
10. Ghi `IfcSpace` (+ biểu diễn đùn hoặc BRep) và `IfcRelSpaceBoundary*`; giữ GUID và Pset của space cũ nếu có.

**Điểm cần quyết nếu tự cài đặt (đề xuất):**
- Tự viết bằng Python (IfcOpenShell mới + pythonocc) hay dùng lại/bọc IFC2SB (C++, GPL, thư viện cũ)?
- Chia nhỏ để kiểm soát chi phí fuse: theo `IfcBuildingStorey`, theo khối công trình (khu khán đài), rồi ghép. **Chưa có nguồn nào xác nhận cách này đúng**; cần thử trên mô hình lớn của TASK-001.

## 2. Biến thể B — đồ thị tường 2D theo tầng (ý ban đầu của người dùng)
**Nút** = giao điểm/đầu mút trục tường trong mặt phẳng tầng; **cạnh** = đoạn tường; miền kín = mặt (face) của đồ thị phẳng, tìm bằng duyệt chu trình theo nửa cạnh (kiểu DCEL), hoặc bằng `shapely.polygonize` hay `BOPTools.SplitAPI.slice`. Sau đó đùn từ cao độ sàn đến trần/mái.
- **Không tìm thấy tiền lệ cho IFC.** Công cụ gần nhất, `DetectRoom` của FreeCAD_SketchArch, chia hộp bao theo cạnh sketch rồi đùn `FloorHeight`: là phép chia mặt phẳng (arrangement), không phải duyệt chu trình đồ thị, và đầu vào là sketch chứ không phải IFC.
- Về lý thuyết, "chu trình của đồ thị phẳng" và "polygonize" cho cùng kết quả hình học; khác nhau ở cài đặt. Nên **gộp vào TASK-005** thay vì làm hướng Graph riêng, trừ khi đồ thị cung cấp thứ mà polygonize không có (ví dụ truy vấn liên thông giữa các phòng).
- Yếu: tường cong/chéo (cần đường trục cong), mái dốc, khán đài bậc thang (không phải khối đùn), cột và vách kính (không có trục tường), cao độ cắt phải chọn.

## 3. Yếu điểm chung với công trình lớn như sân vận động (suy luận, chưa thử)
| Vấn đề | Biến thể A | Biến thể B |
|---|---|---|
| Khối không kín (khán đài mở trời) | Không tạo space kín; cần mặt ảo (virtual) hoặc `IfcExternalSpatialElement` đóng vỏ | Miền không bị bao kín bởi tường nên không thành mặt của đồ thị |
| Số lượng mặt (nghìn tới hàng trăm nghìn) | Chi phí General Fuse tăng theo số mặt và mức giao cắt; **chưa có số liệu** | Rẻ hơn nhiều (2D) |
| Hình cong / mặt xoắn | OCCT xử lý mặt cong, bài báo nói không giới hạn độ cong; chưa có thử nghiệm | Khó (trục cong) |
| Hình học bẩn | Chịu được khe vài cm (bài báo); bị ảnh hưởng nếu khe lớn | Tường lệch/chồng làm đồ thị hở |

## Chưa xác minh / việc còn lại
- Luận án Fichter 2022 (đang BLOCKED, cần người dùng tải tay) có thể mô tả đầy đủ bước tỉa, luật chấp nhận không gian khi pháp tuyến chưa biết, và độ phức tạp: cần đọc trước khi chốt thiết kế.
- Bài van Treeck & Rank 2007 (gốc) chưa mở.
- Chưa có thử nghiệm nào về chia khối để giảm chi phí fuse.

## Nguồn
Xem `ifc2sb-analysis.md`, `survey.md`. Ngoài ra: Fichter et al. 2021 https://publications.ibpsa.org/proceedings/bs/2021/papers/bs2021_30156.pdf (đã đọc); FreeCAD_SketchArch `ArchSketchObject.py` (đã đọc).

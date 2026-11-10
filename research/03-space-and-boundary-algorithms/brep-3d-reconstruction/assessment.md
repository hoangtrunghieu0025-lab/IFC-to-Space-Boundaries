# Đánh giá hướng B-rep 3D

- **Câu hỏi nghiên cứu**: hướng dựng thể tích `IfcSpace` từ B-rep 3D và sinh boundary mức 2 bằng chiếu/cắt có đáng làm cho dự án không?
- **Kết luận ngắn**: **Nên làm, ở dạng pipeline hai nửa**: (A) suy ra `IfcSpace` kiểu ASG (trừ mặt tiếp xúc cặp, gom vỏ, phân vỏ trong/ngoài bằng thể tích có dấu), rồi (B) sinh boundary mức 2 kiểu CBIP/BIP (chiếu và cắt, ngưỡng độ dày). Thuật toán đã được mô tả đủ chi tiết để cài lại và chỉ cần phép toán 2D trên đa giác đồng phẳng. **Mức bằng chứng: trung bình** (đọc toàn văn ASG, CBIP, Fichter; Ying & Lee chỉ tóm tắt; không có mã, không có số liệu hiệu năng). Nên chạy **song song với hướng Graph** (TASK-002): hai hướng cùng bản chất "gom mặt theo cạnh chung" ở bước tìm space.
- **Độ tin cậy**: trung bình.
- **Ngày thực hiện**: 2026-11-10 (claude-02)

## Bảng tiêu chí chung
| Tiêu chí | Đánh giá (kèm bằng chứng) |
|---|---|
| Sinh được `IfcSpace`? | **Có** (ASG). CBIP **không** sinh (cần `IfcSpace`). Ying & Lee: chưa rõ |
| Sinh được `IfcRelSpaceBoundary` 1st/2nd? | **Mức 2: có** (CBIP: `CorrespondingBoundary`, internal/external 6 giá trị, physical/virtual, `ParentBoundary`/`InnerBoundary`, shading, air element). Mức 1: ASG sinh space = mặt mức 1. Nhưng **chưa có bài nào đã đọc nối trọn ASG → CBIP** thành một chuỗi chạy được |
| Yêu cầu hình học đầu vào | **Cao**: B-rep đầy đủ, pháp tuyến đúng hướng ra ngoài, tránh clash và khe giữa space–phần tử (ASG, CBIP). Clash được xử lý một phần ở ASG (tập `IS_ij`); mặt thiếu/ngược phải sửa trước. Chỉ số LIS < 2e−4 là ngưỡng "tốt" |
| Hình cong / mái dốc / khán đài bậc thang | **Cong**: bắt buộc xấp xỉ đa diện (CBIP) hoặc facet trước (ASG, Ying & Lee 2019). **Mái dốc, bậc thang**: là mặt phẳng nên chấp nhận được; chưa có thử nghiệm. **Khán đài mở trời**: không có vỏ trong kín (suy luận) |
| Quy mô | Tối đa 11 tầng (Torre Turina), toà văn phòng 78 space (IFC2SB). **Sân vận động: không có bằng chứng**. Ying & Lee 2021 tuyên bố "large-scale" nhưng chưa đọc số liệu |
| Hiệu năng / bộ nhớ | **Không có số liệu** trong ASG, CBIP. Nghẽn khả dĩ: kiểm mọi cặp B-rep (ASG), cây BSP (CBIP) (suy luận). Xem `scalability-notes.md` |
| Độ phức tạp cài đặt, thư viện, license | **Vừa**: ASG chỉ cần 2D polygon clipping (Clipper/Shapely) và gom vỏ; CBIP cần BSP-tree và cắt đa diện. Không có mã công khai tìm thấy; có thể cài bằng Python (pythonocc/Shapely), hoặc dùng OCCT. License: không áp dụng (không dùng lại mã) |
| Độ trưởng thành | **Thấp–trung bình**: thuật toán học thuật, 1–2 mô hình mỗi bài; không thấy công cụ phát hành hay mã mở; nhóm UCL tuyên bố đưa ASG vào khung web service (chưa kiểm chứng đã làm) |
| Rủi ro chính | (1) Phụ thuộc hình học sạch: mô hình thật thường có clash và khe → space dính nhau hoặc hở; (2) khán đài mở và khối không kín; (3) không có số liệu quy mô, kiểm mọi cặp có thể bùng nổ; (4) chưa có mã tham chiếu để đối chiếu kết quả |
| **Kết luận** | **Nên làm.** Mức bằng chứng: **trung bình**. Để nâng lên "cao": đọc toàn văn Ying & Lee 2021; cài thử ASG-kiểu trên IFC nhỏ trong `samples/small/` và đo LIS, IoU diện tích với `IfcSpace` gốc; đo thời gian và RAM trên mô hình lớn của TASK-001 |

## So sánh nhanh với hướng Graph (TASK-002)
| | B-rep 3D (ASG + CBIP) | Graph (IFC2SB) |
|---|---|---|
| Tìm space | Trừ mặt tiếp xúc cặp-đôi rồi gom vỏ theo cạnh chung | Fuse toàn bộ mặt, dựng đồ thị kề, thành phần liên thông |
| Phép toán lõi | 2D đa giác đồng phẳng (Clipper) + 3D cây BSP | Boolean 3D General Fuse (OCCT) |
| Khe/clash | Nhạy; cần sửa trước; có xử lý clash qua `IS_ij` | Chịu khe "vài cm" nhờ offset/fuzzy (offset tắt mặc định trong mã) |
| Mã tham chiếu | Không có (mô tả trong bài) | Có (C++, GPL/LGPL, thư viện cũ) |
| Boundary mức 2 | Có CBIP/BIP cụ thể | Có (chiếu + cắt + ray tracing) |
Hai hướng **không loại trừ nhau**: có thể dùng IFC2SB làm tham chiếu để kiểm kết quả cài lại ASG.

## Việc đề xuất tiếp
1. Đọc toàn văn Ying & Lee 2021 (tìm bản đọc được) để biết ba biểu diễn hình học.
2. Prototype ASG-kiểu trên IFC nhỏ bằng IfcOpenShell + Shapely (không phải trong task nghiên cứu này, nếu cần thì lập task mới).
3. Cập nhật `dataset-quality-criteria.md` (TASK-001) với tiêu chí hình học đầu vào của ASG/CBIP và chỉ số LIS.

## Chưa xác minh / việc còn lại
- Toàn văn Ying & Lee 2021, Rose & Bazjanac, Ladenhauf 2016.
- Chưa chạy bất kỳ thuật toán nào của hướng này (chỉ đọc bài).
- Mã nguồn công khai của ASG, CBIP (không tìm thấy).
- Số liệu thời gian/RAM: không có trong nguồn, chưa đo.

## Nguồn
Xem `survey.md`, `ucl-asg-analysis.md`, `boundary-generation-analysis.md`, `scalability-notes.md`.

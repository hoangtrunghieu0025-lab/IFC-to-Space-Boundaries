# Đánh giá hướng lát cắt mặt bằng + polygonize

- **Câu hỏi nghiên cứu**: hướng này có đáng làm mốc so sánh (baseline) không, và nó cần đạt mức nào mới có ý nghĩa?
- **Kết luận ngắn**: **Làm mức cơ sở (baseline)**, không làm hướng chính. Chạy được ngay trên IFC thật, rất nhanh với nhà nhỏ, cài bằng thư viện phổ thông. Đo: **38/63 `IfcSpace` (60 %) khớp IoU ≥ 0,5** trên 6 file nhỏ. Không biểu diễn được mái dốc, khán đài bậc thang, không gian không đùn. Mức bằng chứng: **trung bình** (đo thật nhưng chỉ 6 file nhỏ, đa số nhà trực giao).
- **Đề nghị ngưỡng baseline (ý kiến người viết)**: trên các IFC nhỏ đã chọn, hướng 3D/graph/voxel nên đạt tỉ lệ khớp cao hơn con số 60 % và khớp ở cả tầng mái. Hướng nào không vượt được baseline này thì không đáng cài đặt phức tạp hơn.
- **Độ tin cậy**: trung bình.
- **Ngày thực hiện**: 2026-11-10 (claude-02)

## Bảng tiêu chí chung
| Tiêu chí | Đánh giá (kèm bằng chứng) |
|---|---|
| Sinh được `IfcSpace`? | **Có thể**: tìm được vùng phòng 2D; chưa cài bước chiều cao và đùn. Bonsai và SketchArch đã làm bước đùn |
| Sinh được `IfcRelSpaceBoundary` 1st/2nd? | **Không** trực tiếp: chỉ cho phòng 2D; boundary phải dùng hướng khác |
| Yêu cầu hình học đầu vào | **Thấp–vừa**: phần tử là solid kín, pháp tuyến ra ngoài; tường khép kín ở cao độ cắt; cửa có cánh đặc hoặc có vách ảo. Phần tử hỏng bị bỏ qua mà không báo |
| Hình cong / mái dốc / khán đài bậc thang | **Cong**: cắt lưới cho đa tuyến, có thể ổn. **Mái dốc**: kém (tầng áp mái FZK 0/1 ở `close = 0`). **Khán đài bậc thang**: không (suy luận) |
| Quy mô | Đo trên nhà tối đa 4 tầng, 21 `IfcSpace` (duplex-a). Sân vận động: **không có bằng chứng**; phần hình học 2D rẻ, nhưng lấy hình học 3D bằng IfcOpenShell tốn (tới 10 s cho nhà nhỏ) |
| Hiệu năng / bộ nhớ | Cắt và polygonize 0,01–0,25 s mỗi file nhỏ (đo); lấy hình học 0,7–10 s. RAM chưa đo riêng |
| Độ phức tạp cài đặt, thư viện, license | **Thấp**: IfcOpenShell + Shapely + numpy; prototype khoảng 200 dòng Python. License thư viện: IfcOpenShell LGPL, Shapely BSD (chưa kiểm tra lại) |
| Độ trưởng thành | **Thấp** về học thuật (không có bài), **vừa** về thực dụng (Bonsai, SketchArch có tính năng tương tự, nhưng người dùng báo lỗi trên file thật) |
| Rủi ro chính | (1) Kết quả phụ thuộc cao độ cắt và cửa; (2) tường không khép kín thì mất phòng; (3) không phản ánh được chiều cao thật; (4) đóng khe bằng buffer có thể làm dính phòng |
| **Kết luận** | **Làm mức cơ sở.** Mức bằng chứng: **trung bình**. Để nâng lên "cao": điều tra các ca không khớp, thử nhiều `dz`, thêm bước chiều cao và đùn, thử mô hình có cột, mái dốc, tường cong |

## Số liệu tham chiếu để so sánh với các hướng khác
| | Giá trị |
|---|---|
| Số `IfcSpace` (6 file nhỏ) | 63 |
| Khớp IoU ≥ 0,5 (`close = 0`) | 38 (60 %) |
| Phòng thừa | 9 |
| Thời gian cắt và polygonize | ≤ 0,25 s mỗi file |
Chi tiết: `prototype/README.md`.

## Chưa xác minh / việc còn lại
- Nguyên nhân từng ca không khớp (duplex-a, bsi-ifc4).
- Chưa thử trên mô hình M/L; chưa cài bước chiều cao/đùn.
- Giấy phép các thư viện cần kiểm tra lại trước khi dùng thật.

## Nguồn
Xem `survey.md`, `method-analysis.md`, `limits.md`, `prototype/README.md`.

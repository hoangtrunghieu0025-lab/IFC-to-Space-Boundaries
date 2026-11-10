# Phân tích phương pháp lát cắt mặt bằng cho IFC

- **Câu hỏi nghiên cứu**: quy trình lát cắt mặt bằng + polygonize để suy ra `IfcSpace` từ IFC cụ thể ra sao; chọn cao độ cắt, xử lý cửa, tường không khép kín, cột, nhiều tầng?
- **Kết luận ngắn**: quy trình tối thiểu gồm 5 bước (cắt → vòng có hướng → hợp footprint → lấy lỗ → đùn) chạy được trên IFC thật và rất nhanh (dưới 0,3 s phần hình học 2D cho nhà nhỏ). Đo trên 6 file nhỏ: **38/63 `IfcSpace` khớp (IoU ≥ 0,5)**. Phần quyết định chất lượng là cao độ cắt, phân cách giữa phòng không có tường (vách ảo), và khe ở góc tường.
- **Độ tin cậy**: trung bình: có chạy thật nhưng chỉ 6 file nhỏ; các bước chiều cao và đùn mới là đề xuất, chưa cài.
- **Ngày thực hiện**: 2026-11-10 (claude-02)

## 1. Quy trình đề xuất
| # | Bước | Trạng thái |
|---|---|---|
| 1 | Chọn cao độ cắt cho từng `IfcBuildingStorey` | **Đã cài** (`z = cao độ tầng + dz`, dz = 1,0 m) |
| 2 | Cắt phần tử bằng mặt phẳng, lấy đoạn có hướng, nối vòng, dựng tiết diện | **Đã cài**, hiệu chỉnh hướng bằng hộp đơn vị |
| 3 | Hợp tiết diện thành footprint; phòng = lỗ của footprint | **Đã cài** |
| 4 | Đóng khe nhỏ bằng `buffer(+x).buffer(-x)` | **Đã cài**, thử x = 0,05 và 0,15 m |
| 5 | Đối chiếu với `IfcSpace` gốc theo IoU | **Đã cài** (chỉ để đánh giá) |
| 6 | Xác định chiều cao (từ mặt sàn lên trần hoặc mặt dưới sàn/mái) | **Đề xuất**: bắn tia thẳng đứng từ trọng tâm vùng tới mặt sàn/mái đầu tiên |
| 7 | Đùn thành `IfcSpace` và gán vào `IfcBuildingStorey` | **Đề xuất**; tương tự Bonsai và SketchArch |
| 8 | Ghép vùng giữa các tầng cho không gian thông tầng | **Đề xuất**; chưa có tiền lệ đã đọc |

## 2. Quyết định thiết kế và bằng chứng từ thử nghiệm
### Cao độ cắt
- Cắt ở 1,0 m trên cao độ tầng cắt qua cửa đi (thường có cánh đặc), cắt dưới bậu cửa sổ (nhiều file mô hình hoá kính thành khối) và dưới các lỗ treo. Đó là lý do chọn 1,0 m, **không kiểm chứng giá trị khác**.
- Tầng mái (FZK-Haus tầng áp mái, duplex tầng mái): mặt cắt cao 3,7 m (FZK) cắt qua mái xiên nên ra 0 phòng ở `close = 0`; `close = 0,05` đưa FZK tầng áp mái từ 0 lên 1 phòng khớp. Chưa rõ vì sao (nghi khe ở chỗ giao tường–mái).

### Khe và đóng khe
- `--close 0.05` cho FZK-Haus tăng 3 → 4 khớp; duplex-a và bsi không đổi. Đóng khe bằng buffer có thể **làm dính** hai phòng gần nhau; chưa đo tác dụng phụ.

### Cửa đi
- Cánh cửa là khối đặc thì cắt ở 1,0 m đóng được lối đi; nếu cửa mở hoặc không mô hình hoá cánh thì hai phòng nhập một. Nghi ngờ đây là nguyên nhân chính của kết quả thấp ở duplex-a tầng 1 (2 khớp trên 10 `IfcSpace`), nhưng **chưa điều tra**.

### Cột, vách kính, tường cong
- Cột nằm trong phòng tạo lỗ nhỏ trong phòng; code hiện lọc phòng theo diện tích tối thiểu, không loại lỗ do cột. Chưa thử mô hình có cột.
- Tường cong: cắt lưới tam giác cho ra đa tuyến gần cong; không cần đường trục. Ưu điểm so với đồ thị đường trục. Chưa thử.

## 3. Hiệu năng (đo)
| Tác vụ | Thời gian |
|---|---|
| Lấy hình học thế giới bằng IfcOpenShell (nhà nhỏ) | 0,7–10 s mỗi file |
| Cắt và polygonize toàn bộ tầng | 0,01–0,25 s mỗi file |
Máy 14 CPU. Lưu ý phần cắt viết bằng Python thuần trên từng tam giác; vẫn nhanh với nhà nhỏ. Chưa đo trên mô hình lớn.

## 4. Quy trình cho nhiều tầng thông nhau (đề xuất, chưa cài)
Không gian thông tầng (atrium, sảnh, khán đài) cho vùng chồng nhau ở nhiều tầng. Ý tưởng: lấy vùng ở từng tầng, rồi hợp những vùng chồng lên nhau theo chiều đứng nếu không có sàn chắn giữa (kiểm bằng tia thẳng đứng). Chưa có nguồn xác nhận cách này.

## Chưa xác minh / việc còn lại
- Nguyên nhân kết quả thấp ở duplex-a và bsi-ifc4 (không điều tra).
- Ảnh hưởng của `dz` khác 1,0 m; thử nhiều cao độ cắt cho cùng tầng.
- Bước chiều cao và đùn chưa cài.
- Chưa thử mô hình có cột, tường cong, mái dốc lớn.

## Nguồn
Xem `survey.md`. Kết quả đo: `prototype/README.md` và `prototype/results/*.json`.

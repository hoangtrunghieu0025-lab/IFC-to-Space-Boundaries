# Prototype: lát cắt mặt bằng + polygonize (TASK-005)

Mã nghiên cứu, **không phải mã sản phẩm**. Mục đích: đo xem hướng lát cắt mặt bằng đúng/sai ở đâu trên IFC thật nhỏ.

## Chạy
```bash
# venv có ifcopenshell (0.9.0.post1), shapely (2.2.0), numpy
python slice_polygonize.py ../../../../samples/small/ac20-fzk-haus.ifc --dz 1.0 --min-area 1.0 --close 0.0 --json results/ac20-fzk-haus.json
```
Tham số: `--dz` cao độ cắt so với cao độ tầng; `--close x` đóng khe bằng `buffer(+x).buffer(-x)`; `--min-area` diện tích tối thiểu của phòng.

## Thuật toán (đúng như mã)
1. Lấy hình học thế giới (mét) mọi phần tử, **trừ** `IfcSpace`, `IfcOpeningElement`, `IfcVirtualElement`…
2. Với từng `IfcBuildingStorey`, cắt tại `z = cao độ tầng + dz`; chỉ xét phần tử có `zmin < z < zmax`.
3. Đoạn tiết diện **có hướng** (đã hiệu chỉnh bằng hộp đơn vị: diện tích phải ra +1) nối thành vòng; vòng CCW là biên ngoài, CW là lỗ.
4. Footprint = hợp mọi tiết diện. **Phòng ứng viên** = các lỗ (vòng trong) của footprint có diện tích ≥ `min-area`.
5. So với `IfcSpace` cùng tầng (qua `get_aggregate`/`get_container`): tiết diện của `IfcSpace` tại cùng `z`, IoU diện tích; "khớp" khi IoU ≥ 0,5.

## Kết quả (6 file IFC trong `samples/small/`, `close = 0`)
| File | Schema | IfcSpace | bị cắt ở z | khớp IoU ≥ 0,5 | phòng tìm được | phòng thừa |
|---|---|---|---|---|---|---|
| bsi-ifc4-building-architecture | IFC4 | 2 | 2 | 0 | 0 | 0 |
| ac20-fzk-haus | IFC4 | 7 | 7 | 3 | 4 | 1 |
| duplex-a | IFC2x3 | 21 | 19 | 6 | 12 | 6 |
| pilot-project-1 | IFC2x3 | 10 | 10 | 8 | 8 | 0 |
| pilot-project-2 | IFC2x3 | 11 | 11 | 11 | 13 | 2 |
| pilot-project-3 | IFC2x3 | 12 | 12 | 10 | 10 | 0 |
| **Tổng** | | **63** | **61** | **38** | 47 | 9 |

- Tổng thể: **38/63 `IfcSpace` (60 %)** khớp với phòng tìm được, 38/61 (62 %) trong số IfcSpace bị mặt phẳng cắt tới.
- Tham số đóng khe `--close 0.05` (ba file thử): ac20-fzk-haus tăng 3 → 4 khớp (tầng mái 0 → 1); duplex-a không đổi (6); bsi không đổi (0). `--close 0.15` cho kết quả giống 0,05.
- Thời gian (máy 14 CPU): lấy hình học 0,7–10 s mỗi file; cắt và polygonize 0,01–0,25 s.
- File JSON thô trong `results/`.

## Cảnh báo về độ tin cậy
- Chỉ 6 file nhỏ, đa số nhà thấp tầng trực giao; **không đại diện** cho công trình lớn.
- "Khớp" đo bằng IoU tiết diện ở một cao độ cắt, **không** kiểm tra chiều cao hay thể tích.
- Cao độ tầng lấy từ placement; `dz = 1,0 m` đặt cố định, chưa thử nhiều giá trị.
- `bsi-ifc4-building-architecture`: 0 phòng, chưa điều tra nguyên nhân (5 phần tử bị cắt nhưng không tạo vùng kín; có thể 4 tường không khép kín).
- Giả định mô hình là các solid kín có pháp tuyến ra ngoài; phần tử hỏng sẽ cho vòng hở và bị bỏ qua mà không báo.

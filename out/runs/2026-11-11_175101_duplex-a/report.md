# Báo cáo lần chạy: duplex-a.ifc

- Thời điểm: 2026-11-11 17:51:01
- Commit: c79f8eb+chưa commit
- Môi trường: Python 3.12.3, ifcopenshell 0.9.0.post1
- File: `duplex-a.ifc` (2.4 MB, schema IFC2X3)
- Thư mục chạy: `out/runs/2026-11-11_175101_duplex-a`
- Tổng thời gian: 2.7 s, RAM đỉnh: 403 MB

## Thời gian từng bước

| Bước | Giây |
|---|---|
| read_ifc | 0.7 |
| fuse | 0.1 |
| air_faces | 0.2 |
| buried_faces | 0.3 |
| link_faces | 0.2 |
| find_spaces | 0.0 |
| boundaries | 0.0 |
| write_ifc | 1.1 |
| compare_spaces | 0.1 |
| **tổng** | **2.7** |

## Số liệu chính

| Chỉ số | Giá trị |
|---|---|
| Phần tử bao có hình học | 128 |
| Tam giác đầu vào | 7032 |
| Mảnh sau fuse | 11622 |
| Mảnh nhìn về phía không khí | 6346 |
| Mảnh chìm bị loại | 2485 |
| Nhóm mảnh | 15 |
| Phòng tìm được | 9 |
| Boundary mức 1 | 163 |
|   trong đó EXTERNAL | 63 |
|   trong đó INTERNAL | 100 |
| IfcSpace gốc | 21 |

## So với IfcSpace gốc (xấp xỉ)

IfcSpace gốc: 21 (không có hình học: 0). Phòng tìm được: 9. Ghép được: 4 (thể tích chênh không quá 20% và cao độ sàn chênh không quá 0.5 m). Phòng tìm được không ghép được: 5. IfcSpace gốc chưa có phòng tương ứng: 17.

| Phòng tìm được | Thể tích (m3) | IfcSpace gốc | Thể tích gốc (m3) | Chênh |
|---|---|---|---|---|
| Space 04 | 66.98 | B201 | 71.78 | 6.7% |
| Space 06 | 66.44 | A203 | 56.89 | 16.8% |
| Space 03 | 8.79 | A104 | 8.18 | 7.4% |
| Space 02 | 8.78 | B104 | 8.18 | 7.4% |

## Các phòng tìm được

| Phòng | Thể tích (m3) | Cao độ sàn (m) | Cạnh hở | Số mảnh |
|---|---|---|---|---|
| Space 01 | 407.03 | 0.00 | 0.8% | 1372 |
| Space 02 | 8.78 | 0.01 | 0.1% | 40 |
| Space 03 | 8.79 | 0.01 | 0.1% | 38 |
| Space 04 | 66.98 | 3.12 | 0.2% | 250 |
| Space 05 | 42.23 | 3.12 | 2.4% | 246 |
| Space 06 | 66.44 | 3.12 | 0.0% | 211 |
| Space 07 | 41.69 | 3.12 | 2.6% | 209 |
| Space 08 | 18.08 | 3.11 | 1.4% | 108 |
| Space 09 | 16.22 | 3.11 | 2.7% | 103 |

## Nhận xét

(điền tay sau khi xem kết quả)

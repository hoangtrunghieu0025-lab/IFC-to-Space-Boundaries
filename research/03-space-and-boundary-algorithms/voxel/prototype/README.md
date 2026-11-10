# Prototype: suy ra không gian kín bằng voxel (TASK-004)

Mã nghiên cứu, **không phải mã sản phẩm**. Hiện thực ý "flood fill + đảo + trừ" mà Krijnen et al. 2021 nêu là hướng nghiên cứu tiếp theo (mục 6) nhưng chưa làm.

## Chạy
```bash
# venv có ifcopenshell 0.9.0.post1, numpy 2.5.4 (scipy tuỳ chọn)
python voxel_infer.py ../../../../samples/small/pilot-project-1.ifc --h 0.1 --json results/pilot-project-1.h0.1.json
```
Tham số: `--h` cạnh voxel (m); `--close k` giãn k ô để đóng khe; `--min-vol` thể tích tối thiểu của vùng (m³, mặc định 1); `--no-fill-solids` tắt tô đặc phần tử.

## Thuật toán (đúng như mã)
1. Lấy hình học thế giới mọi phần tử **trừ** `IfcSpace`, `IfcOpeningElement`, `IfcVirtualElement`…
2. Voxel hoá **bề mặt** từng phần tử bằng lấy mẫu dày trên tam giác (khoảng mẫu h/2); **xấp xỉ** phép giao tam giác-hộp, có thể bỏ sót tam giác sát biên ô.
3. **Tô đặc** phần tử: trong lưới cục bộ của phần tử, ô trống không nối với viền là phần bên trong. (Không tô thì ruột tường thành "vùng kín" giả: lần chạy đầu cho 18 vùng thay vì 10 ở pilot-project-1 với h = 0,1; kết quả chưa tô lưu ở `results_nofill/`.)
4. Gán nhãn thành phần liên thông 6-liền kề của ô trống; thành phần chạm biên lưới là ngoài trời; còn lại ≥ `min-vol` là **vùng kín ứng viên**.
5. So với `IfcSpace`: tô đặc `IfcSpace` trên cùng lưới và tính IoU thể tích với vùng chứa trọng tâm của nó (vùng ghép nhiều space vẫn tính cả vùng nên IoU thấp).

## Kết quả (6 file IFC nhỏ trong `samples/small/`, 63 `IfcSpace`)
| h (m) | `IfcSpace` khớp IoU ≥ 0,5 | số vùng kín | vùng không có `IfcSpace` |
|---|---|---|---|
| 0,1 | **47/63 (75 %)** | 56 | 7 |
| 0,2 | 45/63 (71 %) | 51 | 2 |
| 0,5 | 2/63 (3 %) | 51 | 2 |

Chi tiết theo file ở `h = 0,1`:
| File | `IfcSpace` | vùng kín | khớp | ghi chú |
|---|---|---|---|---|
| pilot-project-1 | 10 | 10 | 10 | |
| pilot-project-2 | 11 | 13 | 11 | 2 vùng không có `IfcSpace` |
| pilot-project-3 | 12 | 12 | 12 | |
| ac20-fzk-haus | 7 | 4 | 4 | 1 vùng chứa nhiều `IfcSpace` (không gian thông, không vách) |
| duplex-a | 21 | 17 | 10 | 2 vùng ghép nhiều space, 5 vùng thừa |
| bsi-ifc4-building-architecture | 2 | **0** | 0 | công trình không khép kín (cũng 0 phòng ở hướng lát cắt) |

- Thời gian lần chạy cuối (máy 14 CPU): lấy hình học 0,1–3 s mỗi file; voxel hoá + gán nhãn 0,01–2,9 s mỗi file (lớn nhất: duplex-a h = 0,1 với 2,3 triệu ô: 2,6 s). Một phần lần chạy dùng `scipy.ndimage.label` (cài xong giữa chừng) nên thời gian gán nhãn lẫn hai cách; số vùng giống nhau.
- Đo riêng khâu gán nhãn trên lưới 2,37 triệu ô: `scipy.ndimage.label` 0,02 s; BFS Python thuần 1,47 s, cùng số vùng.
- JSON thô: `results/` (đã tô đặc) và `results_nofill/` (chưa tô đặc, bản đầu).

## Cảnh báo về độ tin cậy
- Chỉ 6 file nhỏ, đa số nhà trực giao; không đại diện cho công trình lớn.
- IoU tính trên lưới voxel của chính nó. Với lưới thô, voxel hoá bề mặt làm tường **ăn** vào vùng không khí cỡ một ô ở mỗi mặt nên vùng kín nhỏ hơn `IfcSpace`: IoU giảm mạnh khi h tăng (3 % ở 0,5 m). Chưa hiệu chỉnh.
- "Vùng không có `IfcSpace`" có thể là phòng thật thiếu space (pilot-project-2 cũng có 2 phòng thừa ở hướng lát cắt) hoặc khoang rỗng; chưa kiểm từng ca.
- `bsi-ifc4`: chưa điều tra vì sao không khép kín (cửa bị thiếu hay lỗ hở).
- Sử dụng mô hình sạch; chưa thử mô hình có lỗi hình học.

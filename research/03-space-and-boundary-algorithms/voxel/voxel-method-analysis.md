# Phân tích phương pháp voxel: quy trình, rò rỉ, độ phân giải

- **Câu hỏi nghiên cứu**: quy trình voxel đầy đủ để suy ra không gian kín và boundary; xử lý rò rỉ giữa các space; chọn độ phân giải; chuyển voxel về `IfcSpace` và `IfcRelSpaceBoundary`?
- **Kết luận ngắn**:
  - Voxel **suy ra được vùng không gian kín** từ phần tử bao nếu tường–sàn–trần–cửa tạo vỏ kín: prototype cho **47/63 `IfcSpace` khớp (IoU ≥ 0,5) ở h = 0,1 m** trên 6 IFC nhỏ.
  - Nhưng đó là **kết quả của mình**, không phải của bài báo: Krijnen 2021 chỉ voxel hoá `IfcSpace` có sẵn để sinh thermal interface.
  - Độ phân giải là đánh đổi: h = 0,5 m cho kết quả vô dụng với cách voxel hoá bề mặt của mình (2/63 khớp).
- **Độ tin cậy**: trung bình (có đo thật, nhưng chỉ nhà nhỏ trực giao).
- **Ngày thực hiện**: 2026-11-10 (claude-02)

## 1. Hai quy trình khác nhau, đừng nhầm
| | Krijnen 2021 (đã đọc) | Prototype của mình |
|---|---|---|
| Voxel hoá cái gì | `IfcSpace` | Phần tử bao (tường, sàn…), không voxel hoá `IfcSpace` |
| Mục tiêu | Giao diện nhiệt giữa hai space kề nhau | Tìm khoang không khí kín = space ứng viên |
| Cách khép khe tường dày | Voxel thô làm hai space "chạm nhau" qua tường | Không cần: tìm khoang trống giữa các tường |
| Rò rỉ | Không phát sinh (ranh giới đã là space) | Có: khoang thông ra ngoài hoặc sang phòng khác nếu có khe/cửa mở |
| Trạng thái | Có bài báo, có kết quả | Prototype, 6 file nhỏ |

## 2. Quy trình của prototype (đã cài)
1. Voxel hoá bề mặt từng phần tử (lấy mẫu dày), **tô đặc** phần tử.
2. Ô trống → gán nhãn thành phần liên thông 6-liền kề.
3. Thành phần chạm biên lưới là ngoài trời; thành phần còn lại ≥ 1 m³ là space ứng viên.
4. So với `IfcSpace`: IoU thể tích.
Chi tiết, kết quả: `prototype/README.md`.

## 3. Rò rỉ giữa các space
- **Nguyên nhân thấy trong dữ liệu:** (a) vùng không có tường (FZK-Haus: 4 vùng cho 7 `IfcSpace`, tức nhiều space nằm chung một khoảng không gian thông); (b) công trình không khép kín (bsi-ifc4: 0 vùng); (c) khe nhỏ có thể làm hai space nhập một hoặc làm khoang thông ra ngoài (duplex-a: 2 vùng ghép nhiều space).
- **Cách đã thử:** không áp dụng `--close` trong bảng kết quả chính (chưa chạy tổng hợp).
- **Cách đề xuất (chưa thử):** giãn nhị phân k ô để đóng khe nhỏ (đã cài tham số `--close`); đóng cửa mở bằng khối ảo từ `IfcDoor`/`IfcOpeningElement`; thêm vách ảo (`IfcVirtualElement`) làm ranh giới giữa các space không có tường; tách vùng lớn bằng khoảng cách đến tường (xói mòn hình thái học hoặc phân đoạn khoảng cách, như tóm tắt VOX2BIM+ cho đám mây điểm). OSArch cảnh báo nguy cơ rò rỉ và đề xuất "grow the voxels" (chưa thử).

## 4. Chọn độ phân giải
- Quy tắc từ Krijnen: dùng độ phân giải **đủ thô** để voxel hoá tự đóng khe; nhưng kéo theo sai số: ước lớn thể tích và mất space nhỏ gần độ phân giải; xoay chéo làm tăng diện tích bề mặt (√2 ở 45°).
- Số đo của mình (IoU ≥ 0,5): 75 % ở 0,1 m, 71 % ở 0,2 m, 3 % ở 0,5 m. Sụt mạnh ở 0,5 m vì voxel hoá bề mặt làm tường lấn vào khoang một ô mỗi mặt (đối nghịch với Krijnen: họ voxel hoá space nên ước **lớn**, mình voxel hoá phần tử bao nên khoang ước **nhỏ**).
- Dung sai diện tích trong `PRIMARY_OBJECTIVE.md` (mặc định 1e−3) **không đạt** bằng voxel ở bất kỳ h nào đã thử: sai số tối thiểu cỡ một ô trên mỗi mặt (h = 0,1 m trên phòng 4 m rộng ≈ 5 % diện tích (ước lượng thô)). Voxel chỉ hợp để **định vị** space, không để tính diện tích/chiều dài chính xác.

## 5. Từ voxel về `IfcSpace` và boundary
- **Về `IfcSpace`:** cần khối hình học đẹp: Krijnen đơn giản hoá lưới tam giác thành đa diện bằng cách gộp tam giác cùng nhãn, pháp tuyến và khoảng cách (mặt trực giao nên chính xác); với tường chéo thì mặt bậc thang. Có thể thay bằng đùn từ polygon dấu chân hoặc nội suy mặt từ hình học gốc (đề xuất).
- **Về boundary:** Krijnen: so sánh nhãn voxel kề nhau theo ba hướng dương để dựng tam giác, mỗi tam giác gắn hai nhãn space (hoặc một nhãn nếu ở mặt ngoài); sau đó chiếu lỗ mở (cây AABB) lên mặt giao diện. Tạo `IfcRelSpaceBoundary` **mức 1**; mức 2 và `CorrespondingBoundary` không được bài đề cập.
- Gắn boundary với phần tử gốc (`RelatedBuildingElement`) cần ánh xạ ô về phần tử: bài không nêu; prototype chưa làm.

## Chưa xác minh / việc còn lại
- Toàn văn VOX2BIM+ (trang tạp chí đòi đăng nhập), voxelization toolkit (hàm `segment`, `volume2`): chưa chạy được vì clone/tải thất bại.
- Chưa thử `--close`, chưa thử mô hình có lỗi hình học.
- Chưa có bước chuyển về mặt/`IfcSpace` hoàn chỉnh trong prototype.

## Nguồn
Xem `survey.md`; kết quả đo: `prototype/README.md`.

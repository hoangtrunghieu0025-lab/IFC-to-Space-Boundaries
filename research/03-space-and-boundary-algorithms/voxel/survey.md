# Khảo sát hướng voxel hoá

- **Câu hỏi nghiên cứu**: voxel hoá được dùng thế nào cho IFC/BIM để suy ra space hoặc boundary; độ phân giải, quy mô, giới hạn ra sao?
- **Kết luận ngắn**: bằng chứng **đã đọc** (Krijnen et al. 2021) cho thấy voxel được dùng để **sinh thermal interface từ `IfcSpace` có sẵn**, không phải để suy ra space; suy ra space bằng voxel được tác giả nêu là **hướng nghiên cứu tương lai**. Hướng voxel suy ra phòng có thật nhưng ở lĩnh vực **scan-to-BIM** (đám mây điểm), không phải IFC → IFC.
- **Độ tin cậy**: cao cho Krijnen (đã đọc toàn văn); thấp cho phần scan-to-BIM (chỉ tóm tắt).
- **Ngày thực hiện**: 2026-11-10 (claude-02)

| Nguồn | Đầu vào | Dùng voxel để làm gì | Độ phân giải | Cần `IfcSpace`? | Thử nghiệm | Mức đọc |
|---|---|---|---|---|---|---|
| **Krijnen, El-Diraby, Konomi, Attalla 2021** (CIB W78) | IFC (chỉ `IfcSpace` được voxel hoá) | Thermal interface: voxel hoá `IfcSpace`, tô đặc, phát hiện gián đoạn giữa hai nhãn, dựng lưới tam giác, đơn giản hoá, rồi đưa lỗ mở lên; xuất OSM cho OpenStudio/EnergyPlus | thô có chủ ý (hình 6 ghi 0,5 m) "để tự đóng khe do tường đặc" | **Có** ("still depends on explicit IfcSpace elements") | 1 trường học, 21 `IfcSpace` → 20 ô giao diện; mô hình tổng hợp xoay 0–45° | **toàn văn** |
| Voxelization toolkit (opensourceBIM, MIT) | IFC | Hàm: `voxelize`, `traverse` (6/26 liền kề), `exterior`, `fill_volume`, `fill_gaps`, các phép Boolean và hình thái học, `segment`, `mesh`; ứng dụng liệt kê gồm tính thể tích, khoảng cách thoát nạn | không nêu | không nêu | không có số liệu | trang GitHub (clone thất bại); **chưa kiểm chứng hàm có sinh space** |
| **VOX2BIM+** (Martens & Blankenbach, PFG 91:4, 2023, DOI 10.1007/s41064-023-00243-1) | đám mây điểm trong nhà | Tách tầng bằng mặt cắt ngang ước từ lưới voxel; **tách phòng bằng toán tử hình thái học trên lưới voxel**; xuất IFC (tường) | chưa rõ | không (đầu vào là điểm) | chưa rõ | chỉ tóm tắt; trang tạp chí chuyển hướng sang đăng nhập nên chưa đọc |
| Cloud2BIM (arXiv 2503.11498) | đám mây điểm | Tách phòng theo bề mặt tường; xuất IFC | chưa rõ | không | chưa rõ | tóm tắt bên thứ ba |
| Đề xuất OSArch (voxel hoá rồi trừ tường/sàn) | IFC | Gợi ý: voxel hoá phần tử đặc, trừ ra khoang trống | — | không | chưa thử; cảnh báo rò rỉ vì mô hình không kín | diễn đàn |

## Điểm quan trọng từ Krijnen 2021
- Ý tưởng cốt lõi: **voxel hợp lệ về topo theo bản chất** và Boolean đóng kín; phù hợp mô hình thiếu thông tin hoặc lỗi (tác giả nhắc "partial or imperfect scan2bim").
- Chỉ voxel hoá `IfcSpace`, dùng tam giác–hộp giao; **tô đặc** bằng duyệt đồ thị đệ quy từ một điểm chắc chắn ngoài vùng rồi đảo.
- Kết quả: thể tích và diện tích bị **ước lớn** (trung bình thêm nửa voxel mỗi hướng); số ô giao diện ít hơn số `IfcSpace` (20 so với 21) vì space nhỏ gần độ phân giải bị mất; mô hình **xoay chéo** làm diện tích bề mặt tăng tới hệ số √2 ở 45° và tăng số mặt.
- Mục 6, kết luận: *"depends on explicit IfcSpace elements… Further research will be directed at using the voxelization algorithms to geometrically infer the position of spaces"*; hình 9 phác "flood fill, đảo, trừ Boolean", xói mòn hoặc đếm.

## Ghi chú
- Một số con số trong bản PDF bị hỏng ký tự (đọc thiếu chữ số, ví dụ độ phân giải "0. m"); mình theo hình 6 ghi 0,5 m. Chưa kiểm tra bản gốc.

## Nguồn
- [S1] Krijnen et al. 2021: https://eres.scix.net/pdfs/w78-2021-paper-044.pdf — đã đọc toàn văn; trang TU Delft https://repository.tudelft.nl/record/uuid:98ad4f7e-105d-4511-baa8-57a088eb7c51
- [S2] Voxelization toolkit: https://github.com/opensourceBIM/voxelization_toolkit (chỉ trang GitHub)
- [S3] VOX2BIM+: DOI 10.1007/s41064-023-00243-1 (tóm tắt qua kết quả tìm kiếm)
- [S4] Cloud2BIM: https://arxiv.org/html/2503.11498v1 (chỉ kết quả tìm kiếm)
- [S5] OSArch voxel + trừ tường: https://community.osarch.org/discussion/811/ (chỉ kết quả tìm kiếm)

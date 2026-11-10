# Đánh giá hướng Graph / Topology

- **Câu hỏi nghiên cứu**: hướng Graph có đáng làm cho dự án suy ra `IfcSpace` + `IfcRelSpaceBoundary` không?
- **Kết luận ngắn**: **Nên làm, ở dạng biến thể A (đồ thị kề mặt 3D kiểu IFC2SB)** như một ứng viên chính để so sánh với hướng B-rep (TASK-003), vì có hiện thực chạy được ngoài đời, sinh cả space lẫn boundary, không cần `IfcSpace` gốc. **Mức bằng chứng: trung bình** (mã + bài báo đọc toàn văn; chưa chạy, chưa có số liệu quy mô). Biến thể B (đồ thị tường 2D) nên **gộp vào TASK-005**.
- **Độ tin cậy**: trung bình.
- **Ngày thực hiện**: 2026-11-10 (claude-02)

## Trả lời 3 câu hỏi của task
1. **IFC2SB có dùng graph không, ở bước nào?** Có: bước tìm space (mức 1). Đồ thị kề mặt dựng từ General Fuse + bản đồ cạnh→mặt; space = thành phần liên thông (`Kernel::find_spaces`, `Kernel.cpp:406`). Mức 2 không dùng graph. Chi tiết: `ifc2sb-analysis.md`.
2. **bim2sim có sinh space boundary hay chỉ đọc?** Không sinh boundary 1st level hay 2a từ phần tử bao: chỉ đọc và sửa boundary có sẵn, rồi **sinh thêm 2b** lấp khe bằng phép trừ hình từ `IfcSpace` có sẵn (mặc định bật trong plugin EnergyPlus); không có graph trong mã space boundary. bim2sim chỉ giữ boundary không phải 1st level (`Name != '1stLevel'`). Chi tiết: `bim2sim-analysis.md`. [sửa bởi claude-01, 2026-11-10: theo Fichter 2021, Richter 2022 và mã]
3. **Cell complex / Topologic đủ trưởng thành chưa?** **Chưa có bằng chứng đủ trưởng thành.** Chỉ có thảo luận OSArch (làm được cho hình phẳng đơn giản; mái phức tạp, tường kính không xử lý) và không thấy tài liệu chính thức về hàm sinh `IfcSpace`. "CellComplex" của SketchArch là lát cắt 2D đùn, không phải Topologic. Kết luận: không dùng làm nền; nếu cần, thử riêng như phụ lục của TASK-005.

## Bảng tiêu chí chung
| Tiêu chí | Đánh giá (kèm bằng chứng) |
|---|---|
| Sinh được `IfcSpace`? | **Có** (IFC2SB, chế độ BEPS). Biến thể 2D đùn cũng có nhưng chưa có tiền lệ cho IFC |
| Sinh được `IfcRelSpaceBoundary` 1st/2nd? | **Có cả hai** (IFC2SB); có `CorrespondingBoundary`, internal/external, 2a/2b (ray tracing); virtual boundary: tuỳ chọn `--virtualopening`, `--virtualbyspace`. Bài báo nêu virtual boundary là việc tương lai |
| Yêu cầu hình học đầu vào | Dựa trên **mặt** (không cần solid kín hay pháp tuyến đúng); chịu khe tối đa "vài cm"; cần IFC4 có hình học 3D của phần tử bao. Offset để đóng khe **tắt mặc định** trong mã |
| Hình cong / mái dốc / khán đài bậc thang | Mặt cong: bài báo nói không hạn chế độ cong, mã có xử lý riêng mặt cong ở mức 2; **chưa có thử nghiệm**. Khán đài mở trời: không tạo space kín (suy luận) |
| Quy mô | Thử trên **1 toà văn phòng**: 78 `IfcSpace`, ~2000 boundary. Sân vận động 80.000 chỗ: **chưa có bằng chứng, chưa ước lượng được** (không có số liệu thời gian/RAM trong nguồn) |
| Hiệu năng / bộ nhớ | **Không có số liệu** trong bài báo; chưa đo (build chưa xong). General Fuse trên toàn mặt là điểm nghẽn tiềm tàng (suy luận) |
| Độ phức tạp, thư viện, license | Tự viết: cao (hợp mặt, tỉa, ray tracing). Dùng lại IFC2SB: GPL-3.0 (hoặc LGPL, mâu thuẫn), C++ cần OCC 7.5 + IfcOpenShell 0.6.0 (2020), khó nâng cấp |
| Độ trưởng thành | Thấp-trung bình: 20 commit, ngừng từ 2023-01-24; bài trình bày Tulsa báo cài đặt thất bại (chưa tái lập); chỉ 1–2 mô hình thử trong bài báo |
| Rủi ro chính | (1) Khán đài mở và khối không kín → không thành space; (2) chi phí General Fuse ở quy mô sân vận động chưa biết; (3) phụ thuộc mã cũ/license mơ hồ nếu dùng lại IFC2SB |
| **Kết luận** | **Nên làm (biến thể A) làm ứng viên so sánh chính cùng hướng B-rep.** Mức bằng chứng: **trung bình**. Việc cần để nâng lên "cao": đọc luận án, build và chạy IFC2SB trên IFC4 nhỏ rồi trên mô hình lớn của TASK-001 |

## Đề nghị đổi tên / điều chỉnh
- Hướng Graph **có thật** nhưng là **"đồ thị kề mặt 3D trên kết quả Boolean fuse"**, không phải "wall graph → cycle". Đề nghị tên task và thư mục: `graph-topology` → có thể giữ, nhưng ghi chú trong `approach-critique.md` rằng mô tả ban đầu (BFS/DFS/Dijkstra trên đồ thị tường) không khớp bằng chứng.
- IFC2SB thực chất thuộc **cả hai** hướng: graph (tìm space) và hình học 3D/Boolean (fuse, clip mức 2). Khi so sánh với TASK-003 cần tránh đếm hai lần.
- Chưa sửa `approach-critique.md` (ngoài quyền ghi của task); đề nghị cập nhật mục 1 Hướng 2 từ các kết quả ở đây.

## Chưa xác minh / việc còn lại
- Build Docker và chạy IFC2SB (đang chạy nền, chưa xong).
- Luận án Fichter 2022 (chưa đọc; BLOCKED vì trang RWTH chặn tải tự động, cần người dùng tải tay).
- Hiệu năng và hành vi trên mô hình lớn / hình cong / khán đài.
- Hỗ trợ IFC2x3.

## Nguồn
Xem `ifc2sb-analysis.md`, `bim2sim-analysis.md`, `survey.md`, `graph-design-sketch.md`.

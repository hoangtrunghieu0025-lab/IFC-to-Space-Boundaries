# Khảo sát hướng Graph / Topology

- **Câu hỏi nghiên cứu**: những dự án và bài báo nào thuộc hướng "graph/topology" để suy ra `IfcSpace` và sinh `IfcRelSpaceBoundary`?
- **Kết luận ngắn**: bằng chứng cho hướng này **hẹp nhưng thật**: một nguồn gốc học thuật (van Treeck & Rank, 2007), một hiện thực mã nguồn mở (IFC2SB), và vài nỗ lực ở mức diễn đàn (Topologic) hoặc là lát cắt 2D (SketchArch) chứ không phải graph. bim2sim **không** thuộc hướng này.
- **Độ tin cậy**: trung bình. Mục đã đọc mã/toàn văn được ghi rõ; còn lại chỉ thấy snippet.
- **Ngày thực hiện**: 2026-11-10 (claude-02)

| Mục | Loại | Năm | Ngôn ngữ | License | Bảo trì | Sinh `IfcSpace`? | Boundary | Dùng graph? | Mức đọc |
|---|---|---|---|---|---|---|---|---|---|
| **IFC2SB** (RWTH E3D, Fichter) | công cụ + luận án | 2021–2022 | C++ | GPL-3.0 (LICENSE) / LGPL (badge) | commit cuối 2023-01-24 | **Có** | 1st + 2nd | **Có**: đồ thị kề mặt từ General Fuse; space = thành phần liên thông | mã + bài IBPSA đọc toàn văn; luận án chưa đọc |
| van Treeck & Rank 2007, *Dimensional reduction of 3D building models using graph theory…* (*Engineering with Computers* 23(2):109–122, DOI 10.1007/s00366-006-0053-7 theo danh mục CBIP) | bài báo | 2007 | n/a | n/a | n/a | Có (phát hiện không gian) | 1st (bài IBPSA nói) | **Có**: edge-face graph từ phép Boolean giữa các solid | chỉ qua mô tả trong bài IBPSA; **chưa mở bài gốc**; nơi đăng chưa xác minh |
| **bim2sim** (BIM2SIM; cùng dự án với IFC2SB) | công cụ Python | tới 2026 | Python | LGPL-3.0 | commit 2026-04-14 | Không (dùng `IfcSpace` có sẵn) | Đọc + sửa + sinh 2B (chỉ giữ boundary không phải `1stLevel`) | **Không** trong mã space boundary | mã đọc |
| **FreeCAD_SketchArch** `DetectRoom` | add-on FreeCAD | tới 2026 | Python | LGPL-2.1 | commit 2026-10-03 | Có (dạng khối đùn từ lát cắt sketch) | Không | **Không**: `BOPTools.SplitAPI.slice` chia hộp bao theo cạnh sketch rồi đùn `FloorHeight` | mã đọc (`ArchSketchObject.py:399-417`) |
| **Topologic / Homemaker** (OSArch) | thư viện + thảo luận | ~2019–2023 | C++/Python | chưa xác minh | chưa xác minh | Có thể cho hộp phẳng đơn giản | Có thể (liên hệ tường–space) | CellComplex (topo ô); không phải graph kiểu IFC2SB | chỉ diễn đàn; **chưa có tài liệu chính thức xác nhận chức năng IfcSpace-từ-tường** |
| Jones et al. 2013 (view factors) | bài báo | 2013 | n/a | n/a | n/a | Có (tìm space) | n/a | Không (ray–face) | chỉ qua mô tả trong bài IBPSA |

## Ba biến thể graph theo nhận định của CBIP (Lilis 2017)
CBIP tự nhận là "graph-less" và nêu 3 phương pháp dùng đồ thị: (1) van Treeck & Rank: nút = mặt của B-rep, cạnh = cạnh chung giữa mặt; (2) Rose & Bazjanac: nút = mặt biên chung space–phần tử và các phần tử giữa chúng, cạnh = đường truyền nhiệt khả dĩ; (3) Jones et al.: nút = đa giác phần tử, cạnh = quan hệ "nhìn thấy nhau" theo hệ số hình dạng. Chỉ (1) và (3) không cần `IfcSpace`. Chi tiết: `../brep-3d-reconstruction/boundary-generation-analysis.md`.

## Ghi chú theo mục
- **IFC2SB**: xem `ifc2sb-analysis.md`.
- **bim2sim**: xem `bim2sim-analysis.md`.
- **SketchArch**: tên "CellComplex" ở đây là một compound các khối đùn từ miền 2D của sketch, **không phải** `CellComplex` của Topologic. Thuộc hướng "lát cắt mặt bằng" (TASK-005), không phải graph.
- **Topologic**: nhận xét trên OSArch: làm được "cho nhiều trường hợp" nhưng mái phức tạp và tường kính không xử lý; và có người nhận xét suy space từ tường bao "doesn't work well". [S5] BlenderBIM có tính năng sinh space từ tường chọn (thực chất là dấu chân 2D đùn). Không tìm thấy ghi chú phát hành topologicpy xác nhận hàm sinh `IfcSpace`.
- Trong bài IBPSA 2021, bảng 1 so sánh 5 thuật toán trước (Tre07, Jon13, Ros13, Lad16, Lil16): **chỉ Tre07 và thuật toán đề xuất dùng edge-face graph**; Lad16, Lil16, Ros13 dùng clip/chiếu đa giác. Điều này cho thấy graph là một nhánh thiểu số so với hình học 3D (TASK-003).

## Nguồn
- [S1] https://github.com/RWTH-E3D/IFC2SB (đã đọc mã)
- [S2] https://github.com/BIM2SIM/bim2sim (đã đọc mã)
- [S3] https://github.com/paullee0/FreeCAD_SketchArch — clone `e81620a893` (2026-10-03), `ArchSketchObject.py` (đã đọc)
- [S4] https://publications.ibpsa.org/proceedings/bs/2021/papers/bs2021_30156.pdf — Fichter et al. 2021 (đã đọc toàn văn)
- [S5] https://community.osarch.org/discussion/811/ (chỉ thấy qua kết quả tìm kiếm, chưa mở)

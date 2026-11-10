# Ghi chú quy mô và hiệu năng cho hướng B-rep 3D

- **Câu hỏi nghiên cứu**: hướng B-rep 3D đã được thử ở quy mô nào; điểm nghẽn là đâu; thư viện hình học nào phù hợp; có kỹ thuật tăng tốc nào?
- **Kết luận ngắn**: **không có số liệu thời gian hay bộ nhớ** trong bất kỳ bài nào đã đọc (ASG, CBIP, IFC2SB). Quy mô đã thử: 1–2 toà nhà vài tầng, tối đa 11 tầng (Torre Turina); Ying & Lee 2021 nói "large-scale" nhưng chưa đọc được con số. Khẳng định về sân vận động 80.000 chỗ **không có bằng chứng**.
- **Độ tin cậy**: thấp. Phần thư viện chỉ từ tài liệu API và kết quả tìm kiếm.
- **Ngày thực hiện**: 2026-11-10 (claude-02)

## 1. Quy mô đã được thử (theo bài)
| Thuật toán | Mô hình | Quy mô nêu | Thời gian / RAM |
|---|---|---|---|
| ASG (UCL) | Ký túc xá TU Crete, Torre Turina | 3 tầng (48 vỏ trong); 11 tầng | không nêu |
| CBIP (UCL) | Technical Services, TU Crete | 2 tầng, 514 boundary mức 2 | không nêu |
| IFC2SB (RWTH) | Toà văn phòng KIT | 78 `IfcSpace`, ~2000 boundary | không nêu |
| Ying & Lee 2021 | 2 mô hình thực "large-scale" | chưa rõ | chưa rõ |
Mọi con số trên là từ bài; không có phép đo của mình.

## 2. Điểm nghẽn có thể (suy luận từ mô tả thuật toán; **chưa đo**)
- **ASG** kiểm mọi cặp B-rep ("All possible B-rep pair combinations… tested"): số cặp tăng theo bình phương số phần tử nếu không lọc. Mỗi cặp lại so từng đoạn thẳng của hai khung dây (`Fce`: hai vòng lặp lồng nhau).
- **CBIP** tạo cây BSP cho mỗi đa diện và cắt từng cặp; chi phí phụ thuộc số mặt.
- **IFC2SB** fuse toàn bộ mặt cùng lúc (General Fuse); OCCT cung cấp tuỳ chọn song song, OBB (hộp bao định hướng), glue, fuzzy (`BOPAlgo_Builder`/`BRepAlgoAPI_BuilderAlgo`). Mã IFC2SB bật song song và OBB, không bật glue. [S1]
- Facet hoá vật cong (bắt buộc ở CBIP và ASG) làm **số mặt tăng** với sân vận động nhiều mặt cong.

## 3. Thư viện hình học
| Thư viện | Thấy gì | Giới hạn/cảnh báo (nguồn) |
|---|---|---|
| **OpenCASCADE (OCCT)** | `BOPAlgo_Builder` (General Fuse) và `BRepAlgoAPI_BuilderAlgo`: có song song, OBB, glue (tăng tốc khi các đối số không chồng lấn), fuzzy, non-destructive [S1]. Dùng bởi IFC2SB, IfcOpenShell | Không có số đo hiệu năng trong tài liệu API; mặc định OBB chưa xác minh |
| **IfcOpenShell** | Cung cấp hình học IFC thành OCCT shape (IFC2SB dùng v0.6.0) | Phiên bản cũ 2020; dùng bản mới cần kiểm tra tương thích |
| **CGAL Nef polyhedra** | Chính xác, mạnh | Chậm; cần kernel chính xác (kết quả tìm kiếm; ghi nhận bên thứ ba) [S2] |
| **trimesh** | Boolean qua `manifold3d` hoặc Blender; `check_volume` đòi lưới kín | Boolean trên lưới thường chậm và kém tin cậy (ghi chú gói) [S3] |
| **manifold3d** | Tuyên bố nhanh, đảm bảo đầu ra manifold, song song | Cần lưới manifold; không thấy thử trên IFC [S3] |
| **Clipper** (Angus Johnson) | 2D hợp/giao/hiệu đa giác (Vatti); ASG và IFC2SB dùng | Chỉ 2D, trên mặt phẳng đồng phẳng |
Không có thư viện nào được đo trên mô hình lớn trong nghiên cứu này.

## 4. Kỹ thuật tăng tốc đã thấy trong nguồn
- OCCT: `SetRunParallel`, `SetUseOBB`, glue (IFC2SB dùng hai đầu). [mã IFC2SB]
- ASG: ngắt vòng lặp ngay khi tìm thấy cạnh chung (`Fce` dừng sớm), song song hoá bằng `p_thread` là việc tương lai. [ASG]
- IFC2SB: R-tree (header-only) dùng trong mã; octree trong thư mục `src/octree`. Không rõ dùng ở bước nào (chưa đọc).
- **Chưa có nguồn xác nhận** cách chia theo tầng hoặc theo khối rồi ghép: đây là đề xuất của người viết, cần thử trên mô hình L của TASK-001.

## 5. Việc nên làm để có số liệu thật
- Chạy IFC2SB đã build (TASK-002) trên IFC nhỏ rồi trên mô hình lớn nhất trong `samples/manifest.yaml`, ghi số phần tử, số mặt, thời gian, RAM.
- Cài lại ASG hoặc CBIP bằng Python (pythonocc hay Shapely) trên cùng bộ để so sánh.

## Chưa xác minh / việc còn lại
- Toàn văn Ying & Lee 2021 (số liệu hiệu năng).
- Mặc định `SetUseOBB` trong OCCT 7.5.x.
- Kết quả đo thực: chưa có.

## Nguồn
- [S1] OCCT API: https://dev.opencascade.org/doc/refman/html/classBOPAlgo__Builder.html và https://dev.opencascade.org/doc/occt-7.9.0/refman/html/class_b_rep_algo_a_p_i___builder_algo.html (qua kết quả tìm kiếm, chưa mở)
- [S2] Thảo luận về Nef polyhedra: https://ochafik.com/jekyll/update/2022/02/09/openscad-fast-csg-contibution.html (chỉ kết quả tìm kiếm)
- [S3] trimesh/manifold3d: https://pypi.org/project/trimesh/ ; https://github.com/elalish/manifold (chỉ kết quả tìm kiếm)
- Mã IFC2SB `Kernel.cpp:27` (đọc), ASG/CBIP như trong các file cùng thư mục

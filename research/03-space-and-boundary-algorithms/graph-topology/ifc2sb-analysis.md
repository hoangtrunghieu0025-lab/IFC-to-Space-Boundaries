# Phân tích IFC2SB: graph nằm ở đâu

- **Câu hỏi nghiên cứu**: IFC2SB có dùng graph không, ở bước nào; thuật toán suy ra `IfcSpace` và sinh `IfcRelSpaceBoundary` làm gì; dùng được cho dự án không?
- **Kết luận ngắn**:
  - **Có dùng graph, nhưng không phải "wall graph → cycle".** Graph là **đồ thị kề giữa các mặt (face adjacency graph) của toàn bộ phần tử bao ở dạng 3D**, dựng bằng phép Boolean "General Fuse" của OpenCASCADE rồi tra cạnh chung. `IfcSpace` = **thành phần liên thông (connected component)** của đồ thị đó sau khi tỉa mặt. Đây là phương pháp của van Treeck & Rank (2007) do bài IBPSA 2021 chỉnh lại cho mặt rời.
  - Boundary mức 2 **không dùng graph**: dùng chiếu và cắt mặt (projection + clipping) cộng ray tracing để phân loại 2a/2b.
  - Bằng chứng đến từ **đọc mã nguồn** (commit `96a89cdff6`, 2023-01-24) và **bài báo IBPSA 2021**. Chưa đọc luận án; chưa chạy được chương trình (xem mục 6).
- **Độ tin cậy**: cao cho mô tả kiến trúc thuật toán (mã + bài báo khớp nhau); thấp cho hiệu năng, độ bền, khả năng chạy trên mô hình lớn (chưa có số liệu, chưa tái lập).
- **Ngày thực hiện**: 2026-11-10 (claude-02)

## 1. Thông tin dự án
| Mục | Giá trị | Nguồn |
|---|---|---|
| Repo | https://github.com/RWTH-E3D/IFC2SB ; README ghi nguồn gốc `git.rwth-aachen.de/fichter/ifc2sb` (chưa kiểm tra) | [S1] |
| Tác giả | Eric Fichter, RWTH Aachen E3D; một phần trong dự án BIM2SIM (BMWi 03ET1562A, 05/2018–10/2021) | mã `src/main.cpp`, README |
| Lịch sử | 20 commit, từ 2022-08-25 đến **2023-01-24** (commit cuối `96a89cdff6` "Update README.md"). Không thấy hoạt động sau đó trong bản clone | `git log` |
| Ngôn ngữ / quy mô | C++14, CMake; khoảng 25.100 dòng `.cpp/.h` ở `src/` (không tính `src/viewer`) | `wc -l` |
| Phụ thuộc | OpenCASCADE 7.5.0 (Dockerfile dùng 7.5.3), IfcOpenShell **0.6.0**, Clipper 6.4.2, Boost, libxml2, TBB, Qt5 (cho trình xem SBV); header-only: R-Tree, Triangle, ConvexDecomposition, stl_reader | README, `cmake/CMakeLists.txt`, `add/Dockerfile` |
| License | File `LICENSE` là **GPL v3**; badge trong README ghi **LGPL v3**. Mâu thuẫn; coi như GPL-3.0 cho tới khi làm rõ | `LICENSE`, README |
| Đầu vào | IFC4 có hình học 3D (đặc biệt `IfcBuildingElement`). Mã có nhánh xử lý `IFC2X3` (`Graph.cpp`: `K.ifcSchema == IFC2X3`), README chỉ nêu IFC4: chưa xác minh hỗ trợ IFC2x3 | README, `Graph.cpp` |
| Đầu ra | Chế độ BEPS: IFC4 mới có `IfcSpace` + `IfcRelSpaceBoundary1stLevel` + `2ndLevel` (+ `IfcExternalSpatialElement`); chế độ CFD (`--stl`): STL các khối không khí kín | README, bài IBPSA |
| Tài liệu học thuật | Luận án Fichter 2022 (README trỏ https://publications.rwth-aachen.de/record/856693 ; DOI 10.18154/RWTH-2022-11049 chuyển hướng đúng về trang này. **Trang RWTH chặn tải tự động bằng thử thách JavaScript chống bot nên không đọc được; mình không vượt qua cơ chế đó. Cần người dùng tải tay**); Fichter, Richter, Frisch, van Treeck (2021) | [S2][S3] |

## 2. Luồng xử lý thật (từ `src/Graph.cpp`, hàm `Graph::run`, dòng 108)
1. `prepare_products` (149): đọc IFC bằng IfcOpenShell, lấy hình học `IfcBuildingElement`, opening.
2. `prepare_faces` (304): gom **mọi mặt** của mọi phần tử thành danh sách `oFace`; tuỳ chọn mặt ảo từ IfcSpace; tuỳ chọn mặt "offset"; đưa cửa/cửa sổ vào tường.
3. `calc_faces_first_level` (371): **General Fuse** mọi mặt → `cFace`; kiểm tra; rồi nhánh:
   - mọi pháp tuyến đã biết → `calc_faces_first_level_normals_known` (442);
   - có pháp tuyến chưa biết → `..._normals_unknown` (572).
4. `process_spaces` (663): tìm mặt ngoài cùng ("facade space"), dọn mặt rác, hợp nhất mặt kề, rồi chuyển space thành vỏ để xuất `IfcSpace`.
5. `calc_faces_second_level` (799): chiếu và cắt mặt để ra boundary mức 2; ray tracing xác định 2a/2b và mặt tương ứng.
6. `process_model` (926): **xoá `IfcSpace` và `IfcRelSpaceBoundary` gốc** khỏi mô hình, ghi cái mới; chép GUID và Pset của space cũ sang space mới (`link_old_IfcSpace_data`); xuất IFC.

## 3. Graph: chính xác là gì
**Nút** = mặt phẳng/mặt cong đã tách (`cFace`) sau khi hợp (fuse) tất cả mặt của mọi phần tử. **Cạnh** = hai mặt dùng chung một cạnh hình học.

Các bước, kèm vị trí mã:
| Bước | Mã | Ghi chú |
|---|---|---|
| Hợp mọi mặt | `Kernel::fuse_original_faces`, `Kernel.cpp:27` | `BOPAlgo_Builder` (General Fuse) của OCCT, `SetFuzzyValue(fuzzy_tol)`, `SetRunParallel(true)`, `SetUseOBB(true)`. `fuzzy_tol = 0.0001` đặt cứng ở `Graph.cpp:94` |
| Dựng đồ thị kề | `Kernel::update_face_adjacencies`, `Kernel.cpp:317` | Dùng `TopExp::MapShapesAndAncestors(fuse, EDGE, FACE)` (bản đồ cạnh → mặt), mỗi `cFace` lưu `adjacentfaces` theo cạnh |
| Tỉa theo hướng | `remove_adjacency_by_orientation`, `Kernel.cpp:351` | Bỏ kề sai hướng pháp tuyến |
| Tỉa mặt treo | `identify_hanging_faces`, `Kernel.cpp:363` | Mặt có cạnh không có mặt kề bị loại |
| Tỉa cạnh phi-manifold | `remove_non_manifold_adjacency_by_angle`, `Kernel.cpp:2827` | Khi 1 cạnh có ≥3 mặt, giữ mặt có góc nhỏ hơn (bài báo: "the surface with the smaller angle is selected") |
| **Tìm space** | `Kernel::find_spaces`, `Kernel.cpp:406` | **DFS bằng stack trên đồ thị mặt; mỗi thành phần liên thông thành một `Space`** |
| Pháp tuyến chưa biết | `find_spaces_normals_unknown`, `Kernel.cpp:6663` | Mỗi mặt dùng được tối đa hai lần (hai hướng); duyệt đệ quy tạo các thành phần kín, gom theo thể tích, luật chấp nhận A/B/C ghi trong chú thích mã |
| Mặt ngoài | `identify_facade_space`, `Kernel.cpp:455` | Lấy vỏ ngoài toà nhà làm một space "facade" (liên quan `IfcExternalSpatialElement`) |

Khớp với bài báo: "Boolean intersection of the faces and adjacency evaluation results in an edge-face graph… To find first level SBs… the graph is traversed starting from a randomly selected face, collecting neighbor faces recursively… The search ends with a closed space if no more new faces are found." Kiểm tra sau: space không chồng nhau, pháp tuyến hướng vào trong, mỗi mặt phần tử chỉ dùng một lần. [S3]

**Nguồn gốc ý tưởng**: van Treeck & Rank (2007), "Dimensional reduction of 3D building models using graph theory and its application in building energy simulation" (danh mục của CBIP ghi: *Engineering with Computers* 23(2), 109–122, DOI 10.1007/s00366-006-0053-7. Danh mục của bài IBPSA ghi "Automation in Construction 76", đó là nơi đăng của chính bài CBIP nên có vẻ là nhầm; chưa mở bài gốc). Bài IBPSA chỉnh lại thành phương pháp **hoàn toàn dựa trên mặt**, không cần solid kín hay pháp tuyến đúng. [S3]

## 4. Xử lý lỗi và khe hở
- Bài báo: khe hở ở vỏ hình học **tối đa "vài cm"** không ảnh hưởng thuật toán; khe nhỏ được đóng bằng kéo dài mặt ("face extension"); mặt "offset" vài cm để lấp khe trong và giữa phần tử. [S3]
- **Trong mã phát hành, offset tắt mặc định**: `face_offset_length = 0` (`Graph.cpp:95`) và `main.cpp` **không có tuỳ chọn dòng lệnh** nào để bật. Chỉ sửa mã mới bật được. Khả năng đóng khe thực tế phụ thuộc `fuzzy_tol = 1e-4` và `ShapeHealing`/`ShapeChecker`. Chưa kiểm chứng ảnh hưởng.
- Cửa/cửa sổ: dùng hình học `IfcOpeningElement` thay cho hình chi tiết của cửa; mặt "curtain wall" đơn giản hoá bằng hình chữ nhật bao. [S3]

## 5. Mức 2 và phần phi-graph
- Mức 2: `find_clipping_pairs` + `clip_faces`; khoảng cách tối đa `--length` mặc định 0,41 (phân biệt 2a/2b), ngưỡng góc 95° (`Graph.cpp:806-808`). Không dùng graph. [S1]
- `Topo2D` / `graph_2D.h` (`Point2D`, `Edge2D`) là **đồ thị phẳng 2D** dùng trong `Kernel.cpp` (~4054) để hợp các wire sau khi cắt mặt thành mảnh nhỏ nhất. Chỉ là hạ tầng polygon overlay, **không** dùng để tìm space.
- Tuỳ chọn `--clip` là phương pháp thay thế "only basic structure implemented" (`main.cpp`). Chưa phát triển.
- `IfcSpace` gốc: **không dùng** để sinh boundary mức 1 (bài báo: "IfcSpace geometry should not be used for first level SB generation"). Có tuỳ chọn `--split` (mã ghi "To be deprecated") và `--virtualbyspace` để dùng space gốc tạo boundary ảo.

## 6. Cài đặt và chạy thử (claude-02)
- Máy: Linux, 14 CPU, 15 GB RAM, không có `cmake`, OpenCASCADE, IfcOpenShell; có Docker 29.9.3.
- Dockerfile gốc (`add/Dockerfile`) dựa Ubuntu 20.04, OCC 7.5.3 lấy từ repo bên thứ ba `bimworld/occ`, `qt5-default`; **mình không dùng repo bên thứ ba** mà viết lại Dockerfile lấy OCCT 7.5.3 từ GitHub chính thức `Open-Cascade-SAS/OCCT` (tag `V7_5_3`) và IfcOpenShell tag `v0.6.0`, file ở thư mục scratchpad của phiên (`.../scratchpad/ifc2sb-docker/Dockerfile`).
- Lệnh: `docker build -t ifc2sb-test .` (chạy nền). **Trạng thái tại thời điểm viết: chưa xong**; bước kéo ảnh nền Ubuntu 20.04 chỉ đạt khoảng 19/27 MB sau ~3 phút (mạng chậm), các bước biên dịch OCCT và IfcOpenShell chưa bắt đầu. **Chưa có kết quả cài đặt hay chạy: chưa kiểm chứng.**
- Rủi ro đã biết: bài trình bày ở Univ. of Tulsa báo cài IFC2SB thất bại ("critical failure") trên mô hình RWTH Digital Hub; mình chưa tái lập được. [S4]
- File IFC4 nhỏ để thử: `AC20-FZK-Haus.ifc` được Steptools liệt kê (2,5 MB, IFC4, nguồn KIT), nhưng **chưa tìm thấy URL chính thức của KIT cũng như giấy phép**; nếu dùng chỉ để cục bộ (`samples/corpus_real/`), không commit. Ưu tiên lấy từ kết quả TASK-001.

## 7. Vì sao hợp / không hợp với dự án
| Điểm | Đánh giá |
|---|---|
| Khớp mục tiêu | Rất gần: sinh `IfcSpace` + 1st/2nd level từ phần tử bao, đúng điều `PRIMARY_OBJECTIVE.md` cần |
| Không cần IfcSpace gốc | Có (ưu điểm): suy ra được khi IFC thiếu space |
| Space là vùng **kín** | Mỗi space là thành phần liên thông **kín** của mặt. Bên trong khán đài sân vận động có phần mở ra trời (bowl): suy luận thuật toán sẽ không tạo được space kín ở đó; chỉ còn "facade space". **Đây là suy luận, chưa thử** |
| Quy mô | Một General Fuse trên **toàn bộ mặt toàn công trình**. Bài báo chỉ thử 1 toà văn phòng (78 `IfcSpace`, ~2000 boundary); **không có số liệu thời gian/RAM**. Với sân vận động 80.000 chỗ chưa có bằng chứng |
| Hình cong | Mã dùng `cfaceSetMap M_curved` riêng cho mặt cong ở bước mức 2 và bài báo nói "no restrictions on the curvature"; chưa có thử nghiệm |
| Phụ thuộc cũ | IfcOpenShell 0.6.0 và OCC 7.5 (2020–2021), không bảo trì từ 01/2023; khó nâng cấp |
| License | GPL-3.0 (hoặc LGPL; mâu thuẫn): nếu nhúng vào sản phẩm thì phải làm rõ |

## Chưa xác minh / việc còn lại
- Luận án Fichter 2022 (chi tiết graph, thử nghiệm, hiệu năng): **BLOCKED** vì trang RWTH có thử thách JavaScript chống bot. Nhờ người dùng tải PDF từ https://publications.rwth-aachen.de/record/856693 và đặt vào `samples/corpus_real/` hoặc thư mục cục bộ, rồi agent đọc tiếp.
- Kết quả build Docker và chạy thử trên IFC4 nhỏ; lỗi (nếu có) so với báo cáo của Tulsa.
- IFC2SB có hỗ trợ IFC2x3 không.
- Hành vi trên mô hình lớn, mặt cong, mái dốc; giới hạn khe hở thực tế khi offset tắt.
- Tác động của GPL/LGPL mâu thuẫn.

## Nguồn
- [S1] https://github.com/RWTH-E3D/IFC2SB — clone `96a89cdff6`, đọc `README.md`, `LICENSE`, `src/main.cpp`, `src/Graph.cpp`, `src/Kernel.cpp`, `src/graph_2D.h`, `cmake/CMakeLists.txt`, `add/Dockerfile` (truy cập 2026-11-10)
- [S2] https://publications.rwth-aachen.de/record/856693 — trang luận án; DOI chuyển hướng đúng (truy cập 2026-11-10); nội dung bị chặn bởi thử thách JavaScript, chưa đọc
- [S3] Fichter, Richter, Frisch, van Treeck (2021), *Automatic generation of second level space boundary geometry from IFC models*, IBPSA BS2021. https://publications.ibpsa.org/proceedings/bs/2021/papers/bs2021_30156.pdf (đã đọc toàn văn, 2026-11-10)
- [S4] B. Golla, Univ. of Tulsa: https://www.ucd.ie/eleceng/t4media/Benjamin-Golla_University-of-Tulsa.pdf (chỉ thấy qua kết quả tìm kiếm, chưa mở)

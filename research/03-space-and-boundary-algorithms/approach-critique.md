# Phản biện các hướng tiếp cận suy ra IfcSpace và sinh IfcRelSpaceBoundary

- **Câu hỏi nghiên cứu**: 4 hướng do người dùng đề xuất (Polygonization, Graph/Topology, Adjacency, Rule-based) có thật sự là hướng thị trường/nghiên cứu đang theo không? Còn hướng nào khác có bằng chứng?
- **Kết luận ngắn**:
  - Không hướng nào trong 4 hướng đúng hoàn toàn như mô tả ban đầu; mô tả về FreeCAD, BIM2SIM và IFC2SB có chỗ chưa xác minh hoặc sai.
  - Hướng chủ đạo trong văn liệu về 2nd-level boundary là **hình học 3D (B-rep, boolean/giao mặt)** và **voxel**, không phải graph.
  - **Quyết định của người dùng (2026-11-10): giữ lại hướng Graph** để nghiên cứu, dù chưa có bằng chứng cho nó; task Graph phải bắt đầu bằng việc xác minh IFC2SB thật sự làm gì.
- **Độ tin cậy**: trung bình-thấp. Mỗi ý dựa trên 1 lượt tìm, đọc snippet/README; **chưa đọc toàn văn** các bài báo và luận án. Mục "Chưa xác minh" liệt kê rõ phần còn hở.
- **Ngày thực hiện**: 2026-11-10

## 1. Đánh giá 4 hướng ban đầu

### Hướng 1 — Polygonization / Geometry Reconstruction
Mô tả ban đầu: Wall → polygon kín → IfcSpace → Boundary; học từ FreeCAD BIM, IfcOpenShell.

| Khẳng định | Kết quả kiểm tra |
|---|---|
| "FreeCAD đã có logic Wall enclosure → Space" | **Không đúng với lõi.** `Arch Space` yêu cầu người dùng chọn mặt tường thủ công (`Arch.addSpaceBoundaries`); thể tích tính từ bounding box của các mặt rồi trừ phần phía sau từng mặt. [W1] |
| Tự phát hiện phòng trong FreeCAD | Chỉ có ở add-on thử nghiệm FreeCAD_SketchArch (thuộc tính `Detect Room` trên ArchSketch, CellComplex). Có người dùng báo không thấy toggle trên ArchWall (2022). Chưa kiểm tra trạng thái hiện tại. [W2][W3] |
| "IfcOpenShell lấy BRep/Mesh rồi tự viết polygonization" | Hợp lý về kỹ thuật (IfcOpenShell cung cấp hình học), nhưng chưa tìm thấy dự án nào làm đúng việc này để đối chứng. Chưa xác minh. |
| Ví dụ DXF → Shapely polygonize | Thuộc CAD→BIM, **ngoài phạm vi** (`PRIMARY_OBJECTIVE.md` mục 4). Với IFC, biến thể phù hợp là lát cắt mặt bằng theo tầng. |

### Hướng 2 — Graph / Topology Analysis (GIỮ LẠI)
Mô tả ban đầu: Wall → Graph → Cycle → Space → Boundary; IFC2SB và BIM2SIM là nguồn học chính; "không dùng AI, dùng connectivity/adjacency/enclosure detection".

| Khẳng định | Kết quả kiểm tra |
|---|---|
| IFC2SB là dự án gần mục tiêu nhất | **Đúng.** Ở chế độ BEPS nó xuất IFC4 với `IfcSpace` mới + `IfcRelSpaceBoundary1stLevel` + `2ndLevel`; chế độ CFD xuất STL các khối không khí kín. Tác giả Eric Fichter, RWTH E3D. [W4][W5] |
| IFC2SB dùng topology/graph, connectivity, enclosure detection | **Chưa xác minh.** README không mô tả thuật toán, trỏ tới luận án. Thư viện: OpenCASCADE 7.5.0, IfcOpenShell 0.6.0, Clipper 6.4.2 (cắt/offset polygon), Triangle (mesh), ConvexDecomposition, R-Tree. Nhìn vào đó thì giống xử lý hình học 3D/mesh hơn graph thuần. Có cờ `--graph` nhưng chưa rõ vai trò. [W4] |
| IFC2SB không dùng AI | Không thấy dấu hiệu dùng AI trong README (C++/CMake), nhưng README không mô tả phương pháp, nên mới là suy luận. |
| BIM2SIM có "Topology Graph → Space Graph → Boundary Graph" | **Không tìm thấy bằng chứng.** Bằng chứng ngược lại: bim2sim yêu cầu IFC4 **đã có** 2nd-level space boundary và khuyên bật tuỳ chọn export ở phần mềm gốc; nó là bên tiêu thụ boundary, không phải bên sinh. [W6] Cần đọc mã nguồn bim2sim để kết luận. |
| Độ trưởng thành của IFC2SB | Rủi ro: README ghi license không nhất quán (GPL-3.0 ở sidebar, badge LGPL v3); một bài trình bày ở Univ. of Tulsa báo cài IFC2SB thất bại ("critical failure") trên mô hình RWTH Digital Hub. Chưa tái lập. [W4][W7] |
| "Rất ít repo đi sâu IfcRelSpaceBoundary" | **Phù hợp** với văn liệu: bài Krijnen 2021 nhận định rất ít giải pháp sinh space boundary đầu-cuối. [W8] |
| Văn liệu nghiêng về graph? | **Không.** CBIP (Lilis 2017) dùng B-rep và cây BSP, nêu rõ "not graph-based". [W9] |

Vì sao vẫn giữ: người dùng quyết định giữ; IFC2SB là dự án mã nguồn mở duy nhất tìm được sinh cả `IfcSpace` lẫn 1st/2nd-level boundary; và có thể `--graph` / luận án có phần graph chưa đọc được. **Task Graph phải bắt đầu bằng việc đọc luận án và mã IFC2SB để xác định graph được dùng ở đâu**, nếu hướng này hoá ra không phải graph thì ghi rõ và đổi tên task cho đúng.

### Hướng 3 — Indoor Navigation / Space Adjacency
- ifc2indoorgml (Diakite et al., ISPRS 2022, C++) **lấy các `IfcSpace` đã có** làm ô LCC của IndoorGML; không sinh space. [W10]
- Kết luận: **không phải hướng giải bài toán sinh**, mà là bước sau (digital twin, wayfinding). Dùng làm use case và cách kiểm chứng (đồ thị kề giữa các space suy ra có hợp lý không).
- Chưa xác minh: cách ifc2indoorgml suy adjacency qua cửa (snippet không nói).

### Hướng 4 — Rule-based Semantic BIM
- Là gán loại phòng từ layer/text của CAD (hoặc luật hình học); đã loại khỏi phạm vi (CAD→IFC, nhận dạng chức năng phòng).
- Không tìm thấy bằng chứng cho tuyên bố về FreeCAD/BlenderBIM ở hướng này. Chưa xác minh.
- Kết luận: tạm gác. Chỉ quay lại nếu cần gán `Name`/`PredefinedType` cho `IfcSpace` suy ra.

## 2. Hướng có bằng chứng nhưng chưa nằm trong 4 hướng

| Hướng | Bằng chứng | Ghi chú |
|---|---|---|
| **A. Dựng lại thể tích space từ hình học 3D của phần tử bao** | UCL (Lilis, Katsigarakis, Rovas, 2021): thuật toán tự sinh space, chạy khi IFC thiếu space hoặc space lỗi, xử lý tốt tường cong, **cần hình học đầu vào sạch** (không clash/lỗi bề mặt) và đề ra tiêu chí kiểm tra lỗi. [W11] Ying & Lee (2021): kết hợp 3 dạng biểu diễn hình học để xử lý công trình lớn, chịu được IFC chất lượng thấp hơn, xử lý hình cong; báo kết quả trên 2 mô hình thực lớn. [W12] CBIP (Lilis 2017): sinh 2nd-level boundary từ polyhedron, B-rep + BSP, cần định nghĩa đủ thể tích không khí của space. [W9] | Liên quan nhất tới sân vận động. Chưa có bài nào được thấy thử trên sân vận động. Phương pháp chi tiết của bài UCL **chưa đọc** (mới đọc phần giới thiệu). |
| **B. Voxel hoá** | Krijnen, El-Diraby, Konomi, Attalla (CIB W78 2021): dựng thermal interface từ IFC bằng voxel, đánh đổi độ chính xác lấy độ bền với mô hình lỗi, xuất OSM cho OpenStudio/EnergyPlus; tự phát hiện space từ voxel là việc tương lai. [W8][W13] Đề xuất voxel rồi trừ tường/sàn trên OSArch, cảnh báo rò rỉ giữa các space vì mô hình thực hiếm khi kín. [W14] | Với sân vận động 80.000 chỗ, bộ nhớ/độ phân giải có thể là vấn đề: **đây là suy luận, chưa có số liệu**. |
| **C. Cell complex (Topologic)** | Thảo luận OSArch về sinh IfcSpace từ tường/sàn/mái bằng Topologic; một người dùng nhận xét suy space từ tường bao là làm được nhưng "không chạy tốt". SketchArch dùng CellComplex. [W2][W14] | Chỉ mức diễn đàn/add-on thử nghiệm; bằng chứng yếu. Gần hướng Graph nhất về mặt topology; nên xem cùng task Graph. |
| **D. Kiểm tra/sửa IFC đã có trước khi sinh** | Revit và ArchiCAD có tuỳ chọn export space boundary nhưng nhiều người báo file ra thiếu hoặc rỗng (Revit: tuỳ chọn None/1st/2nd; ArchiCAD: bật là luôn xuất 2nd-level). [W15][W16] OSArch: Revit xuất 2nd-level từ phòng kín, mô hình dựng bằng Dynamo thì không. [W17] | Là bằng chứng bài toán có thật. Gợi ý pipeline có bước đánh giá IFC đầu vào (đã có gì, sai ở đâu) trước khi sinh. |
| E. Deep learning | Tìm scan-to-BIM cho thấy tách phòng chủ yếu vẫn là hình học cổ điển (voxel, khe tường, ô 2D); DL chủ yếu để gán nhãn tường/cửa. [W18] | Không có bằng chứng để đề xuất hướng AI. Đầu vào scan cũng khác đầu vào IFC của dự án. |

## 3. Đề xuất cấu trúc task nghiên cứu (chưa tạo task)
1. **Graph / Topology** (giữ theo quyết định người dùng): xác minh IFC2SB (luận án, mã, `--graph`, license, tái lập cài đặt) và BIM2SIM; kèm hướng C (cell complex).
2. **Dựng thể tích 3D từ B-rep** (hướng A): UCL, Ying & Lee, CBIP.
3. **Voxel** (hướng B): Krijnen và các biến thể.
4. **Lát cắt mặt bằng theo tầng + polygonize** (hướng 1 làm lại cho IFC): mức cơ sở nhẹ nhất để so sánh.
5. Adjacency (hướng 3) và đánh giá IFC đầu vào (hướng D) đưa vào task kiểm chứng (`research/04-datasets-and-validation/`).
6. Hướng 4 (rule-based) tạm gác.

## Chưa xác minh / việc còn lại
- Thuật toán thật của IFC2SB (luận án của tác giả; mã nguồn); vai trò cờ `--graph`; license thực tế; trạng thái bảo trì và ngày commit cuối.
- Cách bim2sim xử lý space boundary thiếu/sai; có hay không bước graph.
- Phương pháp chi tiết và kết quả của bài UCL (Lilis et al. 2021) và Ying & Lee 2021; mô hình thử nghiệm của họ có công trình quy mô sân vận động không.
- Trạng thái hiện tại của `Detect Room` trong FreeCAD_SketchArch.
- Cách ifc2indoorgml suy adjacency qua cửa.
- Số liệu bộ nhớ/thời gian của voxel và B-rep trên mô hình rất lớn.

## Nguồn
Tất cả truy cập 2026-11-10. Phần lớn chỉ đọc snippet kết quả tìm kiếm hoặc README; chỉ mục có ghi "đã đọc" là mở trực tiếp trang.
- [W1] [FreeCAD — Arch Space](https://wiki.freecad.org/Arch_Space)
- [W2] [FreeCAD_SketchArch (paullee0)](https://github.com/paullee0/FreeCAD_SketchArch)
- [W3] [OSArch — FreeCAD: No "Detect Room" attribute for an ArchWall](https://community.osarch.org/discussion/900/)
- [W4] [RWTH-E3D/IFC2SB (README, đã đọc)](https://github.com/RWTH-E3D/IFC2SB)
- [W5] [Mirror IFC2SB; ghi nguồn gốc git.rwth-aachen.de/fichter/ifc2sb (chưa kiểm tra)](https://github-users.yhajoa.workers.dev/RWTH-E3D/IFC2SB)
- [W6] [bim2sim — Discussion #498](https://www.github.com/BIM2SIM/bim2sim/discussions/498)
- [W7] [B. Golla, Univ. of Tulsa — thử BIM2SIM và IFC2SB](https://www.ucd.ie/eleceng/t4media/Benjamin-Golla_University-of-Tulsa.pdf)
- [W8] [Krijnen et al. 2021, CIB W78 paper 044](https://eres.scix.net/pdfs/w78-2021-paper-044.pdf)
- [W9] [Lilis et al. 2017, Automatic generation of second-level space boundary topology from IFC geometry inputs](https://www.bohrium.com/paper-details/automatic-generation-of-second-level-space-boundary-topology-from-ifc-geometry-inputs/811090191052701697-3774)
- [W10] [ifc2indoorgml (Diakite et al., ISPRS 2022)](https://ual.sg/post/2022/06/05/ifc2indoorgml-an-open-source-tool-for-generating-indoorgml-from-ifc/)
- [W11] [Lilis, Katsigarakis, Rovas — Automatic IFC data enrichment with space geometries for BEPS (UCL, 2021; chỉ đọc phần giới thiệu)](https://discovery.ucl.ac.uk/id/eprint/10169911/1/bs2021_30888.pdf)
- [W12] [Ying & Lee 2021 — Generating second level space boundaries from large scale IFC-compliant BIM](https://pure.uos.ac.kr/en/publications/generating-second-level-space-boundaries-from-large-scale-ifc-com/)
- [W13] [TU Delft — Thermal analysis of IFC building models using voxelized geometries](https://repository.tudelft.nl/record/uuid:98ad4f7e-105d-4511-baa8-57a088eb7c51)
- [W14] [OSArch — Topologic: automatically create IfcSpaces from IfcWall/IfcSlab/IfcRoofs](https://community.osarch.org/discussion/811/)
- [W15] [Autodesk forum — Exporting IFC files with space boundaries is not working as desired](https://forums.autodesk.com/t5/revit-architecture-forum/exporting-ifc-files-with-space-boundaries-is-not-working-as/m-p/10394997)
- [W16] [Graphisoft — Export 1st Level Space Boundaries to IFC instead of 2nd Level](https://community.graphisoft.com/t5/Collaboration-with-other/Export-1st-Level-Space-Boundaries-to-IFC-instead-of-2nd-Level/m-p/273145)
- [W17] [OSArch — nhận xét về Revit vs Dynamo](https://community.osarch.org/discussion/comment/16352/)
- [W18] [Gourguechon, Macher, Landes — Automation of as-built BIM creation from point clouds (ISPRS 2022)](https://isprs-archives.copernicus.org/articles/XLIII-B2-2022/193/2022/)

## Câu hỏi còn mở
- Giữ Graph như hướng riêng hay gộp với Cell complex sau khi đọc luận án IFC2SB?
- Ngưỡng nào thì coi "hình học đầu vào đủ sạch" để chạy hướng A (UCL đề ra tiêu chí lỗi; cần lấy ra)?
- Có IFC sân vận động đủ lớn để thử các hướng không (xem TASK-001)?

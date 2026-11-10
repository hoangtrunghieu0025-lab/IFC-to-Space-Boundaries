> **Báo cáo thô** của subagent hỗ trợ claude-01 (TASK-001), ngày 2026-11-10, chép nguyên văn từ scratchpad để lưu vết. Đường dẫn `/tmp/…/scratchpad/…` và `dl/`, `dl2/`, `scripts/` nhắc trong báo cáo là thư mục tạm của phiên, **không còn tồn tại**. Bản tổng hợp đã kiểm lại: `../dataset-survey.md`, `../dataset-search-log.md`.

# Khảo sát nguồn CAD và dataset floor plan (hỗ trợ TASK-001)

- Ngày truy cập: 2026-11-10 cho mọi nguồn bên dưới.
- Phạm vi dự án: suy ra IfcSpace và sinh IfcRelSpaceBoundary từ IFC. Tạo IFC từ CAD/ảnh nằm NGOÀI phạm vi. Vì vậy các nguồn dưới đây chỉ có thể làm **dữ liệu tham khảo/đối chiếu**, không làm đầu vào chính.

## Cách kiểm tra (quan trọng cho độ tin cậy)

Container chỉ đi được tới `raw.githubusercontent.com` và `github.com`. WebFetch tới zenodo.org, staff.ustc.edu.cn, structured3d-dataset.org, grabcad.com, ustc-gcl-f.github.io đều báo lỗi `ENOTFOUND` hoặc `connect_rejected`. Do đó có 3 mức kiểm chứng:

- **[ĐÃ MỞ]**: đã đọc trực tiếp file gốc (README/LICENSE trên GitHub qua raw.githubusercontent.com hoặc WebFetch github.com).
- **[SNIPPET]**: chỉ thấy qua đoạn trích của WebSearch, chưa mở trang gốc. Coi là "chưa xác minh đầy đủ".
- **[CHƯA XÁC MINH]**: không tìm được bằng chứng.

## Bảng 1: Nguồn CAD/DXF/DWG

| Tên | Nhóm | URL chính thức | Giấy phép / điều khoản | Định dạng | Số lượng | Dung lượng | Cách lấy / đăng nhập | Có stadium/arena? | Đánh giá cho dự án |
|---|---|---|---|---|---|---|---|---|---|
| Bibliocad | CAD | https://www.bibliocad.com (chưa mở được, host bị chặn) | **[CHƯA XÁC MINH]**: không tìm thấy nguyên văn Terms. Nguồn thứ cấp chỉ cho biết có bậc free (giới hạn số file/ngày) và premium. Các nguồn thứ cấp mâu thuẫn nhau về việc có cần tài khoản không. | DWG, DXF, RVT… (theo nguồn thứ cấp, chưa xác minh) | ~120.000 file (all3dp, [SNIPPET]) | chưa xác minh | Web thủ công, có giới hạn tải/ngày. Không phù hợp tải tự động. | **[CHƯA XÁC MINH]**: tìm kiếm không trả về trang stadium nào của Bibliocad. | **Loại**. Không rõ quyền tái phân phối. Nội dung do người dùng tải lên, chất lượng/lớp không chuẩn. Chuyển CAD→IFC nằm ngoài phạm vi. Cùng lắm dùng để xem tay. |
| GrabCAD (Library) | CAD (chủ yếu cơ khí 3D) | https://grabcad.com/library ; Terms: https://grabcad.com/terms (chưa mở được) | **[SNIPPET]** từ grabcad.com/terms: license "for your own benefit and non-commercial, internal use"; nội dung người dùng được dùng lại theo "Cross License" non-sublicensable cho "non-commercial, internal use". Code of Conduct (blog.grabcad.com, [SNIPPET]): "models on GrabCAD are for personal use only". Không thấy quyền tái phân phối. | STEP, IGES, SLDPRT, DWG… theo từng model (chưa xác minh từng file) | "millions of CAD models" (help.grabcad.com, [SNIPPET]) | chưa xác minh | Cần tài khoản miễn phí để tải (theo help center, [SNIPPET]). Không có API tải hàng loạt công khai (chưa xác minh). | **[CHƯA XÁC MINH]**: tìm kiếm không trả về model stadium nào trên GrabCAD. | **Loại**. Chỉ cho non-commercial internal use, không được tái phân phối vào repo. Chủ yếu là chi tiết cơ khí, không phải mặt bằng kiến trúc. |
| CADBlocksFree | CAD blocks | https://www.cadblocksfree.com (chưa mở được) | **[CHƯA XÁC MINH]**: không tìm thấy nguyên văn điều khoản. Scan2CAD ([SNIPPET], bài cũ) nói phải đăng ký mới tải được; learnarchitecture.net nói phần lớn không cần đăng ký (mâu thuẫn). | DWG, RFA, SKP… (Product Hunt, [SNIPPET]) | "tens of thousands" (Product Hunt, [SNIPPET]) | chưa xác minh | Web thủ công. | **[CHƯA XÁC MINH]** | **Loại**. Chủ yếu là block (đồ đạc, ký hiệu), không phải mặt bằng có phòng. Điều khoản không rõ. |
| DWGFree | CAD | **[CHƯA XÁC MINH]**: không xác định được tên miền chính thức (tìm kiếm "dwgfree" chỉ trả về dwgmodels.com, designscad.com). | **[CHƯA XÁC MINH]** | DWG | chưa xác minh | chưa xác minh | chưa xác minh | **[CHƯA XÁC MINH]** | **Loại / cần claude-01 cung cấp URL chính xác** nếu muốn kiểm tiếp. |

### Ghi chú về bản vẽ sân vận động/arena (từ site KHÁC, nguồn bổ sung, chỉ [SNIPPET])

Tìm kiếm "stadium dwg" trả về các site khác, không phải 4 site được giao:
- dwgmodels.com: ví dụ https://dwgmodels.com/163-stadium-1-plan-level-6.html, https://dwgmodels.com/704-stadium-plan-elevation.html (đánh dấu free, DWG, ~2,68 MB cho một file; không thấy điều khoản).
- designscad.com: nhiều file stadium (có free và PREMIUM trả phí), ví dụ "Amsterdam Arena Stadium 3D DWG". Không thấy điều khoản.
- cadbull.com: mặt bằng stadium có ghế ngồi (DWG).
- cadforum.cz: có Amsterdam Arena, Olympic stadium… Điều khoản ([SNIPPET]): "CAD blocks can be downloaded and used for your own personal or company design use only. Any distribution of the Catalog content (to other catalogs, web download, CD/DVD media, etc.) is prohibited". => **cấm tái phân phối**.
- cgtrader.com: Coventry Building Society Arena, 235 USD, "Custom License" (trả phí).

Kết luận: có bản vẽ stadium/arena trên web, nhưng (1) không xác minh được trên Bibliocad/GrabCAD/CADBlocksFree/DWGFree; (2) nơi có điều khoản rõ thì đều cấm hoặc không cho tái phân phối; (3) DWG 2D không có ngữ nghĩa IfcSpace. Muốn có ca test stadium cho dự án thì nên tìm **mô hình IFC** có giấy phép mở (việc của nhánh research khác), không dùng các DWG này.

## Bảng 2: Dataset floor plan

| Tên | Nhóm | URL chính thức | Giấy phép (nguyên văn + URL) | Định dạng | Số lượng | Dung lượng | Cách lấy / đăng nhập | Đánh giá cho dự án |
|---|---|---|---|---|---|---|---|---|
| CubiCasa5K | Floor plan ảnh + nhãn vector | Repo: https://github.com/CubiCasa/CubiCasa5k [ĐÃ MỞ]; dữ liệu: https://zenodo.org/record/2613548 (link từ README; host bị chặn, chưa mở) | [ĐÃ MỞ] https://raw.githubusercontent.com/CubiCasa/CubiCasa5k/master/LICENSE : "CubiCasa5K is licensed under a Creative Commons Attribution-NonCommercial 4.0 International License." (CC BY-NC 4.0) | Ảnh mặt bằng + SVG nhãn polygon (README nói "parse the SVG file") | 5000 mẫu, "over 80 floorplan object categories" [ĐÃ MỞ] (gồm tường, cửa, cửa sổ, loại phòng) | Zip ~5,5 GB (snippet Zenodo, [SNIPPET]); LMDB tự sinh ~105 GB [ĐÃ MỞ] | Zenodo, công khai, không cần đăng nhập (chưa xác minh trực tiếp); tải tự động được qua URL Zenodo (chưa thử, host bị chặn) | **Dùng được (phụ)**: tham khảo taxonomy nhãn phòng (map sang tên/loại IfcSpace), và lấy vài SVG polygon phòng/tường để test thuật toán polygonize 2D (tường → vùng kín → phòng). NC: không đưa dữ liệu vào repo, chỉ tải cục bộ. Là căn hộ Phần Lan nhỏ, không có cao độ/3D. |
| RPLAN | Floor plan raster | Trang dự án: https://ustc-gcl-f.github.io/projects/DeepLayout/index.html (đọc nguồn HTML qua raw GitHub repo ustc-gcl-f/ustc-gcl-f.github.io [ĐÃ MỞ]); link "Data set: RPLAN" trỏ tới Google Form: https://docs.google.com/forms/d/e/1FAIpQLSfwteilXzURRKDI5QopWCyOGkeb_CFFbRwtQ0SOPhEg0KGSfw/viewform | **[CHƯA XÁC MINH]**: không có file license; điều khoản (nếu có) nằm trong Google Form, chưa mở được. Không được coi là giấy phép mở. | Ảnh PNG raster nhiều kênh (theo ResPlan paper/MSD paper, [SNIPPET]: "limited by its raster format, simple rectangular room shapes") | "more than 80k floorplan images" (rplanpy README [ĐÃ MỞ]); 80K+ nhà ở Châu Á | chưa xác minh | Điền Google Form, chờ cấp link (rec.ustc.edu.cn). Không tải tự động được. | **Loại (hoặc rất thấp)**. Raster, phòng chủ yếu chữ nhật, giấy phép không rõ, phải xin phép. Không giúp gì cho bài toán IFC hơn CubiCasa5K/ResPlan. |
| Structured3D | Cảnh nhà 3D tổng hợp + chú thích cấu trúc | Repo: https://github.com/bertjiazheng/Structured3D [ĐÃ MỞ]; site: https://structured3d-dataset.org (bị chặn) | Code: MIT [ĐÃ MỞ]. Dữ liệu: "Structured3D Terms of Use" (https://drive.google.com/open?id=13ZwWpU_557ZQccwOUJ8H5lvXD7MeZFMa, link từ README [ĐÃ MỞ]; chưa mở file). Trích [SNIPPET] qua mirror HF: "Researcher shall use the Database only for non-commercial research and educational purposes", "Researcher shall not redistribute the downloaded data, in whole or in part, through other media". | `annotation_3d.json` (junctions, lines, planes kiểu floor/ceiling/wall, semantics gồm room type/door/window, ma trận plane-line, line-junction) + ảnh render [ĐÃ MỞ data_organization.md] | 3.500 scene, 21.835 phòng, >196k ảnh (arXiv 1908.00222, [SNIPPET]); split 0–2999/3000–3249/3250–3499 [ĐÃ MỞ] | chưa xác minh (rất lớn do ảnh) | Điền agreement form (https://forms.gle/LXg4bcjC2aEjrL9o8) [ĐÃ MỞ], chờ cấp quyền. Có mirror HF yêu cầu đồng ý chia sẻ thông tin liên hệ. Không tải tự động ngay. | **Dùng được (phụ, có điều kiện)**: hữu ích nhất về mặt khái niệm vì có quan hệ **plane ↔ room** (phòng = tập các mặt floor/ceiling/wall) — gần với ý tưởng space boundary 3D; có thể dùng làm ground truth để đối chiếu thuật toán suy phòng từ mặt tường (sau khi tự chuyển sang IFC, việc này ngoài phạm vi chính). Cấm tái phân phối: không đưa vào repo. Chỉ cần annotation_3d.json, không cần ảnh. |
| OpenFloorPlan | ? | **[CHƯA XÁC MINH] — không tìm thấy dataset tên này.** WebSearch `"OpenFloorPlan" dataset` không trả về kết quả nào dùng đúng tên. | — | — | — | — | — | **Tên mơ hồ / có thể không tồn tại**. Ứng viên gần nghĩa: (a) FloorPlanCAD; (b) ResPlan (CC BY 4.0, "open"); (c) MSD (CC BY 4.0); (d) WAFFLE (18.556 mặt bằng từ Wikimedia Commons, arXiv 2412.00955, [SNIPPET]); (e) MLStructFP (GitHub MLSTRUCT/MLStructFP, >950 ảnh, JSON tường, cần form). Đề nghị claude-01 hỏi lại nguồn của tên này. |
| ResPlan *(bổ sung)* | Floor plan vector + graph | https://github.com/m-agour/ResPlan [ĐÃ MỞ]; Kaggle: https://www.kaggle.com/datasets/resplan/resplan (link từ README) | [ĐÃ MỞ] https://raw.githubusercontent.com/m-agour/ResPlan/main/LICENSE : "DATA: ResPlan.pkl, split.json, croissant.json — Creative Commons Attribution 4.0 International (CC BY 4.0)"; code MIT. Kèm TAKEDOWN.md (gỡ theo yêu cầu). | Pickle Python (polygon tường/cửa/cửa sổ/phòng/ban công, toạ độ mét), split.json, croissant.json | 17.000 plan; 137.131 polygon phòng (43,2% chữ nhật); 17 nhãn; cạnh graph `via_door`/`adjacency`/`via_window`/`direct` [ĐÃ MỞ] | chưa xác minh (ResPlan.zip trong repo) | `git clone github.com/m-agour/ResPlan` — **tải tự động được, không cần đăng nhập** (GitHub cho phép trong container) | **Dùng được (tốt nhất trong nhóm floor plan)**: giấy phép mở cho phép tái phân phối có ghi công; vector theo mét; có graph kề phòng qua cửa/tường — có thể làm ground truth cho "phòng nào kề phòng nào qua phần tử nào", tương tự logic IfcRelSpaceBoundary 2D (phòng–tường–cửa). Test polygonize 2D. Hạn chế: chỉ 1 tầng, nhà ở Nam Á, không 3D, không phải IFC. |
| MSD – Modified Swiss Dwellings *(bổ sung)* | Floor plan nhiều căn hộ (tòa nhà) | Repo: https://github.com/caspervanengelenburg/msd [ĐÃ MỞ README]; dữ liệu: Kaggle https://www.kaggle.com/datasets/caspervanengelenburg/modified-swiss-dwellings (link từ README); 4TU: https://data.4tu.nl/datasets/e1d89cb5-6872-48fc-be63-aadd687ee6f9 | **[SNIPPET]**: bản ghi DOI 10.4121/e1d89cb5-6872-48fc-be63-aadd687ee6f9 ghi "CC BY 4.0". Repo không có file LICENSE (raw trả 404). Chưa mở được trang 4TU/Kaggle. | Graph (networkx / torch_geometric) với hình phòng, loại phòng, loại kết nối, ảnh [ĐÃ MỞ README] | ">5.3K floor plans … over 18.9K distinct apartments" [ĐÃ MỞ README]; 4TU README: train 4.167 plan ([SNIPPET]) | v1: test zip ~4,76 GB; train ~5,54 GB ([SNIPPET] 4TU) | Kaggle (cần tài khoản Kaggle để tải qua API — chưa xác minh) hoặc 4TU (công khai, chưa xác minh) | **Dùng được (phụ)**: mặt bằng toàn tầng nhiều căn hộ gần với tòa nhà thật hơn ResPlan; có thể test polygonize trên tầng lớn và đối chiếu nhãn phòng. Nguồn gốc là Swiss Dwellings (Archilyse) — có thể có hình học tường/cửa vector, chưa xác minh. |
| FloorPlanCAD *(bổ sung)* | Bản vẽ CAD vector (SVG) có nhãn | https://floorplancad.github.io (host bị chặn; org GitHub `floorplancad` chỉ có repo trang web, cập nhật 2023-02-02 [ĐÃ MỞ github.com/floorplancad]) | **[SNIPPET]** trang chính thức: "The annotations in this dataset along with this website belong to us and are licensed under a Creative Commons Attribution-NonCommercial 4.0 License"; tác giả "do not own the copyright of the drawings". | SVG (vector, nhãn ở mức đoạn thẳng, semantic + instance) | "over 15,000" mặt bằng, nhà ở đến thương mại ([SNIPPET]); mirror HF Voxel51/FloorPlanCAD test 5.308 mẫu | chưa xác minh | Link tải trên trang chính thức (chưa mở); mirror HF Voxel51. Nhóm tác giả được cho là đã giải thể 2022/2023 → link có thể chết. | **Dùng được (phụ, hạn chế)**: gần nhất với "CAD thật" (có nhà thương mại), dùng để test polygonize từ đoạn thẳng tường CAD. NC + bản quyền bản vẽ không thuộc tác giả → tuyệt đối không đưa vào repo. Nhãn tập trung vào ký hiệu (cửa, đồ đạc…), không có polygon phòng → không đối chiếu được phòng. |
| R2V – Raster-to-Vector (LIFULL) *(bổ sung)* | Nhãn vector mặt bằng | https://github.com/art-programmer/FloorplanTransformation [ĐÃ MỞ] | Code: MIT [ĐÃ MỞ LICENSE]. README: "We don't have the permission to share the rasterized images, which are from the LIFULL dataset. Here we only share our vector-graphics annotations". Không có giấy phép riêng cho annotation → **chưa xác minh** quyền dữ liệu. | Text: mỗi dòng (x_min, y_min, x_max, y_max, category, …); tường/cửa là đoạn thẳng, phòng chỉ là **một điểm/vùng nằm trong phòng**, không phải polygon [ĐÃ MỞ] | Annotation ~870 (theo paper, chưa xác minh trong README) trong `data/floorplan_representation`; thêm "100,000+ vector-graphics representation generated by our algorithm" trên Google Drive [ĐÃ MỞ] | nhỏ (trong repo) | `git clone` — tải tự động được | **Dùng được (phụ, nhỏ)**: định dạng rất giống bài toán của dự án: có đoạn tường + một điểm seed cho mỗi phòng → test thuật toán polygonize/flood-fill từ tường để ra polygon phòng rồi kiểm tra điểm seed nằm đúng phòng. Quyền dữ liệu chưa rõ → chỉ dùng cục bộ. |

## Tóm tắt khuyến nghị

1. **Không có nguồn nào ở đây là IFC**, nên không cái nào thay được bộ test IFC. Giá trị chính: (a) taxonomy nhãn phòng; (b) dữ liệu 2D để test riêng bước polygonize tường → phòng; (c) graph kề phòng làm ground truth topo.
2. Ưu tiên: **ResPlan** (CC BY 4.0, clone được ngay) > **R2V annotations** (clone được, định dạng tường + seed phòng) > **MSD** (CC BY 4.0, tầng nhiều căn, cần Kaggle/4TU) > **CubiCasa5K** (NC) > **Structured3D** (NC, cấm tái phân phối, cần form, nhưng có quan hệ phòng–mặt 3D) > FloorPlanCAD (NC, link có thể chết) > RPLAN (loại).
3. Nhóm CAD (Bibliocad, GrabCAD, CADBlocksFree, DWGFree): **loại** — điều khoản không xác minh được hoặc chỉ cho non-commercial/internal, không cho tái phân phối; chuyển DWG→IFC nằm ngoài phạm vi. Bản vẽ stadium có tồn tại trên các site khác (dwgmodels, designscad, cadbull, cadforum, cgtrader) nhưng không xác minh được trên 4 site được giao.
4. "OpenFloorPlan": không tìm thấy dataset nào mang đúng tên này — cần hỏi lại nguồn.
5. Hạn chế khảo sát: các host zenodo.org, grabcad.com, bibliocad.com, structured3d-dataset.org, staff.ustc.edu.cn, ustc-gcl-f.github.io, floorplancad.github.io không truy cập được từ container; các ô đánh [SNIPPET] cần mở lại trang gốc trước khi ghi vào `research/sources.md`.

## Nguồn đã dùng (truy cập 2026-11-10)

Đã mở trực tiếp:
- https://github.com/CubiCasa/CubiCasa5k
- https://raw.githubusercontent.com/CubiCasa/CubiCasa5k/master/LICENSE
- https://raw.githubusercontent.com/CubiCasa/CubiCasa5k/master/README.md
- https://raw.githubusercontent.com/bertjiazheng/Structured3D/master/README.md
- https://raw.githubusercontent.com/bertjiazheng/Structured3D/master/LICENSE
- https://raw.githubusercontent.com/bertjiazheng/Structured3D/master/data_organization.md
- https://raw.githubusercontent.com/m-agour/ResPlan/main/README.md
- https://raw.githubusercontent.com/m-agour/ResPlan/main/LICENSE
- https://raw.githubusercontent.com/art-programmer/FloorplanTransformation/master/README.md
- https://raw.githubusercontent.com/art-programmer/FloorplanTransformation/master/LICENSE
- https://raw.githubusercontent.com/caspervanengelenburg/msd/main/README.md (LICENSE: 404)
- https://raw.githubusercontent.com/unaisaralegui/rplanpy/main/README.md
- https://raw.githubusercontent.com/ustc-gcl-f/ustc-gcl-f.github.io/main/projects/DeepLayout/index.html
- https://github.com/floorplancad

Chỉ qua đoạn trích WebSearch (chưa mở trang gốc):
- https://zenodo.org/records/2613548
- https://arxiv.org/abs/1904.01920v1
- https://arxiv.org/abs/1908.00222
- https://huggingface.co/datasets/Pointcept/structured3d-compressed
- https://arxiv.org/abs/2508.14006
- https://doi.org/10.4121/e1d89cb5-6872-48fc-be63-aadd687ee6f9
- https://data.4tu.nl/datasets/e1d89cb5-6872-48fc-be63-aadd687ee6f9
- https://floorplancad.github.io
- https://docs.voxel51.com/dataset_zoo/datasets_hf/floorplancad.html
- https://arxiv.org/abs/2105.07147
- https://arxiv.org/pdf/2412.00955 (WAFFLE)
- https://github.com/MLSTRUCT/MLStructFP
- https://grabcad.com/terms
- https://help.grabcad.com/article/246-how-can-models-be-used-and-shared
- https://blog.grabcad.com/?p=15000
- https://all3dp.com/2/best-bibliocad-alternatives/
- https://www.scan2cad.com/blog/?p=28818
- https://www.producthunt.com/@cad_blocks_free
- https://www.cadforum.cz/catalog_en/?q=stadium
- https://dwgmodels.com/163-stadium-1-plan-level-6.html
- https://designscad.com/downloads/amsterdam-arena-stadium-3d-dwg-elevation-for-autocad/
- https://cadbull.com/detail/7406/Stadium-Project
- https://cgtrader.com/3d-models/exterior/stadium/coventry-building-society-arena-england

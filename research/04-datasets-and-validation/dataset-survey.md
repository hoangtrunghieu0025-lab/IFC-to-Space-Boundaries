# Khảo sát nguồn dữ liệu IFC/CAD để test (TASK-001)

- **Câu hỏi nghiên cứu**: Nguồn công khai nào cho file IFC dùng được để test việc suy ra `IfcSpace` và sinh `IfcRelSpaceBoundary`, ưu tiên công trình lớn và đông người (sân vận động), với giấy phép rõ và tải lại được?
- **Kết luận ngắn**:
  - Đã chọn **22 file IFC** từ 11 nguồn: 9 file tầng S, 5 tầng M, 8 tầng L. Mỗi file đã mở và đếm bằng IfcOpenShell 0.9.0; xem `samples/manifest.yaml`.
  - **14 file có sẵn `IfcRelSpaceBoundary`** dùng làm ground truth: 9 file 2nd level, 5 file 1st level.
  - **Không tìm thấy IFC sân vận động/arena công khai nào** (xem mục 4). Thay vào đó dùng công trình công cộng và cao tầng: phòng khám 269 phòng, trường học 307 phòng, toà đại học TalTech, giảng đường BIM-Edit, tháp 50 tầng, file 562 MB để đo hiệu năng.
  - Nhóm CAD/DWG và dataset floor plan **không dùng làm đầu vào**; chỉ ghi lại giá trị tham khảo.
- **Độ tin cậy**: cao cho các số đếm (đã chạy thật, có sha256) và cho giấy phép có trích nguyên văn. Trung bình hoặc thấp cho các ô ghi "chưa xác minh" hoặc "[SNIPPET]" (chỉ thấy qua đoạn trích của WebSearch).

## Chi tiết

### 1. Phương pháp và giới hạn

> **Danh sách đầy đủ mọi link và truy vấn đã thử** (kể cả nơi thất bại): `dataset-search-log.md`. Báo cáo thô của subagent: `raw/`.

- Ngày truy cập mọi nguồn: **2026-11-10**. Khảo sát chạy song song bằng 4 subagent của claude-01, sau đó claude-01 tải lại từ URL đã ghim và đo lại toàn bộ bằng `samples/inspect_ifc.py` (lệnh ở mục 6).
- **Mạng**:
  - Ban đầu container chỉ tới được GitHub (`git`, `raw.githubusercontent.com`, `media.githubusercontent.com`).
  - Sau đó môi trường được mở thêm `zenodo.org`, `huggingface.co`, `www.ifcwiki.org`, `www.wbdg.org`, `bimcorner.com`.
  - Vẫn **không truy cập được**:
    - `openifcmodel.cs.auckland.ac.nz`: HTTPS bị reset kết nối, còn site chỉ chạy HTTP.
    - CDN `us.aws.cdn.hf.co`: proxy trả 403.
    - `tib.eu`, `kaggle.com` (cần đăng nhập), `grabcad.com`, `bibliocad.com`, `structured3d-dataset.org`.
- **Kiểm chứng**:
  - "[ĐÃ MỞ]" = đã đọc trang hoặc file gốc.
  - "[SNIPPET]" = chỉ thấy qua đoạn trích của WebSearch.
  - "chưa xác minh" = không có bằng chứng trực tiếp.
- **Chấm điểm**: theo `dataset-quality-criteria.md`. Điểm tự động cộng với điểm nhập tay cho giấy phép và loại công trình.

### 2. Nguồn trong danh sách của người dùng

| Nguồn | URL chính thức (đã mở) | Giấy phép | Schema / số file / dung lượng | Cách tải | Kết luận |
|---|---|---|---|---|---|
| buildingSMART Sample-Test-Files | https://github.com/buildingSMART/Sample-Test-Files [ĐÃ MỞ] | CC BY 4.0 (file `LICENSE`) | IFC2X3/IFC4/IFC4X3_ADD2; 35 `.ifc`, 4 KB–2,4 MB (Simple-Scene, ISO Spec) | raw.githubusercontent | **Dùng** (S): `Building-Architecture` ở 3 schema để test đa schema. Lưu ý: Duplex/Clinic **đã chuyển** sang repo community (dòng dưới). |
| ↳ buildingSMART Community Sample-Test-Files (Duplex, Clinic, Esplanades, Molio, Schependomlaan…) | https://github.com/buildingsmart-community/Community-Sample-Test-Files [ĐÃ MỞ] | README: "you are publishing under the Creative Commons Attribution 4.0 International License". Duplex/Clinic: CC BY 4.0, yêu cầu ghi "BSI (2020)". Schependomlaan: "permission to use the data for scientific and academic purposes" (hạn chế) | IFC2X3/IFC4/IFC4X3; 172 `.ifc`, 0,6–395 MB | **Git LFS** → `media.githubusercontent.com/media/<repo>/<sha>/<path>` | **Dùng**: `duplex-a` (S), `clinic-architectural`, `esplanades`, `molio` (L). Schependomlaan không chọn vì giấy phép chỉ cho học thuật. |
| IFC Open House | https://github.com/cvillagrasa/IfcOpenHouse [ĐÃ MỞ] (Apache-2.0); bản C++ gốc trong IfcOpenShell (LGPL-3.0) | Apache-2.0 / LGPL-3.0 | IFC4, 1 file, ~1 MB | raw | **Loại**: 0 `IfcSpace`, mô hình sinh bằng code. Có thể "IFC Open House" trong danh sách là nhầm với bộ **KIT IFC Examples** (dòng dưới, nguồn bổ sung). |
| Open IFC Model Repository (Univ. Auckland) | http://openifcmodel.cs.auckland.ac.nz/ — **chưa mở được** | chưa xác minh (re3data ghi CC BY 3.0, ~130 model [SNIPPET]) | chưa xác minh | **Bị chặn** từ container | **BLOCKED**: có OTC Conference Center (hội trường, ~72 MB) và West Riverside Hospital (bệnh viện 7 tầng) theo danh sách của BIMData, đúng loại công trình ưu tiên. Đã ghi vào manifest dưới dạng `manual: true`, cần người dùng tải tay. |
| BIMCorner IFC Samples | https://bimcorner.com/ [ĐÃ MỞ] | chưa xác minh | — | — | **Loại**: tìm bằng ô tìm kiếm của site và WP REST API (`?s=ifc+files`, `wp-json/wp/v2/search`) **không thấy thư viện IFC mẫu nào**, chỉ có bài blog. Bài liên quan nhất (https://bimcorner.com/same-bridge-three-ifc-files/) dẫn sang roadtobim.com và là model cầu, không có `IfcSpace`. |
| BIMserver Demo Models (opensourceBIM TestFiles) | https://github.com/opensourceBIM/TestFiles [ĐÃ MỞ] | `TestData/license.txt`: GPL-3.0 cho repo. Bản quyền file gốc (KIT, Revit…) chưa xác minh | IFC2X_FINAL/IFC2X3/IFC4RC4/IFC4; 61 `.ifc`, 5 KB–64 MB | raw | **Dùng có điều kiện**: `ac11-fzk-haus` để ở `corpus_real/` vì giấy phép gốc chưa xác minh. 5 file IFC2X_FINAL và IFC4RC4 **không mở được** bằng IfcOpenShell ("Unsupported schema"). |
| Autodesk Revit Advanced Sample Project | help.autodesk.com (trang 2014) [SNIPPET] | Autodesk Terms of Use, chưa xác minh | Không có bản IFC chính thức | — | **Loại**: không tìm thấy IFC xuất sẵn chính thức. Bản IFC4 `ifc4rac_basic_sample_project.ifc` (24 MB, 14 space, 0 RSB) trong opensourceBIM có nguồn gốc chưa rõ, nên không chọn. |
| Revit Sample Projects (xuất sang IFC) | như trên | như trên | — | Phải tự xuất từ Revit (cần GUI và giấy phép Revit) | **Loại** (ngoài khả năng của container). Ghi lại để làm task SIDE nếu người dùng có Revit. |
| Bibliocad | https://www.bibliocad.com — bị chặn | chưa xác minh (có gói free/premium [SNIPPET]) | DWG/DXF/RVT | Web thủ công, giới hạn lượt tải mỗi ngày | **Loại**: không rõ quyền tái phân phối, và chuyển CAD sang IFC nằm ngoài phạm vi. |
| GrabCAD | https://grabcad.com/library — bị chặn | [SNIPPET] grabcad.com/terms: "non-commercial, internal use" | Chủ yếu cơ khí 3D | Cần tài khoản | **Loại**: không được tái phân phối, không phải mặt bằng kiến trúc. |
| CADBlocksFree | https://www.cadblocksfree.com — bị chặn | chưa xác minh | Block DWG | Web thủ công | **Loại**: chủ yếu block đồ đạc và ký hiệu, không có phòng. |
| DWGFree | **chưa xác minh**: không xác định được tên miền chính thức | — | — | — | **Loại**. Cần người dùng cho URL chính xác nếu muốn khảo sát tiếp. |
| CubiCasa5K | https://github.com/CubiCasa/CubiCasa5k [ĐÃ MỞ]; dữ liệu trên Zenodo record 2613548 | CC BY-NC 4.0 (`LICENSE` [ĐÃ MỞ]) | 5.000 mặt bằng ảnh + SVG polygon, >80 nhãn; zip ~5,5 GB [SNIPPET] | Zenodo | **Không tải**. Chỉ tham khảo taxonomy nhãn phòng và dùng vài SVG để test polygonize 2D cục bộ. Vì là NC nên không đưa vào repo. |
| RPLAN | https://ustc-gcl-f.github.io/projects/DeepLayout/ (đọc qua repo GitHub [ĐÃ MỞ]) | chưa xác minh (phải xin qua Google Form) | >80k ảnh raster | Google Form | **Loại**: dạng raster, phòng chủ yếu chữ nhật, giấy phép không rõ. |
| Structured3D | https://github.com/bertjiazheng/Structured3D [ĐÃ MỞ] | Code MIT. Dữ liệu: "non-commercial research and educational purposes", "shall not redistribute" [SNIPPET] | 3.500 cảnh 3D, `annotation_3d.json` có quan hệ phòng–mặt (floor/ceiling/wall) | Ký form | **Không tải**. Đáng tham khảo về khái niệm (phòng là tập các mặt, gần với space boundary 3D). |
| OpenFloorPlan | **không tìm thấy** dataset nào mang đúng tên này | — | — | — | **Chưa xác minh**. Các ứng viên gần nghĩa: FloorPlanCAD, ResPlan, MSD (mục 3). Cần người dùng cho biết nguồn của tên này. |

### 3. Nguồn bổ sung (ngoài danh sách)

Lý do phải tìm thêm: các nguồn ban đầu **không có IFC công trình lớn hoặc đông người nào có giấy phép rõ**. Bộ buildingSMART đã chuyển chỗ, Open IFC Model Repository bị chặn, BIMCorner và Revit không có IFC. Ngoài ra cần thêm ground truth **IFC4 2nd level** và một file >100 MB để đo hiệu năng.

| Nguồn | URL (đã mở) | Giấy phép (nguyên văn) | Dùng cho |
|---|---|---|---|
| KIT IFC Examples (IAI/KIT) | https://www.ifcwiki.org/index.php?title=KIT_IFC_Examples | "These examples are made by the Institute for Applied Computer Science (IAI) at the Karlsruhe Institute of Technology (KIT), and are for unrestricted use. If you use these examples for publications, please provide the following source: Institute for Automation and Applied Informatics (IAI) / Karlsruhe Institute of Technology (KIT)…" | `ac20-fzk-haus` (S), `ac20-institute-var-2`, `kit-smiley-west` (M): ground truth IFC4 2nd level. Bản ifcwiki trùng sha256 với bản sao trong ThatOpen/engine_web-ifc. |
| brunopostle/IFC-to-gbXML-converter (Test cases) | https://github.com/brunopostle/IFC-to-gbXML-converter | GPL-3.0 (`LICENSE` của repo) | `pilot-project-1/2/3` (S): ground truth IFC2x3 2nd level, rất nhỏ (0,2–0,6 MB) |
| RWTH-E3D/DigitalHub | https://github.com/RWTH-E3D/DigitalHub | "MIT License Copyright (c) 2020 RWTH Aachen University" | `rwth-digitalhub-with-sb` (M): **file duy nhất** dùng lớp con `IfcRelSpaceBoundary1stLevel`/`2ndLevel` và có `CorrespondingBoundary` (1.724) |
| Zenodo — SmartlivingEPC (TalTech) | https://zenodo.org/records/15782433 (API `/api/records/15782433`) | metadata `cc-by-4.0` | `taltech-ds3` (L): toà văn phòng và phòng thí nghiệm đại học, 115 space, 1.927 RSB |
| Zenodo — GNI BIM Dataset (TUM) | https://zenodo.org/records/19722012 ; https://github.com/ZijianWang-ZW/GNI-BIM-Dataset | `LICENSE`: "The contents of this dataset are licensed under the Creative Commons Attribution 4.0 International Public License (CC BY 4.0)" | `gni-model-6-arc` (L, 562 MB): **test hiệu năng**. Mở mất 14,7 s, RAM đỉnh ~3,1 GB. Các model khác cỡ vừa, ≤46 space, 0 RSB |
| Hugging Face — BIM-Edit | https://huggingface.co/datasets/BIM-Edit/BIM-Edit | tag `license:cc-by-4.0` | `bimedit-1fd06ad21e9e` (M): toà giảng đường (Hörsaal, Seminar), IFC4X3, 360 RSB. File lớn (tới 349 MB) **bị chặn** vì CDN `us.aws.cdn.hf.co` |
| Hugging Face — DeKH (bệnh viện Đức) | https://huggingface.co/datasets/RPTU-FGMB/DeKH | README: "released under CC BY-NC-SA 4.0 … may not be used for commercial purposes" | **Chưa tải**: dataset gated (HTTP 401, cần tài khoản và token HF), giấy phép phi thương mại |
| ara3d/IFC-toolkit (test-files) | https://github.com/ara3d/IFC-toolkit | Repo MIT. File test là bản sao từ issue người dùng, **giấy phép file gốc chưa xác minh** | `holter-tower` (L, 50 tầng, 177 MB), `r8-tower` (L, 28 tầng), `nus-skolebygg` (L, trường học 307 phòng). Để ở `corpus_real/`, **không commit** |
| ThatOpen/engine_web-ifc (thay cho IFCjs/test-ifc-files) | https://github.com/ThatOpen/engine_web-ifc | Repo MPL-2.0 (cho mã); giấy phép từng file theo nguồn gốc | `office-a` (M, NIBS Common BIM Files, giấy phép gốc chưa xác minh vì trang WBDG là SPA không đọc được) → `corpus_real/` |
| ResPlan / R2V / MSD / FloorPlanCAD (floor plan) | https://github.com/m-agour/ResPlan ; https://github.com/art-programmer/FloorplanTransformation ; https://github.com/caspervanengelenburg/msd | ResPlan: CC BY 4.0 [ĐÃ MỞ]; R2V: code MIT, quyền dữ liệu chưa rõ; MSD: CC BY 4.0 [SNIPPET]; FloorPlanCAD: CC BY-NC [SNIPPET] | **Không tải**. ResPlan có graph kề phòng qua cửa/tường, hợp làm ground truth topo 2D nếu sau này cần test riêng bước polygonize |
| Đã xem nhưng không chọn | youshengCode/IfcSampleFiles (không có LICENSE), IfcOpenShell/files (không có LICENSE), opensourcebim/ifc-files (CC BY-ND), andrewisen/bim-whale-ifc-samples (MIT, ít space), viktor-platform/ifc-sample-models (0 space), Zenodo RETIME 22125339 (không ghi license) | — | Không chọn: trùng nguồn, ít hoặc không có `IfcSpace`, hoặc giấy phép không phù hợp |

### 4. Tìm IFC sân vận động/arena — kết quả: không có

| Nơi tìm | Kết quả |
|---|---|
| GitHub: tìm repo "stadium ifc", "stadium bim", "arena bim", "stadium digital twin", và liệt kê toàn bộ file của ~15 repo IFC mẫu | Không có IFC sân vận động. Repo digital twin sân vận động (ví dụ Talanta Stadium) chỉ có mesh `.glb`. xeokit chỉ có XKT của OTC/West Riverside/Holter. |
| Zenodo API: `q=stadium|arena|hospital|airport|school&file_type=ifc`, `q="IfcSpace"` | 0 kết quả cho mỗi từ khoá. Toàn Zenodo chỉ có 34 record có file `.ifc`. |
| Danh sách tổng hợp: awesome-bim-datasets, CSV 35 nguồn của GNI, BIMData IFC_FILES.md (40 model) | Không có mục nào là stadium, arena, mall hay airport. |
| WebSearch EN/FR/DE ("stadium .ifc download", "Stadion IFC-Modell", "stade maquette IFC"…) | Chỉ có object IFC lẻ (ghế, khung thành), model thương mại không phải IFC, và ATC-75 (model kết cấu cắt từ một sân vận động, chỉ có PDF mô tả, không có link tải, không có `IfcSpace`). |
| CAD (dwgmodels, designscad, cadforum, cgtrader) [SNIPPET] | Có DWG sân vận động (cả Amsterdam Arena), nhưng là 2D, không có ngữ nghĩa phòng. cadforum cấm tái phân phối, cgtrader là hàng trả phí. |

**Nhận định**: model BIM của sân vận động thật thường là tài sản của chủ đầu tư hoặc nhà thầu (an ninh, NDA). Đây là suy luận, chưa xác minh. Đề xuất cho người dùng:
- (a) dùng các file thay thế đã chọn;
- (b) tự dựng một **sân vận động tổng hợp** bằng IfcOpenShell (khán đài, hành lang vòng, nhiều nghìn `IfcSpace`) làm ca test có ground truth biết trước;
- (c) dùng model thật của dự án digital twin 80.000 chỗ nếu người dùng có quyền, để trong `samples/corpus_real/`.

### 5. Bộ file đã chọn (trích từ `samples/manifest.yaml`)

Cột RSB ghi số lượng kèm level. Level được nhận qua lớp con IFC4, hoặc qua `Name`/`Description` theo exporter. "Mở / RAM" là thời gian `open` + `by_type` + thử tạo hình học cho ≤200 phần tử, và RAM đỉnh (MB), đo trên container 15 GB RAM.

| id | Tầng | Schema | MB | Tầng nhà | IfcSpace (có hình học) | RSB (level) | IfcProduct | Mở (s) / RAM (MB) | Loại | Giấy phép | Thư mục | Điểm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `bsi-ifc2x3-building-architecture` | S | IFC2X3 | 0.09 | 1 | 2 (2) | 0 (—) | 19 | 0.0 / 78 | — | mở | `small` | 58.0 |
| `bsi-ifc4-building-architecture` | S | IFC4 | 0.14 | 1 | 2 (2) | 0 (—) | 20 | 0.0 / 77 | — | mở | `small` | 58.0 |
| `bsi-ifc4x3-building-architecture` | S | IFC4X3 | 0.14 | 1 | 2 (2) | 0 (—) | 20 | 0.0 / 77 | — | mở | `small` | 58.0 |
| `duplex-a` | S | IFC2X3 | 2.38 | 4 | 21 (21) | 265 (1st) | 295 | 0.05 / 94 | residential | mở | `small` | 88.0 |
| `pilot-project-1` | S | IFC2X3 | 0.22 | 3 | 10 (10) | 76 (2nd) | 57 | 0.01 / 85 | — | mở | `small` | 85.0 |
| `pilot-project-2` | S | IFC2X3 | 0.32 | 4 | 11 (11) | 86 (2nd) | 94 | 0.01 / 85 | — | mở | `small` | 90.0 |
| `pilot-project-3` | S | IFC2X3 | 0.56 | 3 | 12 (12) | 166 (2nd) | 97 | 0.01 / 130 | — | mở | `small` | 85.0 |
| `ac20-fzk-haus` | S | IFC4 | 2.57 | 2 | 7 (7) | 81 (2nd) | 127 | 0.06 / 112 | residential | mở | `small` | 87.0 |
| `ac11-fzk-haus` | S | IFC2X3 | 4.15 | 2 | 7 (7) | 98 (2nd) | 144 | 0.11 / 108 | residential | chưa rõ | `corpus_real` | 72.0 |
| `clinic-architectural` | L | IFC2X3 | 13.0 | 4 | 269 (269) | 3124 (1st) | 3298 | 0.29 / 166 | large_public | mở | `large` | 90.0 |
| `esplanades` | L | IFC2X3 | 12.11 | 7 | 285 (285) | 0 (—) | 2862 | 0.35 / 159 | residential | mở | `large` | 78.0 |
| `molio` | L | IFC2X3 | 73.95 | 10 | 117 (117) | 1973 (2nd) | 4192 | 1.66 / 545 | office | mở | `large` | 95.0 |
| `rwth-digitalhub-with-sb` | M | IFC4 | 17.62 | 3 | 59 (59) | 4142 (2nd) | 1033 | 0.5 / 206 | office | mở | `large` | 95.0 |
| `ac20-institute-var-2` | M | IFC4 | 10.93 | 5 | 82 (82) | 1000 (2nd) | 1190 | 0.32 / 146 | office | mở | `large` | 92.0 |
| `office-a` | M | IFC2X3 | 4.1 | 3 | 99 (99) | 1334 (1st) | 1090 | 0.09 / 104 | office | chưa rõ | `corpus_real` | 72.0 |
| `nus-skolebygg` | L | IFC2X3 | 56.36 | 5 | 307 (307) | 0 (—) | 5638 | 1.79 / 497 | office | chưa rõ | `corpus_real` | 65.0 |
| `holter-tower` | L | IFC4 | 177.47 | 50 | 12 (12) | 0 (—) | 61474 | 5.2 / 1331 | office | chưa rõ | `corpus_real` | 62.0 |
| `r8-tower` | L | IFC2X3 | 71.74 | 28 | 0 (0) | 0 (—) | 14652 | 2.36 / 576 | residential | chưa rõ | `corpus_real` | 35.0 |
| `kit-smiley-west` | M | IFC4 | 6.11 | 5 | 140 (140) | 1689 (2nd) | 1272 | 0.19 / 115 | residential | mở | `large` | 90.0 |
| `taltech-ds3` | L | IFC4 | 38.73 | 5 | 115 (115) | 1927 (1st) | 5530 | 0.94 / 340 | office | mở | `large` | 90.0 |
| `gni-model-6-arc` | L | IFC2X3 | 561.84 | 11 | 46 (46) | 0 (—) | 981 | 14.75 / 3121 | office | mở | `large` | 77.0 |
| `bimedit-1fd06ad21e9e` | M | IFC4X3 | 5.26 | 4 | 36 (36) | 360 (1st) | 1073 | 0.13 / 135 | large_public | mở | `large` | 93.0 |
| `otc-conference-center` | (L) | chưa xác minh | ~72 | — | — | — | — | — | large_public | chưa rõ | `corpus_real` | — (**BLOCKED**, cần tải tay) |

Lưu ý: `building_class` = `office` được dùng chung cho văn phòng và trường học/đại học. Đây là bậc 5 điểm trong thang `dataset-quality-criteria.md`.

**Vai trò đề xuất trong pipeline**:
- **Debug thuật toán (test tự động)**: cả 8 file trong `samples/small/`. Pilot 1–3 và FZK-Haus có ground truth 2nd level; Duplex có 1st level; Simple-Scene dùng để test đa schema.
- **Đo độ chính xác so với ground truth**:
  - IFC4: `rwth-digitalhub-with-sb`, `ac20-institute-var-2`, `kit-smiley-west`, `taltech-ds3`, `bimedit-1fd06ad21e9e`.
  - IFC2x3: `molio`, `clinic-architectural`.
- **Suy luận `IfcSpace` trên công trình lớn (so IoU với `IfcSpace` có sẵn, không có RSB)**: `esplanades`, `nus-skolebygg`.
- **Hiệu năng / quy mô**: `gni-model-6-arc` (562 MB), `holter-tower` (50 tầng, 61k phần tử), `r8-tower` (0 `IfcSpace`, suy luận hoàn toàn).

### 6. Lệnh đã chạy (kiểm chứng)

```bash
pip install ifcopenshell pyyaml               # ifcopenshell 0.9.0.post1, Python 3.13
python3 samples/fetch_datasets.py             # tải 22 file từ URL ghim; OTC báo MISSING (manual)
python3 samples/update_manifest.py            # đo toàn bộ, ghi vào manifest (~2,5 phút)
python3 samples/fetch_datasets.py --force --tier S   # tải lại tầng S → "Tất cả khớp."
python3 samples/fetch_datasets.py --check     # 22 OK, 1 MISSING (otc-conference-center)
```

## Liên quan đến pipeline IFC → Space Boundaries

- **Reader phải xử lý ba cách ghi level boundary**:
  - Lớp con IFC4 thật (chỉ RWTH). Lưu ý `IfcRelSpaceBoundary2ndLevel` là lớp con của `1stLevel`.
  - `Name` = `1stLevel`/`2ndLevel` (Revit), hoặc `2ndLevel` kèm `Description` = `2a` (ArchiCAD 20).
  - `Name` = `Second Level` (ArchiCAD 11, IFC2x3).
- `CorrespondingBoundary` chỉ có trong 1 file (RWTH). Muốn kiểm tiêu chí "cặp đối xứng" trên file khác thì phải tự ghép cặp theo phần tử bao.
- `ConnectionGeometry` của ground truth chủ yếu là `IfcCurveBoundedPlane` (2nd level) hoặc `IfcSurfaceOfLinearExtrusion` (Revit 1st level), theo subagent khảo sát (chưa đo lại trong `inspect_ifc.py`).
- Có ArchiCAD xuất **tường chỉ có biểu diễn `Axis`, không có `Body`** (`molio`: 91 tường `[L]AD`). Bước lấy hình học phải bỏ qua các tường này, không coi là lỗi.
- RAM khi chỉ parse tăng khoảng 5,5 MB cho mỗi MB file (562 MB → ~3,1 GB). Tessellation toàn bộ sẽ tốn hơn (chưa đo). Pipeline cho tầng L nên xử lý theo tầng nhà hoặc stream.

## Nguồn
- https://github.com/buildingSMART/Sample-Test-Files — truy cập 2026-11-10
- https://github.com/buildingsmart-community/Community-Sample-Test-Files — truy cập 2026-11-10
- https://www.ifcwiki.org/index.php?title=KIT_IFC_Examples — truy cập 2026-11-10
- https://github.com/brunopostle/IFC-to-gbXML-converter — truy cập 2026-11-10
- https://github.com/RWTH-E3D/DigitalHub — truy cập 2026-11-10
- https://zenodo.org/records/15782433 — truy cập 2026-11-10
- https://zenodo.org/records/19722012 ; https://github.com/ZijianWang-ZW/GNI-BIM-Dataset — truy cập 2026-11-10
- https://huggingface.co/datasets/BIM-Edit/BIM-Edit — truy cập 2026-11-10
- https://huggingface.co/datasets/RPTU-FGMB/DeKH — truy cập 2026-11-10
- https://github.com/ara3d/IFC-toolkit — truy cập 2026-11-10
- https://github.com/ThatOpen/engine_web-ifc — truy cập 2026-11-10
- https://github.com/opensourceBIM/TestFiles — truy cập 2026-11-10
- https://github.com/cvillagrasa/IfcOpenHouse — truy cập 2026-11-10
- https://bimcorner.com/ — truy cập 2026-11-10
- https://github.com/bimdata/BIMData-Research-and-Development/blob/master/pages/IFC_FILES.md — truy cập 2026-11-10
- https://github.com/nbharathik/awesome-bim-datasets — truy cập 2026-11-10
- https://github.com/CubiCasa/CubiCasa5k ; https://github.com/bertjiazheng/Structured3D ; https://github.com/m-agour/ResPlan ; https://github.com/art-programmer/FloorplanTransformation ; https://github.com/caspervanengelenburg/msd — truy cập 2026-11-10
- Chỉ qua WebSearch [SNIPPET]: https://grabcad.com/terms ; re3data r3d100012443 (Open IFC Model Repository) ; https://www.atcouncil.org/pdfs/ATC-75IFCBenchmark.pdf ; https://www.cadforum.cz/catalog_en/?q=stadium — truy cập 2026-11-10

## Câu hỏi còn mở
1. **OTC Conference Center / West Riverside Hospital**: người dùng có tải tay được từ http://openifcmodel.cs.auckland.ac.nz/ không? Nếu được, đặt vào `samples/corpus_real/` và chạy `update_manifest.py --id otc-conference-center`. Cần xác minh giấy phép trên trang gốc.
2. **Sân vận động**: chọn hướng (b) dựng model tổng hợp (đề xuất thành task mới) hay (c) dùng model thật của người dùng?
3. "OpenFloorPlan" và "DWGFree" trong danh sách là nguồn nào (URL)?
4. Có mở thêm CDN `us.aws.cdn.hf.co` để tải các model BIM-Edit lớn (tới 349 MB, CC BY 4.0) không?
5. Giấy phép gốc của NIBS Common BIM Files (`office-a`), KIT bản AC11 (`ac11-fzk-haus`) và các file ara3d vẫn chưa xác minh.

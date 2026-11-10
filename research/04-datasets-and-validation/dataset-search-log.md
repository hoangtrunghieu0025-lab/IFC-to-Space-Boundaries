# Nhật ký tìm kiếm nguồn dữ liệu (TASK-001)

- **Câu hỏi nghiên cứu**: Trong TASK-001, ta đã tìm dữ liệu IFC/CAD ở đâu, bằng truy vấn nào, kết quả mỗi nơi ra sao? Mục đích là để agent sau không phải tìm lại từ đầu và biết chỗ nào đã thử mà thất bại.
- **Kết luận ngắn**:
  - Đã kiểm tra khoảng 45 nguồn và trang, chạy khoảng 30 truy vấn tìm kiếm (GitHub, Zenodo API, WebSearch tiếng Anh, Pháp, Đức). Đã liệt kê hoặc đếm khoảng 150 file IFC.
  - 11 nguồn có file được đưa vào `samples/manifest.yaml`.
  - 9 nhóm host không truy cập được từ container (mục 4).
  - Không nơi nào có IFC sân vận động/arena tải được (mục 6).
- **Độ tin cậy**: cao cho các link ở mục 2–4 (đã truy cập thật, ghi rõ kết quả). Thấp cho mục 5 (chỉ thấy qua đoạn trích của WebSearch).

## Chi tiết

### 1. Cách tìm và quy ước

- **Thời gian**: 2026-11-10, khoảng 11:52–12:20 GMT+7.
- **Người thực hiện**: claude-01, cùng 4 subagent chạy song song:
  - (a) kho IFC mẫu;
  - (b) IFC công trình lớn/đông người;
  - (c) CAD và floor plan;
  - (d) xác minh các host được mở mạng sau.
  Báo cáo thô của từng subagent nằm trong `raw/` (mục 8).
- **Công cụ**:
  - `git ls-remote` / `git clone --depth 1 --filter=blob:none --no-checkout` để liệt kê cây file mà không tải blob.
  - `curl -r 0-3000` để đọc header `FILE_SCHEMA`; `curl -I` để lấy dung lượng.
  - API Zenodo và Hugging Face.
  - WebSearch/WebFetch.
  - IfcOpenShell 0.9.0 để mở file và đếm.
- **Mạng**:
  - Lúc đầu container chỉ tới được GitHub.
  - Khoảng 12:10 mở thêm `zenodo.org`, `huggingface.co`, `www.ifcwiki.org`, `www.wbdg.org`, `bimcorner.com`, qua môi trường riêng của repo do người dùng duyệt.
- **Ký hiệu kết quả**:
  - ✅ = đã lấy file vào bộ test;
  - 👁 = đã mở và xem nhưng không chọn;
  - ⛔ = không truy cập được;
  - 🔎 = chỉ thấy qua đoạn trích WebSearch.

### 2. ✅ Nguồn có file được chọn (xem `samples/manifest.yaml`)

| Nguồn | Link | Lấy được gì | Ghi chú tìm kiếm |
|---|---|---|---|
| buildingSMART Sample-Test-Files | https://github.com/buildingSMART/Sample-Test-Files | `bsi-*-building-architecture` (3 schema) | README cho biết các file cũ (Duplex, Clinic…) đã chuyển sang repo community |
| buildingSMART Community Sample-Test-Files | https://github.com/buildingsmart-community/Community-Sample-Test-Files | `duplex-a`, `clinic-architectural`, `esplanades`, `molio` | Liệt kê 172 `.ifc`. Repo dùng Git LFS: raw URL chỉ trả pointer, phải tải qua `media.githubusercontent.com/media/…` |
| KIT IFC Examples | https://www.ifcwiki.org/index.php?title=KIT_IFC_Examples | `ac20-fzk-haus`, `ac20-institute-var-2`, `kit-smiley-west` | Phải dùng `https://`, vì `http://` không phân giải được. Có 5 model: 3 công trình, 1 cầu, 1 đường |
| IFC-to-gbXML-converter | https://github.com/brunopostle/IFC-to-gbXML-converter (thư mục `Test cases/`) | `pilot-project-1/2/3` | Tìm ra khi tìm file có RSB 2nd level cho IFC2x3 |
| RWTH DigitalHub | https://github.com/RWTH-E3D/DigitalHub | `rwth-digitalhub-with-sb` | Bản `Version_1/..._with_SB_v1.ifc` có boundary, còn bản v2 thì không |
| Zenodo — SmartlivingEPC (TalTech) | https://zenodo.org/records/15782433 | `taltech-ds3` | Tìm qua Zenodo API với `file_type=ifc` |
| Zenodo — GNI BIM Dataset (TUM) | https://zenodo.org/records/19722012 ; https://github.com/ZijianWang-ZW/GNI-BIM-Dataset | `gni-model-6-arc` | DOI concept 19722011 chuyển hướng sang 19722012. Đã tải `2026_BIMprojects.zip` (221 MB, 9 model kiến trúc). Chưa tải `2025_BIMfundamentals.zip` (503 MB, 208 model đồ án) |
| Hugging Face — BIM-Edit | https://huggingface.co/datasets/BIM-Edit/BIM-Edit | `bimedit-1fd06ad21e9e` | 156 mục. File lớn bị chặn ở CDN (mục 4) |
| ara3d IFC-toolkit | https://github.com/ara3d/IFC-toolkit (thư mục `test-files/`) | `holter-tower`, `r8-tower`, `nus-skolebygg` | Liệt kê 38 file. Giấy phép file chưa rõ nên để ở `corpus_real/` |
| ThatOpen engine_web-ifc | https://github.com/ThatOpen/engine_web-ifc (`tests/ifcfiles/public/`) | `office-a` | Đây là nơi thay thế repo "IFCjs/test-ifc-files" cũ |
| opensourceBIM TestFiles (BIMserver) | https://github.com/opensourceBIM/TestFiles (`TestData/data/`) | `ac11-fzk-haus` | 61 `.ifc`. 5 file IFC2X_FINAL/IFC4RC4 IfcOpenShell không mở được |

### 3. 👁 Đã mở, đã xem nhưng không chọn

| Nguồn | Link | Đã xem gì | Vì sao không chọn |
|---|---|---|---|
| IfcOpenHouse | https://github.com/cvillagrasa/IfcOpenHouse | Tải và đếm | 0 `IfcSpace` (mô hình sinh bằng code) |
| IfcOpenShell (repo chính) | https://github.com/IfcOpenShell/IfcOpenShell | Liệt kê 292 `.ifc` | Phần lớn là fixture nhỏ; AC20-FZK-Haus trùng bản KIT |
| IfcOpenShell/files | https://github.com/IfcOpenShell/files | Liệt kê 266 `.ifc`, đếm 3 file | Không có LICENSE, chủ yếu là ca lỗi hình học |
| youshengCode IfcSampleFiles | https://github.com/youshengCode/IfcSampleFiles | 18 file, đếm 11 file | Không có LICENSE; Duplex trùng bản gốc |
| opensourcebim ifc-files | https://github.com/opensourcebim/ifc-files | HHS Office, Schultz Residence | Giấy phép CC BY-ND (không được phát hành bản sửa) |
| bim-whale samples | https://github.com/andrewisen/bim-whale-ifc-samples | 6 file | Ít `IfcSpace` (≤8) |
| viktor-platform samples | https://github.com/viktor-platform/ifc-sample-models | 5 file | 0 `IfcSpace`, không có LICENSE |
| ThatOpen engine_components | https://github.com/ThatOpen/engine_components | `school_str.ifc` | Model kết cấu, 0 `IfcSpace` |
| DataSetSchependomlaan | https://github.com/openBIMstandards/DataSetSchependomlaan | README | Đã chuyển sang repo community. Giấy phép chỉ cho "scientific and academic purposes" |
| Zenodo — RETIME | https://zenodo.org/records/22125339 | Metadata | Không ghi giấy phép (có model trường học 74 MB) |
| Zenodo — KIT Smiley West corrected | https://zenodo.org/records/10680698 | Metadata (CC BY 4.0) | Chưa dùng, vì đã lấy bản gốc trên ifcwiki |
| Hugging Face — DeKH | https://huggingface.co/datasets/RPTU-FGMB/DeKH | README, API | Gated (HTTP 401, cần tài khoản và token), giấy phép CC BY-NC-SA 4.0 |
| BIMCorner | https://bimcorner.com/ ; tìm `?s=ifc+files`, `?s=sample+ifc`, `wp-json/wp/v2/search` | Trang chủ, tìm kiếm WP | Không có thư viện IFC mẫu, chỉ có bài blog (bài cầu dẫn sang roadtobim.com) |
| WBDG Common BIM Files | https://www.wbdg.org/ (bim/cobie/common-bim-files) | HTML | Trang là SPA, HTML trả về rỗng; gọi API bị từ chối quyền |
| BIMData R&D — IFC_FILES | https://github.com/bimdata/BIMData-Research-and-Development/blob/master/pages/IFC_FILES.md | Danh mục 40 model / 100 file | Chỉ là danh mục; nhờ nó biết URL của OTC và West Riverside |
| awesome-bim-datasets | https://github.com/nbharathik/awesome-bim-datasets | Danh mục | Ghi rõ không có stadium/arena/airport/mall/station |
| GNI — `other_online_BIM_model_resources.csv` | trong https://github.com/ZijianWang-ZW/GNI-BIM-Dataset | 35 nguồn | Dùng để biết thêm Kaggle, DURAARK, HiTOS |
| xeokit-sdk (tag v1.4.0) | https://github.com/xeokit/xeokit-sdk | `examples/models/xkt` | Chỉ có XKT (không phải IFC) của OTC, West Riverside, Holter |
| CubiCasa5K | https://github.com/CubiCasa/CubiCasa5k | README, LICENSE | Floor plan ảnh, CC BY-NC 4.0; không phải IFC |
| Structured3D | https://github.com/bertjiazheng/Structured3D | README, LICENSE, data_organization.md | Dữ liệu cấm tái phân phối, phải ký form |
| ResPlan | https://github.com/m-agour/ResPlan | README, LICENSE (CC BY 4.0) | Floor plan 2D; có thể dùng sau này để test polygonize |
| R2V FloorplanTransformation | https://github.com/art-programmer/FloorplanTransformation | README, LICENSE | Quyền dùng dữ liệu chưa rõ |
| MSD | https://github.com/caspervanengelenburg/msd | README (LICENSE 404) | Floor plan 2D, cần Kaggle hoặc 4TU |
| RPLAN | https://ustc-gcl-f.github.io/projects/DeepLayout/ (đọc qua repo `ustc-gcl-f/ustc-gcl-f.github.io`) | HTML | Ảnh raster, phải xin qua Google Form |
| FloorPlanCAD (org GitHub) | https://github.com/floorplancad | Danh sách repo | Chỉ có repo trang web, không có dữ liệu |

### 4. ⛔ Không truy cập được từ container

| Nguồn | Link | Lỗi | Có gì ở đó (theo nguồn thứ cấp) |
|---|---|---|---|
| Open IFC Model Repository (Univ. Auckland) | http://openifcmodel.cs.auckland.ac.nz/ | HTTPS bị reset kết nối; site chỉ chạy HTTP nên không qua proxy | **OTC Conference Center** (~72 MB), **West Riverside Hospital**, Hospital Parking Garage, Trapelo. Cần tải tay |
| DURAARK (TIB) | https://tib.eu/data/duraark/BuildingData/… | Host bị chặn; theo re3data đã offline từ 13.02.2020 | Autodesk 210 King (155 MB), FOJAB Landsarkivet (177 MB), SGD HiTOS, LTU A-House |
| HiTOS (buildingSMART Norway) | ftp://ftp.buildingsmart.no/pub/ifcfiles/HITOS/ | FTP, không thử | Trường cao đẳng Tromsø |
| Kaggle — rvtifc-projects | https://www.kaggle.com/datasets/artemboiko/rvtifc-projects | Cần đăng nhập | ~4.596 IFC "real projects" (chưa xác minh) |
| Hugging Face CDN | `us.aws.cdn.hf.co` | Proxy trả 403 | Các file BIM-Edit lớn (tới 349 MB) |
| NIBS portal | https://portal.nibs.org/… | Bị chặn | Medical Clinic Combined (112 MB) |
| BIMcollab example | https://www.bimcollab.com/Files/Example-Projects/BIMcollab_ifc_models.aspx | Bị chặn | 9 file IFC (175 MB cả bộ) |
| Up:Town (GeoBIM benchmark, TU Delft) | https://3d.bk.tudelft.nl/projects/geobim-benchmark/data.html | Phải ký thỏa thuận dữ liệu | Chung cư cao tầng (241 MB) |
| OSArch AEC Open Data | https://wiki.osarch.org/ | WebFetch báo ENOTFOUND | Danh mục dữ liệu mở |
| CAD: Bibliocad, GrabCAD, CADBlocksFree | https://www.bibliocad.com ; https://grabcad.com/library ; https://www.cadblocksfree.com | Bị chặn | Thư viện DWG/CAD (xem mục 5) |
| Dataset: Structured3D site, FloorPlanCAD site, Zenodo CubiCasa | https://structured3d-dataset.org ; https://floorplancad.github.io ; https://zenodo.org/record/2613548 | Bị chặn trong đợt khảo sát đầu | — |
| DWGFree, "OpenFloorPlan" | — | **Không tìm ra nguồn khớp tên** | Cần người dùng cho URL |

### 5. 🔎 Chỉ thấy qua đoạn trích WebSearch (chưa mở trang gốc)

| Link | Thông tin lấy được |
|---|---|
| https://grabcad.com/terms ; https://help.grabcad.com/article/246-how-can-models-be-used-and-shared | Chỉ cho dùng "non-commercial, internal use" |
| re3data r3d100012443, r3d100012506 | Open IFC Model Repository theo CC BY 3.0, khoảng 130 model; DURAARK offline |
| https://www.atcouncil.org/pdfs/ATC-75IFCBenchmark.pdf | ATC-75: model kết cấu cắt ra từ một sân vận động, không có link tải |
| https://www.cadforum.cz/catalog_en/?q=stadium | Có Amsterdam Arena; điều khoản cấm tái phân phối |
| https://dwgmodels.com/163-stadium-1-plan-level-6.html ; https://dwgmodels.com/704-stadium-plan-elevation.html | DWG sân vận động miễn phí, không thấy điều khoản |
| https://designscad.com/downloads/amsterdam-arena-stadium-3d-dwg-elevation-for-autocad/ | DWG Amsterdam Arena (có bản trả phí) |
| https://cadbull.com/detail/7406/Stadium-Project | Mặt bằng sân vận động DWG |
| https://cgtrader.com/3d-models/exterior/stadium/coventry-building-society-arena-england | Model 3D trả phí, không phải IFC |
| https://help.autodesk.com/cloudhelp/2014/ENU/Revit/files/GUID-4EED7335-DCC7-48AD-A8BD-8156CAB27A33.htm | Trang Revit sample 2014; không có IFC chính thức |
| https://wbdg.org/node/23884 ; https://wbdg.org/node/9165 | Common BIM Files (Duplex, Office, Clinic) |
| https://researchspace.auckland.ac.nz/handle/2292/16583 | Bài báo về Open IFC Model Repository |
| https://vps.visionsdureel.ch/en/sample-ifc-file.html ; https://downloads.steptools.com/docs/stpfiles/ifc/ | Câu "unrestricted use" của KIT (sau đó đã xác minh trên ifcwiki); danh sách IFC của STEP Tools |
| https://arxiv.org/abs/2606.20146 | Bài báo BIM-Edit (CC BY 4.0) |
| https://t.me/s/bimiran/2743 | Bản đăng lại listing West Riverside Hospital ("courtesy of Autodesk… for research"); nguồn thứ cấp |
| https://doi.org/10.4121/e1d89cb5-6872-48fc-be63-aadd687ee6f9 ; https://data.4tu.nl/datasets/e1d89cb5-6872-48fc-be63-aadd687ee6f9 | MSD theo CC BY 4.0 |
| https://arxiv.org/abs/1904.01920v1 ; https://arxiv.org/abs/1908.00222 ; https://arxiv.org/abs/2508.14006 ; https://arxiv.org/pdf/2412.00955 ; https://arxiv.org/abs/2105.07147 | Bài báo CubiCasa5K, Structured3D, ResPlan, WAFFLE, FloorPlanCAD |
| https://github.com/MLSTRUCT/MLStructFP | Dataset floor plan (cần form) |
| https://all3dp.com/2/best-bibliocad-alternatives/ ; https://www.scan2cad.com/blog/?p=28818 ; https://www.producthunt.com/@cad_blocks_free | Thông tin thứ cấp về Bibliocad, CADBlocksFree |

### 6. Riêng cho sân vận động / công trình đông người — truy vấn đã chạy

| Kênh | Truy vấn / thao tác | Kết quả |
|---|---|---|
| GitHub (tìm repo) | `stadium ifc` | 0 repo |
| | `stadium bim` | Chỉ có `ATSmithPB/_Stadium_Tools` (thư viện Grasshopper, không có IFC) |
| | `stadium digital twin` | 56 repo. Đã clone `M5-Engineering-PLC/talanta-twin` (chỉ có `.glb`/`.gltf`); `tuyishimehope/stadium-digital-twin-web` (không có model); `studio-public-demos/stadium-digital-twin` (không clone được) |
| | `arena bim` | Chỉ có HKIBIM "BIMAutomationArena" (cuộc thi, không có model) |
| | `airport ifc`, `hospital ifc` | Không có model công trình phù hợp |
| GitHub (liệt kê toàn bộ file) | ~15 repo IFC mẫu: buildingSMART (2 repo + Certification-datasets), IfcOpenShell (2), ara3d, opensourcebim (2), youshengCode, bim-whale, viktor, ThatOpen (2), IFC4.3.x-sample-models, sylvainHellin/ifc-bench, RWTH DigitalHub, xeokit-sdk | Không có file nào là stadium/arena |
| Zenodo API | `https://zenodo.org/api/records?q=ifc&file_type=ifc&size=25` (+ `page=2`) | 34 record có file `.ifc` |
| | `q=stadium` / `arena` / `hospital` / `airport` / `school` kèm `file_type=ifc` | 0 kết quả mỗi từ |
| | `q="IfcSpace"` | 0 kết quả |
| | `q=ifc space boundary` | Record 14238135 (`demo_building.ifc`, 0,2 MB) và các công cụ |
| | `q=stadium ifc` (không lọc) | 2.057 kết quả nhiễu ("IFC" = Instituto Federal Catarinense…) |
| WebSearch EN/FR/DE | "stadium .ifc BIM model free download", "arena stadium IFC zenodo/figshare/mendeley", "openBIM stadium IFC dataset digital twin", "stade maquette IFC", "Stadion IFC-Modell", "Tekla sample model stadium", "Bonsai/OSArch stadium" | Chỉ có object IFC lẻ (ghế, khung thành trên BIMobject, BIM&CO, ARCAT), model thương mại không phải IFC (BC Place, Letzigrund, Linzer Stadion), model FEM Dlubal, ATC-75 (PDF), bài giới thiệu của Tekla BIM Awards |
| WebSearch "stadium dwg" | — | dwgmodels, designscad, cadbull, cadforum, cgtrader (mục 5) |
| Figshare / Mendeley | WebSearch | Không thấy dataset sân vận động. Mendeley "Arena" là phần mềm mô phỏng, không liên quan |

### 7. Gợi ý cho lần tìm sau
- **Chưa thử:**
  - `2025_BIMfundamentals.zip` của GNI (503 MB, 208 model);
  - các file BIM-Edit lớn (cần mở CDN `us.aws.cdn.hf.co`);
  - Kaggle rvtifc-projects (cần tài khoản);
  - Open IFC Model Repository (cần tải tay);
  - Figshare/Mendeley qua API trực tiếp (hiện mới chỉ dùng WebSearch).
- **Tránh:** ô tìm kiếm tự do của Zenodo không lọc `file_type` (rất nhiễu); raw URL của repo dùng Git LFS (chỉ trả pointer).

### 8. Báo cáo thô của subagent (lưu nguyên văn)

| File | Nội dung |
|---|---|
| `raw/survey-ifc-samples.md` | Khảo sát kho IFC mẫu: bảng khoảng 110 file đã liệt kê, đọc header hoặc đếm, kèm chi tiết ground truth |
| `raw/survey-large-ifc.md` | Tìm IFC công trình lớn và sân vận động: bảng ứng viên, nguồn bị chặn, xếp hạng tầng L |
| `raw/survey-cad-floorplan.md` | Khảo sát CAD/DWG và dataset floor plan |
| `raw/survey-extra-hosts.md` | Xác minh KIT, WBDG, BIMCorner, Zenodo, Hugging Face sau khi mở mạng |

Số liệu trong `raw/` là do subagent đo. Số liệu chính thức là bản claude-01 đo lại trong `samples/manifest.yaml`; nếu hai nơi lệch nhau thì lấy manifest.

## Liên quan đến pipeline IFC → Space Boundaries
- Là danh mục nguồn để bổ sung dữ liệu khi pipeline cần thêm ca test (nhất là công trình đông người và 2nd-level boundary).
- Nếu sau này cần ca test sân vận động, chỉ còn cách dùng model của người dùng: không còn nguồn công khai nào để tìm thêm theo các kênh ở mục 6. **Quyết định của người dùng (2026-11-10): không dựng model sân vận động tổng hợp.**

## Nguồn
- Toàn bộ link ở mục 2–6, truy cập 2026-11-10. Các nguồn chính đã được thêm vào `research/sources.md`.

## Câu hỏi còn mở
- Xem mục "Câu hỏi còn mở" trong `dataset-survey.md` (OTC/West Riverside, sân vận động, URL của DWGFree/OpenFloorPlan, CDN Hugging Face).

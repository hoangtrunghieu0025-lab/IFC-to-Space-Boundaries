> **Báo cáo thô** của subagent hỗ trợ claude-01 (TASK-001), ngày 2026-11-10, chép nguyên văn từ scratchpad để lưu vết. Đường dẫn `/tmp/…/scratchpad/…` và `dl/`, `dl2/`, `scripts/` nhắc trong báo cáo là thư mục tạm của phiên, **không còn tồn tại**. Bản tổng hợp đã kiểm lại: `../dataset-survey.md`, `../dataset-search-log.md`.

# Khảo sát kho IFC mẫu cho TASK-001 (IfcSpace / IfcRelSpaceBoundary)

- Ngày truy cập: 2026-11-10. Người khảo sát: subagent hỗ trợ claude-01.
- Phương pháp: `git ls-remote` + `git clone --depth 1 --filter=blob:none --no-checkout` để liệt kê cây file (không tải blob); `curl -sSL -r 0-1500` raw URL để đọc header `FILE_SCHEMA`; `curl -sSLI` lấy Content-Length; với repo dùng Git LFS thì đọc pointer (`size`) qua raw và tải nội dung qua `media.githubusercontent.com`. File <25 MB được tải về `scratchpad/dl/<nguồn>/` và đếm bằng ifcopenshell (`by_type('IfcSpace')`, `IfcRelSpaceBoundary`, `IfcBuildingStorey`), kèm phân tích kiểu hình học của IfcSpace và `ConnectionGeometry` của boundary.
- Script: `scratchpad/scripts/{fetch.py,count.py,detail.py,names.py}`; kết quả thô JSON: `scratchpad/scripts/count_main.json`, `count_extra.json`.
- Mạng: `github.com` (git), `raw.githubusercontent.com` và **`media.githubusercontent.com` (LFS) đều tải được**. WebFetch bị chặn DNS (ENOTFOUND) với: `www.ifcwiki.org`, `openifcmodel.cs.auckland.ac.nz`, `bimcorner.com`, `www.wbdg.org` → các nguồn đó chỉ có thông tin qua WebSearch, ghi "chưa xác minh".

## Phát hiện quan trọng (đọc trước)

1. **`buildingSMART/Sample-Test-Files` đã được tái cấu trúc**: hiện chỉ còn "Certification datasets" (Simple-Scene + vài file ISO Spec). README ghi: *"Previous content of this repository, curated by users, has been moved to the buildingSMART community organisation"* → **`buildingsmart-community/Community-Sample-Test-Files`** (Duplex, Clinic, Schependomlaan, Esplanades…). Repo này dùng **Git LFS cho `*.ifc`** → raw URL chỉ trả pointer; phải dùng `https://media.githubusercontent.com/media/buildingsmart-community/Community-Sample-Test-Files/main/<path>` (đã kiểm tra, HTTP 206/200 OK).
2. `openBIMstandards/DataSetSchependomlaan` chỉ còn README: *"Schependomlaan has moved!"* → nay nằm trong Community-Sample-Test-Files `IFC 2.3.0.1 (IFC 2x3)/Schependomlaan/`.
3. `IFCjs/test-ifc-files` **không tồn tại/không truy cập được** (git ls-remote đòi đăng nhập ⇒ repo không public). Bộ test IFC của IFC.js nay ở **`ThatOpen/engine_web-ifc`** thư mục `tests/ifcfiles/public/` (đã xác minh).
4. "IFC Open House": thực tế là **IfcOpenHouse** – mô hình nhà sinh bằng code của IfcOpenShell (C++ 2012, `src/examples/IfcOpenHouse.cpp`; bản Python: `cvillagrasa/IfcOpenHouse`). **Không có IfcSpace** → không hữu ích làm ground truth. Các mẫu của KIT (IAI) là bộ "KIT IFC Examples" (AC20-FZK-Haus, AC20-Institute-Var-2…), có bản sao trên GitHub (xem bên dưới).
5. **Ground truth space boundary tốt nhất (đã đếm thật)**:
   - IFC4, 2nd level (`Name='2ndLevel'`, `Description='2a'`), IfcSpace Brep: **AC20-FZK-Haus.ifc** (7 space / 81 RSB / 2 tầng, 2.5 MB) và **AC20-Institute-Var-2** (82 / 1000 / 5 tầng, 10.4 MB).
   - IFC4 Revit 2nd level: **FM_ARC_DigitalHub.ifc** (64 / 1123 / 3 tầng, 13.7 MB).
   - IFC2x3 2nd level (`Name='2ndLevel'`, Revit 2016): **Pilot project 1/2/3.ifc** (10–12 space, 76–166 RSB, 0.2–0.5 MB) – rất nhỏ, lý tưởng cho test.
   - IFC2x3 ArchiCAD "Second Level": AC11-FZK-Haus (7/98), AC90R1-Jasmin-Sun (10/135), AC90R1-niedriha (19/514), AC9R1-Haus-G-H (26/513), AC11-Institute-Var-2 (82/1175).
   - IFC2x3 Revit **1st level** (`Name='1stLevel'`, ConnectionGeometry chủ yếu `IfcSurfaceOfLinearExtrusion`): Duplex_A (21/265), Clinic_Architectural (269/3124), Office_A (99/1334), 4351.ifc (6/142).
   - Trong IFC4 files trên, `by_type('IfcRelSpaceBoundary2ndLevel')` = 0: các exporter dùng lớp cha `IfcRelSpaceBoundary` và đánh dấu level qua `Name`/`Description` — cần xử lý cả hai cách khi so sánh.

## Bảng 1 – Nguồn

| # | Nguồn | URL chính thức | Giấy phép (nguyên văn + file) | Schema | Số file IFC | Dung lượng | Cách tải | Trạng thái |
|---|---|---|---|---|---|---|---|---|
| 1a | buildingSMART Sample-Test-Files (certification) | https://github.com/buildingSMART/Sample-Test-Files (nhánh `main`) | "This work is licensed under the Creative Commons Attribution 4.0 International License." — `LICENSE` (https://github.com/buildingSMART/Sample-Test-Files/blob/main/LICENSE) | IFC2X3, IFC4, IFC4X3_ADD2 | 35 `.ifc` | file 12 KB–185 KB (Simple-Scene) | raw.githubusercontent (không LFS cho .ifc) | Mở được |
| 1b | buildingSMART Community Sample-Test-Files (Duplex, Clinic, Schependomlaan, Esplanades, ISO Spec archive, NURBS…) | https://github.com/buildingsmart-community/Community-Sample-Test-Files (nhánh `main`) | Không có LICENSE gốc; README: "you are publishing under the Creative Commons Attribution 4.0 International License". README Duplex/Clinic: "Creative Commons (CC BY 4.0)" + yêu cầu ghi nguồn "BSI (2020) …". Esplanades: "(c) Esplan … Creative Commons Attribution 4.0 International License". Schependomlaan README: "All data owners have given permission to use the data for scientific and academic purposes" (không ghi CC rõ → coi là **hạn chế học thuật**, chưa xác minh thêm) | IFC2X3, IFC4, IFC4X3 | 172 `.ifc` (199 kể cả ifczip/ifcxml) | 0.6 MB – 395 MB | **Git LFS** → `media.githubusercontent.com/media/<repo>/main/<path>` | Mở được (raw chỉ trả pointer) |
| 2 | IFC Open House / IfcOpenHouse | https://github.com/cvillagrasa/IfcOpenHouse ; bản gốc C++ trong https://github.com/IfcOpenShell/IfcOpenShell `src/examples/IfcOpenHouse.cpp`; bản IFC4 cũng có trong engine_web-ifc | cvillagrasa: Apache License 2.0 (`LICENSE`); IfcOpenShell: LGPL-3.0 (`COPYING.LESSER`) | IFC4 | 1 | 1.0 MB / 113 KB | raw | Mở được, **0 IfcSpace** |
| 2b | KIT IFC Examples (IAI, KIT) | http://www.ifcwiki.org/index.php?title=KIT_IFC_Examples (theo WebSearch) | Theo kết quả tìm kiếm: "for unrestricted use" — **chưa xác minh** (trang bị chặn) | IFC2x3/IFC4/IFC4x3 | chưa xác minh | AC20-FZK-Haus ~2.5 MB | Bản sao trên GitHub: engine_web-ifc `tests/ifcfiles/public/AC20-FZK-Haus.ifc`, IfcOpenShell `docs/ifcopenshell-cpp/models/AC20-FZK-Haus.ifc` | Trang gốc **bị chặn** (cần mở `www.ifcwiki.org`) |
| 3 | Open IFC Model Repository (Univ. Auckland) | https://openifcmodel.cs.auckland.ac.nz/ (host xác nhận qua bài báo/registry, chưa mở được) | Theo registry re3data (qua WebSearch): CC BY 3.0, ~130 model — **chưa xác minh** | chưa xác minh | ~130 (chưa xác minh) | chưa xác minh | chưa xác minh | **Bị chặn** (cần mở `openifcmodel.cs.auckland.ac.nz`) |
| 4 | BIMCorner IFC Samples | https://bimcorner.com/ (URL trang sample chưa xác định) | chưa xác minh | chưa xác minh | chưa xác minh | chưa xác minh | chưa xác minh | **Bị chặn** (cần mở `bimcorner.com`); WebSearch không trả trang nào của BIMCorner |
| 5 | BIMserver TestFiles | https://github.com/opensourceBIM/TestFiles (nhánh `master`, thư mục `TestData/data/`) | `TestData/license.txt`: "GNU General Public License … version 3 … Copyright (C) 2009-2017 BIMserver.org" (nhãn của repo; bản quyền từng file gốc – ArchiCAD/KIT/Revit – chưa xác minh) | IFC2X_FINAL, IFC2X3, IFC4RC4, IFC4 | 61 `.ifc` (64 kể cả ifczip/ifcxml) | 4.7 KB – 64 MB | raw | Mở được |
| 5b | opensourcebim/ifc-files (HHS Office, Schultz Residence) | https://github.com/opensourcebim/ifc-files (`master`); mirror: ezhangle/ifc-files | README: "Post your IFC data under the Creative Commons Attribution-NoDerivatives license https://creativecommons.org/licenses/by-nd/4.0/" (**ND – không được sửa/phân phối bản sửa**) | IFC2X3 | 8 | 13–22 MB | raw | Mở được |
| 6 | Autodesk Revit sample projects (rac_advanced_sample_project…) | https://help.autodesk.com (trang IFC samples cũ 2014, theo WebSearch) | Autodesk Terms of Use — **chưa xác minh**; không thấy IFC xuất sẵn chính thức | — | chưa xác minh | — | — | Không có bản IFC chính thức xác minh được. Bản IFC xuất từ Revit sample có trong opensourceBIM `ifc4rac_basic_sample_project.ifc` (IFC4, 25.4 MB, 14 space, 0 RSB) |
| 6b | Common BIM Files (NIBS/buildingSMART alliance, USACE ERDC) | https://www.wbdg.org/node/23884 (theo WebSearch) | chưa xác minh trên trang gốc; README Community repo nói bản gốc "Creative Commons" và nay phát hành CC BY 4.0 | IFC2X3 | Duplex/Office/Clinic | — | Bản sao: Community repo (Duplex, Clinic); `Office_A_20110811.ifc` trong engine_web-ifc | wbdg.org **bị chặn** |
| 7a | IfcOpenShell (repo chính) | https://github.com/IfcOpenShell/IfcOpenShell (nhánh mặc định `v0.9.0`) | LGPL-3.0 (`COPYING`, `COPYING.LESSER`) — cho mã; file mẫu chưa ghi riêng | IFC2X3/IFC4 | 292 `.ifc` (đa số fixture nhỏ, thư viện phân loại) | — | raw | Mở được |
| 7b | IfcOpenShell/files | https://github.com/IfcOpenShell/files (`master`) | README không nêu license; không có file LICENSE → **chưa xác minh** | IFC2X3/IFC4 | 266 `.ifc` | — | raw | Mở được (chủ yếu ca lỗi hình học) |
| 7c | ThatOpen engine_web-ifc (thay cho IFCjs/test-ifc-files) | https://github.com/ThatOpen/engine_web-ifc (`main`), `tests/ifcfiles/public/` | Repo: Mozilla Public License 2.0 (`LICENSE.md`) — cho mã; giấy phép từng file mẫu (KIT, BSI Office/Duplex/Clinic, Schependomlaan…) theo nguồn gốc, **chưa xác minh** | IFC2X3/IFC4/IFC4X3 | 30 trong `public/` | 0.1 – 73 MB | raw (không LFS) | Mở được |
| 7d | youshengCode/IfcSampleFiles | https://github.com/youshengCode/IfcSampleFiles (`main`) | Không có LICENSE; README chỉ "A collection of IFC sample files for software test use." → **chưa xác minh** | IFC2X3/IFC4 | 18 | 63 KB – 49 MB | raw | Mở được (Duplex = bản sao giống byte-size với Community) |
| 7e | andrewisen/bim-whale-ifc-samples | https://github.com/andrewisen/bim-whale-ifc-samples (`main`) | MIT License (`LICENSE`, "Copyright (c) 2020 André "MG" Wisén") | IFC2X3 (Revit 2021) | 6 | 40 KB – 53 MB | raw | Mở được |
| 7f | brunopostle/IFC-to-gbXML-converter – Test cases | https://github.com/brunopostle/IFC-to-gbXML-converter (`master`), `Test cases/` | GNU GPL v3 (`LICENSE`) | IFC2X3/IFC4 | 5 | 0.2 – 26.7 MB | raw | Mở được — **có 2nd-level RSB** |
| 7g | viktor-platform/ifc-sample-models | https://github.com/viktor-platform/ifc-sample-models (`main`) | Không thấy LICENSE → chưa xác minh | IFC4 | 5 | 5–27 MB | raw | Mở được, 0 IfcSpace ở các file đã đếm |
| 7h | ThatOpen/engine_components | https://github.com/ThatOpen/engine_components | MIT (`LICENSE.md`) | IFC4 | 4 | school_str 8.6 MB | raw | Mở được, school_str 0 space |
| 7i | Bonsai/BlenderBIM sample | trong IfcOpenShell `src/bonsai/test/files/`, `src/bonsai/docs/tutorials/files/` | LGPL/GPL theo repo (chưa xác minh riêng cho file) | IFC4 | ~20 nhỏ | ≤16 KB | raw | Mở được; fixture tối giản, 0 IfcSpace (basic.ifc). `IFC4 Demo Template.ifc` trả 37 byte (có vẻ symlink) |

Ghi chú: **ISSUE_159_kleine_Wohnung_R22.ifc** (engine_web-ifc) là file xuất từ BlenderBIM 0.0.220420, IFC4, 28 IfcSpace, 4 tầng, 0 RSB.

## Bảng 2 – File ứng viên đã kiểm tra

Cột: nguồn | file | URL tải trực tiếp | MB | schema (ifcopenshell, hoặc header) | IfcSpace (số có Representation) | IfcRelSpaceBoundary | số IfcBuildingStorey | ứng dụng xuất (originating_system) | trạng thái kiểm tra.

### 2a. buildingSMART Sample-Test-Files (CC BY 4.0) – đã tải + đếm (tên local tiền tố phiên bản, `dl/bsi-sample-v/`)

| nguồn | file | URL | MB | schema | IfcSpace | RSB | tầng | app | trạng thái |
|---|---|---|---|---|---|---|---|---|---|
| bsi-sample | Building-Architecture.ifc (2x3) | https://raw.githubusercontent.com/buildingSMART/Sample-Test-Files/main/IFC%202.3.0.1%20%28IFC%202x3%20TC1%29/Simple-Scene/Building-Architecture.ifc | 0.09 | IFC2X3 | 2 (2, Body SweptSolid) | 0 | 1 | Sketchup IFC manager 5.6.0 | đã tải+đếm |
| bsi-sample | Building-Architecture.ifc (IFC4) | https://raw.githubusercontent.com/buildingSMART/Sample-Test-Files/main/IFC%204.0.2.1%20%28IFC%204%20ADD2%20TC1%29/Simple-Scene/Building-Architecture.ifc | 0.14 | IFC4 | 2 (2, SweptSolid) | 0 | 1 | Sketchup IFC manager 5.6.0 | đã tải+đếm |
| bsi-sample | Building-Architecture.ifc (4.3) | https://raw.githubusercontent.com/buildingSMART/Sample-Test-Files/main/IFC%204.3.2.0%20%28IFC%204.3%20ADD2%29/Simple-Scene/Building-Architecture.ifc | 0.14 | IFC4X3_ADD2 | 2 (2, SweptSolid) | 0 | 1 | Sketchup IFC manager 5.6.0 | đã tải+đếm |
| bsi-sample | Building-Hvac / Building-Structural (2x3, 4, 4.3) | cùng thư mục `Simple-Scene/` | 0.07–0.19 | IFC2X3/IFC4/IFC4X3 | 0 | 0 | 1 | Sketchup | đã tải+đếm |
| bsi-sample | wall-with-opening-and-window.ifc | https://raw.githubusercontent.com/buildingSMART/Sample-Test-Files/main/IFC%204.0.2.1%20%28IFC%204%20ADD2%20TC1%29/ISO%20Spec%20-%20ReferenceView_V1.2/wall-with-opening-and-window.ifc | 0.01 | IFC4 | 0 | 0 | 1 | RDF Test App | đã tải+đếm |

### 2b. Các nguồn còn lại (tự sinh từ JSON; bản sao trùng được giữ để biết mirror)

| nguồn | file | URL | MB | schema | IfcSpace | RSB | tầng | app | trạng thái |
|---|---|---|---|---|---|---|---|---|---|
| bsi-community | Duplex_A_20110907.ifc | https://media.githubusercontent.com/media/buildingsmart-community/Community-Sample-Test-Files/main/IFC%202.3.0.1%20%28IFC%202x3%29/Duplex%20Apartment/Duplex_A_20110907.ifc | 2.27 | IFC2X3 | 21 (21 có Repr.) | 265 | 4 | 20100326_1700 | đã tải+đếm |
| bsi-community | Duplex_Electrical_20121207.ifc | https://media.githubusercontent.com/media/buildingsmart-community/Community-Sample-Test-Files/main/IFC%202.3.0.1%20%28IFC%202x3%29/Duplex%20Apartment/Duplex_Electrical_20121207.ifc | 1.53 | IFC2X3 | 1 (1 có Repr.) | 4 | 3 | 20121003_2115(x64) | đã tải+đếm |
| bsi-community | Duplex_MEP_20110907.ifc | https://media.githubusercontent.com/media/buildingsmart-community/Community-Sample-Test-Files/main/IFC%202.3.0.1%20%28IFC%202x3%29/Duplex%20Apartment/Duplex_MEP_20110907.ifc | 17.04 | IFC2X3 | 42 (42 có Repr.) | 8 | 3 | 20100326_1700 | đã tải+đếm |
| bsi-community | Duplex_M_20111024_ROOMS_AND_SPACES.ifc | https://media.githubusercontent.com/media/buildingsmart-community/Community-Sample-Test-Files/main/IFC%202.3.0.1%20%28IFC%202x3%29/Duplex%20Apartment/Duplex_M_20111024_ROOMS_AND_SPACES.ifc | 8.38 | IFC2X3 | 37 (37 có Repr.) | 8 | 3 | 20100903_2115(x64) | đã tải+đếm |
| bsi-community | Duplex_Plumbing_20121113.ifc | https://media.githubusercontent.com/media/buildingsmart-community/Community-Sample-Test-Files/main/IFC%202.3.0.1%20%28IFC%202x3%29/Duplex%20Apartment/Duplex_Plumbing_20121113.ifc | 30.09 | IFC2X3 (header) | chưa xác minh | chưa xác minh | chưa xác minh |  | chỉ đọc header/size (>25MB, chưa tải) |
| bsi-community | 1807_EP_AR_v18.ifc | https://media.githubusercontent.com/media/buildingsmart-community/Community-Sample-Test-Files/main/IFC%202.3.0.1%20%28IFC%202x3%29/Esplanades/1807_EP_AR_v18.ifc | 11.55 | IFC2X3 | 285 (285 có Repr.) | 0 | 7 | IFC file generated by GRAPHISOFT AR | đã tải+đếm |
| bsi-community | Clinic_Architectural.ifc | https://media.githubusercontent.com/media/buildingsmart-community/Community-Sample-Test-Files/main/IFC%202.3.0.1%20%28IFC%202x3%29/Medical-Dental%20Clinic/Clinic_Architectural.ifc | 12.40 | IFC2X3 | 269 (269 có Repr.) | 3124 | 4 | 20100326_1700 (Solibri IFC Optimize | đã tải+đếm |
| bsi-community | Clinic_Electrical.ifc | https://media.githubusercontent.com/media/buildingsmart-community/Community-Sample-Test-Files/main/IFC%202.3.0.1%20%28IFC%202x3%29/Medical-Dental%20Clinic/Clinic_Electrical.ifc | 6.49 | IFC2X3 | 266 (266 có Repr.) | 0 | 3 | 20121003_2115(x64) (Solibri IFC Opt | đã tải+đếm |
| bsi-community | Clinic_HVAC.ifc | https://media.githubusercontent.com/media/buildingsmart-community/Community-Sample-Test-Files/main/IFC%202.3.0.1%20%28IFC%202x3%29/Medical-Dental%20Clinic/Clinic_HVAC.ifc | 25.67 | IFC2X3 (header) | chưa xác minh | chưa xác minh | chưa xác minh |  | chỉ đọc header/size (>25MB, chưa tải) |
| bsi-community | Clinic_Plumbing.ifc | https://media.githubusercontent.com/media/buildingsmart-community/Community-Sample-Test-Files/main/IFC%202.3.0.1%20%28IFC%202x3%29/Medical-Dental%20Clinic/Clinic_Plumbing.ifc | 53.25 | IFC2X3 (header) | chưa xác minh | chưa xác minh | chưa xác minh |  | chỉ đọc header/size (>25MB, chưa tải) |
| bsi-community | Clinic_Structural.ifc | https://media.githubusercontent.com/media/buildingsmart-community/Community-Sample-Test-Files/main/IFC%202.3.0.1%20%28IFC%202x3%29/Medical-Dental%20Clinic/Clinic_Structural.ifc | 18.18 | IFC2X3 | 0 (0 có Repr.) | 0 | 4 | (Solibri IFC Optimizer) | đã tải+đếm |
| bsi-community | Molio_with_URIs.ifc | https://media.githubusercontent.com/media/buildingsmart-community/Community-Sample-Test-Files/main/IFC%202.3.0.1%20%28IFC%202x3%29/Molio/Molio_with_URIs.ifc | 70.52 | chưa xác minh (header) | chưa xác minh | chưa xác minh | chưa xác minh |  | chỉ đọc header/size (>25MB, chưa tải) |
| bsi-community | bSDD_references_example.ifc | https://media.githubusercontent.com/media/buildingsmart-community/Community-Sample-Test-Files/main/IFC%202.3.0.1%20%28IFC%202x3%29/SDK%20-%20S1/bSDD_references_example.ifc | 376.41 | IFC2X3 (header) | chưa xác minh | chưa xác minh | chưa xác minh |  | chỉ đọc header/size (>25MB, chưa tải) |
| bsi-community | IFC Schependomlaan incl planningsdata.ifc | https://media.githubusercontent.com/media/buildingsmart-community/Community-Sample-Test-Files/main/IFC%202.3.0.1%20%28IFC%202x3%29/Schependomlaan/As%20Planned%20models/IFC%20Schependomlaan%20incl%20planningsdata.ifc | 62.06 | IFC2X3 (header) | chưa xác minh | chưa xác minh | chưa xác minh |  | chỉ đọc header/size (>25MB, chưa tải) |
| bsi-community | XELLA-Begane grond.ifc | https://media.githubusercontent.com/media/buildingsmart-community/Community-Sample-Test-Files/main/IFC%202.3.0.1%20%28IFC%202x3%29/Schependomlaan/Coordination%20model%20and%20subcontractors%20models/BIMsight%20Projectdata1/ProjectData/XELLA-Begane%20grond.ifc | 0.57 | IFC2X3 | 0 (0 có Repr.) | 0 | 1 | Xella | đã tải+đếm |
| bsi-community | WILLEMSEN-Laagbouw.ifc | https://media.githubusercontent.com/media/buildingsmart-community/Community-Sample-Test-Files/main/IFC%202.3.0.1%20%28IFC%202x3%29/Schependomlaan/Coordination%20model%20and%20subcontractors%20models/BIMsight%20Projectdata1/WILLEMSEN-Laagbouw.ifc | 1.87 | IFC2X3 | 0 (0 có Repr.) | 0 | 0 | AutoCAD Architecture 2014 - English | đã tải+đếm |
| bsi-community | XELLA-Begane grond.ifc | https://media.githubusercontent.com/media/buildingsmart-community/Community-Sample-Test-Files/main/IFC%202.3.0.1%20%28IFC%202x3%29/Schependomlaan/Coordination%20model%20and%20subcontractors%20models/BIMsight%20Projectdata1/XELLA-Begane%20grond.ifc | 0.57 | IFC2X3 | 0 (0 có Repr.) | 0 | 1 | Xella | đã tải+đếm |
| bsi-community | IFC Schependomlaan.ifc | https://media.githubusercontent.com/media/buildingsmart-community/Community-Sample-Test-Files/main/IFC%202.3.0.1%20%28IFC%202x3%29/Schependomlaan/Design%20model%20IFC/IFC%20Schependomlaan.ifc | 47.00 | chưa xác minh (header) | chưa xác minh | chưa xác minh | chưa xác minh |  | chỉ đọc header/size (>25MB, chưa tải) |
| bsi-community | IFC_Schependomlaan_geo.ifc | https://media.githubusercontent.com/media/buildingsmart-community/Community-Sample-Test-Files/main/IFC%202.3.0.1%20%28IFC%202x3%29/Schependomlaan/Design%20model%20IFC/IFC_Schependomlaan_geo.ifc | 47.00 | chưa xác minh (header) | chưa xác minh | chưa xác minh | chưa xác minh |  | chỉ đọc header/size (>25MB, chưa tải) |
| bsi-community | example project location.ifc | https://media.githubusercontent.com/media/buildingsmart-community/Community-Sample-Test-Files/main/IFC%204.0.2.1%20%28IFC%204%29/Example%20project%20location/example%20project%20location.ifc | 2.82 | IFC4 | 48 (48 có Repr.) | 0 | 3 | 20190412_1200(x64) - Exporter 20.3. | đã tải+đếm |
| obim-testfiles | 4351.ifc | https://raw.githubusercontent.com/opensourceBIM/TestFiles/master/TestData/data/4351.ifc | 6.95 | IFC2X3 | 6 (6 có Repr.) | 142 | 5 | 20100326_1700 | đã tải+đếm |
| obim-testfiles | AC11-FZK-Haus-IFC.ifc | https://raw.githubusercontent.com/opensourceBIM/TestFiles/master/TestData/data/AC11-FZK-Haus-IFC.ifc | 3.96 | IFC2X3 | 7 (7 có Repr.) | 98 | 2 | Windows System | đã tải+đếm |
| obim-testfiles | AC11-Institute-Var-2-IFC.ifc | https://raw.githubusercontent.com/opensourceBIM/TestFiles/master/TestData/data/AC11-Institute-Var-2-IFC.ifc | 2.70 | IFC2X3 | 82 (82 có Repr.) | 1175 | 5 | Windows System | đã tải+đếm |
| obim-testfiles | AC90R1-Jasmin-Sun-105-2x3.ifc | https://raw.githubusercontent.com/opensourceBIM/TestFiles/master/TestData/data/AC90R1-Jasmin-Sun-105-2x3.ifc | 3.07 | IFC2X3 | 10 (10 có Repr.) | 135 | 3 | Windows System | đã tải+đếm |
| obim-testfiles | AC90R1-niedriha-V2-2x3.ifc | https://raw.githubusercontent.com/opensourceBIM/TestFiles/master/TestData/data/AC90R1-niedriha-V2-2x3.ifc | 2.33 | IFC2X3 | 19 (19 có Repr.) | 514 | 4 | Windows System | đã tải+đếm |
| obim-testfiles | AC9R1-Haus-G-H-Ver2-2x3.ifc | https://raw.githubusercontent.com/opensourceBIM/TestFiles/master/TestData/data/AC9R1-Haus-G-H-Ver2-2x3.ifc | 4.35 | IFC2X3 | 26 (26 có Repr.) | 513 | 4 | Windows System | đã tải+đếm |
| obim-testfiles | ADT-FZK-Haus-2005-2006.ifc | https://raw.githubusercontent.com/opensourceBIM/TestFiles/master/TestData/data/ADT-FZK-Haus-2005-2006.ifc | 2.77 | IFC2X_FINAL | — | — | — |  | tải được; ifcopenshell lỗi: Unsupported schema: IFC2X_FINAL |
| obim-testfiles | Allplan-Smiley-West.ifc | https://raw.githubusercontent.com/opensourceBIM/TestFiles/master/TestData/data/Allplan-Smiley-West.ifc | 3.89 | IFC2X_FINAL | — | — | — |  | tải được; ifcopenshell lỗi: Unsupported schema: IFC2X_FINAL |
| obim-testfiles | Ettenheim-GIS-05-11-2006.ifc | https://raw.githubusercontent.com/opensourceBIM/TestFiles/master/TestData/data/Ettenheim-GIS-05-11-2006.ifc | 29.63 | IFC2X_FINAL (header) | chưa xác minh | chưa xác minh | chưa xác minh |  | chỉ đọc header/size (>25MB, chưa tải) |
| obim-testfiles | FJK-Project-Final.ifc | https://raw.githubusercontent.com/opensourceBIM/TestFiles/master/TestData/data/FJK-Project-Final.ifc | 0.14 | IFC2X_FINAL | — | — | — |  | tải được; ifcopenshell lỗi: Unsupported schema: IFC2X_FINAL |
| obim-testfiles | HITOS_070308.ifc | https://raw.githubusercontent.com/opensourceBIM/TestFiles/master/TestData/data/HITOS_070308.ifc | 61.13 | IFC2X3 (header) | chưa xác minh | chưa xác minh | chưa xác minh |  | chỉ đọc header/size (>25MB, chưa tải) |
| obim-testfiles | Niedri_org.ifc | https://raw.githubusercontent.com/opensourceBIM/TestFiles/master/TestData/data/Niedri_org.ifc | 2.33 | IFC2X3 | 19 (19 có Repr.) | 514 | 4 | Windows System | đã tải+đếm |
| obim-testfiles | PART02_Wilfer_200302_20070209_IFC.ifc | https://raw.githubusercontent.com/opensourceBIM/TestFiles/master/TestData/data/PART02_Wilfer_200302_20070209_IFC.ifc | 0.69 | IFC2X3 | 0 (0 có Repr.) | 0 | 0 | VDI3805_View_FZK (FZK Version) | đã tải+đếm |
| obim-testfiles | Vogel_Gesamt.ifc | https://raw.githubusercontent.com/opensourceBIM/TestFiles/master/TestData/data/Vogel_Gesamt.ifc | 0.90 | IFC2X_FINAL | — | — | — |  | tải được; ifcopenshell lỗi: Unsupported schema: IFC2X_FINAL |
| obim-testfiles | WallOnly.ifc | https://raw.githubusercontent.com/opensourceBIM/TestFiles/master/TestData/data/WallOnly.ifc | 0.00 | IFC2X3 | 0 (0 có Repr.) | 0 | 1 | IFC Engine DLL version 1.02 beta | đã tải+đếm |
| obim-testfiles | WallOnlyAddedSpace.ifc | https://raw.githubusercontent.com/opensourceBIM/TestFiles/master/TestData/data/WallOnlyAddedSpace.ifc | 0.00 | IFC2X3 | 0 (0 có Repr.) | 0 | 1 | IFC Engine DLL version 1.02 beta | đã tải+đếm |
| obim-testfiles | example.ifc | https://raw.githubusercontent.com/opensourceBIM/TestFiles/master/TestData/data/example.ifc | 0.08 | IFC2X3 | 4 (4 có Repr.) | 8 | 1 | IFC Engine DLL version 1.02 beta | đã tải+đếm |
| obim-testfiles | export1.ifc | https://raw.githubusercontent.com/opensourceBIM/TestFiles/master/TestData/data/export1.ifc | 0.26 | IFC2X3 | 2 (2 có Repr.) | 0 | 3 | ArchiCAD 14.00 Release 1. Windows B | đã tải+đếm |
| obim-testfiles | ifc4.ifc | https://raw.githubusercontent.com/opensourceBIM/TestFiles/master/TestData/data/ifc4.ifc | 0.02 | IFC4RC4 | — | — | — |  | tải được; ifcopenshell lỗi: Unsupported schema: IFC4RC4 |
| obim-testfiles | ifc4Mep export 17-12-2013_IFC4.ifc | https://raw.githubusercontent.com/opensourceBIM/TestFiles/master/TestData/data/ifc4Mep%20export%2017-12-2013_IFC4.ifc | 28.24 | IFC4 (header) | chưa xác minh | chưa xác minh | chưa xác minh |  | chỉ đọc header/size (>25MB, chưa tải) |
| obim-testfiles | ifc4rac_basic_sample_project.ifc | https://raw.githubusercontent.com/opensourceBIM/TestFiles/master/TestData/data/ifc4rac_basic_sample_project.ifc | 24.22 | IFC4 | 14 (14 có Repr.) | 0 | 6 | 20131024_2115(x64) - Exporter 3.7.1 | đã tải+đếm |
| obim-testfiles | revit_quantities.ifc | https://raw.githubusercontent.com/opensourceBIM/TestFiles/master/TestData/data/revit_quantities.ifc | 0.08 | IFC2X3 | 7 (7 có Repr.) | 37 | 1 | 20070324_1700 | đã tải+đếm |
| yousheng | Ifc2s3_Duplex_Electrical.ifc | https://raw.githubusercontent.com/youshengCode/IfcSampleFiles/main/Ifc2s3_Duplex_Electrical.ifc | 1.53 | IFC2X3 | 1 (1 có Repr.) | 4 | 3 | 20121003_2115(x64) | đã tải+đếm |
| yousheng | Ifc2x3_Duplex_Architecture.ifc | https://raw.githubusercontent.com/youshengCode/IfcSampleFiles/main/Ifc2x3_Duplex_Architecture.ifc | 2.27 | IFC2X3 | 21 (21 có Repr.) | 265 | 4 | 20100326_1700 | đã tải+đếm |
| yousheng | Ifc2x3_Duplex_MEP.ifc | https://raw.githubusercontent.com/youshengCode/IfcSampleFiles/main/Ifc2x3_Duplex_MEP.ifc | 17.04 | IFC2X3 | 42 (42 có Repr.) | 8 | 3 | 20100326_1700 | đã tải+đếm |
| yousheng | Ifc2x3_Duplex_Mechanical.ifc | https://raw.githubusercontent.com/youshengCode/IfcSampleFiles/main/Ifc2x3_Duplex_Mechanical.ifc | 8.38 | IFC2X3 | 37 (37 có Repr.) | 8 | 3 | 20100903_2115(x64) | đã tải+đếm |
| yousheng | Ifc2x3_Duplex_Plumbing.ifc | https://raw.githubusercontent.com/youshengCode/IfcSampleFiles/main/Ifc2x3_Duplex_Plumbing.ifc | 30.09 | IFC2X3 (header) | chưa xác minh | chưa xác minh | chưa xác minh |  | chỉ đọc header/size (>25MB, chưa tải) |
| yousheng | Ifc2x3_SampleCastle.ifc | https://raw.githubusercontent.com/youshengCode/IfcSampleFiles/main/Ifc2x3_SampleCastle.ifc | 47.00 | chưa xác minh (header) | chưa xác minh | chưa xác minh | chưa xác minh |  | chỉ đọc header/size (>25MB, chưa tải) |
| yousheng | Ifc4_Revit_ARC.ifc | https://raw.githubusercontent.com/youshengCode/IfcSampleFiles/main/Ifc4_Revit_ARC.ifc | 13.01 | IFC4 | 0 (0 có Repr.) | 0 | 6 | 21.0.0.383 - Exporter 21.0.0.383 -  | đã tải+đếm |
| yousheng | Ifc4_Revit_ARC_FireRatingAdded.ifc | https://raw.githubusercontent.com/youshengCode/IfcSampleFiles/main/Ifc4_Revit_ARC_FireRatingAdded.ifc | 13.02 | IFC4 | 0 (0 có Repr.) | 0 | 6 | 21.0.0.383 - Exporter 21.0.0.383 -  | đã tải+đếm |
| yousheng | Ifc4_Revit_MEP.ifc | https://raw.githubusercontent.com/youshengCode/IfcSampleFiles/main/Ifc4_Revit_MEP.ifc | 27.81 | IFC4 (header) | chưa xác minh | chưa xác minh | chưa xác minh |  | chỉ đọc header/size (>25MB, chưa tải) |
| yousheng | Ifc4_Revit_STR.ifc | https://raw.githubusercontent.com/youshengCode/IfcSampleFiles/main/Ifc4_Revit_STR.ifc | 10.76 | IFC4 | 1 (1 có Repr.) | 0 | 0 | 21.0.0.383 - Exporter 21.0.0.383 -  | đã tải+đếm |
| yousheng | Ifc4_SampleHouse.ifc | https://raw.githubusercontent.com/youshengCode/IfcSampleFiles/main/Ifc4_SampleHouse.ifc | 2.17 | IFC4 | 4 (4 có Repr.) | 0 | 2 | Xbim version 4.0.0.0 | đã tải+đếm |
| yousheng | Ifc4_SampleHouse_0_GroundFloor.ifc | https://raw.githubusercontent.com/youshengCode/IfcSampleFiles/main/Ifc4_SampleHouse_0_GroundFloor.ifc | 2.07 | IFC4 | 2 (2 có Repr.) | 0 | 1 | Ifc.Toolbox v3.9 - BIM Mars | đã tải+đếm |
| yousheng | Ifc4_SampleHouse_1_Roof.ifc | https://raw.githubusercontent.com/youshengCode/IfcSampleFiles/main/Ifc4_SampleHouse_1_Roof.ifc | 0.06 | IFC4 | 0 (0 có Repr.) | 0 | 1 | Ifc.Toolbox v3.9 - BIM Mars | đã tải+đếm |
| ios-files | AC20-Institute-Var-2_227944.ifc | https://raw.githubusercontent.com/IfcOpenShell/files/master/tests/AC20-Institute-Var-2_227944.ifc | 0.12 | IFC4 | 0 (0 có Repr.) | 0 | 1 | IfcOpenShell 0.8.0 | đã tải+đếm |
| ios-files | ISSUE_005_haus_60012.ifc | https://raw.githubusercontent.com/IfcOpenShell/files/master/tests/ISSUE_005_haus_60012.ifc | 0.05 | IFC4 | 0 (0 có Repr.) | 0 | 1 | IfcOpenShell 0.8.0 | đã tải+đếm |
| ios-files | TestModel_IFC4Add2.ifc | https://raw.githubusercontent.com/IfcOpenShell/files/master/TestModel_IFC4Add2.ifc | 0.19 | IFC4 | 2 (2 có Repr.) | 0 | 2 | 20180328_1600(x64) - Exporter 19.0. | đã tải+đếm |
| webifc | AC20-FZK-Haus.ifc | https://raw.githubusercontent.com/ThatOpen/engine_web-ifc/main/tests/ifcfiles/public/AC20-FZK-Haus.ifc | 2.45 | IFC4 | 7 (7 có Repr.) | 81 | 2 | IFC file generated by GRAPHISOFT AR | đã tải+đếm |
| webifc | C20-Institute-Var-2.ifc | https://raw.githubusercontent.com/ThatOpen/engine_web-ifc/main/tests/ifcfiles/public/C20-Institute-Var-2.ifc | 10.43 | IFC4 | 82 (82 có Repr.) | 1000 | 5 | IFC file generated by GRAPHISOFT AR | đã tải+đếm |
| webifc | FM_ARC_DigitalHub.ifc | https://raw.githubusercontent.com/ThatOpen/engine_web-ifc/main/tests/ifcfiles/public/FM_ARC_DigitalHub.ifc | 13.66 | IFC4 | 64 (64 có Repr.) | 1123 | 3 | 20190108_1515(x64) - Exporter 19.3. | đã tải+đếm |
| webifc | ISSUE_005_haus.ifc | https://raw.githubusercontent.com/ThatOpen/engine_web-ifc/main/tests/ifcfiles/public/ISSUE_005_haus.ifc | 2.41 | IFC4 | 7 (7 có Repr.) | 81 | 2 | IFC file generated by GRAPHISOFT AR | đã tải+đếm |
| webifc | ISSUE_021_Mini Project.ifc | https://raw.githubusercontent.com/ThatOpen/engine_web-ifc/main/tests/ifcfiles/public/ISSUE_021_Mini%20Project.ifc | 3.20 | IFC2X3 | 0 (0 có Repr.) | 0 | 1 | Tekla Structures 2019i Service Pack | đã tải+đếm |
| webifc | ISSUE_034_HouseZ.ifc | https://raw.githubusercontent.com/ThatOpen/engine_web-ifc/main/tests/ifcfiles/public/ISSUE_034_HouseZ.ifc | 4.92 | IFC2X3 | 5 (5 có Repr.) | 0 | 3 | ASIFC - 2.15.0.991 | đã tải+đếm |
| webifc | ISSUE_068_ARK_NUS_skolebygg.ifc | https://raw.githubusercontent.com/ThatOpen/engine_web-ifc/main/tests/ifcfiles/public/ISSUE_068_ARK_NUS_skolebygg.ifc | 54.65 | IFC2X3 (header) | chưa xác minh | chưa xác minh | chưa xác minh |  | chỉ đọc header/size (>25MB, chưa tải) |
| webifc | ISSUE_098_R8_F1_MAB_AR_M3_XX_XXX_MO_7000.ifc | https://raw.githubusercontent.com/ThatOpen/engine_web-ifc/main/tests/ifcfiles/public/ISSUE_098_R8_F1_MAB_AR_M3_XX_XXX_MO_7000.ifc | 69.51 | IFC2X3 (header) | chưa xác minh | chưa xác minh | chưa xác minh |  | chỉ đọc header/size (>25MB, chưa tải) |
| webifc | ISSUE_102_M3D-CON-CD.ifc | https://raw.githubusercontent.com/ThatOpen/engine_web-ifc/main/tests/ifcfiles/public/ISSUE_102_M3D-CON-CD.ifc | 26.11 | IFC2X3 (header) | chưa xác minh | chưa xác minh | chưa xác minh |  | chỉ đọc header/size (>25MB, chưa tải) |
| webifc | ISSUE_102_M3D-CON.ifc | https://raw.githubusercontent.com/ThatOpen/engine_web-ifc/main/tests/ifcfiles/public/ISSUE_102_M3D-CON.ifc | 6.10 | IFC2X3 | 0 (0 có Repr.) | 0 | 3 | Tekla Structures 2020, IFC Export V | đã tải+đếm |
| webifc | ISSUE_126_model.ifc | https://raw.githubusercontent.com/ThatOpen/engine_web-ifc/main/tests/ifcfiles/public/ISSUE_126_model.ifc | 4.32 | IFC2X3 | 0 (0 có Repr.) | 0 | 3 | IFC file generated by GRAPHISOFT AR | đã tải+đếm |
| webifc | ISSUE_129_N1540_17_EXE_MOD_448200_02_09_11SMC_IGC_V17.ifc | https://raw.githubusercontent.com/ThatOpen/engine_web-ifc/main/tests/ifcfiles/public/ISSUE_129_N1540_17_EXE_MOD_448200_02_09_11SMC_IGC_V17.ifc | 11.67 | IFC2X3 | 0 (0 có Repr.) | 0 | 10 | 20160225_1515(x64) - Exporter 17.0. | đã tải+đếm |
| webifc | ISSUE_159_kleine_Wohnung_R22.ifc | https://raw.githubusercontent.com/ThatOpen/engine_web-ifc/main/tests/ifcfiles/public/ISSUE_159_kleine_Wohnung_R22.ifc | 9.73 | IFC4 | 28 (28 có Repr.) | 0 | 4 | BlenderBIM 0.0.220420 | đã tải+đếm |
| webifc | IfcOpenHouse_IFC4.ifc | https://raw.githubusercontent.com/ThatOpen/engine_web-ifc/main/tests/ifcfiles/public/IfcOpenHouse_IFC4.ifc | 0.11 | IFC4 | 0 (0 có Repr.) | 0 | 1 | IfcOpenShell 0.5.0-dev | đã tải+đếm |
| webifc | Office_A_20110811.ifc | https://raw.githubusercontent.com/ThatOpen/engine_web-ifc/main/tests/ifcfiles/public/Office_A_20110811.ifc | 3.91 | IFC2X3 | 99 (99 có Repr.) | 1334 | 3 | 20100326_1700 (Solibri IFC Optimize | đã tải+đếm |
| webifc | S_Office_Integrated Design Archi.ifc | https://raw.githubusercontent.com/ThatOpen/engine_web-ifc/main/tests/ifcfiles/public/S_Office_Integrated%20Design%20Archi.ifc | 29.62 | chưa xác minh (header) | chưa xác minh | chưa xác minh | chưa xác minh |  | chỉ đọc header/size (>25MB, chưa tải) |
| webifc | advanced_model.ifc | https://raw.githubusercontent.com/ThatOpen/engine_web-ifc/main/tests/ifcfiles/public/advanced_model.ifc | 33.67 | IFC2X3 (header) | chưa xác minh | chưa xác minh | chưa xác minh |  | chỉ đọc header/size (>25MB, chưa tải) |
| webifc | dental_clinic.ifc | https://raw.githubusercontent.com/ThatOpen/engine_web-ifc/main/tests/ifcfiles/public/dental_clinic.ifc | 12.40 | IFC2X3 | 269 (269 có Repr.) | 3124 | 4 | 20100326_1700 (Solibri IFC Optimize | đã tải+đếm |
| webifc | duplex.ifc | https://raw.githubusercontent.com/ThatOpen/engine_web-ifc/main/tests/ifcfiles/public/duplex.ifc | 2.27 | IFC2X3 | 21 (21 có Repr.) | 265 | 4 | 20100326_1700 | đã tải+đếm |
| webifc | example.ifc | https://raw.githubusercontent.com/ThatOpen/engine_web-ifc/main/tests/ifcfiles/public/example.ifc | 0.39 | IFC2X3 | 1 (1 có Repr.) | 0 | 2 | 21.1.20.44 - Exporter 21.1.20.44 -  | đã tải+đếm |
| webifc | schependomlaan.ifc | https://raw.githubusercontent.com/ThatOpen/engine_web-ifc/main/tests/ifcfiles/public/schependomlaan.ifc | 47.00 | chưa xác minh (header) | chưa xác minh | chưa xác minh | chưa xác minh |  | chỉ đọc header/size (>25MB, chưa tải) |
| webifc | tested_sample_project.ifc | https://raw.githubusercontent.com/ThatOpen/engine_web-ifc/main/tests/ifcfiles/public/tested_sample_project.ifc | 0.68 | IFC2X3 | 0 (0 có Repr.) | 0 | 2 | 21.0.0.383 - Exporter 21.0.0.383 -  | đã tải+đếm |
| ios-main | AC20-FZK-Haus.ifc | https://raw.githubusercontent.com/IfcOpenShell/IfcOpenShell/v0.9.0/docs/ifcopenshell-cpp/models/AC20-FZK-Haus.ifc | 2.41 | IFC4 | 7 (7 có Repr.) | 81 | 2 | IFC file generated by GRAPHISOFT AR | đã tải+đếm |
| ios-main | basic.ifc | https://raw.githubusercontent.com/IfcOpenShell/IfcOpenShell/v0.9.0/src/bonsai/test/files/basic.ifc | 0.01 | IFC4 | 0 (0 có Repr.) | 0 | 2 | Bonsai 0.0.999999 | đã tải+đếm |
| ios-main | sample.ifc | https://raw.githubusercontent.com/IfcOpenShell/IfcOpenShell/v0.9.0/src/ifcviewer-web/sample.ifc | 0.00 | IFC4 | 0 (0 có Repr.) | 0 | 1 | IfcOpenShell 0.0.0 | đã tải+đếm |
| ios-main | 6dbd4d52-14db-11ee-be56-0242ac120002.ifc | https://raw.githubusercontent.com/IfcOpenShell/IfcOpenShell/v0.9.0/src/opencdeserver/api/app/data/documents/6dbd4d52-14db-11ee-be56-0242ac120002.ifc | 0.02 | IFC2X3 | 0 (0 có Repr.) | 0 | 1 | IFC file generated by GRAPHISOFT AR | đã tải+đếm |
| ios-main | 78860d3c-14db-11ee-be56-0242ac120002.ifc | https://raw.githubusercontent.com/IfcOpenShell/IfcOpenShell/v0.9.0/src/opencdeserver/api/app/data/documents/78860d3c-14db-11ee-be56-0242ac120002.ifc | 0.02 | IFC2X3 | 0 (0 có Repr.) | 0 | 1 | IFC file generated by GRAPHISOFT AR | đã tải+đếm |
| ios-main | 78860e68-14db-11ee-be56-0242ac120002.ifc | https://raw.githubusercontent.com/IfcOpenShell/IfcOpenShell/v0.9.0/src/opencdeserver/api/app/data/documents/78860e68-14db-11ee-be56-0242ac120002.ifc | 0.02 | IFC2X3 | 0 (0 có Repr.) | 0 | 1 | IFC file generated by GRAPHISOFT AR | đã tải+đếm |
| ios-main | IFC4 Demo Template.ifc | https://raw.githubusercontent.com/IfcOpenShell/IfcOpenShell/v0.9.0/src/bonsai/bonsai/bim/data/templates/projects/IFC4%20Demo%20Template.ifc | 0.00 | ? | — | — | — |  | tải được; ifcopenshell lỗi: Unable to parse IFC SPF header |
| bimwhale | AdvancedProject.ifc | https://raw.githubusercontent.com/andrewisen/bim-whale-ifc-samples/main/AdvancedProject/IFC/AdvancedProject.ifc | 42.28 | chưa xác minh (header) | chưa xác minh | chưa xác minh | chưa xác minh |  | chỉ đọc header/size (>25MB, chưa tải) |
| bimwhale | BasicHouse.ifc | https://raw.githubusercontent.com/andrewisen/bim-whale-ifc-samples/main/BasicHouse/IFC/BasicHouse.ifc | 50.26 | chưa xác minh (header) | chưa xác minh | chưa xác minh | chưa xác minh |  | chỉ đọc header/size (>25MB, chưa tải) |
| bimwhale | LargeBuilding.ifc | https://raw.githubusercontent.com/andrewisen/bim-whale-ifc-samples/main/LargeBuilding/IFC/LargeBuilding.ifc | 1.23 | IFC2X3 | 8 (8 có Repr.) | 0 | 2 | 21.1.10.26 - Exporter 21.1.10.26 -  | đã tải+đếm |
| bimwhale | ManySimpleWalls.ifc | https://raw.githubusercontent.com/andrewisen/bim-whale-ifc-samples/main/ManySimpleWalls/IFC/ManySimpleWalls.ifc | 0.56 | IFC2X3 | 0 (0 có Repr.) | 0 | 1 | 21.1.10.26 - Exporter 21.1.10.26 -  | đã tải+đếm |
| bimwhale | SimpleWall.ifc | https://raw.githubusercontent.com/andrewisen/bim-whale-ifc-samples/main/SimpleWall/IFC/SimpleWall.ifc | 0.04 | IFC2X3 | 0 (0 có Repr.) | 0 | 1 | 21.1.0.108 - Exporter 21.1.0.108 -  | đã tải+đếm |
| bimwhale | TallBuilding.ifc | https://raw.githubusercontent.com/andrewisen/bim-whale-ifc-samples/main/TallBuilding/IFC/TallBuilding.ifc | 0.59 | IFC2X3 | 3 (3 có Repr.) | 0 | 5 | 21.1.10.26 - Exporter 21.1.10.26 -  | đã tải+đếm |
| obim-ifcfiles | architect.ifc | https://raw.githubusercontent.com/opensourcebim/ifc-files/master/HHS%20Office/architect.ifc | 12.48 | IFC2X3 | 33 (33 có Repr.) | 237 | 4 | 20090925_1815(x64) | đã tải+đếm |
| obim-ifcfiles | Schultz_Residence.ifc | https://raw.githubusercontent.com/opensourcebim/ifc-files/master/OpeningDesign.com/Schultz_Residence.ifc | 21.43 | IFC2X3 | 3 (3 có Repr.) | 0 | 11 | 20131024_2115(x64) - Exporter 3.2.0 | đã tải+đếm |
| thatopen-comp | school_str.ifc | https://raw.githubusercontent.com/ThatOpen/engine_components/main/resources/ifc/school_str.ifc | 8.20 | IFC4 | 0 (0 có Repr.) | 0 | 5 | Autodesk Revit 24.3.10.22 (ENU) - I | đã tải+đếm |
| ifcopenhouse | IfcOpenHouse.ifc | https://raw.githubusercontent.com/cvillagrasa/IfcOpenHouse/master/ifc/IfcOpenHouse.ifc | 0.97 | IFC4 | 0 (0 có Repr.) | 0 | 1 | IfcOpenShell 0.7.0 | đã tải+đếm |
| gbxml | rac_input1.ifc | https://raw.githubusercontent.com/brunopostle/IFC-to-gbXML-converter/master/Test%20cases/Michael%20RAC/rac_input1.ifc | 12.56 | IFC4 | 0 (0 có Repr.) | 0 | 6 | 22.0.2.392 - Exporter 22.0.2.392 -  | đã tải+đếm |
| gbxml | rac_input2.ifc | https://raw.githubusercontent.com/brunopostle/IFC-to-gbXML-converter/master/Test%20cases/Michael%20RAC/rac_input2.ifc | 25.46 | IFC2X3 (header) | chưa xác minh | chưa xác minh | chưa xác minh |  | chỉ đọc header/size (>25MB, chưa tải) |
| gbxml | Pilot project 1.ifc | https://raw.githubusercontent.com/brunopostle/IFC-to-gbXML-converter/master/Test%20cases/Pilot%20project%201/Pilot%20project%201.ifc | 0.21 | IFC2X3 | 10 (10 có Repr.) | 76 | 3 | 20150714_1515(x64) - Exporter 16.4. | đã tải+đếm |
| gbxml | Pilot project 2.ifc | https://raw.githubusercontent.com/brunopostle/IFC-to-gbXML-converter/master/Test%20cases/Pilot%20project%202/Pilot%20project%202.ifc | 0.30 | IFC2X3 | 11 (11 có Repr.) | 86 | 4 | 20150714_1515(x64) - Exporter 16.4. | đã tải+đếm |
| gbxml | Pilot project 3.ifc | https://raw.githubusercontent.com/brunopostle/IFC-to-gbXML-converter/master/Test%20cases/Pilot%20project%203/Pilot%20project%203.ifc | 0.53 | IFC2X3 | 12 (12 có Repr.) | 166 | 3 | 20150714_1515(x64) - Exporter 16.4. | đã tải+đếm |
| viktor | BuildingBIMModel.ifc | https://raw.githubusercontent.com/viktor-platform/ifc-sample-models/main/sample-models/BuildingBIMModel.ifc | 26.20 | IFC4 (header) | chưa xác minh | chưa xác minh | chưa xác minh |  | chỉ đọc header/size (>25MB, chưa tải) |
| viktor | SampleBuilding.ifc | https://raw.githubusercontent.com/viktor-platform/ifc-sample-models/main/sample-models/SampleBuilding.ifc | 6.43 | IFC4 | 0 (0 có Repr.) | 0 | 12 | Autodesk Revit 24.3.0.13 (ENU) - IF | đã tải+đếm |
| viktor | SampleBimModelWebinar.ifc | https://raw.githubusercontent.com/viktor-platform/ifc-sample-models/main/sample-models/SampleBimModelWebinar.ifc | 5.00 | IFC4 | 0 (0 có Repr.) | 0 | 5 | Autodesk Revit 25.3.0.46 (ENU) - IF | đã tải+đếm |

Ghi chú bảng 2b: file IFC2X_FINAL / IFC4RC4 (ADT-FZK-Haus, Allplan-Smiley-West, FJK-Project-Final, Vogel_Gesamt, ifc4.ifc) **ifcopenshell không mở được** ("Unsupported schema"). File >25 MB chỉ kiểm tra header + kích thước (link tải hoạt động), chưa đếm. Bản trùng: `yousheng/Ifc2x3_Duplex_*` = Community Duplex (cùng byte-size); `webifc/duplex.ifc` = Duplex_A; `webifc/dental_clinic.ifc` = Clinic_Architectural; `webifc/schependomlaan.ifc` & `yousheng/Ifc2x3_SampleCastle.ifc` = cùng kích thước 49 286 967 B với `IFC Schependomlaan.ifc`; `webifc/ISSUE_005_haus.ifc` = bản AC20-FZK-Haus trong IfcOpenShell docs.

### 2c. Chi tiết ground truth (đã phân tích bằng `detail.py`, `names.py`)

| file | schema | IfcSpace repr. | RSB `Name` (level) | ConnectionGeometry | PHYSICAL/VIRTUAL × INTERNAL/EXTERNAL | RelatedBuildingElement chính |
|---|---|---|---|---|---|---|
| AC20-FZK-Haus.ifc (webifc) | IFC4 | 7× Body/Brep + Box + FootPrint | `2ndLevel`, Description `2a` (81) | IfcCurveBoundedPlane (81) | P-I 34, P-E 36, V-I 6, V-E 5 | WallStandardCase 28, Slab 23, Window 11, Door 8, VirtualElement 6 |
| C20-Institute-Var-2.ifc (webifc) | IFC4 | 82× Brep | `2a` (1000) | IfcCurveBoundedPlane | P-I 630, P-E 362, V-E 8 | Wall 399, Slab 234, Window 206, Door 153 |
| FM_ARC_DigitalHub.ifc (webifc) | IFC4 | 61 SweptSolid + 3 AdvancedBrep | `2ndLevel` (1123) | IfcCurveBoundedPlane | V-I 184, P-E 418, P-I 521 | IfcWall 529, Slab 160, Door 138, Column 64 |
| Pilot project 1/2/3.ifc (gbXML) | IFC2X3 | SweptSolid | `2ndLevel` (76/86/166) | IfcCurveBoundedPlane | chỉ PHYSICAL | Wall, Slab, Window, Covering |
| AC11-FZK-Haus-IFC.ifc (obim) | IFC2X3 | 5 SweptSolid + 2 Clipping | `Second Level` (98) | IfcCurveBoundedPlane | P-I 48, P-E 42, V-I 8 | Wall 33, Slab 31, Window 11 |
| AC90R1-Jasmin-Sun / niedriha / AC9R1-Haus-G-H (obim) | IFC2X3 | SweptSolid/Clipping + BoundingBox | `Second Level` | IfcCurveBoundedPlane | có cả VIRTUAL | Wall, Slab, Door, Window |
| Duplex_A_20110907.ifc | IFC2X3 | 19 SweptSolid + 2 SurfaceModel | `1stLevel` (265) | 184 SurfaceOfLinearExtrusion + 81 CurveBoundedPlane | P-I 175, P-E 62, V 28 | Wall 106, Slab 58, Door 30 |
| Clinic_Architectural.ifc | IFC2X3 | SweptSolid | `1stLevel` (3124) | SurfaceOfLinearExtrusion | … | Wall 2401, Door 480 |
| Office_A_20110811.ifc | IFC2X3 | SweptSolid | `1stLevel` (1334) | 1231 SurfOfLinExtr + 103 CBP | … | Wall 1013, Door 180, Covering 103 |
| HHS Office architect.ifc | IFC2X3 | 16 SurfaceModel + 17 SweptSolid | `Name` rỗng (237) | 195 SurfOfLinExtr + 42 CBP | P-E 195, P-I 42 | Wall 121, Door 49 (license CC BY-ND) |

## Gợi ý chọn file

### Tầng S (nhỏ, < ~5 MB) – đều đã tải + đếm thật

| # | file | schema | MB | IfcSpace (geom) | RSB | tầng | giấy phép | lý do |
|---|---|---|---|---|---|---|---|---|
| S1 | buildingSMART `Simple-Scene/Building-Architecture.ifc` (IFC4) | IFC4 | 0.14 | 2 (SweptSolid) | 0 | 1 | CC BY 4.0 | Chính chủ bSI, tối giản; có cả bản 2x3 và 4x3 cùng mô hình → test đa schema |
| S2 | buildingSMART `Simple-Scene/Building-Architecture.ifc` (IFC2x3) | IFC2X3 | 0.09 | 2 | 0 | 1 | CC BY 4.0 | như trên |
| S3 | `AC20-FZK-Haus.ifc` (KIT, bản engine_web-ifc hoặc IfcOpenShell docs) | IFC4 | 2.45 | 7 (Brep) | 81 (2nd level) | 2 | KIT "unrestricted use" (chưa xác minh trên ifcwiki); repo chứa: MPL-2.0 / LGPL-3.0 | **Ground truth IFC4 2nd-level**, nhà 2 tầng mái dốc |
| S4 | `Pilot project 1.ifc` (IFC-to-gbXML-converter) | IFC2X3 | 0.21 | 10 (SweptSolid) | 76 (2ndLevel) | 3 | GPL-3.0 (repo) | Ground truth IFC2x3 2nd-level, rất nhỏ; có thêm Pilot 2 (0.30 MB, 11/86, 4 tầng) và Pilot 3 (0.53 MB, 12/166) |
| S5 | `AC11-FZK-Haus-IFC.ifc` (opensourceBIM TestFiles) | IFC2X3 | 3.96 | 7 | 98 ("Second Level") | 2 | GPL-3.0 nhãn repo; gốc KIT | Cùng nhà FZK ở IFC2x3 → đối chiếu 2x3 vs IFC4 |
| S6 | `Duplex_A_20110907.ifc` (Community, LFS) | IFC2X3 | 2.27 | 21 (19 SweptSolid + 2 SurfaceModel) | 265 (1stLevel) | 4 | CC BY 4.0 | Mẫu "Hello World" phổ biến; RSB 1st level |
| S7 | `TestModel_IFC4Add2.ifc` (IfcOpenShell/files) | IFC4 | 0.19 | 2 | 0 | 2 | chưa xác minh | Revit 2019 IFC4, nhỏ, không có RSB → test suy luận |
| S8 | `Ifc4_SampleHouse.ifc` (youshengCode) | IFC4 | 2.17 | 4 | 0 | 2 | chưa xác minh | IFC4 xBIM, có space, không RSB |
| S9 | `AC90R1-Jasmin-Sun-105-2x3.ifc` (obim) | IFC2X3 | 3.07 | 10 | 135 (Second Level) | 3 | GPL-3.0 nhãn repo | ArchiCAD 9, có cả VIRTUAL boundary |
| S10 | `4351.ifc` (obim) | IFC2X3 | 6.95 (hơi > 5MB) | 6 | 142 (1stLevel) | 5 | GPL-3.0 nhãn repo | Revit 2011, ít space nhiều tầng |

Đề xuất bộ tối thiểu: **S1 + S2 (đa schema, không RSB) + S3 (IFC4 GT) + S4 (IFC2x3 GT 2nd) + S6 (IFC2x3 GT 1st)** — 5 file, tổng ~5 MB, cả 5 có IfcSpace có hình học, ≥3 có RSB ground truth.

### Ứng viên nhiều tầng / tầng M–L

| file | schema | MB | IfcSpace | RSB | tầng | giấy phép |
|---|---|---|---|---|---|---|
| AC20-Institute-Var-2 (`C20-Institute-Var-2.ifc`, engine_web-ifc) | IFC4 | 10.43 | 82 (Brep) | 1000 (2a) | 5 | KIT (chưa xác minh) / repo MPL-2.0 |
| AC11-Institute-Var-2-IFC.ifc (obim) | IFC2X3 | 2.70 | 82 | 1175 (Second Level) | 5 | GPL-3.0 nhãn repo |
| FM_ARC_DigitalHub.ifc (engine_web-ifc) | IFC4 | 13.66 | 64 | 1123 (2ndLevel) | 3 | chưa xác minh |
| AC9R1-Haus-G-H-Ver2-2x3.ifc (obim) | IFC2X3 | 4.35 | 26 | 513 | 4 | GPL-3.0 nhãn repo |
| AC90R1-niedriha-V2-2x3.ifc (obim) | IFC2X3 | 2.33 | 19 | 514 | 4 | GPL-3.0 nhãn repo |
| Office_A_20110811.ifc (engine_web-ifc; gốc Common BIM Files) | IFC2X3 | 3.91 | 99 | 1334 (1stLevel) | 3 | gốc NIBS/bSa (chưa xác minh) |
| Clinic_Architectural.ifc (Community, LFS) | IFC2X3 | 12.40 | 269 | 3124 (1stLevel) | 4 | CC BY 4.0 |
| 1807_EP_AR_v18.ifc – Esplanades (Community, LFS) | IFC2X3 | 11.55 | 285 (Brep) | 0 | 7 | CC BY 4.0 → tốt để test suy luận quy mô lớn |
| example project location.ifc – Gymzaal Amersfoort (Community, LFS) | IFC4 | 2.82 | 48 | 0 | 3 | CC BY 4.0 (theo README gốc repo) |
| ifc4rac_basic_sample_project.ifc (obim; Revit sample) | IFC4 | 24.22 | 14 | 0 | 6 | GPL-3.0 nhãn repo; gốc Autodesk (chưa xác minh) |
| ISSUE_159_kleine_Wohnung_R22.ifc (engine_web-ifc) | IFC4 | 9.73 | 28 | 0 | 4 | chưa xác minh |
| HHS Office architect.ifc (opensourcebim/ifc-files) | IFC2X3 | 12.48 | 33 | 237 | 4 | CC BY-ND 4.0 (không phát hành bản sửa) |

## Host cần mở mạng (để claude-01 xin quyền)

- `www.ifcwiki.org` – trang KIT IFC Examples (xác minh license "unrestricted use" và link gốc).
- `openifcmodel.cs.auckland.ac.nz` – Open IFC Model Repository.
- `bimcorner.com` – BIMCorner (chưa xác định được trang mẫu).
- `www.wbdg.org` – Common BIM Files (Duplex/Office/Clinic gốc, license gốc).
- (Đã hoạt động, không cần xin: `github.com` git, `raw.githubusercontent.com`, `media.githubusercontent.com`.)

## Nguồn (truy cập 2026-11-10)

- https://github.com/buildingSMART/Sample-Test-Files (LICENSE, README)
- https://github.com/buildingsmart-community/Community-Sample-Test-Files (README gốc, README Duplex/Clinic/Esplanades/Schependomlaan/Example project location)
- https://github.com/openBIMstandards/DataSetSchependomlaan (README "has moved")
- https://github.com/opensourceBIM/TestFiles (TestData/license.txt)
- https://github.com/opensourcebim/ifc-files (README CC BY-ND)
- https://github.com/youshengCode/IfcSampleFiles
- https://github.com/IfcOpenShell/IfcOpenShell (COPYING.LESSER; docs/ifcopenshell-cpp/models/AC20-FZK-Haus.ifc)
- https://github.com/IfcOpenShell/files
- https://github.com/ThatOpen/engine_web-ifc (LICENSE.md MPL-2.0; tests/ifcfiles/public)
- https://github.com/ThatOpen/engine_components
- https://github.com/andrewisen/bim-whale-ifc-samples (LICENSE MIT)
- https://github.com/brunopostle/IFC-to-gbXML-converter (LICENSE GPL-3.0; Test cases)
- https://github.com/cvillagrasa/IfcOpenHouse (LICENSE Apache-2.0)
- https://github.com/viktor-platform/ifc-sample-models
- Chỉ qua WebSearch (chưa mở trang): https://downloads.steptools.com/docs/stpfiles/ifc/ ; https://vps.visionsdureel.ch/en/sample-ifc-file.html (câu "unrestricted use" của KIT); https://researchspace.auckland.ac.nz/handle/2292/16583 ; https://code-repo.d4science.org/... re3data r3d100012443 (CC BY 3.0, 130 models); https://wbdg.org/node/23884 ; https://wbdg.org/node/9165 ; https://help.autodesk.com/cloudhelp/2014/ENU/Revit/files/GUID-4EED7335-DCC7-48AD-A8BD-8156CAB27A33.htm

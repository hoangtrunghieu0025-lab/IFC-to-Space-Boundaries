> **Báo cáo thô** của subagent hỗ trợ claude-01 (TASK-001), ngày 2026-11-10, chép nguyên văn từ scratchpad để lưu vết. Đường dẫn `/tmp/…/scratchpad/…` và `dl/`, `dl2/`, `scripts/` nhắc trong báo cáo là thư mục tạm của phiên, **không còn tồn tại**. Bản tổng hợp đã kiểm lại: `../dataset-survey.md`, `../dataset-search-log.md`.

# Khảo sát nguồn IFC trên các host mới mở (hỗ trợ TASK-001)

Ngày truy cập mọi URL: 2026-11-10. Công cụ: `curl -sSL` qua proxy; đo bằng ifcopenshell 0.9.0.post1.
Lưu ý đo đạc: máy KHÔNG có `/usr/bin/time` (`No such file or directory`), nên thời gian/RAM đo bằng script
`scratchpad/scripts/count.py` (Python `time.time()` + `resource.getrusage(RUSAGE_SELF).ru_maxrss`), tương đương
"elapsed" và "Maximum resident set size" của tiến trình Python (chỉ gồm `ifcopenshell.open` + `by_type`, không gồm geometry).
Máy: 4 vCPU, 15 GB RAM. Thư mục tải: `scratchpad/dl2/<nguồn>/`.

Cột đo: `schema | IfcProduct | IfcSpace | IfcRelSpaceBoundary (RSB) | IfcBuildingStorey | elapsed | maxRSS`.

---

## 1. KIT IFC Examples (ifcwiki.org)

- URL đã mở: https://www.ifcwiki.org/index.php?title=KIT_IFC_Examples (HTTP 200).
- Lưu ý: link trên trang dùng `http://www.ifcwiki.org/...` → curl lỗi `Could not resolve host` qua http; dùng `https://` thì tải được.

### Điều khoản sử dụng (nguyên văn, mục "Please Note!")
> These examples are made by the Institute for Applied Computer Science (IAI) at the Karlsruhe Institute of Technology (KIT), and are for **unrestricted use**. If you use these examples for publications, please provide the following **source:** **Institute for Automation and Applied Informatics (IAI) / Karlsruhe Institute of Technology (KIT) or Institut für Automation und angewandte Information / Karlsruher Institut für Technologie**

(Không phải giấy phép chuẩn như CC; văn bản nói "unrestricted use" + yêu cầu ghi nguồn khi xuất bản.)

### Danh sách model trên trang (đủ 5 mục)
| Tên trên trang | Mô tả | IFC Version | Phần mềm | URL tải trực tiếp (https) | Size |
|---|---|---|---|---|---|
| FZK Haus | Simple Phantasy Building | IFC 4 | ArchiCAD 20 | https://www.ifcwiki.org/images/e/e3/AC20-FZK-Haus.ifc | 2 570 803 B |
| Office Building | Phantasy Office Building | IFC 4 | ArchiCAD 20 | https://www.ifcwiki.org/images/9/98/AC20-Institute-Var-2.ifc | 10 934 237 B |
| Smiley West | terraced houses | IFC 4 | ArchiCAD 20 | https://www.ifcwiki.org/images/c/c8/AC-20-Smiley-West-10-Bldg.zip | 1 280 471 B (zip; IFC bên trong 6 109 213 B) |
| KIT-Bridge | Simple Phantasy Bridge | IFC 4x2 | Sketchup - KIT manually edited | https://www.ifcwiki.org/images/0/09/KIT-Bridge.zip | chưa tải |
| KIT-Simple-Road-Test | Simple Phantasy Road | IFC 4x3_RC2 | Sketchup - KIT manually edited | https://www.ifcwiki.org/images/2/24/KIT-Simple-Road-Test-Web-IFC4x3_RC2.zip | chưa tải |

Không có model lớn/đông người hơn trên trang này (chỉ 3 công trình nhà + cầu + đường).

### Đo đạc (đã tải về `dl2/kit/`)
| File | sha256 (đầu) | schema | Product | Space | RSB | Storey | elapsed | maxRSS |
|---|---|---|---|---|---|---|---|---|
| AC20-FZK-Haus.ifc | 70cc8ff2… | IFC4 | 127 | 7 | 81 | 2 | 0.1 s | 79 MB |
| AC20-Institute-Var-2.ifc | cfb21244… | IFC4 | 1190 | 82 | 1000 | 5 | 0.3 s | 122 MB |
| AC-20-Smiley-West-10-Bldg.ifc (từ zip b6330136…) | — | IFC4 | 1272 | 140 | 1689 | 5 | 0.2 s | 99 MB |

Phân loại RSB (PhysicalOrVirtual / InternalOrExternal):
- Institute-Var-2: PHYSICAL/INTERNAL 630, PHYSICAL/EXTERNAL 362, VIRTUAL/EXTERNAL 8.
- Smiley West: PHYSICAL/INTERNAL 1012, PHYSICAL/EXTERNAL 554, VIRTUAL/EXTERNAL 95, VIRTUAL/INTERNAL 28.
- Tất cả là entity `IfcRelSpaceBoundary` (không phải subtype 1st/2nd level của IFC4) — cấp boundary chưa xác minh.

Ghi chú: Zenodo có bản "KIT Smiley West corrected" (DOI 10.5281/zenodo.10680698, CC-BY-4.0, `smiley-west.ifc` 6.1 MB) — chưa tải.

Trạng thái: **ĐÃ XÁC MINH + TẢI 3 FILE**. Ứng viên tốt làm ground truth RSB (có sẵn IfcSpace + RSB do ArchiCAD xuất).

---

## 2. WBDG Common BIM Files

- URL đã mở: https://www.wbdg.org/bim/cobie/common-bim-files , https://www.wbdg.org/node/23884 , https://www.wbdg.org/bim/common-bim-files → cả ba trả HTTP 200 nhưng chỉ là vỏ SPA 1 359 byte (`<div id="root"></div>`, JS `/assets/index-DvT-57Dk.js`, API base `https://www.wbdg.org/api/`). Nội dung (giấy phép, danh sách model) được nạp bằng JavaScript.
- Thử gọi các endpoint `https://www.wbdg.org/api/...` để lấy nội dung: **bị chặn** (lệnh bị từ chối quyền bởi bộ phân loại auto-mode; không thử lách).
- Giấy phép nguyên văn: **chưa xác minh** (không đọc được nội dung trang).
- Danh sách model / URL tải: **chưa xác minh**. Thông tin gián tiếp (KHÔNG phải nguồn gốc, chỉ để tham khảo): file CSV trong GNI BIM Dataset (Zenodo 19722012) ghi: `NIBS "Common BIM" Files (USA), "Sample BIM projects (e.g., Medical Clinic) from NIBS", "4 projects (IFC, RVT, etc.)", "Creative Commons (open use)", https://www.wbdg.org/bim/cobie/common-bim-files`.
- Trạng thái: **bị chặn / chưa xác minh**. Cần trình duyệt có JS hoặc quyền gọi API wbdg.org để tiếp tục.

---

## 3. BIMCorner (bimcorner.com)

- URL đã mở: https://bimcorner.com/ (200), tìm kiếm WordPress `https://bimcorner.com/?s=ifc+files`, `?s=sample+ifc`, và REST `https://bimcorner.com/wp-json/wp/v2/search?search=<q>` với q = "ifc files", "sample", "free ifc", "ifc models", "download ifc", "ifc model examples".
- Thử URL đoán https://bimcorner.com/ifc-sample-files/ → 404.
- Kết quả: **không tìm thấy trang "IFC sample files" / thư viện IFC mẫu nào** trên bimcorner.com. Các kết quả chỉ là bài viết (blog). Bài liên quan nhất: https://bimcorner.com/same-bridge-three-ifc-files/ — ghi nguyên văn: "Want to look at the three files yourself? Open them in the free demo of the Road to BIM IFC Viewer and download them from there" (3 IFC cầu, tải qua roadtobim.com — host chưa mở, không phải công trình có IfcSpace). Trang có form "Download BIM CASE STUDIES" / newsletter (đăng ký e-mail), không phải IFC.
- Giấy phép: **không có** (không tìm thấy file mẫu nào để có giấy phép).
- Trạng thái: **đã kiểm, không có nguồn IFC mẫu dùng được** (Office/Residential/Industrial như mô tả nhiệm vụ: chưa xác minh tồn tại).

---

## 4. Zenodo

### 4a. GNI BIM Dataset
- API: https://zenodo.org/api/records/19722011 → redirect về https://zenodo.org/api/records/19722012 (version 1.0.0, ngày 2026-04-24). DOI concept 10.5281/zenodo.19722011, DOI version 10.5281/zenodo.19722012.
- Tác giả: Wang, Zijian; Fuchs, Stefan; Wu, Jiabin; Esser, Sebastian; Wrabel, Tamira; Borrmann, André (TUM GNI).
- License metadata: `cc-by-4.0`. File LICENSE (nguyên văn):
  > Copyright (C) 2026 Zijian Wang, Stefan Fuchs, Jiabin Wu, Sebastian Esser, Tamira Wrabel, André Borrmann (Technical University of Munich, Georg Nemetschek Institute).
  > The contents of this dataset are licensed under the Creative Commons Attribution 4.0 International Public License (CC BY 4.0).
  > https://creativecommons.org/licenses/by/4.0/
- README nhắc: dữ liệu từ bài tập sinh viên, "provided **as is**, with no warranty"; "One 536 MB architectural file from BIM Project could not be loaded on our machine and was skipped".

| File | Size (B) | URL |
|---|---|---|
| 2025_BIMfundamentals.zip | 503 285 210 | https://zenodo.org/api/records/19722012/files/2025_BIMfundamentals.zip/content (208 model 1 môn, "a specific shape building" — chưa tải) |
| 2026_BIMprojects.zip | 221 053 555 | https://zenodo.org/api/records/19722012/files/2026_BIMprojects.zip/content (ĐÃ TẢI, 51 s) |
| other_online_BIM_model_resources.csv | 6 839 | …/files/other_online_BIM_model_resources.csv/content (đã tải; 35 nguồn) |
| README.md, LICENSE, class_distribution.png, group6.png | nhỏ | — |

Đo các model kiến trúc trong 2026_BIMprojects (giải nén tại `dl2/zenodo/gni/2026_BIMprojects/`):
| File | Size | schema | Product | Space | RSB | Storey | elapsed | maxRSS | Loại công trình (suy từ tên IfcSpace) |
|---|---|---|---|---|---|---|---|---|---|
| model_0_arc.ifc | 7.1 MB | IFC2X3 | 2150 | 0 | 0 | 9 | 0.3 s | 104 MB | — |
| model_1_arc.ifc | 187 MB | IFC2X3 | 34268 | 27 | 0 | 6 | 5.1 s | 1141 MB | học tập (Study Area…) |
| model_2_arc.ifc | 106 MB | IFC2X3 | 589 | 31 | 0 | 6 | 2.4 s | 625 MB | học tập (LEARNING HALL, QUIET ROOMS) |
| model_3_arc.ifc | 13.8 MB | IFC2X3 | 1735 | 0 | 0 | 5 | 0.3 s | 143 MB | — |
| model_4_arc.ifc | 52 MB | IFC2X3 | 1419 | 17 | 0 | 8 | 1.5 s | 361 MB | học tập/studio |
| model_5_arc.ifc | 77 MB | IFC2X3 | 3142 | 20 | 0 | 0 | 2.0 s | 495 MB | văn phòng (Forum, Workspace) — 0 IfcBuildingStorey |
| model_6_arc.ifc | 562 MB | IFC2X3 (Revit 2026) | 981 | 46 | 0 | 11 | 14.5 s | 3119 MB | (file 536 MB README nói không load được — ifcopenshell mở được) |
| model_7_arc.ifc | 9.4 MB | IFC2X3 | 1243 | 31 | 0 | 5 | 0.2 s | 118 MB | học tập (Study Zone, Lobby, Terrace) |
| model_8_arc.ifc | 22 MB | IFC4 | 702 | 0 | 0 | 4 | 0.5 s | 153 MB | — |

Nhận xét: **không có stadium/arena/hospital/mall/airport**; các model là thư viện/trung tâm học tập cỡ vừa (5–11 tầng, ≤46 IfcSpace), **không có RSB nào** → phù hợp làm input "suy ra IfcSpace / sinh RSB" (thiếu ground truth RSB). File lớn (model_6, model_1) hữu ích để test hiệu năng: RAM tăng mạnh theo dung lượng (562 MB → ~3.1 GB RSS chỉ để parse).

### 4b. Tìm kiếm Zenodo
Lưu ý cú pháp: search tự do `q=stadium%20ifc` trả 2057 kết quả nhiễu (từ "IFC" = Instituto Federal Catarinense…). Tham số `size` tối đa 25 khi không đăng nhập. Lọc hiệu quả bằng `file_type=ifc`: `https://zenodo.org/api/records?q=ifc&file_type=ifc&size=25` (+`&page=2`) → **34 record** có file .ifc.
- `q=stadium|arena|hospital|airport|school&file_type=ifc` → **0 kết quả** mỗi từ. `q="IfcSpace"` → 0 kết quả.
- `q=ifc space boundary` → chỉ ra record 14238135 (demo_building.ifc 0.2 MB) và các record công cụ.

Record liên quan nhất (license theo metadata API, size file .ifc):
| Record / DOI | Tiêu đề | License | File .ifc (MB) | Ghi chú |
|---|---|---|---|---|
| 10.5281/zenodo.15782433 | SmartlivingEPC public building BIM model and measurements | cc-by-4.0 | DS3_TalTech_V4.ifc 38.7 | Toà văn phòng + phòng thí nghiệm TalTech (Tallinn). **ĐÃ TẢI + ĐO** (dưới) |
| 10.5281/zenodo.22125339 | Integrated digital building information system (BIM model) (RETIME) | **None (không ghi license)** | Educational_Lisbon_Portugal 74.2; Residential_Tartu 77.9; Residential_Lisbon 57.3; SocialServices_Zilina 15.9 | Trường học — nhưng license không rõ → không tải |
| 10.5281/zenodo.5047709 | IFC Building Models for Automated Extraction of Data from Balconies | cc-by-4.0 | a2/a6 261.9; a5 36.2; a3 8.5; a1,a4,a7,a8 ≤2 | nhà ở có ban công; chưa tải |
| 10.5281/zenodo.21470658 | RestageIFC (Reference Construction Site Aachen) | cc-by-4.0 | Restage_IP_ALL_MULTI_001.ifc 189.8 | chưa tải |
| 10.5281/zenodo.7948116 | Indoor point cloud dataset for BIM related applications | cc-by-4.0 | craslabbim.ifc 67.6 | chưa tải |
| 10.5281/zenodo.21924325 | Case A Existing Parking House (IFC 4.3) | cc-by-4.0 | 72.0 | nhà xe |
| 10.5281/zenodo.10937432 / 10931088 | Rame Tower (HBIM) | cc-by-4.0 | 19.5 | di tích |
| 10.5281/zenodo.6685810 | BIM4EEB Demonstration building | cc-by-4.0 | ITA 9.4; FIN 2.0; POL 1.3 | |
| 10.5281/zenodo.6397164 | IFC architectural building models | cc-by-4.0 | 0.9/1.5/4.3 | |
| 10.5281/zenodo.10610773 | DuplexModel+MEP | cc-by-4.0 | Architecture 1.7 + MEP | |
| 10.5281/zenodo.21820756 / 21727160 | Office archetypes 1970/1998/2026 (Klassiqua) | cc-by-4.0 | ~1.3–1.5 mỗi file | |
| 10.5281/zenodo.19150057 | IDScribe dataset | cc-by-4.0 | Architecture Model.ifc 8.0 | |
| 10.5281/zenodo.18414845 | AccesS (CERTH smarthouse) | cc-by-4.0 | 8.2 | |
| 10.5281/zenodo.23808860 | SUM4Re LiDAR dataset | cc-by-4.0 | Target 24.1; Anoeta 4.2; Donor 3.6… | "Anoeta" là địa danh; loại công trình chưa xác minh |
| 10.5281/zenodo.19048493 | RWTH Campus Melaten site model | cc-by-nc-4.0 | 4.5 | NC |
| 10.5281/zenodo.14238135 | Dynamic energy assessment … using IFC | cc-by-4.0 | demo_building.ifc 0.2 | |
| 10.5281/zenodo.10680698 | KIT Smiley West corrected | cc-by-4.0 | 6.1 | |

Đo DS3_TalTech_V4.ifc (tải từ https://zenodo.org/api/records/15782433/files/DS3_TalTech_V4.ifc/content, 38 728 810 B, lưu `dl2/zenodo/`):
| schema | Product | Space | RSB | Storey | elapsed | maxRSS |
|---|---|---|---|---|---|---|
| IFC4 | 5530 | 115 | 1927 | 5 | 1.0 s | 270 MB |
RSB: PHYSICAL/INTERNAL 1587, PHYSICAL/EXTERNAL 263, VIRTUAL/INTERNAL 77. Tên IfcSpace đều là "Space" (không có LongName chức năng). IfcBuilding Name rỗng.
→ **Ứng viên tốt nhất trong đợt này**: công trình công cộng thật, CC-BY-4.0, có sẵn 115 IfcSpace + 1927 RSB làm ground truth.

Trạng thái Zenodo: **ĐÃ XÁC MINH**; **không tìm thấy IFC stadium/arena/hội trường/bệnh viện/mall/airport** trên Zenodo (theo `file_type=ifc`).

---

## 5. Hugging Face

### 5a. RPTU-FGMB/DeKH (German Hospital Dataset)
- API: https://huggingface.co/api/datasets/RPTU-FGMB/DeKH ; tree: https://huggingface.co/api/datasets/RPTU-FGMB/DeKH/tree/main?recursive=true
- `gated: "auto"`; license tag `cc-by-nc-sa-4.0`. README (tải được, HTTP 200) mục License nguyên văn:
  > This dataset is released under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) (Attribution-NonCommercial-ShareAlike). It may not be used for commercial purposes.
- Mô tả: "multi-scene dataset of real hospital environments comprising high-resolution 3D point clouds with semantic annotations and ground-truth IFC BIM models" (arXiv 2604.24311, EC3 2026).
- File IFC (size theo tree API):
  | Path | Size (B) | Ghi chú |
  |---|---|---|
  | Buildings/A/DeKH_A.ifc | 3 203 398 | ground truth |
  | Buildings/B/DeKH_B_ICU.ifc | 1 040 427 | ground truth (ICU) |
  | Buildings/C/DeKH_C_surgery.ifc | 395 114 | ground truth (phòng mổ) |
  | Buildings/A/1st_floor/DeKH_A_1st_floor_pred_2025-06-03.ifc | 60 762 | dự đoán pipeline |
  | Buildings/A/2nd_floor/DeKH_A_2nd_floor_pred_2025-06-03.ifc | 100 592 | dự đoán |
  | Buildings/B/DeKH_B_ICU_pred_2025-06-03.ifc | 39 905 | dự đoán |
  | Buildings/C/DeKH_C_surgery_pred_2025-06-03.ifc | 47 344 | dự đoán |
- Thử tải https://huggingface.co/datasets/RPTU-FGMB/DeKH/resolve/main/Buildings/A/DeKH_A.ifc → **HTTP 401**: "Access to dataset RPTU-FGMB/DeKH is restricted. You must have access to it and be authenticated to access it. Please log in." → cần tài khoản HF + chấp nhận điều kiện + token. **Chưa tải**; schema/IfcSpace: chưa xác minh. Lưu ý license **NonCommercial**.

### 5b. BIM-Edit/BIM-Edit
- API: https://huggingface.co/api/datasets/BIM-Edit/BIM-Edit (gated: false, tag `license:cc-by-4.0`); README.md nguyên văn chỉ có front-matter `license: cc-by-4.0`.
- Tree: 156 mục; thư mục `simple/` (~100 IFC nhỏ 15–490 KB, cặp input/gt) và `complex/` (IFC 4.7 MB → 349 MB). File lớn nhất: complex/093ec38d4859*.ifc ~349 MB; 0e29802b440f*.ifc ~225 MB; 9fc9f7d62d4a*.ifc ~161 MB; 65dc48e7147a*.ifc ~155–158 MB; 6dc4da160a96*.ifc ~149 MB; 9d81a20e025d*.ifc ~47 MB; 3ca337cf0aef*.ifc ~21 MB; 1c98aa6c7ea5*.ifc ~16 MB; 91ced022fd65*.ifc ~12 MB. Loại công trình của các file lớn: chưa xác minh (tên là hash).
- Tải file LFS/Xet (vd. complex/9d81a20e025d.ifc): huggingface.co trả **302** sang `https://us.aws.cdn.hf.co/xet-bridge-us/...` → proxy **403 CONNECT tunnel failed** → **bị chặn. Host CDN cần mở thêm: `us.aws.cdn.hf.co`** (có thể còn host CDN khác theo vùng — chưa xác minh).
- File không qua LFS tải được trực tiếp: complex/1fd06ad21e9e.ifc (5 256 001 B, https://huggingface.co/datasets/BIM-Edit/BIM-Edit/resolve/main/complex/1fd06ad21e9e.ifc), lưu `dl2/hf/bimedit/`:
  | schema | Product | Space | RSB | Storey | elapsed | maxRSS |
  |---|---|---|---|---|---|---|
  | IFC4X3 | 1073 | 36 | 360 | 4 | 0.1 s | 95 MB |
  IfcSpace: Büro 8, Sanitär 6, Labor 5, Seminar 3, Flur 3, **Hörsaal 2**, Foyer 1… (toà nhà giảng đường/viện). RSB: PHYSICAL/INTERNAL 272, PHYSICAL/EXTERNAL 81, VIRTUAL/INTERNAL 7. Nhiều file complex/ ~4.7–5.4 MB khác có vẻ là biến thể của cùng model (chưa xác minh).
- Trạng thái: license rõ (CC-BY-4.0); file nhỏ tải được; file lớn **bị chặn bởi CDN**.

---

## Tóm tắt host CDN / chặn
- `us.aws.cdn.hf.co` — cần mở để tải file LFS/Xet của Hugging Face (BIM-Edit complex lớn).
- DeKH: cần đăng nhập HF + token (không phải vấn đề host).
- wbdg.org: nội dung qua SPA/API; gọi `www.wbdg.org/api/...` bị từ chối quyền.
- `http://www.ifcwiki.org` không resolve; dùng `https://`.

## Nguồn (truy cập 2026-11-10)
- https://www.ifcwiki.org/index.php?title=KIT_IFC_Examples
- https://www.wbdg.org/bim/cobie/common-bim-files
- https://bimcorner.com/ ; https://bimcorner.com/wp-json/wp/v2/search?search=ifc%20files ; https://bimcorner.com/same-bridge-three-ifc-files/
- https://zenodo.org/api/records/19722012 ; https://doi.org/10.5281/zenodo.19722011
- https://zenodo.org/api/records?q=ifc&file_type=ifc&size=25
- https://zenodo.org/api/records/15782433 ; https://zenodo.org/api/records/22125339 ; https://zenodo.org/api/records/5047709
- https://huggingface.co/api/datasets/RPTU-FGMB/DeKH ; https://huggingface.co/datasets/RPTU-FGMB/DeKH
- https://huggingface.co/api/datasets/BIM-Edit/BIM-Edit ; https://huggingface.co/api/datasets/BIM-Edit/BIM-Edit/tree/main?recursive=true

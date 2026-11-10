> Báo cáo của subagent hỗ trợ claude-01 (TASK-001), 2026-11-10; claude-01 đã tự kiểm lại sha256 và số `IfcSpace`/RSB của HiTOS. Đường dẫn `scratchpad/…` nhắc trong bài là thư mục tạm của phiên, không còn tồn tại. Số liệu chính thức: `samples/manifest.yaml`.

# Đánh giá danh sách IFC của BIMData (IFC_FILES.md) cho kiểm thử và cho các phương pháp suy IfcSpace / IfcRelSpaceBoundary

- **Câu hỏi nghiên cứu**: Các model trong danh sách IFC_FILES.md của BIMData (40 model, khoảng 100 file) có dùng được để (a) kiểm thử thuật toán (debug, đo độ chính xác so với ground truth, đo hiệu năng) và (b) thử các phương pháp đang nghiên cứu (graph/topology kiểu IFC2SB, dựng B-rep 3D, voxel hoá, lát cắt mặt bằng theo tầng rồi polygonize) không?
- **Kết luận ngắn**:
  - BIMData chỉ là **danh mục**. Repo không có file IFC và không có LICENSE. Mọi URL gốc (tib.eu/DURAARK, portal.nibs.org, dropbox.com, bimcollab.com, openifcmodel.cs.auckland.ac.nz, cgcad.thss.tsinghua.edu.cn) đều **bị chặn hoặc không phân giải được** từ container. Chưa tải được file nào từ URL gốc.
  - Tìm theo tên/dung lượng trên các repo GitHub công khai thì có **bản sao** của 9 file. Đã tải và đo 7 file mới. Hai phát hiện lớn: **HiTOS** (`HITOS_070308.ifc`, 64 MB, 7 tầng, 243 IfcSpace, **8 969 IfcRelSpaceBoundary "Second Level"** có hình học) và **Schependomlaan** (49 MB, 100 IfcSpace, **1 675 RSB "2ndLevel"**). Đây là hai file có **ground truth RSB 2nd level lớn nhất** dự án có trong tay, ngoài `rwth-digitalhub-with-sb`.
  - Không có model nào là sân vận động hay arena. HiTOS (trường cao đẳng, 7 tầng) và Medical Clinic là loại "large_public/school" gần nhất.
- **Độ tin cậy**: trung bình. Số đo là số thật (inspect_ifc.py, ifcopenshell 0.9.0.post1, 2026-11-10). Việc bản sao GitHub có trùng file BIMData liệt kê hay không chỉ suy theo tên và dung lượng; trừ LTU A-House redesign (181,31 MB, khớp 181,3) và Schependomlaan (49,29 MB, khớp 49,3), còn lại là **suy luận**. Giấy phép gốc của hầu hết file **chưa xác minh**.

## Chi tiết

### 1. Cách làm
1. Clone `bimdata/BIMData-Research-and-Development` (depth 1) và đọc `pages/IFC_FILES.md`. Repo chỉ có `README.md`, `assets/` (ảnh chụp màn hình) và `pages/`. **Không có file LICENSE, không có file IFC.**
2. Thử từng host gốc bằng `curl -sS` (timeout 25 s). Kết quả:

| Host | Kết quả từ container (2026-11-10) | Model liên quan |
|---|---|---|
| `tib.eu` (DURAARK) | `CONNECT tunnel failed, response 403` (proxy chặn). Theo re3data, DURAARK offline từ 13.02.2020 (đã ghi ở TASK-001) | Phần lớn các model (NBU_*, SGD_*, LTU, NVW, FOJAB, Autodesk_*, KIT_*, NBS_Lakeside…) |
| `portal.nibs.org` | `CONNECT tunnel failed, response 403` | MedicalClinic_* |
| `www.dropbox.com` | `CONNECT tunnel failed, response 403` | Holter_Tower_10 |
| `www.bimcollab.com` | `CONNECT tunnel failed, response 403` | BIMCollab_* |
| `openifcmodel.cs.auckland.ac.nz` | HTTP: `Could not resolve host`; HTTPS: không phản hồi trong 25 s | Trapelo, Hospital, OTC, Ettenheim, Staal_Saxion, Dubal_Herrera, Svaleveien8, HospitalGarage, FZK_Haus |
| `cgcad.thss.tsinghua.edu.cn` | `Could not resolve host` | IfcCompressor_M1 |
| `duraark.eu`, `www.markusplassen.no` | `Could not resolve host` | (trang nguồn) |
| `github.com/openBIMstandards/DataSetSchependomlaan` | proxy trả "GitHub access to this repository is not enabled for this session" | Schependomlaan (repo đã chuyển sang buildingsmart-community) |

   Không tìm cách lách và không xin mở mạng.
3. Tìm bản sao: clone kiểu blobless (`--filter=blob:none --no-checkout`) năm repo công khai đã dùng ở TASK-001, rồi so tên và dung lượng (`git ls-tree -r -l`). Năm repo: `ThatOpen/engine_web-ifc`@28a6527, `ara3d/IFC-toolkit`@9ad378a, `opensourceBIM/TestFiles`@2fdf948, `buildingsmart-community/Community-Sample-Test-Files`@31eb1dd (LFS pointer cho oid sha256), `IfcOpenShell/files`.
4. Tải bản sao qua `raw.githubusercontent.com` vào `scratchpad/bimdata/dl/`, tính sha256 để so với manifest, rồi đo bằng `python3 samples/inspect_ifc.py --isolate`. Chạy thêm một script truy vấn phụ (`scratchpad/bimdata/scripts/q.py`) để xem tên tầng/phòng, kiểu biểu diễn của IfcSpace, và phân bố RSB theo phần tử, Physical/Virtual, Internal/External.

### 2. Bảng toàn bộ file trong IFC_FILES.md
Schema mặc định là IFC2X3 theo ghi chú của BIMData ("If not specified, the files are in the IFC2X3 schema"), trừ khi tên file ghi IFC4. Dung lượng là số BIMData ghi (MB). "Bị chặn" nghĩa là URL gốc không tải được (xem bảng host). Cột "Bản sao / trùng" chỉ ghi khi đã kiểm thật.

| # | Model (loại công trình, suy từ tên/nguồn) | File | MB | Host URL gốc | Trạng thái | Bản sao / trùng |
|---|---|---|---|---|---|---|
| 1 | Medical Clinic (phòng khám, NIBS) | MedicalClinic_Combined.ifc | 112.6 | portal.nibs.org | Bị chặn | — |
| 2 | | MedicalClinic_ARC.ifc | 15.5 | portal.nibs.org | Bị chặn | Có thể cùng dự án với `clinic-architectural` (13,0 MB); dung lượng khác, chưa xác minh |
| 3 | | MedicalClinic_ELE.ifc | 41.1 | portal.nibs.org | Bị chặn | — |
| 4 | | MedicalClinic_MECH.ifc | 56.8 | portal.nibs.org | Bị chặn | — |
| 5 | | NBU_MedicalClinic_ARC.ifc | 18.1 | tib.eu | Bị chặn | — |
| 6 | | NBU_MedicalClinic_MEP.ifc | 207.3 | tib.eu | Bị chặn | — |
| 7 | | NBU_MedicalClinic_HVAC.ifc | 27.4 | tib.eu | Bị chặn | Gần `Clinic_HVAC.ifc` (26,91 MB, buildingsmart-community); chưa xác minh trùng |
| 8 | | NBU_MedicalClinic_ELE.ifc | 12.0 | tib.eu | Bị chặn | — |
| 9 | | NBU_MedicalClinic_STR.ifc | 19.4 | tib.eu | Bị chặn | Gần `Clinic_Structural.ifc` (19,06 MB); chưa xác minh |
| 10 | LTU A-House (nhà ở/công trình đại học Luleå, suy luận) | LTU_AHouse_ARC.ifc | 94.2 | tib.eu | Bị chặn | — |
| 11 | | LTU_AHouse_SAN.ifc | 27.0 | tib.eu | Bị chặn | — |
| 12 | | LTU_AHouse_Redesign.ifc | 181.3 | tib.eu | Bị chặn | **Bản sao** `ThatOpen/.../LTU_A-House_redesign.ifczip` → giải nén ra 181,31 MB, khớp. **Đã đo** |
| 13 | | LTU_AHouse_HEAT.ifc | 34.2 | tib.eu | Bị chặn | — |
| 14 | | LTU_AHouse_COOL.ifc | 32.3 | tib.eu | Bị chặn | — |
| 15 | | LTU_AHouse_VOID.ifc | 25.3 | tib.eu | Bị chặn | — |
| 16 | | LTU_AHouse_AIR.ifc | 25.4 | tib.eu | Bị chặn | — |
| 17 | | LTU_AHouse_DUCT.ifc | 8.4 | tib.eu | Bị chặn | — |
| 18 | | LTU_AHouse_STR.ifc | 32.4 | tib.eu | Bị chặn | — |
| 19 | | LTU_AHouse_PLB.ifc | 73.0 | tib.eu | Bị chặn | — |
| 20 | NVW DCR LOD300 (chưa rõ loại) | NVW_DCR_LOD300_ARC.ifc | 288.1 | tib.eu | Bị chặn | — |
| 21 | | NVW_DCR_LOD300_STR.ifc | 11.1 | tib.eu | Bị chặn | — |
| 22 | | NVW_DCR_LOD300_HVAC.ifc | 24.1 | tib.eu | Bị chặn | — |
| 23 | SGD BODO (Statsbygg Bodø, suy luận: công trình công) | SGD_BODO_ARC.ifc | 64.1 | tib.eu | Bị chặn | — |
| 24 | | SGD_BODO_PLB.ifc | 72.8 | tib.eu | Bị chặn | — |
| 25 | | SGD_BODO_VENT.ifc | 47.2 | tib.eu | Bị chặn | — |
| 26 | Holter Tower (tháp) | Holter_Tower_10.ifc | 177.5 | dropbox.com | Bị chặn | **trùng `holter-tower`** (ara3d/ThatOpen ifczip 30 805 675 B, cùng tên `20181220Holter_Tower_10`) |
| 27 | FOJAB Landsarkivet (lưu trữ quốc gia, công trình công) | FOJAB_Landsarkivet.ifc | 177.5 | tib.eu | Bị chặn | — |
| 28 | BIMCollab (văn phòng mẫu) | BIMCollab_ARC.ifc | 26.0 | bimcollab.com | Bị chặn | — |
| 29 | | BIMCollab_STR.ifc | 0.6 | bimcollab.com | Bị chặn | — |
| 30 | | BIMCollab_MEP.ifc | 45.0 | bimcollab.com | Bị chặn | — |
| 31 | | BIMCollab_Elevatorshaft.ifc | 1.4 | bimcollab.com | Bị chặn | — |
| 32 | | BIMCollab_HollowCoreSlabs.ifc | 14.7 | bimcollab.com | Bị chặn | — |
| 33 | | BIMCollab_LimestoneWalls.ifc | 0.2 | bimcollab.com | Bị chặn | — |
| 34 | | BIMCollab_Structural Steel.ifc | 0.3 | bimcollab.com | Bị chặn | — |
| 35 | | BIMCollab_VENT.ifc | 32.8 | bimcollab.com | Bị chặn | — |
| 36 | | BIMCollab_HEAT_PLB.ifc | 54.6 | bimcollab.com | Bị chặn | — |
| 37 | Autodesk 210 King (văn phòng cao tầng Toronto, suy luận) | Autodesk_210King.ifc | 155.1 | tib.eu | Bị chặn | — |
| 38 | Trapelo (văn phòng, Autodesk sample) | Trapelo_IFC2X3_ARC.ifc | 27.2 | openifcmodel (Details/302) | Bị chặn | — |
| 39 | | Trapelo_IFC2X3_MEP.ifc | 65.3 | openifcmodel | Bị chặn | — |
| 40 | | Trapelo_IFC2X3_STR.ifc | 3.6 | openifcmodel | Bị chặn | — |
| 41 | | Trapelo_IFC4_ARC.ifc (IFC4) | 22.4 | openifcmodel (Details/303) | Bị chặn | — |
| 42 | | Trapelo_IFC4_MEP.ifc (IFC4) | 67.8 | openifcmodel | Bị chặn | — |
| 43 | | Trapelo_IFC4_STR.ifc (IFC4) | 3.5 | openifcmodel | Bị chặn | — |
| 44 | SGD Duplex (nhà ở) | SGD_Duplex_PLB.ifc | 92.8 | tib.eu | Bị chặn | — |
| 45 | | SGD_Duplex_VENT.ifc | 3.3 | tib.eu | Bị chặn | — |
| 46 | NBU Office Building (văn phòng; BIMData trỏ nhầm link sang zip MedicalClinic) | NBU_OfficeBuilding_ARC.ifc | 4.1 | tib.eu | Bị chặn | Có thể là `office-a` (4,10 MB, NIBS); suy luận, chưa xác minh |
| 47 | | NBU_OfficeBuilding_HVAC.ifc | 65.8 | tib.eu | Bị chặn | — |
| 48 | | NBU_OfficeBuilding_ELE.ifc | 6.5 | tib.eu | Bị chặn | — |
| 49 | | NBU_OfficeBuilding_STR.ifc | 11.1 | tib.eu | Bị chặn | — |
| 50 | SGD HiTOS (Høgskolen i Tromsø, trường học, suy luận theo tên) | SGD_HiTOS_ARC.ifc | 52.9 | tib.eu | Bị chặn | **Bản khác** cùng dự án: `opensourceBIM/TestFiles/TestData/data/HITOS_070308.ifc` (64,10 MB). **Đã đo** |
| 51 | | SGD_HiTOS_ELE.ifc | 7.5 | tib.eu | Bị chặn | — |
| 52 | | SGD_HiTOS_HVAC.ifc | 18.5 | tib.eu | Bị chặn | — |
| 53 | Hospital (West Riverside Hospital, bệnh viện; theo TASK-001) | Hospital_IFC2X3_ELE.ifc | 4.7 | openifcmodel (Details/305) | Bị chặn | — |
| 54 | | Hospital_IFC2X3_FIRE.ifc | 0.9 | openifcmodel | Bị chặn | — |
| 55 | | Hospital_IFC2X3_PLB.ifc | 25.0 | openifcmodel | Bị chặn | — |
| 56 | | Hospital_IFC2X3_SPR.ifc | 35.7 | openifcmodel | Bị chặn | — |
| 57 | | Hospital_IFC2X3_STR.ifc | 6.4 | openifcmodel | Bị chặn | — |
| 58–62 | | Hospital_IFC4_{ELE,FIRE,PLB,SPR,STR}.ifc (IFC4) | 4.4 / 0.9 / 23.8 / 34.0 / 6.5 | openifcmodel (Details/308) | Bị chặn | — (lưu ý: danh sách **không có file ARC** của Hospital) |
| 63 | OTC Conference Center (hội trường) | OTC_ConfCenter_IFC4.ifc (IFC4) | 71.7 | openifcmodel | Bị chặn | Đã có trong manifest dạng `manual: true` (`otc-conference-center`) |
| 64 | | OTC_ConfCenter_IFC2X3.ifc | 70.3 | openifcmodel | Bị chặn | như trên |
| 65 | NVW DCR LOD200 | NVW_DCR_LOD200_ARC.ifc | 25.3 | tib.eu | Bị chặn | — |
| 66 | | NVW_DCR_LOD200_STR.ifc | 9.4 | tib.eu | Bị chặn | — |
| 67 | | NVW_DCR_LOD200_HVAC.ifc | 33.2 | tib.eu | Bị chặn | — |
| 68 | IfcCompressor M1 (Tsinghua) | IfcCompressor_M1.ifc | 58.5 | cgcad.thss.tsinghua.edu.cn | Bị chặn | — |
| 69 | SGD BARD | SGD_BARD_ARC.ifc | 11.5 | tib.eu | Bị chặn | — |
| 70 | | SGD_BARD_Merged.ifc | 43.8 | tib.eu | Bị chặn | — |
| 71 | NBU Duplex (nhà ở) | NBU_Duplex_ARC.ifc | 2.4 | tib.eu | Bị chặn | Có thể là `duplex-a` (2,38 MB); bản `duplex.ifc` của ThatOpen có sha256 trùng `duplex-a` → **trùng duplex-a** (suy luận về tên NBU) |
| 72 | | NBU_Duplex_MEP.ifc | 32.1 | tib.eu | Bị chặn | — |
| 73 | | NBU_Duplex_HVAC.ifc | 18.2 | tib.eu | Bị chặn | — |
| 74 | | NBU_Duplex_MEP1.ifc | 1.6 | tib.eu | Bị chặn | — |
| 75 | Schependomlaan (10 căn hộ, Nijmegen) | Schependomlaan.ifc | 49.3 | tib.eu (BIMData trỏ nhầm zip KIT_Institute) | Bị chặn | **Bản sao** ThatOpen `schependomlaan.ifc` 49 286 967 B, sha256 trùng oid LFS của `buildingsmart-community/.../Design model IFC/IFC Schependomlaan.ifc`. **Đã đo** |
| 76 | NBS Lakeside (chưa rõ loại) | NBS_LakesideAC01.ifc | 42.3 | tib.eu | Bị chặn | — |
| 77 | Autodesk Advanced (rac_advanced_sample, văn phòng) | Autodesk_Advanced.ifc | 38.1 | tib.eu | Bị chặn | **Bản khác** (suy luận): ThatOpen/ara3d `advanced_model.ifc` 35,31 MB, xuất từ Revit 2021. **Đã đo** |
| 78 | SGD Munkerud (Statsbygg) | SGD_Munkerud_ARC.ifc | 3.9 | tib.eu | Bị chặn | — |
| 79 | | SGD_Munkerud_ELE.ifc | 14.9 | tib.eu | Bị chặn | — |
| 80 | | SGD_Munkerud_SAN.ifc | 10.6 | tib.eu | Bị chặn | — |
| 81 | | SGD_Munkerud_VENT.ifc | 5.4 | tib.eu | Bị chặn | — |
| 82 | Ettenheim (mô hình GIS thị trấn, KIT) | Ettenheim.ifc (bản `_optimized`) | 31.1 | openifcmodel | Bị chặn | **Bản khác**: `opensourceBIM/.../Ettenheim-GIS-05-11-2006.ifc` 31,07 MB, schema **IFC2X_FINAL**; ifcopenshell 0.9 **không mở được** (G1 trượt) |
| 83 | Staal Saxion (kết cấu thép) | Staal_Saxion_STR.ifc | 25.3 | openifcmodel | Bị chặn | — |
| 84 | Dubal Herrera (chưa rõ) | Dubal_Herrera_limpio.ifc | 24.4 | openifcmodel | Bị chặn | — |
| 85 | SGD Blueberry | SGD_Blueberry_ARC.ifc | 8.0 | tib.eu | Bị chặn | — |
| 86 | | SGD_Blueberry_HVAC.ifc | 10.7 | tib.eu | Bị chặn | — |
| 87 | Plan3D Haus30 (nhà ở) | Plan3D_Haus30.ifc | 20.2 | tib.eu (BIMData trỏ zip KIT_Smiley-West) | Bị chặn | — |
| 88 | Svaleveien 8 Hus A (nhà ở Na Uy) | Svaleveien8_HusA06.ifc | 12.1 | openifcmodel | Bị chặn | — |
| 89 | FZK Haus (Nemetschek) | FZK_HausNem.ifc | 10.4 | (BIMData để link trống) | Không có URL | Bản Allplan khác cùng họ (`Allplan-Smiley-West.ifc`) là IFC2X_FINAL, không mở được; FZK_HausNem không thấy bản sao |
| 90 | FZK Haus (EliteCAD) | FZK_HausEliteCAD.ifc | 7.4 | (link trống) | Không có URL | — |
| 91 | Autodesk Basic (rac_basic_sample) | Autodesk_Basic.ifc | 5.4 | tib.eu | Bị chặn | **Bản khác**: `opensourceBIM/.../ifc4rac_basic_sample_project.ifc` (IFC4, 25,40 MB). **Đã đo** |
| 92 | Hospital Garage (bãi đỗ xe bệnh viện) | HospitalGarage_IFC4.ifc (IFC4) | 6.5 | openifcmodel | Bị chặn | — |
| 93 | | HospitalGarage_IFC2X3.ifc | 6.4 | openifcmodel | Bị chặn | — |
| 94 | FZK Haus (AC11) | FZK_Haus.ifc (`231110AC11-FZK-Haus-IFC.ifc`) | 4.1 | openifcmodel | Bị chặn | **trùng `ac11-fzk-haus`** (tên gốc 231110AC11-FZK-Haus-IFC, 4,1 MB) |
| 95 | KIT Smiley West | KIT_SmileyWest.ifc | 3.4 | tib.eu | Bị chặn | Cùng dự án với `kit-smiley-west` (AC20, 6,11 MB); khác bản |
| 96 | KIT Institute | KIT_Institute.ifc | 2.8 | tib.eu | Bị chặn | Có thể là `AC11-Institute-Var-2-IFC.ifc` (2,84 MB, opensourceBIM) — cùng dự án với `ac20-institute-var-2`; chưa xác minh |
| 97 | NVW DCR LOD100 | NVW_DCR_LOD100_ARC.ifc | 0.2 | tib.eu | Bị chặn | — |

BIMData ghi "100 IFC files (3.7 GB)", nhưng bảng của họ chỉ liệt kê 97 tên file. Ba file còn lại không có trong bảng (chưa xác minh).

### 3. Bảng file đã đo (inspect_ifc.py --isolate, 2026-11-10)
Điểm `score_auto` chưa cộng `legal` và `building_type`. Thời gian và RAM đo trên container hiện tại.

| File (bản sao) | Schema | MB | open_s | peak RSS MB | Tầng | n_products | Storey | IfcSpace (có rep / dưới storey) | RSB (label) | RSB có hình học / Virtual / External / có Corresponding | geom_ok elem | geom_ok space | Tier | score_auto |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HITOS_070308.ifc | IFC2X3 | 64.10 | 2.60 | 541.9 | 7 | 12 148 | 7 | 243 (243/243) | 8 969 (`Second Level`) | 8 969 / 1 401 / 5 306 / 0 | 1.00 | 1.00 | L | 72 |
| schependomlaan.ifc | IFC2X3 | 49.29 | 1.29 | 410.8 | 6 | 3 822 | 6 | 100 (100/100) | 1 675 (`2ndLevel`, Description `2a`) | 1 675 / 667 / 1 459 / 0 | 1.00 | **0.06** | L | 72 |
| ifc4rac_basic_sample_project.ifc | IFC4 | 25.40 | 1.06 | 262.8 | 6 | 524 | 6 | 14 (14/14) | 0 | — | 1.00 | 1.00 | L | 60 |
| LTU_A-House_redesign.ifc | IFC2X3 | 181.31 | 6.07 | 1 441.3 | 5 | 9 730 | 5 | 0 | 0 | — | 1.00 | — | L | 35 |
| advanced_model.ifc | IFC2X3 | 35.31 | 1.13 | 326.3 | 4 | 14 369 | 4 | 0 | 0 | — | 1.00 | — | L | 32 |
| Ettenheim-GIS-05-11-2006.ifc | IFC2X_FINAL | 31.07 | — | — | — | — | — | — | — | — | — | — | — | lỗi `SchemaError: Unsupported schema: IFC2X_FINAL` |
| Allplan-Smiley-West.ifc | IFC2X_FINAL | 4.08 | — | — | — | — | — | — | — | — | — | — | — | lỗi như trên |

Thêm hai file tải về chỉ để so sha256: `dental_clinic.ifc` (ThatOpen) có sha256 `2ac970ce…7880`, **trùng `clinic-architectural`**; `duplex.ifc` (ThatOpen) có sha256 `b347a2c8…06ed`, **trùng `duplex-a`**.

Truy vấn bổ sung (script q.py):
- **HiTOS**: tầng `fundamentetasje, kjeller, u.etg, 1.etg, 2.etg, 3.etg, takplan` (cao độ 17 300 → 40 300 mm, mỗi tầng 4 m, trừ tầng đầu 3 m). Phòng có số và tên Na Uy (`80.001 El`, `80.003 Sluse`…). 243/243 IfcSpace là `Body/IfcExtrudedAreaSolid`. RSB: PHYSICAL 7 568, VIRTUAL 1 401; INTERNAL 3 663, EXTERNAL 5 306. Phần tử liên quan: IfcColumn 2 588, IfcWallStandardCase 2 580, IfcSlab 1 677, None 1 211, IfcDoor 379, IfcWindow 259, IfcVirtualElement 190, IfcOpeningElement 81. Hình học 100 % là `IfcConnectionSurfaceGeometry/IfcCurveBoundedPlane`. Tường (300 mẫu đầu): 280 `IfcExtrudedAreaSolid`, 23 `IfcFacetedBrep`, 17 `IfcBooleanClippingResult`. Header: "IFC Engine Kernal version 1.10 beta", FILE_NAME 'IFC Engine DLL test' (2006-03-31), Project/Building tên mặc định. Phần mềm tác giả chưa xác minh.
- **Schependomlaan**: ArchiCAD 18 NED (header). Tầng `-1 fundering … 04 dak` (cách 3 m). Trong 100 IfcSpace, 94 chỉ có `FootPrint/IfcGeometricCurveSet` + `Box/IfcBoundingBox`, chỉ 6 có `Body/IfcExtrudedAreaSolid`. Vì vậy `geom_ok_ratio_spaces` = 0,06: ifcopenshell không tạo được solid khi không có Body, file không hỏng. Tường: 100 % `IfcFacetedBrep` (400/400 item mẫu). RSB: Name `2ndLevel`, Description `2a` (khớp ký hiệu 2a của CV2.0 SB, *chưa xác minh với tài liệu buildingSMART*). PHYSICAL 1 008, VIRTUAL 667; INTERNAL 216, EXTERNAL 1 459. Phần tử: None 639, IfcSlab 535, IfcWall 160, IfcWallStandardCase 143, IfcCovering 84, IfcDoor 73…
- **Lưu ý chung**: trong cả hai file, `n_rsb_with_corresponding` = 0. Trong IFC2X3, `CorrespondingBoundary` không có trong schema (theo `dataset-quality-criteria.md`), nên cặp boundary phải tự ghép theo hình học.

### 4. Đánh giá theo mục đích và phương pháp

| File | Ground truth (level) | Cỡ | Loại công trình | Giấy phép | (a) Kiểm thử | (b) Phương pháp hợp | Lý do |
|---|---|---|---|---|---|---|---|
| **HiTOS (HITOS_070308)** | IfcSpace 243 (extrusion, đều thuộc storey) + **RSB 2nd level 8 969** có hình học, có Virtual | L | Trường cao đẳng (school/large_public, suy luận theo tên dự án HiTOS) | **Chưa xác minh**: repo opensourceBIM/TestFiles ghi GPL-3.0 (`TestData/license.txt`, "Copyright (C) 2009-2017 BIMserver.org"), gốc Statsbygg | **Rất hợp**: đo độ đúng boundary ở quy mô L, đo hiệu năng (12 k product, 541 MB RAM) | **Tất cả**. Lát cắt + polygonize: so IoU footprint từng tầng (7 tầng, phòng là extrusion nên mặt cắt chính là profile). Graph/IFC2SB: tường phần lớn là extrusion sạch, có B-rep/boolean xen kẽ, có ground truth RSB để so cặp mặt. Voxel: dùng làm baseline ở quy mô L. B-rep 3D: có thể so thể tích với IfcSpace | Là file có RSB 2nd level lớn nhất tìm được. Có cột (2 588 RSB gắn IfcColumn) giúp test boundary quanh cột |
| **Schependomlaan** | IfcSpace 100 (94 chỉ FootPrint 2D) + **RSB 2ndLevel/2a 1 675** | L | Chung cư 10 căn (residential) | **Hạn chế**: "permission to use the data for scientific and academic purposes" (TASK-001, README repo community). Không tái phân phối | Hợp cho đo boundary, nhưng chỉ dùng nội bộ/học thuật | **Lát cắt + polygonize**: FootPrint 2D của IfcSpace chính là ground truth 2D, so IoU trực tiếp. **Graph/IFC2SB, B-rep**: tường 100 % `IfcFacetedBrep`, đúng loại đầu vào cho General Fuse. Test độ bền: IfcSpace thiếu Body nên reader phải dùng FootPrint + chiều cao tầng | Bổ sung dạng hình học (B-rep thay vì extrusion) mà HiTOS không có |
| ifc4rac_basic_sample_project | IfcSpace 14 (có rep), không RSB | L (theo dung lượng; thực chất nhỏ về số phòng) | Nhà ở mẫu Revit (suy luận) | Chưa xác minh (GPL repo opensourceBIM; gốc Autodesk sample) | Test IFC4 cỡ trung với mái (2 IfcRoof), curtain wall, cầu thang | Lát cắt + polygonize (6 tầng); voxel/B-rep cho mái dốc (suy luận: mái Revit mẫu là mái dốc, chưa xem bằng viewer) | IFC4 có IfcSpace thật, ít file IFC4 như vậy trong manifest |
| LTU_A-House_redesign | Không IfcSpace, không RSB | L (181 MB, 1,44 GB RAM) | Chưa rõ (suy luận: công trình của LTU) | Chưa xác minh (ThatOpen MPL-2.0 cho mã, file gốc DURAARK) | Hiệu năng/stress: 2 623 tường, 976 cửa sổ, 2 785 opening | Test suy luận IfcSpace không có ground truth (graph/voxel), đo thời gian/RAM | Không đo được độ đúng |
| advanced_model (Revit 2021) | Không IfcSpace, không RSB | L | Văn phòng mẫu Revit (suy luận) | Chưa xác minh | Stress cột (135) + curtain wall (33), 0 IfcWindow | Graph/IFC2SB và voxel để suy luận phòng; không có ground truth | Có thể dùng làm test "suy IfcSpace từ đầu" |
| Ettenheim, Allplan-Smiley-West | — | — | GIS thị trấn / nhà ở | — | Chỉ để test reader từ chối IFC2X_FINAL một cách sạch sẽ | — | ifcopenshell 0.9 không hỗ trợ schema |
| Các file bị chặn có tiềm năng (chưa kiểm) | | | | | | | |
| OTC Conference Center (IFC4 & 2X3) | chưa xác minh | L | Hội trường (large_public) | chưa xác minh (re3data ghi Open IFC Repo CC BY 3.0) | Ưu tiên tải tay | chưa xác minh | Loại công trình gần sân vận động nhất trong danh sách |
| Hospital IFC2X3/IFC4 | chưa xác minh; **danh sách chỉ có MEP/STR/FIRE/SPR, không có ARC** | M | Bệnh viện | chưa xác minh | Hạn chế: không có kiến trúc thì khó có IfcSpace (suy luận) | MEP là "nhiễu" khi test lọc phần tử bao | — |
| MedicalClinic_Combined, NBU_MedicalClinic_* | chưa xác minh | L | Phòng khám | NIBS, chưa xác minh | Test mô hình liên ngành gộp (ARC+MEP) | Test lọc phần tử bao | Đã có `clinic-architectural` cùng dự án |
| FOJAB Landsarkivet, Autodesk 210 King, SGD BODO, NVW DCR LOD300 ARC (288 MB) | chưa xác minh | L | Công trình công / văn phòng cao tầng | chưa xác minh | Hiệu năng L | chưa xác minh | DURAARK đã offline, chỉ còn cách tìm bản sao khác |

### 5. Đề xuất thêm vào manifest
Tất cả để ở `samples/large/` hoặc `samples/corpus_real/` (**không commit**) vì giấy phép chưa rõ hoặc hạn chế. Nhóm `legal` và `building_type` do claude-01 chốt.

| id gợi ý | URL (pin commit) | sha256 | Giấy phép (nguyên văn/hiện trạng) | Tầng | Lý do |
|---|---|---|---|---|---|
| `hitos` | https://raw.githubusercontent.com/opensourceBIM/TestFiles/2fdf94854a7fba814a17604ed65f543f125cd265/TestData/data/HITOS_070308.ifc | fe339277c7390b4a99d327846e34239e4d853371fac6951e46503ba8faaa2dcf | chưa xác minh — `TestData/license.txt` của repo: "Copyright (C) 2009-2017 BIMserver.org … GNU General Public License … version 3"; gốc HiTOS/Statsbygg, giấy phép gốc chưa xác minh → `license_class: unknown` | L | **Ưu tiên 1**: 243 IfcSpace + 8 969 RSB 2nd level có hình học, 7 tầng, trường học. Ground truth chính cho đo boundary ở quy mô L |
| `schependomlaan` | https://raw.githubusercontent.com/ThatOpen/engine_web-ifc/28a65274189ef6df13832813472612ca068b7911/tests/ifcfiles/public/schependomlaan.ifc (hoặc LFS của buildingsmart-community@31eb1dd, cùng sha256) | 2c3565ca1904f2aa61adab92024cf3755b2c5b21a498144d3094d7cb58cebec7 | Hạn chế: "permission to use the data for scientific and academic purposes" (README repo community, đã trích ở TASK-001) → `use_only` | L | **Ưu tiên 2**: 1 675 RSB 2ndLevel/2a, 100 IfcSpace FootPrint 2D (ground truth cho polygonize), tường B-rep (đầu vào cho IFC2SB). Trước đây bị loại vì giấy phép; đề xuất đưa lại dạng `corpus_real` chỉ dùng nội bộ để đánh giá |
| `rac-basic-ifc4` | https://raw.githubusercontent.com/opensourceBIM/TestFiles/2fdf94854a7fba814a17604ed65f543f125cd265/TestData/data/ifc4rac_basic_sample_project.ifc | 1421b55315b99044b639db2704dc086aeb42a37d6032bbc2aecdc8649f7c05f2 | chưa xác minh (GPL-3.0 của repo; gốc Autodesk sample) | L (25 MB) / thực tế 14 phòng | IFC4 có IfcSpace + mái + curtain wall, 6 tầng; bổ sung IFC4 cỡ trung |
| `ltu-ahouse-redesign` (tuỳ chọn) | https://raw.githubusercontent.com/ThatOpen/engine_web-ifc/28a65274189ef6df13832813472612ca068b7911/tests/ifcfiles/public/LTU_A-House_redesign.ifczip | zip: daab20e085f494a01c9faf04b8c0475e9f7b01d73a9b3b7c9e4a50199a3b8a33 | chưa xác minh (gốc DURAARK) | L (181 MB, RAM 1,44 GB) | Stress/hiệu năng không có ground truth |
| `revit-advanced-2021` (tuỳ chọn) | https://raw.githubusercontent.com/ThatOpen/engine_web-ifc/28a65274189ef6df13832813472612ca068b7911/tests/ifcfiles/public/advanced_model.ifc | 3c822eed72ab588697f3f4d4c2b074d1bb888802f877218c769845180f2b7ad2 | chưa xác minh | L | Test suy IfcSpace từ đầu (0 phòng), nhiều cột/curtain wall |

Không đề xuất: Ettenheim/Allplan (IFC2X_FINAL, trượt G1), `dental_clinic`/`duplex` (trùng `clinic-architectural`/`duplex-a`), Holter Tower và FZK_Haus AC11 (đã có).

## Liên quan đến pipeline IFC → Space Boundaries
- Reader IFC2X3 cần nhận cả hai quy ước nhãn level: `Name='Second Level'` (HiTOS) và `Name='2ndLevel'`, `Description='2a'` (Schependomlaan). `inspect_ifc.py` đã đếm đúng cả hai (`n_rsb_name_2ndlevel`).
- IFC2X3 không có `CorrespondingBoundary`, nên metric "cặp boundary" phải ghép theo hình học (mặt song song, khoảng cách ≈ bề dày phần tử). Cần ghi rõ điều này trong spec đánh giá (suy luận).
- IfcSpace chỉ có FootPrint (Schependomlaan): nhánh lát cắt + polygonize so được trực tiếp. Nhánh B-rep/voxel cần dựng solid bằng FootPrint × chiều cao tầng.
- HiTOS có 1 211 RSB không có `RelatedBuildingElement` và 190 RSB gắn `IfcVirtualElement`. Metric phải tách boundary vật lý và ảo.

## Nguồn
- [BIMData R&D — IFC_FILES.md](https://github.com/bimdata/BIMData-Research-and-Development/blob/master/pages/IFC_FILES.md) — truy cập 2026-11-10 (clone depth 1)
- [ThatOpen/engine_web-ifc @28a6527 — tests/ifcfiles/public](https://github.com/ThatOpen/engine_web-ifc/tree/28a65274189ef6df13832813472612ca068b7911/tests/ifcfiles/public) — LICENSE.md: Mozilla Public License 2.0 (cho repo) — truy cập 2026-11-10
- [opensourceBIM/TestFiles @2fdf948 — TestData/data](https://github.com/opensourceBIM/TestFiles/tree/2fdf94854a7fba814a17604ed65f543f125cd265/TestData/data) và `TestData/license.txt` (GPL-3.0, "Copyright (C) 2009-2017 BIMserver.org") — truy cập 2026-11-10
- [buildingsmart-community/Community-Sample-Test-Files @31eb1dd](https://github.com/buildingsmart-community/Community-Sample-Test-Files/tree/31eb1dd0a0406fb9ebf0ebd823b48e1ec95afc08) — LFS pointer (oid sha256) của Schependomlaan, Clinic_* — truy cập 2026-11-10
- [ara3d/IFC-toolkit @9ad378a — test-files](https://github.com/ara3d/IFC-toolkit/tree/9ad378ae8db3203dbedfc6ffc7fb56ded56590ea/test-files) — truy cập 2026-11-10
- IfcOpenShell 0.9.0.post1 (https://pypi.org/project/ifcopenshell/) — dùng để đo, không hỗ trợ IFC2X_FINAL — truy cập 2026-11-10
- Host bị chặn/không phân giải (2026-11-10): tib.eu, portal.nibs.org, www.dropbox.com, www.bimcollab.com (CONNECT 403); openifcmodel.cs.auckland.ac.nz, cgcad.thss.tsinghua.edu.cn, duraark.eu, www.markusplassen.no (không phân giải / không phản hồi)

## Câu hỏi còn mở
- Giấy phép gốc của HiTOS (Statsbygg) chưa xác minh. Cần tìm trang chính thức của Statsbygg hoặc buildingSMART Norway.
- Phần mềm nào tạo HiTOS_070308, và RSB do phần mềm tự sinh hay do công cụ hậu xử lý (header là "IFC Engine DLL test")? Câu trả lời ảnh hưởng đến độ tin cậy của ground truth. Chưa xác minh.
- Nên kiểm tra chất lượng RSB của HiTOS/Schependomlaan trước khi dùng làm ground truth: tổng diện tích boundary so với diện tích bao của phòng, độ khép kín. Đây là việc của task validation sau.
- OTC Conference Center, Hospital, Trapelo, FOJAB, 210 King vẫn cần người dùng tải tay hoặc tìm bản sao khác.
- 1 401 RSB VIRTUAL của HiTOS (190 gắn `IfcVirtualElement`, phần còn lại không gắn phần tử) có thật sự tương ứng với ranh giới giữa các phòng thông nhau không? Cần mở bằng viewer để xác minh.

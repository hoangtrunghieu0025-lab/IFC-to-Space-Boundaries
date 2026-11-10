> **Báo cáo thô** của subagent hỗ trợ claude-01 (TASK-001), ngày 2026-11-10, chép nguyên văn từ scratchpad để lưu vết. Đường dẫn `/tmp/…/scratchpad/…` và `dl/`, `dl2/`, `scripts/` nhắc trong báo cáo là thư mục tạm của phiên, **không còn tồn tại**. Bản tổng hợp đã kiểm lại: `../dataset-survey.md`, `../dataset-search-log.md`.

# Khảo sát file IFC công trình LỚN / PHỨC HỢP / ĐÔNG NGƯỜI (hỗ trợ TASK-001)

- Người thực hiện: subagent hỗ trợ claude-01
- Ngày truy cập mọi nguồn: **2026-11-10**
- Môi trường: container 16 GB RAM, Python 3 + IfcOpenShell 0.9.0.post1. Không có `/usr/bin/time`, nên số đo lấy bằng `time.time()` và `resource.getrusage(RUSAGE_SELF).ru_maxrss` trong cùng tiến trình (script: `scripts/m.py`). "Mở" ở đây chỉ là `ifcopenshell.open()` cộng các truy vấn `by_type`, **chưa** tính tessellation hình học.
- File đã tải: `dl/large/` (khoảng 694 MB).

## 0. Tóm tắt nhanh

- **Chưa tìm thấy file IFC sân vận động/arena nào công khai và tải được** (chi tiết ở mục 3).
- Lớn nhất đã tải và mở được: **Holter Tower** (tháp 50 tầng IFC4 làm bằng ArchiCAD, file .ifc 177 MB, 61.474 IfcProduct, RSS 1,0 GB, mở trong 6,1 s), nhưng chỉ có 12 IfcSpace.
- Nhiều IfcSpace nhất trong số đã tải: trường học Na Uy **NUS skolebygg** (307 IfcSpace, không có RSB), chung cư Estonia **Esplanades** (285 IfcSpace), **Medical-Dental Clinic** (269 IfcSpace, 3.124 RSB 1st level).
- Có sẵn RSB để làm "ground truth": Clinic (1st level), Molio-huset (1.973 RSB 2nd level), RWTH DigitalHub *with_SB* (2.581 IfcRelSpaceBoundary2ndLevel và 1.560 IfcRelSpaceBoundary1stLevel), AC20 Institute, Schependomlaan.
- Ứng viên lớn hơn và gần "đông người" hơn (hội trường, bệnh viện, văn phòng cao tầng, trường cao đẳng) đều nằm ở host **bị chặn**: openifcmodel.cs.auckland.ac.nz, tib.eu (DURAARK), zenodo.org, huggingface.co, kaggle.com, portal.nibs.org/wbdg.org, bimcollab.com, dropbox.com, 3d.bk.tudelft.nl.

## 1. Bảng ứng viên đã tải và đo thật

Tất cả URL tải đều là `raw.githubusercontent.com` hoặc `media.githubusercontent.com` (Git LFS), tải được bằng curl từ container. Bảng sắp theo mức độ phù hợp với tầng L.

| # | Tên | Loại công trình | Trang chính thức | URL tải trực tiếp | Dung lượng | Schema / phần mềm | Giấy phép (nguyên văn + URL) | IfcSpace / RSB / tầng (IfcProduct) | Thời gian mở / RSS | Trạng thái |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Holter Tower 10 | Tháp cao tầng (dự án "Holter City", Na Uy; tên phòng là văn phòng/kho/WC) | https://github.com/ara3d/IFC-toolkit (thư mục test-files) | https://raw.githubusercontent.com/ara3d/IFC-toolkit/HEAD/test-files/ISSUE_053_20181220Holter_Tower_10.ifczip | 29,4 MB ifczip, giải nén ra 177,5 MB .ifc | IFC4, ArchiCAD 20 NOR | Repo: "MIT License, Copyright (c) Ara 3D Inc." (https://github.com/ara3d/IFC-toolkit/blob/main/LICENSE.txt). README ghi test file do "Tom van Diggelen and That Open Company" cung cấp. **Giấy phép của chính file IFC: chưa xác minh.** Nguồn gốc theo BIMData là Dropbox https://www.dropbox.com/s/ybocflzyt33ilg5/Holter_Tower_10.ifc | 12 / 0 / **50 tầng** (61.474) | 6,1 s / **1.009 MB** | đã tải |
| 2 | R8_F1_MAB_AR_M3 (tháp ở Ý) | Chung cư cao tầng: 24 tầng nổi + 2 tầng hầm có chỗ đỗ xe (tên cửa tiếng Ý, "Posto auto") | như #1 | https://raw.githubusercontent.com/ara3d/IFC-toolkit/HEAD/test-files/ISSUE_098_R8_F1_MAB_AR_M3_XX_XXX_MO_7000.IFC | 68,4 MB | IFC2X3 CV2.0, Revit 2022 | như #1; giấy phép file: chưa xác minh | **0** / 0 / 28 (14.652; 6.040 IfcWallStandardCase, 1.458 IfcDoor, 1.199 IfcWindow) | 2,3 s / 447 MB | đã tải |
| 3 | ARK_NUS_skolebygg | Trường học (Na Uy): lớp học, khu chung, WC | như #1 | https://raw.githubusercontent.com/ara3d/IFC-toolkit/HEAD/test-files/ISSUE_068_ARK_NUS_skolebygg.ifc | 53,7 MB | IFC2X3, Revit 2019 | như #1; giấy phép file: chưa xác minh | **307** / 0 / 5 (5.638; 1.057 wall, 310 door) | 2,0 s / 386 MB | đã tải |
| 4 | Molio-huset (Molio_with_URIs) | Nhà văn phòng mẫu của Đan Mạch (buildingSMART Danmark) | https://github.com/buildingsmart-community/Community-Sample-Test-Files | https://media.githubusercontent.com/media/buildingsmart-community/Community-Sample-Test-Files/HEAD/IFC%202.3.0.1%20%28IFC%202x3%29/Molio/Molio_with_URIs.ifc | 73,9 MB | IFC2X3, ArchiCAD 25 | README repo: "Be aware that you are publishing under the Creative Commons Attribution 4.0 International License." (https://github.com/buildingsmart-community/Community-Sample-Test-Files/blob/main/README.md) | 117 / **1.973 (2ndLevel)** / 10 (4.192) | 2,3 s / 447 MB | đã tải |
| 5 | Medical-Dental Clinic (NIBS/ERDC, Revit 2011) | Phòng khám y tế + nha khoa (Mỹ) | https://github.com/buildingsmart-community/Community-Sample-Test-Files (thư mục Medical-Dental Clinic), bản sao ở ara3d | https://raw.githubusercontent.com/ara3d/IFC-toolkit/HEAD/test-files/dental_clinic.ifc (giống byte-size với `Clinic_Architectural.ifc` trên media.githubusercontent, 13.003.205 B) | 12,4 MB | IFC2X3, Revit 2011 + Solibri IFC Optimizer | CC BY 4.0 theo README repo community (như #4) | **269** / **3.124 (1stLevel)** / 4 (3.298; 1.080 wall) | 0,4 s / 141 MB | đã tải |
| 6 | Esplanades 1807_EP_AR_v18 (Maleva 18) | Chung cư (Estonia) | thư mục Esplanades trong repo community | https://media.githubusercontent.com/media/buildingsmart-community/Community-Sample-Test-Files/HEAD/IFC%202.3.0.1%20%28IFC%202x3%29/Esplanades/1807_EP_AR_v18.ifc | 12,1 MB | IFC2X3, ArchiCAD 22 | readme thư mục: "(c) Esplan http://www.esplan.ee/en  Published under the Creative Commons Attribution 4.0 International License." | **285** / 0 / 7 (2.862; 846 wall) | 0,6 s / 135 MB | đã tải |
| 7 | RWTH DigitalHub (FM_ARC_DigitalHub_with_SB_v1) | Văn phòng / cơ sở R&D 3 tầng (Aachen): văn phòng nhóm, cafeteria, phòng sự kiện | https://github.com/RWTH-E3D/DigitalHub | https://raw.githubusercontent.com/RWTH-E3D/DigitalHub/HEAD/Version_1/FM_ARC_DigitalHub_with_SB_v1.ifc | 17,6 MB | IFC4 DesignTransferView, Revit 2019 | "MIT License  Copyright (c) 2020 RWTH Aachen University - E3D Institute of Energy Efficiency and Sustainable Building" (https://github.com/RWTH-E3D/DigitalHub/blob/master/LICENSE) | 59 / **4.142** (2.581 IfcRelSpaceBoundary2ndLevel và 1.560 IfcRelSpaceBoundary1stLevel) / 3 | 0,6 s / 162 MB | đã tải |
| 7b | RWTH DigitalHub v2 (DigitalHub_FM-ARC_v2) | như #7 | như #7 | https://raw.githubusercontent.com/RWTH-E3D/DigitalHub/HEAD/Version_2/DigitalHub_FM-ARC_v2.ifc | 9,0 MB | IFC4 | MIT (như #7) | 64 / 0 / 3 | 0,3 s / 106 MB | đã tải |
| 7c | FM_ARC_DigitalHub (bản sao trên ara3d) | như #7 | ara3d | https://raw.githubusercontent.com/ara3d/IFC-toolkit/HEAD/test-files/FM_ARC_DigitalHub.ifc | 13,4 MB | IFC4 | MIT (bản gốc ở RWTH) | 64 / 1.123 (2ndLevel) / 3 | 0,5 s / 140 MB | đã tải |
| 8 | AC20-Institute-Var-2 (KIT "Bürogebäude") | Viện nghiên cứu / văn phòng (KIT) | ara3d | https://raw.githubusercontent.com/ara3d/IFC-toolkit/HEAD/test-files/C20-Institute-Var-2.ifc | 10,3 MB | IFC4, ArchiCAD 20 | KIT Examples được mô tả là "for unrestricted use" (nguồn thứ cấp; trang gốc ifcwiki.org bị chặn): **chưa xác minh** | 82 / 1.000 (2ndLevel) / 5 | 0,5 s / 123 MB | đã tải |
| 9 | Schependomlaan (design model) | Chung cư 10 căn (Hà Lan) | https://github.com/openBIMstandards/DataSetSchependomlaan | https://raw.githubusercontent.com/ara3d/IFC-toolkit/HEAD/test-files/schependomlaan.ifc | 47,0 MB | IFC2X3, ArchiCAD 18 | Community repo: CC BY 4.0 (bản "incl planningsdata" 65 MB ở media.githubusercontent) | 100 / 1.675 (2ndLevel) / 6 | 1,4 s / 334 MB | đã tải (cỡ M, nhà ở) |
| 10 | HHS Office (architect.ifc) | Trường/văn phòng (Hà Lan): xưởng, phòng thí nghiệm, hội sinh viên | https://github.com/opensourcebim/ifc-files | https://raw.githubusercontent.com/opensourcebim/ifc-files/HEAD/HHS%20Office/architect.ifc | 12,5 MB (MEP.ifc 37,8 MB) | IFC2X3, Revit 2010 | README: "Post your IFC data under the Creative Commons Attribution-NoDerivatives license https://creativecommons.org/licenses/by-nd/4.0/" (CC BY-ND: **không được phân phối bản đã sửa**) | 33 / 237 / 4 | 0,5 s / 139 MB | đã tải |
| 11 | bim-whale AdvancedProject | Chung cư (căn 3ROK/5ROK, mẫu Revit) | https://github.com/andrewisen/bim-whale-ifc-samples | https://raw.githubusercontent.com/andrewisen/bim-whale-ifc-samples/HEAD/AdvancedProject/IFC/AdvancedProject.ifc | 44,3 MB | IFC2X3, Revit 2021 | "MIT License Copyright (c) 2020 André "MG" Wisén" | 8 / 0 / 10 | 1,6 s / 309 MB | đã tải (ít space) |
| 12 | advanced_model (Revit Advanced Sample, UI tiếng Tây Ban Nha) | Văn phòng mẫu Revit | ara3d | https://raw.githubusercontent.com/ara3d/IFC-toolkit/HEAD/test-files/advanced_model.ifc | 33,7 MB | IFC2X3, Revit 2021 | như #1; file gốc của Autodesk: chưa xác minh | 0 / 0 / 4 (14.369) | 1,3 s / 259 MB | đã tải |
| 13 | S_Office (ArchiCAD "S-house – Sample Project") | Văn phòng mẫu ArchiCAD | ara3d | https://raw.githubusercontent.com/ara3d/IFC-toolkit/HEAD/test-files/S_Office_Integrated%20Design%20Archi.ifc | 29,6 MB | IFC2X3, ArchiCAD 24 | Graphisoft EULA (theo CSV của GNI); chưa xác minh | 0 / 0 / 7 | 1,1 s / 239 MB | đã tải |
| 14 | PRIMARK ("Colombo Fun Center") | Kết cấu thép, Tekla | ara3d | https://raw.githubusercontent.com/ara3d/IFC-toolkit/HEAD/test-files/20210221PRIMARK.ifc | 12,3 MB | IFC2X3, Tekla 21.1 | như #1 | 0 / 0 / 1 (13.808, kết cấu) | 0,5 s / 138 MB | đã tải, **không phù hợp** |
| 15 | Ifc4_Revit_ARC | Nhà mẫu (Samuel Macalister) | https://github.com/youshengCode/IfcSampleFiles | https://raw.githubusercontent.com/youshengCode/IfcSampleFiles/HEAD/Ifc4_Revit_ARC.ifc | 13,0 MB | IFC4 | README không ghi giấy phép: chưa xác minh | 0 / 0 / 6 | 0,4 s / 116 MB | đã tải, không phù hợp |

Những file khác đã đo nhưng không phù hợp: `ISSUE_102_M3D-CON-CD.ifc` (cầu đường Tekla ở Peru), `ISSUE_129_...SMC_IGC_V17.ifc` (kết cấu 10 tầng ở Pháp, 0 space), `bim-whale LargeBuilding.ifc` (1,3 MB, 8 space, "Large" chỉ là tên gọi).

Nhận xét về RAM: mọi file ở trên mở với RSS ≤ 1,01 GB. Với Holter Tower (177 MB) có thể ước lượng khoảng 5,7 MB RSS mỗi MB file khi chỉ parse. Tessellation hình học (geom iterator hay boolean) sẽ tốn hơn nhiều (chưa đo).

## 2. Ứng viên lớn hoặc đông người nhưng KHÔNG tải được từ container (cần mở host)

Dung lượng lấy từ bảng của BIMData R&D (https://github.com/bimdata/BIMData-Research-and-Development/blob/master/pages/IFC_FILES.md, đọc qua `git show`). Chưa tải nên **chưa xác minh** schema, số IfcSpace và RSB.

| Tên | Loại | URL tải (theo BIMData / nguồn) | Host cần mở | Dung lượng (BIMData) | Giấy phép | Trạng thái |
|---|---|---|---|---|---|---|
| OTC Conference Center (IFC4 / IFC2x3) | **Trung tâm hội nghị** (đông người) | http://openifcmodel.cs.auckland.ac.nz/_models/20160125OTC-Conference%20Center%20-%20IFC4.ifc ; http://openifcmodel.cs.auckland.ac.nz/_models/20160124OTC-Conference%20Center.ifc | openifcmodel.cs.auckland.ac.nz | 71,7 / 70,3 MB | chưa xác minh (re3data ghi repo Auckland theo CC BY 3.0, chưa đọc được trang gốc) | bị chặn |
| West Riverside Hospital (Architecture, HVAC, Fire, Electrical, Plumbing, Sprinkler, Structure) | **Bệnh viện 7 tầng** (mẫu Autodesk) | trang Model/Details/305 (IFC2x3) và /308 (IFC4) trên openifcmodel; BIMData liệt kê ELE 4,7, FIRE 0,9, PLB 25,0, SPR 35,7, STR 6,4 MB (**không có ARC** trong danh sách BIMData) | openifcmodel.cs.auckland.ac.nz | chưa xác minh với ARC | Theo bản repost listing: được cung cấp "courtesy of Autodesk Inc. for the purpose of research…" kèm điều kiện giữ ghi công Autodesk (nguồn thứ cấp t.me/bimiran): **chưa xác minh** | bị chặn |
| Hospital Parking Garage | Bãi đỗ xe bệnh viện | http://openifcmodel.cs.auckland.ac.nz/_models/20160125Autodesk_Hospital_Parking%20Garage_2015%20-%20IFC4.ifc | openifcmodel | 6,5 MB | chưa xác minh | bị chặn |
| Trapelo (ARC, MEP, STR) | Văn phòng (mẫu Autodesk) | openifcmodel Model/Details/302 và /303 | openifcmodel | ARC 27,2, MEP 65,3 MB | chưa xác minh | bị chặn |
| FOJAB_Landsarkivet | Lưu trữ quốc gia (Thụy Điển), công trình công cộng | https://tib.eu/data/duraark/BuildingData/03_IFC_E57/FOJAB_Landsarkivet_IFC.zip | tib.eu | 177,5 MB | DURAARK: "licensing varies" (theo OSArch, nguồn thứ cấp); re3data báo repo DURAARK offline từ 13.02.2020 | bị chặn |
| Autodesk_210King | Văn phòng cao tầng (Toronto) | https://tib.eu/data/duraark/BuildingData/03_IFC_E57/Autodesk_210-King_ifc.zip | tib.eu | 155,1 MB | chưa xác minh | bị chặn |
| NVW_DCR_LOD300 (ARC 288 MB) | chưa rõ | https://tib.eu/data/duraark/BuildingData/01_IFC/NVW_DCR-LOD_ifc.zip | tib.eu | 323,3 MB cả bộ (ARC 288,1) | chưa xác minh | bị chặn, vượt ngưỡng 300 MB nếu tính cả bộ |
| SGD_HiTOS (Statsbygg, Tromsø) | **Trường cao đẳng / đại học** | https://tib.eu/data/duraark/BuildingData/01_IFC/SGD_HiTOS_ifc.zip ; cũ: ftp://ftp.buildingsmart.no/pub/ifcfiles/HITOS/ | tib.eu, ftp.buildingsmart.no | ARC 52,9 MB | "Open government sample" theo CSV của GNI: chưa xác minh | bị chặn |
| LTU_AHouse | Nhà của Đại học Luleå (Thụy Điển) | https://tib.eu/data/duraark/BuildingData/03_IFC_E57/LTU_A-House_2014-09-25_ifc.zip | tib.eu | ARC 94,2 MB (cả bộ 553 MB) | chưa xác minh | bị chặn |
| NIBS Medical Clinic Combined / MECH… | Phòng khám (bản đầy đủ MEP) | https://portal.nibs.org/files/wl/?id=ceZq7cZxLUwLm2pouJR0mXjPpf2HuclD ; trang https://www.wbdg.org/bim/cobie/common-bim-files | portal.nibs.org, wbdg.org | Combined 112,6 MB | chưa xác minh | bị chặn |
| BIMcollab example project (9 file IFC) | chưa rõ loại công trình | https://www.bimcollab.com/Files/Example-Projects/BIMcollab_ifc_models.aspx | bimcollab.com | 175,6 MB cả bộ (ARC 26 MB) | chưa xác minh | bị chặn |
| GNI BIM Dataset (TUM) | 224 IFC từ đồ án sinh viên, có 1 file ARC 536 MB | https://doi.org/10.5281/zenodo.19722011 (README ghi; khối trích dẫn lại ghi …19722012) | zenodo.org | chưa rõ | README: "The dataset contents are licensed under CC BY 4.0" (https://github.com/ZijianWang-ZW/GNI-BIM-Dataset) | bị chặn |
| Kaggle "rvtifc-projects" | khoảng 4.596 IFC và 6.471 RVT, "real projects" (theo CSV của GNI) | https://www.kaggle.com/datasets/artemboiko/rvtifc-projects | kaggle.com (cần đăng nhập để tải) | chưa rõ | CSV của GNI ghi "CC BY or similar": **chưa xác minh**, WebSearch không tìm được trang | bị chặn, cần đăng nhập |
| DeKH (German Hospital Dataset) | **Bệnh viện** (scan + IFC tham chiếu) | https://huggingface.co/datasets/RPTU-FGMB/DeKH | huggingface.co | chưa rõ | CC BY-NC-SA 4.0 (theo awesome-bim-datasets): chưa xác minh | bị chặn |
| BIM-Edit benchmark | 11 "realistic building models" | https://huggingface.co/BIM-Edit (arXiv 2606.20146) | huggingface.co | chưa rõ | CC-BY 4.0 (theo bài báo) | bị chặn |
| Up:Town (GeoBIM benchmark) | Chung cư cao tầng Rotterdam | https://3d.bk.tudelft.nl/projects/geobim-benchmark/data.html | 3d.bk.tudelft.nl | 241 MB | Phải tham gia benchmark và ký data agreement | **cần ký thỏa thuận** |

Gợi ý mở host theo thứ tự lợi ích: **openifcmodel.cs.auckland.ac.nz** (có hội trường OTC và bệnh viện West Riverside) > **tib.eu** (210 King, Landsarkivet, HiTOS; có thể đã offline) > **zenodo.org** (GNI, DURAARK có record https://zenodo.org/record/1326652, nội dung chưa xác minh) > huggingface.co > portal.nibs.org/wbdg.org > bimcollab.com. Cũng cần mở **wiki.osarch.org** để đọc AEC Open Data directory (WebFetch báo ENOTFOUND).

## 3. Tìm sân vận động / arena

| Nơi tìm | Cách làm | Kết quả |
|---|---|---|
| GitHub repo search (WebFetch github.com/search) | "stadium ifc", "stadium bim", "arena bim", "stadium digital twin", "airport ifc", "hospital ifc" | "stadium ifc": 0 repo. "stadium bim": chỉ có ATSmithPB/_Stadium_Tools (thư viện C#/Grasshopper dựng hình sân vận động tham số, không có IFC). "stadium digital twin": 56 repo; đã clone thử `M5-Engineering-PLC/talanta-twin` (Talanta Stadium, Kenya) thì chỉ có .glb/.gltf, **không có IFC**; `tuyishimehope/stadium-digital-twin-web` không có model; `studio-public-demos/stadium-digital-twin` không clone được (repo riêng tư hoặc không tồn tại). "arena bim" chỉ ra HKIBIM "BIMAutomationArena" (cuộc thi, không có model). |
| Các repo mẫu IFC lớn trên GitHub | Liệt kê toàn bộ file trong buildingSMART/Sample-Test-Files, buildingSMART/Certification-datasets, buildingsmart-community/Community-Sample-Test-Files (200 file), IfcOpenShell/files (272), ara3d/IFC-toolkit (38), opensourcebim/ifc-files, youshengCode/IfcSampleFiles, bim-whale, viktor-platform/ifc-sample-models, ThatOpen/engine_web-ifc, engine_components, IFC4.3.x-sample-models, sylvainHellin/ifc-bench, RWTH-E3D/DigitalHub, xeokit-sdk (HEAD và v1.4.0) | Không có file nào là stadium/arena. Riêng xeokit v1.4.0 chỉ có **XKT** (không phải IFC) của HolterTower, OTCConferenceCenter, WestRiverSideHospital. |
| Danh sách dataset tổng hợp | nbharathik/awesome-bim-datasets; CSV 35 nguồn của GNI-BIM-Dataset; BIMData IFC_FILES.md (40 model, 100 file) | Không mục nào là stadium/arena. awesome-bim-datasets ghi rõ không có stadium, arena, airport, mall hay station. |
| WebSearch tổng quát (EN/FR/DE) | "stadium .ifc BIM model free download", "arena stadium IFC zenodo/figshare/mendeley", "openBIM stadium IFC dataset digital twin", "stade maquette IFC", "Stadion IFC-Modell", "Tekla sample model stadium", "Bonsai/OSArch stadium" | Chỉ có **object** IFC lẻ (ghế sân vận động, khung thành trên BIMobject, BIM&CO, ARCAT); model 3D thương mại không phải IFC (CGTrader: BC Place, Letzigrund, Linzer Stadion); model kết cấu FEM của Dlubal (RFEM, không phải IFC); **ATC-75 IFC Structural Testbed** (https://www.atcouncil.org/pdfs/ATC-75IFCBenchmark.pdf) dựa trên một phần cắt ra từ sân vận động, làm bằng Tekla, file `ifc_test2.ifc`, nhưng chỉ có PDF mô tả, **chưa thấy link tải** và đó là model kết cấu, không có IfcSpace; Tekla BIM Awards (A27 multipurpose mega stadium, Lille sports complex) chỉ là bài giới thiệu, không tải được. |
| Zenodo / Figshare / Mendeley / HF / Kaggle | WebSearch (không truy cập trực tiếp được) | Không thấy dataset stadium nào. Mendeley "Arena" là phần mềm mô phỏng Arena, không liên quan. Kaggle 4.596 IFC có thể chứa sân vận động nhưng **chưa xác minh** (cần đăng nhập và mở host). |

**Kết luận về sân vận động:** chưa có file IFC sân vận động/arena công khai nào tải được. Lý do hợp lý: model sân vận động thật là tài sản của chủ đầu tư hoặc nhà thầu (bảo mật an ninh, NDA), còn các bản "demo" công khai thường ở dạng mesh (glb/obj) dùng cho trình diễn digital twin. Hướng đi đề xuất cho tầng L:
(a) Dùng công trình đông người thay thế: hội trường OTC hoặc bệnh viện West Riverside (cần mở openifcmodel), trường học NUS skolebygg, tháp Holter hoặc R8 để thử tải quy mô.
(b) Tự dựng một **sân vận động tổng hợp** bằng IfcOpenShell hoặc Bonsai (khán đài dạng vòng, concourse, phòng kỹ thuật, nhiều nghìn IfcSpace). Có thể tham khảo hình học từ ATSmithPB/_Stadium_Tools.
(c) Xin model thật từ đối tác của người dùng.

## 4. Xếp hạng đề xuất cho tầng L

Tiêu chí: tải được ngay, lớn, nhiều tầng hoặc nhiều phòng, có giá trị kiểm thử suy luận IfcSpace và RSB, giấy phép rõ.

1. **Holter Tower** (177 MB, 50 tầng, IFC4, 61k product, RSS 1 GB): bài test **quy mô và hiệu năng** chính; gần như không có IfcSpace nên hợp để thử *suy luận IfcSpace*. Cần lưu ý giấy phép file chưa xác minh, chỉ nên dùng nội bộ.
2. **R8 tháp ở Ý** (68 MB, 28 tầng, 6.040 tường, 1.458 cửa, 0 IfcSpace): test suy luận IfcSpace trên mặt bằng lặp lại nhiều tầng, có hầm đỗ xe. Giấy phép chưa xác minh.
3. **NUS skolebygg** (54 MB, 307 IfcSpace, 0 RSB, trường học): công trình đông người tải được và có nhiều IfcSpace nhất; hợp để **sinh RSB** rồi so với IfcSpace có sẵn. Giấy phép chưa xác minh.
4. **Molio-huset** (74 MB, 117 IfcSpace, 1.973 RSB 2nd level, 10 tầng, **CC BY 4.0**): tham chiếu RSB 2nd level lớn nhất có giấy phép rõ.
5. **Medical-Dental Clinic** (13 MB, 269 IfcSpace, 3.124 RSB 1st level, CC BY 4.0): tham chiếu y tế. Thực chất là cỡ M.
6. **RWTH DigitalHub with_SB** (17,6 MB, IFC4, có cả IfcRelSpaceBoundary1stLevel và 2ndLevel, **MIT**): ground truth tốt nhất cho IFC4. Cỡ M.
7. **Esplanades** (285 IfcSpace, CC BY 4.0, chung cư 7 tầng): nhiều phòng, không có RSB.
8. Xếp sau, cần mở host: **OTC Conference Center** và **West Riverside Hospital** (openifcmodel), **Autodesk 210 King** và **FOJAB Landsarkivet** (tib.eu), **HiTOS** (trường cao đẳng). Nếu được mở mạng thì nên đưa OTC và West Riverside lên đầu vì đúng loại công trình đông người.

## 5. Nguồn (truy cập 2026-11-10)

- https://github.com/ara3d/IFC-toolkit (README, LICENSE.txt, test-files)
- https://github.com/buildingsmart-community/Community-Sample-Test-Files (README; Esplanades/readme.md)
- https://github.com/RWTH-E3D/DigitalHub (LICENSE)
- https://github.com/opensourcebim/ifc-files (README)
- https://github.com/andrewisen/bim-whale-ifc-samples (LICENSE)
- https://github.com/youshengCode/IfcSampleFiles
- https://github.com/bimdata/BIMData-Research-and-Development/blob/master/pages/IFC_FILES.md
- https://github.com/nbharathik/awesome-bim-datasets
- https://github.com/ZijianWang-ZW/GNI-BIM-Dataset (README, other_online_BIM_model_resources.csv)
- https://github.com/M5-Engineering-PLC/talanta-twin ; https://github.com/ATSmithPB/_Stadium_Tools
- https://github.com/xeokit/xeokit-sdk (tag v1.4.0, examples/models/xkt)
- https://3d.bk.tudelft.nl/projects/geobim-benchmark/data.html (qua WebSearch)
- https://www.atcouncil.org/pdfs/ATC-75IFCBenchmark.pdf (qua WebSearch)
- https://arxiv.org/abs/2606.20146 (BIM-Edit, qua WebSearch)
- re3data r3d100012443 (Open IFC Model Repository, CC BY 3.0) và r3d100012506 (DURAARK offline 13.02.2020), qua WebSearch
- Repost listing West Riverside Hospital: https://t.me/s/bimiran/2743 (nguồn thứ cấp, qua WebSearch)

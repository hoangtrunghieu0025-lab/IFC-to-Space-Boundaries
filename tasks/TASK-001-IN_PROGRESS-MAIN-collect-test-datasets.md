---
id: TASK-001
title: "[IN_PROGRESS][MAIN] Khảo sát nguồn dữ liệu và thu thập bộ bản vẽ CAD/BIM dùng để test"
category: MAIN
assignees: [claude-01]
created_by: user
created_at: 2026-11-10T11:42:16+07:00
updated_at: 2026-11-10T11:51:52+07:00
status: in_progress
priority: high
depends_on: []
---

# [IN_PROGRESS][MAIN] TASK-001 — Khảo sát nguồn dữ liệu và thu thập bộ bản vẽ CAD/BIM dùng để test
<!-- Thẻ trạng thái/category ở tên file, title và dòng này đều sinh từ `status` + `category`: sửa hai trường đó rồi chạy python3 tasks/list.py --sync -->

## Mô tả
Dự án cần dữ liệu thật để test việc suy ra `IfcSpace` và sinh `IfcRelSpaceBoundary` (xem `PRIMARY_OBJECTIVE.md`). Người dùng đã gom sơ bộ danh sách nguồn bên dưới (chưa xác minh, **chưa có URL**: agent tự tìm URL chính thức, không đoán). Việc cần làm: khảo sát từng nguồn, **tự đề ra tiêu chí chất lượng**, chấm điểm, rồi tải về những bộ dùng được.

### Danh sách nguồn do người dùng cung cấp
| Nhóm | Nguồn |
|---|---|
| IFC mẫu | buildingSMART Sample-Test-Files (Duplex, Clinic, MEP…); IFC Open House; Open IFC Model Repository (IFC2x3, IFC4); BIMCorner IFC Samples (Office, Residential, Industrial); BIMserver Demo Models |
| BIM thực tế | Autodesk Revit Advanced Sample Project (Office: Room, Stair, Corridor, MEP); Revit Sample Projects (xuất sang IFC) |
| CAD/DXF/DWG | Bibliocad; GrabCAD; CADBlocksFree; DWGFree |
| Dataset floor plan (raster/ảnh, nhãn phòng) | CubiCasa5K (~5000, nhãn Wall/Door/Window/Room); RPLAN (~80.000); Structured3D; OpenFloorPlan |

### Yêu cầu bổ sung (người dùng, "2026-11-10T11:46:33+07:00")
Người dùng đang làm **digital twin cho sân vận động 80.000 chỗ ngồi**, nên:
- **Ưu tiên cao nhất: công trình lớn, phức hợp, đông người** (sân vận động, trung tâm thương mại/mall, bệnh viện, sân bay, nhà ga, hội trường…). Càng lớn càng tốt.
- **Bắt buộc có ít nhất 1–2 file IFC loại này** (ưu tiên sân vận động/arena; nếu không tìm được IFC sân vận động thì lấy mall/bệnh viện/sân bay lớn và ghi rõ đã tìm sân vận động ở đâu, vì sao không có).
- **Đồng thời tải thêm nhiều IFC nhà ở/công trình nhỏ** để dựng nhanh và test nhanh khi phát triển thuật toán.
- **Nếu các nguồn ban đầu không đáp ứng đủ** (thiếu IFC lớn/sân vận động, thiếu số lượng, giấy phép không dùng được, bị chặn tải…) thì **được tự search thêm nguồn khác** (GitHub, Zenodo, kho dữ liệu học thuật, trang của hãng BIM/kiến trúc, dự án mở…). Nguồn mới cũng phải qua cùng bộ tiêu chí chất lượng, có URL đã mở kiểm tra thật, giấy phép và ngày truy cập, và được ghi riêng trong `dataset-survey.md` mục "Nguồn bổ sung" kèm lý do phải tìm thêm.
- Vì vậy tập dữ liệu chia thành **hai tầng**: `S` (nhỏ, chạy test mỗi lần sửa code) và `L` (lớn, test độ đúng ở quy mô thật và hiệu năng, chạy thủ công).
- Gợi ý để tìm, **chưa xác minh**: trong repo cũ `/home/hieuht50/CAD-and-BIM-deep-dive/out/poc/amsterdam-arena/` có `in/arena.dwg` (~2 MB) và các `.ifc` tự dựng từ CAD (~22 MB). Các IFC đó **không phải IFC gốc từ BIM**, không có `IfcSpace` thật nên **không dùng làm ground truth**; chỉ biết nguồn `arena.dwg` ở file đó để tìm lại nguồn/giấy phép nếu cần.

### Lưu ý phạm vi
- **IFC là ưu tiên số 1**: đây là đầu vào của pipeline. IFC có sẵn `IfcSpace` / `IfcRelSpaceBoundary` dùng làm **ground truth** để đo độ khớp.
- CAD/DXF/DWG và dataset floor plan nằm ngoài pipeline (mục "Ngoài phạm vi" trong `PRIMARY_OBJECTIVE.md`: không tạo IFC từ CAD). Vẫn khảo sát, nhưng ghi rõ chúng dùng được vào việc gì (ví dụ đối chiếu hình học phòng, tham khảo), hoặc loại với lý do. Không tải số lượng lớn (RPLAN, CubiCasa5K…) khi chưa có lý do dùng; chỉ ghi cách lấy, dung lượng, giấy phép.
- Giấy phép: file không rõ giấy phép chỉ để cục bộ trong `samples/corpus_real/` (đã git-ignore), **không commit**.

## Đầu vào (inputs)
- Danh sách nguồn ở trên (agent được tìm thêm nguồn ngoài danh sách, nhất là cho sân vận động/công trình lớn; ghi rõ nguồn nào là bổ sung); `PRIMARY_OBJECTIVE.md` (mục 3 Tiêu chí đạt); `research/_templates/finding.md`.

## Đầu ra mong đợi (expected_outputs)
1. `research/04-downstream-validation/dataset-quality-criteria.md`: tiêu chí chất lượng + cách đo (mỗi tiêu chí có ngưỡng, cách kiểm tra bằng IfcOpenShell hoặc thủ công, trọng số/cấp bắt buộc–nên có).
2. `research/04-downstream-validation/dataset-survey.md`: bảng khảo sát từng nguồn (URL chính thức, giấy phép, định dạng/phiên bản schema, số file, dung lượng, cách tải, điểm theo tiêu chí, kết luận dùng/không dùng và dùng vào việc gì).
3. `samples/manifest.yaml`: danh mục file đã tải (đường dẫn, nguồn, URL, giấy phép, ngày tải, sha256, schema, số `IfcSpace`, số `IfcRelSpaceBoundary`, điểm chất lượng).
4. `samples/fetch_datasets.py` (hoặc tương đương): tải lại được từ manifest, kiểm sha256.
5. `samples/README.md`: cách dùng, quy ước thư mục, cảnh báo giấy phép.
6. File IFC đã tải, chia theo tầng: `samples/small/` (tầng S, giấy phép cho phép thì commit) và `samples/large/` (tầng L, **không commit**: thêm vào `.gitignore`, chỉ ghi trong manifest + script tải). File chưa rõ giấy phép để ở `samples/corpus_real/` (đã git-ignore).
7. Thêm mọi nguồn đã dùng vào `research/sources.md`.

### Gợi ý tiêu chí chất lượng khởi điểm (agent được bổ sung/sửa, nêu lý do)
| Nhóm | Tiêu chí |
|---|---|
| Pháp lý | Giấy phép rõ và cho phép dùng/tái phân phối; nguồn gốc xác định được |
| Định dạng | Mở được bằng IfcOpenShell không lỗi; ghi nhận schema (IFC2x3 / IFC4 / IFC4.3); đủ cả IFC2x3 và IFC4 trong tập |
| Ground truth | Có `IfcSpace` có hình học (`Representation`); có `IfcRelSpaceBoundary` (1st/2nd level) hay không; `IfcSpace` gắn đúng `IfcBuildingStorey` |
| Hình học | Phần tử bao (tường, sàn, trần, mái, cửa, cửa sổ) có hình học trích được; ít lỗi (non-manifold, self-intersection); đơn vị và placement hợp lý |
| Độ đa dạng | Nhiều tầng; có lỗ mở (cửa/cửa sổ); tường chéo/cong; không gian không phải hộp; phòng thông nhau/shaft; mái dốc |
| Quy mô | Hai tầng: `S` nhỏ (dưới ~5 MB, dưới ~50 phòng, chạy vài giây) và `L` lớn (hàng chục–trăm MB, hàng trăm–nghìn `IfcSpace`, nhiều tầng); `L` phải mở được trên máy 16GB RAM, ghi rõ thời gian/RAM khi mở |
| Loại công trình | Điểm cộng cho công trình phức hợp đông người (sân vận động > mall/bệnh viện/sân bay > văn phòng > nhà ở); sân vận động có khán đài bậc thang, mái lớn, hành lang vòng, nhiều khối chức năng |
| Khả năng tái lập | Tải lại được bằng script; sha256 cố định |
| Mức phù hợp pipeline | Dùng được để (a) debug thuật toán, (b) đo độ chính xác so với ground truth, (c) test hiệu năng |

## Tiêu chí hoàn thành (acceptance)
- [ ] Mỗi nguồn trong danh sách có một dòng trong `dataset-survey.md` với URL chính thức đã mở kiểm tra thật (không đoán URL), có ngày truy cập; nguồn không truy cập được ghi "chưa xác minh"
- [ ] `dataset-quality-criteria.md` có ngưỡng đo được cho từng tiêu chí
- [ ] **Tầng L**: ≥1–2 file IFC công trình lớn/phức hợp đông người (ưu tiên sân vận động); mỗi file ghi dung lượng, số phần tử, số `IfcSpace`, thời gian và RAM khi mở bằng IfcOpenShell
- [ ] **Tầng S**: ≥5 file IFC nhà ở/công trình nhỏ, gồm ≥1 IFC2x3 và ≥1 IFC4, ≥3 file có `IfcSpace` có hình học
- [ ] Tổng cộng có ≥1 file nhiều tầng; mỗi file đã mở và đếm `IfcSpace` / `IfcRelSpaceBoundary` bằng IfcOpenShell (ghi lệnh đã chạy)
- [ ] `samples/manifest.yaml` khớp thực tế; chạy lại script tải thì sha256 khớp
- [ ] Không file nào chưa rõ giấy phép bị commit
- [ ] `python3 tasks/list.py` không có cảnh báo

## Phạm vi từng agent
> Toàn bộ task. Được ghi: `research/04-downstream-validation/`, `samples/`, `research/sources.md` (chỉ thêm dòng) và file task này.
- **claude-01**: toàn bộ (có thể dùng subagent nội bộ để khảo sát song song; subagent cũng chỉ ghi trong phạm vi trên).

---

# Tiến độ

## Tổng quan
| Agent | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-01 | in_progress | 2026-11-10T11:51:52+07:00 | Nhận task, bắt đầu khảo sát nguồn |

## Nhật ký — (agent nhận việc thêm mục riêng)
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-10T11:42:16+07:00 | todo | Tạo task theo danh sách nguồn người dùng cung cấp |
| 2026-11-10T11:46:33+07:00 | todo | Người dùng bổ sung: ưu tiên công trình lớn/phức hợp (sân vận động 80.000 chỗ), ≥1–2 IFC tầng L, thêm IFC nhỏ tầng S; sửa task theo đó |
| 2026-11-10T11:48:02+07:00 | todo | Người dùng bổ sung: nếu nguồn ban đầu không đáp ứng đủ thì được tự search thêm nguồn khác |

## Nhật ký — claude-01
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-10T11:51:52+07:00 | in_progress | Nhận task; bắt đầu khảo sát nguồn IFC (song song bằng subagent) |

## Blocker / câu hỏi mở
- Danh sách nguồn chưa có URL; có nguồn có thể cần đăng nhập hoặc chặn tải tự động (Bibliocad, GrabCAD, Revit Sample): nếu bị chặn thì ghi BLOCKED và nhờ người dùng tải tay.

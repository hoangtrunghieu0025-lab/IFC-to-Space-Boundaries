---
id: TASK-004
title: "[TODO][MAIN] Nghiên cứu hướng voxel hoá để suy ra IfcSpace và sinh IfcRelSpaceBoundary"
category: MAIN
assignees: []
created_by: user
created_at: 2026-11-10T12:11:25+07:00
updated_at: 2026-11-10T12:11:25+07:00
status: todo
priority: normal
depends_on: []
---

# [TODO][MAIN] TASK-004 — Nghiên cứu hướng voxel hoá để suy ra IfcSpace và sinh IfcRelSpaceBoundary
<!-- Thẻ trạng thái/category ở tên file, title và dòng này đều sinh từ `status` + `category`: sửa hai trường đó rồi chạy python3 tasks/list.py --sync -->

## Mô tả
Hướng voxel (xem `research/03-space-and-boundary-algorithms/approach-critique.md`, mục 2 hướng B): Krijnen và cộng sự (TU Delft, 2021) dựng thermal interface từ IFC bằng voxel, đánh đổi độ chính xác lấy độ bền với mô hình lỗi; tự phát hiện space từ voxel được nêu là việc tương lai. Task này đánh giá voxel có phù hợp để **suy ra IfcSpace** không, nhất là với mô hình không kín và công trình rất lớn.

Bối cảnh chung: `PRIMARY_OBJECTIVE.md` (suy ra `IfcSpace` rồi sinh `IfcRelSpaceBoundary`); công trình đích cuối là sân vận động 80.000 chỗ cho digital twin, nên **quy mô lớn và hình cong** là mối quan tâm chính. Task này là **nghiên cứu**, chưa phải cài đặt pipeline.

## Đầu vào (inputs)
- `research/03-space-and-boundary-algorithms/approach-critique.md` (mục 2 hướng B)
- Krijnen, El-Diraby, Konomi, Attalla, Thermal analysis of IFC building models using voxelized geometries (CIB W78 2021): https://eres.scix.net/pdfs/w78-2021-paper-044.pdf; bản TU Delft https://repository.tudelft.nl/record/uuid:98ad4f7e-105d-4511-baa8-57a088eb7c51; slides (SpeakerDeck, tác giả aothms)
- Voxel trong scan-to-BIM: VOX2BIM và bản mở rộng (Photogrammetrie, Fernerkundung, Geoinformation 2023), cloud2bim (tự tìm bài gốc, chưa xác minh)
- Bằng chứng về thư viện voxel hoá (ví dụ trong IfcOpenShell hay dự án của Krijnen): tự kiểm tra tài liệu/mã chính thức, **không giả định có sẵn**
- Thảo luận OSArch về voxel + trừ tường/sàn: https://community.osarch.org/discussion/811/

## Đầu ra mong đợi (expected_outputs)
Mọi file nằm trong `research/03-space-and-boundary-algorithms/voxel/` (theo mẫu `research/_templates/finding.md`):
1. `survey.md`: bảng các bài/dự án (nguồn, năm, độ phân giải voxel dùng, đầu vào/đầu ra, quy mô thử nghiệm, hạn chế)
2. `voxel-method-analysis.md`: quy trình đầy đủ (voxel hoá phần tử, tô vùng không khí, tách space, đặt tên/ID), cách xử lý rò rỉ giữa các space (khe hở tường, cửa mở), cách chọn độ phân giải, chuyển từ voxel về bề mặt/`IfcRelSpaceBoundary`
3. `memory-estimate.md`: **ước tính có công thức** bộ nhớ và thời gian cho công trình kích thước sân vận động (đặt giả định kích thước, ví dụ bounding box 300×250×60 m, ở các độ phân giải 0,1/0,25/0,5 m; ghi rõ là ước tính), và các cách giảm (octree/sparse, chia theo tầng/khối)
4. `prototype/` (tuỳ chọn): script nhỏ voxel hoá một IFC nhỏ (từ TASK-001, `samples/small/`) bằng IfcOpenShell + numpy, đếm vùng không khí kín và so với số `IfcSpace` gốc; kèm lệnh chạy và kết quả
5. `assessment.md`: đánh giá theo bảng ở mục Tiêu chí đánh giá chung bên dưới

Nhiệm vụ đặc thù: trả lời (1) voxel suy ra được `IfcSpace` hay chỉ dùng cho thermal interface; (2) sai số hình học chấp nhận được so với dung sai diện tích trong `PRIMARY_OBJECTIVE.md` (mặc định 1e-3) thì độ phân giải tối đa là bao nhiêu, voxel có đạt không.

### Tiêu chí đánh giá chung (dùng trong `assessment.md` của mọi task hướng)
| Tiêu chí | Câu hỏi cần trả lời (kèm bằng chứng) |
|---|---|
| Sinh được `IfcSpace`? | Có / chỉ boundary / chưa rõ |
| Sinh được `IfcRelSpaceBoundary` 1st/2nd level? | Có / không / chưa rõ; có `CorrespondingBoundary`, internal/external, virtual không |
| Yêu cầu hình học đầu vào | Mức sạch cần thiết (kín, không clash, đơn vị…); xử lý được mô hình lỗi thế nào |
| Hình cong / mái dốc / khán đài bậc thang | Xử lý được, một phần, hay không |
| Quy mô | Đã thử trên công trình bao lớn (số liệu có nguồn); ước tính cho sân vận động 80.000 chỗ (ghi rõ là ước tính) |
| Hiệu năng / bộ nhớ | Số liệu có nguồn hoặc đo thật |
| Độ phức tạp cài đặt, thư viện, license | Có dùng lại được mã có sẵn không; license có phù hợp không |
| Độ trưởng thành | Ngày commit cuối, có người dùng/tái lập, có test |
| Rủi ro chính | 3 rủi ro lớn nhất |
| **Kết luận** | Nên làm / làm mức cơ sở / chỉ tham khảo / loại — kèm **mức bằng chứng** (cao/trung bình/thấp) |

## Tiêu chí hoàn thành (acceptance)
- [ ] Đủ các file đầu ra ở trên, đều nằm trong `research/03-space-and-boundary-algorithms/voxel/`; không sửa file ngoài thư mục này (trừ thêm dòng vào `research/sources.md`)
- [ ] Mọi khẳng định kỹ thuật có nguồn (URL **đã mở kiểm tra**, ngày truy cập); thứ chỉ thấy qua snippet tìm kiếm hay chưa đọc toàn văn thì ghi "chưa xác minh"
- [ ] `assessment.md` điền đủ mọi dòng của bảng tiêu chí đánh giá chung, có kết luận kèm mức bằng chứng
- [ ] Mục "Chưa xác minh / việc còn lại" ở cuối mỗi file trung thực: không bịa tên chuẩn, class IFC, hàm thư viện (theo `CLAUDE.md`)
- [ ] Phần việc có chạy thật (cài, chạy script) ghi lệnh và kết quả; chưa chạy thì ghi "chưa kiểm chứng"
- [ ] Nguồn mới đã thêm vào `research/sources.md` (chỉ thêm dòng)
- [ ] `python3 tasks/list.py` không có cảnh báo

## Phạm vi từng agent
> Toàn bộ task. Được ghi: `research/03-space-and-boundary-algorithms/voxel/`, `research/sources.md` (chỉ thêm dòng) và file task này. Không sửa `research/03-space-and-boundary-algorithms/approach-critique.md`; nếu phát hiện cần sửa, ghi vào mục "Blocker / câu hỏi mở" của task.
- **(chưa giao)**: agent đầu tiên nhận ghi tên vào `assignees`, commit + push rồi mới làm (theo `collab/CONTRACT.md` mục 2).

---

# Tiến độ

## Tổng quan
| Agent | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| (chưa giao) | todo | 2026-11-10T12:11:25+07:00 | Tạo từ phản biện các hướng tiếp cận |

## Nhật ký — (agent nhận việc thêm mục riêng)
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-10T12:11:25+07:00 | todo | Tạo task từ `research/03-space-and-boundary-algorithms/approach-critique.md` |

## Blocker / câu hỏi mở
-

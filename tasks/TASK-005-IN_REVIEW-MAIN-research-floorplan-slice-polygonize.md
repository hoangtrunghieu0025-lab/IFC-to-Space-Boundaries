---
id: TASK-005
title: "[IN_REVIEW][MAIN] Nghiên cứu hướng lát cắt mặt bằng theo tầng và polygonize để suy ra IfcSpace"
category: MAIN
assignees: [claude-02]
created_by: user
created_at: 2026-11-10T12:11:25+07:00
updated_at: 2026-11-10T16:27:32+07:00
status: in_review
priority: normal
depends_on: []
---

# [IN_REVIEW][MAIN] TASK-005 — Nghiên cứu hướng lát cắt mặt bằng theo tầng và polygonize để suy ra IfcSpace
<!-- Thẻ trạng thái/category ở tên file, title và dòng này đều sinh từ `status` + `category`: sửa hai trường đó rồi chạy python3 tasks/list.py --sync -->

## Mô tả
Đây là hướng 1 của người dùng ("Polygonization") làm lại cho đầu vào IFC (xem `research/03-space-and-boundary-algorithms/approach-critique.md`, mục 1 Hướng 1): cắt các phần tử bao theo một mặt phẳng ngang của từng `IfcBuildingStorey`, polygonize các vùng kín, đóng cửa bằng `IfcDoor`/`IfcOpeningElement`, rồi đùn từ sàn lên trần. Dùng làm **mức cơ sở nhẹ nhất** để so sánh với các hướng 3D, không phải hướng CAD→IFC (đã ngoài phạm vi). Mục tiêu: biết rõ nó đúng ở đâu và hỏng ở đâu.

Bối cảnh chung: `PRIMARY_OBJECTIVE.md` (suy ra `IfcSpace` rồi sinh `IfcRelSpaceBoundary`); công trình đích cuối là sân vận động 80.000 chỗ cho digital twin, nên **quy mô lớn và hình cong** là mối quan tâm chính. Task này là **nghiên cứu**, chưa phải cài đặt pipeline.

## Đầu vào (inputs)
- `research/03-space-and-boundary-algorithms/approach-critique.md` (mục 1 Hướng 1, mục 2 hướng C)
- FreeCAD `Arch Space` (https://wiki.freecad.org/Arch_Space) và add-on FreeCAD_SketchArch (https://github.com/paullee0/FreeCAD_SketchArch): đọc mã `Detect Room`/CellComplex để hiểu họ làm gì
- Shapely (`polygonize`, `unary_union`, `buffer`) và Topologic: tài liệu chính thức
- Bằng chứng về phương pháp 2D tương tự (tự tìm: ví dụ bằng sáng chế phát hiện phòng từ vòng tường trong mặt bằng, bài báo, dự án mã nguồn mở): chỉ đưa vào khi mở được nguồn
- File IFC nhỏ từ TASK-001 (`samples/small/`) nếu đã có

## Đầu ra mong đợi (expected_outputs)
Mọi file nằm trong `research/03-space-and-boundary-algorithms/floorplan-slice-polygonize/` (theo mẫu `research/_templates/finding.md`):
1. `survey.md`: các công cụ/bài báo dùng lát cắt mặt bằng hoặc cell complex 2D để tìm phòng (nguồn, đầu vào, xử lý cửa, xử lý tường cong/chéo, hạn chế)
2. `method-analysis.md`: quy trình đề xuất cho IFC: chọn cao độ cắt (và vì sao), xử lý tường cắt không kín, đóng cửa, cột, vách kính, tường cong; lấy cao độ trần/mái để đùn; xử lý nhiều tầng thông nhau (atrium, cầu thang, khán đài bậc thang)
3. `limits.md`: liệt kê trường hợp hướng này **chắc chắn không xử lý được** (mái dốc, khán đài bậc thang, space không phải hình đùn) kèm lý do hình học; ước lượng phần công trình như sân vận động nằm ngoài khả năng
4. `prototype/` (tuỳ chọn): script Python (IfcOpenShell + Shapely) chạy trên 1–2 IFC nhỏ, so số vùng kín tìm được với số `IfcSpace` gốc; kèm lệnh chạy và kết quả
5. `assessment.md`: đánh giá theo bảng ở mục Tiêu chí đánh giá chung bên dưới

Nhiệm vụ đặc thù: nêu rõ vai trò baseline: nó cần đạt IoU diện tích bao nhiêu trên IFC nhỏ thì mới đáng làm mốc so sánh; không thiết kế pipeline CAD→IFC.

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
- [ ] Đủ các file đầu ra ở trên, đều nằm trong `research/03-space-and-boundary-algorithms/floorplan-slice-polygonize/`; không sửa file ngoài thư mục này (trừ thêm dòng vào `research/sources.md`)
- [ ] Mọi khẳng định kỹ thuật có nguồn (URL **đã mở kiểm tra**, ngày truy cập); thứ chỉ thấy qua snippet tìm kiếm hay chưa đọc toàn văn thì ghi "chưa xác minh"
- [ ] `assessment.md` điền đủ mọi dòng của bảng tiêu chí đánh giá chung, có kết luận kèm mức bằng chứng
- [ ] Mục "Chưa xác minh / việc còn lại" ở cuối mỗi file trung thực: không bịa tên chuẩn, class IFC, hàm thư viện (theo `CLAUDE.md`)
- [ ] Phần việc có chạy thật (cài, chạy script) ghi lệnh và kết quả; chưa chạy thì ghi "chưa kiểm chứng"
- [ ] Nguồn mới đã thêm vào `research/sources.md` (chỉ thêm dòng)
- [ ] `python3 tasks/list.py` không có cảnh báo

## Phạm vi từng agent
> Toàn bộ task. Được ghi: `research/03-space-and-boundary-algorithms/floorplan-slice-polygonize/`, `research/sources.md` (chỉ thêm dòng) và file task này. Không sửa `research/03-space-and-boundary-algorithms/approach-critique.md`; nếu phát hiện cần sửa, ghi vào mục "Blocker / câu hỏi mở" của task.
- **claude-02**: toàn bộ.

---

# Tiến độ

## Tổng quan
| Agent | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-02 | in_review | 2026-11-10T16:27:32+07:00 | PARTIAL: 5 file + prototype; chưa cài bước chiều cao/đùn, chưa điều tra các ca không khớp |

## Nhật ký — claude-02
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-10T12:11:25+07:00 | todo | Tạo task từ `research/03-space-and-boundary-algorithms/approach-critique.md` |
| 2026-11-10T15:58:24+07:00 | in_progress | Nhận việc (làm trong lúc chờ build IFC2SB của TASK-002) |
| 2026-11-10T16:27:32+07:00 | in_review | Báo cáo **PARTIAL**. File: `research/03-space-and-boundary-algorithms/floorplan-slice-polygonize/{survey,method-analysis,limits,assessment}.md`, `prototype/{slice_polygonize.py,README.md,results/}`. Lệnh: `python slice_polygonize.py samples/small/*.ifc --dz 1.0 [--close 0.05]` (venv: ifcopenshell 0.9.0.post1, shapely 2.2.0, numpy 2.5.4). Kết quả (6 IFC nhỏ, 63 IfcSpace): 38/63 khớp IoU diện tích ≥ 0,5 ở z = 1 m trên cao độ tầng (`close = 0`); `--close 0.05` tăng FZK-Haus 3 → 4; cắt và polygonize ≤ 0,25 s mỗi file. Kết luận: làm mức cơ sở (baseline), mức bằng chứng trung bình. Đã đọc mã SketchArch `DetectRoom`. |

## Blocker / câu hỏi mở
- Chưa điều tra nguyên nhân các ca không khớp (duplex-a, bsi-ifc4: 0 phòng).
- Chưa cài bước chiều cao và đùn thành `IfcSpace`; chưa thử nhiều giá trị `dz`.
- Bonsai, floorplan-parser, Cloud2BIM chỉ thấy qua kết quả tìm kiếm.

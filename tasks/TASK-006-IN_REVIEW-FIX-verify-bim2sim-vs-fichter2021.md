---
id: TASK-006
title: "[IN_REVIEW][FIX] Đối chiếu bài Fichter 2021 (IBPSA) với phần bim2sim của TASK-002"
category: FIX
assignees: [claude-01]
created_by: claude-01
created_at: 2026-11-10T16:24:32+07:00
updated_at: 2026-11-10T16:26:39+07:00
status: in_review
priority: normal
depends_on: []
---

# [IN_REVIEW][FIX] TASK-006 — Đối chiếu bài Fichter 2021 (IBPSA) với phần bim2sim của TASK-002
<!-- Thẻ trạng thái/category ở tên file, title và dòng này đều sinh từ `status` + `category`: sửa hai trường đó rồi chạy python3 tasks/list.py --sync -->

## Mô tả
**Task gốc: TASK-002** (claude-02), file `research/03-space-and-boundary-algorithms/graph-topology/bim2sim-analysis.md`.
Người dùng yêu cầu (2026-11-10): đọc bài Fichter, Richter, Frisch, van Treeck (2021), *Automatic generation of second level space boundary geometry from IFC models*, IBPSA BS2021 (https://publications.ibpsa.org/proceedings/bs/2021/papers/bs2021_30156.pdf), đối chiếu với phần bim2sim của TASK-002 và nghiên cứu sâu hơn, vì người dùng chưa tin kết quả hiện có.

## Đầu vào (inputs)
- Bài Fichter 2021 (link trên); bài liên quan được README bim2sim trích (Richter 2021, Richter 2022)
- Mã bim2sim https://github.com/BIM2SIM/bim2sim (toàn bộ lịch sử), mã IFC2SB https://github.com/RWTH-E3D/IFC2SB
- `research/03-space-and-boundary-algorithms/graph-topology/bim2sim-analysis.md`, `ifc2sb-analysis.md` (claude-02)
- Bộ IFC của TASK-001 (`samples/`)

## Đầu ra mong đợi (expected_outputs)
- `research/03-space-and-boundary-algorithms/graph-topology/bim2sim-crosscheck.md` (file mới; **không sửa file của claude-02**): bảng đối chiếu từng khẳng định của `bim2sim-analysis.md` với bài báo và mã (đúng / đúng một phần / thiếu / sai), phát hiện mới, ý nghĩa cho dự án
- Thêm nguồn mới vào `research/sources.md`

## Tiêu chí hoàn thành (acceptance)
- [x] Mỗi khẳng định trong `bim2sim-analysis.md` có kết luận kèm bằng chứng (đoạn bài báo hoặc file:dòng trong mã)
- [x] Phần chạy thật ghi lệnh và kết quả; phần chưa chạy ghi "chưa kiểm chứng"
- [x] Đề xuất sửa cho claude-02 ghi ở mục Blocker của task này (không tự sửa file TASK-002)
- [x] `python3 tasks/list.py` không có cảnh báo

## Phạm vi từng agent
> Được ghi: `research/03-space-and-boundary-algorithms/graph-topology/bim2sim-crosscheck.md` (file mới), `research/sources.md` (chỉ thêm dòng), file task này. Không sửa các file khác trong `graph-topology/` (thuộc TASK-002).
- **claude-01**: toàn bộ.

---

# Tiến độ

## Tổng quan
| Agent | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-01 | in_review | 2026-11-10T16:26:39+07:00 | PARTIAL: đối chiếu xong; chưa chạy bim2sim end-to-end, chưa đọc Richter 2021 |

## Nhật ký — claude-01
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-10T16:24:32+07:00 | in_progress | Tạo task theo yêu cầu người dùng; đã mở mạng cho publications.ibpsa.org, tải và đọc toàn văn Fichter 2021 và Richter 2022; clone bim2sim (`270cd0a36f`, 5.987 commit) và IFC2SB (`96a89cd`) |
| 2026-11-10T16:26:39+07:00 | in_review | Báo cáo **PARTIAL**. Viết `graph-topology/bim2sim-crosscheck.md`; thêm 3 nguồn vào `research/sources.md`. Lệnh: `pdftotext` 2 bài; `git clone` bim2sim (đầy đủ) + IFC2SB; `git log -S/--grep`; script IfcOpenShell tái lập bộ lọc level `sb_creation.py:393-395` trên 14 IFC có RSB → 5 file bị bỏ sạch boundary. Kết quả: 3 kết luận chính của TASK-002 đúng; 3 điểm cần chỉnh, 5 phát hiện bỏ sót (xem file) |

## Blocker / câu hỏi mở
- (claude-01 → claude-02) Đề xuất sửa `bim2sim-analysis.md` và `ifc2sb-analysis.md`: xem mục 6 của `bim2sim-crosscheck.md`. claude-01 không tự sửa file TASK-002.
- Cần mở mạng `tuprints.ulb.tu-darmstadt.de` (bài Richter 2021 về thuật toán sửa boundary của bim2sim) nếu muốn đọc tiếp.
- Chưa chạy bim2sim end-to-end (cần conda + pythonocc-core).

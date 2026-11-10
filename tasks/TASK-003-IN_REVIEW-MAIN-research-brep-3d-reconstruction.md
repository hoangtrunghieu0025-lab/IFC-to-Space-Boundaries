---
id: TASK-003
title: "[IN_REVIEW][MAIN] Nghiên cứu hướng dựng thể tích IfcSpace từ hình học B-rep 3D và sinh boundary"
category: MAIN
assignees: [claude-02]
created_by: user
created_at: 2026-11-10T12:11:25+07:00
updated_at: 2026-11-10T15:04:20+07:00
status: in_review
priority: normal
depends_on: []
---

# [IN_REVIEW][MAIN] TASK-003 — Nghiên cứu hướng dựng thể tích IfcSpace từ hình học B-rep 3D và sinh boundary
<!-- Thẻ trạng thái/category ở tên file, title và dòng này đều sinh từ `status` + `category`: sửa hai trường đó rồi chạy python3 tasks/list.py --sync -->

## Mô tả
Hướng hình học 3D (B-rep, boolean/giao mặt) là hướng chủ đạo trong văn liệu về 2nd-level boundary (xem `research/03-space-and-boundary-algorithms/approach-critique.md`, mục 2 hướng A). Task này nghiên cứu sâu: dựng lại thể tích space từ phần tử bao (thuật toán Automatic Space Generation của UCL) và sinh 2nd-level boundary (CBIP, Ying & Lee). Ưu tiên hiểu giới hạn với **hình cong, công trình rất lớn** (mục tiêu sân vận động 80.000 chỗ).

Bối cảnh chung: `PRIMARY_OBJECTIVE.md` (suy ra `IfcSpace` rồi sinh `IfcRelSpaceBoundary`); công trình đích cuối là sân vận động 80.000 chỗ cho digital twin, nên **quy mô lớn và hình cong** là mối quan tâm chính. Task này là **nghiên cứu**, chưa phải cài đặt pipeline.

## Đầu vào (inputs)
- `research/03-space-and-boundary-algorithms/approach-critique.md` (mục 2 hướng A)
- Lilis, Katsigarakis, Rovas (UCL, 2021), Automatic IFC data enrichment with space geometries for BEPS: https://discovery.ucl.ac.uk/id/eprint/10169911/1/bs2021_30888.pdf (**cần đọc phần phương pháp**, bản trước mới đọc phần giới thiệu; file PDF nén, dùng `pdftotext` nếu có)
- Lilis et al. 2017 (CBIP), Automation in Construction vol. 76; Ying & Lee 2021, Automation in Construction (tóm tắt: https://pure.uos.ac.kr/en/publications/generating-second-level-space-boundaries-from-large-scale-ifc-com/)
- Các tài liệu bài UCL trích dẫn (chưa xác minh, tự tìm và kiểm tra): Rose & Bazjanac 2015; Ladenhauf et al. 2016; El-Diraby et al. 2017; Fichter et al. 2021 (RWTH, second-level space boundary geometry); OpenCascade publication page
- IfcOpenShell geometry API (tài liệu chính thức) và OpenCascade/CGAL: khả năng boolean trên mô hình lớn

## Đầu ra mong đợi (expected_outputs)
Mọi file nằm trong `research/03-space-and-boundary-algorithms/brep-3d-reconstruction/` (theo mẫu `research/_templates/finding.md`):
1. `survey.md`: bảng các bài/dự án (nguồn, năm, phương pháp, đầu vào, đầu ra, mô hình thử nghiệm và quy mô, hạn chế tự nhận)
2. `ucl-asg-analysis.md`: mô tả đầy đủ thuật toán sinh space của UCL (các bước, giả định, tiêu chí kiểm tra lỗi hình học đầu vào mà họ đề ra: **trích nguyên tiêu chí** để dùng ở TASK-001 và pipeline)
3. `boundary-generation-analysis.md`: CBIP và Ying & Lee: cách ghép boundary với phần tử, xử lý lỗ mở, ghép `CorrespondingBoundary`, phân loại internal/external, virtual boundary
4. `scalability-notes.md`: hiệu năng trên mô hình lớn (số liệu có nguồn); nơi nghẽn; thư viện hình học phù hợp (OpenCascade, CGAL, trimesh) và giới hạn từng cái; kỹ thuật tăng tốc (R-tree, chia theo tầng/khối)
5. `assessment.md`: đánh giá theo bảng ở mục Tiêu chí đánh giá chung bên dưới

Nhiệm vụ đặc thù: nêu rõ bài nào đã thử trên công trình quy mô lớn, quy mô bao nhiêu; **không suy diễn** rằng phương pháp chạy được trên sân vận động nếu bài không thử. Nếu chạy thử bằng IfcOpenShell trên IFC nhỏ thì ghi lệnh và kết quả.

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
- [ ] Đủ các file đầu ra ở trên, đều nằm trong `research/03-space-and-boundary-algorithms/brep-3d-reconstruction/`; không sửa file ngoài thư mục này (trừ thêm dòng vào `research/sources.md`)
- [ ] Mọi khẳng định kỹ thuật có nguồn (URL **đã mở kiểm tra**, ngày truy cập); thứ chỉ thấy qua snippet tìm kiếm hay chưa đọc toàn văn thì ghi "chưa xác minh"
- [ ] `assessment.md` điền đủ mọi dòng của bảng tiêu chí đánh giá chung, có kết luận kèm mức bằng chứng
- [ ] Mục "Chưa xác minh / việc còn lại" ở cuối mỗi file trung thực: không bịa tên chuẩn, class IFC, hàm thư viện (theo `CLAUDE.md`)
- [ ] Phần việc có chạy thật (cài, chạy script) ghi lệnh và kết quả; chưa chạy thì ghi "chưa kiểm chứng"
- [ ] Nguồn mới đã thêm vào `research/sources.md` (chỉ thêm dòng)
- [ ] `python3 tasks/list.py` không có cảnh báo

## Phạm vi từng agent
> Toàn bộ task. Được ghi: `research/03-space-and-boundary-algorithms/brep-3d-reconstruction/`, `research/sources.md` (chỉ thêm dòng) và file task này. Không sửa `research/03-space-and-boundary-algorithms/approach-critique.md`; nếu phát hiện cần sửa, ghi vào mục "Blocker / câu hỏi mở" của task.
- **claude-02**: toàn bộ.

---

# Tiến độ

## Tổng quan
| Agent | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-02 | in_review | 2026-11-10T15:04:20+07:00 | PARTIAL: 5 file xong; thiếu toàn văn Ying & Lee 2021, chưa chạy thuật toán nào |

## Nhật ký — claude-02
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-10T12:11:25+07:00 | todo | Tạo task từ `research/03-space-and-boundary-algorithms/approach-critique.md` |
| 2026-11-10T14:58:14+07:00 | in_progress | Nhận việc (làm trong lúc chờ build IFC2SB của TASK-002); bắt đầu đọc bài UCL, CBIP, Ying & Lee |
| 2026-11-10T15:04:20+07:00 | in_review | Báo cáo **PARTIAL**. File: `research/03-space-and-boundary-algorithms/brep-3d-reconstruction/{survey,ucl-asg-analysis,boundary-generation-analysis,scalability-notes,assessment}.md`. Đã đọc toàn văn ASG (UCL 2021), CBIP (Lilis 2017, bản thảo đã sửa), Fichter 2021; lệnh: `curl` tải PDF, `pdftotext -layout`. Kết luận: nên làm pipeline hai nửa ASG (sinh space) + CBIP/BIP (boundary mức 2); mức bằng chứng trung bình. Không có số liệu thời gian/RAM trong nguồn; chưa chạy thuật toán nào (chưa kiểm chứng). Phát hiện phụ: CBIP tự nhận 'graph-less' và cần `IfcSpace`; danh mục bài IBPSA ghi nhầm nơi đăng của van Treeck & Rank 2007 (theo CBIP: Eng. with Computers 23(2), DOI 10.1007/s00366-006-0053-7). |

## Blocker / câu hỏi mở
- **Toàn văn Ying & Lee 2021** (Automation in Construction 126:103659, DOI 10.1016/j.autcon.2021.103659): paywall Elsevier; chỉ đọc được tóm tắt. Nhờ người dùng cung cấp PDF nếu có quyền truy cập.
- Chưa tìm thấy mã nguồn công khai của ASG/CBIP.
- Chưa chạy thử thuật toán nào; nếu cần prototype ASG-kiểu, nên lập task riêng.

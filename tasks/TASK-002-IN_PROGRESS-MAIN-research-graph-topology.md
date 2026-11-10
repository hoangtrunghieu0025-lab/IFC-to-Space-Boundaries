---
id: TASK-002
title: "[IN_PROGRESS][MAIN] Nghiên cứu hướng Graph / Topology để suy ra IfcSpace và sinh IfcRelSpaceBoundary"
category: MAIN
assignees: [claude-02]
created_by: user
created_at: 2026-11-10T12:11:25+07:00
updated_at: 2026-11-10T12:25:55+07:00
status: in_progress
priority: high
depends_on: []
---

# [IN_PROGRESS][MAIN] TASK-002 — Nghiên cứu hướng Graph / Topology để suy ra IfcSpace và sinh IfcRelSpaceBoundary
<!-- Thẻ trạng thái/category ở tên file, title và dòng này đều sinh từ `status` + `category`: sửa hai trường đó rồi chạy python3 tasks/list.py --sync -->

## Mô tả
Người dùng quyết định **giữ hướng Graph** (xem `research/03-space-and-boundary-algorithms/approach-critique.md`, mục 1 Hướng 2). Bằng chứng hiện có **chưa ủng hộ** mô tả "Wall → Graph → Cycle → Space": README của IFC2SB không mô tả thuật toán (thư viện dùng: OpenCASCADE, IfcOpenShell, Clipper, Triangle, ConvexDecomposition; có cờ `--graph` chưa rõ vai trò); không tìm thấy bằng chứng bim2sim có "Topology Graph → Space Graph → Boundary Graph". Task này phải **xác minh** hướng Graph có thật không, và nếu có thì thiết kế được thế nào. Nếu kết luận hướng này thực chất không dùng graph thì ghi rõ và đề nghị đổi tên task (không gượng ép).

Bối cảnh chung: `PRIMARY_OBJECTIVE.md` (suy ra `IfcSpace` rồi sinh `IfcRelSpaceBoundary`); công trình đích cuối là sân vận động 80.000 chỗ cho digital twin, nên **quy mô lớn và hình cong** là mối quan tâm chính. Task này là **nghiên cứu**, chưa phải cài đặt pipeline.

## Đầu vào (inputs)
- `research/03-space-and-boundary-algorithms/approach-critique.md` (đọc kỹ mục 1 Hướng 2 và mục 2 hướng C)
- IFC2SB: https://github.com/RWTH-E3D/IFC2SB (mirror; nguồn gốc ghi `git.rwth-aachen.de/fichter/ifc2sb`, chưa kiểm tra) và luận án của tác giả (Eric Fichter, RWTH E3D; README trỏ tới luận án: tự tìm bản chính thức)
- bim2sim: https://github.com/BIM2SIM/bim2sim (đọc mã phần xử lý space boundary)
- FreeCAD_SketchArch (CellComplex) https://github.com/paullee0/FreeCAD_SketchArch và Topologic (thảo luận OSArch https://community.osarch.org/discussion/811/)
- File IFC nhỏ từ TASK-001 (`samples/small/`) nếu đã có, để thử chạy công cụ

## Đầu ra mong đợi (expected_outputs)
Mọi file nằm trong `research/03-space-and-boundary-algorithms/graph-topology/` (theo mẫu `research/_templates/finding.md`):
1. `survey.md`: tổng quan các dự án/bài báo thuộc hướng này, mỗi mục ghi: nguồn, năm, ngôn ngữ, license, trạng thái bảo trì (ngày commit cuối), đầu vào/đầu ra, có sinh `IfcSpace` hay chỉ boundary
2. `ifc2sb-analysis.md`: phân tích IFC2SB từ luận án và mã: các bước thuật toán, **graph được dùng ở đâu** (nếu có), cấu trúc dữ liệu, cách xử lý clash/gap, giả định về đầu vào, hạn chế; kết quả cố gắng cài và chạy (lệnh, kết quả, lỗi) trên ít nhất 1 IFC nhỏ; đối chiếu lỗi cài đặt báo ở Univ. of Tulsa
3. `bim2sim-analysis.md`: bim2sim sinh hay chỉ đọc space boundary; có bước graph không (chỉ ra file/hàm trong mã)
4. `graph-design-sketch.md`: nếu hướng Graph khả thi, phác thảo thiết kế cho dự án: nút và cạnh là gì (phần tử bao, điểm giao, mặt?), cách tìm vùng kín (chu trình/mặt của đồ thị phẳng, hoặc cell complex), cách đưa vào `IfcSpace` và boundary, độ phức tạp, điểm yếu với tường cong và mái dốc
5. `assessment.md`: đánh giá theo bảng ở mục Tiêu chí đánh giá chung bên dưới

Nhiệm vụ đặc thù: trả lời dứt khoát 3 câu hỏi: (1) IFC2SB có dùng graph không, ở bước nào; (2) bim2sim có sinh space boundary hay chỉ đọc; (3) cell complex/Topologic có đủ trưởng thành để dùng không (bằng chứng, không cảm tính).

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
- [ ] Đủ các file đầu ra ở trên, đều nằm trong `research/03-space-and-boundary-algorithms/graph-topology/`; không sửa file ngoài thư mục này (trừ thêm dòng vào `research/sources.md`)
- [ ] Mọi khẳng định kỹ thuật có nguồn (URL **đã mở kiểm tra**, ngày truy cập); thứ chỉ thấy qua snippet tìm kiếm hay chưa đọc toàn văn thì ghi "chưa xác minh"
- [ ] `assessment.md` điền đủ mọi dòng của bảng tiêu chí đánh giá chung, có kết luận kèm mức bằng chứng
- [ ] Mục "Chưa xác minh / việc còn lại" ở cuối mỗi file trung thực: không bịa tên chuẩn, class IFC, hàm thư viện (theo `CLAUDE.md`)
- [ ] Phần việc có chạy thật (cài, chạy script) ghi lệnh và kết quả; chưa chạy thì ghi "chưa kiểm chứng"
- [ ] Nguồn mới đã thêm vào `research/sources.md` (chỉ thêm dòng)
- [ ] `python3 tasks/list.py` không có cảnh báo

## Phạm vi từng agent
> Toàn bộ task. Được ghi: `research/03-space-and-boundary-algorithms/graph-topology/`, `research/sources.md` (chỉ thêm dòng) và file task này. Không sửa `research/03-space-and-boundary-algorithms/approach-critique.md`; nếu phát hiện cần sửa, ghi vào mục "Blocker / câu hỏi mở" của task.
- **claude-02**: toàn bộ.

---

# Tiến độ

## Tổng quan
| Agent | Trạng thái | Cập nhật lúc | Ghi chú ngắn |
|---|---|---|---|
| claude-02 | in_progress | 2026-11-10T12:25:55+07:00 | Đã viết 5 file; còn chờ build IFC2SB và luận án (BLOCKED tải tay) |

## Nhật ký — claude-02
| Thời điểm (GMT+7) | Trạng thái | Nội dung |
|---|---|---|
| 2026-11-10T12:11:25+07:00 | todo | Tạo task từ `research/03-space-and-boundary-algorithms/approach-critique.md` |
| 2026-11-10T12:14:01+07:00 | in_progress | Nhận việc, bắt đầu xác minh IFC2SB (README, luận án, mã) |
| 2026-11-10T12:25:55+07:00 | in_progress | Đã viết `survey.md`, `ifc2sb-analysis.md`, `bim2sim-analysis.md`, `graph-design-sketch.md`, `assessment.md` trong `research/03-space-and-boundary-algorithms/graph-topology/`. Kết luận chính: IFC2SB có dùng graph (đồ thị kề mặt 3D sau General Fuse, space = thành phần liên thông); bim2sim chỉ đọc boundary; Topologic chưa đủ bằng chứng. Đã đọc toàn văn bài IBPSA 2021 và mã IFC2SB/bim2sim/SketchArch. Lệnh: `git clone` 3 repo (scratchpad), `pdftotext` bài IBPSA, `docker build` (nền, chưa xong). |

## Blocker / câu hỏi mở
- **Luận án Fichter 2022**: trang RWTH (https://publications.rwth-aachen.de/record/856693) chặn tải tự động bằng thử thách JavaScript chống bot; agent không vượt qua. **Nhờ người dùng tải PDF tay** rồi đặt vào thư mục cục bộ (ví dụ `samples/corpus_real/`).
- **Build IFC2SB trong Docker** (Dockerfile ở scratchpad phiên) đang chạy nền, mới ở bước kéo ảnh Ubuntu 20.04 do mạng chậm; biên dịch OCCT 7.5.3 và IfcOpenShell 0.6.0 sẽ mất lâu. Chưa có kết quả chạy: ghi "chưa kiểm chứng".
- Cần file IFC4 nhỏ có giấy phép rõ để chạy thử (chờ TASK-001, hoặc người dùng cung cấp).
- `approach-critique.md` (ngoài quyền ghi) cần cập nhật mục 1 Hướng 2 theo kết quả mới: đề nghị người dùng quyết định.


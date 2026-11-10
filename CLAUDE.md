# Quy tắc chung cho mọi agent

Mục tiêu dự án: xem `PRIMARY_OBJECTIVE.md`.

## Ngôn ngữ & định dạng
- Viết tiếng Việt; giữ nguyên thuật ngữ kỹ thuật tiếng Anh (IfcSpace, IfcRelSpaceBoundary, Pset, B-rep…).
- Mỗi ghi chú research dùng mẫu `research/_templates/finding.md`.

## Độ tin cậy
- Mọi khẳng định kỹ thuật phải có nguồn (URL + ngày truy cập). Thêm nguồn vào `research/sources.md` (chỉ thêm dòng mới, không sửa dòng cũ).
- Không bịa tên chuẩn, class/thuộc tính IFC, thuật ngữ MVD hay tên tham số thư viện. Không chắc thì ghi rõ "chưa xác minh".

## Phân quyền ghi (tránh xung đột khi chạy song song)
- Mỗi agent research CHỈ ghi vào thư mục được giao: `research/NN-<chủ đề>/`, hoặc thư mục con của nó nếu thư mục đó chia theo hướng tiếp cận (ví dụ `research/03-space-and-boundary-algorithms/voxel/`). Task chia nhiều hướng thì mỗi task chỉ ghi vào thư mục con của hướng mình; file tổng quan ở gốc thư mục (ví dụ `approach-critique.md`) chỉ sửa khi task yêu cầu. Được đọc thư mục khác.
- Chỉ agent `synthesizer` được ghi vào `docs/`.
- Không sửa `PRIMARY_OBJECTIVE.md`, `CLAUDE.md`, `.claude/` nếu không được yêu cầu.

## Đặt tên file
- Theo chủ đề, chữ thường, gạch ngang: `ifc-spatial-structure.md`.

## Cộng tác nhiều agent (claude-01, claude-02, …)
- Theo `collab/CONTRACT.md`; push thẳng lên `main`, pull --rebase trước khi push. Không dùng mailbox.
- Việc được giao trong `tasks/` (xem `tasks/README.md`); cập nhật tiến độ trong file task của mình.

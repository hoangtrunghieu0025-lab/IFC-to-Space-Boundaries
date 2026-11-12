# Quy tắc chung cho mọi agent

Mục tiêu dự án: xem `PRIMARY_OBJECTIVE.md`.

## Ngôn ngữ & định dạng
- Viết tiếng Việt; giữ nguyên thuật ngữ kỹ thuật tiếng Anh (IfcSpace, IfcRelSpaceBoundary, Pset, B-rep…).
- Mỗi ghi chú research dùng mẫu `research/_templates/finding.md`.

## Độ tin cậy
- Mọi khẳng định kỹ thuật phải có nguồn (URL + ngày truy cập). Thêm nguồn vào `research/sources.md` (chỉ thêm dòng mới, không sửa dòng cũ).
- Không bịa tên chuẩn, class/thuộc tính IFC, thuật ngữ MVD hay tên tham số thư viện. Không chắc thì ghi rõ "chưa xác minh".

## Quyền ghi (các agent được sửa file của nhau)
- Mỗi task có **thư mục đầu ra mặc định** (ví dụ `research/NN-<chủ đề>/` hoặc thư mục con theo hướng như `research/03-space-and-boundary-algorithms/voxel/`); viết kết quả mới của task vào đó. Được đọc mọi thư mục.
- **Mọi agent được sửa file của agent khác** (research, `samples/`, `src/`, `reports/`, `docs/`, file task…) khi cần sửa sai, bổ sung bằng chứng hoặc gộp kết quả. Khi sửa:
  - `git pull --rebase origin main` ngay trước khi sửa; commit nhỏ, push ngay;
  - commit message nêu rõ sửa file của ai và vì sao, ví dụ `research(claude-01): fix bim2sim-analysis (TASK-002) per Fichter 2021`;
  - ghi một dòng vào nhật ký của task liên quan (mục của mình); không xoá nhật ký của agent khác;
  - không xoá nội dung của người khác nếu không thay bằng nội dung đúng hơn kèm nguồn; đoạn sửa lớn thì ghi chú `[sửa bởi claude-0x, YYYY-MM-DD: lý do]`.
- **Sửa/bổ sung kết quả của một task thì ghi thẳng vào task đó** (thêm tên mình vào `assignees`), không tạo task mới chỉ để sửa.
- `docs/` do agent `synthesizer` viết chính; agent khác được sửa theo các quy tắc trên.
- Không sửa `PRIMARY_OBJECTIVE.md`, `CLAUDE.md`, `.claude/` nếu người dùng không yêu cầu.

## Đặt tên file
- Theo chủ đề, chữ thường, gạch ngang: `ifc-spatial-structure.md`.

## Cộng tác nhiều agent (claude-01, claude-02, …)
- Theo `collab/CONTRACT.md`; push thẳng lên `main`, pull --rebase trước khi push. Không dùng mailbox.
- Việc được giao trong `tasks/` (xem `tasks/README.md`); cập nhật tiến độ trong file task của mình.

# Quy tắc chung cho mọi agent

Mục tiêu dự án: xem `PRIMARY_OBJECTIVE.md`.

## Ngôn ngữ & định dạng
- Viết tiếng Việt; giữ nguyên thuật ngữ kỹ thuật tiếng Anh (IfcSpace, IfcRelSpaceBoundary, Pset, B-rep…).
- Mỗi ghi chú research dùng mẫu `research/_templates/finding.md`.

## Nguồn
- Mọi khẳng định kỹ thuật phải có nguồn (URL + ngày truy cập). Thêm nguồn vào `research/sources.md` (chỉ thêm dòng mới, không sửa dòng cũ).
- Không bịa tên chuẩn, class/thuộc tính IFC, thuật ngữ MVD hay tên tham số thư viện. Điều không có nguồn thì không đưa vào tài liệu.

## Quy tắc viết tài liệu (BẮT BUỘC, ưu tiên cao hơn mọi mẫu và quy ước khác)
Áp dụng cho mọi tài liệu agent viết ra: docx, Google Docs, Claude Docs, file `.md` trong `research/`, `docs/`, `reports/`, `tasks/`, và mọi định dạng khác.

- **Tài liệu chỉ chứa thông tin thuộc nội dung đề tài**: định nghĩa, dữ kiện, công thức, thuật toán, số đo, kết quả, mô tả phương pháp, danh sách tài liệu tham khảo.
- **Được phép**: trích dẫn nguồn (tác giả, năm, tên tài liệu, URL, ngày truy cập) và đánh số tham chiếu `[n]`.
- **Cấm viết vào tài liệu**:
  - mọi chỉ báo độ tin cậy hoặc độ chắc chắn: nhãn như `[suy luận]`, `[đã đo]`, `[chưa xác minh]`, `[nguồn]`; mục "Độ tin cậy"; cụm rào đón như "có thể", "nghi là", "có lẽ", "chưa chắc", "theo tôi";
  - mọi lời nhận định, nhận xét, đánh giá, cảnh báo, lưu ý, đề xuất hay ý kiến của agent;
  - mô tả công việc của agent (đã đọc gì, chưa đọc gì, chưa chạy lại, tác giả báo cáo tính ra);
  - lời mở đầu, lời kết, tóm tắt kiểu "kết luận chính" mang tính bình luận.
- Khi cần nói về độ chắc chắn, giới hạn hiểu biết hoặc việc còn dở thì nói trong phản hồi chat cho người dùng, không viết vào tài liệu.
- Quy tắc này thay thế các trường "Độ tin cậy", "Kết luận ngắn" mang tính nhận định và mục "Chưa xác minh" trong `research/_templates/finding.md`; không điền các trường đó.

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

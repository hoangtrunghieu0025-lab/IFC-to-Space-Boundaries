# CONTRACT giữa các agent claude-0x

Các agent làm việc trên cùng repo GitHub, phối hợp qua commit trên `main` và các file trong repo (không dùng mailbox); người dùng chuyển yêu cầu giữa các agent khi cần.

## 1. Định danh
- Mỗi agent có tên `claude-0x`, trong đó `x` là số thứ tự: `claude-01`, `claude-02`, `claude-03`…
- Các agent **ngang hàng**, không phân biệt vai trò hay môi trường chạy: ai cũng có thể nhận bất kỳ việc nào (nghiên cứu, code, chạy pipeline, kiểm tra, tài liệu). Việc cần môi trường đặc biệt (GUI, file IFC lớn, mạng bị chặn) thì ghi rõ yêu cầu đó trong task để agent có đủ điều kiện nhận.
- Người dùng cho mỗi agent biết tên của nó khi bắt đầu phiên. Không tự đặt hoặc đổi tên; không dùng lại số đã có agent khác.

## 2. Phối hợp
- Không có mailbox. Kết quả và ghi chú bàn giao đặt trong file ở thư mục được giao (mục 3), mô tả rõ trong commit message.
- Việc được giao qua `tasks/` (xem `tasks/README.md`): mỗi task ghi rõ ai làm (`assignees`); mọi agent có tên trong `assignees` được sửa file task đó (mục tiến độ: mỗi agent ghi phần của mình, nhật ký chỉ thêm dòng cuối).
- Agent **được sửa file của agent khác** (kể cả file của task khác) theo quy tắc "Quyền ghi" trong `CLAUDE.md`: pull --rebase ngay trước khi sửa, commit nêu rõ sửa của ai và vì sao, ghi một dòng vào nhật ký task liên quan. Sửa/bổ sung kết quả của một task thì ghi thẳng vào task đó (thêm tên mình vào `assignees`), không tạo task mới.
- Task chưa có `assignees` thì agent nào rảnh nhận trước ghi tên mình vào `assignees` (kèm commit + push ngay) rồi mới làm, tránh hai agent làm trùng.

## 3. Contract đầu vào – đầu ra giữa các agent

1. **Mọi yêu cầu phải tự đủ**: người nhận không phải đoán. Nêu rõ đường dẫn file đầu vào (tương đối từ gốc repo), lệnh/thao tác mong muốn, và đường dẫn đầu ra.
2. **Đầu ra đặt đúng chỗ** (người gửi chỉ định, mặc định như dưới):

| Loại | Thư mục |
|---|---|
| Ghi chú nghiên cứu | `research/NN-<chủ đề>/` (hoặc thư mục con theo hướng, xem `CLAUDE.md`) |
| Tài liệu tổng hợp | `docs/` |
| Cấu hình (dung sai, quy tắc phân loại) | `config/` |
| Code | `src/`, test ở `tests/` |
| File mẫu đầu vào | `samples/` |
| Kết quả chạy (IFC/JSON đầu ra, ảnh) | `out/` (git-ignore; chỉ commit file nhỏ có chủ đích, đặt vào `samples/` hoặc `docs/assets/`) |

3. **Tiêu chí hoàn thành kiểm chứng được** (ví dụ: file `out/x.ifc` mở được bằng IfcOpenShell, có `IfcSpace` suy ra cho mỗi vùng kín và ≥1 `IfcRelSpaceBoundary` cho mỗi `IfcSpace`, tổng diện tích boundary khớp bề mặt không gian trong dung sai 1e-3).
4. **Báo cáo kết quả (trong file đầu ra hoặc commit message)**: `DONE|PARTIAL|BLOCKED`, danh sách file đã tạo, lệnh đã chạy, kết quả kiểm tra, vấn đề còn mở.
5. **Không bịa**: kết quả chưa chạy thật thì ghi "chưa kiểm chứng". Các quy tắc độ tin cậy khác theo `CLAUDE.md`.
6. **Tách việc rõ ràng**: mỗi yêu cầu nêu thư mục đầu ra mặc định; khi cần sửa file của agent khác thì làm theo quy tắc "Quyền ghi" trong `CLAUDE.md`.

## 4. Quy trình git
- **Chỉ dùng một nhánh `main`**; không tạo nhánh riêng, không tạo pull request. Mọi agent push thẳng lên `main`.
- **Trước khi bắt đầu và trước mỗi lần push**: `git pull --rebase origin main`. Nếu push bị từ chối vì remote có commit mới, pull --rebase lại rồi push lại. Không dùng `--force`.
- **Commit + push ngay** sau khi hoàn thành việc, để agent khác thấy được. Commit nhỏ, thường xuyên.
- Các agent được sửa file của nhau, nên **luôn pull --rebase ngay trước khi sửa** và push ngay sau khi sửa. Nếu xung đột khi rebase: giữ cả hai phần, không ghi đè mất công việc của agent khác.
- Commit message nêu rõ agent và nhiệm vụ, ví dụ: `research(claude-02): add ifc spatial structure notes`.

## 5. Múi giờ
Mọi thời điểm trong repo (task, nhật ký, thông báo, báo cáo) ghi theo **giờ Việt Nam GMT+7 (Asia/Ho_Chi_Minh)**, dạng `YYYY-MM-DDTHH:MM:SS+07:00` hoặc `YYYY-MM-DD HH:MM GMT+7`. Lấy giờ bằng `TZ=Asia/Ho_Chi_Minh date`, không đoán.

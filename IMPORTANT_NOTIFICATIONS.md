# ⚠️ IMPORTANT_NOTIFICATIONS — THÔNG BÁO QUAN TRỌNG CHO MỌI AGENT

> Agent nào cũng phải đọc file này ngay sau Bước 0 trong `AGENTS.md`.
> File có 3 phần tách biệt: **PHẦN 1 – Cách ghi** · **PHẦN 2 – Mục lục** · **PHẦN 3 – Các thông báo** (mới nhất ở trên cùng).

---

# PHẦN 1 — CÁCH GHI THÔNG BÁO (BẮT BUỘC)

1. **Vị trí**: thêm thông báo mới vào **đầu PHẦN 3** (ngay dưới dòng `# PHẦN 3`) và thêm 1 dòng vào bảng PHẦN 2. Không sửa nội dung thông báo cũ. Chỉ được đổi dòng `Trạng thái` của thông báo cũ (ví dụ sang "Đã thay thế bởi N-003").
2. **Mã thông báo**: `N-001`, `N-002`, … tăng dần, không dùng lại. Mỗi thông báo có đúng **một** mã, và tiêu đề phải nói rõ việc gì (không đặt hai thông báo có tiêu đề gần giống nhau; thông tin cập nhật thì viết thông báo mới nêu "cập nhật N-xxx").
3. **Dòng tiêu đề**: `## N-<số> · [YYYY-MM-DD HH:MM GMT+7] · <biểu tượng mức độ> TIÊU ĐỀ VIẾT HOA`
4. **Giờ**: giờ Việt Nam. Lấy bằng `TZ=Asia/Ho_Chi_Minh date +"%Y-%m-%d %H:%M"` (máy cloud chạy giờ UTC; đừng đoán giờ).
5. **Mức độ**: 🔴 CAO (phải xử lý trước khi làm tiếp) · 🟡 TRUNG BÌNH (nên biết) · 🟢 THÔNG TIN (tham khảo).
6. **Thân thông báo** gồm đúng các mục sau, theo thứ tự:
   - Dòng thông tin: `Người gửi` · `Gửi lúc` · `Gửi cho` (`tất cả` / `claude-0x`) · `Mức độ` · `Trạng thái` (`Đang hiệu lực` / `Đã hết hiệu lực` / `Đã thay thế bởi N-xxx`)
   - `### ĐÃ XẢY RA GÌ` · `### ĐÃ XỬ LÝ GÌ` · `### YÊU CẦU ĐỐI VỚI TỪNG AGENT` · `### KHI NÀO HẾT HIỆU LỰC`
7. **Không ghi** email, mật khẩu, token hay thông tin cá nhân.
8. **Sau khi ghi**: `git pull --rebase origin main` → commit (message bắt đầu bằng `notify:`) → `git push origin main`.
9. **Khi đọc**: xử lý mọi thông báo 🔴 và 🟡 có `Trạng thái: Đang hiệu lực` trước khi làm task.

**Mẫu để sao chép** (chỉ là mẫu, KHÔNG phải thông báo thật; các giá trị trong `< >` phải thay):

```markdown
## N-<số> · [<YYYY-MM-DD HH:MM> GMT+7] · <🔴|🟡|🟢> <TIÊU ĐỀ VIẾT HOA>

- **Người gửi**: <claude-0x>
- **Gửi lúc**: <YYYY-MM-DD HH:MM> GMT+7
- **Gửi cho**: <tất cả|claude-0x>
- **Mức độ**: <🔴|🟡|🟢> <lý do ngắn>
- **Trạng thái**: Đang hiệu lực

### ĐÃ XẢY RA GÌ
### ĐÃ XỬ LÝ GÌ
### YÊU CẦU ĐỐI VỚI TỪNG AGENT
### KHI NÀO HẾT HIỆU LỰC
```

---

# PHẦN 2 — MỤC LỤC

| Mã | Giờ (GMT+7) | Mức | Gửi → nhận | Tiêu đề | Trạng thái |
|---|---|---|---|---|---|
| N-001 | 2026-11-10 16:46 | 🟡 | claude-01 → tất cả | ĐỔI QUY TẮC: CÁC AGENT ĐƯỢC SỬA FILE CỦA NHAU | Đang hiệu lực |

---


# PHẦN 3 — CÁC THÔNG BÁO (mới nhất ở trên cùng)

## N-001 · [2026-11-10 16:46 GMT+7] · 🟡 ĐỔI QUY TẮC: CÁC AGENT ĐƯỢC SỬA FILE CỦA NHAU

- **Người gửi**: claude-01
- **Gửi lúc**: 2026-11-10 16:46 GMT+7
- **Gửi cho**: tất cả
- **Mức độ**: 🟡 thay đổi quy tắc cộng tác, cần biết trước khi sửa file
- **Trạng thái**: Đang hiệu lực

### ĐÃ XẢY RA GÌ
Người dùng yêu cầu: các agent được sửa file của nhau; không tạo task mới chỉ để sửa/bổ sung kết quả của task đang có, mà ghi thẳng vào task đó.

### ĐÃ XỬ LÝ GÌ
- Sửa harness (commit `ad800a1`): `CLAUDE.md` (mục "Quyền ghi" thay cho "Phân quyền ghi"), `collab/CONTRACT.md`, `tasks/README.md` (định nghĩa lại `FIX`), `AGENTS.md`, `.claude/agents/*.md`.
- Áp dụng ngay (commit `e4ff9fc`): claude-01 sửa trực tiếp `research/03-space-and-boundary-algorithms/graph-topology/bim2sim-analysis.md`, `assessment.md`, `survey.md`, bổ sung mục 8 vào `ifc2sb-analysis.md` (TASK-002 của claude-02), thêm claude-01 vào `assignees` của TASK-002; xoá TASK-006 và `bim2sim-crosscheck.md` (đã gộp vào TASK-002).

### YÊU CẦU ĐỐI VỚI TỪNG AGENT
- **Tất cả**: đọc lại mục "Quyền ghi" trong `CLAUDE.md`. Trước khi sửa file bất kỳ: `git pull --rebase origin main`; commit nêu rõ sửa file của ai và vì sao; ghi một dòng vào nhật ký task liên quan; không xoá nội dung người khác nếu không thay bằng nội dung đúng hơn kèm nguồn.
- **claude-02**: đọc lại `bim2sim-analysis.md` (kết luận "chỉ đọc" đã sửa: bim2sim có sinh 2b; bộ lọc level bỏ mọi boundary `Name='1stLevel'`) và mục 8 của `ifc2sb-analysis.md` trước khi làm tiếp TASK-002.

### KHI NÀO HẾT HIỆU LỰC
Khi người dùng đổi lại quy tắc quyền ghi, hoặc khi mọi agent đã xác nhận đọc (đổi Trạng thái thành "Đã hết hiệu lực").

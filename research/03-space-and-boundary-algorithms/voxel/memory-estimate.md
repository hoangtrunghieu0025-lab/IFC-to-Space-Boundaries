# Ước tính bộ nhớ và thời gian cho công trình cỡ sân vận động

- **Câu hỏi nghiên cứu**: voxel hoá một công trình cỡ sân vận động 80.000 chỗ ở các độ phân giải 0,1 / 0,25 / 0,5 m tốn bao nhiêu bộ nhớ và thời gian, và giảm thế nào?
- **Kết luận ngắn**: lưới dày đặc kiểu mảng bool khả thi tới **0,25 m (khoảng 0,3 GB bool, 1,15 GB nếu giữ nhãn int32)**; ở **0,1 m cần 4,5 GB bool và 18 GB nhãn** nên bắt buộc dùng lưới thưa/octree hoặc chia khối. Đây là **ước tính từ công thức**, giả định kích thước, **không phải phép đo trên sân vận động**.
- **Độ tin cậy**: thấp cho kích thước (giả định); trung bình cho phép nhân số ô; thấp cho thời gian (ngoại suy tuyến tính từ một phép đo nhỏ).
- **Ngày thực hiện**: 2026-11-10 (claude-02)

## 1. Giả định
Hộp bao **300 × 250 × 60 m** (giả định của task, không lấy từ bản vẽ sân vận động nào; sân 80.000 chỗ thực tế có thể khác). Số ô: `N = (L/h)·(W/h)·(H/h)`.

## 2. Bộ nhớ lưới dày đặc
| h (m) | Số ô | Mảng bool (1 B/ô) | Bitset (1/8 B/ô) | Nhãn int32 (4 B/ô) |
|---|---|---|---|---|
| 0,5 | 36 triệu | 0,04 GB | ~0 GB | 0,14 GB |
| 0,25 | 288 triệu | 0,29 GB | 0,04 GB | 1,15 GB |
| 0,1 | 4,5 tỷ | **4,5 GB** | 0,56 GB | **18 GB** |
Máy làm việc hiện có 15 GB RAM. Chưa tính bộ nhớ cho điểm lấy mẫu và lưới tam giác (hàng chục triệu tam giác với sân vận động, chưa ước lượng được).

## 3. Thời gian
- Đo: `scipy.ndimage.label` trên lưới 2,37 triệu ô mất **0,02 s** (≈ 8 ns/ô); BFS Python thuần **1,47 s** (≈ 0,6 µs/ô).
- Ngoại suy tuyến tính **chỉ cho khâu gán nhãn** bằng scipy: 0,5 m → 0,3 s; 0,25 m → 2,4 s; 0,1 m → 38 s.
- Khâu **voxel hoá bề mặt** (lấy mẫu tam giác) mới là chi phí chính trong prototype (vài giây cho nhà 21 `IfcSpace`) và tăng theo (diện tích bề mặt / h²); không ngoại suy được từ nhà nhỏ.

## 4. Cách giảm (đề xuất, một phần có trong nguồn)
- Lưu thưa theo phân cấp (octree): toolkit của Krijnen có "hierarchical storage" (bài báo nhắc).
- Chia theo tầng hoặc khối rồi ghép (chưa có nguồn xác nhận).
- Dùng độ phân giải thô để định vị space, rồi tinh chỉnh bằng hình học gốc (hướng B-rep) ở bước sau.
- Bitset hoặc mảng nén thay cho mảng bool.

## 5. Điều kiện khả thi
Với độ chính xác diện tích 1e−3 (xem `voxel-method-analysis.md`, mục 4), voxel không đủ bất kể h; nên dùng voxel cho **định vị/gán nhãn**, không cho số đo.

## Chưa xác minh / việc còn lại
- Chưa chạy trên mô hình lớn (tầng M, L trong `samples/manifest.yaml` chưa được tải về máy).
- Kích thước hộp bao giả định; chưa có số phần tử/tam giác của sân vận động.

## Nguồn
Phép đo trong phiên này (`prototype/README.md`); khái niệm lưu trữ phân cấp theo Krijnen et al. 2021 mục 3.2.1.

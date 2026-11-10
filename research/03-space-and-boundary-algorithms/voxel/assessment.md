# Đánh giá hướng voxel

- **Câu hỏi nghiên cứu**: voxel có đáng làm cho việc suy ra `IfcSpace` và sinh `IfcRelSpaceBoundary` không?
- **Kết luận ngắn**: **Chỉ tham khảo/hỗ trợ**, không phải hướng chính để sinh boundary. Voxel **định vị tốt** không gian kín trên IFC sạch (prototype: **47/63** khớp IoU ≥ 0,5 ở h = 0,1 m) và chịu được khe nhỏ, nhưng **không đạt dung sai diện tích** (sai số tối thiểu cỡ một ô mỗi mặt), cần lưới thưa để chạy ở quy mô sân vận động, và không sinh được boundary mức 2/`CorrespondingBoundary` theo tài liệu đã đọc. Dùng làm bước **định vị space thô** hoặc **kiểm tra chéo** kết quả của hướng B-rep/Graph. Mức bằng chứng: **trung bình**.
- **Độ tin cậy**: trung bình.
- **Ngày thực hiện**: 2026-11-10 (claude-02)

## Trả lời hai câu hỏi đặc thù của task
1. **Voxel suy ra được `IfcSpace` hay chỉ cho thermal interface?** Bài báo (Krijnen 2021) mới làm **thermal interface từ `IfcSpace` có sẵn**; suy ra space là việc tương lai. Prototype của mình chứng tỏ suy ra được vùng không gian kín từ phần tử bao ở mức định vị (47/63), nhưng đó là kết quả sơ bộ trên 6 file nhỏ.
2. **Độ phân giải tối đa để đạt dung sai 1e−3?** **Không có độ phân giải nào đạt** với voxel hoá bề mặt: sai số tối thiểu cỡ một ô trên mỗi mặt, h = 0,1 m trên phòng 4 m rộng ≈ 5 % diện tích (ước lượng thô). Muốn 1e−3 phải tinh chỉnh bằng hình học gốc sau khi định vị.

## Bảng tiêu chí chung
| Tiêu chí | Đánh giá (kèm bằng chứng) |
|---|---|
| Sinh được `IfcSpace`? | **Một phần**: tìm được khoang kín (prototype); chưa cài bước chuyển về mặt/khối đẹp. Bài báo: cần `IfcSpace` có sẵn |
| Sinh được `IfcRelSpaceBoundary` 1st/2nd? | **Mức 1: có** (Krijnen: so nhãn voxel kề nhau, mỗi tam giác gắn hai space). **Mức 2, `CorrespondingBoundary`, internal/external, virtual: bài không nêu** |
| Yêu cầu hình học đầu vào | **Thấp**: không cần solid kín/pháp tuyến đúng (voxel luôn hợp lệ về topo, theo bài). Nhưng cần khoang **kín** về mặt voxel: công trình không khép kín (bsi-ifc4) cho 0 vùng |
| Hình cong / mái dốc / khán đài bậc thang | Xử lý được tổng quát (không giả định dạng hình học), tốn độ phân giải; mô hình xoay chéo tăng diện tích bề mặt tới √2 ở 45° (Krijnen) |
| Quy mô | Đo: nhà tối đa 2,3 triệu ô. Ước tính sân vận động: xem `memory-estimate.md` (0,25 m: 288 triệu ô; 0,1 m: 4,5 tỷ ô). **Chưa đo** |
| Hiệu năng / bộ nhớ | Đo nhỏ: ≤ 3 s mỗi file; ngoại suy chỉ cho khâu gán nhãn; xem `memory-estimate.md` |
| Độ phức tạp cài đặt, thư viện, license | **Thấp**: prototype ~200 dòng Python (IfcOpenShell + numpy, scipy tuỳ chọn). Toolkit sẵn có (MIT): `opensourceBIM/voxelization_toolkit`, chưa kiểm chứng chức năng |
| Độ trưởng thành | Voxel cho IFC → thermal: có bài báo, 1 trường học. Voxel suy ra space từ IFC: **chưa có** bài/công cụ; có nhánh scan-to-BIM (VOX2BIM+) |
| Rủi ro chính | (1) Sai số kích thước cỡ một ô, không đạt dung sai; (2) rò rỉ giữa space khi có khe/cửa mở; (3) bộ nhớ ở độ phân giải mịn; (4) không có đường rõ ràng tới boundary mức 2 |
| **Kết luận** | **Chỉ tham khảo/hỗ trợ.** Mức bằng chứng: **trung bình**. Để nâng lên "cao": thử trên mô hình M/L, đo thời gian/RAM thật, thử `--close` và vách ảo, chạy toolkit chính thức |

## Số liệu tham chiếu để so sánh với các hướng khác (cùng 6 file, 63 `IfcSpace`)
| Hướng | Khớp |
|---|---|
| Lát cắt mặt bằng (TASK-005, IoU diện tích tại z = 1 m) | 38/63 (60 %) |
| Voxel h = 0,1 m (IoU thể tích) | 47/63 (75 %) |
| Voxel h = 0,2 m | 45/63 (71 %) |
**Không so sánh trực tiếp được**: hai phép đo dùng IoU khác nhau (2D tại một cao độ so với 3D toàn thể tích) và voxel có thể bị ảnh hưởng bởi thiên lệch lưới. Chỉ để tham khảo.

## Chưa xác minh / việc còn lại
- Chạy `voxelization_toolkit` (clone thất bại lần đầu; chưa thử lại), đọc toàn văn VOX2BIM+ (trang tạp chí chuyển hướng sang đăng nhập; không đi tiếp).
- Thử mô hình M/L khi có; thử `--close`; đối chiếu IoU khi hiệu chỉnh thiên lệch lưới.

## Nguồn
Xem `survey.md`, `voxel-method-analysis.md`, `memory-estimate.md`, `prototype/README.md`.

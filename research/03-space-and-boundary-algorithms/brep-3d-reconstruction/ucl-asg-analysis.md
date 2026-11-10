# Phân tích thuật toán Automatic Space Generation (ASG) của UCL

- **Câu hỏi nghiên cứu**: ASG dựng thể tích `IfcSpace` từ B-rep của phần tử bao như thế nào, cần đầu vào sạch đến mức nào, và các tiêu chí lỗi hình học họ đề ra là gì?
- **Kết luận ngắn**:
  - ASG suy ra `IfcSpace` bằng cách **trừ các mặt tiếp xúc giữa từng cặp phần tử** khỏi B-rep của mỗi phần tử, rồi **gom các mặt còn lại thành vỏ (shell) theo cạnh chung** và phân vỏ trong/ngoài bằng thể tích có dấu. Không dùng Boolean 3D tổng quát, không cần `IfcSpace` gốc.
  - Chất lượng đầu vào quyết định kết quả: mặt thiếu, pháp tuyến ngược, va chạm (clash) giữa phần tử đều làm vỏ hở hoặc hai space dính nhau.
  - Bằng chứng thử nghiệm mỏng: 2 toà nhà thật, **không có số liệu thời gian hay bộ nhớ**; chưa thấy mã nguồn công khai.
- **Độ tin cậy**: cao cho mô tả thuật toán (đã đọc toàn văn); thấp cho hiệu năng và khả năng mở rộng (không có số liệu).
- **Ngày thực hiện**: 2026-11-10 (claude-02)

## 1. Nguồn và ngữ cảnh
Lilis, Katsigarakis, Rovas (UCL IEDE), *Automatic IFC data enrichment with space geometries for Building Energy Performance Simulations*, IBPSA BS2021, tr. 2134–2140. [S1]
- Nằm trong quy trình làm giàu IFC: nếu IFC **chưa có space** hoặc space lỗi → chạy ASG; sau đó mới sinh boundary mức 2. ASG chỉ sinh **space mức 1** (thể tích không khí), chưa gom thành vùng nhiệt (zone).
- Loại phần tử bao được dùng: tường, sàn, dầm, cột… Lan can, cầu thang bị **bỏ qua** vì ảnh hưởng nhỏ lên cân bằng nhiệt (theo bài).

## 2. Thuật toán 4 giai đoạn
| Giai đoạn | Việc | Chi tiết |
|---|---|---|
| 1. Tạo B-rep | Mọi biểu diễn solid (extrusion, manifold, revolved, faceted B-rep…) chuyển sang **faceted B-rep** | Phần tử cong phải quy về mặt phẳng; bài nhắc đến thuật toán facet tường cong của Ying & Lee 2019 |
| 2. Trích mặt biên chung và mặt trong | Với mọi **cặp** B-rep (tường–tường, tường–sàn…) tìm các đa giác chung `CB_ij = Fcod(∂B_i, ∂B_j)` (đồng phẳng, ngược pháp tuyến); nếu hai phần tử va chạm (clash), các mặt của `i` nằm trong `j` gom vào tập mặt trong `IS_ij` | Công thức (1), (2) trong bài |
| 3. Dựng vỏ và phân loại | Với mỗi B-rep `i`: `R_i` = các đa giác còn lại sau khi trừ `CB_ij ∪ IS_ij` (phép trừ đa giác đồng phẳng, làm bằng 2D polygon clipping); gộp mọi `R_i` thành `R`, tách thành các **vỏ** (mỗi đa giác có ít nhất một cạnh chung với đa giác khác trong vỏ, mỗi đoạn cạnh thuộc tối đa 2 đa giác); phân loại **trong/ngoài** bằng thể tích có dấu `V = (1/3) Σ <n̂_k, r_k> A_k` (âm: pháp tuyến hướng vào, vỏ trong; dương: vỏ ngoài) | Algorithm 1 (`Fce`: hai khung dây có chung cạnh không, kiểm giao đoạn thẳng trong 3D), Algorithm 2 (`Fsg`: gom đa giác thành vỏ) |
| 4. Làm giàu IFC | Ghi `IfcSpace` với biểu diễn `IfcFacetedBrep` từ các vỏ trong; nếu có `IfcBuildingStorey` thì dịch về hệ toạ độ tầng, không thì hệ toạ độ toà nhà | Dùng thư viện IFC tự viết bằng **Java** để đọc/ghi IFC2x3, IFC4… |

Phụ thuộc phần mềm: thư viện IFC bằng Java (tự phát triển), thư viện hình học **C++** dựa trên **Clipper** (Vatti) cho phép toán 2D (hợp/giao/hiệu đa giác). **Không** dùng IfcOpenShell hay OpenCASCADE. [S1]

**Nhận xét của người viết (suy luận từ mô tả, không từ bài):** giai đoạn 3 *gom đa giác theo cạnh chung thành vỏ* cùng bản chất với việc tìm **thành phần liên thông trên đồ thị kề mặt** của IFC2SB (xem `../graph-topology/ifc2sb-analysis.md`). Khác biệt: ASG **trừ trước** các mặt tiếp xúc cặp-đôi rồi mới gom; IFC2SB **fuse toàn bộ mặt** rồi tỉa. Hai hướng "Graph" và "B-rep" trùng nhau ở bước này; khi so sánh cần tránh đếm hai lần.

## 3. Yêu cầu đầu vào và tiêu chí lỗi hình học (để dùng ở TASK-001 và pipeline)
Bài đề ra 3 loại lỗi cần kiểm **trước** khi chạy, gồm cả khi IFC đã có space: [S1]
| Loại lỗi | Định nghĩa trong bài | Hệ quả khi bỏ qua |
|---|---|---|
| **Surface error** | Mặt **thiếu hoặc ngược** trong B-rep của phần tử và space | Vỏ hở (không gom đủ), hoặc vỏ trong bị coi là vỏ ngoài vì thể tích dương |
| **Clash error** | Các solid của phần tử (và space) **giao nhau** | Mặt trong của chỗ va chạm bị coi là mặt space → hai space kề nhau dính thành một (ví dụ cột cắt hai tường ở Torre Turina) |
| **Space error** | Phần mặt biên của space **không gắn với phần tử bao nào** | Khe hở giữa space và tường |

Biện pháp trong thuật toán: gộp `IS_ij` (mặt trong do clash) vào tập loại trừ để tránh lỗi clash (hình 8 của bài). Không có biện pháp cho mặt thiếu hoặc ngược pháp tuyến: người dùng phải sửa.

**Chỉ số chất lượng đầu ra, LIS (Length of Isolated Segments):** tổng độ dài các đoạn biên chỉ thuộc **một** đa giác của vỏ. Vỏ kín hoàn toàn thì LIS = 0; LIS càng lớn thì dựng càng tệ (do mặt thiếu hoặc mặt cắt nhau). Mô hình tốt đạt LIS **dưới 2e−4**. Chỉ số này có thể dùng làm tiêu chí kiểm tra kín của `IfcSpace` suy ra trong dự án. [S1]

## 4. Thử nghiệm trong bài
| Mô hình | Kết quả | Ghi chú |
|---|---|---|
| Toà nhà ký túc xá, Đại học Kỹ thuật Crete (hoàn thành 2020, 3 tầng) | 48 vỏ trong dựng thành công, LIS < 2e−4 trừ một vỏ (lệch tường–sàn); có vài "space" nhỏ không dùng được (đỉnh hai giếng thang) cần hậu xử lý | Bài mô tả "3 tầng, mỗi tầng 6 space" nhưng kết quả 48 vỏ và tham chiếu hình không khớp nhau (số hình bị lệch); **chưa rõ vì sao 48** |
| Torre Turina, Valladolid, 11 tầng | Phần lớn space đúng; clash cột–tường gây space dính nhau khi **không** bật `IS_ij`; khi bật thì đúng. Một số vỏ vẫn sai do lỗi bề mặt | Mô hình có nhiều clash do thiết kế |

**Không có**: thời gian chạy, bộ nhớ, số phần tử, số mặt; so sánh với `IfcSpace` gốc; thử trên công trình lớn hay hình cong thật.

## 5. Giới hạn do chính bài nêu
- Kết quả bị ảnh hưởng bởi lỗi hình học của IFC (clash làm mất mặt biên chung; pháp tuyến ngược làm vỏ không phân loại được là vỏ trong; mặt thiếu làm vỏ hở).
- Sinh ra các space nhỏ không dùng được (đỉnh giếng thang): **cần hậu xử lý** (xoá, đặt tên) sẽ báo cáo trong bài sau.
- Tính toán song song (`p_thread`) là việc tương lai; hiện chưa tối ưu hiệu năng.
- Lan can, cầu thang bị bỏ qua.

## 6. Ý nghĩa với dự án (đề xuất của người viết)
- **Dùng được làm mẫu thuật toán suy ra `IfcSpace`** khi IFC thiếu space: ý tưởng "trừ mặt tiếp xúc rồi gom vỏ" đơn giản, chỉ cần phép toán 2D trên đa giác đồng phẳng (không cần Boolean 3D), có thể cài bằng Shapely/Clipper hoặc pythonocc.
- **Điểm yếu cho sân vận động (suy luận):**
  - Bài thử **mọi cặp** B-rep ("All possible B-rep pair combinations… are tested"): nếu không có lọc theo hộp bao thì tăng theo bình phương số phần tử; cần R-tree hoặc chia theo khối (chưa có nguồn xác nhận).
  - Khán đài mở trời không có vỏ trong kín: nó sẽ ra "vỏ hở" (LIS lớn) hoặc nhập vào vỏ ngoài.
  - Phần tử cong phải facet trước (Ying & Lee 2019 — chưa đọc), nên số mặt tăng.
- Tiêu chí lỗi và LIS ở mục 3 nên đưa vào `dataset-quality-criteria.md` (TASK-001) như tiêu chí "hình học đầu vào" và vào bộ kiểm chứng đầu ra.

## Chưa xác minh / việc còn lại
- Chưa tìm thấy mã nguồn hay công cụ công khai của ASG.
- Bản "bs2021_30888" là bản IBPSA: tham chiếu hình/số liệu trong bài có chỗ không khớp (ví dụ Figure 3/7 cho toà nhà Crete); chưa kiểm tra bản khác.
- Chưa đọc: Lilis et al. 2015 (phát hiện và sửa lỗi hình học IFC), Ying & Lee 2019 (facet tường cong), Lilis et al. 2018 (kiểm tra IFC cho BEPS).

## Nguồn
- [S1] Lilis, Katsigarakis, Rovas (2021), IBPSA BS2021, bs2021_30888: https://discovery.ucl.ac.uk/id/eprint/10169911/1/bs2021_30888.pdf — đã đọc toàn văn (2026-11-10)

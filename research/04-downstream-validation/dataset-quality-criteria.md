# Tiêu chí chất lượng bộ IFC dùng để test (TASK-001)

- **Câu hỏi nghiên cứu**: Một file IFC cần thỏa gì để dùng làm dữ liệu test cho pipeline suy ra `IfcSpace` và sinh `IfcRelSpaceBoundary`, và đo các tiêu chí đó thế nào cho lặp lại được?
- **Kết luận ngắn**: Mỗi file qua 3 **cổng bắt buộc** (mở được, có phần tử bao với hình học tạo được, nguồn/giấy phép ghi nhận được). Sau đó chấm **0–100 điểm** theo 6 nhóm: ground truth 35, hình học 20, đa dạng 20, pháp lý 15, loại công trình 10 (cộng thêm), và xếp **tầng S/M/L** theo dung lượng và số `IfcSpace`. Phần đo tự động nằm trong `samples/inspect_ifc.py`; hai nhóm pháp lý và loại công trình nhập tay vào `samples/manifest.yaml`.
- **Độ tin cậy**: trung bình. Cấu trúc lớp IFC đã kiểm bằng schema EXPRESS trong IfcOpenShell 0.9.0. Các ngưỡng là **đề xuất của claude-01** dựa trên `PRIMARY_OBJECTIVE.md` mục 3 và yêu cầu trong TASK-001, chưa có nguồn chuẩn ngành; sẽ chốt lại khi viết spec.

## Chi tiết

### 1. Cổng bắt buộc (không qua thì loại, không chấm điểm)

| Mã | Tiêu chí | Ngưỡng | Cách kiểm tra |
|---|---|---|---|
| G1 | Mở được bằng IfcOpenShell | `ifcopenshell.open()` không ném lỗi | `inspect_ifc.py` (trường `error` không có) |
| G2 | Có phần tử bao có hình học | ≥1 `IfcWall` hoặc `IfcSlab` có `Representation`, và `geom_ok_ratio_elements` ≥ 0,90 | `inspect_ifc.py` (lấy mẫu ngẫu nhiên ≤200 phần tử gọi `ifcopenshell.geom.create_shape`) |
| G3 | Nguồn gốc xác định được | Có URL nguồn đã mở kiểm tra thật và ngày truy cập. Giấy phép **chưa rõ vẫn qua cổng** nhưng file chỉ để ở `samples/corpus_real/`, không commit | Thủ công, ghi vào manifest (`license`, `license_class`) |

### 2. Tầng quy mô

| Tầng | Điều kiện (tự động, `tier_of()`) | Dùng để | Lưu ở đâu |
|---|---|---|---|
| `S` | ≤5 MB **và** ≤50 `IfcSpace` | Test tự động mỗi lần sửa code (vài giây) | `samples/small/`. Commit nếu giấy phép cho phép tái phân phối |
| `M` | Nằm giữa S và L | Test độ đúng trung bình, chạy thủ công | `samples/large/` (không commit) |
| `L` | ≥20 MB **hoặc** ≥200 `IfcSpace` | Test độ đúng ở quy mô thật + hiệu năng. Bắt buộc ghi `open_s`, `peak_rss_mb`; phải mở được trên máy 16 GB RAM (`peak_rss_mb` < 12 000) | `samples/large/` (không commit) |

Lý do thêm tầng `M` (task chỉ nêu S/L): có những file quá lớn để chạy mỗi lần sửa code, nhưng chưa đủ "quy mô thật". Gộp chúng vào S làm test chậm, còn gộp vào L làm sai lệch số đo hiệu năng.

### 3. Thang điểm (100 + 10 điểm cộng)

| Nhóm | Mã điểm (trong `score_auto`) | Điểm | Ngưỡng / công thức | Cấp |
|---|---|---|---|---|
| Ground truth | `gt_space_geom` | 15 | 15 × (tỉ lệ `IfcSpace` có `Representation`) | Nên có (≥3 file S phải > 0) |
| | `gt_space_storey` | 5 | ≥95 % `IfcSpace` nằm dưới một `IfcBuildingStorey` qua `IfcRelAggregates` | Nên có |
| | `gt_rsb` | 10 | Có ≥1 `IfcRelSpaceBoundary` | Nên có |
| | `gt_rsb_2nd` | 5 | Có `IfcRelSpaceBoundary2ndLevel` (IFC4), hoặc `Name` bắt đầu bằng "2nd" (quy ước IFC2x3, *chưa xác minh*) | Điểm cộng ground truth |
| Hình học | `geometry` | 20 | 20 × clamp((r − 0,90)/0,08), với r = `geom_ok_ratio_elements`; r ≥ 0,98 được đủ điểm | Bắt buộc ≥0,90 (G2) |
| Đa dạng | `div_storeys` | 5 | ≥2 `IfcBuildingStorey` | Nên có (cả tập phải có ≥1 file) |
| | `div_openings` | 5 | Có `IfcDoor`/`IfcWindow` **và** `IfcOpeningElement` (5đ); chỉ có cửa mà không có opening (2đ) | Nên có |
| | `div_roof` | 3 | Có `IfcRoof` | Nên có |
| | `div_other` | 2 | Có `IfcColumn`, `IfcCovering` hoặc `IfcStair` | Tham khảo |
| | `div_space_count` | 5 | ≥10 `IfcSpace` (5đ); 3–9 (2đ) | Nên có |
| Pháp lý | `legal` | 15 | `redistributable` (giấy phép mở cho tái phân phối, ví dụ CC-BY, CC0, MIT…) = 15; `use_only` (dùng được nhưng không rõ quyền tái phân phối) = 8; `unknown` = 0 | Nhập tay |
| Loại công trình | `building_type` | +10 | `stadium` 10 · `large_public` (mall, bệnh viện, sân bay, nhà ga, hội trường) 8 · `office`/trường học 5 · `residential` 3 | Nhập tay; điểm cộng theo ưu tiên của người dùng |

`inspect_ifc.py` tính các mục tự động. Điểm cuối trong manifest = tự động + `legal` + `building_type`.

### 4. Các tiêu chí ghi nhận nhưng không chấm điểm tự động

| Tiêu chí | Cách ghi nhận | Lý do không chấm tự động |
|---|---|---|
| Tường chéo/cong, không gian không phải hộp, mái dốc, phòng thông nhau/shaft | Ghi chú tay trong manifest (`notes`) sau khi mở bằng viewer | Cần phân tích hình học; sẽ làm khi có pipeline |
| Lỗi non-manifold, self-intersection | Lỗi thì thể hiện qua `geom_ok_ratio_*`; kiểm sâu hơn ở TASK hình học sau | Kiểm tra đầy đủ tốn thời gian và cần thư viện bổ sung |
| Đơn vị, placement hợp lý | `length_unit` trong kết quả đo; kiểm placement bằng mắt trên viewer | Không có ngưỡng chung |
| Có cả IFC2x3 và IFC4 trong tập | Đếm theo `schema` trong manifest | Là tiêu chí của **cả tập**, không phải của từng file |

### 5. Tiêu chí cho cả tập (acceptance của TASK-001)
- Tầng L: ≥1–2 file công trình lớn/phức hợp (ưu tiên sân vận động), có `open_s`, `peak_rss_mb`, `n_products`, `n_spaces`.
- Tầng S: ≥5 file, có ≥1 IFC2X3 và ≥1 IFC4, ≥3 file có `n_spaces_with_rep` > 0.
- Có ≥1 file có `n_storeys` ≥ 2.
- Có ít nhất một file với `n_rsb` > 0 để đo boundary so với ground truth. Đây là bổ sung của claude-01: thiếu nó thì không đo được tiêu chí boundary ở `PRIMARY_OBJECTIVE.md` mục 3.

### 6. Cách đo (lệnh)
```bash
pip install ifcopenshell pyyaml
python3 samples/inspect_ifc.py --isolate samples/small/*.ifc   # JSON Lines, mỗi file một dòng
```
Trường RAM `peak_rss_mb` lấy từ `resource.getrusage(RUSAGE_SELF).ru_maxrss` của tiến trình đo. Muốn số RAM của từng file đúng thì chạy với `--isolate`; nếu không, RAM cộng dồn khi đo nhiều file trong cùng tiến trình.

## Liên quan đến pipeline IFC → Space Boundaries
- File có `IfcSpace` kèm hình học dùng để đo IoU diện tích (tiêu chí 3.2 trong `PRIMARY_OBJECTIVE.md`).
- File có `IfcRelSpaceBoundary` dùng để so boundary sinh ra với boundary gốc (diện tích, cặp `CorrespondingBoundary`).
- IFC2x3 không có lớp `IfcRelSpaceBoundary1stLevel`/`2ndLevel`; level của boundary phải suy ra từ quy ước khác (`Name`/`Description`), *chưa xác minh*. Vì vậy reader của pipeline cần xử lý riêng theo schema.

## Nguồn
- IfcOpenShell 0.9.0.post1 (PyPI `ifcopenshell`), schema EXPRESS nhúng sẵn. Kiểm bằng `ifcopenshell.ifcopenshell_wrapper.schema_by_name('IFC2X3'|'IFC4').declaration_by_name(...)`. Kết quả: IFC2X3 không có `IfcRelSpaceBoundary1stLevel`/`2ndLevel`; IFC4 có, với `ParentBoundary` (1stLevel) và thêm `CorrespondingBoundary` (2ndLevel) — chạy 2026-11-10. https://pypi.org/project/ifcopenshell/ — truy cập 2026-11-10
- Tài liệu buildingSMART (https://standards.buildingsmart.org/) bị Cloudflare chặn khi truy cập từ container (HTTP 403, 2026-11-10), nên chưa trích trực tiếp được.

## Câu hỏi còn mở
- Ngưỡng tầng (5 MB/50 phòng, 20 MB/200 phòng) và ngưỡng hình học (0,90/0,98) cần chốt cùng người dùng trong spec.
- Quy ước đánh dấu level boundary trong IFC2x3 (CV2.0 Space Boundary Add-on) cần agent `ifc-spatial-researcher` xác minh.

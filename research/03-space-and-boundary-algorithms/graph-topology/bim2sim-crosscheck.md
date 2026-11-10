# Đối chiếu bài Fichter 2021 với phần bim2sim của TASK-002 (TASK-006)

- **Câu hỏi nghiên cứu**: Các kết luận về bim2sim trong `bim2sim-analysis.md` (claude-02, TASK-002) có khớp với bài Fichter et al. 2021, các bài liên quan, và mã nguồn không? Có gì bị bỏ sót?
- **Kết luận ngắn**:
  - Ba kết luận chính của claude-02 **đúng**:
    - bim2sim không tự sinh boundary 1st level hay 2a từ phần tử bao;
    - mã space boundary của bim2sim không dùng graph;
    - bim2sim là bên tiêu thụ boundary.
  - Nhưng có **3 điểm cần chỉnh** và **5 phát hiện bị bỏ sót**. Quan trọng nhất:
    1. **"Chỉ đọc" là nói quá.** bim2sim có **sinh hình học boundary 2b** để lấp khe. Việc này dùng hình của `IfcSpace` có sẵn, và trong plugin EnergyPlus nó **bật mặc định**.
    2. **Bộ lọc level của bim2sim rất thô.** Hàm `instantiate_space_boundaries` chỉ loại boundary là lớp `IfcRelSpaceBoundary1stLevel` hoặc có `Name == '1stLevel'`; **mọi boundary khác đều bị coi là 2nd level**. Chạy thử trên bộ IFC của TASK-001: **5/14 file có boundary bị bỏ sạch** (Duplex, Clinic, Office A, TalTech, BIM-Edit).
    3. **IFC2SB và bim2sim cùng một dự án** (BIM2SIM, BMWi 03ET1562A). IFC2SB là công cụ được thiết kế để **cung cấp boundary cho bim2sim**, không chỉ là "một nguồn có thể có". Bằng chứng: phần BEPS của bài Fichter 2021 chạy qua toolchain BIM2SIM, và bộ test của bim2sim dùng file do IFC2SB sinh.
  - Thêm một phát hiện ảnh hưởng tới ground truth của TASK-001: theo Richter et al. 2022, chính file **AC20-FZK-Haus** (đang có trong `samples/small/`) có **62/81 pháp tuyến boundary quay sai hướng** và **4 space không kín**.
- **Độ tin cậy**: cao. Đã đọc toàn văn 2 bài, đọc mã kèm lịch sử commit, và chạy thử bộ lọc level trên 14 file IFC. **Chưa chạy bim2sim end-to-end** (cần pythonocc-core qua conda): chưa kiểm chứng.
- **Ngày thực hiện**: 2026-11-10 (claude-01)

## 1. Nguồn đã đọc

| Mã | Nguồn | Cách đọc |
|---|---|---|
| [F21] | Fichter, Richter, Frisch, van Treeck (2021). *Automatic generation of second level space boundary geometry from IFC models*. Proc. 17th IBPSA Conf., Bruges, tr. 1083–1090. https://publications.ibpsa.org/proceedings/bs/2021/papers/bs2021_30156.pdf (DOI 10.26868/25222708.2021.30156) | Tải PDF, `pdftotext`, đọc toàn văn |
| [R22] | Richter, Malhotra, Fichter, Hochberger, Frisch, van Treeck (2022). *Validation of IFC-based Geometric Input for Building Energy Performance Simulation*. SimBuild 2022, tr. 287–294. https://publications.ibpsa.org/proceedings/simbuild/2022/papers/simbuild2022_C033.pdf | Tải PDF (tìm trên trang mục lục SimBuild 2022 của IBPSA), đọc toàn văn. Bản quyền ASHRAE "for personal use only" nên **không lưu PDF vào repo** |
| [B] | bim2sim https://github.com/BIM2SIM/bim2sim, clone đầy đủ, HEAD `270cd0a36f` (2026-04-14), 5.987 commit | Đọc mã, `git log -S`, `git log --grep` |
| [I] | IFC2SB https://github.com/RWTH-E3D/IFC2SB, HEAD `96a89cd` (2023-01-24) | Đọc `src/Graph.cpp`, `src/Kernel.cpp` |
| [D498] | bim2sim Discussion #498 https://github.com/BIM2SIM/bim2sim/discussions/498 | Đã mở (WebFetch). claude-02 mới chỉ thấy qua tìm kiếm |
| — | Richter et al. 2021, Forum Bauinformatik (https://tuprints.ulb.tu-darmstadt.de/21521/). Đây là bài về thuật toán sửa boundary (`sb_correction`) của bim2sim | **Chưa đọc**: host `tuprints.ulb.tu-darmstadt.de` và `doi.org` chưa được mở mạng |

## 2. Đối chiếu từng khẳng định của `bim2sim-analysis.md`

| # | Khẳng định của claude-02 | Kết luận | Bằng chứng |
|---|---|---|---|
| 1 | bim2sim **chỉ đọc** `IfcRelSpaceBoundary` rồi sửa và bù khe; **không sinh** boundary từ phần tử bao | **Đúng một phần, cần chỉnh chữ "chỉ đọc"** | (a) Không sinh boundary 1st level hay 2a: đúng. [F21] viết về toolchain BIM2SIM rằng việc có sẵn SB là thiết yếu vì hình học SB được dùng làm đầu vào cho mô hình năng lượng (mục *Challenges using IFC data*). [R22] xếp việc "làm mới SB" là hướng của các thuật toán khác (van Treeck & Rank, Rose & Bazjanac, Lilis, Fichter), còn hướng của nhóm bim2sim là kiểm tra và sửa. (b) Nhưng bim2sim **có sinh hình học mới**: `sb_2b_generation.py:71-125` lấy hình `IfcSpace` (`bps_elements.py:234-245`), trừ dần các boundary (`BRepAlgoAPI_Cut`, dòng 118), mỗi mặt còn lại thành một `SpaceBoundary2B`. Docstring dòng 79 tự nhận là gán 2b "for simplicity", chưa xác minh lại loại 2a/2b |
| 2 | Không có graph trong mã space boundary; `networkx` chỉ ở HVAC | **Đúng** | `grep networkx` chỉ ra `elements/graphs/hvac_graph.py`, `elements/aggregation/hvac_aggregations.py`, `tasks/hvac/connect_elements.py` [B]. Graph của chuỗi IFC2SB→bim2sim nằm hoàn toàn trong IFC2SB [I][F21] |
| 3 | bim2sim là bên tiêu thụ IFC có boundary (do IFC2SB hoặc phần mềm CAD sinh); README trích Fichter 2021 và Richter 2021 | **Đúng, nhưng thiếu mối quan hệ chặt** | IFC2SB **thuộc cùng dự án BIM2SIM**: lời cảm ơn trong [F21] ghi dự án "BIM2SIM", mã 03ET1562A. Phần ứng dụng BEPS của [F21] dựng IDF bằng chính toolchain BIM2SIM (IfcOpenShell + GeomEppy). Bộ test bim2sim dùng file do IFC2SB sinh: docstring `PluginEnergyPlus/test/integration/test_energyplus.py:66` nhắc "Eric Fichter's Space Boundary Generation tool"; `PluginIFCCheck/test/integration/test_ifccheck.py:38` dùng `AC20-FZK-Haus_with_SB55.ifc`; `PluginOpenFOAM/test/integration/test_openfoam.py:177` nhắc "IFC2SB Version". Commit `0b2fd437e` (2021-04-09) thêm test "KIT-EDC_with_SB.ifc… with generated Space Boundaries" |
| 4 | `CreateSpaceBoundaries` lọc bằng `TypeFilter(('IfcRelSpaceBoundary',))` và dựng `SpaceBoundary` | **Đúng, nhưng bỏ sót bộ lọc level** | `sb_creation.py:56` đúng như claude-02 ghi. **Bỏ sót** `sb_creation.py:393-395`: bỏ qua boundary nếu `entity.is_a() == 'IfcRelSpaceBoundary1stLevel'` hoặc `entity.Name == '1stLevel'`; mọi boundary khác đi tiếp như 2nd level. Xem mục 3 |
| 5 | `AddSpaceBoundaries2B` bù khe khi chênh diện tích ≥ 1e-2 và cần `IfcSpace` có sẵn | **Đúng, bổ sung chi tiết** | `sb_2b_generation.py:101` (`< 1e-2` thì bỏ qua); chỉ cắt boundary nằm sát hình space (khoảng cách `> 1e-6` thì bỏ, dòng 115); lỗi bất kỳ thì chỉ ghi warning và không thêm 2b (dòng 63). Ngưỡng 1e-2 là **tuyệt đối** (đơn vị diện tích theo pint), không phải tương đối: chưa kiểm chứng đơn vị cụ thể |
| 6 | Các task chạy "khi bật" cờ tương ứng | **Đúng một phần: thiếu giá trị mặc định** | Ở `BaseSimSettings` cả ba cờ mặc định `False` (`sim_settings.py:447-462`), nhưng `BuildingSimSettings` đặt `add_space_boundaries=True` (dòng 945). Plugin EnergyPlus đặt `correct_space_boundaries=True` và `close_space_boundary_gaps=True` (`PluginEnergyPlus/bim2sim_energyplus/sim_settings.py:180-189`). Tức là với EnergyPlus, **mặc định cả ba bước đều chạy**, kể cả bước sinh 2b |
| 7 | Thứ tự plugin EnergyPlus: Create → Add2B → Correct | **Đúng** | `PluginEnergyPlus/bim2sim_energyplus/__init__.py:20-22` |
| 8 | Discussion #498: IFC4 phải có boundary 2nd level; phần lớn phần mềm CAD không xuất mặc định (claude-02 ghi "chưa mở") | **Đúng, nay đã xác minh**; còn hai ý claude-02 chưa ghi | Maintainer (veronikarichter, 29/03/2023) xác nhận hai ý đó. Câu trả lời được chấp nhận (31/03/2023) còn nêu: bim2sim **chưa xử lý được curtain wall**, và có lỗi chuyển đơn vị (milimét) [D498] |
| 9 | "Chưa đọc `get_parents_and_children`; không cần cho kết luận" | Chấp nhận được | Hàm này ở `sb_creation.py:132` (ngưỡng `opening_area_tolerance=0.01`): gán boundary cửa/lỗ mở vào boundary tường cha. Không ảnh hưởng các kết luận trên |

## 3. Chạy thử bộ lọc level của bim2sim trên bộ IFC của TASK-001

Mình tái lập đúng điều kiện ở `sb_creation.py:393-395` bằng IfcOpenShell 0.9.0, không chạy bim2sim. Lệnh và kết quả:

```python
keep = [e for e in f.by_type("IfcRelSpaceBoundary")
        if not (e.is_a() == "IfcRelSpaceBoundary1stLevel" or e.Name == "1stLevel")]
```

| File (`samples/…`) | Nhãn level trong file | RSB | bim2sim giữ | Bỏ |
|---|---|---|---|---|
| `small/pilot-project-1/2/3` | `Name='2ndLevel'` | 76 / 86 / 166 | toàn bộ | 0 |
| `small/ac20-fzk-haus` | `Name='2ndLevel'`, `Description='2a'` | 81 | 81 | 0 |
| `corpus_real/ac11-fzk-haus` | `Name='Second Level'` | 98 | 98 | 0 |
| `large/ac20-institute-var-2`, `large/kit-smiley-west`, `large/molio` | `2ndLevel` / `2a` | 1000 / 1689 / 1973 | toàn bộ | 0 |
| `large/rwth-digitalhub-with-sb` | lớp con IFC4 thật | 4142 | 2582 (1866 trên `IfcSpace` + 716 trên `IfcExternalSpatialElement`) | 1560 (đúng bằng số 1st level) |
| `small/duplex-a` | `Name='1stLevel'` | 265 | **0** | 265 |
| `large/clinic-architectural` | `Name='1stLevel'` | 3124 | **0** | 3124 |
| `corpus_real/office-a` | `Name='1stLevel'` | 1334 | **0** | 1334 |
| `large/taltech-ds3` | `Name='1stLevel'` | 1927 | **0** | 1927 |
| `large/bimedit-1fd06ad21e9e` | `Name='1stLevel'` | 360 | **0** | 360 |

**Hệ quả** (suy ra từ mã, chưa chạy bim2sim):
- Với các file chỉ có 1st level, bim2sim không còn boundary nào. Khi đó bước 2b không chạy được, vì hàm `get_spaces_with_bounds` cần space có boundary (chưa kiểm chứng).
- Bộ lọc là **loại trừ**, nên một boundary 1st level có `Name` rỗng hoặc ghi khác `'1stLevel'` (ví dụ HHS Office, `Name` rỗng, xem `research/04-datasets-and-validation/raw/survey-ifc-samples.md`) sẽ bị bim2sim **coi nhầm là 2nd level**.
- Tài liệu bim2sim (`docs/source/simulation-guide/simulation-types.md:55-57`) yêu cầu "IfcRelSpaceBoundary2ndLevel (optimum) or IfcRelSpaceBoundary with **Description** 2ndLevel". Nhưng mã kiểm tra **`Name`**, không kiểm tra `Description`. Trong dữ liệu thật thì `Description` là `2a`, còn `2ndLevel` nằm ở `Name`. **Tài liệu và mã không khớp nhau.**

## 4. Đối chiếu bài Fichter 2021 với phần IFC2SB của TASK-002 (kiểm chéo nhanh)

| Điểm | Bài [F21] | Mã [I] / claude-02 | Nhận xét |
|---|---|---|---|
| Graph | Edge-face graph tạo bằng giao Boolean các mặt; duyệt từ một mặt ngẫu nhiên, gom láng giềng đệ quy; ở cạnh có nhiều mặt thì chọn mặt có góc nhỏ hơn | `Kernel::find_spaces` (`Kernel.cpp:406`) dùng stack, mỗi thành phần liên thông là một `Space` | **Khớp** với `ifc2sb-analysis.md`. Việc chọn mặt theo góc nhỏ hơn được làm ở bước tỉa trước đó (`remove_non_manifold_adjacency_by_angle`), nên khi tới `find_spaces` thì DFS thuần là đủ |
| Offset mặt | Mặt được offset "a few centimeters" để lấp khe | `face_offset_length = 0` (`Graph.cpp:95`), không có tuỳ chọn dòng lệnh | **Khớp** với ghi chú của claude-02: bản phát hành **không bật** bước bài báo mô tả |
| Boundary ảo (virtual) | Kết luận nêu "support of virtual space boundaries" là việc **tương lai**; zone cầu thang lệch vì thiếu boundary ảo | — | `ifc2sb-analysis.md` **chưa nêu** hạn chế này. Với sân vận động (nhiều không gian thông nhau, hành lang mở) đây là rủi ro lớn |
| Mặt tiếp đất | Việc phân loại boundary tiếp xúc đất chưa xong vì chưa xét `IfcSite` | — | **Chưa nêu** trong `ifc2sb-analysis.md` |
| Kiểm chứng | Chỉ **1 mô hình**: KIT IFC4 "Phantasy office building" (AC20-Institute-Var-2). Kết quả: 1 `IfcExternalSpatialElement`, 78 `IfcSpace`, "almost 2000" boundary. Khớp số và vị trí zone so với bản gốc, trừ cầu thang. **Không có số liệu thời gian chạy hay bộ nhớ** | — | So với số mình đo ở TASK-001 trên bản gốc: 82 `IfcSpace`, 1000 RSB (chỉ 2a, không có 2b). Bằng chứng cho **quy mô lớn = thấp** (chỉ một toà nhà cỡ M) |

## 5. Phát hiện mới ảnh hưởng tới dự án

1. **Ground truth từ exporter cũng có lỗi.** [R22] kiểm tra AC20-FZK-Haus (IFC4, ArchiCAD), chính là `samples/small/ac20-fzk-haus.ifc`:
   - 5 lỗi cú pháp (`RelatedBuildingElement` không trỏ tới `IfcElement`);
   - 7 lỗi đỉnh thẳng hàng hoặc trùng nhau;
   - **62 pháp tuyến quay vào trong space**, chỉ 19 được coi là đúng (phần lớn là lỗ mở);
   - **4 space không kín**.

   → Khi đo độ khớp với ground truth (`PRIMARY_OBJECTIVE.md` mục 3), phép so phải **không phụ thuộc hướng pháp tuyến**. Không được giả định boundary gốc kín và đúng.
2. **Cách kiểm độ kín rẻ hơn ray tracing.** [R22] khâu (sew) mọi boundary của một space rồi đếm **cạnh tự do (free edges)**; còn cạnh tự do là còn hở. Cách này dùng được trực tiếp cho tiêu chí "tập boundary đóng kín" của dự án.
3. **bim2sim chuyển boundary ảo thành tường hoặc sàn có cấu tạo "air wall".** [R22] ghi điều này khi so sánh IFC với IDF. Nó không làm hỏng mô phỏng, nhưng làm lệch thống kê theo loại bề mặt.
4. **Không có thuật toán sinh boundary 1st/2a trong lịch sử bim2sim.** Đã kiểm `git log --grep` (116 commit nhắc "space boundar"). Các commit có chữ "space boundary generation" (ví dụ `a6de19b32`, 2021-02-22) nói về việc **khởi tạo đối tượng Python** từ `IfcRelSpaceBoundary`, không phải sinh hình học. Riêng "webtool generated space boundaries" (lớp `SpaceBoundaryRepresentation`, dạng `IfcBuildingElementProxy` tên `ProxyBound`) đã bị xoá ở commit `65b01fb17` (2025-05-12). Nguồn gốc của webtool này **chưa xác minh**.
5. **Hướng dùng bim2sim cho dự án:**
   - Đầu ra của pipeline nên ghi level bằng **lớp con IFC4** (`IfcRelSpaceBoundary2ndLevel`) **và** `Name='2ndLevel'`, để bim2sim cũng như các công cụ dựa vào `Name` đều đọc đúng.
   - Không nên đưa file chỉ có 1st level vào bim2sim.
   - Nếu dùng bim2sim/EnergyPlus làm bộ kiểm chứng ngoài (như `bim2sim-analysis.md` mục 4 đề xuất), nên **tắt `close_space_boundary_gaps`**. Nếu không, bim2sim sẽ tự lấp khe bằng 2b và che mất lỗi độ kín của pipeline.

## 6. Đề xuất sửa cho `bim2sim-analysis.md` (để claude-02 quyết định)
- Kết luận ngắn: đổi "chỉ đọc" thành "không sinh boundary 1st level hay 2a; chỉ sinh thêm 2b lấp khe từ hình `IfcSpace` có sẵn (mặc định bật trong plugin EnergyPlus)".
- Thêm bộ lọc level ở `sb_creation.py:393-395` và chỗ tài liệu không khớp mã (`Name` so với `Description`).
- Thêm quan hệ cùng dự án BIM2SIM giữa IFC2SB và bim2sim, kèm bằng chứng từ test.
- Đánh dấu Discussion #498 là đã xác minh; thêm ý về curtain wall và lỗi đơn vị mm.
- `ifc2sb-analysis.md`: thêm hai hạn chế do bài báo tự nêu (chưa có boundary ảo, chưa phân loại mặt tiếp đất) và ghi chú rằng bài chỉ kiểm chứng trên 1 mô hình, không có số liệu hiệu năng.

## Chưa xác minh / việc còn lại
- **Chưa chạy bim2sim** (cần conda và `pythonocc-core`). Các hệ quả ở mục 3 là suy ra từ mã.
- Chưa đọc Richter et al. 2021 (Forum Bauinformatik), là bài mô tả các thuật toán trong `sb_correction.py`. Cần mở `tuprints.ulb.tu-darmstadt.de`.
- Chưa đọc Jansen et al. 2021 (BIM2SIM, IBPSA BS2021, DOI 10.26868/25222708.2021.30228), có thể nằm trên `publications.ibpsa.org`.
- Đơn vị của ngưỡng 1e-2 trong `_compute_2b_bound_gaps`; nguồn gốc của "webtool".

## Nguồn
- [F21] https://publications.ibpsa.org/proceedings/bs/2021/papers/bs2021_30156.pdf — truy cập 2026-11-10 (toàn văn)
- [R22] https://publications.ibpsa.org/proceedings/simbuild/2022/papers/simbuild2022_C033.pdf (trang bài: https://publications.ibpsa.org/conference/paper/?id=simbuild2022_C033) — truy cập 2026-11-10 (toàn văn)
- [B] https://github.com/BIM2SIM/bim2sim — clone đầy đủ `270cd0a36f`, truy cập 2026-11-10
- [I] https://github.com/RWTH-E3D/IFC2SB — clone `96a89cd`, truy cập 2026-11-10
- [D498] https://github.com/BIM2SIM/bim2sim/discussions/498 — truy cập 2026-11-10

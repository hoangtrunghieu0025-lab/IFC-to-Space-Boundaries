# Phân tích bim2sim: sinh hay chỉ đọc space boundary

- **Câu hỏi nghiên cứu**: bim2sim sinh `IfcRelSpaceBoundary` hay chỉ đọc? Có bước graph "Topology Graph → Space Graph → Boundary Graph" không?
- **Kết luận ngắn**:
  - bim2sim **không sinh boundary 1st level hay 2a từ phần tử bao**. Nó đọc `IfcRelSpaceBoundary` có sẵn trong IFC rồi **sửa** (hướng bề mặt, tách đa giác lõm, dời boundary con về cha). Nó chỉ **sinh thêm hình học boundary loại 2b** để lấp khe, bằng cách lấy hình `IfcSpace` có sẵn trừ đi các boundary. Trong plugin EnergyPlus, cả ba bước này **bật mặc định**. [sửa bởi claude-01, 2026-11-10: bản trước ghi "chỉ đọc" và "chạy khi bật cờ", chưa nêu việc sinh 2b và giá trị mặc định]
  - **Không có graph** trong mã space boundary: `networkx` chỉ xuất hiện ở mã HVAC. Khẳng định "Topology Graph → Space Graph → Boundary Graph" của ghi chú ban đầu **không có bằng chứng**. Graph của chuỗi xử lý này nằm trong IFC2SB (xem `ifc2sb-analysis.md`).
  - **IFC2SB và bim2sim cùng một dự án** (BIM2SIM, BMWi 03ET1562A). IFC2SB được làm ra để **cung cấp boundary cho bim2sim**; bộ test của bim2sim dùng file do IFC2SB sinh (mục 3).
  - **Bộ lọc level rất thô**: bim2sim chỉ bỏ boundary có lớp `IfcRelSpaceBoundary1stLevel` hoặc `Name == '1stLevel'`, còn lại đều bị coi là 2nd level. Chạy thử trên bộ IFC của TASK-001: **5/14 file có boundary bị bỏ sạch** (mục 4).
- **Độ tin cậy**: cao. Đã đọc mã kèm toàn bộ lịch sử commit, đọc toàn văn Fichter 2021 và Richter 2022, chạy thử bộ lọc level trên 14 file IFC. **Chưa chạy bim2sim end-to-end**: chưa kiểm chứng.
- **Ngày thực hiện**: 2026-11-10 (claude-02; claude-01 kiểm lại và bổ sung theo yêu cầu người dùng)

## 1. Thông tin
| Mục | Giá trị |
|---|---|
| Repo | https://github.com/BIM2SIM/bim2sim, HEAD `270cd0a36f` (2026-04-14). claude-01 clone đầy đủ: 5.987 commit |
| License | LGPL v3 (`LICENSE`) |
| Ngôn ngữ | Python; hình học dùng pythonocc (`OCC.Core`); dựng IDF bằng GeomEppy (bản fork `BIM2SIM/geomeppy`, `pyproject.toml`) |

## 2. Việc cụ thể (từ `bim2sim/tasks/bps/`)
| Task | Việc | Bằng chứng |
|---|---|---|
| `CreateSpaceBoundaries` (`sb_creation.py`) | Lọc `IfcRelSpaceBoundary` (`TypeFilter(('IfcRelSpaceBoundary',))`, dòng 56) và dựng đối tượng `SpaceBoundary`; gán phần tử cha, cửa/lỗ mở (`get_parents_and_children`, dòng 132, `opening_area_tolerance=0.01`). **Bỏ qua boundary là lớp `IfcRelSpaceBoundary1stLevel` hoặc có `Name == '1stLevel'`** (dòng 393-395); boundary trên `IfcExternalSpatialElement` chỉ được giữ khi bật `create_external_elements` | docstring: "Create space boundaries for elements from IfcRelSpaceBoundary" |
| `AddSpaceBoundaries2B` (`sb_2b_generation.py`) | **Sinh hình học 2b**: lấy hình `space_shape` của **`IfcSpace` có sẵn** (`bps_elements.py:234-245`), trừ dần (`BRepAlgoAPI_Cut`, dòng 118) các boundary nằm sát hình space (khoảng cách ≤ 1e-6, dòng 115). Mỗi mặt còn lại thành một `SpaceBoundary2B`. Bỏ qua space nếu diện tích mặt space trừ tổng diện tích boundary < 1e-2 (dòng 101; ngưỡng tuyệt đối, đơn vị chưa kiểm chứng). Lỗi bất kỳ thì chỉ ghi warning và không thêm 2b (dòng 63) | Docstring dòng 79: mặt dư được gán loại 2b "for simplicity", chưa xác minh 2a hay 2b |
| `CorrectSpaceBoundaries` (`sb_correction.py`) | `fix_surface_orientation` (172), `move_children_to_parents` (114), `split_non_convex_bounds` (267), `add_and_split_bounds_for_shadings` (88) | tên hàm; thuật toán mô tả trong Richter et al. 2021 (Forum Bauinformatik), **chưa đọc** |
| Thứ tự plugin EnergyPlus | `CreateSpaceBoundaries`, `AddSpaceBoundaries2B`, `CorrectSpaceBoundaries` | `plugins/PluginEnergyPlus/bim2sim_energyplus/__init__.py:20-22` |
| Giá trị mặc định | `BaseSimSettings`: `add_space_boundaries`, `correct_space_boundaries`, `close_space_boundary_gaps` đều `False` (`sim_settings.py:447-462`). `BuildingSimSettings`: `add_space_boundaries=True` (dòng 945). Plugin EnergyPlus: `correct_space_boundaries=True`, `close_space_boundary_gaps=True` (`PluginEnergyPlus/bim2sim_energyplus/sim_settings.py:180-189`) | **Với EnergyPlus, mặc định cả ba bước đều chạy, kể cả sinh 2b** |

Lịch sử commit: không có thuật toán sinh boundary 1st level hay 2a trong bim2sim.

> [sửa bởi claude-02, 2026-11-10: bổ sung định nghĩa 2a/2b có nguồn] Theo NISTIR 7687 (mục thuật ngữ 2LSB, trang 2; chú thích 1 trang 84): 2a = phía bên kia của boundary là một **space**; 2b = phía bên kia **không có space mà là một phần tử vật lý** (còn gọi 3rd level). Mô tả `AddSpaceBoundaries2B` ở trên (phần mặt `IfcSpace` còn lại sau khi trừ các boundary sát nó, dùng để lấp khe) **chưa được đối chiếu** với định nghĩa này: chưa kiểm phần dư đó có đúng là 2b theo NIST hay chỉ là cách bim2sim gọi tên. Chưa kiểm chứng. Nguồn: https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nistir7687.pdf (đã tải và đọc đoạn trích, 2026-11-10).
- Đã kiểm `git log --grep` (116 commit nhắc "space boundar"). Các commit có chữ "space boundary generation" (ví dụ `a6de19b32`, 2021-02-22) nói về việc **khởi tạo đối tượng Python** từ `IfcRelSpaceBoundary`, không phải sinh hình học.
- Lớp `SpaceBoundaryRepresentation` dành cho "webtool generated space boundaries" (dạng `IfcBuildingElementProxy` tên `ProxyBound`) đã bị xoá ở commit `65b01fb17` (2025-05-12). Nguồn gốc của webtool này **chưa xác minh**.

## 3. Quan hệ với IFC2SB (bổ sung bởi claude-01)
- Lời cảm ơn trong [S3] ghi dự án "BIM2SIM", mã 03ET1562A. Phần ứng dụng BEPS của [S3] dựng IDF bằng **chính toolchain BIM2SIM** (IfcOpenShell + GeomEppy). Ở đó 2b do IFC2SB sinh và được đặt adiabatic trong EnergyPlus. [S3] cũng nêu rằng với toolchain này, việc có sẵn SB là thiết yếu vì hình học SB là đầu vào của mô hình năng lượng.
- Bộ test bim2sim dùng đầu ra của IFC2SB:
  - docstring `PluginEnergyPlus/test/integration/test_energyplus.py:66` nhắc "Eric Fichter's Space Boundary Generation tool";
  - `PluginIFCCheck/test/integration/test_ifccheck.py:38` dùng `AC20-FZK-Haus_with_SB55.ifc`;
  - `PluginOpenFOAM/test/integration/test_openfoam.py:177` nhắc "DigitalHub, IFC2SB Version";
  - commit `0b2fd437e` (2021-04-09) thêm test `KIT-EDC_with_SB.ifc` "with generated Space Boundaries".
- [S4] (Richter et al. 2022, cùng nhóm) xếp việc "làm mới SB" là hướng của các thuật toán sinh boundary (van Treeck & Rank, Rose & Bazjanac, Lilis, Fichter). Hướng của nhóm bim2sim là **kiểm tra và sửa** boundary có sẵn.

## 4. Bộ lọc level: chạy thử trên bộ IFC của TASK-001 (claude-01)
Tái lập điều kiện ở `sb_creation.py:393-395` bằng IfcOpenShell 0.9.0, không chạy bim2sim:

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
| `small/duplex-a`, `large/clinic-architectural`, `corpus_real/office-a`, `large/taltech-ds3`, `large/bimedit-1fd06ad21e9e` | `Name='1stLevel'` | 265 / 3124 / 1334 / 1927 / 360 | **0** | toàn bộ |

Hệ quả (suy ra từ mã, chưa chạy bim2sim):
- File chỉ có 1st level thì bim2sim không còn boundary nào.
- Bộ lọc là **loại trừ**, nên boundary 1st level có `Name` rỗng (ví dụ HHS Office, xem `research/04-datasets-and-validation/raw/survey-ifc-samples.md`) sẽ bị **coi nhầm là 2nd level**.
- **Tài liệu và mã không khớp**: tài liệu (`docs/source/simulation-guide/simulation-types.md:55-57`) yêu cầu "IfcRelSpaceBoundary2ndLevel (optimum) or IfcRelSpaceBoundary with **Description** 2ndLevel", nhưng mã kiểm tra **`Name`**. Dữ liệu thật ghi `2ndLevel` ở `Name`, còn `Description` là `2a`.

## 5. Cảnh báo thực tế từ chính dự án
Thảo luận #498 của bim2sim, **đã mở và xác minh** (claude-01, 2026-11-10) [S2]:
- Maintainer (veronikarichter, 29/03/2023): IFC4 phải chứa space boundary 2nd level; phần lớn phần mềm CAD **không xuất mặc định**, phải bật trong tuỳ chọn export.
- Câu trả lời được chấp nhận (31/03/2023) nêu thêm:
  - bim2sim **chưa xử lý được curtain wall**;
  - dữ liệu enrichment chỉ có template tới năm 2015;
  - có lỗi chuyển đơn vị khi file dùng milimét.

Ghi chú liên quan đến hướng D trong `approach-critique.md`.

## 6. Ý nghĩa cho dự án
- **Bộ kiểm chứng ngoài**: bim2sim là **người dùng tiềm năng** của đầu ra (IFC có `IfcSpace` + boundary 2nd level). Có thể đưa IFC suy ra vào bim2sim/EnergyPlus xem có chạy không, nhưng không lấy làm nguồn thuật toán graph. Khi dùng nó để kiểm chứng:
  - nên **tắt `close_space_boundary_gaps`**, nếu không bim2sim tự lấp khe bằng 2b và che mất lỗi độ kín của pipeline;
  - đầu ra nên ghi level bằng **lớp con IFC4 `IfcRelSpaceBoundary2ndLevel` và đồng thời `Name='2ndLevel'`**;
  - không đưa file chỉ có 1st level vào.
- **Bù khe bằng phép trừ hình**: có thể dùng ý tưởng này để kiểm tra độ kín (so diện tích space với tổng boundary). Nhưng nó **cần `IfcSpace` có sẵn**, nên không dùng được khi phải suy ra space.
- **Kiểm độ kín rẻ hơn ray tracing**: [S4] khâu (sew) mọi boundary của một space rồi đếm **cạnh tự do (free edges)**; còn cạnh tự do là còn hở. Dùng được cho tiêu chí "tập boundary đóng kín" của `PRIMARY_OBJECTIVE.md`.
- **Ground truth từ exporter cũng có lỗi**: [S4] kiểm AC20-FZK-Haus (IFC4, ArchiCAD), chính là `samples/small/ac20-fzk-haus.ifc`:
  - 5 lỗi cú pháp (`RelatedBuildingElement` không trỏ tới `IfcElement`);
  - 7 lỗi đỉnh thẳng hàng hoặc trùng nhau;
  - **62 pháp tuyến quay vào trong space**, chỉ 19 được coi là đúng;
  - **4 space không kín**.

  → Phép so với ground truth phải **không phụ thuộc hướng pháp tuyến**, và không được giả định boundary gốc kín.
- **Boundary ảo**: [S4] ghi rằng bim2sim chuyển boundary ảo thành tường hoặc sàn có cấu tạo "air wall". Việc này không làm hỏng mô phỏng, nhưng làm lệch thống kê theo loại bề mặt.

## Chưa xác minh / việc còn lại
- **Chưa chạy bim2sim end-to-end** (cần conda + `pythonocc-core`); chưa biết nó chịu được IFC lớn không.
- Chưa đọc Richter et al. 2021 (Forum Bauinformatik, https://tuprints.ulb.tu-darmstadt.de/21521/): bài mô tả thuật toán trong `sb_correction.py`. Đã mở mạng (2026-11-10) nhưng trang có thử thách chống bot Anubis, không vượt qua; chưa thấy bản công khai khác. **BLOCKED**, cần tải tay.
- Chưa đọc Jansen et al. 2021 (BIM2SIM, IBPSA BS2021, DOI 10.26868/25222708.2021.30228).
- Đơn vị của ngưỡng 1e-2 trong `_compute_2b_bound_gaps`; nguồn gốc của "webtool".
- Chưa kiểm tra plugin OpenFOAM dùng IFC2SB ở bước nào ngoài file test.

## Nguồn
- [S1] https://github.com/BIM2SIM/bim2sim — clone `270cd0a36f` (claude-02 clone nông; claude-01 clone đầy đủ lịch sử). Các file `bim2sim/tasks/bps/sb_creation.py`, `sb_2b_generation.py`, `sb_correction.py`, `bim2sim/sim_settings.py`, `bim2sim/elements/bps_elements.py`, `plugins/PluginEnergyPlus/…`, `docs/source/simulation-guide/simulation-types.md`, tests, `README.md`, `LICENSE` (truy cập 2026-11-10)
- [S2] https://github.com/BIM2SIM/bim2sim/discussions/498 — đã mở (truy cập 2026-11-10)
- [S3] Fichter, Richter, Frisch, van Treeck (2021). *Automatic generation of second level space boundary geometry from IFC models*. Proc. 17th IBPSA Conf., tr. 1083–1090. https://publications.ibpsa.org/proceedings/bs/2021/papers/bs2021_30156.pdf (đọc toàn văn, truy cập 2026-11-10)
- [S4] Richter, Malhotra, Fichter, Hochberger, Frisch, van Treeck (2022). *Validation of IFC-based Geometric Input for Building Energy Performance Simulation*. SimBuild 2022, tr. 287–294. https://publications.ibpsa.org/proceedings/simbuild/2022/papers/simbuild2022_C033.pdf (đọc toàn văn, truy cập 2026-11-10; bản quyền ASHRAE, không lưu PDF)

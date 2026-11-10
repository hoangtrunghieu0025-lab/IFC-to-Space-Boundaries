# Phân tích bim2sim: sinh hay chỉ đọc space boundary

- **Câu hỏi nghiên cứu**: bim2sim sinh `IfcRelSpaceBoundary` hay chỉ đọc? Có bước graph "Topology Graph → Space Graph → Boundary Graph" không?
- **Kết luận ngắn**:
  - bim2sim **chỉ đọc** `IfcRelSpaceBoundary` có sẵn trong IFC, rồi **sửa** (hướng bề mặt, tách đa giác lõm, dời con về cha) và **bù khe hở** bằng boundary loại 2B. Nó **không sinh space boundary từ phần tử bao**.
  - **Không có graph** trong mã space boundary: `networkx` chỉ xuất hiện ở mã HVAC. Khẳng định "Topology Graph → Space Graph → Boundary Graph" của ghi chú ban đầu **không có bằng chứng**.
  - Quan hệ với IFC2SB: README của bim2sim trích bài Fichter 2021 và Richter 2021; bim2sim là bên **tiêu thụ** IFC có boundary (do IFC2SB hoặc phần mềm CAD sinh).
- **Độ tin cậy**: cao (đọc mã trực tiếp); chưa chạy bim2sim.
- **Ngày thực hiện**: 2026-11-10 (claude-02)

## 1. Thông tin
| Mục | Giá trị |
|---|---|
| Repo | https://github.com/BIM2SIM/bim2sim, clone nông `270cd0a36f` (2026-04-14) |
| License | LGPL v3 (`LICENSE`) |
| Ngôn ngữ | Python; hình học dùng pythonocc (`OCC.Core`) |

## 2. Việc cụ thể (từ `bim2sim/tasks/bps/`)
| Task | Việc | Bằng chứng |
|---|---|---|
| `CreateSpaceBoundaries` (`sb_creation.py`) | Lọc `IfcRelSpaceBoundary` (`TypeFilter(('IfcRelSpaceBoundary',))`) và dựng đối tượng `SpaceBoundary`; gán phần tử cha, cửa/lỗ mở | docstring: "Create space boundaries for elements from IfcRelSpaceBoundary"; chạy khi `add_space_boundaries` bật |
| `AddSpaceBoundaries2B` (`sb_2b_generation.py`) | Bù khe: lấy hình `space_shape` của **`IfcSpace` có sẵn**, trừ (`BRepAlgoAPI_Cut`) từng boundary; phần dư thành boundary loại 2B để space kín. Chỉ chạy khi `close_space_boundary_gaps` bật | `_compute_2b_bound_gaps`: so diện tích mặt space với tổng diện tích boundary, nếu chênh ≥ 1e-2 mới bù |
| `CorrectSpaceBoundaries` (`sb_correction.py`) | `fix_surface_orientation`, `move_children_to_parents`, `split_non_convex_bounds`, bóng đổ | tên hàm; bật bằng `correct_space_boundaries` |
| Thứ tự plugin EnergyPlus | `CreateSpaceBoundaries`, `AddSpaceBoundaries2B`, `CorrectSpaceBoundaries` | `plugins/PluginEnergyPlus/bim2sim_energyplus/__init__.py` |

## 3. Cảnh báo thực tế từ chính dự án
Thảo luận #498 của bim2sim: IFC4 phải chứa space boundary mức 2; phần lớn phần mềm CAD **không xuất mặc định**, phải bật trong tuỳ chọn export. [S2] Ghi chú liên quan đến hướng D trong `approach-critique.md`.

## 4. Ý nghĩa cho dự án
- bim2sim là **người dùng tiềm năng** của đầu ra (IFC có `IfcSpace` + boundary mức 2): có thể dùng làm **bộ kiểm chứng ngoài** (đưa IFC suy ra vào bim2sim/EnergyPlus xem có chạy không), không phải nguồn thuật toán graph.
- Thuật toán "bù khe" bằng phép trừ hình có thể dùng ý tưởng cho kiểm tra độ kín (so diện tích space với tổng boundary), nhưng **cần `IfcSpace` có sẵn**, không dùng được khi phải suy ra space.
- Chưa đọc: `sb_creation.get_parents_and_children` (logic ghép cha–con), mô hình `ThermalZone`. Không cần cho kết luận trên.

## Chưa xác minh / việc còn lại
- Chưa chạy bim2sim trên IFC mẫu; chưa biết nó chịu được IFC lớn không.
- Chưa kiểm tra các nhánh/plugin khác (OpenFOAM) có dùng IFC2SB ở bước nào (mã test nhắc "IFC2SB Version" ở `PluginOpenFOAM/test/integration/test_openfoam.py:177`).

## Nguồn
- [S1] https://github.com/BIM2SIM/bim2sim — clone `270cd0a36f`, các file `bim2sim/tasks/bps/sb_creation.py`, `sb_2b_generation.py`, `sb_correction.py`, `bim2sim/sim_settings.py`, `README.md`, `LICENSE` (truy cập 2026-11-10)
- [S2] https://www.github.com/BIM2SIM/bim2sim/discussions/498 (chỉ thấy qua kết quả tìm kiếm, chưa mở)

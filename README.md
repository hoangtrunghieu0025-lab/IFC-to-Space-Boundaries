# IFC-to-Space-Boundaries

Suy ra `IfcSpace` và sinh space boundary (`IfcRelSpaceBoundary`) từ mô hình IFC. Mục tiêu và phạm vi: xem `PRIMARY_OBJECTIVE.md`.

## Quy trình làm việc
- Agent đọc `AGENTS.md` đầu tiên; quy tắc chung ở `CLAUDE.md`; cộng tác ở `collab/CONTRACT.md`; việc cần làm ở `tasks/` (`python3 tasks/list.py`).

## Cấu trúc
| Thư mục | Nội dung |
|---|---|
| `research/` | Ghi chú nghiên cứu theo chủ đề (`01-ifc-spatial-model`, `02-ifc-geometry`, `03-space-and-boundary-algorithms`, `04-downstream-validation`) |
| `docs/` | Tài liệu tổng hợp cuối |
| `src/`, `tests/` | Code và test |
| `samples/` | File IFC mẫu |
| `config/` | Cấu hình (dung sai, quy tắc phân loại) |
| `out/` | Kết quả chạy (git-ignore) |
| `reports/` | Báo cáo tiến độ |

## Cài đặt
TODO (sẽ chốt khi có code: Python 3.12, `ifcopenshell`, `pytest`).

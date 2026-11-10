# samples/ — bộ IFC dùng để test

Bộ dữ liệu được chọn ở TASK-001. Tiêu chí chọn và thang điểm nằm ở `research/04-downstream-validation/dataset-quality-criteria.md`; khảo sát từng nguồn ở `research/04-downstream-validation/dataset-survey.md`.

## Cài đặt và tải lại

```bash
pip install ifcopenshell pyyaml
python3 samples/fetch_datasets.py            # tải mọi file còn thiếu theo manifest, kiểm sha256
python3 samples/fetch_datasets.py --tier S   # chỉ tầng S (nhỏ, dùng cho test tự động)
python3 samples/fetch_datasets.py --check    # chỉ kiểm sha256, không tải
```

- URL trong manifest ghim theo **commit SHA** của repo nguồn, nên tải lại cho ra đúng byte. Script báo `BADSHA` nếu không khớp.
- Nguồn dùng Git LFS (buildingsmart-community) tải qua `media.githubusercontent.com`.
- Mục `manual: true` (host bị chặn hoặc cần đăng nhập) không tải tự động được; script in hướng dẫn tải tay.

## Đo lại và cập nhật manifest

```bash
python3 samples/inspect_ifc.py --isolate samples/small/*.ifc   # in JSON Lines, mỗi file một dòng
python3 samples/update_manifest.py                             # đo mọi file có trên đĩa, ghi vào manifest
python3 samples/update_manifest.py --id clinic-architectural   # đo một file
```

## Quy ước thư mục

| Thư mục | Nội dung | Commit? |
|---|---|---|
| `samples/small/` | Tầng **S** (≤5 MB, ≤50 `IfcSpace`), giấy phép **cho phép tái phân phối** | **Có** |
| `samples/large/` | Tầng **M/L** có giấy phép rõ | Không (`.gitignore`); tải bằng script |
| `samples/corpus_real/` | File **chưa rõ giấy phép** (mọi tầng) | **Không bao giờ** (`.gitignore`) |
| `samples/manifest.yaml` | Danh mục: nguồn, URL, giấy phép, sha256, schema, số `IfcSpace`/`IfcRelSpaceBoundary`, điểm | Có |

## ⚠️ Giấy phép

- Không chép file từ `corpus_real/` sang `small/` khi chưa xác minh giấy phép và chưa cập nhật `license_class` trong manifest.
- **CC BY 4.0** (buildingSMART, Duplex, Clinic, Esplanades, Molio): khi dùng hoặc phát hành phải ghi nguồn như cột `source`/`license` trong manifest. README của Duplex yêu cầu ghi "BSI (2020)".
- **GPL-3.0** (Pilot project 1–3, lấy từ repo `brunopostle/IFC-to-gbXML-converter`): phân phối lại phải kèm giấy phép GPL-3.0 (https://www.gnu.org/licenses/gpl-3.0.html). Repo đó chỉ ghi GPL cho toàn repo, không có giấy phép riêng cho file dữ liệu.
- **MIT** (RWTH DigitalHub): giữ thông báo bản quyền "Copyright (c) 2020 RWTH Aachen University".

## Ghi chú khi dùng làm ground truth

- Level của `IfcRelSpaceBoundary` được ghi khác nhau giữa các file:
  - IFC4 có lớp con thật `IfcRelSpaceBoundary1stLevel`/`2ndLevel`. Chỉ `rwth-digitalhub-with-sb` dùng cách này. Lưu ý `2ndLevel` là lớp con của `1stLevel`.
  - Các file còn lại dùng lớp cha và ghi level vào `Name`: Revit ghi `1stLevel`/`2ndLevel`, ArchiCAD ghi `2ndLevel` kèm `Description` `2a`, ArchiCAD 11 ghi `Second Level`.
  - Xem `measured.rsb_level_labels` trong manifest để biết file nào dùng cách nào.
- `CorrespondingBoundary` hiện chỉ có trong `rwth-digitalhub-with-sb`.

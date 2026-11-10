# PRIMARY OBJECTIVE

> Mục tiêu chính của dự án **IFC-to-Space-Boundaries**: từ một mô hình **IFC** (IFC2x3 / IFC4), tự động **suy ra `IfcSpace`** (khi mô hình thiếu, thiếu sót hoặc sai) **và sinh `IfcRelSpaceBoundary`** (ưu tiên 2nd level) cho từng không gian, phân loại đúng và kiểm chứng được, để dùng cho phân tích năng lượng/nhiệt và các bài toán không gian khác.

## 1. Hiểu mô hình
- Vai trò của `IfcSpace`, `IfcRelSpaceBoundary` (1st/2nd level), phần tử bao (tường, sàn, trần, mái, cột, cửa, cửa sổ) và các quan hệ `IfcRelVoidsElement` / `IfcRelFillsElement`, `IfcRelAggregates` / `IfcRelContainedInSpatialStructure`.
- `IfcSpace` nằm ở đâu trong cây không gian (`IfcBuildingStorey`), thuộc tính cần có (`Name`, `LongName`, `CompositionType`, `PredefinedType`, `Representation`, Pset_SpaceCommon…).
- Khác biệt IFC2x3 vs IFC4 vs IFC4.3; MVD nào yêu cầu space và space boundary.

## 2. Pipeline mục tiêu
1. **Đọc IFC** bằng IfcOpenShell; chuẩn hoá đơn vị và hệ toạ độ.
2. **Lấy hình học** các phần tử bao theo tầng; làm sạch (dung sai, non-manifold).
3. **Suy ra IfcSpace**:
   - Nếu đã có `IfcSpace`: kiểm tra, đối chiếu với vùng bao kín thực tế; bổ sung không gian bị thiếu.
   - Nếu chưa có: tìm các vùng kín bao bởi tường/sàn/trần/cửa (lát cắt mặt bằng theo tầng, polygonize), tạo `IfcSpace` với `Representation` (extrusion từ mặt sàn đến trần/mái), gán vào `IfcBuildingStorey`.
   - Gán thuộc tính cơ bản (Name, diện tích, thể tích, chiều cao) và cách xử lý vùng hở (cửa đi, không gian mở, shaft).
4. **Sinh boundary**: giao bề mặt không gian với phần tử bao, tách theo phần tử, xử lý lỗ mở.
5. **Phân loại**: `PhysicalOrVirtualBoundary`, `InternalOrExternalBoundary`, ghép `CorrespondingBoundary`, `ParentBoundary`.
6. **Xuất**: ghi `IfcSpace` + `IfcRelSpaceBoundary` (kèm `ConnectionGeometry`) vào IFC mới, và/hoặc bảng JSON/CSV; giữ GUID của phần tử gốc.

## 3. Tiêu chí đạt
- Mỗi vùng kín thực tế có đúng một `IfcSpace` (không thiếu, không trùng); hình học space không chồng lấn nhau quá dung sai.
- Với IFC đã có `IfcSpace`: kết quả suy ra khớp không gian gốc (đo bằng IoU diện tích, ngưỡng chốt trong spec).
- Mỗi `IfcSpace` có tập boundary đóng kín; tổng diện tích khớp bề mặt không gian trong dung sai (mặc định 1e-3, sẽ chốt trong spec).
- Boundary nội bộ có cặp `CorrespondingBoundary` đối xứng.
- Đầu ra mở được bằng IfcOpenShell và viewer IFC (Bonsai); có test tự động trên mẫu nhỏ.

## 4. Ngoài phạm vi (tạm thời)
- Tạo mô hình IFC từ CAD, GIS/GeoPackage/IMDF.
- Nhận dạng chức năng phòng (loại phòng) bằng AI/ML.

> Ghi chú: các giả định ở trên là bản nháp; chốt lại cùng người dùng trong task đầu tiên.

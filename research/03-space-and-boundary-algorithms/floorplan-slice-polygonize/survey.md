# Khảo sát hướng lát cắt mặt bằng theo tầng và polygonize

- **Câu hỏi nghiên cứu**: những công cụ và bài báo nào tìm phòng bằng lát cắt mặt bằng, cell complex 2D hoặc polygonize; xử lý cửa, tường cong ra sao?
- **Kết luận ngắn**: hướng này **có tiền lệ thực dụng** (FreeCAD SketchArch, Bonsai) nhưng **không thấy bài báo học thuật** coi nó là phương pháp sinh `IfcSpace` từ IFC; các công cụ đều dựng khối **đùn từ dấu chân 2D**. Bằng chứng về độ tin cậy là yếu: chủ yếu là diễn đàn và mã.
- **Độ tin cậy**: trung bình-thấp. Chỉ SketchArch đọc được mã; Bonsai, floorplan-parser, Cloud2BIM chỉ thấy qua kết quả tìm kiếm.
- **Ngày thực hiện**: 2026-11-10 (claude-02)

| Công cụ / nguồn | Đầu vào | Cách tìm miền kín | Cửa | Tường cong/chéo | Đầu ra | Mức đọc |
|---|---|---|---|---|---|---|
| **FreeCAD_SketchArch** `DetectRoom` (LGPL-2.1, commit `e81620a893`) | cạnh của một sketch | `BOPTools.SplitAPI.slice(hộp bao, cạnh)` chia hộp bao thành vùng, bỏ vùng chạm hộp bao, **đùn `FloorHeight`** | không xử lý cửa (người dùng vẽ cạnh đóng) | cạnh cong của sketch dùng được | khối đùn (compound), không phải `IfcSpace` | **đã đọc mã** (`ArchSketchObject.py:399-417`) |
| **FreeCAD `Arch Space`** (lõi) | mặt chọn tay | tính từ hộp bao trừ phần sau từng mặt | — | — | `Arch Space` | trang wiki |
| **Bonsai / BlenderBIM** "Generate spaces from walls" | tường được chọn hoặc vị trí con trỏ 3D | "từ dấu chân 2D của tường, chỉ ra khối đùn" (người dùng trên OSArch) | dùng `IfcVirtualElement` làm mặt phẳng ngăn | nhánh phát triển (chưa xác nhận phát hành) thêm tường xiên/cong, bước footprint-to-profile + B-rep dự phòng | `IfcSpace` đùn | chỉ diễn đàn |
| **floorplan-parser** (`detect_rooms_from_walls`, trên Hugging Face) | tường 2D | đồ thị đường trục tường → `shapely.polygonize` lấy mặt kín, lọc diện tích; hoặc trừ hợp tường khỏi biên tầng (tường dày) | khe lớn hơn ngưỡng nhưng nhỏ hơn giới hạn thì đóng | — | polygon phòng | chỉ kết quả tìm kiếm |
| **Cloud2BIM** (arXiv 2503.11498) | đám mây điểm | tạo polygon phòng từ bề mặt tường thật, tách phòng | có phát hiện lỗ mở | — | IFC | chỉ tóm tắt bên thứ ba |
| Bằng sáng chế US 10997325 | mặt bằng 2D | tìm "vòng kín" của tường, gắn cửa vào vòng | có | — | — | chỉ tiêu đề và tóm tắt |
| Topologic (OSArch) | mặt phẳng tường/sàn/mái | CellComplex 3D | — | khó với mái phức tạp, tường kính | — | chỉ diễn đàn |

## Xử lý khe cửa trong văn liệu (mức tóm tắt)
- Phát hiện vòng kín trên biểu diễn polygon của tường, đóng khe do cửa và cửa sổ (một tổng quan).
- Với ảnh raster: đóng hình thái học, phát hiện cửa để đóng. [không áp dụng trực tiếp cho IFC]

## Điểm đáng chú ý cho dự án
- Công cụ gần với "đầu ra" nhất là **Bonsai**: cho `IfcSpace` đùn dấu chân. Báo cáo của người dùng: lệch 3 cm so với tường khi dùng "từ tường", một file từ kiến trúc sư không sinh được space, và chọn tường chỉ ra một space lớn (diễn đàn, chưa xác nhận bản mới).
- Không thấy công cụ nào dùng cho khán đài/mái dốc. Chưa có thử nghiệm quy mô lớn.

## Nguồn
- [S1] FreeCAD_SketchArch `ArchSketchObject.py` — clone `e81620a893`, đã đọc (2026-11-10): https://github.com/paullee0/FreeCAD_SketchArch
- [S2] FreeCAD Arch Space: https://wiki.freecad.org/Arch_Space
- [S3] OSArch — Create ifcSpaces in BlenderBIM: https://community.osarch.org/discussion/comment/15839/ ; Generate spaces efficiently: https://community.osarch.org/discussion/comment/18735/ (chỉ kết quả tìm kiếm)
- [S4] floorplan-parser `geometry.py`: https://huggingface.co/rikhoffbauer2/floorplan-parser/blob/main/floorplan/geometry.py (chỉ kết quả tìm kiếm)
- [S5] Cloud2BIM: https://arxiv.org/html/2503.11498v1 (chỉ kết quả tìm kiếm)
- [S6] US 10997325: https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/10997325 (chỉ kết quả tìm kiếm)

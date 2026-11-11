import logging

import ifcopenshell
import ifcopenshell.api
import ifcopenshell.guid
import ifcopenshell.util.unit
import numpy as np

from face_graph import AirFace
from find_spaces import SpaceCandidate
from space_boundaries import SpaceBoundary

# =====================================================================
# GIẢI THÍCH FILE: ghi IfcSpace và IfcRelSpaceBoundary vào một file IFC mới
#
# 1. Ý CHÍNH
# Đến bước này mọi kết quả mới chỉ nằm trong bộ nhớ Python. File này ghi chúng thành một file IFC
# thật: mỗi phòng thành một IfcSpace có hình học, mỗi boundary thành một IfcRelSpaceBoundary, để
# mở được bằng viewer IFC.
#
# 2. TẠO BẢN SAO FILE IFC SỬA
# File gốc có thể đã có IfcSpace và boundary của riêng nó. Kết quả mới thay thế chúng (IFC2SB
# cũng làm vậy) để không bị trùng lặp. File gốc không bị sửa, kết quả ghi ra file khác.
#
# 3. HÌNH HỌC CỦA IfcSpace
# IFC mô tả vỏ của phòng từ nhỏ đến lớn: điểm (IfcCartesianPoint) -> vòng (IfcPolyLoop) -> mặt
# (IfcFace, viền ngoài là IfcFaceOuterBound) -> vỏ kín (IfcClosedShell) -> khối (IfcFacetedBrep).
# Khối này được gói vào IfcShapeRepresentation (loại "Body", "Brep") rồi IfcProductDefinitionShape
# và gắn vào IfcSpace qua thuộc tính Representation.
#
# 4. CHIỀU CỦA CÁC VÒNG MẶT
# IFC yêu cầu pháp tuyến của khối hướng ra ngoài khối. Nhưng pháp tuyến của mình hướng vào không
# khí, tức vào trong phòng. Nên khi ghi hình cho IfcSpace phải đảo thứ tự các đỉnh.
#
# 5. ĐƠN VỊ
# Tọa độ của mình tính bằng mét, còn file IFC có thể dùng đơn vị khác (ví dụ milimét). Nên mọi
# tọa độ được chia cho hệ số đổi đơn vị của file (unit_scale) trước khi ghi.
#
# 6. GẮN PHÒNG VÀO TẦNG
# Mỗi IfcSpace được gắn vào tầng (IfcBuildingStorey) có cao độ cao nhất mà vẫn không cao hơn sàn
# phòng (cho phép lệch 0,3 mét).
#
# 7. BOUNDARY THEO TỪNG PHIÊN BẢN IFC
# - IFC2X3 chỉ có lớp IfcRelSpaceBoundary, nên mức 1 được ghi ở thuộc tính Description.
# - IFC4 có lớp riêng IfcRelSpaceBoundary1stLevel.
# Hình học tiếp xúc của boundary gồm các mặt của boundary, bọc trong IfcConnectionSurfaceGeometry.
# Lưu ý: ở IFC4, thuộc tính CorrespondingBoundary chỉ có ở IfcRelSpaceBoundary2ndLevel, không có
# ở IfcRelSpaceBoundary1stLevel. Vì file này chỉ ghi mức 1 nên không ghi cặp đối ứng ra file. Cặp
# đối ứng vẫn được ghép trong space_boundaries.py, để dùng khi làm mức 2.
#
# 8. LUỒNG CHẠY
# write_result -> remove_existing_spaces, add_space (gọi make_faceted_brep, pick_storey, ...),
# add_boundary.
# =====================================================================


logger = logging.getLogger(__name__)


def remove_existing_spaces(model):
    """Xóa mọi IfcRelSpaceBoundary và IfcSpace có sẵn trong model.

    Input:
        model: đối tượng model của IfcOpenShell. Bị sửa trực tiếp.
    Output:
        Không có.
    """
    for relation in model.by_type("IfcRelSpaceBoundary"):
        model.remove(relation)
    for space in model.by_type("IfcSpace"):
        # api.run("root.remove_product", ...): xóa phần tử cùng các quan hệ liên quan đến nó
        ifcopenshell.api.run("root.remove_product", model, product=space)


def make_face_entity(model, points: np.ndarray, unit_scale: float):
    """Tạo một IfcFace từ các đỉnh.

    Input:
        model: đối tượng model của IfcOpenShell. Thực thể mới được thêm vào đó.
        points: mảng numpy (n, 3), đỉnh của mặt theo thứ tự đi quanh viền, mét.
        unit_scale: hệ số đổi đơn vị của file ra mét (tọa độ được chia cho hệ số này).
    Output:
        Thực thể IfcFace có một viền ngoài đi qua n đỉnh.
    """
    # model.createIfcXxx(...): tạo thực thể IFC theo tên lớp, tham số theo thứ tự thuộc tính của
    # lớp đó. IfcPolyLoop nhận danh sách điểm; createIfcFaceOuterBound(vòng, True): True nghĩa là
    # chiều vòng đúng như đã khai báo.
    cartesian_points = [
        model.createIfcCartesianPoint([float(coordinate / unit_scale) for coordinate in point])
        for point in points
    ]
    loop = model.createIfcPolyLoop(cartesian_points)
    return model.createIfcFace([model.createIfcFaceOuterBound(loop, True)])


def make_faceted_brep(model, faces_points: list[np.ndarray], unit_scale: float):
    """Tạo một khối IfcFacetedBrep từ nhiều mặt.

    Input:
        model: đối tượng model của IfcOpenShell.
        faces_points: danh sách các mảng numpy (n, 3), mỗi mảng là đỉnh của một mặt (mét).
        unit_scale: hệ số đổi đơn vị của file ra mét.
    Output:
        Thực thể IfcFacetedBrep có vỏ kín gồm các mặt đó.
    """
    faces = [make_face_entity(model, points, unit_scale) for points in faces_points]
    return model.createIfcFacetedBrep(model.createIfcClosedShell(faces))


def oriented_for_space(face: AirFace) -> np.ndarray:
    """Đảo thứ tự đỉnh của một mảnh để vòng mặt có pháp tuyến hướng ra khỏi phòng.

    Input:
        face: AirFace có pháp tuyến hướng vào không khí (tức vào trong phòng).
    Output:
        Mảng numpy (n, 3), đỉnh của mảnh theo thứ tự sao cho pháp tuyến suy ra từ thứ tự đỉnh
        hướng ra khỏi phòng, đúng quy ước IFC cho khối.
    """
    area_vector = np.cross(face.points, np.roll(face.points, -1, axis=0)).sum(axis=0)
    if np.dot(area_vector, face.normal) > 0:
        # [::-1]: đảo ngược thứ tự các dòng
        return face.points[::-1]
    return face.points


def find_body_context(model):
    """Tìm ngữ cảnh hình học "Body" để gắn hình cho IfcSpace.

    Input:
        model: đối tượng model của IfcOpenShell.
    Output:
        Ngữ cảnh con "Body" nếu có, nếu không thì ngữ cảnh hình học đầu tiên của model.
    """
    for context in model.by_type("IfcGeometricRepresentationSubContext"):
        if context.ContextIdentifier == "Body":
            return context
    return model.by_type("IfcGeometricRepresentationContext")[0]


def pick_storey(model, floor_height: float, unit_scale: float):
    """Chọn tầng để gắn phòng vào.

    Input:
        model: đối tượng model của IfcOpenShell.
        floor_height: cao độ sàn phòng, mét.
        unit_scale: hệ số đổi đơn vị của file ra mét (để đổi cao độ của tầng ra mét).
    Output:
        IfcBuildingStorey có cao độ cao nhất mà vẫn không cao hơn floor_height + 0,3 m. Nếu
        không tầng nào như vậy thì lấy tầng thấp nhất. None nếu model không có tầng nào.
    """
    storeys = model.by_type("IfcBuildingStorey")
    if not storeys:
        return None

    def elevation_of(storey) -> float:
        """Input: một IfcBuildingStorey. Output: cao độ của tầng, mét (0 nếu không ghi)."""
        return (storey.Elevation or 0.0) * unit_scale

    below_floor = [s for s in storeys if elevation_of(s) <= floor_height + 0.3]
    if not below_floor:
        return min(storeys, key=elevation_of)
    return max(below_floor, key=elevation_of)


def add_space(model, candidate: SpaceCandidate, air_faces: list[AirFace], unit_scale: float):
    """Tạo một IfcSpace có hình học và gắn vào tầng.

    Input:
        model: đối tượng model của IfcOpenShell. Bị sửa trực tiếp.
        candidate: phòng ứng viên cần ghi.
        air_faces: danh sách AirFace (candidate.face_indices trỏ vào danh sách này).
        unit_scale: hệ số đổi đơn vị của file ra mét.
    Output:
        Thực thể IfcSpace vừa tạo, đã có Representation và đã được gắn vào tầng.
    """
    # api.run("root.create_entity", ...): tạo phần tử IFC kèm GlobalId và lịch sử sở hữu
    space = ifcopenshell.api.run(
        "root.create_entity", model, ifc_class="IfcSpace", name=candidate.name
    )

    faces_points = [oriented_for_space(air_faces[i]) for i in candidate.face_indices]
    brep = make_faceted_brep(model, faces_points, unit_scale)
    # IfcShapeRepresentation(context, "Body", "Brep", [hình]): "Body" là phần thân hình học,
    # "Brep" là loại biểu diễn (khối biên). IfcProductDefinitionShape(None, None, [biểu diễn]):
    # gói các biểu diễn để gắn vào phần tử.
    representation = model.createIfcShapeRepresentation(
        find_body_context(model), "Body", "Brep", [brep]
    )
    space.Representation = model.createIfcProductDefinitionShape(None, None, [representation])

    storey = pick_storey(model, candidate.floor_height, unit_scale)
    if storey is not None:
        # api.run("aggregate.assign_object", ...): gắn phần tử con vào phần tử cha (IfcSpace vào tầng)
        ifcopenshell.api.run(
            "aggregate.assign_object", model, products=[space], relating_object=storey
        )
    return space


def add_boundary(model, boundary, space, element, air_faces, unit_scale, owner_history):
    """Tạo một IfcRelSpaceBoundary (IFC2X3) hoặc IfcRelSpaceBoundary1stLevel (IFC4).

    Input:
        model: đối tượng model của IfcOpenShell. Bị sửa trực tiếp.
        boundary: SpaceBoundary cần ghi.
        space: IfcSpace của phòng (kết quả của add_space).
        element: phần tử IFC mà phòng tựa vào (tìm theo boundary.element_guid).
        air_faces: danh sách AirFace (boundary.face_indices trỏ vào danh sách này).
        unit_scale: hệ số đổi đơn vị của file ra mét.
        owner_history: IfcOwnerHistory dùng cho thực thể mới, hoặc None nếu file không có.
    Output:
        Thực thể quan hệ vừa tạo.
    """
    face_set = model.createIfcConnectedFaceSet(
        [make_face_entity(model, air_faces[i].points, unit_scale) for i in boundary.face_indices]
    )
    # IfcFaceBasedSurfaceModel: bề mặt gồm nhiều mặt; IfcConnectionSurfaceGeometry bọc nó thành
    # hình học tiếp xúc của boundary
    geometry = model.createIfcConnectionSurfaceGeometry(
        model.createIfcFaceBasedSurfaceModel([face_set]), None
    )

    values = dict(
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=owner_history,
        Name="1stLevel",
        RelatingSpace=space,
        RelatedBuildingElement=element,
        ConnectionGeometry=geometry,
        PhysicalOrVirtualBoundary="PHYSICAL",
        InternalOrExternalBoundary="EXTERNAL" if boundary.is_external else "INTERNAL",
    )

    if model.schema == "IFC2X3":
        values["Description"] = "1stLevel"
        # model.create_entity("Tên_lớp", **thuộc_tính): tạo thực thể và gán thuộc tính theo tên
        return model.create_entity("IfcRelSpaceBoundary", **values)

    values.pop("OwnerHistory") if owner_history is None else None
    return model.create_entity("IfcRelSpaceBoundary1stLevel", **values)


def write_result(
    source_path: str,
    output_path: str,
    candidates: list[SpaceCandidate],
    boundaries: list[SpaceBoundary],
    air_faces: list[AirFace],
):
    """Ghi kết quả ra một file IFC mới. Đây là hàm bên ngoài gọi.

    Input:
        source_path: đường dẫn file IFC gốc (mở lại để làm nền, không bị sửa).
        output_path: đường dẫn file IFC kết quả.
        candidates: danh sách phòng ứng viên.
        boundaries: danh sách SpaceBoundary.
        air_faces: danh sách AirFace.
    Output:
        File kết quả được ghi ra output_path, trong đó IfcSpace và boundary gốc đã bị xóa
        và thay bằng cái mới. Cặp đối ứng (CorrespondingBoundary) không được ghi ra file (xem
        mục 7 ở đầu file).
    """
    model = ifcopenshell.open(source_path)
    # calculate_unit_scale(model): hệ số đổi đơn vị dài của file ra mét (file dùng mm thì là 0.001)
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(model)

    remove_existing_spaces(model)
    owner_histories = model.by_type("IfcOwnerHistory")
    owner_history = owner_histories[0] if owner_histories else None

    spaces_by_name = {}
    for candidate in candidates:
        spaces_by_name[candidate.name] = add_space(model, candidate, air_faces, unit_scale)

    elements_by_guid = {}

    for boundary in boundaries:
        if boundary.element_guid not in elements_by_guid:
            # model.by_guid(guid): tìm phần tử theo GlobalId
            elements_by_guid[boundary.element_guid] = model.by_guid(boundary.element_guid)

        add_boundary(
            model,
            boundary,
            spaces_by_name[boundary.space_name],
            elements_by_guid[boundary.element_guid],
            air_faces,
            unit_scale,
            owner_history,
        )

    model.write(output_path)
    logger.info("Wrote %s", output_path)

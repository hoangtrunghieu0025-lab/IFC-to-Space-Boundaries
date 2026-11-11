import logging

import ifcopenshell
import ifcopenshell.geom
import numpy as np

# =====================================================================
# GIẢI THÍCH FILE: đọc file IFC và lấy hình dạng của từng phần tử bao dưới dạng lưới tam giác
#
# 1. Ý CHÍNH
# File IFC không lưu tường, sàn thành các tam giác mà lưu theo kiểu "công thức/tham số". Muốn cắt 
# và so sánh các bề mặt, mình cần hình dạng cụ thể. IfcOpenShell tính hình từ công thức đó ra thành 
# lưới tam giác. File này gọi IfcOpenShell cho từng tường, sàn, cửa... rồi gói kết quả lại để các 
# bước sau dùng.
#
# 2. LOẠI PHẦN TỬ ĐƯỢC CHỌN
# Chỉ những phần tử có thể bao quanh một không gian (tường, sàn, mái, cửa, cửa sổ, cột, dầm...)
# mới cần. IfcOpeningElement bị bỏ vì một nó là tham số mô tả hình dạng lỗ (liên kết với tường qua 
# IfcRelVoidsElement). Khi IfcOpenShell tính hình của IfcWall, mặc định nó trừ khối lỗ đó khỏi tường. 
# Kết quả là lưới của tường đã có sẵn cái lỗ và bốn mặt trong của lỗ (mặt trên, dưới, hai bên). 
# Các mặt đó đã thuộc về tường nên đã được đưa vào fuse.
#
# 3. TỌA ĐỘ CHUNG
# Mỗi phần tử IFC có hệ tọa độ riêng của nó. Nếu giữ nguyên thì tường và sàn nằm ở những gốc
# khác nhau, không thể biết chúng chạm nhau hay không. Nên mọi đỉnh được đổi sang một hệ tọa độ
# chung của cả công trình, đơn vị mét.
#
# 4. CHIỀU CỦA MỖI TAM GIÁC
# Mỗi tam giác ghi 3 đỉnh A, B, C theo một thứ tự, và thứ tự đó quyết định pháp tuyến hướng ra không khí
# hay vào vật rắn. Cần phân biệt rằng một bức tường 3D có độ dày thì thực chất nó là một khối lập 
# phương 6 mặt và có 2 mặt chính và 4 mặt nhỏ phụ. Mỗi mặt tường thì pháp tuyến có thể hướng một
# trong hai chiều. Một là hướng ra ngoài khoảng trống không khí, hai là đâm thẳng vào sâu trong 
# bề dày của tường tức là vật rắn . Quy ước (của chuẩn IFC, IfcOpenShell giữ nguyên): cuộn bốn ngón tay phải theo
# A -> B -> C, nếu ngón cái chỉ về phía người nhìn từ ngoài khối thì pháp tuyến hướng ra ngoài không khí. 
# Có thể kiểm tra lại bằng công thức tính thể tích có dấu của khối lưới. Nếu thể tích âm thì các tam giác đang hướng 
# vào trong vật rắn, cần đảo lại.
#
# 5. LUỒNG CHẠY
# read_element_meshes -> find_bounding_elements (chọn phần tử) -> build_element_mesh (tạo lưới
# cho từng phần tử) -> flip_if_inside_out (đảo nếu bị ghi ngược).
#
# 6. BIẾN QUAN TRỌNG
# - BOUNDING_ELEMENT_TYPES: các loại IFC có thể bao quanh một không gian.
# - ElementMesh: lưới của một phần tử, gồm:
#   + element: đối tượng IFC gốc.
#   + guid: GlobalId của phần tử.
#   + vertices: bảng N x 3, tọa độ (x, y, z) mét của N đỉnh.
#   + triangles: bảng M x 3, mỗi dòng là chỉ số (vào bảng vertices) của 3 đỉnh một tam giác.
# =====================================================================


logger = logging.getLogger(__name__)

BOUNDING_ELEMENT_TYPES = [
    "IfcWall",
    "IfcSlab",
    "IfcRoof",
    "IfcDoor",
    "IfcWindow",
    "IfcColumn",
    "IfcBeam",
    "IfcCurtainWall",
    "IfcPlate",
    "IfcMember",
]


class ElementMesh:
    def __init__(self, element, vertices, triangles):
        self.element = element
        self.guid = element.GlobalId
        self.vertices = vertices
        self.triangles = triangles


def load_model(ifc_path: str):
    return ifcopenshell.open(ifc_path)


def find_bounding_elements(model) -> list:
    """Gom mọi phần tử có thể bao quanh một không gian.

    Input:
        model: đối tượng model của IfcOpenShell (kết quả của load_model).
    Output:
        Danh sách phần tử IFC thuộc các loại trong BOUNDING_ELEMENT_TYPES, mỗi phần tử đúng một
        lần (không trùng dù thuộc nhiều loại cha con).
    """
    elements = []
    seen_ids = set()

    for type_name in BOUNDING_ELEMENT_TYPES:
        for element in model.by_type(type_name):
            # by_type đã gồm loại con nên IfcWallStandardCase nằm sẵn trong IfcWall
            if element.id() in seen_ids:
                continue
            seen_ids.add(element.id())
            elements.append(element)

    return elements


def build_element_mesh(element, settings) -> ElementMesh | None:
    """Tạo lưới tam giác cho một phần tử.

    Input:
        element: một phần tử IFC (ví dụ một IfcWall).
        settings: bộ tùy chọn hình học của IfcOpenShell (xem read_element_meshes).
    Output:
        ElementMesh của phần tử đó (vertices N x 3 mét, triangles M x 3 chỉ số đỉnh), hoặc None
        nếu phần tử không có hình học hoặc lưới rỗng.
    """
    try:
        # create_shape tính hình học của phần tử; ném RuntimeError nếu không có hình để tính
        shape = ifcopenshell.geom.create_shape(settings, element)
    except RuntimeError as error:
        logger.warning("No geometry for %s %s: %s", element.is_a(), element.GlobalId, error)
        return None

    # verts là mảng phẳng x,y,z,x,y,z...; faces là mảng phẳng chỉ số đỉnh, cứ 3 số là một tam giác.
    # reshape(-1, 3) gom thành bảng N dòng, 3 cột cho dễ đọc và xử lý.
    vertices = np.array(shape.geometry.verts, dtype=float).reshape(-1, 3)
    triangles = np.array(shape.geometry.faces, dtype=int).reshape(-1, 3)

    if len(triangles) == 0:
        return None

    return ElementMesh(element, vertices, triangles)


def read_element_meshes(model) -> list[ElementMesh]:
    """Đọc lưới tam giác của mọi phần tử bao trong mô hình. Đây là hàm bên ngoài gọi.

    Input:
        model: đối tượng model của IfcOpenShell (kết quả của load_model).
    Output:
        Danh sách ElementMesh, mỗi phần tử bao có hình học một cái, đỉnh theo tọa độ chung của
        công trình (mét). Phần tử không có hình bị bỏ; phần tử ghi ngược chiều đã được đảo lại.
    """
    settings = ifcopenshell.geom.settings()
    # use-world-coords: trả đỉnh theo tọa độ chung của công trình, không phải tọa độ riêng
    # của từng phần tử.
    settings.set("use-world-coords", True)

    meshes = []

    flipped_count = 0

    for element in find_bounding_elements(model):
        mesh = build_element_mesh(element, settings)
        if mesh is None:
            continue

        if flip_if_inside_out(mesh):
            flipped_count += 1
            logger.warning("Flipped normals of %s %s", element.is_a(), element.GlobalId)
        meshes.append(mesh)

    logger.info(
        "Read geometry of %d bounding elements, %d had flipped normals", len(meshes), flipped_count
    )
    return meshes


def signed_volume(mesh: ElementMesh) -> float:
    """Tính thể tích có dấu của một phần tử, để kiểm tra chiều các tam giác.

    Input:
        mesh: ElementMesh của một phần tử (lưới nên là vỏ kín).
    Output:
        Số thực, đơn vị m3. Dương: các tam giác hướng ra ngoài vật rắn (đúng). Âm: bị ghi ngược.
    """
    # Đánh chỉ số kiểu numpy: ra mảng (số tam giác, 3 đỉnh, 3 tọa độ).
    corners = mesh.vertices[mesh.triangles]
    # np.cross: cross product. einsum("ij,ij->"): dot product từng dòng rồi cộng kết quả của mọi
    # dòng. Thể tích có dấu là tổng a . (b x c) / 6 trên mọi tam giác (a, b, c là 3 đỉnh).
    return float(np.einsum("ij,ij->", corners[:, 0], np.cross(corners[:, 1], corners[:, 2])) / 6.0)


def flip_if_inside_out(mesh: ElementMesh) -> bool:
    """Đảo chiều các tam giác của một phần tử nếu chúng đang hướng vào trong vật rắn.

    Input:
        mesh: ElementMesh của một phần tử. Bị sửa trực tiếp (mesh.triangles) khi cần đảo.
    Output:
        True nếu đã đảo (thể tích có dấu âm), False nếu giữ nguyên.
    """
    if signed_volume(mesh) >= 0:
        return False

    # [:, [0, 2, 1]]: giữ mọi dòng, sắp lại 3 cột theo thứ tự 0, 2, 1 (đổi chỗ đỉnh thứ 2 và 3)
    mesh.triangles = mesh.triangles[:, [0, 2, 1]]
    return True

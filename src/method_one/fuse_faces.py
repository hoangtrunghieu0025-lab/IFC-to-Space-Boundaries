import logging
from dataclasses import dataclass

import numpy as np
from OCP.BOPAlgo import BOPAlgo_Builder
from OCP.BRep import BRep_Tool
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepTools import BRepTools, BRepTools_WireExplorer
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_VERTEX, TopAbs_WIRE
from OCP.TopLoc import TopLoc_Location
from OCP.TopExp import TopExp, TopExp_Explorer
from OCP.TopoDS import TopoDS

from read_elements import ElementMesh

# --------------------------------------------------------------------------------------
# GIẢI THÍCH FILE: cắt các bề mặt tại chỗ chúng giao nhau để tạo ra cạnh chung
#
# 1. Ý CHÍNH
# Hai bề mặt kề nhau thì mặt phẳng kéo dài của mỗi bề mặt cắt nhau theo một đường thẳng, và đoạn
# nằm trên cả hai bề mặt chính là cạnh chung của chúng.

# Nhưng theo cấu trúc dữ liệu IFC, mỗi tường, mỗi sàn là một vật thể riêng (IfcWall, IfcSlab), có
# hình học riêng và không chia sẻ mặt hay cạnh với vật khác. Nên ban đầu chưa có cạnh chung nào.

# File này tìm các đường giao rồi cắt các bề mặt dọc theo đường giao, để mép các mảnh vừa cắt trùng
# khít nhau và thành cạnh chung. Phải cắt vì một mặt lớn thường thuộc nhiều phòng: mặt trên của một
# tấm sàn có tường chia đôi là một mặt duy nhất chạm cả phòng A lẫn phòng B; cắt dọc chân tường thì
# mỗi mảnh chỉ thuộc một phòng. Có cạnh chung rồi mới xét được mảnh nào là hàng xóm của mảnh nào.

# Việc tìm giao và cắt do OpenCASCADE làm sẵn (phép General Fuse), mình chỉ đưa mặt (tất cả tam
# giác của mọi phần tử, mỗi tam giác là một mặt) vào và lấy mảnh ra.


# 2. MỖI BỀ MẶT LÀ MỘT TAM GIÁC
# IfcOpenShell chỉ đưa ra lưới tam giác. Hình dung một mặt tường là tờ giấy chữ nhật: nó bị cắt
# thành 2 tam giác rồi mới đưa cho mình, và mình dùng từng tam giác làm một bề mặt. Cái giá là số
# mặt nhiều nên fuse chậm. Cách tốt hơn (chưa làm): gom các tam giác đồng phẳng thành một đa giác
# trước khi fuse.
#
# 3. "MẶT" TRONG OPENCASCADE LÀ GÌ
# Nó dựng hình từ nhỏ đến lớn: vertex (một điểm) -> edge (đoạn nối hai vertex) -> wire (các edge
# nối thành đường viền khép kín) -> mặt (tấm phẳng bị giới hạn bởi wire). Khác với ba tọa độ thô,
# nó nhớ edge nào thuộc mặt nào, nên mới cắt và ghép cạnh chung được.
#
# 4. LUỒNG CHẠY
# make_source_faces (mỗi tam giác thành một mặt) -> fuse_source_faces (cắt tại chỗ giao)
# -> collect_fused_faces (lấy đỉnh từng mảnh, ghi nhớ mảnh thuộc phần tử IFC nào).
# fuse_meshes gọi cả chuỗi này.
#
# 5. BIẾN QUAN TRỌNG
# - FUZZY_TOLERANCE: hai điểm gần nhau trong khoảng này (mét) được coi là một.
# - MINIMUM_TRIANGLE_AREA: tam giác nhỏ hơn mức này bị bỏ (gần như một đường thẳng).

# - SourceFace: tam giác gốc, gồm 3 thứ:
#   + face: mặt OpenCASCADE dựng từ tam giác mà IfcOpenShell định nghĩa. Khác ba tọa
#     độ thô, mặt này nhớ edge nào thuộc mặt nào nên mới cắt và ghép cạnh chung được.
#   + element_guid: GlobalId của phần tử IFC gốc (IfcWall, IfcSlab...). Sau fuse mặt bị cắt thành
#     nhiều mảnh, mảnh nào cũng mang guid này nên biết mảnh thuộc phần tử nào.
#   + normal: pháp tuyến, vector vuông góc với bề mặt và hướng ra khỏi vật rắn, tức hướng vào
#     không khí. Chiều lấy từ thứ tự 3 đỉnh (IFC ghi ngược chiều kim đồng hồ khi nhìn từ ngoài vào),
#     ở read_elements.py có kiểm tra thể tích có dấu và đảo nếu bị ghi ngược. Dùng để biết phía nào
#     là không khí, nối mặt quanh cạnh, phân biệt phòng với bên ngoài, và loại mảnh kẹt giữa hai vật
#     rắn.
# - FusedFace: mảnh sau khi cắt = các đỉnh quanh mảnh + danh sách SourceFace mà nó được cắt ra.
# ------------------------------------------------------------------------------------------------------


logger = logging.getLogger(__name__)

FUZZY_TOLERANCE = 1e-4  # cùng giá trị IFC2SB dùng
MINIMUM_TRIANGLE_AREA = 1e-9


@dataclass
class FusedFace:
    points: np.ndarray
    sources: list


@dataclass
class SourceFace:
    face: object
    element_guid: str
    normal: np.ndarray  # hướng ra khỏi vật rắn, tức vào không khí


def make_triangle_face(corner_a, corner_b, corner_c):
    """Dựng một mặt OpenCASCADE hình tam giác từ 3 đỉnh.

    Input:
        corner_a, corner_b, corner_c: mỗi cái là mảng numpy gồm 3 số (x, y, z), đơn vị mét,
            theo tọa độ chung của công trình. Ba đỉnh là ba góc của một tam giác trong lưới.
    Output:
        Một mặt OpenCASCADE (TopoDS_Face) là tam giác phẳng đi qua 3 đỉnh đó,
        hoặc None nếu không dựng được (ví dụ ba điểm thẳng hàng).
    """
    # MakePolygon nối các điểm thành wire, True = đóng kín.
    polygon = BRepBuilderAPI_MakePolygon(
        gp_Pnt(*corner_a), gp_Pnt(*corner_b), gp_Pnt(*corner_c), True
    )
    if not polygon.IsDone():
        return None

    # MakeFace căng một mặt lên wire, True = chỉ nhận mặt phẳng.
    face_maker = BRepBuilderAPI_MakeFace(polygon.Wire(), True)
    if not face_maker.IsDone():
        return None
    return face_maker.Face()


def make_source_faces(meshes: list[ElementMesh]) -> list[SourceFace]:
    """Biến mọi tam giác của mọi phần tử thành mặt OpenCASCADE, kèm guid và pháp tuyến.

    Input:
        meshes: danh sách ElementMesh, mỗi cái là lưới của một phần tử IFC, gồm
            vertices (bảng N x 3 tọa độ đỉnh, mét), triangles (bảng M x 3 chỉ số đỉnh của
            từng tam giác) và guid (GlobalId của phần tử).
    Output:
        Danh sách SourceFace, mỗi tam giác hợp lệ cho một SourceFace gồm mặt OpenCASCADE,
        guid của phần tử chứa nó và pháp tuyến (vector đơn vị 3 số, tính từ thứ tự đỉnh).
        Tam giác nhỏ hơn MINIMUM_TRIANGLE_AREA hoặc không dựng được thì bị bỏ.
    """
    source_faces = []

    for mesh in meshes:
        corners = mesh.vertices[mesh.triangles]

        for corner_a, corner_b, corner_c in corners:
            cross = np.cross(corner_b - corner_a, corner_c - corner_a)
            area = np.linalg.norm(cross) / 2.0
            if area < MINIMUM_TRIANGLE_AREA:
                continue

            face = make_triangle_face(corner_a, corner_b, corner_c)
            if face is None:
                continue

            normal = cross / np.linalg.norm(cross)
            source_faces.append(SourceFace(face, mesh.guid, normal))

    logger.info("Built %d source faces", len(source_faces))
    return source_faces


def fuse_source_faces(source_faces: list[SourceFace]):
    """Đưa tất cả mặt vào OpenCASCADE cùng một lúc và chạy phép General Fuse.

    Input:
        source_faces: danh sách SourceFace từ make_source_faces (thường vài nghìn mặt cho một
            tòa nhà nhỏ).
    Output:
        Đối tượng BOPAlgo_Builder đã chạy xong. Nó chưa phải danh sách mảnh; muốn biết mỗi mặt
        gốc đã bị cắt thành những mảnh nào thì hỏi builder.Modified(mặt) (xem collect_fused_faces).
        Ném RuntimeError nếu OpenCASCADE báo lỗi. Bước này chậm, vài phút với cả tòa nhà.
    """
    # Sau bước này mọi giao cắt giữa hai mặt đều thành cạnh chung.
    builder = BOPAlgo_Builder()  # bộ máy General Fuse
    for source in source_faces:
        builder.AddArgument(source.face)

    builder.SetFuzzyValue(FUZZY_TOLERANCE)  # dung sai để coi hai điểm là một
    builder.SetRunParallel(True)
    builder.SetUseOBB(True)  # dùng hộp bao có hướng để lọc cặp mặt nhanh hơn
    builder.Perform()

    if builder.HasErrors():
        raise RuntimeError("General Fuse failed")

    return builder


def outer_wire_points(face) -> np.ndarray:
    """Lấy các đỉnh của wire ngoài của một mặt, theo thứ tự đi quanh viền.

    Input:
        face: một mặt OpenCASCADE (TopoDS_Face), thường là mảnh sau khi fuse.
    Output:
        Mảng numpy kích thước (n, 3): n đỉnh của viền ngoài, mỗi dòng là (x, y, z) mét,
        sắp xếp nối tiếp nhau. Lỗ trong mặt (wire trong) không được tính.
    """
    # Đỉnh của vòng ngoài theo thứ tự nối tiếp.
    # Hậu tố _s là hàm tĩnh: gọi trên lớp, không cần tạo đối tượng.
    wire = BRepTools.OuterWire_s(face)  # wire ngoài cùng của mặt (wire trong là lỗ)
    points = []

    # WireExplorer duyệt các edge của wire theo thứ tự nối tiếp: More() còn edge không,
    # Current() là edge hiện tại, Next() sang edge kế.
    wire_explorer = BRepTools_WireExplorer(wire, face)
    while wire_explorer.More():
        # FirstVertex_s(edge, True): vertex đầu của edge, True = tính cả hướng của edge
        vertex = TopExp.FirstVertex_s(wire_explorer.Current(), True)
        # Pnt_s(vertex) lấy điểm gp_Pnt của vertex
        point = BRep_Tool.Pnt_s(vertex)
        points.append([point.X(), point.Y(), point.Z()])
        wire_explorer.Next()

    return np.array(points)


def count_wires(face) -> int:
    """Đếm số wire của một mặt.

    Input:
        face: một mặt OpenCASCADE (TopoDS_Face).
    Output:
        Số nguyên: 1 nghĩa là mặt chỉ có viền ngoài, lớn hơn 1 nghĩa là mặt có lỗ
        (mỗi lỗ thêm một wire).
    """
    # TopExp_Explorer(hình, loại): duyệt mọi thành phần con thuộc loại đó (ở đây là wire).
    explorer = TopExp_Explorer(face, TopAbs_WIRE)
    count = 0
    while explorer.More():
        count += 1
        explorer.Next()
    return count


def vertex_key(face) -> frozenset:
    """Tạo khóa nhận dạng một mảnh theo tập đỉnh của nó.

    Input:
        face: một mảnh mặt OpenCASCADE (TopoDS_Face).
    Output:
        frozenset các bộ ba (x, y, z) đã làm tròn 6 chữ số thập phân, gồm mọi đỉnh của mảnh
        (kể cả đỉnh của lỗ). Hai mảnh có cùng khóa là cùng một mảnh, dù OpenCASCADE gán hướng khác
        nhau. Dùng được làm khóa của dict vì frozenset băm được.
    """
    # Cùng tập đỉnh là cùng một mảnh, bất kể OpenCASCADE gán hướng nào.
    corners = set()
    explorer = TopExp_Explorer(face, TopAbs_VERTEX)
    while explorer.More():
        # TopoDS.Vertex(): ép kiểu một hình bất kỳ thành vertex
        point = BRep_Tool.Pnt_s(TopoDS.Vertex(explorer.Current()))
        corners.add((round(point.X(), 6), round(point.Y(), 6), round(point.Z(), 6)))
        explorer.Next()
    return frozenset(corners)


def triangulate_face(face) -> list[np.ndarray]:
    """Chia một mặt (thường là mặt có lỗ) thành các tam giác.

    Input:
        face: một mặt OpenCASCADE (TopoDS_Face).
    Output:
        Danh sách các mảng numpy kích thước (3, 3): mỗi mảng là một tam giác gồm 3 đỉnh,
        mỗi đỉnh là (x, y, z) mét theo tọa độ chung. Danh sách rỗng nếu không chia được.
    """
    # Mặt có lỗ (mặt nhỏ nằm trọn trong mặt lớn đồng phẳng) không mô tả được bằng một vòng ngoài,
    # nên chia thành tam giác.
    # IncrementalMesh chia mặt thành tam giác, 0.1 là độ võng cho phép.
    BRepMesh_IncrementalMesh(face, 0.1)
    location = TopLoc_Location()
    # Triangulation_s lấy lưới vừa chia; location nhận phép dời hình của mặt.
    triangulation = BRep_Tool.Triangulation_s(face, location)
    if triangulation is None:
        return []

    transformation = location.Transformation()
    nodes = []
    for index in range(1, triangulation.NbNodes() + 1):
        # Node(i) và Triangle(i) đánh chỉ số từ 1; Transformed đưa điểm về tọa độ thật.
        point = triangulation.Node(index).Transformed(transformation)
        nodes.append([point.X(), point.Y(), point.Z()])

    triangles = []
    for index in range(1, triangulation.NbTriangles() + 1):
        # Get() trả 3 chỉ số node của tam giác (đếm từ 1, nên trừ 1 khi tra bảng nodes)
        first, second, third = triangulation.Triangle(index).Get()
        triangles.append(np.array([nodes[first - 1], nodes[second - 1], nodes[third - 1]]))
    return triangles


def polygons_of(face) -> list[np.ndarray]:
    """Trả về hình dạng của mặt dưới dạng danh sách đa giác.

    Input:
        face: một mảnh mặt OpenCASCADE (TopoDS_Face).
    Output:
        Danh sách các mảng numpy kích thước (n, 3) là đỉnh của từng đa giác. Mặt không có lỗ cho
        đúng một đa giác (viền ngoài, n đỉnh). Mặt có lỗ cho nhiều tam giác (n = 3 mỗi cái).
    """
    if count_wires(face) == 1:
        return [outer_wire_points(face)]
    return triangulate_face(face)


def collect_fused_faces(builder, source_faces: list[SourceFace]) -> list[FusedFace]:
    """Lấy các mảnh sau fuse ra và truy ngược mỗi mảnh về các mặt gốc.

    Input:
        builder: BOPAlgo_Builder đã chạy xong, lấy từ fuse_source_faces.
        source_faces: đúng danh sách SourceFace đã đưa vào builder đó.
    Output:
        Danh sách FusedFace. Mỗi FusedFace có points (mảng (n, 3) đỉnh của mảnh, mét) và sources
        (danh sách SourceFace mà mảnh được cắt ra, ít nhất 1). Có từ 2 nguồn trở lên khi nhiều mặt
        gốc cùng rơi vào một mảnh, ví dụ đáy tường nằm trên mặt sàn. Mảnh có lỗ được chia thành
        nhiều FusedFace dùng chung danh sách sources. Mảnh ít hơn 3 đỉnh bị bỏ.
    """
    # Hai mặt gốc rơi vào cùng một mảnh (vd mặt tường nằm trên mặt sàn) gộp thành một FusedFace.
    pieces_by_key = {}

    for source in source_faces:
        if builder.IsDeleted(source.face):
            continue

        # Modified(mặt): các mảnh được cắt ra từ mặt đó (rỗng nếu không bị cắt).
        pieces = [TopoDS.Face(piece) for piece in builder.Modified(source.face)]
        if not pieces:
            pieces = [source.face]

        for piece in pieces:
            key = vertex_key(piece)
            if key not in pieces_by_key:
                pieces_by_key[key] = (piece, [])
            pieces_by_key[key][1].append(source)

    fused_faces = []
    for piece, sources in pieces_by_key.values():
        for points in polygons_of(piece):
            if len(points) >= 3:
                fused_faces.append(FusedFace(points, sources))

    logger.info("General Fuse produced %d faces", len(fused_faces))
    return fused_faces


def fuse_meshes(meshes: list[ElementMesh]) -> list[FusedFace]:
    """Chạy cả chuỗi: dựng mặt, fuse, lấy mảnh ra. Đây là hàm bên ngoài gọi.

    Input:
        meshes: danh sách ElementMesh của mọi phần tử bao (kết quả của read_element_meshes).
    Output:
        Danh sách FusedFace như collect_fused_faces. Chậm vì có bước fuse (vài phút với cả tòa nhà),
        nên run_method_one.py cho phép lưu kết quả vào cache.
    """
    source_faces = make_source_faces(meshes)
    builder = fuse_source_faces(source_faces)
    return collect_fused_faces(builder, source_faces)

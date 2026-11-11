import logging
import math
from dataclasses import dataclass

import numpy as np

from fuse_faces import FusedFace

# =====================================================================
# GIẢI THÍCH FILE: chia các mảnh mặt phẳng thành từng nhóm, mỗi nhóm bao quanh một khối không khí
#
# 1. Ý CHÍNH
# Sau khi fuse, mình có hàng nghìn mảnh mặt phẳng chung cạnh với nhau. Một phòng là tập các mảnh cùng
# nhìn vào một khối không khí: mặt trong của các tường, sàn, trần... của phòng đó. File này chia
# các mảnh thành từng nhóm như vậy: hai mảnh cùng bao một khối không khí thì cho vào cùng nhóm.
#
# 2. MẶT NHÌN VỀ PHÍA KHÔNG KHÍ
# Mỗi mảnh có hai phía: một phía là vật rắn (thân tường), phía kia là không khí. Pháp tuyến chỉ
# về phía không khí. Mảnh nào kẹt giữa hai vật rắn (ví dụ đáy tường đặt trên sàn) không có phía
# nào là không khí, nên bị bỏ.
#
# 3. HAI MẢNH NÀO CÙNG BAO MỘT KHỐI KHÔNG KHÍ
# Hãy nhìn từ trên xuống, như bản vẽ mặt bằng. Một cạnh thẳng đứng là một chấm, mỗi mảnh tường
# đi qua chấm đó thành một đoạn thẳng. Chấm đó là bản lề, mỗi mảnh tường là một cánh cửa gắn vào
# bản lề. Lấy góc trong của một căn phòng: hai bức tường gặp nhau thành chữ L, không khí của
# phòng nằm trong chữ L. Đẩy cánh cửa A xoay quanh bản lề về phía không khí (phía pháp tuyến của
# A chỉ tới, không phải xuyên vào thân tường) cho tới khi chạm cánh B. Pháp tuyến không bị bẻ
# cong, nó chỉ cho biết xoay về phía nào. Khoảng quét giữa A và B là một góc không gian trống, ở đây là
# góc 90 độ của phòng. Pháp tuyến của B cũng quay vào góc không gian trống đó, nên A và B cùng bao khối không khí
# này và được nối lại.
# Nếu tại một cạnh có hơn hai mảnh gặp nhau (cạnh nối 3 tường), mảnh nào chạm đầu tiên khi
# quay từ A về phía không khí mới là hàng xóm của A. Nếu pháp tuyến của mảnh đó lại quay ra khỏi góc không gian trống
# (ví dụ do hai phần tử chồng lên nhau) thì không nối.
#
# 4. GOM NHÓM
# Mỗi cặp mảnh được nối thì cho vào cùng một nhóm. Làm xong mọi cạnh, các mảnh chia thành những
# nhóm; mỗi nhóm là mọi mảnh bao quanh một khối không khí.
#
# 5. NHÓM LÀ PHÒNG HAY BÊN NGOÀI
# Tính thể tích khối bao bởi nhóm từ chính các mặt của nó. Mỗi mặt cùng gốc tọa độ tạo thành một
# khối chóp, thể tích bằng 1/3 diện tích nhân khoảng cách từ gốc tới mặt (khoảng cách có dấu, đo
# theo pháp tuyến). Cộng lại:
#   V = (1/3) * tổng của [ (c . n) * S ] trên mọi mặt
# (c là tâm mặt, n là pháp tuyến, S là diện tích; "c . n" là dot product của c và n: nhân từng
# cặp tọa độ rồi cộng lại, ra một số).
# Pháp tuyến hướng vào trong khối thì V âm: đó là phòng. Pháp tuyến hướng ra ngoài thì V dương:
# đó là khối không khí bao ngoài công trình. (Công thức chỉ đúng khi nhóm là vỏ kín.)
#
# 6. CẠNH HỞ
# Mô hình thật hay có khe vài cm giữa các tường. Cạnh nào không tìm được mảnh kế tiếp là cạnh hở.
# open_ratio là tỉ lệ chiều dài cạnh hở trên tổng chiều dài cạnh của nhóm, để biết nhóm có
# gần kín hay không.
#
# 7. LUỒNG CHẠY
# make_air_faces -> link_faces_around_air, hàm này gọi group_faces_by_edge, rồi
# next_face_around_edge cho từng cạnh, nối bằng UnionFind, rồi tính signed_volume_of cho từng nhóm.
#
# 8. BIẾN QUAN TRỌNG
# - PARALLEL_TOLERANCE: ngưỡng để coi pháp tuyến của B là thật sự quay vào nêm không khí. Con số
#   đem so với ngưỡng là dot product của pháp tuyến B với hướng vào nêm.
# - COINCIDENT_ANGLE: góc (rad) nhỏ hơn mức này coi là hai mặt trùng nhau và bỏ qua.
# - EDGE_KEY_DIGITS: số chữ số thập phân khi làm tròn tọa độ để so khớp hai đầu cạnh.
# - AirFace: một mảnh mặt nhìn về phía không khí, gồm:
#   + points: bảng n x 3, đỉnh của mảnh (mét).
#   + normal: vector đơn vị hướng vào không khí.
#   + element_guids: GlobalId của các phần tử IFC mà mảnh thuộc về.
#   + area: diện tích (m2). centroid: tâm mảnh (3 số, mét).
# - FaceGroup: một nhóm mảnh, gồm:
#   + face_indices: vị trí các mảnh của nhóm trong danh sách AirFace.
#   + open_edge_length: tổng chiều dài cạnh hở (mét). edge_length: tổng chiều dài mọi cạnh (mét).
#   + signed_volume: thể tích tính ở mục 5 (m3), âm là phòng, dương là bao ngoài.
# =====================================================================


logger = logging.getLogger(__name__)

PARALLEL_TOLERANCE = 1e-3
COINCIDENT_ANGLE = 1e-6
EDGE_KEY_DIGITS = 6


@dataclass
class AirFace:

    points: np.ndarray
    normal: np.ndarray
    element_guids: list[str]
    area: float
    centroid: np.ndarray


@dataclass
class FaceGroup:
    """Một nhóm mảnh nối với nhau qua khối không khí mà chúng bao quanh (xem mục 8)."""

    face_indices: list[int]
    open_edge_length: float
    edge_length: float
    signed_volume: float

    # @property: gọi như thuộc tính (group.open_ratio), không cần ngoặc
    @property
    def open_ratio(self) -> float:
        """Tỉ lệ chiều dài cạnh hở trên tổng chiều dài cạnh, từ 0 (kín) đến 1 (hở hết)."""
        if self.edge_length == 0:
            return 1.0
        return self.open_edge_length / self.edge_length


def polygon_area_vector(points: np.ndarray) -> np.ndarray:
    """Tính vector diện tích của một đa giác phẳng.

    Input:
        points: mảng numpy (n, 3), đỉnh của đa giác theo thứ tự đi quanh viền, mét.
    Output:
        Mảng numpy 3 số. Độ dài bằng diện tích (m2), hướng vuông góc với đa giác, chiều theo
        quy tắc bàn tay phải của thứ tự đỉnh.
    """
    # np.roll(points, -1, axis=0): dịch các dòng lên một bậc, dòng đầu xuống cuối, nên ghép với
    # points ta được từng cặp (đỉnh, đỉnh kế). Tổng các tích có hướng của các cặp, chia 2, là
    # vector diện tích.
    following = np.roll(points, -1, axis=0)
    return np.cross(points, following).sum(axis=0) / 2.0


def make_air_faces(fused_faces: list[FusedFace]) -> list[AirFace]:
    """Đổi các mảnh sau fuse thành các mảnh nhìn về phía không khí, bỏ mảnh kẹt giữa hai vật rắn.

    Input:
        fused_faces: danh sách FusedFace từ fuse_faces.fuse_meshes. Mỗi cái có points (n, 3, mét)
            và sources (danh sách SourceFace, mỗi cái có normal là vector đơn vị).
    Output:
        Danh sách AirFace: points như đầu vào, normal lấy từ nguồn đầu tiên, element_guids đã
        sắp xếp và không trùng, area (m2), centroid là trung bình các đỉnh. Mảnh có nguồn
        pháp tuyến ngược nhau (kẹt giữa hai vật rắn) hoặc diện tích nhỏ hơn 1e-10 bị bỏ.
    """
    air_faces = []
    contact_faces = 0

    for fused in fused_faces:
        normals = np.array([source.normal for source in fused.sources])
        reference = normals[0]
        # @: nhân ma trận; ở đây ra tích của từng pháp tuyến với pháp tuyến đầu tiên
        directions = normals @ reference

        # Tường đặt trên sàn để lại mảnh có hai pháp tuyến ngược nhau: hai bên đều là vật rắn.
        if np.any(directions < 0):
            contact_faces += 1
            continue

        area_vector = polygon_area_vector(fused.points)
        # np.linalg.norm: độ dài của vector
        area = float(np.linalg.norm(area_vector))
        if area < 1e-10:
            continue

        guids = sorted({source.element_guid for source in fused.sources})
        # mean(axis=0): trung bình theo từng cột, tức tâm của các đỉnh
        air_faces.append(
            AirFace(fused.points, reference, guids, area, fused.points.mean(axis=0))
        )

    logger.info(
        "%d faces face the air, %d were contact faces between two solids",
        len(air_faces),
        contact_faces,
    )
    return air_faces


def edge_key(point_a: np.ndarray, point_b: np.ndarray):
    """Tạo khóa nhận dạng một cạnh, không phụ thuộc chiều đi.

    Input:
        point_a, point_b: mảng numpy 3 số (x, y, z), hai đầu của cạnh, mét.
    Output:
        Tuple (khóa_nhỏ, khóa_lớn). Mỗi khóa là tuple 3 số đã làm tròn EDGE_KEY_DIGITS chữ số.
        Cạnh đi từ A đến B và từ B đến A cho cùng một khóa, dùng được làm khóa của dict.
    """
    # np.round(x, n) làm tròn; tuple(...) để băm được (mảng numpy không dùng làm khóa dict được)
    key_a = tuple(np.round(point_a, EDGE_KEY_DIGITS))
    key_b = tuple(np.round(point_b, EDGE_KEY_DIGITS))
    return (key_a, key_b) if key_a <= key_b else (key_b, key_a)


def group_faces_by_edge(air_faces: list[AirFace]) -> dict:
    """Gom các mảnh theo từng cạnh chung.

    Input:
        air_faces: danh sách AirFace.
    Output:
        Dict: khóa cạnh (từ edge_key) -> danh sách các bộ ba (face_index, along, into_face).
        face_index là vị trí của mảnh trong air_faces. along là vector đơn vị dọc theo cạnh
        (3 số). into_face là vector đơn vị nằm trong mặt phẳng của mảnh, vuông góc với cạnh,
        chỉ từ cạnh vào phía thân mảnh. Một cạnh chung của k mảnh có k bộ ba. Cạnh ngắn hơn
        1e-9 bị bỏ.
    """
    faces_by_edge = {}

    for face_index, face in enumerate(air_faces):
        following_points = np.roll(face.points, -1, axis=0)

        # zip: duyệt song song từng cặp đỉnh liên tiếp (start, end) tức từng cạnh của mảnh
        for start, end in zip(face.points, following_points):
            along = end - start
            length = np.linalg.norm(along)
            if length < 1e-9:
                continue
            along = along / length

            to_centroid = face.centroid - (start + end) / 2.0
            # np.dot: tích chấm. Bỏ thành phần dọc cạnh, chỉ giữ phần vuông góc với cạnh.
            into_face = to_centroid - np.dot(to_centroid, along) * along
            norm = np.linalg.norm(into_face)
            if norm < 1e-12:
                continue
            into_face = into_face / norm

            key = edge_key(start, end)
            # setdefault(khóa, []): lấy danh sách của khóa, chưa có thì tạo danh sách rỗng
            faces_by_edge.setdefault(key, []).append((face_index, along, into_face))

    return faces_by_edge


def next_face_around_edge(face: AirFace, into_face: np.ndarray, neighbours: list, air_faces):
    """Tìm mảnh kế tiếp của một mảnh khi xoay quanh một cạnh về phía không khí.

    Nhìn dọc theo cạnh, mỗi mảnh là một nan xòe ra từ cạnh. Lấy into_face của mảnh hiện tại làm
    góc 0, quay về phía pháp tuyến (phía không khí). Nan đầu tiên gặp phải là mảnh kế tiếp.
    Khoảng giữa hai nan là một nêm không khí; mảnh kế tiếp chỉ hợp lệ nếu pháp tuyến của nó
    quay vào nêm đó.

    Input:
        face: AirFace hiện tại.
        into_face: vector đơn vị (3 số) hướng vào thân của face tại cạnh này (từ group_faces_by_edge).
        neighbours: các bộ ba (face_index, along, into_face) của các mảnh khác chung cạnh này.
        air_faces: toàn bộ danh sách AirFace, để tra mảnh theo vị trí.
    Output:
        Vị trí (số nguyên) của mảnh kế tiếp trong air_faces, hoặc None nếu không có mảnh nào
        khác, hoặc mảnh tìm được quay lưng với nêm không khí.
    """
    best_angle = None
    best_face_index = None

    for other_index, _, other_into_face in neighbours:
        x_part = np.dot(other_into_face, into_face)
        y_part = np.dot(other_into_face, face.normal)
        # atan2(y, x): góc của điểm (x, y) so với trục x, trong khoảng -pi đến pi.
        # % (2 * pi) đưa về khoảng 0 đến 2 pi, tức đo theo chiều quay về phía không khí.
        angle = math.atan2(y_part, x_part) % (2 * math.pi)

        if angle < COINCIDENT_ANGLE:
            continue
        if best_angle is None or angle < best_angle:
            best_angle = angle
            best_face_index = other_index

    if best_face_index is None:
        return None

    other = air_faces[best_face_index]
    # vector vuông góc với nan kế tiếp, chỉ về phía nêm (phía góc nhỏ hơn)
    wedge_side = math.sin(best_angle) * into_face - math.cos(best_angle) * face.normal
    if np.dot(other.normal, wedge_side) < PARALLEL_TOLERANCE:
        return None

    return best_face_index


class UnionFind:
    """Gộp các phần tử thành nhóm.

    Ban đầu mỗi phần tử một nhóm riêng. join(a, b) gộp nhóm chứa a và nhóm chứa b. find(x) trả
    về đại diện của nhóm chứa x; hai phần tử cùng nhóm thì có cùng đại diện.
    """

    def __init__(self, size: int):
        """Input: size là số phần tử, đánh số từ 0 đến size - 1."""
        self.parent = list(range(size))

    def find(self, item: int) -> int:
        """Input: item là vị trí một phần tử. Output: vị trí phần tử đại diện của nhóm chứa nó."""
        while self.parent[item] != item:
            # trỏ thẳng lên ông nội để các lần tìm sau nhanh hơn
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def join(self, first: int, second: int):
        """Input: hai vị trí phần tử. Output: không có, nhóm của hai phần tử được gộp lại."""
        self.parent[self.find(first)] = self.find(second)


def link_faces_around_air(air_faces: list[AirFace]) -> list[FaceGroup]:
    """Nối các mảnh cùng bao một khối không khí thành từng nhóm.

    Input:
        air_faces: danh sách AirFace từ make_air_faces.
    Output:
        Danh sách FaceGroup, mỗi mảnh thuộc đúng một nhóm. Mỗi nhóm có face_indices, tổng chiều dài
        cạnh hở và tổng chiều dài mọi cạnh (mét), và signed_volume (m3, âm là phòng, dương là
        bao ngoài). Cạnh hở là cạnh mà next_face_around_edge không tìm được mảnh kế tiếp.
    """
    faces_by_edge = group_faces_by_edge(air_faces)
    union_find = UnionFind(len(air_faces))
    open_length = np.zeros(len(air_faces))
    total_length = np.zeros(len(air_faces))

    for key, entries in faces_by_edge.items():
        length = float(np.linalg.norm(np.array(key[0]) - np.array(key[1])))

        for face_index, _, into_face in entries:
            others = [entry for entry in entries if entry[0] != face_index]
            next_index = next_face_around_edge(
                air_faces[face_index], into_face, others, air_faces
            )

            total_length[face_index] += length
            if next_index is None:
                open_length[face_index] += length
            else:
                union_find.join(face_index, next_index)

    members = {}
    for face_index in range(len(air_faces)):
        members.setdefault(union_find.find(face_index), []).append(face_index)

    groups = []
    for face_indices in members.values():
        # open_length[face_indices]: chỉ số kiểu danh sách, lấy các phần tử tại những vị trí đó
        groups.append(
            FaceGroup(
                face_indices,
                float(open_length[face_indices].sum()),
                float(total_length[face_indices].sum()),
                signed_volume_of(air_faces, face_indices),
            )
        )

    logger.info("Found %d groups of faces", len(groups))
    return groups


def signed_volume_of(air_faces: list[AirFace], face_indices: list[int]) -> float:
    """Tính thể tích khối bao bởi một nhóm mảnh (công thức ở mục 5 đầu file).

    Input:
        air_faces: toàn bộ danh sách AirFace.
        face_indices: vị trí các mảnh của một nhóm trong air_faces.
    Output:
        Số thực, m3. Pháp tuyến hướng vào trong nhóm thì ra số âm (phòng), hướng ra ngoài thì
        ra số dương (bao ngoài). Chính xác khi nhóm là vỏ kín.
    """
    total = 0.0
    for index in face_indices:
        face = air_faces[index]
        total += np.dot(face.centroid, face.normal) * face.area / 3.0
    return float(total)

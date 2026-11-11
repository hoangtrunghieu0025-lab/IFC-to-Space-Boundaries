import logging

import numpy as np

from face_graph import AirFace
from read_elements import ElementMesh

# =====================================================================
# GIẢI THÍCH FILE: loại các mảnh mặt phẳng nằm chìm bên trong một vật rắn khác
#
# 1. Ý CHÍNH
# Trong mô hình thật, tường hay chồng lên sàn, hai bức tường hay xuyên vào nhau. Sau khi fuse vẫn
# còn những mảnh mặt phẳng nằm chìm bên trong một vật rắn khác. Chúng không chạm không khí thật
# nên không được tham gia tìm phòng, nếu không sẽ làm nhiễu việc nối các mảnh. File này tìm và
# loại chúng.
#
# 2. HỎI "MẢNH NÀY CÓ BỊ CHÔN KHÔNG"
# Mỗi mảnh có pháp tuyến chỉ về phía được coi là không khí. Bước ra khỏi mảnh một đoạn rất nhỏ
# (PROBE_DISTANCE) theo pháp tuyến để có một điểm thử. Nếu điểm thử nằm trong một vật rắn khác
# thì phía "không khí" của mảnh thật ra là vật rắn, tức mảnh đang chìm, và bị bỏ.
#
# 3. LÀM SAO BIẾT MỘT ĐIỂM NẰM TRONG VẬT RẮN
# Điểm cần hỏi ở đây là điểm thử: tâm của một mảnh, lùi ra PROBE_DISTANCE (1 mm) theo pháp tuyến,
# tức một điểm sát mảnh ở phía được coi là không khí.
# Bắn một tia từ điểm đó theo một hướng cố định rồi đếm số lần tia xuyên qua bề mặt của vật rắn.
# Tia là nửa đường thẳng dài vô hạn về một phía, không phải một đoạn: code chỉ kiểm tra chỗ cắt
# nằm phía trước điểm bắn, không giới hạn độ xa.
# Vỏ của vật rắn là mặt kín chia không gian thành trong và ngoài, mỗi lần tia xuyên qua vỏ là đổi
# bên một lần. Tia đi mãi sẽ ra xa vô tận, nơi chắc chắn là bên ngoài. Nên xuất phát từ trong thì
# phải đổi bên một số lần lẻ mới ra ngoài (số lẻ nghĩa là điểm ở trong, đã đi vào mà chưa ra).
# Xuất phát từ ngoài thì đổi bên một số lần chẵn (số chẵn nghĩa là điểm ở ngoài: vào rồi ra, hoặc
# không chạm).
# Để nhanh, chỉ thử những vật rắn có hộp bao (hộp chữ nhật nhỏ nhất chứa vật đó) chứa điểm.
# Hai lưu ý: cách này chỉ đúng khi vỏ kín (lưới hở làm đếm sai), và tia trúng đúng cạnh tam giác
# có thể bị đếm sai, nên RAY_DIRECTION chọn hướng lẻ để hiếm khi trùng cạnh.
#
# 4. TIA CẮT MỘT TAM GIÁC KHI NÀO (thuật toán Moller-Trumbore)
# Lấy đỉnh V0 của tam giác làm gốc, hai cạnh e1 (V0 đến V1) và e2 (V0 đến V2) làm hai trục. Mọi
# điểm P trên mặt phẳng tam giác viết được là P = V0 + u·e1 + v·e2, (u, v) là tọa độ của P.
# V0 là (0, 0), V1 là (1, 0), V2 là (0, 1). P nằm trong tam giác khi u >= 0, v >= 0 (chưa vượt hai
# cạnh nằm trên hai trục) và u + v <= 1 (chưa vượt cạnh V1-V2, là đường u + v = 1).
# Chỗ tia chạm mặt phẳng là O + t·d (O là điểm bắn, d là hướng tia). Thuật toán giải t, u, v từ
# O + t·d = V0 + u·e1 + v·e2. Tia cắt tam giác khi u, v thỏa các điều kiện trên và t > 0 (chạm ở
# phía trước điểm bắn). Code tính cho mọi tam giác của một phần tử cùng lúc bằng numpy.
#
# 5. LUỒNG CHẠY
# remove_buried_faces -> SolidLookup (chuẩn bị hộp bao) -> contains (cho từng điểm thử) ->
# count_ray_hits (đếm số lần tia cắt từng phần tử).
#
# 6. BIẾN QUAN TRỌNG
# - PROBE_DISTANCE: khoảng bước ra khỏi mảnh (mét), phải lớn hơn dung sai fuse.
# - RAY_DIRECTION: hướng tia bắn thử, chọn số lẻ để hiếm khi chạy đúng dọc cạnh tam giác.
# - SolidLookup: giữ dữ liệu để hỏi "điểm này có nằm trong vật rắn nào không", gồm:
#   + corners: danh sách theo phần tử, mỗi cái là mảng (số tam giác, 3 đỉnh, 3 tọa độ).
#   + lower, upper: bảng N x 3, góc nhỏ nhất và lớn nhất của hộp bao N phần tử.
# =====================================================================


logger = logging.getLogger(__name__)

PROBE_DISTANCE = 1e-3

# Hướng lẻ để tia hiếm khi chạy đúng dọc cạnh.
RAY_DIRECTION = np.array([0.5773, 0.3141, 0.7552])
RAY_DIRECTION = RAY_DIRECTION / np.linalg.norm(RAY_DIRECTION)


def count_ray_hits(point: np.ndarray, corners: np.ndarray) -> int:
    """Đếm số tam giác của một phần tử mà tia bắn từ một điểm cắt phải.

    Input:
        point: mảng numpy 3 số (x, y, z), điểm bắn tia, mét. Tia đi theo RAY_DIRECTION.
        corners: mảng numpy (M, 3, 3): M tam giác của một phần tử, mỗi tam giác 3 đỉnh, mỗi đỉnh
            3 tọa độ, mét.
    Output:
        Số nguyên: số tam giác bị tia cắt ở phía trước điểm bắn.
    """
    # corners[:, 1]: đỉnh thứ hai (cột chỉ số 1) của mọi tam giác. Hai cạnh xuất phát từ đỉnh 0.
    edge_one = corners[:, 1] - corners[:, 0]
    edge_two = corners[:, 2] - corners[:, 0]

    p_vector = np.cross(RAY_DIRECTION, edge_two)
    # np.einsum("ij,ij->i", a, b): dot product từng dòng của hai bảng (mỗi dòng nhân từng cặp tọa
    # độ rồi cộng lại), ra một số cho mỗi dòng
    determinant = np.einsum("ij,ij->i", edge_one, p_vector)
    # gần 0 nghĩa là tia song song với mặt phẳng tam giác, không cắt được
    valid = np.abs(determinant) > 1e-12

    # np.where(điều_kiện, a, b): chọn a hoặc b theo từng phần tử; ở đây thay số 0 bằng 1 để
    # không chia cho 0 (kết quả của các tam giác không hợp lệ bị loại ở `hits`)
    safe_determinant = np.where(valid, determinant, 1.0)
    t_vector = point - corners[:, 0]
    u = np.einsum("ij,ij->i", t_vector, p_vector) / safe_determinant

    q_vector = np.cross(t_vector, edge_one)
    # @: nhân ma trận; ở đây, với mỗi dòng của q_vector, ra dot product với hướng tia
    v = (q_vector @ RAY_DIRECTION) / safe_determinant
    distance = np.einsum("ij,ij->i", edge_two, q_vector) / safe_determinant

    # &: "và" theo từng phần tử của các mảng đúng/sai. sum() đếm số giá trị đúng.
    hits = valid & (u >= 0) & (v >= 0) & (u + v <= 1) & (distance > 1e-9)
    return int(hits.sum())


class SolidLookup:
    """Trả lời câu hỏi "một điểm có nằm trong vật rắn nào không" cho một tập phần tử."""

    def __init__(self, meshes: list[ElementMesh]):
        """Input: meshes là danh sách ElementMesh của mọi phần tử bao (từ read_element_meshes)."""
        self.corners = [mesh.vertices[mesh.triangles] for mesh in meshes]
        # Hộp bao (bounding box) của một phần tử là hộp chữ nhật nhỏ nhất, các cạnh song song với trục
        # x, y, z, chứa trọn phần tử đó. Chỉ cần hai góc là mô tả được: góc thấp (lower) và góc cao
        # (upper). min(axis=0) / max(axis=0): nhỏ nhất / lớn nhất theo từng cột (x, y, z) của mọi đỉnh.
        self.lower = np.array([mesh.vertices.min(axis=0) for mesh in meshes])
        self.upper = np.array([mesh.vertices.max(axis=0) for mesh in meshes])

    def contains(self, point: np.ndarray) -> bool:
        """Kiểm tra một điểm có nằm trong vật rắn nào không.

        Input:
            point: mảng numpy 3 số (x, y, z), mét.
        Output:
            True nếu điểm nằm trong ít nhất một phần tử (tia cắt phần tử đó một số lẻ lần),
            False nếu không nằm trong phần tử nào. Chỉ thử những phần tử có hộp bao chứa điểm.
        """
        # np.all(..., axis=1): mọi cột trong mỗi dòng đều đúng, tức điểm nằm trong khoảng của cả
        # x, y, z. np.where(điều_kiện)[0]: lấy vị trí các phần tử thỏa điều kiện.
        candidates = np.where(
            np.all(point >= self.lower, axis=1) & np.all(point <= self.upper, axis=1)
        )[0]

        for index in candidates:
            if count_ray_hits(point, self.corners[index]) % 2 == 1:
                return True
        return False


def remove_buried_faces(air_faces: list[AirFace], meshes: list[ElementMesh]) -> list[AirFace]:
    """Bỏ các mảnh mặt phẳng nằm chìm bên trong một phần tử khác. Đây là hàm bên ngoài gọi.

    Input:
        air_faces: danh sách AirFace từ face_graph.make_air_faces.
        meshes: danh sách ElementMesh của mọi phần tử bao, dùng để biết điểm thử có nằm trong
            vật rắn không.
    Output:
        Danh sách con của air_faces: chỉ giữ những mảnh mà điểm thử (tâm mảnh lùi ra
        PROBE_DISTANCE theo pháp tuyến) không nằm trong vật rắn nào. Thứ tự giữ nguyên.
    """
    lookup = SolidLookup(meshes)
    visible_faces = []

    for face in air_faces:
        probe = face.centroid + face.normal * PROBE_DISTANCE
        if not lookup.contains(probe):
            visible_faces.append(face)

    logger.info("Removed %d buried faces", len(air_faces) - len(visible_faces))
    return visible_faces

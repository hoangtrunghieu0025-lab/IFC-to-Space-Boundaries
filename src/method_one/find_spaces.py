import logging
from dataclasses import dataclass

import numpy as np

from face_graph import AirFace, FaceGroup

# =====================================================================
# GIẢI THÍCH FILE: chọn nhóm mảnh mặt phẳng nào là phòng (IfcSpace ứng viên)
#
# 1. Ý CHÍNH
# face_graph.py đã chia các mảnh mặt phẳng thành từng nhóm, mỗi nhóm bao quanh một khối không khí.
# Nhưng không phải nhóm nào cũng là phòng: có nhóm là khối không khí bao ngoài công trình, có nhóm
# chỉ là khe hở hay hốc nhỏ trong tường. File này chọn ra các nhóm là phòng, và chọn thêm nhóm
# bao ngoài để các bước sau biết phần tử nào tiếp xúc với bên ngoài.
#
# 2. NHÓM NÀO LÀ PHÒNG
# Một nhóm là phòng khi thỏa cả ba điều kiện:
# - Thể tích âm (pháp tuyến hướng vào trong khối, xem mục 5 của face_graph.py).
# - Thể tích đủ lớn (MINIMUM_ROOM_VOLUME), để loại khe hở và hốc tường.
# - Gần như kín (open_ratio không quá MAXIMUM_OPEN_RATIO). Mô hình thật hay có khe vài cm giữa
#   các tường nên không đòi kín tuyệt đối.
# Nhóm bao ngoài là nhóm có thể tích dương và nhiều mảnh nhất.
#
# 3. ĐẶT TÊN VÀ SẮP XẾP
# Mỗi phòng được đặt tên "Space 01", "Space 02"... Phòng nằm thấp xếp trước (cao độ sàn là điểm
# thấp nhất của phòng, làm tròn 0,1 mét); cùng độ cao thì phòng có nhiều mảnh hơn xếp trước.
#
# 4. LUỒNG CHẠY
# find_space_candidates -> is_room (lọc từng nhóm) và find_exterior_group (tìm nhóm bao ngoài).
#
# 5. BIẾN QUAN TRỌNG
# - MINIMUM_ROOM_VOLUME: thể tích tối thiểu (m3) để nhóm được tính là phòng.
# - MAXIMUM_OPEN_RATIO: tỉ lệ chiều dài cạnh hở tối đa chấp nhận. Giá trị 5% do tôi chọn, chưa có
#   căn cứ nghiên cứu.
# - SpaceCandidate: một phòng ứng viên, gồm:
#   + name: tên phòng. face_indices: vị trí các mảnh của phòng trong danh sách AirFace.
#   + volume: thể tích (m3, số dương). floor_height: cao độ sàn (mét).
#   + open_ratio: tỉ lệ cạnh hở của nhóm (0 là kín hoàn toàn).
# =====================================================================


logger = logging.getLogger(__name__)

MINIMUM_ROOM_VOLUME = 1.0  # m3
MAXIMUM_OPEN_RATIO = 0.05


# @dataclass: tự sinh hàm __init__ từ các trường khai báo bên dưới
@dataclass
class SpaceCandidate:
    """Một phòng ứng viên (các trường xem mục 5 ở đầu file)."""

    name: str
    face_indices: list[int]
    volume: float
    floor_height: float
    open_ratio: float


def is_room(group: FaceGroup) -> bool:
    """Kiểm tra một nhóm mảnh có phải phòng không.

    Input:
        group: một FaceGroup từ face_graph.link_faces_around_air.
    Output:
        True nếu thể tích có dấu của nhóm nhỏ hơn -MINIMUM_ROOM_VOLUME (âm và đủ lớn) và tỉ lệ cạnh
        hở không quá MAXIMUM_OPEN_RATIO; ngược lại False.
    """
    # Pháp tuyến hướng vào phòng nên thể tích có dấu của phòng là số âm.
    return (
        group.signed_volume < -MINIMUM_ROOM_VOLUME
        and group.open_ratio <= MAXIMUM_OPEN_RATIO
    )


def find_exterior_group(groups: list[FaceGroup]) -> FaceGroup | None:
    """Tìm nhóm là khối không khí bao ngoài công trình.

    Input:
        groups: danh sách FaceGroup.
    Output:
        FaceGroup có thể tích dương và nhiều mảnh nhất, hoặc None nếu không nhóm nào có thể tích
        dương.
    """
    outside_groups = [group for group in groups if group.signed_volume > 0]
    if not outside_groups:
        return None
    # key=lambda ...: hàm cho biết lấy giá trị nào để so sánh (ở đây là số mảnh của nhóm)
    return max(outside_groups, key=lambda group: len(group.face_indices))


def find_space_candidates(
    groups: list[FaceGroup], air_faces: list[AirFace]
) -> tuple[list[SpaceCandidate], FaceGroup | None]:
    """Chọn các nhóm là phòng và nhóm bao ngoài. Đây là hàm bên ngoài gọi.

    Input:
        groups: danh sách FaceGroup từ face_graph.link_faces_around_air.
        air_faces: danh sách AirFace, dùng để tính cao độ sàn của từng phòng.
    Output:
        Một cặp (candidates, exterior). candidates là danh sách SpaceCandidate đã sắp xếp theo
        mục 3 ở đầu file; exterior là FaceGroup bao ngoài hoặc None nếu không có.
    """
    rooms = [group for group in groups if is_room(group)]

    def floor_height_of(group: FaceGroup) -> float:
        """Input: một FaceGroup. Output: cao độ z thấp nhất của mọi đỉnh trong nhóm, mét."""
        # points[:, 2]: cột chỉ số 2 (tọa độ z) của mọi đỉnh
        return min(air_faces[index].points[:, 2].min() for index in group.face_indices)

    # list.sort(key=...): sắp xếp theo khóa. Khóa là tuple nên so sánh từng phần tử một; dấu trừ
    # trước len(...) để nhóm nhiều mảnh hơn xếp trước.
    rooms.sort(key=lambda group: (round(floor_height_of(group), 1), -len(group.face_indices)))

    candidates = []
    # enumerate(rooms, start=1): vừa lấy phòng vừa đánh số, bắt đầu từ 1
    for number, group in enumerate(rooms, start=1):
        candidates.append(
            SpaceCandidate(
                # {number:02d}: số nguyên rộng 2 chữ số, thêm số 0 phía trước (1 thành 01)
                name=f"Space {number:02d}",
                face_indices=group.face_indices,
                volume=-group.signed_volume,
                floor_height=floor_height_of(group),
                open_ratio=group.open_ratio,
            )
        )

    exterior = find_exterior_group(groups)
    logger.info("Found %d space candidates", len(candidates))
    return candidates, exterior

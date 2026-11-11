import logging

import ifcopenshell
import ifcopenshell.geom
import numpy as np

from read_elements import ElementMesh, signed_volume

# =====================================================================
# GIẢI THÍCH FILE: so các phòng tìm được với IfcSpace gốc của file IFC
#
# 1. Ý CHÍNH
# File IFC đầu vào có thể đã có IfcSpace do người vẽ tạo. Coi chúng là đáp án gần đúng và xem các
# phòng thuật toán tìm được khớp với bao nhiêu phòng gốc. Chưa có cách so hình dạng chính xác
# (chưa đo IoU diện tích), nên ở đây chỉ so thể tích.
#
# 2. CÁCH GHÉP
# Duyệt các phòng tìm được từ lớn đến nhỏ. Mỗi phòng chọn IfcSpace gốc chưa được ghép có thể tích
# gần nhất; ghép được khi chênh lệch thể tích tương đối không quá DEFAULT_TOLERANCE VÀ cao độ sàn
# chênh không quá FLOOR_TOLERANCE_M (để không ghép nhầm hai phòng khác tầng có thể tích gần nhau).
# Đây vẫn là cách xấp xỉ: IfcSpace gốc thường được vẽ lệch so với mặt trong của tường nên thể tích
# không bao giờ khớp tuyệt đối, và hai phòng khác nhau trên cùng tầng vẫn có thể trùng thể tích.
#
# 3. BIẾN QUAN TRỌNG
# - DEFAULT_TOLERANCE: chênh lệch thể tích tương đối tối đa để coi là khớp (0,2 là 20%).
# - FLOOR_TOLERANCE_M: chênh lệch cao độ sàn tối đa để coi là khớp (mét).
# =====================================================================


logger = logging.getLogger(__name__)

DEFAULT_TOLERANCE = 0.2
FLOOR_TOLERANCE_M = 0.5


def original_spaces(ifc_path: str) -> list[dict]:
    """Đọc các IfcSpace gốc của file IFC và tính thể tích của từng cái.

    Input:
        ifc_path: đường dẫn file IFC gốc (chưa qua thuật toán).
    Output:
        Danh sách dict, mỗi IfcSpace một dict gồm: name (tên hoặc GlobalId), volume_m3 (số dương,
        hoặc None nếu không có hình học), floor_height_m (cao độ thấp nhất, hoặc None).
    """
    model = ifcopenshell.open(ifc_path)
    settings = ifcopenshell.geom.settings()
    settings.set("use-world-coords", True)

    spaces = []
    for space in model.by_type("IfcSpace"):
        entry = {
            "name": space.Name or space.GlobalId,
            "volume_m3": None,
            "floor_height_m": None,
        }
        try:
            shape = ifcopenshell.geom.create_shape(settings, space)
            vertices = np.array(shape.geometry.verts, dtype=float).reshape(-1, 3)
            triangles = np.array(shape.geometry.faces, dtype=int).reshape(-1, 3)
            if len(triangles) > 0:
                mesh = ElementMesh(space, vertices, triangles)
                entry["volume_m3"] = round(abs(signed_volume(mesh)), 3)
                entry["floor_height_m"] = round(float(vertices[:, 2].min()), 3)
        except RuntimeError as error:
            logger.warning("No geometry for original IfcSpace %s: %s", entry["name"], error)
        spaces.append(entry)

    return spaces


def match_rooms(found_rooms: list[dict], originals: list[dict], tolerance: float = DEFAULT_TOLERANCE):
    """Ghép các phòng tìm được với IfcSpace gốc theo thể tích và cao độ sàn.

    Input:
        found_rooms: danh sách phòng từ RunResult.rooms (mỗi phòng có name, volume_m3 và
            floor_height_m).
        originals: danh sách từ original_spaces.
        tolerance: chênh lệch thể tích tương đối tối đa để coi là khớp (cao độ sàn dùng
            FLOOR_TOLERANCE_M).
    Output:
        Dict gồm: matched (danh sách cặp: found, original, volume_diff là chênh lệch tương đối),
        unmatched_found (phòng tìm được không ghép được), unmatched_original (IfcSpace gốc có
        thể tích mà không được ghép), no_geometry (số IfcSpace gốc không có hình học).
    """
    candidates = [space for space in originals if space["volume_m3"]]
    no_geometry = len(originals) - len(candidates)

    matched = []
    unmatched_found = []

    # sorted(..., key=..., reverse=True): sắp xếp giảm dần theo thể tích
    for room in sorted(found_rooms, key=lambda room: room["volume_m3"], reverse=True):
        if not candidates:
            unmatched_found.append(room)
            continue

        # chỉ xét các IfcSpace gốc có cao độ sàn gần phòng này
        same_floor = [
            space for space in candidates
            if abs(room["floor_height_m"] - space["floor_height_m"]) <= FLOOR_TOLERANCE_M
        ]
        if not same_floor:
            unmatched_found.append(room)
            continue

        closest = min(same_floor, key=lambda space: abs(room["volume_m3"] - space["volume_m3"]))
        difference = abs(room["volume_m3"] - closest["volume_m3"]) / closest["volume_m3"]

        if difference <= tolerance:
            matched.append({"found": room, "original": closest, "volume_diff": round(difference, 3)})
            candidates.remove(closest)
        else:
            unmatched_found.append(room)

    return {
        "matched": matched,
        "unmatched_found": unmatched_found,
        "unmatched_original": candidates,
        "no_geometry": no_geometry,
    }

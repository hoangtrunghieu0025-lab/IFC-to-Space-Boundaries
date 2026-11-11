import logging
from dataclasses import dataclass, field

from face_graph import AirFace
from find_spaces import SpaceCandidate

# =====================================================================
# GIẢI THÍCH FILE: sinh boundary mức 1, tức ghi nhận "phòng này tựa vào phần tử nào"
#
# 1. Ý CHÍNH
# Có phòng rồi, còn phải nói rõ phòng đó được bao bởi những phần tử nào: bức tường nào, tấm sàn
# nào. Mỗi mối liên hệ như vậy là một boundary (IfcRelSpaceBoundary). Ở mức 1, mỗi cặp (phòng,
# phần tử) là một boundary, gồm mọi mảnh mặt phẳng của phòng thuộc phần tử đó. Ví dụ: tất cả các
# mảnh mặt trong của bức tường T quay vào phòng khách gộp thành một boundary giữa phòng khách và T.
#
# 2. BOUNDARY TRONG HAY NGOÀI
# Boundary là EXTERNAL nếu phần tử đó cũng có mảnh nằm trong nhóm bao ngoài (ví dụ tường ngoài vừa
# nhìn thấy phòng vừa nhìn thấy sân). Ngược lại là INTERNAL. Đây là cách xấp xỉ, chưa xét kỹ.
#
# 3. GHÉP CẶP ĐỐI ỨNG
# Bức tường nằm giữa hai phòng cho hai boundary, mỗi phòng một cái; hai boundary đó đối ứng với
# nhau. Chỉ ghép khi phần tử thấy đúng hai phòng khác nhau, các trường hợp phức tạp hơn (một
# phần tử thấy ba phòng trở lên) để không ghép cho khỏi sai.
#
# 4. LUỒNG CHẠY
# build_boundaries -> pair_corresponding_boundaries.
#
# 5. BIẾN QUAN TRỌNG
# - SpaceBoundary: một boundary, gồm:
#   + space_name: tên phòng. element_guid: GlobalId của phần tử IFC mà phòng tựa vào.
#   + face_indices: vị trí các mảnh thuộc boundary trong danh sách AirFace.
#   + area: tổng diện tích các mảnh (m2).
#   + is_external: True nếu tiếp xúc bên ngoài.
#   + corresponding: boundary đối ứng ở phòng bên kia, hoặc None.
# =====================================================================


logger = logging.getLogger(__name__)

@dataclass
class SpaceBoundary:
    """Một boundary mức 1 (các trường xem mục 5 ở đầu file)."""

    space_name: str
    element_guid: str
    face_indices: list[int]
    area: float
    is_external: bool = False
    corresponding: "SpaceBoundary | None" = field(default=None, repr=False)


def build_boundaries(
    candidates: list[SpaceCandidate],
    air_faces: list[AirFace],
    exterior_face_indices: list[int],
) -> list[SpaceBoundary]:
    """Tạo boundary mức 1 cho mọi phòng. Đây là hàm bên ngoài gọi.

    Input:
        candidates: danh sách SpaceCandidate từ find_spaces.find_space_candidates.
        air_faces: danh sách AirFace.
        exterior_face_indices: vị trí các mảnh của nhóm bao ngoài trong air_faces (danh sách rỗng
            nếu không có nhóm bao ngoài).
    Output:
        Danh sách SpaceBoundary, mỗi cặp (phòng, phần tử) một cái, đã ghép cặp đối ứng. Mảnh có
        nhiều phần tử cùng sở hữu (chồng nhau) chỉ được tính cho phần tử đầu tiên trong danh sách
        element_guids của mảnh.
    """
    # set.update(...): thêm nhiều phần tử vào tập hợp (tập hợp không giữ phần tử trùng)
    exterior_elements = set()
    for index in exterior_face_indices:
        exterior_elements.update(air_faces[index].element_guids)

    boundaries = []

    for candidate in candidates:
        faces_by_element = {}
        for index in candidate.face_indices:
            face = air_faces[index]
            # Mảnh chung của hai phần tử (chồng nhau) chỉ tính cho phần tử đầu.
            # setdefault(khóa, []): lấy danh sách của khóa, chưa có thì tạo danh sách rỗng
            faces_by_element.setdefault(face.element_guids[0], []).append(index)

        for element_guid, face_indices in faces_by_element.items():
            area = sum(air_faces[index].area for index in face_indices)
            boundaries.append(
                SpaceBoundary(
                    space_name=candidate.name,
                    element_guid=element_guid,
                    face_indices=face_indices,
                    area=area,
                    is_external=element_guid in exterior_elements,
                )
            )

    pair_corresponding_boundaries(boundaries)
    logger.info("Built %d boundaries", len(boundaries))
    return boundaries


def pair_corresponding_boundaries(boundaries: list[SpaceBoundary]):
    """Ghép các boundary đối ứng với nhau.

    Input:
        boundaries: danh sách SpaceBoundary. Bị sửa trực tiếp: thuộc tính corresponding của các
            boundary được ghép.
    Output:
        Không có. Hai boundary được ghép khi cùng một phần tử chỉ có đúng hai boundary và chúng
        thuộc hai phòng khác nhau.
    """
    boundaries_by_element = {}
    for boundary in boundaries:
        boundaries_by_element.setdefault(boundary.element_guid, []).append(boundary)

    for element_boundaries in boundaries_by_element.values():
        # Chỉ ghép khi không mơ hồ: phần tử thấy đúng hai phòng.
        if len(element_boundaries) != 2:
            continue

        first, second = element_boundaries
        if first.space_name == second.space_name:
            continue

        first.corresponding = second
        second.corresponding = first

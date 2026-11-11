"""Space boundaries từ IFC bằng đồ thị kề mặt (hướng 1).

Chạy từ thư mục gốc dự án:
    .venv/bin/python src/method_one/run_method_one.py samples/small/duplex-a.ifc out/duplex-a-method-one.ifc
"""
import argparse
import logging
import pickle
from pathlib import Path
from types import SimpleNamespace

from buried_faces import remove_buried_faces
from face_graph import link_faces_around_air, make_air_faces
from find_spaces import find_space_candidates
from fuse_faces import FusedFace, fuse_meshes
from read_elements import load_model, read_element_meshes
from space_boundaries import build_boundaries
from write_ifc import write_result

# =====================================================================
# GIẢI THÍCH FILE: chạy toàn bộ quy trình hướng 1, từ file IFC đến file IFC có IfcSpace mới
#
# 1. CÁC BƯỚC THEO THỨ TỰ
# 1) Đọc IFC, lấy lưới tam giác của các phần tử bao (read_elements).
# 2) Cắt các mặt tại chỗ giao nhau để có cạnh chung (fuse_faces).
# 3) Đổi sang các mảnh mặt phẳng nhìn về phía không khí (face_graph.make_air_faces).
# 4) Bỏ các mảnh chìm trong vật rắn khác (buried_faces).
# 5) Nối các mảnh cùng bao một khối không khí thành nhóm (face_graph.link_faces_around_air).
# 6) Chọn nhóm nào là phòng (find_spaces).
# 7) Sinh boundary mức 1 (space_boundaries).
# 8) Ghi file IFC mới (write_ifc).
#
# 2. CACHE KẾT QUẢ FUSE
# Bước 2 ở trên khi chạy sẽ khá chậm, vài phút với cả tòa nhà. Khi gỡ lỗi các bước sau, có thể lưu kết quả bước 2 ra
# một file (tham số --fuse-cache) để các lần chạy sau đọc lại mà không fuse lại. 

# 3. THAM SỐ DÒNG LỆNH
# - ifc_path: file IFC cần xử lý. output_path: file IFC kết quả.
# - --fuse-cache: đường dẫn file cache (không bắt buộc).
# =====================================================================


logger = logging.getLogger("method_one")


def load_or_fuse(meshes, cache_path: Path | None) -> list[FusedFace]:
    """Chạy bước fuse, hoặc đọc kết quả đã lưu nếu có cache.

    Input:
        meshes: danh sách ElementMesh từ read_element_meshes.
        cache_path: đường dẫn file cache, hoặc None nếu không dùng cache.
    Output:
        Danh sách FusedFace. Khi đọc từ cache, mỗi nguồn của mảnh chỉ có element_guid và normal
        (không có mặt OpenCASCADE).
    """
    if cache_path is not None and cache_path.exists():
        logger.info("Reusing fused faces from %s", cache_path)
        # đổi dãy byte về lại đối tượng Python. 
        rows = pickle.loads(cache_path.read_bytes())
        # SimpleNamespace(a=..., b=...): đối tượng đơn giản có thuộc tính a, b. Dùng thay cho
        # SourceFace vì mặt OpenCASCADE không lưu được bằng pickle.
        return [
            FusedFace(
                points,
                [SimpleNamespace(element_guid=guid, normal=normal) for guid, normal in sources],
            )
            for points, sources in rows
        ]

    fused_faces = fuse_meshes(meshes)

    if cache_path is not None:
        rows = [
            (fused.points, [(s.element_guid, s.normal) for s in fused.sources])
            for fused in fused_faces
        ]
        # đổi đối tượng Python thành dãy byte.
        cache_path.write_bytes(pickle.dumps(rows))
    return fused_faces


def main():
    """Đọc tham số dòng lệnh, chạy cả quy trình và in danh sách phòng tìm được.
    Input:
        Đọc từ dòng lệnh: ifc_path, output_path, và --fuse-cache tùy chọn.
    Output:
        Ghi file IFC kết quả ra output_path và in mỗi phòng một dòng:
        tên, thể tích (m3), cao độ sàn (m) và tỉ lệ cạnh hở. 
    """
    parser = argparse.ArgumentParser(description="Generate IfcSpace and space boundaries from IFC")
    parser.add_argument("ifc_path")
    parser.add_argument("output_path")
    parser.add_argument("--fuse-cache", type=Path, help="pickle file to keep the fuse result in")
    arguments = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    model = load_model(arguments.ifc_path)
    meshes = read_element_meshes(model)
    if not meshes:
        logger.error("No bounding elements with geometry were found in %s", arguments.ifc_path)
        return

    fused_faces = load_or_fuse(meshes, arguments.fuse_cache)
    air_faces = make_air_faces(fused_faces)
    air_faces = remove_buried_faces(air_faces, meshes)

    groups = link_faces_around_air(air_faces)
    candidates, exterior = find_space_candidates(groups, air_faces)
    exterior_faces = exterior.face_indices if exterior else []

    boundaries = build_boundaries(candidates, air_faces, exterior_faces)
    write_result(arguments.ifc_path, arguments.output_path, candidates, boundaries, air_faces)

    for candidate in candidates:
        print(
            f"{candidate.name}: volume {candidate.volume:7.2f} m3, "
            f"floor at {candidate.floor_height:5.2f} m, open edges {candidate.open_ratio:.1%}"
        )

if __name__ == "__main__":
    main()

"""Space boundaries từ IFC bằng đồ thị kề mặt (hướng 1).

Chạy từ thư mục gốc dự án:
    .venv/bin/python src/method_one/run_method_one.py samples/small/duplex-a.ifc out/duplex-a-method-one.ifc
"""
import argparse
import json
import logging
import pickle
import resource
import sys
import time
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

from buried_faces import remove_buried_faces
from compare_spaces import DEFAULT_TOLERANCE, FLOOR_TOLERANCE_M, match_rooms, original_spaces
from face_graph import link_faces_around_air, make_air_faces
from find_spaces import find_space_candidates
from fuse_faces import FusedFace, fuse_meshes
from read_elements import load_model, read_element_meshes
from run_report import write_report
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
# - ifc_path: file IFC cần xử lý.
# - output_path (không bắt buộc): file IFC kết quả; không đưa thì ghi vào thư mục chạy.
# - --run-dir (không bắt buộc): thư mục của lần chạy; không đưa thì tự tạo out/runs/<giờ>_<tên file>.
# - --fuse-cache: đường dẫn file cache của bước fuse (không bắt buộc).
# - -v / --verbose: hiện log chi tiết hơn. -q / --quiet: chỉ hiện cảnh báo và lỗi.
#
# 4. THƯ MỤC CỦA MỖI LẦN CHẠY
# Mỗi lần chạy đều tự tạo một thư mục chạy gồm:
# - run.log: toàn bộ log (tiếng Anh, có ngày giờ và mức INFO, WARNING...).
# - result.json: số liệu thô (thời gian từng bước, số mặt qua từng bước, danh sách phòng, RAM đỉnh,
#   kết quả so với IfcSpace gốc).
# - report.md: báo cáo đọc được, tự sinh từ mẫu templates/report.md (xem run_report.py).
# - file IFC kết quả (nếu không đưa output_path).
# Mỗi bước được đo thời gian và ghi một dòng "Step ... done in ... s"; cuối lần chạy in bảng tóm tắt.
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


@dataclass
class RunResult:
    """Số liệu của một lần chạy (các trường xem result.json và mục 4 ở đầu file)."""

    ifc_path: str
    output_path: str
    started_at: str
    schema: str
    original_space_count: int
    timings: dict
    counts: dict
    rooms: list
    comparison: dict | None
    peak_memory_mb: int


# @contextmanager: biến hàm có một `yield` thành khối `with`; code trước yield chạy lúc vào khối,
# code sau yield chạy lúc ra khỏi khối (kể cả khi có lỗi, nhờ finally)
@contextmanager
def timed_step(step_name: str, timings: dict):
    """Đo thời gian một bước, ghi vào timings và in một dòng log.

    Input:
        step_name: tên bước (khóa trong timings).
        timings: dict tên bước -> số giây. Được thêm một mục khi bước kết thúc.
    Output:
        Không có (dùng trong `with timed_step(...):`).
    """
    logger.info("Step %s started", step_name)
    start = time.perf_counter()
    try:
        yield
    finally:
        timings[step_name] = time.perf_counter() - start
        logger.info("Step %s done in %.1f s", step_name, timings[step_name])


def compare_with_original(ifc_path: str, rooms: list) -> dict | None:
    """So các phòng tìm được với IfcSpace gốc của file, không để lỗi ở đây làm hỏng cả lần chạy.

    Input:
        ifc_path: file IFC gốc.
        rooms: danh sách phòng của RunResult (mỗi phòng có name và volume_m3).
    Output:
        Dict kết quả của compare_spaces.match_rooms kèm khóa tolerance, hoặc None nếu so không được
        (lỗi được ghi vào log).
    """
    try:
        comparison = match_rooms(rooms, original_spaces(ifc_path), DEFAULT_TOLERANCE)
    except Exception:
        logger.exception("Could not compare with the original IfcSpace of %s", ifc_path)
        return None
    comparison["tolerance"] = DEFAULT_TOLERANCE
    comparison["floor_tolerance_m"] = FLOOR_TOLERANCE_M
    return comparison


def run_pipeline(ifc_path: str, output_path: str, fuse_cache: Path | None = None) -> RunResult:
    """Chạy cả quy trình trên một file IFC.

    Input:
        ifc_path: đường dẫn file IFC cần xử lý.
        output_path: đường dẫn file IFC kết quả.
        fuse_cache: đường dẫn file cache của bước fuse, hoặc None nếu không dùng cache.
    Output:
        RunResult của lần chạy. Ném ValueError nếu file không có phần tử bao nào có hình học.
    """
    timings = {}
    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with timed_step("read_ifc", timings):
        model = load_model(ifc_path)
        meshes = read_element_meshes(model)
    if not meshes:
        raise ValueError(f"No bounding elements with geometry were found in {ifc_path}")

    original_space_count = len(model.by_type("IfcSpace"))
    triangle_count = sum(len(mesh.triangles) for mesh in meshes)
    logger.info(
        "Schema %s, %d bounding elements, %d triangles, %d original IfcSpace",
        model.schema, len(meshes), triangle_count, original_space_count,
    )

    with timed_step("fuse", timings):
        fused_faces = load_or_fuse(meshes, fuse_cache)

    with timed_step("air_faces", timings):
        air_faces_all = make_air_faces(fused_faces)

    with timed_step("buried_faces", timings):
        air_faces = remove_buried_faces(air_faces_all, meshes)

    with timed_step("link_faces", timings):
        groups = link_faces_around_air(air_faces)

    with timed_step("find_spaces", timings):
        candidates, exterior = find_space_candidates(groups, air_faces)
        exterior_faces = exterior.face_indices if exterior else []

    with timed_step("boundaries", timings):
        boundaries = build_boundaries(candidates, air_faces, exterior_faces)

    with timed_step("write_ifc", timings):
        write_result(ifc_path, output_path, candidates, boundaries, air_faces)

    external_count = sum(1 for boundary in boundaries if boundary.is_external)
    counts = {
        "bounding_elements": len(meshes),
        "triangles": triangle_count,
        "fused_faces": len(fused_faces),
        "air_faces": len(air_faces_all),
        "buried_faces_removed": len(air_faces_all) - len(air_faces),
        "face_groups": len(groups),
        "rooms": len(candidates),
        "boundaries": len(boundaries),
        "boundaries_external": external_count,
        "boundaries_internal": len(boundaries) - external_count,
    }
    rooms = [
        {
            "name": candidate.name,
            "volume_m3": round(candidate.volume, 3),
            "floor_height_m": round(candidate.floor_height, 3),
            "open_ratio": round(candidate.open_ratio, 4),
            "face_count": len(candidate.face_indices),
        }
        for candidate in candidates
    ]

    comparison = None
    if original_space_count > 0:
        with timed_step("compare_spaces", timings):
            comparison = compare_with_original(ifc_path, rooms)

    # ru_maxrss: RAM đỉnh của tiến trình, tính bằng KB trên Linux
    peak_memory_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024

    return RunResult(
        ifc_path=ifc_path,
        output_path=output_path,
        started_at=started_at,
        schema=model.schema,
        original_space_count=original_space_count,
        timings=timings,
        counts=counts,
        rooms=rooms,
        comparison=comparison,
        peak_memory_mb=peak_memory_mb,
    )


def setup_logging(verbose: bool, quiet: bool, log_file: Path | None):
    """Cấu hình log: một handler ra terminal, một handler ra file nếu có.

    Input:
        verbose: True thì terminal hiện cả mức DEBUG.
        quiet: True thì terminal chỉ hiện WARNING trở lên.
        log_file: đường dẫn file log, hoặc None. File luôn ghi từ mức DEBUG, có ngày giờ đầy đủ.
    Output:
        Không có (cấu hình logger gốc).
    """
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    console = logging.StreamHandler()
    if quiet:
        console.setLevel(logging.WARNING)
    elif verbose:
        console.setLevel(logging.DEBUG)
    else:
        console.setLevel(logging.INFO)
    console.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s", "%H:%M:%S")
    )
    root.addHandler(console)

    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s")
        )
        root.addHandler(file_handler)


def print_summary(result: RunResult):
    """In bảng tóm tắt lần chạy ra terminal.

    Input:
        result: RunResult của lần chạy.
    Output:
        Không có (in ra màn hình): thời gian từng bước, số liệu chính và danh sách phòng.
    """
    total_seconds = sum(result.timings.values())
    print()
    print(f"=== Summary: {Path(result.ifc_path).name} ({result.schema}) ===")
    print("Timings:")
    for step_name, seconds in result.timings.items():
        print(f"  {step_name:<14} {seconds:8.1f} s")
    print(f"  {'total':<14} {total_seconds:8.1f} s   peak RAM {result.peak_memory_mb} MB")
    print("Counts:")
    for name, value in result.counts.items():
        print(f"  {name:<22} {value:>9}")
    print(f"  {'original IfcSpace':<22} {result.original_space_count:>9}")
    if result.comparison is not None:
        matched = len(result.comparison["matched"])
        print(f"  {'matched with original':<22} {matched:>9}  (volume within {result.comparison['tolerance']:.0%}, same floor)")
    print("Rooms:")
    for room in result.rooms:
        print(
            f"  {room['name']}: volume {room['volume_m3']:8.2f} m3, "
            f"floor at {room['floor_height_m']:6.2f} m, open edges {room['open_ratio']:.1%}"
        )


def default_run_dir(ifc_path: str) -> Path:
    """Tạo đường dẫn thư mục chạy mặc định out/runs/<giờ>_<tên file>.

    Input:
        ifc_path: đường dẫn file IFC.
    Output:
        Đường dẫn thư mục (chưa được tạo), tính từ thư mục đang đứng khi chạy lệnh.
    """
    stem = Path(ifc_path).stem.replace(" ", "-")
    return Path("out") / "runs" / f"{datetime.now():%Y-%m-%d_%H%M%S}_{stem}"


def main() -> int:
    """Đọc tham số dòng lệnh, chạy cả quy trình, ghi log, số liệu, báo cáo và in bảng tóm tắt.

    Input:
        Đọc từ dòng lệnh: ifc_path và các tham số tùy chọn (xem mục 3 ở đầu file).
    Output:
        Mã thoát: 0 nếu chạy xong, 1 nếu có lỗi (lỗi được ghi vào run.log). Trong thư mục chạy có
        run.log, result.json, report.md và file IFC kết quả (nếu không đưa output_path).
    """
    parser = argparse.ArgumentParser(description="Generate IfcSpace and space boundaries from IFC")
    parser.add_argument("ifc_path")
    # nargs="?": tham số theo vị trí này không bắt buộc, không đưa thì giá trị là None
    parser.add_argument("output_path", nargs="?", help="result IFC file (default: inside the run dir)")
    parser.add_argument("--run-dir", type=Path, help="folder for log, result.json and report.md")
    parser.add_argument("--fuse-cache", type=Path, help="pickle file to keep the fuse result in")
    # action="store_true": tham số không có giá trị, có mặt trên dòng lệnh thì bằng True
    parser.add_argument("-v", "--verbose", action="store_true", help="show debug messages")
    parser.add_argument("-q", "--quiet", action="store_true", help="show warnings and errors only")
    arguments = parser.parse_args()

    run_dir = arguments.run_dir or default_run_dir(arguments.ifc_path)
    run_dir.mkdir(parents=True, exist_ok=True)
    setup_logging(arguments.verbose, arguments.quiet, run_dir / "run.log")

    stem = Path(arguments.ifc_path).stem.replace(" ", "-")
    output_path = arguments.output_path or str(run_dir / f"{stem}-method-one.ifc")
    logger.info("Run folder: %s", run_dir)

    try:
        result = run_pipeline(arguments.ifc_path, output_path, arguments.fuse_cache)
    except Exception:
        # logger.exception ghi cả thông báo lỗi lẫn traceback vào log
        logger.exception("Pipeline failed for %s", arguments.ifc_path)
        return 1

    result_dict = asdict(result)
    # asdict: đổi dataclass thành dict; ensure_ascii=False giữ nguyên chữ có dấu
    (run_dir / "result.json").write_text(
        json.dumps(result_dict, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    report_path = write_report(result_dict, result.comparison, run_dir, result.started_at)
    logger.info("Report written to %s", report_path)

    print_summary(result)
    print(f"\nRun folder: {run_dir}")
    return 0


# Chỉ chạy main() khi file được chạy trực tiếp; nếu file khác import file này thì không tự chạy.
if __name__ == "__main__":
    sys.exit(main())

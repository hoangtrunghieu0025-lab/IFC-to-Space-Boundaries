import platform
import subprocess
from pathlib import Path
from string import Template

import ifcopenshell

# =====================================================================
# GIẢI THÍCH FILE: tự sinh báo cáo markdown cho một lần chạy từ mẫu templates/report.md
#
# 1. Ý CHÍNH
# Mỗi lần chạy pipeline cần một bản ghi dễ đọc: chạy file nào, mất bao lâu, ra bao nhiêu phòng, so
# với IfcSpace gốc thế nào. File này đổi số liệu của lần chạy (RunResult, dạng dict) thành các
# bảng markdown rồi điền vào mẫu. Mẫu để riêng thành file .md nên sửa hình thức báo cáo không cần
# sửa code.
#
# 2. MẪU BÁO CÁO
# templates/report.md có các chỗ điền dạng ${tên}. string.Template thay từng ${tên} bằng giá trị
# tương ứng. Các bảng được dựng sẵn bằng markdown_table rồi điền vào chỗ ${steps_table},
# ${counts_table}, ${comparison}, ${rooms_table}. Mục "Nhận xét" để trống cho người viết tay.
#
# 3. LUỒNG CHẠY
# write_report -> build_report (dựng các bảng, điền mẫu) -> ghi report.md vào thư mục chạy.
#
# 4. BIẾN QUAN TRỌNG
# - TEMPLATE_PATH: đường dẫn mẫu báo cáo.
# - COUNT_LABELS: tên tiếng Việt của từng số đếm trong RunResult.counts.
# - MAX_TABLE_ROWS: số dòng tối đa của bảng phòng và bảng ghép cặp trong báo cáo (đủ dòng thì
#   báo cáo ghi thêm "và N dòng khác", danh sách đầy đủ nằm trong result.json).
# =====================================================================


TEMPLATE_PATH = Path(__file__).parent / "templates" / "report.md"
MAX_TABLE_ROWS = 40

COUNT_LABELS = {
    "bounding_elements": "Phần tử bao có hình học",
    "triangles": "Tam giác đầu vào",
    "fused_faces": "Mảnh sau fuse",
    "air_faces": "Mảnh nhìn về phía không khí",
    "buried_faces_removed": "Mảnh chìm bị loại",
    "face_groups": "Nhóm mảnh",
    "rooms": "Phòng tìm được",
    "boundaries": "Boundary mức 1",
    "boundaries_external": "  trong đó EXTERNAL",
    "boundaries_internal": "  trong đó INTERNAL",
}


def markdown_table(headers: list[str], rows: list[list]) -> str:
    """Dựng một bảng markdown.

    Input:
        headers: danh sách tên cột.
        rows: danh sách dòng, mỗi dòng là danh sách giá trị (số hoặc chuỗi) cùng số cột với headers.
    Output:
        Chuỗi markdown của bảng. Nếu rows rỗng thì chỉ có dòng tiêu đề.
    """
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def git_commit_short() -> str:
    """Lấy mã commit ngắn của thư mục đang chạy, để biết báo cáo ứng với phiên bản code nào.

    Input:
        Không có.
    Output:
        Chuỗi mã commit ngắn, thêm "+chưa commit" nếu có thay đổi chưa commit; "không rõ" nếu
        không chạy được git.
    """
    try:
        # subprocess.run(lệnh, capture_output=True, text=True): chạy lệnh ngoài, lấy kết quả dạng chuỗi
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain", "--untracked-files=no"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "không rõ"
    return commit + ("+chưa commit" if dirty else "")


def format_comparison(comparison: dict | None, result: dict) -> str:
    """Viết phần so với IfcSpace gốc.

    Input:
        comparison: kết quả của compare_spaces.match_rooms (cộng thêm khóa tolerance), hoặc None
            nếu file không có IfcSpace gốc hoặc không so được.
        result: dict RunResult (cần original_space_count và rooms).
    Output:
        Chuỗi markdown: một dòng tóm tắt và bảng các cặp ghép được.
    """
    if comparison is None:
        return "File không có IfcSpace gốc để so sánh."

    matched = comparison["matched"]
    summary = (
        f"IfcSpace gốc: {result['original_space_count']} "
        f"(không có hình học: {comparison['no_geometry']}). "
        f"Phòng tìm được: {len(result['rooms'])}. "
        f"Ghép được: {len(matched)} (thể tích chênh không quá {comparison['tolerance']:.0%} "
        f"và cao độ sàn chênh không quá {comparison['floor_tolerance_m']} m). "
        f"Phòng tìm được không ghép được: {len(comparison['unmatched_found'])}. "
        f"IfcSpace gốc chưa có phòng tương ứng: {len(comparison['unmatched_original'])}."
    )

    rows = [
        [
            pair["found"]["name"],
            f"{pair['found']['volume_m3']:.2f}",
            pair["original"]["name"],
            f"{pair['original']['volume_m3']:.2f}",
            f"{pair['volume_diff']:.1%}",
        ]
        for pair in matched[:MAX_TABLE_ROWS]
    ]
    table = markdown_table(
        ["Phòng tìm được", "Thể tích (m3)", "IfcSpace gốc", "Thể tích gốc (m3)", "Chênh"], rows
    )
    if len(matched) > MAX_TABLE_ROWS:
        table += f"\n\n... và {len(matched) - MAX_TABLE_ROWS} cặp khác (xem result.json)."

    return summary + "\n\n" + table


def build_report(result: dict, comparison: dict | None, run_dir: Path, started_at: str) -> str:
    """Điền số liệu lần chạy vào mẫu báo cáo.

    Input:
        result: dict RunResult (khóa: ifc_path, schema, timings, counts, rooms, peak_memory_mb,
            original_space_count...).
        comparison: kết quả so với IfcSpace gốc (xem format_comparison), hoặc None.
        run_dir: thư mục của lần chạy (chỉ để ghi vào báo cáo).
        started_at: thời điểm bắt đầu, chuỗi dạng "2026-11-11 17:30:12".
    Output:
        Nội dung báo cáo (chuỗi markdown).
    """
    ifc_path = Path(result["ifc_path"])
    total_seconds = sum(result["timings"].values())

    steps_rows = [[name, f"{seconds:.1f}"] for name, seconds in result["timings"].items()]
    steps_rows.append(["**tổng**", f"**{total_seconds:.1f}**"])

    counts_rows = [
        [label, result["counts"][key]] for key, label in COUNT_LABELS.items() if key in result["counts"]
    ]
    counts_rows.append(["IfcSpace gốc", result["original_space_count"]])

    room_rows = [
        [
            room["name"],
            f"{room['volume_m3']:.2f}",
            f"{room['floor_height_m']:.2f}",
            f"{room['open_ratio']:.1%}",
            room["face_count"],
        ]
        for room in result["rooms"][:MAX_TABLE_ROWS]
    ]
    rooms_table = markdown_table(
        ["Phòng", "Thể tích (m3)", "Cao độ sàn (m)", "Cạnh hở", "Số mảnh"], room_rows
    )
    if len(result["rooms"]) > MAX_TABLE_ROWS:
        rooms_table += f"\n\n... và {len(result['rooms']) - MAX_TABLE_ROWS} phòng khác (xem result.json)."

    values = {
        "ifc_name": ifc_path.name,
        "started_at": started_at,
        "commit": git_commit_short(),
        "python_version": platform.python_version(),
        "ifcopenshell_version": ifcopenshell.version,
        "size_mb": round(ifc_path.stat().st_size / 1e6, 1) if ifc_path.exists() else "?",
        "schema": result["schema"],
        "run_dir": str(run_dir),
        "total_seconds": f"{total_seconds:.1f}",
        "peak_memory_mb": result["peak_memory_mb"],
        "steps_table": markdown_table(["Bước", "Giây"], steps_rows),
        "counts_table": markdown_table(["Chỉ số", "Giá trị"], counts_rows),
        "comparison": format_comparison(comparison, result),
        "rooms_table": rooms_table,
    }
    # Template.substitute: thay mọi ${tên} trong mẫu bằng values["tên"]; thiếu khóa thì báo lỗi
    return Template(TEMPLATE_PATH.read_text(encoding="utf-8")).substitute(values)


def write_report(result: dict, comparison: dict | None, run_dir: Path, started_at: str) -> Path:
    """Sinh báo cáo và ghi thành report.md trong thư mục chạy.

    Input:
        result, comparison, run_dir, started_at: như build_report.
    Output:
        Đường dẫn file report.md vừa ghi.
    """
    report_path = run_dir / "report.md"
    report_path.write_text(build_report(result, comparison, run_dir, started_at), encoding="utf-8")
    return report_path

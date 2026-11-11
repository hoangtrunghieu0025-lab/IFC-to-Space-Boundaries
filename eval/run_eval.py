"""Chạy pipeline hướng 1 lần lượt trên nhiều file IFC rồi gom một bảng tổng.

Chạy từ thư mục gốc dự án:
    .venv/bin/python eval/run_eval.py                     # mọi ca trong eval/cases.json
    .venv/bin/python eval/run_eval.py --only duplex-a     # chỉ một vài ca
    .venv/bin/python eval/run_eval.py --list              # chỉ liệt kê, không chạy
"""
import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from string import Template

# =====================================================================
# GIẢI THÍCH FILE: chạy hàng loạt các file IFC thử nghiệm và gom kết quả vào một bảng tổng
#
# 1. Ý CHÍNH
# Pipeline (src/method_one/run_method_one.py) tự tạo báo cáo cho từng file. File này chỉ lo việc
# chạy nhiều file liên tiếp theo danh sách trong cases.json, rồi gom các kết quả riêng lẻ vào một
# bảng tổng để so sánh các file với nhau.
#
# 2. MỖI CA CHẠY TRONG MỘT TIẾN TRÌNH RIÊNG
# Mỗi file IFC được chạy bằng một lệnh con (subprocess) có thời gian chờ tối đa (timeout_minutes
# trong cases.json). Làm vậy để một file nặng treo hoặc hết RAM thì chỉ ca đó bị dừng, các ca còn
# lại vẫn chạy tiếp, và RAM của ca này được trả lại hệ điều hành trước khi sang ca sau.
#
# 3. KẾT QUẢ
# out/eval/<mã lần chạy>/
#   summary.md, summary.json   bảng tổng của cả lần chạy (mẫu: eval/templates/summary.md)
#   <mã ca>/                   thư mục chạy của từng ca (run.log, result.json, report.md, file IFC)
# Thư mục out/ đã được bỏ qua trong .gitignore nên kết quả không bị commit nhầm.
#
# 4. BIẾN QUAN TRỌNG
# - cases.json: danh sách ca (id, title, ifc là đường dẫn tính từ thư mục eval/, timeout_minutes
#   là thời gian chờ tối đa của ca đó) và default_timeout_minutes.
# - Trạng thái một ca: ok (chạy xong), failed (pipeline báo lỗi), timeout (quá thời gian chờ).
# =====================================================================


EVAL_DIR = Path(__file__).resolve().parent
REPO_ROOT = EVAL_DIR.parent
PIPELINE_SCRIPT = REPO_ROOT / "src" / "method_one" / "run_method_one.py"
RESULTS_ROOT = REPO_ROOT / "out" / "eval"
SUMMARY_TEMPLATE = EVAL_DIR / "templates" / "summary.md"


def load_cases(cases_path: Path, only_ids: list[str] | None) -> tuple[list[dict], int]:
    """Đọc danh sách ca từ cases.json.

    Input:
        cases_path: đường dẫn cases.json.
        only_ids: danh sách mã ca cần chạy, hoặc None để chạy tất cả.
    Output:
        Cặp (cases, default_timeout_minutes). Mỗi ca là một dict của file JSON. Ném ValueError
        nếu một mã trong only_ids không có trong file.
    """
    data = json.loads(cases_path.read_text(encoding="utf-8"))
    cases = data["cases"]

    if only_ids is not None:
        known_ids = {case["id"] for case in cases}
        unknown = [case_id for case_id in only_ids if case_id not in known_ids]
        if unknown:
            raise ValueError(f"Unknown case id(s): {', '.join(unknown)}")
        cases = [case for case in cases if case["id"] in only_ids]

    return cases, data.get("default_timeout_minutes", 60)


def run_case(case: dict, run_dir: Path, default_timeout_minutes: int, reuse_fuse: bool) -> dict:
    """Chạy pipeline trên một ca bằng một tiến trình con.

    Input:
        case: một ca trong cases.json.
        run_dir: thư mục của cả lần đánh giá; thư mục của ca nằm trong đó.
        default_timeout_minutes: thời gian chờ mặc định nếu ca không ghi timeout_minutes.
        reuse_fuse: True thì dùng cache của bước fuse (lưu ở out/eval/cache/<mã ca>.pkl).
    Output:
        Dict của ca: id, title, ifc, status (ok, failed hoặc timeout), wall_seconds, case_dir,
        result (nội dung result.json, hoặc None nếu không có).
    """
    case_dir = run_dir / case["id"]
    ifc_path = (EVAL_DIR / case["ifc"]).resolve()
    timeout_minutes = case.get("timeout_minutes", default_timeout_minutes)

    command = [
        sys.executable, str(PIPELINE_SCRIPT), str(ifc_path),
        "--run-dir", str(case_dir), "--quiet",
    ]
    if reuse_fuse:
        cache_path = RESULTS_ROOT / "cache" / f"{case['id']}.pkl"
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        command += ["--fuse-cache", str(cache_path)]

    print(f"[{case['id']}] running (timeout {timeout_minutes} min) ...", flush=True)
    started = time.perf_counter()
    try:
        # timeout=giây: quá thời gian thì ném TimeoutExpired và tiến trình con bị dừng
        completed = subprocess.run(
            command, cwd=REPO_ROOT, capture_output=True, text=True, timeout=timeout_minutes * 60
        )
        status = "ok" if completed.returncode == 0 else "failed"
    except subprocess.TimeoutExpired:
        status = "timeout"
    wall_seconds = time.perf_counter() - started

    result_path = case_dir / "result.json"
    result = None
    if status == "ok" and result_path.exists():
        result = json.loads(result_path.read_text(encoding="utf-8"))

    print(f"[{case['id']}] {status} in {wall_seconds:.0f} s", flush=True)
    return {
        "id": case["id"],
        "title": case["title"],
        "ifc": case["ifc"],
        "status": status,
        "wall_seconds": round(wall_seconds, 1),
        "case_dir": str(case_dir.relative_to(REPO_ROOT)),
        "result": result,
    }


def summary_row(outcome: dict) -> list:
    """Dựng một dòng của bảng tổng cho một ca.

    Input:
        outcome: dict do run_case trả về.
    Output:
        Danh sách giá trị theo thứ tự cột của bảng tổng: ca, trạng thái, thời gian, RAM, số phần
        tử, số phòng tìm được, số IfcSpace gốc, số phòng ghép được. Ca không chạy xong thì các
        cột số liệu là dấu gạch ngang.
    """
    result = outcome["result"]
    if result is None:
        return [outcome["id"], outcome["status"], f"{outcome['wall_seconds']:.0f}", "-", "-", "-", "-", "-"]

    comparison = result["comparison"]
    matched = len(comparison["matched"]) if comparison else "-"
    return [
        outcome["id"],
        outcome["status"],
        f"{outcome['wall_seconds']:.0f}",
        result["peak_memory_mb"],
        result["counts"]["bounding_elements"],
        result["counts"]["rooms"],
        result["original_space_count"],
        matched,
    ]


def write_summary(outcomes: list[dict], run_id: str, started_at: str, run_dir: Path):
    """Ghi bảng tổng summary.md và summary.json của cả lần đánh giá.

    Input:
        outcomes: danh sách dict do run_case trả về.
        run_id: mã lần đánh giá (dùng làm tên thư mục).
        started_at: thời điểm bắt đầu, chuỗi dạng "2026-11-11 17:30:12".
        run_dir: thư mục của lần đánh giá.
    Output:
        Không có (ghi hai file vào run_dir).
    """
    headers = ["Ca", "Trạng thái", "Giây", "RAM đỉnh (MB)", "Phần tử", "Phòng tìm được", "IfcSpace gốc", "Ghép được"]
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for outcome in outcomes:
        lines.append("| " + " | ".join(str(value) for value in summary_row(outcome)) + " |")

    links = "\n".join(
        f"- `{outcome['id']}`: {outcome['title']}, báo cáo chi tiết ở `{outcome['case_dir']}/report.md`"
        for outcome in outcomes
    )
    # Template.substitute: thay mọi ${tên} trong mẫu bằng giá trị tương ứng
    text = Template(SUMMARY_TEMPLATE.read_text(encoding="utf-8")).substitute(
        run_id=run_id,
        started_at=started_at,
        summary_table="\n".join(lines),
        case_links=links,
    )
    (run_dir / "summary.md").write_text(text, encoding="utf-8")
    (run_dir / "summary.json").write_text(
        json.dumps(outcomes, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def main() -> int:
    """Đọc tham số dòng lệnh, chạy các ca và ghi bảng tổng.

    Input:
        Đọc từ dòng lệnh: --cases, --only, --reuse-fuse, --list.
    Output:
        Mã thoát: 0 nếu mọi ca chạy xong, 1 nếu có ca lỗi hoặc quá thời gian chờ, 2 nếu tham số sai.
    """
    parser = argparse.ArgumentParser(description="Run method one on several IFC test files")
    parser.add_argument("--cases", type=Path, default=EVAL_DIR / "cases.json")
    parser.add_argument("--only", help="comma separated case ids to run")
    parser.add_argument("--reuse-fuse", action="store_true", help="cache the fuse step per case")
    parser.add_argument("--list", action="store_true", help="list the cases and exit")
    arguments = parser.parse_args()

    only_ids = arguments.only.split(",") if arguments.only else None
    try:
        cases, default_timeout = load_cases(arguments.cases, only_ids)
    except ValueError as error:
        print(error)
        return 2

    if arguments.list:
        for case in cases:
            print(f"{case['id']:<22} {case['ifc']}  (timeout {case.get('timeout_minutes', default_timeout)} min)")
        return 0

    started = datetime.now()
    run_id = started.strftime("%Y-%m-%d_%H%M%S")
    run_dir = RESULTS_ROOT / run_id
    run_dir.mkdir(parents=True)

    outcomes = [run_case(case, run_dir, default_timeout, arguments.reuse_fuse) for case in cases]
    write_summary(outcomes, run_id, started.strftime("%Y-%m-%d %H:%M:%S"), run_dir)

    print(f"\nSummary: {run_dir / 'summary.md'}")
    return 0 if all(outcome["status"] == "ok" for outcome in outcomes) else 1


if __name__ == "__main__":
    sys.exit(main())

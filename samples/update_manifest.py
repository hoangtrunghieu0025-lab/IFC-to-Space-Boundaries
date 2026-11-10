#!/usr/bin/env python3
"""Đo lại các file trong `samples/manifest.yaml` bằng `inspect_ifc.py` và ghi kết quả vào manifest.

Phần nhập tay (nguồn, URL, giấy phép, license_class, building_class, notes…) giữ nguyên.
Script ghi đè `sha256`, `tier` và khối `measured` / `score` cho các file đang có trên đĩa.

    python3 samples/update_manifest.py                 # đo mọi file có trên đĩa
    python3 samples/update_manifest.py --id duplex-a   # đo một file
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MANIFEST = os.path.join(HERE, "manifest.yaml")
sys.path.insert(0, HERE)
from inspect_ifc import score  # noqa: E402

HEADER = """\
# Danh mục bộ IFC test (TASK-001). Sinh/cập nhật bằng samples/update_manifest.py;
# phần nhập tay (source, url, license, license_class, building_class, notes) sửa trực tiếp.
# Tải lại: python3 samples/fetch_datasets.py   (xem samples/README.md)
# Tiêu chí & thang điểm: research/04-datasets-and-validation/dataset-quality-criteria.md
"""

KEEP = ["n_storeys", "n_spaces", "n_spaces_with_rep", "n_spaces_in_storey", "n_rsb", "n_rsb_1st_class",
        "n_rsb_2nd_class", "n_rsb_name_2ndlevel", "n_rsb_with_geom", "n_rsb_virtual", "n_rsb_external",
        "n_rsb_with_corresponding", "rsb_level_labels", "n_products", "n_zones", "counts", "length_unit",
        "geom_ok_ratio_elements", "geom_tested_elements", "n_elements_without_body", "geom_ok_ratio_spaces", "open_s", "peak_rss_mb",
        "ifcopenshell"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", action="append")
    ap.add_argument("--geom-sample", type=int, default=200)
    a = ap.parse_args()
    with open(MANIFEST, encoding="utf-8") as fh:
        man = yaml.safe_load(fh)
    today = dt.date.today().isoformat()
    for e in man["files"]:
        if a.id and e["id"] not in a.id:
            continue
        p = os.path.join(ROOT, e["path"])
        if not os.path.exists(p):
            print(f"bỏ qua (chưa có file): {e['id']}")
            continue
        r = subprocess.run([sys.executable, os.path.join(HERE, "inspect_ifc.py"), "--geom-sample",
                            str(a.geom_sample), p], capture_output=True, text=True)
        m = json.loads(r.stdout.strip().splitlines()[-1])
        if "error" in m:
            print(f"LỖI {e['id']}: {m['error']}")
            e["measured"] = {"error": m["error"], "measured_at": today}
            continue
        e["sha256"] = m["sha256"]
        e["size_mb"] = m["size_mb"]
        e["schema"] = m["schema"]
        e["tier"] = m["tier"]
        meas = {k: m.get(k) for k in KEEP}
        meas["measured_at"] = today
        e["measured"] = meas
        sc = score(m, e.get("license_class"), e.get("building_class"))
        e["score"] = sc["total"]
        e["score_detail"] = {k: v for k, v in sc.items() if k != "total"}
        print(f"{e['id']:40} {m['schema']:8} {m['size_mb']:8.2f}MB tier={m['tier']} "
              f"space={m['n_spaces']} rsb={m['n_rsb']} storey={m['n_storeys']} score={sc['total']}")
    with open(MANIFEST, "w", encoding="utf-8") as fh:
        fh.write(HEADER)
        yaml.safe_dump(man, fh, sort_keys=False, allow_unicode=True, width=120)
    return 0


if __name__ == "__main__":
    sys.exit(main())

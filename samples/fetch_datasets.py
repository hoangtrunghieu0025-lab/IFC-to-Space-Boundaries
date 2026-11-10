#!/usr/bin/env python3
"""Tải lại bộ IFC test từ `samples/manifest.yaml` và kiểm sha256 (TASK-001).

Ví dụ (chạy từ gốc repo):
    python3 samples/fetch_datasets.py                 # tải mọi file còn thiếu, kiểm sha256
    python3 samples/fetch_datasets.py --tier S        # chỉ tầng S
    python3 samples/fetch_datasets.py --tier L        # tầng L (file lớn, không commit)
    python3 samples/fetch_datasets.py --check         # chỉ kiểm sha256 file đã có, không tải
    python3 samples/fetch_datasets.py --id bsst-ifc4-building-architecture

Mã thoát khác 0 nếu có file thiếu / sai sha256 / tải lỗi.
Mục có `archive: zip` được giải nén thành viên `archive_member` ra `path`
(sha256 trong manifest là của file .ifc sau giải nén).
Mục có `manual: true` (cần đăng nhập, bị chặn tải tự động) chỉ in hướng dẫn tải tay.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
import tempfile
import urllib.request
import zipfile

import yaml  # pip install pyyaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "samples", "manifest.yaml")


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest: str) -> None:
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "ifc-to-space-boundaries-fetch/1.0"})
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(dest), suffix=".part")
    try:
        with urllib.request.urlopen(req, timeout=120) as r, os.fdopen(fd, "wb") as out:
            shutil.copyfileobj(r, out, 1 << 20)
        os.replace(tmp, dest)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", default=MANIFEST)
    ap.add_argument("--tier", choices=["S", "M", "L"], action="append", help="lọc theo tầng (lặp được)")
    ap.add_argument("--id", action="append", help="lọc theo id (lặp được)")
    ap.add_argument("--check", action="store_true", help="chỉ kiểm sha256, không tải")
    ap.add_argument("--force", action="store_true", help="tải lại kể cả khi file đã có và đúng sha256")
    a = ap.parse_args()

    with open(a.manifest, encoding="utf-8") as fh:
        man = yaml.safe_load(fh)

    bad = 0
    for e in man.get("files", []):
        if a.tier and e.get("tier") not in a.tier:
            continue
        if a.id and e["id"] not in a.id:
            continue
        dest = os.path.join(ROOT, e["path"])
        want = e.get("sha256")
        have_ok = os.path.exists(dest) and (want is None or sha256(dest) == want)
        if have_ok and not a.force:
            print(f"OK       {e['id']}  ({e['path']})")
            continue
        if a.check or e.get("manual"):
            state = "MISSING" if not os.path.exists(dest) else "BADSHA"
            hint = f"  -> tải tay: {e.get('manual_instructions') or e.get('url')}" if e.get("manual") else ""
            print(f"{state:8} {e['id']}  ({e['path']}){hint}")
            bad += 1
            continue
        try:
            print(f"GET      {e['id']}  <- {e['url']}")
            if e.get("archive") == "zip":
                # tải file nén (ví dụ .ifczip) rồi giải nén đúng một thành viên ra `path`
                zdest = dest + ".zip"
                download(e["url"], zdest)
                with zipfile.ZipFile(zdest) as z, open(dest, "wb") as out:
                    with z.open(e["archive_member"]) as src:
                        shutil.copyfileobj(src, out, 1 << 20)
                os.remove(zdest)
            else:
                download(e["url"], dest)
        except Exception as ex:  # noqa: BLE001
            print(f"ERROR    {e['id']}: {type(ex).__name__}: {ex}")
            bad += 1
            continue
        got = sha256(dest)
        if want and got != want:
            print(f"BADSHA   {e['id']}: mong đợi {want}, nhận {got}")
            bad += 1
        else:
            print(f"OK       {e['id']}  sha256={got}")
    print(f"\n{'Tất cả khớp.' if not bad else f'{bad} mục lỗi/thiếu.'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

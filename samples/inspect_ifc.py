#!/usr/bin/env python3
"""Đo các chỉ số chất lượng của một (hoặc nhiều) file IFC cho TASK-001.

Chỉ số và cách chấm điểm theo
`research/04-datasets-and-validation/dataset-quality-criteria.md`.

Ví dụ:
    python3 samples/inspect_ifc.py samples/small/*.ifc            # in JSON
    python3 samples/inspect_ifc.py --geom-sample 300 file.ifc
    python3 samples/inspect_ifc.py --isolate a.ifc b.ifc           # mỗi file một tiến trình (đo RAM riêng)

Mỗi file in ra một dòng JSON (JSON Lines).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import resource
import subprocess
import sys
import time

# Phần tử bao quan tâm (tên lớp gốc; by_type đã gồm lớp con, ví dụ IfcWallStandardCase).
BOUNDING_TYPES = [
    "IfcWall", "IfcSlab", "IfcRoof", "IfcCovering", "IfcColumn", "IfcBeam",
    "IfcDoor", "IfcWindow", "IfcCurtainWall", "IfcStair", "IfcRamp", "IfcRailing",
    "IfcOpeningElement",
]


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def peak_rss_mb() -> float:
    # Linux: ru_maxrss tính bằng KiB.
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def safe_count(f, cls: str) -> int:
    try:
        return len(f.by_type(cls))
    except RuntimeError:  # lớp không tồn tại trong schema này
        return 0


def length_unit(f) -> str | None:
    try:
        for ua in f.by_type("IfcUnitAssignment"):
            for u in ua.Units:
                if u.is_a("IfcSIUnit") and u.UnitType == "LENGTHUNIT":
                    return f"{u.Prefix or ''}{u.Name}"
                if u.is_a("IfcConversionBasedUnit") and u.UnitType == "LENGTHUNIT":
                    return f"{u.Name} (conversion)"
    except Exception:  # noqa: BLE001
        pass
    return None


def storey_of_space(space):
    """Trả về IfcBuildingStorey chứa space (đi lên qua IfcRelAggregates, kể cả space cha)."""
    seen = 0
    obj = space
    while obj is not None and seen < 10:
        seen += 1
        rels = getattr(obj, "Decomposes", None) or []
        parent = None
        for r in rels:
            if r.is_a("IfcRelAggregates"):
                parent = r.RelatingObject
                break
        if parent is None:
            return None
        if parent.is_a("IfcBuildingStorey"):
            return parent
        obj = parent
    return None


def boundary_stats(f) -> dict:
    rsb = f.by_type("IfcRelSpaceBoundary")
    st = {
        "n_rsb": len(rsb),
        # IfcRelSpaceBoundary2ndLevel là lớp con của IfcRelSpaceBoundary1stLevel (IFC4),
        # nên đếm 1stLevel "thuần" = by_type(1stLevel) - by_type(2ndLevel).
        "n_rsb_1st_class": safe_count(f, "IfcRelSpaceBoundary1stLevel") - safe_count(f, "IfcRelSpaceBoundary2ndLevel"),
        "n_rsb_2nd_class": safe_count(f, "IfcRelSpaceBoundary2ndLevel"),
        # Nhãn level do exporter ghi trong Name/Description (không chuẩn hoá giữa các phần mềm, chưa xác minh
        # với mọi exporter): Revit '1stLevel'/'2ndLevel', ArchiCAD 'Second Level' hoặc Description '2a'/'2b'.
        "n_rsb_name_2ndlevel": 0,
        "rsb_level_labels": {},
        "n_rsb_with_geom": 0,
        "n_rsb_virtual": 0,
        "n_rsb_external": 0,
        "n_rsb_with_corresponding": 0,
    }
    labels: dict[str, int] = {}
    for b in rsb:
        name = (b.Name or "").strip()
        desc = (b.Description or "").strip()
        key = f"{name}|{desc}"
        labels[key] = labels.get(key, 0) + 1
        nl = name.lower().replace(" ", "")
        if nl.startswith("2nd") or nl.startswith("secondlevel") or desc.lower() in ("2a", "2b"):
            st["n_rsb_name_2ndlevel"] += 1
        if b.ConnectionGeometry is not None:
            st["n_rsb_with_geom"] += 1
        if str(b.PhysicalOrVirtualBoundary).upper() == "VIRTUAL":
            st["n_rsb_virtual"] += 1
        if str(b.InternalOrExternalBoundary).upper().startswith("EXTERNAL"):
            st["n_rsb_external"] += 1
        if getattr(b, "CorrespondingBoundary", None) is not None:
            st["n_rsb_with_corresponding"] += 1
    st["rsb_level_labels"] = dict(sorted(labels.items(), key=lambda kv: -kv[1])[:6])
    return st


def geometry_check(f, sample: int, seed: int = 0) -> dict:
    """Thử tạo hình học cho một mẫu ngẫu nhiên phần tử bao + IfcSpace."""
    import ifcopenshell.geom

    settings = ifcopenshell.geom.settings()
    def has_body(e) -> bool:
        # Chỉ thử phần tử có biểu diễn 3D 'Body'. Phần tử chỉ có 'Axis'/'FootPrint' 2D
        # (ví dụ tường giả của ArchiCAD) không phải lỗi hình học, đếm riêng.
        rep = e.Representation
        return rep is not None and any(r.RepresentationIdentifier == "Body" for r in rep.Representations)

    elems, no_body = [], 0
    for cls in ["IfcWall", "IfcSlab", "IfcRoof", "IfcColumn", "IfcDoor", "IfcWindow", "IfcCovering"]:
        for e in f.by_type(cls):
            if e.Representation is None:
                continue
            if has_body(e):
                elems.append(e)
            else:
                no_body += 1
    spaces = [s for s in f.by_type("IfcSpace") if s.Representation is not None]
    rng = random.Random(seed)

    def run(items):
        if not items:
            return None, 0
        pick = items if len(items) <= sample else rng.sample(items, sample)
        ok = 0
        for e in pick:
            try:
                ifcopenshell.geom.create_shape(settings, e)
                ok += 1
            except Exception:  # noqa: BLE001
                pass
        return ok / len(pick), len(pick)

    t0 = time.time()
    r_el, n_el = run(elems)
    r_sp, n_sp = run(spaces)
    return {
        "geom_ok_ratio_elements": None if r_el is None else round(r_el, 4),
        "geom_tested_elements": n_el,
        "n_elements_without_body": no_body,
        "geom_ok_ratio_spaces": None if r_sp is None else round(r_sp, 4),
        "geom_tested_spaces": n_sp,
        "geom_check_s": round(time.time() - t0, 2),
    }


def tier_of(size_mb: float, n_spaces: int) -> str:
    if size_mb <= 5 and n_spaces <= 50:
        return "S"
    if size_mb >= 20 or n_spaces >= 200:
        return "L"
    return "M"


def score(m: dict, license_class: str | None = None, building_class: str | None = None) -> dict:
    """Chấm điểm 0–100 theo dataset-quality-criteria.md (mục 3)."""
    s = {}
    n_sp = m["n_spaces"]
    # Ground truth (35)
    s["gt_space_geom"] = 15 * (m["n_spaces_with_rep"] / n_sp) if n_sp else 0
    s["gt_space_storey"] = 5 if n_sp and m["n_spaces_in_storey"] / n_sp >= 0.95 else 0
    s["gt_rsb"] = 10 if m["n_rsb"] > 0 else 0
    s["gt_rsb_2nd"] = 5 if (m["n_rsb_2nd_class"] + m["n_rsb_name_2ndlevel"]) > 0 else 0
    # Hình học (20)
    r = m.get("geom_ok_ratio_elements")
    s["geometry"] = 0 if r is None else 20 * max(0.0, min(1.0, (r - 0.90) / 0.08))
    # Đa dạng (20)
    c = m["counts"]
    s["div_storeys"] = 5 if m["n_storeys"] >= 2 else 0
    s["div_openings"] = 5 if (c.get("IfcDoor", 0) + c.get("IfcWindow", 0)) > 0 and c.get("IfcOpeningElement", 0) > 0 else (2 if (c.get("IfcDoor", 0) + c.get("IfcWindow", 0)) > 0 else 0)
    s["div_roof"] = 3 if c.get("IfcRoof", 0) > 0 else 0
    s["div_other"] = 2 if c.get("IfcColumn", 0) + c.get("IfcCovering", 0) + c.get("IfcStair", 0) > 0 else 0
    s["div_space_count"] = 5 if n_sp >= 10 else (2 if n_sp >= 3 else 0)
    # Pháp lý (15) — nhập tay
    s["legal"] = {"redistributable": 15, "use_only": 8}.get(license_class or "", 0)
    # Loại công trình (10) — nhập tay
    s["building_type"] = {"stadium": 10, "large_public": 8, "office": 5, "residential": 3}.get(building_class or "", 0)
    s = {k: round(v, 2) for k, v in s.items()}
    s["total"] = round(sum(s.values()), 1)
    return s


def inspect(path: str, geom_sample: int) -> dict:
    import ifcopenshell

    size_mb = os.path.getsize(path) / 1e6
    t0 = time.time()
    f = ifcopenshell.open(path)
    open_s = time.time() - t0

    spaces = f.by_type("IfcSpace")
    m = {
        "path": path,
        "size_mb": round(size_mb, 2),
        "sha256": sha256(path),
        "schema": f.schema,
        "ifcopenshell": ifcopenshell.version,
        "open_s": round(open_s, 2),
        "length_unit": length_unit(f),
        "n_entities": len(list(f)) if size_mb < 200 else None,
        "n_products": safe_count(f, "IfcProduct"),
        "n_storeys": safe_count(f, "IfcBuildingStorey"),
        "n_buildings": safe_count(f, "IfcBuilding"),
        "n_spaces": len(spaces),
        "n_spaces_with_rep": sum(1 for s in spaces if s.Representation is not None),
        "n_spaces_in_storey": sum(1 for s in spaces if storey_of_space(s) is not None),
        "counts": {cls: safe_count(f, cls) for cls in BOUNDING_TYPES},
        "n_zones": safe_count(f, "IfcZone"),
    }
    m.update(boundary_stats(f))
    if geom_sample > 0:
        m.update(geometry_check(f, geom_sample))
    m["tier"] = tier_of(size_mb, len(spaces))
    m["peak_rss_mb"] = round(peak_rss_mb(), 1)
    m["score_auto"] = score(m)
    return m


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--geom-sample", type=int, default=200, help="số phần tử thử tạo hình học (0 = bỏ qua)")
    ap.add_argument("--isolate", action="store_true", help="chạy mỗi file trong tiến trình riêng để đo RAM chính xác")
    a = ap.parse_args()
    rc = 0
    for p in a.files:
        if a.isolate and len(a.files) > 1:
            r = subprocess.run([sys.executable, __file__, "--geom-sample", str(a.geom_sample), p])
            rc |= r.returncode
            continue
        try:
            print(json.dumps(inspect(p, a.geom_sample), ensure_ascii=False), flush=True)
        except Exception as e:  # noqa: BLE001
            print(json.dumps({"path": p, "error": f"{type(e).__name__}: {e}"}, ensure_ascii=False), flush=True)
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())

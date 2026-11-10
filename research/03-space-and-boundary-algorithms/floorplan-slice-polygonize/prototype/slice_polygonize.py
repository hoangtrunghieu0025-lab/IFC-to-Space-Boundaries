#!/usr/bin/env python3
"""Prototype (nghiên cứu, không phải mã sản phẩm): lát cắt mặt bằng theo tầng + polygonize để suy ra phòng.

Quy trình:
  1. Với mỗi IfcBuildingStorey, chọn cao độ cắt z = cao độ tầng + dz (mặc định 1.0 m).
  2. Cắt mọi phần tử bao (KHÔNG gồm IfcSpace, IfcOpeningElement) bằng mặt phẳng z: lấy các đoạn thẳng có
     hướng (tam giác định hướng CCW nhìn từ ngoài => chất rắn nằm bên trái đoạn), nối thành vòng kín.
     Vòng ngược chiều kim đồng hồ = biên ngoài, cùng chiều = lỗ.
  3. Hợp tất cả tiết diện thành "footprint" chất rắn. Phòng ứng viên = các lỗ trong footprint (vùng trống bị bao kín).
  4. So với IfcSpace gốc cùng tầng: tiết diện của IfcSpace ở cùng cao độ; IoU diện tích.

Dùng: python slice_polygonize.py file.ifc [--dz 1.0] [--min-area 1.0] [--close 0.0] [--json out.json]
Cần ifcopenshell, numpy, shapely. Giả định mô hình là các solid kín có pháp tuyến hướng ra ngoài.
"""
import argparse, json, sys, time
from collections import defaultdict
import numpy as np
import ifcopenshell, ifcopenshell.geom, ifcopenshell.util.element as ue, ifcopenshell.util.placement as up, ifcopenshell.util.unit as uu
from shapely.geometry import Polygon
from shapely.ops import unary_union

SKIP = ("IfcSpace", "IfcOpeningElement", "IfcVirtualElement", "IfcAnnotation", "IfcGrid",
        "IfcSite", "IfcBuilding", "IfcBuildingStorey", "IfcProject")
Q = 1e-4


def mesh_of(shape):
    g = shape.geometry
    return np.array(g.verts, dtype=np.float64).reshape(-1, 3), np.array(g.faces, dtype=np.int64).reshape(-1, 3)


def section_segments(v, f, z):
    """Đoạn có hướng của tiết diện ngang tại cao độ z. Trả về list ((x1,y1),(x2,y2))."""
    segs = []
    zz = v[:, 2] - z
    for tri in f:
        s = zz[tri]
        if (s > 0).all() or (s < 0).all() or (s == 0).all():
            continue
        pts = []  # (loại, điểm) theo thứ tự biên CCW
        for k in range(3):
            i, j = tri[k], tri[(k + 1) % 3]
            a, b = zz[i], zz[j]
            if (a < 0 <= b) or (a >= 0 > b):
                t = a / (a - b)
                p = v[i] + t * (v[j] - v[i])
                pts.append(("up" if a < 0 <= b else "down", (round(p[0] / Q) * Q, round(p[1] / Q) * Q)))
        if len(pts) != 2:
            continue
        (k1, p1), (k2, p2) = pts
        if p1 == p2:
            continue
        # Hướng được hiệu chỉnh bằng phép thử hộp (xem calibrate()): đoạn đi từ điểm "down" tới điểm "up"
        if k1 == "down":
            segs.append((p1, p2))
        else:
            segs.append((p2, p1))
    return segs


def rings_from_segments(segs):
    nxt = defaultdict(list)
    for a, b in segs:
        nxt[a].append(b)
    rings, used = [], set()
    for a, b in segs:
        if (a, b) in used:
            continue
        ring = [a]
        cur, nx = a, b
        used.add((a, b))
        guard = 0
        while nx != ring[0] and guard < 100000:
            ring.append(nx)
            cand = [c for c in nxt[nx] if (nx, c) not in used]
            if not cand:
                ring = None
                break
            used.add((nx, cand[0]))
            cur, nx = nx, cand[0]
            guard += 1
        if ring and len(ring) >= 3:
            rings.append(ring)
    return rings


def solid_from_rings(rings):
    outers, holes = [], []
    for r in rings:
        p = Polygon(r)
        if not p.is_valid:
            p = p.buffer(0)
        if p.is_empty:
            continue
        ar = 0.5 * sum(r[i][0] * r[(i + 1) % len(r)][1] - r[(i + 1) % len(r)][0] * r[i][1] for i in range(len(r)))
        (outers if ar > 0 else holes).append(p)
    if not outers:
        return None
    s = unary_union(outers)
    if holes:
        s = s.difference(unary_union(holes))
    return s


def calibrate():
    """Hộp đơn vị CCW nhìn từ ngoài: tiết diện phải ra đa giác diện tích dương (+1)."""
    v = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]], float)
    f = np.array([[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7], [0, 1, 5], [0, 5, 4], [1, 2, 6], [1, 6, 5],
                  [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]])
    s = solid_from_rings(rings_from_segments(section_segments(v, f, 0.5)))
    return None if s is None else s.area


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ifc")
    ap.add_argument("--dz", type=float, default=1.0)
    ap.add_argument("--min-area", type=float, default=1.0)
    ap.add_argument("--close", type=float, default=0.0, help="đóng khe: buffer +x rồi -x (m)")
    ap.add_argument("--json")
    a = ap.parse_args()
    cal = calibrate()
    if cal is None or abs(cal - 1.0) > 1e-6:
        print(f"hiệu chỉnh hướng thất bại: diện tích hộp thử = {cal}", file=sys.stderr)
        sys.exit(2)
    t0 = time.time()
    f = ifcopenshell.open(a.ifc)
    scale = uu.calculate_unit_scale(f)
    st = ifcopenshell.geom.settings()
    st.set("use-world-coords", True)
    meshes, spmeshes = [], []
    it = ifcopenshell.geom.iterator(st, f, 4)
    if it.initialize():
        while True:
            sh = it.get()
            prod = f.by_id(sh.id)
            cls = prod.is_a()
            v, fa = mesh_of(sh)
            if len(fa):
                if cls == "IfcSpace":
                    spmeshes.append((prod, v, fa))
                elif cls not in SKIP:
                    meshes.append((prod, v, fa))
            if not it.next():
                break
    t_geom = time.time() - t0
    storeys = sorted(f.by_type("IfcBuildingStorey"), key=lambda s: up.get_local_placement(s.ObjectPlacement)[2][3])
    out = {"file": a.ifc, "dz": a.dz, "min_area": a.min_area, "close": a.close, "unit_scale": scale,
           "n_elements": len(meshes), "n_ifcspace_total": len(spmeshes), "time_geometry_s": round(t_geom, 2), "storeys": []}
    t1 = time.time()
    for s in storeys:
        zs = up.get_local_placement(s.ObjectPlacement)[2][3] * scale  # đã ở mét nếu geom ở mét
        # Hình học trả về bởi iterator ở đơn vị mét; placement ở đơn vị dự án => nhân scale ở trên
        z = zs + a.dz
        solids = []
        for prod, v, fa in meshes:
            if v[:, 2].min() < z < v[:, 2].max():
                sol = solid_from_rings(rings_from_segments(section_segments(v, fa, z)))
                if sol is not None and not sol.is_empty:
                    solids.append(sol)
        foot = unary_union(solids) if solids else None
        rooms = []
        if foot is not None:
            if a.close > 0:
                foot = foot.buffer(a.close).buffer(-a.close)
            polys = list(foot.geoms) if foot.geom_type == "MultiPolygon" else [foot]
            for p in polys:
                for ring in p.interiors:
                    r = Polygon(ring)
                    if r.area >= a.min_area:
                        rooms.append(r)
        # IfcSpace của tầng này
        sps = []
        for prod, v, fa in spmeshes:
            cont = ue.get_aggregate(prod) or ue.get_container(prod)
            if cont is not None and cont.id() == s.id():
                if v[:, 2].min() < z < v[:, 2].max():
                    sp = solid_from_rings(rings_from_segments(section_segments(v, fa, z)))
                    sps.append({"name": prod.Name, "guid": prod.GlobalId, "poly": sp})
                else:
                    sps.append({"name": prod.Name, "guid": prod.GlobalId, "poly": None})
        matched, ious = 0, []
        used = set()
        for sp in sps:
            if sp["poly"] is None or sp["poly"].is_empty:
                continue
            best, bi = 0.0, None
            for i, r in enumerate(rooms):
                inter = r.intersection(sp["poly"]).area
                if inter > 0:
                    iou = inter / r.union(sp["poly"]).area
                    if iou > best:
                        best, bi = iou, i
            ious.append(round(best, 3))
            if best >= 0.5:
                matched += 1
                used.add(bi)
        out["storeys"].append({
            "storey": s.Name, "z_cut_m": round(z, 3), "n_elements_cut": len(solids),
            "n_rooms_found": len(rooms), "rooms_area_sum_m2": round(sum(r.area for r in rooms), 2),
            "n_ifcspace_in_storey": len(sps), "n_ifcspace_cut_by_plane": sum(1 for sp in sps if sp["poly"] is not None),
            "ifcspace_area_sum_m2": round(sum(sp["poly"].area for sp in sps if sp["poly"] is not None), 2),
            "matched_iou_ge_0.5": matched, "best_iou_per_ifcspace": ious,
            "rooms_without_ifcspace": len(rooms) - len(used)})
    out["time_slice_s"] = round(time.time() - t1, 2)
    print(json.dumps(out, indent=1, ensure_ascii=False))
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()

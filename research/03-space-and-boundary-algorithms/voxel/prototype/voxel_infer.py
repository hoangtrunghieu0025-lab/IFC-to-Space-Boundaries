#!/usr/bin/env python3
"""Prototype (nghiên cứu, không phải mã sản phẩm): suy ra không gian kín từ IFC bằng voxel.

Quy trình (theo gợi ý ở phần kết luận của Krijnen et al. 2021, mục 6: flood fill + đảo + trừ):
  1. Lấy hình học các phần tử bao (KHÔNG gồm IfcSpace, IfcOpeningElement) bằng IfcOpenShell, toạ độ thế giới.
  2. Voxel hoá bề mặt: lấy mẫu dày trên từng tam giác (khoảng cách mẫu <= h/2), đánh dấu ô chứa mẫu.
     Đây là XẤP XỈ của phép giao tam giác-hộp (có thể bỏ sót tam giác sát biên ô).
  3. Tuỳ chọn: đóng khe bằng phép giãn (dilation) k ô.
  4. Gán nhãn thành phần liên thông (6-liền kề) của các ô trống; thành phần chạm biên lưới = ngoài trời.
  5. Các thành phần còn lại có thể tích >= min_vol là "không gian kín ứng viên".
  6. So với IfcSpace gốc: IfcSpace nào có trọng tâm rơi vào thành phần nào.

Dùng: python voxel_infer.py file.ifc --h 0.1 [--close 0] [--min-vol 1.0] [--json out.json]
Chạy bằng venv có ifcopenshell, numpy (scipy là tuỳ chọn).
"""
import argparse, json, math, sys, time
import numpy as np
import ifcopenshell, ifcopenshell.geom
try:
    from scipy import ndimage  # tuỳ chọn; có thì dùng, không thì dùng bản numpy/BFS bên dưới
except ImportError:  # pragma: no cover
    ndimage = None
from collections import deque

SKIP = ("IfcSpace", "IfcOpeningElement", "IfcVirtualElement", "IfcAnnotation", "IfcGrid",
        "IfcSite", "IfcBuilding", "IfcBuildingStorey", "IfcProject")


def mesh_of(shape):
    g = shape.geometry
    v = np.array(g.verts, dtype=np.float64).reshape(-1, 3)
    f = np.array(g.faces, dtype=np.int64).reshape(-1, 3)
    return v, f


def signed_volume_centroid(v, f):
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    vol = np.einsum("ij,ij->i", a, np.cross(b, c)) / 6.0
    V = vol.sum()
    if abs(V) < 1e-9:
        return 0.0, v.mean(axis=0)
    cen = ((a + b + c) / 4.0 * vol[:, None]).sum(axis=0) / V
    return abs(V), cen


def sample_triangles(v, f, step):
    """Lấy mẫu điểm dày trên bề mặt các tam giác; trả về mảng (N,3)."""
    a, b, c = v[f[:, 0]], v[f[:, 1]], v[f[:, 2]]
    e = np.maximum.reduce([np.linalg.norm(b - a, axis=1), np.linalg.norm(c - b, axis=1), np.linalg.norm(a - c, axis=1)])
    n = np.maximum(1, np.ceil(e / step).astype(int))
    out = [v]
    for k in np.unique(n):
        idx = np.where(n == k)[0]
        i, j = np.meshgrid(np.arange(k + 1), np.arange(k + 1), indexing="ij")
        m = (i + j) <= k
        u, w = (i[m] / k), (j[m] / k)
        t = 1.0 - u - w
        # (T, P, 3)
        p = (a[idx, None, :] * t[None, :, None] + b[idx, None, :] * u[None, :, None] + c[idx, None, :] * w[None, :, None])
        out.append(p.reshape(-1, 3))
    return np.vstack(out)


def dilate6(occ, iterations):
    """Giãn nhị phân theo 6 láng giềng, chỉ dùng numpy."""
    out = occ.copy()
    for _ in range(iterations):
        n = out.copy()
        n[1:] |= out[:-1]; n[:-1] |= out[1:]
        n[:, 1:] |= out[:, :-1]; n[:, :-1] |= out[:, 1:]
        n[:, :, 1:] |= out[:, :, :-1]; n[:, :, :-1] |= out[:, :, 1:]
        out = n
    return out


def label6(empty):
    """Gán nhãn thành phần liên thông 6-liền kề bằng BFS (không cần scipy). Trả về (nhãn, số thành phần)."""
    dims = empty.shape
    flat = empty.ravel()
    lab = np.zeros(flat.shape, dtype=np.int32)
    sx, sy, sz = dims[1] * dims[2], dims[2], 1
    n = 0
    idxs = np.flatnonzero(flat)
    for s in idxs:
        if lab[s]:
            continue
        n += 1
        lab[s] = n
        dq = deque([int(s)])
        while dq:
            c = dq.popleft()
            x, r = divmod(c, sx)
            y, z = divmod(r, sy)
            for nb, ok in ((c - sx, x > 0), (c + sx, x < dims[0] - 1), (c - sy, y > 0), (c + sy, y < dims[1] - 1),
                           (c - 1, z > 0), (c + 1, z < dims[2] - 1)):
                if ok and flat[nb] and not lab[nb]:
                    lab[nb] = n
                    dq.append(nb)
    return lab.reshape(dims), n


def voxelize_mesh(v, fa, lo, h, fill):
    """Voxel hoá một lưới; trả về (i0, i1, mặt nạ cục bộ)."""
    pts = sample_triangles(v, fa, h * 0.5)
    ijk = np.floor((pts - lo) / h).astype(int)
    i0, i1 = ijk.min(0), ijk.max(0) + 1
    loc = np.zeros(i1 - i0 + 2, dtype=bool)  # +2: viền 1 ô để biết "ngoài"
    loc[ijk[:, 0] - i0[0] + 1, ijk[:, 1] - i0[1] + 1, ijk[:, 2] - i0[2] + 1] = True
    if fill:
        ll, ln = label6(~loc)
        if ln:
            edge = np.unique(np.concatenate([ll[0].ravel(), ll[-1].ravel(), ll[:, 0].ravel(), ll[:, -1].ravel(), ll[:, :, 0].ravel(), ll[:, :, -1].ravel()]))
            loc = ~np.isin(ll, edge[edge > 0]) | loc
    return i0, i1, len(pts), loc[1:-1, 1:-1, 1:-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ifc")
    ap.add_argument("--h", type=float, default=0.1, help="cạnh voxel (m)")
    ap.add_argument("--close", type=int, default=0, help="số lần giãn để đóng khe")
    ap.add_argument("--min-vol", type=float, default=1.0, help="thể tích tối thiểu (m3)")
    ap.add_argument("--no-fill-solids", dest="fill_solids", action="store_false", help="không tô đặc phần tử (mặc định có tô)")
    ap.add_argument("--json")
    a = ap.parse_args()
    t0 = time.time()
    f = ifcopenshell.open(a.ifc)
    st = ifcopenshell.geom.settings()
    st.set("use-world-coords", True)
    elems, spaces = [], []
    it = ifcopenshell.geom.iterator(st, f, 4)
    ok = it.initialize()
    n_el = 0
    meshes = []
    if ok:
        while True:
            sh = it.get()
            prod = f.by_id(sh.id)
            cls = prod.is_a()
            v, fa = mesh_of(sh)
            if len(fa):
                if cls == "IfcSpace":
                    vol, cen = signed_volume_centroid(v, fa)
                    spaces.append({"guid": prod.GlobalId, "name": prod.Name, "vol": vol, "cen": cen.tolist(), "mesh": (v, fa)})
                elif not cls.startswith(SKIP) and cls not in SKIP:
                    meshes.append((v, fa))
                    n_el += 1
            if not it.next():
                break
    t_geom = time.time() - t0
    if not meshes:
        print("không có hình học phần tử bao", file=sys.stderr); sys.exit(1)
    allv = np.vstack([m[0] for m in meshes])
    lo = allv.min(0) - 2 * a.h
    hi = allv.max(0) + 2 * a.h
    dims = np.ceil((hi - lo) / a.h).astype(int) + 1
    n_cells = int(np.prod(dims))
    t1 = time.time()
    occ = np.zeros(dims, dtype=bool)
    n_pts = 0
    for v, fa in meshes:
        i0, i1, npt, loc = voxelize_mesh(v, fa, lo, a.h, a.fill_solids)
        n_pts += npt
        occ[i0[0]:i1[0], i0[1]:i1[1], i0[2]:i1[2]] |= loc
    n_occ_before = int(occ.sum())
    if a.close:
        occ = ndimage.binary_dilation(occ, structure=ndimage.generate_binary_structure(3, 1), iterations=a.close) if ndimage else dilate6(occ, a.close)
    empty = ~occ
    lab, n = ndimage.label(empty) if ndimage else label6(empty)  # 6-liền kề
    sizes = np.bincount(lab.ravel())
    border = np.unique(np.concatenate([lab[0].ravel(), lab[-1].ravel(), lab[:, 0].ravel(), lab[:, -1].ravel(), lab[:, :, 0].ravel(), lab[:, :, -1].ravel()]))
    exterior = set(border.tolist()) - {0}
    cell_vol = a.h ** 3
    comps = []
    for L in range(1, n + 1):
        if L in exterior:
            continue
        vol = sizes[L] * cell_vol
        if vol >= a.min_vol:
            comps.append((L, vol))
    t_vox = time.time() - t1
    # so với IfcSpace
    lab_of_space = []
    for s in spaces:
        c = (np.array(s["cen"]) - lo) / a.h
        idx = np.floor(c).astype(int)
        L = int(lab[tuple(idx)]) if all(0 <= idx[k] < dims[k] for k in range(3)) else 0
        lab_of_space.append(L)
    comp_ids = {L for L, _ in comps}
    ious = []
    for s, L in zip(spaces, lab_of_space):
        if L not in comp_ids:
            ious.append(0.0)
            continue
        i0, i1, _, m = voxelize_mesh(s["mesh"][0], s["mesh"][1], lo, a.h, True)
        i0 = np.maximum(i0, 0); 
        win = lab[i0[0]:i0[0] + m.shape[0], i0[1]:i0[1] + m.shape[1], i0[2]:i0[2] + m.shape[2]]
        mm = m[:win.shape[0], :win.shape[1], :win.shape[2]]
        inter = int(((win == L) & mm).sum())
        uni = int(m.sum()) + int(sizes[L]) - inter
        ious.append(inter / uni if uni else 0.0)
    rec = [L for L in lab_of_space if L in comp_ids]
    from collections import Counter
    cnt = Counter(rec)
    merged = sum(1 for L, c in cnt.items() if c > 1)
    res = {
        "file": a.ifc, "h": a.h, "close": a.close, "min_vol": a.min_vol,
        "n_elements": n_el, "n_sample_points": int(n_pts), "grid_dims": dims.tolist(), "n_cells": n_cells,
        "grid_mem_MB_bool": round(n_cells / 1e6, 2), "n_occupied_before_close": n_occ_before,
        "n_ifcspace": len(spaces), "n_ifcspace_volume_sum": round(sum(s["vol"] for s in spaces), 2),
        "n_enclosed_components": len(comps), "enclosed_volume_sum": round(sum(v for _, v in comps), 2),
        "ifcspace_centroid_in_enclosed": len(rec), "ifcspace_centroid_in_exterior_or_solid": len(spaces) - len(rec),
        "components_containing_more_than_one_ifcspace": merged,
        "components_without_ifcspace": len(comp_ids - set(rec)),
        "matched_iou_ge_0.5": sum(1 for x in ious if x >= 0.5), "mean_iou": round(float(np.mean(ious)), 3) if ious else 0.0,
        "iou_per_ifcspace": [round(x, 3) for x in ious],
        "time_geometry_s": round(t_geom, 2), "time_voxel_s": round(t_vox, 2),
    }
    print(json.dumps(res, indent=1, ensure_ascii=False))
    if a.json:
        json.dump(res, open(a.json, "w"), indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()

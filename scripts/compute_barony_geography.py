#!/usr/bin/env python3
"""
compute_barony_geography.py

Computes geometric, maritime coast, and imperial frontier metadata for all 11,297 CK3
baronies from data/ck3_baronies.geojson, data/ck3_adjacencies.json, and 1194 Roman
Empire title ownership:
  - Area-weighted polygon centroids (x, y), pixel area, bbox, and intra-county cardinal direction
  - True sea-coast vs. inland river/lake classification via span-level morphological
    opening (r=3, width >= 7 px) with off-map frontier seals, marine strait bridging,
    and constrained 4-step geodesic dilation back to exact coastlines
  - Endorheic Caspian Sea shoreline detection (is_caspian_coast)
  - 1194 Roman Empire frontier / march status at both county and barony resolution

Output:
  data/barony_geography.json
"""

import argparse
import json
import math
import time
from collections import defaultdict, deque
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_DIR / "data"
TITLES_DATA_PATH = Path("/var/tmp/ck3_audit/phase1/titles_data.json")

GRID_W = 8800
GRID_H = 4660

# Known enclosed or narrow-strait marine basins that pinch below r=2 width
# (Mediterranean at Gibraltar, Black Sea / Marmara / Azov at Bosporus-Dardanelles-Kerch,
# Zuiderzee at Marsdiep, Seto Inland Sea at Akashi/Kitan/Kanmon, Varangerfjord).
MARINE_BASIN_SEEDS = [
    ("mediterranean", (1300, 2250)),
    ("black_sea", (2850, 2650)),
    ("sea_of_marmara", (2560, 2440)),
    ("sea_of_azov", (3050, 2850)),
    ("zuiderzee", (1260, 3380)),
    ("seto_inland_sea", (8130, 2830)),
    ("varangerfjord", (2115, 4510)),
]

CASPIAN_SEED = (3600, 2600)


def ring_signed_area_centroid(ring: list) -> tuple[float, float, float]:
    """Computes signed Shoelace area and centroid (area, cx, cy) for a closed coordinate ring."""
    if len(ring) < 3:
        return 0.0, 0.0, 0.0
    a2 = 0.0
    cx6 = 0.0
    cy6 = 0.0
    for i in range(len(ring) - 1):
        x0, y0 = ring[i]
        x1, y1 = ring[i + 1]
        cross = x0 * y1 - x1 * y0
        a2 += cross
        cx6 += (x0 + x1) * cross
        cy6 += (y0 + y1) * cross
    if abs(a2) < 1e-9:
        return 0.0, 0.0, 0.0
    return a2 * 0.5, cx6 / (3.0 * a2), cy6 / (3.0 * a2)


def compute_geometry_metrics(geom: dict) -> tuple[float, float, float, list]:
    """Computes total area (px^2), area-weighted centroid (cx, cy), and [xmin, ymin, xmax, ymax]."""
    polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
    total_area = 0.0
    sum_ax = 0.0
    sum_ay = 0.0
    all_pts = []

    for poly in polys:
        outer_area, ocx, ocy = ring_signed_area_centroid(poly[0])
        part_area = abs(outer_area)
        part_ax = part_area * ocx
        part_ay = part_area * ocy
        for hole in poly[1:]:
            ha, hcx, hcy = ring_signed_area_centroid(hole)
            habs = abs(ha)
            part_area -= habs
            part_ax -= habs * hcx
            part_ay -= habs * hcy
        if part_area > 0:
            total_area += part_area
            sum_ax += part_ax
            sum_ay += part_ay
        for ring in poly:
            all_pts.extend(ring)

    xs = [p[0] for p in all_pts]
    ys = [p[1] for p in all_pts]
    bbox = [round(min(xs), 1), round(min(ys), 1), round(max(xs), 1), round(max(ys), 1)]
    if total_area > 0:
        return total_area, sum_ax / total_area, sum_ay / total_area, bbox
    return 0.0, sum(xs) / len(xs), sum(ys) / len(ys), bbox


def cardinal_direction(dx: float, dy: float, radius: float) -> str:
    """Returns 8-wind direction or 'Center' for offset (dx, dy) relative to county center."""
    dist = math.hypot(dx, dy)
    if dist < max(1.0, radius * 0.25):
        return "Center"
    angle = math.degrees(math.atan2(dy, dx)) % 360.0
    idx = int((angle + 22.5) // 45.0) % 8
    return ["E", "NE", "N", "NW", "W", "SW", "S", "SE"][idx]


def merge_spans(segs: list) -> list:
    """Merges overlapping/touching [a, b) integer intervals."""
    if not segs:
        return []
    segs.sort()
    merged = [segs[0]]
    for a, b in segs[1:]:
        if a <= merged[-1][1]:
            if b > merged[-1][1]:
                merged[-1] = (merged[-1][0], b)
        else:
            merged.append((a, b))
    return merged


def intersect_spans(s1: list, s2: list) -> list:
    """Intersects two sorted disjoint interval lists in linear time."""
    res = []
    i = j = 0
    n1, n2 = len(s1), len(s2)
    while i < n1 and j < n2:
        a = s1[i][0] if s1[i][0] > s2[j][0] else s2[j][0]
        b = s1[i][1] if s1[i][1] < s2[j][1] else s2[j][1]
        if a < b:
            res.append((a, b))
        if s1[i][1] < s2[j][1]:
            i += 1
        else:
            j += 1
    return res


def sliding_extremum(arr: list, win: int, find_max: bool) -> list:
    """Computes centered sliding window max or min over a 1D integer array."""
    n = len(arr)
    out = [0] * n
    dq = deque()
    for i in range(n + win):
        if i < n:
            while dq and ((arr[dq[-1]] <= arr[i]) if find_max else (arr[dq[-1]] >= arr[i])):
                dq.pop()
            dq.append(i)
        if dq and dq[0] < i - 2 * win:
            dq.popleft()
        idx = i - win
        if 0 <= idx < n:
            out[idx] = arr[dq[0]]
    return out


def rasterize_baronies(features: list) -> tuple[list, list]:
    """Scanline-rasterizes GeoJSON features into per-row land segments and per-barony spans."""
    row_segs = [[] for _ in range(GRID_H)]
    barony_spans = []
    for ft in features:
        g = ft["geometry"]
        polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        bspans = []
        for poly in polys:
            ymin = 10**9
            ymax = -10**9
            edges = []
            for ring in poly:
                for i in range(len(ring) - 1):
                    x1, y1 = ring[i]
                    x2, y2 = ring[i + 1]
                    if y1 == y2:
                        continue
                    if y1 > y2:
                        x1, y1, x2, y2 = x2, y2, x1, y1
                    if y1 < ymin:
                        ymin = y1
                    if y2 > ymax:
                        ymax = y2
                    edges.append((x1, y1, x2, y2, (x2 - x1) / (y2 - y1)))
            for y in range(max(0, int(ymin)), min(GRID_H - 1, int(ymax)) + 1):
                yf = y + 0.5
                xs = [ex1 + (yf - ey1) * inv_m for ex1, ey1, ex2, ey2, inv_m in edges if ey1 <= yf < ey2]
                if xs:
                    xs.sort()
                    for k in range(0, len(xs) - 1, 2):
                        xa = max(0, int(xs[k] + 0.5))
                        xb = min(GRID_W, int(xs[k + 1] + 0.5))
                        if xa < xb:
                            row_segs[y].append((xa, xb))
                            bspans.append((y, xa, xb))
        barony_spans.append(bspans)
    return row_segs, barony_spans


def build_sealed_empty_mask(row_segs: list) -> list:
    """
    Seals off-map continental horizons (Northern Eurasia taiga, Equatorial/Central Africa interior)
    and the Egyptian Eastern Desert coastal wasteland so exterior ocean flood cannot leak onto
    inland frontier counties or Nile Valley holdings.
    """
    north_raw = [0] * GRID_W
    south_raw = [GRID_H] * GRID_W
    for y, segs in enumerate(row_segs):
        for a, b in segs:
            for x in range(a, b):
                if y > north_raw[x]:
                    north_raw[x] = y
                if y < south_raw[x]:
                    south_raw[x] = y

    north_env = sliding_extremum(north_raw, 15, find_max=True)
    south_env = sliding_extremum(south_raw, 15, find_max=False)

    seal_segs = [[] for _ in range(GRID_H)]
    # 1. Northern Eurasian off-map horizon (east of White Sea at x=2675 to Tugur/Okhotsk at x=8045)
    for x in range(2675, 8046):
        ym = north_env[x]
        if ym > 3400:
            y_start = max(0, ym - 4)
            for y in range(y_start, GRID_H):
                seal_segs[y].append((x, x + 1))

    # 2. Central Africa southern off-map horizon (Cameroon coast x=1665 to Tanzania coast x=3147)
    for x in range(1665, 3148):
        ym = south_env[x]
        if ym < 1050:
            y_end = min(GRID_H, ym + 5)
            for y in range(0, y_end):
                seal_segs[y].append((x, x + 1))

    # 3. Egyptian / Nubian Eastern Desert coastal wasteland behind Suez-Safaga-Qusayr shore
    egypt_barrier = [(2778, 1766), (2880, 1660), (2896, 1598), (2896, 1480), (2976, 1452)]
    for k in range(len(egypt_barrier) - 1):
        x1, y1 = egypt_barrier[k]
        x2, y2 = egypt_barrier[k + 1]
        steps = max(abs(x2 - x1), abs(y2 - y1)) + 1
        for t in range(steps + 1):
            px = int(round(x1 + (x2 - x1) * t / steps))
            py = int(round(y1 + (y2 - y1) * t / steps))
            for yy in range(py - 4, py + 5):
                if 0 <= yy < GRID_H:
                    seal_segs[yy].append((max(0, px - 4), min(GRID_W, px + 5)))

    sealed_empty = []
    for y in range(GRID_H):
        occupied = merge_spans(row_segs[y] + seal_segs[y])
        emp = []
        cur = 0
        for a, b in occupied:
            if cur < a:
                emp.append((cur, a))
            cur = max(cur, b)
        if cur < GRID_W:
            emp.append((cur, GRID_W))
        sealed_empty.append(emp)
    return sealed_empty


def erode_and_label_components(empty_rows: list, r: int) -> tuple[list, list, list, list]:
    """Chebyshev-erodes empty space by radius r pixels and computes 4/8-span connected components."""
    if r == 0:
        er = [list(row) for row in empty_rows]
    else:
        h_shrunk = [
            [
                (a + r if a > 0 else 0, b - r if b < GRID_W else GRID_W)
                for a, b in row
                if (b - r if b < GRID_W else GRID_W) > (a + r if a > 0 else 0)
            ]
            for row in empty_rows
        ]
        er = []
        for y in range(GRID_H):
            cur = h_shrunk[max(0, y - r)]
            for yy in range(max(0, y - r) + 1, min(GRID_H - 1, y + r) + 1):
                if not cur:
                    break
                cur = intersect_spans(cur, h_shrunk[yy])
            er.append(cur)

    span_id_rows = []
    spans = []
    for y, row in enumerate(er):
        ids = []
        for a, b in row:
            ids.append(len(spans))
            spans.append((y, a, b))
        span_id_rows.append(ids)

    n_spans = len(spans)
    adj = [[] for _ in range(n_spans)]
    for y in range(GRID_H - 1):
        r1, r2 = span_id_rows[y], span_id_rows[y + 1]
        i = j = 0
        n1, n2 = len(r1), len(r2)
        while i < n1 and j < n2:
            s1, s2 = r1[i], r2[j]
            if spans[s1][1] < spans[s2][2] and spans[s2][1] < spans[s1][2]:
                adj[s1].append(s2)
                adj[s2].append(s1)
            if spans[s1][2] < spans[s2][2]:
                i += 1
            else:
                j += 1

    comp = [-1] * n_spans
    for s in range(n_spans):
        if comp[s] != -1:
            continue
        cid = s
        q = deque([s])
        comp[s] = cid
        while q:
            u = q.popleft()
            for v in adj[u]:
                if comp[v] == -1:
                    comp[v] = cid
                    q.append(v)
    return er, span_id_rows, spans, comp


def dilate_components_to_coast(
    target_cids: set,
    spans: list,
    comp: list,
    sealed_empty: list,
    barony_spans: list,
    steps: int = 4,
) -> set:
    """Geodesically dilates eroded water cores inside sealed_empty and returns touching barony indices."""
    cur = [[] for _ in range(GRID_H)]
    for sid, (y, a, b) in enumerate(spans):
        if comp[sid] in target_cids:
            cur[y].append((a, b))

    for _ in range(steps):
        nxt = [[] for _ in range(GRID_H)]
        for y in range(GRID_H):
            segs = [
                (max(0, a - 1), min(GRID_W, b + 1))
                for yy in (y - 1, y, y + 1)
                if 0 <= yy < GRID_H
                for a, b in cur[yy]
            ]
            if segs:
                nxt[y] = intersect_spans(merge_spans(segs), sealed_empty[y])
        cur = nxt

    touching = set()
    for bi, bspans in enumerate(barony_spans):
        for y, xa, xb in bspans:
            hit = False
            for yy in (y - 1, y, y + 1):
                if 0 <= yy < GRID_H and any(sa <= xb and (xa - 1) < sb for sa, sb in cur[yy]):
                    hit = True
                    break
            if hit:
                touching.add(bi)
                break
    return touching


def detect_coastlines(features: list) -> tuple[set, set]:
    """Runs morphological opening (r=3) + constrained geodesic dilation to detect sea and Caspian coastlines."""
    t0 = time.time()
    print("  Rasterizing 11,297 barony polygons onto 8800x4660 grid...")
    row_segs, barony_spans = rasterize_baronies(features)
    sealed_empty = build_sealed_empty_mask(row_segs)

    print("  Running r=2 and r=3 span erosions...")
    _, sir2, spans2, comp2 = erode_and_label_components(sealed_empty, 2)
    _, sir3, spans3, comp3 = erode_and_label_components(sealed_empty, 3)

    # Atlantic / Arctic West exterior + Indo-Pacific East exterior in r=2 erosion
    ext_cids_2 = {comp2[sir2[0][0]], comp2[sir2[0][-1]]}
    sea_cids = set()
    for y in range(GRID_H):
        r2_oc = [(spans2[s][1], spans2[s][2]) for s in sir2[y] if comp2[s] in ext_cids_2]
        if not r2_oc:
            continue
        for sid in sir3[y]:
            a, b = spans3[sid][1], spans3[sid][2]
            if any(a < ob and oa < b for oa, ob in r2_oc):
                sea_cids.add(comp3[sid])

    for _, (px, py) in MARINE_BASIN_SEEDS:
        for sid in sir3[py]:
            if spans3[sid][1] <= px < spans3[sid][2]:
                sea_cids.add(comp3[sid])

    caspian_cids = set()
    cx, cy = CASPIAN_SEED
    for sid in sir3[cy]:
        if spans3[sid][1] <= cx < spans3[sid][2]:
            caspian_cids.add(comp3[sid])

    print("  Dilating marine & Caspian cores back to shorelines (4 geodesic steps)...")
    sea_indices = dilate_components_to_coast(sea_cids, spans3, comp3, sealed_empty, barony_spans, steps=4)
    caspian_indices = dilate_components_to_coast(caspian_cids, spans3, comp3, sealed_empty, barony_spans, steps=4)
    print(f"  -> Coastline detection completed in {time.time() - t0:.2f}s "
          f"({len(sea_indices)} sea-coast, {len(caspian_indices)} Caspian-coast)")
    return sea_indices, caspian_indices


def load_county_roman_status() -> dict:
    """Loads 1194 Roman Empire status per county from titles_data.json or barony_toponymic_profiles.json."""
    county_in_hre = {}
    if TITLES_DATA_PATH.exists():
        with open(TITLES_DATA_PATH, "r", encoding="utf-8") as f:
            td = json.load(f)
        for k, v in td.items():
            if k.startswith("c_"):
                county_in_hre[k] = bool(v.get("is_in_roman_empire"))
        return county_in_hre

    prof_path = DATA_DIR / "barony_toponymic_profiles.json"
    if prof_path.exists():
        with open(prof_path, "r", encoding="utf-8") as f:
            prof = json.load(f)
        for rec in prof.get("baronies", {}).values():
            ck = rec.get("county")
            if ck and ck not in county_in_hre:
                county_in_hre[ck] = bool(rec.get("conquest_date"))
    return county_in_hre


def main():
    parser = argparse.ArgumentParser(description="Compute Section 4.B data/barony_geography.json from GeoJSON")
    parser.add_argument("--geojson", default=str(DATA_DIR / "ck3_baronies.geojson"))
    parser.add_argument("--adjacencies", default=str(DATA_DIR / "ck3_adjacencies.json"))
    parser.add_argument("--holdings", default=str(DATA_DIR / "barony_holdings.json"))
    parser.add_argument("--output", default=str(DATA_DIR / "barony_geography.json"))
    args = parser.parse_args()

    t_start = time.time()
    print("==========================================================")
    print("Computing Barony Geography (Centroids, Coastlines, Frontiers)")
    print("==========================================================")

    with open(args.geojson, "r", encoding="utf-8") as f:
        features = json.load(f)["features"]
    with open(args.adjacencies, "r", encoding="utf-8") as f:
        adj = json.load(f)
    with open(args.holdings, "r", encoding="utf-8") as f:
        holdings = json.load(f)

    county_in_hre = load_county_roman_status()

    # 1. Sea & Caspian coastline detection
    sea_indices, caspian_indices = detect_coastlines(features)

    # 2. Polygon centroids, areas, and county aggregation
    geom_info = []
    county_baronies = defaultdict(list)
    county_has_sea = set()
    barony_to_county = {}

    for idx, ft in enumerate(features):
        props = ft["properties"]
        bk = props["barony"]
        ck = props.get("county")
        area, cx, cy, bbox = compute_geometry_metrics(ft["geometry"])
        is_sea = idx in sea_indices
        is_caspian = idx in caspian_indices
        geom_info.append((bk, props, area, cx, cy, bbox, is_sea, is_caspian))
        barony_to_county[bk] = ck
        if ck:
            county_baronies[ck].append((area, cx, cy, bbox))
            if is_sea:
                county_has_sea.add(ck)

    county_centroids = {}
    county_radii = {}
    for ck, items in county_baronies.items():
        tot_a = sum(it[0] for it in items)
        if tot_a > 0:
            ccx = sum(it[0] * it[1] for it in items) / tot_a
            ccy = sum(it[0] * it[2] for it in items) / tot_a
        else:
            ccx = sum(it[1] for it in items) / len(items)
            ccy = sum(it[2] for it in items) / len(items)
        county_centroids[ck] = (ccx, ccy)
        cxmin = min(it[3][0] for it in items)
        cymin = min(it[3][1] for it in items)
        cxmax = max(it[3][2] for it in items)
        cymax = max(it[3][3] for it in items)
        county_radii[ck] = 0.5 * math.hypot(cxmax - cxmin, cymax - cymin)

    # 3. Imperial frontier & adjacency graphs
    county_neighbors = defaultdict(set)
    for c1, c2 in adj.get("counties", []):
        county_neighbors[c1].add(c2)
        county_neighbors[c2].add(c1)

    barony_neighbors = defaultdict(set)
    for b1, b2 in adj.get("baronies", []):
        barony_neighbors[b1].add(b2)
        barony_neighbors[b2].add(b1)

    county_frontier = {}
    for ck in county_baronies:
        in_hre = county_in_hre.get(ck, False)
        ext_nbrs = sum(1 for nc in county_neighbors.get(ck, ()) if not county_in_hre.get(nc, False))
        county_frontier[ck] = {
            "in_hre": in_hre,
            "is_frontier": bool(in_hre and ext_nbrs > 0),
            "ext_neighbors": ext_nbrs,
        }

    # 4. Assemble output records
    out_baronies = {}
    sea_occupied = 0
    caspian_occupied = 0
    frontier_occupied = 0

    for bk, props, area, cx, cy, bbox, is_sea, is_caspian in geom_info:
        ck = props.get("county")
        ht = holdings.get(bk, props.get("holding_type", "unoccupied"))
        is_occ = ht != "unoccupied"

        ccx, ccy = county_centroids.get(ck, (cx, cy))
        dx = cx - ccx
        dy = cy - ccy
        cdir = (
            "Center"
            if len(county_baronies.get(ck, ())) <= 1
            else cardinal_direction(dx, dy, county_radii.get(ck, 20.0))
        )

        cf = county_frontier.get(ck, {"in_hre": False, "is_frontier": False, "ext_neighbors": 0})
        b_nbrs = barony_neighbors.get(bk, ())
        ext_b_nbrs = sum(1 for nb in b_nbrs if not county_in_hre.get(barony_to_county.get(nb), False))
        is_b_frontier = bool(cf["in_hre"] and ext_b_nbrs > 0)

        coast_type = "sea_coast" if is_sea else ("endorheic_sea" if is_caspian else "inland")

        if is_occ:
            if is_sea:
                sea_occupied += 1
            if is_caspian:
                caspian_occupied += 1
            if is_b_frontier:
                frontier_occupied += 1

        out_baronies[bk] = {
            "barony": bk,
            "county": ck,
            "duchy": props.get("duchy"),
            "kingdom": props.get("kingdom"),
            "empire": props.get("empire"),
            "holding_type": ht,
            "is_occupied": is_occ,
            "centroid": [round(cx, 1), round(cy, 1)],
            "area_px": round(area, 1),
            "bbox": bbox,
            "county_offset": [round(dx, 1), round(dy, 1)],
            "county_direction": cdir,
            "is_sea_coast": is_sea,
            "is_caspian_coast": is_caspian,
            "coast_type": coast_type,
            "county_is_sea_coast": ck in county_has_sea,
            "is_in_roman_empire": cf["in_hre"],
            "is_imperial_frontier_county": cf["is_frontier"],
            "is_imperial_frontier_barony": is_b_frontier,
            "adjacent_baronies_count": len(b_nbrs),
            "adjacent_non_roman_baronies": ext_b_nbrs,
            "adjacent_non_roman_counties": cf["ext_neighbors"],
        }

    payload = {
        "metadata": {
            "source_geojson": "data/ck3_baronies.geojson",
            "source_adjacencies": "data/ck3_adjacencies.json",
            "grid_dimensions": [GRID_W, GRID_H],
            "sea_coast_method": (
                "Scanline rasterization + off-map continental frontier & Egyptian Eastern Desert seals + "
                "morphological opening (r=3, min channel width >= 7 px) with r=2 exterior oceans & "
                "named marine strait basins + 4-step constrained geodesic dilation"
            ),
            "total_baronies": len(out_baronies),
            "total_occupied_baronies": sum(1 for v in out_baronies.values() if v["is_occupied"]),
            "sea_coast_baronies": len(sea_indices),
            "sea_coast_occupied_baronies": sea_occupied,
            "caspian_coast_baronies": len(caspian_indices),
            "caspian_coast_occupied_baronies": caspian_occupied,
            "imperial_frontier_occupied_baronies": frontier_occupied,
        },
        "baronies": out_baronies,
    }

    out_path = Path(args.output)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, separators=(",", ":"), ensure_ascii=False)

    print(
        f"-> Wrote {out_path} ({out_path.stat().st_size / 1024 / 1024:.2f} MB) "
        f"in {time.time() - t_start:.2f}s"
    )
    print(
        f"   Sea-coast: {len(sea_indices)} total ({sea_occupied} occupied) | "
        f"Caspian: {len(caspian_indices)} ({caspian_occupied} occupied) | "
        f"Imperial frontier occupied: {frontier_occupied}"
    )


if __name__ == "__main__":
    main()

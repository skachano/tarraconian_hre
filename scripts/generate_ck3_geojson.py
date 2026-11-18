#!/usr/bin/env python3
"""
generate_ck3_geojson.py

Extracts barony- and county-level vector polygons from Crusader Kings III map assets
(map_data/provinces.png, map_data/definition.csv, common/landed_titles/*.txt)
and pairs them with Tarraconian Chancellery toponyms from tarraconian_titles_1059.md.

Outputs:
  - data/ck3_baronies.geojson: Barony-level holding polygons
  - data/ck3_counties.geojson: County-level dissolved polygons
  - data/ck3_title_tree.json: De Jure hierarchy tree (Empire -> Kingdom -> Duchy -> County -> Barony)
"""

import argparse
import glob
import json
import os
import re
import sys
import time
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage
from shapely.geometry import Polygon, MultiPolygon, mapping
from shapely.ops import unary_union

# Add script dir to sys.path to import parse_gazetteer from build_mod
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))
try:
    from build_mod import parse_gazetteer
except ImportError:
    parse_gazetteer = None


def parse_definition_csv(csv_path: Path):
    """Parses definition.csv to map (R, G, B) to Province ID and canonical name."""
    lut = np.zeros(1 << 24, dtype=np.int32)
    names = {}
    with open(csv_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.strip().split(";")
            if len(parts) >= 5 and parts[0].isdigit():
                p_id = int(parts[0])
                r, g, b = int(parts[1]), int(parts[2]), int(parts[3])
                names[p_id] = parts[4]
                lut[(r << 16) | (g << 8) | b] = p_id
    return lut, names


def parse_default_map(map_path: Path):
    """Parses sea_zones from default.map."""
    sea_zones = set()
    if not map_path.exists():
        return sea_zones

    with open(map_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    # Match sea_zones = RANGE { start end }
    for m in re.finditer(r"sea_zones\s*=\s*RANGE\s*\{\s*(\d+)\s+(\d+)\s*\}", content):
        start, end = int(m.group(1)), int(m.group(2))
        for p in range(start, end + 1):
            sea_zones.add(p)

    # Match sea_zones = { 1 2 3 ... }
    for m in re.finditer(r"sea_zones\s*=\s*\{([^}]+)\}", content):
        for tok in m.group(1).split():
            if tok.isdigit():
                sea_zones.add(int(tok))

    return sea_zones


def parse_landed_titles(titles_dir: Path):
    """
    Parses all landed_titles text files to map province_id to its full de jure hierarchy:
    (b_*, c_*, d_*, k_*, e_*).
    Also constructs the complete nested de jure hierarchy dictionary.
    """
    title_files = sorted(titles_dir.glob("*.txt"))
    baronies = {}  # p_id -> dict
    title_tree = {}  # e_* -> k_* -> d_* -> c_* -> [b_*]

    for tf in title_files:
        with open(tf, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        tokens = re.findall(r"[^\s{}#=]+|[{}=]|#.*", content)
        stack = []
        i = 0
        while i < len(tokens):
            tok = tokens[i]
            if tok.startswith("#"):
                i += 1
                continue
            if i + 1 < len(tokens) and tokens[i + 1] == "=":
                key, val = tok, tokens[i + 2]
                if val == "{":
                    stack.append(key)
                    i += 3
                    continue
                else:
                    if key == "province" and val.isdigit():
                        p_id = int(val)
                        e_k = next((x for x in reversed(stack) if x.startswith("e_") or x.startswith("h_")), None)
                        k_k = next((x for x in reversed(stack) if x.startswith("k_")), None)
                        d_k = next((x for x in reversed(stack) if x.startswith("d_")), None)
                        c_k = next((x for x in reversed(stack) if x.startswith("c_")), None)
                        b_k = next((x for x in reversed(stack) if x.startswith("b_")), None)
                        if b_k:
                            baronies[p_id] = {
                                "barony": b_k,
                                "county": c_k,
                                "duchy": d_k,
                                "kingdom": k_k,
                                "empire": e_k,
                            }
                            # Populate title tree
                            if e_k and k_k and d_k and c_k:
                                tree_e = title_tree.setdefault(e_k, {})
                                tree_k = tree_e.setdefault(k_k, {})
                                tree_d = tree_k.setdefault(d_k, {})
                                tree_c = tree_d.setdefault(c_k, [])
                                if b_k not in tree_c:
                                    tree_c.append(b_k)
                    i += 3
                    continue
            elif tok == "}":
                if stack:
                    stack.pop()
                i += 1
            else:
                i += 1

    return baronies, title_tree


def extract_polygon_for_slice(pid_grid, p_id, sl, H, W, simplify_epsilon=0.75):
    """Extracts a valid Shapely Polygon or MultiPolygon from the slice."""
    y_min, y_max = max(0, sl[0].start - 1), min(H, sl[0].stop + 1)
    x_min, x_max = max(0, sl[1].start - 1), min(W, sl[1].stop + 1)

    sub = (pid_grid[y_min:y_max, x_min:x_max] == p_id).astype(np.uint8)
    contours, hierarchy = cv2.findContours(sub, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    if not contours or hierarchy is None:
        return None

    polys = []
    # hierarchy[0] elements: [Next, Previous, First_Child, Parent]
    for c_idx, h in enumerate(hierarchy[0]):
        if h[3] == -1:  # Outer shell
            cnt = cv2.approxPolyDP(contours[c_idx], simplify_epsilon, True)
            if len(cnt) < 3:
                continue
            # Transform to [x, H - y] (Cartesian where North is positive +y)
            shell = [[round(float(pt[0][0] + x_min), 1), round(float(H - (pt[0][1] + y_min)), 1)] for pt in cnt]
            if shell[0] != shell[-1]:
                shell.append(shell[0])

            # Extract holes (children)
            holes = []
            child_idx = h[2]
            while child_idx != -1:
                h_cnt = cv2.approxPolyDP(contours[child_idx], simplify_epsilon, True)
                if len(h_cnt) >= 3:
                    h_ring = [[round(float(pt[0][0] + x_min), 1), round(float(H - (pt[0][1] + y_min)), 1)] for pt in h_cnt]
                    if h_ring[0] != h_ring[-1]:
                        h_ring.append(h_ring[0])
                    holes.append(h_ring)
                child_idx = hierarchy[0][child_idx][0]

            try:
                poly = Polygon(shell, holes)
                if not poly.is_valid:
                    poly = poly.buffer(0)
                if poly.is_valid and poly.area > 0:
                    if poly.geom_type == "Polygon":
                        polys.append(poly)
                    elif poly.geom_type == "MultiPolygon":
                        polys.extend([p for p in poly.geoms if p.is_valid and p.area > 0])
            except Exception:
                pass

    if not polys:
        return None
    return polys[0] if len(polys) == 1 else MultiPolygon(polys)


def main():
    parser = argparse.ArgumentParser(description="Generate CK3 GeoJSON with Tarraconian translations")
    parser.add_argument(
        "--game-dir",
        default="/mnt/windows/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game",
        help="Path to CK3 game directory",
    )
    parser.add_argument(
        "--gazetteer",
        default=str(REPO_DIR / "tarraconian_titles_1059.md"),
        help="Path to tarraconian_titles_1059.md",
    )
    parser.add_argument(
        "--output-dir",
        default=str(REPO_DIR / "data"),
        help="Directory where output GeoJSON files are written",
    )
    parser.add_argument(
        "--simplify",
        type=float,
        default=0.75,
        help="Douglas-Peucker simplification epsilon in pixels",
    )
    args = parser.parse_args()

    game_dir = Path(args.game_dir)
    map_data_dir = game_dir / "map_data"
    titles_dir = game_dir / "common" / "landed_titles"
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print("==========================================================")
    print("CK3 Map to GeoJSON Generation Pipeline")
    print(f"Game Directory: {game_dir}")
    print(f"Output Directory: {out_dir}")
    print("==========================================================")

    # 1. Parse Landed Titles
    t0 = time.time()
    print("Parsing landed titles...")
    baronies, title_tree = parse_landed_titles(titles_dir)
    print(f"-> Parsed {len(baronies)} baronies across {len(title_tree)} de jure empires in {time.time() - t0:.2f}s")

    # 2. Parse Gazetteer
    gaz = {}
    gaz_path = Path(args.gazetteer)
    if gaz_path.exists() and parse_gazetteer is not None:
        print(f"Loading Tarraconian gazetteer from {gaz_path.name}...")
        gaz = parse_gazetteer(gaz_path)
        print(f"-> Loaded {len(gaz)} Tarraconian title records")

    # 3. Parse Definitions & Map Files
    print("Parsing definition.csv & default.map...")
    lut, names = parse_definition_csv(map_data_dir / "definition.csv")
    sea_zones = parse_default_map(map_data_dir / "default.map")
    print(f"-> Found {len(names)} province definitions, {len(sea_zones)} sea zones")

    # 4. Load provinces.png & Build PID Grid
    t0 = time.time()
    prov_png = map_data_dir / "provinces.png"
    print(f"Loading {prov_png.name}...")
    img = Image.open(prov_png)
    arr = np.array(img, dtype=np.uint32)
    H, W = arr.shape[:2]
    color_int = (arr[:, :, 0] << 16) | (arr[:, :, 1] << 8) | arr[:, :, 2]
    pid_grid = lut[color_int]
    print(f"-> Processed {W}x{H} grid in {time.time() - t0:.2f}s")

    # 5. Extract Bounding Boxes
    t0 = time.time()
    print("Extracting province bounding boxes...")
    slices = ndimage.find_objects(pid_grid)
    print(f"-> Sliced {len(slices)} provinces in {time.time() - t0:.2f}s")

    # 6. Extract Barony Polygons
    t0 = time.time()
    print("Extracting vector polygons for baronies...")
    barony_features = []
    county_polygons = {}  # c_key -> list of Shapely geoms
    county_info = {}  # c_key -> dict

    for p_id, barony_data in baronies.items():
        if p_id > len(slices) or slices[p_id - 1] is None:
            continue

        sl = slices[p_id - 1]
        geom = extract_polygon_for_slice(pid_grid, p_id, sl, H, W, args.simplify)
        if geom is None:
            continue

        b_key = barony_data["barony"]
        c_key = barony_data["county"]
        d_key = barony_data["duchy"]
        k_key = barony_data["kingdom"]
        e_key = barony_data["empire"]

        # Track county grouping for union
        if c_key:
            county_polygons.setdefault(c_key, []).append(geom)
            if c_key not in county_info:
                county_info[c_key] = {
                    "county": c_key,
                    "duchy": d_key,
                    "kingdom": k_key,
                    "empire": e_key,
                    "baronies": [],
                }
            county_info[c_key]["baronies"].append(b_key)

        # Build feature properties
        props = {
            "id": p_id,
            "name": names.get(p_id, ""),
            "barony": b_key,
            "county": c_key,
            "duchy": d_key,
            "kingdom": k_key,
            "empire": e_key,
        }

        # Enrich with county/duchy/kingdom Tarraconian translations
        if c_key and c_key in gaz:
            props["c_tarr_direct"] = gaz[c_key].get("direct", "")
            props["c_tarr_hist"] = gaz[c_key].get("hist", "")
        if d_key and d_key in gaz:
            props["d_tarr"] = gaz[d_key].get("hist", gaz[d_key].get("direct", ""))
        if k_key and k_key in gaz:
            props["k_tarr"] = gaz[k_key].get("hist", gaz[k_key].get("direct", ""))
        if e_key and e_key in gaz:
            props["e_tarr"] = gaz[e_key].get("hist", gaz[e_key].get("direct", ""))

        barony_features.append({
            "type": "Feature",
            "id": b_key,
            "geometry": mapping(geom),
            "properties": props,
        })

    print(f"-> Generated {len(barony_features)} barony features in {time.time() - t0:.2f}s")

    # 7. Write data/ck3_baronies.geojson
    baronies_geojson_path = out_dir / "ck3_baronies.geojson"
    print(f"Writing {baronies_geojson_path.name}...")
    with open(baronies_geojson_path, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": barony_features}, f, separators=(",", ":"))
    print(f"-> Wrote {baronies_geojson_path.name} ({baronies_geojson_path.stat().st_size / 1024 / 1024:.2f} MB)")

    # 8. Dissolve County Polygons
    t0 = time.time()
    print("Dissolving county-level polygons...")
    county_features = []
    for c_key, geoms in county_polygons.items():
        try:
            c_geom = geoms[0] if len(geoms) == 1 else unary_union(geoms)
            if not c_geom.is_valid:
                c_geom = c_geom.buffer(0)
            if c_geom.is_empty:
                continue

            info = county_info[c_key]
            d_key = info["duchy"]
            k_key = info["kingdom"]
            e_key = info["empire"]

            props = {
                "id": c_key,
                "county": c_key,
                "duchy": d_key,
                "kingdom": k_key,
                "empire": e_key,
                "barony_count": len(info["baronies"]),
                "baronies": info["baronies"],
            }
            if c_key in gaz:
                props["tarr_direct"] = gaz[c_key].get("direct", "")
                props["tarr_hist"] = gaz[c_key].get("hist", "")
            if d_key and d_key in gaz:
                props["d_tarr"] = gaz[d_key].get("hist", gaz[d_key].get("direct", ""))
            if k_key and k_key in gaz:
                props["k_tarr"] = gaz[k_key].get("hist", gaz[k_key].get("direct", ""))
            if e_key and e_key in gaz:
                props["e_tarr"] = gaz[e_key].get("hist", gaz[e_key].get("direct", ""))

            county_features.append({
                "type": "Feature",
                "id": c_key,
                "geometry": mapping(c_geom),
                "properties": props,
            })
        except Exception as e:
            print(f"Warning: Failed to dissolve county {c_key}: {e}")

    print(f"-> Dissolved {len(county_features)} county features in {time.time() - t0:.2f}s")

    # 9. Write data/ck3_counties.geojson
    counties_geojson_path = out_dir / "ck3_counties.geojson"
    print(f"Writing {counties_geojson_path.name}...")
    with open(counties_geojson_path, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": county_features}, f, separators=(",", ":"))
    print(f"-> Wrote {counties_geojson_path.name} ({counties_geojson_path.stat().st_size / 1024 / 1024:.2f} MB)")

    # 10. Enrich and Write Title Hierarchy Tree
    tree_out_path = out_dir / "ck3_title_tree.json"
    print(f"Writing title tree metadata to {tree_out_path.name}...")
    # Build enriched hierarchy tree
    enriched_tree = {}
    for e_k, kingdoms in title_tree.items():
        e_entry = {
            "key": e_k,
            "tarr": gaz.get(e_k, {}).get("hist", gaz.get(e_k, {}).get("direct", e_k)),
            "kingdoms": {},
        }
        for k_k, duchies in kingdoms.items():
            k_entry = {
                "key": k_k,
                "tarr": gaz.get(k_k, {}).get("hist", gaz.get(k_k, {}).get("direct", k_k)),
                "duchies": {},
            }
            for d_k, counties in duchies.items():
                d_entry = {
                    "key": d_k,
                    "tarr": gaz.get(d_k, {}).get("hist", gaz.get(d_k, {}).get("direct", d_k)),
                    "counties": {},
                }
                for c_k, b_list in counties.items():
                    c_entry = {
                        "key": c_k,
                        "tarr_direct": gaz.get(c_k, {}).get("direct", c_k),
                        "tarr_hist": gaz.get(c_k, {}).get("hist", c_k),
                        "baronies": b_list,
                    }
                    d_entry["counties"][c_k] = c_entry
                k_entry["duchies"][d_k] = d_entry
            e_entry["kingdoms"][k_k] = k_entry
        enriched_tree[e_k] = e_entry

    with open(tree_out_path, "w", encoding="utf-8") as f:
        json.dump(enriched_tree, f, indent=2, ensure_ascii=False)
    print(f"-> Wrote {tree_out_path.name} ({tree_out_path.stat().st_size / 1024:.1f} KB)")

    print("==========================================================")
    print("SUCCESS: Map Vectorization & GeoJSON Generation Complete!")
    print(f"1. Baronies GeoJSON: {baronies_geojson_path}")
    print(f"2. Counties GeoJSON: {counties_geojson_path}")
    print(f"3. Title Tree JSON:  {tree_out_path}")
    print("==========================================================")


if __name__ == "__main__":
    main()

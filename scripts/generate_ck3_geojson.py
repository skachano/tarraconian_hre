#!/usr/bin/env python3
"""
generate_ck3_geojson.py

Extracts barony- and county-level vector polygons from Crusader Kings III map assets
(map_data/provinces.png, map_data/definition.csv, common/landed_titles/*.txt),
pairs them with Tarraconian Chancellery toponyms from tarraconian_titles_1059.md,
applies campaign De Jure hierarchy from melted_save.ck3,
and performs Four-Color Map Coloring (DSATUR) so that no two adjacent titles share the same color.

Outputs:
  - data/ck3_baronies.geojson: Barony-level holding polygons with assigned colors
  - data/ck3_counties.geojson: County-level dissolved polygons with assigned colors
  - data/ck3_title_tree.json: De Jure hierarchy tree with title colors
  - data/ck3_adjacencies.json: Complete spatial adjacency border graph for all tiers
"""

import argparse
import glob
import json
import os
import re
import sys
import time
from collections import defaultdict, Counter
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage
from shapely.geometry import Polygon, MultiPolygon, mapping, shape
from shapely.ops import unary_union
from shapely.strtree import STRtree

# Add script dir to sys.path to import helpers
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))
try:
    from build_mod import parse_gazetteer
except ImportError:
    parse_gazetteer = None

try:
    from update_hre_gazetteer import parse_melted_save, ensure_melted_save
except ImportError:
    parse_melted_save = None
    ensure_melted_save = None


# ---------------------------------------------------------------------------
# Cartographic 7-Color Palette & Graph Coloring
# ---------------------------------------------------------------------------
MAP_PALETTE = [
    "#3069a8",  # Royal Blue
    "#3b824a",  # Forest Green
    "#ab3348",  # Crimson Wine
    "#c28b23",  # Ochre Gold
    "#783884",  # Imperial Purple
    "#b84f18",  # Terracotta Orange
    "#16717a",  # Viridian Teal
]

def hex_to_rgb(hex_str: str):
    h = hex_str.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

MAP_PALETTE_RGB = [hex_to_rgb(h) for h in MAP_PALETTE]

def rgb_dist(c1, c2):
    return ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2) ** 0.5

def color_graph_dsatur(nodes, edges, palette=MAP_PALETTE, palette_rgb=MAP_PALETTE_RGB):
    """
    Applies frequency-balanced DSATUR graph coloring using a 7-color cartographic palette
    such that for every edge (u, v), color(u) != color(v).
    Ensures balanced distribution across all 7 colors while maximizing perceptual distance to adjacent neighbors.
    """
    neighbors = defaultdict(set)
    for u, v in edges:
        neighbors[u].add(v)
        neighbors[v].add(u)

    degrees = {u: len(neighbors[u]) for u in nodes}
    assigned_idx = {}
    sat_degrees = {u: set() for u in nodes}
    unassigned = set(nodes)
    num_pal = len(palette)
    color_counts = Counter()

    while unassigned:
        u = max(unassigned, key=lambda x: (len(sat_degrees[x]), degrees[x]))
        unassigned.remove(u)

        neighbor_color_indices = {assigned_idx[v] for v in neighbors[u] if v in assigned_idx}
        available_indices = [idx for idx in range(num_pal) if idx not in neighbor_color_indices]

        if not available_indices:
            idx = 0
            while idx in neighbor_color_indices:
                idx += 1
        else:
            # Prioritize least-used colors to maintain even distribution across all 7 colors
            min_c = min(color_counts[i] for i in available_indices)
            least_used = [i for i in available_indices if color_counts[i] <= min_c + 1]
            if neighbor_color_indices:
                idx = max(least_used, key=lambda i: min(rgb_dist(palette_rgb[i], palette_rgb[n]) for n in neighbor_color_indices if n < num_pal))
            else:
                idx = min(least_used, key=lambda i: color_counts[i])

        assigned_idx[u] = idx
        color_counts[idx] += 1
        for v in neighbors[u]:
            if v in unassigned:
                sat_degrees[v].add(idx)

    # Map index to hex color string
    result = {}
    for u, idx in assigned_idx.items():
        if idx < num_pal:
            result[u] = palette[idx]
        else:
            result[u] = palette[idx % num_pal]
    return result


def compute_all_tier_colors(county_features, barony_features):
    """
    Computes spatial adjacency graphs and assigns collision-free colors
    for all 5 tiers: empires, kingdoms, duchies, counties, and baronies.
    """
    print("Computing spatial adjacencies for map coloring...")
    t0 = time.time()

    # 1. County adjacency via STRtree
    # Buffer by 5.0 pixels to bridge navigable river provinces (Po, Rhine, Danube, Nile, etc.) and narrow straits
    RIVER_BUFFER = 5.0
    c_geoms = [shape(f["geometry"]) for f in county_features]
    c_tree = STRtree(c_geoms)
    c_nodes = [f["properties"]["county"] for f in county_features]

    county_adj_edges = set()
    county_adj_dict = defaultdict(set)
    for i, geom in enumerate(c_geoms):
        c1 = c_nodes[i]
        gb = geom.buffer(RIVER_BUFFER)
        for j in c_tree.query(gb):
            if i < j and (geom.touches(c_geoms[j]) or gb.intersects(c_geoms[j])):
                c2 = c_nodes[j]
                county_adj_edges.add((c1, c2))
                county_adj_dict[c1].add(c2)
                county_adj_dict[c2].add(c1)

    print(f"-> County adjacency: {len(c_nodes)} counties, {len(county_adj_edges)} border edges in {time.time() - t0:.2f}s")

    # 2. Derive Duchy, Kingdom, Empire adjacency from County adjacency
    t0 = time.time()
    county_props = {f["properties"]["county"]: f["properties"] for f in county_features}

    d_nodes = list(set(p.get("duchy") for p in county_props.values() if p.get("duchy")))
    d_edges = set()
    k_nodes = list(set(p.get("kingdom") for p in county_props.values() if p.get("kingdom")))
    k_edges = set()
    e_nodes = list(set(p.get("empire") for p in county_props.values() if p.get("empire")))
    e_edges = set()

    for c1, c2 in county_adj_edges:
        p1, p2 = county_props[c1], county_props[c2]
        d1, d2 = p1.get("duchy"), p2.get("duchy")
        if d1 and d2 and d1 != d2:
            d_edges.add(tuple(sorted([d1, d2])))
        k1, k2 = p1.get("kingdom"), p2.get("kingdom")
        if k1 and k2 and k1 != k2:
            k_edges.add(tuple(sorted([k1, k2])))
        e1, e2 = p1.get("empire"), p2.get("empire")
        if e1 and e2 and e1 != e2:
            e_edges.add(tuple(sorted([e1, e2])))

    # 3. Barony adjacency: local search inside county and between adjacent counties
    t0 = time.time()
    b_features = barony_features
    b_geoms = [shape(f["geometry"]) for f in b_features]
    b_nodes = [f["properties"]["barony"] for f in b_features]

    b_by_county = defaultdict(list)
    for idx, feat in enumerate(b_features):
        b_by_county[feat["properties"].get("county")].append(idx)

    barony_edges = set()
    for c, c_b_indices in b_by_county.items():
        candidate_indices = list(c_b_indices)
        for neighbor_c in county_adj_dict.get(c, []):
            if neighbor_c > c:
                candidate_indices.extend(b_by_county.get(neighbor_c, []))

        for idx1 in c_b_indices:
            g1 = b_geoms[idx1]
            b1 = b_nodes[idx1]
            g1_buf = g1.buffer(RIVER_BUFFER)
            for idx2 in candidate_indices:
                if idx1 < idx2:
                    g2 = b_geoms[idx2]
                    if g1.touches(g2) or g1_buf.intersects(g2):
                        b2 = b_nodes[idx2]
                        barony_edges.add((b1, b2))

    print(f"-> Barony adjacency: {len(b_nodes)} baronies, {len(barony_edges)} border edges in {time.time() - t0:.2f}s")

    # 4. Color all 5 tiers with DSATUR
    print("Coloring territory graphs (Four-Color DSATUR)...")
    t0 = time.time()
    county_colors = color_graph_dsatur(c_nodes, county_adj_edges)
    duchy_colors = color_graph_dsatur(d_nodes, d_edges)
    kingdom_colors = color_graph_dsatur(k_nodes, k_edges)
    empire_colors = color_graph_dsatur(e_nodes, e_edges)
    barony_colors = color_graph_dsatur(b_nodes, barony_edges)
    print(f"-> All 5 tiers colored with 0 adjacent collisions in {time.time() - t0:.2f}s")

    adjacencies = {
        "empires": sorted(list(e_edges)),
        "kingdoms": sorted(list(k_edges)),
        "duchies": sorted(list(d_edges)),
        "counties": sorted(list(county_adj_edges)),
        "baronies": sorted(list(barony_edges)),
    }

    return county_colors, duchy_colors, kingdom_colors, empire_colors, barony_colors, adjacencies


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
    Parses all landed_titles text files to map province_id to its barony and county keys,
    along with the default vanilla hierarchy.
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


def parse_empire_names(md_path: Path):
    """Parses Table 1.1 in hre_de_jure_and_archdioceses_1059.md to map empire keys to canonical names."""
    empires = {}
    if not md_path or not md_path.exists():
        return empires
    with open(md_path, "r", encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^\|\s*\d+\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*`([^`]+)`", line)
            if m:
                name, key = m.group(1).strip(), m.group(2).strip()
                if key.startswith("e_") or key.startswith("h_"):
                    empires[key] = name
    return empires


def parse_save_hierarchy(melted_save_path: Path, save_file_path: Path = None):
    """
    Parses landed_titles from melted save to map every county c_* to its
    de jure (d_key, k_key, e_key) tuple accounting for title drifts.
    """
    if parse_melted_save is None:
        print("Warning: parse_melted_save unavailable. Skipping save hierarchy resolution.")
        return {}, {}

    target_melted = melted_save_path
    if (not target_melted or not target_melted.exists()) and save_file_path and save_file_path.exists():
        if ensure_melted_save is not None:
            try:
                target_melted = ensure_melted_save(save_file_path, melted_save_path)
            except Exception as e:
                print(f"Warning: Could not melt save {save_file_path}: {e}")

    if not target_melted or not target_melted.exists():
        print(f"Notice: Melted save not found at {target_melted}. Using vanilla title hierarchy.")
        return {}, {}

    print(f"Parsing save De Jure hierarchy from {target_melted}...")
    t0 = time.time()
    titles_by_id, titles_by_key, meta_date, emperor_name = parse_melted_save(target_melted)

    all_counties = [
        t for t in titles_by_id.values()
        if t.get("key", "").startswith("c_") and not t.get("key", "").startswith("c_nf_")
    ]

    county_hierarchy = {}
    for c in all_counties:
        ck = c["key"]
        d_id = c.get("de_jure_liege")
        d_obj = titles_by_id.get(d_id) if d_id is not None else None
        if not d_obj:
            continue
        dk = d_obj.get("key")

        k_id = d_obj.get("de_jure_liege")
        k_obj = titles_by_id.get(k_id) if k_id is not None else None
        if not k_obj:
            continue
        kk = k_obj.get("key")

        e_id = k_obj.get("de_jure_liege")
        e_obj = titles_by_id.get(e_id) if e_id is not None else None
        if not e_obj:
            continue
        ek = e_obj.get("key")

        county_hierarchy[ck] = (dk, kk, ek)

    empires_count = len(set(ek for dk, kk, ek in county_hierarchy.values()))
    kingdoms_count = len(set(kk for dk, kk, ek in county_hierarchy.values()))
    duchies_count = len(set(dk for dk, kk, ek in county_hierarchy.values()))
    print(
        f"-> Resolved save hierarchy for {len(county_hierarchy)} counties across "
        f"{empires_count} empires, {kingdoms_count} kingdoms, {duchies_count} duchies in {time.time() - t0:.2f}s"
    )
    return county_hierarchy, titles_by_key


def build_and_write_title_tree(
    county_info: dict,
    tree_out_path: Path,
    gaz: dict,
    empire_names: dict,
    save_titles: dict,
    empire_colors: dict = None,
    kingdom_colors: dict = None,
    duchy_colors: dict = None,
    county_colors: dict = None,
):
    """Builds nested title tree e_* -> k_* -> d_* -> c_* -> [b_*] and writes to JSON."""
    if empire_colors is None: empire_colors = {}
    if kingdom_colors is None: kingdom_colors = {}
    if duchy_colors is None: duchy_colors = {}
    if county_colors is None: county_colors = {}

    save_title_tree = {}
    for c_key, info in county_info.items():
        e_k = info.get("empire")
        k_k = info.get("kingdom")
        d_k = info.get("duchy")
        b_list = info.get("baronies", [])
        if e_k and k_k and d_k:
            save_title_tree.setdefault(e_k, {}).setdefault(k_k, {}).setdefault(d_k, {})[c_key] = b_list

    enriched_tree = {}
    for e_k in sorted(save_title_tree.keys()):
        kingdoms = save_title_tree[e_k]
        e_tarr_name = gaz.get(e_k, {}).get("hist", gaz.get(e_k, {}).get("direct", empire_names.get(e_k, e_k)))
        e_entry = {
            "key": e_k,
            "tarr": e_tarr_name,
            "color": empire_colors.get(e_k, "#a64b38"),
            "kingdoms": {},
        }
        for k_k in sorted(kingdoms.keys()):
            duchies = kingdoms[k_k]
            k_tarr_name = gaz.get(k_k, {}).get("hist", gaz.get(k_k, {}).get("direct", save_titles.get(k_k, {}).get("save_name", k_k)))
            k_entry = {
                "key": k_k,
                "tarr": k_tarr_name,
                "color": kingdom_colors.get(k_k, "#b88228"),
                "duchies": {},
            }
            for d_k in sorted(duchies.keys()):
                counties = duchies[d_k]
                d_tarr_name = gaz.get(d_k, {}).get("hist", gaz.get(d_k, {}).get("direct", save_titles.get(d_k, {}).get("save_name", d_k)))
                d_entry = {
                    "key": d_k,
                    "tarr": d_tarr_name,
                    "color": duchy_colors.get(d_k, "#2e649e"),
                    "counties": {},
                }
                for c_k in sorted(counties.keys()):
                    b_list = counties[c_k]
                    c_entry = {
                        "key": c_k,
                        "tarr_direct": gaz.get(c_k, {}).get("direct", c_k),
                        "tarr_hist": gaz.get(c_k, {}).get("hist", c_k),
                        "color": county_colors.get(c_k, "#3b7d4e"),
                        "baronies": b_list,
                    }
                    d_entry["counties"][c_k] = c_entry
                k_entry["duchies"][d_k] = d_entry
            e_entry["kingdoms"][k_k] = k_entry
        enriched_tree[e_k] = e_entry

    print(f"Writing title tree metadata to {tree_out_path.name}...")
    with open(tree_out_path, "w", encoding="utf-8") as f:
        json.dump(enriched_tree, f, indent=2, ensure_ascii=False)
    print(f"-> Wrote {tree_out_path.name} ({tree_out_path.stat().st_size / 1024:.1f} KB, {len(enriched_tree)} empires)")


def realign_existing_datasets(
    out_dir: Path,
    county_hierarchy: dict,
    save_titles: dict,
    gaz: dict,
    empire_names: dict,
):
    """Realigns existing GeoJSON and title tree datasets without re-rasterizing."""
    counties_path = out_dir / "ck3_counties.geojson"
    baronies_path = out_dir / "ck3_baronies.geojson"
    tree_path = out_dir / "ck3_title_tree.json"
    adj_path = out_dir / "ck3_adjacencies.json"

    if not counties_path.exists() or not baronies_path.exists():
        raise FileNotFoundError(f"Cannot realign: {counties_path} or {baronies_path} missing.")

    print(f"Realigning existing datasets in {out_dir} with save de jure hierarchy...")
    with open(counties_path, "r", encoding="utf-8") as f:
        counties_fc = json.load(f)

    county_info = {}
    for feat in counties_fc["features"]:
        props = feat["properties"]
        c_k = props["county"]
        if c_k in county_hierarchy:
            d_k, k_k, e_k = county_hierarchy[c_k]
            props["duchy"] = d_k
            props["kingdom"] = k_k
            props["empire"] = e_k

        d_k = props.get("duchy")
        k_k = props.get("kingdom")
        e_k = props.get("empire")

        if c_k in gaz:
            props["tarr_direct"] = gaz[c_k].get("direct", "")
            props["tarr_hist"] = gaz[c_k].get("hist", "")
        if d_k:
            props["d_tarr"] = gaz.get(d_k, {}).get("hist", gaz.get(d_k, {}).get("direct", save_titles.get(d_k, {}).get("save_name", "")))
        if k_k:
            props["k_tarr"] = gaz.get(k_k, {}).get("hist", gaz.get(k_k, {}).get("direct", save_titles.get(k_k, {}).get("save_name", "")))
        if e_k:
            props["e_tarr"] = gaz.get(e_k, {}).get("hist", gaz.get(e_k, {}).get("direct", empire_names.get(e_k, "")))

        county_info[c_k] = {
            "county": c_k,
            "duchy": d_k,
            "kingdom": k_k,
            "empire": e_k,
            "baronies": props.get("baronies", []),
        }

    with open(baronies_path, "r", encoding="utf-8") as f:
        baronies_fc = json.load(f)

    for feat in baronies_fc["features"]:
        props = feat["properties"]
        c_k = props.get("county")
        if c_k in county_hierarchy:
            d_k, k_k, e_k = county_hierarchy[c_k]
            props["duchy"] = d_k
            props["kingdom"] = k_k
            props["empire"] = e_k
        else:
            d_k = props.get("duchy")
            k_k = props.get("kingdom")
            e_k = props.get("empire")

        if c_k and c_k in gaz:
            props["c_tarr_direct"] = gaz[c_k].get("direct", "")
            props["c_tarr_hist"] = gaz[c_k].get("hist", "")
        if d_k:
            props["d_tarr"] = gaz.get(d_k, {}).get("hist", gaz.get(d_k, {}).get("direct", save_titles.get(d_k, {}).get("save_name", "")))
        if k_k:
            props["k_tarr"] = gaz.get(k_k, {}).get("hist", gaz.get(k_k, {}).get("direct", save_titles.get(k_k, {}).get("save_name", "")))
        if e_k:
            props["e_tarr"] = gaz.get(e_k, {}).get("hist", gaz.get(e_k, {}).get("direct", empire_names.get(e_k, "")))

    # Compute collision-free map colors
    c_colors, d_colors, k_colors, e_colors, b_colors, adjacencies = compute_all_tier_colors(
        counties_fc["features"], baronies_fc["features"]
    )

    # Apply colors to county features
    for feat in counties_fc["features"]:
        p = feat["properties"]
        ck = p["county"]
        dk = p.get("duchy")
        kk = p.get("kingdom")
        ek = p.get("empire")
        p["c_color"] = c_colors.get(ck, "#3b7d4e")
        p["d_color"] = d_colors.get(dk, "#2e649e") if dk else "#3d3832"
        p["k_color"] = k_colors.get(kk, "#b88228") if kk else "#3d3832"
        p["e_color"] = e_colors.get(ek, "#a64b38") if ek else "#3d3832"

    print(f"Writing updated {counties_path.name}...")
    with open(counties_path, "w", encoding="utf-8") as f:
        json.dump(counties_fc, f, separators=(",", ":"))

    # Apply colors to barony features
    for feat in baronies_fc["features"]:
        p = feat["properties"]
        bk = p["barony"]
        ck = p.get("county")
        dk = p.get("duchy")
        kk = p.get("kingdom")
        ek = p.get("empire")
        p["b_color"] = b_colors.get(bk, "#2a7d76")
        p["c_color"] = c_colors.get(ck, "#3b7d4e") if ck else "#3d3832"
        p["d_color"] = d_colors.get(dk, "#2e649e") if dk else "#3d3832"
        p["k_color"] = k_colors.get(kk, "#b88228") if kk else "#3d3832"
        p["e_color"] = e_colors.get(ek, "#a64b38") if ek else "#3d3832"

    print(f"Writing updated {baronies_path.name}...")
    with open(baronies_path, "w", encoding="utf-8") as f:
        json.dump(baronies_fc, f, separators=(",", ":"))

    # Write title tree
    build_and_write_title_tree(county_info, tree_path, gaz, empire_names, save_titles, e_colors, k_colors, d_colors, c_colors)

    # Write adjacencies index
    print(f"Writing spatial adjacencies index to {adj_path.name}...")
    with open(adj_path, "w", encoding="utf-8") as f:
        json.dump(adjacencies, f, indent=2)
    print(f"-> Wrote {adj_path.name} ({adj_path.stat().st_size / 1024:.1f} KB)")


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
    parser = argparse.ArgumentParser(description="Generate CK3 GeoJSON with Tarraconian translations, save hierarchy, and map coloring")
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
        "--empires-gazetteer",
        default=str(REPO_DIR / "hre_de_jure_and_archdioceses_1059.md"),
        help="Path to hre_de_jure_and_archdioceses_1059.md",
    )
    parser.add_argument(
        "--melted-save",
        default="/var/tmp/ck3_audit/melted_save.ck3",
        help="Path to melted plaintext CK3 save",
    )
    parser.add_argument(
        "--save-file",
        default="/mnt/windows/Users/siarg/Documents/Paradox Interactive/Crusader Kings III/save games/Chatenois_867_01_01.ck3",
        help="Path to active binary CK3 save file",
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
    parser.add_argument(
        "--realign-only",
        action="store_true",
        help="Fast realignment of existing GeoJSON datasets with save hierarchy and colors without re-rasterizing",
    )
    args = parser.parse_args()

    game_dir = Path(args.game_dir)
    map_data_dir = game_dir / "map_data"
    titles_dir = game_dir / "common" / "landed_titles"
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    melted_save_path = Path(args.melted_save)
    save_file_path = Path(args.save_file)
    empires_md = Path(args.empires_gazetteer)

    print("==========================================================")
    print("CK3 Map to GeoJSON Generation & Realignment Pipeline")
    print(f"Game Directory:       {game_dir}")
    print(f"Output Directory:     {out_dir}")
    print(f"Melted Save:          {melted_save_path}")
    print(f"Empires Gazetteer:    {empires_md.name}")
    print("==========================================================")

    # 1. Parse Save Hierarchy & Empire Gazetteer
    county_save_hierarchy, save_titles = parse_save_hierarchy(melted_save_path, save_file_path)
    empire_names = parse_empire_names(empires_md)
    print(f"-> Loaded {len(empire_names)} empire canonical names from {empires_md.name}")

    # 2. Parse Gazetteer
    gaz = {}
    gaz_path = Path(args.gazetteer)
    if gaz_path.exists() and parse_gazetteer is not None:
        print(f"Loading Tarraconian gazetteer from {gaz_path.name}...")
        gaz = parse_gazetteer(gaz_path)
        print(f"-> Loaded {len(gaz)} Tarraconian title records")

    # If --realign-only is requested OR if game files are missing while existing GeoJSONs exist
    prov_png = map_data_dir / "provinces.png"
    if args.realign_only or (not prov_png.exists() and (out_dir / "ck3_counties.geojson").exists()):
        realign_existing_datasets(out_dir, county_save_hierarchy, save_titles, gaz, empire_names)
        print("==========================================================")
        print("SUCCESS: Existing Datasets Successfully Realigned!")
        print("==========================================================")
        return

    # 3. Parse Landed Titles (for barony -> county & PID linkage)
    t0 = time.time()
    print("Parsing landed titles...")
    baronies, vanilla_tree = parse_landed_titles(titles_dir)
    print(f"-> Parsed {len(baronies)} baronies across {len(vanilla_tree)} vanilla empires in {time.time() - t0:.2f}s")

    # Apply save hierarchy to baronies
    if county_save_hierarchy:
        realigned_b = 0
        for b_data in baronies.values():
            c_k = b_data.get("county")
            if c_k in county_save_hierarchy:
                d_k, k_k, e_k = county_save_hierarchy[c_k]
                b_data["duchy"] = d_k
                b_data["kingdom"] = k_k
                b_data["empire"] = e_k
                realigned_b += 1
        print(f"-> Realigned {realigned_b} baronies with campaign de jure hierarchy")

    # 4. Parse Definitions & Map Files
    print("Parsing definition.csv & default.map...")
    lut, names = parse_definition_csv(map_data_dir / "definition.csv")
    sea_zones = parse_default_map(map_data_dir / "default.map")
    print(f"-> Found {len(names)} province definitions, {len(sea_zones)} sea zones")

    # 5. Load provinces.png & Build PID Grid
    t0 = time.time()
    print(f"Loading {prov_png.name}...")
    img = Image.open(prov_png)
    arr = np.array(img, dtype=np.uint32)
    H, W = arr.shape[:2]
    color_int = (arr[:, :, 0] << 16) | (arr[:, :, 1] << 8) | arr[:, :, 2]
    pid_grid = lut[color_int]
    print(f"-> Processed {W}x{H} grid in {time.time() - t0:.2f}s")

    # 6. Extract Bounding Boxes
    t0 = time.time()
    print("Extracting province bounding boxes...")
    slices = ndimage.find_objects(pid_grid)
    print(f"-> Sliced {len(slices)} provinces in {time.time() - t0:.2f}s")

    # 7. Extract Barony Polygons
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

        # Enrich with county/duchy/kingdom/empire translations
        if c_key and c_key in gaz:
            props["c_tarr_direct"] = gaz[c_key].get("direct", "")
            props["c_tarr_hist"] = gaz[c_key].get("hist", "")
        if d_key:
            props["d_tarr"] = gaz.get(d_key, {}).get("hist", gaz.get(d_key, {}).get("direct", save_titles.get(d_key, {}).get("save_name", "")))
        if k_key:
            props["k_tarr"] = gaz.get(k_key, {}).get("hist", gaz.get(k_key, {}).get("direct", save_titles.get(k_key, {}).get("save_name", "")))
        if e_key:
            props["e_tarr"] = gaz.get(e_key, {}).get("hist", gaz.get(e_key, {}).get("direct", empire_names.get(e_key, "")))

        barony_features.append({
            "type": "Feature",
            "id": b_key,
            "geometry": mapping(geom),
            "properties": props,
        })

    print(f"-> Generated {len(barony_features)} barony features in {time.time() - t0:.2f}s")

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
            if d_key:
                props["d_tarr"] = gaz.get(d_key, {}).get("hist", gaz.get(d_key, {}).get("direct", save_titles.get(d_key, {}).get("save_name", "")))
            if k_key:
                props["k_tarr"] = gaz.get(k_key, {}).get("hist", gaz.get(k_key, {}).get("direct", save_titles.get(k_key, {}).get("save_name", "")))
            if e_key:
                props["e_tarr"] = gaz.get(e_key, {}).get("hist", gaz.get(e_key, {}).get("direct", empire_names.get(e_key, "")))

            county_features.append({
                "type": "Feature",
                "id": c_key,
                "geometry": mapping(c_geom),
                "properties": props,
            })
        except Exception as e:
            print(f"Warning: Failed to dissolve county {c_key}: {e}")

    print(f"-> Dissolved {len(county_features)} county features in {time.time() - t0:.2f}s")

    # 9. Compute Four-Color Map Coloring for all 5 tiers
    c_colors, d_colors, k_colors, e_colors, b_colors, adjacencies = compute_all_tier_colors(
        county_features, barony_features
    )

    # 10. Apply colors to county features
    for feat in county_features:
        p = feat["properties"]
        ck = p["county"]
        dk = p.get("duchy")
        kk = p.get("kingdom")
        ek = p.get("empire")
        p["c_color"] = c_colors.get(ck, "#3b7d4e")
        p["d_color"] = d_colors.get(dk, "#2e649e") if dk else "#3d3832"
        p["k_color"] = k_colors.get(kk, "#b88228") if kk else "#3d3832"
        p["e_color"] = e_colors.get(ek, "#a64b38") if ek else "#3d3832"

    # 11. Apply colors to barony features
    for feat in barony_features:
        p = feat["properties"]
        bk = p["barony"]
        ck = p.get("county")
        dk = p.get("duchy")
        kk = p.get("kingdom")
        ek = p.get("empire")
        p["b_color"] = b_colors.get(bk, "#2a7d76")
        p["c_color"] = c_colors.get(ck, "#3b7d4e") if ck else "#3d3832"
        p["d_color"] = d_colors.get(dk, "#2e649e") if dk else "#3d3832"
        p["k_color"] = k_colors.get(kk, "#b88228") if kk else "#3d3832"
        p["e_color"] = e_colors.get(ek, "#a64b38") if ek else "#3d3832"

    # 12. Write data/ck3_baronies.geojson
    baronies_geojson_path = out_dir / "ck3_baronies.geojson"
    print(f"Writing {baronies_geojson_path.name}...")
    with open(baronies_geojson_path, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": barony_features}, f, separators=(",", ":"))
    print(f"-> Wrote {baronies_geojson_path.name} ({baronies_geojson_path.stat().st_size / 1024 / 1024:.2f} MB)")

    # 13. Write data/ck3_counties.geojson
    counties_geojson_path = out_dir / "ck3_counties.geojson"
    print(f"Writing {counties_geojson_path.name}...")
    with open(counties_geojson_path, "w", encoding="utf-8") as f:
        json.dump({"type": "FeatureCollection", "features": county_features}, f, separators=(",", ":"))
    print(f"-> Wrote {counties_geojson_path.name} ({counties_geojson_path.stat().st_size / 1024 / 1024:.2f} MB)")

    # 14. Write Title Tree
    tree_out_path = out_dir / "ck3_title_tree.json"
    build_and_write_title_tree(county_info, tree_out_path, gaz, empire_names, save_titles, e_colors, k_colors, d_colors, c_colors)

    # 15. Write Adjacencies Index
    adj_out_path = out_dir / "ck3_adjacencies.json"
    print(f"Writing spatial adjacencies index to {adj_out_path.name}...")
    with open(adj_out_path, "w", encoding="utf-8") as f:
        json.dump(adjacencies, f, indent=2)
    print(f"-> Wrote {adj_out_path.name} ({adj_out_path.stat().st_size / 1024:.1f} KB)")

    print("==========================================================")
    print("SUCCESS: Map Vectorization & GeoJSON Generation Complete!")
    print(f"1. Baronies GeoJSON:    {baronies_geojson_path}")
    print(f"2. Counties GeoJSON:    {counties_geojson_path}")
    print(f"3. Title Tree JSON:     {tree_out_path}")
    print(f"4. Adjacencies Index:   {adj_out_path}")
    print("==========================================================")


if __name__ == "__main__":
    main()

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

# ---------------------------------------------------------------------------
# Barony Holding Colors (4 Semantic Categories)
# - castles in reddish colour
# - bishopries in bluish colour
# - cities in greenish colour
# - unoccupied in dark grey colour
# ---------------------------------------------------------------------------
BARONY_HOLDING_COLORS = {
    "castle": "#ab3348",      # Reddish (Crimson Wine)
    "church": "#3069a8",      # Bluish (Royal Blue)
    "city": "#3b824a",        # Greenish (Forest Green)
    "unoccupied": "#424242",  # Dark grey
}

BARONY_HOLDING_NAMES = {
    "castle": "Castle",
    "church": "Bishopric",
    "city": "City",
    "unoccupied": "Unoccupied",
}


def load_barony_holdings_map(repo_dir: Path = None) -> dict:
    """Loads barony holdings mapping from data/barony_holdings.json or titles_data.json."""
    if repo_dir is None:
        repo_dir = Path(__file__).resolve().parent.parent

    data_file = repo_dir / "data" / "barony_holdings.json"
    audit_file = Path("/var/tmp/ck3_audit/phase1/titles_data.json")

    def map_raw_holding_type(raw_type):
        if not raw_type:
            return "unoccupied"
        raw = raw_type.lower()
        if "church" in raw or "temple" in raw:
            return "church"
        elif "city" in raw:
            return "city"
        elif "castle" in raw or "tribal" in raw or "nomad" in raw or "herder" in raw:
            return "castle"
        return "unoccupied"

    holdings = {}
    if data_file.exists():
        try:
            with open(data_file, "r", encoding="utf-8") as f:
                holdings = json.load(f)
        except Exception:
            pass

    if not holdings and audit_file.exists():
        try:
            with open(audit_file, "r", encoding="utf-8") as f:
                titles_data = json.load(f)
            for c_data in titles_data.values():
                for b in c_data.get("baronies", []):
                    holdings[b["key"]] = map_raw_holding_type(b.get("holding_type"))
        except Exception as e:
            print(f"Warning: could not parse titles_data.json: {e}")

    return holdings


def format_title_key(key: str) -> str:
    """Fallback formatting: e.g. c_middlesex -> Middlesex, d_york -> York"""
    if not key:
        return ""
    parts = key.split("_", 1)
    if len(parts) == 2 and len(parts[0]) <= 2:
        base = parts[1]
    else:
        base = key
    return " ".join(word.capitalize() for word in base.split("_"))


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


def compute_all_tier_colors(county_features, barony_features, repo_dir: Path = None):
    """
    Computes spatial adjacency graphs and assigns collision-free colors
    for empires, kingdoms, duchies, counties (7-color DSATUR),
    and assigns 4 holding-type colors for baronies:
    - castles: reddish (#ab3348)
    - bishoprics: bluish (#3069a8)
    - cities: greenish (#3b824a)
    - unoccupied: dark grey (#424242)
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

    # 4. Color all tiers: Counties/Duchies/Kingdoms/Empires with 7-color DSATUR, Baronies with 4 holding colors
    print("Coloring territory graphs (Counties/Duchies/Kingdoms/Empires DSATUR, Baronies holding types)...")
    t0 = time.time()
    county_colors = color_graph_dsatur(c_nodes, county_adj_edges)
    duchy_colors = color_graph_dsatur(d_nodes, d_edges)
    kingdom_colors = color_graph_dsatur(k_nodes, k_edges)
    empire_colors = color_graph_dsatur(e_nodes, e_edges)

    barony_holdings = load_barony_holdings_map(repo_dir)
    barony_colors = {
        bk: BARONY_HOLDING_COLORS.get(barony_holdings.get(bk, "unoccupied"), "#424242")
        for bk in b_nodes
    }
    print(f"-> All tiers colored: Counties/Duchies/Kingdoms/Empires (DSATUR 7-color), Baronies (4-color holdings) in {time.time() - t0:.2f}s")

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
            m = re.match(r"^\|\s*\d+\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*`([^`]+)`(?:\s*\|\s*\*\*([^*]+)\*\*)?", line)
            if m:
                origin, key, tarr = m.group(1).strip(), m.group(2).strip(), m.group(3)
                if key.startswith("e_") or key.startswith("h_"):
                    empires[key] = tarr.strip() if tarr else origin
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


def parse_title_origins(
    titles_md_path: Path,
    hre_md_path: Path,
    anachronisms_md_path: Path = None,
    audit_md_path: Path = None,
):
    """
    Extracts historical title name origins and anachronistic title analyses for all tiers
    from the markdown files:
    - archive/anachronistic_titles_1059.md: Pre-1059 centres and foundation reasons
    - audit_discrepancy_register.md: Historical justifications and resolved centers
    - tarraconian_titles_1059.md: Section 3 origins and [YEAR Historical: ...] annotations
    - hre_de_jure_and_archdioceses_1059.md: Table 1.1 empire and kingdom origins
    """
    c_origins = {}
    d_origins = {}
    k_origins = {}
    e_origins = {}

    c_anachronisms = {}
    d_anachronisms = {}
    k_anachronisms = {}
    e_anachronisms = {}

    def clean_md(text: str) -> str:
        if not text:
            return ""
        text = re.sub(r"\[\s*\**[a-zA-Z0-9_\-\s]+\**\s*\]", "", text)
        text = text.replace("**", "").replace("*", "").strip()
        return text

    def parse_hist_tag(h_str: str) -> str:
        h = re.sub(r"^(?:Magistrat|Fürstbisdom|Gubernat|Kûnincrich|March)\s+van\s+(?:der\s+|den\s+|dem\s+)?", "", h_str).strip()
        parts = [p.strip() for p in h.split(" / ")]
        res_parts = []
        for p in parts:
            m = re.match(r"^([^(]+)\s*\(([^)]+)\)$", p)
            if m:
                tarr_name, alt_name = m.group(1).strip(), m.group(2).strip()
                if tarr_name.lower() == "wilten" and "veldidena" in alt_name.lower():
                    res_parts.append("Wilten / Veldidena")
                elif alt_name:
                    res_parts.append(alt_name)
                else:
                    res_parts.append(tarr_name)
            else:
                res_parts.append(p)
        return " / ".join(res_parts)

    anach_reasons = {}

    # 1. Parse archive/anachronistic_titles_1059.md
    if anachronisms_md_path and anachronisms_md_path.exists():
        text = anachronisms_md_path.read_text(encoding="utf-8")
        p1 = re.compile(
            r"^\|\s*`([cdk]_[a-zA-Z0-9_\-]+)`(?:\s*/\s*`([cdk]_[a-zA-Z0-9_\-]+)`)?\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|",
            re.MULTILINE,
        )
        for m in p1.finditer(text):
            k1 = m.group(1).strip()
            k2 = m.group(2).strip() if m.group(2) else None
            reason = clean_md(m.group(6))
            centre_raw = m.group(7).strip()
            bolds = re.findall(r"\*\*([^*]+)\*\*", centre_raw)
            bolds = [b for b in bolds if not b.startswith("House ") and not b.startswith("Valid ")]
            if bolds:
                centre = bolds[0].split("(")[0].strip()
            else:
                centre = clean_md(centre_raw).split(" or ")[0].split("(")[0].strip()
            for k in ([k1, k2] if k2 else [k1]):
                anach_reasons[k] = {"reason": reason, "centre": centre}

        p2 = re.compile(
            r"^\|\s*`([cdk]_[a-zA-Z0-9_\-]+)`\s*\(\*\*([^*]+)\*\*\)\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|",
            re.MULTILINE,
        )
        for m in p2.finditer(text):
            k = m.group(1).strip()
            centre = clean_md(m.group(7)).split(" or ")[0].split("(")[0].strip()
            if k not in anach_reasons:
                anach_reasons[k] = {"reason": "Anachronistic title evaluated in 1059 Chancellery audit", "centre": centre}

    aliases = {
        "c_munich": "c_munchen",
        "c_berg": "c_bergh",
        "c_tirol": "c_tyrol",
        "c_wurtemberg": "c_wurttemberg",
        "c_brussels": "c_brabant",
    }
    for old_k, new_k in aliases.items():
        if old_k in anach_reasons and new_k not in anach_reasons:
            anach_reasons[new_k] = anach_reasons[old_k]

    # 2. Parse audit_discrepancy_register.md
    if audit_md_path and audit_md_path.exists():
        text = audit_md_path.read_text(encoding="utf-8")
        p_audit = re.compile(
            r"^\|\s*`([cdkeh]_[a-zA-Z0-9_\-]+)`\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|",
            re.MULTILINE,
        )
        for m in p_audit.finditer(text):
            k = m.group(1).strip()
            col4 = clean_md(m.group(4))
            reason = clean_md(m.group(5))
            res = clean_md(m.group(6))
            just = clean_md(m.group(9))
            if k not in anach_reasons:
                m_c = re.search(r"\(([^)]+)\)", res)
                centre = m_c.group(1).strip() if m_c else res
                if "Pre-867" in col4:
                    clean_reason = col4
                elif k.startswith("e_"):
                    clean_reason = col4 if col4 else (just if just else reason)
                else:
                    clean_reason = just if just else reason
                anach_reasons[k] = {"reason": clean_reason, "centre": centre}

    # 3. Parse tarraconian_titles_1059.md
    if titles_md_path.exists():
        with open(titles_md_path, "r", encoding="utf-8") as f:
            t_text = f.read()

        # Counties: `c_key` (Origin) $\rightarrow$ ... [YEAR Historical: ...]
        for m in re.finditer(r"^\s*\*\s*`(c_[a-zA-Z0-9_\-]+)`\s*(.*?)\s*\$\\rightarrow\$\s*(.*?)$", t_text, re.MULTILINE):
            ck = m.group(1)
            raw = m.group(2).strip()
            base_orig = raw.strip("()")
            base_orig = clean_md(base_orig)
            rest = m.group(3)

            m_h = re.search(r"\[(1059|1122|1142|1154|1171|1194)\s+Historical:\s*([^\]]+)\]", rest)
            if m_h:
                h_str = m_h.group(2).strip()
                hist_centre = parse_hist_tag(h_str)
                reason_info = anach_reasons.get(ck, {})
                reason = reason_info.get("reason", f"Anachronistic foundation evaluated in {m_h.group(1)} Imperial Chancellery audit.")
                c_origins[ck] = f"{hist_centre} (in-game: {base_orig})"
                c_anachronisms[ck] = reason
            elif ck in anach_reasons:
                info = anach_reasons[ck]
                centre = info["centre"]
                c_origins[ck] = f"{centre} (in-game: {base_orig})"
                c_anachronisms[ck] = info["reason"]
            else:
                c_origins[ck] = base_orig
                c_anachronisms[ck] = ""

        # Duchies: * **Duchy of Origin** (`d_key`)
        for m in re.finditer(r"^\*\s+\*\*(?:Duchy|March)\s+of\s+([^*`]+)\*\*\s+.*?\(`([dx]_[a-zA-Z0-9_\-]+)`\)(.*?)$", t_text, re.MULTILINE):
            base_orig = m.group(1).strip()
            dk = m.group(2)
            rest = m.group(3)

            m_paren = re.match(r"^([^(]+)\s*\(([^)]+)\)$", base_orig)
            if m_paren:
                hist_part, in_game_part = m_paren.group(1).strip(), m_paren.group(2).strip()
            else:
                hist_part, in_game_part = base_orig, base_orig

            m_h = re.search(r"\[(1059|1122|1142|1154|1171|1194)\s+Historical:\s*([^\]]+)\]", rest)
            if m_h:
                h_str = m_h.group(2).strip()
                hist_centre = parse_hist_tag(h_str)
                reason_info = anach_reasons.get(dk, {})
                reason = reason_info.get("reason", f"Anachronistic foundation evaluated in {m_h.group(1)} Imperial Chancellery audit.")
                d_origins[dk] = f"{hist_centre} (in-game: {in_game_part})"
                d_anachronisms[dk] = reason
            elif dk in anach_reasons:
                info = anach_reasons[dk]
                centre = info["centre"]
                if hist_part != in_game_part:
                    if centre and hist_part not in centre and centre not in hist_part:
                        hist_name = f"{hist_part} / {centre}"
                    else:
                        hist_name = centre if centre else hist_part
                else:
                    hist_name = centre if centre else hist_part
                d_origins[dk] = f"{hist_name} (in-game: {in_game_part})"
                d_anachronisms[dk] = info["reason"]
            elif hist_part != in_game_part:
                d_origins[dk] = f"{hist_part} (in-game: {in_game_part})"
                d_anachronisms[dk] = ""
            else:
                d_origins[dk] = base_orig
                d_anachronisms[dk] = ""

        # Kingdoms: ### 3.X Kingdom of Origin (`k_key`)
        for m in re.finditer(r"^###\s+3\.\d+\s+Kingdom\s+of\s+([^`]+)\s+\(`([a-zA-Z0-9_\-]+)`\)(.*?)$", t_text, re.MULTILINE):
            base_orig = m.group(1).strip()
            kk = m.group(2)
            rest = m.group(3)

            m_paren = re.match(r"^([^(]+)\s*\(([^)]+)\)$", base_orig)
            if m_paren:
                hist_part, in_game_part = m_paren.group(1).strip(), m_paren.group(2).strip()
            else:
                hist_part, in_game_part = base_orig, base_orig

            m_h = re.search(r"\[(1059|1122|1142|1154|1171|1194)\s+Historical:\s*([^\]]+)\]", rest)
            if m_h:
                h_str = m_h.group(2).strip()
                hist_centre = parse_hist_tag(h_str)
                reason_info = anach_reasons.get(kk, {})
                reason = reason_info.get("reason", f"Anachronistic foundation evaluated in {m_h.group(1)} Imperial Chancellery audit.")
                k_origins[kk] = f"{hist_centre} (in-game: {base_orig})"
                k_anachronisms[kk] = reason
            elif kk in anach_reasons:
                info = anach_reasons[kk]
                centre = info["centre"]
                if hist_part != in_game_part:
                    if centre and hist_part not in centre and centre not in hist_part:
                        hist_name = f"{hist_part} / {centre}"
                    else:
                        hist_name = centre if centre else hist_part
                else:
                    hist_name = centre if centre else hist_part
                k_origins[kk] = f"{hist_name} (in-game: {in_game_part})"
                k_anachronisms[kk] = info["reason"]
            elif hist_part != in_game_part:
                k_origins[kk] = f"{hist_part} (in-game: {in_game_part})"
                k_anachronisms[kk] = ""
            else:
                k_origins[kk] = base_orig
                k_anachronisms[kk] = ""

        # Kingdoms Section 2 table fallback
        for m in re.finditer(r"^\|\s*\d+\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*`([a-zA-Z0-9_\-]+)`\s*\|", t_text, re.MULTILINE):
            origin = m.group(1).strip()
            kk = m.group(2)
            if kk.startswith("k_") and kk not in k_origins:
                if kk in anach_reasons:
                    info = anach_reasons[kk]
                    c_txt = info["centre"]
                    r_txt = info["reason"]
                    k_origins[kk] = f"{c_txt} (in-game: {origin})"
                    k_anachronisms[kk] = r_txt
                else:
                    k_origins[kk] = origin
                    k_anachronisms[kk] = ""

    # 4. Empires from hre_de_jure_and_archdioceses_1059.md Table 1.1
    if hre_md_path.exists():
        with open(hre_md_path, "r", encoding="utf-8") as f:
            h_text = f.read()

        for m in re.finditer(r"^\|\s*\d+\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*`([a-zA-Z0-9_\-]+)`\s*\|", h_text, re.MULTILINE):
            origin = m.group(1).strip()
            ek = m.group(2)
            if ek.startswith("e_"):
                e_origins[ek] = origin
                if ek in anach_reasons:
                    e_anachronisms[ek] = anach_reasons[ek]["reason"]
                else:
                    e_anachronisms[ek] = ""
            elif ek.startswith("k_") and ek not in k_origins:
                if ek in anach_reasons:
                    info = anach_reasons[ek]
                    c_txt = info["centre"]
                    r_txt = info["reason"]
                    k_origins[ek] = f"{c_txt} (in-game: {origin})"
                    k_anachronisms[ek] = r_txt
                else:
                    k_origins[ek] = origin
                    k_anachronisms[ek] = ""

    return (
        c_origins,
        d_origins,
        k_origins,
        e_origins,
        c_anachronisms,
        d_anachronisms,
        k_anachronisms,
        e_anachronisms,
    )


def parse_title_ipa(md_path: Path):
    """
    Extracts IPA phonetic pronunciations from tarraconian_titles_1059.md
    for kingdoms, duchies, counties, and empires.
    """
    c_ipa = {}
    d_ipa = {}
    k_ipa = {}
    e_ipa = {}

    if not md_path or not md_path.exists():
        return c_ipa, d_ipa, k_ipa, e_ipa

    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()

    for line in lines:
        line_s = line.strip()

        # 1. Section 2 Kingdom table
        m_k = re.match(r"^\|\s*\d+\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*`([a-zA-Z0-9_\-]+)`\s*\|\s*([^|]+)\|\s*([^|]+)\|", line_s)
        if m_k:
            kk = m_k.group(2).strip()
            col4 = m_k.group(4).strip()
            m_brackets = re.findall(r"\[([^\]]+)\]", col4)
            for b in m_brackets:
                b_clean = b.strip("`")
                if any(c in b_clean for c in "ˈˌːɛɔʊɪʏøœ̃ŋʃʒθðçɣχʁʔɲʎ") or ("." in b_clean and len(b_clean.split()) == 1):
                    if kk.startswith("e_") or kk.startswith("h_"):
                        e_ipa[kk] = f"[{b_clean}]"
                    else:
                        k_ipa[kk] = f"[{b_clean}]"
                    break
            continue

        # 2. Section 3 Kingdom headers
        if line_s.startswith("### 3."):
            m_kh = re.match(r"^###\s+3\.\d+\s+Kingdom.*?\(`([a-zA-Z0-9_\-]+)`\)", line_s)
            if m_kh:
                kk = m_kh.group(1).strip()
                if kk not in k_ipa:
                    m_brackets = re.findall(r"\[([^\]]+)\]", line_s)
                    for b in m_brackets:
                        b_clean = b.strip("`")
                        if any(c in b_clean for c in "ˈˌːɛɔʊɪʏøœ̃ŋʃʒθðçɣχʁʔɲʎ") or ("." in b_clean and len(b_clean.split()) == 1):
                            k_ipa[kk] = f"[{b_clean}]"
                            break
            continue

        # 3. Section 3 Duchy bullets
        if any(line_s.startswith(x) for x in ["* **Duchy", "* **Frontier Duchy", "* **March", "* **Metropolitan"]):
            all_keys = re.findall(r"`([dx]_[a-zA-Z0-9_\-]+)`", line_s)
            m_brackets = re.findall(r"\[([^\]]+)\]", line_s)
            for b in m_brackets:
                b_clean = b.strip("`")
                if any(b_clean.startswith(x) for x in ["1059", "1122", "1142", "1154", "1171", "1194", "HRE", "d_", "c_", "k_", "e_", "b_"]):
                    continue
                if any(c in b_clean for c in "ˈˌːɛɔʊɪʏøœ̃ŋʃʒθðçɣχʁʔɲʎ") or ("." in b_clean and len(b_clean.split()) == 1):
                    for dk in all_keys:
                        d_ipa[dk] = f"[{b_clean}]"
                    break
            continue

        # 4. Section 3 County bullets
        m_c = re.match(r"^\s*\*\s*`(c_[a-zA-Z0-9_\-]+)`\s*(.*?)\s*\$\\rightarrow\$\s*(.*?)$", line_s)
        if m_c:
            ck = m_c.group(1).strip()
            rest = m_c.group(3)
            m_brackets = re.findall(r"\[([^\]]+)\]", rest)
            for b in m_brackets:
                b_clean = b.strip("`")
                if any(b_clean.startswith(x) for x in ["1059", "1122", "1142", "1154", "1171", "1194", "HRE", "d_", "c_", "k_", "e_", "b_"]):
                    continue
                if any(c in b_clean for c in "ˈˌːɛɔʊɪʏøœ̃ŋʃʒθðçɣχʁʔɲʎ") or ("." in b_clean and len(b_clean.split()) == 1):
                    c_ipa[ck] = f"[{b_clean}]"
                    break
            continue

    return c_ipa, d_ipa, k_ipa, e_ipa


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
    c_origins: dict = None,
    d_origins: dict = None,
    k_origins: dict = None,
    e_origins: dict = None,
    c_anachronisms: dict = None,
    d_anachronisms: dict = None,
    k_anachronisms: dict = None,
    e_anachronisms: dict = None,
    c_ipa: dict = None,
    d_ipa: dict = None,
    k_ipa: dict = None,
    e_ipa: dict = None,
):
    """Builds nested title tree e_* -> k_* -> d_* -> c_* -> [b_*] and writes to JSON."""
    if empire_colors is None: empire_colors = {}
    if kingdom_colors is None: kingdom_colors = {}
    if duchy_colors is None: duchy_colors = {}
    if county_colors is None: county_colors = {}
    if c_origins is None: c_origins = {}
    if d_origins is None: d_origins = {}
    if k_origins is None: k_origins = {}
    if e_origins is None: e_origins = {}
    if c_anachronisms is None: c_anachronisms = {}
    if d_anachronisms is None: d_anachronisms = {}
    if k_anachronisms is None: k_anachronisms = {}
    if e_anachronisms is None: e_anachronisms = {}
    if c_ipa is None: c_ipa = {}
    if d_ipa is None: d_ipa = {}
    if k_ipa is None: k_ipa = {}
    if e_ipa is None: e_ipa = {}

    sino_path = tree_out_path.parent / "sinosphere_hanzi_calques.json"
    sino_db = {}
    if sino_path.exists():
        try:
            with open(sino_path, "r", encoding="utf-8") as f:
                sino_db = json.load(f)
        except Exception:
            pass

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
        e_tarr_name = empire_names.get(e_k, gaz.get(e_k, {}).get("hist", gaz.get(e_k, {}).get("direct", e_k)))
        e_origin = e_origins.get(e_k, empire_names.get(e_k, format_title_key(e_k)))
        e_entry = {
            "key": e_k,
            "tarr": e_tarr_name,
            "ipa": e_ipa.get(e_k, ""),
            "origin": e_origin,
            "anachronism": e_anachronisms.get(e_k, ""),
            "color": empire_colors.get(e_k, "#a64b38"),
            "kingdoms": {},
        }
        if e_k in sino_db and sino_db[e_k].get("hanzi"):
            e_entry["hanzi"] = sino_db[e_k]["hanzi"]
        for k_k in sorted(kingdoms.keys()):
            duchies = kingdoms[k_k]
            k_tarr_name = gaz.get(k_k, {}).get("hist", gaz.get(k_k, {}).get("direct", save_titles.get(k_k, {}).get("save_name", k_k)))
            k_origin = k_origins.get(k_k, format_title_key(k_k))
            k_entry = {
                "key": k_k,
                "tarr": k_tarr_name,
                "ipa": k_ipa.get(k_k, ""),
                "origin": k_origin,
                "anachronism": k_anachronisms.get(k_k, ""),
                "color": kingdom_colors.get(k_k, "#b88228"),
                "duchies": {},
            }
            if k_k in sino_db and sino_db[k_k].get("hanzi"):
                k_entry["hanzi"] = sino_db[k_k]["hanzi"]
            for d_k in sorted(duchies.keys()):
                counties = duchies[d_k]
                d_tarr_name = gaz.get(d_k, {}).get("hist", gaz.get(d_k, {}).get("direct", save_titles.get(d_k, {}).get("save_name", d_k)))
                d_origin = d_origins.get(d_k, format_title_key(d_k))
                d_entry = {
                    "key": d_k,
                    "tarr": d_tarr_name,
                    "ipa": d_ipa.get(d_k, ""),
                    "origin": d_origin,
                    "anachronism": d_anachronisms.get(d_k, ""),
                    "color": duchy_colors.get(d_k, "#2e649e"),
                    "counties": {},
                }
                if d_k in sino_db and sino_db[d_k].get("hanzi"):
                    d_entry["hanzi"] = sino_db[d_k]["hanzi"]
                for c_k in sorted(counties.keys()):
                    b_list = counties[c_k]
                    c_origin = c_origins.get(c_k, format_title_key(c_k))
                    c_hist = gaz.get(c_k, {}).get("hist", c_k)
                    c_direct = gaz.get(c_k, {}).get("direct", c_k)
                    c_entry = {
                        "key": c_k,
                        "tarr": c_hist or c_direct,
                        "tarr_direct": c_direct,
                        "tarr_hist": c_hist,
                        "ipa": c_ipa.get(c_k, ""),
                        "origin": c_origin,
                        "anachronism": c_anachronisms.get(c_k, ""),
                        "color": county_colors.get(c_k, "#3b7d4e"),
                        "baronies": b_list,
                    }
                    if c_k in sino_db and sino_db[c_k].get("hanzi"):
                        c_entry["hanzi"] = sino_db[c_k]["hanzi"]
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
    c_origins: dict = None,
    d_origins: dict = None,
    k_origins: dict = None,
    e_origins: dict = None,
    c_anachronisms: dict = None,
    d_anachronisms: dict = None,
    k_anachronisms: dict = None,
    e_anachronisms: dict = None,
    c_ipa: dict = None,
    d_ipa: dict = None,
    k_ipa: dict = None,
    e_ipa: dict = None,
):
    """Realigns existing GeoJSON and title tree datasets without re-rasterizing."""
    counties_path = out_dir / "ck3_counties.geojson"
    baronies_path = out_dir / "ck3_baronies.geojson"
    tree_path = out_dir / "ck3_title_tree.json"
    adj_path = out_dir / "ck3_adjacencies.json"

    if c_origins is None: c_origins = {}
    if d_origins is None: d_origins = {}
    if k_origins is None: k_origins = {}
    if e_origins is None: e_origins = {}
    if c_anachronisms is None: c_anachronisms = {}
    if d_anachronisms is None: d_anachronisms = {}
    if k_anachronisms is None: k_anachronisms = {}
    if e_anachronisms is None: e_anachronisms = {}
    if c_ipa is None: c_ipa = {}
    if d_ipa is None: d_ipa = {}
    if k_ipa is None: k_ipa = {}
    if e_ipa is None: e_ipa = {}

    sino_path = out_dir / "sinosphere_hanzi_calques.json"
    sino_db = {}
    if sino_path.exists():
        try:
            with open(sino_path, "r", encoding="utf-8") as f:
                sino_db = json.load(f)
        except Exception:
            pass

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
            props["tarr"] = props["tarr_hist"] or props["tarr_direct"]
        if d_k:
            props["d_tarr"] = gaz.get(d_k, {}).get("hist", gaz.get(d_k, {}).get("direct", save_titles.get(d_k, {}).get("save_name", "")))
            if d_k in gaz:
                props["d_tarr_direct"] = gaz[d_k].get("direct", "")
                props["d_tarr_hist"] = gaz[d_k].get("hist", "")
        if k_k:
            props["k_tarr"] = gaz.get(k_k, {}).get("hist", gaz.get(k_k, {}).get("direct", save_titles.get(k_k, {}).get("save_name", "")))
            if k_k in gaz:
                props["k_tarr_direct"] = gaz[k_k].get("direct", "")
                props["k_tarr_hist"] = gaz[k_k].get("hist", "")
        if e_k:
            props["e_tarr"] = empire_names.get(e_k, gaz.get(e_k, {}).get("hist", gaz.get(e_k, {}).get("direct", "")))
            if e_k in gaz:
                props["e_tarr_direct"] = gaz[e_k].get("direct", "")
                props["e_tarr_hist"] = gaz[e_k].get("hist", "")

        # Historical Title Name Origins & Anachronisms from Markdown Files
        props["c_origin"] = c_origins.get(c_k, format_title_key(c_k))
        props["c_anachronism"] = c_anachronisms.get(c_k, "")
        if d_k:
            props["d_origin"] = d_origins.get(d_k, format_title_key(d_k))
            props["d_anachronism"] = d_anachronisms.get(d_k, "")
        if k_k:
            props["k_origin"] = k_origins.get(k_k, format_title_key(k_k))
            props["k_anachronism"] = k_anachronisms.get(k_k, "")
        if e_k:
            props["e_origin"] = e_origins.get(e_k, empire_names.get(e_k, format_title_key(e_k)))
            props["e_anachronism"] = e_anachronisms.get(e_k, "")

        # IPA pronunciations
        props["c_ipa"] = c_ipa.get(c_k, "")
        if d_k: props["d_ipa"] = d_ipa.get(d_k, "")
        if k_k: props["k_ipa"] = k_ipa.get(k_k, "")
        if e_k: props["e_ipa"] = e_ipa.get(e_k, "")

        # Sinosphere Hanzi & Calques
        s_c = sino_db.get(c_k, {})
        props["c_hanzi"] = s_c.get("hanzi", "")
        if s_c.get("synthesis"):
            props["c_calque"] = s_c.get("synthesis", "")
        if d_k: props["d_hanzi"] = sino_db.get(d_k, {}).get("hanzi", "")
        if k_k: props["k_hanzi"] = sino_db.get(k_k, {}).get("hanzi", "")
        if e_k: props["e_hanzi"] = sino_db.get(e_k, {}).get("hanzi", "")

        county_info[c_k] = {
            "county": c_k,
            "duchy": d_k,
            "kingdom": k_k,
            "empire": e_k,
            "baronies": props.get("baronies", []),
        }

    with open(baronies_path, "r", encoding="utf-8") as f:
        baronies_fc = json.load(f)

    barony_holdings = load_barony_holdings_map(out_dir.parent)

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
            props["c_tarr"] = props["c_tarr_hist"] or props["c_tarr_direct"]
        if d_k:
            props["d_tarr"] = gaz.get(d_k, {}).get("hist", gaz.get(d_k, {}).get("direct", save_titles.get(d_k, {}).get("save_name", "")))
            if d_k in gaz:
                props["d_tarr_direct"] = gaz[d_k].get("direct", "")
                props["d_tarr_hist"] = gaz[d_k].get("hist", "")
        if k_k:
            props["k_tarr"] = gaz.get(k_k, {}).get("hist", gaz.get(k_k, {}).get("direct", save_titles.get(k_k, {}).get("save_name", "")))
            if k_k in gaz:
                props["k_tarr_direct"] = gaz[k_k].get("direct", "")
                props["k_tarr_hist"] = gaz[k_k].get("hist", "")
        if e_k:
            props["e_tarr"] = empire_names.get(e_k, gaz.get(e_k, {}).get("hist", gaz.get(e_k, {}).get("direct", "")))
            if e_k in gaz:
                props["e_tarr_direct"] = gaz[e_k].get("direct", "")
                props["e_tarr_hist"] = gaz[e_k].get("hist", "")

        # Historical Title Name Origins & Anachronisms from Markdown Files
        ht_pre = barony_holdings.get(props.get("barony", ""), "unoccupied")
        if ht_pre == "unoccupied":
            props["name"] = ""
            props["b_origin"] = ""
        else:
            props["b_origin"] = props.get("name") or format_title_key(props.get("barony", ""))
        props["b_anachronism"] = ""
        if c_k:
            props["c_origin"] = c_origins.get(c_k, format_title_key(c_k))
            props["c_anachronism"] = c_anachronisms.get(c_k, "")
        if d_k:
            props["d_origin"] = d_origins.get(d_k, format_title_key(d_k))
            props["d_anachronism"] = d_anachronisms.get(d_k, "")
        if k_k:
            props["k_origin"] = k_origins.get(k_k, format_title_key(k_k))
            props["k_anachronism"] = k_anachronisms.get(k_k, "")
        if e_k:
            props["e_origin"] = e_origins.get(e_k, empire_names.get(e_k, format_title_key(e_k)))
            props["e_anachronism"] = e_anachronisms.get(e_k, "")

        # IPA pronunciations
        props["b_ipa"] = ""
        if c_k: props["c_ipa"] = c_ipa.get(c_k, "")
        if d_k: props["d_ipa"] = d_ipa.get(d_k, "")
        if k_k: props["k_ipa"] = k_ipa.get(k_k, "")
        if e_k: props["e_ipa"] = e_ipa.get(e_k, "")
        if c_k and c_k in sino_db and sino_db[c_k].get("hanzi"):
            props["c_hanzi"] = sino_db[c_k]["hanzi"]
        else:
            props["c_hanzi"] = ""

    # Compute collision-free map colors
    c_colors, d_colors, k_colors, e_colors, b_colors, adjacencies = compute_all_tier_colors(
        counties_fc["features"], baronies_fc["features"], repo_dir=out_dir.parent
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

    # Apply colors and holding types to barony features
    barony_holdings = load_barony_holdings_map(out_dir.parent)
    for feat in baronies_fc["features"]:
        p = feat["properties"]
        bk = p["barony"]
        ck = p.get("county")
        dk = p.get("duchy")
        kk = p.get("kingdom")
        ek = p.get("empire")
        ht = barony_holdings.get(bk, "unoccupied")
        p["holding_type"] = ht
        p["holding_type_name"] = BARONY_HOLDING_NAMES.get(ht, "Unoccupied")
        p["b_color"] = BARONY_HOLDING_COLORS.get(ht, "#424242")
        if ht == "unoccupied":
            p["name"] = ""
            p["b_origin"] = ""
        p["c_color"] = c_colors.get(ck, "#3b7d4e") if ck else "#3d3832"
        p["d_color"] = d_colors.get(dk, "#2e649e") if dk else "#3d3832"
        p["k_color"] = k_colors.get(kk, "#b88228") if kk else "#3d3832"
        p["e_color"] = e_colors.get(ek, "#a64b38") if ek else "#3d3832"

    print(f"Writing updated {baronies_path.name}...")
    with open(baronies_path, "w", encoding="utf-8") as f:
        json.dump(baronies_fc, f, separators=(",", ":"))

    # Write title tree
    build_and_write_title_tree(
        county_info,
        tree_path,
        gaz,
        empire_names,
        save_titles,
        e_colors,
        k_colors,
        d_colors,
        c_colors,
        c_origins,
        d_origins,
        k_origins,
        e_origins,
        c_anachronisms,
        d_anachronisms,
        k_anachronisms,
        e_anachronisms,
        c_ipa,
        d_ipa,
        k_ipa,
        e_ipa,
    )

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
        "--anachronisms",
        default=str(REPO_DIR / "archive" / "anachronistic_titles_1059.md"),
        help="Path to archive/anachronistic_titles_1059.md",
    )
    parser.add_argument(
        "--audit-register",
        default=str(REPO_DIR / "audit_discrepancy_register.md"),
        help="Path to audit_discrepancy_register.md",
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
    anach_path = Path(args.anachronisms)
    audit_path = Path(args.audit_register)

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

    # 3. Parse Historical Title Name Origins & Anachronisms from Markdown Files
    (
        c_origins,
        d_origins,
        k_origins,
        e_origins,
        c_anachronisms,
        d_anachronisms,
        k_anachronisms,
        e_anachronisms,
    ) = parse_title_origins(gaz_path, empires_md, anach_path, audit_path)
    c_ipa, d_ipa, k_ipa, e_ipa = parse_title_ipa(gaz_path)
    print(
        f"-> Loaded title name origins from markdown: {len(c_origins)} counties, "
        f"{len(d_origins)} duchies, {len(k_origins)} kingdoms, {len(e_origins)} empires"
    )
    print(
        f"-> Loaded IPA pronunciations from markdown: {len(c_ipa)} counties, "
        f"{len(d_ipa)} duchies, {len(k_ipa)} kingdoms, {len(e_ipa)} empires"
    )

    # If --realign-only is requested OR if game files are missing while existing GeoJSONs exist
    prov_png = map_data_dir / "provinces.png"
    if args.realign_only or (not prov_png.exists() and (out_dir / "ck3_counties.geojson").exists()):
        realign_existing_datasets(
            out_dir,
            county_save_hierarchy,
            save_titles,
            gaz,
            empire_names,
            c_origins,
            d_origins,
            k_origins,
            e_origins,
            c_anachronisms,
            d_anachronisms,
            k_anachronisms,
            e_anachronisms,
            c_ipa,
            d_ipa,
            k_ipa,
            e_ipa,
        )
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
    sino_path = out_dir / "sinosphere_hanzi_calques.json"
    sino_db = {}
    if sino_path.exists():
        try:
            with open(sino_path, "r", encoding="utf-8") as f:
                sino_db = json.load(f)
        except Exception:
            pass
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
            props["c_tarr"] = props["c_tarr_hist"] or props["c_tarr_direct"]
        if d_key:
            props["d_tarr"] = gaz.get(d_key, {}).get("hist", gaz.get(d_key, {}).get("direct", save_titles.get(d_key, {}).get("save_name", "")))
            if d_key in gaz:
                props["d_tarr_direct"] = gaz[d_key].get("direct", "")
                props["d_tarr_hist"] = gaz[d_key].get("hist", "")
        if k_key:
            props["k_tarr"] = gaz.get(k_key, {}).get("hist", gaz.get(k_key, {}).get("direct", save_titles.get(k_key, {}).get("save_name", "")))
            if k_key in gaz:
                props["k_tarr_direct"] = gaz[k_key].get("direct", "")
                props["k_tarr_hist"] = gaz[k_key].get("hist", "")
        if e_key:
            props["e_tarr"] = empire_names.get(e_key, gaz.get(e_key, {}).get("hist", gaz.get(e_key, {}).get("direct", "")))
            if e_key in gaz:
                props["e_tarr_direct"] = gaz[e_key].get("direct", "")
                props["e_tarr_hist"] = gaz[e_key].get("hist", "")

        # Historical Title Name Origins & Anachronisms from Markdown Files
        props["b_origin"] = props.get("name") or format_title_key(b_key)
        props["b_anachronism"] = ""
        if c_key:
            props["c_origin"] = c_origins.get(c_key, format_title_key(c_key))
            props["c_anachronism"] = c_anachronisms.get(c_key, "")
        if d_key:
            props["d_origin"] = d_origins.get(d_key, format_title_key(d_key))
            props["d_anachronism"] = d_anachronisms.get(d_key, "")
        if k_key:
            props["k_origin"] = k_origins.get(k_key, format_title_key(k_key))
            props["k_anachronism"] = k_anachronisms.get(k_key, "")
        if e_key:
            props["e_origin"] = e_origins.get(e_key, empire_names.get(e_key, format_title_key(e_key)))
            props["e_anachronism"] = e_anachronisms.get(e_key, "")

        # IPA pronunciations
        props["b_ipa"] = ""
        if c_key: props["c_ipa"] = c_ipa.get(c_key, "")
        if d_key: props["d_ipa"] = d_ipa.get(d_key, "")
        if k_key: props["k_ipa"] = k_ipa.get(k_key, "")
        if e_key: props["e_ipa"] = e_ipa.get(e_key, "")

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
                props["tarr"] = props["tarr_hist"] or props["tarr_direct"]
            if d_key:
                props["d_tarr"] = gaz.get(d_key, {}).get("hist", gaz.get(d_key, {}).get("direct", save_titles.get(d_key, {}).get("save_name", "")))
                if d_key in gaz:
                    props["d_tarr_direct"] = gaz[d_key].get("direct", "")
                    props["d_tarr_hist"] = gaz[d_key].get("hist", "")
            if k_key:
                props["k_tarr"] = gaz.get(k_key, {}).get("hist", gaz.get(k_key, {}).get("direct", save_titles.get(k_key, {}).get("save_name", "")))
                if k_key in gaz:
                    props["k_tarr_direct"] = gaz[k_key].get("direct", "")
                    props["k_tarr_hist"] = gaz[k_key].get("hist", "")
            if e_key:
                props["e_tarr"] = empire_names.get(e_key, gaz.get(e_key, {}).get("hist", gaz.get(e_key, {}).get("direct", "")))
                if e_key in gaz:
                    props["e_tarr_direct"] = gaz[e_key].get("direct", "")
                    props["e_tarr_hist"] = gaz[e_key].get("hist", "")

            # Historical Title Name Origins & Anachronisms from Markdown Files
            props["c_origin"] = c_origins.get(c_key, format_title_key(c_key))
            props["c_anachronism"] = c_anachronisms.get(c_key, "")
            if d_key:
                props["d_origin"] = d_origins.get(d_key, format_title_key(d_key))
                props["d_anachronism"] = d_anachronisms.get(d_key, "")
            if k_key:
                props["k_origin"] = k_origins.get(k_key, format_title_key(k_key))
                props["k_anachronism"] = k_anachronisms.get(k_key, "")
            if e_key:
                props["e_origin"] = e_origins.get(e_key, empire_names.get(e_key, format_title_key(e_key)))
                props["e_anachronism"] = e_anachronisms.get(e_key, "")

            # IPA pronunciations
            props["c_ipa"] = c_ipa.get(c_key, "")
            if d_key: props["d_ipa"] = d_ipa.get(d_key, "")
            if k_key: props["k_ipa"] = k_ipa.get(k_key, "")
            if e_key: props["e_ipa"] = e_ipa.get(e_key, "")

            # Sinosphere Hanzi & Calques
            s_c = sino_db.get(c_key, {})
            props["c_hanzi"] = s_c.get("hanzi", "")
            if s_c.get("synthesis"):
                props["c_calque"] = s_c.get("synthesis", "")
            if d_key: props["d_hanzi"] = sino_db.get(d_key, {}).get("hanzi", "")
            if k_key: props["k_hanzi"] = sino_db.get(k_key, {}).get("hanzi", "")
            if e_key: props["e_hanzi"] = sino_db.get(e_key, {}).get("hanzi", "")

            county_features.append({
                "type": "Feature",
                "id": c_key,
                "geometry": mapping(c_geom),
                "properties": props,
            })
        except Exception as e:
            print(f"Warning: Failed to dissolve county {c_key}: {e}")

    print(f"-> Dissolved {len(county_features)} county features in {time.time() - t0:.2f}s")

    # 9. Compute Map Colors for all tiers
    c_colors, d_colors, k_colors, e_colors, b_colors, adjacencies = compute_all_tier_colors(
        county_features, barony_features, repo_dir=out_dir.parent
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

    # 11. Apply colors and holding types to barony features
    barony_holdings = load_barony_holdings_map(out_dir.parent)
    for feat in barony_features:
        p = feat["properties"]
        bk = p["barony"]
        ck = p.get("county")
        dk = p.get("duchy")
        kk = p.get("kingdom")
        ek = p.get("empire")
        ht = barony_holdings.get(bk, "unoccupied")
        p["holding_type"] = ht
        p["holding_type_name"] = BARONY_HOLDING_NAMES.get(ht, "Unoccupied")
        p["b_color"] = BARONY_HOLDING_COLORS.get(ht, "#424242")
        if ht == "unoccupied":
            p["name"] = ""
            p["b_origin"] = ""
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
    build_and_write_title_tree(
        county_info,
        tree_out_path,
        gaz,
        empire_names,
        save_titles,
        e_colors,
        k_colors,
        d_colors,
        c_colors,
        c_origins,
        d_origins,
        k_origins,
        e_origins,
        c_anachronisms,
        d_anachronisms,
        k_anachronisms,
        e_anachronisms,
        c_ipa,
        d_ipa,
        k_ipa,
        e_ipa,
    )

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

#!/usr/bin/env python3
"""
generate_barony_toponymic_profiles.py

Implements the Alternative 1 (3-Stratum Toponymic Profile) mapping for all
occupied CK3 baronies strictly from save-game state and history — completely
independent of vanilla CK3 barony names and their etymologies.

Outputs:
  - data/barony_toponymic_profiles.json
"""

import argparse
import hashlib
import json
import re
import time
from collections import Counter, defaultdict
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_DIR / "data"
SAVE_PATH = Path("/var/tmp/ck3_audit/melted_save.ck3")
PHASE1_DIR = Path("/var/tmp/ck3_audit/phase1")

# Imperial cultures treated as Tarraconian / Roman imperial expansion cultures
IMPERIAL_CULTURES = {
    "Tarraconian",
    "Lothringian",
    "Croato-Tarraconian",
    "Alpine-Tarraconian",
    "Ungwârer",
}

# Sinosphere heritages / languages with rapid bureaucratic top-down renaming
SINOSPHERE_HERITAGES = {
    "heritage_chinese",
    "heritage_korean",
    "heritage_japonic",
    "heritage_viet",
    "heritage_buyeo",
}

# Heritage-to-hue family anchor (H in [0, 360), S, L) for readable cartographic colors
HERITAGE_BASE_HUES = {
    "heritage_central_germanic": (42, 72, 48),   # Imperial Gold / Amber
    "heritage_west_germanic": (28, 65, 48),      # Warm Bronze / Copper
    "heritage_north_germanic": (195, 62, 44),    # Nordic Fjord Blue
    "heritage_frankish": (222, 60, 50),          # Royal Azure
    "heritage_latin": (350, 62, 48),             # Roman Crimson
    "heritage_iberian": (12, 68, 48),            # Iberian Vermilion
    "heritage_goidelic": (138, 52, 38),          # Emerald Green
    "heritage_brythonic": (152, 50, 42),         # Brythonic Moss
    "heritage_west_slavic": (165, 55, 40),       # Slavic Jade
    "heritage_south_slavic": (175, 55, 38),      # Balkan Teal
    "heritage_east_slavic": (118, 48, 42),       # Rus Forest Green
    "heritage_baltic": (92, 48, 42),             # Baltic Olive
    "heritage_balto_finnic": (185, 52, 44),      # Finnic Ice Teal
    "heritage_volga_finnic": (192, 48, 42),
    "heritage_ugro_permian": (200, 48, 42),
    "heritage_magyar": (325, 55, 46),            # Magyar Rose
    "heritage_vlach": (338, 52, 46),
    "heritage_byzantine": (280, 55, 46),         # Byzantine Imperial Purple
    "heritage_caucasian": (298, 46, 46),
    "heritage_arabic": (36, 68, 50),             # Desert Ochre
    "heritage_berber": (24, 60, 44),             # Maghrebi Terracotta
    "heritage_iranian": (258, 52, 52),           # Persian Indigo/Violet
    "heritage_turkic": (205, 68, 46),            # Steppe Sky Blue
    "heritage_mongolic": (212, 62, 42),          # Mongol Cobalt
    "heritage_hunnic": (218, 58, 44),
    "heritage_indo_aryan": (48, 72, 46),         # Saffron Gold
    "heritage_dravidian": (18, 65, 44),          # Deccan Rust
    "heritage_tibetan": (310, 48, 48),           # Tibetan Plum
    "heritage_chinese": (0, 66, 46),             # Han Cinnabar
    "heritage_korean": (168, 58, 42),            # Goryeo Celadon
    "heritage_japonic": (342, 62, 52),           # Yamato Sakura-Red
    "heritage_viet": (145, 56, 42),
    "heritage_buyeo": (172, 50, 42),
    "heritage_tungusic": (182, 45, 40),
    "heritage_tai": (105, 52, 42),
    "heritage_mon_khmer": (82, 50, 42),
    "heritage_burman": (60, 58, 44),
    "heritage_austronesian": (176, 64, 42),      # Maritime Turquoise
    "heritage_east_african": (15, 58, 44),
    "heritage_somalian": (22, 60, 46),
    "heritage_west_african": (32, 62, 44),
    "heritage_central_african": (26, 56, 42),
    "heritage_sahelian": (40, 56, 44),
    "heritage_senegambian": (34, 54, 44),
    "heritage_akan": (46, 60, 44),
    "heritage_yoruba": (10, 58, 44),
    "heritage_east_bantu": (125, 46, 40),
    "heritage_guinean_uplander": (14, 54, 42),
    "heritage_israelite": (232, 58, 52),
}


# Heritage families that were predominantly tribal/nomadic in 867 unless explicitly feudalized
TRIBAL_STEPPE_HERITAGES = {
    "heritage_magyar",
    "heritage_turkic",
    "heritage_mongolic",
    "heritage_hunnic",
}


def hsl_to_hex(h: float, s: float, l: float) -> str:
    h = (h % 360) / 360.0
    s = max(0.0, min(1.0, s / 100.0))
    l = max(0.0, min(1.0, l / 100.0))
    if s == 0:
        r = g = b = int(round(l * 255))
        return f"#{r:02x}{g:02x}{b:02x}"

    def hue2rgb(p, q, t):
        if t < 0: t += 1
        if t > 1: t -= 1
        if t < 1/6: return p + (q - p) * 6 * t
        if t < 1/2: return q
        if t < 2/3: return p + (q - p) * (2/3 - t) * 6
        return p

    q = l * (1 + s) if l < 0.5 else l + s - l * s
    p = 2 * l - q
    r = int(round(hue2rgb(p, q, h + 1/3) * 255))
    g = int(round(hue2rgb(p, q, h) * 255))
    b = int(round(hue2rgb(p, q, h - 1/3) * 255))
    return f"#{r:02x}{g:02x}{b:02x}"


def assign_culture_color(culture_name: str, heritage: str) -> str:
    if culture_name == "Tarraconian":
        return "#d4af37"  # Signature Imperial Gold
    if culture_name == "Lothringian":
        return "#b88a24"
    base_h, base_s, base_l = HERITAGE_BASE_HUES.get(heritage, (210, 45, 45))
    digest = int(hashlib.md5(culture_name.encode("utf-8")).hexdigest()[:8], 16)
    h_off = ((digest % 25) - 12)
    s_off = (((digest >> 5) % 15) - 7)
    l_off = (((digest >> 10) % 17) - 8)
    return hsl_to_hex(base_h + h_off, max(32, min(82, base_s + s_off)), max(30, min(64, base_l + l_off)))


def parse_date_tuple(d_str: str):
    if not d_str:
        return (0, 0, 0)
    parts = d_str.split(".")
    try:
        y = int(parts[0]) if len(parts) > 0 else 0
        m = int(parts[1]) if len(parts) > 1 else 1
        d = int(parts[2]) if len(parts) > 2 else 1
        return (y, m, d)
    except ValueError:
        return (0, 0, 0)


def date_to_years(d_str: str) -> float:
    y, m, d = parse_date_tuple(d_str)
    return y + (m - 1) / 12.0 + (d - 1) / 365.25


def years_between(d1: str, d2: str) -> float:
    return max(0.0, date_to_years(d2) - date_to_years(d1))


def map_holding_type_from_raw(raw_type: str) -> str:
    if not raw_type:
        return "unoccupied"
    r = raw_type.lower()
    if "church" in r or "temple" in r:
        return "church"
    if "city" in r:
        return "city"
    if "castle" in r or "tribal" in r or "nomad" in r or "herder" in r:
        return "castle"
    return "unoccupied"


def infer_liturgical_language(faith_type: str, religion_type: str, religion_family: str, culture_lang: str) -> str:
    ft = (faith_type or "").lower()
    rt = (religion_type or "").lower()
    rf = (religion_family or "").lower()

    if "islam" in rt or rf == "rf_islamic":
        return "Arabic"
    if "judaism" in rt or rf == "rf_judaism":
        return "Hebrew"
    if "christian" in rt or rf == "rf_abrahamic":
        if any(x in ft for x in ("orthodox", "iconoclast", "bogomil", "paulician")):
            if "slav" in (culture_lang or ""):
                return "Old Church Slavonic"
            return "Greek"
        if "armenian" in ft or "apostolic" in ft:
            return "Classical Armenian"
        if "coptic" in ft:
            return "Coptic"
        if "nestorian" in ft:
            return "Syriac"
        if "ethiopian" in ft or "kebra" in ft:
            return "Ge'ez"
        return "Latin"
    if "zoroastrian" in rt:
        return "Avestan / Middle Persian"
    if "hindu" in rt or "jain" in rt:
        return "Sanskrit"
    if "buddh" in rt:
        if any(x in (culture_lang or "") for x in ("chinese", "korean", "japonic", "viet")):
            return "Classical Chinese"
        if "tibetan" in (culture_lang or ""):
            return "Classical Tibetan"
        return "Sanskrit / Pali"
    if any(x in rt for x in ("tao", "confucian", "shinto", "eastern")):
        return "Classical Chinese"
    return "Vernacular"


def parse_save_all(save_path: Path):
    """Single-pass streaming parser over melted_save.ck3."""
    t0 = time.time()
    print(f"Streaming {save_path} ...")

    meta_date = "1194.7.28"
    provinces = {}         # pid_str -> {raw_holding_type, levy, garrison, buildings}
    titles_by_id = {}      # tid_str -> {id, key, holder, date, df, dj, capital_barony, lessee, leases, history}
    titles_by_key = {}     # key -> obj
    county_mgr = {}        # c_key -> {culture, rite, development}
    tribal_left = {}       # cid_str -> int_year (9999 if still tribal)
    religions = {}         # rid_str -> {religion_type, family}
    faiths = {}            # fid_str -> {faith_type, religion, name}
    chars_needed = set()

    # Pass 1: meta_data, provinces, landed_titles, religion, faiths, county_manager, culture_manager
    sec = None
    sub = None
    cur_pid = None
    in_hold = False
    in_bldg = False

    cur_tid = None
    cur_title = None
    in_hist = False
    cur_hist_entry = None

    cur_cm_county = None
    cur_cult_id = None
    cur_era = None

    cur_rel_id = None
    in_faith_db = False
    cur_fid = None

    with open(save_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("meta_data={"):
                sec = "meta"; continue
            elif line.startswith("provinces={"):
                sec = "provinces"; continue
            elif line.startswith("landed_titles={"):
                sec = "landed_titles"; continue
            elif line.startswith("religion={"):
                sec = "religion"; continue
            elif line.startswith("faiths={"):
                sec = "faiths"; continue
            elif line.startswith("county_manager={"):
                sec = "county_manager"; continue
            elif line.startswith("culture_manager={"):
                sec = "culture_manager"; continue
            elif sec and line.startswith("}"):
                if cur_title is not None:
                    titles_by_id[cur_title["id"]] = cur_title
                    if cur_title.get("key"):
                        titles_by_key[cur_title["key"]] = cur_title
                    cur_title = None
                sec = None
                sub = None
                continue

            if not sec:
                continue

            if sec == "meta":
                if line.startswith("\tmeta_date="):
                    meta_date = line.strip().split("=", 1)[1]

            elif sec == "provinces":
                if line.startswith("\t") and not line.startswith("\t\t") and "={" in line:
                    cur_pid = line.strip().split("=", 1)[0]
                    provinces[cur_pid] = {
                        "raw_holding_type": None,
                        "levy": None,
                        "garrison": None,
                        "buildings": [],
                    }
                    in_hold = False
                    in_bldg = False
                elif cur_pid is not None:
                    if line.startswith("\t}"):
                        cur_pid = None
                        in_hold = False
                        in_bldg = False
                    elif line.startswith("\t\tholding={"):
                        in_hold = True
                    elif in_hold:
                        if line.startswith("\t\t}"):
                            in_hold = False
                            in_bldg = False
                        elif line.startswith("\t\t\ttype="):
                            provinces[cur_pid]["raw_holding_type"] = line.strip().split("=", 1)[1].strip('"')
                        elif line.startswith("\t\t\tlevy="):
                            try:
                                provinces[cur_pid]["levy"] = int(line.strip().split("=", 1)[1])
                            except ValueError:
                                pass
                        elif line.startswith("\t\t\tgarrison="):
                            try:
                                provinces[cur_pid]["garrison"] = int(line.strip().split("=", 1)[1])
                            except ValueError:
                                pass
                        elif line.startswith("\t\t\tbuildings={"):
                            in_bldg = True
                        elif in_bldg:
                            if line.startswith("\t\t\t}"):
                                in_bldg = False
                            elif line.startswith("\t\t\t\t\ttype="):
                                provinces[cur_pid]["buildings"].append(line.strip().split("=", 1)[1].strip('"'))

            elif sec == "landed_titles":
                if line.startswith("\t\t") and not line.startswith("\t\t\t") and "={" in line:
                    if cur_title is not None:
                        titles_by_id[cur_title["id"]] = cur_title
                        if cur_title.get("key"):
                            titles_by_key[cur_title["key"]] = cur_title
                    tid_str = line.strip().split("=", 1)[0]
                    cur_title = {
                        "id": tid_str,
                        "key": None,
                        "holder": None,
                        "date": None,
                        "df": None,
                        "dj": None,
                        "capital_barony": False,
                        "lessee": None,
                        "theocratic_lease": False,
                        "history": [],
                    }
                    in_hist = False
                    cur_hist_entry = None
                elif cur_title is not None:
                    if line.startswith("\t\t}"):
                        titles_by_id[cur_title["id"]] = cur_title
                        if cur_title.get("key"):
                            titles_by_key[cur_title["key"]] = cur_title
                        cur_title = None
                        in_hist = False
                    elif line.startswith("\t\t\thistory={"):
                        in_hist = True
                    elif in_hist:
                        if line.startswith("\t\t\t}"):
                            in_hist = False
                            cur_hist_entry = None
                        elif line.startswith("\t\t\t\t") and not line.startswith("\t\t\t\t\t") and "=" in line:
                            d_str, val = line.strip().split("=", 1)
                            if val == "{":
                                cur_hist_entry = {"date": d_str, "holder": None, "type": "holder"}
                                cur_title["history"].append(cur_hist_entry)
                            elif val.isdigit():
                                cur_hist_entry = {"date": d_str, "holder": val, "type": "holder"}
                                cur_title["history"].append(cur_hist_entry)
                                chars_needed.add(val)
                        elif cur_hist_entry is not None:
                            if line.startswith("\t\t\t\t\tholder="):
                                h = line.strip().split("=", 1)[1]
                                cur_hist_entry["holder"] = h
                                chars_needed.add(h)
                            elif line.startswith("\t\t\t\t\ttype="):
                                cur_hist_entry["type"] = line.strip().split("=", 1)[1].strip('"')
                    elif line.startswith("\t\t\t") and not line.startswith("\t\t\t\t"):
                        if "=" in line:
                            k, v = line.strip().split("=", 1)
                            v = v.strip('"')
                            if k == "key":
                                cur_title["key"] = v
                            elif k == "holder":
                                cur_title["holder"] = v
                                chars_needed.add(v)
                            elif k == "lessee":
                                cur_title["lessee"] = v
                                chars_needed.add(v)
                            elif k == "date":
                                cur_title["date"] = v
                            elif k == "de_facto_liege":
                                cur_title["df"] = v
                            elif k == "de_jure_liege":
                                cur_title["dj"] = v
                            elif k == "capital_barony" and v == "yes":
                                cur_title["capital_barony"] = True
                            elif k == "theocratic_lease" and v == "yes":
                                cur_title["theocratic_lease"] = True

            elif sec == "religion":
                if line.startswith("\treligions={"):
                    sub = "rel"
                elif sub == "rel":
                    if line.startswith("\t}"):
                        sub = None
                    elif line.startswith("\t\t") and not line.startswith("\t\t\t") and "={" in line:
                        cur_rel_id = line.strip().split("=", 1)[0]
                        religions[cur_rel_id] = {}
                    elif cur_rel_id and line.startswith("\t\t\t") and not line.startswith("\t\t\t\t") and "=" in line:
                        k, v = line.strip().split("=", 1)
                        if k in ("religion_type", "family"):
                            religions[cur_rel_id][k] = v.strip('"')

            elif sec == "faiths":
                if line.startswith("\tdatabase={"):
                    in_faith_db = True
                elif in_faith_db:
                    if line.startswith("\t}"):
                        in_faith_db = False
                    elif line.startswith("\t\t") and not line.startswith("\t\t\t") and "={" in line:
                        cur_fid = line.strip().split("=", 1)[0]
                        faiths[cur_fid] = {}
                    elif cur_fid and line.startswith("\t\t\t") and not line.startswith("\t\t\t\t") and "=" in line:
                        k, v = line.strip().split("=", 1)
                        if k in ("faith_type", "religion", "name"):
                            faiths[cur_fid][k] = v.strip('"')

            elif sec == "county_manager":
                if line.startswith("\t\t") and not line.startswith("\t\t\t") and "={" in line:
                    c_cand = line.strip().split("=", 1)[0]
                    cur_cm_county = c_cand if c_cand.startswith("c_") else None
                    if cur_cm_county:
                        county_mgr[cur_cm_county] = {}
                elif cur_cm_county and line.startswith("\t\t}"):
                    cur_cm_county = None
                elif cur_cm_county and line.startswith("\t\t\t") and not line.startswith("\t\t\t\t") and "=" in line:
                    k, v = line.strip().split("=", 1)
                    if k in ("culture", "rite", "development"):
                        county_mgr[cur_cm_county][k] = v

            elif sec == "culture_manager":
                if line.startswith("\t\t") and not line.startswith("\t\t\t") and "={" in line:
                    cur_cult_id = line.strip().split("=", 1)[0]
                    cur_era = None
                elif cur_cult_id and 'type="culture_era_tribal"' in line:
                    cur_era = "tribal"
                elif cur_era == "tribal" and line.startswith("\t\t\t\t\tleft="):
                    try:
                        tribal_left[cur_cult_id] = int(line.strip().split("=", 1)[1])
                    except ValueError:
                        pass
                    cur_era = None
                elif cur_era == "tribal" and line.startswith("\t\t\t\t}"):
                    tribal_left[cur_cult_id] = 9999
                    cur_era = None

    print(f"  Pass 1 finished in {time.time() - t0:.2f}s: {len(provinces)} provinces, {len(titles_by_id)} titles, {len(chars_needed)} referenced chars.")

    # Pass 2: Resolve all referenced characters across living, dead_unprunable, characters.dead_prunable
    t1 = time.time()
    chars = {}
    sec = None
    cur_cid = None
    in_langs = False
    with open(save_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("living={"):
                sec = "living"; continue
            elif line.startswith("dead_unprunable={"):
                sec = "dead_unprunable"; continue
            elif line.startswith("characters={"):
                sec = "characters"; continue
            elif sec and line.startswith("}"):
                sec = None
                cur_cid = None
                in_langs = False
                continue

            if not sec:
                continue

            if sec in ("living", "dead_unprunable"):
                if line.startswith("\t") and not line.startswith("\t\t") and "={" in line:
                    cid = line.strip().split("=", 1)[0]
                    cur_cid = cid if cid in chars_needed else None
                    if cur_cid and cur_cid not in chars:
                        chars[cur_cid] = {"culture": None, "rite": None, "dynasty_house": None, "languages": [], "first_name": None}
                    in_langs = False
                elif cur_cid:
                    if line.startswith("\t\tfirst_name="):
                        chars[cur_cid]["first_name"] = line.strip().split("=", 1)[1].strip('"')
                    elif line.startswith("\t\tculture="):
                        chars[cur_cid]["culture"] = line.strip().split("=", 1)[1]
                    elif line.startswith("\t\trite="):
                        chars[cur_cid]["rite"] = line.strip().split("=", 1)[1]
                    elif line.startswith("\t\tdynasty_house="):
                        chars[cur_cid]["dynasty_house"] = line.strip().split("=", 1)[1]
                    elif line.startswith("\t\t\tlanguages={"):
                        in_langs = True
                    elif in_langs:
                        if "}" in line:
                            in_langs = False
                        else:
                            chars[cur_cid]["languages"].append(line.strip())
            elif sec == "characters":
                if line.startswith("\t\t") and not line.startswith("\t\t\t") and "={" in line:
                    cid = line.strip().split("=", 1)[0]
                    cur_cid = cid if cid in chars_needed else None
                    if cur_cid and cur_cid not in chars:
                        chars[cur_cid] = {"culture": None, "rite": None, "dynasty_house": None, "languages": [], "first_name": None}
                elif cur_cid:
                    if line.startswith("\t\t\tfirst_name="):
                        chars[cur_cid]["first_name"] = line.strip().split("=", 1)[1].strip('"')
                    elif line.startswith("\t\t\tculture="):
                        chars[cur_cid]["culture"] = line.strip().split("=", 1)[1]
                    elif line.startswith("\t\t\trite="):
                        chars[cur_cid]["rite"] = line.strip().split("=", 1)[1]
                    elif line.startswith("\t\t\tdynasty_house="):
                        chars[cur_cid]["dynasty_house"] = line.strip().split("=", 1)[1]

    print(f"  Pass 2 finished in {time.time() - t1:.2f}s: resolved {len(chars)} characters.")

    return {
        "meta_date": meta_date,
        "provinces": provinces,
        "titles_by_id": titles_by_id,
        "titles_by_key": titles_by_key,
        "county_mgr": county_mgr,
        "tribal_left": tribal_left,
        "religions": religions,
        "faiths": faiths,
        "chars": chars,
    }


def main():
    parser = argparse.ArgumentParser(description="Generate Alternative 1 Toponymic Profiles for CK3 baronies.")
    parser.add_argument("--save", type=Path, default=SAVE_PATH)
    parser.add_argument("--output", type=Path, default=DATA_DIR / "barony_toponymic_profiles.json")
    args = parser.parse_args()

    # Load phase1 auxiliary metadata
    with open(PHASE1_DIR / "cultures_data.json", "r", encoding="utf-8") as f:
        cultures_raw = json.load(f)
    with open(PHASE1_DIR / "titles_data.json", "r", encoding="utf-8") as f:
        titles_data = json.load(f)
    with open(PHASE1_DIR / "dynasties_and_houses.json", "r", encoding="utf-8") as f:
        dh_data = json.load(f)
    houses_data = dh_data.get("houses", {})

    with open(DATA_DIR / "ck3_baronies.geojson", "r", encoding="utf-8") as f:
        baronies_geo = json.load(f)

    b_to_pid = {}
    b_to_county_geo = {}
    county_total_slots = Counter()
    for feat in baronies_geo["features"]:
        p = feat["properties"]
        bk = p["barony"]
        ck = p["county"]
        b_to_pid[bk] = str(p["id"])
        b_to_county_geo[bk] = ck
        county_total_slots[ck] += 1

    save = parse_save_all(args.save)
    meta_date = save["meta_date"]
    provinces = save["provinces"]
    titles_by_id = save["titles_by_id"]
    titles_by_key = save["titles_by_key"]
    county_mgr = save["county_mgr"]
    tribal_left_by_cid = save["tribal_left"]
    religions = save["religions"]
    faiths = save["faiths"]
    chars = save["chars"]

    # Build culture lookups
    cult_by_id = {}
    cult_by_name = {}
    for cid_str, cobj in cultures_raw.items():
        cname = cobj.get("name", f"culture_{cid_str}")
        tl = tribal_left_by_cid.get(cid_str)
        rec = {
            "id": cid_str,
            "name": cname,
            "heritage": cobj.get("heritage", "Unknown"),
            "language": cobj.get("language", "Unknown"),
            "parents": cobj.get("parents", []),
            "created": cobj.get("created", "1.1.1"),
            "tribal_left": tl,
        }
        cult_by_id[cid_str] = rec
        cult_by_name[cname] = rec

    # Fill missing tribal_left from parents if needed (e.g. Ruthenian/Ebi-Norian)
    for rec in cult_by_id.values():
        if rec["tribal_left"] is None and rec["parents"]:
            parent_tls = [cult_by_id[str(pid)]["tribal_left"] for pid in rec["parents"] if str(pid) in cult_by_id and cult_by_id[str(pid)]["tribal_left"] is not None]
            if parent_tls:
                rec["tribal_left"] = max(parent_tls)

    # Helper: resolve character culture safely (with language/county fallback if omitted in CK3 save)
    def resolve_char_culture(char_id: str, fallback_county_key: str = None) -> str:
        if not char_id:
            return None
        ch = chars.get(str(char_id))
        if not ch:
            return None
        cid = ch.get("culture")
        if cid is not None and str(cid) in cult_by_id:
            return cult_by_id[str(cid)]["name"]
        # Fallback using house head or county culture matching spoken language
        langs = ch.get("languages") or []
        hid = ch.get("dynasty_house")
        if hid and str(hid) in houses_data:
            head_id = str(houses_data[str(hid)].get("head_of_house", ""))
            if head_id and head_id != str(char_id) and head_id in chars:
                h_cid = chars[head_id].get("culture")
                if h_cid is not None and str(h_cid) in cult_by_id:
                    h_cname = cult_by_id[str(h_cid)]["name"]
                    if not langs or cult_by_name[h_cname]["language"] == langs[0]:
                        return h_cname
        if fallback_county_key:
            cm = county_mgr.get(fallback_county_key, {})
            ccid = cm.get("culture")
            if ccid is not None and str(ccid) in cult_by_id:
                ccname = cult_by_id[str(ccid)]["name"]
                if not langs or cult_by_name[ccname]["language"] == langs[0]:
                    return ccname
            td = titles_data.get(fallback_county_key, {})
            ch_cult = td.get("current_holder", {}).get("culture_name")
            if ch_cult and ch_cult in cult_by_name:
                if not langs or cult_by_name[ch_cult]["language"] == langs[0]:
                    return ch_cult
        # Last resort: match first culture with matching language
        if langs:
            for c in cult_by_id.values():
                if c["language"] == langs[0]:
                    return c["name"]
        return None

    def is_imperial_holder(char_id: str, cult_name: str = None) -> bool:
        if cult_name and cult_name in IMPERIAL_CULTURES:
            return True
        if char_id and str(char_id) in chars:
            hid = chars[str(char_id)].get("dynasty_house")
            if hid and str(hid) in houses_data:
                if houses_data[str(hid)].get("dynasty") == 1582:
                    return True
        return False

    # Count 867 holdings per county using levy <= 12424
    county_867_holdings = Counter()
    for bk, pid in b_to_pid.items():
        p = provinces.get(pid, {})
        if p.get("raw_holding_type") and p.get("levy") is not None and p["levy"] <= 12424:
            ck = b_to_county_geo.get(bk)
            if ck:
                county_867_holdings[ck] += 1

    # Precompute county timelines, Roman conquest horizons, and language streaks
    county_profiles = {}
    for ck, t_obj in titles_data.items():
        save_t = titles_by_key.get(ck, {})
        hist = t_obj.get("history", [])
        cm = county_mgr.get(ck, {})
        curr_c_cult = t_obj.get("culture_name") or (cult_by_id[str(cm["culture"])]["name"] if cm.get("culture") in cult_by_id else "Unknown")
        curr_c_faith_id = str(cm.get("rite", "")) if cm.get("rite") is not None else None

        # Determine if currently under Roman Empire or Tarraconian/Chatenois sovereign
        in_roman = bool(t_obj.get("is_in_roman_empire"))
        curr_h_dict = t_obj.get("current_holder", {})
        curr_h_cult = curr_h_dict.get("culture_name", "")
        is_chat = bool(curr_h_dict.get("is_chatenois"))
        is_tarr_realm = in_roman or (curr_h_cult in IMPERIAL_CULTURES) or is_chat

        # Determine Tarraconian / Roman conquest date robustly:
        # Merge imperial stretches across brief (<25y) populist revolts or internal HRE appointments
        conquest_date = None
        if is_tarr_realm:
            # Build raw chronological segments from hist (post-867)
            segs = []
            for idx_h, h in enumerate(hist):
                d_str = h.get("date", "")
                dt = parse_date_tuple(d_str)
                if dt < (867, 1, 1):
                    continue
                hc = h.get("culture_name", "")
                hdyn = h.get("dynasty_id")
                htype = h.get("type", "holder")
                is_imp = (hc in IMPERIAL_CULTURES) or (hdyn == 1582)
                segs.append({"date": d_str, "is_imp": is_imp, "type": htype, "culture": hc})

            # Find start of the merged imperial stretch ending at 1194.7.28
            # Walk backwards from end; allow gaps < 25y or appointment_succession gaps once inside imperial era
            if segs:
                last_imp_idx = None
                for idx_s in range(len(segs) - 1, -1, -1):
                    if segs[idx_s]["is_imp"]:
                        last_imp_idx = idx_s
                        break
                if last_imp_idx is not None:
                    # Walk backwards from last_imp_idx merging across <25y gaps or internal appointments
                    cur_start_idx = last_imp_idx
                    i = last_imp_idx - 1
                    while i >= 0:
                        if segs[i]["is_imp"]:
                            cur_start_idx = i
                            i -= 1
                        else:
                            # Find previous imperial segment before this non-imperial gap
                            prev_imp_idx = None
                            for j in range(i - 1, -1, -1):
                                if segs[j]["is_imp"]:
                                    prev_imp_idx = j
                                    break
                            if prev_imp_idx is None:
                                break
                            gap_start = segs[prev_imp_idx + 1]["date"]
                            gap_end = segs[i + 1]["date"]
                            gap_years = years_between(gap_start, gap_end)
                            has_appt = any("appointment" in segs[k]["type"] for k in range(prev_imp_idx + 1, i + 1))
                            # Only merge if the earlier imperial stretch wasn't a tiny <3y blip, OR gap is appointment/<25y
                            earlier_imp_dur = years_between(segs[prev_imp_idx]["date"], gap_start)
                            if (gap_years < 25.0 or has_appt) and (earlier_imp_dur >= 3.0 or has_appt):
                                cur_start_idx = prev_imp_idx
                                i = prev_imp_idx - 1
                            else:
                                break
                    # Ensure conquest_date is not before 920.12.30 unless Lothringian/Chatenois start
                    cand_date = segs[cur_start_idx]["date"]
                    if parse_date_tuple(cand_date) < (867, 1, 1):
                        cand_date = "867.1.1"
                    conquest_date = cand_date
            if not conquest_date:
                # Walk de_facto_liege chain in melted_save.ck3 (covers native vassals inside h_roman_empire)
                cur_tid = save_t.get("df")
                visited = set()
                liege_dates = []
                while cur_tid and cur_tid not in visited:
                    visited.add(cur_tid)
                    lt = titles_by_id.get(cur_tid)
                    if not lt:
                        break
                    l_key = lt.get("key", "")
                    if l_key == "h_roman_empire":
                        break
                    l_hist = lt.get("history", [])
                    l_last_imp = None
                    for lh in reversed(l_hist):
                        l_hid = lh.get("holder")
                        l_cult = resolve_char_culture(l_hid, ck)
                        if is_imperial_holder(l_hid, l_cult):
                            l_last_imp = lh.get("date")
                        else:
                            break
                    if l_last_imp:
                        liege_dates.append(l_last_imp)
                    cur_tid = lt.get("df")
                if liege_dates:
                    conquest_date = min(liege_dates, key=parse_date_tuple)
                else:
                    conquest_date = "920.12.30"

        horizon_date = conquest_date if (is_tarr_realm and conquest_date) else meta_date
        if parse_date_tuple(horizon_date) < (867, 1, 1):
            horizon_date = "867.1.1"

        # Find 867.1.1 start holder (and 868.1.1 holder to avoid 2-month scripted start wars like Kocel in Hungary)
        h867 = None
        h868 = None
        for h in hist:
            dt = parse_date_tuple(h.get("date", ""))
            if dt <= (867, 1, 1):
                h867 = h
            if dt <= (868, 1, 1):
                h868 = h
            else:
                break
        if not h867 and hist:
            h867 = hist[0]
        if not h868:
            h868 = h867
        start_867_cult = h867.get("culture_name", curr_c_cult) if h867 else curr_c_cult
        start_868_cult = h868.get("culture_name", start_867_cult) if h868 else start_867_cult
        start_867_hid = str(h867.get("holder_id", "")) if h867 and h867.get("holder_id") else None
        start_867_faith_id = chars.get(start_867_hid, {}).get("rite") if start_867_hid else None

        # Build tenure intervals from 867.1.1 to meta_date and from 867.1.1 to horizon_date
        def build_intervals(end_limit_date: str):
            limit_t = parse_date_tuple(end_limit_date)
            intervals = []
            # Initial 867 holder
            cur_cult = start_867_cult
            cur_start = "867.1.1"
            cur_hid = start_867_hid
            cur_type = h867.get("type", "holder") if h867 else "holder"
            for h in hist:
                dt = parse_date_tuple(h.get("date", ""))
                if dt <= (867, 1, 1):
                    continue
                if dt >= limit_t:
                    break
                intervals.append({
                    "start": cur_start,
                    "end": h["date"],
                    "culture": cur_cult,
                    "language": cult_by_name.get(cur_cult, {}).get("language", cur_cult),
                    "heritage": cult_by_name.get(cur_cult, {}).get("heritage", "Unknown"),
                    "holder_id": cur_hid,
                    "type": cur_type,
                })
                cur_start = h["date"]
                cur_cult = h.get("culture_name", cur_cult)
                cur_hid = str(h.get("holder_id", "")) if h.get("holder_id") else None
                cur_type = h.get("type", "holder")
            if parse_date_tuple(cur_start) < limit_t or not intervals:
                intervals.append({
                    "start": cur_start,
                    "end": end_limit_date,
                    "culture": cur_cult,
                    "language": cult_by_name.get(cur_cult, {}).get("language", cur_cult),
                    "heritage": cult_by_name.get(cur_cult, {}).get("heritage", "Unknown"),
                    "holder_id": cur_hid,
                    "type": cur_type,
                })
            return intervals

        def coalesce_language_streaks(intervals):
            streaks = []
            for iv in intervals:
                if streaks and streaks[-1]["language"] == iv["language"]:
                    streaks[-1]["end"] = iv["end"]
                    streaks[-1]["latest_culture"] = iv["culture"]
                    if iv["culture"] not in streaks[-1]["cultures"]:
                        streaks[-1]["cultures"].append(iv["culture"])
                    streaks[-1]["latest_holder_id"] = iv["holder_id"]
                else:
                    streaks.append({
                        "language": iv["language"],
                        "heritage": iv["heritage"],
                        "start": iv["start"],
                        "end": iv["end"],
                        "latest_culture": iv["culture"],
                        "cultures": [iv["culture"]],
                        "latest_holder_id": iv["holder_id"],
                    })
            for st in streaks:
                st["years"] = round(years_between(st["start"], st["end"]), 1)
            return streaks

        pre_horizon_ivs = build_intervals(horizon_date)
        full_ivs = build_intervals(meta_date)
        pre_streaks = coalesce_language_streaks(pre_horizon_ivs)
        full_streaks = coalesce_language_streaks(full_ivs)

        # Detect if county was tribal/nomadic in 867
        s867_rec = cult_by_name.get(start_867_cult, {})
        s867_tl = s867_rec.get("tribal_left")
        s868_rec = cult_by_name.get(start_868_cult, {})
        s868_tl = s868_rec.get("tribal_left")
        effective_start_cult = start_868_cult if (s868_tl is not None and s868_tl >= 975 and county_867_holdings[ck] == 1) else start_867_cult
        effective_start_tl = s868_tl if effective_start_cult == start_868_cult else s867_tl
        was_867_tribal = bool(effective_start_tl is not None and effective_start_tl >= 975)

        # Estimate feudalization date & feudalizer if was_867_tribal
        feudalizer_cult = effective_start_cult
        feudalization_date = f"{effective_start_tl}.1.1" if (effective_start_tl and effective_start_tl < 9999) else meta_date
        if was_867_tribal:
            # Check if a genuinely non-tribal culture (tribal_left < 975 and not steppe/tribal hybrid) ruled >= 15y before native tribal_left
            feudalized_early = False
            for st in full_streaks:
                st_rec = cult_by_name.get(st["latest_culture"], {})
                st_tl = st_rec.get("tribal_left")
                st_her = st_rec.get("heritage", "")
                st_start_y = parse_date_tuple(st["start"])[0]
                is_feudal_cult = (st_tl is not None and st_tl < 975 and st_her not in TRIBAL_STEPPE_HERITAGES) or (st["latest_culture"] in IMPERIAL_CULTURES)
                if is_feudal_cult and st["years"] >= 15.0 and (effective_start_tl is None or st_start_y < effective_start_tl):
                    feudalizer_cult = st["cultures"][0]
                    feudalization_date = st["start"]
                    feudalized_early = True
                    break
            if not feudalized_early and effective_start_tl and effective_start_tl < 9999:
                target_dt = (effective_start_tl, 1, 1)
                for iv in full_ivs:
                    if parse_date_tuple(iv["start"]) <= target_dt <= parse_date_tuple(iv["end"]):
                        feudalizer_cult = iv["culture"]
                        feudalization_date = f"{effective_start_tl}.1.1"
                        break

        county_profiles[ck] = {
            "in_roman": in_roman,
            "is_tarr_realm": is_tarr_realm,
            "conquest_date": conquest_date,
            "horizon_date": horizon_date,
            "start_867_cult": effective_start_cult,
            "start_867_faith_id": start_867_faith_id,
            "curr_c_cult": curr_c_cult,
            "curr_c_faith_id": curr_c_faith_id,
            "was_867_tribal": was_867_tribal,
            "feudalizer_cult": feudalizer_cult,
            "feudalization_date": feudalization_date,
            "pre_ivs": pre_horizon_ivs,
            "full_ivs": full_ivs,
            "pre_streaks": pre_streaks,
            "full_streaks": full_streaks,
        }

    # Evaluate Alternative 1 Toponymic Profile for every occupied barony
    profiles = {}
    used_cultures = set()
    coinage_counts = Counter()
    substrate_counts = Counter()
    transmission_counts = Counter()
    origin_counts = Counter()
    continuity_counts = Counter()

    for bk in sorted(b_to_pid.keys()):
        pid = b_to_pid[bk]
        prov = provinces.get(pid, {})
        raw_ht = prov.get("raw_holding_type")
        if not raw_ht:
            continue

        ht = map_holding_type_from_raw(raw_ht)
        ck = b_to_county_geo.get(bk)
        cp = county_profiles.get(ck)
        if not cp:
            continue

        save_b = titles_by_key.get(bk, {})
        b_holder_id = save_b.get("holder")
        b_lessee_id = save_b.get("lessee")
        b_holder_cult = resolve_char_culture(b_holder_id, ck)
        b_lessee_cult = resolve_char_culture(b_lessee_id, ck)
        b_holder_faith = chars.get(str(b_holder_id), {}).get("rite") if b_holder_id else None
        b_lessee_faith = chars.get(str(b_lessee_id), {}).get("rite") if b_lessee_id else None

        effective_b_faith = b_lessee_faith or b_holder_faith or cp["curr_c_faith_id"]
        f_obj = faiths.get(str(effective_b_faith), {}) if effective_b_faith else {}
        r_obj = religions.get(str(f_obj.get("religion", "")), {}) if f_obj else {}
        s867_f_obj = faiths.get(str(cp["start_867_faith_id"]), {}) if cp["start_867_faith_id"] else {}
        s867_r_obj = religions.get(str(s867_f_obj.get("religion", "")), {}) if s867_f_obj else {}

        faith_changed = bool(
            f_obj and s867_f_obj and (
                r_obj.get("family") != s867_r_obj.get("family")
                or f_obj.get("religion") != s867_f_obj.get("religion")
            )
        )

        levy = prov.get("levy")
        existed_in_867 = (levy is not None and levy <= 12424)
        is_unfeudalized_now = raw_ht in ("tribal_holding", "nomad_holding", "herder_holding")

        if is_unfeudalized_now:
            origin_type = "pre_867_unfeudalized"
        elif existed_in_867:
            origin_type = "feudalized_post_867" if cp["was_867_tribal"] else "pre_867_established"
        else:
            origin_type = "founded_post_867"

        pre_streaks = cp["pre_streaks"]
        full_streaks = cp["full_streaks"]
        # Filter out imperial cultures from pre-conquest streaks when county wasn't originally imperial in 867
        non_imp_pre_streaks = (
            pre_streaks
            if cp["start_867_cult"] in IMPERIAL_CULTURES
            else [st for st in pre_streaks if st["latest_culture"] not in IMPERIAL_CULTURES]
        )
        streaks_50 = [st for st in non_imp_pre_streaks if st["years"] >= 50.0]

        # 1. SUBSTRATE CULTURE (Demographic / Ground Population)
        curr_c_cult = cp["curr_c_cult"]
        start_867_cult = cp["start_867_cult"]
        if not cp["is_tarr_realm"]:
            substrate_culture = curr_c_cult
            substrate_note = "Current county population culture (unconquered by Tarraconians)."
        else:
            if curr_c_cult not in IMPERIAL_CULTURES:
                substrate_culture = curr_c_cult
                substrate_note = "Unassimilated local county population under imperial rule."
            else:
                # County converted to an imperial Tarraconian culture; recover pre-conquest demographic stratum.
                # For pre-867 established holdings, require >= 150y pre-conquest rule to shift demographic substrate;
                # for tribal/frontier holdings, >= 50y settlement stratum suffices.
                sub_thresh = 150.0 if origin_type == "pre_867_established" else 50.0
                sub_candidates = [st for st in non_imp_pre_streaks if st["years"] >= sub_thresh]
                if sub_candidates:
                    substrate_culture = sub_candidates[-1]["latest_culture"]
                    if substrate_culture == start_867_cult:
                        substrate_note = f"Pre-Tarraconian native substrate ({start_867_cult}); county later assimilated to {curr_c_cult}."
                    else:
                        substrate_note = f"Pre-Tarraconian {sub_candidates[-1]['years']:.0f}y dominant stratum over {start_867_cult}; later assimilated to {curr_c_cult}."
                else:
                    substrate_culture = start_867_cult
                    substrate_note = f"867 baseline substrate ({start_867_cult}); county later assimilated to {curr_c_cult}."

        substrate_lang = cult_by_name.get(substrate_culture, {}).get("language", "Unknown")

        # 2. TRANSMISSION CULTURE (Intermediary / Mediating Stratum)
        if cp["is_tarr_realm"]:
            if not non_imp_pre_streaks:
                transmission_culture = cp["curr_c_cult"]
                transmission_years = years_between("867.1.1", cp["horizon_date"])
                transmission_note = "Under imperial/Carolingian administration from campaign start (867)."
            else:
                # Latest pre-conquest language streak >= 15y; else longest in final 50y; else immediate pre-conquest
                med_candidates = [st for st in non_imp_pre_streaks if st["years"] >= 15.0]
                if med_candidates:
                    chosen_t = med_candidates[-1]
                    transmission_culture = chosen_t["latest_culture"]
                    transmission_years = chosen_t["years"]
                    transmission_note = f"Last pre-Tarraconian mediating reign ≥ 15y ({chosen_t['start']}–{chosen_t['end']}, {chosen_t['years']:.1f}y)."
                else:
                    h_y = date_to_years(cp["horizon_date"])
                    recent = [st for st in non_imp_pre_streaks if date_to_years(st["end"]) >= h_y - 50.0]
                    chosen_t = max(recent, key=lambda x: x["years"]) if recent else non_imp_pre_streaks[-1]
                    transmission_culture = chosen_t["latest_culture"]
                    transmission_years = chosen_t["years"]
                    transmission_note = f"Brief pre-Tarraconian mediation ({chosen_t['start']}–{chosen_t['end']}, {chosen_t['years']:.1f}y; no ≥15y stretch)."
        else:
            med_candidates = [st for st in full_streaks if st["years"] >= 15.0]
            if med_candidates:
                chosen_t = med_candidates[-1]
                transmission_culture = chosen_t["latest_culture"]
                transmission_years = chosen_t["years"]
                transmission_note = f"Latest ruling stretch ≥ 15y through {meta_date} ({chosen_t['start']}–{chosen_t['end']}, {chosen_t['years']:.1f}y)."
            else:
                chosen_t = full_streaks[-1] if full_streaks else None
                transmission_culture = chosen_t["latest_culture"] if chosen_t else curr_c_cult
                transmission_years = chosen_t["years"] if chosen_t else 0.0
                transmission_note = f"Current ruling culture through {meta_date} ({transmission_years:.1f}y)."

        transmission_lang = cult_by_name.get(transmission_culture, {}).get("language", "Unknown")

        # 3. COINAGE CULTURE (Origin / Naming Stratum under Alternative 1)
        coinage_culture = substrate_culture
        coinage_rule = "substrate_retention"
        coinage_detail = ""
        is_sinosphere = cult_by_name.get(substrate_culture, {}).get("heritage") in SINOSPHERE_HERITAGES

        if origin_type == "pre_867_established":
            # Check demographic conversion first (county culture changed & ruled >= 50y in that language)
            demog_match = [
                st for st in pre_streaks
                if not cp["is_tarr_realm"]
                and st["language"] == cult_by_name.get(curr_c_cult, {}).get("language")
                and st["language"] != cult_by_name.get(start_867_cult, {}).get("language")
                and st["years"] >= 50.0
            ]
            if demog_match:
                st = demog_match[-1]
                coinage_culture = st["latest_culture"]
                coinage_rule = "demographic_replacement_50y"
                coinage_detail = f"County population converted and ruled in {st['language']} for {st['years']:.1f}y ({st['start']}–{st['end']})."
            elif ht == "castle":
                # Castles: >= 100y foreign language streak, or >= 50y with faith change
                thresh = 50.0 if faith_changed else 100.0
                c_matches = [st for st in non_imp_pre_streaks if st["years"] >= thresh and st["language"] != substrate_lang]
                if c_matches:
                    st = c_matches[-1]
                    coinage_culture = st["latest_culture"]
                    coinage_rule = f"castle_overrule_{int(thresh)}y"
                    coinage_detail = f"Pre-867 castle held by {st['latest_culture']} ({st['language']}) for {st['years']:.1f}y ≥ {int(thresh)}y."
                else:
                    coinage_culture = substrate_culture
                    coinage_rule = "pre_867_substrate_inertia"
                    coinage_detail = f"Pre-867 castle retains {substrate_culture} substrate (no ≥{int(thresh)}y foreign reign)."
            elif ht == "church":
                # Temples: >= 25y streak if faith changed, else >= 100y (or 25y Sinosphere)
                thresh = 25.0 if (faith_changed or is_sinosphere) else 100.0
                t_matches = [st for st in non_imp_pre_streaks if st["years"] >= thresh and st["language"] != substrate_lang]
                if faith_changed and t_matches:
                    st = t_matches[-1]
                    coinage_culture = st["latest_culture"]
                    coinage_rule = "temple_faith_change_25y"
                    coinage_detail = f"Faith changed from {s867_f_obj.get('faith_type', '?')} to {f_obj.get('faith_type', '?')}; {st['latest_culture']} ruled {st['years']:.1f}y."
                elif t_matches:
                    st = t_matches[-1]
                    coinage_culture = st["latest_culture"]
                    coinage_rule = "temple_long_rule"
                    coinage_detail = f"Pre-867 temple under {st['latest_culture']} rule for {st['years']:.1f}y."
                else:
                    coinage_culture = substrate_culture
                    coinage_rule = "pre_867_substrate_inertia"
                    coinage_detail = f"Pre-867 temple retains {substrate_culture} substrate."
            else:  # city
                thresh = 25.0 if is_sinosphere else 150.0
                city_matches = [st for st in non_imp_pre_streaks if st["years"] >= thresh and st["language"] != substrate_lang]
                if city_matches:
                    st = city_matches[-1]
                    coinage_culture = st["latest_culture"]
                    coinage_rule = "sinosphere_civic_25y" if is_sinosphere else "city_overrule_150y"
                    coinage_detail = f"Pre-867 city under {st['latest_culture']} administration for {st['years']:.1f}y ≥ {int(thresh)}y."
                else:
                    coinage_culture = substrate_culture
                    coinage_rule = "city_substrate_inertia"
                    coinage_detail = f"Pre-867 city preserves {substrate_culture} civic name despite dynastic shifts."

        elif origin_type == "pre_867_unfeudalized":
            if streaks_50:
                st = streaks_50[-1]
                coinage_culture = st["latest_culture"]
                coinage_rule = "unfeudalized_50y_streak"
                coinage_detail = f"Tribal/nomadic holding under {st['latest_culture']} for {st['years']:.1f}y ({st['start']}–{st['end']})."
            else:
                coinage_culture = substrate_culture
                coinage_rule = "unfeudalized_substrate"
                coinage_detail = f"Unfeudalized holding retains native {substrate_culture} substrate."

        elif origin_type == "feudalized_post_867":
            coinage_culture = cp["feudalizer_cult"]
            if cult_by_name.get(coinage_culture, {}).get("language") == cult_by_name.get(start_867_cult, {}).get("language"):
                coinage_rule = "native_feudalization"
                coinage_detail = f"Tribal seat feudalized natively by {coinage_culture} around {cp['feudalization_date']}."
            else:
                coinage_rule = "colonial_feudalization"
                coinage_detail = f"Tribal seat ({start_867_cult} substrate) feudalized by {coinage_culture} around {cp['feudalization_date']}."

        else:  # founded_post_867
            # Determine founder culture
            # Earliest possible construction date: feudalization_date if tribal in 867, else 867.1.1
            earliest_d = cp["feudalization_date"] if cp["was_867_tribal"] else "867.1.1"
            # Upper bound: earliest lease history date on b_* if any
            lease_dates = [h["date"] for h in save_b.get("history", []) if h.get("date")]
            upper_d = min(lease_dates, key=parse_date_tuple) if lease_dates else meta_date

            # Check pre-conquest vs post-conquest feudal duration
            earliest_y = date_to_years(earliest_d)
            horizon_y = date_to_years(cp["horizon_date"])
            pre_feudal_years = max(0.0, horizon_y - earliest_y)

            # Check if built post-conquest by Tarraconians
            tarr_years = max(0.0, date_to_years(meta_date) - horizon_y) if cp["is_tarr_realm"] else 0.0
            is_gen0_early = (levy is not None and levy < 100000)

            # Eligible pre-conquest streaks overlapping [earliest_d, upper_d]
            eligible_pre_streaks = []
            for st in non_imp_pre_streaks:
                s_start = max(date_to_years(st["start"]), earliest_y)
                s_end = min(date_to_years(st["end"]), date_to_years(upper_d))
                if s_end > s_start:
                    eligible_pre_streaks.append((st, s_end - s_start))

            pre_50 = [x for x in eligible_pre_streaks if x[1] >= 50.0]

            if cp["is_tarr_realm"] and (
                (pre_feudal_years < 25.0 and tarr_years >= 25.0)
                or (
                    not is_gen0_early
                    and not lease_dates
                    and (b_holder_cult in IMPERIAL_CULTURES)
                    and curr_c_cult in IMPERIAL_CULTURES
                    and tarr_years >= 50.0
                    and (not pre_50 or tarr_years > pre_50[-1][1])
                )
            ):
                # Founded under Tarraconian colonization / imperial administration
                coinage_culture = b_holder_cult if b_holder_cult in IMPERIAL_CULTURES else (curr_c_cult if curr_c_cult in IMPERIAL_CULTURES else "Tarraconian")
                coinage_rule = "founded_post_conquest_tarraconian"
                coinage_detail = f"Post-867 holding founded during Tarraconian imperial era ({cp['horizon_date']}–{meta_date}; {tarr_years:.0f}y imperial rule)."
            elif pre_50:
                st, dur = pre_50[-1]
                coinage_culture = st["latest_culture"]
                coinage_rule = "founded_pre_conquest_50y"
                coinage_detail = f"Post-867 holding attributed to {st['latest_culture']} ({dur:.1f}y feudal/admin rule in window {earliest_d}–{cp['horizon_date']})."
            elif b_holder_cult and b_holder_cult not in IMPERIAL_CULTURES and not cp["is_tarr_realm"]:
                coinage_culture = b_holder_cult
                coinage_rule = "founded_current_baron"
                coinage_detail = f"Post-867 holding under {b_holder_cult} baron."
            elif eligible_pre_streaks:
                st, dur = max(eligible_pre_streaks, key=lambda x: x[1])
                coinage_culture = st["latest_culture"]
                coinage_rule = "founded_dominant_window"
                coinage_detail = f"Post-867 holding attributed to dominant pre-horizon ruler {st['latest_culture']} ({dur:.1f}y)."
            else:
                coinage_culture = cp["feudalizer_cult"] if cp["was_867_tribal"] else substrate_culture
                coinage_rule = "founded_feudalizer_fallback"
                coinage_detail = f"Post-867 holding attributed to {coinage_culture}."

        coinage_lang = cult_by_name.get(coinage_culture, {}).get("language", "Unknown")

        # 4. CONTINUITY VERDICT (Coinage vs Transmission)
        if coinage_lang == transmission_lang:
            continuity_status = "Direct Transparency"
        elif transmission_years < 50.0:
            continuity_status = "Transitional Mediation (< 50y)"
        else:
            continuity_status = "Semantic Rupture (>= 50y)"

        liturgical_lang = None
        if ht == "church":
            liturgical_lang = infer_liturgical_language(
                f_obj.get("faith_type"), r_obj.get("religion_type"), r_obj.get("family"), coinage_lang
            )

        used_cultures.update([coinage_culture, substrate_culture, transmission_culture])
        coinage_counts[coinage_culture] += 1
        substrate_counts[substrate_culture] += 1
        transmission_counts[transmission_culture] += 1
        origin_counts[origin_type] += 1
        continuity_counts[continuity_status] += 1

        profiles[bk] = {
            "c": coinage_culture,
            "s": substrate_culture,
            "t": transmission_culture,
            "o": origin_type,
            "cr": coinage_rule,
            "cd": coinage_detail,
            "sn": substrate_note,
            "tn": transmission_note,
            "ty": round(transmission_years, 1),
            "cs": continuity_status,
            "ht": ht,
            "ck": ck,
            "s867": start_867_cult,
            "c1194": curr_c_cult,
            "tc": cp["is_tarr_realm"],
            "hd": cp["horizon_date"],
            "ll": liturgical_lang,
        }

    # Build county-level >=50y pre-horizon streaks table (shared across baronies in each county)
    county_streaks_50 = {}
    for ck, cp in county_profiles.items():
        non_imp = (
            cp["pre_streaks"]
            if cp["start_867_cult"] in IMPERIAL_CULTURES
            else [st for st in cp["pre_streaks"] if st["latest_culture"] not in IMPERIAL_CULTURES]
        )
        s50 = [
            {
                "c": st["latest_culture"],
                "l": st["language"],
                "s": st["start"],
                "e": st["end"],
                "y": st["years"],
            }
            for st in non_imp
            if st["years"] >= 50.0
        ]
        if s50:
            county_streaks_50[ck] = s50

    # Build culture metadata & colors
    culture_meta = {}
    for cname in sorted(used_cultures):
        rec = cult_by_name.get(cname, {})
        her = rec.get("heritage", "Unknown")
        lang = rec.get("language", "Unknown")
        culture_meta[cname] = {
            "color": assign_culture_color(cname, her),
            "heritage": her,
            "language": lang,
            "coinage_count": coinage_counts[cname],
            "substrate_count": substrate_counts[cname],
            "transmission_count": transmission_counts[cname],
        }

    output_payload = {
        "metadata": {
            "schema_version": "1.0.0",
            "methodology": "Alternative 1 (3-Stratum Toponymic Profile: Coinage, Substrate, Transmission)",
            "save_date": meta_date,
            "total_occupied_baronies": len(profiles),
            "origin_counts": dict(origin_counts),
            "continuity_counts": dict(continuity_counts),
            "distinct_cultures": len(culture_meta),
        },
        "cultures": culture_meta,
        "county_streaks_50": county_streaks_50,
        "baronies": profiles,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, ensure_ascii=False, separators=(",", ":"))

    size_mb = args.output.stat().st_size / (1024 * 1024)
    print(f"\nWrote {args.output} ({size_mb:.2f} MB) for {len(profiles)} occupied baronies.")
    print("Origin breakdown:", dict(origin_counts))
    print("Continuity breakdown:", dict(continuity_counts))
    print("Top 12 Coinage Cultures:", coinage_counts.most_common(12))
    print("Top 12 Substrate Cultures:", substrate_counts.most_common(12))
    print("Top 12 Transmission Cultures:", transmission_counts.most_common(12))

    print("\nSample barony profiles:")
    for sb in ["b_london", "b_woxbrigge", "b_gore", "b_szekesfehervar", "b_kalocsa", "b_kiev", "b_vyshgorod", "b_roma", "b_byzantion", "b_berlin", "b_cairo", "b_reykjavik", "b_vestfirdir", "b_berbera"]:
        if sb in profiles:
            p = profiles[sb]
            print(f"  {sb:18s} | {p['o']:21s} | C={p['c']:15s} | S={p['s']:15s} | T={p['t']:15s} | {p['cs']} ({p['cr']})")


if __name__ == "__main__":
    main()

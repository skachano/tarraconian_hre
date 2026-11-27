#!/usr/bin/env python3
"""
extract_barony_coinage_and_context.py

Extracts the Section 4.A datasets from melted_save.ck3 and Phase 1 / Toponymic Profile data:
  1. data/barony_coinage_rulers.json
  2. data/barony_physical_and_event_context.json
  3. Reconciles data/barony_holdings.json (10,239 occupied / 1,058 unoccupied)
"""

import argparse
import json
import re
import time
from collections import Counter, defaultdict
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_DIR / "data"
SAVE_PATH = Path("/var/tmp/ck3_audit/melted_save.ck3")
PHASE1_DIR = Path("/var/tmp/ck3_audit/phase1")

from ck3_name_decoder import clean_ck3_name


IMPERIAL_CULTURES = {
    "Tarraconian",
    "Lothringian",
    "Croato-Tarraconian",
    "Alpine-Tarraconian",
    "Ungwârer",
}

PIOUS_TRAITS = {"zealous", "theologian", "pilgrim", "monk", "celibate", "humble", "devoted", "hajjaj", "saint"}
VAIN_TRAITS = {"arrogant", "ambitious", "greedy", "august", "fickle"}
MARTIAL_TRAITS = {
    "brave", "strategist", "architect", "paranoid", "craven",
    "military_engineer", "holy_warrior", "reaver", "organizer",
    "unyielding_defender", "aggressive_attacker", "gallant", "overseer",
}
MERCANTILE_TRAITS = {
    "education_stewardship_3", "education_stewardship_4",
    "avaricious", "diligent", "administrator", "profligate",
}


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


def is_circular_house(house_name: str, barony_key: str, county_key: str) -> bool:
    if not house_name:
        return False

    def norm(s):
        s = re.sub(r"[^a-z]", "", s.lower())
        s = s.replace("y", "i").replace("ie", "i").replace("ae", "e").replace("oe", "e").replace("ph", "f").replace("ck", "k")
        return re.sub(r"(.)\1+", r"\1", s)

    h = norm(house_name.replace("Chatenois-", "").replace("Kestenholz-", "").replace("dynn_", ""))
    if len(h) < 3:
        return False
    b = norm((barony_key or "").replace("b_", ""))
    c = norm((county_key or "").replace("c_", ""))
    return bool((b and (h in b or b in h)) or (c and (h in c or c in h)))


def classify_archetype(traits_decoded: list, piety: float, prestige: float, holding_type: str, ctx: dict) -> tuple:
    tset = set(traits_decoded or [])
    pious_hits = sorted(tset & PIOUS_TRAITS)
    vain_hits = sorted(tset & VAIN_TRAITS)
    martial_hits = sorted(tset & MARTIAL_TRAITS)
    merc_hits = sorted(tset & MERCANTILE_TRAITS)

    pois = set(ctx.get("points_of_interest") or [])
    bldgs = set(ctx.get("building_families") or [])
    has_ho = bool(ctx.get("holy_order_lease"))
    has_saint = bool(ctx.get("saint_shrine")) or ("poi_buried_saint" in pois)
    has_battle = bool(pois & {"poi_battles", "poi_battles_historical"})

    # Note: CK3 accumulated piety/prestige includes a +1000 baseline on living characters
    if holding_type == "church" and (has_saint or pious_hits or piety >= 2500.0):
        return "pious_devotional", pious_hits or (["buried_saint"] if has_saint else ["high_piety"])
    if pious_hits and len(pious_hits) >= max(len(vain_hits), len(martial_hits)):
        return "pious_devotional", pious_hits
    if has_ho or (holding_type == "castle" and has_battle):
        signals = list(martial_hits)
        if has_ho:
            signals.append("holy_order_lease")
        if has_battle:
            signals.append("poi_battle")
        return "martial_frontier", signals
    if vain_hits and len(vain_hits) > len(martial_hits):
        return "vain_dynastic", vain_hits
    if prestige >= 3500.0 and not martial_hits:
        return "vain_dynastic", ["high_prestige"]
    if martial_hits and holding_type == "castle" and len(martial_hits) >= 2:
        return "martial_frontier", martial_hits
    if holding_type == "city" and (merc_hits or ("common_tradeport" in bldgs and "education_stewardship_2" in tset)):
        signals = list(merc_hits)
        if "common_tradeport" in bldgs:
            signals.append("common_tradeport")
        return "mercantile_civic", signals
    if len(merc_hits) >= 2:
        return "mercantile_civic", merc_hits
    return "topographic_default", []


def parse_save_context_and_chars(save_path: Path, extra_char_ids: set):
    """Two-pass streaming parse over melted_save.ck3 for physical/event context and full character details."""
    t0 = time.time()
    print(f"Pass 1: Streaming physical & title context from {save_path} ...")

    meta_date = "1194.7.28"
    traits_lookup = []
    provinces = {}        # pid -> {...}
    baronies_save = {}    # b_key -> {id, holder, date, lessee, leases, capital_barony}
    title_id_to_key = {}  # tid -> key
    religions = {}
    faiths = {}
    holy_orders = {}      # order_id -> {...}
    title_to_holy_order = {}  # barony_tid -> order_obj
    epidemics_by_prov = defaultdict(list)
    county_plague_mod = set()
    needed_chars = set(extra_char_ids)

    sec = None
    sub = None
    cur_pid = None
    in_hold = False
    in_bldg = False
    in_poi = False

    cur_tid = None
    cur_tkey = None
    cur_holder = None
    cur_date = None
    cur_lessee = None
    cur_cap = False
    cur_leases = []
    in_hist = False
    cur_hist_date = None

    cur_rel_id = None
    in_faith_db = False
    cur_fid = None
    in_saints = False

    cur_cm_county = None
    cur_ho_id = None
    in_ho_titles = False

    in_epi_db = False
    cur_epi_id = None
    cur_epi = None
    in_epi_inf = False
    cur_inf_pid = None

    with open(save_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("meta_data={"):
                sec = "meta"; continue
            elif line.startswith("traits_lookup={"):
                sec = "traits"; continue
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
            elif line.startswith("holy_orders={"):
                sec = "holy_orders"; continue
            elif line.startswith("epidemics={"):
                sec = "epidemics"; continue
            elif sec and line.startswith("}"):
                if sec == "landed_titles" and cur_tid and cur_tkey and cur_tkey.startswith("b_"):
                    baronies_save[cur_tkey] = {
                        "title_id": cur_tid,
                        "holder": cur_holder,
                        "date": cur_date,
                        "lessee": cur_lessee,
                        "capital_barony": cur_cap,
                        "leases": cur_leases,
                    }
                sec = None
                sub = None
                continue

            if not sec:
                continue

            if sec == "meta":
                if line.startswith("\tmeta_date="):
                    meta_date = line.strip().split("=", 1)[1]

            elif sec == "traits":
                traits_lookup.extend(line.strip().split())

            elif sec == "provinces":
                if line.startswith("\t") and not line.startswith("\t\t") and "={" in line:
                    cur_pid = line.strip().split("=", 1)[0]
                    provinces[cur_pid] = {
                        "raw_holding_type": None,
                        "buildings": [],
                        "special_building_type": None,
                        "great_building_type": None,
                        "duchy_capital_building": None,
                        "fort_level": 0,
                        "income": 0.0,
                        "points_of_interest": [],
                    }
                    in_hold = False
                    in_bldg = False
                    in_poi = False
                elif cur_pid is not None:
                    if line.startswith("\t}"):
                        cur_pid = None
                        in_hold = False
                        in_bldg = False
                        in_poi = False
                    elif line.startswith("\t\tholding={"):
                        in_hold = True
                    elif in_hold:
                        if line.startswith("\t\t}"):
                            in_hold = False
                            in_bldg = False
                        elif line.startswith("\t\t\ttype="):
                            provinces[cur_pid]["raw_holding_type"] = line.strip().split("=", 1)[1].strip('"')
                        elif line.startswith("\t\t\tspecial_building_type="):
                            provinces[cur_pid]["special_building_type"] = line.strip().split("=", 1)[1].strip('"')
                        elif line.startswith("\t\t\tgreat_building_type="):
                            provinces[cur_pid]["great_building_type"] = line.strip().split("=", 1)[1].strip('"')
                        elif line.startswith("\t\t\tduchy_capital_building={"):
                            pass
                        elif line.startswith("\t\t\t\ttype=") and not in_bldg:
                            if provinces[cur_pid]["duchy_capital_building"] is None:
                                val = line.strip().split("=", 1)[1].strip('"')
                                if not val.startswith("great_project_"):
                                    provinces[cur_pid]["duchy_capital_building"] = val
                        elif line.startswith("\t\t\tincome="):
                            try:
                                provinces[cur_pid]["income"] = round(float(line.strip().split("=", 1)[1]), 2)
                            except ValueError:
                                pass
                        elif line.startswith("\t\t\tbuildings={"):
                            in_bldg = True
                        elif in_bldg:
                            if line.startswith("\t\t\t}"):
                                in_bldg = False
                            elif line.startswith("\t\t\t\t\ttype="):
                                provinces[cur_pid]["buildings"].append(line.strip().split("=", 1)[1].strip('"'))
                    elif line.startswith("\t\tfort_level="):
                        try:
                            provinces[cur_pid]["fort_level"] = int(line.strip().split("=", 1)[1])
                        except ValueError:
                            pass
                    elif line.startswith("\t\tpoints_of_interest={"):
                        in_poi = True
                    elif in_poi:
                        if line.startswith("\t\t}"):
                            in_poi = False
                        else:
                            for p_str in re.findall(r'"([^"]+)"', line):
                                provinces[cur_pid]["points_of_interest"].append(p_str)

            elif sec == "landed_titles":
                if line.startswith("\t\t") and not line.startswith("\t\t\t") and "={" in line:
                    if cur_tid and cur_tkey and cur_tkey.startswith("b_"):
                        baronies_save[cur_tkey] = {
                            "title_id": cur_tid,
                            "holder": cur_holder,
                            "date": cur_date,
                            "lessee": cur_lessee,
                            "capital_barony": cur_cap,
                            "leases": cur_leases,
                        }
                    cur_tid = line.strip().split("=", 1)[0]
                    cur_tkey = None
                    cur_holder = None
                    cur_date = None
                    cur_lessee = None
                    cur_cap = False
                    cur_leases = []
                    in_hist = False
                    cur_hist_date = None
                elif cur_tid is not None:
                    if line.startswith("\t\t}"):
                        if cur_tkey and cur_tkey.startswith("b_"):
                            baronies_save[cur_tkey] = {
                                "title_id": cur_tid,
                                "holder": cur_holder,
                                "date": cur_date,
                                "lessee": cur_lessee,
                                "capital_barony": cur_cap,
                                "leases": cur_leases,
                            }
                        cur_tid = None
                        cur_tkey = None
                        in_hist = False
                    elif line.startswith("\t\t\tkey=\""):
                        cur_tkey = line.strip().split('"', 2)[1]
                        title_id_to_key[cur_tid] = cur_tkey
                    elif cur_tkey and cur_tkey.startswith("b_"):
                        if line.startswith("\t\t\thistory={"):
                            in_hist = True
                        elif in_hist:
                            if line.startswith("\t\t\t}"):
                                in_hist = False
                            elif line.startswith("\t\t\t\t") and not line.startswith("\t\t\t\t\t") and "=" in line:
                                cur_hist_date = line.strip().split("=", 1)[0]
                            elif line.startswith("\t\t\t\t\ttype="):
                                ltype = line.strip().split("=", 1)[1].strip('"')
                                cur_leases.append({"date": cur_hist_date, "type": ltype, "holder": None})
                            elif line.startswith("\t\t\t\t\tholder=") and cur_leases:
                                lh = line.strip().split("=", 1)[1]
                                cur_leases[-1]["holder"] = lh
                                needed_chars.add(lh)
                        elif line.startswith("\t\t\tholder="):
                            cur_holder = line.strip().split("=", 1)[1]
                            needed_chars.add(cur_holder)
                        elif line.startswith("\t\t\tdate="):
                            cur_date = line.strip().split("=", 1)[1]
                        elif line.startswith("\t\t\tlessee="):
                            cur_lessee = line.strip().split("=", 1)[1]
                            needed_chars.add(cur_lessee)
                        elif line.startswith("\t\t\tcapital_barony=yes"):
                            cur_cap = True

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
                        faiths[cur_fid] = {"saints": []}
                        in_saints = False
                    elif cur_fid:
                        if line.startswith("\t\t\tsaints={"):
                            in_saints = True
                        elif in_saints:
                            if line.startswith("\t\t\t}"):
                                in_saints = False
                            else:
                                for sid in line.strip().split():
                                    if sid.isdigit():
                                        faiths[cur_fid]["saints"].append(sid)
                                        needed_chars.add(sid)
                        elif line.startswith("\t\t\t") and not line.startswith("\t\t\t\t") and "=" in line:
                            k, v = line.strip().split("=", 1)
                            if k in ("faith_type", "religion", "name"):
                                faiths[cur_fid][k] = v.strip('"')

            elif sec == "county_manager":
                if line.startswith("\t\t") and not line.startswith("\t\t\t") and "={" in line:
                    c_cand = line.strip().split("=", 1)[0]
                    cur_cm_county = c_cand if c_cand.startswith("c_") else None
                elif cur_cm_county and line.startswith("\t\t}"):
                    cur_cm_county = None
                elif cur_cm_county and 'modifier="shattered_by_plague"' in line:
                    county_plague_mod.add(cur_cm_county)

            elif sec == "holy_orders":
                if line.startswith("\t\t") and not line.startswith("\t\t\t") and "={" in line:
                    cur_ho_id = line.strip().split("=", 1)[0]
                    holy_orders[cur_ho_id] = {"order_id": cur_ho_id, "titles": [], "rite": None, "title": None, "founder": None, "holy_order_type": None}
                    in_ho_titles = False
                elif cur_ho_id:
                    if line.startswith("\t\t}"):
                        for tid in holy_orders[cur_ho_id]["titles"]:
                            title_to_holy_order[tid] = holy_orders[cur_ho_id]
                        cur_ho_id = None
                        in_ho_titles = False
                    elif line.startswith("\t\t\ttitles={"):
                        in_ho_titles = True
                    elif in_ho_titles:
                        if line.startswith("\t\t\t}"):
                            in_ho_titles = False
                        else:
                            holy_orders[cur_ho_id]["titles"].extend(line.strip().split())
                    elif line.startswith("\t\t\t") and not line.startswith("\t\t\t\t") and "=" in line:
                        k, v = line.strip().split("=", 1)
                        v = v.strip('"')
                        if k in ("rite", "title", "founder", "holy_order_type"):
                            holy_orders[cur_ho_id][k] = v
                            if k == "founder":
                                needed_chars.add(v)

            elif sec == "epidemics":
                if line.startswith("\tdatabase={"):
                    in_epi_db = True
                elif in_epi_db:
                    if line.startswith("\t}"):
                        in_epi_db = False
                    elif line.startswith("\t\t") and not line.startswith("\t\t\t") and "={" in line:
                        cur_epi_id = line.strip().split("=", 1)[0]
                        cur_epi = {"id": cur_epi_id, "type": None, "intensity": None, "name": None}
                        in_epi_inf = False
                        cur_inf_pid = None
                    elif cur_epi is not None:
                        if line.startswith("\t\t}"):
                            cur_epi = None
                            in_epi_inf = False
                        elif line.startswith("\t\t\tinfections={"):
                            in_epi_inf = True
                        elif in_epi_inf:
                            if line.startswith("\t\t\t}"):
                                in_epi_inf = False
                                cur_inf_pid = None
                            elif line.startswith("\t\t\t\t") and not line.startswith("\t\t\t\t\t") and "={" in line:
                                cur_inf_pid = line.strip().split("=", 1)[0]
                                epidemics_by_prov[cur_inf_pid].append({
                                    "type": cur_epi["type"],
                                    "intensity": cur_epi["intensity"],
                                    "name": cur_epi["name"],
                                })
                        elif line.startswith("\t\t\t") and not line.startswith("\t\t\t\t") and "=" in line:
                            k, v = line.strip().split("=", 1)
                            v = v.strip('"')
                            if k in ("type", "intensity", "name"):
                                cur_epi[k] = v

    print(f"  Pass 1 finished in {time.time() - t0:.2f}s: {len(provinces)} provs, {len(baronies_save)} baronies, {len(needed_chars)} chars needed.")

    # Pass 2: Extract full character data (including traits, piety, prestige, faith, house)
    t1 = time.time()
    chars = {}
    sec = None
    cur_cid = None
    in_traits = False
    in_alive = False
    in_piety = False
    in_prestige = False

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
                in_traits = False
                in_alive = False
                continue

            if not sec:
                continue

            if sec in ("living", "dead_unprunable"):
                if line.startswith("\t") and not line.startswith("\t\t") and "={" in line:
                    cid = line.strip().split("=", 1)[0]
                    cur_cid = cid if cid in needed_chars else None
                    if cur_cid and cur_cid not in chars:
                        chars[cur_cid] = {
                            "id": int(cur_cid) if cur_cid.isdigit() else cur_cid,
                            "alive": (sec == "living"),
                            "first_name": "",
                            "nickname": "",
                            "birth": None,
                            "death": None,
                            "culture": None,
                            "rite": None,
                            "dynasty_house": None,
                            "traits": [],
                            "piety": 0.0,
                            "prestige": 0.0,
                        }
                    in_traits = False
                    in_alive = False
                    in_piety = False
                    in_prestige = False
                elif cur_cid:
                    if line.startswith("\t}"):
                        cur_cid = None
                    elif line.startswith("\t\tfirst_name="):
                        chars[cur_cid]["first_name"] = line.strip().split("=", 1)[1].strip('"')
                    elif line.startswith("\t\tnickname_text="):
                        chars[cur_cid]["nickname"] = line.strip().split("=", 1)[1].strip('"')
                    elif line.startswith("\t\tbirth="):
                        chars[cur_cid]["birth"] = line.strip().split("=", 1)[1]
                    elif line.startswith("\t\tculture="):
                        chars[cur_cid]["culture"] = line.strip().split("=", 1)[1]
                    elif line.startswith("\t\trite="):
                        chars[cur_cid]["rite"] = line.strip().split("=", 1)[1]
                    elif line.startswith("\t\tdynasty_house="):
                        chars[cur_cid]["dynasty_house"] = line.strip().split("=", 1)[1]
                    elif line.startswith("\t\t\tdate=") and sec == "dead_unprunable":
                        if chars[cur_cid]["death"] is None:
                            chars[cur_cid]["death"] = line.strip().split("=", 1)[1]
                    elif line.startswith("\t\ttraits={"):
                        tr_str = line.strip().split("=", 1)[1].strip("{ }")
                        if tr_str:
                            chars[cur_cid]["traits"].extend(int(x) for x in tr_str.split() if x.isdigit())
                        if not line.strip().endswith("}"):
                            in_traits = True
                    elif in_traits:
                        if "}" in line:
                            in_traits = False
                        tr_str = line.strip().strip("{ }")
                        if tr_str:
                            chars[cur_cid]["traits"].extend(int(x) for x in tr_str.split() if x.isdigit())
                    elif line.startswith("\t\talive_data={"):
                        in_alive = True
                    elif in_alive:
                        if line.startswith("\t\t}"):
                            in_alive = False
                            in_piety = False
                            in_prestige = False
                        elif line.startswith("\t\t\tpiety={"):
                            in_piety = True
                        elif in_piety:
                            if line.startswith("\t\t\t}"):
                                in_piety = False
                            elif line.startswith("\t\t\t\taccumulated="):
                                try:
                                    chars[cur_cid]["piety"] = round(float(line.strip().split("=", 1)[1]), 1)
                                except ValueError:
                                    pass
                        elif line.startswith("\t\t\tprestige={"):
                            in_prestige = True
                        elif in_prestige:
                            if line.startswith("\t\t\t}"):
                                in_prestige = False
                            elif line.startswith("\t\t\t\taccumulated="):
                                try:
                                    chars[cur_cid]["prestige"] = round(float(line.strip().split("=", 1)[1]), 1)
                                except ValueError:
                                    pass
            elif sec == "characters":
                if line.startswith("\t\t") and not line.startswith("\t\t\t") and "={" in line:
                    cid = line.strip().split("=", 1)[0]
                    cur_cid = cid if cid in needed_chars else None
                    if cur_cid and cur_cid not in chars:
                        chars[cur_cid] = {
                            "id": int(cur_cid) if cur_cid.isdigit() else cur_cid,
                            "alive": False,
                            "first_name": "",
                            "nickname": "",
                            "birth": None,
                            "death": None,
                            "culture": None,
                            "rite": None,
                            "dynasty_house": None,
                            "traits": [],
                            "piety": 0.0,
                            "prestige": 0.0,
                        }
                    in_traits = False
                elif cur_cid:
                    if line.startswith("\t\t}"):
                        cur_cid = None
                    elif line.startswith("\t\t\tfirst_name="):
                        chars[cur_cid]["first_name"] = line.strip().split("=", 1)[1].strip('"')
                    elif line.startswith("\t\t\tnickname_text="):
                        chars[cur_cid]["nickname"] = line.strip().split("=", 1)[1].strip('"')
                    elif line.startswith("\t\t\tbirth="):
                        chars[cur_cid]["birth"] = line.strip().split("=", 1)[1]
                    elif line.startswith("\t\t\tculture="):
                        chars[cur_cid]["culture"] = line.strip().split("=", 1)[1]
                    elif line.startswith("\t\t\trite="):
                        chars[cur_cid]["rite"] = line.strip().split("=", 1)[1]
                    elif line.startswith("\t\t\tdynasty_house="):
                        chars[cur_cid]["dynasty_house"] = line.strip().split("=", 1)[1]
                    elif line.startswith("\t\t\t\tdate="):
                        if chars[cur_cid]["death"] is None:
                            chars[cur_cid]["death"] = line.strip().split("=", 1)[1]
                    elif line.startswith("\t\t\ttraits={"):
                        tr_str = line.strip().split("=", 1)[1].strip("{ }")
                        if tr_str:
                            chars[cur_cid]["traits"].extend(int(x) for x in tr_str.split() if x.isdigit())
                        if not line.strip().endswith("}"):
                            in_traits = True
                    elif in_traits:
                        if "}" in line:
                            in_traits = False
                        tr_str = line.strip().strip("{ }")
                        if tr_str:
                            chars[cur_cid]["traits"].extend(int(x) for x in tr_str.split() if x.isdigit())

    # Decode traits
    for cdata in chars.values():
        decoded = []
        for tid in cdata["traits"]:
            if 0 <= tid < len(traits_lookup):
                decoded.append(traits_lookup[tid])
        cdata["traits_decoded"] = decoded

    print(f"  Pass 2 finished in {time.time() - t1:.2f}s: resolved {len(chars)} characters.")

    return {
        "meta_date": meta_date,
        "provinces": provinces,
        "baronies_save": baronies_save,
        "title_id_to_key": title_id_to_key,
        "religions": religions,
        "faiths": faiths,
        "holy_orders": holy_orders,
        "title_to_holy_order": title_to_holy_order,
        "epidemics_by_prov": epidemics_by_prov,
        "county_plague_mod": county_plague_mod,
        "chars": chars,
    }


def main():
    parser = argparse.ArgumentParser(description="Extract Section 4.A datasets from melted_save.ck3.")
    parser.add_argument("--save", type=Path, default=SAVE_PATH)
    args = parser.parse_args()

    # Load existing companion datasets
    with open(DATA_DIR / "barony_toponymic_profiles.json", "r", encoding="utf-8") as f:
        topo_profiles = json.load(f)
    with open(DATA_DIR / "ck3_baronies.geojson", "r", encoding="utf-8") as f:
        baronies_geo = json.load(f)
    with open(DATA_DIR / "saint_holding_imagery.json", "r", encoding="utf-8") as f:
        saint_imagery = json.load(f)
    with open(PHASE1_DIR / "titles_data.json", "r", encoding="utf-8") as f:
        titles_data = json.load(f)
    with open(PHASE1_DIR / "cultures_data.json", "r", encoding="utf-8") as f:
        cultures_data = json.load(f)
    with open(PHASE1_DIR / "dynasties_and_houses.json", "r", encoding="utf-8") as f:
        dh_data = json.load(f)
    houses_data = dh_data.get("houses", {})

    cult_by_id = {str(k): v for k, v in cultures_data.items()}
    cult_lang_by_name = {v["name"]: v["language"] for v in cultures_data.values()}

    b_to_pid = {}
    b_to_county = {}
    for feat in baronies_geo["features"]:
        p = feat["properties"]
        b_to_pid[p["barony"]] = str(p["id"])
        b_to_county[p["barony"]] = p["county"]

    # Collect all character IDs from county histories so Pass 2 gets them all
    extra_char_ids = set()
    for t_obj in titles_data.values():
        ch = t_obj.get("current_holder", {})
        if ch.get("id"):
            extra_char_ids.add(str(ch["id"]))
        for h in t_obj.get("history", []):
            if h.get("holder_id"):
                extra_char_ids.add(str(h["holder_id"]))

    save = parse_save_context_and_chars(args.save, extra_char_ids)
    meta_date = save["meta_date"]
    provinces = save["provinces"]
    baronies_save = save["baronies_save"]
    religions = save["religions"]
    faiths = save["faiths"]
    title_to_holy_order = save["title_to_holy_order"]
    epidemics_by_prov = save["epidemics_by_prov"]
    county_plague_mod = save["county_plague_mod"]
    chars = save["chars"]

    # ------------------------------------------------------------------
    # 1. Reconcile data/barony_holdings.json
    # ------------------------------------------------------------------
    reconciled_holdings = {}
    for bk in sorted(b_to_pid.keys()):
        pid = b_to_pid[bk]
        raw_ht = provinces.get(pid, {}).get("raw_holding_type")
        reconciled_holdings[bk] = map_holding_type_from_raw(raw_ht)

    bh_path = DATA_DIR / "barony_holdings.json"
    with open(bh_path, "w", encoding="utf-8") as f:
        json.dump(reconciled_holdings, f, ensure_ascii=False, separators=(",", ":"))
    bh_counts = Counter(reconciled_holdings.values())
    print(f"Reconciled {bh_path}: {dict(bh_counts)}")

    # ------------------------------------------------------------------
    # 2. Build data/barony_physical_and_event_context.json
    # ------------------------------------------------------------------
    faith_saints = {}
    for fid, fobj in faiths.items():
        if fobj.get("saints"):
            rid = str(fobj.get("religion", ""))
            robj = religions.get(rid, {})
            s_list = []
            for sid in fobj["saints"]:
                sc = chars.get(str(sid), {})
                sc_cid = str(sc.get("culture", "")) if sc.get("culture") is not None else ""
                sc_cult = cult_by_id.get(sc_cid, {}).get("name")
                s_list.append({
                    "char_id": int(sid) if sid.isdigit() else sid,
                    "raw_name": sc.get("first_name", ""),
                    "clean_name": clean_ck3_name(sc.get("first_name", ""), culture=sc_cult),
                    "birth": sc.get("birth"),
                    "death": sc.get("death"),
                    "culture": sc_cult,
                })
            faith_saints[fid] = {
                "faith_type": fobj.get("faith_type"),
                "religion_type": robj.get("religion_type"),
                "saints": s_list,
            }

    physical_context = {}
    bldg_family_counts = Counter()
    special_count = 0
    great_count = 0
    ho_lease_count = 0
    tradeport_count = 0
    saint_shrine_count = 0
    battle_poi_count = 0

    for bk, prof in topo_profiles["baronies"].items():
        pid = b_to_pid[bk]
        ck = b_to_county[bk]
        prov = provinces.get(pid, {})
        bsave = baronies_save.get(bk, {})
        tid = bsave.get("title_id")

        bldgs = prov.get("buildings", [])
        families = []
        max_tier = 0
        for b in bldgs:
            m = re.match(r"^(.+)_(\d+)$", b)
            if m:
                fam, tier_s = m.group(1), int(m.group(2))
                if fam not in families:
                    families.append(fam)
                if fam in ("castle", "city", "temple", "tribal") and tier_s > max_tier:
                    max_tier = tier_s
            else:
                if b not in families:
                    families.append(b)
        for fam in families:
            bldg_family_counts[fam] += 1

        # Note: CK3 common_tradeport is buildable on sea coasts, navigable rivers, and lakes (not coastal-only)
        has_tradeport = "common_tradeport" in families
        if has_tradeport:
            tradeport_count += 1

        sp_b = prov.get("special_building_type")
        gr_b = prov.get("great_building_type")
        if sp_b:
            special_count += 1
        if gr_b:
            great_count += 1

        ho = title_to_holy_order.get(tid) if tid else None
        ho_info = None
        if ho:
            ho_lease_count += 1
            f_id = ho.get("founder")
            f_ch = chars.get(str(f_id), {}) if f_id else {}
            ho_info = {
                "order_id": ho.get("order_id"),
                "holy_order_type": ho.get("holy_order_type"),
                "rite": ho.get("rite"),
                "founder_id": int(f_id) if f_id and f_id.isdigit() else f_id,
                "founder_name": clean_ck3_name(f_ch.get("first_name", "")),
            }

        leases = bsave.get("leases", [])
        lease_dates = [l["date"] for l in leases if l.get("date")]
        earliest_lease = min(lease_dates, key=parse_date_tuple) if lease_dates else None

        s_img = saint_imagery.get(bk)
        saint_info = None
        if s_img:
            saint_shrine_count += 1
            saint_info = {
                "saint_name": s_img.get("saint_name"),
                "shrine_type": s_img.get("shrine_type"),
                "relic_description": s_img.get("relic_description"),
            }

        pois = prov.get("points_of_interest", [])
        if any("battle" in p for p in pois):
            battle_poi_count += 1

        physical_context[bk] = {
            "province_id": int(pid) if pid.isdigit() else pid,
            "county_key": ck,
            "raw_holding_type": prov.get("raw_holding_type"),
            "holding_type": prof["ht"],
            "is_capital_barony": bsave.get("capital_barony", False),
            "holding_tier": max_tier,
            "fort_level": prov.get("fort_level", 0),
            "income": prov.get("income", 0.0),
            "buildings": bldgs,
            "building_families": families,
            "has_tradeport": has_tradeport,
            "special_building_type": sp_b,
            "great_building_type": gr_b,
            "duchy_capital_building": prov.get("duchy_capital_building"),
            "points_of_interest": pois,
            "holy_order_lease": ho_info,
            "earliest_lease_date": earliest_lease,
            "lease_history_count": len(leases),
            "saint_shrine": saint_info,
            "active_epidemics": epidemics_by_prov.get(pid, []),
            "county_shattered_by_plague": ck in county_plague_mod,
        }

    ctx_payload = {
        "metadata": {
            "schema_version": "1.0.0",
            "save_date": meta_date,
            "total_occupied_baronies": len(physical_context),
            "tradeport_holdings": tradeport_count,
            "special_building_holdings": special_count,
            "great_building_holdings": great_count,
            "holy_order_leased_holdings": ho_lease_count,
            "saint_shrine_holdings": saint_shrine_count,
            "battle_poi_holdings": battle_poi_count,
            "top_building_families": dict(bldg_family_counts.most_common(25)),
        },
        "faith_saints": faith_saints,
        "baronies": physical_context,
    }

    ctx_path = DATA_DIR / "barony_physical_and_event_context.json"
    with open(ctx_path, "w", encoding="utf-8") as f:
        json.dump(ctx_payload, f, ensure_ascii=False, separators=(",", ":"))
    print(f"Wrote {ctx_path} ({ctx_path.stat().st_size / (1024*1024):.2f} MB)")

    # ------------------------------------------------------------------
    # 3. Build data/barony_coinage_rulers.json
    # ------------------------------------------------------------------
    # Precompute county tenure intervals from 867.1.1 to 1194.7.28
    county_tenures = {}
    for ck, t_obj in titles_data.items():
        hist = t_obj.get("history", [])
        h867 = None
        for h in hist:
            if parse_date_tuple(h.get("date", "")) <= (867, 1, 1):
                h867 = h
            else:
                break
        if not h867 and hist:
            h867 = hist[0]

        ivs = []
        cur_start = "867.1.1"
        cur_hid = str(h867.get("holder_id")) if h867 and h867.get("holder_id") else None
        cur_cult = h867.get("culture_name", "Unknown") if h867 else "Unknown"
        cur_type = h867.get("type", "holder") if h867 else "holder"
        for h in hist:
            dt = parse_date_tuple(h.get("date", ""))
            if dt <= (867, 1, 1):
                continue
            ivs.append({
                "start": cur_start,
                "end": h["date"],
                "years": round(years_between(cur_start, h["date"]), 2),
                "holder_id": cur_hid,
                "culture": cur_cult,
                "language": cult_lang_by_name.get(cur_cult, cur_cult),
                "type": cur_type,
            })
            cur_start = h["date"]
            cur_hid = str(h.get("holder_id")) if h.get("holder_id") else cur_hid
            cur_cult = h.get("culture_name", cur_cult)
            cur_type = h.get("type", "holder")
        ivs.append({
            "start": cur_start,
            "end": meta_date,
            "years": round(years_between(cur_start, meta_date), 2),
            "holder_id": cur_hid,
            "culture": cur_cult,
            "language": cult_lang_by_name.get(cur_cult, cur_cult),
            "type": cur_type,
        })
        county_tenures[ck] = ivs

    def score_ruler_for_coinage(iv, prefer_culture: str, prefer_builder: bool) -> tuple:
        ch = chars.get(str(iv["holder_id"]), {}) if iv["holder_id"] else {}
        tset = set(ch.get("traits_decoded") or [])
        exact_c = 1 if iv["culture"] == prefer_culture else 0
        builder_pts = 0
        if prefer_builder:
            if tset & {"architect", "education_stewardship_4", "education_stewardship_3", "diligent", "administrator"}:
                builder_pts += 2
            if tset & MARTIAL_TRAITS:
                builder_pts += 1
        return (exact_c, builder_pts, iv["years"])

    coinage_rulers = {}
    archetype_counts = Counter()
    mode_counts = Counter()
    unresolved_count = 0

    for bk, prof in topo_profiles["baronies"].items():
        ck = prof["ck"]
        coin_c = prof["c"]
        coin_lang = cult_lang_by_name.get(coin_c, coin_c)
        crule = prof["cr"]
        horizon = prof["hd"]
        horizon_t = parse_date_tuple(horizon)
        ivs = county_tenures.get(ck, [])
        ctx = physical_context[bk]
        bsave = baronies_save.get(bk, {})

        chosen_iv = None
        attribution_mode = "coinage_sovereign"

        if crule == "founded_current_baron":
            bhid = bsave.get("holder")
            chosen_iv = {
                "start": bsave.get("date") or horizon,
                "end": meta_date,
                "years": round(years_between(bsave.get("date") or horizon, meta_date), 2),
                "holder_id": bhid,
                "culture": coin_c,
                "type": "baron_incumbent",
            }
            attribution_mode = "direct_baron_founder"

        elif crule == "founded_post_conquest_tarraconian":
            # Look inside [horizon, meta_date]
            post_ivs = [iv for iv in ivs if parse_date_tuple(iv["end"]) > horizon_t]
            cand = [iv for iv in post_ivs if iv["culture"] in IMPERIAL_CULTURES or iv["language"] == coin_lang]
            if not cand:
                cand = post_ivs
            if cand:
                chosen_iv = max(cand, key=lambda iv: score_ruler_for_coinage(iv, coin_c, prefer_builder=True))
            attribution_mode = "post_conquest_imperial_founder"

        elif crule in ("founded_pre_conquest_50y", "founded_dominant_window"):
            pre_ivs = [iv for iv in ivs if parse_date_tuple(iv["start"]) < horizon_t]
            upper_d = ctx.get("earliest_lease_date") or horizon
            upper_t = parse_date_tuple(upper_d)
            cand = [iv for iv in pre_ivs if parse_date_tuple(iv["start"]) < upper_t and iv["language"] == coin_lang]
            if not cand:
                cand = [iv for iv in pre_ivs if iv["culture"] == coin_c]
            if cand:
                chosen_iv = max(cand, key=lambda iv: score_ruler_for_coinage(iv, coin_c, prefer_builder=True))
            attribution_mode = "pre_conquest_founder"

        elif crule in ("native_feudalization", "colonial_feudalization", "founded_feudalizer_fallback"):
            # Match earliest tenure matching coin_c / coin_lang that starts the feudalization window
            cand = [iv for iv in ivs if iv["culture"] == coin_c]
            if not cand:
                cand = [iv for iv in ivs if iv["language"] == coin_lang]
            if cand:
                # Prefer first non-blip (>=5y) feudalizer, else longest
                non_blip = [iv for iv in cand if iv["years"] >= 5.0]
                chosen_iv = non_blip[0] if non_blip else cand[0]
            attribution_mode = "feudalizer_sovereign"

        elif crule in (
            "castle_overrule_100y", "castle_overrule_50y",
            "temple_faith_change_25y", "temple_long_rule",
            "sinosphere_civic_25y", "city_overrule_150y",
            "demographic_replacement_50y", "unfeudalized_50y_streak",
        ):
            pre_ivs = [iv for iv in ivs if parse_date_tuple(iv["start"]) < horizon_t]
            cand = [iv for iv in pre_ivs if iv["language"] == coin_lang]
            if cand:
                # Take the latest qualifying stretch's conqueror/longest ruler
                chosen_iv = max(cand, key=lambda iv: score_ruler_for_coinage(iv, coin_c, prefer_builder=False))
            attribution_mode = "overruling_sovereign"

        else:
            # pre_867_substrate_inertia, city_substrate_inertia, unfeudalized_substrate
            pre_ivs = [iv for iv in ivs if parse_date_tuple(iv["start"]) < horizon_t]
            cand = [iv for iv in pre_ivs if iv["language"] == coin_lang]
            if cand:
                chosen_iv = cand[0]  # 867 baseline ruler
            elif pre_ivs:
                chosen_iv = pre_ivs[0]
            attribution_mode = "substrate_retained"

        # Fallback if still None
        if not chosen_iv and ivs:
            chosen_iv = ivs[0]

        hid = chosen_iv["holder_id"] if chosen_iv else None
        ch = chars.get(str(hid), {}) if hid else {}
        if not ch:
            unresolved_count += 1

        raw_fname = ch.get("first_name", "")
        ruler_c = cult_by_id.get(str(ch.get("culture", "")), {}).get("name") or (chosen_iv["culture"] if chosen_iv else None)
        clean_fname = clean_ck3_name(raw_fname, culture=ruler_c or coin_c)
        house_id = ch.get("dynasty_house")
        h_obj = houses_data.get(str(house_id), {}) if house_id else {}
        house_name = h_obj.get("localized_name") or (h_obj.get("name", "").replace("dynn_", ""))
        dyn_id = h_obj.get("dynasty")
        is_chat = (dyn_id == 1582)
        circ_house = is_circular_house(house_name, bk, ck)

        fid = str(ch.get("rite")) if ch.get("rite") is not None else None
        fobj = faiths.get(fid, {}) if fid else {}
        robj = religions.get(str(fobj.get("religion", "")), {}) if fobj else {}

        t_decoded = ch.get("traits_decoded", [])
        piety = ch.get("piety", 0.0)
        prestige = ch.get("prestige", 0.0)
        archetype, signals = classify_archetype(t_decoded, piety, prestige, prof["ht"], ctx)

        archetype_counts[archetype] += 1
        mode_counts[attribution_mode] += 1

        coinage_rulers[bk] = {
            "holder_id": int(hid) if hid and str(hid).isdigit() else hid,
            "raw_first_name": raw_fname,
            "clean_first_name": clean_fname,
            "nickname": ch.get("nickname", ""),
            "birth": ch.get("birth"),
            "death": ch.get("death"),
            "coinage_culture": coin_c,
            "ruler_culture": cult_by_id.get(str(ch.get("culture", "")), {}).get("name") or (chosen_iv["culture"] if chosen_iv else None),
            "faith_id": int(fid) if fid and fid.isdigit() else fid,
            "faith_type": fobj.get("faith_type"),
            "religion_type": robj.get("religion_type"),
            "dynasty_house_id": int(house_id) if house_id and str(house_id).isdigit() else house_id,
            "house_name": house_name,
            "dynasty_id": dyn_id,
            "is_chatenois": is_chat,
            "is_circular_house": circ_house,
            "traits": t_decoded,
            "piety": piety,
            "prestige": prestige,
            "tenure_start": chosen_iv["start"] if chosen_iv else None,
            "tenure_end": chosen_iv["end"] if chosen_iv else None,
            "tenure_years": chosen_iv["years"] if chosen_iv else 0.0,
            "attribution_mode": attribution_mode,
            "coinage_rule": crule,
            "archetype": archetype,
            "archetype_signals": signals,
        }

    rulers_payload = {
        "metadata": {
            "schema_version": "1.0.0",
            "save_date": meta_date,
            "total_occupied_baronies": len(coinage_rulers),
            "unresolved_characters": unresolved_count,
            "attribution_mode_counts": dict(mode_counts),
            "archetype_counts": dict(archetype_counts),
        },
        "baronies": coinage_rulers,
    }

    rulers_path = DATA_DIR / "barony_coinage_rulers.json"
    with open(rulers_path, "w", encoding="utf-8") as f:
        json.dump(rulers_payload, f, ensure_ascii=False, separators=(",", ":"))
    print(f"Wrote {rulers_path} ({rulers_path.stat().st_size / (1024*1024):.2f} MB)")
    print("Attribution modes:", dict(mode_counts))
    print("Archetypes:", dict(archetype_counts))
    print("Unresolved characters:", unresolved_count)

    print("\nSample coinage rulers:")
    for sb in ["b_london", "b_woxbrigge", "b_szekesfehervar", "b_kalocsa", "b_kiev", "b_vyshgorod", "b_roma", "b_baranovichi", "b_lorient", "b_reykjavik", "b_vestfirdir"]:
        if sb in coinage_rulers:
            r = coinage_rulers[sb]
            c = physical_context[sb]
            print(f"  {sb:16s} | {r['attribution_mode']:28s} | {r['clean_first_name']} ({r['house_name']}) [{r['ruler_culture']}] | {r['archetype']} {r['archetype_signals']} | bldgs={c['building_families'][:4]}")


if __name__ == "__main__":
    main()

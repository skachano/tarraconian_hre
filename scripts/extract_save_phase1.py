#!/usr/bin/env python3
"""
Crusader Kings III Save Game & Title Hierarchy Extractor (Phase 1)
------------------------------------------------------------------
Part of the Historical Title Audit & Progression Pipeline for Tarraconian HRE.

Parses:
  1. Vanilla game title hierarchy (00_landed_titles.txt)
  2. Melted or raw binary CK3 save game (chatenois_867_01_01.ck3)
Extracts:
  - Landed title status, holders, history, and constituent baronies
  - County manager parameters (culture, faith, development, control)
  - Province holdings and buildings
  - Dynasties, cadet houses, and living member counts
  - Culture metadata (name, heritage, language, ethos, parents)
  - Historical characters and decoded personality traits (Option C engine)
  - In-depth Chatenois dynasty (ID 1582) analysis and Tarraconian/Germanic name adaptation (Kestenholz)

Writes all results to the designated output folder (defaults to /tmp/ck3_audit_phase1).
"""

import argparse
import csv
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path


def log(msg: str):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


def parse_landed_titles(filepath: Path):
    """
    Parses 00_landed_titles.txt to extract the canonical de jure hierarchy
    and mapping of baronies to province IDs.
    """
    log(f"Parsing vanilla landed titles from: {filepath}")
    titles = {}  # title_key -> {'tier': str, 'parent': str, 'province': int or None}
    stack = []
    depth = 0

    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = re.sub(r'#.*', '', line).strip()
            if not line:
                continue

            # Check province ID assignment for baronies
            m_prov = re.search(r'\bprovince\s*=\s*(\d+)', line)
            if m_prov and stack:
                cur_key = stack[-1][0]
                if cur_key in titles:
                    titles[cur_key]['province'] = int(m_prov.group(1))

            tokens = re.findall(r'[a-zA-Z0-9_@]+|[{}]', line)
            for i, t in enumerate(tokens):
                if t == '{':
                    depth += 1
                    if i > 0 and tokens[i - 1].startswith(('e_', 'k_', 'd_', 'c_', 'b_')):
                        title_key = tokens[i - 1]
                        parent = None
                        for ancestor, _ in reversed(stack):
                            if ancestor:
                                parent = ancestor
                                break
                        stack.append((title_key, depth))
                        titles[title_key] = {
                            'tier': title_key[0],
                            'parent': parent,
                            'province': None
                        }
                    else:
                        stack.append((None, depth))
                elif t == '}':
                    while stack and stack[-1][1] == depth:
                        stack.pop()
                    depth -= 1

    # Build de jure ancestor mapping and county -> baronies mapping
    county_to_baronies = {}
    county_de_jure = {}
    barony_to_province = {}

    for key, data in titles.items():
        tier = data['tier']
        if tier == 'b':
            if data['province'] is not None:
                barony_to_province[key] = data['province']
            parent = data['parent']
            if parent and parent.startswith('c_'):
                county_to_baronies.setdefault(parent, []).append(key)
        elif tier == 'c':
            parent_d = data['parent']
            parent_k = titles.get(parent_d, {}).get('parent') if parent_d else None
            parent_e = titles.get(parent_k, {}).get('parent') if parent_k else None
            county_de_jure[key] = {
                'duchy': parent_d,
                'kingdom': parent_k,
                'empire': parent_e
            }

    log(f"Parsed {len(titles)} vanilla titles ({len(county_de_jure)} counties, {len(barony_to_province)} baronies)")
    return {
        'all_titles': titles,
        'county_to_baronies': county_to_baronies,
        'county_de_jure': county_de_jure,
        'barony_to_province': barony_to_province
    }


def ensure_melted_save(save_path: Path, melted_path: Path, rakaly_bin: Path) -> Path:
    """
    Ensures that a plaintext (melted) version of the save exists.
    If melted_path already exists and is non-empty, reuses it.
    Otherwise invokes rakaly melt.
    """
    if melted_path.is_file() and melted_path.stat().st_size > 1024 * 1024:
        log(f"Found existing melted save: {melted_path} ({melted_path.stat().st_size / 1024 / 1024:.1f} MB)")
        return melted_path

    if not save_path.is_file():
        raise FileNotFoundError(f"Save file not found at: {save_path}")

    log(f"Melting save game {save_path} -> {melted_path} using {rakaly_bin}...")
    cmd = [str(rakaly_bin), "melt", str(save_path), "-u", "stringify", "-o", str(melted_path)]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"Rakaly melt failed: {res.stderr}")

    log(f"Melt successful! File size: {melted_path.stat().st_size / 1024 / 1024:.1f} MB")
    return melted_path


def parse_melted_save(melted_path: Path, landed_info: dict):
    """
    Streaming two-pass parser for melted CK3 save file.
    Pass 1: traits_lookup, county_manager, provinces, landed_titles, dynasties/houses, cultures.
    Pass 2: living and dead_unprunable characters referenced by titles and houses.
    """
    log("Starting Pass 1: Parsing metadata, provinces, titles, dynasties, and cultures...")

    traits_lookup = []
    county_mgr = {}  # c_* -> {culture, rite, development, county_control}
    provinces = {}   # prov_id -> {holding_type, buildings, fort_level}
    titles_by_id = {}
    titles_by_key = {}
    houses = {}
    dynasties = {}
    cultures = {}

    referenced_char_ids = set()

    # Pass 1 state variables
    in_provinces = False
    in_prov_block = False
    in_holding = False
    in_buildings = False
    cur_pid = None

    in_titles = False
    in_title_block = False
    in_history = False
    in_name_data = False
    in_vassals = False
    cur_tid = None
    cur_hist_entry = None

    in_dyn_block = False
    dyn_sub_block = None
    cur_hid = None
    cur_did = None

    in_cult_mgr = False
    in_cults = False
    cur_cid = None

    in_county_mgr = False
    cur_cm_county = None

    t0 = time.time()

    with open(melted_path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            # 1. traits_lookup
            if line.startswith('\teducation_intrigue_1'):
                traits_lookup = line.strip().split()
                continue

            # 2. county_manager
            if line.startswith('county_manager={'):
                in_county_mgr = True
                continue
            elif in_county_mgr:
                if line.startswith('}'):
                    in_county_mgr = False
                    cur_cm_county = None
                elif line.startswith('\t\tc_'):
                    cur_cm_county = line.strip().split('=')[0]
                    county_mgr[cur_cm_county] = {}
                elif cur_cm_county and line.startswith('\t\t\t') and not line.startswith('\t\t\t\t'):
                    parts = line.strip().split('=', 1)
                    if len(parts) == 2:
                        k, v = parts[0].strip(), parts[1].strip()
                        if k in ('culture', 'rite', 'development', 'county_control'):
                            try:
                                county_mgr[cur_cm_county][k] = float(v) if '.' in v else int(v)
                            except ValueError:
                                county_mgr[cur_cm_county][k] = v
                continue

            # 3. provinces
            if line.startswith('provinces={'):
                in_provinces = True
                continue
            elif in_provinces:
                if line.startswith('}'):
                    in_provinces = False
                    in_prov_block = False
                    cur_pid = None
                elif line.startswith('\t') and not line.startswith('\t\t') and '={' in line:
                    parts = line.strip().split('=')
                    try:
                        cur_pid = int(parts[0].strip())
                        provinces[cur_pid] = {
                            'id': cur_pid,
                            'holding_type': None,
                            'buildings': [],
                            'fort_level': 0
                        }
                        in_prov_block = True
                        in_holding = False
                        in_buildings = False
                    except ValueError:
                        cur_pid = None
                        in_prov_block = False
                elif in_prov_block and cur_pid is not None:
                    if line.startswith('\t}'):
                        in_prov_block = False
                        cur_pid = None
                        continue
                    if line.startswith('\t\tholding={'):
                        in_holding = True
                        continue
                    elif in_holding:
                        if line.startswith('\t\t}'):
                            in_holding = False
                        elif line.startswith('\t\t\ttype='):
                            provinces[cur_pid]['holding_type'] = line.strip().split('=', 1)[1].strip().strip('\"')
                        elif line.startswith('\t\t\tbuildings={'):
                            in_buildings = True
                        elif in_buildings:
                            if line.startswith('\t\t\t}'):
                                in_buildings = False
                            elif line.startswith('\t\t\t\t\ttype='):
                                b_type = line.strip().split('=', 1)[1].strip().strip('\"')
                                provinces[cur_pid]['buildings'].append(b_type)
                        continue
                    if line.startswith('\t\tfort_level='):
                        fl = line.strip().split('=', 1)[1].strip()
                        try:
                            provinces[cur_pid]['fort_level'] = int(fl)
                        except ValueError:
                            pass
                continue

            # 4. landed_titles
            if line.startswith('landed_titles={'):
                in_titles = True
                continue
            elif in_titles:
                if line.startswith('}'):
                    in_titles = False
                    in_title_block = False
                    cur_tid = None
                elif line.startswith('\t\t') and not line.startswith('\t\t\t') and '={' in line:
                    parts = line.strip().split('=')
                    try:
                        cur_tid = int(parts[0].strip())
                        titles_by_id[cur_tid] = {
                            'id': cur_tid,
                            'history': [],
                            'de_jure_vassals': []
                        }
                        in_title_block = True
                        in_history = False
                        in_name_data = False
                        in_vassals = False
                        cur_hist_entry = None
                    except ValueError:
                        cur_tid = None
                        in_title_block = False
                elif in_title_block and cur_tid is not None:
                    if line.startswith('\t\t}'):
                        in_title_block = False
                        cur_tid = None
                        continue

                    if line.startswith('\t\t\tde_jure_vassals={'):
                        in_vassals = True
                        v_str = line.strip().split('=', 1)[1].strip('{ }')
                        if v_str:
                            titles_by_id[cur_tid]['de_jure_vassals'].extend(
                                [int(x) for x in v_str.split() if x.isdigit()]
                            )
                        continue
                    elif in_vassals:
                        if line.startswith('\t\t\t}'):
                            in_vassals = False
                        else:
                            titles_by_id[cur_tid]['de_jure_vassals'].extend(
                                [int(x) for x in line.strip().split() if x.isdigit()]
                            )
                        continue

                    if line.startswith('\t\t\thistory={'):
                        in_history = True
                        continue
                    elif in_history:
                        if line.startswith('\t\t\t}'):
                            in_history = False
                            cur_hist_entry = None
                        elif line.startswith('\t\t\t\t') and not line.startswith('\t\t\t\t\t') and '=' in line:
                            p = line.strip().split('=', 1)
                            date_str = p[0].strip()
                            val = p[1].strip()
                            if val == '{':
                                cur_hist_entry = {'date': date_str, 'holder': None, 'type': 'holder'}
                                titles_by_id[cur_tid]['history'].append(cur_hist_entry)
                            elif val.isdigit():
                                cur_hist_entry = {'date': date_str, 'holder': int(val), 'type': 'holder'}
                                titles_by_id[cur_tid]['history'].append(cur_hist_entry)
                                referenced_char_ids.add(int(val))
                        elif cur_hist_entry is not None:
                            if line.startswith('\t\t\t\t\tholder='):
                                h_id = line.strip().split('=')[1].strip()
                                if h_id.isdigit():
                                    cur_hist_entry['holder'] = int(h_id)
                                    referenced_char_ids.add(int(h_id))
                            elif line.startswith('\t\t\t\t\ttype='):
                                cur_hist_entry['type'] = line.strip().split('=')[1].strip().strip('\"')
                        continue

                    if line.startswith('\t\t\ttitle_name_data={'):
                        in_name_data = True
                        continue
                    elif in_name_data:
                        if line.startswith('\t\t\t}'):
                            in_name_data = False
                        elif line.startswith('\t\t\t\t'):
                            p = line.strip().split('=', 1)
                            if len(p) == 2:
                                k, v = p[0].strip(), p[1].strip().strip('\"')
                                if k in ('name', 'adj', 'custom', 'localization_key'):
                                    titles_by_id[cur_tid][k] = v
                        continue

                    if line.startswith('\t\t\t') and not line.startswith('\t\t\t\t'):
                        p = line.strip().split('=', 1)
                        if len(p) == 2:
                            k, v = p[0].strip(), p[1].strip().strip('\"')
                            if k == 'key':
                                titles_by_id[cur_tid]['key'] = v
                                titles_by_key[v] = titles_by_id[cur_tid]
                            elif k in ('holder', 'de_facto_liege', 'de_jure_liege', 'capital'):
                                try:
                                    iv = int(v)
                                    titles_by_id[cur_tid][k] = iv
                                    if k == 'holder':
                                        referenced_char_ids.add(iv)
                                except ValueError:
                                    titles_by_id[cur_tid][k] = v
                continue

            # 5. dynasties
            if line.startswith('dynasties={'):
                in_dyn_block = True
                continue
            elif in_dyn_block:
                if line.startswith('}'):
                    in_dyn_block = False
                    dyn_sub_block = None
                elif line.startswith('\tdynasty_house={'):
                    dyn_sub_block = 'house'
                    continue
                elif line.startswith('\tdynasties={'):
                    dyn_sub_block = 'dynasty'
                    continue
                elif line.startswith('\t}'):
                    dyn_sub_block = None
                    continue

                if dyn_sub_block == 'house':
                    if line.startswith('\t\t') and not line.startswith('\t\t\t') and '={' in line:
                        parts = line.strip().split('=')
                        try:
                            cur_hid = int(parts[0].strip())
                            houses[cur_hid] = {
                                'house_id': cur_hid,
                                'historical': []
                            }
                        except ValueError:
                            cur_hid = None
                    elif cur_hid is not None and line.startswith('\t\t\t') and not line.startswith('\t\t\t\t'):
                        parts = line.strip().split('=', 1)
                        if len(parts) == 2:
                            k, v = parts[0].strip(), parts[1].strip().strip('\"')
                            if k in ('name', 'localized_name', 'prefix', 'found_date'):
                                houses[cur_hid][k] = v
                            elif k in ('dynasty', 'founder', 'head_of_house', 'parent_dynasty_house'):
                                try:
                                    iv = int(v)
                                    houses[cur_hid][k] = iv
                                    if k in ('founder', 'head_of_house'):
                                        referenced_char_ids.add(iv)
                                except ValueError:
                                    houses[cur_hid][k] = v
                elif dyn_sub_block == 'dynasty':
                    if line.startswith('\t\t') and not line.startswith('\t\t\t') and '={' in line:
                        parts = line.strip().split('=')
                        try:
                            cur_did = int(parts[0].strip())
                            dynasties[cur_did] = {'dynasty_id': cur_did}
                        except ValueError:
                            cur_did = None
                    elif cur_did is not None and line.startswith('\t\t\t') and not line.startswith('\t\t\t\t'):
                        parts = line.strip().split('=', 1)
                        if len(parts) == 2:
                            k, v = parts[0].strip(), parts[1].strip().strip('\"')
                            if k in ('name', 'key', 'culture'):
                                dynasties[cur_did][k] = v
                            elif k == 'coat_of_arms_id':
                                try:
                                    dynasties[cur_did][k] = int(v)
                                except ValueError:
                                    pass
                continue

            # 6. culture_manager
            if line.startswith('culture_manager={'):
                in_cult_mgr = True
                continue
            elif in_cult_mgr:
                if line.startswith('}'):
                    in_cult_mgr = False
                elif line.startswith('\tcultures={'):
                    in_cults = True
                    continue
                elif in_cults:
                    if line.startswith('\t}'):
                        in_cults = False
                        cur_cid = None
                    elif line.startswith('\t\t') and not line.startswith('\t\t\t'):
                        parts = line.strip().split('=')
                        if len(parts) == 2 and parts[1].strip() == '{':
                            try:
                                cur_cid = int(parts[0].strip())
                                cultures[cur_cid] = {
                                    'id': cur_cid,
                                    'parents': [],
                                    'traditions': []
                                }
                            except ValueError:
                                cur_cid = None
                    elif cur_cid is not None and line.startswith('\t\t\t') and not line.startswith('\t\t\t\t'):
                        parts = line.strip().split('=', 1)
                        if len(parts) == 2:
                            k, v = parts[0].strip(), parts[1].strip().strip('\"')
                            if k in ('culture_template', 'name', 'collective_noun', 'prefix',
                                    'ethos', 'heritage', 'language', 'created'):
                                cultures[cur_cid][k] = v
                            elif k == 'parents':
                                p_str = v.strip('{ }')
                                if p_str:
                                    cultures[cur_cid]['parents'] = [int(p) for p in p_str.split() if p.isdigit()]
                            elif k == 'traditions':
                                t_str = v.strip('{ }')
                                if t_str:
                                    cultures[cur_cid]['traditions'] = t_str.split()
                continue

    log(f"Pass 1 complete in {time.time() - t0:.2f}s:")
    log(f"  Traits lookup: {len(traits_lookup)}")
    log(f"  Counties in county_manager: {len(county_mgr)}")
    log(f"  Provinces: {len(provinces)}")
    log(f"  Titles in landed_titles: {len(titles_by_id)}")
    log(f"  Dynasty houses: {len(houses)}")
    log(f"  Dynasties: {len(dynasties)}")
    log(f"  Cultures: {len(cultures)}")
    log(f"  Referenced character IDs to resolve: {len(referenced_char_ids)}")

    # Pass 2: Extract referenced characters and count living members per house
    log("Starting Pass 2: Extracting characters and computing house living counts...")
    t1 = time.time()

    characters = {}
    house_living_counts = {}

    in_living = False
    in_dead = False
    cur_char_id = None
    cur_char_data = None
    in_traits_block = False

    with open(melted_path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            if line.startswith('living={'):
                in_living = True
                continue
            elif in_living:
                if line.startswith('}'):
                    in_living = False
                    cur_char_id = None
                    cur_char_data = None
                    continue

                if line.startswith('\t') and not line.startswith('\t\t') and '={' in line:
                    p = line.strip().split('=')[0]
                    try:
                        cid = int(p)
                        cur_char_id = cid
                        if cid in referenced_char_ids:
                            cur_char_data = {
                                'id': cid,
                                'alive': True,
                                'traits': [],
                                'piety': 0.0,
                                'prestige': 0.0
                            }
                            characters[cid] = cur_char_data
                        else:
                            cur_char_data = None
                    except ValueError:
                        cur_char_id = None
                        cur_char_data = None
                    continue

                if cur_char_id is not None:
                    if line.startswith('\t\tdynasty_house='):
                        try:
                            hid = int(line.strip().split('=', 1)[1])
                            house_living_counts[hid] = house_living_counts.get(hid, 0) + 1
                            if cur_char_data is not None:
                                cur_char_data['dynasty_house'] = hid
                        except ValueError:
                            pass
                    elif cur_char_data is not None:
                        if line.startswith('\t\tfirst_name='):
                            cur_char_data['first_name'] = line.strip().split('=', 1)[1].strip().strip('\"')
                        elif line.startswith('\t\tnickname_text='):
                            cur_char_data['nickname'] = line.strip().split('=', 1)[1].strip().strip('\"')
                        elif line.startswith('\t\tculture='):
                            try:
                                cur_char_data['culture'] = int(line.strip().split('=', 1)[1])
                            except ValueError:
                                pass
                        elif line.startswith('\t\tbirth='):
                            cur_char_data['birth'] = line.strip().split('=', 1)[1].strip()
                        elif line.startswith('\t\ttraits={'):
                            in_traits_block = True
                            tr_str = line.strip().split('=', 1)[1].strip('{ }')
                            if tr_str:
                                cur_char_data['traits'].extend([int(x) for x in tr_str.split() if x.isdigit()])
                            if line.strip().endswith('}'):
                                in_traits_block = False
                        elif in_traits_block:
                            if '}' in line:
                                in_traits_block = False
                            tr_str = line.strip().strip('{ }')
                            if tr_str:
                                cur_char_data['traits'].extend([int(x) for x in tr_str.split() if x.isdigit()])
                continue

            if line.startswith('dead_unprunable={'):
                in_dead = True
                continue
            elif in_dead:
                if line.startswith('}'):
                    in_dead = False
                    cur_char_id = None
                    cur_char_data = None
                    continue

                if line.startswith('\t') and not line.startswith('\t\t') and '={' in line:
                    p = line.strip().split('=')[0]
                    try:
                        cid = int(p)
                        cur_char_id = cid
                        if cid in referenced_char_ids and cid not in characters:
                            cur_char_data = {
                                'id': cid,
                                'alive': False,
                                'traits': [],
                                'piety': 0.0,
                                'prestige': 0.0
                            }
                            characters[cid] = cur_char_data
                        else:
                            cur_char_data = None
                    except ValueError:
                        cur_char_id = None
                        cur_char_data = None
                    continue

                if cur_char_data is not None:
                    if line.startswith('\t\tfirst_name='):
                        cur_char_data['first_name'] = line.strip().split('=', 1)[1].strip().strip('\"')
                    elif line.startswith('\t\tnickname_text='):
                        cur_char_data['nickname'] = line.strip().split('=', 1)[1].strip().strip('\"')
                    elif line.startswith('\t\tdynasty_house='):
                        try:
                            cur_char_data['dynasty_house'] = int(line.strip().split('=', 1)[1])
                        except ValueError:
                            pass
                    elif line.startswith('\t\tculture='):
                        try:
                            cur_char_data['culture'] = int(line.strip().split('=', 1)[1])
                        except ValueError:
                            pass
                    elif line.startswith('\t\tbirth='):
                        cur_char_data['birth'] = line.strip().split('=', 1)[1].strip()
                    elif line.startswith('\t\tdead_data={'):
                        pass
                    elif line.startswith('\t\t\tdate='):
                        cur_char_data['death'] = line.strip().split('=', 1)[1].strip()
                    elif line.startswith('\t\ttraits={'):
                        in_traits_block = True
                        tr_str = line.strip().split('=', 1)[1].strip('{ }')
                        if tr_str:
                            cur_char_data['traits'].extend([int(x) for x in tr_str.split() if x.isdigit()])
                        if line.strip().endswith('}'):
                            in_traits_block = False
                    elif in_traits_block:
                        if '}' in line:
                            in_traits_block = False
                        tr_str = line.strip().strip('{ }')
                        if tr_str:
                            cur_char_data['traits'].extend([int(x) for x in tr_str.split() if x.isdigit()])
                continue

    # Decode character traits from numeric IDs to strings using traits_lookup
    for cid, cdata in characters.items():
        decoded = []
        for tid in cdata.get('traits', []):
            if 0 <= tid < len(traits_lookup):
                decoded.append(traits_lookup[tid])
            else:
                decoded.append(f"trait_{tid}")
        cdata['traits_decoded'] = decoded

    # Assign living members counts to houses
    for hid, hdata in houses.items():
        hdata['living_members_count'] = house_living_counts.get(hid, 0)

    log(f"Pass 2 complete in {time.time() - t1:.2f}s:")
    log(f"  Extracted historical characters: {len(characters)}")

    return {
        'traits_lookup': traits_lookup,
        'county_mgr': county_mgr,
        'provinces': provinces,
        'titles_by_id': titles_by_id,
        'titles_by_key': titles_by_key,
        'houses': houses,
        'dynasties': dynasties,
        'cultures': cultures,
        'characters': characters
    }


def synthesize_and_analyze(landed_info: dict, save_data: dict, output_dir: Path):
    """
    Synthesizes game file and save file data into cohesive datasets and reports:
      - titles_data.json & counties_summary.csv
      - dynasties_and_houses.json & dynasties_and_houses.csv
      - cultures_data.json
      - historical_characters.json
      - chatenois_dynasty_analysis.json & chatenois_dynasty_analysis.md
      - phase1_extraction_report.md
    """
    log("Synthesizing datasets and generating outputs...")
    output_dir.mkdir(parents=True, exist_ok=True)

    titles_by_key = save_data['titles_by_key']
    titles_by_id = save_data['titles_by_id']
    county_mgr = save_data['county_mgr']
    provinces = save_data['provinces']
    houses = save_data['houses']
    dynasties = save_data['dynasties']
    cultures = save_data['cultures']
    characters = save_data['characters']

    vanilla_counties = landed_info['county_de_jure']
    county_to_baronies = landed_info['county_to_baronies']
    barony_to_prov = landed_info['barony_to_province']

    # Helper: resolve top liege title
    def get_top_liege(title_id):
        visited = set()
        cur_id = title_id
        while cur_id is not None and cur_id not in visited:
            visited.add(cur_id)
            t_obj = titles_by_id.get(cur_id)
            if not t_obj:
                break
            liege_id = t_obj.get('de_facto_liege')
            if liege_id is None or liege_id == cur_id:
                return t_obj
            cur_id = liege_id
        return titles_by_id.get(cur_id)

    # 1. Process Counties & Landed Titles
    processed_counties = {}
    csv_counties_rows = []

    for c_key, de_jure in vanilla_counties.items():
        save_title = titles_by_key.get(c_key, {})
        c_mgr = county_mgr.get(c_key, {})

        c_culture_id = c_mgr.get('culture')
        cult_info = cultures.get(c_culture_id, {}) if c_culture_id is not None else {}
        cult_name = cult_info.get('name', 'Unknown')
        cult_heritage = cult_info.get('heritage', 'Unknown')
        cult_lang = cult_info.get('language', 'Unknown')

        # Current holder
        holder_id = save_title.get('holder')
        holder_char = characters.get(holder_id, {}) if holder_id else {}
        holder_name = holder_char.get('first_name', 'None')
        if holder_char.get('nickname'):
            holder_name += f" \"{holder_char['nickname']}\""

        holder_hid = holder_char.get('dynasty_house')
        holder_house = houses.get(holder_hid, {}) if holder_hid else {}
        holder_house_name = holder_house.get('localized_name') or holder_house.get('name', 'None')
        is_chatenois_holder = (holder_house.get('dynasty') == 1582)

        # Holder culture resolution with fallbacks (house head -> dynasty -> county)
        holder_culture_id = holder_char.get('culture')
        if holder_culture_id is None and holder_hid:
            head_id = holder_house.get('head_of_house')
            if head_id and head_id in characters:
                holder_culture_id = characters[head_id].get('culture')
        if holder_culture_id is None and is_chatenois_holder:
            holder_culture_id = 316
        if holder_culture_id is None:
            holder_culture_id = c_culture_id
        holder_cult_name = cultures.get(holder_culture_id, {}).get('name', 'Unknown') if holder_culture_id is not None else 'Unknown'

        # Liege status & Roman Empire membership
        top_liege = get_top_liege(save_title.get('id')) if save_title.get('id') is not None else None
        top_liege_key = top_liege.get('key', 'None') if top_liege else 'None'
        is_in_roman_empire = top_liege_key in ('h_roman_empire', 'e_roman_empire', 'e_hre')

        # Baronies
        constituent_baronies = county_to_baronies.get(c_key, [])
        baronies_data = []
        built_baronies_names = []

        for b_key in constituent_baronies:
            b_prov_id = barony_to_prov.get(b_key)
            prov_data = provinces.get(b_prov_id, {}) if b_prov_id else {}
            b_save_title = titles_by_key.get(b_key, {})

            b_entry = {
                'key': b_key,
                'name': b_save_title.get('name') or b_key.replace('b_', '').replace('_', ' ').title(),
                'province_id': b_prov_id,
                'holding_type': prov_data.get('holding_type'),
                'buildings': prov_data.get('buildings', []),
                'fort_level': prov_data.get('fort_level', 0),
                'holder_id': b_save_title.get('holder')
            }
            baronies_data.append(b_entry)
            if prov_data.get('holding_type'):
                built_baronies_names.append(f"{b_key}({prov_data.get('holding_type')})")

        # History & Conquering / Founding Lord (for Option C personality engine)
        history = save_title.get('history', [])
        resolved_history = []
        conquering_lord = None

        for h in history:
            hid = h.get('holder')
            h_char = characters.get(hid, {})
            h_house_id = h_char.get('dynasty_house')
            h_house = houses.get(h_house_id, {}) if h_house_id else {}
            
            h_cult_id = h_char.get('culture')
            if h_cult_id is None and h_house_id:
                h_head_id = h_house.get('head_of_house')
                if h_head_id and h_head_id in characters:
                    h_cult_id = characters[h_head_id].get('culture')
            if h_cult_id is None and h_house.get('dynasty') == 1582:
                h_cult_id = 316
            if h_cult_id is None:
                h_cult_id = c_culture_id
            h_cult = cultures.get(h_cult_id, {}) if h_cult_id is not None else {}

            h_entry = {
                'date': h.get('date'),
                'type': h.get('type'),
                'holder_id': hid,
                'holder_name': h_char.get('first_name', 'Unknown'),
                'nickname': h_char.get('nickname', ''),
                'house_name': h_house.get('localized_name') or h_house.get('name', 'Unknown'),
                'dynasty_id': h_house.get('dynasty'),
                'culture_name': h_cult.get('name', 'Unknown'),
                'traits': h_char.get('traits_decoded', [])
            }
            resolved_history.append(h_entry)

            # Detect first post-867 conqueror / creator / appointment
            if not conquering_lord and h.get('date'):
                try:
                    year = float(h.get('date').split('.')[0])
                    if year >= 867.0 and h.get('type') in ('conquest', 'appointment', 'created', 'usurped', 'revoked'):
                        conquering_lord = h_entry
                except ValueError:
                    pass

        if not conquering_lord and resolved_history:
            # fallback to latest historical or current holder
            conquering_lord = resolved_history[-1]

        county_record = {
            'key': c_key,
            'name': save_title.get('name') or save_title.get('custom'),
            'custom_name': save_title.get('custom'),
            'localization_key': save_title.get('localization_key'),
            'adjective': save_title.get('adj'),
            'de_jure_duchy': de_jure.get('duchy'),
            'de_jure_kingdom': de_jure.get('kingdom'),
            'de_jure_empire': de_jure.get('empire'),
            'de_facto_top_liege': top_liege_key,
            'is_in_roman_empire': is_in_roman_empire,
            'culture_id': c_culture_id,
            'culture_name': cult_name,
            'culture_heritage': cult_heritage,
            'culture_language': cult_lang,
            'faith_id': c_mgr.get('rite'),
            'development': c_mgr.get('development', 0),
            'county_control': c_mgr.get('county_control', 0),
            'current_holder': {
                'id': holder_id,
                'name': holder_name,
                'house_id': holder_hid,
                'house_name': holder_house_name,
                'is_chatenois': is_chatenois_holder,
                'culture_name': holder_cult_name,
                'traits': holder_char.get('traits_decoded', [])
            },
            'conquering_or_founding_lord': conquering_lord,
            'baronies': baronies_data,
            'history': resolved_history
        }
        processed_counties[c_key] = county_record

        csv_counties_rows.append({
            'county_key': c_key,
            'save_name': county_record['name'] or '',
            'custom_name': county_record['custom_name'] or '',
            'localization_key': county_record['localization_key'] or '',
            'de_jure_duchy': de_jure.get('duchy') or '',
            'de_jure_kingdom': de_jure.get('kingdom') or '',
            'de_jure_empire': de_jure.get('empire') or '',
            'top_liege': top_liege_key,
            'is_in_roman_empire': is_in_roman_empire,
            'county_culture': cult_name,
            'county_heritage': cult_heritage,
            'county_language': cult_lang,
            'development': county_record['development'],
            'county_control': county_record['county_control'],
            'current_holder_id': holder_id or '',
            'current_holder_name': holder_name,
            'current_holder_house': holder_house_name,
            'current_holder_culture': holder_cult_name,
            'is_chatenois_holder': is_chatenois_holder,
            'founding_holder_name': conquering_lord['holder_name'] if conquering_lord else '',
            'founding_holder_traits': ';'.join(conquering_lord.get('traits', [])) if conquering_lord else '',
            'constituent_baronies_count': len(baronies_data),
            'built_baronies': ', '.join(built_baronies_names)
        })

    # 2. Process Dynasty 1582 ("Chatenois") & All Houses
    log("Analyzing Chatenois Dynasty (ID 1582) and all cadet branches...")
    chatenois_houses = []
    all_houses_csv_rows = []

    for hid, hdata in houses.items():
        did = hdata.get('dynasty')
        is_chatenois = (did == 1582)
        h_name = hdata.get('localized_name') or hdata.get('name', f"House_{hid}")
        founder_id = hdata.get('founder')
        founder_char = characters.get(founder_id, {})
        head_id = hdata.get('head_of_house')
        head_char = characters.get(head_id, {})

        # Proposed Tarraconian adjustment for Chatenois
        proposed_name = h_name
        if is_chatenois:
            if h_name == 'dynn_Chatenois' or h_name == 'Chatenois':
                proposed_name = 'Kestenholz'
            elif h_name.startswith('Chatenois-'):
                stem = h_name[len('Chatenois-'):]
                proposed_name = f"Kestenholz-{stem}"
            else:
                proposed_name = f"Kestenholz ({h_name})"

        house_entry = {
            'house_id': hid,
            'dynasty_id': did,
            'name': hdata.get('name', ''),
            'localized_name': hdata.get('localized_name', ''),
            'current_display_name': h_name,
            'proposed_tarraconian_name': proposed_name,
            'is_chatenois': is_chatenois,
            'found_date': hdata.get('found_date', ''),
            'founder_id': founder_id,
            'founder_name': founder_char.get('first_name', ''),
            'head_id': head_id,
            'head_name': head_char.get('first_name', ''),
            'head_nickname': head_char.get('nickname', ''),
            'living_members_count': hdata.get('living_members_count', 0),
            'parent_house_id': hdata.get('parent_dynasty_house')
        }

        if is_chatenois:
            chatenois_houses.append(house_entry)

        all_houses_csv_rows.append({
            'house_id': hid,
            'dynasty_id': did or '',
            'current_name': h_name,
            'proposed_tarraconian_name': proposed_name,
            'is_chatenois': is_chatenois,
            'found_date': hdata.get('found_date', ''),
            'head_id': head_id or '',
            'head_name': head_char.get('first_name', ''),
            'head_nickname': head_char.get('nickname', ''),
            'living_members_count': hdata.get('living_members_count', 0),
            'parent_house_id': hdata.get('parent_dynasty_house') or ''
        })

    # Sort Chatenois houses by living members count descending
    chatenois_houses.sort(key=lambda x: x['living_members_count'], reverse=True)

    # 3. Write Output Files
    log("Writing output files to output directory...")

    # A. titles_data.json
    titles_json_path = output_dir / "titles_data.json"
    with open(titles_json_path, 'w', encoding='utf-8') as f:
        json.dump(processed_counties, f, indent=2, ensure_ascii=False)
    log(f"  Wrote: {titles_json_path} ({titles_json_path.stat().st_size / 1024 / 1024:.1f} MB)")

    # B. counties_summary.csv
    counties_csv_path = output_dir / "counties_summary.csv"
    with open(counties_csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(csv_counties_rows[0].keys()))
        writer.writeheader()
        writer.writerows(csv_counties_rows)
    log(f"  Wrote: {counties_csv_path} ({counties_csv_path.stat().st_size / 1024:.1f} KB)")

    # C. dynasties_and_houses.json
    dyn_json_path = output_dir / "dynasties_and_houses.json"
    with open(dyn_json_path, 'w', encoding='utf-8') as f:
        json.dump({'dynasties': dynasties, 'houses': houses}, f, indent=2, ensure_ascii=False)
    log(f"  Wrote: {dyn_json_path} ({dyn_json_path.stat().st_size / 1024 / 1024:.1f} MB)")

    # D. dynasties_and_houses.csv
    dyn_csv_path = output_dir / "dynasties_and_houses.csv"
    with open(dyn_csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(all_houses_csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(all_houses_csv_rows)
    log(f"  Wrote: {dyn_csv_path} ({dyn_csv_path.stat().st_size / 1024:.1f} KB)")

    # E. cultures_data.json
    cult_json_path = output_dir / "cultures_data.json"
    with open(cult_json_path, 'w', encoding='utf-8') as f:
        json.dump(cultures, f, indent=2, ensure_ascii=False)
    log(f"  Wrote: {cult_json_path} ({cult_json_path.stat().st_size / 1024:.1f} KB)")

    # F. historical_characters.json
    chars_json_path = output_dir / "historical_characters.json"
    with open(chars_json_path, 'w', encoding='utf-8') as f:
        json.dump(characters, f, indent=2, ensure_ascii=False)
    log(f"  Wrote: {chars_json_path} ({chars_json_path.stat().st_size / 1024 / 1024:.1f} MB)")

    # G. chatenois_dynasty_analysis.json
    chatenois_analysis_data = {
        'dynasty_id': 1582,
        'current_name': 'Chatenois',
        'etymology': {
            'french_root': 'Châtenois / Chastenois',
            'latin_root': 'Castinetum (chestnut grove)',
            'germanic_historical_name': 'Kestenholz',
            'alsace_lorraine_attestation': 'Châtenois (Bas-Rhin) attested in German as Kestenholz since the Middle Ages',
            'tarraconian_phonology': 'Middle High German Moselle/Rhine Franconian kestene/kesten + holz [hɔlts] -> Kestenholz (or Kestenholt)'
        },
        'cadet_branches_count': len(chatenois_houses),
        'cadet_branches': chatenois_houses
    }
    chatenois_json_path = output_dir / "chatenois_dynasty_analysis.json"
    with open(chatenois_json_path, 'w', encoding='utf-8') as f:
        json.dump(chatenois_analysis_data, f, indent=2, ensure_ascii=False)
    log(f"  Wrote: {chatenois_json_path}")

    # H. chatenois_dynasty_analysis.md
    chatenois_md_path = output_dir / "chatenois_dynasty_analysis.md"
    with open(chatenois_md_path, 'w', encoding='utf-8') as f:
        f.write("# Linguistic Analysis & Tarraconian Adaptation: Dynasty Chatenois (ID 1582)\n\n")
        f.write("## 1. Etymological Background & Linguistic Sound Laws\n\n")
        f.write("* **Vanilla / Save Name:** `dynn_Chatenois` (*Chatenois*)\n")
        f.write("* **Etymological Origin:** From Gallo-Romance / Old French *Chastenois* / *Châtenois*, deriving from Latin **Castinetum** (*castanea* 'chestnut' + collective suffix *-etum*, meaning 'chestnut grove' or 'chestnut woods').\n")
        f.write("* **Historical Germanic Exonym:** In Alsace and Lorraine, toponyms named *Châtenois* (such as Châtenois in Bas-Rhin and Châtenois in Vosges) have been historically and consistently rendered in German as **Kestenholz** (Middle High German *kestene* / *kesten* 'chestnut' + *holz* 'wood / grove').\n")
        f.write("* **Tarraconian Sound Laws (MHG / Rhine-Moselle Franconian):**\n")
        f.write("  * Retains unshifted initial `k-` (`Kesten-`).\n")
        f.write("  * Preserves Middle High German affricate `-z` `[ts]` in `-holz`.\n")
        f.write("  * Under the Romano-Germanic imperial synthesis of the Tarraconian Chancellery, the authentic imperial Germanic name for House Châtenois is **House Kestenholz** (*Dat Hûs van Kestenholz*).\n\n")
        f.write("## 2. Inventory of Cadet Houses & Proposed Tarraconian Renames\n\n")
        f.write(f"The save contains **{len(chatenois_houses)}** cadet houses belonging to Dynasty 1582. Below is the complete register sorted by living members count:\n\n")
        f.write("| House ID | Current Name | Proposed Tarraconian Name | Found Date | Head of House | Living Members | Parent House |\n")
        f.write("| :---: | :--- | :--- | :---: | :--- | :---: | :---: |\n")
        for ch in chatenois_houses:
            head_str = f"{ch['head_name']}"
            if ch['head_nickname']:
                head_str += f" \"{ch['head_nickname']}\""
            f.write(f"| `{ch['house_id']}` | **{ch['current_display_name']}** | `{ch['proposed_tarraconian_name']}` | {ch['found_date']} | {head_str} (`{ch['head_id']}`) | {ch['living_members_count']} | `{ch['parent_house_id'] or 'None'}` |\n")
        f.write("\n---\n")
    log(f"  Wrote: {chatenois_md_path}")

    # I. phase1_extraction_report.md
    report_md_path = output_dir / "phase1_extraction_report.md"
    total_roman_counties = sum(1 for c in processed_counties.values() if c['is_in_roman_empire'])
    with open(report_md_path, 'w', encoding='utf-8') as f:
        f.write("# Phase 1 Extraction Report: Landed Titles, Dynasties & Historical Canon\n\n")
        f.write(f"* **Extraction Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"* **Output Directory:** `{output_dir}`\n\n")
        f.write("## 1. Executive Summary & Core Statistics\n\n")
        f.write(f"| Metric | Extracted Count | Description |\n")
        f.write(f"| :--- | :---: | :--- |\n")
        f.write(f"| **De Jure Counties Processed** | **{len(processed_counties)}** | Total counties mapped from vanilla landed titles hierarchy |\n")
        f.write(f"| **Counties in Roman Empire** | **{total_roman_counties}** ({total_roman_counties / len(processed_counties) * 100:.1f}%) | Counties whose de facto top liege is `h_roman_empire` / `e_hre` |\n")
        f.write(f"| **Active Cultures** | **{len(cultures)}** | Extracted from `culture_manager` with ethos, language & heritage |\n")
        f.write(f"| **Dynasties & Cadet Houses** | **{len(dynasties)}** dynasties / **{len(houses)}** houses | Total noble lineages recorded in save gamestate |\n")
        f.write(f"| **Chatenois Cadet Houses** | **{len(chatenois_houses)}** | Branches of Dynasty 1582 evaluated for Germanic rename |\n")
        f.write(f"| **Historical Characters Decoded** | **{len(characters)}** | Title holders, history conquerors, and house heads with personality traits |\n")
        f.write(f"| **Mapped Built Baronies** | **{sum(len(c['baronies']) for c in processed_counties.values())}** | Baronies with province holdings, buildings, and fort levels |\n\n")
        f.write("## 2. Culture Distribution in the Empire\n\n")
        roman_cult_counts = {}
        for c in processed_counties.values():
            if c['is_in_roman_empire']:
                c_name = c['culture_name']
                roman_cult_counts[c_name] = roman_cult_counts.get(c_name, 0) + 1
        sorted_cults = sorted(roman_cult_counts.items(), key=lambda x: x[1], reverse=True)[:15]
        f.write("Top 15 cultures across counties inside the Roman Empire:\n\n")
        f.write("| Culture | Counties Count | Percentage |\n")
        f.write("| :--- | :---: | :---: |\n")
        for c_name, count in sorted_cults:
            f.write(f"| **{c_name}** | {count} | {count / total_roman_counties * 100:.1f}% |\n")
        f.write("\n## 3. Chatenois Dynasty Germanic Adjustment\n\n")
        f.write("As detailed in [chatenois_dynasty_analysis.md](chatenois_dynasty_analysis.md), the ruling dynasty **Chatenois** (ID `1582`) derives from Latin *Castinetum* ('chestnut grove'). In historical German / Lorraine tradition and Tarraconian sound laws, the name is **Kestenholz**.\n\n")
        f.write("Key cadet branches adjusted:\n")
        for ch in chatenois_houses[:8]:
            f.write(f"* `{ch['current_display_name']}` $\\rightarrow$ **`{ch['proposed_tarraconian_name']}`** ({ch['living_members_count']} living members, Head: {ch['head_name']} `{ch['head_id']}`)\n")
        f.write("\n## 4. Generated Artifacts & File Inventory\n\n")
        f.write(f"* `titles_data.json`: Complete county-level dictionary with history, baronies, development, and liege chains.\n")
        f.write(f"* `counties_summary.csv`: Tabular spreadsheet of all counties for rapid screening and analysis.\n")
        f.write(f"* `dynasties_and_houses.json` & `dynasties_and_houses.csv`: Full register of dynasties, houses, living member counts, and proposed renames.\n")
        f.write(f"* `cultures_data.json`: Full culture definitions including hybrid parentage, ethos, language, and traditions.\n")
        f.write(f"* `historical_characters.json`: Character records with decoded traits ready for Option C personality engine.\n")
        f.write(f"* `chatenois_dynasty_analysis.json` & `.md`: Dedicated linguistic adaptation for House Chatenois $\\rightarrow$ Kestenholz.\n")
    log(f"  Wrote: {report_md_path}")
    log("All Phase 1 outputs successfully generated!")


def main():
    parser = argparse.ArgumentParser(description="CK3 Save Game & Title Hierarchy Extractor (Phase 1)")
    parser.add_argument(
        "--save-game",
        default="/mnt/windows/Program Files (x86)/Steam/userdata/204281054/1158310/remote/save games/chatenois_867_01_01.ck3",
        help="Path to .ck3 save file"
    )
    parser.add_argument(
        "--game-dir",
        default="/mnt/windows/Program Files (x86)/Steam/steamapps/common/Crusader Kings III/game",
        help="Path to CK3 game directory containing common/landed_titles"
    )
    parser.add_argument(
        "--output-dir",
        default="/var/tmp/ck3_audit/phase1",
        help="Directory to write extracted data and reports (defaults to /var/tmp/ck3_audit/phase1)"
    )
    parser.add_argument(
        "--rakaly-bin",
        default="/tmp/rakaly-0.8.22-x86_64-unknown-linux-musl/rakaly",
        help="Path to rakaly CLI binary"
    )
    parser.add_argument(
        "--melted-save",
        default="/var/tmp/ck3_audit/melted_save.ck3",
        help="Path to existing or temporary melted save file"
    )
    args = parser.parse_args()

    log("Starting Phase 1 Save Game & Game File Extraction")
    save_path = Path(args.save_game)
    game_dir = Path(args.game_dir)
    output_dir = Path(args.output_dir)
    rakaly_bin = Path(args.rakaly_bin)
    melted_save_path = Path(args.melted_save)

    # 1. Parse Landed Titles
    landed_titles_file = game_dir / "common" / "landed_titles" / "00_landed_titles.txt"
    if not landed_titles_file.is_file():
        # check alternative paths
        alt = Path("tarraconian_chancellery")
        log(f"Warning: {landed_titles_file} not found directly, checking fallback...")

    landed_info = parse_landed_titles(landed_titles_file)

    # 2. Ensure Melted Save Exists
    melted_file = ensure_melted_save(save_path, melted_save_path, rakaly_bin)

    # 3. Stream Parse Melted Save
    save_data = parse_melted_save(melted_file, landed_info)

    # 4. Synthesize & Analyze
    synthesize_and_analyze(landed_info, save_data, output_dir)
    log("Phase 1 extraction completed successfully!")


if __name__ == "__main__":
    main()

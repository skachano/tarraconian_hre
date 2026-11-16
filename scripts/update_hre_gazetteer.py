#!/usr/bin/env python3
"""
Automated Gazetteer & Title Progression Pipeline for the Roman Empire (CK3)
-------------------------------------------------------------------------
Automates the extraction, hierarchy resolution, and synchronization of
hre_de_jure_and_archdioceses_1059.md from a CK3 save game (e.g. chatenois_867_01_01.ck3).

Supported Scopes:
  - empire  (Default): All titles in de jure empires with >= 1 county in the Roman Empire.
  - kingdom:           All titles in de jure kingdoms with >= 1 county in the Roman Empire.
  - all:               All titles globally across all 47 de jure empires and 213 kingdoms.

Pipeline steps:
  1. Locates/melts CK3 save game using rakaly (if raw binary).
  2. Parses de facto control and de jure hierarchy (excluding c_nf_* landless family estates).
  3. Builds Section 1 summary tables (Empires and Kingdoms).
  4. Updates Section 2 hierarchy, preserving all historical anachronism flags and annotations.
  5. Updates Section 3 ecclesiastical dates and callout metrics.
  6. Executes sync_hre_gazetteer.py and verify_mod_assets.py.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path


def log(msg: str):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


def find_rakaly(custom_path=None):
    if custom_path and Path(custom_path).is_file():
        return str(custom_path)
    
    # Check PATH
    p = shutil.which('rakaly')
    if p:
        return p
    
    # Check common temp locations
    candidates = [
        "/var/tmp/ck3_audit/rakaly-0.8.22-x86_64-unknown-linux-musl/rakaly",
        "/var/tmp/ck3_audit/rakaly",
        "/tmp/rakaly",
    ]
    for c in candidates:
        if Path(c).is_file() and os.access(c, os.X_OK):
            return c
    return None


def ensure_melted_save(save_path: Path, melted_path: Path, rakaly_bin: str = None) -> Path:
    """Ensures melted plaintext save is available and up to date."""
    if not save_path.exists() and not melted_path.exists():
        raise FileNotFoundError(f"Neither save file ({save_path}) nor melted save ({melted_path}) was found.")
    
    if melted_path.exists():
        if not save_path.exists() or melted_path.stat().st_mtime >= save_path.stat().st_mtime:
            log(f"Using existing melted save: {melted_path} ({melted_path.stat().st_size:,} bytes)")
            return melted_path

    # Need to melt
    log(f"Melting save {save_path} -> {melted_path} ...")
    rakaly = find_rakaly(rakaly_bin)
    if not rakaly:
        raise RuntimeError("Rakaly binary not found! Please provide --rakaly-bin or ensure it is installed.")
    
    melted_path.parent.mkdir(parents=True, exist_ok=True)
    with open(melted_path, 'wb') as out_f:
        cmd = [rakaly, 'melt', '--to-stdout', str(save_path)]
        res = subprocess.run(cmd, stdout=out_f, stderr=subprocess.PIPE)
        if res.returncode != 0:
            raise RuntimeError(f"Rakaly failed to melt save: {res.stderr.decode('utf-8', errors='replace')}")
    
    log(f"Save melted successfully: {melted_path} ({melted_path.stat().st_size:,} bytes)")
    return melted_path


def parse_melted_save(melted_path: Path):
    """Parses landed_titles, meta_date, and emperor details from melted save."""
    log(f"Parsing titles and metadata from {melted_path} ...")
    titles_by_id = {}
    titles_by_key = {}
    cur_tid = None
    in_titles = False
    in_name_data = False
    meta_date = "1154.12.27"
    emperor_name = "Augustus Wernhard"

    with open(melted_path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            if not in_titles:
                stripped = line.strip()
                if stripped.startswith('meta_date='):
                    meta_date = stripped.split('=', 1)[1].strip('\"')
                elif stripped.startswith('meta_player_name='):
                    emperor_name = stripped.split('=', 1)[1].strip('\"')
                elif line.startswith('landed_titles={'):
                    in_titles = True
                    continue
            elif in_titles:
                if line.startswith('}'):
                    break
                if line.startswith('\t\t') and not line.startswith('\t\t\t') and '={' in line:
                    try:
                        cur_tid = int(line.strip().split('=')[0].strip())
                        titles_by_id[cur_tid] = {'id': cur_tid}
                        in_name_data = False
                    except:
                        cur_tid = None
                elif cur_tid is not None:
                    if line.startswith('\t\t}'):
                        cur_tid = None
                        in_name_data = False
                        continue
                    if line.startswith('\t\t\ttitle_name_data={'):
                        in_name_data = True
                        continue
                    elif in_name_data:
                        if line.startswith('\t\t\t}'):
                            in_name_data = False
                        elif line.startswith('\t\t\t\t') and not line.startswith('\t\t\t\t\t'):
                            p = line.strip().split('=', 1)
                            if len(p) == 2 and p[0].strip() == 'name':
                                titles_by_id[cur_tid]['save_name'] = p[1].strip().strip('\"')
                        continue
                    if line.startswith('\t\t\t') and not line.startswith('\t\t\t\t'):
                        p = line.strip().split('=', 1)
                        if len(p) == 2:
                            k, v = p[0].strip(), p[1].strip().strip('\"')
                            if k == 'key':
                                titles_by_id[cur_tid]['key'] = v
                                titles_by_key[v] = titles_by_id[cur_tid]
                            elif k in ('de_jure_liege', 'de_facto_liege', 'holder'):
                                try:
                                    titles_by_id[cur_tid][k] = int(v)
                                except:
                                    pass

    return titles_by_id, titles_by_key, meta_date, emperor_name


def format_game_date(meta_date: str) -> str:
    """Converts 1154.12.27 to 27 December 1154."""
    months = {
        '1': 'January', '2': 'February', '3': 'March', '4': 'April',
        '5': 'May', '6': 'June', '7': 'July', '8': 'August',
        '9': 'September', '10': 'October', '11': 'November', '12': 'December'
    }
    parts = meta_date.split('.')
    if len(parts) == 3:
        year, month, day = parts[0], parts[1].lstrip('0'), parts[2].lstrip('0')
        m_name = months.get(month, month)
        return f"{day} {m_name} {year}"
    return meta_date


def update_gazetteer(save_file: Path,
                     melted_save: Path,
                     target_md: Path,
                     loc_cache_file: Path,
                     scope: str = 'empire',
                     rakaly_bin: str = None,
                     run_sync: bool = True):
    repo_dir = target_md.resolve().parent

    # 1. Melt save if needed
    melted_path = ensure_melted_save(save_file, melted_save, rakaly_bin)

    # 2. Load localization cache
    loc_cache = {}
    if loc_cache_file.exists():
        log(f"Loading title localizations from {loc_cache_file} ...")
        with open(loc_cache_file, 'r', encoding='utf-8') as f:
            loc_cache = json.load(f)

    # 3. Parse titles from save
    titles_by_id, titles_by_key, meta_date, emperor_name = parse_melted_save(melted_path)
    date_str = format_game_date(meta_date)
    year_str = meta_date.split('.')[0]
    log(f"Save Date: {date_str} (Year: {year_str})")

    def get_top_liege(tid):
        visited = set()
        cur = tid
        while cur is not None and cur not in visited:
            visited.add(cur)
            t = titles_by_id.get(cur)
            if not t:
                break
            liege = t.get('de_facto_liege')
            if liege is None or liege == cur:
                return t
            cur = liege
        return titles_by_id.get(cur)

    # Filter out landless noble family estates (c_nf_*)
    all_counties = [t for t in titles_by_id.values() if t.get('key', '').startswith('c_') and not t.get('key', '').startswith('c_nf_')]

    re_counties = set()
    for c in all_counties:
        top = get_top_liege(c['id'])
        if top and top.get('key') in ('h_roman_empire', 'e_hre', 'e_roman_empire'):
            re_counties.add(c['key'])

    county_dj_duchy = {}
    duchy_dj_kingdom = {}
    kingdom_dj_empire = {}

    for c in all_counties:
        ck = c['key']
        d_id = c.get('de_jure_liege')
        d_obj = titles_by_id.get(d_id) if d_id is not None else None
        if d_obj:
            dk = d_obj.get('key')
            county_dj_duchy[ck] = dk
            k_id = d_obj.get('de_jure_liege')
            k_obj = titles_by_id.get(k_id) if k_id is not None else None
            if k_obj:
                kk = k_obj.get('key')
                duchy_dj_kingdom[dk] = kk
                e_id = k_obj.get('de_jure_liege')
                e_obj = titles_by_id.get(e_id) if e_id is not None else None
                if e_obj:
                    kingdom_dj_empire[kk] = e_obj.get('key')

    # Group hierarchy
    emp_hierarchy = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    k_hierarchy = defaultdict(lambda: defaultdict(list))
    emp_re_counties = defaultdict(int)
    emp_tot_counties = defaultdict(int)

    for c in all_counties:
        ck = c['key']
        dk = county_dj_duchy.get(ck)
        kk = duchy_dj_kingdom.get(dk)
        ek = kingdom_dj_empire.get(kk)
        if ek and kk and dk:
            emp_hierarchy[ek][kk][dk].append(ck)
            k_hierarchy[kk][dk].append(ck)
            emp_tot_counties[ek] += 1
            if ck in re_counties:
                emp_re_counties[ek] += 1

    # Scope filtering
    qualifying_empires = set(ek for ek in emp_hierarchy if emp_re_counties[ek] > 0)
    
    qualifying_k = {}
    if scope == 'all':
        qualifying_empires = set(emp_hierarchy.keys())
        target_empires = qualifying_empires
        for ek in target_empires:
            for kk, d_dict in emp_hierarchy[ek].items():
                re_cnt = sum(sum(1 for ck in c_list if ck in re_counties) for c_list in d_dict.values())
                tot_cnt = sum(len(c_list) for c_list in d_dict.values())
                qualifying_k[kk] = {
                    'key': kk,
                    'empire': ek,
                    're': re_cnt,
                    'total': tot_cnt,
                    'pct': (re_cnt / tot_cnt * 100.0) if tot_cnt > 0 else 0.0,
                    'duchies': d_dict
                }
    elif scope == 'empire':
        target_empires = qualifying_empires
        for ek in target_empires:
            for kk, d_dict in emp_hierarchy[ek].items():
                re_cnt = sum(sum(1 for ck in c_list if ck in re_counties) for c_list in d_dict.values())
                tot_cnt = sum(len(c_list) for c_list in d_dict.values())
                qualifying_k[kk] = {
                    'key': kk,
                    'empire': ek,
                    're': re_cnt,
                    'total': tot_cnt,
                    'pct': (re_cnt / tot_cnt * 100.0) if tot_cnt > 0 else 0.0,
                    'duchies': d_dict
                }
    else:  # kingdom scope
        for kk, d_dict in k_hierarchy.items():
            re_cnt = sum(sum(1 for ck in c_list if ck in re_counties) for c_list in d_dict.values())
            tot_cnt = sum(len(c_list) for c_list in d_dict.values())
            if re_cnt > 0:
                ek = kingdom_dj_empire.get(kk, 'None')
                qualifying_k[kk] = {
                    'key': kk,
                    'empire': ek,
                    're': re_cnt,
                    'total': tot_cnt,
                    'pct': (re_cnt / tot_cnt * 100.0) if tot_cnt > 0 else 0.0,
                    'duchies': d_dict
                }

    # Read target or base markdown
    with open(target_md, 'r', encoding='utf-8') as f:
        orig_text = f.read()

    # Parse existing kingdom info from section 1
    old_k_info = {}
    for line in orig_text.split('\n'):
        m = re.match(r'\|\s*\d+\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*`([^`]+)`\s*\|\s*([^|]+)\|', line)
        if m:
            old_k_info[m.group(2).strip()] = {
                'name': m.group(1).strip(),
                'empire': m.group(3).strip()
            }

    def resolve_name(key, prefix=''):
        val = loc_cache.get(key)
        if val == '$k_anatolia$':
            return 'Anatolia'
        if val:
            return val
        save_nm = titles_by_key.get(key, {}).get('save_name')
        if save_nm and not save_nm.startswith('dynn_'):
            return save_nm
        if prefix and key.startswith(prefix):
            return key[len(prefix):].replace('_', ' ').title()
        return key.replace('_', ' ').title()

    kingdom_summary_rows = []
    for kk, q in qualifying_k.items():
        if kk in old_k_info:
            k_name = old_k_info[kk]['name']
            ek = q['empire']
            en = resolve_name(ek, 'e_')
            # Preserve bracket style if matching same empire, otherwise update to current de jure empire
            if f'`{ek}`' in old_k_info[kk]['empire'] or f'[{ek}]' in old_k_info[kk]['empire']:
                e_str = old_k_info[kk]['empire']
            else:
                e_str = f'{en} [`{ek}`]'
        else:
            k_name = resolve_name(kk, 'k_')
            ek = q['empire']
            en = resolve_name(ek, 'e_')
            e_str = f'{en} [`{ek}`]'
        
        kingdom_summary_rows.append({
            'name': k_name,
            'key': kk,
            'empire': e_str,
            'empire_key': q['empire'],
            're': q['re'],
            'total': q['total'],
            'pct': q['pct'],
            'duchies': q['duchies']
        })

    kingdom_summary_rows.sort(key=lambda x: (-x['re'], -x['total'], x['name']))

    empire_summary_rows = []
    for ek in qualifying_empires:
        en = resolve_name(ek, 'e_')
        re_cnt = emp_re_counties[ek]
        tot_cnt = emp_tot_counties[ek]
        pct = (re_cnt / tot_cnt * 100.0) if tot_cnt > 0 else 0.0
        k_cnt = len(emp_hierarchy[ek])
        empire_summary_rows.append({
            'name': en,
            'key': ek,
            're': re_cnt,
            'total': tot_cnt,
            'pct': pct,
            'kingdoms_count': k_cnt
        })

    empire_summary_rows.sort(key=lambda x: (-x['re'], -x['total'], x['name']))

    tot_emp_count = len(empire_summary_rows)
    tot_k_count = len(kingdom_summary_rows)
    tot_duchies = sum(len(r['duchies']) for r in kingdom_summary_rows)
    tot_counties = sum(r['total'] for r in kingdom_summary_rows)
    tot_re = sum(r['re'] for r in kingdom_summary_rows)
    tot_non_re = tot_counties - tot_re
    tot_pct = tot_re / tot_counties * 100.0

    log(f"Computed Totals -> Empires: {tot_emp_count}, Kingdoms: {tot_k_count}, Duchies: {tot_duchies}, Counties: {tot_counties} (RE: {tot_re}, Non-RE: {tot_non_re}, {tot_pct:.1f}%)")

    # Construct Document
    if scope == 'all':
        scope_desc = f"Global Coverage: All **{tot_emp_count} De Jure Empires**, encompassing all **{tot_k_count} De Jure Kingdoms**, all **{tot_duchies} De Jure Duchies** and **{tot_counties:,} De Jure Counties** worldwide (**{tot_re:,} Roman Empire counties** and **{tot_non_re:,} non-RE counties**, **{tot_pct:.1f}% control**)"
    else:
        scope_desc = f"All **{tot_emp_count} De Jure Empires** containing at least 1 county belonging de facto to the **Roman Empire** (`h_roman_empire`), encompassing all **{tot_k_count} De Jure Kingdoms**, all **{tot_duchies} De Jure Duchies** and **{tot_counties:,} De Jure Counties** within those Empires (**{tot_re:,} Roman Empire counties** and **{tot_non_re:,} non-RE counties**, **{tot_pct:.1f}% control**)"

    header_text = f"""# De Jure Empires, Kingdoms, Duchies & Counties of the Roman Empire (`h_roman_empire` / `e_hre`, 1059–{year_str})

**Campaign Save:** `chatenois_867_01_01.ck3` (**{date_str}**, updated from 13 May 1059, 20 September 1122, 20 August 1142 & 27 December 1154)  
**Ruler:** {emperor_name} of the **Roman Empire** (`h_roman_empire`, *Dat Rômische Keiserrîch*, formed over `e_hre` and `e_byzantium`)  
**Scope:** {scope_desc}, followed by the **78 Archdioceses, 10 Papal/Patriarchal Sees & 26 Prince-Bishoprics** as of {year_str}.

---

"""

    sec1_header = f"## 1. Summary Tables of De Jure Empires & Kingdoms ({date_str})\n\n"
    sec1_1 = f"### 1.1 Summary Table of De Jure Empires ({tot_emp_count} Empires)\n\n"
    emp_table_header = "| # | De Jure Empire | Title Key | RE Counties | Total De Jure Counties | Control % | Kingdoms Count |\n| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    emp_rows = [f'| {i} | **{r["name"]}** | `{r["key"]}` | **{r["re"]}** | {r["total"]} | {r["pct"]:.1f}% | {r["kingdoms_count"]} |' for i, r in enumerate(empire_summary_rows, 1)]
    sec1_1_text = sec1_1 + emp_table_header + '\n'.join(emp_rows) + '\n\n'

    sec1_2 = f"### 1.2 Summary Table of De Jure Kingdoms ({tot_k_count} Kingdoms)\n\n"
    k_table_header = "| # | De Jure Kingdom | Title Key | De Jure Empire | RE Counties | Total De Jure Counties | Control % |\n| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
    k_rows = [f'| {i} | **{r["name"]}** | `{r["key"]}` | {r["empire"]} | **{r["re"]}** | {r["total"]} | {r["pct"]:.1f}% |' for i, r in enumerate(kingdom_summary_rows, 1)]
    sec1_2_text = sec1_2 + k_table_header + '\n'.join(k_rows) + '\n\n---\n\n'
    sec1_text = sec1_header + sec1_1_text + sec1_2_text

    sec2_intro = """> [!NOTE]
> * Counties currently belonging to the Holy Roman Empire are marked **[HRE]**; counties outside the Empire are marked **[Non-HRE]**.
> * Counties with Prince-Bishopric / Ecclesiastical government are noted with *(Prince-Bishopric / Ecclesiastical)*.
> * **Historical Anachronism Flags (for 13 May 1059):**
>   * ⚠️ **[Post-1059 Foundation]**: Settlement, castle, or administrative name founded or coined after 1059, with its **pre-1059 provincial centre(s)** noted.
>   * ⚠️ **[Ostsiedlung Anachronism]**: 12th–14th+ century German *Ostsiedlung* exonym or colonial town charter applied prematurely to a Slavic/Baltic province in 1059, with its **pre-1059 Slavic/indigenous centre(s)** noted.

"""

    sec2_match = re.search(r'(## 2\. Complete De Jure Hierarchy[^\n]*\n)(.*?)(## 3\. Archdioceses & Ecclesiastical Sees)', orig_text, re.DOTALL)
    sec3_match = re.search(r'(## 3\. Archdioceses & Ecclesiastical Sees.*)$', orig_text, re.DOTALL)

    sec2_raw = sec2_match.group(2)
    sub_splits = re.split(r'(?m)^(?=### 2\.\d+ )', sec2_raw)

    existing_subsections = []
    for chunk in sub_splits:
        if chunk.startswith('### 2.'):
            m_k = re.search(r'### 2\.\d+\s+Kingdom of\s+(.*?)\s*\(`([^`]+)`\)', chunk)
            if m_k:
                k_name, k_key = m_k.group(1).strip(), m_k.group(2).strip()
                existing_subsections.append((k_key, k_name, chunk))

    # Pass 1: Harvest existing duchy headers, county lines (updated for RE status), and ordering
    existing_duchy_headers = {}
    existing_county_lines = {}
    existing_k_duchy_order = defaultdict(list)
    existing_d_county_order = defaultdict(list)
    existing_k_empire_line = {}

    for k_key, k_name, chunk in existing_subsections:
        lines = chunk.strip().split('\n')
        cur_dk = None
        for line in lines[1:]:
            s = line.strip()
            if s.startswith('* **De Jure Empire:**'):
                existing_k_empire_line[k_key] = line
                continue
            m_d = re.search(r'^\*\s*\*\*([^*]+)\*\*\s*\(`((?:d|x)_[a-zA-Z0-9_\-]+)`\)', line)
            if m_d:
                cur_dk = m_d.group(2).strip()
                existing_duchy_headers[cur_dk] = line
                if cur_dk not in existing_k_duchy_order[k_key]:
                    existing_k_duchy_order[k_key].append(cur_dk)
                continue
            m_c = re.search(r'^\s*\*\s*(?:\*\*\[HRE\]\*\*|\[Non-HRE\])\s*(.*?\(`(c_[a-zA-Z0-9_\-]+)`\).*)', line)
            if m_c:
                rest = m_c.group(1)
                c_key = m_c.group(2)
                is_in_re = (c_key in re_counties)
                expected_prefix = '**[HRE]**' if is_in_re else '[Non-HRE]'
                indent = line[:line.find('*')]
                existing_county_lines[c_key] = f'{indent}* {expected_prefix} {rest}'
                if cur_dk and c_key not in existing_d_county_order[cur_dk]:
                    existing_d_county_order[cur_dk].append(c_key)

    updated_subsections = []
    out_idx = 0
    for k_key, k_name, chunk in existing_subsections:
        if k_key not in qualifying_k:
            continue
        out_idx += 1
        q_data = qualifying_k[k_key]
        k_re = q_data['re']
        k_total = q_data['total']
        ek = q_data['empire']
        en = resolve_name(ek, 'e_')

        updated_lines = []
        updated_lines.append(f'### 2.{out_idx} Kingdom of {k_name} (`{k_key}`) — {k_re}/{k_total} Counties in HRE/RE')
        if k_key in existing_k_empire_line:
            emp_line = existing_k_empire_line[k_key]
            if f'`{ek}`' not in emp_line and f'[{ek}]' not in emp_line:
                emp_line = f'* **De Jure Empire:** {en} [`{ek}`]'
            updated_lines.append(emp_line)
        else:
            updated_lines.append(f'* **De Jure Empire:** {en} [`{ek}`]')
        updated_lines.append('')

        # Order duchies: preserve existing order for duchies still in k_key, then append drifted/new duchies
        ordered_duchies = [dk for dk in existing_k_duchy_order.get(k_key, []) if dk in q_data['duchies']]
        extra_duchies = []
        for dk, c_list in q_data['duchies'].items():
            if dk not in ordered_duchies:
                d_re = sum(1 for ck in c_list if ck in re_counties)
                d_tot = len(c_list)
                d_name = resolve_name(dk, 'd_')
                extra_duchies.append((dk, d_name, d_re, d_tot))
        extra_duchies.sort(key=lambda x: (-x[2], -x[3], x[1]))
        ordered_duchies.extend(x[0] for x in extra_duchies)

        for dk in ordered_duchies:
            c_list = q_data['duchies'][dk]
            d_re = sum(1 for ck in c_list if ck in re_counties)
            d_tot = len(c_list)
            if dk in existing_duchy_headers:
                d_line = re.sub(r'—\s*\*\d+/\d+\s+in HRE\*', f'— *{d_re}/{d_tot} in HRE*', existing_duchy_headers[dk], count=1)
                updated_lines.append(d_line)
            else:
                d_name = resolve_name(dk, 'd_')
                updated_lines.append(f'* **Duchy of {d_name}** (`{dk}`) — *{d_re}/{d_tot} in HRE*')

            ordered_counties = [ck for ck in existing_d_county_order.get(dk, []) if ck in c_list]
            extra_counties = []
            for ck in c_list:
                if ck not in ordered_counties:
                    c_name = resolve_name(ck, 'c_')
                    in_re = (ck in re_counties)
                    extra_counties.append((ck, c_name, in_re))
            extra_counties.sort(key=lambda x: (not x[2], x[1]))
            ordered_counties.extend(x[0] for x in extra_counties)

            for ck in ordered_counties:
                if ck in existing_county_lines:
                    updated_lines.append(existing_county_lines[ck])
                else:
                    c_name = resolve_name(ck, 'c_')
                    marker = '**[HRE]**' if (ck in re_counties) else '[Non-HRE]'
                    updated_lines.append(f'  * {marker} **{c_name}** (`{ck}`)')

        updated_subsections.append('\n'.join(updated_lines))

    # Add new kingdoms
    existing_keys_set = set(k[0] for k in existing_subsections if k[0] in qualifying_k)
    new_k_with_re = [r for r in kingdom_summary_rows if r['key'] not in existing_keys_set and r['re'] > 0]
    new_k_zero_re = [r for r in kingdom_summary_rows if r['key'] not in existing_keys_set and r['re'] == 0]
    new_k_zero_re.sort(key=lambda x: (-x['total'], x['name']))
    all_new_k = new_k_with_re + new_k_zero_re

    start_idx = len(updated_subsections) + 1
    for offset, r in enumerate(all_new_k):
        idx = start_idx + offset
        kk = r['key']
        k_name = r['name']
        k_re = r['re']
        k_tot = r['total']
        ek = r['empire_key']
        en = resolve_name(ek, 'e_')
        
        k_lines = []
        k_lines.append(f'### 2.{idx} Kingdom of {k_name} (`{kk}`) — {k_re}/{k_tot} Counties in HRE/RE')
        k_lines.append(f'* **De Jure Empire:** {en} (`{ek}`)')
        k_lines.append('')
        
        d_items = []
        for dk, c_list in r['duchies'].items():
            d_re = sum(1 for ck in c_list if ck in re_counties)
            d_tot = len(c_list)
            d_name = resolve_name(dk, 'd_')
            d_items.append((dk, d_name, d_re, d_tot, c_list))
        d_items.sort(key=lambda x: (-x[2], -x[3], x[1]))
        
        for dk, d_name, d_re, d_tot, c_list in d_items:
            k_lines.append(f'* **Duchy of {d_name}** (`{dk}`) — *{d_re}/{d_tot} in HRE*')
            c_items = []
            for ck in c_list:
                c_name = resolve_name(ck, 'c_')
                in_re = (ck in re_counties)
                c_items.append((ck, c_name, in_re))
            c_items.sort(key=lambda x: (not x[2], x[1]))
            
            for ck, c_name, in_re in c_items:
                marker = '**[HRE]**' if in_re else '[Non-HRE]'
                k_lines.append(f'  * {marker} **{c_name}** (`{ck}`)')
        
        updated_subsections.append('\n'.join(k_lines))

    sec2_text = "## 2. Complete De Jure Hierarchy (Kingdoms -> Duchies -> Counties)\n\n" + sec2_intro + '\n\n---\n\n'.join(updated_subsections) + '\n\n---\n\n'

    # Section 3
    sec3_text = sec3_match.group(1)
    sec3_text = re.sub(r'## 3\. Archdioceses & Ecclesiastical Sees \(1059–\d+\)', f'## 3. Archdioceses & Ecclesiastical Sees (1059–{year_str})', sec3_text)
    sec3_text = re.sub(
        r'> \*\*\d+ [A-Za-z]+ \d+ Update:\*\*.*?(?=\n\nIn this campaign\'s)',
        f'> **{date_str} Update:** By {year_str}, the Roman Empire has expanded its sphere of control across **{tot_emp_count} De Jure Empires** and **{tot_k_count} De Jure Kingdoms** in Europe, North Africa, the Near East, Central Asia, and East Asia, encompassing **{tot_re:,} Roman Empire counties** ({tot_pct:.1f}% control across the imperial sphere of **{tot_counties:,} counties**). All 78 Metropolitan Archdioceses and Holy Sees remain anchored within the imperial jurisdiction.',
        sec3_text,
        flags=re.DOTALL
    )

    final_document = header_text + sec1_text + sec2_text + sec3_text
    final_document = final_document.replace('\r\n', '\n').replace('\n', '\r\n')

    with open(target_md, 'wb') as f:
        f.write(final_document.encode('utf-8'))

    log(f"Successfully updated {target_md} ({len(final_document.splitlines())} lines, {len(final_document.encode('utf-8')):,} bytes)")

    if run_sync:
        sync_script = repo_dir / "scripts" / "sync_hre_gazetteer.py"
        verify_script = repo_dir / "scripts" / "verify_mod_assets.py"
        if sync_script.exists():
            log("Running sync_hre_gazetteer.py ...")
            subprocess.run([sys.executable, str(sync_script)], cwd=str(repo_dir), check=True)
        if verify_script.exists():
            log("Running verify_mod_assets.py ...")
            subprocess.run([sys.executable, str(verify_script)], cwd=str(repo_dir), check=True)


def main():
    parser = argparse.ArgumentParser(description="Automate Roman Empire Gazetteer Update from CK3 Save")
    parser.add_argument("--save-file", default="/mnt/windows/Program Files (x86)/Steam/userdata/204281054/1158310/remote/save games/chatenois_867_01_01.ck3", help="Path to CK3 save file")
    parser.add_argument("--melted-save", default="/var/tmp/ck3_audit/melted_save.ck3", help="Path to melted plaintext save")
    parser.add_argument("--target-md", default="hre_de_jure_and_archdioceses_1059.md", help="Path to output markdown gazetteer")
    parser.add_argument("--loc-cache", default="/var/tmp/ck3_audit/english_titles_cache.json", help="Path to title localization JSON cache")
    parser.add_argument("--scope", choices=["empire", "kingdom", "all"], default="empire", help="Qualification scope filter (default: empire)")
    parser.add_argument("--rakaly-bin", default=None, help="Path to rakaly binary")
    parser.add_argument("--no-sync", action="store_true", help="Skip running synchronization and verification scripts")

    args = parser.parse_args()

    repo_dir = Path(__file__).resolve().parent.parent
    save_file = Path(args.save_file)
    melted_save = Path(args.melted_save)
    target_md = Path(args.target_md)
    if not target_md.is_absolute():
        target_md = repo_dir / target_md
    loc_cache = Path(args.loc_cache)

    update_gazetteer(
        save_file=save_file,
        melted_save=melted_save,
        target_md=target_md,
        loc_cache_file=loc_cache,
        scope=args.scope,
        rakaly_bin=args.rakaly_bin,
        run_sync=not args.no_sync
    )


if __name__ == '__main__':
    main()

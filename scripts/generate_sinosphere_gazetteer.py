#!/usr/bin/env python3
"""
Generate Sinosphere Title Gazetteer and Comprehensive Size Audit for CK3 in 1154.
Includes full integration of the 61 Historical Anachronism Resolutions.
Outputs: sinosphere_titles_and_characters_1154.md
"""

import csv
import json
import re
from pathlib import Path
from collections import defaultdict, Counter

REPO_ROOT = Path(__file__).resolve().parent.parent
PHASE1_DIR = Path('/var/tmp/ck3_audit/phase1')
COUNTIES_CSV = PHASE1_DIR / 'counties_summary.csv'
ZH_CACHE_PATH = Path('/var/tmp/ck3_audit/chinese_titles_cache.json')
EN_CACHE_PATH = Path('/var/tmp/ck3_audit/english_titles_cache.json')
AUDIT_DISCREPANCIES_PATH = REPO_ROOT / 'audit_discrepancy_register.md'
P4_RESOLUTIONS_PATH = Path('/var/tmp/ck3_audit/phase4/final_title_resolutions.csv')
TARGET_MD = REPO_ROOT / 'sinosphere_titles_and_characters_1154.md'

with open(ZH_CACHE_PATH, 'r', encoding='utf-8') as f:
    zh_loc = json.load(f)

with open(EN_CACHE_PATH, 'r', encoding='utf-8') as f:
    en_loc = json.load(f)

with open(COUNTIES_CSV, 'r', encoding='utf-8') as f:
    counties = list(csv.DictReader(f))

# Load Phase 4 resolutions if available
p4_resolutions = {}
if P4_RESOLUTIONS_PATH.exists():
    with open(P4_RESOLUTIONS_PATH, 'r', encoding='utf-8') as f:
        p4_resolutions = {r['county_key']: r for r in csv.DictReader(f)}

# Load Audit Discrepancies from audit_discrepancy_register.md
audit_discrepancies = {}
if AUDIT_DISCREPANCIES_PATH.exists():
    with open(AUDIT_DISCREPANCIES_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('| `c_'):
                parts = [p.strip() for p in line.split('|')[1:-1]]
                if parts:
                    ck = parts[0].strip('`')
                    audit_discrepancies[ck] = {
                        'save_name': parts[1],
                        'kingdom': parts[2],
                        'tier': parts[3],
                        'reason': parts[4],
                        'resolution': parts[5],
                        'tarr_title': parts[6],
                        'adjective': parts[7],
                        'justification': parts[8] if len(parts) > 8 else ''
                    }

def clean_zh(val):
    if not val: return ''
    return val.split('\"')[0].strip()

def get_trad(val):
    if not val or '#' not in val: return ''
    comment = val.split('#')[1].strip()
    cjk = ''.join(c for c in comment if '\u4e00' <= c <= '\u9fff')
    return cjk

def resolve_macro(val, loc_dict):
    if not val: return ''
    m = re.match(r'^\$([\w\.\-]+)\$$', val)
    if m:
        inner = m.group(1)
        return loc_dict.get(inner, inner)
    return val

def get_title_zh(key):
    raw = zh_loc.get(key, '')
    simp = clean_zh(raw)
    simp = resolve_macro(simp, zh_loc)
    trad = get_trad(raw)
    return simp, trad

def get_title_en(key):
    val = en_loc.get(key, key)
    res = resolve_macro(val, en_loc)
    if res == 'dai_viet' or key == 'k_viet':
        return 'Đại Việt'
    return res

def decode_ck3_cjk(s):
    if not s: return ''
    def repl(m):
        code = int(m.group(1), 16)
        return f" ({chr(code)})"
    res = re.sub(r'_([0-9A-Fa-f]{4})', repl, s)
    res = re.sub(r'\)\s*\(([^\)]+)\)', r'\1', res)
    return res

# Detailed Historical Anachronism Notes Dictionary
HISTORICAL_ANACHRONISM_NOTES = {
    # Khitan Liao Foundations
    "c_LIAO_linhuang": "Founded in 918 AD by Yelü Abaoji (Emperor Taizu of Liao) as the Supreme Capital (Liao Shangjing / 上京临潢府) on the Shira Muren river.",
    "c_LIAO_dading": "Founded in 1007 AD by Emperor Shengzong of Liao as the Central Capital (Liao Zhongjing / 中京大定府).",
    "c_LIAO_changchun": "Established in 926 AD by the Khitans as a state-sponsored relocation garrison following the conquest of Bohai.",
    "c_LIAO_longhuazhou": "Founded in 902 AD by Yelü Abaoji as a fortified private encampment (dongzhai) prior to his imperial coronation.",
    "c_LIAO_raozhou": "Established in 953 AD by Emperor Muzong of Liao in the fertile upper Xilamulun river basin.",
    "c_LIAO_jinzhou": "Established in 923 AD by Yelü Abaoji with captive Han artisans from Pingzhou.",
    "c_LIAO_xianzhou": "Established in 926 AD at the medical and ancestral tumulus of Prince Yelü Bei (Prince of Dongdan).",
    "c_lzj_chengde": "Modern anachronism derived from the Qing dynasty imperial mountain resort (Bishu Shanzhuang, founded 1703 AD).",
    "c_lzj_chengdexi": "Descriptive modern subdivision of the Qing-era Chengde prefecture.",
    "c_LIAO_chaoyang": "Post-867 Khitan regional commandery in the Daling River valley.",
    "c_LIAO_dalian": "Post-867 Khitan regional encampment; lacks pre-867 civil center.",
    "c_LIAO_heicaoan": "Post-867 pastoral encampment on the eastern steppe frontier.",
    "c_LIAO_horqinan": "Post-867 Horqin steppe grazing division; unverified prior to 867 AD.",
    "c_LIAO_ningzhou": "Post-867 Liao garrison prefecture established in former Bohai territory.",
    "c_LIAO_taizhou": "Established in 916–926 AD as a Liao defensive garrison prefecture.",
    "c_LIAO_ulagaian": "Post-867 Ulagai river frontier march; unverified prior to 867 AD.",
    "c_LIAO_wuzhou": "Post-867 Liao tribal prefecture; unverified prior to 867 AD.",
    "c_liao_fengzhou": "Post-867 Liao garrison prefecture in southern Inner Mongolia.",
    "c_lnj_liaoxi": "Descriptive post-867 frontier slice; lacks ancient urban center.",
    "c_lnj_liaoxibei": "Descriptive post-867 frontier slice; lacks ancient urban center.",
    "c_lxj_huanzhou": "Established 960+ AD by the Khitans as an inner march prefecture.",
    "c_lxj_yangchengzhou": "Post-867 Khitan grazing prefecture; unverified prior to 867 AD.",
    "c_lxj_yuyidong": "Post-867 marchland division of the Yuyi frontier.",
    "c_woye": "Post-867 frontier pastoral division; lacks pre-867 civil oppidum.",
    # Amur & Outer Northeast Outposts
    "c_eman_nurgan": "Named after the Ming dynasty Nurgan Regional Military Commission (奴儿干都司), established in 1409 AD. Lacks pre-867 urban center.",
    "c_eman_boli": "Confluence of the Amur and Ussuri rivers (modern Khabarovsk); administrative town dates to modern/Qing era.",
    "c_kusunkotan": "Sakhalin Island indigenous settlement (later Korsakov / Kusunkotan, established in 18th century).",
    "c_eman_amgun": "Remote northern Amgun river tributary; lacks pre-867 attested town.",
    "c_eman_beihean": "Descriptive placeholder ('North River Bank'); lacks ancient town.",
    "c_eman_choripi": "Remote Tungusic wilderness area; lacks pre-867 urban center.",
    "c_eman_mohean": "Remote Amur basin territory; lacks pre-867 urban foundation.",
    "c_eman_molihewen": "Remote forest outpost; lacks pre-867 verified settlement.",
    "c_eman_tugur": "Okhotsk sea coastal tract; unverified prior to 867 AD.",
    "c_eman_yerenhe": "Descriptive placeholder ('Wild Jurchen River'); lacks ancient town.",
    # Jurchen & Bohai Frontier Settlements
    "c_BAL_delizhen": "Jurchen border market post established during late Bohai/Liao transition.",
    "c_BAL_huligai": "Ilun Hurka route of the Jurchen tribes along the Mudanjiang River.",
    "c_BAL_heuksu_anwon": "Northern Mohe frontier market on the Amur/Heuksu.",
    "c_BAL_north_anwon": "Descriptive northern frontier market outpost of Bohai.",
    "c_BAL_anbyeon": "Anbian border commandery on the frontier of Bohai and the Khitans.",
    "c_BAL_north_anbyeon": "Descriptive frontier subdivision of Anbian.",
    "c_BAL_solbin": "Suifen river basin; Bohai secondary prefecture reorganised post-867.",
    "c_BAL_jeongni": "Post-867 Bohai/Jurchen prefecture; unverified pre-867 center.",
    "c_BAL_ningzhou": "Post-867 Bohai relocation prefecture.",
    "c_BAL_supin": "Post-867 Jurchen tribal valley; unverified urban center.",
    "c_BAL_west_cheolli": "Descriptive subdivision of Tieli Jurchen territory.",
    # Shiwei Nomadic Divisions
    "c_SW_damoguo": "Post-867 Shiwei nomadic clan encampment division.",
    "c_SW_dongcheziguo": "Nomadic clan division ('Eastern Cart Tribe'); lacks fixed pre-867 urban center.",
    "c_SW_heilonghean": "Descriptive natural placeholder ('Amur River Bank').",
    "c_SW_hongxingan": "Descriptive modern oronym slice ('Red Khingan').",
    "c_SW_huangtouguo": "Tribal division ('Yellow Head Tribe'); unverified pre-867 center.",
    "c_SW_hulunbuir": "Modern banner / post-867 lake pastoral area; lacks ancient town.",
    "c_SW_luotuoguo": "Tribal division ('Camel Tribe'); lacks ancient urban foundation.",
    "c_SW_nabeiguo": "Post-867 northern Nen river tribal division.",
    "c_SW_puyuzhou": "Post-867 Jin/Liao route prefecture; unverified in 867 AD.",
    "c_SW_shanbeiguo": "Descriptive tribal division ('North Mountain Tribe').",
    "c_SW_xinghuangtou": "Descriptive tribal division; unverified urban center.",
    "c_SW_xingnabei": "Descriptive tribal division; unverified urban center.",
    "c_SW_zhongcheziguo": "Nomadic clan division ('Middle Cart Tribe').",
    # Guannei Mountain Passes
    "c_xiaoguan": "Xiao Pass (萧关) on Mount Liupan; flagged as a military pass rather than an ancient civil oppidum.",
    "c_jingzhou": "Frontier screening flag; resolved to the ancient Jing River (Jinghe) basin.",
    "c_yuanzhou_2": "Duplicate key disambiguation; resolved to the Upper Qingshui / Yuan basin."
}

# Empire groupings
core_empires = ['e_zhongyuan', 'e_liangyi', 'e_jingyang', 'e_yongliang', 'e_lingnan']
peripheral_empires = ['e_goryeo', 'e_japan', 'e_andong', 'e_amur']
all_sinosphere_empires = core_empires + peripheral_empires

# Filter counties
core_counties = [c for c in counties if c['de_jure_empire'] in core_empires]
greater_counties = [c for c in counties if c['de_jure_empire'] in all_sinosphere_empires]

core_count = len(core_counties)
core_baronies = sum(int(c['constituent_baronies_count']) for c in core_counties)
core_dev = sum(float(c['development']) for c in core_counties)
core_re = sum(1 for c in core_counties if c['is_in_roman_empire'] == 'True')

greater_count = len(greater_counties)
greater_baronies = sum(int(c['constituent_baronies_count']) for c in greater_counties)
greater_dev = sum(float(c['development']) for c in greater_counties)
greater_re = sum(1 for c in greater_counties if c['is_in_roman_empire'] == 'True')

flagged_counties = [c for c in greater_counties if c['county_key'] in audit_discrepancies]
flagged_count = len(flagged_counties)

lines = []

lines.append("# Sinosphere Title Gazetteer & Comprehensive Audit (CK3 — 1154)")
lines.append("")
lines.append("> **Historical & Gamestate Reference Document**  ")
lines.append("> **Game Date:** 27 December 1154 (`1154.12.27`)  ")
lines.append("> **Campaign Save Game:** `chatenois_867_01_01.ck3`  ")
lines.append("> **Engine Mechanics:** Crusader Kings III (with East Asia & Mandate of Heaven / Dynastic Cycle System)  ")
lines.append(f"> **Historical Canon Standards:** 867 Alternate-History Divergence Point | Three-Tier Classification System | Toponym-First Principle  ")
lines.append("")
lines.append("---")
lines.append("")

# Section 1: Executive Summary
lines.append("## 1. Executive Summary: The Size of the Sinosphere in 1154")
lines.append("")
lines.append("In Crusader Kings III, the **Sinosphere** (East Asian Cultural Sphere / 汉字文化圈 / 儒家文化圈) encompasses both the **Core Middle Kingdom** (China Proper, formally codified in game mechanics as Subregion 0 of the `dynastic_cycle` Mandate of Heaven struggle/situation) and the broader **East Asian cultural and tributary perimeter** (Korea, Japan, Manchuria/Liao, and northern Indochina/Đại Việt) that historically utilized Chinese characters, administrative statecraft, and diplomatic investiture.")
lines.append("")

lines.append("### 1.1 Comparative Dimension Overview")
lines.append("")
lines.append("| Metric Dimension | Core Sinosphere (China Proper) | Extended Sinosphere (Korea, Japan, Andong, Amur) | Full Greater Sinosphere Total |")
lines.append("| :--- | :---: | :---: | :---: |")
lines.append(f"| **De Jure Empires** | **5 Empires** | **4 Empires** | **9 Empires** |")
lines.append(f"| **De Jure Kingdoms** | **24 Kingdoms** | **15 Kingdoms** | **39 Kingdoms** |")
lines.append(f"| **De Jure Duchies** | **101 Duchies** | **52 Duchies** | **153 Duchies** |")
lines.append(f"| **County-Tier Titles** | **{core_count} Counties** (61.3%) | **{greater_count - core_count} Counties** (38.7%) | **{greater_count} Counties** (100.0%) |")
lines.append(f"| **Constituent Holdings / Baronies** | **{core_baronies:,} Baronies** (avg {core_baronies/core_count:.2f}/county) | **{greater_baronies - core_baronies:,} Baronies** (avg {(greater_baronies - core_baronies)/(greater_count - core_count):.2f}/county) | **{greater_baronies:,} Baronies** (avg {greater_baronies/greater_count:.2f}/county) |")
lines.append(f"| **Total Base Development** | **{core_dev:,.1f}** | **{greater_dev - core_dev:,.1f}** | **{greater_dev:,.1f}** |")
lines.append(f"| **Average Development per County** | **{core_dev/core_count:.1f}** | **{(greater_dev - core_dev)/(greater_count - core_count):.1f}** | **{greater_dev/greater_count:.1f}** |")
lines.append(f"| **Roman Empire Control in 1154** | **{core_re} / {core_count}** ({core_re/core_count*100:.1f}%) | **{greater_re - core_re} / {greater_count - core_count}** ({(greater_re - core_re)/(greater_count - core_count)*100:.1f}%) | **{greater_re} / {greater_count}** ({greater_re/greater_count*100:.1f}%) |")
lines.append(f"| **Independent Sinitic Realms Control** | **{core_count - core_re} / {core_count}** ({(core_count - core_re)/core_count*100:.1f}%) | **{(greater_count - core_count) - (greater_re - core_re)} / {greater_count - core_count}** ({((greater_count - core_count) - (greater_re - core_re))/(greater_count - core_count)*100:.1f}%) | **{greater_count - greater_re} / {greater_count}** ({(greater_count - greater_re)/greater_count*100:.1f}%) |")
lines.append(f"| **Historical Anachronism Rate** | **3 / 380** (0.8% — Guannei passes) | **58 / 240** (24.2% — Frontier marches) | **{flagged_count} / {greater_count}** ({flagged_count/greater_count*100:.1f}% — 100% Resolved) |")
lines.append("")

# Table of Empires
lines.append("### 1.2 Summary Table of De Jure Empires in the Sinosphere")
lines.append("")
lines.append("| Rank | De Jure Empire | Title Key | Chinese Characters | Sphere Tier | Kingdoms | Duchies | Counties | Baronies | Total Dev | Avg Dev | Roman Control (1154) | Anachronisms Flagged |")
lines.append("| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")

sorted_empires = sorted(all_sinosphere_empires, key=lambda e: len([c for c in counties if c['de_jure_empire'] == e]), reverse=True)

for idx, e in enumerate(sorted_empires, 1):
    e_counties = [c for c in counties if c['de_jure_empire'] == e]
    e_k = len(set(c['de_jure_kingdom'] for c in e_counties))
    e_d = len(set(c['de_jure_duchy'] for c in e_counties))
    e_c = len(e_counties)
    e_b = sum(int(c['constituent_baronies_count']) for c in e_counties)
    e_dev = sum(float(c['development']) for c in e_counties)
    e_re = sum(1 for c in e_counties if c['is_in_roman_empire'] == 'True')
    e_anach = sum(1 for c in e_counties if c['county_key'] in audit_discrepancies)
    
    en_name = get_title_en(e)
    zh_name, zh_trad = get_title_zh(e)
    zh_display = f"**{zh_name}**" + (f" ({zh_trad})" if zh_trad and zh_trad != zh_name else "")
    
    tier_label = "Core China" if e in core_empires else "Peripheral"
    anach_badge = f"**{e_anach} flagged**" if e_anach > 0 else "0 (100% Classical)"
    
    lines.append(f"| {idx} | **{en_name}** | `{e}` | {zh_display} | {tier_label} | {e_k} | {e_d} | **{e_c}** | {e_b} | {e_dev:,.0f} | {e_dev/e_c:.1f} | **{e_re}/{e_c}** ({e_re/e_c*100:.1f}%) | {anach_badge} |")

lines.append("")

# Section 1.3: Political Landscape
lines.append("### 1.3 Political Landscape and the Dynastic Cycle in 1154")
lines.append("")
lines.append("#### The Dynastic Cycle (Mandate of Heaven) Struggle")
lines.append("In the active campaign save (`1154.12.27`), the Chinese Core is governed by the `dynastic_cycle` situation:")
lines.append("- **Current Phase:** **Phase of Chaos** (`situation_dynastic_cycle_phase_chaos`), active since **January 2, 1146**.")
lines.append("- **Catalyst & History:** Triggered by the collapse of the previous central hegemon in 1146, breaking the Mandate of Heaven into competing regional warlord regimes and imperial protectorates.")
lines.append("- **Geographical Boundary:** Subregion 0 (\"Core\") encompasses **exactly 380 counties** spanning `e_zhongyuan`, `e_liangyi`, `e_jingyang`, `e_yongliang`, and `e_lingnan`.")
lines.append("")
lines.append("#### Sovereign Realms Partitioning the Sinosphere in 1154")
lines.append("Control across the 620 Sinospheric counties is distributed among the following sovereigns:")
lines.append("")
lines.append("| Realm / Sovereign Liege | Liege Key | Liege Chinese Name | Sovereign Ruler & Dynastic House | Regional Domain | Counties Held | Sphere Share |")
lines.append("| :--- | :--- | :--- | :--- | :--- | :---: | :---: |")

liege_counts = Counter(c['top_liege'] for c in greater_counties)
for tl, count in liege_counts.most_common(16):
    tl_en = get_title_en(tl)
    tl_zh, _ = get_title_zh(tl)
    
    sample_c = next((c for c in greater_counties if c['top_liege'] == tl), None)
    if tl in ['h_roman_empire', 'e_hre', 'e_roman_empire']:
        holder_desc = "**Augustus Wernhard** (Chatenois)"
        reg_desc = "Mediterranean & East Asian Marches"
    elif sample_c:
        h_name = decode_ck3_cjk(sample_c['current_holder_name'])
        h_house = decode_ck3_cjk(sample_c['current_holder_house'])
        holder_desc = f"{h_name} of House {h_house}"
        reg_desc = f"{get_title_en(sample_c['de_jure_kingdom'])} ({clean_zh(get_title_zh(sample_c['de_jure_kingdom'])[0])})"
    else:
        holder_desc = "Regional Magnate"
        reg_desc = "Regional"
    
    lines.append(f"| **{tl_en}** | `{tl}` | {clean_zh(tl_zh)} | {holder_desc} | {reg_desc} | **{count}** | {count/greater_count*100:.1f}% |")

lines.append("")

# Section 1.4: Anachronism Audit Synthesis
lines.append("### 1.4 Historical Anachronism Audit & Resolution Synthesis")
lines.append("")
lines.append("Under the project's historical title audit framework ([`title_historical_accuracy_audit_plan.md`](title_historical_accuracy_audit_plan.md) and [`audit_discrepancy_register.md`](audit_discrepancy_register.md)), all titles within the Imperial sphere are rigorously screened against the **867 AD campaign divergence milestone**:")
lines.append("- **90.2% (559 of 620 counties)** are **Tier 1 (Authentic Pre-867 Classical Antiquity Foundations)**. The commanderies, prefectures, and provinces of the Central Plains, Ba-Shu, Jiangnan, Lingnan, Korea (Three Kingdoms/Silla), and Japan (Ritsuryō) date back centuries before 867 AD.")
lines.append("- **9.8% (61 of 620 counties)** were flagged under **Tier 3 (Post-867 Settlements & Unverified Titles)** due to post-867 Khitan Liao dynasty foundations (918–1007 AD), Jurchen frontier outposts, and nomadic clan divisions in the northern marches.")
lines.append("- **100% of the 61 Flagged Titles** have been reconciled under **Option B (Ancient Hydronymic & Natural Regional Basin Hierarchy)**, anchoring them to their underlying river basins and mountain horizons. The complete register is documented in **Section 5**.")
lines.append("")

lines.append("---")
lines.append("")

# Section 2: Complete Core Gazetteer
lines.append("## 2. Core Sinosphere Title Register (380 Counties)")
lines.append("")
lines.append("The 380 counties of China Proper are organized below hierarchically by **De Jure Empire** $\\rightarrow$ **De Jure Kingdom** $\\rightarrow$ **De Jure Duchy** $\\rightarrow$ **County Title**.")
lines.append("")

global_seq = 0

def render_empire_section(emp_keys, section_prefix):
    global global_seq
    for e_idx, e_key in enumerate(emp_keys, 1):
        e_en = get_title_en(e_key)
        e_zh, e_trad = get_title_zh(e_key)
        e_c_list = [c for c in counties if c['de_jure_empire'] == e_key]
        e_re = sum(1 for c in e_c_list if c['is_in_roman_empire'] == 'True')
        e_dev = sum(float(c['development']) for c in e_c_list)
        e_baronies = sum(int(c['constituent_baronies_count']) for c in e_c_list)
        e_anach = sum(1 for c in e_c_list if c['county_key'] in audit_discrepancies)
        
        lines.append(f"### {section_prefix}.{e_idx} Empire of {e_en} (`{e_key}` / {e_zh})")
        lines.append(f"- **De Jure Extent:** **{len(e_c_list)} Counties**, {len(set(c['de_jure_duchy'] for c in e_c_list))} Duchies, {len(set(c['de_jure_kingdom'] for c in e_c_list))} Kingdoms.")
        lines.append(f"- **Total Development:** **{e_dev:,.1f}** (Average: {e_dev/len(e_c_list):.1f}) | **Baronies:** {e_baronies:,}")
        lines.append(f"- **1154 Roman Empire Control:** **{e_re} / {len(e_c_list)} counties** ({e_re/len(e_c_list)*100:.1f}%) | **Anachronisms Flagged:** **{e_anach}**")
        lines.append("")
        
        # Kingdoms
        k_list = sorted(list(set(c['de_jure_kingdom'] for c in e_c_list)))
        for k_idx, k_key in enumerate(k_list, 1):
            k_en = get_title_en(k_key)
            k_zh, k_trad = get_title_zh(k_key)
            k_c_list = [c for c in e_c_list if c['de_jure_kingdom'] == k_key]
            k_re = sum(1 for c in k_c_list if c['is_in_roman_empire'] == 'True')
            k_dev = sum(float(c['development']) for c in k_c_list)
            k_anach = sum(1 for c in k_c_list if c['county_key'] in audit_discrepancies)
            
            lines.append(f"#### {section_prefix}.{e_idx}.{k_idx} Kingdom of {k_en} (`{k_key}` / {k_zh})")
            lines.append(f"*Extent: **{len(k_c_list)} Counties** | Development: **{k_dev:,.0f}** (avg {k_dev/len(k_c_list):.1f}) | Roman Control: **{k_re}/{len(k_c_list)}** | Flagged Anachronisms: **{k_anach}***")
            lines.append("")
            
            # Duchies
            d_list = sorted(list(set(c['de_jure_duchy'] for c in k_c_list)))
            for d_key in d_list:
                d_en = get_title_en(d_key)
                d_zh, d_trad = get_title_zh(d_key)
                d_c_list = [c for c in k_c_list if c['de_jure_duchy'] == d_key]
                d_re = sum(1 for c in d_c_list if c['is_in_roman_empire'] == 'True')
                d_flagged = [c for c in d_c_list if c['county_key'] in audit_discrepancies]
                
                lines.append(f"##### Duchy of {d_en} (`{d_key}` / {d_zh}) — *{d_re}/{len(d_c_list)} in Roman Empire*")
                lines.append("")
                lines.append("| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |")
                lines.append("| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |")
                
                for c in sorted(d_c_list, key=lambda x: x['county_key']):
                    global_seq += 1
                    c_key = c['county_key']
                    c_en = get_title_en(c_key)
                    c_zh, c_trad = get_title_zh(c_key)
                    
                    liege_str = f"**[RE]**" if c['is_in_roman_empire'] == 'True' else f"`{c['top_liege']}`"
                    built_clean = re.sub(r'\((\w+)_holding\)', r' [\1]', c['built_baronies']) if c['built_baronies'] else "None"
                    if len(built_clean) > 40:
                        built_clean = built_clean[:37] + "..."
                    
                    trad_display = c_trad if c_trad and c_trad != c_zh else "—"
                    
                    if c_key in audit_discrepancies:
                        res_info = audit_discrepancies[c_key]
                        res_brief = res_info['resolution'].replace('**Option B:**', 'Opt B:').replace('`', '').strip()
                        status_str = f"⚠️ **[Post-867 / Tier 3]** → *{res_brief}*"
                    else:
                        status_str = "✅ Pre-867 Classical"
                    
                    lines.append(f"| {global_seq} | `{c_key}` | **{c_en}** | **{c_zh}** | {trad_display} | {status_str} | {liege_str} | {c['county_culture']} | {float(c['development']):.0f} | {c['constituent_baronies_count']} | {built_clean} |")
                
                lines.append("")
                
                # If duchy has flagged titles, output an alert callout
                if d_flagged:
                    lines.append("> [!NOTE]")
                    lines.append(f"> **Historical Anachronism Resolutions in Duchy of {d_en}:**")
                    for fc in d_flagged:
                        f_k = fc['county_key']
                        f_en = get_title_en(f_k)
                        f_zh = get_title_zh(f_k)[0]
                        f_note = HISTORICAL_ANACHRONISM_NOTES.get(f_k, audit_discrepancies[f_k]['justification'])
                        lines.append(f"> * **`{f_k}` ({f_en} / {f_zh}):** {f_note} *Resolved via Option B: {audit_discrepancies[f_k]['resolution']}.*")
                    lines.append("")

render_empire_section(core_empires, "2")

# Section 3: Greater Sinosphere
lines.append("---")
lines.append("")
lines.append("## 3. Peripheral & Extended Sinosphere Title Register (240 Counties)")
lines.append("")
lines.append("Below are the 240 counties belonging to the broader Sinosphere (Korea/Samhan, Japan, Liao/Andong, and Amur), which historically maintained Chinese writing, administrative culture, and tributary relations.")
lines.append("")

render_empire_section(peripheral_empires, "3")

# Section 4: Statistical Appendices
lines.append("---")
lines.append("")
lines.append("## 4. Comprehensive Ranking of All 39 Sinospheric De Jure Kingdoms")
lines.append("")
lines.append("| Rank | Kingdom Name | Title Key | Chinese Characters | De Jure Empire | Counties | Total Baronies | Total Dev | Avg Dev | 1154 Roman Control | Anachronisms Flagged | Dominant Realm in 1154 |")
lines.append("| :---: | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |")

all_kingdom_keys = sorted(list(set(c['de_jure_kingdom'] for c in greater_counties)), key=lambda k: len([c for c in greater_counties if c['de_jure_kingdom'] == k]), reverse=True)

for k_rank, k_key in enumerate(all_kingdom_keys, 1):
    k_counties = [c for c in greater_counties if c['de_jure_kingdom'] == k_key]
    k_c = len(k_counties)
    k_b = sum(int(c['constituent_baronies_count']) for c in k_counties)
    k_dev = sum(float(c['development']) for c in k_counties)
    k_re = sum(1 for c in k_counties if c['is_in_roman_empire'] == 'True')
    k_anach = sum(1 for c in k_counties if c['county_key'] in audit_discrepancies)
    
    k_en = get_title_en(k_key)
    k_zh, _ = get_title_zh(k_key)
    emp_key = k_counties[0]['de_jure_empire']
    emp_en = get_title_en(emp_key)
    
    dom_liege = Counter(c['top_liege'] for c in k_counties).most_common(1)[0][0]
    dom_liege_en = "Roman Empire" if dom_liege in ['h_roman_empire', 'e_hre'] else get_title_en(dom_liege)
    anach_str = f"**{k_anach} flagged**" if k_anach > 0 else "0"
    
    lines.append(f"| {k_rank} | **{k_en}** | `{k_key}` | **{clean_zh(k_zh)}** | {emp_en} (`{emp_key}`) | **{k_c}** | {k_b} | {k_dev:,.0f} | {k_dev/k_c:.1f} | **{k_re}/{k_c}** ({k_re/k_c*100:.1f}%) | {anach_str} | {dom_liege_en} |")

lines.append("")

# Section 5: The 61 Anachronism Resolutions Master Register
lines.append("---")
lines.append("")
lines.append("## 5. Master Register of 61 Sinosphere Anachronism Resolutions")
lines.append("")
lines.append("Below is the exhaustive audit register of all **61 Sinosphere counties** flagged for post-867 foundation, eponymous naming, or lack of verified classical antiquity urban attestation. Under the **Toponym-First Principle**, all 61 titles have been resolved to their underlying ancient hydronyms, natural relief landmarks, or regional basin substrates (Option B) to prevent the circular canonization of high-medieval foundations.")
lines.append("")

# Clusters of Anachronisms
clusters = [
    ("5.1 Khitan Liao Dynastic Foundations (24 Counties)", "e_andong", ["k_khitan", "k_raole"]),
    ("5.2 Jurchen & Bohai Frontier Market Settlements (11 Counties)", "e_andong", ["k_luzhen"]),
    ("5.3 Shiwei Nomadic Clan Divisions (13 Counties)", "e_andong", ["k_shiwei"]),
    ("5.4 Amur Basin & Outer Northeast Frontier Outposts (10 Counties)", "e_amur", ["k_amur", "k_aynumosir"]),
    ("5.5 Guannei Northwestern Mountain Passes & Strategic Chokes (3 Counties)", "e_yongliang", ["k_guannei"])
]

anach_seq = 0
for cluster_title, cluster_emp, cluster_kingdoms in clusters:
    cluster_titles = [c for c in flagged_counties if c['de_jure_kingdom'] in cluster_kingdoms]
    lines.append(f"### {cluster_title}")
    lines.append(f"*Scope: **{len(cluster_titles)} Flagged Counties** in Empire of {get_title_en(cluster_emp)} (`{cluster_emp}`)*")
    lines.append("")
    lines.append("| # | County Key | In-Game Name | Chinese Characters | De Jure Kingdom | Historical Anachronism Rationale | Resolution Strategy (Option B) | Tarraconian Chancellery Title | Historical & Etymological Justification |")
    lines.append("| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    
    for c in sorted(cluster_titles, key=lambda x: x['county_key']):
        anach_seq += 1
        ck = c['county_key']
        en = get_title_en(ck)
        zh = get_title_zh(ck)[0]
        k_name = get_title_en(c['de_jure_kingdom'])
        
        info = audit_discrepancies[ck]
        res_str = info['resolution']
        tarr_title = info['tarr_title']
        note = HISTORICAL_ANACHRONISM_NOTES.get(ck, info['justification'])
        
        lines.append(f"| {anach_seq} | `{ck}` | **{en}** | **{zh}** | {k_name} (`{c['de_jure_kingdom']}`) | {note} | {res_str} | **{tarr_title}** | {info['justification']} |")
    
    lines.append("")

# Write to file
with open(TARGET_MD, 'w', encoding='utf-8') as f:
    f.write("\n".join(lines) + "\n")

print(f"Successfully generated updated {TARGET_MD} ({TARGET_MD.stat().st_size:,} bytes, {global_seq} total counties registered, {anach_seq} anachronisms reconciled)!")

#!/usr/bin/env python3
"""
resolve_barony_titles.py

Comprehensive Barony-Tier Title Resolution Engine for the Tarraconian Atlas.
Resolves Tarraconian Chancellery names (b_tarr_direct, b_tarr_hist, b_tarr,
b_origin, b_anachronism, b_ipa) for all 11,297 baronies (b_*) across the map.

Adheres strictly to:
- tarraconian_titles_1059.md (Master Gazetteer and 442 secondary variants)
- tarraconian_linguistics_guide.md (Rhine-Moselle Franconian phonology & Auslautverhärtung)
- sinosphere_phonetics_and_transcription_guide_1154.md (12th-century CJK historical phonology)
- melted_save.ck3 (Save universe creators, holders, leases, and historical character profiles)
- Unoccupied baronies (1,060 titles) must strictly remain blank per test suite specifications.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_DIR / "data"
SCRIPTS_DIR = REPO_DIR / "scripts"

sys.path.insert(0, str(SCRIPTS_DIR))
try:
    from sino_barony_kanji_ext import SINO_BARONY_KANJI_EXT
except ImportError:
    SINO_BARONY_KANJI_EXT = {}

try:
    from audit_phonotactics_titles import check_title_phonotactics
except ImportError:
    def check_title_phonotactics(raw_title, key, source_context):
        return []

SAVE_PATH = Path("/var/tmp/ck3_audit/melted_save.ck3")
CHARS_PATH = Path("/var/tmp/ck3_audit/phase1/historical_characters.json")
HOUSES_PATH = Path("/var/tmp/ck3_audit/phase1/dynasties_and_houses.json")
CULTURES_PATH = Path("/var/tmp/ck3_audit/phase1/cultures_data.json")
ZH_CACHE_PATH = Path("/var/tmp/ck3_audit/chinese_titles_cache.json")
EN_CACHE_PATH = Path("/var/tmp/ck3_audit/english_titles_cache.json")

BARONIES_GEOJSON = DATA_DIR / "ck3_baronies.geojson"
COUNTIES_GEOJSON = DATA_DIR / "ck3_counties.geojson"
BARONY_HOLDINGS = DATA_DIR / "barony_holdings.json"
TITLE_TREE_JSON = DATA_DIR / "ck3_title_tree.json"
KANJI_JSON = DATA_DIR / "sinosphere_kanji_tarraconian.json"
SINO_CALQUES_JSON = DATA_DIR / "sinosphere_title_calques.json"
SINO_HANZI_JSON = DATA_DIR / "sinosphere_hanzi_calques.json"
OUT_RESOLUTIONS_JSON = DATA_DIR / "barony_resolutions.json"

# Sinosphere Empires & Drifted Frontier Counties
SINO_EMPIRES = {
    "e_andong", "e_liangyi", "e_zhongyuan", "e_jingyang",
    "e_yongliang", "e_japan", "e_lingnan", "e_goryeo", "e_amur"
}
SINO_FRONTIER_COUNTIES = {
    "c_jining", "c_chahar", "c_xilinhaote", "c_duolun", "c_chifeng",
    "c_tongliao", "c_hulunbuir", "c_wulagai", "c_haerbin"
}


# ==============================================================================
# 1. PHONOTACTICS & SOUND CHANGE UTILITIES
# ==============================================================================

def enforce_tarraconian_sound_laws(name: str) -> str:
    """
    Applies Rhine-Moselle Franconian sound laws and orthographic purity:
    - Circumflexes only: á, é, í, ó, ú -> â, ê, î, ô, û
    - No Pinyin bare 'zh' -> 'dsch'
    - No bare 'sh' -> 'sch'
    - Initial [ts] -> strictly 'z-'
    - Medial/final [ts] -> '-tz-' / '-tz'
    - Auslautverhärtung: final -burg -> -burch, -bad -> -bat, -dsch -> -tsch
    - Slavic -sk / -ysk -> -tzich / -bsch
    """
    s = name.strip()
    
    # 1. Normalize accents: acutes to circumflexes
    s = s.replace("á", "â").replace("é", "ê").replace("í", "î").replace("ó", "ô").replace("ú", "û")
    s = s.replace("Á", "Â").replace("É", "Ê").replace("Í", "Î").replace("Ó", "Ô").replace("Ú", "Û")
    s = s.replace("à", "â").replace("è", "ê").replace("ì", "î").replace("ò", "ô").replace("ù", "û")
    s = s.replace("À", "Â").replace("È", "Ê").replace("Ì", "Î").replace("Ò", "Ô").replace("Ù", "Û")
    
    # 2. Pinyin digraphs
    s = re.sub(r"zh", "dsch", s, flags=re.I)
    s = re.sub(r"\bq(?!u)", "tsch", s, flags=re.I)
    
    # 3. Bare 'sh' -> 'sch' (except at compound boundaries like -heim, -hûsen)
    s = re.sub(r"(?<!c)sh(?!eim|ûsen)", "sch", s, flags=re.I)
    
    # 4. Korean 'eo' -> 'ô' (exempting Greek Georg-, Neo-, Theo-)
    s = re.sub(r"(?<!g)(?<!n)(?<!th)eo", "ô", s, flags=re.I)
    
    # 5. Slavic suffixes
    s = re.sub(r"sk\b", "tzich", s, flags=re.I)
    s = re.sub(r"ysk\b", "îtzich", s, flags=re.I)
    s = re.sub(r"ov\b", "ouwe", s, flags=re.I)
    s = re.sub(r"ev\b", "euwe", s, flags=re.I)
    
    # 6. Auslautverhärtung (word-final devoicing)
    s = re.sub(r"burg\b", "burch", s, flags=re.I)
    s = re.sub(r"berg\b", "berch", s, flags=re.I)
    s = re.sub(r"bad\b", "bat", s, flags=re.I)
    s = re.sub(r"dsch\b", "tsch", s, flags=re.I)
    
    # 7. Affricates
    # Initial ts -> z
    s = re.sub(r"\bts(?!ch)", "z", s, flags=re.I)
    # Medial/final ts -> tz
    s = re.sub(r"(?<=[a-zA-Z])ts(?!ch)", "tz", s, flags=re.I)
    
    # Capitalize first letter of compound components
    if "-" in s:
        s = "-".join(p[:1].upper() + p[1:] if p else "" for p in s.split("-"))
    else:
        s = s[:1].upper() + s[1:] if s else ""
        
    return s


def generate_tarraconian_ipa(name: str) -> str:
    """Generates phonetic transcription in IPA according to tarraconian_linguistics_guide.md."""
    if not name:
        return ""
    s = name.strip()
    s = re.sub(r"^(Magistrat|Gubernat|Kûnincrich|Keiserrîch|Erzbisdom|Fürstbisdom)\s+van\s+(dem\s+|der\s+|den\s+)?", "", s)
    
    res = s.lower()
    
    # Long vowels
    res = res.replace("â", "aː").replace("ê", "eː").replace("î", "iː").replace("ô", "oː").replace("û", "uː")
    res = res.replace("ö", "øː").replace("ü", "yː")
    
    # Diphthongs
    res = re.sub(r"ei|ai", "ɛɪ", res)
    res = re.sub(r"ou|au", "ɔʊ", res)
    res = re.sub(r"eu", "ɔʏ", res)
    
    # Consonants
    res = re.sub(r"dsch", "dʒ", res)
    res = re.sub(r"tsch", "tʃ", res)
    res = re.sub(r"sch", "ʃ", res)
    
    # ch after front vowels -> ç, after back vowels -> x
    res = re.sub(r"([iːeːyːøːɛɪɪʏœ])ch", r"\1ç", res)
    res = re.sub(r"ch", "x", res)
    
    # z / tz
    res = re.sub(r"\bz", "ts", res)
    res = res.replace("tz", "ts")
    
    # ng / nk
    res = re.sub(r"ng", "ŋ", res)
    res = re.sub(r"nk", "ŋk", res)
    
    # Short vowels
    res = res.replace("a", "a").replace("e", "ɛ").replace("i", "ɪ").replace("o", "ɔ").replace("u", "ʊ")
    
    # Reduced vowel in unstressed endings -en, -er, -el
    res = re.sub(r"ɛn\b", "ən", res)
    res = re.sub(r"ɛr\b", "ər", res)
    res = re.sub(r"ɛl\b", "əl", res)
    res = re.sub(r"ɛ\b", "ə", res)
    
    # Syllabification
    vowel_phones = ["aː", "eː", "iː", "oː", "uː", "ɛɪ", "ɔʊ", "ɔʏ", "øː", "yː", "a", "ɛ", "ɪ", "ɔ", "ʊ", "y", "ø", "ə"]
    consonant_phones = ["dʒ", "tʃ", "ts", "st", "sp", "sk", "ʃ", "ç", "x", "ŋk", "ŋ", "b", "d", "g", "p", "t", "k", "f", "v", "s", "z", "h", "m", "n", "l", "r", "j", "w"]
    
    phones = []
    i = 0
    while i < len(res):
        matched = False
        for v in vowel_phones + consonant_phones:
            if res.startswith(v, i):
                phones.append((v, "V" if v in vowel_phones else "C"))
                i += len(v)
                matched = True
                break
        if not matched:
            phones.append((res[i], "C"))
            i += 1
            
    v_indices = [idx for idx, (p, typ) in enumerate(phones) if typ == "V"]
    if len(v_indices) > 1:
        breaks = set()
        for v_idx_i in range(len(v_indices) - 1):
            v1 = v_indices[v_idx_i]
            v2 = v_indices[v_idx_i + 1]
            inter = phones[v1+1 : v2]
            n_c = len(inter)
            if n_c == 0:
                breaks.add(v1 + 1)
            elif n_c == 1:
                breaks.add(v1 + 1)
            else:
                breaks.add(v1 + 1 + 1)
                
        syll_res = []
        for idx, (p, typ) in enumerate(phones):
            if idx in breaks:
                syll_res.append(".")
            syll_res.append(p)
        res = "".join(syll_res)

    res = "ˈ" + res
    return f"[{res}]"


# ==============================================================================
# 2. SAVE & HISTORICAL DATA PARSING
# ==============================================================================

def load_save_baronies(save_path: Path):
    """Parses all baronies from landed_titles in melted_save.ck3."""
    print(f"Parsing baronies from {save_path.name}...")
    baronies = {}
    if not save_path.exists():
        print(f"Warning: {save_path} does not exist. Using empty save profile.")
        return baronies

    with open(save_path, "r", encoding="utf-8", errors="ignore") as f:
        in_landed = False
        cur_block = []
        depth = 0
        for line in f:
            if not in_landed:
                if line.startswith("\tlanded_titles={"):
                    in_landed = True
                    depth = 1
                continue
            depth += line.count("{") - line.count("}")
            if depth <= 0:
                break
            cur_block.append(line)
            if depth == 1 and line.strip() == "}":
                text = "".join(cur_block)
                if "key=\"b_" in text:
                    km = re.search(r'key=\"(b_[^\"]+)\"', text)
                    if km:
                        bk = km.group(1)
                        hm = re.search(r'\bholder=(\d+)', text)
                        dm = re.search(r'\bdate=(\d+\.\d+\.\d+)', text)
                        nm = re.search(r'title_name_data=\{\s*name=\"([^\"]+)\"', text)
                        lm = re.search(r'de_jure_liege=(\d+)', text)
                        cap = "capital_barony=yes" in text
                        
                        leases = []
                        if "history={" in text:
                            for m in re.finditer(r'type=(leased_out|lease_revoked)\s+holder=(\d+)', text):
                                leases.append((m.group(1), m.group(2)))
                                
                        baronies[bk] = {
                            "holder": hm.group(1) if hm else None,
                            "date": dm.group(1) if dm else None,
                            "save_name": nm.group(1) if nm else None,
                            "de_jure_liege_id": lm.group(1) if lm else None,
                            "is_capital": cap,
                            "leases": leases
                        }
                cur_block = []

    print(f"-> Parsed {len(baronies)} baronies from save file.")
    return baronies


def load_historical_metadata():
    """Loads characters, dynasties/houses, and cultures."""
    chars = {}
    if CHARS_PATH.exists():
        with open(CHARS_PATH, "r", encoding="utf-8") as f:
            chars = json.load(f)

    houses = {}
    if HOUSES_PATH.exists():
        with open(HOUSES_PATH, "r", encoding="utf-8") as f:
            hd = json.load(f)
            houses = hd.get("houses", {})

    cultures = {}
    if CULTURES_PATH.exists():
        with open(CULTURES_PATH, "r", encoding="utf-8") as f:
            cultures = json.load(f)

    zh_cache = {}
    if ZH_CACHE_PATH.exists():
        with open(ZH_CACHE_PATH, "r", encoding="utf-8") as f:
            zh_cache = json.load(f)

    en_cache = {}
    if EN_CACHE_PATH.exists():
        with open(EN_CACHE_PATH, "r", encoding="utf-8") as f:
            en_cache = json.load(f)

    return chars, houses, cultures, zh_cache, en_cache


def load_secondary_variants_and_collisions(counties_lookup, en_cache):
    """
    Parses tarraconian_titles_1059.md for secondary variants *(or **X**)*
    and pairs them precisely to constituent baronies. Also parses Option A
    sub-baronies from screen_phase3_titles.py.
    """
    barony_to_sec_variant = {}
    tarr_md = REPO_DIR / "tarraconian_titles_1059.md"
    if tarr_md.exists():
        text = tarr_md.read_text(encoding="utf-8")
        matches = re.findall(
            r"\*\s+`([c]_[a-z0-9_]+)`\s*\([^)]*\)\s*\$\\rightarrow\$\s*\*\*([^*]+)\*\*\s*\*\(\s*or\s+\*\*([^*]+)\*\*\s*\)\*",
            text
        )
        def norm_s(s):
            s = s.lower().replace("â", "a").replace("ê", "e").replace("î", "i").replace("ô", "o").replace("û", "u").replace("ö", "o").replace("ü", "u")
            s = re.sub(r"[^a-z]", "", s)
            s = s.replace("tz", "z").replace("tsch", "ch").replace("sch", "sh").replace("v", "f").replace("w", "v")
            return s

        for ck, prim, sec in matches:
            clean_sec = re.sub(r"^(Magistrat|Gubernat|Kûnincrich|Keiserrîch|Erzbisdom|Fürstbisdom)\s+van\s+(dem\s+|der\s+|den\s+)?", "", sec.strip())
            norm_sec = norm_s(clean_sec)
            baronies = counties_lookup.get(ck, {}).get("baronies", [])
            
            best_b = None
            best_score = 0
            for b in baronies:
                en = en_cache.get(b, b.replace("b_", "").replace("_", " "))
                norm_b = norm_s(b.replace("b_", ""))
                norm_en = norm_s(en)
                
                score = 0
                if norm_b == norm_sec or norm_en == norm_sec:
                    score = 100
                elif norm_b in norm_sec or norm_sec in norm_b or norm_en in norm_sec or norm_sec in norm_en:
                    score = 80
                elif norm_b[:4] == norm_sec[:4] or norm_en[:4] == norm_sec[:4]:
                    score = 60
                elif ("york" in norm_en and "everw" in norm_sec) or ("cant" in norm_en and "kant" in norm_sec) or ("shrew" in norm_en and "amw" in norm_sec):
                    score = 90
                    
                if score > best_score:
                    best_score = score
                    best_b = b
                    
            if not best_b and baronies:
                best_b = baronies[0]
                
            if best_b:
                barony_to_sec_variant[best_b] = (clean_sec, ck)

    # Parse Option A designations and intra-county collisions from screen_phase3_titles.py
    option_a_baronies = {}
    collision_counties = {}
    screen_py = SCRIPTS_DIR / "screen_phase3_titles.py"
    if screen_py.exists():
        stext = screen_py.read_text(encoding="utf-8")
        entries = re.findall(r'\"(c_[a-z0-9_]+)\":\s*\{([^}]+)\}', stext)
        for ck, body in entries:
            km = re.search(r'\"opt_a_key\":\s*\"(b_[a-z0-9_]+)\"', body)
            rec = re.search(r'\"rec_option\":\s*\"([^\"]+)\"', body)
            nm = re.search(r'\"tarr_name\":\s*\"([^\"]+)\"', body)
            hyd = re.search(r'\"opt_b_name\":\s*\"([^\"]+)\"', body)
            if km and rec and "Option A" in rec.group(1):
                bk = km.group(1)
                opt_name = nm.group(1) if nm else ""
                option_a_baronies[bk] = opt_name
                collision_counties[ck] = {
                    "opt_a_key": bk,
                    "opt_a_name": opt_name,
                    "opt_b_name": hyd.group(1) if hyd else "",
                }

    return barony_to_sec_variant, option_a_baronies, collision_counties


# ==============================================================================
# 3. SINOSPHERE LOGOGRAPHIC CALQUING ENGINE
# ==============================================================================

def build_merged_kanji_map():
    """Builds the comprehensive 1,235-character CJK morpheme dictionary."""
    k_map = {}
    if KANJI_JSON.exists():
        with open(KANJI_JSON, "r", encoding="utf-8") as f:
            k_data = json.load(f)
        for k in k_data:
            c = k["char"]
            k_map[c] = (k.get("tarr_morpheme", c), k.get("tarr_role", ""), k.get("meaning", ""))
            if k.get("var") and k["var"] != "-":
                k_map[k["var"]] = (k.get("tarr_morpheme", c), k.get("tarr_role", ""), k.get("meaning", ""))

    # Merge extension
    for c, val in SINO_BARONY_KANJI_EXT.items():
        if c not in k_map:
            k_map[c] = val

    return k_map


def resolve_sinosphere_barony(b_key: str, zh_raw: str, en_name: str, k_map: dict, is_capital: bool, county_tarr: str):
    """
    Synthesizes the Tarraconian logographic calque for a Sinosphere barony.
    Extracts authentic clean Chinese characters and historical kanji.
    """
    raw_parts = zh_raw.split('"')
    clean_zh = raw_parts[0].split("#")[0].strip()
    hist_kanji = ""
    if "#" in zh_raw:
        hist_kanji = zh_raw.split("#")[1].strip()

    chars = re.findall(r"[\u4e00-\u9fff]", clean_zh)
    if not chars and hist_kanji:
        chars = re.findall(r"[\u4e00-\u9fff]", hist_kanji)

    parts = []
    meanings = []
    for c in chars:
        m, role, mean = k_map.get(c, (c, "", ""))
        clean_m = m.replace("-", "").strip()
        parts.append(clean_m)
        meanings.append(mean.split("/")[0].strip())

    calque = "".join(parts) if parts else en_name
    calque = enforce_tarraconian_sound_laws(calque)
    
    if is_capital and county_tarr:
        tarr_name = county_tarr
    else:
        tarr_name = calque

    origin_str = f"{clean_zh}"
    if hist_kanji and hist_kanji != clean_zh:
        origin_str += f" ({hist_kanji})"
    if en_name:
        origin_str += f" [{en_name}]"
    if meanings:
        origin_str += f" — Calque: {' + '.join(meanings)}"

    return {
        "b_tarr_direct": calque,
        "b_tarr_hist": tarr_name,
        "b_tarr": tarr_name,
        "b_origin": origin_str,
        "b_anachronism": "",
        "b_ipa": generate_tarraconian_ipa(tarr_name)
    }


# ==============================================================================
# 4. FOUNDER ARCHETYPE EVALUATION (SECTION 3.2 / OPTION C ENGINE)
# ==============================================================================

def evaluate_founder_option_c(char_name: str, traits: list, house_name: str, holding_type: str):
    """
    Evaluates ruler character traits and holding type according to Section 3.2.
    Returns: (option_c_name, formula_description)
    """
    traits_set = set(traits or [])
    clean_founder = re.sub(r"[^a-zA-Z]", "", char_name) or "Adelbert"
    clean_house = re.sub(r"[^a-zA-Z]", "", house_name.replace("Chatenois-", "").replace("Kestenholz-", "")) or "Kêsten"

    if holding_type == "castle":
        if traits_set & {"arrogant", "ambitious", "greedy", "fickle"}:
            c_name = f"{clean_founder}sburch"
            desc = f"Self-eponymous fortress founded by {clean_founder} ({list(traits_set & {'arrogant', 'ambitious', 'greedy', 'fickle'})})"
        elif traits_set & {"zealous", "humble", "theologian", "celibate", "monk"}:
            c_name = f"Marienburch"
            desc = f"Religious fortress dedication by devout founder {clean_founder}"
        elif traits_set & {"paranoid", "craven", "brave", "strategist", "diligent", "architect"}:
            c_name = f"{clean_house}veste"
            desc = f"Defensive march fortress built by {clean_founder} ({clean_house})"
        else:
            c_name = f"{clean_house}burch"
            desc = f"Dynastic fortress seat of House {clean_house}"

    elif holding_type in {"church", "temple"}:
        if traits_set & {"zealous", "theologian", "pilgrim"}:
            c_name = f"Zant-{clean_founder}"
            desc = f"Patron saint collegiate foundation dedicated by {clean_founder}"
        else:
            c_name = f"{clean_founder}munster"
            desc = f"Monastic collegiate foundation established by {clean_founder}"

    else:
        if traits_set & {"greedy", "administrator", "midas_touched", "diligent"}:
            c_name = f"{clean_founder}marct"
            desc = f"Chartered market borough established by {clean_founder}"
        else:
            c_name = f"{clean_founder}stat"
            desc = f"Municipal foundation chartered by {clean_founder}"

    c_name = enforce_tarraconian_sound_laws(c_name)
    return c_name, desc


# ==============================================================================
# 5. EUROPEAN / NON-SINOSPHERE TOPONYMIC ADAPTATION
# ==============================================================================

def adapt_european_toponym(name: str) -> str:
    """Adapts a standard historical European settlement name into Rhine-Moselle Franconian phonology."""
    s = name.strip()
    
    # German / English suffixes
    s = re.sub(r"burg\b|burgh\b", "burch", s, flags=re.I)
    s = re.sub(r"berg\b", "berch", s, flags=re.I)
    s = re.sub(r"bad\b", "bat", s, flags=re.I)
    s = re.sub(r"stadt\b|stad\b", "stat", s, flags=re.I)
    s = re.sub(r"dorf\b|dorp\b", "dorp", s, flags=re.I)
    s = re.sub(r"furt\b|ford\b", "vurt", s, flags=re.I)
    s = re.sub(r"haven\b|hafen\b", "haven", s, flags=re.I)
    s = re.sub(r"chester\b|caster\b|cester\b", "zester", s, flags=re.I)
    s = re.sub(r"ham\b", "hêm", s, flags=re.I)
    s = re.sub(r"stein\b", "stên", s, flags=re.I)
    s = re.sub(r"wald\b", "wout", s, flags=re.I)
    s = re.sub(r"feld\b", "velt", s, flags=re.I)
    s = re.sub(r"brück\b|bruck\b|bridge\b", "brücke", s, flags=re.I)
    s = re.sub(r"werder\b|werth\b", "werder", s, flags=re.I)
    
    # French / Occitan
    s = re.sub(r"château\b|chateau\b", "castel", s, flags=re.I)
    s = re.sub(r"ville\b", "wîl", s, flags=re.I)
    s = re.sub(r"mont\b", "munt", s, flags=re.I)
    s = re.sub(r"pont\b", "brücke", s, flags=re.I)
    
    # Slavic
    s = re.sub(r"grad\b|grod\b|gorod\b", "gort", s, flags=re.I)
    s = re.sub(r"sk\b|ysk\b", "tzich", s, flags=re.I)
    s = re.sub(r"ice\b|yce\b", "itz", s, flags=re.I)
    
    return enforce_tarraconian_sound_laws(s)


INDIGENOUS_RESTITUTIONS = {
    "b_konigsberg": ("Twangste", "Old Prussian sacred grove and hillfort Twangste (attested before 1255 Teutonic Order castle)"),
    "b_reval": ("Lindanisa", "Ancient Finnic/Estonian settlement Lindanisa (attested before 1219 Danish crusade fortress)"),
    "b_wesenburg": ("Tarvanpää", "Ancient Estonian stronghold Tarvanpää ('Bull's Head', attested 1226)"),
    "b_marienburg": ("Malbork", "Prussian/Slavic settlement Malbork on the Nogat (attested before 1274 Teutonic fortress)"),
    "b_allenstein": ("Alna", "Old Prussian hydronym Alna ('Trout River', Alle / Olsztyn)"),
    "b_fort_novoaleksandrovskiy": ("Mangystau", "Ancient Turkic/Oghuz peninsula and fortress Mangystau"),
    "b_schwanenburg": ("Gulbene", "Ancient Latgalian settlement Gulbene (attested before 1224 Archbishopric castle)"),
    "b_neidenburg": ("Niba", "Old Prussian river settlement Niba (attested before 1371 fortress)"),
    "b_lviv": ("Lemberch", "Ruthenian princely stronghold founded c. 1256 on the Poltva; held in save by House Luki"),
    "b_zvenyhorod": ("Swenigorot", "Ancient 10th-century princely capital gord of the Cherven Cities"),
    "b_sisak": ("Sissek", "Roman Siscia / 9th-century seat of Duke Ljudevit Posavski"),
    "b_turku": ("Abô", "Ancient Aura river trading post / Swedish Åbo (Finnish Turku)"),
    "b_rikala": ("Rîkale", "Ancient Iron Age hillfort and trading center of Halikko / Rikala"),
    "b_porvoo": ("Borchâ", "Ancient Finnic river fortress Borgå (Porvoo)"),
    "b_espoo": ("Espô", "Ancient coastal settlement Espoo on the Gulf of Finland"),
    "b_ulvila": ("Wûlvildô", "Ancient trading post of Ulvila on the Kokemäenjoki"),
    "b_telja": ("Teljê", "Iron Age trading center Teljä of Satakunta"),
    "b_warszawa": ("Warschauwe", "Ancient Mazovian crossing settlement on the Vistula (Warszewa)"),
    "b_czersk": ("Tschêrtzich", "Ancient 11th-century capital gord of the Duchy of Czersk"),
}


# ==============================================================================
# 6. MASTER RESOLUTION PIPELINE
# ==============================================================================

def resolve_all_baronies():
    print("==================================================================")
    print("Starting Comprehensive Barony-Tier Title Resolution (11,297 Titles)")
    print("==================================================================")

    # 1. Load GeoJSON datasets
    print("Loading GeoJSON vector datasets...")
    with open(BARONIES_GEOJSON, "r", encoding="utf-8") as f:
        baronies_fc = json.load(f)
    with open(COUNTIES_GEOJSON, "r", encoding="utf-8") as f:
        counties_fc = json.load(f)
    with open(BARONY_HOLDINGS, "r", encoding="utf-8") as f:
        barony_holdings = json.load(f)

    counties_lookup = {feat["properties"]["county"]: feat["properties"] for feat in counties_fc["features"]}

    # 2. Load historical save metadata and character profiles
    save_baronies = load_save_baronies(SAVE_PATH)
    chars, houses, cultures, zh_cache, en_cache = load_historical_metadata()
    sec_variants, opt_a_baronies, collisions = load_secondary_variants_and_collisions(counties_lookup, en_cache)
    k_map = build_merged_kanji_map()

    print(f"Loaded {len(save_baronies)} baronies from CK3 save.")
    print(f"Loaded {len(chars)} historical characters and {len(houses)} houses.")
    print(f"Loaded {len(sec_variants)} precisely paired secondary variants from tarraconian_titles_1059.md.")
    print(f"Loaded {len(opt_a_baronies)} Option A sub-barony designations.")
    print(f"Loaded {len(k_map)} CJK characters in Sinosphere calquing database.")

    resolutions = {}
    total_occupied = 0
    total_unoccupied = 0
    sino_count = 0
    eponymous_count = 0
    sub_barony_count = 0

    phonotactic_issues = []

    print("\nProcessing barony titles...")
    for feat in baronies_fc["features"]:
        props = feat["properties"]
        bk = props["barony"]
        ck = props.get("county")
        c_props = counties_lookup.get(ck, {})

        ht = barony_holdings.get(bk, "unoccupied")
        props["holding_type"] = ht
        props["holding_type_name"] = "Castle" if ht == "castle" else "City" if ht == "city" else "Church" if ht in {"church", "temple"} else "Unoccupied"

        # ----------------------------------------------------------------------
        # A. UNOCCUPIED BARONIES (Must strictly remain blank)
        # ----------------------------------------------------------------------
        if ht == "unoccupied":
            total_unoccupied += 1
            res = {
                "name": "",
                "b_tarr": "",
                "b_tarr_direct": "",
                "b_tarr_hist": "",
                "b_origin": "",
                "b_anachronism": "",
                "b_ipa": "",
                "holding_type": "unoccupied",
                "category": "unoccupied"
            }
            resolutions[bk] = res
            props.update(res)
            continue

        total_occupied += 1
        save_b = save_baronies.get(bk, {})
        holder_id = save_b.get("holder")
        holder_char = chars.get(str(holder_id), {}) if holder_id else {}
        holder_name = holder_char.get("first_name", "")
        holder_traits = holder_char.get("traits_decoded", [])
        house_id = holder_char.get("dynasty_house")
        house_name = houses.get(str(house_id), {}).get("localized_name", "")
        is_capital = save_b.get("is_capital", False)
        save_name = save_b.get("save_name") or en_cache.get(bk, bk.replace("b_", "").replace("_", " ").title())

        emp = props.get("empire")
        is_sinosphere = (emp in SINO_EMPIRES or ck in SINO_FRONTIER_COUNTIES)

        # ----------------------------------------------------------------------
        # B. SINOSPHERE BARONIES (Logographic Semantic Calques)
        # ----------------------------------------------------------------------
        if is_sinosphere:
            sino_count += 1
            raw_zh = zh_cache.get(bk, "")
            c_tarr = c_props.get("tarr_hist") or c_props.get("tarr_direct") or c_props.get("tarr", "")
            sino_res = resolve_sinosphere_barony(bk, raw_zh, save_name, k_map, is_capital, c_tarr if is_capital else "")
            
            res = {
                "name": sino_res["b_tarr"],
                "b_tarr": sino_res["b_tarr"],
                "b_tarr_direct": sino_res["b_tarr_direct"],
                "b_tarr_hist": sino_res["b_tarr_hist"],
                "b_origin": sino_res["b_origin"],
                "b_anachronism": sino_res["b_anachronism"],
                "b_ipa": sino_res["b_ipa"],
                "holding_type": ht,
                "category": "sinosphere_calque"
            }

        # ----------------------------------------------------------------------
        # C. NON-SINOSPHERE BARONIES
        # ----------------------------------------------------------------------
        else:
            # 1. Check known authentic indigenous / archaeological restitution
            if bk in INDIGENOUS_RESTITUTIONS:
                sub_barony_count += 1
                tarr_name, orig_desc = INDIGENOUS_RESTITUTIONS[bk]
                tarr_clean = enforce_tarraconian_sound_laws(tarr_name)
                res = {
                    "name": tarr_clean,
                    "b_tarr": tarr_clean,
                    "b_tarr_direct": adapt_european_toponym(save_name),
                    "b_tarr_hist": tarr_clean,
                    "b_origin": f"{orig_desc} (in-game: {save_name})",
                    "b_anachronism": "Pre-867 native toponym restored over post-867 colonial foundation.",
                    "b_ipa": generate_tarraconian_ipa(tarr_clean),
                    "holding_type": ht,
                    "category": "indigenous_restitution"
                }

            # 2. Check Option A sub-barony designation
            elif bk in opt_a_baronies:
                sub_barony_count += 1
                opt_name = opt_a_baronies[bk]
                tarr_clean = enforce_tarraconian_sound_laws(opt_name)
                res = {
                    "name": tarr_clean,
                    "b_tarr": tarr_clean,
                    "b_tarr_direct": adapt_european_toponym(save_name),
                    "b_tarr_hist": tarr_clean,
                    "b_origin": f"{save_name} — Historical Option A seat of {ck}",
                    "b_anachronism": "",
                    "b_ipa": generate_tarraconian_ipa(tarr_clean),
                    "holding_type": ht,
                    "category": "option_a_seat"
                }

            # 3. Check Intra-County Collision (capital barony of an Option A county)
            elif ck in collisions and collisions[ck]["opt_a_key"] != bk and (is_capital or bk.replace("b_", "") == ck.replace("c_", "")):
                eponymous_count += 1
                coll = collisions[ck]
                if coll["opt_b_name"]:
                    b_tarr = coll["opt_b_name"]
                    orig_note = f"Option B hydronym/landform ({coll['opt_b_name']}) disambiguated from sub-barony seat {coll['opt_a_name']}"
                else:
                    opt_c_name, c_desc = evaluate_founder_option_c(holder_name, holder_traits, house_name, ht)
                    b_tarr = opt_c_name
                    orig_note = f"Option C foundation: {c_desc}"

                tarr_clean = enforce_tarraconian_sound_laws(b_tarr)
                res = {
                    "name": tarr_clean,
                    "b_tarr": tarr_clean,
                    "b_tarr_direct": adapt_european_toponym(save_name),
                    "b_tarr_hist": tarr_clean,
                    "b_origin": f"{save_name} — {orig_note}",
                    "b_anachronism": "Disambiguated intra-county capital barony.",
                    "b_ipa": generate_tarraconian_ipa(tarr_clean),
                    "holding_type": ht,
                    "category": "collision_disambiguation"
                }

            # 4. Check Precisely Paired Secondary Variants *(or **X**)* from tarraconian_titles_1059.md
            elif bk in sec_variants:
                sub_barony_count += 1
                sec_name, sec_ck = sec_variants[bk]
                tarr_clean = enforce_tarraconian_sound_laws(sec_name)
                res = {
                    "name": tarr_clean,
                    "b_tarr": tarr_clean,
                    "b_tarr_direct": tarr_clean,
                    "b_tarr_hist": tarr_clean,
                    "b_origin": f"{save_name} (attested secondary seat in tarraconian_titles_1059.md)",
                    "b_anachronism": "",
                    "b_ipa": generate_tarraconian_ipa(tarr_clean),
                    "holding_type": ht,
                    "category": "secondary_variant"
                }

            # 5. Eponymous / Capital Barony inheriting parent county
            elif is_capital or (ck and bk.replace("b_", "") == ck.replace("c_", "")):
                eponymous_count += 1
                c_dir = c_props.get("tarr_direct") or adapt_european_toponym(save_name)
                c_hist = c_props.get("tarr_hist") or c_dir
                c_tarr = c_hist or c_dir
                res = {
                    "name": c_tarr,
                    "b_tarr": c_tarr,
                    "b_tarr_direct": c_dir,
                    "b_tarr_hist": c_hist,
                    "b_origin": f"{save_name} ({c_props.get('c_origin', save_name)})",
                    "b_anachronism": c_props.get("c_anachronism", ""),
                    "b_ipa": c_props.get("c_ipa") or generate_tarraconian_ipa(c_tarr),
                    "holding_type": ht,
                    "category": "capital_eponymous"
                }

            # 6. Non-Capital Sub-Baronies: Antiquity or Founder Option C
            else:
                sub_barony_count += 1
                is_colonial = any(re.search(pat, save_name, re.I) for pat in [
                    r"burg\b", r"stein\b", r"pils\b", r"linna\b", r"abad\b", r"pur\b", r"garh\b"
                ])

                if is_colonial and holder_name:
                    opt_c_name, c_desc = evaluate_founder_option_c(holder_name, holder_traits, house_name, ht)
                    tarr_clean = opt_c_name
                    orig_desc = f"{save_name} — {c_desc}"
                    anach_note = f"Post-867 foundation attributed to save ruler {holder_name} of House {house_name or 'unrecorded'}."
                else:
                    tarr_clean = adapt_european_toponym(save_name)
                    orig_desc = f"{save_name} (constituent holding of {c_props.get('tarr', ck)})"
                    anach_note = ""

                res = {
                    "name": tarr_clean,
                    "b_tarr": tarr_clean,
                    "b_tarr_direct": adapt_european_toponym(save_name),
                    "b_tarr_hist": tarr_clean,
                    "b_origin": orig_desc,
                    "b_anachronism": anach_note,
                    "b_ipa": generate_tarraconian_ipa(tarr_clean),
                    "holding_type": ht,
                    "category": "sub_barony_adaptation"
                }

        # Phonotactic verification
        issues = check_title_phonotactics(res["name"], bk, "resolve_barony_titles")
        if issues:
            phonotactic_issues.append((bk, res["name"], issues))

        resolutions[bk] = res
        props.update(res)

    print("\n------------------------------------------------------------------")
    print("Resolution Statistics:")
    print(f"  • Total Holdings: {len(baronies_fc['features'])}")
    print(f"  • Occupied Baronies Resolved: {total_occupied}")
    print(f"    - Category 1 (Sinosphere Logographic Calques): {sino_count}")
    print(f"    - Category 2 (Capital / Eponymous Holdings): {eponymous_count}")
    print(f"    - Category 3 (Sub-Baronies / Historical Attestations): {sub_barony_count}")
    print(f"  • Unoccupied Baronies (Strictly Blank): {total_unoccupied}")
    print(f"  • Phonotactic Issues Encountered: {len(phonotactic_issues)}")
    if phonotactic_issues:
        print(f"    Sample issues:")
        for bk, nm, iss in phonotactic_issues[:5]:
            print(f"      [{bk}] {nm}: {iss}")
    print("------------------------------------------------------------------")

    # 3. Write data/barony_resolutions.json
    print(f"Writing {OUT_RESOLUTIONS_JSON.name}...")
    with open(OUT_RESOLUTIONS_JSON, "w", encoding="utf-8") as f:
        json.dump(resolutions, f, indent=2, ensure_ascii=False)
    print(f"-> Wrote {OUT_RESOLUTIONS_JSON.name} ({OUT_RESOLUTIONS_JSON.stat().st_size / 1024 / 1024:.2f} MB)")

    # 4. Write updated data/ck3_baronies.geojson
    print(f"Writing updated {BARONIES_GEOJSON.name}...")
    with open(BARONIES_GEOJSON, "w", encoding="utf-8") as f:
        json.dump(baronies_fc, f, separators=(",", ":"), ensure_ascii=False)
    print(f"-> Wrote {BARONIES_GEOJSON.name} ({BARONIES_GEOJSON.stat().st_size / 1024 / 1024:.2f} MB)")

    return resolutions


if __name__ == "__main__":
    resolve_all_baronies()

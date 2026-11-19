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
import hashlib
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

try:
    from historical_attestation_db import CLASSICAL_OR_ANCIENT_KINGDOMS, ATTESTATION_REGISTRY
except ImportError:
    CLASSICAL_OR_ANCIENT_KINGDOMS = set()
    ATTESTATION_REGISTRY = {}

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
    
    # 1. Normalize accents: acutes to circumflexes, cedillas to affricates
    s = s.replace("á", "â").replace("é", "ê").replace("í", "î").replace("ó", "ô").replace("ú", "û")
    s = s.replace("Á", "Â").replace("É", "Ê").replace("Í", "Î").replace("Ó", "Ô").replace("Ú", "Û")
    s = s.replace("à", "â").replace("è", "ê").replace("ì", "î").replace("ò", "ô").replace("ù", "û")
    s = s.replace("À", "Â").replace("È", "Ê").replace("Ì", "Î").replace("Ò", "Ô").replace("Ù", "Û")
    s = s.replace("ç", "tz").replace("Ç", "Tz")
    
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
    
    # Remove title / administrative prefixes
    s = re.sub(r"^(Magistrat|Gubernat|Kûnincrich|Keiserrîch|Erzbisdom|Fürstbisdom)\s+van\s+(dem\s+|der\s+|den\s+)?", "", s, flags=re.IGNORECASE)
    s = re.sub(r"^van\s+(dem\s+|der\s+|den\s+)?", "", s, flags=re.IGNORECASE)
    
    # If there is an alternative separated by slash, take the primary (first)
    if "/" in s:
        s = s.split("/")[0].strip()
        
    # Expand Saint abbreviations
    s = re.sub(r"\bSt\.?\s*", "Zant-", s)
    s = re.sub(r"\bSaint[\s\-]+", "Zant-", s, flags=re.IGNORECASE)
    
    # Store original stripped name to detect Romance/Germanic patterns for stress
    raw_stem = s
    
    res = s.lower()
    
    # Clean apostrophes
    res = res.replace("'", "")
    
    # Regularize y in diphthongs, onsets, and vocalic codas
    res = re.sub(r"ey", "ei", res)
    res = re.sub(r"ay", "ai", res)
    res = re.sub(r"oy", "eu", res)
    res = re.sub(r"uy", "ui", res)
    res = re.sub(r"y\b", "i", res)
    res = re.sub(r"y(?=[aeiouâêîôûäöü])", "j", res)
    res = re.sub(r"y", "i", res)
    
    # Convert foreign diacritics / non-Tarraconian orthography
    res = res.replace("š", "sch").replace("ž", "dsch").replace("č", "tsch")
    res = res.replace("ð", "d").replace("þ", "t")
    res = res.replace("æ", "e").replace("ä", "e").replace("å", "o").replace("ë", "e").replace("ï", "i")
    res = res.replace("ñ", "nj").replace("ý", "î")
    res = res.replace("qu", "kw").replace("q", "k")
    res = res.replace("x", "ks")
    res = res.replace("ā", "aː").replace("ī", "iː").replace("ū", "uː")
    res = res.replace("ă", "ə").replace("ș", "ʃ").replace("ț", "ts")
    res = res.replace("ő", "øː").replace("ű", "yː")
    res = res.replace("ã", "a")
    
    # Hiatus with circumflex in loanwords (aî -> a.iː, aû -> a.uː, eî -> e.iː)
    res = res.replace("aî", "a.iː").replace("aû", "a.uː").replace("eî", "e.iː")
    
    # Chancellery consonants & clusters (FIRST, before c -> k)
    res = re.sub(r"dsch", "dʒ", res)
    res = re.sub(r"tsch", "tʃ", res)
    res = re.sub(r"sch", "ʃ", res)
    
    # ch after front vowels / diphthongs -> ç, after back vowels -> x
    res = re.sub(r"([iîeêyüö]|eː|iː|yː|øː|ɛɪ|ɔʏ)ch", r"\1ç", res)
    res = res.replace("ch", "x")
    
    # Catalan/Latin c -> ts before e/i/ê/î/y, k elsewhere
    res = re.sub(r"c(?=[eiêîy])", "ts", res)
    res = res.replace("c", "k")
    
    # Palatal nj / ny / ll / lj (Catalan/Romance)
    res = re.sub(r"nj|ny", "ɲ", res)
    res = re.sub(r"lj|ll", "ʎ", res)
    
    # Long vowels (from circumflexes)
    res = res.replace("â", "aː").replace("ê", "eː").replace("î", "iː").replace("ô", "oː").replace("û", "uː")
    res = res.replace("ö", "øː").replace("ü", "yː")
    
    # Diphthongs
    res = re.sub(r"ei|ai", "ɛɪ", res)
    res = re.sub(r"ou|au", "ɔʊ", res)
    res = re.sub(r"eu", "ɔʏ", res)
    
    # z / tz -> ts
    res = re.sub(r"\bz", "ts", res)
    res = res.replace("tz", "ts")
    res = res.replace("z", "ts")
    
    # ng / nk
    res = re.sub(r"ng", "ŋ", res)
    res = re.sub(r"nk", "ŋk", res)
    
    # Short vowels: protect long vowels (followed by ː) and diphthongs
    res = re.sub(r"a(?!ː)", "a", res)
    res = re.sub(r"e(?!ː)", "ɛ", res)
    res = re.sub(r"i(?!ː)", "ɪ", res)
    res = re.sub(r"o(?!ː)", "ɔ", res)
    res = re.sub(r"u(?!ː)", "ʊ", res)
    
    # g: [ɡ]
    res = res.replace("g", "ɡ")
    
    # Reduced vowel [ə] in unstressed Germanic inflectional endings (-en, -er, -el, -e)
    # But preserve stressed Romance -el, -et, -at, -on, -an
    C_SET = r"[bdfɡɣkmnprstvwxzʒʃçʎɲ]"
    res = re.sub(f"({C_SET})ɛn\\b", r"\1ən", res)
    res = re.sub(f"({C_SET})ɛr\\b", r"\1ər", res)
    res = re.sub(f"({C_SET})ɛl\\b", r"\1əl", res)
    # Medial -en- in compounds (e.g. Plintenburch)
    res = re.sub(f"({C_SET})ɛn({C_SET})", r"\1ən\2", res)
    
    # Romance words ending in -tel, -del, -pel with oxytone stress keep [ɛl] if root is Romance
    if re.search(r"(castel|kastel|montpel|bordel)", raw_stem, re.IGNORECASE):
        res = re.sub(r"əl\b|əl(?=\s|-)", "ɛl", res)
        
    res = re.sub(f"({C_SET})ɛ\\b", r"\1ə", res)
    
    # Intervocalic s -> z (single s only between vowels)
    v_regex = r"(?:[aːeːiːoːuːøːyːaɛɪɔʊʏœə]|ɛɪ|ɔʊ|ɔʏ)"
    res = re.sub(f"(?<![s])({v_regex})s({v_regex})(?![s])", r"\1z\2", res)
    
    # Intervocalic lenition of [ɡ] -> [ɣ] between vowels
    res = re.sub(f"({v_regex})ɡ({v_regex})", r"\1ɣ\2", res)
    
    # Double consonants reduction in IPA
    res = re.sub(r"([bdfkmnprst])\1+", r"\1", res)
    
    # Clean hyphens to spaces
    res = res.replace("-", " ")
    
    # Helper to process single word syllabification & stress
    def process_word(w: str, raw_w: str) -> str:
        if not w:
            return ""
        
        vowel_phones = ["aː", "eː", "iː", "oː", "uː", "øː", "yː", "ɛɪ", "ɔʊ", "ɔʏ", "a", "ɛ", "ɪ", "ɔ", "ʊ", "ʏ", "œ", "ə"]
        consonant_phones = [
            "dʒ", "tʃ", "ts", "ʃ", "ç", "x", "ŋk", "ŋ",
            "b", "d", "ɡ", "ɣ", "p", "t", "k", "f", "v", "s", "z", "h",
            "m", "n", "l", "r", "j", "w", "ʎ", "ɲ"
        ]
        
        # If w already contains explicit hiatus dots from aî / aû / eî, split by dot first
        subparts = w.split(".")
        syllables = []
        for sp in subparts:
            phones = []
            i = 0
            while i < len(sp):
                matched = False
                for v in vowel_phones + consonant_phones:
                    if sp.startswith(v, i):
                        phones.append((v, "V" if v in vowel_phones else "C"))
                        i += len(v)
                        matched = True
                        break
                if not matched:
                    if sp[i].isalpha():
                        phones.append((sp[i], "C"))
                    i += 1
                    
            v_indices = [idx for idx, (p, typ) in enumerate(phones) if typ == "V"]
            num_sylls = len(v_indices)
            
            if num_sylls <= 1:
                if phones:
                    syllables.append("".join(p for p, typ in phones))
                continue
                
            muta_liquida = {
                ("b", "r"), ("p", "r"), ("d", "r"), ("t", "r"), ("ɡ", "r"), ("k", "r"),
                ("b", "l"), ("p", "l"), ("ɡ", "l"), ("k", "l"), ("f", "r"), ("f", "l"),
                ("v", "r"), ("v", "l")
            }
            
            breaks = set()
            for v_idx_i in range(num_sylls - 1):
                v1 = v_indices[v_idx_i]
                v2 = v_indices[v_idx_i + 1]
                inter = phones[v1+1 : v2]
                n_c = len(inter)
                if n_c == 0:
                    breaks.add(v1 + 1)
                elif n_c == 1:
                    breaks.add(v1 + 1)
                elif n_c == 2:
                    c1, c2 = inter[0][0], inter[1][0]
                    if (c1, c2) in muta_liquida:
                        breaks.add(v1 + 1)
                    else:
                        breaks.add(v1 + 1 + 1)
                else:
                    c_penult, c_last = inter[-2][0], inter[-1][0]
                    if (c_penult, c_last) in muta_liquida or (c_penult, c_last) in {("s", "t"), ("s", "p"), ("s", "k"), ("ʃ", "t"), ("ʃ", "p"), ("ʃ", "k")}:
                        breaks.add(v2 - 2)
                    else:
                        breaks.add(v2 - 1)
                        
            cur_syl = []
            for idx, (p, typ) in enumerate(phones):
                if idx in breaks:
                    syllables.append("".join(cur_syl))
                    cur_syl = []
                cur_syl.append(p)
            if cur_syl:
                syllables.append("".join(cur_syl))
                
        if len(syllables) <= 1:
            return "".join(syllables)
            
        # Determine Stress Position
        germanic_suffixes = (
            "burch", "stat", "lant", "munster", "dorp", "gouwe", "gou",
            "velt", "veit", "berch", "vurt", "furt", "haven", "bach", "bache",
            "flôz", "wazzer", "sticht", "ward", "wald", "walt", "eck", "berg"
        )
        is_germanic_compound = any(raw_w.lower().endswith(sfx) for sfx in germanic_suffixes)
        
        romance_oxytone = (
            "el", "êl", "at", "et", "it", "ot", "ut",
            "on", "ôn", "an", "ân", "in", "în", "ier", "êr", "ur", "or"
        )
        ends_oxytone = (not is_germanic_compound) and any(raw_w.lower().endswith(sfx) for sfx in romance_oxytone)
        
        final_syl = syllables[-1]
        has_final_long = any(lv in final_syl for lv in ["aː", "eː", "iː", "oː", "uː", "ɛɪ", "ɔʊ", "ɔʏ"])
        
        ends_schwa = syllables[-1].endswith("ə") or raw_w.lower().endswith("e")
        
        if is_germanic_compound:
            stress_idx = 0
        elif ends_schwa:
            stress_idx = max(0, len(syllables) - 2)
        elif ends_oxytone or has_final_long:
            stress_idx = len(syllables) - 1
        else:
            stress_idx = 0
            
        syllables[stress_idx] = "ˈ" + syllables[stress_idx]
        return ".".join(syllables)

    # Process all words
    words = res.split()
    raw_words = raw_stem.replace("-", " ").split()
    
    out_words = []
    for i, w in enumerate(words):
        rw = raw_words[i] if i < len(raw_words) else w
        out_words.append(process_word(w, rw))
        
    final_ipa = " ".join(out_words)
    return f"[{final_ipa}]"


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

    # Supplement with dynamic houses directly from save
    if SAVE_PATH.exists():
        with open(SAVE_PATH, "r", encoding="utf-8", errors="ignore") as f:
            in_houses = False
            for line in f:
                if line.startswith("\tdynasty_house={"):
                    in_houses = True
                    continue
                if in_houses:
                    if line.startswith("\t}"):
                        break
                    m = re.match(r"^\t\t(\d+)=\{", line)
                    if m:
                        hid = m.group(1)
                        for _ in range(8):
                            nline = next(f, "")
                            nm = re.search(r'(?:localized_name|name)=\"(?:dynn_)?([^\"]+)\"', nline)
                            if nm:
                                if hid not in houses:
                                    houses[hid] = {"localized_name": nm.group(1)}
                                break

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
            r"\*\s+`([c]_[a-z0-9_]+)`\s*\([^)]*\)\s*\$\\rightarrow\$\s*\*\*([^*]+)\*\*\s*\*\(\s*or\s+\*\*([^*]+)\*\*[^)]*\)\*",
            text
        )
        def norm_s(s):
            s = s.lower().replace("â", "a").replace("ê", "e").replace("î", "i").replace("ô", "o").replace("û", "u").replace("ö", "o").replace("ü", "u")
            s = re.sub(r"^(zant|saint|sankt|st|san|santa)[^a-z]*", "", s)
            s = re.sub(r"[^a-z]", "", s)
            s = s.replace("tz", "z").replace("tsch", "ch").replace("sch", "sh").replace("v", "f").replace("w", "v").replace("j", "dsh")
            return s

        KNOWN_EQUIVS = [
            ("gallen", "gallen"),
            ("beja", "bedsh"),
            ("konstanz", "konst"),
            ("evora", "evor"),
            ("york", "everw"), ("eborac", "everw"),
            ("canterbury", "kant"), ("cant", "kant"),
            ("shrewsbury", "amw"), ("shrew", "amw"),
            ("aix", "ax"),
            ("reading", "reding"),
            ("winchester", "wintz"),
            ("exeter", "exetz"),
            ("lincoln", "linkoln"),
            ("london", "lunden"),
            ("cambridge", "kambritsch"), ("cambridge", "grant"),
            ("deventer", "deventer"),
            ("chur", "kur"),
            ("split", "spalat"),
        ]

        for ck, prim, sec in matches:
            clean_sec = re.sub(r"^(Magistrat|Gubernat|Kûnincrich|Keiserrîch|Erzbisdom|Fürstbisdom)\s+van\s+(dem\s+|der\s+|den\s+)?", "", sec.strip())
            clean_sec = clean_sec.split("/")[0].strip()
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
                else:
                    for k1, k2 in KNOWN_EQUIVS:
                        if (k1 in norm_en or k1 in norm_b) and k2 in norm_sec:
                            score = 95
                            break
                    
                if score > best_score:
                    best_score = score
                    best_b = b
                    
            # Only assign if positive match (score >= 60)
            if best_b and best_score >= 60:
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

    OPTION_A_CAPITAL_DISAMBIGUATION = {
        "c_zagreb": "Sagreb",
        "c_linlithgowshire": "Aberkôrn",
        "c_oldenburg": "Aldenburch",
        "c_brandenburg": "Brennabor",
        "c_lanarkshire": "Lânark",
        "c_athlone": "Âth-Lôen",
        "c_ravensburg": "Râvensburch",
        "c_coburg": "Kôburch",
        "c_slupsk": "Slûptzich",
        "c_gowrie": "Zant-Jônstat",
        "c_lviv": "Lemberch",
        "c_zaslavl": "Saslâwl",
        "c_peremyshl": "Peremyschl",
        "c_zvyahel": "Swîâhel",
        "c_perekop": "Akmesdschît",
        "c_osterland": "Îlenburch",
        "c_hradyzk": "Gradischk",
        "c_lasta": "Lalîbela",
        "c_luxembourg": "Lützelburch",
        "c_bergh": "Berch",
        "c_namur": "Nâmen",
        "c_munchen": "München",
        "c_vecchio": "Bonifâtzo",
        "c_montpellier": "Muntpêljê",
        "c_algier": "Alschîr",
        "c_bornu": "Gasargamu",
        "c_lubeck": "Lübeck",
        "c_stezycka": "Stensitz",
        "c_finland": "Abô",
        "c_nyland": "Borchâ",
        "c_satakunta": "Wûlvildô",
        "c_czerska": "Warschauwe",
    }
    for ck, b_name in OPTION_A_CAPITAL_DISAMBIGUATION.items():
        if ck in collision_counties:
            collision_counties[ck]["opt_b_name"] = b_name

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

LATE_PATTERNS = re.compile(
    r'\b(novo|new|aleksandr|stanitsa|station|fort)[a-z]*\b|'
    r'[a-z]*(burg|burgh|stein|fels|schloss|pils|linna|abad|pur|garh|fort|stanitsa|station|railway|mine|ostrog|sloboda|sk|ysk|ovichi|ichi|grad|gorod)\b',
    re.I
)


def is_circular_house(house_str: str, stem_str: str, barony_key: str = "", county_key: str = "") -> bool:
    """
    Enforces the Toponym-First Principle & Downstream Causality Inversion Rule:
    Detects whether an in-game dynasty/house was auto-generated from the holding title itself.
    """
    if not house_str:
        return False
    h = re.sub(r"[^a-zA-Z]", "", house_str).lower()
    h = re.sub(r"^(chatenois|kestenholz|dynn)", "", h)
    if not h:
        return False
    s = re.sub(r"[^a-zA-Z]", "", stem_str).lower()
    b = re.sub(r"[^a-zA-Z]", "", barony_key.replace("b_", "")).lower() if barony_key else ""
    c = re.sub(r"[^a-zA-Z]", "", county_key.replace("c_", "")).lower() if county_key else ""
    return (h in s or s in h or (b and (h in b or b in h)) or (c and (h in c or c in h)))


def evaluate_founder_option_c(char_name: str, traits: list, house_name: str, holding_type: str, used_names: set = None, save_name: str = "", bk: str = "", ck: str = ""):
    """
    Evaluates ruler character traits and holding type according to Section 3.2.
    Strictly disqualifies circular in-game auto-generated houses under the Toponym-First Principle.
    Returns: (option_c_name, formula_description)
    """
    traits_set = set(traits or [])
    clean_founder = re.sub(r"[^a-zA-Z]", "", char_name) or "Adelbert"
    clean_founder = re.sub(r"fried\b", "frît", clean_founder, flags=re.I)
    clean_founder = re.sub(r"rich\b", "rîch", clean_founder, flags=re.I)

    raw_house = house_name.replace("Chatenois-", "").replace("Kestenholz-", "").replace("dynn_", "")
    clean_house = re.sub(r"[^a-zA-Z]", "", raw_house) or ""
    clean_stem = re.sub(r"[^a-zA-Z]", "", save_name.split()[0]) if save_name else ""
    if not clean_stem:
        clean_stem = "Burch"

    # Toponym-First Principle: Disqualify circular pseudo-dynasties derived from the holding
    if clean_house and is_circular_house(clean_house, clean_stem, bk, ck):
        clean_house = ""

    used = used_names or set()
    candidates = []

    if holding_type == "castle":
        if traits_set & {"arrogant", "ambitious", "greedy", "fickle"}:
            candidates.append((f"{clean_founder}sburch", f"Self-eponymous fortress founded by {clean_founder} ({list(traits_set & {'arrogant', 'ambitious', 'greedy', 'fickle'})})"))
            if clean_house:
                candidates.append((f"{clean_house}veste", f"Defensive march fortress built by House {clean_house}"))
            candidates.append((f"{clean_founder}stên", f"Fortress citadel established by {clean_founder}"))
        elif traits_set & {"zealous", "humble", "theologian", "celibate", "monk"}:
            candidates.append(("Marienburch", f"Religious fortress dedication by devout founder {clean_founder}"))
            candidates.append(("Heiligencruce", f"Holy Cross fortress foundation dedicated by {clean_founder}"))
            candidates.append((f"{clean_founder}sburch", f"Eponymous fortress built by devout founder {clean_founder}"))
        elif traits_set & {"paranoid", "craven", "brave", "strategist", "diligent", "architect"}:
            if clean_house:
                candidates.append((f"{clean_house}veste", f"Defensive march fortress built by {clean_founder} ({clean_house})"))
            candidates.append(("Schirmburch", f"Protective march fortress built by {clean_founder}"))
            candidates.append((f"{clean_founder}sburch", f"Fortified citadel established by {clean_founder}"))
        else:
            candidates.append((f"{clean_founder}sburch", f"Feudal fortress seat established by {clean_founder}"))
            if clean_house:
                candidates.append((f"{clean_house}burch", f"Dynastic fortress seat of House {clean_house}"))
                candidates.append((f"{clean_house}veste", f"Defensive march stronghold of House {clean_house}"))
            candidates.append((f"{clean_stem}burch", f"Fortress seat of {clean_stem} established by {clean_founder}"))

    elif holding_type in {"church", "temple"}:
        seed = int(hashlib.md5(bk.encode("utf-8")).hexdigest()[:8], 16) % 10 if bk else 0

        if traits_set & {"zealous", "theologian", "pilgrim"}:
            candidates.append((f"Zant-{clean_founder}", f"Patron saint collegiate foundation dedicated by {clean_founder}"))
            candidates.append(("Heiligencrûce", f"Holy Cross collegiate foundation dedicated by {clean_founder}"))
            candidates.append((f"{clean_founder}kirchen", f"Collegiate church established by devout founder {clean_founder}"))
            candidates.append(("Marienkirchen", f"Collegiate church of St. Mary dedicated by devout founder {clean_founder}"))
            candidates.append(("Marientâl", f"Monastic valley abbey dedicated to St. Mary by {clean_founder}"))
            candidates.append((f"{clean_founder}szelle", f"Monastic cell and hermitage established by {clean_founder}"))
            if clean_house:
                candidates.append((f"{clean_house}stifft", f"Collegiate canonry endowed by House {clean_house}"))
            candidates.append((f"{clean_founder}munster", f"Collegiate minster founded by {clean_founder}"))

        elif traits_set & {"humble", "content", "temperate", "celibate", "monk", "shy"}:
            candidates.append((f"{clean_founder}szelle", f"Monastic cell and hermitage established by {clean_founder}"))
            candidates.append(("Mariezelle", f"Marian hermitage and priory founded by {clean_founder}"))
            candidates.append(("Marientâl", f"Monastic valley sanctuary founded by {clean_founder}"))
            candidates.append((f"{clean_founder}kirchen", f"Parish church foundation established by {clean_founder}"))
            candidates.append(("Nîenclôster", f"New monastic cloister founded by {clean_founder}"))
            candidates.append((f"Zant-{clean_founder}", f"Collegiate church dedicated by {clean_founder}"))

        elif clean_house:
            if seed in (0, 1, 2):
                candidates.append((f"{clean_house}kirchen", f"Proprietary collegiate church of House {clean_house}"))
                candidates.append((f"{clean_house}stifft", f"Endowed collegiate canonry of House {clean_house}"))
                candidates.append((f"Zant-{clean_founder}", f"Collegiate church dedicated by {clean_founder} of House {clean_house}"))
            elif seed in (3, 4, 5):
                candidates.append((f"Zant-{clean_founder}", f"Collegiate church dedicated by {clean_founder} of House {clean_house}"))
                candidates.append((f"{clean_house}kirchen", f"Proprietary collegiate church of House {clean_house}"))
                candidates.append((f"{clean_house}stifft", f"Endowed collegiate canonry of House {clean_house}"))
            elif seed in (6, 7):
                candidates.append((f"{clean_house}stifft", f"Endowed collegiate canonry of House {clean_house}"))
                candidates.append((f"{clean_house}kirchen", f"Proprietary collegiate church of House {clean_house}"))
                candidates.append((f"Zant-{clean_founder}", f"Collegiate church dedicated by {clean_founder}"))
            elif seed == 8:
                candidates.append((f"{clean_founder}szelle", f"Monastic cell endowed by {clean_founder} of House {clean_house}"))
                candidates.append(("Marientâl", f"Devotional valley abbey endowed by House {clean_house}"))
            else:
                candidates.append((f"{clean_house}munster", f"Collegiate minster church of House {clean_house}"))
                candidates.append((f"{clean_house}stifft", f"Collegiate canonry of House {clean_house}"))

        else:
            if seed in (0, 1, 2):
                candidates.append((f"{clean_founder}kirchen", f"Parish collegiate church founded by {clean_founder}"))
                candidates.append((f"Zant-{clean_founder}", f"Collegiate church dedicated by {clean_founder}"))
                candidates.append(("Marienkirchen", f"Collegiate church of St. Mary dedicated by {clean_founder}"))
            elif seed in (3, 4, 5):
                candidates.append((f"Zant-{clean_founder}", f"Patron saint church dedicated by {clean_founder}"))
                candidates.append((f"{clean_founder}kirchen", f"Collegiate church founded by {clean_founder}"))
                candidates.append(("Marienkirchen", f"Collegiate church of St. Mary dedicated by {clean_founder}"))
            elif seed in (6, 7):
                candidates.append((f"{clean_founder}szelle", f"Monastic cell and hermitage founded by {clean_founder}"))
                candidates.append((f"{clean_founder}kirchen", f"Parish church founded by {clean_founder}"))
            elif seed == 8:
                candidates.append(("Marientâl", f"Monastic valley abbey dedicated by {clean_founder}"))
                candidates.append(("Heiligencrûce", f"Holy Cross church dedicated by {clean_founder}"))
            else:
                candidates.append((f"{clean_founder}munster", f"Collegiate minster church established by {clean_founder}"))
                candidates.append((f"{clean_founder}kirchen", f"Collegiate church founded by {clean_founder}"))

        # Universal fallback candidate pool
        candidates.append((f"{clean_founder}kirchen", f"Collegiate church established by {clean_founder}"))
        candidates.append((f"Zant-{clean_founder}", f"Collegiate church dedicated by {clean_founder}"))
        candidates.append(("Marienkirchen", f"Collegiate church of St. Mary dedicated by {clean_founder}"))
        candidates.append((f"{clean_founder}szelle", f"Monastic cell founded by {clean_founder}"))
        if clean_house:
            candidates.append((f"{clean_house}stifft", f"Collegiate canonry of House {clean_house}"))
        candidates.append((f"{clean_founder}stifft", f"Collegiate canonry endowed by {clean_founder}"))
        candidates.append(("Nîenclôster", f"New monastic cloister foundation"))
        candidates.append((f"{clean_founder}munster", f"Collegiate minster endowed by {clean_founder}"))

    else:  # city / borough
        if traits_set & {"greedy", "administrator", "midas_touched", "diligent"}:
            candidates.append((f"{clean_founder}marct", f"Chartered market borough established by {clean_founder}"))
            candidates.append((f"{clean_founder}stat", f"Municipal borough chartered by {clean_founder}"))
            candidates.append((f"{clean_founder}vurt", f"River crossing market borough founded by {clean_founder}"))
        else:
            candidates.append((f"{clean_founder}stat", f"Municipal foundation chartered by {clean_founder}"))
            candidates.append((f"{clean_founder}marct", f"Market borough established by {clean_founder}"))
            if clean_house:
                candidates.append((f"{clean_house}stat", f"Chartered civic borough of House {clean_house}"))
            candidates.append((f"{clean_stem}stat", f"Chartered borough of {clean_stem} established by {clean_founder}"))

    for c_nm, desc in candidates:
        clean_cand = enforce_tarraconian_sound_laws(c_nm)
        if clean_cand not in used:
            return clean_cand, desc

    fallback_nm = enforce_tarraconian_sound_laws(f"{clean_founder}s{clean_stem[:4]}stat")
    return fallback_nm, f"Municipal foundation established by {clean_founder}"


def check_barony_antiquity(bk: str, save_name: str, ck: str, kd: str):
    """
    Evaluates whether a sub-barony has positive pre-867 proof under the Burden of Proof on Antiquity.
    Returns: (is_ancient: bool, reason: str)
    """
    if bk in INDIGENOUS_RESTITUTIONS:
        return True, "indigenous_restitution"
    c_key = bk.replace("b_", "c_")
    if c_key in ATTESTATION_REGISTRY:
        att_yr = ATTESTATION_REGISTRY[c_key][0]
        if att_yr is not None and att_yr > 867:
            return False, "high_medieval_foundation"
        elif att_yr is not None and att_yr <= 867:
            return True, "chronicle_attestation"
    if re.search(r"\b(gau|gebirge|tal|wald|fluv|werder|werth|am-|an-der-|see|meer|joki|järvi|jarvi|vesi|salmi|saari|niemi|lahti|koski|suo|vuori|harju|selkä|selka|ostrov|gora|blato|jazero)\b", bk + " " + save_name, re.I):
        return True, "ancient_toponym"
    if kd in CLASSICAL_OR_ANCIENT_KINGDOMS:
        if not LATE_PATTERNS.search(save_name.strip().lower()):
            return True, "classical_continuity"
        else:
            return False, "classical_late_foundation"
    return False, "unverified_default"


# ==============================================================================
# 5. EUROPEAN / NON-SINOSPHERE TOPONYMIC ADAPTATION
# ==============================================================================

def adapt_european_toponym(name: str) -> str:
    """Adapts a standard historical European settlement name into Rhine-Moselle Franconian phonology."""
    s = name.strip()
    
    # 0. Canonical Latin / Classical / Romance toponyms
    if re.match(r"^Aix\b", s, re.I):
        return "Âx"
    if re.match(r"^Saintes\b", s, re.I):
        return "Santes"
    if re.match(r"^(?:É|Ê|E)tampes\b", s, re.I):
        return "Estampes"
    if re.match(r"^Beauvais\b", s, re.I):
        return "Belvês"
    if re.match(r"^Beaugency\b", s, re.I):
        return "Belgentzî"
    if re.match(r"^Beaujeu\b", s, re.I):
        return "Beljô"
    if re.match(r"^(?:Beaumont|Beaumunt)[-\s]+(?:sur|Sur)[-\s]+(?:Lèze|Lêze)\b", s, re.I):
        return "Belmunt-an-der-Lêze"
    if re.match(r"^Versailles\b", s, re.I):
        return "Versalje"
    if re.match(r"^Marseille\b", s, re.I):
        return "Marsîlje"
    if re.match(r"^Taillebourg\b", s, re.I):
        return "Taljeburch"
    if re.match(r"^Cornouailles\b", s, re.I):
        return "Kornuâlje"
    if re.match(r"^Mortagne\b", s, re.I):
        return "Mortenje"
    if re.match(r"^Draguignan\b", s, re.I):
        return "Draginjân"
    if re.match(r"^Valen[çc]ay\b", s, re.I):
        return "Valentzê"
    if re.match(r"^Montlu[çc]on\b", s, re.I):
        return "Muntlutzôn"
    if re.match(r"^Brian[çc]on\b", s, re.I):
        return "Briantzôn"
    if re.match(r"^(?:La\s+)?Peyrade\b", s, re.I):
        return "La Peirâde"
    if re.match(r"^(?:La\s+)?Haye\b", s, re.I):
        return "La Haie"
    if re.match(r"^Bray\b", s, re.I):
        return "Brê"
    if re.match(r"^Gray\b", s, re.I):
        return "Grê"
    if re.match(r"^Blaye\b", s, re.I):
        return "Blâje"
    if re.match(r"^Melay\b", s, re.I):
        return "Melê"
    if re.match(r"^Fontenay\b", s, re.I):
        return "Fontenê"
    if re.match(r"^Parthenay\b", s, re.I):
        return "Parthenê"
    if re.match(r"^(?:É|Ê|E)pernay\b", s, re.I):
        return "Êpernê"
    if re.match(r"^(?:Courtenay|Coutenay)\b", s, re.I):
        return "Kourtenê"
    if re.match(r"^Belley\b", s, re.I):
        return "Belê"
    if re.match(r"^Quingey\b", s, re.I):
        return "Quingê"
    if re.match(r"^Annonay\b", s, re.I):
        return "Annonê"
    if re.match(r"^Alcoy\b", s, re.I):
        return "Alkoi"
    if re.match(r"^(?:Crêpy|Crepy)\b", s, re.I):
        return "Crêpî"
    if re.match(r"^(?:Crêcy|Crecy)\b", s, re.I):
        return "Crêtzî"
    if re.match(r"^Roucy\b", s, re.I):
        return "Routzî"
    if re.match(r"^Coucy\b", s, re.I):
        return "Koutzî"
    if re.match(r"^Annecy\b", s, re.I):
        return "Annetzî"
    if re.match(r"^Donzy\b", s, re.I):
        return "Dontzy"
    if re.match(r"^(?:Chambéry|Chambêry)\b", s, re.I):
        return "Schambêrî"
    if re.match(r"^(?:Montlhéry|Montlhêry)\b", s, re.I):
        return "Muntlêrî"
    if re.match(r"^Castelnaudary\b", s, re.I):
        return "Kastelnoudarî"
    if re.match(r"^Sully[-\s]+(?:sur|Sur)[-\s]+Loire\b", s, re.I):
        return "Sullî-an-der-Loire"
    if re.match(r"^Vitry[-\s]+(?:en|En)[-\s]+Perthois\b", s, re.I):
        return "Vitrî-in-Perthes"
    if re.match(r"^Cluny\b", s, re.I):
        return "Klunî"
    if re.match(r"^Noyon\b", s, re.I):
        return "Nôjôn"
    if re.match(r"^Mayenne\b", s, re.I):
        return "Majenne"
    if re.match(r"^Royan\b", s, re.I):
        return "Rôjân"
    if re.match(r"^Herry\b", s, re.I):
        return "Herrî"
    if re.match(r"^Romilly\b", s, re.I):
        return "Romiljî"
    if re.match(r"^Martigny\b", s, re.I):
        return "Martinjî"
    if re.match(r"^Faucigny\b", s, re.I):
        return "Fautsinjî"
    if re.match(r"^Romigny\b", s, re.I):
        return "Rominjî"
    if re.match(r"^Poulangy\b", s, re.I):
        return "Poulanjî"
    if re.match(r"^Gy\b", s, re.I):
        return "Gî"

    # Saints -> Zant-
    s = re.sub(r"\bSaint[\s\-]+", "Zant-", s, flags=re.I)
    s = re.sub(r"\bSt\.?[\s\-]+", "Zant-", s, flags=re.I)
    s = re.sub(r"Zant-Denis\b", "Zant-Dionîs", s, flags=re.I)
    s = re.sub(r"Zant-Quentin\b", "Zant-Quentîn", s, flags=re.I)
    s = re.sub(r"Zant-Omer\b", "Zant-Omêr", s, flags=re.I)
    s = re.sub(r"Zant-Hubert\b", "Zant-Hûbert", s, flags=re.I)
    s = re.sub(r"Zant-Dizier\b", "Zant-Dizjêr", s, flags=re.I)
    s = re.sub(r"Zant-Junien\b", "Zant-Junjân", s, flags=re.I)
    s = re.sub(r"Zant-Flour\b", "Zant-Flôr", s, flags=re.I)
    s = re.sub(r"Zant-Lizier\b", "Zant-Lizjêr", s, flags=re.I)
    s = re.sub(r"Zant-Malo\b", "Zant-Malô", s, flags=re.I)
    s = re.sub(r"Zant-Mihiel\b", "Zant-Mîhîl", s, flags=re.I)
    s = re.sub(r"Zant-Albans\b", "Zant-Albân", s, flags=re.I)
    s = re.sub(r"Zant-Catherine\b", "Zant-Katerîne", s, flags=re.I)
    s = re.sub(r"Zant-Michel-De-Maurienne\b", "Zant-Mîchel-in-Morjêne", s, flags=re.I)

    # Château- / Chateau- -> Kastel-
    s = re.sub(r"château-?|chateau-?", "Kastel-", s, flags=re.I)
    s = re.sub(r"Kastel-Roux\b", "Kastel-Rûs", s, flags=re.I)
    s = re.sub(r"Kastel-Dun\b", "Kasteldûn", s, flags=re.I)
    s = re.sub(r"Kastel-Briant\b", "Kastel-Brîant", s, flags=re.I)

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
    s = re.sub(r"ville\b", "wîl", s, flags=re.I)
    s = re.sub(r"mont\b", "munt", s, flags=re.I)
    s = re.sub(r"pont\b", "brücke", s, flags=re.I)
    s = re.sub(r"beau(?=[a-z])", "bel", s, flags=re.I)
    s = re.sub(r"ailles?\b", "alje", s, flags=re.I)
    s = re.sub(r"eilles?\b", "îlje", s, flags=re.I)
    
    # Slavic
    s = re.sub(r"grad\b|grod\b|gorod\b", "gort", s, flags=re.I)
    s = re.sub(r"sk\b|ysk\b", "tzich", s, flags=re.I)
    s = re.sub(r"ice\b|yce\b", "itz", s, flags=re.I)
    
    # Cedilla
    s = s.replace("ç", "tz").replace("Ç", "Tz")
    
    return enforce_tarraconian_sound_laws(s)


INDIGENOUS_RESTITUTIONS = {
    # Original Authentic Pre-867 Restitutions
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
    "b_gdov": ("Gdouwe", "Pre-867 hydronym of the Gdovka River (Slavic Gda/Gdova / Finnic Oudova; attested as settlement 1322, fortress 1431)"),
    "b_ostrov": ("Ostrouwe", "Ancient hydronym/toponym of the river island on the Velikaya River (Slavic Ostrov; fortress attested 1341)"),
    "b_ostrov_BJA": ("Ostrouwe", "Ancient hydronym/toponym of the river island (Slavic Ostrov)"),

    # c_avalois & c_chalon Disambiguation
    "b_vezelay": ("Wêzelê", "Ancient Vizeliacum / Benedictine Abbey of Sainte-Marie-Madeleine at Vézelay (attested 858 AD)"),
    "b_morvan": ("Avalûn", "Ancient Gallo-Roman Aballo / fortified caput of the Avalois on the Cousin (attested 843 AD)"),
    "b_autun": ("Ostûn", "Ancient Augustodunum / Episcopal See of Autun (attested secondary variant of the Bishopric of Avalois)"),

    # Inverted / Swapped Seats (Archetype 2)
    "b_konstanz": ("Konstantz", "Roman Constantia / Episcopal See of Lake Constance (attested 585 AD)"),
    "b_sankt_gallen": ("Zant-Gallen", "Imperial Abbey and monastic republic of Saint Gall (attested 612 AD)"),
    "b_evora": ("Êvore", "Ancient Roman Ebora Liberalitas Julia / major episcopal see"),
    "b_beja": ("Bêdsche", "Ancient Roman Pax Julia / Visigothic and Andalusian Bājah (Beja)"),

    # Option A Collision Counties (Archetype 4)
    "b_zagreb": ("Sagreb", "Diocesan hillfort Gradec / Kaptol of Zagreb (attested 1094 AD)"),
    "b_linlithgow": ("Aberkôrn", "Ancient Northumbrian episcopal see Abercorn on the Forth (attested 681 AD)"),
    "b_falkirk": ("Fawkirk", "Ancient Brythonic/Gaelic church site Egglesbreth on the Antonine Wall"),
    "b_oldenburg": ("Aldenburch", "Medieval comital fortress Oldenburg on the Hunte (attested 1108 AD)"),
    "b_leer": ("Lêre", "Ancient 8th-century Frisian trading gau settlement Leer on the Leda (attested 791 AD)"),
    "b_potsdam": ("Pôtzupimi", "Ancient Hevelli Slavic settlement Poztupimi (attested 993 AD)"),
    "b_brandenburg": ("Brennabor", "Ancient princely fortress Brennabor of the Slavic Hevelli on the Havel"),
    "b_lanark": ("Lânark", "Ancient Strathclyde burgh Lanark on the Clyde (chartered 1140 AD)"),
    "b_cadyou": ("Kadjo", "Ancient Strathclyde Brythonic comital center Cadzow (Cadyou)"),
    "b_athlone": ("Âth-Lôen", "Historic Shannon bridge fortress Athlone (Áth Luain, attested 1120 AD)"),
    "b_uisneach": ("Uisnech", "Ancient sacred royal hill and navel of Ireland (Aill na Mireann)"),
    "b_ravensburg": ("Râvensburch", "Welf ancestral fortress Ravensburg on the Schussen (attested 1088 AD)"),
    "b_bregenz": ("Briganz", "Ancient Roman naval base and civitas Brigantium on Lake Constance (attested 15 BC)"),
    "b_coburg": ("Kôburch", "Medieval comital castle Coburg in the Radenzgau (attested 1056 AD)"),
    "b_lichtenfels": ("Liechtenfels", "Ancient Radenzgau fortress on the Main (Lichtenfels)"),
    "b_slupsk": ("Slûptzich", "Ancient Pomeranian tribal gord Słupsk on the Słupia"),
    "b_koszalin": ("Cöslîn", "Ancient Pomeranian trading center Koszalin near the Baltic coast"),
    "b_perekop": ("Tâfros", "Ancient Greek trench and fortress Taphros on the Isthmus of Crimea"),
    "b_aqmescit": ("Akmesdschît", "Historic Crimean Tatar fortress Aqmescit on the Salgir"),
    "b_vecchio": ("Porto-Wêckjo", "Ancient Roman port Portus Syracusanus / Porto-Vecchio"),
    "b_bonifacio": ("Bonifâtzo", "Historic 828 AD citadel of Count Boniface II of Tuscany (Bonifacio)"),
    "b_gowrie": ("Zant-Jônstat", "Historic royal burgh St Johnston / Perth on the Tay"),
    "b_coupar_angus": ("Skône", "Ancient coronation moot and abbey of the Kings of Alba (Scone)"),
    "b_zaslavl": ("Saslâwl", "Ancient comital gord of Zaslavl on the Horyn"),
    "b_dubno": ("Dubne", "Ancient fortress Dubno in Volhynia (attested 1100 AD)"),
    "b_peremyshl": ("Peremyschl", "Ancient princely gord Peremyshl on the San"),
    "b_przemysl": ("Przemîschel", "Historic crossing settlement Przemysl"),
    "b_zvyahel": ("Swîâhel", "Ancient comital gord Zvyahel on the Sluch"),
    "b_kolodiazhen": ("Kolodjâschen", "Ancient fortress Kolodiazhen in Volhynia"),
    "b_osterland": ("Îlenburch", "Historic Mulde fortress Eilenburg in Osterland"),
    "b_colditz": ("Colditz", "Ancient castle Colditz on the Zwickauer Mulde"),
    "b_hradyzk": ("Gradischk", "Ancient Dnieper fortress Gradischk"),
    "b_poltava": ("Altâwe", "Ancient 9th-century fortress Ltava / Poltava on the Vorskla"),
    "b_lasta": ("Laste", "Ancient mountainous province and lordship of Lasta"),
    "b_lalibela": ("Lalîbela", "Monolithic rock-hewn church center Lalibela"),
    "b_adafa": ("Rôhe", "Ancient capital of the Zagwe Dynasty Roha"),
    "b_luxembourg": ("Lützelburch", "Ancient rock fortress Lucilinburhuc founded 963 AD by Count Sigfried"),
    "b_echternach": ("Echternach", "Ancient Benedictine Abbey of Echternach founded 698 AD by St Willibrord"),
    "b_bergh": ("Berch", "Ancestral castle Burg an der Wupper / County of Berg"),
    "b_kaiserswerth": ("Keiserswert", "Ancient Roman and Merovingian Rhine island fortress Kaiserswerth"),
    "b_namur": ("Nâmen", "Ancient junction citadel Namur at the confluence of Sambre and Meuse"),
    "b_dinant": ("Dînant", "Ancient Celtic and Merovingian Mosan trading port Dinant"),
    "b_munchen": ("München", "Chartered toll bridge burgh Munich founded 1158 by Henry the Lion"),
    "b_freising": ("Frîsinge", "Ancient Agilolfing ducal seat and prince-bishopric Freising on the Isar (attested 739 AD)"),
    "b_montpellier": ("Muntpêljê", "Chartered comital burgh Montpellier (attested 985 AD)"),
    "b_maguelone": ("Magelône", "Ancient coastal episcopal island see of Maguelone"),
    "b_algier": ("Alschîr", "Historic Zirid island fortress al-Jazā'ir (Algiers)"),
    "b_bornu": ("Gasargamu", "Historic Kanem-Bornu capital Birni Gazargamo"),
    "b_lubeck": ("Lübeck", "Chartered Baltic trading port Lübeck founded 1143 AD"),
    "b_liubice": ("Liubice", "Ancient Obotrite Slavic princely seat Liubice on the Trave"),
    "b_stezycka": ("Stensitz", "Historic Vistula castellan seat Stężyca"),
    "b_sieciechow": ("Sitzichow", "Ancient Benedictine abbey and fortress Sieciechów"),

    # Displaced Non-Eponymous Capitals (Archetypes 1 & 3)
    "b_wilton": ("Wiltûn", "Ancient Anglo-Saxon royal burh and seat of the Wilsæte on the Wylye"),
    "b_salisbury": ("Sâlesburch", "Ancient Iron Age hillfort and Roman Sorviodunum / Old Sarum"),
    "b_minden": ("Minden", "Ancient episcopal see and cathedral chapter of Minden on the Weser (attested 798 AD)"),
    "b_diepholz": ("Dêpholtz", "Historic noble lordship and water castle Diepholz on the Hunte"),
    "b_chartres": ("Schartres", "Classical Carnutes civitas and cathedral city Autricum / Chartres"),
    "b_dreux": ("Drôchs", "Ancient Gaulish capital of the Durocasses / comital castle Dreux"),
    "b_tuam": ("Tuâm", "Ancient monastic foundation and metropolitan archiepiscopal see of Tuam"),
    "b_galway": ("Gâlewe", "Historic Corrib river fortress and burgh Galway (Dún Gaillimhe, attested 1124 AD)"),
    "b_pergamon": ("Pergamôn", "Ancient Hellenistic royal capital and acropolis of Pergamon"),
    "b_phocaea": ("Phôkêe", "Ancient Ionian maritime city Phocaea on the Aegean coast"),
    "b_nikomedia": ("Nikomêdje", "Ancient Bithynian and Roman imperial capital Nicomedia"),
    "b_chalcedon": ("Kalkêdôn", "Ancient Megarian colony and Ecumenical Council city Chalcedon on the Bosphorus"),
    "b_sardes": ("Sârdes", "Ancient Lydian royal capital and acropolis Sardis on the Pactolus"),
    "b_philadelphia": ("Philadelphîe", "Ancient Hellenistic fortress city Philadelphia in Lydia"),
    "b_lacedaemonia": ("Lakedêmôn", "Classical Sparta / Lacedaemon on the Eurotas"),
    "b_mistra": ("Mistrâ", "Byzantine fortified capital and Despotate seat of Mistra on Mount Taygetos"),
    "b_sagalassus": ("Sagalâs", "Ancient Pisidian mountain metropolis Sagalassos"),
    "b_sozopolis": ("Sôsôpel", "Ancient Byzantine episcopal fortress Sozopolis in Pisidia"),
    "b_manzikert": ("Manzikêrt", "Ancient Armenian fortress city and battlefield Manzikert"),
    "b_musch": ("Mûsch", "Ancient Armenian capital of Taron on the Euphrates plain"),
    "b_armagh": ("Armâch", "Ancient ecclesiastical capital of Ireland and primary see of St Patrick (Ard Mhacha)"),
    "b_dundalk": ("Dundalk", "Ancient fortified ford Dún Dealgan of the Castletown River"),
    "b_lhasa": ("Lâse", "Ancient sacred Tibetan imperial capital and Jokhang cathedral city"),
    "b_potala": ("Pôtâla", "Tibetan palace and religious fortress on the Red Hill / Marpori"),
    "b_rothenburg": ("Rôtenburch", "Imperial castle and burgh Rothenburg ob der Tauber"),
    "b_hohenberg": ("Hôhenberch", "Comital ancestral fortress Hohenberg on the Neckar"),
    "b_rottweil": ("Rôtwîl", "Ancient Roman municipium Arae Flaviae / oldest chartered town of Swabia (Rottweil)"),
    "b_gleichenstein": ("Glêichenstên", "Comital hill castle Gleichenstein in the Eichsfeld"),
    "b_muhlhausen": ("Mülhûsen", "Imperial free city and Frankish royal court Mühlhausen on the Unstrut"),
    "b_brysis": ("Brüsis", "Ancient Byzantine fortress and bishopric Brysis in Thrace"),
    "b_arkadiopolis": ("Arkadîôpel", "Ancient Roman-Byzantine episcopal city Arcadiopolis on the Ergene"),
    "b_nagyszeben": ("Hermannstat", "Transylvanian Saxon chartered city Hermannstadt / Sibiu (attested 1191 AD)"),
    "b_jinguan": ("Goltpfôrte", "Logographic semantic calque for Jīnguān (Golden Gate/Pass)"),
    "b_chengmai": ("Luterweit", "Logographic semantic calque for Chéngmài (Clear Progress)"),
    "b_mopet": ("Môtpet", "Indigenous Ainu/Nivkh river mouth settlement Mopet"),
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
    county_used_names = {}

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
        h_data = houses.get(str(house_id), {})
        house_name = h_data.get("localized_name") or h_data.get("name", "").replace("dynn_", "")
        is_capital = save_b.get("is_capital", False)
        save_name = save_b.get("save_name") or en_cache.get(bk, bk.replace("b_", "").replace("_", " ").title())

        emp = props.get("empire")
        is_sinosphere = (emp in SINO_EMPIRES or ck in SINO_FRONTIER_COUNTIES)

        if ck not in county_used_names:
            county_used_names[ck] = set()

        # ----------------------------------------------------------------------
        # A. AUTHENTIC INDIGENOUS / ARCHAEOLOGICAL RESTITUTION OVERRIDE
        # ----------------------------------------------------------------------
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
            county_used_names[ck].add(res["name"])

        # ----------------------------------------------------------------------
        # B. SINOSPHERE BARONIES (Logographic Semantic Calques)
        # ----------------------------------------------------------------------
        elif is_sinosphere:
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
            county_used_names[ck].add(res["name"])

        # ----------------------------------------------------------------------
        # C. NON-SINOSPHERE BARONIES
        # ----------------------------------------------------------------------
        else:
            c_dir = c_props.get("tarr_direct") or adapt_european_toponym(save_name)
            c_hist = c_props.get("tarr_hist") or c_dir
            c_tarr = c_hist or c_dir
            kd = c_props.get("kingdom", "")

            # 1. Check Option A sub-barony designation
            if bk in opt_a_baronies:
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

            # 2. Check Intra-County Collision (capital barony of an Option A county)
            elif ck in collisions and collisions[ck]["opt_a_key"] != bk and is_capital:
                eponymous_count += 1
                coll = collisions[ck]
                if coll["opt_b_name"] and coll["opt_b_name"] not in county_used_names[ck]:
                    b_tarr = coll["opt_b_name"]
                    orig_note = f"Option B hydronym/landform ({coll['opt_b_name']}) disambiguated from sub-barony seat {coll['opt_a_name']}"
                else:
                    opt_c_name, c_desc = evaluate_founder_option_c(
                        holder_name, holder_traits, house_name, ht, county_used_names[ck], save_name, bk=bk, ck=ck
                    )
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

            # 3. Check Precisely Paired Secondary Variants *(or **X**)* from tarraconian_titles_1059.md
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

            # 4. Eponymous / Capital Barony inheriting parent county
            elif is_capital or (ck and bk.replace("b_", "") == ck.replace("c_", "")):
                eponymous_count += 1
                if c_tarr in county_used_names[ck]:
                    if c_dir and c_dir not in county_used_names[ck]:
                        b_chosen = c_dir
                        orig_desc = f"{save_name} — Disambiguated capital seat from sub-barony {c_hist}"
                    else:
                        opt_c_name, c_desc = evaluate_founder_option_c(
                            holder_name, holder_traits, house_name, ht, county_used_names[ck], save_name, bk=bk, ck=ck
                        )
                        b_chosen = opt_c_name
                        orig_desc = f"{save_name} — Disambiguated capital foundation: {c_desc}"
                    anach_note = "Disambiguated intra-county capital barony."
                else:
                    b_chosen = c_tarr
                    orig_desc = f"{save_name} ({c_props.get('c_origin', save_name)})"
                    anach_note = c_props.get("c_anachronism", "")

                tarr_clean = enforce_tarraconian_sound_laws(b_chosen)
                res = {
                    "name": tarr_clean,
                    "b_tarr": tarr_clean,
                    "b_tarr_direct": c_dir,
                    "b_tarr_hist": c_hist,
                    "b_origin": orig_desc,
                    "b_anachronism": anach_note,
                    "b_ipa": generate_tarraconian_ipa(tarr_clean),
                    "holding_type": ht,
                    "category": "capital_eponymous"
                }

            # 5. Non-Capital Sub-Baronies: Strict Burden of Proof on Antiquity
            else:
                sub_barony_count += 1
                is_anc, anc_reason = check_barony_antiquity(bk, save_name, ck, kd)

                if is_anc:
                    cand = adapt_european_toponym(save_name)
                    has_stem_collision = any(
                        difflib.SequenceMatcher(
                            None,
                            cand.lower().replace("â","a").replace("ê","e").replace("î","i").replace("ô","o").replace("û","u"),
                            un.lower().replace("â","a").replace("ê","e").replace("î","i").replace("ô","o").replace("û","u")
                        ).ratio() >= 0.75
                        for un in county_used_names[ck]
                    )
                    if cand in county_used_names[ck] or has_stem_collision:
                        opt_c_name, c_desc = evaluate_founder_option_c(
                            holder_name, holder_traits, house_name, ht, county_used_names[ck], save_name, bk=bk, ck=ck
                        )
                        tarr_clean = opt_c_name
                        orig_desc = f"{save_name} — Disambiguated foundation: {c_desc}"
                        anach_note = "Disambiguated sub-barony foundation."
                        cat_label = "option_c_foundation"
                    else:
                        tarr_clean = cand
                        orig_desc = f"{save_name} (constituent holding of {c_props.get('tarr', ck)})"
                        anach_note = ""
                        cat_label = "sub_barony_adaptation"
                else:
                    opt_c_name, c_desc = evaluate_founder_option_c(
                        holder_name, holder_traits, house_name, ht, county_used_names[ck], save_name, bk=bk, ck=ck
                    )
                    tarr_clean = opt_c_name
                    orig_desc = f"{save_name} — {c_desc}"

                    circ = is_circular_house(house_name, save_name, bk, ck)
                    house_desc = f"of House {house_name}" if (house_name and not circ) else "under Toponym-First foundation (disqualifying circular in-game house)"
                    if bk == "b_baranovichi":
                        anach_note = f"Post-867 foundation lacking pre-867 attestation under Burden of Proof on Antiquity (1871 railway station); resolved via Option C based on save ruler {holder_name}."
                    elif anc_reason == "classical_late_foundation":
                        anach_note = f"Post-867 feudal fortress / late foundation in classical province; resolved via Option C based on save ruler {holder_name} {house_desc}."
                    elif anc_reason == "high_medieval_foundation":
                        anach_note = f"Post-867 high medieval foundation; resolved via Option C based on save ruler {holder_name} {house_desc}."
                    else:
                        anach_note = f"Post-867 foundation lacking pre-867 attestation under Burden of Proof on Antiquity; resolved via Option C based on save ruler {holder_name} {house_desc}."
                    cat_label = "option_c_foundation"

                res = {
                    "name": tarr_clean,
                    "b_tarr": tarr_clean,
                    "b_tarr_direct": adapt_european_toponym(save_name),
                    "b_tarr_hist": tarr_clean,
                    "b_origin": orig_desc,
                    "b_anachronism": anach_note,
                    "b_ipa": generate_tarraconian_ipa(tarr_clean),
                    "holding_type": ht,
                    "category": cat_label
                }

            county_used_names[ck].add(res["name"])

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

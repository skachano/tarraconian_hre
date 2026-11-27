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
import difflib
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
    "c_tongliao", "c_hulunbuir", "c_wulagai", "c_haerbin",
    "c_SW_ergunia", "c_SW_hailar", "c_SW_heiergun", "c_SW_mengwuo",
    "c_SW_pibeihe", "c_SW_dongcheziguo", "c_SW_hongxingan",
    "c_SW_zhongcheziguo", "c_SW_heiheguo", "c_SW_lingxiguo", "c_SW_powoguo"
}
SINO_CURATED_COUNTIES = set()
if SINO_HANZI_JSON.exists():
    try:
        with open(SINO_HANZI_JSON, "r", encoding="utf-8") as _f:
            _shc = json.load(_f)
            SINO_CURATED_COUNTIES = {k for k in _shc if k.startswith("c_")}
    except Exception:
        pass


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
    
    # 0. Foreign grapheme regularization to Tarraconian Chancellery orthography
    # German Eszett
    s = s.replace("ß", "ss")

    # Polish / Slavic nasals & digraphs
    s = s.replace("ą", "on").replace("ę", "en").replace("Ą", "On").replace("Ę", "En")
    s = re.sub(r"cz", lambda m: "Tsch" if m.group(0)[0].isupper() else "tsch", s, flags=re.I)
    s = re.sub(r"sz(?!elle)", lambda m: "Sch" if m.group(0)[0].isupper() else "sch", s, flags=re.I)
    s = re.sub(r"rz", lambda m: "Rsch" if m.group(0)[0].isupper() else "rsch", s, flags=re.I)
    s = s.replace("ł", "l").replace("Ł", "L")
    s = s.replace("ń", "nj").replace("Ń", "Nj")
    s = s.replace("ś", "sch").replace("Ś", "Sch")
    s = s.replace("ć", "tsch").replace("Ć", "Tsch")
    s = s.replace("ź", "sch").replace("Ź", "Sch")
    s = s.replace("ż", "sch").replace("Ż", "Sch")
    s = s.replace("ř", "rsch").replace("Ř", "Rsch")
    s = s.replace("ě", "e").replace("Ě", "E")
    s = s.replace("ė", "e").replace("Ė", "E")
    
    # Czech / Slovak
    s = s.replace("ň", "n").replace("Ň", "N")
    s = s.replace("ů", "û").replace("Ů", "Û")
    s = s.replace("ď", "d").replace("Ď", "D")
    s = s.replace("ť", "t").replace("Ť", "T")
    s = s.replace("ĺ", "l").replace("Ĺ", "L")
    s = s.replace("ľ", "l").replace("Ľ", "L")
    s = s.replace("ŕ", "r").replace("Ŕ", "R")

    # Slavic háčeks
    s = s.replace("š", "sch").replace("Š", "Sch")
    s = s.replace("ž", "sch").replace("Ž", "Sch")
    s = s.replace("č", "tsch").replace("Č", "Tsch")
    s = s.replace("đ", "dsch").replace("Đ", "Dsch")
    
    # Scandinavian
    s = s.replace("å", "ô").replace("Å", "Ô")
    s = s.replace("æ", "ê").replace("Æ", "Ê")
    s = s.replace("ø", "ö").replace("Ø", "Ö")
    s = s.replace("ð", "d").replace("Ð", "D")
    s = s.replace("þ", "t").replace("Þ", "T")
    s = s.replace("ý", "î").replace("Ý", "Î")
    
    # Romanian, Turkish, Azeri, IPA
    s = s.replace("ș", "sch").replace("Ș", "Sch")
    s = s.replace("ț", "tz").replace("Ț", "Tz")
    s = s.replace("ă", "e").replace("Ă", "E")
    s = s.replace("ə", "e").replace("Ə", "E")
    s = s.replace("ı", "i").replace("İ", "I")
    s = s.replace("ğ", "g").replace("Ğ", "G")
    
    # Iberian
    s = s.replace("ñ", "nj").replace("Ñ", "Nj")
    s = s.replace("ã", "â").replace("Ã", "Â")
    
    # Macrons
    s = s.replace("ā", "â").replace("Ā", "Â")
    s = s.replace("ī", "î").replace("Ī", "Î")
    s = s.replace("ū", "û").replace("Ū", "Û")
    
    # Diaereses & Hungarian
    s = s.replace("ë", "e").replace("Ë", "E")
    s = s.replace("ï", "î").replace("Ï", "Î")
    s = s.replace("ő", "ö").replace("Ő", "Ö")
    s = s.replace("ű", "ü").replace("Ű", "Ü")

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
    s = re.sub(r"stadt\b", "stat", s, flags=re.I)
    s = re.sub(r"land\b", "lant", s, flags=re.I)
    
    # 7. Affricates
    # Initial ts -> z (preserve leading or eclipsed capital case like Tsang-Po -> Zang-Po, tSiûir -> Ziûir)
    s = re.sub(r"\bts(?!ch)", lambda m: "Z" if any(c.isupper() for c in m.group(0)) else "z", s, flags=re.I)
    # Medial/final ts -> tz (only after vowels, preventing corruption of -st- clusters like -stat, -stûr, -sachsen)
    s = re.sub(r"(?<=[aeiouyâêîôûäöü])ts(?!ch|z)", "tz", s, flags=re.I)
    s = re.sub(r"tz[z]+", "tz", s, flags=re.I)
    
    # Strip any broken trailing punctuation
    s = s.rstrip(" (;,[{")
    
    # Capitalize first letter of compound components while keeping grammatical prepositions lowercase
    if "-" in s:
        parts = s.split("-")
        LOWERCASE_PARTICLES = {"in", "an", "der", "dem", "den", "am", "van", "vom", "von", "ende", "und", "el", "es", "er", "al", "de", "del", "du", "hügel"}
        res_parts = []
        for idx, p in enumerate(parts):
            words = p.split(" ") if p else [""]
            new_words = []
            for w_idx, w in enumerate(words):
                if (idx > 0 or w_idx > 0) and w.lower() in LOWERCASE_PARTICLES:
                    new_words.append(w.lower())
                else:
                    new_words.append(w[:1].upper() + w[1:] if w else "")
            res_parts.append(" ".join(new_words))
        s = "-".join(res_parts)
    else:
        s = s[:1].upper() + s[1:] if s else ""
        
    return s


def normalize_phonetic_stem(s: str) -> str:
    """Normalizes toponym stems to detect homophonic and near-duplicate collisions."""
    if not s:
        return ""
    s = s.lower().replace("â", "a").replace("ê", "e").replace("î", "i").replace("ô", "o").replace("û", "u").replace("ä", "e").replace("ö", "e").replace("ü", "i")
    s = s.replace("-", "").replace(" ", "")
    s = s.replace("ck", "k").replace("ch", "k").replace("c", "k")
    s = s.replace("tz", "z").replace("ts", "z").replace("sch", "sh").replace("z", "s")
    s = s.replace("v", "w").replace("f", "w").replace("ph", "w")
    s = s.replace("dt", "t").replace("th", "t").replace("d", "t")
    s = s.replace("y", "i").replace("j", "i")
    s = re.sub(r"[^a-z]", "", s)
    s = re.sub(r"(.)\1+", r"\1", s)
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
        
    # Expand Saint abbreviations (requiring dot or whitespace before capital to prevent matching Stendal, Stade, etc.)
    s = re.sub(r"\bSt\.(?:\s+|-)?", "Zant-", s)
    s = re.sub(r"\bSt\s+(?=[A-Z])", "Zant-", s)
    s = re.sub(r"\bSaint[\s\-]+", "Zant-", s, flags=re.IGNORECASE)
    
    # Store original stripped name to detect Romance/Germanic patterns for stress
    raw_stem = s
    
    res = s.lower()
    
    # Clean apostrophes
    res = res.replace("'", "")
    
    # Regularize y in onsets, glides, diphthongs, and vocalic codas
    res = re.sub(r"y(?=[aeiouâêîôûäöü])", "j", res)
    res = re.sub(r"(?<=[aeiouâêîôûäöü])i(?=[aeiouâêîôûäöü])", "j", res)
    res = re.sub(r"ey", "ei", res)
    res = re.sub(r"ay", "ai", res)
    res = re.sub(r"oy", "eu", res)
    res = re.sub(r"uy", "ui", res)
    res = re.sub(r"y\b", "i", res)
    res = re.sub(r"y", "i", res)
    
    # Convert foreign diacritics / non-Tarraconian orthography
    res = res.replace("š", "sch").replace("ž", "dsch").replace("č", "tsch")
    res = res.replace("ð", "d").replace("þ", "t")
    res = res.replace("æ", "e").replace("ä", "e").replace("å", "o").replace("ë", "e").replace("ï", "i")
    res = res.replace("ñ", "nj").replace("ý", "î")
    res = res.replace("qu", "kw").replace("q", "k")
    # Catalan/Romance gu before front vowels -> ɡ (velar stop digraph)
    res = re.sub(r"gu(?=[eiêîy])", "ɡ", res)
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
    res = re.sub(r"([iîeêyüö]|eː|iː|yː|øː|aɪ|ɛɪ|ɔʏ)ch", r"\1ç", res)
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
    
    # Diphthongs: ei is [ɛɪ] (native MHG), ai is [aɪ] (Romance/Arabic/Asian/Southern loans)
    res = re.sub(r"ei", "ɛɪ", res)
    res = re.sub(r"ai", "aɪ", res)
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
    # Only in multisyllabic words (must be preceded by a vowel in the stem)
    # But preserve stressed Romance -el, -et, -at, -on, -an
    v_regex = r"(?:[aːeːiːoːuːøːyːaɛɪɔʊʏœə]|aɪ|ɛɪ|ɔʊ|ɔʏ)"
    C_SET = r"[bdfɡɣkmnprstvwxzʒʃçʎɲ]"
    res = re.sub(f"({v_regex}{C_SET}*?)({C_SET})ɛn\\b", r"\1\2ən", res)
    res = re.sub(f"({v_regex}{C_SET}*?)({C_SET})ɛr\\b", r"\1\2ər", res)
    res = re.sub(f"({v_regex}{C_SET}*?)({C_SET})ɛl\\b", r"\1\2əl", res)
    # Medial -en- in compounds (e.g. Plintenburch) - must be between syllables
    res = re.sub(f"({v_regex}{C_SET}*?)({C_SET})ɛn({C_SET}+?{v_regex})", r"\1\2ən\3", res)
    
    # Romance words ending in -tel, -del, -pel with oxytone stress keep [ɛl] if root is Romance
    if re.search(r"(castel|kastel|montpel|bordel)", raw_stem, re.IGNORECASE):
        res = re.sub(r"əl\b|əl(?=\s|-)", "ɛl", res)
        
    res = re.sub(f"({v_regex}{C_SET}*?)({C_SET})ɛ\\b", r"\1\2ə", res)
    
    # Intervocalic s -> z (single s only between vowels)
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
        
        vowel_phones = ["aː", "eː", "iː", "oː", "uː", "øː", "yː", "aɪ", "ɛɪ", "ɔʊ", "ɔʏ", "a", "ɛ", "ɪ", "ɔ", "ʊ", "ʏ", "œ", "ə"]
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
        has_final_long = any(lv in final_syl for lv in ["aː", "eː", "iː", "oː", "uː", "aɪ", "ɛɪ", "ɔʊ", "ɔʏ"])
        
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
            s = s.replace("ž", "sh").replace("š", "sh").replace("č", "ch").replace("ř", "r").replace("ď", "d").replace("ť", "t").replace("ň", "n").replace("á", "a").replace("é", "e").replace("í", "i").replace("ý", "i")
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
                elif (len(norm_b) >= 4 and len(norm_sec) >= 4 and (norm_b in norm_sec or norm_sec in norm_b)) or \
                     (len(norm_en) >= 4 and len(norm_sec) >= 4 and (norm_en in norm_sec or norm_sec in norm_en)):
                    score = 80
                elif (len(norm_b) >= 4 and len(norm_sec) >= 4 and norm_b[:4] == norm_sec[:4]) or \
                     (len(norm_en) >= 4 and len(norm_sec) >= 4 and norm_en[:4] == norm_sec[:4]):
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
        "c_ravensburg": "Altdorf",
        "c_coburg": "Kôburch",
        "c_slupsk": "Slûptzich",
        "c_gowrie": "Zant-Jônstat",
        "c_lviv": "Lemberch",
        "c_zaslavl": "Saslâwl",
        "c_peremyshl": "Peremyschl",
        "c_zvyahel": "Swîâhel",
        "c_perekop": "Neâpolis",
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
    
    if not parts and is_capital and county_tarr:
        tarr_name = enforce_tarraconian_sound_laws(county_tarr)
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
        "b_hanzi": clean_zh or hist_kanji,
        "b_ipa": generate_tarraconian_ipa(tarr_name)
    }


# ==============================================================================
# 4. FOUNDER ARCHETYPE EVALUATION (SECTION 3.2 / OPTION C ENGINE)
# ==============================================================================

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


def evaluate_founder_option_c(char_name: str, traits: list, house_name: str, holding_type: str, used_names: set = None, save_name: str = "", bk: str = "", ck: str = "", is_anachronism: bool = True):
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
    clean_stem = "" if is_anachronism else (re.sub(r"[^a-zA-Z]", "", save_name.split()[0]) if save_name else "")
    if not clean_stem and not is_anachronism:
        clean_stem = "Burch"

    # Toponym-First Principle: Disqualify circular pseudo-dynasties derived from the holding
    if clean_house and is_circular_house(clean_house, clean_stem or save_name, bk, ck):
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
            if clean_stem:
                candidates.append((f"{clean_stem}burch", f"Fortress seat of {clean_stem} established by {clean_founder}"))
            else:
                candidates.append((f"{clean_founder}shûsen", f"Feudal settlement and stronghold of {clean_founder}"))

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
            if clean_stem:
                candidates.append((f"{clean_stem}stat", f"Chartered borough of {clean_stem} established by {clean_founder}"))
            else:
                candidates.append((f"{clean_founder}shûsen", f"Chartered borough established by {clean_founder}"))

    for c_nm, desc in candidates:
        clean_cand = enforce_tarraconian_sound_laws(c_nm)
        if clean_cand not in used:
            return clean_cand, desc

    if clean_stem:
        fallback_nm = enforce_tarraconian_sound_laws(f"{clean_founder}s{clean_stem[:4]}stat")
    else:
        fallback_nm = enforce_tarraconian_sound_laws(f"{clean_founder}swart")
    return fallback_nm, f"Municipal foundation established by {clean_founder}"


POST_867_ANACHRONISMS = {
    "b_lorient": "1666 French East India Company port",
    "b_portsmouth": "1180 Norman port founded by Jean de Gisors",
    "b_dunkirk": "c. 960 Flemish coastal town",
    "b_cherbourg": "10th-century Norman fortress",
    "b_versailles": "1038 medieval village",
    "b_cuxhaven": "16th-century Elbe mouth port",
    "b_montauban": "1144 bastide founded by Alfonso Jordan",
    "b_limbourg": "1020 castle built by Frederick of Luxembourg",
    "b_combourg": "1014-1040 castle built by Archbishop of Dol",
    "b_taillebourg": "10th-11th century Charente fortress",
    "b_floridsdorf": "1786 modern Danube plain foundation",
    "b_castlebar": "1235 Norman castle built by Gerald de Barry",
    "b_portogruaro": "1140 Lemene river port",
    "b_gelnhausen": "1170 Barbarossa Kaiserpfalz",
    "b_bruchhausen": "1199 collegiate church",
    "b_recklinghausen": "1017 first attested settlement",
    "b_wolfratshausen": "1116 first attested castle",
    "b_burghausen": "1025 castle first attested",
    "b_neumarkt": "1130 planned market town",
    "b_rockenhausen": "1144 first attested settlement",
    "b_sangerhausen": "991 first attested settlement",
    "b_peterborough": "970 refounded monastic burh",
    "b_chatellerault": "952 Castrum Heraldi",
    "b_saint_dizier": "1227 castle built by Guy II of Dampierre",
    "b_chambery": "1057 first attested castle",
    "b_montbrison": "1089 castle of the Counts of Forez",
    "b_faucigny": "1000 castle of the Lords of Faucigny",
    "b_jonkoping": "1284 chartered trading town",
    "b_borgarsyslar": "1016 royal fortress founded by St. Olaf",
    "b_pushkin": "1937 Soviet renaming of Tsarskoye Selo (founded 1710) on Finnish Saari Mojs",
    "b_naro-fominsk": "1864 textile factory town formed around 1339 Fominskoye",
    "b_novorzhev": "1777 administrative foundation by Catherine the Great on Lake Arsho",
    "b_pavlovsk": "1709 Osered fortress founded by Peter the Great on the Don",
    "b_wilhelmshaven": "1869 Prussian naval base on the Jade Bight",
    "b_peterhead": "1593 planned fishing port founded by George Keith",
    "b_arkhangelsk": "1584 fortress Novokholmogory founded around 1388 Archangel monastery",
    "b_oryol": "1566 fortress founded by Ivan the Terrible at Oka/Orlik confluence",
    "b_konotop": "1634 Cossack outpost on Konotopka",
    "b_sudzha": "1664 fortified sloboda on Sudzha",
    "b_oulu": "1605 chartered trading town by Charles IX of Sweden opposite 1590 castle",
    "b_vinnytsia": "1363 Lithuanian fortress built by Koriatovych princes on Southern Bug",
    "b_kaunas": "1361 Teutonic chronicle mention",
    "b_olsztyn": "1348 Allenstein castle founded by Warmian chapter on Lyna (Alle)",
    "b_serpukhov": "1339 testament of Ivan Kalita on Serpeyka",
    "b_lodz": "1332 agricultural village of Lodzia",
    "b_vilnius": "1323 letter of Gediminas",
    "b_daugavpils": "1275 Dinaburg castle built by Livonian Order Master Ernst von Ratzeburg",
    "b_slonim": "1252 Vslonim in Hypatian Chronicle",
    "b_zhelezny_ustyug": "1252 Ustyuzhna Zheleznopolskaya ironworks outpost on Katun",
    "b_newport": "1100 Anglo-Norman planned borough Novus Burgus",
    "b_newbury": "1080 Anglo-Norman planned borough Neuberie",
    "b_barysaw": "1102 fortress founded by Prince Boris of Polotsk",
    "b_maladzyechna": "1388 charter of Prince Dmitry Olgierdovich",
    "b_starodub-on-the-klyazma": "1152 fortress founded by Yuri Dolgorukiy on Klyazma River",
    "b_yegoryevsk": "1778 town chartered by Catherine II; originally 1462 village of Vysokoye on Guslitsa",
    "b_yuriev": "1032 fortress founded on the Ros by Yaroslav the Wise (baptismal name Yuri)",
    "b_yuryev": "1152 fortress Yuryev-Polsky founded by Yuri Dolgorukiy on Koloksha/Gza",
    "b_yaroslav_VOL": "1031 fortress Jarosław founded on the San by Yaroslav the Wise",
    "b_rostislavl": "1153 fortress founded on the Oka by Prince Rostislav Yaroslavich",
    "b_danilov": "Late medieval settlement founded on Pelenda by Prince Daniil of Moscow",
}


def check_barony_antiquity(bk: str, save_name: str, ck: str, kd: str):
    """
    Evaluates whether a sub-barony has positive pre-867 proof under the Burden of Proof on Antiquity.
    Returns: (is_ancient: bool, reason: str)
    """
    if bk in INDIGENOUS_RESTITUTIONS:
        return True, "indigenous_restitution"
    if bk in POST_867_ANACHRONISMS:
        return False, "classical_late_foundation"
    if bk == "b_baranovichi":
        return False, "modern_railway_foundation"

    clean_k = bk.replace("b_", "").replace("_", " ")
    test_text = f"{clean_k} {save_name}"

    # Specific late industrial/railway markers
    if re.search(r"\b(railway|station|mine|kolkhoz|soviet|lenin|stalin|zavod|fabrik)\b", test_text, re.I):
        return False, "modern_railway_foundation"

    # Late patronymic / manor settlement morphology (Slavic -ovichi/-evichi, -shchina, etc.)
    if re.search(r'(ovichi|evichi|avichy|evichy|ovichy|evits|ovits|ovtsy|evtsy|shchina|szczyna|chytsy)$', save_name, re.I) or \
       re.search(r'(ovichi|evichi|avichy|evichy|ovichy|evits|ovits|ovtsy|evtsy|shchina|szczyna|chytsy)$', clean_k, re.I):
        return False, "late_settlement_foundation"

    # Late medieval planned towns, bastides, repoblaciones, and conquest boroughs
    if re.search(r'\b(villeneuve|villefranche|neuville|bourgneuf|castelnau|chateauneuf|sauveterre|bastide|aigueperse)\b', test_text, re.I) or \
       re.search(r'\b(newport|newbury|newcastle|newborough|pontefract)\b', test_text, re.I) or \
       re.search(r'\b(neustadt|neuenburg|neuburg|freiberg|freistadt)\b', test_text, re.I) or \
       re.search(r'\b(villanueva|villafranca|puebla|ciudad[-_ ]real|villarreal|lapueblademontalban)\b', test_text, re.I) or \
       re.search(r'\b(castelfranco|castelnuovo|villanuova|cittanova)\b', test_text, re.I):
        return False, "late_settlement_foundation"

    # Eponymous foundations named after concrete historical persons living after 867 AD
    # (e.g. Yaroslav the Wise, Yuri Dolgorukiy, Vladimir Monomakh, Izyaslav, Rostislav, Mstislav, Danilov, etc.)
    if re.search(r'\b(?:yuri[e]?v|yury[e]?v|jurjew|yuriew|yuryevsk|yurievets)[a-z]*\b', test_text, re.I) or \
       re.search(r'\b(?:yaroslav|jaroslaw|jaroslav)[a-z]*\b', test_text, re.I) or \
       re.search(r'\b(?:izyaslav|zasla[vw]|isjaslaw)[a-z]*\b', test_text, re.I) or \
       re.search(r'\b(?:mstislav|rostislav|svyatoslav|vsevolod|vsevolozh)[a-z]*\b', test_text, re.I) or \
       re.search(r'\b(?:borisov|barysaw|borisogleb|glebov)[a-z]*\b', test_text, re.I) or \
       re.search(r'\b(?:dmitrov|danilov|bogolyub)[a-z]*\b', test_text, re.I) or \
       re.search(r'\b(?:konstantinov|romanov)[a-z]*\b', test_text, re.I) or \
       re.search(r'\b(?:kristianstad|christiania|frederik|valdemars|philippeville|charleville)[a-z]*\b', test_text, re.I):
        return False, "post_867_eponymous_person"

    c_key = bk.replace("b_", "c_")
    if c_key in ATTESTATION_REGISTRY:
        att_data = ATTESTATION_REGISTRY[c_key]
        att_yr = att_data[0]
        is_geo_stem = att_data[3] if len(att_data) > 3 else False
        if att_yr is not None and att_yr > 867 and not is_geo_stem:
            return False, "high_medieval_foundation"
        elif att_yr is not None and (att_yr <= 867 or is_geo_stem):
            return True, "chronicle_attestation"

    if re.search(r"\b(gau|gebirge|tal|wald|fluv|werder|werth|am-|an-der-|see|meer|joki|järvi|jarvi|vesi|salmi|saari|niemi|lahti|koski|suo|vuori|harju|selkä|selka|ostrov|gora|blato|jazero)\b", bk + " " + save_name, re.I):
        return True, "ancient_toponym"

    # Cultural & historical settlement continuity across all realms
    return True, "cultural_continuity"


# ==============================================================================
# 5. EUROPEAN / NON-SINOSPHERE TOPONYMIC ADAPTATION
# ==============================================================================

def _adapt_european_toponym_raw(name: str) -> str:
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
    if re.match(r"^(?:Gu[éêe]ret|Garait)\b", s, re.I):
        return "Garait"
    if re.match(r"^Gu[éêe]rande\b", s, re.I):
        return "Guerande"
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
    if re.match(r"^Ch[aâ]tillon\b", s, re.I):
        return "Schâtillôn"
    if re.match(r"^Chaumont\b", s, re.I):
        return "Schaumunt"
    if re.match(r"^Chablis\b", s, re.I):
        return "Schablîs"
    if re.match(r"^Champs\b", s, re.I):
        return "Schamps"
    if re.match(r"^Ch[aâ]lus\b", s, re.I):
        return "Schâlus"
    if re.match(r"^Champagnole\b", s, re.I):
        return "Schampanjôle"
    if re.match(r"^Chiny\b", s, re.I):
        return "Schinî"
    if re.match(r"^(?:La\s+)?Fl[eêè]che\b", s, re.I):
        return "La Flêsche"
    if re.match(r"^Loches\b", s, re.I):
        return "Lôsches"
    if re.match(r"^(?:La\s+)?Roche\b", s, re.I):
        return "La Rosche"
    if re.match(r"^(?:La\s+)?Teste[-\s]+De[-\s]+Buch\b", s, re.I):
        return "La Teste-De-Büsch"
    if re.match(r"^Montereau\b", s, re.I):
        return "Monterô"
    if re.match(r"^Morteau\b", s, re.I):
        return "Môrtô"

    # Italian Ch- -> Kj- (velar plosive /k/ before front vowels)
    if re.match(r"^Chieri\b", s, re.I):
        return "Kjêri"
    if re.match(r"^Chiari\b", s, re.I):
        return "Kjâri"
    if re.match(r"^Chiavari\b", s, re.I):
        return "Kjâvari"
    if re.match(r"^Chiusi\b", s, re.I):
        return "Kjûsi"
    if re.match(r"^Chieti\b", s, re.I):
        return "Kjêti"
    if re.match(r"^Chioggia\b", s, re.I):
        return "Kjôdscha"
    if re.match(r"^Comacchio\b", s, re.I):
        return "Komakkjô"
    if re.match(r"^Civitavecchia\b", s, re.I):
        return "Zivitavekkje"

    # English Ch- -> Tsch-
    if re.match(r"^Chelmsford\b", s, re.I):
        return "Tschelmsvurt"
    if re.match(r"^Chesterfield\b", s, re.I):
        return "Tschesterfild"
    if re.match(r"^Chichester\b", s, re.I):
        return "Tschitschester"
    if re.match(r"^Christchurch\b", s, re.I):
        return "Kristkirchen"
    if re.match(r"^Northwich\b", s, re.I):
        return "Nordwîch"

    # Iberian Ch- / -ch- -> Sch- / -tsch-
    if re.match(r"^Chaves\b", s, re.I):
        return "Schâves"
    if re.match(r"^Belchite\b", s, re.I):
        return "Beltschîte"
    if re.match(r"^Pedroche\b", s, re.I):
        return "Pêdrôtsche"
    if re.match(r"^Hornachos\b", s, re.I):
        return "Fornatschos"

    # Slavic /tʃ/ -> Tsch- / -tsch-
    if re.match(r"^Cherven\b", s, re.I):
        return "Tscherwen"
    if re.match(r"^Belogradchik\b", s, re.I):
        return "Belogradtschik"
    if re.match(r"^Lovech\b", s, re.I):
        return "Lowetsch"
    if re.match(r"^Krichim\b", s, re.I):
        return "Kritschim"

    # Indic / Asian / Southeast Asian /tʃ/ -> Tsch-
    if re.match(r"^Chachran\b", s, re.I):
        return "Tschachran"
    if re.match(r"^Chunian\b", s, re.I):
        return "Tschunian"
    if re.match(r"^Chilas\b", s, re.I):
        return "Tschilas"
    if re.match(r"^Ch[āa]tig[āa]ma\b", s, re.I):
        return "Tschatigama"
    if re.match(r"^Chapra\b", s, re.I):
        return "Tschapra"
    if re.match(r"^Chutur\b", s, re.I):
        return "Tschutur"
    if re.match(r"^Chaul\b", s, re.I):
        return "Tschaul"
    if re.match(r"^Chiprarulana\b", s, re.I):
        return "Tschiprarulana"
    if re.match(r"^Chiang\s+Klang\b", s, re.I):
        return "Tschjang Klang"
    if re.match(r"^Chiang\s+Rai\b", s, re.I):
        return "Tschjang Rai"
    if re.match(r"^Chiang\s+Mai\b", s, re.I):
        return "Tschjang Mai"
    if re.match(r"^Thap\s+Chumphon\b", s, re.I):
        return "Thap Tschumphon"
    if re.match(r"^Chumpon\b", s, re.I):
        return "Tschumpon"
    if re.match(r"^Chom\s+Thong\b", s, re.I):
        return "Tschom Thong"
    if re.match(r"^Choam\s+Khsant\b", s, re.I):
        return "Tschoam Khsant"
    if re.match(r"^Chaturmukha\b", s, re.I):
        return "Tschaturmukha"
    if re.match(r"^Chachoengsoo\b", s, re.I):
        return "Tschachoengsoo"
    if re.match(r"^Chaiyaphum\b", s, re.I):
        return "Tschaiyaphum"
    if re.match(r"^Changdschi\b", s, re.I):
        return "Tschangdschi"

    # Slavic & Baltic historical exonyms and standard adaptations
    if re.match(r"^Vyr['’]?\b", s, re.I):
        return "Wîr"
    if re.match(r"^Vy[sš]ehrad\b", s, re.I):
        return "Wischegrat"
    if re.match(r"^M[eě]ln[ií]k\b", s, re.I):
        return "Melnîch"
    if re.match(r"^Loket\b", s, re.I):
        return "Ellebôgen"
    if re.match(r"^P[rř]imda\b", s, re.I):
        return "Pfrîmde"
    if re.match(r"^Beroun\b", s, re.I):
        return "Berûn"
    if re.match(r"^Vilnius\b", s, re.I):
        return "Wilne"
    if re.match(r"^Trakai\b", s, re.I):
        return "Tracken"
    if re.match(r"^Kernav[eė]\b", s, re.I):
        return "Kernouwe"
    if re.match(r"^Lutsk\b", s, re.I):
        return "Lûtzich"
    if re.match(r"^Vyshgorod\b", s, re.I):
        return "Wischgort"
    if re.match(r"^Olsztyn\b", s, re.I):
        return "Olschtîn"
    if re.match(r"^Cz[eę]stochowa\b", s, re.I):
        return "Tschestochouwe"
    if re.match(r"^Wi[sś]lica\b", s, re.I):
        return "Wislîtze"
    if re.match(r"^Wieliczka\b", s, re.I):
        return "Wjelitschke"
    if re.match(r"^D[aą]browa\s+G[oó]rnicza\b", s, re.I):
        return "Dombrôwa-Gôrnitza"
    if re.match(r"^J[eę]drzej[oó]w\b", s, re.I):
        return "Jendrschêjôw"
    if re.match(r"^Radomsko\b", s, re.I):
        return "Radomskô"
    if re.match(r"^Ciechan[oó]w\b", s, re.I):
        return "Tschechanôw"
    if re.match(r"^P[ií]sek\b", s, re.I):
        return "Pîsek"
    if re.match(r"^Krumlov\b", s, re.I):
        return "Krummouwe"
    if re.match(r"^Prachatice\b", s, re.I):
        return "Prachatitz"
    if re.match(r"^Bechyn[eě]\b", s, re.I):
        return "Bechîn"
    if re.match(r"^B[ií]lina\b", s, re.I):
        return "Bîline"
    if re.match(r"^Slan[yý]\b", s, re.I):
        return "Slânî"

    # South Slavic & Balkan adaptations
    if re.match(r"^[SŠ]ibenik\b", s, re.I):
        return "Schibenîk"
    if re.match(r"^Dre[zž]nik\b", s, re.I):
        return "Dreschnîch"
    if re.match(r"^Klju[cč]\s+na\s+Sani\b", s, re.I):
        return "Kljutsch-an-der-Sâne"
    if re.match(r"^Kotor\s+Varo[sš]\b", s, re.I):
        return "Kotor-Wârosch"
    if re.match(r"^Gradi[sš]ka\b", s, re.I):
        return "Gradischke"
    if re.match(r"^Gla[zž]\b", s, re.I):
        return "Glasch"
    if re.match(r"^Glamo[cč]\b", s, re.I):
        return "Glamotsch"
    if re.match(r"^Omi[sš]\b", s, re.I):
        return "Omîsch"
    if re.match(r"^[ZŽ]ica\b", s, re.I):
        return "Schitze"
    if re.match(r"^Bre[zž]nica\b", s, re.I):
        return "Breschnitze"
    if re.match(r"^Gora[zž]de\b", s, re.I):
        return "Goraschde"
    if re.match(r"^U[zž]i[cč]e?\b|^U[zž]itz\b", s, re.I):
        return "Uschitze"
    if re.match(r"^Onogo[sš]t\b", s, re.I):
        return "Onogoscht"
    if re.match(r"^Ke[zž]marok\b", s, re.I):
        return "Keschmarck"
    if re.match(r"^Szendr[oő]\b", s, re.I):
        return "Sendrô"

    # Scandinavian adaptations
    if re.match(r"^Tors[aå]s\b", s, re.I):
        return "Torsôs"
    if re.match(r"^N[aæ]stved\b", s, re.I):
        return "Nestwêt"
    if re.match(r"^Randr[oø]s\b", s, re.I):
        return "Randers"
    if re.match(r"^L[iî][dð]andisnes\b", s, re.I):
        return "Lîdandisnes"
    if re.match(r"^R[yý]gjarfylki\b", s, re.I):
        return "Rîgjarfîlki"
    if re.match(r"^Har[dð]angr\b", s, re.I):
        return "Hardanger"
    if re.match(r"^Nor[dð]rm[aæ]rr\b", s, re.I):
        return "Nordmer"
    if re.match(r"^Sto[dð]reimr\b", s, re.I):
        return "Stodrem"
    if re.match(r"^Su[dð]r\s+Eystridalr\b", s, re.I):
        return "Suder-Estridal"
    if re.match(r"^Rau[dð]ey\b", s, re.I):
        return "Roudei"
    if re.match(r"^Ra[dð]und\b", s, re.I):
        return "Radunt"
    if re.match(r"^Vestfir[dð]ir\b", s, re.I):
        return "Westfirder"
    if re.match(r"^Borg\s+[aâ]\s+M[yý]rum\b", s, re.I):
        return "Burch-an-den-Mîren"
    if re.match(r"^Vopnafj[oö]r[dð]r\b", s, re.I):
        return "Wopnafierd"
    if re.match(r"^[AÂ]r[dð]ardalr\b", s, re.I):
        return "Ârdartâl"
    if re.match(r"^St[oô]rs[aæ]r\b", s, re.I):
        return "Stôrsê"
    if re.match(r"^Hei[dð]v[iî]k\b", s, re.I):
        return "Heidwîch"

    # Romanian adaptations
    if re.match(r"^Arge[sș]\b", s, re.I):
        return "Argesch"
    if re.match(r"^Filia[sș]i\b", s, re.I):
        return "Filjasch"
    if re.match(r"^Zore[sș]ti\b", s, re.I):
        return "Zorescht"
    if re.match(r"^Dumbr[aă]veni\b", s, re.I):
        return "Dumbrawên"
    if re.match(r"^Baia\s+de\s+Aram[aă]\b", s, re.I):
        return "Baia-de-Arama"
    if re.match(r"^Or[sș]ova\b", s, re.I):
        return "Orschowe"
    if re.match(r"^Dr[aă]g[aă][sș]ani\b", s, re.I):
        return "Dragaschân"

    # Iberian adaptations
    if re.match(r"^Oca[nñ]a\b", s, re.I):
        return "Okanje"
    if re.match(r"^Valdepe[nñ]as\b", s, re.I):
        return "Valdepenjas"
    if re.match(r"^Sari[nñ]ena\b", s, re.I):
        return "Sarinjene"
    if re.match(r"^Mondo[nñ]edo\b", s, re.I):
        return "Mondonjêdo"
    if re.match(r"^Guimar[aã]es\b", s, re.I):
        return "Gimarês"

    # Indic, Semitic, Tibetan & Asian adaptations
    if re.match(r"^W[aä]rj[iī]h\b", s, re.I):
        return "Werdschîh"
    if re.match(r"^N[iī]r[uū]n\b", s, re.I):
        return "Nîrûn"
    if re.match(r"^P[aā]ndu[aā]\b", s, re.I):
        return "Pândûe"
    if re.match(r"^Raktamrittik[aā]\b", s, re.I):
        return "Raktamrittike"
    if re.match(r"^Candranath[aā]\b", s, re.I):
        return "Kandranathe"
    if re.match(r"^S[aā]ntipura\b", s, re.I):
        return "Sântipur"
    if re.match(r"^P[aā]v[aā]\b", s, re.I):
        return "Pâve"
    if re.match(r"^B[oô]h[aā]ri\b", s, re.I):
        return "Bôhâri"
    if re.match(r"^Handi[aā]\b", s, re.I):
        return "Handje"
    if re.match(r"^Camp[aā]ranya\b", s, re.I):
        return "Kampâranje"
    if re.match(r"^M[uū][oö]t\b", s, re.I):
        return "Mûet"
    if re.match(r"^Champaner\b", s, re.I):
        return "Tschampanêr"
    if re.match(r"^Vadnagar\b", s, re.I):
        return "Wadnâgar"
    if re.match(r"^Modhera\b", s, re.I):
        return "Modhêra"
    if re.match(r"^Khambhat\b", s, re.I):
        return "Chambhât"
    if re.match(r"^Ashaval\b", s, re.I):
        return "Aschawâl"
    if re.match(r"^Agar\b", s, re.I):
        return "Âgar"
    if re.match(r"^Osian\b", s, re.I):
        return "Osjân"
    if re.match(r"^Karub\b", s, re.I):
        return "Karûb"
    if re.match(r"^Takts[eéè]\b", s, re.I):
        return "Taktzê"
    if re.match(r"^Porho[eë]t\b", s, re.I):
        return "Porhoet"
    if re.match(r"^(?:Montlhéry|Montlhêry)\b", s, re.I):
        return "Muntlêrî"
    if re.match(r"^Castelnaudary\b", s, re.I):
        return "Kastelnoudarî"
    if re.match(r"^Sully[-\s]+(?:sur|Sur)[-\s]+Loire\b", s, re.I):
        return "Sullî-an-der-Loire"
    if re.match(r"^Bar[-\s]+(?:sur|Sur)[-\s]+Aube\b", s, re.I):
        return "Bar-an-der-Ôbe"
    if re.match(r"^Bar[-\s]+(?:sur|Sur)[-\s]+Seine\b", s, re.I):
        return "Bar-an-der-Sêne"
    if re.match(r"^Montreuil[-\s]+(?:sur|Sur)[-\s]+Mer\b", s, re.I):
        return "Montreuil-am-Mêr"
    if re.match(r"^Starodub[-\s]+(?:on|On)[-\s]+(?:the|The)[-\s]+Klyazma\b", s, re.I):
        return "Starodûp-an-der-Klêsme"
    if re.match(r"^Yegoryevsk\b", s, re.I):
        return "Guslîtze"
    if re.match(r"^Yuriev\b", s, re.I):
        return "Rostawîtze"
    if re.match(r"^Yuryev\b", s, re.I):
        return "Kolôksche"
    if re.match(r"^Yaroslav\b", s, re.I):
        return "Mletschke"
    if re.match(r"^Rostislavl\b", s, re.I):
        return "Osjôtr"
    if re.match(r"^Danilov\b", s, re.I):
        return "Pelende"
    if re.match(r"^Valenciennes\b", s, re.I):
        return "Valentzîn"
    if re.match(r"^(?:Gravelines|Grevelines)\b", s, re.I):
        return "Grevelingen"
    if re.match(r"^Tournai\b", s, re.I):
        return "Dornîch"
    if re.match(r"^Courtrai\b", s, re.I):
        return "Kortrîch"
    if re.match(r"^Bastogne\b", s, re.I):
        return "Bastenach"
    if re.match(r"^Clervaux\b", s, re.I):
        return "Clierf"
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
    s = re.sub(r"wark\b", "werc", s, flags=re.I)
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
    
    return s


def adapt_european_toponym(name: str) -> str:
    """Adapts a standard historical European settlement name into Rhine-Moselle Franconian phonology."""
    raw = _adapt_european_toponym_raw(name)
    return enforce_tarraconian_sound_laws(raw)


INDIGENOUS_RESTITUTIONS = {
    # Authentic Pre-867 Indigenous Restitutions (Baltic, Finnic, Oghuz, Slavic over foreign colonial/crusader fortresses)
    "b_konigsberg": ("Twangste", "Old Prussian sacred grove and hillfort Twangste (attested before 1255 Teutonic Order castle)", "indigenous_restitution", "Pre-867 native toponym restored over post-867 colonial foundation."),
    "b_reval": ("Lindanisa", "Ancient Finnic/Estonian settlement Lindanisa (attested before 1219 Danish crusade fortress)", "indigenous_restitution", "Pre-867 native toponym restored over post-867 colonial foundation."),
    "b_wesenburg": ("Tarvanpää", "Ancient Estonian stronghold Tarvanpää ('Bull's Head', attested 1226)", "indigenous_restitution", "Pre-867 native toponym restored over post-867 colonial foundation."),
    "b_marienburg": ("Malbork", "Prussian/Slavic settlement Malbork on the Nogat (attested before 1274 Teutonic fortress)", "indigenous_restitution", "Pre-867 native toponym restored over post-867 colonial foundation."),
    "b_allenstein": ("Alna", "Old Prussian hydronym Alna ('Trout River', Alle / Olsztyn)", "indigenous_restitution", "Pre-867 native toponym restored over post-867 colonial foundation."),
    "b_fort_novoaleksandrovkiy": ("Mangystau", "Ancient Turkic/Oghuz peninsula and fortress Mangystau", "indigenous_restitution", "Pre-867 native toponym restored over post-867 colonial foundation."),
    "b_schwanenburg": ("Gulbene", "Ancient Latgalian settlement Gulbene (attested before 1224 Archbishopric castle)", "indigenous_restitution", "Pre-867 native toponym restored over post-867 colonial foundation."),
    "b_neidenburg": ("Niba", "Old Prussian river settlement Niba (attested before 1371 fortress)", "indigenous_restitution", "Pre-867 native toponym restored over post-867 colonial foundation."),
    "b_zvenyhorod": ("Swenigorot", "Ancient 10th-century princely capital gord of the Cherven Cities", "indigenous_restitution", "Pre-867 native toponym restored over post-867 colonial foundation."),
    "b_turku": ("Abô", "Ancient Aura river trading post / Swedish Åbo (Finnish Turku)", "indigenous_restitution", "Pre-867 native toponym restored over post-867 colonial foundation."),
    "b_rikala": ("Rîkale", "Ancient Iron Age hillfort and trading center of Halikko / Rikala", "indigenous_restitution", "Pre-867 native toponym restored over post-867 colonial foundation."),
    "b_porvoo": ("Borchâ", "Ancient Finnic river fortress Borgå (Porvoo)", "indigenous_restitution", "Pre-867 native toponym restored over post-867 colonial foundation."),
    "b_espoo": ("Espô", "Ancient coastal settlement Espoo on the Gulf of Finland", "indigenous_restitution", "Pre-867 native toponym restored over post-867 colonial foundation."),
    "b_ulvila": ("Wûlvildô", "Ancient trading post of Ulvila on the Kokemäenjoki", "indigenous_restitution", "Pre-867 native toponym restored over post-867 colonial foundation."),
    "b_telja": ("Teljê", "Iron Age trading center Teljä of Satakunta", "indigenous_restitution", "Pre-867 native toponym restored over post-867 colonial foundation."),
    "b_czersk": ("Tschêrtzich", "Ancient 11th-century capital gord of the Duchy of Czersk", "indigenous_restitution", "Pre-867 native toponym restored over post-867 colonial foundation."),
    "b_gdov": ("Gdouwe", "Pre-867 hydronym of the Gdovka River (Slavic Gda/Gdova / Finnic Oudova)", "indigenous_restitution", "Pre-867 native toponym restored over post-867 colonial foundation."),
    "b_ostrov": ("Ostrouwe", "Ancient hydronym/toponym of the river island on the Velikaya River (Slavic Ostrov)", "indigenous_restitution", "Pre-867 native toponym restored over post-867 colonial foundation."),
    "b_ostrov_BJA": ("Ostrouwe", "Ancient hydronym/toponym of the river island (Slavic Ostrov)", "indigenous_restitution", "Pre-867 native toponym restored over post-867 colonial foundation."),
    "b_mopet": ("Môtpet", "Indigenous Ainu/Nivkh river mouth settlement Mopet", "indigenous_restitution", "Pre-867 native toponym restored over post-867 colonial foundation."),

    # Classical Antiquity & Pre-867 Historical Restitutions (Greco-Roman, Celtic, Armenian, Tibetan, Early Medieval)
    "b_mistra": ("Amûklê", "Ancient Achaean polis and sacred sanctuary of Apollo Amyklaios on Mount Taygetos (in-game: Mistra)", "classical_antiquity", "Authentic Classical Antiquity / Pre-867 Historical Polis (Amyclae)."),
    "b_aqmescit": ("Neâpolis", "Ancient 3rd-century BC royal capital Scythian Neapolis on the Salgir River (in-game: Aqmescit)", "classical_antiquity", "Authentic Classical Antiquity / Pre-867 Historical Civitas (Scythian Neapolis)."),
    "b_ravensburg": ("Altdorf", "Ancestral 750 AD Welf estate and monastery of Altdorf / Weingarten on the Schussen (in-game: Ravensburg)", "classical_antiquity", "Authentic Pre-867 Historical Settlement (attested 750 AD)."),
    "b_vezelay": ("Wêzelê", "Ancient Vizeliacum / Benedictine Abbey of Sainte-Marie-Madeleine at Vézelay (attested 858 AD)", "classical_antiquity", "Authentic Pre-867 Historical Monastic Abbey (founded 858 AD)."),
    "b_morvan": ("Avalûn", "Ancient Gallo-Roman Aballo / fortified caput of the Avalois on the Cousin (attested 843 AD)", "classical_antiquity", "Authentic Classical Antiquity / Pre-867 Gallo-Roman Civitas."),
    "b_autun": ("Ostûn", "Ancient Augustodunum / Episcopal See of Autun (attested secondary variant of the Bishopric of Avalois)", "classical_antiquity", "Authentic Classical Antiquity / Pre-867 Roman Civitas."),
    "b_konstanz": ("Konstantz", "Roman Constantia / Episcopal See of Lake Constance (attested 585 AD)", "classical_antiquity", "Authentic Classical Antiquity / Pre-867 Roman Civitas."),
    "b_sankt_gallen": ("Zant-Gallen", "Imperial Abbey and monastic republic of Saint Gall (attested 612 AD)", "classical_antiquity", "Authentic Pre-867 Monastic Abbey (founded 612 AD)."),
    "b_evora": ("Êvore", "Ancient Roman Ebora Liberalitas Julia / major episcopal see", "classical_antiquity", "Authentic Classical Antiquity / Pre-867 Roman Civitas."),
    "b_beja": ("Bêdsche", "Ancient Roman Pax Julia / Visigothic and Andalusian Bājah (Beja)", "classical_antiquity", "Authentic Classical Antiquity / Pre-867 Roman Civitas."),
    "b_sisak": ("Sissek", "Roman Siscia / 9th-century seat of Duke Ljudevit Posavski", "classical_antiquity", "Authentic Classical Antiquity / Pre-867 Roman Civitas."),
    "b_linlithgow": ("Aberkôrn", "Ancient Northumbrian episcopal see Abercorn on the Forth (attested 681 AD)", "classical_antiquity", "Authentic Pre-867 Northumbrian Episcopal See (attested 681 AD)."),
    "b_falkirk": ("Fawkirk", "Ancient Brythonic/Gaelic church site Egglesbreth on the Antonine Wall", "classical_antiquity", "Authentic Pre-867 Roman Wall Site."),
    "b_leer": ("Lêre", "Ancient 8th-century Frisian trading gau settlement Leer on the Leda (attested 791 AD)", "classical_antiquity", "Authentic Pre-867 Frisian Missionary Center (attested 791 AD)."),
    "b_brandenburg": ("Brennabor", "Ancient princely fortress Brennabor of the Slavic Hevelli on the Havel", "classical_antiquity", "Authentic Pre-867 Slavic Princely Gord."),
    "b_cadyou": ("Kadjo", "Ancient Strathclyde Brythonic comital center Cadzow (Cadyou)", "classical_antiquity", "Authentic Pre-867 Strathclyde Royal Center."),
    "b_uisneach": ("Uisnech", "Ancient sacred royal hill and navel of Ireland (Aill na Mireann)", "classical_antiquity", "Authentic Prehistoric Sacred Royal Hill."),
    "b_bregenz": ("Briganz", "Ancient Roman naval base and civitas Brigantium on Lake Constance (attested 15 BC)", "classical_antiquity", "Authentic Classical Antiquity / Pre-867 Roman Civitas."),
    "b_lichtenfels": ("Liechtenfels", "Ancient Radenzgau fortress on the Main (Lichtenfels)", "classical_antiquity", "Authentic Pre-867 Radenzgau Fortress."),
    "b_slupsk": ("Slûptzich", "Ancient Pomeranian tribal gord Słupsk on the Słupia", "classical_antiquity", "Authentic 9th-Century Slavic Gord."),
    "b_koszalin": ("Cöslîn", "Ancient Pomeranian trading center Koszalin near the Baltic coast", "classical_antiquity", "Authentic Early Medieval Slavic Settlement."),
    "b_perekop": ("Tâfros", "Ancient Greek trench and fortress Taphros on the Isthmus of Crimea", "classical_antiquity", "Authentic Classical Antiquity Greek Fortress."),
    "b_bonifacio": ("Bonifâtzo", "Historic 828 AD citadel of Count Boniface II of Tuscany (Bonifacio)", "classical_antiquity", "Authentic Pre-867 Citadel (attested 828 AD)."),
    "b_vecchio": ("Porto-Wêckjo", "Ancient Roman port Portus Syracusanus / Porto-Vecchio", "classical_antiquity", "Authentic Classical Antiquity Roman Port."),
    "b_coupar_angus": ("Skône", "Ancient coronation moot and abbey of the Kings of Alba (Scone)", "classical_antiquity", "Authentic Pre-867 Royal Moot (attested 843 AD)."),
    "b_wilton": ("Wiltûn", "Ancient Anglo-Saxon royal burh and seat of the Wilsæte on the Wylye", "classical_antiquity", "Authentic Pre-867 Anglo-Saxon Royal Burh (attested 802 AD)."),
    "b_salisbury": ("Sêreburch", "Ancient Iron Age hillfort and Roman Sorviodunum / Old Sarum (Old English Searoburh)", "classical_antiquity", "Authentic Pre-867 Iron Age / Roman / Saxon Fortress Searoburh."),
    "b_minden": ("Minden", "Ancient episcopal see and cathedral chapter of Minden on the Weser (attested 798 AD)", "classical_antiquity", "Authentic Pre-867 Episcopal See (founded 798 AD)."),
    "b_chartres": ("Schartres", "Classical Carnutes civitas and cathedral city Autricum / Chartres", "classical_antiquity", "Authentic Classical Antiquity / Pre-867 Civitas."),
    "b_dreux": ("Drôchs", "Ancient Gaulish capital of the Durocasses / comital castle Dreux", "classical_antiquity", "Authentic Classical Antiquity / Pre-867 Gaulish Civitas."),
    "b_tuam": ("Tuâm", "Ancient monastic foundation and metropolitan archiepiscopal see of Tuam", "classical_antiquity", "Authentic Pre-867 Monastic See (founded c. 501 AD)."),
    "b_pergamon": ("Pergamôn", "Ancient Hellenistic royal capital and acropolis of Pergamon", "classical_antiquity", "Authentic Classical Antiquity / Pre-867 Historical Polis."),
    "b_phocaea": ("Phôkêe", "Ancient Ionian maritime city Phocaea on the Aegean coast", "classical_antiquity", "Authentic Classical Antiquity / Pre-867 Historical Polis."),
    "b_nikomedia": ("Nikomêdje", "Ancient Bithynian and Roman imperial capital Nicomedia", "classical_antiquity", "Authentic Classical Antiquity / Pre-867 Historical Civitas."),
    "b_chalcedon": ("Kalkêdôn", "Ancient Megarian colony and Ecumenical Council city Chalcedon on the Bosphorus", "classical_antiquity", "Authentic Classical Antiquity / Pre-867 Historical Polis."),
    "b_sardes": ("Sârdes", "Ancient Lydian royal capital and acropolis Sardis on the Pactolus", "classical_antiquity", "Authentic Classical Antiquity / Pre-867 Historical Civitas."),
    "b_philadelphia": ("Philadelphîe", "Ancient Hellenistic fortress city Philadelphia in Lydia", "classical_antiquity", "Authentic Classical Antiquity / Pre-867 Historical Polis."),
    "b_lacedaemonia": ("Lakedêmôn", "Classical Sparta / Lacedaemon on the Eurotas", "classical_antiquity", "Authentic Classical Antiquity / Pre-867 Historical Polis."),
    "b_sagalassus": ("Sagalâs", "Ancient Pisidian mountain metropolis Sagalassos", "classical_antiquity", "Authentic Classical Antiquity / Pre-867 Historical Polis."),
    "b_sozopolis": ("Sôsôpel", "Ancient Byzantine episcopal fortress Sozopolis in Pisidia", "classical_antiquity", "Authentic Classical Antiquity / Pre-867 Historical Civitas."),
    "b_manzikert": ("Manzikêrt", "Ancient Armenian fortress city and battlefield Manzikert", "classical_antiquity", "Authentic Pre-867 Historical Armenian Fortress."),
    "b_musch": ("Mûsch", "Ancient Armenian capital of Taron on the Euphrates plain", "classical_antiquity", "Authentic Pre-867 Historical Armenian Capital."),
    "b_armagh": ("Armâch", "Ancient ecclesiastical capital of Ireland and primary see of St Patrick (Ard Mhacha)", "classical_antiquity", "Authentic Pre-867 Episcopal See (founded 445 AD)."),
    "b_dundalk": ("Dundalk", "Ancient fortified ford Dún Dealgan of the Castletown River", "classical_antiquity", "Authentic Pre-867 Prehistoric Irish Fortress."),
    "b_lhasa": ("Lâse", "Ancient sacred Tibetan imperial capital and Jokhang cathedral city", "classical_antiquity", "Authentic Pre-867 Historical Tibetan Capital (built 647 AD)."),
    "b_potala": ("Pôtâla", "Tibetan palace and religious fortress on the Red Hill / Marpori", "classical_antiquity", "Authentic Pre-867 Historical Tibetan Fortress (built 637 AD)."),
    "b_echternach": ("Echternach", "Ancient Benedictine Abbey of Echternach founded 698 AD by St Willibrord", "classical_antiquity", "Authentic Pre-867 Benedictine Abbey (founded 698 AD)."),
    "b_kaiserswerth": ("Keiserswert", "Ancient Roman and Merovingian Rhine island fortress Kaiserswerth", "classical_antiquity", "Authentic Pre-867 Merovingian Fortress."),
    "b_dinant": ("Dînant", "Ancient Celtic and Merovingian Mosan trading port Dinant", "classical_antiquity", "Authentic Pre-867 Mosan Trading Port."),
    "b_freising": ("Frîsinge", "Ancient Agilolfing ducal seat and prince-bishopric Freising on the Isar (attested 739 AD)", "classical_antiquity", "Authentic Pre-867 Ducal See (attested 739 AD)."),
    "b_maguelone": ("Magelône", "Ancient coastal episcopal island see of Maguelone", "classical_antiquity", "Authentic Classical Antiquity Episcopal Island See."),
    "b_liubice": ("Liubice", "Ancient Obotrite Slavic princely seat Liubice on the Trave", "classical_antiquity", "Authentic Pre-867 Obotrite Slavic Seat."),
    "b_sieciechow": ("Sitzichow", "Ancient Benedictine abbey and fortress Sieciechów", "classical_antiquity", "Authentic Pre-867 Benedictine Abbey."),
    "b_poltava": ("Altâwe", "Ancient 9th-century fortress Ltava / Poltava on the Vorskla", "classical_antiquity", "Authentic 9th-Century Fortress."),
    "b_rottweil": ("Rôtwîl", "Ancient Roman municipium Arae Flaviae / oldest chartered town of Swabia (Rottweil)", "classical_antiquity", "Authentic Classical Antiquity Roman Municipium."),
    "b_brysis": ("Brüsis", "Ancient Byzantine fortress and bishopric Brysis in Thrace", "classical_antiquity", "Authentic Classical Antiquity Byzantine Fortress."),
    "b_arkadiopolis": ("Arkadîôpel", "Ancient Roman-Byzantine episcopal city Arcadiopolis on the Ergene", "classical_antiquity", "Authentic Classical Antiquity Byzantine Civitas."),
    "b_namur": ("Nâmen", "Ancient junction citadel Namur at the confluence of Sambre and Meuse", "classical_antiquity", "Authentic Classical Antiquity Junction Citadel."),
    "b_peremyshl": ("Peremyschl", "Ancient princely gord Peremyshl on the San", "classical_antiquity", "Authentic Ancient Slavic Princely Gord."),
    "b_przemysl": ("Przemîschel", "Historic crossing settlement Przemysl", "classical_antiquity", "Authentic Ancient Slavic Settlement."),
    "b_zaslavl": ("Saslâwl", "Ancient comital gord of Zaslavl on the Horyn", "classical_antiquity", "Authentic Ancient Slavic Gord."),
    "b_zvyahel": ("Swîâhel", "Ancient comital gord Zvyahel on the Sluch", "classical_antiquity", "Authentic Ancient Slavic Gord."),
    "b_kolodiazhen": ("Kolodjâschen", "Ancient fortress Kolodiazhen in Volhynia", "classical_antiquity", "Authentic Ancient Slavic Fortress."),
    "b_eilenburg": ("Îlenburch", "Historic Mulde fortress Eilenburg in Osterland", "classical_antiquity", "Authentic Ancient Slavic Gord."),
    "b_colditz": ("Colditz", "Ancient castle Colditz on the Zwickauer Mulde", "classical_antiquity", "Authentic Ancient Slavic Castle."),
    "b_hradyzk": ("Gradischk", "Ancient Dnieper fortress Gradischk", "classical_antiquity", "Authentic Ancient Dnieper Gord."),
    "b_lasta": ("Laste", "Ancient mountainous province and lordship of Lasta", "classical_antiquity", "Authentic Pre-867 Lordship."),
    "b_lalibela": ("Lalîbela", "Monolithic rock-hewn church center Lalibela", "classical_antiquity", "Authentic Historic Church Center."),
    "b_adafa": ("Rôhe", "Ancient capital of the Zagwe Dynasty Roha", "classical_antiquity", "Authentic Ancient Zagwe Capital."),
    "b_algiers": ("Alschîr", "Historic Zirid island fortress al-Jazā'ir (Algiers)", "classical_antiquity", "Authentic Ancient Island Fortress."),
    "b_gazargamo": ("Gasargamu", "Historic Kanem-Bornu capital Birni Gazargamo", "classical_antiquity", "Authentic Historic Capital."),
    "b_bergh": ("Berch", "Ancestral castle Burg an der Wupper / County of Berg", "classical_antiquity", "Authentic Ancestral Comital Seat."),
    "b_stezyca": ("Stensitz", "Historic Vistula castellan seat Stężyca", "classical_antiquity", "Authentic Vistula Castellan Seat."),
    "b_bartenstein": ("Barte", "Old Prussian tribal territory and river basin of Bartia (replacing 1326 Teutonic castle Bartenstein)", "option_b_hydronym", "Teutonic Order castle Bartenstein built in 1326 in Bartia. Resolved via Option B to the authentic Old Prussian regional stem Barte."),
    "b_rothenburg": ("Rôtenburch", "Imperial castle and burgh Rothenburg ob der Tauber", "classical_antiquity", "Authentic Imperial Castle."),
    "b_hohenberg": ("Hôhenberch", "Comital ancestral fortress Hohenberg on the Neckar", "classical_antiquity", "Authentic Comital Fortress."),
    "b_gleichenstein": ("Glêichenstên", "Comital hill castle Gleichenstein in the Eichsfeld", "classical_antiquity", "Authentic Comital Castle."),
    "b_muhlhausen": ("Mülhûsen", "Imperial free city and Frankish royal court Mühlhausen on the Unstrut", "classical_antiquity", "Authentic Frankish Royal Court."),
    "b_jinguan": ("Goltpfôrte", "Logographic semantic calque for Jīnguān (Golden Gate/Pass)", "classical_antiquity", "Logographic semantic calque."),
    "b_chengmai": ("Luterweit", "Logographic semantic calque for Chéngmài (Clear Progress)", "classical_antiquity", "Logographic semantic calque."),

    # Burden of Proof on Antiquity: Pre-867 Chronicle Gords, Ancient Hydronyms & Hillfort Restitutions
    # White Rus' & Polesia
    "b_zhlobin": ("Strêschew", "Chronicle border gord & Iron Age hillfort Stary Gorodok on the Dnieper (attested 1127 Strezhev / modern Streshin) (in-game: Zhlobin)", "chronicle_gord", "1654 Cossack fortress Zhlobin fails Burden of Proof on Antiquity; resolved to 1127 chronicle gord Strezhev."),
    "b_kalinkavichy": ("Ipat", "Ancient pre-867 Ipa River basin (in-game: Kalinkavichy)", "option_b_hydronym", "1560 village Kalinkavichy fails Burden of Proof on Antiquity; resolved to ancient Ipa hydronym."),
    "b_sarny": ("Slûtsch", "Ancient Sluch River basin (in-game: Sarny)", "option_b_hydronym", "1670 village Sarny fails Burden of Proof on Antiquity; resolved to ancient Sluch hydronym."),
    "b_selo": ("Stwîga", "Stvyha River basin in the Pripyat marshes (in-game: Selo)", "option_b_hydronym", "Generic settlement label 'Selo' resolved to ancient Stvyha hydronym."),
    "b_ovruch": ("Wrûtsch", "Ancient Drevlian chronicle gord Vruchiy (attested 977 in Primary Chronicle) (in-game: Ovruch)", "chronicle_gord", "Authentic 10th-century chronicle gord of the Drevlians."),
    "b_mazyr": ("Masîr", "Ancient Pripyat chronicle gord Mazyr (attested 1155 in Hypatian Chronicle) (in-game: Mazyr)", "chronicle_gord", "Authentic 12th-century chronicle gord on the Pripyat."),
    "b_naroulia": ("Narôwlja", "Narovlyanka River basin at the Pripyat bend (in-game: Naroulia)", "option_b_hydronym", "18th-century private estate Naroulia fails Burden of Proof on Antiquity; resolved to Narovlyanka hydronym."),
    "b_lelchytsy": ("Ûbort", "Ubort River basin in the Polesian lowlands (in-game: Lelchytsy)", "option_b_hydronym", "1569 charter settlement Lelchytsy fails Burden of Proof on Antiquity; resolved to ancient Ubort hydronym."),
    "b_stepan": ("Horîn", "Horyn River basin (attested 1292 gord Stepan) (in-game: Stepan)", "option_b_hydronym", "13th-century settlement resolved to ancient Horyn hydronym."),
    "b_liubeshiv": ("Stokhît", "Stokhid River basin ('Hundred Paths' marsh river) (in-game: Liubeshiv)", "option_b_hydronym", "1484 private estate Liubeshiv fails Burden of Proof on Antiquity; resolved to Stokhid hydronym."),
    "b_lyubech": ("Liubêtsch", "Ancient 9th-century chronicle gord Lyubech on the Dnieper (attested 882 in Primary Chronicle) (in-game: Lyubech)", "chronicle_gord", "Authentic 9th-century chronicle gord on the Dnieper trade route."),
    "b_gomel": ("Gômê", "Ancient Radimich chronicle gord Gomiy at the Homeyka/Sozh confluence (attested 1142 in Hypatian Chronicle) (in-game: Gomel)", "chronicle_gord", "Authentic 12th-century Radimich chronicle gord."),
    "b_unenezh": ("Unenetsch", "Ancient chronicle gord Unenezh in Chernigov land (attested 1147 in Hypatian Chronicle) (in-game: Unenezh)", "chronicle_gord", "Authentic 12th-century chronicle gord."),
    "b_surazichi": ("Îput", "Iput River basin (in-game: Surazichi)", "option_b_hydronym", "17th-century settlement Surazh fails Burden of Proof on Antiquity; resolved to Iput hydronym."),
    "b_lida": ("Lidêja", "Lideya River basin (replacing 1323 Gediminas castle Lida) (in-game: Lida)", "option_b_hydronym", "1323 castle Lida fails Burden of Proof on Antiquity; resolved to Lideya hydronym."),
    "b_sokolka": ("Sokôlda", "Sokołda River basin in the Knyszyn Forest (in-game: Sokolka)", "option_b_hydronym", "16th-century village Sokolka fails Burden of Proof on Antiquity; resolved to Sokołda hydronym."),
    "b_bielastock": ("Bêla", "Biała River basin ('White River') (replacing 1437 settlement Bialystok) (in-game: Bielastock)", "option_b_hydronym", "1437 settlement Bialystok fails Burden of Proof on Antiquity; resolved to ancient Biała hydronym."),
    "b_lahishyn": ("Jâselda", "Yaselda River basin (replacing 1495 village Lohishyn) (in-game: Lahishyn)", "option_b_hydronym", "1495 estate Lohishyn fails Burden of Proof on Antiquity; resolved to ancient Yaselda hydronym."),
    "b_luninets": ("Zwîne", "Tsvna River basin in Pinsk marshlands (replacing 1449 village Luninets) (in-game: Luninets)", "option_b_hydronym", "1449 village Luninets fails Burden of Proof on Antiquity; resolved to Tsvna hydronym."),
    "b_zhytkavichy": ("Hlûschitza", "Glushitsa stream and marshes of Turov land (in-game: Zhytkavichy)", "option_b_hydronym", "1500 estate Zhytkavichy fails Burden of Proof on Antiquity; resolved to Glushitsa hydronym."),
    "b_mikashevichy": ("Lan", "Lan River basin (replacing 1785 private estate Mikashevichy) (in-game: Mikashevichy)", "option_b_hydronym", "1785 private estate Mikashevichy fails Burden of Proof on Antiquity; resolved to Lan hydronym."),
    "b_rechytsa": ("Rechtzîe", "Rechitsa stream confluence with the Dnieper (attested 1213 in Novgorod Chronicle) (in-game: Rechytsa)", "chronicle_gord", "Authentic Dregovich chronicle settlement on the Dnieper."),
    "b_lahoysk": ("Logôtsk", "Logozhsk on the Gaina River (attested 1078 in Vladimir Monomakh's Pouchenie) (in-game: Lahoysk)", "chronicle_gord", "Authentic 11th-century chronicle gord."),
    "b_zaslawye": ("Isjaslâwl", "Izyaslavl on the Svisloch (founded 985 by Grand Prince Vladimir for Rogneda) (in-game: Zaslawye)", "chronicle_gord", "Authentic 10th-century chronicle fortress of Rogneda."),
    "b_drutsk": ("Drûtzich", "Drutsk on the Drut River (attested 1092 in Primary Chronicle) (in-game: Drutsk)", "chronicle_gord", "Authentic 11th-century chronicle princely center."),
    "b_drysa": ("Drîse", "Drysa River confluence with the Western Dvina (in-game: Drysa)", "option_b_hydronym", "Ancient Drysa hydronym at the Dvina confluence."),
    "b_myory": ("Mêre", "Lake Myory and Meryanka stream (replacing 1514 village Myory) (in-game: Myory)", "option_b_hydronym", "1514 village Myory fails Burden of Proof on Antiquity; resolved to Lake Myory hydronym."),
    "b_vetrino": ("Ekimân", "Ancient Dvina crossing and settlement Ekimania (in-game: Vetrino)", "indigenous_restitution", "Late village Vetrino fails Burden of Proof on Antiquity; resolved to ancient Dvina crossing Ekimania."),
    "b_hlybokaye": ("Berêswets", "Ancient Berezvechye on Lake Berezovitsa (in-game: Hlybokaye)", "option_b_hydronym", "1414 private estate Hlybokaye fails Burden of Proof on Antiquity; resolved to ancient Berezvechye."),
    "b_haradok": ("Horodôtz", "Ancient Gorodok hillfort on the Gorozhanka (in-game: Haradok)", "chronicle_gord", "Authentic ancient Slavic hillfort."),
    "b_dorogobyzh": ("Dorogobûsch", "Dorogobuzh on the Dnieper (attested 1150 in Prince Rostislav's charter) (in-game: Dorogobyzh)", "chronicle_gord", "Authentic 12th-century Smolensk Dnieper gord."),
    "b_mstislavl": ("Wîchra", "Vikhra River basin (replacing 1135 fortress Mstislavl) (in-game: Mstislavl)", "option_b_hydronym", "1135 foundation Mstislavl fails Burden of Proof on Antiquity; resolved to ancient Vikhra hydronym."),
    "b_yelnya": ("Ôverdêsne", "Upper Desna River basin (attested 1150 Yelnya) (in-game: Yelnya)", "option_b_hydronym", "1150 charter Yelnya resolved to Upper Desna hydronym."),
    "b_vyazma": ("Wjâsma", "Vyazma River basin (attested 1239 Life of St. Euphrosyne) (in-game: Vyazma)", "option_b_hydronym", "Pre-867 Vyazma hydronym on the Volga-Dnieper watershed."),
    "b_velizh": ("Wêlisa", "Velizhka River basin at the Western Dvina (in-game: Velizh)", "option_b_hydronym", "1536 fortress Velizh fails Burden of Proof on Antiquity; resolved to Velizhka hydronym."),
    "b_dukhovshchina": ("Tzârewitza", "Tsarevitsa River basin (in-game: Dukhovshchina)", "option_b_hydronym", "1777 town Dukhovshchina fails Burden of Proof on Antiquity; resolved to Tsarevitsa hydronym."),
    "b_klimavichy": ("Lôbdscha", "Lobzha River basin (in-game: Klimavichy)", "option_b_hydronym", "1581 village Klimavichy fails Burden of Proof on Antiquity; resolved to Lobzha hydronym."),
    "b_cherykaw": ("Sôsch", "Sozh River basin (in-game: Cherykaw)", "option_b_hydronym", "1460 village Cherykaw fails Burden of Proof on Antiquity; resolved to ancient Sozh hydronym."),
    "b_lotoshino": ("Lôbe", "Lob River basin (in-game: Lotoshino)", "option_b_hydronym", "1478 estate Lotoshino fails Burden of Proof on Antiquity; resolved to Lob hydronym."),
    "b_zubstov": ("Wâsûsa", "Vazuza River confluence with the Volga (attested 1216 in Novgorod Chronicle) (in-game: Zubstov)", "option_b_hydronym", "Pre-867 Vazuza hydronym at the Volga junction."),
    "b_andreapol": ("Ôverdwîne", "Upper Western Dvina headwaters (in-game: Andreapol)", "option_b_hydronym", "1906 railway station Andreapol fails Burden of Proof on Antiquity; resolved to Upper Dvina hydronym."),
    "b_ozerski": ("Sêliger", "Lake Seliger basin (in-game: Ozerski)", "option_b_hydronym", "Generic settlement Ozerski resolved to Lake Seliger hydronym."),

    # Baltic, Prussia & Livonia
    "b_graudenz": ("Kwidzîn", "Old Prussian tribal settlement Kwidzîn / Queden on the Liwa (replacing 1233 Teutonic castle Marienwerder) (in-game: Graudenz)", "indigenous_restitution", "1233 Teutonic castle Marienwerder fails Burden of Proof on Antiquity; restored to native Old Prussian Kwidzîn."),
    "b_wislana": ("Wîselwerder", "Vistula Spit and Nogat river delta (replacing Stutthof) (in-game: Wislana)", "option_b_hydronym", "Late estate Stutthof fails Burden of Proof on Antiquity; resolved to Vistula delta hydronym Wîselwerder."),
    "b_mohrungen": ("Marînge", "Old Prussian Lake Marąg basin (replacing 1302 Teutonic castle Mohrungen) (in-game: Mohrungen)", "indigenous_restitution", "1302 Teutonic castle Mohrungen fails Burden of Proof on Antiquity; restored to Old Prussian Lake Marąg."),
    "b_braunsberg": ("Passarîa", "Old Prussian Pasłęka River basin in Warmia (replacing 1240 Teutonic castle Braunsberg) (in-game: Braunsberg)", "indigenous_restitution", "1240 Teutonic castle Braunsberg fails Burden of Proof on Antiquity; restored to Old Prussian Pasłęka."),
    "b_paterswalde": ("Tapiouwe", "Old Prussian Pregolya river settlement Tapiow (replacing 1258 Teutonic castle Tapiau) (in-game: Paterswalde)", "indigenous_restitution", "1258 Teutonic castle Tapiau fails Burden of Proof on Antiquity; restored to Old Prussian Tapiow."),
    "b_ostlandsberg": ("Welouwe", "Old Prussian Pregolya/Lava fortress Welow (replacing 1255 Teutonic castle Wehlau) (in-game: Ostlandsberg)", "indigenous_restitution", "1255 Teutonic castle Wehlau fails Burden of Proof on Antiquity; restored to Old Prussian Welow."),
    "b_insterburg": ("Instre", "Old Prussian Inster River confluence (replacing 1336 Teutonic castle Insterburg) (in-game: Insterburg)", "indigenous_restitution", "1336 Teutonic castle Insterburg fails Burden of Proof on Antiquity; restored to Old Prussian Inster."),
    "b_rastenburg": ("Raste", "Old Prussian tribal settlement Raste (replacing 1329 Teutonic castle Rastenburg) (in-game: Rastenburg)", "indigenous_restitution", "1329 Teutonic castle Rastenburg fails Burden of Proof on Antiquity; restored to Old Prussian Raste."),
    "b_briesen": ("Wonbrscheschno", "Ancient Slavic/Prussian settlement Wąbrzeźno (in-game: Briesen)", "indigenous_restitution", "Pre-867 native toponym restored over Teutonic Order Briesen."),
    "b_brodnica": ("Drwêntza", "Drwęca River crossing (replacing 1298 Teutonic castle Strasburg) (in-game: Brodnica)", "option_b_hydronym", "1298 Teutonic castle Strasburg fails Burden of Proof on Antiquity; resolved to ancient Drwęca hydronym."),
    "b_ortelsburg": ("Pessûne", "Old Prussian Galindian lake settlement (replacing 1360 Teutonic castle Ortelsburg) (in-game: Ortelsburg)", "indigenous_restitution", "1360 Teutonic castle Ortelsburg fails Burden of Proof on Antiquity; restored to Old Prussian Galindian stem."),
    "b_lyck": ("Lêke", "Ancient Old Prussian/Yotvingian Ełk River basin (replacing 1398 Teutonic castle Lyck) (in-game: Lyck)", "indigenous_restitution", "1398 Teutonic castle Lyck fails Burden of Proof on Antiquity; restored to Old Prussian river stem Lêke."),
    "b_mitau": ("Jêlgawa", "Ancient Semigallian Lielupe river crossing (replacing 1265 Livonian castle Mitau) (in-game: Mitau)", "indigenous_restitution", "1265 Livonian castle Mitau fails Burden of Proof on Antiquity; restored to native Jelgava."),
    "b_bauska": ("Bôwse", "Ancient Semigallian Mūša/Mēmele river confluence (replacing 1443 Livonian castle Bauska) (in-game: Bauska)", "indigenous_restitution", "1443 Livonian castle Bauska fails Burden of Proof on Antiquity; restored to native Semigallian stem."),
    "b_neuenburg": ("Jaunepel", "Curonian hillfort Jaunpils (replacing 14th-century Livonian castle Neuenburg) (in-game: Neuenburg)", "indigenous_restitution", "14th-century Livonian castle Neuenburg fails Burden of Proof on Antiquity; restored to Curonian hillfort."),
    "b_tilsit": ("Tîlse", "Old Prussian Tilse River confluence with the Nemunas (replacing 1288 Teutonic castle Tilsit) (in-game: Tilsit)", "indigenous_restitution", "1288 Teutonic castle Tilsit fails Burden of Proof on Antiquity; restored to Old Prussian Tilse."),
    "b_taurage": ("Jûra", "Jūra River basin (replacing 1507 village Tauragė) (in-game: Taurage)", "option_b_hydronym", "1507 settlement Tauragė fails Burden of Proof on Antiquity; resolved to ancient Jūra hydronym."),
    "b_rauna": ("Rôwne", "Ancient Latgalian Rauna river hillfort (replacing 1262 Archbishop castle Ronneburg) (in-game: Rauna)", "indigenous_restitution", "1262 Archbishop castle Ronneburg fails Burden of Proof on Antiquity; restored to native Rauna hillfort."),
    "b_cesvaine": ("Sessouwe", "Ancient Latgalian hillfort Cessowe (attested 1209) (replacing Sesswegen) (in-game: Cesvaine)", "indigenous_restitution", "Authentic 1209 Latgalian hillfort."),
    "b_lennewarden": ("Lênewarde", "Ancient Livonian Daugava hillfort Lielvārde (in-game: Lennewarden)", "indigenous_restitution", "Authentic ancient Livonian Daugava hillfort."),
    "b_jekabpils": ("Sêlburch", "Ancient Selonian Daugava crossing and hillfort Sēlpils (replacing 1670 town Jakobstadt) (in-game: Jekabpils)", "indigenous_restitution", "1670 ducal town Jakobstadt fails Burden of Proof on Antiquity; restored to ancient Selonian Sēlpils."),
    "b_rezekne": ("Rêsne", "Ancient Latgalian Rēzekne hillfort on the Rēzekne river (replacing 1285 Livonian castle Rositten) (in-game: Rezekne)", "indigenous_restitution", "1285 Livonian castle Rositten fails Burden of Proof on Antiquity; restored to native Latgalian hillfort."),
    "b_kandava": ("Kandouwe", "Ancient Curonian hillfort Candeve (attested 1230 in treaty of Balduin von Alna) (in-game: Kandava)", "indigenous_restitution", "Authentic Curonian hillfort."),
    "b_jurbarkas": ("Jurbarch", "Nemunas river crossing (replacing 1259 Teutonic castle Georgenburg) (in-game: Jurbarkas)", "indigenous_restitution", "1259 Teutonic castle Georgenburg fails Burden of Proof on Antiquity; restored to native Nemunas crossing."),

    # Novgorod & North Russia
    "b_noteborg": ("Nêwewerder", "Ancient Neva River island at Lake Ladoga (replacing 1323 Oreshek fortress) (in-game: Noteborg)", "option_b_hydronym", "1323 fortress Oreshek fails Burden of Proof on Antiquity; resolved to Neva island hydronym Nêwewerder."),
    "b_koporye": ("Kôpôre", "Ancient Votic hillfort of the Izhora plateau (attested 1237) (in-game: Koporye)", "indigenous_restitution", "Authentic Votic hillfort on the Izhora plateau."),
    "b_yama": ("Lûge", "Luga River basin (replacing 1384 Novgorod fortress Yama / Kingisepp) (in-game: Yama)", "option_b_hydronym", "1384 fortress Yama fails Burden of Proof on Antiquity; resolved to ancient Luga hydronym."),
    "b_cherepovets": ("Schêksna", "Sheksna River basin at Lake Beloye (replacing 1362 Voskresensky monastery Cherepovets) (in-game: Cherepovets)", "option_b_hydronym", "1362 monastery Cherepovets fails Burden of Proof on Antiquity; resolved to ancient Sheksna hydronym."),
    "b_kirishi": ("Ôverwolchouwe", "Upper Volkhov River basin (replacing 1693 village Kirishi) (in-game: Kirishi)", "option_b_hydronym", "1693 village Kirishi fails Burden of Proof on Antiquity; resolved to Upper Volkhov hydronym."),
    "b_borovichi": ("Mste", "Msta River rapids trade route (replacing 1495 pogost Borovichi) (in-game: Borovichi)", "option_b_hydronym", "1495 pogost Borovichi fails Burden of Proof on Antiquity; resolved to ancient Msta river hydronym."),
    "b_podporozhye": ("Swîre", "Svir River rapids (replacing 1563 village Podporozhye) (in-game: Podporozhye)", "option_b_hydronym", "1563 village Podporozhye fails Burden of Proof on Antiquity; resolved to ancient Svir hydronym."),
    "b_vyshny_volochyok": ("Wolôch", "Ancient Tsna/Msta portage of the Valdai Hills (in-game: Vyshny Volochyok)", "option_b_hydronym", "1471 settlement Vyshny Volochyok fails Burden of Proof on Antiquity; resolved to ancient Valdai portage Wolôch."),
    "b_dedovichi": ("Schêlôn", "Shelon River basin (replacing 1901 railway station Dedovichi) (in-game: Dedovichi)", "option_b_hydronym", "1901 railway station Dedovichi fails Burden of Proof on Antiquity; resolved to ancient Shelon hydronym."),
    "b_lyuban": ("Tîgôda", "Tigoda River basin (replacing 1499 village Lyuban) (in-game: Lyuban)", "option_b_hydronym", "1499 village Lyuban fails Burden of Proof on Antiquity; resolved to Tigoda hydronym."),
    "b_soltsy": ("Salzbrûch", "Shelon river salt crossing (attested 1239 under Alexander Nevsky) (in-game: Soltsy)", "indigenous_restitution", "Authentic 13th-century salt ford on the Shelon."),

    # Ruthenia & Galicia-Volhynia
    "b_boryspil": ("Alte", "Ancient chronicle river Alta, site of 1019 & 1068 battles (replacing 1590 town Boryspil) (in-game: Boryspil)", "option_b_hydronym", "1590 town Boryspil fails Burden of Proof on Antiquity; resolved to ancient Alta river."),
    "b_zolotonosha": ("Gûldenbach", "Zolotonoshka River basin ('Golden Stream') (in-game: Zolotonosha)", "option_b_hydronym", "1576 settlement Zolotonosha fails Burden of Proof on Antiquity; resolved to Zolotonoshka hydronym."),
    "b_haisyn": ("Sôbe", "Sob River basin (in-game: Haisyn)", "option_b_hydronym", "1545 settlement Haisyn fails Burden of Proof on Antiquity; resolved to Sob hydronym."),
    "b_yampil": ("Ôverdnester", "Dniester River rapids of Podolia (in-game: Yampil)", "option_b_hydronym", "16th-century settlement Yampil fails Burden of Proof on Antiquity; resolved to Dniester rapids hydronym."),
    "b_ivankiv": ("Teterîw", "Teteriv River crossing (in-game: Ivankiv)", "option_b_hydronym", "1589 private estate Ivankiv fails Burden of Proof on Antiquity; resolved to Teteriv hydronym."),
    "b_kaniv": ("Kanouwe", "Ancient chronicle gord Kaniv on the Dnieper (attested 1144 in Hypatian Chronicle) (in-game: Kaniv)", "chronicle_gord", "Authentic 12th-century chronicle gord."),
    "b_suvorov": ("Tscherêpet", "Cherepet River basin (replacing 1949 Soviet industrial town Suvorov) (in-game: Suvorov)", "option_b_hydronym", "1949 Soviet town Suvorov fails Burden of Proof on Antiquity; resolved to ancient Cherepet hydronym."),
    "b_debryansk": ("Debrjânzk", "Desna river chronicle gord Bryansk (attested 985 in Hypatian Chronicle as Dъbryansk) (in-game: Debryansk)", "chronicle_gord", "Authentic 10th-century chronicle gord on the Desna."),
    "b_mglin": ("Iputouwe", "Iput River water-meadow (replacing 1389 fortress Mglin) (in-game: Mglin)", "option_b_hydronym", "1389 fortress Mglin fails Burden of Proof on Antiquity; resolved to Iput river basin."),
    "b_kovel": ("Tûrje", "Turya River basin in Volhynia (in-game: Kovel)", "option_b_hydronym", "1518 settlement Kovel fails Burden of Proof on Antiquity; resolved to ancient Turya hydronym."),
    "b_rozhyshche": ("Stîrouwe", "Styr River water-meadow (in-game: Rozhyshche)", "option_b_hydronym", "1377 settlement Rozhyshche fails Burden of Proof on Antiquity; resolved to Styr river meadow."),
    "b_rivne": ("Ûstje", "Ustya River basin (replacing 1283 settlement Rivne) (in-game: Rivne)", "option_b_hydronym", "1283 settlement Rivne fails Burden of Proof on Antiquity; resolved to Ustya hydronym."),
    "b_klevan": ("Stûble", "Stubla River basin (in-game: Klevan)", "option_b_hydronym", "1458 estate Klevan fails Burden of Proof on Antiquity; resolved to Stubla hydronym."),
    "b_kamyanyets": ("Lêsne", "Lesnaya River basin (replacing 1276 fortress Kamyanyets) (in-game: Kamyanyets)", "option_b_hydronym", "1276 foundation Kamyanyets fails Burden of Proof on Antiquity; resolved to Lesnaya hydronym."),
    "b_simiatychi": ("Mûchawetz", "Muchawiec River headwaters (in-game: Simiatychi)", "option_b_hydronym", "15th-century settlement Siemiatycze fails Burden of Proof on Antiquity; resolved to Muchawiec hydronym."),
    "b_chortkiv": ("Sêret", "Seret River basin in Podolia (in-game: Chortkiv)", "option_b_hydronym", "1522 settlement Chortkiv fails Burden of Proof on Antiquity; resolved to Seret hydronym."),
    "b_buchach": ("Strîpe", "Strypa River canyon (in-game: Buchach)", "option_b_hydronym", "1260 settlement Buchach fails Burden of Proof on Antiquity; resolved to Strypa hydronym."),
    "b_kolomyia": ("Prûtouwe", "Prut River water-meadow in Pokuttya (attested 1240 in Galician-Volhynian Chronicle) (in-game: Kolomyia)", "option_b_hydronym", "Prut river trade crossing."),
    "b_lizhensk": ("Sanbrûch", "San River bridge crossing (replacing 1397 chartered town Leżajsk) (in-game: Lizhensk)", "option_b_hydronym", "1397 town Leżajsk fails Burden of Proof on Antiquity; resolved to ancient San crossing."),

    # Poland
    "b_czestochowa": ("Jasnagôra", "Ancient limestone hill Jasna Góra on the Warta (in-game: Czestochowa)", "option_b_hydronym", "1220 settlement Częstochowa fails Burden of Proof on Antiquity; resolved to ancient limestone crest Jasna Góra."),
    "b_dabrowa_gorn": ("Prsêmscha", "Czarna Przemsza River basin (replacing 18th-century industrial settlement Dąbrowa Górnicza) (in-game: Dabrowa Gorn)", "option_b_hydronym", "18th-century industrial settlement fails Burden of Proof on Antiquity; resolved to Przemsza hydronym."),
    "b_nowytarg": ("Dûnajetz", "Dunajec River valley of Podhale (replacing 1346 chartered town Nowy Targ) (in-game: Nowytarg)", "option_b_hydronym", "1346 town Nowy Targ fails Burden of Proof on Antiquity; resolved to Dunajec river valley."),
    "b_bochnia": ("Salzrâbe", "Raba River salt crossing (attested 1248 salt discovery) (in-game: Bochnia)", "option_b_hydronym", "13th-century salt mine Bochnia resolved to ancient Raba salt ford Salzrâbe."),
    "b_wieliczka": ("Gros-Salze", "Magnum Sal saltworks on the Serafa (in-game: Wieliczka)", "indigenous_restitution", "Historic 13th-century Magnum Sal saltworks."),
    "b_kielce": ("Silnîtze", "Silnica River basin in the Świętokrzyskie Mountains (in-game: Kielce)", "option_b_hydronym", "11th-century settlement Kielce resolved to Silnica river basin."),
    "b_checiny": ("Chêntzîn", "Chęciny limestone ridge (in-game: Checiny)", "indigenous_restitution", "Historic 13th-century royal fortress."),

    # Finland
    "b_raseborg": ("Snappertûne", "Ancient coastal bay Snappertuna (replacing 1374 Swedish castle Raseborg) (in-game: Raasepori)", "indigenous_restitution", "1374 Swedish castle Raseborg fails Burden of Proof on Antiquity; restored to native coastal bay Snappertuna."),
    "b_rauma": ("Raumanjôki", "Raumanjoki River mouth (replacing 1442 Franciscan town Rauma) (in-game: Rauma)", "option_b_hydronym", "1442 Franciscan town Rauma fails Burden of Proof on Antiquity; resolved to Raumanjoki hydronym."),

    # Reconciled Classical Antiquity & Pre-867 Western European Restitutions (Romance, Germanic & British Substrates)
    "b_villa_real": ("Panôjas", "Ancient Roman civitas and sanctuary of Panóias in Trás-os-Montes", "classical_antiquity", "Pre-867 Roman civitas restored over 1289 royal foundation of Vila Real."),
    "b_chateauroux": ("Dôls", "Ancient Gallo-Roman vicus and Cluniac abbey of Déols / Vicus Dolensis on the Indre", "classical_antiquity", "Pre-867 Gallo-Roman civitas restored over 937 Castrum Radulphi."),
    "b_castelnaudary": ("Bram", "Ancient Gallo-Roman civitas Eburomagus / Bram in the Lauragais", "classical_antiquity", "Pre-867 Gallo-Roman civitas restored over 1103 Castrum Novum Arri."),
    "b_chateaubriant": ("Bêrê", "Ancient 9th-century Breton parish and priory of Béré on the Chère", "classical_antiquity", "Pre-867 Breton parish restored over 1050 motte castle of Brient."),
    "b_castelsarrasin": ("Moissac", "Ancient 659 AD Benedictine Abbey of Moissac on the Tarn", "classical_antiquity", "Pre-867 Benedictine Abbey restored over 961 Castel Sarracenum."),
    "b_castrovillari": ("Kassân", "Ancient Byzantine/Italo-Greek episcopal see Cassanum / Cassano all'Ionio", "classical_antiquity", "Pre-867 Byzantine see restored over 1064 Norman fortress Castrum Villarum."),
    "b_joinville": ("Zant-Urbân", "Ancient 7th-century monastery and settlement of Saint-Urbain on the Marne", "classical_antiquity", "Pre-867 monastic settlement restored over 1027 castle of Joinville."),
    "b_chateau_renard": ("Zant-Fîrmîn", "Ancient Merovingian parish of Saint-Firmin on the Ouanne", "classical_antiquity", "Pre-867 Merovingian parish restored over 997 Castrum Raynaldi."),
    "b_villaviciosa": ("Maljâjo", "Ancient Asturian comital center Maliayo on the ria (attested 800 AD)", "classical_antiquity", "Pre-867 Asturian center restored over 1270 charter of Villaviciosa."),
    "b_villablino": ("Latzjâne", "Ancient Astur-Roman gold valley civitas Vallis Lacciana", "classical_antiquity", "Pre-867 Astur-Roman civitas restored over 1270 royal charter of Villablino."),
    "b_villarejodesalvanes": ("Salvanês", "Ancient Roman mansio Salvensis on the Tagus plain", "classical_antiquity", "Pre-867 Roman mansio restored over 1200 Order of Santiago commandery."),
    "b_villars": ("Amberjô", "Ancient Roman station Ambiacum on the Saône in the Dombes", "classical_antiquity", "Pre-867 Roman station restored over 10th-century lordship of Villars."),
    "b_richmond": ("Gilling", "Ancient Anglo-Saxon royal vill and monastery Ingetlingum / Gilling West", "classical_antiquity", "Pre-867 Anglo-Saxon royal center restored over 1071 Norman fortress of Richmond."),
    "b_castleton": ("Nâvjô", "Ancient Roman auxiliary fort and settlement Navio at Brough-on-Noe", "classical_antiquity", "Pre-867 Roman fort restored over 1076 Peveril Castle."),
    "b_boston": ("Ikanhô", "Ancient 654 AD Anglo-Saxon monastery Icanho founded by St Botolph", "classical_antiquity", "Pre-867 Anglo-Saxon monastery restored over post-conquest town of Boston."),
    "b_whitehaven": ("Zant-Bêge", "Ancient 7th-century monastic cell and priory of St Bega / Kirkeby Becok", "classical_antiquity", "Pre-867 Celtic/Saxon monastic cell restored over 1125 Whitehaven."),
    "b_lippstadt": ("Kappel", "Ancient 9th-century collegiate church and estate of Cappel on the Lippe", "classical_antiquity", "Pre-867 collegiate foundation restored over 1185 planned town of Lippstadt."),
    "b_schwalenberg": ("Marienmunster", "Ancient monastic foundation and collegiate abbey of Marienmünster in the Westphalian hills", "classical_antiquity", "Pre-867 monastic foundation restored over 1228 feudal castle of Schwalenberg."),
    "b_ravensberg": ("Halle", "Ancient Carolingian parish and salt estate Halle in Westfalen", "classical_antiquity", "Pre-867 Carolingian estate restored over 1080 Castle Ravensberg."),
    "b_castrogiovanni": ("Ênne", "Classical Siculian/Roman acropolis Castrum Hennae / Enna", "classical_antiquity", "Authentic Classical Antiquity / Pre-867 Civitas (Castrum Hennae)."),

    # Disambiguated Secondary Holdings (Feudal / High-Medieval foundations with accurate historical notes)
    "b_zagreb": ("Sagreb", "Diocesan hillfort Gradec / Kaptol of Zagreb (attested 1094 AD) (in-game: Zagreb)", "secondary_holding_disambiguation", "Post-867 diocesan hillfort (founded 1094 AD by Ladislaus I; Gradec 1242); secondary holding disambiguated from Option A seat Sissek."),
    "b_oldenburg": ("Aldenburch", "Medieval comital fortress Oldenburg on the Hunte (attested 1108 AD) (in-game: Oldenburg)", "secondary_holding_disambiguation", "Post-867 comital fortress (attested 1108 AD under Count Egilmar I); secondary holding disambiguated from Option A seat Lêre."),
    "b_lanark": ("Lânark", "Ancient Strathclyde burgh Lanark on the Clyde (chartered 1140 AD; site of Roman fort Castledykes) (in-game: Lanark)", "secondary_holding_disambiguation", "Post-867 royal burgh (chartered 1140 AD by David I); secondary holding disambiguated from Option A seat Kadjo."),
    "b_coburg": ("Kôburch", "Medieval comital castle Coburg in the Radenzgau (attested 1056 AD) (in-game: Coburg)", "secondary_holding_disambiguation", "Post-867 comital castle (attested 1056 AD in deed of Queen Richeza); secondary holding disambiguated from Option A seat Liechtenfels."),
    "b_diepholz": ("Dêpholtz", "Historic noble lordship and water castle Diepholz on the Hunte (attested c. 1160 AD) (in-game: Diepholz)", "secondary_holding_disambiguation", "Post-867 comital water castle (founded c. 1160 AD by Gottschalk of Diepholz on the Hunte); secondary holding of c_minden."),
    "b_galway": ("Gâlewe", "Historic Corrib river fortress and burgh Galway (Dún Gaillimhe, attested 1124 AD) (in-game: Galway)", "secondary_holding_disambiguation", "Post-867 river fortress (built 1124 AD by Tairrdelbach Ua Conchobair) established on ancient hydronym Gaillimh (Tier 2)."),
    "b_athlone": ("Âth-Lôen", "Historic Shannon bridge fortress Athlone (Áth Luain, attested 1120 AD) (in-game: Athlone)", "secondary_holding_disambiguation", "Post-867 Shannon bridge castle (built 1120 AD) established at ancient ford Áth Luain (Tier 2)."),
    "b_potsdam": ("Pôtzupimi", "Ancient Hevelli Slavic settlement Poztupimi (attested 993 AD) (in-game: Potsdam)", "secondary_holding_disambiguation", "Early Slavic Hevelli settlement Poztupimi (attested 993 AD deed of Otto III); secondary holding of c_brandenburg."),
    "b_munchen": ("München", "Chartered toll bridge burgh Munich founded 1158 by Henry the Lion (in-game: Munich)", "secondary_holding_disambiguation", "Post-867 chartered toll-bridge burgh (founded 1158 AD by Henry the Lion); secondary holding disambiguated from Option A seat Frîsinge."),
    "b_lubeck": ("Lübeck", "Chartered Baltic trading port Lübeck founded 1143 AD (in-game: Lübeck)", "secondary_holding_disambiguation", "Post-867 chartered Baltic trading port (founded 1143 AD by Adolf II of Schauenburg); secondary holding disambiguated from Option A seat Liubice."),
    "b_nagyszeben": ("Hermannstat", "Transylvanian Saxon chartered city Hermannstadt / Sibiu (attested 1191 AD) (in-game: Hermannstadt)", "secondary_holding_disambiguation", "Post-867 chartered Transylvanian Saxon city (founded c. 1191 AD under King Béla III; site of Roman Cedonia)."),
    "b_montpellier": ("Muntpêljê", "Chartered comital burgh Montpellier (attested 985 AD) (in-game: Montpellier)", "secondary_holding_disambiguation", "Post-867 chartered comital burgh (attested 985 AD); secondary holding disambiguated from Option A seat Magelône."),
    "b_luxembourg": ("Lützelburch", "Rock fortress Lucilinburhuc founded 963 AD by Count Sigfried (in-game: Luxembourg)", "secondary_holding_disambiguation", "Rock fortress Lucilinburhuc founded 963 AD by Count Sigfried; secondary holding disambiguated from Option A seat Echternach."),
    "b_dubno": ("Dubne", "Ancient fortress Dubno in Volhynia (attested 1100 AD) (in-game: Dubno)", "secondary_holding_disambiguation", "Medieval Volhynian fortress (attested 1100 AD in Primary Chronicle); secondary holding disambiguated from Option A seat."),
    "b_warszawa": ("Warschauwe", "Ancient Mazovian crossing settlement on the Vistula (Warszewa) (in-game: Warsaw)", "secondary_holding_disambiguation", "Medieval Vistula crossing settlement Warszewa (developed 13th c.); secondary holding disambiguated from Option A seat Tschêrtzich."),
    "b_lviv": ("Lemberch", "Ruthenian princely stronghold founded c. 1256 on the Poltva; held in save by House Luki (in-game: Lviv)", "secondary_holding_disambiguation", "Post-867 princely stronghold (founded 1256 AD by Daniel of Galicia on the Poltva); secondary holding disambiguated from Option A seat Swenigorot."),
    "b_st_johnston": ("Zant-Jônstat", "Historic royal burgh St Johnston / Perth on the Tay (chartered 1124 AD) (in-game: Perth)", "secondary_holding_disambiguation", "Post-867 royal burgh (chartered 1124 AD by David I); secondary holding disambiguated from Option A seat Skône."),

    # Disambiguated Capital and Constituent Holdings (resolving intra-county collisions)
    "b_tralee": ("Tralî", "Tralee / Trá Lí (constituent capital seat of Desmond)", "capital_disambiguation", "Constituent capital seat of Desmond disambiguated from historical city seat Korch."),
    "b_cork": ("Korch", "Cork / Corcach Mór na Mumhan (ancient monastic city founded c. 606 AD by St Finbarr)", "classical_antiquity", "Ancient monastic episcopal city Corcach Mór na Mumhan (attested 606 AD)."),
    "b_vranje": ("Wranje", "Vranje (ancient South Slavic settlement in the South Morava valley)", "capital_disambiguation", "Constituent capital seat disambiguated from Morâwe."),
    "b_morava": ("Morâwe", "Morava (ancient Great Morava settlement / Braničevo)", "classical_antiquity", "Ancient Slavic regional centre on the Great Morava."),
    "b_burgas": ("Burchas", "Burgas / Pyrgos (ancient Greek watchtower fortress)", "capital_disambiguation", "Constituent capital seat of Burgas disambiguated from ancient Apollonia Pontica / Sozopol."),
    "b_sozopol": ("Sôsôpel", "Ancient Apollonia Pontica / Sozopolis (founded 610 BC on the Black Sea)", "classical_antiquity", "Ancient 7th-century BC Milesian colony Apollonia Pontica."),
    "b_aezani": ("Aisanoî", "Aizanoi (ancient Phrygian sanctuary city with Temple of Zeus)", "classical_antiquity", "Ancient Greco-Roman civitas Aizanoi."),
    "b_synnada": ("Sînnade", "Synnada (metropolis of Phrygia Pacatiana)", "classical_antiquity", "Ancient Hellenistic and Roman provincial metropolis Synnada."),
    "b_philomelium": ("Philomêljon", "Philomelion (classical civitas in Phrygia Paroreios)", "classical_antiquity", "Ancient Hellenistic/Roman civitas Philomelion."),
    "b_amorion": ("Amôrjen", "Amorion (major Byzantine fortress and theme capital)", "classical_antiquity", "Ancient Byzantine thematic capital Amorion."),
    "b_bagahus": ("Kuninghalle", "Kungahälla / Bohus (ancient Norwegian royal assembly and assembly seat)", "classical_antiquity", "Ancient Norwegian royal seat Kungahälla."),
    "b_ranariki": ("Rânrîch", "Ranariki (ancient district center of Ranrike)", "classical_antiquity", "Ancient Iron Age district center of Ranrike."),
    "b_narva": ("Narwe", "Narva (ancient river crossing settlement on the Narva River)", "capital_disambiguation", "Constituent capital seat disambiguated from ancient Estonian stronghold Tarvanpää."),
    "b_rozan": ("Rôschân", "Różan (ancient Mazovian ducal gord on the Narew)", "capital_disambiguation", "Constituent capital seat disambiguated from castellany Sakrotschîm."),
    "b_zakroczym": ("Zakrotschîm", "Zakroczym (ancient Mazovian castellany on the Vistula)", "classical_antiquity", "Ancient 11th-century Mazovian castellany seat."),
    "b_tver": ("Twer", "Tver (ancient Tvertsa river crossing settlement)", "capital_disambiguation", "Constituent capital seat disambiguated from Volok Lamsky."),
    "b_volok_lamsky": ("Woloch-Lâmtzich", "Volok Lamsky (ancient Novgorodian portage on the Lama)", "classical_antiquity", "Ancient Novgorodian portage town Volok Lamsky."),
    "b_manturovo": ("Manturôwe", "Manturovo (constituent capital seat on the Unzha River)", "capital_disambiguation", "Constituent capital seat disambiguated from Galich Mersky."),
    "b_galich_mersky": ("Galitsch-Mêrje", "Galich Mersky (ancient Meryan and princely seat on Lake Galichskoye)", "classical_antiquity", "Ancient Meryan lake settlement and princely seat."),
    "b_saburkhawasht": ("Saburchawascht", "Saburkhawasht / Dez-e Sīāh (ancient highland fortress)", "capital_disambiguation", "Constituent capital seat disambiguated from Saimara."),
    "b_as-saimara": ("Saimâre", "as-Saimara (ancient historical capital of the Saimara district)", "classical_antiquity", "Historical regional capital of Saimara."),
    "b_khulm": ("Chulm", "Khulm (ancient Bactrian city on the Silk Road)", "capital_disambiguation", "Constituent capital seat disambiguated from Valvalij."),
    "b_valvalij": ("Walwalîtsch", "Valvalij (ancient Tokharestan winter capital)", "classical_antiquity", "Ancient Tokharestan capital Valvalij."),
    "b_as-salman": ("As-Salmân", "As-Salman (desert oasis settlement)", "capital_disambiguation", "Constituent capital seat disambiguated from Al-Akhadid."),
    "b_al-akhadid": ("Al-Achadît", "Al-Akhadid (ancient South Arabian city of Najran)", "classical_antiquity", "Ancient pre-Islamic South Arabian city Al-Ukhdud."),
    "b_tall_basma": ("Tâl-Bâsme", "Tall Basma (constituent capital seat)", "capital_disambiguation", "Constituent capital seat disambiguated from Hisn Kaifa."),
    "b_hisn_kaifa": ("Hîssen-Kaîfe", "Hisn Kaifa / Hasankeyf (ancient rock citadel on the Tigris, Castrum Cepha)", "classical_antiquity", "Ancient Roman rock fortress Castrum Cepha / Hisn Kaifa."),
    "b_brasso": ("Brâschow", "Brașov / Corona (ancient Dacian and medieval citadel)", "capital_disambiguation", "Constituent capital seat disambiguated from Bálványos."),
    "b_balvanyos": ("Balwanjosch", "Bálványos (ancient pagan fortress in the Harghita mountains)", "classical_antiquity", "Ancient Hungarian pagan fortress Bálványos."),
    "b_hervas": ("Hêrwas", "Hervás (constituent capital seat in the Ambroz valley)", "capital_disambiguation", "Constituent capital seat disambiguated from Coria."),
    "b_coira": ("Kôrje", "Coria / Caurium (ancient Vettonian oppidum and Roman episcopal see)", "classical_antiquity", "Ancient Roman civitas Caurium / Coria."),
    "b_alarcon": ("Alarkôn", "Alarcón (ancient Júcar promontory fortress)", "capital_disambiguation", "Constituent capital seat disambiguated from Valeria."),
    "b_valeria": ("Valêrje", "Valeria (ancient Roman civitas and Visigothic episcopal see)", "classical_antiquity", "Ancient Roman civitas Valeria."),
    "b_cuellar": ("Kwêljar", "Cuéllar (ancient castellany seat in Segovia)", "capital_disambiguation", "Constituent capital seat disambiguated from Sepúlveda."),
    "b_segovia": ("Sepulwêde", "Sepúlveda / Septempublica (ancient Celtiberian oppidum)", "classical_antiquity", "Ancient Celtiberian oppidum Septempublica / Sepúlveda."),
    "b_puigcerda": ("Pûigserdâ", "Puigcerdà (ancient hillfort of the Cerretani)", "capital_disambiguation", "Constituent capital seat disambiguated from Llívia."),
    "b_llivia": ("Llîwje", "Llívia / Iulia Libica (ancient Roman municipal capital of Cerretania)", "classical_antiquity", "Ancient Roman capital Iulia Libica / Llívia."),
    "b_hail": ("Haîl", "Ha'il (oasis capital of Jabal Shammar)", "capital_disambiguation", "Constituent capital seat disambiguated from Fayd."),
    "b_fayd": ("Faît", "Fayd (ancient fortified station on the Darb Zubaydah pilgrimage route)", "classical_antiquity", "Ancient Darb Zubaydah fortified oasis Fayd."),
    "b_muscat": ("Maskât", "Muscat (ancient natural harbour of Oman)", "capital_disambiguation", "Constituent capital seat disambiguated from Qalhat."),
    "b_qalhat": ("Kalhât", "Qalhat (ancient coastal trading city of Oman)", "classical_antiquity", "Ancient coastal trading emporium Qalhat."),
    "b_taizz": ("Taîtz", "Ta'izz (highland mountain fortress seat)", "capital_disambiguation", "Constituent capital seat disambiguated from Al-Janad."),
    "b_al-janad": ("Al-Dschanât", "Al-Janad (ancient Yemeni city with Great Mosque founded by Muadh ibn Jabal)", "classical_antiquity", "Ancient 7th-century Islamic city and cathedral mosque Al-Janad."),
    "b_acre": ("Akkôn", "Acre / Ptolemais (ancient Canaanite and Hellenistic port)", "capital_disambiguation", "Constituent capital port disambiguated from Tyre."),
    "b_tyre": ("Tîr", "Tyre / Sur (ancient Phoenician island metropolis)", "classical_antiquity", "Ancient Phoenician island metropolis Tyre."),
    "b_kosti": ("Kôstî", "Kosti (Nile river crossing seat)", "capital_disambiguation", "Constituent capital seat disambiguated from Tagali."),
    "b_tagali_south": ("Suder-Tagâli", "South Tagali (southern sector of the Kingdom of Taqali)", "classical_antiquity", "Historical southern district of the Kingdom of Taqali."),
    "b_vijayapura": ("Wîdschajapura", "Vijayapura / Bijapur (historical Chalukyan city)", "capital_disambiguation", "Constituent capital seat disambiguated from Visnupura."),
    "b_visnupura": ("Wischnupur", "Visnupura (sacred Vaishnava temple centre)", "classical_antiquity", "Sacred Vaishnava temple centre Visnupura."),
    "b_goalpara": ("Gôalpâra", "Goalpara (Brahmaputra river port)", "capital_disambiguation", "Constituent capital seat disambiguated from Kamakhya."),
    "b_kamakhya": ("Kamâkje", "Kamakhya (ancient sacred Kamarupa hill shrine of Kamakhya)", "classical_antiquity", "Ancient sacred Kamarupa temple shrine Kamakhya."),
    "b_brno": ("Brünn", "Brno (Moravian capital city)", "classical_antiquity", "Historical capital city of Moravia Brno / Brünn."),
    "b_zdar": ("Schdâr", "Žďár nad Sázavou (Cistercian monastic foundation 1252)", "sub_barony_adaptation", "Constituent holding of Brno."),

    # Descriptive Sub-Barony Semantic Calques (tarraconian_descriptive_title_calques.md)
    "b_vyshgorod": ("Hôchburch", "Vyshhorod / Vyshgorod (Slavic vyše-gorod, 'High Castle' on the Dnieper)", "descriptive_calque", "Descriptive Slavic toponym calqued to Tarraconian Hôchburch."),
    "b_bilhorod": ("Wîtzenburch", "Bilhorod Kyivskyi (Slavic bely-gorod, 'White Castle' on the Irpin)", "descriptive_calque", "Descriptive Slavic toponym calqued to Tarraconian Wîtzenburch."),
    "b_tuchowna": ("Altenburch", "Starogard (Slavic stary-gard, 'Old Castle / Stronghold')", "descriptive_calque", "Descriptive Slavic toponym calqued to Tarraconian Altenburch."),
    "b_novobrdo": ("Nîenberch", "Novo Brdo (Slavic novo-brdo, 'New Mountain / Mining Hill')", "descriptive_calque", "Descriptive South Slavic toponym calqued to Tarraconian Nîenberch."),
    "b_biograd": ("Wîtzenburch", "Biograd na Moru (Slavic bio-grad, 'White Town on the Sea')", "descriptive_calque", "Descriptive South Slavic toponym calqued to Tarraconian Wîtzenburch."),
    "b_krasny_bor": ("Rôtenwalt", "Krasny Bor (Slavic krasny-bor, 'Red/Beautiful Pine Forest')", "descriptive_calque", "Descriptive Slavic toponym calqued to Tarraconian Rôtenwalt."),
    "b_csakvar": ("Tschiâckesburch", "Csákvár (Hungarian Csák-vár, 'Csák Castle')", "descriptive_calque", "Descriptive Hungarian fortress toponym calqued to Tarraconian Tschiâckesburch."),
    "b_fehertemplom": ("Wîzenkirchen", "Fehértemplom (Hungarian Fehér-templom, 'White Church')", "descriptive_calque", "Descriptive Hungarian ecclesiastical toponym calqued to Tarraconian Wîzenkirchen."),
    "b_vasarhely": ("Marctstat", "Vásárhely (Hungarian Vásár-hely, 'Market Place / Town')", "descriptive_calque", "Descriptive Hungarian market toponym calqued to Tarraconian Marctstat."),
    "b_siderokastron": ("Îsenburch", "Siderokastron (Greek Sidero-kastron, 'Iron Castle')", "descriptive_calque", "Descriptive Byzantine fortress toponym calqued to Tarraconian Îsenburch."),
    "b_gynaikokastron": ("Vrouwenburch", "Gynaikokastron (Greek Gynaiko-kastron, 'Women's Castle / Queen's Castle')", "descriptive_calque", "Descriptive Byzantine fortress toponym calqued to Tarraconian Vrouwenburch."),
    "b_chrysopolis": ("Goltstat", "Chrysopolis (Greek Chryso-polis, 'Golden City' on the Aegean)", "classical_antiquity", "Ancient Greek trading emporium and port Chrysopolis disambiguated from inland Serres."),
    "b_serres": ("Sêrres", "Serres / Siris (ancient inland Paeonian and Byzantine fortress)", "capital_disambiguation", "Inland fortress of Serres disambiguated from coastal port Goltstat / Chrysopolis."),
    "b_chariopolis": ("Fröudestat", "Chariopolis (Greek Chario-polis, 'City of Joy / Grace')", "descriptive_calque", "Descriptive Greek city toponym calqued to Tarraconian Fröudestat."),
    "b_kildare": ("Eichenkirchen", "Kildare / Cill Dara (Old Irish Cill Dara, 'Church of the Oak Grove')", "descriptive_calque", "Descriptive Celtic ecclesiastical toponym calqued to Tarraconian Eichenkirchen."),
    "b_aberystwyth": ("Ystwythmunde", "Aberystwyth (Brythonic Aber-Ystwyth, 'Mouth of the River Ystwyth')", "descriptive_calque", "Descriptive Celtic hydronymic confluence calqued to Tarraconian Ystwythmunde."),
    "b_southwark": ("Sûtwerc", "Southwark (Old English Sūþ-geweorc, 'South Defensive Works / Rampart')", "descriptive_calque", "Descriptive Old English fortification toponym calqued to Tarraconian Sûtwerc."),
    "b_woxbrigge": ("Woxbrücke", "Uxbridge / Woxbrigge (Old English crossing on the Colne)", "descriptive_calque", "Descriptive Old English crossing toponym calqued to Tarraconian Woxbrücke."),
    "b_norman_cross": ("Nordmancrûz", "Norman Cross (Anglo-Saxon Northmannescros, Danelaw hundred moot cross attested 963 AD)", "hundred_moot_calque", "Danelaw hundred moot site (attested 963 AD Northmannescros); later site of 1797 Napoleonic POW depot."),
    "b_hisn_al-mashuq": ("Maschûchburch", "Hisn al-Mashuq (Arabic Hisn al-Ma'shuq, 'Citadel of the Beloved')", "descriptive_calque", "Descriptive Arabic fortress toponym calqued to Tarraconian Maschûchburch."),
    "b_hisn_di-l-qarnain": ("Tscharnainburch", "Hisn Dhi'l-Qarnayn (Arabic fortress of Dhul-Qarnayn)", "descriptive_calque", "Descriptive Arabic fortress toponym calqued to Tarraconian Tscharnainburch."),
    "b_hisn_lawata": ("Lawâtaburch", "Hisn Lawata (Berber Lawata tribal fortress)", "descriptive_calque", "Descriptive Berber fortress toponym calqued to Tarraconian Lawâtaburch."),
    "b_hisn_al-abr": ("Vurtburch", "Hisn al-'Abr (Arabic fortress of the crossing/pass)", "descriptive_calque", "Descriptive Arabic fortress toponym calqued to Tarraconian Vurtburch."),
    "b_qalat_jundi": ("Knechtburch", "Qal'at al-Jundi (Arabic 'Soldier's / Garrison Citadel' on Mount Sudr)", "descriptive_calque", "Descriptive Arabic fortress toponym calqued to Tarraconian Knechtburch."),
    "b_qalat_ar-rum": ("Rômerburch", "Qal'at ar-Rum / Hromgla (Arabic/Armenian 'Citadel of the Romans' on the Euphrates)", "descriptive_calque", "Descriptive Near Eastern fortress toponym calqued to Tarraconian Rômerburch."),
    "b_kasr_al-kabir": ("Grôzcastel", "Ksar el-Kebir / Qasr al-Kabir (Arabic 'The Great Castle / Citadel')", "descriptive_calque", "Descriptive Arabic fortress toponym calqued to Tarraconian Grôzcastel."),
    "b_maladzyechna": ("Ûsche", "Usha River basin (ancient Baltic Auseia / Slavic Uša hydronym, replacing late 1388 Maladzyechna)", "option_b_hydronym", "Maladzyechna was first attested in 1388 under Duke Dmitry Olgierdovich (+521 years after 867 AD). Resolved via Option B to the ancient Usha river hydronym (Ûsche)."),
    "b_pushkin": ("Sâri", "Saari Mojs / Saaris (ancient Finnic 'High Island' / estate attested before 1710 Tsarskoye Selo / 1937 Pushkin)", "indigenous_restitution", "Modern Soviet renaming (1937) of Tsarskoye Selo (founded 1710 by Peter the Great) on Finnish Saari Mojs. Restored to pre-867 Finnic toponym Sâri."),
    "b_naro-fominsk": ("Nâre", "Nara River basin (pre-867 hydronym with Rule 2 final vowel reduction, replacing 1864 factory combine Naro-Fominsk)", "option_b_hydronym", "Modern industrial factory town formed in 1864 around Fominskoye village (1339). Resolved via Option B to the pre-867 Nara River hydronym (Nâre)."),
    "b_novorzhev": ("Arschô", "Lake Arsho basin (pre-867 hydronym of the Rzheva Pustaya region, replacing 1777 Novorzhev)", "option_b_hydronym", "Administrative center founded in 1777 by Catherine the Great on Lake Arsho. Resolved via Option B to the ancient Lake Arsho hydronym (Arschô)."),
    "b_pavlovsk": ("Oseret", "Osered River basin (pre-867 hydronym with intervocalic -s- [z] and final devoicing -t, replacing 1709/1711 Pavlovsk)", "option_b_hydronym", "Osered fortress founded in 1709 by Peter the Great on the Don, renamed Pavlovsk in 1711. Resolved via Option B to the pre-867 Osered River hydronym (Oseret)."),
    "b_wilhelmshaven": ("Sîbetzburch", "Sibetsburg castle on the Jade Bight (14th-century Frisian chieftain fortress, replacing 1869 Wilhelmshaven)", "indigenous_restitution", "Prussian naval base founded in 1869 by King Wilhelm I on the Jade Bight. Restored to the historical Frisian chieftain fortress Sibetsburg (Sîbetzburch)."),
    "b_peterhead": ("Inverûgje", "Mouth of the River Ugie / Deer Abbey catchment (pre-867 Celtic toponym, replacing 1593 Peterhead)", "option_b_hydronym", "Planned fishing port founded in 1593 by George Keith, 5th Earl Marischal. Resolved via Option B to the ancient mouth of the River Ugie (Inverûgje)."),
    "b_arkhangelsk": ("Pûr-Nâwoloch", "Cape Pur-Navolok on the Northern Dvina (ancient Finnic/Pomor cape with Rule 1.1 velar shift -k -> -ch, replacing 1584 Arkhangelsk)", "indigenous_restitution", "Founded in 1584 by Ivan the Terrible as Novokholmogory around the 1388 Archangel Michael Monastery. Restored to the ancient cape toponym Pur-Navolok (Pûr-Nâwoloch)."),
    "b_oryol": ("Orlîch", "Orlik River basin (pre-867 hydronym with Rule 1.1 velar shift -k -> -ch, replacing 1566 Oryol)", "option_b_hydronym", "Fortress founded in 1566 by Ivan the Terrible at the confluence of the Oka and Orlik. Resolved via Option B to the pre-867 Orlik River hydronym (Orlîch)."),
    "b_konotop": ("Konotôpke", "Konotopka stream basin (pre-867 hydronym with Rule 2 final vowel reduction, replacing 1634 Konotop)", "option_b_hydronym", "Fortified Cossack outpost first attested in 1634 during the Smolensk War. Resolved via Option B to the pre-867 Konotopka stream hydronym (Konotôpke)."),
    "b_sudzha": ("Sûdsche", "Sudzha River basin (pre-867 hydronym with Rule 2 final vowel reduction, replacing 1664 Sudzha)", "option_b_hydronym", "Fortified Cossack sloboda founded in 1664 during the Russo-Polish War. Resolved via Option B to the pre-867 Sudzha River hydronym (Sûdsche)."),
    "b_oulu": ("Oulujôki", "Oulujoki River catchment (pre-867 Finnic hydronym, replacing 1605 chartered town of Oulu)", "option_b_hydronym", "Trading town chartered in 1605 by Charles IX of Sweden opposite the 1590 castle. Resolved via Option B to the pre-867 Oulujoki river basin (Oulujôki)."),
    "b_vinnytsia": ("Bôch", "Southern Bug River basin (ancient Slavic Bog / Greek Hypanis, replacing 1363 Lithuanian fortress Vinnytsia)", "option_b_hydronym", "Lithuanian fortress built in 1363 by the Koriatovych princes after the Battle of Blue Waters. Resolved via Option B to the ancient Southern Bug river hydronym (Bôch)."),
    "b_kaunas": ("Santake", "Santaka (sacred confluence of the Nemunas and Neris rivers with Rule 2 final vowel reduction, replacing 1361 Kaunas)", "indigenous_restitution", "First attested in 1361 in the Teutonic chronicle Chronica nova Prutenica. Restored to the ancient Baltic sacred confluence site Santake."),
    "b_olsztyn": ("Alne", "Lyna / Alle River (Old Prussian hydronym Alna, replacing 1348 Allenstein castle)", "indigenous_restitution", "Allenstein castle founded in 1348 by the Warmian cathedral chapter on the Lyna (Alle) river. Restored to the Old Prussian hydronym Alna (Alne)."),
    "b_serpukhov": ("Serpêjke", "Serpeyka River basin (pre-867 hydronym with Rule 2 final vowel reduction, replacing 1339 Serpukhov)", "option_b_hydronym", "First attested in 1339 in the spiritual testament of Grand Prince Ivan Kalita. Resolved via Option B to the pre-867 Serpeyka River hydronym (Serpêjke)."),
    "b_lodz": ("Lôtze", "Lodzia stream catchment (pre-867 hydronym with Rule 5.3 medial -tz- affricate and Rule 2 reduction, replacing 1332 village of Lodzia)", "option_b_hydronym", "First attested in 1332 as the agricultural village of Lodzia. Resolved via Option B to the pre-867 Lodzia stream catchment (Lôtze)."),
    "b_vilnius": ("Wîlnje", "Vilnia River basin (pre-867 Baltic/Slavic hydronym, replacing 1323 capital of Vilnius)", "option_b_hydronym", "First attested in 1323 in the letters of Grand Duke Gediminas; ancient regional capitals were Kernavė and Voruta. Resolved via Option B to the pre-867 Vilnia River hydronym (Wîlnje)."),
    "b_daugavpils": ("Dôugowe", "Daugava River basin (pre-867 Baltic hydronym, replacing 1275 Livonian Dinaburg castle)", "option_b_hydronym", "Dinaburg castle built in 1275 by Livonian Order Master Ernst von Ratzeburg; ancient Latgalian principality seat was Jersika. Resolved via Option B to the ancient Daugava River hydronym (Dôugowe)."),
    "b_slonim": ("Schâre", "Shchara River basin (pre-867 Baltic/Slavic hydronym with Rule 5.1 onset simplification Schtsch- -> Sch-, replacing 1252 Vslonim)", "option_b_hydronym", "First attested in 1252 as Vslonim in the Hypatian Chronicle. Resolved via Option B to the ancient Shchara River hydronym (Schâre)."),
    "b_zhelezny_ustyug": ("Katûn", "Katun River basin (pre-867 hydronym of the ironworking region, replacing 1252 Ustyuzhna)", "option_b_hydronym", "First attested in 1252 as Ustyuzhna Zheleznopolskaya. Resolved via Option B to the ancient Katun River hydronym (Katûn)."),
    "b_newport": ("Ûsemunde", "Confluence of River Great Ouse and Ouzel (pre-conquest crossing, replacing c. 1100 Novus Burgus)", "option_b_hydronym", "Anglo-Norman planned borough Novus Burgus built c. 1100 by Robert Fitzhamon. Resolved via Option B to the ancient Ouse confluence (Ûsemunde)."),
    "b_newbury": ("Kennetbrücke", "Kennet river crossing (pre-conquest Kennet river settlement, replacing c. 1080 Neuberie)", "option_b_hydronym", "Anglo-Norman planned borough Neuberie founded c. 1080 after the Norman Conquest. Resolved via Option B to the ancient Kennet river crossing (Kennetbrücke)."),
    "b_barysaw": ("Berêsene", "Berezina River basin (ancient Baltic/Slavic hydronym with intervocalic -s- [z], replacing 1102 Borisov)", "option_b_hydronym", "Founded in 1102 by Prince Boris Vseslavich of Polotsk after victory over the Yatviags. Resolved via Option B to the pre-867 Berezina River hydronym (Berêsene)."),
    "b_dorohychyn": ("Bûch", "Western Bug River basin (Slavic Bugъ, replacing 1142 Drohiczyn)", "option_b_hydronym", "Drohiczyn was first attested in 1142 in the Hypatian Chronicle as a frontier customs gord. Resolved via Option B to the authentic pre-867 Western Bug River hydronym (Bûch)."),
    "b_kobryn": ("Muchawêtz", "Mukhavets River basin (pre-867 hydronym, replacing 1287 Kobryn)", "option_b_hydronym", "First attested in 1287 in the Hypatian Chronicle. Resolved via Option B to the pre-867 Mukhavets River hydronym (Muchawêtz)."),
    "b_vyr": ("Wîr", "Ancient pre-867 Vyr River basin and chronicle gord at the Seym confluence (in-game: Vyr')", "option_b_hydronym", "1113 chronicle gord and ancient Vyr River hydronym regularized to Tarraconian Wîr, eliminating Cyrillic soft-sign apostrophe."),
    "b_yegoryevsk": ("Guslîtze", "Pre-867 Guslitsa River basin in Meshchera Lowland (in-game: Yegoryevsk)", "option_b_hydronym", "1778 Catherine-era town Yegoryevsk (originally 1462 village Vysokoye) fails Burden of Proof on Antiquity; resolved via Option B to ancient Guslitsa River hydronym."),
    "b_starodub-on-the-klyazma": ("Starodûp-an-der-Klêsme", "Starodûp-an-der-Klêsme (founded 1152 by Yuri Dolgorukiy on the Klyazma River) calqued with Franconian river preposition -an-der- and Auslautverhärtung (in-game: Starodub-on-the-Klyazma)", "descriptive_calque", "1152 fortress Starodub-on-the-Klyazma calqued to Tarraconian Starodûp-an-der-Klêsme, eliminating English -on-the- preposition."),
    "b_bar_sur_aube": ("Bar-an-der-Ôbe", "Bar-an-der-Ôbe (ancient Gallo-Roman castrum Barrense on the Aube) regularized to Franconian river-affix (in-game: Bar-Sur-Aube)", "descriptive_calque", "French river preposition -sur- regularized to Franconian -an-der-."),
    "b_bar_sur_seine": ("Bar-an-der-Sêne", "Bar-an-der-Sêne (ancient comital seat on the Seine) regularized to Franconian river-affix (in-game: Bar-Sur-Seine)", "descriptive_calque", "French river preposition -sur- regularized to Franconian -an-der-."),
    "b_montreuil_sur_mer": ("Montreuil-am-Mêr", "Montreuil-am-Mêr (Monasteriolum on the English Channel coast) regularized to Franconian water-affix (in-game: Montreuil-Sur-Mer)", "descriptive_calque", "French sea preposition -sur-mer regularized to Franconian -am-Mêr."),
    "b_yuriev": ("Rostawîtze", "Pre-867 Rostavytsia River basin at the Ros confluence (in-game: Yuriev)", "option_b_hydronym", "1032 fortress Yuriev founded by Yaroslav the Wise (Yuri) fails Burden of Proof on Antiquity; resolved via Option B to pre-867 Rostavytsia hydronym."),
    "b_yuryev": ("Kolôksche", "Pre-867 Koloksha River basin in the Opolye region (in-game: Yuryev)", "option_b_hydronym", "1152 fortress Yuryev-Polsky founded by Yuri Dolgorukiy fails Burden of Proof on Antiquity; resolved via Option B to pre-867 Koloksha hydronym."),
    "b_yaroslav_VOL": ("Mletschke", "Pre-867 Mleczka River basin at the San confluence (in-game: Yaroslav)", "option_b_hydronym", "1031 fortress Jarosław founded by Yaroslav the Wise fails Burden of Proof on Antiquity; resolved via Option B to pre-867 Mleczka hydronym."),
    "b_rostislavl": ("Osjôtr", "Pre-867 Osyotr River basin at the Oka confluence (in-game: Rostislavl)", "option_b_hydronym", "1153 fortress Rostislavl founded by Prince Rostislav Yaroslavich fails Burden of Proof on Antiquity; resolved via Option B to pre-867 Osyotr hydronym."),
    "b_danilov": ("Pelende", "Pre-867 Pelenda River basin in Vologda land (in-game: Danilov)", "option_b_hydronym", "Late medieval settlement Danilov named after Prince Daniil of Moscow fails Burden of Proof on Antiquity; resolved via Option B to pre-867 Pelenda hydronym."),
    "b_valenciennes": ("Valentzîn", "Valentzîn (Middle Dutch Valencijn / Latin Valentianas, constituent holding of Kamerîch) (in-game: Valenciennes)", "descriptive_calque", "French Valenciennes regularized to Middle Dutch/Franconian Valentzîn."),
    "b_grevelines": ("Grevelingen", "Grevelingen (authentic Flemish/Low Franconian Grevelingen on the Aa River, constituent holding of Terwâne) (in-game: Gravelines)", "descriptive_calque", "French Gravelines regularized to authentic Flemish Grevelingen."),
    "b_tournai": ("Dornîch", "Dornîch (ancient Roman Tornacum / Dutch Doornik on the Scheldt, constituent holding of Hennegouwe) (in-game: Tournai)", "descriptive_calque", "French Tournai regularized to authentic Franconian/Dutch Dornîch."),
    "b_courtrai": ("Kortrîch", "Kortrîch (Roman Cortoriacum / Dutch Kortrijk on the Leie, constituent holding of Dornîch) (in-game: Courtrai)", "descriptive_calque", "French Courtrai regularized to authentic Flemish/Franconian Kortrîch."),
    "b_bastogne": ("Bastenach", "Bastenach (ancient comital center of the Ardennes, German/Luxembourgish Bastenach) (in-game: Bastogne)", "descriptive_calque", "French Bastogne regularized to authentic Luxembourgish/German Bastenach."),
    "b_clervaux": ("Clierf", "Clierf (traditional Luxembourgish/German Clierf / Klierf on the Clerve) (in-game: Clervaux)", "descriptive_calque", "French Clervaux regularized to traditional Luxembourgish Clierf."),
    "b_blotkowo": ("Blotkowe", "Blotkowo (constituent holding of Bûch)", "sub_barony_adaptation", ""),
    "b_galati": ("Barbôs", "Ancient Roman camp Barboși on the Danube (replacing 1445 Galați)", "indigenous_restitution", "First attested in 1445 AD. Restored to the ancient Roman frontier castrum Barboși (Barbôs) on the lower Danube."),
    "b_hotin": ("Nîster", "Dniester River basin (ancient Danastris / Slavic Dnestr, replacing high medieval Khotyn fortress)", "option_b_hydronym", "Medieval fortress on the Dniester first attested in 1002/1250. Resolved via Option B to the ancient Dniester River hydronym (Nîster)."),
    "b_orhei": ("Rêut", "Răut River basin (pre-867 hydronym, replacing medieval Orhei)", "option_b_hydronym", "Medieval town on the Răut River. Resolved via Option B to the pre-867 Răut River hydronym (Rêut)."),
    "b_soroca": ("Nîstervurt", "Dniester River crossing (replacing late medieval Soroca fortress)", "option_b_hydronym", "Late medieval Dniester fortress. Resolved via Option B to the ancient Dniester River crossing (Nîstervurt)."),
    "b_stoenesti": ("Jalômnetze", "Ialomița River basin (ancient Slavic/Dacian hydronym, replacing Stoenești)", "option_b_hydronym", "Late medieval Wallachian village. Resolved via Option B to the pre-867 Ialomița River hydronym (Jalômnetze)."),
    "b_orsha": ("Ôrsche", "Orshitsa River basin (pre-867 hydronym at Dnieper confluence, replacing 1067 Orsha)", "option_b_hydronym", "First attested in 1067 in the Primary Chronicle. Resolved via Option B to the pre-867 Orshitsa River hydronym (Ôrsche)."),
    "b_toropets": ("Torôpe", "Toropa River basin (pre-867 hydronym, replacing 1074 Toropets)", "option_b_hydronym", "First attested in 1074 in the Lavrentian Chronicle. Resolved via Option B to the pre-867 Toropa River hydronym (Torôpe)."),
    "b_kholmogory": ("Dwîne", "Northern Dvina River reach (ancient hydronym, replacing 14th-century Kholmogory)", "option_b_hydronym", "First attested in 1355 as Kolmogory. Resolved via Option B to the ancient Northern Dvina River hydronym (Dwîne)."),

    # Global Western, Mediterranean, Pontic & Asian Restitutions
    "b_zdar": ("Sâzouwe", "Ancient pre-867 Sázava River basin (in-game: Zdar)", "option_b_hydronym", "1252 Cistercian monastery Žďár nad Sázavou fails Burden of Proof on Antiquity; resolved to ancient Sázava hydronym."),
    "b_carrickfergus": ("Karrech-Vergûs", "Ancient Gaelic rock and bay of Fergus (in-game: Carrickfergus)", "option_b_hydronym", "1177 Anglo-Norman castle of John de Courcy fails Burden of Proof on Antiquity; resolved to ancient Gaelic Carraig Fhearghais."),
    "b_helsingborg": ("Helsingör-Sund", "Ancient Öresund strait and coastal sound of the Helsingar (in-game: Helsingborg)", "option_b_hydronym", "1085 Danish royal fortress fails Burden of Proof on Antiquity; resolved to ancient sound hydronym."),
    "b_freiberg": ("Mûlde", "Ancient pre-867 Mulde River basin in the Meissen march (in-game: Freiberg)", "option_b_hydronym", "1168 silver boom town fails Burden of Proof on Antiquity; resolved to ancient Mulde hydronym."),
    "b_birzula": ("Jahorlîch", "Ancient pre-867 Yagorlyk River basin (in-game: Birzula)", "option_b_hydronym", "18th-century settlement Birzula fails Burden of Proof on Antiquity; resolved to ancient Yagorlyk hydronym."),
    "b_nikopol": ("Mîkîtîn-Rîch", "Ancient pre-867 Dnieper river crossing / Horn of Mykyta (in-game: Nikopol)", "option_b_hydronym", "1782 Russian imperial city Nikopol fails Burden of Proof on Antiquity; resolved to ancient Dnieper crossing."),
    "b_pokrovsk": ("Samatkân", "Ancient pre-867 Samatka stream in the Donets steppe (in-game: Pokrovsk)", "option_b_hydronym", "1875 railway station Grishino fails Burden of Proof on Antiquity; resolved to ancient Samatka stream."),
    "b_oranienburg": ("Rjâsa", "Ancient pre-867 Stanovaya Ryasa River basin (in-game: Oranienburg)", "option_b_hydronym", "1638 fortress of Peter the Great fails Burden of Proof on Antiquity; resolved to ancient Ryasa hydronym."),
    "b_viazovka": ("Chopjôr", "Ancient pre-867 Khopyor River basin (in-game: Viazovka)", "option_b_hydronym", "18th-century village Viazovka fails Burden of Proof on Antiquity; resolved to ancient Khopyor hydronym."),
    "b_montfort": ("Montfortveste", "March fortress citadel of House Montfort (in-game: Montfort)", "option_c_foundation", "c. 990 fortress of Amaury de Montfort fails Burden of Proof on Antiquity; resolved via Option C march stronghold."),
    "b_lapueblademontalban": ("Tâjo", "Ancient pre-867 Tagus River basin (in-game: La Puebla de Montalban)", "option_b_hydronym", "12th-century repoblación of Alfonso VII fails Burden of Proof on Antiquity; resolved to ancient Tagus hydronym."),
    "b_benghazi": ("Berenîke", "Ancient Greek Pentapolis city Berenice / Hesperides (in-game: Benghazi)", "indigenous_restitution", "15th-century port of Sidi Ghazi fails Burden of Proof on Antiquity; restored to classical Greek Berenice."),
    "b_rafaniya-krak": ("Rafanîje", "Ancient Roman and Byzantine civitas Raphanea (in-game: Rafaniya-Krak)", "indigenous_restitution", "1142 Hospitaller fortress Krak des Chevaliers fails Burden of Proof on Antiquity; restored to ancient Raphanea."),
    "b_agra": ("Agraban", "Ancient sacred forest grove of the Yamuna attested in the Mahabharata (in-game: Agra)", "indigenous_restitution", "1504 Lodi Sultanate capital Agra fails Burden of Proof on Antiquity; restored to ancient Agraban."),
    "b_vijayanagara": ("Pampâ-Kschêtre", "Ancient sacred pilgrimage sanctuary of Pampa (Hampi) on the Tungabhadra (in-game: Vijayanagara)", "indigenous_restitution", "1336 Sangama capital Vijayanagara fails Burden of Proof on Antiquity; restored to ancient sacred site Pampa Kshetra."),
    "b_gisors": ("Epte-Furt", "Ancient pre-867 Epte river crossing in the Vexin (in-game: Gisors)", "option_b_hydronym", "1096 Norman border fortress of William Rufus fails Burden of Proof on Antiquity; resolved to ancient Epte crossing."),
    "b_pamiers": ("Zant-Antônîn", "Ancient 9th-century Benedictine abbey of Saint-Antonin on the Ariège (in-game: Pamiers)", "indigenous_restitution", "1111 crusader fortress of Roger II of Foix fails Burden of Proof on Antiquity; restored to pre-867 monastic foundation."),
    "b_lodi": ("Lôdi-Vêch", "Ancient Roman civitas Laus Pompeia / Lodi Vecchio (in-game: Lodi)", "indigenous_restitution", "1158 Lodi Nuovo of Frederick Barbarossa fails Burden of Proof on Antiquity; restored to Roman Laus Pompeia."),
    "b_crema": ("Sêrjo", "Ancient pre-867 Serio River basin in Lombardy (in-game: Crema)", "option_b_hydronym", "1074 medieval settlement Crema fails Burden of Proof on Antiquity; resolved to ancient Serio hydronym."),
    "b_coucy": ("Koutzîveste", "March fortress citadel of Coucy (in-game: Coucy)", "option_c_foundation", "c. 920 fortress of Archbishop Herve fails Burden of Proof on Antiquity; resolved via Option C march stronghold."),

    # Regional Sweep: Africa, India, Southeast Asia & Scandinavia
    "b_timbuktu": ("Djôlibe", "Ancient native Mandé hydronym of the Niger River Joliba (in-game: Timbuktu)", "option_b_hydronym", "c. 1100 Tuareg seasonal camp fails Burden of Proof on Antiquity; resolved to ancient Niger river hydronym Djôlibe."),
    "b_mansuriya": ("Sâbrâ", "Ancient substrate Sabra in the Byzacena plain near Kairouan (in-game: Mansuriya)", "indigenous_restitution", "946 Fatimid caliphal capital al-Mansuriya fails Burden of Proof on Antiquity; restored to ancient site Sabra."),
    "b_raqqada": ("Safûn", "Ancient Byzacena river course and olive plain (in-game: Raqqada)", "option_b_hydronym", "876 Aghlabid palace city Raqqada fails Burden of Proof on Antiquity; resolved to ancient Byzacena watercourse."),
    "b_gede": ("Sabâki", "Ancient Sabaki River estuary on the Swahili coast (in-game: Gede)", "option_b_hydronym", "11th-century Swahili stone town fails Burden of Proof on Antiquity; resolved to ancient Sabaki river basin."),
    "b_ungwana": ("Tâne", "Ancient Tana River delta reach on the Swahili coast (in-game: Ungwana)", "option_b_hydronym", "13th-century Swahili coastal town fails Burden of Proof on Antiquity; resolved to ancient Tana river delta."),
    "b_hargeisa": ("Lâs-Gêel", "Ancient Neolithic rock art sanctuary complex Las Geel (in-game: Hargeisa)", "indigenous_restitution", "19th-century settlement Hargeisa fails Burden of Proof on Antiquity; restored to ancient prehistoric sanctuary complex."),
    "b_bangkok": ("Mênam", "Ancient Chao Phraya River basin, Mother of Waters (in-game: Bangkok)", "option_b_hydronym", "15th-century village / 1782 capital fails Burden of Proof on Antiquity; resolved to ancient Chao Phraya hydronym Mênam."),
    "b_chiang_mai": ("Pîng", "Ancient Mae Ping River basin of the Mon-Dvaravati realm (in-game: Chiang Mai)", "option_b_hydronym", "1296 new capital of Lan Na fails Burden of Proof on Antiquity; resolved to ancient Ping river hydronym."),
    "b_BOR_Seria": ("Serîje", "Ancient Seria River basin of northern Borneo (in-game: Seria)", "option_b_hydronym", "1929 oil town fails Burden of Proof on Antiquity; resolved to ancient Seria river hydronym."),
    "b_faizabad": ("Sarajû", "Ancient sacred Sarayu River of the Ramayana (in-game: Faizabad)", "option_b_hydronym", "1730 foundation of Nawab Saadat Ali Khan I fails Burden of Proof on Antiquity; resolved to ancient sacred Sarayu hydronym."),
    "b_ahmadnagar": ("Sînâ", "Ancient Sina River basin in the Deccan plateau (in-game: Ahmadnagar)", "option_b_hydronym", "1494 capital of Ahmad Nizam Shah I fails Burden of Proof on Antiquity; resolved to ancient Sina river hydronym."),
    "b_hoshangabad": ("Narmadâ", "Ancient sacred Narmada River reach (in-game: Hoshangabad)", "option_b_hydronym", "1405 fortress of Hoshang Shah fails Burden of Proof on Antiquity; resolved to ancient sacred Narmada hydronym."),
    "b_fathabad": ("Padmâ", "Ancient Padma River reach of the Ganges delta (in-game: Fathabad)", "option_b_hydronym", "Late 15th-century sultanate mint town fails Burden of Proof on Antiquity; resolved to ancient Padma river hydronym."),
    "b_nasirabad": ("Brahmapûtra", "Ancient sacred Brahmaputra River reach (in-game: Nasirabad)", "option_b_hydronym", "19th-century colonial town fails Burden of Proof on Antiquity; resolved to ancient Brahmaputra river hydronym."),
    "b_khudabad": ("Mêhrân", "Ancient Mehran / Indus River reach in Sindh (in-game: Khudabad)", "option_b_hydronym", "1701 Kalhora capital fails Burden of Proof on Antiquity; resolved to ancient Indus/Mehran river hydronym."),
    "b_shergarh": ("Kâbul", "Ancient Kabul River confluence reach (in-game: Shergarh)", "option_b_hydronym", "1540 fortress of Sher Shah Suri fails Burden of Proof on Antiquity; resolved to ancient Kabul river hydronym."),
    "b_udaipur": ("Rangamatî", "Ancient Manikya royal capital Rangamati on the Gomati (in-game: Udaipur)", "indigenous_restitution", "1567 capital of Udai Manikya fails Burden of Proof on Antiquity; restored to ancient capital Rangamati."),
    "b_gangaikondacolapuram": ("Kâvêrî", "Ancient sacred Kaveri River reach in Cholamandalam (in-game: Gangaikondacolapuram)", "option_b_hydronym", "1025 Chola imperial capital of Rajendra Chola I fails Burden of Proof on Antiquity; resolved to ancient Kaveri hydronym."),
    "b_svendborg": ("Swînesunt", "Ancient Svendborgsund sound and strait of Funen (in-game: Svendborg)", "option_b_hydronym", "1229 Danish royal castle fails Burden of Proof on Antiquity; resolved to ancient Svendborgsund sound."),

    # Step 1: Western European Reform Abbeys, Dams & Dynastic Castles
    "b_clairvaux": ("Albetâl", "Ancient pre-867 Aube River valley (in-game: Clairvaux)", "option_b_hydronym", "1115 Cistercian abbey Clairvaux of St. Bernard fails Burden of Proof on Antiquity; resolved to ancient Aube river valley."),
    "b_citeaux": ("Vonge", "Ancient pre-867 Vouge River reach in Burgundy (in-game: Citeaux)", "option_b_hydronym", "1098 Cistercian mother abbey Cîteaux fails Burden of Proof on Antiquity; resolved to ancient Vouge river hydronym."),
    "b_rotterdam": ("Rotte", "Ancient pre-867 Rotte River basin in Holland (in-game: Rotterdam)", "option_b_hydronym", "c. 1270 river dam and settlement Rotterdam fails Burden of Proof on Antiquity; resolved to ancient Rotte river hydronym."),
    "b_heidelberg": ("Heiligenberch", "Ancient Celtic hillfort oppidum and Roman sanctuary on the Heiligenberg overlooking the Neckar (in-game: Heidelberg)", "indigenous_restitution", "1196 Hohenstaufen comital castle Heidelberg fails Burden of Proof on Antiquity; restored to ancient Celtic/Roman Heiligenberg."),
    "b_katzenelnbogen": ("Dörsbach", "Ancient pre-867 Dörsbach stream basin in the Taunus (in-game: Katzenelnbogen)", "option_b_hydronym", "c. 1095 comital castle Katzenelnbogen fails Burden of Proof on Antiquity; resolved to ancient Dörsbach hydronym."),
    "b_isenburg": ("Iserbach", "Ancient pre-867 Iserbach stream basin in the Westerwald (in-game: Isenburg)", "option_b_hydronym", "c. 1100 comital castle Isenburg fails Burden of Proof on Antiquity; resolved to ancient Iserbach hydronym."),
    "b_jaisalmer": ("Kaknî", "Ancient pre-867 Kakni River basin in the Thar desert (in-game: Jaisalmer)", "option_b_hydronym", "1156 desert citadel of Rawal Jaisal fails Burden of Proof on Antiquity; resolved to ancient Kakni river basin."),
    "b_furness": ("Vûrnês", "Ancient pre-867 Norse and Celtic coastal headland Fúrnese (in-game: Furness)", "option_b_hydronym", "1123 Cistercian abbey Furness fails Burden of Proof on Antiquity; resolved to ancient coastal headland."),

    # Step 2: Non-European Frontier Sweep (India, Africa, Southeast Asia)
    "b_amarkot": ("Hakrâ", "Ancient pre-867 Hakra River paleochannel basin in Sindh (in-game: Amarkot)", "option_b_hydronym", "11th-century Soomro desert fortress Amarkot fails Burden of Proof on Antiquity; resolved to ancient Hakra river basin."),
    "b_pathankot": ("Tschakkî", "Ancient pre-867 Chakki River confluence in Trigarta (in-game: Pathankot)", "option_b_hydronym", "11th-century Pathania Rajput stronghold fails Burden of Proof on Antiquity; resolved to ancient Chakki river confluence."),
    "b_gawilgarh": ("Sâtpure", "Ancient pre-867 Satpura mountain ridge in Maharashtra (in-game: Gawilgarh)", "option_b_hydronym", "12th-century Gawali hillfort fails Burden of Proof on Antiquity; resolved to ancient Satpura range."),
    "b_borgarh": ("Narmadâ-Tâl", "Ancient pre-867 Narmada River valley in Malwa (in-game: Borgarh)", "option_b_hydronym", "High medieval Paramara fortress fails Burden of Proof on Antiquity; resolved to ancient Narmada valley."),
    "b_aswan-west": ("Elefantîne", "Ancient Pharaonic and Roman island fortress Elephantine on the Nile (in-game: West Aswan)", "indigenous_restitution", "Modern administrative sector West Aswan fails Burden of Proof on Antiquity; restored to classical island fortress Elephantine."),
    "b_benin_marshes": ("Osse", "Ancient pre-867 Osse River delta reach (in-game: Benin marsches)", "option_b_hydronym", "Colonial administrative sector fails Burden of Proof on Antiquity; resolved to ancient Osse river delta."),
    "b_gobir-east": ("Rîme", "Ancient pre-867 Rima River basin in Hausaland (in-game: Gobir-East)", "option_b_hydronym", "Administrative sector Gobir-East fails Burden of Proof on Antiquity; resolved to ancient Rima river basin."),
    "b_salavan": ("Sê-Dôn", "Ancient pre-867 Se Don River basin in southern Laos (in-game: Salavan)", "option_b_hydronym", "Late medieval provincial outpost fails Burden of Proof on Antiquity; resolved to ancient Se Don river basin."),
    "b_BOR_Melak": ("Mahakâm", "Ancient pre-867 Mahakam River basin in Borneo (in-game: Melak)", "option_b_hydronym", "Late river trading post fails Burden of Proof on Antiquity; resolved to ancient Mahakam river basin."),

    # Step 3: De-Anglicization & Colonial Directional Remediation
    # West Africa & Sahel
    "b_upper_gambia": ("Kantôra", "Ancient pre-867 Mandinka trade kingdom and terminal Kantora on the Upper Gambia (in-game: Upper Gambia)", "indigenous_restitution", "Colonial administrative sector Upper Gambia fails Burden of Proof on Antiquity; restored to ancient Mandinka kingdom Kantora."),
    "b_west_kru": ("West-Krû", "Western reach of the ancient Kru / Krao coastline (in-game: West Kru)", "option_b_hydronym", "Colonial English descriptor West Kru fails Burden of Proof on Antiquity; standardized to West-Krû."),
    "b_upper_lobo": ("Ober-Lobô", "Upper reach of the pre-867 Lobo River basin (in-game: Upper Lobo)", "option_b_hydronym", "Colonial English descriptor Upper Lobo fails Burden of Proof on Antiquity; standardized to Ober-Lobô."),
    "b_lower_lobo": ("Nider-Lobô", "Lower confluence of the pre-867 Lobo and Sassandra rivers (in-game: Lower Lobo)", "option_b_hydronym", "Colonial English descriptor Lower Lobo fails Burden of Proof on Antiquity; standardized to Nider-Lobô."),
    "b_bandama-west": ("West-Bandama", "Western basin of the pre-867 Bandama River (in-game: Bandama-West)", "option_b_hydronym", "Colonial English descriptor Bandama-West fails Burden of Proof on Antiquity; standardized to West-Bandama."),
    "b_upper_nyene": ("Ober-Njene", "Upper reach of the pre-867 Nyene River basin (in-game: Upper Nyene)", "option_b_hydronym", "Colonial English descriptor Upper Nyene fails Burden of Proof on Antiquity; standardized to Ober-Njene."),
    "b_lower_nyene": ("Nider-Njene", "Lower reach of the pre-867 Nyene River basin (in-game: Lower Nyene)", "option_b_hydronym", "Colonial English descriptor Lower Nyene fails Burden of Proof on Antiquity; standardized to Nider-Njene."),
    "b_upper_nzi": ("Ober-Nzi", "Upper reach of the pre-867 Nzi River basin (in-game: Upper Nzi)", "option_b_hydronym", "Colonial English descriptor Upper Nzi fails Burden of Proof on Antiquity; standardized to Ober-Nzi."),
    "b_kweni-east": ("Ôst-Kwêni", "Eastern plateau of the pre-867 Kweni region (in-game: Kweni-East)", "sub_barony_adaptation", "Colonial English descriptor Kweni-East fails Burden of Proof on Antiquity; standardized to Ôst-Kwêni."),
    "b_upper_tano": ("Ober-Tano", "Upper reach of the pre-867 sacred Tano River basin in Akan territory (in-game: Upper Tano)", "option_b_hydronym", "Colonial English descriptor Upper Tano fails Burden of Proof on Antiquity; standardized to Ober-Tano."),
    "b_middle_tano": ("Middel-Tano", "Middle reach of the pre-867 sacred Tano River basin (in-game: Middle Tano)", "option_b_hydronym", "Colonial English descriptor Middle Tano fails Burden of Proof on Antiquity; standardized to Middel-Tano."),
    "b_mole_south": ("Sût-Mole", "Southern basin of the pre-867 Mole River in Gonja (in-game: Mole-South)", "option_b_hydronym", "Colonial English descriptor Mole-South fails Burden of Proof on Antiquity; standardized to Sût-Mole."),
    "b_upper_mole": ("Ober-Mole", "Upper basin of the pre-867 Mole River near Daboya (in-game: Upper Mole)", "option_b_hydronym", "Colonial English descriptor Upper Mole fails Burden of Proof on Antiquity; standardized to Ober-Mole."),
    "b_south_igbo": ("Sût-Igbô", "Southern forest reach of the pre-867 Igbo territory (in-game: South Igbo)", "sub_barony_adaptation", "Colonial English descriptor South Igbo fails Burden of Proof on Antiquity; standardized to Sût-Igbô."),
    "b_east_igala": ("Ôst-Igale", "Eastern plateau of the pre-867 Igala realm (in-game: East Igala)", "sub_barony_adaptation", "Colonial English descriptor East Igala fails Burden of Proof on Antiquity; standardized to Ôst-Igale."),
    "b_lower_guara": ("Nider-Guara", "Lower confluence of the pre-867 Gurara River with the Niger (in-game: Lower Guara)", "option_b_hydronym", "Colonial English descriptor Lower Guara fails Burden of Proof on Antiquity; standardized to Nider-Guara."),
    "b_seno-south": ("Sût-Senô", "Southern plain of the pre-867 Séno-Gondo depression (in-game: Seno-South)", "sub_barony_adaptation", "Colonial English descriptor Seno-South fails Burden of Proof on Antiquity; standardized to Sût-Senô."),
    "b_west_mema": ("West-Meme", "Western marshes of the ancient pre-867 Soninke kingdom of Méma (in-game: West Mema)", "sub_barony_adaptation", "Colonial English descriptor West Mema fails Burden of Proof on Antiquity; standardized to West-Meme."),
    "b_hodh_west": ("West-Hodh", "Western basin of the ancient pre-867 Hodh depression (in-game: Hodh-West)", "sub_barony_adaptation", "Colonial English descriptor Hodh-West fails Burden of Proof on Antiquity; standardized to West-Hodh."),

    # Horn of Africa, Nile Basin & East Africa
    "b_lower_omo": ("Nider-Omo", "Lower delta reach of the pre-867 Omo River near Lake Turkana (in-game: Lower Omo)", "option_b_hydronym", "Colonial English descriptor Lower Omo fails Burden of Proof on Antiquity; standardized to Nider-Omo."),
    "b_upper_dinder": ("Ober-Dinder", "Upper headwaters reach of the pre-867 Dinder River in the Ethiopian highlands (in-game: Upper Dinder)", "option_b_hydronym", "Colonial English descriptor Upper Dinder fails Burden of Proof on Antiquity; standardized to Ober-Dinder."),
    "b_upper_milk": ("Ober-Mîlch", "Upper reach of the pre-867 Wadi el-Malik in the Bayuda Steppe (in-game: Upper Milk)", "option_b_hydronym", "Colonial English descriptor Upper Milk fails Burden of Proof on Antiquity; standardized to Ober-Mîlch."),
    "b_middle_atbara": ("Middel-Atbara", "Middle reach of the pre-867 Atbara River basin in Kassala (in-game: Middle Atbara)", "option_b_hydronym", "Colonial English descriptor Middle Atbara fails Burden of Proof on Antiquity; standardized to Middel-Atbara."),
    "b_middle_awash": ("Middel-Awâsch", "Middle rift basin reach of the pre-867 Awash River (in-game: Middle Awâsch)", "option_b_hydronym", "Colonial English descriptor Middle Awâsch fails Burden of Proof on Antiquity; standardized to Middel-Awâsch."),
    "b_lower_odib": ("Nider-Aidâp", "Lower coastal plain of the pre-867 Wadi Odib near Aidhab (in-game: Lower Odib)", "option_b_hydronym", "Colonial English descriptor Lower Odib fails Burden of Proof on Antiquity; standardized to Nider-Aidâp."),
    "b_naqis-north": ("Nord-Nakîs", "Northern gold-mining district of the pre-867 Wadi Allaqi (in-game: North Naqis)", "sub_barony_adaptation", "Colonial English descriptor North Naqis fails Burden of Proof on Antiquity; standardized to Nord-Nakîs."),
    "b_upper_amur": ("Ober-Amûr", "Upper basin reach of the pre-867 Wadi Amur in Nubia (in-game: Upper Amur)", "option_b_hydronym", "Colonial English descriptor Upper Amur fails Burden of Proof on Antiquity; standardized to Ober-Amûr."),
    "b_baqlin-north": ("Nord-Baklîn", "Northern territory of the pre-867 Beja Baqlin kingdom (in-game: North Baqlin)", "sub_barony_adaptation", "Colonial English descriptor North Baqlin fails Burden of Proof on Antiquity; standardized to Nord-Baklîn."),
    "b_baqlin-west": ("West-Baklîn", "Western hills of the pre-867 Beja Baqlin kingdom (in-game: West Baqlin)", "sub_barony_adaptation", "Colonial English descriptor West Baqlin fails Burden of Proof on Antiquity; standardized to West-Baklîn."),
    "b_south_seraye": ("Sût-Seraje", "Southern plateau of the pre-867 Seraye realm (in-game: South Seraye)", "sub_barony_adaptation", "Colonial English descriptor South Seraye fails Burden of Proof on Antiquity; standardized to Sût-Seraje."),
    "b_east_amhara": ("Ôst-Amhära", "Eastern escarpment of the pre-867 Amhara realm (in-game: East Amhära)", "sub_barony_adaptation", "Colonial English descriptor East Amhära fails Burden of Proof on Antiquity; standardized to Ôst-Amhära."),
    "b_west_gojjam": ("West-Gojjam", "Western loop of the pre-867 Gojjam province within the Blue Nile bend (in-game: West Gojjam)", "sub_barony_adaptation", "Colonial English descriptor West Gojjam fails Burden of Proof on Antiquity; standardized to West-Gojjam."),
    "b_damot-west": ("West-Damôt", "Western marches of the pre-867 Kingdom of Damot (in-game: Damot-West)", "sub_barony_adaptation", "Colonial English descriptor Damot-West fails Burden of Proof on Antiquity; standardized to West-Damôt."),
    "b_wellega-south": ("Sût-Welega", "Southern basin of the pre-867 Welega / Didesa region (in-game: Wellega-South)", "sub_barony_adaptation", "Colonial English descriptor Wellega-South fails Burden of Proof on Antiquity; standardized to Sût-Welega."),
    "b_arusi-north": ("Nord-Arûsi", "Northern plateau reach of the pre-867 Arsi realm (in-game: Arusi-North)", "sub_barony_adaptation", "Colonial English descriptor Arusi-North fails Burden of Proof on Antiquity; standardized to Nord-Arûsi."),
    "b_west_adal": ("West-Adal", "Western plateau reach of the pre-867 Adal region near Harar (in-game: West Adal)", "sub_barony_adaptation", "Colonial English descriptor West Adal fails Burden of Proof on Antiquity; standardized to West-Adal."),
    "b_hargaya-south": ("Sût-Hargâje", "Southern Ogo plateau reach near Hargeisa (in-game: Hargaya-South)", "sub_barony_adaptation", "Colonial English descriptor Hargaya-South fails Burden of Proof on Antiquity; standardized to Sût-Hargâje."),
    "b_fafan-south": ("Sût-Fafân", "Southern reach of the pre-867 Fafan River valley (in-game: Fafan-South)", "option_b_hydronym", "Colonial English descriptor Fafan-South fails Burden of Proof on Antiquity; standardized to Sût-Fafân."),
    "b_edd-north": ("Nord-Êt", "Northern coastal plain of the pre-867 Red Sea port of Edd (in-game: Edd-North)", "sub_barony_adaptation", "Colonial English descriptor Edd-North fails Burden of Proof on Antiquity; standardized to Nord-Êt."),
    "b_south_danakil": ("Sût-Danakil", "Southern salt depression reach of the pre-867 Danakil basin (in-game: South Danakil)", "sub_barony_adaptation", "Colonial English descriptor South Danakil fails Burden of Proof on Antiquity; standardized to Sût-Danakil."),
    "b_lower_nugaal": ("Nider-Nugâl", "Lower reach of the pre-867 Nugaal Valley towards the ocean (in-game: Lower Nugaal)", "option_b_hydronym", "Colonial English descriptor Lower Nugaal fails Burden of Proof on Antiquity; standardized to Nider-Nugâl."),
    "b_upper_nugaal": ("Ober-Nugâl", "Upper limestone plateau reach of the pre-867 Nugaal Valley (in-game: Upper Nugaal)", "option_b_hydronym", "Colonial English descriptor Upper Nugaal fails Burden of Proof on Antiquity; standardized to Ober-Nugâl."),
    "b_mudug-north": ("Nord-Mudûch", "Northern plateau reach of the pre-867 Mudug region (in-game: Mudug-North)", "sub_barony_adaptation", "Colonial English descriptor Mudug-North fails Burden of Proof on Antiquity; standardized to Nord-Mudûch."),
    "b_hobyo-north": ("Nord-Hobyo", "Northern coastal reach of the pre-867 Hobyo strand (in-game: Hobyo-North)", "sub_barony_adaptation", "Colonial English descriptor Hobyo-North fails Burden of Proof on Antiquity; standardized to Nord-Hobyo."),
    "b_jubba-north": ("Nord-Jubba", "Upper reach of the pre-867 Jubba River confluence near Luuq (in-game: Jubba-North)", "option_b_hydronym", "Colonial English descriptor Jubba-North fails Burden of Proof on Antiquity; standardized to Nord-Jubba."),
    "b_marehan-north": ("Nord-Marehân", "Northern pastoral reach of the pre-867 Marehan region on the Jubba (in-game: Marehan-North)", "sub_barony_adaptation", "Colonial English descriptor Marehan-North fails Burden of Proof on Antiquity; standardized to Nord-Marehân."),
    "b_middle_shebelle": ("Middel-Schebelle", "Middle agricultural basin of the pre-867 Shebelle River (in-game: Middle-Schebelle)", "option_b_hydronym", "Colonial English descriptor Middle-Schebelle fails Burden of Proof on Antiquity; standardized to Middel-Schebelle."),
    "b_gidaya-north": ("Nord-Gidâje", "Northern highland basin reach of the pre-867 Gidaya realm (in-game: Gidaya-North)", "sub_barony_adaptation", "Colonial English descriptor Gidaya-North fails Burden of Proof on Antiquity; standardized to Nord-Gidâje."),
    "b_east_sidamo": ("Ôst-Sidâme", "Eastern escarpment reach of the pre-867 Sidamo region (in-game: East Sidamo)", "sub_barony_adaptation", "Colonial English descriptor East Sidamo fails Burden of Proof on Antiquity; standardized to Ôst-Sidâme."),
    "b_lower_dawa": ("Nider-Dawa", "Lower canyon confluence reach of the pre-867 Dawa River (in-game: Lower Dawa)", "option_b_hydronym", "Colonial English descriptor Lower Dawa fails Burden of Proof on Antiquity; standardized to Nider-Dawa."),
    "b_bali-west": ("West-Bâle", "Western alpine reach of the pre-867 Bale Mountains (in-game: Bali-West)", "sub_barony_adaptation", "Colonial English descriptor Bali-West fails Burden of Proof on Antiquity; standardized to West-Bâle."),
    "b_upper_kutulo": ("Ober-Kutulo", "Upper watering basin reach of the pre-867 Kutulo depression (in-game: Upper Kutulo)", "sub_barony_adaptation", "Colonial English descriptor Upper Kutulo fails Burden of Proof on Antiquity; standardized to Ober-Kutulo."),
    "b_dawa_south": ("Sût-Dawa", "Southern basin reach of the pre-867 Dawa River near El Wak (in-game: Dawa-South)", "option_b_hydronym", "Colonial English descriptor Dawa-South fails Burden of Proof on Antiquity; standardized to Sût-Dawa."),
    "b_lower_jubba": ("Gobweyn", "Ancient estuarine coastal settlement of Gobweyn at the mouth of the Jubba River (in-game: Lower Jubba)", "indigenous_restitution", "Colonial English descriptor Lower Jubba fails Burden of Proof on Antiquity; restored to ancient estuarine settlement Gobweyn."),
    "b_lower_kutulo": ("Nider-Kutulo", "Lower drainage reach of the pre-867 Kutulo / Lak Dera basin (in-game: Lower Kutulo)", "sub_barony_adaptation", "Colonial English descriptor Lower Kutulo fails Burden of Proof on Antiquity; standardized to Nider-Kutulo."),
    "b_central_jbl_quzlum": ("Middel-Kolsûm", "Central range of the classical Red Sea Hills Mount Clysma / Qulzum (in-game: Central Jabal Quzlum)", "classical_antiquity", "Colonial English descriptor Central Jabal Quzlum fails Burden of Proof on Antiquity; standardized to Middel-Kolsûm."),
    "b_south_jbl_quzlum": ("Sût-Kolsûm", "Southern range of the classical Red Sea Hills Mount Clysma monastic zone (in-game: South Jabal Quzlum)", "classical_antiquity", "Colonial English descriptor South Jabal Quzlum fails Burden of Proof on Antiquity; standardized to Sût-Kolsûm."),
    "b_central_kordofan": ("Middel-Kordofân", "Central savanna reach of the pre-867 Kordofan realm (in-game: Central Kordofan)", "sub_barony_adaptation", "Colonial English descriptor Central Kordofan fails Burden of Proof on Antiquity; standardized to Middel-Kordofân."),
    "b_kadam-west": ("West-Kadâm", "Western slopes of the pre-867 Mount Kadam massif (in-game: Kadam-West)", "sub_barony_adaptation", "Colonial English descriptor Kadam-West fails Burden of Proof on Antiquity; standardized to West-Kadâm."),
    "b_tibesti-central": ("Middel-Tibêsti", "Central volcanic plateau of the pre-867 Tibesti Mountains (in-game: Central Tibesti)", "sub_barony_adaptation", "Colonial English descriptor Central Tibesti fails Burden of Proof on Antiquity; standardized to Middel-Tibêsti."),
    "b_fazughli_east": ("Ôst-Fasûgli", "Eastern foothills of the pre-867 Fazughli gold-bearing massif on the Blue Nile (in-game: Eastern Fazughli)", "sub_barony_adaptation", "Colonial English descriptor Eastern Fazughli fails Burden of Proof on Antiquity; standardized to Ôst-Fasûgli."),
    "b_gumuz_west": ("West-Gumûs", "Western lowlands of the pre-867 Gumuz realm (in-game: Gumuz-West)", "sub_barony_adaptation", "Colonial English descriptor Gumuz-West fails Burden of Proof on Antiquity; standardized to West-Gumûs."),

    # Steppe, Central Asia, Iran & Burma
    "b_mariupol": ("Kalmjûs", "Ancient pre-867 Kalmius River estuary on the Sea of Azov (in-game: South Kalka)", "option_b_hydronym", "1778 foundation Mariupol / colonial descriptor South Kalka fails Burden of Proof on Antiquity; resolved to ancient Kalmius rivermouth."),
    "b_karabutak": ("Mugaldschar-Berch", "Ancient Turkic Mugalzhar mountain range in western Kazakhstan (in-game: Mugodschar Hills)", "option_b_hydronym", "Colonial English descriptor Mugodschar Hills fails Burden of Proof on Antiquity; standardized to Mugaldschar-Berch."),
    "b_lower_karran": ("Nider-Karrân", "Lower alluvial reach of the pre-867 Karran district in Transoxiana (in-game: Lower Karran)", "sub_barony_adaptation", "Colonial English descriptor Lower Karran fails Burden of Proof on Antiquity; standardized to Nider-Karrân."),
    "b_north_jaz_murian": ("Nord-Jaz-Murjân", "Northern endorheic depression of the pre-867 Jaz Murian basin in Kirman (in-game: North Jaz Murian)", "sub_barony_adaptation", "Colonial English descriptor North Jaz Murian fails Burden of Proof on Antiquity; standardized to Nord-Jaz-Murjân."),
    "b_popa": ("Popa-Berch", "Classical Burmese sacred volcanic Nat sanctuary Popa Taung (in-game: Mount Popa)", "indigenous_restitution", "Colonial English descriptor Mount Popa fails Burden of Proof on Antiquity; restored to classical Burmese sacred peak Popa-Berch."),

    # Step 4: Britannia & Insular Anglo-Saxon Semantic Calques
    # Fortresses, Burhs & Enclosures (-burh / -bury / -borough -> -burch)
    "b_aylesbury": ("Eilesburch", "Aylesbury (Old English Ægeles-burh, Aegel's stronghold) calqued to Tarraconian Eilesburch (in-game: Aylesbury)", "descriptive_calque", "Anglo-Saxon burh toponym calqued to Tarraconian Eilesburch."),
    "b_banbury": ("Bannaburch", "Banbury (Old English Banna's burh) calqued to Tarraconian Bannaburch (in-game: Banbury)", "descriptive_calque", "Anglo-Saxon burh toponym calqued to Tarraconian Bannaburch."),
    "b_bishops_castle": ("Westburch", "Westbury (Old English West-burh, western stronghold) calqued to Tarraconian Westburch (in-game: Bishops Castle)", "descriptive_calque", "Anglo-Saxon burh toponym calqued to Tarraconian Westburch."),
    "b_malmesbury": ("Malmesburch", "Malmesbury (Old English Maildubh's burh) calqued to Tarraconian Malmesburch (in-game: Malmesbury)", "descriptive_calque", "Anglo-Saxon burh toponym calqued to Tarraconian Malmesburch."),
    "b_ramsbury": ("Ramesburch", "Ramsbury (Old English Hræfnes-burh, Raven's fort) calqued to Tarraconian Ramesburch (in-game: Ramsbury)", "descriptive_calque", "Anglo-Saxon burh toponym calqued to Tarraconian Ramesburch."),
    "b_rothbury": ("Rôtburch", "Rothbury (Old English Rōþ-burh, red/cleared stronghold) calqued to Tarraconian Rôtburch (in-game: Rothbury)", "descriptive_calque", "Anglo-Saxon burh toponym calqued to Tarraconian Rôtburch."),
    "b_shaftesbury": ("Schaftesburch", "Shaftesbury (Old English Sceaftes-burh) calqued to Tarraconian Schaftesburch (in-game: Shaftesbury)", "descriptive_calque", "Anglo-Saxon burh toponym calqued to Tarraconian Schaftesburch."),
    "b_sudbury": ("Sûtburch", "Sudbury (Old English Sūþ-burh, southern stronghold) calqued to Tarraconian Sûtburch (in-game: Sudbury)", "descriptive_calque", "Anglo-Saxon burh toponym calqued to Tarraconian Sûtburch."),
    "b_scarborough": ("Scharburch", "Scarborough (Old Norse Skarthabork) calqued to Tarraconian Scharburch (in-game: Scarborough)", "descriptive_calque", "Norse burh toponym calqued to Tarraconian Scharburch."),

    # Homesteads & Settlements (-hām / -ham / -hêm -> -heim)
    "b_birmingham": ("Bôrmingheim", "Birmingham (Old English Beorminga-hām, estate of Beorma's kin) regularized to archaic Old English Bôrmingheim (in-game: Birmingham)", "descriptive_calque", "Archaic Old English hām toponym regularized to Bôrmingheim."),
    "b_buckingham": ("Buckingheim", "Buckingham (Old English Buccingahamm, meadow/settlement of Bucca's folk) calqued to Tarraconian Buckingheim (in-game: Buckingham)", "descriptive_calque", "Anglo-Saxon hām toponym calqued to Tarraconian Buckingheim."),
    "b_cottingham": ("Cottingheim", "Cottingham (Old English Cottinga-hām, homestead of Cotta's folk) calqued to Tarraconian Cottingheim (in-game: Cottingham)", "descriptive_calque", "Anglo-Saxon hām toponym calqued to Tarraconian Cottingheim."),
    "b_evesham": ("Evescheim", "Evesham (Old English Eoves-ham, homestead of Eof) calqued to Tarraconian Evescheim (in-game: Evesham)", "descriptive_calque", "Anglo-Saxon hām toponym calqued to Tarraconian Evescheim."),
    "b_hexham": ("Hexheim", "Hexham (Old English Hagustaldes-hām, warrior's estate) calqued to Tarraconian Hexheim (in-game: Hexham)", "descriptive_calque", "Anglo-Saxon hām toponym calqued to Tarraconian Hexheim."),
    "b_walsingham": ("Walschingheim", "Walsingham (Old English Wælsinga-hām, homestead of Wæls's folk) calqued to Tarraconian Walschingheim (in-game: Walsingham)", "descriptive_calque", "Anglo-Saxon hām toponym calqued to Tarraconian Walschingheim."),
    "b_nottingham": ("Snotingheim", "Nottingham (Old English Snotingahām, homestead of Snot's folk) calqued to Tarraconian Snotingheim (in-game: Nottingham)", "descriptive_calque", "Anglo-Saxon hām toponym calqued to Tarraconian Snotingheim."),
    "b_cunningham": ("Cunningheim", "Cunningham (Gaelic/Scots Cunnyngham) calqued to Tarraconian Cunningheim (in-game: Cunningham)", "descriptive_calque", "Scoto-Saxon toponym calqued to Tarraconian Cunningheim."),
    "b_coldingham": ("Coldingheim", "Coldingham (Old English Coludes-burh / Coldingham) calqued to Tarraconian Coldingheim (in-game: Coldingham)", "descriptive_calque", "Scoto-Saxon toponym calqued to Tarraconian Coldingheim."),

    # Open Fields & Clearings (-feld / -field / -fild -> -velt)
    "b_chesterfield": ("Tschestervelt", "Chesterfield (Old English Ceaster-feld, open field by the Roman fort) calqued to Tarraconian Tschestervelt (in-game: Chesterfield)", "descriptive_calque", "Anglo-Saxon feld toponym calqued to Tarraconian Tschestervelt."),
    "b_macclesfield": ("Makelesvelt", "Macclesfield (Old English Maccelesfeld, open field of Maccel) regularized to Old English Makelesvelt (in-game: Macclesfield)", "descriptive_calque", "Anglo-Saxon feld toponym regularized to Makelesvelt."),
    "b_radfield": ("Radvelt", "Radfield (Old English Rād-feld, open field by the highway/riding road) calqued to Tarraconian Radvelt (in-game: Radfield)", "descriptive_calque", "Anglo-Saxon feld toponym calqued to Tarraconian Radvelt."),

    # Woodlands & Forests (-wudu / -wood -> -walt)
    "b_newark": ("Scherwald", "Sherwood (Old English Scīrwudu, shire boundary forest) calqued to Tarraconian Scherwald (in-game: Newark)", "descriptive_calque", "Anglo-Saxon wudu toponym calqued to Tarraconian Scherwald."),

    # Enclosures & Homesteads (-weorþ / -worth -> -werth)
    "b_beodericsworth": ("Bôdericswerth", "Beodericsworth / Bury St Edmunds (Old English Beodrices-weorþ, Beodric's enclosure) calqued to Tarraconian Bôdericswerth (in-game: Beodericsworth)", "descriptive_calque", "Anglo-Saxon weorþ toponym calqued to Tarraconian Bôdericswerth."),
    "b_bosworth": ("Boswerth", "Bosworth (Old English Bosa's weorþ) calqued to Tarraconian Boswerth (in-game: Bosworth)", "descriptive_calque", "Anglo-Saxon weorþ toponym calqued to Tarraconian Boswerth."),
    "b_papworth": ("Papwerth", "Papworth (Old English Pappa's weorþ) calqued to Tarraconian Papwerth (in-game: Papworth)", "descriptive_calque", "Anglo-Saxon weorþ toponym calqued to Tarraconian Papwerth."),

    # Stone Landmarks (-stān / -stone -> -stên)
    "b_bolingsbroke": ("Bolingstên", "Bolingbroke / Bolingstone (Old English stone marker of Bulla's folk) calqued to Tarraconian Bolingstên (in-game: Bolingbroke)", "descriptive_calque", "Anglo-Saxon stān toponym calqued to Tarraconian Bolingstên."),
    "b_leightonstone": ("Leightonstên", "Leightonstone (Old English stone marker of the leek enclosure) calqued to Tarraconian Leightonstên (in-game: Leightonstone)", "descriptive_calque", "Anglo-Saxon stān toponym calqued to Tarraconian Leightonstên."),

    # Outlying Hamlets & Dairy Farms (-stoc / -stoke -> -stoc)
    "b_basingstoke": ("Basingstoc", "Basingstoke (Old English Basinga-stoc, outlying hamlet of Basa's folk) calqued to Tarraconian Basingstoc (in-game: Basingstoke)", "descriptive_calque", "Anglo-Saxon stoc toponym calqued to Tarraconian Basingstoc."),
    "b_winterstoke": ("Winterstoc", "Winterstoke (Old English Winter-stoc, winter settlement) calqued to Tarraconian Winterstoc (in-game: Winterstoke)", "descriptive_calque", "Anglo-Saxon stoc toponym calqued to Tarraconian Winterstoc."),

    # Pools & Harbors (-pōl / -pool -> -pûl)
    "b_hartlepool": ("Hôrtepûl", "Hartlepool (Old English Heruteu-pōl, pool of the Hart/Deer island) calqued to Tarraconian Hôrtepûl (in-game: Hartlepool)", "descriptive_calque", "Anglo-Saxon pōl toponym calqued to Tarraconian Hôrtepûl."),
    "b_poole": ("Pûl", "Poole (Old English Pōl, harbor pool) calqued to Tarraconian Pûl (in-game: Poole)", "descriptive_calque", "Anglo-Saxon pōl toponym calqued to Tarraconian Pûl."),

    # Romano-British Castra (-ceaster -> -zester)
    "b_colchester": ("Colnezester", "Colchester (Old English Colne-ceaster, Roman Camulodunum fort on the River Colne) regularized to Old English Colnezester (in-game: Colchester)", "descriptive_calque", "Romano-British castra toponym regularized to Colnezester."),
    "b_chichester": ("Tschitzester", "Chichester (Old English Cisse-ceaster, fort of Cissa) adapted with High German affrication to Tschitzester (in-game: Chichester)", "descriptive_calque", "Romano-British castra toponym adapted to Tarraconian Tschitzester."),

    # Enclosed Estates & Towns (-tūn / -ton -> -tûn)
    "b_abingdon": ("Abingtûn", "Abingdon (Old English Æbban-dun / Abing-tūn) calqued to Tarraconian Abingtûn (in-game: Abingdon)", "descriptive_calque", "Anglo-Saxon tūn toponym calqued to Tarraconian Abingtûn."),
    "b_bolton": ("Bôltûn", "Bolton (Old English Bōþl-tūn, settlement with a hall/manor) calqued to Tarraconian Bôltûn (in-game: Bolton)", "descriptive_calque", "Anglo-Saxon tūn toponym calqued to Tarraconian Bôltûn."),
    "b_bridlington": ("Bridlingtûn", "Bridlington (Old English Bretling-tūn) calqued to Tarraconian Bridlingtûn (in-game: Bridlington)", "descriptive_calque", "Anglo-Saxon tūn toponym calqued to Tarraconian Bridlingtûn."),
    "b_darlington": ("Darlingtûn", "Darlington (Old English Deornōþing-tūn) calqued to Tarraconian Darlingtûn (in-game: Darlington)", "descriptive_calque", "Anglo-Saxon tūn toponym calqued to Tarraconian Darlingtûn."),
    "b_kingston": ("Künincstûn", "Kingston upon Thames (Old English Cyninges-tūn, royal estate of coronations) calqued to Tarraconian Künincstûn (in-game: Kingston)", "descriptive_calque", "Anglo-Saxon tūn toponym calqued to Tarraconian Künincstûn."),
    "b_melton": ("Meltûn", "Melton Mowbray (Old English Middel-tūn / Melton) calqued to Tarraconian Meltûn (in-game: Melton)", "descriptive_calque", "Anglo-Saxon tūn toponym calqued to Tarraconian Meltûn."),
    "b_okehampton": ("Ochamptûn", "Okehampton (Old English Okement-tūn, settlement on the Okement) calqued to Tarraconian Ochamptûn (in-game: Okehampton)", "descriptive_calque", "Anglo-Saxon tūn toponym calqued to Tarraconian Ochamptûn."),
    "b_southampton": ("Sûthamptûn", "Southampton (Old English Sūþ-hām-tūn) calqued to Tarraconian Sûthamptûn (in-game: Southampton)", "descriptive_calque", "Anglo-Saxon tūn toponym calqued to Tarraconian Sûthamptûn."),
    "b_wigton": ("Wigtûn", "Wigton (Old English Wicga's tūn) calqued to Tarraconian Wigtûn (in-game: Wigton)", "descriptive_calque", "Anglo-Saxon tūn toponym calqued to Tarraconian Wigtûn."),
    "b_wigtown": ("Wigtûn", "Wigtown (Old English Wicga's tūn) calqued to Tarraconian Wigtûn (in-game: Wigtown)", "descriptive_calque", "Northumbrian Old English tūn calqued to Tarraconian Wigtûn."),
    "b_wolverhampton": ("Wulfrûne-Hamptûn", "Wolverhampton (Old English Wulfrūnehēantūn, high estate endowed by Lady Wulfrūn in 985 AD) calqued to Tarraconian Wulfrûne-Hamptûn (in-game: Wolverhampton)", "descriptive_calque", "Anglo-Saxon tūn toponym calqued to Tarraconian Wulfrûne-Hamptûn."),
    "b_taunton": ("Tônetûn", "Taunton (Old English Tone-tūn, town on the River Tone) calqued to Tarraconian Tônetûn (in-game: Taunton)", "descriptive_calque", "Anglo-Saxon tūn toponym calqued to Tarraconian Tônetûn."),
    "b_luton": ("Lêatûn", "Luton (Old English Lea-tūn, town on the River Lea) calqued to Tarraconian Lêatûn (in-game: Luton)", "descriptive_calque", "Anglo-Saxon tūn toponym calqued to Tarraconian Lêatûn."),

    # Minsters, Pillars & Churches (-mynster / -stapol / -kirk -> -munster / -stapel / -kirchen)
    "b_kidderminster": ("Kiddermunster", "Kidderminster (Old English Crideminster, minster church of Cynebert) calqued to High German Kiddermunster (in-game: Kidderminster)", "descriptive_calque", "Anglo-Saxon mynster toponym calqued to Tarraconian Kiddermunster."),
    "b_barnstaple": ("Bôrnstapel", "Barnstaple (Old English Beorn-stapol, post/pillar of Beorn) calqued to Tarraconian Bôrnstapel (in-game: Barnstaple)", "descriptive_calque", "Anglo-Saxon stapol toponym calqued to Tarraconian Bôrnstapel."),
    "b_selkirk": ("Selkirchen", "Selkirk (Old English Sele-cyrice, hall-church) calqued to Tarraconian Selkirchen (in-game: Selkirk)", "descriptive_calque", "Northumbrian Old English church toponym calqued to Selkirchen."),

    # Scandinavian Settlements & Havens (-býr / -by / -vík -> -dörp / -bî / -wîch / -lô)
    "b_west_derby": ("Westdörp", "West Derby (Old Norse Djúrbý / Domesday Westderbi, western deer-park settlement) calqued to Tarraconian Westdörp (in-game: West Derby)", "descriptive_calque", "Norse býr toponym calqued to Tarraconian Westdörp."),
    "b_appleby": ("Applebî", "Appleby (Old Norse Eplabý, apple orchard farmstead) adapted to Tarraconian Applebî (in-game: Appleby)", "descriptive_calque", "Norse býr toponym adapted to Tarraconian Applebî."),
    "b_whitby": ("Whitbî", "Whitby (Old Norse Hvítabý, white settlement / Streoneshalh) adapted to Tarraconian Whitbî (in-game: Whitby)", "descriptive_calque", "Norse býr toponym adapted to Tarraconian Whitbî."),
    "b_grimsby": ("Grimsbî", "Grimsby (Old Norse Grímsbý, Grim's settlement) adapted to Tarraconian Grimsbî (in-game: Grimsby)", "descriptive_calque", "Norse býr toponym adapted to Tarraconian Grimsbî."),
    "b_berwick": ("Berwîch", "Berwick-upon-Tweed (Old English Bere-wīc, barley farm/granary) calqued to Tarraconian Berwîch (in-game: Berwick)", "descriptive_calque", "Northumbrian Old English toponym calqued to Tarraconian Berwîch."),
    "b_wicklow": ("Wîkingelô", "Wicklow (Old Norse Víkingaló, meadow of the vikings) calqued to Tarraconian Wîkingelô (in-game: Wicklow)", "descriptive_calque", "Norse coastal haven toponym calqued to Tarraconian Wîkingelô."),

    # Metropolitan Restitutions & Disambiguations
    "b_york": ("Everwîch", "York (Old English Eoforwīc, Latin Eboracum, Old Norse Jórvík) metropolitan archiepiscopal capital of Northumbria disambiguated from regional North Riding (in-game: York)", "metropolitan_restitution", "Historical metropolitan archiepiscopal seat restored over riding."),
    "b_pockington": ("Pocklingtûn", "Pocklington (Old English Poclintun, royal estate of the East Riding) disambiguated from regional East Riding (in-game: Pocklington)", "descriptive_calque", "Historical constituent holding disambiguated from riding."),
    "b_leeds": ("Ledes", "Leeds (Celtic Elmet regio Loidis, Domesday Ledes) ancient district capital disambiguated from regional West Riding (in-game: Leeds)", "descriptive_calque", "Historical constituent holding disambiguated from riding."),

    # Tribal & Hundred Descriptors (-ingas / -ing -> -ingen)
    "b_blything": ("Blîthingen", "Blything (Old English Blīðingas, dwellers on the River Blyth) calqued to Tarraconian Blîthingen (in-game: Blything)", "descriptive_calque", "Anglo-Saxon tribal/hundred designation calqued to Blîthingen."),
    "b_kettering": ("Keteringen", "Kettering (Old English Cytringas, settlement of Ketel's folk) calqued to Tarraconian Keteringen (in-game: Kettering)", "descriptive_calque", "Anglo-Saxon tribal designation calqued to Keteringen."),
    "b_hastings": ("Hestingen", "Hastings (Old English Hæstingas, settlement of Hæsta's folk) calqued to Tarraconian Hestingen (in-game: Hastings)", "descriptive_calque", "Anglo-Saxon tribal designation calqued to Hestingen."),

    # Topographic Features & Valleys (-māw / -hlāw / -mōr / -gāra / -hyll / -cumb / -dell)
    "b_dunmow": ("Dûnmâwe", "Dunmow (Old English Dūn-māw, meadow on the hill) calqued to Tarraconian Dûnmâwe (in-game: Dunmow)", "descriptive_calque", "Anglo-Saxon topographic toponym calqued to Dûnmâwe."),
    "b_ludlow": ("Lûdlouwe", "Ludlow (Old English Hlūd-hlāw, hill by the loud river/rapids) calqued to Tarraconian Lûdlouwe (in-game: Ludlow)", "descriptive_calque", "Anglo-Saxon topographic toponym calqued to Lûdlouwe."),
    "b_wigmore": ("Wiggamôr", "Wigmore (Old English Wicga's mōr, Wicga's moorland) calqued to Tarraconian Wiggamôr (in-game: Wigmore)", "descriptive_calque", "Anglo-Saxon topographic toponym calqued to Wiggamôr."),
    "b_gore": ("Gâre", "Gore (Old English Gāra, triangular spit of land, ancient hundred moot site) calqued to Tarraconian Gâre (in-game: Gore)", "hundred_moot_calque", "Anglo-Saxon hundred moot site calqued to Gâre."),
    "b_ampthill": ("Emetehil", "Ampthill (Old English Æmete-hyll, ant hill) calqued to Tarraconian Emetehil (in-game: Ampthill)", "descriptive_calque", "Anglo-Saxon topographic toponym calqued to Emetehil."),
    "b_wycombe": ("Wîckumbe", "Wycombe (Old English Wīc-cumb, valley of dwellings) calqued to Tarraconian Wîckumbe (in-game: Wycombe)", "descriptive_calque", "Anglo-Saxon topographic toponym calqued to Wîckumbe."),
    "b_arun": ("Arundâl", "Arundel (Old English Hārhunde-dell, horehound herb valley) calqued to Tarraconian Arundâl (in-game: Arun)", "descriptive_calque", "Anglo-Saxon topographic toponym calqued to Arundâl."),
    # Archaic Old English Stem Regularizations & Civic Restorations
    "b_shrewsbury": ("Schrobbesburch", "Shrewsbury (Old English Scrobbesburh, scrubland fort) regularized to authentic Old English Schrobbesburch (in-game: Shrewsbury)", "indigenous_restitution", "Archaic Old English burh restored over Anglo-Norman Scrobesbyry."),
    "b_ilchester": ("Gifelzester", "Ilchester (Old English Givelceaster, Roman Lindinis fort on River Gifle/Ivel) regularized to Old English Gifelzester (in-game: Ilchester)", "descriptive_calque", "Archaic Old English ceaster regularized over Anglo-Norman Ivelcestre."),
    "b_leicester": ("Legrezester", "Leicester (Old English Legraceaster, fort of the Legra dwellers on River Soar) regularized to Old English Legrezester (in-game: Leicester)", "descriptive_calque", "Archaic Old English ceaster regularized over Anglo-Norman Leicester."),
    "b_worcester": ("Wigortzester", "Worcester (Old English Wigorceaster / Weogornaceaster, fort of the Weogora folk) regularized to Old English Wigortzester (in-game: Worcester)", "descriptive_calque", "Archaic Old English ceaster regularized to Wigortzester."),
    "b_gloucester": ("Glôwzester", "Gloucester (Old English Glēawceaster, Roman Glevum) regularized to Old English Glôwzester (in-game: Gloucester)", "descriptive_calque", "Archaic Old English ceaster regularized to Glôwzester."),
    "b_rochester": ("Rôfezester", "Rochester (Old English Hrōfeceaster, Roman Durobrivae fort of Hrof) regularized to Old English Rôfezester (in-game: Rochester)", "descriptive_calque", "Archaic Old English ceaster regularized to Rôfezester."),
    "b_chelmsford": ("Tschelmêresvurt", "Chelmsford (Old English Cēolmǣresford, crossing of Ceolmaer) regularized to Old English Tschelmêresvurt (in-game: Chelmsford)", "descriptive_calque", "Archaic Old English crossing regularized to Tschelmêresvurt."),
    "b_coventry": ("Koventrê", "Coventry (Old English Cofantrēo, Cofa's boundary tree) regularized to Old English Koventrê (in-game: Coventry)", "descriptive_calque", "Archaic Old English boundary toponym regularized to Koventrê."),
    "b_witney": ("Wittenöye", "Witney (Old English Wittan-īeg, Witta's island / meadow) regularized to Old English Wittenöye (in-game: Witney)", "descriptive_calque", "Archaic Old English river island toponym regularized to Wittenöye."),
    "b_totnes": ("Tottenês", "Totnes (Old English Tottan-næss, Totta's headland/ridge) regularized to Old English Tottenês (in-game: Totnes)", "descriptive_calque", "Archaic Old English headland toponym regularized to Tottenês."),
    "b_lyme": ("Lîm", "Lyme Regis (Old English Līm, ancient stream hydronym) regularized to Old English Lîm (in-game: Lyme)", "option_b_hydronym", "Archaic Old English stream hydronym regularized to Lîm."),
    "b_ripon": ("Hripum", "Ripon (Old English Inhrypum, dative settlement of the Hrype tribe) regularized to Old English Hripum (in-game: Ripon)", "indigenous_restitution", "Ancient tribal folk settlement regularized to Old English Hripum."),
    "b_chertsey": ("Tschôrtesöye", "Chertsey (Old English Ceortes-īeg, Ceorot's island, site of 666 AD St. Erkenwald abbey) regularized to Old English Tschôrtesöye (in-game: Chertsey)", "indigenous_restitution", "Ancient monastic river-island foundation restored over county designation."),
    "b_wareham": ("Wêrheim", "Wareham (Old English Werhām, settlement by the weir, King Alfred's burh) regularized to Old English Wêrheim (in-game: Wareham)", "indigenous_restitution", "Alfredian fortified naval burh restored over county designation."),
    "b_winchester": ("Wintanzester", "Winchester (Old English Wintanceaster, Roman Venta Belgarum, royal capital of Wessex) regularized to Old English Wintanzester (in-game: Winchester)", "indigenous_restitution", "Ancient royal capital of Wessex restored over county designation."),
    "b_exeter": ("Exanzester", "Exeter (Old English Exanceaster, Roman Isca Dumnoniorum fort on River Exe) regularized to Old English Exanzester (in-game: Exeter)", "indigenous_restitution", "Ancient Roman-Saxon capital of Devon restored over county designation."),
    "b_dover": ("Dovras", "Dover (Old English Dofras, Roman Portus Dubris at the Dour waters) regularized to Old English Dovras (in-game: Dover)", "indigenous_restitution", "Ancient Roman-Saxon port haven restored over county designation."),
    "b_bath": ("Hâtbatu", "Bath (Old English Hāt Bæðu, Roman Aquae Sulis, King Edgar's 973 coronation site) regularized to Old English Hâtbatu (in-game: Bath)", "indigenous_restitution", "Ancient Roman-Saxon bath and coronation sanctuary restored over county designation."),
    "b_kendal": ("Kêntâl", "Kendal (Old English Cenet-dāl, valley of the River Kent) regularized to Old English Kêntâl (in-game: Kendal)", "option_b_hydronym", "Ancient Kent river valley toponym regularized over county designation."),

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
        if c_props:
            props["c_tarr"] = c_props.get("tarr", "")
            props["c_tarr_direct"] = c_props.get("tarr_direct", "")
            props["c_tarr_hist"] = c_props.get("tarr_hist", "")
            props["c_origin"] = c_props.get("c_origin", "")
            props["c_anachronism"] = c_props.get("c_anachronism", "")

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
        is_sinosphere = (emp in SINO_EMPIRES or ck in SINO_FRONTIER_COUNTIES or ck in SINO_CURATED_COUNTIES)

        if ck not in county_used_names:
            county_used_names[ck] = set()

        # ----------------------------------------------------------------------
        # A. AUTHENTIC INDIGENOUS / ARCHAEOLOGICAL RESTITUTION OVERRIDE
        # ----------------------------------------------------------------------
        if bk in INDIGENOUS_RESTITUTIONS:
            sub_barony_count += 1
            entry = INDIGENOUS_RESTITUTIONS[bk]
            if len(entry) == 4:
                tarr_name, orig_desc, b_cat, anach_text = entry
            else:
                tarr_name, orig_desc = entry
                b_cat = "indigenous_restitution"
                anach_text = "Pre-867 native toponym restored over post-867 colonial foundation."
            tarr_clean = enforce_tarraconian_sound_laws(tarr_name)
            orig_final = orig_desc if "(in-game:" in orig_desc else f"{orig_desc} (in-game: {save_name})"
            res = {
                "name": tarr_clean,
                "b_tarr": tarr_clean,
                "b_tarr_direct": adapt_european_toponym(save_name),
                "b_tarr_hist": tarr_clean,
                "b_origin": orig_final,
                "b_anachronism": anach_text,
                "b_ipa": generate_tarraconian_ipa(tarr_clean),
                "holding_type": ht,
                "category": b_cat
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
                "b_hanzi": sino_res.get("b_hanzi", ""),
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
                if anach_note and (
                    f"Option B {tarr_clean}" in anach_note
                    or f"Option B {b_chosen}" in anach_note
                    or ("Option B" in anach_note and (b_chosen == c_tarr or b_chosen == save_name))
                    or ("Lacks documented pre-867 urban center" in anach_note and (tarr_clean in anach_note or b_chosen in anach_note))
                ):
                    anach_note = ""
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
                    cand_phon = normalize_phonetic_stem(cand)
                    has_stem_collision = any(
                        cand == un or
                        cand_phon == normalize_phonetic_stem(un) or
                        (len(cand_phon) >= 3 and len(normalize_phonetic_stem(un)) >= 3 and
                         difflib.SequenceMatcher(None, cand_phon, normalize_phonetic_stem(un)).ratio() >= 0.75)
                        for un in county_used_names[ck]
                    )
                    if cand in county_used_names[ck] or has_stem_collision:
                        opt_c_name, c_desc = evaluate_founder_option_c(
                            holder_name, holder_traits, house_name, ht, county_used_names[ck], save_name, bk=bk, ck=ck, is_anachronism=False
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
                        holder_name, holder_traits, house_name, ht, county_used_names[ck], save_name, bk=bk, ck=ck, is_anachronism=True
                    )
                    tarr_clean = opt_c_name
                    orig_desc = f"{save_name} — {c_desc}"

                    circ = is_circular_house(house_name, save_name, bk, ck)
                    house_desc = f"of House {house_name}" if (house_name and not circ) else "under Toponym-First foundation (disqualifying circular in-game house)"
                    if bk == "b_baranovichi":
                        anach_note = f"Post-867 foundation lacking pre-867 attestation under Burden of Proof on Antiquity (1871 railway station); resolved via Option C based on save ruler {holder_name}."
                    elif bk in POST_867_ANACHRONISMS:
                        anach_note = f"Post-867 foundation lacking pre-867 attestation under Burden of Proof on Antiquity ({POST_867_ANACHRONISMS[bk]}); resolved via Option C based on save ruler {holder_name} {house_desc}."
                    elif anc_reason == "classical_late_foundation":
                        anach_note = f"Post-867 feudal fortress / late foundation in classical province; resolved via Option C based on save ruler {holder_name} {house_desc}."
                    elif anc_reason == "high_medieval_foundation":
                        anach_note = f"Post-867 high medieval foundation; resolved via Option C based on save ruler {holder_name} {house_desc}."
                    elif anc_reason == "modern_railway_foundation":
                        anach_note = f"Modern industrial/railway foundation lacking pre-867 attestation under Burden of Proof on Antiquity; resolved via Option C based on save ruler {holder_name} {house_desc}."
                    elif anc_reason == "late_settlement_foundation":
                        anach_note = f"Post-867 late settlement foundation lacking pre-867 attestation under Burden of Proof on Antiquity; resolved via Option C based on save ruler {holder_name} {house_desc}."
                    elif anc_reason == "post_867_eponymous_person":
                        anach_note = f"Post-867 eponymous foundation named after historical person post-dating 867 AD under Burden of Proof on Antiquity; resolved via Option C based on save ruler {holder_name} {house_desc}."
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

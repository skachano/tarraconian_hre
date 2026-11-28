#!/usr/bin/env python3
"""
pipeline_stage4_calque_mediation.py

Stage 4 of the Tarraconian Barony-Tier Toponymic Naming Pipeline (v2):
Procedure 1 & 2 Transparency, Calquing & Phonological Mediation across all
10,239 occupied baronies from Stage 3 (`data/pipeline_stage3_synthesized.json`).

Implements:
  - Track S Procedure 1 CJK logographic calquing (1,235-char lexicon from
    data/sinosphere_kanji_tarraconian.json + SINO_BARONY_KANJI_EXT), paired
    with pre-867 Hanzi enrichment from barony_resolutions.json ONLY for
    pre-867 attested Track S sites, and 12th-century LMC/EMK/EMJ phonetics.
  - Rule 1 Gate: Rule 3 opaque marker / eponym / tribal guard (with exception
    for productive <Founder/Saint> + <Holding Generic> compounds).
  - Rule 2 (Direct Transparency): Full semantic calquing of transparent
    audit morphemes & Stage 3 abstract compounds, plus generic+topographic-head
    translation (e.g. Khalīj Ḥawākil -> Hawâkilbucht / Marsa -> -hâven).
  - Rule 3 (Transitional Mediation < 50y): Hybrid calque — indigenous proper
    stem adapted via transmission_profile + holding generic calqued.
  - Rule 4 (Semantic Rupture >= 50y): Strict phonetic nativization via
    multi-hop `historical_intermediaries` + `transmission_rules.to_tarraconian`.

Emits:
  - data/pipeline_stage4_mediated.json
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from sino_barony_kanji_ext import SINO_BARONY_KANJI_EXT
from historical_phonology import (
    GALLO_ROMANCE_IRREGULAR_STEMS,
    GALLO_ROMANCE_ISOS,
    LATIN_CURATED_PHRASES,
    LATIN_SINGLE_CURATED,
    LATIN_STRIPPABLE_GEO_WHEN_COMPOUNDED,
    NON_GALLO_ROMANCE_WORDS,
    NON_LATIN_MISATTRIBUTED,
    TARRACONIAN_DIRECT_CULTURES,
    adapt_gallo_romance_to_tarraconian,
    adapt_gallo_romance_word,
    adapt_latin_to_tarraconian,
    adapt_latin_word,
    is_gallo_romance_stem,
    is_true_latin_stem,
    resolve_wave1_decoder,
)

REPO_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_DIR / "data"

# Proper-person descriptors that must NEVER trigger accidental adjective/noun calquing
DISQUALIFIED_GLOSS_WORDS = {
    "alexander", "antiochus", "augustus", "attalus", "apama", "seleucus",
    "caesar", "constantine", "hadrian", "trajan", "philip", "ptolemy",
    "pompey", "tiberius", "herod", "king", "queen", "emperor", "prince",
    "duke", "count", "saint", "deity", "god", "goddess", "hero", "legendary",
    "possibly", "perhaps", "uncertain", "probably", "ancient",
}

# Transparent initial geographic heads commonly appearing in 2-word NTR phrases (Direct Transparency)
TRANSPARENT_NTR_HEADS: dict[str, tuple[str, str]] = {
    # lowercase phrase head/tail -> (tarr_suffix, gloss)
    "khalīj": ("-bucht", "gulf/bay"),
    "khalij": ("-bucht", "gulf/bay"),
    "buḥayrat": ("-sêe", "lake/lagoon"),
    "buhayrat": ("-sêe", "lake/lagoon"),
    "baḥr": ("-mêr", "sea/river"),
    "wādī": ("-vliez", "wadi/valley"),
    "wadi": ("-vliez", "wadi/valley"),
    "oued": ("-vliez", "river/wadi"),
    "jebel": ("-berch", "mountain"),
    "djebel": ("-berch", "mountain"),
    "jabal": ("-berch", "mountain"),
    "gunung": ("-berch", "mountain"),
    "bukit": ("-bühil", "hill"),
    "teluk": ("-bucht", "bay"),
    "selat": ("-strâte", "strait"),
    "pulau": ("-werder", "island"),
    "nusa": ("-werder", "island"),
    "dataran": ("-velt", "plain"),
    "banjaran": ("-grat", "range"),
    "kali": ("-bach", "river"),
    "sungai": ("-flôz", "river"),
    "batang": ("-flôz", "river"),
    "muara": ("-münde", "estuary"),
    "mont": ("-berch", "mount"),
    "monte": ("-berch", "mount"),
    "sierra": ("-kamm", "mountain range"),
    "rio": ("-flôz", "river"),
    "río": ("-flôz", "river"),
    "lago": ("-sêe", "lake"),
    "isola": ("-werder", "island"),
    "valle": ("-tâl", "valley"),
    "ponte": ("-brücke", "bridge"),
    "porto": ("-hâven", "harbor"),
    "ozero": ("-sêe", "lake"),
    "reka": ("-flôz", "river"),
    "gora": ("-berch", "mountain"),
    "ostrov": ("-werder", "island"),
    "kolpos": ("-bucht", "gulf"),
    "kólpos": ("-bucht", "gulf"),
    "potamos": ("-flôz", "river"),
    "limni": ("-sêe", "lake"),
    "oros": ("-berch", "mountain"),
    "nessos": ("-werder", "island"),
    "sinus": ("-bucht", "gulf"),
    "lacus": ("-sêe", "lake"),
    "flumen": ("-flôz", "river"),
    "mons": ("-berch", "mountain"),
    "montes": ("-berch", "mountains"),
    "insula": ("-werder", "island"),
    "portus": ("-port", "harbor"),
    "river": ("-flôz", "river"),
    "prefecture": ("-stat", "prefecture"),
    "commandery": ("-march", "commandery"),
    "mountain": ("-berch", "mountain"),
    "mountains": ("-berch", "mountains"),
    "mount": ("-berch", "mount"),
    "mt": ("-berch", "mount"),
    "lake": ("-sêe", "lake"),
    "island": ("-werder", "island"),
    "bay": ("-bucht", "bay"),
    "gulf": ("-bucht", "gulf"),
    "plain": ("-ebene", "plain"),
    "great": ("Grôz-", "great"),
    "little": ("Klein-", "little"),
    "cape": ("Kap-", "cape"),
    "northern": ("Nord-", "northern"),
    "southern": ("Sût-", "southern"),
    "eastern": ("Ôst-", "eastern"),
    "western": ("West-", "western"),
}

ENGLISH_META_GEO_WORDS = {"mount", "mt", "great", "little", "plain", "gulf", "bay", "river", "lake", "mountain", "mountains", "island", "strait", "commandery", "prefecture", "northern", "southern", "eastern", "western"}

# Supplementary Traditional/Simplified Hanzi & Stage 3 classifier entries
SUPPLEMENTARY_HANZI: dict[str, tuple[str, str, str]] = {
    "觀": ("-tempel", "Sacral Suffix", "Taoist abbey / Shrine"),
    "观": ("-tempel", "Sacral Suffix", "Taoist abbey / Shrine"),
    "關": ("-klûse", "Defensive Suffix", "Mountain pass / Frontier gate"),
    "院": ("-hof", "Sacral Suffix", "Cloister / Academy"),
    "宮": ("-palz", "Sacral Suffix", "Sacred palace / Shrine"),
    "宫": ("-palz", "Sacral Suffix", "Sacred palace / Shrine"),
    "府": ("-palz", "Administrative Suffix", "Prefectural seat"),
    "港": ("-hâven", "Maritime Suffix", "Sea harbor"),
    "津": ("-vurt", "Riparian Suffix", "River ford / ferry"),
    "汗": ("chân", "Phonetic Morpheme", "Khan / Huhan phonetic"),
    "慈": ("Gnâd-", "Virtue Prefix", "Merciful / Compassion"),
    "法": ("Êw-", "Sacral Prefix", "Dharma / Sacred Law"),
    "靖": ("Frid-", "Frontier Prefix", "Pacify / Tranquilize"),
    "寶": ("Edel-", "Precious Prefix", "Treasure"),
    "豐": ("Rîch-", "Abundance Prefix", "Abundant / Prosperous"),
    "鐵": ("Îsen-", "Material Prefix", "Iron"),
    "鎮": ("-wart", "Defensive Suffix", "Garrison fort"),
    "高": ("Hôch-", "Elevation Prefix", "High / Lofty"),
    "明": ("Lîcht-", "Solar Prefix", "Bright / Radiant"),
}

# Fallback 12th-century raw romanized readings BEFORE single-pass adaptation
HANZI_PHONETIC_READINGS: dict[str, str] = {
    "城": "cheng", "堡": "bao", "關": "guan", "关": "guan", "鎮": "zhen", "镇": "zhen",
    "州": "zhou", "府": "fu", "市": "shi", "港": "gang", "津": "jin",
    "寺": "si", "院": "yuan", "觀": "guan", "观": "guan", "宮": "gong", "宫": "gong",
    "威": "wei", "靖": "jing", "鐵": "tie", "铁": "tie", "高": "gao", "明": "ming",
    "清": "qing", "白": "bai", "青": "qing", "石": "shi", "松": "song",
    "慈": "ci", "法": "fa", "福": "fu", "靜": "jing", "寶": "bao", "宝": "bao",
    "豐": "feng", "丰": "feng", "利": "li", "通": "tong", "興": "xing", "兴": "xing",
    "永": "yong", "隆": "long", "德": "de", "昌": "chang",
}


def _apply_case(src: str, target: str) -> str:
    if not src:
        return target
    if src[0].isupper():
        return target[:1].upper() + target[1:]
    return target.lower() if target.isupper() else target


def _romanize_embedded_hanzi(
    s: str,
    kanji_readings: dict[str, tuple[str, str, str]],
    tf: str,
) -> str:
    """Replace any CJK Hanzi in a phonetic string using 12th-c. LMC/EMK/EMJ readings."""
    if not re.search(r"[\u3400-\u9FFF\uF900-\uFAFF]", s):
        return s
    out: list[str] = []
    for ch in s:
        if "\u3400" <= ch <= "\u9FFF" or "\uF900" <= ch <= "\uFAFF":
            if ch in kanji_readings:
                py, kr, jp = kanji_readings[ch]
                if "korean" in tf and kr:
                    rd = kr.split("/")[0].strip().lower()
                elif "japonic" in tf and jp:
                    rd = jp.split("/")[0].strip().lower()
                else:
                    rd = (py or kr or jp or "").split("/")[0].strip().lower()
                # strip pinyin tone marks
                for a, b in [("ā","a"),("á","a"),("ǎ","a"),("à","a"),("ē","e"),("é","e"),("ě","e"),("è","e"),("ī","i"),("í","i"),("ǐ","i"),("ì","i"),("ō","o"),("ó","o"),("ǒ","o"),("ò","o"),("ū","u"),("ú","u"),("ǔ","u"),("ù","u"),("ǖ","ü"),("ǘ","ü"),("ǚ","ü"),("ǜ","ü")]:
                    rd = rd.replace(a, b)
                out.append(rd or HANZI_PHONETIC_READINGS.get(ch, ""))
            else:
                out.append(HANZI_PHONETIC_READINGS.get(ch, ""))
        else:
            out.append(ch)
    return "".join(out)


# Stage 4A Historical Phonology decoders (Latin, Gallo-Romance, Byzantine Greek,
# Italo-/Occitano-/Ibero-/Eastern Romance) live under scripts/historical_phonology/.


def transliterate_stem_to_tarr(
    stem: str,
    transmission_profile: str,
    coinage_family: str,
    transmission_family: str,
    intermediaries_map: dict[tuple[str, str], dict[str, Any]],
    trans_rules: dict[str, Any],
    kanji_readings: dict[str, tuple[str, str, str]] | None = None,
    is_rupture: bool = False,
    source_iso: str | None = None,
) -> tuple[str, list[str]]:
    """
    Cascade-free single-pass phonological adaptation:
      1. Romanize any embedded CJK Hanzi into 12th-century phonetic reading.
      2. Apply documented historical multi-hop intermediary shift (when applicable).
      3. Apply single-pass longest-match digraph/orthography adaptation per family
         (no double `J -> Dsch -> Dstsch` or `kh -> ch -> tsch` cascades!).
    """
    notes: list[str] = []
    s = stem.strip()
    if not s:
        return s, notes
    s = re.sub(r"\bBashqurd", "Baschkurd", s, flags=re.I)

    tf = (transmission_family or coinage_family or "").lower()
    if kanji_readings is not None:
        s = _romanize_embedded_hanzi(s, kanji_readings, tf)

    # Step 1: Multi-hop historical intermediary filter (when coinage != transmission)
    if (coinage_family, transmission_family) in intermediaries_map:
        inter = intermediaries_map[(coinage_family, transmission_family)]
        iid = inter["id"]
        notes.append(iid)
        if iid == "greek_to_turkish":
            s = re.sub(r"polis$", "bolu", s, flags=re.I)
            s = re.sub(r"^K(?=[aeiou])", "G", s)
        elif iid == "greek_to_south_slavic":
            s = re.sub(r"polis$", "pol", s, flags=re.I)
            s = re.sub(r"os$", "", s, flags=re.I) if len(s) > 4 else s
        elif iid == "greek_to_arabic":
            s = re.sub(r"polis$", "bulus", s, flags=re.I)
            s = s.replace("p", "b").replace("P", "B")
        elif iid == "arabic_to_ibero_romance":
            s = re.sub(r"^W[aā]d[iī]\s+", "Guad-", s, flags=re.I)
            s = re.sub(r"^Qal['’`]?at\s+", "Calat-", s, flags=re.I)
            s = re.sub(r"\bkh", "g", s, flags=re.I)
        elif iid == "slavic_to_magyar":
            s = re.sub(r"grad$", "grád", s, flags=re.I)
        elif iid == "celtic_to_anglo_saxon":
            s = re.sub(r"dunum$", "tun", s, flags=re.I)

    # Step 2: Build single-pass non-overlapping substitution table for target family
    subs_map: dict[str, str] = {}
    rule_obj = trans_rules.get(transmission_profile) or {}
    # Import safe literal tokens from transmission_rules (excluding end-only anchors unless matched cleanly)
    for pat, repl in rule_obj.get("substitutions", []):
        if pat.startswith("^") or pat.endswith("$"):
            try:
                # only apply anchor-specific rules like vár$ -> wâr, burg$ -> burch
                if pat.endswith("$"):
                    if pat == "a$" and repl == "e" and tf not in {"east_slavic", "south_slavic", "west_slavic_lechitic", "west_slavic_czech_slovak"} and (coinage_family or "").lower() not in {"east_slavic", "south_slavic", "west_slavic_lechitic", "west_slavic_czech_slovak"}:
                        # Never turn -ca into -ce [ts] outside Slavic (Slavic -ca is already [tsa] -> -tze)
                        s = re.sub(r"([A-Za-zÀ-ɏ]{2,})[cC]a\b", r"\1ke", s)
                    s = re.sub(pat, repl, s)
            except re.error:
                pass
        elif len(pat) <= 3 and re.fullmatch(r"[A-Za-zÀ-ɏ]+", pat):
            subs_map[pat.lower()] = repl.lower()

    # Guarded polysyllabic Greek -os / -on drop (never clip short/classical island stems like Kos, Chios, Argos, Ainos, Andros, Lemnos)
    if transmission_profile == "greek_to_tarraconian":
        s_words = s.split()
        out_gw = []
        for gw in s_words:
            mg = re.match(r"^([A-Za-zÀ-ɏ]+)(os|on)$", gw, flags=re.I)
            if mg and len(mg.group(1)) >= 5 and len(re.findall(r"[aeiouyâêîôûäöü]+", mg.group(1), flags=re.I)) >= 2:
                out_gw.append(mg.group(1))
            else:
                out_gw.append(gw)
        s = " ".join(out_gw)

    if tf in {"arabic", "berber", "aramaic_hebrew"}:
        s = re.sub(r"\bBashqurd", "Baschkurd", s, flags=re.I)
        subs_map.update({"kh": "ch", "sh": "sch", "dj": "dsch", "dh": "d", "th": "t", "gh": "g", "j": "dsch", "q": "k"})
    elif tf in {"turkic", "oghur", "mongolic", "iranian"}:
        subs_map.update({"kh": "ch", "zh": "dsch", "sh": "sch", "ş": "sch", "š": "sch", "ç": "tsch", "č": "tsch", "q": "k"})
        if tf == "turkic":
            subs_map["ch"] = "tsch"
            subs_map["c"] = "dsch"
            subs_map["j"] = "dsch"
        if (coinage_family or "").lower() in {
            "hellenic", "latin_classical", "gallo_romance", "occitano_catalan",
            "ibero_romance", "italo_romance", "eastern_romance",
            "west_germanic", "north_germanic", "high_german", "low_german_dutch",
            "goidelic", "brythonic",
        }:
            subs_map.pop("c", None)
        if tf == "iranian":
            subs_map["ch"] = "tsch"
            subs_map["j"] = "dsch"
    elif tf in {"east_slavic", "south_slavic", "west_slavic_lechitic", "west_slavic_czech_slovak", "baltic"}:
        subs_map.update({"shch": "sch", "sz": "sch", "cz": "tsch", "rz": "rj", "zh": "sch", "sh": "sch", "š": "sch", "č": "tsch", "ž": "sch", "ř": "rj", "v": "w"})
        if tf != "baltic" and (coinage_family or "").lower() in {"east_slavic", "south_slavic", "west_slavic_lechitic", "west_slavic_czech_slovak"}:
            subs_map["ch"] = "ch"
            subs_map["c"] = "tz"
    elif tf in {"magyar"}:
        subs_map.update({"cs": "tsch", "sz": "s", "zs": "sch", "sh": "sch", "v": "w"})
    elif tf in {"indo_aryan", "dravidian", "austronesian", "mon_khmer", "tai_hmong", "tibetic", "burmese_qiangic"}:
        subs_map.update({"tsh": "tsch", "sh": "sch", "ch": "tsch", "ś": "sch", "ṣ": "sch", "j": "dsch"})
    elif tf in {"sinosphere_chinese", "korean", "japonic", "viet", "khitan", "tungusic"}:
        subs_map.update({"zh": "dsch", "ch": "tsch", "sh": "sch", "ts": "tz", "j": "dsch", "q": "tsch"})
    elif tf in {"tarraconian_imperial", "high_german", "low_german_dutch"}:
        # Preserve Tarraconian/German orthography cleanly without corrupting -st- / ch / j
        subs_map = {"ß": "ss"}
    else:
        subs_map.update({"sh": "sch", "zh": "sch", "dj": "dsch", "sj": "sch", "š": "sch", "č": "tsch", "ž": "sch"})

    # Never apply Romance/Turkic ch -> tsch onto Slavic [x] stems (e.g. Slovak vrchy)
    if (coinage_family or "").lower() in {"east_slavic", "south_slavic", "west_slavic_lechitic", "west_slavic_czech_slovak"}:
        if subs_map.get("ch") == "tsch":
            subs_map.pop("ch", None)

    # Adapt Berber/Tamazight 'gh' (Adagh -> Adach, Ifoghas -> Ifogas) and Sahara Arabic Tāghābū -> Tâgâbû
    # even when transmitted through Pontic/African rulers
    if (source_iso or "").lower() in {"ber", "tzm", "zgh", "kab", "shi"}:
        s = re.sub(r"gh\b", "ch", s, flags=re.I)
        subs_map.setdefault("gh", "g")
    elif (source_iso or "").lower() == "ara" and re.search(r"t[aā]gh[aā]b", s, re.I):
        subs_map.setdefault("gh", "g")

    if subs_map:
        # Protect longer Chancellery digraphs so single-pass never tears apart sch/tsch/dsch/tz
        for protected in ("dsch", "tsch", "sch", "tz"):
            if protected not in subs_map and any(k in subs_map for k in ("c", "ch", "sh", "ts", "j")):
                subs_map[protected] = protected
        # Sort longest keys first; match without cascading overlaps
        pat_parts = sorted(subs_map.keys(), key=len, reverse=True)
        # Do not match 'q' inside 'qu'
        regex_tokens = []
        for k in pat_parts:
            if k == "q":
                regex_tokens.append(r"q(?![uU])")
            elif k == "c" and tf == "turkic":
                regex_tokens.append(r"c(?=[aeiouäöüı]|$)")
            elif k == "c" and tf in {"east_slavic", "south_slavic", "west_slavic_lechitic", "west_slavic_czech_slovak"}:
                regex_tokens.append(r"(?<=[A-Za-zÀ-ɏ])(?<![sS])c(?=[aeiouyäöüâêîôû]|$)")
            else:
                regex_tokens.append(re.escape(k))
        single_re = re.compile("|".join(regex_tokens), re.I)

        def _repl_tok(m: re.Match[str]) -> str:
            tok = m.group(0)
            target = subs_map.get(tok.lower(), tok)
            return _apply_case(tok, target)

        s = single_re.sub(_repl_tok, s)

    # Handle word-initial Sinosphere Y->J / Ts->Z without re-scanning Ch/Sch
    if tf in {"sinosphere_chinese", "korean", "japonic", "viet", "khitan", "tungusic"}:
        s = re.sub(r"\b[Yy](?=[aeiou])", lambda m: "J" if m.group(0).isupper() else "j", s)
        s = re.sub(r"\b[Tt]z", lambda m: "Z" if m.group(0)[0].isupper() else "z", s)
    s = re.sub(r"\bXiao\s+Yangtong\b", "Schiaojangtong", s)

    # Diacritic & acute -> circumflex normalization (Rule 1)
    char_rep = {
        "ā": "â", "á": "â", "à": "a", "Ā": "Â", "Á": "Â", "À": "A",
        "ē": "ê", "é": "ê", "è": "e", "æ": "ê", "Ē": "Ê", "É": "Ê", "È": "E", "Æ": "Ê",
        "ī": "î", "í": "î", "ì": "i", "ý": "î", "Ī": "Î", "Í": "Î", "Ì": "I", "Ý": "Î",
        "ō": "ô", "ó": "ô", "ò": "o", "ø": "ö", "Ō": "Ô", "Ó": "Ô", "Ò": "O", "Ø": "Ö",
        "ū": "û", "ú": "û", "ù": "u", "Ū": "Û", "Ú": "Û", "Ù": "U",
        "ḥ": "h", "Ḥ": "H", "ṭ": "t", "Ṭ": "T", "ṣ": "s", "Ṣ": "S",
        "ḍ": "d", "Ḍ": "D", "ẓ": "z", "Ẓ": "Z", "ğ": "g", "Ğ": "G",
        "ł": "l", "Ł": "L", "ń": "n", "Ń": "N", "þ": "th", "Þ": "Th", "ð": "d", "Ð": "D",
        "ʿ": "", "ʾ": "", "'": "", "ı": "i",
    }
    # Expand Romance de-elision (d'Arcaishon -> de Arcaishon) and fix mid-word CamelCase
    # from stripped apostrophes or Gaelic eclipsis prefixes (N'Echach -> Nechach, Mac nÊan -> Mac Nêan)
    s = re.sub(r"\bd['’](?=[A-ZÀ-ɏ])", "de ", s)
    s = re.sub(r"\b([A-Za-z])'([A-Z]+)", lambda m: m.group(1) + m.group(2).lower(), s)
    s = re.sub(r"\b([NnMm])([AEIOUÂÊÎÔÛ][a-zâêîôû]{2,})", lambda m: m.group(1).upper() + m.group(2).lower(), s)
    s = "".join(char_rep.get(c, c) for c in s)
    s = re.sub(r"(?:ch){2,}", "ch", s, flags=re.I)
    s = re.sub(r"(?:tsch){2,}", "tsch", s, flags=re.I)
    if s and s[0].islower():
        s = s[0].upper() + s[1:]
    return s, notes


def norm_stage4a(s_in: str) -> str:
    """Normalize macrons, acutes, and breathings on Stage 4A decoder outputs."""
    rep = {
        "ā": "â", "Ā": "Â", "á": "â", "Á": "Â",
        "ē": "ê", "Ē": "Ê", "é": "ê", "É": "Ê",
        "ī": "î", "Ī": "Î", "í": "î", "Í": "Î",
        "ō": "ô", "Ō": "Ô", "ó": "ô", "Ó": "Ô",
        "ū": "û", "Ū": "Û", "ú": "û", "Ú": "Û",
        "ʿ": "", "ʾ": "", "'": "",
    }
    res = "".join(rep.get(ch, ch) for ch in s_in)
    return re.sub(r"\b([NnMm])([AEIOUÂÊÎÔÛ][a-zâêîôû]{2,})", lambda m: m.group(1).upper() + m.group(2).lower(), res)


def adapt_stage4a_text(
    txt: str,
    use_prof: str,
    coin_fam: str,
    trans_fam: str,
    inter_map: dict,
    trans_rules: dict,
    wave1_dec: Any = None,
    *,
    kanji_readings: dict | None = None,
    rup: bool = False,
    force_gallo: bool = False,
    source_iso: str | None = None,
) -> str:
    """Adapt a stem via an active Stage 4A historical decoder (with token-level fallback)."""
    if kanji_readings is not None and txt:
        txt = _romanize_embedded_hanzi(txt, kanji_readings, (trans_fam or coin_fam or "").lower())
    active_dec = (
        ("gallo_romance_12c", adapt_gallo_romance_to_tarraconian, adapt_gallo_romance_word)
        if force_gallo
        else wave1_dec
    )
    if active_dec and (
        use_prof != "tarraconian_direct"
        or active_dec[0] in {
            "goidelic_12c", "brythonic_12c", "north_germanic_12c",
            "magyar_12c", "west_slavic_lechitic_12c", "west_slavic_cs_12c",
            "south_slavic_12c", "east_slavic_12c",
            "chinese_12c_phonetic", "korean_12c", "japanese_12c", "vietnamese_12c",
            "turkic_12c", "iranian_12c", "colonial_wrapper_12c",
        }
    ):
        dec_name, phrase_fn, tok_fn = active_dec
        out_str, used_fb = phrase_fn(txt)
        if not used_fb:
            return norm_stage4a(out_str)
        tokens = re.split(r"([\s\-]+)", txt)
        rebuilt: list[str] = []
        for tok in tokens:
            if not tok or re.fullmatch(r"[\s\-]+", tok):
                rebuilt.append(tok)
            elif tok[0].isalpha() or any(ord(c) > 127 for c in tok):
                d_tok = tok_fn(tok)
                if d_tok is not None:
                    rebuilt.append(norm_stage4a(d_tok) if tok[0].isupper() else d_tok)
                else:
                    same_fam_prof = {
                        "gallo_romance_12c": "gallo_romance_to_tarraconian",
                        "italo_romance_12c": "italo_romance_to_tarraconian",
                        "occitano_catalan_12c": "occitano_catalan_to_tarraconian",
                        "ibero_romance_12c": "ibero_romance_to_tarraconian",
                        "eastern_romance_12c": "eastern_romance_to_tarraconian",
                        "goidelic_12c": "celtic_to_tarraconian",
                        "brythonic_12c": "celtic_to_tarraconian",
                        "anglo_saxon_12c": "west_germanic_to_tarraconian",
                        "north_germanic_12c": "north_germanic_to_tarraconian",
                        "magyar_12c": "magyar_to_tarraconian",
                        "west_slavic_lechitic_12c": "west_slavic_to_tarraconian",
                        "west_slavic_cs_12c": "west_slavic_to_tarraconian",
                        "south_slavic_12c": "south_slavic_to_tarraconian",
                        "east_slavic_12c": "east_slavic_to_tarraconian",
                        "chinese_12c_phonetic": "sinosphere_1154_to_tarraconian",
                        "korean_12c": "sinosphere_1154_to_tarraconian",
                        "japanese_12c": "sinosphere_1154_to_tarraconian",
                        "vietnamese_12c": "southeast_asian_to_tarraconian",
                        "turkic_12c": "turkic_to_tarraconian",
                        "iranian_12c": "iranian_to_tarraconian",
                    }.get(dec_name, "")
                    # Keep greek_to_tarraconian for non-Greek loans so -polis->-pel & th->t/ph->f still apply
                    fb_prof = "general_phonetic_adaptation" if (same_fam_prof and use_prof == same_fam_prof) else use_prof
                    fb_tok, _ = transliterate_stem_to_tarr(
                        tok, fb_prof, coin_fam, trans_fam, inter_map, trans_rules,
                        kanji_readings=kanji_readings, is_rupture=rup, source_iso=source_iso,
                    )
                    rebuilt.append(fb_tok)
            else:
                rebuilt.append(tok)
        res_mixed = "".join(rebuilt)
        return res_mixed[:1].upper() + res_mixed[1:] if res_mixed and res_mixed[0].islower() else res_mixed
    res, _ = transliterate_stem_to_tarr(
        txt, use_prof, coin_fam, trans_fam, inter_map, trans_rules,
        kanji_readings=kanji_readings, is_rupture=rup, source_iso=source_iso,
    )
    return res


def calque_hanzi_string(
    hanzi: str,
    kanji_map: dict[str, tuple[str, str, str]],
    *,
    religion_type: str = "",
) -> tuple[str | None, list[str]]:
    """
    Translate a multi-character CJK Hanzi compound character-by-character into Tarraconian
    using the 1,235-char Sinosphere lexicon (`sinosphere_kanji_tarraconian.json` +
    `SINO_BARONY_KANJI_EXT`). Returns `(calqued_str_or_None, gloss_parts)`.
    """
    chars = re.findall(r"[\u3400-\u9FFF\uF900-\uFAFF]", hanzi or "")
    if not chars:
        return None, []
    # Check coverage: calque if at least all chars map cleanly or >= 2-char compound where all except maybe 1 are known
    parts: list[str] = []
    meanings: list[str] = []
    missing = 0
    is_islam = "islam" in (religion_type or "").lower()
    for idx, ch in enumerate(chars):
        if ch in kanji_map:
            m, role, mean = kanji_map[ch]
            clean_m = m.strip("-").strip()
            # Keep Buddhist/Taoist temple char 寺 as -tempel, or -meschit for Chinese Islamic holdings (清真寺)
            if ch == "寺":
                if is_islam:
                    clean_m = "meschit"
                elif clean_m.lower() == "munster":
                    clean_m = "tempel"
            if idx == 0:
                if clean_m.lower() == "bî-dem":
                    clean_m = "Bî-dem-"
                else:
                    clean_m = clean_m[:1].upper() + clean_m[1:]
            else:
                if parts and parts[-1].endswith("-"):
                    clean_m = clean_m[:1].upper() + clean_m[1:].lower()
                else:
                    clean_m = clean_m.lower()
            # Deduplicate tautological double hydro/oronym generics (e.g. Huangflôz + flôz/wazzer, Wâgestein + berch)
            if parts:
                prev_low = parts[-1].lower()
                cur_low = clean_m.lower()
                if cur_low in {"flôz", "wazzer"} and (prev_low.endswith("flôz") or prev_low.endswith("wazzer")):
                    if prev_low in {"flôz", "wazzer"}:
                        # Bare Flôz+flôz or Flôz+wazzer (e.g. 流江 / 河水): reject literal calque -> phonetic reading
                        return None, []
                    continue
                if cur_low in {"berch", "stein"} and (prev_low.endswith("berch") or prev_low.endswith("stein")):
                    if prev_low in {"berch", "stein"}:
                        return None, []
                    continue
            parts.append(clean_m)
            if mean:
                meanings.append(mean.split("/")[0].strip())
        else:
            missing += 1
            break
    if missing > 0 or not parts:
        return None, []
    joined = "".join(parts)
    # Collapse accidental triple consonants at boundaries (e.g. nnn -> nn)
    joined = re.sub(r"([a-z])\1\1+", r"\1\1", joined)
    return joined, meanings


def match_descriptive_audit_calque(
    audit_morphemes: list[dict[str, Any]],
    lex: dict[str, Any],
) -> tuple[str | None, list[str]]:
    """
    Strict check for Procedure 2 full semantic calquing of pre-867 descriptive audit morphemes.
    Requires >= 2 morphemes, zero opaque/proper/uncertain markers, and complete lexicon hit.
    """
    if len(audit_morphemes) < 2:
        return None, []

    gidx = lex["gloss_index"]
    concepts = lex["concepts"]
    stops = set(lex["grammatical_stopwords"])
    opaque_m = set(lex["rule3_opaque_markers"])

    matched_cids: list[str] = []
    for mor in audit_morphemes:
        tr_raw = (mor.get("translation") or "").lower()
        mlang = (mor.get("language") or "").lower()
        if not tr_raw:
            return None, []
        if any(om in tr_raw for om in opaque_m) or "?" in tr_raw or "reinterpreted" in mlang or "folk" in tr_raw or "rabah" in tr_raw:
            return None, []
        # Reject alternate-name/hagiographic parenthetical notes (e.g. "wisdom (Church of St. Sophia)" on b_sredets)
        if re.search(r"\b(?:st\.|church of|named after)\b", tr_raw):
            return None, []
        tr = re.sub(r"\([^)]*\)", "", tr_raw).strip()
        words = re.findall(r"[a-z]+", tr)
        if not words or any(w in DISQUALIFIED_GLOSS_WORDS for w in words):
            return None, []
        # Disambiguate adverbial "well / good" (Latin bene) from noun "well" (water spring -> Brunn-)
        is_adverb_well = ("well" in words and any(w in words for w in ("good", "propitious", "fortunate", "favorable")))
        cid = None
        for w in words:
            if w in stops or (w == "well" and is_adverb_well):
                continue
            if w in gidx:
                cid = gidx[w]
                break
        if cid is None:
            return None, []
        matched_cids.append(cid)

    # Reject tautological double-identical concepts (e.g. Châteaudun = castle + castle -> Burchburch)
    if len(matched_cids) < 2 or len(set(matched_cids)) < len(matched_cids):
        return None, []

    # Build Tarraconian compound: modifier(s) as prefix, final element as suffix
    # Heuristic: in Romance/Arabic/Celtic (head-initial) if first morpheme is a holding/feature noun
    # and last is adjective/color/cardinal (e.g. Algeciras = island + green), swap order in German!
    first_c = concepts[matched_cids[0]]
    last_c = concepts[matched_cids[-1]]
    ordered = list(matched_cids)
    # Adjectives/numbers/colors/materials go BEFORE nouns in Germanic compounds
    adj_categories = {"colors_and_qualities", "numerals", "color", "size_age_quality", "cardinal_direction", "material_resource"}
    if (
        len(ordered) == 2
        and (last_c.get("category") in adj_categories or "quality" in (last_c.get("category") or ""))
        and first_c.get("category") not in adj_categories
    ):
        ordered = [ordered[1], ordered[0]]

    pieces: list[str] = []
    for idx, cid in enumerate(ordered):
        cobj = concepts[cid]
        if idx == 0:
            form = (cobj.get("tarr_prefix") or cobj.get("tarr_standalone") or "").strip("-")
            form = form[:1].upper() + form[1:]
        else:
            form = (cobj.get("tarr_suffix") or cobj.get("tarr_standalone") or "").strip("-").lower()
        if not form:
            return None, []
        pieces.append(form)

    return "".join(pieces), ordered


def run_stage4() -> dict[str, Any]:
    with open(DATA_DIR / "pipeline_stage3_synthesized.json", "r", encoding="utf-8") as f:
        s3 = json.load(f)["baronies"]
    with open(DATA_DIR / "ck3_culture_to_iso_and_generics.json", "r", encoding="utf-8") as f:
        cb = json.load(f)
    cult_bridge = cb["cultures"]
    trans_rules = cb["transmission_rules"]["to_tarraconian"]
    inter_map = {
        (x["source_family"], x["transmission_family"]): x
        for x in cb["transmission_rules"]["historical_intermediaries"]
    }
    with open(DATA_DIR / "multilingual_morpheme_calque_lexicon.json", "r", encoding="utf-8") as f:
        lex = json.load(f)
    with open(DATA_DIR / "sinosphere_kanji_tarraconian.json", "r", encoding="utf-8") as f:
        kanji_list = json.load(f)
    kanji_map: dict[str, tuple[str, str, str]] = {}
    kanji_readings: dict[str, tuple[str, str, str]] = {}
    kanji_map.update(SUPPLEMENTARY_HANZI)
    for ch, val in SINO_BARONY_KANJI_EXT.items():
        if isinstance(val, (tuple, list)) and len(val) >= 3:
            kanji_map[ch] = (val[0], val[1], val[2])
    for item in kanji_list:
        ch = item.get("char")
        if ch:
            kanji_map[ch] = (
                item.get("tarr_morpheme") or "",
                item.get("tarr_role") or "",
                item.get("meaning") or "",
            )
            kanji_readings[ch] = (
                item.get("pinyin_sort") or item.get("pinyin") or "",
                item.get("kr") or "",
                item.get("jp") or "",
            )
            if item.get("var") and item["var"] != "-":
                for vch in item["var"].split("/"):
                    vch = vch.strip()
                    if vch:
                        kanji_map.setdefault(vch, kanji_map[ch])
                        kanji_readings.setdefault(vch, kanji_readings[ch])

    with open(DATA_DIR / "barony_resolutions.json", "r", encoding="utf-8") as f:
        v1_res = json.load(f)
    with open(DATA_DIR / "barony_coinage_rulers.json", "r", encoding="utf-8") as f:
        coinage_rulers = json.load(f)["baronies"]

    calque_mode_counts: Counter[str] = Counter()
    historical_phonology_counts: Counter[str] = Counter()
    rule3_blocked_count = 0
    intermediary_applied_count = 0
    stage4_baronies: dict[str, dict[str, Any]] = {}

    for bk in sorted(s3.keys()):
        r3 = s3[bk]
        if not r3["is_occupied"]:
            stage4_baronies[bk] = {
                "barony_key": bk,
                "is_occupied": False,
                "final_record": r3["final_record"],
            }
            continue

        cs = r3["continuity_status"]
        coin_fam = r3["coinage_morphology_family"]
        trans_cult = r3["transmission_culture"]
        trans_info = cult_bridge.get(trans_cult) or {}
        trans_fam = trans_info.get("morphology_family") or coin_fam
        trans_prof = r3["transmission_profile"] or "general_phonetic_adaptation"

        is_sino = bool(r3["is_sinosphere_scope"])
        is_direct_trans = (cs == "Direct Transparency") or (r3["coinage_culture"] in {"Tarraconian", "Lothringian", "Croato-Tarraconian", "Alpine-Tarraconian", "Ungwârer"})
        is_transitional = cs == "Transitional Mediation (< 50y)" and not is_direct_trans
        is_rupture = cs == "Semantic Rupture (>= 50y)" and not is_direct_trans

        is_true_latin = is_true_latin_stem(r3)
        is_gallo_stem = is_gallo_romance_stem(r3, trans_fam)
        has_intermediary = (coin_fam, trans_fam) in inter_map
        wave1_dec = resolve_wave1_decoder(r3, trans_fam)
        # Do not short-circuit Greek multi-hop intermediaries (greek_to_turkish / greek_to_south_slavic / greek_to_arabic)
        if wave1_dec and wave1_dec[0] == "byzantine_greek_12c" and has_intermediary and is_rupture:
            wave1_dec = None
        dec_id = (
            "latin_classical"
            if is_true_latin
            else (wave1_dec[0] if wave1_dec else "default_transmission")
        )
        coined_form = r3["coined_source_form"]
        mod = r3["coined_modifier"]
        gen = r3["coined_generic"]

        # Always compute direct phonological adaptation of the Stage 3 form
        # Do not run Magyar/Slavic transmission substitutions onto compounds already coined in Imperial German
        eff_trans_prof = (
            "tarraconian_direct"
            if (
                (r3["coinage_culture"] in TARRACONIAN_DIRECT_CULTURES and not is_gallo_stem)
                or (r3.get("selected_iso") in {"deu", "gmh", "goh"} and trans_prof == "magyar_to_tarraconian")
            )
            else trans_prof
        )

        def _strip_eng_meta(s: str) -> str:
            meta_words = ENGLISH_META_GEO_WORDS | {"montes", "portus"}
            if not any(w.lower() in meta_words for w in s.split()):
                return s
            ws = [w for w in s.split() if w.lower() != "of" and not (w.lower() == "de" and s.lower().startswith(("montes ", "monts ")))]
            if len(ws) >= 2:
                if ws[-1].lower() in TRANSPARENT_NTR_HEADS:
                    hsuf, _ = TRANSPARENT_NTR_HEADS[ws[-1].lower()]
                    return f"{' '.join(ws[:-1])}{hsuf.strip('-')}"
                if ws[0].lower() in TRANSPARENT_NTR_HEADS:
                    hsuf, _ = TRANSPARENT_NTR_HEADS[ws[0].lower()]
                    rest = " ".join(ws[1:])
                    return f"{hsuf}{rest}" if hsuf.endswith("-") else f"{rest}{hsuf.strip('-')}"
            return s

        def adapt(txt: str, prof: str | None = None, rup: bool = False, force_gallo: bool = False) -> str:
            return adapt_stage4a_text(
                txt,
                prof or eff_trans_prof,
                coin_fam,
                trans_fam,
                inter_map,
                trans_rules,
                wave1_dec,
                kanji_readings=kanji_readings,
                rup=rup,
                force_gallo=force_gallo,
                source_iso=r3.get("selected_iso"),
            )

        if is_true_latin:
            inter_notes = []
            if r3["stage3_mode"] == "passthrough_stage2_stem" or gen is None:
                tarr_direct = adapt_latin_to_tarraconian(coined_form, suppress_geo_head=False)
            elif r3["stage3_mode"] not in {"synthesized_pious_saint", "synthesized_vain_eponym"} and not mod.get("tarr_equivalent"):
                mod_lat_dir = adapt_latin_to_tarraconian(mod["text"], suppress_geo_head=(gen["affix_position"] == "suffix" or gen["tarr_calque"].startswith("Castel-")))
                g_nat_dir = gen["native_form"]
                g_is_fr = (coin_fam == "gallo_romance")
                if gen["affix_position"] == "prefix":
                    sep = "" if g_nat_dir.endswith("-") else (gen.get("joiner") or " ")
                    g_part = adapt(g_nat_dir.strip(), eff_trans_prof, rup=is_rupture, force_gallo=g_is_fr)
                    tarr_direct = f"{g_part}{sep}{mod_lat_dir}"
                else:
                    g_part = adapt(g_nat_dir.lstrip("-"), eff_trans_prof, rup=is_rupture, force_gallo=g_is_fr).lower()
                    tarr_direct = f"{mod_lat_dir}{g_part}"
            else:
                if coin_fam == "gallo_romance" and gen and r3["stage3_mode"] in {"synthesized_pious_saint", "synthesized_vain_eponym"}:
                    g_nat_dir = gen["native_form"]
                    mod_s3 = mod.get("tarr_equivalent") or mod["text"]
                    if gen["affix_position"] == "prefix":
                        sep = "" if g_nat_dir.endswith("-") else (gen.get("joiner") or " ")
                        g_part = adapt(g_nat_dir.strip(), eff_trans_prof, rup=is_rupture, force_gallo=True)
                        tarr_direct = f"{g_part}{sep}{mod_s3}"
                    else:
                        g_part = adapt(g_nat_dir.lstrip("-"), eff_trans_prof, rup=is_rupture, force_gallo=True).lower()
                        tarr_direct = f"{mod_s3}{g_part}"
                else:
                    tarr_direct, inter_notes = transliterate_stem_to_tarr(
                        coined_form, eff_trans_prof, coin_fam, trans_fam, inter_map, trans_rules,
                        kanji_readings=kanji_readings, is_rupture=is_rupture,
                        source_iso=r3.get("selected_iso"),
                    )
        elif wave1_dec:
            inter_notes = []
            tarr_direct = adapt(coined_form, eff_trans_prof, rup=is_rupture)
        else:
            tarr_direct, inter_notes = transliterate_stem_to_tarr(
                coined_form, eff_trans_prof, coin_fam, trans_fam, inter_map, trans_rules,
                kanji_readings=kanji_readings, is_rupture=is_rupture,
                source_iso=r3.get("selected_iso"),
            )

        tarr_direct = _strip_eng_meta(tarr_direct)

        # Pre-867 Track S: supplement Hanzi from verified v1 Sinosphere entry ONLY when pre-867 attested & not saint/eponym!
        is_s3_named_eponym = r3.get("stage3_mode") in {"synthesized_pious_saint", "synthesized_vain_eponym"}
        hanzi_str = r3.get("coined_hanzi")
        if is_sino and not hanzi_str and r3["is_historical_867"] and not is_s3_named_eponym:
            v1_hz = (v1_res.get(bk) or {}).get("b_hanzi") or ""
            if v1_hz and r3["stem_category"] != "tribe":
                hanzi_str = v1_hz

        tarr_hist = ""
        calque_mode = ""
        calque_concepts: list[str] = []
        pathway = ""

        # --- BRANCH A: Track S (Sinosphere Procedure 1 + 12th-century Phonetics) ---
        if coined_form.strip().lower() == "monastery of the transfiguration":
            tarr_hist = "Verclêrungeclôster"
            tarr_direct = "Verclêrungeclôster"
            calque_mode = "full_semantic_calque"
            calque_concepts = ["transfiguration", "monastery"]
            pathway = f"{coined_form} -> [Direct Chancellery Calque: transfiguration + monastery] -> {tarr_hist}"
        elif is_sino:
            NO_LITERAL_HANZI_CALQUE = {"b_iyo", "b_kinasir", "b_xi"}
            ATEJI_PHONETIC_SUBSTRINGS = (
                "興安", "兴安", "祁連", "祁连", "烏蘇里", "乌苏里",
                "穆稜", "穆棱", "貝爾", "贝尔", "粟末", "完達", "完达",
                "張廣才", "张广才", "賀蘭", "贺兰", "沙魯里", "沙鲁里",
                "率賓", "率宾", "夜郎", "雅魯藏布", "雅鲁藏布",
            )
            is_ateji_phonetic = bool(hanzi_str and any(sub in hanzi_str for sub in ATEJI_PHONETIC_SUBSTRINGS))
            has_ateji_morpheme = (
                r3.get("stage3_mode") == "passthrough_stage2_stem"
                and any(
                    re.search(r"\b(?:ateji|phonetic)\b", (m.get("translation") or "").lower())
                    for m in (r3.get("audit_morphemes") or [])
                )
            )
            opaque_sino = (
                r3["is_opaque_proper_stem"]
                or is_s3_named_eponym
                or (r3["stem_category"] == "tribe")
                or (bk in NO_LITERAL_HANZI_CALQUE)
                or is_ateji_phonetic
                or has_ateji_morpheme
            )
            hz_count = len(re.findall(r"[\u3400-\u9FFF\uF900-\uFAFF]", hanzi_str or ""))
            rel_type = (coinage_rulers.get(bk) or {}).get("religion_type") or ""
            if hanzi_str and hz_count >= 2 and not opaque_sino and not is_rupture:
                calqued_hz, hz_meanings = calque_hanzi_string(hanzi_str, kanji_map, religion_type=rel_type)
                if calqued_hz and len(calqued_hz) >= 3:
                    tarr_hist = calqued_hz
                    calque_mode = "sinosphere_procedure1_calque"
                    calque_concepts = hz_meanings
                    pathway = f"{coined_form} ({hanzi_str}) -> [Procedure 1 CJK Calque: {' + '.join(hz_meanings)}] -> {tarr_hist}"
            if not tarr_hist:
                # Transitional or opaque/post-867 synthesized Sinosphere: adapt modifier + calque generic if transparent & not rupture
                if gen and not is_rupture:
                    raw_teq = mod.get("tarr_equivalent") if is_s3_named_eponym else None
                    if raw_teq and raw_teq == mod.get("text") and wave1_dec and wave1_dec[0] in {"chinese_12c_phonetic", "korean_12c"}:
                        mod_adapt = adapt(raw_teq, trans_prof)
                    else:
                        mod_adapt = raw_teq or adapt(mod["text"], trans_prof)
                    tc_raw = gen.get("tarr_calque", "")
                    g_tarr = tc_raw.strip("-")
                    if tc_raw.startswith("Zant") or tc_raw.endswith("-"):
                        tarr_hist = f"{tc_raw}{mod_adapt}"
                    else:
                        tarr_hist = f"{mod_adapt}{g_tarr}"
                    calque_mode = "sinosphere_hybrid_generic_calque" if mod.get("is_opaque_eponym") else "sinosphere_12c_phonetic"
                    pathway = f"{coined_form} ({hanzi_str or '12c phonetic'}) -> [{trans_prof}] -> {tarr_hist}"
                else:
                    tarr_hist = tarr_direct
                    calque_mode = "semantic_rupture_phonetic" if is_rupture else "sinosphere_12c_phonetic"
                    pathway = f"{coined_form} -> [{calque_mode}: {trans_prof}] -> {tarr_hist}"

        # --- BRANCH B: Rule 4 Semantic Rupture (>= 50y) ---
        elif is_rupture:
            # Strict phonetic mediation through transmission_culture (no semantic calquing, single-pass)
            if mod.get("is_opaque_eponym") and r3["stage3_mode"] in {"synthesized_vain_eponym", "synthesized_pious_saint"}:
                mod_src = mod["tarr_equivalent"] or mod["text"]
                if gen:
                    g_nat = gen["native_form"]
                    g_is_fr = (coin_fam == "gallo_romance")
                    if gen["affix_position"] == "prefix":
                        sep = "" if g_nat.endswith("-") else (gen.get("joiner") or " ")
                        raw_g = adapt(g_nat.strip(), trans_prof, rup=True, force_gallo=g_is_fr) if g_is_fr else None
                        if raw_g is not None:
                            tarr_hist = f"{raw_g}{sep}{mod_src}"
                        else:
                            raw_part = f"{g_nat.strip()}{sep}{mod_src}"
                            tarr_hist = adapt(raw_part, trans_prof, rup=True)
                    else:
                        raw_g = adapt(g_nat.lstrip("-"), trans_prof, rup=True, force_gallo=g_is_fr).lower() if g_is_fr else None
                        if raw_g is not None:
                            tarr_hist = f"{mod_src}{raw_g}"
                        else:
                            raw_part = f"{mod_src}{g_nat.lstrip('-')}"
                            tarr_hist = adapt(raw_part, trans_prof, rup=True)
                else:
                    tarr_hist = adapt(mod_src, trans_prof, rup=True)
            elif is_true_latin:
                if r3["stage3_mode"] == "passthrough_stage2_stem" or gen is None:
                    tarr_hist = adapt_latin_to_tarraconian(coined_form, suppress_geo_head=False)
                else:
                    mod_src_text = mod["text"]
                    mod_lat = adapt_latin_to_tarraconian(mod_src_text, suppress_geo_head=(gen["affix_position"] == "suffix" or gen["tarr_calque"].startswith("Castel-")))
                    g_nat = gen["native_form"]
                    g_is_fr = (coin_fam == "gallo_romance")
                    if gen["affix_position"] == "prefix":
                        sep = "" if g_nat.endswith("-") else (gen.get("joiner") or " ")
                        g_part = adapt(g_nat.strip(), trans_prof, rup=True, force_gallo=g_is_fr)
                        tarr_hist = f"{g_part}{sep}{mod_lat}"
                    else:
                        g_part = adapt(g_nat.lstrip("-"), trans_prof, rup=True, force_gallo=g_is_fr).lower()
                        tarr_hist = f"{mod_lat}{g_part}"
            else:
                tarr_hist = tarr_direct
            calque_mode = "semantic_rupture_phonetic"
            pathway = f"{coined_form} ({r3['coinage_culture']}) -> [Rupture >=50y via {trans_cult} ({', '.join(inter_notes) or trans_prof})] -> {tarr_hist}"

        # --- BRANCH C: Synthesized Stage 3 Compounds (Direct Transparency or Transitional < 50y) ---
        elif r3["stage3_mode"] != "passthrough_stage2_stem" and gen is not None:
            g_calque = gen["tarr_calque"]
            g_clean = g_calque.strip("-")
            mod_text = mod["text"]

            # Case C1: Opaque personal/saint/tribal modifier -> Exception: adapt modifier + calque generic
            if mod.get("is_opaque_eponym"):
                rule3_blocked_count += 1
                mod_tarr = mod.get("tarr_equivalent")
                if mod_tarr and wave1_dec:
                    if wave1_dec[0] == "brythonic_12c":
                        mod_tarr = re.sub(r"\bRh", "R", mod_tarr)
                    elif wave1_dec[0] == "north_germanic_12c":
                        mod_tarr = re.sub(r"([bcdfghjklmnpqrstvwxz])rs\b", r"\1s", mod_tarr)
                    elif wave1_dec[0] == "east_slavic_12c" and mod_tarr == "Euphrosyne":
                        mod_tarr = "Eufrosyne"
                    elif wave1_dec[0] == "west_slavic_lechitic_12c" and mod_tarr.endswith("wic"):
                        mod_tarr = mod_tarr[:-1] + "tz"
                if not mod_tarr:
                    mod_tarr = adapt_latin_to_tarraconian(mod_text, suppress_geo_head=True) if is_true_latin else adapt(mod_text, eff_trans_prof)
                if g_calque.startswith("Zant-"):
                    tarr_hist = f"Zant-{mod_tarr}"
                elif g_calque.endswith("-"):
                    tarr_hist = f"{g_calque}{mod_tarr}"
                elif g_calque.startswith("Castel-"):
                    tarr_hist = f"{mod_tarr}burch"
                else:
                    tarr_hist = f"{mod_tarr}{g_clean}"
                calque_mode = "hybrid_generic_calque"
                pathway = f"{coined_form} -> [Rule 3 Proper Stem + Calqued Generic '{g_calque}'] -> {tarr_hist}"

            # Case C2: Transparent abstract Stage 3 modifier (shield, market, toll, holy, battle)
            elif mod.get("tarr_equivalent"):
                t_mod = mod["tarr_equivalent"]
                if is_direct_trans:
                    if g_calque.startswith("Zant-"):
                        tarr_hist = f"Zant-{t_mod}"
                    elif g_calque.endswith("-"):
                        tarr_hist = f"{g_calque}{t_mod}"
                    elif g_calque.startswith("Castel-"):
                        tarr_hist = f"Castel-{t_mod}"
                    else:
                        tarr_hist = f"{t_mod}{g_clean}"
                    calque_mode = "full_semantic_calque"
                    calque_concepts = [mod.get("semantic_concept", ""), gen.get("gloss", "")]
                    pathway = f"{coined_form} -> [Direct Transparency Full Calque: {t_mod} + {g_calque}] -> {tarr_hist}"
                else:
                    # Transitional (<50y): keep adapted modifier, calque generic
                    mod_ad = adapt_latin_to_tarraconian(mod_text, suppress_geo_head=True) if is_true_latin else adapt(mod_text, eff_trans_prof)
                    tarr_hist = f"{mod_ad}{g_clean}" if not g_calque.endswith("-") else f"{g_calque}{mod_ad}"
                    calque_mode = "hybrid_generic_calque"
                    pathway = f"{coined_form} -> [Transitional <50y Hybrid: {mod_ad} + {g_calque}] -> {tarr_hist}"

            # Case C3: NTR landscape stem + holding generic
            elif is_true_latin:
                mod_ad = adapt_latin_to_tarraconian(mod_text, suppress_geo_head=True)
                if g_calque.startswith("Castel-"):
                    tarr_hist = f"Castel-{mod_ad}"
                elif g_calque.endswith("-"):
                    tarr_hist = f"{g_calque}{mod_ad}"
                else:
                    tarr_hist = f"{mod_ad}{g_clean}"
                calque_mode = "hybrid_generic_calque"
                pathway = f"{coined_form} (Latin) -> [Latin Hybrid Calque: {mod_ad} + {g_calque}] -> {tarr_hist}"
            else:
                words = mod_text.split()
                head_calq = TRANSPARENT_NTR_HEADS.get(words[0].lower()) if len(words) >= 2 else None
                if is_direct_trans and head_calq:
                    rest_stem = " ".join(words[1:])
                    rest_ad = adapt(rest_stem)
                    tarr_hist = f"{rest_ad}{g_clean}"
                    calque_mode = "hybrid_generic_calque"
                    calque_concepts = [head_calq[1], gen.get("gloss", "")]
                    pathway = f"{coined_form} -> [Direct NTR Head '{words[0]}' + {g_calque}] -> {tarr_hist}"
                elif is_direct_trans and len(words) >= 2 and words[-1].lower() in TRANSPARENT_NTR_HEADS:
                    rest_stem = " ".join(words[:-1])
                    tail_calq = TRANSPARENT_NTR_HEADS[words[-1].lower()]
                    rest_ad = adapt(rest_stem)
                    tarr_hist = f"{rest_ad}{g_clean}"
                    calque_mode = "hybrid_generic_calque"
                    calque_concepts = [tail_calq[1], gen.get("gloss", "")]
                    pathway = f"{coined_form} -> [Direct NTR Tail '{words[-1]}' + {g_calque}] -> {tarr_hist}"
                else:
                    mod_ad = adapt(mod_text)
                    if g_calque.startswith("Castel-"):
                        tarr_hist = f"Castel-{mod_ad}"
                    elif g_calque.endswith("-"):
                        tarr_hist = f"{g_calque}{mod_ad}"
                    else:
                        tarr_hist = f"{mod_ad}{g_clean}"
                    calque_mode = "hybrid_generic_calque"
                    pathway = f"{coined_form} -> [Hybrid Generic Calque: {mod_ad} + {g_calque}] -> {tarr_hist}"

        # --- BRANCH D: Passthrough Pre-867 Attested or NTR/Natural Restitution (no generic appended) ---
        else:
            # Guard: only inspect audit_morphemes when stem_source actually derives from audited name
            # and contains no ethnonymic/tribal root (e.g. preserve Canterbury rather than reducing it to 'Volcburch')!
            audit_ms = r3.get("audit_morphemes") or []
            has_ethnonym_morpheme = any(
                any(w in (m.get("translation") or "").lower() for w in ("people", "tribe", "folk", "king", "ethnic"))
                or (m.get("form") or "").lower() in {"cantwara"}
                for m in audit_ms if isinstance(m, dict)
            )
            can_calque_audit = (
                is_direct_trans
                and not r3["is_opaque_proper_stem"]
                and not has_ethnonym_morpheme
                and r3["stem_source"] in {"pre867_attested_vanilla", "existing_natural_proper_name"}
            )
            desc_calque, matched_cids = (
                match_descriptive_audit_calque(audit_ms, lex)
                if can_calque_audit
                else (None, [])
            )
            if desc_calque and not (" " not in coined_form and any(cid == "people_folk" for cid in matched_cids)):
                tarr_hist = desc_calque
                calque_mode = "full_semantic_calque"
                calque_concepts = matched_cids
                pathway = f"{coined_form} -> [Direct Transparency Audit Calque: {' + '.join(matched_cids)}] -> {tarr_hist}"
            elif is_true_latin:
                tarr_hist = adapt_latin_to_tarraconian(coined_form, suppress_geo_head=False)
                is_lat_calque = coined_form.lower() in LATIN_CURATED_PHRASES and " " in coined_form
                calque_mode = "hybrid_generic_calque" if is_lat_calque else "phonetic_mediation_direct"
                pathway = f"{coined_form} (Latin) -> [Latin-to-Tarraconian] -> {tarr_hist}"
            else:
                if r3["is_opaque_proper_stem"]:
                    rule3_blocked_count += 1
                words = [w for w in coined_form.replace(".", "").split() if w.lower() != "of" and not (w.lower() == "de" and coined_form.lower().startswith(("montes ", "monts ")))]
                head_w = words[0].lower() if len(words) >= 2 else ""
                tail_w = words[-1].lower() if len(words) >= 2 else ""
                meta_words = ENGLISH_META_GEO_WORDS | {"montes", "portus"}
                head_is_eng_meta = head_w in meta_words
                tail_is_eng_meta = tail_w in meta_words
                if (is_direct_trans or head_is_eng_meta) and len(words) >= 2 and head_w in TRANSPARENT_NTR_HEADS:
                    hsuf, hgl = TRANSPARENT_NTR_HEADS[head_w]
                    rest_ad = adapt(" ".join(words[1:]))
                    tarr_hist = f"{hsuf}{rest_ad}" if hsuf.endswith("-") else f"{rest_ad}{hsuf.strip('-')}"
                    calque_mode = "hybrid_generic_calque"
                    calque_concepts = [hgl]
                    pathway = f"{coined_form} -> [Direct Transparency Head '{words[0]}' -> '{hsuf}'] -> {tarr_hist}"
                elif (is_direct_trans or tail_is_eng_meta) and len(words) >= 2 and tail_w in TRANSPARENT_NTR_HEADS:
                    hsuf, hgl = TRANSPARENT_NTR_HEADS[tail_w]
                    rest_ad = adapt(" ".join(words[:-1]))
                    tarr_hist = f"{hsuf}{rest_ad}" if hsuf.endswith("-") else f"{rest_ad}{hsuf.strip('-')}"
                    calque_mode = "hybrid_generic_calque"
                    calque_concepts = [hgl]
                    pathway = f"{coined_form} -> [Direct Transparency Tail '{words[-1]}' -> '{hsuf}'] -> {tarr_hist}"
                else:
                    # Guard against non-Sinosphere standalone cardinal calque like 'West' replacing 'Xi'
                    tarr_hist = tarr_direct
                    calque_mode = "phonetic_mediation_direct"
                    pathway = f"{coined_form} ({r3['coinage_culture']}) -> [Phonetic Mediation: {eff_trans_prof}] -> {tarr_hist}"

        tarr_hist = _strip_eng_meta(tarr_hist)

        if inter_notes:
            intermediary_applied_count += 1
        calque_mode_counts[calque_mode] += 1
        historical_phonology_counts[dec_id] += 1

        stage4_baronies[bk] = {
            **r3,
            "tarr_direct_pre_law": tarr_direct,
            "tarr_hist_pre_law": tarr_hist,
            "coined_hanzi": hanzi_str,
            "calque_mode": calque_mode,
            "calque_concepts": calque_concepts,
            "historical_phonology_decoder": dec_id,
            "intermediary_shifts_applied": inter_notes,
            "phonological_pathway": pathway,
        }

    payload = {
        "metadata": {
            "schema_version": "1.0.0",
            "pipeline_stage": "stage_4_calquing_and_phonological_mediation",
            "total_baronies": len(stage4_baronies),
            "occupied_baronies": sum(calque_mode_counts.values()),
            "unoccupied_baronies": len(stage4_baronies) - sum(calque_mode_counts.values()),
            "calque_mode_counts": dict(calque_mode_counts),
            "historical_phonology_counts": dict(historical_phonology_counts),
            "rule3_opaque_calque_blocks": rule3_blocked_count,
            "intermediary_shift_applications": intermediary_applied_count,
        },
        "baronies": stage4_baronies,
    }
    return payload


def main() -> None:
    payload = run_stage4()
    out_path = DATA_DIR / "pipeline_stage4_mediated.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    print(f"Wrote {out_path} ({out_path.stat().st_size / (1024*1024):.2f} MB)")
    print("Stage 4 metadata:", json.dumps(payload["metadata"], indent=2))


if __name__ == "__main__":
    main()

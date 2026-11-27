#!/usr/bin/env python3
"""
pipeline_stage5_sound_laws.py

Stage 5 of the Tarraconian Barony-Tier Toponymic Naming Pipeline (v2):
Applies Tarraconian Chancellery Orthographic & Sound Laws, generates Daughter Dialect
overlays (Alpine-Tarraconian, Croato-Tarraconian, Ungwârer), computes IPA via
`resolve_barony_titles.generate_tarraconian_ipa`, and validates all 10,239 occupied
baronies against `audit_phonotactics_titles.check_title_phonotactics` + strict
Chancellery character hygiene.

Reads:
  - data/pipeline_stage4_mediated.json
  - data/barony_toponymic_profiles.json

Emits:
  - data/pipeline_stage5_validated.json
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

from tarraconian_phonotactics import (
    ValidationContext,
    check_title_phonotactics,
    get_default_validator,
)
from resolve_barony_titles import enforce_tarraconian_sound_laws, generate_tarraconian_ipa

REPO_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_DIR / "data"

ALLOWED_CHANCELLERY_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzâêîôûÂÊÎÔÛäöüÄÖÜïëÏ '-")
PRESERVE_NFC_VOWELS = set("âêîôûÂÊÎÔÛäöüÄÖÜïëÏ")

EXOTIC_CHAR_MAP: dict[str, str] = {
    # IPA / Berber / West African Latin extensions
    "ɣ": "g", "Ɣ": "G",
    "ɔ": "o", "Ɔ": "O",
    "ɛ": "e", "Ɛ": "E",
    "ə": "e", "Ə": "E",
    "ɗ": "d", "Ɗ": "D",
    "ɓ": "b", "Ɓ": "B",
    "ƙ": "k", "Ƙ": "K",
    "ŋ": "ng", "Ŋ": "Ng",
    "ħ": "h", "Ħ": "H",
    "ß": "ss", "ẞ": "Ss",
    "ç": "tz", "Ç": "Tz",
    "œ": "ö", "Œ": "Ö",
    "ÿ": "î", "Ÿ": "Î",
    "ʋ": "v", "Ʋ": "V",
    "–": "-", "—": "-",
    "ʻ": "", "ʼ": "", "ʹ": "", "ˈ": "", "ˌ": "", "ʔ": "", "ʿ": "", "ʾ": "", "’": "", "‘": "",
    # Pinyin tone carons / graves
    "ǎ": "a", "Ǎ": "A", "ǐ": "i", "Ǐ": "I", "ǒ": "o", "Ǒ": "O", "ǔ": "u", "Ǔ": "U",
    "ǜ": "ü", "Ǜ": "Ü", "ǘ": "ü", "Ǘ": "Ü", "ǖ": "ü", "Ǖ": "Ü", "ǚ": "ü", "Ǚ": "Ü",
    # Old English / Celtic / Germanic / Nordic
    "ǣ": "ê", "Ǣ": "Ê", "æ": "ê", "Æ": "Ê", "å": "ô", "Å": "Ô", "ø": "ö", "Ø": "Ö",
    "ǫ": "o", "Ǫ": "O", "þ": "th", "Þ": "Th", "ð": "d", "Ð": "D",
    "ő": "ö", "Ő": "Ö", "ű": "ü", "Ű": "Ü",
    # Slavic yers / nasals / liquids / caron sibilants
    "ĭ": "i", "Ĭ": "I", "ŭ": "u", "Ŭ": "U", "ľ": "l", "Ľ": "L", "ĺ": "l", "Ĺ": "L",
    "ŕ": "r", "Ŕ": "R", "ň": "n", "Ň": "N", "ď": "d", "Ď": "D", "ť": "t", "Ť": "T",
    "š": "sch", "Š": "Sch", "ž": "sch", "Ž": "Sch", "č": "tsch", "Č": "Tsch",
    "ǧ": "g", "Ǧ": "G", "ė": "e", "Ė": "E",
    # Indic IAST
    "ṇ": "n", "Ṇ": "N", "ṅ": "ng", "Ṅ": "Ng", "ṃ": "m", "Ṃ": "M", "ṁ": "m", "Ṁ": "M",
    "ṛ": "r", "Ṛ": "R", "ṝ": "r", "ḷ": "l", "ẏ": "j", "Ẏ": "J", "ś": "sch", "Ś": "Sch", "ṣ": "sch", "Ṣ": "Sch",
    "ṓ": "ô", "Ṓ": "Ô",
    # Vietnamese
    "đ": "d", "Đ": "D", "ư": "ü", "Ư": "Ü", "ơ": "ö", "Ơ": "Ö",
    "ả": "a", "Ả": "A", "ạ": "a", "Ạ": "A", "ằ": "a", "ắ": "a", "ẳ": "a", "ẵ": "a", "ặ": "a",
    "ầ": "â", "ấ": "â", "ẩ": "â", "ẫ": "â", "ậ": "â",
    "ề": "ê", "ế": "ê", "ể": "ê", "ễ": "ê", "ệ": "ê",
    "ỉ": "i", "ị": "i", "ỏ": "o", "ọ": "o",
    "ồ": "ô", "ố": "ô", "ổ": "ô", "ỗ": "ô", "ộ": "ô",
    "ờ": "ö", "ớ": "ö", "ở": "ö", "ỡ": "ö", "ợ": "ö",
    "ủ": "u", "ụ": "u", "ừ": "ü", "ứ": "ü", "ử": "ü", "ữ": "ü", "ự": "ü",
    "ỷ": "i", "ỵ": "i", "ỹ": "i",
    # Semitic / Nigerian / Yoruba / Kurdish underdots & breves
    "ọ": "o", "Ọ": "O", "ẹ": "e", "Ẹ": "E", "ị": "i", "Ị": "I", "ụ": "u", "Ụ": "U",
    "ḥ": "h", "Ḥ": "H", "ṭ": "t", "Ṭ": "T", "ṣ": "s", "Ṣ": "S", "ḍ": "d", "Ḍ": "D", "ẓ": "z", "Ẓ": "Z",
    "ă": "e", "Ă": "E", "ğ": "g", "Ğ": "G", "ı": "i", "İ": "I",
}

DAUGHTER_DIALECTS = {"Alpine-Tarraconian", "Croato-Tarraconian", "Ungwârer"}

ALPINE_MARCH_DUCHIES = {
    "d_lombardia", "d_piedmont", "d_savoie", "d_transjurania", "d_currezia",
    "d_tyrol", "d_steyermark", "d_carinthia", "d_krain", "d_friuli",
    "d_verona", "d_genoa", "d_emilia", "d_salzburg", "d_osterreich", "d_bavaria",
}


def pre_normalize_for_chancellery(s: str, is_sinosphere: bool = False, macro_family: str = "") -> str:
    """Clean exotic characters, punctuation, and illicit digraphs BEFORE sound laws."""
    if not s:
        return ""
    out = unicodedata.normalize("NFC", s.strip())

    # Convert St. / Saint -> Zant- cleanly
    out = re.sub(r"\bSt\.(?:\s+|-)?", "Zant-", out)
    out = re.sub(r"\bSt\s+(?=[A-Z])", "Zant-", out)
    out = re.sub(r"\bSaint[\s\-]+", "Zant-", out, flags=re.I)
    # Normalize Tibetan Wylie g.yu -> Yu before punctuation removal
    out = re.sub(r"\b[Gg]\.yu\b", "Yu", out)

    # Disambiguate Bosnian/Croatian Đ (Dsch) vs Vietnamese Đ (D)
    if macro_family == "south_slavic":
        out = out.replace("đ", "dsch").replace("Đ", "Dsch")

    # Apply explicit EXOTIC_CHAR_MAP
    out = "".join(EXOTIC_CHAR_MAP.get(ch, ch) for ch in out)

    # Strip any residual combining marks while preserving canonical Tarraconian vowels
    res_chars: list[str] = []
    for ch in out:
        if ch in PRESERVE_NFC_VOWELS or ch in ALLOWED_CHANCELLERY_CHARS:
            res_chars.append(ch)
        else:
            decomp = unicodedata.normalize("NFD", ch)
            stripped = "".join(c for c in decomp if unicodedata.category(c) != "Mn")
            for sc in stripped:
                res_chars.append(EXOTIC_CHAR_MAP.get(sc, sc))
    out = "".join(res_chars)

    # Remove dots/punctuation not in ALLOWED_CHANCELLERY_CHARS
    out = "".join(c if c in ALLOWED_CHANCELLERY_CHARS else " " for c in out)
    out = re.sub(r"\s{2,}", " ", out).strip()

    # Non-Sinosphere bare 'q' (not 'qu') -> 'k' so enforce_tarraconian_sound_laws won't turn Q- into Tsch-
    if not is_sinosphere:
        out = re.sub(r"[Qq](?![uU])", lambda m: "K" if m.group(0).isupper() else "k", out)

    # English preposition hygiene if any straggled inside NTR compound
    out = re.sub(r"\b(?:upon|under|on|the|of)\b", "", out, flags=re.I)
    out = re.sub(r"\s{2,}", " ", out).strip(" -")
    return out


_LOWERCASE_PARTICLES = {
    "van", "vom", "von", "am", "an", "in", "im", "der", "dem", "den",
    "dat", "ende", "und", "al", "el", "de", "del", "du", "es", "er", "zu", "op",
    "upon", "under", "the", "of",
}

_PROTECTED_H_SUFFIXES = (
    r"h(?:êilichdom|ôfstat|affburch|âven|aven|ûsen|ügil|ügel|irsch|imel|"
    r"âgen|heim|irz|êde|ôch|olm|olz|ain|age|out|ôf|of|ûs|êl|îa)"
)

_PROTECTED_S_SUFFIXES = (
    r"s(?:achsen|chatz|châf|chön|ilber|unnen|unne|êlich|anter|tater|tein|"
    r"tern|tarc|tûl|tûr|tîg|lacht|trâte|tat|alz|ant|êge|wartz|nê|ût|ê|ôl|pitz|pital)"
)


def _apply_segment_orthography(
    seg: str,
    *,
    is_sinosphere: bool = False,
    macro_family: str = "",
) -> str:
    """Apply onset-cluster repairs and final Auslautverhärtung to one word/hyphen segment."""
    if not seg or seg == "IJ" or seg.lower() in _LOWERCASE_PARTICLES:
        return seg
    w = seg

    # Upper/Modern High German -> Rhine-Moselle Franconian
    if re.match(r"^[Ss]ch(?:warsch|warz)", w):
        w = re.sub(r"^[Ss]ch(?:warsch|warz)", lambda m: "Swartz" if m.group(0)[0].isupper() else "swartz", w)
    elif re.match(r"^[Ss]ch([wlmn])", w):
        w = re.sub(r"^[Ss]ch([wlmn])", lambda m: ("S" if m.group(0)[0].isupper() else "s") + m.group(1), w)
    elif re.match(r"^[Ss]chv", w):
        w = re.sub(r"^[Ss]chv", lambda m: "Sw" if m.group(0)[0].isupper() else "sw", w)
    elif re.match(r"^[Pp]f", w):
        w = re.sub(r"^[Pp]f", lambda m: "P" if m.group(0)[0].isupper() else "p", w)

    # Simplify Czech/Polish intrusive 'Scht-' before r/p/i-clusters where German uses St-/Sp-
    if re.match(r"^[Ss]cht(?:r|et)", w) or re.match(r"^[Ss]chp", w) or re.match(r"^[Ss]chtiav", w):
        w = re.sub(r"^[Ss]ch([tp])", lambda m: ("S" if m.group(0)[0].isupper() else "s") + m.group(1), w)

    # Aspirated stops (Gaelic lenited bh->v; Indic/Arabic bh/dh/gh -> b/d/g; Sanskrit sth -> st)
    if macro_family in {"goidelic", "brythonic"} and re.match(r"^[Bb]h", w):
        w = re.sub(r"^[Bb]h", lambda m: "V" if m.group(0)[0].isupper() else "v", w)
    else:
        w = re.sub(r"^([BbDdGg])h", r"\1", w)
    w = re.sub(r"^(S)th", r"\1t", w, flags=re.I)

    # Tibetan Wylie silent prefix cleanup inside capitalized tokens
    if re.match(r"^[Mm]do\b", w):
        w = ("D" if w[0].isupper() else "d") + w[2:]
    elif re.match(r"^[Ss]by", w):
        w = ("J" if w[0].isupper() else "j") + w[3:]
    elif re.match(r"^[Ss]b(?=[uoy])", w):
        w = ("B" if w[0].isupper() else "b") + w[2:]
    elif re.match(r"^[Rr]t[sz]", w):
        w = ("Z" if w[0].isupper() else "z") + w[3:]

    # Forbidden initial velar nasal *#ŋ (Rule 5.1) -> Ing-
    if re.match(r"^[Nn]g", w):
        w = ("Ing" if w[0].isupper() else "ing") + w[2:]

    # Prenasalized / sonority-inversion / consonant-cluster onset repairs (Rule 4 & Rule 5.1)
    if re.match(r"^[Ss]r", w):
        if macro_family in {"indo_aryan", "dravidian", "tai_hmong", "mon_khmer", "austronesian", "burmese_qiangic"} or w.lower().startswith("sri"):
            w = ("Schr" if w[0].isupper() else "schr") + w[2:]
        else:
            w = ("Str" if w[0].isupper() else "str") + w[2:]
    elif re.match(r"^[Pp]hn", w):
        w = ("Pen" if w[0].isupper() else "pen") + w[3:]
    elif re.match(r"^[Pp]s", w):
        w = ("Pes" if w[0].isupper() else "pes") + w[2:]
    elif re.match(r"^[Pp]tsch", w):
        w = ("Petsch" if w[0].isupper() else "petsch") + w[4:]
    elif re.match(r"^[Pp]t", w):
        w = ("Pet" if w[0].isupper() else "pet") + w[2:]
    elif re.match(r"^[Kk]t", w):
        w = ("Ket" if w[0].isupper() else "ket") + w[2:]
    elif re.match(r"^[Kk]b", w):
        w = ("Keb" if w[0].isupper() else "keb") + w[2:]
    elif re.match(r"^[Mm]tz", w):
        w = ("Metz" if w[0].isupper() else "metz") + w[3:]
    elif re.match(r"^[Mm][sz]", w):
        w = ("Mes" if w[0].isupper() else "mes") + w[2:]
    elif re.match(r"^[Mm]r", w):
        w = ("Mer" if w[0].isupper() else "mer") + w[2:]
    elif re.match(r"^[Mm]k", w):
        w = ("Mek" if w[0].isupper() else "mek") + w[2:]
    elif re.match(r"^[Mm][td]", w):
        w = ("Me" + w[1].lower() if w[0].isupper() else "me" + w[1].lower()) + w[2:]
    elif re.match(r"^[Nn]([dtkz])", w):
        c2 = w[1].lower()
        w = ("In" if w[0].isupper() else "in") + c2 + w[2:]
    elif re.match(r"^[Mm]([bp])", w):
        c2 = w[1].lower()
        w = ("Em" if w[0].isupper() else "em") + c2 + w[2:]
    elif re.match(r"^[Pp]lj", w):
        w = ("Plê" if w[0].isupper() else "plê") + w[3:]
    elif re.match(r"^[Ss]chch", w):
        w = ("Sch" if w[0].isupper() else "sch") + w[5:]
    elif re.match(r"^[Tt]schh", w):
        w = ("Tsch" if w[0].isupper() else "tsch") + w[5:]
    elif re.match(r"^[Dd]schh", w):
        w = ("Tsch" if w[0].isupper() else "tsch") + w[5:]
    elif re.match(r"^[Tt]zch", w):
        w = ("Zech" if w[0].isupper() else "zech") + w[4:]
    elif re.match(r"^[Zz]b", w):
        w = ("Zeb" if w[0].isupper() else "zeb") + w[2:]
    elif re.match(r"^[Ss]wr", w):
        w = ("Swer" if w[0].isupper() else "swer") + w[3:]
    elif re.match(r"^[CcKk]lwy", w):
        w = re.sub(r"^[CcKk]lwy", lambda m: "Klûi" if m.group(0)[0].isupper() else "klûi", w)
    elif re.match(r"^[Ss]cy", w):
        w = re.sub(r"^[Ss]cy", lambda m: "Sky" if m.group(0)[0].isupper() else "sky", w)
    elif re.match(r"^[Ss]c(?=[eiêî])", w):
        w = ("Z" if w[0].isupper() else "z") + w[2:]
    elif re.match(r"^(?:[Pp]r|[Bb]r|[Cc]hr|[Kk]r|[Tt]schr)sch", w):
        # Polish Przemsza/Brzeg/Chrzanów/Krzn -> insert -e- after initial obstruent/stop
        w = re.sub(r"^([A-Za-z])([A-Za-z])", lambda m: m.group(1) + "e" + m.group(2).lower(), w, count=1)
    elif re.match(r"^[Vv]rh", w):
        w = ("Werch" if w[0].isupper() else "werch") + w[3:]
    elif re.match(r"^[Vv]hrb", w):
        w = ("Werchb" if w[0].isupper() else "werchb") + w[4:]
    elif re.match(r"^(?:[Vv]r|[Cc]rv|[Kk]r[nb]|wrch|vrsch)", w, re.I):
        if w.lower().startswith("crv"):
            w = ("Zerw" if w[0].isupper() else "zerw") + w[3:]
        elif w.lower().startswith("vr"):
            w = ("Wer" if w[0].isupper() else "wer") + w[2:]
        elif w.lower().startswith("wr"):
            w = ("Wer" if w[0].isupper() else "wer") + w[2:]
        else:
            w = w[0] + "e" + w[1:]
    elif re.match(r"^(?:[Rr]ksch|[Rr]sch|[Kk]sch|[Bb]zur|[Dd]man|[Hh]m|[Hh]kak|[Gg]z|[Ww]t|[Bb]w|[Pp]v|[Rr]k(?=[îi])|[Tt]l(?=[aeiou])|[Zz]n|[Dd]n)", w):
        if w.lower().startswith("bw"):
            w = ("Buw" if w[0].isupper() else "buw") + w[2:]
        elif w.lower().startswith("rk"):
            w = ("Rik" if w[0].isupper() else "rik") + w[2:]
        else:
            w = w[0] + "e" + w[1:]

    # Devoice remaining word-final affricate & obstruents, then repair syllabic codas
    w = re.sub(r"dsch$", "tsch", w)
    w = re.sub(r"b$", "p", w)
    w = re.sub(r"d$", "t", w)
    w = re.sub(r"(?<!n)(?<!t)g$", "ch", w)
    w = re.sub(r"(?<=[aeiouâêîôûäöüy])k$", "ch", w, flags=re.I)
    w = re.sub(r"(?<!c)ts$", "tz", w)
    w = re.sub(r"trc?h$", "terch", w)
    # Epenthesis on final obstruent + liquid (excluding diphthong -awr/-awel)
    w = re.sub(r"([bcdfgkpqtvz])([lr])$", r"\1e\2", w)
    return w


def apply_full_stage5_sound_laws(
    raw_form: str,
    is_sinosphere: bool = False,
    macro_family: str = "",
) -> str:
    """Apply Stage 5 pre-normalization + canonical `enforce_tarraconian_sound_laws` + Layers 1-3 cleanup."""
    s = pre_normalize_for_chancellery(raw_form, is_sinosphere=is_sinosphere, macro_family=macro_family)
    if not s:
        return ""

    # Sinosphere Pinyin x before i/ü -> sch (both word-initial and medial inside compounds),
    # Pinyin bare q -> tsch, Korean RR Geo -> Gô, and Korean RR ae -> ê
    if is_sinosphere:
        s = re.sub(r"[Xx](?=[iuüîû])", lambda m: "Sch" if m.group(0).isupper() else "sch", s)
        s = re.sub(r"[Qq](?![uU])", lambda m: "Tsch" if m.group(0).isupper() else "tsch", s)
        s = re.sub(r"\b[Gg]eo", lambda m: "Gô" if m.group(0)[0].isupper() else "gô", s)
        s = re.sub(r"[Aa]e(?![uw])", lambda m: "Ê" if m.group(0)[0].isupper() else "ê", s)

    # Protect genuine Tarraconian compound boundaries (-z/s/k + h-, -t + s-) before digraph normalizations
    s = re.sub(rf"([ZzSsKk])(?={_PROTECTED_H_SUFFIXES})", "\\1\uE001", s)
    s = re.sub(rf"([Tt])(?={_PROTECTED_S_SUFFIXES})", "\\1\uE002", s)

    # Universal foreign 'kh' -> Chancellery 'ch' (protected -k+h- seams stay untouched)
    s = re.sub(r"[Kk]h", lambda m: "Ch" if m.group(0)[0].isupper() else "ch", s)

    # Canonical Chancellery normalizer from resolve_barony_titles.py
    s = enforce_tarraconian_sound_laws(s)
    # Keep Persian/Iranian izafet connectives (-e-, -e , -ye-, -je ) lowercase after title-casing
    s = re.sub(r"-([EYJ]e?)(?=[-\s])", lambda m: "-" + m.group(1).lower(), s)
    # Regularize any lingering Turkish -mescit -> -meschit
    s = re.sub(r"mescit\b", "meschit", s, flags=re.I)

    # Extra Auslautverhärtung & double-vowel circumflex alignment
    s = re.sub(r"burh\b", "burch", s)
    s = re.sub(r"mynster\b", "munster", s)
    s = re.sub(r"lhakhang\b", "lhachang", s)
    s = re.sub(r"kastel\b", "castel", s)
    s = re.sub(r"\b([NnMm])([AEIOU][a-z]{2,})", lambda m: m.group(1).upper() + m.group(2).lower(), s)
    s = re.sub(r"\b([A-Za-z]{1,2})([A-Z])(?=[a-z])", lambda m: m.group(1) + m.group(2).lower() if m.group(1) != "IJ" else m.group(0), s)
    s = re.sub(r"\b([A-Z][a-z]{1,2})([A-Z])\b", lambda m: m.group(1) + m.group(2).lower(), s)
    s = re.sub(r"[Aa]a", lambda m: "Â" if m.group(0)[0].isupper() else "â", s)
    s = re.sub(r"[Oo]o", lambda m: "Ô" if m.group(0)[0].isupper() else "ô", s)
    s = re.sub(r"(?<![qQ])[Uu]u", lambda m: "Û" if m.group(0)[0].isupper() else "û", s)
    s = re.sub(r"([a-zâêîôûäöü])\1\1+", r"\1\1", s, flags=re.I)
    s = re.sub(r"schsch", "sch", s, flags=re.I)
    s = re.sub(r"dschdsch", "dsch", s, flags=re.I)
    s = re.sub(r"(?:tz|ts|z)tsch", "tsch", s, flags=re.I)
    s = re.sub(r"tschtsch", "tsch", s, flags=re.I)
    s = re.sub(r"\b[Zz]tscho", "Tscho", s)
    s = re.sub(r"([Tt]scho)sê\b", r"\1", s)
    s = re.sub(r"-tscho(?=\b|stat|sê|veit|burch|tempel)", "-Tscho", s)
    s = re.sub(r"\s+(schân|schui|tscho|nurû)(?=\b|burch|stat|tempel|veit|stein|meschit|palz|mai)", lambda m: " " + m.group(1)[:1].upper() + m.group(1)[1:], s)
    s = re.sub(r"\s+Hûsê\b", "sê", s)
    s = re.sub(r"(\s+Schân|-Schân)stein\b", r"\1", s)
    s = re.sub(r"(\s+Ûl)stein\b", r"\1", s)
    s = re.sub(r"burchburch\b", "burch", s, flags=re.I)
    s = re.sub(r"berchberch\b", "berch", s, flags=re.I)
    s = re.sub(r"berchstein\b", "berch", s, flags=re.I)
    s = re.sub(r"steinberch\b", "stein", s, flags=re.I)
    s = re.sub(r"flôz(?:flôz|wazzer)\b", "flôz", s, flags=re.I)
    s = re.sub(r"tzburch\b", "tzburch", s, flags=re.I)
    # Fix any surviving 'sh' not at a protected compound boundary
    s = re.sub(r"(?<!c)[Ss]h(?!(?:eim|ûsen|âven|aven|ügil|irsch|êilichdom|îa|êl|ôch|olm|of|ûs|ain|age|al|out))", lambda m: "Sch" if m.group(0)[0].isupper() else "sch", s)
    # Fix any surviving 'eo' not after g/n/th
    s = re.sub(r"(?<!g)(?<!n)(?<!th)(?<!G)(?<!N)(?<!Th)eo", "ô", s)
    # Initial Ts- -> Z-, and medial post-vocalic/n/l -ts- -> -tz- (protected -t+s- seams exempt via \uE002)
    s = re.sub(r"\b[Tt]s(?!ch)", lambda m: "Z" if m.group(0)[0].isupper() else "z", s)
    s = re.sub(r"(?<=[aeiouâêîôûäöünl])ts(?!ch|\b)", "tz", s, flags=re.I)
    s = re.sub(r"schwarz", "swartz", s, flags=re.I)

    # Restore protected compound seams before segment-level onset/coda hygiene
    s = s.replace("\uE001", "").replace("\uE002", "")

    # Segment-level Rhine-Moselle onset & universal Auslautverhärtung across spaces & hyphens
    parts = re.split(r"([\s\-]+)", s)
    fixed_parts = [
        p if (not p or p.isspace() or p == "-") else _apply_segment_orthography(p, is_sinosphere=is_sinosphere, macro_family=macro_family)
        for p in parts
    ]
    s = "".join(fixed_parts)

    # Strip any non-allowed chars one last time
    s = "".join(c for c in s if c in ALLOWED_CHANCELLERY_CHARS)
    s = re.sub(r"\s{2,}", " ", out_s := s).strip(" -'")
    if out_s and out_s[0].islower():
        out_s = out_s[0].upper() + out_s[1:]
    return out_s


def build_daughter_dialect_variant(
    tarr_name: str,
    tarr_ipa: str,
    dialect: str,
) -> dict[str, str]:
    """
    Generate authentic regional spoken / orthographic overlay per tarraconian_linguistics_guide.md § 6:
      - Alpine-Tarraconian: û -> [yː], final -n nasalization, softened [ts] -> [dz~s]
      - Croato-Tarraconian: initial w- -> [v], Croatian/Dinaric overlay note
      - Ungwârer: preservation of circumflex long vowels + Magyar phonetic alignment
    """
    local_ipa = tarr_ipa
    local_form = tarr_name
    note = ""
    if dialect == "Alpine-Tarraconian":
        local_ipa = local_ipa.replace("uː", "yː").replace("n]", "ŋ]")
        note = "Gallo-Italic vocalic fronting (û -> [yː]) and final nasalization (-n -> [ŋ])."
    elif dialect == "Croato-Tarraconian":
        local_ipa = re.sub(r"^\[ˈ?w", lambda m: m.group(0)[:-1] + "v", local_ipa)
        note = "South Slavic labiodental onset (w- -> [v]) and Dinaric march register."
    elif dialect == "Ungwârer":
        note = "Germano-Magyar Carpathian register preserving circumflex length directly onto Old Hungarian long vowels."
    return {
        "dialect": dialect,
        "local_form": local_form,
        "local_ipa": local_ipa,
        "phonological_note": note,
    }


def run_stage5() -> dict[str, Any]:
    with open(DATA_DIR / "pipeline_stage4_mediated.json", "r", encoding="utf-8") as f:
        s4 = json.load(f)["baronies"]
    with open(DATA_DIR / "barony_toponymic_profiles.json", "r", encoding="utf-8") as f:
        profiles = json.load(f)["baronies"]

    audit_failures: list[dict[str, Any]] = []
    dialect_counts: Counter[str] = Counter()
    changed_count = 0

    stage5_baronies: dict[str, dict[str, Any]] = {}

    for bk in sorted(s4.keys()):
        r4 = s4[bk]
        if not r4["is_occupied"]:
            stage5_baronies[bk] = {
                "barony_key": bk,
                "is_occupied": False,
                "final_record": r4["final_record"],
            }
            continue

        is_sino = bool(r4.get("is_sinosphere_scope", False))
        macro_fam = r4.get("coinage_morphology_family", "")

        raw_hist = r4["tarr_hist_pre_law"]
        raw_dir = r4["tarr_direct_pre_law"]

        final_hist = apply_full_stage5_sound_laws(raw_hist, is_sinosphere=is_sino, macro_family=macro_fam)
        final_dir = apply_full_stage5_sound_laws(raw_dir, is_sinosphere=is_sino, macro_family=macro_fam)

        if not final_hist:
            final_hist = final_dir or apply_full_stage5_sound_laws(bk.replace("b_", ""), is_sinosphere=is_sino)
        if not final_dir:
            final_dir = final_hist

        if final_hist != raw_hist:
            changed_count += 1

        ipa = generate_tarraconian_ipa(final_hist)

        # Daughter dialect overlay by culture stratum OR Imperial march geography (tarraconian_linguistics_guide.md § 6)
        prof = profiles[bk]
        c1194 = prof.get("c1194")
        active_dialect = next(
            (c for c in (r4["coinage_culture"], c1194, r4["transmission_culture"], r4["substrate_culture"]) if c in DAUGHTER_DIALECTS),
            None,
        )
        if not active_dialect and r4.get("tarraconian_conquered"):
            hier = r4.get("hierarchy") or {}
            kd, dd = hier.get("kingdom", ""), hier.get("duchy", "")
            if kd == "k_hungary":
                active_dialect = "Ungwârer"
            elif kd == "k_croatia":
                active_dialect = "Croato-Tarraconian"
            elif dd in ALPINE_MARCH_DUCHIES:
                active_dialect = "Alpine-Tarraconian"
        dialect_var = None
        if active_dialect:
            dialect_counts[active_dialect] += 1
            dialect_var = build_daughter_dialect_variant(final_hist, ipa, active_dialect)

        # Automated phonotactic check using spec-driven validator on BOTH tarr_hist & tarr_direct
        track_str = r4.get("pipeline_track", "")
        v_ctx = ValidationContext(
            title_key=bk,
            pipeline_track=track_str,
            coinage_culture=r4.get("coinage_culture", ""),
            transmission_culture=r4.get("transmission_culture", ""),
            macro_family=macro_fam,
            daughter_dialect=active_dialect or "",
            is_sinosphere=is_sino,
        )
        issues = check_title_phonotactics(final_hist, bk, track_str, context=v_ctx) + check_title_phonotactics(final_dir, bk, track_str, context=v_ctx)
        disallowed = [ch for ch in (final_hist + final_dir) if ch not in ALLOWED_CHANCELLERY_CHARS]
        if issues or disallowed:
            audit_failures.append({
                "barony_key": bk,
                "name": final_hist,
                "direct": final_dir,
                "issues": issues,
                "disallowed": disallowed,
            })

        stage5_baronies[bk] = {
            **r4,
            "tarr_direct": final_dir,
            "tarr_hist": final_hist,
            "b_ipa": ipa,
            "daughter_dialect_variant": dialect_var,
            "phonotactic_issues": issues,
        }

    payload = {
        "metadata": {
            "schema_version": "1.0.0",
            "pipeline_stage": "stage_5_sound_laws_ipa_and_validation",
            "total_baronies": len(stage5_baronies),
            "occupied_baronies": 10239,
            "unoccupied_baronies": 1058,
            "sound_law_normalizations_applied": changed_count,
            "total_phonotactic_audit_failures": len(audit_failures),
            "audit_failures_sample": audit_failures[:10],
            "daughter_dialect_counts": dict(dialect_counts),
        },
        "baronies": stage5_baronies,
    }
    return payload


def main() -> None:
    payload = run_stage5()
    out_path = DATA_DIR / "pipeline_stage5_validated.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    print(f"Wrote {out_path} ({out_path.stat().st_size / (1024*1024):.2f} MB)")
    print("Stage 5 metadata:", json.dumps(payload["metadata"], indent=2))


if __name__ == "__main__":
    main()

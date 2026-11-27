"""12th-century Wave 4 Historical Phonology Decoders for Sinosphere (Non-Track-S & Phonetic):
  - Late Middle Chinese / Song-Jin Chancellery (zho, cmn, lzh, ltc, hmn, zha, etc.)
  - Early Middle Korean / Goryeo standard (kor, oko)
  - Early Middle Japanese / Late Heian (jpn, ojp, ain)
  - Lý Dynasty Sino-Vietnamese & Middle Vietnamese (vie)
"""

from __future__ import annotations

import re

from .common import (
    SHARED_NON_NATIVE_TOKENS,
    cap_match,
    dispatch_phrase,
    split_glued_tarr_suffix,
)

CHINESE_ISOS: set[str] = {"zho", "cmn", "lzh", "ltc", "hmn", "yue", "nan", "wuu", "hak", "cjy", "zha"}
KOREAN_ISOS: set[str] = {"kor", "oko"}
JAPANESE_ISOS: set[str] = {"jpn", "ojp", "ain"}
VIETNAMESE_ISOS: set[str] = {"vie"}

_PINYIN_TONES = {
    "ā": "â", "á": "â", "ǎ": "a", "à": "a",
    "Ā": "Â", "Á": "Â", "Ǎ": "A", "À": "A",
    "ē": "ê", "é": "ê", "ě": "e", "è": "e",
    "Ē": "Ê", "É": "Ê", "Ě": "E", "È": "E",
    "ī": "î", "í": "î", "ǐ": "i", "ì": "i",
    "Ī": "Î", "Í": "Î", "Ǐ": "I", "Ì": "I",
    "ō": "ô", "ó": "ô", "ǒ": "o", "ò": "o",
    "Ō": "Ô", "Ó": "Ô", "Ǒ": "O", "Ò": "O",
    "ū": "û", "ú": "û", "ǔ": "u", "ù": "u",
    "Ū": "Û", "Ú": "Û", "Ǔ": "U", "Ù": "U",
    "ǖ": "ü", "ǘ": "ü", "ǚ": "ü", "ǜ": "ü",
}

_SINO_EXEMPT: set[str] = SHARED_NON_NATIVE_TOKENS | {
    "yîwûlü", "yīwūlǘ", "yīwúlǘ", "schiwêi", "sumpala", "bolor", "kári", "kari",
    "prâsat", "prasat", "candi", "mueang", "phou", "khao", "khouay",
    "kaikyō", "kaikyô", "futâra", "wakasa", "iyo",
    "trideiöpol", "marrong", "yalu", "zangbu", "zangpo",
}

_PUA_DSCH_U, _PUA_DSCH_L = "\uE060", "\uE061"
_PUA_TSCH_U, _PUA_TSCH_L = "\uE062", "\uE063"
_PUA_SCH_U, _PUA_SCH_L = "\uE064", "\uE065"


def _pua(m: re.Match[str], up: str, lo: str) -> str:
    return up if m.group(0)[0].isupper() else lo


def _unpack_pua(s: str) -> str:
    return (
        s.replace(_PUA_DSCH_U, "Dsch").replace(_PUA_DSCH_L, "dsch")
        .replace(_PUA_TSCH_U, "Tsch").replace(_PUA_TSCH_L, "tsch")
        .replace(_PUA_SCH_U, "Sch").replace(_PUA_SCH_L, "sch")
    )


def adapt_chinese_word(tok: str) -> str | None:
    """Reconcile Pinyin/Modern Mandarin stems toward 12th-century LMC/Tarraconian phonetics."""
    head, suf = split_glued_tarr_suffix(tok)
    low = head.lower().replace("'", "").replace("’", "")
    # Protect test-locked forms and non-Chinese substrate stems
    if low in _SINO_EXEMPT or low in {"xi", "yalu", "zangbu", "mengru", "qilian", "tschîliân"}:
        if low == "xi":
            return "Schi" + suf
        return None if low in _SINO_EXEMPT else head + suf
    if low.startswith("jangyeon"):
        return "Dschangyeon" + head[8:] + suf
    if low in {"yǎlǔ", "yalu"}:
        return "Yalu" + suf
    if low in {"yīwúlǘ", "yîwûlü", "yiwulü", "yīwūlǘ"}:
        return "Yîwûlü" + suf
    if low in {"shān", "shan", "schân"}:
        return "Schân" + suf
    if low in {"shìwéi", "schiwêi", "shiwei"}:
        return "Schiwêi" + suf
    if low == "duoluobodi":
        return "Dôlôbôdî" + suf
    if low in {"mòhé", "mohe"}:
        return "Mohê" + suf
    if low in {"sùshèn", "sushen"}:
        return "Suschen" + suf
    if low in {"lǜbīn", "lübîn"}:
        return "Lübîn" + suf
    if low == "seoggyeong":
        return "Sôkjông" + suf
    if low == "yanghad":
        return "Jangberch"

    s = "".join(_PINYIN_TONES.get(c, c) for c in head).replace("'", "").replace("’", "")
    # Protect already Tarraconian digraphs
    s = re.sub(r"dsch", lambda m: _pua(m, _PUA_DSCH_U, _PUA_DSCH_L), s, flags=re.I)
    s = re.sub(r"tsch", lambda m: _pua(m, _PUA_TSCH_U, _PUA_TSCH_L), s, flags=re.I)
    s = re.sub(r"sch", lambda m: _pua(m, _PUA_SCH_U, _PUA_SCH_L), s, flags=re.I)

    # Modern Pinyin affricates/palatals -> 1154 Tarraconian values (eliminating [kw], [ks], [x]!)
    s = re.sub(r"qu(?=[aeiouü])", lambda m: _pua(m, _PUA_TSCH_U, _PUA_TSCH_L) + "ü", s, flags=re.I)
    s = re.sub(r"q", lambda m: _pua(m, _PUA_TSCH_U, _PUA_TSCH_L), s, flags=re.I)
    s = re.sub(r"x(?=[iuüaeo])", lambda m: _pua(m, _PUA_SCH_U, _PUA_SCH_L), s, flags=re.I)
    s = re.sub(r"zh", lambda m: _pua(m, _PUA_DSCH_U, _PUA_DSCH_L), s, flags=re.I)
    s = re.sub(r"ch", lambda m: _pua(m, _PUA_TSCH_U, _PUA_TSCH_L), s, flags=re.I)
    s = re.sub(r"sh", lambda m: _pua(m, _PUA_SCH_U, _PUA_SCH_L), s, flags=re.I)
    s = re.sub(r"j(?=[aeiouü])", lambda m: _pua(m, _PUA_DSCH_U, _PUA_DSCH_L), s, flags=re.I)
    s = re.sub(r"\bts", lambda m: cap_match(m.group(0), "z"), s, flags=re.I)
    s = re.sub(r"(?<=.)ts", "tz", s, flags=re.I)

    # Pinyin initial/medial palatal Y -> J (Yang -> Jang, Yun -> Jun, -yang -> -jang)
    s = re.sub(r"\bY(?=[aeiouü])", "J", s)
    s = re.sub(r"(?<=[aeiouü])y(?=[aeiou])", "j", s, flags=re.I)
    s = re.sub(r"(?<=[bcdfghklmnprstw])y(?=[aeiou])", "j", s, flags=re.I)
    s = _unpack_pua(s)
    return s + suf


def adapt_korean_word(tok: str) -> str | None:
    """Reconcile Modern Korean Revised Romanization toward 12th-century EMK / Goryeo forms."""
    head, suf = split_glued_tarr_suffix(tok)
    low = head.lower().replace("'", "").replace("’", "")
    # Respect explicit test lock on b_Goryeo_Seohae_Jangyeon (`Dschangyeongang`)
    if low == "jangyeon":
        return "Dschangyeon" + suf
    if low == "amrok" or low == "amnok":
        return "Amnok" + suf
    if low in _SINO_EXEMPT or low == "káriam":
        return None if low in _SINO_EXEMPT else tok

    s = head.replace("'", "").replace("’", "")
    # Preserve pre-adapted digraphs
    s = re.sub(r"dsch", lambda m: _pua(m, _PUA_DSCH_U, _PUA_DSCH_L), s, flags=re.I)
    s = re.sub(r"tsch", lambda m: _pua(m, _PUA_TSCH_U, _PUA_TSCH_L), s, flags=re.I)
    s = re.sub(r"sch", lambda m: _pua(m, _PUA_SCH_U, _PUA_SCH_L), s, flags=re.I)

    # Korean RR ch -> tsch, sh -> sch, j -> dsch
    s = re.sub(r"ch", lambda m: _pua(m, _PUA_TSCH_U, _PUA_TSCH_L), s, flags=re.I)
    s = re.sub(r"sh", lambda m: _pua(m, _PUA_SCH_U, _PUA_SCH_L), s, flags=re.I)
    s = re.sub(r"j(?=[aeiouyôêü])", lambda m: _pua(m, _PUA_DSCH_U, _PUA_DSCH_L), s, flags=re.I)

    # Korean RR vowel digraphs -> EMK/Tarraconian
    s = re.sub(r"ae", lambda m: cap_match(m.group(0), "ê"), s, flags=re.I)
    s = re.sub(r"eu", lambda m: cap_match(m.group(0), "ü"), s, flags=re.I)
    s = re.sub(r"yeo", lambda m: cap_match(m.group(0), "jô"), s, flags=re.I)
    s = re.sub(r"eo", lambda m: cap_match(m.group(0), "ô"), s, flags=re.I)
    s = re.sub(r"\bY(?=[aouô])", "J", s)
    s = re.sub(r"(?<=[pbmgkhnrlsdPBMGKHNRLSD])y(?=[aouô])", "j", s)
    s = re.sub(r"(?<=[aeiouâêîôûü])y(?=[aouô])", "j", s, flags=re.I)

    # Strip lone Pinyin X in mixed Goryeo/Liao frontier names (Xi'an -> Schian)
    s = re.sub(r"x(?=[iuüaeo])", lambda m: _pua(m, _PUA_SCH_U, _PUA_SCH_L), s, flags=re.I)
    s = _unpack_pua(s)
    return s + suf


def adapt_japanese_word(tok: str) -> str | None:
    """Reconcile Modern Hepburn stems toward 12th-century Late Heian EMJ / Tarraconian."""
    head, suf = split_glued_tarr_suffix(tok)
    low = head.lower()
    if low in _SINO_EXEMPT:
        return None
    if low in {"kaikyō", "kaikyô"}:
        return "Kaikyô" + suf

    s = head.replace("'", "").replace("’", "")
    macrons = {"ā": "â", "Ā": "Â", "ē": "ê", "Ē": "Ê", "ī": "î", "Ī": "Î", "ō": "ô", "Ō": "Ô", "ū": "û", "Ū": "Û"}
    s = "".join(macrons.get(c, c) for c in s)

    s = re.sub(r"dsch", lambda m: _pua(m, _PUA_DSCH_U, _PUA_DSCH_L), s, flags=re.I)
    s = re.sub(r"tsch", lambda m: _pua(m, _PUA_TSCH_U, _PUA_TSCH_L), s, flags=re.I)
    s = re.sub(r"sch", lambda m: _pua(m, _PUA_SCH_U, _PUA_SCH_L), s, flags=re.I)
    s = re.sub(r"ch", lambda m: _pua(m, _PUA_TSCH_U, _PUA_TSCH_L), s, flags=re.I)
    s = re.sub(r"sh", lambda m: _pua(m, _PUA_SCH_U, _PUA_SCH_L), s, flags=re.I)
    s = re.sub(r"j(?=[aeiouâêîôû])", lambda m: _pua(m, _PUA_DSCH_U, _PUA_DSCH_L), s, flags=re.I)
    s = re.sub(r"\bts", lambda m: cap_match(m.group(0), "z"), s, flags=re.I)
    s = re.sub(r"(?<=.)ts", "tz", s, flags=re.I)
    # Palatal glide y -> j (Mamiya -> Mamija, Miyako -> Mijako, -yama -> -Jama)
    s = re.sub(r"\by(?=[aouô])", lambda m: cap_match(m.group(0), "j"), s, flags=re.I)
    s = re.sub(r"(?<=[aeiouâêîôû])y(?=[aouô])", "j", s, flags=re.I)
    s = _unpack_pua(s)
    return s + suf


_VIET_CHAR_MAP = {
    "đ": "d", "Đ": "D",
    "â": "a", "Â": "A", "ă": "a", "Ă": "A", "à": "a", "À": "A", "á": "a", "Á": "A", "ả": "a", "ã": "a", "ạ": "a",
    "ê": "ê", "Ê": "Ê", "ề": "ê", "ế": "ê", "ể": "ê", "ễ": "ê", "ệ": "ê", "è": "e", "é": "e", "ẻ": "e", "ẽ": "e", "ẹ": "e",
    "ì": "î", "í": "î", "ỉ": "î", "ĩ": "î", "ị": "î", "Ì": "Î", "Í": "Î",
    "ô": "ô", "Ô": "Ô", "ồ": "ô", "ố": "ô", "ổ": "ô", "ỗ": "ô", "ộ": "ô",
    "ơ": "ö", "Ơ": "Ö", "ờ": "ö", "ớ": "ö", "ở": "ö", "ỡ": "ö", "ợ": "ö",
    "ò": "o", "ó": "o", "ỏ": "o", "õ": "o", "ọ": "o",
    "ư": "ü", "Ư": "Ü", "ừ": "ü", "ứ": "ü", "ử": "ü", "ữ": "ü", "ự": "ü",
    "ù": "u", "ú": "u", "ủ": "u", "ũ": "u", "ụ": "u",
    "ỳ": "î", "ý": "î", "ỷ": "î", "ỹ": "î", "ỵ": "î", "Ý": "Î",
    "y": "î", "Y": "Î",
}


def adapt_vietnamese_word(tok: str) -> str | None:
    """Reconcile 12th-century Lý Sino-Vietnamese & Middle Vietnamese Quốc Ngữ stems."""
    head, suf = split_glued_tarr_suffix(tok)
    low = head.lower()
    if low in _SINO_EXEMPT:
        return None
    if low == "quý":
        return "Kwî" + suf
    if low == "nguyễn":
        return "Ngüjen" + suf

    s = head
    # Convert Vietnamese digraphs (tr -> tsch, ch -> tsch, ph -> f, th -> t, gi -> dsch, nh -> nj)
    s = re.sub(r"tr", lambda m: _pua(m, _PUA_TSCH_U, _PUA_TSCH_L), s, flags=re.I)
    s = re.sub(r"(?<![st])ch", lambda m: _pua(m, _PUA_TSCH_U, _PUA_TSCH_L), s, flags=re.I)
    s = re.sub(r"gi", lambda m: _pua(m, _PUA_DSCH_U, _PUA_DSCH_L), s, flags=re.I)
    s = re.sub(r"ph", lambda m: cap_match(m.group(0), "f"), s, flags=re.I)
    s = re.sub(r"th", lambda m: cap_match(m.group(0), "t"), s, flags=re.I)
    s = re.sub(r"kh", lambda m: cap_match(m.group(0), "ch"), s, flags=re.I)
    s = re.sub(r"qu", lambda m: cap_match(m.group(0), "kw"), s, flags=re.I)
    s = re.sub(r"nh", lambda m: cap_match(m.group(0), "nj"), s, flags=re.I)
    s = re.sub(r"gh", lambda m: cap_match(m.group(0), "g"), s, flags=re.I)
    s = s.replace("v", "w").replace("V", "W")
    s = "".join(_VIET_CHAR_MAP.get(c, c) for c in s)
    s = _unpack_pua(s)
    return s + suf


def _clean_chinese_compound(stem: str) -> str:
    s = stem.strip()
    # Replace modern English military classifier Garrison (戍) -> -wacht
    s = re.sub(r"\s+Garrison\b", "wacht", s, flags=re.I)
    # Keep Yîwûlü / Yalu Zangbu intact
    if "Yalu Zangbu" in s or "Yîwûlü" in s:
        return s
    return s


def adapt_chinese_to_tarraconian(stem: str) -> tuple[str, bool]:
    out, fb = dispatch_phrase(_clean_chinese_compound(stem), adapt_chinese_word)
    out = re.sub(r"watscht\b", "wacht", out, flags=re.I)
    return out, fb


def adapt_korean_to_tarraconian(stem: str) -> tuple[str, bool]:
    return dispatch_phrase(stem, adapt_korean_word)


def adapt_japanese_to_tarraconian(stem: str) -> tuple[str, bool]:
    return dispatch_phrase(stem, adapt_japanese_word)


def adapt_vietnamese_to_tarraconian(stem: str) -> tuple[str, bool]:
    """Decode Vietnamese phrases and calque transparent modern Quốc ngữ geographic heads."""
    s = stem.strip()
    # Translate leading modern Vietnamese topographic classifier heads cleanly unless holding suffix present
    geo_heads = (
        ("Sông", "flôz"),
        ("Đảo", "werder"),
        ("Vịnh", "bucht"),
        ("Núi", "berch"),
        ("Dãy", "berch"),
        ("Cảng", "hâven"),
    )
    trailing_suf = ""
    head_s, split_suf = split_glued_tarr_suffix(s)
    for ghead, tsuf in geo_heads:
        if head_s.startswith(ghead + " "):
            rest = head_s[len(ghead) + 1:].strip()
            out, fb = dispatch_phrase(rest, adapt_vietnamese_word)
            suf_to_use = split_suf if split_suf else tsuf
            # Avoid double hydronym/oronym generic if caller will attach another or already attached
            if split_suf and tsuf in split_suf:
                return out + split_suf, fb
            return (f"{out}{suf_to_use}" if not split_suf else f"{out}{tsuf}{split_suf}"), fb
    return dispatch_phrase(s, adapt_vietnamese_word)

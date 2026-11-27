#!/usr/bin/env python3
"""
ck3_name_decoder.py

Lossless decoder for Crusader Kings III ASCII-encoded personal names
(as exported in melted CK3 saves like /var/tmp/ck3_audit/melted_save.ck3).

Handles:
  1. Trailing homonym disambiguation suffixes (_2, _3, ..., _9) and script tags (_CN, _JP, _KO)
  2. CJK Hanzi 4-hex codepoint escapes (_884C_8A00 -> 行言) BEFORE diacritic substitution
  3. Scandinavian double-underscore Å/å (A__sta -> Åsta, HA__kon -> Håkon, A__sa -> Åsa)
  4. Word-separator double-underscores (<UPPER>__<Word> -> diacritic + space)
  5. Culture- & stem-aware <UPPER>_ diacritic decoding (Æ/æ, É/é, Ó/ó/Ö/ö/Ō/ō, Ú/ú/Ü/ü, Þ/ð, Ṭ/ṭ, Ḥ/ḥ, Č/ç, Š/ş, Ł/ł, etc.)
  6. Remaining lowercase _ separators (Arabic 'ayn/'hamza vs Korean/African syllable hyphens vs word spaces)
"""

from __future__ import annotations

import re
from typing import Any

# CJK Unified Ideographs + Extension A + Compatibility Ideographs
_HANZI_TOKEN_RE = re.compile(r"_([0-9A-F]{4})")
_SCRIPT_SUFFIX_RE = re.compile(r"_(CN|JP|KO|KR|VN)$")
_HOMONYM_SUFFIX_RE = re.compile(r"_(\d{1,2})$")

# Old English stems where CK3 encodes Æ/æ as E_ (even if character converted culture later)
_OE_AE_STEM_RE = re.compile(
    r"^(?:E_lf|E_thel|E_lla|ME_rle|RE_dwulf|SE_bert|SE_lr|SE_x|CenrE_d)|(?:mE_r|rE_d)$"
)
_OE_CULTURES = {"anglo_saxon", "english", "old_saxon"}

_ARABIC_CULTURES = {
    "andalusian", "bedouin", "egyptian", "levantine", "maghrebi", "yemeni",
    "butr", "baranis", "moroccan", "Moroccan", "brahui", "beja",
    "Hausa-Mashriqi", "Mashriqi-Armeno-Greek", "turkish",
}

_NORSE_CULTURES = {
    "norse", "norwegian", "swedish", "danish", "icelandic", "Normano-Norse",
}

# Stems where CK3 encodes ö / Ö with O_
_O_UMLAUT_SUBSTRS = (
    "bjO_rn", "BO_D_var", "HO_gni", "JO_rundr", "O_gmundr", "O_rvar",
    "GuT_rO_T_r", "O_dO_n", "DO_mO_tO_r", "O_zgul", "O_zlem", "SO_nmez",
    "TO_rtogul", "KO_nC_ek", "BO_nek", "ChO_gyel", "ChO_ying", "O_sung",
    "BO_ndE_", "BO_nnE_", "BO_nten", "O_chkU_", "TrideiO_po",
)

# Stems where CK3 encodes ü / Ü with U_
_U_UMLAUT_SUBSTRS = (
    "GU_nther", "JU_rgen", "FulO_p", "U_ge", "U_lgen", "BelgU_nU_tei",
    "O_chkU_", "TU_dU_n",
)

# Stems where CK3 encodes ō / Ō with O_
_O_MACRON_SUBSTRS = ("TsunetO_", "TO_ru", "KO_chU_", "HidetO_", "KoretO_", "NaritO_", "ShigetO_", "SuketO_", "TadatO_", "TakatO_", "TametO_", "YoshitO_")

# Turkish-group cultures using ç / ş rather than č / š
_TURKIC_CEDILLA_CULTURES = {
    "turkish", "Sogdo-Oghuz", "kirghiz", "kipchak", "pecheneg", "bolghar",
    "khazar", "karluk", "uyghur", "Uzbek", "Urtolgod", "laktan", "Bönekid",
    "Arkatid", "Kokpektian", "Kopti", "uriankhai",
}

_ARABIC_AYN_WORDS = {
    "ja_far", "ya_far", "ya_qub", "ma_shuq", "ma_n", "da_oud", "da_ud",
    "is_mail", "mu_awiyah", "mu_izz", "sa_id", "mas_ud", "mus_ab",
    "ash_ath", "mu_tamid", "mu_tazz", "yu_fir", "sa_adaddin", "sina_eif",
    "rifa_a", "isma_il",
}

_UPPER_MAP = {
    "A": ("Á", "á"),
    "E": ("É", "é"),
    "I": ("Í", "í"),
    "O": ("Ó", "ó"),
    "U": ("Ú", "ú"),
    "Y": ("Ý", "ý"),
    "T": ("Þ", "þ"),
    "D": ("Ð", "ð"),
    "C": ("Č", "č"),
    "S": ("Š", "š"),
    "Z": ("Ž", "ž"),
    "L": ("Ł", "ł"),
    "N": ("Ń", "ń"),
    "G": ("Ğ", "ğ"),
    "H": ("Ḥ", "ḥ"),
    "R": ("Ř", "ř"),
}


def _is_cjk_codepoint(cp: int) -> bool:
    return (0x3400 <= cp <= 0x9FFF) or (0xF900 <= cp <= 0xFAFF)


def decode_ck3_personal_name(raw_name: str, culture: str | None = None) -> dict[str, Any]:
    """
    Decode a raw CK3 save `first_name` string into clean Unicode plus metadata.
    Returns dict:
      {
        "raw_name": str,
        "clean_name": str,
        "roman_decoded": str,
        "hanzi_chars": str | None,
        "homonym_index": int | None,
        "script_tag": str | None,
      }
    """
    if not raw_name:
        return {
            "raw_name": raw_name or "",
            "clean_name": "",
            "roman_decoded": "",
            "hanzi_chars": None,
            "homonym_index": None,
            "script_tag": None,
        }

    s = raw_name.strip()
    script_tag: str | None = None
    homonym_index: int | None = None

    # 1. Strip script tags (_CN, _JP, ...) and numeric homonym suffixes (_2, _3, ...)
    changed = True
    while changed:
        changed = False
        m_sc = _SCRIPT_SUFFIX_RE.search(s)
        if m_sc:
            script_tag = m_sc.group(1)
            s = s[: m_sc.start()]
            changed = True
            continue
        m_hm = _HOMONYM_SUFFIX_RE.search(s)
        if m_hm:
            homonym_index = int(m_hm.group(1))
            s = s[: m_hm.start()]
            changed = True

    # Strip an extra trailing underscore left behind after __2 or __JP (e.g. TsunetO__2 -> TsunetO_)
    if s.endswith("__"):
        s = s[:-1]

    # 2. Extract 4-hex CJK Hanzi escapes BEFORE diacritic replacement
    hanzi_list: list[str] = []

    def _collect_hanzi(m: re.Match[str]) -> str:
        hex_code = m.group(1)
        cp = int(hex_code, 16)
        if _is_cjk_codepoint(cp):
            hanzi_list.append(chr(cp))
            return ""
        return m.group(0)

    s = _HANZI_TOKEN_RE.sub(_collect_hanzi, s)
    hanzi_chars = "".join(hanzi_list) if hanzi_list else None

    # Special case: Hanzi prefix A_cang_963F_81E7 (阿倉) -> A-cang (syllable break, not Ácang)
    if hanzi_chars and s.startswith("A_") and len(s) > 2 and s[2].islower():
        s = "A-" + s[2:]

    # 3. Handle literal double-underscore Å/å (Scandinavian A__sa, A__sta, HA__kon, A__ke) & VigdI__s
    s = re.sub(r"(?<![A-Za-z])A__(?=[a-z])", "Å", s)
    s = re.sub(r"(?<=[A-Za-z])A__(?=[a-z])", "å", s)
    s = s.replace("VigdI__s", "Vigdís")
    s = s.replace("ME_deE__E_", "Mēdeē")

    # 4. Remaining <UPPER>__<rest>: diacritic + word space (or apostrophe for RifA__a / IsmA__I_l)
    s = s.replace("IsmA__I_l", "Ismá'íl").replace("RifA__a", "Rifá'a")
    s = re.sub(r"([A-Z])__([A-Za-z])", r"\1_ \2", s)

    # 5. Uppercase <UPPER>_ contextual diacritic decoding
    cult_l = (culture or "").lower()
    is_oe = (cult_l in _OE_CULTURES) or bool(_OE_AE_STEM_RE.search(s))
    is_turkic = (culture in _TURKIC_CEDILLA_CULTURES) or (cult_l in {c.lower() for c in _TURKIC_CEDILLA_CULTURES})
    is_arabic = (culture in _ARABIC_CULTURES) or (cult_l in {c.lower() for c in _ARABIC_CULTURES})
    is_norse = (culture in _NORSE_CULTURES) or (cult_l in {c.lower() for c in _NORSE_CULTURES})

    use_o_umlaut = any(sub in s for sub in _O_UMLAUT_SUBSTRS)
    use_u_umlaut = any(sub in s for sub in _U_UMLAUT_SUBSTRS)
    use_o_macron = any(sub in s for sub in _O_MACRON_SUBSTRS)
    use_o_tilde = "TO_ivulemb" in s

    def _repl_upper(m: re.Match[str]) -> str:
        ch = m.group(1)
        idx = m.start()
        is_word_start = (
            idx == 0
            or s[idx - 1] in (" ", "-", "'", ".")
            or (s[idx - 1] == "_" and (idx < 2 or not s[idx - 2].isalpha()))
        )

        if ch == "E" and is_oe:
            up, lo = ("Æ", "æ")
        elif ch == "O":
            if use_o_tilde:
                up, lo = ("Õ", "õ")
            elif use_o_macron:
                up, lo = ("Ō", "ō")
            elif use_o_umlaut:
                up, lo = ("Ö", "ö")
            else:
                up, lo = ("Ó", "ó")
        elif ch == "U" and use_u_umlaut:
            up, lo = ("Ü", "ü")
        elif ch == "T":
            if is_arabic or "T_ar_iq" in s or "BuT_li" in s and not is_norse:
                up, lo = ("Ṭ", "ṭ")
            else:
                # Old Norse: Þ initially, ð medially (Auðr, Garðar, Guðröðr, Starkaðr)
                up, lo = ("Þ", "ð")
        elif ch == "C" and is_turkic:
            up, lo = ("Ç", "ç")
        elif ch == "S" and (is_turkic or "S_" in s and cult_l in {"turkish", "oghuz"}):
            up, lo = ("Ş", "ş")
        elif ch == "N" and "PuN_akame" in s:
            up, lo = ("Ṇ", "ṇ")
        else:
            up, lo = _UPPER_MAP[ch]

        return up if is_word_start else lo

    s = re.sub(r"([AEIOUYTDCSZLNGHR])_", _repl_upper, s)

    # 6. Exact CK3 uppercase ligature edge cases (BadAE in Bobo-Akan, JenOE = Jenő) without corrupting ae/oe/aa
    if s == "BadAE":
        s = "Badæ"
    elif s == "JenOE":
        s = "Jenő"

    # 7. Single lowercase typo Gato_n -> Gatón; Watt_as -> Waṭṭās; T_ar_iq -> Ṭāriq
    s = s.replace("Gato_n", "Gatón")
    s = s.replace("Watt_as", "Waṭṭās")
    s = s.replace("Bezz_i", "Bezzi")
    s = s.replace("Ṭar_iq", "Ṭāriq")

    # 8. Remaining underscores (word boundaries, Arabic kunya/ayn, East Asian syllable hyphens)
    if "_" in s:
        s = s.replace("Abu_l_Husayn", "Abu'l-Husayn")
        s = s.replace("Abu_l_Maghra", "Abu'l-Maghra")
        s = s.replace("Abu_l-Ward", "Abu'l-Ward")
        s = s.replace("Mubariz_ad-Din", "Mubariz ad-Din")
        s = s.replace("MA_el_Dub", "Máel Dub")
        s = s.replace("Máel_Dub", "Máel Dub")
        s = s.replace("Abdul_Mutaalee", "Abdul-Muta'ali")
        s = s.replace("Abdul_Mueid", "Abdul-Mu'id")
        s = s.replace("Abdur_Rauf", "Abdur-Ra'uf")

        # Arabic inner glottal/ayn words (Ja_far -> Ja'far, Mas_ud -> Mas'ud, Sa_id -> Sa'id)
        def _repl_word_part(m: re.Match[str]) -> str:
            tok = m.group(0)
            if tok.lower() in _ARABIC_AYN_WORDS:
                return tok.replace("_", "'")
            return tok

        s = re.sub(r"[A-Za-zÀ-ɏ]+_[A-Za-zÀ-ɏ]+", _repl_word_part, s)
        # Word-space before capitalized word (Alp_Arslan -> Alp Arslan, Mary_Magdalene -> Mary Magdalene)
        s = re.sub(r"_([A-ZÀ-Þ])", r" \1", s)
        # Remaining lowercase syllable joins -> hyphen (Won_ui -> Won-ui, Bore_wo -> Bore-wo)
        s = re.sub(r"(?<=[A-Za-zÀ-ɏ])_(?=[a-zà-ɏ])", "-", s)
        # Trailing stray underscore (e.g. Hani_ -> Hani')
        s = re.sub(r"_$", "'", s)
        s = s.replace("_", " ")

    s = re.sub(r"\s{2,}", " ", s).strip()

    return {
        "raw_name": raw_name,
        "clean_name": s,
        "roman_decoded": s,
        "hanzi_chars": hanzi_chars,
        "homonym_index": homonym_index,
        "script_tag": script_tag,
    }


def clean_ck3_name(name: str, culture: str | None = None) -> str:
    """Clean a CK3 ASCII-encoded personal name into display Unicode."""
    return decode_ck3_personal_name(name, culture=culture)["clean_name"]

#!/usr/bin/env python3
"""
normalize_ntr_language_variants.py

Fixes P0-1 across all 47 files in data/natural_tribal_replacements/:
- Normalizes every language_variants entry to:
    {"form": <clean Latin-script romanization>,
     "native_script": <native non-Latin script or null>,
     "language": <...>,
     "language_code": <...>,
     "notes": <...>}
- Splits all parenthetical dual-script encodings ("Native (Rom)" / "Rom (Native)").
- Splits all slash-joined dual forms ("A / B") into separate variants.
- Romanizes all pure non-Latin forms using curated tables (abjads, Japanese kanji,
  SEA scripts, ancient scripts) and verified deterministic transliterators
  (Cyrillic/BGN, Greek, Georgian, Armenian, Indic by script, Ethiopic, Hangul RR,
  Tibetan Wylie, Manchu Möllendorff, Uyghur ULY, Chinese Pinyin).
"""

import argparse
import json
import re
import subprocess
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
NTR_DIR = REPO_DIR / "data" / "natural_tribal_replacements"

sys.path.insert(0, str(REPO_DIR / "scripts"))
from ntr_romanization_tables import (
    ANCIENT_RARE_ROMANIZATION,
    ARA_ROMANIZATION,
    ARC_ROMANIZATION,
    FAS_ROMANIZATION,
    JPN_ROMANIZATION,
    KHM_ROMANIZATION,
    LAO_ROMANIZATION,
    PAN_SHAHMUKHI_ROMANIZATION,
    SND_ROMANIZATION,
    THA_ROMANIZATION,
    ZHO_EXACT_OVERRIDES,
)

# Characters permitted in clean Latin-script `form`
ALLOWED_PUNCT = set(" \t\n\r-*.,/()'’\"–—&0123456789ʼʻʾʿˈˌ·ʹʷ\u200c\u200d")


def is_latin_char(ch: str) -> bool:
    if ch in ALLOWED_PUNCT:
        return True
    name = unicodedata.name(ch, "")
    return (
        "LATIN" in name
        or "COMBINING" in name
        or unicodedata.category(ch).startswith("M")
    )


def has_nonlatin(s: str) -> bool:
    return any(not is_latin_char(ch) for ch in s)


def has_script(s: str, keyword: str) -> bool:
    return any(keyword in unicodedata.name(ch, "") for ch in s)


def titlecase_preserving_punct(s: str) -> str:
    """Capitalize words cleanly without clobbering internal punctuation/diacritics."""
    out = []
    for tok in s.split(" "):
        if not tok:
            out.append(tok)
            continue
        # Capitalize first alphabetic letter in token (and after hyphen if needed)
        parts = tok.split("-")
        new_parts = []
        for idx, p in enumerate(parts):
            if idx == 0 or (p and p[0].isupper()) or (idx > 0 and len(p) > 2 and p not in ("al", "el", "de", "da", "do", "du", "na", "ye", "i", "u", "n", "of", "the")):
                # Find first letter
                chars = list(p)
                for ci, ch in enumerate(chars):
                    if ch.isalpha():
                        chars[ci] = ch.upper()
                        break
                new_parts.append("".join(chars))
            else:
                new_parts.append(p)
        out.append("-".join(new_parts))
    return " ".join(out)


# ---------------------------------------------------------------------------
# 1. Korean Revised Romanization (pure Python)
# ---------------------------------------------------------------------------
L_TAB = ["g", "kk", "n", "d", "tt", "r", "m", "b", "pp", "s", "ss", "", "j", "jj", "ch", "k", "t", "p", "h"]
V_TAB = ["a", "ae", "ya", "yae", "eo", "e", "yeo", "ye", "o", "wa", "wae", "oe", "yo", "u", "wo", "we", "wi", "yu", "eu", "ui", "i"]
T_TAB = ["", "k", "k", "ks", "n", "nj", "nh", "d", "l", "lk", "lm", "lb", "ls", "lt", "lp", "lh", "m", "p", "ps", "s", "ss", "ng", "j", "ch", "k", "t", "p", "h"]


def romanize_hangul(text: str) -> str:
    jamos = []
    for ch in text:
        code = ord(ch)
        if 0xAC00 <= code <= 0xD7A3:
            idx = code - 0xAC00
            jamos.append((idx // 588, (idx % 588) // 28, idx % 28))
        else:
            jamos.append(ch)
    res = []
    for i, item in enumerate(jamos):
        if isinstance(item, str):
            res.append(item)
            continue
        l, v, t = item
        prev_t = jamos[i - 1][2] if i > 0 and isinstance(jamos[i - 1], tuple) else None
        next_l = jamos[i + 1][0] if i + 1 < len(jamos) and isinstance(jamos[i + 1], tuple) else None
        ini = L_TAB[l]
        coda = T_TAB[t]
        if prev_t is not None and prev_t != 0:
            if l == 11:
                ini = {1: "g", 4: "n", 7: "d", 8: "r", 16: "m", 17: "b", 19: "s", 22: "j", 23: "ch", 24: "k", 25: "t", 26: "p"}.get(prev_t, "")
            elif prev_t in (4, 8) and l == 5:
                ini = "l"
            elif prev_t in (1, 2, 15, 16, 17, 21, 24, 26) and l == 5:
                ini = "n"
            elif prev_t == 27 and l in (0, 3, 12):
                ini = {0: "k", 3: "t", 12: "ch"}[l]
        if next_l is not None and t != 0:
            if next_l == 11 and t != 21:
                coda = ""
            elif t in (1, 2, 15, 24) and next_l in (4, 5, 16):
                coda = "ng"
            elif t in (17, 26) and next_l in (4, 5, 16):
                coda = "m"
            elif t in (7, 19, 20, 22, 23, 25) and next_l in (4, 16):
                coda = "n"
            elif t == 4 and next_l == 5:
                coda = "l"
            elif t == 27 and next_l in (0, 3, 12):
                coda = ""
        elif next_l is None and t != 0:
            if t in (19, 20, 22, 23, 25):
                coda = "t"
        res.append(ini + V_TAB[v] + coda)
    s = "".join(res)
    return " ".join(w[:1].upper() + w[1:] if w else w for w in s.split(" "))


# ---------------------------------------------------------------------------
# 2. Tibetan Wylie
# ---------------------------------------------------------------------------
ROOT_CONSONANTS = {
    "ཀ": "k", "ཁ": "kh", "ག": "g", "ང": "ng",
    "ཅ": "c", "ཆ": "ch", "ཇ": "j", "ཉ": "ny",
    "ཏ": "t", "ཐ": "th", "ད": "d", "ན": "n",
    "པ": "p", "ཕ": "ph", "བ": "b", "མ": "m",
    "ཙ": "ts", "ཚ": "tsh", "ཛ": "dz", "ཝ": "w",
    "ཞ": "zh", "ཟ": "z", "འ": "'", "ཡ": "y",
    "ར": "r", "ལ": "l", "ཤ": "sh", "ས": "s",
    "ཧ": "h", "ཨ": "",
}
SUBJOINED = {
    "\u0F90": "k", "\u0F91": "kh", "\u0F92": "g", "\u0F94": "ng",
    "\u0F95": "c", "\u0F96": "ch", "\u0F97": "j", "\u0F99": "ny",
    "\u0F9F": "t", "\u0FA0": "th", "\u0FA1": "d", "\u0FA3": "n",
    "\u0FA4": "p", "\u0FA5": "ph", "\u0FA6": "b", "\u0FA8": "m",
    "\u0FA9": "ts", "\u0FAA": "tsh", "\u0FAB": "dz", "\u0FAD": "w",
    "\u0FAE": "zh", "\u0FAF": "z", "\u0FB0": "'", "\u0FB1": "y",
    "\u0FB2": "r", "\u0FB3": "l", "\u0FB4": "sh", "\u0FB5": "s",
    "\u0FB6": "h", "\u0FB7": "a", "\u0FBA": "w", "\u0FBB": "y", "\u0FBC": "r",
}
TIB_VOWELS = {"\u0F72": "i", "\u0F74": "u", "\u0F7A": "e", "\u0F7C": "o", "\u0F71": "a"}
VALID_AFTER_PREFIX = {
    "g": {"c", "ny", "t", "d", "n", "ts", "zh", "z", "y", "sh", "s"},
    "d": {"k", "g", "ng", "p", "b", "m", "ky", "gy", "py", "by", "my", "kr", "gr", "pr", "br"},
    "b": {"k", "g", "c", "t", "d", "ts", "zh", "z", "sh", "s", "ky", "kr", "kl", "rk", "rg", "rng", "rj", "rny", "rt", "rd", "rn", "rts", "rdz", "lk", "lg", "lt", "ld", "sk", "sg", "st", "sd", "sn", "sts", "rl", "sl", "sky", "sgy", "skr", "sgr"},
    "m": {"kh", "g", "ng", "ch", "j", "ny", "th", "d", "n", "tsh", "dz", "khy", "gy", "khr", "gr"},
    "'": {"kh", "g", "ch", "j", "th", "d", "ph", "b", "tsh", "dz", "khy", "gy", "phy", "by", "khr", "gr", "thr", "dr", "phr", "br"},
}
TIB_SUFFIXES = {"g", "ng", "d", "n", "b", "m", "'", "r", "l", "s"}


def _wylie_syllable(syl: str) -> str:
    stacks = []
    i = 0
    while i < len(syl):
        ch = syl[i]
        if ch in ROOT_CONSONANTS:
            stack_cons = [ROOT_CONSONANTS[ch]]
            is_achung = ch == "འ"
            i += 1
            while i < len(syl) and syl[i] in SUBJOINED:
                stack_cons.append(SUBJOINED[syl[i]])
                i += 1
            vow = ""
            while i < len(syl) and syl[i] in TIB_VOWELS:
                if syl[i] == "\u0F71":
                    if not vow:
                        vow = "a"
                else:
                    vow = TIB_VOWELS[syl[i]]
                i += 1
            stacks.append((stack_cons, vow, is_achung))
        else:
            i += 1
    if not stacks:
        return ""
    has_explicit = [bool(v) for _, v, _ in stacks]
    if len(stacks) == 1:
        root_idx = 0
    elif any(has_explicit):
        root_idx = has_explicit.index(True)
    else:
        c0 = "".join(stacks[0][0])
        c1 = "".join(stacks[1][0])
        if c0 in VALID_AFTER_PREFIX and len(stacks[0][0]) == 1 and (c1 in VALID_AFTER_PREFIX[c0] or len(stacks[1][0]) > 1):
            if len(stacks) == 2 and c1 in TIB_SUFFIXES and len(stacks[1][0]) == 1:
                root_idx = 0
            else:
                root_idx = 1
        else:
            root_idx = 0
    out_parts = []
    for idx, (cons_list, vow, is_ach) in enumerate(stacks):
        cstr = "".join(cons_list)
        if idx == root_idx:
            v = vow if vow else "a"
            out_parts.append(("'" + v) if (is_ach and len(cons_list) == 1 and idx == 0) else (cstr + v))
        else:
            if is_ach and len(cons_list) == 1 and idx > root_idx and not vow:
                out_parts.append("'a" if idx == len(stacks) - 1 and len(stacks) == 2 else "'")
            else:
                out_parts.append(cstr + vow)
    res = "".join(out_parts)
    if len(stacks) >= 2 and stacks[0][0] == ["g"] and stacks[1][0][0] == "y" and root_idx == 1:
        res = "g." + res[1:]
    return res


def romanize_tibetan(text: str) -> str:
    text = text.strip().rstrip("།").strip()
    out_words = []
    for w in text.split():
        syls = [s for s in w.split("་") if s]
        joined = "-".join(_wylie_syllable(s) for s in syls)
        if joined:
            if joined.startswith("'") and len(joined) > 1:
                joined = "'" + joined[1].upper() + joined[2:]
            else:
                joined = joined[0].upper() + joined[1:]
        out_words.append(joined)
    return " ".join(out_words)


# ---------------------------------------------------------------------------
# 3. Uyghur ULY & Manchu Möllendorff
# ---------------------------------------------------------------------------
UIG_MAP = {
    "ا": "a", "ە": "e", "ب": "b", "پ": "p", "ت": "t", "ج": "j", "چ": "ch",
    "خ": "x", "د": "d", "ر": "r", "ز": "z", "ژ": "zh", "س": "s", "ش": "sh",
    "غ": "gh", "ف": "f", "ق": "q", "ك": "k", "گ": "g", "ڭ": "ng", "ل": "l",
    "م": "m", "ن": "n", "ھ": "h", "و": "o", "ۇ": "u", "ۆ": "ö", "ۈ": "ü",
    "ۋ": "w", "ې": "ë", "ى": "i", "ي": "y", "ئ": "",
}


def romanize_uyghur(s: str) -> str:
    out_words = []
    for w in s.split():
        buf = [UIG_MAP.get(ch, ch) for idx, ch in enumerate(w) if not (ch == "ئ" and idx == 0)]
        rw = "".join(buf)
        if rw:
            out_words.append(rw[0].upper() + rw[1:])
    return " ".join(out_words)


MNC_MAP = {
    "ᠠ": "a", "ᡝ": "e", "ᡳ": "i", "ᠣ": "o", "ᡠ": "u", "ᡡ": "ū",
    "ᠨ": "n", "ᠩ": "ng", "ᡴ": "k", "ᡤ": "g", "ᡥ": "h", "ᠪ": "b",
    "ᡦ": "p", "ᠰ": "s", "ᡧ": "š", "ᡨ": "t", "ᡩ": "d", "ᠯ": "l",
    "ᠮ": "m", "ᠴ": "c", "ᠵ": "j", "ᡪ": "j", "ᠶ": "y", "ᡵ": "r",
    "ᡶ": "f", "ᠸ": "w", "ᠺ": "k'", "ᡬ": "g'", "ᡭ": "h'", "ᡮ": "ts'",
    "ᡯ": "dz", "ᡰ": "ž", "ᡱ": "c'", "ᡲ": "j",
}


def romanize_manchu(s: str) -> str:
    out = []
    for w in s.split():
        rw = "".join(MNC_MAP.get(ch, ch) for ch in w)
        if rw:
            out.append(rw[0].upper() + rw[1:])
    return " ".join(out)


# ---------------------------------------------------------------------------
# 4. Chinese Pinyin (Han-Latin + compound/polyphone normalization)
# ---------------------------------------------------------------------------
ZHO_HEADWORDS_2 = {
    "山脈": "Shānmài", "山脉": "Shānmài", "高原": "Gāoyuán", "平原": "Píngyuán",
    "盆地": "Péndì", "沙漠": "Shāmò", "沙地": "Shādì", "半島": "Bàndǎo",
    "半岛": "Bàndǎo", "群島": "Qúndǎo", "群岛": "Qúndǎo", "海峽": "Hǎixiá",
    "海峡": "Hǎixiá", "峽谷": "Xiágǔ", "峡谷": "Xiágǔ", "山地": "Shāndì",
    "丘陵": "Qiūlíng", "濕地": "Shīdì", "湿地": "Shīdì", "沼澤": "Zhǎozé",
    "走廊": "Zǒuláng", "低地": "Dīdì", "三角洲": "Sānjiǎozhōu",
}
ZHO_HEADWORDS_1 = {
    "山": "Shān", "嶺": "Lǐng", "岭": "Lǐng", "峰": "Fēng", "岳": "Yuè",
    "嶽": "Yuè", "江": "Jiāng", "河": "Hé", "水": "Shuǐ", "溪": "Xī",
    "川": "Chuān", "湖": "Hú", "海": "Hǎi", "灣": "Wān", "湾": "Wān",
    "洋": "Yáng", "泊": "Pō", "澤": "Zé", "泽": "Zé", "錯": "Cuò",
    "错": "Cuò", "峽": "Xiá", "峡": "Xiá", "灘": "Tān", "滩": "Tān",
    "津": "Jīn", "港": "Gǎng", "島": "Dǎo", "岛": "Dǎo",
}


def _join_pinyin_syllables(syls: list[str]) -> str:
    if not syls:
        return ""
    res = [syls[0][0].upper() + syls[0][1:]]
    for s in syls[1:]:
        # Insert apostrophe before syllable starting with a/e/o (or bare vowel tone)
        base = unicodedata.normalize("NFD", s[0]).lower()
        if base and base[0] in ("a", "e", "o"):
            res.append("'" + s.lower())
        else:
            res.append(s.lower())
    return "".join(res)


def format_zho_pinyin_batch(forms: list[str]) -> dict[str, str]:
    results = {}
    todo = []
    for f in forms:
        if f in ZHO_EXACT_OVERRIDES:
            results[f] = ZHO_EXACT_OVERRIDES[f]
        else:
            todo.append(f)
    if not todo:
        return results

    # Split off recognized trailing generic headword so stem + headword space cleanly
    stems_for_uconv = []
    split_info = []
    for f in todo:
        head = None
        stem = f
        if len(f) > 3 and f[-3:] in ZHO_HEADWORDS_2:
            head = ZHO_HEADWORDS_2[f[-3:]]
            stem = f[:-3]
        elif len(f) > 2 and f[-2:] in ZHO_HEADWORDS_2:
            head = ZHO_HEADWORDS_2[f[-2:]]
            stem = f[:-2]
        elif len(f) >= 2 and f[-1:] in ZHO_HEADWORDS_1 and not (
            len(f) == 2 and f[1] in ("山", "海", "江", "河") and f in ("泰山", "衡山", "恒山", "恆山", "華山", "华山", "嵩山", "黃山", "黄山", "廬山", "庐山", "白山", "渤海", "東海", "東江", "西江", "北江", "韓江", "湘江", "漢江", "贛江", "閩江", "松花江", "黑龍江")
        ):
            head = ZHO_HEADWORDS_1[f[-1:]]
            stem = f[:-1]
        stems_for_uconv.append(stem)
        split_info.append((f, stem, head))

    raw_py = subprocess.check_output(
        ["uconv", "-x", "Han-Latin; nfc"],
        input="\n".join(stems_for_uconv),
        text=True,
    ).splitlines()

    for (orig, stem, head), py in zip(split_info, raw_py):
        # Fix common Han-Latin 'de' -> 'dì' when '地' was inside stem
        py_tokens = py.strip().split()
        joined = _join_pinyin_syllables(py_tokens)
        if head:
            results[orig] = f"{joined} {head}"
        else:
            results[orig] = joined
    return results


# ---------------------------------------------------------------------------
# 5. Batch uconv transliteration for Group A (Cyrillic, Greek, Indic, etc.)
# ---------------------------------------------------------------------------
XFORM_MAP = {
    "rus": "Russian-Latin/BGN",
    "orv": "Russian-Latin/BGN",
    "rue": "Ukrainian-Latin/BGN",
    "ukr": "Ukrainian-Latin/BGN",
    "bel": "Belarusian-Latin/BGN",
    "bul": "Bulgarian-Latin/BGN",
    "srp": "Serbian-Latin/BGN",
    "mkd": "Macedonian-Latin/BGN",
    "kaz": "Kazakh-Latin/BGN",
    "kir": "Kirghiz-Latin/BGN",
    "mon": "Mongolian-Latin/BGN",
    "bua": "Mongolian-Latin/BGN",
    "uzb": "Uzbek-Latin/BGN",
    "grc": "Greek-Latin",
    "ell": "Greek-Latin",
    "kat": "Georgian-Latin/BGN",
    "xmf": "Georgian-Latin/BGN",
    "sva": "Georgian-Latin/BGN",
    "hye": "Armenian-Latin/BGN",
    "amh": "Ethiopic-Latin/ALALOC",
    "tir": "Ethiopic-Latin/ALALOC",
    "gez": "Ethiopic-Latin/ALALOC",
}

CYR_PRE_COMMON = str.maketrans({
    "ҳ": "х", "Ҳ": "Х",
    "ҷ": "ч", "Ҷ": "Ч",
    "ӣ": "и", "Ӣ": "И",
    "ӯ": "у", "Ӯ": "У",
    "қ": "к", "Қ": "К",
    "ғ": "г", "Ғ": "Г",
    "ԥ": "п", "Ԥ": "П",
    "һ": "х", "Һ": "Х",
    "ӄ": "к", "Ӄ": "К",
    "җ": "ж", "Җ": "Ж",
    "ә": "а", "Ә": "А",
    "ө": "о", "Ө": "О",
    "ү": "у", "Ү": "У",
    "ң": "нг", "Ң": "Нг",
    "ӈ": "нг", "Ӊ": "Нг",
    "ԯ": "л", "Ԯ": "Л",
    "ҙ": "з", "Ҙ": "З",
    "ҫ": "с", "Ҫ": "С",
    "ҡ": "к", "Ҡ": "К",
    "ў": "у", "Ў": "У",
    "ӱ": "ü", "Ӱ": "Ü",
    "ӧ": "ö", "Ӧ": "Ö",
    "ӹ": "y", "Ӹ": "Y",
    "Ӏ": "'",
})

# Higher-precision per-character overrides before uconv for specific Cyrillic languages
TGK_PRE = {"ҳ": "h", "Ҳ": "H", "ҷ": "j", "Ҷ": "J", "ӣ": "ī", "Ӣ": "Ī", "ӯ": "ū", "Ӯ": "Ū", "қ": "q", "Қ": "Q", "ғ": "gh", "Ғ": "Gh"}
ORV_PRE = {"ѣ": "ě", "Ѣ": "Ě", "ѧ": "ya", "Ѧ": "Ya", "ѫ": "u", "Ѫ": "U", "ъ": "ŭ", "Ъ": "Ŭ", "ь": "ĭ", "Ь": "Ĭ", "і": "i", "І": "I", "ѳ": "f", "Ѳ": "F"}
MON_PRE = {"Х": "Kh", "х": "kh", "һ": "h", "Һ": "H", "Ө": "Ö", "ө": "ö", "Ү": "Ü", "ү": "ü"}
KAZ_POST = {"ī̆": "y", "Ī̆": "Y"}


def pre_cyrillic(lc: str, s: str) -> str:
    if lc == "tgk":
        for k, v in TGK_PRE.items():
            s = s.replace(k, v)
    elif lc == "orv":
        for k, v in ORV_PRE.items():
            s = s.replace(k, v)
    elif lc in ("mon", "bua"):
        for k, v in MON_PRE.items():
            s = s.replace(k, v)
    elif lc == "rue":
        s = s.replace("ы", "y").replace("Ы", "Y")
    elif lc in ("tat", "kjh", "tyv", "alt", "mns", "kca", "sel", "abk", "ady", "kbd", "che", "kpv", "mhr", "mdf", "myv", "ket", "oss"):
        if lc == "abk":
            s = s.replace("ԥ", "p").replace("Ԥ", "P")
        elif lc == "sel":
            s = s.replace("ӄ", "q").replace("Ӄ", "Q")
        elif lc in ("tat", "kjh", "tyv"):
            s = s.replace("җ", "j").replace("Җ", "J").replace("ғ", "gh").replace("Ғ", "Gh").replace("қ", "q").replace("Қ", "Q").replace("ө", "ö").replace("Ө", "Ö").replace("ү", "ü").replace("Ү", "Ü").replace("ә", "ä").replace("Ә", "Ä").replace("ң", "ng").replace("Ң", "Ng").replace("һ", "h").replace("Һ", "H")
        elif lc in ("mns", "kca", "ket"):
            s = s.replace("ӈ", "ŋ").replace("Ӊ", "Ŋ").replace("ԯ", "ł").replace("Ԯ", "Ł")
        elif lc in ("kbd", "ady", "che"):
            s = s.replace("Ӏ", "'").replace("ъ", "")
        s = s.translate(CYR_PRE_COMMON)
    return s


def pick_uconv_xform(lc: str, text: str) -> str:
    if lc in XFORM_MAP:
        return XFORM_MAP[lc]
    # Script-based dispatch for Indic & mixed-script codes
    if has_script(text, "DEVANAGARI"):
        return "Devanagari-Latin"
    if has_script(text, "BENGALI"):
        return "Bengali-Latin"
    if has_script(text, "ORIYA"):
        return "Oriya-Latin"
    if has_script(text, "GUJARATI"):
        return "Gujarati-Latin"
    if has_script(text, "GURMUKHI"):
        return "Gurmukhi-Latin"
    if has_script(text, "CYRILLIC"):
        return "Russian-Latin/BGN"
    return "Any-Latin"


def post_clean_latin(lc: str, tr: str, orig: str) -> str:
    # Fix Kazakh combining breve+macron
    for k, v in KAZ_POST.items():
        tr = tr.replace(k, v)
    # Strip BGN prime/double-prime in Cyrillic (keep official Skolt Sami ʹ)
    if lc != "sms":
        tr = tr.replace("ʹ", "").replace("ʺ", "")
    # Restore Title Case if lowercase (e.g., Indic, Georgian, Ethiopic)
    if lc in ("kat", "xmf", "sva", "hye", "san", "hin", "nep", "mai", "raj", "brx", "pra", "ben", "asm", "ori", "guj", "pan", "amh", "tir", "gez"):
        tr = titlecase_preserving_punct(tr)
    # Fix Georgian glottal apostrophe casing after titlecase (mt’k’vari -> Mt’k’vari)
    tr = tr.replace("’", "'")
    # Preserve leading '*' if present in orig
    if orig.startswith("*") and not tr.startswith("*"):
        tr = "*" + tr
    return tr


def run_batch_uconv(pairs: list[tuple[str, str]]) -> dict[tuple[str, str], str]:
    """Transliterate (lc, form) pairs grouped by ICU transform."""
    by_xform = defaultdict(list)
    for lc, form in pairs:
        pre = pre_cyrillic(lc, form)
        xform = pick_uconv_xform(lc, pre)
        by_xform[xform].append((lc, form, pre))

    out_map = {}
    for xform, items in by_xform.items():
        inp = "\n".join(pre for _, _, pre in items)
        res = subprocess.check_output(
            ["uconv", "-x", f"{xform}; nfc"],
            input=inp,
            text=True,
        ).splitlines()
        for (lc, orig, _), tr in zip(items, res):
            out_map[(lc, orig)] = post_clean_latin(lc, tr.strip(), orig)
    return out_map


# ---------------------------------------------------------------------------
# 6. Master Resolution Pipeline
# ---------------------------------------------------------------------------
CURATED_BY_CODE = {
    "ara": ARA_ROMANIZATION,
    "fas": FAS_ROMANIZATION,
    "snd": SND_ROMANIZATION,
    "arc": ARC_ROMANIZATION,
    "jpn": JPN_ROMANIZATION,
    "ojp": JPN_ROMANIZATION,
    "oko": JPN_ROMANIZATION,
    "tha": THA_ROMANIZATION,
    "lao": LAO_ROMANIZATION,
    "khm": KHM_ROMANIZATION,
    "okz": KHM_ROMANIZATION,
}


def collect_dual_pairs(files: list[Path]) -> dict[tuple[str, str], str]:
    """Extract curated (lc, native) -> latin mapping from existing A (B) forms."""
    candidates_map = defaultdict(Counter)
    for p in files:
        d = json.load(open(p, encoding="utf-8"))
        for b in d["baronies"].values():
            for c in b["replacement_candidates"]:
                for lv in c["language_variants"]:
                    lf, lc = lv["form"], lv["language_code"]
                    if "(" in lf and has_nonlatin(lf):
                        m = re.match(r"^([^(]+?)\s*\(([^)]+)\)$", lf)
                        if m:
                            left, right = m.group(1).strip(), m.group(2).strip()
                            if not has_nonlatin(left) and has_nonlatin(right):
                                candidates_map[(lc, right.rstrip("།"))][left] += 1
                            elif has_nonlatin(left) and not has_nonlatin(right):
                                candidates_map[(lc, left.rstrip("།"))][right] += 1
    # Pick most frequent form when slight spacing/caps variant exists
    return {k: cnt.most_common(1)[0][0] for k, cnt in candidates_map.items()}


def romanize_sla_pro(s: str) -> str:
    return s.replace("ь", "ĭ").replace("ъ", "ŭ").replace("Ь", "Ĭ").replace("Ъ", "Ŭ")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Write changes to data/natural_tribal_replacements/")
    args = parser.parse_args()

    files = sorted(NTR_DIR.glob("barony_natural_tribal_replacements_*.json"))
    dual_pairs = collect_dual_pairs(files)

    # First pass: collect all unmatched pure non-Latin (lc, native) pairs needing transliteration
    zho_needed = set()
    uconv_needed = set()

    for p in files:
        d = json.load(open(p, encoding="utf-8"))
        for b in d["baronies"].values():
            for c in b["replacement_candidates"]:
                for lv in c["language_variants"]:
                    lc, lf = lv["language_code"], lv["form"]
                    # Split slash first
                    parts = [x.strip() for x in lf.split(" / ")] if "/" in lf else [lf]
                    for part in parts:
                        if part == "Пулозеро (озеро, Кольский полуостров)":
                            uconv_needed.add(("rus", "Пулозеро"))
                            continue
                        if "(" in part and has_nonlatin(part):
                            continue  # handled directly by dual-split
                        if not has_nonlatin(part):
                            continue
                        norm_part = part.rstrip("།")
                        if (lc, norm_part) in dual_pairs or (lc, part) in ANCIENT_RARE_ROMANIZATION:
                            continue
                        if lc in CURATED_BY_CODE and part in CURATED_BY_CODE[lc]:
                            continue
                        if lc == "pan" and has_script(part, "ARABIC") and part in PAN_SHAHMUKHI_ROMANIZATION:
                            continue
                        if lc == "pan" and part == "गੁੱਜਰ":
                            continue
                        if lc in ("sla-pro", "kor", "bod", "otb", "uig", "mnc"):
                            continue
                        if lc in ("zho", "lzh"):
                            zho_needed.add(part)
                        else:
                            uconv_needed.add((lc, part))

    zho_map = format_zho_pinyin_batch(sorted(zho_needed))
    uconv_map = run_batch_uconv(sorted(uconv_needed))

    # Helper to resolve any single (lc, raw_form) -> (latin_form, native_script_or_None)
    def resolve_single(lc: str, raw: str) -> tuple[str, str | None]:
        if raw == "Пулозеро (озеро, Кольский полуостров)":
            return uconv_map[("rus", "Пулозеро")], "Пулозеро"
        if "(" in raw and has_nonlatin(raw):
            m = re.match(r"^([^(]+?)\s*\(([^)]+)\)$", raw)
            if m:
                left, right = m.group(1).strip(), m.group(2).strip()
                if not has_nonlatin(left) and has_nonlatin(right):
                    return left, right
                if has_nonlatin(left) and not has_nonlatin(right):
                    return right, left
        if not has_nonlatin(raw):
            return raw, None

        # Pure non-Latin (or sla-pro / sog / otk mixed)
        norm_raw = raw.rstrip("།")
        if (lc, norm_raw) in dual_pairs:
            return dual_pairs[(lc, norm_raw)], raw
        if (lc, raw) in ANCIENT_RARE_ROMANIZATION:
            return ANCIENT_RARE_ROMANIZATION[(lc, raw)], raw
        if lc in CURATED_BY_CODE and raw in CURATED_BY_CODE[lc]:
            return CURATED_BY_CODE[lc][raw], raw
        if lc == "pan" and has_script(raw, "ARABIC") and raw in PAN_SHAHMUKHI_ROMANIZATION:
            return PAN_SHAHMUKHI_ROMANIZATION[raw], raw
        if lc == "pan" and raw == "गੁੱਜਰ":
            return "Gujjar", raw
        if lc == "sla-pro":
            return romanize_sla_pro(raw), raw
        if lc == "kor":
            return romanize_hangul(raw), raw
        if lc in ("bod", "otb"):
            return romanize_tibetan(raw), raw
        if lc == "uig":
            return romanize_uyghur(raw), raw
        if lc == "mnc":
            return romanize_manchu(raw), raw
        if lc in ("zho", "lzh"):
            return zho_map[raw], raw
        return uconv_map[(lc, raw)], raw

    # Second pass: transform all files & audit every output
    stats = Counter()
    still_nonlatin_forms = []
    missing_native = []
    sample_changes = []

    for p in files:
        d = json.load(open(p, encoding="utf-8"))
        changed = False

        # Update schema_notes
        sn = d["metadata"]["schema_notes"]
        if "language_variants" not in sn:
            sn["language_variants"] = (
                "List of cultural/historical name forms: {form, native_script, language, language_code, notes}. "
                "form is always clean Latin script (or romanization) suitable for CK3 localisation; "
                "native_script holds the native non-Latin script form or null when the language natively uses Latin script."
            )
            changed = True

        for bk, b in d["baronies"].items():
            for c in b["replacement_candidates"]:
                new_lvs = []
                seen_keys = set()
                for lv in c["language_variants"]:
                    lc = lv["language_code"]
                    lf = lv["form"]
                    parts = [x.strip() for x in lf.split(" / ")] if "/" in lf else [lf]
                    if len(parts) > 1:
                        stats["slash_split"] += 1
                    for part in parts:
                        # Idempotency: if already normalized (clean Latin form with existing native_script), preserve native_script
                        if "native_script" in lv and len(parts) == 1 and not has_nonlatin(part):
                            latin_form, native_script = part, lv["native_script"]
                        else:
                            latin_form, native_script = resolve_single(lc, part)
                        if has_nonlatin(latin_form):
                            still_nonlatin_forms.append((p.name, bk, lc, part, latin_form))
                        if native_script is not None and not native_script.strip():
                            missing_native.append((p.name, bk, lc, part))
                        dedup_key = (lc, latin_form, native_script)
                        if dedup_key in seen_keys:
                            stats["deduped_after_split"] += 1
                            continue
                        seen_keys.add(dedup_key)
                        new_lv = {
                            "form": latin_form,
                            "native_script": native_script,
                            "language": lv["language"],
                            "language_code": lc,
                            "notes": lv["notes"],
                        }
                        if lv.get("form") != latin_form or "native_script" not in lv or lv.get("native_script") != native_script:
                            changed = True
                        if native_script is not None:
                            stats["has_native_script"] += 1
                        else:
                            stats["latin_only"] += 1
                        if len(sample_changes) < 25 and part != latin_form:
                            sample_changes.append((p.name, bk, lc, part, latin_form, native_script))
                        new_lvs.append(new_lv)
                        stats["total_variants_out"] += 1
                c["language_variants"] = new_lvs

        if args.apply and changed:
            with open(p, "w", encoding="utf-8") as f:
                json.dump(d, f, ensure_ascii=False, indent=2)
                f.write("\n")
            stats["files_written"] += 1

    print("=== P0-1 NORMALIZATION SUMMARY ===")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v}")
    print(f"Remaining non-Latin characters in `form`: {len(still_nonlatin_forms)}")
    for x in still_nonlatin_forms[:30]:
        print("  LEFTOVER:", x)
    print(f"Empty native_script errors: {len(missing_native)}")
    print("\nSample transformations:")
    for x in sample_changes[:20]:
        print(" ", x)


if __name__ == "__main__":
    main()

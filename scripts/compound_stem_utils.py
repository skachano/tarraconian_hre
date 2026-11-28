#!/usr/bin/env python3
"""
Shared multi-word stem reduction utilities for Stages 2, 3, 4, and 6 of the
Tarraconian Barony Naming Pipeline.

Enforces the Single-Stem Compounding Law: bound derivational suffixes
(`-burch`, `-stat`, `-tempel`, `-ostrog`, `-la`, etc.) may only attach to a
single phonological word (`" " not in stem`).
"""

from __future__ import annotations

import re
import unicodedata

# Trailing Arabic postnominal adjectives stripped BEFORE head generics so
# `Al-Irk al-Scharkî al-Kabîr` -> `Al-Irk` -> `Irk` and `al-Nîl al-Abyat` -> `Nîl`.
ARABIC_ADJ_TAIL = re.compile(
    r"\b(?:al-)?(?:"
    r"Kabir|Saghir|Sagir|Scharki|Sharki|Sharqi|Garbi|Gharbi|"
    r"Scharkiyya|Sharqiyya|Garbiyya|Gharbiyya|Abyat|Abyad|Azrak|Azraq|"
    r"Azam|Bahriyya|Dschunubiyya|Schamaliyya|Aswad|Ahmar|Kubra|Sughra"
    r")$",
    re.I,
)

# Unified diacritic-insensitive leading geographic/ethnolinguistic classifiers & articles.
EXPANDED_HEAD_PAT = re.compile(
    r"^(?:"
    r"(?:Northern|Southern|Eastern|Western)\s+border\s+of|"
    r"Gunung\s+Bukit|Doi\s+Luang|Doi\s+Phu|Phou\s+Luang|Phou\s+Khao|Mae\s+Nam|Lam\s+Nam|"
    r"Thi\s+Rap\s+Sung|Thio\s+Khao\s+Phu|Thio\s+Khao|Chuor\s+Phnom|Chhoung\s+Samut|"
    r"Al-Bahr\s+al-|Al-Sahra\s+al-|Al-Wahat\s+al-|Al-Rimal\s+al-|"
    r"Schatt\s+al-|Shatt\s+al-|Chott\s+al-|Hadabat\s+al-|Hawr\s+al-|"
    r"Jazirat\s+al-|Dschazirat\s+al-|Batn\s+al-|Kudyat\s+al-|Umm\s+al-|Ras\s+al-|"
    r"Milima\s+ya|Mfereji\s+wa|Monts\s+du|Monts\s+de|Plateau\s+de|Falaise\s+de|"
    r"Massif\s+des?|Mer\s+de|Golfu\s+de|Strasse\s+von|Ports?\s+de|Portz\s+de|Koad\s+ar|Koat\s+ar|"
    r"Kipot\s+ng|Golpo\s+ng|Gulpo\s+sa|Look\s+ng|Lawa\s+ng|Tangway\s+ng|Suba\s+sang|Suba\s+sa|Isla\s+sa|"
    r"Cnoic\s+na|Sliav\s+an|Sliabh\s+an|Slieve|Carrick|Monadh|Uisge|Bog\s+of|"
    r"Daryatsche-?ye|Daryatsche-?je|Daryacheh?-?ye|Hamun-?e|Dasht-?e|Rud-?e|Kuh-?e|"
    r"Nahr\s+al-|Nahr|Wadi|Bahr\s+al-|Bahr|Jabal|Jibal|Khalij|Munkhafad|"
    r"Qatorkuhi|Vodii|Puszcza|Fforest|Fadamar|"
    r"Laut|Dagat|Sungai|Bukit|Bukid|Bulkang|Gunung|Gunong|Pegunungan|Kepulauan|Semenanjung|"
    r"Danau|Selat|Pulau|Teluk|Tanjung|Kuala|Muara|Suku|Urang|Bundok|"
    r"Foho|Mota|Kali|Batang|Tasik|Tasich|Lanaw|Krueng|Segenting|Song|Nui|Ao|Prey|Daen|"
    r"Boeung|Stueng|Tonle|Mae|Nam|Doi|Phu|Khao|"
    r"Webi|Kogin|Mto|Odo|Laga|Ilog|Asif\s+n|Adrar\s+n|Aglan\s+n|Tasili\s+n|Asif|Adrar|Muntii|Muntzii|"
    r"Shatt|Schatt|Chott|Hadabat|Hawr|Chawr|Khawr|Jazirat|Dschazirat|Juzur|Dschuzur|Batn|Kudyat|Ras|"
    r"Loch(?:\s+(?:na|an|a'))?|Glen|Strath|Port|Plain\s+of|Gulf\s+of|Bay\s+of|Bight\s+of|Strait\s+of|"
    r"Lake|Mount|Mountain|River|Island|Inner|"
    r"Ozero|Reka|Gora|Zaliv|Ostrov|"
    r"Rio(?:\s+Grande\s+de|\s+de(?:\s+(?:l[ao]s?|el))?)?|Lago|Monte|Sierra(?:\s+de(?:\s+(?:l[ao]s?|el))?)?|"
    r"Sliabh|Sliav|Cnoc|Bae|Sistema|Meseta|Urbs|Ri-o|"
    r"Omo|Clann|Ait|Bani|Skitike|Scythian|Magna|Grand|Grant|Hornja|Uttara|"
    r"Am|An|Y|Al|El|La|Le|Les|Des"
    r")\b",
    re.I,
)

# Unified diacritic-insensitive trailing geographic/administrative/ethnonym classifiers.
EXPANDED_TAIL_PAT = re.compile(
    r"\b(?:"
    r"people|tribe|group|river|lake|sea|mountain|mountains|range|hills|hill|plain|basin|valley|"
    r"gulf|bay|strait|island|islands|peninsula|channel|upland|uplands|lowland|lowlands|levels|"
    r"water|bight|commandery|prefecture|province|district|downs|delta|"
    r"vozvyshennost|wozwyschennost|vysochyna|khrebet|dolina|reka|bardzravandak|hegyseg|"
    r"srnkhala|schrngchala|kafetana\s+botawoc|kalquligi|"
    r"Gol|Nuruu|Nuru|Ula|Uul|Ul|Nuur|Nur|Kuh|Nadi|Yoma|Denu|Doab|Pahariya|"
    r"Vrchy|Werchy|Taung|Tscho|Tsho|Take|Oypaty|Tizmisi|Eremos|Central|Prebetic|"
    r"Slovene|Slowene|Dschun|Jun|Dao|Dschimi|Jimi"
    r")$",
    re.I,
)

PREP_TAIL_PAT = re.compile(
    r"\s+(?:di|de|do|del|du|des|da|ad|at|von|am|im|an\s+der|no|na|ibn|bin)\s+.+$",
    re.I,
)

STOP_TOKENS = {
    "al", "el", "an", "am", "y", "n", "no", "de", "di", "do",
    "des", "du", "da", "von", "a", "i", "e", "ar", "na", "at", "ad",
}

HEAD_INITIAL_FAMILIES = {
    "arabic", "berber", "austronesian", "mon_khmer", "tai_hmong",
    "goidelic", "brythonic", "ibero_romance", "gallo_romance",
    "italo_romance", "occitano_catalan", "ethiopic_cushitic",
    "west_central_african", "east_bantu_swahili",
}

BOUND_TARR_SUFFIX_RE = re.compile(
    r"(?:burch|stat|stein|tempel|veste|meschit|kirchen|marct|ribât|"
    r"hâven|wîe|wart|berch|march|zelle|flôz|wal|castel|klûse|vurt|"
    r"munde|palz|tôr)$",
    re.I,
)


def strip_diacritics(s: str) -> str:
    """Fold diacritics and Semitic/special letters to ASCII for classifier matching."""
    nfd = unicodedata.normalize("NFD", s)
    out = "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn")
    return (
        out.replace("ʾ", "")
        .replace("ʿ", "")
        .replace("’", "'")
        .replace("ł", "l")
        .replace("Ł", "L")
        .replace("đ", "d")
        .replace("Đ", "D")
        .replace("ß", "ss")
    )


def _alpha_len(s: str) -> int:
    return len(re.sub(r"[^A-Za-zÀ-ɏ]", "", s))


def match_prefix_diacritic_insensitive(s: str, pat: re.Pattern[str]) -> str | None:
    """Match a leading classifier on a diacritic-stripped mirror while slicing original tokens."""
    tokens = s.split()
    if len(tokens) < 2:
        return None
    norm = " ".join(strip_diacritics(t) for t in tokens)
    m = pat.match(norm)
    if not m:
        return None
    matched_words = len(m.group(0).strip().split())
    rest = " ".join(tokens[matched_words:]).strip()
    # Guard against exposing illicit word-initial nasal+obstruent clusters (e.g. 'Asif n Nfis' -> 'Nfis')
    if _alpha_len(rest) >= 3 and not re.match(r"^(?:nf|ng|mb|nd|nk|nt|nz|mp|mg|mv|ml|mr|mn)", strip_diacritics(rest), re.I):
        return rest
    return None


def match_suffix_diacritic_insensitive(s: str, pat: re.Pattern[str]) -> str | None:
    """Match a trailing classifier on a diacritic-stripped mirror while slicing original tokens."""
    tokens = s.split()
    if len(tokens) < 2:
        return None
    norm = " ".join(strip_diacritics(t) for t in tokens)
    m = pat.search(norm)
    if not m:
        return None
    matched_words = len(m.group(0).strip().split())
    rest = " ".join(tokens[:-matched_words]).strip(" -")
    if _alpha_len(rest) >= 3:
        return rest
    return None


def strip_leading_al_prefix(tok: str) -> str:
    """Strip residual Arabic 'Al-' / 'al-' prefix on a single compound stem when >= 3 chars remain."""
    if tok.lower().startswith("al-") and _alpha_len(tok[3:]) >= 3:
        t = tok[3:]
        return t[:1].upper() + t[1:]
    return tok


def strip_classifiers_diacritic_insensitive(s: str, *, max_passes: int = 3) -> str:
    """Run Arabic postnominal adjective + leading/trailing geographic classifier stripping."""
    cur = s.strip()
    if " " not in cur:
        return cur
    for _ in range(max_passes):
        nxt_adj = match_suffix_diacritic_insensitive(cur, ARABIC_ADJ_TAIL)
        if nxt_adj and nxt_adj != cur:
            cur = nxt_adj
        else:
            break
    for _ in range(max_passes):
        nxt = match_prefix_diacritic_insensitive(cur, EXPANDED_HEAD_PAT)
        if nxt and nxt != cur:
            cur = nxt
            continue
        nxt2 = match_suffix_diacritic_insensitive(cur, EXPANDED_TAIL_PAT)
        if nxt2 and nxt2 != cur:
            # Also trim Slavic relational adjective endings exposed by stripping an ethnonym tail (e.g. Ilmenskiye slovene -> Ilmen)
            nxt2 = re.sub(r"([A-Za-zÀ-ɏ]{3,})(?:skoye|skaya|skiye|skiy|sky)$", r"\1", nxt2, flags=re.I)
            cur = nxt2
            continue
        break
    return cur


def reduce_stem_for_suffixing(
    stem: str,
    *,
    is_ruler_eponym: bool = False,
    morphology_family: str = "",
) -> tuple[str, str]:
    """
    Reduce any multi-word stem to a single phonological word before bound suffixation.

    Returns `(reduced_stem, rule_applied)`.
    """
    s = stem.strip()
    if not s or " " not in s:
        return strip_leading_al_prefix(s), "already_single"

    # 1. Ruler eponyms: extract personal/clan head token rather than Dynasty + GivenName
    if is_ruler_eponym:
        tok = s.split()[-1]
        return strip_leading_al_prefix(tok), "ruler_eponym_head"

    # 2 & 3. Arabic postnominal adjectives + diacritic-insensitive generic/article stripping
    cur = strip_classifiers_diacritic_insensitive(s, max_passes=3)
    if " " not in cur:
        return strip_leading_al_prefix(cur), "generic_stripped"

    # 4. Prepositional tail clipping (Alba di Monferrato -> Alba, Asama no Take -> Asama)
    m_prep = PREP_TAIL_PAT.search(cur)
    if m_prep:
        head = cur[: m_prep.start()].strip()
        if head and _alpha_len(head) >= 3:
            cur = head
            if " " not in cur:
                return strip_leading_al_prefix(cur), "prep_tail_clipped"

    # 5. Short opaque 2-word pair -> univerbate (no hyphens, no stop-words, <= 11 letters)
    toks = cur.split()
    if (
        len(toks) == 2
        and "-" not in cur
        and _alpha_len(cur) <= 11
        and not any(t.lower() in STOP_TOKENS for t in toks)
    ):
        fused = toks[0] + toks[1][:1].lower() + toks[1][1:]
        return strip_leading_al_prefix(fused), "univerbated_short_pair"

    # 6. Head-select salient proper token based on language family headedness
    content_toks = [t for t in toks if t.lower() not in STOP_TOKENS] or toks
    is_head_initial = (morphology_family or "").lower() in HEAD_INITIAL_FAMILIES
    picked = content_toks[-1] if is_head_initial else content_toks[0]
    return strip_leading_al_prefix(picked), (
        "head_select_last" if is_head_initial else "head_select_first"
    )

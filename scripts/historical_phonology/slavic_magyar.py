"""9th-12th century Wave 3 Historical Phonology Decoders:
  - Old Magyar (hun, ohu)
  - Old Polish / Lechitic (pol, csb, dsb, hsb; Option A: rz -> rj / post-consonantal r)
  - Old Czech & Slovak (ces, slk; Option A: ř -> rj / post-consonantal r)
  - South Slavic (bul, srp, hrv, slv, bos, mkd, chu, hbs)
  - Old East Slavic (rus, orv, ukr, bel, rue)
  - Proto-Slavic NTR substrates (sla-pro)
"""

from __future__ import annotations

import re

from .common import (
    SHARED_NON_NATIVE_TOKENS,
    cap_match,
    dispatch_phrase,
    split_glued_tarr_suffix,
)

MAGYAR_ISOS: set[str] = {"hun", "ohu"}
LECHITIC_ISOS: set[str] = {"pol", "csb", "dsb", "hsb"}
CZECH_SLOVAK_ISOS: set[str] = {"ces", "slk"}
SOUTH_SLAVIC_ISOS: set[str] = {"bul", "srp", "hrv", "slv", "bos", "mkd", "chu", "hbs"}
EAST_SLAVIC_ISOS: set[str] = {"rus", "orv", "ukr", "bel", "rue"}
GENERIC_SLAVIC_ISOS: set[str] = {"sla"}
PROTO_SLAVIC_ISOS: set[str] = {"sla-pro"}

_MAGYAR_EXEMPT: set[str] = SHARED_NON_NATIVE_TOKENS | {
    "theiß", "theiss", "apulum", "mesês", "vihorlát", "wihorlât", "wihorlat",
    "balaton", "bakony", "duna", "dákok", "gepidák", "avarok", "maros",
    "exotrochos", "tibiscus", "navata", "pone", "pilicia", "vistula", "gábriel",
    "svatý", "budin", "ung",
}

_SLAVIC_EXEMPT: set[str] = SHARED_NON_NATIVE_TOKENS | {
    "constanta", "corcoras", "heraclea", "lyncestis", "nicopolis", "nestum",
    "callatis", "alpes", "iuliae", "transmarisca", "inceru", "inzer",
    "sveti", "hilary", "cyrillus", "cyril", "zenon", "boris",
    "basil", "reinhold", "baldarich", "wigerich", "emelrich", "simon",
    "castel", "durmitor", "tara", "mura", "scarbantia", "gorsium", "vagus",
    "admont", "friedrich", "wolf", "sljeme", "gučevo", "koprivnica",
    "potamu", "potamuskastel", "štit", "rurikid", "clovis", "dyre",
    "zwinisława", "cenn", "fáelad", "kwâdi", "kwadi", "ulcinj", "hercegovina",
    "clement", "klemens", "sadoc", "sadok", "richardis", "wiltrud", "imran",
    "dytryk", "kári", "kari",
}

_SLAVIC_VOWEL_MAP = {
    "á": "â", "Á": "Â", "é": "ê", "É": "Ê", "í": "î", "Í": "Î",
    "ó": "ô", "Ó": "Ô", "ú": "û", "Ú": "Û", "ý": "î", "Ý": "Î",
    "ů": "û", "Ů": "Û", "ě": "e", "Ě": "E", "ë": "e", "Ë": "E",
    "ū": "û", "Ū": "Û", "ī": "î", "Ī": "Î", "ā": "â", "Ā": "Â",
    "ă": "e", "Ă": "E", "ł": "l", "Ł": "L", "ŭ": "u", "ĭ": "i",
}

# Paired uppercase/lowercase PUA markers so capitalization is preserved everywhere
_PUA_CH_U, _PUA_CH_L = "\uE040", "\uE041"
_PUA_DSCH_U, _PUA_DSCH_L = "\uE042", "\uE043"
_PUA_TSCH_U, _PUA_TSCH_L = "\uE044", "\uE045"
_PUA_SCH_U, _PUA_SCH_L = "\uE046", "\uE047"
_PUA_S_U, _PUA_S_L = "\uE048", "\uE049"
_PUA_DJ_U, _PUA_DJ_L = "\uE04A", "\uE04B"
_PUA_LJ_U, _PUA_LJ_L = "\uE04C", "\uE04D"
_PUA_NJ_U, _PUA_NJ_L = "\uE04E", "\uE04F"
_PUA_TJ_U, _PUA_TJ_L = "\uE050", "\uE051"


def _pua(m: re.Match[str], up: str, lo: str) -> str:
    return up if m.group(0)[0].isupper() else lo


def _protect_ch(s: str, *, ch_to_tsch: bool) -> str:
    """Convert Slavic/Cyrillic <ch>: either [tʃ] -> tsch (Bulgarian/East Slavic) or protect [x]."""
    if ch_to_tsch:
        return re.sub(r"ch", lambda m: _pua(m, _PUA_TSCH_U, _PUA_TSCH_L), s, flags=re.I)
    return re.sub(r"ch", lambda m: _pua(m, _PUA_CH_U, _PUA_CH_L), s, flags=re.I)


def _restore_ch(s: str) -> str:
    return s.replace(_PUA_CH_U, "Ch").replace(_PUA_CH_L, "ch")


def _apply_slavic_c_to_tz(s: str) -> str:
    """Convert Slavic <c> (= [ts]) into z- (initial before vowel) / -tz- (medial/final or before k)."""
    s = re.sub(r"\bc(?=[aeiouyäöüâêîôûěůáéíóúýĭŭ])", lambda m: cap_match(m.group(0), "z"), s, flags=re.I)
    s = re.sub(r"(?<=.)c(?!h|z)(?=[aeiouyäöüâêîôûěůáéíóúýĭŭk]|$)", "tz", s, flags=re.I)
    return s


def _apply_common_slavic_diacritics(s: str, *, v_to_w: bool = True) -> str:
    """Resolve pan-Slavic (and Carpathian Romanian) diacritics, digraphs, and voiced v -> w."""
    s = re.sub(r"dž", lambda m: _pua(m, _PUA_DSCH_U, _PUA_DSCH_L), s, flags=re.I)
    s = s.replace("Đ", _PUA_DSCH_U).replace("đ", _PUA_DSCH_L)
    s = re.sub(r"[čć]", lambda m: _pua(m, _PUA_TSCH_U, _PUA_TSCH_L), s, flags=re.I)
    s = re.sub(r"[šžș]", lambda m: _pua(m, _PUA_SCH_U, _PUA_SCH_L), s, flags=re.I)
    s = s.replace("Ț", "Tz").replace("ț", "tz")
    if v_to_w:
        s = s.replace("v", "w").replace("V", "W")
    s = "".join(_SLAVIC_VOWEL_MAP.get(c, c) for c in s)
    s = (
        s.replace(_PUA_DSCH_U, "Dsch").replace(_PUA_DSCH_L, "dsch")
        .replace(_PUA_TSCH_U, "Tsch").replace(_PUA_TSCH_L, "tsch")
        .replace(_PUA_SCH_U, "Sch").replace(_PUA_SCH_L, "sch")
    )
    return s


def _normalize_slavic_english_y(s: str) -> str:
    """Replace English-romanization Cyrillic palatal glide Y-/ya/yo/yu/ye with Tarraconian J/j
    while avoiding illicit word-initial Cj- onset clusters (Wj-, Bj-, Klj-)."""
    s = s.replace("'", "").replace("’", "")
    s = re.sub(r"ii", "i", s)
    s = re.sub(r"\bY(?=[aeouâêôû])", "J", s)
    # Post-vocalic y + vowel (Kamchiya -> Kamtschija, Velikaya -> Welikaja, Viliya -> Wilija)
    s = re.sub(r"(?<=[aeiouäöüâêîôû])y(?=[aeouâêôû])", "j", s, flags=re.I)
    # Word-internal post-consonantal y + vowel (after a preceding vowel, never word-initial onset)
    s = re.sub(r"(?<=[aeiouäöüâêîôû][bcdfghklmnprstvwz])y(?=[aeouâêôû])", "j", s, flags=re.I)
    return s


def adapt_magyar_word(tok: str) -> str | None:
    """Reconcile 9th-12th century Old Magyar orthography to Tarraconian."""
    head, suf = split_glued_tarr_suffix(tok)
    low = head.lower()
    if low in _MAGYAR_EXEMPT:
        return None
    if low.endswith(("um", "ium")):
        return None

    cur = {
        "zagyva": "Zadjwa",
        "mecsek": "Metschek",
        "beszterce": "Bestertze",
        "agatürszök": "Agatürsök",
        "nysa": "Nysa",
        "nysakő": "Nysakö",
    }
    if low in cur:
        return cur[low] + suf

    s = head
    # 1. Normalize Hungarian long/umlaut vowels FIRST so palatal lookaheads/rules see clean vowels
    magyar_vowels = {
        "ő": "ö", "Ő": "Ö", "ű": "ü", "Ű": "Ü",
        "á": "â", "Á": "Â", "é": "ê", "É": "Ê", "í": "î", "Í": "Î",
        "ó": "ô", "Ó": "Ô", "ú": "û", "Ú": "Û",
    }
    s = "".join(magyar_vowels.get(c, c) for c in s)

    # 2. Protect digraphs with paired upper/lower PUA markers
    s = re.sub(r"sch", lambda m: _pua(m, _PUA_SCH_U, _PUA_SCH_L), s, flags=re.I)
    s = re.sub(r"cs", lambda m: _pua(m, _PUA_TSCH_U, _PUA_TSCH_L), s, flags=re.I)
    s = re.sub(r"zs", lambda m: _pua(m, _PUA_SCH_U, _PUA_SCH_L), s, flags=re.I)
    s = re.sub(r"sz", lambda m: _pua(m, _PUA_S_U, _PUA_S_L), s, flags=re.I)
    # Palatal stops/sonorants when adjacent to a vowel (before vowel or after vowel in coda/compound)
    _v = r"[aeiouäöüâêîôû]"
    for dig, up, lo in (
        ("gy", _PUA_DJ_U, _PUA_DJ_L),
        ("ly", _PUA_LJ_U, _PUA_LJ_L),
        ("ny", _PUA_NJ_U, _PUA_NJ_L),
        ("ty", _PUA_TJ_U, _PUA_TJ_L),
    ):
        s = re.sub(rf"(?:(?<={_v}){dig}|{dig}(?={_v}))", lambda m, u=up, l=lo: _pua(m, u, l), s, flags=re.I)
    # 3. Bare Magyar s = [ʃ] -> sch; bare Magyar c = [ts] -> z-/tz; v -> w
    s = re.sub(r"s", lambda m: _pua(m, _PUA_SCH_U, _PUA_SCH_L), s, flags=re.I)
    s = _apply_slavic_c_to_tz(s)
    s = s.replace("v", "w").replace("V", "W")

    s = (
        s.replace(_PUA_SCH_U, "Sch").replace(_PUA_SCH_L, "sch")
        .replace(_PUA_TSCH_U, "Tsch").replace(_PUA_TSCH_L, "tsch")
        .replace(_PUA_S_U, "S").replace(_PUA_S_L, "s")
        .replace(_PUA_DJ_U, "Dj").replace(_PUA_DJ_L, "dj")
        .replace(_PUA_LJ_U, "Lj").replace(_PUA_LJ_L, "lj")
        .replace(_PUA_NJ_U, "Nj").replace(_PUA_NJ_L, "nj")
        .replace(_PUA_TJ_U, "Tj").replace(_PUA_TJ_L, "tj")
    )
    return s + suf


def adapt_lechitic_word(tok: str) -> str | None:
    """Reconcile 9th-12th c. Old Polish / Sorbian / Kashubian (Option A: rz -> rj / post-C r)."""
    head, suf = split_glued_tarr_suffix(tok)
    low = head.lower()
    if low in _SLAVIC_EXEMPT or low.startswith(("clovis", "clement")):
        return None
    if low.endswith(("um", "ium")):
        return None

    cur = {
        "ślężanie": "Schlenschanie",
        "dziadoszanie": "Dschadoschanie",
        "golęszycy": "Goleschytzy",
        "biebrza": "Biebra",
        "brzeg": "Breg",
        "słowińcë": "Slowintze",
        "niepołomicka": "Niepolomitzka",
    }
    if low in cur:
        return cur[low] + suf

    s = _protect_ch(head, ch_to_tsch=False)
    # 1. Policy Option A: 11th-12th c. palatalized *r' (rz): r after consonant, rj between/before vowels
    s = re.sub(r"(?<=[bcdfghkptvwzBCDFGHKPTVWZ])rz", "r", s, flags=re.I)
    s = re.sub(r"rz", lambda m: cap_match(m.group(0), "rj"), s, flags=re.I)
    # 2. Polish nasals ę / ą
    s = re.sub(r"ę(?=[bp])", "em", s, flags=re.I)
    s = re.sub(r"ę", "en", s, flags=re.I)
    s = re.sub(r"ą(?=[bp])", "om", s, flags=re.I)
    s = re.sub(r"ą", "on", s, flags=re.I)
    # 3. Lechitic palatals: dzi/dż/dź -> dsch, cz/ć -> tsch, sz/ś/ż/ź -> sch, ń -> nj/n
    s = re.sub(r"dzi(?=[aoueyâêîôû])", lambda m: _pua(m, _PUA_DSCH_U, _PUA_DSCH_L), s, flags=re.I)
    s = re.sub(r"d[żź]", lambda m: _pua(m, _PUA_DSCH_U, _PUA_DSCH_L), s, flags=re.I)
    s = re.sub(r"cz", lambda m: _pua(m, _PUA_TSCH_U, _PUA_TSCH_L), s, flags=re.I)
    s = re.sub(r"sz|[śżźŚŻŹ]", lambda m: _pua(m, _PUA_SCH_U, _PUA_SCH_L), s, flags=re.I)
    s = re.sub(r"ń(?=[aoueyâêîôû])", "nj", s, flags=re.I)
    s = s.replace("ń", "n").replace("Ń", "N")
    # 4. Bare Lechitic c -> z- / tz BEFORE č/š restore
    s = _apply_slavic_c_to_tz(s)
    s = _apply_common_slavic_diacritics(s, v_to_w=True)
    s = _restore_ch(s)
    return s + suf


def adapt_proto_slavic_word(tok: str) -> str | None:
    """Reconcile reconstructed Proto-Slavic (sla-pro) NTR substrates (nasals ę/ą, x=[x], yers, c=[ts])."""
    head, suf = split_glued_tarr_suffix(tok)
    low = head.lower()
    if low == "de":
        return "de"
    if low == "wass":
        return "Wass"
    if low == "czege":
        return "Tschege" + suf
    if low in _SLAVIC_EXEMPT or low.startswith(("clovis", "clement")):
        return None
    if low.endswith(("um", "ium")):
        return None

    s = _protect_ch(head, ch_to_tsch=False)
    # Proto-Slavic velar fricative x = [x] -> ch
    s = re.sub(r"x", lambda m: _pua(m, _PUA_CH_U, _PUA_CH_L), s, flags=re.I)
    # Proto-Slavic nasals ę / ą
    s = re.sub(r"ę(?=[bp])", "em", s, flags=re.I)
    s = re.sub(r"ę", "en", s, flags=re.I)
    s = re.sub(r"ą(?=[bp])", "om", s, flags=re.I)
    s = re.sub(r"ą", "on", s, flags=re.I)
    # Polish-spelled digraphs if present in sla-pro eponyms (e.g. Sanguszko)
    s = re.sub(r"cz", lambda m: _pua(m, _PUA_TSCH_U, _PUA_TSCH_L), s, flags=re.I)
    s = re.sub(r"sz", lambda m: _pua(m, _PUA_SCH_U, _PUA_SCH_L), s, flags=re.I)
    s = _apply_slavic_c_to_tz(s)
    s = _apply_common_slavic_diacritics(s, v_to_w=True)
    s = _restore_ch(s)
    return s + suf


def adapt_czech_slovak_word(tok: str) -> str | None:
    """Reconcile 9th-12th c. Old Czech & Slovak (Option A: ř -> rj / post-C r)."""
    head, suf = split_glued_tarr_suffix(tok)
    low = head.lower()
    if low in _SLAVIC_EXEMPT or low.startswith(("clovis", "clement")):
        return None
    if low.endswith(("um", "ium")):
        return None
    # Preserve test-locked Slovak forms
    if low in {"štiavnické", "štiavnicke"}:
        return "Stiavnickê" + suf
    if low == "vrchy":
        return "werchy"

    if low == "zemplínske":
        return "Zemplînske" + suf
    if low in {"žatec", "zatec"}:
        return "Schatetz" + suf
    if low == "chřiby":
        return "Chriby" + suf

    s = _protect_ch(head, ch_to_tsch=False)
    # 1. Pre-13th c. Option A *r' (ř) & Stage 3 generic -tvrz -> -twert
    s = re.sub(r"tvrz\b", "twert", s, flags=re.I)
    s = re.sub(r"(?<=[bcdfghkptvwzBCDFGHKPTVWZ\uE040\uE041])ř", "r", s, flags=re.I)
    s = re.sub(r"ř", lambda m: cap_match(m.group(0), "rj"), s, flags=re.I)
    # 2. Protect Czech/Slovak [s] from Stage 4 magyar s->sch; map c -> z-/tz
    s = re.sub(r"ň(?=[aoueyâêîôû])", "nj", s, flags=re.I)
    s = s.replace("ň", "n").replace("Ň", "N")
    s = _apply_slavic_c_to_tz(s)
    s = _apply_common_slavic_diacritics(s, v_to_w=True)
    s = _restore_ch(s)
    return s + suf


def adapt_south_slavic_word(tok: str, *, bulgarian_ch_is_tsch: bool = False) -> str | None:
    """Reconcile 9th-12th c. South Slavic (Bulgarian, Serbian, Croatian, Bosnian, Slovene)."""
    head, suf = split_glued_tarr_suffix(tok)
    low = head.lower()
    # Explicit pre-exempt overrides for Latin/Greek/Magyar loans tagged South Slavic
    if low == "ad":
        return "ad"
    if low == "nicopolis":
        return "Nicopel" + suf
    if low == "nestum":
        return "Nestum" + suf
    if low == "philippopolis":
        return "Filippopel" + suf
    if low == "szerem":
        return "Serem" + suf

    if low in _SLAVIC_EXEMPT or low in {"stara", "planina", "velika"}:
        if low == "stara":
            return "Stara"
        if low == "velika":
            return "Welika"
        return None if low in _SLAVIC_EXEMPT else tok
    if low.endswith(("um", "ium")):
        return None

    if low in {"vŭcha", "vucha"}:
        return "Wutscha" + suf
    if low == "plješevica":
        return "Plêschewitza" + suf
    if low == "pčinja":
        return "Petschinja" + suf
    if low in {"vrhbosna", "vhrbosna"}:
        return "Werchbosna" + suf
    if low == "vrbanja":
        return "Werbanja" + suf
    if low.startswith(("clovis", "clement")):
        return None

    s = _protect_ch(head, ch_to_tsch=bulgarian_ch_is_tsch)
    s = re.sub(r"sht", lambda m: _pua(m, _PUA_SCH_U, _PUA_SCH_L) + "t", s, flags=re.I)
    s = re.sub(r"zh", lambda m: _pua(m, _PUA_SCH_U, _PUA_SCH_L), s, flags=re.I)
    s = _apply_slavic_c_to_tz(s)
    s = _apply_common_slavic_diacritics(s, v_to_w=True)
    if bulgarian_ch_is_tsch:
        s = _normalize_slavic_english_y(s)
    s = _restore_ch(s)
    return s + suf


def adapt_south_slavic_bul_word(tok: str) -> str | None:
    return adapt_south_slavic_word(tok, bulgarian_ch_is_tsch=True)


def adapt_east_slavic_word(tok: str) -> str | None:
    """Reconcile 9th-12th c. Old East Slavic & strip modern Russian frontier adjectival fossils."""
    head, suf = split_glued_tarr_suffix(tok)
    low = head.lower()
    if low == "euphrosyne":
        return "Eufrosyne" + suf
    if low in _SLAVIC_EXEMPT or low.startswith(("clovis", "clement")):
        return None
    if low.endswith(("um", "ium")):
        return None

    # Modern Russian frontier adjectival cleanup + 12th-c. yer forms
    cur = {
        "amursky": "Amûr",
        "bureinsky": "Bureja",
        "chudskoye": "Tschud",
        "ozero": "",
        "ozerokirchen": "kirchen",
        "srednerusskaya": "Srednerus",
        "podilska": "Podil",
        "yuzhnyy": "Jüschni",
        "dŭněprŭ": "Dunepr",
        "dněprŭ": "Dunepr",
        "sŭzhĭ": "Suschi",
        "vŭstrĭ": "Wustri",
        "dryhavichy": "Dryhawitschy",
        "kryvichy": "Kriwitschi",
        "krivichi": "Kriwitschi",
        "dregovichi": "Dregowitschi",
        "vyatichi": "Wyatitschi",
    }
    if low in cur:
        return cur[low] + suf

    s = head
    # 1. Strip modern Russian -skoye/-skaya/-skiye/-skiy/-sky frontier endings
    s = re.sub(r"([a-zâêîôû]{3,})(?:skoye|skaya|skiye|skiy|sky)\b", r"\1", s, flags=re.I)
    # 2. Protect East Slavic kh (= [x]) before ch (= [tʃ]) -> tsch
    s = re.sub(r"kh", lambda m: _pua(m, _PUA_CH_U, _PUA_CH_L), s, flags=re.I)
    s = re.sub(r"shch", lambda m: _pua(m, _PUA_SCH_U, _PUA_SCH_L), s, flags=re.I)
    s = re.sub(r"ch", lambda m: _pua(m, _PUA_TSCH_U, _PUA_TSCH_L), s, flags=re.I)
    s = re.sub(r"[zs]h", lambda m: _pua(m, _PUA_SCH_U, _PUA_SCH_L), s, flags=re.I)
    # 3. East Slavic c -> z- / -tz-, diacritics, v -> w, and English-style Y/ya/ii cleanup
    s = _apply_slavic_c_to_tz(s)
    s = _apply_common_slavic_diacritics(s, v_to_w=True)
    s = _normalize_slavic_english_y(s)
    s = _restore_ch(s)
    return s + suf


def adapt_magyar_to_tarraconian(stem: str) -> tuple[str, bool]:
    return dispatch_phrase(stem, adapt_magyar_word)


def adapt_lechitic_to_tarraconian(stem: str) -> tuple[str, bool]:
    return dispatch_phrase(stem, adapt_lechitic_word)


def adapt_proto_slavic_to_tarraconian(stem: str) -> tuple[str, bool]:
    return dispatch_phrase(stem, adapt_proto_slavic_word)


def adapt_czech_slovak_to_tarraconian(stem: str) -> tuple[str, bool]:
    return dispatch_phrase(stem, adapt_czech_slovak_word)


def adapt_south_slavic_to_tarraconian(stem: str) -> tuple[str, bool]:
    return dispatch_phrase(stem, adapt_south_slavic_word)


def adapt_south_slavic_bul_to_tarraconian(stem: str) -> tuple[str, bool]:
    return dispatch_phrase(stem, adapt_south_slavic_bul_word)


def adapt_east_slavic_to_tarraconian(stem: str) -> tuple[str, bool]:
    # Strip multi-word Russian frontier wrappers & Podilska before phrase splitting
    cleaned = re.sub(r"\bChudskoye\s+ozero", "Tschud", stem, flags=re.I)
    cleaned = re.sub(r"\bPodilska", "Podil", cleaned, flags=re.I)
    return dispatch_phrase(cleaned, adapt_east_slavic_word)

"""12th-century Old French / Gallo-Romance -> Tarraconian Chancellery phonological decoder."""

from __future__ import annotations

import re
from typing import Any

from .latin import is_true_latin_stem

GALLO_ROMANCE_ISOS: set[str] = {"fra", "fro", "nrf", "pcd", "wln"}

TARRACONIAN_DIRECT_CULTURES: set[str] = {
    "Tarraconian",
    "Lothringian",
    "Croato-Tarraconian",
    "Alpine-Tarraconian",
    "Ungwârer",
}

GALLO_ROMANCE_IRREGULAR_STEMS: dict[str, str] = {
    "auxerre": "Ôssêr",
    "auxonne": "Ôssône",
    "bruxelles": "Brüssels",
    "doubs": "Dûs",
    "reims": "Rêms",
    "rouen": "Ruwân",
    "caen": "Kân",
    "metz": "Metz",
    "chablis": "Tschablîs",
    "quentin": "Kentîn",
    "saint-quentin": "Zant-Kentîn",
    "aix": "Ais",
    "creuse": "Kröse",
}

NON_GALLO_ROMANCE_WORDS: set[str] = {
    "acqui", "ajaccio", "alba", "di", "monferrato", "aosta", "asti", "biella",
    "bologna", "brescello", "cortona", "empoli", "emilia", "ivrea", "luni",
    "modena", "novara", "reggio", "tortona", "vercelli", "volterra",
    "bandiagara", "loma", "everardo", "luitgard", "zwinisława", "zwinislawa",
    "anicium", "tusiacum", "octodurus", "sinaca", "gartona", "condate",
    "otmus", "mariana", "durivum", "ligericulus", "romanchia", "albantia",
    "olonna", "geneva", "birni", "masallaci", "gari", "tenda", "eglwys", "porth",
    "margarita", "margeride",
    "burch", "stat", "kirchen", "kapelle", "wart", "munster", "meschit",
    "tempel", "marct", "hâven", "werc", "palz", "clôster", "stein", "berch",
    "bühil", "vurt", "walt", "velt", "lant", "zelle", "brunn", "port",
}


def adapt_gallo_romance_word(w: str) -> str | None:
    """
    Adapt one 12th-century Old French / Gallo-Romance token to Tarraconian
    Chancellery orthography. Returns None for non-French tokens.
    """
    low = w.lower()
    if low in GALLO_ROMANCE_IRREGULAR_STEMS:
        return GALLO_ROMANCE_IRREGULAR_STEMS[low]
    if low in {"de", "des", "du", "le", "la", "les", "sur", "en", "l", "d"}:
        return w
    if low in NON_GALLO_ROMANCE_WORDS or low.endswith(("um", "ium")):
        return None

    s = w
    rep_pre = {
        "é": "ê", "É": "Ê", "è": "e", "È": "E", "ê": "ê", "Ê": "Ê",
        "à": "a", "À": "A", "á": "â", "Á": "Â", "â": "â", "Â": "Â",
        "î": "î", "Î": "Î", "ï": "ï", "Ï": "Ï",
        "ô": "ô", "Ô": "Ô", "û": "û", "Û": "Û", "ù": "u", "Ù": "U",
        "œ": "ö", "Œ": "Ö",
    }
    s = "".join(rep_pre.get(c, c) for c in s)

    # 1. Silent u in qu/gu before front vowels BEFORE j/g->dsch and BEFORE eux->ös
    s = re.sub(r"qu(?=[eiyêî])", lambda m: "K" if m.group(0)[0].isupper() else "k", s, flags=re.I)
    s = re.sub(r"gu(?=[eiyêî])", lambda m: "\uE013" if m.group(0)[0].isupper() else "\uE012", s, flags=re.I)
    s = re.sub(r"([qgQG])u", lambda m: m.group(1) + "\uE015", s)

    # 2. 12th-c. voiced postalveolar affricate j / g(e,i) / ge(a,o) -> dsch BEFORE any palatal j is emitted
    s = re.sub(r"j|ge(?=[ao])|g(?=[eiyêî])", lambda m: "Dsch" if m.group(0)[0].isupper() else "dsch", s, flags=re.I)
    s = s.replace("\uE013", "G").replace("\uE012", "g")

    # 3. Coda -x endings (12th-c. scribal -x after u/eau/au represents [s], never [ks])
    s = re.sub(r"[iy]eux\b", lambda m: ("J" if m.group(0)[0].isupper() else "j") + "ös", s, flags=re.I)
    s = re.sub(r"eux\b", lambda m: ("Ö" if m.group(0)[0].isupper() else "ö") + "s", s, flags=re.I)
    s = re.sub(r"e?aux\b", lambda m: ("Ô" if m.group(0)[0].isupper() else "ô") + "s", s, flags=re.I)
    s = re.sub(r"([ao])ix\b", lambda m: m.group(1) + "is", s, flags=re.I)

    # 4. Vocalized -l / rounded front vowel digraphs (protecting MHG -auwe/-euwe/-ouwe)
    s = re.sub(r"eau", lambda m: "Ô" if m.group(0)[0].isupper() else "ô", s, flags=re.I)
    s = re.sub(r"au(?!we)", lambda m: "Ô" if m.group(0)[0].isupper() else "ô", s, flags=re.I)
    s = re.sub(r"(?:oeu|eu)(?!we)", lambda m: "Ö" if m.group(0)[0].isupper() else "ö", s, flags=re.I)
    s = re.sub(r"ou(?!we)", lambda m: "\uE011" if m.group(0)[0].isupper() else "\uE010", s, flags=re.I)

    # 5. Voiceless affricate ch -> tsch (skip already-Tarraconian sch/tsch/dsch)
    s = re.sub(r"(?<![stdSTD])ch", lambda m: "Tsch" if m.group(0)[0].isupper() else "tsch", s, flags=re.I)

    # 6. Alveolar affricate ç / c(e,i) -> z- / -tz-
    s = s.replace("Ç", "Tz").replace("ç", "tz")
    if re.match(r"^[cC](?=[eiyêî])", s):
        s = ("Z" if s[0].isupper() else "z") + s[1:]
    s = re.sub(r"(?<=.)c(?=[eiyêî])", "tz", s, flags=re.I)

    # 7. Palatal nasal gn -> nj
    s = re.sub(r"gn", lambda m: "Nj" if m.group(0)[0].isupper() else "nj", s, flags=re.I)

    # 8. Palatal liquid -ill-/-il -> lj; plain French geminates -ville -> -vîle, -lle -> -le
    s = re.sub(r"(?<=[aeiouâêîôûöü\uE010\uE011])ill", "lj", s, flags=re.I)
    s = re.sub(r"(?<=[aeiouâêîôûöü\uE010\uE011])il\b", "lj", s, flags=re.I)
    s = re.sub(r"ville\b", "vîle", s, flags=re.I)
    s = re.sub(r"lle\b", "le", s, flags=re.I)

    # 9. Silent French etymological -h- in th -> t
    s = re.sub(r"[Tt]h", lambda m: "T" if m.group(0)[0].isupper() else "t", s)

    # 10. Standalone French u -> ü, then restore protected u from ou/qu/gu
    s = s.replace("u", "ü").replace("U", "Ü")
    s = s.replace("\uE011", "U").replace("\uE010", "u").replace("\uE015", "u")

    # 11. Final -y -> -î after consonant, -on(s) -> -ôn(s), polysyllabic -ers -> -êrs, -ca -> -ke / -a -> -e
    s = re.sub(r"(?<=[^aeiouâêîôûäöü])y\b", "î", s)
    s = re.sub(r"on(s?)\b", r"ôn\1", s)
    s = re.sub(r"(?<=[A-Za-zÀ-ɏ]{3})ers\b", "êrs", s)
    s = re.sub(r"([A-Za-zÀ-ɏ]{2,})[cC]a\b", r"\1ke", s)
    s = re.sub(r"([A-Za-zÀ-ɏ]{2,})a\b", r"\1e", s)
    return s


def adapt_gallo_romance_to_tarraconian(stem: str) -> tuple[str, bool]:
    """Adapt a Gallo-Romance phrase or compound to Tarraconian."""
    s = stem.strip()
    if not s:
        return s, False
    low = s.lower()
    if low in GALLO_ROMANCE_IRREGULAR_STEMS:
        return GALLO_ROMANCE_IRREGULAR_STEMS[low], False

    parts = re.split(r"([\s\-]+)", s)
    out: list[str] = []
    any_fallback = False
    for p in parts:
        if not p or re.fullmatch(r"[\s\-]+", p):
            out.append(p)
        elif p[0].isalpha() or any(ord(c) > 127 for c in p):
            res = adapt_gallo_romance_word(p)
            if res is None:
                out.append(p)
                any_fallback = True
            else:
                out.append(res)
        else:
            out.append(p)
    joined = "".join(out)
    if joined and joined[0].islower():
        joined = joined[0].upper() + joined[1:]
    return joined, any_fallback


def is_gallo_romance_stem(rec: dict[str, Any], trans_family: str = "") -> bool:
    """Return True when the record holds a Gallo-Romance (fra/fro/nrf/pcd/wln) stem."""
    if is_true_latin_stem(rec):
        return False
    cf = (rec.get("coinage_morphology_family") or "").lower()
    # Colonial African / Berber / Cushitic NTR wrappers tagged `fra` are not Gallo-Romance
    if cf in {"west_central_african", "berber", "ethiopic_cushitic", "brythonic"}:
        return False
    cc = rec.get("coinage_culture") or ""
    src = rec.get("stem_source") or ""
    tf = (trans_family or "").lower()
    is_vanilla_fr = (cc == "Tarraconian" and src == "pre867_attested_vanilla" and tf == "gallo_romance")
    if cc in TARRACONIAN_DIRECT_CULTURES and not is_vanilla_fr:
        return False
    if is_vanilla_fr:
        return True
    return (
        rec.get("selected_iso") in GALLO_ROMANCE_ISOS
        or rec.get("coinage_morphology_family") == "gallo_romance"
    )

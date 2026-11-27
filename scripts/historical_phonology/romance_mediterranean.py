"""9th-12th century Mediterranean & Eastern Romance decoders:
  - Italo-Romance (ita, lom, scn, srd, vec, nap)
  - Occitano-Catalan (oci, cat)
  - Old Ibero-Romance (spa, por, glg, ast)
  - Eastern Romance / Vlach (ron, rup)
"""

from __future__ import annotations

import re

from .common import (
    SHARED_NON_NATIVE_TOKENS,
    cap_match as _cap_match,
    dispatch_phrase as _dispatch_phrase,
    split_glued_tarr_suffix as _split_glued_tarr_suffix,
)

ITALO_ISOS: set[str] = {"ita", "lom", "scn", "srd", "vec", "nap"}
OCCITANO_CATALAN_ISOS: set[str] = {"oci", "cat"}
IBERO_ISOS: set[str] = {"spa", "por", "glg", "ast"}
EASTERN_ROMANCE_ISOS: set[str] = {"ron", "rup"}

_SHARED_NON_ROMANCE: set[str] = SHARED_NON_NATIVE_TOKENS


def _weaken_final_a(s: str) -> str:
    """Weaken final -a -> -e without palatalizing preceding -ca into -ce [ts]."""
    if re.match(r"^[A-Za-zÀ-ɏ]{2,}ca$", s, flags=re.I):
        return s[:-2] + "ke"
    if re.match(r"^[A-Za-zÀ-ɏ]{3,}gha$", s, flags=re.I):
        return s[:-3] + "ge"
    if re.match(r"^[A-Za-zÀ-ɏ]{3,}a$", s, flags=re.I):
        return s[:-1] + "e"
    return s


def adapt_italo_romance_word(tok: str) -> str | None:
    """Adapt an Italo-Romance token into 12th-century Tarraconian orthography."""
    head, suf = _split_glued_tarr_suffix(tok)
    low = head.lower()
    if low in _SHARED_NON_ROMANCE or low in {"di", "da", "del", "della", "dei", "degli", "san", "rocca", "colli"}:
        return tok if low in {"di", "da", "del", "della", "dei", "degli"} else None
    if low in {"rome"}:
        return None
    if low.endswith(("um", "ium")):
        return None

    s = head
    # 1. Hard velar digraphs before front vowels -> k / g
    s = re.sub(r"cch(?=[eiêî])", lambda m: _cap_match(m.group(0), "k"), s, flags=re.I)
    s = re.sub(r"ch(?=[eiêî])", lambda m: _cap_match(m.group(0), "k"), s, flags=re.I)
    s = re.sub(r"gh(?=[eiêî])", lambda m: _cap_match(m.group(0), "g"), s, flags=re.I)
    # 2. Palatal gli -> lj
    s = re.sub(r"gli(?=[aeouâêîôû])", "lj", s, flags=re.I)
    s = re.sub(r"gli\b", "lj", s, flags=re.I)
    # 3. Affricates & sibilants: sci/sce -> sch, ggi/gge -> dsch, cci/cce -> tsch, gi/ge -> dsch, ci/ce -> tsch
    s = re.sub(r"sci(?=[aouâôû])", lambda m: _cap_match(m.group(0), "sch"), s, flags=re.I)
    s = re.sub(r"sc(?=[eiêî])", lambda m: _cap_match(m.group(0), "sch"), s, flags=re.I)
    s = re.sub(r"ggi(?=[aouâôû])", lambda m: _cap_match(m.group(0), "dsch"), s, flags=re.I)
    s = re.sub(r"gg(?=[eiêî])", lambda m: _cap_match(m.group(0), "dsch"), s, flags=re.I)
    s = re.sub(r"cci(?=[aouâôû])", lambda m: _cap_match(m.group(0), "tsch"), s, flags=re.I)
    s = re.sub(r"cc(?=[eiêî])", lambda m: _cap_match(m.group(0), "tsch"), s, flags=re.I)
    s = re.sub(r"gi(?=[aouâôû])", lambda m: _cap_match(m.group(0), "dsch"), s, flags=re.I)
    s = re.sub(r"g(?=[eiêî])", lambda m: _cap_match(m.group(0), "dsch"), s, flags=re.I)
    s = re.sub(r"ci(?=[aouâôû])", lambda m: _cap_match(m.group(0), "tsch"), s, flags=re.I)
    s = re.sub(r"c(?=[eiêî])", lambda m: _cap_match(m.group(0), "tsch"), s, flags=re.I)
    # 4. gn -> nj, zz -> tz, medial/final z -> tz
    s = re.sub(r"gn", lambda m: _cap_match(m.group(0), "nj"), s, flags=re.I)
    s = re.sub(r"zz+", "tz", s, flags=re.I)
    # 5. -eia$ -> -êe (Aquileia -> Aquilêe), dual apocope (-o dropped on polysyllables, -ca -> -ke / -a -> -e)
    if re.match(r"^[A-Za-zÀ-ɏ]{3,}eia$", s, flags=re.I):
        s = s[:-3] + "êe"
    elif re.match(r"^[A-Za-zÀ-ɏ]{4,}o$", s, flags=re.I) and not s.lower().endswith(("ko", "go")):
        s = s[:-1]
    else:
        s = _weaken_final_a(s)
    return s + suf


def adapt_occitano_catalan_word(tok: str) -> str | None:
    """Adapt a 12th-century Occitan/Catalan token into Tarraconian Chancellery orthography."""
    head, suf = _split_glued_tarr_suffix(tok)
    low = head.lower()
    if low in _SHARED_NON_ROMANCE or low in {"de", "del", "dels", "la", "las", "el", "en", "sur"}:
        return tok if low in {"de", "del", "dels", "la", "las", "el", "en", "sur"} else None
    if low in {"castell", "puig", "vila", "agde", "albi", "andorra", "orange", "palma", "pallars"}:
        return None
    if low.endswith(("um", "ium")):
        return None

    s = head
    rep = {"à": "a", "À": "A", "á": "â", "Á": "Â", "è": "e", "È": "E", "é": "ê", "É": "Ê", "ó": "ô", "Ó": "Ô", "ò": "o", "Ò": "O", "í": "î", "Í": "Î", "ú": "û", "Ú": "Û"}
    s = "".join(rep.get(c, c) for c in s)
    # 1. qu/gu before front vowels BEFORE j/g -> dsch
    s = re.sub(r"qu(?=[eiyêî])", lambda m: _cap_match(m.group(0), "k"), s, flags=re.I)
    s = re.sub(r"gu(?=[eiyêî])", lambda m: _cap_match(m.group(0), "\uE020"), s, flags=re.I)
    # 2. j / tg / tj / ge(a,o) / g(e,i,y) -> dsch
    s = re.sub(r"t[gj]|j|ge(?=[ao])|g(?=[eiyêî])", lambda m: _cap_match(m.group(0), "dsch"), s, flags=re.I)
    s = s.replace("\uE020", "g")
    # 3. Coda -ix/-oux/-ux -> -isch/-ûs/-us
    s = re.sub(r"ix\b", "isch", s, flags=re.I)
    s = re.sub(r"oux\b", "ûs", s, flags=re.I)
    s = re.sub(r"ux\b", "us", s, flags=re.I)
    s = re.sub(r"\bx(?=[aeiouâêîôû])", lambda m: _cap_match(m.group(0), "sch"), s, flags=re.I)
    # 4. gn / ny / nh -> nj, ç / c(e,i) -> z- / -tz-, ch -> tsch (not sch)
    s = re.sub(r"gn|n[yh]", lambda m: _cap_match(m.group(0), "nj"), s, flags=re.I)
    s = re.sub(r"(?<![stdSTD])ch", lambda m: _cap_match(m.group(0), "tsch"), s, flags=re.I)
    s = s.replace("Ç", "Tz").replace("ç", "tz")
    if re.match(r"^[cC](?=[eiyêî])", s):
        s = ("Z" if s[0].isupper() else "z") + s[1:]
    s = re.sub(r"(?<=.)c(?=[eiyêî])", "tz", s, flags=re.I)
    # 5. Catalan palatal ll -> lj at initial Ll- or final palatal -ll (Urgell -> Urdschelj)
    s = re.sub(r"\bll", lambda m: _cap_match(m.group(0), "lj"), s, flags=re.I)
    s = re.sub(r"ll\b", "lj", s, flags=re.I)
    s = re.sub(r"on[a]\b", "ôn", s, flags=re.I)
    s = re.sub(r"on\b", "ôn", s, flags=re.I)
    s = _weaken_final_a(s)
    return s + suf


def adapt_ibero_romance_word(tok: str) -> str | None:
    """Adapt a 12th-century Old Ibero-Romance (Spanish/Galician-Portuguese/Leonese) token."""
    head, suf = _split_glued_tarr_suffix(tok)
    low = head.lower()
    if low in _SHARED_NON_ROMANCE or low in {"de", "del", "la", "las", "los", "el", "o", "a", "y"}:
        return tok if low in {"de", "del", "la", "las", "los", "el", "o", "a", "y"} else None
    if low in {"santiago", "alava", "alba", "amaya", "gredos", "meseta", "central", "systema", "sistema"}:
        return None
    if low.endswith(("um", "ium")):
        return None

    s = head
    rep = {"á": "â", "Á": "Â", "é": "ê", "É": "Ê", "í": "î", "Í": "Î", "ó": "ô", "Ó": "Ô", "ú": "û", "Ú": "Û"}
    s = "".join(rep.get(c, c) for c in s)
    # 1. gü(e,i) -> gw, qu(e,i) -> k, gu(e,i) -> g
    s = re.sub(r"gü(?=[eiêî])", lambda m: _cap_match(m.group(0), "gw"), s, flags=re.I)
    s = re.sub(r"qu(?=[eiyêî])", lambda m: _cap_match(m.group(0), "k"), s, flags=re.I)
    s = re.sub(r"gu(?=[eiyêî])", lambda m: _cap_match(m.group(0), "\uE021"), s, flags=re.I)
    # 2. 12th-c. Old Spanish/Portuguese palatals & sibilants
    s = re.sub(r"j|g(?=[eiyêî])", lambda m: _cap_match(m.group(0), "dsch"), s, flags=re.I)
    s = s.replace("\uE021", "g")
    s = re.sub(r"x", lambda m: _cap_match(m.group(0), "sch"), s, flags=re.I)
    s = re.sub(r"ñ|nh", lambda m: _cap_match(m.group(0), "nj"), s, flags=re.I)
    s = re.sub(r"ll|lh", lambda m: _cap_match(m.group(0), "lj"), s, flags=re.I)
    s = re.sub(r"(?<![stdSTD])ch", lambda m: _cap_match(m.group(0), "tsch"), s, flags=re.I)
    s = s.replace("Ç", "Tz").replace("ç", "tz")
    if re.match(r"^[cC](?=[eiyêî])", s):
        s = ("Z" if s[0].isupper() else "z") + s[1:]
    s = re.sub(r"(?<=.)c(?=[eiyêî])", "tz", s, flags=re.I)
    s = re.sub(r"ón\b", "ôn", s, flags=re.I)
    if re.match(r"^[A-Za-zÀ-ɏ]{4,}o$", s, flags=re.I) and low not in {"toledo", "oviedo", "ebro"}:
        s = s[:-1]
    else:
        s = _weaken_final_a(s)
    return s + suf


def adapt_eastern_romance_word(tok: str) -> str | None:
    """Adapt an Eastern Romance (Vlach/Romanian) token to Tarraconian Chancellery orthography."""
    head, suf = _split_glued_tarr_suffix(tok)
    low = head.lower()
    if low in _SHARED_NON_ROMANCE or low in {"de", "cu", "din", "în", "pe"}:
        return tok if low in {"de", "cu", "din", "în", "pe"} else None
    if low.endswith(("um", "ium")):
        return None

    s = head
    # Strip modern Romanian definite genitive -ului / -lui before compounding (Trascăului -> Trascău)
    if suf and re.search(r"ului$", s, flags=re.I) and len(s) > 6:
        s = re.sub(r"ului$", "u", s, flags=re.I)

    # 1. Hard velar digraphs che/chi/ghe/ghi -> ke/ki/ge/gi
    s = re.sub(r"ch(?=[eiîê])", lambda m: _cap_match(m.group(0), "k"), s, flags=re.I)
    s = re.sub(r"gh(?=[eiîê])", lambda m: _cap_match(m.group(0), "\uE022"), s, flags=re.I)
    # 2. Palatal affricates ce/ci/ge/gi
    s = re.sub(r"ce(?=[aouâôă])", lambda m: _cap_match(m.group(0), "tsch"), s, flags=re.I)
    s = re.sub(r"c(?=[eiî])", lambda m: _cap_match(m.group(0), "tsch"), s, flags=re.I)
    s = re.sub(r"ge(?=[aouâôă])", lambda m: _cap_match(m.group(0), "dsch"), s, flags=re.I)
    s = re.sub(r"g(?=[eiî])", lambda m: _cap_match(m.group(0), "dsch"), s, flags=re.I)
    s = s.replace("\uE022", "g")
    # 3. Romanian sibilants & central vowels (preserve â/î circumflexes; simplify -ea hiatus)
    s = s.replace("Ș", "Sch").replace("ș", "sch")
    s = s.replace("Ț", "Tz").replace("ț", "tz")
    s = s.replace("Ă", "E").replace("ă", "e")
    s = s.replace("Î", "Â").replace("î", "â")
    if re.match(r"^[A-Za-zÀ-ɏ]{3,}ea$", s, flags=re.I):
        s = s[:-2] + "e"
    else:
        s = _weaken_final_a(s)
    return s + suf


def adapt_italo_romance_to_tarraconian(stem: str) -> tuple[str, bool]:
    return _dispatch_phrase(stem, adapt_italo_romance_word)


def adapt_occitano_catalan_to_tarraconian(stem: str) -> tuple[str, bool]:
    return _dispatch_phrase(stem, adapt_occitano_catalan_word, split_de_elision=True)


def adapt_ibero_romance_to_tarraconian(stem: str) -> tuple[str, bool]:
    return _dispatch_phrase(stem, adapt_ibero_romance_word)


def adapt_eastern_romance_to_tarraconian(stem: str) -> tuple[str, bool]:
    return _dispatch_phrase(stem, adapt_eastern_romance_word)

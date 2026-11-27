"""Shared utilities for Stage 4A historical-phonology decoders."""

from __future__ import annotations

import re
from typing import Callable

TARR_GLUED_SUFFIXES: tuple[str, ...] = (
    "burch", "stat", "kirchen", "kapelle", "wart", "munster", "meschit",
    "tempel", "marct", "hâven", "werc", "palz", "clôster", "stein", "berch",
    "bühil", "vurt", "walt", "velt", "lant", "zelle", "brunn", "port", "torn",
    "smida", "wîe", "march", "brücke", "tôr", "wal", "felt", "sê", "hûs", "castel",
    "borg", "burh", "tun", "wic", "cirice", "kirkja", "virki", "fell", "vík",
)

SHARED_NON_NATIVE_TOKENS: set[str] = {
    "burch", "stat", "kirchen", "kapelle", "wart", "munster", "meschit",
    "tempel", "marct", "hâven", "werc", "palz", "clôster", "stein", "berch",
    "bühil", "vurt", "walt", "velt", "lant", "zelle", "brunn", "port", "torn",
    "smida", "wîe", "wal", "castel", "brücke", "tôr",
    "luitgard", "bérenger", "berenger", "everardo", "welf", "mary", "nikodemos",
    "markos", "benedict", "catherine", "george", "nicholas", "andrew", "clovis",
    "columba", "declan", "jerome", "gabriel", "gábriel", "anthony", "barbara",
    "brigid", "lucia", "boniface", "cyprian", "cypriân", "withgils", "paul",
    "henry", "william", "martin", "cellachán", "cellachân", "cellachan",
    "syväri", "karlotte", "ampelas", "neajlov", "neajlouwe",
    "civitas", "alba", "fucens", "ad", "nonum", "hix",
}


def cap_match(orig: str, repl: str) -> str:
    """Match leading capitalization of `orig` onto `repl`."""
    return repl[:1].upper() + repl[1:] if orig and orig[0].isupper() else repl


def split_glued_tarr_suffix(tok: str) -> tuple[str, str]:
    """Split a glued Tarraconian (or Stage 3 calqued) holding suffix from `tok`."""
    low = tok.lower()
    for suf in TARR_GLUED_SUFFIXES:
        if len(low) > len(suf) + 2 and low.endswith(suf):
            # Preserve exact suffix only for canonical Tarraconian suffixes; Stage 3 native suffixes stay part of stem
            if suf in {"borg", "burh", "tun", "wic", "cirice", "kirkja", "virki", "fell", "vík"}:
                continue
            return tok[: -len(suf)], suf
    return tok, ""


def dispatch_phrase(
    stem: str,
    word_fn: Callable[[str], str | None],
    *,
    split_de_elision: bool = False,
) -> tuple[str, bool]:
    """Apply token-level `word_fn` across spaces/hyphens, tracking fallback need."""
    s = stem.strip()
    if not s:
        return s, False
    if split_de_elision:
        s = re.sub(r"\bd['’](?=[A-ZÀ-ɏ])", "de ", s)
    parts = re.split(r"([\s\-]+)", s)
    out: list[str] = []
    any_fb = False
    for p in parts:
        if not p or re.fullmatch(r"[\s\-]+", p):
            out.append(p)
        elif p[0].isalpha() or any(ord(c) > 127 for c in p):
            res = word_fn(p)
            if res is None:
                out.append(p)
                any_fb = True
            else:
                out.append(res)
        else:
            out.append(p)
    joined = "".join(out)
    if joined and joined[0].islower():
        joined = joined[0].upper() + joined[1:]
    return joined, any_fb


COLONIAL_WRAPPER_MAP: tuple[tuple[str, str], ...] = (
    ("Golfe de Guinée", "Ginêebucht"),
    ("Golfe du Bénin", "Bênînbucht"),
    ("Fleuve Sénégal", "Sênêgalflôz"),
    ("Monts Mandingues", "Mandingberch"),
    ("Cordillera Cantábrica", "Cordiljere Cantâbrike"),
    ("Cordilleras Béticas", "Kordiljêre Bêtike"),
    ("Massif des Maures", "Môrenmassîf"),
    ("Mer du Nord", "Nortmêr"),
    ("Les Moëres", "Moeren"),
    ("Kozhozero", "Koschsêe"),
    ("Kanozero", "Kansêe"),
)


def is_colonial_wrapper_stem(rec: dict) -> bool:
    """Return True when a record carries a modern colonial/atlas geographic wrapper."""
    cf = (rec.get("coinage_morphology_family") or "").lower()
    src = rec.get("coined_source_form") or ""
    iso = rec.get("selected_iso") or ""
    if any(pat.lower() in src.lower() for pat, _ in COLONIAL_WRAPPER_MAP):
        if cf in {"west_central_african", "berber", "ethiopic_cushitic", "tarraconian_imperial", "brythonic", "finnic", "sami"}:
            return True
        if iso in {"fra", "spa", "fin", "smi"} and cf in {"west_central_african", "tarraconian_imperial", "brythonic", "finnic", "sami"}:
            return True
    return False


def adapt_colonial_wrapper_word(tok: str) -> str | None:
    return None


def adapt_colonial_wrapper_to_tarraconian(stem: str) -> tuple[str, bool]:
    """Strip/calque colonial French/Spanish/European geographic wrappers in NTR stems."""
    s = stem.strip()
    if not s:
        return s, False
    for pat, repl in COLONIAL_WRAPPER_MAP:
        if pat.lower() in s.lower():
            s = re.sub(re.escape(pat), repl, s, flags=re.I)
            return s, False
    return s, True


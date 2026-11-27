"""Stage 4A: Modular 9th-12th Century Historical Phonology Reconciliation Package."""

from __future__ import annotations

import re
from typing import Any, Callable

from .byzantine_greek import (
    BYZANTINE_ISOS,
    adapt_byzantine_greek_to_tarraconian,
    adapt_byzantine_greek_token,
    is_byzantine_greek_stem,
)
from .celtic_germanic import (
    BRYTHONIC_ISOS,
    ENGLISH_ISOS,
    GOIDELIC_ISOS,
    NORTH_GERMANIC_ISOS,
    WELSH_ISOS,
    adapt_breton_cornish_to_tarraconian,
    adapt_breton_cornish_word,
    adapt_brythonic_to_tarraconian,
    adapt_brythonic_word,
    adapt_english_to_tarraconian,
    adapt_english_word,
    adapt_goidelic_to_tarraconian,
    adapt_goidelic_word,
    adapt_north_germanic_to_tarraconian,
    adapt_north_germanic_word,
    adapt_welsh_to_tarraconian,
    adapt_welsh_word,
)
from .common import (
    adapt_colonial_wrapper_to_tarraconian,
    adapt_colonial_wrapper_word,
    is_colonial_wrapper_stem,
)
from .gallo_romance import (
    GALLO_ROMANCE_IRREGULAR_STEMS,
    GALLO_ROMANCE_ISOS,
    NON_GALLO_ROMANCE_WORDS,
    TARRACONIAN_DIRECT_CULTURES,
    adapt_gallo_romance_to_tarraconian,
    adapt_gallo_romance_word,
    is_gallo_romance_stem,
)
from .latin import (
    LATIN_CURATED_PHRASES,
    LATIN_SINGLE_CURATED,
    LATIN_STRIPPABLE_GEO_WHEN_COMPOUNDED,
    NON_LATIN_MISATTRIBUTED,
    adapt_latin_to_tarraconian,
    adapt_latin_word,
    is_true_latin_stem,
)
from .romance_mediterranean import (
    EASTERN_ROMANCE_ISOS,
    IBERO_ISOS,
    ITALO_ISOS,
    OCCITANO_CATALAN_ISOS,
    adapt_eastern_romance_to_tarraconian,
    adapt_eastern_romance_word,
    adapt_ibero_romance_to_tarraconian,
    adapt_ibero_romance_word,
    adapt_italo_romance_to_tarraconian,
    adapt_italo_romance_word,
    adapt_occitano_catalan_to_tarraconian,
    adapt_occitano_catalan_word,
)
from .slavic_magyar import (
    CZECH_SLOVAK_ISOS,
    EAST_SLAVIC_ISOS,
    GENERIC_SLAVIC_ISOS,
    LECHITIC_ISOS,
    MAGYAR_ISOS,
    PROTO_SLAVIC_ISOS,
    SOUTH_SLAVIC_ISOS,
    adapt_czech_slovak_to_tarraconian,
    adapt_czech_slovak_word,
    adapt_east_slavic_to_tarraconian,
    adapt_east_slavic_word,
    adapt_lechitic_to_tarraconian,
    adapt_lechitic_word,
    adapt_magyar_to_tarraconian,
    adapt_magyar_word,
    adapt_proto_slavic_to_tarraconian,
    adapt_proto_slavic_word,
    adapt_south_slavic_bul_to_tarraconian,
    adapt_south_slavic_bul_word,
    adapt_south_slavic_to_tarraconian,
    adapt_south_slavic_word,
)
from .sinosphere_non_s import (
    CHINESE_ISOS,
    JAPANESE_ISOS,
    KOREAN_ISOS,
    VIETNAMESE_ISOS,
    adapt_chinese_to_tarraconian,
    adapt_chinese_word,
    adapt_japanese_to_tarraconian,
    adapt_japanese_word,
    adapt_korean_to_tarraconian,
    adapt_korean_word,
    adapt_vietnamese_to_tarraconian,
    adapt_vietnamese_word,
)
from .turko_iranian import (
    IRANIAN_ISOS,
    TURKIC_ISOS,
    adapt_iranian_to_tarraconian,
    adapt_iranian_word,
    adapt_turkic_to_tarraconian,
    adapt_turkic_word,
)


def resolve_historical_decoder(
    rec: dict[str, Any],
    trans_family: str = "",
) -> tuple[str, Callable[[str], tuple[str, bool]], Callable[[str], str | None]] | None:
    """
    Determine whether a record should pass through a Stage 4A historical-phonology
    decoder (Wave 1 Byzantine/Mediterranean Romance or Wave 2 Celtic/English/Norse).
    Returns `(decoder_id, phrase_fn, token_fn)` or None.
    """
    if is_colonial_wrapper_stem(rec):
        return ("colonial_wrapper_12c", adapt_colonial_wrapper_to_tarraconian, adapt_colonial_wrapper_word)
    if is_true_latin_stem(rec):
        return None
    cc = rec.get("coinage_culture") or ""
    if is_gallo_romance_stem(rec, trans_family):
        return ("gallo_romance_12c", adapt_gallo_romance_to_tarraconian, adapt_gallo_romance_word)

    iso = rec.get("selected_iso") or ""
    cf = (rec.get("coinage_morphology_family") or "").lower()
    tf = (trans_family or "").lower()

    if cc in TARRACONIAN_DIRECT_CULTURES:
        # Allow Wave 2 & Wave 3 decoders on genuine non-German NTR substrates coined under Tarraconian
        # rulers (excluding saints/eponyms or pre-calqued German modifiers with tarr_equivalent).
        mod = rec.get("coined_modifier") or {}
        is_raw_ntr_sub = (
            rec.get("stage3_mode") not in {"synthesized_pious_saint", "synthesized_vain_eponym"}
            and not mod.get("tarr_equivalent")
            and rec.get("stem_source") in {"natural_tribal_replacements_867", "existing_natural_proper_name"}
        )
        if is_raw_ntr_sub:
            if iso in GOIDELIC_ISOS:
                return ("goidelic_12c", adapt_goidelic_to_tarraconian, adapt_goidelic_word)
            if iso in BRYTHONIC_ISOS:
                if iso in WELSH_ISOS:
                    return ("brythonic_12c", adapt_welsh_to_tarraconian, adapt_welsh_word)
                return ("brythonic_12c", adapt_breton_cornish_to_tarraconian, adapt_breton_cornish_word)
            if iso in NORTH_GERMANIC_ISOS:
                return ("north_germanic_12c", adapt_north_germanic_to_tarraconian, adapt_north_germanic_word)
            if iso in MAGYAR_ISOS:
                return ("magyar_12c", adapt_magyar_to_tarraconian, adapt_magyar_word)
            if iso in LECHITIC_ISOS:
                return ("west_slavic_lechitic_12c", adapt_lechitic_to_tarraconian, adapt_lechitic_word)
            if iso in CZECH_SLOVAK_ISOS:
                return ("west_slavic_cs_12c", adapt_czech_slovak_to_tarraconian, adapt_czech_slovak_word)
            if iso in SOUTH_SLAVIC_ISOS:
                if iso == "bul":
                    return ("south_slavic_12c", adapt_south_slavic_bul_to_tarraconian, adapt_south_slavic_bul_word)
                return ("south_slavic_12c", adapt_south_slavic_to_tarraconian, adapt_south_slavic_word)
            if iso in EAST_SLAVIC_ISOS:
                return ("east_slavic_12c", adapt_east_slavic_to_tarraconian, adapt_east_slavic_word)
            if iso in PROTO_SLAVIC_ISOS:
                return ("east_slavic_12c", adapt_proto_slavic_to_tarraconian, adapt_proto_slavic_word)
            if iso in VIETNAMESE_ISOS:
                return ("vietnamese_12c", adapt_vietnamese_to_tarraconian, adapt_vietnamese_word)
            if iso in KOREAN_ISOS:
                return ("korean_12c", adapt_korean_to_tarraconian, adapt_korean_word)
            if iso in JAPANESE_ISOS:
                return ("japanese_12c", adapt_japanese_to_tarraconian, adapt_japanese_word)
            if iso in CHINESE_ISOS:
                return ("chinese_12c_phonetic", adapt_chinese_to_tarraconian, adapt_chinese_word)
            if iso in TURKIC_ISOS:
                return ("turkic_12c", adapt_turkic_to_tarraconian, adapt_turkic_word)
            if iso in IRANIAN_ISOS:
                return ("iranian_12c", adapt_iranian_to_tarraconian, adapt_iranian_word)
        return None

    if is_byzantine_greek_stem(rec, trans_family):
        return ("byzantine_greek_12c", adapt_byzantine_greek_to_tarraconian, adapt_byzantine_greek_token)

    def _matches_family(isos: set[str], fam: str, *, extra_fams: set[str] = set()) -> bool:
        if iso in isos:
            return True
        if (cf == fam or cf in extra_fams) and iso in {"", "und", "lat"}:
            return True
        if fam == "occitano_catalan" and tf == "occitano_catalan" and (rec.get("coined_source_form") or "").startswith("Ll"):
            return True
        return False

    if _matches_family(ITALO_ISOS, "italo_romance") and iso not in EASTERN_ROMANCE_ISOS | OCCITANO_CATALAN_ISOS | IBERO_ISOS:
        return ("italo_romance_12c", adapt_italo_romance_to_tarraconian, adapt_italo_romance_word)
    if _matches_family(OCCITANO_CATALAN_ISOS, "occitano_catalan"):
        return ("occitano_catalan_12c", adapt_occitano_catalan_to_tarraconian, adapt_occitano_catalan_word)
    if _matches_family(IBERO_ISOS, "ibero_romance"):
        return ("ibero_romance_12c", adapt_ibero_romance_to_tarraconian, adapt_ibero_romance_word)
    if _matches_family(EASTERN_ROMANCE_ISOS, "eastern_romance"):
        return ("eastern_romance_12c", adapt_eastern_romance_to_tarraconian, adapt_eastern_romance_word)

    # Wave 2: Insular Celtic, Late Old/Early Middle English, North Germanic
    if _matches_family(GOIDELIC_ISOS, "goidelic"):
        return ("goidelic_12c", adapt_goidelic_to_tarraconian, adapt_goidelic_word)
    if _matches_family(BRYTHONIC_ISOS, "brythonic"):
        if iso in WELSH_ISOS or (iso in {"", "und", "lat"} and cc in {"welsh", "cumbrian"}):
            return ("brythonic_12c", adapt_welsh_to_tarraconian, adapt_welsh_word)
        return ("brythonic_12c", adapt_breton_cornish_to_tarraconian, adapt_breton_cornish_word)
    if _matches_family(ENGLISH_ISOS, "anglo_saxon", extra_fams={"west_germanic"}):
        return ("anglo_saxon_12c", adapt_english_to_tarraconian, adapt_english_word)
    if _matches_family(NORTH_GERMANIC_ISOS, "north_germanic"):
        return ("north_germanic_12c", adapt_north_germanic_to_tarraconian, adapt_north_germanic_word)

    # Wave 3: Old Magyar, West Slavic (Lechitic / Czech-Slovak), South Slavic, Old East Slavic
    # Proto-Slavic (sla-pro) is always Slavic (never Magyar s->sch even under mogyer rulers)
    if iso in PROTO_SLAVIC_ISOS:
        dec_id = (
            "east_slavic_12c"
            if cf == "east_slavic"
            else "west_slavic_cs_12c"
            if cf == "west_slavic_czech_slovak"
            else "south_slavic_12c"
            if cf == "south_slavic"
            else "west_slavic_lechitic_12c"
        )
        return (dec_id, adapt_proto_slavic_to_tarraconian, adapt_proto_slavic_word)

    # Generic `sla` routes strictly by coinage morphology family (avoiding capturing Magyar/Bavarian/Finnic)
    if iso in GENERIC_SLAVIC_ISOS:
        if cf == "magyar":
            return ("magyar_12c", adapt_magyar_to_tarraconian, adapt_magyar_word)
        if cf == "west_slavic_lechitic":
            return ("west_slavic_lechitic_12c", adapt_lechitic_to_tarraconian, adapt_lechitic_word)
        if cf == "west_slavic_czech_slovak":
            return ("west_slavic_cs_12c", adapt_czech_slovak_to_tarraconian, adapt_czech_slovak_word)
        if cf == "south_slavic":
            return ("south_slavic_12c", adapt_south_slavic_to_tarraconian, adapt_south_slavic_word)
        if cf == "east_slavic":
            return ("east_slavic_12c", adapt_east_slavic_to_tarraconian, adapt_east_slavic_word)
        return None

    if _matches_family(MAGYAR_ISOS, "magyar"):
        return ("magyar_12c", adapt_magyar_to_tarraconian, adapt_magyar_word)
    if _matches_family(LECHITIC_ISOS, "west_slavic_lechitic"):
        return ("west_slavic_lechitic_12c", adapt_lechitic_to_tarraconian, adapt_lechitic_word)
    if _matches_family(CZECH_SLOVAK_ISOS, "west_slavic_czech_slovak"):
        return ("west_slavic_cs_12c", adapt_czech_slovak_to_tarraconian, adapt_czech_slovak_word)
    if _matches_family(SOUTH_SLAVIC_ISOS, "south_slavic"):
        if iso == "bul":
            return ("south_slavic_12c", adapt_south_slavic_bul_to_tarraconian, adapt_south_slavic_bul_word)
        return ("south_slavic_12c", adapt_south_slavic_to_tarraconian, adapt_south_slavic_word)
    if _matches_family(EAST_SLAVIC_ISOS, "east_slavic"):
        return ("east_slavic_12c", adapt_east_slavic_to_tarraconian, adapt_east_slavic_word)

    # Wave 4: Non-Track-S / Phonetic Sinosphere, Middle Turkic, Early New Persian
    if _matches_family(VIETNAMESE_ISOS, "viet"):
        return ("vietnamese_12c", adapt_vietnamese_to_tarraconian, adapt_vietnamese_word)
    if _matches_family(KOREAN_ISOS, "korean"):
        return ("korean_12c", adapt_korean_to_tarraconian, adapt_korean_word)
    if _matches_family(JAPANESE_ISOS, "japonic", extra_fams={"ainu"}):
        return ("japanese_12c", adapt_japanese_to_tarraconian, adapt_japanese_word)
    if _matches_family(CHINESE_ISOS, "sinosphere_chinese"):
        return ("chinese_12c_phonetic", adapt_chinese_to_tarraconian, adapt_chinese_word)
    if _matches_family(TURKIC_ISOS, "turkic", extra_fams={"oghur"}):
        return ("turkic_12c", adapt_turkic_to_tarraconian, adapt_turkic_word)
    if _matches_family(IRANIAN_ISOS, "iranian"):
        return ("iranian_12c", adapt_iranian_to_tarraconian, adapt_iranian_word)
    return None


def resolve_wave1_decoder(
    rec: dict[str, Any],
    trans_family: str = "",
) -> tuple[str, Callable[[str], tuple[str, bool]], Callable[[str], str | None]] | None:
    """Backwards-compatible alias to `resolve_historical_decoder`."""
    return resolve_historical_decoder(rec, trans_family)


__all__ = [
    "BRYTHONIC_ISOS",
    "BYZANTINE_ISOS",
    "CHINESE_ISOS",
    "CZECH_SLOVAK_ISOS",
    "EASTERN_ROMANCE_ISOS",
    "EAST_SLAVIC_ISOS",
    "ENGLISH_ISOS",
    "GALLO_ROMANCE_IRREGULAR_STEMS",
    "GALLO_ROMANCE_ISOS",
    "GENERIC_SLAVIC_ISOS",
    "GOIDELIC_ISOS",
    "IBERO_ISOS",
    "IRANIAN_ISOS",
    "ITALO_ISOS",
    "JAPANESE_ISOS",
    "KOREAN_ISOS",
    "LATIN_CURATED_PHRASES",
    "LATIN_SINGLE_CURATED",
    "LATIN_STRIPPABLE_GEO_WHEN_COMPOUNDED",
    "LECHITIC_ISOS",
    "MAGYAR_ISOS",
    "NON_GALLO_ROMANCE_WORDS",
    "NON_LATIN_MISATTRIBUTED",
    "NORTH_GERMANIC_ISOS",
    "OCCITANO_CATALAN_ISOS",
    "PROTO_SLAVIC_ISOS",
    "SOUTH_SLAVIC_ISOS",
    "TARRACONIAN_DIRECT_CULTURES",
    "TURKIC_ISOS",
    "VIETNAMESE_ISOS",
    "WELSH_ISOS",
    "adapt_breton_cornish_to_tarraconian",
    "adapt_breton_cornish_word",
    "adapt_brythonic_to_tarraconian",
    "adapt_brythonic_word",
    "adapt_byzantine_greek_to_tarraconian",
    "adapt_byzantine_greek_token",
    "adapt_chinese_to_tarraconian",
    "adapt_chinese_word",
    "adapt_colonial_wrapper_to_tarraconian",
    "adapt_colonial_wrapper_word",
    "adapt_czech_slovak_to_tarraconian",
    "adapt_czech_slovak_word",
    "adapt_east_slavic_to_tarraconian",
    "adapt_east_slavic_word",
    "adapt_eastern_romance_to_tarraconian",
    "adapt_eastern_romance_word",
    "adapt_english_to_tarraconian",
    "adapt_english_word",
    "adapt_gallo_romance_to_tarraconian",
    "adapt_gallo_romance_word",
    "adapt_goidelic_to_tarraconian",
    "adapt_goidelic_word",
    "adapt_ibero_romance_to_tarraconian",
    "adapt_ibero_romance_word",
    "adapt_iranian_to_tarraconian",
    "adapt_iranian_word",
    "adapt_italo_romance_to_tarraconian",
    "adapt_italo_romance_word",
    "adapt_japanese_to_tarraconian",
    "adapt_japanese_word",
    "adapt_korean_to_tarraconian",
    "adapt_korean_word",
    "adapt_latin_to_tarraconian",
    "adapt_latin_word",
    "adapt_lechitic_to_tarraconian",
    "adapt_lechitic_word",
    "adapt_magyar_to_tarraconian",
    "adapt_magyar_word",
    "adapt_north_germanic_to_tarraconian",
    "adapt_north_germanic_word",
    "adapt_occitano_catalan_to_tarraconian",
    "adapt_occitano_catalan_word",
    "adapt_proto_slavic_to_tarraconian",
    "adapt_proto_slavic_word",
    "adapt_south_slavic_bul_to_tarraconian",
    "adapt_south_slavic_bul_word",
    "adapt_south_slavic_to_tarraconian",
    "adapt_south_slavic_word",
    "adapt_turkic_to_tarraconian",
    "adapt_turkic_word",
    "adapt_vietnamese_to_tarraconian",
    "adapt_vietnamese_word",
    "adapt_welsh_to_tarraconian",
    "adapt_welsh_word",
    "is_byzantine_greek_stem",
    "is_colonial_wrapper_stem",
    "is_gallo_romance_stem",
    "is_true_latin_stem",
    "resolve_historical_decoder",
    "resolve_wave1_decoder",
]

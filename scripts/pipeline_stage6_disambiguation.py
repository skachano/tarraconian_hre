#!/usr/bin/env python3
"""Stage 6: Intra-County & Neighbor Disambiguation + Provenance Export.

Consumes:
  - data/pipeline_stage5_validated.json
  - data/ck3_adjacencies.json
  - data/barony_geography.json
  - data/ck3_baronies.geojson (color & optional save sync via --apply-to-geojson)
  - data/barony_coinage_rulers.json

Enforces (bottom-up barony autonomy, independent of upper-tier county/duchy/kingdom/empire names):
  1. Zero exact or near-homophonic intra-county collisions across all 3,476 counties via the
     4-step Collision Resolution Cascade (prioritizing pre-867 historical seats, then capitals):
       Step 1: 2nd/3rd candidate in ranked_ntr_candidates
       Step 2: Holding-type generic differentiation (-burch/-stat/-kirchen/-hâven coastal-gated)
       Step 3: True polygon-centroid directional prefix (Nord-/Ôst-/Sût-/West-/Mittel-/Alt-/Nîe-)
       Step 4: Stage 3 coinage-era founder/saint differentiation fallback
  2. Cross-border duplicate resolution on directly bordering non-Track_A baronies and full
     neighbor_duplicate_flags reporting across adjacent counties and baronies.
  3. Strict post-disambiguation Chancellery sound laws, phonotactic audit (0 failures), and IPA
     recomputation.

Emits:
  - data/barony_resolutions_v2.json (all 11,297 baronies with full v2 provenance schema)
  - data/tarraconian_barony_names_v2_l_english.yml (CK3 UTF-8 BOM + CRLF localisation)
  - Optional: --apply-to-geojson updates data/ck3_baronies.geojson & data/barony_resolutions.json
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from difflib import SequenceMatcher
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from audit_phonotactics_titles import check_title_phonotactics
from pipeline_stage4_calque_mediation import transliterate_stem_to_tarr
from pipeline_stage5_sound_laws import (
    ALLOWED_CHANCELLERY_CHARS,
    apply_full_stage5_sound_laws,
    build_daughter_dialect_variant,
)
from resolve_barony_titles import (
    generate_tarraconian_ipa,
    normalize_phonetic_stem,
)

IN_STAGE5 = ROOT / "data" / "pipeline_stage5_validated.json"
IN_ADJ = ROOT / "data" / "ck3_adjacencies.json"
IN_GEO = ROOT / "data" / "barony_geography.json"
IN_BARONIES_GJ = ROOT / "data" / "ck3_baronies.geojson"
IN_RULERS = ROOT / "data" / "barony_coinage_rulers.json"
IN_CULTURE_BRIDGE = ROOT / "data" / "ck3_culture_to_iso_and_generics.json"
IN_KANJI = ROOT / "data" / "sinosphere_kanji_tarraconian.json"

OUT_V2_JSON = ROOT / "data" / "barony_resolutions_v2.json"
OUT_V2_YML = ROOT / "data" / "tarraconian_barony_names_v2_l_english.yml"
OUT_V1_RES = ROOT / "data" / "barony_resolutions.json"

# Sorted longest-first so suffix stripping matches multi-char generics cleanly.
KNOWN_GENERICS = (
    "kirchen", "clôster", "klôster", "munster", "mynster", "castel", "ceaster",
    "brügge", "brück", "strâte", "wazzer", "pyrgos", "meschit", "tempel",
    "schûle", "hûsen", "hâven", "marct", "markt", "berge", "berch", "velde",
    "burch", "veste", "stein", "gouwe", "halle", "zelle", "klûse", "clûse",
    "stât", "stat", "burg", "berg", "haim", "heim", "dorp", "dorf", "port",
    "flôz", "wîer", "torre", "polis", "torn", "walt", "wald", "lant", "land",
    "palz", "wîe", "hof", "wîc", "furt", "sêe", "sê", "wal", "pel",
)

COASTAL_GENERICS = {"hâven", "port", "wik", "wîc"}

HOLDING_GENERIC_POOLS = {
    "castle": ["burch", "veste", "stein", "berch", "wal", "castel", "torn"],
    "city": ["stat", "marct", "dorp", "brügge", "hof", "wîc", "furt"],
    "church": ["kirchen", "zelle", "munster", "clôster"],
    "church_islam": ["meschit", "wîe", "halle"],
    "church_judaism": ["schûle", "halle", "wîe"],
    "church_non_christian": ["tempel", "wîe", "halle"],
}
NON_CHRISTIAN_FAMILIES = {
    "sinosphere_chinese", "korean", "japonic", "viet", "khitan", "tungusic",
    "mongolic", "austronesian", "indo_aryan", "dravidian", "tibetic",
    "burmese_qiangic", "tai_hmong", "mon_khmer", "arabic", "berber",
    "iranian", "turkic", "oghur", "west_central_african", "east_bantu_swahili",
}
CHRISTIAN_CHURCH_GENERICS = {"kirchen", "zelle", "munster", "clôster", "mynster", "klôster"}
COASTAL_EXTRA_GENERICS = {
    "castle": ["port"],
    "city": ["hâven", "port"],
    "church": [],
}

DIRECTION_PREFIX_MAP = {
    "N": ["Nord-", "Alt-"],
    "NE": ["Nordôst-", "Ôst-"],
    "E": ["Ôst-", "Nîe-"],
    "SE": ["Sûtôst-", "Sût-"],
    "S": ["Sût-", "Nider-"],
    "SW": ["Sûtwest-", "West-"],
    "W": ["West-", "Nîe-"],
    "NW": ["Nordwest-", "Nord-"],
    "CENTER": ["Mittel-", "Alt-"],
}
FALLBACK_POS_PREFIXES = ["Ober-", "Nider-", "Alt-", "Nîe-", "Nord-", "Sût-", "Ôst-", "West-"]

PRIORITY_GROUP_BY_TRACK = {
    "Track_A_retained": 1,
    "Track_S_pre867_attested": 1,
    "Track_D1_pre867_chartered": 2,
    "Track_C1_pre867_feudalized": 2,
    "Track_A_coinage_overrule": 2,
    "Track_S_pre867_overruled": 2,
    "Track_B_historical_names": 4,
    "Track_B_existing_natural": 4,
    "Track_B_ntr_restitution": 4,
    "Track_S_post867_historical_anchor": 4,
    "Track_C2_post867_feudalized": 5,
    "Track_D2_post867_foundation": 5,
    "Track_S_post867_coined_compound": 5,
    "Track_S_post867_ntr_sino_variant": 5,
}


def strip_holding_generic(name: str) -> tuple[str, str]:
    """Separate trailing Tarraconian holding generic if a >=3-letter stem remains."""
    if not name:
        return "", ""
    low = name.lower()
    for gen in KNOWN_GENERICS:
        if low.endswith(gen) and len(low) - len(gen) >= 3:
            stem = name[: len(name) - len(gen)].rstrip(" -")
            if len(re.sub(r"[^a-zA-ZâêîôûäöüÂÊÎÔÛÄÖÜ]", "", stem)) >= 3:
                return stem, gen
    return name, ""


def is_phonetic_collision(name_a: str, name_b: str, *, strict_stem: bool = False) -> bool:
    """Return True if two barony names collide exactly or near-homophonically (>=0.75)."""
    if not name_a or not name_b:
        return False
    if name_a.lower() == name_b.lower():
        return True
    pa = normalize_phonetic_stem(name_a)
    pb = normalize_phonetic_stem(name_b)
    if pa == pb:
        return True
    if strict_stem:
        ba, _ = strip_holding_generic(name_a)
        bb, _ = strip_holding_generic(name_b)
        sa = normalize_phonetic_stem(ba)
        sb = normalize_phonetic_stem(bb)
        if sa and sb and (
            sa == sb
            or (
                min(len(sa), len(sb)) >= 3
                and max(SequenceMatcher(None, sa, sb).ratio(), SequenceMatcher(None, sb, sa).ratio()) >= 0.75
            )
        ):
            return True
    if len(pa) >= 3 and len(pb) >= 3 and max(SequenceMatcher(None, pa, pb).ratio(), SequenceMatcher(None, pb, pa).ratio()) >= 0.75:
        return True
    return False


def has_allowed_chars(name: str) -> bool:
    """Check whether all characters belong to Chancellery Latin orthography."""
    return bool(name) and all(ch in ALLOWED_CHANCELLERY_CHARS for ch in name)


def finalize_candidate_name(
    raw_name: str,
    b_rec: dict,
    *,
    is_sea_coast: bool,
) -> str | None:
    """Normalize a candidate string through Stage 5 sound laws and phonotactic audit."""
    if not raw_name or "_" in raw_name:
        return None
    if not is_sea_coast:
        _, gen = strip_holding_generic(raw_name)
        if gen in COASTAL_GENERICS:
            return None
    normalized = apply_full_stage5_sound_laws(
        raw_name,
        is_sinosphere=bool(b_rec.get("is_sinosphere_scope", False)),
        macro_family=b_rec.get("coinage_morphology_family", ""),
    )
    if not normalized or not has_allowed_chars(normalized):
        return None
    if not is_sea_coast:
        _, gen2 = strip_holding_generic(normalized)
        if gen2 in COASTAL_GENERICS:
            return None
    issues = check_title_phonotactics(
        normalized,
        b_rec["barony_key"],
        b_rec.get("hierarchy", {}).get("empire", ""),
    )
    if issues:
        return None
    return normalized


def barony_priority_key(bk: str, b_rec: dict) -> tuple:
    """Sort key within a county: smaller tuple means higher priority to keep its stem."""
    track = b_rec.get("stage1_track", "")
    is_hist867 = bool(b_rec.get("is_historical_867"))
    is_cap = bool(b_rec.get("is_capital_barony"))
    group = PRIORITY_GROUP_BY_TRACK.get(track, 5)
    if is_cap and group > 3:
        group = 3
    return (
        group,
        0 if is_hist867 else 1,
        0 if is_cap else 1,
        bk,
    )


def load_mediation_ctx() -> dict:
    """Load Stage 4 transliteration tables cleanly once."""
    cb = json.loads(IN_CULTURE_BRIDGE.read_text(encoding="utf-8"))
    kanji_list = json.loads(IN_KANJI.read_text(encoding="utf-8"))
    kanji_readings: dict[str, tuple[str, str, str]] = {}
    for item in kanji_list:
        ch = item.get("char")
        if ch:
            kanji_readings[ch] = (
                item.get("pinyin_sort") or item.get("pinyin") or "",
                item.get("kr") or "",
                item.get("jp") or "",
            )
    return {
        "cult_bridge": cb["cultures"],
        "trans_rules": cb["transmission_rules"]["to_tarraconian"],
        "inter_map": {
            (x["source_family"], x["transmission_family"]): x
            for x in cb["transmission_rules"]["historical_intermediaries"]
        },
        "kanji_readings": kanji_readings,
    }


def adapt_with_stage4(raw: str, b_rec: dict, med_ctx: dict) -> str:
    """Invoke Stage 4 single-pass transliterate_stem_to_tarr for a barony record."""
    cult_bridge = med_ctx["cult_bridge"]
    coin_fam = b_rec.get("coinage_morphology_family") or ""
    trans_cult = b_rec.get("transmission_culture") or ""
    trans_fam = (cult_bridge.get(trans_cult) or {}).get("morphology_family") or coin_fam
    trans_prof = b_rec.get("transmission_profile") or "general_phonetic_adaptation"
    cs = b_rec.get("continuity_status") or ""
    is_direct_trans = (cs == "Direct Transparency") or (
        b_rec.get("coinage_culture")
        in {"Tarraconian", "Lothringian", "Croato-Tarraconian", "Alpine-Tarraconian", "Ungwârer"}
    )
    is_rupture = (cs == "Semantic Rupture (>= 50y)") and not is_direct_trans
    adapted, _notes = transliterate_stem_to_tarr(
        raw,
        trans_prof,
        coin_fam,
        trans_fam,
        med_ctx["inter_map"],
        med_ctx["trans_rules"],
        kanji_readings=med_ctx["kanji_readings"],
        is_rupture=is_rupture,
    )
    return adapted


def _church_pool_key(b_rec: dict, ruler_info: dict | None) -> str:
    """Return faith-appropriate generic pool key for church holdings."""
    if b_rec.get("holding_type") != "church":
        return b_rec.get("holding_type", "castle")
    rel = ((ruler_info or {}).get("religion_type") or "").lower()
    if rel:
        if "christian" in rel:
            return "church"
        if "islam" in rel:
            return "church_islam"
        if "juda" in rel:
            return "church_judaism"
        return "church_non_christian"
    if b_rec.get("coinage_culture") in {"Tarraconian", "Lothringian", "Croato-Tarraconian", "Alpine-Tarraconian", "Ungwârer"}:
        return "church"
    if b_rec.get("coinage_morphology_family") in NON_CHRISTIAN_FAMILIES or b_rec.get("is_sinosphere_scope"):
        return "church_non_christian"
    if strip_holding_generic(b_rec.get("tarr_hist", ""))[1] in {"tempel", "meschit", "schûle", "wîe", "halle", "palz"}:
        return "church_non_christian"
    return "church"


def render_ntr_candidate(
    cand: dict,
    b_rec: dict,
    is_sea_coast: bool,
    med_ctx: dict,
    *,
    ruler_info: dict | None = None,
) -> str | None:
    """Mediate an NTR ranked candidate into a Tarraconian Stage 5 compliant name."""
    raw = (cand.get("clean_stem") or cand.get("selected_form") or cand.get("localisation_stem") or cand.get("candidate_name") or "").strip()
    if not raw or "_" in raw:
        return None
    raw = re.sub(r"\s+(people|tribe|group|dynasty)$", "", raw, flags=re.I)
    ht = b_rec.get("holding_type", "castle")
    ckey = _church_pool_key(b_rec, ruler_info)
    base_tarr = adapt_with_stage4(raw, b_rec, med_ctx)
    if not base_tarr:
        return None
    _base_clean, existing_gen = strip_holding_generic(base_tarr)
    subtype = (cand.get("feature_subtype") or "").lower()

    if existing_gen and (existing_gen not in COASTAL_GENERICS or is_sea_coast):
        candidate_raw = base_tarr
    else:
        if subtype in ("lake", "lagoon") and "sê" not in base_tarr.lower() and not re.search(r"(?:tscho|hû|hu)$", base_tarr, re.I):
            candidate_raw = f"{base_tarr}sê"
        elif subtype in ("lake", "lagoon"):
            candidate_raw = base_tarr
        elif subtype in ("river", "stream", "creek") and ht == "castle" and len(base_tarr) <= 8:
            candidate_raw = f"{base_tarr}burch"
        elif subtype in ("mountain", "peak", "hill", "ridge") and ht == "castle":
            if re.search(r"(?:berch|stein|schân|uul|rücke)$", base_tarr, re.I):
                candidate_raw = f"{base_tarr}burch"
            else:
                candidate_raw = f"{base_tarr}stein"
        else:
            church_gen = HOLDING_GENERIC_POOLS.get(ckey, ["kirchen"])[0]
            gen = {"castle": "burch", "city": "stat", "church": church_gen}.get(ht, "burch")
            candidate_raw = f"{base_tarr}{gen}"

    return finalize_candidate_name(candidate_raw, b_rec, is_sea_coast=is_sea_coast)


def build_generic_variants(
    current_name: str,
    b_rec: dict,
    is_sea_coast: bool,
    *,
    ruler_info: dict | None = None,
) -> list[str]:
    """Generate Step 2 candidates by swapping or attaching holding-type generics."""
    ht = b_rec.get("holding_type", "castle")
    pool_key = _church_pool_key(b_rec, ruler_info)
    non_christ = pool_key != "church" and ht == "church"
    base, cur_gen = strip_holding_generic(current_name)
    pool = list(HOLDING_GENERIC_POOLS.get(pool_key, ["burch", "stat", "tempel" if non_christ else "kirchen"]))
    if is_sea_coast:
        pool = COASTAL_EXTRA_GENERICS.get(ht, []) + pool
    extras = ("burch", "stat", "stein", "veste", "dorp", "hûsen", "velde", "hof")
    if not non_christ:
        extras = extras + ("kirchen", "zelle")
    for extra in extras:
        if extra not in pool:
            pool.append(extra)

    out = []
    # Strip trailing hyphenated joiners cleanly
    stem = base.rstrip(" -")
    for gen in pool:
        if gen == cur_gen:
            continue
        raw = f"{stem}{gen}"
        cand = finalize_candidate_name(raw, b_rec, is_sea_coast=is_sea_coast)
        if cand and cand != current_name and cand not in out:
            out.append(cand)
    return out


def build_directional_variants(
    current_name: str,
    b_rec: dict,
    direction: str,
    is_sea_coast: bool,
) -> list[str]:
    """Generate Step 3 candidates with true polygon-centroid directional prefixes + optional generic shift."""
    prefixes = list(DIRECTION_PREFIX_MAP.get(direction or "CENTER", ["Nord-", "Sût-"]))
    for p in FALLBACK_POS_PREFIXES:
        if p not in prefixes:
            prefixes.append(p)

    # Remove an existing directional prefix before attaching another so we never stack Nord-Sût-
    stripped_dir = re.sub(
        r"^(Nordôst-|Nordwest-|Sûtôst-|Sûtwest-|Nord-|Sût-|Ôst-|West-|Ober-|Nider-|Mittel-|Alt-|Nîe-)",
        "",
        current_name,
    )
    out = []
    # Try combining directional prefix with plain stem AND with a varied generic if needed
    base, _ = strip_holding_generic(stripped_dir)
    ht = b_rec.get("holding_type", "castle")
    alt_gen = {"castle": "stein", "city": "marct", "church": "zelle"}.get(ht, "stat")

    for pref in prefixes:
        for raw in (f"{pref}{stripped_dir}", f"{pref}{base}{alt_gen}"):
            cand = finalize_candidate_name(raw, b_rec, is_sea_coast=is_sea_coast)
            if cand and cand != current_name and cand not in out:
                out.append(cand)
    return out


def build_coinage_fallback_variants(
    current_name: str,
    b_rec: dict,
    ruler_info: dict | None,
    is_sea_coast: bool,
    med_ctx: dict,
) -> list[str]:
    """Generate Step 4 coinage-era founder, saint, or compound differentiation variants."""
    ht = b_rec.get("holding_type", "castle")
    gens = HOLDING_GENERIC_POOLS.get(ht, ["burch", "stat", "kirchen"])
    if is_sea_coast and COASTAL_EXTRA_GENERICS.get(ht):
        gens = COASTAL_EXTRA_GENERICS[ht] + gens

    tokens = []
    saint = (b_rec.get("saint_dedication") or "").strip()
    if saint:
        saint_tarr = adapt_with_stage4(saint, b_rec, med_ctx)
        if saint_tarr:
            tokens.append(f"Zant-{saint_tarr}")
            tokens.append(saint_tarr)

    ruler_ep = (b_rec.get("ruler_eponym") or "").strip()
    if ruler_ep:
        tokens.append(ruler_ep)

    if ruler_info:
        rname = (ruler_info.get("clean_first_name") or "").strip()
        if rname and "_" not in rname:
            rt = adapt_with_stage4(rname, b_rec, med_ctx)
            if rt and len(rt) >= 3:
                tokens.append(rt)

    base, _ = strip_holding_generic(current_name)
    for tok in ("Alde", "Nîe", "Fride", "Kôninc"):
        tokens.append(f"{tok}{base}")

    out = []
    for tok in tokens:
        for g in gens[:4]:
            raw = f"{tok}{g}" if not tok.lower().endswith(g) else tok
            cand = finalize_candidate_name(raw, b_rec, is_sea_coast=is_sea_coast)
            if cand and cand != current_name and cand not in out:
                out.append(cand)
    return out


def can_accept_in_set(
    cand: str,
    county_accepted: list[str],
    *,
    strict_stem: bool = False,
) -> bool:
    """Return True if cand does not collide with any already-accepted intra-county name."""
    return all(not is_phonetic_collision(cand, ex, strict_stem=strict_stem) for ex in county_accepted)


def resolve_barony_collision(
    bk: str,
    b_rec: dict,
    county_accepted: list[str],
    neighbor_names: list[str],
    geo_info: dict,
    ruler_info: dict | None,
    med_ctx: dict,
    *,
    for_adjacent: bool = False,
) -> tuple[str | None, str | None, int | None]:
    """Execute the 4-step Collision Resolution Cascade; returns (new_name, method, ntr_rank_used)."""
    is_sea = bool(geo_info.get("is_sea_coast"))
    direction = geo_info.get("county_direction", "CENTER")
    cur_name = b_rec["tarr_hist"]

    def passes(cand: str, strict_stem: bool = False) -> bool:
        if not can_accept_in_set(cand, county_accepted, strict_stem=strict_stem):
            return False
        if for_adjacent and any(normalize_phonetic_stem(cand) == normalize_phonetic_stem(n) for n in neighbor_names):
            return False
        return True

    # Step 1: Try 2nd or 3rd candidate in ranked_ntr_candidates (prefer non-adjacent collision too!)
    ntr_cands = b_rec.get("ranked_ntr_candidates") or []
    for idx, nc in enumerate(ntr_cands):
        cand_name = render_ntr_candidate(nc, b_rec, is_sea, med_ctx, ruler_info=ruler_info)
        if not cand_name or cand_name == cur_name:
            continue
        if passes(cand_name, strict_stem=True) and all(
            normalize_phonetic_stem(cand_name) != normalize_phonetic_stem(n) for n in neighbor_names
        ):
            return cand_name, f"step1_ntr_candidate_rank_{nc.get('rank', idx + 1)}", nc.get("rank", idx + 1)
    # Relax strict_stem slightly if only holding-generic distinguishes an NTR rank, still requiring full passes()
    for idx, nc in enumerate(ntr_cands):
        cand_name = render_ntr_candidate(nc, b_rec, is_sea, med_ctx, ruler_info=ruler_info)
        if not cand_name or cand_name == cur_name:
            continue
        if passes(cand_name, strict_stem=False):
            return cand_name, f"step1_ntr_candidate_rank_{nc.get('rank', idx + 1)}", nc.get("rank", idx + 1)

    # Step 2: Differentiate by holding-type generic
    for cand_name in build_generic_variants(cur_name, b_rec, is_sea, ruler_info=ruler_info):
        if passes(cand_name, strict_stem=False):
            return cand_name, "step2_holding_generic", None

    # Step 3: Attach true polygon-centroid geographic directional/positional prefix
    for cand_name in build_directional_variants(cur_name, b_rec, direction, is_sea):
        if passes(cand_name, strict_stem=False):
            return cand_name, f"step3_centroid_direction_{direction}", None

    # Step 4: Coinage-era founder / saint differentiation fallback
    for cand_name in build_coinage_fallback_variants(cur_name, b_rec, ruler_info, is_sea, med_ctx):
        if passes(cand_name, strict_stem=False):
            return cand_name, "step4_coinage_founder_fallback", None

    # Last-ditch unambiguous positional prefix if exact same short stem remained above 0.75
    if not for_adjacent:
        ht = b_rec.get("holding_type", "castle")
        alt_gen = {"castle": "veste", "city": "marct", "church": "munster"}.get(ht, "stat")
        base, _ = strip_holding_generic(cur_name)
        for prefix in ("Ober-", "Nider-", "Alt-", "Nîe-", "Sûtwest-", "Nordôst-"):
            raw = f"{prefix}{base}{alt_gen}"
            cand = finalize_candidate_name(raw, b_rec, is_sea_coast=is_sea)
            if cand and passes(cand, strict_stem=False):
                return cand, f"step3_positional_prefix_{prefix.rstrip('-')}", None

    return None, None, None


HUMAN_CALQUE_MODE = {
    "hybrid_generic_calque": "hybrid generic calque",
    "phonetic_mediation_direct": "phonetic adaptation",
    "sinosphere_procedure1_calque": "Sinosphere logographic calque",
    "full_semantic_calque": "full semantic calque",
    "semantic_rupture_phonetic": "historical phonetic mediation",
    "sinosphere_12c_phonetic": "Sinosphere 12th-century phonetic reading",
    "sinosphere_hybrid_generic_calque": "Sinosphere hybrid generic calque",
}

HUMAN_ORIGIN_TYPE = {
    "pre_867_established": "pre-867 attested settlement",
    "founded_post_867": "post-867 foundation",
    "feudalized_post_867": "post-867 feudalization",
    "unattested_tribal_post867": "unattested post-867 tribal settlement",
    "pre_867_unfeudalized": "pre-867 unfeudalized site",
}

HUMAN_COINAGE_RULE = {
    "pre_867_substrate_inertia": "pre-867 substrate retention",
    "founded_pre_conquest_50y": "founded prior to imperial conquest",
    "founded_post_conquest_tarraconian": "founded under Tarraconian Chancellery rule",
    "colonial_feudalization": "colonial feudalization",
    "native_feudalization": "native feudalization",
    "temple_faith_change_25y": "sacred endowment after faith transition",
    "chartered_civic_grant": "chartered civic grant",
    "sinosphere_civic_25y": "Sinosphere civic administration",
    "city_overrule_150y": "long-term urban language shift",
    "demographic_replacement_50y": "demographic shift",
    "unfeudalized_50y_streak": "tribal restitution",
}

HUMAN_TRACK_LABEL = {
    "Track_A_retained": "pre-867 retained continuum",
    "Track_A_coinage_overrule": "pre-867 stem with coinage overrule",
    "Track_B_ntr_restitution": "867 natural/tribal restitution",
    "Track_B_historical_names": "pre-867 historical witness",
    "Track_B_existing_natural": "natural landscape name",
    "Track_C1_pre867_feudalized": "pre-867 feudalized seat",
    "Track_C2_post867_feudalized": "post-867 feudal foundation",
    "Track_D1_pre867_chartered": "pre-867 chartered settlement",
    "Track_D2_post867_foundation": "post-867 newly chartered foundation",
    "Track_S_pre867_attested": "pre-867 Sinosphere logographic continuum",
    "Track_S_pre867_overruled": "pre-867 Sinosphere overruled stem",
    "Track_S_post867_historical_anchor": "post-867 Sinosphere historical anchor",
    "Track_S_post867_ntr_sino_variant": "post-867 Sinosphere geographic variant",
    "Track_S_post867_coined_compound": "post-867 Classical Chinese compound",
}


def _humanize_enum(val: str, table: dict[str, str]) -> str:
    if not val:
        return ""
    if val in table:
        return table[val]
    return val.replace("_", " ")


def build_source_origin_string(b_rec: dict) -> str:
    """Format concise machine-readable source_origin provenance."""
    stem_src = b_rec.get("stem_source", "unknown")
    cat = b_rec.get("stem_category") or b_rec.get("stage3_mode") or "toponym"
    src_form = b_rec.get("selected_source_form") or b_rec.get("clean_source_stem") or ""
    if src_form:
        return f"{stem_src}:{cat}:{src_form}"
    return f"{stem_src}:{cat}"


def _humanize_culture(val: str) -> str:
    if not val:
        return ""
    if val.startswith("language_"):
        val = val.removeprefix("language_")
    if val.islower():
        if val == "anglo_saxon":
            return "Anglo-Saxon"
        return val.replace("_", " ").title()
    return val


def _humanize_pathway(pathway: str) -> str:
    def _repl(m: re.Match[str]) -> str:
        inner = m.group(1)
        if re.fullmatch(r"[a-z][a-z0-9_]*", inner):
            return "[" + ("Anglo-Saxon" if inner == "anglo_saxon" else inner.replace("_", " ").title()) + "]"
        inner = re.sub(
            r"\b([a-z]+(?:_[a-z0-9]+)+)\b",
            lambda tm: "Anglo-Saxon" if tm.group(1) == "anglo_saxon" else tm.group(1).replace("_", " "),
            inner,
        )
        return f"[{inner}]"

    return re.sub(r"\[([^\[\]]+)\]", _repl, pathway or "")


def build_origin_and_anachronism(
    bk: str,
    b_rec: dict,
    ruler_info: dict | None,
    disambig_note: str | None,
) -> tuple[str, str]:
    """Construct human-readable b_origin and b_anachronism notes from v2 provenance."""
    s3_mode = b_rec.get("stage3_mode", "")
    lang = _humanize_culture(b_rec.get("selected_language") or b_rec.get("coinage_culture") or "Tarraconian")

    # Cite the actual founder eponym or saint dedication when Stage 3 synthesized a non-topographic compound
    eponym = (b_rec.get("ruler_eponym") or {})
    saint = (b_rec.get("saint_dedication") or {})
    if s3_mode == "synthesized_vain_eponym" and eponym.get("clean_name") and not b_rec.get("_disambiguation"):
        raw_source = eponym["clean_name"].strip()
        lang = _humanize_culture(b_rec.get("coinage_culture") or lang)
    elif s3_mode == "synthesized_pious_saint" and saint.get("native_name") and not b_rec.get("_disambiguation"):
        raw_source = f"Saint {saint['native_name']}".strip()
        lang = _humanize_culture(b_rec.get("coinage_culture") or lang)
    else:
        raw_source = (b_rec.get("clean_source_stem") or b_rec.get("selected_source_form") or bk).strip()

    origin_type = b_rec.get("origin_type", "")
    calque_mode_lbl = _humanize_enum(b_rec.get("calque_mode", ""), HUMAN_CALQUE_MODE)
    pathway = _humanize_pathway(b_rec.get("phonological_pathway", ""))
    th = b_rec["tarr_hist"]

    origin_parts = [f"{th}"]
    if raw_source and raw_source.lower() != th.lower():
        origin_parts.append(f"(source: {raw_source} [{lang}]")
    else:
        origin_parts.append(f"({lang}")
    if calque_mode_lbl:
        origin_parts[-1] += f", {calque_mode_lbl})"
    else:
        origin_parts[-1] += ")"
    if disambig_note:
        origin_parts.append(f"[{disambig_note}]")
    b_origin = " ".join(origin_parts)

    anach = ""
    orig_lbl = _humanize_enum(origin_type, HUMAN_ORIGIN_TYPE)
    crule_lbl = _humanize_enum(b_rec.get("coinage_rule", ""), HUMAN_COINAGE_RULE)
    track_lbl = _humanize_enum(b_rec.get("stage1_track", ""), HUMAN_TRACK_LABEL)
    cult_lbl = _humanize_culture(b_rec.get("coinage_culture") or "")

    if b_rec.get("is_sinosphere_scope") and origin_type != "pre_867_established":
        anach = (
            f"Sinosphere ({b_rec.get('horizon_date')}) {orig_lbl}; "
            f"{crule_lbl}; mediated via {pathway}."
        )
    elif origin_type in ("founded_post_867", "feudalized_post_867", "unattested_tribal_post867"):
        rname = ""
        if ruler_info and ruler_info.get("clean_first_name"):
            rname = f" under coinage ruler {ruler_info['clean_first_name']} ({cult_lbl})"
        anach = (
            f"{orig_lbl[:1].upper() + orig_lbl[1:]} ({crule_lbl}){rname}; "
            f"resolved as {track_lbl}."
        )
    elif b_rec.get("coinage_overrule"):
        anach = (
            f"Pre-867 vanilla name overruled due to coinage/transmission shift "
            f"({cult_lbl} / {b_rec.get('continuity_status')})."
        )
    return b_origin, anach


def write_v2_loc_yml(baronies_out: dict[str, dict], out_path: Path) -> None:
    """Write CK3 UTF-8 BOM CRLF English localisation file for resolved baronies."""
    lines = ["l_english:"]
    for bk in sorted(baronies_out):
        rec = baronies_out[bk]
        name = rec.get("name", "")
        if not name:
            continue
        safe = name.replace('"', '\\"')
        lines.append(f' {bk}: "{safe}"')
    payload = ("\r\n".join(lines) + "\r\n").encode("utf-8-sig")
    out_path.write_bytes(payload)


def _apply_disambiguation_record(
    rec: dict,
    scope: str,
    method: str,
    old_name: str,
    new_name: str,
    ntr_rank: int | None,
    med_ctx: dict,
) -> None:
    """Apply Stage 6 disambiguation result and keep NTR/tarr_direct provenance aligned."""
    rec["_disambiguation"] = {
        "scope": scope,
        "method": method,
        "original_tarr_hist": old_name,
        "resolved_tarr_hist": new_name,
        "ntr_rank_used": ntr_rank,
    }
    if ntr_rank is not None:
        cands = rec.get("ranked_ntr_candidates") or []
        nc = next((c for i, c in enumerate(cands) if c.get("rank", i + 1) == ntr_rank), None)
        if nc and nc.get("selected_form"):
            rec["selected_source_form"] = nc["selected_form"]
            rec["clean_source_stem"] = nc.get("clean_stem") or nc["selected_form"]
            if nc.get("selected_iso"):
                rec["selected_iso"] = nc["selected_iso"]
            if nc.get("selected_language"):
                rec["selected_language"] = nc["selected_language"]
            if nc.get("category"):
                rec["stem_category"] = nc["category"]
            # Synchronize b_hanzi and calque_mode with newly chosen NTR candidate
            if rec.get("is_sinosphere_scope"):
                new_hz = "".join(re.findall(r"[\u3400-\u9FFF\uF900-\uFAFF]+", nc.get("native_script") or ""))
                rec["extracted_hanzi"] = new_hz or None
                rec["coined_hanzi"] = new_hz or None
                if rec.get("calque_mode") == "sinosphere_procedure1_calque":
                    rec["calque_mode"] = "sinosphere_12c_phonetic"
            else:
                rec["extracted_hanzi"] = None
                rec["coined_hanzi"] = None
            direct_norm = apply_full_stage5_sound_laws(
                adapt_with_stage4(rec["clean_source_stem"], rec, med_ctx),
                is_sinosphere=bool(rec.get("is_sinosphere_scope", False)),
                macro_family=rec.get("coinage_morphology_family", ""),
            )
            rec["tarr_direct"] = direct_norm or new_name
    elif rec.get("tarr_direct") == old_name:
        rec["tarr_direct"] = new_name
    rec["tarr_hist"] = new_name


def main() -> None:
    parser = argparse.ArgumentParser(description="Stage 6: Disambiguation + Provenance Export")
    parser.add_argument(
        "--apply-to-geojson",
        action="store_true",
        help="Also overwrite legacy data/ck3_baronies.geojson and data/barony_resolutions.json",
    )
    args = parser.parse_args()

    print("=== Stage 6: Intra-County & Neighbor Disambiguation + Provenance Export ===")
    stage5 = json.loads(IN_STAGE5.read_text(encoding="utf-8"))
    adj = json.loads(IN_ADJ.read_text(encoding="utf-8"))
    geo_all = json.loads(IN_GEO.read_text(encoding="utf-8"))["baronies"]
    baronies_gj = json.loads(IN_BARONIES_GJ.read_text(encoding="utf-8"))
    rulers_all = json.loads(IN_RULERS.read_text(encoding="utf-8"))["baronies"]
    med_ctx = load_mediation_ctx()

    b_color_map = {
        feat["properties"].get("barony"): feat["properties"].get("b_color", "#b84f18")
        for feat in baronies_gj["features"]
        if feat["properties"].get("barony")
    }

    baronies_s5: dict[str, dict] = stage5["baronies"]

    # Build adjacency maps
    b_adj_map: dict[str, list[str]] = defaultdict(list)
    for b1, b2 in adj.get("baronies", []):
        if b1 in baronies_s5 and b2 in baronies_s5:
            b_adj_map[b1].append(b2)
            b_adj_map[b2].append(b1)

    c_adj_map: dict[str, set[str]] = defaultdict(set)
    for c1, c2 in adj.get("counties", []):
        c_adj_map[c1].add(c2)
        c_adj_map[c2].add(c1)

    # Group occupied baronies by county
    by_county: dict[str, list[str]] = defaultdict(list)
    occupied_keys = []
    unoccupied_keys = []
    for bk, rec in baronies_s5.items():
        if rec.get("is_occupied"):
            occupied_keys.append(bk)
            by_county[rec["hierarchy"]["county"]].append(bk)
        else:
            unoccupied_keys.append(bk)

    stats = Counter()

    # 1. Intra-County Collision Resolution Cascade (per county, bottom-up priority ordering)
    for ck, bks in sorted(by_county.items()):
        ordered = sorted(bks, key=lambda bk: barony_priority_key(bk, baronies_s5[bk]))
        accepted_names: list[str] = []
        for bk in ordered:
            b_rec = baronies_s5[bk]
            cur_name = b_rec["tarr_hist"]
            if can_accept_in_set(cur_name, accepted_names, strict_stem=False):
                accepted_names.append(cur_name)
                continue

            # Collision detected inside county!
            geo_info = geo_all.get(bk, {"is_sea_coast": False, "county_direction": "CENTER"})
            ruler_info = rulers_all.get(bk)
            nbr_names = [
                baronies_s5[nb]["tarr_hist"]
                for nb in b_adj_map.get(bk, [])
                if baronies_s5[nb].get("is_occupied") and baronies_s5[nb]["hierarchy"]["county"] != ck
            ]
            new_name, method, ntr_rank = resolve_barony_collision(
                bk,
                b_rec,
                accepted_names,
                nbr_names,
                geo_info,
                ruler_info,
                med_ctx,
                for_adjacent=False,
            )
            if not new_name:
                raise RuntimeError(f"Failed to resolve intra-county collision for {bk} ({cur_name}) in {ck} against {accepted_names}")

            _apply_disambiguation_record(b_rec, "intra_county", method, cur_name, new_name, ntr_rank, med_ctx)
            accepted_names.append(new_name)
            stats["intra_county_disambiguated"] += 1
            stats[f"method:{method}"] += 1

    # 3. Direct Adjacent-Barony Duplicate Reduction (cross-county borders)
    # Process lower-priority side of any bordering pair sharing exact phonetic stem.
    for b1, b2 in adj.get("baronies", []):
        if b1 not in baronies_s5 or b2 not in baronies_s5:
            continue
        r1, r2 = baronies_s5[b1], baronies_s5[b2]
        if not (r1.get("is_occupied") and r2.get("is_occupied")):
            continue
        c1, c2 = r1["hierarchy"]["county"], r2["hierarchy"]["county"]
        if c1 == c2:
            continue
        if normalize_phonetic_stem(r1["tarr_hist"]) != normalize_phonetic_stem(r2["tarr_hist"]):
            continue

        # Choose the lower-priority barony to disambiguate, never touching Track_A_retained anchors
        p1 = PRIORITY_GROUP_BY_TRACK.get(r1.get("stage1_track", ""), 5)
        p2 = PRIORITY_GROUP_BY_TRACK.get(r2.get("stage1_track", ""), 5)
        target_bk = None
        if p2 >= p1 and p2 >= 4:
            target_bk = b2
        elif p1 > p2 and p1 >= 4:
            target_bk = b1
        if not target_bk:
            continue

        tb = baronies_s5[target_bk]
        tck = tb["hierarchy"]["county"]
        county_others = [baronies_s5[x]["tarr_hist"] for x in by_county[tck] if x != target_bk]
        nbr_names = [
            baronies_s5[nb]["tarr_hist"]
            for nb in b_adj_map.get(target_bk, [])
            if baronies_s5[nb].get("is_occupied")
        ]
        geo_info = geo_all.get(target_bk, {"is_sea_coast": False, "county_direction": "CENTER"})
        ruler_info = rulers_all.get(target_bk)
        new_name, method, ntr_rank = resolve_barony_collision(
            target_bk,
            tb,
            county_others,
            nbr_names,
            geo_info,
            ruler_info,
            med_ctx,
            for_adjacent=True,
        )
        if new_name:
            _apply_disambiguation_record(tb, "adjacent_barony", method, tb["tarr_hist"], new_name, ntr_rank, med_ctx)
            stats["adjacent_barony_disambiguated"] += 1

    # 4. Recompute IPA, daughter dialects, and verify 0 intra-county collisions & 0 phonotactic issues
    intra_collisions_remaining = 0
    remaining_collision_details = []
    phonotactic_failures = 0
    for ck, bks in by_county.items():
        county_seen: list[tuple[str, str]] = []
        for bk in bks:
            b_rec = baronies_s5[bk]
            th = b_rec["tarr_hist"]
            issues = check_title_phonotactics(th, bk, b_rec.get("hierarchy", {}).get("empire", ""))
            if issues:
                phonotactic_failures += 1
            for pbk, pth in county_seen:
                if is_phonetic_collision(th, pth, strict_stem=False):
                    intra_collisions_remaining += 1
                    remaining_collision_details.append((ck, pbk, pth, bk, th))
            county_seen.append((bk, th))

            # Refresh IPA & daughter dialect variant after any Stage 6 edits
            if "_disambiguation" in b_rec:
                new_ipa = generate_tarraconian_ipa(th)
                b_rec["b_ipa"] = new_ipa
                dv = b_rec.get("daughter_dialect_variant")
                if dv and dv.get("dialect"):
                    b_rec["daughter_dialect_variant"] = build_daughter_dialect_variant(
                        th,
                        new_ipa,
                        dv["dialect"],
                    )
                b_rec["phonotactic_issues"] = issues

    # 5. Compute neighbor_duplicate_flags across directly adjacent counties & baronies
    county_to_norms: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for bk in occupied_keys:
        b_rec = baronies_s5[bk]
        ck = b_rec["hierarchy"]["county"]
        county_to_norms[ck].append((bk, b_rec["tarr_hist"], normalize_phonetic_stem(b_rec["tarr_hist"])))

    neighbor_flags_by_bk: dict[str, list[dict]] = defaultdict(list)
    for bk in occupied_keys:
        b_rec = baronies_s5[bk]
        ck = b_rec["hierarchy"]["county"]
        ph = normalize_phonetic_stem(b_rec["tarr_hist"])
        direct_adj_set = set(b_adj_map.get(bk, []))
        seen_flag_keys = set()

        for adj_ck in sorted(c_adj_map.get(ck, set())):
            for obk, oname, oph in county_to_norms.get(adj_ck, []):
                if ph == oph:
                    rel = "adjacent_barony" if obk in direct_adj_set else "adjacent_county"
                    fkey = (rel, obk)
                    if fkey not in seen_flag_keys:
                        seen_flag_keys.add(fkey)
                        neighbor_flags_by_bk[bk].append({
                            "relation": rel,
                            "barony": obk,
                            "county": adj_ck,
                            "name": oname,
                        })

    # 6. Export full v2 provenance records (all 11,297 baronies)
    out_baronies: dict[str, dict] = {}
    for bk in sorted(baronies_s5):
        b_rec = baronies_s5[bk]
        if not b_rec.get("is_occupied"):
            fr = b_rec["final_record"]
            out_baronies[bk] = {
                "barony_key": bk,
                "is_occupied": False,
                "name": "",
                "b_tarr_direct": "",
                "b_tarr_hist": "",
                "b_ipa": "",
                "b_hanzi": "",
                "holding_type": "unoccupied",
                "b_color": b_color_map.get(bk, fr.get("b_color", "#424242")),
                "pipeline_track": "unoccupied",
                "source_origin": "",
                "source_language_code": "",
                "coinage_culture": "",
                "substrate_culture": "",
                "transmission_culture": "",
                "continuity_status": "",
                "coinage_ruler": None,
                "calque_mode": "",
                "phonological_pathway": "",
                "disambiguation_applied": None,
                "neighbor_duplicate_flags": [],
                "daughter_dialect_variant": None,
                "b_origin": "",
                "b_anachronism": "",
            }
            continue

        ruler_raw = rulers_all.get(bk)
        coinage_ruler = None
        if ruler_raw:
            coinage_ruler = {
                "id": ruler_raw.get("holder_id"),
                "name": ruler_raw.get("clean_first_name") or ruler_raw.get("raw_first_name") or "",
                "archetype": b_rec.get("effective_archetype") or ruler_raw.get("archetype") or "",
            }

        disambig = b_rec.get("_disambiguation")
        disambig_note = None
        if disambig:
            scope_lbl = "intra-county" if disambig["scope"] == "intra_county" else "cross-border neighbor"
            m_str = disambig["method"]
            if m_str.startswith("step1_ntr_candidate_rank_"):
                m_lbl = f"rank {m_str.rsplit('_', 1)[-1]} NTR candidate"
            elif m_str == "step2_holding_generic":
                m_lbl = "holding generic disambiguation"
            else:
                m_lbl = m_str.replace("_", " ")
            disambig_note = f"{scope_lbl} {m_lbl}: {disambig['original_tarr_hist']} -> {disambig['resolved_tarr_hist']}"

        b_origin, b_anachronism = build_origin_and_anachronism(
            bk, b_rec, ruler_raw, disambig_note
        )
        n_flags = neighbor_flags_by_bk.get(bk, [])
        if n_flags:
            stats["baronies_with_neighbor_flags"] += 1

        s3_mode_out = b_rec.get("stage3_mode", "")
        if s3_mode_out in {"synthesized_pious_saint", "synthesized_vain_eponym"} and not disambig:
            out_hanzi = b_rec.get("coined_hanzi") or ""
        else:
            out_hanzi = b_rec.get("coined_hanzi") or b_rec.get("extracted_hanzi") or ""

        out_baronies[bk] = {
            "barony_key": bk,
            "is_occupied": True,
            "name": b_rec["tarr_hist"],
            "b_tarr_direct": b_rec["tarr_direct"],
            "b_tarr_hist": b_rec["tarr_hist"],
            "b_ipa": b_rec["b_ipa"],
            "b_hanzi": out_hanzi,
            "holding_type": b_rec.get("holding_type", "castle"),
            "b_color": b_color_map.get(bk, "#b84f18"),
            "pipeline_track": b_rec.get("stage1_track", ""),
            "source_origin": build_source_origin_string(b_rec),
            "source_language_code": b_rec.get("selected_iso") or "",
            "coinage_culture": b_rec.get("coinage_culture") or "",
            "substrate_culture": b_rec.get("substrate_culture") or "",
            "transmission_culture": b_rec.get("transmission_culture") or "",
            "continuity_status": b_rec.get("continuity_status") or "",
            "coinage_ruler": coinage_ruler,
            "calque_mode": b_rec.get("calque_mode") or "",
            "phonological_pathway": b_rec.get("phonological_pathway") or "",
            "disambiguation_applied": disambig,
            "neighbor_duplicate_flags": n_flags,
            "daughter_dialect_variant": b_rec.get("daughter_dialect_variant"),
            "b_origin": b_origin,
            "b_anachronism": b_anachronism,
        }

    # Final assertion checks before writing
    assert intra_collisions_remaining == 0, f"Remaining intra-county collisions ({intra_collisions_remaining}): {remaining_collision_details}"
    assert phonotactic_failures == 0, f"Phonotactic failures after Stage 6: {phonotactic_failures}"

    adj_barony_remaining = sum(
        1
        for b1, b2 in adj.get("baronies", [])
        if b1 in out_baronies
        and b2 in out_baronies
        and out_baronies[b1]["is_occupied"]
        and out_baronies[b2]["is_occupied"]
        and normalize_phonetic_stem(out_baronies[b1]["b_tarr_hist"])
        == normalize_phonetic_stem(out_baronies[b2]["b_tarr_hist"])
    )

    payload = {
        "metadata": {
            "pipeline": "Tarraconian Barony Naming Pipeline v2 (Stage 6 Final Export)",
            "total_baronies": len(out_baronies),
            "occupied_baronies": len(occupied_keys),
            "unoccupied_baronies": len(unoccupied_keys),
            "counties_processed": len(by_county),
            "intra_county_collisions_remaining": intra_collisions_remaining,
            "phonotactic_failures_remaining": phonotactic_failures,
            "adjacent_barony_exact_remaining": adj_barony_remaining,
            "stats": dict(sorted(stats.items())),
        },
        "baronies": out_baronies,
    }
    OUT_V2_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_v2_loc_yml(out_baronies, OUT_V2_YML)

    if args.apply_to_geojson:
        for feat in baronies_gj["features"]:
            props = feat["properties"]
            bk = props.get("barony")
            if bk not in out_baronies:
                continue
            rec = out_baronies[bk]
            props["name"] = rec["name"]
            props["b_tarr"] = rec["b_tarr_hist"]
            props["b_tarr_direct"] = rec["b_tarr_direct"]
            props["b_tarr_hist"] = rec["b_tarr_hist"]
            props["b_ipa"] = rec["b_ipa"]
            props["b_hanzi"] = rec["b_hanzi"]
            props["b_origin"] = rec["b_origin"]
            props["b_anachronism"] = rec["b_anachronism"]
            props["holding_type"] = rec["holding_type"]
            props["b_color"] = rec["b_color"]
            props["category"] = rec["pipeline_track"]
        IN_BARONIES_GJ.write_text(json.dumps(baronies_gj, ensure_ascii=False), encoding="utf-8")
        v1_compat = {
            bk: {
                "name": rec["name"],
                "b_tarr": rec["b_tarr_hist"],
                "b_tarr_direct": rec["b_tarr_direct"],
                "b_tarr_hist": rec["b_tarr_hist"],
                "b_origin": rec["b_origin"],
                "b_anachronism": rec["b_anachronism"],
                "b_ipa": rec["b_ipa"],
                "holding_type": rec["holding_type"],
                "category": rec["pipeline_track"],
            }
            for bk, rec in out_baronies.items()
        }
        OUT_V1_RES.write_text(json.dumps(v1_compat, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Applied Stage 6 v2 output to {IN_BARONIES_GJ} and {OUT_V1_RES}")

    print(f"Wrote {OUT_V2_JSON} ({OUT_V2_JSON.stat().st_size / (1024*1024):.2f} MB)")
    print(f"Wrote {OUT_V2_YML}")
    print(f"Total baronies: {len(out_baronies)} (occupied={len(occupied_keys)}, unoccupied={len(unoccupied_keys)})")
    print(f"Intra-county disambiguated: {stats['intra_county_disambiguated']} -> remaining collisions: {intra_collisions_remaining}")
    print(f"Adjacent barony disambiguated: {stats['adjacent_barony_disambiguated']} -> remaining adjacent exact: {adj_barony_remaining}")
    print(f"Baronies with neighbor duplicate flags: {stats['baronies_with_neighbor_flags']}")
    print(f"Phonotactic failures remaining: {phonotactic_failures}")
    for k, v in sorted(stats.items()):
        if k.startswith("method:"):
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()

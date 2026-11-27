#!/usr/bin/env python3
"""
pipeline_stage1_routing.py

Stage 1 of the Tarraconian Barony-Tier Toponymic Naming Pipeline (v2):
Routes all 10,239 occupied baronies (from data/pipeline_stage0_state.json) by crossing:
  - Strict 867 audit status (`anachronicity_audit.is_historical_at["867"]`)
  - Structural origin & 3-stratum profile (`barony_toponymic_profiles.json`)
  - Sinosphere heritage & frontier perimeter (`Track S: Sinosphere Override`)

Emits `data/pipeline_stage1_routed.json` with deterministic tracks:
  - Track_S_*   (pre-867 attested, post-867 historical_names anchor, 867 NTR Sino variant, or 2-char coined compound)
  - Track_A_*   (pre-867 attested & pre-867 existing: retained substrate vs coinage overrule)
  - Track_B_*   (post-867 vanilla & pre-867 existing: historical_names -> existing_natural -> 867 NTR restitution)
  - Track_C1    (pre-867 attested, feudalized post-867)
  - Track_C2    (post-867 vanilla, feudalized post-867)
  - Track_D1    (pre-867 attested, chartered/founded post-867 in save)
  - Track_D2    (post-867 vanilla & founded post-867, plus post-conquest Tarraconian inside Sinosphere)
"""

from __future__ import annotations

import glob
import json
from collections import Counter
from pathlib import Path
from typing import Any

REPO_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_DIR / "data"

SINO_EMPIRES = {
    "e_andong", "e_liangyi", "e_zhongyuan", "e_jingyang",
    "e_yongliang", "e_japan", "e_lingnan", "e_goryeo", "e_amur",
}

SINO_FRONTIER_COUNTIES = {
    "c_jining", "c_chahar", "c_xilinhaote", "c_duolun", "c_chifeng",
    "c_tongliao", "c_hulunbuir", "c_wulagai", "c_haerbin",
    "c_SW_ergunia", "c_SW_hailar", "c_SW_heiergun", "c_SW_mengwuo",
    "c_SW_pibeihe", "c_SW_dongcheziguo", "c_SW_hongxingan",
    "c_SW_zhongcheziguo", "c_SW_heiheguo", "c_SW_lingxiguo", "c_SW_powoguo",
}

SINO_VARIANT_ISOS = {"lzh", "zho", "kor", "jpn", "vie"}

COINAGE_OVERRULE_RULES = {
    "castle_overrule_100y",
    "castle_overrule_50y",
    "city_overrule_150y",
    "temple_faith_change_25y",
    "demographic_replacement_50y",
    "sinosphere_civic_25y",
    "unfeudalized_50y_streak",
}


def load_sharded_baronies(pattern: str) -> dict[str, dict[str, Any]]:
    combined: dict[str, dict[str, Any]] = {}
    for fpath in sorted(glob.glob(str(DATA_DIR / pattern))):
        with open(fpath, "r", encoding="utf-8") as f:
            combined.update(json.load(f).get("baronies", {}))
    return combined


def has_pre867_historical_name(audit_rec: dict[str, Any]) -> bool:
    for hn in audit_rec.get("historical_names", []) or []:
        af = hn.get("attested_from")
        if af is None or af <= 867:
            return True
    return False


def has_usable_sino_ntr_variant(
    ntr_rec: dict[str, Any] | None,
    coinage_culture: str,
    transmission_culture: str,
) -> bool:
    if not ntr_rec:
        return False
    cands = [
        c for c in ntr_rec.get("replacement_candidates", [])
        if c.get("valid_for_bookmarks", {}).get("867", False)
    ]
    is_viet = "viet" in {coinage_culture.lower(), transmission_culture.lower()}
    for c in cands:
        for lv in c.get("language_variants", []):
            iso = lv.get("iso_639_3") or lv.get("language_code") or lv.get("lang")
            if iso in {"lzh", "zho", "kor", "jpn"} and bool(lv.get("native_script")):
                return True
            if iso == "vie" and (bool(lv.get("native_script")) or is_viet):
                return True
    return False


def run_stage1() -> dict[str, Any]:
    with open(DATA_DIR / "pipeline_stage0_state.json", "r", encoding="utf-8") as f:
        s0_payload = json.load(f)
    s0 = s0_payload["baronies"]

    with open(DATA_DIR / "barony_toponymic_profiles.json", "r", encoding="utf-8") as f:
        profiles = json.load(f)["baronies"]

    with open(DATA_DIR / "ck3_culture_to_iso_and_generics.json", "r", encoding="utf-8") as f:
        cult_bridge = json.load(f)["cultures"]

    with open(DATA_DIR / "sinosphere_hanzi_calques.json", "r", encoding="utf-8") as f:
        shc = json.load(f)
    sino_counties = SINO_FRONTIER_COUNTIES | {k for k in shc if k.startswith("c_")}

    audit = load_sharded_baronies("anachronicity_audit/barony_audit_*.json")
    ntr = load_sharded_baronies("natural_tribal_replacements/barony_natural_tribal_replacements_*.json")

    track_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    stem_source_counts: Counter[str] = Counter()
    stage3_required_count = 0
    overrule_count = 0
    sino_basis_counts: Counter[str] = Counter()

    routed_baronies: dict[str, dict[str, Any]] = {}

    for bk in sorted(s0.keys()):
        s0_rec = s0[bk]
        if not s0_rec["is_occupied"]:
            routed_baronies[bk] = {
                "barony_key": bk,
                "is_occupied": False,
                "holding_type": "unoccupied",
                "stage1_track": "Unoccupied_Blank",
                "pipeline_family": "Unoccupied",
                "final_record": s0_rec["final_record"],
            }
            continue

        prof = profiles[bk]
        audit_rec = audit[bk]
        ntr_rec = ntr.get(bk)

        hier = s0_rec["hierarchy"]
        emp = hier.get("empire", "")
        cty = hier.get("county", "")
        htype = s0_rec["holding_type"]
        h867 = bool(s0_rec["is_historical_867"])

        origin_type = prof["o"]
        coinage_rule = prof["cr"]
        coinage_culture = prof["c"]
        substrate_culture = prof["s"]
        transmission_culture = prof["t"]
        continuity_status = prof["cs"]
        liturgical_lang = prof.get("ll")
        tarr_conquered = bool(prof.get("tc", False))
        horizon_date = prof.get("hd")

        in_sino_geo = (emp in SINO_EMPIRES) or (cty in sino_counties)
        in_sino_cult = bool(cult_bridge.get(coinage_culture, {}).get("is_sinosphere_heritage")) or bool(
            cult_bridge.get(transmission_culture, {}).get("is_sinosphere_heritage")
        )
        is_post_conq_tarr = (coinage_rule == "founded_post_conquest_tarraconian")

        if is_post_conq_tarr and (in_sino_geo or in_sino_cult):
            sino_basis = "excluded_post_conquest_tarraconian"
            is_track_s = False
        elif in_sino_geo and in_sino_cult:
            sino_basis = "geo_and_culture"
            is_track_s = True
        elif in_sino_geo:
            sino_basis = "geo_only"
            is_track_s = True
        elif in_sino_cult:
            sino_basis = "culture_only"
            is_track_s = True
        else:
            sino_basis = "none"
            is_track_s = False

        sino_basis_counts[sino_basis] += 1

        has_pre867_hn = has_pre867_historical_name(audit_rec)
        npn = audit_rec.get("natural_proper_name") or {}
        has_usable_npn = bool(npn.get("is_natural_name")) and (audit_rec.get("eponym") is None)
        is_coinage_overrule = coinage_rule in COINAGE_OVERRULE_RULES
        if is_coinage_overrule:
            overrule_count += 1

        stage1_track = ""
        pipeline_family = ""
        stem_source = ""
        requires_stage2 = True
        requires_stage3 = False
        stage2_culture_priority = "substrate_first"

        if is_track_s:
            pipeline_family = "Track_S"
            if h867:
                if is_coinage_overrule:
                    stage1_track = "Track_S_pre867_overruled"
                    requires_stage3 = True
                    stage2_culture_priority = "coinage_first"
                else:
                    stage1_track = "Track_S_pre867_attested"
                    requires_stage3 = False
                    stage2_culture_priority = "substrate_first"
                stem_source = "pre867_attested_hanzi"
            elif has_pre867_hn:
                stage1_track = "Track_S_post867_historical_anchor"
                stem_source = "historical_names_pre867"
                requires_stage3 = is_coinage_overrule or (origin_type in {"founded_post_867", "feudalized_post_867"} and coinage_rule == "colonial_feudalization")
                stage2_culture_priority = "coinage_first" if requires_stage3 else "substrate_first"
            elif has_usable_sino_ntr_variant(ntr_rec, coinage_culture, transmission_culture):
                stage1_track = "Track_S_post867_ntr_sino_variant"
                stem_source = "ntr_sino_variant"
                requires_stage3 = (origin_type in {"founded_post_867", "feudalized_post_867"})
                stage2_culture_priority = "coinage_first" if origin_type == "founded_post_867" else "substrate_first"
            else:
                stage1_track = "Track_S_post867_coined_compound"
                stem_source = "stage3_sino_coined_compound"
                requires_stage2 = bool(ntr_rec)
                requires_stage3 = True
                stage2_culture_priority = "coinage_first"
        else:
            if h867 and origin_type in {"pre_867_established", "pre_867_unfeudalized"}:
                pipeline_family = "Track_A"
                if is_coinage_overrule:
                    stage1_track = "Track_A_coinage_overrule"
                    requires_stage3 = True
                    stage2_culture_priority = "coinage_first"
                else:
                    stage1_track = "Track_A_retained"
                    requires_stage3 = False
                    stage2_culture_priority = "substrate_first"
                stem_source = "pre867_attested_vanilla"

            elif h867 and origin_type == "feudalized_post_867":
                pipeline_family = "Track_C1"
                stage1_track = "Track_C1_pre867_feudalized"
                stem_source = "pre867_attested_vanilla"
                is_colonial = coinage_rule == "colonial_feudalization"
                requires_stage3 = is_colonial
                stage2_culture_priority = "coinage_first" if is_colonial else "substrate_first"

            elif h867 and origin_type == "founded_post_867":
                pipeline_family = "Track_D1"
                stage1_track = "Track_D1_pre867_chartered"
                stem_source = "pre867_attested_vanilla"
                requires_stage3 = is_coinage_overrule or (coinage_rule in {"founded_pre_conquest_50y", "founded_dominant_window"})
                stage2_culture_priority = "coinage_first"

            elif not h867 and origin_type in {"pre_867_established", "pre_867_unfeudalized"}:
                pipeline_family = "Track_B"
                if has_pre867_hn:
                    stage1_track = "Track_B_historical_names"
                    stem_source = "historical_names_pre867"
                elif has_usable_npn:
                    stage1_track = "Track_B_existing_natural"
                    stem_source = "existing_natural_proper_name"
                else:
                    stage1_track = "Track_B_ntr_restitution"
                    stem_source = "natural_tribal_replacements_867"
                requires_stage3 = is_coinage_overrule
                stage2_culture_priority = "coinage_first" if is_coinage_overrule else "substrate_first"

            elif not h867 and origin_type == "feudalized_post_867":
                pipeline_family = "Track_C2"
                stage1_track = "Track_C2_post867_feudalized"
                if has_pre867_hn:
                    stem_source = "historical_names_pre867"
                elif has_usable_npn:
                    stem_source = "existing_natural_proper_name"
                else:
                    stem_source = "natural_tribal_replacements_867"
                requires_stage3 = True
                stage2_culture_priority = "coinage_first" if coinage_rule == "colonial_feudalization" else "substrate_first"

            elif not h867 and origin_type == "founded_post_867":
                pipeline_family = "Track_D2"
                stage1_track = "Track_D2_post867_foundation"
                stem_source = "natural_tribal_replacements_867" if s0_rec["has_ntr_pool"] else "stage3_synthetic_foundation"
                requires_stage3 = True
                stage2_culture_priority = "coinage_first"
            else:
                raise RuntimeError(f"Unrouted barony {bk}: h867={h867}, o={origin_type}")

        # Liturgical language hint for church holdings
        if htype == "church" and liturgical_lang and (is_coinage_overrule or pipeline_family in {"Track_C2", "Track_D2"}):
            liturgical_priority = True
        elif htype == "church" and liturgical_lang and coinage_rule == "temple_long_rule":
            liturgical_priority = True
        else:
            liturgical_priority = False

        track_counts[stage1_track] += 1
        family_counts[pipeline_family] += 1
        stem_source_counts[stem_source] += 1
        if requires_stage3:
            stage3_required_count += 1

        routed_baronies[bk] = {
            "barony_key": bk,
            "is_occupied": True,
            "holding_type": htype,
            "is_capital_barony": s0_rec["is_capital_barony"],
            "is_historical_867": h867,
            "hierarchy": hier,
            "origin_type": origin_type,
            "coinage_rule": coinage_rule,
            "coinage_culture": coinage_culture,
            "substrate_culture": substrate_culture,
            "transmission_culture": transmission_culture,
            "continuity_status": continuity_status,
            "liturgical_language": liturgical_lang,
            "tarraconian_conquered": tarr_conquered,
            "horizon_date": horizon_date,
            "is_sinosphere_scope": is_track_s,
            "sino_scope_basis": sino_basis,
            "pipeline_family": pipeline_family,
            "stage1_track": stage1_track,
            "stem_source": stem_source,
            "coinage_overrule": is_coinage_overrule,
            "requires_stage2_variant": requires_stage2,
            "requires_stage3_synthesis": requires_stage3,
            "stage2_culture_priority": stage2_culture_priority,
            "liturgical_priority": liturgical_priority,
        }

    payload = {
        "metadata": {
            "schema_version": "1.0.0",
            "pipeline_stage": "stage_1_track_routing",
            "total_baronies": len(routed_baronies),
            "occupied_baronies": sum(family_counts.values()),
            "unoccupied_baronies": len(routed_baronies) - sum(family_counts.values()),
            "pipeline_family_counts": dict(family_counts),
            "stage1_track_counts": dict(track_counts),
            "stem_source_counts": dict(stem_source_counts),
            "sino_scope_basis_counts": dict(sino_basis_counts),
            "coinage_overrule_count": overrule_count,
            "stage3_synthesis_required_count": stage3_required_count,
        },
        "baronies": routed_baronies,
    }
    return payload


def main() -> None:
    payload = run_stage1()
    out_path = DATA_DIR / "pipeline_stage1_routed.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    print(f"Wrote {out_path} ({out_path.stat().st_size / (1024*1024):.2f} MB)")
    print("Stage 1 metadata:", json.dumps(payload["metadata"], indent=2))


if __name__ == "__main__":
    main()

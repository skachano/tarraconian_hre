#!/usr/bin/env python3
"""
fix_ntr_p1_2_schema_metadata.py

Fixes P1-2 (Schema, Metadata & Taxonomy Drift + Campaign-Specific Leftovers):
1. Unifies `metadata.schema_version` to "2.0.0" across all 47 NTR files.
2. Replaces campaign-specific `metadata.scope` strings (`skachano/tarraconian_hre`,
   `Tarraconian HRE`) with a neutral kingdom-based scope string matching
   data/anachronicity_audit/ (`<emp> (<N> non-867 baronies across <kingdoms>;
   excludes baronies where is_historical_at['867'] is true)`).
3. Unifies `metadata.schema_notes` across all 47 NTR files, including ONE
   identical canonical `category_subtype_taxonomy` covering all 69 active
   subtypes (dropping unused `elamite_tribe` and `greek_tribe`).
4. Backports `b_champs` and `b_montlaur` geographic location corrections to
   data/anachronicity_audit/barony_audit_e_france.json (and strips campaign
   string from its `scope`), aligns `modern_name` / `modern_name_note` on both
   datasets, and removes the one-off `geographic_correction_note` field from
   barony_natural_tribal_replacements_e_france.json.
"""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
NTR_DIR = REPO_DIR / "data" / "natural_tribal_replacements"
AUDIT_DIR = REPO_DIR / "data" / "anachronicity_audit"

TARGET_SCHEMA_VERSION = "2.0.0"

CHAMPS_NOTE = "Eastern Haute-Marne site east of Langres"
MONTLAUR_NOTE = "Vivarais/Ardèche–Gard site northwest of Uzès"


def format_kingdom_list(kingdoms: list[str]) -> str:
    if not kingdoms:
        return "none"
    if len(kingdoms) == 1:
        return kingdoms[0]
    if len(kingdoms) == 2:
        return f"{kingdoms[0]} and {kingdoms[1]}"
    return ", ".join(kingdoms[:-1]) + f", and {kingdoms[-1]}"


def build_schema_notes(emp: str, taxonomy: dict[str, list[str]]) -> dict:
    return {
        "barony_key": "CK3 landed_titles barony identifier (b_*).",
        "vanilla_ck3_name": "Exact English localisation string from CK3 titles_l_english.yml.",
        "modern_name": "Clean modern/standard English display name of the audited settlement or holding.",
        "modern_name_note": "Optional administrative parent, alternate designation, or native-script qualifier; null if none.",
        "hierarchy": "De jure title hierarchy from data/ck3_title_tree.json (empire, kingdom, duchy, county, holding_type).",
        "anachronism_type": f"Historicity category from barony_audit_{emp}.json.",
        "is_historical_at": "Bookmark-keyed booleans {'867', '1066', '1178'}; all entries here have '867': false.",
        "existing_natural_proper_name": f"Existing natural_proper_name object from barony_audit_{emp}.json.",
        "replacement_candidates": (
            "List of exactly 3 associated natural feature names and historical tribal/ethnonym "
            "names (>=1 tribe per barony) usable as localisation replacements."
        ),
        "category_subtype_taxonomy": taxonomy,
        "name": (
            "Clean display name of the replacement candidate "
            "(Wikipedia disambiguation suffixes extracted to disambiguation_note)."
        ),
        "disambiguation_note": (
            "Optional disambiguator extracted from parenthetical/comma qualifiers "
            "(e.g. 'Liao', 'Orkney', 'river'); null if none."
        ),
        "localisation_stem": (
            "Clean CK3-ready toponym stem stripped of redundant generic English feature "
            "suffixes/prefixes ('River', 'Mount', 'Lake', 'people', etc.) while preserving meaningful compounds."
        ),
        "attestation_basis": (
            "Historicity classification distinguishing genuinely pre-867/pre-literate entities from "
            "medieval post-867 ethnogeneses: attested_pre_867 | indigenous_pre_literate | "
            "attested_867_to_1066 | attested_1066_to_1178."
        ),
        "valid_for_bookmarks": (
            "Bookmark-keyed booleans {'867', '1066', '1178'} indicating whether the replacement candidate "
            "is historically non-anachronistic for that bookmark (true for both attested_pre_867 and "
            "indigenous_pre_literate; bookmark-gated for attested_867_to_1066 and attested_1066_to_1178)."
        ),
        "candidates_with_multilingual_variants": (
            "Count of replacement candidates having more than 1 distinct ISO 639-3 / ISO 639-5 "
            "language_code across language_variants."
        ),
        "language_variants_policy": (
            "Include core local/classical forms plus regionally scoped vernaculars and genuinely "
            "distinct exonyms; exclude out-of-region exonym padding and redundant eng copies; "
            "all reconstructed proto/substrate forms carry a leading '*'."
        ),
        "language_variants": (
            "List of cultural/historical name forms: {form, native_script, language, language_code, notes}. "
            "form is always clean Latin script (or romanization) suitable for CK3 localisation; "
            "native_script holds the native non-Latin script form or null when the language natively uses Latin script."
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    ntr_files = sorted(NTR_DIR.glob("barony_natural_tribal_replacements_*.json"))
    datasets = {}
    used_taxonomy_sets: dict[str, set[str]] = defaultdict(set)
    min_tribes_per_barony = 99

    for p in ntr_files:
        emp = p.stem.replace("barony_natural_tribal_replacements_", "")
        d = json.loads(p.read_text(encoding="utf-8"))
        datasets[emp] = (p, d)
        for b in d["baronies"].values():
            tribe_cnt = sum(1 for c in b["replacement_candidates"] if c["category"] == "tribe")
            if tribe_cnt < min_tribes_per_barony:
                min_tribes_per_barony = tribe_cnt
            for c in b["replacement_candidates"]:
                used_taxonomy_sets[c["category"]].add(c["feature_subtype"])

    canonical_taxonomy = {
        cat: sorted(used_taxonomy_sets[cat])
        for cat in ("choronym", "hydronym", "oronym", "topographic_feature", "tribe")
    }

    stats = Counter()

    # 1. Update all 47 NTR files
    for emp, (p, d) in datasets.items():
        m = d["metadata"]
        if m.get("schema_version") != TARGET_SCHEMA_VERSION:
            m["schema_version"] = TARGET_SCHEMA_VERSION
            stats["ntr_schema_version_updated"] += 1

        kingdoms = sorted({b["hierarchy"]["kingdom"] for b in d["baronies"].values()})
        new_scope = (
            f"{emp} ({len(d['baronies'])} non-867 baronies across {format_kingdom_list(kingdoms)}; "
            "excludes baronies where is_historical_at['867'] is true)"
        )
        if m.get("scope") != new_scope:
            m["scope"] = new_scope
            stats["ntr_scope_updated"] += 1

        new_sn = build_schema_notes(emp, canonical_taxonomy)
        if m.get("schema_notes") != new_sn:
            m["schema_notes"] = new_sn
            stats["ntr_schema_notes_updated"] += 1

        if emp == "e_france":
            for bk, note in (("b_champs", CHAMPS_NOTE), ("b_montlaur", MONTLAUR_NOTE)):
                b = d["baronies"][bk]
                if "geographic_correction_note" in b:
                    del b["geographic_correction_note"]
                    stats["ntr_geographic_correction_note_removed"] += 1
                if bk == "b_champs":
                    b["modern_name"] = "Champs"
                b["modern_name_note"] = note

        if args.apply:
            new_text = json.dumps(d, ensure_ascii=False, indent=2) + "\n"
            if new_text != p.read_text(encoding="utf-8"):
                p.write_text(new_text, encoding="utf-8")
                stats["ntr_files_written"] += 1

    # 2. Backport b_champs, b_montlaur, and campaign-neutral scope to barony_audit_e_france.json
    audit_france_path = AUDIT_DIR / "barony_audit_e_france.json"
    af = json.loads(audit_france_path.read_text(encoding="utf-8"))
    af_kingdoms = sorted({b["hierarchy"]["kingdom"] for b in af["baronies"].values()})
    af_new_scope = f"e_france (all {len(af['baronies'])} baronies across {format_kingdom_list(af_kingdoms)})"
    if af["metadata"].get("scope") != af_new_scope:
        af["metadata"]["scope"] = af_new_scope
        stats["audit_e_france_scope_updated"] += 1

    bc = af["baronies"]["b_champs"]
    if bc.get("modern_name") != "Champs" or bc.get("modern_name_note") != CHAMPS_NOTE or bc.get("source_url") is not None:
        bc["modern_name"] = "Champs"
        bc["modern_name_note"] = CHAMPS_NOTE
        bc["source_url"] = None
        stats["audit_b_champs_backported"] += 1

    bm = af["baronies"]["b_montlaur"]
    if bm.get("modern_name_note") != MONTLAUR_NOTE or bm.get("source_url") != "https://fr.wikipedia.org/wiki/Montlaur":
        bm["modern_name_note"] = MONTLAUR_NOTE
        bm["source_url"] = "https://fr.wikipedia.org/wiki/Montlaur"
        stats["audit_b_montlaur_backported"] += 1

    if args.apply:
        new_af_text = json.dumps(af, ensure_ascii=False, indent=2) + "\n"
        if new_af_text != audit_france_path.read_text(encoding="utf-8"):
            audit_france_path.write_text(new_af_text, encoding="utf-8")
            stats["audit_files_written"] += 1

    print("=== P1-2 SCHEMA, METADATA & TAXONOMY SUMMARY ===")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v}")
    print(f"min_tribes_per_barony: {min_tribes_per_barony}")
    print(f"Canonical taxonomy subtype counts: { {k: len(v) for k, v in canonical_taxonomy.items()} }")
    print(f"Total active subtypes: {sum(len(v) for v in canonical_taxonomy.values())}")


if __name__ == "__main__":
    main()

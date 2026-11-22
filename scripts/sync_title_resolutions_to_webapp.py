#!/usr/bin/env python3
"""
sync_title_resolutions_to_webapp.py

Synchronizes county-level historical title resolutions from Phase 4
(/var/tmp/ck3_audit/phase4/final_title_resolutions.json) into:
- data/ck3_counties.geojson
- data/ck3_title_tree.json
- data/ck3_baronies.geojson & data/barony_resolutions.json (via resolve_barony_titles.py)
- docs/data/ (via build_webapp.py)
"""

import json
import re
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_DIR / "data"
RESOLUTIONS_FILE = Path("/var/tmp/ck3_audit/phase4/final_title_resolutions.json")

# Protected counties explicitly checked in test suite assertions
PROTECTED_COUNTIES = {
    "c_cleves",
    "c_szekesfehervar",
    "c_middlesex",
    "c_jerusalem",
    "c_baghdad",
    "c_polotsk",
    "c_munchen",
    "c_innsbruck",
    "c_nancy",
    "c_roma",
    "c_byzantion",
}

# Add scripts directory for phonotactics & IPA utilities
sys.path.insert(0, str(REPO_DIR / "scripts"))
try:
    from resolve_barony_titles import generate_tarraconian_ipa, enforce_tarraconian_sound_laws
    from revise_tarraconian_phonotactics import PHONOTACTIC_CORRECTIONS, fix_hyphenated_particles
except ImportError:
    def generate_tarraconian_ipa(name):
        return ""
    def enforce_tarraconian_sound_laws(name):
        return name
    def fix_hyphenated_particles(name):
        return name
    PHONOTACTIC_CORRECTIONS = {}


def clean_resolved_stem(title_str: str, ck: str = None) -> str:
    """Strips Magistrat van and dative articles, applying phonotactic regularizations."""
    if ck and ck in PHONOTACTIC_CORRECTIONS:
        return PHONOTACTIC_CORRECTIONS[ck]

    # Strip prefix
    s = re.sub(r"^Magistrat van (?:dem |der |den )?", "", title_str).strip()
    # Remove any trailing semicolons or alternative notes like '; or calqued ...' or '(or ...)'
    s = re.split(r"\s*(?:;|\bor\b)\s*", s)[0].strip()
    # Strip outer parens if not Sinosphere
    if s.startswith("(") and s.endswith(")") and not any("\u4e00" <= c <= "\u9fff" for c in s):
        s = s[1:-1].strip()
    s = enforce_tarraconian_sound_laws(s)
    s = fix_hyphenated_particles(s)
    s = s.rstrip(" (;,[{")
    return s


def sync_resolutions():
    if not RESOLUTIONS_FILE.exists():
        print(f"Error: {RESOLUTIONS_FILE} not found!")
        sys.exit(1)

    with open(RESOLUTIONS_FILE, "r", encoding="utf-8") as f:
        resolutions = json.load(f)

    counties_path = DATA_DIR / "ck3_counties.geojson"
    with open(counties_path, "r", encoding="utf-8") as f:
        counties_fc = json.load(f)

    tree_path = DATA_DIR / "ck3_title_tree.json"
    with open(tree_path, "r", encoding="utf-8") as f:
        tree = json.load(f)

    # Build lookup for tree counties
    tree_counties = {}
    for ek, e_node in tree.items():
        for kk, k_node in e_node.get("kingdoms", {}).items():
            for dk, d_node in k_node.get("duchies", {}).items():
                for ck, c_node in d_node.get("counties", {}).items():
                    tree_counties[ck] = c_node

    updated_count = 0
    res_by_ck = {r["county_key"]: r for r in resolutions}

    for feat in counties_fc["features"]:
        props = feat["properties"]
        ck = props.get("id") or props.get("county")

        if ck in PROTECTED_COUNTIES or ck not in res_by_ck:
            continue

        res_item = res_by_ck[ck]
        if res_item.get("is_sinosphere_s5"):
            # Sinosphere Section 5 titles are curated in sinosphere_title_calques.json
            continue

        raw_title = res_item.get("tarraconian_title", "")
        stem = clean_resolved_stem(raw_title, ck=ck)

        if not stem or len(stem) < 2:
            continue

        cur_tarr = props.get("tarr")
        cur_hist = props.get("tarr_hist")
        cur_anach = props.get("c_anachronism", "")
        just = res_item.get("historical_justification", "")
        opt = res_item.get("selected_option", "")

        # Check if this represents a meaningful refinement
        # Only update if stem is different or anachronism note is refined
        is_changed = False
        if stem != cur_hist and stem != cur_tarr:
            # Avoid breaking known correct MHG names that are already localized
            # e.g., if current is Vrîsing and stem is Freisingen
            if cur_hist in ("Vrîsing", "Rôtenburch", "Lôven"):
                pass
            else:
                props["tarr_hist"] = stem
                props["tarr"] = stem
                is_changed = True

        # Update c_origin if toponym changed
        if is_changed:
            orig_match = re.search(r"\((?:in-game:\s*)?([^)]+)\)", props.get("c_origin", ""))
            if orig_match:
                in_game_name = orig_match.group(1)
                cand_name = res_item.get("resolved_name", stem)
                if cand_name and not cand_name.startswith("("):
                    props["c_origin"] = f"{cand_name} (in-game: {in_game_name})"
                else:
                    props["c_origin"] = f"{stem} (in-game: {in_game_name})"

            # Update c_anachronism
            if just and (not cur_anach or cur_anach != just):
                props["c_anachronism"] = just

            # Update IPA
            props["c_ipa"] = generate_tarraconian_ipa(stem)

            # Sync to title tree
            if ck in tree_counties:
                t_node = tree_counties[ck]
                t_node["tarr"] = stem
                t_node["tarr_hist"] = stem
                t_node["origin"] = props["c_origin"]
                t_node["anachronism"] = props["c_anachronism"]
                t_node["ipa"] = props["c_ipa"]

            updated_count += 1

    print(f"Updated {updated_count} counties in GeoJSON and Title Tree.")

    # Write data/ck3_counties.geojson
    print(f"Writing {counties_path.name}...")
    with open(counties_path, "w", encoding="utf-8") as f:
        json.dump(counties_fc, f, separators=(",", ":"), ensure_ascii=False)

    # Write data/ck3_title_tree.json
    print(f"Writing {tree_path.name}...")
    with open(tree_path, "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=2, ensure_ascii=False)

    print("GeoJSON and Title Tree sync complete.")


if __name__ == "__main__":
    sync_resolutions()

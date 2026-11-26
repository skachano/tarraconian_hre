#!/usr/bin/env python3
"""
fix_ntr_p2_1_semantics.py

Fixes P2-1 (Field Semantics Drift in `relationship` & `etymology_notes`) across all
47 files in data/natural_tribal_replacements/:
1. Converts all 3,574 snake_case `relationship` enum tokens (65 distinct tokens
   across 9 empires) into clean grammatical prose sentences parameterized with the
   barony's modern_name / vanilla_ck3_name.
2. Replaces raw CK3 title keys (`c_*`, `d_*`, `k_*`, `e_*`, `b_*`) inside `2,631`
   `relationship` prose strings with readable humanized names and collapses redundant
   duplicated region labels (e.g. `canarias / canarias` -> `Canarias`,
   `c_dali/d_dali (Dali)` -> `Dali`).
3. Standardizes leading capitalization and trailing periods in `relationship`.
4. Enriches purely geographic `etymology_notes` entries where verified linguistic/
   onomastic notes already exist in `language_variants[].notes` (without fabricating
   speculative etymologies).
5. Adds `relationship` and `etymology_notes` descriptions to `metadata.schema_notes`.
"""

import argparse
import json
import re
from collections import Counter
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
NTR_DIR = REPO_DIR / "data" / "natural_tribal_replacements"


def make_snake_templates(tok: str, b_label: str) -> str:
    direct = {
        "local_river": f"Local river in the {b_label} area.",
        "flows_near": f"Watercourse flowing near {b_label}.",
        "flows_nearby": f"Watercourse flowing near {b_label}.",
        "flows_through": f"Watercourse flowing directly through {b_label}.",
        "inhabited_by": f"Historical group inhabiting the {b_label} area.",
        "regional_people": f"Regional people historically associated with {b_label}.",
        "indigenous_people_of_region": f"Indigenous people historically inhabiting the {b_label} region.",
        "adjacent_river": f"River bordering or adjoining {b_label}.",
        "overlooks": f"Elevated landform overlooking {b_label}.",
        "local_mountain_range": f"Mountain range in the {b_label} area.",
        "local_people": f"Historical people associated with {b_label}.",
        "local_hydronym": f"Local water feature in the {b_label} area.",
        "encompassing_region": f"Historical region encompassing {b_label}.",
        "located_in": f"Located in or spanning the {b_label} area.",
        "located_on": f"Situated on or along this feature near {b_label}.",
        "located_along": f"Situated along this feature in the {b_label} area.",
        "adjacent_lake": f"Lake adjacent to {b_label}.",
        "local_mountain": f"Prominent mountain in the {b_label} area.",
        "regional_name": f"Traditional regional name encompassing {b_label}.",
        "local_region": f"Historical subregion encompassing {b_label}.",
        "regional_river": f"Major regional river traversing the {b_label} area.",
        "regional_tribe": f"Regional tribal group attested in the {b_label} area.",
        "local_lake": f"Local lake in the {b_label} area.",
        "borders": f"Natural landmark bordering {b_label}.",
        "local_valley": f"Local valley in the {b_label} area.",
        "regional_plateau": f"Regional plateau encompassing or bordering {b_label}.",
        "adjacent_to": f"Natural feature adjacent to {b_label}.",
        "local_watercourse": f"Local watercourse draining the {b_label} area.",
        "prominent_local_mountain": f"Prominent mountain massif overlooking {b_label}.",
        "local_hill_range": f"Hill range in the {b_label} area.",
        "local_hill": f"Local hill in the {b_label} area.",
        "local_hills": f"Local hills in the {b_label} area.",
        "local_stream": f"Local stream in the {b_label} area.",
        "regional_lake": f"Major regional lake near {b_label}.",
        "local_wetland": f"Local wetland or marsh in the {b_label} area.",
        "local_plateau": f"Local plateau in the {b_label} area.",
        "local_coastal_feature": f"Coastal feature adjoining {b_label}.",
        "regional_mountain_range": f"Regional mountain range near {b_label}.",
        "adjacent_desert_region": f"Desert region bordering {b_label}.",
        "local_bay": f"Coastal bay adjoining {b_label}.",
        "historical_region": f"Historical region encompassing {b_label}.",
        "local_woodland": f"Local woodland or forest in the {b_label} area.",
        "encompassing_basin": f"Natural drainage basin encompassing {b_label}.",
        "regional_depression": f"Regional topographic depression around {b_label}.",
        "indigenous_tribe": f"Indigenous tribal group of the {b_label} area.",
        "ancient_civilisation_of_region": f"Ancient civilisation of the region encompassing {b_label}.",
        "regional_massif": f"Regional mountain massif near {b_label}.",
        "local_estuary": f"River estuary adjoining {b_label}.",
        "pastoral_people_of_region": f"Historical pastoralist people inhabiting the {b_label} region.",
        "prominent_local_monolith": f"Prominent rock monolith overlooking {b_label}.",
        "local_topographic_feature": f"Local landform in the {b_label} area.",
        "local_oronym": f"Local highland feature overlooking {b_label}.",
        "local_lagoon": f"Coastal lagoon adjoining {b_label}.",
        "regional_valley": f"Major regional valley traversing the {b_label} area.",
        "local_waterfall_and_river": f"Local river and waterfall feature near {b_label}.",
        "local_choronym": f"Traditional territorial name for the {b_label} area.",
        "drains_into": f"Watercourse connected to the drainage of {b_label}.",
        "local_delta_marsh": f"Deltaic marshland in the {b_label} area.",
        "regional_forest": f"Regional forest encompassing or bordering {b_label}.",
        "adjacent_oasis_region": f"Oasis region adjoining {b_label}.",
        "local_sea": f"Adjacent maritime sea bordering {b_label}.",
        "local_strait": f"Maritime strait adjoining {b_label}.",
        "coastal_region": f"Historical coastal region encompassing {b_label}.",
        "regional_ecotone": f"Regional ecological transition zone encompassing {b_label}.",
        "historical_ruling_people": f"Historical ruling people associated with the {b_label} region.",
    }
    if tok in direct:
        return direct[tok]
    words = tok.replace("_", " ").capitalize()
    return f"{words} associated with {b_label}."


def humanize_key(key: str) -> str:
    body = re.sub(r"^[bcdke]_", "", key)
    body = re.sub(r"^(FIC|Liao|EMan|Mong|THAI|MAL|PHI|IDO|SUM|SUL|Goryeo)_", "", body, flags=re.I)
    parts = [p for p in body.split("_") if p]
    return " ".join(p.upper() if p in ("TARIM", "UVS") else p.capitalize() for p in parts)


CK3_PAIR_RE = re.compile(r"\b([dk]_[A-Za-z0-9_]+)\s*/\s*(c_[A-Za-z0-9_]+)")
CK3_PAIR_REV_RE = re.compile(r"\b(c_[A-Za-z0-9_]+)\s*/\s*([dk]_[A-Za-z0-9_]+)\s*\(([^)]+)\)")
CK3_STANDALONE_PARENS_RE = re.compile(r"\s*\(\s*[bcdke]_[A-Za-z0-9_]+\s*\)")
CK3_PRECEDED_PARENS_RE = re.compile(r"\b(c_[A-Za-z0-9_]+)\s*\(([^)]+)\)")
CK3_SINGLE_KEY_RE = re.compile(r"\b[bcdke]_[A-Za-z0-9_]+\b")
DUP_SLASH_REGION_RE = re.compile(r"\bin the ([A-Za-zÀ-ÿ0-9_-]+) / \1 region\b", re.I)
DUP_PAREN_WORD_RE = re.compile(r"\b([A-Za-zÀ-ÿ0-9_-]+)\s*\(\1\)", re.I)

ETYM_EXISTING_RX = re.compile(
    r"\b(from|derives?|derived|etymology|meaning|means|root|proto-|cognate|compound|"
    r"ethnonym|toponym|hydronym|oronym|choronym|endonym|exonym|named\s+for|named\s+after|"
    r"loan|calque|corruption|adaptation|reflex|diminutive|portmanteau|associated\s+with)\b|\*",
    re.I,
)
STRICT_LV_CLUE_RX = re.compile(
    r"\b(meaning|means|lit\.|literally|from\s+|derived|cognate|compound|adaptation\s+of|"
    r"endonym|exonym|named\s+after|named\s+for|calque)\b|\*\w+",
    re.I,
)


def clean_relationship(rel: str, b_label: str, stats: Counter) -> str:
    s = rel.strip()
    if re.match(r"^[a-z0-9_]+$", s):
        stats["snake_converted"] += 1
        return make_snake_templates(s, b_label)

    orig = s
    # Replace "c_weichu/d_dali (Moyu)" -> "Moyu (Dali)"
    def _rev_sub(m):
        c_key, d_key, bar_label = m.group(1), m.group(2), m.group(3)
        d_h = humanize_key(d_key)
        c_h = humanize_key(c_key)
        if d_h.lower() == bar_label.lower() or c_h.lower() == bar_label.lower():
            return bar_label
        return f"{bar_label} ({d_h})"

    s = CK3_PAIR_REV_RE.sub(_rev_sub, s)

    # Replace "d_aleppo / c_aleppo" -> "Aleppo" or "Ardabil (Azerbaijan)"
    def _pair_sub(m):
        d_h = humanize_key(m.group(1))
        c_h = humanize_key(m.group(2))
        if d_h.lower() == c_h.lower():
            return c_h
        return f"{c_h} ({d_h})"

    s = CK3_PAIR_RE.sub(_pair_sub, s)

    # Replace "c_jahkamakke (Jåhkåmåhkke)" -> "Jåhkåmåhkke"
    s = CK3_PRECEDED_PARENS_RE.sub(lambda m: m.group(2), s)

    # Drop redundant trailing "(c_chanderi)"
    s = CK3_STANDALONE_PARENS_RE.sub("", s)

    # Replace remaining raw keys (e.g. "in the d_aral_karakum steppe" -> "in the Aral Karakum steppe")
    s = CK3_SINGLE_KEY_RE.sub(lambda m: humanize_key(m.group(0)), s)

    # Fix "in the canarias / canarias region" -> "in the Canarias region"
    s = DUP_SLASH_REGION_RE.sub(lambda m: f"in the {m.group(1).capitalize()} region", s)

    # Fix "canarias (canarias)" -> "Canarias"
    s = DUP_PAREN_WORD_RE.sub(
        lambda m: m.group(1).capitalize() if m.group(1).islower() else m.group(1), s
    )

    if s != orig:
        stats["ck3_keys_cleaned"] += 1

    # Normalize spacing & terminal period & leading sentence capitalization
    s = re.sub(r"\s{2,}", " ", s).strip()
    if s and s[0].islower():
        s = s[0].upper() + s[1:]
        stats["capitalized"] += 1
    if s and s[-1] not in ".!?":
        s += "."
        stats["period_added"] += 1

    return s


def enrich_etymology_from_variants(c: dict, stats: Counter) -> None:
    ety = c["etymology_notes"].strip()
    if not ety:
        return
    if ETYM_EXISTING_RX.search(ety):
        return

    clues = []
    seen = set()
    for lv in c["language_variants"]:
        nt = (lv.get("notes") or "").strip().rstrip(".")
        if not nt or not STRICT_LV_CLUE_RX.search(nt):
            continue
        if nt.lower() in ety.lower():
            continue
        # Format cleanly: "Afar 'Qafar' (Afar endonym)" or "Tigrinya 'X' — meaning '...'"
        sig = nt.lower()
        if sig in seen:
            continue
        seen.add(sig)
        # Avoid tautological "Afar 'Qafar': Afar endonym" -> "Afar endonym 'Qafar'" if note already starts with language name
        if nt.lower().startswith(lv["language"].lower()):
            clues.append(f"{nt} ('{lv['form']}')")
        else:
            clues.append(f"{lv['language']} '{lv['form']}' ({nt})")
        if len(clues) >= 2:
            break

    if clues:
        base = ety.rstrip(".")
        c["etymology_notes"] = f"{base}. Onomastic note: {'; '.join(clues)}."
        stats["etymology_enriched_from_variants"] += 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    files = sorted(NTR_DIR.glob("barony_natural_tribal_replacements_*.json"))
    stats = Counter()
    remaining_snake = []
    remaining_ck3_keys = []

    rel_doc = (
        "Prose description of the geographical, ecological, or historical relationship between "
        "the replacement entity and the audited barony."
    )
    etym_doc = (
        "Linguistic etymology, onomastic origin, or geographic/ethnographic characterization of the "
        "replacement entity (incorporating attested onomastic notes from language variants where documented)."
    )

    for p in files:
        emp = p.stem.replace("barony_natural_tribal_replacements_", "")
        d = json.loads(p.read_text(encoding="utf-8"))
        sn = d["metadata"]["schema_notes"]
        sn["relationship"] = rel_doc
        sn["etymology_notes"] = etym_doc

        for bk, b in d["baronies"].items():
            b_label = b.get("modern_name") or b["vanilla_ck3_name"]
            for c in b["replacement_candidates"]:
                new_rel = clean_relationship(c["relationship"], b_label, stats)
                if new_rel != c["relationship"]:
                    c["relationship"] = new_rel
                if re.match(r"^[a-z0-9_]+$", c["relationship"]):
                    remaining_snake.append((emp, bk, c["relationship"]))
                if CK3_SINGLE_KEY_RE.search(c["relationship"]):
                    remaining_ck3_keys.append((emp, bk, c["relationship"]))

                enrich_etymology_from_variants(c, stats)

        if args.apply:
            new_text = json.dumps(d, ensure_ascii=False, indent=2) + "\n"
            if new_text != p.read_text(encoding="utf-8"):
                p.write_text(new_text, encoding="utf-8")
                stats["files_written"] += 1

    print("=== P2-1 SEMANTICS CLEANUP SUMMARY ===")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v}")
    print(f"remaining_snake={len(remaining_snake)} {remaining_snake[:5]}")
    print(f"remaining_ck3_keys={len(remaining_ck3_keys)} {remaining_ck3_keys[:5]}")


if __name__ == "__main__":
    main()

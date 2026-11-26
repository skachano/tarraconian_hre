#!/usr/bin/env python3
"""
fix_ntr_p0_3_historicity.py

Fixes P0-3 across all 47 files in data/natural_tribal_replacements/:
1. Replaces all colonial/modern/post-867-eponym natural features (60 unique) and
   all post-1178 tribes (72 unique) with historically attested pre-867 or
   pre-literate indigenous equivalents (collision-checked within each barony).
2. Adds `attestation_basis` and `valid_for_bookmarks` ({867, 1066, 1178}) to all
   24,462 replacement candidates, cleanly separating:
   - attested_pre_867 (valid 867/1066/1178)
   - indigenous_pre_literate (valid 867/1066/1178)
   - attested_867_to_1066 (valid 1066/1178)
   - attested_1066_to_1178 (valid 1178)
3. Recomputes metadata.summary_statistics and updates metadata.schema_notes.
"""

import argparse
import copy
import json
import sys
import unicodedata
from collections import Counter
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
NTR_DIR = REPO_DIR / "data" / "natural_tribal_replacements"

sys.path.insert(0, str(REPO_DIR / "scripts"))
from ntr_p03_replacements import NAT_REPLACEMENTS, POST1178_TRIBE_MAP, TRIBE_POOL

TRUE_POST867_TO_1066 = {
    "Volga Bulgars", "Pechenegs", "Khamag Mongol", "Jurchens", "Jurchen people",
    "Keraites", "Tajiks", "Chigils", "Tuhsi", "Banu Kanz", "Al-Muntafiq",
    "Hadhabani", "Aromanians", "Vlachs", "Dalmatian Italians", "Hakka people",
    "Yugurs", "Kachhwahas", "Chudasamas", "Gakhars", "Soomra", "Mandinka people",
    "Balochs", "Baloch", "Fula people", "Tuareg", "Songhai people", "Toucouleur people",
}
TRUE_POST1066_TO_1178 = {
    "Naimans", "Merkit", "Merkits", "Kangly", "Székelys", "Icelanders",
    "Cumans", "Gahadavalas", "Hawiye", "Albanians", "Izhorians", "Bolokhovians",
    "Bosniaks",
}

ALLOWED_PUNCT = set(" \t\n\r-*.,/()'’\"–—&0123456789ʼʻʾʿˈˌ·ʹʷ\u200c\u200d")


def is_latin_char(ch: str) -> bool:
    if ch in ALLOWED_PUNCT:
        return True
    name = unicodedata.name(ch, "")
    return "LATIN" in name or "COMBINING" in name or unicodedata.category(ch).startswith("M")


def classify_candidate(c: dict) -> tuple[str, dict]:
    nm = c["name"]
    cat = c["category"]
    ay = c["earliest_attestation_year"]
    if cat == "tribe":
        if nm in TRUE_POST867_TO_1066:
            return "attested_867_to_1066", {"867": False, "1066": True, "1178": True}
        if nm in TRUE_POST1066_TO_1178:
            return "attested_1066_to_1178", {"867": False, "1066": False, "1178": True}
    if ay is not None and ay <= 867:
        return "attested_pre_867", {"867": True, "1066": True, "1178": True}
    return "indigenous_pre_literate", {"867": True, "1066": True, "1178": True}


def pick_non_colliding(pool_list: list[dict], forbidden_names: set[str], forbidden_urls: set[str]) -> dict | None:
    for cand in pool_list:
        if cand["name"].lower() not in forbidden_names and cand["source_url"] not in forbidden_urls:
            return copy.deepcopy(cand)
    # Fallback: allow url reuse if needed before failing
    for cand in pool_list:
        if cand["name"].lower() not in forbidden_names:
            return copy.deepcopy(cand)
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    files = sorted(NTR_DIR.glob("barony_natural_tribal_replacements_*.json"))

    stats = Counter()
    basis_counts = Counter()
    bookmark_counts = Counter()
    baronies_with_867 = 0
    baronies_with_867_tribe = 0
    total_baronies = 0
    unreplaced_misses = []
    bad_latin_forms = []

    for p in files:
        d = json.load(open(p, encoding="utf-8"))
        tax = d["metadata"]["schema_notes"]["category_subtype_taxonomy"]

        for bk, b in d["baronies"].items():
            total_baronies += 1
            enpn = b.get("existing_natural_proper_name") or {}
            self_names = {
                (b.get("vanilla_ck3_name") or "").lower(),
                (b.get("modern_name") or "").lower(),
            }
            if enpn.get("is_natural_name") and enpn.get("name"):
                self_names.add(enpn["name"].lower())

            cands = b["replacement_candidates"]
            # First identify which indices need replacement
            new_cands = list(cands)
            for idx, c in enumerate(cands):
                nm = c["name"]
                other_names = {x["name"].lower() for j, x in enumerate(new_cands) if j != idx}
                other_urls = {x["source_url"] for j, x in enumerate(new_cands) if j != idx}
                forbidden_names = self_names | other_names

                if nm in NAT_REPLACEMENTS:
                    rep = pick_non_colliding(NAT_REPLACEMENTS[nm], forbidden_names, other_urls)
                    if rep is None:
                        unreplaced_misses.append((p.name, bk, nm))
                    else:
                        new_cands[idx] = rep
                        stats["nat_replaced"] += 1
                elif nm in POST1178_TRIBE_MAP:
                    pool = [TRIBE_POOL[k] for k in POST1178_TRIBE_MAP[nm]]
                    # Extended regional fallback if all 3 already used
                    ext_pool = pool + [v for v in TRIBE_POOL.values() if v not in pool]
                    rep = pick_non_colliding(ext_pool, forbidden_names, other_urls)
                    if rep is None:
                        unreplaced_misses.append((p.name, bk, nm))
                    else:
                        new_cands[idx] = rep
                        stats["tribe_replaced"] += 1

            # Classify all 3 candidates (P0-3 schema fields)
            has_867 = False
            has_867_tribe = False
            for c in new_cands:
                # Fix any accidental Cyrillic yer in form if present
                for lv in c["language_variants"]:
                    if "ъ" in lv["form"] or "ь" in lv["form"]:
                        lv["native_script"] = lv["form"]
                        lv["form"] = lv["form"].replace("ъ", "ŭ").replace("ь", "ĭ")
                    if any(not is_latin_char(ch) for ch in lv["form"]):
                        bad_latin_forms.append((p.name, bk, c["name"], lv["form"]))

                basis, valid_bm = classify_candidate(c)
                c["attestation_basis"] = basis
                c["valid_for_bookmarks"] = valid_bm
                basis_counts[basis] += 1
                for bm, ok in valid_bm.items():
                    if ok:
                        bookmark_counts[bm] += 1
                if valid_bm["867"]:
                    has_867 = True
                    if c["category"] == "tribe":
                        has_867_tribe = True

                # Ensure subtype is registered in taxonomy
                cat = c["category"]
                sub = c["feature_subtype"]
                if sub not in tax.get(cat, []):
                    tax.setdefault(cat, []).append(sub)
                    tax[cat].sort()

            if has_867:
                baronies_with_867 += 1
            if has_867_tribe:
                baronies_with_867_tribe += 1
            b["replacement_candidates"] = new_cands

        # Update metadata.schema_notes
        sn = d["metadata"]["schema_notes"]
        sn["attestation_basis"] = (
            "Historicity classification distinguishing genuinely pre-867/pre-literate entities from "
            "medieval post-867 ethnogeneses: attested_pre_867 | indigenous_pre_literate | "
            "attested_867_to_1066 | attested_1066_to_1178."
        )
        sn["valid_for_bookmarks"] = (
            "Bookmark-keyed booleans {'867', '1066', '1178'} indicating whether the replacement candidate "
            "is historically non-anachronistic for that bookmark (true for both attested_pre_867 and "
            "indigenous_pre_literate; bookmark-gated for attested_867_to_1066 and attested_1066_to_1178)."
        )

        # Recompute metadata.summary_statistics
        ss = d["metadata"]["summary_statistics"]
        cand_by_cat = Counter()
        bar_with_cat = Counter()
        uniq_names = set()
        uniq_urls = set()
        wiki_cnt = 0
        multiling = 0
        lang_codes = set()
        emp_basis = Counter()
        emp_bm = Counter()
        emp_bar_867 = 0

        for b in d["baronies"].values():
            cats = set()
            b867 = False
            for c in b["replacement_candidates"]:
                cand_by_cat[c["category"]] += 1
                cats.add(c["category"])
                uniq_names.add(c["name"])
                if c["source_url"]:
                    uniq_urls.add(c["source_url"])
                    if "wikipedia.org" in c["source_url"]:
                        wiki_cnt += 1
                codes = {lv["language_code"] for lv in c["language_variants"]}
                lang_codes.update(codes)
                if len(codes) > 1:
                    multiling += 1
                emp_basis[c["attestation_basis"]] += 1
                for bm, ok in c["valid_for_bookmarks"].items():
                    if ok:
                        emp_bm[bm] += 1
                if c["valid_for_bookmarks"]["867"]:
                    b867 = True
            for cat in cats:
                bar_with_cat[f"has_{cat}_candidate"] += 1
            if b867:
                emp_bar_867 += 1

        ss["unique_replacement_names"] = len(uniq_names)
        ss["candidates_with_multilingual_variants"] = multiling
        ss["wikipedia_source_attached"] = wiki_cnt
        ss["unique_source_urls"] = len(uniq_urls)
        for cat in ss["candidates_by_category"]:
            ss["candidates_by_category"][cat] = cand_by_cat.get(cat, 0)
        for k in ss["baronies_with_category"]:
            ss["baronies_with_category"][k] = bar_with_cat.get(k, 0)
        ss["unique_language_codes"] = sorted(lang_codes)
        ss["candidates_by_attestation_basis"] = dict(sorted(emp_basis.items()))
        ss["bookmark_valid_candidates"] = {bm: emp_bm.get(bm, 0) for bm in ("867", "1066", "1178")}
        ss["baronies_with_867_valid_candidate"] = emp_bar_867

        if args.apply:
            with open(p, "w", encoding="utf-8") as fh:
                json.dump(d, fh, ensure_ascii=False, indent=2)
                fh.write("\n")
            stats["files_written"] += 1

    print("=== P0-3 HISTORICITY SUMMARY ===")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v}")
    print(f"Total baronies: {total_baronies}")
    print(f"Baronies with >=1 valid 867 candidate: {baronies_with_867}/{total_baronies}")
    print(f"Baronies with >=1 valid 867 tribe: {baronies_with_867_tribe}/{total_baronies}")
    print(f"Attestation basis counts: {dict(basis_counts)}")
    print(f"Bookmark valid candidate counts: {dict(bookmark_counts)}")
    print(f"Unreplaced misses: {len(unreplaced_misses)} {unreplaced_misses[:10]}")
    print(f"Bad non-Latin forms introduced: {len(bad_latin_forms)} {bad_latin_forms[:10]}")


if __name__ == "__main__":
    main()

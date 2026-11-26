#!/usr/bin/env python3
"""
fix_ntr_p1_1_reconcile_entities.py

Fixes P1-1 (Cross-File Entity Reconciliation) across all 47 files in
data/natural_tribal_replacements/:
1. Splits 7 shared URLs where distinct real-world homonyms accidentally pointed to
   the same Wikipedia URL (Kinda Sweden vs Arabia, Sió Catalonia vs Hungary,
   Bago River Philippines vs Myanmar, Chu River Vietnam vs Central Asia,
   Ikva Hungary vs Ukraine, Manasi River Xinjiang vs Bhutan Manas,
   Baba Mountain North Macedonia vs Bosnia/Herzegovina).
2. Canonicalizes 21 Wikipedia redirect / duplicate URLs (e.g. Syrian_desert ->
   Syrian_Desert, Aras_River -> Aras_(river), Shiwei_people -> Shiwei,
   Maithil_people -> Maithils, Bug_River -> Bug_(river), etc.).
3. Reconciles category, feature_subtype, name, disambiguation_note,
   localisation_stem, earliest_attestation_year, earliest_attestation_note,
   attestation_basis, and valid_for_bookmarks per canonical source_url.
4. Prevents intra-barony stem collisions globally by propagating full-name stems
   for any source_url involved in a same-barony stem collision.
5. Registers any newly introduced feature_subtypes in each file's
   metadata.schema_notes.category_subtype_taxonomy and recomputes
   metadata.summary_statistics.
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
NTR_DIR = REPO_DIR / "data" / "natural_tribal_replacements"

sys.path.insert(0, str(REPO_DIR / "scripts"))
from fix_ntr_p0_3_historicity import classify_candidate, is_latin_char
from fix_ntr_p0_4_name_hygiene import compute_stem


# Contextual splits: (empire_key, old_url) -> (new_url, forced_name, forced_disambig)
CONTEXTUAL_URL_SPLITS = {
    ("e_scandinavia", "https://en.wikipedia.org/wiki/Kinda"): (
        "https://sv.wikipedia.org/wiki/Kinda_h%C3%A4rad",
        "Kinda",
        "Sweden",
    ),
    ("e_france", "https://en.wikipedia.org/wiki/Si%C3%B3"): (
        "https://ca.wikipedia.org/wiki/Riu_Si%C3%B3",
        "Sió",
        "Catalonia",
    ),
    ("e_nusantara", "https://en.wikipedia.org/wiki/Bago_River"): (
        "https://en.wikipedia.org/wiki/Bago,_Negros_Occidental",
        "Bago River",
        "Philippines",
    ),
    ("e_lingnan", "https://en.wikipedia.org/wiki/Chu_(river)"): (
        "https://en.wikipedia.org/wiki/Nam_Sam_River",
        "Chu",
        "Vietnam",
    ),
    ("e_germany", "https://en.wikipedia.org/wiki/Ikva"): (
        "https://hu.wikipedia.org/wiki/Ikva",
        "Ikva",
        "Hungary",
    ),
    ("e_tartaria", "https://en.wikipedia.org/wiki/Manas_River"): (
        "https://en.wikipedia.org/wiki/Manasi_River",
        "Manas River",
        "Xinjiang",
    ),
    ("e_byzantium", "https://en.wikipedia.org/wiki/Baba_Mountain"): (
        "https://en.wikipedia.org/wiki/Baba_(North_Macedonia)",
        "Baba Mountain",
        "North Macedonia",
    ),
    ("e_illyria", "https://en.wikipedia.org/wiki/Baba_Mountain"): (
        "https://bs.wikipedia.org/wiki/Baba_(planina)",
        "Baba Mountain",
        "Herzegovina",
    ),
}

# Duplicate / redirect Wikipedia URLs representing the exact same entity
URL_REDIRECT_MAP = {
    "https://en.wikipedia.org/wiki/Abhira": "https://en.wikipedia.org/wiki/Abhira_people",
    "https://en.wikipedia.org/wiki/Aras_River": "https://en.wikipedia.org/wiki/Aras_(river)",
    "https://en.wikipedia.org/wiki/Bayanaul": "https://en.wikipedia.org/wiki/Bayanaul_Range",
    "https://en.wikipedia.org/wiki/Brda_(river)": "https://en.wikipedia.org/wiki/Brda",
    "https://en.wikipedia.org/wiki/Bug_River": "https://en.wikipedia.org/wiki/Bug_(river)",
    "https://en.wikipedia.org/wiki/Cenomani_(Cisalpine_Gaul)": "https://en.wikipedia.org/wiki/Cenomani",
    "https://en.wikipedia.org/wiki/Eider_(river)": "https://en.wikipedia.org/wiki/Eider",
    "https://en.wikipedia.org/wiki/Ghaghara_River": "https://en.wikipedia.org/wiki/Ghaghara",
    "https://en.wikipedia.org/wiki/Irgiz": "https://en.wikipedia.org/wiki/Irgiz_(Turgay)",
    "https://en.wikipedia.org/wiki/Kan_(river)": "https://en.wikipedia.org/wiki/Kan_River",
    "https://en.wikipedia.org/wiki/Khabur_River": "https://en.wikipedia.org/wiki/Khabur",
    "https://en.wikipedia.org/wiki/Khas_people": "https://en.wikipedia.org/wiki/Khasas",
    "https://en.wikipedia.org/wiki/Kokshetau_Hills": "https://en.wikipedia.org/wiki/Kokshetau_Mountains",
    "https://en.wikipedia.org/wiki/Kura_River": "https://en.wikipedia.org/wiki/Kura_(river)",
    "https://en.wikipedia.org/wiki/Lu%C5%BEnice_(river)": "https://en.wikipedia.org/wiki/Lu%C5%BEnice",
    "https://en.wikipedia.org/wiki/Maithil_people": "https://en.wikipedia.org/wiki/Maithils",
    "https://en.wikipedia.org/wiki/Naxi": "https://en.wikipedia.org/wiki/Naxi_people",
    "https://en.wikipedia.org/wiki/Shiwei_people": "https://en.wikipedia.org/wiki/Shiwei",
    "https://en.wikipedia.org/wiki/Syrian_desert": "https://en.wikipedia.org/wiki/Syrian_Desert",
    "https://en.wikipedia.org/wiki/Timi%C8%99_(river)": "https://en.wikipedia.org/wiki/Timi%C8%99",
    "https://en.wikipedia.org/wiki/Veps_people": "https://en.wikipedia.org/wiki/Vepsians",
    "https://en.wikipedia.org/wiki/Yao": "https://en.wikipedia.org/wiki/Yao_people_(Asia)",
}

# Explicit canonical (category, feature_subtype) per canonical URL
CANONICAL_CAT_SUB = {
    # 16 category conflicts (Kinda already split above)
    "https://en.wikipedia.org/wiki/%C5%BDitn%C3%BD_ostrov": ("choronym", "region"),
    "https://en.wikipedia.org/wiki/Aoukar": ("choronym", "region"),
    "https://en.wikipedia.org/wiki/Ardennes": ("topographic_feature", "forest"),
    "https://en.wikipedia.org/wiki/Caspian_Depression": ("choronym", "region"),
    "https://en.wikipedia.org/wiki/Chedi_kingdom": ("tribe", "indo_aryan_people"),
    "https://en.wikipedia.org/wiki/Hexi_Corridor": ("choronym", "region"),
    "https://en.wikipedia.org/wiki/Kamarupa": ("tribe", "indo_aryan_people"),
    "https://en.wikipedia.org/wiki/Kaouar": ("oronym", "plateau"),
    "https://en.wikipedia.org/wiki/Kuma%E2%80%93Manych_Depression": ("topographic_feature", "valley"),
    "https://en.wikipedia.org/wiki/Mu_Us_Desert": ("choronym", "region"),
    "https://en.wikipedia.org/wiki/Ordos_Desert": ("choronym", "region"),
    "https://en.wikipedia.org/wiki/Turpan_Depression": ("topographic_feature", "valley"),
    "https://en.wikipedia.org/wiki/Upper_Palatine_Forest": ("oronym", "mountain_range"),
    "https://en.wikipedia.org/wiki/Wadi_Allaqi": ("topographic_feature", "valley"),
    "https://en.wikipedia.org/wiki/West_Siberian_Plain": ("choronym", "region"),
    "https://en.wikipedia.org/wiki/Zanj": ("tribe", "bantu_tribe"),
    # Non-medieval_people subtype resolutions
    "https://en.wikipedia.org/wiki/Bobo_people": ("tribe", "mande_people"),
    "https://en.wikipedia.org/wiki/Boii": ("tribe", "celtic_tribe"),
    "https://en.wikipedia.org/wiki/Brigantes": ("tribe", "brittonic_tribe"),
    "https://en.wikipedia.org/wiki/Getae": ("tribe", "dacian_tribe"),
    "https://en.wikipedia.org/wiki/Ghassanids": ("tribe", "arab_tribe"),
    "https://en.wikipedia.org/wiki/Gulf_of_Oman": ("hydronym", "sea"),
    "https://en.wikipedia.org/wiki/Gulf_of_Thailand": ("hydronym", "bay"),
    "https://en.wikipedia.org/wiki/Histri": ("tribe", "illyrian_tribe"),
    "https://en.wikipedia.org/wiki/Kuranko_people": ("tribe", "mande_people"),
    "https://en.wikipedia.org/wiki/Lingones": ("tribe", "gaulish_tribe"),
    "https://en.wikipedia.org/wiki/Mandinka_people": ("tribe", "mande_people"),
    "https://en.wikipedia.org/wiki/Mishmi_Hills": ("oronym", "mountain_range"),
    "https://en.wikipedia.org/wiki/Mugalzhar": ("oronym", "mountain_range"),
    "https://en.wikipedia.org/wiki/Nabataeans": ("tribe", "semitic_tribe"),
    "https://en.wikipedia.org/wiki/Nuba_peoples": ("tribe", "nilo_saharan_people"),
    "https://en.wikipedia.org/wiki/Ochil_Hills": ("oronym", "mountain_range"),
    "https://en.wikipedia.org/wiki/Pentland_Hills": ("oronym", "mountain_range"),
    "https://en.wikipedia.org/wiki/Saka": ("tribe", "iranian_tribe"),
    "https://en.wikipedia.org/wiki/Susu_people": ("tribe", "mande_people"),
    "https://en.wikipedia.org/wiki/U%C4%8Dka": ("oronym", "mountain_range"),
    "https://en.wikipedia.org/wiki/Volga_Delta": ("topographic_feature", "coastal_feature"),
}

# Explicit canonical (name, disambiguation_note) per canonical URL
CANONICAL_NAME_DISAMBIG = {
    # Split entities
    "https://sv.wikipedia.org/wiki/Kinda_h%C3%A4rad": ("Kinda", "Sweden"),
    "https://ca.wikipedia.org/wiki/Riu_Si%C3%B3": ("Sió", "Catalonia"),
    "https://en.wikipedia.org/wiki/Bago,_Negros_Occidental": ("Bago River", "Philippines"),
    "https://en.wikipedia.org/wiki/Nam_Sam_River": ("Chu", "Vietnam"),
    "https://hu.wikipedia.org/wiki/Ikva": ("Ikva", "Hungary"),
    "https://en.wikipedia.org/wiki/Manasi_River": ("Manas River", "Xinjiang"),
    "https://en.wikipedia.org/wiki/Baba_(North_Macedonia)": ("Baba Mountain", "North Macedonia"),
    "https://bs.wikipedia.org/wiki/Baba_(planina)": ("Baba Mountain", "Herzegovina"),
    # Merged / conflicting canonical names & disambiguation notes
    "https://en.wikipedia.org/wiki/Abhira_people": ("Abhiras", None),
    "https://en.wikipedia.org/wiki/Bayanaul_Range": ("Bayanaul Range", None),
    "https://en.wikipedia.org/wiki/Bug_(river)": ("Western Bug", None),
    "https://en.wikipedia.org/wiki/Cataracts_of_the_Nile": ("Cataracts of the Nile", None),
    "https://en.wikipedia.org/wiki/Chedi_kingdom": ("Chedis", None),
    "https://en.wikipedia.org/wiki/Chu_(river)": ("Chu River", None),
    "https://en.wikipedia.org/wiki/Daugava": ("Daugava", None),
    "https://en.wikipedia.org/wiki/Itbay": ("Red Sea Hills", None),
    "https://en.wikipedia.org/wiki/Kamarupa": ("Kamarupas", None),
    "https://en.wikipedia.org/wiki/Khitan_people": ("Khitan", None),
    "https://en.wikipedia.org/wiki/Kimak%E2%80%93Kipchak_confederation": ("Kimaks", None),
    "https://en.wikipedia.org/wiki/Kokshetau_Mountains": ("Kokshetau Mountains", None),
    "https://en.wikipedia.org/wiki/Krobyzoi": ("Crobyzi", None),
    "https://en.wikipedia.org/wiki/Kuma%E2%80%93Manych_Depression": ("Kuma-Manych Depression", None),
    "https://en.wikipedia.org/wiki/Kupa": ("Kupa", None),
    "https://en.wikipedia.org/wiki/Neris": ("Neris", None),
    "https://en.wikipedia.org/wiki/Oslofjord": ("Oslofjord", None),
    "https://en.wikipedia.org/wiki/Slavs_in_Lower_Pannonia": ("Pannonian Slavs", None),
    "https://en.wikipedia.org/wiki/Tannu-Ola_mountains": ("Tannu-Ola Mountains", None),
    "https://en.wikipedia.org/wiki/Uy_(Tobol)": ("Uy", "Tobol"),
    "https://en.wikipedia.org/wiki/Vepsians": ("Vepsians", None),
    "https://en.wikipedia.org/wiki/Yao_people_(Asia)": ("Yao", None),
}


def resolve_cat_sub(url: str, recs: list[dict]) -> tuple[str, str]:
    if url in CANONICAL_CAT_SUB:
        return CANONICAL_CAT_SUB[url]
    pairs = Counter((c["category"], c["feature_subtype"]) for c in recs)
    if len(pairs) == 1:
        return next(iter(pairs))
    # Prefer non-'medieval_people' specific ethnolinguistic subtype if any
    non_generic = {k: v for k, v in pairs.items() if k[1] != "medieval_people"}
    pool = non_generic if non_generic else pairs
    return sorted(pool.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]


def resolve_name_disambig(url: str, recs: list[dict], disambig_locked_names: set[str]) -> tuple[str, str | None]:
    if url in CANONICAL_NAME_DISAMBIG:
        return CANONICAL_NAME_DISAMBIG[url]
    pairs = Counter((c["name"], c["disambiguation_note"]) for c in recs)
    if len(pairs) == 1:
        return next(iter(pairs))
    # Check if URL has an existing non-None disambiguation_note vs None
    # If another distinct URL already uses the bare name (in same disambig cluster), preserve disambig;
    # otherwise prefer disambig=None if any entry has disambig=None, picking most frequent clean name.
    none_pairs = {k: v for k, v in pairs.items() if k[1] is None}
    pool = none_pairs if (none_pairs and not any(n in disambig_locked_names for n, _ in none_pairs)) else pairs
    return sorted(pool.items(), key=lambda kv: (-kv[1], len(kv[0][0]), kv[0][0], kv[0][1] or ""))[0][0]


def resolve_year_note(recs: list[dict]) -> tuple[int | None, str]:
    yrs = [c["earliest_attestation_year"] for c in recs if c["earliest_attestation_year"] is not None]
    if not yrs:
        notes = Counter(c["earliest_attestation_note"] for c in recs)
        best_note = sorted(notes.items(), key=lambda kv: (-kv[1], -len(kv[0]), kv[0]))[0][0]
        return None, best_note
    min_yr = min(yrs)
    matching_notes = Counter(
        c["earliest_attestation_note"]
        for c in recs
        if c["earliest_attestation_year"] == min_yr
    )
    best_note = sorted(matching_notes.items(), key=lambda kv: (-kv[1], -len(kv[0]), kv[0]))[0][0]
    return min_yr, best_note


def recompute_summary_statistics(d: dict) -> None:
    ss = d["metadata"]["summary_statistics"]
    cand_by_cat = Counter()
    bar_with_cat = Counter()
    uniq_names = set()
    uniq_stems = set()
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
            uniq_stems.add(c["localisation_stem"])
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
    ss["unique_localisation_stems"] = len(uniq_stems)
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    files = sorted(NTR_DIR.glob("barony_natural_tribal_replacements_*.json"))
    datasets = {}
    for p in files:
        emp = p.stem.replace("barony_natural_tribal_replacements_", "")
        with open(p, encoding="utf-8") as fh:
            datasets[emp] = (p, json.load(fh))

    stats = Counter()

    # Step 1: Canonicalize source_url across all candidates
    by_url: dict[str, list[dict]] = defaultdict(list)
    names_to_urls: dict[str, set[str]] = defaultdict(set)
    for emp, (_, d) in datasets.items():
        for bk, b in d["baronies"].items():
            for c in b["replacement_candidates"]:
                old_url = c["source_url"]
                if (emp, old_url) in CONTEXTUAL_URL_SPLITS:
                    new_url, forced_nm, forced_dis = CONTEXTUAL_URL_SPLITS[(emp, old_url)]
                    c["source_url"] = new_url
                    c["name"] = forced_nm
                    c["disambiguation_note"] = forced_dis
                    stats["contextual_url_split"] += 1
                elif old_url in URL_REDIRECT_MAP:
                    c["source_url"] = URL_REDIRECT_MAP[old_url]
                    stats["redirect_url_merged"] += 1
                by_url[c["source_url"]].append(c)
                names_to_urls[c["name"]].add(c["source_url"])

    # Clean names mapped to >1 distinct URL that actually represent homonyms (only keep disambig where needed)
    disambig_locked_names = {nm for nm, us in names_to_urls.items() if len(us) > 1}

    # Step 2: Build canonical entity table per source_url
    canon_table = {}
    for url, recs in by_url.items():
        cat, sub = resolve_cat_sub(url, recs)
        nm, disambig = resolve_name_disambig(url, recs, disambig_locked_names)
        yr, yr_note = resolve_year_note(recs)
        probe = {"name": nm, "category": cat, "earliest_attestation_year": yr}
        basis, valid_bm = classify_candidate(probe)
        base_stem = compute_stem(nm, cat)
        canon_table[url] = {
            "name": nm,
            "disambiguation_note": disambig,
            "category": cat,
            "feature_subtype": sub,
            "earliest_attestation_year": yr,
            "earliest_attestation_note": yr_note,
            "attestation_basis": basis,
            "valid_for_bookmarks": valid_bm,
            "base_stem": base_stem,
        }

    # Step 3: Detect any intra-barony stem collisions using base_stem, and determine
    # which URLs must globally keep full clean_name as localisation_stem so BOTH
    # intra-barony uniqueness AND cross-file URL consistency hold simultaneously.
    force_full_stem_urls = set()
    for emp, (_, d) in datasets.items():
        for bk, b in d["baronies"].items():
            cands = b["replacement_candidates"]
            stems = [canon_table[c["source_url"]]["base_stem"] for c in cands]
            if len(set(stems)) < len(stems):
                # Resolve priority inside barony: unshortened first, then tribe, then hydronym, then idx
                prio = sorted(
                    range(len(cands)),
                    key=lambda idx: (
                        0 if canon_table[cands[idx]["source_url"]]["base_stem"] == canon_table[cands[idx]["source_url"]]["name"] else 1,
                        0 if canon_table[cands[idx]["source_url"]]["category"] == "tribe" else (
                            1 if canon_table[cands[idx]["source_url"]]["category"] == "hydronym" else 2
                        ),
                        idx,
                    ),
                )
                used = set()
                for idx in prio:
                    u = cands[idx]["source_url"]
                    bs = canon_table[u]["base_stem"]
                    if bs not in used:
                        used.add(bs)
                    else:
                        force_full_stem_urls.add(u)
                        used.add(canon_table[u]["name"])

    for url, info in canon_table.items():
        info["localisation_stem"] = info["name"] if url in force_full_stem_urls else info["base_stem"]

    # Step 4: Apply canonical attributes to all candidates & verify invariants
    dup_barony_name = []
    dup_barony_stem = []
    dup_barony_url = []
    no_867_baronies = []
    bad_latin_forms = []

    for emp, (p, d) in datasets.items():
        tax = d["metadata"]["schema_notes"]["category_subtype_taxonomy"]
        for bk, b in d["baronies"].items():
            seen_names = set()
            seen_stems = set()
            seen_urls = set()
            has_867 = False

            for c in b["replacement_candidates"]:
                u = c["source_url"]
                canon = canon_table[u]

                for fld in (
                    "name",
                    "disambiguation_note",
                    "localisation_stem",
                    "category",
                    "feature_subtype",
                    "earliest_attestation_year",
                    "earliest_attestation_note",
                    "attestation_basis",
                    "valid_for_bookmarks",
                ):
                    if c.get(fld) != canon[fld]:
                        c[fld] = canon[fld]
                        stats[f"updated_{fld}"] += 1

                # Ensure taxonomy registers this subtype in this file
                if c["feature_subtype"] not in tax.get(c["category"], []):
                    tax.setdefault(c["category"], []).append(c["feature_subtype"])
                    tax[c["category"]].sort()
                    stats["taxonomy_subtypes_added"] += 1

                if c["name"] in seen_names:
                    dup_barony_name.append((emp, bk, c["name"]))
                seen_names.add(c["name"])

                if c["localisation_stem"] in seen_stems:
                    dup_barony_stem.append((emp, bk, c["localisation_stem"]))
                seen_stems.add(c["localisation_stem"])

                if u in seen_urls:
                    dup_barony_url.append((emp, bk, u))
                seen_urls.add(u)

                if c["valid_for_bookmarks"]["867"]:
                    has_867 = True

                for lv in c["language_variants"]:
                    if any(not is_latin_char(ch) for ch in lv["form"]):
                        bad_latin_forms.append((emp, bk, c["name"], lv["form"]))

            if not has_867:
                no_867_baronies.append((emp, bk))

        recompute_summary_statistics(d)

        if args.apply:
            new_text = json.dumps(d, ensure_ascii=False, indent=2) + "\n"
            old_text = p.read_text(encoding="utf-8")
            if new_text != old_text:
                p.write_text(new_text, encoding="utf-8")
                stats["files_written"] += 1

    print("=== P1-1 ENTITY RECONCILIATION SUMMARY ===")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v}")
    print(f"Canonical unique source_urls: {len(canon_table)}")
    print(f"URLs kept at full name as stem globally to prevent collision: {len(force_full_stem_urls)}")
    print(f"dup_barony_name={len(dup_barony_name)} {dup_barony_name[:5]}")
    print(f"dup_barony_stem={len(dup_barony_stem)} {dup_barony_stem[:5]}")
    print(f"dup_barony_url={len(dup_barony_url)} {dup_barony_url[:5]}")
    print(f"no_867_baronies={len(no_867_baronies)} {no_867_baronies[:5]}")
    print(f"bad_latin_forms={len(bad_latin_forms)} {bad_latin_forms[:5]}")


if __name__ == "__main__":
    main()

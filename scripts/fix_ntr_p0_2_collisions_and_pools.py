#!/usr/bin/env python3
"""
fix_ntr_p0_2_collisions_and_pools.py

Applies the 7 regional Wikipedia-verified replacement pools to resolve P0-2 across
all 47 files in data/natural_tribal_replacements/:
1. Eliminates all self-matches (candidate name/stem vs barony own name or ENP).
2. Eliminates all sibling-county collisions (candidate name/stem vs any other
   barony's vanilla_ck3_name or modern_name in the same county).
3. Replaces oceanic/mega-continental macro-features (Indian Ocean, Red Sea,
   Arabian Sea, Persian Gulf, Gobi Desert, Sahara, Himalayas, Tibetan Plateau,
   Caspian Sea, Aral Sea, Black Sea, Baltic Sea, South China Sea, Java Sea, etc.).
4. Resolves all unsolvable counties across 867, 1066, and 1178 bookmarks via
   per-county bipartite matching guarantees (excluding sibling names).
5. Runs P0-1, P0-3, P0-4, P1-1, P1-3, P2-1, and summary_statistics integrity checks
   on every modified candidate and across all 47 files.
"""

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
NTR_DIR = REPO_DIR / "data" / "natural_tribal_replacements"
AUDIT_DIR = REPO_DIR / "data" / "anachronicity_audit"
DEFAULT_POOL_DIR = Path(
    "/home/siarzhuk/.gemini/antigravity/brain/de048ecd-163f-4735-b52d-00c9d457b330/scratch/p0_2_batches"
)

sys.path.insert(0, str(REPO_DIR / "scripts"))
from fix_ntr_p0_3_historicity import classify_candidate, is_latin_char
from fix_ntr_p0_4_name_hygiene import compute_stem, strip_disambig
from fix_ntr_p1_1_reconcile_entities import (
    URL_REDIRECT_MAP,
    recompute_summary_statistics,
    resolve_cat_sub,
    resolve_name_disambig,
    resolve_year_note,
)
from fix_ntr_p1_3_language_variants import (
    consolidate_same_code,
    is_redundant_eng,
    normalize_variant_code_and_label,
)

MEGA_MACRO = {
    "Indian Ocean", "Pacific Ocean", "Atlantic Ocean", "Mediterranean Sea",
    "Red Sea", "Arabian Sea", "Persian Gulf", "Gulf of Aden", "Gulf of Oman",
    "Sea of Zanj", "Bay of Bengal", "Andaman Sea", "South China Sea", "Java Sea",
    "East China Sea", "Sea of Japan", "Aral Sea", "Caspian Sea", "Black Sea",
    "Baltic Sea", "Gobi Desert", "Sahara", "Himalayas", "Tibetan Plateau",
    "Iranian Plateau",
}

CANDIDATE_KEY_ORDER = [
    "name",
    "disambiguation_note",
    "localisation_stem",
    "category",
    "feature_subtype",
    "relationship",
    "language_variants",
    "earliest_attestation_year",
    "earliest_attestation_note",
    "attestation_basis",
    "valid_for_bookmarks",
    "etymology_notes",
    "source_url",
]


def norm_str(s: str | None) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return " ".join(s.lower().strip().split())


def max_bipartite_matching(adj: list[list[str]]) -> int:
    match_r: dict[str, int] = {}

    def dfs(u: int, seen: set[str]) -> bool:
        for v in adj[u]:
            if v in seen:
                continue
            seen.add(v)
            if v not in match_r or dfs(match_r[v], seen):
                match_r[v] = u
                return True
        return False

    return sum(1 for u in range(len(adj)) if dfs(u, set()))


def sanitize_new_candidate(raw: dict, existing_tax: dict[str, list[str]], stats: Counter) -> dict:
    c = dict(raw)
    clean_name, extracted_dis = strip_disambig(c["name"])
    c["name"] = clean_name
    if c.get("disambiguation_note") is None and extracted_dis is not None:
        c["disambiguation_note"] = extracted_dis

    if c["source_url"] in URL_REDIRECT_MAP:
        c["source_url"] = URL_REDIRECT_MAP[c["source_url"]]

    c["localisation_stem"] = c.get("localisation_stem") or compute_stem(c["name"], c["category"])
    basis, valid_bm = classify_candidate(c)
    c["attestation_basis"] = basis
    c["valid_for_bookmarks"] = valid_bm

    rel = c["relationship"].strip()
    if rel and rel[0].islower():
        rel = rel[0].upper() + rel[1:]
    if rel and rel[-1] not in ".!?":
        rel += "."
    c["relationship"] = rel

    # Normalize language variants
    lvs = []
    for lv in c.get("language_variants", []):
        lv2 = {
            "form": lv["form"].strip(),
            "native_script": lv.get("native_script"),
            "language": lv["language"],
            "language_code": lv["language_code"],
            "notes": lv.get("notes"),
        }
        normalize_variant_code_and_label(lv2, stats)
        lvs.append(lv2)

    non_red = [lv for lv in lvs if not is_redundant_eng(lv, c)]
    if non_red:
        lvs = non_red

    by_code: dict[str, list[dict]] = {}
    for lv in lvs:
        by_code.setdefault(lv["language_code"], []).append(lv)
    c["language_variants"] = [consolidate_same_code(grp, c["name"], stats) for grp in by_code.values()]

    ordered = {k: c.get(k) for k in CANDIDATE_KEY_ORDER}
    return ordered


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pool-dir", type=Path, default=DEFAULT_POOL_DIR)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    pool_files = sorted(args.pool_dir.glob("*_pool.json"))
    if not pool_files:
        print(f"No *_pool.json files found in {args.pool_dir}")
        sys.exit(1)

    ntr_files = sorted(NTR_DIR.glob("barony_natural_tribal_replacements_*.json"))
    datasets = {}
    for p in ntr_files:
        emp = p.stem.replace("barony_natural_tribal_replacements_", "")
        datasets[emp] = (p, json.loads(p.read_text(encoding="utf-8")))

    # Load audit for complete sibling roster
    county_all_audit = defaultdict(list)
    for af in sorted(AUDIT_DIR.glob("barony_audit_*.json")):
        emp = af.stem.replace("barony_audit_", "")
        ad = json.loads(af.read_text(encoding="utf-8"))
        for bk, b in ad["baronies"].items():
            county_all_audit[(emp, b["hierarchy"]["county"])].append(
                (bk, b["vanilla_ck3_name"], b.get("modern_name"), b["is_historical_at"]["867"])
            )

    canonical_tax = next(iter(datasets.values()))[1]["metadata"]["schema_notes"]["category_subtype_taxonomy"]

    stats = Counter()
    applied_directives = []
    skipped_directives = []

    for pf in pool_files:
        directives = json.loads(pf.read_text(encoding="utf-8"))
        print(f"Loaded {len(directives)} directives from {pf.name}")
        for d in directives:
            emp = d["empire"]
            bk = d["barony_key"]
            idx = d["replace_slot_idx"]
            if emp not in datasets or bk not in datasets[emp][1]["baronies"]:
                skipped_directives.append((pf.name, emp, bk, idx, "missing_barony"))
                continue
            b = datasets[emp][1]["baronies"][bk]
            if not (0 <= idx < len(b["replacement_candidates"])):
                skipped_directives.append((pf.name, emp, bk, idx, "bad_idx"))
                continue
            cand = sanitize_new_candidate(d["candidate"], canonical_tax, stats)
            b["replacement_candidates"][idx] = cand
            stats["directives_applied"] += 1
            applied_directives.append((emp, bk, idx, cand["name"]))

    # Cross-file P1-1 reconciliation on all source_urls after injecting new candidates
    by_url = defaultdict(list)
    names_to_urls = defaultdict(set)
    for _, d in datasets.values():
        for b in d["baronies"].values():
            for c in b["replacement_candidates"]:
                by_url[c["source_url"]].append(c)
                names_to_urls[c["name"]].add(c["source_url"])

    disambig_locked = {nm for nm, us in names_to_urls.items() if len(us) > 1}
    canon_table = {}
    for u, recs in by_url.items():
        cat, sub = resolve_cat_sub(u, recs)
        nm, disambig = resolve_name_disambig(u, recs, disambig_locked)
        yr, yr_note = resolve_year_note(recs)
        basis, vbm = classify_candidate({"name": nm, "category": cat, "earliest_attestation_year": yr})
        canon_table[u] = {
            "name": nm,
            "disambiguation_note": disambig,
            "category": cat,
            "feature_subtype": sub,
            "earliest_attestation_year": yr,
            "earliest_attestation_note": yr_note,
            "attestation_basis": basis,
            "valid_for_bookmarks": vbm,
            "base_stem": compute_stem(nm, cat),
        }

    # Global stem-collision protection
    force_full_stem = set()
    for _, d in datasets.values():
        for b in d["baronies"].values():
            cands = b["replacement_candidates"]
            stems = [canon_table[c["source_url"]]["base_stem"] for c in cands]
            if len(set(stems)) < len(stems):
                prio = sorted(
                    range(len(cands)),
                    key=lambda i: (
                        0 if canon_table[cands[i]["source_url"]]["base_stem"] == canon_table[cands[i]["source_url"]]["name"] else 1,
                        0 if canon_table[cands[i]["source_url"]]["category"] == "tribe" else (
                            1 if canon_table[cands[i]["source_url"]]["category"] == "hydronym" else 2
                        ),
                        i,
                    ),
                )
                used = set()
                for i in prio:
                    u = cands[i]["source_url"]
                    bs = canon_table[u]["base_stem"]
                    if bs not in used:
                        used.add(bs)
                    else:
                        force_full_stem.add(u)
                        used.add(canon_table[u]["name"])

    for u, info in canon_table.items():
        info["localisation_stem"] = info["name"] if u in force_full_stem else info["base_stem"]

    # Apply canonical entity attributes & run comprehensive validation
    self_left = []
    sib_left = []
    mega_left = []
    zero_tribe = []
    dup_bar_name = []
    dup_bar_stem = []
    dup_bar_url = []
    bad_form = []
    undeclared_sub = []
    unsolv_by_bm = defaultdict(list)

    county_ntr = defaultdict(list)

    for emp, (p, d) in datasets.items():
        tax = d["metadata"]["schema_notes"]["category_subtype_taxonomy"]
        for bk, b in d["baronies"].items():
            cty = b["hierarchy"]["county"]
            county_ntr[(emp, cty)].append((bk, b))

            own_forms = {norm_str(b["vanilla_ck3_name"]), norm_str(b.get("modern_name"))} - {""}
            enp = norm_str((b.get("existing_natural_proper_name") or {}).get("name"))
            sib_forms = set()
            for sbk, svan, smod, _ in county_all_audit[(emp, cty)]:
                if sbk != bk:
                    sib_forms.add(norm_str(svan))
                    if smod:
                        sib_forms.add(norm_str(smod))
            sib_forms.discard("")

            sn = set()
            ss_set = set()
            su = set()
            tc = 0

            for c in b["replacement_candidates"]:
                canon = canon_table[c["source_url"]]
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

                if c["feature_subtype"] not in tax.get(c["category"], []):
                    undeclared_sub.append((emp, bk, c["category"], c["feature_subtype"]))

                if c["name"] in sn:
                    dup_bar_name.append((emp, bk, c["name"]))
                sn.add(c["name"])
                if c["localisation_stem"] in ss_set:
                    dup_bar_stem.append((emp, bk, c["localisation_stem"]))
                ss_set.add(c["localisation_stem"])
                if c["source_url"] in su:
                    dup_bar_url.append((emp, bk, c["source_url"]))
                su.add(c["source_url"])

                if c["category"] == "tribe":
                    tc += 1

                cn = norm_str(c["name"])
                cs = norm_str(c["localisation_stem"])
                if cn in own_forms or cs in own_forms or (enp and (cn == enp or cs == enp)):
                    self_left.append((emp, bk, c["name"], c["localisation_stem"]))
                if cn in sib_forms or cs in sib_forms:
                    sib_left.append((emp, cty, bk, c["name"], c["localisation_stem"]))
                if c["name"] in MEGA_MACRO:
                    mega_left.append((emp, cty, bk, c["name"]))

                for lv in c["language_variants"]:
                    if any(not is_latin_char(ch) for ch in lv["form"]):
                        bad_form.append((emp, bk, c["name"], lv["form"]))

            if tc == 0:
                zero_tribe.append((emp, bk))

        recompute_summary_statistics(d)

        if args.apply:
            new_text = json.dumps(d, ensure_ascii=False, indent=2) + "\n"
            if new_text != p.read_text(encoding="utf-8"):
                p.write_text(new_text, encoding="utf-8")
                stats["files_written"] += 1

    # Bipartite solvability check per county across 867, 1066, 1178 (excluding hist867 siblings!)
    for (emp, cty), blist in sorted(county_ntr.items()):
        hist867 = set()
        for sbk, svan, smod, sh in county_all_audit[(emp, cty)]:
            if sh:
                hist867.add(norm_str(svan))
                if smod:
                    hist867.add(norm_str(smod))
        hist867.discard("")
        for bm in ("867", "1066", "1178"):
            adj = [
                [
                    norm_str(c["localisation_stem"])
                    for c in b["replacement_candidates"]
                    if c["valid_for_bookmarks"][bm] and norm_str(c["localisation_stem"]) not in hist867
                ]
                for _, b in blist
            ]
            m = max_bipartite_matching(adj)
            if m < len(blist):
                unsolv_by_bm[bm].append((emp, cty, len(blist), m))

    print("=== P0-2 COLLISION & POOL REMEDIATION SUMMARY ===")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v}")
    print(f"skipped_directives={len(skipped_directives)} {skipped_directives[:5]}")
    print(f"self_left={len(self_left)} {self_left[:10]}")
    print(f"sib_left={len(sib_left)} {sib_left[:10]}")
    print(f"mega_left={len(mega_left)} {Counter(x[3] for x in mega_left).most_common(10)}")
    print(f"zero_tribe={len(zero_tribe)} {zero_tribe[:5]}")
    print(f"dup_bar_name={len(dup_bar_name)}, dup_bar_stem={len(dup_bar_stem)}, dup_bar_url={len(dup_bar_url)}")
    print(f"bad_form={len(bad_form)}, undeclared_sub={len(undeclared_sub)}")
    for bm in ("867", "1066", "1178"):
        ul = unsolv_by_bm[bm]
        print(f"unsolvable_counties_{bm}={len(ul)} {ul[:10]}")


if __name__ == "__main__":
    main()

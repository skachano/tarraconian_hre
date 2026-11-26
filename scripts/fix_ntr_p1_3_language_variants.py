#!/usr/bin/env python3
"""
fix_ntr_p1_3_language_variants.py

Fixes P1-3 (Language Variant Policy & ISO 639-3 / 639-5 Consistency) across all
47 files in data/natural_tribal_replacements/:
1. Fixes ISO codes & language labels:
   - Siberian Tatar `tat` -> ISO 639-3 `sty` (keeping `tat` = "Tatar").
   - Classical Mongolian `mon` -> ISO 639-3 `cmg` (keeping `mon` = "Mongolian").
   - `otk` "Turkic" -> "Old Turkic".
   - `ses` "Songhai" / "Koyraboro Senni" -> "Koyraboro Senni Songhai".
   - `roa` "Gallo" -> "Romance (Gallo)".
   - Gaulish `cel-gau` -> ISO 639-3 `xtg`.
2. Removes stray leading `*` on attested non-proto codes (`cym: *Ir-afon`, `ang: *Wagenēa`).
3. Removes redundant `eng` copies (`form == name / stem / River <name>`) whenever
   at least one non-`eng` variant exists (retaining `eng` only for the 35 English/
   Nigerian features where no non-English variant exists).
4. Consolidates duplicate `language_code` entries within the same candidate cleanly,
   preserving alternate forms/native scripts/notes inside `notes` so every candidate
   has unique `language_code` keys without losing historical forms.
5. Documents both ISO 639-3/639-5 and permitted Wiktionary proto-stage codes
   (`cel-bry`, `cel-pro`, `gem-pro`, `sla-pro`, `urj-fin-pro`) in `schema_notes`,
   and recomputes `metadata.summary_statistics` (`unique_language_codes`,
   `candidates_with_multilingual_variants`).
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
NTR_DIR = REPO_DIR / "data" / "natural_tribal_replacements"

sys.path.insert(0, str(REPO_DIR / "scripts"))
from fix_ntr_p0_3_historicity import is_latin_char
from fix_ntr_p1_1_reconcile_entities import recompute_summary_statistics

PROTO_STAR_CODES = {"cel-bry", "cel-pro", "gem-pro", "sla-pro", "urj-fin-pro", "bat", "xtg"}


def normalize_variant_code_and_label(lv: dict, stats: Counter) -> None:
    lc = lv["language_code"]
    lang = lv["language"]

    if lc == "tat" and lang == "Siberian Tatar":
        lv["language_code"] = "sty"
        stats["code_tat_to_sty"] += 1
    elif lc == "mon" and lang == "Classical Mongolian":
        lv["language_code"] = "cmg"
        stats["code_mon_to_cmg"] += 1
    elif lc == "otk" and lang != "Old Turkic":
        lv["language"] = "Old Turkic"
        stats["label_otk_fixed"] += 1
    elif lc == "ses" and lang != "Koyraboro Senni Songhai":
        lv["language"] = "Koyraboro Senni Songhai"
        stats["label_ses_unified"] += 1
    elif lc == "roa" and lang == "Gallo":
        lv["language"] = "Romance (Gallo)"
        stats["label_roa_clarified"] += 1
    elif lc == "cel-gau":
        lv["language_code"] = "xtg"
        stats["code_cel_gau_to_xtg"] += 1
    elif lc == "tmh" and lang != "Tamashek":
        lv["language"] = "Tamashek"
        stats["label_tmh_unified"] += 1
    elif lc == "syc" and lang != "Syriac":
        lv["language"] = "Syriac"
        stats["label_syc_unified"] += 1
    elif lc == "mak" and lang != "Makasar":
        lv["language"] = "Makasar"
        stats["label_mak_unified"] += 1

    # Strip stray leading '*' on attested non-proto languages
    if lv["language_code"] not in PROTO_STAR_CODES and lv["form"].startswith("*"):
        lv["form"] = lv["form"].lstrip("*").strip()
        stats["stray_star_stripped"] += 1


def is_redundant_eng(lv: dict, c: dict) -> bool:
    if lv["language_code"] != "eng" or lv.get("native_script") is not None:
        return False
    fl = lv["form"].strip().lower()
    nl = c["name"].strip().lower()
    sl = c["localisation_stem"].strip().lower()
    return fl == nl or fl == sl or fl == f"river {nl}" or fl == f"river {sl}"


def consolidate_same_code(group: list[dict], c_name: str, stats: Counter) -> dict:
    if len(group) == 1:
        return group[0]

    # Pick primary variant: prefer non-'River X' form, else exact match to c_name if non-eng, else first
    def rank(idx_lv):
        idx, lv = idx_lv
        fl = lv["form"].strip().lower()
        is_river_prefix = 1 if fl.startswith("river ") else 0
        exact = 0 if fl == c_name.strip().lower() else 1
        return (is_river_prefix, exact, idx)

    ordered = [lv for _, lv in sorted(enumerate(group), key=rank)]
    prim = dict(ordered[0])
    seen_forms = {(prim["form"].lower(), prim.get("native_script"))}
    alt_parts = []

    for sec in ordered[1:]:
        sig = (sec["form"].lower(), sec.get("native_script"))
        s_note = (sec.get("notes") or "").strip().rstrip(".")
        if sig in seen_forms:
            stats["exact_dup_code_dropped"] += 1
            if s_note and s_note.lower() not in (prim.get("notes") or "").lower():
                alt_parts.append(s_note)
            continue
        seen_forms.add(sig)
        stats["dup_code_merged"] += 1
        part = f"'{sec['form']}'"
        if sec.get("native_script"):
            part += f" ({sec['native_script']})"
        if s_note:
            part += f" — {s_note}"
        alt_parts.append(part)

    if alt_parts:
        p_note = (prim.get("notes") or "").strip().rstrip(".")
        joined = "; also ".join(alt_parts)
        if p_note:
            prim["notes"] = f"{p_note}; also {joined}."
        else:
            prim["notes"] = f"Also {joined}."

    return prim


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    files = sorted(NTR_DIR.glob("barony_natural_tribal_replacements_*.json"))
    stats = Counter()
    code_to_langs = defaultdict(set)
    empty_lvs = []
    remaining_eng = []
    bad_latin_forms = []
    sample_merges = []

    updated_policy = (
        "Include core local/classical forms plus regionally scoped vernaculars and genuinely "
        "distinct exonyms; exclude out-of-region exonym padding and redundant eng copies "
        "(eng is retained only when no non-English variant exists). Uses ISO 639-3 / ISO 639-5 "
        "language_code values plus documented Wiktionary proto/stage codes (sla-pro, gem-pro, "
        "cel-pro, cel-bry, urj-fin-pro); reconstructed proto/ancient forms carry a leading '*'."
    )
    updated_multiling_note = (
        "Count of replacement candidates having more than 1 distinct language_code "
        "(ISO 639-3 / ISO 639-5 or documented proto-stage code) across language_variants."
    )

    for p in files:
        d = json.loads(p.read_text(encoding="utf-8"))
        sn = d["metadata"]["schema_notes"]
        sn["language_variants_policy"] = updated_policy
        sn["candidates_with_multilingual_variants"] = updated_multiling_note

        for bk, b in d["baronies"].items():
            for c in b["replacement_candidates"]:
                lvs = c["language_variants"]
                for lv in lvs:
                    normalize_variant_code_and_label(lv, stats)

                # Drop redundant 'eng' only when at least one other variant survives
                non_redundant = [lv for lv in lvs if not is_redundant_eng(lv, c)]
                if len(non_redundant) >= 1 and len(non_redundant) < len(lvs):
                    stats["redundant_eng_removed"] += len(lvs) - len(non_redundant)
                    lvs = non_redundant
                elif len(non_redundant) == 0 and lvs:
                    stats["sole_eng_retained"] += 1

                # Consolidate duplicate language_code within candidate (preserving order of first appearance)
                by_code: dict[str, list[dict]] = {}
                for lv in lvs:
                    by_code.setdefault(lv["language_code"], []).append(lv)

                new_lvs = []
                for lc, grp in by_code.items():
                    merged = consolidate_same_code(grp, c["name"], stats)
                    if len(grp) > 1 and len(sample_merges) < 10:
                        sample_merges.append((p.stem, bk, c["name"], lc, merged["form"], merged["notes"]))
                    new_lvs.append(merged)

                c["language_variants"] = new_lvs

                if not new_lvs:
                    empty_lvs.append((p.name, bk, c["name"]))
                for lv in new_lvs:
                    code_to_langs[lv["language_code"]].add(lv["language"])
                    if lv["language_code"] == "eng":
                        remaining_eng.append((p.name, bk, c["name"], len(new_lvs), lv["form"]))
                    if any(not is_latin_char(ch) for ch in lv["form"]):
                        bad_latin_forms.append((p.name, bk, c["name"], lv["form"]))

        recompute_summary_statistics(d)

        if args.apply:
            new_text = json.dumps(d, ensure_ascii=False, indent=2) + "\n"
            if new_text != p.read_text(encoding="utf-8"):
                p.write_text(new_text, encoding="utf-8")
                stats["files_written"] += 1

    inconsistent_labels = {k: sorted(v) for k, v in code_to_langs.items() if len(v) > 1}
    print("=== P1-3 LANGUAGE VARIANT CLEANUP SUMMARY ===")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v}")
    print(f"Empty language_variants lists: {len(empty_lvs)} {empty_lvs[:5]}")
    print(f"Inconsistent language_code -> language labels: {len(inconsistent_labels)} {inconsistent_labels}")
    print(f"Remaining eng variants total: {len(remaining_eng)} (multi-var: {sum(1 for x in remaining_eng if x[3] > 1)})")
    for x in [r for r in remaining_eng if r[3] > 1][:10]:
        print("  multi-var eng kept:", x)
    print(f"Bad non-Latin forms: {len(bad_latin_forms)}")
    print("\nSample merged duplicate codes:")
    for sm in sample_merges[:8]:
        print(" ", sm)


if __name__ == "__main__":
    main()

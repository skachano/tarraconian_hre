#!/usr/bin/env python3
"""
fix_ntr_p0_4_name_hygiene.py

Fixes P0-4 across all 47 files in data/natural_tribal_replacements/:
1. Strips Wikipedia disambiguation parentheticals and comma-qualifiers from
   candidate `name`, moving them to `disambiguation_note` (null if none).
2. Adds `localisation_stem` to every candidate — a clean CK3-ready toponym
   stem free of redundant English generic suffixes/prefixes ('River', 'Mount',
   'Lake', 'Mountains', 'people', etc.) while preserving meaningful compounds
   ('Red River', 'White Nile', 'Gulf of Oman', 'Great Lakes Depression').
3. Strips the 6 Wikipedia disambiguators from `language_variants[].form` in e_germany.
4. Updates metadata.schema_notes and recomputes summary_statistics.
"""

import argparse
import json
import re
from collections import Counter
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
NTR_DIR = REPO_DIR / "data" / "natural_tribal_replacements"

COMMON_ENG = {
    "the", "ore", "owl", "bear", "beaver", "wolf", "fox", "eagle", "snake", "fish", "bird",
    "duck", "swan", "deer", "elk", "bull", "cow", "horse", "sheep", "goat", "dog", "cat",
    "pine", "oak", "birch", "willow", "alder", "ash", "elm", "cedar", "maple", "reed",
    "grass", "moss", "peat", "wood", "timber", "coal", "chalk", "lime", "flint", "clay",
    "slate", "granite", "marble", "crystal", "moon", "sun", "star", "cloud", "rain", "snow",
    "ice", "wind", "storm", "thunder", "fire", "smoke", "shadow", "spring", "well", "bridge",
    "castle", "tower", "church", "chapel", "abbey", "mill", "ford", "port", "harbor", "haven",
    "crown", "king", "queen", "prince", "duke", "bishop", "monk", "devil", "giant", "dragon",
    "ghost", "spirit", "angel", "heaven", "hell", "paradise", "hope", "fortune", "good",
    "bad", "fair", "foul", "wild", "calm", "swift", "rapid", "slow", "smooth", "rough",
    "sharp", "blunt", "broad", "narrow", "wide", "thick", "thin", "heavy", "light", "bright",
    "dark", "clear", "cloudy", "muddy", "sandy", "rocky", "stony", "grassy", "wooded",
    "forested", "barren", "fertile", "empty", "full", "middle", "central", "inner", "outer",
    "high", "low", "upper", "lower", "twin", "double", "half", "main", "side", "back",
    "front", "top", "bottom", "head", "foot", "mouth", "neck", "arm", "leg", "hand",
    "finger", "thumb", "toe", "eye", "ear", "nose", "tooth", "horn", "tail", "wing",
    "feather", "peak", "ridge", "crest", "slope", "cliff", "crag", "gorge", "pass", "gap",
    "cut", "bend", "fork", "branch", "stream", "creek", "brook", "pond", "pool", "sound",
    "channel", "basin", "drain", "sand", "dune", "flat", "moors", "downs", "dales",
    "black", "white", "red", "blue", "green", "yellow", "grey", "gray", "brown", "golden",
    "silver", "salt", "bitter", "sweet", "sour", "great", "big", "large", "grand", "little",
    "small", "short", "long", "deep", "shallow", "north", "south", "east", "west",
    "northern", "southern", "eastern", "western", "new", "old", "dead", "holy", "sacred",
    "dry", "wet", "hot", "cold", "warm", "cross", "stone", "rock", "mud", "pearl", "jade",
    "gold", "iron", "copper", "tin", "flaming", "burning", "sleeping", "broken", "two",
    "three", "four", "five", "six", "seven", "eight", "nine", "ten", "thousand", "hundred",
    "royal", "imperial", "ancient", "hidden", "lost", "open", "bare", "bald", "silent",
    "frozen", "coastal", "maritime", "inland", "alpine", "interior", "sea", "ocean", "lake",
    "river", "mountain", "mountains", "hill", "hills", "forest", "desert", "valley", "plain",
    "plateau", "island", "islands", "peninsula", "marsh", "swamp", "bay", "gulf", "strait",
    "cape", "mount", "gorge", "pass", "oasis", "delta", "sandstone", "limestone", "volcanic",
    "cattle", "water", "waters", "bush", "savanna", "steppe", "tundra", "taiga", "jungle",
    "rainforest", "coast", "shore", "reef", "atoll", "alluvial", "highland", "lowland",
    "upland", "table", "sugar", "camel", "elephant", "lion", "tiger", "leopard", "monkey",
    "buffalo", "crocodile",
}

DIR_PREFIXES = {
    "great", "little", "big", "upper", "lower", "middle", "central", "inner", "outer",
    "north", "south", "east", "west", "northern", "southern", "eastern", "western",
    "northeast", "northwest", "southeast", "southwest", "three", "two", "four", "five",
}

KEEP_FULL_WHEN_DIR_MODIFIED = {
    "plain", "plains", "valley", "depression", "delta", "bay", "gulf", "strait",
    "archipelago", "pass", "forest", "desert", "steppe", "highlands", "lowlands", "uplands",
}

TRAILING_DESCRIPTOR_RX = re.compile(
    r"^(.+?)\s+(River|Rivers|Mountain|Mountains|Range|Hills|Hill|Lake|Lakes|Valley|"
    r"Basin|Plateau|Forest|Marsh|Marshes|Swamp|Bog|Fen|Fens|Bay|Gulf|Strait|Estuary|"
    r"Desert|Plain|Plains|Steppe|Highlands|Lowlands|Uplands|Peninsula|Island|Islands|"
    r"Volcanic Complex|Massif|Ridge|Archipelago|Lagoon|Delta|Oasis|Depression|"
    r"Corridor|Canyon|Gorge|Pass)$"
)


def strip_disambig(name: str) -> tuple[str, str | None]:
    if name == "Akershus / Oslofjord":
        return "Oslofjord", None
    if name in ("Mainland, Orkney", "Mainland, Shetland"):
        a, b = name.split(", ", 1)
        return a.strip(), b.strip()
    m = re.match(r"^(.+?)\s*\(([^)]+)\)$", name)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return name.strip(), None


def compute_stem(clean_name: str, cat: str) -> str:
    s = clean_name
    if cat == "tribe":
        m = re.match(r"^(.+?)\s+(peoples?|tribes?|clans?|confederation|confederacy)$", s, re.I)
        if m:
            cand = m.group(1).strip()
            if cand.lower() not in COMMON_ENG and not any(w in COMMON_ENG for w in cand.lower().split()):
                return cand
        return s

    if re.search(r"\bof\b", s, re.I):
        return s

    m = re.match(r"^(River|Lake|Mount)\s+(.+)$", s)
    if m:
        rest = m.group(2).strip()
        rwords = rest.lower().split()
        if len(rwords) == 1 and rwords[0] in COMMON_ENG:
            return s
        if all(w in COMMON_ENG for w in rwords):
            return s
        return rest

    m = TRAILING_DESCRIPTOR_RX.match(s)
    if m:
        head = m.group(1).strip()
        tail = m.group(2).strip().lower()
        hwords = head.lower().split()
        if all(w in COMMON_ENG for w in hwords):
            return s
        if hwords[-1] in COMMON_ENG:
            return s
        if hwords[0] in DIR_PREFIXES and tail in KEEP_FULL_WHEN_DIR_MODIFIED:
            return s
        return head

    return s


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    files = sorted(NTR_DIR.glob("barony_natural_tribal_replacements_*.json"))
    stats = Counter()
    dup_clean_names = []
    dup_stems = []
    still_dirty = []

    for p in files:
        d = json.load(open(p, encoding="utf-8"))
        sn = d["metadata"]["schema_notes"]
        sn["name"] = "Clean display name of the replacement candidate (Wikipedia disambiguation suffixes extracted to disambiguation_note)."
        sn["disambiguation_note"] = "Optional disambiguator extracted from parenthetical/comma qualifiers (e.g. 'Liao', 'Orkney', 'river'); null if none."
        sn["localisation_stem"] = "Clean CK3-ready toponym stem stripped of redundant generic English feature suffixes/prefixes ('River', 'Mount', 'Lake', 'people', etc.) while preserving meaningful compounds."

        uniq_names = set()
        uniq_stems = set()

        for bk, b in d["baronies"].items():
            # Pass 1: clean names and candidate stems
            temp = []
            for c in b["replacement_candidates"]:
                if "disambiguation_note" in c and "(" not in c["name"] and "," not in c["name"] and "/" not in c["name"]:
                    clean_name = c["name"]
                    disambig = c["disambiguation_note"]
                else:
                    clean_name, disambig = strip_disambig(c["name"])
                stem = compute_stem(clean_name, c["category"])
                temp.append((c, clean_name, disambig, stem))

            # Pass 2: if two candidates in the same barony share a stem (e.g. 'Nuba' + 'Nuba Mountains',
            # 'Bureya River' + 'Bureya Range'), keep clean_name for non-tribe / later secondary entries.
            stem_counts = Counter(t[3] for t in temp)
            if any(cnt > 1 for cnt in stem_counts.values()):
                used_stems = set()
                resolved = []
                # Prefer unshortened entries first (so 'Gorgol' claims 'Gorgol' before 'Gorgol River' does),
                # then tribe, then hydronym, else first occurrence.
                priority = sorted(
                    range(len(temp)),
                    key=lambda idx: (
                        0 if temp[idx][3] == temp[idx][1] else 1,
                        0 if temp[idx][0]["category"] == "tribe" else (1 if temp[idx][0]["category"] == "hydronym" else 2),
                        idx,
                    ),
                )
                stem_override = {}
                for idx in priority:
                    c, clean_name, disambig, stem = temp[idx]
                    if stem not in used_stems:
                        used_stems.add(stem)
                        stem_override[idx] = stem
                    else:
                        stem_override[idx] = clean_name
                        used_stems.add(clean_name)
                temp = [(c, cn, dn, stem_override[idx]) for idx, (c, cn, dn, _) in enumerate(temp)]

            new_cands = []
            seen_names = set()
            seen_stems = set()
            for c, clean_name, disambig, stem in temp:
                if disambig is not None:
                    stats["with_disambiguation_note"] += 1
                if c["name"] != clean_name:
                    stats["name_cleaned"] += 1

                if stem != clean_name:
                    stats["stem_shortened"] += 1

                if any(ch in clean_name for ch in ("(", ")", ",", "/")) or any(ch in stem for ch in ("(", ")", ",", "/")):
                    still_dirty.append((p.name, bk, clean_name, stem))

                if clean_name in seen_names:
                    dup_clean_names.append((p.name, bk, clean_name))
                seen_names.add(clean_name)

                if stem in seen_stems:
                    dup_stems.append((p.name, bk, stem, [x["name"] for x in b["replacement_candidates"]]))
                seen_stems.add(stem)

                # Also clean any lingering disambiguators in language_variants[].form
                for lv in c["language_variants"]:
                    lv_clean, _ = strip_disambig(lv["form"])
                    if lv_clean != lv["form"]:
                        lv["form"] = lv_clean
                        stats["lv_form_cleaned"] += 1

                # Construct ordered candidate dict
                new_c = {
                    "name": clean_name,
                    "disambiguation_note": disambig,
                    "localisation_stem": stem,
                    "category": c["category"],
                    "feature_subtype": c["feature_subtype"],
                    "relationship": c["relationship"],
                    "language_variants": c["language_variants"],
                    "earliest_attestation_year": c["earliest_attestation_year"],
                    "earliest_attestation_note": c["earliest_attestation_note"],
                    "attestation_basis": c["attestation_basis"],
                    "valid_for_bookmarks": c["valid_for_bookmarks"],
                    "etymology_notes": c["etymology_notes"],
                    "source_url": c["source_url"],
                }
                new_cands.append(new_c)
                uniq_names.add(clean_name)
                uniq_stems.add(stem)

            b["replacement_candidates"] = new_cands

        ss = d["metadata"]["summary_statistics"]
        ss["unique_replacement_names"] = len(uniq_names)
        ss["unique_localisation_stems"] = len(uniq_stems)

        if args.apply:
            with open(p, "w", encoding="utf-8") as fh:
                json.dump(d, fh, ensure_ascii=False, indent=2)
                fh.write("\n")
            stats["files_written"] += 1

    print("=== P0-4 NAME HYGIENE SUMMARY ===")
    for k, v in sorted(stats.items()):
        print(f"  {k}: {v}")
    print(f"Still dirty (parens/comma/slash): {len(still_dirty)} {still_dirty[:10]}")
    print(f"Intra-barony duplicate clean names: {len(dup_clean_names)} {dup_clean_names[:10]}")
    print(f"Intra-barony duplicate stems: {len(dup_stems)} {dup_stems[:10]}")


if __name__ == "__main__":
    main()

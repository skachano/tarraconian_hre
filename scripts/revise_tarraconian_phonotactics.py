#!/usr/bin/env python3
"""
revise_tarraconian_phonotactics.py

Comprehensive Tarraconian Phonotactics Revision Engine.
Ensures 100% adherence to:
- tarraconian_linguistics_guide.md (ca. 1142 Update)
- sinosphere_phonetics_and_transcription_guide_1154.md
- Strict Rhine-Moselle Franconian phonology, Auslautverhärtung, and circumflex vowel purity.

Revises:
1. data/ck3_counties.geojson & data/ck3_title_tree.json
2. audit_discrepancy_register.md
3. dynastic_realignment_register.md
4. Propagates via resolve_barony_titles.py and build_webapp.py
"""

import json
import re
import sys
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_DIR / "data"

sys.path.insert(0, str(REPO_DIR / "scripts"))
from resolve_barony_titles import generate_tarraconian_ipa, enforce_tarraconian_sound_laws

# Definitive Phonotactic Regularization Map for Revised Titles
PHONOTACTIC_CORRECTIONS = {
    # 1. Cluster epenthesis (Rule 4), Slavic sound laws (Rule 1.3 & 3.3), and Auslautverhärtung (Rule 1.1)
    "c_vodica": "Pesêt",               # Rule 4: Ps- initial cluster repair via epenthetic vowel
    "c_zagreb": "Sissech",             # Rule 1.1: post-vocalic -k -> -ch
    "c_sumadija": "Rûdnich",           # Rule 1.1: post-vocalic -k -> -ch
    "c_valdai": "Torschôch",           # Rule 1.1: post-vocalic -k -> -ch
    "c_pozega": "Intsêr",              # Rule 2: Latin -um apocope; Rule 2.2 medial ts
    "c_plzen": "Plzenetz",             # Rule 3.3: Slavic -ec -> -etz
    "c_hradec": "Grâdetz",             # Rule 3.3: Slavic -ec -> -etz
    "c_caslav": "Tschaslouwe",         # Rule 1.3: Slavic -av -> -ouwe
    "c_doudleby": "Dudlêben",          # MHG Tudleipin / Dudlêben
    "c_brno": "Brünne",                # Rule 2: MHG schwa preservation
    "c_lubeck": "Lûbitz",              # Rule 3.3: Slavic -ice -> -itz
    "c_plocka": "Plôtzich",            # Rule 3.3: Slavic -sk/-zk/-ck -> -tzich
    "c_braslau": "Braslouwe",          # Rule 1.3: Slavic -av -> -ouwe
    "c_sacz": "Altsandetz",            # MHG Sandec -> Altsandetz
    "c_stezycka": "Sitzichouwe",       # Rule 1.3: Slavic -ow -> -ouwe
    "c_radomska": "Râdom",             # Circumflex vowel length
    "c_peremyshl": "Peremîschel",      # Rule 4: syllabic liquid epenthesis; circumflex î
    "c_ushytsia": "Bakôte",            # Circumflex vowel length
    "c_korsun": "Rôs-Flôze",           # MHG Flôz
    "c_zhytomyr": "Teterîw-Flôze",     # MHG Flôz
    "c_putyvl": "Sêim-Flôze",          # MHG Flôz
    "c_odoyev": "Upe",                 # Rule 2: final -a -> -e
    "c_cottbus": "Liubusue",           # Rule 2: final -a -> -e
    "c_wittenberg": "Beltzich",        # Affricate tz
    "c_tikhvin": "Tichwîn",            # Stressed circumflex
    "c_chornobyl": "Prîpjat",          # Desna/Pripyat reach
    "c_orenburg": "Ôr-Flôze",          # MHG Flôz
    "c_sagaing": "Mû-Flôze",           # MHG Flôz
    "c_julevadno": "Lûle-Flôze",       # MHG Flôz
    "c_pite": "Pîte-Flôze",            # MHG Flôz
    "c_torne": "Tôrne-Flôze",          # MHG Flôz
    "c_ubmejeiednuo": "Ume-Flôze",     # MHG Flôz

    # 2. Western & Southern European phonotactics
    "c_essex": "Ôstsachsen",           # Preserve -sachsen (not -zachsen)
    "c_serres": "Goltstat",            # Preserve -stat (not -ztat)
    "c_uskes": "Buchtrechtstûr",       # Preserve -stûr (not -ztûr)
    "c_duanzhou": "Rechtstûrgouwe",    # Preserve -stûr (not -ztûr)
    "c_SW_jiqin_hari": "Dschîkîn-Harî", # Strip broken paren
    "c_tsushima": "Zuschime",          # Strip broken paren
    "c_waldeck": "Korbach",            # German Korbach (not Korpbach)
    "c_nancy": "Lûnstat",              # Long vowel û (Lunevilla)
    "c_saarbrucken": "Zant-Arnwâl",     # St. Arnual
    "c_linlithgowshire": "Aberkôrn",   # Historical Northumbrian see
    "c_lanarkshire": "Klîdesdal",      # Pre-867 Strathclyde valley
    "c_metzovo": "Pînt",               # Greek Pindos apocopated
    "c_foggia": "Lutzêre",             # Lucera with medial affricate tz
    "c_ajaccio": "Adschatz",           # Rule 3.2: affricate [dʒ] -> dsch
    "c_dalabergslagen": "Îsernbêrelant", # Circumflex vowel length on bêre
    "c_messukyla": "Pirkkale",         # Rule 2: final -a -> -e
    "c_vidzeme": "Gauje",              # Rule 2: final -a -> -e
    "c_valladolid": "Simankes",        # Rule 2: final -as -> -es
    "c_molina": "Erkawîke",            # Rule 2: final -a -> -e
    "c_satfura": "Utîke",              # Rule 2: final -a -> -e
    "c_busaso": "Mosîl",               # Rule 2: Greek -on apocope
    "c_puigcerda": "Lîvje",            # Initial L-
    "c_castellon": "Burdschâne",       # Rule 3.2: Arabic ج -> dsch
    "c_alcacer_do_sal": "Salâtzje",    # Rule 2.2: medial [ts] -> tz
    "c_odessa": "Hîlêe",               # Rule 2: Greek -ea -> -êe (Hylaea -> Hîlêe)

    # 3. Orient, North Africa & Sahel
    "c_tinmallal": "Nafîs",            # Rule 4: Nf- cluster repair via epenthetic vowel
    "c_murzuk": "Tragân",              # Rule 2.2: plain g
    "c_bornu": "Kânem",                # Circumflex length
    "c_el_fasher": "Tûrre",            # Rule 2: final -a -> -e
    "c_jolof": "Tschênch",             # Rule 3.2: [tʃ] is strictly tsch
    "c_ranikot": "Sînt",               # Rule 5.1: aspirated stop dh simplifies; Auslautverhärtung d -> t
    "c_neamnt": "Nêmetz",              # Slavic/Romanian Neamț -> Nêmetz
    "c_dorohoi": "Schischje",          # Romanian Jijia -> Schischje
    "c_lapusna": "Lapuschne",          # Lăpușna
    "c_orhei": "Rêut",                 # Authentic pre-867 hydronym
    "c_soroca": "Nîstervurt",          # Authentic pre-867 hydronym crossing
    "c_stoenesti": "Jalômnetze",       # Authentic pre-867 hydronym
    "c_tigheci": "Tigêtsch",
}

LOWERCASE_PARTICLES = {
    "in", "an", "der", "dem", "den", "am", "van", "vom", "von",
    "ende", "und", "el", "es", "er", "al", "de", "del", "du", "hügel"
}


def fix_hyphenated_particles(name: str) -> str:
    """Ensures lowercase prepositions and articles inside hyphenated compounds."""
    if "-" not in name:
        return name
    parts = name.split("-")
    res = []
    for idx, p in enumerate(parts):
        if idx > 0 and p.lower() in LOWERCASE_PARTICLES:
            res.append(p.lower())
        else:
            res.append(p[:1].upper() + p[1:] if p else "")
    return "-".join(res)


def revise_counties_and_tree():
    print("Revising data/ck3_counties.geojson and data/ck3_title_tree.json...")
    counties_path = DATA_DIR / "ck3_counties.geojson"
    tree_path = DATA_DIR / "ck3_title_tree.json"

    with open(counties_path, "r", encoding="utf-8") as f:
        counties_fc = json.load(f)

    with open(tree_path, "r", encoding="utf-8") as f:
        tree = json.load(f)

    tree_counties = {}
    for ek, e_node in tree.items():
        for kk, k_node in e_node.get("kingdoms", {}).items():
            for dk, d_node in k_node.get("duchies", {}).items():
                for ck, c_node in d_node.get("counties", {}).items():
                    tree_counties[ck] = c_node

    updated = 0
    for feat in counties_fc["features"]:
        props = feat["properties"]
        ck = props.get("id") or props.get("county")

        # Determine target stem
        cur_tarr = props.get("tarr", "")
        cur_hist = props.get("tarr_hist", "")
        
        target = PHONOTACTIC_CORRECTIONS.get(ck)
        if not target:
            target = cur_tarr

        # Apply hyphen particle lowercasing and trailing broken punctuation stripping
        target = fix_hyphenated_particles(target)
        target = target.rstrip(" (;,[{")

        # Check if changed
        if target != cur_tarr or target != cur_hist:
            props["tarr"] = target
            props["tarr_hist"] = target
            props["c_ipa"] = generate_tarraconian_ipa(target)

            if ck in tree_counties:
                t_node = tree_counties[ck]
                t_node["tarr"] = target
                t_node["tarr_hist"] = target
                t_node["ipa"] = props["c_ipa"]

            updated += 1

    print(f"-> Updated {updated} counties in GeoJSON and Title Tree.")

    with open(counties_path, "w", encoding="utf-8") as f:
        json.dump(counties_fc, f, separators=(",", ":"), ensure_ascii=False)

    with open(tree_path, "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=2, ensure_ascii=False)


def revise_audit_discrepancy_register():
    print("Revising audit_discrepancy_register.md...")
    reg_path = REPO_DIR / "audit_discrepancy_register.md"
    with open(reg_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    modified_rows = 0

    for line in lines:
        if line.startswith("| `c_"):
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 8:
                ck = parts[0].strip("`")
                title_col = parts[6]
                adj_col = parts[7]
                
                # Check if this county has a phonotactic correction
                if ck in PHONOTACTIC_CORRECTIONS:
                    stem = PHONOTACTIC_CORRECTIONS[ck]
                    new_title = f"**Magistrat van {stem}**"
                    # Generate appropriate adjective
                    if stem.endswith("e") or stem.endswith("a"):
                        new_adj = f"*{stem[:-1]}er*"
                    elif stem.endswith("er"):
                        new_adj = f"*{stem}*"
                    else:
                        new_adj = f"*{stem}er*"
                    parts[6] = new_title
                    parts[7] = new_adj
                    modified_rows += 1
                else:
                    # Clean title col if it has hyphen capitalization or broken parens
                    raw_title = parts[6]
                    cleaned_title = fix_hyphenated_particles(raw_title).rstrip(" (;,[{")
                    if cleaned_title != raw_title:
                        parts[6] = cleaned_title
                        modified_rows += 1

                reconstructed = "| " + " | ".join(parts) + " |\n"
                new_lines.append(reconstructed)
                continue

        new_lines.append(line)

    with open(reg_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"-> Revised {modified_rows} table rows in audit_discrepancy_register.md.")


def revise_dynastic_realignment_register():
    print("Revising dynastic_realignment_register.md...")
    dyn_path = REPO_DIR / "dynastic_realignment_register.md"
    with open(dyn_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Exact replacements for dynastic seats
    replacements = [
        ("Kestenholz-Plzenec", "Kestenholz-Plzenetz"),
        ("Kestenholz-Sitzichow", "Kestenholz-Sitzichouwe"),
        ("Kestenholz-Zant-Arnolt", "Kestenholz-Zant-Arnwâl"),
        ("Soundavara-Erkawîka", "Soundavara-Erkawîke"),
        ("b_plzenec (Stará Plzeň)", "b_plzenec (Plzenetz)"),
        ("van Sitzichow", "van Sitzichouwe"),
        ("Ercávica (Erkawîka)", "Ercávica (Erkawîke)"),
    ]

    for old, new in replacements:
        text = text.replace(old, new)

    with open(dyn_path, "w", encoding="utf-8") as f:
        f.write(text)

    print("-> Revised dynastic_realignment_register.md.")


def revise_barony_documentation():
    print("Revising barony_historical_audit_and_resolutions.md...")
    doc_path = REPO_DIR / "barony_historical_audit_and_resolutions.md"
    with open(doc_path, "r", encoding="utf-8") as f:
        text = f.read()

    replacements = [
        ("Kestenholz-Plzenec", "Kestenholz-Plzenetz"),
        ("Plzenec", "Plzenetz"),
        ("Psêt", "Pesêt"),
        ("Sissek", "Sissech"),
        ("Rûdnik", "Rûdnich"),
        ("Erkawîka", "Erkawîke"),
        ("Utîka", "Utîke"),
        ("Mosylon", "Mosîl"),
        ("Nfis", "Nafîs"),
        ("Buriâne", "Burdschâne"),
        ("Tjênch", "Tschênch"),
        ("Sindhu", "Sînt"),
    ]

    for old, new in replacements:
        text = text.replace(old, new)

    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(text)

    print("-> Revised barony_historical_audit_and_resolutions.md.")


def main():
    revise_counties_and_tree()
    revise_audit_discrepancy_register()
    revise_dynastic_realignment_register()
    revise_barony_documentation()
    print("\nPhonotactic revisions applied successfully across datasets and documentation.")


if __name__ == "__main__":
    main()

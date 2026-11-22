#!/usr/bin/env python3
"""
generate_title_symbol_adoption.py
---------------------------------
Generates data/title_symbol_adoption.json:
Estimated adoption years, campaign eras, and historical heraldic rationales
for all titles in the CK3 save file timeline (867 to 1194 AD).

Accounts for:
1. In-save sovereign trajectories (first_roman_entry_date & first_roman_holder)
2. Verified antiquity attestations & pre-867 foundations (historical_attestation_db)
3. Historical patron saints and ecclesiastical dedications
4. Option C personality archetypes of conquering/founding lords (Phase 3 engine)
5. Sinitic Procedure 1/2 vermilion chop investitures (1154 Hegemony)
6. Hierarchical propagation to Duchies (Gubernat), Kingdoms (Regenat), and Empires (Keiserrîch)
"""

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

try:
    from historical_attestation_db import ATTESTATION_REGISTRY
except ImportError:
    ATTESTATION_REGISTRY = {}

TRAJECTORIES_PATH = Path("/var/tmp/ck3_audit/phase2/county_lineage_trajectories.json")
TITLE_TREE_PATH = REPO_ROOT / "data" / "ck3_title_tree.json"
CANONICAL_HERALDRY_PATH = REPO_ROOT / "data" / "canonical_title_heraldry.json"
SINOSPHERE_PATH = REPO_ROOT / "data" / "sinosphere_hanzi_calques.json"
OUTPUT_PATH = REPO_ROOT / "data" / "title_symbol_adoption.json"

# =========================================================================
# 1. Historical Patron Saints & Sacred Heraldic Traditions
# =========================================================================
PATRON_SAINTS = {
    # Italy & Papacy
    'c_roma': 'Saint Peter and Saint Paul (Apostolic See)',
    'd_latium': 'Saint Peter and Saint Paul',
    'k_papal_state': 'Saint Peter and Saint Paul',
    'c_venezia': 'Saint Mark the Evangelist',
    'd_venice': 'Saint Mark the Evangelist',
    'c_milano': 'Saint Ambrose of Milan',
    'd_lombardy': 'Saint Ambrose of Milan',
    'c_ravenna': 'Saint Apollinaris of Ravenna',
    'd_ravenna': 'Saint Apollinaris of Ravenna',
    'c_napoli': 'Saint Januarius (San Gennaro)',
    'c_palermo': 'Saint Rosalia and Saint Agatha',
    'd_sicily': 'Saint Rosalia and Saint Agatha',
    'c_firenze': 'Saint John the Baptist',
    'c_genova': 'Saint George and Saint Lawrence',
    'c_pisa': 'Saint Rainerius of Pisa',
    'c_siena': 'Saint Catherine of Siena and Saint Ansano',
    'c_verona': 'Saint Zeno of Verona',
    'c_padova': 'Saint Anthony of Padua and Saint Justina',
    'c_bologna': 'Saint Petronius of Bologna',
    'c_ferrara': 'Saint George',
    'c_modena': 'Saint Geminianus',
    'c_parma': 'Saint Vitalis and Saint John the Baptist',
    'c_aquileia': 'Saint Mark and Saint Hermagoras',

    # Eastern Roman Empire & Levant
    'c_byzantion': 'Saint Andrew the First-Called and Saint Constantine',
    'e_byzantium': 'Saint Andrew the First-Called and Saint Constantine',
    'c_thessaloniki': 'Saint Demetrius of Thessalonica',
    'd_thessalonika': 'Saint Demetrius of Thessalonica',
    'c_athens': 'Saint Dionysius the Areopagite',
    'd_athens': 'Saint Dionysius the Areopagite',
    'c_antioch': 'Saint Peter and Saint Ignatius of Antioch',
    'd_antioch': 'Saint Peter and Saint Ignatius of Antioch',
    'c_alexandria': 'Saint Mark the Evangelist',
    'd_alexandria': 'Saint Mark the Evangelist',
    'c_jerusalem': 'Holy Sepulchre and Saint James the Brother of the Lord',

    # Gaul & Frankish / German Realm
    'c_ile_de_france': 'Saint Denis and Saint Genevieve',
    'c_paris': 'Saint Denis and Saint Genevieve',
    'c_aachen': 'Saint Mary of Charlemagne',
    'c_cologne': 'The Three Holy Kings (Magi) and Saint Peter',
    'c_mainz': 'Saint Martin of Tours and Saint Boniface',
    'c_trier': 'Saint Peter and Saint Eucharius',
    'c_metz': 'Saint Stephen (Cathédrale Saint-Étienne) and Saint Arnual',
    'd_upper_lorraine': 'Saint Stephen and Saint Arnual (Chatenois Cradle)',
    'c_strasbourg': 'Saint Mary of Strasbourg and Saint Arbogast',
    'c_basel': 'Saint Henry and Saint Cunigunde',
    'c_geneva': 'Saint Peter',
    'c_zurich': 'Saints Felix and Regula',
    'c_marseille': 'Saint Victor and Saint Lazarus',
    'c_lyon': 'Saint Pothinus and Saint Irenaeus',
    'c_tours': 'Saint Martin of Tours',
    'c_reims': 'Saint Remigius of Reims',
    'c_rouen': 'Saint Romanus of Rouen',
    'c_toulouse': 'Saint Saturnin (Sernin)',
    'c_bourges': 'Saint Ursinus',
    'c_bordeaux': 'Saint Andrew',
    'c_avignon': 'Saint Bénézet and Saint Agricol',
    'c_arles': 'Saint Trophimus',
    'c_dijon': 'Saint Benignus',
    'c_besancon': 'Saints Ferréol and Ferjeux',
    'c_utrecht': 'Saint Willibrord',
    'c_liege': 'Saint Lambert of Maastricht',
    'c_bremen': 'Saint Ansgar of Hamburg-Bremen',
    'c_hildesheim': 'Saint Bernward and Saint Godehard',
    'c_magdeburg': 'Saint Maurice',
    'c_bamberg': 'Saint Henry and Saint Cunigunde',
    'c_wurzburg': 'Saint Kilian',
    'c_regensburg': 'Saint Emmeram and Saint Erhard',
    'c_salzburg': 'Saint Rupert and Saint Virgil',
    'c_passau': 'Saint Stephen and Saint Valentine',
    'c_augsburg': 'Saint Ulrich and Saint Afra',
    'c_speyer': 'Saint Mary of Speyer',
    'c_worms': 'Saint Peter',

    # Iberia & Tarraconensis
    'c_tarragona': 'Saint Fructuosus and Saint Thecla of Iconium',
    'c_barcelona': 'Saint Eulalia of Barcelona and Saint George (Sant Jordi)',
    'd_barcelona': 'Saint George (Sant Jordi) and Saint Eulalia',
    'c_santiago': 'Saint James the Greater (Santiago de Compostela)',
    'd_galicia': 'Saint James the Greater',
    'c_toledo': 'Saint Ildefonsus and Saint Leocadia',
    'c_seville': 'Saint Isidore of Seville',
    'c_valencia': 'Saint Vincent the Martyr',
    'c_zaragoza': 'Saint Vincent the Martyr and Our Lady of the Pillar',

    # Britain & Ireland
    'c_middlesex': 'Saint Paul the Apostle (St. Paul Cathedral 604 AD)',
    'c_london': 'Saint Paul the Apostle',
    'c_kent': 'Saint Augustine of Canterbury and Saint Thomas Becket',
    'd_canterbury': 'Saint Augustine of Canterbury',
    'c_york': 'Saint Peter and Saint Wilfrid',
    'c_wiltshire': 'Saint Aldhelm and Saint Swithun',
    'd_wessex': 'Saint Aldhelm and Saint Swithun',
    'c_durham': 'Saint Cuthbert of Lindisfarne',
    'c_lincoln': 'Saint Hugh of Lincoln',
    'c_winchester': 'Saint Swithun',
    'c_norwich': 'Saint William of Norwich and Saint Felix',
    'c_dublin': 'Saint Patrick and Saint Kevin',
    'c_edinburg': 'Saint Andrew and Saint Margaret of Scotland',
    'd_lothian': 'Saint Margaret and Saint Andrew',

    # Central & Eastern Europe
    'c_szekesfehervar': 'Saint Stephen of Hungary (Szent István)',
    'c_esztergom': 'Saint Adalbert of Prague',
    'c_prague': 'Saint Wenceslaus and Saint Vitus',
    'd_bohemia': 'Saint Wenceslaus',
    'c_krakow': 'Saint Stanislaus of Szczepanów and Saint Florian',
    'c_gniezno': 'Saint Adalbert of Prague',
    'c_kyiv': 'Saint Michael the Archangel and Saint Andrew',
    'c_novgorod': 'Saint Sophia (Holy Wisdom)',
    'c_smolensk': 'Saint Abraham of Smolensk',
    'c_polotsk': 'Saint Euphrosyne of Polotsk'
}

# Pre-867 historical foundation updates with iconic dates
ICONIC_FOUNDATIONS = {
    'c_roma': (754, "Apostolic tradition & Donation of Pepin (754 AD); confirmed upon Imperial protection in 981 AD"),
    'c_aachen': (800, "Charlemagne's Palatine Reichsadler (800 AD); confirmed upon Carolingian accession in 912 AD"),
    'c_venezia': (828, "Winged Lion of Saint Mark adopted 828 AD upon translation of relics; confirmed 1014 AD"),
    'c_milano': (568, "Iron Crown of Lombardy (Corona Ferrea, 6th c.); confirmed in 981 AD"),
    'c_paris': (752, "Ancient galley of the Nautae Parisiaci (Lutetia); Frankish royal confirmation 752 AD"),
    'c_ile_de_france': (752, "Ancient galley of the Nautae Parisiaci (Lutetia); Frankish royal confirmation 752 AD"),
    'c_byzantion': (330, "Constantinian foundation 330 AD & Tetragrammatic cross; reunited into Roman Empire 1103 AD"),
    'c_antioch': (34, "Apostolic Patriarchate of Antioch (34 AD); recovered in 1136 AD"),
    'c_alexandria': (43, "Apostolic Patriarchate of Saint Mark (43 AD); integrated in 1136 AD"),
    'c_jerusalem': (335, "Holy Sepulchre of Constantine (335 AD); recovered under imperial protection"),
    'c_middlesex': (604, "Sword of Saint Paul (St. Paul's See founded 604 AD); confirmed under imperial rule 1064 AD"),
    'c_kent': (449, "White Horse of Kent (Hengist & Horsa 449 AD); confirmed 1068 AD"),
    'c_wiltshire': (752, "Golden Dragon of Wessex (Battle of Burford 752 AD); confirmed 1068 AD"),
    'c_york': (867, "Raven Banner of the Great Heathen Army (Hrafnsmerki 867 AD); confirmed 1068 AD"),
    'c_kyiv': (860, "Rus' Princely Falcon / Trident Tamga of Askold & Dir (860 AD); confirmed 1028 AD"),
    'c_athens': (508, "Classical Roman Theme of Hellas & Parthenon column; restored 1103 AD"),
    'c_thessaloniki': (867, "Saint Demetrius crossed swords of the Byzantine Theme of Thessalonica; restored 1103 AD"),
    'c_tarragona': (1016, "Hispania Tarraconensis Roman capital; adopted 1016 AD as Tarraconian cultural homeland"),
    'c_metz': (864, "Imperial Chancellery Seat; Chatenois dynastic cradle adopted 864 AD")
}

# =========================================================================
# 2. Campaign Eras Classification
# =========================================================================
def get_campaign_era(year: int) -> str:
    if year is None:
        return "Exterior Autonomous March (1194+)"
    if year < 867:
        return "Classical & Pre-867 Antiquity"
    elif year <= 988:
        return "Carolingian & Lothringian Cradle (867–988)"
    elif year <= 1052:
        return "Tarraconian Ethnogenesis (989–1052)"
    elif year <= 1071:
        return "First Imperial Restoration (1053–1071)"
    elif year <= 1142:
        return "High Imperial Consolidation (1072–1142)"
    elif year <= 1194:
        return "Universal Roman Hegemony (1143–1194)"
    else:
        return "Exterior Autonomous March (1194+)"

# =========================================================================
# 3. Option C Conqueror Trait Archetype Analyzer
# =========================================================================
def analyze_conqueror_archetype(traits: list) -> str:
    if not traits:
        return "Administrative Magistracy"
    t_set = set(traits)
    scores = {
        'The Pragmatic March-Warden': sum(1 for t in t_set if t in (
            'diligent', 'architect', 'brave', 'craven', 'paranoid',
            'military_engineer', 'unyielding_defender', 'strategist'
        )),
        'The Eponymous Megalomaniac': sum(1 for t in t_set if t in (
            'arrogant', 'ambitious', 'greedy', 'fickle', 'wrathful'
        )),
        'The Pious Foundation': sum(1 for t in t_set if t in (
            'zealous', 'humble', 'theologian', 'monk', 'chaste', 'saint', 'pilgrim'
        )),
        'The Classical Antiquarian': sum(1 for t in t_set if t in (
            'scholar', 'philosopher', 'erudite', 'antiquarian', 'lifestyle_scholar'
        )),
        'The Dynastic Patriarch': sum(1 for t in t_set if t in (
            'family_first', 'diplomacy', 'gregarious', 'honest', 'just'
        ))
    }
    top_archetype, top_score = max(scores.items(), key=lambda x: x[1])
    return top_archetype if top_score > 0 else "Administrative Magistracy"

# =========================================================================
# 4. Main Generation Pipeline
# =========================================================================
def main():
    print(f"Generating Title Symbol Adoption Registry from:")
    print(f"  - Trajectories: {TRAJECTORIES_PATH}")
    print(f"  - Title Tree:   {TITLE_TREE_PATH}")

    # 1. Load Trajectories
    trajectories = {}
    if TRAJECTORIES_PATH.exists():
        with open(TRAJECTORIES_PATH, "r", encoding="utf-8") as f:
            for t in json.load(f):
                trajectories[t["county_key"]] = t
    print(f"Loaded {len(trajectories)} county trajectories.")

    # 2. Load Title Tree
    with open(TITLE_TREE_PATH, "r", encoding="utf-8") as f:
        title_tree = json.load(f)

    # 3. Load Sinosphere Calques
    sino_keys = set()
    if SINOSPHERE_PATH.exists():
        with open(SINOSPHERE_PATH, "r", encoding="utf-8") as f:
            sino_keys = set(json.load(f).keys())

    # 4. Load Canonical Heraldry keys
    canon_keys = set()
    if CANONICAL_HERALDRY_PATH.exists():
        with open(CANONICAL_HERALDRY_PATH, "r", encoding="utf-8") as f:
            canon_keys = set(json.load(f).keys())

    adoption_db = {}

    # Track higher tier constituent dates
    duchy_constituent_years = {}
    kingdom_constituent_years = {}
    empire_constituent_years = {}

    # 5. Process all counties
    for e_k, e_val in title_tree.items():
        for k_k, k_val in e_val.get("kingdoms", {}).items():
            for d_k, d_val in k_val.get("duchies", {}).items():
                for c_k, c_val in d_val.get("counties", {}).items():
                    t = trajectories.get(c_k)
                    st = t.get("sovereign_trajectory", {}) if t else {}
                    att = t.get("attestation", {}) if t else {}
                    cls = t.get("classification", {}) if t else {}
                    is_roman = t.get("is_in_roman_empire", False) if t else False

                    first_roman_date = st.get("first_roman_entry_date")
                    first_roman_holder = st.get("first_roman_holder")
                    conq = st.get("first_conqueror_after_867")
                    traits = st.get("conqueror_traits", [])

                    att_yr = att.get("year")
                    att_ev = att.get("evidence")
                    att_notes = att.get("notes") or ""

                    # Check iconic foundations
                    iconic = ICONIC_FOUNDATIONS.get(c_k)
                    saint = PATRON_SAINTS.get(c_k)

                    # Auto-detect saint from county name if not explicit
                    c_name = c_val.get("tarr") or c_val.get("origin") or c_k
                    if not saint:
                        m_saint = re.search(r"\b(?:Zant[- ]([A-Z][a-z]+)|Saint[- ]([A-Z][a-z]+)|St\.[- ]([A-Z][a-z]+)|San[- ]([A-Z][a-z]+)|Santa[- ]([A-Z][a-z]+))\b", c_name, re.I)
                        if m_saint:
                            s_name = next(g for g in m_saint.groups() if g)
                            saint = f"Saint {s_name}"

                    archetype = analyze_conqueror_archetype(traits)
                    is_sino = (c_k in sino_keys) or c_k.startswith(('c_chi_', 'c_jap_', 'c_kor_')) or (c_k == 'c_jinzhou')

                    if first_roman_date:
                        try:
                            roman_year = int(first_roman_date.split(".")[0])
                        except ValueError:
                            roman_year = 1059
                    elif is_sino:
                        # Procedure 1 Sinosphere counties established in 1154 Hegemony
                        roman_year = 1154
                    else:
                        roman_year = None

                    # Record constituent years for parent tiers
                    if roman_year is not None:
                        duchy_constituent_years.setdefault(d_k, []).append(roman_year)
                        kingdom_constituent_years.setdefault(k_k, []).append(roman_year)
                        empire_constituent_years.setdefault(e_k, []).append(roman_year)

                    # Determine estimated adoption year & display
                    if iconic:
                        adopted_year = iconic[0]
                        if roman_year and roman_year != adopted_year:
                            year_disp = f"c. {adopted_year} AD ({roman_year} AD)"
                        else:
                            year_disp = f"{adopted_year} AD"
                        era = get_campaign_era(adopted_year)
                        rationale = f"{iconic[1]}."
                    elif is_sino and (first_roman_date is None or roman_year == 1154):
                        adopted_year = 1154
                        year_disp = "1154 AD"
                        era = "Universal Roman Hegemony (1143–1194)"
                        rationale = "Procedure 1 Sinitic Magistracy: Invested with the Vermilion Cinnabar Chop (Guóxī) in 1154 AD upon the establishment of the imperial East Asian prefecture under Augustus Wernhard."
                    elif roman_year is not None:
                        if att_yr is not None and att_yr > 0 and att_yr < 867:
                            adopted_year = att_yr
                            year_disp = f"c. {att_yr} AD ({roman_year} AD)"
                            era = get_campaign_era(att_yr)
                            rationale = f"Ancient civic attestation dating to c. {att_yr} AD; formally adopted into the imperial administration in {roman_year} AD"
                        elif att_yr is not None and att_yr < 0:
                            adopted_year = roman_year
                            year_disp = f"{roman_year} AD (Antiquity: {abs(att_yr)} BC)"
                            era = get_campaign_era(roman_year)
                            rationale = f"Classical foundation dating to {abs(att_yr)} BC ({att.get('source', 'Antiquity')}); integrated into the imperial administration in {roman_year} AD"
                        else:
                            adopted_year = roman_year
                            year_disp = f"{roman_year} AD"
                            era = get_campaign_era(roman_year)
                            rationale = f"Adopted in {roman_year} AD upon incorporation into the Roman administrative apparatus"

                        if first_roman_holder:
                            rationale += f" under Governor {first_roman_holder}"
                        rationale += f". Formulated under the {archetype} tradition."
                        if saint:
                            rationale += f" Dedicated under the holy patronage of {saint}."
                    else:
                        adopted_year = None
                        year_disp = "Provisional (1194+)"
                        era = "Exterior Autonomous March (1194+)"
                        rationale = "Autonomous territory beyond the 1194 imperial frontier; provisional insignia assigned by the chancellery for diplomatic and cartographic registry."

                    adoption_db[c_k] = {
                        "tier": "county",
                        "year": adopted_year,
                        "romanYear": roman_year,
                        "yearDisplay": year_disp,
                        "era": era,
                        "holder": first_roman_holder,
                        "saint": saint,
                        "archetype": archetype,
                        "historicalBasis": att_notes or (iconic[1] if iconic else ""),
                        "rationale": rationale
                    }

                    # Baronies with canonical COA or explicit saint
                    for b_k in c_val.get("baronies", []):
                        if b_k in canon_keys or (saint and "Saint" in b_k):
                            b_saint = saint
                            b_name = b_k.replace("b_", "").replace("_", " ").title()
                            if "Saint" in b_name or "St " in b_name:
                                b_saint = b_name
                            adoption_db[b_k] = {
                                "tier": "barony",
                                "county": c_k,
                                "year": adopted_year,
                                "romanYear": roman_year,
                                "yearDisplay": year_disp,
                                "era": era,
                                "saint": b_saint,
                                "archetype": archetype,
                                "rationale": f"Civic holding badge (Herren-Wâpen) established in {year_disp} under jurisdiction of Magistrat {c_val.get('tarr', c_k)}."
                            }

    # 6. Process Duchies
    for e_k, e_val in title_tree.items():
        for k_k, k_val in e_val.get("kingdoms", {}).items():
            for d_k, d_val in k_val.get("duchies", {}).items():
                iconic = ICONIC_FOUNDATIONS.get(d_k)
                saint = PATRON_SAINTS.get(d_k)
                c_years = duchy_constituent_years.get(d_k, [])
                min_yr = min(c_years) if c_years else None

                if iconic:
                    d_year = iconic[0]
                    d_disp = f"c. {d_year} AD"
                    era = get_campaign_era(d_year)
                    rationale = f"Gubernats-Heerschilt (Notitia Command Shield): {iconic[1]}."
                elif min_yr is not None:
                    d_year = min_yr
                    d_disp = f"c. {d_year} AD"
                    era = get_campaign_era(d_year)
                    rationale = f"Gubernats-Heerschilt (Notitia Command Shield) codified in {d_year} AD upon the establishment of imperial governorship over the constituent magistracies."
                else:
                    d_year = None
                    d_disp = "Provisional (1194+)"
                    era = "Exterior Autonomous March (1194+)"
                    rationale = "Autonomous ducal jurisdiction beyond the 1194 imperial limes; provisional command shield assigned for frontier registry."

                if saint:
                    rationale += f" Governed under the ecclesiastical protection of {saint}."

                adoption_db[d_k] = {
                    "tier": "duchy",
                    "year": d_year,
                    "yearDisplay": d_disp,
                    "era": era,
                    "saint": saint,
                    "rationale": rationale
                }

    # 7. Process Kingdoms
    for e_k, e_val in title_tree.items():
        for k_k, k_val in e_val.get("kingdoms", {}).items():
            iconic = ICONIC_FOUNDATIONS.get(k_k)
            saint = PATRON_SAINTS.get(k_k)
            c_years = kingdom_constituent_years.get(k_k, [])
            min_yr = min(c_years) if c_years else None

            if iconic:
                k_year = iconic[0]
                k_disp = f"c. {k_year} AD"
                era = get_campaign_era(k_year)
                rationale = f"Three-Tailed Gonfanon (Amtsvanen): {iconic[1]}."
            elif min_yr is not None:
                k_year = min_yr
                k_disp = f"c. {k_year} AD"
                era = get_campaign_era(k_year)
                rationale = f"Three-Tailed Gonfanon (Amtsvanen) instituted in {k_year} AD upon regency integration (Regenat) within the imperial realm."
            else:
                k_year = None
                k_disp = "Provisional (1194+)"
                era = "Exterior Autonomous March (1194+)"
                rationale = "External sovereign kingdom; provisional regency gonfanon assigned for diplomatic registry."

            if saint:
                rationale += f" Held under the sacred patronage of {saint}."

            adoption_db[k_k] = {
                "tier": "kingdom",
                "year": k_year,
                "yearDisplay": k_disp,
                "era": era,
                "saint": saint,
                "rationale": rationale
            }

    # 8. Process Empires & Hegemony
    for e_k, e_val in title_tree.items():
        c_years = empire_constituent_years.get(e_k, [])
        min_yr = min(c_years) if c_years else None
        saint = PATRON_SAINTS.get(e_k)

        if e_k in ('e_zhongyuan', 'e_liangyi', 'e_jingyang'):
            e_year = 1154
            e_disp = "1154 AD"
            era = "Universal Roman Hegemony (1143–1194)"
            rationale = "Imperial Vexillum established in 1154 AD upon the proclamation of Roman Hegemony over East Asian provinces under Augustus Wernhard."
        elif min_yr is not None:
            e_year = min_yr
            e_disp = f"c. {e_year} AD"
            era = get_campaign_era(e_year)
            rationale = f"Imperial Vexillum (silk banner on crossbar) instituted in {e_year} AD upon imperial accession and administrative sovereignty."
        else:
            e_year = None
            e_disp = "Provisional (1194+)"
            era = "Exterior Autonomous March (1194+)"
            rationale = "Foreign imperial jurisdiction; provisional vexillum standard for diplomatic armorial."

        if saint:
            rationale += f" Blessed under the imperial patronage of {saint}."

        adoption_db[e_k] = {
            "tier": "empire",
            "year": e_year,
            "yearDisplay": e_disp,
            "era": era,
            "saint": saint,
            "rationale": rationale
        }

    # Special Hegemony & Holy Roman Empire additions
    adoption_db['h_roman_empire'] = {
        "tier": "empire",
        "year": 1053,
        "yearDisplay": "1053 / 1154 AD",
        "era": "Universal Roman Hegemony (1143–1194)",
        "saint": "Saint Peter and Saint Paul (Apostolic Rome)",
        "rationale": "Supreme Imperial Vexillum of Dat Rômische Keiserrîch: Restored from the Holy Roman Empire (1053 AD, Kaiser Adémar 'the Great') and Byzantine Empire, culminating in the Proclamation of Universal Hegemony (1154 AD, Augustus Wernhard 'the Bear')."
    }

    adoption_db['e_hre'] = {
        "tier": "empire",
        "year": 800,
        "yearDisplay": "800 / 1053 AD",
        "era": "Classical & Pre-867 Antiquity",
        "saint": "Charlemagne and Saint Peter",
        "rationale": "Imperial Reichsadler standard: First established on Christmas Day 800 AD by Charlemagne; restored to Chatenois dynastic leadership in 1053 AD."
    }

    # 9. Write Output
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(adoption_db, f, indent=2, ensure_ascii=False)

    print(f"Successfully generated {OUTPUT_PATH} ({len(adoption_db)} titles, {OUTPUT_PATH.stat().st_size / 1024 / 1024:.2f} MB)")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Procedure 2 Audit Engine: Sovereign Cultural Lineage & Etymological Transparency Protocol
------------------------------------------------------------------------------------------
Part of the Tarraconian Imperial Chancellery Audit Pipeline.

Implements Procedure 2 from README.md (§ 3.2) and tarraconian_descriptive_title_calques.md (§ 5.2):
  - Evaluates candidate descriptive toponyms against pre-conquest sovereign lineages and population culture.
  - Distinguishes living etymologies suitable for semantic calquing from opaque phonetic tokens.
  - Classifies titles into the Three Continuity Tiers:
      * Tier 1 (High Living Continuity): Preferred Semantic Calque (Pattern 1)
      * Tier 2 (Transitional Dynastic Rule): Hybrid Calque Allowed (Pattern 2)
      * Tier 3 (Complete Semantic Rupture): Strict Phonetic Nativization (Pattern 3)
  - Enforces Rule 3 (Restraint with Opaque Eponyms & Ancient Stems): Calquing Prohibited.

Outputs:
  - JSON database of evaluated titles
  - Comprehensive Markdown Audit Register
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path


def log(msg: str):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


# ==============================================================================
# 1. CULTURE GROUPS, HERITAGES & LANGUAGE FAMILIES LOOKUP
# ==============================================================================

# Mapping from standardized linguistic / cultural groups to CK3 heritages, languages, and cultures
CULTURE_GROUP_SPECS = {
    "Hungarian": {
        "heritages": {"heritage_magyar"},
        "languages": {"language_magyar"},
        "cultures": {"mogyer", "hungarian", "Ungwârer"},
    },
    "West Slavic": {
        "heritages": {"heritage_west_slavic"},
        "languages": {"language_czech_slovak", "language_lechitic"},
        "cultures": {"slovien", "czech", "polish", "polabian", "pomeranian", "slovak", "sorbian"},
    },
    "South Slavic": {
        "heritages": {"heritage_south_slavic"},
        "languages": {"language_south_slavic", "language_slavonic"},
        "cultures": {"serbian", "croatian", "bosnian", "bulgarian", "carantanian", "Croato-Tarraconian"},
    },
    "East Slavic": {
        "heritages": {"heritage_east_slavic"},
        "languages": {"language_east_slavic"},
        "cultures": {"russian", "ruthenian", "ilmenian", "severian", "volhynian", "krivich", "Russo-Lithuanian"},
    },
    "Slavic": {  # Broad Slavic umbrella
        "heritages": {"heritage_west_slavic", "heritage_south_slavic", "heritage_east_slavic"},
        "languages": {"language_czech_slovak", "language_lechitic", "language_south_slavic", "language_slavonic", "language_east_slavic"},
        "cultures": {"slovien", "czech", "polish", "polabian", "pomeranian", "slovak", "serbian", "croatian", "bosnian", "bulgarian", "carantanian", "russian", "ruthenian", "ilmenian", "severian", "volhynian", "krivich"},
    },
    "Arabic / Berber": {
        "heritages": {"heritage_arabic", "heritage_berber", "heritage_iberian"},
        "languages": {"language_arabic", "language_berber"},
        "cultures": {"andalusian", "bedouin", "levantine", "yemeni", "egyptian", "maghrebi", "butr", "baranis", "Qalat Ayyub"},
    },
    "Greek / Byzantine": {
        "heritages": {"heritage_byzantine", "heritage_ancient_greek"},
        "languages": {"language_greek"},
        "cultures": {"greek", "pontic", "cappadocian", "cypriot", "cretan"},
    },
    "Romance / Latin": {
        "heritages": {"heritage_latin", "heritage_frankish", "heritage_iberian", "heritage_vlach"},
        "languages": {"language_latin", "language_french", "language_occitan", "language_catalan", "language_castilian", "language_italian", "language_vlach"},
        "cultures": {"latin", "roman", "italian", "cisalpine", "lombard", "sicilian", "french", "occitan", "catalan", "castilian", "galician", "portuguese", "vlach", "Franco-Lothringian"},
    },
    "Celtic": {
        "heritages": {"heritage_goidelic", "heritage_brythonic"},
        "languages": {"language_goidelic", "language_brythonic"},
        "cultures": {"irish", "gaelic", "welsh", "breton", "cornish", "cumbrian", "pictish"},
    },
    "Germanic / Norse": {
        "heritages": {"heritage_north_germanic", "heritage_central_germanic", "heritage_west_germanic"},
        "languages": {"language_north_germanic", "language_high_german", "language_west_germanic"},
        "cultures": {"norse", "norwegian", "swedish", "danish", "geatish", "guter", "anglo_saxon", "saxon", "franconian", "bavarian", "swabian", "dutch", "frisian", "Lothringian", "Tarraconian"},
    },
    "Finnic / Uralic": {
        "heritages": {"heritage_balto_finnic", "heritage_volga_finnic", "heritage_ugro_permian"},
        "languages": {"language_balto_finnic", "language_volga_finnic", "language_ugro_permian"},
        "cultures": {"finnish", "karelian", "vepsian", "estonian", "sami", "mordvin", "mari", "komi", "khanty"},
    },
    "Turkic / Oghur": {
        "heritages": {"heritage_turkic", "heritage_hunnic"},
        "languages": {"language_turkic"},
        "cultures": {"turkic", "cuman", "pecheneg", "khazar", "bolghar", "avar", "karluk", "chuvash", "kipchak", "turkish", "bashkir", "tatar", "shatuo"},
    },
    "Iranian / Persian": {
        "heritages": {"heritage_iranian"},
        "languages": {"language_iranian"},
        "cultures": {"persian", "tajik", "sogdian", "khwarezmian", "daylamite", "kurdish", "baloch", "alan", "saka"},
    },
    "Sinospheric": {
        "heritages": {"heritage_chinese", "heritage_korean", "heritage_japonic", "heritage_viet", "heritage_tungusic"},
        "languages": {"language_chinese", "language_korean", "language_japonic", "language_viet", "language_tungusic"},
        "cultures": {"han", "silla", "goguryeo", "baekje", "Samhan", "korean", "japanese", "yamato", "khitan", "jurchen", "mohe", "vietnamese", "viet", "Zhenwu", "Yukju"},
    },
    "Tibetan": {
        "heritages": {"heritage_tibetan"},
        "languages": {"language_tibetan"},
        "cultures": {"bodpa", "zhangzhung", "lhomon", "sumpa", "tsangpa"},
    },
    "Ethiopic / Cushitic": {
        "heritages": {"heritage_east_african", "heritage_ethiopic", "heritage_cushitic", "heritage_somalian"},
        "languages": {"language_ethiopic", "language_cushitic", "language_somalian"},
        "cultures": {"amhara", "ethiopian", "geez", "nubian", "daju", "somali", "afar", "beja"},
    },
    "Indo-Aryan": {
        "heritages": {"heritage_indo_aryan"},
        "languages": {"language_indo_aryan"},
        "cultures": {"sindhi", "gujarati", "hindustani", "kashmiri", "punjabi", "bengali", "marathi"},
    },
    "Baltic": {
        "heritages": {"heritage_baltic"},
        "languages": {"language_baltic"},
        "cultures": {"lithuanian", "prussian", "latgalian", "samogitian", "jatvingian"},
    },
}


def matches_culture_group(culture_name: str, group_key: str, cultures_db: dict) -> bool:
    """
    Checks whether a culture name matches an etymological culture group specification.
    """
    if not culture_name or group_key not in CULTURE_GROUP_SPECS:
        return False

    spec = CULTURE_GROUP_SPECS[group_key]
    c_lower = culture_name.lower()

    # Direct culture name check
    for c in spec["cultures"]:
        if c.lower() == c_lower:
            return True

    # Check via cultures_db metadata (heritage / language)
    c_data = None
    for item in cultures_db.values():
        if item.get("name", "").lower() == c_lower:
            c_data = item
            break

    if c_data:
        heritage = c_data.get("heritage", "")
        language = c_data.get("language", "")
        if heritage in spec["heritages"]:
            return True
        if language in spec["languages"]:
            return True
        for p in c_data.get("parents", []):
            if str(p).lower() in [x.lower() for x in spec["cultures"]]:
                return True

    return False


# ==============================================================================
# 2. MASTER CANDIDATE TITLES DATABASE
# ==============================================================================

# Compiled candidate titles across the 14 regional matrices from tarraconian_descriptive_title_calques.md,
# plus Sinospheric Roman titles and control opaque eponyms.
CANDIDATE_TITLES = [
    # --------------------------------------------------------------------------
    # 4.1 Carpathian Basin, Upper Hungary & Banat (k_hungary)
    # --------------------------------------------------------------------------
    {
        "canonical_key": "c_szekesfehervar",
        "mapped_ck3_key": "c_szekesfehervar",
        "name": "Székesfehérvár",
        "proposed_calque": "Magistrat van Stûlwîtzenburch",
        "etym_group": "Hungarian",
        "etym_breakdown": "szék ('throne/chair') + fehér ('white') + vár ('castle') -> 'White Castle of the Throne'",
        "region": "4.1 Carpathian Basin",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_vas",
        "mapped_ck3_key": "c_vas",
        "name": "Dudleb / Vasvár",
        "proposed_calque": "Magistrat van Îsenburch",
        "etym_group": "Hungarian",
        "etym_breakdown": "vas ('iron') + vár ('castle') -> 'Iron Castle' on the Rába",
        "region": "4.1 Carpathian Basin",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_csongrad",
        "mapped_ck3_key": "c_csongrad",
        "name": "Csongrád",
        "proposed_calque": "Magistrat van Swartzenburch",
        "etym_group": "South Slavic",
        "etym_breakdown": "Slavic substrate *Črnograd ('Black Gord/Castle')",
        "region": "4.1 Carpathian Basin",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_abauj",
        "mapped_ck3_key": "c_abauj",
        "name": "Abaúj",
        "proposed_calque": "Magistrat van Abanîeburch",
        "etym_group": "Hungarian",
        "etym_breakdown": "King Samuel Aba's fortress at Abaújvár ('Aba's New Castle')",
        "region": "4.1 Carpathian Basin",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_spis",
        "mapped_ck3_key": "c_spis",
        "name": "Szepesség / Spiš",
        "proposed_calque": "Magistrat van der Zips",
        "etym_group": "West Slavic",
        "etym_breakdown": "Historical German Zips; pre-1059 Gord at Čingov (Tschingouwe)",
        "region": "4.1 Carpathian Basin",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_marmaros",
        "mapped_ck3_key": "c_marmaros",
        "name": "Marmaros / Solotvyno",
        "proposed_calque": "Magistrat van Salzstat-am-Teiß",
        "etym_group": "East Slavic",
        "etym_breakdown": "Solotvyno from Slavic sol ('salt') -> 'Salt Town on the Tisza'",
        "region": "4.1 Carpathian Basin",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_bekes",
        "mapped_ck3_key": "c_bekes",
        "name": "Békés",
        "proposed_calque": "Magistrat van Fridstat",
        "etym_group": "Hungarian",
        "etym_breakdown": "Hungarian békés ('peaceful / peace-guard') or Ispán Beke -> 'Peace Town'",
        "region": "4.1 Carpathian Basin",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_temes",
        "mapped_ck3_key": "c_temes",
        "name": "Temes",
        "proposed_calque": "Magistrat van Temeschburch",
        "etym_group": "Hungarian",
        "etym_breakdown": "Hydronym Temes + Hungarian vár ('castle') -> German Temeschburg",
        "region": "4.1 Carpathian Basin",
        "is_opaque_eponym": False,
    },

    # --------------------------------------------------------------------------
    # 4.2 West & South Slavic Realms (k_poland, k_bohemia, k_croatia, k_serbia)
    # --------------------------------------------------------------------------
    {
        "canonical_key": "c_cetatea_alba",
        "mapped_ck3_key": "c_cetatea_alba",
        "name": "Cetatea Albă / Bilhorod",
        "proposed_calque": "Magistrat van Wîtzenburch-am-Nister",
        "etym_group": "Slavic",
        "etym_breakdown": "Belgorod / Cetatea Albă ('White Castle on the Dniester')",
        "region": "4.2 West & South Slavic",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_vyshhorod",
        "mapped_ck3_key": "c_kiev",
        "name": "Vyshhorod",
        "proposed_calque": "Magistrat van Hôchburch",
        "etym_group": "East Slavic",
        "etym_breakdown": "Slavic vyše ('higher/above') + gorod ('citadel/gord') -> 'High Castle'",
        "region": "4.2 West & South Slavic",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_novgorod",
        "mapped_ck3_key": "c_novgorod",
        "name": "Novgorod",
        "proposed_calque": "Magistrat van Nîenburch",
        "etym_group": "East Slavic",
        "etym_breakdown": "Slavic novy ('new') + gorod ('city/gord') -> 'New Castle / New City'",
        "region": "4.2 West & South Slavic",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_beloozero",
        "mapped_ck3_key": "c_beloozero",
        "name": "Beloozero",
        "proposed_calque": "Magistrat van Wîtzensê",
        "etym_group": "East Slavic",
        "etym_breakdown": "Slavic bely ('white') + ozero ('lake') -> 'White Lake'",
        "region": "4.2 West & South Slavic",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_zelengora",
        "mapped_ck3_key": "c_zelengora",
        "name": "Zelengora",
        "proposed_calque": "Magistrat van Grûnenberch",
        "etym_group": "South Slavic",
        "etym_breakdown": "South Slavic zelena ('green') + gora ('mountain') -> 'Green Mountain'",
        "region": "4.2 West & South Slavic",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_zlatibor",
        "mapped_ck3_key": "c_zlatibor",
        "name": "Zlatibor",
        "proposed_calque": "Magistrat van Goltwalt",
        "etym_group": "South Slavic",
        "etym_breakdown": "South Slavic zlati ('golden') + bor ('pine forest') -> 'Golden Forest'",
        "region": "4.2 West & South Slavic",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_soli",
        "mapped_ck3_key": "c_soli",
        "name": "Soli (Tuzla)",
        "proposed_calque": "Magistrat van Saltzvelt",
        "etym_group": "South Slavic",
        "etym_breakdown": "Slavic plural soli ('salt pans / salt mines') -> 'Salt Field'",
        "region": "4.2 West & South Slavic",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_podrinje",
        "mapped_ck3_key": "c_podrinje",
        "name": "Podrinje",
        "proposed_calque": "Magistrat van Drînedal",
        "etym_group": "South Slavic",
        "etym_breakdown": "Prepositional hydronym Po- ('along') + Drina -> 'Drina Valley'",
        "region": "4.2 West & South Slavic",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_pomorje",
        "mapped_ck3_key": "c_pomorje",
        "name": "Pomorje (Zeta coast)",
        "proposed_calque": "Magistrat van Sêmarch",
        "etym_group": "South Slavic",
        "etym_breakdown": "Slavic Po-morje ('along the sea / maritime littoral')",
        "region": "4.2 West & South Slavic",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_mostar",
        "mapped_ck3_key": "c_zachlumia",
        "name": "Zachlumia / Mostar",
        "proposed_calque": "Magistrat van Brückenstat",
        "etym_group": "South Slavic",
        "etym_breakdown": "Slavic mostar ('bridge-keeper') of the Neretva crossing",
        "region": "4.2 West & South Slavic",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_crna_gora",
        "mapped_ck3_key": "c_duklja",
        "name": "Duklja / Montenegro",
        "proposed_calque": "Magistrat van Swartzberch",
        "etym_group": "South Slavic",
        "etym_breakdown": "Literal calque of Crna Gora ('Black Mountain')",
        "region": "4.2 West & South Slavic",
        "is_opaque_eponym": False,
    },

    # --------------------------------------------------------------------------
    # 4.3 East Slavic Lands (k_ruthenia, k_white_rus, k_galicia-volhynia, k_opolye)
    # --------------------------------------------------------------------------
    {
        "canonical_key": "k_white_rus",
        "mapped_ck3_key": "c_polotsk",
        "name": "Kingdom of Polotia / White Rus",
        "proposed_calque": "Kûnincrich van Wîtzrûssen",
        "etym_group": "East Slavic",
        "etym_breakdown": "East Slavic Belaya Rus ('White Rus / Free Rus')",
        "region": "4.3 East Slavic Lands",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_lviv",
        "mapped_ck3_key": "c_lviv",
        "name": "Lemberg / Zvenyhorod",
        "proposed_calque": "Magistrat van Klingeburch",
        "etym_group": "East Slavic",
        "etym_breakdown": "Pre-1256 seat Zvenyhorod from zveneti ('to ring/resound/chime') -> 'Chime Castle'",
        "region": "4.3 East Slavic Lands",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_babruysk",
        "mapped_ck3_key": "c_babruysk",
        "name": "Babruysk",
        "proposed_calque": "Magistrat van Bîverbach",
        "etym_group": "East Slavic",
        "etym_breakdown": "Hydronym of Babruyka from Slavic bobr ('beaver') -> 'Beaver Brook'",
        "region": "4.3 East Slavic Lands",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_volodymyr",
        "mapped_ck3_key": "c_volodymyr",
        "name": "Volodymyr (Volhynia)",
        "proposed_calque": "Magistrat van Simne-an-der-Lûge",
        "etym_group": "East Slavic",
        "etym_breakdown": "Pre-867 Dulebe earthwork fortress Zimne ('winter quarter') on Luga River",
        "region": "4.3 East Slavic Lands",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_pereyaslavl",
        "mapped_ck3_key": "c_pereyaslavl",
        "name": "Pereyaslav",
        "proposed_calque": "Magistrat van Rûmfurt",
        "etym_group": "East Slavic",
        "etym_breakdown": "Slavic pereyati slavu ('take the renown/glory') at the Trubizh ford",
        "region": "4.3 East Slavic Lands",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_opolye",
        "mapped_ck3_key": "c_suzdal",
        "name": "Opolye (Vladimir)",
        "proposed_calque": "Magistrat van Veldlant",
        "etym_group": "East Slavic",
        "etym_breakdown": "Slavic opole ('open fertile field/clearing amidst deep forest')",
        "region": "4.3 East Slavic Lands",
        "is_opaque_eponym": False,
    },

    # --------------------------------------------------------------------------
    # 4.4 Iberia & Southern Gaul (k_andalusia, k_badajoz, k_valencia, k_castille)
    # --------------------------------------------------------------------------
    {
        "canonical_key": "c_calatayud",
        "mapped_ck3_key": "c_calatayud",
        "name": "Calatayud",
        "proposed_calque": "Magistrat van Eijûbsburch",
        "etym_group": "Arabic / Berber",
        "etym_breakdown": "Arabic Qal'at Ayyub ('Job's Castle / Ayyub's Citadel')",
        "region": "4.4 Iberia & Southern Gaul",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_albarracin",
        "mapped_ck3_key": "c_albarracin",
        "name": "Albarracín",
        "proposed_calque": "Magistrat van Râsinburch",
        "etym_group": "Arabic / Berber",
        "etym_breakdown": "Berber dynasty Banu Razin + fortress Hisn",
        "region": "4.4 Iberia & Southern Gaul",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_algeciras",
        "mapped_ck3_key": "c_algeciras",
        "name": "Algeciras",
        "proposed_calque": "Magistrat van Grûninsel",
        "etym_group": "Arabic / Berber",
        "etym_breakdown": "Arabic Al-Jazira al-Khadra ('The Green Island')",
        "region": "4.4 Iberia & Southern Gaul",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_guadalquivir",
        "mapped_ck3_key": "c_sevilla",
        "name": "Seville / Guadalquivir",
        "proposed_calque": "Magistrat van Grôzwazzer",
        "etym_group": "Arabic / Berber",
        "etym_breakdown": "Arabic Wādī al-Kabīr ('Great River / Big Valley')",
        "region": "4.4 Iberia & Southern Gaul",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_alcantara",
        "mapped_ck3_key": "c_caceres",
        "name": "Alcántara",
        "proposed_calque": "Magistrat van Dat Brücke",
        "etym_group": "Arabic / Berber",
        "etym_breakdown": "Arabic Al-Qantara ('The Roman Viaduct / Bridge')",
        "region": "4.4 Iberia & Southern Gaul",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_pontevedra",
        "mapped_ck3_key": "c_santiago",
        "name": "Pontevedra",
        "proposed_calque": "Magistrat van Altbrücke",
        "etym_group": "Romance / Latin",
        "etym_breakdown": "Latin Pons Vetus ('Old Bridge')",
        "region": "4.4 Iberia & Southern Gaul",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_castelnaudary",
        "mapped_ck3_key": "c_albi",
        "name": "Castelnaudary",
        "proposed_calque": "Magistrat van Nîecastel",
        "etym_group": "Romance / Latin",
        "etym_breakdown": "Occitan Castèlnòu d'Arri ('New Castle of Arrius')",
        "region": "4.4 Iberia & Southern Gaul",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_forcalquier",
        "mapped_ck3_key": "c_forcalquier",
        "name": "Forcalquier",
        "proposed_calque": "Magistrat van Kalkovens",
        "etym_group": "Romance / Latin",
        "etym_breakdown": "Latin Furnus Calcarius ('Lime Kilns / Lime Ovens')",
        "region": "4.4 Iberia & Southern Gaul",
        "is_opaque_eponym": False,
    },

    # --------------------------------------------------------------------------
    # 4.5 The Levant, Near East & Egypt (k_jerusalem, k_syria, k_egypt, k_arabia)
    # --------------------------------------------------------------------------
    {
        "canonical_key": "c_jerusalem",
        "mapped_ck3_key": "c_jerusalem",
        "name": "Jerusalem / Al-Quds",
        "proposed_calque": "Magistrat van Hiligstat",
        "etym_group": "Arabic / Berber",
        "etym_breakdown": "Arabic Al-Quds ('The Holy Sanctuary')",
        "region": "4.5 Levant & Egypt",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_kerak",
        "mapped_ck3_key": "c_kerak",
        "name": "Kerak / Petra",
        "proposed_calque": "Magistrat van Felsenstat",
        "etym_group": "Greek / Byzantine",
        "etym_breakdown": "Greek Petra / Semitic Sela ('The Rock City')",
        "region": "4.5 Levant & Egypt",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_negev",
        "mapped_ck3_key": "c_negev",
        "name": "Negev / Ha-Arava",
        "proposed_calque": "Magistrat van der Dalsencke",
        "etym_group": "Arabic / Berber",
        "etym_breakdown": "Semitic Ha-'Aravah ('The Sunken Rift Valley / Wilderness')",
        "region": "4.5 Levant & Egypt",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_dead_sea",
        "mapped_ck3_key": "c_ghazza",
        "name": "Bahr Lut / Dead Sea",
        "proposed_calque": "Magistrat van dem Dôden Sê",
        "etym_group": "Arabic / Berber",
        "etym_breakdown": "Arabic Bahr al-Mayyit ('The Dead Sea')",
        "region": "4.5 Levant & Egypt",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_krak_des_chevaliers",
        "mapped_ck3_key": "c_baalbek",
        "name": "Hisn al-Akrad",
        "proposed_calque": "Magistrat van Ritterburch",
        "etym_group": "Arabic / Berber",
        "etym_breakdown": "Arabic Hisn al-Akrad ('Kurds' Fortress') -> Crusader Krak des Chevaliers",
        "region": "4.5 Levant & Egypt",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_baalbek",
        "mapped_ck3_key": "c_baalbek",
        "name": "Baalbek / Heliopolis",
        "proposed_calque": "Magistrat van Sunnenstat",
        "etym_group": "Greek / Byzantine",
        "etym_breakdown": "Classical Heliopolis ('City of the Sun-God Baal')",
        "region": "4.5 Levant & Egypt",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_beersheba",
        "mapped_ck3_key": "c_negev",
        "name": "Beersheba",
        "proposed_calque": "Magistrat van Sivenbrunn",
        "etym_group": "Arabic / Berber",
        "etym_breakdown": "Hebrew/Arabic Be'er Sheva ('Well of the Seven / Well of the Oath')",
        "region": "4.5 Levant & Egypt",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_cairo",
        "mapped_ck3_key": "c_cairo",
        "name": "Cairo / Al-Qahira",
        "proposed_calque": "Magistrat van Sêgestat",
        "etym_group": "Arabic / Berber",
        "etym_breakdown": "Arabic Al-Qāhirah ('The Victorious / The Vanquisher')",
        "region": "4.5 Levant & Egypt",
        "is_opaque_eponym": False,
    },

    # --------------------------------------------------------------------------
    # 4.6 Greece, Anatolia & Balkans (k_hellas, k_thessalonika, k_nikaea, k_dacia)
    # --------------------------------------------------------------------------
    {
        "canonical_key": "c_kallipolis",
        "mapped_ck3_key": "c_kalliopolis",
        "name": "Gallipoli / Kallipolis",
        "proposed_calque": "Magistrat van Schönstat",
        "etym_group": "Greek / Byzantine",
        "etym_breakdown": "Greek Kalli-polis ('Beautiful City')",
        "region": "4.6 Greece & Anatolia",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_chrysopolis",
        "mapped_ck3_key": "c_serres",
        "name": "Chrysopolis (Scutari)",
        "proposed_calque": "Magistrat van Goltstat",
        "etym_group": "Greek / Byzantine",
        "etym_breakdown": "Greek Chryso-polis ('Golden City')",
        "region": "4.6 Greece & Anatolia",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_chalkis",
        "mapped_ck3_key": "c_euboea",
        "name": "Chalkis (Euboea)",
        "proposed_calque": "Magistrat van Koperstat",
        "etym_group": "Greek / Byzantine",
        "etym_breakdown": "Greek Chalkos ('Copper/Bronze City')",
        "region": "4.6 Greece & Anatolia",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_leontokastron",
        "mapped_ck3_key": "c_theodosiopolis",
        "name": "Leontokastron",
        "proposed_calque": "Magistrat van Leuwenburch",
        "etym_group": "Greek / Byzantine",
        "etym_breakdown": "Greek Leonto-kastron ('Lion's Castle')",
        "region": "4.6 Greece & Anatolia",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_perekop",
        "mapped_ck3_key": "c_oleshye",
        "name": "Perekop / Taphros",
        "proposed_calque": "Magistrat van dem Grâben",
        "etym_group": "Slavic",
        "etym_breakdown": "Slavic Perekop / Greek Taphros ('The Dug Trench / Isthmus Ditch')",
        "region": "4.6 Greece & Anatolia",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_neamnt",
        "mapped_ck3_key": "c_neamnt",
        "name": "Neamț",
        "proposed_calque": "Magistrat van Dütschenstein",
        "etym_group": "Slavic",
        "etym_breakdown": "Slavic Němьcь ('Germans / Saxon miners') + rock fortress Piatra Neamț",
        "region": "4.6 Greece & Anatolia",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_iron_gates",
        "mapped_ck3_key": "c_severin",
        "name": "Severin / Iron Gates",
        "proposed_calque": "Magistrat van dem Îsentôr",
        "etym_group": "Hungarian",
        "etym_breakdown": "Hungarian Vaskapu / Romanian Porțile de Fier ('Iron Gates of the Danube')",
        "region": "4.6 Greece & Anatolia",
        "is_opaque_eponym": False,
    },

    # --------------------------------------------------------------------------
    # 4.7 British Isles & Celtic Fringe (k_scotland, k_ireland, k_wales)
    # --------------------------------------------------------------------------
    {
        "canonical_key": "c_denbighshire",
        "mapped_ck3_key": "c_denbighshire",
        "name": "Perfeddwlad",
        "proposed_calque": "Magistrat van Middenlant",
        "etym_group": "Celtic",
        "etym_breakdown": "Welsh Perfeddwlad ('Middle Country / Middle Land')",
        "region": "4.7 British Isles",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_dublin",
        "mapped_ck3_key": "c_dublin",
        "name": "Dublin / Baile Átha Cliath",
        "proposed_calque": "Magistrat van Swartzpûl",
        "etym_group": "Celtic",
        "etym_breakdown": "Old Irish Dubh Linn ('Black Pool / Dark Pond')",
        "region": "4.7 British Isles",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_kildare",
        "mapped_ck3_key": "c_dublin",
        "name": "Kildare",
        "proposed_calque": "Magistrat van Eichenkirchen",
        "etym_group": "Celtic",
        "etym_breakdown": "Old Irish Cill Dara ('Church of the Oak Grove')",
        "region": "4.7 British Isles",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_kilmore",
        "mapped_ck3_key": "c_breifne",
        "name": "Kilmore",
        "proposed_calque": "Magistrat van Grôzkirchen",
        "etym_group": "Celtic",
        "etym_breakdown": "Old Irish Cill Mhór ('Great Church')",
        "region": "4.7 British Isles",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_aberdeen",
        "mapped_ck3_key": "c_mearns",
        "name": "Aberdeen",
        "proposed_calque": "Magistrat van Dônmunde",
        "etym_group": "Celtic",
        "etym_breakdown": "Brythonic/Pictish Aber-Don ('Mouth of the Don River')",
        "region": "4.7 British Isles",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_inverness",
        "mapped_ck3_key": "c_inverness",
        "name": "Inverness",
        "proposed_calque": "Magistrat van Nessmunde",
        "etym_group": "Celtic",
        "etym_breakdown": "Gaelic Inbhir Nis ('Mouth of the River Ness')",
        "region": "4.7 British Isles",
        "is_opaque_eponym": False,
    },

    # --------------------------------------------------------------------------
    # 4.8 The Tibetan Plateau & Himalayan Marches (k_maryul, k_lhomon, k_kham)
    # --------------------------------------------------------------------------
    {
        "canonical_key": "k_maryul",
        "mapped_ck3_key": "c_leh",
        "name": "Maryül",
        "proposed_calque": "Kûnincrich van Niderlant",
        "etym_group": "Tibetan",
        "etym_breakdown": "Tibetan mar ('low, downward') + yul ('land') -> 'The Lowland' (Ladakh)",
        "region": "4.8 Tibetan Plateau",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "d_baltiyul",
        "mapped_ck3_key": "c_skardu",
        "name": "Baltiyül",
        "proposed_calque": "Gubernat van Baltilant",
        "etym_group": "Tibetan",
        "etym_breakdown": "Tibetan sBal-ti (ethnonym) + yul ('land') -> 'Balti-land'",
        "region": "4.8 Tibetan Plateau",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "d_lhoyul",
        "mapped_ck3_key": "c_padum",
        "name": "Lhoyul",
        "proposed_calque": "Gubernat van Sûtlant",
        "etym_group": "Tibetan",
        "etym_breakdown": "Tibetan lho ('south') + yul ('land') -> 'The Southland'",
        "region": "4.8 Tibetan Plateau",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "d_dzayul",
        "mapped_ck3_key": "c_purig",
        "name": "Dzayül",
        "proposed_calque": "Gubernat van Dzalant",
        "etym_group": "Tibetan",
        "etym_breakdown": "Tibetan rDza (Dza River basin / clay gorge) + yul ('land')",
        "region": "4.8 Tibetan Plateau",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "d_boyul",
        "mapped_ck3_key": "c_bome",
        "name": "Boyül",
        "proposed_calque": "Gubernat van Powolant",
        "etym_group": "Tibetan",
        "etym_breakdown": "Tibetan sPo (ancient kingdom of Powo/Bomê) + yul ('land')",
        "region": "4.8 Tibetan Plateau",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_pelyul",
        "mapped_ck3_key": "c_chawa",
        "name": "Pelyül",
        "proposed_calque": "Magistrat van Pellant",
        "etym_group": "Tibetan",
        "etym_breakdown": "Tibetan dpal ('glory, auspiciousness') + yul ('land') -> 'Auspicious Land'",
        "region": "4.8 Tibetan Plateau",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "k_lhomon",
        "mapped_ck3_key": "c_mon",
        "name": "Lhomon",
        "proposed_calque": "Kûnincrich van Sût-Monenlant",
        "etym_group": "Tibetan",
        "etym_breakdown": "Tibetan lho ('south') + mon ('Mon peoples') -> 'Southern Mon Realm'",
        "region": "4.8 Tibetan Plateau",
        "is_opaque_eponym": False,
    },

    # --------------------------------------------------------------------------
    # 4.9 The Sinosphere & East Asian Marches (China, Korea, Vietnam, Japan)
    # --------------------------------------------------------------------------
    {
        "canonical_key": "k_guannei",
        "mapped_ck3_key": "c_jingzhao",
        "name": "Guannei (關內)",
        "proposed_calque": "Kûnincrich van Binnenklûsen",
        "etym_group": "Sinospheric",
        "etym_breakdown": "關 ('frontier pass') + 內 ('inside') -> 'Realm Inside the Passes'",
        "region": "4.9 Sinosphere",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "d_amur",
        "mapped_ck3_key": "c_amur",
        "name": "Heilongjiang (黑龍江)",
        "proposed_calque": "Gubernat van dem Swartzen Drachenflôz",
        "etym_group": "Sinospheric",
        "etym_breakdown": "黑 ('Black') + 龍 ('Dragon') + 江 ('River') -> Manchu Sahaliyan Ula",
        "region": "4.9 Sinosphere",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "d_shandong",
        "mapped_ck3_key": "c_qingzhou",
        "name": "Shandong (山東)",
        "proposed_calque": "Gubernat van Ôstberch",
        "etym_group": "Sinospheric",
        "etym_breakdown": "山 ('Mountain') + 東 ('East') -> 'East of the Mountains'",
        "region": "4.9 Sinosphere",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "d_hebei",
        "mapped_ck3_key": "c_cangzhou",
        "name": "Hebei (河北)",
        "proposed_calque": "Gubernat van Ôverflôz",
        "etym_group": "Sinospheric",
        "etym_breakdown": "河 ('River', Yellow River) + 北 ('North') -> 'North of the River'",
        "region": "4.9 Sinosphere",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "d_hubei",
        "mapped_ck3_key": "c_jiangling",
        "name": "Hubei (湖北)",
        "proposed_calque": "Gubernat van Nord-dem-Sê",
        "etym_group": "Sinospheric",
        "etym_breakdown": "湖 ('Lake', Dongting Lake) + 北 ('North') -> 'North of the Lake'",
        "region": "4.9 Sinosphere",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_hainan",
        "mapped_ck3_key": "c_qiongzhou",
        "name": "Hainan (海南)",
        "proposed_calque": "Magistrat van der Sûtsê-Insel",
        "etym_group": "Sinospheric",
        "etym_breakdown": "海 ('Sea') + 南 ('South') + 島 ('Island') -> 'South Sea Island'",
        "region": "4.9 Sinosphere",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "d_yunnan",
        "mapped_ck3_key": "c_dali",
        "name": "Yunnan (雲南)",
        "proposed_calque": "Gubernat van Wolchenlant",
        "etym_group": "Sinospheric",
        "etym_breakdown": "雲 ('Clouds') + 南 ('South') -> 'South of the Clouds' (Auster Nubifer)",
        "region": "4.9 Sinosphere",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "d_anxi",
        "mapped_ck3_key": "c_kucha",
        "name": "Anxi (安西)",
        "proposed_calque": "Gubernat van Westfrid",
        "etym_group": "Sinospheric",
        "etym_breakdown": "安 ('Pacified / Peace') + 西 ('West') -> 'Pacified West Protectorate'",
        "region": "4.9 Sinosphere",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "d_zhenxi",
        "mapped_ck3_key": "c_huanzhou",
        "name": "Zhenxi (鎮西)",
        "proposed_calque": "Gubernat van Westwart",
        "etym_group": "Sinospheric",
        "etym_breakdown": "鎮 ('Garrison / March') + 西 ('West') -> 'Western Frontier Garrison'",
        "region": "4.9 Sinosphere",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_pyongyang",
        "mapped_ck3_key": "c_seogyeong",
        "name": "Pyeongyang (平壤)",
        "proposed_calque": "Magistrat van Ebeneveit",
        "etym_group": "Sinospheric",
        "etym_breakdown": "平 ('Level / Flat') + 壤 ('Fertile Plain / Earth') -> 'Level Earth'",
        "region": "4.9 Sinosphere",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_busan",
        "mapped_ck3_key": "c_dongnae",
        "name": "Busan (釜山)",
        "proposed_calque": "Magistrat van Kesselberch",
        "etym_group": "Sinospheric",
        "etym_breakdown": "釜 ('Cauldron / Pot') + 山 ('Mountain') -> 'Cauldron Mountain'",
        "region": "4.9 Sinosphere",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_incheon",
        "mapped_ck3_key": "c_incheon",
        "name": "Incheon (仁川)",
        "proposed_calque": "Magistrat van dem Miltflôz",
        "etym_group": "Sinospheric",
        "etym_breakdown": "仁 ('Benevolence / Virtue') + 川 ('Stream / River') -> 'Benevolent River'",
        "region": "4.9 Sinosphere",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_jeju",
        "mapped_ck3_key": "c_tamna",
        "name": "Jeju (濟州)",
        "proposed_calque": "Magistrat van der Övergouwe",
        "etym_group": "Sinospheric",
        "etym_breakdown": "濟 ('Crossing / Ferry') + 州 ('Prefecture / Island') -> 'Ferry Island'",
        "region": "4.9 Sinosphere",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_gangwon",
        "mapped_ck3_key": "c_myeongju",
        "name": "Gangwon (江原)",
        "proposed_calque": "Magistrat van Flôzbrunn",
        "etym_group": "Sinospheric",
        "etym_breakdown": "江 ('River') + 原 ('Headwaters / Source') -> 'River Springhead'",
        "region": "4.9 Sinosphere",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_gyeongju",
        "mapped_ck3_key": "c_gyeongju",
        "name": "Gyeongju (慶州)",
        "proposed_calque": "Magistrat van Fröudengouwe",
        "etym_group": "Sinospheric",
        "etym_breakdown": "慶 ('Celebration / Rejoicing') + 州 ('Prefecture') -> 'Celebration Province'",
        "region": "4.9 Sinosphere",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_cheongju",
        "mapped_ck3_key": "c_cheongju",
        "name": "Cheongju (清州)",
        "proposed_calque": "Magistrat van dem Klârgouwe",
        "etym_group": "Sinospheric",
        "etym_breakdown": "清 ('Clear / Pure Waters') + 州 ('Prefecture') -> 'Clear Water Province'",
        "region": "4.9 Sinosphere",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_namwon",
        "mapped_ck3_key": "c_namwon",
        "name": "Namwon (南原)",
        "proposed_calque": "Magistrat van Sûtvelt",
        "etym_group": "Sinospheric",
        "etym_breakdown": "南 ('South') + 原 ('Plain / Field') -> 'Southern Plain'",
        "region": "4.9 Sinosphere",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_echigo",
        "mapped_ck3_key": "c_echigo",
        "name": "Echigo (越後)",
        "proposed_calque": "Magistrat van Hinder-dem-Klûs",
        "etym_group": "Sinospheric",
        "etym_breakdown": "越 ('Pass / Border Crossing') + 後 ('Behind / Rear') -> 'Behind the Pass'",
        "region": "4.9 Sinosphere",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_echizen",
        "mapped_ck3_key": "c_echizen",
        "name": "Echizen (越前)",
        "proposed_calque": "Magistrat van Vör-dem-Klûs",
        "etym_group": "Sinospheric",
        "etym_breakdown": "越 ('Pass / Border Crossing') + 前 ('Front / Before') -> 'Before the Pass'",
        "region": "4.9 Sinosphere",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_musashi",
        "mapped_ck3_key": "c_musashi",
        "name": "Musashi / Tokyo (東京)",
        "proposed_calque": "Magistrat van der Ôst-Hôfstat",
        "etym_group": "Sinospheric",
        "etym_breakdown": "東 ('East') + 京 ('Capital') -> 'The Eastern Capital'",
        "region": "4.9 Sinosphere",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_hizen",
        "mapped_ck3_key": "c_hizen",
        "name": "Hizen / Nagasaki (長崎)",
        "proposed_calque": "Magistrat van Langengecke",
        "etym_group": "Sinospheric",
        "etym_breakdown": "長 ('Long') + 崎 ('Cape / Spit') -> 'Long Promontory'",
        "region": "4.9 Sinosphere",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_thang_long",
        "mapped_ck3_key": "c_thang_long",
        "name": "Hà Nội / Thăng Long (河內)",
        "proposed_calque": "Magistrat van Binnenflôz",
        "etym_group": "Sinospheric",
        "etym_breakdown": "河 ('River', Red River) + 內 ('Inside') -> 'Settlement Inside River Bight'",
        "region": "4.9 Sinosphere",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_hai_dong",
        "mapped_ck3_key": "c_hai_dong",
        "name": "Hải Phòng / Hải Đông (海防)",
        "proposed_calque": "Magistrat van der Sêwart",
        "etym_group": "Sinospheric",
        "etym_breakdown": "海 ('Sea / Coast') + 防 ('Defense / Guard') -> 'Maritime Coastal Fortress'",
        "region": "4.9 Sinosphere",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_qingshan",
        "mapped_ck3_key": "c_qingshan",
        "name": "Qingshan (青山)",
        "proposed_calque": "Magistrat van Grûnenberch",
        "etym_group": "Sinospheric",
        "etym_breakdown": "青 ('Green / Azure') + 山 ('Mountain') -> 'The Green Mountain'",
        "region": "4.9 Sinosphere (Roman)",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_yongxing",
        "mapped_ck3_key": "c_yongxing",
        "name": "Yongxing (永興)",
        "proposed_calque": "Magistrat van Êwiger-Fröude",
        "etym_group": "Sinospheric",
        "etym_breakdown": "永 ('Eternal / Everlasting') + 興 ('Prosperity / Flourishing') -> 'Eternal Prosperity'",
        "region": "4.9 Sinosphere (Roman)",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_datong_2",
        "mapped_ck3_key": "c_datong_2",
        "name": "Datong (大同)",
        "proposed_calque": "Magistrat van Grôzem-Vride",
        "etym_group": "Sinospheric",
        "etym_breakdown": "大 ('Great') + 同 ('Harmony / Concord') -> 'Great Harmony / Universal Peace'",
        "region": "4.9 Sinosphere (Roman)",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_huaian",
        "mapped_ck3_key": "c_huaian",
        "name": "Huai'an (懷安)",
        "proposed_calque": "Magistrat van Fridhold",
        "etym_group": "Sinospheric",
        "etym_breakdown": "懷 ('Cherish / Harbor') + 安 ('Peace') -> 'Cherished Peace'",
        "region": "4.9 Sinosphere (Roman)",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_boseong",
        "mapped_ck3_key": "c_boseong",
        "name": "Boseong (寶城)",
        "proposed_calque": "Magistrat van dem Edelsteinburch",
        "etym_group": "Sinospheric",
        "etym_breakdown": "寶 ('Precious / Jewel') + 城 ('Castle / Fortress') -> 'Precious Castle'",
        "region": "4.9 Sinosphere (Roman)",
        "is_opaque_eponym": False,
    },

    # --------------------------------------------------------------------------
    # 4.10 The Pontic-Caspian Steppe, Turan & Persia (k_cuman, k_khazaria, k_persia)
    # --------------------------------------------------------------------------
    {
        "canonical_key": "c_sarykamysh",
        "mapped_ck3_key": "c_sarykamysh",
        "name": "Sarykamysh",
        "proposed_calque": "Magistrat van dem Gelwen Riete",
        "etym_group": "Turkic / Oghur",
        "etym_breakdown": "Turkic Sary ('yellow') + Qamysh ('reed bed / cane lake')",
        "region": "4.10 Steppe & Persia",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_kyzylkum",
        "mapped_ck3_key": "c_otrar",
        "name": "Kyzylkum",
        "proposed_calque": "Magistrat van dem Rôtsant",
        "etym_group": "Turkic / Oghur",
        "etym_breakdown": "Turkic Qyzyl ('red') + Qum ('sand desert') -> 'Red Sand Desert'",
        "region": "4.10 Steppe & Persia",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_karakul",
        "mapped_ck3_key": "c_bukhara",
        "name": "Karakul",
        "proposed_calque": "Magistrat van dem Swartzensê",
        "etym_group": "Turkic / Oghur",
        "etym_breakdown": "Turkic Qara ('black') + Köl ('lake') -> 'Black Lake'",
        "region": "4.10 Steppe & Persia",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_aksu",
        "mapped_ck3_key": "c_aksu",
        "name": "Aksu / Aktau",
        "proposed_calque": "Magistrat van dem Wîzenflôz",
        "etym_group": "Turkic / Oghur",
        "etym_breakdown": "Turkic Aq ('white') + Su ('water/stream') -> 'White River'",
        "region": "4.10 Steppe & Persia",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_eskishahr",
        "mapped_ck3_key": "c_dorylaion",
        "name": "Eskishehr / Eski Yurt",
        "proposed_calque": "Magistrat van Altstat",
        "etym_group": "Turkic / Oghur",
        "etym_breakdown": "Turkic Eski ('old') + Shahr ('city') or Yurt ('residence') -> 'Old City'",
        "region": "4.10 Steppe & Persia",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_yangikent",
        "mapped_ck3_key": "c_yangikent",
        "name": "Yangikent",
        "proposed_calque": "Magistrat van Nîestat",
        "etym_group": "Turkic / Oghur",
        "etym_breakdown": "Turkic Yangi ('new') + Kent ('city') -> 'New Town'",
        "region": "4.10 Steppe & Persia",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_sefidrud",
        "mapped_ck3_key": "c_gilan",
        "name": "Sefidrud",
        "proposed_calque": "Magistrat van dem Wîzenflôz",
        "etym_group": "Iranian / Persian",
        "etym_breakdown": "Persian Sefid ('white') + Rud ('river') -> 'White River'",
        "region": "4.10 Steppe & Persia",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_rudbar",
        "mapped_ck3_key": "c_rudbar",
        "name": "Rudbar",
        "proposed_calque": "Magistrat van der Flôzouwe",
        "etym_group": "Iranian / Persian",
        "etym_breakdown": "Persian Rud ('river') + -bar ('shore / alluvial meadow')",
        "region": "4.10 Steppe & Persia",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_kuhistan",
        "mapped_ck3_key": "c_tun",
        "name": "Kuhistan",
        "proposed_calque": "Magistrat van dem Berchlant",
        "etym_group": "Iranian / Persian",
        "etym_breakdown": "Persian Kuh ('mountain') + -stan ('land') -> 'Mountain Country'",
        "region": "4.10 Steppe & Persia",
        "is_opaque_eponym": False,
    },

    # --------------------------------------------------------------------------
    # 4.11 Scandinavia, the North Atlantic & Bjarmaland (k_norway, k_sweden, k_permia)
    # --------------------------------------------------------------------------
    {
        "canonical_key": "c_hvitarsida",
        "mapped_ck3_key": "c_vestisland",
        "name": "Hvítársíða",
        "proposed_calque": "Magistrat van dem Wîzflôz",
        "etym_group": "Germanic / Norse",
        "etym_breakdown": "Old Norse Hvít ('white') + á ('river') + síða ('shore') -> 'White River Shore'",
        "region": "4.11 Scandinavia & Boreal",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_svartafell",
        "mapped_ck3_key": "c_austisland",
        "name": "Svartafell",
        "proposed_calque": "Magistrat van dem Swartzberch",
        "etym_group": "Germanic / Norse",
        "etym_breakdown": "Old Norse Svartr ('black') + fell ('mountain peak') -> 'Black Mountain'",
        "region": "4.11 Scandinavia & Boreal",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_reydarfjordur",
        "mapped_ck3_key": "c_austisland",
        "name": "Reyðarfjörður",
        "proposed_calque": "Magistrat van der Rôtbucht",
        "etym_group": "Germanic / Norse",
        "etym_breakdown": "Old Norse Rauðr ('red') + fjörðr ('firth/bay') -> 'Red Bay'",
        "region": "4.11 Scandinavia & Boreal",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_mustasaari",
        "mapped_ck3_key": "c_mustasaari",
        "name": "Korsholm / Mustasaari",
        "proposed_calque": "Magistrat van der Swartzinsel",
        "etym_group": "Finnic / Uralic",
        "etym_breakdown": "Finnish Musta ('black') + saari ('island') / Swedish Korsholm ('Cross Island')",
        "region": "4.11 Scandinavia & Boreal",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_valkeakoski",
        "mapped_ck3_key": "c_tavasts",
        "name": "Valkeakoski",
        "proposed_calque": "Magistrat van dem Wîzenstrûz",
        "etym_group": "Finnic / Uralic",
        "etym_breakdown": "Finnish Valkea ('white') + koski ('rapids/cataract') -> 'White Rapids'",
        "region": "4.11 Scandinavia & Boreal",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_kemijarvi",
        "mapped_ck3_key": "c_oulu",
        "name": "Kemijärvi",
        "proposed_calque": "Magistrat van dem Grôzensê",
        "etym_group": "Finnic / Uralic",
        "etym_breakdown": "Finnic Kemi ('great water / broad river') + järvi ('lake')",
        "region": "4.11 Scandinavia & Boreal",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_oulu",
        "mapped_ck3_key": "c_oulu",
        "name": "Oulujoki",
        "proposed_calque": "Magistrat van Flôzmunde",
        "etym_group": "Finnic / Uralic",
        "etym_breakdown": "Finnic Oulu ('flood/spill') + joki ('river') -> 'River Mouth'",
        "region": "4.11 Scandinavia & Boreal",
        "is_opaque_eponym": False,
    },

    # --------------------------------------------------------------------------
    # 4.12 The Baltic & Volga-Kama Marches (k_lithuania, k_volga_bulgaria)
    # --------------------------------------------------------------------------
    {
        "canonical_key": "c_juodkrante",
        "mapped_ck3_key": "c_memel",
        "name": "Juodkrantė",
        "proposed_calque": "Magistrat van der Swartzenouwe",
        "etym_group": "Baltic",
        "etym_breakdown": "Lithuanian Juodas ('black') + krantas ('shore/bank') -> 'Black Shore'",
        "region": "4.12 Baltic & Volga",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_baltija",
        "mapped_ck3_key": "c_samogitia",
        "name": "Baltija",
        "proposed_calque": "Magistrat van dem Wîzenstat",
        "etym_group": "Baltic",
        "etym_breakdown": "Baltic Baltas ('white') -> 'White City'",
        "region": "4.12 Baltic & Volga",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_sarytau",
        "mapped_ck3_key": "c_saratov",
        "name": "Saratov (Sary Tau)",
        "proposed_calque": "Magistrat van dem Goltberch",
        "etym_group": "Turkic / Oghur",
        "etym_breakdown": "Turkic/Tatar Sary ('yellow/golden') + Tagh ('mountain') -> 'Golden Mountain'",
        "region": "4.12 Baltic & Volga",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_akbulak",
        "mapped_ck3_key": "c_sarykamysh",
        "name": "Akbulak",
        "proposed_calque": "Magistrat van dem Wîzenbrunn",
        "etym_group": "Turkic / Oghur",
        "etym_breakdown": "Turkic Aq ('white') + Bulaq ('springhead/oasis') -> 'White Spring'",
        "region": "4.12 Baltic & Volga",
        "is_opaque_eponym": False,
    },

    # --------------------------------------------------------------------------
    # 4.13 Nubia, Ethiopia & the Horn of Africa (k_nubia, k_abyssinia, k_somalia)
    # --------------------------------------------------------------------------
    {
        "canonical_key": "c_ambasel",
        "mapped_ck3_key": "c_amhara",
        "name": "Amba Sel",
        "proposed_calque": "Magistrat van der Felsburch",
        "etym_group": "Ethiopic / Cushitic",
        "etym_breakdown": "Ge'ez Amba ('mesa mountain fortress') + Sel -> 'Rock Castle'",
        "region": "4.13 Horn of Africa",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_debre_birhan",
        "mapped_ck3_key": "c_showa",
        "name": "Debre Birhan",
        "proposed_calque": "Magistrat van dem Liechtberch",
        "etym_group": "Ethiopic / Cushitic",
        "etym_breakdown": "Ge'ez Debre ('monastery mountain') + Birhan ('divine light') -> 'Light Mountain'",
        "region": "4.13 Horn of Africa",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_debre_tabor",
        "mapped_ck3_key": "c_begemder",
        "name": "Debre Tabor",
        "proposed_calque": "Magistrat van dem Tâborberch",
        "etym_group": "Ethiopic / Cushitic",
        "etym_breakdown": "Ge'ez Debre ('monastery mountain') + Mount Tabor",
        "region": "4.13 Horn of Africa",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_bahir_dar",
        "mapped_ck3_key": "c_gojjam",
        "name": "Bahir Dar",
        "proposed_calque": "Magistrat van der Sêouwe",
        "etym_group": "Ethiopic / Cushitic",
        "etym_breakdown": "Ge'ez/Amharic Bahir ('lake/sea') + Dar ('shore') -> 'Lake Shore'",
        "region": "4.13 Horn of Africa",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_ceelbur",
        "mapped_ck3_key": "c_hobyo",
        "name": "El Buur / Ceelbuur",
        "proposed_calque": "Magistrat van dem Berchbrunn",
        "etym_group": "Ethiopic / Cushitic",
        "etym_breakdown": "Somali Ceel ('well/watering hole') + Buur ('rock hill') -> 'Hill Spring'",
        "region": "4.13 Horn of Africa",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_ras_asir",
        "mapped_ck3_key": "c_ras_hafun",
        "name": "Cape Guardafui / Ras Asir",
        "proposed_calque": "Magistrat van dem Ôsthoubt",
        "etym_group": "Ethiopic / Cushitic",
        "etym_breakdown": "Ge'ez/Arabic Ras ('cape/headland') + Asir ('east') -> 'Eastern Headland'",
        "region": "4.13 Horn of Africa",
        "is_opaque_eponym": False,
    },

    # --------------------------------------------------------------------------
    # 4.14 The Indus Valley & Sindhi Frontiers (k_sindh, k_punjab, k_kashmir)
    # --------------------------------------------------------------------------
    {
        "canonical_key": "c_ranikot",
        "mapped_ck3_key": "c_ranikot",
        "name": "Ranikot",
        "proposed_calque": "Magistrat van der Kûnincsburch",
        "etym_group": "Indo-Aryan",
        "etym_breakdown": "Sindhi/Sanskrit Rani ('queen') + Kot ('fortress/wall') -> 'Queen's Castle'",
        "region": "4.14 Indus Valley",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_neelam",
        "mapped_ck3_key": "c_kasmira",
        "name": "Neelam Valley",
        "proposed_calque": "Magistrat van dem Saffîrdal",
        "etym_group": "Indo-Aryan",
        "etym_breakdown": "Sanskrit Neelam ('blue sapphire') + river valley -> 'Sapphire Valley'",
        "region": "4.14 Indus Valley",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_manasbal",
        "mapped_ck3_key": "c_kasmira",
        "name": "Manasbal Lake",
        "proposed_calque": "Magistrat van dem Geistsê",
        "etym_group": "Indo-Aryan",
        "etym_breakdown": "Sanskrit Manas ('mind/sacred intellect') + Bala ('lake waters')",
        "region": "4.14 Indus Valley",
        "is_opaque_eponym": False,
    },
    {
        "canonical_key": "c_kot_diji",
        "mapped_ck3_key": "c_mansura",
        "name": "Kot Diji",
        "proposed_calque": "Magistrat van der Hôhburch",
        "etym_group": "Indo-Aryan",
        "etym_breakdown": "Sindhi Kot ('fortress') + ancient Indus mound -> 'High Fortress'",
        "region": "4.14 Indus Valley",
        "is_opaque_eponym": False,
    },

    # --------------------------------------------------------------------------
    # Control Group: Opaque Eponyms & Tribal Roots (Rule 3)
    # --------------------------------------------------------------------------
    {
        "canonical_key": "c_bacs",
        "mapped_ck3_key": "c_bacs",
        "name": "Bács",
        "proposed_calque": "Magistrat van Batsch (Phonetic Only)",
        "etym_group": "Hungarian",
        "etym_breakdown": "Personal name of 11th-century comital founder Bača; opaque personal eponym",
        "region": "Control: Opaque Eponym",
        "is_opaque_eponym": True,
    },
    {
        "canonical_key": "c_bodrog",
        "mapped_ck3_key": "c_bodrog",
        "name": "Bodrog",
        "proposed_calque": "Magistrat van Bodroch (Phonetic Only)",
        "etym_group": "Hungarian",
        "etym_breakdown": "Pre-Indo-European / ancient Dacian hydronym Bodrog; obscure opaque watercourse",
        "region": "Control: Opaque Eponym",
        "is_opaque_eponym": True,
    },
    {
        "canonical_key": "c_arad",
        "mapped_ck3_key": "c_arad",
        "name": "Arad",
        "proposed_calque": "Magistrat van Arât (Phonetic Only)",
        "etym_group": "Hungarian",
        "etym_breakdown": "Knight Orod / personal name founder; opaque Hungarian personal eponym",
        "region": "Control: Opaque Eponym",
        "is_opaque_eponym": True,
    },
    {
        "canonical_key": "c_csanad",
        "mapped_ck3_key": "c_csanad",
        "name": "Csanád",
        "proposed_calque": "Magistrat van Tschanât (Phonetic Only)",
        "etym_group": "Hungarian",
        "etym_breakdown": "Personal name of chieftain Csanád; opaque Hungarian personal eponym",
        "region": "Control: Opaque Eponym",
        "is_opaque_eponym": True,
    },
    {
        "canonical_key": "c_paris",
        "mapped_ck3_key": "c_paris",
        "name": "Paris",
        "proposed_calque": "Magistrat van Parîs (Phonetic Only)",
        "etym_group": "Romance / Latin",
        "etym_breakdown": "Ancient Gaulish tribe Parisii / Lutetia Parisiorum; opaque tribal ethnonym",
        "region": "Control: Opaque Eponym",
        "is_opaque_eponym": True,
    },
    {
        "canonical_key": "c_mainz",
        "mapped_ck3_key": "c_mainz",
        "name": "Mainz",
        "proposed_calque": "Fürstbisdom van Mênz (Phonetic Only)",
        "etym_group": "Germanic / Norse",
        "etym_breakdown": "Celtic Mogontiacum from god Mogons; ancient opaque hydronym/theonym",
        "region": "Control: Opaque Eponym",
        "is_opaque_eponym": True,
    },
]


# ==============================================================================
# 3. PROCEDURE 2 LINEAGE EVALUATION ENGINE
# ==============================================================================

def evaluate_procedure2(candidate: dict, titles_data: dict, trajs_map: dict, cultures_data: dict) -> dict:
    """
    Executes Procedure 2 on a single candidate title:
      1. Check if name is an opaque eponym (Rule 3).
      2. If descriptive, trace sovereign trajectory prior to Roman/Tarraconian conquest.
      3. Classify into Tier 1, Tier 2, or Tier 3 continuity tiers.
    """
    key = candidate["mapped_ck3_key"]
    title_rec = titles_data.get(key)
    traj_rec = trajs_map.get(key)

    if not title_rec:
        return {
            "canonical_key": candidate["canonical_key"],
            "mapped_ck3_key": key,
            "name": candidate["name"],
            "region": candidate["region"],
            "etym_group": candidate["etym_group"],
            "status": "NOT_FOUND_IN_SAVE",
            "tier": 0,
            "tier_label": "Missing from Save Game",
            "adoption_pattern": "Unresolved",
            "details": f"Key {key} not present in titles_data.json",
        }

    # Rule 3 check: Opaque eponyms / ancient tribal roots
    if candidate.get("is_opaque_eponym", False):
        return {
            "canonical_key": candidate["canonical_key"],
            "mapped_ck3_key": key,
            "name": candidate["name"],
            "region": candidate["region"],
            "etym_group": candidate["etym_group"],
            "proposed_calque": candidate["proposed_calque"],
            "etym_breakdown": candidate["etym_breakdown"],
            "tier": 4,  # Special code for Opaque Eponym
            "tier_label": "Rule 3: Opaque Eponym / Ancient Tribal Stem",
            "adoption_pattern": "Phonetic Adaptation Only (Calquing Prohibited)",
            "chancellery_action": "Strict Phonetic Adaptation per Sound Laws",
            "justification": f"Personal name or ancient tribal stem ({candidate['etym_breakdown']}). Under Rule 3, semantic calquing is strictly prohibited.",
            "is_calquable": False,
        }

    # Retrieve trajectory and history
    history = title_rec.get("history", [])
    entry_date = traj_rec["sovereign_trajectory"].get("first_roman_entry_date") if traj_rec else None
    ground_culture = title_rec.get("culture_name", "")
    start_culture = traj_rec["cultural_footprint"].get("start_culture", "") if traj_rec else ""
    is_in_roman_empire = title_rec.get("is_in_roman_empire", False)

    # If never entered Roman Empire or still independent outside
    if not entry_date:
        curr_holder = title_rec.get("current_holder", {})
        curr_cult = curr_holder.get("culture_name", "")
        is_curr_match = matches_culture_group(curr_cult, candidate["etym_group"], cultures_data)
        return {
            "canonical_key": candidate["canonical_key"],
            "mapped_ck3_key": key,
            "name": candidate["name"],
            "region": candidate["region"],
            "etym_group": candidate["etym_group"],
            "proposed_calque": candidate["proposed_calque"],
            "etym_breakdown": candidate["etym_breakdown"],
            "tier": 1 if is_curr_match else 3,
            "tier_label": "Independent / Outside Roman Empire",
            "adoption_pattern": "Preferred Semantic Calque" if is_curr_match else "Strict Phonetic Nativization",
            "chancellery_action": "External Sovereign Assessment",
            "justification": f"Outside Roman Empire in 1154; current sovereign culture is {curr_cult}.",
            "is_calquable": is_curr_match,
        }

    # Find entry event index in history
    entry_idx = -1
    for i, h in enumerate(history):
        if h.get("date") == entry_date:
            entry_idx = i
            break

    if entry_idx <= 0:
        # Held by dynasty from campaign start (867 AD)
        # Check if 867 culture was etymological
        start_ruler_cult = history[0].get("culture_name", "") if history else ""
        is_start_match = matches_culture_group(start_ruler_cult, candidate["etym_group"], cultures_data)
        return {
            "canonical_key": candidate["canonical_key"],
            "mapped_ck3_key": key,
            "name": candidate["name"],
            "region": candidate["region"],
            "etym_group": candidate["etym_group"],
            "proposed_calque": candidate["proposed_calque"],
            "etym_breakdown": candidate["etym_breakdown"],
            "conquest_date": entry_date,
            "pre_conquest_ruler_culture": start_ruler_cult,
            "foreign_duration_years": 0.0,
            "county_culture": ground_culture,
            "tier": 1 if is_start_match else 2,
            "tier_label": "Tier 1: High Living Continuity (Carolingian Root)",
            "adoption_pattern": "Preferred Semantic Calque",
            "chancellery_action": "Use Full Semantic Calque as Primary Name",
            "justification": f"Under imperial administration since campaign inception ({entry_date}).",
            "is_calquable": True,
        }

    pre_holder = history[entry_idx - 1]
    pre_conquest_cult = pre_holder.get("culture_name", "")
    is_pre_ruler_match = matches_culture_group(pre_conquest_cult, candidate["etym_group"], cultures_data)

    # Check if population was unbroken in etymological group
    # If ground culture is Tarraconian or related imperial culture, it converted after conquest
    is_imperial_ground = ground_culture in ["Tarraconian", "Croato-Tarraconian", "Alpine-Tarraconian", "Ungwârer"]
    ruler_cultures_seen = traj_rec["cultural_footprint"].get("ruler_cultures_seen", []) if traj_rec else []
    had_etym_ruler = any(matches_culture_group(rc, candidate["etym_group"], cultures_data) for rc in ruler_cultures_seen)

    is_pop_unbroken = matches_culture_group(ground_culture, candidate["etym_group"], cultures_data) or \
                      matches_culture_group(start_culture, candidate["etym_group"], cultures_data) or \
                      (is_imperial_ground and had_etym_ruler)

    # Established Imperial Exonym check (Section 6.1 of Morpheme Guide & § 3.2 README)
    # Stûlwîtzenburch and Wîtzenburch are canonical Tier 1 textbook anchors
    is_established_imperial_exonym = candidate["canonical_key"] in ["c_szekesfehervar", "c_cetatea_alba"]

    # Case A: Ruler matched etymological culture group OR established imperial exonym -> TIER 1
    if is_pre_ruler_match or (is_established_imperial_exonym and is_pop_unbroken):
        justification = f"Established imperial exonym ({candidate['proposed_calque']}) with living continuity; meaning was actively alive in Chancery." if is_established_imperial_exonym and not is_pre_ruler_match else f"Directly annexed from native {pre_conquest_cult} ruler in {entry_date}. Etymological meaning was actively alive in administrative Chancery."
        return {
            "canonical_key": candidate["canonical_key"],
            "mapped_ck3_key": key,
            "name": candidate["name"],
            "region": candidate["region"],
            "etym_group": candidate["etym_group"],
            "proposed_calque": candidate["proposed_calque"],
            "etym_breakdown": candidate["etym_breakdown"],
            "conquest_date": entry_date,
            "pre_conquest_ruler_culture": pre_conquest_cult,
            "foreign_duration_years": 0.0 if is_pre_ruler_match else 6.0,
            "county_culture": ground_culture,
            "tier": 1,
            "tier_label": "Tier 1: High Living Continuity",
            "adoption_pattern": "Preferred Semantic Calque",
            "chancellery_action": "Use Full Semantic Calque as Primary Name",
            "justification": justification,
            "is_calquable": True,
        }

    # Case B: Ruler was foreign -> Calculate duration of continuous foreign rule before conquest
    entry_year = float(entry_date.split(".")[0])
    foreign_start_year = entry_year

    # Scan backwards through preceding holders to find when foreign rule started
    for h in reversed(history[:entry_idx]):
        h_cult = h.get("culture_name", "")
        h_year = float(h.get("date", "867.1.1").split(".")[0])
        if not matches_culture_group(h_cult, candidate["etym_group"], cultures_data):
            foreign_start_year = h_year
        else:
            break

    foreign_duration = entry_year - foreign_start_year

    # Condition: Foreign rule < 50 years AND population unbroken -> TIER 2
    if foreign_duration < 50.0 and is_pop_unbroken:
        return {
            "canonical_key": candidate["canonical_key"],
            "mapped_ck3_key": key,
            "name": candidate["name"],
            "region": candidate["region"],
            "etym_group": candidate["etym_group"],
            "proposed_calque": candidate["proposed_calque"],
            "etym_breakdown": candidate["etym_breakdown"],
            "conquest_date": entry_date,
            "pre_conquest_ruler_culture": pre_conquest_cult,
            "foreign_duration_years": round(foreign_duration, 1),
            "county_culture": ground_culture,
            "tier": 2,
            "tier_label": "Tier 2: Transitional Dynastic Rule",
            "adoption_pattern": "Hybrid Calque Allowed",
            "chancellery_action": "Dual Designation / Hybrid Calque Approved",
            "justification": f"Foreign {pre_conquest_cult} dynastic rule lasted only {foreign_duration:.1f} years (< 50 yrs) before conquest in {entry_date}. Indigenous scribal traditions intact; hybrid calque or dual designation approved.",
            "is_calquable": True,
        }

    # Case C: Foreign rule >= 50-100 years OR population converted -> TIER 3
    return {
        "canonical_key": candidate["canonical_key"],
        "mapped_ck3_key": key,
        "name": candidate["name"],
        "region": candidate["region"],
        "etym_group": candidate["etym_group"],
        "proposed_calque": candidate["proposed_calque"],
        "etym_breakdown": candidate["etym_breakdown"],
        "conquest_date": entry_date,
        "pre_conquest_ruler_culture": pre_conquest_cult,
        "foreign_duration_years": round(foreign_duration, 1),
        "county_culture": ground_culture,
        "tier": 3,
        "tier_label": "Tier 3: Complete Semantic Rupture",
        "adoption_pattern": "Strict Phonetic Nativization",
        "chancellery_action": "Strict Phonetic Token (Semantic Calque Relegated to Secondary Alternate)",
        "justification": f"Alien {pre_conquest_cult} rule persisted for {foreign_duration:.1f} years (>= 50 yrs) prior to conquest in {entry_date}. Original etymology suffered semantic rupture and is treated as an opaque phonetic token.",
        "is_calquable": False,
    }


# ==============================================================================
# 4. MARKDOWN AUDIT REGISTER COMPILER
# ==============================================================================

def generate_markdown_report(results: list, output_path: Path):
    """
    Compiles the exhaustive Markdown report detailing the Procedure 2 audit findings,
    grouped by Toponym Adoption Pattern.
    """
    tier1_items = [r for r in results if r["tier"] == 1]
    tier2_items = [r for r in results if r["tier"] == 2]
    tier3_items = [r for r in results if r["tier"] == 3]
    rule3_items = [r for r in results if r["tier"] == 4]

    md = []
    md.append("# Master Procedure 2 Audit Register: Title Calquability & Toponym Adoption Patterns")
    md.append("")
    md.append("> **Imperial Chancellery Toponymic Reference**  ")
    md.append(f"> **Date of Audit:** {time.strftime('%Y-%m-%d')} | **Game Horizon:** 1154.12.27 | **Ruleset:** Procedure 2 (§ 3.2 README)  ")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 1. Executive Summary & Audit Metrics")
    md.append("")
    md.append("To prevent armchair etymology and enforce realistic medieval scribal conventions, the **Imperial Chancellery** executes **Procedure 2 (Sovereign Cultural Lineage & Etymological Transparency Protocol)** across all candidate descriptive titles.")
    md.append("")
    md.append("Toponyms are classified into three distinct **Toponym Adoption Patterns** depending on whether the etymological meaning remained living, transitional, or suffered complete semantic rupture:")
    md.append("")
    md.append("| Toponym Adoption Pattern | Continuity Tier | Qualifying Condition in CK3 Sovereign History | Chancellery Outcome | Title Count |")
    md.append("| :--- | :--- | :--- | :--- | :---: |")
    md.append(f"| **Pattern 1: Preferred Semantic Calque** | **Tier 1: High Living Continuity** | Annexed directly from naming culture ruler OR unbroken native population | Full semantic translation adopted as primary name (*Stûlwîtzenburch*, *Wîtzenburch*) | **{len(tier1_items)}** |")
    md.append(f"| **Pattern 2: Hybrid Calque Allowed** | **Tier 2: Transitional Dynastic Rule** | Foreign rule lasted $< 50$ years AND local population intact | Dual designation: primary phonetic or hybrid with approved secondary calque (*Temeschburch*, *Calatajût*) | **{len(tier2_items)}** |")
    md.append(f"| **Pattern 3: Strict Phonetic Nativization** | **Tier 3: Complete Semantic Rupture** | Alien rule persisted $\\ge 50–100$ years OR population converted | Immutable phonetic token; semantic calque rejected as primary (*Tschongrât*, *Sevîlje*) | **{len(tier3_items)}** |")
    md.append(f"| **Rule 3: Calquing Prohibited** | **Control: Opaque Eponyms** | Personal names, tribal founders, or pre-Indo-European stems | Calquing strictly forbidden; pure phonetic adaptation (*Batsch*, *Bodroch*, *Parîs*) | **{len(rule3_items)}** |")
    md.append(f"| **Total Evaluated Titles** | — | — | — | **{len(results)}** |")
    md.append("")
    md.append("---")
    md.append("")

    # Section 2: Pattern 1
    md.append("## 2. Pattern 1: Preferred Semantic Calques (Tier 1: High Living Continuity)")
    md.append("")
    md.append("These titles were annexed **directly from rulers belonging to the etymological culture group**, or had **unbroken native populations**. Their descriptive meanings were actively understood in oral reports and local chancelleries. The Tarraconian Chancellery approves these calques as **official primary names** or authoritative established exonyms:")
    md.append("")
    md.append("| Title Key | Vanilla Title | Proposed Semantic Calque | Etymological Root | Pre-Conquest Sovereign | Annexation Date | Historical Justification |")
    md.append("| :--- | :--- | :--- | :--- | :--- | :---: | :--- |")
    for r in tier1_items:
        key_str = f"`{r['canonical_key']}`" + (f" (`{r['mapped_ck3_key']}`)" if r['canonical_key'] != r['mapped_ck3_key'] else "")
        md.append(f"| {key_str} | **{r['name']}** | **{r['proposed_calque']}** | *{r['etym_group']}*: {r['etym_breakdown']} | {r.get('pre_conquest_ruler_culture', 'Native')} | `{r.get('conquest_date', '867')}` | {r['justification']} |")
    md.append("")
    md.append("---")
    md.append("")

    # Section 3: Pattern 2
    md.append("## 3. Pattern 2: Hybrid Calques Allowed (Tier 2: Transitional Dynastic Rule)")
    md.append("")
    md.append("In these provinces, the ruler at conquest was foreign, but **foreign reign lasted $< 50$ years (1–2 generations)** while the indigenous scribal class and population remained unbroken. Both forms are recognized: the Chancellery authorizes **hybrid calques** (combining the indigenous stem with a Tarraconian generic) or **dual designations**:")
    md.append("")
    md.append("| Title Key | Vanilla Title | Authorized Hybrid / Calque | Etymological Root | Foreign Sovereign Duration | Annexation Date | Historical Justification |")
    md.append("| :--- | :--- | :--- | :--- | :---: | :---: | :--- |")
    for r in tier2_items:
        key_str = f"`{r['canonical_key']}`" + (f" (`{r['mapped_ck3_key']}`)" if r['canonical_key'] != r['mapped_ck3_key'] else "")
        md.append(f"| {key_str} | **{r['name']}** | **{r['proposed_calque']}** | *{r['etym_group']}*: {r['etym_breakdown']} | {r.get('pre_conquest_ruler_culture', 'Foreign')} ({r.get('foreign_duration_years', 0)} yrs) | `{r.get('conquest_date', '867')}` | {r['justification']} |")
    md.append("")
    md.append("---")
    md.append("")

    # Section 4: Pattern 3
    md.append("## 4. Pattern 3: Strict Phonetic Nativization (Tier 3: Complete Semantic Rupture)")
    md.append("")
    md.append("These provinces were held by alien cultures for **$\\ge 50$ to 100+ years**, or their local populations had converted away from the etymological culture before Tarraconian conquest. The original descriptive meaning is **lost in time**—the local court itself treated the name as an opaque phonetic token. **Full semantic calques are strictly rejected as official names**; Tarraconian scribes transcribe the phonetic form current at conquest, keeping calques only as parenthetical historical curiosities:")
    md.append("")
    md.append("| Title Key | Vanilla Title | Chancellery Phonetic Form | Deprecated Semantic Calque | Etymological Root | Alien Rule Duration | Rupture Justification |")
    md.append("| :--- | :--- | :--- | :--- | :--- | :---: | :--- |")
    for r in tier3_items:
        key_str = f"`{r['canonical_key']}`" + (f" (`{r['mapped_ck3_key']}`)" if r['canonical_key'] != r['mapped_ck3_key'] else "")
        md.append(f"| {key_str} | **{r['name']}** | `Magistrat van {r['canonical_key'].replace('c_', '').capitalize()}` | *{r['proposed_calque']}* | *{r['etym_group']}*: {r['etym_breakdown']} | {r.get('pre_conquest_ruler_culture', 'Alien')} ({r.get('foreign_duration_years', 0)} yrs) | {r['justification']} |")
    md.append("")
    md.append("---")
    md.append("")

    # Section 5: Rule 3 Opaque Eponyms
    md.append("## 5. Control Group: Opaque Eponyms & Tribal Roots (Rule 3 Enforcement)")
    md.append("")
    md.append("Per Section 6.3 of the Morpheme Guide, imperial scribes exercise strict restraint with opaque personal names, ancient tribal founders, and pre-Indo-European hydronyms. **Artificial semantic calques are strictly illicit**; titles must be preserved phonetically:")
    md.append("")
    md.append("| Title Key | Historical Title | Chancellery Phonetic Name | Origin & Category | Chancellery Ruling |")
    md.append("| :--- | :--- | :--- | :--- | :--- |")
    for r in rule3_items:
        md.append(f"| `{r['canonical_key']}` | **{r['name']}** | **{r['proposed_calque']}** | {r['etym_breakdown']} | ❌ **Calquing Prohibited** — Strictly Phonetic per Sound Laws |")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 6. Chancellery Synchronization Directives")
    md.append("1. **Update `tarraconian_titles_1059.md`:**")
    md.append("   - Ensure all **Pattern 1** titles carry their semantic calques as the primary official entry.")
    md.append("   - Format all **Pattern 2** titles as dual designations (*Phonetic primary with authorized hybrid/secondary calque*).")
    md.append("   - Enforce pure phonetic nativization for **Pattern 3** titles, relegating semantic calques to italicized historical glosses.")
    md.append("2. **Mod Synchronization (`build_mod.py`):**")
    md.append("   - Re-run `python3 scripts/build_mod.py` to regenerate `tarr_chancellery_title_list_effects.txt` and `tarraconian_titles_l_english.yml`.")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    log(f"Markdown audit register written to: {output_path}")


# ==============================================================================
# 5. MAIN ENTRYPOINT
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Procedure 2: Sovereign Cultural Lineage & Title Calquability Audit")
    parser.add_argument("--phase1-dir", default="/var/tmp/ck3_audit/phase1", help="Path to Phase 1 JSON directory")
    parser.add_argument("--phase2-dir", default="/var/tmp/ck3_audit/phase2", help="Path to Phase 2 JSON directory")
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parser.add_argument("--output-json", default=os.path.join(repo_root, "procedure2_calque_audit.json"), help="Path to output JSON")
    parser.add_argument("--output-md", default=os.path.join(repo_root, "tarraconian_procedure2_title_audit.md"), help="Path to output Markdown report")
    args = parser.parse_args()

    phase1_dir = Path(args.phase1_dir)
    phase2_dir = Path(args.phase2_dir)
    output_json = Path(args.output_json)
    output_md = Path(args.output_md)

    log("Starting Procedure 2 Sovereign Lineage & Calquability Audit...")

    # Load datasets
    titles_file = phase1_dir / "titles_data.json"
    cultures_file = phase1_dir / "cultures_data.json"
    trajs_file = phase2_dir / "county_lineage_trajectories.json"

    if not titles_file.is_file() or not cultures_file.is_file() or not trajs_file.is_file():
        log(f"Error: Missing input datasets in {phase1_dir} or {phase2_dir}")
        sys.exit(1)

    with open(titles_file, "r", encoding="utf-8") as f:
        titles_data = json.load(f)
    with open(cultures_file, "r", encoding="utf-8") as f:
        cultures_data = json.load(f)
    with open(trajs_file, "r", encoding="utf-8") as f:
        trajs_list = json.load(f)

    trajs_map = {t["county_key"]: t for t in trajs_list}
    log(f"Loaded {len(titles_data)} titles, {len(cultures_data)} cultures, and {len(trajs_map)} trajectories.")

    # Execute Procedure 2 on candidate titles
    results = []
    for cand in CANDIDATE_TITLES:
        res = evaluate_procedure2(cand, titles_data, trajs_map, cultures_data)
        results.append(res)

    log(f"Audited {len(results)} candidate titles across 14 geographic zones.")

    # Write JSON results
    output_json.parent.mkdir(parents=True, exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    log(f"Machine-readable JSON saved to: {output_json}")

    # Write Markdown Register
    generate_markdown_report(results, output_md)

    # Print summary
    tier1_c = sum(1 for r in results if r["tier"] == 1)
    tier2_c = sum(1 for r in results if r["tier"] == 2)
    tier3_c = sum(1 for r in results if r["tier"] == 3)
    rule3_c = sum(1 for r in results if r["tier"] == 4)

    print("\n" + "="*70)
    print("PROCEDURE 2 AUDIT SUMMARY: TOPONYM ADOPTION PATTERNS")
    print("="*70)
    print(f"Pattern 1 (Tier 1: Preferred Semantic Calque):   {tier1_c} titles")
    print(f"Pattern 2 (Tier 2: Hybrid Calque Allowed):        {tier2_c} titles")
    print(f"Pattern 3 (Tier 3: Strict Phonetic Nativization): {tier3_c} titles")
    print(f"Rule 3 (Control: Opaque Eponyms - No Calquing):   {rule3_c} titles")
    print(f"Total Audited Candidates:                         {len(results)} titles")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()

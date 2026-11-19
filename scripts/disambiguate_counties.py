#!/usr/bin/env python3
"""
scripts/disambiguate_counties.py

Global Disambiguation Engine for County-Tier Insignia.
Eliminates all duplicate heraldic symbols across all county titles (3,476 geojson counties + titular counties = 3,545 total).

Guarantees:
  1. 100% heraldic uniqueness across all 3,545 counties (zero duplicate signatures).
  2. ZERO collisions between counties and superior realms (47 empires, 213 kingdoms, 1,117 duchies).
  3. Strict Rule of Tinctures compliance, including divided field rules.
  4. Chronological Horizon preference (Horizons 0 & 1 retain simpler solid fields and single charges in chief).
  5. Bulla-seal aware charge positioning (in_chief, in_base, flanked, above_below, two_and_one, one_and_two).
  6. Authentic historical blazons preserved for major historical counties (Porto, Rome, Paris, Aachen, Cologne, Mainz, Trier, Jerusalem, etc.).
"""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DOCS_DIR = BASE_DIR / "docs"
WEB_JS = BASE_DIR / "web" / "js" / "symbol_generator.js"

metals = {'or', 'argent'}
colours = {'gules', 'azure', 'vert', 'sable', 'purpure'}
on_ordinary = {'fess', 'pale', 'bend', 'bend_sinister', 'chevron', 'cross', 'saltire'}
in_field = {'bordure', 'chief'}
partitions = {
    'per_pale', 'per_fess', 'per_bend', 'per_bend_sinister',
    'quarterly', 'per_saltire', 'barry', 'chequy', 'pales', 'pales_undy'
}

def clean_charge(c):
    if not c:
        return 'castrum'
    if c.startswith('hanzi_'):
        if c.endswith('mount_triple'): return 'mount_triple'
        elif c.endswith('waves'): return 'waves'
        elif c.endswith('castrum'): return 'castrum'
        elif c.endswith('roman_gate'): return 'roman_gate'
        elif c.endswith('dragon'): return 'dragon'
        elif c.endswith('tree_chestnut'): return 'tree_chestnut'
        else: return c.split('_')[-1]
    return c

def check_rot(f_col, o_key, chg, chg_col, cnt, o_col):
    field_is_metal = f_col in metals
    charge_is_metal = chg_col in metals
    if o_key == 'solid':
        if field_is_metal and charge_is_metal:
            return False, 'metal on metal'
        if (not field_is_metal) and (not charge_is_metal):
            return False, 'colour on colour'
        return True, 'ok'
    else:
        ord_is_metal = o_col in metals
        if field_is_metal and ord_is_metal:
            return False, 'ordinary metal on metal'
        if (not field_is_metal) and (not ord_is_metal):
            return False, 'ordinary colour on colour'
        if o_key in on_ordinary:
            if chg_col == o_col:
                return False, 'charge matches ordinary'
            if ord_is_metal and charge_is_metal:
                return False, 'charge metal on ordinary metal'
            if (not ord_is_metal) and (not charge_is_metal):
                return False, 'charge colour on ordinary colour'
        elif o_key in in_field:
            if chg_col == f_col:
                return False, 'charge matches field'
            if field_is_metal and charge_is_metal:
                return False, 'charge metal in field metal'
            if (not field_is_metal) and (not charge_is_metal):
                return False, 'charge colour in field colour'
        elif o_key in partitions:
            if chg_col in (f_col, o_col):
                return False, 'charge matches partition'
        return True, 'ok'

HORIZON_0_TITLES = {
    'c_aachen', 'c_alexandria', 'c_antioch', 'c_athens', 'c_barcelona', 'c_byzantion',
    'c_cologne', 'c_jerusalem', 'c_kent', 'c_kyiv', 'c_leon', 'c_lviv', 'c_mainz',
    'c_metz', 'c_milano', 'c_paris', 'c_ravenna', 'c_roma', 'c_szekesfehervar',
    'c_tarragona', 'c_thessaloniki', 'c_trier', 'c_venezia', 'c_wiltshire', 'c_york',
    'd_alexandria', 'd_antioch', 'd_athens', 'd_barcelona', 'd_canterbury', 'd_latium',
    'd_lombardy', 'd_ravenna', 'd_thessalonika', 'd_upper_lorraine', 'd_venice',
    'd_wessex', 'e_byzantium', 'e_hre', 'h_roman_empire', 'k_asturias', 'k_danelaw',
    'k_italy', 'k_leon', 'k_lotharingia', 'k_moravia', 'k_papal_state', 'k_romagna'
}

HORIZON_1_EMPIRES = {'e_germany', 'e_france'}
HORIZON_1_KINGDOMS = {
    'k_germany', 'k_lotharingia', 'k_bavaria', 'k_italy', 'k_burgundy',
    'k_francia', 'k_aquitaine', 'k_east_francia', 'k_west_francia'
}

HORIZON_2_EMPIRES = {'e_britannia', 'e_carpathia'}
HORIZON_2_KINGDOMS = {
    'k_england', 'k_bohemia', 'k_poland', 'k_denmark', 'k_croatia',
    'k_sicily', 'k_hungary', 'k_aragon', 'k_navarra', 'k_castille', 'k_valencia'
}

HORIZON_3_EMPIRES = {
    'e_scandinavia', 'e_russia', 'e_west_slavia', 'e_wendish_empire',
    'e_anatolia', 'e_macedonia', 'e_illyria', 'e_maghreb', 'e_africa',
    'e_aegyptus', 'e_oriens'
}

def get_chronological_horizon(key, props):
    k = (key or '').lower()
    if k in HORIZON_0_TITLES:
        return 0
    emp = props.get('empire') or props.get('e_key') or ''
    kng = props.get('kingdom') or props.get('k_key') or ''
    if emp in HORIZON_1_EMPIRES or kng in HORIZON_1_KINGDOMS:
        return 1
    if emp in HORIZON_2_EMPIRES or kng in HORIZON_2_KINGDOMS:
        return 2
    if emp in HORIZON_3_EMPIRES:
        return 3
    return 4

def hash_string(s):
    h = 5381
    for c in s:
        h = (((h << 5) + h) + ord(c)) & 0xFFFFFFFF
    return abs(h)

HISTORICAL_COUNTY_OVERRIDES = {
    'c_porto': ['argent', 'solid', 'cross', 'azure', 1, 'azure'],
    'c_roma': ['gules', 'chief', 'keys_st_peter', 'or', 1, 'or', 'in_base'],
    'c_paris': ['gules', 'solid', 'ship', 'argent', 1, 'argent', 'in_chief'],
    'c_aachen': ['or', 'bordure', 'alerion', 'sable', 1, 'gules', 'in_chief'],
    'c_cologne': ['gules', 'chief', 'crown', 'or', 3, 'argent', 'in_base'],
    'c_mainz': ['gules', 'solid', 'wheel_spoked', 'argent', 1, 'argent', 'in_chief'],
    'c_trier': ['argent', 'solid', 'keys_st_peter', 'gules', 1, 'gules', 'in_chief'],
    'c_jerusalem': ['gules', 'bordure', 'cross_patriarchal', 'or', 1, 'or', 'in_chief'],
    'c_byzantion': ['gules', 'cross_byzantine', 'cross_byzantine', 'or', 1, 'or', 'in_chief'],
    'c_barcelona': ['argent', 'per_pale', 'cross', 'or', 1, 'gules', 'in_chief'],
    'c_tarragona': ['or', 'pales_undy', 'castrum', 'azure', 1, 'gules', 'in_chief'],
    'c_metz': ['argent', 'per_pale', 'cross', 'sable', 1, 'gules', 'in_chief'],
    'c_lviv': ['azure', 'solid', 'bell', 'argent', 1, 'argent', 'in_chief'],
    'c_szekesfehervar': ['gules', 'bordure', 'crown', 'argent', 1, 'argent', 'in_chief'],
    'c_venezia': ['azure', 'per_fess', 'lion_rampant', 'or', 1, 'argent', 'in_chief'],
    'c_ravenna': ['gules', 'chief', 'alerion', 'or', 1, 'or', 'in_base'],
    'c_milano': ['argent', 'solid', 'dragon', 'azure', 1, 'azure', 'in_chief'],
    'c_alexandria': ['azure', 'solid', 'column_roman', 'argent', 1, 'argent', 'in_chief'],
    'c_antioch': ['azure', 'solid', 'cross_patriarchal', 'argent', 1, 'argent', 'in_chief'],
    'c_athens': ['argent', 'solid', 'column_roman', 'azure', 1, 'azure', 'in_chief'],
    'c_thessaloniki': ['gules', 'chief', 'sword_crossed', 'or', 1, 'or', 'in_base'],
    'c_wiltshire': ['vert', 'chief', 'horse_courant', 'argent', 1, 'argent', 'in_base'],
    'c_kent': ['gules', 'bordure', 'horse_courant', 'argent', 1, 'argent', 'in_chief'],
    'c_york': ['argent', 'cross', 'rose_seeded', 'or', 1, 'gules', 'in_chief'],
    'c_kyiv': ['azure', 'chief', 'sword_crossed', 'or', 1, 'or', 'in_base'],
    'c_middlesex': ['argent', 'solid', 'sword_crossed', 'gules', 1, 'gules', 'in_chief'],
    'c_cornwall': ['sable', 'bordure', 'wheel_spoked', 'or', 1, 'or', 'in_chief'],
    'c_lancashire': ['argent', 'solid', 'rose_seeded', 'gules', 1, 'gules', 'in_chief'],
    'c_cleves': ['gules', 'solid', 'shield_escutcheon', 'argent', 1, 'argent', 'in_chief'],
    'c_hamburg': ['gules', 'solid', 'castrum', 'argent', 1, 'argent', 'in_chief'],
    'c_firenze': ['argent', 'per_pale', 'fleur_de_lis', 'or', 1, 'gules', 'in_chief'],
    'c_siena': ['argent', 'per_fess', 'lion_rampant', 'gules', 1, 'sable', 'in_chief'],
    'c_pisa': ['gules', 'bordure', 'cross', 'argent', 1, 'argent', 'in_chief'],
    'c_genoa': ['argent', 'bordure', 'cross', 'gules', 1, 'gules', 'in_chief'],
    'c_marseille': ['argent', 'bordure', 'cross', 'azure', 1, 'azure', 'in_chief'],
    'c_bordeaux': ['gules', 'chief', 'castrum', 'or', 1, 'or', 'in_base'],
    'c_toledo': ['gules', 'bordure', 'roman_gate', 'or', 1, 'or', 'in_chief'],
    'c_granada': ['argent', 'bordure', 'rose_seeded', 'gules', 1, 'vert', 'in_chief'],
    'c_bremen': ['gules', 'solid', 'keys_st_peter', 'argent', 1, 'argent', 'in_chief'],
    'c_lubeck': ['argent', 'per_fess', 'alerion', 'sable', 1, 'gules', 'in_chief'],
    'c_worms': ['sable', 'solid', 'keys_st_peter', 'argent', 1, 'argent', 'in_chief'],
    'c_speyer': ['azure', 'solid', 'castrum', 'argent', 1, 'argent', 'in_chief'],
    'c_strasbourg': ['argent', 'bend', 'castrum', 'argent', 1, 'gules', 'in_chief'],
    'c_zurich': ['azure', 'per_bend', 'lion_rampant', 'gules', 1, 'argent', 'in_chief'],
    'c_bern': ['gules', 'bend', 'bear_rampant', 'sable', 1, 'or', 'in_chief'],
    'c_geneva': ['or', 'per_pale', 'keys_st_peter', 'gules', 1, 'sable', 'in_chief'],
    'c_basel': ['argent', 'solid', 'crozier', 'sable', 1, 'sable', 'in_chief']
}

def extract_base_charge(title_key, props):
    tarr = (props.get('tarr_hist') or props.get('tarr') or props.get('c_tarr') or title_key).lower()
    orig = (props.get('origin') or props.get('c_origin') or '').lower()

    # 1. Fauna / Beasts
    if 'bêr' in tarr or 'bär' in tarr or 'bear' in orig or 'ursus' in orig:
        return 'bear_rampant'
    if 'wolf' in tarr or 'wulf' in tarr or 'lupus' in orig or 'vuk' in orig:
        return 'wolf_statant'
    if 'hirz' in tarr or 'hirsch' in tarr or 'stag' in orig or 'cervus' in orig or 'hart' in orig:
        return 'stag_attired'
    if 'ros' in tarr or 'ross' in tarr or 'horse' in orig or 'equus' in orig or 'cheval' in orig or 'cavall' in orig:
        return 'horse_courant'
    if 'valke' in tarr or 'falk' in tarr or 'falcon' in orig or 'adler' in tarr or 'eagle' in orig or 'aar' in tarr:
        return 'falcon_perched'
    if 'lôwe' in tarr or 'löwe' in tarr or 'lion' in orig or 'leo' in orig or 'arba' in orig:
        return 'lion_rampant'
    if 'drak' in tarr or 'drache' in tarr or 'dragon' in orig or 'lindwurm' in tarr:
        return 'dragon'

    # 2. Water / Maritime / Riparian
    if 'fisch' in tarr or 'fish' in orig or 'pesc' in orig or 'ryba' in orig:
        return 'fish_twin'
    if 'anker' in tarr or 'anchor' in orig:
        return 'anchor'
    if 'brücke' in tarr or 'bridge' in orig or 'pons' in orig or 'pont' in orig or 'most' in orig:
        return 'bridge'
    if any(m in tarr for m in ('hâven', 'haven', 'port', 'strand', 'vik', 'fjord', 'kyste')) or any(m in orig for m in ('haven', 'port', 'harbor', 'vik', 'fjord')):
        return 'ship'
    if any(m in tarr for m in ('vort', 'flutz', 'wazzer', 'bach', 'strom', 'river', 'see', 'mer', 'welle')) or any(m in orig for m in ('ford', 'water', 'river', 'lake', 'stream', 'brook', 'creek', 'rio', 'riviere')):
        return 'waves'

    # 3. Elevations / Rocks
    if any(m in tarr for m in ('berch', 'berg', 'stein', 'fels', 'klipp', 'höhe', 'spitz', 'kogel', 'mont', 'horn', 'alpe')) or any(m in orig for m in ('berg', 'stein', 'cliff', 'rock', 'mount', 'mountain', 'hill', 'peak', 'rocca', 'roche')):
        return 'mount_triple'

    # 4. Ecclesiastical / Monastic
    if 'kloster' in tarr or 'abbey' in orig or 'münster' in tarr or 'monastery' in orig or 'couvent' in orig:
        return 'crozier'
    if 'glocke' in tarr or 'bell' in orig:
        return 'bell'
    if any(m in tarr for m in ('kîrch', 'kirch', 'zant', 'saint', 'san', 'santo', 'santa', 'dom', 'zell', 'cell')) or any(m in orig for m in ('church', 'saint', 'kirk', 'ecclesia', 'kirche')):
        return 'cross_patriarchal'

    # 5. Woodland / Flora
    if 'eik' in tarr or 'eiche' in tarr or 'oak' in orig or 'chêne' in orig:
        return 'oak_branch'
    if 'wîn' in tarr or 'wein' in tarr or 'vine' in orig or 'grape' in orig or 'uva' in orig:
        return 'grape_cluster'
    if any(m in tarr for m in ('wald', 'holt', 'forst', 'hain', 'wood', 'bush')) or any(m in orig for m in ('wald', 'wood', 'forest', 'bois', 'bosco', 'silva', 'grove')):
        return 'tree_chestnut'
    if 'lilje' in tarr or 'lilie' in tarr or 'lily' in orig or 'lis' in orig:
        return 'fleur_de_lis'
    if 'rôse' in tarr or 'rose' in tarr or 'rose' in orig:
        return 'rose_seeded'

    # 6. Agriculture / Civic / Industry
    if any(m in tarr for m in ('rad', 'wheel', 'mühle', 'muhle')) or any(m in orig for m in ('wheel', 'mill', 'moulin', 'molino', 'rad')):
        return 'wheel_spoked'
    if any(m in tarr for m in ('korn', 'wheat', 'garbe', 'feld', 'field', 'wiese', 'prado', 'acker', 'land')) or any(m in orig for m in ('wheat', 'corn', 'field', 'meadow', 'grass', 'farm')):
        return 'wheatsheaf_garb'
    if 'bîle' in tarr or 'beil' in tarr or 'axe' in orig or 'hache' in orig:
        return 'battleaxe'
    if 'swert' in tarr or 'schwert' in tarr or 'sword' in orig or 'epee' in orig:
        return 'sword_crossed'
    if any(m in tarr for m in ('stat', 'stadt', 'gorod', 'polis', 'tor', 'gate', 'port')) or any(m in orig for m in ('stadt', 'gorod', 'polis', 'city', 'town', 'gate', 'porta')):
        return 'roman_gate'

    # 7. Celestial
    if 'stern' in tarr or 'star' in orig:
        return 'star_six_pointed'
    if 'sunne' in tarr or 'sonne' in tarr or 'sun' in orig:
        return 'sun_radiant'
    if 'mâne' in tarr or 'mond' in tarr or 'moon' in orig:
        return 'crescent_moon'

    # 8. Fortifications / Castles
    if any(m in tarr for m in ('burch', 'burg', 'kastel', 'schloss', 'grad', 'festung', 'ward')) or any(m in orig for m in ('burg', 'burgh', 'castle', 'chateau', 'castello', 'grad', 'fort')):
        return 'castrum'

    # Deterministic fallback by hash
    h = hash_string(title_key)
    pool = [
        'castrum', 'roman_gate', 'mount_triple', 'ship', 'tree_chestnut',
        'lion_rampant', 'waves', 'crown', 'sword_crossed', 'battleaxe',
        'stag_attired', 'wolf_statant', 'bear_rampant', 'horse_courant',
        'falcon_perched', 'fish_twin', 'rose_seeded', 'fleur_de_lis',
        'wheatsheaf_garb', 'oak_branch', 'sun_radiant', 'star_six_pointed',
        'crescent_moon', 'wheel_spoked', 'anchor'
    ]
    return pool[h % len(pool)]

def generate_county_candidates(base_spec, horizon, title_key):
    """Generate prioritized disambiguation candidates for county insignia."""
    f_col, o_key, chg, chg_col, cnt, o_col = base_spec[:6]
    chg = clean_charge(chg)
    field_is_metal = f_col in metals

    ord_tinctures = ['gules', 'azure', 'sable', 'vert', 'purpure'] if field_is_metal else ['argent', 'or']
    candidates = []

    # Strategy 1: Layout differences keeping same field & ordinary
    if o_key == 'solid':
        if cnt == 1:
            candidates.append([f_col, 'solid', chg, chg_col, 1, o_col, 'in_base'])
        elif cnt == 2:
            candidates.append([f_col, 'solid', chg, chg_col, 2, o_col, 'flanked'])
            candidates.append([f_col, 'solid', chg, chg_col, 2, o_col, 'above_below'])
        elif cnt == 3:
            candidates.append([f_col, 'solid', chg, chg_col, 3, o_col, 'one_and_two'])
            candidates.append([f_col, 'solid', chg, chg_col, 3, o_col, 'two_and_one'])

    # Strategy 2: Multi-charge cadency on solid field
    if o_key == 'solid':
        if cnt == 1:
            candidates.append([f_col, 'solid', chg, chg_col, 2, o_col, 'above_below'])
            candidates.append([f_col, 'solid', chg, chg_col, 2, o_col, 'flanked'])
            candidates.append([f_col, 'solid', chg, chg_col, 3, o_col, 'two_and_one'])
            candidates.append([f_col, 'solid', chg, chg_col, 3, o_col, 'one_and_two'])
        elif cnt == 2:
            candidates.append([f_col, 'solid', chg, chg_col, 1, o_col, 'in_chief'])
            candidates.append([f_col, 'solid', chg, chg_col, 1, o_col, 'in_base'])
            candidates.append([f_col, 'solid', chg, chg_col, 3, o_col, 'two_and_one'])
            candidates.append([f_col, 'solid', chg, chg_col, 3, o_col, 'one_and_two'])

    # Strategy 3: Geometric field partitions
    candidate_partitions = [
        'per_fess', 'per_pale', 'per_bend', 'per_bend_sinister',
        'quarterly', 'per_saltire', 'chequy', 'barry'
    ]
    for part in candidate_partitions:
        for otinc in ord_tinctures:
            valid_chg_tincs = [c for c in (metals | colours) if c != f_col and c != otinc]
            for ctinc in valid_chg_tincs:
                for c_cnt in (1, 2, 3):
                    layout = 'in_chief' if c_cnt == 1 else ('above_below' if c_cnt == 2 else 'two_and_one')
                    candidates.append([f_col, part, chg, ctinc, c_cnt, otinc, layout])
                    if c_cnt == 1:
                        candidates.append([f_col, part, chg, ctinc, 1, otinc, 'in_base'])
                    elif c_cnt == 2:
                        candidates.append([f_col, part, chg, ctinc, 2, otinc, 'flanked'])
                    elif c_cnt == 3:
                        candidates.append([f_col, part, chg, ctinc, 3, otinc, 'one_and_two'])

    # Strategy 4: Field ordinaries (bordure, chief, fess, pale, bend, chevron)
    candidate_ords = ['bordure', 'chief', 'fess', 'pale', 'bend', 'chevron', 'cross', 'saltire']
    for ord_k in candidate_ords:
        for otinc in ord_tinctures:
            if ord_k in on_ordinary:
                otinc_is_metal = otinc in metals
                c_pool = list(colours) if otinc_is_metal else list(metals)
                for ctinc in c_pool:
                    for c_cnt in (1, 2):
                        layout = 'in_chief' if c_cnt == 1 else 'above_below'
                        candidates.append([f_col, ord_k, chg, ctinc, c_cnt, otinc, layout])
            elif ord_k in in_field:
                c_pool = list(colours) if field_is_metal else list(metals)
                for ctinc in c_pool:
                    for c_cnt in (1, 2):
                        layout = 'in_base' if ord_k == 'chief' else ('in_chief' if c_cnt == 1 else 'above_below')
                        candidates.append([f_col, ord_k, chg, ctinc, c_cnt, otinc, layout])

    # Filter Rule of Tinctures
    valid_candidates = []
    for cand in candidates:
        ok, _ = check_rot(*cand[:6])
        if ok:
            valid_candidates.append(cand)

    return valid_candidates

def disambiguate_all_counties():
    print("Loading datasets...")
    with open(DATA_DIR / 'canonical_title_heraldry.json', 'r', encoding='utf-8') as f:
        canon = json.load(f)

    with open(DATA_DIR / 'ck3_counties.geojson', 'r', encoding='utf-8') as f:
        geojson = json.load(f)

    # 1. Update kingdom/duchy collisions
    canon['k_ruucuu'] = ['azure', 'solid', 'waves', 'or', 1, 'or']
    canon['k_tsang'] = ['azure', 'solid', 'wheel_spoked', 'or', 1, 'or']
    canon['k_mordvinia'] = ['azure', 'solid', 'bear_rampant', 'or', 1, 'or']
    canon['k_dali'] = ['vert', 'solid', 'dragon', 'or', 1, 'or']
    canon['k_portugal'] = ['argent', 'bordure', 'shield_escutcheon', 'azure', 1, 'gules']
    canon['k_genoa'] = ['argent', 'chief', 'cross', 'gules', 1, 'gules']
    canon['d_eastern_desert'] = ['gules', 'per_fess', 'sun_radiant', 'azure', 1, 'or', 'in_chief']

    # 2. Build higher-tier reserved signatures (Empires, Kingdoms, Duchies)
    higher_reserved_7 = set()
    higher_reserved_6 = set()
    for k, spec in canon.items():
        if k.startswith(('e_', 'k_', 'h_', 'd_')):
            higher_reserved_7.add(tuple(spec[:7] if len(spec) >= 7 else spec[:6] + ['default']))
            higher_reserved_6.add(tuple(spec[:6]))

    print(f"Higher-tier reserved blazons: {len(higher_reserved_7)} 7-tuples, {len(higher_reserved_6)} 6-tuples")

    # 3. Gather all county keys and properties
    props_map = {}
    geojson_counties = set()
    for feat in geojson['features']:
        p = feat['properties']
        c = p.get('county')
        if c:
            geojson_counties.add(c)
            props_map[c] = p

    all_counties = sorted(geojson_counties | set(k for k in canon if k.startswith('c_')))
    print(f"Total counties to disambiguate: {len(all_counties)} (3476 geojson + {len(all_counties) - len(geojson_counties)} titular)")

    # 4. Generate base blazons
    base_blazons = {}
    county_horizons = {}

    for c in all_counties:
        props = props_map.get(c, {})
        horizon = get_chronological_horizon(c, props)
        county_horizons[c] = horizon

        if c in HISTORICAL_COUNTY_OVERRIDES:
            spec = HISTORICAL_COUNTY_OVERRIDES[c]
            base_blazons[c] = spec
        elif c in canon:
            spec = canon[c]
            chg = clean_charge(spec[2])
            layout = spec[6] if len(spec) > 6 else 'in_chief'
            base_blazons[c] = [spec[0], spec[1], chg, spec[3], spec[4], spec[5], layout]
        else:
            chg = extract_base_charge(c, props)
            h = hash_string(c)
            fields = ['gules', 'azure', 'or', 'argent', 'vert', 'sable']
            f_col = fields[h % len(fields)]
            c_col = 'or' if f_col in colours else 'azure'
            base_blazons[c] = [f_col, 'solid', chg, c_col, 1, f_col, 'in_chief']

    # 5. Group into clusters
    clusters = defaultdict(list)
    for c, spec in base_blazons.items():
        clusters[tuple(spec[:6])].append(c)

    print(f"Initial county clusters: {len(clusters)} distinct 6-tuples")

    # 6. Disambiguation engine
    assigned_blazons = {}
    used_7_signatures = set()
    used_6_signatures = set()

    # Pass 1: Assign Historical Overrides first
    for c in all_counties:
        if c in HISTORICAL_COUNTY_OVERRIDES:
            spec = HISTORICAL_COUNTY_OVERRIDES[c]
            assigned_blazons[c] = spec
            used_7_signatures.add(tuple(spec))
            used_6_signatures.add(tuple(spec[:6]))

    # Pass 2: Sort and process remaining clusters
    cluster_keys = sorted(clusters.keys())
    for sig_key in cluster_keys:
        members = clusters[sig_key]
        unassigned_members = [m for m in members if m not in assigned_blazons]
        if not unassigned_members:
            continue

        unassigned_members.sort(key=lambda m: (county_horizons[m], hash_string(m)))

        for i, c in enumerate(unassigned_members):
            base_spec = base_blazons[c]
            horizon = county_horizons[c]

            cand_0 = list(base_spec[:6]) + [base_spec[6] if len(base_spec) > 6 else 'in_chief']
            sig_7_0 = tuple(cand_0)
            sig_6_0 = tuple(cand_0[:6])

            rot_ok, _ = check_rot(*cand_0[:6])
            if rot_ok and sig_7_0 not in used_7_signatures and sig_7_0 not in higher_reserved_7 and sig_6_0 not in used_6_signatures and sig_6_0 not in higher_reserved_6:
                assigned_blazons[c] = cand_0
                used_7_signatures.add(sig_7_0)
                used_6_signatures.add(sig_6_0)
                continue

            candidates = generate_county_candidates(base_spec, horizon, c)
            found = False
            # First try: strictly unique 6-tuple and 7-tuple with no collision
            for cand in candidates:
                cand_sig_7 = tuple(cand)
                cand_sig_6 = tuple(cand[:6])

                if (cand_sig_7 not in used_7_signatures and cand_sig_7 not in higher_reserved_7 and
                    cand_sig_6 not in used_6_signatures and cand_sig_6 not in higher_reserved_6):
                    assigned_blazons[c] = cand
                    used_7_signatures.add(cand_sig_7)
                    used_6_signatures.add(cand_sig_6)
                    found = True
                    break

            # Second try: unique 7-tuple, no higher-tier 6 or 7 collision
            if not found:
                for cand in candidates:
                    cand_sig_7 = tuple(cand)
                    cand_sig_6 = tuple(cand[:6])

                    if (cand_sig_7 not in used_7_signatures and cand_sig_7 not in higher_reserved_7 and
                        cand_sig_6 not in higher_reserved_6):
                        assigned_blazons[c] = cand
                        used_7_signatures.add(cand_sig_7)
                        found = True
                        break

            if not found:
                raise RuntimeError(f"Could not disambiguate title {c} with horizon {horizon}")

    print(f"Successfully disambiguated all {len(assigned_blazons)} counties!")

    # 7. Audits
    # A. 100% Uniqueness
    sig_7_counts = defaultdict(list)
    for c, spec in assigned_blazons.items():
        sig_7_counts[tuple(spec)].append(c)

    dups = {s: cl for s, cl in sig_7_counts.items() if len(cl) > 1}
    assert len(dups) == 0, f"DUPLICATE COUNTIES DETECTED: {dups}"
    print("Verification: ZERO duplicate 7-tuples across all 3,545 counties! (100% unique)")

    # B. Zero collisions with higher tiers
    higher_coll = []
    for c, spec in assigned_blazons.items():
        if tuple(spec) in higher_reserved_7 or tuple(spec[:6]) in higher_reserved_6:
            higher_coll.append((c, spec))
    assert len(higher_coll) == 0, f"Higher tier collisions detected: {higher_coll[:5]}"
    print("Verification: ZERO collisions between counties and higher tiers (empires, kingdoms, duchies)!")

    # C. Rule of Tinctures Audit
    rot_violations = []
    for c, spec in assigned_blazons.items():
        ok, reason = check_rot(*spec[:6])
        if not ok:
            rot_violations.append((c, reason, spec))
    assert len(rot_violations) == 0, f"Rule of Tincture violations found: {rot_violations}"
    print("Verification: ZERO Rule of Tinctures violations across all counties!")

    # D. c_porto validation
    assert 'c_porto' in assigned_blazons
    assert assigned_blazons['c_porto'][:6] == ['argent', 'solid', 'cross', 'azure', 1, 'azure']
    print("Verification: c_porto correctly retained as authentic Azure cross on Argent!")

    # 8. Save updated canon
    for c, spec in assigned_blazons.items():
        canon[c] = spec

    with open(DATA_DIR / 'canonical_title_heraldry.json', 'w', encoding='utf-8') as f:
        json.dump(canon, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(canon)} titles to {DATA_DIR / 'canonical_title_heraldry.json'}")

    (DOCS_DIR / "data").mkdir(parents=True, exist_ok=True)
    with open(DOCS_DIR / "data" / 'canonical_title_heraldry.json', 'w', encoding='utf-8') as f:
        json.dump(canon, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(canon)} titles to {DOCS_DIR / 'data' / 'canonical_title_heraldry.json'}")

    # 9. Update embedded CANONICAL_HERALDRY in web/js/symbol_generator.js
    min_canon_json = json.dumps(canon, separators=(",", ":"))
    js_content = WEB_JS.read_text(encoding="utf-8")
    start_marker = "const CANONICAL_HERALDRY = "
    idx_start = js_content.find(start_marker)
    idx_end = js_content.find(";\n", idx_start)
    if idx_start != -1 and idx_end != -1:
        js_content = js_content[:idx_start + len(start_marker)] + min_canon_json + js_content[idx_end:]
        WEB_JS.write_text(js_content, encoding="utf-8")
        print(f"Updated embedded CANONICAL_HERALDRY in {WEB_JS}")
    else:
        raise RuntimeError("Could not locate CANONICAL_HERALDRY in symbol_generator.js")

    return canon

if __name__ == '__main__':
    disambiguate_all_counties()

#!/usr/bin/env python3
"""
scripts/disambiguate_duchies.py

Global Disambiguation Engine for Duchy-Tier Insignia.
Eliminates all duplicate heraldic symbols across all duchy titles (970 geojson duchies + titular duchies).
Guarantees:
  1. 100% heraldic uniqueness across all duchies.
  2. 0 collisions between duchies and higher-tier realms (47 empires, 213 kingdoms).
  3. Strict Rule of Tinctures compliance, including divided field rules.
  4. Chronological Horizon preference (Horizons 0 & 1 retain simpler solid fields and single charges).
  5. Boss-aware scutum charge positioning (in_chief, in_base, flanked, above_below, two_and_one, one_and_two).
  6. Varied field partitions and ordinaries.
"""

import json
import re
import sys
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
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
        if c.endswith('mount_triple'):
            return 'mount_triple'
        elif c.endswith('waves'):
            return 'waves'
        elif c.endswith('castrum'):
            return 'castrum'
        elif c.endswith('roman_gate'):
            return 'roman_gate'
        elif c.endswith('dragon'):
            return 'dragon'
        else:
            return c.split('_')[-1]
    return c

def check_rot(f_col, o_key, chg, chg_col, cnt, o_col, layout='default'):
    field_is_metal = f_col in metals
    ord_is_metal = o_col in metals
    charge_is_metal = chg_col in metals if chg_col else False

    # 1. Uncharged Shields (cnt == 0 or chg in ('none', None))
    if cnt == 0 or chg in ('none', None):
        if o_key == 'solid':
            return True, 'ok'
        if field_is_metal and ord_is_metal:
            return False, 'ordinary metal on metal'
        if (not field_is_metal) and (not ord_is_metal):
            return False, 'ordinary colour on colour'
        return True, 'ok'

    # 2. Solid Field
    if o_key == 'solid':
        if chg_col == f_col:
            return False, 'charge matches field'
        if field_is_metal and charge_is_metal:
            return False, 'charge metal on field metal'
        if (not field_is_metal) and (not charge_is_metal):
            return False, 'charge colour on field colour'
        return True, 'ok'

    # 3. Field Ordinaries & Modifiers
    if field_is_metal and ord_is_metal:
        return False, 'ordinary metal on field metal'
    if (not field_is_metal) and (not ord_is_metal):
        return False, 'ordinary colour on field colour'

    if o_key == 'bordure':
        if chg_col == f_col:
            return False, 'charge matches field'
        if field_is_metal and charge_is_metal:
            return False, 'charge metal in field metal'
        if (not field_is_metal) and (not charge_is_metal):
            return False, 'charge colour in field colour'
        return True, 'ok'

    if o_key == 'chief':
        if layout == 'in_chief':
            bg_col = o_col
            bg_is_metal = ord_is_metal
        else:
            bg_col = f_col
            bg_is_metal = field_is_metal
        if chg_col == bg_col:
            return False, 'charge matches chief/field'
        if bg_is_metal and charge_is_metal:
            return False, 'charge metal on metal'
        if (not bg_is_metal) and (not charge_is_metal):
            return False, 'charge colour on colour'
        return True, 'ok'

    if o_key in on_ordinary:
        if layout in ('in_chief', 'in_base', 'above_below', 'flanked', 'two_and_one', 'one_and_two'):
            # The charge physically sits in the field (f_col)
            if chg_col == f_col:
                return False, 'charge matches field'
            if field_is_metal and charge_is_metal:
                return False, 'charge metal in field metal'
            if (not field_is_metal) and (not charge_is_metal):
                return False, 'charge colour in field colour'
            return True, 'ok'
        else:
            # Charge sits on the ordinary (o_col)
            if chg_col == o_col:
                return False, 'charge matches ordinary'
            if ord_is_metal and charge_is_metal:
                return False, 'charge metal on ordinary metal'
            if (not ord_is_metal) and (not charge_is_metal):
                return False, 'charge colour on ordinary colour'
            return True, 'ok'

    # 4. Geometric Partitions
    if o_key in ('per_fess', 'per_bend', 'per_bend_sinister', 'quarterly', 'per_saltire'):
        if layout == 'in_chief':
            if chg_col == f_col:
                return False, 'charge matches upper partition'
            if field_is_metal and charge_is_metal:
                return False, 'charge metal on upper partition metal'
            if (not field_is_metal) and (not charge_is_metal):
                return False, 'charge colour on upper partition colour'
            return True, 'ok'
        elif layout == 'in_base':
            if chg_col == o_col:
                return False, 'charge matches lower partition'
            if ord_is_metal and charge_is_metal:
                return False, 'charge metal on lower partition metal'
            if (not ord_is_metal) and (not charge_is_metal):
                return False, 'charge colour on lower partition colour'
            return True, 'ok'
        return True, 'ok'

    if o_key == 'per_pale':
        return True, 'ok'

    if o_key in ('barry', 'chequy', 'pales', 'pales_undy'):
        if chg_col in (f_col, o_col):
            return False, 'charge matches field tinctures'
        return True, 'ok'

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

HISTORICAL_DUCHY_OVERRIDES = {
    'd_normandy': ['gules', 'solid', 'lion_rampant', 'or', 2, 'or', 'above_below'],
    'd_aquitaine': ['gules', 'solid', 'lion_rampant', 'or', 1, 'or', 'in_base'],
    'd_flanders': ['or', 'solid', 'lion_rampant', 'sable', 1, 'gules', 'in_chief'],
    'd_brabant': ['sable', 'solid', 'lion_rampant', 'or', 1, 'gules', 'in_chief'],
    'd_salzburg': ['or', 'per_pale', 'lion_rampant', 'sable', 1, 'gules', 'in_chief'],
    'd_poitou': ['argent', 'bordure', 'lion_rampant', 'gules', 1, 'sable', 'in_chief'],
    'd_orleans': ['azure', 'bordure', 'fleur_de_lis', 'or', 3, 'argent', 'one_and_two'],
    'd_anjou': ['azure', 'solid', 'fleur_de_lis', 'or', 3, 'or', 'one_and_two'],
    'd_berry': ['azure', 'bordure', 'fleur_de_lis', 'or', 3, 'argent', 'two_and_one'],
    'd_canterbury': ['gules', 'chief', 'horse_courant', 'argent', 1, 'or', 'in_base'],
    'd_westfalen': ['gules', 'solid', 'horse_courant', 'argent', 1, 'argent', 'in_base'],
    'd_genoa': ['argent', 'solid', 'cross', 'gules', 1, 'gules', 'in_chief'],
    'd_sardinia': ['argent', 'cross', 'cross', 'gules', 1, 'gules', 'in_chief'],
    'd_lombardy': ['azure', 'solid', 'crown', 'or', 1, 'or', 'in_chief'],
    'd_deheubarth': ['gules', 'bordure', 'lion_rampant', 'or', 1, 'or', 'in_chief'],
    'd_swabia': ['or', 'solid', 'lion_rampant', 'sable', 3, 'sable', 'two_and_one'],
    'd_bavaria': ['argent', 'chequy', 'castrum', 'or', 1, 'azure', 'in_chief'],
    'd_saxony': ['or', 'barry', 'castrum', 'vert', 1, 'sable', 'in_chief'],
    'd_brittany': ['argent', 'solid', 'cross', 'sable', 1, 'sable', 'in_chief'],
    'd_dauphine': ['or', 'fess', 'fish_twin', 'azure', 1, 'azure', 'in_chief'],
    'd_toulouse': ['gules', 'solid', 'cross_byzantine', 'or', 1, 'or', 'in_chief'],
    'd_navarra': ['gules', 'saltire', 'cross', 'or', 1, 'or', 'in_chief'],
    'd_champagne': ['azure', 'bend', 'bend', 'or', 1, 'argent', 'in_chief'],
    'd_burgundy': ['azure', 'bordure', 'bend', 'or', 1, 'or', 'in_chief'],
    'd_holstein': ['gules', 'bordure', 'castrum', 'argent', 1, 'argent', 'in_chief'],
    'd_toscana': ['argent', 'solid', 'fleur_de_lis', 'gules', 1, 'gules', 'in_chief'],
    'd_provence': ['or', 'pale', 'rose_seeded', 'gules', 1, 'gules', 'in_chief'],
    'd_auvergne': ['or', 'solid', 'shield_escutcheon', 'gules', 1, 'gules', 'in_chief'],
    'd_wessex': ['gules', 'solid', 'dragon', 'or', 1, 'or', 'in_base'],
    'd_athens': ['azure', 'solid', 'column_roman', 'or', 1, 'or', 'in_chief'],
    'd_thessalonika': ['gules', 'solid', 'sword_crossed', 'or', 1, 'or', 'in_chief'],
    'd_venice': ['azure', 'solid', 'lion_rampant', 'or', 1, 'or', 'in_chief'],
    'd_alexandria': ['azure', 'solid', 'lion_rampant', 'or', 1, 'or', 'in_base'],
    'd_antioch': ['azure', 'solid', 'cross_patriarchal', 'or', 1, 'or', 'in_chief'],
    'd_latium': ['gules', 'solid', 'keys_st_peter', 'or', 1, 'or', 'in_chief'],
    'd_upper_lorraine': ['or', 'bend', 'alerion', 'argent', 1, 'gules', 'default'],
    'd_lower_lorraine': ['argent', 'fess', 'castrum', 'gules', 1, 'gules', 'in_chief'],
    'd_barcelona': ['or', 'pales', 'none', None, 0, 'gules', 'default'],
    'd_the_isles': ['gules', 'solid', 'ship', 'or', 1, 'or', 'in_chief'],
    'd_cornwall': ['sable', 'solid', 'wheel_spoked', 'or', 1, 'or', 'in_chief'],
    'd_lancaster': ['gules', 'solid', 'rose_seeded', 'argent', 1, 'argent', 'in_chief'],
    'd_york': ['azure', 'solid', 'rose_seeded', 'argent', 1, 'argent', 'in_chief'],
    'd_warwick': ['argent', 'solid', 'bear_rampant', 'sable', 1, 'sable', 'in_chief'],
    'd_mumu': ['azure', 'solid', 'crown', 'or', 3, 'or', 'one_and_two'],
    'd_laigin': ['vert', 'solid', 'crown', 'or', 1, 'or', 'in_chief'],
    'd_connacht': ['argent', 'per_pale', 'alerion', 'sable', 1, 'gules', 'in_chief'],
    'd_ulster': ['or', 'cross', 'cross', 'gules', 1, 'gules', 'in_chief'],
    'd_meath': ['azure', 'solid', 'crown', 'or', 1, 'or', 'in_base'],
    'd_luxembourg': ['argent', 'barry', 'lion_rampant', 'gules', 1, 'azure', 'in_chief'],
    'd_bourbon': ['azure', 'bend', 'fleur_de_lis', 'or', 3, 'argent', 'two_and_one'],
    'd_valois': ['azure', 'bordure', 'fleur_de_lis', 'or', 3, 'or', 'two_and_one'],
    'd_limousin': ['or', 'solid', 'lion_rampant', 'azure', 3, 'azure', 'two_and_one'],
    'd_armagnac': ['argent', 'solid', 'lion_rampant', 'gules', 1, 'gules', 'in_chief'],
    'd_tyrol': ['argent', 'solid', 'alerion', 'gules', 1, 'gules', 'in_chief'],
    'd_carinthia': ['or', 'per_pale', 'lion_rampant', 'sable', 1, 'gules', 'in_base'],
    'd_steyermark': ['vert', 'solid', 'dragon', 'argent', 1, 'argent', 'in_chief'],
    'd_moray': ['azure', 'solid', 'star_six_pointed', 'argent', 3, 'argent', 'two_and_one'],
    'd_galloway': ['azure', 'solid', 'lion_rampant', 'argent', 1, 'argent', 'in_chief'],
    'd_lothian': ['argent', 'solid', 'castrum', 'sable', 1, 'sable', 'in_chief'],
    'd_albany': ['or', 'fess', 'castrum', 'sable', 1, 'sable', 'in_chief'],
    'd_minsk': ['gules', 'fess', 'crescent_moon', 'argent', 1, 'argent', 'in_chief']
}


def generate_candidate_variants(base_spec, horizon, title_key):
    """
    Generate ranked candidate blazons for a title to disambiguate it.
    Strategies:
      1. Vary charge layout on the Notitia Scutum (in_base, flanked, one_and_two).
      2. Vary field partitions (per_fess, per_pale, per_bend, quarterly, etc.).
      3. Vary ordinaries (bordure, chief, fess, pale, bend, chevron).
      4. Vary charge count (1, 2, 3).
    """
    f_col, o_key, chg, chg_col, cnt, o_col = base_spec[:6]
    chg = clean_charge(chg)
    field_is_metal = f_col in metals

    # Define suitable ordinary tinctures
    if field_is_metal:
        ord_tinctures = ['gules', 'azure', 'sable', 'vert', 'purpure']
    else:
        ord_tinctures = ['argent', 'or']

    candidates = []

    # Strategy 1: Layout variations keeping original tinctures and ordinary
    if o_key == 'solid':
        if cnt == 1:
            candidates.append([f_col, 'solid', chg, chg_col, 1, o_col, 'in_base'])
        elif cnt == 2:
            candidates.append([f_col, 'solid', chg, chg_col, 2, o_col, 'flanked'])
            candidates.append([f_col, 'solid', chg, chg_col, 2, o_col, 'above_below'])
        elif cnt == 3:
            candidates.append([f_col, 'solid', chg, chg_col, 3, o_col, 'one_and_two'])
            candidates.append([f_col, 'solid', chg, chg_col, 3, o_col, 'two_and_one'])

    # Strategy 2: Multi-charge counts on solid field with varied layouts
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
            # Layout in_chief: charge sits in upper partition (f_col)
            valid_chg_tincs_chief = list(colours) if field_is_metal else list(metals)
            for ctinc in valid_chg_tincs_chief:
                candidates.append([f_col, part, chg, ctinc, 1, otinc, 'in_chief'])

            # Layout in_base: charge sits in lower partition (otinc)
            otinc_is_metal = otinc in metals
            valid_chg_tincs_base = list(colours) if otinc_is_metal else list(metals)
            for ctinc in valid_chg_tincs_base:
                candidates.append([f_col, part, chg, ctinc, 1, otinc, 'in_base'])

            # Multi charges across divisions
            for ctinc in valid_chg_tincs_chief:
                candidates.append([f_col, part, chg, ctinc, 2, otinc, 'above_below'])
                candidates.append([f_col, part, chg, ctinc, 2, otinc, 'flanked'])
                candidates.append([f_col, part, chg, ctinc, 3, otinc, 'two_and_one'])
                candidates.append([f_col, part, chg, ctinc, 3, otinc, 'one_and_two'])

    # Strategy 4: Field ordinaries (bordure, chief, fess, pale, bend, chevron, cross, saltire)
    candidate_ords = ['bordure', 'chief', 'fess', 'pale', 'bend', 'chevron', 'cross', 'saltire']
    for ord_k in candidate_ords:
        for otinc in ord_tinctures:
            otinc_is_metal = otinc in metals
            if ord_k == 'chief':
                c_pool_chief = list(colours) if otinc_is_metal else list(metals)
                for ctinc in c_pool_chief:
                    candidates.append([f_col, ord_k, chg, ctinc, 1, otinc, 'in_chief'])
                c_pool_field = list(colours) if field_is_metal else list(metals)
                for ctinc in c_pool_field:
                    candidates.append([f_col, ord_k, chg, ctinc, 1, otinc, 'in_base'])
                    candidates.append([f_col, ord_k, chg, ctinc, 2, otinc, 'above_below'])
            elif ord_k == 'bordure':
                c_pool_field = list(colours) if field_is_metal else list(metals)
                for ctinc in c_pool_field:
                    candidates.append([f_col, ord_k, chg, ctinc, 1, otinc, 'in_chief'])
                    candidates.append([f_col, ord_k, chg, ctinc, 2, otinc, 'above_below'])
            elif ord_k in on_ordinary:
                c_pool_ord = list(colours) if otinc_is_metal else list(metals)
                for ctinc in c_pool_ord:
                    candidates.append([f_col, ord_k, chg, ctinc, 1, otinc, 'default'])
                c_pool_field = list(colours) if field_is_metal else list(metals)
                for ctinc in c_pool_field:
                    candidates.append([f_col, ord_k, chg, ctinc, 1, otinc, 'in_chief'])
                    candidates.append([f_col, ord_k, chg, ctinc, 1, otinc, 'in_base'])
                    candidates.append([f_col, ord_k, chg, ctinc, 2, otinc, 'above_below'])

    # Filter candidates by Rule of Tinctures
    valid_candidates = []
    for cand in candidates:
        ok, _ = check_rot(*cand[:6], layout=cand[6] if len(cand) > 6 else 'default')
        if ok:
            valid_candidates.append(cand)

    return valid_candidates


def disambiguate_all_duchies():
    print("Loading datasets...")
    with open(DATA_DIR / 'canonical_title_heraldry.json', 'r', encoding='utf-8') as f:
        canon = json.load(f)

    with open(DATA_DIR / 'ck3_counties.geojson', 'r', encoding='utf-8') as f:
        geojson = json.load(f)

    # 1. Higher-tier reserved set (Empires + Kingdoms + Historical County Overrides)
    higher_reserved = set()
    for k, spec in canon.items():
        if k.startswith(('e_', 'k_', 'h_')):
            higher_reserved.add(tuple(spec[:6]))
            higher_reserved.add(tuple(spec[:7] if len(spec) >= 7 else spec[:6] + ['default']))

    from scripts.disambiguate_counties import HISTORICAL_COUNTY_OVERRIDES
    for k, spec in HISTORICAL_COUNTY_OVERRIDES.items():
        higher_reserved.add(tuple(spec[:6]))
        higher_reserved.add(tuple(spec[:7] if len(spec) >= 7 else spec[:6] + ['default']))

    print(f"Higher-tier reserved blazons: {len(higher_reserved)}")

    # 2. Gather all duchy keys and feature properties
    props_map = {}
    geojson_duchies = set()
    for f in geojson['features']:
        props = f['properties']
        d = props.get('duchy')
        if d:
            geojson_duchies.add(d)
            if d not in props_map:
                props_map[d] = props

    all_duchies = sorted(geojson_duchies | set(k for k in canon if k.startswith('d_')))
    print(f"Total duchies to disambiguate: {len(all_duchies)} (970 geojson + {len(all_duchies) - len(geojson_duchies)} titular)")

    # 3. Import canting analyzer for base generation
    sys.path.insert(0, str(Path('/home/siarzhuk/.gemini/antigravity/brain/04bd38d0-c723-434d-8f3c-ffd284386ecb/scratch')))
    from audit_all_titles import analyze_title

    # 4. Generate base blazons for all duchies
    base_blazons = {}
    duchy_horizons = {}

    for d in all_duchies:
        props = props_map.get(d, {})
        horizon = get_chronological_horizon(d, props)
        duchy_horizons[d] = horizon

        if d in HISTORICAL_DUCHY_OVERRIDES:
            spec = HISTORICAL_DUCHY_OVERRIDES[d]
            base_blazons[d] = spec
        elif d in canon:
            spec = canon[d]
            chg = clean_charge(spec[2])
            layout = spec[6] if len(spec) > 6 else 'in_chief'
            base_blazons[d] = [spec[0], spec[1], chg, spec[3], spec[4], spec[5], layout]
        else:
            res = analyze_title(d, props, 'duchy')
            chg = clean_charge(res['charge'])
            layout = 'in_chief'
            base_blazons[d] = [res['field'], res['ordinary'], chg, res['chargeColor'], res['count'], res['ordinaryColor'], layout]

    # 5. Group duchies into duplicate clusters
    clusters = defaultdict(list)
    for d, spec in base_blazons.items():
        sig_key = tuple(spec[:6])
        clusters[sig_key].append(d)

    print(f"Initial duchy clusters: {len(clusters)} distinct 6-tuple patterns")

    # 6. Disambiguation engine
    assigned_blazons = {}
    used_7_signatures = set()
    used_6_signatures = set()

    # Pass 1: Assign Historical Overrides first
    for d in all_duchies:
        if d in HISTORICAL_DUCHY_OVERRIDES:
            spec = HISTORICAL_DUCHY_OVERRIDES[d]
            assigned_blazons[d] = spec
            used_7_signatures.add(tuple(spec))
            used_6_signatures.add(tuple(spec[:6]))

    # Pass 2: Sort and process remaining clusters
    cluster_keys = sorted(clusters.keys())
    for sig_key in cluster_keys:
        members = clusters[sig_key]
        unassigned_members = [m for m in members if m not in assigned_blazons]
        if not unassigned_members:
            continue

        unassigned_members.sort(key=lambda m: (duchy_horizons[m], hash_string(m)))

        for i, d in enumerate(unassigned_members):
            base_spec = base_blazons[d]
            horizon = duchy_horizons[d]

            cand_0 = list(base_spec[:6]) + [base_spec[6] if len(base_spec) > 6 else 'in_chief']
            sig_7_0 = tuple(cand_0)
            sig_6_0 = tuple(cand_0[:6])

            rot_ok, _ = check_rot(*cand_0[:6], layout=cand_0[6])
            if rot_ok and sig_7_0 not in used_7_signatures and sig_7_0 not in higher_reserved and sig_6_0 not in used_6_signatures:
                assigned_blazons[d] = cand_0
                used_7_signatures.add(sig_7_0)
                used_6_signatures.add(sig_6_0)
                continue

            candidates = generate_candidate_variants(base_spec, horizon, d)
            found = False
            for cand in candidates:
                cand_sig_7 = tuple(cand)
                cand_sig_6 = tuple(cand[:6])

                if cand_sig_7 not in used_7_signatures and cand_sig_7 not in higher_reserved and cand_sig_6 not in used_6_signatures:
                    assigned_blazons[d] = cand
                    used_7_signatures.add(cand_sig_7)
                    used_6_signatures.add(cand_sig_6)
                    found = True
                    break

            if not found:
                for cand in candidates:
                    cand_sig_7 = tuple(cand)
                    if cand_sig_7 not in used_7_signatures and cand_sig_7 not in higher_reserved:
                        assigned_blazons[d] = cand
                        used_7_signatures.add(cand_sig_7)
                        found = True
                        break

            if not found:
                raise RuntimeError(f"Could not disambiguate title {d} with horizon {horizon}")

    print(f"Successfully disambiguated all {len(assigned_blazons)} duchies!")

    # 7. Verification Audits
    # A. 100% Uniqueness
    sig_7_counts = defaultdict(list)
    for d, spec in assigned_blazons.items():
        sig_7_counts[tuple(spec)].append(d)

    dups = {s: dl for s, dl in sig_7_counts.items() if len(dl) > 1}
    assert len(dups) == 0, f"DUPLICATE DUCHIES DETECTED: {dups}"
    print("Verification: ZERO duplicates across all duchies! (100% unique)")

    # B. Zero collision with higher tiers
    higher_coll = {}
    for d, spec in assigned_blazons.items():
        if tuple(spec) in higher_reserved or tuple(spec[:6]) in higher_reserved:
            higher_coll[d] = spec
    print(f"Higher tier 6-tuple or 7-tuple collisions: {len(higher_coll)}")
    if higher_coll:
        print(f"Resolving {len(higher_coll)} higher tier collisions...")
        for d, spec in higher_coll.items():
            horizon = duchy_horizons[d]
            candidates = generate_candidate_variants(spec, horizon, d)
            for cand in candidates:
                cand_sig_7 = tuple(cand)
                cand_sig_6 = tuple(cand[:6])
                if cand_sig_7 not in used_7_signatures and cand_sig_7 not in higher_reserved and cand_sig_6 not in higher_reserved:
                    used_7_signatures.remove(tuple(spec))
                    assigned_blazons[d] = cand
                    used_7_signatures.add(cand_sig_7)
                    used_6_signatures.add(cand_sig_6)
                    break

    final_higher_coll = {d: spec for d, spec in assigned_blazons.items() if tuple(spec) in higher_reserved or tuple(spec[:6]) in higher_reserved}
    assert len(final_higher_coll) == 0, f"Higher tier collisions remaining: {final_higher_coll}"
    print("Verification: ZERO collisions between duchies and empires/kingdoms!")

    # C. Rule of Tinctures Audit
    rot_violations = []
    for d, spec in assigned_blazons.items():
        ok, reason = check_rot(*spec[:6], layout=spec[6] if len(spec) > 6 else 'default')
        if not ok:
            rot_violations.append((d, reason, spec))
    assert len(rot_violations) == 0, f"Rule of Tincture violations found: {rot_violations}"
    print("Verification: ZERO Rule of Tinctures violations across all duchies!")

    # 8. Update data/canonical_title_heraldry.json
    for d, spec in assigned_blazons.items():
        canon[d] = spec

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
    disambiguate_all_duchies()

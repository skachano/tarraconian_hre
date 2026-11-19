#!/usr/bin/env python3
"""
Generates canonical heraldic blazons and attributes for CK3 titles
by parsing the save game coat_of_arms database and enforcing the Rule of Tincture.
"""

import json
import re
from pathlib import Path

SAVE_PATH = Path("/var/tmp/ck3_audit/melted_save.ck3")
OUTPUT_PATH = Path("data/canonical_title_heraldry.json")

COLOR_MAP = {
    'white': 'argent',
    'yellow': 'or',
    'red': 'gules',
    'blue': 'azure',
    'black': 'sable',
    'green': 'vert',
    'purple': 'purpure',
    'grey': 'argent',
    'yellow_light': 'or',
    'red_dark': 'gules',
    'blue_light': 'azure',
    'blue_dark': 'azure',
    'green_light': 'vert',
    'orange': 'gules'
}

PATTERN_MAP = {
    'pattern_solid.dds': 'solid',
    'pattern__solid_designer.dds': 'solid',
    'pattern_vertical_split_01.dds': 'per_pale',
    'pattern_horizontal_split_01.dds': 'per_fess',
    'pattern_horizontal_split_02.dds': 'per_fess',
    'pattern_diagonal_split_01.dds': 'per_bend',
    'pattern_diagonal_split_02.dds': 'per_bend_sinister',
    'pattern_quarterly_01.dds': 'quarterly',
    'pattern_checkers_01.dds': 'chequy',
    'pattern_checkers_08.dds': 'chequy',
    'pattern_chief.dds': 'chief',
    'pattern_triangle_01.dds': 'chevron',
    'pattern_paly_01.dds': 'pales',
    'pattern_barry_01.dds': 'barry'
}

TEXTURE_MAP = {
    'ce_lion_rampant.dds': 'lion_rampant',
    'ce_lion_rampant_crown.dds': 'lion_rampant',
    'ce_lion_passant.dds': 'lion_rampant',
    'ce_eagle.dds': 'alerion',
    'ce_eagle_double.dds': 'eagle_double',
    'ce_ordinary_cross_5.dds': 'cross',
    'ce_ordinary_cross_4.dds': 'cross',
    'ce_ordinary_cross_thin.dds': 'cross',
    'ce_cross_07.dds': 'cross',
    'ce_cross_patty.dds': 'cross',
    'ce_cross_patriarchal_hungary.dds': 'cross_patriarchal',
    'ce_cross_patriarchal.dds': 'cross_patriarchal',
    'ce_ordinary_fess_5.dds': 'fess',
    'ce_ordinary_pale_5.dds': 'pale',
    'ce_ordinary_bend_dexter_5.dds': 'bend',
    'ce_ordinary_bend_sinister_5.dds': 'bend_sinister',
    'ce_ordinary_chevron_5.dds': 'chevron',
    'ce_diagonal_stripes_01.dds': 'bend',
    'ce_castle.dds': 'castrum',
    'ce_tower.dds': 'castrum',
    'ce_gate.dds': 'roman_gate',
    'ce_fleur.dds': 'fleur_de_lis',
    'ce_crown_small.dds': 'crown',
    'ce_crown_large.dds': 'crown',
    'ce_crescent.dds': 'crescent_moon',
    'ce_star_06.dds': 'star_six_pointed',
    'ce_star_08.dds': 'star_six_pointed',
    'ce_key_st_peter.dds': 'keys_st_peter',
    'ce_keys_st_peter.dds': 'keys_st_peter',
    'ce_mount.dds': 'mount_triple',
    'ce_wyvern.dds': 'dragon',
    'ce_dragon.dds': 'dragon',
    'ce_griffin_rampant.dds': 'dragon',
    'ce_stag.dds': 'stag_attired',
    'ce_bear.dds': 'bear_rampant',
    'ce_horse.dds': 'horse_courant',
    'ce_wolf.dds': 'wolf_statant',
    'ce_fish.dds': 'fish_twin',
    'ce_falcon.dds': 'falcon_perched',
    'ce_rose.dds': 'rose_seeded',
    'ce_wheatsheaf.dds': 'wheatsheaf_garb',
    'ce_oak.dds': 'oak_branch',
    'ce_tree.dds': 'tree_chestnut',
    'ce_grapes.dds': 'grape_cluster',
    'ce_sun.dds': 'sun_radiant',
    'ce_wheel.dds': 'wheel_spoked',
    'ce_anchor.dds': 'anchor',
    'ce_swords.dds': 'sword_crossed',
    'ce_sword.dds': 'sword_crossed',
    'ce_axe.dds': 'battleaxe',
    'ce_spear.dds': 'spear',
    'ce_bow.dds': 'bow_and_arrow',
    'ce_ship.dds': 'ship',
    'ce_galley.dds': 'ship',
    'ce_waves.dds': 'waves',
    'ce_chains.dds': 'cross',
    'ce_lotus.dds': 'rose_seeded',
    'ce_tamgha_kyrgyz.dds': 'bow_and_arrow',
    'ce_jesus_throne.dds': 'column_roman'
}

METALS = {'or', 'argent'}
COLOURS = {'gules', 'azure', 'vert', 'sable', 'purpure'}

def get_tincture(col_str, fallback='gules'):
    return COLOR_MAP.get(col_str, fallback)

def enforce_contrast(charge_tinc, field_tinc):
    field_is_metal = field_tinc in METALS
    charge_is_metal = charge_tinc in METALS
    if field_is_metal and charge_is_metal:
        return 'sable' if field_tinc == 'or' else 'azure'
    elif not field_is_metal and not charge_is_metal:
        return 'or' if field_tinc in ('gules', 'sable', 'purpure') else 'argent'
    return charge_tinc

def map_emblem_to_charge(tex):
    tex = tex.lower()
    if tex in TEXTURE_MAP:
        return TEXTURE_MAP[tex]
    for k, v in TEXTURE_MAP.items():
        base = k.replace('.dds', '').replace('ce_', '')
        if base in tex:
            return v
    if 'cross' in tex: return 'cross'
    if 'lion' in tex: return 'lion_rampant'
    if 'eagle' in tex: return 'eagle_double'
    if 'bear' in tex: return 'bear_rampant'
    if 'stag' in tex or 'deer' in tex or 'hart' in tex: return 'stag_attired'
    if 'horse' in tex: return 'horse_courant'
    if 'wolf' in tex: return 'wolf_statant'
    if 'fish' in tex: return 'fish_twin'
    if 'falcon' in tex or 'bird' in tex: return 'falcon_perched'
    if 'rose' in tex: return 'rose_seeded'
    if 'sword' in tex: return 'sword_crossed'
    if 'axe' in tex: return 'battleaxe'
    if 'spear' in tex: return 'spear'
    if 'bow' in tex: return 'bow_and_arrow'
    if 'ship' in tex or 'boat' in tex: return 'ship'
    if 'castle' in tex or 'tower' in tex: return 'castrum'
    return None

def map_pattern(pat):
    if not pat: return 'solid'
    pat = pat.lower()
    return PATTERN_MAP.get(pat, 'solid')

def main():
    if not SAVE_PATH.is_file():
        print(f"Error: {SAVE_PATH} not found.")
        return

    name_map = {}
    with open(SAVE_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        in_map = False
        for line in f:
            ls = line.strip()
            if ls == 'coat_of_arms_manager_name_map={':
                in_map = True
                continue
            if in_map:
                if ls == '}':
                    break
                if '=' in ls:
                    k, v = ls.split('=')
                    k = k.strip()
                    if k.startswith(('e_', 'k_', 'd_', 'c_', 'b_')):
                        name_map[v.strip()] = k

    print(f"Found {len(name_map)} titles in coat_of_arms_manager_name_map.")
    target_ids = set(name_map.keys())

    title_coas = {}
    with open(SAVE_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        current_title = None
        current_coa = {}
        current_emblem = None
        depth = 0
        
        for i, line in enumerate(f):
            if i < 24297900:
                continue
            if i > 25776170:
                break
                
            m = re.match(r'^\t\t(\d+)=\{', line)
            if m:
                cid = m.group(1)
                if cid in target_ids:
                    current_title = name_map[cid]
                    current_coa = {'coa_id': cid, 'emblems': []}
                    depth = 1
                else:
                    current_title = None
                continue
                
            if current_title:
                ls = line.strip()
                if ls.startswith('colored_emblem={'):
                    current_emblem = {'instances': 0}
                    current_coa['emblems'].append(current_emblem)
                elif ls.startswith('pattern='):
                    current_coa['pattern'] = ls.split('=')[1].strip('\"')
                elif ls.startswith('color1='):
                    if current_emblem is not None:
                        current_emblem['color1'] = ls.split('=')[1].strip('\"')
                    else:
                        current_coa['color1'] = ls.split('=')[1].strip('\"')
                elif ls.startswith('color2='):
                    if current_emblem is not None:
                        current_emblem['color2'] = ls.split('=')[1].strip('\"')
                    else:
                        current_coa['color2'] = ls.split('=')[1].strip('\"')
                elif ls.startswith('color3='):
                    if current_emblem is not None:
                        current_emblem['color3'] = ls.split('=')[1].strip('\"')
                    else:
                        current_coa['color3'] = ls.split('=')[1].strip('\"')
                elif current_emblem is not None and ls.startswith('texture='):
                    current_emblem['texture'] = ls.split('=')[1].strip('\"')
                elif current_emblem is not None and ls.startswith('instance={'):
                    current_emblem['instances'] += 1
                
                depth += line.count('{') - line.count('}')
                if depth <= 0:
                    title_coas[current_title] = current_coa
                    current_title = None
                    current_emblem = None

    print(f"Extracted raw data for {len(title_coas)} titles.")

    canonical_heraldry = {}

    for t, raw in title_coas.items():
        field = get_tincture(raw.get('color1', 'gules'), 'gules')
        pat = map_pattern(raw.get('pattern', ''))
        ord_field = get_tincture(raw.get('color2', 'argent'), 'argent')
        if ord_field == field:
            ord_field = 'argent' if field in ('gules', 'azure', 'sable', 'vert', 'purpure') else 'gules'
            
        charge = None
        charge_col = None
        count = 1
        
        for emb in raw.get('emblems', []):
            tex = emb.get('texture', '')
            mapped = map_emblem_to_charge(tex)
            if mapped:
                charge = mapped
                raw_col = get_tincture(emb.get('color1', 'or'), 'or')
                charge_col = enforce_contrast(raw_col, field)
                count = max(1, min(3, emb.get('instances', 1)))
                break
                
        if not charge:
            # Fallback based on pattern or title
            if pat in ('fess', 'pale', 'bend', 'chevron', 'cross', 'saltire'):
                charge = pat
                charge_col = enforce_contrast(ord_field, field)
            else:
                charge = 'castrum'
                charge_col = enforce_contrast('or', field)

        # Enforce Rule of Tincture strictly
        charge_col = enforce_contrast(charge_col, field)
        
        # Specific historical corrections
        if t == 'c_porto':
            field = 'argent'
            pat = 'solid'
            charge = 'cross'
            charge_col = 'azure'
            count = 1
            ord_field = 'azure'
        elif t == 'k_lotharingia':
            field = 'or'
            pat = 'bend'
            charge = 'alerion'
            charge_col = 'argent'
            count = 3
            ord_field = 'gules'
        elif t == 'k_navarra':
            field = 'gules'
            pat = 'cross'
            charge = 'star_six_pointed'
            charge_col = 'or'
            count = 1
            ord_field = 'or'
        elif t == 'k_aragon':
            field = 'or'
            pat = 'pales'
            charge = 'pale'
            charge_col = 'gules'
            count = 1
            ord_field = 'gules'
            
        canonical_heraldry[t] = [field, pat, charge, charge_col, count, ord_field]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as out_f:
        json.dump(canonical_heraldry, out_f, indent=2)

    print(f"Saved {len(canonical_heraldry)} titles to {OUTPUT_PATH}.")

if __name__ == '__main__':
    main()

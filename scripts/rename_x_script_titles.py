#!/usr/bin/env python3
"""
Renames the 25 dynamically generated 'X Script <num>' duchies to their
authentic, toponymic territorial names based on their constituent counties.
Updates:
1. hre_de_jure_and_archdioceses_1059.md
2. tarraconian_titles_1059.md
3. scripts/build_mod.py
"""

import re
import sys
from pathlib import Path

RENAME_MAP = {
    'x_script_2362': {
        'eng': 'Ulleong',
        'tarr': 'Ulleong',
        'county': 'c_ulleong'
    },
    'x_script_1315': {
        'eng': 'Dipalpur',
        'tarr': 'Dipalpur',
        'county': 'c_dipalpur'
    },
    'x_script_1553': {
        'eng': 'Aksu',
        'tarr': 'Aksu',
        'county': 'c_aksu'
    },
    'x_script_1250': {
        'eng': 'Vanda',
        'tarr': 'Wande',
        'county': 'c_eman_vanda'
    },
    'x_script_1439': {
        'eng': 'Choripi',
        'tarr': 'Tschoripi',
        'county': 'c_eman_choripi'
    },
    'x_script_2047': {
        'eng': 'Molihewen',
        'tarr': 'Molihewen',
        'county': 'c_eman_molihewen'
    },
    'x_script_2533': {
        'eng': 'Boli',
        'tarr': 'Boli',
        'county': 'c_eman_boli'
    },
    'x_script_2799': {
        'eng': 'Mohean',
        'tarr': 'Mohean',
        'county': 'c_eman_mohean'
    },
    'x_script_2924': {
        'eng': 'Yerenhe',
        'tarr': 'Jerenhe',
        'county': 'c_eman_yerenhe'
    },
    'x_script_1737': {
        'eng': 'Urehokto',
        'tarr': 'Urehoktô',
        'county': 'c_eman_urehokto'
    },
    'x_script_2388': {
        'eng': 'Urmi',
        'tarr': 'Urmi',
        'county': 'c_eman_urmi'
    },
    'x_script_1505': {
        'eng': 'Tsugaru',
        'tarr': 'Tsugaru',
        'county': 'c_tsugaru'
    },
    'x_script_2481': {
        'eng': 'Kaabu',
        'tarr': 'Kaabu',
        'county': 'c_kaabu'
    },
    'x_script_8046': {
        'eng': 'Chuguchak',
        'tarr': 'Tschugutschach',
        'county': 'c_chuguchak'
    },
    'x_script_1506': {
        'eng': 'Kilimanjaro',
        'tarr': 'Kilimanjarô',
        'county': 'c_kilimanjaro'
    },
    'x_script_1816': {
        'eng': 'Tanga',
        'tarr': 'Tange',
        'county': 'c_tanga'
    },
    'x_script_1894': {
        'eng': 'Kirinyaga',
        'tarr': 'Kirinyage',
        'county': 'c_kirinyaga'
    },
    'x_script_2263': {
        'eng': 'Galana',
        'tarr': 'Galane',
        'county': 'c_mto_galana'
    },
    'x_script_3608': {
        'eng': 'Pemba',
        'tarr': 'Pembe',
        'county': 'c_pemba'
    },
    'x_script_4892': {
        'eng': 'Gurgi',
        'tarr': 'Gurgi',
        'county': 'c_gurgi'
    },
    'x_script_3271': {
        'eng': 'Salamat',
        'tarr': 'Salamat',
        'county': 'c_salamat'
    },
    'x_script_1314': {
        'eng': 'Dadhipadra',
        'tarr': 'Dadhipadre',
        'county': 'c_dadhipadra'
    },
    'x_script_3406': {
        'eng': 'Ujjayini',
        'tarr': 'Ujjayini',
        'county': 'c_ujjayini'
    },
    'x_script_3434': {
        'eng': 'Dasapura',
        'tarr': 'Dasapure',
        'county': 'c_dasapura'
    },
    'x_script_2703': {
        'eng': 'Biun',
        'tarr': 'Biun',
        'county': 'c_biun'
    },
}

def main():
    repo_root = Path(__file__).resolve().parent.parent
    hre_path = repo_root / "hre_de_jure_and_archdioceses_1059.md"
    tarr_path = repo_root / "tarraconian_titles_1059.md"
    build_mod_path = repo_root / "scripts" / "build_mod.py"

    # 1. Update hre_de_jure_and_archdioceses_1059.md
    with open(hre_path, 'rb') as f:
        hre_raw = f.read()
    hre_is_crlf = b'\r\n' in hre_raw
    hre_text = hre_raw.decode('utf-8')

    hre_count = 0
    for k, data in RENAME_MAP.items():
        pat = re.compile(r'\*\s+\*\*Duchy of X Script \d+\*\*\s+\(`' + k + r'`\)')
        if pat.search(hre_text):
            hre_text = pat.sub(f"* **Duchy of {data['eng']}** (`{k}`)", hre_text, count=1)
            hre_count += 1

    with open(hre_path, 'wb') as f:
        newline = '\r\n' if hre_is_crlf else '\n'
        # Normalize newlines if needed
        hre_text = hre_text.replace('\r\n', '\n').replace('\n', newline)
        f.write(hre_text.encode('utf-8'))
    print(f"[HRE MD] Renamed {hre_count} / 25 duchies in {hre_path.name}")

    # 2. Update tarraconian_titles_1059.md
    with open(tarr_path, 'rb') as f:
        tarr_raw = f.read()
    tarr_is_crlf = b'\r\n' in tarr_raw
    tarr_text = tarr_raw.decode('utf-8')

    tarr_count = 0
    for k, data in RENAME_MAP.items():
        pat = re.compile(r'\*\s+\*\*Duchy of X Script \d+\*\*\s+\(`' + k + r'`\)\s+\$(?:\\rightarrow|ightarrow)\$\s+\*\*Gubernat van [^*]+\*\*')
        if pat.search(tarr_text):
            tarr_text = pat.sub(lambda m, k=k, d=data: f"* **Duchy of {d['eng']}** (`{k}`) $\\rightarrow$ **Gubernat van {d['tarr']}**", tarr_text, count=1)
            tarr_count += 1

    with open(tarr_path, 'wb') as f:
        newline = '\r\n' if tarr_is_crlf else '\n'
        tarr_text = tarr_text.replace('\r\n', '\n').replace('\n', newline)
        f.write(tarr_text.encode('utf-8'))
    print(f"[TARR MD] Renamed {tarr_count} / 25 duchies in {tarr_path.name}")

    # 3. Update build_mod.py
    with open(build_mod_path, 'r', encoding='utf-8') as f:
        build_text = f.read()

    # Build dynamic title lines
    dyn_lines = []
    for k, data in RENAME_MAP.items():
        c = data['county']
        dyn_lines.append(f'\t\ttitle:{c}.de_jure_liege ?= {{ tarr_rename_title_effect = {{ NAME = cn_tarr_{k} HIST = cn_tarr_{k} }} }}')

    dyn_block = '\n'.join([f'        "{l}",' for l in dyn_lines])

    target_anchor = '        "\\ttitle:c_vijnot.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_6239 HIST = cn_tarr_x_script_6239 } }",'
    if target_anchor in build_text and 'x_script_2362' not in build_text:
        replacement = target_anchor + '\n' + dyn_block
        build_text = build_text.replace(target_anchor, replacement, 1)
        with open(build_mod_path, 'w', encoding='utf-8') as f:
            f.write(build_text)
        print(f"[BUILD MOD] Added 25 dynamic duchy resolution lines into {build_mod_path.name}")
    else:
        print(f"[BUILD MOD] Anchor already modified or not found in {build_mod_path.name}")

if __name__ == '__main__':
    main()

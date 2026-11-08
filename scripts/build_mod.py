#!/usr/bin/env python3
"""
Tarraconian Chancellery - Mod Asset Build Pipeline
Replaces scripts/build_mod.ps1 with a cross-platform Python 3 implementation.

Reads master gazetteer `tarraconian_titles_1059.md` and generates:
1. `tarraconian_chancellery/common/scripted_effects/tarr_chancellery_title_list_effects.txt`
2. `tarraconian_chancellery/localization/english/tarraconian_titles_l_english.yml`

Preserves UTF-8 with BOM and Windows CRLF line endings.
"""

import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GAZETTEER_PATH = REPO_ROOT / "tarraconian_titles_1059.md"
DYNASTIC_REGISTER_PATH = REPO_ROOT / "dynastic_realignment_register.md"
EFFECTS_PATH = REPO_ROOT / "tarraconian_chancellery" / "common" / "scripted_effects" / "tarr_chancellery_title_list_effects.txt"
DYNASTIC_EFFECTS_PATH = REPO_ROOT / "tarraconian_chancellery" / "common" / "scripted_effects" / "tarr_chancellery_dynastic_effects.txt"
LOC_PATH = REPO_ROOT / "tarraconian_chancellery" / "localization" / "english" / "tarraconian_titles_l_english.yml"

def clean_toponym(raw: str) -> str:
    s = raw.strip()
    # Strip parenthetical notes like (Freising) or (Chellah / Salé)
    s = re.sub(r'\s*\([^)]*\)', '', s)
    # Strip any rank prefix + optional van (with or without space)
    s = re.sub(
        r'^(Keiserrîch|Keiserrich|Kûnincrich|Kunincrich|Regenat|Gubernat|March|Erzbisdom|Fürstbisdom|Furstbisdom|Magistrat)\s*(van\s*|van)?(der\s+|den\s+|dem\s+|dat\s+|des\s+)?',
        '',
        s,
        flags=re.IGNORECASE
    )
    s = re.sub(r'^[^\s]+\s+van\s+(der\s+|den\s+|dem\s+|dat\s+|des\s+)?', '', s)
    # Strip trailing asterisks or quotes
    s = s.strip('* "\'')
    return s.strip()

def extract_first_hist(raw_hist_group: str) -> str:
    # Remove parenthetical notes before splitting so slashes inside (...) do not split
    no_parens = re.sub(r'\s*\([^)]*\)', '', raw_hist_group)
    first = re.split(r'\s*(?:[/;—]|\bor\b)\s*', no_parens)[0]
    return clean_toponym(first)

def get_tarr_adj(name: str, key: str) -> str:
    if not name:
        return name
    if key in ('e_hre', 'h_roman_empire', 'e_roman_empire'):
        return 'Rômisch-Keiserlich'
    if key == 'k_papal_state':
        return 'Rômisch-Pâbestlich'
    if key == 'k_orthodox':
        return 'Ökumênisch-Patriarchalisch'
    if key == 'd_coptic_papacy':
        return 'Koptisch-Pâbestlich'
    if key == 'd_apostolic_church':
        return 'Armênisch-Apostôlisch'
    if key == 'd_conversos':
        return 'Konversisch-Pâbestlich'

    m_pab = re.match(r'^Pâbestdôm van (.+)$', name)
    if m_pab:
        name = m_pab.group(1)

    if name in ('Pontischen Steppe', 'Pontische Steppe'):
        return 'Pontisch-Steppisch'
    if name in ('Kaspischen Steppe', 'Kaspische Steppe'):
        return 'Kaspisch-Steppisch'
    if name == 'Welschen March':
        return 'Welsch-Märchisch'
    if name == 'Rôten Wûste':
        return 'Rôtwûstisch'
    if name == 'Egêischen Inseln':
        return 'Egêisch'

    # Explicit historical/chancellery stem adjectives & compounds
    explicit_adjs = {
        'Beiern': 'Beierisch',
        'Sâpmi': 'Sâmisch',
        'Finlant': 'Finnisch',
        'Suômi': 'Suômisch',
        'Estlant': 'Estnisch',
        'Bjarmelant': 'Bjarmisch',
        'Krête': 'Krêtisch',
        'Tzipern': 'Tziprisch',
        'Tzîpern': 'Tziprisch',
        'Bâli': 'Bâlisch',
        'Songâi': 'Songâisch',
        'Amdô': 'Amdôisch',
        'Lômon': 'Lômonisch',
        'Gogurjô': 'Gogurjôisch',
        'Zantsch': 'Zantschisch',
        'Chara Dale': 'Chara Daleer',
        'Râdschputâne': 'Râdschputânisch',
        'Gudscharât': 'Gudscharâtisch',
        'Dschenne': 'Dschenneer',
        'Zukuschi': 'Zukuschiisch',
        'Twê-Zschêlant': 'Twê-Zschêlantisch',
        'Sînt': 'Sîndisch',
        'Hellas': 'Hellênisch',
        'Îrlant': 'Îrisch',
        'Schotlant': 'Schottisch',
        'Brîe': 'Brîisch',
        'Trîer': 'Trîerisch',
        'Bâr-in-Pûlje': 'Bâr-Pûljer',
        'Alt-Mêne': 'Alt-Mêner',
        'Rôtenburch-an-der-Hûtzwe': 'Rôtenburch-an-der-Hûtzwer',
        'Nîenburch-am-Wolchouwe': 'Nîenburch-Wolchouwer',
        'Amâje-in-Kastîljen': 'Amâje-Kastîljer',
        'Môre-in-Dâlen': 'Môre-Dâler',
        'Ôsterdal-an-der-Glomme': 'Ôsterdal-Glommer',
        'Zutfen': 'Zutfisch',
        'Ardennen': 'Ardennisch',
        'Bôtzen-Brixen': 'Bôtzen-Brixisch',
        'Lôven': 'Lôvisch',
        'Oplant': 'Oplantisch',
        'Îsernbêrelant': 'Îsernbêrelantisch',
        'Ôsterbotten': 'Ôsterbottisch',
        'Tjênch': 'Tjênger',
        'Tschênch': 'Tschênger',
        'Egitânje': 'Egitânjisch',
        'Finnmarch': 'Finnmarchisch',
        'Grôzwazzer': 'Grôzwazzerisch',
    }
    if name in explicit_adjs:
        return explicit_adjs[name]

    # Prepositional qualifiers (-in-..., -an-der-..., -am-..., -ob-..., -uf-...)
    m_prep = re.match(r'^([^-]+)-(in|an|am|ob|uf)-.+$', name)
    if m_prep:
        stem = m_prep.group(1)
        if stem in explicit_adjs:
            return explicit_adjs[stem]
        name = stem

    if name in explicit_adjs:
        return explicit_adjs[name]

    m = re.match(r'^(.+)jen$', name)
    if m:
        return f"{m.group(1)}isch"
    m = re.match(r'^(.+)nje$', name)
    if m:
        return f"{m.group(1)}njisch"
    m = re.match(r'^(.+)(îe|ie)$', name)
    if m:
        return f"{m.group(1)}isch"
    m = re.match(r'^(.+)êe$', name)
    if m:
        return f"{m.group(1)}êisch"

    if key.startswith('k_') or key.startswith('d_'):
        m = re.match(r'^(.+)en$', name)
        if m:
            return f"{m.group(1)}isch"
        if re.search(r'(lant|land|rîch|rich|march)$', name):
            return f"{name}isch"

    m = re.match(r'^(.+)e$', name)
    if m:
        return f"{m.group(1)}er"
    if name.endswith('er'):
        return name
    return f"{name}er"

def parse_gazetteer(md_path: Path):
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    entries = {}

    # Empire & Hegemony titles
    entries['h_roman_empire'] = {
        'key': 'h_roman_empire',
        'direct': 'Dat Rômische Keiserrîch',
        'hist': 'Dat Rômische Keiserrîch',
    }
    entries['e_roman_empire'] = {
        'key': 'e_roman_empire',
        'direct': 'Dat Rômische Keiserrîch',
        'hist': 'Dat Rômische Keiserrîch',
    }
    entries['e_hre'] = {
        'key': 'e_hre',
        'direct': 'Dat Hilige Rômische Keiserrîch',
        'hist': 'Dat Hilige Rômische Keiserrîch',
    }

    for line in lines:
        line = line.strip('\r\n')

        # 1. Table row for Kingdoms (Section 2) or Archdioceses (Section 4.2)
        m = re.match(r'^\|\s*\d+\s*\|\s*\*\*[^*]+\*\*\s*\|\s*`([a-zA-Z0-9_\-]+)`\s*\|\s*\*\*([^*]+)\*\*', line)
        if m:
            key = m.group(1)
            raw_name = m.group(2)
            # Skip Section 4.3 Prince-Bishoprics table if county already parsed in Section 3
            if key.startswith('c_') and key in entries:
                continue
            clean = clean_toponym(raw_name)
            entries[key] = {
                'key': key,
                'direct': clean,
                'hist': clean,
            }
            continue

        # 2. Section 4.1 Papal & Patriarchal Heads of Faith
        m = re.match(r'^\|\s*\*\*[^*]+\*\*\s*\|\s*`([a-zA-Z0-9_\-]+)`\s*\|\s*\*\*([^*]+)\*\*', line)
        if m:
            key = m.group(1)
            raw_name = m.group(2).strip()
            entries[key] = {
                'key': key,
                'direct': raw_name,
                'hist': raw_name,
            }
            continue

        # 3. Section 3 Kingdom headers
        m = re.match(r'^###\s+3\.\d+\s+Kingdom.*?\(`([a-zA-Z0-9_\-]+)`\)\s+\$\\rightarrow\$\s+\*\*([^*]+)\*\*', line)
        if m:
            key = m.group(1)
            direct = clean_toponym(m.group(2))
            hist = direct
            m_hist = re.search(r'\[(1059|1122|1142|1154)[^\]:]*?:\s*([^\]]+)\]', line)
            if m_hist:
                hist = extract_first_hist(m_hist.group(2))
            entries[key] = {
                'key': key,
                'direct': direct,
                'hist': hist,
            }
            continue

        # 4. Section 3 Duchy bullets
        m = re.match(r'^\*\s+\*\*(?:Duchy|March)[^`]+`([a-zA-Z0-9_\-]+)`.*?\$\\rightarrow\$\s*\*\*([^*]+)\*\*', line)
        if m:
            direct = clean_toponym(m.group(2))
            hist = direct
            m_hist = re.search(r'\[(1059|1122|1142)[^\]:]*?:\s*([^\]]+)\]', line)
            if m_hist:
                hist = extract_first_hist(m_hist.group(2))
            all_keys = re.findall(r'`([dx]_[a-zA-Z0-9_\-]+)`', line)
            for k in all_keys:
                entries[k] = {
                    'key': k,
                    'direct': direct,
                    'hist': hist,
                }
            continue

        # 5. Section 3 County bullets
        m = re.match(r'^\s+\*\s+`(c_[a-zA-Z0-9_\-]+)`.*?\$\\rightarrow\$\s*\*\*([^*]+)\*\*', line)
        if m:
            key = m.group(1)
            direct = clean_toponym(m.group(2))
            hist = direct
            m_hist = re.search(r'\[(1059|1122|1142)[^\]:]*?:\s*([^\]]+)\]', line)
            if m_hist:
                hist = extract_first_hist(m_hist.group(2))
            entries[key] = {
                'key': key,
                'direct': direct,
                'hist': hist,
            }
            continue

    return entries

def build_scripted_effects(entries):
    lines = [
        "##############################################################################",
        "# Tarraconian Chancellery - Generated Title Rename Lists (1059-1142)",
        "# Auto-generated by build_mod.py from tarraconian_titles_1059.md",
        "##############################################################################",
        "",
        "tarr_apply_static_titles_effect = {",
    ]

    for e in entries.values():
        k = e['key']
        if k.startswith('x_script_'):
            continue
        name_key = f"cn_tarr_{k}"
        hist_key = f"cn_tarr_hist_{k}" if e['direct'] != e['hist'] else name_key
        lines.append(f"\ttitle:{k} ?= {{ tarr_rename_title_effect = {{ NAME = {name_key} HIST = {hist_key} }} }}")

    lines.extend([
        "}",
        "",
        "# Dynamic titles resolved safely via de jure children or capital counties at runtime",
        "tarr_apply_dynamic_titles_effect = {",
        "\t# Dynamic Duchies (resolved via their de jure counties)",
        "\ttitle:c_opava.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_3603 HIST = cn_tarr_x_script_3603 } }",
        "\ttitle:c_caslav.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_5253 HIST = cn_tarr_x_script_5253 } }",
        "\ttitle:c_chernigov.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_4589 HIST = cn_tarr_x_script_4589 } }",
        "\ttitle:c_odoyev.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_4712 HIST = cn_tarr_x_script_4712 } }",
        "\ttitle:c_gabes.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_4732 HIST = cn_tarr_x_script_4732 } }",
        "\ttitle:c_juwain.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_4403 HIST = cn_tarr_x_script_4403 } }",
        "\ttitle:c_subay.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_2536 HIST = cn_tarr_x_script_2536 } }",
        "\ttitle:c_bisha.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_5297 HIST = cn_tarr_x_script_5297 } }",
        "\ttitle:c_ahqaf.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_1416 HIST = cn_tarr_x_script_1416 } }",
        "\ttitle:c_sharka.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_4597 HIST = cn_tarr_x_script_4597 } }",
        "\ttitle:c_ganale.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_1373 HIST = cn_tarr_x_script_1373 } }",
        "\ttitle:c_jolof.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_1782 HIST = cn_tarr_hist_x_script_1782 } }",
        "\ttitle:c_vijnot.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_6239 HIST = cn_tarr_x_script_6239 } }",
        "\ttitle:c_ulleong.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_2362 HIST = cn_tarr_x_script_2362 } }",
        "\ttitle:c_dipalpur.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_1315 HIST = cn_tarr_x_script_1315 } }",
        "\ttitle:c_aksu.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_1553 HIST = cn_tarr_x_script_1553 } }",
        "\ttitle:c_eman_vanda.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_1250 HIST = cn_tarr_x_script_1250 } }",
        "\ttitle:c_eman_choripi.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_1439 HIST = cn_tarr_x_script_1439 } }",
        "\ttitle:c_eman_molihewen.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_2047 HIST = cn_tarr_x_script_2047 } }",
        "\ttitle:c_eman_boli.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_2533 HIST = cn_tarr_x_script_2533 } }",
        "\ttitle:c_eman_mohean.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_2799 HIST = cn_tarr_x_script_2799 } }",
        "\ttitle:c_eman_yerenhe.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_2924 HIST = cn_tarr_x_script_2924 } }",
        "\ttitle:c_eman_urehokto.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_1737 HIST = cn_tarr_x_script_1737 } }",
        "\ttitle:c_eman_urmi.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_2388 HIST = cn_tarr_x_script_2388 } }",
        "\ttitle:c_tsugaru.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_1505 HIST = cn_tarr_x_script_1505 } }",
        "\ttitle:c_kaabu.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_2481 HIST = cn_tarr_x_script_2481 } }",
        "\ttitle:c_chuguchak.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_8046 HIST = cn_tarr_x_script_8046 } }",
        "\ttitle:c_kilimanjaro.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_1506 HIST = cn_tarr_x_script_1506 } }",
        "\ttitle:c_tanga.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_1816 HIST = cn_tarr_x_script_1816 } }",
        "\ttitle:c_kirinyaga.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_1894 HIST = cn_tarr_x_script_1894 } }",
        "\ttitle:c_mto_galana.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_2263 HIST = cn_tarr_x_script_2263 } }",
        "\ttitle:c_pemba.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_3608 HIST = cn_tarr_x_script_3608 } }",
        "\ttitle:c_gurgi.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_4892 HIST = cn_tarr_x_script_4892 } }",
        "\ttitle:c_salamat.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_3271 HIST = cn_tarr_x_script_3271 } }",
        "\ttitle:c_dadhipadra.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_1314 HIST = cn_tarr_x_script_1314 } }",
        "\ttitle:c_ujjayini.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_3406 HIST = cn_tarr_x_script_3406 } }",
        "\ttitle:c_dasapura.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_3434 HIST = cn_tarr_x_script_3434 } }",
        "\ttitle:c_biun.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_2703 HIST = cn_tarr_x_script_2703 } }",
        "",
        "\t# Dynamic Kingdoms (resolved via their de jure duchies)",
        "\ttitle:d_sicily.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_4328 HIST = cn_tarr_x_script_4328 } }",
        "\ttitle:d_brabant.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_3965 HIST = cn_tarr_d_brabant } }",
        "\ttitle:d_alwa.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_2942 HIST = cn_tarr_hist_x_script_2942 } }",
        "\ttitle:d_apulia.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_6717 HIST = cn_tarr_x_script_6717 } }",
        "\ttitle:d_paphlagonia.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_4774 HIST = cn_tarr_x_script_4774 } }",
        "\ttitle:d_thessalonika.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_7238 HIST = cn_tarr_x_script_7238 } }",
        "\ttitle:d_thessaly.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_4359 HIST = cn_tarr_x_script_4359 } }",
        "\ttitle:d_khazaria.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_5503 HIST = cn_tarr_hist_x_script_5503 } }",
        "\ttitle:d_chaldia.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_6373 HIST = cn_tarr_x_script_6373 } }",
        "",
        "\t# Dynamic Antipapal Sees (resolved via holder of the see or liege of the archdiocese)",
        "\ttitle:d_et_besancon.holder.liege.primary_title ?= {",
        "\t\tif = {",
        "\t\t\tlimit = { has_variable = pam_antipope_office }",
        "\t\t\ttarr_rename_title_effect = { NAME = cn_tarr_x_script_5088 HIST = cn_tarr_x_script_5088 }",
        "\t\t}",
        "\t}",
        "\ttitle:d_et_cologne.holder.liege.primary_title ?= {",
        "\t\tif = {",
        "\t\t\tlimit = { has_variable = pam_antipope_office }",
        "\t\t\ttarr_rename_title_effect = { NAME = cn_tarr_x_script_3883 HIST = cn_tarr_x_script_3883 }",
        "\t\t}",
        "\t}",
        "\ttitle:c_tortona.holder.primary_title ?= {",
        "\t\tif = {",
        "\t\t\tlimit = { has_variable = pam_antipope_office }",
        "\t\t\ttarr_rename_title_effect = { NAME = cn_tarr_x_script_6119 HIST = cn_tarr_x_script_6119 }",
        "\t\t}",
        "\t}",
        "\ttitle:c_geisenhausen.holder.primary_title ?= {",
        "\t\tif = {",
        "\t\t\tlimit = { has_variable = pam_antipope_office }",
        "\t\t\ttarr_rename_title_effect = { NAME = cn_tarr_x_script_6508 HIST = cn_tarr_x_script_6508 }",
        "\t\t}",
        "\t}",
        "\ttitle:c_brandenburg.holder.primary_title ?= {",
        "\t\tif = {",
        "\t\t\tlimit = { has_variable = pam_antipope_office }",
        "\t\t\ttarr_rename_title_effect = { NAME = cn_tarr_x_script_7218 HIST = cn_tarr_x_script_7218 }",
        "\t\t}",
        "\t}",
        "}",
        ""
    ])

    return "\r\n".join(lines)

def parse_dynastic_register(md_path: Path):
    with open(md_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Section 2: Non-Chatenois Dynastic & Cadet branches
    s2_m = re.search(r"## 2\. Non-Chatenois Dynastic & Cadet Realignment Register.*?\n\| :---:.*?\n(.*?)\n---", text, re.DOTALL)
    s2_entries = []
    if s2_m:
        for line in s2_m.group(1).strip().splitlines():
            if not line.strip().startswith("|"):
                continue
            cols = [c.strip() for c in line.split("|")[1:-1]]
            hid = cols[0].strip("` ")
            dyn_match = re.search(r"\(([^)]+)\)", cols[1])
            dyn_id = dyn_match.group(1).strip("` ") if dyn_match else ""
            cur_name = cols[2].strip("`* ")
            seat_match = re.search(r"(c_[a-zA-Z0-9_\-]+|b_[a-zA-Z0-9_\-]+)", cols[3])
            seat = seat_match.group(1) if seat_match else ""
            realigned_name = cols[6].strip("`* ")
            tarr_form = cols[7].strip("`* ")
            s2_entries.append({
                "house_id": hid,
                "dynasty_id": dyn_id,
                "current_name": cur_name,
                "seat": seat,
                "realigned_name": realigned_name,
                "tarr_form": tarr_form
            })

    # Section 3.2: Cadet branches of House Kestenholz
    s3_m = re.search(r"### 3\.2 Master Cadet Branch Rename Register.*?\n\| :---:.*?\n(.*?)\n---", text, re.DOTALL)
    s3_entries = []
    if s3_m:
        for line in s3_m.group(1).strip().splitlines():
            if not line.strip().startswith("|"):
                continue
            cols = [c.strip() for c in line.split("|")[1:-1]]
            hid = cols[0].strip("` ")
            cur_name = cols[1].strip("`* ")
            final_name = cols[3].strip("`* ")
            seat_match = re.search(r"(c_[a-zA-Z0-9_\-]+|b_[a-zA-Z0-9_\-]+)", cols[4])
            seat = seat_match.group(1) if seat_match else ""
            s3_entries.append({
                "house_id": hid,
                "current_name": cur_name,
                "realigned_name": final_name,
                "seat": seat
            })

    # Section 4: Dynamic Emergent Cultures
    s4_m = re.search(r"## 4\. Dynamic Emergent Culture Realignment Register.*?\n\| :---:.*?\n(.*?)\n---", text, re.DOTALL)
    s4_entries = []
    if s4_m:
        for line in s4_m.group(1).strip().splitlines():
            if not line.strip().startswith("|"):
                continue
            cols = [c.strip() for c in line.split("|")[1:-1]]
            cid = cols[0].strip("` ")
            cur_name = cols[1].strip("`* ")
            seat_match = re.search(r"(c_[a-zA-Z0-9_\-]+)", cols[3])
            seat = seat_match.group(1) if seat_match else ""
            realigned_name = cols[5].strip("`* ")
            collective_noun = cols[6].strip("`* ")
            tarr_name = cols[7].strip("`* ")
            s4_entries.append({
                "culture_id": cid,
                "current_name": cur_name,
                "seat": seat,
                "realigned_name": realigned_name,
                "collective_noun": collective_noun,
                "tarr_name": tarr_name
            })

    return s2_entries, s3_entries, s4_entries

def build_dynastic_scripted_effects(s2_entries, s3_entries, s4_entries):
    lines = [
        "##############################################################################",
        "# Tarraconian Chancellery - Dynastic & Cultural Realignment Effects",
        "# Auto-generated by build_mod.py from dynastic_realignment_register.md",
        "# Enforces the Toponym-First Principle across noble houses and emergent cultures.",
        "##############################################################################",
        "",
        "tarr_apply_dynastic_and_cultural_realignment_effect = {",
        "\t# =========================================================================",
        "\t# 1. Dynamic Emergent Cultures (set_culture_name)",
        "\t# Scoped via active 1154 counties and character holders, guarded by",
        "\t# cultural pillars and protected against overwriting Tarraconian.",
        "\t# =========================================================================",
    ]

    # (counties, char_holder_titles, pillar_guards)
    culture_scopes = {
        '260': (
            ['c_juterbog'],
            [],
            ['has_cultural_pillar = heritage_west_slavic', 'has_cultural_pillar = language_lechitic', 'has_cultural_pillar = ethos_egalitarian']
        ),
        '270': (
            ['c_pereyaslavl'],
            [],
            ['has_cultural_pillar = heritage_east_slavic', 'has_cultural_pillar = language_east_slavic']
        ),
        '275': (
            ['c_galati'],
            [],
            ['has_cultural_pillar = heritage_vlach', 'has_cultural_pillar = ethos_bureaucratic']
        ),
        '279': (
            ['c_munchen', 'c_passau', 'c_ingolstadt', 'c_eschenlohe', 'c_falkenstein', 'c_rothenburg'],
            ['c_falkenstein', 'c_passau'],
            ['has_cultural_pillar = heritage_central_germanic', 'has_cultural_pillar = language_high_german', 'has_cultural_pillar = ethos_stoic']
        ),
        '286': (
            [],
            ['c_naumburg', 'b_altenburg', 'b_lubben'],
            ['has_cultural_pillar = heritage_west_slavic', 'has_cultural_pillar = language_lechitic']
        ),
        '288': (
            ['c_galati', 'c_buzau', 'c_braila', 'c_calarasi', 'c_bucuresti', 'c_campulung', 'c_giurgiu', 'c_stoenesti'],
            ['c_braila', 'c_bucuresti', 'c_buzau'],
            ['has_cultural_pillar = heritage_vlach', 'has_cultural_pillar = ethos_spiritual']
        ),
        '293': (
            ['c_chilia', 'c_cetatea_alba', 'c_iasi', 'c_barlad', 'c_lapusna'],
            [],
            ['has_cultural_pillar = heritage_magyar', 'has_cultural_pillar = language_wallachian']
        ),
        '303': (
            ['c_schmalkalden', 'c_orlamunde', 'c_gleichenstein', 'c_lobdaburg'],
            [],
            ['has_cultural_pillar = heritage_central_germanic', 'has_cultural_pillar = language_high_german', 'has_cultural_pillar = ethos_spiritual']
        ),
        '331': (
            ['c_novgorod_seversky'],
            [],
            ['has_cultural_pillar = heritage_east_slavic', 'has_cultural_pillar = language_east_slavic']
        ),
        '338': (
            ['c_burgas', 'c_thessalonika', 'c_adrianopolis', 'c_kran', 'c_mosynopolis', 'c_pirin', 'c_serres', 'c_strumica'],
            [],
            ['has_cultural_pillar = heritage_byzantine', 'has_cultural_pillar = language_slavonic']
        ),
        '358': (
            ['c_kazanskaya', 'c_sarysyn', 'c_balachev', 'c_millerovo'],
            ['c_talava'],
            ['has_cultural_pillar = heritage_turkic', 'has_cultural_pillar = language_oghur']
        ),
        '367': (
            ['c_hewes', 'c_spis'],
            ['c_ungvar', 'c_fogaras', 'c_polovragi'],
            ['has_cultural_pillar = heritage_central_germanic', 'has_cultural_pillar = language_magyar']
        ),
    }

    for c in s4_entries:
        cid = c['culture_id']
        counties, char_titles, pillars = culture_scopes.get(cid, ([c['seat']], [], []))
        lines.append(f"\t# Culture {cid}: {c['current_name']} -> {c['realigned_name']} ({c['tarr_name']})")
        for cty in counties:
            lines.extend([
                f"\ttitle:{cty} ?= {{",
                "\t\tif = {",
                "\t\t\tlimit = {",
                "\t\t\t\texists = culture",
                "\t\t\t\tNOT = { culture = title:c_barcelona.culture }",
            ])
            for p in pillars:
                lines.append(f"\t\t\t\tculture = {{ {p} }}")
            lines.extend([
                "\t\t\t}",
                "\t\t\tif = {",
                "\t\t\t\tlimit = { has_global_variable = tarr_direct_mode }",
                "\t\t\t\tculture = {",
                "\t\t\t\t\tset_culture_name = {",
                f"\t\t\t\t\t\tnoun = tarr_culture_{cid}_tarr_name",
                f"\t\t\t\t\t\tcollective_noun = tarr_culture_{cid}_tarr_collective",
                f"\t\t\t\t\t\tprefix = tarr_culture_{cid}_tarr_prefix",
                "\t\t\t\t\t}",
                "\t\t\t\t}",
                "\t\t\t}",
                "\t\t\telse = {",
                "\t\t\t\tculture = {",
                "\t\t\t\t\tset_culture_name = {",
                f"\t\t\t\t\t\tnoun = tarr_culture_{cid}_name",
                f"\t\t\t\t\t\tcollective_noun = tarr_culture_{cid}_collective",
                f"\t\t\t\t\t\tprefix = tarr_culture_{cid}_prefix",
                "\t\t\t\t\t}",
                "\t\t\t\t}",
                "\t\t\t}",
                "\t\t}",
                "\t}",
            ])
        for cht in char_titles:
            lines.extend([
                f"\ttitle:{cht}.holder ?= {{",
                "\t\tif = {",
                "\t\t\tlimit = {",
                "\t\t\t\texists = culture",
                "\t\t\t\tNOT = { culture = title:c_barcelona.culture }",
            ])
            for p in pillars:
                lines.append(f"\t\t\t\tculture = {{ {p} }}")
            lines.extend([
                "\t\t\t}",
                "\t\t\tif = {",
                "\t\t\t\tlimit = { has_global_variable = tarr_direct_mode }",
                "\t\t\t\tculture = {",
                "\t\t\t\t\tset_culture_name = {",
                f"\t\t\t\t\t\tnoun = tarr_culture_{cid}_tarr_name",
                f"\t\t\t\t\t\tcollective_noun = tarr_culture_{cid}_tarr_collective",
                f"\t\t\t\t\t\tprefix = tarr_culture_{cid}_tarr_prefix",
                "\t\t\t\t\t}",
                "\t\t\t\t}",
                "\t\t\t}",
                "\t\t\telse = {",
                "\t\t\t\tculture = {",
                "\t\t\t\t\tset_culture_name = {",
                f"\t\t\t\t\t\tnoun = tarr_culture_{cid}_name",
                f"\t\t\t\t\t\tcollective_noun = tarr_culture_{cid}_collective",
                f"\t\t\t\t\t\tprefix = tarr_culture_{cid}_prefix",
                "\t\t\t\t\t}",
                "\t\t\t\t}",
                "\t\t\t}",
                "\t\t}",
                "\t}",
            ])

    lines.extend([
        "",
        "\t# =========================================================================",
        "\t# 2. Imperial Cadet Branches (House Kestenholz / Chatenois - dynasty:667)",
        "\t# Covers all 39 living non-dynn_ cadet branches (32 direct static title",
        "\t# holders + 7 relational/dynastic scopes) without save-file modification.",
        "\t# =========================================================================",
    ])

    # 2A. Dynasty-level house head scopes for Noble Family houses without static titles
    lines.extend([
        "\t# House 24600: Chatenois-Arnedo -> Kestenholz-Arnedo",
        "\tdynasty:667 ?= {",
        "\t\tevery_dynasty_house = {",
        "\t\t\tlimit = {",
        "\t\t\t\texists = house_head",
        "\t\t\t\thouse_head = { is_female = no age = 23 }",
        "\t\t\t}",
        "\t\t\tset_house_name = tarr_house_kestenholz_arnedo",
        "\t\t}",
        "\t\t# House 26976: Chatenois-Lecce -> Kestenholz-Lecce",
        "\t\tevery_dynasty_house = {",
        "\t\t\tlimit = {",
        "\t\t\t\texists = house_head",
        "\t\t\t\thouse_head = { is_female = yes age = 21 }",
        "\t\t\t}",
        "\t\t\tset_house_name = tarr_house_kestenholz_lecce",
        "\t\t}",
        "\t}",
    ])

    # 2B. Direct static title holder scopes for all 32 landed Kestenholz cadet branches
    direct_kestenholz_holders = [
        # (house_id, comment, titles, loc_key)
        ('13928', 'Chatenois-Metz -> Kestenholz-Metz (Imperial House)', ['h_roman_empire', 'c_barcelona', 'd_jabal_kufs'], 'tarr_house_kestenholz_metz'),
        ('19476', 'Chatenois-Ravenna -> Kestenholz-Raben', ['d_westfalen', 'c_osnabruck', 'c_agadir'], 'tarr_house_kestenholz_raben'),
        ('16791696', 'Chatenois-Saumur -> Kestenholz-Saumur', ['d_smolensk', 'c_bihar', 'c_al-buhaira'], 'tarr_house_kestenholz_saumur'),
        ('18311', 'Chatenois-Annonay -> Kestenholz-Annonay', ['d_sicily', 'c_novgorod', 'c_agrigento'], 'tarr_house_kestenholz_annonay'),
        ('16799240', 'Chatenois-Fécamp -> Kestenholz-Fécamp', ['d_armagnac', 'c_armagnac'], 'tarr_house_kestenholz_fecamp'),
        ('18122', 'Chatenois-Albret -> Kestenholz-Albret', ['c_sevede', 'c_eschenlohe', 'c_allenstein'], 'tarr_house_kestenholz_albret'),
        ('16796964', 'Flanders -> Kestenholz-Flanders', ['d_carinthia', 'c_kammersberg', 'c_attica'], 'tarr_house_kestenholz_flanders'),
        ('16790779', 'Chatenois-Geteina -> Kestenholz-Geteina', ['c_fazughli', 'c_mainz', 'c_benevento'], 'tarr_house_kestenholz_geteina'),
        ('16797465', 'Chatenois-Dillingen -> Kestenholz-Dillingen', ['c_kaiserslautern', 'c_paphlagonia'], 'tarr_house_kestenholz_dillingen'),
        ('50346404', 'Chatenois-Amersfoort -> Kestenholz-Utrecht', ['d_alwa', 'c_alodia'], 'tarr_house_kestenholz_utrecht'),
        ('50348946', 'Chatenois-Koschmin -> Kestenholz-Kalisch', ['d_iceland', 'c_gnieznienska', 'c_kaliska'], 'tarr_house_kestenholz_kalisch'),
        ('50347588', 'Chatenois-Hirschberg -> Kestenholz-Legnica', ['d_nordgau', 'c_eichstadt'], 'tarr_house_kestenholz_legnica'),
        ('16799191', 'Chatenois-Tyddewi -> Kestenholz-Tyddewi', ['c_yatvyagi'], 'tarr_house_kestenholz_tyddewi'),
        ('24384', 'Chatenois-Kammersberg -> Kestenholz-Judenburch', ['c_baqlin', 'c_djarin'], 'tarr_house_kestenholz_judenburch'),
        ('33573102', 'Cologne -> Kestenholz-Cologne', ['c_pavia', 'c_pagania'], 'tarr_house_kestenholz_cologne'),
        ('26275', 'Chatenois-Buthrotum -> Kestenholz-Buthrotum', ['k_epirus', 'c_buthrotum'], 'tarr_house_kestenholz_buthrotum'),
        ('19355', 'Chatenois-Pau -> Kestenholz-Pau', ['c_arnsberg', 'c_hallstatt', 'c_alencon'], 'tarr_house_kestenholz_pau'),
        ('25659', 'Chatenois-Mérida -> Kestenholz-Mêrida', ['d_badajoz', 'c_badajoz', 'c_merida'], 'tarr_house_kestenholz_merida'),
        ('16796257', 'Chatenois-Swenigorot -> Kestenholz-Swenigorot', ['c_iasi', 'c_torda'], 'tarr_house_kestenholz_swenigorot'),
        ('23237', 'Chatenois-Sennar -> Kestenholz-Sennar', ['c_hohenau'], 'tarr_house_kestenholz_sennar'),
        ('25175', 'Chatenois-Blasien -> Kestenholz-Blasien', ['d_anhalt', 'c_blankenburg'], 'tarr_house_kestenholz_blasien'),
        ('25769', 'Chatenois-Bechyně -> Kestenholz-Bechin', ['b_akto'], 'tarr_house_kestenholz_bechin'),
        ('16789468', 'Chatenois-Stężyca -> Kestenholz-Sitzichow', ['d_rashka', 'c_krakowska', 'c_stezycka'], 'tarr_house_kestenholz_sitzichow'),
        ('26541', 'Chatenois-Moraca -> Kestenholz-Moraca', ['d_duklja', 'c_duklja'], 'tarr_house_kestenholz_moraca'),
        ('26581', 'Chatenois-Berg -> Kestenholz-Berch', ['c_bergh', 'c_cologne', 'c_murom'], 'tarr_house_kestenholz_berch'),
        ('25655', 'Chatenois-Terebovl -> Kestenholz-Terebovl', ['d_northumberland', 'c_halych', 'c_amaya'], 'tarr_house_kestenholz_terebovl'),
        ('22345', 'Chatenois-Mons -> Kestenholz-Bergen', ['d_cyrenaica', 'c_awjila'], 'tarr_house_kestenholz_bergen'),
        ('26913', 'Chatenois-Sargans -> Kestenholz-Kûr', ['d_currezia', 'c_grisons'], 'tarr_house_kestenholz_kur'),
        ('24655', 'Chatenois-Plzeň -> Kestenholz-Plzenec', ['c_frontenhausen', 'c_iskaf'], 'tarr_house_kestenholz_plzenec'),
        ('16802581', 'Chatenois-Vendôme -> Kestenholz-Vendôme', ['d_orleans', 'c_orleans', 'c_vendome'], 'tarr_house_kestenholz_vendome'),
        ('24627', 'Chatenois-Zutphen -> Kestenholz-Zutphen', ['d_gelre', 'c_arnhem', 'c_zutphen'], 'tarr_house_kestenholz_zutphen'),
        ('23892', 'Chatenois-Baht -> Kestenholz-Baht', ['d_fes', 'c_fes'], 'tarr_house_kestenholz_baht'),
    ]

    for hid, comment, t_list, key in direct_kestenholz_holders:
        lines.append(f"\t# House {hid}: {comment}")
        for t in t_list:
            lines.extend([
                f"\ttitle:{t}.holder ?= {{",
                "\t\tif = {",
                "\t\t\tlimit = { house ?= { dynasty ?= dynasty:667 } }",
                f"\t\t\thouse = {{ set_house_name = {key} }}",
                "\t\t}",
                "\t}",
            ])

    # 2C. Relational 1-hop scopes for unlanded/administrative Kestenholz cadet branches
    relational_kestenholz = [
        ('18111', 'Chatenois-Bremen -> Kestenholz-Bremen', 'c_mainz', 'primary_spouse', 'tarr_house_kestenholz_bremen'),
        ('20743', 'Flanders -> Kestenholz-Flanders', 'd_hereford', 'primary_spouse', 'tarr_house_kestenholz_flanders'),
        ('23583', 'Chatenois-Peiting -> Kestenholz-Altenstadt', 'd_ciscaucasia', 'primary_spouse', 'tarr_house_kestenholz_altenstadt'),
        ('25132', 'Chatenois-Orléans -> Kestenholz-Orleans', 'd_socotra', 'primary_spouse', 'tarr_house_kestenholz_orleans'),
        ('26976', 'Chatenois-Lecce -> Kestenholz-Lecce (via betrothed)', 'c_eman_yerenhe', 'betrothed', 'tarr_house_kestenholz_lecce'),
        ('33566549', 'Chatenois-Saarbrücken -> Kestenholz-Zant-Arnolt', 'c_sieradzka', 'primary_spouse', 'tarr_house_kestenholz_zant_arnolt'),
    ]

    for hid, comment, anchor_title, rel_scope, key in relational_kestenholz:
        lines.extend([
            f"\t# House {hid}: {comment}",
            f"\ttitle:{anchor_title}.holder.{rel_scope} ?= {{",
            "\t\tif = {",
            "\t\t\tlimit = { house ?= { dynasty ?= dynasty:667 } }",
            f"\t\t\thouse = {{ set_house_name = {key} }}",
            "\t\t}",
            "\t}",
        ])

    lines.extend([
        "",
        "\t# =========================================================================",
        "\t# 3. Non-Chatenois Historical Cadet Branches & Elevated Dynasties (Section 2)",
        "\t# Covers all 29 living non-dynn_ houses (17 direct static holders +",
        "\t# 12 relational/dynastic scopes) plus ancestral seats for extinct branches.",
        "\t# =========================================================================",
    ])

    # 3A. Direct static title holder scopes for vanilla dynasty cadet branches
    # Uses exact vanilla database keys: Billung=656, Karling=25061, Palemonaitis=9116,
    # Gellones=100217, Reginar=7198, Umayyad=597, Cetchathach=9217, Ebrauc=1029002
    vanilla_cadet_mappings = [
        ('33574710', 'Billung-Gleichen -> Billung-Erfurt', ['c_marmaros', 'c_erfurt'], '656', 'tarr_house_billung_erfurt'),
        ('16800201', 'Gellones-Güstrow -> Gellones-Wurle', ['d_friuli', 'c_aquileia'], '100217', 'tarr_house_gellones_wurle'),
        ('50343822', 'Karling-Uničov -> Karling-Litovel', ['d_moravia', 'c_brno', 'c_olomouc'], '25061', 'tarr_house_karling_litovel'),
        ('33571287', 'Karling-Korosten -> Karling-Ush', ['d_spoleto', 'c_abruzzi', 'c_korosten'], '25061', 'tarr_house_karling_ush'),
        ('14423', 'Karling-Opava -> Karling-Troppouwe (ancestral)', ['c_opava'], '25061', 'tarr_house_karling_troppouwe'),
        ('16800883', 'Palemonaitis-Jurmala -> Palemonaitis-Lielupe', ['c_selpils', 'c_jurmala'], '9116', 'tarr_house_palemonaitis_lielupe'),
        ('27674', 'Palemonaitis-Siauliai -> Palemonaitis-Schaulen', ['c_siauliai'], '9116', 'tarr_house_palemonaitis_schaulen'),
        ('67131755', 'Reginar-Vecchio -> Reginar-Sirakusan', ['d_alsace', 'c_ajaccio', 'c_vecchio'], '7198', 'tarr_house_reginar_sirakusan'),
        ('33577966', 'Umayyad-Povenets -> Umayyad-Wîchsê', ['c_pudozh', 'c_povenets'], '597', 'tarr_house_umayyad_wichse'),
        ('12948', 'Cétchathach-Athlone -> Cétchathach-Uisnech (ancestral)', ['c_athlone'], '9217', 'tarr_house_cetchathach_uisnech'),
        ('16797551', 'Ebrauc-Athlone -> Ebrauc-Uisnech (ancestral)', ['c_athlone'], '1029002', 'tarr_house_ebrauc_uisnech'),
    ]

    for hid, comment, t_list, dyn_key, hkey in vanilla_cadet_mappings:
        lines.append(f"\t# House {hid}: {comment}")
        for title in t_list:
            lines.extend([
                f"\ttitle:{title}.holder ?= {{",
                "\t\tif = {",
                f"\t\t\tlimit = {{ house ?= {{ dynasty ?= dynasty:{dyn_key} }} }}",
                f"\t\t\thouse = {{ set_house_name = {hkey} }}",
                "\t\t}",
                "\t}",
            ])

    # 3B. Relational & Dynasty-level scopes for unlanded vanilla dynasty cadet branches
    vanilla_relational_mappings = [
        ('12726', 'Karling-Calw -> Karling-Hirsau', 'd_kiev', 'primary_spouse', '25061', 'tarr_house_karling_hirsau'),
        ('24293', 'Palemonaitis-Orsha -> Palemonaitis-Orsche', 'c_siauliai', 'primary_spouse', '9116', 'tarr_house_palemonaitis_orsche'),
        ('24307', 'Palemonaitis-Kazanskaya -> Palemonaitis-Middel-Dôn', 'c_selpils', 'mother', '9116', 'tarr_house_palemonaitis_middel_don'),
        ('24355', 'Palemonaitis-Raseiniai -> Palemonaitis-Rassêinen', 'd_vologda', 'primary_spouse', '9116', 'tarr_house_palemonaitis_rasseinen'),
        ('33574947', 'Palemonaitis-Kokenois -> Palemonaitis-Kukena', 'c_selpils', 'primary_spouse', '9116', 'tarr_house_palemonaitis_kukena'),
    ]

    for hid, comment, anchor_title, rel_scope, dyn_key, hkey in vanilla_relational_mappings:
        lines.extend([
            f"\t# House {hid}: {comment}",
            f"\ttitle:{anchor_title}.holder.{rel_scope} ?= {{",
            "\t\tif = {",
            f"\t\t\tlimit = {{ house ?= {{ dynasty ?= dynasty:{dyn_key} }} }}",
            f"\t\t\thouse = {{ set_house_name = {hkey} }}",
            "\t\t}",
            "\t}",
        ])

    lines.extend([
        "\t# House 27311: Hede-Tambov -> Hede-Tzene (dynasty:836)",
        "\tdynasty:836 ?= {",
        "\t\tevery_dynasty_house = {",
        "\t\t\tlimit = {",
        "\t\t\t\texists = house_head",
        "\t\t\t\thouse_head = { is_female = no age = 37 }",
        "\t\t\t}",
        "\t\t\tset_house_name = tarr_house_hede_tzene",
        "\t\t}",
        "\t}",
        "\t# House 16796949: Borg-Shenkursk -> Borg-Wâga (dynasty:830)",
        "\tdynasty:830 ?= {",
        "\t\tevery_dynasty_house = {",
        "\t\t\tlimit = {",
        "\t\t\t\texists = house_head",
        "\t\t\t\thouse_head = { is_female = yes }",
        "\t\t\t}",
        "\t\t\tset_house_name = tarr_house_borg_waga",
        "\t\t}",
        "\t}",
    ])

    lines.extend([
        "",
        "\t# =========================================================================",
        "\t# 4. Elevated Noble Houses & Dynamic Dynasties",
        "\t# =========================================================================",
    ])

    # 4A. Direct static title holders for Elevated Dynasties & Dynamic Cadet Houses
    # (house_id, comment, titles, loc_key, rename_dynasty_too)
    elevated_direct_mappings = [
        ('16800136', 'Buxtehude -> Este', ['c_hamburg', 'b_buxtehude'], 'tarr_house_este', True),
        ('67125621', 'Celle -> Alre', ['c_starodub', 'c_lanzhou'], 'tarr_house_alre', True),
        ('50349259', 'Coburg -> Îtze', ['c_coburg'], 'tarr_house_itze', True),
        ('25935', 'Leoben -> Göss', ['b_nawa'], 'tarr_house_goss', True),
        ('33568115', 'Philippopolis-Priština -> Philippopolis-Ulpiana', ['c_zlatibor', 'b_zvecan'], 'tarr_house_philippopolis_ulpiana', False),
        ('28114', 'Roslavl -> Ôster', ['c_roslavl'], 'tarr_house_oster', True),
        ('16803302', 'Steyr -> Enns', ['b_steyr'], 'tarr_house_enns', True),
        ('21816', 'Vologda -> Walgede', ['d_vologda', 'c_vologda', 'c_capua'], 'tarr_house_walgede', True),
        ('27893', 'Werle -> Wurle', ['c_werle'], 'tarr_house_wurle', True),
        ('16792693', 'Naugardukas -> iš Plesės (ancestral)', ['c_novogrudok'], 'tarr_house_plise', True),
        ('21909', 'Babruysk -> Berezina (ancestral)', ['c_babruysk'], 'tarr_house_berezina', True),
        ('22261', 'Stężyca -> Sitzichow (ancestral)', ['c_sandomierz'], 'tarr_house_sitzichow', True),
    ]

    for hid, comment, t_list, hkey, rename_dyn in elevated_direct_mappings:
        lines.append(f"\t# House {hid}: {comment}")
        for title in t_list:
            lines.extend([
                f"\ttitle:{title}.holder ?= {{",
                "\t\tif = {",
                "\t\t\tlimit = {",
                "\t\t\t\texists = house",
                "\t\t\t\tNOT = { house ?= { dynasty ?= dynasty:667 } }",
                "\t\t\t\tNOT = { house ?= { dynasty ?= dynasty:25061 } }",
                "\t\t\t\tNOT = { house ?= { dynasty ?= dynasty:656 } }",
                "\t\t\t\tNOT = { house ?= { dynasty ?= dynasty:100217 } }",
                "\t\t\t}",
                f"\t\t\thouse = {{ set_house_name = {hkey} }}",
            ])
            if rename_dyn:
                lines.append(f"\t\t\thouse.dynasty ?= {{ set_dynasty_name = {hkey} }}")
            lines.extend([
                "\t\t}",
                "\t}",
            ])

    # 4B. Relational scopes for unlanded Elevated Dynasties & Dynamic Cadet Houses
    lines.extend([
        "\t# House 17334: Jihlava -> Rokytna (via spouse of c_bornholm holder)",
        "\ttitle:c_bornholm.holder.primary_spouse ?= {",
        "\t\tif = {",
        "\t\t\tlimit = { exists = house }",
        "\t\t\thouse = { set_house_name = tarr_house_rokytna }",
        "\t\t\thouse.dynasty ?= { set_dynasty_name = tarr_house_rokytna }",
        "\t\t}",
        "\t}",
        "\t# House 16800196: Soundavara-Lyubim -> Soundavara-Obnore (via spouse of c_scalovia holder)",
        "\t# House 33569509: Soundavara-Molina -> Soundavara-Erkawîka (via same dynasty, male house head)",
        "\t# House 23369: Sheksna-Kholmogory -> Sheksna-Dwina (via spouse of Soundavara-Obnore house head)",
        "\ttitle:c_scalovia.holder.primary_spouse ?= {",
        "\t\tif = {",
        "\t\t\tlimit = { exists = house }",
        "\t\t\thouse = {",
        "\t\t\t\tset_house_name = tarr_house_soundavara_obnore",
        "\t\t\t\thouse_head.primary_spouse ?= {",
        "\t\t\t\t\tif = {",
        "\t\t\t\t\t\tlimit = { exists = house }",
        "\t\t\t\t\t\thouse = { set_house_name = tarr_house_sheksna_dwina }",
        "\t\t\t\t\t}",
        "\t\t\t\t}",
        "\t\t\t}",
        "\t\t\tdynasty ?= {",
        "\t\t\t\tevery_dynasty_house = {",
        "\t\t\t\t\tlimit = {",
        "\t\t\t\t\t\texists = house_head",
        "\t\t\t\t\t\thouse_head = { is_female = no }",
        "\t\t\t\t\t}",
        "\t\t\t\t\tset_house_name = tarr_house_soundavara_erkawika",
        "\t\t\t\t}",
        "\t\t\t}",
        "\t\t}",
        "\t}",
        "\t# House 16801742: Brunnsholm-Sebezh -> Brunnsholm-Sebêsch (via noble guest at d_yanmen)",
        "\ttitle:d_yanmen.holder ?= {",
        "\t\tevery_pool_guest = {",
        "\t\t\tlimit = { exists = house }",
        "\t\t\thouse = { set_house_name = tarr_house_brunnsholm_sebesch }",
        "\t\t}",
        "\t}",
    ])

    lines.append("}\n")
    return "\r\n".join(lines)

def build_localization(entries, s2_entries, s3_entries, s4_entries):
    lines = [
        "l_english:",
        " # === Decisions & Events ===",
        ' tarr_chancellery_ordinance_decision:0 "Issue the Tarraconian Chancellery Ordinance"',
        ' tarr_chancellery_ordinance_decision_tooltip:0 "Standardize the names of Imperial and Tarraconian Kingdoms, Governorships, Magistracies, Prince-Bishoprics, and Archdioceses in the Tarraconian court tongue."',
        ' tarr_chancellery_ordinance_decision_desc:0 "Since the union of Lothringian High Franconian and Catalan courtly administration in 989, the scribes of the Imperial Chancellery have rendered the realms, governorships, magistracies, and ecclesiastical sees of the Roman Empire in the Tarraconian tongue. By imperial ordinance, we may codify these official registers across the Empire."',
        ' tarr_chancellery_ordinance_decision_confirm:0 "Summon the Imperial Chancellery"',
        ' tarr_chancellery_ordinance_decision_effect_tt:0 "Applies #V Tarraconian#! chancellery toponymy (using #V 1059–1142 Historical Resolutions#! by default, including #V Lûnstat#! for Nancy and #V Swenigorot#! for Lemberg) and opens the Chancellery configuration register."',
        "",
        ' tarr_chancellery.0001.t:0 "The Imperial Tarraconian Register"',
        r' tarr_chancellery.0001.desc:0 "The Protonotaries of the Imperial Chancellery present the great register of [ROOT.Char.GetCulture.GetNameNoTooltip] toponymy for the Roman Empire.\n\nUnder the #bold Historical Resolution#! standard, anachronistic castles and colonial towns are replaced by their authentic pre-1059/1122/1142 provincial centres and sub-baronies (such as #italic Lûnstat#! for Nancy, #italic Vrîsing#! for München, #italic Wilten#! for Innsbruck, #italic Swenigorot#! for Lemberg, #italic Skône#! for Gowrie, #italic Sôsôpel#! for Burgas, #italic Olbîe#! for Kara-Kerman, #italic Rêwale#! for Reval, #italic Atîl-Chasarân#! for Astrakhan, and #italic Rôhe#! for Lasta), while all titles are updated automatically on the 1st of January each year."',
        ' tarr_chancellery.0001.a:0 "Enforce the Historical Register across the Empire (Default)"',
        ' tarr_chancellery.0001.a.tt:0 "Renames all titles in the #V Roman Empire / HRE#! and any #V Tarraconian#! (or daughter-culture) provinces using #V 1059–1142 Historical Resolutions#!."',
        ' tarr_chancellery.0001.b:0 "Extend the Historical Register to all 160 De Jure Kingdoms"',
        ' tarr_chancellery.0001.b.tt:0 "Renames all 160 De Jure Kingdoms, 752 Duchies, 2,732 Counties, and 78 Archdioceses (including non-Imperial provinces) using #V 1059–1154 Historical Resolutions#!."',
        ' tarr_chancellery.0001.c:0 "Use Direct Toponymic Adaptations in the Empire"',
        ' tarr_chancellery.0001.c.tt:0 "Renames Imperial and Tarraconian titles using direct phonological adaptations of their vanilla/save names rather than historical resolutions."',
        ' tarr_chancellery.0001.d:0 "Repeal the Ordinance and restore original title names"',
        ' tarr_chancellery.0001.d.tt:0 "Resets all titles renamed by the Tarraconian Chancellery back to their default names."',
        "",
        " # === Tarraconian Rank & Title Prefix Flavorization ===",
        ' emperor_tarraconian_male:0 "Keiser"',
        ' emperor_tarraconian_female:0 "Keiserin"',
        ' empire_tarraconian:0 "Keiserrîch"',
        ' king_tarraconian_admin_male:0 "Vîzerege"',
        ' king_tarraconian_admin_female:0 "Vîzeregin"',
        ' kingdom_tarraconian_admin:0 "Regenat"',
        ' king_tarraconian_feudal_male:0 "Kûninc"',
        ' king_tarraconian_feudal_female:0 "Kûningin"',
        ' kingdom_tarraconian_feudal:0 "Kûnincrich"',
        ' duke_tarraconian_admin_male:0 "Gubernator"',
        ' duke_tarraconian_admin_female:0 "Gubernatrix"',
        ' duchy_tarraconian_admin:0 "Gubernat"',
        ' duke_tarraconian_ecclesiastical_male:0 "Erzbischof"',
        ' duke_tarraconian_ecclesiastical_female:0 "Erzbischöfin"',
        ' duchy_tarraconian_ecclesiastical:0 "Erzbisdom"',
        ' count_tarraconian_admin_male:0 "Magistrat"',
        ' count_tarraconian_admin_female:0 "Magistratin"',
        ' county_tarraconian_admin:0 "Magistrat"',
        ' count_tarraconian_ecclesiastical_male:0 "Fürstbischof"',
        ' count_tarraconian_ecclesiastical_female:0 "Fürstbischöfin"',
        ' county_tarraconian_ecclesiastical:0 "Fürstbisdom"',
        "",
        " # === Title & Archdiocese Localisation Keys ===",
    ]

    for e in entries.values():
        k = e['key']
        d_name = e['direct']
        d_adj = get_tarr_adj(d_name, k)

        lines.append(f' cn_tarr_{k}:0 "{d_name}"')
        lines.append(f' cn_tarr_{k}_adj:0 "{d_adj}"')

        if e['hist'] != e['direct']:
            h_name = e['hist']
            h_adj = get_tarr_adj(h_name, k)
            lines.append(f' cn_tarr_hist_{k}:0 "{h_name}"')
            lines.append(f' cn_tarr_hist_{k}_adj:0 "{h_adj}"')

    # === Master Dynastic Realignment Overrides (Section 2 & 3) ===
    lines.extend([
        "",
        " # === Master Dynastic Realignment Overrides (Toponym-First Coupling) ===",
        ' dynn_Chatenois:0 "Kestenholz"',
        ' dynn_Egisheim:0 "Egisheim"',
        ' dynn_Dachsburg:0 "Dachsburg"',
        ' dynn_Lorraine:0 "Lorraine"',
        ' dynn_de_Blamont:0 "de Blâmont"',
        ' dynn_Harjaroda:0 "Kestenholz-Harjaroda"',
        ' dynn_Beichlingen:0 "Kestenholz-Beichlingen"',
        ' dynn_der_Mark:0 "van Soest"',
        ' dynn_Gudensberg:0 "Gudensberch"',
        ' dynn_Pernstein:0 "Swratka"',
        ' dynn_Luxembourg:0 "Echternach"',
        ' dynn_Memel:0 "Pilsāts"',
        ' dynn_Tigheci:0 "Tîghetsch"',
        ' dynn_Tula:0 "Prôntzich"',
        ' dynn_Wittenberg:0 "Belzig"',
        ' dynn_Silesia-Glogau:0 "Silesia-Dziadosz"',
        ' dynn_Bluome:0 "Kestenholz-Bluome"',
        ' dynn_Carenwall:0 "Kestenholz-Carenwall"',
        ' dynn_Diest:0 "Kestenholz-Diest"',
        ' dynn_Orlamunde:0 "Kestenholz-Orlamunde"',
        ' dynn_Verona:0 "Kestenholz-Verona"',
        ' dynn_Suerbeer:0 "Kestenholz-Suerbeer"',
        ' dynn_Muhlhausen:0 "Kestenholz-Muhlhausen"',
        ' dynn_O_sel:0 "Kestenholz-Sâremâ"',
        ' dynn_Montjoie:0 "Kestenholz-Montjoie"',
    ])

    # === Dynamic Emergent Culture Realignments (Section 4) ===
    lines.extend([
        "",
        " # === Dynamic Emergent Culture Realignments (Section 4) ===",
    ])
    for c in s4_entries:
        cid = c['culture_id']
        name = c['realigned_name']
        coll = c['collective_noun']
        tname = c['tarr_name']
        prefix_m = re.match(r"^([^\s\-]+)", name)
        prefix_stem = prefix_m.group(1) if prefix_m else name
        prefix = f"{prefix_stem.rstrip('ian').rstrip('an')}-" if not prefix_stem.endswith('-') else prefix_stem
        tprefix = f"{tname.rstrip('en').rstrip('er')}isch-"

        lines.extend([
            f' # Culture {cid}: {c["current_name"]} -> {name}',
            f' tarr_culture_{cid}_name:0 "{name}"',
            f' tarr_culture_{cid}_collective:0 "{coll}"',
            f' tarr_culture_{cid}_prefix:0 "{prefix}"',
            f' tarr_culture_{cid}_tarr_name:0 "{tname}"',
            f' tarr_culture_{cid}_tarr_collective:0 "{tname}"',
            f' tarr_culture_{cid}_tarr_prefix:0 "{tprefix}"',
        ])

    # === Cadet House & Noble Dynasty Names ===
    lines.extend([
        "",
        " # === Cadet House & Noble Dynasty Names ===",
        # Kestenholz cadet branches (all 41 non-dynn_ houses in Section 3.2)
        ' tarr_house_kestenholz_raben:0 "Kestenholz-Raben"',
        ' tarr_house_kestenholz_utrecht:0 "Kestenholz-Utrecht"',
        ' tarr_house_kestenholz_kalisch:0 "Kestenholz-Kalisch"',
        ' tarr_house_kestenholz_legnica:0 "Kestenholz-Legnica"',
        ' tarr_house_kestenholz_judenburch:0 "Kestenholz-Judenburch"',
        ' tarr_house_kestenholz_altenstadt:0 "Kestenholz-Altenstadt"',
        ' tarr_house_kestenholz_bechin:0 "Kestenholz-Bechin"',
        ' tarr_house_kestenholz_sitzichow:0 "Kestenholz-Sitzichow"',
        ' tarr_house_kestenholz_gudensberch:0 "Kestenholz-Gudensberch"',
        ' tarr_house_kestenholz_berch:0 "Kestenholz-Berch"',
        ' tarr_house_kestenholz_bergen:0 "Kestenholz-Bergen"',
        ' tarr_house_kestenholz_kur:0 "Kestenholz-Kûr"',
        ' tarr_house_kestenholz_plzenec:0 "Kestenholz-Plzenec"',
        ' tarr_house_kestenholz_zant_arnolt:0 "Kestenholz-Zant-Arnolt"',
        ' tarr_house_kestenholz_sarema:0 "Kestenholz-Sâremâ"',
        ' tarr_house_kestenholz_swenigorot:0 "Kestenholz-Swenigorot"',
        ' tarr_house_kestenholz_metz:0 "Kestenholz-Metz"',
        ' tarr_house_kestenholz_bremen:0 "Kestenholz-Bremen"',
        ' tarr_house_kestenholz_dillingen:0 "Kestenholz-Dillingen"',
        ' tarr_house_kestenholz_orleans:0 "Kestenholz-Orleans"',
        ' tarr_house_kestenholz_merida:0 "Kestenholz-Mêrida"',
        ' tarr_house_kestenholz_terebovl:0 "Kestenholz-Terebovl"',
        ' tarr_house_kestenholz_zutphen:0 "Kestenholz-Zutphen"',
        ' tarr_house_kestenholz_lecce:0 "Kestenholz-Lecce"',
        ' tarr_house_kestenholz_saumur:0 "Kestenholz-Saumur"',
        ' tarr_house_kestenholz_buthrotum:0 "Kestenholz-Buthrotum"',
        ' tarr_house_kestenholz_annonay:0 "Kestenholz-Annonay"',
        ' tarr_house_kestenholz_fecamp:0 "Kestenholz-Fécamp"',
        ' tarr_house_kestenholz_albret:0 "Kestenholz-Albret"',
        ' tarr_house_kestenholz_flanders:0 "Kestenholz-Flanders"',
        ' tarr_house_kestenholz_geteina:0 "Kestenholz-Geteina"',
        ' tarr_house_kestenholz_tyddewi:0 "Kestenholz-Tyddewi"',
        ' tarr_house_kestenholz_cologne:0 "Kestenholz-Cologne"',
        ' tarr_house_kestenholz_pau:0 "Kestenholz-Pau"',
        ' tarr_house_kestenholz_sennar:0 "Kestenholz-Sennar"',
        ' tarr_house_kestenholz_blasien:0 "Kestenholz-Blasien"',
        ' tarr_house_kestenholz_moraca:0 "Kestenholz-Moraca"',
        ' tarr_house_kestenholz_vendome:0 "Kestenholz-Vendôme"',
        ' tarr_house_kestenholz_baht:0 "Kestenholz-Baht"',
        ' tarr_house_kestenholz_arnedo:0 "Kestenholz-Arnedo"',
        ' tarr_house_kestenholz_machynlleth:0 "Kestenholz-Machynlleth"',
        ' tarr_house_kestenholz_house_10882:0 "Kestenholz"',
        # Non-Chatenois cadet branches
        ' tarr_house_billung_erfurt:0 "Billung-Erfurt"',
        ' tarr_house_karling_litovel:0 "Karling-Litovel"',
        ' tarr_house_karling_hirsau:0 "Karling-Hirsau"',
        ' tarr_house_karling_troppouwe:0 "Karling-Troppouwe"',
        ' tarr_house_karling_ush:0 "Karling-Ush"',
        ' tarr_house_palemonaitis_middel_don:0 "Palemonaitis-Middel-Dôn"',
        ' tarr_house_palemonaitis_lielupe:0 "Palemonaitis-Lielupe"',
        ' tarr_house_palemonaitis_schaulen:0 "Palemonaitis-Schaulen"',
        ' tarr_house_palemonaitis_orsche:0 "Palemonaitis-Orsche"',
        ' tarr_house_palemonaitis_rasseinen:0 "Palemonaitis-Rassêinen"',
        ' tarr_house_palemonaitis_kukena:0 "Palemonaitis-Kukena"',
        ' tarr_house_umayyad_wichse:0 "Umayyad-Wîchsê"',
        ' tarr_house_reginar_sirakusan:0 "Reginar-Sirakusan"',
        ' tarr_house_gellones_wurle:0 "Gellones-Wurle"',
        ' tarr_house_cetchathach_uisnech:0 "Cétchathach-Uisnech"',
        ' tarr_house_ebrauc_uisnech:0 "Ebrauc-Uisnech"',
        ' tarr_house_hede_tzene:0 "Hede-Tzene"',
        ' tarr_house_borg_waga:0 "Borg-Wâga"',
        # Elevated dynasties
        ' tarr_house_plise:0 "iš Plesės"',
        ' tarr_house_berezina:0 "Berezina"',
        ' tarr_house_este:0 "Este"',
        ' tarr_house_alre:0 "Alre"',
        ' tarr_house_itze:0 "Îtze"',
        ' tarr_house_rokytna:0 "Rokytna"',
        ' tarr_house_goss:0 "Göss"',
        ' tarr_house_oster:0 "Ôster"',
        ' tarr_house_enns:0 "Enns"',
        ' tarr_house_sitzichow:0 "Sitzichow"',
        ' tarr_house_walgede:0 "Walgede"',
        ' tarr_house_wurle:0 "Wurle"',
        ' tarr_house_brunnsholm_sebesch:0 "Brunnsholm-Sebêsch"',
        ' tarr_house_philippopolis_ulpiana:0 "Philippopolis-Ulpiana"',
        ' tarr_house_sheksna_dwina:0 "Sheksna-Dwina"',
        ' tarr_house_soundavara_obnore:0 "Soundavara-Obnore"',
        ' tarr_house_soundavara_erkawika:0 "Soundavara-Erkawîka"',
    ])

    lines.append("")
    return "\r\n".join(lines)

def main():
    print(f"Reading gazetteer from: {GAZETTEER_PATH}")
    entries = parse_gazetteer(GAZETTEER_PATH)
    print(f"Total entries parsed: {len(entries)}")

    hist_diffs = [k for k, v in entries.items() if v['direct'] != v['hist']]
    print(f"Entries with 1059-1142 historical resolution (HIST != DIRECT): {len(hist_diffs)}")

    print(f"Reading dynastic register from: {DYNASTIC_REGISTER_PATH}")
    s2_entries, s3_entries, s4_entries = parse_dynastic_register(DYNASTIC_REGISTER_PATH)
    print(f"Dynastic register parsed: {len(s2_entries)} S2, {len(s3_entries)} S3, {len(s4_entries)} S4")

    # 1. Generate title scripted effects
    effects_content = build_scripted_effects(entries)
    EFFECTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(EFFECTS_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        f.write(effects_content)
    print(f"Wrote {len(effects_content.splitlines())} lines to {EFFECTS_PATH}")

    # 2. Generate dynastic & cultural scripted effects
    dynastic_effects_content = build_dynastic_scripted_effects(s2_entries, s3_entries, s4_entries)
    DYNASTIC_EFFECTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DYNASTIC_EFFECTS_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        f.write(dynastic_effects_content)
    print(f"Wrote {len(dynastic_effects_content.splitlines())} lines to {DYNASTIC_EFFECTS_PATH}")

    # 3. Generate localization YAML
    loc_content = build_localization(entries, s2_entries, s3_entries, s4_entries)
    LOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOC_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        f.write(loc_content)
    print(f"Wrote {len(loc_content.splitlines())} lines to {LOC_PATH}")

if __name__ == '__main__':
    main()

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
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GAZETTEER_PATH = REPO_ROOT / "tarraconian_titles_1059.md"
DYNASTIC_REGISTER_PATH = REPO_ROOT / "dynastic_realignment_register.md"
EFFECTS_PATH = REPO_ROOT / "tarraconian_chancellery" / "common" / "scripted_effects" / "tarr_chancellery_title_list_effects.txt"
DYNASTIC_EFFECTS_PATH = REPO_ROOT / "tarraconian_chancellery" / "common" / "scripted_effects" / "tarr_chancellery_dynastic_effects.txt"
LOC_PATH = REPO_ROOT / "tarraconian_chancellery" / "localization" / "english" / "tarraconian_titles_l_english.yml"
REPLACE_LOC_PATH = REPO_ROOT / "tarraconian_chancellery" / "localization" / "replace" / "english" / "tarraconian_dynasty_overrides_l_english.yml"

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
    if key in ('e_hre', 'h_roman_empire'):
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
        'Bengâlen': 'Bengâlisch',
        'Bihâr': 'Bihârisch',
        'Gondwâne': 'Gondwânisch',
        'Kâmarûpe': 'Kâmarûpisch',
        'Orisse': 'Orissisch',
        'Andhre': 'Andhrisch',
        'Karnâte': 'Karnâtisch',
        'Lanke': 'Lankisch',
        'Mahâraschtre': 'Mahâraschtrisch',
        'Tamilakam': 'Tamilakamisch',
        'Telingâne': 'Telingânisch',
        'Tschampe': 'Tschampisch',
        'Tschenle': 'Tschenlisch',
        'Angkôr': 'Angkôrisch',
        'Kabisajân': 'Kabisajânisch',
        'Ljûkjû': 'Ljûkjûisch',
        'Lusung': 'Lusungisch',
        'Maluku': 'Malukuisch',
        'Rûtschû': 'Rûtschûisch',
        'Sulawêsi': 'Sulawêsisch',
        'Hudschung Medîni': 'Hudschung-Medînisch',
        'Malajadwîpe': 'Malajadwîpisch',
        'Tandschungnagare': 'Tandschungnagarisch',
        'Jawakadwîpe': 'Jawakadwîpisch',
        'Dwârawatî': 'Dwârawatîisch',
        'Pagân': 'Pagânisch',
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
            m_hist = re.search(r'\[(1059|1122|1142|1154|1171)[^\]:]*?:\s*([^\]]+)\]', line)
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
            m_hist = re.search(r'\[(1059|1122|1142|1154|1171)[^\]:]*?:\s*([^\]]+)\]', line)
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
            m_hist = re.search(r'\[(1059|1122|1142|1154|1171)[^\]:]*?:\s*([^\]]+)\]', line)
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
        "\ttitle:c_munda.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_1218 HIST = cn_tarr_x_script_1218 } }",
        "\ttitle:c_pegu.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_1264 HIST = cn_tarr_x_script_1264 } }",
        "\ttitle:c_SUM_barus.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_1641 HIST = cn_tarr_x_script_1641 } }",
        "\ttitle:c_mentawai.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_2260 HIST = cn_tarr_x_script_2260 } }",
        "\ttitle:c_PHI_zamboanga.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_2623 HIST = cn_tarr_x_script_2623 } }",
        "\ttitle:c_kodalaka_mandala.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_2626 HIST = cn_tarr_x_script_2626 } }",
        "\ttitle:c_kyaukse.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_2637 HIST = cn_tarr_x_script_2637 } }",
        "\ttitle:c_puri.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_2975 HIST = cn_tarr_x_script_2975 } }",
        "\ttitle:c_nakkavaram.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_3253 HIST = cn_tarr_x_script_3253 } }",
        "\ttitle:c_SuMa_luwu.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_3987 HIST = cn_tarr_x_script_3987 } }",
        "\ttitle:c_binh_long.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_5215 HIST = cn_tarr_x_script_5215 } }",
        "\ttitle:c_koh_ker.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_5703 HIST = cn_tarr_x_script_5703 } }",
        "\ttitle:c_rayapura.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_5729 HIST = cn_tarr_x_script_5729 } }",
        "\ttitle:c_sran.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_6299 HIST = cn_tarr_x_script_6299 } }",
        "\ttitle:c_kanchipuram.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_7177 HIST = cn_tarr_x_script_7177 } }",
        "\ttitle:c_panaji.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_7430 HIST = cn_tarr_x_script_7430 } }",
        "\ttitle:c_papua_selatan.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_7455 HIST = cn_tarr_x_script_7455 } }",
        "\ttitle:c_kepala_burung.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_7781 HIST = cn_tarr_x_script_7781 } }",
        "\ttitle:c_east_darfur.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_8252 HIST = cn_tarr_x_script_8252 } }",
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
        "\t# 0. V3 House Localization Key Migration Block",
        "\t# Clears legacy tarr_pin_* locks once so existing saves update from unlocalized",
        "\t# literal dynn_tarr_* keys to localized dynn_tarr_* keys.",
        "\t# =========================================================================",
        "\tif = {",
        "\t\tlimit = {",
        "\t\t\tNOT = { has_global_variable = tarr_v3_dynasty_loc_migration }",
        "\t\t}",
        "\t\tset_global_variable = { name = tarr_v3_dynasty_loc_migration value = yes }",
        "\t\tremove_global_variable = tarr_pin_1652",
        "\t\tremove_global_variable = tarr_pin_12726",
        "\t\tremove_global_variable = tarr_pin_13928",
        "\t\tremove_global_variable = tarr_pin_17334",
        "\t\tremove_global_variable = tarr_pin_18111",
        "\t\tremove_global_variable = tarr_pin_18122",
        "\t\tremove_global_variable = tarr_pin_18311",
        "\t\tremove_global_variable = tarr_pin_18404",
        "\t\tremove_global_variable = tarr_pin_19355",
        "\t\tremove_global_variable = tarr_pin_19476",
        "\t\tremove_global_variable = tarr_pin_20743",
        "\t\tremove_global_variable = tarr_pin_21733",
        "\t\tremove_global_variable = tarr_pin_21816",
        "\t\tremove_global_variable = tarr_pin_22244",
        "\t\tremove_global_variable = tarr_pin_22345",
        "\t\tremove_global_variable = tarr_pin_22711",
        "\t\tremove_global_variable = tarr_pin_23237",
        "\t\tremove_global_variable = tarr_pin_23369",
        "\t\tremove_global_variable = tarr_pin_23583",
        "\t\tremove_global_variable = tarr_pin_23892",
        "\t\tremove_global_variable = tarr_pin_24293",
        "\t\tremove_global_variable = tarr_pin_24307",
        "\t\tremove_global_variable = tarr_pin_24355",
        "\t\tremove_global_variable = tarr_pin_24384",
        "\t\tremove_global_variable = tarr_pin_24454",
        "\t\tremove_global_variable = tarr_pin_24600",
        "\t\tremove_global_variable = tarr_pin_24627",
        "\t\tremove_global_variable = tarr_pin_24655",
        "\t\tremove_global_variable = tarr_pin_25132",
        "\t\tremove_global_variable = tarr_pin_25175",
        "\t\tremove_global_variable = tarr_pin_25655",
        "\t\tremove_global_variable = tarr_pin_25659",
        "\t\tremove_global_variable = tarr_pin_25769",
        "\t\tremove_global_variable = tarr_pin_25935",
        "\t\tremove_global_variable = tarr_pin_26275",
        "\t\tremove_global_variable = tarr_pin_26438",
        "\t\tremove_global_variable = tarr_pin_26541",
        "\t\tremove_global_variable = tarr_pin_26581",
        "\t\tremove_global_variable = tarr_pin_26913",
        "\t\tremove_global_variable = tarr_pin_26976",
        "\t\tremove_global_variable = tarr_pin_27311",
        "\t\tremove_global_variable = tarr_pin_27663",
        "\t\tremove_global_variable = tarr_pin_27674",
        "\t\tremove_global_variable = tarr_pin_27863",
        "\t\tremove_global_variable = tarr_pin_27907",
        "\t\tremove_global_variable = tarr_pin_28114",
        "\t\tremove_global_variable = tarr_pin_28330",
        "\t\tremove_global_variable = tarr_pin_28856",
        "\t\tremove_global_variable = tarr_pin_16789468",
        "\t\tremove_global_variable = tarr_pin_16790779",
        "\t\tremove_global_variable = tarr_pin_16791696",
        "\t\tremove_global_variable = tarr_pin_16793861",
        "\t\tremove_global_variable = tarr_pin_16796257",
        "\t\tremove_global_variable = tarr_pin_16796344",
        "\t\tremove_global_variable = tarr_pin_16796949",
        "\t\tremove_global_variable = tarr_pin_16796964",
        "\t\tremove_global_variable = tarr_pin_16797465",
        "\t\tremove_global_variable = tarr_pin_16798500",
        "\t\tremove_global_variable = tarr_pin_16799007",
        "\t\tremove_global_variable = tarr_pin_16799191",
        "\t\tremove_global_variable = tarr_pin_16799240",
        "\t\tremove_global_variable = tarr_pin_16799847",
        "\t\tremove_global_variable = tarr_pin_16800136",
        "\t\tremove_global_variable = tarr_pin_16800196",
        "\t\tremove_global_variable = tarr_pin_16800201",
        "\t\tremove_global_variable = tarr_pin_16800883",
        "\t\tremove_global_variable = tarr_pin_16801742",
        "\t\tremove_global_variable = tarr_pin_16801965",
        "\t\tremove_global_variable = tarr_pin_16802071",
        "\t\tremove_global_variable = tarr_pin_16802188",
        "\t\tremove_global_variable = tarr_pin_16802581",
        "\t\tremove_global_variable = tarr_pin_16803030",
        "\t\tremove_global_variable = tarr_pin_16803302",
        "\t\tremove_global_variable = tarr_pin_16804037",
        "\t\tremove_global_variable = tarr_pin_33566549",
        "\t\tremove_global_variable = tarr_pin_33568115",
        "\t\tremove_global_variable = tarr_pin_33569509",
        "\t\tremove_global_variable = tarr_pin_33571287",
        "\t\tremove_global_variable = tarr_pin_33572174",
        "\t\tremove_global_variable = tarr_pin_33573102",
        "\t\tremove_global_variable = tarr_pin_33574710",
        "\t\tremove_global_variable = tarr_pin_33574947",
        "\t\tremove_global_variable = tarr_pin_33577966",
        "\t\tremove_global_variable = tarr_pin_50343822",
        "\t\tremove_global_variable = tarr_pin_50346404",
        "\t\tremove_global_variable = tarr_pin_50347588",
        "\t\tremove_global_variable = tarr_pin_50348946",
        "\t\tremove_global_variable = tarr_pin_50349259",
        "\t\tremove_global_variable = tarr_pin_50353419",
        "\t\tremove_global_variable = tarr_pin_67124011",
        "\t\tremove_global_variable = tarr_pin_67125621",
        "\t\tremove_global_variable = tarr_pin_67131755",
        "\t}",
        "\t# =========================================================================",
        "\t# 1. Dynamic Emergent Cultures (set_culture_name)",
        "\t# Scoped via every_culture_global using unique pillar / name_list / tradition",
        "\t# signatures, overwriting stale save-baked culture names while protecting Tarraconian.",
        "\t# =========================================================================",
    ]

    # Exact 1/394 unique predicates verified against last_save.ck3 (0 static vanilla collisions)
    culture_predicates = {
        '260': (
            ['heritage_west_slavic', 'language_lechitic', 'ethos_egalitarian'],
            [],
            ['tradition_hereditary_hierarchy'],
        ),
        '270': (
            ['heritage_east_slavic', 'language_east_slavic', 'ethos_stoic'],
            ['name_list_russian'],
            ['tradition_hard_working'],
        ),
        '275': (
            ['heritage_vlach', 'language_wallachian', 'ethos_bureaucratic'],
            [],
            [],
        ),
        '279': (
            ['heritage_central_germanic', 'language_high_german', 'ethos_stoic'],
            ['name_list_bavarian'],
            [],
        ),
        '286': (
            ['heritage_west_slavic', 'language_lechitic', 'ethos_egalitarian'],
            [],
            ['tradition_mountaineer_ruralism'],
        ),
        '288': (
            ['heritage_vlach', 'language_wallachian', 'ethos_spiritual'],
            [],
            [],
        ),
        '293': (
            ['heritage_magyar', 'language_wallachian', 'ethos_spiritual'],
            [],
            [],
        ),
        '303': (
            ['heritage_central_germanic', 'language_high_german', 'ethos_spiritual'],
            ['name_list_franconian'],
            [],
        ),
        '331': (
            ['heritage_east_slavic', 'language_east_slavic', 'ethos_stoic'],
            ['name_list_russian'],
            ['tradition_stand_and_fight'],
        ),
        '338': (
            ['heritage_byzantine', 'language_slavonic', 'ethos_stoic'],
            [],
            [],
        ),
        '358': (
            ['heritage_turkic', 'language_oghur', 'ethos_bellicose'],
            ['name_list_khazar'],
            ['tradition_stand_and_fight'],
        ),
        '367': (
            ['heritage_central_germanic', 'language_magyar', 'ethos_bellicose'],
            [],
            [],
        ),
    }

    for c in s4_entries:
        cid = c['culture_id']
        pillars, name_lists, traditions = culture_predicates[cid]
        lines.extend([
            f"\t# Culture {cid}: {c['current_name']} -> {c['realigned_name']} ({c['tarr_name']})",
            "\tevery_culture_global = {",
            "\t\tlimit = {",
            "\t\t\tNOT = { this = title:c_barcelona.culture }",
            "\t\t\ttrigger_if = {",
            "\t\t\t\tlimit = { has_global_variable = tarr_culture }",
            "\t\t\t\tNOT = { this = global_var:tarr_culture }",
            "\t\t\t}",
        ])
        for p in pillars:
            lines.append(f"\t\t\thas_cultural_pillar = {p}")
        for nl in name_lists:
            lines.append(f"\t\t\thas_name_list = {nl}")
        for tr in traditions:
            lines.append(f"\t\t\thas_cultural_tradition = {tr}")
        lines.extend([
            "\t\t}",
            "\t\tif = {",
            "\t\t\tlimit = { has_global_variable = tarr_direct_mode }",
            "\t\t\tset_culture_name = {",
            f"\t\t\t\tnoun = tarr_culture_{cid}_tarr_name",
            f"\t\t\t\tcollective_noun = tarr_culture_{cid}_tarr_collective",
            f"\t\t\t\tprefix = tarr_culture_{cid}_tarr_prefix",
            "\t\t\t}",
            "\t\t}",
            "\t\telse = {",
            "\t\t\tset_culture_name = {",
            f"\t\t\t\tnoun = tarr_culture_{cid}_name",
            f"\t\t\t\tcollective_noun = tarr_culture_{cid}_collective",
            f"\t\t\t\tprefix = tarr_culture_{cid}_prefix",
            "\t\t\t}",
            "\t\t}",
            "\t}",
        ])

    # Vanilla multi-house / named dynasties excluded from unrelated dynamic elevated rules
    excluded_vanilla_dynasties = [
        '667', '25061', '656', '100217', '9116', '7198',
        '597', '9217', '1029002', '836', '830', '4039',
    ]

    def append_house_apply(indent: str, hid: str, loc_key: str, tag: str, rename_dyn: bool = False):
        lines.extend([
            f"{indent}house = {{",
            f"{indent}\tset_house_name = {loc_key}",
            f"{indent}\tset_variable = {{ name = tarr_house_tag value = flag:{tag} }}",
            f"{indent}}}",
        ])
        if rename_dyn:
            lines.append(f"{indent}dynasty ?= {{ set_dynasty_name = {loc_key} }}")
        lines.append(f"{indent}set_global_variable = {{ name = tarr_pin_{hid} value = yes }}")

    def append_char_limit_block(indent: str, hid: str, loc_key: str, tag: str,
                                dyn_key: str = None, exclude_vanilla: bool = False,
                                rename_dyn: bool = False, extra_limits=None):
        lines.extend([
            f"{indent}if = {{",
            f"{indent}\tlimit = {{",
            f"{indent}\t\texists = house",
            f"{indent}\t\thouse = {{",
            f"{indent}\t\t\tOR = {{",
            f"{indent}\t\t\t\tNOT = {{ has_variable = tarr_house_tag }}",
            f"{indent}\t\t\t\tvar:tarr_house_tag = flag:{tag}",
            f"{indent}\t\t\t}}",
            f"{indent}\t\t}}",
        ])
        if dyn_key is not None:
            lines.append(f"{indent}\t\tdynasty ?= dynasty:{dyn_key}")
        if exclude_vanilla:
            lines.append(f"{indent}\t\tNOR = {{")
            for vd in excluded_vanilla_dynasties:
                lines.append(f"{indent}\t\t\tdynasty ?= dynasty:{vd}")
            lines.append(f"{indent}\t\t}}")
        if extra_limits:
            for ex in extra_limits:
                lines.append(f"{indent}\t\t{ex}")
        lines.append(f"{indent}\t}}")
        append_house_apply(indent + "\t", hid, loc_key, tag, rename_dyn=rename_dyn)
        lines.append(f"{indent}}}")

    def emit_title_rule(hid: str, comment: str, titles, loc_key: str, tag: str,
                        rel_scope: str = None, dyn_key: str = None,
                        exclude_vanilla: bool = False, rename_dyn: bool = False):
        lines.extend([
            f"\t# House {hid}: {comment}",
            "\tif = {",
            f"\t\tlimit = {{ NOT = {{ has_global_variable = tarr_pin_{hid} }} }}",
        ])
        for t in titles:
            scope_expr = f"title:{t}.holder.{rel_scope}" if rel_scope else f"title:{t}.holder"
            lines.append(f"\t\t{scope_expr} ?= {{")
            append_char_limit_block("\t\t\t", hid, loc_key, tag, dyn_key=dyn_key,
                                    exclude_vanilla=exclude_vanilla, rename_dyn=rename_dyn)
            lines.append("\t\t}")
        lines.append("\t}")

    def emit_courtier_rule(hid: str, comment: str, titles, loc_key: str, tag: str,
                           dyn_key: str = None, exclude_vanilla: bool = False,
                           rename_dyn: bool = False, extra_limits=None):
        lines.extend([
            f"\t# House {hid}: {comment}",
            "\tif = {",
            f"\t\tlimit = {{ NOT = {{ has_global_variable = tarr_pin_{hid} }} }}",
        ])
        for t in titles:
            lines.extend([
                f"\t\ttitle:{t}.holder ?= {{",
                "\t\t\tevery_courtier_or_guest = {",
            ])
            append_char_limit_block("\t\t\t\t", hid, loc_key, tag, dyn_key=dyn_key,
                                    exclude_vanilla=exclude_vanilla, rename_dyn=rename_dyn,
                                    extra_limits=extra_limits)
            lines.extend(["\t\t\t}", "\t\t}"])
        lines.append("\t}")

    def emit_domicile_rule(hid: str, comment: str, dyn_key: str, county: str, loc_key: str, tag: str):
        lines.extend([
            f"\t# House {hid}: {comment}",
            "\tif = {",
            f"\t\tlimit = {{ NOT = {{ has_global_variable = tarr_pin_{hid} }} }}",
            f"\t\tdynasty:{dyn_key} ?= {{",
            "\t\t\tevery_dynasty_member = {",
            "\t\t\t\tlimit = {",
            "\t\t\t\t\tis_alive = yes",
            "\t\t\t\t\texists = domicile",
            f"\t\t\t\t\tdomicile.domicile_location.county ?= title:{county}",
            "\t\t\t\t}",
        ])
        append_char_limit_block("\t\t\t\t", hid, loc_key, tag, dyn_key=dyn_key)
        lines.extend(["\t\t\t}", "\t\t}", "\t}"])

    lines.extend([
        "",
        "\t# =========================================================================",
        "\t# 2. Collateral Damage Restorations (V1 Script Recoveries)",
        "\t# Restores unrelated dynasties/houses misnamed by prior unguarded runs.",
        "\t# =========================================================================",
    ])

    collateral_unrelated = [
        ('16793861', 'Restore Suerbeer (previously overwritten by Berezina)', ['c_berlin', 'c_novosil', 'c_wormditt'], 'dynn_Suerbeer', 'suerbeer', True),
        ('18404', 'Restore Sachsen (previously overwritten by iš Plesės)', ['c_novogrudok', 'd_pinsk'], 'dynn_Sachsen', 'sachsen', True),
        ('21733', 'Restore Gnezdovo (previously overwritten by iš Plesės)', ['d_minsk', 'c_minsk', 'c_thouars'], 'dynn_tarr_gnezdovo', 'gnezdovo', True),
        ('28330', 'Restore Xu (previously overwritten by Alre)', ['c_lanzhou'], 'dynn_Xu_8BB8', 'xu_8bb8', True),
    ]
    for hid, comment, titles, loc_key, tag, rename_dyn in collateral_unrelated:
        emit_title_rule(hid, comment, titles, loc_key, tag, exclude_vanilla=True, rename_dyn=rename_dyn)

    emit_title_rule('1652', 'Restore House Hede founder branch (previously clobbered by age=37)',
                    ['c_memar'], 'dynn_Hede', 'hede', rel_scope='primary_spouse', dyn_key='836')
    emit_title_rule('33572174', 'Restore Borg-Morarna (previously clobbered by is_female=yes)',
                    ['c_SUM_barus'], 'dynn_tarr_borg_morarna', 'borg_morarna', rel_scope='primary_spouse', dyn_key='830')

    lines.extend([
        "",
        "\t# =========================================================================",
        "\t# 3. Imperial Cadet Branches (House Kestenholz / Chatenois - dynasty:667)",
        "\t# Covers all living Kestenholz cadet branches with character-scoped dynasty:667",
        "\t# guards and house variable pinning (direct holders first, then courtier/domicile).",
        "\t# =========================================================================",
    ])

    kestenholz_direct = [
        ('13928', 'Chatenois-Metz -> Kestenholz-Metz (restore from Wurle)', ['h_roman_empire', 'c_barcelona', 'd_jabal_kufs', 'c_bampur'], 'dynn_tarr_kestenholz_metz', 'kestenholz_metz'),
        ('19476', 'Chatenois-Ravenna -> Kestenholz-Raben', ['d_westfalen', 'c_osnabruck', 'd_lombardia', 'd_prussia'], 'dynn_tarr_kestenholz_raben', 'kestenholz_raben'),
        ('16791696', 'Chatenois-Saumur -> Kestenholz-Saumur', ['d_smolensk', 'd_somerset', 'd_bihar', 'c_bihar', 'c_tadla'], 'dynn_tarr_kestenholz_saumur', 'kestenholz_saumur'),
        ('18311', 'Chatenois-Annonay -> Kestenholz-Annonay', ['d_hesse', 'd_luki', 'd_novgorod', 'c_novgorod', 'c_rusa'], 'dynn_tarr_kestenholz_annonay', 'kestenholz_annonay'),
        ('22711', 'dynn_Bluome -> Kestenholz-Bluome', ['k_navarra', 'c_viscaya', 'c_vastergotland'], 'dynn_tarr_kestenholz_bluome', 'kestenholz_bluome'),
        ('16799240', 'Chatenois-Fécamp -> Kestenholz-Fécamp', ['d_deheubarth', 'd_lower_silesia', 'd_mazovia', 'c_breslau'], 'dynn_tarr_kestenholz_fecamp', 'kestenholz_fecamp'),
        ('18122', 'Chatenois-Albret -> Kestenholz-Albret', ['c_sevede', 'c_eschenlohe', 'd_opolye'], 'dynn_tarr_kestenholz_albret', 'kestenholz_albret'),
        ('16796964', 'Flanders -> Kestenholz-Flanders (restore from Kestenholz-Arnedo)', ['k_andalusia', 'd_sevilla', 'd_carinthia', 'c_karnten', 'c_munchen'], 'dynn_tarr_kestenholz_flanders', 'kestenholz_flanders'),
        ('16790779', 'Chatenois-Geteina -> Kestenholz-Geteina', ['d_thracesia', 'c_gezira'], 'dynn_tarr_kestenholz_geteina', 'kestenholz_geteina'),
        ('16797465', 'Chatenois-Dillingen -> Kestenholz-Dillingen', ['c_kaiserslautern', 'd_paphlagonia', 'c_paphlagonia', 'c_zichia'], 'dynn_tarr_kestenholz_dillingen', 'kestenholz_dillingen'),
        ('16796344', 'dynn_Carenwall -> Kestenholz-Carenwall (restore from Walgede)', ['d_sebasteia', 'c_sebasteia', 'c_hont', 'c_lipto'], 'dynn_tarr_kestenholz_carenwall', 'kestenholz_carenwall'),
        ('16799847', 'dynn_Carenwall -> Kestenholz-Carenwall', ['k_galicia-volhynia', 'c_el_fasher', 'd_ulster', 'c_ulster'], 'dynn_tarr_kestenholz_carenwall', 'kestenholz_carenwall'),
        ('28856', 'dynn_Carenwall -> Kestenholz-Carenwall (Duklja/Usora branch)', ['d_usora', 'c_zachlumia'], 'dynn_tarr_kestenholz_carenwall', 'kestenholz_carenwall'),
        ('50346404', 'Chatenois-Amersfoort -> Kestenholz-Utrecht', ['d_alwa', 'c_alodia', 'd_sanaag', 'd_kanem'], 'dynn_tarr_kestenholz_utrecht', 'kestenholz_utrecht'),
        ('50348946', 'Chatenois-Koschmin -> Kestenholz-Kalisch', ['d_iceland', 'c_wschowska', 'b_prades_rossello'], 'dynn_tarr_kestenholz_kalisch', 'kestenholz_kalisch'),
        ('50347588', 'Chatenois-Hirschberg -> Kestenholz-Legnica', ['d_nordgau', 'c_eichstadt', 'c_ljubljana', 'c_korinthos'], 'dynn_tarr_kestenholz_legnica', 'kestenholz_legnica'),
        ('16799191', 'Chatenois-Tyddewi -> Kestenholz-Tyddewi', ['c_beszterce', 'c_stoenesti', 'c_guizhou_2'], 'dynn_tarr_kestenholz_tyddewi', 'kestenholz_tyddewi'),
        ('24384', 'Chatenois-Kammersberg -> Kestenholz-Judenburch', ['d_albany', 'c_baqlin', 'c_djarin'], 'dynn_tarr_kestenholz_judenburch', 'kestenholz_judenburch'),
        ('16798500', 'dynn_Diest -> Kestenholz-Diest', ['b_olot', 'c_satif', 'c_tiris'], 'dynn_tarr_kestenholz_diest', 'kestenholz_diest'),
        ('27663', 'dynn_Orlamunde -> Kestenholz-Orlamunde', ['c_boleslav', 'c_rennes', 'c_clermont_sur_allier'], 'dynn_tarr_kestenholz_orlamunde', 'kestenholz_orlamunde'),
        ('33573102', 'Cologne -> Kestenholz-Cologne', ['c_pavia'], 'dynn_tarr_kestenholz_cologne', 'kestenholz_cologne'),
        ('23583', 'Chatenois-Peiting -> Kestenholz-Altenstadt', ['k_bohemia', 'd_bohemia', 'c_praha', 'd_asturias'], 'dynn_tarr_kestenholz_altenstadt', 'kestenholz_altenstadt'),
        ('19355', 'Chatenois-Pau -> Kestenholz-Pau', ['c_hallstatt'], 'dynn_tarr_kestenholz_pau', 'kestenholz_pau'),
        ('25132', 'Chatenois-Orléans -> Kestenholz-Orleans', ['b_balaguer'], 'dynn_tarr_kestenholz_orleans', 'kestenholz_orleans'),
        ('25659', 'Chatenois-Mérida -> Kestenholz-Mêrida', ['d_badajoz', 'c_badajoz', 'd_castilla', 'b_vic'], 'dynn_tarr_kestenholz_merida', 'kestenholz_merida'),
        ('16796257', 'Chatenois-Swenigorot -> Kestenholz-Swenigorot', ['c_iasi', 'd_kuyavia', 'c_campulung'], 'dynn_tarr_kestenholz_swenigorot', 'kestenholz_swenigorot'),
        ('23237', 'Chatenois-Sennar -> Kestenholz-Sennar (restore from Arnedo)', ['c_hohenau'], 'dynn_tarr_kestenholz_sennar', 'kestenholz_sennar'),
        ('25175', 'Chatenois-Blasien -> Kestenholz-Blasien', ['d_anhalt', 'c_dessau'], 'dynn_tarr_kestenholz_blasien', 'kestenholz_blasien'),
        ('25769', 'Chatenois-Bechyně -> Kestenholz-Bechin', ['b_talekan'], 'dynn_tarr_kestenholz_bechin', 'kestenholz_bechin'),
        ('16789468', 'Chatenois-Stężyca -> Kestenholz-Sitzichow', ['d_rashka', 'c_rashka', 'd_flanders', 'c_brugge'], 'dynn_tarr_kestenholz_sitzichow', 'kestenholz_sitzichow'),
        ('16802188', 'dynn_Gudensberg -> Kestenholz-Gudensberch', ['d_aleppo', 'c_aleppo', 'd_pereyaslavl', 'c_pereyaslavl'], 'dynn_tarr_kestenholz_gudensberch', 'kestenholz_gudensberch'),
        ('26541', 'Chatenois-Moraca -> Kestenholz-Moraca', ['d_duklja', 'c_duklja'], 'dynn_tarr_kestenholz_moraca', 'kestenholz_moraca'),
        ('26581', 'Chatenois-Berg -> Kestenholz-Berch', ['k_lotharingia', 'd_luxembourg', 'd_bornu'], 'dynn_tarr_kestenholz_berch', 'kestenholz_berch'),
        ('25655', 'Chatenois-Terebovl -> Kestenholz-Terebovl', ['k_castille', 'd_northumberland', 'd_don_valley', 'c_voronezh'], 'dynn_tarr_kestenholz_terebovl', 'kestenholz_terebovl'),
        ('22345', 'Chatenois-Mons -> Kestenholz-Bergen', ['c_tripolitana'], 'dynn_tarr_kestenholz_bergen', 'kestenholz_bergen'),
        ('18111', 'Chatenois-Bremen -> Kestenholz-Bremen', ['c_mainz'], 'dynn_tarr_kestenholz_bremen', 'kestenholz_bremen'),
        ('26913', 'Chatenois-Sargans -> Kestenholz-Kûr', ['d_currezia', 'c_grisons', 'd_kaffa'], 'dynn_tarr_kestenholz_kur', 'kestenholz_kur'),
        ('16802581', 'Chatenois-Vendôme -> Kestenholz-Vendôme', ['d_orleans', 'c_orleans'], 'dynn_tarr_kestenholz_vendome', 'kestenholz_vendome'),
        ('16801965', 'dynn_Suerbeer -> Kestenholz-Suerbeer', ['d_azov', 'c_tmutarakan'], 'dynn_tarr_kestenholz_suerbeer', 'kestenholz_suerbeer'),
        ('24627', 'Chatenois-Zutphen -> Kestenholz-Zutphen', ['d_gelre', 'c_guelders', 'c_zagorje'], 'dynn_tarr_kestenholz_zutphen', 'kestenholz_zutphen'),
        ('16802071', 'dynn_Muhlhausen -> Kestenholz-Muhlhausen', ['k_sardinia', 'c_cagliari'], 'dynn_tarr_kestenholz_muhlhausen', 'kestenholz_muhlhausen'),
        ('27907', 'dynn_O_sel -> Kestenholz-Sâremâ', ['d_alger', 'c_algier'], 'dynn_tarr_kestenholz_sarema', 'kestenholz_sarema'),
        ('23892', 'Chatenois-Baht -> Kestenholz-Baht', ['d_fes', 'c_fes'], 'dynn_tarr_kestenholz_baht', 'kestenholz_baht'),
        ('50353419', 'Chatenois-Capua -> Kestenholz-Capua (restore from Walgede)', ['d_capua', 'c_capua', 'd_viken'], 'dynn_tarr_kestenholz_capua', 'kestenholz_capua'),
    ]
    for hid, comment, titles, loc_key, tag in kestenholz_direct:
        emit_title_rule(hid, comment, titles, loc_key, tag, dyn_key='667')

    # Unlanded Kestenholz spouses, courtiers & unique noble-family domiciles
    emit_title_rule('24600', 'Chatenois-Arnedo -> Kestenholz-Arnedo (via d_moravia spouse)',
                    ['d_moravia'], 'dynn_tarr_kestenholz_arnedo', 'kestenholz_arnedo',
                    rel_scope='primary_spouse', dyn_key='667')
    emit_title_rule('26976', 'Chatenois-Lecce -> Kestenholz-Lecce (via c_eman_yerenhe spouse)',
                    ['c_eman_yerenhe'], 'dynn_tarr_kestenholz_lecce', 'kestenholz_lecce',
                    rel_scope='primary_spouse', dyn_key='667')
    emit_domicile_rule('26275', 'Chatenois-Buthrotum -> Kestenholz-Buthrotum (domicile c_cephalonia)',
                       '667', 'c_cephalonia', 'dynn_tarr_kestenholz_buthrotum', 'kestenholz_buthrotum')
    emit_domicile_rule('20743', 'Flanders -> Kestenholz-Flanders (domicile c_venezia)',
                       '667', 'c_venezia', 'dynn_tarr_kestenholz_flanders', 'kestenholz_flanders')
    emit_domicile_rule('24655', 'Chatenois-Plzeň -> Kestenholz-Plzenec (domicile c_regensburg)',
                       '667', 'c_regensburg', 'dynn_tarr_kestenholz_plzenec', 'kestenholz_plzenec')
    emit_domicile_rule('33566549', 'Chatenois-Saarbrücken -> Kestenholz-Zant-Arnolt (domicile c_valencia)',
                       '667', 'c_valencia', 'dynn_tarr_kestenholz_zant_arnolt', 'kestenholz_zant_arnolt')
    # Runs AFTER 13928 & 22711 are tagged so NOT = { has_variable = tarr_house_tag } isolates 16799007 cleanly
    emit_courtier_rule('16799007', 'dynn_Verona -> Kestenholz-Verona (untagged dynasty:667 in c_najran court)',
                       ['c_najran'], 'dynn_tarr_kestenholz_verona', 'kestenholz_verona', dyn_key='667')

    lines.extend([
        "",
        "\t# =========================================================================",
        "\t# 4. Non-Chatenois Historical Cadet Branches & Dynasties (Section 2)",
        "\t# =========================================================================",
    ])

    vanilla_cadet_direct = [
        ('33574710', 'Billung-Gleichen -> Billung-Erfurt', ['c_marmaros', 'c_shamir'], '656', 'dynn_tarr_billung_erfurt', 'billung_erfurt'),
        ('16800201', 'Gellones-Güstrow -> Gellones-Wurle', ['c_more', 'c_rugen', 'd_angria', 'c_minden'], '100217', 'dynn_tarr_gellones_wurle', 'gellones_wurle'),
        ('50343822', 'Karling-Uničov -> Karling-Litovel', ['c_jihlava', 'd_bukovina', 'c_suceava'], '25061', 'dynn_tarr_karling_litovel', 'karling_litovel'),
        ('33571287', 'Karling-Korosten -> Karling-Ush', ['c_sagami'], '25061', 'dynn_tarr_karling_ush', 'karling_ush'),
        ('16800883', 'Palemonaitis-Jurmala -> Palemonaitis-Lielupe', ['c_selpils'], '9116', 'dynn_tarr_palemonaitis_lielupe', 'palemonaitis_lielupe'),
        ('67131755', 'Reginar-Vecchio -> Reginar-Sirakusan', ['d_alsace', 'c_strassburg', 'd_corsica', 'c_ajaccio', 'd_aksay'], '7198', 'dynn_tarr_reginar_sirakusan', 'reginar_sirakusan'),
        ('26438', 'Hede-Kazanskaya -> Hede-Middel-Dôn (restore from Hede-Tzene)', ['d_latgalians', 'c_talava'], '836', 'dynn_tarr_hede_middel_don', 'hede_middel_don'),
    ]
    for hid, comment, titles, dyn_key, loc_key, tag in vanilla_cadet_direct:
        emit_title_rule(hid, comment, titles, loc_key, tag, dyn_key=dyn_key)

    # Single-house S2 dynn_* conversions (excluding multi-house vanilla dynasties)
    single_house_s2 = [
        ('22244', 'dynn_Luxembourg -> Echternach', ['c_vermandois'], 'dynn_tarr_echternach', 'echternach', True),
        ('27863', 'dynn_Pernstein -> Swratka', ['d_qilian', 'c_qilin'], 'dynn_tarr_swratka', 'swratka', True),
        ('24454', 'dynn_Silesia-Glogau -> Silesia-Dziadosz', ['c_carcassonne'], 'dynn_tarr_silesia_dziadosz', 'silesia_dziadosz', True),
        ('16803030', 'dynn_Tula -> Prôntzich', ['b_dori'], 'dynn_tarr_prontzich', 'prontzich', True),
        ('16804037', 'dynn_der_Mark -> Soest', ['c_linlithgowshire'], 'dynn_tarr_soest', 'soest', True),
    ]
    for hid, comment, titles, loc_key, tag, rename_dyn in single_house_s2:
        emit_title_rule(hid, comment, titles, loc_key, tag, exclude_vanilla=True, rename_dyn=rename_dyn)

    emit_courtier_rule('67124011', 'dynn_Wittenberg -> Belzig (dynasty:4039 in d_powys court)',
                       ['d_powys'], 'dynn_tarr_belzig', 'belzig', dyn_key='4039')
    emit_courtier_rule('12726', 'Karling-Calw -> Karling-Hirsau (dynasty:25061 in d_kiev court)',
                       ['d_kiev'], 'dynn_tarr_karling_hirsau', 'karling_hirsau', dyn_key='25061')
    emit_domicile_rule('12726', 'Karling-Calw -> Karling-Hirsau (domicile c_aachen fallback)',
                       '25061', 'c_aachen', 'dynn_tarr_karling_hirsau', 'karling_hirsau')
    emit_courtier_rule('33577966', 'Umayyad-Povenets -> Umayyad-Wîchsê (dynasty:597 in d_chudia court)',
                       ['d_chudia'], 'dynn_tarr_umayyad_wichse', 'umayyad_wichse', dyn_key='597')
    emit_domicile_rule('27311', 'Hede-Tambov -> Hede-Tzene (dynasty:836 domicile c_northumberland)',
                       '836', 'c_northumberland', 'dynn_tarr_hede_tzene', 'hede_tzene')
    emit_title_rule('16796949', 'Borg-Shenkursk -> Borg-Wâga (via c_darcha spouse)',
                    ['c_darcha'], 'dynn_tarr_borg_waga', 'borg_waga', rel_scope='primary_spouse', dyn_key='830')

    # Palemonaitis (dynasty:9116) relational chain in strict order
    emit_title_rule('33574947', 'Palemonaitis-Kokenois -> Palemonaitis-Kukena (via c_selpils spouse)',
                    ['c_selpils'], 'dynn_tarr_palemonaitis_kukena', 'palemonaitis_kukena',
                    rel_scope='primary_spouse', dyn_key='9116')
    emit_title_rule('24355', 'Palemonaitis-Raseiniai -> Palemonaitis-Rassêinen (via d_vologda spouse)',
                    ['d_vologda'], 'dynn_tarr_palemonaitis_rasseinen', 'palemonaitis_rasseinen',
                    rel_scope='primary_spouse', dyn_key='9116')
    emit_courtier_rule('24293', 'Palemonaitis-Orsha -> Palemonaitis-Orsche (via c_zemigalians court)',
                       ['c_zemigalians'], 'dynn_tarr_palemonaitis_orsche', 'palemonaitis_orsche', dyn_key='9116')
    lines.extend([
        "\t# House 24307: Palemonaitis-Kazanskaya -> Palemonaitis-Middel-Dôn (via d_gotland & d_pamir guests)",
        "\tif = {",
        "\t\tlimit = { NOT = { has_global_variable = tarr_pin_24307 } }",
        "\t\ttitle:d_gotland.holder ?= {",
        "\t\t\tevery_courtier_or_guest = {",
        "\t\t\t\tlimit = {",
        "\t\t\t\t\tdynasty ?= dynasty:9116",
        "\t\t\t\t\texists = house",
        "\t\t\t\t\thouse = {",
        "\t\t\t\t\t\tOR = {",
        "\t\t\t\t\t\t\tNOT = { has_variable = tarr_house_tag }",
        "\t\t\t\t\t\t\tvar:tarr_house_tag = flag:palemonaitis_middel_don",
        "\t\t\t\t\t\t}",
        "\t\t\t\t\t}",
        "\t\t\t\t\tNOT = { house = dynasty:9116.dynasty_founder.house }",
        "\t\t\t\t}",
        "\t\t\t\thouse = {",
        "\t\t\t\t\tset_house_name = dynn_tarr_palemonaitis_middel_don",
        "\t\t\t\t\tset_variable = { name = tarr_house_tag value = flag:palemonaitis_middel_don }",
        "\t\t\t\t}",
        "\t\t\t\tset_global_variable = { name = tarr_pin_24307 value = yes }",
        "\t\t\t}",
        "\t\t}",
        "\t\tif = {",
        "\t\t\tlimit = { NOT = { has_global_variable = tarr_pin_24307 } }",
        "\t\t\ttitle:d_pamir.holder ?= {",
        "\t\t\t\tevery_courtier_or_guest = {",
        "\t\t\t\t\tlimit = {",
        "\t\t\t\t\t\tdynasty ?= dynasty:9116",
        "\t\t\t\t\t\texists = house",
        "\t\t\t\t\t\thouse = {",
        "\t\t\t\t\t\t\tOR = {",
        "\t\t\t\t\t\t\t\tNOT = { has_variable = tarr_house_tag }",
        "\t\t\t\t\t\t\t\tvar:tarr_house_tag = flag:palemonaitis_middel_don",
        "\t\t\t\t\t\t\t}",
        "\t\t\t\t\t\t}",
        "\t\t\t\t\t\tNOT = { house = dynasty:9116.dynasty_founder.house }",
        "\t\t\t\t\t}",
        "\t\t\t\t\thouse = {",
        "\t\t\t\t\t\tset_house_name = dynn_tarr_palemonaitis_middel_don",
        "\t\t\t\t\t\tset_variable = { name = tarr_house_tag value = flag:palemonaitis_middel_don }",
        "\t\t\t\t\t}",
        "\t\t\t\t\tset_global_variable = { name = tarr_pin_24307 value = yes }",
        "\t\t\t\t}",
        "\t\t\t}",
        "\t\t}",
        "\t}",
        "\t# House 27674: Palemonaitis-Siauliai -> Palemonaitis-Schaulen (child of H=24293)",
        "\tif = {",
        "\t\tlimit = { NOT = { has_global_variable = tarr_pin_27674 } }",
        "\t\tdynasty:9116 ?= {",
        "\t\t\tevery_dynasty_member = {",
        "\t\t\t\tlimit = {",
        "\t\t\t\t\tis_alive = yes",
        "\t\t\t\t\thouse ?= { var:tarr_house_tag ?= flag:palemonaitis_orsche }",
        "\t\t\t\t}",
        "\t\t\t\tevery_child = {",
        "\t\t\t\t\tlimit = {",
        "\t\t\t\t\t\tis_alive = yes",
        "\t\t\t\t\t\tdynasty ?= dynasty:9116",
        "\t\t\t\t\t\texists = house",
        "\t\t\t\t\t\thouse = {",
        "\t\t\t\t\t\t\tOR = {",
        "\t\t\t\t\t\t\t\tNOT = { has_variable = tarr_house_tag }",
        "\t\t\t\t\t\t\t\tvar:tarr_house_tag = flag:palemonaitis_schaulen",
        "\t\t\t\t\t\t\t}",
        "\t\t\t\t\t\t}",
        "\t\t\t\t\t\tNOT = { house = dynasty:9116.dynasty_founder.house }",
        "\t\t\t\t\t}",
        "\t\t\t\t\thouse = {",
        "\t\t\t\t\t\tset_house_name = dynn_tarr_palemonaitis_schaulen",
        "\t\t\t\t\t\tset_variable = { name = tarr_house_tag value = flag:palemonaitis_schaulen }",
        "\t\t\t\t\t}",
        "\t\t\t\t\tset_global_variable = { name = tarr_pin_27674 value = yes }",
        "\t\t\t\t}",
        "\t\t\t}",
        "\t\t}",
        "\t}",
    ])

    lines.extend([
        "",
        "\t# =========================================================================",
        "\t# 5. Elevated Noble Houses & Dynamic Dynasties (Section 4 / S2)",
        "\t# All rules exclude vanilla multi-house dynasties, require untagged houses,",
        "\t# and permanently pin on first match to prevent conquest collateral drift.",
        "\t# =========================================================================",
    ])

    elevated_direct = [
        ('16800136', 'Buxtehude -> Este', ['c_hamburg', 'b_buxtehude'], 'dynn_tarr_este', 'este', True),
        ('67125621', 'Celle -> Alre', ['c_starodub'], 'dynn_tarr_alre', 'alre', True),
        ('25935', 'Leoben -> Göss', ['b_nawa'], 'dynn_tarr_goss', 'goss', True),
        ('33568115', 'Philippopolis-Priština -> Philippopolis-Ulpiana', ['c_zlatibor', 'b_zvecan'], 'dynn_tarr_philippopolis_ulpiana', 'philippopolis_ulpiana', False),
        ('28114', 'Roslavl -> Ôster', ['c_roslavl'], 'dynn_tarr_oster', 'oster', True),
        ('16803302', 'Steyr -> Enns', ['b_steyr'], 'dynn_tarr_enns', 'enns', True),
        ('21816', 'Vologda -> Walgede', ['d_vologda', 'c_vologda'], 'dynn_tarr_walgede', 'walgede', True),
    ]
    for hid, comment, titles, loc_key, tag, rename_dyn in elevated_direct:
        emit_title_rule(hid, comment, titles, loc_key, tag, exclude_vanilla=True, rename_dyn=rename_dyn)

    emit_courtier_rule('50349259', 'Coburg -> Îtze (house head guest at c_hohenberg)',
                       ['c_hohenberg'], 'dynn_tarr_itze', 'itze',
                       exclude_vanilla=True, rename_dyn=True,
                       extra_limits=['is_house_head = yes', 'is_female = yes'])
    emit_title_rule('17334', 'Jihlava -> Rokytna (via c_bornholm spouse)',
                    ['c_bornholm'], 'dynn_tarr_rokytna', 'rokytna',
                    rel_scope='primary_spouse', exclude_vanilla=True, rename_dyn=True)
    emit_courtier_rule('16801742', 'Brunnsholm-Sebezh -> Brunnsholm-Sebêsch (courtier at b_sheffield)',
                       ['b_sheffield'], 'dynn_tarr_brunnsholm_sebesch', 'brunnsholm_sebesch',
                       exclude_vanilla=True, rename_dyn=False,
                       extra_limits=['is_house_head = yes', 'is_female = yes'])

    lines.extend([
        "\t# House 16800196 & 33569509: Soundavara-Obnore (spouse of c_scalovia) & Soundavara-Erkawîka (male house_head)",
        "\tif = {",
        "\t\tlimit = { NOT = { has_global_variable = tarr_pin_16800196 } }",
        "\t\ttitle:c_scalovia.holder.primary_spouse ?= {",
        "\t\t\tif = {",
        "\t\t\t\tlimit = {",
        "\t\t\t\t\texists = house",
        "\t\t\t\t\thouse = {",
        "\t\t\t\t\t\tOR = {",
        "\t\t\t\t\t\t\tNOT = { has_variable = tarr_house_tag }",
        "\t\t\t\t\t\t\tvar:tarr_house_tag = flag:soundavara_obnore",
        "\t\t\t\t\t\t}",
        "\t\t\t\t\t}",
        "\t\t\t\t}",
        "\t\t\t\thouse = {",
        "\t\t\t\t\tset_house_name = dynn_tarr_soundavara_obnore",
        "\t\t\t\t\tset_variable = { name = tarr_house_tag value = flag:soundavara_obnore }",
        "\t\t\t\t}",
        "\t\t\t\tset_global_variable = { name = tarr_pin_16800196 value = yes }",
        "\t\t\t\tdynasty ?= {",
        "\t\t\t\t\tevery_dynasty_member = {",
        "\t\t\t\t\t\tlimit = {",
        "\t\t\t\t\t\t\tis_alive = yes",
        "\t\t\t\t\t\t\tis_house_head = yes",
        "\t\t\t\t\t\t\tis_male = yes",
        "\t\t\t\t\t\t\texists = house",
        "\t\t\t\t\t\t\thouse = {",
        "\t\t\t\t\t\t\t\tOR = {",
        "\t\t\t\t\t\t\t\t\tNOT = { has_variable = tarr_house_tag }",
        "\t\t\t\t\t\t\t\t\tvar:tarr_house_tag = flag:soundavara_erkawika",
        "\t\t\t\t\t\t\t\t}",
        "\t\t\t\t\t\t\t}",
        "\t\t\t\t\t\t}",
        "\t\t\t\t\t\thouse = {",
        "\t\t\t\t\t\t\tset_house_name = dynn_tarr_soundavara_erkawika",
        "\t\t\t\t\t\t\tset_variable = { name = tarr_house_tag value = flag:soundavara_erkawika }",
        "\t\t\t\t\t\t}",
        "\t\t\t\t\t\tset_global_variable = { name = tarr_pin_33569509 value = yes }",
        "\t\t\t\t\t}",
        "\t\t\t\t}",
        "\t\t\t}",
        "\t\t}",
        "\t}",
        "\t# House 23369: Sheksna-Kholmogory -> Sheksna-Dwina (HRE noble family domicile c_qaraustyurt)",
        "\tif = {",
        "\t\tlimit = { NOT = { has_global_variable = tarr_pin_23369 } }",
        "\t\ttitle:h_roman_empire.holder ?= {",
        "\t\t\tevery_noble_family = {",
        "\t\t\t\tlimit = {",
        "\t\t\t\t\tholder ?= {",
        "\t\t\t\t\t\tis_alive = yes",
        "\t\t\t\t\t\texists = domicile",
        "\t\t\t\t\t\tdomicile.domicile_location.county ?= title:c_qaraustyurt",
        "\t\t\t\t\t\texists = house",
        "\t\t\t\t\t\thouse = {",
        "\t\t\t\t\t\t\tOR = {",
        "\t\t\t\t\t\t\t\tNOT = { has_variable = tarr_house_tag }",
        "\t\t\t\t\t\t\t\tvar:tarr_house_tag = flag:sheksna_dwina",
        "\t\t\t\t\t\t\t}",
        "\t\t\t\t\t\t}",
        "\t\t\t\t\t}",
        "\t\t\t\t}",
        "\t\t\t\tholder ?= {",
        "\t\t\t\t\thouse = {",
        "\t\t\t\t\t\tset_house_name = dynn_tarr_sheksna_dwina",
        "\t\t\t\t\t\tset_variable = { name = tarr_house_tag value = flag:sheksna_dwina }",
        "\t\t\t\t\t}",
        "\t\t\t\t\tset_global_variable = { name = tarr_pin_23369 value = yes }",
        "\t\t\t\t}",
        "\t\t\t}",
        "\t\t}",
        "\t}",
        "\tset_global_variable = { name = tarr_v2_collateral_fix_applied value = yes }",
        "}",
        "",
    ])
    return "\r\n".join(lines)

def build_localization(entries, s2_entries, s3_entries, s4_entries):
    lines = [
        "l_english:",
        " # === Decisions & Events ===",
        ' tarr_chancellery_ordinance_decision:0 "Issue the Tarraconian Chancellery Ordinance"',
        ' tarr_chancellery_ordinance_decision_tooltip:0 "Standardize the names of Imperial and Tarraconian Kingdoms, Governorships, Magistracies, Prince-Bishoprics, and Archdioceses in the Tarraconian court tongue."',
        ' tarr_chancellery_ordinance_decision_desc:0 "Since the union of Lothringian High Franconian and Catalan courtly administration in 989, the scribes of the Imperial Chancellery have rendered the realms, governorships, magistracies, and ecclesiastical sees of the Roman Empire in the Tarraconian tongue. By imperial ordinance, we may codify these official registers across the Empire."',
        ' tarr_chancellery_ordinance_decision_confirm:0 "Summon the Imperial Chancellery"',
        ' tarr_chancellery_ordinance_decision_effect_tt:0 "Applies #V Tarraconian#! chancellery toponymy (using #V 1059–1171 Historical Resolutions#! by default, including #V Lûnstat#! for Nancy and #V Swenigorot#! for Lemberg) and opens the Chancellery configuration register."',
        "",
        ' tarr_chancellery.0001.t:0 "The Imperial Tarraconian Register"',
        r' tarr_chancellery.0001.desc:0 "The Protonotaries of the Imperial Chancellery present the great register of [ROOT.Char.GetCulture.GetNameNoTooltip] toponymy for the Roman Empire.\n\nUnder the #bold Historical Resolution#! standard, anachronistic castles and colonial towns are replaced by their authentic pre-1059/1122/1142/1154/1171 provincial centres and sub-baronies (such as #italic Lûnstat#! for Nancy, #italic Vrîsing#! for München, #italic Wilten#! for Innsbruck, #italic Swenigorot#! for Lemberg, #italic Skône#! for Gowrie, #italic Sôsôpel#! for Burgas, #italic Olbîe#! for Kara-Kerman, #italic Rêwale#! for Reval, #italic Atîl-Chasarân#! for Astrakhan, and #italic Rôhe#! for Lasta), while all titles are updated automatically on the 1st of January each year."',
        ' tarr_chancellery.0001.a:0 "Enforce the Historical Register across the Empire (Default)"',
        ' tarr_chancellery.0001.a.tt:0 "Renames all titles in the #V Roman Empire / HRE#! and any #V Tarraconian#! (or daughter-culture) provinces using #V 1059–1171 Historical Resolutions#!."',
        ' tarr_chancellery.0001.b:0 "Extend the Historical Register to all 186 De Jure Kingdoms"',
        ' tarr_chancellery.0001.b.tt:0 "Renames all 186 De Jure Kingdoms, 868 Duchies, 3,082 Counties, and 78 Archdioceses (including non-Imperial provinces) using #V 1059–1171 Historical Resolutions#!."',
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

    # === Dynamic Emergent Culture Realignments (Section 4) ===
    lines.extend([
        "",
        " # === Dynamic Emergent Culture Realignments (Section 4) ===",
    ])
    for c in s4_entries:
        cid = c['culture_id']
        name = c['realigned_name']
        coll = c['collective_noun']
        tname = re.sub(r'\s*\([^)]*\)', '', c['tarr_name']).strip()
        prefix_m = re.match(r"^([^\s\-]+)", name)
        prefix_stem = prefix_m.group(1) if prefix_m else name
        if prefix_stem.endswith('-'):
            prefix = prefix_stem
        elif prefix_stem.endswith('ian'):
            prefix = f"{prefix_stem[:-3]}-"
        elif prefix_stem.endswith('an'):
            prefix = f"{prefix_stem[:-2]}-"
        else:
            prefix = f"{prefix_stem}-"
        tstem = tname
        if tstem.endswith('isch'):
            tprefix = f"{tstem}-"
        elif tstem.endswith('en'):
            tprefix = f"{tstem[:-2]}isch-"
        elif tstem.endswith('er'):
            tprefix = f"{tstem[:-2]}isch-"
        elif tstem.endswith('e'):
            tprefix = f"{tstem[:-1]}isch-"
        else:
            tprefix = f"{tstem}isch-"

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
        ' dynn_tarr_kestenholz_raben:0 "Kestenholz-Raben"',
        ' dynn_tarr_kestenholz_utrecht:0 "Kestenholz-Utrecht"',
        ' dynn_tarr_kestenholz_kalisch:0 "Kestenholz-Kalisch"',
        ' dynn_tarr_kestenholz_legnica:0 "Kestenholz-Legnica"',
        ' dynn_tarr_kestenholz_judenburch:0 "Kestenholz-Judenburch"',
        ' dynn_tarr_kestenholz_altenstadt:0 "Kestenholz-Altenstadt"',
        ' dynn_tarr_kestenholz_bechin:0 "Kestenholz-Bechin"',
        ' dynn_tarr_kestenholz_sitzichow:0 "Kestenholz-Sitzichow"',
        ' dynn_tarr_kestenholz_gudensberch:0 "Kestenholz-Gudensberch"',
        ' dynn_tarr_kestenholz_berch:0 "Kestenholz-Berch"',
        ' dynn_tarr_kestenholz_bergen:0 "Kestenholz-Bergen"',
        ' dynn_tarr_kestenholz_kur:0 "Kestenholz-Kûr"',
        ' dynn_tarr_kestenholz_plzenec:0 "Kestenholz-Plzenec"',
        ' dynn_tarr_kestenholz_zant_arnolt:0 "Kestenholz-Zant-Arnolt"',
        ' dynn_tarr_kestenholz_sarema:0 "Kestenholz-Sâremâ"',
        ' dynn_tarr_kestenholz_swenigorot:0 "Kestenholz-Swenigorot"',
        ' dynn_tarr_kestenholz_metz:0 "Kestenholz-Metz"',
        ' dynn_tarr_kestenholz_bremen:0 "Kestenholz-Bremen"',
        ' dynn_tarr_kestenholz_dillingen:0 "Kestenholz-Dillingen"',
        ' dynn_tarr_kestenholz_orleans:0 "Kestenholz-Orleans"',
        ' dynn_tarr_kestenholz_merida:0 "Kestenholz-Mêrida"',
        ' dynn_tarr_kestenholz_terebovl:0 "Kestenholz-Terebovl"',
        ' dynn_tarr_kestenholz_zutphen:0 "Kestenholz-Zutphen"',
        ' dynn_tarr_kestenholz_lecce:0 "Kestenholz-Lecce"',
        ' dynn_tarr_kestenholz_saumur:0 "Kestenholz-Saumur"',
        ' dynn_tarr_kestenholz_buthrotum:0 "Kestenholz-Buthrotum"',
        ' dynn_tarr_kestenholz_annonay:0 "Kestenholz-Annonay"',
        ' dynn_tarr_kestenholz_fecamp:0 "Kestenholz-Fécamp"',
        ' dynn_tarr_kestenholz_albret:0 "Kestenholz-Albret"',
        ' dynn_tarr_kestenholz_flanders:0 "Kestenholz-Flanders"',
        ' dynn_tarr_kestenholz_geteina:0 "Kestenholz-Geteina"',
        ' dynn_tarr_kestenholz_tyddewi:0 "Kestenholz-Tyddewi"',
        ' dynn_tarr_kestenholz_cologne:0 "Kestenholz-Cologne"',
        ' dynn_tarr_kestenholz_pau:0 "Kestenholz-Pau"',
        ' dynn_tarr_kestenholz_sennar:0 "Kestenholz-Sennar"',
        ' dynn_tarr_kestenholz_blasien:0 "Kestenholz-Blasien"',
        ' dynn_tarr_kestenholz_moraca:0 "Kestenholz-Moraca"',
        ' dynn_tarr_kestenholz_vendome:0 "Kestenholz-Vendôme"',
        ' dynn_tarr_kestenholz_baht:0 "Kestenholz-Baht"',
        ' dynn_tarr_kestenholz_arnedo:0 "Kestenholz-Arnedo"',
        ' dynn_tarr_kestenholz_machynlleth:0 "Kestenholz-Machynlleth"',
        ' dynn_tarr_kestenholz_house_10882:0 "Kestenholz"',
        ' dynn_tarr_kestenholz_bluome:0 "Kestenholz-Bluome"',
        ' dynn_tarr_kestenholz_carenwall:0 "Kestenholz-Carenwall"',
        ' dynn_tarr_kestenholz_diest:0 "Kestenholz-Diest"',
        ' dynn_tarr_kestenholz_orlamunde:0 "Kestenholz-Orlamunde"',
        ' dynn_tarr_kestenholz_verona:0 "Kestenholz-Verona"',
        ' dynn_tarr_kestenholz_suerbeer:0 "Kestenholz-Suerbeer"',
        ' dynn_tarr_kestenholz_muhlhausen:0 "Kestenholz-Muhlhausen"',
        ' dynn_tarr_kestenholz_capua:0 "Kestenholz-Capua"',
        ' dynn_tarr_kestenholz_montjoie:0 "Kestenholz-Montjoie"',
        # Non-Chatenois cadet branches
        ' dynn_tarr_billung_erfurt:0 "Billung-Erfurt"',
        ' dynn_tarr_karling_litovel:0 "Karling-Litovel"',
        ' dynn_tarr_karling_hirsau:0 "Karling-Hirsau"',
        ' dynn_tarr_karling_troppouwe:0 "Karling-Troppouwe"',
        ' dynn_tarr_karling_ush:0 "Karling-Ush"',
        ' dynn_tarr_palemonaitis_middel_don:0 "Palemonaitis-Middel-Dôn"',
        ' dynn_tarr_palemonaitis_lielupe:0 "Palemonaitis-Lielupe"',
        ' dynn_tarr_palemonaitis_schaulen:0 "Palemonaitis-Schaulen"',
        ' dynn_tarr_palemonaitis_orsche:0 "Palemonaitis-Orsche"',
        ' dynn_tarr_palemonaitis_rasseinen:0 "Palemonaitis-Rassêinen"',
        ' dynn_tarr_palemonaitis_kukena:0 "Palemonaitis-Kukena"',
        ' dynn_tarr_umayyad_wichse:0 "Umayyad-Wîchsê"',
        ' dynn_tarr_reginar_sirakusan:0 "Reginar-Sirakusan"',
        ' dynn_tarr_gellones_wurle:0 "Gellones-Wurle"',
        ' dynn_tarr_cetchathach_uisnech:0 "Cétchathach-Uisnech"',
        ' dynn_tarr_ebrauc_uisnech:0 "Ebrauc-Uisnech"',
        ' dynn_tarr_hede_tzene:0 "Hede-Tzene"',
        ' dynn_tarr_hede_middel_don:0 "Hede-Middel-Dôn"',
        ' dynn_tarr_borg_waga:0 "Borg-Wâga"',
        ' dynn_tarr_borg_morarna:0 "Borg-Morarna"',
        ' dynn_tarr_echternach:0 "Echternach"',
        ' dynn_tarr_swratka:0 "Swratka"',
        ' dynn_tarr_silesia_dziadosz:0 "Silesia-Dziadosz"',
        ' dynn_tarr_prontzich:0 "Prôntzich"',
        ' dynn_tarr_belzig:0 "Belzig"',
        ' dynn_tarr_soest:0 "Soest"',
        ' dynn_tarr_gnezdovo:0 "Gnezdovo"',
        # Elevated dynasties
        ' dynn_tarr_plise:0 "iš Plesės"',
        ' dynn_tarr_berezina:0 "Berezina"',
        ' dynn_tarr_este:0 "Este"',
        ' dynn_tarr_alre:0 "Alre"',
        ' dynn_tarr_itze:0 "Îtze"',
        ' dynn_tarr_rokytna:0 "Rokytna"',
        ' dynn_tarr_goss:0 "Göss"',
        ' dynn_tarr_oster:0 "Ôster"',
        ' dynn_tarr_enns:0 "Enns"',
        ' dynn_tarr_sitzichow:0 "Sitzichow"',
        ' dynn_tarr_walgede:0 "Walgede"',
        ' dynn_tarr_wurle:0 "Wurle"',
        ' dynn_tarr_brunnsholm_sebesch:0 "Brunnsholm-Sebêsch"',
        ' dynn_tarr_philippopolis_ulpiana:0 "Philippopolis-Ulpiana"',
        ' dynn_tarr_sheksna_dwina:0 "Sheksna-Dwina"',
        ' dynn_tarr_soundavara_obnore:0 "Soundavara-Obnore"',
        ' dynn_tarr_soundavara_erkawika:0 "Soundavara-Erkawîka"',
    ])

    lines.append("")
    return "\r\n".join(lines)

def build_replace_localization():
    lines = [
        "l_english:",
        " # === Global Replace Overrides for Non-Colliding Historical Dynasties ===",
        ' dynn_Chatenois:0 "Kestenholz"',
        ' dynn_Memel:0 "Pilsāts"',
        ' dynn_Tigheci:0 "Tîghetsch"',
        "",
    ]
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

    # 3. Generate localization YAML & replace overrides
    loc_content = build_localization(entries, s2_entries, s3_entries, s4_entries)
    LOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOC_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        f.write(loc_content)
    print(f"Wrote {len(loc_content.splitlines())} lines to {LOC_PATH}")

    replace_loc_content = build_replace_localization()
    REPLACE_LOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPLACE_LOC_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        f.write(replace_loc_content)
    print(f"Wrote {len(replace_loc_content.splitlines())} lines to {REPLACE_LOC_PATH}")

    # 3b. Ensure all handwritten mod .txt files have UTF-8 BOM + CRLF line endings
    src_mod_dir = REPO_ROOT / "tarraconian_chancellery"
    for txt_path in src_mod_dir.glob("**/*.txt"):
        raw_txt = txt_path.read_text(encoding='utf-8-sig')
        norm_txt = raw_txt.replace('\r\n', '\n').replace('\n', '\r\n')
        with open(txt_path, 'w', encoding='utf-8-sig', newline='') as f:
            f.write(norm_txt)

    # 4. Sync to Paradox Interactive CK3 mod directory if accessible
    paradox_mod_root = Path.home() / "Documents" / "Paradox Interactive" / "Crusader Kings III" / "mod"
    try:
        if paradox_mod_root.exists():
            paradox_mod_dir = paradox_mod_root / "tarraconian_chancellery"
            paradox_mod_dir.mkdir(parents=True, exist_ok=True)
            for dest_item in list(paradox_mod_dir.glob("**/*")):
                if dest_item.is_file():
                    rel = dest_item.relative_to(paradox_mod_dir)
                    if not (src_mod_dir / rel).exists():
                        dest_item.unlink()
            for item in src_mod_dir.glob("**/*"):
                if item.is_file():
                    rel = item.relative_to(src_mod_dir)
                    dest = paradox_mod_dir / rel
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest)
            mod_desc = (src_mod_dir / "descriptor.mod").read_text(encoding='utf-8')
            posix_path = str(paradox_mod_dir).replace("\\", "/")
            mod_file_content = f'{mod_desc.strip()}\npath="{posix_path}"\n'
            (paradox_mod_root / "tarraconian_chancellery.mod").write_text(mod_file_content, encoding='utf-8')
            print(f"Successfully synced mod assets to {paradox_mod_dir}")
    except Exception as e:
        print(f"Note: Could not sync to Paradox mod directory ({e})")

if __name__ == '__main__':
    main()
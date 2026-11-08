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
EFFECTS_PATH = REPO_ROOT / "tarraconian_chancellery" / "common" / "scripted_effects" / "tarr_chancellery_title_list_effects.txt"
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
        'Sînt': 'Sîndisch',
        'Hellas': 'Hellênisch',
        'Îrlant': 'Îrisch',
        'Schotlant': 'Schottisch',
        'Brîe': 'Brîisch',
        'Trîer': 'Trîerisch',
        'Bâr-in-Pûlje': 'Bâr-Pûljer',
        'Alt-Mêne': 'Alt-Mêner',
        'Rôtenburch-an-der-Hûtzwe': 'Rôtenburch-an-der-Hûtzwer',
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
        m = re.match(r'^###\s+3\.\d+\s+Kingdom[^(]+\(`([a-zA-Z0-9_\-]+)`\)\s+\$\\rightarrow\$\s+\*\*([^*]+)\*\*', line)
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

def build_localization(entries):
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

    lines.append("")
    return "\r\n".join(lines)

def main():
    print(f"Reading gazetteer from: {GAZETTEER_PATH}")
    entries = parse_gazetteer(GAZETTEER_PATH)
    print(f"Total entries parsed: {len(entries)}")

    hist_diffs = [k for k, v in entries.items() if v['direct'] != v['hist']]
    print(f"Entries with 1059-1142 historical resolution (HIST != DIRECT): {len(hist_diffs)}")

    # 1. Generate scripted effects
    effects_content = build_scripted_effects(entries)
    EFFECTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(EFFECTS_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        f.write(effects_content)
    print(f"Wrote {len(effects_content.splitlines())} lines to {EFFECTS_PATH}")

    # 2. Generate localization YAML
    loc_content = build_localization(entries)
    LOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOC_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        f.write(loc_content)
    print(f"Wrote {len(loc_content.splitlines())} lines to {LOC_PATH}")

if __name__ == '__main__':
    main()

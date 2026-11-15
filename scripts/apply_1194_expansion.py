#!/usr/bin/env python3
"""
Applies 1194 Campaign Expansion (28 July 1194) to:
1. tarraconian_titles_1059.md
2. hre_de_jure_and_archdioceses_1059.md (via sync_hre_gazetteer.py)
3. scripts/build_mod.py
4. Rebuilds and verifies mod assets
"""

import json
import re
import sys
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# 1. Load Sinosphere calques and patch Flôzhügel -> Flôz-hügel
with open(REPO_ROOT / "data" / "sinosphere_title_calques.json", "r", encoding="utf-8") as f:
    sino = json.load(f)

sino["c_jiangling"] = "Magistrat van Flôz-hügel"

# 2. Non-Sinosphere additions & earlier additions
NON_SINO = {
    # Yorubaland
    "k_yorubaland": "Kûnincrich van Jorubalant",
    "d_oyo": "Gubernat van Ôjo",
    "c_igana": "Magistrat van Igane",
    "c_igbomina": "Magistrat van Igbomine",
    "c_ilorin": "Magistrat van Ilorîn",
    "c_oyo": "Magistrat van Ôjo",
    "c_yagba": "Magistrat van Jagbe",
    "d_ibadan": "Gubernat van Ibadân",
    "c_abomey": "Magistrat van Abomê",
    "c_ibadan": "Magistrat van Ibadân",
    "c_ifonyin": "Magistrat van Ivonjîn",
    "c_ketu": "Magistrat van Ketû",
    "d_ife": "Gubernat van Îve",
    "c_ife": "Magistrat van Îve",
    "c_ijebu": "Magistrat van Idschêbu",
    "c_owu": "Magistrat van Ôwu",
    "d_benin": "Gubernat van Benîn",
    "c_benin": "Magistrat van Benîn",
    "x_script_4423": "Gubernat van Edô",
    "c_edo": "Magistrat van Edô",

    # Akan
    "k_akan": "Kûnincrich van Akân",
    "d_ashanti": "Gubernat van Aschanti",
    "c_adanse": "Magistrat van Adanse",
    "c_fante": "Magistrat van Fante",
    "c_kumasi": "Magistrat van Kumasî",
    "c_kwahu-akyem": "Magistrat van Kwahu-Akjem",
    "c_wassa": "Magistrat van Wasse",
    "d_adiukru": "Gubernat van Adjukrû",
    "c_aowin": "Magistrat van Aowîn",
    "c_attie": "Magistrat van Attîe",
    "c_dabou": "Magistrat van Dabû",
    "d_eweland": "Gubernat van Ewelant",
    "c_afram": "Magistrat van Afrâm",
    "c_ewe": "Magistrat van Êwe",
    "c_nanumba": "Magistrat van Nanumbe",
    "d_brong": "Gubernat van Brong",
    "c_begho": "Magistrat van Bêgo",
    "c_bono": "Magistrat van Bonô",
    "c_bonoso": "Magistrat van Bonosô",
    "c_upper_bono": "Magistrat van Ôver-Bonô",
    "d_gyaman": "Gubernat van Gjamân",
    "c_bonduku": "Magistrat van Bondukû",
    "c_ndenye": "Magistrat van Ndenje",

    # Borgu
    "k_borgu": "Kûnincrich van Borgû",
    "d_borgu": "Gubernat van Borgû",
    "c_bussa": "Magistrat van Busse",
    "c_djugu": "Magistrat van Dschugû",
    "c_ilesa": "Magistrat van Ilêse",
    "c_ilo": "Magistrat van Ilô",
    "c_nikki": "Magistrat van Nikkî",
    "d_savalu": "Gubernat van Savalû",
    "c_savalu": "Magistrat van Savalû",
    "c_shabe": "Magistrat van Schâbe",
    "c_sokode": "Magistrat van Sokodê",
    "c_todo": "Magistrat van Todô",

    # Gur
    "k_gur": "Kûnincrich van Gûr",
    "d_dagomba": "Gubernat van Dagombe",
    "c_daboya": "Magistrat van Daboje",
    "c_dagomba": "Magistrat van Dagombe",
    "c_gonja": "Magistrat van Gondscha",
    "d_mamprusi": "Gubernat van Mamprusî",
    "c_kuisugu": "Magistrat van Kuisugû",
    "c_mamprusi": "Magistrat van Mamprusî",
    "c_pendjari": "Magistrat van Pendscharî",
    "d_wagadugu": "Gubernat van Wagadugû",
    "c_po": "Magistrat van Pô",
    "c_wagadugu": "Magistrat van Wagadugû",

    # Igbo-Benue
    "k_igbo-benue": "Kûnincrich van Igbô-Bênue",
    "d_igboland": "Gubernat van Igbôlant",
    "c_ibibo": "Magistrat van Ibibô",
    "c_idoma": "Magistrat van Idomê",
    "c_igala": "Magistrat van Igale",
    "c_igbo": "Magistrat van Igbô",
    "c_ijaw": "Magistrat van Idschou",
    "d_nupe": "Gubernat van Nûpe",
    "c_kyadya": "Magistrat van Kjadje",
    "c_nupe": "Magistrat van Nûpe",
    "c_guwari": "Magistrat van Guwarî",
    "c_opanda": "Magistrat van Opande",

    # Naimania
    "k_naimania": "Kûnincrich van Naimanjen",
    "d_ovorkhangai": "Gubernat van Ôverchangâi",
    "c_gobi_gurvan_saikhan": "Magistrat van Gurwan Sêchân",
    "c_ikh_bogd": "Magistrat van Ich Bogd",
    "c_ongi": "Magistrat van Ongî",
    "c_tovkhon": "Magistrat van Tövchön",
    "c_bombogor": "Magistrat van Bombögör",
    "c_khasagt_khairkhan": "Magistrat van Chasagt Chêrchân",
    "d_western_sayan": "Gubernat van West-Sajân",
    "c_kantegir": "Magistrat van Kantegîr",
    "c_sayanchu": "Magistrat van Sajantschû",
    "c_stoyanka": "Magistrat van Stojanke",
    "d_arkhangai": "Gubernat van Archangâi",
    "c_oigon": "Magistrat van Oigôn",
    "c_tarvagatai": "Magistrat van Tarwagatâi",
    "c_telmen": "Magistrat van Telmên",
    "d_gobi_altai": "Gubernat van Gôbi-Altâi",
    "c_sharga": "Magistrat van Scharge",
    "c_tseel": "Magistrat van Zêl",
    "c_zarman": "Magistrat van Zarmân",
    "d_kargassia": "Gubernat van Kargasjen",
    "c_burugu_aallar": "Magistrat van Burugu Âllâr",
    "c_chagdy_aallar": "Magistrat van Tschagdy Âllâr",
    "c_songuu_aallar": "Magistrat van Songû Âllâr",
    "d_khovsgol": "Gubernat van Chövsgöl",
    "c_darkhad_valley": "Magistrat van Darchad-Tal",
    "c_tomorbulag": "Magistrat van Tömörbulach",
    "c_ulantaiga": "Magistrat van Ulantâige",
    "d_tannu_ola": "Gubernat van Tannu-Ôle",
    "c_central_tannu": "Magistrat van Midden-Tannu",
    "c_eastern_tannu": "Magistrat van Ôst-Tannu",
    "c_western_tannu": "Magistrat van West-Tannu",
    "d_ubsunur_hollow": "Gubernat van Ubsunûr-Dal",
    "c_tesiin_gol": "Magistrat van Tesîn-Gôl",
    "c_ulaangom": "Magistrat van Ulângôm",
    "c_uvs_nuur": "Magistrat van Uws-Nûr",
    "d_zavkhan": "Gubernat van Sawchân",
    "c_khar_us": "Magistrat van Char-Ûs",
    "c_uliastai": "Magistrat van Uljastâi",
    "c_urgamal": "Magistrat van Urgamâl",
    "d_katu_yaryk": "Gubernat van Katu-Jarîch",
    "c_kara_khol": "Magistrat van Kara-Chôl",
    "c_katu_yaryk": "Magistrat van Katu-Jarîch",

    # Guinea
    "k_guinea": "Kûnincrich van Gînêe",
    "d_toro": "Gubernat van Torô",
    "c_kabarasana": "Magistrat van Kabarasane",
    "c_konyan": "Magistrat van Konjân",
    "c_mau": "Magistrat van Mâu",
    "c_toma": "Magistrat van Tome",
    "c_toro": "Magistrat van Torô",
    "d_kru": "Gubernat van Krû",
    "c_boubo": "Magistrat van Bûbo",
    "c_dibri": "Magistrat van Dibrî",
    "c_kru": "Magistrat van Krû",
    "c_lobo": "Magistrat van Lobô",
    "d_sapi": "Gubernat van Sapî",
    "c_nalu": "Magistrat van Nalû",
    "c_sanda": "Magistrat van Sande",
    "c_tamiso": "Magistrat van Tamisô",
    "c_temne": "Magistrat van Temne",
    "d_bassa": "Gubernat van Basse",
    "c_bassa": "Magistrat van Basse",
    "c_man": "Magistrat van Mân",
    "c_nuon": "Magistrat van Nuôn",
    "d_kono": "Gubernat van Konô",
    "c_gola": "Magistrat van Gole",
    "c_kono": "Magistrat van Konô",
    "c_sherbro": "Magistrat van Scherbrô",
    "d_wenyon": "Gubernat van Wenjôn",
    "c_grebo": "Magistrat van Grêbo",
    "c_wenyon": "Magistrat van Wenjôn",

    # Kong
    "k_kong": "Kûnincrich van Kong",
    "d_kong": "Gubernat van Kong",
    "c_boron": "Magistrat van Borôn",
    "c_kong": "Magistrat van Kong",
    "c_leraba": "Magistrat van Lerabe",
    "c_nzi": "Magistrat van Nzî",
    "d_lobi": "Gubernat van Lobî",
    "c_dyulaso": "Magistrat van Djulasô",
    "c_wa": "Magistrat van Wâ",
    "c_lobi": "Magistrat van Lobî",
    "c_loropeni": "Magistrat van Loropenî",
    "d_worodugu": "Gubernat van Worodugû",
    "c_nyene": "Magistrat van Njene",
    "c_tyendugu": "Magistrat van Tjendugû",
    "c_worodugu": "Magistrat van Worodugû",

    # Additions in earlier kingdoms
    "x_script_9046": "Gubernat van Fafân",
    "c_fafan": "Magistrat van Fafân",
    "x_script_8766": "Gubernat van Nagaude",
    "c_nagauda": "Magistrat van Nagaude",
    "d_shoria": "Gubernat van Schorjen",
    "c_kuzbas": "Magistrat van Kusbas",
    "c_shor": "Magistrat van Schôr",
    "c_uul_chors": "Magistrat van Ûl-Chôrs",
    "d_kulyndy_steppe": "Gubernat van der Kulundischen Steppe",
    "c_barnaul": "Magistrat van Barnaûl",
    "c_kachu": "Magistrat van Katschû",
    "c_kuchuk": "Magistrat van Kutschuk",
    "c_kulunda": "Magistrat van Kulunde",
}

TARR_MAP = dict(sino)
TARR_MAP.update(NON_SINO)

def main():
    print("=== Applying 1194 Campaign Expansion ===")

    # Read hre_de_jure_and_archdioceses_1059.md to get latest kingdom counts & hierarchy
    hre_path = REPO_ROOT / "hre_de_jure_and_archdioceses_1059.md"
    with open(hre_path, "r", encoding="utf-8") as f:
        hre_text = f.read()

    # Parse kingdom RE / Total counts from Section 1.2
    k_counts = {}
    for line in hre_text.splitlines():
        m = re.match(r"^\|\s*\d+\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*`([^`]+)`\s*\|\s*[^|]+\|\s*\*\*(\d+)\*\*\s*\|\s*(\d+)\s*\|", line)
        if m:
            k_key = m.group(2)
            re_c = int(m.group(3))
            tot_c = int(m.group(4))
            k_counts[k_key] = (re_c, tot_c)

    # -------------------------------------------------------------
    # 1. Update tarraconian_titles_1059.md
    # -------------------------------------------------------------
    tarr_path = REPO_ROOT / "tarraconian_titles_1059.md"
    with open(tarr_path, "r", encoding="utf-8") as f:
        tarr_raw = f.read()

    # Determine line ending
    is_crlf = "\r\n" in tarr_raw
    newline = "\r\n" if is_crlf else "\n"
    lines = tarr_raw.split(newline)

    updated_lines = []
    in_sec2 = False
    in_sec3 = False

    # New kingdom table entries (187-204)
    new_kingdom_table_rows = [
        f"| 187 | **Lingnan** | `k_lingnan` | **Kûnincrich van dem Sûtrücke** | *Sûtrückisch* | **{k_counts['k_lingnan'][0]}/{k_counts['k_lingnan'][1]} RE** — Added in 1194 Imperial Chancellery update; calque of Chinese *Lǐngnán* (岭南). |",
        f"| 188 | **Lingxi** | `k_lingxi` | **Kûnincrich van dem Westrücke** | *Westrückisch* | **{k_counts['k_lingxi'][0]}/{k_counts['k_lingxi'][1]} RE** — Added in 1194 Imperial Chancellery update; calque of Chinese *Lǐngxī* (岭西). |",
        f"| 189 | **Shannan** | `k_shannan` | **Kûnincrich van dem Sûtberch** | *Sûtberchisch* | **{k_counts['k_shannan'][0]}/{k_counts['k_shannan'][1]} RE** — Added in 1194 Imperial Chancellery update; calque of Chinese *Shānnán* (山南). |",
        f"| 190 | **Jiangxi** | `k_jiangxi` | **Kûnincrich van dem Westflôze** | *Westflôzisch* | **{k_counts['k_jiangxi'][0]}/{k_counts['k_jiangxi'][1]} RE** — Added in 1194 Imperial Chancellery update; calque of Chinese *Jiāngxī* (江西). |",
        f"| 191 | **Yorubaland** | `k_yorubaland` | **Kûnincrich van Jorubalant** | *Jorubalantisch* | **{k_counts['k_yorubaland'][0]}/{k_counts['k_yorubaland'][1]} RE** — Added in 1194 Imperial Chancellery update. |",
        f"| 192 | **Akan** | `k_akan` | **Kûnincrich van Akân** | *Akânisch* | **{k_counts['k_akan'][0]}/{k_counts['k_akan'][1]} RE** — Added in 1194 Imperial Chancellery update. |",
        f"| 193 | **Liangzhe** | `k_liangzhe` | **Kûnincrich van Twê-Zschêlant** | *Twê-Zschêlantisch* | **{k_counts['k_liangzhe'][0]}/{k_counts['k_liangzhe'][1]} RE** — Added in 1194 Imperial Chancellery update; calque of Chinese *Liǎngzhè* (两浙). |",
        f"| 194 | **Huainan** | `k_huainan` | **Kûnincrich van dem Sûthuai** | *Sûthuaiesch* | **{k_counts['k_huainan'][0]}/{k_counts['k_huainan'][1]} RE** — Added in 1194 Imperial Chancellery update; calque of Chinese *Huáinán* (淮南). |",
        f"| 195 | **Đại Việt** | `k_viet` | **Kûnincrich van Jüetlant** | *Jüetlantisch* | **{k_counts['k_viet'][0]}/{k_counts['k_viet'][1]} RE** — Added in 1194 Imperial Chancellery update; Sino-Vietnamese *Đại Việt* (大越). |",
        f"| 196 | **Borgu** | `k_borgu` | **Kûnincrich van Borgû** | *Borgûisch* | **{k_counts['k_borgu'][0]}/{k_counts['k_borgu'][1]} RE** — Added in 1194 Imperial Chancellery update. |",
        f"| 197 | **Fujian** | `k_fujian` | **Kûnincrich van Sêlichbache** | *Sêlichbachisch* | **{k_counts['k_fujian'][0]}/{k_counts['k_fujian'][1]} RE** — Added in 1194 Imperial Chancellery update; calque of Chinese *Fújiàn* (福建). |",
        f"| 198 | **Hunan** | `k_hunan` | **Kûnincrich van dem Sûtsê** | *Sûtsêisch* | **{k_counts['k_hunan'][0]}/{k_counts['k_hunan'][1]} RE** — Added in 1194 Imperial Chancellery update; calque of Chinese *Húnán* (湖南). |",
        f"| 199 | **Gur** | `k_gur` | **Kûnincrich van Gûr** | *Gûrisch* | **{k_counts['k_gur'][0]}/{k_counts['k_gur'][1]} RE** — Added in 1194 Imperial Chancellery update. |",
        f"| 200 | **Jiangdong** | `k_jiangdong` | **Kûnincrich van dem Ôstflôze** | *Ôstflôzisch* | **{k_counts['k_jiangdong'][0]}/{k_counts['k_jiangdong'][1]} RE** — Added in 1194 Imperial Chancellery update; calque of Chinese *Jiāngdōng* (江东). |",
        f"| 201 | **Igbo-Benue** | `k_igbo-benue` | **Kûnincrich van Igbô-Bênue** | *Igbô-Bênuesch* | **{k_counts['k_igbo-benue'][0]}/{k_counts['k_igbo-benue'][1]} RE** — Added in 1194 Imperial Chancellery update. |",
        f"| 202 | **Naimania** | `k_naimania` | **Kûnincrich van Naimanjen** | *Naimansch* | **{k_counts['k_naimania'][0]}/{k_counts['k_naimania'][1]} RE** — Added in 1194 Imperial Chancellery update. |",
        f"| 203 | **Guinea** | `k_guinea` | **Kûnincrich van Gînêe** | *Gînêisch* | **{k_counts['k_guinea'][0]}/{k_counts['k_guinea'][1]} RE** — Added in 1194 Imperial Chancellery update. |",
        f"| 204 | **Kong** | `k_kong` | **Kûnincrich van Kong** | *Kongisch* | **{k_counts['k_kong'][0]}/{k_counts['k_kong'][1]} RE** — Added in 1194 Imperial Chancellery update. |",
    ]

    # Pre-build Section 3 for 187 to 204
    new_sec3_blocks = []
    for k_num in range(187, 205):
        m = re.search(r"### 2\." + str(k_num) + r"\s+Kingdom of ([^`\n]+)\s*\(`([^`]+)`\).*?(?=### 2\.|\Z)", hre_text, re.DOTALL)
        if not m:
            print(f"Warning: Kingdom {k_num} not found in HRE gazetteer")
            continue
        sec = m.group(0)
        knm = m.group(1).strip()
        kk = m.group(2)
        ktarr = TARR_MAP[kk]
        
        k_lines = [f"### 3.{k_num} Kingdom of {knm} (`{kk}`) $\\rightarrow$ **{ktarr}**\n"]
        duchies = re.split(r"\n(?=\* \*\*Duchy of)", sec)[1:]
        for d_block in duchies:
            d_m = re.match(r"^\*\s+\*\*Duchy of ([^*]+)\*\*\s*\(`([d|x][^`]+)`\)", d_block)
            if not d_m:
                continue
            dnm, dk = d_m.group(1), d_m.group(2)
            dtarr = TARR_MAP[dk]
            k_lines.append(f"* **Duchy of {dnm}** (`{dk}`) $\\rightarrow$ **{dtarr}**")
            for c_line in d_block.splitlines():
                c_m = re.search(r"\*\s+(\*\*\[HRE\]\*\*|\[Non-HRE\])\s+\*\*([^*]+)\*\*\s*\(`([c|x][^`]+)`\)", c_line)
                if c_m:
                    status, cnm, ck = c_m.group(1), c_m.group(2), c_m.group(3)
                    ctarr = TARR_MAP[ck]
                    k_lines.append(f"  * `{ck}` ({status} {cnm}) $\\rightarrow$ **{ctarr}**")
        
        new_sec3_blocks.append("\n".join(k_lines))

    # Iterate lines and reconstruct
    i = 0
    while i < len(lines):
        line = lines[i]

        # Header title
        if line.startswith("# Tarraconian Translations of De Jure Titles & Archdioceses"):
            updated_lines.append("# Tarraconian Translations of De Jure Titles & Archdioceses (1059–1194)")
            i += 1
            continue

        # Campaign save line
        if "* **Campaign Save:** `chatenois_867_01_01.ck3`" in line:
            updated_lines.append("* **Campaign Save:** `chatenois_867_01_01.ck3` (**28 July 1194**, updated from 13 May 1059, 20 September 1122, 20 August 1142, 27 December 1154 & 18 June 1171)")
            i += 1
            continue

        # Section 2 header
        if line.startswith("## 2. Summary Table: The"):
            updated_lines.append("## 2. Summary Table: The 204 De Jure Kingdoms in Tarraconian (28 July 1194)")
            in_sec2 = True
            i += 1
            continue

        # End of Section 2 table
        if in_sec2 and line.startswith("## 3. Complete De Jure Hierarchy"):
            in_sec2 = False
            # Append new kingdom rows before leaving section 2
            # Notice the table separator '---' comes before '## 3.'
            # We will handle rows insertion right before '---'
            updated_lines.append(line)
            in_sec3 = True
            i += 1
            continue

        if in_sec2:
            # Check if this is row 186
            m_186 = re.match(r"^\|\s*186\s*\|", line)
            # Update counts if row matches kingdom pattern
            m_row = re.match(r"^(\|\s*\d+\s*\|\s*\*\*[^*]+\*\*\s*\|\s*`([^`]+)`\s*\|\s*[^|]+\|\s*[^|]+\|\s*)\*\*\d+/\d+\s+RE\*\*(.*)$", line)
            if m_row:
                k_key = m_row.group(2)
                if k_key in k_counts:
                    re_c, tot_c = k_counts[k_key]
                    line = f"{m_row.group(1)}**{re_c}/{tot_c} RE**{m_row.group(3)}"
            updated_lines.append(line)
            if m_186:
                # Append rows 187 to 204 right after 186
                for nr in new_kingdom_table_rows:
                    updated_lines.append(nr)
            i += 1
            continue

        # Inside Section 3: earlier kingdom additions
        # 1. k_adal: replace c_fafan in d_adal with Duchy of Fafan block
        if "  * `c_fafan` (**[HRE]** Fafan) $\\rightarrow$ **Magistrat van Fafân**" in line:
            # Check if previous line was part of d_adal
            # Replace with standalone Duchy of Fafan
            updated_lines.append("* **Duchy of Fafan** (`x_script_9046`) $\\rightarrow$ **Gubernat van Fafân**")
            updated_lines.append("  * `c_fafan` (**[HRE]** Fafan) $\\rightarrow$ **Magistrat van Fafân**")
            i += 1
            continue

        # 2. k_buryatia: insert d_shoria before end of k_buryatia
        if "### 3.133 Kingdom of Saryarka" in line:
            # Insert d_shoria right before 3.133 separator
            # Backtrack past empty line / ---
            # Instead, we can insert before '### 3.133'
            # Let's inspect what lines come right before
            # Usually: --- \n\n ### 3.133
            shoria_block = (
                "* **Duchy of Shoria** (`d_shoria`) $\\rightarrow$ **Gubernat van Schorjen**\n"
                "  * `c_kuzbas` ([Non-HRE] Kuzbas) $\\rightarrow$ **Magistrat van Kusbas**\n"
                "  * `c_shor` ([Non-HRE] Shor) $\\rightarrow$ **Magistrat van Schôr**\n"
                "  * `c_uul_chors` ([Non-HRE] Uul-Chors) $\\rightarrow$ **Magistrat van Ûl-Chôrs**\n\n---\n"
            )
            # Replace the preceding '---' if already appended
            if updated_lines and updated_lines[-1].strip() == "---":
                updated_lines.pop()
                if updated_lines and updated_lines[-1].strip() == "":
                    updated_lines.pop()
            updated_lines.append(shoria_block.strip())
            updated_lines.append("")
            updated_lines.append("---")
            updated_lines.append("")
            updated_lines.append(line)
            i += 1
            continue

        # 3. k_saryarka: insert d_kulyndy_steppe before 3.134
        if "### 3.134 Kingdom of Kham" in line:
            kulunda_block = (
                "* **Duchy of Kulyndy Steppe** (`d_kulyndy_steppe`) $\\rightarrow$ **Gubernat van der Kulundischen Steppe**\n"
                "  * `c_barnaul` ([Non-HRE] Barnaul) $\\rightarrow$ **Magistrat van Barnaûl**\n"
                "  * `c_kachu` ([Non-HRE] Kachu) $\\rightarrow$ **Magistrat van Katschû**\n"
                "  * `c_kuchuk` ([Non-HRE] Kuchuk) $\\rightarrow$ **Magistrat van Kutschuk**\n"
                "  * `c_kulunda` ([Non-HRE] Kulunda) $\\rightarrow$ **Magistrat van Kulunde**\n\n---\n"
            )
            if updated_lines and updated_lines[-1].strip() == "---":
                updated_lines.pop()
                if updated_lines and updated_lines[-1].strip() == "":
                    updated_lines.pop()
            updated_lines.append(kulunda_block.strip())
            updated_lines.append("")
            updated_lines.append("---")
            updated_lines.append("")
            updated_lines.append(line)
            i += 1
            continue

        # 4. k_rajputana: insert x_script_8766 (Nagauda) before 3.152
        if "### 3.152 Kingdom of Gujarat" in line:
            nagauda_block = (
                "* **Duchy of Nagauda** (`x_script_8766`) $\\rightarrow$ **Gubernat van Nagaude**\n"
                "  * `c_nagauda` (**[HRE]** Nagauda) $\\rightarrow$ **Magistrat van Nagaude**\n\n---\n"
            )
            if updated_lines and updated_lines[-1].strip() == "---":
                updated_lines.pop()
                if updated_lines and updated_lines[-1].strip() == "":
                    updated_lines.pop()
            updated_lines.append(nagauda_block.strip())
            updated_lines.append("")
            updated_lines.append("---")
            updated_lines.append("")
            updated_lines.append(line)
            i += 1
            continue

        # End of Section 3 / Start of Section 4
        if line.startswith("## 4. Archdioceses & Ecclesiastical Sees"):
            in_sec3 = False
            # Append subsections 3.187 to 3.204 before Section 4
            # Pop trailing separator if present
            if updated_lines and updated_lines[-1].strip() == "---":
                updated_lines.pop()
                if updated_lines and updated_lines[-1].strip() == "":
                    updated_lines.pop()
            
            for block in new_sec3_blocks:
                updated_lines.append("")
                updated_lines.append("---")
                updated_lines.append("")
                updated_lines.append(block)
            
            updated_lines.append("")
            updated_lines.append("---")
            updated_lines.append("")
            updated_lines.append("## 4. Archdioceses & Ecclesiastical Sees in Tarraconian (1059–1194)")
            i += 1
            continue

        updated_lines.append(line)
        i += 1

    final_tarr = newline.join(updated_lines)
    with open(tarr_path, "wb") as f:
        f.write(final_tarr.encode("utf-8"))

    print(f"[Tarraconian Titles] Updated {tarr_path.name} ({len(final_tarr.splitlines())} lines, {len(final_tarr.encode('utf-8')):,} bytes)")

    # -------------------------------------------------------------
    # 2. Update scripts/build_mod.py
    # -------------------------------------------------------------
    build_mod_path = REPO_ROOT / "scripts" / "build_mod.py"
    with open(build_mod_path, "r", encoding="utf-8") as f:
        bm_text = f.read()

    # Update regex to support 1194 historical notes
    bm_text = re.sub(
        r"1059\|1122\|1142\|1154\|1171",
        "1059|1122|1142|1154|1171|1194",
        bm_text
    )

    # Add explicit adjectives for new kingdoms
    new_adjs = """        'Sûtrücke': 'Sûtrückisch',
        'Westrücke': 'Westrückisch',
        'Sûtberch': 'Sûtberchisch',
        'Westflôze': 'Westflôzisch',
        'Jorubalant': 'Jorubalantisch',
        'Akân': 'Akânisch',
        'Sûthuai': 'Sûthuaiesch',
        'Jüetlant': 'Jüetlantisch',
        'Borgû': 'Borgûisch',
        'Sêlichbache': 'Sêlichbachisch',
        'Sûtsê': 'Sûtsêisch',
        'Gûr': 'Gûrisch',
        'Ôstflôze': 'Ôstflôzisch',
        'Igbô-Bênue': 'Igbô-Bênuesch',
        'Naimanjen': 'Naimansch',
        'Gînêe': 'Gînêisch',
        'Kong': 'Kongisch',"""

    if "'Sûtrücke': 'Sûtrückisch'" not in bm_text:
        bm_text = bm_text.replace(
            "        'Pagân': 'Pagânisch',",
            "        'Pagân': 'Pagânisch',\n" + new_adjs
        )

    with open(build_mod_path, "w", encoding="utf-8") as f:
        f.write(bm_text)

    print(f"[Build Mod] Updated {build_mod_path.name}")

    # -------------------------------------------------------------
    # 3. Synchronize HRE Gazetteer
    # -------------------------------------------------------------
    print("Running sync_hre_gazetteer.py ...")
    subprocess.run([sys.executable, str(REPO_ROOT / "scripts" / "sync_hre_gazetteer.py")], cwd=str(REPO_ROOT), check=True)

    # -------------------------------------------------------------
    # 4. Rebuild Mod Assets
    # -------------------------------------------------------------
    print("Running build_mod.py ...")
    subprocess.run([sys.executable, str(REPO_ROOT / "scripts" / "build_mod.py")], cwd=str(REPO_ROOT), check=True)

    # -------------------------------------------------------------
    # 5. Verify Mod Assets
    # -------------------------------------------------------------
    print("Running verify_mod_assets.py ...")
    subprocess.run([sys.executable, str(REPO_ROOT / "scripts" / "verify_mod_assets.py")], cwd=str(REPO_ROOT), check=True)

    # -------------------------------------------------------------
    # 6. Audit Phonotactics
    # -------------------------------------------------------------
    print("Running audit_phonotactics_titles.py ...")
    subprocess.run([sys.executable, str(REPO_ROOT / "scripts" / "audit_phonotactics_titles.py")], cwd=str(REPO_ROOT), check=True)

    print("=== 1194 Campaign Expansion Successfully Applied! ===")

if __name__ == "__main__":
    main()

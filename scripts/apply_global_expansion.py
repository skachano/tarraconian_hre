#!/usr/bin/env python3
"""
Applies Global Title Expansion (all 47 De Jure Empires, 213 Kingdoms, 3,476 Counties) to:
1. hre_de_jure_and_archdioceses_1059.md (via update_hre_gazetteer with scope='all')
2. tarraconian_titles_1059.md (adding rows 205-213 in Section 2, and subsections 3.205-3.213 in Section 3)
3. Synchronizes both via sync_hre_gazetteer.py
4. Rebuilds mod assets via build_mod.py
5. Verifies mod integrity via verify_mod_assets.py and audit_phonotactics_titles.py
"""

import json
import re
import sys
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

# 1. Load Sinosphere calques and patch Flôzhügel -> Flôz-hügel
with open(REPO_ROOT / "data" / "sinosphere_title_calques.json", "r", encoding="utf-8") as f:
    sino = json.load(f)

sino["c_jiangling"] = "Magistrat van Flôz-hügel"

# 2. Siberian translations
SIBERIA = {
    # Empire
    "e_siberia": "Keiserrîch van Sibirjen",
    
    # k_yugra
    "k_yugra": "Kûnincrich van Jûgren",
    "d_ostyaki": "Gubernat van Ostjâken",
    "c_tyumen": "Magistrat van Tjumên",
    "c_laia": "Magistrat van Lâje",
    "c_tabary": "Magistrat van Tabâre",
    "c_neramkary": "Magistrat van Nêramkare",
    "d_konda": "Gubernat van Konde",
    "c_tselym_dalyn": "Magistrat van Zêlim-Dalîn",
    "c_kharam-vosh": "Magistrat van Charamwosch",
    "c_kartauzh": "Magistrat van Kartaûsch",
    "d_pelym": "Gubernat van Pelîm",
    "c_pelym": "Magistrat van Pelîm",
    "c_koshuki": "Magistrat van Koschûke",
    "d_kazym": "Gubernat van Kazîm",
    "c_kazym": "Magistrat van Kazîm",
    "c_sosva": "Magistrat van Sôswe",
    "c_koda": "Magistrat van Kôde",

    # k_sibir
    "k_sibir": "Kûnincrich van Sibîr",
    "d_sibir": "Gubernat van Sibîr",
    "c_sibir": "Magistrat van Sibîr",
    "c_tobol": "Magistrat van Tobôl",
    "c_belogorje": "Magistrat van Wîzenberch",
    "c_bardak": "Magistrat van Bardach",
    "d_ishim": "Gubernat van Ischîm",
    "c_ishim": "Magistrat van Ischîm",
    "c_dolgujar": "Magistrat van Dolgujâr",
    "d_tara": "Gubernat van Târe",
    "c_tara": "Magistrat van Târe",
    "c_kazanskoye": "Magistrat van Saltzwazzer",
    "c_petropavolsk": "Magistrat van Irtîsch",
    "c_chich": "Magistrat van Tschîtsch",
    "d_lanikaz": "Gubernat van Lanikâz",
    "c_omsk": "Magistrat van Ôm",
    "c_kainsk": "Magistrat van Kaînsk",
    "c_pavlodar": "Magistrat van Imêkje",
    "d_kazakh": "Gubernat van Kasâchen",
    "c_astana": "Magistrat van Wîzengrâv",
    "c_astrakhanka": "Magistrat van Astrachanke",
    "c_shchuchinsk": "Magistrat van Burabâi",
    "c_teke": "Magistrat van Têke",

    # k_ob
    "k_ob": "Kûnincrich van dem Ôb",
    "d_ala_tau": "Gubernat van dem Buntberch",
    "c_tomsk": "Magistrat van Eûschte",
    "c_kiia": "Magistrat van Kîe",
    "c_taskyl": "Magistrat van Taskîl",
    "c_kojuk": "Magistrat van Kojûk",
    "c_chulym": "Magistrat van Tschulîm",
    "c_narim": "Magistrat van Narîm",
    "c_sochur": "Magistrat van Sotschûr",
    "c_yenisei": "Magistrat van Jenissêi",
    "d_vasyugan_mire": "Gubernat van dem Wasjûganmôr",
    "c_vasyugan": "Magistrat van Wasjûgan",
    "c_umiai": "Magistrat van Umjâi",
    "c_tartas_SIB": "Magistrat van Tartâs",
    "d_baraba_steppe": "Gubernat van der Barâbaveit",
    "c_kolyvan": "Magistrat van Kolywân",
    "c_sartlan": "Magistrat van Sartlân",
    "c_ubins": "Magistrat van Ubînsk",
    "c_igaran": "Magistrat van Igarân",
    "c_konda_ob": "Magistrat van Ôbkônde",
    "x_script_5386": "Gubernat van Tschîtsch",
}

TARR_MAP = dict(sino)
TARR_MAP.update(SIBERIA)

def main():
    print("=== Step 1: Update HRE Gazetteer with --scope all ===")
    from scripts.update_hre_gazetteer import update_gazetteer
    hre_path = REPO_ROOT / "hre_de_jure_and_archdioceses_1059.md"
    update_gazetteer(
        save_file=Path("/var/tmp/ck3_audit/melted_save.ck3"),
        melted_save=Path("/var/tmp/ck3_audit/melted_save.ck3"),
        target_md=hre_path,
        loc_cache_file=Path("/var/tmp/ck3_audit/english_titles_cache.json"),
        scope="all",
        run_sync=False
    )

    print("=== Step 2: Read updated HRE Gazetteer hierarchy ===")
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

    print("=== Step 3: Update tarraconian_titles_1059.md ===")
    tarr_path = REPO_ROOT / "tarraconian_titles_1059.md"
    with open(tarr_path, "r", encoding="utf-8") as f:
        tarr_raw = f.read()

    is_crlf = "\r\n" in tarr_raw
    newline = "\r\n" if is_crlf else "\n"
    lines = tarr_raw.split(newline)

    # Update summary table header: 204 -> 213
    lines = [
        line.replace("The 204 De Jure Kingdoms in Tarraconian", "The 213 De Jure Kingdoms in Tarraconian")
        for line in lines
    ]

    # Map for Table 2 rows (205 to 213)
    table_notes = {
        "k_qianzhong": (
            "Kûnincrich van dem Swartzmidden",
            "*Swartzmidsch*",
            f"**{k_counts.get('k_qianzhong', (0,18))[0]}/{k_counts.get('k_qianzhong', (0,18))[1]} RE** — Added in 1194 Global Chancellery update; calque of Chinese *Qiánzhōng* (黔中)."
        ),
        "k_dali": (
            "Kûnincrich van Grôzrecht",
            "*Grôzrechtisch*",
            f"**{k_counts.get('k_dali', (0,17))[0]}/{k_counts.get('k_dali', (0,17))[1]} RE** — Added in 1194 Global Chancellery update; calque of Chinese *Dàlǐ* (大理)."
        ),
        "k_kuizhou": (
            "Kûnincrich van Kuîgouwe",
            "*Kuîgouwisch*",
            f"**{k_counts.get('k_kuizhou', (0,17))[0]}/{k_counts.get('k_kuizhou', (0,17))[1]} RE** — Added in 1194 Global Chancellery update; calque of Chinese *Kuízhōu* (夔州)."
        ),
        "k_sibir": (
            "Kûnincrich van Sibîr *(or **Sibirrîch**)*",
            "[zi.ˈbiːr] / *Sibirisch*",
            f"**{k_counts.get('k_sibir', (0,17))[0]}/{k_counts.get('k_sibir', (0,17))[1]} RE** — Added in 1194 Global Chancellery update; Siberian Khanate & Irtysh basin (*Isker*)."
        ),
        "k_ob": (
            "Kûnincrich van dem Ôb",
            "[oːp] / *Ôbisch*",
            f"**{k_counts.get('k_ob', (0,16))[0]}/{k_counts.get('k_ob', (0,16))[1]} RE** — Added in 1194 Global Chancellery update; Great Ob hydronym (*As / Yag*)."
        ),
        "k_xingyuan": (
            "Kûnincrich van Bloyvürst",
            "*Bloyvürstisch*",
            f"**{k_counts.get('k_xingyuan', (0,13))[0]}/{k_counts.get('k_xingyuan', (0,13))[1]} RE** — Added in 1194 Global Chancellery update; calque of Chinese *Xīngyuán* (兴元)."
        ),
        "k_dongchuan": (
            "Kûnincrich van dem Ôstbache",
            "*Ôstbachisch*",
            f"**{k_counts.get('k_dongchuan', (0,12))[0]}/{k_counts.get('k_dongchuan', (0,12))[1]} RE** — Added in 1194 Global Chancellery update; calque of Chinese *Dōngchuān* (东川)."
        ),
        "k_xichuan": (
            "Kûnincrich van dem Westbache",
            "*Westbachisch*",
            f"**{k_counts.get('k_xichuan', (0,12))[0]}/{k_counts.get('k_xichuan', (0,12))[1]} RE** — Added in 1194 Global Chancellery update; calque of Chinese *Xīchuān* (西川)."
        ),
        "k_yugra": (
            "Kûnincrich van Jûgren *(or **Jûgrelant**)*",
            "[ˈjuː.ɡrən] / *Jûgrisch*",
            f"**{k_counts.get('k_yugra', (0,12))[0]}/{k_counts.get('k_yugra', (0,12))[1]} RE** — Added in 1194 Global Chancellery update; Uralic Ugric heartland (*Iugria*)."
        ),
    }

    # Find the kingdom order from Section 2 of hre_de_jure_and_archdioceses_1059.md
    ordered_k_205_213 = []
    for k_num in range(205, 214):
        m = re.search(r"### 2\." + str(k_num) + r"\s+Kingdom of ([^`\n]+)\s*\(`([^`]+)`\)", hre_text)
        if m:
            ordered_k_205_213.append((k_num, m.group(1).strip(), m.group(2).strip()))
        else:
            print(f"Warning: Kingdom {k_num} not found in HRE gazetteer!")

    new_table_rows = []
    for k_num, knm, kk in ordered_k_205_213:
        tarr_name, adj, note = table_notes[kk]
        new_table_rows.append(f"| {k_num} | **{knm}** | `{kk}` | **{tarr_name}** | {adj} | {note} |")

    # Insert new table rows after row 204 if not already present
    if "| 205 |" not in tarr_raw:
        row204_idx = -1
        for i, line in enumerate(lines):
            if line.startswith("| 204 |"):
                row204_idx = i
                break
        if row204_idx != -1:
            for j, nr in enumerate(new_table_rows):
                lines.insert(row204_idx + 1 + j, nr)

    # Pre-build Section 3 for 205 to 213
    new_sec3_blocks = []
    for k_num, knm, kk in ordered_k_205_213:
        m = re.search(r"### 2\." + str(k_num) + r"\s+Kingdom of ([^`\n]+)\s*\(`([^`]+)`\).*?(?=### 2\.|\Z)", hre_text, re.DOTALL)
        if not m:
            continue
        sec = m.group(0)
        ktarr = TARR_MAP[kk]
        
        k_lines = [f"### 3.{k_num} Kingdom of {knm} (`{kk}`) $\\rightarrow$ **{ktarr}**\n"]
        duchies = re.split(r"\n(?=\* \*\*Duchy of)", sec)[1:]
        for d_block in duchies:
            d_m = re.match(r"^\*\s+\*\*Duchy of ([^*]+)\*\*\s*\(`([d|x][^`]+)`\)", d_block)
            if not d_m:
                continue
            dnm, dk = d_m.group(1), d_m.group(2)
            dtarr = TARR_MAP.get(dk, f"Gubernat van {dnm}")
            k_lines.append(f"* **Duchy of {dnm}** (`{dk}`) $\\rightarrow$ **{dtarr}**")
            
            # Counties under this duchy
            counties = re.findall(r"^\s*\*\s*(?:\*\*\[HRE\]\*\*|\[Non-HRE\])\s+\*\*([^*]+)\*\*\s*\(`(c_[^`]+)`\)", d_block, re.M)
            for cnm, ck in counties:
                ctarr = TARR_MAP.get(ck, f"Magistrat van {cnm}")
                k_lines.append(f"  * `{ck}` ([Non-HRE] {cnm}) $\\rightarrow$ **{ctarr}**")
        
        new_sec3_blocks.append("\n".join(k_lines))

    new_sec3_text = "\n\n---\n\n".join(new_sec3_blocks) + "\n\n---\n\n"

    # Reconstruct text and insert new Section 3 blocks right before ## 4. Archdioceses
    assembled_text = newline.join(lines)
    sec4_target = "## 4. Archdioceses & Ecclesiastical Sees"
    if "### 3.205" not in assembled_text and sec4_target in assembled_text:
        idx_sec4 = assembled_text.find(sec4_target)
        assembled_text = assembled_text[:idx_sec4] + new_sec3_text + assembled_text[idx_sec4:]

    with open(tarr_path, "wb") as f:
        f.write(assembled_text.encode("utf-8"))
    print(f"Updated {tarr_path.name} with all 213 kingdoms!")

    print("=== Step 4: Run sync_hre_gazetteer.py ===")
    from scripts.sync_hre_gazetteer import sync_hre_gazetteer
    sync_hre_gazetteer(REPO_ROOT)

    print("=== Step 5: Run build_mod.py ===")
    res_build = subprocess.run([sys.executable, str(REPO_ROOT / "scripts" / "build_mod.py")], capture_output=True, text=True)
    print(res_build.stdout)
    if res_build.returncode != 0:
        print("ERROR building mod:", res_build.stderr)
        sys.exit(1)

    print("=== Step 6: Run verify_mod_assets.py ===")
    res_verify = subprocess.run([sys.executable, str(REPO_ROOT / "scripts" / "verify_mod_assets.py")], capture_output=True, text=True)
    print(res_verify.stdout)
    if res_verify.returncode != 0:
        print("ERROR verifying mod assets:", res_verify.stderr)
        sys.exit(1)

    print("=== Step 7: Run audit_phonotactics_titles.py ===")
    res_phono = subprocess.run([sys.executable, str(REPO_ROOT / "scripts" / "audit_phonotactics_titles.py")], capture_output=True, text=True)
    print(res_phono.stdout)
    if res_phono.returncode != 0:
        print("ERROR in phonotactic audit:", res_phono.stderr)
        sys.exit(1)

    print("=== ALL STEPS COMPLETED SUCCESSFULLY! ===")

if __name__ == "__main__":
    main()

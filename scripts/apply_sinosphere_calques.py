import json, re

with open("data/sinosphere_title_calques.json") as f:
    calques = json.load(f)

# Empire custom strings for tables
empire_table_titles = {
    "e_andong": "**Gubernat van dem Ôstfrid** *(or **Andong**)*",
    "e_liangyi": "**Keiserrîch van Lîangjî** *(Balk-ende-Vollrîch)*",
    "e_zhongyuan": "**Keiserrîch van dem Middenvelt**",
    "e_jingyang": "**Keiserrîch van Dôrnflôz** *(Dôrn-ende-Upheve)*",
    "e_yongliang": "**Keiserrîch van dem Kôlen-Vredelant**",
    "e_japan": "**Keiserrîch van der Sunnenorigin** *(Dat Japansche Keiserrîch)*",
    "e_lingnan": "**Keiserrîch van dem Sûtrücke**",
    "e_goryeo": "**Keiserrîch van den Drî-Hânen** *(Dat Koreânsche Keiserrîch)*",
    "e_amur": "**Keiserrîch van Amûrlant**",
}

with open("sinosphere_titles_and_characters_1154.md", "r", encoding="utf-8") as f:
    lines = f.readlines()

output_lines = []
in_sec2_or_3 = False
in_sec4 = False
in_sec5 = False

county_table_header_old = "| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |"
county_table_header_new = "| # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | Tarraconian Chancellery Title | Historical Status & Resolution | 1154 Liege | 1154 Culture | Dev | Holdings | Built Holdings |"

county_table_sep_old = "| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |"
county_table_sep_new = "| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :--- |"

updated_counties = 0
updated_headers = 0

for line in lines:
    line_clean = line.strip()

    # Track sections
    if line_clean.startswith("## 2.") or line_clean.startswith("## 3."):
        in_sec2_or_3 = True
        in_sec4 = False
        in_sec5 = False
    elif line_clean.startswith("## 4."):
        in_sec2_or_3 = False
        in_sec4 = True
        in_sec5 = False
    elif line_clean.startswith("## 5."):
        in_sec2_or_3 = False
        in_sec4 = False
        in_sec5 = True

    # 1. Section 1.2 Empire summary table
    if not in_sec2_or_3 and not in_sec4 and not in_sec5:
        if line_clean.startswith("| Rank | De Jure Empire | Title Key | Chinese Characters | Sphere Tier |"):
            output_lines.append("| Rank | De Jure Empire | Title Key | Chinese Characters | Tarraconian Title | Sphere Tier | Kingdoms | Duchies | Counties | Baronies | Total Dev | Avg Dev | Roman Control (1154) | Anachronisms Flagged |\n")
            continue
        if line_clean.startswith("| :---: | :--- | :--- | :--- | :---: | :---: |"):
            output_lines.append("| :---: | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |\n")
            continue
        if line_clean.startswith("|") and "`e_" in line_clean:
            parts = [p.strip() for p in line.split("|")]
            # parts[0] is empty, parts[1]=Rank, parts[2]=De Jure Empire, parts[3]=Title Key, parts[4]=Chinese Characters, parts[5]=Sphere Tier, ...
            if len(parts) >= 6 and "`e_" in parts[3]:
                e_key = parts[3].replace("`", "").strip()
                tarr_title = empire_table_titles.get(e_key, f"**{calques.get(e_key, '')}**")
                # Insert tarr_title after parts[4]
                new_parts = parts[:5] + [f" {tarr_title} "] + parts[5:]
                output_lines.append("|".join(new_parts))
                continue

    # 2. Section 2 & 3 Headers
    if in_sec2_or_3:
        # Empire header: ### 2.1 Empire of Zhongyuan (`e_zhongyuan` / 中原)
        m_emp = re.match(r"^(###\s+[\d\.]+\s+Empire\s+of\s+[^(]+\(`(e_[^`]+)`\s*/\s*[^)]+\))(.*)$", line)
        if m_emp:
            emp_prefix = m_emp.group(1)
            emp_key = m_emp.group(2)
            calque_str = calques.get(emp_key, "")
            output_lines.append(f"{emp_prefix} — **{calque_str}**\n")
            updated_headers += 1
            continue

        # Kingdom header: #### 2.1.1 Kingdom of Daibei (`k_daibei` / 代北)
        m_k = re.match(r"^(####\s+[\d\.]+\s+Kingdom\s+of\s+[^(]+\(`(k_[^`]+)`\s*/\s*([^)]+)\))(.*)$", line)
        if m_k:
            k_prefix = m_k.group(1)
            k_key = m_k.group(2)
            calque_str = calques.get(k_key, "")
            output_lines.append(f"{k_prefix} — **{calque_str}**\n")
            updated_headers += 1
            continue

        # Duchy header: ##### Duchy of Sanggan (`d_sanggan` / 桑干) — *4/4 in Roman Empire*
        m_d = re.match(r"^(#####\s+Duchy\s+of\s+[^(]+\(`(d_[^`]+)`\s*/\s*[^)]+\))(\s*—\s*.*)?$", line)
        if m_d:
            d_prefix = m_d.group(1)
            d_key = m_d.group(2)
            trailing = m_d.group(3) or ""
            calque_str = calques.get(d_key, "")
            output_lines.append(f"{d_prefix} — **{calque_str}**{trailing}\n")
            updated_headers += 1
            continue

        # County table headers
        if county_table_header_old in line:
            output_lines.append(county_table_header_new + "\n")
            continue
        if county_table_sep_old in line:
            output_lines.append(county_table_sep_new + "\n")
            continue

        # County rows: | 1 | `c_huaian` | **Huai'an** | **怀安** | — | ✅ Pre-867 Classical | ...
        if line_clean.startswith("|") and "`c_" in line_clean and "Historical Status & Resolution" not in line_clean:
            parts = [p.strip() for p in line.split("|")]
            # parts[0]="", parts[1]="#", parts[2]="County Key", parts[3]="English Name", parts[4]="Chinese Characters", parts[5]="Traditional / Variant", parts[6]="Historical Status..."
            if len(parts) >= 8 and "`c_" in parts[2]:
                c_key = parts[2].replace("`", "").strip()
                c_calque = calques.get(c_key, f"Magistrat van {parts[3].replace('*', '').strip()}")
                new_parts = parts[:6] + [f" **{c_calque}** "] + parts[6:]
                output_lines.append("|".join(new_parts) + "\n")
                updated_counties += 1
                continue

    # 3. Section 4: Kingdom Ranking Table
    if in_sec4:
        if line_clean.startswith("| Rank | Kingdom Name | Title Key | Chinese Characters | De Jure Empire |"):
            output_lines.append("| Rank | Kingdom Name | Title Key | Chinese Characters | Tarraconian Title | De Jure Empire | Counties | Total Baronies | Total Dev | Avg Dev | 1154 Roman Control | Anachronisms Flagged | Dominant Realm in 1154 |\n")
            continue
        if line_clean.startswith("| :---: | :--- | :--- | :--- | :--- | :---: |"):
            output_lines.append("| :---: | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |\n")
            continue
        if line_clean.startswith("|") and "`k_" in line_clean:
            parts = [p.strip() for p in line.split("|")]
            # parts[0]="", parts[1]=Rank, parts[2]=Kingdom Name, parts[3]=Title Key, parts[4]=Chinese Characters, parts[5]=De Jure Empire...
            if len(parts) >= 6 and "`k_" in parts[3]:
                k_key = parts[3].replace("`", "").strip()
                k_calque = calques.get(k_key, f"Kûnincrich van {parts[2].replace('*', '').strip()}")
                new_parts = parts[:5] + [f" **{k_calque}** "] + parts[5:]
                output_lines.append("|".join(new_parts) + "\n")
                continue

    # 4. Section 5: Master Register of 61 Sinosphere Anachronism Resolutions
    if in_sec5:
        # Table row: | 1 | `c_LIAO_changchun` | **Changchun** | **长春** | Khitan (`k_khitan`) | ... | **Option B:** ... | ****Magistrat van Liao_changchun**** | ...
        if line_clean.startswith("|") and "`c_" in line_clean:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 10 and "`c_" in parts[2]:
                c_key = parts[2].replace("`", "").strip()
                c_calque = calques.get(c_key, f"Magistrat van {parts[3].replace('*', '').strip()}")
                # parts[8] is the Tarraconian Chancellery Title column
                # Replace parts[8] with the semantic calque (with Option B note)
                opt_b_match = re.search(r"`([A-Za-z0-9_]+)\s+River", parts[7])
                opt_b_stem = opt_b_match.group(1) if opt_b_match else c_key.replace("c_", "")
                parts[8] = f" **{c_calque}** *(1154 Option B: **{opt_b_stem}**)* "
                output_lines.append("|".join(parts) + "\n")
                continue

    # Default pass-through
    output_lines.append(line)

print(f"Updated headers: {updated_headers}")
print(f"Updated counties in Sec 2 & 3: {updated_counties}")

with open("sinosphere_titles_and_characters_1154.md", "w", encoding="utf-8") as f:
    f.writelines(output_lines)

print("Saved updated sinosphere_titles_and_characters_1154.md")

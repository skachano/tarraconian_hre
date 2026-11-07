#!/usr/bin/env python3
"""
Applies newly generated Tarraconian translations for Kingdoms 101-160
(60 kingdoms, 301 duchies, 1,029 counties) to:
1. hre_de_jure_and_archdioceses_1059.md
2. tarraconian_titles_1059.md
"""

import json
import re
import sys
from pathlib import Path

def main():
    repo_root = Path(__file__).resolve().parent.parent
    hierarchy_path = Path("/tmp/translated_101_hierarchy.json")
    hre_path = repo_root / "hre_de_jure_and_archdioceses_1059.md"
    tarr_path = repo_root / "tarraconian_titles_1059.md"

    if not hierarchy_path.exists():
        print(f"Error: Missing {hierarchy_path}")
        sys.exit(1)

    with open(hierarchy_path, 'r', encoding='utf-8') as f:
        hierarchy = json.load(f)

    # Build county map
    county_map = {}
    for k in hierarchy:
        for d in k['duchies']:
            for c in d['counties']:
                county_map[c['key']] = c

    # -------------------------------------------------------------
    # 1. Update hre_de_jure_and_archdioceses_1059.md
    # -------------------------------------------------------------
    with open(hre_path, 'rb') as f:
        hre_raw = f.read()

    hre_is_crlf = b'\r\n' in hre_raw
    hre_newline = '\r\n' if hre_is_crlf else '\n'
    hre_lines = hre_raw.decode('utf-8').split(hre_newline)

    updated_hre_lines = []
    in_101 = False
    hre_annotated = 0

    for line in hre_lines:
        if '### 2.101 Kingdom of Amdo' in line:
            in_101 = True
        elif '### 3.1 Papal' in line:
            in_101 = False

        new_line = line
        if in_101:
            m = re.search(r'`(c_[a-zA-Z0-9_\-]+)`', line)
            if m:
                ckey = m.group(1)
                if ckey in county_map and 'Tarraconian:' not in line:
                    tarr_name = county_map[ckey]['tarr_name']
                    # Append Tarraconian annotation
                    new_line = f"{line.rstrip()} — *Tarraconian: **Magistrat van {tarr_name}****"
                    hre_annotated += 1

        updated_hre_lines.append(new_line)

    with open(hre_path, 'wb') as f:
        f.write(hre_newline.join(updated_hre_lines).encode('utf-8'))

    print(f"[HRE MD] Successfully annotated {hre_annotated} counties in {hre_path.name}")

    # Extract kingdom counts for Section 2 table
    k_counts = {}
    for m in re.finditer(r'### 2\.(1[0-5][0-9]|160)\s+Kingdom of (.*?)\s+\(`([a-zA-Z0-9_\-]+)`\)\s+—\s+([0-9]+/[0-9]+)\s+Counties in HRE/RE', hre_raw.decode('utf-8')):
        k_num = int(m.group(1))
        k_counts[k_num] = m.group(4)

    # -------------------------------------------------------------
    # 2. Update tarraconian_titles_1059.md
    # -------------------------------------------------------------
    with open(tarr_path, 'rb') as f:
        tarr_raw = f.read()

    tarr_is_crlf = b'\r\n' in tarr_raw
    tarr_newline = '\r\n' if tarr_is_crlf else '\n'
    tarr_lines = tarr_raw.decode('utf-8').split(tarr_newline)

    # Build Section 2 new rows
    s2_rows = []
    for k in hierarchy:
        num = k['num']
        name = k['name']
        key = k['key']
        tarr_name = k['tarr_name']
        tarr_adj = k['tarr_adj']
        count = k_counts.get(num, "0/0")
        s2_rows.append(f"| {num} | **{name}** | `{key}` | **Kûnincrich van {tarr_name}** | *{tarr_adj}* | **{count} RE** — Added in 1154 Imperial Chancellery update. |")

    # Build Section 3 new kingdom blocks
    s3_new_lines = []
    for k in hierarchy:
        num = k['num']
        name = k['name']
        key = k['key']
        tarr_name = k['tarr_name']

        s3_new_lines.append("")
        s3_new_lines.append("---")
        s3_new_lines.append("")
        s3_new_lines.append(f"### 3.{num} Kingdom of {name} (`{key}`) $\\rightarrow$ **Kûnincrich van {tarr_name}**")
        s3_new_lines.append("")

        for d in k['duchies']:
            d_name = d['name']
            d_key = d['key']
            d_tarr = d['tarr_name']
            s3_new_lines.append(f"* **Duchy of {d_name}** (`{d_key}`) $\\rightarrow$ **Gubernat van {d_tarr}**")
            for c in d['counties']:
                c_key = c['key']
                c_name = c['name']
                c_tarr = c['tarr_name']
                tag = "**[HRE]**" if c['is_hre'] else "[Non-HRE]"
                s3_new_lines.append(f"  * `{c_key}` ({tag} {c_name}) $\\rightarrow$ **Magistrat van {c_tarr}**")

    # Assembly into tarraconian_titles_1059.md
    updated_tarr_lines = []
    permia_inserted = False
    chaldia_inserted = False

    for i, line in enumerate(tarr_lines):
        # Update Section 2 header
        if line.startswith("## 2. Summary Table: The 100 De Jure Kingdoms"):
            updated_tarr_lines.append("## 2. Summary Table: The 160 De Jure Kingdoms in Tarraconian (27 December 1154)")
            continue

        updated_tarr_lines.append(line)

        # After Permia (row 100), insert rows 101-160
        if not permia_inserted and line.startswith("| 100 |") and "k_permia" in line:
            for r in s2_rows:
                updated_tarr_lines.append(r)
            permia_inserted = True

        # After Chaldia (Section 3.100), insert Sections 3.101-3.160
        if not chaldia_inserted and "c_satala" in line and "Magistrat van Satâle" in line:
            for l in s3_new_lines:
                updated_tarr_lines.append(l)
            chaldia_inserted = True

    with open(tarr_path, 'wb') as f:
        f.write(tarr_newline.join(updated_tarr_lines).encode('utf-8'))

    print(f"[TARR MD] Successfully updated Section 2 (rows 101-160) and Section 3 (blocks 3.101-3.160) in {tarr_path.name}")
    print(f"Permia inserted: {permia_inserted}, Chaldia inserted: {chaldia_inserted}")

if __name__ == '__main__':
    main()

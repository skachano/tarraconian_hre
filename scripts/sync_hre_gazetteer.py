#!/usr/bin/env bash
"""
Synchronization Engine: Master Chancellery Gazetteer -> English De Jure Reference
Ensures hre_de_jure_and_archdioceses_1059.md is kept 100% synchronized with the
single source of truth: tarraconian_titles_1059.md.
"""
import os
import re
import sys
from pathlib import Path

def parse_canonical_titles(tarr_md_path):
    """
    Parses canonical Tarraconian titles from tarraconian_titles_1059.md.
    Returns: dict[title_key -> canonical_tarraconian_name]
    """
    canonical = {}
    with open(tarr_md_path, 'r', encoding='utf-8') as f:
        for line in f:
            # County/Duchy/Kingdom pattern: * `key` (...) -> **Name** or * **Title** (`key`) -> **Name**
            # e.g.: * `c_volodymyr` (Volodymyr) $\rightarrow$ **Magistrat van Simne**
            m = re.search(r'`([a-z0-9_]+)`.*?\\rightarrow\s+\*\*([^*]+)\*\*', line)
            if m:
                key, name = m.group(1), m.group(2).strip()
                canonical[key] = name
                continue
            # Archdiocese table pattern: | 26 | **Archdiocese of Bari** | `d_et_bari` | **Erzbisdom van Bâr-in-Pûlje** |
            m_arch = re.search(r'\|\s*\d+\s*\|\s*\*\*[^*]+\*\*\s*\|\s*`([a-z0-9_]+)`\s*\|\s*\*\*([^*]+)\*\*', line)
            if m_arch:
                key, name = m_arch.group(1), m_arch.group(2).strip()
                canonical[key] = name
    return canonical

def sync_hre_gazetteer(repo_dir=None):
    if repo_dir is None:
        repo_dir = Path(__file__).resolve().parent.parent
    else:
        repo_dir = Path(repo_dir)

    tarr_md = repo_dir / "tarraconian_titles_1059.md"
    hre_md = repo_dir / "hre_de_jure_and_archdioceses_1059.md"

    if not tarr_md.exists() or not hre_md.exists():
        print(f"Error: Missing {tarr_md} or {hre_md}")
        return False

    canonical = parse_canonical_titles(tarr_md)
    print(f"[Sync] Parsed {len(canonical)} canonical titles from {tarr_md.name}")

    with open(hre_md, 'rb') as f:
        raw = f.read().decode('utf-8')

    is_crlf = '\r\n' in raw
    lines = raw.split('\r\n' if is_crlf else '\n')
    updated_lines = []
    changes = 0

    for line in lines:
        new_line = line
        # Match county pattern in HRE gazetteer:
        # e.g. * **[HRE]** **Vladimir** (`c_vladimir`) — *Tarraconian: **Magistrat van Klêsme***
        m_c = re.search(r'`([a-z0-9_]+)`\)\s*—\s*\*Tarraconian:\s*\*\*([^*]+)\*\*\*', line)
        if m_c:
            key, current_name = m_c.group(1), m_c.group(2).strip()
            if key in canonical and canonical[key] != current_name:
                expected = canonical[key]
                new_line = line.replace(f"**{current_name}***", f"**{expected}***")
                print(f"[Sync] Updated {key}: '{current_name}' -> '{expected}'")
                changes += 1

        # Match archdiocese table pattern:
        # | **Archdiocese of Bari** | `d_et_bari` | Bâr-in-Pûlje (`c_bari`) | ...
        m_arch = re.search(r'\|\s*\*\*Archdiocese of [^*]+\*\*\s*\|\s*`([a-z0-9_]+)`\s*\|\s*([^|`]+)\(`c_[a-z0-9_]+`\)', line)
        if m_arch:
            d_key, cur_seat = m_arch.group(1), m_arch.group(2).strip()
            # check if canonical archdiocese exists
            if d_key in canonical:
                canon_arch = canonical[d_key]
                # Extract clean seat name from "Erzbisdom van <Seat>"
                canon_seat = re.sub(r'^Erzbisdom\s+van\s+', '', canon_arch).strip()
                if cur_seat != canon_seat:
                    new_line = line.replace(f"| {cur_seat} (`c_", f"| {canon_seat} (`c_")
                    print(f"[Sync] Updated {d_key} seat: '{cur_seat}' -> '{canon_seat}'")
                    changes += 1

        updated_lines.append(new_line)

    if changes > 0:
        newline_char = '\r\n' if is_crlf else '\n'
        with open(hre_md, 'wb') as f:
            f.write(newline_char.join(updated_lines).encode('utf-8'))
        print(f"[Sync] Successfully synchronized {changes} titles in {hre_md.name}!")
    else:
        print(f"[Sync] {hre_md.name} is already 100% in sync with {tarr_md.name}!")

    return True

if __name__ == '__main__':
    sync_hre_gazetteer()

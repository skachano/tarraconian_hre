#!/usr/bin/env python3
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
    Parses canonical Tarraconian titles and historical notes from tarraconian_titles_1059.md.
    Returns: (canonical_names, canonical_hists)
    """
    canonical_names = {}
    canonical_hists = {}
    with open(tarr_md_path, 'r', encoding='utf-8') as f:
        for line in f:
            idx = -1
            for arr in ['$\\rightarrow$', r'\rightarrow', '->', '→']:
                if arr in line:
                    idx = line.find(arr) + len(arr)
                    break
            if idx == -1:
                # Archdiocese table pattern: | 26 | **Archdiocese of Bari** | `d_et_bari` | **Erzbisdom van Bâr-in-Pûlje** |
                m_arch = re.search(r'\|\s*\d+\s*\|\s*\*\*[^*]+\*\*\s*\|\s*`([a-zA-Z0-9_\-]+)`\s*\|\s*\*\*([^*]+)\*\*', line)
                if m_arch:
                    key, name = m_arch.group(1), m_arch.group(2).strip()
                    canonical_names[key] = name
                continue

            m_key = re.search(r'`([a-zA-Z0-9_\-]+)`', line[:idx])
            if not m_key:
                continue
            key = m_key.group(1)
            after = line[idx:].strip()

            m_bold = re.search(r'\*\*([^*]+)\*\*', after)
            if m_bold:
                canonical_names[key] = m_bold.group(1).strip()

            m_hist = re.search(r'\[((?:\d{4}[^\]:]*?|Slavic-Root):[^\]]+)\]', after)
            if m_hist:
                canonical_hists[key] = m_hist.group(1).strip()

    return canonical_names, canonical_hists

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

    canonical_names, canonical_hists = parse_canonical_titles(tarr_md)
    print(f"[Sync] Parsed {len(canonical_names)} canonical titles and {len(canonical_hists)} historical notes from {tarr_md.name}")

    with open(hre_md, 'rb') as f:
        raw = f.read().decode('utf-8')

    is_crlf = '\r\n' in raw
    lines = raw.split('\r\n' if is_crlf else '\n')
    updated_lines = []
    changes = 0

    for line in lines:
        new_line = line

        # 1. Match county/duchy pattern in HRE gazetteer:
        # e.g. * **[HRE]** **Vladimir** (`c_vladimir`) — *Tarraconian: **Magistrat van Klêsme****
        # or   * **[HRE]** **Tver** (`c_tver`) — *Tarraconian: **Magistrat van Twer** (`[1122 Historical: Magistrat van Woloch-Lâmtzich]`)*
        m_c = re.search(r'(`([a-zA-Z0-9_\-]+)`\)\s*—\s*\*Tarraconian:\s*)\*\*([^*]+)\*\*', new_line)
        if m_c:
            prefix = m_c.group(1)
            key = m_c.group(2)
            current_name = m_c.group(3).strip()
            if key in canonical_names and canonical_names[key] != current_name:
                expected = canonical_names[key]
                # Replace only the specific occurrence in this Tarraconian block
                old_target = f"{prefix}**{current_name}**"
                new_target = f"{prefix}**{expected}**"
                new_line = new_line.replace(old_target, new_target, 1)
                print(f"[Sync] Updated {key} title: '{current_name}' -> '{expected}'")
                changes += 1
        else:
            # County line lacking Tarraconian annotation (e.g. newly added kingdoms/counties)
            m_plain = re.match(r'^(\s*\*\s*(?:\*\*\[HRE\]\*\*|\[Non-HRE\])\s*.*?\(`(c_[a-zA-Z0-9_\-]+)`\))\s*$', new_line)
            if m_plain:
                key = m_plain.group(2)
                if key in canonical_names:
                    expected = canonical_names[key]
                    new_line = (
                        f"{m_plain.group(1)} — *Tarraconian: **{expected}** (`[{canonical_hists[key]}]`)*"
                        if key in canonical_hists
                        else f"{m_plain.group(1)} — *Tarraconian: **{expected}***"
                    )
                    print(f"[Sync] Annotated {key}: '{expected}'")
                    changes += 1

        # 2. Match historical note pattern in HRE gazetteer:
        m_h = re.search(r'`([a-zA-Z0-9_\-]+)`.*?\[((?:\d{4}[^\]:]*?|Slavic-Root):[^\]]+)\]', new_line)
        if m_h:
            key = m_h.group(1)
            cur_h = m_h.group(2).strip()
            if key in canonical_hists and canonical_hists[key] != cur_h:
                expected_h = canonical_hists[key]
                new_line = new_line.replace(f"[{cur_h}]", f"[{expected_h}]", 1)
                print(f"[Sync] Updated {key} historical note: '{cur_h}' -> '{expected_h}'")
                changes += 1
        elif m_c and m_c.group(2) in canonical_hists:
            key = m_c.group(2)
            m_tail = re.search(r'(\*Tarraconian:\s*\*\*[^*]+\*\*)(\*+)(\s*)$', new_line)
            if m_tail:
                expected_h = canonical_hists[key]
                new_line = (
                    new_line[:m_tail.start()]
                    + f"{m_tail.group(1)} (`[{expected_h}]`){m_tail.group(2)}{m_tail.group(3)}"
                )
                print(f"[Sync] Added {key} historical note: '{expected_h}'")
                changes += 1

        # 3. Match archdiocese table pattern:
        # | **Archdiocese of Bari** | `d_et_bari` | Bâr-in-Pûlje (`c_bari`) | ...
        m_arch = re.search(r'\|\s*\*\*Archdiocese of [^*]+\*\*\s*\|\s*`([a-zA-Z0-9_\-]+)`\s*\|\s*([^|`]+)\(`c_[a-zA-Z0-9_\-]+`\)', new_line)
        if m_arch:
            d_key, cur_seat = m_arch.group(1), m_arch.group(2).strip()
            if d_key in canonical_names:
                canon_arch = canonical_names[d_key]
                canon_seat = re.sub(r'^Erzbisdom\s+van\s+', '', canon_arch).strip()
                if cur_seat != canon_seat:
                    new_line = new_line.replace(f"| {cur_seat} (`c_", f"| {canon_seat} (`c_")
                    print(f"[Sync] Updated {d_key} seat: '{cur_seat}' -> '{canon_seat}'")
                    changes += 1

        updated_lines.append(new_line)

    if changes > 0:
        newline_char = '\r\n' if is_crlf else '\n'
        with open(hre_md, 'wb') as f:
            f.write(newline_char.join(updated_lines).encode('utf-8'))
        print(f"[Sync] Successfully synchronized {changes} titles/notes in {hre_md.name}!")
    else:
        print(f"[Sync] {hre_md.name} is already 100% in sync with {tarr_md.name}!")

    return True

if __name__ == '__main__':
    sync_hre_gazetteer()

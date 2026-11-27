#!/usr/bin/env python3
"""
Comprehensive Phonotactic & Sound-Change Audit for Kingdom and Duchy Titles.
Checks titles against rules in:
- tarraconian_linguistics_guide.md
- sinosphere_phonetics_and_transcription_guide_1154.md
"""

import re
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from tarraconian_phonotactics import check_title_phonotactics  # noqa: E402

def clean_title(raw_str):
    """Strip prefixes, markdown formatting, IPA, and philological notes."""
    s = raw_str.strip()
    # Remove nested or single bracket/parenthetical notes
    while re.search(r"\([^()]*\)", s):
        s = re.sub(r"\([^()]*\)", "", s)
    while re.search(r"\[[^\[\]]*\]", s):
        s = re.sub(r"\[[^\[\]]*\]", "", s)
    s = s.replace("**", "").replace("*", "")
    s = re.sub(r"^(Kûnincrich|Gubernat|Keiserrîch|Magistrat|Erzbisdom|Fürstbisdom)\s+van\s+(?:dem\s+|der\s+|den\s+)?", "", s, flags=re.I)
    return s.strip()

def audit_sinosphere():
    print("=== AUDITING SINOSPHERE KINGDOMS & DUCHIES ===")
    
    # 1. sinosphere_titles_and_characters_1154.md
    with open("sinosphere_titles_and_characters_1154.md") as f:
        sino_md = f.read()

    sino_titles = []
    for line in sino_md.splitlines():
        # Kingdoms
        m_k = re.search(r"^####\s+[\d\.]+\s+Kingdom\s+of\s+([^(]+)\(`(k_[^`]+)`\s*/\s*([^)]+)\)\s*—\s*\*\*([^*]+)\*\*", line)
        if m_k:
            sino_titles.append((m_k.group(2), f"Kingdom of {m_k.group(1).strip()}", m_k.group(4).strip(), "sinosphere_titles_and_characters_1154.md"))
        # Duchies
        m_d = re.search(r"^#####\s+Duchy\s+of\s+([^(]+)\(`([dx][^`]+)`\s*/\s*([^)]+)\)\s*—\s*\*\*([^*]+)\*\*", line)
        if m_d:
            sino_titles.append((m_d.group(2), f"Duchy of {m_d.group(1).strip()}", m_d.group(4).strip(), "sinosphere_titles_and_characters_1154.md"))

    total_issues = 0
    for key, name, tarr, src in sino_titles:
        issues = check_title_phonotactics(tarr, key, src)
        if issues:
            total_issues += len(issues)
            print(f"[{key}] {name} -> {tarr}")
            for iss in issues:
                print(f"  * ISSUE: {iss}")

    print(f"Total Sinosphere titles audited: {len(sino_titles)} | Issues found: {total_issues}\n")

def audit_gazetteer():
    print("=== AUDITING MASTER GAZETTEER (tarraconian_titles_1059.md) ===")
    with open("tarraconian_titles_1059.md") as f:
        text = f.read()

    titles = []

    # Section 2 Kingdom table
    for line in text.splitlines():
        m = re.search(r"^\|\s*(\d+)\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*`([kd]_[^`]+|x_script_\d+)`\s*\|\s*([^|]+)\|", line)
        if m:
            titles.append((m.group(3).strip(), f"Kingdom of {m.group(2).strip()}", m.group(4).strip(), f"Table row {m.group(1)}"))

    # Section 3 Kingdoms
    for line in text.splitlines():
        m = re.search(r"^###\s+([\d\.]+)\s+Kingdom\s+of\s+([^(]+)\(`(k_[^`]+)`\)\s*(?:\$\\rightarrow\$|->|→)\s*(.+)", line)
        if m:
            titles.append((m.group(3).strip(), f"Kingdom of {m.group(2).strip()}", m.group(4).strip(), f"Section {m.group(1)}"))

    # Section 3 Duchies
    for line in text.splitlines():
        m = re.search(r"^\*\s+\*\*Duchy\s+of\s+([^*]+)\*\*\s*\(`([d|x][^`]+)`\)\s*(?:\$\\rightarrow\$|->|→)\s*(.+)", line)
        if m:
            titles.append((m.group(2).strip(), f"Duchy of {m.group(1).strip()}", m.group(3).strip(), "Duchy Bullet"))

    # Section 3 Counties
    for line in text.splitlines():
        m = re.search(r"^\s*\*\s*`([c][a-zA-Z0-9_\-]+)`\s*\(([^)]*)\)\s*(?:\$\\rightarrow\$|->|→)\s*(.+)", line)
        if m:
            titles.append((m.group(1).strip(), f"County of {m.group(2).strip()}", m.group(3).strip(), "County Bullet"))

    total_issues = 0
    for key, name, tarr_line, src in titles:
        # Extract bold title names (canonical title and any bold alternates)
        bold_names = re.findall(r'\*\*([^*]+)\*\*', tarr_line)
        if not bold_names:
            bold_names = [tarr_line]
        for tarr in bold_names:
            issues = check_title_phonotactics(tarr, key, src)
            if issues:
                total_issues += len(issues)
                print(f"[{key}] ({src}) {name} -> {tarr}")
                for iss in issues:
                    print(f"  * ISSUE: {iss}")

    print(f"Total master gazetteer titles audited: {len(titles)} | Issues found: {total_issues}\n")

def audit_discrepancy_register():
    print("=== AUDITING AUDIT DISCREPANCY REGISTER (audit_discrepancy_register.md) ===")
    p = Path("audit_discrepancy_register.md")
    if not p.exists():
        return
    text = p.read_text(encoding="utf-8")
    rows = re.findall(r'\|\s*`([a-z0-9_]+)`\s*\|\s*([^|]+)\|\s*([a-z0-9_\-]+)\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*\*\*([^*]+)\*\*\s*\|\s*\*([^*]+)\*\s*\|\s*([^|\n]+)\|', text)
    
    total_issues = 0
    for r in rows:
        key, save_name, kingdom, tier, reason, res, title, adj, just = r
        iss1 = check_title_phonotactics(title, key, f"{kingdom} title")
        iss2 = check_title_phonotactics(adj, key, f"{kingdom} adj")
        issues = iss1 + iss2
        if issues:
            total_issues += len(issues)
            print(f"[{key}] ({kingdom}) {title} -> {adj}")
            for iss in issues:
                print(f"  * ISSUE: {iss}")
                
    print(f"Total discrepancy register titles audited: {len(rows)} | Issues found: {total_issues}\n")

if __name__ == "__main__":
    audit_sinosphere()
    audit_gazetteer()
    audit_discrepancy_register()

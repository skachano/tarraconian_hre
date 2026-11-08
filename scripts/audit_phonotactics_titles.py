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

def clean_title(raw_str):
    """Strip prefixes and markdown formatting."""
    s = raw_str.strip()
    # Remove markdown bold/italics
    s = s.replace("**", "").replace("*", "")
    # Remove tier prefixes
    s = re.sub(r"^(Kûnincrich|Gubernat|Keiserrîch|Magistrat)\s+van\s+(?:dem\s+|der\s+|den\s+)?", "", s, flags=re.I)
    return s.strip()

def check_title_phonotactics(raw_title, key, source_context):
    issues = []
    
    # Check parenthetical / variant forms if present
    # e.g. "Gubernat van X *(or Y)*"
    parts = re.split(r"\s*(?:\*\(or\s+|\bor\b|\/)\s*", raw_title)
    
    for part in parts:
        part_clean = clean_title(part)
        # ignore empty or note parts
        if not part_clean or "direct vanilla" in part_clean.lower() or "attested" in part_clean.lower() or "calque" in part_clean.lower():
            continue
            
        name = part_clean.strip("()*, ")
        
        # 1. Acute accents (should be circumflex)
        acutes = re.findall(r"[áéíóúÁÉÍÓÚ]", name)
        if acutes:
            issues.append(f"Acute accent {acutes} in '{name}' (must use circumflex â, ê, î, ô, û)")
            
        # 2. Illicit digraph: eo (Modern Korean Revised Romanization)
        if re.search(r"eo", name, re.I):
            issues.append(f"Illicit digraph 'eo' in '{name}' (prohibited modern Korean Romanization)")

        # 3. Modern Pinyin: zh
        if re.search(r"zh", name, re.I):
            issues.append(f"Modern Pinyin 'zh' in '{name}' (must be 'dsch')")

        # 4. Bare 'sh' (not part of 'sch')
        # match 'sh' not preceded by 'c'
        sh_matches = re.findall(r"(?<!c)sh", name, re.I)
        if sh_matches:
            issues.append(f"Non-German 'sh' {sh_matches} in '{name}' (must be 'sch')")

        # 5. Initial ts- (Rule 5.1: Initial [ts] is strictly 'z-')
        ts_init = re.findall(r"\bts(?!ch)", name, re.I)
        if ts_init:
            issues.append(f"Initial 'ts-' (not 'tsch-') in '{name}' (Rule 5.1: Initial [ts] must be 'z-')")

        # 6. Pinyin bare q (not 'qu')
        if re.search(r"\bq(?!u)", name, re.I):
            issues.append(f"Pinyin 'q-' in '{name}' (must be 'tsch' or 'ch')")

        # 7. Final -burg instead of -burch (Auslautverhärtung)
        if re.search(r"burg\b", name, re.I):
            issues.append(f"Final '-burg' in '{name}' (Auslautverhärtung requires '-burch')")

        # 8. Final -bad instead of -bat
        if re.search(r"bad\b", name, re.I) and not re.search(r"bagdad", name, re.I):
            issues.append(f"Final '-bad' in '{name}' (Auslautverhärtung requires '-bat')")

        # 9. Pinyin / modern Chinese affricate 'j' (Jin, Jing, Jiang, Jiao, Jie, etc.)
        # Note: In genuine Tarraconian, J- is [j] (glide).
        # But if it's Chinese affricate, it must be Dsch-!
        # Check against common Chinese affricate roots
        pinyin_j_roots = [
            r"\bji(?!m|n|e|a|u)", # wait, let us check specific Chinese stems
        ]

    return issues

def audit_sinosphere():
    print("=== AUDITING SINOSPHERE KINGDOMS & DUCHIES ===")
    
    # 1. sinosphere_titles_and_characters_1154.md
    with open("sinosphere_titles_and_characters_1154.md") as f:
        sino_md = f.read()

    sino_titles = []
    for line in sino_md.splitlines():
        # Kingdoms
        m_k = re.search(r"^####\s+[\d\.]+\s+Kingdom\s+of\s+([^(]+)\(`(k_[^`]+)`\s*/\s*([^)]+)\)\s*—\s*(.+)", line)
        if m_k:
            sino_titles.append((m_k.group(2), f"Kingdom of {m_k.group(1).strip()}", m_k.group(4).strip(), "sinosphere_titles_and_characters_1154.md"))
        # Duchies
        m_d = re.search(r"^#####\s+Duchy\s+of\s+([^(]+)\(`([dx][^`]+)`\s*/\s*([^)]+)\)\s*—\s*(.+)", line)
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

    total_issues = 0
    for key, name, tarr, src in titles:
        issues = check_title_phonotactics(tarr, key, src)
        if issues:
            total_issues += len(issues)
            print(f"[{key}] ({src}) {name} -> {tarr}")
            for iss in issues:
                print(f"  * ISSUE: {iss}")

    print(f"Total master gazetteer titles audited: {len(titles)} | Issues found: {total_issues}\n")

if __name__ == "__main__":
    audit_sinosphere()
    audit_gazetteer()

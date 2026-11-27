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
            
        # 2. Illicit digraph: eo (Modern Korean Revised Romanization; exempt Greek Georg-, Neo-, and Theo-)
        if re.search(r"(?<!g)(?<!n)(?<!th)eo", name, re.I):
            issues.append(f"Illicit digraph 'eo' in '{name}' (prohibited modern Korean Romanization)")

        # 3. Modern Pinyin: zh (exempting Tarraconian compound boundaries like Flôz-hügil, Grôz-hâven, Swartz-hirsch)
        if re.search(r"zh(?!(?:eim|ûsen|âven|aven|ügil|irsch|êilichdom|îa|êl|ôch|olm|of|ûs|ain|age|al|out))", name, re.I):
            issues.append(f"Modern Pinyin 'zh' in '{name}' (must be 'dsch')")

        # 4. Bare 'sh' (not part of 'sch', exempting compound boundaries like -heim, -hûsen, -hâven, -hügil, -hêl, -holm)
        sh_matches = re.findall(r"(?<!c)sh(?!(?:eim|ûsen|âven|aven|ügil|irsch|êilichdom|îa|êl|ôch|olm|of|ûs|ain|age|al|out))", name, re.I)
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

        # 9. Word-final -dsch instead of -tsch
        if re.search(r"dsch\b", name, re.I):
            issues.append(f"Word-final '-dsch' in '{name}' (Auslautverhärtung requires '-tsch')")

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

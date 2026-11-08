import re
from collections import defaultdict

def parse_sinosphere_kanji():
    with open('sinosphere_titles_and_characters_1154.md', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    title_kanji = defaultdict(list)
    title_keys_seen = set()

    for line_idx, line in enumerate(lines):
        line_clean = line.strip()
        if not line_clean:
            continue
        
        # Skip header rows of markdown tables
        if 'Chinese Characters (汉字)' in line_clean or line_clean.startswith('| :---') or line_clean.startswith('|:---'):
            continue
        
        # Section 1.2 Empire summary table:
        # | 1 | **Andong** | `e_andong` | **安东** | ...
        if line_clean.startswith('|') and '`e_' in line_clean:
            parts = [p.strip() for p in line_clean.split('|') if p.strip()]
            if len(parts) >= 4 and parts[2].startswith('`e_'):
                emp_name = parts[1].replace('*', '').strip()
                emp_key = parts[2].replace('`', '').strip()
                emp_chars = parts[3]
                title_keys_seen.add(emp_key)
                for c in re.findall(r'[\u4e00-\u9fff]', emp_chars):
                    title_kanji[c].append((emp_key, emp_name))
        
        # County tables in Section 2 and 3:
        # | # | County Key | English Name | Chinese Characters (汉字) | Traditional / Variant | ...
        # e.g.: | 1 | `c_kaifeng` | **Kaifeng** | **开封** | 開封 | ...
        if line_clean.startswith('|') and '`c_' in line_clean:
            parts = [p.strip() for p in line_clean.split('|')]
            if len(parts) >= 6 and '`c_' in parts[2]:
                c_key = parts[2].replace('`', '').strip()
                c_name = parts[3].replace('*', '').strip()
                c_simp = parts[4].replace('*', '').strip()
                c_trad = parts[5].replace('*', '').strip()
                title_keys_seen.add(c_key)
                for c in re.findall(r'[\u4e00-\u9fff]', c_simp):
                    title_kanji[c].append((c_key, c_name))
                if c_trad and c_trad != '-':
                    for c in re.findall(r'[\u4e00-\u9fff]', c_trad):
                        title_kanji[c].append((c_key, f"{c_name} (Trad)"))

        # Duchy & Kingdom headers:
        # #### 2.1.1 Kingdom of Daibei (`k_daibei` / 代北)
        # ##### Duchy of Sanggan (`d_sanggan` / 桑干) — *4/4 in Roman Empire*
        m_kd = re.search(r'#+\s*(?:[\d\.]+\s*)?(?:Kingdom|Duchy)\s+of\s+([^(]+)\(`([kd]_[^`]+)`\s*/\s*([^)]+)\)', line_clean)
        if m_kd:
            t_name = m_kd.group(1).strip()
            t_key = m_kd.group(2).strip()
            t_chars = m_kd.group(3).strip()
            title_keys_seen.add(t_key)
            for c in re.findall(r'[\u4e00-\u9fff]', t_chars):
                title_kanji[c].append((t_key, t_name))

        # Section 4 Kingdom table:
        # | Rank | Kingdom | Title Key | Empire | Characters | ...
        if line_clean.startswith('|') and '`k_' in line_clean:
            parts = [p.strip() for p in line_clean.split('|') if p.strip()]
            if len(parts) >= 5 and '`k_' in parts[2]:
                k_name = parts[1].replace('*', '').strip()
                k_key = parts[2].replace('`', '').strip()
                k_chars = parts[4].replace('*', '').strip()
                title_keys_seen.add(k_key)
                for c in re.findall(r'[\u4e00-\u9fff]', k_chars):
                    title_kanji[c].append((k_key, k_name))

    print(f"Total unique titles parsed: {len(title_keys_seen)}")
    print(f"Total unique characters in titles: {len(title_kanji)}")
    return title_kanji

if __name__ == '__main__':
    title_kanji = parse_sinosphere_kanji()
    sorted_kanji = sorted(title_kanji.keys(), key=lambda c: len(title_kanji[c]), reverse=True)
    print("Sample top 25 characters:")
    for c in sorted_kanji[:25]:
        print(f"{c}: {len(title_kanji[c])} occurrences (e.g., {title_kanji[c][:3]})")

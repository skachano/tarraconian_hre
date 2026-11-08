import json, re

with open("data/sinosphere_kanji_tarraconian.json") as f:
    kanji_data = json.load(f)

char_map = {k["char"]: k for k in kanji_data}
for k in kanji_data:
    if k.get("var") and k["var"] != "-":
        char_map[k["var"]] = k

# Exemplar lookup
key_to_ex = {}
for entry in kanji_data:
    ex = entry.get("tarr_example", "")
    for line in re.split(r"<br>|/", ex):
        m = re.search(r"([ecdk]_[a-zA-Z0-9_]+)\s*([^->]*)\s*->\s*(.+)", line)
        if m:
            k = m.group(1).strip()
            ch = m.group(2).strip()
            res = m.group(3).strip()
            res = re.sub(r"<[^>]+>", "", res).strip()
            stem = re.sub(r"^(Magistrat|Gubernat|Kûnincrich|Keiserrîch)\s+van\s+(dem\s+|der\s+|den\s+)?", "", res, flags=re.I).strip()
            if k not in key_to_ex:
                key_to_ex[k] = stem

manual_kingdoms = {
    "k_daibei": "Kûnincrich van Dênordlant",
    "k_hebei": "Kûnincrich van dem Nordflôze",
    "k_hedong": "Kûnincrich van dem Ôstflôze",
    "k_henan": "Kûnincrich van dem Sûtflôze",
    "k_qingxu": "Kûnincrich van Blousacht",
    "k_youji": "Kûnincrich van Düsterdistel",
    "k_dali": "Kûnincrich van Grôzrecht",
    "k_dongchuan": "Kûnincrich van dem Ôstbache",
    "k_kuizhou": "Kûnincrich van Kuîgouwe",
    "k_qianzhong": "Kûnincrich van dem Swartzmidden",
    "k_xichuan": "Kûnincrich van dem Westbache",
    "k_xingyuan": "Kûnincrich van Bloyvürst",
    "k_fujian": "Kûnincrich van Sêlichbache",
    "k_huainan": "Kûnincrich van dem Sûthuai",
    "k_hunan": "Kûnincrich van dem Sûtsê",
    "k_jiangdong": "Kûnincrich van dem Ôstflôze",
    "k_jiangxi": "Kûnincrich van dem Westflôze",
    "k_liangzhe": "Kûnincrich van den Tweê-Tsche",
    "k_shannan": "Kûnincrich van dem Sûtberch",
    "k_guannei": "Kûnincrich van der Binnenklûse",
    "k_hexi": "Kûnincrich van dem Westflôze",
    "k_xia": "Kûnincrich van dem Sommerlant",
    "k_lingnan": "Kûnincrich van dem Sûtrücke",
    "k_lingxi": "Kûnincrich van dem Westrücke",
    "k_viet": "Kûnincrich van Jüetlant",
    "k_baekje": "Kûnincrich van Bêkdsche",
    "k_goguryeo": "Kûnincrich van Gôgûrjeo",
    "k_silla": "Kûnincrich van Schilla",
    "k_azuma": "Kûnincrich van Azuma",
    "k_tsukushi": "Kûnincrich van Tsukûschi",
    "k_yamato": "Kûnincrich van Jamato",
    "k_balhae": "Kûnincrich van dem Bôchmêre",
    "k_khitan": "Kûnincrich van Chitân",
    "k_luzhen": "Kûnincrich van Sinswâr",
    "k_raole": "Kûnincrich van Rîchvro",
    "k_shiwei": "Kûnincrich van Schîwêj",
    "k_amur": "Kûnincrich van Amûrlant",
    "k_aynumosir": "Kûnincrich van Ajnulant",
    "k_hitakami": "Kûnincrich van Hîtakamî",
}

manual_empires = {
    "e_andong": "Keiserrîch van dem Ôstfrid",
    "e_liangyi": "Keiserrîch van Lîangjî",
    "e_zhongyuan": "Keiserrîch van dem Middenvelt",
    "e_jingyang": "Keiserrîch van Dôrnflôz",
    "e_yongliang": "Keiserrîch van dem Kôlen-Vredelant",
    "e_japan": "Keiserrîch van der Sunnenorigin",
    "e_lingnan": "Keiserrîch van dem Sûtrücke",
    "e_goryeo": "Keiserrîch van den Drî-Hânen",
    "e_amur": "Keiserrîch van Amûrlant",
}

def clean_stem(s):
    s = s.replace("-", "").strip()
    return s[0].upper() + s[1:] if s else ""

def generate_calque(key, name, simp, tier="c"):
    if tier == "e":
        return manual_empires.get(key, f"Keiserrîch van {name}")
    if tier == "k":
        return manual_kingdoms.get(key, f"Kûnincrich van {name}")
    
    # Specific known fixes
    if simp == "九十九泉": return "Magistrat van Niuntzig-ende-Niunbrunn"
    if simp == "怀安": return "Magistrat van Koesterfrid"
    if simp == "对涯村": return "Magistrat van Tegenstrantdorp"
    if simp == "原州": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van Veltgouwe"
    if simp == "河中": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van dem Middenflôze"
    if simp == "卫州": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van Wachtgouwe"
    if simp == "魏州": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van Wêjgouwe"
    if simp == "桑干": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van dem Mûlberienbache"
    if simp == "振武": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van Wâpenmacht"
    if simp == "云朔": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van Wolchennord"
    if simp == "沧景": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van Kôlblouschouwe"
    if simp == "成德": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van Vollbrâchtdôget"
    if simp == "河阳": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van Flôzsunne"
    if simp == "魏博": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van Wêiweit"
    if simp == "邢洺": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van Schîng-Mîng"
    if simp == "河东": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van dem Ôstflôze"
    if simp == "雁门": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van dem Ganstôre"
    if simp == "泽潞": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van Lûbrûch"
    if simp == "汴宋": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van Bîensông"
    if simp == "陈许": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van Tschênschû"
    if simp == "东畿": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van der Ôstkeisermarch"
    if simp == "陕虢": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van Klûsengûôk"
    if simp == "郑滑": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van Dschêngglitscher"
    if simp == "徐泗": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van Schûsî"
    if simp == "兖海": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van Jânmêr"
    if simp == "郓曹": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van Wallstat-Tsô"
    if simp == "淄青": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van Zîblou"
    if simp == "易定": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van Îfest"
    if simp == "瀛莫": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van Ôstmêr-Mô"
    if simp == "幽州": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van Jôugouwe"
    if simp == "大理": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van Grôzrecht"
    if simp == "会川": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van dem Samelingbache"
    if simp == "剑川": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van dem Swertbache"
    if simp == "通海": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van Dörchgancmêr"
    if simp == "拓东": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van Ontgont-Ôst"
    if simp == "银生": return f"{'Gubernat' if tier=='d' else 'Magistrat'} van Silberlêven"

    # If exemplar exists in key_to_ex and matches title
    if key in key_to_ex:
        prefix = "Gubernat van" if tier == "d" else "Magistrat van"
        raw = key_to_ex[key]
        raw_clean = clean_stem(raw)
        return f"{prefix} {raw_clean}"

    chars = re.findall(r"[\u4e00-\u9fff]", simp)
    if not chars:
        prefix = "Gubernat van" if tier == "d" else "Magistrat van"
        return f"{prefix} {name}"

    parts = []
    for c in chars:
        entry = char_map.get(c, {})
        m = entry.get("tarr_morpheme", c)
        parts.append((c, m, entry.get("tarr_role", "")))

    prefix = "Gubernat van" if tier == "d" else "Magistrat van"

    if len(parts) == 1:
        c, m, r = parts[0]
        s = clean_stem(m)
        if tier == "c" and c == "州":
            return f"{prefix} Gouwe"
        return f"{prefix} {s}"

    if len(parts) == 2:
        c1, m1, r1 = parts[0]
        c2, m2, r2 = parts[1]
        s1 = clean_stem(m1)
        s2 = clean_stem(m2)

        if c2 == "州": return f"{prefix} {s1}gouwe"
        if c2 in ("城", "堡"): return f"{prefix} {s1}burch"
        if c2 == "山": return f"{prefix} {s1}berch"
        if c2 == "川": return f"{prefix} {s1}bache"
        if c2 in ("河", "江"): return f"{prefix} {s1}flôz"
        if c2 == "关": return f"{prefix} {s1}klûse"
        if c2 == "原": return f"{prefix} {s1}veit"
        if c2 == "阳": return f"{prefix} {s1}sunne"
        if c2 == "阴": return f"{prefix} {s1}schate"
        if c2 == "海": return f"{prefix} {s1}mêr"
        if c2 in ("湖", "池"): return f"{prefix} {s1}sê"
        if c2 == "泉": return f"{prefix} {s1}brunn"
        if c2 == "安": return f"{prefix} {s1}frid"
        if c2 == "宁": return f"{prefix} {s1}rûwe"
        if c2 == "定": return f"{prefix} {s1}fest"
        if c2 == "平": return f"{prefix} {s1}ebene"
        if c2 == "昌": return f"{prefix} {s1}glantz"
        if c2 == "兴": return f"{prefix} {s1}bloy"
        if c2 == "德": return f"{prefix} {s1}dôget"
        if c2 == "门": return f"{prefix} {s1}tôr"
        if c2 == "陵": return f"{prefix} {s1}hügel"
        if c2 in ("港", "津"): return f"{prefix} {s1}haven"
        if c2 == "市": return f"{prefix} {s1}markt"
        if c2 == "村": return f"{prefix} {s1}dorp"

        return f"{prefix} {s1}{s2.lower()}"

    if len(parts) >= 3:
        if parts[-1][0] == "州":
            pfx = "".join(clean_stem(p[1]) for p in parts[:-1])
            return f"{prefix} {pfx}gouwe"
        if parts[-1][0] in ("城", "堡"):
            pfx = "".join(clean_stem(p[1]) for p in parts[:-1])
            return f"{prefix} {pfx}burch"
        if parts[-1][0] == "山":
            pfx = "".join(clean_stem(p[1]) for p in parts[:-1])
            return f"{prefix} {pfx}berch"
        if parts[-1][0] in ("河", "江"):
            pfx = "".join(clean_stem(p[1]) for p in parts[:-1])
            return f"{prefix} {pfx}flôz"
        if parts[-1][0] == "川":
            pfx = "".join(clean_stem(p[1]) for p in parts[:-1])
            return f"{prefix} {pfx}bache"
        
        comp = "".join(clean_stem(p[1]) for p in parts)
        return f"{prefix} {comp}"

# Read all titles from sinosphere_titles_and_characters_1154.md
with open("sinosphere_titles_and_characters_1154.md") as f:
    text = f.read()

title_dict = {}

# 1. Empires
for line in text.splitlines():
    l = line.strip()
    if l.startswith("|") and "`e_" in l:
        parts = [p.strip() for p in l.split("|") if p.strip()]
        if len(parts) >= 4 and parts[2].startswith("`e_"):
            k = parts[2].replace("`", "").strip()
            name = parts[1].replace("*", "").strip()
            chars = parts[3].replace("*", "").strip()
            title_dict[k] = generate_calque(k, name, chars, tier="e")

# 2. Kingdoms
for line in text.splitlines():
    l = line.strip()
    m_k = re.search(r"^####\s+[\d\.]+\s+Kingdom\s+of\s+([^(]+)\(`(k_[^`]+)`\s*/\s*([^)]+)\)", l)
    if m_k:
        k = m_k.group(2).strip()
        name = m_k.group(1).strip()
        chars = m_k.group(3).strip()
        title_dict[k] = generate_calque(k, name, chars, tier="k")

# 3. Duchies
for line in text.splitlines():
    l = line.strip()
    m_d = re.search(r"^#####\s+Duchy\s+of\s+([^(]+)\(`(d_[^`]+)`\s*/\s*([^)]+)\)", l)
    if m_d:
        k = m_d.group(2).strip()
        name = m_d.group(1).strip()
        chars = m_d.group(3).strip()
        title_dict[k] = generate_calque(k, name, chars, tier="d")

# 4. Counties
for line in text.splitlines():
    l = line.strip()
    if l.startswith("|") and "`c_" in l and "Historical Status & Resolution" not in l:
        parts = [p.strip() for p in l.split("|")]
        if len(parts) >= 6 and "`c_" in parts[2]:
            k = parts[2].replace("`", "").strip()
            name = parts[3].replace("*", "").strip()
            chars = parts[4].replace("*", "").strip()
            if k not in title_dict:
                title_dict[k] = generate_calque(k, name, chars, tier="c")

print(f"Total titles processed into title_dict: {len(title_dict)}")
with open("data/sinosphere_title_calques.json", "w", encoding="utf-8") as f:
    json.dump(title_dict, f, ensure_ascii=False, indent=2)

print("Saved to data/sinosphere_title_calques.json")

import os
import sys
import re
import json
import unicodedata
from collections import defaultdict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from scripts.parse_kanji import parse_sinosphere_kanji
from scripts.kanji_part1 import PART1_DATA
from scripts.kanji_part2 import PART2_DATA
from scripts.kanji_part3 import PART3_DATA
from scripts.kanji_part4 import PART4_DATA

CATEGORY_NAMES = {
    1: "Administrative Classifiers, Jurisdictions & Civic Strongholds",
    2: "Hydrography, Waterways, Coasts & Springs",
    3: "Orography, Landforms, Relief & Geomorphology",
    4: "Cardinal Directions, Spatial Geometry & Relative Orientations",
    5: "Flora, Trees, Vegetation & Agriculture",
    6: "Fauna, Animals & Mythological Creatures",
    7: "Minerals, Metals, Colors, Elements & Meteorology",
    8: "Auspicious Qualities, Imperial Virtues & Cosmic Mandate",
    9: "Toponymic Verbs, Modifiers, Dynamics & Quantifiers",
    10: "Dynastic Stems, Ethnonyms, Transcriptions & Regional Stems"
}

CATEGORY_DESCRIPTIONS = {
    1: "Imperial administrative tiers, municipal jurisdictions, fortified settlements, citadels, passes, and civic boundary formants (e.g. 州 `-gouwe`, 城 `-burch`, 关 `-klûse`, 京 `-hôfstat`, 府 `-ambet`, 镇 `-wart`).",
    2: "Natural and artificial waterways, rivers, streams, lakes, gulfs, springs, rapids, canal conduits, and riparian margins (e.g. 河/江 `-flôz`, 川 `-bache`, 水 `-wazzer`, 湖 `-sê`, 海 `-mêr`, 泉 `-brunn`, 津 `-haven`).",
    3: "Mountain elevations, alpine divides, plateaus, valleys, canyons, slopes, islands, promontories, and cliffs (e.g. 山 `-berch`, 岭 `-rücke`, 岳 `-hôchberch`, 原 `-veit`, 谷 `-dal`, 峡 `-enge`, 岬 `-necke`).",
    4: "Compass points, inner/outer frontiers, positional alignments, and relative geographical orientations (e.g. 东 `Ôst-`, 西 `West-`, 南 `Sût-`, 北 `Nord-`, 中 `Midden-`, 上 `Ôver-`, 下 `Nider-`, 内 `Binnen-`, 外 `Ûzen-`).",
    5: "Woodlands, timber stands, flowering trees, bamboo, agricultural crops, cultivated paddies, and herbs (e.g. 林 `-walt`, 桑 `Mûlberie-`, 松 `Pîn-`, 柳 `Wîden-`, 田 `-acker`, 桂 `Lôrber-`).",
    6: "Equine mounts, livestock, wildlife, avian species, and sovereign mythological beasts (e.g. 龙 `Drachen-`, 凤 `Fênix-`, 马 `Ros-`, 鹿 `Hirsch-`, 鱼 `Fisch-`, 鸭 `Antflôz-`, 麟 `Eênhoorn-`).",
    7: "Precious and utilitarian minerals, metallurgical deposits, celestial bodies, weather phenomena, and heraldic colors (e.g. 金 `Golt-`, 银 `Silber-`, 铁 `Îsen-`, 白 `Wîz-`, 黑 `Swartz-`, 青 `Blou-`, 云 `Wolchen-`, 雷 `Donder-`).",
    8: "Imperial governance virtues, pacification titles, moral principles, longevity blessings, and auspicious omens (e.g. 安 `Frid-`, 宁 `Rûwe-`, 定 `Fest-`, 平 `Ebene-`, 德 `Dôget-`, 泰 `Grôzfrid-`, 福 `Sêlich-`, 庆 `Fröude-`).",
    9: "Topographic size adjectives, foundational verbs, directional shifts, and numerical qualifiers (e.g. 大 `Grôz-`, 小 `Klein-`, 太 `Allergrôzst-`, 新 `Nîe-`, 古 `Alt-`, 开 `Open-`, 建 `Sticht-`, 一 `Eên-`, 三 `Drî-`, 万 `Têndûsent-`).",
    10: "Classical Sinitic dynastic kingdoms, ancient non-Han ethnic groups, Steppe nomad transcriptions, and unique regional phonetic toponyms (e.g. 汉 `Hân-`, 唐 `Tâng-`, 宋 `Sông-`, 晋 `Schîn-`, 契丹 `Chitân-`, 辽 `Ljô-`, 越 `Jüet-`, 蒙 `Mongol-`)."
}

def clean_pinyin_for_sort(pinyin_str):
    s = pinyin_str.lower().split('/')[0].strip()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join([c for c in s if not unicodedata.combining(c)])
    s = re.sub(r'[^a-z]', '', s)
    return s

def assemble_master_database():
    title_kanji = parse_sinosphere_kanji()
    
    merged_raw = {}
    for p in [PART1_DATA, PART2_DATA, PART3_DATA, PART4_DATA]:
        merged_raw.update(p)

    assert len(merged_raw) == 641, f"Expected 641, got {len(merged_raw)}"
    assert len(title_kanji) == 641, f"Expected 641 from titles, got {len(title_kanji)}"

    db = []
    for char, raw in merged_raw.items():
        var, pinyin, jp, kr, cat, meaning, morpheme, ipa, role, example = raw
        titles = title_kanji.get(char, [])
        t_sample = [f"{t[1]} (`{t[0]}`)" for t in titles[:4]]
        
        record = {
            'char': char,
            'var': var,
            'pinyin': pinyin,
            'pinyin_sort': clean_pinyin_for_sort(pinyin),
            'jp': jp,
            'kr': kr,
            'cat_id': cat,
            'cat_name': CATEGORY_NAMES[cat],
            'meaning': meaning,
            'tarr_morpheme': morpheme,
            'tarr_ipa': ipa,
            'tarr_role': role,
            'tarr_example': example,
            'title_count': len(titles),
            'titles': t_sample
        }
        db.append(record)

    db.sort(key=lambda x: x['pinyin_sort'])
    for idx, r in enumerate(db, 1):
        r['id'] = idx

    return db

def generate_markdown(db):
    total_kanji = len(db)
    
    by_cat = defaultdict(list)
    for r in db:
        by_cat[r['cat_id']].append(r)
        
    md = []
    md.append("# Sinosphere Kanji Toponymic Lexicon & Tarraconian Interpretation Index\n")
    md.append("> **Historical Linguistic Reference & Chancellery Gazetteering Guide**  ")
    md.append("> **Campaign Date:** 27 December 1154 (`1154.12.27`)  ")
    md.append("> **Campaign Save Game:** `chatenois_867_01_01.ck3` | **Imperial Realm:** The Roman Empire (*Dat Rômische Keiserrîch*)  ")
    md.append("> **Total Attested Sinosphere Kanji:** **641 Distinct Characters** (100% Comprehensive Coverage)  ")
    md.append("> **Governing Principles:** [Tarraconian Linguistics Guide](tarraconian_linguistics_guide.md) | [Semantic Calque Matrix](tarraconian_descriptive_title_calques.md) | [Sinosphere Title Gazetteer](sinosphere_titles_and_characters_1154.md)\n")
    md.append("---\n")
    
    md.append("## 1. Executive Summary & Chancellery Calquing Doctrine\n")
    md.append("In the administration of East Asian provinces across the **Core Middle Kingdom** (China Proper), the **Korean Peninsula** (Goryeo/Samhan), the **Japanese Archipelago** (Yamato), and the **Northern Marches** (Liao, Bohai, Jurchen, and Amur), imperial scribes operate within a logographic toponymic system. Unlike alphabetic place names that function as opaque phonetic tokens, **Sinospheric toponyms are inherently semantic and logographic** (*Hànzì*, *Hanja*, *Kanji*, *Chữ Hán*).\n")
    md.append("Following the project's **Chancellery Calquing Paradigm** (*Lehnübersetzung*), the Tarraconian Chancellery resolves East Asian toponyms using a two-tiered protocol:\n")
    md.append("1. **Descriptive, Topographic, and Administrative Morphemes:** Translated root-for-root into High German (Moselle/Rhine Franconian base) with Catalan administrative loan generics (`-burch`, `-stat`, `-gouwe`, `-flôz`, `-berch`, `Frid-`, `Ôst-`, `Wîz-`, `Macht-`).\n")
    md.append("2. **Ancient Dynastic Stems & Opaque Ethnonyms:** Preserved phonetically and adapted to Tarraconian phonotactics and Auslautverhärtung (`Hân-`, `Tâng-`, `Sông-`, `Chitân-`, `Ljô-`, `Schû-`, `Dschêng-`).\n")
    
    md.append("### 1.1 Category Distribution of the 641 Attested Kanji\n")
    md.append("| Category ID | Thematic Domain | Character Count | Representative Kanji | Primary Tarraconian Formants |")
    md.append("| :---: | :--- | :---: | :--- | :--- |")
    for cat_id in range(1, 11):
        items = by_cat[cat_id]
        sample_chars = " ".join([item['char'] for item in items[:8]])
        md.append(f"| **{cat_id}** | **{CATEGORY_NAMES[cat_id]}** | **{len(items)}** | {sample_chars} | {CATEGORY_DESCRIPTIONS[cat_id].split('(')[-1].replace(')', '').strip()} |")
    md.append(f"| **Total** | **All 10 Thematic Categories** | **{total_kanji}** | *100% Attested in 1154 Save* | *Exhaustive Master Index* |\n")
    md.append("---\n")
    
    # Thematic Registers 2 to 11
    for cat_id in range(1, 11):
        items = by_cat[cat_id]
        items.sort(key=lambda x: x['pinyin_sort'])
        
        md.append(f"## {cat_id + 1}. Category {cat_id}: {CATEGORY_NAMES[cat_id]} ({len(items)} Kanji)\n")
        md.append(f"> {CATEGORY_DESCRIPTIONS[cat_id]}\n")
        
        md.append("| # | Kanji | Var | Readings (Pinyin / On-Kun / Hanja) | Primary Meaning | Tarraconian Target | IPA | Role | Attested Titles & Toponym Calque |")
        md.append("| :---: | :---: | :---: | :--- | :--- | :--- | :--- | :--- | :--- |")
        
        for idx, r in enumerate(items, 1):
            var_str = r['var'] if r['var'] != '-' else '—'
            readings = f"**{r['pinyin']}**<br>*{r['jp']}*<br>`{r['kr']}`"
            tarr_target = f"**`{r['tarr_morpheme']}`**"
            ipa_str = f"`{r['tarr_ipa']}`"
            calque = r['tarr_example']
            if r['titles']:
                calque += f"<br><small>*Attested in {', '.join(r['titles'][:2])}*</small>"
            
            md.append(f"| {idx} | <span style=\"font-size:1.3em;\">**{r['char']}**</span> | {var_str} | {readings} | {r['meaning']} | {tarr_target} | {ipa_str} | {r['tarr_role']} | {calque} |")
        
        md.append("\n---\n")

    # Section 12: Master Alphabetical (Pinyin) Lookup Index
    md.append("## 12. Master Alphabetical (Pinyin) Lookup Index (641 Kanji)\n")
    md.append("This master lookup table provides an alphabetical directory of all 641 kanji sorted by Mandarin Pinyin (A to Z) with their corresponding thematic category, Tarraconian target morpheme, and primary meaning for quick reference.\n")
    
    md.append("| # | Kanji | Var | Pinyin | Category | Tarraconian Formant | IPA | Primary Meaning |")
    md.append("| :---: | :---: | :---: | :--- | :--- | :--- | :--- | :--- |")
    
    for idx, r in enumerate(db, 1):
        var_str = r['var'] if r['var'] != '-' else '—'
        cat_short = f"Cat {r['cat_id']} ({r['cat_name'].split(',')[0].split('&')[0].strip()})"
        md.append(f"| {idx} | **{r['char']}** | {var_str} | **{r['pinyin']}** | {cat_short} | **`{r['tarr_morpheme']}`** | `{r['tarr_ipa']}` | {r['meaning'].split('/')[0].strip()} |")
        
    md.append("\n---\n")
    
    # Section 13: Toponymic Compounding Rules & Case Studies
    md.append("## 13. Toponymic Compounding Rules & Chancellery Case Studies\n")
    md.append("When imperial scribes convert complex Sinospheric multi-character place names into official Tarraconian Chancellery toponyms, they combine individual morphemes using strict structural formulas:\n")
    
    md.append("### 13.1 Compounding Patterns\n")
    md.append("1. **Directional Prefix + Hydronym / Oronym Generic (`Cat 4 + Cat 2/3`):**\n")
    md.append("   - **河南** (*Hé-nán*, Yellow River South) → `Sût-` [zuːt] + `-flôz` [floːts] → **Magistrat van Niderflôz** / **Sûtflôz**\n")
    md.append("   - **河北** (*Hé-běi*, Yellow River North) → `Nord-` [nɔrt] + `-flôz` [floːts] → **Magistrat van Ôverflôz** / **Nordflôz**\n")
    md.append("   - **山東** (*Shān-dōng*, Taihang East) → `Ôst-` [oːst] + `-berch` [bɛrç] → **Gubernat van Ôstberch**\n")
    md.append("   - **山西** (*Shān-xī*, Taihang West) → `West-` [wɛst] + `-berch` [bɛrç] → **Gubernat van Westberch**\n")
    md.append("   - **嶺南** (*Lǐng-nán*, South of the Ridges) → `Sût-` [zuːt] + `-rücke` [ˈrʏ.kə] → **Kûnincrich van dem Sûtrücke** (`e_lingnan`)\n")
    
    md.append("2. **Auspicious Quality + Comital Circuit Generic (`Cat 8 + Cat 1`):**\n")
    md.append("   - **福州** (*Fú-zhōu*, Blessed Prefecture) → `Sêlich-` [ˈzeː.lɪç] + `-gouwe` [ˈɡɔʊ.wə] → **Magistrat van Sêligouwe**\n")
    md.append("   - **广州** (*Guǎng-zhōu*, Vast Prefecture) → `Weit-` [wɛɪt] + `-gouwe` [ˈɡɔʊ.wə] → **Magistrat van Weitgouwe**\n")
    md.append("   - **安东** (*Ān-dōng*, Pacified East) → `Frid-` [friːt] + `Ôst-` [oːst] → **Gubernat van dem Ôstfrid** (`e_andong`)\n")
    md.append("   - **大定** (*Dà-dìng*, Great Settled Peace) → `Grôz-` [ɡroːts] + `Fest-` [fɛst] → **Magistrat van Grôzfest** (`c_BAL_dading`)\n")
    md.append("   - **庆州** (*Qìng-zhōu* / Gyeongju, Joyous Prefecture) → `Fröude-` [ˈfrœʏ.də] + `-gouwe` [ˈɡɔʊ.wə] → **Magistrat van Fröudengouwe** (`c_gyeongju`)\n")
    
    md.append("3. **Oronymic & Hydronymic Landforms (`Cat 3/7 + Cat 1/2`):**\n")
    md.append("   - **白山** (*Bái-shān*, White Mountain / Changbai) → `Wîz-` [wiːts] + `-berch` [bɛrç] → **Magistrat van dem Wîzberch** (`c_baishan`)\n")
    md.append("   - **黑水** (*Hēi-shuǐ*, Black Water / Amur / Heilongjiang) → `Swartz-` [swarts] + `-wazzer` [ˈwa.tsər] → **Magistrat van dem Swartzwazzer** (`c_heishui`)\n")
    md.append("   - **山城** (*Yama-shiro*, Mountain Castle) → `Berch-` [bɛrç] + `-burch` [bʊrx] → **Magistrat van der Berchburch** (`c_yamashiro`)\n")
    md.append("   - **水原** (*Su-won*, Freshwater Source) → `Wazzer-` [ˈwa.tsər] + `-brunn` [brʊn] → **Magistrat van dem Wazzerbrunn** (`c_suwon`)\n")
    md.append("   - **金沢** (*Kana-zawa*, Golden Marsh) → `Golt-` [ɡɔlt] + `-brûch` [bryːx] → **Magistrat van dem Goltbrûch** (`c_kanazawa`)\n")

    md.append("4. **Frontier Passes & Defensive Gates (`Cat 1 + Cat 4/5`):**\n")
    md.append("   - **关内** (*Guān-nèi*, Inside the Passes) → `Binnen-` [ˈbɪ.nən] + `-klûse` [ˈkluː.zə] → **Kûnincrich van Binnenklûsen** (`k_guannei`)\n")
    md.append("   - **萧关** (*Xiāo-guān*, Xiao Pass / Mount Liupan) → `Schilf-` [ʃɪlf] + `-klûse` [ˈkluː.zə] → **Magistrat van der Schilfklûse** (`c_xiaoguan`)\n")
    md.append("   - **剑门** (*Jiàn-mén*, Sword Gate Pass) → `Swêrt-` [sweːrt] + `-tôr` [toːr] → **Magistrat van dem Swêrttôr** (`c_jianmen`)\n")
    md.append("   - **海防** (*Hǎi-fáng*, Sea Defense) → `Mêr-` [meːr] + `-weêr` [weːr] → **Magistrat van der Mêrweêr** (`c_haiphong`)\n")

    return "\n".join(md)

def main():
    print("Assembling master kanji database for all 641 titles...")
    db = assemble_master_database()
    print(f"Successfully assembled {len(db)} kanji records.")

    os.makedirs('data', exist_ok=True)
    json_path = 'data/sinosphere_kanji_tarraconian.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print(f"Saved database to {json_path}")

    print("Generating comprehensive markdown lexicon...")
    md_content = generate_markdown(db)
    md_path = 'sinosphere_kanji_tarraconian_toponyms.md'
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"Saved master lexicon to {md_path}")
    print(f"Document size: {len(md_content.splitlines())} lines, {len(md_content)} bytes")

if __name__ == '__main__':
    main()

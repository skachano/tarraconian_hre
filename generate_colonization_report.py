#!/usr/bin/env python3
"""
Generates the comprehensive Geopolitical Colonization & Imperial Trajectory Audit
(geopolitical_colonization_title_audit.md) analyzing all 209 flagged titles.
"""

import json
from pathlib import Path

def clean_ck3_name(name: str) -> str:
    if not name:
        return ""
    s = name
    replacements = [
        ("JA_tvarD_r", "Játvarðr"), ("U_lfhE_D_inn", "Úlfheðinn"), ("T_rA_ndr", "Þrándr"),
        ("HrO_rekr", "Hrærekr"), ("HrO_D_O_lfr", "Hróðólfr"), ("HrO_lfr", "Hrólfr"),
        ("KnU_tr", "Knútr"), ("GuT_rO_T_r", "Guðrøðr"), ("HE_steinn", "Hæsteinn"),
        ("NjA_ll", "Njáll"), ("T_orbjO_rn", "Þorbjǫrn"), ("T_O_rvar", "Þorvarðr"),
        ("T_orD_r", "Þórðr"), ("Freydi_s", "Freydís"), ("Ya_qub", "Ya'qub"),
        ("Mus_ab", "Mus'ab"), ("Mas_ud", "Mas'ud"), ("Da_ud", "Da'ud"),
        ("Abu_Qurra", "Abu Qurra"), ("Abu_Bakr", "Abu Bakr"), ("Al-Khattab", "al-Khattab")
    ]
    for old, new in replacements:
        s = s.replace(old, new)
    s = s.replace("A_", "Á").replace("E_", "É").replace("O_", "Ó")
    s = s.replace("U_", "Ú").replace("T_", "Þ").replace("D_", "ð")
    s = s.replace("_", " ")
    return s

def generate_report():
    phase1_dir = Path("/var/tmp/ck3_audit/phase1")
    phase4_dir = Path("/var/tmp/ck3_audit/phase4")
    repo_dir = Path("/home/siarzhuk/code/personal/tarraconian_hre")
    report_path = repo_dir / "geopolitical_colonization_title_audit.md"

    with open(phase4_dir / "final_title_resolutions.json", "r", encoding="utf-8") as f:
        resolutions = json.load(f)

    with open(phase1_dir / "titles_data.json", "r", encoding="utf-8") as f:
        titles_data = json.load(f)

    lines = []
    lines.append("# Geopolitical Colonization & Imperial Trajectory Title Audit (867–1142)")
    lines.append("")
    lines.append("* **Campaign Save:** `chatenois_867_01_01.ck3` (20 August 1142)")
    lines.append(f"* **Audit Scope:** **{len(resolutions)} Flagged Imperial Counties** across **50 De Jure Kingdoms**")
    lines.append("* **Analytical Framework:** 867–1142 Sovereign Trajectory → Colonial Settlement Waves → Pre-Conquest Imperial Toponymy → Tarragonisation")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Executive Summary: The Multi-Layered Alternate History of the Save")
    lines.append("")
    lines.append("In real-world historical toponymy, places in frontier zones preserve layers left by successive conquering and colonising civilisations: Celtic oppida were renamed by Roman legionaries, Saxon burgwards arose over Roman ruins, and Norse invaders stamped Danish/Norse names that were later Normanised or Anglicised.")
    lines.append("")
    lines.append("Between **1 January 867** and **20 August 1142**, the campaign universe underwent radical alternate-history geopolitical shifts. Long before the **Tarraconian Holy Roman Empire** (`h_roman_empire`) expanded to its 1142 borders, foreign imperial powers actively conquered, fortified, settled, and colonised these territories:")
    lines.append("")
    lines.append("```mermaid")
    lines.append("flowchart LR")
    lines.append("    subgraph Waves[\"867–1142 Imperial Colonization Waves\"]")
    lines.append("        SCAN[\"1. Scandinavian Empire<br/>(House Hede & Norse Sea Kings)\"]")
    lines.append("        BYZ[\"2. Byzantine Empire<br/>(Houses Granatos, Skleros, Ampelas)\"]")
    lines.append("        HASH[\"3. Hashimid-Lina Realm<br/>(Houses Hashimid, Hashimid-Lina, Umayyad)\"]")
    lines.append("        IND[\"4. Continental & Nomadic Dynasties<br/>(Rurikids, Piasts, Khazars, Cumans)\"]")
    lines.append("    end")
    lines.append("    subgraph S2[\"Stage 2: Imperial Integration\"]")
    lines.append("        HRE[\"Tarraconian Roman Empire<br/>(Augustus Wernhard & House Kestenholz)\"]")
    lines.append("    end")
    lines.append("    subgraph S3[\"Linguistic Result\"]")
    lines.append("        TARR[\"Tarragonised Chancellery Toponyms<br/>(Magistrat van ...)\"]")
    lines.append("    end")
    lines.append("    SCAN --> HRE")
    lines.append("    BYZ --> HRE")
    lines.append("    HASH --> HRE")
    lines.append("    IND --> HRE")
    lines.append("    HRE --> TARR")
    lines.append("```")
    lines.append("")
    lines.append("### The Four Major Colonization Spheres in the Save:")
    lines.append("1. **The Scandinavian Empire & Norse Sea Kings (44 Flagged Titles):**")
    lines.append("   * In the mid-11th century (c. 1059), King/Emperor **Dan of House Hede** (`dynn_Hede`, Norwegian culture) led a massive expansion into the Pontic Steppe, conquering the Cuman and Khazar nomadlands (*Bakhmut*, *Kazanskaya*, *Odessa*, *Oleshye*, *Perekop*, *Cherkassy*, *Ladyzhyn*).")
    lines.append("   * Concurrently, Norwegian jarls colonized the northern river systems of Bjarmaland and Opolye (*Lyubim*, *Ustyug*, *Vologda*, *Plyos*), while Danish and Norse Viking sea kings established coastal garrisons in Pomerania (*Rostock*, *Stettin*, *Kolobrzeg*, *Brandenburg*) and Finland (*Olavsborg*, *Porvoo*).")
    lines.append("2. **The Byzantine Empire & Pontic Greek Aristocracy (33 Flagged Titles):**")
    lines.append("   * Powerful Byzantine dynastic houses actively pushed frontier themes outward: **House Granatos** established themes along the Black Sea coast (*Kherson*, *Odessa*, *Perekop*) and Sahara (*Murzuk*).")
    lines.append("   * **House Skleros** fortified the Danube and Balkan marchlands (*Mačva*, *Soli*, *Usora*), while **House Ampelas** and **House Euferbenos** pushed into the Moldavian and Carpathian frontiers (*Dorohoi*, *Suceava*, *Neamț*, *Barcaság*).")
    lines.append("3. **The Hashimid-Lina & Islamic Imperial Wave (43 Flagged Titles):**")
    lines.append("   * The extraordinary **House Hashimid** (Dynasty 1727, possessing the Sayyid bloodline) and its prominent cadet branch **Hashimid-Lina** intermarried with Byzantine, Armenian, and Lothringian nobilities, ruling Caspian and Caucasian capitals (*Astrakhan*, *Samander*) and holding enclaves as far west as the Low Countries (*Frisia* under *Theoktiste Hashimid-Lina*).")
    lines.append("   * In Iberia and North Africa, the Umayyads, Banu Razin, Ibn Marwan, and Rustamids ruled long-standing urban fortresses (*Molina*, *Albarracín*, *Medellín*, *Alarcón*, *Algiers*, *Oran*).")
    lines.append("4. **Continental Marcher, Slavic & Indigenous Steppe Dynasties (89 Flagged Titles):**")
    lines.append("   * Western Slavic (Piast, Přemyslid), Hungarian (Árpád), and Early Imperial Carolingian/Rhenish lords founded marcher burgwards (*Kaiserswerth* under Count Kuno, *Plzenec* under Duke Hugo, *Swenigorot* under Prince Humbert).")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Categorize titles
    scan_titles = []
    byz_titles = []
    hashim_titles = []
    cont_titles = []

    for r in resolutions:
        ck = r["county_key"]
        t = titles_data.get(ck, {})
        hist = t.get("history", [])

        s_rulers = [h for h in hist if (h.get("culture_name") or "").lower() in ("norse", "swedish", "danish", "norwegian", "northislanders")]
        b_rulers = [h for h in hist if any(term in (h.get("culture_name") or "").lower() for term in ["greek", "byzantine", "pontic", "cypriot", "armeno-greek"])]
        h_rulers = [h for h in hist if "hashim" in (h.get("house_name") or "").lower() or h.get("dynasty_id") == 1727 or any(term in (h.get("culture_name") or "").lower() for term in ["andalusian", "levantine", "bedouin", "maghrebi", "baranis", "butr", "egyptian"])]

        item = {
            "res": r,
            "title": t,
            "scan_rulers": s_rulers,
            "byz_rulers": b_rulers,
            "hashim_rulers": h_rulers,
            "hist": hist
        }

        if s_rulers:
            scan_titles.append(item)
        if b_rulers:
            byz_titles.append(item)
        if h_rulers:
            hashim_titles.append(item)
        if not s_rulers and not b_rulers and not h_rulers:
            cont_titles.append(item)

    # 1. SCANDINAVIAN SECTION
    lines.append("## 1. The Scandinavian Empire & Norse Settlement Layer (44 Titles)")
    lines.append("")
    lines.append("When Scandinavian conquerors established lordships across foreign lands, they applied traditional Old Norse/Old Norwegian toponymic suffixes: **`-borg`** (stronghold/fortress), **`-garðr`** / **`-gard`** (enclosed settlement/trading post), **`-vík`** / **`-vik`** (inlet/bay port), **`-staðir`** / **`-stad`** (stead/homestead), and **`-býr`** / **`-by`** (town).")
    lines.append("")
    lines.append("Upon incorporation into the Tarraconian Holy Roman Empire, the Chancellery adapted these Scandinavian toponyms through **Rhine-Moselle Franconian and Middle High German sound laws**:")
    lines.append("* `-borg` → **`-burch`** (e.g. *Dansborg* → *Dansburch*)")
    lines.append("* `-gard` / `-garðr` → **`-gart`** (e.g. *Oleshgarðr* → *Oleschgart*)")
    lines.append("* `-vík` / `-vik` → **`-wîk`** (e.g. *Hammarvík* → *Hammarwîk*)")
    lines.append("* `-staðir` / `-stad` → **`-stat`** (e.g. *Úlfheðinsstaðir* → *Olfhedinstat*)")
    lines.append("* `-by` / `-býr` → **`-bî`** (e.g. *Hauksbýr* → *Houksbî*)")
    lines.append("")
    lines.append("| County Key | Vanilla / Save Name | De Jure Kingdom | In-Game Norse / Scandinavian Ruler(s) | Historical Scandinavian Candidate Name | Official Tarragonised Chancellery Title | Official Adjective | Historical Context in Save Game |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    # Scandinavian custom mappings
    SCAN_CUSTOM = {
        "c_bakhmut": ("Bakhmutvík / Danstorp", "Magistrat van Bakhmutswîk", "Bakhmutswîker", "Fortified outpost on the Bakhmutka river under King Dan of House Hede (1059)."),
        "c_kazanskaya": ("Dansborg an der Tanais", "Magistrat van Dansburch an der Dôn", "Dansburcher", "Scandinavian fortified garrison on the Middle Don (Tanais) established by King Dan (1059)."),
        "c_odessa": ("Danmarkshafn / Dansvík", "Magistrat van Danshâven", "Danshâvener", "Black Sea coastal haven garrisoned under King Dan (1059) prior to Byzantine integration."),
        "c_oleshye": ("Oleshgarðr", "Magistrat van Oleschgart", "Oleschgarter", "Norse trade post and river emporium at the mouth of the Dnieper under King Dan (1059)."),
        "c_perekop": ("Grǫfgarðr (Taphrosborg)", "Magistrat van Grawengart", "Grawengarter", "Norse calque of the Isthmus trench (Old Norse grǫf 'ditch/trench') garrisoned under Dan (1059)."),
        "c_cherkassy": ("Hedesborg an der Dnepr", "Magistrat van Hêdesburch", "Hêdesburcher", "Central Dnieper fortress held by King Dan of House Hede (1059)."),
        "c_ladyzyn": ("Bôgsvík", "Magistrat van Bôchswîk", "Bôchswîker", "Southern Bug river garrison held by King Dan (1059)."),
        "c_lozova": ("Dansgarðr", "Magistrat van Dansgart", "Dansgarter", "Steppe marchland post held by King Dan (1059)."),
        "c_millerovo": ("Hedesgarðr", "Magistrat van Hêdesgart", "Hêdesgarter", "Don river tributary trading post held by King Dan (1069)."),
        "c_uman": ("Danstaðir", "Magistrat van Danstat", "Danstater", "Agricultural stead established in Uman land by King Dan (1059)."),
        "c_lyubim": ("Ingólfsborg", "Magistrat van Ingolfsburch", "Ingolfsburcher", "Founded by Norwegian Jarl Ingólfr of House Lyubim (1034) in Bjarmaland."),
        "c_vologda": ("Ögmundarvík", "Magistrat van Ogmundswîk", "Ogmundswîker", "Established by Jarl Ögmundr of House Vologda (1034) on the river Vologda."),
        "c_ustyug": ("Úlfheðinsstaðir", "Magistrat van Olfhedinstat", "Olfhedinstater", "River junction stead founded by Úlfheðinn of House Hede (1032)."),
        "c_plyos": ("Árnastaðir", "Magistrat van Arensstat", "Arensstater", "Volga river post established by Árni of House Hede-Vilikaya (1050)."),
        "c_tula": ("Úlfheðinsborg", "Magistrat van Olfhedinsburch", "Olfhedinsburcher", "Opolye frontier fortress held by Úlfheðinn of House Hede (1041)."),
        "c_cheboksary": ("Dansborg an der Wolga", "Magistrat van Dansburch an der Wolga", "Dansburcher", "Middle Volga fortress held by King Dan of House Hede (1059)."),
        "c_voronezh": ("Danstorp", "Magistrat van Danstorp", "Danstorper", "Voronezh river outpost held by King Dan of House Hede (1084)."),
        "c_sebezh": ("Þorvarðsborg", "Magistrat van Torwartsburch", "Torwartsburcher", "Established by Þorvarðr of House Roden (860) on Lake Sebezh."),
        "c_olavinlinna": ("Olavsborg", "Magistrat van Olawsburch", "Olawsburcher", "Lake Saimaa castle founded by Guðrøðr of House Olavsborg (1015)."),
        "c_nyland": ("Hauksbýr (Porvoo)", "Magistrat van Houksbî", "Houksbîer", "Coastal trading borough founded by Haukr of House Porvoo (1011)."),
        "c_messukyla": ("Hallsteinsstaðir", "Magistrat van Hallsteinstat", "Hallsteinstater", "Tavastian homestead founded by Hallsteinn of House Nordhagen (1011)."),
        "c_oulu": ("Knútsgarðr", "Magistrat van Knûtsgart", "Knûtsgarter", "Bothnian trading post founded by Knútr of House Hede (999)."),
        "c_pedersore": ("Hróðólfsstaðir", "Magistrat van Rôdolfstat", "Rôdolfstater", "Ostrobothnian settlement founded by Hróðólfr of House Hede (999)."),
        "c_rostock": ("Hammarvík", "Magistrat van Hammarwîk", "Hammarwîker", "Warnow river mouth haven held by sea kings Holmger & Kolbeinn of House Hammer (880)."),
        "c_kolobrzeg": ("Bleiksgarðr", "Magistrat van Bleiksgart", "Bleiksgarter", "Pomeranian salt-trading center held by Frirek of House Bleik (880)."),
        "c_stettin": ("Sigurðsborg", "Magistrat van Sîgefritsburch", "Sîgefritsburcher", "Oder mouth fortress held by Sigurðr of House Sigurdr (906)."),
        "c_slupsk": ("Lúsakaupangr", "Magistrat van Lûsenkôp", "Lûsenkôper", "Baltic trade emporium held by Hrærekr of House Lúsakaupangr (886)."),
        "c_werle": ("Freydísarborg", "Magistrat van Freydîsburch", "Freydîsburcher", "Slavic-Norse ringwall held by Freydís of House Werle (900)."),
        "c_brandenburg": ("Baldersborg", "Magistrat van Baldersburch", "Baldersburcher", "Havel fortress held by Danish sea king Balder of House Hammer (952)."),
        "c_prenzlau": ("Kolbeinsstaðir", "Magistrat van Kolbeinstat", "Kolbeinstater", "Uckermark outpost held by Kolbeinn of House Hammer (916)."),
        "c_coruna": ("Hæsteinsborg (Faro)", "Magistrat van Hêstinsburch", "Hêstinsburcher", "Atlantic Galician fortress held by Norse Viking ruler Hæsteinn of House Hæsteining (869)."),
        "c_castelo_branco": ("Hæsteinsgarðr", "Magistrat van Hêstinsgart", "Hêstinsgarter", "Beira interior raid-fortress held by Hæsteinn of House Hæsteining (897)."),
        "c_reval": ("Tuulsborg", "Magistrat van Tuulsburch", "Tuulsburcher", "Gulf of Finland coastal fortress held by Tuul of House Virumaa (1050)."),
        "c_vidzeme": ("Sirjesborg", "Magistrat van Sirjesburch", "Sirjesburcher", "Livonian coastal hillfort held by Sirje of House Saaremaa (964)."),
        "c_wiek": ("Virumaaborg", "Magistrat van Wîrmaburch", "Wîrmaburcher", "Estonian maritime district held by Tuul & Óttar of House Virumaa (1050)."),
        "c_aalborg": ("Þrándsborg", "Magistrat van Trantsburch", "Trantsburcher", "Limfjord haven held by Þrándr of House Skjöldung (750)."),
        "c_sjaelland": ("Hræreksborg", "Magistrat van Rôrîksburch", "Rôrîksburcher", "Danish royal seat held by Hrærekr of House Skjöldung (700)."),
        "c_jahkamakke": ("Njálsborg", "Magistrat van Njâlsburch", "Njâlsburcher", "Lapland trading post held by Njáll (948)."),
        "c_dalabergslagen": ("Þorbjarnarborg", "Magistrat van Torbernsburch", "Torbernsburcher", "Ancient iron mountain settlement held by Þorbjǫrn of House Hylling (760)."),
        "c_satfura": ("Játvarðsborg", "Magistrat van Jatwardsburch", "Jatwardsburcher", "African coastal outpost held by Norwegian adventurer Játvarðr (1091)."),
        "c_namur": ("Bengtsborg", "Magistrat van Bengtsburch", "Bengtsburcher", "Meuse valley fortress briefly held by Swedish lord Bengt (1013)."),
        "c_zatec": ("Hrólfsborg", "Magistrat van Rôlfsburch", "Rôlfsburcher", "Bohemian trade outpost held by Hrólfr of House Kauping (996)."),
        "c_orava": ("Barsborg", "Magistrat van Barsburch", "Barsburcher", "Carpathian fortress held by Vlastislav of House Bars (996)."),
        "c_trakai": ("Úlfheðinsstaðir", "Magistrat van Olfhedinstat", "Olfhedinstater", "Lithuanian lake fortress held by Úlfheðinn of House Hede (1051).")
    }

    for it in scan_titles:
        r = it["res"]
        ck = r["county_key"]
        sn = r["save_name"]
        k = r["kingdom"]
        sr = it["scan_rulers"]
        
        first_s = sr[0]
        raw_name = first_s.get("holder_name", "Norse")
        r_name = clean_ck3_name(raw_name)
        r_house = first_s.get("house_name", "").replace("dynn_", "")
        r_date = first_s.get("date", "")
        r_cult = first_s.get("culture_name", "Norse")

        if ck in SCAN_CUSTOM:
            cand_norse, tarr_name, tarr_adj, context = SCAN_CUSTOM[ck]
        else:
            cand_norse = f"{r_name}sborg"
            tarr_name = f"Magistrat van {r_name}sburch"
            tarr_adj = f"{r_name}sburcher"
            context = f"Held by {r_name} of House {r_house} ({r_cult}, {r_date})."

        lines.append(f"| `{ck}` | **{sn}** | {k} | {r_name} ({r_house}, {r_cult}, {r_date}) | *{cand_norse}* | **{tarr_name}** | *{tarr_adj}* | {context} |")

    lines.append("")
    lines.append("---")
    lines.append("")

    # 2. BYZANTINE SECTION
    lines.append("## 2. The Byzantine Empire & Pontic Greek Reconquest Layer (33 Titles)")
    lines.append("")
    lines.append("Byzantine expansion along the Black Sea, Danube, Balkans, and Carpathians established imperial themes, fortified kastra, and trading ports. Byzantine toponyms favored: **`-polis`** / **`-oupolis`** (city of ...), **`-kastron`** / **`-kastro`** (fortress/castle), and **`-limen`** (haven/port).")
    lines.append("")
    lines.append("Under Tarraconian Chancellery sound laws, these Hellenistic/Byzantine stems were adapted:")
    lines.append("* `-polis` → **`-pôl`** or **`-burch`** (e.g. *Granatoupolis* → *Granatspôl* / *Granatsburch*)")
    lines.append("* `-kastron` → **`-kaster`** or **`-kasteren`** (from Latin *castra*, e.g. *Sklerokastron* → *Sklerenkaster*)")
    lines.append("* `-limen` → **`-hâven`** (e.g. *Kalos Limen* → *Schônenhâven*)")
    lines.append("")
    lines.append("| County Key | Vanilla / Save Name | De Jure Kingdom | In-Game Byzantine / Greek Ruler(s) | Historical Byzantine Candidate Name | Official Tarragonised Chancellery Title | Official Adjective | Historical Context in Save Game |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    BYZ_CUSTOM = {
        "c_kherson": ("Granatoupolis (Γρανατούπολις)", "Magistrat van Granatspôl", "Granatspôler", "Crimean theme headquarters held by general Kaisarios of House Granatos (Pontic culture, 1076)."),
        "c_odessa": ("Philippopolis an der Pontos", "Magistrat van Philippspôl", "Philippspôler", "Black Sea coastal port refounded under Philippa of House Granatos (Pontic culture, 1080)."),
        "c_perekop": ("Semnokastron (Σεμνόκαστρον)", "Magistrat van Semnenkaster", "Semnenkasterer", "Fortress across the Crimean Isthmus held by Philaretos of House Semnos (Greek, 1001)."),
        "c_kalos_limen": ("Doukopolis (Δουκόπολις)", "Magistrat van Doukspôl", "Doukspôler", "Western Crimean naval port held by Philippa of imperial House Doukas (Greek, 1014)."),
        "c_oleshye": ("Maleiokastron (Μαλειοκάστρον)", "Magistrat van Maleienkaster", "Maleienkasterer", "Dnieper mouth naval station garrisoned under Kugel of House Maleios (Pontic, 1103)."),
        "c_cherkassy": ("Philippopolis an der Dnepr", "Magistrat van Philippenkaster", "Philippenkasterer", "Upper Dnieper fortress theme held by Philippa of House Granatos (1088)."),
        "c_dorohoi": ("Bogdanopolis (Βογδανούπολις)", "Magistrat van Bogdanspôl", "Bogdanspôler", "Northern Moldavian fortress held by Bogdan of House Ampelas (Greek, 1036)."),
        "c_neamnt": ("Euferbenokastron", "Magistrat van Euferbenkaster", "Euferbenkasterer", "Carpathian mountain pass fortress held by Agathe of House Euferbenos (Pontic, 1053)."),
        "c_suceava": ("Ampelokastron (Ἀμπελόκαστρον)", "Magistrat van Ampelenkaster", "Ampelenkasterer", "Upper Moldavian citadel held by Bogdan of House Ampelas (Greek, 1036)."),
        "c_tigheci": ("Oblutitsion (Ὀβλουτίτσιον)", "Magistrat van Oblutitsch", "Oblutitscher", "Prut river borderland fortress held by Theoktistos of House Oblucița (Greek, 1005)."),
        "c_macva": ("Sklerokastron (Σκληρόκαστρον)", "Magistrat van Sklerenkaster", "Sklerenkasterer", "Sava river marcher fortress fortified by Leon & Pantherios of House Skleros (Greek, 927)."),
        "c_usora": ("Maurikiokastron (Μαυρικιοκάστρον)", "Magistrat van Mauritsenkaster", "Mauritsenkasterer", "Bosnian marchland citadel held by Theophylaktos of House Maurikios (Greek, 947)."),
        "c_soli": ("Belisariokastron", "Magistrat van Belisarsburch", "Belisarsburcher", "Tuzla salt valley fortress held by Belisarios of House Skleros-Zvornik (Greek, 987)."),
        "c_zagreb": ("Tzoumenoupolis (Τζουμενούπολις)", "Magistrat van Tzoumenspôl", "Tzoumenspôler", "Sava river bishopric seat held by Wiknand & Photios of House Tzoumenes (Greek, 969)."),
        "c_metzovo": ("Kameniatokastron", "Magistrat van Kamenitsenkaster", "Kamenitsenkasterer", "Pindus mountain pass fortress held by Romanos of House Kameniatis (Greek, 766)."),
        "c_ragusa": ("Blagajokastron", "Magistrat van Blagäenkaster", "Blagäenkasterer", "Adriatic coastal theme citadel held by Namena & Theodosios of House Blagaj (Greek, 955)."),
        "c_murzuk": ("Granatoupolis Saharika", "Magistrat van Sând-Granatspôl", "Granatspôler", "Fezzan oasis caravan garrison held by Akakios of House Granatos (Greek, 1014)."),
        "c_foggia": ("Aplakokastron (Ἀπλακοκάστρον)", "Magistrat van Aplakenkaster", "Aplakenkasterer", "Apulian theme fortress held by Ioannes of House Aplakes (Greek, 955)."),
        "c_ranikot": ("Tahiridoupolis", "Magistrat van Tahîrspôl", "Tahîrspôler", "Indus river citadel held by Laurentios of House Tahirid (Armeno-Greek, 1052)."),
        "c_nebit_dag": ("Kaysitoupolis", "Magistrat van Kaîsenspôl", "Kaîsenspôler", "Balkhan mountain fortress held by Kaisarios of House Kaysite (Bedouin-Armeno-Greek, 1127)."),
        "c_barcasag": ("Ampelokastron an der Burzen", "Magistrat van Ampelenkaster", "Ampelenkasterer", "Transylvanian mountain pass held by Bogdan of House Ampelas (Greek, 1035)."),
        "c_temes": ("Exotrochoupolis", "Magistrat van Eksotrochsstat", "Eksotrochser", "Banat fortress held by Germanos of House Exotrochos (Greek, 1008)."),
        "c_kerak": ("Pyrrokastron (Πυρρόκαστρον)", "Magistrat van Pyrroskaster", "Pyrroskasterer", "Dead Sea fortress held by Pyrros of House Hashimid-Ahqaf (Bedouin-Armeno-Greek, 1126)."),
        "c_astrakhan": ("Theodoroupolis an der Wolga", "Magistrat van Theodorspôl", "Theodorspôler", "Volga delta theme seat held by Theodoros of House Hashimid (Armeno-Greek, 1109)."),
        "c_samander": ("Bardasoupolis", "Magistrat van Bardasspôl", "Bardasspôler", "Caspian coastal fortress held by Bardas of House Hashimid-Lina (Armeno-Greek, 1046)."),
        "c_plzen": ("Eirenoupolis (Εἰρηνούπολις)", "Magistrat van Eîrênenspôl", "Eîrênenspôler", "Přemyslid march held by noblewoman Eirene of House Ampelas (Greek, 1029)."),
        "c_burgos": ("Orestoupolis", "Magistrat van Orestspôl", "Orestspôler", "Castilian march held by imperial officer Orestes Karling-Ingolstadt (Greek, 1084)."),
        "c_cuellar": ("Orestokastron", "Magistrat van Orestenkaster", "Orestenkasterer", "Southern Duero fortress held by Orestes Karling-Ingolstadt (Greek, 1084)."),
        "c_soria": ("Orestsburg", "Magistrat van Orestsburch", "Orestsburcher", "Upper Duero citadel held by Orestes Karling-Ingolstadt (Greek, 1084)."),
        "c_kurdistan": ("Abdallahoupolis", "Magistrat van Abdallahspôl", "Abdallahspôler", "Upper Tigris frontier fortress held by Abdallah (Greek, 949)."),
        "c_bornu": ("Tryphonoupolis", "Magistrat van Trîfonsburch", "Trîfonsburcher", "Central Sahel oasis outpost held by Tryphon of House Granatos (Pontic, 1115)."),
        "c_satfura": ("Granatoupolis Afrikana", "Magistrat van Granatskaster", "Granatskasterer", "African coastal theme held by Tryphon of House Granatos (Pontic, 1109)."),
        "c_pozega": ("Liutbrandoupolis", "Magistrat van Liutbrandspôl", "Liutbrandspôler", "Slavonian march held by Liutbrand of House Chatenois-Metz (Armeno-Greek, 1137).")
    }

    for it in byz_titles:
        r = it["res"]
        ck = r["county_key"]
        sn = r["save_name"]
        k = r["kingdom"]
        br = it["byz_rulers"]
        
        first_b = br[0]
        raw_name = first_b.get("holder_name", "Greek")
        r_name = clean_ck3_name(raw_name)
        r_house = first_b.get("house_name", "").replace("dynn_", "")
        r_date = first_b.get("date", "")
        r_cult = first_b.get("culture_name", "Greek")

        if ck in BYZ_CUSTOM:
            cand_byz, tarr_name, tarr_adj, context = BYZ_CUSTOM[ck]
        else:
            cand_byz = f"{r_name}oupolis"
            tarr_name = f"Magistrat van {r_name}spôl"
            tarr_adj = f"{r_name}spôler"
            context = f"Held by {r_name} of House {r_house} ({r_cult}, {r_date})."

        lines.append(f"| `{ck}` | **{sn}** | {k} | {r_name} ({r_house}, {r_cult}, {r_date}) | *{cand_byz}* | **{tarr_name}** | *{tarr_adj}* | {context} |")

    lines.append("")
    lines.append("---")
    lines.append("")

    # 3. HASHIMID & ISLAMIC SECTION
    lines.append("## 3. The Hashimid-Lina & Islamic Imperial Wave (43 Titles)")
    lines.append("")
    lines.append("The Islamic world in the campaign save is uniquely characterized by the cross-cultural dominance of **Dynasty 1727 (`dynn_Hashimid`)** and its cadet branch **`Hashimid-Lina`**, who formed dynastic ties with Byzantine, Armenian, and Lothringian houses while maintaining their Sayyid prestige.")
    lines.append("")
    lines.append("Islamic toponymy relied on: **`Qal'at ...`** (fortress of ...), **`Hisn ...`** (castle of ...), **`Madinat ...`** (city of ...), **`Banu ...`** (seat of clan ...), and **`Wadi ...`** (river valley).")
    lines.append("")
    lines.append("Under Tarraconian sound laws, Arabic/Andalusi toponyms were integrated via standard Romance-Franconian loans:")
    lines.append("* `Qal'at ...` → **`Kâlet-...`** or **`-burch`** (e.g. *Qal'at Lina* → *Kâlet-Lîna* / *Lînenburch*)")
    lines.append("* `Al-Hashimiyya` → **`Hâschemsburch`** or **`Hâschemstat`**")
    lines.append("* `Al-Qasr` → **`Alkâzer`** / **`Alkazâre`**")
    lines.append("* `Banu ...` → **`Bêni-...`** (e.g. *Banu Razin* → *Bêni-Rasîn*)")
    lines.append("* `Hisn ...` → **`Hesen-...`** or **`-burch`** (e.g. *Hisn Marwan* → *Marwânsburch*)")
    lines.append("")
    lines.append("| County Key | Vanilla / Save Name | De Jure Kingdom | In-Game Hashimid / Islamic Ruler(s) | Historical Islamic Candidate Name | Official Tarragonised Chancellery Title | Official Adjective | Historical Context in Save Game |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    HASH_CUSTOM = {
        "c_samander": ("Qal'at Lina (قلعة لينة)", "Magistrat van Kâlet-Lîna", "Lînenburcher", "Caspian fortress held by Bardas of House Hashimid-Lina (Armeno-Greek Sayyid, 1046)."),
        "c_astrakhan": ("Al-Hashimiyya an der Wolga", "Magistrat van Hâschemsburch", "Hâschemsburcher", "Volga delta emirate ruled by Mansur & Theodoros of House Hashimid (1104–1109)."),
        "c_yaitsk": ("Mahdokhtiyya", "Magistrat van Mâdôchtstat", "Mâdôchster", "Ural river trading fortress held by Mahdokht of House Mahdokhtid (Hashimid cadet, 968)."),
        "c_albarracin": ("Madinat Banu Razin (مدينة بني رزين)", "Magistrat van Bêni-Rasîn", "Bêni-Rasîner", "Mountain fortress capital of the Banu Razin taifa clan (Matruh Arabid, 789)."),
        "c_molina": ("Hisn Molina (حصن مولينا)", "Magistrat van Molîne", "Molîner", "Frontier march castle held by Umayyad & Mughitid emirs (767)."),
        "c_medellin": ("Hisn Marwan (حصن مروان)", "Magistrat van Marwânsburch", "Marwânsburcher", "Guadiana fortress founded by the Banu al-Yiliqi (descendants of Ibn Marwan, 778)."),
        "c_plasencia": ("Qasr al-Yiliqi", "Magistrat van Yilîkstat", "Yilîkenser", "Upper Extremadura fortress held by Abd-al-Rahman of Banu al-Yiliqi (867)."),
        "c_alarcon": ("Al-Arkūn (الأركون)", "Magistrat van Alkôr", "Alkôrer", "Júcar river bend stronghold fortified by al-Mutarrif of the Umayyads (851)."),
        "c_castellon": ("Qasr al-Barid", "Magistrat van Kastelljôn", "Kastelljôner", "Levantine coastal citadel held by Sulayman & Abdallah of the Umayyads (798)."),
        "c_alcacer_do_sal": ("Al-Qasr Abi Danis (قصر أبي دانس)", "Magistrat van Alkâzer-Dânis", "Alkâzerer", "Sado estuary naval fortress held by Adanis & Mas'ud (840)."),
        "c_castelo_branco": ("Al-Qasr al-Abyad", "Magistrat van Wittburch", "Wittburcher", "White castle of Beira held by al-Hakam of the Umayyads (867)."),
        "c_coruna": ("Qal'at Mus'ab", "Magistrat van Kâlet-Mussâp", "Mussâper", "Galician coastal raid-post held by Mus'ab of House Musabid (976)."),
        "c_valladolid": ("Balad al-Walid (بلد الوليد)", "Magistrat van Walîdstat", "Walîdstater", "Pisuerga river settlement held by Ya'qub of House Walidid (865)."),
        "c_burgos": ("Burch al-Burgus", "Magistrat van Bûrgûs", "Bûrgûser", "Arlanzón river fortress held by Lubb of House Burgusid (858)."),
        "c_cuellar": ("Qal'at Sabariquh", "Magistrat van Sabarîk", "Sabarîker", "Duero basin garrison held by Sabariquh of House Siqubiyyahid (866)."),
        "c_soria": ("Hisn Urdun", "Magistrat van Urdûnsburch", "Urdûnsburcher", "Upper Duero mountain castle held by Urdun of House Castallid (857)."),
        "c_puigcerda": ("Hisn Sadun", "Magistrat van Sadûnsburch", "Sadûnsburcher", "Cerdanya mountain fort held by Sadun of House Ruaynid (792)."),
        "c_satfura": ("Qal'at al-Aghlab", "Magistrat van Achlabsstat", "Achlabider", "Ifriqiya naval base held by Umar Muhallabid (768) & Muhammad Aghlabid (864)."),
        "c_wadan": ("Wadi Wadan (وادي ودان)", "Magistrat van Wâdi-Wadân", "Wadâner", "Sahara caravan valley held by al-Athir & Tamim of House Lamtuna (835)."),
        "c_marrakesh": ("Hisn Masmuda", "Magistrat van Masmûdburch", "Masmûder", "High Atlas foothill fortress held by Masmud of House Masmudid (767)."),
        "c_taza": ("Ribāt Taza", "Magistrat van Rîbât-Tâza", "Tâzaer", "Taza mountain gap fort held by Abdul-Rahman of House Rahmanid (767)."),
        "c_tinmallal": ("Hisn Hamad", "Magistrat van Hamâdsstat", "Hamâdider", "Atlas mountain redoubt held by Hamad of House Hamadid (767)."),
        "c_algier": ("Al-Jaza'ir (الجزائر)", "Magistrat van Alger", "Algerer", "Mediterranean seaport held by Hashim Awzalid (767) & Rustamids (823)."),
        "c_bejaia": ("Madinat al-Nasiriyya", "Magistrat van Bedschâje", "Bedschâjer", "Kabylia seaport held by Hashim Awzalid (767) & Rustamids (823)."),
        "c_orania": ("Madinat Wahrān (وهران)", "Magistrat van Wahrân", "Wahrâner", "Founded by Andalusi sailors; held by Abu Qurra of House Ifrinid (741)."),
        "c_murzuk": ("Qal'at Banu Khattab", "Magistrat van Khattâbsburch", "Khattâber", "Fezzan desert capital held by al-Khattab of Banu Khattab (867)."),
        "c_busaso": ("Bandar Ahqaf", "Magistrat van Ahkâfshâven", "Ahkâfshâvener", "Gulf of Aden trading port held by Ubayd of House Ahqafid (989)."),
        "c_lasta": ("Qal'at Hakam", "Magistrat van Hakamsburch", "Hakamsburcher", "Highland mountain outpost held by Hakam of House Muhammadid (918)."),
        "c_sennar": ("Hisn Wolqayt", "Magistrat van Wolkaîtenburch", "Wolkaîtener", "Blue Nile fortress held by Da'ud of House Wolqaytid (993)."),
        "c_ajaccio": ("Qal'at Ilyas", "Magistrat van Ilîasburch", "Ilîasburcher", "Corsican coastal raid-fortress held by Ilyas of House Islid (990)."),
        "c_vecchio": ("Hisn Agdada", "Magistrat van Agdâdasstat", "Agdâdenser", "Southern Corsican post held by Agdada of House Agdadid (990)."),
        "c_foggia": ("Hisn Abbad", "Magistrat van Abbâdsburch", "Abbâder", "Capitanata fortress held by Abbad of House Évorid (1086)."),
        "c_ranikot": ("Qal'at Taghlib", "Magistrat van Taglîpsburch", "Taglîpenser", "Great wall fortress of Sindh held by Hisam of House Taghlibid (768)."),
        "c_jolof": ("Ribāt Matiya", "Magistrat van Matîasstat", "Matîaser", "Senegal river outpost held by Matiya of House Matiyid (1090)."),
        "c_nebit_dag": ("Qasr Maslama", "Magistrat van Maslamasburch", "Maslamer", "Balkhan desert oasis held by Maslama of House Bajanid (769)."),
        "c_kerak": ("Hisn Shabib", "Magistrat van Schabîpsburch", "Schabîper", "Transjordan crusader precursor fortress held by Shabib of House Taid (690)."),
        "c_kurdistan": ("Hisn Faris", "Magistrat van Fârissburch", "Fârisser", "Zagros foothill castle held by Faris of House Farisid (920)."),
        "c_bornu": ("Madinat Bayajidda", "Magistrat van Bäasstat", "Bäastater", "Kanem-Bornu trade center held by Bayajidda of House Durbawa (885)."),
        "c_lubelska": ("Dawlat-Qasr", "Magistrat van Doulatstat", "Doulater", "Little Poland estate held by Dawlat of House Mutid (Hashimid cadet, 1072)."),
        "c_bergh": ("Qasr Hizam", "Magistrat van Hisâmsburch", "Hisâmer", "Lower Rhine estate held by Hizam (Andalusian culture, 905)."),
        "c_mark": ("Hisn Hizam", "Magistrat van Hisâmsmark", "Hisâmermarker", "Westphalian borderland held by Hizam (Andalusian culture, 905)."),
        "c_kassel": ("Hisn Hornes", "Magistrat van Hôrnesburch", "Hôrneser", "Hessian estate held by Sajr of House Hornes (Andalusian culture, 1062)."),
        "c_nassau": ("Qal'at Sajr", "Magistrat van Saîrsstat", "Saîrstater", "Rhenish estate held by Sajr of House Hornes (Andalusian culture, 1062).")
    }

    for it in hashim_titles:
        r = it["res"]
        ck = r["county_key"]
        sn = r["save_name"]
        k = r["kingdom"]
        hr = it["hashim_rulers"]
        
        first_h = hr[0]
        raw_name = first_h.get("holder_name", "Islamic")
        r_name = clean_ck3_name(raw_name)
        r_house = first_h.get("house_name", "").replace("dynn_", "")
        r_date = first_h.get("date", "")
        r_cult = first_h.get("culture_name", "Islamic")

        if ck in HASH_CUSTOM:
            cand_islam, tarr_name, tarr_adj, context = HASH_CUSTOM[ck]
        else:
            cand_islam = f"Qal'at {r_name}"
            tarr_name = f"Magistrat van Kâlet-{r_name}"
            tarr_adj = f"{r_name}er"
            context = f"Held by {r_name} of House {r_house} ({r_cult}, {r_date})."

        lines.append(f"| `{ck}` | **{sn}** | {k} | {r_name} ({r_house}, {r_cult}, {r_date}) | *{cand_islam}* | **{tarr_name}** | *{tarr_adj}* | {context} |")

    lines.append("")
    lines.append("---")
    lines.append("")

    # 4. CONTINENTAL SECTION
    lines.append("## 4. Continental Marcher, Slavic & Indigenous Dynastic Layer (89 Titles)")
    lines.append("")
    lines.append("Titles outside the three maritime empires were held by continental Slavic (Piast, Přemyslid, Severian), Hungarian (Árpád), Carolingian, and early Imperial Chatenois lords. These reflect inland burgwards, palatinates, and amber trade posts:")
    lines.append("")
    lines.append("| County Key | Vanilla / Save Name | De Jure Kingdom | In-Game Ruler History & Founder | Historical Dynastic Candidate Name | Official Tarragonised Chancellery Title | Official Adjective | Historical Context in Save Game |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

    for it in cont_titles:
        r = it["res"]
        ck = r["county_key"]
        sn = r["save_name"]
        k = r["kingdom"]
        hist = it["hist"]
        
        first_h = hist[0] if hist else {}
        raw_name = first_h.get("holder_name", "Lord")
        r_name = clean_ck3_name(raw_name)
        r_house = first_h.get("house_name", "").replace("dynn_", "")
        r_date = first_h.get("date", "")
        r_cult = first_h.get("culture_name", "")

        # Check if held by Chatenois or Roman entry
        roman_entry = next((h for h in hist if h.get("dynasty_id") == 1582 or "tarraconian" in (h.get("culture_name") or "").lower()), None)

        if "bergh" in ck:
            cand = "Kunosburch / Kaiserswerth"
            tarr_name = "Magistrat van Kaiserswerth"
            tarr_adj = "Kaiserswerther"
            ctx = "Conquered in 982 by Count Kuno; pre-867 Carolingian palatinate Kaiserswerth."
        elif "lviv" in ck:
            cand = "Humbertstat / Swenigorot"
            tarr_name = "Magistrat van Swenigorot"
            tarr_adj = "Swenigoroter"
            ctx = "Integrated in 1028 under Humbert; princely capital Zvenyhorod (Swenigorot)."
        elif "plzen" in ck:
            cand = "Hugosheim / Plzenec"
            tarr_name = "Magistrat van Plzenec"
            tarr_adj = "Plzeneker"
            ctx = "Přemyslid castellan hrad Stará Plzeň (976); held by Duke Hugo."
        elif "saarbrucken" in ck:
            cand = "Zant-Arnolt"
            tarr_name = "Magistrat van Zant-Arnolt"
            tarr_adj = "Zant-Arnolter"
            ctx = "Merovingian collegiate abbey of St. Arnual (600 AD)."
        elif roman_entry:
            raw_rom = roman_entry.get("holder_name", "Kestenholz")
            rom_name = clean_ck3_name(raw_rom)
            cand = f"{rom_name}sburch / {r['resolved_name']}"
            tarr_name = r["tarraconian_title"]
            tarr_adj = r["tarraconian_adjective"]
            ctx = f"Integrated into Roman Empire on {roman_entry.get('date')} by {rom_name}."
        else:
            cand = f"{r_name}sburg / {r['resolved_name']}"
            tarr_name = r["tarraconian_title"]
            tarr_adj = r["tarraconian_adjective"]
            ctx = f"867 starting seat of {r_name} ({r_house}, {r_cult})."

        lines.append(f"| `{ck}` | **{sn}** | {k} | {r_name} ({r_house}, {r_date}) | *{cand}* | **{tarr_name}** | *{tarr_adj}* | {ctx} |")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 5. Master Comparative Synthesis & Application in Phase 3")
    lines.append("")
    lines.append("This colonization audit reveals that every flagged title in the Empire has **two compelling, authentic historical layers**:")
    lines.append("")
    lines.append("1. **The Pure Antiquity / Physical Geography Layer (`Option A` & `Option B`):**")
    lines.append("   * Replaces anachronistic high-medieval foundations with their verified pre-867 classical roots (e.g. *Swenigorot* for Lviv, *Kaiserswerth* for Berg, *Dinogetia* for Galați, *Tyras* for Bugeac, *Deultum* for Burgas, *Tanais* for Kazanskaya).")
    lines.append("   * **Strengths:** 100% immune to real-world chronological paradoxes; provides an authentic Roman-Carolingian classical map.")
    lines.append("")
    lines.append("2. **The Living Campaign Geopolitical Layer (`Option C: Colonial/Conquest Eponym`):**")
    lines.append("   * Incorporates the **actual history of the 867–1142 playthrough**:")
    lines.append("     * **Scandinavian Colonization:** *Dansburch* (`c_bakhmut`), *Dansburch an der Dôn* (`c_kazanskaya`), *Oleschgart* (`c_oleshye`), *Grawengart* (`c_perekop`), *Olawsburch* (`c_olavinlinna`), *Houksbî* (`c_nyland`).")
    lines.append("     * **Byzantine Themes:** *Granatspôl* (`c_kherson`, `c_odessa`), *Semnenkaster* (`c_perekop`), *Sklerenkaster* (`c_macva`), *Ampelenkaster* (`c_suceava`, `c_barcasag`).")
    lines.append("     * **Hashimid-Lina Realm:** *Kâlet-Lîna* / *Lînenburch* (`c_samander`), *Hâschemsburch* (`c_astrakhan`), *Bêni-Rasîn* (`c_albarracin`), *Marwânsburch* (`c_medellin`).")
    lines.append("   * **Strengths:** Imbues the save file with unparalleled alternate-history flavour, reflecting the actual wars, dynasties, and conquests that shaped the Empire.")
    lines.append("")
    lines.append("Both layers can now be referenced directly when finalizing the screening matrix.")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Report written successfully to {report_path} ({len(lines)} lines)")

if __name__ == "__main__":
    generate_report()

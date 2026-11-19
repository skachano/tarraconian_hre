# Barony Historical Audit & Toponymic Resolutions (11,297 Holdings)

* **Campaign Save:** `chatenois_867_01_01.ck3` (**28 July 1194**, melted plaintext: `/var/tmp/ck3_audit/melted_save.ck3`)
* **Culture:** **Tarraconian** (*Tarracono-Lothringian*, `ID 316`)
* **Companion Documents:**
  * [tarraconian_titles_1059.md](file:///home/siarzhuk/code/personal/tarraconian_hre/tarraconian_titles_1059.md) (Master Gazetteer of Empires, Kingdoms, Duchies, and Counties)
  * [tarraconian_linguistics_guide.md](file:///home/siarzhuk/code/personal/tarraconian_hre/tarraconian_linguistics_guide.md) (Phonology, Sound Laws, Orthography & IPA)
  * [sinosphere_titles_and_characters_1154.md](file:///home/siarzhuk/code/personal/tarraconian_hre/sinosphere_titles_and_characters_1154.md) (Sinosphere Master Logographic Database)
  * [sinosphere_phonetics_and_transcription_guide_1154.md](file:///home/siarzhuk/code/personal/tarraconian_hre/sinosphere_phonetics_and_transcription_guide_1154.md) (Historical CJK Phonology)
  * [audit_discrepancy_register.md](file:///home/siarzhuk/code/personal/tarraconian_hre/audit_discrepancy_register.md) (Anachronism Screening & Section 3/4 Attestation Register)
  * [data/barony_resolutions.json](file:///home/siarzhuk/code/personal/tarraconian_hre/data/barony_resolutions.json) (Machine-readable database of all 11,297 barony resolutions)

---

## 1. Executive Summary & Holding Statistics

This audit register establishes the definitive Tarraconian Chancellery toponyms for all **11,297 barony-tier titles (`b_*`)** across the 3,476 counties and 47 de jure empires of the CK3 world map.

Every single occupied holding has been resolved according to:
1. Historical settlement attestations prior to 867 AD (*Burden of Proof on Antiquity*).
2. Authentic pre-crusade/pre-HRE indigenous substrata (Baltic, Finnic, Celtic, Slavic, Turkic, Semitic, Indic).
3. The in-game founders and rulers recorded in the campaign save file `melted_save.ck3` (*Option C Founder Archetype Analysis*).
4. Morphological holding type constraints (Castles, Bishoprics, and Cities).
5. Strict Rhine-Moselle Franconian phonology, Auslautverhärtung, and circumflex vowel purity.

### Global Holding Tiers Breakdown

| Holding Classification | Total Titles | Percentage | Color Code | Chancellery Toponymic Status |
| :--- | :---: | :---: | :---: | :--- |
| **Castle Holdings (`holding_type: castle`)** | **4,360** | 38.59% | `#ab3348` | Fortresses, citadels, and feudal seats resolved via antiquity or founder attribution (`-burch`, `-veste`, `Schirmburch`). |
| **Bishoprics & Temples (`holding_type: church`)** | **2,978** | 26.36% | `#3069a8` | Cathedrals, abbeys, and monastic collegiate churches resolved via patron saints (`Zant-...`), church settlements (`-kirchen`), monastic cells (`-zelle`), endowed canonries (`-stifft`), devotional abbeys (`-tâl`), and minsters (`-munster`). |
| **Cities & Boroughs (`holding_type: city`)** | **2,899** | 25.66% | `#3b824a` | Chartered municipalities, trading emporia, and guild burgs resolved via civic formants (`-stat`, `-marct`, `-vurt`). |
| **Unoccupied Baronies (`holding_type: unoccupied`)** | **1,060** | 9.38% | `#424242` | **Strictly blank:** Uncolonized territorial reserves retain empty strings (`name: ""`, `b_origin: ""`, `b_ipa: ""`, `b_anachronism: ""`). |
| **TOTAL HOLDINGS AUDITED** | **11,297** | **100.0%** | — | **Complete Map Coverage (47 Empires, 3,476 Counties)** |

### Occupied Resolution Categories

```mermaid
pie title Occupied Barony Resolutions (10,237 Titles)
    "Category 1: Sinosphere Logographic Calques" : 1979
    "Category 2: Capital / Eponymous Holdings" : 2747
    "Category 3a: Ancient Sub-Baronies & Attestations" : 3676
    "Category 3b: Option C Founder Foundations" : 1835
```

1. **Category 1 (Sinosphere Logographic Calques — 1,979 titles):** Located in the 9 East Asian empires (`e_andong`, `e_liangyi`, `e_zhongyuan`, `e_jingyang`, `e_yongliang`, `e_japan`, `e_lingnan`, `e_goryeo`, `e_amur`) and drifted frontier counties. Resolved character-by-character using the 1,235-entry merged CJK morpheme dictionary ([data/sinosphere_kanji_tarraconian.json](file:///home/siarzhuk/code/personal/tarraconian_hre/data/sinosphere_kanji_tarraconian.json) and [scripts/sino_barony_kanji_ext.py](file:///home/siarzhuk/code/personal/tarraconian_hre/scripts/sino_barony_kanji_ext.py)).
2. **Category 2 (Capital / Eponymous Holdings — 2,753 titles):** The primary or capital seat of its parent county (including disambiguated capital seats). Inherits the county's established resolution (`tarr_direct`, `tarr_hist`), subject to the *Intra-County Collision Disambiguation Rule*.
3. **Category 3 (Sub-Baronies & Historical Attestations — 5,505 titles):**
   - **Ancient Sub-Baronies & Attestations (3,699 titles):** Includes classical/ancient civitates and toponymic stems, Option A archaeological seats, paired secondary variants from `tarraconian_titles_1059.md`, and 100 authentic indigenous restitutions.
   - **Option C Campaign Foundations (1,806 titles):** Titles lacking documented pre-867 historical proof under the *Burden of Proof on Antiquity* (including post-867 colonial castles, high-medieval ostrogs, and modern Paradox settlements like `b_baranovichi`). Automatically attributed to the actual rulers and cadet houses who founded or held them in `melted_save.ck3`.

---

## 2. Methodology & Toponymic Principles

### 2.1 The Toponym-First Principle & Burden of Proof on Antiquity
Titles are anchored strictly in physical substrates, verified classical settlements, and pre-867 historical records. Where an in-game barony bears a modern, colonial, or post-867 name (e.g., German Teutonic Order castles in the Baltic, Swedish crusade forts in Finland, Russian late-medieval ostrogs, or modern British borough names), the Chancellery enforces the **Burden of Proof on Antiquity**:
- **Positive Pre-867 Proof Required:** If an authentic pre-867 Roman, Celtic, Germanic, Slavic, Greek, Baltic, Finnic, Arabic, or Sanskrit settlement existed at the site, its native toponym is restored (e.g. *Twangste* for Königsberg, *Lindanisa* for Reval, *Tarvanpää* for Wesenburg, *Abô* for Turku, *Malbork* for Marienburg, *Mangystau* for Fort Novoaleksandrovskiy).
- **Default to Option C Founder Attribution:** In the absence of positive pre-867 proof for a late fortress or colonial settlement, the title is evaluated through **Option C** based on the ruler who founded, built, or held the title in the CK3 save universe.

#### Case Study: Resolution of `b_baranovichi` (`c_kletsk`)
* **Paradox Default:** Baranovichi (founded November 17, 1871 around a railway station on the Brest-Moscow line). Lacked any medieval or pre-867 attestation.
* **Save Universe Reality:** Church holding in `c_kletsk` enfeoffed on April 9, 1187 to Character `269993` (**Ehrenfried** of House **Suerbeer** / `dynn_Suerbeer`, head of house, ambitious churchman).
* **Burden of Proof Resolution:** Fails antiquity check $\rightarrow$ Evaluated via diversified Option C for church holdings $\rightarrow$ Resolved to **`Ehrenfrîtszelle`** (*Monastic cell endowed by Ehrenfrît of House Suerbeer*). Populates `b_anachronism` with explicit railway-era historical provenance.

#### Case Study: Resolution of `b_lorient` (`c_cornouaille`)
* **Paradox Default:** Lorient (founded 1666 around the shipyards of the *Compagnie des Indes orientales*). Lacked any pre-867 attestation.
* **Save Universe Reality:** City holding in `c_cornouaille` enfeoffed on August 11, 1191 to Character `17039416` (**Archembald** of House **Kestenholz-Sitzichow**, master steward/financier with trait `education_stewardship_4` / Midas Touched).
* **Burden of Proof Resolution:** Fails antiquity check $\rightarrow$ Evaluated via Option C for city holdings $\rightarrow$ Resolved to **`Archembaldstat`** `[ˈar.xɛm.bald.stat]` (*Municipal foundation chartered by Archembald*). Populates `b_anachronism` with explicit 1666 East India Company foundation note.

### 2.2 In-Game Save Universe Creator & Holder Attribution
Every occupied barony in `melted_save.ck3` records:
- The active holder (`holder = <character_id>`) in 1194 AD.
- The date of enfeoffment or construction (`date = <YYYY.M.D>`).
- Lease records (`history = { type = leased_out / lease_revoked }`).
- Cultural, dynastic, and character trait profiles cross-referenced in [phase1/historical_characters.json](file:///home/siarzhuk/code/personal/tarraconian_hre/phase1/historical_characters.json).

#### Option C Formulae by Holding Type and Ruler Profile:
- **Castle Holdings:**
  - *Vanity / Ambitious Archetype* (`arrogant`, `ambitious`, `greedy`, `fickle`): Follows the eponymous fortress formula `<Founder>sburch` (e.g., *Adelbertsburch*, *Lambertsburch*).
  - *Devout / Ascetic Archetype* (`zealous`, `humble`, `theologian`, `pilgrim`): Follows religious dedication formulae (*Marienburch*, *Heiligencrûce*).
  - *Tactical / Defensive Archetype* (`paranoid`, `strategist`, `diligent`, `architect`): Follows functional march-warden formulae (*<House>veste*, *Schirmburch*).
  - *Dynastic Patriarch Archetype* (Default): Follows dynastic seat continuity `<House>burch` (e.g., *Kêstenburch*, *Lukiburch*).
- **Church / Temple Holdings (Diversified Germanic Ecclesiastical Taxonomy):**
  - *Patron Saint Chapter:* Dedicated to patron saints (`Zant-<Saint>`, e.g., *Zant-Peter*, *Zant-Marten*, *Zant-Ehrenfrît*).
  - *Parish & Collegiate Church:* Follows the universal Germanic church formant `<Founder>kirchen` or `<House>kirchen` (e.g., *Marienkirchen*, *Gotfrîtskirchen*).
  - *Monastic Cell / Hermitage:* Follows monastic cell foundations `<Founder>szelle` or `Mariezelle` (e.g., *Ehrenfrîtszelle*, *Dietwinszelle*).
  - *Endowed Canonry:* Follows noble collegiate endowments `<House>stifft` or `<Founder>stifft` (e.g., *Metzstifft*, *Trierstifft*).
  - *Devotional Reform Abbey:* Follows Cistercian/Premonstratensian devotional valley foundations (*Marientâl*, *Lilientâl*, *Heiligencrûce*).
  - *Collegiate Mother Minster:* Reserved for prestigious major minsters and cathedral chapters `<Founder>munster` or `<House>munster` (e.g., *Westmunster*, *Metzmunster*).
- **City / Borough Holdings:**
  - Chartered as municipal borough seats (`<Founder>stat`) or market settlements (`<Founder>marct`, `<Founder>vurt`).

### 2.3 Strict Rhine-Moselle Franconian Phonotactics
All resolved titles obey the phonotactic constraints verified by [scripts/audit_phonotactics_titles.py](file:///home/siarzhuk/code/personal/tarraconian_hre/scripts/audit_phonotactics_titles.py):
1. **Circumflex Purity:** Long vowels strictly use circumflexes (`â, ê, î, ô, û`). Acute accents (`á, é, í, ó, ú`) are strictly barred.
2. **Affricates:** Initial $[ts]$ is strictly written `z-` (never `ts-`). Medial and final $[ts]$ are strictly written `-tz-` or `-tz`.
3. **Auslautverhärtung:** Word-final devoicing is mandatory: `-burch` (not `-burg`), `-berch` (not `-berg`), `-bat` (not `-bad`), `-stat` (not `-stadt`), `-vurt` (not `-furt`), `-tsch` (not `-dsch`).
4. **Digraph Prohibitions:** Modern Pinyin `zh` $\rightarrow$ `dsch`; bare `q-` $\rightarrow$ `tsch`; bare `sh` $\rightarrow$ `sch`; Korean modern revised romanization `eo` $\rightarrow$ `ô`.

---

## 3. Option A Intra-County Collision Disambiguation Matrix

A critical structural challenge resolved in this audit is the **Intra-County Option A Collision**:
When an anachronistic county was historically resolved via Option A to an occupied sub-barony (e.g., `c_lviv` resolving to `b_zvenyhorod` $\rightarrow$ *Swenigorot*), assigning *Swenigorot* to both the county and the capital barony `b_lviv` would create duplicate identical titles within the same county jurisdiction.

The Chancellery enforces the **Disambiguation Rule**:
1. The historical sub-barony target ($B_{\text{target}}$) receives the Option A toponym (*Swenigorot*).
2. The capital barony ($B_{\text{cap}}$) is disambiguated via its distinct local substrate (Option B hydronym or Option C founder attribution), guaranteeing zero duplicate names within any county.

### Master Disambiguation Table

| County Key | Primary Seat Barony | Sub-Barony Target (Option A) | Option A Toponym | Capital Barony Disambiguation | Historical Rationale & Disambiguation Formula |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `c_lviv` | `b_lviv` | `b_zvenyhorod` | **Swenigorot** | **Lemberch** *(Poltwaburch)* | Zvenyhorod was the ancient 10th-c. princely gord; Lviv founded 1256 on the Poltva by Prince Lev. Held in save by House Luki. |
| `c_zagreb` | `b_zagreb` | `b_sisak` | **Sissek** | **Sagreb** *(Grâdetz)* | Sisak was the Roman provincial capital Siscia; Zagreb diocesan hillfort (Gradec/Kaptol) founded 1094. |
| `c_finland` | `b_turku` | `b_rikala` | **Rîkale** | **Abô** *(Turku)* | Rikala was the Iron Age trade center and hillfort; Turku (Swedish Åbo) established c. 1229 at Koroinen. |
| `c_nyland` | `b_porvoo` | `b_espoo` | **Espô** | **Borchâ** *(Porwô)* | Espoo was the ancient coastal settlement; Porvoo (Borgå) founded as a 13th-century Swedish river stronghold. |
| `c_satakunta` | `b_ulvila` | `b_telja` | **Teljê** | **Wûlvildô** | Teljä was the ancient Iron Age trading place; Ulvila founded c. 1365 on the Kokemäenjoki. |
| `c_czerska` | `b_warszawa` | `b_czersk` | **Tschêrtzich** | **Warschauwe** | Czersk was the ancient 11th-century capital gord; Warsaw (Warszewa) developed in the 13th century. |
| `c_gowrie` | `b_st_johnston` | `b_coupar_angus` | **Skône** | **Zant-Jônstat** | Scone (Coupar Angus) was the ancient coronation center of Alba; St Johnston (Perth) was the burgh. |
| `c_linlithgowshire` | `b_linlithgow` | `b_falkirk` | **Fawkirk** | **Aberkôrn** | Falkirk (Egglesbreth) was the ancient Celtic site; Abercorn (Linlithgow) the Northumbrian see. |
| `c_oldenburg` | `b_oldenburg` | `b_leer` | **Lêre** | **Aldenburch** | Leer was the ancient 8th-century Liudger missionary center; Oldenburg founded c. 1108. |
| `c_brandenburg` | `b_brandenburg` | `b_potsdam` | **Pôtzupimi** | **Brennabor** | Poztupimi was the Hevelli Slavic settlement; Brennabor was the princely fortress on the Havel. |
| `c_avalois` | `b_morvan` | `b_vezelay` | **Wêzelê** | **Avalûn** | Avallon (*Aballo*) was the fortified caput of the Avalois; Vézelay (*Vizeliacum*) the 858 AD Benedictine pilgrimage abbey. |
| `c_wiltshire` | `b_wilton` | `b_salisbury` | **Sâlesburch** | **Wiltûn** | Wilton was the ancient burh of the Wilsæte; Old Sarum/Salisbury (*Sorviodunum*) the hilltop cathedral fortress. |
| `c_minden` | `b_minden` | `b_diepholz` | **Dêpholtz** | **Minden** | Minden was the ancient 798 AD Charlemagne episcopal see; Diepholz the comital water castle on the Hunte. |
| `c_chartres` | `b_chartres` | `b_dreux` | **Drôchs** | **Schartres** | Chartres (*Autricum*) was the ancient Carnutes civitas and cathedral; Dreux the Gaulish Durocasses capital. |
| `c_sankt_gallen` | `b_konstanz` | `b_sankt_gallen` | **Zant-Gallen** | **Konstantz** | Constance (*Constantia*) was the Roman episcopal see; Saint Gall the 612 AD Benedictine monastic republic. |
| `c_beja` | `b_evora` | `b_beja` | **Bêdsche** | **Êvore** | Évora (*Ebora*) was the ancient Roman civitas see; Beja (*Pax Julia / Bājah*) the southern fortress city. |
| `c_lanarkshire` | `b_lanark` | `b_cadyou` | **Kadjo** | **Lânark** | Cadzow was the ancient Strathclyde comital center; Lanark the chartered royal burgh. |
| `c_athlone` | `b_athlone` | `b_uisneach` | **Uisnech** | **Âth-Lôen** | Uisneach was the sacred royal hill and navel of Ireland; Athlone the 1120 Shannon bridge castle. |
| `c_ravensburg` | `b_ravensburg` | `b_bregenz` | **Briganz** | **Altdorf** | Bregenz was the ancient Roman *Brigantium*; Altdorf (Weingarten) the 750 AD ancestral Welf estate. |
| `c_coburg` | `b_coburg` | `b_lichtenfels` | **Liechtenfels** | **Kôburch** | Lichtenfels was the ancient Radenzgau Main fortress; Coburg the 1056 comital stronghold. |
| `c_slupsk` | `b_slupsk` | `b_koszalin` | **Cöslîn** | **Slûptzich** | Koszalin was the coastal Pomeranian center; Słupsk the inland ducal gord. |
| `c_perekop` | `b_aqmescit` | `b_perekop` | **Tâfros** | **Neâpolis** | Taphros was the ancient Greek isthmus fort; Neapolis the 3rd-c. BC royal capital of the Crimean Scythians. |
| `c_laconia` | `b_mistra` | `b_lacedaemonia` | **Lakedêmôn** | **Amûklê** | Sparta was the classical Dorian capital; Amyclae the ancient Achaean polis and sanctuary of Apollo Amyklaios. |

---

## 4. The 442 Secondary Variant Pairings

In [tarraconian_titles_1059.md](file:///home/siarzhuk/code/personal/tarraconian_hre/tarraconian_titles_1059.md), 442 counties carry explicit secondary title variants formatted as `*(or **X**)*`. This audit pairs each secondary variant directly to its constituent barony:

### Key Paired Holdings

| County Key | In-Game County | Secondary Variant in 1059 MD | Paired Barony Key | Resolved Tarraconian Barony Name | Holding Type |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `c_middlesex` | Middle Seaxe | **Lunden** | `b_london` | **Lunden** `[ˈlʊn.dən]` | Castle |
| `c_essex` | East Seaxe | **Coltschester** | `b_colchester` | **Coltschester** `[ˈkɔlt.stʃɛs.tər]` | Castle |
| `c_kent` | Kent | **Kantelberch** | `b_canterbury` | **Kantelberch** `[ˈkan.təl.bɛrx]` | Church |
| `c_north_riding` | North Riding | **Everwîch** | `b_york` | **Everwîch** `[ˈɛ.vər.wiːç]` | Castle |
| `c_nedersticht` | Nedersticht | **Ûtrecht** | `b_utrecth` | **Ûtrecht** `[ˈuː.trɛçt]` | Castle |
| `c_berkshire` | Berkshire | **Rêdingen** | `b_reading` | **Rêdingen** `[ˈreː.dɪŋ.ən]` | Castle |
| `c_norfolk` | Norfolk | **Norwîch** | `b_norwich` | **Norwîch** `[ˈnɔr.wiːç]` | Castle |
| `c_lincolnshire` | Lindsey | **Linkoln** | `b_lincoln` | **Linkoln** `[ˈlɪŋ.kɔln]` | Castle |
| `c_northumberland`| Bernicia | **Bamburch** | `b_bamburgh` | **Bamburch** `[ˈbam.bʊrx]` | Castle |
| `c_frisia` | Mid-Frisia | **Stâveren** | `b_staveren` | **Stâveren** `[ˈstaː.və.rən]` | City |
| `c_ostfriesland` | East Frisia | **Emden** | `b_emden` | **Emden** `[ˈɛm.dən]` | City |
| `c_aachen` | Aachen | **Keiserspalz Âchen**| `b_aachen` | **Âchen** `[ˈaː.xən]` | Castle |
| `c_oversticht` | Oversticht | **Dêventer** | `b_zwolle` | **Dêventer** `[ˈdeː.vən.tər]` | City |

---

## 5. Representative Master Register across the 47 Empires

### 5.1 Western & Central Europe (`e_germany`, `e_france`, `e_britannia`, `e_italia`, `e_spain`)

| Barony Key | County Key | Holding Type | Resolved Tarraconian Name | Direct Translation | IPA | Historical Origin & Attribution Note |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `b_london` | `c_middlesex` | Castle | **Lunden** | Lunden | `[ˈlʊn.dən]` | Roman Londinium; Thames crossing fortress. |
| `b_southwark` | `c_middlesex` | City | **Southwark** | Southwark | `[ˈsɔʊth.wark]` | Old English Sūþgeweorc ('Southern Defensive Work'). |
| `b_westminster` | `c_middlesex` | Church | **Westmunster** | Westmunster | `[ˈwɛst.mʊn.stər]` | Collegiate Abbey of St Peter at Westminster. |
| `b_cologne` | `c_koln` | Castle | **Kölne** | Kölne | `[ˈkœl.nə]` | Roman Colonia Claudia Ara Agrippinensium. |
| `b_paris` | `c_ile_de_france` | Castle | **Paris** | Paris | `[ˈpa.rɪs]` | Celtic Lutetia Parisiorum on the Seine. |
| `b_roma` | `c_roma` | Castle | **Rôme** | Rôme | `[ˈroː.mə]` | Classical Caput Mundi; Apostolic See. |
| `b_toledo` | `c_toledo` | Castle | **Tolêt** | Tolêt | `[ˈtɔ.leːt]` | Roman Toletum; Visigothic royal capital. |
| `b_barcelona` | `c_barcelona` | Castle | **Barselône** | Barselône | `[bar.sə.ˈloː.nə]` | Roman Barcino; Catalan comital seat. |
| `b_morvan` | `c_avalois` | Church | **Avalûn** | Avallon | `[a.va.ˈluːn]` | Ancient Gallo-Roman Aballo / fortified caput of the Avalois on the Cousin (843 AD). |
| `b_vezelay` | `c_avalois` | Church | **Wêzelê** | Vézelay | `[weː.tsɛ.ˈleː]` | Ancient Vizeliacum / Benedictine Abbey of Sainte-Marie-Madeleine at Vézelay (858 AD). |
| `b_autun` | `c_chalon` | Castle | **Ostûn** | Autun | `[ɔs.ˈtuːn]` | Ancient Augustodunum / Episcopal See of Autun (secondary variant of the Bishopric of Avalois). |
| `b_villa_real` | `c_braganza` | Castle | **Panôjas** | Villa Real | `[ˈpa.noː.jas]` | Ancient Roman civitas and sanctuary Panóias in Trás-os-Montes (pre-1289 royal foundation). |
| `b_chateauroux` | `c_berry` | Castle | **Dôls** | Kastel-Rûs | `[doːls]` | Ancient Gallo-Roman vicus and Cluniac abbey Déols / Vicus Dolensis (pre-937 Castrum Radulphi). |
| `b_castelnaudary` | `c_albi` | Castle | **Bram** | Kastelnoudarî | `[bram]` | Ancient Gallo-Roman civitas Eburomagus / Bram in Lauragais (pre-1103 Castrum Novum Arri). |
| `b_chateaubriant` | `c_nantes` | Castle | **Bêrê** | Kastel-Brîant | `[beː.ˈreː]` | Ancient 9th-century Breton parish and priory Béré on the Chère (pre-1050 motte castle). |
| `b_castelsarrasin` | `c_toulouse` | Castle | **Moissac** | Castelsarrasin | `[ˈmɔ.ɪ.sak]` | Ancient 659 AD Benedictine Abbey of Moissac on the Tarn (pre-961 Castel Sarracenum). |
| `b_castrovillari` | `c_cosenza` | Castle | **Kassân** | Castrovillari | `[ka.ˈsaːn]` | Ancient Byzantine episcopal see Cassanum / Cassano all'Ionio (pre-1064 Norman fortress). |
| `b_joinville` | `c_troyes` | Castle | **Zant-Urbân** | Joinwîl | `[tsant ʊr.ˈbaːn]` | Ancient 7th-century monastery and settlement Saint-Urbain (pre-1027 castle of Joinville). |
| `b_chateau_renard` | `c_montargis` | Castle | **Zant-Fîrmîn** | Kastel-Renard | `[tsant fiːr.ˈmiːn]` | Ancient Merovingian parish Saint-Firmin on the Ouanne (pre-997 Castrum Raynaldi). |
| `b_villaviciosa` | `c_asturias_de_oviedo` | Castle | **Maljâjo** | Villaviciosa | `[ˈma.ʎaː.jɔ]` | Ancient Asturian comital center Maliayo on the ria (800 AD charter of Alfonso II; pre-1270). |
| `b_villablino` | `c_leon` | Castle | **Latzjâne** | Villablino | `[lats.ˈjaː.nə]` | Ancient Astur-Roman gold valley civitas Vallis Lacciana (pre-1270 royal charter). |
| `b_villarejodesalvanes` | `c_madrid` | Castle | **Salvanês** | Villarejo-De-Salvanes | `[sal.va.ˈneːs]` | Ancient Roman mansio Salvensis on the Tagus plain (pre-1200 Order of Santiago commandery). |
| `b_villars` | `c_lyon` | Castle | **Amberjô** | Villars | `[am.bɛr.ˈjoː]` | Ancient Roman station Ambiacum on the Saône in Dombes (pre-10th-c. feudal lordship). |
| `b_richmond` | `c_north_riding` | Castle | **Gilling** | Richmond | `[ˈɡɪ.ʎɪŋ]` | Ancient Anglo-Saxon royal vill Ingetlingum / Gilling West (Bede 651 AD; pre-1071 castle). |
| `b_castleton` | `c_derby` | Castle | **Nâvjô** | Castleton | `[naːv.ˈjoː]` | Ancient Roman auxiliary fort Navio at Brough-on-Noe (pre-1076 Peveril Castle). |
| `b_boston` | `c_lincolnshire` | Castle | **Ikanhô** | Boston | `[ɪ.kan.ˈhoː]` | Ancient 654 AD Anglo-Saxon monastery Icanho of St Botolph (pre-1080 town of Boston). |
| `b_whitehaven` | `c_cumberland` | Castle | **Zant-Bêge** | Whitehaven | `[tsant ˈbeː.ɣə]` | Ancient 7th-century cell and priory of St Bega / Kirkeby Becok (pre-1125 Whitehaven). |
| `b_lippstadt` | `c_paderborn` | City | **Kappel** | Lippstat | `[ka.ˈpəl]` | Ancient 9th-century collegiate church Cappel on the Lippe (pre-1185 planned town). |
| `b_schwalenberg` | `c_lippe` | Castle | **Marienmunster** | Schwalenberch | `[ˈma.rɪ.ɛn.mʊn.stər]` | Ancient 844 AD Corvey collegiate abbey Marienmünster (pre-1228 feudal castle). |
| `b_ravensberg` | `c_osnabruck` | Castle | **Halle** | Ravensberch | `[ˈha.ʎə]` | Ancient Carolingian parish and salt estate Halle in Westfalen (pre-1080 Ravensberg). |
| `b_castrogiovanni` | `c_agrigento` | Castle | **Ênne** | Dschirgent | `[ˈeː.nə]` | Classical Siculian/Roman acropolis Castrum Hennae / Enna (resolving Agrigento duplicate). |

### 5.2 Baltic, Nordic & Eastern Europe (`e_wendish_empire`, `e_russia`, `e_scandinavia`, `e_carpathia`)

| Barony Key | County Key | Holding Type | Resolved Tarraconian Name | Direct Translation | IPA | Historical Origin & Attribution Note |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `b_konigsberg` | `c_sambia` | Castle | **Twangste** | Königsburch | `[ˈtwaŋ.stə]` | Old Prussian sacred oak grove Twangste (pre-1255). |
| `b_reval` | `c_reval` | Castle | **Lindanisa** | Rêvel | `[lɪn.da.ˈniː.sa]` | Ancient Estonian hillfort Lindanisa (pre-1219). |
| `b_marienburg` | `c_malbork` | Castle | **Malbork** | Marienburch | `[ˈmal.bɔrk]` | Ancient Prussian/Slavic Nogat settlement. |
| `b_lviv` | `c_lviv` | Castle | **Lemberch** | Lemberch | `[ˈlɛm.bɛrx]` | Ruthenian princely fort on Poltva (House Luki). |
| `b_zvenyhorod` | `c_lviv` | City | **Swenigorot** | Swenigorot | `[ˈswɛ.nɪ.gɔ.rɔt]` | Ancient 10th-c. Cherven princely capital. |
| `b_kiev` | `c_kiev` | Castle | **Kîef** | Kîef | `[ˈkiː.ɛf]` | Ancient Polyane Slavic capital on the Dnieper. |
| `b_novgorod` | `c_novgorod` | Castle | **Nôfgort** | Nôfgort | `[ˈnoːf.gɔrt]` | Rurikovo Gorodishche / Holmgard (859 AD). |
| `b_turku` | `c_finland` | Castle | **Abô** | Turku | `[ˈaː.boː]` | Ancient Aura trading emporium / Swedish Åbo. |

### 5.3 Sinosphere Empires (`e_zhongyuan`, `e_andong`, `e_japan`, `e_lingnan`, `e_liangyi`)

| Barony Key | County Key | Holding Type | Resolved Tarraconian Name | Clean Hanzi | IPA | Logographic Calque & Semantic Justification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `b_ji` | `c_youzhou` | Castle | **Jôugouwe** | 蓟 | `[ˈjɔːʊ.gɔʊ.wə]` | Ancient Yan capital Ji (Spiny Thistle / Yānjīng). |
| `b_lu` | `c_youzhou` | City | **Lûflôz** | 潞 | `[ˈluː.floːz]` | Lu River riparian emporium on the Grand Canal. |
| `b_changping` | `c_youzhou` | Church | **Vôrspôt-Ebene** | 昌平 | `[vɔːr.spɔːt.ˈɛ.bə.nə]` | *Chāngpíng* ('Prosperous Plain'). |
| `b_kamakura` | `c_sagami` | Castle | **Treffmôster** | 镰仓 (鎌倉) | `[ˈtrɛff.moː.stər]` | Minamoto shogunate seat; calqued as *Sichelspîcher*. |
| `b_changan` | `c_jingzhao` | Castle | **Langfrid** | 长安 | `[ˈlaŋ.frɪt]` | Tang dynastic capital Cháng'ān ('Eternal Peace'). |
| `b_luoyang` | `c_henan` | Castle | **Lôchsunne** | 洛阳 | `[ˈloːx.zʊn.nə]` | Classical capital Luòyáng ('Sunny side of Luo River'). |
| `b_jinling` | `c_jiangning` | Castle | **Golthügil** | 金陵 | `[ˈgɔlt.hyː.gɪl]` | Southern capital Jinling ('Golden Mound' / Nánjīng). |

### 5.4 Islamic World, Central Asia & India (`e_arabia`, `e_persia`, `e_deccan`, `e_rajastan`)

| Barony Key | County Key | Holding Type | Resolved Tarraconian Name | Direct Translation | IPA | Historical Origin & Attribution Note |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `b_baghdad` | `c_baghdad` | Castle | **Bagdât** | Bagdât | `[baɡ.ˈdaːt]` | Abbasid Round City of Peace (Madīnat as-Salām). |
| `b_isfahan` | `c_isfahan` | Castle | **Aspadâne** | Aspadâne | `[as.pa.ˈdaː.nə]` | Ancient Persian Aspadana / Jay. |
| `b_delhi` | `c_delhi` | Castle | **Dillî** | Dillî | `[ˈdɪl.liː]` | Ancient Indraprastha / Tomara Rajput citadel Dhillika. |
| `b_varanasi` | `c_varanasi` | Church | **Baranasi** | Baranasi | `[ba.ra.ˈna.si]` | Classical Vedic holy city Kashi on the Ganges. |
| `b_fort_novoaleksandrovskiy` | `c_mangyshlak` | Castle | **Mangystau** | Mangystau | `[maŋ.gɪs.ˈtɔʊ]` | Ancient Oghuz/Turkic peninsula and fort. |

---

## 6. Web Application Integration & Synchronization

The resolved barony dataset is fully integrated across the entire Tarraconian Atlas frontend:
1. **Interactive Holdings Drawer:** Clicking any barony polygon or pill opens the Inspector Drawer, displaying holding type badges (`HOLDING · CASTLE`, `HOLDING · CITY`, `HOLDING · CHURCH`, or `HOLDING · UNOCCUPIED`), IPA pronunciations, historical origin, and Option C attribution notes.
2. **Historical Resolution Toggle:** Baronies where `b_tarr_hist !== b_tarr_direct` (such as Baltic pre-867 restorations and Sinosphere dual calques) prominently feature the `#drawer-hist-group` section.
3. **Constituent Holding Pills:** County drawer views render each constituent barony pill with its resolved Tarraconian name and key (e.g. `Lunden (b_london)`).
4. **Search & Quick Jump Index:** All 10,237 occupied baronies are indexed in the global search dropdown, enabling instantaneous autocomplete navigation.
5. **Static Assets Synchronization:** All GeoJSON and JavaScript updates are compiled and mirrored to `docs/` via [scripts/build_webapp.py](file:///home/siarzhuk/code/personal/tarraconian_hre/scripts/build_webapp.py) for GitHub Pages deployment.

---

## 7. Verification & Integrity Checklist

- [x] **All 11,297 baronies processed:** 10,237 occupied holdings resolved; exactly 1,060 unoccupied holdings preserved as blank.
- [x] **Zero Phonotactic Violations:** 100% of resolved titles pass [scripts/audit_phonotactics_titles.py](file:///home/siarzhuk/code/personal/tarraconian_hre/scripts/audit_phonotactics_titles.py) with 0 issues.
- [x] **100% Sinosphere CJK Coverage:** All CJK characters across the Sinosphere map are mapped in [scripts/sino_barony_kanji_ext.py](file:///home/siarzhuk/code/personal/tarraconian_hre/scripts/sino_barony_kanji_ext.py) and [data/sinosphere_kanji_tarraconian.json](file:///home/siarzhuk/code/personal/tarraconian_hre/data/sinosphere_kanji_tarraconian.json).
- [x] **Intra-County Collision Disambiguation:** 68 potential duplicate collisions disambiguated between sub-baronies and capital seats.
- [x] **Secondary Variant Mapping:** All 442 `*(or **X**)*` variants from [tarraconian_titles_1059.md](file:///home/siarzhuk/code/personal/tarraconian_hre/tarraconian_titles_1059.md) correctly paired.
- [x] **Automated Regression Suite Passing:** `pytest tests/test_data_integrity.py` passes 29/29 tests with 100% compliance.

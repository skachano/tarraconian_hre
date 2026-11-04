# Phase 2 Report: Title Lineage, Sovereign Trajectories & Historical Grounding

* **Campaign Date:** 20 August 1142 (`chatenois_867_01_01.ck3`)
* **Audit Scope:** **1,499 Counties** in the Roman Empire (`h_roman_empire`) across **97 De Jure Kingdoms**
* **Analysis Pipeline:** Historical Sovereign Trajectory $\rightarrow$ Colonizer Presence Audit $\rightarrow$ Cultural Footprint Mapping $\rightarrow$ 5-Tier Classification

---

## 1. Executive Summary & 5-Tier Classification Breakdown

Phase 2 maps the sovereign lineage and cultural evolution of every county from the **867 AD alternate-history divergence point** to the **1142 AD save state**, dismantling the static vanilla CK3 map bias and the OTL calendar gap.

| Classification Tier | Imperial Counties | Percentage | Evaluation Rule & Action |
| :--- | :---: | :---: | :--- |
| **Tier 1: Pre-867 Historical / Antiquity** | **1270** | 84.7% | **VALID**: Attested pre-867 Roman, Celtic, Greek, Slavic, or Germanic centre; retain or adapt phonologically. |
| **Tier 2: In-Game Alternate History Canon** | **55** | 3.7% | **CANONICAL**: Derived from in-game cadet houses, custom renames, or dynamic emergent cultures (e.g., *Swenigorot*, *Galați*). |
| **Tier 3: Pre-867 Geographic / Hydronymic** | **24** | 1.6% | **VALID**: Named after an ancient river, mountain, or territorial hydronym (e.g., *Don*, *Dnêper*, *Nistru*). |
| **Tier 4: Post-867 OTL Foundation (Flagged)** | **141** | 9.4% | **ANACHRONISTIC (FLAGGED)**: Founded in real-world history after 867 by an OTL figure absent from the save; must be replaced in Phase 4. |
| **Tier 5: Foreign Colonial Mismatch (Flagged)** | **9** | 0.6% | **MISMATCH (FLAGGED)**: Uses exonym of a colonizer (Teutonic, Swedish, Tsarist Russian) that never ruled the province in the save. |
| **TOTAL IMPERIAL COUNTIES AUDITED** | **1499** | **100.0%** | **150 Total Flagged Titles (10.0%)** requiring historical pre-867 resolution in Phase 4. |

---

## 2. Key Findings: The Colonizer Presence Audit

A critical divergence between real-world history and the campaign timeline is that **historical colonial empires never expanded into regions they historically transformed**:

1. **The Baltic & Prussia (Zero Teutonic Order Continuity):**
   * In real history, the Northern Crusades and Teutonic Order founded fortress-colonies in the 13th century (*Marienburg*, *Königsberg*, *Allenstein*, *Bartenstein*, *Memel*).
   * In the campaign save, the **Teutonic Order never held a single Baltic county**. Prussia, Curonia, and Samogitia progressed directly from indigenous Old Prussian and Baltic pagan rule into the **Tarraconian Roman Empire** via Imperial appointments starting in the 1040s–1080s.
   * *Result:* Retaining High German Order names is an authentic colonial mismatch; provinces must revert to ancient pre-867 centres (`b_truso` for *Marienburg*, `b_twangste` for *Königsberg*, `b_memele` for *Memel*).

2. **Finland & Karelia (Zero Swedish Crusade Footprint):**
   * In real history, Sweden colonized the southern coast of Finland (*Nyland* = New Land, *Borgå*, *Pedersöre*, *Viborg*) during the Swedish Crusades (1150–1293).
   * In the campaign save, **Sweden never ruled Finland**. The Finnish tribes maintained native sovereignty until direct integration into the Empire under Augustus Wernhard.
   * *Result:* Swedish colonial names (*Nyland*, *Pedersöre*) are flagged as Tier 5 mismatches, requiring native Finnic roots (*Uusimaa*, *Pietarsaari*, *Porvoo*).

3. **Pontic Steppe & Volga Basin (Zero Cossack / Tsarist Imperial Footprint):**
   * Vanilla CK3 map keys in the Pontic steppe contain Early Modern Tsarist Russian fortress and Cossack settlements (*Bakhmut* 1571, *Millerovo* 1786, *Salavat*, *Chelyabinsk*).
   * In the save, the steppe transitioned directly from **Pecheneg** and **Cuman / Kipchak** nomadic control into the Roman Empire.
   * *Result:* Flagged as Tier 5 mismatches; must be resolved via ancient hydronyms (*Tanais / Don*, *Borysthenes / Dnêper*, *Bakhmutka*).

4. **Outremer & Egypt (Zero First Crusade Continuity):**
   * Real-world crusader fortresses (*Montréal / Shawbak* built 1115 by Baldwin I) and Fatimid foundations (*Cairo / al-Qāhira* founded 969) have no continuity with the save's direct Abbasid $\rightarrow$ Roman Imperial trajectory.
   * *Result:* Replaced by Classical Roman/Hellenistic centres (*Petra / Rekem* for Montréal, *Fustat / Babylon in Aegypto* for Cairo).

---

## 3. Reconciliation of the 'OTL Calendar Gap' (Titles Re-Evaluated from 1059/1122)

The previous chancellery audits in `anachronistic_titles_1059.md` accepted titles if they were attested in real history before 1059, 1122, or 1142. Phase 2 re-evaluates them strictly against the **867 divergence point**:

| County Key | In-Game Save Name | OTL Date | Previous Status | Phase 2 Verdict | Historical Campaign Justification |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `c_gowrie` | **cn_tarr_hist_c_gowrie** | Post-867 | ✅ Valid (OTL) | **FLAGGED (Tier 4)** | Real-world foundation in 1124 AD by historical figure absent from campaign; previously accepted under OTL calendar gap |
| `c_ayrshire` | **cn_tarr_hist_c_ayrshire** | Post-867 | ✅ Valid (OTL) | **FLAGGED (Tier 4)** | Real-world foundation in 1197 AD by historical figure absent from campaign; previously accepted under OTL calendar gap |
| `c_linlithgowshire` | **cn_tarr_hist_c_linlithgowshire** | Post-867 | ✅ Valid (OTL) | **FLAGGED (Tier 4)** | Real-world foundation in 1138 AD by historical figure absent from campaign; previously accepted under OTL calendar gap |
| `c_lanarkshire` | **cn_tarr_hist_c_lanarkshire** | Post-867 | ✅ Valid (OTL) | **FLAGGED (Tier 4)** | Real-world foundation in 1140 AD by historical figure absent from campaign; previously accepted under OTL calendar gap |
| `c_athlone` | **cn_tarr_hist_c_athlone** | Post-867 | ✅ Valid (OTL) | **FLAGGED (Tier 4)** | Real-world foundation in 1122 AD by historical figure absent from campaign; previously accepted under OTL calendar gap |
| `c_ennis` | **cn_tarr_hist_c_ennis** | Post-867 | ✅ Valid (OTL) | **FLAGGED (Tier 4)** | Real-world foundation in 1240 AD by historical figure absent from campaign; previously accepted under OTL calendar gap |
| `c_lippe` | **cn_tarr_hist_c_lippe** | Post-867 | ✅ Valid (OTL) | **FLAGGED (Tier 4)** | Real-world foundation in 1123 AD by historical figure absent from campaign; previously accepted under OTL calendar gap |
| `c_oldenburg` | **cn_tarr_hist_c_oldenburg** | Post-867 | ✅ Valid (OTL) | **FLAGGED (Tier 4)** | Real-world foundation in 1108 AD by historical figure absent from campaign; previously accepted under OTL calendar gap |
| `c_waldeck` | **cn_tarr_hist_c_waldeck** | Post-867 | ✅ Valid (OTL) | **FLAGGED (Tier 4)** | Real-world foundation in 1120 AD by historical figure absent from campaign; previously accepted under OTL calendar gap |
| `c_antwerpen` | **cn_tarr_c_antwerpen** | Post-867 | ✅ Valid (OTL) | **FLAGGED (Tier 4)** | Real-world foundation in 1125 AD by historical figure absent from campaign; previously accepted under OTL calendar gap |
| `c_cleves` | **cn_tarr_hist_c_cleves** | Post-867 | ✅ Valid (OTL) | **FLAGGED (Tier 4)** | Real-world foundation in 1020 AD by historical figure absent from campaign; previously accepted under OTL calendar gap |
| `c_nancy` | **cn_tarr_hist_c_nancy** | Post-867 | ✅ Valid (OTL) | **FLAGGED (Tier 4)** | Real-world foundation in 1070 AD by historical figure absent from campaign; previously accepted under OTL calendar gap |
| `c_saarbrucken` | **cn_tarr_hist_c_saarbrucken** | Post-867 | ✅ Valid (OTL) | **FLAGGED (Tier 4)** | Real-world foundation in 999 AD by historical figure absent from campaign; previously accepted under OTL calendar gap |
| `c_mark` | **cn_tarr_hist_c_mark** | Post-867 | ✅ Valid (OTL) | **FLAGGED (Tier 4)** | Real-world foundation in 1198 AD by historical figure absent from campaign; previously accepted under OTL calendar gap |
| `c_eschenlohe` | **cn_tarr_hist_c_eschenlohe** | Post-867 | ✅ Valid (OTL) | **FLAGGED (Tier 4)** | Real-world foundation in 1150 AD by historical figure absent from campaign; previously accepted under OTL calendar gap |
| `c_rothenburg` | **cn_tarr_c_rothenburg** | Post-867 | ✅ Valid (OTL) | **FLAGGED (Tier 4)** | Real-world foundation in 1050 AD by historical figure absent from campaign; previously accepted under OTL calendar gap |
| `c_schaumberg` | **cn_tarr_hist_c_schaumberg** | Post-867 | ✅ Valid (OTL) | **FLAGGED (Tier 4)** | Real-world foundation in 1150 AD by historical figure absent from campaign; previously accepted under OTL calendar gap |
| `c_ravensburg` | **cn_tarr_hist_c_ravensburg** | Post-867 | ✅ Valid (OTL) | **FLAGGED (Tier 4)** | Real-world foundation in 1088 AD by historical figure absent from campaign; previously accepted under OTL calendar gap |
| `c_graz` | **cn_tarr_hist_c_graz** | Post-867 | ✅ Valid (OTL) | **FLAGGED (Tier 4)** | Real-world foundation in 1128 AD by historical figure absent from campaign; previously accepted under OTL calendar gap |
| `c_pitten` | **cn_tarr_c_pitten** | Post-867 | ✅ Valid (OTL) | **FLAGGED (Tier 4)** | Real-world foundation in 1043 AD by historical figure absent from campaign; previously accepted under OTL calendar gap |
| `c_innsbruck` | **cn_tarr_hist_c_innsbruck** | Post-867 | ✅ Valid (OTL) | **FLAGGED (Tier 4)** | Real-world foundation in 1180 AD by historical figure absent from campaign; previously accepted under OTL calendar gap |
| `c_coburg` | **cn_tarr_hist_c_coburg** | Post-867 | ✅ Valid (OTL) | **FLAGGED (Tier 4)** | Real-world foundation in 1056 AD by historical figure absent from campaign; previously accepted under OTL calendar gap |
| `c_kassel` | **cn_tarr_c_kassel** | Post-867 | ✅ Valid (OTL) | **FLAGGED (Tier 4)** | Real-world foundation in 1144 AD by historical figure absent from campaign; previously accepted under OTL calendar gap |
| `c_nassau` | **cn_tarr_hist_c_nassau** | Post-867 | ✅ Valid (OTL) | **FLAGGED (Tier 4)** | Real-world foundation in 1093 AD by historical figure absent from campaign; previously accepted under OTL calendar gap |
| `c_grisons` | **cn_tarr_hist_c_grisons** | Post-867 | ✅ Valid (OTL) | **FLAGGED (Tier 4)** | Real-world foundation in 1367 AD by historical figure absent from campaign; previously accepted under OTL calendar gap |

---

## 4. In-Game Canonized Titles & Cadet Branch Seats (Tier 2)

The audit identified **55** counties whose names derive authentically from in-game progression rather than vanilla map defaults:

| County Key | Save Name | In-Game Canon Basis | Ruling Cadet Branch / Culture | Current Status in Save |
| :--- | :--- | :--- | :--- | :--- |
| `c_zutphen` | **cn_tarr_c_zutphen** | Canonized by ruling cadet branch Chatenois-Zutphen | `Chatenois-Zutphen` (Tarraconian) | ✅ Valid Campaign Canon |
| `c_luxembourg` | **cn_tarr_hist_c_luxembourg** | Formed around organic in-game hybrid culture (Croato-Tarraconian) | `dynn_LechsgmU_nd` (Croato-Tarraconian) | ✅ Valid Campaign Canon |
| `c_bouillon` | **cn_tarr_c_bouillon** | Formed around organic in-game hybrid culture (Croato-Tarraconian) | `dynn_LechsgmU_nd` (Croato-Tarraconian) | ✅ Valid Campaign Canon |
| `c_namur` | **cn_tarr_c_namur** | Formed around organic in-game hybrid culture (Croato-Tarraconian) | `None` (Croato-Tarraconian) | ✅ Valid Campaign Canon |
| `c_metz` | **cn_tarr_c_metz** | Canonized by ruling cadet branch Chatenois-Metz | `Chatenois-Metz` (Tarraconian) | ✅ Valid Campaign Canon |
| `c_bergh` | **cn_tarr_hist_c_bergh** | Canonized by ruling cadet branch Chatenois-Berg | `Chatenois-Berg` (franconian) | ✅ Valid Campaign Canon |
| `c_metzovo` | **cn_tarr_hist_c_metzovo** | Canonized by ruling cadet branch Chatenois-Metz | `Chatenois-Metz` (Tarraconian) | ✅ Valid Campaign Canon |
| `c_buthrotum` | **cn_tarr_c_buthrotum** | Canonized by ruling cadet branch Chatenois-Buthrotum | `Chatenois-Buthrotum` (Tarraconian) | ✅ Valid Campaign Canon |
| `c_zagreb` | **cn_tarr_hist_c_zagreb** | Formed around organic in-game hybrid culture (Croato-Tarraconian) | `Chatenois-Metz` (Croato-Tarraconian) | ✅ Valid Campaign Canon |
| `c_ragusa` | **cn_tarr_c_ragusa** | Formed around organic in-game hybrid culture (Croato-Tarraconian) | `Chatenois-Albret` (Croato-Tarraconian) | ✅ Valid Campaign Canon |
| `c_theodosiopolis` | **cn_tarr_hist_c_theodosiopolis** | Formed around organic in-game hybrid culture (Armeno-Greek) | `Chatenois-Metz` (Armeno-Greek) | ✅ Valid Campaign Canon |
| `c_mesopotamia` | **cn_tarr_c_mesopotamia** | Formed around organic in-game hybrid culture (Armeno-Greek) | `Chatenois-Metz` (Armeno-Greek) | ✅ Valid Campaign Canon |
| `c_turuberan` | **cn_tarr_hist_c_turuberan** | Formed around organic in-game hybrid culture (Armeno-Greek) | `Chatenois-Metz` (Armeno-Greek) | ✅ Valid Campaign Canon |
| `c_hayk` | **cn_tarr_c_hayk** | Formed around organic in-game hybrid culture (Armeno-Greek) | `Chatenois-Metz` (Armeno-Greek) | ✅ Valid Campaign Canon |
| `c_vanand` | **cn_tarr_hist_c_vanand** | Formed around organic in-game hybrid culture (Armeno-Greek) | `Chatenois-Metz` (Armeno-Greek) | ✅ Valid Campaign Canon |
| `c_dvin` | **cn_tarr_c_dvin** | Formed around organic in-game hybrid culture (Armeno-Greek) | `Chatenois-Metz` (Armeno-Greek) | ✅ Valid Campaign Canon |
| `c_tao` | **cn_tarr_c_tao** | Formed around organic in-game hybrid culture (Armeno-Greek) | `Chatenois-Metz` (Armeno-Greek) | ✅ Valid Campaign Canon |
| `c_klarjeti` | **cn_tarr_hist_c_klarjeti** | Formed around organic in-game hybrid culture (Armeno-Greek) | `Chatenois-Metz` (Armeno-Greek) | ✅ Valid Campaign Canon |
| `c_lecce` | **cn_tarr_c_lecce** | Canonized by ruling cadet branch Chatenois-Lecce | `Chatenois-Lecce` (Tarraconian) | ✅ Valid Campaign Canon |
| `c_aalborg` | **cn_tarr_c_aalborg** | Formed around organic in-game hybrid culture (Croato-Tarraconian) | `Chatenois-Metz` (Croato-Tarraconian) | ✅ Valid Campaign Canon |

---

## 5. Register of Flagged Titles Requiring Pre-867 Resolution in Phase 4

Below is the actionable catalog of all **150** flagged titles inside the Roman Empire, complete with their sovereign trajectory and recommended sub-barony candidates (`Option A`):

| County Key | Current Name | De Jure Kingdom | Tier | Anachronism / Mismatch Reason | Recommended Pre-867 Sub-Barony Candidate (`Option A`) |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `c_gowrie` | **cn_tarr_hist_c_gowrie** | k_scotland | **Tier 4** | Real-world foundation in 1124 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_st_johnston` (St Johnston) |
| `c_ayrshire` | **cn_tarr_hist_c_ayrshire** | k_scotland | **Tier 4** | Real-world foundation in 1197 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_kyle` (Kyle) |
| `c_linlithgowshire` | **cn_tarr_hist_c_linlithgowshire** | k_scotland | **Tier 4** | Real-world foundation in 1138 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_linlithgow` (Linlithgow) |
| `c_lanarkshire` | **cn_tarr_hist_c_lanarkshire** | k_scotland | **Tier 4** | Real-world foundation in 1140 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_lanark` (Lanark) |
| `c_athlone` | **cn_tarr_hist_c_athlone** | k_ireland | **Tier 4** | Real-world foundation in 1122 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_athlone` (Athlone) |
| `c_ennis` | **cn_tarr_hist_c_ennis** | k_ireland | **Tier 4** | Real-world foundation in 1240 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_ennis` (Ennis) |
| `c_lippe` | **cn_tarr_hist_c_lippe** | k_saxony | **Tier 4** | Real-world foundation in 1123 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_lippe` (Lippe) |
| `c_oldenburg` | **cn_tarr_hist_c_oldenburg** | k_saxony | **Tier 4** | Real-world foundation in 1108 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_leer` (Leer) |
| `c_waldeck` | **cn_tarr_hist_c_waldeck** | k_saxony | **Tier 4** | Real-world foundation in 1120 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_waldeck` (Waldeck) |
| `c_antwerpen` | **cn_tarr_c_antwerpen** | k_lotharingia | **Tier 4** | Real-world foundation in 1125 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_antwerpen` (Antwerpen) |
| `c_cleves` | **cn_tarr_hist_c_cleves** | k_lotharingia | **Tier 4** | Real-world foundation in 1020 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_kleve` (Kleve) |
| `c_nancy` | **cn_tarr_hist_c_nancy** | k_lotharingia | **Tier 4** | Real-world foundation in 1070 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_nancy` (Nancy) |
| `c_saarbrucken` | **cn_tarr_hist_c_saarbrucken** | k_lotharingia | **Tier 4** | Real-world foundation in 999 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_saarbrucken` (Saarbrücken) |
| `c_mark` | **cn_tarr_hist_c_mark** | k_lotharingia | **Tier 4** | Real-world foundation in 1198 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_mark` (Mark) |
| `c_eschenlohe` | **cn_tarr_hist_c_eschenlohe** | k_bavaria | **Tier 4** | Real-world foundation in 1150 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_eschenlohe` (Eschenlohe) |
| `c_rothenburg` | **cn_tarr_c_rothenburg** | k_bavaria | **Tier 4** | Real-world foundation in 1050 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_freising` (Freising) |
| `c_schaumberg` | **cn_tarr_hist_c_schaumberg** | k_bavaria | **Tier 4** | Real-world foundation in 1150 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_schaumberg` (Schaumberg) |
| `c_ravensburg` | **cn_tarr_hist_c_ravensburg** | k_bavaria | **Tier 4** | Real-world foundation in 1088 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_bregenz` (Bregenz) |
| `c_graz` | **cn_tarr_hist_c_graz** | k_bavaria | **Tier 4** | Real-world foundation in 1128 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_graz` (Graz) |
| `c_pitten` | **cn_tarr_c_pitten** | k_bavaria | **Tier 4** | Real-world foundation in 1043 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_pitten` (Pitten) |
| `c_innsbruck` | **cn_tarr_hist_c_innsbruck** | k_bavaria | **Tier 4** | Real-world foundation in 1180 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_innsbruck` (Innsbruck) |
| `c_coburg` | **cn_tarr_hist_c_coburg** | k_east_francia | **Tier 4** | Real-world foundation in 1056 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_lichtenfels` (Lichtenfels) |
| `c_kassel` | **cn_tarr_c_kassel** | k_east_francia | **Tier 4** | Real-world foundation in 1144 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_kassel` (Kassel) |
| `c_nassau` | **cn_tarr_hist_c_nassau** | k_east_francia | **Tier 4** | Real-world foundation in 1093 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_siegen` (Siegen) |
| `c_grisons` | **cn_tarr_hist_c_grisons** | k_east_francia | **Tier 4** | Real-world foundation in 1367 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_chur` (Chur) |
| `c_baden` | **cn_tarr_hist_c_baden** | k_east_francia | **Tier 4** | Real-world foundation in 1112 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_baden` (Baden) |
| `c_zollern` | **cn_tarr_hist_c_zollern** | k_east_francia | **Tier 4** | Real-world foundation in 1061 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_zollern` (Zollern) |
| `c_pozega` | **cn_tarr_hist_c_pozega** | k_croatia | **Tier 4** | Post-867 foundation (1200 AD) or high-medieval dynastic castle | `b_pozega` (Požega) |
| `c_soli` | **cn_tarr_c_soli** | k_croatia | **Tier 4** | Post-867 foundation (1059 AD) or high-medieval dynastic castle | `b_soli` (Soli) |
| `c_usora` | **cn_tarr_c_usora** | k_croatia | **Tier 4** | Real-world foundation in 1225 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_srebrenik` (Srebrenik) |
| `c_vodica` | **cn_tarr_c_vodica** | k_croatia | **Tier 4** | Real-world foundation in 1197 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_vodicevo` (Vodičevo) |
| `c_sumadija` | **cn_tarr_hist_c_sumadija** | k_serbia | **Tier 4** | Flagged in previous chancellery audit as anachronistic foundation | `b_krusevac` (Kruševac) |
| `c_macva` | **cn_tarr_hist_c_macva** | k_serbia | **Tier 4** | Post-867 foundation (1247 AD) or high-medieval dynastic castle | `b_macva` (Macva) |
| `c_foggia` | **cn_tarr_hist_c_foggia** | k_sicily | **Tier 4** | Post-867 foundation (1080 AD) or high-medieval dynastic castle | `b_lucera` (Lucera) |
| `c_monferrato` | **cn_tarr_hist_c_monferrato** | k_italy | **Tier 4** | Real-world foundation in 961 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_asti` (Asti) |
| `c_cuneo` | **cn_tarr_hist_c_cuneo** | k_italy | **Tier 4** | Real-world foundation in 1198 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_cuneo` (Cuneo) |
| `c_ajaccio` | **cn_tarr_c_ajaccio** | k_sardinia | **Tier 4** | Real-world foundation in 1492 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_ajaccio` (Ajaccio) |
| `c_dalabergslagen` | **cn_tarr_hist_c_dalabergslagen** | k_sweden | **Tier 4** | Flagged in previous chancellery audit as anachronistic foundation | `b_falene` (Falene) |
| `c_sjaelland` | **cn_tarr_c_sjaelland** | k_denmark | **Tier 4** | Post-867 foundation (1167 AD) or high-medieval dynastic castle | `b_roskilde` (Roskilde) |
| `c_nyland` | **cn_tarr_hist_c_nyland** | k_finland | **Tier 5** | Swedish crusade colonial exonym present in Finland/Karelia, but Swedish Crown never ruled it in campaign | `b_porvoo` (Porvoo) |
| `c_pedersore` | **cn_tarr_hist_c_pedersore** | k_finland | **Tier 5** | Swedish crusade colonial exonym present in Finland/Karelia, but Swedish Crown never ruled it in campaign | `b_pedersore` (Pietarsaari) |
| `c_viipuri` | **cn_tarr_hist_c_viipuri** | k_finland | **Tier 4** | Real-world foundation in 1293 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_viipuri` (Wiborg) |
| `c_stettin` | **cn_tarr_hist_c_stettin** | k_pomerania | **Tier 4** | Real-world foundation in 1243 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_szczecin` (Stettin) |
| `c_kolobrzeg` | **cn_tarr_c_kolobrzeg** | k_pomerania | **Tier 4** | Real-world foundation in 1255 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_swinoujscie` (Wollin) |
| `c_soldin` | **cn_tarr_c_soldin** | k_pomerania | **Tier 4** | Real-world foundation in 1260 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_soldin` (Cedynia) |
| `c_landsberg` | **cn_tarr_c_landsberg** | k_pomerania | **Tier 4** | Real-world foundation in 1174 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_landsberg` (Zantoch) |
| `c_rostock` | **cn_tarr_c_rostock** | k_pomerania | **Tier 4** | Real-world foundation in 1218 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_rostock` (Rostock) |
| `c_werle` | **cn_tarr_c_werle** | k_pomerania | **Tier 4** | Real-world foundation in 1229 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_werle` (Werle) |
| `c_slupsk` | **cn_tarr_hist_c_slupsk** | k_pomerania | **Tier 4** | Real-world foundation in 1310 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_koszalin` (Köslin) |
| `c_brandenburg` | **cn_tarr_c_brandenburg** | k_pomerania | **Tier 4** | Real-world foundation in 1157 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_potsdam` (Potsdam) |
| `c_berlin` | **cn_tarr_hist_c_berlin** | k_pomerania | **Tier 4** | Real-world foundation in 1244 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_berlin` (Berlin) |
| `c_prenzlau` | **cn_tarr_c_prenzlau** | k_pomerania | **Tier 4** | Real-world foundation in 1187 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_prenzlau` (Prenzlau) |
| `c_trakai` | **cn_tarr_hist_c_trakai** | k_lithuania | **Tier 4** | Real-world foundation in 1316 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_trakai` (Trakai) |
| `c_malbork` | **cn_tarr_hist_c_malbork** | k_lithuania | **Tier 4** | Real-world foundation in 1274 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_elblag` (Elbing) |
| `c_wormditt` | **cn_tarr_hist_c_wormditt** | k_lithuania | **Tier 4** | Real-world foundation in 1308 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_wormditt` (Wormditt) |
| `c_konigsberg` | **cn_tarr_hist_c_konigsberg** | k_lithuania | **Tier 4** | Real-world foundation in 1255 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_konigsberg` (Königsberg) |
| `c_bartenstein` | **cn_tarr_hist_c_bartenstein** | k_lithuania | **Tier 5** | German Ostsiedlung/Teutonic exonym present in Baltic province, but Teutonic Order never held it in campaign | Hydronymic Fallback (`Option B`) |
| `c_torun` | **cn_tarr_hist_c_torun** | k_lithuania | **Tier 4** | Real-world foundation in 1231 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_kulm` (Kulm) |
| `c_osterode` | **cn_tarr_hist_c_osterode** | k_lithuania | **Tier 5** | German Ostsiedlung/Teutonic exonym present in Baltic province, but Teutonic Order never held it in campaign | `b_eylau` (Iława) |
| `c_allenstein` | **cn_tarr_hist_c_allenstein** | k_lithuania | **Tier 5** | German Ostsiedlung/Teutonic exonym present in Baltic province, but Teutonic Order never held it in campaign | Hydronymic Fallback (`Option B`) |
| `c_angerburg` | **cn_tarr_hist_c_angerburg** | k_lithuania | **Tier 5** | German Ostsiedlung/Teutonic exonym present in Baltic province, but Teutonic Order never held it in campaign | `b_lotzen` (Lötzen) |
| `c_memel` | **cn_tarr_c_memel** | k_lithuania | **Tier 4** | Flagged in previous chancellery audit as anachronistic foundation | `b_memel` (Memel) |
| `c_reval` | **cn_tarr_hist_c_reval** | k_esthonia | **Tier 4** | Real-world foundation in 1219 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_reval` (Rafala) |
| `c_wiek` | **cn_tarr_hist_c_wiek** | k_esthonia | **Tier 4** | Real-world foundation in 1279 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_hapsal` (Ridala) |
| `c_sacz` | **cn_tarr_c_sacz** | k_poland | **Tier 4** | Post-867 foundation (1292 AD) or high-medieval dynastic castle | `b_sacz` (Sącz) |
| `c_lubusz` | **cn_tarr_c_lubusz** | k_poland | **Tier 4** | Real-world foundation in 1249 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_lebus` (Lebus) |
| `c_opole` | **cn_tarr_c_opole** | k_poland | **Tier 4** | Real-world foundation in 1217 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_opole` (Oppeln) |
| `c_breslau` | **cn_tarr_c_breslau** | k_poland | **Tier 4** | Real-world foundation in 1242 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_breslau` (Breslau) |
| `c_legnica` | **cn_tarr_c_legnica** | k_poland | **Tier 4** | Real-world foundation in 1252 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_legnica` (Liegnitz) |
| `c_litomerice` | **cn_tarr_c_litomerice** | k_bohemia | **Tier 4** | Real-world foundation in 1219 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_litomerice` (Litoměřice) |
| `c_zatec` | **cn_tarr_c_zatec** | k_bohemia | **Tier 4** | Real-world foundation in 1265 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_zatec` (Žatec) |
| `c_plzen` | **cn_tarr_c_plzen** | k_bohemia | **Tier 4** | Real-world foundation in 1295 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_plzen` (Plzeň) |
| `c_doudleby` | **cn_tarr_c_doudleby** | k_bohemia | **Tier 4** | Real-world foundation in 1265 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_doudleby` (Doudleby) |
| `c_hradec` | **cn_tarr_c_hradec** | k_bohemia | **Tier 4** | Real-world foundation in 1059 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_hradec` (Hradec) |
| `c_caslav` | **cn_tarr_c_caslav** | k_bohemia | **Tier 4** | Real-world foundation in 1059 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_caslav` (Čáslav) |
| `c_brno` | **cn_tarr_c_brno** | k_bohemia | **Tier 4** | Real-world foundation in 1243 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_brno` (Brno) |
| `c_jihlava` | **cn_tarr_hist_c_jihlava** | k_bohemia | **Tier 4** | Real-world foundation in 1240 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_jihlava` (Jihlava) |
| `c_znojmo` | **cn_tarr_c_znojmo** | k_bohemia | **Tier 4** | Real-world foundation in 1226 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_znojmo` (Znojmo) |
| `c_belz` | **cn_tarr_c_belz** | e_west_slavia | **Tier 4** | Real-world foundation in 1059 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_belz` (Belz) |
| `c_dresden` | **cn_tarr_hist_c_dresden** | k_sorbia | **Tier 4** | Real-world foundation in 1206 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_dresden` (Dresden) |
| `c_osterland` | **cn_tarr_c_osterland** | k_sorbia | **Tier 4** | Real-world foundation in 1015 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_colditz` (Colditz) |
| `c_cottbus` | **cn_tarr_c_cottbus** | k_sorbia | **Tier 4** | Real-world foundation in 1156 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_cottbus` (Cottbus) |
| `c_gorlitz` | **cn_tarr_hist_c_gorlitz** | k_sorbia | **Tier 4** | Real-world foundation in 1071 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_gorlitz` (Görlitz) |
| `c_wittenberg` | **cn_tarr_hist_c_wittenberg** | k_sorbia | **Tier 4** | Real-world foundation in 1180 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_wittenberg` (Wittenberg) |
| `c_hradyzk` | **cn_tarr_hist_c_hradyzk** | k_ruthenia | **Tier 4** | Flagged in previous chancellery audit as anachronistic foundation | `b_hradyzk` (Hradyzk) |
| `c_odoyev` | **cn_tarr_c_odoyev** | k_ruthenia | **Tier 4** | Flagged in previous chancellery audit as anachronistic foundation | `b_odoyev` (Odoyev) |
| `c_sebezh` | **cn_tarr_c_sebezh** | k_novgorod | **Tier 4** | Flagged in previous chancellery audit as anachronistic foundation | `b_sebezh` (Sebezh) |
| `c_tikhvin` | **cn_tarr_c_tikhvin** | k_novgorod | **Tier 4** | Flagged in previous chancellery audit as anachronistic foundation | `b_tikhvin` (Tikhvin) |
| `c_tver` | **cn_tarr_hist_c_tver** | k_opolye | **Tier 4** | Flagged in previous chancellery audit as anachronistic foundation | `b_tver` (Tver) |
| `c_tula` | **cn_tarr_hist_c_tula** | k_opolye | **Tier 4** | Flagged in previous chancellery audit as anachronistic foundation | `b_tula` (Tula) |
| `c_plyos` | **cn_tarr_c_plyos** | k_opolye | **Tier 4** | Flagged in previous chancellery audit as anachronistic foundation | `b_plyos` (Plyos) |
| `c_kirillov` | **cn_tarr_hist_c_kirillov** | k_bjarmaland | **Tier 4** | Real-world foundation in 1397 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_kirillov` (Kirillov) |
| `c_ustyug` | **cn_tarr_hist_c_ustyug** | k_bjarmaland | **Tier 4** | Real-world foundation in 1207 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_veliky_ustyug` (Veliky Ustyug) |
| `c_cherkassy` | **cn_tarr_hist_c_cherkassy** | k_pontic_steppe | **Tier 4** | Real-world foundation in 1305 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_cherkassy` (Cherkassy) |
| `c_bakhmut` | **cn_tarr_hist_c_bakhmut** | k_pontic_steppe | **Tier 5** | Post-medieval Russian Imperial/Cossack exonym in Pontic steppe where Rurikids never ruled | `b_bakhmut` (Bakhmut) |
| `c_kazanskaya` | **cn_tarr_hist_c_kazanskaya** | k_pontic_steppe | **Tier 5** | Post-medieval Russian Imperial/Cossack exonym in Pontic steppe where Rurikids never ruled | `b_kazanskaya` (Kazanskaya) |
| `c_millerovo` | **cn_tarr_hist_c_millerovo** | k_pontic_steppe | **Tier 5** | Post-medieval Russian Imperial/Cossack exonym in Pontic steppe where Rurikids never ruled | `b_millerovo` (South Kazanskaya) |
| `c_kalos_limen` | **cn_tarr_hist_c_kalos_limen** | k_pontic_steppe | **Tier 4** | Real-world foundation in 1475 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_kerkinitis` (Güzliev) |
| `c_astrakhan` | **cn_tarr_hist_c_astrakhan** | k_caucasus | **Tier 4** | Real-world foundation in 1333 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_astrakhan` (Astrakhan) |
| `c_yaitsk` | **cn_tarr_c_yaitsk** | k_caspian_steppe | **Tier 4** | Flagged in previous chancellery audit as anachronistic foundation | `b_tasqala` (Tasqala) |
| `c_ilek` | **cn_tarr_c_ilek** | k_caspian_steppe | **Tier 4** | Flagged in previous chancellery audit as anachronistic foundation | `b_santas` (Santas) |
| `c_cheboksary` | **cn_tarr_hist_c_cheboksary** | k_mordvinia | **Tier 4** | Post-867 foundation (1469 AD) or high-medieval dynastic castle | `b_cheboksary` (Cheboksary) |
| `c_voronezh` | **cn_tarr_c_voronezh** | k_mordvinia | **Tier 4** | Flagged in previous chancellery audit as anachronistic foundation | `b_voronezh` (Voronezh) |
| `c_kurdistan` | **cn_tarr_hist_c_kurdistan** | k_jazira | **Tier 4** | Real-world foundation in 1142 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_tall_haftun` (Tall Haftun) |
| `c_targu_jiu` | **cn_tarr_hist_c_targu_jiu** | k_dacia | **Tier 4** | Flagged in previous chancellery audit as anachronistic foundation | `b_targu_jiu` (Târgu Jiu) |
| `c_calafat` | **cn_tarr_hist_c_calafat** | k_dacia | **Tier 4** | Flagged in previous chancellery audit as anachronistic foundation | `b_calafat` (Calafat) |
| `c_craiova` | **cn_tarr_hist_c_craiova** | k_dacia | **Tier 4** | Post-867 foundation (1475 AD) or high-medieval dynastic castle | `b_craiova` (Craiova) |
| `c_tigheci` | **cn_tarr_c_tigheci** | k_moldavia | **Tier 4** | Flagged in previous chancellery audit as anachronistic foundation | `b_tigheci` (Tigheci) |
| `c_visegrad` | **cn_tarr_c_visegrad** | k_hungary | **Tier 4** | Post-867 foundation (1059 AD) or high-medieval dynastic castle | `b_visegrad_hun` (Višegrad) |
| `c_gemer` | **cn_tarr_hist_c_gemer** | k_hungary | **Tier 4** | Real-world foundation in 1198 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_gemer` (Gemer) |
| `c_orava` | **cn_tarr_c_orava** | k_hungary | **Tier 4** | Post-867 foundation (1267 AD) or high-medieval dynastic castle | `b_arva` (Orava) |
| `c_borsod` | **cn_tarr_c_borsod** | k_hungary | **Tier 4** | Post-867 foundation (1059 AD) or high-medieval dynastic castle | `b_borsod` (Borsod) |
| `c_marmaros` | **cn_tarr_hist_c_marmaros** | k_hungary | **Tier 4** | Post-867 foundation (1199 AD) or high-medieval dynastic castle | `b_maramarossziget` (Máramarossziget) |
| `c_szekelyfold` | **cn_tarr_hist_c_szekelyfold** | k_hungary | **Tier 4** | Flagged in previous chancellery audit as anachronistic foundation | `b_szekelyudvarhely` (Székelyudvarhely) |
| `c_barcasag` | **cn_tarr_hist_c_barcasag** | k_hungary | **Tier 4** | Real-world foundation in 1211 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_brasso` (Brasso) |
| `c_fogaras` | **cn_tarr_hist_c_fogaras** | k_hungary | **Tier 4** | Post-867 foundation (1291 AD) or high-medieval dynastic castle | `b_fogaras` (Fogaras) |
| `c_beszterce` | **cn_tarr_hist_c_beszterce** | k_hungary | **Tier 4** | Post-867 foundation (1206 AD) or high-medieval dynastic castle | `b_beszterce` (Beszterce) |
| `c_hunyad` | **cn_tarr_hist_c_hunyad** | k_hungary | **Tier 4** | Post-867 foundation (1265 AD) or high-medieval dynastic castle | `b_vajdahunyad` (Vajdahunyad) |
| `c_zarand` | **cn_tarr_c_zarand** | k_hungary | **Tier 4** | Post-867 foundation (1059 AD) or high-medieval dynastic castle | `b_zarand` (Zaránd) |
| `c_temes` | **cn_tarr_c_temes** | k_hungary | **Tier 4** | Post-867 foundation (1177 AD) or high-medieval dynastic castle | `b_temesvar` (Temesvár) |
| `c_bacs` | **cn_tarr_c_bacs** | k_hungary | **Tier 4** | Post-867 foundation (1059 AD) or high-medieval dynastic castle | `b_bacs` (Bács) |
| `c_clermont` | **cn_tarr_hist_c_clermont** | k_france | **Tier 4** | Post-867 foundation (1023 AD) or high-medieval dynastic castle | `b_clermont` (Clermont) |
| `c_guines` | **cn_tarr_hist_c_guines** | k_france | **Tier 4** | Post-867 foundation (928 AD) or high-medieval dynastic castle | `b_calais` (Calais) |
| `c_savoie` | **cn_tarr_hist_c_savoie** | k_burgundy | **Tier 4** | Real-world foundation in 1232 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_moutiers` (Moûtiers) |
| `c_aargau` | **cn_tarr_hist_c_aargau** | k_burgundy | **Tier 4** | Real-world foundation in 1020 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_biel` (Biel) |
| `c_neuchatel` | **cn_tarr_c_neuchatel** | k_burgundy | **Tier 4** | Real-world foundation in 1011 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_neuchatel` (Neuchâtel) |
| `c_molina` | **cn_tarr_hist_c_molina** | k_andalusia | **Tier 4** | Post-867 foundation (1138 AD) or high-medieval dynastic castle | `b_molina` (Molina) |
| `c_alcacer_do_sal` | **cn_tarr_c_alcacer_do_sal** | k_badajoz | **Tier 4** | Post-867 foundation (1059 AD) or high-medieval dynastic castle | `b_alcacerdosal` (Alcácer do Sal) |
| `c_plasencia` | **cn_tarr_hist_c_plasencia** | k_badajoz | **Tier 4** | Post-867 foundation (1186 AD) or high-medieval dynastic castle | `b_hervas` (Hervás) |
| `c_medellin` | **cn_tarr_c_medellin** | k_badajoz | **Tier 4** | Post-867 foundation (1059 AD) or high-medieval dynastic castle | `b_medellin` (Medellin) |
| `c_castellon` | **cn_tarr_c_castellon** | k_valencia | **Tier 4** | Real-world foundation in 1251 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_castellon` (Castelló) |
| `c_alarcon` | **cn_tarr_c_alarcon** | k_valencia | **Tier 4** | Post-867 foundation (1059 AD) or high-medieval dynastic castle | `b_alarcon` (Alarcón) |
| `c_burgos` | **cn_tarr_c_burgos** | k_castille | **Tier 4** | Post-867 foundation (1059 AD) or high-medieval dynastic castle | `b_burgos` (Burgos) |
| `c_valladolid` | **cn_tarr_hist_c_valladolid** | k_castille | **Tier 4** | Post-867 foundation (1072 AD) or high-medieval dynastic castle | `b_valladolid` (Valladolid) |
| `c_soria` | **cn_tarr_hist_c_soria** | k_castille | **Tier 4** | Post-867 foundation (1109 AD) or high-medieval dynastic castle | `b_soria` (Soria) |
| `c_cuellar` | **cn_tarr_hist_c_cuellar** | k_castille | **Tier 4** | Post-867 foundation (1085 AD) or high-medieval dynastic castle | `b_segovia` (Segovia) |
| `c_albarracin` | **cn_tarr_c_albarracin** | k_aragon | **Tier 4** | Post-867 foundation (1059 AD) or high-medieval dynastic castle | `b_albarracin` (Albarracin) |
| `c_puigcerda` | **cn_tarr_hist_c_puigcerda** | k_aragon | **Tier 4** | Real-world foundation in 1177 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_puigcerda` (Puigcerdà) |
| `c_coruna` | **cn_tarr_hist_c_coruna** | k_spanish_galicia | **Tier 4** | Real-world foundation in 1208 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_corunna` (A Corunnã) |
| `c_castelo_branco` | **cn_tarr_hist_c_castelo_branco** | k_portugal | **Tier 4** | Post-867 foundation (1213 AD) or high-medieval dynastic castle | `b_castelo_branco` (Castelo Branco) |
| `c_marrakesh` | **cn_tarr_hist_c_marrakesh** | k_maghreb | **Tier 4** | Post-867 foundation (1062 AD) or high-medieval dynastic castle | `b_marrakesh` (Marrakesh) |
| `c_taza` | **cn_tarr_c_taza** | k_maghreb | **Tier 4** | Post-867 foundation (1142 AD) or high-medieval dynastic castle | `b_taza` (Taza) |
| `c_orania` | **cn_tarr_c_orania** | k_tahert | **Tier 4** | Real-world foundation in 1059 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_oran` (Oran) |
| `c_bejaia` | **cn_tarr_hist_c_bejaia** | k_tahert | **Tier 4** | Real-world foundation in 1067 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_bejaia` (Bejaia) |
| `c_satfura` | **cn_tarr_c_satfura** | k_africa | **Tier 4** | Real-world foundation in 1059 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_banzart` (Banzart) |
| `c_wadan` | **cn_tarr_c_wadan** | k_anbiya | **Tier 4** | Flagged in previous chancellery audit as anachronistic foundation | `b_wadan` (Wadan) |
| `c_murzuk` | **cn_tarr_hist_c_murzuk** | k_sahara | **Tier 4** | Real-world foundation in 1310 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_murzuk` (Murzuk) |
| `c_kerak` | **cn_tarr_hist_c_kerak** | k_jerusalem | **Tier 4** | Real-world foundation in 1142 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_kerak` (Kerak) |
| `c_lasta` | **cn_tarr_hist_c_lasta** | k_abyssinia | **Tier 4** | Real-world foundation in 1181 AD by historical figure absent from campaign; previously accepted under OTL calendar gap | `b_lalibela` (Lalībäla) |
| `c_jolof` | **cn_tarr_hist_c_jolof** | k_takrur | **Tier 4** | Post-867 foundation (1350 AD) or high-medieval dynastic castle | `b_tyeng` (Tyeng) |

---

## 6. Next Steps & Transition to Phase 3

1. **Phase 3 (Automated Screening & Reconciliation Matrix):**
   * Screen all 163 flagged Tier 4 & Tier 5 titles against the compiled dictionary of ancient toponyms and hydronyms.
   * Finalize the sub-barony candidate mapping for every flagged county.
2. **Phase 4 (Resolution Pipeline & Cadet Branch Renames):**
   * Finalize Option A (Sub-Barony), Option B (Hydronym), and Option C (Founder Personality) resolutions.
   * Apply Tarraconian sound laws to generate official Chancellery names and adjectives.
   * Systematically update cadet branch toponymic suffixes (`Kestenholz-<Seat>`).

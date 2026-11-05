# Master Dynastic Realignment Register (Toponym-First Coupling)

* **Project:** Tarraconian Chancellery Mod & Imperial Documentation
* **Scope:** All noble dynasties and cadet houses derived from anachronistic title names in the Holy Roman Empire and imperial borderlands.
* **Guiding Rule:** **The Toponym-First Principle** (Physical Geography & Antiquity Substrates $\rightarrow$ Landed Title $\rightarrow$ Dynastic Eponym).

---

## 1. Problem Statement & The Inversion of Dynastic Causality

In Crusader Kings III, dynastic generation operates mechanically in reverse:
1. **Static Vanilla Map Anachronisms:** CK3 uses a single landed title map spanning 867 to 1453. Numerous titles represent post-867 High/Late Medieval castles (*Habsburg*, *Hohenzollern*, *Berg*, *Saarbrücken*, *Mark*), 12th–14th century Ostsiedlung foundations (*Lemberg*, *Uničov*, *Hirschberg*, *Koschmin*), or post-867 frontier outposts (*Novogrudok*, *Volkovysk*, *Porto-Vecchio*, *Lyubim*).
2. **Dynamic Cadet & Eponym Generation:** When an unlanded character is granted land or a ruler establishes a cadet branch, the game engine automatically stamps the holding's name onto the dynasty (e.g., *House Naugardukas* from `c_novogrudok`, *Karling-Uničov* from `b_unicov`, *Reginar-Vecchio* from `c_vecchio`, *Chatenois-Lemberg* from `c_lviv`).
3. **The Toponym-First Inversion:** Under imperial historiography, houses cannot validate or grandfather anachronistic titles. Instead, causality must be inverted: **the holding is first cleansed of its post-867 name**, and the noble house's name is subsequently realigned to the restored authentic antiquity centre or hydronym.

---

## 2. Non-Chatenois Dynastic & Cadet Realignment Register

The following noble houses across the Empire and its marchlands were generated from anachronistic holding names and are hereby realigned to their authentic pre-867 seats:

| House ID | Dynasty | Current In-Game Name | Underlying Origin Seat | Anachronism Reason | Resolved Toponym-First Seat | Realigned House Name | Tarraconian Chancellery Form | Status & Justification |
| :---: | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `21909` | **Babruysk** (`16793920`) | `Babruysk` | `c_babruysk` (c_babruysk (attested 1387)) | Post-867 foundation | **Berezina / Rechytsa** | **Berezina** | `Beresîne` | Bobruysk is a 14th-c. settlement. Realigned to major river corridor Berezina / Dregovich gord Rechytsa. |
| `16801742` | **Brunnsholm** (`33570086`) | `Brunnsholm-Sebezh` | `c_sebezh` (c_sebezh (fortress 1414)) | Post-867 foundation | **Lake Sebezh (Sebēža)** | **Brunnsholm-Sebêsch** | `Brunnsholm-Sebêsch` | Sebezh fortress dates to 1414. Realigned to ancient Baltic hydronym of Lake Sebezh (*Sebēža*). |
| `12948` | **Cétchathach** (`1839`) | `Cétchathach-Athlone` | `c_athlone` (c_athlone (wicker bridge & castle 1120)) | Post-867 foundation | **Uisnech** | **Cétchathach-Uisnech** | `Cétchathach-Uisnech` | Athlone castle/bridge dates to 1120. Realigned to ancient royal ritual hill Uisnech (b_uisneach). |
| `50343822` | **Karling** (`2027`) | `Karling-Uničov` | `c_olomouc` (b_unicov (chartered 1213 by Margrave Vladislaus Henry)) | Post-867 foundation | **Litovel / Morawa** | **Karling-Litovel** | `Karling-Litovel` | Underlying seat Uničov was founded in 1213. Realigned to pre-867 Moravian center Litovel on the river Morava. |
| `12726` | **Karling** (`2027`) | `Karling-Calw` | `c_calw` (c_calw (Burg Calw 11th c.)) | Post-867 foundation | **Hirsau** | **Karling-Hirsau** | `Karling-Hirsau` | Underlying seat Burg Calw is an 11th-c. foundation. Realigned to the 830 Carolingian imperial abbey Hirsau. |
| `14423` | **Karling** (`2027`) | `Karling-Opava` | `c_opava` (c_opava (town chartered 1224)) | Post-867 foundation | **Troppouwe (river Opava / Hradec nad Moravicí)** | **Karling-Troppouwe** | `Karling-Troppouwe` | Town charter is 13th c.; realigned via authentic ancient hydronym Upava / Troppau. |
| `25935` | **Leoben** (`24396`) | `Leoben` | `c_leoben` (c_leoben (planned city 1261 by Ottokar II)) | Post-867 foundation | **Göss (Imperial Abbey 1004)** | **Göss** | `van Göss` | Leoben planned town founded 1261. Realigned to Ottonian imperial abbey Göss (1004). |
| `2107` | **Memel** (`2107`) | `dynn_Memel` | `c_memel` (c_memel (Memelburg castle 1252)) | Post-867 foundation | **Pilsāts / Mēmele** | **Pilsāts** | `Mêmele` | Memelburg castle dates to 1252. Realigned to ancient Curonian fortress Pilsāts and river Mēmele. |
| `16792693` | **Naugardukas** (`16792444`) | `Naugardukas` | `c_novogrudok` (Naugardukas (c. 1044 AD 'New Castle')) | Post-867 foundation | **Plîse (Baltic Plesė)** | **iš Plesės** | `Dat Hûs van der Plîse` | Derived in 977 when Chief Girdenis was granted c_novogrudok. Realigned to authentic pre-867 Baltic hydronym Plisa / Plesė. |
| `24307` | **Palemonaitis** (`1817`) | `Palemonaitis-Kazanskaya` | `c_kazanskaya` (c_kazanskaya (17th-c. Cossack stanitsa)) | Post-867 foundation | **Middel-Dôn (Middle Don basin)** | **Palemonaitis-Middel-Dôn** | `Palemonaitis-Middel-Dôn` | Kazanskaya is a 17th-c. stanitsa. Realigned to physical geography of the Middle Don basin. |
| `67131755` | **Reginar** (`1716`) | `Reginar-Vecchio` | `c_vecchio` (c_vecchio (Porto-Vecchio founded 1539 by Genoa)) | Post-867 foundation | **Portus Syracusanus (Sirakusan)** | **Reginar-Sirakusan** | `Reginar-Sirakusan` | Porto-Vecchio is a 1539 Genoese fortress. Realigned to classical Greco-Roman Portus Syracusanus. |
| `16800196` | **Soundavara** (`33567416`) | `Soundavara-Lyubim` | `c_lyubim` (c_lyubim (Muscovite line fort 1538)) | Post-867 foundation | **Obnore (river Obnora)** | **Soundavara-Obnore** | `Soundavara-Obnore` | Lyubim is a 16th-c. fortress. Realigned to the ancient hydronym of the Obnora River. |
| `33569509` | **Soundavara** (`33567416`) | `Soundavara-Molina` | `c_molina` (c_molina (12th-c. Lordship of Molina)) | Post-867 foundation | **Ercávica (Erkawîka)** | **Soundavara-Erkawîka** | `Soundavara-Erkawîka` | Molina is a 12th-c. taifa/lordship. Realigned to pre-867 Celtiberian/Roman civitas Ercávica. |
| `16803302` | **Steyr** (`16801755`) | `Steyr` | `c_steyr` (c_steyr (Styraburg c. 985)) | Post-867 foundation | **Enns / Lorch (Lauriacum)** | **Enns** | `van Enns` | Styraburg dates to c. 985. Realigned to Roman legionary fortress and bishopric Lauriacum / Enns. |
| `22261` | **Stężyca** (`21005`) | `Stężyca` | `c_sandomierz` (b_stezyca (town attested 1330)) | Post-867 foundation | **Sieciechów (Sitzichow)** | **Sitzichow** | `van Sitzichow` | Stężyca is a 14th-c. foundation. Realigned to 11th-c. Piast palatine castrum Sieciechów. |
| `3464` | **Tigheci** (`3464`) | `dynn_Tigheci` | `c_tigheci` (c_tigheci) | Post-867 foundation | **Codrii Tigheciului (Tîghetsch)** | **Tîghetsch** | `Tîghetsch` | Retained via Category C topographic ancient forest Codrii Tigheciului. |
| `16803030` | **Tula** (`16801494`) | `dynn_Tula` | `c_tula` (c_tula (14th-c. Muscovite frontier town)) | Post-867 foundation | **Pronsk / Tulitsa** | **Pronsk** | `Pronsk` | Tula attested 14th c. Realigned to 10th-c. Vyatichi hillfort Pronsk or Tulitsa river. |
| `21816` | **Vologda** (`20602`) | `Vologda` | `c_vologda` (c_vologda (chartered 1147)) | Post-867 foundation | **Walgede (Finno-Ugric / Vepsian hydronym)** | **Walgede** | `Walgede` | Town founded 1147. Realigned to authentic pre-Slavic Finno-Ugric/Vepsian hydronym Walgede. |

---

## 3. The Imperial Dynasty: House Châtenois / Kestenholz (ID 1582)

### 3.1 Etymological Background & Linguistic Sound Laws
* **Vanilla / Save Name:** `dynn_Chatenois` (*Chatenois*)
* **Etymological Origin:** From Gallo-Romance / Old French *Chastenois* / *Châtenois*, deriving from Latin **Castinetum** (*castanea* 'chestnut' + collective suffix *-etum*, meaning 'chestnut grove' or 'chestnut woods').
* **Historical Germanic Exonym:** In Alsace and Lorraine, toponyms named *Châtenois* (such as Châtenois in Bas-Rhin and Châtenois in Vosges) have been historically and consistently rendered in German as **Kestenholz** (Middle High German *kestene* / *kesten* 'chestnut' + *holz* 'wood / grove').
* **Tarraconian Sound Laws (MHG / Rhine-Moselle Franconian):**
  * Retains unshifted initial `k-` (`Kesten-`).
  * Preserves Middle High German affricate `-z` `[ts]` in `-holz`.
  * Under the Romano-Germanic imperial synthesis of the Tarraconian Chancellery, the authentic imperial Germanic name for House Châtenois is **House Kestenholz** (*Dat Hûs van Kestenholz*).

### 3.2 Master Cadet Branch Rename Register (The 50 Houses of House Kestenholz)
Coupled realignments for all 50 cadet houses of the imperial dynasty, sorted by living members count:

| House ID | Current In-Game Name | Phase 1 Baseline Name | Final Realigned Name | Underlying Seat Origin | Living Members | Head of House | Status & Justification |
| :---: | :--- | :--- | :--- | :--- | :---: | :--- | :--- |
| `13928` | **Chatenois-Metz** | `Kestenholz-Metz` | **Kestenholz-Metz** | `b_metz (Metz)` | **1322** | Wernhard (`67256089`) | Realigned to Resolved Pre-867 Seat: Authentic pre-867 Roman Divodurum Mediomatricorum / Metz. Retains Franconian form Kestenholz-Metz. |
| `16791696` | **Chatenois-Saumur** | `Kestenholz-Saumur` | **Kestenholz-Saumur** | `b_saumur (Saumur)` | **98** | Poppo (`194813`) | Realigned to Resolved Pre-867 Seat: Ancient castrum on the Loire (Saumur). Retains Kestenholz-Saumur. |
| `19476` | **Chatenois-Ravenna** | `Kestenholz-Ravenna` | **Kestenholz-Raben** | `b_ravenna (Ravenna)` | **69** | Thietmar (`219528`) | Realigned to Resolved Pre-867 Seat: Ancient Roman imperial capital Ravenna. Adapted via Tarraconian / MHG sound laws to Kestenholz-Raben. |
| `22711` | **dynn_Bluome** | `Kestenholz (dynn_Bluome)` | **Kestenholz (dynn_Bluome)** | `Authentic / Uncoupled` | **63** | Thomas (`16954461`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `18311` | **Chatenois-Annonay** | `Kestenholz-Annonay` | **Kestenholz-Annonay** | `Authentic / Uncoupled` | **59** | Ansgar (`33668348`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `16799240` | **Chatenois-Fécamp** | `Kestenholz-Fécamp` | **Kestenholz-Fécamp** | `Authentic / Uncoupled` | **59** | Rudolf (`198300`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `18122` | **Chatenois-Albret** | `Kestenholz-Albret` | **Kestenholz-Albret** | `Authentic / Uncoupled` | **52** | Udalrich (`67279763`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `16796964` | **Flanders** | `Kestenholz (Flanders)` | **Kestenholz (Flanders)** | `Authentic / Uncoupled` | **45** | Sofie (`16985947`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `16790779` | **Chatenois-Geteina** | `Kestenholz-Geteina` | **Kestenholz-Geteina** | `Authentic / Uncoupled` | **41** | Gunzelin (`67268119`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `50346404` | **Chatenois-Amersfoort** | `Kestenholz-Amersfoort` | **Kestenholz-Utrecht** | `b_utrecht (Utrecht)` | **38** | Emmerich (`207144`) | Realigned to Resolved Pre-867 Seat: Underlying seat Amersfoort (1021) resolves to Roman Traiectum / Episcopal see of Utrecht. |
| `16796344` | **dynn_Carenwall** | `Kestenholz (dynn_Carenwall)` | **Kestenholz (dynn_Carenwall)** | `Authentic / Uncoupled` | **34** | Emund (`100822897`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `50348946` | **Chatenois-Koschmin** | `Kestenholz-Koschmin` | **Kestenholz-Kalisz** | `b_kalisz (Kalisz)` | **31** | Christopher (`33743480`) | Realigned to Resolved Pre-867 Seat: Underlying seat Koschmin (12th-c. town) in Kalisz land resolves to ancient Roman Amber Road emporium Kalisz. |
| `16797465` | **Chatenois-Dillingen** | `Kestenholz-Dillingen` | **Kestenholz-Dillingen** | `Authentic / Uncoupled` | **29** | Burchard (`67218942`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `24384` | **Chatenois-Kammersberg** | `Kestenholz-Kammersberg` | **Kestenholz-Judenburg** | `b_judenburg (Judenburg)` | **29** | Erich (`117529751`) | Realigned to Resolved Pre-867 Seat: Underlying seat Kammersberg (1207 castle in Styria) resolves to ancient Mur valley settlement Judenburg. |
| `19355` | **Chatenois-Pau** | `Kestenholz-Pau` | **Kestenholz-Pau** | `Authentic / Uncoupled` | **28** | Ernst (`230078`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `16798500` | **dynn_Diest** | `Kestenholz (dynn_Diest)` | **Kestenholz (dynn_Diest)** | `Authentic / Uncoupled` | **28** | Hoger (`84027331`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `50347588` | **Chatenois-Hirschberg** | `Kestenholz-Hirschberg` | **Kestenholz-Legnica** | `b_legnica (Legnica)` | **26** | Bruno (`215707`) | Realigned to Resolved Pre-867 Seat: Underlying seat Hirschberg (13th-c. Ostsiedlung in Silesia) resolves to 10th-c. Piast castellan grad Legnica. |
| `16799191` | **Chatenois-Tyddewi** | `Kestenholz-Tyddewi` | **Kestenholz-Tyddewi** | `Authentic / Uncoupled` | **26** | Wilhelm (`16980075`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `33573102` | **Cologne** | `Kestenholz (Cologne)` | **Kestenholz (Cologne)** | `Authentic / Uncoupled` | **21** | Talha (`33714868`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `23583` | **Chatenois-Peiting** | `Kestenholz-Peiting` | **Kestenholz-Altenstadt** | `b_altenstadt (Altenstadt)` | **20** | Kuno (`208492`) | Realigned to Resolved Pre-867 Seat: Underlying seat Peiting (11th-c. Welf castle) resolves to ancient mother settlement Altenstadt an der Schongau. |
| `23237` | **Chatenois-Sennar** | `Kestenholz-Sennar` | **Kestenholz-Sennar** | `Authentic / Uncoupled` | **19** | Leopold (`16957192`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `26275` | **Chatenois-Buthrotum** | `Kestenholz-Buthrotum` | **Kestenholz-Buthrotum** | `b_buthrotum (Butrint)` | **19** | Georg (`211291`) | Realigned to Resolved Pre-867 Seat: Classical Greek/Roman colony Bouthroton. Retains Kestenholz-Buthrotum. |
| `26581` | **Chatenois-Berg** | `Kestenholz-Berg` | **Kestenholz-Kaiserswerth** | `b_kaiserswerth (Kaiserswerth)` | **19** | Wannaqo (`33723564`) | Realigned to Resolved Pre-867 Seat: Underlying seat c_berg (Burg Berge 1077) resolves to Carolingian abbey/palace Kaiserswerth (700/1045). |
| `16796257` | **Chatenois-Swenigorot** | `Kestenholz-Swenigorot` | **Kestenholz-Swenigorot** | `b_zvenyhorod (Zvenyhorod)` | **18** | Adalbero (`16943644`) | Realigned to Resolved Pre-867 Seat: Underlying seat c_lviv was historically resolved from Lemberg (1256) to 10th-c. Zvenyhorod. Coupled and canonized. |
| `16799847` | **dynn_Carenwall** | `Kestenholz (dynn_Carenwall)` | **Kestenholz (dynn_Carenwall)** | `Authentic / Uncoupled` | **18** | Albrecht (`205713`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `25655` | **Chatenois-Terebovl** | `Kestenholz-Terebovl` | **Kestenholz-Terebovl** | `Authentic / Uncoupled` | **16** | Ezzo (`213887`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `16789468` | **Chatenois-Stężyca** | `Kestenholz-Stężyca` | **Kestenholz-Sitzichow** | `b_sieciechow (Sieciechów)` | **15** | Giselbert (`134315524`) | Realigned to Resolved Pre-867 Seat: Underlying seat c_stezyca (attested 1330) resolves to 11th-c. Piast palatine seat Sieciechów. |
| `25132` | **Chatenois-Orléans** | `Kestenholz-Orléans` | **Kestenholz-Orleans** | `b_orleans (Orléans)` | **15** | Siegmund (`167887122`) | Realigned to Resolved Pre-867 Seat: Classical Aurelianum / Orléans. Normalized to Kestenholz-Orleans. |
| `22345` | **Chatenois-Mons** | `Kestenholz-Mons` | **Kestenholz-Bergen** | `b_mons (Mons)` | **14** | Lothar (`202358`) | Realigned to Resolved Pre-867 Seat: Roman Castrilocus / Dutch Bergen in Henegouwen. Adapted to Tarraconian Kestenholz-Bergen. |
| `25175` | **Chatenois-Blasien** | `Kestenholz-Blasien` | **Kestenholz-Blasien** | `Authentic / Uncoupled` | **13** | Adolf (`84058417`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `25659` | **Chatenois-Mérida** | `Kestenholz-Mérida` | **Kestenholz-Mêrida** | `b_merida (Mérida)` | **13** | Matthias (`203824`) | Realigned to Resolved Pre-867 Seat: Roman capital of Lusitania Emerita Augusta. Adapted to Kestenholz-Mêrida. |
| `20743` | **Flanders** | `Kestenholz (Flanders)` | **Kestenholz (Flanders)** | `Authentic / Uncoupled` | **12** | Clotaire (`117528958`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `24655` | **Chatenois-Plzeň** | `Kestenholz-Plzeň` | **Kestenholz-Plzenec** | `b_plzenec (Stará Plzeň)` | **10** | Albrecht (`84061195`) | Realigned to Resolved Pre-867 Seat: Underlying seat c_plzen (New Plzeň 1295) resolves to 10th-c. Přemyslid castellan hrad Plzenec (976). |
| `25769` | **Chatenois-Bechyně** | `Kestenholz-Bechyně` | **Kestenholz-Bechin** | `b_bechyne (Bechyně)` | **10** | Wiltrud (`16978195`) | Realigned to Resolved Pre-867 Seat: 9th-c. Slavic Přemyslid gord Bechyně. Adapted to Tarraconian Kestenholz-Bechin. |
| `26541` | **Chatenois-Moraca** | `Kestenholz-Moraca` | **Kestenholz-Moraca** | `Authentic / Uncoupled` | **10** | Siegfried (`16978881`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `18111` | **Chatenois-Bremen** | `Kestenholz-Bremen` | **Kestenholz-Bremen** | `b_bremen (Bremen)` | **9** | Siegmund (`67209938`) | Realigned to Resolved Pre-867 Seat: Authentic Carolingian archbishopric Bremen (787). Retains Kestenholz-Bremen. |
| `16802188` | **dynn_Gudensberg** | `Kestenholz (dynn_Gudensberg)` | **Kestenholz (dynn_Gudensberg)** | `Authentic / Uncoupled` | **9** | Liutbert (`100757863`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `33566549` | **Chatenois-Saarbrücken** | `Kestenholz-Saarbrücken` | **Kestenholz-Zant-Arnolt** | `b_arnual (St. Arnual)` | **8** | Romilda (`33785783`) | Realigned to Resolved Pre-867 Seat: Underlying seat c_saarbrucken (Sarabrucca 999) resolves to Merovingian collegiate church St. Arnual (600). |
| `16799007` | **dynn_Verona** | `Kestenholz (dynn_Verona)` | **Kestenholz (dynn_Verona)** | `Authentic / Uncoupled` | **7** | Adalbert (`67203350`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `16802581` | **Chatenois-Vendôme** | `Kestenholz-Vendôme` | **Kestenholz-Vendôme** | `Authentic / Uncoupled` | **7** | Eberhard (`208775`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `24627` | **Chatenois-Zutphen** | `Kestenholz-Zutphen` | **Kestenholz-Zutphen** | `b_zutphen (Zutphen)` | **6** | Viktor (`33760809`) | Realigned to Resolved Pre-867 Seat: 9th-c. comital circular ringwall Suet-venne / Zutphen. Retains Kestenholz-Zutphen. |
| `23892` | **Chatenois-Baht** | `Kestenholz-Baht` | **Kestenholz-Baht** | `Authentic / Uncoupled` | **5** | Ida (`100811024`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `26913` | **Chatenois-Sargans** | `Kestenholz-Sargans` | **Kestenholz-Kûr** | `b_chur (Chur)` | **4** | Hermann (`67206352`) | Realigned to Resolved Pre-867 Seat: Underlying seat Sargans (12th-c. castle) resolves to Roman provincial capital of Curia Raetorum (Chur). |
| `24600` | **Chatenois-Arnedo** | `Kestenholz-Arnedo` | **Kestenholz-Arnedo** | `Authentic / Uncoupled` | **3** | Maria (`16981848`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `16802071` | **dynn_Muhlhausen** | `Kestenholz (dynn_Muhlhausen)` | **Kestenholz (dynn_Muhlhausen)** | `Authentic / Uncoupled` | **3** | Hoger (`232156`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `26976` | **Chatenois-Lecce** | `Kestenholz-Lecce` | **Kestenholz-Lecce** | `b_lecce (Lecce)` | **2** | Berard (`33722727`) | Realigned to Resolved Pre-867 Seat: Ancient Messapian/Roman Lupiae / Lecce. Retains Kestenholz-Lecce. |
| `1582` | **dynn_Chatenois** | `Kestenholz` | **Kestenholz** | `Authentic / Uncoupled` | **0** |  (`None`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `10882` | **House_10882** | `Kestenholz (House_10882)` | **Kestenholz (House_10882)** | `Authentic / Uncoupled` | **0** |  (`None`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `16795120` | **dynn_Montjoie** | `Kestenholz (dynn_Montjoie)` | **Kestenholz (dynn_Montjoie)** | `Authentic / Uncoupled` | **0** |  (`None`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |
| `23605` | **Chatenois-Machynlleth** | `Kestenholz-Machynlleth` | **Kestenholz-Machynlleth** | `Authentic / Uncoupled` | **0** |  (`None`) | Stem Normalized: House name stem normalized to Kestenholz; seat does not require realignment. |

---

## 4. Summary & Implementation Instructions

1. **County Name Localisation Primacy:** In accordance with imperial chancellery directives, **county localizations are revised** (e.g. `c_novogrudok` $\rightarrow$ **`Plîse`**, `c_volkovysk` $\rightarrow$ **`Rôse`**, `c_minsk` $\rightarrow$ **`Mêne`**), while **barony names (`b_*`) remain unaltered** in the map definition.
2. **Dynastic Synchronization:** For characters holding titles in-game, house names can be realigned using the in-game House Customizer, save editing, or mod character flavorization scripts based on the **Realigned House Name** column above.
3. **Pipeline Coupling:** This document is automatically generated by Phase 4 of the Tarraconian Historical Accuracy Audit Pipeline, ensuring permanent containerized synchronization.

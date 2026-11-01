# Anachronistic Counties & Duchies in the 1059 Campaign (`chatenois_867_01_01.ck3`)

* **Campaign Date:** 13 May 1059
* **Scope:** All post-1059 urban/castle foundations and anachronistic *Ostsiedlung* exonyms among the **44 De Jure Kingdoms** (198 Duchies, 830 Counties) that contain at least one county in the **Holy Roman Empire**.
* **Companion Reference:** [hre_de_jure_and_archdioceses_1059.md](file:///C:/Users/siarg/Documents/Projects/Tarraconian/hre_de_jure_and_archdioceses_1059.md)

---

## 1. Methodology & Resolution Framework

Because *Crusader Kings 3* uses a single static map of landed titles spanning 867 to 1453, many counties and duchies bear the names of:
1. **High/Late Medieval Dynastic Castles** (11th–14th c. *Höhenburg* seats such as *Habsburg*, *Hohenzollern*, *Mark*, *Berg*, *Cleves*, *Wirtemberg*, *Schaumberg*).
2. **Planned Princely & Colonial Towns** (12th–14th c. foundations such as *München*, *Innsbruck*, *Karlsruhe*, *Lemberg/Lviv*, *Roslavl*, *Valdai*, *Madeira*).
3. **12th–14th Century *Ostsiedlung* German Exonyms** for West Slavic, Baltic, or Bohemian provinces prior to historical German eastward settlement (or in regions converted directly to **Tarraconian** in the 1050s).

Following your criteria, every anachronistic title is resolved into one of four categories:
- **Category A — Pre-1059 Centre in the Same Geographic Province:** Replaced or anchored by a documented Roman, Carolingian, Ottonian, Slavic, or Early Medieval ecclesiastical/gau centre located within the same geographic county (Section 2).
- **Category B — Pre-1059 Sub-Barony (`b_*`) Inside the County:** Where the nominal county capital is post-1059, but another barony (`b_*`) inside that exact CK3 county was already a thriving pre-1059 settlement or fortified *gord* (Section 3.1).
- **Category C — Geographic or Tribal Etymology (Valid 1059 Candidates):** Where the town itself was chartered after 1059, but its name derives directly from an ancient **hydronym** (river/lake), **topographic/botanical feature**, or **pre-1059 tribal ethnonym** already present in 1059 (Section 3.2).
- **Category D — In-Game Province History & Geographic Toponymy Proposals:** For counties lacking both a pre-1059 urban centre and a geographic/tribal etymology (e.g., personal/dynastic names, uninhabited islands, or late colonial outposts), proposed names are derived from the **in-game history of the province** (holder dynasties, in-game divergent/hybrid cultures, and regional rulers extracted from `gamestate.bin`) alongside **provincial geographic toponymy** (Section 3.3).

---

## 2. Category A: Counties & Duchies Resolved via Pre-1059 Centres in the Same Province

### 2.1 Kingdom of Lotharingia (`k_lotharingia`)

| Title ID | Save Name (1059) | De Jure Duchy | HRE | Anachronism Reason | Pre-1059 Centre(s) in the Same Province |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `d_luxembourg` / `c_luxembourg` | **Luxembourg** | Luxembourg | ✅ | Castle *Lucilinburhuc* acquired by Siegfried of the Ardennes in **963**; comital title *Count of Luxembourg* only adopted under Conrad I (**1083**). | **Echternach** (Abbey founded 698 by St. Willibrord) or **Arlon** (*Orolaunum*) / **Bitburg** (*Beda Vicus*). |
| `d_brabant` | **Brabant** | Brabant | ✅ | *Pagus Bracbatensis* is Carolingian, but the **Landgraviate (1085)** and **Duchy of Brabant (1183)** are post-1059 elevations of the Counts of Louvain. | **Louvain / Leuven** (*Loven*, attested 891) or **Nivelles** (Abbey 640). |
| `c_brussels` | **Brussels** | Brabant | ✅ | *Brosella* attested **966**, fortified *castrum* built c. **979** by Charles of Lower Lorraine; overtook Leuven only in the late 11th–12th c. | **Nivelles** (*Nijvel*, Carolingian abbey & comital centre, 640) or **Anderlecht / Asse** (Roman *vicus*). |
| `c_antwerpen` | **Breda** | Brabant | ✅ | *Breda* first attested **1125**; localized in the save over the older Imperial March of Antwerp. | **Antwerp** (*Antwerpen / Andawerpum*, attested 726, Ottonian margraviate 974) or **Bergen op Zoom**. |
| `d_julich` | **Jülich** | Jülich | ✅ | County of *Julichgau* is Carolingian, but **Duchy of Jülich** was only elevated in **1356** (Margraviate 1336). | **Jülich** (*Juliacum*, Roman *vicus* and Carolingian *Gau* capital, solely as a County/Gau). |
| `c_cleves` | **Cleves** | Jülich | ✅ | County of Cleves established c. **1020–1033** (*Schwanenburg*), rising to prominence in the late 11th c. | **Xanten** (*Ad Sanctos / Colonia Ulpia Traiana*, major Roman & Carolingian collegiate centre) or **Nijmegen** (*Noviomagus*, imperial palace). |
| `c_gelre` | **Geldern** | Gelre | ✅ | County of Gelre only emerged c. **1096** around Geldern castle (Gerard I Flamens). | **Zutphen** (*Zuid-venne*, 9th-c. comital ringwall) or **Roermond / Kessel** (*Castellum Menapiorum* in the Maasgau). |
| `c_berg` | **Berg** | Lower Lorraine | ✅ | Counts of Berg first attested **1077–1101** (*Burg Berge* at Altenberg). | **Kaiserswerth** (*Insula Sancti Suitberti*, monastery 700, imperial palace 1045) or **Deutz** (*Divitia*, Roman fort & abbey 1003) / **Werden** (Abbey 799). |
| `c_mark` | **Mark** | Lower Lorraine | ✅ | *Burg Mark* near Hamm acquired c. **1198**; Counts of the Mark from **1202** (split from Berg-Altena). | **Soest** (*Sosat*, major Ottonian urban centre in Westphalia) or **Dortmund** (*Throtmanni*, royal palace 882) / **Werl** (10th–11th c. comital seat before Altena/Mark). |
| `c_nancy` | **Nancy** | Upper Lorraine (Metz) | ✅ | *Nanciacum* castle founded c. **1070** by Duke Gerard of Lorraine (previously a minor marshland *villa*). | **Lunéville / Lünstadt** (*Lunaris Villa*, `b_blankenberg #Lunstadt`, seat of the County of Lunéville from **995** & Abbey of St-Rémy 999) or **Épinal** (*Spinal*, `b_epinal`, founded c. **980** by Bishop Dietrich I of Metz) / **Salm** (`b_salm`, 1059). |
| `c_nassau` | **Nassau** | Upper Lorraine | ✅ | *Burg Nassau* founded c. **1093** by Dudo of Laurenburg; title *Count of Nassau* first used **1159**. | **Weilburg** (*Wilineburg*, Conradine stronghold & abbey 906) or **Limburg an der Lahn** (910) / **Wetzlar** (*Lahn-gau*). |
| `c_saarbrucken` | **Saarbrücken** | Upper Lorraine | ✅ | *Castellum Sarabrucca* granted to the Bishop of Metz in **999**; **County of Saarbrücken** only created **1080/1118**. | **St. Arnual** (Merovingian collegiate church) or **Tholey** (Abbey 634) / **Blieskastel** (*Bliesgau*). |
| `c_zweibrucken` | **Zweibrücken** | Upper Lorraine | ✅ | *Zweibrücken* castle first attested c. **1170**; County of Zweibrücken created **1182** (partition of Saarbrücken). | **Hornbach** (Carolingian monastery founded 741 by St. Pirmin in the *Bliesgau*). |
| `c_vaud` | **Vaud** | Transjurane Burgundy | ✅ | *Pagus Waldensis* is Carolingian, but the feudal **Barony of Vaud** was created for Savoy in **1285**. | **Lausanne** (*Lousonna*, Episcopal see since the 6th c.) or **Avenches** (*Aventicum*, Roman capital) / **Orbe** (*Urba*, Carolingian royal villa). |
| `c_neuchatel` | **Neuchâtel** | Transjurane Burgundy | ✅ | *Novum Castellum* founded **1011** by King Rudolph III of Burgundy; Lords/Counts of Neuchâtel only emerge late 11th–12th c. | **Saint-Imier** (7th-c. monastery) or **Moutier-Grandval** (Abbey 640). |

---

### 2.2 Kingdom of Bavaria (`k_bavaria`)

| Title ID | Save Name (1059) | De Jure Duchy | HRE | Anachronism Reason | Pre-1059 Centre(s) in the Same Province |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `c_munich` | **Munich** | Bavaria | ✅ | *München* officially founded **1158** (*Augsburger Schied*) by Henry the Lion. | **Freising** (*Frigisinga*, Episcopal see since 739) or **Tegernsee / Schäftlarn** (8th-c. Carolingian abbeys). |
| `c_rothenburg` | **Nürnberg** | Bavaria | ✅ | *Nürnberg* (*Norenberc*) first attested **1050** as a new Salian castle (9 years before save); *Rothenburg ob der Tauber* built **1070/1142**. | **Fürth** (*Furti*, Carolingian royal estate 1007) or **Forchheim** (major Carolingian royal palace, *Pfalz* 805). |
| `c_eschenlohe` | **Eschenlohe** | Bavaria | ✅ | *Burg Eschenlohe* built c. **1150** by the Counts of Eppan; sold to Augsburg 1294. | **Staffelsee** (8th-c. Carolingian island monastery) or **Schäftlarn / Partenkirchen** (*Parthanum*). |
| `c_schaumberg` | **Schaumberg** | Austria | ✅ | *Burg Schaunberg* built c. **1150–1160** by the Edle von Julbach; County of Schaunberg is 12th–14th c. | **Wels** (*Ovilava*, Roman city & Carolingian *Curtis*) or **Linz** (*Lentia*, attested 799) / **Lambach** (Comital seat & abbey 1056). |
| `c_steyr` | **Steyr** | Austria | ✅ | *Styraburg* first attested c. **985**, became main Traungau seat late 11th c. giving its name to Styria (*Steiermark*). | **Enns / Lorch** (*Lauriacum*, major Roman legionary fortress & Early Christian episcopal see) or **Kremsmünster** (Abbey founded 777 by Tassilo III). |
| `c_pitten` | **Pitten** | Austria | ✅ | *Mark Pitten* only established **1043–1050** after Henry III's Hungarian campaigns; *Wiener Neustadt* founded **1194**. | **Neunkirchen** (*Niuwenchirgun*, attested 1094 on older Carolingian *ecclesia*) or **Savaria / Sabaria** frontier (*bucklige Welt*). |
| `c_graz` | **Graz** | Steyermark | ✅ | *Gradec* first attested **1128** under Leopold I of Styria (Ducal capital 1180). | **Hengistburg** (10th–11th c. capital of the Carantanian March / *Mark an der Mur*) or **Judenburg / Leibnitz** (*Flavia Solva*). |
| `c_leoben` | **Leoben** | Steyermark | ✅ | *Liupina* attested 904, planned fortified town moved and founded in **1261** by Ottokar II. | **Göss** (Imperial Abbey founded 1004 by Aribo I in the *Leobental*) or **Bruck an der Mur** (*Prukke*, 860). |
| `c_innsbruck` | **Innsbruck** | Tyrol | ✅ | *Innsbruck* market founded c. **1180** by the Counts of Andechs. | **Wilten** (*Veldidena*, Roman fort & ancient Premonstratensian/monastic settlement on the Inn) or **Säben / Brixen** (*Sabiona*, Episcopal see since the 6th c.). |
| `c_tirol` | **Lienz** | Tyrol | ✅ | *Schloss Tirol* (Meran) built c. **1100**, Counts of Tyrol from **1140**; *Lienz* (*Luenzina* attested c. 1030) became Gorizian comital residence in the 12th c. | **Innichen** (*San Candido / India*, monastery founded 769 by Duke Tassilo III) or **Aguntum** (Roman *municipium* near Lienz). |
| `c_krain` | **Krain** | Istria | ✅ | March of Carniola (*Creina*) severed from Carinthia in **1040**; capital *Ljubljana / Laibach* first attested **1144**. | **Kranj / Krainburg** (*Carnium*, Lombard & Carolingian fortress-capital of the *Mark Krain*). |
| `c_postojna` | **Postojna** | Istria | ✅ | *Postojna (Adelsberg)* castle first attested **1226**. | **Trieste** (*Tergeste*, Roman city & bishopric) or **Hrušica** (*Ad Pirum*, Late Roman alpine claustra fortress). |

---

### 2.3 Kingdom of Germany (`k_east_francia`)

| Title ID | Save Name (1059) | De Jure Duchy | HRE | Anachronism Reason | Pre-1059 Centre(s) in the Same Province |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `c_hesse` | **Marburg** | Hesse | ✅ | *Marburg* castle built c. **1100** by the Gisonen; Landgraviate of Hesse created **1247/1264**. | **Fritzlar** (Monastery & town founded 723 by St. Boniface, royal *Pfalz* 919) or **Amöneburg** (721) / **Kassel** (*Chassalla*, royal court 913). |
| `c_kassel` | **Ziegenhain** | Hesse | ✅ | County of *Ziegenhain* founded **1144** by Gozmar II (Reichenbach branch). | **Hersfeld** (Imperial Abbey founded 769 by Lullus) or **Kassel** (*Chassalla*, attested 913). |
| `c_weimar` | **Schmalkalden** | Thuringia | ✅ | *Schmalkalden* (attested 874) only became a comital/urban Lordship under the Ludovingians & Hennebergs in the **12th–14th c.** | **Weimar** (*Wimares*, seat of the Counts of Weimar-Orlamünde from 949) or **Erfurt** (*Erphesfurt*, Boniface bishopric 742). |
| `c_plauen` | **Vogtland** | Thuringia | ✅ | *Vogtland* named after the Imperial *Vögte* of Weida, Gera, and Plauen appointed c. **1180–1209** (*Plauen* attested 1122). | **Gau Dobna** (Slavic *župa* of *Dobna* centered on the Elster valley) or **Zeitz / Naumburg** frontier. |
| `c_coburg` | **Coburg** | Franconia | ✅ | *Coburg* first attested **1056** (donation to Saalfeld Abbey); town and Henneberg Lordship are **12th–13th c.** | **Bamberg** (*Babenberch*, Imperial bishopric founded 1007) or **Schweinfurt** (*Suuinfurte*, Margraves of Schweinfurt, 10th c.). |
| `c_leiningen` | **Leiningen** | Rhine | ✅ | *Burg Altleiningen* built c. **1100–1110**; Counts of Leiningen first attested **1128**. | **Worms** (*Borbetomagus / Wormatia*, Roman & Salian imperial cathedral city) or **Lorsch** (Imperial Abbey 764) / **Limburg an der Haardt** (Salian abbey 1025). |
| `c_baden` | **Karlsruhe** | Swabia | ✅ | *Karlsruhe* founded in **1715** (Early Modern anachronism); Margraves of Baden adopted title at *Hohenbaden* in **1112**. | **Speyer / Bruchsal** (*Bruchsella*, Ottonian royal palace 976) or **Baden-Baden** (*Aquae Aureliae*, Roman baths in the *Uffgau*). |
| `c_wurtemberg` | **Wirtemberg** | Swabia | ✅ | *Burg Wirtemberg* dedicated **1083** under Conrad of Beutelsbach. | **Esslingen** (*Ezelinga*, attested 777, Ottonian market & mint) or **Cannstatt** (*Condistat*, Roman fort & Carolingian court 746) / **Waiblingen** (Carolingian/Salian royal *Pfalz* 885). |
| `c_zollern` | **Hohenzollern** | Swabia | ✅ | Counts of *Zollern* first attested **1061** (*Wezel und Burchard von Zolorin*). | **Rottweil** (*Arae Flaviae / Rotuvilla*, Roman *municipium* & major Carolingian royal palace in Swabia) or **Hechingen** (attested 786). |
| `c_badenweiler` | **Badenweiler** | Alsace | ✅ | *Burg Baden* at Badenweiler held by the Zähringer from **1122** (Dowry of Clementia of Badenweiler, 1147). | **Breisach** (*Mons Brisiacus*, Roman & Ottonian ducal fortress on the Rhine) or **Sulzburg** (Monastery founded 993 by Birchtilo of the Breisgau). |
| `c_aargau` | **Habsburg** | Currezia | ✅ | *Habichtsburg* founded c. **1020–1030**; Otto II was the first to style himself *Count of Habsburg* in **1090/1108**. | **Windisch** (*Vindonissa*, Roman legionary camp & early bishopric) or **Baden im Aargau** (*Aquae Helveticae*) / **Muri** (Abbey 1027). |
| `c_grisons` | **Grisons** | Currezia | ✅ | *Graubünden / Grisons* ("Grey Leagues") formed in **1367–1471** (Late Medieval confederacy). | **Chur / Churrätien** (*Curia Raetorum*, Roman provincial capital & Episcopal see since 451). |
| `c_ravensburg` | **Ravensburg** | Swabia | ✅ | *Ravensburg* first attested **1088** (transferred Welf seat from Altdorf). | **Altdorf / Weingarten** (Ancestral Swabian Welf seat & abbey since the 9th–10th c.) or **Buchhorn** (Seat of the Udalrichinger Counts of the Linzgau). |
| `c_oldenburg` | **Oldenburg** | Westphalia | ✅ | *Aldenburg* first attested **1108** under Count Egilmar I. | **Wildeshausen** (Saxon collegiate foundation of Waltbert, grandson of Widukind, **851**) or **Rastede** (1059) in the *Ammergau*. |
| `c_ravensberg` | **Ravensberg** | Westphalia | ✅ | *Burg Ravensberg* built c. **1140** by Hermann I of Calvelage. | **Bielefeld / Herford** (Imperial Abbey of **Herford** founded 789) or **Calvelage** (11th-c. comital seat). |
| `c_waldeck` | **Waldeck** | Westphalia | ✅ | *Burg Waldeck* first attested **1120**; Counts of Schwalenberg adopted *Count of Waldeck* in **1180**. | **Korbach** (*Curbechi*, Carolingian royal court attested 980) or **Corvey** (Imperial Abbey 822) in the *Ittergau*. |
| `c_lippe` | **Lippe** | Angria | ✅ | Lords of *Lippe* first attested **1123** (*Bernhardus de Lippe* at Lippstadt). | **Paderborn** (Carolingian imperial palace & Episcopal see founded 799) or **Detmold** (*Theotmalli*, 783). |
| `c_schaumburg` | **Schaumburg** | Angria | ✅ | *Schauenburg* castle founded c. **1100–1110** by Adolf I of Sandersleben. | **Minden** (Episcopal see founded 800 by Charlemagne) or **Bückeburg** (*Bukigau*). |
| `c_hoya` | **Hoya** | Angria | ✅ | County of *Hoya* founded c. **1202** by Count Heinrich I. | **Bücken** (Collegiate church founded **882** by Archbishop Rimbert of Bremen in the *Entergau*) or **Nienburg**. |
| `c_diepholz` | **Diepholz** | Angria | ✅ | Noble Lordship of *Diepholz* first attested **1160** (*Conradus de Diepenholte*). | **Wildeshausen** (*Wigaldinghus*, 851) or **Vechta / Drebber** (*Pagus Derve*, attested 980). |
| `c_bliesgau` | **Bliesgau** | Angria | ✅ | Misplaced map key (`c_bliesgau`) in the Eastphalian Harz / Brunswick region. | **Braunschweig / Brunswik** (Brunonen seat founded 9th–11th c.) or **Goslar** (Imperial Palace founded 1005 by Henry II) / **Halberstadt** (804). |
| `c_dithmarschen` | **Dithmarschen** | Holstein | ✅ | *Thiatmaresgaho* is a genuine 9th-c. Saxon *Gau*, though the autonomous Peasant Republic is **1227–1559**. | **Meldorf** (Mother-church of Dithmarschen founded c. **810–826** by Ansgar; seat of the *Stade* counts). |

---

### 2.4 Kingdoms of Croatia (`k_croatia`), Serbia (`k_serbia`) & Epirus (`k_epirus`)

| Title ID | Save Name (1059) | De Jure Duchy | HRE | Anachronism Reason | Pre-1059 Centre(s) in the Same Province |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `d_ragusa` / `c_ragusa` | **Dubrovnik** | Dubrovnik | ✅ | *Rausa / Ragusa* is 7th-c., while Slavic *Dubrovnik* first appears in the **Charter of Ban Kulin (1189)**; Maritime Republic is post-1358. | **Ragusa** (*Rausa / Epidaurum*, Byzantine/Dalmatian theme city & archbishopric). |
| `c_zagreb` | **Zagreb** | Slavonia | ✅ | *Zagreb* first attested **1094** when King Ladislaus I of Hungary founded the Diocese of Zagreb. | **Sisak** (*Siscia*, Roman capital of *Pannonia Savia*, seat of Duke Ljudevit Posavski in 819–822). |
| `c_pozega` | **Požega** | Slavonia | ❌ | *Castrum de Posega* first attested in *Gesta Hungarorum* (c. **1200**) and papal letters of **1210/1227**. | **Incerum / Vallis Požegana** or nearby **Cibalae (Vinkovci)** / **Brod**. |
| `c_vodica` | **Vodica** | Bosnia | ✅ | *Vodica (Voćin / Vodičevo)* on the Una/Sana first attested c. **1197–1200** under the Babonić family. | **Pset** (*Pesenta*, 10th-c. Croatian *župa* recorded by Constantine Porphyrogenitus in *De Administrando Imperio*) or **Pliva**. |
| `c_donji_kraji` | **Donji Kraji** | Bosnia | ✅ | *Donji Kraji* ("Lower Ends", *Partes Inferiores*) first attested in **1244** charter of King Béla IV. | **Pliva** (*Πλεύα*, 10th-c. *župa* in *DAI*) and **Zemljanik** (*Zemlenyk*). |
| `c_usora` | **Usora** | Usora | ✅ | Banate of *Usora* first attested c. **1225–1236** (Hydronym of the *Usora* River). | **Salines / Soli** (*Σαληνές*, 10th-c. fortified city in *DAI*, modern Tuzla). |
| `c_soli` | **Soli** | Usora | ❌ | **Valid in 1059** (*Σαληνές* in *DAI* c. 950; *Tuzla* is Ottoman post-1463). | **Soli / Salines** (Already historical for 1059). |
| `c_macva` | **Mačva** | Macva | ❌ | Banate of *Mačva (Macsó)* organized by King Béla IV in **1247**. | **Sirmium** (*Srem / Sremska Mitrovica*, Roman imperial capital & 11th-c. Byzantine *Theme of Sirmium*). |
| `c_sumadija` | **Šumadija** | Rashka | ❌ | *Šumadija* ("Woodland") is an Early Modern (**18th–19th c.**) regional name. | **Rudnik / Borač** or **Morava / Braničevo** frontier. |
| `c_arta` | **Arta** | Epirus | ❌ | *Arta* first attested **1082** (Norman siege); capital of the Despotate of Epirus in **1204**. | **Ambracia** (*Ἀμβρακία*, classical/Byzantine name of the same site) or **Nicopolis** (Episcopal metropolis of Old Epirus). |

---

### 2.5 Kingdoms of Italy (`k_italy`), Sicily (`k_sicily`) & Corsica (`k_corsica`)

| Title ID | Save Name (1059) | De Jure Duchy | HRE | Anachronism Reason | Pre-1059 Centre(s) in the Same Province |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `c_cuneo` | **Cuneo** | Piemonte | ✅ | *Cuneo* founded in **1198** as a new free commune against the Marquis of Saluzzo and Bishop of Asti. | **Pedona** (*Borgo San Dalmazzo*, Lombard/Carolingian royal abbey founded c. 614) or **Bredolo** (10th-c. comital seat of the *Comitatus Bredulensis*). |
| `c_monferrato` | **Monferrato** | Piemonte | ✅ | Aleramici March of Montferrat established late **10th c.** (*961–991*), though the fixed capital at *Casale* or *Chivasso* is **12th–15th c.** | **Acqui** (*Aquae Statiellae*, Roman city & Episcopal see since the 4th c.) or **Vercelli / Asti**. |
| `c_savoie` | **Savoie** | Savoy (`k_burgundy`) | ✅ | *Sapaudia* is Late Roman/Carolingian, but *Chambéry* was only acquired as Savoyard capital in **1232** (Humbert Whitehand titled Count of Maurienne in 1032). | **Saint-Jean-de-Maurienne** (Episcopal see since 575 & original seat of the Humbertines) or **Aiguebelle / Moûtiers** (*Darantasia*, Metropolitan Archbishopric). |
| `c_foggia` | **Foggia** | Apulia | ❌ | *Foggia* first attested c. **1080–1100** under Robert Guiscard; Imperial palace built by Frederick II in **1223**. | **Arpi** (Ancient Daanian city) or **Troia** (Founded **1019** by Byzantine Catepan Basil Boioannes) / **Lucera** (*Luceria*, Roman city & Lombard gastaldate). |
| `c_l_aquila` | **Aquila** | Spoleto | ❌ | *L'Aquila* founded in **1254** by Conrad IV (and refounded 1266 by Charles of Anjou) from 99 older castles. | **Amiternum** (Roman city & early bishopric) or **Forcona** (*Furconium*, Lombard/Frankish Episcopal see until transferred to L'Aquila in 1256). |
| `c_ajaccio` | **Ajaccio** | Corsica | ✅ | Modern *Ajaccio* founded in **1492** by the Genoese *Banco di San Giorgio*, though the Early Christian/Papal see of *Adiacium* is attested by Gregory the Great (**591**). | **Adiacium / Castelvecchio** (Early Medieval bishopric) or **Sagone** (*Sagona*, Episcopal see). |
| `c_vecchio` | **Vecchio** | Corsica | ✅ | *Porto-Vecchio* founded in **1539** by the Genoese Republic. | **Aléria** (Roman provincial capital of Corsica & Early Medieval Episcopal see) or **Bonifacio** (Founded **828** by Marquis Boniface II of Tuscany). |

---

### 2.6 Kingdom of Denmark (`k_denmark`)

| Title ID | Save Name (1059) | De Jure Duchy | HRE | Anachronism Reason | Pre-1059 Centre(s) in the Same Province |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `c_sjaelland` | **København** | Sjælland | ❌ | *Havn* fortified in **1167** by Bishop Absalon (*Køpmannæhafn*). | **Roskilde** (Danish royal seat & Episcopal see since c. **991/1020**) or **Lejre** (Vendel/Viking royal hall). |
| `c_scania` | **Malmö** | Skåne | ❌ | *Malmøghe* founded c. **1250–1275** by the Archbishop of Lund as a fortified ferry/herring port. | **Lund** (Royal mint & Episcopal see founded c. **990** by Sweyn Forkbeard) or **Uppåkra** (Iron Age & Viking Age metropolis of Scania). |

---

### 2.7 Kingdoms of Pomerania (`k_pomerania`), Sorbia (`k_sorbia`), Poland (`k_poland`), Bohemia (`k_bohemia`) & Galicia-Volhynia (`k_galicia-volhynia`)

| Title ID | Save Name (1059) | De Jure Duchy | HRE | Anachronism Reason | Pre-1059 Centre(s) in the Same Province |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `c_rostock` | **Rostock** | Nordmark | ✅ | German Lübeck-law town chartered **1218**; Kissini Slavic *Roztoc* ringwall first burned in **1161** by Valdemar I. | **Kessin** (10th–11th c. capital of the *Kissini* tribe of the Lutici confederation) or **Reric / Dierkow** (8th–9th c. Obodrite emporium). |
| `c_werle` | **Werle** | Nordmark | ✅ | Lordship of *Werle* created **1229** at Güstrow, though the Slavic Obodrite/Wilzi Burgwall *Wurle* on the Warnow is pre-1059. | **Wurle / Burg Werle** (As the pre-1160 Slavic *grad* on the Warnow, or **Teterow** island *grad*). |
| `c_berlin` | **Berlin** | Ostmark | ✅ | *Berlin* (1244) and *Cölln* (1237) founded in the early **13th c.** | ** Köpenick** (*Copnik*, 9th–11th c. capital of the Slavic *Sprewane* tribe) or **Spandau** (10th-c. Hevelli fortress). |
| `c_brandenburg` | **Brandenburg** | Ostmark | ✅ | German Margraviate of Brandenburg founded **1157** by Albert the Bear (after the 983 Slavic uprising). | **Brennabor / Branibor** (Capital of the Hevelli / Stodoranie tribe; temporary Ottonian bishopric 948–983). |
| `c_rupPIN` | **Ruppin** | Ostmark | ✅ | German Lordship of *Ruppin* established c. **1214** by the Counts of Arnstein. | **Altruppin / Zamzizi** (10th–11th c. island *grad* of the Lutician *Zamzizi* tribe on the Ruppiner See). |
| `c_prenzlau` | **Prenzlau** | Ostmark | ✅ | *Prenzlau* first attested **1187** (German town charter 1234). | **Ukranenland / Drense** (9th–11th c. principal fortified *grad* of the Slavic *Ukrani* tribe in the Uckermark). |
| `c_stettin` | **Stettin** | Pomerania | ✅ | German *Stettin* town charter **1243**; prior to 1124 it was a Pomeranian triglav temple-republic. | **Szczecin / Ščečin** (9th–11th c. Pomeranian tribal port & temple-stronghold on the Oder). |
| `c_kolobrzeg` | **Kolberg** | Pomerania | ✅ | German *Kolberg* chartered **1255**. | **Kołobrzeg / Salsa Cholbergiensis** (Pomeranian salt-fortress & Polish diocese founded in **1000** at the Congress of Gniezno). |
| `c_slupsk` | **Stolp** | Pomerania | ✅ | German *Stolp* chartered **1310** under the Margraves of Brandenburg. | **Słupsk /Stłpsk** (9th–11th c. Pomeranian castellan *grad* on the Słupia River). |
| `c_cedynia` | **Zehden** | Pomerania | ✅ | German *Zehden* is 13th-c. *Ostsiedlung*. | **Cedynia / Cidini** (Piast border fortress, site of Mieszko I's Battle of Cidini in **972**). |
| `c_soldin` | **Soldin** | Pomerania | ✅ | *Soldin* founded c. **1260** as capital of the Brandenburgian *Neumark*. | **Myślibórz / Santok** (*Santok*, 10th-c. "Key and Watchtower of the Kingdom" at the Warta-Noteć confluence). |
| `c_landsberg` | **Landsberg** | Lausitz | ✅ | *Landsberg* castle built **1174** by Margrave Dietrich of Wettin. | **Halle / Giebichenstein** (*Givikansten*, 10th-c. Ottonian royal salt-castle on the Saale) or **Merseburg** (968). |
| `c_wittenberg` | **Wittenberg** | Meissen | ✅ | *Wittenberg* first attested **1180** under Bernhard of Anhalt (Ascanian ducal seat). | **Niemegk / Belzig** (*Burgwardium Belizi*, attested **997** under Otto III in the Slavic *Gau Ploni*). |
| `c_dresden` | **Dresden** | Meissen | ✅ | *Dresdene* first attested **1206** under Margrave Dietrich of Meissen. | **Nisan / Dohna** (*Donin*, 10th–11th c. imperial castle & Slavic *župa* of *Nisan* in the Elbe valley) or **Meissen** (Founded 929 by Henry the Fowler). |
| `c_osterland` | **Osterland** | Meissen | ✅ | *Terra Orientalis* (12th c.), centered on *Leipzig* (*Urbs Libzi* attested 1015, chartered c. 1165). | **Zeitz** (Ottonian bishopric founded 968) or **Altenburg** (*Pfalz* 976) / **Groitzsch**. |
| `c_gorlitz` | **Görlitz** | Meissen | ✅ | *Villa Goreliz* first attested **1071** (Henry IV donation to Meissen); town founded c. **1220**. | **Bautzen / Budissin** (*Budusin*, capital of the Slavic *Milceni*, Peace of Bautzen **1018**) or **Landskrone** (Milceni ringwall). |
| `c_cottbus` | **Cottbus** | Lausitz | ✅ | *Chotibuz* castellan attested **1156**. | **Liubusua / Lübbenau** or **Niemitzsch** (*Niempsi*, attested **1000** by Thietmar of Merseburg in Lower Lusatia). |
| `c_sprewa` | **Sprewa** | Lausitz | ✅ | German *Spreewald* naming; 11th-c. Lusatian marchland. | **Köpenick** (*Copnik*, Sprewane seat) or **Jarina / Gehren** (Lusatian *grad* attested 1000). |
| `c_breslau` | **Breslau** | Lower Silesia | ✅ | German *Breslau* chartered **1242/1261** after the Mongol invasion. | **Wrocław / Vratislavia** (Bohemian/Piast stronghold & Episcopal see founded in **1000**). |
| `c_glogau` | **Glogau** | Lower Silesia | ✅ | German *Glogau* chartered **1253**. | **Głogów** (Capital of the Silesian *Dziadoszanie* tribe; besieged by Emperor Henry V in 1109, attested **1010** by Thietmar). |
| `c_legnica` | **Liegnitz** | Lower Silesia | ✅ | German *Liegnitz* chartered **1252**. | **Legnica** (Trzebowianie/Piast castellan *grad* on the Kaczawa, 10th–11th c.). |
| `c_opole` | **Oppeln** | Upper Silesia | ✅ | German *Oppeln* chartered **1217**. | **Opole** (9th–11th c. tribal capital of the Silesian *Opolanie*, attested by the Bavarian Geographer c. 850 as *Opolini*). |
| `c_raciborz` | **Ratibor** | Upper Silesia | ✅ | German *Ratibor* chartered **1217** (first attested **1108** in Gallus Anonymus). | **Racibórz / Golensizi** (Stronghold of the Moravian/Silesian *Golensizi* tribe in the Moravian Gate). |
| `c_bytom` | **Beuthen** | Upper Silesia | ✅ | German *Beuthen* chartered **1254** (castellany attested 1136). | **Bytom** (11th-c. Piast silver-mining settlement) or **Cieszyn** (*Teschen*, 9th–11th c. Golensizi *grad*). |
| `c_katowice` | **Kattowitz** | Upper Silesia | ✅ | *Katowice* first attested **1598** (city 1865 — severe Early Modern anachronism). | **Będzin** (9th–11th c. Vistulan fortified *grad* on the Czarna Przemsza) or **Oświęcim / Siewierz**. |
| `c_lubusz` | **Lebus** | Wielkopolska | ✅ | German *Lebus* ceded to Brandenburg in **1249**. | **Lubusz** (10th–11th c. Piast *grad* of the *Lubuszanie* on the middle Oder). |
| `c_poznan` | **Posen** | Wielkopolska | ✅ | German *Posen* chartered **1253**. | **Poznań** (Primary Piast ducal seat & first Polish missionary bishopric **968**). |
| `c_gniezno` | **Gnesen** | Wielkopolska | ✅ | German *Gnesen* exonym. | **Gniezno** (Piast cradle & Metropolitan Archbishopric founded in **1000**). |
| `c_kalisz` | **Kalisch** | Wielkopolska | ✅ | German *Kalisch* exonym. | **Kalisz** (*Calisia*, ancient Amber Road emporium & 10th–11th c. Piast regional capital). |
| `c_konin` | **Konin** | Wielkopolska | ✅ | *Konin* castellan attested **1136** (town charter 1293). | **Ląd** (9th–11th c. major Piast *grad* on the Warta River) or **Kruszwica** (Legendary Gopło capital of the Goplans). |
| `c_inowroclaw` | **Jungbreslau** | Kuyavia | ✅ | *Inowrocław* ("Young Wrocław") founded c. **1185** (*Jungleslau* under Teutonic Order). | **Kruszwica** (Major 9th–11th c. Kuyavian capital & temporary 11th-c. episcopal see on Lake Gopło). |
| `c_dobrzyn` | **Dobrin** | Kuyavia | ✅ | German *Dobrin* (Order of Dobrzyń founded **1228**; attested 1065 in Mogilno forgery). | **Włocławek** (*Vladislavia*, 10th–11th c. Piast stronghold on the Vistula) or **Płock**. |
| `c_sieradz` | **Schieratz** | Kuyavia | ✅ | German *Schieratz* exonym. | **Sieradz** (11th-c. Piast castellan *grad* on the Warta, attested 1136) or **Łęczyca** (*Tum*, 10th-c. collegiate abbey & *grad*). |
| `c_plock` | **Plock** | Mazovia | ✅ | **Valid in 1059** (10th–11th c. capital of Mazovia under Miecław in 1037–1047; Diocese 1075). | **Płock** (Already historical in 1059). |
| `c_warszawa` | **Warszawa** | Mazovia | ❌ | *Warszawa* founded c. **1300**. | **Czersk** (11th-c. Mazovian ducal stronghold on the Vistula) or **Bródno / Jazdów** (10th–11th c. fortified *grads*). |
| `c_lomza` | **Lomza** | Mazovia | ❌ | Modern *Łomża* moved in the 14th c., though **Stara Łomża** (*Old Łomża* on the Narew) was a flourishing **10th–11th c.** Mazovian *grad*. | **Stara Łomża** or **Wizna** (11th-c. border fortress on the Narew). |
| `c_sandomierz` | **Sandomir** | Lesser Poland | ✅ | Germanized *Sandomir*; Polish *Sandomierz* was one of the three *Sedes Regni Principales* in **1059**. | **Sandomierz** (10th–11th c. Polish provincial capital on the Vistula). |
| `c_radom` | **Radom** | Lesser Poland | ✅ | **Valid in 1059** (*Piotrówka* fortified *grad* in Radom dates to the late **9th–10th c.**). | **Radom** (*Piotrówka*). |
| `c_stezyca` | **Stężyca** | Lesser Poland | ✅ | *Stężyca* first attested **1330**. | **Sieciechów** (11th-c. seat of Palatine Sieciech & Benedictine abbey on the Vistula). |
| `c_lublin` | **Lublin** | Lesser Poland | ❌ | Castellan tower built 12th c., though Old Town Hill (*Czwartek*) had a **6th–11th c.** Lendzian tribal settlement. | **Lublin (Czwartek)** or **Chodlik** (Massive 8th–10th c. Lendzian tribal ringwall in the Lublin Upland). |
| `c_sacz` | **Sącz** | Lesser Poland | ❌ | *Nowy Sącz* founded **1292**, while **Stary Sącz** (*Podchełmie* / *Naszacowice*) was a **9th–11th c.** Vistulan Dunajec valley fortress. | **Stary Sącz / Naszacowice** or **Wojnicz** (10th–11th c. castellan *grad*). |
| `c_przemysl` | **Peremyshl** | Cherven Cities | ✅ | **Valid in 1059** (*Peremyshl* recorded in the *Primary Chronicle* under **981**). | **Peremyshl / Przemyśl** (Already historical in 1059). |
| `c_belz` | **Belz** | Cherven Cities | ✅ | **Valid in 1059** (*Belz* recorded under **1030** when conquered by Yaroslav the Wise). | **Belz** (Already historical in 1059). |
| `c_chelm` | **Chełm** | Cherven Cities | ❌ | *Kholm (Chełm)* founded c. **1237** by Daniel of Galicia. | **Uhrusk / Stołpie** or **Wołyń (Gródek nad Bugiem)** (Capital of the Volhynians in 1018). |
| `c_plzen` | **Eger** | Bohemia | ✅ | *New Plzeň* founded **1295**; German *Eger* (*Pfalz* built 1179 by Barbarossa). | **Stará Plzeň** (*Plzenec*, 10th-c. Přemyslid castellan *hrad* attested **976**) and **Cheb** (Slavic *hrad* of the *Sedličané* from the 9th–10th c., attested 1061). |
| `c_caslav` | **Chrudim** | Bohemia | ✅ | **Valid in 1059** (*Čáslav* was a 10th-c. Slavníkid mint/fortress; *Chrudim* died-at site of Bretislav I in **1055**). | **Čáslav** (*Hrádek*) & **Chrudim** (Both historical in 1059). |
| `c_litomerice` | **Leitmeritz** | Bohemia | ✅ | German *Leitmeritz* chartered **1219**. | **Litoměřice** (10th-c. Přemyslid castle & collegiate chapter founded in **1057** by Spytihněv II). |
| `c_zatec` | **Saaz** | Bohemia | ✅ | German *Saaz* chartered **1265**. | **Žatec** (Capital of the Bohemian *Lučané* tribe; attested **1004** in Thietmar of Merseburg). |
| `c_doudleby` | **Budweis** | Bohemia | ✅ | *Budweis (České Budějovice)* founded in **1265** by King Ottokar II. | **Doudleby** (10th-c. southern Bohemian *hrad* of the *Doudlebané* tribe, attested **981** by Cosmas of Prague). |
| `c_hradec` | **Hradec** | Bohemia | ✅ | **Valid in 1059** (*Hradec Králové* was a 10th-c. Slavníkid and Přemyslid castellan *hrad*, attested 1062). | **Hradec** (*Gradec*, historical in 1059). |
| `c_olomouc` | **Olmütz** | Moravia | ✅ | German *Olmütz* chartered **1240s**. | **Olomouc** (Great Moravian stronghold, Přemyslid apanage capital in **1055**, Bishopric restored 1063). |
| `c_brno` | **Brünn** | Moravia | ✅ | German *Brünn* chartered **1243**. | **Brno** (*Staré Brno*, Přemyslid apanage castle founded c. **1021–1034** by Bretislav I) or **Mikulčice / Veligrad**. |
| `c_znojmo` | **Znaim** | Moravia | ✅ | German *Znaim* chartered **1226**. | **Znojmo** (*Hradiště sv. Hypolita*, 9th-c. Great Moravian fortress & Přemyslid apanage capital **1055**). |
| `c_jihlava` | **Iglau** | Moravia | ✅ | Silver-mining town of *Jihlava / Iglau* founded c. **1240** under King Wenceslaus I. | **Znojmo / Rokytná** (*Rokytná*, 11th-c. Moravian *hrad*) or **Třebíč** (Founded as a Benedictine monastery in 1101 along the old *Habry* path). |

---

### 2.8 Kingdom of Hungary (`k_hungary`)

| Title ID | Save Name (1059) | De Jure Duchy | HRE | Anachronism Reason | Pre-1059 Centre(s) in the Same Province |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `c_pressburg` | **Pressburg** | Nyitra | ✅ | Late Medieval German *Pressburg* form; in 1059 it is the frontier fortress besieged by Emperor Henry III in **1052**. | **Brezalauspurc / Posonium** (*Pozsony / Preslava*, attested **907** at the Battle of Brezalauspurc). |
| `c_trencin` | **Trenčín** | Nyitra | ❌ | **Valid in 1059** (*Laugaricio* in Roman times; 10th–11th c. stone castle of *Trenčín*). | **Trenčín** (*Trencsén*, historical in 1059). |
| `c_gemer` | **Gemer** | Nyitra | ✅ | *Castrum Gumur* first attested **1198** (*Anonymi Gesta Hungarorum*). | **Borsod** (10th–11th c. Hungarian comital earthwork *ispánság*) or **Rimavská / Sajó** valley. |
| `c_orava` | **Orava** | Nyitra | ❌ | *Orava Castle (Árva)* first attested **1267** (built after the 1241 Mongol invasion). | **Vyšný Kubín** (Púchov/Early Slavic hilltop fortresses on the *Orava* River) or **Zvolen / Liptov**. |
| `c_saros` | **Šariš** | Ungvár | ✅ | *Šariš Castle (Sáros)* built in the **13th c.** (first attested **1245**). | **Užhorod (Ungvár)** (9th–11th c. White Croatian & Árpádian comital fortress) or **Zemplín** (10th–11th c. earthwork *ispánság*). |
| `c_marmaros` | **Marmaros** | Transcarpathia | ❌ | *Maramureș (Máramaros)* first attested **1199** as a royal hunting forest; County organized **1303**. | **Bereg / Borsova** (*Boržava*, 10th–11th c. earthwork comital fortress in the Tisza headwaters). |
| `c_szepes` | **Szepes** | Viségrad | ✅ | *Szepes (Spiš) Castle* built in the **12th c.** (first attested **1120/1209**). | **Čingov / Dreveník** (9th–11th c. Slavic fortified hillforts in the Hornád basin). |
| `c_visegrad` | **Viségrad** | Viségrad | ❌ | **Valid in 1059** (9th-c. Slavic fortress on the Danube, made an *ispánság* seat by St. Stephen in **1009**). | **Visegrád** (Already historical in 1059). |
| `c_hewes` | **Heves** | Viségrad | ❌ | **Valid in 1059** (11th-c. *Újvár / Heves* comital seat alongside the **Diocese of Eger** founded c. **1004** by St. Stephen). | **Eger** (*Agria*, Episcopal see 1004) or **Újvár (Abaújvár)** (Founded by King Samuel Aba, r. 1041–1044). |
| `c_borsod` | **Borsod** | Viségrad | ❌ | **Valid in 1059** (10th–11th c. earthwork *ispánság* founded by chieftain *Bors*). | **Borsod** (Already historical in 1059). |
| `c_bacs` | **Bács** | Bács | ❌ | **Valid in 1059** (Founded as an *ispánság* and Suffragan/Archbishopric under St. Stephen I & Ladislaus, 11th c.). | **Bács** (Already historical in 1059). |
| `c_fogaras` | **Fogaras** | Transylvania | ❌ | *Făgăraș (Fogaras)* first attested **1291** (*Terra Fogaras* of the Vlachs). | **Alba Iulia / Gyulafehérvár** (*Bălgrad / Apulum*, 10th-c. seat of the *Gyula* and Bishopric of Transylvania since **1009**). |
| `c_szekelyfold` | **Székelyföld** | Transylvania | ❌ | Székelys settled in eastern Transylvania in the **12th c.** (previously in Bihar/Telegd). | **Küküllő / Târnava** (11th-c. Transylvanian *ispánság*) or **Castrum Sancti Emerici**. |
| `c_beszterce` | **Beszterce** | Transylvania | ❌ | Saxon *Bistritz / Beszterce* chartered **1206–1264** (named after the Slavic *Bistrița* "fast river"). | **Dăbâca (Doboka)** or **Șirioara** (10th–11th c. Transylvanian comital earthwork fortresses). |
| `c_hunyad` | **Fehér** | Transylvania | ❌ | *Hunyad (Hunedoara)* attested 1265, **but the save already displays `Fehér` (*Gyulafehérvár / Alba Iulia*)**, which is completely historical in 1059! | **Fehér / Gyulafehérvár / Bălgrad** (Already resolved in-game). |
| `c_zarand` | **Zaránd** | Bihar | ❌ | **Valid in 1059** (*Zaránd* was one of St. Stephen's original 11th-c. counties around *Zaránd / Maros*). | **Zaránd** or **Csanád** (*Morisena*, Bishopric founded 1030). |
| `c_temes` | **Temes** | Temes | ❌ | *Castrum Temesiensis* first attested **1177** (along the *Timiș / Tibiscus* River). | **Csanád / Morisena** (Seat of Ajtony until 1028; Diocese of Csanád founded **1030** by St. Gerard). |

---

### 2.9 Kingdoms of France (`k_france`) & Burgundy (`k_burgundy`)

| Title ID | Save Name (1059) | De Jure Duchy | HRE | Anachronism Reason | Pre-1059 Centre(s) in the Same Province |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `c_montbeliard` | **Montbéliard** | Upper Burgundy | ✅ | *Mons Biligardi* attested **985**, created as a County by Emperor Conrad II in **1042** for Louis of Mousson (17 years old in 1059). | **Mandeure** (*Epomanduodurum*, Roman city in the *Elsgau / Ajoie*) or **Baume-les-Dames** (5th-c. abbey). |
| `c_clermont` | **Clermont-en-Beauvaisis** | Valois | ❌ | *Clermont* castle first attested **1023** (*Balduinus de Claromonte*). | **Beauvais** (*Caesaromagus / Bellovacum*, Roman capital & powerful Carolingian/Capetian Bishop-County). |
| `c_guines` | **Guînes** | Flanders | ❌ | Motte-and-bailey founded c. **928/965** by Siegfried the Dane; minor fief compared to the ancient maritime capital. | **Thérouanne** (*Tarvenna*, Episcopal see of the Morini since the 7th c.) or **Sithiu / Saint-Omer** (Abbey 651). |

---

### 2.10 Kingdoms of Iberia (`k_spanish_galicia`, `k_castille`, `k_valencia`, `k_andalusia`, `k_badajoz`)

| Title ID | Save Name (1059) | De Jure Duchy | HRE | Anachronism Reason | Pre-1059 Centre(s) in the Same Province |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `c_coruna` | **A Coruña** | Galicia | ✅ | Renamed *Crunia* in **1208** when King Alfonso IX of León refounded the city. | **Faro / Brigantium** (*Burgo de Faro*, the 9th–11th c. Galician name around the Roman Tower of Hercules) or **Iria Flavia / Santiago de Compostela**. |
| `c_burgos` | **Burgos** | Castille | ❌ | Founded in **884** by Count Diego Rodríguez Porcelos (175 years old in 1059 — valid, though secondary to older Roman sees). | **Burgos** (Valid in 1059) or **Oca / Amaya** (Visigothic & early Cantabrian-Castilian episcopal/ducal capitals). |
| `c_valladolid` | **Valladolid** | Castille | ❌ | Repopulated in **1072** by Count Pedro Ansúrez under Alfonso VI. | **Simancas** (*Septimanca*, site of the great Battle of Simancas in **939**) or **Cabezón** on the Pisuerga. |
| `c_soria` | **Soria** | Castille | ❌ | Repopulated in **1109–1119** by Alfonso I the Battler of Aragon. | **Numancia (Garray)** or **Osma** (*Uxama Argaela*, Visigothic Episcopal see & 10th-c. frontier fortress). |
| `c_cuellar` | **Cuéllar** | Castille | ❌ | Repopulated c. **1085–1093** by Count Pedro Ansúrez after the fall of Toledo. | **Sepúlveda** (*Septempublica*, repopulated in **940** by Count Fernán González with its famous *Fuero*). |
| `c_miranda_do_douro` | **Miranda do Douro** | Castille | ❌ | Chartered by King Afonso I of Portugal in **1136** (and King Dinis in **1286**). | **Bragança** (*Brigantia*) or **Caliabria** (Visigothic Episcopal see in the Douro marches). |
| `c_puigcerda` | **Puigcerdà** | Barcelona | ✅ | Founded in **1177** by King Alfonso II of Aragon (moving the Cerdanya capital down from Llívia). | **Llívia** (*Julia Lybica*, Roman *municipium* and capital of the County of Cerdanya until 1177) or **Cuixà** (Abbey 878). |
| `c_albarracin` | **Albarracín** | Valencia | ❌ | **Valid in 1059** (Capital of the Berber *Taifa of Sahla / Banu Razin* from **1012 to 1104**). | **Albarracín / Santa María de Oriente** (Already historical in 1059). |
| `c_castellon` | **Castelló** | Valencia | ✅ | Founded in **1251** by King James I of Aragon (moving the population from the Moorish hill castle of *Fadrell* to the plain). | **Burriana** (*Madinat Burriana*, major 10th–11th c. Andalusi walled city of the *Plana*) or **Sagunto / Murviedro** (*Murbiter*). |
| `c_alarcon` | **Alarcón** | Toledo | ❌ | **Valid in 1059** (Andalusi fortress *al-Arkūn* of the Banu Dhi'l-Nun of Toledo since the 9th–10th c.). | **Alarcón** or **Valeria** (Visigothic Episcopal see adjacent to Alarcón). |
| `c_molina` | **Molina** | Toledo | ❌ | Christian *Señorío de Molina* founded **1138** by Manrique Pérez de Lara, though Moorish *Molina de los Caballeros* existed in the 10th–11th c. | **Ercávica** (Visigothic Episcopal see) or **Medinaceli** (*Madīnat Sālim*, capital of the Middle March). |
| `c_castelo_branco` | **Castelo Branco** | Beja | ❌ | Founded in **1213** by the Knights Templar on the hill of *Cardosa*. | **Idanha-a-Velha** (*Egitania*, Roman city & Visigothic/Suebic Episcopal see). |
| `c_alcacer_do_sal` | **Alcácer do Sal** | Beja | ❌ | **Valid in 1059** (*al-Qaṣr Abī Dānis*, major Umayyad and Aftasid naval port on the Sado; Roman *Salacia*). | **Alcácer do Sal / Salacia** (Already historical in 1059). |
| `c_plasencia` | **Plasencia** | Badajoz | ❌ | Founded in **1186** by King Alfonso VIII of Castile (*"Ut placeat Deo et hominibus"*). | **Coria** (*Caurium*, Roman city, Visigothic Episcopal see, and 10th–11th c. Umayyad/Aftasid fortress *Qūriya*). |
| `c_medellin` | **Medellín** | Badajoz | ❌ | **Valid in 1059** (Roman *Metellinum*, refortified in the 10th c. by the Umayyads on the Guadiana). | **Medellín / Metellinum** (Already historical in 1059). |
| `c_jerez` | **Jerez** | Seville | ❌ | **Valid in 1059** (Andalusi *Šarīš*, flourishing 10th–11th c. cora city; Taifa of Arcos/Jerez). | **Jerez / Šarīš** or **Asidona** (*Medina-Sidonia*, Visigothic Episcopal see & capital of the *Kūra of Sidonia*). |

---

### 2.11 Kingdoms of Maghreb (`k_maghreb`), Tahert (`k_tahert`), Africa (`k_africa`) & Egypt (`k_egypt`)

| Title ID | Save Name (1059) | De Jure Duchy | HRE | Anachronism Reason | Pre-1059 Centre(s) in the Same Province |
| :--- | :--- | :--- | :---: | :--- | :--- |
| `c_marrakesh` | **Marrakesh** | Marrakesh | ❌ | Founded in **1062** or **1070** by Almoravid Amir Abu Bakr ibn Umar / Yusuf ibn Tashfin (3–11 years *after* the save date!). | **Aghmat** (Ancient Haouz commercial metropolis and capital of the Berghouata/Maghrawa prior to Marrakesh) or **Nafis**. |
| `c_rabat` | **Rabat** | Fes | ❌ | Founded as *Ribāṭ al-Fatḥ* in **1150–1191** by the Almohad Caliphs Abd al-Mu'min and Ya'qub al-Mansur. | **Salé / Chellah** (*Šālla*, Roman *Sala Colonia* & 8th–11th c. Idrisid/Ifrenid capital across the Bou Regreg). |
| `c_tinmallal` | **Tinmallal** | Marrakesh | ❌ | Founded c. **1124** by Ibn Tumart as the mountain cradle of the Almohad movement. | **Nafis** (9th–11th c. High Atlas Masmuda capital on the Oued N'fis) or **Igiliz**. |
| `c_taza` | **Taza** | Fes | ❌ | Fortified as a major Almohad stronghold by Abd al-Mu'min in **1142**, though Miknasa Berbers established *Ribāṭ Tāzā* in the **8th–10th c.** | **Taza (Miknasa Ribat)** or **Guercif / Tsoul** (Idrisid corridor towns). |
| `c_algiers` | **Algiers** | Alger | ✅ | Founded in **960** by Buluggin ibn Ziri as *Jazā'ir Banī Mazghanna* on Roman *Icosium* (99 years old in 1059 — valid, though young). | **Algiers / Icosium** (Valid in 1059) or **Rusguniae** (Late Antique Episcopal see at Tamentfoust). |
| `c_bejaia` | **Béjaïa** | Bejaia | ✅ | Refounded as *al-Nāṣiriyya (Bougie)* in **1067** by Hammadid Sultan al-Nasir ibn Alnas (8 years *after* the save date!). | **Qal'at Bani Hammad** (Founded **1007** as the Hammadid royal capital) or **Saldae** (Roman/Late Antique port at Béjaïa) / **M'Sila** (927). |
| `c_orania` | **Oran** | Tlemcen | ✅ | **Valid in 1059** (Founded in **902/903** by Andalusi sailors as *Wahrān*, thriving Fatimid/Umayyad port in 1059). | **Oran / Wahrān** (Valid in 1059) or **Tihert / Tahert** (761). |
| `c_bizerte` | **Benzert** | Tunis | ✅ | **Valid in 1059** (Phoenician/Roman *Hippo Diarrhytus*, Arab *Binzart* since the 7th c.). | **Benzert / Hippo Diarrhytus** (Already historical in 1059). |
| `c_Medjerda` | **Baja** | Tunis | ✅ | **Valid in 1059** (Roman *Vaga*, Aghlabid/Zirid wheat capital *Bāja*). | **Baja / Vaga** (Already historical in 1059). |
| `c_satfura` | **Satfura** | Tunis | ✅ | **Valid in 1059** (*Saṭfūra*, 9th–11th c. Aghlabid/Zirid administrative district of northern Ifriqiya). | **Satfura / Utica** (Already historical in 1059). |
| `c_al_gharbia` | **Mahalla** | Delta | ✅ | *Al-Maḥalla al-Kubrā* only became provincial capital of Gharbia under the Fatimids/Ayyubids in the **late 11th–12th c.** | **Sais** (*Ṣā al-Ḥajar*) or **Xois (Sakha)** / **Busiris (Abu Sir Bana)** (Coptic & Early Islamic capitals of the central Delta). |

---

## 3. Counties Without an Obvious Classical/Early-Medieval Urban Centre: Etymologies, Sub-Baronies & In-Game History Proposals

For the **32 eastern, frontier, and colonial counties** that lack a famous classical or Carolingian city, we extracted their exact **sub-baronies (`b_*`)**, **in-game county cultures (`CultureID`)**, **faiths (`FaithID`)**, and **holder chains (`HistHolders`)** directly from `gamestate.bin`.

### 3.1 Category B: Resolved via Pre-1059 Sub-Baronies (`b_*`) Inside the Same CK3 County

In five Slavic/Rus' counties, the nominal county capital (`c_*`) was founded after 1059, but **another barony (`b_*`) inside that exact CK3 county** was already an active pre-1059 fortified *gord* or trading town:

| County ID & Save Name | De Jure Kingdom | HRE | In-Game County Culture | Sub-Baronies (`b_*`) in Save | Pre-1059 Sub-Barony Resolution |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `c_valdai` (**Valdai**) | Novgorod (`k_novgorod`) | ✅ | **Russian** (`ID 67`) | `b_torzhok`, `b_klichen`, `b_valday`, `b_vyshny_volochyok` | **Torzhok** (`b_torzhok`, *Novy Torg*, 10th–11th c. Novgorodian merchant town on the Tvertsa; *Valdai* village is only attested 1495). *(Note: **Valdai** itself is also a Finnic hydronym/oronym for Lake Valdai & the Valdai Hills).* |
| `c_zvyahel` (**Zvyahel**) | Galicia-Volhynia (`k_galicia-volhynia`) | ✅ | **Ruthenian** (`ID 246`) | `b_zvyahel`, `b_kolodiazhen`, `b_chortolisy`, `b_horodnytsia` | **Kolodiazhen** (`b_kolodiazhen`) or **Horodnytsia** (`b_horodnytsia`) — both are 10th–11th c. Drevlian/Volhynian fortified *gords* on the Sluch River right inside the county (*Zvyahel* is attested 1257). |
| `c_zaslavl` (**Zaslavl**) | Galicia-Volhynia (`k_galicia-volhynia`) | ✅ | **Rutheno-Mogyër** (`ID 295`) | `b_zaslavl`, `b_dubno`, `b_ostroh` | **Dubno** (`b_dubno`, 10th–11th c. Volhynian *gord* on the Ikva, attested 1100) or **Ostroh** (`b_ostroh`, attested 1100 on the Horyn), whereas *Iziaslav / Zaslavl* was founded in the 12th–13th c. |
| `c_lviv` (**Lemberg**) | Galicia-Volhynia (`k_galicia-volhynia`) | ✅ | **Tarraconian** (`ID 316`, promoted 10 Mar 1051) | `b_lviv`, `b_zvenyhorod`, `b_busk`, `b_buchach`, `b_moklekov` | **Zvenyhorod** (`b_zvenyhorod`, 10th–11th c. princely capital before Lviv) or **Busk** (`b_busk`, *Buzhsk* on the Western Bug, attested 1097). *(Note: Held in 1059 by Count `67213373` of **House Chatenois-Lemberg**, `x_nf_5888`, so **Lemberg** is also canonized by the ruling cadet house!).* |
| `c_hradyzk` (**Hradyzk**) | Ruthenia (`k_ruthenia`) | ❌ | **Oskolid** (`ID 292`, Khazar-Mordvin hybrid) | `b_hradyzk`, `b_akhtyr`, `b_myrhorod`, `b_poltava` | **Poltava / Ltava** (`b_poltava`, 8th–10th c. Severian fortified settlement on the Vorskla, attested 1174 as *Ltava*) or **Voin'** (10th-c. Dnieper-Sula fortress), whereas *Hradyzk* is 17th c. |

---

### 3.2 Category C: Geographic & Tribal Etymologies (Retained as Valid 1059 Candidates)

Per your rule, counties whose names derive from **ancient rivers, lakes, mountains, flora/fauna, or pre-1059 tribes** are retained as **valid 1059 candidates**, because the geographic feature or tribe already bore that name in 1059 even if the formal town charter came later:

| County ID & Save Name | De Jure Kingdom | HRE | In-Game County Culture | Sub-Baronies (`b_*`) in Save | Etymological Analysis (Geographic / Tribal Origin) | Status for 1059 |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- |
| `c_opava` (**Opava**) | Moravia (`k_moravia`) | ✅ | **Tarraconian** (`ID 316`, promoted 1058) | `b_opava`, `b_hradec-nad-moravici` | **Hydronym:** Named after the **Opava River** (*Upava*, from Pre-Slavic/Germanic *\*Apa-ahwa* "water-stream"). Also contains pre-1059 barony **Hradec nad Moravicí** (`b_hradec-nad-moravici`, 9th–11th c. Golensizi/Přemyslid castle). | ✅ **Retain (`Opava` / `Troppau` or `Hradec`)** |
| `c_suceava` (**Suceava**) | Moldavia (`k_moldavia`) | ✅ | **Mogyër** (`ID 138`) | `b_suceava`, `b_baia`, `b_vatra_dornei`, `b_campulung_moldovenesc`, `b_siret` | **Hydronym (+ In-Game Mogyër Match!):** *Suceava* is the hydronym of the **Suceava River**, derived from Hungarian *Szucsáva* (*szűcs* "furrier" + Slavic river suffix *-ava*). Remarkably, the county's in-game culture in 1059 is **Mogyër** (`ID 138`), making a Hungarian-derived river name 100% historically consistent in-game! Also contains ancient river/town **Siret** (`b_siret`, classical *Hierasus*). | ✅ **Retain (`Suceava` or `Siret`)** |
| `c_neamnt` (**Neamț**) | Moldavia (`k_moldavia`) | ✅ | **Bugeacian-Mogyër** (`ID 293`) | `b_piatra_neamnt`, `b_targu_neamnt`, `b_roman` | **Tribal/Ethnic Exonym & Hydronym:** From Slavic *Němьcь* ("German / Teuton"), applied both to Germanic/Imperial frontier settlers and to the **Neamț (Ozana) River**. Given that `c_neamnt` is already inside the **Holy Roman Empire** in 1059 and held by House Chatenois-Lemberg, "Land/River of the Germans" (*Neamț*) or **Piatra** ("The Crag", `b_piatra_neamnt`) is remarkably apt! | ✅ **Retain (`Neamț` or `Piatra`)** |
| `c_iasi` (**Iași**) | Moldavia (`k_moldavia`) | ❌ | **Bugeacian-Mogyër** (`ID 293`) | `b_iasi`, `b_ungheni`, `b_falesti` | **Tribal Ethnonym:** Named after the **Jász / Alans / Iazyges** (*As*, Hungarian *Jászok*, Old East Slavic *Jasi*), an Iranian steppe tribe attested along the Prut and Dniester since antiquity and the 10th–11th c. (*Sviatoslav's campaigns against the Yasi in 965*). | ✅ **Retain (`Iași / Jász`)** |
| `c_barlad` (**Bârlad**) | Moldavia (`k_moldavia`) | ❌ | **Bugeacian-Mogyër** (`ID 293`) | `b_barlad`, `b_vaslui`, `b_husi` | **Hydronym:** Named after the **Bârlad River** (from Slavic *berlo / barlo* "marshy/muddy stream"). | ✅ **Retain (`Bârlad`)** |
| `c_lapusna` (**Lăpușna**) | Moldavia (`k_moldavia`) | ❌ | **Bugeacian-Mogyër** (`ID 293`) | `b_lapusna`, `b_chisinau` | **Hydronym & Botanical:** Named after the **Lăpușna River** (from Slavic *lopušna* "burdock / butterbur river"). | ✅ **Retain (`Lăpușna`)** |
| `c_tigheci` (**Tigheci**) | Moldavia (`k_moldavia`) | ❌ | **Bugeacian-Mogyër** (`ID 293`) | `b_tigheci`, `b_cahul` | **Topographic / Forest Region:** Named after the **Codrii Tigheciului** (the forested hills of Tigheci in southern Bessarabia, from Slavic *tih-* "quiet/still forest" or Turkic *tigeč*). | ✅ **Retain (`Tigheci`)** |
| `c_ushytsia` (**Ushytsia**) | Galicia-Volhynia (`k_galicia-volhynia`) | ✅ | **Ruthenian** (`ID 246`) | `b_ushytsia`, `b_vinnytsia`, `b_yampil` | **Hydronym:** Named after the **Ushytsia River** (tributary of the Dniester; attested in the *Primary Chronicle* under 1144). | ✅ **Retain (`Ushytsia` or `Bakota`)** |
| `c_chornobyl` (**Chornobyl**) | Ruthenia (`k_ruthenia`) | ✅ | **Ruthenian** (`ID 246`) | `b_chornobyl`, `b_ivankiv`, `b_radynka` | **Botanical / Topographic:** From Old East Slavic *čornobyl'* ("mugwort / black wormwood", *Artemisia vulgaris*), describing the wormwood-covered floodplains at the confluence of the **Pripyat** and **Uzh** rivers (town attested 1193). | ✅ **Retain (`Chornobyl` or `Uzh`)** |
| `c_babruysk` (**Babruiskas**) | White Rus' (`k_white_rus`) | ✅ | **Russian** (`ID 67`) | `b_babruysk`, `b_zhlobin`, `b_kalinkavichy`, `b_rechytsa` | **Hydronym & Faunal:** Named after the **Babruyka River** (from Balto-Slavic *bobr / bebras* "beaver" — "Beaver River"). Also contains Dregovich Dnieper *gord* **Rechytsa** (`b_rechytsa`, "River-place"). | ✅ **Retain (`Babruysk` or `Rechytsa`)** |
| `c_mozhaysk` (**Mozhaysk**) | Vladimir (`k_vladimir`) | ✅ | **Merya** (`ID 221`, Finno-Ugric) | `b_mozhaysk`, `b_lotoshino`, `b_zubstov` | **Hydronym:** Named after the **Mozhayka River** (from Baltic/Finno-Ugric *Mažōjā* "small river", tributary of the Moskva). Matches the county's pre-Slavic **Merya** culture in 1059! | ✅ **Retain (`Mozhaysk`)** |
| `c_odoyev` (**Odoyev**) | Vladimir (`k_vladimir`) | ❌ | **Meshchera** (`ID 222`, Finno-Ugric) | `b_odoyev`, `b_suvorov` | **Topographic:** From Old East Slavic *odoje / udol'* ("valley / river-hollow") along the steep banks of the **Upa River**. | ✅ **Retain (`Odoyev` or `Upa`)** |
| `c_tikhvin` (**Tikhvin**) | Novgorod (`k_novgorod`) | ❌ | **Russian** (`ID 67`) | `b_tikhvin`, `b_kirishi`, `b_borovichi`, `b_svolensk`, `b_pikalyovo` | **Hydronym & Trade Route:** Named after the **Tikhvinka River** (from Finnic/Vepsian *Tihvin* "path/way to the market", the ancient Volga–Baltic portage river). | ✅ **Retain (`Tikhvin`)** |
| `c_sebezh` (**Sebezh**) | Novgorod (`k_novgorod`) | ❌ | **Russo-Lithuanian** (`ID 320`) | `b_sebezh`, `b_nevel`, `b_novorzhev` | **Hydronym:** Named after **Lake Sebezh** (*Sebežas*, ancient Baltic/Finnic lake hydronym on the Polotsk-Pskov border; matches the county's **Russo-Lithuanian** hybrid culture!). | ✅ **Retain (`Sebezh`)** |
| `c_wadan` (**Wadan**) | Anbiya (`k_anbiya`) | ❌ | **Butr** (`ID 19`, Berber) | `b_wadan`, `b_tingi`, `b_shinqiti`, `b_agharaf_road` | **Topographic:** From Arabic/Berber *Wādān* ("Two Wadis / Two Valleys" — the oasis of two valleys in the Adrar plateau; caravan settlement founded 1147). | ✅ **Retain (`Wadan` or `Adrar`)** |

---

### 3.3 Category D: Proposals Based on In-Game Province History (Holders, Cultures) & Geographic Toponymy

For the remaining **12 counties** whose names are personal/patronymic foundations, late fortresses, or uninhabited islands, we examine their **in-game campaign history** (`gamestate.bin`) and **provincial geographic toponymy** to propose fitting 1059 names:

#### 1. `c_madeira` (**Madeira**, Kingdom of Badajoz — **HRE ✅**)
* **Why Anachronistic:** Uninhabited Atlantic archipelago until Portuguese discovery by João Gonçalves Zarco in **1419** (*Ilha da Madeira*, "Island of Wood/Timber").
* **In-Game Province Data (`1059`):**
  * **Barony:** `b_madeira`
  * **In-Game County Culture:** **Guanches** (`ID 21`, Berber-Canarian!)
  * **In-Game Faith:** **Catholic** (`ID 5`)
  * **Holder Chain:** `50474815` (current HRE count), preceded by `17154`, `33609204`, `16828410`, `16893138`, `121738`, `50375099`.
* **Proposed 1059 Names (In-Game History & Toponymy):**
  1. **Classical / Ecclesiastical Name (Latin/Romance):** **`Purpuraria`** (*Insulae Purpurariae*, Pliny the Elder's classical name for the Madeiran/Canarian archipelago) or **`Silmaria / Bosconia`** (Romance calque of "Wooded Island" prior to 15th-c. Portuguese *Madeira*).
  2. **Tarraconian / Imperial Calque:** **`Holtzinsel`** or **`Wâldinsel`** ("Timber/Forest Island", calquing *Materia / Madeira* into High Franconian/Tarraconian).
  3. **In-Game Guanche Substrate Name:** Because the island is inhabited by Catholic **Guanches** (`ID 21`) in your save, a Canarian-Berber island name such as **`Titeroy`** or **`Achinech-Wâld`** reflects its actual in-game Guanche population.

#### 2. `c_galati` (**Galați**, Kingdom of Moldavia — Non-HRE)
* **Why Flagged Initially:** Historically, the town of Galați is first documented in **1445**.
* **In-Game Province Discovery (`1059`):**
  * **Baronies:** `b_galati`, `b_tecuci`, `b_focsani`
  * **In-Game Cultural History:** In your save (`gamestate.bin`), a divergent Vlach culture named **`Galațian`** (*Galațian-Vlachs*, `ID 275`) and **`Bugeacian`** (*Bugeacian-Vlachs*, `ID 288`, plus hybrid **`Bugeacian-Mogyër`**, `ID 293`) **already emerged before 1059**!
* **Proposed 1059 Resolution:**
  1. **In-Game Canonical Name:** **`Galați`** (or **`Bugeac`**) — Because the province already gave birth to the **Galațian** (*Galațian-Vlachs*) culture in your campaign prior to 1059, *Galați* (from Cuman/Pecheneg *Galat* or Slavic *Halyč / Galitch* "Little Halych" on the Danube) is **100% canonical in your save's timeline!**
  2. **Pre-1059 Classical/Byzantine Alternative:** **`Dinogetia`** or **`Siret-Dunăre`** (at the confluence of the Siret, Prut, and Danube).

#### 3. `c_stoenesti` (**Stoenești**, Kingdom of Moldavia — Non-HRE)
* **Why Anachronistic:** *Stoenești* is a late patronymic village name ("descendants of *Stoian*").
* **In-Game Province Data (`1059`):**
  * **Baronies:** `b_stoenesti`, `b_bacau` (**Bacău**)
  * **In-Game County Culture:** **`Galațian`** (*Galațian-Vlachs*, `ID 275`)
* **Proposed 1059 Names (In-Game History & Toponymy):**
  1. **Geographic Toponymy (Rivers):** **`Trotuș`** (*Tatroș*) or **`Bistrița-Siret`** — The county covers the strategic **Trotuș** and lower **Bistrița** valleys flowing into the Siret across the Eastern Carpathian passes.
  2. **Sub-Barony / Mogyër-Vlach Frontier Name:** **`Bacău`** (`b_bacau`, from personal/Cuman-Hungarian *Bako* at the Bistrița-Siret confluence).

#### 4. `c_dorohoi` (**Dorohoi**, Kingdom of Moldavia — **HRE ✅**)
* **Why Anachronistic:** *Dorohoi* is first attested in **1407** (from Slavic personal name *Dorog-* or *doroga* "road/way").
* **In-Game Province Data (`1059`):**
  * **Baronies:** `b_dorohoi`, `b_harlau` (**Hârlău**)
  * **In-Game County Culture:** **`Bugeacian-Mogyër`** (`ID 293`, Catholic)
  * **Holder History:** Held in history by `67213373` (**House Chatenois-Lemberg**, `x_nf_5888`), currently held by `12583`.
* **Proposed 1059 Names (In-Game History & Toponymy):**
  1. **Geographic Toponymy (River):** **`Jijia`** (or **`Prut-Jijia`**) — The county sits along the upper **Jijia River** and **Prut River** basin.
  2. **In-Game Culture (`Bugeacian-Mogyër`) / Sub-Barony:** **`Hârlău`** (`b_harlau`, from Hungarian *Harló* / Slavic *Horlovo* on the Bahlui) or **`Codrii Jijiei`**.

#### 5. `c_orhei` (**Orhei**, Kingdom of Moldavia — Non-HRE)
* **Why Anachronistic:** *Orhei* derives from Hungarian *Örhely / Várhely* ("watch-post / castle-site", a 13th–14th c. frontier fortification name).
* **In-Game Province Data (`1059`):**
  * **Baronies:** `b_orhei`, `b_tuzara` (**Tuzara**)
  * **In-Game County Culture:** **Russian** (`ID 67`, Tivertsi/East Slavic!)
* **Proposed 1059 Names (In-Game History & Toponymy):**
  1. **Pre-1059 Slavic *Gord* in the Province:** **`Echimăuți`** or **`Alcedar`** — Major 9th–11th c. Tivertsi Slavic fortified *gords* right in the Orhei/Rezina district, matching the county's **Russian** (`ID 67`) culture in 1059!
  2. **Geographic Toponymy (River):** **`Răut`** (*Reut River*, the main river carving the limestone canyon of Orheiul Vechi).
  3. **In-Game Neighboring Mogyër Hybrid Influence:** Retain **`Várhely / Orhei`** as a Mogyër-Slavic frontier watchpost name (since neighboring counties are *Bugeacian-Mogyër*).

#### 6. `c_soroca` (**Soroca**, Kingdom of Moldavia — Non-HRE)
* **Why Anachronistic:** *Soroca* fortress was built by Stephen the Great in **1499** (literally Slavic *soroka* "magpie").
* **In-Game Province Data (`1059`):**
  * **Baronies:** `b_soroca`, `b_balti` (**Bălți**)
  * **In-Game County Culture:** **Russian** (`ID 67`)
* **Proposed 1059 Names (In-Game History & Toponymy):**
  1. **Pre-1059 Tivertsi *Gord* in the Province:** **`udič / Рудь (Rudi)`** — Site of the 9th–11th c. Tivertsi circular earthwork fortress (*Farfuria Turcească*, "Turkish Plate") on the Dniester in Soroca district.
  2. **Geographic Toponymy:** **`Nistru (Dniester)`** / **`Porohy Nistru`** (the Dniester rapids at Yampil–Soroca) or **`Bălți`** (`b_balti`, "The Marshes/Fens" of the Răut).

#### 7. `c_roslavl` (**Roslavl**, Kingdom of White Rus' — **HRE ✅**)
* **Why Anachronistic:** Founded in **1137** by **Prince Rostislav Mstislavich of Smolensk** and named personally after him (*Rostislavl'* $\rightarrow$ *Roslavl*).
* **In-Game Province Data (`1059`):**
  * **Baronies:** `b_roslavl`, `b_klimavichy` (**Klimavichy**), `b_cherykaw` (**Cherykaw**)
  * **In-Game County Culture:** **Ruthenian** (`ID 246`, Catholic)
  * **Holder Chain:** `50485673` (current HRE count), `67157098`, `85955`, `50469185`, `50384626`.
* **Proposed 1059 Names (In-Game History & Toponymy):**
  1. **Geographic Toponymy (Rivers):** **`Oster`** (*Ostr'*, the **Oster River** on which Roslavl stands) or **`Sozh`** (the **Sozh River** flowing through `b_cherykaw`).
  2. **Tribal / Sub-Barony Name:** **`Radimichi`** (core territory of the East Slavic *Radimich* tribe conquered in 984 on the Sozh/Pishchana) or **`Cherykaw`** (`b_cherykaw` on the Sozh).

#### 8. `c_tindouf` (**Tindouf**, Kingdom of Anbiya — Non-HRE)
* **Why Anachronistic:** Modern town of *Tindouf* was founded as a Tajakant Saharan oasis *ksar* in **1852** (though its name is Berber *Tin-Duf*, "Well/Mound of Duf").
* **In-Game Province Data (`1059`):**
  * **Baronies:** `b_tindouf`, `b_tindouf_road`, `b_iguidi_west` (**West Iguidi**)
  * **In-Game County Culture:** **Butr** (`ID 19`, Sanhaja/Zanata Berber)
* **Proposed 1059 Names (In-Game History & Toponymy):**
  1. **Geographic Toponymy (Sub-Barony):** **`Iguidi`** (`b_iguidi_west`, the great **Erg Iguidi** Saharan dune sea and trans-Saharan caravan corridor).
  2. **Berber Topographic Name:** **`Hamada du Draa`** / **`Tin-Duf`** (understood strictly as the ancient Berber desert well *Tin-Duf* on the Draa–Taghaza salt road rather than the 1852 town).

#### 9 & 10. `c_kassala` (**Kassala**, Non-HRE) & `c_showak` (**Showak**, **HRE ✅**), Kingdom of Abyssinia
* **Why Anachronistic:** *Kassala* was founded in **1840** as an Ottoman-Egyptian military camp (though named after the ancient granite domes of **Jebel Taka / Jebel Kassala**); *Showak* is a modern Atbara river crossing town.
* **In-Game Province Data (`1059`):**
  * **`c_kassala` Baronies:** `b_kassala`, `b_middle_atbara` (**Middle Atbara**), `b_to_lus` (**To Lus**)
  * **`c_showak` Baronies:** `b_showak`, `b_gash` (**Gash**), `b_showak_south`
  * **In-Game County Culture (`1059`):** **Ethiopian** (`ID 62`, Catholic in `c_showak`)
* **Proposed 1059 Names (In-Game History & Toponymy):**
  1. **For `c_kassala`:** **`Taka`** (the medieval Beja/Sudanese region of *al-Tāka* recorded by Arab geographers around Jebel Taka), **`Atbara / Astaboras`** (`b_middle_atbara`, the classical & Aksumite name of the Atbara River), or **`To-Lus`** (`b_to_lus`, Beja name).
  2. **For `c_showak` (HRE):** **`Mareb / Gash`** (`b_gash`, the **Mareb / Gash River**, matching the county's **Ethiopian** culture in 1059!) or **`Upper Atbara`** (*Astaboras Superior*).

---

## 4. Summary Cheat-Sheet for Tarraconian Title Translation

When we proceed to translating the 44 Kingdoms, 198 Duchies, and 830 Counties into **Tarraconian**, we can apply the following clean rule-set to all anachronistic entries:
1. ***Ostsiedlung* German Exonyms (Category A.7):** Since Tarraconian *is* a High Franconian-rooted Imperial language (`name_list_franconian`), West Slavic and Bohemian/Polish titles inside the HRE naturally undergo **Tarraconian sound-changes** directly from their authentic 1059 Slavic/Latin stems (or pre-1059 *Gau*/*grad* centres like *Brennabor*, *Kessin*, *Kruszwica*, *Stará Plzeň*, *Doudleby*, *Hradec*).
2. **Post-1059 Dynastic Castles & Towns with Pre-1059 Centres (Categories A & B):** Use either the **pre-1059 provincial centre** (e.g., *Freising* for Munich, *Wilten/Brixen* for Innsbruck, *Enns/Lorch* for Steyr, *Sisak* for Zagreb, *Roskilde* for København, *Lund* for Malmö, *Aghmat* for Marrakesh, *Salé* for Rabat, *Torzhok* for Valdai, *Zvenyhorod/Busk* for Lemberg, *Kolodiazhen* for Zvyahel, *Dubno* for Zaslavl, *Ltava* for Hradyzk) **or**, where an in-game dynasty has already canonized the name by 1059 (such as **House Chatenois-Lemberg** in `c_lviv` or **Galațian** culture in `c_galati`), preserve the in-game canonical form.
3. **Geographic & Tribal Etymologies (Category C):** Retain hydronyms, landforms, and tribal names (*Opava*, *Suceava*, *Neamț*, *Iași*, *Bârlad*, *Lăpușna*, *Tigheci*, *Ushytsia*, *Chornobyl*, *Babruysk*, *Mozhaysk*, *Odoyev*, *Tikhvin*, *Sebezh*, *Wadan*) and adapt them phonologically into Tarraconian.
4. **Unresolved Colonial / Personal Names (Category D):** Use the provincial river/topographic or in-game cultural proposals (*Purpuraria / Holtzinsel* for Madeira, *Trotuș / Bacău* for Stoenești, *Jijia / Hârlău* for Dorohoi, *Răut / Echimăuți* for Orhei, *Nistru / Rudi* for Soroca, *Oster / Radimichi* for Roslavl, *Iguidi* for Tindouf, *Taka / Atbara* for Kassala, and *Mareb / Gash* for Showak).

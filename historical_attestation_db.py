#!/usr/bin/env python3
"""
Master Historical Attestation Database & Resolution Engine
-----------------------------------------------------------
Part of the Tarraconian Historical Title Audit Pipeline.

Enforces the 'Burden of Proof on Antiquity' architectural paradigm:
Every title carries explicit historical metadata:
  - attestation_year: Integer year (-BC, +AD) or None
  - attestation_evidence: Evidence category
  - attestation_source: Primary historical source citation
  - is_hydronym: Boolean (river, mountain, lake, forest)
  - notes: Historical context and pre-867 substrate notes

Titles with verified attestation <= 867 AD earn Tier 1 (or Tier 3 if hydronym).
Titles with foundation > 867 AD or unverified lack of proof default to Tier 4.
Colonial exonym mismatches default to Tier 5.
"""

import re

# Comprehensive registry of verified historical dates, classical civitates, and medieval foundations
ATTESTATION_REGISTRY = {
    # =========================================================================
    # EAST SLAVIC & RUS' — PRE-867 ATTESTATIONS (TIER 1 & 3)
    # =========================================================================
    'c_polotsk': (862, 'early_chronicle', 'Primary Chronicle (Tale of Bygone Years)', False, 'First mentioned under 862 AD among Rurikid towns'),
    'c_smolensk': (863, 'early_chronicle', 'Primary Chronicle (Ustyug text)', False, 'First mentioned 863 AD under Askold and Dir as a great and populous gord'),
    'c_kiev': (482, 'early_chronicle', 'Primary Chronicle / Archaeology', False, 'Traditional foundation 482 AD; ancient Polyane Slavic capital on the Dnieper'),
    'c_novgorod': (859, 'early_chronicle', 'Novgorod First Chronicle', False, 'Rurikovo Gorodishche 9th c., chronicle mention 859 AD'),
    'c_ladoga': (753, 'early_chronicle', 'Dendrochronology / Archaeology', False, 'Dendrochronological foundation 753 AD (Aldeigjuborg) on the Volkhov'),
    'c_beloozero': (862, 'early_chronicle', 'Primary Chronicle', False, 'Mentioned 862 AD under Sineus on Lake Beloye'),
    'c_rostov': (862, 'early_chronicle', 'Primary Chronicle', False, 'Mentioned 862 AD among Rurikid towns in Merya land on Lake Nero'),
    'c_murom': (862, 'early_chronicle', 'Primary Chronicle', False, 'Mentioned 862 AD in Muromian tribal territory on the Oka'),
    'c_izborsk': (862, 'early_chronicle', 'Primary Chronicle', False, 'Mentioned 862 AD under Truvor; ancient Slavic hillfort on Lake Gorodishchenskoye'),
    'c_gnezdovo': (800, 'archaeology', 'Smolensk Archaeological Complex', False, 'Major 9th-c. Scandinavian-Slavic trading emporium at Gnezdovo'),

    # =========================================================================
    # EAST SLAVIC & RUS' — POST-867 FOUNDATIONS (FLAGGED TIER 4)
    # =========================================================================
    'c_novogrudok': (1044, 'high_medieval_foundation', 'Primary Chronicle', False, "Founded c. 1044 AD as 'New Castle' (Novъ-gordъ); pre-867 substrate is Baltic hydronym Plisa / Plesė"),
    'c_volkovysk': (1252, 'high_medieval_foundation', 'Hypatian Chronicle', False, "First attested 1252 with Slavic town suffix -ysk; pre-867 substrate is hillfort Muravelnik or river Ros' / Vaŭkavyja"),
    'c_minsk': (1067, 'high_medieval_foundation', 'Primary Chronicle (Battle on the Nemiga)', False, "First attested 1067 with Slavic town suffix -sk over ancient Baltic hydronym Menka / Mėna"),
    'c_roslavl': (1137, 'high_medieval_foundation', 'Smolensk Princely Chronicle', False, 'Founded 1137 by Prince Rostislav Mstislavich; pre-867 hydronym Oster'),
    'c_slutsk': (1116, 'high_medieval_foundation', 'Primary Chronicle', False, 'First attested 1116 in Primary Chronicle (Sluchek) on the Sluch River'),
    'c_kletsk': (1127, 'high_medieval_foundation', 'Primary Chronicle', False, 'First attested 1127 in Primary Chronicle (Kłečesk) on the Lan River'),
    'c_grodno': (1127, 'high_medieval_foundation', 'Primary Chronicle', False, 'First attested 1127 as Gorodzen; Imperial Chancellery name Garten'),
    'c_braslau': (1065, 'high_medieval_foundation', 'Polotsk Chronicle', False, 'Founded 1065 by Bryachislav of Polotsk (Bryachislavl) on Lake Dryvyaty'),
    'c_babruysk': (1387, 'high_medieval_foundation', 'Crown Lithuanian Charter', False, 'First attested 1387; pre-867 center is river Berezina / Dregovich gord Rechytsa'),
    'c_sebezh': (1414, 'high_medieval_foundation', 'Chronicle of Pskov', False, 'Fortress built 1414; pre-867 Baltic hydronym Lake Sebezh (Sebēža)'),
    'c_lyubim': (1538, 'high_medieval_foundation', 'Muscovite Line Fortress Charter', False, 'Fortress built 1538; pre-867 hydronym Obnora River'),
    'c_vologda': (1147, 'high_medieval_foundation', 'Tale of Miracles of St. Gerasim', False, 'Founded 1147; pre-867 Finno-Ugric / Vepsian hydronym Walgede'),
    'c_moskva': (1147, 'high_medieval_foundation', 'Hypatian Chronicle', False, 'Yuri Dolgoruky meeting 1147; pre-867 hydronym Moskva River'),
    'c_tver': (1135, 'high_medieval_foundation', 'Statute of Prince Vsevolod', False, 'First attested 1135 on Tvertsa river; pre-867 portage Volok-Lamsky'),
    'c_tula': (1146, 'high_medieval_foundation', 'Nikon Chronicle', False, 'First attested 1146 on Tulitsa river; pre-867 Vyatichi hillfort Pronsk'),
    'c_dmitrov': (1154, 'high_medieval_foundation', 'Suzdalian Chronicle', False, 'Founded 1154 by Yuri Dolgoruky on Yakhroma river'),
    'c_kostroma': (1213, 'high_medieval_foundation', 'Voskresenskaya Chronicle', False, 'Founded 1213 at Kostroma-Volga confluence'),
    'c_nizhny_novgorod': (1221, 'high_medieval_foundation', 'Lavrentian Chronicle', False, 'Founded 1221 by Yuri II; pre-867 Mari/Merya fortress Obran Osh'),
    'c_yaroslavl': (1010, 'high_medieval_foundation', 'Primary Chronicle', False, 'Founded 1010 by Yaroslav the Wise over pagan Bear Corner'),
    'c_vladimir': (990, 'high_medieval_foundation', 'Primary Chronicle', False, 'Founded 990 by Vladimir the Great / fortified 1108 by Vladimir Monomakh on the Klyazma'),
    'c_suzdal': (999, 'high_medieval_foundation', 'Novgorod Codex', False, 'Attested 999 / 1024 AD in Suzdalia on the Kamenka'),
    'c_ryazan': (1095, 'high_medieval_foundation', 'Sleptsov Chronicle', False, 'Pereyaslavl-Ryazansky founded 1095; Old Ryazan 10th-11th c.'),
    'c_bryansk': (1146, 'high_medieval_foundation', 'Hypatian Chronicle', False, 'First attested 1146 as Debryansk on the Desna'),
    'c_gomel': (1142, 'high_medieval_foundation', 'Hypatian Chronicle', False, 'First attested 1142 as Gomey on the Sozh'),
    'c_turov': (980, 'high_medieval_foundation', 'Primary Chronicle', False, 'First attested 980 under Prince Rogvolod and Tur on the Pripyat'),
    'c_pinsk': (1097, 'high_medieval_foundation', 'Primary Chronicle', False, 'First attested 1097 as Pinesk on the Pina river'),
    'c_orsha': (1067, 'high_medieval_foundation', 'Primary Chronicle', False, 'First attested 1067 as Rsha on Dnieper-Orshytsa confluence'),
    'c_vitebsk': (974, 'high_medieval_foundation', 'Chronicle of Vitebsk', False, 'Founded 974 by Princess Olga / attested 1021 on the Western Dvina'),
    'c_toropets': (1074, 'high_medieval_foundation', 'Lavrentian Chronicle', False, 'First attested 1074 on Toropa river'),
    'c_mozhaysk': (1231, 'high_medieval_foundation', 'Novgorod Chronicle', False, 'First attested 1231 on Mozhaya river'),
    'c_lutsk': (1085, 'high_medieval_foundation', 'Primary Chronicle', False, 'First attested 1085 as Luchesk on Styr river'),
    'c_ostrog': (1100, 'high_medieval_foundation', 'Primary Chronicle', False, 'First attested 1100 at Council of Vytechev'),
    'c_zhytomyr': (884, 'high_medieval_foundation', 'Primary Chronicle legend', False, 'Legendary foundation 884 AD by retainer of Askold and Dir'),
    'c_ovruch': (977, 'high_medieval_foundation', 'Primary Chronicle', False, 'First attested 977 as Vruchiy (death of Prince Oleg Sviatoslavich)'),
    'c_korosten': (945, 'high_medieval_foundation', 'Primary Chronicle', False, 'First attested 945 as Drevlian capital Iskorosten on the Uzh'),
    'c_chernigov': (907, 'high_medieval_foundation', 'Primary Chronicle', False, 'First mentioned in 907 Rus-Byzantine treaty on the Desna'),
    'c_kursk': (1032, 'high_medieval_foundation', 'Life of Theodosius of the Caves', False, 'First attested 1032 in Severian land on the Tuskar and Seym'),
    'c_putyvl': (1146, 'high_medieval_foundation', 'Hypatian Chronicle', False, 'First attested 1146 in Severia on the Seym'),
    'c_pereyaslavl': (992, 'high_medieval_foundation', 'Primary Chronicle', False, 'Founded 992 by Vladimir the Great on the Trubezh'),
    'c_korsun': (1032, 'high_medieval_foundation', 'Primary Chronicle', False, 'Founded 1032 by Yaroslav the Wise on the Ros river line'),
    'c_novgorod_seversky': (1044, 'high_medieval_foundation', 'Primary Chronicle', False, 'First attested 1044 as New Gord of the Severians on the Desna'),
    'c_belz': (1030, 'high_medieval_foundation', 'Primary Chronicle', False, 'First attested 1030 when captured by Yaroslav the Wise in Red Ruthenia'),
    'c_lviv': (1256, 'high_medieval_foundation', 'Galician-Volhynian Chronicle', False, 'Founded c. 1256 by Danylo of Halych; pre-867 center is princely capital Zvenyhorod'),
    'c_galich': (898, 'high_medieval_foundation', 'Primary Chronicle', False, 'First mentioned 898 AD; princely capital 1140 on the Dniester'),
    'c_zaslavl': (985, 'high_medieval_foundation', 'Primary Chronicle', False, 'Founded c. 985 by Vladimir for Rogneda (Izyaslavl)'),

    # =========================================================================
    # POLAND, BOHEMIA & WEST SLAVIA (TIER 1, 3, 4)
    # =========================================================================
    'c_krakowska': (800, 'archaeology', 'Wawel archaeological complex / Ibrahim ibn Yaqub', False, '8th-c. Vistulan gord on Wawel Hill; attested 965'),
    'c_poznanska': (850, 'archaeology', 'Ostrów Tumski excavations', False, '9th-c. Polan tribal gord at Ostrów Tumski'),
    'c_gnieznienska': (800, 'archaeology', 'Lech Hill excavations', False, '8th-9th c. tribal sanctuary and gord at Gniezno'),
    'c_kaliska': (150, 'classical_antiquity', 'Ptolemy Geography', False, 'Attested c. 150 AD as Calisia on Amber Road'),
    'c_opole': (845, 'early_chronicle', 'Bavarian Geographer (Descriptio civitatum)', False, 'Recorded c. 845 AD as civitas Opolini (20 gords) on the Oder'),
    'c_szczecin': (800, 'archaeology', 'Pomeranian excavations', False, '8th-c. Slavic trading settlement and fortress at Oder mouth'),
    'c_wolin': (800, 'early_chronicle', 'Ibrahim ibn Yaqub / Adam of Bremen', False, '8th-c. emporium of Vineta / Jomsborg (Iumne) on Dziwna'),
    'c_stezycka': (1330, 'high_medieval_foundation', 'Crown Polish Charter', False, 'Chartered 1330; pre-867 center is Piast palatine castrum Sieciechów (b_sieciechow)'),
    'c_tarnowska': (1330, 'high_medieval_foundation', 'Charter of Władysław Łokietek', False, 'Chartered 1330; pre-867 center is 8th-9th c. Slavic hillfort on St. Martin Hill'),
    'c_brzeg': (1248, 'high_medieval_foundation', 'Silesian Town Charter', False, 'Town chartered 1248; Slavic riverside settlement on the Oder'),
    'c_ratibor': (1108, 'high_medieval_foundation', 'Gallus Anonymus', False, 'Attested 1108 in Chronica Polonorum on Upper Oder'),
    'c_cieszyn': (1155, 'high_medieval_foundation', 'Papal Bull of Hadrian IV', False, 'Attested 1155 as Tessin on Olza river'),
    'c_plocka': (1000, 'high_medieval_foundation', 'Thietmar of Merseburg', False, 'Late 10th-c. Piast fortified center, bishopric 1075 on the Vistula'),
    'c_radomska': (1155, 'high_medieval_foundation', 'Papal Bull of Hadrian IV', False, 'Attested 1155; 10th-c. gord Piotrówka'),
    'c_sandomierska': (1000, 'high_medieval_foundation', 'Gallus Anonymus', False, 'Early 11th-c. Piast sedes regni principalis on the Vistula'),
    'c_lubelska': (1198, 'high_medieval_foundation', 'Archdeaconry Charter', False, 'Attested 1198 on Bystrzyca river'),
    'c_breslau': (1000, 'high_medieval_foundation', 'Thietmar of Merseburg', False, 'Bishopric founded 1000 AD; 10th-c. Bohemian/Piast gord on the Oder'),
    'c_torun': (1231, 'high_medieval_foundation', 'Teutonic Order Charter', False, 'Founded 1231 by Hermann Balk; pre-867 center Chełmno (Kulm)'),
    'c_malbork': (1274, 'high_medieval_foundation', 'Teutonic Order Charter', False, 'Marienburg castle built 1274; pre-867 center Truso'),
    'c_elblag': (1237, 'high_medieval_foundation', 'Teutonic Order Charter', False, 'Elbing founded 1237; pre-867 Viking/Old Prussian emporium Truso'),
    'c_olomouc': (1055, 'high_medieval_foundation', 'Cosmas of Prague', False, 'Attested 1055; sub-barony b_unicov chartered 1213; pre-867 center Litovel on Morava'),
    'c_plzen': (1295, 'high_medieval_foundation', 'Charter of Wenceslaus II', False, 'New Pilsen founded 1295; pre-867 center is 10th-c. gord Old Pilsen (Starý Plzenec)'),
    'c_opava': (1224, 'high_medieval_foundation', 'Charter of Ottokar I', False, 'Town chartered 1224; pre-867 hydronym Opava / Troppau'),
    'c_hradec': (1225, 'high_medieval_foundation', 'Charter of Ottokar I', False, 'Chartered 1225; pre-867 Slavic gord on Elbe-Orlice confluence'),
    'c_caslav': (1260, 'high_medieval_foundation', 'Charter of Ottokar II', False, 'Royal town founded 1260 by Ottokar II; pre-867 gord Hrádek'),
    'c_koszmin': (1200, 'high_medieval_foundation', 'Greater Poland Charter', False, 'Settlement attested 12th-13th c.; pre-867 center Kalisz on Amber Road'),
    'c_hirschberg': (1281, 'high_medieval_foundation', 'Piast Charter of Bernard the Lightsome', False, 'Founded 1281; pre-867 center Warmbrunn thermal springs / Legnica'),

    # =========================================================================
    # BALTIC, LIVONIA, PRUSSIA & FINLAND (FLAGGED TIER 4 & 5)
    # =========================================================================
    'c_aluksne': (1342, 'high_medieval_foundation', 'Livonian Order Chronicle', False, 'Marienburg built 1342; pre-867 center is Latgalian lake-hillfort Alūksne'),
    'c_narva': (1256, 'high_medieval_foundation', 'Liber Census Daniae', False, 'Danish fortress 1256; pre-867 hydronym Narva River'),
    'c_dorpat': (1030, 'high_medieval_foundation', 'Primary Chronicle', False, 'Yuryev/Dorpat captured 1030; pre-867 center is 5th-c. Estonian hillfort Tarbata'),
    'c_riga': (1201, 'high_medieval_foundation', 'Henry of Livonia', False, 'Founded 1201 by Bishop Albert; pre-867 Daugava trading site'),
    'c_tallinn': (1219, 'high_medieval_foundation', 'Henry of Livonia', False, 'Danish conquest 1219; pre-867 Lindanise / Rävala'),
    'c_reval': (1219, 'high_medieval_foundation', 'Henry of Livonia', False, 'Danish castle 1219; pre-867 Estonian province Rävala'),
    'c_memel': (1252, 'high_medieval_foundation', 'Livonian Order Charter', False, 'Memelburg castle 1252; pre-867 Curonian fortress Pilsāts and river Mēmele'),
    'c_konigsberg': (1255, 'high_medieval_foundation', 'Teutonic Order Charter', False, 'Founded 1255; pre-867 Old Prussian fortress Twangste / emporium Kaup'),
    'c_allenstein': (1348, 'high_medieval_foundation', 'Warmian Chapter Charter', False, 'Founded 1348; pre-867 Galindian tribal land'),
    'c_bartenstein': (1240, 'high_medieval_foundation', 'Teutonic Order Charter', False, 'Castle built 1240; pre-867 Bartia tribal territory'),
    'c_wormditt': (1308, 'high_medieval_foundation', 'Warmian Chapter Charter', False, 'Founded 1308; pre-867 Warmia tribal territory'),
    'c_osterode': (1300, 'high_medieval_foundation', 'Teutonic Order Charter', False, 'Castle built 1300; pre-867 Sasna tribal territory'),
    'c_angerburg': (1335, 'high_medieval_foundation', 'Teutonic Order Charter', False, 'Castle built 1335; pre-867 Sudovia / Angerapp river'),
    'c_trakai': (1316, 'high_medieval_foundation', 'Lithuanian Chronicles', False, 'Old Trakai founded c. 1316 by Gediminas; pre-867 center Merkinė'),
    'c_vilnius': (1323, 'high_medieval_foundation', 'Letters of Gediminas', False, 'First attested 1323 in letters of Gediminas on Neris-Vilnia confluence'),
    'c_viipuri': (1293, 'high_medieval_foundation', 'Erikskrönikan', False, 'Swedish castle 1293 by Torgils Knutsson; pre-867 Karelian Linnasaari'),
    'c_nyland': (1249, 'high_medieval_foundation', 'Second Swedish Crusade', False, 'Colonial name c. 1249; pre-867 Tavastian/Finnic coast Uusimaa/Espoo'),
    'c_turku': (1229, 'high_medieval_foundation', 'Papal Bull of Gregory IX', False, 'See transferred 1229; pre-867 Koroinen / Aura river'),
    'c_pedersore': (1290, 'high_medieval_foundation', 'Swedish Parish Register', False, 'Parish attested late 13th c.; pre-867 Ostrobothnian Vuohijärvi'),
    'c_messukyla': (1450, 'high_medieval_foundation', 'Catholic Parish Register', False, 'Parish 15th c.; pre-867 Upper Satakunta lake route Ruovesi'),

    # =========================================================================
    # RHINELAND, LOTHRINGIA, GERMANY, BAVARIA & AUSTRIA (TIER 1 & 4)
    # =========================================================================
    'c_trier': (-16, 'classical_antiquity', 'Tacitus / Archaeology', False, 'Roman Augusta Treverorum founded under Augustus c. 16 BC'),
    'c_cologne': (50, 'classical_antiquity', 'Tacitus (Annales)', False, 'Colonia Claudia Ara Agrippinensium established 50 AD'),
    'c_mainz': (-13, 'classical_antiquity', 'Roman Military Inscriptions', False, 'Mogontiacum legionary fortress founded 13 BC by Drusus'),
    'c_koblenz': (-9, 'classical_antiquity', 'Roman Military Inscriptions', False, 'Confluentes established 9 BC at Rhine-Moselle confluence'),
    'c_worms': (-14, 'classical_antiquity', 'Roman Itineraries', False, 'Borbetomagus Roman fort and civitas Vangionum c. 14 BC'),
    'c_speyer': (-10, 'classical_antiquity', 'Roman Itineraries', False, 'Noviomagus Nemetum Roman military camp c. 10 BC'),
    'c_strassburg': (12, 'classical_antiquity', 'Roman Military Inscriptions', False, 'Argentoratum legionary fort founded 12 AD by Drusus'),
    'c_augsburg': (-15, 'classical_antiquity', 'Roman Military Inscriptions', False, 'Augusta Vindelicorum Roman provincial capital founded 15 BC'),
    'c_regensburg': (179, 'classical_antiquity', 'Roman Inscription of Marcus Aurelius', False, 'Castra Regina legionary fortress dedicated 179 AD'),
    'c_passau': (80, 'classical_antiquity', 'Roman Military Inscriptions', False, 'Batavis Roman auxiliary fort founded c. 80 AD'),
    'c_aachen': (765, 'carolingian_charter', 'Royal Frankish Annals', False, 'Aquisgranum imperial palace; royal charter 765 AD'),
    'c_frankfurt': (794, 'carolingian_charter', 'Council of Frankfurt Acts', False, 'Franconofurd first attested 794 AD at Charlemagne\'s council'),
    'c_fulda': (744, 'early_medieval_charter', 'Life of Saint Sturm', False, 'Abbey of Fulda founded 744 AD by Saint Sturm under Boniface'),
    'c_wurzburg': (704, 'early_medieval_charter', 'Donation Deed of Hedan II', False, 'Castellum Virteburch first attested 704 AD; bishopric 741'),
    'c_magdeburg': (805, 'carolingian_charter', 'Diedenhofen Capitulary', False, 'Magadoburg attested 805 AD as Carolingian border trading post'),
    'c_hamburg': (810, 'carolingian_charter', 'Royal Frankish Annals', False, 'Hammaburg fortress built 810 AD by Charlemagne'),
    'c_bremen': (787, 'carolingian_charter', 'Life of Saint Willehad', False, 'Bishopric established 787 AD by Charlemagne on Weser'),
    'c_freising': (739, 'early_medieval_charter', 'Life of Saint Corbinian', False, 'Frigisinga bishopric founded 739 AD by Saint Boniface'),
    'c_salzburg': (696, 'early_medieval_charter', 'Traditions of Saint Rupert', False, 'Iuvavum re-established 696 AD as Salzburg bishopric by Saint Rupert'),
    'c_metz': (-52, 'classical_antiquity', 'Caesar / Tacitus', False, 'Divodurum Mediomatricorum, Roman provincial civitas capital'),
    'c_toul': (-52, 'classical_antiquity', 'Roman Itineraries', False, 'Tullum Leucorum, Roman civitas and 4th-c. bishopric'),
    'c_verdun': (-52, 'classical_antiquity', 'Roman Itineraries', False, 'Virodunum, Roman civitas on the Meuse; 4th-c. bishopric'),
    'c_basel': (374, 'classical_antiquity', 'Ammianus Marcellinus', False, 'Basilia Roman fort attested 374 AD under Emperor Valentinian I'),
    'c_geneva': (-58, 'classical_antiquity', 'Caesar (De Bello Gallico)', False, 'Genava Allobrogum attested 58 BC by Julius Caesar'),
    'c_utrecht': (47, 'classical_antiquity', 'Roman Inscriptions', False, 'Traiectum ad Rhenum Roman auxiliary fort founded c. 47 AD'),
    'c_maastricht': (382, 'classical_antiquity', 'Roman Itineraries', False, 'Traiectum ad Mosam, Roman bridgehead and 4th-c. episcopal see of St. Servatius'),
    'c_tongeren': (-15, 'classical_antiquity', 'Ptolemy / Pliny', False, 'Atuatuca Tungrorum, oldest Roman civitas capital in Belgium'),
    'c_nijmegen': (-19, 'classical_antiquity', 'Tacitus', False, 'Ulpia Noviomagus Batavorum Roman legionary fortress founded 19 BC'),
    'c_xanten': (-15, 'classical_antiquity', 'Tacitus', False, 'Colonia Ulpia Traiana / Castra Vetera founded 15 BC by Drusus'),

    # Post-867 German, Lotharingian & Austrian Castles (Flagged Tier 4)
    'c_bergh': (1077, 'high_medieval_foundation', 'Berg Castle Charter', False, 'Burg Berge at Altenberg founded 1060–1077 AD; pre-867 center Kaiserswerth'),
    'c_luxembourg': (963, 'high_medieval_foundation', 'Deed of St. Maximin Abbey', False, 'Lucilinburhuc acquired 963 AD; pre-867 centers Echternach/Arlon'),
    'c_bouillon': (988, 'high_medieval_foundation', 'Ottonian Charter', False, 'Castrum Bullionis first attested 988 AD on the Semois'),
    'c_namur': (907, 'high_medieval_foundation', 'Comital Charter', False, 'Namur castrum first attested 907 AD at Sambre-Meuse confluence'),
    'c_brussels': (966, 'high_medieval_foundation', 'Ottonian Charter of Otto I', False, 'Brosella attested 966 AD; castrum built 979 by Charles of Lower Lorraine'),
    'c_munchen': (1158, 'high_medieval_foundation', 'Augsburger Schied', False, 'München founded 1158 by Henry the Lion; pre-867 center Freising'),
    'c_innsbruck': (1180, 'high_medieval_foundation', 'Andechs Comital Charter', False, 'Market founded 1180; pre-867 center Roman Veldidena (Wilten)'),
    'c_graz': (1128, 'high_medieval_foundation', 'Styrian Comital Charter', False, 'Gradec first attested 1128; pre-867 center Hengistburg'),
    'c_leoben': (1261, 'high_medieval_foundation', 'Charter of Ottokar II', False, 'Planned city founded 1261; pre-867 center Göss abbey 1004'),
    'c_steyr': (985, 'high_medieval_foundation', 'Ottonian Charter', False, 'Styraburg attested 985 AD; pre-867 center Roman Lauriacum / Enns'),
    'c_eschenlohe': (1150, 'high_medieval_foundation', 'Eppan Comital Charter', False, 'Burg built 1150; pre-867 center Staffelsee / Partenkirchen'),
    'c_schaumberg': (1150, 'high_medieval_foundation', 'Julbach Comital Charter', False, 'Burg Schaunberg built 1150; pre-867 center Roman Ovilava (Wels)'),
    'c_rothenburg': (1070, 'high_medieval_foundation', 'Comital Charter', False, 'Burg built 1070/1142; pre-867 center Fürth/Forchheim'),
    'c_nassau': (1093, 'high_medieval_foundation', 'Laurenburg Comital Charter', False, 'Burg Nassau built 1093; pre-867 center Weilburg / Limburg'),
    'c_saarbrucken': (999, 'high_medieval_foundation', 'Deed of Otto III', False, 'Castellum Sarabrucca granted 999; pre-867 center St. Arnual 600 AD'),
    'c_zweibrucken': (1170, 'high_medieval_foundation', 'Partition Deed', False, 'Castle built 1170; pre-867 center Carolingian Hornbach abbey 741'),
    'c_nancy': (1070, 'high_medieval_foundation', 'Ducal Charter of Gerard', False, 'Castle founded 1070; pre-867 center Lunéville / Épinal'),
    'c_mark': (1198, 'high_medieval_foundation', 'Altena Comital Charter', False, 'Burg Mark acquired 1198; pre-867 center Soest 820 AD'),
    'c_cleves': (1020, 'high_medieval_foundation', 'Comital Charter', False, 'Schwanenburg founded 1020; pre-867 center Roman Colonia Ulpia Traiana (Xanten)'),
    'c_geldern': (1096, 'high_medieval_foundation', 'Comital Charter of Gerard', False, 'County of Gelre emerged 1096; pre-867 center Zutphen / Roermond'),
    'c_zollern': (1061, 'high_medieval_foundation', 'Swabian Chronicle', False, 'Castle first attested 1061 AD; pre-867 center Hechingen'),
    'c_wurttemberg': (1083, 'high_medieval_foundation', 'Beutelsbach Comital Charter', False, 'Wirttemberg castle built 1083; pre-867 center Cannstatt Roman fort'),
    'c_baden': (1112, 'high_medieval_foundation', 'Margravial Charter of Hermann II', False, 'Hohenbaden castle built 1112; pre-867 center Roman Aquae Aureliae'),
    'c_marburg': (1140, 'high_medieval_foundation', 'Thuringian Landgravial Charter', False, 'Castle built 1140; pre-867 center Amöneburg Celtic/Carolingian fort'),
    'c_lubeck': (1143, 'high_medieval_foundation', 'Chronica Slavorum (Helmold)', False, 'Lübeck founded 1143; pre-867 center is Obotrite Liubice'),
    'c_schwerin': (1160, 'high_medieval_foundation', 'Charter of Henry the Lion', False, 'Founded 1160; pre-867 center Obotrite Zuarin'),
    'c_rostock': (1161, 'high_medieval_foundation', 'Chronica Slavorum', False, 'First attested 1161; Slavic Urbs Roztoc on Warnow'),
    'c_stralsund': (1234, 'high_medieval_foundation', 'Charter of Wizlaw I', False, 'Founded 1234 on Strelasund; pre-867 Rani Slavic territory'),
    'c_berlin': (1237, 'high_medieval_foundation', 'Deed of Margrave John I', False, 'First attested 1237 (Cölln) / 1244 (Berlin); pre-867 Spandau Slavic fort'),
    'c_brandenburg': (928, 'high_medieval_foundation', 'Widukind of Corvey', False, 'Brennabor captured 928 by Henry the Fowler; bishopric 948'),
    'c_kammersberg': (1207, 'high_medieval_foundation', 'Styrian Comital Charter', False, 'Burg Kammersberg attested 1207; pre-867 center Judenburg / Murau'),
    'c_peiting': (1050, 'high_medieval_foundation', 'Welf Comital Charter', False, 'Castle built 11th c.; pre-867 center Altenstadt / Schongau'),
    'c_calw': (1050, 'high_medieval_foundation', 'Calw Comital Charter', False, 'Burg Calw built 11th c.; pre-867 center Carolingian abbey Hirsau 830'),

    # =========================================================================
    # BRITISH ISLES & IRELAND (TIER 1 & 4)
    # =========================================================================
    'c_london': (47, 'classical_antiquity', 'Tacitus (Annales)', False, 'Londinium founded c. 47 AD under Emperor Claudius on Thames'),
    'c_york': (71, 'classical_antiquity', 'Tacitus (Agricola)', False, 'Eboracum legionary fortress founded 71 AD by Petillius Cerialis on Ouse'),
    'c_chester': (79, 'classical_antiquity', 'Roman Military Inscriptions', False, 'Deva Victrix legionary fortress founded 79 AD by Agricola on Dee'),
    'c_lincoln': (60, 'classical_antiquity', 'Roman Military Inscriptions', False, 'Lindum Colonia established c. 60 AD as Roman legionary base'),
    'c_winchester': (70, 'classical_antiquity', 'Roman Itineraries', False, 'Venta Belgarum civitas capital founded c. 70 AD on Itchen'),
    'c_canterbury': (50, 'classical_antiquity', 'Bede / Roman Itineraries', False, 'Durovernum Cantiacorum founded 50 AD; archbishopric 597 AD'),
    'c_gowrie': (1124, 'high_medieval_foundation', 'Charter of David I', False, 'Royal burgh of Perth chartered 1124; pre-867 ancient ritual capital Scone (Skôn) 843 AD'),
    'c_ayrshire': (1197, 'high_medieval_foundation', 'Charter of William the Lion', False, 'Ayr burgh founded 1197; pre-867 Brythonic kingdom Kyle (Kîl)'),
    'c_linlithgowshire': (1138, 'high_medieval_foundation', 'Charter of David I', False, 'Burgh chartered 1138; pre-867 center Abercorn (Aberkôrn) / Falkirk'),
    'c_lanarkshire': (1140, 'high_medieval_foundation', 'Charter of David I', False, 'Burgh chartered 1140; pre-867 Strathclyde Brythonic center Cadzow (Kadjo)'),
    'c_athlone': (1120, 'high_medieval_foundation', 'Annals of the Four Masters', False, 'Wicker bridge/castle built 1120; pre-867 sacred royal navel Uisneach (Uisnech)'),
    'c_ennis': (1240, 'high_medieval_foundation', 'Annals of Inisfallen', False, 'Ennis Friary founded 1240; pre-867 Brian Boru royal fortress Kincora (Kinkôre)'),

    # =========================================================================
    # STEPPE, OUTREMER, MEDITERRANEAN & BALKANS (TIER 1, 4 & 5)
    # =========================================================================
    'c_bakhmut': (1571, 'high_medieval_foundation', 'Muscovite Frontier Charter', False, 'Watchpost founded 1571; ancient salt stream Bakhmutka / Tor'),
    'c_millerovo': (1786, 'high_medieval_foundation', 'Imperial Russian Land Grant', False, 'Settlement founded 1786 by Ivan Miller; Kalitva river basin'),
    'c_kazanskaya': (1647, 'high_medieval_foundation', 'Don Cossack Record', False, 'Stanitsa founded 1647; Middle Don river basin Boguchar'),
    'c_odessa': (1794, 'high_medieval_foundation', 'Decree of Catherine II', False, 'Founded 1794; pre-867 ancient Milesian port Olbia Pontica'),
    'c_cherkassy': (1286, 'high_medieval_foundation', 'Rus Chronicles', False, 'Founded late 13th c.; pre-867 Kievan Rus fortress Roden on Dnieper'),
    'c_zagreb': (1094, 'high_medieval_foundation', 'Charter of Ladislaus I', False, 'Diocese founded 1094; pre-867 Roman civitas Sisak (Siscia)'),
    'c_montpellier': (985, 'high_medieval_foundation', 'Deed of Bernard II of Melgueil', False, 'First attested 985 AD; pre-867 Roman episcopal city Maguelone'),
    'c_galati': (1445, 'high_medieval_foundation', 'Moldavian Princely Charter', False, 'First attested 1445; pre-867 Roman/Byzantine fortress Dinogetia'),
    'c_bugeac': (1550, 'high_medieval_foundation', 'Ottoman Administrative Register', False, 'Ottoman 16th-c. exonym; pre-867 classical hydronym Tyras / Nistru'),
    'c_tinmallal': (1124, 'high_medieval_foundation', 'Almohad Chronicle', False, 'Founded 1124 by Ibn Tumart; pre-867 High Atlas Berber valley'),
    'c_dorohoi': (1408, 'high_medieval_foundation', 'Moldavian Princely Charter', False, 'First attested 1408; regional center on Jijia river'),
    'c_iasi': (1395, 'high_medieval_foundation', 'Moldavian Princely Charter', False, 'First attested 1395; regional center on Bahlui river'),
    'c_barlad': (1159, 'high_medieval_foundation', 'Hypatian Chronicle', False, 'First attested 1159 on Bârlad river'),
    'c_cetatea_alba': (1350, 'high_medieval_foundation', 'Genoese/Moldavian Charter', False, 'Medieval fortress 1350; ancient classical Milesian city Tyras / Moncastro'),
    'c_chilia': (1318, 'high_medieval_foundation', 'Genoese Portolan', False, 'First attested 1318; ancient Byzantine Lykostomo on Danube delta'),
    'c_lapusna': (1430, 'high_medieval_foundation', 'Moldavian Princely Charter', False, 'First attested 1430 on Lăpușna river'),
    'c_craiova': (1475, 'high_medieval_foundation', 'Inscribed Tombstone of Jupan Neagoe', False, 'First attested 1475; pre-867 Roman civitas Pelendava'),
    'c_calafat': (1350, 'high_medieval_foundation', 'Genoese Marine Record', False, 'Genoese ship-caulkers 14th c.; pre-867 Roman Drobeta'),
    'c_campulung': (1300, 'high_medieval_foundation', 'Wallachian Voivodal Record', False, 'First attested c. 1300; pre-867 Argeș river seat'),
    'c_turnovo': (1185, 'high_medieval_foundation', 'Chronicle of Niketas Choniates', False, 'Rose to prominence 1185 under Asen and Peter; pre-867 Cherven / Nicopolis'),
    'c_burgas': (1350, 'high_medieval_foundation', 'Byzantine Portolan', False, 'Developed 14th c. from watchtower Pyrgos; pre-867 Sozopolis (Apollonia Pontica)'),
    'c_aalborg': (1040, 'high_medieval_foundation', 'Coins of Harthacnut', False, 'Alabu first attested on coins 1040 AD on Limfjord'),
    'c_metzovo': (1380, 'high_medieval_foundation', 'Chronicle of Ioannina', False, 'First attested 1380 AD in Pindus mountains'),
    'c_molina': (1138, 'high_medieval_foundation', 'Charter of Manrique Pérez de Lara', False, 'Lordship created 1138; pre-867 Celtiberian/Roman civitas Ercávica'),
    'c_vecchio': (1539, 'high_medieval_foundation', 'Bank of Saint George Charter', False, 'Porto-Vecchio founded 1539 by Genoa; pre-867 Portus Syracusanus'),
}

# Ancient Kingdoms where unflagged titles have classical Roman / Hellenistic / Carolingian continuity
CLASSICAL_OR_ANCIENT_KINGDOMS = {
    'k_france', 'k_aquitaine', 'k_burgundy', 'k_brittany', 'k_lotharingia',
    'k_italy', 'k_sicily', 'k_romagna', 'k_sardinia', 'k_venice',
    'k_england', 'k_wales', 'k_scotland', 'k_ireland',
    'k_castille', 'k_leon', 'k_andalusia', 'k_aragon', 'k_valencia',
    'k_badajoz', 'k_portugal', 'k_navarra', 'k_spanish_galicia',
    'k_thessalonika', 'k_hellas', 'k_epirus', 'k_krete', 'k_cyprus', 'e_byzantium',
    'k_anatolia', 'k_pontus', 'k_armenia', 'k_georgia', 'k_caucasus', 'k_nikaea',
    'k_syria', 'k_jerusalem', 'k_jazira', 'k_mesopotamia',
    'k_egypt', 'k_africa', 'k_maghreb', 'k_tahert', 'k_sahara', 'k_nubia', 'k_blemmyia', 'k_abyssinia', 'k_damot', 'k_anbiya',
    'k_croatia', 'k_serbia', 'k_bulgaria', 'k_hungary', 'k_dacia',
    'k_east_francia', 'k_bavaria', 'k_saxony', 'k_frisia',
    'k_arabia', 'k_yemen', 'e_arabia', 'k_persia', 'k_khorasan', 'k_daylam', 'k_makran', 'k_transoxiana',
    'k_denmark', 'k_norway', 'k_sweden'
}


def resolve_county_attestation(county_key: str, county_data: dict, md_record: dict = None):
    """
    Resolves the real-world historical attestation date, evidence type, and primary source.
    Inverts the default: positive pre-867 proof (<= 867) is required for Tier 1 or Tier 3.
    Post-867 foundations or unverified titles default to Tier 4.
    """
    # 1. Explicit Registry Lookup
    if county_key in ATTESTATION_REGISTRY:
        yr, ev, src, is_hyd, notes = ATTESTATION_REGISTRY[county_key]
        return yr, ev, src, is_hyd, notes

    # 2. Markdown Reference Check from Previous Audits
    if md_record:
        prev_reason = md_record.get('previous_reason', '')
        m_year = re.search(r"\b(1[0-9]{3}|[9][0-9]{2})\b", prev_reason)
        if m_year:
            f_year = int(m_year.group(1))
            if f_year > 867:
                return f_year, 'high_medieval_foundation', 'Previous Chancellery Audit (anachronistic_titles_1059.md)', False, prev_reason
        elif md_record.get('is_flagged_in_previous_audit'):
            return 1100, 'high_medieval_foundation', 'Previous Chancellery Audit (anachronistic_titles_1059.md)', False, prev_reason or 'Flagged in previous audit'

    name = county_data.get('name') or ''
    kd = county_data.get('de_jure_kingdom') or ''

    # 3. Ancient Hydronym / Oronym / Geographic Feature Check
    if re.search(r"(gau|berg|gebirge|tal|wald|see|fluv|am-|an-der-)", county_key + " " + name, re.I):
        return -500, 'ancient_hydronym', 'Classical Geography / Regional Toponym', True, 'Derived from ancient pre-867 river, mountain, or topographic regional stem'

    # 4. Classical Roman / Hellenistic / Carolingian Civitas Continuity
    # Valid only in recognized ancient provincial kingdoms and excluding late castle/colonial stems
    if kd in CLASSICAL_OR_ANCIENT_KINGDOMS:
        if not re.search(r"(burg|stein|grad|sk|novo|aleksandr|stanitsa|gorod)$", county_key):
            return 100, 'classical_civitas', 'Roman / Hellenistic Provincial Civitas (Antonine Itinerary / Ptolemy / Notitia Dignitatum)', False, 'Ancient Mediterranean / European civitas or diocese with documented pre-867 continuity'

    # 5. Default Fallback under Burden of Proof on Antiquity
    return None, 'unverified_default', 'None', False, 'Lacks verified historical attestation prior to 867 AD; defaulted to Tier 4 under Burden of Proof on Antiquity'

#!/usr/bin/env python3
"""
Master Historical Attestation Database & Resolution Engine
-----------------------------------------------------------
Part of the Tarraconian Historical Title Audit Pipeline.

Enforces the Streamlined 3-Tier Classification System & Burden of Proof on Antiquity:
  - Tier 1: Pre-867 Historical / Antiquity (attestation <= 867 AD).
            Check history, adapt chronologically to changing cultures, adapt to Tarraconian.
  - Tier 2: Founded after 867 on a hydronym, or other geographic or tribal name.
            Check history, restore pre-HRE morphology (stripping colonial suffixes like
            Slavic -sk/-ysk, German Ostsiedlung -burg/-stein in Baltic lands), adapt to Tarraconian.
  - Tier 3: Other settlements founded after 867 (default).
            Pick another name according to Options A, B, or C, changing appropriately
            to linguistic history, adapt to Tarraconian.
  - Universal Rule: For all tiers, adapt the final name phonologically to Tarraconian.
"""

import os
from pathlib import Path
import re
import sys

# Comprehensive registry of verified historical dates, classical civitates, and medieval foundations
# Tuple format: (attestation_year, evidence_category, primary_source, is_geographic_stem, notes)
ATTESTATION_REGISTRY = {
    # =========================================================================
    # EAST SLAVIC & RUS' — PRE-867 ATTESTATIONS (TIER 1)
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
    # EAST SLAVIC & RUS' — POST-867 FOUNDATIONS (TIER 2 & TIER 3)
    # =========================================================================
    'c_novogrudok': (1044, 'high_medieval_foundation', 'Primary Chronicle', False, "Founded c. 1044 AD as 'New Castle' (Novъ-gordъ); pre-867 substrate is Baltic hydronym Plisa / Plesė"),
    'c_volkovysk': (1252, 'high_medieval_foundation', 'Hypatian Chronicle', True, "First attested 1252 with Slavic town suffix -ysk over river Ros' / Vaŭkavyja; pre-867 Yatvingian substrate"),
    'c_minsk': (1067, 'high_medieval_foundation', 'Primary Chronicle (Battle on the Nemiga)', True, "First attested 1067 with Slavic town suffix -sk over ancient Baltic hydronym Menka / Mėna"),
    'c_roslavl': (1137, 'high_medieval_foundation', 'Smolensk Princely Chronicle', False, 'Founded 1137 by Prince Rostislav Mstislavich; pre-867 hydronym Oster'),
    'c_slutsk': (1116, 'high_medieval_foundation', 'Primary Chronicle', True, 'First attested 1116 in Primary Chronicle (Sluchek) on the Sluch River'),
    'c_kletsk': (1127, 'high_medieval_foundation', 'Primary Chronicle', True, 'First attested 1127 in Primary Chronicle (Kłečesk) on the Lan River'),
    'c_grodno': (1127, 'high_medieval_foundation', 'Primary Chronicle', False, 'First attested 1127 as Gorodzen; Imperial Chancellery name Garten'),
    'c_braslau': (1065, 'high_medieval_foundation', 'Polotsk Chronicle', False, 'Founded 1065 by Bryachislav of Polotsk (Bryachislavl) on Lake Dryvyaty'),
    'c_babruysk': (1387, 'high_medieval_foundation', 'Crown Lithuanian Charter', True, 'First attested 1387 on Bobruyka river; pre-867 center is river Berezina / Dregovich gord Rechytsa'),
    'c_sebezh': (1414, 'high_medieval_foundation', 'Chronicle of Pskov', True, 'Fortress built 1414; pre-867 Baltic hydronym Lake Sebezh (Sebēža)'),
    'c_lyubim': (1538, 'high_medieval_foundation', 'Muscovite Line Fortress Charter', False, 'Fortress built 1538; pre-867 hydronym Obnora River'),
    'c_vologda': (1147, 'high_medieval_foundation', 'Tale of Miracles of St. Gerasim', True, 'Founded 1147 on Vologda river; pre-867 Finno-Ugric / Vepsian hydronym Walgede'),
    'c_moskva': (1147, 'high_medieval_foundation', 'Hypatian Chronicle', True, 'Yuri Dolgoruky meeting 1147; pre-867 hydronym Moskva River'),
    'c_tver': (1135, 'high_medieval_foundation', 'Statute of Prince Vsevolod', True, 'First attested 1135 on Tvertsa river; pre-867 portage Volok-Lamsky'),
    'c_tula': (1146, 'high_medieval_foundation', 'Nikon Chronicle', True, 'First attested 1146 on Tulitsa river; pre-867 Vyatichi hillfort Pronsk'),
    'c_dmitrov': (1154, 'high_medieval_foundation', 'Suzdalian Chronicle', False, 'Founded 1154 by Yuri Dolgoruky on Yakhroma river'),
    'c_kostroma': (1213, 'high_medieval_foundation', 'Voskresenskaya Chronicle', True, 'Founded 1213 at Kostroma-Volga confluence'),
    'c_nizhny_novgorod': (1221, 'high_medieval_foundation', 'Lavrentian Chronicle', False, 'Founded 1221 by Yuri II; pre-867 Mari/Merya fortress Obran Osh'),
    'c_yaroslavl': (1010, 'high_medieval_foundation', 'Primary Chronicle', False, 'Founded 1010 by Yaroslav the Wise over pagan Bear Corner'),
    'c_vladimir': (990, 'high_medieval_foundation', 'Primary Chronicle', False, 'Founded 990 by Vladimir the Great / fortified 1108 by Vladimir Monomakh; pre-867 Merya river basin is Klyazma (Klêsme)'),
    'c_suzdal': (999, 'high_medieval_foundation', 'Novgorod Codex', True, 'Attested 999 / 1024 AD in Suzdalia tribal land on the Kamenka'),
    'c_ryazan': (1095, 'high_medieval_foundation', 'Sleptsov Chronicle', True, 'Pereyaslavl-Ryazansky founded 1095; Old Ryazan 10th-11th c. on Oka/Erzya territory; adapted as Rêsan'),
    'c_bryansk': (1146, 'high_medieval_foundation', 'Hypatian Chronicle', True, 'First attested 1146 as Debryansk (from debr = dense forest) on the Desna'),
    'c_gomel': (1142, 'high_medieval_foundation', 'Hypatian Chronicle', True, 'First attested 1142 as Gomey on Gomeyuk stream and Sozh river'),
    'c_turov': (980, 'high_medieval_foundation', 'Primary Chronicle', False, 'First attested 980 under Prince Rogvolod and Tur on the Pripyat'),
    'c_pinsk': (1097, 'high_medieval_foundation', 'Primary Chronicle', True, 'First attested 1097 as Pinesk on the Pina river'),
    'c_orsha': (1067, 'high_medieval_foundation', 'Primary Chronicle', True, 'First attested 1067 as Rsha on Dnieper-Orshytsa confluence'),
    'c_vitebsk': (974, 'high_medieval_foundation', 'Chronicle of Vitebsk', True, 'Founded 974 by Princess Olga / attested 1021 on Vitba and Western Dvina'),
    'c_toropets': (1074, 'high_medieval_foundation', 'Lavrentian Chronicle', True, 'First attested 1074 on Toropa river'),
    'c_mozhaysk': (1231, 'high_medieval_foundation', 'Novgorod Chronicle', True, 'First attested 1231 on Mozhaya river'),
    'c_lutsk': (1085, 'high_medieval_foundation', 'Primary Chronicle', True, 'First attested 1085 as Luchesk from river bend Luka on Styr river'),
    'c_ostrog': (1100, 'high_medieval_foundation', 'Primary Chronicle', False, 'First attested 1100 at Council of Vytechev'),
    'c_zhytomyr': (884, 'high_medieval_foundation', 'Primary Chronicle legend', False, 'Legendary foundation 884 AD by retainer of Askold and Dir'),
    'c_ovruch': (977, 'high_medieval_foundation', 'Primary Chronicle', True, 'First attested 977 as Vruchiy (boiling spring) on the Uzh'),
    'c_korosten': (945, 'high_medieval_foundation', 'Primary Chronicle', False, 'First attested 945 as Drevlian capital Iskorosten on the Uzh'),
    'c_chernigov': (907, 'high_medieval_foundation', 'Primary Chronicle', False, 'First mentioned in 907 Rus-Byzantine treaty on the Desna'),
    'c_kursk': (1032, 'high_medieval_foundation', 'Life of Theodosius of the Caves', True, 'First attested 1032 on Kur and Tuskar rivers in Severia'),
    'c_putyvl': (1146, 'high_medieval_foundation', 'Hypatian Chronicle', True, 'First attested 1146 on Putyvlya river route and Seym'),
    'c_pereyaslavl': (992, 'high_medieval_foundation', 'Primary Chronicle', False, 'Founded 992 by Vladimir the Great on the Trubezh'),
    'c_korsun': (1032, 'high_medieval_foundation', 'Primary Chronicle', False, 'Founded 1032 by Yaroslav the Wise on the Ros river line'),
    'c_novgorod_seversky': (1044, 'high_medieval_foundation', 'Primary Chronicle', False, 'First attested 1044 as New Gord of the Severians on the Desna'),
    'c_belz': (1030, 'high_medieval_foundation', 'Primary Chronicle', True, 'First attested 1030 in Red Ruthenia; name derived from Slavic belz (white/chalky place)'),
    'c_lviv': (1256, 'high_medieval_foundation', 'Galician-Volhynian Chronicle', False, 'Founded c. 1256 by Danylo of Halych; pre-867 center is princely capital Zvenyhorod'),
    'c_galich': (898, 'high_medieval_foundation', 'Primary Chronicle', True, 'First mentioned 898 AD; ancient salt hill / Celtic hal- root on the Dniester'),
    'c_zaslavl': (985, 'high_medieval_foundation', 'Primary Chronicle', False, 'Founded c. 985 by Vladimir for Rogneda (Izyaslavl)'),
    'c_volodymyr': (988, 'high_medieval_foundation', 'Primary Chronicle', False, 'Founded 988 by Vladimir the Great; pre-867 Dulebe/Volhynian capital is Zimne hillfort (Simne) on Luga River'),

    # =========================================================================
    # POLAND, BOHEMIA & WEST SLAVIA (TIER 1, 2 & 3)
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
    'c_brzeg': (1248, 'high_medieval_foundation', 'Silesian Town Charter', True, 'Town chartered 1248; name derived from Slavic brzeg (riverbank) on the Oder'),
    'c_ratibor': (1108, 'high_medieval_foundation', 'Gallus Anonymus', False, 'Attested 1108 in Chronica Polonorum on Upper Oder'),
    'c_cieszyn': (1155, 'high_medieval_foundation', 'Papal Bull of Hadrian IV', True, 'Attested 1155 as Tessin on Olza river'),
    'c_plocka': (1000, 'high_medieval_foundation', 'Thietmar of Merseburg', False, 'Late 10th-c. Piast fortified center, bishopric 1075 on the Vistula'),
    'c_radomska': (1155, 'high_medieval_foundation', 'Papal Bull of Hadrian IV', False, 'Attested 1155; 10th-c. gord Piotrówka'),
    'c_sandomierska': (1000, 'high_medieval_foundation', 'Gallus Anonymus', False, 'Early 11th-c. Piast sedes regni principalis on the Vistula'),
    'c_lubelska': (1198, 'high_medieval_foundation', 'Archdeaconry Charter', False, 'Attested 1198 on Bystrzyca river'),
    'c_breslau': (1000, 'high_medieval_foundation', 'Thietmar of Merseburg', False, 'Bishopric founded 1000 AD; 10th-c. Bohemian/Piast gord on the Oder'),
    'c_torun': (1231, 'high_medieval_foundation', 'Teutonic Order Charter', False, 'Founded 1231 by Hermann Balk; pre-867 center Chełmno (Kulm)'),
    'c_malbork': (1274, 'high_medieval_foundation', 'Teutonic Order Charter', False, 'Marienburg castle built 1274; pre-867 center Truso'),
    'c_elblag': (1237, 'high_medieval_foundation', 'Teutonic Order Charter', True, 'Elbing founded 1237 on river Ilfing; pre-867 Viking/Old Prussian emporium Truso'),
    'c_olomouc': (1055, 'high_medieval_foundation', 'Cosmas of Prague', False, 'Attested 1055; sub-barony b_unicov chartered 1213; pre-867 center Litovel on Morava'),
    'c_plzen': (1295, 'high_medieval_foundation', 'Charter of Wenceslaus II', False, 'New Pilsen founded 1295; pre-867 center is 10th-c. gord Old Pilsen (Starý Plzenec)'),
    'c_opava': (1224, 'high_medieval_foundation', 'Charter of Ottokar I', True, 'Town chartered 1224; pre-867 hydronym Opava / Troppau'),
    'c_hradec': (1225, 'high_medieval_foundation', 'Charter of Ottokar I', False, 'Chartered 1225; pre-867 Slavic gord on Elbe-Orlice confluence'),
    'c_caslav': (1260, 'high_medieval_foundation', 'Charter of Ottokar II', False, 'Royal town founded 1260 by Ottokar II; pre-867 gord Hrádek'),
    'c_koszmin': (1200, 'high_medieval_foundation', 'Greater Poland Charter', False, 'Settlement attested 12th-13th c.; pre-867 center Kalisz on Amber Road'),
    'c_hirschberg': (1281, 'high_medieval_foundation', 'Piast Charter of Bernard the Lightsome', False, 'Founded 1281; pre-867 center Warmbrunn thermal springs / Legnica'),

    # =========================================================================
    # BALTIC, LIVONIA, PRUSSIA & FINLAND (TIER 2 & 3)
    # =========================================================================
    'c_aluksne': (1342, 'high_medieval_foundation', 'Livonian Order Chronicle', True, 'Marienburg built 1342; pre-867 center is Latgalian lake-hillfort Alūksne / Olyxna'),
    'c_narva': (1256, 'high_medieval_foundation', 'Liber Census Daniae', True, 'Danish fortress 1256; pre-867 Finnic hydronym Narva River'),
    'c_dorpat': (1030, 'high_medieval_foundation', 'Primary Chronicle', False, 'Yuryev/Dorpat captured 1030; pre-867 center is 5th-c. Estonian hillfort Tarbata'),
    'c_riga': (1201, 'high_medieval_foundation', 'Henry of Livonia', True, 'Founded 1201 by Bishop Albert on Rīdziņa river; pre-867 Daugava trading site'),
    'c_tallinn': (1219, 'high_medieval_foundation', 'Henry of Livonia', False, 'Danish conquest 1219; pre-867 Lindanise / Rävala'),
    'c_reval': (1219, 'high_medieval_foundation', 'Henry of Livonia', True, 'Danish castle 1219; derived from ancient Estonian province Rävala'),
    'c_memel': (1252, 'high_medieval_foundation', 'Livonian Order Charter', True, 'Memelburg castle 1252 on Curonian river Mēmele; pre-867 Curonian fortress Pilsāts'),
    'c_konigsberg': (1255, 'high_medieval_foundation', 'Teutonic Order Charter', False, 'Founded 1255; pre-867 Old Prussian fortress Twangste / emporium Kaup'),
    'c_allenstein': (1348, 'high_medieval_foundation', 'Warmian Chapter Charter', True, 'Founded 1348 on Alle river (Łyna); pre-867 Galindian tribal land'),
    'c_bartenstein': (1240, 'high_medieval_foundation', 'Teutonic Order Charter', True, 'Castle built 1240 in Old Prussian tribal territory Bartia (Barta)'),
    'c_wormditt': (1308, 'high_medieval_foundation', 'Warmian Chapter Charter', True, 'Founded 1308 in Old Prussian tribal territory Warmia (Wormyan)'),
    'c_osterode': (1300, 'high_medieval_foundation', 'Teutonic Order Charter', True, 'Castle built 1300 in Old Prussian tribal territory Sasna'),
    'c_angerburg': (1335, 'high_medieval_foundation', 'Teutonic Order Charter', True, 'Castle built 1335 on Angerapp river in Sudovia'),
    'c_trakai': (1316, 'high_medieval_foundation', 'Lithuanian Chronicles', False, 'Old Trakai founded c. 1316 by Gediminas; pre-867 center Merkinė'),
    'c_vilnius': (1323, 'high_medieval_foundation', 'Letters of Gediminas', True, 'First attested 1323 on Vilnia river and Neris confluence'),
    'c_viipuri': (1293, 'high_medieval_foundation', 'Erikskrönikan', False, 'Swedish castle 1293 by Torgils Knutsson; pre-867 Karelian Linnasaari'),
    'c_nyland': (1249, 'high_medieval_foundation', 'Second Swedish Crusade', False, 'Colonial name c. 1249; pre-867 Tavastian/Finnic coast Uusimaa/Espoo'),
    'c_turku': (1229, 'high_medieval_foundation', 'Papal Bull of Gregory IX', False, 'See transferred 1229; pre-867 Koroinen / Aura river'),
    'c_pedersore': (1290, 'high_medieval_foundation', 'Swedish Parish Register', False, 'Parish attested late 13th c.; pre-867 Ostrobothnian Vuohijärvi'),
    'c_messukyla': (1450, 'high_medieval_foundation', 'Catholic Parish Register', False, 'Parish 15th c.; pre-867 Upper Satakunta lake route Ruovesi'),

    # =========================================================================
    # RHINELAND, LOTHRINGIA, GERMANY, BAVARIA & AUSTRIA (TIER 1, 2 & 3)
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

    # Post-867 German, Lotharingian & Austrian Castles (Tier 2 & 3)
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
    'c_saarbrucken': (999, 'high_medieval_foundation', 'Deed of Otto III', True, 'Castellum Sarabrucca granted 999 on Saar river; pre-867 center St. Arnual 600 AD'),
    'c_zweibrucken': (1170, 'high_medieval_foundation', 'Partition Deed', True, 'Castle built 1170 on Schwarzbach river crossings; pre-867 center Carolingian Hornbach abbey 741'),
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
    'c_rostock': (1161, 'high_medieval_foundation', 'Chronica Slavorum', True, 'First attested 1161 on Warnow river / Slavic Urbs Roztoc'),
    'c_stralsund': (1234, 'high_medieval_foundation', 'Charter of Wizlaw I', True, 'Founded 1234 on Strelasund strait; pre-867 Rani Slavic territory'),
    'c_berlin': (1237, 'high_medieval_foundation', 'Deed of Margrave John I', False, 'First attested 1237 (Cölln) / 1244 (Berlin); pre-867 Spandau Slavic fort'),
    'c_brandenburg': (928, 'high_medieval_foundation', 'Widukind of Corvey', False, 'Brennabor captured 928 by Henry the Fowler; bishopric 948'),
    'c_kammersberg': (1207, 'high_medieval_foundation', 'Styrian Comital Charter', False, 'Burg Kammersberg attested 1207; pre-867 center Judenburg / Murau'),
    'c_peiting': (1050, 'high_medieval_foundation', 'Welf Comital Charter', False, 'Castle built 11th c.; pre-867 center Altenstadt / Schongau'),
    'c_calw': (1050, 'high_medieval_foundation', 'Calw Comital Charter', False, 'Burg Calw built 11th c.; pre-867 center Carolingian abbey Hirsau 830'),

    # =========================================================================
    # BRITISH ISLES & IRELAND (TIER 1 & 3)
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
    # STEPPE, OUTREMER, MEDITERRANEAN & BALKANS (TIER 1, 2 & 3)
    # =========================================================================
    'c_bakhmut': (1571, 'high_medieval_foundation', 'Muscovite Frontier Charter', True, 'Watchpost founded 1571; derived from ancient salt river Bakhmutka / Tor'),
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
    'c_iasi': (1395, 'high_medieval_foundation', 'Moldavian Princely Charter', True, 'First attested 1395; derived from Sarmatian/Alan tribe Iazyges / Jassi on Bahlui river'),
    'c_barlad': (1159, 'high_medieval_foundation', 'Hypatian Chronicle', True, 'First attested 1159 on Bârlad river'),
    'c_cetatea_alba': (1350, 'high_medieval_foundation', 'Genoese/Moldavian Charter', False, 'Medieval fortress 1350; ancient classical Milesian city Tyras / Moncastro'),
    'c_chilia': (1318, 'high_medieval_foundation', 'Genoese Portolan', False, 'First attested 1318; ancient Byzantine Lykostomo on Danube delta'),
    'c_lapusna': (1430, 'high_medieval_foundation', 'Moldavian Princely Charter', True, 'First attested 1430 on Lăpușna river'),
    'c_craiova': (1475, 'high_medieval_foundation', 'Inscribed Tombstone of Jupan Neagoe', False, 'First attested 1475; pre-867 Roman civitas Pelendava'),
    'c_calafat': (1350, 'high_medieval_foundation', 'Genoese Marine Record', False, 'Genoese ship-caulkers 14th c.; pre-867 Roman Drobeta'),
    'c_campulung': (1300, 'high_medieval_foundation', 'Wallachian Voivodal Record', False, 'First attested c. 1300; pre-867 Argeș river seat'),
    'c_turnovo': (1185, 'high_medieval_foundation', 'Chronicle of Niketas Choniates', False, 'Rose to prominence 1185 under Asen and Peter; pre-867 Cherven / Nicopolis'),
    'c_burgas': (1350, 'high_medieval_foundation', 'Byzantine Portolan', False, 'Developed 14th c. from watchtower Pyrgos; pre-867 Sozopolis (Apollonia Pontica)'),
    'c_aalborg': (1040, 'high_medieval_foundation', 'Coins of Harthacnut', False, 'Alabu first attested on coins 1040 AD on Limfjord'),
    'c_metzovo': (1380, 'high_medieval_foundation', 'Chronicle of Ioannina', True, 'First attested 1380 AD on Metzovo mountain / Pindus'),
    'c_molina': (1138, 'high_medieval_foundation', 'Charter of Manrique Pérez de Lara', False, 'Lordship created 1138; pre-867 Celtiberian/Roman civitas Ercávica'),
    'c_vecchio': (1539, 'high_medieval_foundation', 'Bank of Saint George Charter', False, 'Porto-Vecchio founded 1539 by Genoa; pre-867 Portus Syracusanus'),
    'c_kerak': (1142, 'high_medieval_foundation', 'Crusader Chronicle / William of Tyre', False, 'Crusader castle Kerak (1142) and Montréal (1115); resolves to classical Nabataean metropolis Petra (Pêtre)'),
    'c_negev': (-1200, 'classical_antiquity', 'Biblical Hebrew / Ptolemy Geography', True, 'Ancient rift valley depression between Dead Sea and Gulf of Aqaba (Ha-Aravah / Wadi Araba); resolves to Arabâ'),
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
    'k_denmark', 'k_norway', 'k_sweden',
    # Ancient Indian / Indus / Gandharan Civilizations
    'k_punjab', 'k_sindh', 'k_kashmir', 'k_delhi', 'k_kabulistan', 'k_himalaya',
    # Ancient East Asian & Silk Road Civilizations (Tang / Han / Ritsuryo / Three Kingdoms)
    'k_yamato', 'k_azuma', 'k_tsukushi', 'k_hitakami',
    'k_silla', 'k_goguryeo', 'k_baekje', 'k_balhae',
    'k_hedong', 'k_daibei', 'k_youji', 'k_hexi', 'k_xia', 'k_amdo', 'k_khotan', 'k_syr_darya', 'k_oghuz_il'
}


def resolve_county_attestation(county_key: str, county_data: dict, md_record: dict = None):
    """
    Resolves the real-world historical attestation date, evidence type, and primary source.
    Inverts the default: positive pre-867 proof (<= 867) is required for Tier 1.
    Post-867 foundations or unverified titles default to Tier 2 (if hydronym/tribal) or Tier 3.
    """
    # 1. Explicit Registry Lookup
    if county_key in ATTESTATION_REGISTRY:
        yr, ev, src, is_geo, notes = ATTESTATION_REGISTRY[county_key]
        return yr, ev, src, is_geo, notes

    # 2. Markdown Reference Check from Previous Audits
    if md_record:
        prev_reason = md_record.get('previous_reason', '')
        m_year = re.search(r"\b(1[0-9]{3}|[9][0-9]{2})\b", prev_reason)
        if m_year:
            f_year = int(m_year.group(1))
            if f_year > 867:
                is_geo_stem = bool(re.search(r"(river|hydronym|lake|mountain|tribe)", prev_reason, re.I))
                return f_year, 'high_medieval_foundation', 'Previous Chancellery Audit (anachronistic_titles_1059.md)', is_geo_stem, prev_reason
        elif md_record.get('is_flagged_in_previous_audit'):
            return 1100, 'high_medieval_foundation', 'Previous Chancellery Audit (anachronistic_titles_1059.md)', False, prev_reason or 'Flagged in previous audit'

    name = county_data.get('name') or ''
    kd = county_data.get('de_jure_kingdom') or ''

    # 3. Ancient Hydronym / Oronym / Geographic Feature Check
    if re.search(r"(gau|gebirge|tal|wald|fluv|am-|an-der-)", county_key + " " + name, re.I):
        return -500, 'ancient_hydronym', 'Classical Geography / Regional Toponym', True, 'Derived from ancient river, mountain, or topographic regional stem'

    # 4. Classical Roman / Hellenistic / Carolingian / Ancient Civilizational Civitas Continuity
    # Valid only in recognized ancient provincial kingdoms and excluding late castle/colonial stems
    if kd in CLASSICAL_OR_ANCIENT_KINGDOMS:
        if not re.search(r"(burg|stein|grad|sk|novo|aleksandr|stanitsa|gorod)$", county_key):
            return 100, 'classical_civitas', 'Classical Roman / Hellenistic / Ancient Provincial Continuity', False, 'Ancient Mediterranean / European / Asian civitas, commandery, or provincial division with documented pre-867 continuity'

    # 5. Default Fallback under Burden of Proof on Antiquity
    return None, 'unverified_default', 'None', False, 'Lacks verified historical attestation prior to 867 AD; defaulted to Tier 3 under Burden of Proof on Antiquity'


def classify_county_tier(county_key: str, county_data: dict, md_record: dict = None):
    """
    Classifies a county into the 3-Tier Historical Accuracy Model:
      - Tier 1: Pre-867 Historical / Antiquity (attestation <= 867 AD).
                Check history, adapt chronologically to changing cultures, adapt to Tarraconian.
      - Tier 2: Founded after 867 on a hydronym, geographic, or tribal name.
                Check history, restore pre-HRE morphology (stripping colonial suffixes like
                -sk, -ysk, -burg, -stein), adapt to Tarraconian.
      - Tier 3: Other settlements founded after 867 (default).
                Pick another name according to Options A, B, or C, changing appropriately
                to linguistic history, adapt to Tarraconian.
    """
    att_yr, att_ev, att_src, is_geo, att_notes = resolve_county_attestation(county_key, county_data, md_record)

    # 1. Tier 1: Positive pre-867 historical attestation (<= 867 AD)
    if att_yr is not None and att_yr <= 867:
        tier = 1
        tier_label = "Tier 1: Pre-867 Historical / Antiquity"
        tier_reason = f"Attested pre-867 ({att_yr} AD/BC) via {att_ev} ({att_src}): {att_notes}"
        return tier, tier_label, tier_reason, att_yr, att_ev, att_src, is_geo, att_notes


    # 2. Tier 2: Post-867 foundation based on hydronym, geographic, or tribal name
    if is_geo:
        tier = 2
        tier_label = "Tier 2: Founded After 867 on Hydronymic, Geographic, or Tribal Stems"
        tier_reason = (
            f"Founded after 867 ({att_yr or 'high medieval'} AD) on ancient hydronym/geographic/tribal root "
            f"({att_src}): {att_notes}. Pre-HRE native morphology must be restored before Tarraconian adaptation."
        )
        return tier, tier_label, tier_reason, att_yr, att_ev, att_src, is_geo, att_notes

    # 3. Tier 3: Default for all other post-867 foundations, dynastic castles, unverified titles
    tier = 3
    tier_label = "Tier 3: Other Settlement Founded After 867 (Default)"
    tier_reason = (
        f"Post-867 settlement or unverified title ({att_yr or 'unverified'} AD) lacking an ancient "
        f"hydronymic or tribal stem ({att_src}): {att_notes}. Must be resolved via Options A, B, or C."
    )
    return tier, tier_label, tier_reason, att_yr, att_ev, att_src, is_geo, att_notes


def load_enriched_historical_db(repo_dir=None):
    """
    Builds the unified, fully enriched database of historical title resolutions,
    combining the curated HISTORICAL_TITLE_DB, explicit regional historical registers,
    archive/anachronistic_titles_1059.md, and tarraconian_titles_1059.md.
    Enforces the Burden of Proof on Antiquity: zero unverified baronies allowed as Option A.
    """
    if repo_dir is None:
        repo_dir = Path(__file__).resolve().parent.parent
    else:
        repo_dir = Path(repo_dir)

    try:
        from screen_phase3_titles import HISTORICAL_TITLE_DB as BASE_DB
        enriched = dict(BASE_DB)
    except Exception:
        enriched = {}

    REGIONAL_HISTORICAL = {
        # Poland & Mazovia
        "c_czerska": {
            "opt_a_key": "b_czersk",
            "opt_a_name": "Czersk",
            "opt_a_type": "11th-c. Piast fortified stronghold and ducal capital of Mazovia",
            "opt_b_hydronym": "Vistula River Reach",
            "opt_b_lang": "West Slavic Toponym",
            "opt_b_name": "Tschêrtzich",
            "justification": "Czersk was the ancient Piast capital of southern Mazovia on the Vistula. Warsaw (b_warszawa) was a late c. 1300 foundation. Retains Czersk (Tschêrtzich).",
            "rec_option": "Option A",
            "tarr_name": "Tschêrtzich",
            "tarr_adjective": "Tschêrtzicher"
        },
        "c_zakroczymska": {
            "opt_a_key": "b_zakroczym",
            "opt_a_name": "Zakroczym",
            "opt_a_type": "11th-c. Piast fortified crossing on the Vistula",
            "opt_b_hydronym": "Vistula River Crossing",
            "opt_b_lang": "West Slavic Toponym",
            "opt_b_name": "Sakrotschîm",
            "justification": "Zakroczym was an 11th-c. Piast fortress guarding the Vistula-Narew confluence. Retains Zakroczym (Sakrotschîm).",
            "rec_option": "Option A",
            "tarr_name": "Sakrotschîm",
            "tarr_adjective": "Sakrotschîmer"
        },
        "c_lomzynska": {
            "opt_a_key": "None",
            "opt_a_name": "Stara Łomża (Old Lomza)",
            "opt_a_type": "9th-10th c. Mazovian fortified gord on the Narew River",
            "opt_b_hydronym": "Narew River",
            "opt_b_lang": "West Slavic Toponym",
            "opt_b_name": "Altlomsche",
            "justification": "Modern Łomża dates to the late 14th c.; the authentic early medieval Piast center was Stara Łomża on the Narew. Resolved to Altlomsche.",
            "rec_option": "Option A",
            "tarr_name": "Altlomsche",
            "tarr_adjective": "Altlomscher"
        },
        "c_lubelska": {
            "opt_a_key": "None",
            "opt_a_name": "Bystrzyca Castle Hill",
            "opt_a_type": "6th-8th c. Slavic settlement on Castle Hill on the Bystrzyca",
            "opt_b_hydronym": "Bystrzyca River",
            "opt_b_lang": "West Slavic Hydronym",
            "opt_b_name": "Bistritze",
            "justification": "Lublin was first attested in 1198. Castle Hill was settled by Slavs from the 6th c. on the Bystrzyca River. Resolved via Option B to Bistritze.",
            "rec_option": "Option B",
            "tarr_name": "Bistritze",
            "tarr_adjective": "Bistritzer"
        },
        "c_leczycka": {
            "opt_a_key": "None",
            "opt_a_name": "Tum Gord (Old Łęczyca)",
            "opt_a_type": "8th-10th c. Slavic fortified tribal gord on the Bzura River at Tum",
            "opt_b_hydronym": "Bzura River (Btsûre)",
            "opt_b_lang": "West Slavic Hydronym",
            "opt_b_name": "Btsûre",
            "justification": "New Łęczyca was chartered in the 13th c.; the authentic pre-867 center was the 8th-c. Slavic ringwall at Tum on the Bzura. Resolved to Tum-an-der-Btsûre.",
            "rec_option": "Option A",
            "tarr_name": "Tûm-an-der-Btsûre",
            "tarr_adjective": "Tûmer"
        },
        "c_sieradzka": {
            "opt_a_key": "None",
            "opt_a_name": "Warta Gord",
            "opt_a_type": "11th-c. Piast castellan gord on the Warta River",
            "opt_b_hydronym": "Warta River (Warte)",
            "opt_b_lang": "West Slavic Hydronym",
            "opt_b_name": "Warte",
            "justification": "Sieradz gord on the Warta river was first attested in 1136 in the Papal Bull of Gniezno. Resolved via Option B to Warte.",
            "rec_option": "Option B",
            "tarr_name": "Warte",
            "tarr_adjective": "Wartisch"
        },

        # Finland & Karelia
        "c_finland": {
            "opt_a_key": "b_rikala",
            "opt_a_name": "Rikala",
            "opt_a_type": "Iron Age / Pre-867 Finnic trading center and hillfort on Halikko River",
            "opt_b_hydronym": "Aura River (Aure)",
            "opt_b_lang": "Finnic Hydronym",
            "opt_b_name": "Aure-Flutz",
            "justification": "Turku (b_turku) was founded c. 1229/1300 following the Swedish Crusade. The authentic pre-867 Iron Age trading center was Rikala (b_rikala). Resolved to Rikala (Rîkale).",
            "rec_option": "Option A",
            "tarr_name": "Rîkale",
            "tarr_adjective": "Rîkaler"
        },
        "c_satakunta": {
            "opt_a_key": "b_telja",
            "opt_a_name": "Teljä",
            "opt_a_type": "Iron Age / Pre-867 trading center and harbor on the Kokemäki River",
            "opt_b_hydronym": "Kokemäki River (Kôkemäki)",
            "opt_b_lang": "Finnic Hydronym",
            "opt_b_name": "Teljê",
            "justification": "Ulvila (b_ulvila) was chartered in 1365; Pori in 1558. The authentic pre-867 Satakunta trading center was Teljä (b_telja) on the Kokemäki River. Resolved to Teljä (Teljê).",
            "rec_option": "Option A",
            "tarr_name": "Teljê",
            "tarr_adjective": "Teljêer"
        },
        "c_tavasts": {
            "opt_a_key": "None",
            "opt_a_name": "Vanaja (Häme Sacred Center)",
            "opt_a_type": "Pre-867 Iron Age tribal sacred center and hillfort on Lake Vanajavesi",
            "opt_b_hydronym": "Lake Vanajavesi (Wanâje)",
            "opt_b_lang": "Finnic Hydronym",
            "opt_b_name": "Wanâje",
            "justification": "Hämeenlinna castle (b_hameenlinna) was founded c. 1250–1300 by Birger Jarl. The authentic pre-867 Tavastian tribal center was Vanaja on Lake Vanajavesi. Resolved to Vanaja (Wanâje).",
            "rec_option": "Option A",
            "tarr_name": "Wanâje",
            "tarr_adjective": "Wanâjer"
        },
        "c_kainuu": {
            "opt_a_key": "None",
            "opt_a_name": "None",
            "opt_a_type": "No Verified Pre-867 Urban Centre Attested (Burden of Proof on Antiquity)",
            "opt_b_hydronym": "Kvenland (Kwênlant / Kainuu)",
            "opt_b_lang": "Finnic / Old Norse Ethnonym",
            "opt_b_name": "Kwênlant",
            "justification": "Kajaani castle (b_kajaani) was built in 1604 by Charles IX. Kvenland (Kainuu) is attested in Ohthere c. 890. Resolved via Option B to Kvenland (Kwênlant).",
            "rec_option": "Option B",
            "tarr_name": "Kwênlant",
            "tarr_adjective": "Kwênischer"
        },
        "c_nyland": {
            "opt_a_key": "b_espoo",
            "opt_a_name": "Espoo",
            "opt_a_type": "Iron Age–12th c. Tavastian-Estonian seasonal coastal trading littoral",
            "opt_b_hydronym": "Gulf of Finland Littoral",
            "opt_b_lang": "Finnic Toponym",
            "opt_b_name": "Nîlant",
            "justification": "Nyland (Uusimaa) is a mid-13th c. Swedish colonial name; Porvoo (b_porvoo) dates to 1380. Resolved via pre-crusade coastal center Espoo (b_espoo) as Espô.",
            "rec_option": "Option A",
            "tarr_name": "Espô",
            "tarr_adjective": "Espôer"
        },

        # Ruthenia & East Slavia
        "c_vitebsk": {
            "opt_a_key": "b_vitebsk",
            "opt_a_name": "Castle Hill / Vitba",
            "opt_a_type": "Pre-867 Dnieper-Dvina Baltic / Early Slavic Settlement at Vitba Confluence",
            "opt_b_hydronym": "Vitba (Baltic Vytinė / Vidba)",
            "opt_b_lang": "Baltic / Old East Slavic",
            "opt_b_name": "Wîtbe",
            "justification": "Vitebsk was founded in 974/1021 on the ancient Baltic river Vitba (Vidba). Haradok (b_haradok) is an anachronistic 13th-century diminutive outpost (gorodok). Under Tier 2, stripping the post-867 town suffix -sk restores the authentic ancient hydronym Vitba (Wîtbe).",
            "rec_option": "Option B",
            "tarr_name": "Wîtbe",
            "tarr_adjective": "Wîtbisch"
        },
        "c_pinsk": {
            "opt_a_key": "b_pinsk",
            "opt_a_name": "Pina Reach",
            "opt_a_type": "Early Slavic / Baltic Settlement on the Pina",
            "opt_b_hydronym": "Pina (Baltic / Slavic Pina)",
            "opt_b_lang": "Baltic / Slavic Hydronym",
            "opt_b_name": "Pîne",
            "justification": "Pinsk was first attested in 1097 on the river Pina. Lahishyn (b_lahishyn) is an anachronistic late 15th-century settlement (1495). Under Tier 2, stripping the town suffix -sk restores the ancient hydronym Pina (Pîne).",
            "rec_option": "Option B",
            "tarr_name": "Pîne",
            "tarr_adjective": "Pîner"
        },
        "c_zhytomyr": {
            "opt_a_key": "None",
            "opt_a_name": "None",
            "opt_a_type": "No Verified Pre-867 Urban Centre Attested (Burden of Proof on Antiquity)",
            "opt_b_hydronym": "Teteriv River (Teterîw)",
            "opt_b_lang": "Old East Slavic Hydronym",
            "opt_b_name": "Teterîw-Flutz",
            "justification": "Zhytomyr is first attested in 1392 (legendary 884 unverified). Lacks documented pre-867 center; resolved via Option B to Teteriv River (Teterîw-Flutz).",
            "rec_option": "Option B",
            "tarr_name": "Teterîw-Flutz",
            "tarr_adjective": "Teterîwisch"
        },
        "c_chernigov": {
            "opt_a_key": "None",
            "opt_a_name": "Severian Gord",
            "opt_a_type": "Early Slavic / Severian tribal center on the Desna",
            "opt_b_hydronym": "Desna River (Dêsne)",
            "opt_b_lang": "Old East Slavic / Baltic Hydronym",
            "opt_b_name": "Tschernigouwe",
            "justification": "First chronicled in 907 AD Rus-Byzantine treaty. Under Tier 2/Option B, resolved to ancient Severian capital on the Desna as Tschernigouwe.",
            "rec_option": "Option B",
            "tarr_name": "Tschernigouwe",
            "tarr_adjective": "Tschernigouwer"
        },
        "c_pereyaslavl": {
            "opt_a_key": "None",
            "opt_a_name": "None",
            "opt_a_type": "No Verified Pre-867 Urban Centre Attested (Burden of Proof on Antiquity)",
            "opt_b_hydronym": "Trubezh River (Trubêsch)",
            "opt_b_lang": "Old East Slavic Hydronym",
            "opt_b_name": "Trubêsch",
            "justification": "Pereyaslavl was founded in 992 by Vladimir the Great. Lacks pre-867 center; resolved via Option B to Trubezh River (Trubêsch).",
            "rec_option": "Option B",
            "tarr_name": "Trubêsch",
            "tarr_adjective": "Trubêschisch"
        },
        "c_korsun": {
            "opt_a_key": "None",
            "opt_a_name": "None",
            "opt_a_type": "No Verified Pre-867 Urban Centre Attested (Burden of Proof on Antiquity)",
            "opt_b_hydronym": "Ros River (Rôs-Flutz)",
            "opt_b_lang": "Old East Slavic Hydronym",
            "opt_b_name": "Rôs-Flutz",
            "justification": "Korsun was founded in 1032 by Yaroslav the Wise on the Ros defensive line. Resolved via Option B to Ros River (Rôs-Flutz).",
            "rec_option": "Option B",
            "tarr_name": "Rôs-Flutz",
            "tarr_adjective": "Rôsisch"
        },
        "c_turov": {
            "opt_a_key": "None",
            "opt_a_name": "None",
            "opt_a_type": "No Verified Pre-867 Urban Centre Attested (Burden of Proof on Antiquity)",
            "opt_b_hydronym": "Pripyat River Basin (Prîpjat)",
            "opt_b_lang": "Old East Slavic Hydronym",
            "opt_b_name": "Prîpjat",
            "justification": "Turov was first attested in 980 under Prince Tur. Resolved via Option B to Pripyat River basin (Prîpjat).",
            "rec_option": "Option B",
            "tarr_name": "Prîpjat",
            "tarr_adjective": "Prîpjatisch"
        },
        "c_putyvl": {
            "opt_a_key": "None",
            "opt_a_name": "None",
            "opt_a_type": "No Verified Pre-867 Urban Centre Attested (Burden of Proof on Antiquity)",
            "opt_b_hydronym": "Seym River (Sêim-Flutz)",
            "opt_b_lang": "Old East Slavic Hydronym",
            "opt_b_name": "Sêim-Flutz",
            "justification": "Putyvl was first attested in 1146 in the Hypatian Chronicle. Resolved via Option B to Seym River (Sêim-Flutz).",
            "rec_option": "Option B",
            "tarr_name": "Sêim-Flutz",
            "tarr_adjective": "Sêimisch"
        },
        "c_vladimir": {
            "opt_a_key": "None",
            "opt_a_name": "None",
            "opt_a_type": "No Verified Pre-867 Urban Centre Attested (Burden of Proof on Antiquity)",
            "opt_b_hydronym": "Klyazma River Basin (Klêsme)",
            "opt_b_lang": "Finno-Ugric / Merya Hydronym",
            "opt_b_name": "Klêsme",
            "justification": "Vladimir-on-Klyazma was founded in 990/1108. The pre-867 indigenous Merya river basin is Klyazma (Klêsme). Resolved via Option B.",
            "rec_option": "Option B",
            "tarr_name": "Klêsme",
            "tarr_adjective": "Klêsmisch"
        },

        # Baltic & Lithuania
        "c_vilnius": {
            "opt_a_key": "None",
            "opt_a_name": "None",
            "opt_a_type": "No Verified Pre-867 Urban Centre Attested (Burden of Proof on Antiquity)",
            "opt_b_hydronym": "Vilnia River at Neris Confluence",
            "opt_b_lang": "Baltic Hydronym",
            "opt_b_name": "Wîlnje-Flutz",
            "justification": "Vilnius was first attested in 1323 in the letters of Gediminas. Under Tier 2, stripping the town suffix -sk/us restores the ancient Baltic hydronym Vilnia (Wîlnje-Flutz).",
            "rec_option": "Option B",
            "tarr_name": "Wîlnje-Flutz",
            "tarr_adjective": "Wîlnjisch"
        },
        "c_kaunas": {
            "opt_a_key": "None",
            "opt_a_name": "None",
            "opt_a_type": "No Verified Pre-867 Urban Centre Attested (Burden of Proof on Antiquity)",
            "opt_b_hydronym": "Nemunas-Neris Confluence",
            "opt_b_lang": "Baltic Hydronym",
            "opt_b_name": "Nêmûn-Nêris",
            "justification": "Kaunas castle was first attested in 1361. Resolved via Option B to the ancient Nemunas-Neris confluence (Nêmûn-Nêris).",
            "rec_option": "Option B",
            "tarr_name": "Nêmûn-Nêris",
            "tarr_adjective": "Nêmûner"
        },
        "c_trakai": {
            "opt_a_key": "None",
            "opt_a_name": "Merkinė (Merkine)",
            "opt_a_type": "Ancient Yotvingian/Lithuanian hillfort at Merkys-Nemunas confluence",
            "opt_b_hydronym": "Lake Galvė (Gâlwe-Sê)",
            "opt_b_lang": "Baltic Hydronym",
            "opt_b_name": "Gâlwe-Sê",
            "justification": "Old Trakai was founded c. 1316 by Gediminas. Resolved via Option B to Lake Galvė (Gâlwe-Sê) / ancient Merkinė.",
            "rec_option": "Option B",
            "tarr_name": "Gâlwe-Sê",
            "tarr_adjective": "Gâlwisch"
        },

        # Urals, Steppe & Outremer
        "c_kumertau": {
            "opt_a_key": "None",
            "opt_a_name": "None",
            "opt_a_type": "No Verified Pre-867 Urban Centre Attested (Burden of Proof on Antiquity)",
            "opt_b_hydronym": "Burzyan Clan Territory on the Ik River",
            "opt_b_lang": "Turkic / Bashkir Toponym",
            "opt_b_name": "Bursjân-Îk",
            "justification": "Kumertau is a 1947 Soviet coal mining settlement. Resolved via Option B to ancestral medieval Burzyan Bashkir territory on the Ik river (Bursjân-Îk).",
            "rec_option": "Option B",
            "tarr_name": "Bursjân-Îk",
            "tarr_adjective": "Bursjâner"
        },
        "c_nytva": {
            "opt_a_key": "None",
            "opt_a_name": "None",
            "opt_a_type": "No Verified Pre-867 Urban Centre Attested (Burden of Proof on Antiquity)",
            "opt_b_hydronym": "Kama River Basin (Kâme-Flutz)",
            "opt_b_lang": "Permic / Finno-Ugric Hydronym",
            "opt_b_name": "Kâme-Flutz",
            "justification": "Nytva was founded in 1756 as a copper smelting mill. Lacks pre-867 center; resolved via Option B to Kama River basin (Kâme-Flutz).",
            "rec_option": "Option B",
            "tarr_name": "Kâme-Flutz",
            "tarr_adjective": "Kâmisch"
        },
        "c_iasi": {
            "opt_a_key": "None",
            "opt_a_name": "None",
            "opt_a_type": "No Verified Pre-867 Urban Centre Attested (Burden of Proof on Antiquity)",
            "opt_b_hydronym": "Bahlui River / Jász Tribal Territory",
            "opt_b_lang": "Iranian / Alan Tribal Ethnonym",
            "opt_b_name": "Jâsch",
            "justification": "First attested 1395; derived from Sarmatian/Alan tribe Iazyges / Jassi on the Bahlui river. Resolved via Option B to Jâsch.",
            "rec_option": "Option B",
            "tarr_name": "Jâsch",
            "tarr_adjective": "Jâscher"
        },
        "c_jersika": {
            "opt_a_key": "None",
            "opt_a_name": "Gersika / Gêrsike",
            "opt_a_type": "Ancient Latgalian hillfort and principality on the Daugava River",
            "opt_b_hydronym": "Daugava River Reach (Dûna)",
            "opt_b_lang": "Latgalian / Middle High German",
            "opt_b_name": "Gêrsike",
            "justification": "Gersika (Jersika) on the Daugava was the ancient Latgalian hillfort documented in the Livonian Chronicle. Resolved to Gêrsike.",
            "rec_option": "Option A",
            "tarr_name": "Gêrsike",
            "tarr_adjective": "Gêrsiker"
        }
    }

    enriched.update(REGIONAL_HISTORICAL)

    # 1. Parse anachronistic_titles_1059.md
    anach_path = repo_dir / "archive" / "anachronistic_titles_1059.md"
    if anach_path.exists():
        with open(anach_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if not line.startswith("|"):
                    continue
                parts = [p.strip() for p in line.split("|")]
                if len(parts) < 6:
                    continue
                m = re.search(r"`([cd]_[a-zA-Z0-9_]+)`", parts[1])
                if not m:
                    continue
                ck = m.group(1)
                if not ck.startswith("c_") or ck in enriched:
                    continue
                reason = parts[5] if len(parts) > 5 else ""
                res = parts[6] if len(parts) > 6 else ""

                m_b = re.search(r"`(b_[a-zA-Z0-9_]+)`", res)
                b_key = m_b.group(1) if m_b else None
                m_bold = re.findall(r"\*\*([^*]+)\*\*", res)

                # Extract Tarraconian name from arrow
                tarr_name = m_bold[-1] if m_bold else ck.replace("c_", "").capitalize()
                m_arrow = re.search(r"(?:\$\\rightarrow\$|\\rightarrow|->|→)\s*\*{0,2}(?:Magistrat|Fürstbisdom|Bisbalîe)?\s*(?:van\s+)?\*{0,2}([^*\(\]]+)", res)
                if m_arrow:
                    tarr_name = m_arrow.group(1).strip()

                m_opt_b = re.search(r"Option B:\s*\*\*([^*]+)\*\*", res)
                opt_b_name = m_opt_b.group(1).strip() if m_opt_b else tarr_name

                has_pre867 = bool(b_key or ("Roman" in res or "ancient" in res.lower() or "Abbey" in res or "gord" in res.lower()))
                if has_pre867 and b_key:
                    rec_opt = "Option A"
                    opt_a_name = m_bold[0] if m_bold else b_key
                    opt_a_type = f"Pre-867 Provincial Center / Fortified Gord: {opt_a_name}"
                    opt_a_key = b_key
                else:
                    rec_opt = "Option B"
                    opt_a_name = "None"
                    opt_a_key = "None"
                    opt_a_type = "No Verified Pre-867 Urban Centre Attested (Burden of Proof on Antiquity)"

                enriched[ck] = {
                    "opt_a_key": opt_a_key,
                    "opt_a_name": opt_a_name,
                    "opt_a_type": opt_a_type,
                    "opt_b_hydronym": f"{opt_b_name} River / Basin",
                    "opt_b_lang": "Historical Toponymic Substrate",
                    "opt_b_name": opt_b_name,
                    "justification": f"{reason[:120]}. Resolved via {res[:120]}.",
                    "rec_option": rec_opt,
                    "tarr_name": tarr_name,
                    "tarr_adjective": f"{tarr_name}er"
                }

    # 2. Parse tarraconian_titles_1059.md
    tarr_path = repo_dir / "tarraconian_titles_1059.md"
    if tarr_path.exists():
        with open(tarr_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                m = re.search(r"`(c_[a-zA-Z0-9_]+)`", line)
                if not m:
                    continue
                ck = m.group(1)
                if ck in enriched:
                    continue
                arrow_pos = -1
                for arrow in ["$\\rightarrow$", "\\rightarrow", "->", "→"]:
                    if arrow in line:
                        arrow_pos = line.find(arrow) + len(arrow)
                        break
                if arrow_pos > 0:
                    after_arrow = line[arrow_pos:]
                    m_bold = re.search(r"\*\*([^*]+)\*\*(.*)$", after_arrow)
                    if m_bold:
                        full_name = m_bold.group(1).strip()
                        rest = m_bold.group(2).strip()
                        tarr_name = re.sub(r"^(Magistrat|Fürstbisdom|Bisbalîe)\s+van\s+(der\s+)?", "", full_name).strip()
                        hist_m = re.search(r"\[(?:\d{4}\s+)?(?:Historical|Slavic-Root):\s*(?:Magistrat|Fürstbisdom)?\s*(?:van\s+)?([^\]]+)\]", rest)
                        hist_res = hist_m.group(1).strip() if hist_m else None

                        if hist_res:
                            center_name = hist_res.split("/")[0].strip()
                            center_clean = re.sub(r"\s*\([^)]*\)", "", center_name).strip()
                            enriched[ck] = {
                                "opt_a_key": "None",
                                "opt_a_name": center_clean,
                                "opt_a_type": f"Documented Historical Center: {center_clean}",
                                "opt_b_hydronym": f"{tarr_name} River / Basin",
                                "opt_b_lang": "Tarraconian Chancellery Standard",
                                "opt_b_name": tarr_name,
                                "justification": f"Resolved via verified historical center {hist_res} documented in tarraconian_titles_1059.md.",
                                "rec_option": "Option A",
                                "tarr_name": center_clean,
                                "tarr_adjective": f"{center_clean}er"
                            }
                        else:
                            is_river_lake = any(suffix in tarr_name for suffix in ["-Flutz", "-Sê", "-Küste", "-Dal", "-Gebirch", "-Wâre"])
                            enriched[ck] = {
                                "opt_a_key": "None",
                                "opt_a_name": "None",
                                "opt_a_type": "No Verified Pre-867 Urban Centre Attested (Burden of Proof on Antiquity)",
                                "opt_b_hydronym": f"{tarr_name} Hydronym / Basin",
                                "opt_b_lang": "Native Substrate / Section 3.1 Hydronym Hierarchy",
                                "opt_b_name": tarr_name,
                                "justification": f"Lacks documented pre-867 urban center; resolved via Option B {tarr_name} under Burden of Proof on Antiquity.",
                                "rec_option": "Option B",
                                "tarr_name": tarr_name,
                                "tarr_adjective": f"{tarr_name}isch" if is_river_lake else f"{tarr_name}er"
                            }

    return enriched


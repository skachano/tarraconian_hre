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
    'c_dorohychyn': (1142, 'high_medieval_foundation', 'Hypatian Chronicle', True, 'First mentioned 1142 in Hypatian Chronicle on Western Bug; ancient territory of Buzhane; pre-867 hydronym is Western Bug (Bûch)'),
    'c_berestye': (850, 'archaeology', 'Brest archaeological museum / Berestye gord', False, 'Pre-867 East Slavic tribal gord and portage at Bug-Mukhavets confluence'),
    'c_halych': (800, 'archaeology', 'Halych-Krylos archaeological complex', False, 'Ancient capital gord of White Croats on Dniester, 8th-9th c. salt trade center'),
    'c_lviv': (1256, 'high_medieval_foundation', 'Galician-Volhynian Chronicle', False, 'Founded c. 1256 by Danylo of Halych; pre-867 center is princely capital Zvenyhorod'),
    'c_galich': (898, 'high_medieval_foundation', 'Primary Chronicle', True, 'First mentioned 898 AD; ancient salt hill / Celtic hal- root on the Dniester'),
    'c_zaslavl': (985, 'high_medieval_foundation', 'Primary Chronicle', False, 'Founded c. 985 by Vladimir for Rogneda (Izyaslavl)'),
    'c_volodymyr': (988, 'high_medieval_foundation', 'Primary Chronicle', False, 'Founded 988 by Vladimir the Great; pre-867 Dulebe/Volhynian capital is Zimne hillfort (Simne) on Luga River'),
    'c_pskov': (800, 'archaeology', 'Pskov Kremlin excavations', False, 'Pre-867 Slavic-Finnic trading settlement at Velikaya-Pskova confluence; recorded in Primary Chronicle under 903 AD'),
    'c_cetatea_alba': (-600, 'classical_antiquity', 'Classical Greek sources (Herodotus)', False, 'Ancient Milesian Greek colony Tyras (6th c. BC) and Byzantine Moncastro on Dniester Liman'),
    'c_chilia': (-500, 'classical_antiquity', 'Classical Greek sources', False, 'Ancient Greek/Byzantine Achilleia on the Danube delta'),
    'c_luneburg': (795, 'early_chronicle', 'Royal Frankish Annals', False, 'Attested 795 AD as Hliuni / Luni in Saxon wars of Charlemagne; salt production center on Ilmenau'),
    'c_mersenburg': (830, 'early_chronicle', 'Hersfeld Tithe Register', False, 'Attested c. 830-850 AD as Mersiburc on the Saale'),
    'c_meissen': (800, 'archaeology', 'Daleminzi Slavic excavations', True, 'Pre-867 Slavic Misni settlement on Elbe/Triebisch; Daleminzi tribal territory'),
    'c_brene': (800, 'archaeology', 'Hevelli Slavic excavations', False, 'Ancient Hevelli tribal capital Brenna on the Havel River'),
    'c_juterbog': (800, 'archaeology', 'Slavic Jutriboc excavations', False, 'Ancient Slavic tribal gord Jutriboc'),
    'c_csongrad': (800, 'archaeology', 'Slavic/Avar excavations', False, 'Early medieval Slavic Črn grad (Black Castle) on the Tisza and Körös'),
    'c_beograd': (-279, 'classical_antiquity', 'Classical Greco-Roman & Byzantine sources', False, 'Celtic/Roman Singidunum 3rd c. BC; Slavic Belgrad attested 878 AD on Danube-Sava confluence'),
    'c_praha': (800, 'archaeology', 'Prague basin excavations / Cosmas of Prague', False, 'Continuous pre-867 Slavic settlement & Celtic oppidum (Závist) on Vltava rapids; Bohemians / Přemyslid center'),
    'c_prerov': (800, 'archaeology', 'Great Moravian archaeological complex', False, '8th-9th c. Great Moravian fortified center on Bečva River'),

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
    'c_saratov': (1590, 'high_medieval_foundation', 'Tsarist Fortress Charter', True, 'Tsarist fortress founded 1590 over ancestral Turkic geographic feature Sary Tau (Yellow Mountain -> Goltberch)'),

    # =========================================================================
    # 1171 FRONTIER: INDIA, MAINLAND SEA & MARITIME SEA (TIER 1, 2 & 3)
    # =========================================================================
    # Attested Pre-867 Maritime SEA Entrepots (Tier 1 <= 867 AD)
    'c_MAL_kedah': (400, 'epigraphy', 'Bujang Valley Sanskrit Inscriptions', False, '4th-5th c. AD Kataha / Kadaram entrepot in Bujang Valley'),
    'c_MAL_gangganegara': (450, 'archaeology', 'Beruas / Perak Classical Annals', False, '5th-c. Hindu-Malay kingdom of Gangga Negara'),
    'c_THAI_tambralinga': (150, 'classical_antiquity', 'Ptolemy / 775 AD Ligor Stele', False, 'Ancient Isthmian kingdom Tambralinga (775 AD Wat Sema Mueang stele)'),
    'c_THAI_takua_pa': (200, 'classical_antiquity', 'Ptolemy / Tang / Takuapa Tamil Stele', False, 'Classical entrepot Takkola / Takuapa on Kra Isthmus'),
    'c_MAL_patani': (200, 'early_chronicle', 'Liangshu / Chinese Annals', False, 'Ancient 2nd-c. Malayic kingdom of Langkasuka'),
    'c_BOR_santubong': (650, 'archaeology', 'Sarawak River Delta Excavations', False, '7th-c. Tang-era iron smelting and trade port at Santubong'),
    'c_BOR_brunei': (600, 'early_chronicle', 'Chinese Annals (Po-ni)', False, 'Early maritime polity of Po-ni / Poni in northwestern Borneo'),
    'c_SUM_bangka-belitung': (686, 'epigraphy', 'Kota Kapur Inscription (686 AD)', False, 'Old Malay Srivijayan inscription of 686 AD at Kota Kapur, Bangka'),
    'c_SUM_palembang': (682, 'epigraphy', 'Kedukan Bukit Inscription (682 AD)', False, 'Capital of Srivijaya attested in 682-686 AD Sabokingking & Kedukan Bukit stelae'),
    'c_SUM_jambi': (644, 'early_chronicle', 'Yijing / Tang Huiyao', False, 'Kingdom of Malayu attested sending embassy to Tang China in 644 AD'),

    # Tier 2 Post-867 Geographic / Topographic / Directional Frontier Titles
    'c_sagya': (1073, 'monastic_chronicle', 'Sakya Chronicles', True, '1073 AD monastery named after indigenous Tibetan terrain Sa-skya (Pale/Grey Soil)'),
    'c_BOR_kutai_utara': (1999, 'modern_geographic', 'Indonesian Administrative Geography', True, 'Directional subdivision ("North Kutai") over Mahakam-Sangkulirang coastal basin'),
    'c_BOR_kutai_jauh': (1999, 'modern_geographic', 'Indonesian Administrative Geography', True, 'Directional subdivision ("Far Kutai") on the Upper Mahakam basin'),
    'c_SuMa_banggai_utara': (1999, 'modern_geographic', 'Indonesian Administrative Geography', True, 'Directional subdivision ("North Banggai") over Tomini-Togian Gulf'),
    'c_PHI_cagayan_valley': (1900, 'modern_geographic', 'Geographic Valley Descriptor', True, 'River valley descriptor named after the Cagayan River basin'),
    'c_PHI_south_palawan': (1900, 'modern_geographic', 'Geographic Island Descriptor', True, 'Directional descriptor over ancestral Tagbanwa-Palawan island territory'),

    # Tier 3 Post-867 / Colonial Anachronisms in 1171 Frontier (Resolved via Options A/B)
    'c_vijayapura': (1095, 'high_medieval_foundation', 'Sena Dynastic Records', False, 'Post-1095 Sena seat; pre-867 center is ancient Bishnupur / Mallabhum (b_visnupura)'),
    'c_laksmanavati': (1178, 'high_medieval_foundation', 'Sena Epigraphy', False, 'Named after Laksmana Sena (r. 1178-1206, post-1171); resolves to Ramavati (b_ramavati)'),
    'c_damin_i_koh': (1832, 'colonial_survey', 'East India Company Survey', False, '1832 British colonial term; resolves to ancient Kajangala / Vaidyanath (b_deogarh2)'),
    'c_midnapore': (1760, 'colonial_survey', 'Bengal Presidency Gazetteer', False, 'Colonial English spelling Midnapore; resolves to classical 6th-c. Dandabhukti (b_dantan)'),
    'c_ubon_ratchathani': (1786, 'modern_foundation', 'Rattanakosin Chronicle', False, 'Founded 1786; resolves to ancient Mun River basin (Mûndal)'),
    'c_IDO_barat_daya': (1945, 'modern_geographic', 'Indonesian Republic Administration', False, 'Modern Indonesian directional term ("Southwest"); resolves to ancient island Wetar (b_IDO_Wetar)'),
    'c_papua_selatan': (2022, 'modern_geographic', 'Modern Provincial Act', False, 'Modern directional term ("South Papua"); resolves to indigenous Asmat territory'),
    'c_kepala_burung': (1950, 'modern_geographic', 'Modern Dutch/Indonesian Toponym', False, 'Modern calque "Bird\'s Head"; resolves to indigenous gulf Bintuni'),
    'c_MAL_johor': (1528, 'high_medieval_foundation', 'Malay Annals', False, 'Johor founded 1528; resolves to pre-867 maritime emporium Temasek / Tumasik (b_MAL_Tumasik)'),
    'c_SUM_east_sumatra': (1948, 'modern_geographic', 'Modern English/Colonial Descriptor', False, 'Modern English geographic label; pre-867 river basin Mesuji (b_SUM_Mesuji)'),
    'c_SUM_pekanbaru': (1784, 'modern_foundation', 'Siak Sultanate Record', False, 'Founded 1784 ("New Market"); resolves to river district Rokan Hilir (b_SUM_Rokan_Hilir)'),
    'c_BOR_kudat': (1881, 'colonial_survey', 'British North Borneo Charter', False, 'Founded 1881 by British North Borneo Co.; resolves to ancient bay Marudu (b_BOR_Marudu)'),
    'c_BOR_lahad_datu': (1879, 'colonial_survey', 'Sulu-Sabah Charter', False, '19th-c. colonial settlement; resolves to ancient Sulu-Borneo strait Sibutu (b_BOR_Sibutu)'),
    'c_thanbyuzayat': (1942, 'modern_foundation', '20th-c. Railway Town', False, 'Modern railway town; resolves to ancient Mon port Dawei (b_dawei)'),
    'c_ava': (1364, 'high_medieval_foundation', 'Burmese Royal Chronicles', False, 'Ava founded 1364 by Thado Minbya; resolves to ancient Irrawaddy shrine-town Taungbyon (b_taungbyon)'),
    'c_toungoo': (1279, 'high_medieval_foundation', 'Toungoo Chronicle', False, 'Toungoo founded 1279/1510; resolves to ancient Sittaung valley settlement Swa (b_swa)'),
    'c_charaideo': (1253, 'high_medieval_foundation', 'Ahom Buranjis', False, 'Ahom royal capital Che-Rai-Doi founded 1253 by Sukaphaa; pre-Ahom Patkai Range (b_patkai)'),
    'c_dimapur': (1150, 'high_medieval_foundation', 'Dimasa Kachari Tradition', False, 'Dimasa capital founded 12th-13th c.; resolves to ancient Dhansiri River basin (Dansîri)'),
    'c_goalpara': (1765, 'colonial_survey', 'Mughal-British Frontier Register', False, '17th-18th c. frontier outpost; resolves to classical Kamakhya / Pragjyotisha (b_kamakhya)'),
    'c_kamatapur': (1250, 'high_medieval_foundation', 'Kamata Chronicle', False, 'Founded mid-13th c. by Sandhya of Kamata; resolves to 6th-c. fortified city Bhitagarh (b_bhitagarh)'),
    'c_nabadwipa': (1063, 'high_medieval_foundation', 'Sena Gazetteer', False, 'Nabadwip founded c. 1063; resolves to ancient Shakta Pitha Attahasa (b_attahasa)'),
    'c_bangaon': (990, 'high_medieval_foundation', 'Pala Copperplate', False, 'Late Pala/colonial name; resolves to pre-867 Burhi Gandak river basin'),
    'c_saptagrama': (1100, 'high_medieval_foundation', 'Bengal Epigraphy', False, 'Emerged c. 11th-12th c. succeeding Tamralipti; resolves to classical Bhagirathi river basin'),
    'c_racakonda': (1365, 'high_medieval_foundation', 'Recherla Nayaka Chronicle', False, 'Built 1360s; resolves to pre-867 Chalukya/Rashtrakuta hillfort Nalgonda (b_nalgonda)'),
    'c_candragiri': (1000, 'high_medieval_foundation', 'Yadavaraya Record', False, 'Yadavaraya fort c. 1000 AD; resolves to 9th-c. Pallava/Chola seat Melpadi (b_melpadi)'),
    'c_muluvagil': (1050, 'high_medieval_foundation', 'Hoysala Border Record', False, 'Hoysala-era frontier post; resolves to 4th-c. Western Ganga capital Kuvalala / Kolar (b_kuvalala)'),
    'c_penugonda': (1350, 'high_medieval_foundation', 'Vijayanagara Chronicle', False, '14th-c. fort; resolves to 8th-c. Nolamba/Ganga hillfort Nandagiri (b_nandi)'),
    'c_batticaloa': (1638, 'colonial_survey', 'Dutch East India Record', False, 'Colonial corruption of Mattakkalappu; resolves to 3rd-c. BC Mahavamsa city Dighavapi (b_dighavapi)'),
    'c_yamethin': (1100, 'high_medieval_foundation', 'Bagan Inscriptions', False, 'Bagan/Pinya frontier town; resolves to 1st-5th c. AD Pyu capital Beikthano (b_peikthanomyo)'),
    'c_sagaing': (1315, 'high_medieval_foundation', 'Sagaing Chronicle', False, 'Founded 1315 by Athinkhaya; resolves to ancient Mu River basin (Mû-Flutz)'),
    'c_nyaungshwe': (1359, 'high_medieval_foundation', 'Shan Saopha Chronicle', False, 'Founded 1359 by Hso Hom Hpa; resolves to ancient Lake Inle basin (Inle-Sê)'),
    'c_sukhothai': (1238, 'high_medieval_foundation', 'Wat Si Chum Inscription', False, 'Thai kingdom founded 1238; resolves to older Dvaravati/Khmer river city Chaliang (b_si_satchanalai)'),
    'c_phetchabun': (1250, 'high_medieval_foundation', 'Sukhothai Frontier Charter', False, 'Late medieval town; resolves to 3rd-8th c. AD Dvaravati/pre-Angkorian city Sri Deva / Si Thep (b_srideb)'),
    'c_mukdahan': (1770, 'modern_foundation', 'Thonburi Chronicle', False, 'Founded 1770 AD by Chao Kinnaree; resolves to ancient Chenla seat Nong Han Luang (b_sakhon_nakhon)'),
    'c_SUM_dharmasraya': (1050, 'high_medieval_foundation', 'Melayu Grahi Stele', False, 'Post-1025 Melayu upstream seat; resolves to ancient Srivijayan Batanghari River basin'),
    'c_BOR_sukadana': (1365, 'high_medieval_foundation', 'Nagarakretagama', False, 'Late medieval sultanate; resolves to classical Bornean coastal polity Tanjungpura'),
    'c_BOR_martapura': (1630, 'high_medieval_foundation', 'Banjar Chronicle', False, 'Banjar Martapura dates to 1630; resolves to 400 AD Mulavarman Sanskrit Yupa site Muara Kaman (b_BOR_Muara_Kaman)'),
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
    # Ancient Indian, Sri Lankan & Gandharan Civilizations
    'k_punjab', 'k_sindh', 'k_kashmir', 'k_delhi', 'k_kabulistan', 'k_himalaya',
    'k_bengal', 'k_bihar', 'k_orissa', 'k_kamarupa', 'k_gondwana',
    'k_andhra', 'k_karnata', 'k_lanka', 'k_maharastra', 'k_tamilakam', 'k_telingana',
    # Classical Mainland Southeast Asia, Java & Sumatra Indic Civilizations
    'k_pagan', 'k_dvaravati', 'k_funan', 'k_chenla', 'k_champa',
    'k_yavakadvipa', 'k_malayadvipa',
    # Dynamic Classical Mediterranean / Western / Sudanese Imperial Kingdoms
    'x_script_4328', 'x_script_6717', 'x_script_3965', 'x_script_7238',
    'x_script_4359', 'x_script_4774', 'x_script_6373', 'x_script_2942',
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
        "c_dorohychyn": {
            "opt_a_key": "None",
            "opt_a_name": "None",
            "opt_a_type": "No Verified Pre-867 Urban Centre Attested (Burden of Proof on Antiquity)",
            "opt_b_hydronym": "Western Bug River Reach",
            "opt_b_lang": "Old East Slavic / West Slavic Hydronym (Bugъ)",
            "opt_b_name": "Bûch",
            "justification": "Drohiczyn was first attested in 1142 in the Hypatian Chronicle as a frontier customs gord on the Western Bug. Resolved via Option B to the authentic pre-867 Western Bug River hydronym (Bûch).",
            "rec_option": "Option B",
            "tarr_name": "Bûch",
            "tarr_adjective": "Bûchisch"
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
        "c_barlad": {
            "opt_a_key": "None",
            "opt_a_name": "None",
            "opt_a_type": "No Verified Pre-867 Urban Centre Attested (Burden of Proof on Antiquity)",
            "opt_b_hydronym": "Bârlad River Basin (Berlat)",
            "opt_b_lang": "Slavic / Vlach Hydronym",
            "opt_b_name": "Berlat",
            "justification": "Town first attested in 1159 Hypatian Chronicle; restores the pre-urban Bârlad river hydronym (Berlat).",
            "rec_option": "Option B",
            "tarr_name": "Berlat",
            "tarr_adjective": "Berlater"
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
        },
        "c_saratov": {
            "opt_a_key": "None",
            "opt_a_name": "None",
            "opt_a_type": "No Verified Pre-867 Urban Centre Attested (Burden of Proof on Antiquity)",
            "opt_b_hydronym": "Sary Tau (Yellow Mountain / Volga Reach)",
            "opt_b_lang": "Turkic Toponymic Substrate Calque",
            "opt_b_name": "Goltberch",
            "justification": "Tsarist fortress Saratov founded 1590 over ancestral Turkic geographic feature Sary Tau ('Yellow Mountain'); calqued as Goltberch.",
            "rec_option": "Option B",
            "tarr_name": "Goltberch",
            "tarr_adjective": "Goltbercher"
        },
        # 1171 Frontier Additions: Bengal, Assam, Bihar, Deccan, Lanka, SEA & Nusantara
        "c_vijayapura": {
            "opt_a_key": "b_visnupura",
            "opt_a_name": "Bishnupur (Visnupura)",
            "opt_a_type": "Pre-1095 Sena / Malla Seat (b_visnupura)",
            "opt_b_hydronym": "Damodar-Dwarakeswar Basin",
            "opt_b_lang": "Sanskrit / Bengali",
            "opt_b_name": "Wischnupur",
            "justification": "Vijayapura was founded as a post-1095 Sena capital; resolves via Option A to ancient Mallabhum center Bishnupur (Wischnupur).",
            "rec_option": "Option A",
            "tarr_name": "Wischnupur",
            "tarr_adjective": "Wischnupurer"
        },
        "c_laksmanavati": {
            "opt_a_key": "b_ramavati",
            "opt_a_name": "Ramavati",
            "opt_a_type": "Pre-1178 Pala Imperial Seat (b_ramavati)",
            "opt_b_hydronym": "Mahananda-Ganges Confluence",
            "opt_b_lang": "Sanskrit / Prakrit",
            "opt_b_name": "Râmâwatî",
            "justification": "Laksmanavati was named after Laksmana Sena (r. 1178-1206, after 1171); resolves via Option A to Pala imperial seat Ramavati (Râmâwatî).",
            "rec_option": "Option A",
            "tarr_name": "Râmâwatî",
            "tarr_adjective": "Râmâwatîer"
        },
        "c_midnapore": {
            "opt_a_key": "b_dantan",
            "opt_a_name": "Dandabhukti (Dantan)",
            "opt_a_type": "6th-c. Gupta / Shashanka Provincial Capital (b_dantan)",
            "opt_b_hydronym": "Subarnarekha-Kangsabati Basin",
            "opt_b_lang": "Sanskrit Provincial Term",
            "opt_b_name": "Dandabukti",
            "justification": "Colonial English spelling Midnapore; resolves via Option A to ancient Gupta/Shashanka province Dandabhukti (b_dantan).",
            "rec_option": "Option A",
            "tarr_name": "Dandabukti",
            "tarr_adjective": "Dandabuktier"
        },
        "c_charaideo": {
            "opt_a_key": "b_patkai",
            "opt_a_name": "Patkai Range",
            "opt_a_type": "Pre-Ahom Oronymic Eastern March (b_patkai)",
            "opt_b_hydronym": "Patkai Range / Dikhau River Basin",
            "opt_b_lang": "Tibeto-Burman Oronym",
            "opt_b_name": "Patkâi",
            "justification": "Charaideo (Che-Rai-Doi) was founded in 1253 by Ahom king Sukaphaa; resolves via pre-Ahom oronym Patkai Range (Patkâi).",
            "rec_option": "Option A",
            "tarr_name": "Patkâi",
            "tarr_adjective": "Patkâier"
        },
        "c_dimapur": {
            "opt_a_key": "None",
            "opt_a_name": "None",
            "opt_a_type": "No Verified Pre-867 Urban Centre Attested",
            "opt_b_hydronym": "Dhansiri River Basin",
            "opt_b_lang": "Indo-Aryan / Bodo-Kachari Hydronym",
            "opt_b_name": "Dansîri",
            "justification": "Dimasa capital Dimapur emerged in the 12th-13th c.; resolves via Option B to the ancient Dhansiri River basin (Dansîri).",
            "rec_option": "Option B",
            "tarr_name": "Dansîri",
            "tarr_adjective": "Dansîrier"
        },
        "c_goalpara": {
            "opt_a_key": "b_kamakhya",
            "opt_a_name": "Kamakhya (Pragjyotisa)",
            "opt_a_type": "4th-c. Allahabad Pillar / Xuanzang Sacred Metropolis (b_kamakhya)",
            "opt_b_hydronym": "Brahmaputra (Lauhitya) Basin",
            "opt_b_lang": "Classical Sanskrit",
            "opt_b_name": "Kamâkje",
            "justification": "Goalpara is an 18th-c. Mughal/British revenue outpost; resolves via Option A to ancient classical sacred center Kamakhya (Kamâkje).",
            "rec_option": "Option A",
            "tarr_name": "Kamâkje",
            "tarr_adjective": "Kamâkjer"
        },
        "c_kamatapur": {
            "opt_a_key": "b_bhitagarh",
            "opt_a_name": "Bhitagarh",
            "opt_a_type": "6th-7th c. Fortified Ancient Kamarupa Trade City (b_bhitagarh)",
            "opt_b_hydronym": "Karatoya-Tista Basin",
            "opt_b_lang": "Ancient Kamarupan",
            "opt_b_name": "Bîtâgar",
            "justification": "Kamatapur was founded in the mid-13th c. by Sandhya of Kamata; resolves via Option A to the 6th-c. fortified trade city Bhitagarh (Bîtâgar).",
            "rec_option": "Option A",
            "tarr_name": "Bîtâgar",
            "tarr_adjective": "Bîtâgarer"
        },
        "c_nabadwipa": {
            "opt_a_key": "b_attahasa",
            "opt_a_name": "Attahasa",
            "opt_a_type": "Ancient Shakta Pitha Centre (b_attahasa)",
            "opt_b_hydronym": "Bhagirathi Delta",
            "opt_b_lang": "Classical Sanskrit",
            "opt_b_name": "Attahâse",
            "justification": "Nabadwipa emerged after c. 1063 under the Senas; resolves via Option A to the ancient Shakta Pitha site Attahasa (Attahâse).",
            "rec_option": "Option A",
            "tarr_name": "Attahâse",
            "tarr_adjective": "Attahâser"
        },
        "c_bangaon": {
            "opt_a_key": "None",
            "opt_a_name": "None",
            "opt_a_type": "No Verified Pre-867 Urban Centre Attested",
            "opt_b_hydronym": "Burhi Gandak River Basin",
            "opt_b_lang": "Indo-Aryan Hydronym",
            "opt_b_name": "Bûri-Gandach",
            "justification": "Bangaon is a post-867 Pala/colonial settlement; resolves via Option B to the ancient Burhi Gandak river basin (Bûri-Gandach).",
            "rec_option": "Option B",
            "tarr_name": "Bûri-Gandach",
            "tarr_adjective": "Bûri-Gandacher"
        },
        "c_saptagrama": {
            "opt_a_key": "None",
            "opt_a_name": "None",
            "opt_a_type": "No Verified Pre-867 Urban Centre Attested",
            "opt_b_hydronym": "Bhagirathi River Basin",
            "opt_b_lang": "Classical Sanskrit Hydronym",
            "opt_b_name": "Bagîratî",
            "justification": "Saptagrama rose in the 11th-13th c. as Tamralipti silted up; resolves via Option B to the classical Bhagirathi River (Bagîratî).",
            "rec_option": "Option B",
            "tarr_name": "Bagîratî",
            "tarr_adjective": "Bagîratîer"
        },
        "c_racakonda": {
            "opt_a_key": "b_nalgonda",
            "opt_a_name": "Nalgonda (Nallagonda)",
            "opt_a_type": "Pre-867 Chalukya / Rashtrakuta Hillfort (b_nalgonda)",
            "opt_b_hydronym": "Musi River Basin",
            "opt_b_lang": "Telugu / Deccani",
            "opt_b_name": "Nalgonde",
            "justification": "Rachakonda was built in the 1360s by Recherla Nayakas; resolves via Option A to older Chalukya hillfort Nalgonda (Nalgonde).",
            "rec_option": "Option A",
            "tarr_name": "Nalgonde",
            "tarr_adjective": "Nalgonder"
        },
        "c_candragiri": {
            "opt_a_key": "b_melpadi",
            "opt_a_name": "Melpadi (Merpadi)",
            "opt_a_type": "9th-c. Pallava / Chola Temple Town (b_melpadi)",
            "opt_b_hydronym": "Palar-Swarnamukhi Basin",
            "opt_b_lang": "Tamil / Telugu",
            "opt_b_name": "Melpâdi",
            "justification": "Chandragiri fort dates to c. 1000 AD under Yadavarayas; resolves via Option A to ancient Pallava border city Melpadi (Melpâdi).",
            "rec_option": "Option A",
            "tarr_name": "Melpâdi",
            "tarr_adjective": "Melpâdier"
        },
        "c_muluvagil": {
            "opt_a_key": "b_kuvalala",
            "opt_a_name": "Kuvalala (Kolar)",
            "opt_a_type": "4th-c. Western Ganga Capital Kuvalalapura (b_kuvalala)",
            "opt_b_hydronym": "Palar Upper Plateau",
            "opt_b_lang": "Kannada / Sanskrit",
            "opt_b_name": "Kuwalâle",
            "justification": "Mulbagal is a post-1050 Hoysala/Vijayanagara frontier pass; resolves via Option A to the 350 AD Western Ganga capital Kuvalala (Kuwalâle).",
            "rec_option": "Option A",
            "tarr_name": "Kuwalâle",
            "tarr_adjective": "Kuwalâler"
        },
        "c_penugonda": {
            "opt_a_key": "b_nandi",
            "opt_a_name": "Nandagiri (Nandi Hills)",
            "opt_a_type": "8th-9th c. Nolamba / Ganga Hillfort (b_nandi)",
            "opt_b_hydronym": "Penner Upper Basin",
            "opt_b_lang": "Kannada / Sanskrit",
            "opt_b_name": "Nandagiri",
            "justification": "Penukonda is a 14th-c. Vijayanagara stronghold; resolves via Option A to the ancient 8th-c. Nolamba hillfort Nandagiri (b_nandi).",
            "rec_option": "Option A",
            "tarr_name": "Nandagiri",
            "tarr_adjective": "Nandagirier"
        },
        "c_batticaloa": {
            "opt_a_key": "b_dighavapi",
            "opt_a_name": "Dighavapi",
            "opt_a_type": "3rd-c. BC Sacred Mahavamsa City (b_dighavapi)",
            "opt_b_hydronym": "Gal Oya Basin",
            "opt_b_lang": "Pali / Sinhala",
            "opt_b_name": "Dîgawâpi",
            "justification": "Batticaloa is a colonial corruption of Mattakkalappu; resolves via Option A to ancient Mahavamsa city Dighavapi (Dîgawâpi).",
            "rec_option": "Option A",
            "tarr_name": "Dîgawâpi",
            "tarr_adjective": "Dîgawâpier"
        },
        "c_yamethin": {
            "opt_a_key": "b_peikthanomyo",
            "opt_a_name": "Beikthano (Visnupura)",
            "opt_a_type": "1st-5th c. AD Pyu Capital City (b_peikthanomyo)",
            "opt_b_hydronym": "Yin Chaung Basin",
            "opt_b_lang": "Pyu / Burmese",
            "opt_b_name": "Beiktanô",
            "justification": "Yamethin is a Bagan/Pinya frontier town; resolves via Option A to the 1st-5th c. AD Pyu metropolis Beikthano (Beiktanô).",
            "rec_option": "Option A",
            "tarr_name": "Beiktanô",
            "tarr_adjective": "Beiktanôer"
        },
        "c_sagaing": {
            "opt_a_key": "None",
            "opt_a_name": "None",
            "opt_a_type": "Pre-867 Halin already mapped on c_hanlan; uses Mu River hydronym",
            "opt_b_hydronym": "Mu River Basin",
            "opt_b_lang": "Burmese Hydronym",
            "opt_b_name": "Mû-Flutz",
            "justification": "Sagaing was founded in 1315 AD by Athinkhaya; resolves via Option B to the ancient Mu River basin (Mû-Flutz).",
            "rec_option": "Option B",
            "tarr_name": "Mû-Flutz",
            "tarr_adjective": "Mû-Flützer"
        },
        "c_nyaungshwe": {
            "opt_a_key": "None",
            "opt_a_name": "None",
            "opt_a_type": "No Verified Pre-867 Urban Centre Attested",
            "opt_b_hydronym": "Lake Inle Basin",
            "opt_b_lang": "Shan / Tibeto-Burman Hydronym",
            "opt_b_name": "Inle-Sê",
            "justification": "Nyaungshwe (Yawnghwe) was founded in 1359 AD by Shan Saopha Hso Hom Hpa; resolves via Option B to Lake Inle basin (Inle-Sê).",
            "rec_option": "Option B",
            "tarr_name": "Inle-Sê",
            "tarr_adjective": "Inle-Sêer"
        },
        "c_thanbyuzayat": {
            "opt_a_key": "b_dawei",
            "opt_a_name": "Dawei",
            "opt_a_type": "Ancient Mon / Dvaravati Coastal Port (b_dawei)",
            "opt_b_hydronym": "Dawei Estuary",
            "opt_b_lang": "Mon / Burmese",
            "opt_b_name": "Dawêi",
            "justification": "Thanbyuzayat is a modern railway settlement; resolves via Option A to ancient Mon port Dawei (Dawêi).",
            "rec_option": "Option A",
            "tarr_name": "Dawêi",
            "tarr_adjective": "Dawêier"
        },
        "c_ava": {
            "opt_a_key": "b_taungbyon",
            "opt_a_name": "Taungbyon",
            "opt_a_type": "Ancient Irrawaddy Shrine-Town (b_taungbyon)",
            "opt_b_hydronym": "Myitnge-Irrawaddy Confluence",
            "opt_b_lang": "Burmese",
            "opt_b_name": "Toungbjôn",
            "justification": "Ava (Inwa) was founded in 1364 AD; resolves via Option A to ancient Irrawaddy town Taungbyon (Toungbjôn).",
            "rec_option": "Option A",
            "tarr_name": "Toungbjôn",
            "tarr_adjective": "Toungbjôner"
        },
        "c_toungoo": {
            "opt_a_key": "b_swa",
            "opt_a_name": "Swa",
            "opt_a_type": "Ancient Sittaung Valley Town (b_swa)",
            "opt_b_hydronym": "Sittaung Upper Basin",
            "opt_b_lang": "Burmese",
            "opt_b_name": "Swâ",
            "justification": "Toungoo was founded 1279/1510 AD; resolves via Option A to ancient Sittaung valley town Swa (Swâ).",
            "rec_option": "Option A",
            "tarr_name": "Swâ",
            "tarr_adjective": "Swâer"
        },
        "c_sukhothai": {
            "opt_a_key": "b_si_satchanalai",
            "opt_a_name": "Chaliang (Si Satchanalai)",
            "opt_a_type": "Ancient Dvaravati / Pre-Khmer Yom River Seat (b_si_satchanalai)",
            "opt_b_hydronym": "Yom River Basin",
            "opt_b_lang": "Mon-Khmer / Tai",
            "opt_b_name": "Tschaljâng",
            "justification": "Sukhothai emerged c. 1238 AD; resolves via Option A to the older Dvaravati-Khmer settlement Chaliang (Tschaljâng) on the Yom river.",
            "rec_option": "Option A",
            "tarr_name": "Tschaljâng",
            "tarr_adjective": "Tschaljânger"
        },
        "c_phetchabun": {
            "opt_a_key": "b_srideb",
            "opt_a_name": "Sri Deva (Si Thep)",
            "opt_a_type": "3rd-8th c. AD Dvaravati / Pre-Angkorian Metropolis (b_srideb)",
            "opt_b_hydronym": "Pa Sak River Basin",
            "opt_b_lang": "Sanskrit / Mon",
            "opt_b_name": "Srî Dêwa",
            "justification": "Phetchabun is a late Sukhothai/Ayutthaya town; resolves via Option A to the 3rd-8th c. AD Dvaravati metropolis Sri Deva / Si Thep (Srî Dêwa).",
            "rec_option": "Option A",
            "tarr_name": "Srî Dêwa",
            "tarr_adjective": "Srî-Dêwer"
        },
        "c_mukdahan": {
            "opt_a_key": "b_sakhon_nakhon",
            "opt_a_name": "Nong Han Luang (Sakon Nakhon)",
            "opt_a_type": "Ancient Chenla / Pre-Angkorian City (b_sakhon_nakhon)",
            "opt_b_hydronym": "Middle Mekong Basin",
            "opt_b_lang": "Khmer / Lao",
            "opt_b_name": "Nông Hân Lûang",
            "justification": "Mukdahan was founded in 1770 AD by Chao Kinnaree; resolves via Option A to ancient Chenla seat Nong Han Luang (Nông Hân Lûang).",
            "rec_option": "Option A",
            "tarr_name": "Nông Hân Lûang",
            "tarr_adjective": "Nông-Hân-Lûanger"
        },
        "c_MAL_johor": {
            "opt_a_key": "b_MAL_Tumasik",
            "opt_a_name": "Tumasik (Temasek)",
            "opt_a_type": "Pre-867 Malay Maritime Emporium (b_MAL_Tumasik)",
            "opt_b_hydronym": "Singapore-Johor Strait",
            "opt_b_lang": "Old Malay",
            "opt_b_name": "Tumâsich",
            "justification": "Johor Sultanate was founded 1528 AD; resolves via Option A to ancestral maritime emporium Tumasik (Tumâsich).",
            "rec_option": "Option A",
            "tarr_name": "Tumâsich",
            "tarr_adjective": "Tumâsicher"
        },
        "c_SUM_east_sumatra": {
            "opt_a_key": "b_SUM_Mesuji",
            "opt_a_name": "Mesuji",
            "opt_a_type": "Pre-867 Sumatran River Basin (b_SUM_Mesuji)",
            "opt_b_hydronym": "Mesuji River Basin",
            "opt_b_lang": "Old Malay",
            "opt_b_name": "Mesûdschi",
            "justification": "East Sumatra is a modern English geographic descriptor; resolves via Option A to indigenous river district Mesuji (Mesûdschi).",
            "rec_option": "Option A",
            "tarr_name": "Mesûdschi",
            "tarr_adjective": "Mesûdschier"
        },
        "c_SUM_pekanbaru": {
            "opt_a_key": "b_SUM_Rokan_Hilir",
            "opt_a_name": "Rokan Hilir",
            "opt_a_type": "Pre-1784 River District (b_SUM_Rokan_Hilir)",
            "opt_b_hydronym": "Lower Rokan Basin",
            "opt_b_lang": "Malay",
            "opt_b_name": "Nider-Rôkan",
            "justification": "Pekanbaru ('New Market') was founded in 1784 AD; resolves via Option A to lower Rokan river district (Nider-Rôkan).",
            "rec_option": "Option A",
            "tarr_name": "Nider-Rôkan",
            "tarr_adjective": "Nider-Rôkaner"
        },
        "c_SUM_dharmasraya": {
            "opt_a_key": "None",
            "opt_a_name": "None",
            "opt_a_type": "No Verified Pre-867 Urban Centre Attested",
            "opt_b_hydronym": "Batanghari River Basin",
            "opt_b_lang": "Old Malay Hydronym",
            "opt_b_name": "Batangharî",
            "justification": "Dharmasraya emerged as Melayu's upstream capital only after the 1025 Chola raid; resolves via Option B to the Batanghari River basin (Batangharî).",
            "rec_option": "Option B",
            "tarr_name": "Batangharî",
            "tarr_adjective": "Batangharîer"
        },
        "c_BOR_kudat": {
            "opt_a_key": "b_BOR_Marudu",
            "opt_a_name": "Marudu",
            "opt_a_type": "Ancient Sabah Bay Settlement (b_BOR_Marudu)",
            "opt_b_hydronym": "Marudu Bay",
            "opt_b_lang": "Sabah / Bajau",
            "opt_b_name": "Marûdu",
            "justification": "Kudat was founded in 1881 by the British North Borneo Company; resolves via Option A to ancient Marudu Bay (Marûdu).",
            "rec_option": "Option A",
            "tarr_name": "Marûdu",
            "tarr_adjective": "Marûduer"
        },
        "c_BOR_lahad_datu": {
            "opt_a_key": "b_BOR_Sibutu",
            "opt_a_name": "Sibutu",
            "opt_a_type": "Ancient Sulu-Borneo Island / Strait (b_BOR_Sibutu)",
            "opt_b_hydronym": "Darvel-Sibutu Passage",
            "opt_b_lang": "Sulu / Dayak",
            "opt_b_name": "Sibûtu",
            "justification": "Lahad Datu is a 19th-c. town; resolves via Option A to ancient maritime strait Sibutu (Sibûtu).",
            "rec_option": "Option A",
            "tarr_name": "Sibûtu",
            "tarr_adjective": "Sibûtuer"
        },
        "c_BOR_sukadana": {
            "opt_a_key": "None",
            "opt_a_name": "None",
            "opt_a_type": "No Verified Pre-867 Urban Centre Attested",
            "opt_b_hydronym": "Tanjungpura Coastal Reach",
            "opt_b_lang": "Classical Old Malay",
            "opt_b_name": "Tandschungpure",
            "justification": "Sukadana dates to late Majapahit/sultanate records; resolves via Option B to classical West Borneo coastal polity Tanjungpura (Tandschungpure).",
            "rec_option": "Option B",
            "tarr_name": "Tandschungpure",
            "tarr_adjective": "Tandschungpurer"
        },
        "c_BOR_martapura": {
            "opt_a_key": "b_BOR_Muara_Kaman",
            "opt_a_name": "Muara Kaman",
            "opt_a_type": "400 AD Mulavarman Sanskrit Yupa Site (b_BOR_Muara_Kaman)",
            "opt_b_hydronym": "Lower Mahakam Basin",
            "opt_b_lang": "Sanskrit / Kutai Malay",
            "opt_b_name": "Mûara Kaman",
            "justification": "Banjar Martapura dates to 1630 AD; resolves unambiguously via Option A to the 400 AD Mulavarman Sanskrit Yupa site at Muara Kaman (Mûara Kaman).",
            "rec_option": "Option A",
            "tarr_name": "Mûara Kaman",
            "tarr_adjective": "Mûara-Kamaner"
        },
        "c_IDO_barat_daya": {
            "opt_a_key": "b_IDO_Wetar",
            "opt_a_name": "Wetar",
            "opt_a_type": "Ancient Maluku Island Seat (b_IDO_Wetar)",
            "opt_b_hydronym": "Banda-Wetar Archipelago",
            "opt_b_lang": "Maluku Indigenous",
            "opt_b_name": "Wêtar",
            "justification": "Barat Daya is a modern Indonesian directional term ('Southwest'); resolves via Option A to ancient island Wetar (Wêtar).",
            "rec_option": "Option A",
            "tarr_name": "Wêtar",
            "tarr_adjective": "Wêtarer"
        },
        "c_BOR_kutai_jauh": {
            "opt_a_key": "None",
            "opt_a_name": "None",
            "opt_a_type": "No Verified Pre-867 Urban Centre Attested",
            "opt_b_hydronym": "Upper Mahakam / Distant Kutai Basin",
            "opt_b_lang": "Malay / Dayak Toponym",
            "opt_b_name": "Ferne-Kutai",
            "justification": "Post-867 Malay/Dayak directional subdivision ('Distant Kutai'); Procedure 2 confirms unbroken Dayak continuity, calquing jauh ('far') to Ferne-Kutai parallel to Nord-Kutai.",
            "rec_option": "Option B",
            "tarr_name": "Ferne-Kutai",
            "tarr_adjective": "Ferne-Kutaier"
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
                m = re.search(r"`([cd]_[a-zA-Z0-9_\-]+)`", parts[1])
                if not m:
                    continue
                ck = m.group(1)
                if not ck.startswith("c_") or ck in enriched:
                    continue
                reason = parts[5] if len(parts) > 5 else ""
                res = parts[6] if len(parts) > 6 else ""

                m_b = re.search(r"`(b_[a-zA-Z0-9_\-]+)`", res)
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
                m = re.search(r"`(c_[a-zA-Z0-9_\-]+)`", line)
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
                                "opt_b_hydronym": f"{tarr_name} River Basin / Territorial Substrate",
                                "opt_b_lang": "Native Substrate / Section 3.1 Hydronym Hierarchy",
                                "opt_b_name": tarr_name,
                                "justification": f"Authentic pre-867 indigenous physical toponym and territorial catchment ({tarr_name}).",
                                "rec_option": "Option B",
                                "tarr_name": tarr_name,
                                "tarr_adjective": f"{tarr_name}isch" if is_river_lake else f"{tarr_name}er"
                            }

    return enriched


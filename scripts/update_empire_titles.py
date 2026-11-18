#!/usr/bin/env python3
"""
update_empire_titles.py

Comprehensive pipeline script to update Empire-tier de jure titles across:
1. data/ck3_title_tree.json (Web app title hierarchy dataset)
2. data/ck3_counties.geojson (County properties e_tarr, e_origin, e_ipa, e_anachronism)
3. hre_de_jure_and_archdioceses_1059.md (Section 1.1 summary table and Section 2 headers)
4. tarraconian_titles_1059.md (Section 1 formulae and Section 2.0 summary table)
5. audit_discrepancy_register.md (Section 4.0 Empire-Tier Anachronism Register)
6. docs/data/ (Synchronized via build_webapp.py)
"""

import re
import json
import subprocess
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Master Empire Data Dictionary (47 De Jure Empires)
# ---------------------------------------------------------------------------
EMPIRES_MASTER = {
    'e_germany': {
        'in_game': 'Germania',
        'tarr': 'Dat Vrankische Imperi',
        'alt': 'Dat Imperi van Germânjen',
        'ipa': '[dat ˈvraŋ.kɪ.ʃə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 1',
        'origin': 'Germania',
        'anachronism': 'Carolingian/Frankish Western imperial sphere encompassing East Francia, Bavaria, Lotharingia, Italy, Burgundy, England, and Spain.',
        'adj': 'Vrankisch',
        'justification': 'Represents the vast Carolingian Western imperial sphere. MHG Vrankisch [ˈvraŋ.kɪʃ] with voiced initial v- and velar nasal [ŋ].'
    },
    'e_france': {
        'in_game': 'Francia',
        'tarr': 'Dat Imperi van Vrancrîch',
        'alt': 'Dat Westvrankische Imperi',
        'ipa': '[dat ɪm.ˈpɛ.ri van ˈvraŋk.riːç]',
        'tier': 'Tier 1',
        'origin': 'Francia',
        'anachronism': 'Pre-867 West Francia (Verdun 843 AD). Subdued by Chatenois in 920 AD.',
        'adj': 'Vrankisch',
        'justification': 'OHG Frankarīhhi -> MHG Vrankrîche -> Tarraconian Vrancrîch [ˈvraŋk.riːç] with voiced initial v- and Auslautverhärtung -ch.'
    },
    'e_britannia': {
        'in_game': 'Britannia',
        'tarr': 'Dat Imperi van dem Wâllant',
        'alt': 'Dat Welsche Imperi / Dat Schottische Imperi',
        'ipa': '[dat ɪm.ˈpɛ.ri van dɛm ˈvaːl.lant]',
        'tier': 'Tier 1',
        'origin': 'Britannia',
        'anachronism': 'Pre-867 Germanic/Old English exonym for the Insular Celtic realm (Wēalland / Valland). In 1059, England drifted to e_germany, leaving Gaelic Scotland and Ireland.',
        'adj': 'Wâllendisch',
        'justification': 'Calqued on Old English Wēalland / Old Norse Valland (Land of the Celts) -> Wâllant [ˈvaːl.lant] with regular adjective Wâllendisch.'
    },
    'e_byzantium': {
        'in_game': 'Byzantine Empire',
        'tarr': 'Dat Grîkische Imperi',
        'alt': 'Dat Imperi van Bisantz / Dat Ôstrômische Imperi',
        'ipa': '[dat ˈgʀiː.kɪ.ʃə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 1',
        'origin': 'Byzantine Empire',
        'anachronism': '18th-century exonym. Historical Frankish style Imperium Graecorum / Rhōmania. Subsumed into h_roman_empire.',
        'adj': 'Grîkisch',
        'justification': 'Authentic Frankish/German diplomatic style Imperium Graecorum -> Dat Grîkische Imperi [ˈgʀiː.kɪ.ʃə] with circumflexed long î in bimoraic open root, or Bisantz [bi.ˈzants] after Byzantion.'
    },
    'e_illyria': {
        'in_game': 'Illyria',
        'tarr': 'Dat Illîrische Imperi',
        'alt': 'Dat Adriatische Imperi / Dat Imperi van Illîrjen',
        'ipa': '[dat ɪl.ˈliː.rɪ.ʃə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 1',
        'origin': 'Illyria',
        'anachronism': 'Classical Roman Praetorian Prefecture of Illyricum and the Adriatic maritime sphere.',
        'adj': 'Illîrisch',
        'justification': 'Classical Illyricum -> Illîrisch [ɪl.ˈliː.rɪʃ] with long -î-.'
    },
    'e_macedonia': {
        'in_game': 'Macedonia',
        'tarr': 'Dat Imperi van Bizantjen',
        'alt': 'Dat Bizantinische Imperi / Dat Hellênische Imperi',
        'ipa': '[dat ɪm.ˈpɛ.ri van bɪ.ˈtsan.tjən]',
        'tier': 'Tier 1',
        'origin': 'Macedonia',
        'anachronism': 'Renamed from Macedonia: consists of Classical Hellas (Athens, Peloponnese, Aegean) and Thrace with the imperial city of Byzantion (Constantinople). Historical Macedonia is in e_byzantium.',
        'adj': 'Bizantinisch',
        'justification': 'Anchored to the imperial city of Byzantion (Constantinople / c_byzantion) in Thrace alongside Hellas: Bizantjen [bɪ.ˈtsan.tjən] -> Bizantinisch.'
    },
    'e_anatolia': {
        'in_game': 'Anatolia',
        'tarr': 'Dat Anatôlische Imperi',
        'alt': 'Dat Imperi van Anatôljen',
        'ipa': '[dat a.na.ˈtoː.lɪ.ʃə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 1',
        'origin': 'Anatolia',
        'anachronism': 'Pre-867 Byzantine Anatolic Theme / Classical Asia Minor.',
        'adj': 'Anatôlisch',
        'justification': 'Greek Anatolē (Ἀνατολή) -> Anatôlisch [a.na.ˈtoː.lɪʃ].'
    },
    'e_oriens': {
        'in_game': 'Oriens',
        'tarr': 'Dat Imperi van dem Môrghenlant',
        'alt': 'Dat Sîrische Imperi / Dat Imperi van Ôrjent',
        'ipa': '[dat ɪm.ˈpɛ.ri van dɛm ˈmoːr.ɡən.lant]',
        'tier': 'Tier 1',
        'origin': 'Oriens',
        'anachronism': 'Pre-867 Roman Dioecesis Orientis (Diocletian 297 AD, capital Antioch).',
        'adj': 'Môrghenlendisch',
        'justification': 'Latin Oriens ("the rising sun / East") translates root-for-root to High German Môrghenlant [ˈmoːr.ɡən.lant], or adapted as Ôrjent [ˈoːr.jɛnt].'
    },
    'e_aegyptus': {
        'in_game': 'Aegyptus',
        'tarr': 'Dat Êgyptische Imperi',
        'alt': 'Dat Imperi van Êgypten',
        'ipa': '[dat eː.ˈɡʏp.tɪ.ʃə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 1',
        'origin': 'Aegyptus',
        'anachronism': 'Pre-867 Roman Dioecesis Aegypti (Theodosius 381 AD).',
        'adj': 'Êgyptisch',
        'justification': 'Classical Aegyptus with diphthong Ae- -> Ê- [eː] and Greek y -> [ʏ]: Êgyptisch [eː.ˈɡʏp.tɪʃ].'
    },
    'e_africa': {
        'in_game': 'Africa',
        'tarr': 'Dat Mouritânische Imperi',
        'alt': 'Dat Imperi van dem Westmôrenlant / Fâs',
        'ipa': '[dat muː.rɪ.ˈtaː.nɪ.ʃə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 1',
        'origin': 'Africa',
        'anachronism': 'Correcting vanilla inversion: this title holds Morocco and Tahert, which is historically Roman and Berber Mauretania.',
        'adj': 'Mouritânisch',
        'justification': 'Classical Mauretania Tingitana & Caesariensis -> Mouritânisch [muː.rɪ.ˈtaː.nɪʃ] with circumflexed long â.'
    },
    'e_maghreb': {
        'in_game': 'Maghreb',
        'tarr': 'Dat Âfrikânsche Imperi',
        'alt': 'Dat Imperi van Affrîke / Kairouân',
        'ipa': '[dat aː.frɪ.ˈkaːn.ʃə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 2',
        'origin': 'Maghreb',
        'anachronism': 'Correcting vanilla inversion: this title holds Tunisia (Ifriqiya / ancient Africa Proconsularis) and the Sahara.',
        'adj': 'Âfrikânsch',
        'justification': 'Latin Africa Proconsularis / Arabic Ifriqiya -> Âfrikânsch [aː.frɪ.ˈkaːn.ʃə] with long â-.'
    },
    'e_scandinavia': {
        'in_game': 'Scandinavia',
        'tarr': 'Dat Imperi van dem Norderlant',
        'alt': 'Dat Norderlantsche Imperi / Dat Skandinavische Imperi',
        'ipa': '[dat ɪm.ˈpɛ.ri van dɛm ˈnɔr.dər.lant]',
        'tier': 'Tier 1',
        'origin': 'Scandinavia',
        'anachronism': 'Conquered 1142 from House Hede (Norwegian). Native endonym Norðrlönd ("The Northlands").',
        'adj': 'Norderlantsch',
        'justification': 'Semantic calque of Old Norse Norðrlönd ("The Northlands") -> Norderlant [ˈnɔr.dər.lant]. Replaces Plinian Latin exonym with native Nordic high-kingship style.'
    },
    'e_west_slavia': {
        'in_game': 'West-Slavia',
        'tarr': 'Dat Imperi van dem Tôtlant',
        'alt': 'Dat Tôtische Imperi / Dat West-Wendische Imperi',
        'ipa': '[dat ɪm.ˈpɛ.ri van dɛm ˈtoːt.lant]',
        'tier': 'Tier 3',
        'origin': 'West-Slavia',
        'anachronism': '⚠️ Modern 19th/20th-century historiographical coinage. Held in 952 AD by Boris of House Árpád upon partition of Árpád II\'s realm.',
        'adj': 'Tôtisch',
        'justification': 'Calqued on Old Hungarian Tótország / Tótföld (Land of the West Slavs: Czechs, Slovaks, Poles), created on Árpád II\'s death in 952 AD for his son Boris. Tôtlant [ˈtoːt.lant] with circumflex vowel ô.'
    },
    'e_russia': {
        'in_game': 'Russia',
        'tarr': 'Dat Kîewsche Imperi',
        'alt': 'Dat Imperi van den Rûssen / Dat Imperi van dem Gârderîch',
        'ipa': '[dat ˈkiː.ɛf.ʃə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 1',
        'origin': 'Russia',
        'anachronism': 'Historical sovereign grand-princely realm of Kievan Rus\', replacing anachronistic modern \'Russian Empire\'.',
        'adj': 'Kîewsch',
        'justification': 'Named after the grand-princely seat of Kiev (Kyiv) -> Kîewsch [ˈkiː.ɛf.ʃə] with Auslautverhärtung of -v -> -f before -sch.'
    },
    'e_wendish_empire': {
        'in_game': 'Baltic Empire',
        'tarr': 'Dat Imperi van Bêlingen',
        'alt': 'Dat Bêlingische Imperi / Dat Baltische Imperi',
        'ipa': '[dat ɪm.ˈpɛ.ri van ˈbeː.lɪŋ.ən]',
        'tier': 'Tier 2',
        'origin': 'Baltic Empire',
        'anachronism': '⚠️ Paradox misnomer e_wendish_empire. Held in 952 AD by Béla of House Árpád upon partition of Árpád II\'s realm.',
        'adj': 'Bêlingisch',
        'justification': 'Formed after King Béla of House Árpád (who received the Baltic tier in the 952 succession) using the authentic Franconian territorial patronymic suffix -ingen (exactly mirroring Lothair -> Lotharingen / Lôthringen). Bêlingen [ˈbeː.lɪŋ.ən] with regular adjective Bêlingisch.'
    },
    'e_carpathia': {
        'in_game': 'Carpathia',
        'tarr': 'Dat Arpâdische Imperi',
        'alt': 'Dat Imperi van dem Tôtlant-ende-Ungarn / Dat Karpatische Imperi',
        'ipa': '[dat ar.ˈpaː.dɪ.ʃə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 1',
        'origin': 'Carpathia',
        'anachronism': 'Created 885 AD by Árpád (House Árpád) and ruled continuously as the dynastic imperial seat until 958 AD.',
        'adj': 'Arpâdisch',
        'justification': 'Dynastic imperial seat founded by Árpád in 885 AD. Middle Franconian Arpâdisch [ar.ˈpaː.dɪʃ] with circumflex long â.'
    },
    'e_caspian-pontic_steppe': {
        'in_game': 'Khazaria',
        'tarr': 'Dat Chasârische Imperi',
        'alt': 'Dat Imperi van Chasârjen / Dat Pontisch-Kaspische Imperi',
        'ipa': '[dat xa.ˈzaː.rɪ.ʃə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 1',
        'origin': 'Khazaria',
        'anachronism': 'Pre-867 Khazar Khaganate (7th-10th c. AD, fortress Sarkel built 838 AD), held in save by Zebulun (House 1902, Khazar culture).',
        'adj': 'Chasârisch',
        'justification': 'Held in save by Zebulun of House 1902 (Khazar culture), representing the Khazar Khaganate. Ethnonym Khazar -> Chasârjen, regular adjective Chasârisch [xa.ˈzaː.rɪʃ].'
    },
    'e_volga-ural': {
        'in_game': 'Volga-Ural',
        'tarr': 'Dat Bulgârische Imperi',
        'alt': 'Dat Wolga-Bulgârische Imperi / Dat Imperi van Bolgâr',
        'ipa': '[dat bʊl.ˈgaː.rɪ.ʃə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 2',
        'origin': 'Volga-Ural',
        'anachronism': 'Replaced Soviet-era geographic neologism Volga-Ural with the historical sovereign medieval empire of Volga Bulgaria.',
        'adj': 'Bulgârisch',
        'justification': 'Historical sovereign state of Volga Bulgaria (Magna Bulgaria) -> Bulgârisch [bʊl.ˈgaː.rɪʃ].'
    },
    'e_tartaria': {
        'in_game': 'Tartaria',
        'tarr': 'Dat Kiptschachische Imperi',
        'alt': 'Dat Imperi van Kiptschâk',
        'ipa': '[dat kɪp.ˈtʃaː.xɪ.ʃə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 2',
        'origin': 'Tartaria',
        'anachronism': '⚠️ Late medieval Western umbrella term Tartaria for the Cuman-Kipchak steppe.',
        'adj': 'Kiptschachisch',
        'justification': 'Disambiguated from Khitans and Mongols; indigenous endonym of the Cuman-Kipchak steppe confederation Kiptschâk -> Kiptschachisch [kɪp.ˈtʃaː.xɪ.ʃə] with affricate tsch and spirantization k -> ch.'
    },
    'e_turan': {
        'in_game': 'Turan',
        'tarr': 'Dat Sogdische Imperi',
        'alt': 'Dat Imperi van Sogdjên / Chwâresm',
        'ipa': '[dat ˈzɔg.dɪ.ʃə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 1',
        'origin': 'Turan',
        'anachronism': 'Sedentary cultural core and Samanid imperial seat of Sogdiana, replacing Persian epic mythological Turan.',
        'adj': 'Sogdisch',
        'justification': 'Classical and medieval Sogdiana (Sogdia) -> Sogdisch [ˈzɔg.dɪʃ] with voiced initial s- [z].'
    },
    'e_kirghiz_khanate': {
        'in_game': 'Kirghiz Khanate',
        'tarr': 'Dat Kirgîsische Imperi',
        'alt': 'Dat Imperi van den Kirgîsen / Naimânen',
        'ipa': '[dat kɪr.ˈɡiː.zɪ.ʃə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 1',
        'origin': 'Kirghiz Khanate',
        'anachronism': 'Pre-867 Yenisei Kirghiz Khaganate (840 AD). Holds only Naimania in save.',
        'adj': 'Kirgîsisch',
        'justification': 'Ethnonym Qyrgyz adapts with voiced medial -s- [z] and long -î-: Kirgîsen [kɪr.ˈɡiː.zən].'
    },
    'e_mongolia': {
        'in_game': 'Mongolia',
        'tarr': 'Dat Mongôlische Imperi',
        'alt': 'Dat Imperi van dem Hilligen Ôtüken',
        'ipa': '[dat mɔŋ.ˈgoː.lɪ.ʃə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 2',
        'origin': 'Mongolia',
        'anachronism': 'Pre-Genghisid umbrella name applied to Göktürk/Uyghur sacred seat Ötüken.',
        'adj': 'Mongôlisch',
        'justification': 'Ethnonym Mongol -> Mongôlisch [mɔŋ.ˈgoː.lɪʃ] with regular adjectival ending and circumflexed long ô.'
    },
    'e_siberia': {
        'in_game': 'Siberia',
        'tarr': 'Dat Jûgrische Imperi',
        'alt': 'Dat Imperi van Jûgren / Dat Imperi van dem Ôb',
        'ipa': '[dat ˈjuː.grɪ.ʃə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 2',
        'origin': 'Siberia',
        'anachronism': 'Medieval Uralic endonym and Novgorodian designation Yugra, replacing post-1400 Tatar/Russian Sibir.',
        'adj': 'Jûgrisch',
        'justification': 'Historical medieval Uralic realm of Yugra (Ugria) -> Jûgrisch [ˈjuː.grɪʃ] with long û.'
    },
    'e_arabia': {
        'in_game': 'Arabian Empire',
        'tarr': 'Dat Kalîfische Imperi',
        'alt': 'Dat Imperi van dem Kalifât / Dat Arâbische Imperi',
        'ipa': '[dat ka.ˈliː.fɪ.ʃə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 1',
        'origin': 'Arabian Empire',
        'anachronism': 'Conquered 1136 from Hashimid Caliphs. Native institutional endonym al-Khilāfah ("The Stewardship/Caliphate").',
        'adj': 'Kalîfisch',
        'justification': 'Calque of the institutional Islamic sovereign title al-Khilāfah (الخلافة) -> Dat Kalîfische Imperi [dat ka.ˈliː.fɪ.ʃə ɪm.ˈpɛ.ri] with circumflexed long î.'
    },
    'e_persia': {
        'in_game': 'Persian Empire',
        'tarr': 'Dat Imperi van Êrânschahr',
        'alt': 'Dat Persische Imperi',
        'ipa': '[dat ɪm.ˈpɛ.ri van eː.ˈraːn.ʃaːr]',
        'tier': 'Tier 1',
        'origin': 'Persian Empire',
        'anachronism': 'Pre-867 Sasanian Empire (Ērānshahr, fell 651 AD). Destroyed historically in 651 AD.',
        'adj': 'Êrânisch',
        'justification': 'Authentic classical Sasanian/Iranian imperial endonym Ērānshahr ("Empire of the Iranians") -> Êrânschahr [eː.ˈraːn.ʃaːr].'
    },
    'e_rajastan': {
        'in_game': 'Rajasthan',
        'tarr': 'Dat Ârjavartische Imperi',
        'alt': 'Dat Radschastânische Imperi / Dat Pratihâra-Imperi',
        'ipa': '[dat aːr.ja.ˈvar.tɪ.ʃə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 1',
        'origin': 'Rajasthan',
        'anachronism': '⚠️ Early modern regional name applied to the ancient Indo-Gangetic Plain (Aryavarta / Harsha).',
        'adj': 'Ârjavartisch',
        'justification': 'Classical Sanskrit Āryāvarta ("Abode of the Nobles"), the imperial northern Indian realm of Harsha and the Gurjara-Pratihāras. Āryāvarta -> Ârjavartisch [aːr.ja.ˈvar.tɪʃ].'
    },
    'e_bengal': {
        'in_game': 'Pracya',
        'tarr': 'Dat Bengalische Imperi',
        'alt': 'Dat Pâla-Imperi / Dat Ôstindische Imperi',
        'ipa': '[dat bɛŋ.ˈgaː.lɪ.ʃə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 1',
        'origin': 'Pracya',
        'anachronism': 'Pre-867 Sanskrit Prācya / Pala Empire 750 AD. Destroyed historically in 550 AD.',
        'adj': 'Bengalisch',
        'justification': 'Replaces generic East India with Bengal, imperial seat of the Buddhist Pāla Empire (dynn_pala). Bengâlen -> Bengalisch [bɛŋ.ˈgaː.lɪʃ].'
    },
    'e_deccan': {
        'in_game': 'Deccan Empire',
        'tarr': 'Dat Karnâtische Imperi',
        'alt': 'Dat Tschôla-Imperi / Dat Sûtindische Imperi',
        'ipa': '[dat kar.ˈnaː.tɪ.ʃə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 1',
        'origin': 'Deccan Empire',
        'anachronism': 'Authentic medieval imperial endonym used by Deccan emperors (Karnata Samrajya), replacing modern geographic construct South India.',
        'adj': 'Karnâtisch',
        'justification': 'Direct calque of Sanskrit/Kannada Karnata Samrajya -> Karnâtisch [kar.ˈnaː.tɪʃ].'
    },
    'e_tibet': {
        'in_game': 'Tibet',
        'tarr': 'Dat Imperi van Bôtlant',
        'alt': 'Dat Tibêtische Imperi / Dat Imperi van dem Hôgen Bôtlant',
        'ipa': '[dat ɪm.ˈpɛ.ri van ˈboːt.lant]',
        'tier': 'Tier 1',
        'origin': 'Tibet',
        'anachronism': 'Pre-867 Yarlung dynasty Tibetan Empire (Songtsen Gampo). Destroyed historically in 842 AD.',
        'adj': 'Bôtisch',
        'justification': 'Tibetan imperial endonym Bod Chenpo ("Greater Bod") -> Bôtlant [ˈboːt.lant] with regular adjective Bôtisch.'
    },
    'e_zhongyuan': {
        'in_game': 'Zhongyuan',
        'tarr': 'Dat Imperi van dem Middenvelt',
        'alt': 'Dat Middenveltsche Imperi / Dat Imperi van Dschôngjüan',
        'ipa': '[dat ɪm.ˈpɛ.ri van dɛm ˈmɪ.dən.vɛlt]',
        'tier': 'Tier 1',
        'origin': 'Zhongyuan',
        'anachronism': 'Pre-867 Classical Zhōngyuán (Central Plains of China / Han and Tang dynasties).',
        'adj': 'Middenveltsch',
        'justification': 'Chinese Zhōngyuán (中原, 中 = middle -> Midden-; 原 = plain/field -> -velt): Middenvelt [ˈmɪ.dən.vɛlt].'
    },
    'e_jingyang': {
        'in_game': 'Jingyang',
        'tarr': 'Dat Imperi van Dôrnflôz',
        'alt': 'Dat Dôrnflôzische Imperi / Dat Imperi van Dschingjâng',
        'ipa': '[dat ɪm.ˈpɛ.ri van ˈdoːrn.floːts]',
        'tier': 'Tier 1',
        'origin': 'Jingyang',
        'anachronism': 'Pre-867 Nine Provinces: Jingzhou and Yangzhou along the Yangtze River.',
        'adj': 'Dôrnflôzisch',
        'justification': 'Calqued from Jing (荆 = thorn -> Dôrn) and Yang (扬 = lift up / Yangtze River -> Flôz): Dôrnflôz [ˈdoːrn.floːts].'
    },
    'e_liangyi': {
        'in_game': 'Liangyi',
        'tarr': 'Dat Imperi van den Vîr-Strômen',
        'alt': 'Dat Vîrstrômische Imperi / Dat Sîtschuânsche Imperi',
        'ipa': '[dat ɪm.ˈpɛ.ri van dɛn ˈfiːr.stroː.mən]',
        'tier': 'Tier 1',
        'origin': 'Liangyi',
        'anachronism': 'Pre-867 Nine Provinces: Liangzhou and Yizhou (Sichuan basin & Yunnan).',
        'adj': 'Vîrstrômisch',
        'justification': 'Calqued from Chinese Sìchuān (四川, Four Rivers/Circuits, the historical geographical reality of Liang-Yi / 梁益): Vîr (four) + Strôme (rivers) -> Vîr-Strômen [ˈfiːr.stroː.mən].'
    },
    'e_yongliang': {
        'in_game': 'Yongliang',
        'tarr': 'Dat Imperi van dem Kôlvredelant',
        'alt': 'Dat Kôlvredische Imperi / Dat Imperi van Jônglîang',
        'ipa': '[dat ɪm.ˈpɛ.ri van dɛm ˈkoːl.vreː.də.lant]',
        'tier': 'Tier 1',
        'origin': 'Yongliang',
        'anachronism': 'Pre-867 Nine Provinces: Yongzhou and Liangzhou (Hexi Corridor / Silk Road gateway).',
        'adj': 'Kôlvredisch',
        'justification': 'Calqued from Liang (凉 = cool -> Kôl) and Yong (雍 = peace/harmony -> Vrede): Kôlvredelant [ˈkoːl.vreː.də.lant].'
    },
    'e_lingnan': {
        'in_game': 'Lingnan',
        'tarr': 'Dat Imperi van dem Sûtrücke',
        'alt': 'Dat Sûtrückische Imperi / Dat Imperi van Lingnân',
        'ipa': '[dat ɪm.ˈpɛ.ri van dɛm ˈzyːt.rʏ.kə]',
        'tier': 'Tier 1',
        'origin': 'Lingnan',
        'anachronism': 'Pre-867 Nanyue / Nanling mountains / Tang Circuit of Lingnan and Annan.',
        'adj': 'Sûtrückisch',
        'justification': 'Chinese Lǐngnán (岭南) translates root-for-root to "South of the Mountain Ridges" (岭 = ridge -> Rücke; 南 = south -> Sût-): Sûtrücke [ˈzyːt.rʏ.kə].'
    },
    'e_andong': {
        'in_game': 'Andong',
        'tarr': 'Dat Chitaische Imperi',
        'alt': 'Dat Ljâo-Imperi / Dat Imperi van dem Ôstfrid',
        'ipa': '[dat çi.ˈtaː.ɪ.ʃə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 1',
        'origin': 'Andong',
        'anachronism': 'Conquered in 999 AD by Yelü Xiuge (House Yelü, Khitan culture), representing the Liao/Khitan imperial domain encompassing k_khitan.',
        'adj': 'Chitaisch',
        'justification': 'Reflects the Khitan conquest under Yelü Xiuge in 999 AD. Middle Franconian Chitaisch [çi.ˈtaː.ɪʃ] derived from Khitai/Cathay.'
    },
    'e_amur': {
        'in_game': 'Amur',
        'tarr': 'Dat Bohâi-Imperi',
        'alt': 'Dat Dschürtschen-Imperi',
        'ipa': '[dat bɔ.ˈhaːi ɪm.ˈpɛ.ri]',
        'tier': 'Tier 2',
        'origin': 'Amur',
        'anachronism': 'Pre-867 historical sovereign empire of the Amur and Manchuria (Balhae/Bohai), replacing modern Russian/Tungusic river name Amur.',
        'adj': 'Bohâisch',
        'justification': 'Historical Mohe/Tungusic kingdom of Balhae (Bohai) -> Bohâi [bɔ.ˈhaːi] with circumflexed long â.'
    },
    'e_goryeo': {
        'in_game': 'Samhan',
        'tarr': 'Dat Hôchprachtige Imperi',
        'alt': 'Dat Imperi van den Drî-Hânen / Dat Imperi van Goryeo',
        'ipa': '[dat ˈhoːx.pʀax.tɪ.ɣə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 1',
        'origin': 'Samhan',
        'anachronism': 'Conquered 1153 from House Aliyid. Native endonyms Goryeo (高麗 = "Lofty Splendor") and Samhan (三韓 = "Three Hans").',
        'adj': 'Hôchprachtig',
        'justification': 'Semantic calque of Goryeo (高麗: gāo = high/lofty, lì = magnificent/splendid) -> Hôchpracht with weak adjective Hôchprachtige [ˈhoːx.pʀax.tɪ.ɣə]. Alt Drî-Hânen (Samhan).'
    },
    'e_japan': {
        'in_game': 'Japan',
        'tarr': 'Dat Imperi van dem Sunnenufganch',
        'alt': 'Dat Sunnenlant / Dat Imperi van der Sunnenorigin',
        'ipa': '[dat ɪm.ˈpɛ.ri van dɛm ˈzʊ.nən.ʊf.ɡaŋç]',
        'tier': 'Tier 1',
        'origin': 'Japan',
        'anachronism': 'Conquered 1154 from Minabuchi dynasty. Native endonym Hinamoto / Nihon ("Origin of the Sun / Sunrise").',
        'adj': 'Sunnenufganchisch',
        'justification': 'Pure Germanic calque of Hinamoto / Nihon (日本) via Middle High German sunnen-ufganc -> Sunnenufganch [ˈzʊ.nən.ʊf.ɡaŋç]. Trade form Japansch.'
    },
    'e_srivijaya': {
        'in_game': 'Srivijaya',
        'tarr': 'Dat Imperi van Glantz-Zêch',
        'alt': 'Dat Sêchhafte Imperi / Dat Srîwidschajische Imperi',
        'ipa': '[dat ɪm.ˈpɛ.ri van ˈɡlants.tseːç]',
        'tier': 'Tier 1',
        'origin': 'Srivijaya',
        'anachronism': 'Conquered 1165 from House Śailēndra. Sanskrit Śrī-vijaya ("Radiant/Glorious Victory").',
        'adj': 'Glantz-Zêchisch',
        'justification': 'Semantic calque of Sanskrit Śrī ("radiant/glorious" -> Glantz) and Vijaya ("victory/triumph" -> Zêch with Auslautverhärtung): Glantz-Zêch [ˈɡlants.tseːç].'
    },
    'e_nusantara': {
        'in_game': 'Nusantara',
        'tarr': 'Dat Malûkische Imperi',
        'alt': 'Dat Krûdinsels-Imperi',
        'ipa': '[dat ma.ˈluː.kɪ.ʃə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 2',
        'origin': 'Nusantara',
        'anachronism': 'Representative kingdom of the Spice Islands; Nusantara is a late 14th-century Javanese concept and modern political term.',
        'adj': 'Malûkisch',
        'justification': 'Representative kingdom of Maluku (Spice Islands) -> Malûkisch [ma.ˈluː.kɪʃ] with circumflexed long û.'
    },
    'e_suvarnabhumi': {
        'in_game': 'Suvarnabhumi',
        'tarr': 'Dat Pagânsche Imperi',
        'alt': 'Dat Imperi van dem Guldenlant',
        'ipa': '[dat pa.ˈgaːn.ʃə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 1',
        'origin': 'Suvarnabhumi',
        'anachronism': 'Historical sovereign medieval empire uniting Burma and Dvaravati (849–1287), replacing mythical Sanskrit Suvarnabhumi.',
        'adj': 'Pagânsch',
        'justification': 'Historical sovereign empire of Pagan (Bagan) -> Pagânsch [pa.ˈgaːn.ʃə] with long â.'
    },
    'e_kambuja': {
        'in_game': 'Kambuja',
        'tarr': 'Dat Angkôrsche Imperi',
        'alt': 'Dat Chmêrische Imperi',
        'ipa': '[dat aŋ.ˈkoːr.ʃə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 1',
        'origin': 'Kambuja',
        'anachronism': 'Historical imperial capital and representative kingdom of Angkor (802–1431), replacing modern political Kampuchea.',
        'adj': 'Angkôrsch',
        'justification': 'Khmer imperial capital Angkor -> Angkôrsch [aŋ.ˈkoːr.ʃə] with long ô.'
    },
    'e_mali': {
        'in_game': 'Mali',
        'tarr': 'Dat Imperi van Gâna',
        'alt': 'Dat Gânasche Imperi / Dat Imperi van Wagadû',
        'ipa': '[dat ɪm.ˈpɛ.ri van ˈgaː.na]',
        'tier': 'Tier 3',
        'origin': 'Mali',
        'anachronism': 'Historical medieval imperial hegemon of the Western Sahel (Ghana / Wagadu); Mali Empire did not exist until 1235.',
        'adj': 'Gânasch',
        'justification': 'Historical medieval empire of Ghana (Wagadu) -> Gâna [ˈgaː.na] with regular adjective Gânasch [ˈgaː.naʃ].'
    },
    'e_guinea': {
        'in_game': 'Guinea',
        'tarr': 'Dat Imperi van dem Swartzenlant',
        'alt': 'Dat Swartzenlantsche Imperi / Dat Guinêische Imperi',
        'ipa': '[dat ɪm.ˈpɛ.ri van dɛm ˈswar.tsən.lant]',
        'tier': 'Tier 2',
        'origin': 'Guinea',
        'anachronism': 'Conquered 1187 from House Nyū. Berber Akal n-Iguinawen ("Land of the Black Peoples").',
        'adj': 'Swartzenlantsch',
        'justification': 'Direct semantic calque of Berber Akal n-Iguinawen (Land of the Black Peoples) -> Swartzenlant [ˈswar.tsən.lant].'
    },
    'e_kanem_bornu': {
        'in_game': 'Kanem-Bornu',
        'tarr': 'Dat Kanêmische Imperi',
        'alt': 'Dat Imperi van Kanêm / Dat Kanêm-Bornûische Imperi',
        'ipa': '[dat ka.ˈneː.mɪ.ʃə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 1',
        'origin': 'Kanem-Bornu',
        'anachronism': 'In 1059 under the Sayfawa dynasty (held in save by Sharaf), the realm was centered solely on Kanem (capital Njimi); Bornu was a late 14th-century addition.',
        'adj': 'Kanêmisch',
        'justification': 'Historical Sayfawa kingdom of Kanem -> Kanêmisch [ka.ˈneː.mɪʃ] with regular adjectival ending.'
    },
    'e_abyssinia': {
        'in_game': 'Abyssinia',
        'tarr': 'Dat Ethjôpische Imperi',
        'alt': 'Dat Imperi van Axûm / Dat Abessînische Imperi',
        'ipa': '[dat ɛt.ˈjoː.pɪ.ʃə ɪm.ˈpɛ.ri]',
        'tier': 'Tier 1',
        'origin': 'Abyssinia',
        'anachronism': 'Classical and medieval Greek/Latin and Ge\'ez imperial designation Ethiopia / Aksum, held in save by Getachew (ethiopian culture).',
        'adj': 'Ethjôpisch',
        'justification': 'Classical and medieval imperial designation Ethiopia / Aksum -> Ethjôpisch [ɛt.ˈjoː.pɪʃ].'
    },
    'e_azania': {
        'in_game': 'Azania',
        'tarr': 'Dat Zandsch-Imperi',
        'alt': 'Dat Imperi van dem Zandsch / Dat Imperi van Azânjen',
        'ipa': '[dat ˈzandʒ.ɪm.ˌpɛ.ri]',
        'tier': 'Tier 1',
        'origin': 'Azania',
        'anachronism': 'Medieval Indian Ocean endonym for the Swahili coast (Zanj), replacing 1st-century Greco-Roman maritime label Azania.',
        'adj': 'Zandschisch',
        'justification': 'Medieval endonym Bilad al-Zanj -> Zandsch [zandʒ] with affricate dsch [dʒ].'
    }
}

# ---------------------------------------------------------------------------
# 1. Update data/ck3_title_tree.json
# ---------------------------------------------------------------------------
def update_title_tree():
    tree_path = REPO_DIR / "data" / "ck3_title_tree.json"
    print(f"Updating {tree_path.name}...")
    with open(tree_path, "r", encoding="utf-8") as f:
        tree = json.load(f)

    updated_count = 0
    for ek, info in EMPIRES_MASTER.items():
        if ek in tree:
            tree[ek]["tarr"] = info["tarr"]
            tree[ek]["origin"] = info["origin"]
            tree[ek]["ipa"] = info["ipa"]
            tree[ek]["anachronism"] = info["anachronism"]
            updated_count += 1

    # Update k_thessalonika in title tree
    if 'e_macedonia' in tree and 'kingdoms' in tree['e_macedonia']:
        if 'k_thessalonika' in tree['e_macedonia']['kingdoms']:
            k_node = tree['e_macedonia']['kingdoms']['k_thessalonika']
            k_node['tarr'] = 'Bizantjen'
            k_node['origin'] = 'Byzantion (in-game: Thessalonika)'
            k_node['anachronism'] = 'Renamed from Thessalonika: kingdom consists solely of Thrace and the imperial city of Byzantion (Constantinople).'

    with open(tree_path, "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=2, ensure_ascii=False)
    print(f"-> Updated {updated_count} empire nodes in {tree_path.name}")

# ---------------------------------------------------------------------------
# 2. Update data/ck3_counties.geojson
# ---------------------------------------------------------------------------
def update_counties_geojson():
    counties_path = REPO_DIR / "data" / "ck3_counties.geojson"
    print(f"Updating empire properties in {counties_path.name}...")
    with open(counties_path, "r", encoding="utf-8") as f:
        fc = json.load(f)

    updated_features = 0
    for feat in fc["features"]:
        p = feat["properties"]
        ek = p.get("empire")
        if ek in EMPIRES_MASTER:
            info = EMPIRES_MASTER[ek]
            p["e_tarr"] = info["tarr"]
            p["e_origin"] = info["origin"]
            p["e_ipa"] = info["ipa"]
            p["e_anachronism"] = info["anachronism"]
            updated_features += 1
        if p.get("kingdom") == "k_thessalonika":
            p["k_tarr"] = "Bizantjen"
            p["k_origin"] = "Byzantion (in-game: Thessalonika)"
            p["k_anachronism"] = "Renamed from Thessalonika: kingdom consists solely of Thrace and the imperial city of Byzantion (Constantinople)."

    with open(counties_path, "w", encoding="utf-8") as f:
        json.dump(fc, f, separators=(",", ":"))
    print(f"-> Updated {updated_features} county features in {counties_path.name}")

def update_baronies_geojson():
    baronies_path = REPO_DIR / "data" / "ck3_baronies.geojson"
    print(f"Updating empire properties in {baronies_path.name}...")
    with open(baronies_path, "r", encoding="utf-8") as f:
        fc = json.load(f)

    updated_features = 0
    for feat in fc["features"]:
        p = feat["properties"]
        ek = p.get("empire")
        if ek in EMPIRES_MASTER:
            info = EMPIRES_MASTER[ek]
            p["e_tarr"] = info["tarr"]
            p["e_origin"] = info["origin"]
            p["e_ipa"] = info["ipa"]
            p["e_anachronism"] = info["anachronism"]
            updated_features += 1
        if p.get("kingdom") == "k_thessalonika":
            p["k_tarr"] = "Bizantjen"
            p["k_origin"] = "Byzantion (in-game: Thessalonika)"
            p["k_anachronism"] = "Renamed from Thessalonika: kingdom consists solely of Thrace and the imperial city of Byzantion (Constantinople)."

    with open(baronies_path, "w", encoding="utf-8") as f:
        json.dump(fc, f, separators=(",", ":"))
    print(f"-> Updated {updated_features} barony features in {baronies_path.name}")

# ---------------------------------------------------------------------------
# 3. Update hre_de_jure_and_archdioceses_1059.md
# ---------------------------------------------------------------------------
def update_hre_gazetteer():
    hre_path = REPO_DIR / "hre_de_jure_and_archdioceses_1059.md"
    print(f"Updating {hre_path.name}...")
    text = hre_path.read_text(encoding="utf-8")

    # 3.1 Update Section 1.1 Table
    # Pattern: | # | **Name** | `ek` | RE | Total | Control% | KCount |
    lines = text.splitlines()
    new_lines = []
    in_sec1_1 = False
    table_header_done = False

    for line in lines:
        if line.startswith("### 1.1 Summary Table of De Jure Empires"):
            in_sec1_1 = True
            new_lines.append(line)
            continue
        elif in_sec1_1 and line.startswith("### 1.2"):
            in_sec1_1 = False
            new_lines.append(line)
            continue

        if in_sec1_1:
            if line.startswith("| # | De Jure Empire |"):
                new_lines.append("| # | De Jure Empire | Title Key | Tarraconian Chancellery Title (`Dat Imperi`) | IPA | RE Counties | Total De Jure Counties | Control % | Kingdoms Count |")
                table_header_done = True
                continue
            elif in_sec1_1 and table_header_done and line.startswith("| :---"):
                new_lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
                continue
            m = re.match(r"^\|\s*(\d+)\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*`(e_[a-zA-Z0-9_\-]+)`\s*\|", line)
            if m:
                idx = m.group(1)
                eng_name = m.group(2).strip()
                ek = m.group(3).strip()
                parts = [p.strip() for p in line.strip().split('|')[1:-1]]
                re_cnt = parts[-4].strip('* ')
                tot_cnt = parts[-3].strip('* ')
                pct = parts[-2].strip('* ')
                k_cnt = parts[-1].strip('* ')
                info = EMPIRES_MASTER.get(ek, {})
                tarr_title = info.get('tarr', eng_name)
                ipa_str = info.get('ipa', '')
                new_lines.append(f"| {idx} | **{eng_name}** | `{ek}` | **{tarr_title}** | `{ipa_str}` | **{re_cnt}** | {tot_cnt} | {pct} | {k_cnt} |")
                continue

        # 3.2 Update Section 2 Kingdom header lines: * **De Jure Empire:** ...
        m_emp_line = re.match(r"^\*\s*\*\*De Jure Empire:\*\*\s*(.*?)\s*\[`(e_[a-zA-Z0-9_\-]+)`\](.*)$", line)
        if m_emp_line:
            orig_name = m_emp_line.group(1).strip()
            ek = m_emp_line.group(2).strip()
            rest = m_emp_line.group(3).strip()
            info = EMPIRES_MASTER.get(ek, {})
            tarr_title = info.get('tarr', orig_name)
            new_lines.append(f"* **De Jure Empire:** {orig_name} [`{ek}`] — *Tarraconian: **{tarr_title}***")
            continue

        # 3.3 Update k_thessalonika
        if "`k_thessalonika`" in line:
            line = re.sub(r"\*\*Thessalonika\*\*", "**Byzantion**", line)
            line = re.sub(r"Macedonia\s*\[e_macedonia\]", "Byzantium [e_macedonia]", line)
        if line.startswith("### 2.47 Kingdom of Thessalonika (`k_thessalonika`)"):
            line = "### 2.47 Kingdom of Byzantion (`k_thessalonika`) — 3/3 Counties in HRE/RE"

        new_lines.append(line)

    hre_path.write_text("\n".join(new_lines), encoding="utf-8")
    print(f"-> Successfully updated Section 1.1 and Section 2 in {hre_path.name}")

# ---------------------------------------------------------------------------
# 4. Update tarraconian_titles_1059.md
# ---------------------------------------------------------------------------
def update_titles_gazetteer():
    titles_path = REPO_DIR / "tarraconian_titles_1059.md"
    print(f"Updating {titles_path.name}...")
    text = titles_path.read_text(encoding="utf-8")

    # 4.1 Update Section 1 formula table if Empire row missing
    if "| **Empire (`e_*`)" not in text:
        target_s1 = "| **Kingdom (`k_*`)"
        replacement_s1 = "| **Empire (`e_*`)** | **Dat Imperi** `[dat ɪm.ˈpɛ.ri]` | **Imperi** | **Dat Imperi van ...** / **Dat [Adjective] Imperi** |\n| **Kingdom (`k_*`)"
        text = text.replace(target_s1, replacement_s1, 1)

    # 4.2 Insert / Replace Section 2.0 (Summary Table: The 47 De Jure Empires in Tarraconian)
    emp_rows = []
    hre_text = (REPO_DIR / "hre_de_jure_and_archdioceses_1059.md").read_text(encoding="utf-8")
    emp_order = []
    for h_line in hre_text.splitlines():
        m = re.match(r"^\|\s*(\d+)\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*`(e_[a-zA-Z0-9_\-]+)`\s*\|", h_line)
        if m:
            idx = m.group(1)
            eng_name = m.group(2).strip()
            ek = m.group(3).strip()
            parts = [p.strip() for p in h_line.strip().split('|')[1:-1]]
            re_cnt = parts[-4].strip('* ')
            tot_cnt = parts[-3].strip('* ')
            pct = parts[-2].strip('* ')
            k_cnt = parts[-1].strip('* ')
            emp_order.append((eng_name, ek, re_cnt, tot_cnt, pct, k_cnt))
    
    for idx, (eng_name, ek, re_cnt, tot_cnt, pct, k_cnt) in enumerate(emp_order, 1):
        info = EMPIRES_MASTER.get(ek, {})
        tarr_title = info.get('tarr', eng_name)
        ipa_str = info.get('ipa', '')
        alt = info.get('alt', '')
        alt_str = f" *(or **{alt}**)*" if alt else ""
        anach = info.get('anachronism', '')
        adj = info.get('adj', '')
        emp_rows.append(f"| {idx} | **{eng_name}** | `{ek}` | **{tarr_title}**{alt_str} | `{ipa_str}` | *{adj}* | **{re_cnt}/{tot_cnt} RE** — {anach} |")

    sec2_0_table = """## 2.0 Summary Table: The 47 De Jure Empires in Tarraconian (28 July 1194)

| # | In-Game Empire | Title Key | Tarraconian Title (`Dat Imperi`) | IPA | Adjective | RE / Total Counties & Historical Rationale |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
""" + "\n".join(emp_rows) + "\n\n---\n\n"

    target_sec2 = "## 2. Summary Table: The 213 De Jure Kingdoms in Tarraconian (28 July 1194)"
    if "## 2.0 Summary Table: The 47 De Jure Empires in Tarraconian" in text:
        text = re.sub(
            r"## 2\.0 Summary Table: The 47 De Jure Empires in Tarraconian.*?---\n\n" + re.escape(target_sec2),
            sec2_0_table + target_sec2,
            text,
            flags=re.DOTALL
        )
    else:
        text = text.replace(target_sec2, sec2_0_table + target_sec2, 1)

    # 4.3 Update k_thessalonika row in Section 2 table and Section 3.47 header
    text = re.sub(
        r"\|\s*90\s*\|\s*\*\*Thessalonika\*\*\s*\|\s*`k_thessalonika`\s*\|\s*\*\*Kûnincrich van Thessalonîke\*\*\s*\|\s*\*Thessalonîkisch\*\s*\|.*?\|.*?\|.*?\|",
        "| 90 | **Byzantion** | `k_thessalonika` | **Kûnincrich van Bizantjen** | *Bizantinisch* | `[ˈkyː.nɪŋk.riːx van bɪ.ˈtsan.tjən]` | Byzantion (in-game: Thessalonika) | Renamed from Thessalonika: kingdom consists solely of Thrace and the imperial city of Byzantion (Constantinople), with no territory in historical Macedonia. |",
        text
    )
    text = text.replace(
        "### 3.47 Kingdom of Thessalonika (`k_thessalonika`) $\\rightarrow$ **Kûnincrich van Thessalonîke**",
        "### 3.47 Kingdom of Byzantion (`k_thessalonika`) $\\rightarrow$ **Kûnincrich van Bizantjen**"
    )

    titles_path.write_text(text, encoding="utf-8")
    print(f"-> Successfully updated Section 1 and inserted Section 2.0 in {titles_path.name}")

# ---------------------------------------------------------------------------
# 5. Update audit_discrepancy_register.md
# ---------------------------------------------------------------------------
def update_audit_register():
    audit_path = REPO_DIR / "audit_discrepancy_register.md"
    print(f"Updating {audit_path.name}...")
    text = audit_path.read_text(encoding="utf-8")

    emp_audit_rows = []
    for ek in sorted(EMPIRES_MASTER.keys()):
        info = EMPIRES_MASTER[ek]
        emp_audit_rows.append(
            f"| `{ek}` | **{info['in_game']}** | **{info['tier']}** | {info['anachronism']} | **Option B/Antiquity:** {info['origin']} | **{info['tarr']}** | *{info['adj']}* | `{info['ipa']}` | {info['justification']} |"
        )

    sec4_0_text = """### 4.0 Empire-Tier Historical Title Resolution Register (47 De Jure Empires)

| Empire Key | In-Game Name | Tier | Anachronism & Discrepancy Analysis | Historical Resolution & Pre-867 Center | Official Tarraconian Chancellery Title (`Dat Imperi`) | Official Adjective | IPA Pronunciation | Historical & Etymological Justification |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- |
""" + "\n".join(emp_audit_rows) + "\n\n"

    target_sec4 = "## 4. Master Title Discrepancy & Resolution Register (1012 Imperial Counties)"
    if "### 4.0 Empire-Tier Historical Title Resolution Register (47 De Jure Empires)" in text:
        text = re.sub(
            r"### 4\.0 Empire-Tier Historical Title Resolution Register \(47 De Jure Empires\).*?(?=\n\| `c_|\n\| County Key)",
            sec4_0_text,
            text,
            flags=re.DOTALL
        )
    else:
        text = text.replace(target_sec4, target_sec4 + "\n\n" + sec4_0_text, 1)

    audit_path.write_text(text, encoding="utf-8")
    print(f"-> Successfully added Section 4.0 in {audit_path.name}")

# ---------------------------------------------------------------------------
# Main Execution
# ---------------------------------------------------------------------------
def main():
    print("==========================================================")
    print("Tarraconian Empire-Tier Titles Update Pipeline (Dat Imperi)")
    print("==========================================================")
    update_title_tree()
    update_counties_geojson()
    update_baronies_geojson()
    update_hre_gazetteer()
    update_titles_gazetteer()
    update_audit_register()

    # Package web app
    print("Packaging web assets via build_webapp.py...")
    subprocess.run(["python3", str(REPO_DIR / "scripts" / "build_webapp.py")], check=True)
    print("All tasks completed successfully!")

if __name__ == "__main__":
    main()

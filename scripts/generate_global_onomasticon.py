#!/usr/bin/env python3
"""
generate_global_onomasticon.py

Generates data/global_onomasticon_adaptation.json (Section 4.B #6 of
barony_tarraconian_naming_pipeline.md):
  - Clean CK3-ASCII-decoder rules & metadata (sync'd with ck3_name_decoder.py)
  - All 239 official name_list_franconian entries + 85 expanded & 58 saint entries
    parsed from tarraconian_onomasticon_and_name_register.md
  - All unique first_name values from coinage-era rulers (data/barony_coinage_rulers.json)
    plus canonical faith saints (data/barony_physical_and_event_context.json)
  - Culture-aware phonological adaptation into Chancellery Tarraconian orthography
    (circumflex vowels â ê î ô û, Rhine-Moselle p-/d-/z-/-tz-, Auslautverhärtung,
     zero raw CK3 underscores/hex escapes/acutes/carons), IPA transcription, and
     compound/genitive stems for eponymous barony naming.
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from ck3_name_decoder import decode_ck3_personal_name

REPO_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_DIR / "data"
ONOMASTICON_MD = REPO_DIR / "tarraconian_onomasticon_and_name_register.md"

# ---------------------------------------------------------------------------
# Curated historical & high-frequency Tarraconian personal name adaptations
# Keys are case-folded decoded personal names (`clean_name.lower()`) or
# `(clean_name.lower(), macro_group)`.
# ---------------------------------------------------------------------------
CURATED_BASE: dict[str, tuple[str, str, str]] = {
    # Germanic / Franconian / Saxon / Anglo-Saxon / Frankish not in basic 239 key list
    "æthelred": ("Êdelrêt", "[ˈeː.dəl.reːt]", "M"),
    "ethelred": ("Êdelrêt", "[ˈeː.dəl.reːt]", "M"),
    "ælfwynn": ("Elfwîn", "[ˈɛlf.wiːn]", "F"),
    "ælfric": ("Elfrîch", "[ˈɛlf.riːç]", "M"),
    "ælfgar": ("Elfgâr", "[ˈɛlf.ɡaːr]", "M"),
    "ælfwald": ("Elfwalt", "[ˈɛlf.walt]", "M"),
    "ælfmær": ("Elfmâr", "[ˈɛlf.maːr]", "M"),
    "æthelstan": ("Edelstân", "[ˈeː.dəl.ʃtaːn]", "M"),
    "æthelwulf": ("Edelwolf", "[ˈeː.dəl.wɔlf]", "M"),
    "ælla": ("Elle", "[ˈɛ.lə]", "M"),
    "burghred": ("Burchrêt", "[ˈbʊrx.reːt]", "M"),
    "cenred": ("Kênrêt", "[ˈkeːn.reːt]", "M"),
    "cenræd": ("Kênrêt", "[ˈkeːn.reːt]", "M"),
    "rædwulf": ("Rêtwolf", "[ˈreːt.wɔlf]", "M"),
    "sæbert": ("Sêbert", "[ˈzeː.bɛrt]", "M"),
    "sælræd": ("Sêlrêt", "[ˈzeːl.reːt]", "M"),
    "sæxbald": ("Sêxbalt", "[ˈzeːks.balt]", "M"),
    "sæxræd": ("Sêxrêt", "[ˈzeːks.reːt]", "M"),
    "mærleswegn": ("Mêrlswên", "[ˈmeːrl.zweːn]", "M"),
    "eadgar": ("Êdgâr", "[ˈeːd.ɡaːr]", "M"),
    "eadmund": ("Êdmunt", "[ˈeːd.mʊnt]", "M"),
    "eadweard": ("Êdwart", "[ˈeːd.wart]", "M"),
    "harold": ("Hârolt", "[ˈhaː.rɔlt]", "M"),
    "godwine": ("Gôtwîn", "[ˈɡoːt.wiːn]", "M"),
    "oswine": ("Ôswîn", "[ˈoːs.wiːn]", "M"),
    "alfred": ("Alfrît", "[ˈal.friːt]", "M"),
    "wernhard": ("Wernhard", "[ˈwɛrn.hart]", "M"),
    "giselbert": ("Gîselbert", "[ˈɡiː.zəl.bɛrt]", "M"),
    "ekkehard": ("Ekkehart", "[ˈɛ.kə.hart]", "M"),
    "farabert": ("Fârabert", "[ˈfaː.ra.bɛrt]", "M"),
    "karlmann": ("Kârlman", "[ˈkaːrl.man]", "M"),
    "adalwin": ("Âdalwîn", "[ˈaː.dal.wiːn]", "M"),
    "adalhard": ("Âdalhart", "[ˈaː.dal.hart]", "M"),
    "sieghard": ("Sîchart", "[ˈziːç.hart]", "M"),
    "wigerich": ("Wîgerîch", "[ˈwiː.ɣə.riːç]", "M"),
    "archembald": ("Erchembalt", "[ˈɛr.çəm.balt]", "M"),
    "cobbo": ("Kôbbo", "[ˈkɔ.bo]", "M"),
    "günther": ("Günther", "[ˈɡʏn.tər]", "M"),
    "iwo": ("Îwô", "[ˈiː.woː]", "M"),
    "sigibert": ("Sîgîbert", "[ˈziː.ɡiː.bɛrt]", "M"),
    "theuderic": ("Dîterîch", "[ˈdiː.tə.riːç]", "M"),
    "burchard": ("Burkhart", "[ˈbʊrk.hart]", "M"),
    "ferdinand": ("Ferdinant", "[ˈfɛr.dɪ.nant]", "M"),
    "gerold": ("Gêrolt", "[ˈɡeː.rɔlt]", "M"),
    "wilhelm": ("Wilhelm", "[ˈwɪl.hɛlm]", "M"),

    # Old Norse / Scandinavian
    "úlfhéðinn": ("Ulfhêdîn", "[ˈʊlf.heː.diːn]", "M"),
    "vémundr": ("Wêmunt", "[ˈweː.mʊnt]", "M"),
    "bárðr": ("Bârt", "[baːrt]", "M"),
    "auðr": ("Ôde", "[ˈoː.də]", "F"),
    "hróðólfr": ("Rôdolf", "[ˈroː.dɔlf]", "M"),
    "hróðgeirr": ("Rôtger", "[ˈroːt.ɡər]", "M"),
    "garðar": ("Gartâr", "[ˈɡar.taːr]", "M"),
    "guðröðr": ("Gûdrôt", "[ˈɡuːd.roːt]", "M"),
    "starkarðr": ("Starkât", "[ˈʃtar.kaːt]", "M"),
    "starkaðr": ("Starkât", "[ˈʃtar.kaːt]", "M"),
    "þórðr": ("Thôrt", "[toːrt]", "M"),
    "þórbjörn": ("Thôrbjörn", "[ˈtoːr.bjœrn]", "M"),
    "þjóstólfr": ("Thjôstôlf", "[ˈtjoːs.toːlf]", "M"),
    "knútr": ("Knût", "[knuːt]", "M"),
    "hákon": ("Hâkon", "[ˈhaː.kɔn]", "M"),
    "håkon": ("Hâkon", "[ˈhaː.kɔn]", "M"),
    "haraldr": ("Hâralt", "[ˈhaː.ralt]", "M"),
    "óláfr": ("Ôlâf", "[ˈoː.laːf]", "M"),
    "eiríkr": ("Eirîch", "[ˈɛɪ.riːç]", "M"),
    "sveinn": ("Swên", "[zweːn]", "M"),
    "snorri": ("Snôrri", "[ˈznɔ.ri]", "M"),
    "úlfkel": ("Ulfkêl", "[ˈʊlf.keːl]", "M"),
    "úlfkell": ("Ulfkêl", "[ˈʊlf.keːl]", "M"),
    "bótólfr": ("Bôtôlf", "[ˈboː.toːlf]", "M"),
    "böðvar": ("Bödwar", "[ˈbœd.war]", "M"),
    "arnbjörn": ("Arnbjörn", "[ˈarn.bjœrn]", "M"),
    "styrbjörn": ("Stîrbjörn", "[ˈʃtiːr.bjœrn]", "M"),
    "kolbjörn": ("Kôlbjörn", "[ˈkɔl.bjœrn]", "M"),
    "högni": ("Högni", "[ˈhœɡ.ni]", "M"),
    "jörundr": ("Jörunt", "[ˈjœ.rʊnt]", "M"),
    "ögmundr": ("Ögmunt", "[ˈœɡ.mʊnt]", "M"),
    "örvar": ("Örwar", "[ˈœr.war]", "M"),
    "óttar": ("Ôttar", "[ˈoː.tar]", "M"),
    "skúli": ("Skûli", "[ˈʃkuː.li]", "M"),
    "vigfús": ("Wîgfûs", "[ˈwiːɡ.fuːs]", "M"),
    "ingfríðr": ("Ingfrît", "[ˈɪŋ.friːt]", "F"),
    "dýri": ("Dîrî", "[ˈdiː.riː]", "M"),
    "åsta": ("Âste", "[ˈaː.ʃtə]", "F"),
    "åsa": ("Âse", "[ˈaː.zə]", "F"),
    "åke": ("Âke", "[ˈaː.kə]", "M"),
    "dan": ("Dân", "[daːn]", "M"),
    "ragnarr": ("Ragnâr", "[ˈraɡ.naːr]", "M"),
    "sigurðr": ("Sîgurt", "[ˈziː.ɡʊrt]", "M"),

    # Romance (Catalan, Occitan, French, Italian, Castilian, Basque)
    "bernat": ("Bernhart", "[ˈbɛrn.hart]", "M"),
    "eudes": ("Ôdo", "[ˈoː.do]", "M"),
    "charles": ("Karl", "[karl]", "M"),
    "louis": ("Lûdwîch", "[ˈluːd.wiːç]", "M"),
    "lothaire": ("Lôthar", "[ˈloː.tar]", "M"),
    "renaud": ("Reinolt", "[ˈrɛɪ.nɔlt]", "M"),
    "joan-guerau": ("Johann-Gêrout", "[ˈjoː.han ˈɡeː.rɔʊt]", "M"),
    "guifré": ("Wîfrît", "[ˈwiː.friːt]", "M"),
    "guilhem": ("Guilhem", "[ˈɡi.ʎɛm]", "M"),
    "antso": ("Antzo", "[ˈan.tso]", "M"),
    "niccoló": ("Nîkôlô", "[niː.koː.ˈloː]", "M"),
    "niccolò": ("Nîkôlô", "[niː.koː.ˈloː]", "M"),
    "géraud": ("Gêrout", "[ˈɡeː.rɔʊt]", "M"),
    "bérenger": ("Berengâr", "[bə.rɛn.ˈɡaːr]", "M"),
    "adémar": ("Âdemâr", "[ˈaː.də.maːr]", "M"),
    "hervé": ("Herwê", "[hɛr.ˈweː]", "M"),
    "étiennette": ("Steffanîe", "[ʃtɛ.fa.ˈniː.ə]", "F"),
    "vilivald": ("Wilwalt", "[ˈwɪl.walt]", "M"),
    "raimond": ("Raimunt", "[ˈraɪ.mʊnt]", "M"),
    "ramon": ("Raimunt", "[ˈraɪ.mʊnt]", "M"),
    "ponç": ("Pontz", "[pɔnts]", "M"),
    "arnau": ("Arnolt", "[ˈar.nɔlt]", "M"),
    "berenguer": ("Berengâr", "[bə.rɛn.ˈɡaːr]", "M"),
    "guerau": ("Gêrout", "[ˈɡeː.rɔʊt]", "M"),
    "ermengol": ("Ermengôl", "[ɛr.mən.ˈɡoːl]", "M"),
    "jofre": ("Gôtfrît", "[ˈɡɔt.friːt]", "M"),
    "dalmau": ("Dalmâtz", "[dal.ˈmaːts]", "M"),
    "alfonso": ("Alfuns", "[ˈal.fʊns]", "M"),
    "rodrigo": ("Rôdrîch", "[ˈroː.driːç]", "M"),
    "sancho": ("Sanzo", "[ˈzan.tso]", "M"),
    "gatón": ("Gâtôn", "[ɡaː.ˈtoːn]", "M"),
    "gombau": ("Gômbâut", "[ɡɔm.ˈbaːʊt]", "M"),
    "léon": ("Leôn", "[le.ˈoːn]", "M"),
    "drogón": ("Drôgo", "[ˈdroː.ɡo]", "M"),
    "everardo": ("Êberhart", "[ˈeː.bər.hart]", "M"),
    "martino": ("Martîn", "[mar.ˈtiːn]", "M"),
    "augusto": ("August", "[ɔʊ.ˈɡʊst]", "M"),
    "yves": ("Îwô", "[ˈiː.woː]", "M"),
    "julien": ("Jûliân", "[juː.li.ˈaːn]", "M"),

    # Greek & Byzantine / Anatolian / Caucasian
    "ioannes": ("Jôannês", "[joː.a.ˈneːs]", "M"),
    "leon": ("Leôn", "[le.ˈoːn]", "M"),
    "kaisarios": ("Kaisâri", "[kɛɪ.ˈzaː.ri]", "M"),
    "alexandros": ("Alexânder", "[a.lɛk.ˈzan.dər]", "M"),
    "konstantinos": ("Kônstantîn", "[kɔn.ʃtan.ˈtiːn]", "M"),
    "pyrros": ("Pîrrôs", "[ˈpiː.roːs]", "M"),
    "alexios": ("Alêxi", "[a.ˈlɛk.si]", "M"),
    "manouel": ("Manuêl", "[ma.nu.ˈeːl]", "M"),
    "manuel": ("Manuêl", "[ma.nu.ˈeːl]", "M"),
    "basileios": ("Basîli", "[ba.ˈziː.li]", "M"),
    "nikephoros": ("Nîkêphôr", "[niː.keː.ˈfoːr]", "M"),
    "georgios": ("Geôrgi", "[ɡe.ˈɔr.ɣi]", "M"),
    "theodoros": ("Theodôr", "[te.o.ˈdoːr]", "M"),
    "demetrios": ("Dêmêtri", "[deː.ˈmeː.tri]", "M"),
    "andronikos": ("Andrônîk", "[an.droː.ˈniːk]", "M"),
    "christophoros": ("Chrîstôphôr", "[kriːs.toː.ˈfoːr]", "M"),
    "stephanos": ("Steffan", "[ˈʃtɛ.fan]", "M"),
    "nikolaos": ("Nîkôlôs", "[niː.koː.ˈloːs]", "M"),
    "petros": ("Pêter", "[ˈpeː.tər]", "M"),
    "romanos": ("Românôs", "[roː.ˈmaː.noːs]", "M"),
    "euphemios": ("Eufêmi", "[ɔʊ.ˈfeː.mi]", "M"),
    "nikodemos": ("Nîkôdêm", "[niː.koː.ˈdeːm]", "M"),
    "zenon": ("Zênôn", "[ˈzeː.noːn]", "M"),
    "boethios": ("Bôêthi", "[boː.ˈeː.ti]", "M"),
    "eirene": ("Eirêne", "[ɛɪ.ˈreː.nə]", "F"),
    "zoe": ("Zôê", "[ˈzoː.e]", "F"),
    "theodora": ("Theodôre", "[te.o.ˈdoː.rə]", "F"),
    "theophano": ("Theophanû", "[te.o.fa.ˈnuː]", "F"),
    "ashot": ("Aschôt", "[a.ˈʃoːt]", "M"),
    "smbat": ("Smbât", "[ˈzəm.baːt]", "M"),
    "gagik": ("Gâgîk", "[ˈɡaː.ɡiːk]", "M"),
    "bagrat": ("Bâgrât", "[ˈbaː.ɡraːt]", "M"),

    # Biblical / Hebrew / Coptic / Nubian / Christian Universal
    "zakharias": ("Zacharîas", "[za.xa.ˈriː.as]", "M"),
    "isaac": ("Îsaak", "[ˈiː.za.ak]", "M"),
    "mary magdalene": ("Marîe Magdalêne", "[ma.ˈriː.ə maɡ.da.ˈleː.nə]", "F"),
    "mary": ("Marîe", "[ma.ˈriː.ə]", "F"),
    "bartholomew": ("Barthôlomê", "[bar.toː.lo.ˈmeː]", "M"),
    "thaddeus": ("Thaddêus", "[ta.ˈdeː.ʊs]", "M"),
    "constantine": ("Costantîn", "[kɔs.tan.ˈtiːn]", "M"),
    "augustine": ("Augustîn", "[ɔʊ.ɡʊs.ˈtiːn]", "M"),
    "ambrose": ("Ambrôsi", "[am.ˈbroː.zi]", "M"),
    "jerome": ("Dscherôme", "[dʒə.ˈroː.mə]", "M"),
    "george": ("Dschôrdi", "[ˈdʒɔːr.di]", "M"),
    "catherine": ("Katrîne", "[ka.ˈtriː.nə]", "F"),
    "anthony": ("Antônî", "[an.ˈtoː.niː]", "M"),
    "basil": ("Basîli", "[ba.ˈziː.li]", "M"),

    # Arabic / Berber / Maghrebi / Andalusian / Mashriqi
    "muhammad": ("Muhammat", "[mʊ.ˈha.mat]", "M"),
    "mohammed": ("Muhammat", "[mʊ.ˈha.mat]", "M"),
    "ahmad": ("Achmat", "[ˈax.mat]", "M"),
    "isa": ("Îsâ", "[ˈiː.zaː]", "M"),
    "yusuf": ("Jûsuf", "[ˈjuː.zʊf]", "M"),
    "ali": ("Âlî", "[ˈaː.liː]", "M"),
    "musa": ("Mûsâ", "[ˈmuː.zaː]", "M"),
    "ibrahim": ("Îbrâhîm", "[iː.braː.ˈhiːm]", "M"),
    "abdallah": ("Abdallâh", "[ab.da.ˈlaː]", "M"),
    "abdullah": ("Abdullâh", "[ab.dʊ.ˈlaː]", "M"),
    "al-muwaffak": ("Al-Muwaffak", "[al.mʊ.ˈwa.fak]", "M"),
    "ubayd": ("Ubeit", "[ˈʊ.bɛɪt]", "M"),
    "abd-al-rahman": ("Abd-ar-Rahmân", "[abd.ar.rax.ˈmaːn]", "M"),
    "abd-al-aziz": ("Abd-al-Âzîz", "[abd.al.aː.ˈziːz]", "M"),
    "mahmud": ("Machmût", "[max.ˈmuːt]", "M"),
    "umar": ("Ômar", "[ˈoː.mar]", "M"),
    "ya'qub": ("Jâkûp", "[jaː.ˈkuːp]", "M"),
    "halil": ("Chalîl", "[xa.ˈliːl]", "M"),
    "khumarawayh": ("Chumârawei", "[xu.maː.ra.ˈwɛɪ]", "M"),
    "khalid": ("Châlît", "[ˈxaː.liːt]", "M"),
    "mu'izz": ("Mu'îtz", "[mʊ.ˈiːts]", "M"),
    "yahya": ("Jachjâ", "[jax.ˈjaː]", "M"),
    "hisham": ("Hîschâm", "[hiː.ˈʃaːm]", "M"),
    "abu'l-maghra": ("Abû-l-Magrâ", "[a.buːl.ˈmaɡ.raː]", "M"),
    "abdul-azeem": ("Abdul-Âzîm", "[ab.dʊl.aː.ˈziːm]", "M"),
    "adanis": ("Adânîs", "[a.daː.ˈniːs]", "M"),
    "wabisah": ("Wabîse", "[wa.ˈbiː.zə]", "M"),
    "khafif": ("Chafîf", "[xa.ˈfiːf]", "M"),
    "ṭāriq": ("Târîk", "[taː.ˈriːk]", "M"),
    "ja'far": ("Dschafar", "[ˈdʒa.far]", "M"),
    "hasan": ("Hâsan", "[ˈhaː.zan]", "M"),
    "husayn": ("Husain", "[hʊ.ˈsaɪn]", "M"),
    "sulayman": ("Sulaimân", "[zʊ.laɪ.ˈmaːn]", "M"),
    "mansur": ("Mansûr", "[man.ˈzuːr]", "M"),
    "harun": ("Hârûn", "[haː.ˈruːn]", "M"),
    "sa'id": ("Saît", "[za.ˈiːt]", "M"),
    "mas'ud": ("Masût", "[ma.ˈzuːt]", "M"),
    "da'ud": ("Dâût", "[daː.ˈuːt]", "M"),
    "isma'il": ("Îsmâîl", "[iːz.maː.ˈiːl]", "M"),
    "mu'awiyah": ("Mu'âwîje", "[mʊ.aː.ˈwiː.jə]", "M"),
    "uthman": ("Uthmân", "[ʊt.ˈmaːn]", "M"),
    "ḥemmu": ("Hemmû", "[hɛ.ˈmuː]", "M"),
    "žeffun": ("Zeffûn", "[zɛ.ˈfuːn]", "M"),
    "waṭṭās": ("Wattâs", "[wa.ˈtaːs]", "M"),

    # Slavic & Baltic
    "boris": ("Bôris", "[ˈboː.rɪs]", "M"),
    "vladimir": ("Wâldemâr", "[ˈwaːl.də.maːr]", "M"),
    "treniotas": ("Treniôtas", "[trɛ.ni.ˈoː.tas]", "M"),
    "jarosław": ("Jârôslaf", "[ˈjaː.roːs.laf]", "M"),
    "stanisław": ("Stanîslaf", "[ˈʃta.niːs.laf]", "M"),
    "włodzisław": ("Wlôdislaf", "[ˈwloː.dɪs.laf]", "M"),
    "władysław": ("Wlâdislaf", "[ˈwlaː.dɪs.laf]", "M"),
    "wacław": ("Wentzel", "[ˈvɛn.tsəl]", "M"),
    "przemysław": ("Prschemîslaf", "[ˈprʃɛ.miːs.laf]", "M"),
    "miłobrat": ("Mîlobrât", "[ˈmiː.lo.braːt]", "M"),
    "mikołaj": ("Nîkôlôs", "[niː.koː.ˈloːs]", "M"),
    "bogumił": ("Bôgumîl", "[ˈboː.ɡʊ.miːl]", "M"),
    "bohumír": ("Bôhumîr", "[ˈboː.hʊ.miːr]", "M"),
    "slavomír": ("Slâwomîr", "[ˈzlaː.wo.miːr]", "M"),
    "mojmír": ("Moimîr", "[ˈmɔɪ.miːr]", "M"),
    "velemír": ("Wêlemîr", "[ˈweː.lə.miːr]", "M"),
    "mačko": ("Matschko", "[ˈmatʃ.ko]", "M"),
    "bończa": ("Bontsche", "[ˈbɔn.tʃə]", "M"),
    "elžbieta": ("Elzbête", "[ɛlz.ˈbeː.tə]", "F"),
    "zwinisława": ("Zwinîslâwe", "[zwi.niːs.ˈlaː.wə]", "F"),
    "svatopluk": ("Swâtopluk", "[ˈzwaː.to.plʊk]", "M"),
    "casimir": ("Kâzimîr", "[ˈkaː.zi.miːr]", "M"),
    "kazimierz": ("Kâzimîr", "[ˈkaː.zi.miːr]", "M"),
    "oleg": ("Ôlech", "[ˈoː.lɛç]", "M"),
    "igor": ("Îgor", "[ˈiː.ɡɔr]", "M"),
    "ivan": ("Îwân", "[iː.ˈwaːn]", "M"),

    # Hungarian / Magyar
    "istván": ("Istwân", "[ˈɪʃt.waːn]", "M"),
    "árpád": ("Ârpât", "[ˈaːr.paːt]", "M"),
    "béla": ("Bêle", "[ˈbeː.lə]", "M"),
    "lászló": ("Lâslô", "[ˈlaːs.loː]", "M"),
    "lórinc": ("Lôrintz", "[ˈloː.rɪnts]", "M"),
    "jános": ("Jânôs", "[ˈjaː.noːs]", "M"),
    "andrás": ("Andrâsch", "[ˈan.draːʃ]", "M"),
    "miklós": ("Mîklôsch", "[ˈmiːk.loːʃ]", "M"),
    "kálmán": ("Kâlmân", "[ˈkaːl.maːn]", "M"),
    "gellért": ("Gellêrt", "[ˈɡɛ.leːrt]", "M"),
    "álmos": ("Âlmôsch", "[ˈaːl.moːʃ]", "M"),
    "csák": ("Tschâk", "[tʃaːk]", "M"),
    "dömötör": ("Dömötör", "[ˈdœ.mœ.tœr]", "M"),
    "ödön": ("Ödön", "[ˈœ.dœn]", "M"),
    "tamás": ("Tamâsch", "[ˈta.maːʃ]", "M"),
    "bálint": ("Bâlînt", "[ˈbaː.liːnt]", "M"),
    "lukács": ("Lukâtsch", "[ˈlu.kaːtʃ]", "M"),
    "gábriel": ("Gâbriêl", "[ɡaː.bri.ˈeːl]", "M"),
    "péter": ("Pêter", "[ˈpeː.tər]", "M"),
    "jenő": ("Jenö", "[ˈjɛ.nœ]", "M"),

    # Turkic / Steppe / Persian / Iranian
    "kara": ("Kâra", "[ˈkaː.ra]", "M"),
    "taimur": ("Taimûr", "[taɪ.ˈmuːr]", "M"),
    "ilik": ("Ilîk", "[ɪ.ˈliːk]", "M"),
    "khudayar": ("Chudâjâr", "[xu.daː.ˈjaːr]", "M"),
    "feraz": ("Fêrâz", "[feː.ˈraːts]", "M"),
    "fezl": ("Fêzl", "[ˈfeːtsəl]", "M"),
    "kiliç": ("Kilîtsch", "[kɪ.ˈliːtʃ]", "M"),
    "çağri": ("Tschâgrî", "[ˈtʃaː.ɡriː]", "M"),
    "alp arslan": ("Alp Arslân", "[alp ar.ˈzlaːn]", "M"),
    "xuršíd": ("Churschît", "[xʊr.ˈʃiːt]", "M"),
    "šahrux": ("Schâhruch", "[ˈʃaːx.rʊx]", "M"),
    "daryúš": ("Dârjûsch", "[daːr.ˈjuːʃ]", "M"),
    "danúš": ("Dânûsch", "[daː.ˈnuːʃ]", "M"),
    "kúrušé": ("Kûrûsche", "[kuː.ˈruː.ʃə]", "M"),
    "könček": ("Köntschek", "[ˈkœn.tʃɛk]", "M"),
    "eldecük": ("Eldetschük", "[ˈɛl.də.tʃʏk]", "M"),
    "eldečyuk": ("Eldetschük", "[ˈɛl.də.tʃʏk]", "M"),
    "sevinč": ("Sewîntsch", "[zə.ˈwiːntʃ]", "M"),
    "sevenč": ("Sewêntsch", "[zə.ˈweːntʃ]", "M"),

    # Celtic (Irish, Gaelic, Welsh, Breton)
    "íomhar": ("Îwar", "[ˈiː.war]", "M"),
    "áed": ("Aêt", "[a.ˈeːt]", "M"),
    "máel-sechnaill": ("Mêl-Sechnal", "[meːl.ˈzɛx.nal]", "M"),
    "máel-máedóc": ("Mêl-Mêdôk", "[meːl.ˈmeː.doːk]", "M"),
    "cenn-fáelad": ("Ken-Fêlat", "[kɛn.ˈfeː.lat]", "M"),
    "cathalán": ("Kâtalân", "[kaː.ta.ˈlaːn]", "M"),
    "causantín": ("Kôstantîn", "[kɔs.tan.ˈtiːn]", "M"),
    "cináed": ("Kînêt", "[kiː.ˈneːt]", "M"),
    "murchú": ("Murchû", "[ˈmʊr.xuː]", "M"),
    "dúnchad": ("Dûnchat", "[ˈduːn.xat]", "M"),

    # Indic / Southeast Asian
    "sena": ("Sêna", "[ˈzeː.na]", "M"),
    "sangappai": ("Sangappai", "[zaŋ.ˈɡa.paɪ]", "M"),
    "polachola": ("Pôlatschôla", "[poː.la.ˈtʃoː.la]", "M"),
    "narayanapala": ("Nârâjânapâla", "[naː.raː.jaː.na.ˈpaː.la]", "M"),
    "lokapala": ("Lôkapâla", "[loː.ka.ˈpaː.la]", "M"),
    "udaysangh": ("Udeisang", "[ʊ.dɛɪ.ˈzaŋ]", "M"),
    "varakunavarman": ("Warakunâwarman", "[wa.ra.ku.naː.ˈwar.man]", "M"),
    "kulacékara": ("Kulatschêkara", "[ku.la.ˈtʃeː.ka.ra]", "M"),
    "vikramaditya jayameru": ("Wikramâdîtscha Dschâjamêru", "[wɪk.ra.maː.ˈdiː.tʃa dʒaː.ja.ˈmeː.ru]", "M"),
    "suraj dev": ("Sûratsch Dêw", "[ˈzuː.ratʃ deːw]", "M"),
    "dara petak": ("Dâra Pêtak", "[ˈdaː.ra ˈpeː.tak]", "F"),

    # Sinosphere (Chinese, Korean, Japanese, Jurchen/Mohe, Tibetic)
    "wei": ("Wei", "[wɛɪ]", "M"),
    "tong": ("Tông", "[toːŋ]", "M"),
    "yi": ("Jî", "[jiː]", "M"),
    "yun": ("Jün", "[jyn]", "M"),
    "bo": ("Bô", "[boː]", "M"),
    "yan": ("Jân", "[jaːn]", "M"),
    "gui": ("Gui", "[ɡwɛɪ]", "M"),
    "yu": ("Jü", "[jyː]", "M"),
    "qian": ("Tschiân", "[tʃjaːn]", "M"),
    "ji": ("Dschî", "[dʒiː]", "M"),
    "yao": ("Jao", "[jaʊ]", "M"),
    "xun": ("Schün", "[ʃyn]", "M"),
    "fu": ("Fû", "[fuː]", "M"),
    "tian": ("Tiân", "[tjaːn]", "M"),
    "hong": ("Hông", "[hoːŋ]", "M"),
    "xiu": ("Schîu", "[ʃiʊ]", "M"),
    "kui": ("Kui", "[kwɛɪ]", "M"),
    "han": ("Hân", "[haːn]", "M"),
    "jianzhi": ("Dschiândschi", "[dʒjaːn.ˈdʒi]", "M"),
    "quan": ("Tschüân", "[tʃɥaːn]", "M"),
    "xizhuang": ("Schîdschuang", "[ʃiː.ˈdʒwaŋ]", "M"),
    "qing": ("Tsching", "[tʃɪŋ]", "M"),
    "zhi": ("Dschi", "[dʒi]", "M"),
    "aguda": ("Agûdâ", "[a.ˈɡuː.daː]", "M"),
    "xingyan": ("Schingjân", "[ʃɪŋ.ˈjaːn]", "M"),
    "a-cang": ("A-zang", "[ˈaː.tsaŋ]", "M"),
    "tsunetō": ("Zûnêtô", "[tsuː.ˈneː.toː]", "M"),
    "yoshifusa": ("Jôschifûsa", "[joː.ʃɪ.ˈfuː.za]", "M"),
    "takamochi": ("Takamôtschi", "[ta.ka.ˈmoː.tʃi]", "M"),
    "won-ui": ("Won-ui", "[ˈwɔn.ʊɪ]", "M"),
    "gyeong-ae": ("Gjông-ê", "[ˈɡjɔŋ.eː]", "F"),
    "seong-gyu": ("Sông-gju", "[ˈzɔŋ.ɡju]", "M"),
    "tridé yumten": ("Trîdê Jumten", "[ˈtriː.deː ˈjʊm.tɛn]", "M"),
    "namdé ösung": ("Namdê Ösung", "[ˈnam.deː ˈœ.zʊŋ]", "M"),

    # African
    "sungu": ("Sungû", "[zʊŋ.ˈɡuː]", "M"),
    "bore-wo": ("Bôre-wô", "[ˈboː.rə.woː]", "M"),
    "alí bábá": ("Âlî Bâbâ", "[aː.ˈliː baː.ˈbaː]", "M"),
}

# Family -> macro strategy bucket
def get_macro_group(morph_family: str) -> str:
    mf = (morph_family or "").lower()
    if mf in {"tarraconian_imperial", "high_german", "low_german_dutch"}:
        return "germanic_west"
    if mf == "anglo_saxon":
        return "anglo_saxon"
    if mf == "north_germanic":
        return "norse"
    if mf in {"ibero_romance", "occitano_catalan", "gallo_romance", "italo_romance", "eastern_romance", "latin_classical"}:
        return "romance"
    if mf in {"hellenic", "armenian", "kartvelian", "egyptian_coptic"}:
        return "hellenic_eastern"
    if mf in {"east_slavic", "south_slavic", "west_slavic_lechitic", "west_slavic_czech_slovak", "baltic"}:
        return "slavic_baltic"
    if mf in {"magyar", "finnic", "sami", "volga_permian"}:
        return "uralic"
    if mf in {"arabic", "berber", "aramaic_hebrew"}:
        return "semitic_berber"
    if mf in {"turkic", "oghur", "mongolic"}:
        return "turkic_mongolic"
    if mf in {"iranian"}:
        return "iranian"
    if mf in {"goidelic", "brythonic"}:
        return "celtic"
    if mf in {"indo_aryan", "dravidian", "austronesian", "mon_khmer", "tai_hmong", "viet"}:
        return "indic_sea"
    if mf in {"sinosphere_chinese", "khitan", "tungusic"}:
        return "sinosphere_sinitic"
    if mf in {"korean"}:
        return "korean"
    if mf in {"japonic", "ainu"}:
        return "japonic"
    if mf in {"tibetic", "burmese_qiangic"}:
        return "tibetic"
    if mf in {"west_central_african", "east_bantu_swahili", "ethiopic_cushitic"}:
        return "african"
    return "general"


def parse_canonical_onomasticon() -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    """
    Parse tarraconian_onomasticon_and_name_register.md tables for:
      - 239 official name_list_franconian entries
      - expanded Chancellery entries (Sections 3.4 saints + Section 5 additions)
    """
    text = ONOMASTICON_MD.read_text(encoding="utf-8")
    franconian: dict[str, dict[str, Any]] = {}
    expanded: dict[str, dict[str, Any]] = {}

    section = ""
    for line in text.splitlines():
        if line.startswith("## 2.1 ") or line.startswith("### 2.1 "):
            section = "male_239"
        elif line.startswith("### 2.2 "):
            section = "female_239"
        elif line.startswith("### 3.4 "):
            section = "saints_conc"
        elif line.startswith("### 5.1 "):
            section = "male_ext"
        elif line.startswith("### 5.2 "):
            section = "female_ext"
        elif line.startswith("## 6."):
            section = ""

        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or cells[0] in ("#", ":---:", "Saint Name", "Category", "---"):
            continue
        if all(set(c) <= set(":- ") for c in cells):
            continue

        if section in ("male_239", "female_239") and len(cells) >= 6:
            num_s, key_s, van_s, tarr_s, ipa_s, notes_s = cells[:6]
            if not num_s.isdigit():
                continue
            key = key_s.strip("` ")
            vanilla = van_s.strip("* ")
            tarr = tarr_s.strip("* ")
            ipa = ipa_s.strip("` ")
            gender = "M" if section == "male_239" else "F"
            franconian[key] = {
                "index": int(num_s),
                "ck3_key": key,
                "vanilla_name": vanilla,
                "tarr_name": tarr,
                "tarr_ipa": ipa,
                "gender": gender,
                "notes": notes_s,
            }
        elif section == "saints_conc" and len(cells) >= 7:
            saint_n, sphere, gen, tarr_s, ipa_s, feast, ctx = cells[:7]
            saint_clean = saint_n.strip("* ")
            tarr = tarr_s.strip("* ").split("/")[0].strip()
            expanded[saint_clean.lower()] = {
                "source_label": saint_clean,
                "sphere": sphere,
                "gender": gen.strip(),
                "tarr_name": tarr,
                "tarr_aliases": [x.strip() for x in tarr_s.strip("* ").split("/")],
                "tarr_ipa": ipa_s.strip("` "),
                "feast_day": feast,
                "source_section": "section_3_4_saint",
            }
        elif section in ("male_ext", "female_ext") and len(cells) >= 4:
            cat, nm_s, ipa_s, basis = cells[:4]
            nm = nm_s.strip("* ")
            expanded.setdefault(
                nm.lower(),
                {
                    "source_label": nm,
                    "sphere": cat,
                    "gender": "M" if section == "male_ext" else "F",
                    "tarr_name": nm,
                    "tarr_aliases": [nm],
                    "tarr_ipa": ipa_s.strip("` "),
                    "source_section": "section_5_expansion",
                    "notes": basis,
                },
            )
    return franconian, expanded


def _strip_disallowed_diacritics(s: str) -> str:
    """
    Ensure strict Chancellery orthography:
    - Convert acute/macron/tilde/caron/cedilla/barred-l/eth/thorn to Tarraconian Latin
      with circumflexes (â ê î ô û) instead of acutes.
    - Keep only [A-Za-zâêîôûÂÊÎÔÛäöüÄÖÜïëÏ '-].
    """
    rep = {
        "á": "â", "à": "a", "ā": "â", "ă": "a", "ą": "a",
        "Á": "Â", "À": "A", "Ā": "Â", "Ă": "A", "Ą": "A",
        "é": "ê", "è": "e", "ē": "ê", "ě": "e", "ę": "e", "æ": "ê",
        "É": "Ê", "È": "E", "Ē": "Ê", "Ě": "E", "Ę": "E", "Æ": "Ê",
        "í": "î", "ì": "i", "ī": "î", "ý": "î", "ÿ": "i",
        "Í": "Î", "Ì": "I", "Ī": "Î", "Ý": "Î",
        "ó": "ô", "ò": "o", "ō": "ô", "õ": "ô", "ø": "ö", "ő": "ö",
        "Ó": "Ô", "Ò": "O", "Ō": "Ô", "Õ": "Ô", "Ø": "Ö", "Ő": "Ö",
        "ú": "û", "ù": "u", "ū": "û", "ů": "û", "ű": "ü",
        "Ú": "Û", "Ù": "U", "Ū": "Û", "Ů": "Û", "Ű": "Ü",
        "å": "â", "Å": "Â",
        "ç": "tsch", "Ç": "Tsch",
        "č": "tsch", "Č": "Tsch",
        "š": "sch", "Š": "Sch",
        "ş": "sch", "Ş": "Sch",
        "ž": "sch", "Ž": "Sch",
        "ř": "rsch", "Ř": "Rsch",
        "ł": "l", "Ł": "L",
        "ń": "n", "Ń": "N",
        "ñ": "nj", "Ñ": "Nj",
        "ğ": "g", "Ğ": "G",
        "þ": "th", "Þ": "Th",
        "ð": "d", "Ð": "D",
        "ḥ": "h", "Ḥ": "H",
        "ṭ": "t", "Ṭ": "T",
        "ṇ": "n", "Ṇ": "N",
        "ı": "i", "İ": "I",
        "ß": "ss",
    }
    out = "".join(rep.get(ch, ch) for ch in s)
    # Strip any remaining combining marks (e.g. from decomposed strings)
    nfkd = unicodedata.normalize("NFC", out)
    # Remove any stray non-allowed chars while preserving allowed circumflexes/umlauts
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzâêîôûÂÊÎÔÛäöüÄÖÜïëÏ '-")
    cleaned = []
    for ch in nfkd:
        if ch in allowed:
            cleaned.append(ch)
        else:
            decomp = unicodedata.normalize("NFD", ch)
            base = "".join(c for c in decomp if unicodedata.category(c) != "Mn")
            for b in base:
                if b in allowed:
                    cleaned.append(b)
    return "".join(cleaned)


def _adapt_single_token(token: str, macro: str) -> str:
    """Adapt a single personal-name token phonologically according to macro language family."""
    if not token:
        return token

    # First replace known CK3/Unicode diacritics before digraph adaptation,
    # keeping track of Czech/Turkic ç/č/š so family conversion can distinguish.
    low = token.lower()

    # Handle Arabic hyphenated particles as-is if token is purely particle
    if low in {"al", "ar", "as", "ad", "an", "at", "az", "ash", "el", "ibn", "bin", "abu", "abdul", "abdur"}:
        return token if token[0].isupper() else low

    # Pre-normalize non-allowed characters into Tarraconian graphemes
    # Handle some family-specific letters BEFORE generic stripping:
    s = token
    def _case(m_str: str, repl: str) -> str:
        return repl.capitalize() if m_str[0].isupper() else repl

    if macro == "sinosphere_sinitic":
        # Single-pass Song/Chancellery Pinyin adaptation (zero cascade overlap)
        s = re.sub(
            r"^(?:[Tt]s(?![cs]))|[Zz]h|[Cc]h|[Ss]h|\b[Qq]|[Qq]|\b[Cc](?=[aeou])|\b[Xx](?=[iu])|\b[Jj](?=[iu])|\b[Yy]",
            lambda m: _case(
                m.group(0),
                {
                    "ts": "z", "zh": "dsch", "ch": "tsch", "sh": "sch",
                    "q": "tsch", "c": "z", "x": "sch", "j": "dsch", "y": "j",
                }[m.group(0).lower()],
            ),
            s,
        )
    elif macro == "korean":
        s = re.sub(
            r"\b[Cc]h|[Ss]h|\b[Jj]|[Ee]o|[Ee]u|\b[Yy]",
            lambda m: _case(
                m.group(0),
                {"ch": "tsch", "sh": "sch", "j": "dsch", "eo": "ô", "eu": "û", "y": "j"}[m.group(0).lower()],
            ),
            s,
        )
    elif macro == "japonic":
        s = re.sub(
            r"^[Tt]s|[Tt]s|[Ss]h|[Cc]h|[Jj]|\b[Yy]",
            lambda m: (
                _case(m.group(0), "z") if m.start() == 0 and m.group(0).lower() == "ts"
                else _case(m.group(0), {"ts": "tz", "sh": "sch", "ch": "tsch", "j": "dsch", "y": "j"}[m.group(0).lower()])
            ),
            s,
        )
        if s.endswith("o"):
            s = s[:-1] + "ô"
    elif macro == "tibetic":
        s = re.sub(
            r"^[Tt]s|[Ss]h|[Cc]h|[Jj]|\b[Yy]",
            lambda m: _case(m.group(0), {"ts": "z", "sh": "sch", "ch": "tsch", "j": "dsch", "y": "j"}[m.group(0).lower()]),
            s,
        )
    elif macro in {"turkic_mongolic", "iranian", "indic_sea"}:
        pat = r"[Ss]h|[Kk]h|[Cc]h|[Jj]|[Qq]|\b[Vv]|(?<=[aeiouâêîôû])[v](?=[aeiouâêîôû])|\b[Yy]|(?<=[aeiouâêîôû])[y](?=[aeiouâêîôû])"
        if macro == "turkic_mongolic":
            pat = r"\b[Cc](?!h)|" + pat
        elif macro == "iranian":
            pat = r"\b[Xx]|" + pat
        s = re.sub(
            pat,
            lambda m: _case(
                m.group(0),
                {
                    "c": "dsch", "x": "ch", "sh": "sch", "kh": "ch",
                    "ch": "tsch", "j": "dsch", "q": "k", "v": "w", "y": "j",
                }[m.group(0).lower()],
            ),
            s,
        )
    elif macro == "semitic_berber":
        s = s.replace("'", "")
        s = re.sub(
            r"[Ss]h|[Kk]h|[Jj]|[Qq]|\b[Yy]|(?<=[aeiouâêîôû])[y](?=[aeiouâêîôû])",
            lambda m: _case(
                m.group(0),
                {"sh": "sch", "kh": "ch", "j": "dsch", "q": "k", "y": "j"}[m.group(0).lower()],
            ),
            s,
        )
    elif macro == "slavic_baltic":
        s = re.sub(
            r"[Ss]z|[Cc]z|[Rr]z|\b[Cc](?=[aeiouyâêîôû])|(?<=.)[Cc](?=[eiy]|$)|[Vv]",
            lambda m: _case(
                m.group(0),
                {"sz": "sch", "cz": "tsch", "rz": "rsch", "c": "z" if m.start() == 0 else "tz", "v": "w"}[m.group(0).lower()],
            ),
            s,
        )
        if re.search(r"slav$|slaw$", s, re.I):
            s = re.sub(r"sl[av]w?$|sla[vw]$", "slaf", s, flags=re.I)
    elif macro == "uralic":
        s = re.sub(
            r"[Ss]z|[Cc]s|[Vv]",
            lambda m: _case(m.group(0), {"sz": "s", "cs": "tsch", "v": "w"}[m.group(0).lower()]),
            s,
        )
    elif macro == "hellenic_eastern":
        s = re.sub(r"\b[Cc](?=[aouklr])", lambda m: "K" if m.group(0)[0].isupper() else "k", s)
        s = re.sub(r"[Ss]h", lambda m: "Sch" if m.group(0)[0].isupper() else "sch", s)
        if s.endswith("ios") and len(s) > 4:
            s = s[:-3] + "i"
        elif s.endswith("os") and len(s) > 4:
            s = s[:-2] + "ôs"
        elif s.endswith("es") and len(s) > 4:
            s = s[:-2] + "ês"
    elif macro == "romance":
        if s.endswith("a") and len(s) > 3 and not s.endswith("ia"):
            s = s[:-1] + "e"
    elif macro in {"germanic_west", "anglo_saxon", "norse"}:
        s = re.sub(r"[Cc]k", "k", s)
        if s.endswith("frid"):
            s = s[:-4] + "frît"
        elif s.endswith("rich"):
            s = s[:-4] + "rîch"
        if macro == "norse":
            # Drop Old Norse nom -r ending after consonant (e.g. Haraldr -> Haralt)
            if len(s) > 3 and s.endswith("r") and s[-2] in "ðdþtfkln":
                s = s[:-1]

    # Strip remaining exotic diacritics -> clean Chancellery vowels/consonants
    s = _strip_disallowed_diacritics(s)

    # Global Chancellery constraints:
    # 1) Never leave initial Ts- (except Tsch-)
    if re.match(r"^[Tt]s(?![ch])", s):
        s = ("Z" if s[0].isupper() else "z") + s[2:]
    # 2) Never leave unadapted Pinyin q- (except qu)
    s = re.sub(r"[Qq](?![uU])", lambda m: "K" if m.group(0).isupper() else "k", s)
    # 3) Never leave bare 'sh' -> 'sch' or Cyrillic/Uralic 'zh' -> 'sch' (Sinitic 'zh' -> 'dsch' handled above)
    s = re.sub(r"(?<!c)[Ss]h", lambda m: "Sch" if m.group(0)[0].isupper() else "sch", s)
    if macro in {"sinosphere_sinitic", "korean", "tibetic"}:
        s = re.sub(r"[Zz]h", lambda m: "Dsch" if m.group(0)[0].isupper() else "dsch", s)
    else:
        s = re.sub(r"[Zz]h", lambda m: "Sch" if m.group(0)[0].isupper() else "sch", s)
    # 4) Avoid accidental triple consonants like schch or dschsch
    s = s.replace("schch", "sch").replace("Tschtsch", "Tsch").replace("tschtsch", "tsch")
    s = s.replace("dschsch", "dsch").replace("Schsch", "Sch").replace("schsch", "sch")

    # 5) Auslautverhärtung (final devoicing)
    if macro in {"germanic_west", "anglo_saxon", "norse", "slavic_baltic", "uralic", "semitic_berber", "iranian", "turkic_mongolic", "celtic"}:
        if s.endswith("dsch"):
            s = s[:-4] + "tsch"
        elif s.endswith("d") and len(s) > 2:
            s = s[:-1] + "t"
        elif s.endswith("b") and len(s) > 2:
            s = s[:-1] + "p"
        elif s.endswith("v") and len(s) > 2:
            s = s[:-1] + "f"
        elif s.endswith("g") and not s.endswith("ng") and len(s) > 2:
            s = s[:-1] + "ch"

    # Ensure primary stressed long/open vowel or penultimate circumflex if none present in polysyllables from Germanic/Arabic/Persian/Slavic/Sinosphere
    if not any(ch in s for ch in "âêîôûÂÊÎÔÛäöüÄÖÜ"):
        # Lengthen -ar/-an/-in/-un/-ur/-or/-it/-il endings when multi-syllable or CVC heavy tail
        for suf_old, suf_new in [
            ("an", "ân"), ("on", "ôn"), ("un", "ûn"), ("in", "în"),
            ("ar", "âr"), ("ir", "îr"), ("ur", "ûr"), ("or", "ôr"),
            ("ud", "ût"), ("ut", "ût"), ("id", "ît"), ("it", "ît"),
            ("am", "âm"), ("im", "îm"), ("um", "ûm"),
        ]:
            if len(s) >= 4 and s.endswith(suf_old) and not s.endswith("en"):
                s = s[: -len(suf_old)] + suf_new
                break

    if s and s[0].islower() and token[0].isupper():
        s = s[0].upper() + s[1:]
    return s


def approximate_ipa(tarr_name: str) -> str:
    """Deterministic broad phonetic IPA transcription matching Chancellery conventions."""
    s = tarr_name.lower()
    tokens = [
        ("dsch", "dʒ"), ("tsch", "tʃ"), ("sch", "ʃ"), ("ch", "x"),
        ("tz", "ts"), ("qu", "kv"), ("ck", "k"), ("ss", "s"), ("ll", "l"),
        ("ca", "ka"), ("co", "ko"), ("cu", "ku"), ("cr", "kr"), ("cl", "kl"),
        ("câ", "kaː"), ("cô", "koː"), ("cû", "kuː"), ("ce", "tsə"), ("ci", "tsɪ"),
        ("â", "aː"), ("ê", "eː"), ("î", "iː"), ("ô", "oː"), ("û", "uː"),
        ("ä", "ɛ"), ("ö", "œ"), ("ü", "ʏ"),
        ("ai", "aɪ"), ("au", "aʊ"), ("ei", "ɛɪ"), ("eu", "ɔʏ"), ("ou", "ɔʊ"),
        ("ng", "ŋ"), ("j", "j"), ("z", "ts"), ("s", "z"), ("v", "f"),
        ("w", "w"), ("r", "r"), ("l", "l"), ("m", "m"), ("n", "n"),
        ("p", "p"), ("b", "b"), ("t", "t"), ("d", "d"), ("k", "k"), ("g", "ɡ"),
        ("f", "f"), ("h", "h"), ("a", "a"), ("e", "ə"), ("i", "ɪ"), ("o", "ɔ"), ("u", "ʊ"),
        (" ", " "), ("-", "."),
    ]
    out = []
    i = 0
    while i < len(s):
        matched = False
        for k, v in tokens:
            if s.startswith(k, i):
                out.append(v)
                i += len(k)
                matched = True
                break
        if not matched:
            out.append(s[i])
            i += 1
    return "[" + "".join(out) + "]"


def build_genitive_and_prefix(tarr_name: str, gender: str = "M") -> tuple[str, str]:
    """Return `(tarr_genitive_stem, tarr_compound_prefix)` for castle/city/abbey naming."""
    clean = tarr_name.replace("'", "")
    low = clean.lower()
    if low.endswith(("s", "sch", "tz", "z", "x")):
        return (clean, clean)
    if low.endswith("e") and len(clean) > 3:
        # Weak stem (-en) e.g. Âdele -> Âdelenburch / Bêle -> Bêlenburch
        return (clean + "n", clean + "n")
    if low[-1] in "âêîôûaiou":
        return (clean + "s", clean)
    if gender == "F" and not low.endswith("e"):
        return (clean + "e", clean)
    return (clean + "s", clean + "s")


def main() -> None:
    franconian, expanded = parse_canonical_onomasticon()

    with open(DATA_DIR / "ck3_culture_to_iso_and_generics.json", encoding="utf-8") as f:
        cult_bridge = json.load(f)["cultures"]

    with open(DATA_DIR / "sinosphere_kanji_tarraconian.json", encoding="utf-8") as f:
        kanji_list = json.load(f)
    kanji_dict: dict[str, dict[str, Any]] = {}
    for item in kanji_list:
        if isinstance(item, dict) and item.get("char"):
            kanji_dict[item["char"]] = item
            if item.get("var") and item["var"] != "-":
                for vch in item["var"].split("/"):
                    vch = vch.strip()
                    if vch:
                        kanji_dict.setdefault(vch, item)

    with open(DATA_DIR / "barony_coinage_rulers.json", encoding="utf-8") as f:
        coinage = json.load(f)["baronies"]

    with open(DATA_DIR / "barony_physical_and_event_context.json", encoding="utf-8") as f:
        phys = json.load(f)

    # Quick lookup maps for canonical Franconian keys (case-insensitive & vanilla)
    franc_by_key_low = {k.lower(): v for k, v in franconian.items()}
    franc_by_vanilla_low = {v["vanilla_name"].lower(): v for v in franconian.values()}

    # Collect coinage stats per raw_first_name
    raw_stats: dict[str, dict[str, Any]] = {}
    for bk, rec in coinage.items():
        raw = rec.get("raw_first_name") or ""
        if not raw:
            continue
        rcult = rec.get("ruler_culture") or rec.get("coinage_culture") or "unknown"
        entry = raw_stats.setdefault(raw, {
            "count": 0,
            "cultures": Counter(),
            "sample_baronies": [],
            "is_saint": False,
            "saint_faiths": set(),
        })
        entry["count"] += 1
        entry["cultures"][rcult] += 1
        if len(entry["sample_baronies"]) < 5:
            entry["sample_baronies"].append(bk)

    # Also collect all faith_saints raw names so 100% of patron saints are covered
    for fid, fobj in phys.get("faith_saints", {}).items():
        ftype = fobj.get("faith_type")
        for s in fobj.get("saints", []):
            raw = s.get("raw_name") or ""
            if not raw:
                continue
            scult = s.get("culture") or "christian_universal"
            entry = raw_stats.setdefault(raw, {
                "count": 0,
                "cultures": Counter(),
                "sample_baronies": [],
                "is_saint": True,
                "saint_faiths": set(),
            })
            entry["is_saint"] = True
            if ftype:
                entry["saint_faiths"].add(ftype)
            if entry["count"] == 0 or scult != "christian_universal":
                entry["cultures"][scult] += 1

    def resolve_macro(cult_name: str) -> str:
        cinfo = cult_bridge.get(cult_name) or cult_bridge.get(cult_name.lower())
        if cinfo:
            return get_macro_group(cinfo.get("morphology_family", ""))
        cl = cult_name.lower()
        if "tarraconian" in cl or "lothringian" in cl:
            return "germanic_west"
        if "greek" in cl:
            return "hellenic_eastern"
        return "general"

    names_by_raw: dict[str, dict[str, Any]] = {}
    clean_index: dict[str, dict[str, Any]] = {}
    tier_counts: Counter[str] = Counter()

    for raw in sorted(raw_stats.keys()):
        st = raw_stats[raw]
        top_cult = st["cultures"].most_common(1)[0][0] if st["cultures"] else "unknown"
        top_macro = resolve_macro(top_cult)
        dec = decode_ck3_personal_name(raw, culture=top_cult)
        cl = dec["clean_name"]
        cl_low = cl.lower()
        raw_low = raw.lower()

        # Hanzi semantic gloss lookup if present
        hanzi_glosses: list[dict[str, str]] = []
        if dec["hanzi_chars"]:
            for hz in dec["hanzi_chars"]:
                hz_entry = kanji_dict.get(hz)
                if isinstance(hz_entry, dict):
                    hanzi_glosses.append({
                        "char": hz,
                        "tarr": hz_entry.get("tarr") or hz_entry.get("tarr_morpheme") or "",
                        "meaning": hz_entry.get("meaning") or hz_entry.get("en") or "",
                    })
                else:
                    hanzi_glosses.append({"char": hz, "tarr": "", "meaning": ""})

        # Tiered adaptation lookup
        tarr_name = ""
        tarr_ipa = ""
        gender = "M"
        source_tier = "phonological_adaptation"
        canonical_ref: str | None = None

        # Tier 1: Official 239 name_list_franconian exact match
        f_match = franc_by_key_low.get(raw_low) or franc_by_key_low.get(cl_low) or franc_by_vanilla_low.get(cl_low)
        if f_match:
            tarr_name = f_match["tarr_name"]
            tarr_ipa = f_match["tarr_ipa"]
            gender = f_match["gender"]
            source_tier = "canonical_franconian_239"
            canonical_ref = f_match["ck3_key"]
        # Tier 2: Curated historical & high-frequency cross-cultural table
        elif cl_low in CURATED_BASE:
            tarr_name, tarr_ipa, gender = CURATED_BASE[cl_low]
            source_tier = "curated_historical_adaptation"
        # Tier 3: Expanded Chancellery register (Sections 3.4 & 5)
        elif cl_low in expanded:
            exp = expanded[cl_low]
            tarr_name = exp["tarr_name"]
            tarr_ipa = exp["tarr_ipa"]
            gender = exp["gender"] if exp["gender"] in ("M", "F") else "M"
            source_tier = exp["source_section"]
        else:
            # Tier 4: Algorithmic culture-aware adaptation across space/hyphen parts
            adapt_macro = (
                "sinosphere_sinitic"
                if dec["hanzi_chars"] and top_macro not in {"korean", "japonic"}
                else top_macro
            )
            parts = re.split(r"([ -])", cl)
            adapted_parts = [
                p if p in (" ", "-") else _adapt_single_token(p, adapt_macro)
                for p in parts
            ]
            tarr_name = "".join(adapted_parts).strip()
            tarr_name = _strip_disallowed_diacritics(tarr_name)
            tarr_ipa = approximate_ipa(tarr_name)
            if cl_low.endswith("a") and top_macro in {"romance", "germanic_west", "norse"}:
                gender = "F"
            elif cl_low.endswith(("hild", "hilt", "trud", "lind", "gard", "burg", "wynn", "gifu", "swith")):
                gender = "F"
            source_tier = "phonological_adaptation"

        # Guarantee strict Chancellery cleanliness even on curated outputs
        tarr_name = _strip_disallowed_diacritics(tarr_name)
        gen_stem, comp_prefix = build_genitive_and_prefix(tarr_name, gender=gender)
        tier_counts[source_tier] += 1

        cult_list = [c for c, _ in st["cultures"].most_common()]
        names_by_raw[raw] = {
            "raw_name": raw,
            "clean_name": cl,
            "hanzi_chars": dec["hanzi_chars"],
            "hanzi_glosses": hanzi_glosses or None,
            "homonym_index": dec["homonym_index"],
            "script_tag": dec["script_tag"],
            "tarr_name": tarr_name,
            "tarr_ipa": tarr_ipa,
            "tarr_genitive_stem": gen_stem,
            "tarr_compound_prefix": comp_prefix,
            "gender_hint": gender,
            "source_tier": source_tier,
            "canonical_ref": canonical_ref,
            "primary_culture": top_cult,
            "primary_macro_group": top_macro,
            "coinage_frequency": st["count"],
            "is_faith_saint": st["is_saint"],
            "saint_faiths": sorted(st["saint_faiths"]) if st["saint_faiths"] else None,
            "cultures": cult_list,
            "sample_baronies": st["sample_baronies"],
        }

        c_rec = clean_index.setdefault(cl, {
            "clean_name": cl,
            "primary_tarr_name": tarr_name,
            "primary_tarr_ipa": tarr_ipa,
            "tarr_genitive_stem": gen_stem,
            "tarr_compound_prefix": comp_prefix,
            "source_tier": source_tier,
            "raw_keys": [],
            "total_coinage_frequency": 0,
        })
        c_rec["raw_keys"].append(raw)
        c_rec["total_coinage_frequency"] += st["count"]

    # Enrich canonical_franconian entries with genitive stems too
    for v in franconian.values():
        g, p = build_genitive_and_prefix(v["tarr_name"], v["gender"])
        v["tarr_genitive_stem"] = g
        v["tarr_compound_prefix"] = p

    payload = {
        "metadata": {
            "schema_version": "1.0.0",
            "total_occupied_coinage_baronies": len(coinage),
            "unique_raw_names": len(names_by_raw),
            "unique_clean_names": len(clean_index),
            "hanzi_bearing_raw_names": sum(1 for v in names_by_raw.values() if v["hanzi_chars"]),
            "homonym_indexed_raw_names": sum(1 for v in names_by_raw.values() if v["homonym_index"] is not None),
            "faith_saint_raw_names": sum(1 for v in names_by_raw.values() if v["is_faith_saint"]),
            "canonical_franconian_239_count": len(franconian),
            "expanded_chancellery_register_count": len(expanded),
            "source_tier_counts": dict(tier_counts),
        },
        "ck3_decoder_rules": {
            "suffix_order": ["_(CN|JP|KO|KR|VN)", "_<homonym_digits>"],
            "hanzi_hex_escape": "_([0-9A-F]{4}) within CJK Unified/ExtA/Compat (U+3400..U+9FFF, U+F900..U+FAFF) extracted BEFORE accent substitution",
            "scandinavian_a_ring": "A__<lowercase> -> Å/å (A__sta -> Åsta, HA__kon -> Håkon, A__sa -> Åsa)",
            "word_space_double_underscore": "<UPPER>__<Word> splits to <UPPER>_ + space + <Word>",
            "uppercase_underscore_diacritics": {
                "A_": "Á/á", "E_": "É/é (or Æ/æ for Old English)", "I_": "Í/í",
                "O_": "Ó/ó (or Ö/ö, Ō/ō, Õ/õ)", "U_": "Ú/ú (or Ü/ü)",
                "Y_": "Ý/ý", "T_": "Þ/ð (or Ṭ/ṭ in Arabic/Berber)", "D_": "Ð/ð",
                "C_": "Č/č (or Ç/ç in Turkic)", "S_": "Š/š (or Ş/ş in Turkish)",
                "Z_": "Ž/ž", "L_": "Ł/ł", "N_": "Ń/ń (or Ṇ in Tocharian)",
                "G_": "Ğ/ğ", "H_": "Ḥ/ḥ", "R_": "Ř/ř",
            },
            "lowercase_underscore_rule": "Lowercase _ separates words (<word>_<Cap> -> space), Arabic inner 'ayn/hamza (-> '), or Korean/African syllables (-> -); NEVER accented.",
        },
        "chancellery_adaptation_laws": {
            "circumflex_purity": "All long/stressed vowels strictly use â, ê, î, ô, û; acute accents á, é, í, ó, ú and carons/cedillas/barred-l are converted.",
            "affricates": "Initial [ts] written z-; medial/final [ts] written -tz-/-tz; [tʃ] written tsch; [dʒ] written dsch.",
            "auslautverhartung": "Final -d -> -t, -b -> -p, -g -> -ch (except -ng), -v -> -f, -dsch -> -tsch.",
            "sinosphere_transcription": "12th-century Song/EMK/EMJ phonotactics: Pinyin zh -> dsch, q -> tsch, sh -> sch, initial c -> z; Japanese ts -> z-/-tz-, sh -> sch, j -> dsch.",
        },
        "canonical_franconian_239": franconian,
        "expanded_chancellery_register": expanded,
        "by_raw_name": names_by_raw,
        "by_clean_name": clean_index,
    }

    out_path = DATA_DIR / "global_onomasticon_adaptation.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"Wrote {out_path} ({out_path.stat().st_size / (1024*1024):.2f} MB)")
    print("Metadata:", json.dumps(payload["metadata"], indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Procedure 2 Title Updater
Applies the audited Toponym Adoption Pattern names to `tarraconian_titles_1059.md`:
- Pattern 1 (Tier 1): Semantic calques become primary official titles.
- Pattern 2 (Tier 2): Dual designations (primary phonetic or hybrid with authorized secondary calque).
- Pattern 3 (Tier 3): Strict phonetic nativizations (semantic calque relegated to parenthetical notes).
- Pattern 4 (Control): Pure phonetic adaptations preserved without calquing.
"""

import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TARR_MD_PATH = REPO_ROOT / "tarraconian_titles_1059.md"

REPLACEMENTS = [
    # =========================================================================
    # Pattern 1: Preferred Semantic Calques (Tier 1: High Living Continuity)
    # =========================================================================
    (
        r"  \* `c_abauj` \(\*\*\[HRE\]\*\* Abauj\) \$\\rightarrow\$ \*\*Magistrat van Abanûwenburch\*\* \*\(calque of \*Abaújvár\*\)\*",
        r"  * `c_abauj` (**[HRE]** Abauj) $\\rightarrow$ **Magistrat van Abanîeburch** *(calque of *Abaújvár* \"Aba's New Castle\", or **Abanûwenburch**)*"
    ),
    (
        r"  \* `c_bekes` \(Békés\) \$\\rightarrow\$ \*\*Magistrat van Bêkesch\*\*",
        r"  * `c_bekes` (Békés) $\\rightarrow$ **Magistrat van Fridstat** *(calque of *Békés* \"Peaceful Guard\", or **Bêkesch**)*"
    ),
    (
        r"  \* `c_soli` \(Soli\) \$\\rightarrow\$ \*\*Magistrat van Sôli\*\* \*\(or \*\*Saltzvelt\*\*, calque of Slavic \*Soli\* \"Salines\"\)\*",
        r"  * `c_soli` (Soli) $\\rightarrow$ **Magistrat van Saltzvelt** *(calque of Slavic *Soli* \"Salines\", or **Sôli**)*"
    ),
    (
        r"\| 34 \| \*\*Polotia\*\* \| `k_white_rus` \| \*\*Kûnincrich van Polôtzich\*\* \*\(or \*\*Wîtzrûssen\*\*\)\* \| `\[ˈpɔ\.lɔtsk\]` \| \*\*17/17 RE\*\* — Rus' \*Polotsk\* / calque \*Wîtzrûssen\* \(\"White Rus'\x22\)\. \|",
        r"| 34 | **Polotia** | `k_white_rus` | **Kûnincrich van Wîtzrûssen** *(or **Polôtzich**)* | `[ˈpɔ.lɔtsk]` | **17/17 RE** — Calque *Wîtzrûssen* (\"White Rus'\") / Rus' *Polotsk*. |"
    ),
    (
        r"### 3\.24 Kingdom of Polotia \(`k_white_rus`\) \$\\rightarrow\$ \*\*Kûnincrich van Polôtzich\*\*",
        r"### 3.24 Kingdom of Polotia (`k_white_rus`) $\\rightarrow$ **Kûnincrich van Wîtzrûssen** *(or **Polôtzich**)*"
    ),
    (
        r"  \* `c_babruysk` \(Babruiskas\) \$\\rightarrow\$ \*\*Magistrat van Babrûitzich\*\* \*\(or calqued \*\*Bîverbach\*\* from \*Babruyka\* \"Beaver River\", or sub-barony \*\*Rêtschitz\*\*\)\*",
        r"  * `c_babruysk` (Babruiskas) $\\rightarrow$ **Magistrat van Bîverbach** *(calque of *Babruyka* \"Beaver River\", or **Babrûitzich**, or sub-barony **Rêtschitz**)*"
    ),
    (
        r"  \* `c_pereyaslavl` \(\*\*\[HRE\]\*\* Pereyaslavl\) \$\\rightarrow\$ \*\*Magistrat van Perejaslouwe\*\*",
        r"  * `c_pereyaslavl` (**[HRE]** Pereyaslavl) $\\rightarrow$ **Magistrat van Rûmfurt** *(calque of Slavic *Pereyaslav* \"Seize/Cross Glory\", or **Perejaslouwe**)*"
    ),
    (
        r"  \* `c_calatayud` \(Calatayud\) \$\\rightarrow\$ \*\*Magistrat van Calatajût\*\* `\[ka\.la\.ta\.ˈjuːt\]` \*\(Attested Tarraconian county, promoted 1054\)\*",
        r"  * `c_calatayud` (Calatayud) $\\rightarrow$ **Magistrat van Calatajût** `[ka.la.ta.ˈjuːt]` *(or calqued **Eijûbsburch** from Arabic *Qal'at Ayyub* \"Job's Castle\"; attested Tarraconian county, promoted 1054)*"
    ),
    (
        r"  \* `c_albarracin` \(al-Banu Razin\) \$\\rightarrow\$ \*\*Magistrat van Albarrazîn\*\*",
        r"  * `c_albarracin` (al-Banu Razin) $\\rightarrow$ **Magistrat van Râsinburch** *(calque of Arabic *Hisn Ibn Razin*, or **Albarrazîn**)*"
    ),
    (
        r"  \* `c_algeciras` \(al-Gazirah al-Hadra\) \$\\rightarrow\$ \*\*Magistrat van Aldschesîres\*\* \*\(Old Catalan \*Algesires\*\)\*",
        r"  * `c_algeciras` (al-Gazirah al-Hadra) $\\rightarrow$ **Magistrat van Grûninsel** *(calque of Arabic *al-Jazīrah al-Khaḍrā'* \"Green Island\", or **Aldschesîres**)*"
    ),
    (
        r"  \* `c_sevilla` \(Isbiliyyah\) \$\\rightarrow\$ \*\*Magistrat van Sevîlje\*\*",
        r"  * `c_sevilla` (Isbiliyyah) $\\rightarrow$ **Magistrat van Grôzwazzer** *(calque of Arabic *al-Wādī al-Kabīr* \"Great River\" / Guadalquivir, or **Sevîlje**)*"
    ),
    (
        r"  \* `c_caceres` \(hisn Qasras\) \$\\rightarrow\$ \*\*Magistrat van Kâtzeres\*\*",
        r"  * `c_caceres` (hisn Qasras) $\\rightarrow$ **Magistrat van der Brücke** *(calque of Arabic *al-Qanṭarah* \"The Bridge\" / Alcántara, or **Kâtzeres**)*"
    ),
    (
        r"  \* `c_santiago` \(Yant Yaqub\) \$\\rightarrow\$ \*\*Magistrat van Zant-Jâcop\*\* \*\(MHG \*Sant Jâcob\* \+ Catalan \*Sant Jaume\* for Compostela\)\*",
        r"  * `c_santiago` (Yant Yaqub) $\\rightarrow$ **Magistrat van Zant-Jâcop** *(MHG *Sant Jâcob* + Catalan *Sant Jaume* for Compostela; or calqued **Altbrücke** for Pontevedra)*"
    ),
    (
        r"  \* `c_albi` \(Albi\) \$\\rightarrow\$ \*\*Magistrat van Albî\*\*",
        r"  * `c_albi` (Albi) $\\rightarrow$ **Magistrat van Albî** *(or calqued **Nîecastel** for Castelnaudary)*"
    ),
    (
        r"  \* `c_forcalquier` \(Forcalquier\) \$\\rightarrow\$ \*\*Magistrat van Forkalkêr\*\*",
        r"  * `c_forcalquier` (Forcalquier) $\\rightarrow$ **Magistrat van Kalkovens** *(calque of Latin *Furnus Calcarius*, or **Forkalkêr**)*"
    ),
    (
        r"  \* `c_jerusalem` \(\*\*\[HRE\]\*\* Jerusalem\) \$\\rightarrow\$ \*\*Magistrat van Jerûsalem\*\*",
        r"  * `c_jerusalem` (**[HRE]** Jerusalem) $\\rightarrow$ **Magistrat van Hiligstat** *(calque of Arabic *al-Quds* \"Holy Sanctuary\", or **Jerûsalem**)*"
    ),
    (
        r"  \* `c_ghazza` \(\*\*\[HRE\]\*\* Ghazza\) \$\\rightarrow\$ \*\*Magistrat van Gâse\*\* \(`\[1122 Historical: Magistrat van Askalôn\]`\)",
        r"  * `c_ghazza` (**[HRE]** Ghazza) $\\rightarrow$ **Magistrat van Gâse** (`[1122 Historical: Magistrat van Askalôn; or calqued Magistrat van dem Dôden Sê for Bahr Lut]`)"
    ),
    (
        r"  \* `c_baalbek` \(\*\*\[HRE\]\*\* Baalbek\) \$\\rightarrow\$ \*\*Magistrat van Bâlbech\*\* \(`\[1122 Historical: Magistrat van Heljôpel\]`\)",
        r"  * `c_baalbek` (**[HRE]** Baalbek) $\\rightarrow$ **Magistrat van Bâlbech** (`[1122 Historical: Magistrat van Heljôpel; or calqued Ritterburch for Hisn al-Akrad]`)"
    ),
    (
        r"  \* `c_cairo` \(Cairo\) \$\\rightarrow\$ \*\*Magistrat van Kaîre\*\* \*\(or \*\*Fustât\*\*\)\*",
        r"  * `c_cairo` (Cairo) $\\rightarrow$ **Magistrat van Sêgestat** *(calque of Arabic *al-Qāhirah* \"Victorious\", or **Kaîre / Fustât**)*"
    ),
    (
        r"  \* `c_kalliopolis` \(\*\*\[HRE\]\*\* Kallipolis\) \$\\rightarrow\$ \*\*Magistrat van Kallîpel\*\*",
        r"  * `c_kalliopolis` (**[HRE]** Kallipolis) $\\rightarrow$ **Magistrat van Schönstat** *(calque of Greek *Kallipolis* \"Beautiful City\", or **Kallîpel**)*"
    ),
    (
        r"  \* `c_serres` \(Serres\) \$\\rightarrow\$ \*\*Magistrat van Sêrres\*\*",
        r"  * `c_serres` (Serres) $\\rightarrow$ **Magistrat van Goltstat** *(calque of Greek *Chrysopolis* \"Golden City\", or **Sêrres**)*"
    ),
    (
        r"  \* `c_euboea` \(\*\*\[HRE\]\*\* Euboea\) \$\\rightarrow\$ \*\*Magistrat van Euböe\*\* \(`\[1122 Historical: Magistrat van Negropont\]`\)",
        r"  * `c_euboea` (**[HRE]** Euboea) $\\rightarrow$ **Magistrat van Koperstat** *(calque of Greek *Chalkis* \"Copper City\", or **Euböe**; `[1122 Historical: Magistrat van Negropont]`)*"
    ),
    (
        r"  \* `c_theodosiopolis` \(\*\*\[HRE\]\*\* Theodosiopolis\) \$\\rightarrow\$ \*\*Magistrat van Theodosiôpel\*\* \(`\[1142 Historical: Magistrat van Karîn\]`\)",
        r"  * `c_theodosiopolis` (**[HRE]** Theodosiopolis) $\\rightarrow$ **Magistrat van Leuwenburch** *(calque of Byzantine *Leontokastron* \"Lion Castle\", or **Theodosiôpel**; `[1142 Historical: Magistrat van Karîn]`)*"
    ),
    (
        r"  \* `c_severin` \(\*\*\[HRE\]\*\* Severin\) \$\\rightarrow\$ \*\*Magistrat van Sewerîn\*\*",
        r"  * `c_severin` (**[HRE]** Severin) $\\rightarrow$ **Magistrat van dem Îsentôr** *(calque of *Vaskapu* \"Iron Gate\", or **Sewerîn**)*"
    ),
    (
        r"  \* `c_dublin` \(\*\*\[HRE\]\*\* Dublin\) \$\\rightarrow\$ \*\*Magistrat van Dublîn\*\*",
        r"  * `c_dublin` (**[HRE]** Dublin) $\\rightarrow$ **Magistrat van Swartzpûl** *(calque of Old Irish *Dubh Linn* \"Black Pool\", or **Dublîn**; or calqued **Eichenkirchen** for Kildare)*"
    ),
    (
        r"  \* `c_mearns` \(\*\*\[HRE\]\*\* Mearns\) \$\\rightarrow\$ \*\*Magistrat van Mêrns\*\*",
        r"  * `c_mearns` (**[HRE]** Mearns) $\\rightarrow$ **Magistrat van Dônmunde** *(calque of *Aberdeen* \"Don Mouth\", or **Mêrns**)*"
    ),
    (
        r"  \* `c_inverness` \(\*\*\[HRE\]\*\* Inverness\) \$\\rightarrow\$ \*\*Magistrat van Inwernes\*\*",
        r"  * `c_inverness` (**[HRE]** Inverness) $\\rightarrow$ **Magistrat van Nessmunde** *(calque of Gaelic *Inbhir Nis* \"Ness Mouth\", or **Inwernes**)*"
    ),
    (
        r"\| 145 \| \*\*Maryül\*\* \| `k_maryul` \| \*\*Kûnincrich van Maryül\*\* \| \*Maryülisch\* \| \*\*0/16 RE\*\* — Added in 1154 Imperial Chancellery update\. \|",
        r"| 145 | **Maryül** | `k_maryul` | **Kûnincrich van Niderlant** *(or **Maryül**)* | *Niderlantisch* | **0/16 RE** — Added in 1154 Imperial Chancellery update; calque of Tibetan *Mar-yul*. |"
    ),
    (
        r"### 3\.145 Kingdom of Maryül \(`k_maryul`\) \$\\rightarrow\$ \*\*Kûnincrich van Maryül\*\*",
        r"### 3.145 Kingdom of Maryül (`k_maryul`) $\\rightarrow$ **Kûnincrich van Niderlant** *(or **Maryül**)*"
    ),
    (
        r"\* \*\*Duchy of Baltiyül\*\* \(`d_baltiyul`\) \$\\rightarrow\$ \*\*Gubernat van Balti-Jül\*\*",
        r"* **Duchy of Baltiyül** (`d_baltiyul`) $\\rightarrow$ **Gubernat van Baltilant** *(or **Balti-Jül**)*"
    ),
    (
        r"\* \*\*Duchy of Lhoyul\*\* \(`d_lhoyul`\) \$\\rightarrow\$ \*\*Gubernat van Lho-Jül\*\*",
        r"* **Duchy of Lhoyul** (`d_lhoyul`) $\\rightarrow$ **Gubernat van Sûtlant** *(or **Lho-Jül**)*"
    ),
    (
        r"\* \*\*Duchy of Dzayül\*\* \(`d_dzayul`\) \$\\rightarrow\$ \*\*Gubernat van Dza-Jül\*\*",
        r"* **Duchy of Dzayül** (`d_dzayul`) $\\rightarrow$ **Gubernat van Dzalant** *(or **Dza-Jül**)*"
    ),
    (
        r"\| 136 \| \*\*Guannei\*\* \| `k_guannei` \| \*\*Kûnincrich van Guannei\*\* \| \*Guanneiisch\* \| \*\*0/23 RE\*\* — Added in 1154 Imperial Chancellery update\. \|",
        r"| 136 | **Guannei** | `k_guannei` | **Kûnincrich van Binnenklûsen** *(or **Guannei**)* | *Binnenklûsisch* | **0/23 RE** — Added in 1154 Imperial Chancellery update; calque of Chinese *Guānnèi*. |"
    ),
    (
        r"### 3\.136 Kingdom of Guannei \(`k_guannei`\) \$\\rightarrow\$ \*\*Kûnincrich van Guannei\*\*",
        r"### 3.136 Kingdom of Guannei (`k_guannei`) $\\rightarrow$ **Kûnincrich van Binnenklûsen** *(or **Guannei**)*"
    ),
    (
        r"  \* `c_seogyeong` \(\*\*\[HRE\]\*\* Seogyeong\) \$\\rightarrow\$ \*\*Magistrat van Seogyeong\*\*",
        r"  * `c_seogyeong` (**[HRE]** Seogyeong) $\\rightarrow$ **Magistrat van Ebeneveit** *(calque of Sino-Korean *Pyeongyang* \"Flat Ground\", or **Seogyeong**)*"
    ),
    (
        r"  \* `c_tamna` \(\*\*\[HRE\]\*\* Tamna\) \$\\rightarrow\$ \*\*Magistrat van Tamne\*\*",
        r"  * `c_tamna` (**[HRE]** Tamna) $\\rightarrow$ **Magistrat van der Övergouwe** *(calque of Sino-Korean *Jeju* \"Province Across Water\", or **Tamne**)*"
    ),
    (
        r"  \* `c_myeongju` \(\*\*\[HRE\]\*\* Myeongju\) \$\\rightarrow\$ \*\*Magistrat van Myeongdschu\*\*",
        r"  * `c_myeongju` (**[HRE]** Myeongju) $\\rightarrow$ **Magistrat van Flôzbrunn** *(calque of Sino-Korean *Gangwon* \"River Springs\", or **Myeongdschu**)*"
    ),
    (
        r"  \* `c_gyeongju` \(\*\*\[HRE\]\*\* Gyeongju\) \$\\rightarrow\$ \*\*Magistrat van Gyeongdschu\*\*",
        r"  * `c_gyeongju` (**[HRE]** Gyeongju) $\\rightarrow$ **Magistrat van Fröudengouwe** *(calque of Sino-Korean *Gyeongju* \"Joy District\", or **Gyeongdschu**)*"
    ),
    (
        r"  \* `c_cheongju` \(\*\*\[HRE\]\*\* Cheongju\) \$\\rightarrow\$ \*\*Magistrat van Tscheongdschu\*\*",
        r"  * `c_cheongju` (**[HRE]** Cheongju) $\\rightarrow$ **Magistrat van dem Klârgouwe** *(calque of Sino-Korean *Cheongju* \"Clear River District\", or **Tscheongdschu**)*"
    ),
    (
        r"  \* `c_namwon` \(\*\*\[HRE\]\*\* Namwon\) \$\\rightarrow\$ \*\*Magistrat van Namwon\*\*",
        r"  * `c_namwon` (**[HRE]** Namwon) $\\rightarrow$ **Magistrat van Sûtvelt** *(calque of Sino-Korean *Namwon* \"South Plain\", or **Namwon**)*"
    ),
    (
        r"  \* `c_echigo` \(\*\*\[HRE\]\*\* Echigo\) \$\\rightarrow\$ \*\*Magistrat van Etschigô\*\*",
        r"  * `c_echigo` (**[HRE]** Echigo) $\\rightarrow$ **Magistrat van Hinder-dem-Klûs** *(calque of Japanese *Echigo* \"Behind the Pass\", or **Etschigô**)*"
    ),
    (
        r"  \* `c_echizen` \(\*\*\[HRE\]\*\* Echizen\) \$\\rightarrow\$ \*\*Magistrat van Etschizen\*\*",
        r"  * `c_echizen` (**[HRE]** Echizen) $\\rightarrow$ **Magistrat van Vör-dem-Klûs** *(calque of Japanese *Echizen* \"Before the Pass\", or **Etschizen**)*"
    ),
    (
        r"  \* `c_musashi` \(\*\*\[HRE\]\*\* Musashi\) \$\\rightarrow\$ \*\*Magistrat van Musaschi\*\*",
        r"  * `c_musashi` (**[HRE]** Musashi) $\\rightarrow$ **Magistrat van der Ôst-Hôfstat** *(calque of *Tokyo* \"Eastern Capital\", or **Musaschi**)*"
    ),
    (
        r"  \* `c_hizen` \(\*\*\[HRE\]\*\* Hizen\) \$\\rightarrow\$ \*\*Magistrat van Hizen\*\*",
        r"  * `c_hizen` (**[HRE]** Hizen) $\\rightarrow$ **Magistrat van Langengecke** *(calque of *Nagasaki* \"Long Cape\", or **Hizen**)*"
    ),
    (
        r"  \* `c_qingshan` \(\*\*\[HRE\]\*\* Qingshan\) \$\\rightarrow\$ \*\*Magistrat van Tschingschan\*\*",
        r"  * `c_qingshan` (**[HRE]** Qingshan) $\\rightarrow$ **Magistrat van Grûnenberch** *(calque of Chinese *Qingshan* \"Green Mountain\", or **Tschingschan**)*"
    ),
    (
        r"  \* `c_yongxing` \(\*\*\[HRE\]\*\* Yongxing\) \$\\rightarrow\$ \*\*Magistrat van Jongsching\*\*",
        r"  * `c_yongxing` (**[HRE]** Yongxing) $\\rightarrow$ **Magistrat van Êwiger-Fröude** *(calque of Chinese *Yongxing* \"Eternal Prosperity\", or **Jongsching**)*"
    ),
    (
        r"  \* `c_datong_2` \(\*\*\[HRE\]\*\* Datong\) \$\\rightarrow\$ \*\*Magistrat van Datong\*\*",
        r"  * `c_datong_2` (**[HRE]** Datong) $\\rightarrow$ **Magistrat van Grôzem-Vride** *(calque of Chinese *Datong* \"Great Unity\", or **Datong**)*"
    ),
    (
        r"  \* `c_huaian` \(\*\*\[HRE\]\*\* Huai'an\) \$\\rightarrow\$ \*\*Magistrat van Huai-An\*\*",
        r"  * `c_huaian` (**[HRE]** Huai'an) $\\rightarrow$ **Magistrat van Fridhold** *(calque of Chinese *Huai'an* \"Embracing Peace\", or **Huai-An**)*"
    ),
    (
        r"  \* `c_boseong` \(\*\*\[HRE\]\*\* Boseong\) \$\\rightarrow\$ \*\*Magistrat van Boseong\*\*",
        r"  * `c_boseong` (**[HRE]** Boseong) $\\rightarrow$ **Magistrat van dem Edelsteinburch** *(calque of Sino-Korean *Boseong* \"Treasure Castle\", or **Boseong**)*"
    ),
    (
        r"  \* `c_otrar` \(\[Non-HRE\] Otrar\) \$\\rightarrow\$ \*\*Magistrat van Otrar\*\*",
        r"  * `c_otrar` ([Non-HRE] Otrar) $\\rightarrow$ **Magistrat van dem Rôtsant** *(calque of Turkic *Kyzylkum* \"Red Sand\", or **Otrar**)*"
    ),
    (
        r"  \* `c_bukhara` \(Bukhara\) \$\\rightarrow\$ \*\*Magistrat van Buchâre\*\*",
        r"  * `c_bukhara` (Bukhara) $\\rightarrow$ **Magistrat van dem Swartzensê** *(calque of Turkic *Karakul* \"Black Lake\", or **Buchâre**)*"
    ),
    (
        r"  \* `c_aksu` \(\*\*\[HRE\]\*\* Aksu\) \$\\rightarrow\$ \*\*Magistrat van Aksu\*\*",
        r"  * `c_aksu` (**[HRE]** Aksu) $\\rightarrow$ **Magistrat van dem Wîzenflôz** *(calque of Turkic *Ak Su* \"White Water\", or **Aksu**)*"
    ),
    (
        r"  \* `c_yangikent` \(\*\*\[HRE\]\*\* Yangikent\) \$\\rightarrow\$ \*\*Magistrat van Jangikent\*\*",
        r"  * `c_yangikent` (**[HRE]** Yangikent) $\\rightarrow$ **Magistrat van Nîestat** *(calque of Turkic *Yangi Kent* \"New City\", or **Jangikent**)*"
    ),
    (
        r"  \* `c_tun` \(\*\*\[HRE\]\*\* Tun\) \$\\rightarrow\$ \*\*Magistrat van Tûn\*\*",
        r"  * `c_tun` (**[HRE]** Tun) $\\rightarrow$ **Magistrat van dem Berchlant** *(calque of Persian *Kuhistan* \"Mountain Land\", or **Tûn**)*"
    ),
    (
        r"  \* `c_vestisland` \(Vestrland\) \$\\rightarrow\$ \*\*Magistrat van West-Îslant\*\*",
        r"  * `c_vestisland` (Vestrland) $\\rightarrow$ **Magistrat van West-Îslant** *(or calqued **Wîzflôz** for Hvítársíða)*"
    ),
    (
        r"  \* `c_austisland` \(Austrland\) \$\\rightarrow\$ \*\*Magistrat van Ôst-Îslant\*\*",
        r"  * `c_austisland` (Austrland) $\\rightarrow$ **Magistrat van Ôst-Îslant** *(or calqued **Swartzberch** for Svartafell / **Rôtbucht** for Reyðarfjörður)*"
    ),
    (
        r"  \* `c_tavasts` \(\*\*\[HRE\]\*\* Tavasts\) \$\\rightarrow\$ \*\*Magistrat van Tawastlant\*\* \(`\[1142 Historical: Magistrat van Wanâje\]`\)",
        r"  * `c_tavasts` (**[HRE]** Tavasts) $\\rightarrow$ **Magistrat van Tawastlant** (`[1142 Historical: Magistrat van Wanâje; or calqued Wîzenstrûz for Valkeakoski]`)"
    ),
    (
        r"  \* `c_saratov` \(Saratau\) \$\\rightarrow\$ \*\*Magistrat van Saratau\*\*",
        r"  * `c_saratov` (Saratau) $\\rightarrow$ **Magistrat van dem Goltberch** *(calque of Turkic *Sary Tau* \"Yellow Mountain\", or **Saratau**)*"
    ),
    (
        r"  \* `c_showa` \(\*\*\[HRE\]\*\* Showa\) \$\\rightarrow\$ \*\*Magistrat van Schôwe\*\*",
        r"  * `c_showa` (**[HRE]** Showa) $\\rightarrow$ **Magistrat van dem Liechtberch** *(calque of Ge'ez *Debre Birhan* \"Mountain of Light\", or **Schôwe**)*"
    ),
    (
        r"  \* `c_begemder` \(\*\*\[HRE\]\*\* Begemder\) \$\\rightarrow\$ \*\*Magistrat van Bêgemder\*\*",
        r"  * `c_begemder` (**[HRE]** Begemder) $\\rightarrow$ **Magistrat van dem Tâborberch** *(calque of *Debre Tabor* \"Mount Tabor\", or **Bêgemder**)*"
    ),
    (
        r"  \* `c_gojjam` \(\*\*\[HRE\]\*\* Gojjam\) \$\\rightarrow\$ \*\*Magistrat van Godschâm\*\*",
        r"  * `c_gojjam` (**[HRE]** Gojjam) $\\rightarrow$ **Magistrat van der Sêouwe** *(calque of Amharic *Bahir Dar* \"Sea Shore\", or **Godschâm**)*"
    ),
    (
        r"  \* `c_hobyo` \(\*\*\[HRE\]\*\* Hobyo\) \$\\rightarrow\$ \*\*Magistrat van Hôbje\*\*",
        r"  * `c_hobyo` (**[HRE]** Hobyo) $\\rightarrow$ **Magistrat van dem Berchbrunn** *(calque of Somali *Ceelbuur* \"Well of the Hill\", or **Hôbje**)*"
    ),
    (
        r"  \* `c_ras_hafun` \(\*\*\[HRE\]\*\* Ras Hafun\) \$\\rightarrow\$ \*\*Magistrat van Râs-Hafûn\*\* \(`\[1142 Historical: Magistrat van Opône\]`\)",
        r"  * `c_ras_hafun` (**[HRE]** Ras Hafun) $\\rightarrow$ **Magistrat van dem Ôsthoubt** *(calque of Arabic *Ras Asir* \"Eastern Cape\", or **Râs-Hafûn**; `[1142 Historical: Magistrat van Opône]`)*"
    ),
    (
        r"  \* `c_mansura` \(Mansura\) \$\\rightarrow\$ \*\*Magistrat van Mansûre\*\*",
        r"  * `c_mansura` (Mansura) $\\rightarrow$ **Magistrat van Mansûre** *(or calqued **Hôhburch** for Kot Diji)*"
    ),

    # =========================================================================
    # Pattern 2: Hybrid Calque Allowed (Tier 2: Transitional Dynastic Rule)
    # =========================================================================
    (
        r"  \* `c_novgorod` \(Novgorod\) \$\\rightarrow\$ \*\*Magistrat van Nougarden\*\*",
        r"  * `c_novgorod` (Novgorod) $\\rightarrow$ **Magistrat van Nîenburch** *(or **Nougarden**)*"
    ),
    (
        r"  \* `c_lviv` \(Lemberg\) \$\\rightarrow\$ \*\*Magistrat van Lewenburch\*\* `\[ˈlɛ\.wən\.bʊrx\]` \(`\[1059 Historical Default: Magistrat van Swenigorot \(Zvenyhorod\) / Busk — Cadet House: Chatenois-Swenigorot\]`\)",
        r"  * `c_lviv` (Lemberg) $\\rightarrow$ **Magistrat van Klingeburch** *(or **Lüwenburch / Lewenburch**; `[1059 Historical Default: Magistrat van Swenigorot (Zvenyhorod) / Busk — Cadet House: Chatenois-Swenigorot]`)*"
    ),
    (
        r"  \* `c_volodymyr` \(Volodymyr\) \$\\rightarrow\$ \*\*Magistrat van Simne\*\* \*\(or \*\*Lûge\*\*\)\*",
        r"  * `c_volodymyr` (Volodymyr) $\\rightarrow$ **Magistrat van Simne-an-der-Lûge** *(or **Simne / Lûge**)*"
    ),
    (
        r"  \* `c_breifne` \(\*\*\[HRE\]\*\* Breifne\) \$\\rightarrow\$ \*\*Magistrat van Brêfne\*\*",
        r"  * `c_breifne` (**[HRE]** Breifne) $\\rightarrow$ **Magistrat van Grôzkirchen** *(calque of *Kilmore*, or **Kilmôr / Brêfne**)*"
    ),
    (
        r"  \* `c_sarykamysh` \(\*\*\[HRE\]\*\* Sarykamysh\) \$\\rightarrow\$ \*\*Magistrat van Sarikamîsch\*\*",
        r"  * `c_sarykamysh` (**[HRE]** Sarykamysh) $\\rightarrow$ **Magistrat van dem Gelwen Riete** *(or **Gelbriet / Sarikamîsch**; or calqued **Wîzenbrunn** for Akbulak)*"
    ),
    (
        r"  \* `c_memel` \(\*\*\[HRE\]\*\* Memel\) \$\\rightarrow\$ \*\*Magistrat van Memel\*\*",
        r"  * `c_memel` (**[HRE]** Memel) $\\rightarrow$ **Magistrat van der Swartzenouwe** *(calque of *Juodkrantė*, or **Swartzküste / Mêmel**)*"
    ),
    (
        r"  \* `c_amhara` \(\*\*\[HRE\]\*\* Amhara\) \$\\rightarrow\$ \*\*Magistrat van Amhâre\*\*",
        r"  * `c_amhara` (**[HRE]** Amhara) $\\rightarrow$ **Magistrat van der Felsburch** *(calque of *Amba Sel*, or **Ambâsel / Amhâre**)*"
    ),

    # =========================================================================
    # Pattern 3: Strict Phonetic Nativization (Tier 3: Complete Semantic Rupture)
    # =========================================================================
    (
        r"  \* `c_vas` \(\*\*\[HRE\]\*\* Dudleb\) \$\\rightarrow\$ \*\*Magistrat van Îsenburch\*\* \*\(for \*Vasvár\*, or \*\*Teindorf / Dudlêben\*\*, attested Tarraconian county promoted 1051\)\*",
        r"  * `c_vas` (**[HRE]** Dudleb) $\\rightarrow$ **Magistrat van Teindorf** *(or **Dudlêben**; or calqued **Îsenburch** for *Vasvár*; attested Tarraconian county promoted 1051)*"
    ),
    (
        r"  \* `c_spis` \(\*\*\[HRE\]\*\* Szepesség\) \$\\rightarrow\$ \*\*Magistrat van Zips\*\* `\[tsɪps\]` \*\(Attested Tarraconian county, promoted 1052\)\*",
        r"  * `c_spis` (**[HRE]** Szepesség) $\\rightarrow$ **Magistrat van der Zips** `[tsɪps]` *(or **Zips**; calqued **Tschingouwe**; attested Tarraconian county, promoted 1052)*"
    ),
    (
        r"  \* `c_marmaros` \(Marmaros\) \$\\rightarrow\$ \*\*Magistrat van Marmarosch\*\* \(`\[1059 Historical: Magistrat van Saltzburch-an-der-Tîsse \(Solotvyno\)\]`\)",
        r"  * `c_marmaros` (Marmaros) $\\rightarrow$ **Magistrat van Marmarôsch** (`[1059 Historical: Magistrat van Saltzburch-an-der-Tîsse (Solotvyno); or calqued Salzstat-am-Teiß]`)"
    ),
    (
        r"  \* `c_kiev` \(\*\*\[HRE\]\*\* Kyiv\) \$\\rightarrow\$ \*\*Magistrat van Kîouwe\*\*",
        r"  * `c_kiev` (**[HRE]** Kyiv) $\\rightarrow$ **Magistrat van Kîouwe** *(or calqued **Hôchburch** for Vyshhorod)*"
    ),
    (
        r"  \* `c_beloozero` \(Beloozero\) \$\\rightarrow\$ \*\*Magistrat van Wîtzensê\*\* \*\(calque of \*Beloozero\* \"White Lake\", or \*\*Belosêr\*\*\)\*",
        r"  * `c_beloozero` (Beloozero) $\\rightarrow$ **Magistrat van Belosêr** *(or calqued **Wîtzensê** from *Beloozero* \"White Lake\")*"
    ),
    (
        r"  \* `c_zelengora` \(Zelengora\) \$\\rightarrow\$ \*\*Magistrat van Grûnenberch\*\* \*\(calque of \*Zelengora\* \"Green Mountain\", or \*\*Selengôre\*\*\)\*",
        r"  * `c_zelengora` (Zelengora) $\\rightarrow$ **Magistrat van Selengôre** *(or calqued **Grûnenberch** from *Zelengora* \"Green Mountain\")*"
    ),
    (
        r"  \* `c_pomorje` \(\*\*\[HRE\]\*\* Pomorje\) \$\\rightarrow\$ \*\*Magistrat van Sêmarch\*\* \*\(calque of \*Pomorje\* \"Seacoast\", or \*\*Antivâri\*\*\)\*",
        r"  * `c_pomorje` (**[HRE]** Pomorje) $\\rightarrow$ **Magistrat van Pomôrje** *(or calqued **Sêmarch** from *Pomorje* \"Seacoast\", or **Antivâri**)*"
    ),
    (
        r"  \* `c_zachlumia` \(Zachlumia\) \$\\rightarrow\$ \*\*Magistrat van Chulm\*\*",
        r"  * `c_zachlumia` (Zachlumia) $\\rightarrow$ **Magistrat van Chulm** *(or calqued **Brückenstat** for Mostar)*"
    ),
    (
        r"  \* `c_duklja` \(\*\*\[HRE\]\*\* Duklja\) \$\\rightarrow\$ \*\*Magistrat van Dioklêe\*\* \*\(or \*\*Skutâri\*\*\)\*",
        r"  * `c_duklja` (**[HRE]** Duklja) $\\rightarrow$ **Magistrat van Dioklêe** *(or **Skutâri**; calqued **Swartzberch** for Crna Gora)*"
    ),
    (
        r"  \* `c_suzdal` \(\*\*\[HRE\]\*\* Suzdal\) \$\\rightarrow\$ \*\*Magistrat van Sûsdal\*\*",
        r"  * `c_suzdal` (**[HRE]** Suzdal) $\\rightarrow$ **Magistrat van Sûsdal** *(or calqued **Veldlant** for Opolye)*"
    ),
    (
        r"  \* `c_kerak` \(\*\*\[HRE\]\*\* Kerak\) \$\\rightarrow\$ \*\*Magistrat van Pêtre\*\* \(`\[1122 Historical: Magistrat van Pêtre\]`\)",
        r"  * `c_kerak` (**[HRE]** Kerak) $\\rightarrow$ **Magistrat van Pêtre** (`[1122 Historical: Magistrat van Pêtre; or Krach; calqued Felsenstat]`)"
    ),
    (
        r"  \* `c_negev` \(\*\*\[HRE\]\*\* Negev\) \$\\rightarrow\$ \*\*Magistrat van Arabâ\*\* \(`\[1122 Historical: Magistrat van Arabâ\]`\)",
        r"  * `c_negev` (**[HRE]** Negev) $\\rightarrow$ **Magistrat van Arabâ** (`[1122 Historical: Magistrat van Arabâ; or calqued Dalsencke / Sivenbrunn for Beersheba]`)"
    ),
    (
        r"  \* `c_denbighshire` \(Perfeddwlad\) \$\\rightarrow\$ \*\*Magistrat van Middenlant\*\* \*\(calque of Welsh \*Perfeddwlad\*, or \*\*Pervetwlat\*\*\)\*",
        r"  * `c_denbighshire` (Perfeddwlad) $\\rightarrow$ **Magistrat van Pervetwlat** *(or calqued **Middenlant** from Welsh *Perfeddwlad* \"Middle Country\")*"
    ),
    (
        r"\* \*\*Duchy of Boyül\*\* \(`d_boyul`\) \$\\rightarrow\$ \*\*Gubernat van Bo-Jül\*\*",
        r"* **Duchy of Boyül** (`d_boyul`) $\\rightarrow$ **Gubernat van Bo-Jül** *(or calqued **Powolant**)*"
    ),
    (
        r"  \* `c_cangzhou` \(\[Non-HRE\] Cangzhou\) \$\\rightarrow\$ \*\*Magistrat van Zangdschou\*\*",
        r"  * `c_cangzhou` ([Non-HRE] Cangzhou) $\\rightarrow$ **Magistrat van Zangdschou** *(or calqued **Ôverflôz** for Hebei)*"
    ),
    (
        r"  \* `c_kucha` \(\*\*\[HRE\]\*\* Kucha\) \$\\rightarrow\$ \*\*Magistrat van Kutsche\*\*",
        r"  * `c_kucha` (**[HRE]** Kucha) $\\rightarrow$ **Magistrat van Kutsche** *(or calqued **Westfrid** for Anxi)*"
    ),
    (
        r"  \* `c_gilan` \(\*\*\[HRE\]\*\* Gilan\) \$\\rightarrow\$ \*\*Magistrat van Gilân\*\*",
        r"  * `c_gilan` (**[HRE]** Gilan) $\\rightarrow$ **Magistrat van Gilân** *(or calqued **Wîzenflôz** for Sefidrud)*"
    ),
    (
        r"  \* `c_rudbar` \(\*\*\[HRE\]\*\* Rudbar\) \$\\rightarrow\$ \*\*Magistrat van Rudbâr\*\*",
        r"  * `c_rudbar` (**[HRE]** Rudbar) $\\rightarrow$ **Magistrat van Rudbâr** *(or calqued **Flôzouwe**)*"
    ),
    (
        r"  \* `c_mustasaari` \(\*\*\[HRE\]\*\* Mustasaari\) \$\\rightarrow\$ \*\*Magistrat van Mustasâri\*\* \(`\[1142 Historical: Magistrat van Lewänlûchte\]`\)",
        r"  * `c_mustasaari` (**[HRE]** Mustasaari) $\\rightarrow$ **Magistrat van Mustasâri** (`[1142 Historical: Magistrat van Lewänlûchte; or calqued Swartzinsel]`)"
    ),
    (
        r"  \* `c_oulu` \(\*\*\[HRE\]\*\* Oulu\) \$\\rightarrow\$ \*\*Magistrat van Oulû\*\*",
        r"  * `c_oulu` (**[HRE]** Oulu) $\\rightarrow$ **Magistrat van Oulû** *(or calqued **Flôzmunde** for Oulujoki / **Grôzensê** for Kemijärvi)*"
    ),
    (
        r"  \* `c_ranikot` \(\*\*\[HRE\]\*\* Ranikot\) \$\\rightarrow\$ \*\*Magistrat van Ranikôt\*\* \(`\[1142 Historical: Magistrat van Scharusân\]`\)",
        r"  * `c_ranikot` (**[HRE]** Ranikot) $\\rightarrow$ **Magistrat van Ranikôt** (`[1142 Historical: Magistrat van Scharusân; or calqued Kûnincsburch]`)"
    ),
    (
        r"  \* `c_kasmira` \(\*\*\[HRE\]\*\* Kasmira\) \$\\rightarrow\$ \*\*Magistrat van Kasmire\*\*",
        r"  * `c_kasmira` (**[HRE]** Kasmira) $\\rightarrow$ **Magistrat van Kasmire** *(or calqued **Saffîrdal** for Neelam / **Geistsê** for Manasbal)*"
    )
]

def apply_updates():
    with open(TARR_MD_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    total = len(REPLACEMENTS)
    applied = 0
    for pattern, replacement in REPLACEMENTS:
        new_content, count = re.subn(pattern, replacement, content)
        if count > 0:
            applied += 1
            content = new_content
        else:
            print(f"[WARN] Pattern did not match: {pattern[:60]}...")

    with open(TARR_MD_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"[SUCCESS] Applied {applied} / {total} Procedure 2 title updates to {TARR_MD_PATH.name}!")
    return applied == total

if __name__ == "__main__":
    success = apply_updates()
    sys.exit(0 if success else 1)

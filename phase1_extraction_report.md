# Phase 1 Extraction Report: Landed Titles, Dynasties & Historical Canon

* **Extraction Date:** 2026-11-04 07:04:20
* **Output Directory:** `/tmp/ck3_audit_phase1`

## 1. Executive Summary & Core Statistics

| Metric | Extracted Count | Description |
| :--- | :---: | :--- |
| **De Jure Counties Processed** | **2793** | Total counties mapped from vanilla landed titles hierarchy |
| **Counties in Roman Empire** | **1499** (53.7%) | Counties whose de facto top liege is `h_roman_empire` / `e_hre` |
| **Active Cultures** | **388** | Extracted from `culture_manager` with ethos, language & heritage |
| **Dynasties & Cadet Houses** | **25537** dynasties / **27169** houses | Total noble lineages recorded in save gamestate |
| **Chatenois Cadet Houses** | **50** | Branches of Dynasty 1582 evaluated for Germanic rename |
| **Historical Characters Decoded** | **61286** | Title holders, history conquerors, and house heads with personality traits |
| **Mapped Built Baronies** | **8757** | Baronies with province holdings, buildings, and fort levels |

## 2. Culture Distribution in the Empire

Top 15 cultures across counties inside the Roman Empire:

| Culture | Counties Count | Percentage |
| :--- | :---: | :---: |
| **Tarraconian** | 742 | 49.5% |
| **levantine** | 46 | 3.1% |
| **butr** | 30 | 2.0% |
| **norwegian** | 27 | 1.8% |
| **bedouin** | 26 | 1.7% |
| **greek** | 25 | 1.7% |
| **swedish** | 25 | 1.7% |
| **sami** | 18 | 1.2% |
| **somali** | 18 | 1.2% |
| **Armeno-Greek** | 15 | 1.0% |
| **Perso-Greek** | 15 | 1.0% |
| **Croato-Tarraconian** | 14 | 0.9% |
| **Russo-Lithuanian** | 14 | 0.9% |
| **ethiopian** | 14 | 0.9% |
| **franconian** | 13 | 0.9% |

## 3. Chatenois Dynasty Germanic Adjustment

As detailed in [chatenois_dynasty_analysis.md](chatenois_dynasty_analysis.md), the ruling dynasty **Chatenois** (ID `1582`) derives from Latin *Castinetum* ('chestnut grove'). In historical German / Lorraine tradition and Tarraconian sound laws, the name is **Kestenholz**.

Key cadet branches adjusted:
* `Chatenois-Metz` $\rightarrow$ **`Kestenholz-Metz`** (1322 living members, Head: Wernhard `67256089`)
* `Chatenois-Saumur` $\rightarrow$ **`Kestenholz-Saumur`** (98 living members, Head: Poppo `194813`)
* `Chatenois-Ravenna` $\rightarrow$ **`Kestenholz-Ravenna`** (69 living members, Head: Thietmar `219528`)
* `dynn_Bluome` $\rightarrow$ **`Kestenholz (dynn_Bluome)`** (63 living members, Head: Thomas `16954461`)
* `Chatenois-Annonay` $\rightarrow$ **`Kestenholz-Annonay`** (59 living members, Head: Ansgar `33668348`)
* `Chatenois-Fécamp` $\rightarrow$ **`Kestenholz-Fécamp`** (59 living members, Head: Rudolf `198300`)
* `Chatenois-Albret` $\rightarrow$ **`Kestenholz-Albret`** (52 living members, Head: Udalrich `67279763`)
* `Flanders` $\rightarrow$ **`Kestenholz (Flanders)`** (45 living members, Head: Sofie `16985947`)

## 4. Generated Artifacts & File Inventory

* `titles_data.json`: Complete county-level dictionary with history, baronies, development, and liege chains.
* `counties_summary.csv`: Tabular spreadsheet of all counties for rapid screening and analysis.
* `dynasties_and_houses.json` & `dynasties_and_houses.csv`: Full register of dynasties, houses, living member counts, and proposed renames.
* `cultures_data.json`: Full culture definitions including hybrid parentage, ethos, language, and traditions.
* `historical_characters.json`: Character records with decoded traits ready for Option C personality engine.
* `chatenois_dynasty_analysis.json` & `.md`: Dedicated linguistic adaptation for House Chatenois $\rightarrow$ Kestenholz.

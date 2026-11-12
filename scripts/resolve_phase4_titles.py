#!/usr/bin/env python3
"""
Phase 4: Title Resolution, Reconciliation & Dynasty Extraction Pipeline
Part of the Tarraconian Historical Accuracy Audit Pipeline.

This script executes Phase 4 of the audit plan:
1. Finalizes the definitive historical resolution for all 150 flagged titles (Option A, Option B, or Option C).
2. Applies Tarraconian sound laws (Rhine-Moselle Franconian MHG + Old Catalan) to formulate official Chancellery titles and adjectives.
3. Systematically couples each of the 50 cadet branches of Dynasty 1582 (House Kestenholz) to its underlying seat and updates chatenois_dynasty_analysis.md.
4. Generates the comprehensive audit_discrepancy_register.md in the git repository workspace.
5. Writes machine-readable resolution tables to /var/tmp/ck3_audit/phase4/.
"""

import argparse
import csv
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Import the coupling dictionary from screen_phase3_titles
from screen_phase3_titles import CADET_BRANCH_COUPLINGS, HISTORICAL_TITLE_DB, NON_CHATENOIS_HOUSE_REALIGNMENTS

# Dynamic Emergent Culture Realignments (The Toponym-First Principle)
DYNAMIC_CULTURE_REALIGNMENTS = {
    275: {
        "culture_id": 275,
        "current_name": "Galațian",
        "current_collective": "Galațian-Vlachs",
        "current_prefix": "Galațian",
        "heritage": "heritage_vlach",
        "language": "language_wallachian",
        "created": "924.8.8",
        "underlying_origin_seat": "c_galati",
        "underlying_seat_name": "Galați (1445 AD)",
        "resolved_toponym": "Dinogetia",
        "resolved_toponym_detail": "Roman/Late Antique fortress Dinogetia (Bisericuța-Garvăn)",
        "realigned_name": "Dinogetian-Vlachs",
        "realigned_collective": "Dinogetian-Vlachs",
        "realigned_prefix": "Dinogeto-",
        "tarraconian_culture_name": "Dinogetjanen",
        "status": "Realigned to Roman Fortress",
        "historical_justification": "Galați is an anachronistic 1445 foundation. Under the Toponym-First Principle, the title resolves to pre-867 Roman fortress Dinogetia on the Danube, realigning the dynamic Vlach culture to Dinogetian-Vlachs."
    },
    288: {
        "culture_id": 288,
        "current_name": "Bugeacian",
        "current_collective": "Bugeacian-Vlachs",
        "current_prefix": "Bugeacian",
        "heritage": "heritage_vlach",
        "language": "language_wallachian",
        "created": "951.8.8",
        "underlying_origin_seat": "c_bugeac",
        "underlying_seat_name": "Bugeac / Budjak (16th c.)",
        "resolved_toponym": "River Tyras (Nistru)",
        "resolved_toponym_detail": "Classical river hydronym Tyras (Greek Τύρας / Latin Tyras)",
        "realigned_name": "Tyrasian-Vlachs",
        "realigned_collective": "Tyrasian-Vlachs",
        "realigned_prefix": "Tyraso-",
        "tarraconian_culture_name": "Tîrasjanen",
        "status": "Realigned to Classical Hydronym",
        "historical_justification": "Budjak/Bugeac is a 16th-century Ottoman Turkish administrative term. Realigned to the authentic pre-867 classical river hydronym Tyras."
    },
    293: {
        "culture_id": 293,
        "current_name": "Bugeacian-Mogyër",
        "current_collective": "Bugeacian-Mogyërs",
        "current_prefix": "Bugeacian-Mogyëro",
        "heritage": "heritage_magyar",
        "language": "language_wallachian",
        "created": "956.11.10",
        "underlying_origin_seat": "c_bugeac",
        "underlying_seat_name": "Bugeac / Budjak (16th c.)",
        "resolved_toponym": "River Tyras (Nistru)",
        "resolved_toponym_detail": "Classical river hydronym Tyras (Greek Τύρας / Latin Tyras)",
        "realigned_name": "Tyrasian-Mogyër",
        "realigned_collective": "Tyrasian-Mogyërs",
        "realigned_prefix": "Tyraso-Mogyëro",
        "tarraconian_culture_name": "Tîrasisch-Mogyër",
        "status": "Realigned to Classical Hydronym",
        "historical_justification": "Dynamic hybrid between Magyars and local Vlachs in the Budjak steppe. Realigned from the Ottoman exonym to the classical hydronym Tyras."
    },
    286: {
        "culture_id": 286,
        "current_name": "Wolkensteiner",
        "current_collective": "Wolkensteiner-Polabians",
        "current_prefix": "Wolkensteiner",
        "heritage": "heritage_west_slavic",
        "language": "language_lechitic",
        "created": "948.8.26",
        "underlying_origin_seat": "c_wolkenstein",
        "underlying_seat_name": "Wolkenstein (Burg c. 1200)",
        "resolved_toponym": "River Zschopau / Miriquidi",
        "resolved_toponym_detail": "Ancient Slavic hydronym Zschopau (Čopa) and Miriquidi forest",
        "realigned_name": "Zschopauer",
        "realigned_collective": "Zschopauer-Polabians",
        "realigned_prefix": "Zschopau-",
        "tarraconian_culture_name": "Tschopouwer",
        "status": "Realigned to Ancient Hydronym",
        "historical_justification": "Burg Wolkenstein is a High Medieval foundation (c. 1200). Pre-867 Polabian Slavic settlement on the Zschopau river in the Miriquidi forest realigns the ethnonym to Zschopauer."
    },
    260: {
        "culture_id": 260,
        "current_name": "Jutribocian",
        "current_collective": "Jutribocian-Polabians",
        "current_prefix": "Jutribocian",
        "heritage": "heritage_west_slavic",
        "language": "language_lechitic",
        "created": "900.8.26",
        "underlying_origin_seat": "c_juterbog",
        "underlying_seat_name": "Jüterbog / Jutriboc (1007 AD)",
        "resolved_toponym": "Pagus Nicici",
        "resolved_toponym_detail": "Slavic tribal territory Nicici (attested 844 AD in Geographus Bavarus)",
        "realigned_name": "Nicipsian",
        "realigned_collective": "Nicipsian-Polabians",
        "realigned_prefix": "Nicipso-",
        "tarraconian_culture_name": "Nikitzen",
        "status": "Realigned to Pre-867 Tribal Pagus",
        "historical_justification": "Jüterbog/Jutriboc first appears in 1007. The authentic pre-867 Polabian tribal pagus recorded in the Bavarian Geographer (844) was the Nizici/Nicici, realigning the culture to Nicipsian."
    },
    358: {
        "culture_id": 358,
        "current_name": "South Kazanskayan",
        "current_collective": "South Kazanskayan-Khazars",
        "current_prefix": "South Kazanskayan",
        "heritage": "heritage_turkic",
        "language": "language_oghur",
        "created": "1083.7.18",
        "underlying_origin_seat": "c_kazanskaya",
        "underlying_seat_name": "Kazanskaya (Stanitsa 1647)",
        "resolved_toponym": "River Tanais (Don)",
        "resolved_toponym_detail": "Classical river Tanais (Don) / Magistrat van Middel-Dôn",
        "realigned_name": "Tanaite-Turkic",
        "realigned_collective": "Tanaite-Khazars",
        "realigned_prefix": "Tanaito-",
        "tarraconian_culture_name": "Tanaîten (Don-Oghur)",
        "status": "Realigned to Classical Hydronym",
        "historical_justification": "Kazanskaya was a 1647 Don Cossack stanitsa. Tsarist Russia never conquered the steppe in this campaign. Realigned from the resolved title Middel-Dôn to Tanaite-Turkic."
    },
    331: {
        "culture_id": 331,
        "current_name": "Putyvlian",
        "current_collective": "Putyvlian-Russians",
        "current_prefix": "Putyvlian",
        "heritage": "heritage_east_slavic",
        "language": "language_east_slavic",
        "created": "1018.3.9",
        "underlying_origin_seat": "c_putyvl",
        "underlying_seat_name": "Putyvl (1146 AD)",
        "resolved_toponym": "River Sem (Seim) / Severians",
        "resolved_toponym_detail": "Pre-867 hydronym Sem and Severian tribal territory (Severjane)",
        "realigned_name": "Semian-Severians",
        "realigned_collective": "Semian-Severians",
        "realigned_prefix": "Semiano-",
        "tarraconian_culture_name": "Sêmjanen",
        "status": "Realigned to Ancient Hydronym & Tribe",
        "historical_justification": "Putyvl is an 11th/12th-century foundation (first chronicle record 1146). Realigned to the ancient hydronym Sem (Seim) and Severian ethnonym."
    },
    270: {
        "culture_id": 270,
        "current_name": "Pereyaslavian",
        "current_collective": "Pereyaslavian-Russians",
        "current_prefix": "Pereyaslavian",
        "heritage": "heritage_east_slavic",
        "language": "language_east_slavic",
        "created": "916.3.9",
        "underlying_origin_seat": "c_pereyaslavl",
        "underlying_seat_name": "Pereyaslavl (992 AD)",
        "resolved_toponym": "River Trubizh",
        "resolved_toponym_detail": "Pre-867 hydronym Trubizh and Severo-Polian borderland",
        "realigned_name": "Trubezhan-Slavs",
        "realigned_collective": "Trubezhan-Slavs",
        "realigned_prefix": "Trubezho-",
        "tarraconian_culture_name": "Trubeschjanen",
        "status": "Realigned to Ancient Hydronym",
        "historical_justification": "Pereyaslavl was founded in 992 AD by Vladimir the Great. Pre-867 population along the Trubizh river realigns to Trubezhan-Slavs."
    },
    338: {
        "culture_id": 338,
        "current_name": "Burgasan",
        "current_collective": "Burgasan-Greeks",
        "current_prefix": "Burgasan",
        "heritage": "heritage_byzantine",
        "language": "language_slavonic",
        "created": "1045.2.1",
        "underlying_origin_seat": "c_burgas",
        "underlying_seat_name": "Burgas (17th c.)",
        "resolved_toponym": "Deultum (Debeltos)",
        "resolved_toponym_detail": "Roman colonia Deultum (Colonia Flavia Pacis Deultensium)",
        "realigned_name": "Deultian",
        "realigned_collective": "Deultian-Greeks",
        "realigned_prefix": "Deulto-",
        "tarraconian_culture_name": "Deultener",
        "status": "Realigned to Roman Colonia",
        "historical_justification": "Burgas is an Ottoman/early modern settlement. The ancient pre-867 Roman colonia and bishopric is Deultum (Debeltos), realigning the culture to Deultian."
    },
    279: {
        "culture_id": 279,
        "current_name": "Frontenhausian",
        "current_collective": "Frontenhausian-Bavarians",
        "current_prefix": "Frontenhausian",
        "heritage": "heritage_central_germanic",
        "language": "language_high_german",
        "created": "935.2.11",
        "underlying_origin_seat": "c_frontenhausen",
        "underlying_seat_name": "Frantenhusa (788 AD)",
        "resolved_toponym": "Frantenhusa",
        "resolved_toponym_detail": "Attested 788 AD in Breves Notitiae of Salzburg",
        "realigned_name": "Frontenhausian",
        "realigned_collective": "Frontenhausian-Bavarians",
        "realigned_prefix": "Frontenhuso-",
        "tarraconian_culture_name": "Frontenhûser",
        "status": "Validated Pre-867 Historical",
        "historical_justification": "Frontenhausen is attested in 788 AD as Frantenhusa, confirming authentic pre-867 antiquity. Retained with Tarraconian phonological normalization."
    },
    367: {
        "culture_id": 367,
        "current_name": "Ungwârer",
        "current_collective": "Ungwârer-Tarracono-Lothringian",
        "current_prefix": "Ungwârer",
        "heritage": "heritage_central_germanic",
        "language": "language_magyar",
        "created": "1093.11.13",
        "underlying_origin_seat": "c_ungvar",
        "underlying_seat_name": "Ungvár (Castrum Hung)",
        "resolved_toponym": "River Ung",
        "resolved_toponym_detail": "Ancient hydronym Ung (Uzh), origin of ethnonym Ungari",
        "realigned_name": "Ungwârer",
        "realigned_collective": "Ungwârer-Tarraconians",
        "realigned_prefix": "Ungwâro-",
        "tarraconian_culture_name": "Ungwârer",
        "status": "Validated Pre-867 Hydronym",
        "historical_justification": "Ungvár derives from the ancient river Ung, attested in 9th-century sources (Castrum Hung). Validated as authentic pre-867 hydronym."
    },
    303: {
        "culture_id": 303,
        "current_name": "Schmalkalder",
        "current_collective": "Schmalkalder-Franconians",
        "current_prefix": "Schmalkalder",
        "heritage": "heritage_central_germanic",
        "language": "language_high_german",
        "created": "966.2.9",
        "underlying_origin_seat": "c_schmalkalden",
        "underlying_seat_name": "Smalcalda (874 AD)",
        "resolved_toponym": "River Smalcalda",
        "resolved_toponym_detail": "Pre-867 Germanic hydronym Smalcalda ('narrow water')",
        "realigned_name": "Schmalkalder",
        "realigned_collective": "Schmalkalder-Franconians",
        "realigned_prefix": "Smalcaldo-",
        "tarraconian_culture_name": "Smalcalder",
        "status": "Validated Pre-867 Hydronym",
        "historical_justification": "Schmalkalden derives from an ancient Germanic hydronym Smalcalda. Validated as authentic pre-867 hydronym."
    }
}


def run_phase4(phase1_dir, phase3_dir, output_dir, repo_dir):
    print("[Phase 4] Loading Phase 1 and Phase 3 data...")
    with open(Path(phase3_dir) / "title_screening_matrix.json", "r", encoding="utf-8") as f:
        screening_matrix = json.load(f)

    with open(Path(phase1_dir) / "chatenois_dynasty_analysis.json", "r", encoding="utf-8") as f:
        dynasty_data = json.load(f)

    with open(Path(phase1_dir) / "titles_data.json", "r", encoding="utf-8") as f:
        titles_data = json.load(f)

    # Load optional English title lookup & Sinosphere Section 5 DB so save names and calques never regress
    eng_cache = {}
    eng_cache_path = Path("/var/tmp/ck3_audit/english_titles_cache.json")
    if eng_cache_path.is_file():
        with open(eng_cache_path, "r", encoding="utf-8") as f:
            eng_cache = json.load(f)

    sino_names = {}
    sino_gaz_path = Path(repo_dir) / "sinosphere_titles_and_characters_1154.md"
    if sino_gaz_path.is_file():
        with open(sino_gaz_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("|") and "`c_" in line:
                    parts = line.split("|")
                    if len(parts) >= 6:
                        km = re.search(r"`(c_[^`]+)`", parts[2])
                        if km:
                            sino_names[km.group(1)] = (parts[3].replace("**", "").strip(), parts[4].replace("**", "").strip())

    try:
        from prepare_section5_update import section5_db
    except Exception:
        section5_db = {}

    def _sino_adj(tarr_str: str) -> str:
        stem = tarr_str.replace("Magistrat van ", "").strip()
        if stem.startswith("dem "):
            stem = stem[4:]
        return f"{stem[:-1]}er" if stem.endswith("e") else f"{stem}er"

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # 1. Process Final Title Resolutions
    final_resolutions = []
    for item in screening_matrix:
        ck = item["county_key"]
        rec = item["definitive_recommendation"]
        opt_a = item["option_a"]
        opt_b = item["option_b"]
        opt_c = item["option_c"]
        coupling = item["cadet_branch_coupling"]

        save_name = item["save_name"]
        if not save_name or save_name == ck:
            save_name = eng_cache.get(ck, save_name or ck)

        sel_opt = rec["selected_option"]
        res_name = opt_a["candidate_name"] if sel_opt == "Option A" else opt_b["toponymic_stem"]
        res_key = opt_a["candidate_key"] if sel_opt == "Option A" else opt_b["hydronym"]
        tarr_title = rec["tarraconian_chancellery_name"]
        tarr_adj = rec["tarraconian_adjective"]
        hist_just = rec["historical_justification"]

        # Apply curated Harmonized Sinospheric Calque Paradigm (61 titles from Section 5)
        if ck in section5_db:
            opt_b_s5, tarr_s5, note_s5 = section5_db[ck]
            basin_en, chars = opt_b_s5.rsplit(" (", 1)
            eng_s5, ch_s5 = sino_names.get(ck, (save_name, ""))
            save_name = f"{eng_s5} ({ch_s5})" if ch_s5 else eng_s5
            sel_opt = "Option B"
            res_key = basin_en
            res_name = "(" + chars
            tarr_title = tarr_s5
            tarr_adj = _sino_adj(tarr_s5)
            hist_just = note_s5

        res_entry = {
            "county_key": ck,
            "save_name": save_name,
            "kingdom": item["kingdom"],
            "duchy": item["duchy"],
            "tier": item["tier"],
            "tier_reason": item["tier_reason"],
            "selected_option": sel_opt,
            "resolved_name": res_name,
            "resolved_key": res_key,
            "tarraconian_title": tarr_title,
            "tarraconian_adjective": tarr_adj,
            "historical_justification": hist_just,
            "cadet_branch_coupled": coupling["coupled"],
            "cadet_house_id": coupling["cadet_house_id"],
            "cadet_realigned_name": coupling["realigned_name"],
            "is_sinosphere_s5": ck in section5_db,
        }
        final_resolutions.append(res_entry)

    # Export machine-readable title resolutions
    res_json = out_path / "final_title_resolutions.json"
    with open(res_json, "w", encoding="utf-8") as f:
        json.dump(final_resolutions, f, indent=2, ensure_ascii=False)
    print(f"[Phase 4] Wrote title resolutions JSON to {res_json}")

    res_csv = out_path / "final_title_resolutions.csv"
    with open(res_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "county_key", "save_name", "kingdom", "duchy", "tier",
            "tier_reason", "selected_option", "resolved_name", "resolved_key",
            "tarraconian_title", "tarraconian_adjective", "historical_justification",
            "cadet_coupled", "cadet_realigned_name"
        ])
        for r in final_resolutions:
            writer.writerow([
                r["county_key"], r["save_name"], r["kingdom"], r["duchy"], r["tier"],
                r["tier_reason"], r["selected_option"], r["resolved_name"], r["resolved_key"],
                r["tarraconian_title"], r["tarraconian_adjective"], r["historical_justification"],
                r["cadet_branch_coupled"], r["cadet_realigned_name"] or "None"
            ])
    print(f"[Phase 4] Wrote title resolutions CSV to {res_csv}")

    # 2. Process Full 50-House Cadet Branch Register
    cadet_branches = dynasty_data.get("cadet_branches", [])
    dynasty_rename_register = []

    for b in cadet_branches:
        hid = b["house_id"]
        current_display = b["current_display_name"]
        baseline = b["proposed_tarraconian_name"]
        members = b["living_members_count"]
        head_name = b["head_name"]
        head_id = b["head_id"]

        # Check coupling
        if hid in CADET_BRANCH_COUPLINGS:
            c_info = CADET_BRANCH_COUPLINGS[hid]
            realigned = c_info["realigned_name"]
            seat = c_info["seat_origin"]
            reason = c_info["coupling_reason"]
            status = "Realigned to Resolved Pre-867 Seat"
        else:
            realigned = baseline
            seat = "Authentic / Uncoupled"
            reason = "House name stem normalized to Kestenholz; seat does not require realignment."
            status = "Stem Normalized"

        dyn_entry = {
            "house_id": hid,
            "current_name": current_display,
            "phase1_baseline_name": baseline,
            "final_realigned_name": realigned,
            "underlying_seat": seat,
            "head_name": head_name,
            "head_id": head_id,
            "living_members": members,
            "status": status,
            "coupling_justification": reason
        }
        dynasty_rename_register.append(dyn_entry)

    # Sort cadet register by living members descending
    dynasty_rename_register.sort(key=lambda x: x["living_members"], reverse=True)

    dyn_json = out_path / "dynasty_cadet_rename_register.json"
    with open(dyn_json, "w", encoding="utf-8") as f:
        json.dump(dynasty_rename_register, f, indent=2, ensure_ascii=False)
    print(f"[Phase 4] Wrote dynasty rename JSON to {dyn_json}")

    dyn_csv = out_path / "dynasty_cadet_rename_register.csv"
    with open(dyn_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "house_id", "current_name", "phase1_baseline_name", "final_realigned_name",
            "underlying_seat", "head_name", "head_id", "living_members", "status", "coupling_justification"
        ])
        for d in dynasty_rename_register:
            writer.writerow([
                d["house_id"], d["current_name"], d["phase1_baseline_name"], d["final_realigned_name"],
                d["underlying_seat"], d["head_name"], d["head_id"], d["living_members"], d["status"], d["coupling_justification"]
            ])
    print(f"[Phase 4] Wrote dynasty rename CSV to {dyn_csv}")

    # 3. Process Dynamic Emergent Culture Rename Register
    dynamic_cultures_list = list(DYNAMIC_CULTURE_REALIGNMENTS.values())
    dynamic_cultures_list.sort(key=lambda x: x["culture_id"])

    cult_json = out_path / "dynamic_cultures_to_rename.json"
    with open(cult_json, "w", encoding="utf-8") as f:
        json.dump(dynamic_cultures_list, f, indent=2, ensure_ascii=False)
    print(f"[Phase 4] Wrote dynamic cultures rename JSON to {cult_json}")

    cult_csv = out_path / "dynamic_cultures_to_rename.csv"
    with open(cult_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "culture_id", "current_name", "created", "heritage", "language",
            "underlying_origin_seat", "underlying_seat_name", "resolved_toponym",
            "realigned_name", "realigned_collective", "realigned_prefix",
            "tarraconian_culture_name", "status", "historical_justification"
        ])
        for c in dynamic_cultures_list:
            writer.writerow([
                c["culture_id"], c["current_name"], c["created"], c["heritage"], c["language"],
                c["underlying_origin_seat"], c["underlying_seat_name"], c["resolved_toponym"],
                c["realigned_name"], c["realigned_collective"], c["realigned_prefix"],
                c["tarraconian_culture_name"], c["status"], c["historical_justification"]
            ])
    print(f"[Phase 4] Wrote dynamic cultures rename CSV to {cult_csv}")

    # 4. Generate Workspace Deliverable: audit_discrepancy_register.md
    discrepancy_file = Path(repo_dir) / "audit_discrepancy_register.md"
    generate_audit_discrepancy_register(final_resolutions, dynasty_rename_register, dynamic_cultures_list, discrepancy_file)
    print(f"[Phase 4] Wrote audit discrepancy register to {discrepancy_file}")

    # 5. Generate Master Workspace Deliverable: dynastic_realignment_register.md
    dynasty_register_file = Path(repo_dir) / "dynastic_realignment_register.md"
    dynasty_register_csv = Path(output_dir) / "dynasty_historical_realignment_register.csv"
    generate_dynasty_historical_realignment_register(dynasty_rename_register, NON_CHATENOIS_HOUSE_REALIGNMENTS, dynamic_cultures_list, dynasty_register_file, dynasty_register_csv)
    print(f"[Phase 4] Wrote master dynastic realignment register to {dynasty_register_file}")

    # 6. Update Chatenois Dynasty Analysis
    chatenois_doc = Path(phase1_dir) / "chatenois_dynasty_analysis.md"
    try:
        update_chatenois_dynasty_analysis(dynasty_rename_register, chatenois_doc)
        print(f"[Phase 4] Wrote updated Chatenois dynasty analysis to {chatenois_doc}")
    except OSError:
        alt_doc = Path(output_dir) / "chatenois_dynasty_analysis.md"
        update_chatenois_dynasty_analysis(dynasty_rename_register, alt_doc)
        print(f"[Phase 4] Wrote updated Chatenois dynasty analysis to {alt_doc}")


def generate_audit_discrepancy_register(titles, houses, cultures, report_file):
    total_titles = len(titles)
    tier2_count = sum(1 for t in titles if t["tier"] == 2)
    tier3_count = sum(1 for t in titles if t["tier"] == 3)
    opt_a_count = sum(1 for t in titles if t["selected_option"] == "Option A")
    opt_b_count = sum(1 for t in titles if t["selected_option"] == "Option B")
    coupled_houses = [h for h in houses if "Realigned" in h["status"]]

    sino_count = sum(1 for t in titles if t.get("is_sinosphere_s5"))
    lines = [
        "# Audit Discrepancy Register: Historical Accuracy & Title Resolutions",
        "",
        "* **Campaign Date:** 18 June 1171 (`chatenois_867_01_01.ck3`)",
        f"* **Audit Scope:** **{total_titles} Flagged Imperial Counties** across **{len(set(t['kingdom'] for t in titles))} De Jure Kingdoms**",
        "* **Core Framework:** 867 Alternate-History Divergence Point → Colonizer Presence Audit → Toponym-First Principle → Sub-Barony / Hydronymic Hierarchy → Tarraconian Chancellery Sound Laws",
        "",
        "---",
        "",
        "## 1. Executive Summary & Resolution Metrics",
        "",
        "> [!NOTE]",
        "> **Harmonized Calque Paradigm for Logographic Sinospheric Titles:**",
        f"> For the {sino_count} flagged titles within the Sinosphere (East Asia / Mandate of Heaven perimeter), post-867 foundations are predominantly logographic Chinese character compositions (`汉字` / *Hànzì*) rather than feudal eponymous castles. Under this harmonized paradigm:",
        "> 1. Each title's territorial jurisdiction is anchored to its authentic pre-867 physical river basin, mountain pass, or lacustrine catchment (Option B: e.g. *Yitong River / Songhua Basin*, *Daling River*, *Shira Muren*, *Mudan River*, *Xiao Pass*).",
        "> 2. The official Tarraconian Chancellery title is formed by directly calquing the semantic ideographs into Tarraconian (e.g., `长春` \"Eternal Spring\" $\\rightarrow$ **`Magistrat van Langlenten`**; `大定` \"Great Settlement\" $\\rightarrow$ **`Magistrat van Grôzfest`**; `安边` \"Pacified Frontier\" $\\rightarrow$ **`Magistrat van Fridmarch`**), completely resolving the feudal causal paradox while preserving authentic Sinitic statecraft semantics.",
        "",
        "This register constitutes the definitive, finalized reconciliation of all landed titles inside the **Roman Empire** (`h_roman_empire`) evaluated under the **Three-Tier Classification System**: Tier 2 (Post-867 Hydronymic, Geographic, or Tribal Foundations audited for pre-HRE morphology) and Tier 3 (Other Post-867 Settlements resolved via Options A, B, or C). Every title is paired with its verified pre-867 settlement or hydronym, along with official Tarraconian Chancellery forms and adjectives.",
        "",
        "Under the **Toponym-First Principle & Downstream Causality Inversion Rule** (Section 3.3 of the Audit Plan), landed titles possess absolute primacy. Cadet branches of the imperial dynasty and emergent dynamic cultures adapt *from* the historically resolved titles, completely eliminating circular canonization of anachronisms.",
        "",
        "| Audit Category | Total Titles / Entities | Percentage | Resolution Strategy |",
        "| :--- | :---: | :---: | :--- |",
        f"| **Total Flagged Imperial Titles** | **{total_titles}** | **100.0%** | Full reconciliation against 867 campaign divergence |",
        f"| • **Tier 2: Post-867 Hydronymic / Geographic / Tribal** | **{tier2_count}** | {tier2_count/total_titles*100:.1f}% | Pre-HRE native morphology restored (stripping colonial suffixes) before Tarraconian adaptation |",
        f"| • **Tier 3: Other Settlements Founded After 867** | **{tier3_count}** | {tier3_count/total_titles*100:.1f}% | Dynastic castles, eponymous foundations, descriptive outposts, or unverified titles resolved via Options A/B/C |",
        f"| **Option A: Pre-867 Sub-Barony Centers** | **{opt_a_count}** | {opt_a_count/total_titles*100:.1f}% | Anchored to attested ancient oppida, castra, civitates, or collegiate abbeys |",
        f"| **Option B: Ancient Hydronyms / Oronyms** | **{opt_b_count}** | {opt_b_count/total_titles*100:.1f}% | Resolved via river/mountain basins applying Section 3.1 Hydronym Hierarchy |",
        f"| **Coupled Cadet Houses of House Kestenholz** | **{len(coupled_houses)}** | — | Toponymic seat suffixes updated to match resolved pre-867 centres |",
        f"| **Realigned Dynamic Emergent Cultures** | **{len(cultures)}** | — | Dynamic culture ethnonyms realigned to resolved pre-867 centres |",
        "",
        "---",
        "",
        "## 2. Cadet Branch Realignment Coupling Summary",
        "",
        "In accordance with Section 4 of the audit plan, cadet houses belonging to the imperial dynasty (*Dat Hûs van Kestenholz*, Dynasty `1582`) have had their toponymic seat suffixes coupled to their resolved historical pre-867 centers:",
        "",
        "| House ID | Original Save Name | Phase 1 Baseline | Resolved Seat Origin | Final Tarraconian House Name | Living Members | Historical Resolution Justification |",
        "| :---: | :--- | :--- | :--- | :--- | :---: | :--- |",
    ]

    for h in coupled_houses:
        lines.append(
            f"| `{h['house_id']}` | **{h['current_name']}** | `{h['phase1_baseline_name']}` | `{h['underlying_seat']}` | **{h['final_realigned_name']}** | {h['living_members']} | {h['coupling_justification']} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 3. Dynamic Emergent Culture Rename Register",
        "",
        "Under the **Toponym-First Principle**, dynamic divergent and hybrid cultures formed during the campaign whose vanilla/save names derived from post-867 anachronistic foundations have been systematically realigned to the resolved historical toponyms of their ethnogenesis seats:",
        "",
        "| Culture ID | Old In-Game Name | Divergence Date | Underlying Origin Seat | Resolved Historical Toponym | Final Realigned Culture Name | Realigned Collective Noun | Tarraconian Culture Name | Status & Historical Justification |",
        "| :---: | :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- |",
    ])

    for c in cultures:
        lines.append(
            f"| `{c['culture_id']}` | **{c['current_name']}** | {c['created']} | `{c['underlying_origin_seat']}` ({c['underlying_seat_name']}) | **{c['resolved_toponym']}** | **{c['realigned_name']}** | *{c['realigned_collective']}* | `{c['tarraconian_culture_name']}` | **{c['status']}:** {c['historical_justification']} |"
        )

    lines.extend([
        "",
        "---",
        "",
        f"## 4. Master Title Discrepancy & Resolution Register ({total_titles} Imperial Counties)",
        "",
        "| County Key | Current Save Name | De Jure Kingdom | Tier | Discrepancy / Mismatch Reason | Final Historical Resolution | Official Tarraconian Chancellery Title | Official Adjective | Historical & Etymological Justification |",
        "| :--- | :--- | :--- | :---: | :--- | :--- | :--- | :--- | :--- |",
    ])

    for t in titles:
        ck = t["county_key"]
        sn = t["save_name"]
        k = t["kingdom"]
        tier = f"Tier {t['tier']}"
        reason = t["tier_reason"]
        res_str = (
            f"**{t['selected_option']}:** `{t['resolved_key']}` {t['resolved_name']}"
            if t.get("is_sinosphere_s5")
            else f"**{t['selected_option']}:** `{t['resolved_key']}` ({t['resolved_name']})"
        )
        tarr_title = t["tarraconian_title"]
        tarr_adj = t["tarraconian_adjective"]
        just = t["historical_justification"]

        lines.append(f"| `{ck}` | **{sn}** | {k} | **{tier}** | {reason} | {res_str} | **{tarr_title}** | *{tarr_adj}* | {just} |")

    lines.extend([
        "",
        "---",
        "",
        "## 5. Linguistic Adaptation & Sound Law Implementation",
        "",
        "All titles and adjectives conform to the **Romano-Germanic synthesis** of the Tarraconian Imperial Chancellery (`language_high_german`, `heritage_central_germanic`):",
        "1. **Chancellery Formulae:** Every county is titled **Magistrat van ...** (courtly Romance variant: *Veguerîe van ...*).",
        "2. **Phonological Sound Laws:**",
        "   * Preservation of unshifted initial `k-` (*Kesten-*, *Kulm*, *Kaiserswerth*).",
        "   * Preservation of Middle High German affricate `-z` `[ts]` (*-holz*, *Zant-*, *Zutphen*).",
        "   * Retaining long vowels with circumflex notation (*î*, *û*, *ê*, *ô*).",
        "3. **Adjectival Suffixation:** Derivation using authentic Franconian `-er` (e.g. *Freisinger*, *Windischer*, *Trusower*, *Twangstisch*, *Alnensisch*, *Uisnecher*).",
        "",
        "---",
        "",
        "## 6. Transition to Phase 5: Documentation Update & Mod Recompilation",
        "",
        "The resolutions in this register are ready for direct injection into mod configuration files:",
        "1. Update `anachronistic_titles_1059.md` and `tarraconian_titles_1059.md` with the finalized titles and adjectives.",
        "2. Run `build_mod.ps1` to regenerate `tarr_chancellery_title_list_effects.txt` and `tarraconian_titles_l_english.yml`.",
        ""
    ])

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def update_chatenois_dynasty_analysis(houses, doc_file):
    lines = [
        "# Linguistic Analysis & Tarraconian Adaptation: Dynasty Chatenois (ID 1582)",
        "",
        "## 1. Etymological Background & Linguistic Sound Laws",
        "",
        "* **Vanilla / Save Name:** `dynn_Chatenois` (*Chatenois*)",
        "* **Etymological Origin:** From Gallo-Romance / Old French *Chastenois* / *Châtenois*, deriving from Latin **Castinetum** (*castanea* 'chestnut' + collective suffix *-etum*, meaning 'chestnut grove' or 'chestnut woods').",
        "* **Historical Germanic Exonym:** In Alsace and Lorraine, toponyms named *Châtenois* (such as Châtenois in Bas-Rhin and Châtenois in Vosges) have been historically and consistently rendered in German as **Kestenholz** (Middle High German *kestene* / *kesten* 'chestnut' + *holz* 'wood / grove').",
        "* **Tarraconian Sound Laws (MHG / Rhine-Moselle Franconian):**",
        "  * Retains unshifted initial `k-` (`Kesten-`).",
        "  * Preserves Middle High German affricate `-z` `[ts]` in `-holz`.",
        "  * Under the Romano-Germanic imperial synthesis of the Tarraconian Chancellery, the authentic imperial Germanic name for House Châtenois is **House Kestenholz** (*Dat Hûs van Kestenholz*).",
        "",
        "## 2. Two-Step Revision Methodology & Title Historicity Coupling",
        "",
        "Cadet house names in the save game typically follow the formula `<Dynasty>-<Seat>` (e.g., *Chatenois-Lemberg*, *Chatenois-Koschmin*, *Chatenois-Hirschberg*). The audit reconciles these names through a strict **two-step pipeline**:",
        "",
        "1. **Step 1: Dynasty Stem Normalization (Phase 1 Baseline):**",
        "   * Replaces the Gallo-Romance stem *Chatenois* with the authentic Rhine-Moselle Franconian imperial stem **Kestenholz** (*Dat Hûs van Kestenholz*).",
        "",
        "2. **Step 2: Toponymic Suffix Realignment (Phases 2–4 Coupling):**",
        "   * Many cadet branches are named after seats that are themselves **Tier 2 hydronymic foundations** (requiring pre-HRE morphology) or **Tier 3 settlements** (post-867 OTL dynastic castles/settlements).",
        "   * In Phase 4, each cadet branch's toponymic suffix is permanently realigned to match the resolved historical seat and its official Tarraconian Chancellery translation:",
        "     * *Resolved Pre-867 Centre:* `c_lviv` was historically resolved from *Lemberg* (1256 OTL foundation) to the 10th-century princely capital *Swenigorot* (`b_zvenyhorod`). Accordingly, House `16796257` (*Chatenois-Lemberg*) becomes **Kestenholz-Swenigorot**.",
        "     * *Anachronistic Höhenburgen & Ostsiedlung Seats:* Houses named after High Medieval foundations like *Berg*, *Saarbrücken*, *Stężyca*, *Plzeň*, *Koschmin*, *Kammersberg*, *Hirschberg*, or *Peiting* update their toponymic suffix to their verified pre-867 centres in Tarraconian chancellery orthography (*Kestenholz-Kaiserswerth*, *Kestenholz-Zant-Arnolt*, *Kestenholz-Sitzichow*, *Kestenholz-Plzenec*, *Kestenholz-Kalisz*, *Kestenholz-Judenburg*, *Kestenholz-Legnica*, *Kestenholz-Altenstadt*).",
        "     * *Tarraconian Phonological Adaptation:* Authentic pre-867 seats like *Metz*, *Ravenna*, *Bremen*, *Saumur*, or *Orléans* receive their finalized Tarraconian Chancellery forms (*Kestenholz-Metz*, *Kestenholz-Raben*, *Kestenholz-Bremen*, *Kestenholz-Orleans*).",
        "",
        "---",
        "",
        f"## 3. Final Master Cadet Branch Rename Register (The {len(houses)} Houses of House Kestenholz)",
        "",
        f"Below is the complete, finalized register of all **{len(houses)}** cadet branches of Dynasty 1582, sorted by living members count, featuring their Phase 1 baseline name and their finalized Step 2 coupled realigned name:",
        "",
        "| House ID | Current In-Game Name | Phase 1 Baseline Name | Final Realigned Name | Underlying Seat Origin | Living Members | Head of House | Status & Justification |",
        "| :---: | :--- | :--- | :--- | :--- | :---: | :--- | :--- |",
    ]

    for h in houses:
        lines.append(
            f"| `{h['house_id']}` | **{h['current_name']}** | `{h['phase1_baseline_name']}` | **{h['final_realigned_name']}** | `{h['underlying_seat']}` | **{h['living_members']}** | {h['head_name']} (`{h['head_id']}`) | {h['status']}: {h['coupling_justification']} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 4. Chancellery Implementation Guide",
        "",
        "To apply these names in-game:",
        "1. **Dynasty Customization:** When using the in-game Dynasty Customizer, rename Dynasty 1582 from *Chatenois* to **Kestenholz** (*Motto: Dat Hûs van Kestenholz*).",
        "2. **Cadet Branch Renaming:** For each cadet branch landed in the Empire, customize the house name to its **Final Realigned Name** from Section 3 above.",
        "3. **Mod Scripting:** The generated `dynasty_cadet_rename_register.csv` can be directly referenced by mod scripts or save game editing routines.",
        ""
    ])

    with open(doc_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))



def generate_dynasty_historical_realignment_register(chatenois_houses, non_chatenois_houses, cultures, doc_file, csv_file=None):
    """
    Generates dynastic_realignment_register.md compiling all dynasty, house, and emergent culture names
    that were automatically derived from anachronistic title names, enforcing the Toponym-First Principle.
    """
    lines = [
        "# Master Dynastic Realignment Register (Toponym-First Coupling)",
        "",
        "* **Project:** Tarraconian Chancellery Mod & Imperial Documentation",
        "* **Scope:** All noble dynasties, cadet houses, and dynamic emergent cultures derived from anachronistic title names in the Holy Roman Empire and imperial borderlands.",
        "* **Guiding Rule:** **The Toponym-First Principle** (Physical Geography & Antiquity Substrates $\\rightarrow$ Landed Title $\\rightarrow$ Dynastic & Cultural Eponym).",
        "",
        "---",
        "",
        "## 1. Problem Statement & The Inversion of Dynastic Causality",
        "",
        "In Crusader Kings III, dynastic and cultural generation operates mechanically in reverse:",
        "1. **Static Vanilla Map Anachronisms:** CK3 uses a single landed title map spanning 867 to 1453. Numerous titles represent post-867 High/Late Medieval castles (*Habsburg*, *Hohenzollern*, *Berg*, *Saarbrücken*, *Mark*, *Pernstein*, *Coburg*), 12th–14th century Ostsiedlung foundations (*Lemberg*, *Uničov*, *Hirschberg*, *Koschmin*, *Güstrow*, *Buxtehude*, *Celle*, *Wittenberg*, *Jihlava*), or post-867 frontier outposts (*Novogrudok*, *Volkovysk*, *Porto-Vecchio*, *Lyubim*, *Povenets*, *Tambov*).",
        "2. **Dynamic Cadet & Eponym Generation:** When an unlanded character is granted land or a ruler establishes a cadet branch, the game engine automatically stamps the holding's name onto the dynasty (e.g., *House Naugardukas* from `c_novogrudok`, *Karling-Uničov* from `b_unicov`, *Reginar-Vecchio* from `c_vecchio`, *Chatenois-Lemberg* from `c_lviv`, *Umayyad-Povenets* from `c_povenets`, *Gellones-Güstrow* from `b_gustrow`).",
        "3. **Dynamic Emergent Culture Ethnogenesis:** When dynamic hybrid or divergent cultures form, the game automatically anchors their collective ethnonym to the capital holding of the diverged realm (e.g., *Galațian-Vlachs* from `c_galati`, *Bugeacian-Vlachs* from `c_bugeac`, *Wolkensteiner-Polabians* from `c_wolkenstein`, *Jutribocian-Polabians* from `c_juterbog`, *South Kazanskayan-Khazars* from `c_kazanskaya`).",
        "4. **The Toponym-First Inversion:** Under imperial historiography, noble houses and dynamic emergent cultures cannot validate or grandfather anachronistic titles. Instead, causality must be strictly inverted: **the holding is first cleansed of its post-867 name**, and the noble house or emergent culture is subsequently realigned to the restored authentic antiquity centre or hydronym.",
        "",
        "---",
        "",
        "## 2. Non-Chatenois Dynastic & Cadet Realignment Register",
        "",
        "The following noble houses and newly elevated dynasties across the Empire and its marchlands were generated from anachronistic holding names and are hereby realigned to their authentic pre-867 seats:",
        "",
        "| House ID | Dynasty | Current In-Game Name | Underlying Origin Seat | Anachronism Reason | Resolved Toponym-First Seat | Realigned House Name | Tarraconian Chancellery Form | Status & Justification |",
        "| :---: | :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    csv_rows = []
    for hid, data in sorted(non_chatenois_houses.items(), key=lambda x: str(x[1].get("dynasty_name", ""))):
        h_id = data["house_id"]
        d_name = data["dynasty_name"]
        curr_name = data["current_name"]
        seat = data["seat_county"]
        seat_orig = data["seat_origin"]
        res_seat = data["resolved_seat"]
        realigned = data["realigned_name"]
        tarr_name = data["tarraconian_name"]
        reason = data["coupling_reason"]

        lines.append(
            f"| `{h_id}` | **{d_name}** (`{data['dynasty_id']}`) | `{curr_name}` | `{seat}` ({seat_orig}) | Post-867 foundation | **{res_seat}** | **{realigned}** | `{tarr_name}` | {reason} |"
        )
        csv_rows.append([
            h_id, data['dynasty_id'], d_name, curr_name, seat, seat_orig, res_seat, realigned, tarr_name, reason
        ])

    lines.extend([
        "",
        "---",
        "",
        "## 3. The Imperial Dynasty: House Châtenois / Kestenholz (ID 1582)",
        "",
        "### 3.1 Etymological Background & Linguistic Sound Laws",
        "* **Vanilla / Save Name:** `dynn_Chatenois` (*Chatenois*)",
        "* **Etymological Origin:** From Gallo-Romance / Old French *Chastenois* / *Châtenois*, deriving from Latin **Castinetum** (*castanea* 'chestnut' + collective suffix *-etum*, meaning 'chestnut grove' or 'chestnut woods').",
        "* **Historical Germanic Exonym:** In Alsace and Lorraine, toponyms named *Châtenois* (such as Châtenois in Bas-Rhin and Châtenois in Vosges) have been historically and consistently rendered in German as **Kestenholz** (Middle High German *kestene* / *kesten* 'chestnut' + *holz* 'wood / grove').",
        "* **Tarraconian Sound Laws (MHG / Rhine-Moselle Franconian):**",
        "  * Retains unshifted initial `k-` (`Kesten-`).",
        "  * Preserves Middle High German affricate `-z` `[ts]` in `-holz`.",
        "  * Under the Romano-Germanic imperial synthesis of the Tarraconian Chancellery, the authentic imperial Germanic name for House Châtenois is **House Kestenholz** (*Dat Hûs van Kestenholz*).",
        "",
        f"### 3.2 Master Cadet Branch Rename Register (The {len(chatenois_houses)} Houses of House Kestenholz)",
        f"Coupled realignments for all {len(chatenois_houses)} cadet houses of the imperial dynasty, sorted by living members count:",
        "",
        "| House ID | Current In-Game Name | Phase 1 Baseline Name | Final Realigned Name | Underlying Seat Origin | Living Members | Head of House | Status & Justification |",
        "| :---: | :--- | :--- | :--- | :--- | :---: | :--- | :--- |",
    ])

    for h in chatenois_houses:
        lines.append(
            f"| `{h['house_id']}` | **{h['current_name']}** | `{h['phase1_baseline_name']}` | **{h['final_realigned_name']}** | `{h['underlying_seat']}` | **{h['living_members']}** | {h['head_name']} (`{h['head_id']}`) | {h['status']}: {h['coupling_justification']} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 4. Dynamic Emergent Culture Realignment Register",
        "",
        "Under the **Toponym-First Principle & Downstream Causality Inversion Rule** (Section 3.3 of the Master Audit Plan), dynamic divergent and hybrid cultures formed during the campaign whose vanilla or save-generated names derived from post-867 anachronistic foundations are systematically realigned to the resolved historical toponyms of their ethnogenesis seats. Emergent cultures cannot validate or grandfather anachronistic titles; rather, ethnonyms derive *from* the historically resolved physical geography, antiquity civitates, and authentic hydronyms:",
        "",
        "| Culture ID | Current In-Game Name | Divergence Date | Underlying Origin Seat | Resolved Historical Toponym | Final Realigned Culture Name | Realigned Collective Noun | Tarraconian Culture Name | Status & Historical Justification |",
        "| :---: | :--- | :---: | :--- | :--- | :--- | :--- | :--- | :--- |",
    ])

    for c in cultures:
        lines.append(
            f"| `{c['culture_id']}` | **{c['current_name']}** | {c['created']} | `{c['underlying_origin_seat']}` ({c['underlying_seat_name']}) | **{c['resolved_toponym']}** | **{c['realigned_name']}** | *{c['realigned_collective']}* | `{c['tarraconian_culture_name']}` | **{c['status']}:** {c['historical_justification']} |"
        )

    lines.extend([
        "",
        "---",
        "",
        "## 5. Summary & Implementation Instructions",
        "",
        "1. **County Name Localisation Primacy:** In accordance with imperial chancellery directives, **county localizations are revised** (e.g. `c_novogrudok` $\\rightarrow$ **`Plîse`**, `c_volkovysk` $\\rightarrow$ **`Rôse`**, `c_minsk` $\\rightarrow$ **`Mêne`**), while **barony names (`b_*`) remain unaltered** in the map definition.",
        "2. **Dynastic Synchronization:** For characters holding titles in-game, house names can be realigned using the in-game House Customizer, save editing, or mod character flavorization scripts based on the **Realigned House Name** column above.",
        "3. **Dynamic Emergent Culture Localization:** Emergent cultures derived from post-867 anachronisms must be customized via in-game culture reform / hybridization menus or mod localization override keys using the **Final Realigned Culture Name** and **Tarraconian Culture Name** specifications above.",
        "4. **Pipeline Coupling:** This document is automatically generated by Phase 4 of the Tarraconian Historical Accuracy Audit Pipeline, ensuring permanent containerized synchronization.",
        ""
    ])

    with open(doc_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    if csv_file:
        try:
            with open(csv_file, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "house_id", "dynasty_id", "dynasty_name", "current_name", "seat_county",
                    "seat_origin", "resolved_seat", "realigned_name", "tarraconian_name", "coupling_reason"
                ])
                for row in csv_rows:
                    writer.writerow(row)
        except Exception as e:
            print(f"[Phase 4] Warning: Failed to write CSV {csv_file}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Phase 4: Title Resolution & Dynasty Extraction Pipeline")
    parser.add_argument("--phase1-dir", default="/var/tmp/ck3_audit/phase1", help="Path to Phase 1 data directory")
    parser.add_argument("--phase3-dir", default="/var/tmp/ck3_audit/phase3", help="Path to Phase 3 data directory")
    parser.add_argument("--output-dir", default="/var/tmp/ck3_audit/phase4", help="Output directory in /var/tmp")
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parser.add_argument("--repo-dir", default=repo_root, help="Git repository directory")

    args = parser.parse_args()

    run_phase4(
        phase1_dir=args.phase1_dir,
        phase3_dir=args.phase3_dir,
        output_dir=args.output_dir,
        repo_dir=args.repo_dir
    )

if __name__ == "__main__":
    main()

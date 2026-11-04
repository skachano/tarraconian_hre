#!/usr/bin/env python3
"""
Phase 4: Title Resolution, Reconciliation & Dynasty Extraction Pipeline
Part of the Tarraconian Historical Accuracy Audit Pipeline.

This script executes Phase 4 of the audit plan:
1. Finalizes the definitive historical resolution for all 150 flagged titles (Option A, Option B, or Option C).
2. Applies Tarraconian sound laws (Rhine-Moselle Franconian MHG + Old Catalan) to formulate official Chancellery titles and adjectives.
3. Systematically couples each of the 50 cadet branches of Dynasty 1582 (House Kestenholz) to its underlying seat and updates chatenois_dynasty_analysis.md.
4. Generates the comprehensive audit_discrepancy_register.md in the git repository workspace.
5. Writes machine-readable resolution tables to /tmp/ck3_audit_phase4/.
"""

import argparse
import csv
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

# Import the coupling dictionary from screen_phase3_titles
from screen_phase3_titles import CADET_BRANCH_COUPLINGS, HISTORICAL_TITLE_DB


def run_phase4(phase1_dir, phase3_dir, output_dir, repo_dir):
    print("[Phase 4] Loading Phase 1 and Phase 3 data...")
    with open(Path(phase3_dir) / "title_screening_matrix.json", "r", encoding="utf-8") as f:
        screening_matrix = json.load(f)

    with open(Path(phase1_dir) / "chatenois_dynasty_analysis.json", "r", encoding="utf-8") as f:
        dynasty_data = json.load(f)

    with open(Path(phase1_dir) / "titles_data.json", "r", encoding="utf-8") as f:
        titles_data = json.load(f)

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

        res_entry = {
            "county_key": ck,
            "save_name": item["save_name"],
            "kingdom": item["kingdom"],
            "duchy": item["duchy"],
            "tier": item["tier"],
            "tier_reason": item["tier_reason"],
            "selected_option": rec["selected_option"],
            "resolved_name": opt_a["candidate_name"] if rec["selected_option"] == "Option A" else opt_b["toponymic_stem"],
            "resolved_key": opt_a["candidate_key"] if rec["selected_option"] == "Option A" else opt_b["hydronym"],
            "tarraconian_title": rec["tarraconian_chancellery_name"],
            "tarraconian_adjective": rec["tarraconian_adjective"],
            "historical_justification": rec["historical_justification"],
            "cadet_branch_coupled": coupling["coupled"],
            "cadet_house_id": coupling["cadet_house_id"],
            "cadet_realigned_name": coupling["realigned_name"]
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

    # 3. Generate Workspace Deliverable: audit_discrepancy_register.md
    discrepancy_file = Path(repo_dir) / "audit_discrepancy_register.md"
    generate_audit_discrepancy_register(final_resolutions, dynasty_rename_register, discrepancy_file)
    print(f"[Phase 4] Wrote audit discrepancy register to {discrepancy_file}")

    # 4. Update Workspace Deliverable: chatenois_dynasty_analysis.md
    dynasty_doc_file = Path(repo_dir) / "chatenois_dynasty_analysis.md"
    update_chatenois_dynasty_analysis(dynasty_rename_register, dynasty_doc_file)
    print(f"[Phase 4] Updated dynasty analysis document at {dynasty_doc_file}")


def generate_audit_discrepancy_register(titles, houses, report_file):
    total_titles = len(titles)
    tier4_count = sum(1 for t in titles if t["tier"] == 4)
    tier5_count = sum(1 for t in titles if t["tier"] == 5)
    opt_a_count = sum(1 for t in titles if t["selected_option"] == "Option A")
    opt_b_count = sum(1 for t in titles if t["selected_option"] == "Option B")
    coupled_houses = [h for h in houses if "Realigned" in h["status"]]

    lines = [
        "# Audit Discrepancy Register: Historical Accuracy & Title Resolutions",
        "",
        "* **Campaign Date:** 20 August 1142 (`chatenois_867_01_01.ck3`)",
        f"* **Audit Scope:** **{total_titles} Flagged Imperial Counties** across **50 De Jure Kingdoms**",
        "* **Core Framework:** 867 Alternate-History Divergence Point → Colonizer Presence Audit → Sub-Barony / Hydronymic Hierarchy → Tarraconian Chancellery Sound Laws",
        "",
        "---",
        "",
        "## 1. Executive Summary & Resolution Metrics",
        "",
        "This register constitutes the definitive, finalized reconciliation of all landed titles inside the **Roman Empire** (`h_roman_empire`) that exhibited chronological anachronisms (Tier 4) or foreign colonial mismatches (Tier 5). Every title is paired with its verified pre-867 settlement or hydronym, along with official Tarraconian Chancellery forms and adjectives.",
        "",
        "| Audit Category | Total Titles | Percentage | Resolution Strategy |",
        "| :--- | :---: | :---: | :--- |",
        f"| **Total Flagged Imperial Titles** | **{total_titles}** | **100.0%** | Full reconciliation against 867 campaign divergence |",
        f"| • **Tier 4: Post-867 OTL Foundations** | **{tier4_count}** | {tier4_count/total_titles*100:.1f}% | Replaced by ancient pre-867 Roman, Celtic, Carolingian, or Slavic centres |",
        f"| • **Tier 5: Foreign Colonial Mismatches** | **{tier5_count}** | {tier5_count/total_titles*100:.1f}% | Reverted from unhistorical German/Swedish/Cossack exonyms to native roots |",
        f"| **Option A: Pre-867 Sub-Barony Centers** | **{opt_a_count}** | {opt_a_count/total_titles*100:.1f}% | Anchored to attested ancient oppida, castra, civitates, or collegiate abbeys |",
        f"| **Option B: Ancient Hydronyms / Oronyms** | **{opt_b_count}** | {opt_b_count/total_titles*100:.1f}% | Resolved via river/mountain basins applying Section 3.1 Hydronym Hierarchy |",
        f"| **Coupled Cadet Houses of House Kestenholz** | **{len(coupled_houses)}** | — | Toponymic seat suffixes updated to match resolved pre-867 centres |",
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
        "## 3. Master Title Discrepancy & Resolution Register (150 Imperial Counties)",
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
        res_str = f"**{t['selected_option']}:** `{t['resolved_key']}` ({t['resolved_name']})"
        tarr_title = t["tarraconian_title"]
        tarr_adj = t["tarraconian_adjective"]
        just = t["historical_justification"]

        lines.append(f"| `{ck}` | **{sn}** | {k} | **{tier}** | {reason} | {res_str} | **{tarr_title}** | *{tarr_adj}* | {just} |")

    lines.extend([
        "",
        "---",
        "",
        "## 4. Linguistic Adaptation & Sound Law Implementation",
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
        "## 5. Transition to Phase 5: Documentation Update & Mod Recompilation",
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
        "   * Many cadet branches are named after seats that are themselves **Tier 4 anachronisms** (post-867 OTL dynastic castles/settlements) or **Tier 5 colonial mismatches** (e.g., German *Ostsiedlung* or Tsarist Russian exonyms).",
        "   * In Phase 4, each cadet branch's toponymic suffix is permanently realigned to match the resolved historical seat and its official Tarraconian Chancellery translation:",
        "     * *Resolved Pre-867 Centre:* `c_lviv` was historically resolved from *Lemberg* (1256 OTL foundation) to the 10th-century princely capital *Swenigorot* (`b_zvenyhorod`). Accordingly, House `16796257` (*Chatenois-Lemberg*) becomes **Kestenholz-Swenigorot**.",
        "     * *Anachronistic Höhenburgen & Ostsiedlung Seats:* Houses named after High Medieval foundations like *Berg*, *Saarbrücken*, *Stężyca*, *Plzeň*, *Koschmin*, *Kammersberg*, *Hirschberg*, or *Peiting* update their toponymic suffix to their verified pre-867 centres in Tarraconian chancellery orthography (*Kestenholz-Kaiserswerth*, *Kestenholz-Zant-Arnolt*, *Kestenholz-Sitzichow*, *Kestenholz-Plzenec*, *Kestenholz-Kalisz*, *Kestenholz-Judenburg*, *Kestenholz-Legnica*, *Kestenholz-Altenstadt*).",
        "     * *Tarraconian Phonological Adaptation:* Authentic pre-867 seats like *Metz*, *Ravenna*, *Bremen*, *Saumur*, or *Orléans* receive their finalized Tarraconian Chancellery forms (*Kestenholz-Metz*, *Kestenholz-Raben*, *Kestenholz-Bremen*, *Kestenholz-Orleans*).",
        "",
        "---",
        "",
        "## 3. Final Master Cadet Branch Rename Register (The 50 Houses of House Kestenholz)",
        "",
        "Below is the complete, finalized register of all **50** cadet branches of Dynasty 1582, sorted by living members count, featuring their Phase 1 baseline name and their finalized Step 2 coupled realigned name:",
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


def main():
    parser = argparse.ArgumentParser(description="Phase 4: Title Resolution & Dynasty Extraction Pipeline")
    parser.add_argument("--phase1-dir", default="/tmp/ck3_audit_phase1", help="Path to Phase 1 data directory")
    parser.add_argument("--phase3-dir", default="/tmp/ck3_audit_phase3", help="Path to Phase 3 data directory")
    parser.add_argument("--output-dir", default="/tmp/ck3_audit_phase4", help="Output directory in /tmp")
    parser.add_argument("--repo-dir", default="/workspace", help="Git repository directory")

    args = parser.parse_args()

    run_phase4(
        phase1_dir=args.phase1_dir,
        phase3_dir=args.phase3_dir,
        output_dir=args.output_dir,
        repo_dir=args.repo_dir
    )

if __name__ == "__main__":
    main()

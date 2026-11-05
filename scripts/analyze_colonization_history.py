#!/usr/bin/env python3
"""
Geopolitical Colonization & Imperial Trajectory Analysis (867-1142)
Part of the Tarraconian Historical Accuracy Audit.

Analyzes the sovereign history of all 209 flagged titles to uncover the
settlement, conquest, and colonial layers left by:
1. The Scandinavian Empire & Norse Sea Kings
2. The Byzantine Empire & Pontic Greek Aristocracy
3. The Hashimid-Lina & Andalusi/Islamic Realms
4. Continental Dynastic, Marcher & Indigenous Steppe Khanates

Formulates candidate colonial toponyms and their official Tarragonised forms.
"""

import json
from pathlib import Path
from collections import defaultdict

def run_analysis():
    phase1_dir = Path("/var/tmp/ck3_audit/phase1")
    phase4_dir = Path("/var/tmp/ck3_audit/phase4")
    repo_dir = Path(__file__).resolve().parent.parent

    with open(phase4_dir / "final_title_resolutions.json", "r", encoding="utf-8") as f:
        resolutions = json.load(f)

    with open(phase1_dir / "titles_data.json", "r", encoding="utf-8") as f:
        titles_data = json.load(f)

    with open(phase1_dir / "historical_characters.json", "r", encoding="utf-8") as f:
        chars = json.load(f)

    with open(phase1_dir / "dynasties_and_houses.json", "r", encoding="utf-8") as f:
        dyn_data = json.load(f)

    houses = dyn_data.get('houses', {})
    dynasties = dyn_data.get('dynasties', {})

    report_path = repo_dir / "geopolitical_colonization_title_audit.md"
    
    scandinavian_records = []
    byzantine_records = []
    hashimid_records = []
    continental_records = []

    for r in resolutions:
        ck = r["county_key"]
        t = titles_data.get(ck, {})
        hist = t.get("history", [])
        k = t.get("de_jure_kingdom", r.get("kingdom", ""))
        d = t.get("de_jure_duchy", r.get("duchy", ""))

        # Analyze ruler history
        scan_rulers = []
        byz_rulers = []
        hashim_rulers = []
        other_rulers = []

        for h in hist:
            c = (h.get("culture_name") or "").lower()
            house_str = h.get("house_name") or ""
            did = h.get("dynasty_id")

            if any(term in c for term in ["norse", "swedish", "danish", "norwegian", "northislanders"]):
                scan_rulers.append(h)
            elif any(term in c for term in ["greek", "byzantine", "pontic", "cypriot", "armeno-greek"]):
                byz_rulers.append(h)
            elif "hashim" in house_str.lower() or did == 1727 or any(term in c for term in ["andalusian", "levantine", "bedouin", "maghrebi", "baranis", "butr", "egyptian"]):
                hashim_rulers.append(h)
            else:
                other_rulers.append(h)

        entry = {
            "county_key": ck,
            "save_name": r["save_name"],
            "kingdom": k,
            "duchy": d,
            "tier": r["tier"],
            "tier_reason": r["tier_reason"],
            "resolved_option_a": r["resolved_name"],
            "resolved_key_a": r["resolved_key"],
            "tarr_title": r["tarraconian_title"],
            "history": hist,
            "scan_rulers": scan_rulers,
            "byz_rulers": byz_rulers,
            "hashim_rulers": hashim_rulers,
            "other_rulers": other_rulers
        }

        # Assign to primary categories (can belong to multiple if multi-layered)
        is_assigned = False
        if scan_rulers:
            scandinavian_records.append(entry)
            is_assigned = True
        if byz_rulers:
            byzantine_records.append(entry)
            is_assigned = True
        if hashim_rulers:
            hashimid_records.append(entry)
            is_assigned = True
        if not is_assigned:
            continental_records.append(entry)

    print(f"Scandinavian records: {len(scandinavian_records)}")
    print(f"Byzantine records: {len(byzantine_records)}")
    print(f"Hashimid records: {len(hashimid_records)}")
    print(f"Continental/Indigenous records: {len(continental_records)}")

if __name__ == "__main__":
    run_analysis()

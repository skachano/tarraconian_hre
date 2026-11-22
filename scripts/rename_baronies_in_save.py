#!/usr/bin/env python3
"""
rename_baronies_in_save.py

Audits baronies strictly adhering to the Burden of Proof principle and
renames all ahistorical baronies in the active CK3 save:
- /var/tmp/ck3_audit/melted_save.ck3
- /var/tmp/ck3_audit/chatenois_867_01_01.ck3

Updates title_name_data={ name="..." } to official Tarraconian Chancellery historical resolutions.
"""

import io
import json
import os
import re
import shutil
import sys
import time
import zipfile
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_DIR / "data"
RESOLUTIONS_PATH = DATA_DIR / "barony_resolutions.json"

SAVE_MELTED = Path("/var/tmp/ck3_audit/melted_save.ck3")
SAVE_ZIP = Path("/var/tmp/ck3_audit/chatenois_867_01_01.ck3")


def audit_and_rename_save(dry_run=False):
    print("==================================================================")
    print("Historical Audit & Save Renaming Engine (Burden of Proof Principle)")
    print("==================================================================")

    if not RESOLUTIONS_PATH.exists():
        print(f"Error: {RESOLUTIONS_PATH} does not exist!")
        sys.exit(1)

    with open(RESOLUTIONS_PATH, "r", encoding="utf-8") as f:
        resolutions = json.load(f)

    print(f"Loaded {len(resolutions)} barony resolutions from database.")

    if not SAVE_MELTED.exists():
        print(f"Error: {SAVE_MELTED} does not exist!")
        sys.exit(1)

    # 1. Classification & Burden of Proof Audit
    ahistorical_keys = set()
    total_occupied = 0
    for bk, data in resolutions.items():
        name = data.get("name", "")
        if not name:
            continue
        total_occupied += 1
        cat = data.get("category", "")
        anach = data.get("b_anachronism", "")
        hist = data.get("b_tarr_hist", "")
        direct = data.get("b_tarr_direct", "")

        is_ahistorical = False
        if cat in {
            "option_b_hydronym", "option_c_foundation", "indigenous_restitution",
            "hundred_moot_calque", "option_a_seat", "descriptive_calque",
            "capital_disambiguation", "secondary_holding_disambiguation",
            "collision_disambiguation"
        }:
            is_ahistorical = True
        elif anach:
            is_ahistorical = True
        elif hist and direct and hist != direct:
            is_ahistorical = True
        elif cat == "sinosphere_calque":
            is_ahistorical = True

        if is_ahistorical:
            ahistorical_keys.add(bk)

    print(f"Burden of Proof Audit identified {len(ahistorical_keys)} ahistorical baronies requiring resolution.")

    # 2. Process melted save file
    tmp_melted = SAVE_MELTED.with_suffix(".ck3.tmp")
    bak_melted = SAVE_MELTED.with_suffix(".ck3.bak")

    renamed_count = 0
    ahistorical_renamed = 0
    skipped_unoccupied = 0
    already_matching = 0

    renamed_samples = []

    print(f"Streaming and updating {SAVE_MELTED}...")
    t0 = time.time()

    with open(SAVE_MELTED, "r", encoding="utf-8", errors="ignore") as infile, \
         open(tmp_melted, "w", encoding="utf-8") as outfile:

        in_landed_titles = False
        in_barony_block = False
        in_tnd = False
        cur_bk = None
        cur_old_name = None

        for line in infile:
            if not in_landed_titles:
                if line.startswith("\tlanded_titles={"):
                    in_landed_titles = True
                outfile.write(line)
                continue

            if line.startswith("\t}"):
                in_landed_titles = False
                outfile.write(line)
                continue

            if line.startswith("\t\t") and not line.startswith("\t\t\t"):
                # New title block boundary
                in_barony_block = False
                in_tnd = False
                cur_bk = None
                cur_old_name = None
                outfile.write(line)
                continue

            if line.startswith("\t\t\tkey=\"b_"):
                m = re.search(r'key="([^"]+)"', line)
                if m:
                    cur_bk = m.group(1)
                    in_barony_block = True
                outfile.write(line)
                continue

            if in_barony_block:
                if "title_name_data={" in line:
                    in_tnd = True
                    outfile.write(line)
                    continue

                if in_tnd:
                    if line.startswith("\t\t\t}"):
                        in_tnd = False
                        outfile.write(line)
                        continue

                    if line.startswith("\t\t\t\tname=\""):
                        m_nm = re.search(r'name="([^"]*)"', line)
                        cur_old_name = m_nm.group(1) if m_nm else ""

                        if cur_bk and cur_bk in resolutions:
                            res = resolutions[cur_bk]
                            target_name = res.get("name")

                            if not target_name:  # Unoccupied holding: preserve blank / original
                                skipped_unoccupied += 1
                                outfile.write(line)
                            elif target_name == cur_old_name:
                                already_matching += 1
                                outfile.write(line)
                            else:
                                renamed_count += 1
                                if cur_bk in ahistorical_keys:
                                    ahistorical_renamed += 1
                                if len(renamed_samples) < 25:
                                    renamed_samples.append((cur_bk, cur_old_name, target_name, res.get("category")))
                                outfile.write(f'\t\t\t\tname="{target_name}"\n')
                        else:
                            outfile.write(line)
                        continue

                    if line.startswith("\t\t\t\tadj=\""):
                        # If the name was renamed, drop outdated vanilla adjective
                        if cur_bk and cur_bk in resolutions:
                            res = resolutions[cur_bk]
                            target_name = res.get("name")
                            if target_name and target_name != cur_old_name:
                                # Suppress obsolete exonym adjective
                                continue
                        outfile.write(line)
                        continue

            outfile.write(line)

    t1 = time.time()
    print(f"Finished processing in {t1 - t0:.2f} seconds.")
    print(f"  • Total Baronies Renamed in Save: {renamed_count}")
    print(f"  • Ahistorical Baronies Renamed: {ahistorical_renamed}")
    print(f"  • Already Matching / Preserved: {already_matching}")
    print(f"  • Unoccupied Preserved: {skipped_unoccupied}")

    print("\nSample Renamings in Save:")
    for bk, old_n, new_n, cat in renamed_samples:
        print(f"  [{bk}] '{old_n}' -> '{new_n}' ({cat})")

    if dry_run:
        print("\nDry-run mode: temporary file preserved at", tmp_melted)
        return

    # Backup original melted save
    if not bak_melted.exists():
        print(f"Backing up original save to {bak_melted}...")
        shutil.copy2(SAVE_MELTED, bak_melted)

    # Atomic swap of melted save
    print(f"Replacing {SAVE_MELTED} with updated save file...")
    tmp_melted.replace(SAVE_MELTED)
    print("-> Successfully updated melted_save.ck3!")

    # 3. Repack chatenois_867_01_01.ck3 zip file
    if SAVE_ZIP.exists():
        bak_zip = SAVE_ZIP.with_suffix(".ck3.bak")
        if not bak_zip.exists():
            print(f"Backing up {SAVE_ZIP} to {bak_zip}...")
            shutil.copy2(SAVE_ZIP, bak_zip)

        print(f"Repacking {SAVE_ZIP} with updated gamestate...")
        # Read header and meta from existing zip
        with open(SAVE_ZIP, "rb") as zf:
            header_bytes = zf.read(24)

        meta_bytes = b""
        with zipfile.ZipFile(SAVE_ZIP, "r") as zin:
            if "meta" in zin.namelist():
                meta_bytes = zin.read("meta")

        # Write new zip file
        tmp_zip = SAVE_ZIP.with_suffix(".ck3.tmp")
        with open(tmp_zip, "wb") as out_zf:
            out_zf.write(header_bytes)
            with zipfile.ZipFile(out_zf, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zout:
                print("  Writing updated gamestate into zip...")
                zout.write(SAVE_MELTED, arcname="gamestate")
                if meta_bytes:
                    print("  Writing meta into zip...")
                    zout.writestr("meta", meta_bytes)

        tmp_zip.replace(SAVE_ZIP)
        print("-> Successfully repacked chatenois_867_01_01.ck3!")


if __name__ == "__main__":
    audit_and_rename_save()

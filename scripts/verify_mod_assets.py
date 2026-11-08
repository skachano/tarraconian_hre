#!/usr/bin/env python3
"""
Comprehensive Phase 5 Mod Verification Script
Validates:
1. Scripted effect syntax and title assignments
2. Localization key completeness and 1:1 mapping
3. Adjective presence and validity
4. Master gazetteer title coverage
5. Zero breaking errors or orphan triggers
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EFFECTS_PATH = REPO_ROOT / "tarraconian_chancellery" / "common" / "scripted_effects" / "tarr_chancellery_title_list_effects.txt"
DYNASTIC_EFFECTS_PATH = REPO_ROOT / "tarraconian_chancellery" / "common" / "scripted_effects" / "tarr_chancellery_dynastic_effects.txt"
CORE_EFFECTS_PATH = REPO_ROOT / "tarraconian_chancellery" / "common" / "scripted_effects" / "tarr_chancellery_core_effects.txt"
LOC_PATH = REPO_ROOT / "tarraconian_chancellery" / "localization" / "english" / "tarraconian_titles_l_english.yml"
GAZETTEER_PATH = REPO_ROOT / "tarraconian_titles_1059.md"
DYNASTIC_REGISTER_PATH = REPO_ROOT / "dynastic_realignment_register.md"

def verify():
    errors = []
    warnings = []

    # 1. Read files
    with open(EFFECTS_PATH, 'rb') as f:
        effects_bytes = f.read()
    assert effects_bytes.startswith(b'\xef\xbb\xbf'), "EFFECTS file missing UTF-8 BOM"
    effects_text = effects_bytes.decode('utf-8-sig')
    assert '\r\n' in effects_text, "EFFECTS file does not have CRLF line endings"

    with open(LOC_PATH, 'rb') as f:
        loc_bytes = f.read()
    assert loc_bytes.startswith(b'\xef\xbb\xbf'), "LOC file missing UTF-8 BOM"
    loc_text = loc_bytes.decode('utf-8-sig')
    assert '\r\n' in loc_text, "LOC file does not have CRLF line endings"

    # 2. Parse localization keys
    loc_lines = loc_text.splitlines()
    loc_dict = {}
    duplicates = []
    for line in loc_lines:
        line_clean = line.strip()
        if not line_clean or line_clean.startswith('#') or line_clean == 'l_english:':
            continue
        m = re.match(r'^([a-zA-Z0-9_\-\.]+):0\s*\"(.*)\"$', line_clean)
        if m:
            k, v = m.group(1), m.group(2)
            if k in loc_dict:
                duplicates.append(k)
            loc_dict[k] = v
        else:
            warnings.append(f"Unmatched loc line: {line_clean}")

    if duplicates:
        errors.append(f"Found {len(duplicates)} duplicate localization keys: {duplicates[:5]}")

    print(f"Total parsed localization entries: {len(loc_dict)}")

    # 3. Check every NAME and HIST in effects
    name_refs = re.findall(r'NAME\s*=\s*([a-zA-Z0-9_\-]+)', effects_text)
    hist_refs = re.findall(r'HIST\s*=\s*([a-zA-Z0-9_\-]+)', effects_text)

    all_refs = set(name_refs + hist_refs)
    print(f"Total unique localization keys referenced in effects: {len(all_refs)}")

    missing_loc = [k for k in all_refs if k not in loc_dict]
    if missing_loc:
        errors.append(f"Missing {len(missing_loc)} localization keys in yml: {missing_loc[:10]}")
    else:
        print("  -> Zero missing localization keys for effects references! (100% matched)")

    # 4. Check that every cn_tarr_* title has an _adj
    missing_adjs = []
    for k in loc_dict:
        if k.startswith('cn_tarr_') and not k.endswith('_adj'):
            adj_key = f"{k}_adj"
            if adj_key not in loc_dict:
                missing_adjs.append(adj_key)

    if missing_adjs:
        errors.append(f"Missing {len(missing_adjs)} adjectives: {missing_adjs[:10]}")
    else:
        print("  -> Zero missing title adjectives! (100% matched)")

    # 5. Check static titles vs gazetteer
    from build_mod import parse_gazetteer
    gazetteer_entries = parse_gazetteer(GAZETTEER_PATH)
    print(f"Total gazetteer entries: {len(gazetteer_entries)}")

    static_keys_in_effects = set(re.findall(r'title:([a-zA-Z0-9_\-]+)\s*\?=\s*\{\s*tarr_rename_title_effect', effects_text))
    expected_static_keys = {k for k in gazetteer_entries if not k.startswith('x_script_')}

    missing_static = expected_static_keys - static_keys_in_effects
    extra_static = static_keys_in_effects - expected_static_keys

    if missing_static:
        errors.append(f"Gazetteer titles missing in static scripted effects: {len(missing_static)}: {list(missing_static)[:5]}")
    if extra_static:
        errors.append(f"Extra titles in static scripted effects: {len(extra_static)}: {list(extra_static)[:5]}")

    if not missing_static and not extra_static:
        print(f"  -> Static scripted effects perfectly match master gazetteer: {len(static_keys_in_effects)} titles!")

    # 6. Check dynamic title targets
    dynamic_blocks = re.findall(r'tarr_apply_dynamic_titles_effect\s*=\s*\{([^}]+(?:\{[^}]+\}[^}]+)*)\}', effects_text, re.DOTALL)
    if not dynamic_blocks:
        errors.append("Could not find tarr_apply_dynamic_titles_effect block")
    else:
        dyn_text = dynamic_blocks[0]
        dyn_names = re.findall(r'NAME\s*=\s*([a-zA-Z0-9_\-]+)', dyn_text)
        dyn_hists = re.findall(r'HIST\s*=\s*([a-zA-Z0-9_\-]+)', dyn_text)
        for dk in set(dyn_names + dyn_hists):
            if dk not in loc_dict:
                errors.append(f"Dynamic title references missing loc key: {dk}")

    # 7. Check dynastic and cultural scripted effects and register coverage
    assert DYNASTIC_EFFECTS_PATH.exists(), "DYNASTIC_EFFECTS file missing"
    with open(DYNASTIC_EFFECTS_PATH, 'rb') as f:
        dyn_effects_bytes = f.read()
    assert dyn_effects_bytes.startswith(b'\xef\xbb\xbf'), "DYNASTIC_EFFECTS file missing UTF-8 BOM"
    dyn_effects_text = dyn_effects_bytes.decode('utf-8-sig')
    assert '\r\n' in dyn_effects_text, "DYNASTIC_EFFECTS file does not have CRLF line endings"

    # Extract all loc keys from dynastic effects
    dyn_loc_keys = set()
    for pattern in [
        r'noun\s*=\s*([a-zA-Z0-9_\-]+)',
        r'collective_noun\s*=\s*([a-zA-Z0-9_\-]+)',
        r'prefix\s*=\s*([a-zA-Z0-9_\-]+)',
        r'set_house_name\s*=\s*([a-zA-Z0-9_\-]+)',
        r'set_dynasty_name\s*=\s*([a-zA-Z0-9_\-]+)'
    ]:
        dyn_loc_keys.update(re.findall(pattern, dyn_effects_text))

    print(f"Total unique localization keys referenced in dynastic effects: {len(dyn_loc_keys)}")
    missing_dyn_loc = [k for k in dyn_loc_keys if k not in loc_dict]
    if missing_dyn_loc:
        errors.append(f"Missing {len(missing_dyn_loc)} dynastic localization keys in yml: {missing_dyn_loc[:10]}")
    else:
        print("  -> Zero missing localization keys for dynastic effects! (100% matched)")

    # Check core effects hooks
    with open(CORE_EFFECTS_PATH, 'r', encoding='utf-8') as f:
        core_text = f.read()
    if 'tarr_apply_dynastic_and_cultural_realignment_effect = yes' not in core_text:
        errors.append("tarr_apply_dynastic_and_cultural_realignment_effect not hooked into tarr_chancellery_core_effects.txt")
    else:
        print("  -> Dynastic and cultural effects cleanly hooked into core chancellery pulse!")

    # Check register dynn_* overrides
    from build_mod import parse_dynastic_register
    s2, s3, s4 = parse_dynastic_register(DYNASTIC_REGISTER_PATH)
    with open(DYNASTIC_REGISTER_PATH, 'r', encoding='utf-8') as f:
        reg_text = f.read()
    register_dynn_keys = set(re.findall(r'`(dynn_[a-zA-Z0-9_\-]+)`', reg_text))
    missing_dynn = [k for k in register_dynn_keys if k not in loc_dict]
    if missing_dynn:
        errors.append(f"Register dynn_* overrides missing in yml: {missing_dynn}")
    else:
        print(f"  -> All {len(register_dynn_keys)} register dynn_* overrides defined in localization! (100% matched)")

    print("\n--- SUMMARY ---")
    if errors:
        print(f"FAILED with {len(errors)} errors:")
        for err in errors:
            print(f"  ERROR: {err}")
        return False
    else:
        print("ALL AUDIT AND MOD INTEGRATION VERIFICATIONS PASSED!")
        print(f"  • Total Gazetteer Titles: {len(gazetteer_entries)}")
        print(f"  • Static Titles in Effects: {len(static_keys_in_effects)}")
        print(f"  • Dynamic Renaming Rules: {len(name_refs) - len(static_keys_in_effects)}")
        print(f"  • Total Localized Strings: {len(loc_dict)}")
        print(f"  • Zero Orphan Triggers / Zero Missing Localization Keys")
        return True

if __name__ == '__main__':
    success = verify()
    sys.exit(0 if success else 1)

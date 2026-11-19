#!/usr/bin/env python3
"""
Updates pre-867 historical title symbols and integrates them into
data/canonical_title_heraldry.json and web/js/symbol_generator.js.
"""

import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CANON_PATH = BASE_DIR / "data" / "canonical_title_heraldry.json"
JS_PATH = BASE_DIR / "web" / "js" / "symbol_generator.js"

PRE_867_UPDATES = {
    # 1. Paris: Nautae Parisiaci ancient galley / ship
    "c_paris": ["gules", "solid", "ship", "argent", 1, "argent"],
    # 2. Milan & Lombardy: Iron Crown of Lombardy (Corona Ferrea, 6th-9th c.)
    "c_milano": ["gules", "solid", "crown", "or", 1, "or"],
    "d_lombardy": ["gules", "solid", "crown", "or", 1, "or"],
    # 3. Aachen: Charlemagne's Palatine Reichsadler (800 AD)
    "c_aachen": ["or", "solid", "alerion", "sable", 1, "sable"],
    # 4. Venice: Winged Lion of Saint Mark (adopted 828 AD)
    "c_venezia": ["azure", "solid", "lion_rampant", "or", 1, "or"],
    "d_venice": ["azure", "solid", "lion_rampant", "or", 1, "or"],
    # 5. Ravenna: Byzantine Exarchate & Western Empire Capital
    "c_ravenna": ["or", "solid", "eagle_double", "gules", 1, "gules"],
    "d_ravenna": ["or", "solid", "eagle_double", "gules", 1, "gules"],
    # 6. Antioch: Apostolic Patriarchate of Antioch
    "c_antioch": ["azure", "solid", "cross_patriarchal", "or", 1, "or"],
    "d_antioch": ["azure", "solid", "cross_patriarchal", "or", 1, "or"],
    # 7. Alexandria: Apostolic Patriarchate of Alexandria (Lion of St. Mark)
    "c_alexandria": ["azure", "solid", "lion_rampant", "or", 1, "or"],
    "d_alexandria": ["azure", "solid", "lion_rampant", "or", 1, "or"],
    # 8. Jerusalem: Apostolic Patriarchate of Jerusalem / Holy Sepulchre
    "c_jerusalem": ["gules", "solid", "cross_patriarchal", "or", 1, "or"],
    # 9. Wessex: Golden Dragon of Wessex (Battle of Burford 752 AD, Alfred the Great 867)
    "d_wessex": ["gules", "solid", "dragon", "or", 1, "or"],
    "c_wiltshire": ["gules", "solid", "dragon", "or", 1, "or"],
    # 10. Kent & Canterbury: White Horse of Kent (Invicta, Hengist & Horsa 5th c.)
    "c_kent": ["gules", "solid", "horse_courant", "argent", 1, "argent"],
    "d_canterbury": ["gules", "solid", "horse_courant", "argent", 1, "argent"],
    # 11. Danelaw & York: Raven Banner of the Great Heathen Army (Hrafnsmerki 867 AD)
    "k_danelaw": ["argent", "solid", "falcon_perched", "sable", 1, "sable"],
    "c_york": ["argent", "solid", "falcon_perched", "sable", 1, "sable"],
    # 12. Kyiv: Rus' Princely Falcon / Trident Tamga (Askold & Dir 860-867 AD)
    "c_kyiv": ["azure", "solid", "falcon_perched", "or", 1, "or"],
    # 13. Athens: Classical Roman Column / Byzantine Theme of Hellas
    "c_athens": ["azure", "solid", "column_roman", "or", 1, "or"],
    "d_athens": ["azure", "solid", "column_roman", "or", 1, "or"],
    # 14. Thessalonica: Saint Demetrius Crossed Swords / Theme of Thessalonica
    "c_thessaloniki": ["gules", "solid", "sword_crossed", "or", 1, "or"],
    "d_thessalonika": ["gules", "solid", "sword_crossed", "or", 1, "or"],
}


def update_canonical_json():
    with open(CANON_PATH, "r", encoding="utf-8") as f:
        canon = json.load(f)

    for k, v in PRE_867_UPDATES.items():
        canon[k] = v

    with open(CANON_PATH, "w", encoding="utf-8") as f:
        json.dump(canon, f, indent=2, ensure_ascii=False)

    print(
        f"Updated {len(PRE_867_UPDATES)} pre-867 titles in {CANON_PATH.name} (Total: {len(canon)})"
    )
    return canon


def update_symbol_generator_js(canon):
    js_content = JS_PATH.read_text(encoding="utf-8")

    # 1. Update HORIZON_0_TITLES set
    horizon_0_keys = [
        "h_roman_empire",
        "e_hre",
        "c_roma",
        "d_latium",
        "k_romagna",
        "k_papal_state",
        "c_byzantion",
        "e_byzantium",
        "c_tarragona",
        "c_barcelona",
        "d_barcelona",
        "c_metz",
        "d_upper_lorraine",
        "k_lotharingia",
        "c_aachen",
        "c_trier",
        "c_cologne",
        "c_paris",
        "c_alexandria",
        "d_alexandria",
        "c_antioch",
        "d_antioch",
        "c_jerusalem",
        "c_lviv",
        "c_szekesfehervar",
        "c_milano",
        "d_lombardy",
        "k_italy",
        "c_venezia",
        "d_venice",
        "c_ravenna",
        "d_ravenna",
        "c_mainz",
        "c_athens",
        "d_athens",
        "c_thessaloniki",
        "d_thessalonika",
        "d_wessex",
        "c_wiltshire",
        "c_kent",
        "d_canterbury",
        "k_danelaw",
        "c_york",
        "k_moravia",
        "c_kyiv",
        "k_asturias",
        "k_leon",
        "c_leon",
    ]

    h0_str = (
        "  const HORIZON_0_TITLES = new Set([\n    '"
        + "', '".join(sorted(set(horizon_0_keys)))
        + "'\n  ]);"
    )
    js_content = re.sub(
        r"  const HORIZON_0_TITLES = new Set\(\[[^\]]+\]\);",
        h0_str,
        js_content,
        flags=re.DOTALL,
    )

    # 2. Update embedded CANONICAL_HERALDRY in symbol_generator.js
    min_canon_json = json.dumps(canon, separators=(",", ":"))
    js_content = re.sub(
        r"const CANONICAL_HERALDRY = \{.*?\};",
        f"const CANONICAL_HERALDRY = {min_canon_json};",
        js_content,
        count=1,
    )

    # 3. Add explicit high historical title handlers in analyzeTitle
    additional_handlers = """
    if (key === 'c_paris') {
      return {
        medium: 'bulla_seal',
        field: 'gules',
        ordinary: 'solid',
        charges: ['ship'],
        chargeCount: 1,
        chargeColor: PALETTE.argent,
        blazonTarr: 'In Keiser-Rôt ein silbern Schiff van den Nautae Parisiaci mit geschwelltem Segel',
        blazonEn: 'Gules, an ancient nef Argent with sail set (Nautae Parisiaci)',
        legend: '+ S. MAGISTRATVS • PARISIORVM • CIVITAS •',
        source: 'Historical Pre-867 Attestation (Nautae Parisiaci)'
      };
    }

    if (key === 'c_milano' || key === 'd_lombardy' || key === 'k_italy') {
      return {
        medium: tier === 'duchy' ? 'notitia_scutum' : (tier === 'kingdom' ? 'gonfanon' : 'bulla_seal'),
        field: 'gules',
        ordinary: 'solid',
        charges: ['crown'],
        chargeCount: 1,
        chargeColor: PALETTE.or,
        blazonTarr: 'In Keiser-Rôt die goldene Eiserne Krône van Longobardjen mit heiligem Nâgel',
        blazonEn: 'Gules, the Iron Crown of Lombardy Or (Corona Ferrea)',
        legend: '+ S. MAGISTRATVS • MEDIOLANENSIS •',
        source: 'Historical Pre-867 Attestation (Corona Ferrea)'
      };
    }

    if (key === 'c_aachen') {
      return {
        medium: 'bulla_seal',
        field: 'or',
        ordinary: 'solid',
        charges: ['alerion'],
        chargeCount: 1,
        chargeColor: PALETTE.sable,
        blazonTarr: 'In Golt der swartze karolingische Palastadler van Charlemagne',
        blazonEn: 'Or, an eagle displayed Sable (Charlemagne Palatine Reichsadler)',
        legend: '+ S. MAGISTRATVS • AQVISGRANENSIS • PALATII •',
        source: 'Historical Pre-867 Attestation (Palatine Reichsadler 800 AD)'
      };
    }

    if (key === 'c_venezia' || key === 'd_venice') {
      return {
        medium: tier === 'duchy' ? 'notitia_scutum' : 'bulla_seal',
        field: 'azure',
        ordinary: 'solid',
        charges: ['lion_rampant'],
        chargeCount: 1,
        chargeColor: PALETTE.or,
        blazonTarr: 'In Lâsûr der geflügelte Markus-Lôwe van Golt',
        blazonEn: 'Azure, the winged Lion of Saint Mark Or',
        legend: '+ PAX • TIBI • MARCE • EVANGELISTA • MEVS •',
        source: 'Historical Pre-867 Attestation (San Marco 828 AD)'
      };
    }

    if (key === 'c_ravenna' || key === 'd_ravenna') {
      return {
        medium: tier === 'duchy' ? 'notitia_scutum' : 'bulla_seal',
        field: 'or',
        ordinary: 'solid',
        charges: ['eagle_double'],
        chargeCount: 1,
        chargeColor: PALETTE.gules,
        blazonTarr: 'In Golt ein rôter doppelter Exarchats-Adler van Ravenna',
        blazonEn: 'Or, a double-headed eagle Gules of the Exarchate of Ravenna',
        legend: '+ S. MAGISTRATVS • RAVENNATIS • EXARCHATVS •',
        source: 'Historical Pre-867 Attestation (Exarchatus Ravennas)'
      };
    }

    if (key === 'c_antioch' || key === 'd_antioch') {
      return {
        medium: tier === 'duchy' ? 'notitia_scutum' : 'bulla_seal',
        field: 'azure',
        ordinary: 'solid',
        charges: ['cross_patriarchal'],
        chargeCount: 1,
        chargeColor: PALETTE.or,
        blazonTarr: 'In Lâsûr ein goldenes apostolisches Patriarchenkrütz van Zant Peter',
        blazonEn: 'Azure, an apostolic patriarchal cross Or',
        legend: '+ S. PATRIARCHATVS • ANTIOCHENVS •',
        source: 'Historical Pre-867 Attestation (Patriarchatus Antiochenus)'
      };
    }

    if (key === 'c_jerusalem' || key === 'k_jerusalem') {
      return {
        medium: tier === 'kingdom' ? 'gonfanon' : 'bulla_seal',
        field: 'gules',
        ordinary: 'solid',
        charges: ['cross_patriarchal'],
        chargeCount: 1,
        chargeColor: PALETTE.or,
        blazonTarr: 'In Keiser-Rôt das goldene Krütz van dem Heiligen Grabe',
        blazonEn: 'Gules, a patriarchal cross Or (Holy Sepulchre)',
        legend: '+ S. PATRIARCHATVS • HIEROSOLYMITANVS •',
        source: 'Historical Pre-867 Attestation (Crux Sancti Sepulchri)'
      };
    }

    if (key === 'd_wessex' || key === 'c_wiltshire') {
      return {
        medium: tier === 'duchy' ? 'notitia_scutum' : 'bulla_seal',
        field: 'gules',
        ordinary: 'solid',
        charges: ['dragon'],
        chargeCount: 1,
        chargeColor: PALETTE.or,
        blazonTarr: 'In Keiser-Rôt der goldene Drache van Wessex van Kûnic Alfred',
        blazonEn: 'Gules, the Golden Dragon of Wessex Or',
        legend: '+ S. DVCATVS • OCCIDENTALIVM • SAXONVM •',
        source: 'Historical Pre-867 Attestation (Golden Dragon of Wessex 752 AD)'
      };
    }

    if (key === 'c_kent' || key === 'd_canterbury') {
      return {
        medium: tier === 'duchy' ? 'notitia_scutum' : 'bulla_seal',
        field: 'gules',
        ordinary: 'solid',
        charges: ['horse_courant'],
        chargeCount: 1,
        chargeColor: PALETTE.argent,
        blazonTarr: 'In Keiser-Rôt das weisse Ros van Hengist und Horsa van Kent',
        blazonEn: 'Gules, a horse salient Argent (Invicta)',
        legend: '+ INVICTA • S. MAGISTRATVS • CANTII •',
        source: 'Historical Pre-867 Attestation (White Horse of Kent)'
      };
    }

    if (key === 'k_danelaw' || key === 'c_york') {
      return {
        medium: tier === 'kingdom' ? 'gonfanon' : 'bulla_seal',
        field: 'argent',
        ordinary: 'solid',
        charges: ['falcon_perched'],
        chargeCount: 1,
        chargeColor: PALETTE.sable,
        blazonTarr: 'In Silber der swartze Rabe van Ôdin van dem Gierten Hêre van 867',
        blazonEn: 'Argent, a raven displayed Sable (Hrafnsmerki of 867)',
        legend: '+ HRAFNSMERKI • SCANDIA • EBORACENSIS •',
        source: 'Historical 867 Attestation (Raven Banner of 867)'
      };
    }

    if (key === 'c_kyiv') {
      return {
        medium: 'bulla_seal',
        field: 'azure',
        ordinary: 'solid',
        charges: ['falcon_perched'],
        chargeCount: 1,
        chargeColor: PALETTE.or,
        blazonTarr: 'In Lâsûr der fürstliche Valke van Kîew van Askold und Dir',
        blazonEn: 'Azure, a falcon perched Or (Kievan Princely Falcon Tamga)',
        legend: '+ S. MAGISTRATVS • KIOVIENSIS •',
        source: 'Historical 867 Attestation (Princely Falcon Tamga)'
      };
    }

    if (key === 'c_athens' || key === 'd_athens') {
      return {
        medium: tier === 'duchy' ? 'notitia_scutum' : 'bulla_seal',
        field: 'azure',
        ordinary: 'solid',
        charges: ['column_roman'],
        chargeCount: 1,
        chargeColor: PALETTE.or,
        blazonTarr: 'In Lâsûr eine goldene rômische Sûle van Athen',
        blazonEn: 'Azure, a classical Roman column Or',
        legend: '+ S. MAGISTRATVS • ATHENIENSIS •',
        source: 'Historical Pre-867 Attestation (Theme of Hellas)'
      };
    }

    if (key === 'c_thessaloniki' || key === 'd_thessalonika') {
      return {
        medium: tier === 'duchy' ? 'notitia_scutum' : 'bulla_seal',
        field: 'gules',
        ordinary: 'solid',
        charges: ['sword_crossed'],
        chargeCount: 1,
        chargeColor: PALETTE.or,
        blazonTarr: 'In Keiser-Rôt zwên gekrützte goldene Swerte van Zant Demetrius',
        blazonEn: 'Gules, two swords in saltire Or of Saint Demetrius',
        legend: '+ S. THEMA • THESSALONICENSIS •',
        source: 'Historical Pre-867 Attestation (Theme of Thessalonica)'
      };
    }
"""

    # Insert additional handlers right after `key === 'c_byzantion'` block
    target = "legend: '+ BASILEIA • ROMAION • CONSTANTINOPOLIS •',\n        source: 'Historical Attestation (COA 442)'\n      };\n    }"
    if target in js_content:
        js_content = js_content.replace(target, target + "\n" + additional_handlers)
        print("Inserted pre-867 historical handlers into analyzeTitle successfully")
    else:
        print("ERROR: Target anchor for analyzeTitle not found")
        return False

    JS_PATH.write_text(js_content, encoding="utf-8")
    print(f"Updated {JS_PATH.name} successfully")
    return True


def main():
    canon = update_canonical_json()
    update_symbol_generator_js(canon)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
pipeline_stage5_sound_laws.py

Stage 5 of the Tarraconian Barony-Tier Toponymic Naming Pipeline (v2):
Applies Tarraconian Chancellery Orthographic & Sound Laws, generates Daughter Dialect
overlays (Alpine-Tarraconian, Croato-Tarraconian, Ungwârer), computes IPA via
`resolve_barony_titles.generate_tarraconian_ipa`, and validates all 10,239 occupied
baronies against `audit_phonotactics_titles.check_title_phonotactics` + strict
Chancellery character hygiene.

Reads:
  - data/pipeline_stage4_mediated.json
  - data/barony_toponymic_profiles.json

Emits:
  - data/pipeline_stage5_validated.json
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

from audit_phonotactics_titles import check_title_phonotactics
from resolve_barony_titles import enforce_tarraconian_sound_laws, generate_tarraconian_ipa

REPO_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_DIR / "data"

ALLOWED_CHANCELLERY_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzâêîôûÂÊÎÔÛäöüÄÖÜïëÏ '-")
PRESERVE_NFC_VOWELS = set("âêîôûÂÊÎÔÛäöüÄÖÜïëÏ")

EXOTIC_CHAR_MAP: dict[str, str] = {
    # IPA / Berber / West African Latin extensions
    "ɣ": "g", "Ɣ": "G",
    "ɔ": "o", "Ɔ": "O",
    "ɛ": "e", "Ɛ": "E",
    "ə": "e", "Ə": "E",
    "ɗ": "d", "Ɗ": "D",
    "ɓ": "b", "Ɓ": "B",
    "ƙ": "k", "Ƙ": "K",
    "ŋ": "ng", "Ŋ": "Ng",
    "ħ": "h", "Ħ": "H",
    "ʻ": "", "ʼ": "", "ʹ": "", "ˈ": "", "ˌ": "", "ʔ": "", "ʿ": "", "ʾ": "",
    # Pinyin tone carons / graves
    "ǎ": "a", "Ǎ": "A", "ǐ": "i", "Ǐ": "I", "ǒ": "o", "Ǒ": "O", "ǔ": "u", "Ǔ": "U",
    "ǜ": "ü", "Ǜ": "Ü", "ǘ": "ü", "Ǘ": "Ü", "ǖ": "ü", "Ǖ": "Ü", "ǚ": "ü", "Ǚ": "Ü",
    # Old English / Celtic / Germanic / Nordic
    "ǣ": "ê", "Ǣ": "Ê", "æ": "ê", "Æ": "Ê", "å": "ô", "Å": "Ô", "ø": "ö", "Ø": "Ö",
    "ǫ": "o", "Ǫ": "O", "þ": "th", "Þ": "Th", "ð": "d", "Ð": "D",
    # Slavic yers / nasals / liquids
    "ĭ": "i", "Ĭ": "I", "ŭ": "u", "Ŭ": "U", "ľ": "l", "Ľ": "L", "ĺ": "l", "Ĺ": "L",
    "ŕ": "r", "Ŕ": "R", "ň": "n", "Ň": "N", "ď": "d", "Ď": "D", "ť": "t", "Ť": "T",
    "ǧ": "g", "Ǧ": "G", "ė": "e", "Ė": "E",
    # Indic IAST
    "ṇ": "n", "Ṇ": "N", "ṅ": "ng", "Ṅ": "Ng", "ṃ": "m", "Ṃ": "M", "ṁ": "m", "Ṁ": "M",
    "ṛ": "r", "Ṛ": "R", "ṝ": "r", "ḷ": "l", "ẏ": "j", "Ẏ": "J", "ś": "sch", "Ś": "Sch", "ṣ": "sch", "Ṣ": "Sch",
    "ṓ": "ô", "Ṓ": "Ô",
    # Vietnamese
    "đ": "d", "Đ": "D", "ư": "ü", "Ư": "Ü", "ơ": "ö", "Ơ": "Ö",
    "ả": "a", "Ả": "A", "ạ": "a", "Ạ": "A", "ằ": "a", "ắ": "a", "ẳ": "a", "ẵ": "a", "ặ": "a",
    "ầ": "â", "ấ": "â", "ẩ": "â", "ẫ": "â", "ậ": "â",
    "ề": "ê", "ế": "ê", "ể": "ê", "ễ": "ê", "ệ": "ê",
    "ỉ": "i", "ị": "i", "ỏ": "o", "ọ": "o",
    "ồ": "ô", "ố": "ô", "ổ": "ô", "ỗ": "ô", "ộ": "ô",
    "ờ": "ö", "ớ": "ö", "ở": "ö", "ỡ": "ö", "ợ": "ö",
    "ủ": "u", "ụ": "u", "ừ": "ü", "ứ": "ü", "ử": "ü", "ữ": "ü", "ự": "ü",
    "ỷ": "i", "ỵ": "i", "ỹ": "i",
    # Semitic / Nigerian / Yoruba / Kurdish underdots & breves
    "ọ": "o", "Ọ": "O", "ẹ": "e", "Ẹ": "E", "ị": "i", "Ị": "I", "ụ": "u", "Ụ": "U",
    "ḥ": "h", "Ḥ": "H", "ṭ": "t", "Ṭ": "T", "ṣ": "s", "Ṣ": "S", "ḍ": "d", "Ḍ": "D", "ẓ": "z", "Ẓ": "Z",
    "ă": "e", "Ă": "E", "ğ": "g", "Ğ": "G", "ı": "i", "İ": "I",
}

DAUGHTER_DIALECTS = {"Alpine-Tarraconian", "Croato-Tarraconian", "Ungwârer"}


def pre_normalize_for_chancellery(s: str, is_sinosphere: bool = False, macro_family: str = "") -> str:
    """Clean exotic characters, punctuation, and illicit digraphs BEFORE sound laws."""
    if not s:
        return ""
    out = unicodedata.normalize("NFC", s.strip())

    # Convert St. / Saint -> Zant- cleanly
    out = re.sub(r"\bSt\.(?:\s+|-)?", "Zant-", out)
    out = re.sub(r"\bSt\s+(?=[A-Z])", "Zant-", out)
    out = re.sub(r"\bSaint[\s\-]+", "Zant-", out, flags=re.I)

    # Disambiguate Bosnian/Croatian Đ (Dsch) vs Vietnamese Đ (D)
    if macro_family == "south_slavic":
        out = out.replace("đ", "dsch").replace("Đ", "Dsch")

    # Apply explicit EXOTIC_CHAR_MAP
    out = "".join(EXOTIC_CHAR_MAP.get(ch, ch) for ch in out)

    # Strip any residual combining marks while preserving canonical Tarraconian vowels
    res_chars: list[str] = []
    for ch in out:
        if ch in PRESERVE_NFC_VOWELS or ch in ALLOWED_CHANCELLERY_CHARS:
            res_chars.append(ch)
        else:
            decomp = unicodedata.normalize("NFD", ch)
            stripped = "".join(c for c in decomp if unicodedata.category(c) != "Mn")
            for sc in stripped:
                res_chars.append(EXOTIC_CHAR_MAP.get(sc, sc))
    out = "".join(res_chars)

    # Remove dots/punctuation not in ALLOWED_CHANCELLERY_CHARS
    out = "".join(c if c in ALLOWED_CHANCELLERY_CHARS else " " for c in out)
    out = re.sub(r"\s{2,}", " ", out).strip()

    # Non-Sinosphere bare 'q' (not 'qu') -> 'k' so enforce_tarraconian_sound_laws won't turn Q- into Tsch-
    if not is_sinosphere:
        out = re.sub(r"[Qq](?![uU])", lambda m: "K" if m.group(0).isupper() else "k", out)

    # English preposition hygiene if any straggled inside NTR compound
    out = re.sub(r"\b(?:upon|under|on|the|of)\b", "", out, flags=re.I)
    out = re.sub(r"\s{2,}", " ", out).strip(" -")
    return out


def apply_full_stage5_sound_laws(
    raw_form: str,
    is_sinosphere: bool = False,
    macro_family: str = "",
) -> str:
    """Apply Stage 5 pre-normalization + canonical `enforce_tarraconian_sound_laws` + strict audit cleanup."""
    s = pre_normalize_for_chancellery(raw_form, is_sinosphere=is_sinosphere, macro_family=macro_family)
    if not s:
        return ""

    # Sinosphere Pinyin X before i/ü -> Sch
    if is_sinosphere:
        s = re.sub(r"\b[Xx](?=[iuüîû])", lambda m: "Sch" if m.group(0).isupper() else "sch", s)

    # Canonical Chancellery normalizer from resolve_barony_titles.py
    s = enforce_tarraconian_sound_laws(s)

    # Extra Auslautverhärtung, double-vowel circumflex alignment & cluster repair
    s = re.sub(r"burh\b", "burch", s)
    s = re.sub(r"mynster\b", "munster", s)
    s = re.sub(r"\b([NnMm])([AEIOU][a-z]{2,})", lambda m: m.group(1).upper() + m.group(2).lower(), s)
    s = re.sub(r"\b([A-Za-z]{1,2})([A-Z])(?=[a-z])", lambda m: m.group(1) + m.group(2).lower() if m.group(1) != "IJ" else m.group(0), s)
    s = re.sub(r"-tscho\b", "-Tscho", s)
    s = re.sub(r"\bAa(?=[a-z])", "Â", s)
    s = re.sub(r"aa", "â", s)
    s = re.sub(r"oo", "ô", s)
    s = re.sub(r"(?<![qQ])uu", "û", s)
    s = re.sub(r"([a-zâêîôûäöü])\1\1+", r"\1\1", s, flags=re.I)
    s = re.sub(r"schsch", "sch", s, flags=re.I)
    s = re.sub(r"(?:tz|ts)tsch", "tsch", s, flags=re.I)
    s = re.sub(r"tschtsch", "tsch", s, flags=re.I)
    s = re.sub(r"burchburch\b", "burch", s, flags=re.I)
    s = re.sub(r"berchberch\b", "berch", s, flags=re.I)
    s = re.sub(r"tzburch\b", "tzburch", s, flags=re.I)
    # Fix any surviving 'sh' not in -heim/-hûsen
    s = re.sub(r"(?<!c)[Ss]h(?!eim|ûsen)", lambda m: "Sch" if m.group(0)[0].isupper() else "sch", s)
    # Fix any surviving 'eo' not after g/n/th (flagged by audit_phonotactics_titles.py)
    s = re.sub(r"(?<!g)(?<!n)(?<!th)(?<!G)(?<!N)(?<!Th)eo", "ô", s)
    # Initial Ts- -> Z-
    s = re.sub(r"\b[Tt]s(?!ch)", lambda m: "Z" if m.group(0)[0].isupper() else "z", s)
    # Strip any non-allowed chars one last time
    s = "".join(c for c in s if c in ALLOWED_CHANCELLERY_CHARS)
    s = re.sub(r"\s{2,}", " ", out_s := s).strip(" -'")
    if out_s and out_s[0].islower():
        out_s = out_s[0].upper() + out_s[1:]
    return out_s


def build_daughter_dialect_variant(
    tarr_name: str,
    tarr_ipa: str,
    dialect: str,
) -> dict[str, str]:
    """
    Generate authentic regional spoken / orthographic overlay per tarraconian_linguistics_guide.md § 6:
      - Alpine-Tarraconian: û -> [yː], final -n nasalization, softened [ts] -> [dz~s]
      - Croato-Tarraconian: initial w- -> [v], Croatian/Dinaric overlay note
      - Ungwârer: preservation of circumflex long vowels + Magyar phonetic alignment
    """
    local_ipa = tarr_ipa
    local_form = tarr_name
    note = ""
    if dialect == "Alpine-Tarraconian":
        local_ipa = local_ipa.replace("uː", "yː").replace("n]", "ŋ]")
        note = "Gallo-Italic vocalic fronting (û -> [yː]) and final nasalization (-n -> [ŋ])."
    elif dialect == "Croato-Tarraconian":
        local_ipa = re.sub(r"^\[ˈ?w", lambda m: m.group(0)[:-1] + "v", local_ipa)
        note = "South Slavic labiodental onset (w- -> [v]) and Dinaric march register."
    elif dialect == "Ungwârer":
        note = "Germano-Magyar Carpathian register preserving circumflex length directly onto Old Hungarian long vowels."
    return {
        "dialect": dialect,
        "local_form": local_form,
        "local_ipa": local_ipa,
        "phonological_note": note,
    }


def run_stage5() -> dict[str, Any]:
    with open(DATA_DIR / "pipeline_stage4_mediated.json", "r", encoding="utf-8") as f:
        s4 = json.load(f)["baronies"]
    with open(DATA_DIR / "barony_toponymic_profiles.json", "r", encoding="utf-8") as f:
        profiles = json.load(f)["baronies"]

    audit_failures: list[dict[str, Any]] = []
    dialect_counts: Counter[str] = Counter()
    changed_count = 0

    stage5_baronies: dict[str, dict[str, Any]] = {}

    for bk in sorted(s4.keys()):
        r4 = s4[bk]
        if not r4["is_occupied"]:
            stage5_baronies[bk] = {
                "barony_key": bk,
                "is_occupied": False,
                "final_record": r4["final_record"],
            }
            continue

        is_sino = bool(r4.get("is_sinosphere_scope", False))
        macro_fam = r4.get("coinage_morphology_family", "")

        raw_hist = r4["tarr_hist_pre_law"]
        raw_dir = r4["tarr_direct_pre_law"]

        final_hist = apply_full_stage5_sound_laws(raw_hist, is_sinosphere=is_sino, macro_family=macro_fam)
        final_dir = apply_full_stage5_sound_laws(raw_dir, is_sinosphere=is_sino, macro_family=macro_fam)

        if not final_hist:
            final_hist = final_dir or apply_full_stage5_sound_laws(bk.replace("b_", ""), is_sinosphere=is_sino)
        if not final_dir:
            final_dir = final_hist

        if final_hist != raw_hist:
            changed_count += 1

        ipa = generate_tarraconian_ipa(final_hist)

        # Automated phonotactic check using project canonical auditor on BOTH tarr_hist & tarr_direct
        issues = check_title_phonotactics(final_hist, bk, "stage5_hist") + check_title_phonotactics(final_dir, bk, "stage5_direct")
        disallowed = [ch for ch in (final_hist + final_dir) if ch not in ALLOWED_CHANCELLERY_CHARS]
        if issues or disallowed:
            audit_failures.append({
                "barony_key": bk,
                "name": final_hist,
                "direct": final_dir,
                "issues": issues,
                "disallowed": disallowed,
            })

        # Daughter dialect overlay if any stratum or 1194 incumbent belongs to Alpine/Croato/Ungwârer
        prof = profiles[bk]
        c1194 = prof.get("c1194")
        active_dialect = next(
            (c for c in (r4["coinage_culture"], c1194, r4["transmission_culture"], r4["substrate_culture"]) if c in DAUGHTER_DIALECTS),
            None,
        )
        dialect_var = None
        if active_dialect:
            dialect_counts[active_dialect] += 1
            dialect_var = build_daughter_dialect_variant(final_hist, ipa, active_dialect)

        stage5_baronies[bk] = {
            **r4,
            "tarr_direct": final_dir,
            "tarr_hist": final_hist,
            "b_ipa": ipa,
            "daughter_dialect_variant": dialect_var,
            "phonotactic_issues": issues,
        }

    payload = {
        "metadata": {
            "schema_version": "1.0.0",
            "pipeline_stage": "stage_5_sound_laws_ipa_and_validation",
            "total_baronies": len(stage5_baronies),
            "occupied_baronies": 10239,
            "unoccupied_baronies": 1058,
            "sound_law_normalizations_applied": changed_count,
            "total_phonotactic_audit_failures": len(audit_failures),
            "audit_failures_sample": audit_failures[:10],
            "daughter_dialect_counts": dict(dialect_counts),
        },
        "baronies": stage5_baronies,
    }
    return payload


def main() -> None:
    payload = run_stage5()
    out_path = DATA_DIR / "pipeline_stage5_validated.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    print(f"Wrote {out_path} ({out_path.stat().st_size / (1024*1024):.2f} MB)")
    print("Stage 5 metadata:", json.dumps(payload["metadata"], indent=2))


if __name__ == "__main__":
    main()

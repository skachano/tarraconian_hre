#!/usr/bin/env python3
"""
build_sinosphere_calques_db.py

Parses sinosphere_titles_and_characters_1154.md, data/sinosphere_kanji_tarraconian.json,
and sinosphere_phonetics_and_transcription_guide_1154.md to build the comprehensive
Sinosphere Hanzi & Calque database (data/sinosphere_hanzi_calques.json) covering all 821
Sinosphere titles across Empires, Kingdoms, Duchies, and Counties.
"""

import json
import re
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
SINO_MD = REPO_DIR / "sinosphere_titles_and_characters_1154.md"
KANJI_JSON = REPO_DIR / "data" / "sinosphere_kanji_tarraconian.json"
OUT_JSON = REPO_DIR / "data" / "sinosphere_hanzi_calques.json"


def clean_str(s: str) -> str:
    if not s:
        return ""
    return s.replace("**", "").replace("*", "").replace("`", "").strip()


def main():
    print("Building Sinosphere Hanzi & Calque Database...")

    with open(KANJI_JSON, "r", encoding="utf-8") as f:
        kanji_list = json.load(f)
    k_map = {k["char"]: k for k in kanji_list}

    with open(SINO_MD, "r", encoding="utf-8") as f:
        text = f.read()

    # 1. Parse Section 5 Anachronisms (61 titles)
    sec5_part = text[text.find("## 5. Master Register") :]
    sec5_matches = re.findall(
        r"\|\s*\d+\s*\|\s*`(c_[^`]+)`\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|",
        sec5_part,
    )
    sec5_data = {}
    for m in sec5_matches:
        ck = m[0].strip()
        sec5_data[ck] = {
            "name": clean_str(m[1]),
            "hanzi": clean_str(m[2]),
            "kingdom_desc": clean_str(m[3]),
            "rationale": clean_str(m[4]),
            "substrate": clean_str(m[5]),
            "tarr": clean_str(m[6]),
            "justification": clean_str(m[7]),
        }
    print(f"  Parsed {len(sec5_data)} Section 5 anachronism resolutions.")

    # 2. Parse Section 2 & 3 Counties (620 titles)
    sec2_3_part = text[: text.find("## 5. Master Register")]
    county_matches = re.findall(
        r"\|\s*\d+\s*\|\s*`(c_[^`]+)`\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|\s*([^|]*)\|",
        sec2_3_part,
    )
    print(f"  Parsed {len(county_matches)} county rows from Sections 2 & 3.")

    # 3. Parse Empires (9), Kingdoms (39), Duchies (153)
    empires = re.findall(
        r"###\s+[\d\.]+\s+Empire\s+of\s+([^(]+)\(`(e_[^`]+)`\s*/\s*([^)]+)\)\s*(?:—\s*(?:(?:Keiserrîch|Gubernat)[^*]*—\s*)?\*\*([^*]+)\*\*)?",
        text,
    )
    kingdoms = re.findall(
        r"####\s+[\d\.]+\s+Kingdom\s+of\s+([^(]+)\(`(k_[^`]+)`\s*/\s*([^)]+)\)\s*(?:—\s*(?:Kûnincrich[^*]*—\s*)?\*\*([^*]+)\*\*)?",
        text,
    )
    duchies = re.findall(
        r"#####\s+Duchy\s+of\s+([^(]+)\(`(d_[^`]+)`\s*/\s*([^)]+)\)\s*(?:—\s*(?:(?:Gubernat|Keisermarch)[^*]*—\s*)?\*\*([^*]+)\*\*)?",
        text,
    )

    result_db = {}

    def analyze_characters(hanzi_str: str):
        char_list = []
        for ch in hanzi_str:
            if ch in k_map:
                k = k_map[ch]
                char_list.append(
                    {
                        "char": ch,
                        "pinyin": k.get("pinyin", ""),
                        "jp": k.get("jp", ""),
                        "kr": k.get("kr", ""),
                        "meaning": k.get("meaning", ""),
                        "morpheme": k.get("tarr_morpheme", ""),
                        "ipa": k.get("tarr_ipa", ""),
                        "role": k.get("tarr_role", ""),
                        "category": k.get("cat_name", ""),
                    }
                )
        return char_list

    def build_synthesis(name, hanzi, tarr_short, char_list, justification, substrate):
        if justification:
            synth = justification
            if substrate and substrate not in synth:
                synth += f" Geographically anchored to {substrate}."
            return synth

        morpheme_parts = []
        for c in char_list:
            m_short = c["meaning"].split("/")[0].strip()
            ch = c["char"]
            py = c["pinyin"]
            morph = c["morpheme"]
            morpheme_parts.append(f"{ch} ({py}, '{m_short}' → {morph})")

        morpheme_str = " + ".join(morpheme_parts) if morpheme_parts else ""

        synth = f"Calqued root-for-root from CJK {hanzi} ({name}) into Tarraconian High German {tarr_short}."
        if morpheme_str:
            synth += f" Morpheme breakdown: {morpheme_str}."
        return synth

    # Add Empires
    for e in empires:
        name = clean_str(e[0])
        key = clean_str(e[1])
        hanzi = clean_str(e[2])
        tarr = clean_str(e[3]) or name
        chars = analyze_characters(hanzi)
        synth = build_synthesis(name, hanzi, tarr, chars, "", "")
        result_db[key] = {
            "key": key,
            "name": name,
            "hanzi": hanzi,
            "tier": "empire",
            "tarr": tarr,
            "status": "Classical Sinosphere Realm",
            "substrate": "",
            "justification": "",
            "characters": chars,
            "synthesis": synth,
        }

    # Add Kingdoms
    for k in kingdoms:
        name = clean_str(k[0])
        key = clean_str(k[1])
        hanzi = clean_str(k[2])
        tarr = clean_str(k[3]) or name
        chars = analyze_characters(hanzi)
        synth = build_synthesis(name, hanzi, tarr, chars, "", "")
        result_db[key] = {
            "key": key,
            "name": name,
            "hanzi": hanzi,
            "tier": "kingdom",
            "tarr": tarr,
            "status": "Classical Sinosphere Kingdom",
            "substrate": "",
            "justification": "",
            "characters": chars,
            "synthesis": synth,
        }

    # Add Duchies
    for d in duchies:
        name = clean_str(d[0])
        key = clean_str(d[1])
        hanzi = clean_str(d[2])
        tarr = clean_str(d[3]) or name
        chars = analyze_characters(hanzi)
        synth = build_synthesis(name, hanzi, tarr, chars, "", "")
        result_db[key] = {
            "key": key,
            "name": name,
            "hanzi": hanzi,
            "tier": "duchy",
            "tarr": tarr,
            "status": "Classical Sinosphere Governorship",
            "substrate": "",
            "justification": "",
            "characters": chars,
            "synthesis": synth,
        }

    # Add Counties
    for c in county_matches:
        key = clean_str(c[0])
        name = clean_str(c[1])
        hanzi = clean_str(c[2])
        trad = clean_str(c[3])
        tarr = clean_str(c[4])
        # Clean prefix "Magistrat van " if present
        tarr_short = re.sub(r"^(?:Magistrat|Gubernat|Kûnincrich|Keiserrîch)\s+van\s+(?:den\s+|dem\s+|der\s+)?", "", tarr).strip()
        status = clean_str(c[6])

        sec5_info = sec5_data.get(key)
        substrate = sec5_info["substrate"] if sec5_info else ""
        justification = sec5_info["justification"] if sec5_info else ""
        if sec5_info and not tarr_short:
            tarr_short = re.sub(r"^(?:Magistrat|Gubernat|Kûnincrich|Keiserrîch)\s+van\s+(?:den\s+|dem\s+|der\s+)?", "", sec5_info["tarr"]).strip()

        chars = analyze_characters(hanzi)
        synth = build_synthesis(name, hanzi, tarr_short, chars, justification, substrate)

        result_db[key] = {
            "key": key,
            "name": name,
            "hanzi": hanzi,
            "trad": trad if trad != "—" else "",
            "tier": "county",
            "tarr": tarr_short,
            "status": "Tier 3 Anachronism (Resolved via Option B)" if sec5_info else status,
            "substrate": substrate,
            "justification": justification,
            "characters": chars,
            "synthesis": synth,
        }

    print(f"Total compiled Sinosphere titles in database: {len(result_db)}")

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(result_db, f, indent=2, ensure_ascii=False)

    print(f"Saved {OUT_JSON} ({OUT_JSON.stat().st_size / 1024:.1f} KB).")


if __name__ == "__main__":
    main()

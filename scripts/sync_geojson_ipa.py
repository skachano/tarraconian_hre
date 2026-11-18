#!/usr/bin/env python3
"""
sync_geojson_ipa.py

Synchronizes updated Tarraconian names and IPA transcriptions from
tarraconian_titles_1059.md and hre_de_jure_and_archdioceses_1059.md into:
- data/ck3_counties.geojson
- data/ck3_title_tree.json
- docs/data/ (via build_webapp.py)
"""

import json
import re
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_DIR / "data"
DOCS_DIR = REPO_DIR / "docs"


def parse_markdown_titles_and_ipa():
    """Extracts title names and IPA transcriptions from documentation."""
    p_titles = REPO_DIR / "tarraconian_titles_1059.md"
    p_hre = REPO_DIR / "hre_de_jure_and_archdioceses_1059.md"

    c_ipa, d_ipa, k_ipa, e_ipa = {}, {}, {}, {}
    c_tarr, d_tarr, k_tarr, e_tarr = {}, {}, {}, {}

    # 1. Parse tarraconian_titles_1059.md
    if p_titles.exists():
        text = p_titles.read_text(encoding="utf-8")
        for line in text.splitlines():
            line_s = line.strip()

            # Kingdom table in Section 2
            m_k = re.match(
                r"^\|\s*\d+\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*`([a-zA-Z0-9_\-]+)`\s*\|\s*([^|]+)\|\s*([^|]+)\|",
                line_s,
            )
            if m_k:
                kk = m_k.group(2).strip()
                col3 = m_k.group(3).strip()
                col4 = m_k.group(4).strip()
                m_hist = re.search(r"1059 Hist:\s*\*\*([^*]+)\*\*", col3)
                m_bold = re.search(r"\*\*([^*]+)\*\*", col3)
                if m_hist:
                    t_val = (
                        m_hist.group(1)
                        .replace("Kûnincrich van ", "")
                        .replace("Keiserrîch van ", "")
                        .strip()
                    )
                    k_tarr[kk] = t_val
                elif m_bold:
                    t_val = (
                        m_bold.group(1)
                        .replace("Kûnincrich van ", "")
                        .replace("Keiserrîch van ", "")
                        .strip()
                    )
                    k_tarr[kk] = t_val
                m_brackets = re.findall(r"\[([^\]]+)\]", col4)
                for b in m_brackets:
                    b_clean = b.strip("`")
                    if any(c in b_clean for c in "ˈˌːɛɔʊɪʏøœ̃ŋʃʒθðçɣχʁʔɲʎ") or (
                        "." in b_clean and len(b_clean.split()) == 1
                    ):
                        k_ipa[kk] = f"[{b_clean}]"
                        break

            # Kingdom headers in Section 3
            if line_s.startswith("### 3."):
                m_kh = re.match(
                    r"^###\s+3\.\d+\s+Kingdom.*?\(`([a-zA-Z0-9_\-]+)`\)", line_s
                )
                if m_kh:
                    kk = m_kh.group(1).strip()
                    if kk not in k_ipa:
                        m_brackets = re.findall(r"\[([^\]]+)\]", line_s)
                        for b in m_brackets:
                            b_clean = b.strip("`")
                            if any(
                                c in b_clean for c in "ˈˌːɛɔʊɪʏøœ̃ŋʃʒθðçɣχʁʔɲʎ"
                            ) or ("." in b_clean and len(b_clean.split()) == 1):
                                k_ipa[kk] = f"[{b_clean}]"
                                break

            # Duchy bullets in Section 3
            if any(
                line_s.startswith(x)
                for x in [
                    "* **Duchy",
                    "* **Frontier Duchy",
                    "* **March",
                    "* **Metropolitan",
                ]
            ):
                all_keys = re.findall(r"`([dx]_[a-zA-Z0-9_\-]+)`", line_s)
                m_brackets = re.findall(r"\[([^\]]+)\]", line_s)
                for b in m_brackets:
                    b_clean = b.strip("`")
                    if any(
                        b_clean.startswith(x)
                        for x in [
                            "1059",
                            "1122",
                            "1142",
                            "1154",
                            "1171",
                            "1194",
                            "HRE",
                            "d_",
                            "c_",
                            "k_",
                            "e_",
                            "b_",
                        ]
                    ):
                        continue
                    if any(
                        c in b_clean for c in "ˈˌːɛɔʊɪʏøœ̃ŋʃʒθðçɣχʁʔɲʎ"
                    ) or ("." in b_clean and len(b_clean.split()) == 1):
                        for dk in all_keys:
                            d_ipa[dk] = f"[{b_clean}]"
                        break

            # County bullets in Section 3
            m_c = re.match(
                r"^\s*\*\s*`(c_[a-zA-Z0-9_\-]+)`\s*(.*?)\s*\$\\rightarrow\$\s*(.*?)$",
                line_s,
            )
            if m_c:
                ck = m_c.group(1).strip()
                rest = m_c.group(3)
                m_brackets = re.findall(r"\[([^\]]+)\]", rest)
                for b in m_brackets:
                    b_clean = b.strip("`")
                    if any(
                        b_clean.startswith(x)
                        for x in [
                            "1059",
                            "1122",
                            "1142",
                            "1154",
                            "1171",
                            "1194",
                            "HRE",
                            "d_",
                            "c_",
                            "k_",
                            "e_",
                            "b_",
                        ]
                    ):
                        continue
                    if any(
                        c in b_clean for c in "ˈˌːɛɔʊɪʏøœ̃ŋʃʒθðçɣχʁʔɲʎ"
                    ) or ("." in b_clean and len(b_clean.split()) == 1):
                        c_ipa[ck] = f"[{b_clean}]"
                        break

    # 2. Parse hre_de_jure_and_archdioceses_1059.md for all 47 Empire IPAs and names
    if p_hre.exists():
        text_hre = p_hre.read_text(encoding="utf-8")
        for line in text_hre.splitlines():
            line_s = line.strip()
            m_e = re.match(
                r"^\|\s*\d+\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*`([a-zA-Z0-9_\-]+)`\s*\|\s*\*\*([^*]+)\*\*\s*\|\s*`([^`]+)`",
                line_s,
            )
            if m_e:
                ek = m_e.group(2).strip()
                e_tarr[ek] = m_e.group(3).strip()
                e_ipa[ek] = m_e.group(4).strip()

    return (c_ipa, d_ipa, k_ipa, e_ipa), (c_tarr, d_tarr, k_tarr, e_tarr)


def sync_all():
    (c_ipa, d_ipa, k_ipa, e_ipa), (c_tarr, d_tarr, k_tarr, e_tarr) = (
        parse_markdown_titles_and_ipa()
    )

    print("Parsed documentation IPAs:")
    print(f"  • Counties: {len(c_ipa)}")
    print(f"  • Duchies: {len(d_ipa)}")
    print(f"  • Kingdoms: {len(k_ipa)}")
    print(f"  • Empires: {len(e_ipa)}")

    # 1. Update data/ck3_counties.geojson
    counties_path = DATA_DIR / "ck3_counties.geojson"
    print(f"Updating {counties_path.name}...")
    with open(counties_path, "r", encoding="utf-8") as f:
        counties_fc = json.load(f)

    c_updated = 0
    for feat in counties_fc["features"]:
        p = feat["properties"]
        ck = p.get("county")
        dk = p.get("duchy")
        kk = p.get("kingdom")
        ek = p.get("empire")

        if ck in c_ipa:
            p["c_ipa"] = c_ipa[ck]
        if dk and dk in d_ipa:
            p["d_ipa"] = d_ipa[dk]
        if kk and kk in k_ipa:
            p["k_ipa"] = k_ipa[kk]
        if ek and ek in e_ipa:
            p["e_ipa"] = e_ipa[ek]

        # Specific title corrections
        if ck == "c_puigcerda" and "Tzerdanje" in p.get("tarr", ""):
            p["tarr"] = p["tarr"].replace("Tzerdanje", "Zerdanje")
            p["tarr_direct"] = p.get("tarr_direct", "").replace(
                "Tzerdanje", "Zerdanje"
            )
            p["tarr_hist"] = p.get("tarr_hist", "").replace(
                "Tzerdanje", "Zerdanje"
            )
        if dk == "d_et_cyprus" and "Tzîpern" in p.get("d_tarr", ""):
            p["d_tarr"] = p["d_tarr"].replace("Tzîpern", "Zîpern")
            p["d_tarr_direct"] = p.get("d_tarr_direct", "").replace(
                "Tzîpern", "Zîpern"
            )
            p["d_tarr_hist"] = p.get("d_tarr_hist", "").replace(
                "Tzîpern", "Zîpern"
            )

        c_updated += 1

    with open(counties_path, "w", encoding="utf-8") as f:
        json.dump(counties_fc, f, separators=(",", ":"), ensure_ascii=False)
    print(f"-> Updated {c_updated} county features in {counties_path.name}.")

    # 2. Update data/ck3_title_tree.json
    tree_path = DATA_DIR / "ck3_title_tree.json"
    print(f"Updating {tree_path.name}...")
    with open(tree_path, "r", encoding="utf-8") as f:
        tree = json.load(f)

    for ek, e_node in tree.items():
        if ek in e_ipa:
            e_node["ipa"] = e_ipa[ek]
        if ek in e_tarr:
            e_node["tarr"] = e_tarr[ek]

        for kk, k_node in e_node.get("kingdoms", {}).items():
            if kk in k_ipa:
                k_node["ipa"] = k_ipa[kk]
            if kk in k_tarr:
                k_node["tarr"] = k_tarr[kk]

            for dk, d_node in k_node.get("duchies", {}).items():
                if dk in d_ipa:
                    d_node["ipa"] = d_ipa[dk]
                if dk == "d_et_cyprus" and "Tzîpern" in d_node.get("tarr", ""):
                    d_node["tarr"] = d_node["tarr"].replace("Tzîpern", "Zîpern")

                for ck, c_node in d_node.get("counties", {}).items():
                    if ck in c_ipa:
                        c_node["ipa"] = c_ipa[ck]
                    if ck == "c_puigcerda" and "Tzerdanje" in c_node.get(
                        "tarr", ""
                    ):
                        c_node["tarr"] = c_node["tarr"].replace(
                            "Tzerdanje", "Zerdanje"
                        )
                        c_node["tarr_direct"] = c_node.get(
                            "tarr_direct", ""
                        ).replace("Tzerdanje", "Zerdanje")
                        c_node["tarr_hist"] = c_node.get(
                            "tarr_hist", ""
                        ).replace("Tzerdanje", "Zerdanje")

    with open(tree_path, "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=2, ensure_ascii=False)
    print(f"-> Successfully updated {tree_path.name}.")


if __name__ == "__main__":
    sync_all()

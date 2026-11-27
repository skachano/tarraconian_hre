#!/usr/bin/env python3
"""
pipeline_stage2_variant_selection.py

Stage 2 of the Tarraconian Barony-Tier Toponymic Naming Pipeline (v2):
Resolves the exact source-language form (`form`, `native_script`, `iso_code`,
`match_tier`, `target_morphology_family`, and ranked 867 NTR backup candidates)
for all 10,239 occupied baronies routed by Stage 1.

Reads:
  - data/pipeline_stage1_routed.json
  - data/ck3_culture_to_iso_and_generics.json
  - data/barony_geography.json
  - data/anachronicity_audit/*.json (47 shards)
  - data/natural_tribal_replacements/*.json (47 shards)

Emits:
  - data/pipeline_stage2_variants.json
"""

from __future__ import annotations

import glob
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

REPO_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_DIR / "data"

LITURGICAL_NAME_TO_ISOS: dict[str, list[str]] = {
    "Latin": ["lat"],
    "Classical Armenian": ["xcl", "hye", "arm"],
    "Hebrew": ["heb", "arc"],
    "Arabic": ["ara"],
}

FAMILY_PROTO_EXPANSION: dict[str, list[str]] = {
    "east_slavic": ["orv", "sla-pro", "sla", "rus", "ukr", "bel", "chu"],
    "south_slavic": ["chu", "sla-pro", "sla", "bul", "hrv", "srp", "slv", "mkd"],
    "west_slavic_lechitic": ["pol", "csb", "sla-pro", "sla", "ces"],
    "west_slavic_czech_slovak": ["ces", "slk", "sla-pro", "sla", "chu"],
    "baltic": ["lit", "lav", "prg", "bat-pro", "bat"],
    "high_german": ["goh", "gmh", "deu", "gem-pro", "gem"],
    "tarraconian_imperial": ["gmh", "goh", "deu", "cat", "oci", "lat"],
    "low_german_dutch": ["osx", "odt", "dum", "nld", "nds", "gem-pro"],
    "anglo_saxon": ["ang", "enm", "eng", "gem-pro", "non"],
    "north_germanic": ["non", "nor", "swe", "dan", "isl", "gem-pro"],
    "ibero_romance": ["spa", "por", "glg", "ast", "lat", "oci"],
    "occitano_catalan": ["cat", "oci", "lat", "fra"],
    "gallo_romance": ["fro", "fra", "oci", "lat"],
    "italo_romance": ["ita", "scn", "vec", "lat", "nap"],
    "eastern_romance": ["ron", "rup", "lat", "vlx"],
    "latin_classical": ["lat", "ita"],
    "goidelic": ["sga", "mga", "gle", "gla", "cel-pro"],
    "brythonic": ["wlm", "cym", "bre", "cor", "cel-bry", "cel-pro"],
    "hellenic": ["grc", "ell", "gkm"],
    "arabic": ["ara", "sem-pro", "arc", "syc"],
    "berber": ["ber", "tzm", "kab", "shi", "zen", "ara"],
    "aramaic_hebrew": ["syc", "arc", "heb", "ara"],
    "iranian": ["pal", "peo", "fas", "sog", "ira-pro", "os", "oss", "kur", "pus"],
    "turkic": ["otk", "tur", "kaz", "uzb", "tuk", "kir", "tat", "bak", "uig", "aze", "trk-pro"],
    "oghur": ["xbo", "chv", "otk", "tur", "tat"],
    "mongolic": ["xng", "mon", "bua", "xal", "cmg"],
    "khitan": ["zkt", "xng", "mon", "lzh", "zho"],
    "tungusic": ["juc", "mnc", "evn", "gld", "lzh", "zho"],
    "magyar": ["hun", "fiu-pro", "urj-pro"],
    "finnic": ["fin", "est", "krl", "vep", "fiu-pro"],
    "sami": ["sme", "sma", "smj", "smi", "fiu-pro"],
    "volga_permian": ["kpv", "koi", "udm", "mhr", "mdf", "myv", "fiu-pro"],
    "indo_aryan": ["san", "pra", "inc-pro", "hin", "ben", "mar", "guj", "pan", "ori", "sin", "asm", "snd", "nep"],
    "dravidian": ["tam", "tel", "kan", "mal", "dra-pro", "san"],
    "sinosphere_chinese": ["ltc", "lzh", "och", "zho", "cmn", "yue", "hak"],
    "korean": ["oko", "okm", "kor", "lzh", "zho"],
    "japonic": ["ojp", "jpn", "ryu", "lzh"],
    "viet": ["vi", "vie", "lzh", "zho"],
    "tibetic": ["otb", "bod", "xct", "dz", "dzo"],
    "burmese_qiangic": ["obr", "mya", "sit-pro"],
    "austronesian": ["kaw", "jav", "msa", "ind", "mal", "san"],
    "mon_khmer": ["okz", "khm", "mnw", "mkh-pro", "san"],
    "tai_hmong": ["tha", "lao", "shn", "za", "zha", "tai-pro"],
    "ethiopic_cushitic": ["gez", "amh", "tir", "som", "bej", "orm", "aar", "cus-pro"],
    "west_central_african": ["hau", "yor", "ibo", "fub", "ffm", "snk", "bm", "bam", "mos", "tw", "aka", "knc", "fvr"],
    "east_bantu_swahili": ["swa", "bnt-pro", "kon"],
    "armenian": ["xcl", "hye", "arm"],
    "kartvelian": ["oge", "kat", "ccs-pro"],
    "basque": ["eus", "euq-pro"],
    "albanian": ["sqi", "aln", "als"],
}

CLASSICAL_LINGUA_FRANCA_ISOS = ["lat", "grc", "ara", "san", "lzh", "fas", "bod"]
CJK_RE = re.compile(r"[\u3400-\u9FFF\uF900-\uFAFF]+")

# Multi-word foreign/English geographic or ethnolinguistic classifiers stripped from clean_source_stem
# so downstream Stage 3/6 compounding produces "Sulawesikirchen" rather than "Laut Sulawesikirchen".
NTR_HEADWORD_RE = re.compile(
    r"^(?:"
    r"Gunung\s+Bukit|Doi\s+Phu|Mae\s+Nam|Al-Irk\s+al-|Adrar\s+n|Asif\s+n|"
    r"Kipot\s+ng|Golpo\s+ng|Look\s+ng|Tangway\s+ng|"
    r"Cnoic\s+na|Slieve\s+|Carrick\s+|Monadh|Uisge|"
    r"Dary[āa]cheh-?ye|Dasht-?e|R[ūu]d-?e|K[ūu]h-?e|"
    r"Nahr\s+al-|Nahr|W[āa]d[īi]|Bahr\s+al-|Bahr|Jabal|Jib[āa]l|Khal[īi]j|"
    r"Laut|Dagat|Sungai|Bukit|Gunung|Pegunungan|Danau|Selat|Pulau|Teluk|Tanjung|Kuala|Muara|Suku|Urang|Bundok|"
    r"Tonle|Mae|Nam|Doi|Phu|"
    r"Webi|Kogin|Mto|Odo|Ilog|Asif|Adrar|Mun[țt]ii|Muntzii|"
    r"Loch|Glen|Strath|Port|Plain\s+of|Gulf\s+of|Bay\s+of|Strait\s+of|Lake|Mount|Mountain|River|Island|"
    r"Ozero|Reka|Gora|Zaliv|Ostrov|R[íi]o|Lago|Monte|Sierra"
    r")\s+",
    re.I,
)
NTR_TRAILING_RE = re.compile(
    r"\s+(?:people|tribe|group|river|lake|sea|mountain|mountains|range|hills|hill|plain|basin|valley|gulf|bay|strait|island|islands|peninsula|mTsho|mtsho)$",
    re.I,
)
WYLIE_PREFIX_TEST_RE = re.compile(r"(?:^|[\s\-])[srbdgml][KGCJTDNPBMZSYRW]")


def clean_wylie_tibetan(stem: str, iso_code: str | None) -> str:
    """Convert Tibetan Wylie transliteration (e.g. `sPang-gong mTsho`) into readable phonetic form."""
    if not stem:
        return stem
    is_tib = (iso_code in {"bod", "otb", "xct", "dz", "dzo"}) or bool(WYLIE_PREFIX_TEST_RE.search(stem))
    if not is_tib:
        return stem

    def _clean_syl(tok: str) -> str:
        # Handle trailing 'mTsho' -> 'Tscho', 'gTsang' -> 'Tsang', 'sPang' -> 'Pang', 'rGyal' -> 'Gyal', 'Dwangs' -> 'Dangs', 'klungs' -> 'Lung'
        t = re.sub(r"Dwangs\b", "Dangs", tok, flags=re.I)
        t = re.sub(r"klungs\b", "Lung", t, flags=re.I)
        # Strip silent Wylie prefix consonant before root consonant (sPang -> Pang, bKra -> Kra, lDum -> Dum, rGyal -> Gyal)
        m = re.match(r"^([srbdgml])([KGCJTDNPBMZSYRWH][a-zA-Z\-']*)$", t)
        if m and not (m.group(1).lower() == "l" and m.group(2).lower().startswith("ha")):
            t = m.group(2)
        else:
            t = re.sub(r"^([srbdgml])(?=(?:tsh|dz|ng|ny|ky|gy|nj|[kgcjtdpbmzsy])[aeiou])", "", t, flags=re.I)
        t = re.sub(r"tsh", "tsch", t, flags=re.I)
        t = t.replace("'", "")
        return t[:1].upper() + t[1:] if t else ""

    parts = re.split(r"([\s\-]+)", stem)
    cleaned = "".join(p if p.isspace() or p == "-" else _clean_syl(p) for p in parts)
    return cleaned


def clean_ntr_stem_for_compounding(raw_form: str, iso_code: str | None, *, strip_heads: bool = True) -> str:
    """Clean Wylie prefixes, leading geographic classifiers, and trailing qualifiers for Stage 3/6."""
    s = raw_form.lstrip("*").strip()
    if not s:
        return ""
    s = clean_wylie_tibetan(s, iso_code)
    if strip_heads:
        # Strip leading foreign/English classifier if >= 3 letters remain
        m = NTR_HEADWORD_RE.match(s)
        if m:
            rest = s[m.end():].strip()
            if len(re.sub(r"[^A-Za-zÀ-ɏ]", "", rest)) >= 3:
                s = rest
        m2 = NTR_TRAILING_RE.search(s)
        if m2:
            rest2 = s[:m2.start()].strip(" -")
            if len(re.sub(r"[^A-Za-zÀ-ɏ]", "", rest2)) >= 3:
                s = rest2
    return s


def load_sharded_baronies(pattern: str) -> dict[str, dict[str, Any]]:
    combined: dict[str, dict[str, Any]] = {}
    for fpath in sorted(glob.glob(str(DATA_DIR / pattern))):
        with open(fpath, "r", encoding="utf-8") as f:
            combined.update(json.load(f).get("baronies", {}))
    return combined


def extract_cjk_chars(text: str | None) -> str:
    if not text:
        return ""
    return "".join(CJK_RE.findall(text))


def get_culture_info(cult_bridge: dict[str, Any], name: str) -> dict[str, Any]:
    if name in cult_bridge:
        return cult_bridge[name]
    low = name.lower()
    for k, v in cult_bridge.items():
        if k.lower() == low:
            return v
    return {}


def build_iso_search_tiers(
    stage1_rec: dict[str, Any],
    cult_bridge: dict[str, Any],
) -> list[tuple[str, str]]:
    """
    Build deterministic ordered list of `(iso_code, match_tier_label)`.
    Follows Stage 2 priority spec:
      liturgical (on ecclesiastical liturgical priority) -> exact primary ->
      parent hybrids -> exact secondary -> transmission -> language-family/proto ->
      regional classical lingua franca.
    """
    prio = stage1_rec["stage2_culture_priority"]
    c_info = get_culture_info(cult_bridge, stage1_rec["coinage_culture"])
    s_info = get_culture_info(cult_bridge, stage1_rec["substrate_culture"])
    t_info = get_culture_info(cult_bridge, stage1_rec["transmission_culture"])

    if prio == "coinage_first":
        prim_info, sec_info = c_info, s_info
        prim_tag, sec_tag = "coinage", "substrate"
    else:
        prim_info, sec_info = s_info, c_info
        prim_tag, sec_tag = "substrate", "coinage"

    seen: set[str] = set()
    ordered: list[tuple[str, str]] = []

    def add_iso(code: str | None, tier: str) -> None:
        if not code:
            return
        cl = code.lower()
        if cl not in seen:
            seen.add(cl)
            ordered.append((cl, tier))

    # 1. Liturgical override for church holdings
    if stage1_rec.get("liturgical_priority"):
        ll_name = stage1_rec.get("liturgical_language") or ""
        for code in LITURGICAL_NAME_TO_ISOS.get(ll_name, []):
            add_iso(code, "liturgical_exact")
        add_iso(prim_info.get("liturgical_iso"), "liturgical_culture")
        add_iso(c_info.get("liturgical_iso"), "liturgical_coinage")

    # 2. Primary culture primary & parent ISOs (Sinosphere: lzh/zho/kor/jpn also prioritized cleanly)
    prim_isos = list(prim_info.get("iso_codes", []))
    prim_parents = list(prim_info.get("parent_isos", []))
    if prim_isos:
        add_iso(prim_isos[0], f"exact_{prim_tag}_primary")
    for code in prim_isos[1:3]:
        add_iso(code, f"exact_{prim_tag}_primary")
    for code in prim_parents:
        add_iso(code, f"parent_{prim_tag}_hybrid")
    for code in prim_isos[3:]:
        add_iso(code, f"exact_{prim_tag}_secondary_list")

    # 3. Secondary culture ISOs + parents
    for code in sec_info.get("iso_codes", [])[:3]:
        add_iso(code, f"exact_{sec_tag}")
    for code in sec_info.get("parent_isos", []):
        add_iso(code, f"parent_{sec_tag}_hybrid")

    # 4. Transmission culture ISOs
    for code in t_info.get("iso_codes", [])[:3]:
        add_iso(code, "transmission_iso")

    # 5. Family / Proto expansion
    for info in (prim_info, sec_info, t_info):
        mf = info.get("morphology_family", "")
        for code in FAMILY_PROTO_EXPANSION.get(mf, []):
            add_iso(code, "family_proto")

    # 6. Classical lingua franca fallback (prioritized by lit_iso / macro sphere first)
    add_iso(prim_info.get("liturgical_iso"), "classical_lingua_franca")
    for code in CLASSICAL_LINGUA_FRANCA_ISOS:
        add_iso(code, "classical_lingua_franca")

    return ordered


def match_language_variant(
    variants: list[dict[str, Any]],
    iso_tiers: list[tuple[str, str]],
    require_native_sino: bool = False,
) -> tuple[dict[str, Any] | None, str, int]:
    """Return `(matched_variant_dict, match_tier, tier_rank_index)`. Lower tier_rank_index is better."""
    if not variants:
        return None, "localisation_stem_no_variants", 999

    by_code: dict[str, list[dict[str, Any]]] = {}
    for lv in variants:
        code = (lv.get("language_code") or lv.get("iso_639_3") or lv.get("lang") or "").lower()
        if code:
            by_code.setdefault(code, []).append(lv)

    # Pass 1: if Sinosphere prefers native Hanzi script, look within primary/family sino codes first
    if require_native_sino:
        for idx, (iso, tier) in enumerate(iso_tiers):
            if iso in {"ltc", "lzh", "zho", "cmn", "och", "kor", "okm", "oko", "jpn", "ojp", "vie"}:
                for lv in by_code.get(iso, []):
                    if lv.get("native_script"):
                        return lv, f"{tier}_native_script", idx

    # Pass 2: standard deterministic ISO cascade
    for idx, (iso, tier) in enumerate(iso_tiers):
        cands = by_code.get(iso)
        if cands:
            # Prefer one with native_script if require_native_sino
            if require_native_sino:
                for lv in cands:
                    if lv.get("native_script"):
                        return lv, tier, idx
            return cands[0], tier, idx

    return None, "localisation_stem_fallback", 999


def score_ntr_candidate(
    cand: dict[str, Any],
    stage1_rec: dict[str, Any],
    geo_rec: dict[str, Any],
    iso_tiers: list[tuple[str, str]],
) -> tuple[float, dict[str, Any]]:
    """
    Score a single valid-867 NTR candidate by holding_type, origin_type, capital status,
    sea-coast vs inland geometry, and ISO variant fit.
    """
    ht = stage1_rec["holding_type"]
    orig = stage1_rec["origin_type"]
    is_cap = stage1_rec["is_capital_barony"]
    is_sino = stage1_rec["is_sinosphere_scope"]
    is_sea = bool(geo_rec.get("is_sea_coast", False))

    cat = (cand.get("category") or "").lower()
    sub = (cand.get("feature_subtype") or "").lower()
    rel = (cand.get("relationship") or "").lower()
    text_blob = f"{sub} {rel}"

    # 1. Base category preference by holding type
    if ht == "city":
        base = {"hydronym": 40, "choronym": 30, "topographic_feature": 22, "oronym": 12, "tribe": 6}.get(cat, 10)
    elif ht == "castle":
        base = {"oronym": 38, "hydronym": 36, "tribe": 24, "topographic_feature": 18, "choronym": 14}.get(cat, 10)
    elif ht == "church":
        base = {"oronym": 38, "topographic_feature": 36, "hydronym": 26, "tribe": 14, "choronym": 12}.get(cat, 10)
    else:
        base = 20

    # 2. Subtype & physical alignment refinements
    if ht == "castle" and any(w in text_blob for w in ("ford", "crossing", "pass", "ridge", "spur", "crag", "rock")):
        base += 6
    if ht == "church" and any(w in text_blob for w in ("forest", "wood", "valley", "spring", "well", "island", "marsh", "grove", "oak")):
        base += 8
    if ht == "city" and any(w in text_blob for w in ("confluence", "estuary", "river", "harbor", "port")):
        base += 5

    # Sea-coast vs inland guardrail
    marine_words = ("bay", "gulf", "lagoon", "strait", "harbor", "sea", "coast", "peninsula", "cape", "fjord")
    if any(w in sub for w in marine_words):
        base += 10 if is_sea else -22

    # Unfeudalized / feudalized capital boost for tribal & regional stems
    if is_cap and orig in {"pre_867_unfeudalized", "feudalized_post_867"}:
        if cat == "tribe":
            base += 20
        elif cat == "choronym":
            base += 16

    # 3. ISO match quality & Sinosphere native script bonus
    lv, match_tier, tier_idx = match_language_variant(
        cand.get("language_variants", []),
        iso_tiers,
        require_native_sino=is_sino,
    )
    iso_bonus = max(0, 20 - tier_idx * 2) if lv is not None else 0
    if is_sino and lv and lv.get("native_script") and extract_cjk_chars(lv["native_script"]):
        iso_bonus += 18

    total_score = float(base + iso_bonus)
    chosen_form = (lv["form"] if lv and lv.get("form") else None) or cand.get("localisation_stem") or cand.get("name") or ""
    chosen_native = lv.get("native_script") if lv else None
    chosen_iso = (lv.get("language_code") or lv.get("iso_639_3")) if lv else None
    chosen_lang = lv.get("language") if lv else None

    resolved_entry = {
        "candidate_name": cand.get("name"),
        "localisation_stem": cand.get("localisation_stem"),
        "category": cat,
        "feature_subtype": sub,
        "score": total_score,
        "selected_form": chosen_form,
        "clean_stem": clean_ntr_stem_for_compounding(chosen_form, chosen_iso, strip_heads=True),
        "native_script": chosen_native,
        "selected_iso": chosen_iso,
        "selected_language": chosen_lang,
        "match_tier": match_tier,
        "etymology_notes": cand.get("etymology_notes"),
    }
    return total_score, resolved_entry


def select_pre867_historical_name(audit_rec: dict[str, Any], prefer_hanzi: bool = False) -> dict[str, Any] | None:
    hns = [
        hn for hn in (audit_rec.get("historical_names") or [])
        if hn.get("attested_from") is None or hn.get("attested_from") <= 867
    ]
    if not hns:
        return None

    def hn_key(hn: dict[str, Any]) -> tuple[int, int, int]:
        has_cjk = 1 if (prefer_hanzi and extract_cjk_chars(hn.get("native_script"))) else 0
        has_native = 1 if hn.get("native_script") else 0
        same_site = 1 if hn.get("relationship") == "same_site_earlier_name" else 0
        return (has_cjk, same_site, has_native)

    return max(hns, key=hn_key)


def infer_historical_name_iso(hn: dict[str, Any], fallback_iso: str | None) -> str | None:
    blob = " ".join(str(x) for x in (hn.get("language"), hn.get("source"), hn.get("notes")) if x).lower()
    if extract_cjk_chars(hn.get("native_script")):
        if "samguk" in blob or "goryeo" in blob or "silla" in blob or "goguryeo" in blob or "baekje" in blob:
            return "oko"
        return "lzh"
    for kw, iso in [
        ("roman", "lat"), ("latin", "lat"), ("itinerarium", "lat"), ("pliny", "lat"), ("tabula peutinger", "lat"),
        ("greek", "grc"), ("ptolemy", "grc"), ("strabo", "grc"), ("herodotus", "grc"), ("procopius", "grc"),
        ("sanskrit", "san"), ("pali", "pli"), ("prakrit", "pra"),
        ("arabic", "ara"), ("al-idrisi", "ara"), ("al-bakri", "ara"), ("ibn khordadbeh", "ara"),
        ("old english", "ang"), ("anglo-saxon", "ang"), ("bede", "lat"),
        ("old norse", "non"), ("saga", "non"), ("old irish", "sga"),
        ("old east slavic", "orv"), ("primary chronicle", "orv"),
        ("tangshu", "lzh"), ("han shu", "lzh"),
        ("persian", "fas"), ("sasanian", "pal"), ("armenian", "xcl"), ("tibetan", "otb"),
    ]:
        if kw in blob:
            return iso
    return fallback_iso


def run_stage2() -> dict[str, Any]:
    with open(DATA_DIR / "pipeline_stage1_routed.json", "r", encoding="utf-8") as f:
        s1_payload = json.load(f)
    s1 = s1_payload["baronies"]

    with open(DATA_DIR / "ck3_culture_to_iso_and_generics.json", "r", encoding="utf-8") as f:
        cb_data = json.load(f)
    cult_bridge = cb_data["cultures"]

    with open(DATA_DIR / "barony_geography.json", "r", encoding="utf-8") as f:
        geo = json.load(f)["baronies"]

    audit = load_sharded_baronies("anachronicity_audit/barony_audit_*.json")
    ntr = load_sharded_baronies("natural_tribal_replacements/barony_natural_tribal_replacements_*.json")

    match_tier_counts: Counter[str] = Counter()
    stem_category_counts: Counter[str] = Counter()
    primary_iso_counts: Counter[str] = Counter()
    opaque_count = 0
    hanzi_extracted_count = 0

    stage2_baronies: dict[str, dict[str, Any]] = {}

    for bk in sorted(s1.keys()):
        r1 = s1[bk]
        if not r1["is_occupied"]:
            stage2_baronies[bk] = {
                "barony_key": bk,
                "is_occupied": False,
                "stage1_track": "Unoccupied_Blank",
                "final_record": r1["final_record"],
            }
            continue

        audit_rec = audit[bk]
        geo_rec = geo[bk]
        ntr_rec = ntr.get(bk)

        c_info = get_culture_info(cult_bridge, r1["coinage_culture"])
        s_info = get_culture_info(cult_bridge, r1["substrate_culture"])
        t_info = get_culture_info(cult_bridge, r1["transmission_culture"])

        iso_tiers = build_iso_search_tiers(r1, cult_bridge)

        # Rank all valid 867 NTR candidates if barony is in NTR pool
        ranked_ntr: list[dict[str, Any]] = []
        if ntr_rec:
            valid_cands = [
                c for c in ntr_rec.get("replacement_candidates", [])
                if c.get("valid_for_bookmarks", {}).get("867", False)
            ]
            scored = [score_ntr_candidate(c, r1, geo_rec, iso_tiers) for c in valid_cands]
            scored.sort(key=lambda pair: -pair[0])
            for rank_i, (_, entry) in enumerate(scored, 1):
                entry["rank"] = rank_i
                ranked_ntr.append(entry)

        stem_source = r1["stem_source"]
        is_sino = r1["is_sinosphere_scope"]

        selected_form = ""
        selected_native: str | None = None
        selected_iso: str | None = None
        selected_lang: str | None = None
        match_tier = ""
        stem_category = ""
        stem_subtype = ""
        audit_morphemes = audit_rec.get("morphemes") or []

        if stem_source in {"pre867_attested_vanilla", "pre867_attested_hanzi"}:
            selected_form = audit_rec.get("vanilla_ck3_name") or bk
            # Prefer substrate ISO on pre-867 attested anchors unless overruled
            anchor_info = c_info if r1["stage2_culture_priority"] == "coinage_first" else s_info
            # Check if audit morphemes carry an explicit native form or Hanzi
            mor_cjk = extract_cjk_chars(" ".join(m.get("form", "") for m in audit_morphemes))
            if is_sino and mor_cjk:
                selected_native = mor_cjk
            selected_iso = anchor_info.get("primary_iso") or (audit_morphemes[0].get("language_code") if audit_morphemes else None)
            selected_lang = anchor_info.get("ck3_language")
            match_tier = "pre867_attested_anchor"
            npn = audit_rec.get("natural_proper_name") or {}
            stem_category = npn.get("type") or ("eponym" if audit_rec.get("eponym") else "attested_historical")
            stem_subtype = ""

        elif stem_source == "historical_names_pre867":
            hn = select_pre867_historical_name(audit_rec, prefer_hanzi=is_sino)
            assert hn is not None, f"Missing historical_names on {bk}"
            selected_form = hn.get("name") or ""
            selected_native = hn.get("native_script")
            fallback_iso = s_info.get("primary_iso") or c_info.get("primary_iso") or "lat"
            selected_iso = infer_historical_name_iso(hn, fallback_iso)
            selected_lang = hn.get("language") or hn.get("source")
            match_tier = "audit_historical_names_pre867"
            stem_category = hn.get("relationship") or "historical_anchor"
            stem_subtype = ""

        elif stem_source == "existing_natural_proper_name":
            npn = audit_rec.get("natural_proper_name") or {}
            selected_form = audit_rec.get("vanilla_ck3_name") or npn.get("name") or ""
            mor_cjk = extract_cjk_chars(" ".join(m.get("form", "") for m in audit_morphemes))
            selected_native = mor_cjk or None
            selected_iso = (
                (audit_morphemes[0].get("language_code") if audit_morphemes else None)
                or s_info.get("primary_iso")
                or c_info.get("primary_iso")
            )
            selected_lang = audit_morphemes[0].get("language") if audit_morphemes else s_info.get("ck3_language")
            match_tier = "audit_existing_natural_proper_name"
            stem_category = npn.get("type") or "natural_feature"
            stem_subtype = ""

        elif stem_source in {"natural_tribal_replacements_867", "ntr_sino_variant"}:
            assert ranked_ntr, f"Missing valid 867 NTR candidates on {bk}"
            top = ranked_ntr[0]
            selected_form = top["selected_form"]
            selected_native = top["native_script"]
            selected_iso = top["selected_iso"]
            selected_lang = top["selected_language"]
            match_tier = top["match_tier"]
            stem_category = top["category"]
            stem_subtype = top["feature_subtype"]

        elif stem_source == "stage3_sino_coined_compound":
            # Optional NTR landscape hint if available; Stage 3 builds 2-char Classical Chinese compound
            if ranked_ntr:
                top = ranked_ntr[0]
                selected_form = top["selected_form"]
                selected_native = top["native_script"]
                selected_iso = top["selected_iso"] or c_info.get("primary_iso")
                selected_lang = top["selected_language"]
                match_tier = f"coined_with_ntr_hint:{top['match_tier']}"
                stem_category = top["category"]
                stem_subtype = top["feature_subtype"]
            else:
                selected_form = audit_rec.get("vanilla_ck3_name") or bk
                selected_native = None
                selected_iso = c_info.get("primary_iso") or "lzh"
                selected_lang = c_info.get("ck3_language")
                match_tier = "stage3_sino_coined_no_ntr"
                stem_category = "coined_compound"
                stem_subtype = ""
        else:
            raise RuntimeError(f"Unhandled stem_source {stem_source!r} for {bk}")

        # Strip leading/trailing geographic headwords ONLY on non-867/NTR stems when downstream synthesis compounds them,
        # while always normalizing Tibetan Wylie transliteration and stripping reconstruction asterisks.
        strip_heads = stem_source in {"natural_tribal_replacements_867", "ntr_sino_variant", "stage3_sino_coined_compound"} or bool(r1.get("requires_stage3_synthesis"))
        clean_stem = clean_ntr_stem_for_compounding(selected_form, selected_iso, strip_heads=strip_heads)
        hanzi_str = (extract_cjk_chars(selected_native) or extract_cjk_chars(selected_form)) if is_sino else ""

        # Rule 3 opaqueness signal
        is_opaque = bool(audit_rec.get("eponym")) or (stem_category == "tribe")
        if is_opaque:
            opaque_count += 1
        if hanzi_str:
            hanzi_extracted_count += 1

        match_tier_counts[match_tier] += 1
        stem_category_counts[stem_category] += 1
        if selected_iso:
            primary_iso_counts[selected_iso] += 1

        stem_etym_iso = (
            audit_morphemes[0].get("language_code")
            if audit_morphemes and isinstance(audit_morphemes[0], dict)
            else None
        )

        stage2_baronies[bk] = {
            **r1,
            "coinage_morphology_family": c_info.get("morphology_family"),
            "substrate_morphology_family": s_info.get("morphology_family"),
            "transmission_profile": t_info.get("transmission_profile"),
            "ordered_iso_search": [code for code, _ in iso_tiers[:10]],
            "selected_source_form": selected_form,
            "clean_source_stem": clean_stem,
            "selected_native_script": selected_native,
            "extracted_hanzi": hanzi_str or None,
            "selected_iso": selected_iso,
            "stem_etymological_iso": stem_etym_iso,
            "selected_language": selected_lang,
            "match_tier": match_tier,
            "stem_category": stem_category,
            "stem_subtype": stem_subtype,
            "is_opaque_proper_stem": is_opaque,
            "audit_morphemes": audit_morphemes,
            "audit_eponym": audit_rec.get("eponym"),
            "ranked_ntr_candidates": ranked_ntr,
        }

    payload = {
        "metadata": {
            "schema_version": "1.0.0",
            "pipeline_stage": "stage_2_source_language_variant_selection",
            "total_baronies": len(stage2_baronies),
            "occupied_baronies": sum(match_tier_counts.values()),
            "unoccupied_baronies": len(stage2_baronies) - sum(match_tier_counts.values()),
            "match_tier_counts": dict(match_tier_counts),
            "stem_category_counts": dict(stem_category_counts),
            "opaque_proper_stem_count": opaque_count,
            "hanzi_extracted_count": hanzi_extracted_count,
            "top_selected_isos": dict(primary_iso_counts.most_common(25)),
        },
        "baronies": stage2_baronies,
    }
    return payload


def main() -> None:
    payload = run_stage2()
    out_path = DATA_DIR / "pipeline_stage2_variants.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    print(f"Wrote {out_path} ({out_path.stat().st_size / (1024*1024):.2f} MB)")
    print("Stage 2 metadata:", json.dumps(payload["metadata"], indent=2))


if __name__ == "__main__":
    main()

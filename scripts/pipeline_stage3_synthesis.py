#!/usr/bin/env python3
"""
pipeline_stage3_synthesis.py

Stage 3 of the Tarraconian Barony-Tier Toponymic Naming Pipeline (v2):
Coinage-Era Holder Personality Archetype & Structural Synthesis across all
10,239 occupied baronies (active on the 5,599 Stage 3 baronies; clean pass-through
on the remaining 4,640 attested/retained baronies).

Enforces:
  1. True coinage-era ruler attribution (`data/barony_coinage_rulers.json`) +
     `global_onomasticon_adaptation.json` (zero raw CK3 escapes, circular house guard).
  2. Toponym-First budget guardrails (~55-65% topographic/landscape, ~12-18% pious,
     ~10-15% vain/dynastic, ~8-12% martial/frontier, ~5-10% mercantile/civic)
     with county-level quotas preventing excessive eponym/devotional repetition.
  3. Strict sea-coast gating (`data/barony_geography.json`) for maritime generics
     (-hâven, -port, Marsa, Mina, 港) vs inland tradeport waterborne generics
     (-vurt, -brücke, -ford, -brod, Qantara, 津).
  4. Native morphological coinage in `coinage_culture`'s own system first, emitting
     both `coined_source_form` and structured `{modifier, generic, concept, hanzi}`
     slots so Stage 4 can execute Procedure 1/2 calquing or phonological mediation.

Emits:
  - data/pipeline_stage3_synthesized.json
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from ck3_name_decoder import decode_ck3_personal_name

REPO_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_DIR / "data"

# Transparent English concept modifiers used across archetypes & building proxies
CONCEPT_NATIVE_GLOSS: dict[str, dict[str, dict[str, str]]] = {
    "martial_castle": {
        "concept": "shield_defense",
        "tarr": ("Schirm", "Wart", "Îsen", "Rîtter", "Landes"),
        "romance": ("Garde", "Forte", "Val"),
        "arabic": ("al-Haras", "al-Mansur", "al-Fath"),
        "slavic": ("Strazh", "Tverdy", "Kremen"),
        "turkic": ("Demir", "Kara", "Aslan"),
        "indic": ("Vijaya", "Vikrama", "Ran"),
        "sinitic": ("安邊", "靖北", "威鎮", "鐵關"),
        "default": ("Guard", "Iron", "Watch"),
    },
    "martial_battle": {
        "concept": "victory_triumph",
        "tarr": ("Sêge", "Wal"),
        "romance": ("Victoire", "Viktôri"),
        "arabic": ("al-Fath", "an-Nasr"),
        "slavic": ("Pobed", "Rat"),
        "turkic": ("Zafar", "Batyr"),
        "indic": ("Jaya", "Vijaya"),
        "sinitic": ("凱旋", "定功"),
        "default": ("Victory", "Battle"),
    },
    "mercantile_city": {
        "concept": "free_chartered",
        "tarr": ("Frî", "Nîe", "Marct", "Zol", "Kouf"),
        "romance": ("Franca", "Nova", "Mercat"),
        "arabic": ("as-Suq", "al-Bandar", "al-Jadida"),
        "slavic": ("Novy", "Torg", "Volny"),
        "turkic": ("Bazar", "Yangi", "Altun"),
        "indic": ("Nava", "Ratna", "Vanij"),
        "sinitic": ("通寶", "豐市", "新津", "利埠"),
        "default": ("New", "Free", "Market"),
    },
    "mercantile_castle": {
        "concept": "toll_customs",
        "tarr": ("Zol", "Maut", "Golt"),
        "romance": ("Peage", "Gabelle", "Or"),
        "arabic": ("al-Maks", "al-Khazna"),
        "slavic": ("Myto", "Zlat"),
        "turkic": ("Tamga", "Altun"),
        "indic": ("Shulka", "Suvarna"),
        "sinitic": ("稅關", "金鎖"),
        "default": ("Toll", "Customs"),
    },
    "pious_generic": {
        "concept": "holy_sacred",
        "tarr": ("Hiligen", "Marien", "Fride", "Crûce"),
        "romance": ("Sancta", "Maria", "Croix"),
        "arabic": ("as-Salam", "al-Quds", "ar-Rahman"),
        "slavic": ("Svyat", "Bogo", "Mir"),
        "turkic": ("Qut", "Iman", "Nûr"),
        "indic": ("Dharma", "Shanti", "Deva"),
        "sinitic": ("清淨", "慈恩", "永寧", "法華"),
        "default": ("Holy", "Cross", "Peace"),
    },
}

DEFAULT_CHRISTIAN_SAINTS: list[tuple[str, str]] = [
    ("Peter", "Pêter"),
    ("Paul", "Pôl"),
    ("Martin", "Martîn"),
    ("Nicholas", "Nîkôlôs"),
    ("George", "Dschôrdi"),
    ("Michael", "Mîchaêl"),
    ("Laurence", "Laurenz"),
    ("Stephen", "Steffan"),
    ("Arnold", "Arnolf"),
    ("Lambert", "Lampert"),
    ("Hubert", "Hûprecht"),
    ("Eulalia", "Eulâlie"),
    ("Ursula", "Ûrsele"),
    ("Vincent", "Vintzent"),
]

SINO_MODIFIERS_BY_ARCHETYPE: dict[str, list[tuple[str, str, str]]] = {
    # (hanzi_char, concept, english_gloss)
    "topographic_default": [("清", "clear_pure", "clear"), ("高", "high_upper", "high"), ("白", "white", "white"), ("青", "green_azure", "green"), ("石", "stone_rock", "stone"), ("松", "pine", "pine")],
    "pious_devotional": [("慈", "mercy", "merciful"), ("法", "dharma_law", "sacred law"), ("福", "blessing", "blessed"), ("靜", "tranquil", "tranquil"), ("明", "bright_enlightened", "radiant")],
    "martial_frontier": [("鎮", "garrison_pacify", "guard"), ("威", "might", "mighty"), ("靖", "pacify", "pacified"), ("鐵", "iron", "iron"), ("勝", "victory_triumph", "victory")],
    "mercantile_civic": [("豐", "abundant", "prosperous"), ("寶", "treasure", "treasure"), ("利", "profit", "beneficial"), ("通", "open_thoroughfare", "open trade"), ("興", "flourish", "flourishing")],
    "vain_dynastic": [("永", "eternal", "eternal"), ("隆", "grand", "grand"), ("德", "virtue", "virtuous"), ("昌", "prosperous", "illustrious")],
}

SINO_CLASSIFIER_BY_HOLDING: dict[str, list[tuple[str, str, str | None]]] = {
    # (hanzi, gloss, gate)
    "castle": [("城", "castle / walled citadel", None), ("堡", "fortified keep", None), ("關", "frontier pass / gate", "frontier"), ("鎮", "garrison fort", None)],
    "city": [("州", "prefectural city", None), ("府", "prefectural seat", None), ("市", "market town", "mercantile"), ("港", "sea harbor", "sea_coast"), ("津", "river ford / ferry", "waterborne")],
    "church": [("寺", "monastery / temple", "pious"), ("院", "cloister / academy", "pious"), ("觀", "shrine / abbey", None), ("宮", "sacred palace", None)],
}

GEO_GENERIC_SUFFIX_STRIP = re.compile(
    r"\b(?:River|Stream|Brook|Creek|Mountain|Mountains|Mount|Mt\.?|Hill|Hills|Ridge|Peak|Range|Island|Islands|Isle|Bay|Gulf|Harbor|Harbour|Strait|Lake|Loch|Lough|Basin|Plain|Plains|Valley|Vale|Desert|Forest|Woods|Marsh|Swamp|Peninsula|Cape|Liman)\b",
    re.I,
)


def deterministic_pick(options: list[Any], key: str) -> Any:
    h = int(hashlib.md5(key.encode("utf-8")).hexdigest()[:8], 16)
    return options[h % len(options)]


def extract_clean_compound_stem(raw_stem: str) -> str:
    """Clean geographic descriptor words and parenthetical glosses for smooth compounding."""
    s = re.sub(r"\([^)]*\)", "", raw_stem).strip()
    s = GEO_GENERIC_SUFFIX_STRIP.sub("", s).strip(" ,-/")
    s = re.sub(r"\s{2,}", " ", s).strip()
    return s if len(s) >= 2 else raw_stem.split("(")[0].strip()


def macro_family_bucket(mf: str) -> str:
    m = (mf or "").lower()
    if m in {"tarraconian_imperial", "high_german", "low_german_dutch", "anglo_saxon", "north_germanic"}:
        return "tarr"
    if m in {"ibero_romance", "occitano_catalan", "gallo_romance", "italo_romance", "eastern_romance", "latin_classical"}:
        return "romance"
    if m in {"arabic", "berber", "aramaic_hebrew"}:
        return "arabic"
    if m in {"east_slavic", "south_slavic", "west_slavic_lechitic", "west_slavic_czech_slovak", "baltic"}:
        return "slavic"
    if m in {"turkic", "oghur", "mongolic", "iranian"}:
        return "turkic"
    if m in {"indo_aryan", "dravidian", "austronesian", "mon_khmer", "tai_hmong"}:
        return "indic"
    if m in {"sinosphere_chinese", "korean", "japonic", "viet"}:
        return "sinitic"
    return "default"


def building_concept_hint(phys_rec: dict[str, Any], stem_cat: str) -> tuple[str, str] | None:
    """Return `(concept_id, modifier_key)` from local buildings/POIs if notable."""
    fams = set(phys_rec.get("building_families") or [])
    if "quarries" in fams:
        return ("mine_quarry", "quarries")
    if "hill_forts" in fams or "hill_farms" in fams or stem_cat == "oronym":
        return ("hill_ridge", "oronym_terrain")
    if "logging_camps" in fams or "hunting_grounds" in fams:
        return ("forest_wood", "forest_economy")
    if "peat_quarries" in fams:
        return ("marsh_fen", "peat_wetland")
    if "vineyards" in fams or "orchards" in fams:
        return ("meadow_pasture", "vineyard_orchard")
    if "monastic_schools" in fams or "scriptorium" in fams:
        return ("monastery_school", "monastic_learning")
    if "guild_halls" in fams:
        return ("guild_market", "guild_commerce")
    return None


def select_family_generic(
    fam_obj: dict[str, Any],
    holding_type: str,
    archetype: str,
    is_sea_coast: bool,
    has_tradeport: bool,
    is_frontier: bool,
    is_hilly: bool,
    barony_key: str,
) -> dict[str, Any]:
    """
    Choose an environmentally & typologically congruent generic from `morphology_families`,
    strictly enforcing sea_coast gating on maritime generics.
    """
    cands = list(fam_obj["generics"].get(holding_type) or fam_obj["generics"]["castle"])

    # Filter out sea_coast generics unless verified ocean sea_coast
    allowed = []
    for g in cands:
        gate = g.get("gate")
        if gate == "sea_coast" and not is_sea_coast:
            continue
        allowed.append(g)
    if not allowed:
        allowed = cands

    # Score allowed generics against context
    scored: list[tuple[int, int, dict[str, Any]]] = []
    for idx, g in enumerate(allowed):
        gate = g.get("gate")
        score = 10
        if gate == "sea_coast" and is_sea_coast:
            score += 32 if (archetype == "mercantile_civic" or has_tradeport) else 18
        elif gate == "waterborne" and (has_tradeport or is_sea_coast):
            score += 26 if not is_sea_coast else 14
        elif gate == "mercantile" and archetype == "mercantile_civic":
            score += 30
        elif gate in {"frontier", "martial"} and (is_frontier or archetype == "martial_frontier"):
            score += 28
        elif gate == "hill_or_mountain" and is_hilly:
            score += 22
        elif gate == "pious" and archetype == "pious_devotional":
            score += 28
        elif gate is None:
            score += 8
        scored.append((score, -idx, g))

    best_score = max(s for s, _, _ in scored)
    top_group = [g for s, _, g in scored if s == best_score]
    return deterministic_pick(top_group, f"{barony_key}:{holding_type}:{archetype}")


def assemble_compound(modifier: str, generic: dict[str, Any], compound_order: str) -> str:
    """Assemble `(modifier, generic)` cleanly avoiding tautological hyphens/spaces."""
    g_form = generic["form"]
    pos = generic.get("affix_position", "suffix")
    joiner = generic.get("joiner", "")

    mod = modifier.strip()
    if pos == "prefix":
        g_clean = g_form.strip()
        if g_clean.endswith("-"):
            return f"{g_clean}{mod}"
        return f"{g_clean} {mod}".strip()
    else:
        g_clean = g_form.lstrip("-")
        # Avoid double suffix if mod already ends with generic stem (case-insensitive)
        if mod.lower().endswith(g_clean.lower()) and len(mod) > len(g_clean) + 2:
            return mod
        if joiner == "-":
            return f"{mod}-{g_clean}"
        if joiner == " ":
            return f"{mod} {g_clean}"
        return f"{mod}{g_clean}"


def strip_saint_prefix(s: str) -> str:
    s = re.sub(r"^(?:Saints?|Sanct|Zant|St\.?|Santa|Santo|Panagia)\s+", "", s.strip(), flags=re.I)
    # Handle joined saints like "Peter & Ignatius of Antioch" -> "Peter"
    s = re.split(r"\s*(?:&|\band\b|\bof\b|\(|,)\s*", s)[0].strip()
    return s


def resolve_saint_dedication(
    bk: str,
    ruler_rec: dict[str, Any],
    phys_rec: dict[str, Any],
    phys_saints: dict[str, Any],
    shi: dict[str, Any],
    ono_by_raw: dict[str, Any],
    ono_by_clean: dict[str, Any],
) -> tuple[str, str, str]:
    """Return `(native_saint_name, tarr_saint_name, source_label)`."""
    # Priority 1a: Attested saint_holding_imagery (non-generic)
    s_img = shi.get(bk)
    if s_img and s_img.get("saint_name") and not s_img["saint_name"].startswith("Patron Saint of"):
        raw_st = strip_saint_prefix(s_img["saint_name"])
        if raw_st and "Holy Cross" not in s_img["saint_name"] and "Buddha" not in s_img["saint_name"] and "Avalokiteśvara" not in s_img["saint_name"]:
            cl_rec = ono_by_clean.get(raw_st)
            tarr = cl_rec["primary_tarr_name"] if cl_rec else raw_st
            return (raw_st, tarr, "saint_holding_imagery")

    # Priority 1b: poi_buried_saint or ruler faith canonical saint list in melted_save
    fid = str(ruler_rec.get("faith_id") or "")
    if fid in phys_saints and phys_saints[fid].get("saints"):
        s_list = [s for s in phys_saints[fid]["saints"] if s.get("raw_name")]
        if s_list:
            picked = deterministic_pick(s_list, f"{bk}:faith:{fid}")
            raw_n = picked["raw_name"]
            o_rec = ono_by_raw.get(raw_n)
            if o_rec:
                return (o_rec["clean_name"], o_rec["tarr_name"], f"faith_saints:{fid}")
            clean_n = picked.get("clean_name") or raw_n
            return (clean_n, clean_n, f"faith_saints:{fid}")

    # Priority 1c: Christian ruler fallback saint pantheon (for Catholic/Orthodox/etc.)
    rel = (ruler_rec.get("religion_type") or "").lower()
    ftype = (ruler_rec.get("faith_type") or "").lower()
    if "christian" in rel or ftype in {"catholic", "orthodox", "armenian_apostolic", "miaphysitism", "nestorian", "cathar", "waldensian", "lollard", "hussite"}:
        nat, tarr = deterministic_pick(DEFAULT_CHRISTIAN_SAINTS, f"{bk}:christian_patron")
        return (nat, tarr, "christian_patron_calendar")

    return ("", "", "devotional_abstract")


def run_stage3() -> dict[str, Any]:
    with open(DATA_DIR / "pipeline_stage2_variants.json", "r", encoding="utf-8") as f:
        s2 = json.load(f)["baronies"]
    with open(DATA_DIR / "barony_coinage_rulers.json", "r", encoding="utf-8") as f:
        coinage = json.load(f)["baronies"]
    with open(DATA_DIR / "barony_physical_and_event_context.json", "r", encoding="utf-8") as f:
        phys_all = json.load(f)
    phys_b = phys_all["baronies"]
    phys_saints = phys_all.get("faith_saints", {})
    with open(DATA_DIR / "barony_geography.json", "r", encoding="utf-8") as f:
        geo = json.load(f)["baronies"]
    with open(DATA_DIR / "ck3_culture_to_iso_and_generics.json", "r", encoding="utf-8") as f:
        cb = json.load(f)
    morph_fams = cb["morphology_families"]
    cult_bridge = cb["cultures"]
    with open(DATA_DIR / "global_onomasticon_adaptation.json", "r", encoding="utf-8") as f:
        ono = json.load(f)
    ono_by_raw = ono["by_raw_name"]
    ono_by_clean = ono["by_clean_name"]
    with open(DATA_DIR / "saint_holding_imagery.json", "r", encoding="utf-8") as f:
        shi = json.load(f)

    # Track county quotas to enforce Toponym-First distribution across siblings
    county_barony_lists: dict[str, list[str]] = defaultdict(list)
    for bk, r2 in s2.items():
        if r2.get("is_occupied"):
            county_barony_lists[r2["hierarchy"]["county"]].append(bk)

    county_vain_used: Counter[str] = Counter()
    county_pious_secular_used: Counter[str] = Counter()
    # Pre-seed county eponym count from audit_eponym on pass-through baronies
    for bk, r2 in s2.items():
        if r2.get("is_occupied") and not r2.get("requires_stage3_synthesis") and r2.get("audit_eponym"):
            county_vain_used[r2["hierarchy"]["county"]] += 1

    stage3_mode_counts: Counter[str] = Counter()
    effective_archetype_counts: Counter[str] = Counter()
    synthesis_pattern_counts: Counter[str] = Counter()
    sea_gated_harbor_count = 0
    inland_waterborne_count = 0

    stage3_baronies: dict[str, dict[str, Any]] = {}

    # Process deterministically: churches & event POIs first within each county so shrines get priority before quota caps!
    def sort_priority(bk: str) -> tuple[int, str]:
        r2 = s2[bk]
        if not r2.get("is_occupied"):
            return (9, bk)
        p = phys_b[bk]
        if p.get("saint_shrine") or any("buried" in x for x in p.get("points_of_interest", [])):
            return (0, bk)
        if p.get("holy_order_lease") or any("battle" in x for x in p.get("points_of_interest", [])):
            return (1, bk)
        if r2["holding_type"] == "church":
            return (2, bk)
        if r2["is_capital_barony"]:
            return (3, bk)
        return (4, bk)

    for bk in sorted(s2.keys(), key=sort_priority):
        r2 = s2[bk]
        if not r2["is_occupied"]:
            stage3_baronies[bk] = {
                "barony_key": bk,
                "is_occupied": False,
                "stage1_track": "Unoccupied_Blank",
                "final_record": r2["final_record"],
            }
            continue

        if not r2["requires_stage3_synthesis"]:
            stage3_mode_counts["passthrough_stage2_stem"] += 1
            stage3_baronies[bk] = {
                **r2,
                "stage3_mode": "passthrough_stage2_stem",
                "raw_ruler_archetype": coinage[bk].get("archetype", "topographic_default"),
                "effective_archetype": "attested_retained",
                "coined_source_form": r2["selected_source_form"],
                "coined_hanzi": r2.get("extracted_hanzi"),
                "coined_compound_order": None,
                "coined_modifier": {
                    "text": r2["clean_source_stem"],
                    "tarr_equivalent": None,
                    "semantic_concept": r2["stem_category"],
                    "is_opaque_eponym": r2["is_opaque_proper_stem"],
                    "hanzi": r2.get("extracted_hanzi"),
                },
                "coined_generic": None,
                "saint_dedication": None,
                "ruler_eponym": None,
                "special_context_flags": [],
            }
            continue

        # --- Active Stage 3 Synthesis (5,599 baronies) ---
        ht = r2["holding_type"]
        cty = r2["hierarchy"]["county"]
        ruler = coinage[bk]
        phys = phys_b[bk]
        geo_rec = geo[bk]
        fam_key = r2["coinage_morphology_family"]
        fam_obj = morph_fams[fam_key]
        compound_order = fam_obj["compound_order"]
        m_bucket = macro_family_bucket(fam_key)

        is_sea = bool(geo_rec.get("is_sea_coast", False))
        has_tradeport = bool(phys.get("has_tradeport", False))
        is_frontier = bool(geo_rec.get("is_imperial_frontier_barony", False))
        bldgs = set(phys.get("building_families") or [])
        is_hilly = bool({"hill_forts", "hill_farms", "quarries"} & bldgs) or r2["stem_category"] == "oronym"

        pois = phys.get("points_of_interest") or []
        has_buried_saint = any("buried" in p for p in pois)
        has_battle_poi = any("battle" in p for p in pois)
        has_holy_order = bool(phys.get("holy_order_lease"))
        has_shrine = bool(phys.get("saint_shrine"))

        raw_arch = ruler.get("archetype", "topographic_default")
        traits = set(ruler.get("traits") or [])
        sig = set(ruler.get("archetype_signals") or [])
        is_circ = bool(ruler.get("is_circular_house", False))
        faith_change_rule = r2["coinage_rule"] == "temple_faith_change_25y"

        # Toponym-First Archetype Arbitration (respecting POIs + county quotas)
        effective_arch = "topographic_default"
        saint_nat, saint_tarr, saint_src = ("", "", "")
        ruler_ono = ono_by_raw.get(ruler.get("raw_first_name") or "")
        house_raw = (ruler.get("house_name") or "").strip()
        house_dec = decode_ck3_personal_name(house_raw, culture=r2["coinage_culture"]) if house_raw else {"clean_name": "", "hanzi_chars": None}
        house_clean = house_dec["clean_name"]
        house_hanzi = house_dec["hanzi_chars"]
        use_house = bool(house_clean) and house_clean.lower() not in {"unknown", "lowborn"} and not is_circ

        if has_buried_saint or has_shrine or faith_change_rule:
            effective_arch = "pious_devotional"
            saint_nat, saint_tarr, saint_src = resolve_saint_dedication(bk, ruler, phys, phys_saints, shi, ono_by_raw, ono_by_clean)
        elif has_battle_poi or has_holy_order:
            effective_arch = "martial_frontier"
        elif ht == "church" and raw_arch == "pious_devotional":
            saint_nat, saint_tarr, saint_src = resolve_saint_dedication(bk, ruler, phys, phys_saints, shi, ono_by_raw, ono_by_clean)
            if saint_nat or len({"zealous", "theologian", "pilgrim", "monk", "saint"} & traits) >= 1:
                effective_arch = "pious_devotional"
            else:
                effective_arch = "topographic_default"
        elif raw_arch == "pious_devotional":
            if ({"zealous", "saint", "pilgrim"} & traits) and county_pious_secular_used[cty] < 1:
                saint_nat, saint_tarr, saint_src = resolve_saint_dedication(bk, ruler, phys, phys_saints, shi, ono_by_raw, ono_by_clean)
                if saint_nat:
                    effective_arch = "pious_devotional"
                    county_pious_secular_used[cty] += 1
        elif raw_arch == "vain_dynastic" and not is_circ and county_vain_used[cty] < 1:
            if ruler_ono or use_house:
                effective_arch = "vain_dynastic"
                county_vain_used[cty] += 1
        elif (
            ht in {"castle", "city"}
            and not is_circ
            and county_vain_used[cty] < 1
            and ({"arrogant", "ambitious", "august"} & traits)
            and (ruler_ono or use_house)
            and (int(hashlib.md5(bk.encode()).hexdigest()[:4], 16) % 10 < 5)
        ):
            effective_arch = "vain_dynastic"
            county_vain_used[cty] += 1
        elif raw_arch == "martial_frontier" and (ht == "castle" or is_frontier or ({"brave", "strategist", "holy_warrior", "reaver"} & traits)):
            effective_arch = "martial_frontier"
        elif raw_arch == "mercantile_civic" and (ht == "city" or has_tradeport or "guild_halls" in bldgs):
            effective_arch = "mercantile_civic"
        elif ht == "church" and county_pious_secular_used[cty] < 1 and len({"monastic_schools", "hospices"} & bldgs) >= 2:
            # Occasional institutional pious foundation on well-endowed temples
            saint_nat, saint_tarr, saint_src = resolve_saint_dedication(bk, ruler, phys, phys_saints, shi, ono_by_raw, ono_by_clean)
            effective_arch = "pious_devotional" if saint_nat else "topographic_default"

        effective_archetype_counts[effective_arch] += 1

        # Select native generic from coinage_culture morphology family
        gen_obj = select_family_generic(
            fam_obj=fam_obj,
            holding_type=ht,
            archetype=effective_arch,
            is_sea_coast=is_sea,
            has_tradeport=has_tradeport,
            is_frontier=is_frontier,
            is_hilly=is_hilly,
            barony_key=bk,
        )
        if gen_obj.get("gate") == "sea_coast":
            sea_gated_harbor_count += 1
        elif gen_obj.get("gate") == "waterborne":
            inland_waterborne_count += 1

        # --- Special Branch: Stage 3 Two-Character Classical Chinese Coinage ---
        is_sino_coined = (r2["stage1_track"] == "Track_S_post867_coined_compound") and (
            bool(cult_bridge.get(r2["coinage_culture"], {}).get("is_sinosphere_heritage"))
        )
        coined_hanzi: str | None = None
        if is_sino_coined:
            mod_hz, mod_concept, mod_gloss = deterministic_pick(SINO_MODIFIERS_BY_ARCHETYPE[effective_arch], f"{bk}:sino_mod")
            cls_cands = [
                (hz, gl, gt) for hz, gl, gt in SINO_CLASSIFIER_BY_HOLDING[ht]
                if not (gt == "sea_coast" and not is_sea)
            ]
            cls_hz, cls_gl, cls_gt = deterministic_pick(cls_cands, f"{bk}:sino_cls")
            coined_hanzi = f"{mod_hz}{cls_hz}"
            coined_form = coined_hanzi
            mod_record = {
                "text": mod_hz,
                "tarr_equivalent": None,
                "semantic_concept": mod_concept,
                "gloss_en": mod_gloss,
                "is_opaque_eponym": False,
                "hanzi": mod_hz,
            }
            coined_gen = {
                "native_form": cls_hz,
                "tarr_calque": gen_obj["tarr_calque"],
                "affix_position": "suffix",
                "joiner": "",
                "gloss": cls_gl,
                "gate": cls_gt,
            }
            synthesis_pattern_counts["sino_2char_coined"] += 1
            stage3_mode = "sino_2char_coined"
            ruler_eponym_rec = None
            saint_rec = None

        else:
            # Clean landscape stem from Stage 2
            land_raw = r2["clean_source_stem"]
            land_stem = extract_clean_compound_stem(land_raw)

            ruler_eponym_rec = None
            saint_rec = None
            mod_hanzi = r2.get("extracted_hanzi")

            if effective_arch == "pious_devotional":
                if saint_nat:
                    # Saint sanctuary dedication (Priority 1)
                    # Override generic on Christian church with Zant- if Zant- is available or monastery generic
                    if ht == "church" and fam_key in {"tarraconian_imperial", "high_german", "low_german_dutch"} and (has_buried_saint or has_shrine):
                        mod_text = saint_nat
                        gen_obj = next((g for g in fam_obj["generics"]["church"] if "Zant" in g["form"] or "Saint" in g["form"]), gen_obj)
                    else:
                        mod_text = saint_nat
                    coined_form = assemble_compound(mod_text, gen_obj, compound_order)
                    mod_record = {
                        "text": mod_text,
                        "tarr_equivalent": saint_tarr,
                        "semantic_concept": "saint_dedication",
                        "gloss_en": f"Saint {saint_nat}",
                        "is_opaque_eponym": True,
                        "hanzi": None,
                    }
                    saint_rec = {"native_name": saint_nat, "tarr_name": saint_tarr, "source": saint_src}
                    synthesis_pattern_counts["pious_saint_dedication"] += 1
                    stage3_mode = "synthesized_pious_saint"
                else:
                    # Generic devotional modifier (Priority 2)
                    bucket_opts = CONCEPT_NATIVE_GLOSS["pious_generic"].get(m_bucket) or CONCEPT_NATIVE_GLOSS["pious_generic"]["default"]
                    mod_text = deterministic_pick(list(bucket_opts), f"{bk}:pious_mod")
                    coined_form = assemble_compound(mod_text, gen_obj, compound_order)
                    mod_record = {
                        "text": mod_text,
                        "tarr_equivalent": deterministic_pick(list(CONCEPT_NATIVE_GLOSS["pious_generic"]["tarr"]), f"{bk}:pious_tarr"),
                        "semantic_concept": "holy_sacred",
                        "gloss_en": "holy / sacred",
                        "is_opaque_eponym": False,
                        "hanzi": None,
                    }
                    synthesis_pattern_counts["pious_abstract"] += 1
                    stage3_mode = "synthesized_pious_abstract"

            elif effective_arch == "vain_dynastic":
                # Choose between cleaned first_name (70%) and non-circular house_name (30% on castles/cities when available)
                use_dyn = use_house and (ht in {"castle", "church"} and int(hashlib.md5(bk.encode()).hexdigest()[:4], 16) % 10 < 3)
                if use_dyn or not ruler_ono:
                    mod_nat = house_clean
                    mod_tarr = ono_by_clean.get(house_clean, {}).get("tarr_compound_prefix", house_clean)
                    mod_hz_eponym = house_hanzi
                    eponym_kind = "dynasty_house"
                else:
                    mod_nat = ruler_ono["clean_name"]
                    mod_tarr = ruler_ono["tarr_compound_prefix"] if gen_obj["affix_position"] == "suffix" else ruler_ono["tarr_name"]
                    mod_hz_eponym = ruler_ono.get("hanzi_chars")
                    eponym_kind = "ruler_personal_name"
                coined_form = assemble_compound(mod_nat, gen_obj, compound_order)
                mod_record = {
                    "text": mod_nat,
                    "tarr_equivalent": mod_tarr,
                    "semantic_concept": eponym_kind,
                    "gloss_en": f"Founded by {mod_nat}",
                    "is_opaque_eponym": True,
                    "hanzi": mod_hz_eponym,
                }
                ruler_eponym_rec = {
                    "kind": eponym_kind,
                    "raw_first_name": ruler.get("raw_first_name"),
                    "clean_name": ruler_ono["clean_name"] if ruler_ono else ruler.get("clean_first_name"),
                    "tarr_name": ruler_ono["tarr_name"] if ruler_ono else None,
                    "tarr_compound_prefix": mod_tarr,
                    "house_name": house_clean if use_house else None,
                    "holder_id": ruler.get("holder_id"),
                }
                synthesis_pattern_counts["vain_eponymous"] += 1
                stage3_mode = "synthesized_vain_eponym"

            elif effective_arch == "martial_frontier":
                if has_battle_poi or has_holy_order or ht == "castle":
                    cfg_key = "martial_battle" if has_battle_poi else "martial_castle"
                    # 65% landscape + martial fort generic, 35% pure martial modifier (higher if battle POI / frontier)
                    use_abstract_martial = has_battle_poi or has_holy_order or is_frontier or (int(hashlib.md5(bk.encode()).hexdigest()[:4], 16) % 10 < 4)
                    if use_abstract_martial:
                        opts = CONCEPT_NATIVE_GLOSS[cfg_key].get(m_bucket) or CONCEPT_NATIVE_GLOSS[cfg_key]["default"]
                        mod_text = deterministic_pick(list(opts), f"{bk}:martial")
                        coined_form = assemble_compound(mod_text, gen_obj, compound_order)
                        mod_record = {
                            "text": mod_text,
                            "tarr_equivalent": deterministic_pick(list(CONCEPT_NATIVE_GLOSS[cfg_key]["tarr"]), f"{bk}:martial_t"),
                            "semantic_concept": CONCEPT_NATIVE_GLOSS[cfg_key]["concept"],
                            "gloss_en": "battle / shield / watch",
                            "is_opaque_eponym": False,
                            "hanzi": None,
                        }
                        synthesis_pattern_counts["martial_abstract"] += 1
                    else:
                        coined_form = assemble_compound(land_stem, gen_obj, compound_order)
                        mod_record = {
                            "text": land_stem,
                            "tarr_equivalent": None,
                            "semantic_concept": r2["stem_category"],
                            "gloss_en": land_raw,
                            "is_opaque_eponym": r2["is_opaque_proper_stem"],
                            "hanzi": mod_hanzi,
                        }
                        synthesis_pattern_counts["martial_landscape_fort"] += 1
                else:
                    coined_form = assemble_compound(land_stem, gen_obj, compound_order)
                    mod_record = {
                        "text": land_stem,
                        "tarr_equivalent": None,
                        "semantic_concept": r2["stem_category"],
                        "gloss_en": land_raw,
                        "is_opaque_eponym": r2["is_opaque_proper_stem"],
                        "hanzi": mod_hanzi,
                    }
                    synthesis_pattern_counts["martial_landscape_fort"] += 1
                stage3_mode = "synthesized_martial_frontier"

            elif effective_arch == "mercantile_civic":
                cfg_key = "mercantile_castle" if ht == "castle" else "mercantile_city"
                # Prefer landscape/hydronym + mercantile/sea-coast/waterborne generic (~75%), or chartered market coin (~25%)
                use_charter = (ht == "castle") or (int(hashlib.md5(bk.encode()).hexdigest()[:4], 16) % 10 < 3)
                if use_charter:
                    opts = CONCEPT_NATIVE_GLOSS[cfg_key].get(m_bucket) or CONCEPT_NATIVE_GLOSS[cfg_key]["default"]
                    mod_text = deterministic_pick(list(opts), f"{bk}:merc")
                    coined_form = assemble_compound(mod_text, gen_obj, compound_order)
                    mod_record = {
                        "text": mod_text,
                        "tarr_equivalent": deterministic_pick(list(CONCEPT_NATIVE_GLOSS[cfg_key]["tarr"]), f"{bk}:merc_t"),
                        "semantic_concept": CONCEPT_NATIVE_GLOSS[cfg_key]["concept"],
                        "gloss_en": "chartered market / toll",
                        "is_opaque_eponym": False,
                        "hanzi": None,
                    }
                    synthesis_pattern_counts["mercantile_charter"] += 1
                else:
                    coined_form = assemble_compound(land_stem, gen_obj, compound_order)
                    mod_record = {
                        "text": land_stem,
                        "tarr_equivalent": None,
                        "semantic_concept": r2["stem_category"],
                        "gloss_en": land_raw,
                        "is_opaque_eponym": r2["is_opaque_proper_stem"],
                        "hanzi": mod_hanzi,
                    }
                    synthesis_pattern_counts["mercantile_landscape_port"] += 1
                stage3_mode = "synthesized_mercantile_civic"

            else:
                # Topographic / Natural Default: Stage 2 NTR stem (or pre-867 stem) + native generic!
                coined_form = assemble_compound(land_stem, gen_obj, compound_order)
                b_hint = building_concept_hint(phys, r2["stem_category"])
                mod_record = {
                    "text": land_stem,
                    "tarr_equivalent": None,
                    "semantic_concept": r2["stem_category"],
                    "gloss_en": land_raw,
                    "is_opaque_eponym": r2["is_opaque_proper_stem"],
                    "hanzi": mod_hanzi,
                    "building_hint": b_hint,
                }
                synthesis_pattern_counts["topographic_ntr_compound"] += 1
                stage3_mode = "synthesized_topographic_default"

            coined_gen = {
                "native_form": gen_obj["form"],
                "tarr_calque": gen_obj["tarr_calque"],
                "affix_position": gen_obj["affix_position"],
                "joiner": gen_obj["joiner"],
                "gloss": gen_obj["gloss"],
                "gate": gen_obj.get("gate"),
            }

        ctx_flags = []
        if is_sea:
            ctx_flags.append("sea_coast")
        elif has_tradeport:
            ctx_flags.append("inland_tradeport")
        if is_frontier:
            ctx_flags.append("imperial_frontier")
        if has_buried_saint:
            ctx_flags.append("poi_buried_saint")
        if has_battle_poi:
            ctx_flags.append("poi_battle")
        if has_holy_order:
            ctx_flags.append("holy_order_lease")
        if phys.get("special_building_type"):
            ctx_flags.append(f"special:{phys['special_building_type']}")
        if phys.get("great_building_type"):
            ctx_flags.append(f"great:{phys['great_building_type']}")

        stage3_mode_counts[stage3_mode] += 1

        stage3_baronies[bk] = {
            **r2,
            "stage3_mode": stage3_mode,
            "raw_ruler_archetype": raw_arch,
            "effective_archetype": effective_arch,
            "coined_source_form": coined_form,
            "coined_hanzi": coined_hanzi or r2.get("extracted_hanzi"),
            "coined_compound_order": compound_order,
            "coined_modifier": mod_record,
            "coined_generic": coined_gen,
            "saint_dedication": saint_rec,
            "ruler_eponym": ruler_eponym_rec,
            "special_context_flags": ctx_flags,
        }

    # Re-sort output cleanly by barony_key
    ordered_baronies = {bk: stage3_baronies[bk] for bk in sorted(stage3_baronies.keys())}

    s3_total = sum(effective_archetype_counts.values())
    arch_shares = {
        k: round(100.0 * v / s3_total, 2) for k, v in effective_archetype_counts.items()
    }

    payload = {
        "metadata": {
            "schema_version": "1.0.0",
            "pipeline_stage": "stage_3_archetype_and_structural_synthesis",
            "total_baronies": len(ordered_baronies),
            "occupied_baronies": 10239,
            "unoccupied_baronies": 1058,
            "stage3_synthesized_count": s3_total,
            "stage3_passthrough_count": stage3_mode_counts["passthrough_stage2_stem"],
            "effective_archetype_counts": dict(effective_archetype_counts),
            "effective_archetype_shares_pct": arch_shares,
            "synthesis_pattern_counts": dict(synthesis_pattern_counts),
            "sea_gated_harbor_generics": sea_gated_harbor_count,
            "inland_waterborne_generics": inland_waterborne_count,
        },
        "baronies": ordered_baronies,
    }
    return payload


def main() -> None:
    payload = run_stage3()
    out_path = DATA_DIR / "pipeline_stage3_synthesized.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
    print(f"Wrote {out_path} ({out_path.stat().st_size / (1024*1024):.2f} MB)")
    print("Stage 3 metadata:", json.dumps(payload["metadata"], indent=2))


if __name__ == "__main__":
    main()

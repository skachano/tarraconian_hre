#!/usr/bin/env python3
"""
tarraconian_phonotactics.py

Modular, spec-driven phonotactic validator for Tarraconian Chancellery toponyms
(barony-tier through empire-tier). Reads all inventories, morpheme boundaries,
syllable templates, rule definitions, and exemptions from:
    data/tarraconian_phonotactics.yaml

Covers all four validation layers from tarraconian_linguistics_guide.md:
    - L1_orthography      : Character set, circumflexes, foreign Romanization leaks
    - L2_positional       : Universal Auslautverhärtung, Rhine-Moselle shifts, z-/tz-
    - L3_syllable_cluster : Phoneme-level #C0^3 onsets, C0^4# codas, sonority & liquids
    - L4_metrical_stratum : Stress-to-Weight (Rule 6), final -a reduction, stratum j-audit

Drop-in compatibility:
    `check_title_phonotactics(raw_title, key="", source_context="")` returns a list of
    formatted issue strings (errors only by default) so callers such as
    `pipeline_stage5_sound_laws.py`, `pipeline_stage6_disambiguation.py`, and
    `audit_phonotactics_titles.py` consume one unified ruleset.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from compound_stem_utils import BOUND_TARR_SUFFIX_RE
from typing import Any, Iterable

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - stdlib fallback
    yaml = None


# ---------------------------------------------------------------------------
# Zero-dependency YAML loader (used automatically when PyYAML is unavailable)
# ---------------------------------------------------------------------------

def _parse_yaml_scalar(v: str) -> Any:
    v = v.strip()
    if v in ("true", "True"):
        return True
    if v in ("false", "False"):
        return False
    if v in ("null", "~", ""):
        return None
    if v.startswith('"') and v.endswith('"'):
        return json.loads(v)
    if v.startswith("'") and v.endswith("'"):
        return v[1:-1]
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    if re.fullmatch(r"-?\d+\.\d+", v):
        return float(v)
    return v


def _parse_yaml_flow(s: str) -> Any:
    s = s.strip()
    if s == "[]":
        return []
    if s == "{}":
        return {}
    if s.startswith("{"):
        fixed = re.sub(
            r"([{,]\s*)([A-Za-z0-9_]+)\s*:",
            lambda m: f'{m.group(1)}"{m.group(2)}":',
            s,
        )
        return json.loads(fixed)
    return json.loads(s)


def _strip_yaml_comment(line: str) -> str:
    in_q: str | None = None
    for idx, ch in enumerate(line):
        if ch in ('"', "'") and (idx == 0 or line[idx - 1] != "\\"):
            if in_q == ch:
                in_q = None
            elif in_q is None:
                in_q = ch
        elif ch == "#" and in_q is None and (idx == 0 or line[idx - 1].isspace()):
            return line[:idx].rstrip()
    return line.rstrip()


def load_yaml_spec(text: str) -> dict[str, Any]:
    """Load data/tarraconian_phonotactics.yaml using PyYAML if present, else stdlib fallback."""
    if yaml is not None:
        return yaml.safe_load(text)

    lines: list[tuple[int, str]] = []
    for raw in text.splitlines():
        cleaned = _strip_yaml_comment(raw)
        if cleaned.strip():
            indent = len(cleaned) - len(cleaned.lstrip(" "))
            lines.append((indent, cleaned.lstrip(" ")))

    def parse_block(idx: int, min_indent: int) -> tuple[Any, int]:
        if idx >= len(lines):
            return None, idx
        if lines[idx][1].startswith("- "):
            arr: list[Any] = []
            while idx < len(lines) and lines[idx][0] == min_indent and lines[idx][1].startswith("- "):
                item_s = lines[idx][1][2:].strip()
                if item_s.startswith(("{", "[")):
                    arr.append(_parse_yaml_flow(item_s))
                else:
                    arr.append(_parse_yaml_scalar(item_s))
                idx += 1
            return arr, idx

        obj: dict[str, Any] = {}
        while idx < len(lines) and lines[idx][0] == min_indent:
            content = lines[idx][1]
            key_raw, _, rest = content.partition(":")
            key = _parse_yaml_scalar(key_raw)
            rest = rest.strip()
            idx += 1
            if rest == "":
                if idx < len(lines) and lines[idx][0] > min_indent:
                    val, idx = parse_block(idx, lines[idx][0])
                else:
                    val = {}
                obj[key] = val
            elif rest.startswith(("{", "[")):
                obj[key] = _parse_yaml_flow(rest)
            else:
                obj[key] = _parse_yaml_scalar(rest)
        return obj, idx

    res, _ = parse_block(0, lines[0][0])
    return res


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Phoneme:
    grapheme: str
    symbol: str
    kind: str  # "V" or "C"
    weight: int = 0  # 1 = short V, 2 = long V / diphthong, 0 = C


@dataclass(frozen=True)
class Syllable:
    onset: tuple[Phoneme, ...]
    nucleus: Phoneme
    coda: tuple[Phoneme, ...]

    @property
    def is_open(self) -> bool:
        return len(self.coda) == 0

    @property
    def morae(self) -> int:
        return self.nucleus.weight + (1 if self.coda else 0)

    def render(self) -> str:
        o = "".join(p.symbol for p in self.onset)
        c = "".join(p.symbol for p in self.coda)
        return f"{o}{self.nucleus.symbol}{c}"


@dataclass(frozen=True)
class ValidationContext:
    """Optional provenance context from barony_resolutions_v2.json."""
    title_key: str = ""
    pipeline_track: str = ""
    coinage_culture: str = ""
    transmission_culture: str = ""
    macro_family: str = ""
    daughter_dialect: str = ""
    is_sinosphere: bool = False


@dataclass(frozen=True)
class Violation:
    rule_id: str
    layer: str
    severity: str  # "error" or "warning"
    token: str
    morpheme: str
    message: str
    guide_ref: str
    suggestion: str = ""
    title_key: str = ""

    def format_short(self) -> str:
        loc = f"'{self.token}'" if self.morpheme == self.token else f"'{self.token}' (morpheme '{self.morpheme}')"
        return f"[{self.rule_id}|{self.severity}] {loc}: {self.message}"


# ---------------------------------------------------------------------------
# Stage 1: Title Cleaning & Morpheme Boundary Segmentation
# ---------------------------------------------------------------------------

class MorphemeSegmenter:
    """Splits titles into tokens and marks productive Tarraconian compound seams."""

    def __init__(self, spec: dict[str, Any]) -> None:
        morph = spec["morphology"]
        self.particles: set[str] = {p.lower() for p in morph["lowercase_particles"]}
        prefixes_alt = "|".join(re.escape(p) for p in morph["title_prefixes"])
        self._title_prefix_re = re.compile(
            rf"^(?:{prefixes_alt})\s+van\s+(?:dem\s+|der\s+|den\s+)?",
            re.IGNORECASE,
        )
        # Longest-first suffix table for deterministic compound seam detection
        self.suffixes: list[str] = sorted(
            {s.lower() for s in morph["compound_suffixes"]},
            key=len,
            reverse=True,
        )
        self.prefixes: list[str] = sorted(
            {p.lower() for p in morph["compound_prefixes"]},
            key=len,
            reverse=True,
        )

    def clean_title(self, raw_title: str) -> str:
        s = raw_title.strip()
        while re.search(r"\([^()]*\)", s):
            s = re.sub(r"\([^()]*\)", "", s)
        while re.search(r"\[[^\[\]]*\]", s):
            s = re.sub(r"\[[^\[\]]*\]", "", s)
        s = s.replace("**", "").replace("*", "")
        s = self._title_prefix_re.sub("", s)
        return s.strip("()*,; ")

    def tokenize(self, cleaned_title: str) -> list[str]:
        return [tok for tok in re.split(r"[\s\-]+", cleaned_title) if tok]

    def segment_compound(self, token: str) -> list[str]:
        """
        Recursively peel known productive Tarraconian prefixes/suffixes so
        compound seams (e.g., Grôz+hâven, Ôst+sachsen) are visible to rules.
        """
        if len(token) < 5 or token.lower() in self.particles:
            return [token]

        low = token.lower()

        for pref in self.prefixes:
            if low.startswith(pref) and len(token) - len(pref) >= 3:
                left = token[: len(pref)]
                right = token[len(pref) :]
                return [left] + self.segment_compound(right)

        for suf in self.suffixes:
            if low.endswith(suf) and len(token) - len(suf) >= 2:
                stem = token[: len(token) - len(suf)]
                tail = token[len(token) - len(suf) :]
                if tail.lower().startswith("h") and stem.lower().endswith("sc"):
                    continue
                return self.segment_compound(stem) + [tail]

        return [token]


# ---------------------------------------------------------------------------
# Stage 2: Grapheme-to-Phoneme (G2P) & Syllabification Engine
# ---------------------------------------------------------------------------

class PhonologyEngine:
    """Converts Tarraconian orthography into Phoneme streams and Syllables."""

    def __init__(self, spec: dict[str, Any]) -> None:
        inv = spec["inventory"]
        self.g2p_entries: list[dict[str, Any]] = inv["grapheme_to_phoneme"]
        self.sonority: dict[str, int] = inv["sonority"]
        tmpl = spec["syllable_template"]
        self.permitted_complex_onsets: set[tuple[str, ...]] = {
            tuple(o) for o in tmpl["permitted_complex_onsets"]
        }
        self._muta_liquida: set[tuple[str, str]] = {
            (o[0], o[1]) for o in self.permitted_complex_onsets if len(o) == 2
        }

    def to_phonemes(self, morpheme: str) -> list[Phoneme]:
        s = morpheme.lower().replace("'", "")
        out: list[Phoneme] = []
        i = 0
        n = len(s)
        all_vowels = "aeiouyâêîôûäöüïë"
        while i < n:
            # Context-sensitive ny/nh -> [ɲ] only before another vowel (never clip Nordic/Slavic Ny- as in Nyköbing)
            if (s.startswith("ny", i) or s.startswith("nh", i)) and (i + 2 >= n or s[i + 2] not in all_vowels):
                out.append(Phoneme("n", "n", "C", 0))
                i += 1
                continue
            # Context-sensitive qu before another vowel -> [kw]; otherwise q=[k] + u=[ʊ]
            if s.startswith("qu", i) and i + 2 < n and s[i + 2] in all_vowels:
                out.append(Phoneme("qu", "kw", "C", 0))
                i += 2
                continue
            # Context-sensitive Catalan/Romance gu before front vowel -> [ɡ]
            if s.startswith("gu", i) and i + 2 < n and s[i + 2] in "eiêîy":
                out.append(Phoneme("gu", "ɡ", "C", 0))
                i += 2
                continue
            # Context-sensitive c before front vowel -> [ts]
            if s[i] == "c" and i + 1 < n and s[i + 1] in "eiêîy":
                out.append(Phoneme("c", "ts", "C", 0))
                i += 1
                continue

            matched = False
            for entry in self.g2p_entries:
                g = entry["grapheme"]
                if s.startswith(g, i):
                    sym = entry["phoneme"]
                    # Palatal allophone ç after front vowel
                    if g == "ch" and out and out[-1].kind == "V" and out[-1].symbol in {"ɪ", "iː", "i", "ɛ", "eː", "e", "yː", "øː", "aɪ", "ɛɪ", "ɔʏ"}:
                        sym = "ç"
                    out.append(Phoneme(g, sym, entry["kind"], int(entry.get("weight", 0))))
                    i += len(g)
                    matched = True
                    break
            if not matched:
                if s[i].isalpha():
                    out.append(Phoneme(s[i], s[i], "C", 0))
                i += 1
        return out

    def syllabify(self, phonemes: list[Phoneme]) -> list[Syllable]:
        v_indices = [idx for idx, p in enumerate(phonemes) if p.kind == "V"]
        if not v_indices:
            return []

        breaks: set[int] = set()
        for k in range(len(v_indices) - 1):
            v1 = v_indices[k]
            v2 = v_indices[k + 1]
            inter = phonemes[v1 + 1 : v2]
            nc = len(inter)
            if nc <= 1:
                breaks.add(v1 + 1)
            elif nc == 2:
                pair = (inter[0].symbol, inter[1].symbol)
                if pair in self._muta_liquida:
                    breaks.add(v1 + 1)
                else:
                    breaks.add(v1 + 2)
            else:
                last3 = tuple(p.symbol for p in inter[-3:])
                last2 = tuple(p.symbol for p in inter[-2:])
                if last3 in self.permitted_complex_onsets:
                    breaks.add(v2 - 3)
                elif last2 in self.permitted_complex_onsets:
                    breaks.add(v2 - 2)
                else:
                    breaks.add(v2 - 1)

        syllables: list[Syllable] = []
        chunk: list[Phoneme] = []
        for idx, ph in enumerate(phonemes):
            if idx in breaks and chunk:
                syllables.append(self._build_syllable(chunk))
                chunk = []
            chunk.append(ph)
        if chunk:
            syllables.append(self._build_syllable(chunk))
        return syllables

    @staticmethod
    def _build_syllable(chunk: list[Phoneme]) -> Syllable:
        v_pos = next(i for i, p in enumerate(chunk) if p.kind == "V")
        return Syllable(
            onset=tuple(chunk[:v_pos]),
            nucleus=chunk[v_pos],
            coda=tuple(chunk[v_pos + 1 :]),
        )

    def predict_primary_stress_index(self, syllables: list[Syllable], morpheme: str) -> int:
        """
        Rule 6 metrical stress assignment:
          1. Weight-to-Stress: rightmost heavy circumflex syllable if present
          2. Paroxytone if final syllable is schwa -e
          3. Germanic trochaic default (initial syllable)
        """
        if len(syllables) <= 1:
            return 0
        long_idxs = [i for i, syl in enumerate(syllables) if syl.nucleus.grapheme in {"â", "ê", "î", "ô", "û"}]
        if long_idxs:
            return long_idxs[-1]
        if morpheme.lower().endswith("e") and len(syllables) >= 2:
            return len(syllables) - 2
        return 0


# ---------------------------------------------------------------------------
# Stage 3: Four-Layer Declarative Validator
# ---------------------------------------------------------------------------

class TarraconianPhonotacticsValidator:
    """Evaluates Tarraconian titles against all four layers of data/tarraconian_phonotactics.yaml."""

    def __init__(self, spec_path: str | Path | None = None) -> None:
        if spec_path is None:
            spec_path = Path(__file__).resolve().parent.parent / "data" / "tarraconian_phonotactics.yaml"
        self.spec_path = Path(spec_path)
        self.spec: dict[str, Any] = load_yaml_spec(self.spec_path.read_text(encoding="utf-8"))

        self.allowed_chars: set[str] = set(self.spec["inventory"]["allowed_chars"])
        self.rules: dict[str, dict[str, Any]] = self.spec["rules"]
        self.segmenter = MorphemeSegmenter(self.spec)
        self.phonology = PhonologyEngine(self.spec)

        ex = self.spec.get("exemptions", {})
        self.global_exempt: set[str] = {t.lower() for t in ex.get("global_tokens", [])}
        self.rule_exempt: dict[str, list[str]] = {
            rid: [p.lower() for p in pats]
            for rid, pats in ex.get("by_rule", {}).items()
        }
        self.forbidden_initials: list[dict[str, str]] = self.spec["syllable_template"]["forbidden_initial_clusters"]
        self.max_onset: int = int(self.spec["syllable_template"]["max_onset_phonemes"])
        self.max_coda: int = int(self.spec["syllable_template"]["max_coda_phonemes"])
        self.affricate_j_families: set[str] = set(
            self.spec["stratum_profiles"]["affricate_j_suspect_families"]
        )
        self.dialect_profiles: dict[str, dict[str, Any]] = self.spec["stratum_profiles"]["daughter_dialects"]

    def _is_exempt(self, rule_id: str, token: str, ctx: ValidationContext) -> bool:
        low = token.lower()
        if low in self.global_exempt:
            return True
        for prefix in self.rule_exempt.get(rule_id, []):
            if prefix in low:
                return True
        if ctx.daughter_dialect and ctx.daughter_dialect in self.dialect_profiles:
            dprof = self.dialect_profiles[ctx.daughter_dialect]
            if rule_id in dprof.get("relaxed_rules", []):
                if not dprof.get("exempt_tokens") or token in dprof["exempt_tokens"]:
                    return True
        return False

    def _make_violation(
        self,
        rule_id: str,
        token: str,
        morpheme: str,
        ctx: ValidationContext,
        detail: str = "",
        suggestion: str = "",
        severity_override: str | None = None,
    ) -> Violation | None:
        if self._is_exempt(rule_id, token, ctx):
            return None
        meta = self.rules[rule_id]
        msg = detail or meta["description"]
        return Violation(
            rule_id=rule_id,
            layer=meta["layer"],
            severity=severity_override or meta["severity"],
            token=token,
            morpheme=morpheme,
            message=msg,
            guide_ref=meta["guide_ref"],
            suggestion=suggestion,
            title_key=ctx.title_key,
        )

    @staticmethod
    def _add(out: list[Violation], v: Violation | None) -> None:
        if v is not None:
            out.append(v)

    def validate(
        self,
        raw_title: str,
        context: ValidationContext | None = None,
        include_warnings: bool = True,
    ) -> list[Violation]:
        ctx = context or ValidationContext()
        cleaned = self.segmenter.clean_title(raw_title)
        if not cleaned:
            return []

        violations: list[Violation] = []

        # Whole-string L1 character hygiene
        bad_chars = sorted({c for c in cleaned if c not in self.allowed_chars})
        if bad_chars:
            acutes = [c for c in bad_chars if c in "áéíóúÁÉÍÓÚàèìòùÀÈÌÒÙ"]
            others = [c for c in bad_chars if c not in acutes]
            if acutes:
                self._add(
                    violations,
                    self._make_violation(
                        "L1_ACUTE_OR_GRAVE_ACCENT",
                        cleaned,
                        cleaned,
                        ctx,
                        detail=f"Acute/grave accent(s) {acutes} found; use circumflexes (â, ê, î, ô, û).",
                    ),
                )
            if others:
                self._add(
                    violations,
                    self._make_violation(
                        "L1_DISALLOWED_CHAR",
                        cleaned,
                        cleaned,
                        ctx,
                        detail=f"Disallowed character(s) {others} outside 1194 Chancellery inventory.",
                    ),
                )

        # Title-level Layer 4 multi-word compounding integrity (barony tier)
        is_barony_ctx = (ctx.title_key or "").startswith("b_")
        if is_barony_ctx and " " in cleaned:
            raw_words = cleaned.split()
            attested_tracks = {
                "Track_A_retained",
                "Track_A_coinage_overrule",
                "Track_B_historical_names",
                "Track_B_existing_natural",
                "Track_S_pre867_attested",
                "Track_S_pre867_overruled",
                "Track_S_post867_historical_anchor",
            }
            if len(raw_words) >= 2 and BOUND_TARR_SUFFIX_RE.search(raw_words[-1]):
                self._add(
                    violations,
                    self._make_violation(
                        "L4_GLUED_SUFFIX_ON_MULTIWORD",
                        cleaned,
                        raw_words[-1],
                        ctx,
                        detail=f"Bound settlement suffix glued to multi-word barony '{cleaned}'.",
                    ),
                )
            if len(raw_words) >= 3 and ctx.pipeline_track and ctx.pipeline_track not in attested_tracks:
                self._add(
                    violations,
                    self._make_violation(
                        "L4_NON_ATTESTED_MAX_WORDS",
                        cleaned,
                        cleaned,
                        ctx,
                        detail=f"Non-attested barony '{cleaned}' has {len(raw_words)} words (max 2).",
                    ),
                )

        tokens = self.segmenter.tokenize(cleaned)
        for token in tokens:
            low_tok = token.lower()
            if low_tok in {"upon", "under", "the", "of"}:
                self._add(
                    violations,
                    self._make_violation(
                        "L1_ENGLISH_PREPOSITION",
                        token,
                        token,
                        ctx,
                        detail=f"Unadapted English preposition '{token}'.",
                    ),
                )
                continue

            if low_tok in self.segmenter.particles:
                continue

            morphemes = self.segmenter.segment_compound(token)

            for morph in morphemes:
                self._check_l1_morpheme(token, morph, ctx, violations)
                self._check_l2_morpheme(token, morph, ctx, violations)

            self._check_l2_boundaries(token, morphemes, ctx, violations)
            self._check_l3_syllables(token, morphemes, ctx, violations)
            self._check_l4_metrical_and_stratum(token, morphemes, ctx, violations)

        if not include_warnings:
            return [v for v in violations if v.severity == "error"]
        return violations

    # --- Layer 1: Orthography ---
    def _check_l1_morpheme(
        self, token: str, morph: str, ctx: ValidationContext, out: list[Violation]
    ) -> None:
        low = morph.lower()

        if re.search(r"(aa|oo|(?<!q)uu)", low):
            self._add(out, self._make_violation("L1_DOUBLE_VOWEL", token, morph, ctx))

        if "zh" in low:
            self._add(out, self._make_violation("L1_PINYIN_ZH", token, morph, ctx, suggestion="Use 'dsch'."))

        if re.search(r"(?<!c)sh", low):
            self._add(out, self._make_violation("L1_NON_GERMAN_SH", token, morph, ctx, suggestion="Use 'sch'."))

        if re.search(r"q(?!u)", low):
            self._add(out, self._make_violation("L1_PINYIN_Q", token, morph, ctx, suggestion="Use 'tsch'/'ch' or 'k'."))

        if "x" in low:
            sev = "error" if (ctx.is_sinosphere or ctx.pipeline_track.startswith("Track_S")) else "warning"
            self._add(out, self._make_violation("L1_PINYIN_X", token, morph, ctx, severity_override=sev))

        if "eo" in low:
            self._add(out, self._make_violation("L1_KOREAN_RR_DIGRAPH", token, morph, ctx, suggestion="Replace 'eo' with 'ô' or 'o'."))

        if (ctx.is_sinosphere or ctx.pipeline_track.startswith("Track_S")) and re.search(r"(ae|eu)", low):
            if not low.endswith("euwe"):
                self._add(out, self._make_violation("L1_SINOSPHERE_RR_VOWEL", token, morph, ctx))

        if re.search(r"([a-zâêîôûäöü])\1\1", low):
            self._add(out, self._make_violation("L1_TRIPLE_LETTER", token, morph, ctx))

    # --- Layer 2: Positional & Allophonic ---
    def _check_l2_morpheme(
        self, token: str, morph: str, ctx: ValidationContext, out: list[Violation]
    ) -> None:
        low = morph.lower()

        if re.search(r"(?<=[aeiouâêîôûäöünl])ts(?!ch)", low) and not low.endswith("ts"):
            self._add(out, self._make_violation("L2_MEDIAL_TS_NOT_TZ", token, morph, ctx, suggestion="Use '-tz-'."))

        if "kh" in low:
            self._add(out, self._make_violation("L2_FOREIGN_KH", token, morph, ctx, suggestion="Use 'ch'."))

    def _check_l2_boundaries(
        self, token: str, morphemes: list[str], ctx: ValidationContext, out: list[Violation]
    ) -> None:
        low = token.lower()
        first_m = morphemes[0]
        last_m = morphemes[-1]

        if re.match(r"^ts(?!ch)", low):
            self._add(out, self._make_violation("L2_INIT_TS_NOT_Z", token, first_m, ctx, suggestion="Use initial 'z-'."))

        for item in self.forbidden_initials:
            pat = item["pattern"]
            if low.startswith(pat):
                if pat == "kh" and any(v.rule_id == "L2_FOREIGN_KH" and v.token == token for v in out):
                    continue
                self._add(
                    out,
                    self._make_violation(
                        item["rule"],
                        token,
                        first_m,
                        ctx,
                        detail=f"Forbidden initial sequence '{pat}-' in '{token}'.",
                        suggestion=item["suggestion"],
                    ),
                )
                break

        if low.endswith("dsch"):
            self._add(out, self._make_violation("L2_FINAL_VOICED_DSCH", token, last_m, ctx, suggestion="Devoice to '-tsch'."))
        elif low.endswith("b"):
            self._add(out, self._make_violation("L2_FINAL_VOICED_B", token, last_m, ctx, suggestion="Devoice to '-p'."))
        elif low.endswith("d"):
            self._add(out, self._make_violation("L2_FINAL_VOICED_D", token, last_m, ctx, suggestion="Devoice to '-t'."))
        elif low.endswith("g") and not low.endswith("ng"):
            self._add(out, self._make_violation("L2_FINAL_VOICED_G", token, last_m, ctx, suggestion="Shift final '-g' to '-ch'."))
        elif re.search(r"[sz]k$", low):
            self._add(out, self._make_violation("L2_SLAVIC_SK_CODA", token, last_m, ctx, suggestion="Resolve to '-tzich' or '-bsch'."))
        elif re.search(r"[aeiouâêîôûäöüy]k$", low):
            self._add(out, self._make_violation("L2_FINAL_POSTVOCALIC_K", token, last_m, ctx, suggestion="Shift post-vocalic '-k' to '-ch'."))
        elif re.search(r"ts$", low) and not low.endswith("tsch"):
            self._add(out, self._make_violation("L2_FINAL_TS_NOT_TZ", token, last_m, ctx, suggestion="Spell final [ts] as '-tz'."))
        elif re.search(r"[oea]v$", low):
            self._add(out, self._make_violation("L2_SLAVIC_OV_CODA", token, last_m, ctx, suggestion="Vocalize to '-ouwe'/'-euwe'."))

    # --- Layer 3: Syllable Structure & Sonority ---
    def _check_l3_syllables(
        self, token: str, morphemes: list[str], ctx: ValidationContext, out: list[Violation]
    ) -> None:
        low_tok = token.lower()

        for morph in morphemes:
            if re.search(r"(?:^stsch|schsch|dschdsch|tschtsch|(?:tz|ts|z)tsch)", morph.lower()):
                self._add(out, self._make_violation("L3_REDUNDANT_AFFRICATE", token, morph, ctx))
                break

        # Word-final obstruent + liquid (Rule 4; exclude vowel+w/y glides like Hawr, Mawr)
        if re.search(r"[bcdfgkpqtvz][lr]$", low_tok):
            self._add(out, self._make_violation("L3_FINAL_SYLLABIC_LIQUID", token, morphemes[-1], ctx, suggestion="Insert epenthetic vowel (-er/-el) or adapt to -ouwe."))

        first_ph = self.phonology.to_phonemes(morphemes[0])
        first_syls = self.phonology.syllabify(first_ph)
        if first_syls:
            onset = first_syls[0].onset
            onset_syms = tuple(p.symbol for p in onset)
            already_onset_err = any(
                v.token == token and v.rule_id in {"L3_ILLICIT_ONSET_CLUSTER", "L3_INIT_VELAR_NASAL", "L2_NHG_SCH_SONORANT", "L2_UPPER_GERMAN_PF", "L2_INDIC_ASPIRATE", "L2_FOREIGN_KH"}
                for v in out
            )
            if not already_onset_err:
                if len(onset) > self.max_onset:
                    self._add(
                        out,
                        self._make_violation(
                            "L3_ILLICIT_ONSET_CLUSTER",
                            token,
                            morphemes[0],
                            ctx,
                            detail=f"Onset {list(onset_syms)} exceeds #C0^{self.max_onset} template.",
                        ),
                    )
                elif len(onset) >= 2 and onset_syms not in self.phonology.permitted_complex_onsets:
                    self._add(
                        out,
                        self._make_violation(
                            "L3_ILLICIT_ONSET_CLUSTER",
                            token,
                            morphemes[0],
                            ctx,
                            detail=f"Unpermitted initial onset cluster {list(onset_syms)}.",
                        ),
                    )

        last_ph = self.phonology.to_phonemes(morphemes[-1])
        last_syls = self.phonology.syllabify(last_ph)
        if last_syls:
            coda = last_syls[-1].coda
            if len(coda) > self.max_coda:
                self._add(
                    out,
                    self._make_violation(
                        "L3_EXCESSIVE_CODA",
                        token,
                        morphemes[-1],
                        ctx,
                        detail=f"Final coda {[p.symbol for p in coda]} exceeds C0^{self.max_coda}# template.",
                    ),
                )

        for morph in morphemes:
            phs = self.phonology.to_phonemes(morph)
            run = 0
            for p in phs:
                if p.kind == "C":
                    run += 1
                    if run > 4:
                        self._add(out, self._make_violation("L3_EXCESSIVE_MEDIAL_CLUSTER", token, morph, ctx))
                        break
                else:
                    run = 0

    # --- Layer 4: Metrical & Stratum Consistency ---
    def _check_l4_metrical_and_stratum(
        self, token: str, morphemes: list[str], ctx: ValidationContext, out: list[Violation]
    ) -> None:
        root = morphemes[0]
        phs = self.phonology.to_phonemes(root)
        syls = self.phonology.syllabify(phs)
        if len(syls) >= 2:
            stress_idx = self.phonology.predict_primary_stress_index(syls, root)
            stressed = syls[stress_idx]
            if stressed.is_open and stressed.morae < 2:
                self._add(
                    out,
                    self._make_violation(
                        "L4_STRESS_TO_WEIGHT",
                        token,
                        root,
                        ctx,
                        detail=f"Primary stressed open syllable '{stressed.render()}' is monomoraic (Rule 6.1 expects circumflex long vowel or closed coda).",
                    ),
                )

        full_syls = self.phonology.syllabify(self.phonology.to_phonemes(token))
        if len(full_syls) >= 2 and token.endswith("a"):
            self._add(
                out,
                self._make_violation(
                    "L4_FINAL_UNREDUCED_A",
                    token,
                    morphemes[-1],
                    ctx,
                    suggestion="Consider reducing unaccented final '-a' to '-e' (or mark stressed '-â').",
                ),
            )

        in_suspect_stratum = (
            ctx.is_sinosphere
            or ctx.pipeline_track.startswith("Track_S")
            or ctx.macro_family.lower() in self.affricate_j_families
        )
        if in_suspect_stratum:
            low = token.lower()
            stripped_j = re.sub(r"[nl]j", "", low)
            if "j" in stripped_j:
                self._add(
                    out,
                    self._make_violation(
                        "L4_BARE_J_AFFRICATE_LEAK",
                        token,
                        token,
                        ctx,
                        detail=f"Bare 'j' in '{token}' on stratum '{ctx.macro_family or ctx.pipeline_track}'; verify glide [j] vs. affricate 'dsch'.",
                    ),
                )


# ---------------------------------------------------------------------------
# Drop-in Compatibility Wrapper for Legacy Callers
# ---------------------------------------------------------------------------

_DEFAULT_VALIDATOR: TarraconianPhonotacticsValidator | None = None


def get_default_validator(spec_path: str | Path | None = None) -> TarraconianPhonotacticsValidator:
    global _DEFAULT_VALIDATOR
    if _DEFAULT_VALIDATOR is None or spec_path is not None:
        _DEFAULT_VALIDATOR = TarraconianPhonotacticsValidator(spec_path)
    return _DEFAULT_VALIDATOR


def check_title_phonotactics(
    raw_title: str,
    key: str = "",
    source_context: str = "",
    *,
    include_warnings: bool = False,
    context: ValidationContext | None = None,
) -> list[str]:
    """
    Spec-driven drop-in replacement for `audit_phonotactics_titles.check_title_phonotactics`.
    Splits alternate forms (`or`, `/`) and returns formatted violation strings (errors only by default).
    """
    validator = get_default_validator()
    if context is None:
        src_l = (source_context or "").lower()
        is_sino = src_l.startswith("track_s") or "sino" in src_l
        ctx = ValidationContext(title_key=key, pipeline_track=source_context, is_sinosphere=is_sino)
    else:
        ctx = context
    parts = re.split(r"\s*(?:\*\(or\s+|\bor\b|\/)\s*", raw_title)
    issues: list[str] = []
    for part in parts:
        low = part.lower()
        if not part.strip() or any(skip in low for skip in ("direct vanilla", "attested", "calque")):
            continue
        for v in validator.validate(part, context=ctx, include_warnings=include_warnings):
            issues.append(v.format_short())
    return issues


# ---------------------------------------------------------------------------
# CLI: Audit barony_resolutions_v2.json
# ---------------------------------------------------------------------------

def audit_baronies_file(
    baronies_json: Path,
    spec_path: Path | None = None,
    include_warnings: bool = True,
    sample_limit: int = 5,
) -> dict[str, Any]:
    validator = TarraconianPhonotacticsValidator(spec_path)
    with open(baronies_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    baronies = data.get("baronies", data)
    items: Iterable[tuple[str, dict[str, Any]]] = (
        [(b.get("barony_key", ""), b) for b in baronies]
        if isinstance(baronies, list)
        else baronies.items()
    )

    rule_counts: Counter[str] = Counter()
    layer_counts: Counter[str] = Counter()
    severity_counts: Counter[str] = Counter()
    samples: dict[str, list[dict[str, str]]] = {}
    checked = 0
    baronies_with_errors = 0
    baronies_with_warnings = 0

    for bk, rec in items:
        if not isinstance(rec, dict):
            continue
        name = rec.get("name") or rec.get("b_tarr_hist") or ""
        if not name:
            continue
        checked += 1
        track = rec.get("pipeline_track", "")
        dialect = ""
        dv = rec.get("daughter_dialect_variant")
        if isinstance(dv, dict):
            dialect = dv.get("dialect", "")
        ctx = ValidationContext(
            title_key=bk,
            pipeline_track=track,
            coinage_culture=rec.get("coinage_culture", ""),
            transmission_culture=rec.get("transmission_culture", ""),
            macro_family=rec.get("coinage_morphology_family", ""),
            daughter_dialect=dialect,
            is_sinosphere=track.startswith("Track_S"),
        )
        viols = validator.validate(name, context=ctx, include_warnings=include_warnings)
        if any(v.severity == "error" for v in viols):
            baronies_with_errors += 1
        if any(v.severity == "warning" for v in viols):
            baronies_with_warnings += 1
        for v in viols:
            rule_counts[v.rule_id] += 1
            layer_counts[v.layer] += 1
            severity_counts[v.severity] += 1
            bucket = samples.setdefault(v.rule_id, [])
            if len(bucket) < sample_limit:
                bucket.append({"barony_key": bk, "name": name, "token": v.token, "message": v.message})

    return {
        "checked_baronies": checked,
        "baronies_with_errors": baronies_with_errors,
        "baronies_with_warnings": baronies_with_warnings,
        "severity_counts": dict(severity_counts),
        "layer_counts": dict(layer_counts),
        "rule_counts": dict(rule_counts.most_common()),
        "samples": samples,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Tarraconian names against data/tarraconian_phonotactics.yaml")
    parser.add_argument("--spec", type=Path, default=None, help="Path to tarraconian_phonotactics.yaml")
    parser.add_argument("--baronies", type=Path, help="Path to data/barony_resolutions_v2.json")
    parser.add_argument("--name", type=str, help="Validate a single Tarraconian title string")
    parser.add_argument("--errors-only", action="store_true", help="Exclude L4/soft warnings")
    parser.add_argument("--json-out", type=Path, help="Write full audit report JSON to path")
    args = parser.parse_args(argv)

    if args.name:
        v = TarraconianPhonotacticsValidator(args.spec)
        res = v.validate(args.name, include_warnings=not args.errors_only)
        if not res:
            print(f"OK: {args.name}")
            return 0
        for item in res:
            print(item.format_short())
        return 1

    if args.baronies:
        report = audit_baronies_file(args.baronies, spec_path=args.spec, include_warnings=not args.errors_only)
        if args.json_out:
            args.json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Checked baronies        : {report['checked_baronies']}")
        print(f"Baronies with errors    : {report['baronies_with_errors']}")
        print(f"Baronies with warnings  : {report['baronies_with_warnings']}")
        print(f"Layer counts            : {report['layer_counts']}")
        print("\nRule breakdown:")
        for rid, cnt in report["rule_counts"].items():
            ex = ", ".join(s["name"] for s in report["samples"].get(rid, [])[:3])
            print(f"  {rid:30s}: {cnt:5d}  (e.g. {ex})")
        return 0 if report["baronies_with_errors"] == 0 else 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())

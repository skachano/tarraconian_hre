"""9th-12th century Spoken Byzantine (Middle) Greek -> Tarraconian phonological reconciler (Option A)."""

from __future__ import annotations

import re
from typing import Any

BYZANTINE_ISOS: set[str] = {"grc", "ell", "gkm"}

# Curated Imperial/Tarraconian canonical exonyms & non-Greek stems tagged grc
BYZANTINE_CURATED_TOKENS: dict[str, str] = {
    "caesarea": "Kaisarêe",
    "kaisareia": "Kaisarêe",
    "kaisereia": "Kaisarêe",
    "nicaea": "Nîkêe",
    "nikaia": "Nîkêe",
    "nikaea": "Nîkêe",
    "sebasteia": "Sebastêe",
    "sebastia": "Sebastêe",
    "laodicea": "Laodikêe",
    "laodikeia": "Laodikêe",
    "dorylaeum": "Dorîlêe",
    "dorylaion": "Dorîlêe",
    "constantinopolis": "Konstantînôpel",
    "konstantinopolis": "Konstantînôpel",
    "neapolis": "Neapel",
    "thessaloniki": "Sâlonîch",
    "thessalonica": "Sâlonîch",
    "ephesos": "Efês",
    "ephesus": "Efês",
    "athens": "Atên",
    "korinthos": "Korînt",
    "corinthus": "Korînt",
    "chalcedon": "Chalket",
    "byzantion": "Bisantz",
    "brysis": "Brüsch",
    "chios": "Chios",
    "kos": "Kos",
    "taphros": "Tâfros",
    "berenice": "Verenîke",
    "bizye": "Vîzye",
    "abydos": "Avîdos",
    "baeberdon": "Vêverdon",
    "billaios": "Villêos",
    "billaîos": "Villêos",
    "euboea": "Evîe",
    "euboia": "Evîe",
    "thaumaci": "Tavmaki",
    "mousaios": "Musêos",
    "docimium": "Dokimium",
    "buthrotum": "Butrotum",
    "scythian": "Skitian",
    "euphrátēs": "Efrâtês",
    "euphrates": "Efrât",
}

# Non-Greek tokens (Arabic, Turkic, Persian, Armenian, Latin, Malay, Italian, Albanian)
# that must NOT undergo Byzantine Greek vowel/b->v/c->k shifts.
BYZANTINE_NON_GREEK_TOKENS: set[str] = {
    "barus", "takola", "marakanda", "alexandria",
    "claudio", "claudiopolis", "brindisi", "bolzano", "agrafa",
    "bisutun", "baghras", "bahasna", "bagis", "balu", "bitan", "basiyan",
    "bahmanshir", "bahmanshīr", "baab", "mandab", "arthanuji", "al-maafir",
    "al-ma'afir", "ar-ran", "ash-shihr", "iskender", "zafar", "orhan",
    "ahvaz", "abbadan", "aiwana", "adruh", "spauta", "velež", "velez",
    "vilhelm", "boniface", "cyprian", "cypriân", "konstantinos", "konstantin",
    "patras", "split", "kos", "barata", "byalgrad", "karlotte",
    "manda", "inakir", "erta", "ertá’alé", "ertáalé", "banā", "bana",
    "elath", "ghir", "amarta", "ribât", "ribat", "kermen",
    "kaya", "kent", "masjid", "saray", "amrots", "klde", "beta", "qal'at",
    "hagios", "hagio", "p'vok'r", "p'ok'r", "kovkasribât", "kovkas",
    # Non-Greek substrate stems sometimes tagged grc by colonial/medieval holders
    "arrajan", "tawwaj", "firuzabad", "taburshiq", "zubala",
    "catabathmus", "maior", "lezhë", "lezhe",
    "fornacis", "lecce", "terracina",
    # Compound generics (keep until generic stripping/calquing)
    "burch", "stat", "kirchen", "kapelle", "wart", "munster", "meschit",
    "tempel", "marct", "hâven", "werc", "palz", "clôster", "stein", "berch",
    "bühil", "vurt", "walt", "velt", "lant", "zelle", "brunn", "port", "torn",
}

_GREEK_SUFFIX_SPLITS = (
    "phrourion", "ekklesia", "kastron", "pyrgos", "limen", "poros",
    "emporion", "moni", "polis", "ribât", "ribat", "kermen", "kaya",
    "kent", "masjid", "saray", "amrots", "klde",
    "burch", "stat", "kirchen", "kapelle", "wart", "munster", "meschit",
    "tempel", "marct", "hâven", "werc", "palz", "clôster", "stein", "berch",
    "bühil", "vurt", "walt", "velt", "lant", "zelle", "brunn", "port", "torn",
)


def _preserve_case(orig: str, repl: str) -> str:
    if not orig:
        return repl
    if orig[0].isupper():
        return repl[:1].upper() + repl[1:]
    return repl


def adapt_byzantine_greek_token(tok: str) -> str | None:
    """
    Reconcile a single 9th-12th century Spoken Byzantine Greek token into
    Tarraconian Chancellery orthography. Returns None for non-Greek/Latin tokens.
    """
    low = tok.lower()
    if low in BYZANTINE_CURATED_TOKENS:
        return BYZANTINE_CURATED_TOKENS[low]
    if low in {"de", "des", "el", "al", "pros"}:
        return tok
    # Guard Classical Latin -um / -aeum / -ium stems, apostrophe-heavy Caucasian/Arabic tokens, and non-Greek loans
    if "'" in tok or "’" in tok or low in BYZANTINE_NON_GREEK_TOKENS or low.endswith(("um", "aeum", "ium")):
        return None
    for non_gr in ("claudio", "alexandr", "panticap", "adramytt", "catyae"):
        if non_gr in low:
            return None

    # Split glued Greek/foreign compound suffix (e.g. Agranaiekklesia -> Agranai + ekklesia)
    for suf in _GREEK_SUFFIX_SPLITS:
        if len(low) > len(suf) + 2 and low.endswith(suf):
            head = tok[: -len(suf)]
            tail = tok[-len(suf) :]
            head_res = adapt_byzantine_greek_token(head)
            if head_res is None:
                return None
            # Suffixes: phrourion -> frurjen, ekklesia -> ekklesîe, pyrgos -> pirgos, polis -> pel
            tail_low = tail.lower()
            if tail_low == "phrourion":
                tail_res = "frurjen"
            elif tail_low == "ekklesia":
                tail_res = "ekklesîe"
            elif tail_low == "pyrgos":
                tail_res = "pirgos"
            elif tail_low == "kastron":
                tail_res = "kaster"
            elif tail_low == "emporion":
                tail_res = "emporjen"
            elif tail_low == "polis":
                tail_res = "pel"
            elif tail_low == "masjid":
                tail_res = "masdschit"
            else:
                tail_res = tail_low
            return head_res + tail_res

    s = tok
    # Map macrons/acutes on Greek vowels first (including accented upsilon ý/ŷ/ÿ -> î)
    pre = {
        "ē": "ê", "Ē": "Ê", "ā": "â", "Ā": "Â", "ī": "î", "Ī": "Î",
        "ō": "ô", "Ō": "Ô", "ū": "û", "Ū": "Û",
        "á": "â", "Á": "Â", "é": "ê", "É": "Ê", "í": "î", "Í": "Î",
        "ó": "ô", "Ó": "Ô", "ú": "û", "Ú": "Û",
        "ý": "î", "Ý": "Î", "ŷ": "î", "Ŷ": "Î", "ÿ": "î", "Ÿ": "Î",
        "à": "a", "À": "A", "è": "e", "È": "E", "ì": "i", "Ì": "I",
        "ò": "o", "Ò": "O", "ù": "u", "Ù": "U",
    }
    s = "".join(pre.get(c, c) for c in s)

    # 1. Consonants: ph->f, th->t, kh->ch; Latinized Greek κ <c> before front vowel/ae/oe -> k
    s = re.sub(r"ph", lambda m: _preserve_case(m.group(0), "f"), s, flags=re.I)
    s = re.sub(r"th", lambda m: _preserve_case(m.group(0), "t"), s, flags=re.I)
    s = re.sub(r"kh", lambda m: _preserve_case(m.group(0), "ch"), s, flags=re.I)
    s = re.sub(r"c(?=(?:[eiyêî]|ae|oe))", lambda m: "K" if m.group(0).isupper() else "k", s, flags=re.I)

    # 2. Classic Byzantine -eia / -aia / -aea endings -> -êe, and remaining Greek ae -> ê
    s = re.sub(r"(?:[ea][iî]a|aea)\b", "êe", s, flags=re.I)
    s = re.sub(r"ae", lambda m: _preserve_case(m.group(0), "ê"), s, flags=re.I)

    # 3. au / eu -> av / ev before vowels & voiced consonants; af / ef before voiceless or word-final
    def _au_eu_repl(m: re.Match[str]) -> str:
        diph = m.group(1)
        nxt = m.group(2) or ""
        base_v = "a" if diph[0].lower() == "a" else "e"
        if diph[0].isupper():
            base_v = base_v.upper()
        voiceless = not nxt or nxt.lower() in {"p", "t", "k", "c", "s", "f", "x"}
        # Greek χ 'ch' is voiceless; 'sch' starts with 's'
        fr = "f" if voiceless else "v"
        return base_v + fr + nxt

    s = re.sub(r"([aeAE][uûUÛ])([A-Za-zâêîôûÂÊÎÔÛ])?", _au_eu_repl, s)
    s = re.sub(r"([Ee])ff", r"\1f", s)

    # 4. ou -> u / û (handles Athagaoû -> Atagaû)
    s = re.sub(r"[oô][uû]", lambda m: _preserve_case(m.group(0), "û" if ("ô" in m.group(0).lower() or "û" in m.group(0).lower()) else "u"), s, flags=re.I)

    # 5. Itacism: ei / oi -> î, ioi -> î, ai -> ê
    s = re.sub(r"i[oô][iî]\b", "î", s, flags=re.I)
    s = re.sub(r"[eê][iî]", lambda m: _preserve_case(m.group(0), "î"), s, flags=re.I)
    s = re.sub(r"[oô][iî]", lambda m: _preserve_case(m.group(0), "î"), s, flags=re.I)
    s = re.sub(r"[aâ][iî]", lambda m: _preserve_case(m.group(0), "ê"), s, flags=re.I)

    # 6. Pre-consonantal & final upsilon y -> i (keep intervocalic/initial y+V as glide)
    s = re.sub(r"y(?![aeiouâêîôûäöü])", lambda m: "I" if m.group(0).isupper() else "i", s, flags=re.I)

    # 7. Byzantine intervocalic β (b) -> v (avoid initial #b of non-curated loan stems)
    s = re.sub(r"(?<=[aeiouâêîôû])b(?=[aeiouâêîôû])", "v", s, flags=re.I)

    # 8. Inflectional cleanup: polysyllabic -os/-on apocope (keep short 2-syllable words)
    m_os = re.match(r"^([A-Za-zÀ-ɏ]+)(os|on)$", s, flags=re.I)
    if m_os and len(m_os.group(1)) >= 5 and len(re.findall(r"[aeiouyâêîôûäöü]+", m_os.group(1), flags=re.I)) >= 2:
        s = m_os.group(1)

    return s


def adapt_byzantine_greek_to_tarraconian(stem: str) -> tuple[str, bool]:
    """Adapt a Byzantine Greek phrase/compound, reporting whether any token needs fallback."""
    s = stem.strip()
    if not s:
        return s, False
    parts = re.split(r"([\s\-]+)", s)
    out: list[str] = []
    any_fb = False
    for p in parts:
        if not p or re.fullmatch(r"[\s\-]+", p):
            out.append(p)
        elif p[0].isalpha() or any(ord(c) > 127 for c in p):
            res = adapt_byzantine_greek_token(p)
            if res is None:
                out.append(p)
                any_fb = True
            else:
                out.append(res)
        else:
            out.append(p)
    joined = "".join(out)
    if joined and joined[0].islower():
        joined = joined[0].upper() + joined[1:]
    return joined, any_fb


def is_byzantine_greek_stem(rec: dict[str, Any], trans_family: str = "") -> bool:
    """Return True when the record carries a genuine Hellenic / Byzantine Greek source stem."""
    cc = rec.get("coinage_culture") or ""
    if cc in {"Tarraconian", "Lothringian", "Croato-Tarraconian", "Alpine-Tarraconian", "Ungwârer"}:
        return False
    iso = rec.get("selected_iso") or ""
    cf = (rec.get("coinage_morphology_family") or "").lower()
    if iso in BYZANTINE_ISOS:
        return True
    # Only route un-tagged / Latin-glossed hellenic stems as Byzantine Greek (never ara/hye/fas/srp/bul/aar)
    return cf == "hellenic" and iso in {"", "und", "lat"}

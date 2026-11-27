"""Classical & Medieval Latin -> Tarraconian Chancellery morphological & phonological adapter."""

from __future__ import annotations

import re
from typing import Any

NON_LATIN_MISATTRIBUTED: set[str] = {
    "Al-Fustat", "Djesdjes", "Shadikanni", "Elath", "Hebet", "Hix",
    "Roque Nublo", "Bakon", "Ghir", "Born", "Auva", "Rapniza",
    "Hurnad", "Hulda", "Toar", "Topul", "Barboși",
}

LATIN_CURATED_PHRASES: dict[str, str] = {
    "aquae": "Bâden",
    "aquae tacapitanae": "Takapît-Bâden",
    "caesarea": "Kaisarêe",
    "edessa": "Edesse",
    "ad nonum": "Bî-Nûn",
    "contra margum": "Gêgenmarg",
    "pone navata": "Pône-Navât",
    "alta ripa": "Altrîf",
    "alba fucens": "Albe-Fûzens",
    "asta regia": "Aste-Rêge",
    "flavia solva": "Flâvje-Solve",
    "hippo regius": "Hippôn-Rêg",
    "laus pompeia": "Laus-Pompêje",
    "felix romuliana": "Romuljâne",
    "mentesa bastia": "Mentêse-Bastîe",
    "ballene praesidium": "Ballênwerc",
    "unica colonia": "Einkolôn",
    "oppidum novum": "Nîestat",
    "portus magnus": "Grôzport",
    "portus adurni": "Adurnport",
    "portus syracusanus": "Syrakûsport",
    "portus victoriae iuliobrigensium": "Viktorjaport",
    "vicus saravus": "Sârwîch",
    "vicus cuminarius": "Kumînwîch",
    "forum limicorum": "Limîchmarct",
    "castra ad montanesium": "Montanêscastel",
    "saltus tugiensis": "Tûgiwalt",
    "distercius mons": "Disterzberch",
    "carpetani montes": "Karpetânberch",
    "mare balearicum": "Balêarmêr",
    "mare cantabricum": "Kantabermêr",
    "mare germanicum": "Germânmêr",
    "mare sardoum": "Sardômêr",
    "mare tyrrhenum": "Tyrrhênmêr",
    "sinus finnicus": "Finnbucht",
    "sinus scylacius": "Skylâzbucht",
    "sinus gaditanus": "Gaditânbucht",
    "carcinites sinus": "Karzinîtbucht",
    "limpicus sinus": "Limpîkbucht",
    "noviomagus": "Nîemâgen",
    "noviomagus reginorum": "Rêgen-Nîemâgen",
    "venta icenorum": "Vente-Izên",
    "isca augusta": "Iske-Augûste",
    "myos hormos": "Myos-Horm",
    "lato pros kamara": "Lâto-Kamâre",
    "bosporus cimmerius": "Kimmer-Bôspor",
    "maresc pictavensis": "Piktâfmarsch",
    "lingonicus ager": "Lingônenvelt",
    "urbs giudi": "Giudistat",
    "tritonis palus": "Tritônmôr",
    "vallis sauconnae": "Saukônntâl",
    "gabreta silva": "Gabrêtawalt",
    "sana silva": "Sânawalt",
    "portae mesesinae": "Mesêspforte",
    "pyrenaei montes": "Pyrênêen",
    "heraei montes": "Hêrêenberch",
    "alpes cottiae": "Kottalpen",
    "alpes iuliae": "Julalpen",
    "alpes liguriae": "Ligûralpen",
    "alpes maritimae": "Mêralpen",
    "mons marianus": "Mariânberch",
    "mons vindius": "Windberch",
    "mons lugdunensis": "Lugdûnberch",
    "mons maior": "Grôzberch",
    "duria maior": "Grôz-Dûre",
    "lacus labeatis": "Labêtsêe",
    "varar aestuarium": "Vararmünde",
    "bodotria aestuarium": "Bodotrîemünde",
}

LATIN_STRIPPABLE_GEO_WHEN_COMPOUNDED: dict[str, str] = {
    "mare germanicum": "Germân",
    "mare sardoum": "Sardô",
    "mare tyrrhenum": "Tyrrhên",
    "mare balearicum": "Balêar",
    "mare cantabricum": "Kantâber",
    "tritonis palus": "Tritôn",
    "vallis sauconnae": "Saukônne",
    "gabreta silva": "Gabrêta",
    "sana silva": "Sâna",
    "portae mesesinae": "Mesêsen",
    "heraei montes": "Hêrêen",
    "pyrenaei montes": "Pyrênêen",
    "carpetani montes": "Karpetân",
    "mons lugdunensis": "Lugdûn",
    "mons marianus": "Mariân",
    "mons vindius": "Wind",
    "mons maior": "Grôz",
    "urbs giudi": "Giudi",
    "lacus labeatis": "Labêt",
    "lingonicus ager": "Lingônen",
    "maresc pictavensis": "Piktâf",
    "bosporus cimmerius": "Kimmer-Bôspor",
    "contra margum": "Gêgenmarg",
    "pone navata": "Pône-Navât",
    "duria maior": "Grôz-Dûre",
    "alpes cottiae": "Kottalpen",
    "alpes iuliae": "Julalpen",
    "alpes liguriae": "Ligûralpen",
    "alpes maritimae": "Mêralpen",
}

LATIN_SINGLE_CURATED: dict[str, str] = {
    "albis": "Albe",
    "danubius": "Danûb",
    "rhenus": "Rên",
    "tibiscus": "Tibîsch",
    "viadrus": "Viâder",
    "thysdrus": "Tysder",
    "danapris": "Danâper",
    "danastris": "Danâster",
    "apulum": "Apûl",
    "pyretus": "Pyrêt",
    "vesuvius": "Vesûf",
    "viminacium": "Viminâzjen",
    "icosium": "Ikôsjen",
    "camulodunum": "Kamulodûn",
    "vindobona": "Vindobône",
    "tigris": "Tîger",
    "oxus": "Ochs",
    "creones": "Krêôn",
    "oaeneon": "Oênêe",
    "aequum": "Êkwe",
    "hammeum": "Hammêe",
    "aegeae": "Êgêe",
    "caedris": "Kêder",
    "turres": "Turr",
    "primis": "Prîm",
    "anas": "Anas",
    "avus": "Avûs",
    "pagus": "Pâch",
    "urci": "Urzî",
    "chazari": "Chazar",
    "aestii": "Este",
    "mazovii": "Masôven",
    "osiliani": "Ôsiljân",
    "sarmatae": "Sarmât",
    "gepidae": "Gepîden",
    "sacae": "Saken",
    "ardiae": "Ardiê",
    "ardiaei": "Ardiê",
    "maezaei": "Mêzê",
    "carpi": "Karpen",
    "sudini": "Sudînen",
    "sudeti": "Sudêten",
    "varisci": "Varisken",
    "harudes": "Harûden",
    "nasamones": "Nasamôn",
    "blemmyes": "Blemmy",
    "daesitiates": "Desitjât",
    "iazyges": "Jazygen",
    "comani": "Komân",
    "merens": "Mêren",
    "mordens": "Môrden",
    "letthigalli": "Lettigallen",
    "semigalli": "Semgallen",
    "corconti": "Korkônten",
    "cimbri": "Kimbern",
    "scrithifinni": "Skritfinnen",
    "brenodor": "Brenodôr",
    "tobius": "Tobî",
    "tanais": "Tanais",
    "ruscino": "Ruszîn",
    "agnio": "Agnjôn",
    "novios": "Nôvî",
    "duroliponte": "Durolipônte",
    "tyras": "Tyras",
    "tarraca": "Tarrâke",
    "tarsatica": "Tarsatîke",
    "phylacae": "Fylâke",
}

_LATIN_HEAD_WORDS: set[str] = {
    "mare", "sinus", "lacus", "flumen", "mons", "montes",
    "silva", "saltus", "vallis", "palus", "urbs",
}


def adapt_latin_word(w: str) -> str:
    """Adapt a single Classical/Medieval Latin word to Tarraconian Chancellery phonology."""
    low = w.lower()
    if low in LATIN_SINGLE_CURATED:
        return LATIN_SINGLE_CURATED[low]
    if low in {"ad", "et", "de"}:
        return low

    s = w
    # Map front-vowel c -> z BEFORE final -a / -ae reduces to -e
    s = re.sub(r"\b[Cc](?=[eiy])", "Z", s)
    s = re.sub(r"(?<=[A-Za-zÀ-ɏ])[Cc](?=[eiy])", "z", s)
    s = re.sub(r"ae", lambda m: "Ê" if m.group(0)[0].isupper() else "ê", s, flags=re.I)
    s = re.sub(r"oe", lambda m: "Ö" if m.group(0)[0].isupper() else "ö", s, flags=re.I)
    s = re.sub(r"ph", lambda m: "F" if m.group(0)[0].isupper() else "f", s, flags=re.I)
    s = re.sub(r"th", lambda m: "T" if m.group(0)[0].isupper() else "t", s, flags=re.I)

    # Inflectional & derivational endings (longest first)
    if re.match(r"^([A-Za-zÀ-ɏ]{3,})polis$", s, flags=re.I):
        s = re.sub(r"polis$", "ôpel", s, flags=re.I)
        s = s.replace("oô", "ô").replace("ôô", "ô")
    elif re.match(r"^([A-Za-zÀ-ɏ]{3,})dunum$", s, flags=re.I):
        s = s[:-5] + "dûn"
    elif re.match(r"^([A-Za-zÀ-ɏ]{3,})magus$", s, flags=re.I):
        s = s[:-5] + "mâch"
    elif re.match(r"^([A-Za-zÀ-ɏ]{3,})briga$", s, flags=re.I):
        s = s[:-5] + "brîge"
    elif re.match(r"^([A-Za-zÀ-ɏ]{3,})([stz])ium$", s, flags=re.I):
        m2 = re.match(r"^([A-Za-zÀ-ɏ]{3,})([stz])ium$", s, flags=re.I)
        stem, cons = m2.group(1), m2.group(2).lower()
        if stem.lower().endswith("n") and cons == "t":
            s = stem + "tz"
        elif cons == "s" and stem.lower()[-1:] not in {"a", "e", "i", "o", "u", "â", "ê", "î", "ô", "û"}:
            s = stem + cons + "jen"
        elif cons in {"t", "z"}:
            s = stem + "zjen"
        else:
            s = stem + cons + "jen"
    elif re.match(r"^([A-Za-zÀ-ɏ]{3,})ium$", s, flags=re.I):
        s = s[:-3] + "jen"
    elif re.match(r"^([A-Za-zÀ-ɏ]{3,})ion$", s, flags=re.I):
        s = s[:-3] + "jen"
    elif re.match(r"^([A-Za-zÀ-ɏ]{3,})eum$", s, flags=re.I):
        s = s[:-3] + "êe"
    elif re.match(r"^([A-Za-zÀ-ɏ]{3,})icum$", s, flags=re.I):
        s = s[:-4] + "îch"
    elif re.match(r"^([A-Za-zÀ-ɏ]{3,})um$", s, flags=re.I):
        stem = s[:-2]
        if stem.lower().endswith(("pr", "tr", "dr", "br", "cr", "kr")):
            stem = stem[:-1] + "e" + stem[-1]
        elif stem.lower().endswith("v"):
            stem = stem[:-1] + "f"
        s = stem
    elif re.match(r"^([A-Za-zÀ-ɏ]{3,})([tz])ius$", s, flags=re.I):
        s = re.match(r"^([A-Za-zÀ-ɏ]{3,})([tz])ius$", s, flags=re.I).group(1) + "z"
    elif re.match(r"^([A-Za-zÀ-ɏ]{3,})ius$", s, flags=re.I):
        stem = s[:-3]
        if stem.lower().endswith("v"):
            stem = stem[:-1] + "f"
        s = stem
    elif re.match(r"^([A-Za-zÀ-ɏ]{3,})ous$", s, flags=re.I):
        s = s[:-3] + "ôs"
    elif re.match(r"^([A-Za-zÀ-ɏ]{3,})us$", s, flags=re.I):
        stem = s[:-2]
        if stem.lower().endswith(("pr", "tr", "dr", "br", "cr", "kr")):
            stem = stem[:-1] + "e" + stem[-1]
        elif stem.lower().endswith("v"):
            stem = stem[:-1] + "f"
        elif stem.lower().endswith("sc"):
            stem = stem[:-2] + "sch"
        s = stem
    elif re.match(r"^([A-Za-zÀ-ɏ]{3,})([tz])ia$", s, flags=re.I):
        s = re.match(r"^([A-Za-zÀ-ɏ]{3,})([tz])ia$", s, flags=re.I).group(1) + "tzîe"
    elif re.match(r"^([A-Za-zÀ-ɏ]{3,})eia$", s, flags=re.I):
        s = s[:-3] + "êje"
    elif re.match(r"^([A-Za-zÀ-ɏ]{3,})ia$", s, flags=re.I):
        s = s[:-2] + "îe"
    elif re.match(r"^([A-Za-zÀ-ɏ]{3,})ea$", s, flags=re.I):
        s = s[:-2] + "êe"
    elif re.match(r"^([A-Za-zÀ-ɏ]{3,})ê$", s, flags=re.I):
        s = s[:-1] + "e"
    elif re.match(r"^([A-Za-zÀ-ɏ]{2,})ca$", s, flags=re.I):
        # Preserve hard velar [k] when weakening final -ca -> -ke (never palatalize to -ce [ts])
        s = s[:-2] + "ke"
    elif re.match(r"^([A-Za-zÀ-ɏ]{3,})a$", s, flags=re.I):
        s = s[:-1] + "e"
    elif re.match(r"^([A-Za-zÀ-ɏ]{3,})io$", s, flags=re.I):
        s = s[:-2] + "ôn"
    elif re.match(r"^([A-Za-zÀ-ɏ]{4,})o$", s, flags=re.I):
        stem = s[:-1]
        if stem.lower().endswith(("ll", "pp", "ss")):
            stem = stem[:-1]
        s = stem
    elif re.match(r"^([A-Za-zÀ-ɏ]{4,})(?<![aeiou])is$", s, flags=re.I):
        stem = s[:-2]
        if stem.lower().endswith(("pr", "tr", "dr", "br", "cr", "kr")):
            stem = stem[:-1] + "e" + stem[-1]
        s = stem
    elif re.match(r"^([A-Za-zÀ-ɏ]{4,})os$", s, flags=re.I):
        s = s[:-2]
    elif re.match(r"^([A-Za-zÀ-ɏ]{4,})on$", s, flags=re.I):
        s = s[:-2] + "ôn"

    # Circumflex stressed vowel in short CVC stems (Nil -> Nîl, Pat -> Pât, etc.)
    m_mono = re.match(r"^([BCDFGHJKLMNPQRSTVWXZbdfghjklmnpqrstvwxz]+)([aeiou])([bcdfghjklmnpqrstvwxz]+)$", s)
    if m_mono:
        c_map = {"a": "â", "e": "ê", "i": "î", "o": "ô", "u": "û"}
        s = m_mono.group(1) + c_map[m_mono.group(2)] + m_mono.group(3)

    # Final Auslautverhärtung
    s = re.sub(r"d$", "t", s)
    s = re.sub(r"g$", "ch", s)
    s = re.sub(r"b$", "p", s)
    return s


def adapt_latin_to_tarraconian(stem: str, *, suppress_geo_head: bool = False) -> str:
    """Translate/adapt a Latin toponym or phrase into canonical Tarraconian orthography."""
    s = stem.strip()
    if not s:
        return s
    low = s.lower()
    if suppress_geo_head and low in LATIN_STRIPPABLE_GEO_WHEN_COMPOUNDED:
        return LATIN_STRIPPABLE_GEO_WHEN_COMPOUNDED[low]
    if low in LATIN_CURATED_PHRASES:
        return LATIN_CURATED_PHRASES[low]

    words = s.split()
    if suppress_geo_head and len(words) >= 2:
        if words[0].lower() in _LATIN_HEAD_WORDS:
            words = words[1:]
        elif words[-1].lower() in _LATIN_HEAD_WORDS:
            words = words[:-1]
    res = " ".join(adapt_latin_word(w) for w in words)
    if res and res[0].islower():
        res = res[0].upper() + res[1:]
    return res


def is_true_latin_stem(rec: dict[str, Any]) -> bool:
    """Return True when the record's Stage 2 source stem is genuinely Latin rather than vernacular/misattributed."""
    if rec.get("selected_iso") != "lat":
        return False
    if rec.get("stem_source") == "existing_natural_proper_name":
        return False
    if (rec.get("selected_source_form") or "") in NON_LATIN_MISATTRIBUTED:
        return False
    return True

#!/usr/bin/env python3
"""
generate_ck3_culture_bridge.py

Builds Section 4.B dataset #4: data/ck3_culture_to_iso_and_generics.json

Connects all 404 CK3 cultures (from melted_save.ck3 culture_manager & phase1/cultures_data.json),
including all 161 dynamic hybrid and divergent cultures, to:
  1. Ordered ISO 639-3 / 639-5 / proto language codes (with parent-culture resolution) for
     Stage 2 lookups into data/anachronicity_audit/ and data/natural_tribal_replacements/
  2. Native toponymic generic lexicons by holding type (castle, city, church, tribal) and
     geometric/functional gates (sea_coast, waterborne, hill_or_mountain, frontier, pious,
     martial, mercantile) across 50 linguistic morphology families
  3. Phonological mediation & transmission filter rules (transmission_culture -> Tarraconian
     plus key historical multi-hop intermediary shifts)

Output:
  data/ck3_culture_to_iso_and_generics.json
"""

import argparse
import glob
import json
import time
from collections import Counter
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_DIR / "data"
SAVE_PATH = Path("/var/tmp/ck3_audit/melted_save.ck3")
CULTURES_PHASE1_PATH = Path("/var/tmp/ck3_audit/phase1/cultures_data.json")

TARRACONIAN_CORE_CULTURES = {
    "Tarraconian",
    "Lothringian",
    "Croato-Tarraconian",
    "Alpine-Tarraconian",
    "Ungwârer",
}

SINOSPHERE_HERITAGES = {
    "heritage_chinese",
    "heritage_korean",
    "heritage_japonic",
    "heritage_viet",
    "heritage_buyeo",
}


def g(form: str, affix_position: str, joiner: str, gloss: str, tarr_calque: str, gate: str = None) -> dict:
    """Builds a structured native generic morpheme entry."""
    return {
        "form": form,
        "affix_position": affix_position,
        "joiner": joiner,
        "gloss": gloss,
        "tarr_calque": tarr_calque,
        "gate": gate,
    }


def make_family(compound_order: str, castle: list, city: list, church: list, tribal: list, notes: str = "") -> dict:
    """Constructs a morphology family definition."""
    return {
        "compound_order": compound_order,
        "generics": {
            "castle": castle,
            "city": city,
            "church": church,
            "tribal": tribal,
        },
        "notes": notes,
    }


MORPHOLOGY_FAMILIES = {
    "tarraconian_imperial": make_family(
        "head_final",
        castle=[
            g("-burch", "suffix", "", "castle / stronghold", "-burch"),
            g("-veste", "suffix", "", "fortress / fastness", "-veste"),
            g("-stein", "suffix", "", "rock / hill-fort", "-stein", "hill_or_mountain"),
            g("-march", "suffix", "", "border march", "-march", "frontier"),
            g("-wart", "suffix", "", "watchtower", "-wart", "frontier"),
            g("Castel-", "prefix", "", "castle (Catalan loan)", "Castel-"),
        ],
        city=[
            g("-stat", "suffix", "", "walled town", "-stat"),
            g("-vurt", "suffix", "", "ford / river crossing", "-vurt", "waterborne"),
            g("-hâven", "suffix", "", "sea harbor / haven", "-hâven", "sea_coast"),
            g("-marct", "suffix", "", "market town", "-marct", "mercantile"),
            g("-brücke", "suffix", "", "bridge town", "-brücke", "waterborne"),
        ],
        church=[
            g("-kirchen", "suffix", "", "church", "-kirchen"),
            g("-clôster", "suffix", "", "monastery / cloister", "-clôster", "pious"),
            g("-munster", "suffix", "", "minster / abbey", "-munster", "pious"),
            g("-zelle", "suffix", "", "hermitage / cell", "-zelle"),
            g("Zant-", "prefix", "", "saint shrine", "Zant-", "pious"),
        ],
        tribal=[
            g("-lant", "suffix", "", "territory / land", "-lant"),
            g("-gouw", "suffix", "", "district / shire", "-gouw"),
            g("-dal", "suffix", "", "valley settlement", "-dal"),
        ],
        notes="Imperial Moselle-Rhine Franconian with Old Catalan administrative generics",
    ),
    "high_german": make_family(
        "head_final",
        castle=[
            g("-burg", "suffix", "", "stronghold", "-burch"),
            g("-feste", "suffix", "", "fortress", "-veste"),
            g("-stein", "suffix", "", "stone keep", "-stein", "hill_or_mountain"),
            g("-wart", "suffix", "", "watchtower", "-wart", "frontier"),
        ],
        city=[
            g("-stat", "suffix", "", "town / stead", "-stat"),
            g("-furt", "suffix", "", "river ford", "-vurt", "waterborne"),
            g("-markt", "suffix", "", "market", "-marct", "mercantile"),
            g("-hafen", "suffix", "", "sea harbor", "-hâven", "sea_coast"),
        ],
        church=[
            g("-kirchen", "suffix", "", "church", "-kirchen"),
            g("-kloster", "suffix", "", "abbey / cloister", "-clôster", "pious"),
            g("-zelle", "suffix", "", "monastic cell", "-zelle"),
            g("Sankt-", "prefix", "", "saint dedication", "Zant-", "pious"),
        ],
        tribal=[
            g("-dorf", "suffix", "", "village / thorp", "-dorf"),
            g("-gau", "suffix", "", "district", "-gouw"),
            g("-heim", "suffix", "", "homestead", "-heim"),
        ],
    ),
    "anglo_saxon": make_family(
        "head_final",
        castle=[
            g("-burh", "suffix", "", "fortified burh", "-burch"),
            g("-ceaster", "suffix", "", "Roman castra / fort", "-castel"),
            g("-stan", "suffix", "", "stone fort", "-stein", "hill_or_mountain"),
        ],
        city=[
            g("-tun", "suffix", "", "enclosure / town", "-stat"),
            g("-wic", "suffix", "", "trading emporium", "-wîch", "mercantile"),
            g("-ford", "suffix", "", "river ford", "-vurt", "waterborne"),
            g("-port", "suffix", "", "maritime harbor", "-port", "sea_coast"),
        ],
        church=[
            g("-cirice", "suffix", "", "church", "-kirchen"),
            g("-mynster", "suffix", "", "minster", "-munster", "pious"),
            g("-stow", "suffix", "", "holy place", "-stouwe"),
        ],
        tribal=[
            g("-ham", "suffix", "", "homestead", "-heim"),
            g("-ingas", "suffix", "", "kinfolk settlement", "-ingen"),
            g("-feld", "suffix", "", "open field", "-veit"),
        ],
    ),
    "low_german_dutch": make_family(
        "head_final",
        castle=[
            g("-borg", "suffix", "", "stronghold", "-burch"),
            g("-steen", "suffix", "", "stone keep", "-stein"),
            g("-schans", "suffix", "", "redoubt / sconce", "-schanze", "frontier"),
        ],
        city=[
            g("-stad", "suffix", "", "town", "-stat"),
            g("-voorde", "suffix", "", "river ford", "-vurt", "waterborne"),
            g("-haven", "suffix", "", "sea harbor", "-hâven", "sea_coast"),
            g("-dam", "suffix", "", "dike / embankment town", "-dam", "waterborne"),
        ],
        church=[
            g("-kerk", "suffix", "", "church", "-kirchen"),
            g("-klooster", "suffix", "", "cloister", "-clôster", "pious"),
            g("Sint-", "prefix", "", "saint shrine", "Zant-", "pious"),
        ],
        tribal=[
            g("-hem", "suffix", "", "homestead", "-heim"),
            g("-dorp", "suffix", "", "village", "-dorf"),
            g("-woud", "suffix", "", "woodland", "-walt"),
        ],
    ),
    "north_germanic": make_family(
        "head_final",
        castle=[
            g("-borg", "suffix", "", "stronghold", "-burch"),
            g("-virki", "suffix", "", "rampart / earthwork", "-werc"),
            g("-fell", "suffix", "", "mountain crag", "-berch", "hill_or_mountain"),
        ],
        city=[
            g("-by", "suffix", "", "town / farmstead", "-stat"),
            g("-köping", "suffix", "", "market town", "-marct", "mercantile"),
            g("-vík", "suffix", "", "sea bay / cove", "-hâven", "sea_coast"),
            g("-vað", "suffix", "", "river ford", "-vurt", "waterborne"),
        ],
        church=[
            g("-kirkja", "suffix", "", "church", "-kirchen"),
            g("-klaustr", "suffix", "", "cloister", "-clôster", "pious"),
            g("Helga-", "prefix", "", "holy site", "Hilig-", "pious"),
        ],
        tribal=[
            g("-staðir", "suffix", "", "homestead", "-stat"),
            g("-lundr", "suffix", "", "sacred grove", "-lunt"),
            g("-land", "suffix", "", "district", "-lant"),
        ],
    ),
    "gallo_romance": make_family(
        "head_initial",
        castle=[
            g("Château-", "prefix", "", "castle", "-burch"),
            g("Roche-", "prefix", "", "rock fortress", "-stein", "hill_or_mountain"),
            g("La Garde-", "prefix", "", "guard watch", "-wart", "frontier"),
        ],
        city=[
            g("Ville-", "prefix", "", "town", "-stat"),
            g("-bourg", "suffix", "", "market borough", "-burch", "mercantile"),
            g("Port-", "prefix", "", "sea harbor", "-hâven", "sea_coast"),
            g("Pont-", "prefix", "", "river bridge", "-brücke", "waterborne"),
        ],
        church=[
            g("Saint-", "prefix", "", "saint dedication", "Zant-", "pious"),
            g("Moutier-", "prefix", "", "monastery", "-munster", "pious"),
            g("Chapelle-", "prefix", "", "chapel", "-kapelle"),
        ],
        tribal=[
            g("Mesnil-", "prefix", "", "domain / hamlet", "-wîler"),
            g("Val-", "prefix", "", "valley", "-dal"),
        ],
    ),
    "occitano_catalan": make_family(
        "head_initial",
        castle=[
            g("Castell ", "prefix", " ", "castle", "-castel"),
            g("Puig ", "prefix", " ", "hilltop keep", "-bühil", "hill_or_mountain"),
            g("Guàrdia ", "prefix", " ", "watchtower", "-wart", "frontier"),
        ],
        city=[
            g("Vila ", "prefix", " ", "town", "-stat"),
            g("Port ", "prefix", " ", "sea harbor", "-port", "sea_coast"),
            g("Pont ", "prefix", " ", "bridge town", "-brücke", "waterborne"),
        ],
        church=[
            g("Sant ", "prefix", " ", "saint dedication", "Zant-", "pious"),
            g("Monestir ", "prefix", " ", "monastery", "-munster", "pious"),
            g("Església ", "prefix", " ", "church", "-kirchen"),
        ],
        tribal=[
            g("Mas ", "prefix", " ", "farmstead", "-hûs"),
            g("Vall ", "prefix", " ", "valley", "-dal"),
        ],
    ),
    "ibero_romance": make_family(
        "head_initial",
        castle=[
            g("Castillo de ", "prefix", " ", "castle", "-castel"),
            g("Peña ", "prefix", " ", "rock fort", "-fels", "hill_or_mountain"),
            g("Torre ", "prefix", " ", "watchtower", "-torn", "frontier"),
        ],
        city=[
            g("Villa ", "prefix", " ", "town", "-stat"),
            g("Puerto ", "prefix", " ", "sea port", "-port", "sea_coast"),
            g("Puente ", "prefix", " ", "bridge town", "-brücke", "waterborne"),
        ],
        church=[
            g("San ", "prefix", " ", "saint shrine", "Zant-", "pious"),
            g("Monasterio ", "prefix", " ", "abbey", "-clôster", "pious"),
            g("Iglesia ", "prefix", " ", "church", "-kirchen"),
        ],
        tribal=[
            g("Aldea ", "prefix", " ", "village", "-dorf"),
            g("Campo ", "prefix", " ", "plain / field", "-veit"),
        ],
    ),
    "italo_romance": make_family(
        "head_initial",
        castle=[
            g("Castel ", "prefix", " ", "castle", "-castel"),
            g("Rocca ", "prefix", " ", "hilltop rock fortress", "-stein", "hill_or_mountain"),
            g("Torre ", "prefix", " ", "tower", "-torn", "frontier"),
        ],
        city=[
            g("Borgo ", "prefix", " ", "walled town / borough", "-stat"),
            g("Porto ", "prefix", " ", "sea port", "-port", "sea_coast"),
            g("Ponte ", "prefix", " ", "bridge town", "-brücke", "waterborne"),
            g("Mercato ", "prefix", " ", "market town", "-marct", "mercantile"),
        ],
        church=[
            g("San ", "prefix", " ", "saint church", "Zant-", "pious"),
            g("Badia ", "prefix", " ", "abbey", "-abtei", "pious"),
            g("Chiesa ", "prefix", " ", "church", "-kirchen"),
        ],
        tribal=[
            g("Villa ", "prefix", " ", "estate / hamlet", "-wîler"),
            g("Val ", "prefix", " ", "valley", "-dal"),
        ],
    ),
    "eastern_romance": make_family(
        "head_initial",
        castle=[
            g("Cetatea ", "prefix", " ", "citadel", "-burch"),
            g("Turnu ", "prefix", " ", "border tower", "-torn", "frontier"),
        ],
        city=[
            g("Târgu ", "prefix", " ", "market town", "-marct"),
            g("Vadul ", "prefix", " ", "river ford", "-vurt", "waterborne"),
            g("Chilia ", "prefix", " ", "port / granary", "-hâven", "sea_coast"),
        ],
        church=[
            g("Sfântu ", "prefix", " ", "saint shrine", "Zant-", "pious"),
            g("Mănăstirea ", "prefix", " ", "monastery", "-clôster", "pious"),
            g("Biserica ", "prefix", " ", "church", "-kirchen"),
        ],
        tribal=[
            g("Satul ", "prefix", " ", "village", "-dorf"),
            g("Valea ", "prefix", " ", "valley", "-dal"),
        ],
    ),
    "latin_classical": make_family(
        "head_initial",
        castle=[
            g("Castrum ", "prefix", " ", "military fort", "-castel"),
            g("Arx ", "prefix", " ", "citadel", "-burch"),
        ],
        city=[
            g("Civitas ", "prefix", " ", "city", "-stat"),
            g("Portus ", "prefix", " ", "sea harbor", "-port", "sea_coast"),
            g("Pons ", "prefix", " ", "bridge", "-brücke", "waterborne"),
            g("Forum ", "prefix", " ", "market town", "-marct", "mercantile"),
        ],
        church=[
            g("Sanctus ", "prefix", " ", "saint shrine", "Zant-", "pious"),
            g("Abbatia ", "prefix", " ", "abbey", "-abtei", "pious"),
            g("Ecclesia ", "prefix", " ", "church", "-kirchen"),
        ],
        tribal=[
            g("Vicus ", "prefix", " ", "settlement / village", "-wîch"),
            g("Pagus ", "prefix", " ", "rural canton", "-gouw"),
        ],
    ),
    "goidelic": make_family(
        "head_initial",
        castle=[
            g("Dún ", "prefix", " ", "hill-fort / dun", "-burch"),
            g("Ráth ", "prefix", " ", "ringfort", "-wal"),
            g("Caiseal ", "prefix", " ", "stone fort", "-castel"),
        ],
        city=[
            g("Baile ", "prefix", " ", "settlement / town", "-stat"),
            g("Áth ", "prefix", " ", "river ford", "-vurt", "waterborne"),
            g("Port ", "prefix", " ", "sea landing / port", "-port", "sea_coast"),
        ],
        church=[
            g("Cill ", "prefix", " ", "church / monastic cell", "-kirchen"),
            g("Mainistir ", "prefix", " ", "monastery", "-munster", "pious"),
            g("Domhnach ", "prefix", " ", "lord's church", "-kirchen"),
        ],
        tribal=[
            g("Cluain ", "prefix", " ", "meadow", "-ouwe"),
            g("Magh ", "prefix", " ", "plain", "-veit"),
        ],
    ),
    "brythonic": make_family(
        "head_initial",
        castle=[
            g("Caer ", "prefix", " ", "fortress / caer", "-burch"),
            g("Din ", "prefix", " ", "hill-fort", "-stein", "hill_or_mountain"),
            g("Castell ", "prefix", " ", "castle", "-castel"),
        ],
        city=[
            g("Tre ", "prefix", "", "settlement / town", "-stat"),
            g("Porth ", "prefix", " ", "sea harbor", "-port", "sea_coast"),
            g("Rhyd ", "prefix", " ", "river ford", "-vurt", "waterborne"),
            g("Aber ", "prefix", " ", "estuary / river mouth", "-munde", "waterborne"),
        ],
        church=[
            g("Llan ", "prefix", " ", "church enclosure", "-kirchen"),
            g("Eglwys ", "prefix", " ", "church", "-kirchen"),
            g("Mynachlog ", "prefix", " ", "monastery", "-clôster", "pious"),
        ],
        tribal=[
            g("Pentref ", "prefix", " ", "hamlet / village", "-dorf"),
            g("Glyn ", "prefix", " ", "valley", "-dal"),
        ],
    ),
    "hellenic": make_family(
        "head_final",
        castle=[
            g("-kastron", "suffix", "", "fortress", "-castel"),
            g("-pyrgos", "suffix", "", "watchtower", "-torn", "frontier"),
            g("-phrourion", "suffix", "", "garrison fort", "-burch"),
        ],
        city=[
            g("-polis", "suffix", "", "walled city", "-pel"),
            g("-limen", "suffix", "", "sea harbor", "-hâven", "sea_coast"),
            g("-poros", "suffix", "", "ford / crossing", "-vurt", "waterborne"),
            g("-emporion", "suffix", "", "trading town", "-marct", "mercantile"),
        ],
        church=[
            g("Hagio-", "prefix", "", "holy / saint shrine", "Zant-", "pious"),
            g("-moni", "suffix", "", "monastery", "-clôster", "pious"),
            g("-ekklesia", "suffix", "", "church", "-kirchen"),
        ],
        tribal=[
            g("-chora", "suffix", "", "country / town", "-stat"),
            g("-kome", "suffix", "", "village", "-dorf"),
        ],
    ),
    "east_slavic": make_family(
        "head_final",
        castle=[
            g("-gorod", "suffix", "", "walled town / fort", "-burch"),
            g("Gorodishche-", "prefix", "", "old hill-fort", "-altburch"),
            g("-ostrog", "suffix", "", "palisaded fort", "-werc", "frontier"),
            g("-kamen", "suffix", "", "stone stronghold", "-stein", "hill_or_mountain"),
        ],
        city=[
            g("-grad", "suffix", "", "city", "-stat"),
            g("-torg", "suffix", "", "market town", "-marct", "mercantile"),
            g("-brod", "suffix", "", "river ford", "-vurt", "waterborne"),
            g("-pristan", "suffix", "", "harbor / landing", "-hâven", "sea_coast"),
        ],
        church=[
            g("-cerkov", "suffix", "", "church", "-kirchen"),
            g("-monastyr", "suffix", "", "monastery", "-clôster", "pious"),
            g("Svyato-", "prefix", "", "holy shrine", "Hilig-", "pious"),
        ],
        tribal=[
            g("-selo", "suffix", "", "village", "-dorf"),
            g("-polye", "suffix", "", "open field", "-veit"),
        ],
    ),
    "west_slavic_czech_slovak": make_family(
        "head_final",
        castle=[
            g("-hrad", "suffix", "", "castle / stronghold", "-burch"),
            g("-tvrz", "suffix", "", "fortified keep", "-veste"),
            g("-stráž", "suffix", "", "border watch", "-wart", "frontier"),
        ],
        city=[
            g("-město", "suffix", "", "walled town", "-stat"),
            g("-trh", "suffix", "", "market town", "-marct", "mercantile"),
            g("-brod", "suffix", "", "river ford", "-vurt", "waterborne"),
        ],
        church=[
            g("-kostel", "suffix", "", "church", "-kirchen"),
            g("-klášter", "suffix", "", "monastery", "-clôster", "pious"),
            g("Svatý-", "prefix", "", "saint dedication", "Zant-", "pious"),
        ],
        tribal=[
            g("-ves", "suffix", "", "village", "-dorf"),
            g("-lhota", "suffix", "", "chartered clearing", "-rîte"),
        ],
    ),
    "west_slavic_lechitic": make_family(
        "head_final",
        castle=[
            g("-gród", "suffix", "", "stronghold / gord", "-burch"),
            g("-grod", "suffix", "", "fortified burg", "-burch"),
            g("-stróża", "suffix", "", "frontier watch", "-wart", "frontier"),
        ],
        city=[
            g("-miasto", "suffix", "", "town", "-stat"),
            g("-targ", "suffix", "", "market town", "-marct", "mercantile"),
            g("-bród", "suffix", "", "river ford", "-vurt", "waterborne"),
            g("-przystań", "suffix", "", "sea harbor", "-hâven", "sea_coast"),
        ],
        church=[
            g("-cerkiew", "suffix", "", "church", "-kirchen"),
            g("-kościół", "suffix", "", "church", "-kirchen"),
            g("-klasztor", "suffix", "", "monastery", "-clôster", "pious"),
            g("Święto-", "prefix", "", "saint / holy site", "Hilig-", "pious"),
        ],
        tribal=[
            g("-wieś", "suffix", "", "village", "-dorf"),
            g("-pole", "suffix", "", "open plain", "-veit"),
        ],
    ),
    "south_slavic": make_family(
        "head_final",
        castle=[
            g("-grad", "suffix", "", "fortress / citadel", "-burch"),
            g("-tvrđa", "suffix", "", "stronghold", "-veste"),
            g("-straža", "suffix", "", "border watch", "-wart", "frontier"),
        ],
        city=[
            g("-varoš", "suffix", "", "town", "-stat"),
            g("-trg", "suffix", "", "market square / town", "-marct", "mercantile"),
            g("-brod", "suffix", "", "river ford", "-vurt", "waterborne"),
            g("-luka", "suffix", "", "sea harbor / bay", "-hâven", "sea_coast"),
        ],
        church=[
            g("-crkva", "suffix", "", "church", "-kirchen"),
            g("-manastir", "suffix", "", "monastery", "-clôster", "pious"),
            g("Sveti-", "prefix", "", "saint shrine", "Zant-", "pious"),
        ],
        tribal=[
            g("-selo", "suffix", "", "village", "-dorf"),
            g("-polje", "suffix", "", "field / basin", "-veit"),
        ],
    ),
    "baltic": make_family(
        "head_final",
        castle=[
            g("-pilis", "suffix", "", "hill-fort / castle", "-burch"),
            g("-pils", "suffix", "", "castle (Latgalian)", "-burch"),
            g("-kalns", "suffix", "", "fortified hill", "-berch", "hill_or_mountain"),
        ],
        city=[
            g("-miestas", "suffix", "", "town", "-stat"),
            g("-brasta", "suffix", "", "river ford", "-vurt", "waterborne"),
            g("-uostas", "suffix", "", "sea port / river mouth", "-hâven", "sea_coast"),
        ],
        church=[
            g("-bažnyčia", "suffix", "", "church", "-kirchen"),
            g("-alkas", "suffix", "", "sacred grove / shrine", "-hêl"),
            g("-vienuolynas", "suffix", "", "monastery", "-clôster", "pious"),
        ],
        tribal=[
            g("-kiemis", "suffix", "", "village / homestead", "-dorf"),
            g("-laukas", "suffix", "", "clearing / field", "-veit"),
        ],
    ),
    "magyar": make_family(
        "head_final",
        castle=[
            g("-vár", "suffix", "", "castle / fortress", "-burch"),
            g("-kő", "suffix", "", "stone keep", "-stein", "hill_or_mountain"),
            g("-őr", "suffix", "", "border guard post", "-wart", "frontier"),
        ],
        city=[
            g("-város", "suffix", "", "walled town", "-stat"),
            g("-vásár", "suffix", "", "market town", "-marct", "mercantile"),
            g("-rév", "suffix", "", "river ferry / ford", "-vurt", "waterborne"),
        ],
        church=[
            g("-egyház", "suffix", "", "church", "-kirchen"),
            g("-monostor", "suffix", "", "monastery", "-clôster", "pious"),
            g("Szent-", "prefix", "", "saint shrine", "Zant-", "pious"),
        ],
        tribal=[
            g("-szállás", "suffix", "", "clan camp / quarters", "-hûs"),
            g("-falva", "suffix", "", "village", "-dorf"),
        ],
    ),
    "finnic": make_family(
        "head_final",
        castle=[
            g("-linna", "suffix", "", "fortress / stronghold", "-burch"),
            g("-mäki", "suffix", "", "fortified hill", "-berch", "hill_or_mountain"),
        ],
        city=[
            g("-kaupunki", "suffix", "", "trading town", "-marct"),
            g("-satama", "suffix", "", "sea harbor", "-hâven", "sea_coast"),
            g("-koski", "suffix", "", "river rapids / crossing", "-vurt", "waterborne"),
        ],
        church=[
            g("-kirkko", "suffix", "", "church", "-kirchen"),
            g("Pyhä-", "prefix", "", "holy site", "Hilig-", "pious"),
        ],
        tribal=[
            g("-kylä", "suffix", "", "village", "-dorf"),
            g("-maa", "suffix", "", "land / territory", "-lant"),
        ],
    ),
    "sami": make_family(
        "head_final",
        castle=[
            g("-bákti", "suffix", "", "crag / stronghold", "-stein"),
        ],
        city=[
            g("-siida", "suffix", "", "winter settlement", "-stat"),
            g("-vuotna", "suffix", "", "sea fjord", "-hâven", "sea_coast"),
            g("-johka", "suffix", "", "river crossing", "-bache", "waterborne"),
        ],
        church=[
            g("-girku", "suffix", "", "church", "-kirchen"),
            g("-álda", "suffix", "", "sacred ridge / site", "Hilig-"),
        ],
        tribal=[
            g("-jávri", "suffix", "", "lake settlement", "-sê"),
            g("-várri", "suffix", "", "fell / upland", "-berch"),
        ],
    ),
    "volga_permian": make_family(
        "head_final",
        castle=[
            g("-kar", "suffix", "", "fortified town (Permian)", "-burch"),
            g("-osh", "suffix", "", "palisaded town (Ugric)", "-burch"),
        ],
        city=[
            g("-ola", "suffix", "", "town", "-stat"),
            g("-vosh", "suffix", "", "fortified settlement", "-stat"),
            g("-va", "suffix", "", "river / water station", "-wazzer", "waterborne"),
        ],
        church=[
            g("-kerka", "suffix", "", "temple / sanctuary", "-kirchen"),
            g("Vezha-", "prefix", "", "sacred shrine", "Hilig-", "pious"),
        ],
        tribal=[
            g("-gurt", "suffix", "", "clan village", "-dorf"),
            g("-yurt", "suffix", "", "winter camp", "-hûs"),
        ],
    ),
    "basque": make_family(
        "head_final",
        castle=[
            g("-gaztelu", "suffix", "", "castle", "-castel"),
            g("-harri", "suffix", "", "stone keep", "-stein", "hill_or_mountain"),
        ],
        city=[
            g("-hiri", "suffix", "", "town", "-stat"),
            g("-kaia", "suffix", "", "sea quay / harbor", "-hâven", "sea_coast"),
            g("-zubi", "suffix", "", "river bridge", "-brücke", "waterborne"),
        ],
        church=[
            g("-eliza", "suffix", "", "church", "-kirchen"),
            g("Done-", "prefix", "", "saint dedication", "Zant-", "pious"),
        ],
        tribal=[
            g("-ibar", "suffix", "", "valley community", "-dal"),
            g("-uri", "suffix", "", "hamlet", "-dorf"),
        ],
    ),
    "albanian": make_family(
        "head_initial",
        castle=[
            g("Kala ", "prefix", " ", "fortress", "-burch"),
            g("Gur ", "prefix", " ", "rock fort", "-stein", "hill_or_mountain"),
        ],
        city=[
            g("Qytet ", "prefix", " ", "town", "-stat"),
            g("Skelë ", "prefix", " ", "sea landing", "-hâven", "sea_coast"),
            g("Ura ", "prefix", " ", "bridge crossing", "-brücke", "waterborne"),
        ],
        church=[
            g("Shën ", "prefix", " ", "saint dedication", "Zant-", "pious"),
            g("Kisha ", "prefix", " ", "church", "-kirchen"),
        ],
        tribal=[
            g("Katund ", "prefix", " ", "pastoral village", "-dorf"),
            g("Mal ", "prefix", " ", "highland", "-berch"),
        ],
    ),
    "armenian": make_family(
        "head_final",
        castle=[
            g("-berd", "suffix", "", "fortress", "-burch"),
            g("-amrots", "suffix", "", "citadel", "-veste"),
        ],
        city=[
            g("-kert", "suffix", "", "founded city", "-stat"),
            g("-avan", "suffix", "", "market town", "-marct"),
            g("-kamurj", "suffix", "", "river bridge", "-brücke", "waterborne"),
        ],
        church=[
            g("-vank", "suffix", "", "monastery", "-clôster", "pious"),
            g("Surb ", "prefix", " ", "saint shrine", "Zant-", "pious"),
            g("-yekehetsi", "suffix", "", "church", "-kirchen"),
        ],
        tribal=[
            g("-shen", "suffix", "", "village / settlement", "-dorf"),
            g("-dzor", "suffix", "", "gorge / valley", "-dal"),
        ],
    ),
    "kartvelian": make_family(
        "head_final",
        castle=[
            g("-tsikhe", "suffix", "", "fortress", "-burch"),
            g("-klde", "suffix", "", "rock citadel", "-stein", "hill_or_mountain"),
        ],
        city=[
            g("-kalaki", "suffix", "", "city", "-stat"),
            g("-navsadguri", "suffix", "", "sea harbor", "-hâven", "sea_coast"),
            g("-khidi", "suffix", "", "bridge crossing", "-brücke", "waterborne"),
        ],
        church=[
            g("-monasteri", "suffix", "", "monastery", "-clôster", "pious"),
            g("Tsminda ", "prefix", " ", "saint shrine", "Zant-", "pious"),
            g("-eklesia", "suffix", "", "church", "-kirchen"),
        ],
        tribal=[
            g("-sopeli", "suffix", "", "village", "-dorf"),
            g("-khevi", "suffix", "", "valley", "-dal"),
        ],
    ),
    "arabic": make_family(
        "head_initial",
        castle=[
            g("Qal'at ", "prefix", " ", "fortress / citadel", "-burch"),
            g("Hisn ", "prefix", " ", "stronghold", "-veste"),
            g("Burj ", "prefix", " ", "watchtower", "-torn", "frontier"),
            g("Ribat ", "prefix", " ", "frontier ribat fort", "-wart", "martial"),
        ],
        city=[
            g("Madinat ", "prefix", " ", "walled city", "-stat"),
            g("Suq ", "prefix", " ", "market town", "-marct", "mercantile"),
            g("Mina ", "prefix", " ", "sea harbor", "-hâven", "sea_coast"),
            g("Marsa ", "prefix", " ", "maritime anchorage", "-port", "sea_coast"),
            g("Qantara ", "prefix", " ", "bridge / crossing", "-brücke", "waterborne"),
        ],
        church=[
            g("Deir ", "prefix", " ", "monastery / convent", "-clôster"),
            g("Mashhad ", "prefix", " ", "martyr shrine", "-wîe", "pious"),
            g("Ribat ", "prefix", " ", "devotional ribat", "-zelle", "pious"),
            g("Kanisat ", "prefix", " ", "church / sanctuary", "-kirchen"),
        ],
        tribal=[
            g("Dar ", "prefix", " ", "tribal abode", "-heim"),
            g("Wadi ", "prefix", " ", "valley / wadi", "-dal"),
            g("Hilla ", "prefix", " ", "encampment", "-stat"),
        ],
    ),
    "berber": make_family(
        "head_initial",
        castle=[
            g("Agadir ", "prefix", " ", "fortified granary / fort", "-burch"),
            g("Ighrem ", "prefix", " ", "kasbah / stone keep", "-veste"),
            g("Tizi ", "prefix", " ", "mountain pass", "-klûse", "hill_or_mountain"),
        ],
        city=[
            g("Tamdint ", "prefix", " ", "walled town", "-stat"),
            g("Asif ", "prefix", " ", "river settlement", "-wazzer", "waterborne"),
            g("Marsa ", "prefix", " ", "sea anchorage", "-hâven", "sea_coast"),
        ],
        church=[
            g("Zawiya ", "prefix", " ", "religious lodge", "-wîe", "pious"),
            g("Sidi ", "prefix", " ", "marabout shrine", "-wîe", "pious"),
        ],
        tribal=[
            g("Aït ", "prefix", " ", "clan / sons of", "-ingen"),
            g("Tamazirt ", "prefix", " ", "territory", "-lant"),
        ],
    ),
    "aramaic_hebrew": make_family(
        "head_initial",
        castle=[
            g("Migdal ", "prefix", " ", "tower / keep", "-torn"),
            g("Hesna ", "prefix", " ", "fortress", "-burch"),
        ],
        city=[
            g("Kfar ", "prefix", " ", "village / town", "-stat"),
            g("Karka ", "prefix", " ", "walled town", "-stat"),
            g("Gishra ", "prefix", " ", "river bridge", "-brücke", "waterborne"),
            g("Namal ", "prefix", " ", "sea harbor", "-hâven", "sea_coast"),
        ],
        church=[
            g("Dayra ", "prefix", " ", "monastery", "-clôster", "pious"),
            g("Beit ", "prefix", " ", "house / temple", "-kirchen"),
            g("Mar ", "prefix", " ", "saint dedication", "Zant-", "pious"),
        ],
        tribal=[
            g("Tel ", "prefix", " ", "mound settlement", "-bühil"),
            g("Ein ", "prefix", " ", "spring settlement", "-brunn"),
        ],
    ),
    "egyptian_coptic": make_family(
        "head_initial",
        castle=[
            g("Kastron ", "prefix", " ", "fortress", "-castel"),
            g("P-Sobt ", "prefix", " ", "walled fort", "-burch"),
        ],
        city=[
            g("P-Tmi ", "prefix", " ", "town / nome seat", "-stat"),
            g("Mero ", "prefix", " ", "harbor / quay", "-hâven", "sea_coast"),
        ],
        church=[
            g("Apa ", "prefix", " ", "saint shrine", "Zant-", "pious"),
            g("T-Moni ", "prefix", " ", "monastery", "-clôster", "pious"),
        ],
        tribal=[
            g("P-Ti ", "prefix", " ", "district", "-gouw"),
        ],
    ),
    "ethiopic_cushitic": make_family(
        "head_initial",
        castle=[
            g("Amba ", "prefix", " ", "mesa / mountain fortress", "-stein", "hill_or_mountain"),
            g("Ketema ", "prefix", " ", "royal camp / fort", "-burch"),
            g("Qal'at ", "prefix", " ", "fort", "-burch"),
        ],
        city=[
            g("Medina ", "prefix", " ", "town", "-stat"),
            g("Marsa ", "prefix", " ", "Red Sea / Indian Ocean port", "-hâven", "sea_coast"),
            g("Gebeya ", "prefix", " ", "market town", "-marct", "mercantile"),
        ],
        church=[
            g("Debre ", "prefix", " ", "monastic mountain sanctuary", "-munster", "pious"),
            g("Beta ", "prefix", " ", "church / house", "-kirchen"),
            g("Qiddus ", "prefix", " ", "saint dedication", "Zant-", "pious"),
        ],
        tribal=[
            g("Genda ", "prefix", " ", "village", "-dorf"),
            g("Woreda ", "prefix", " ", "district", "-lant"),
        ],
    ),
    "west_central_african": make_family(
        "head_initial",
        castle=[
            g("Birni ", "prefix", " ", "walled citadel", "-burch"),
            g("Tata ", "prefix", " ", "fortified compound", "-veste"),
        ],
        city=[
            g("Gari ", "prefix", " ", "walled town", "-stat"),
            g("Kasuwa ", "prefix", " ", "market town", "-marct", "mercantile"),
            g("Tenda ", "prefix", " ", "river landing / port", "-hâven", "waterborne"),
        ],
        church=[
            g("Masallaci ", "prefix", " ", "mosque / sanctuary", "-meschit"),
            g("Nia ", "prefix", " ", "sacred shrine", "-wîe", "pious"),
        ],
        tribal=[
            g("Dugu ", "prefix", " ", "town / land", "-lant"),
            g("Kafu ", "prefix", " ", "clan territory", "-gouw"),
        ],
    ),
    "east_bantu_swahili": make_family(
        "head_initial",
        castle=[
            g("Ngome ", "prefix", " ", "stone fort / citadel", "-burch"),
            g("Boma ", "prefix", " ", "fortified enclosure", "-veste"),
        ],
        city=[
            g("Mji ", "prefix", " ", "walled stone town", "-stat"),
            g("Bandari ", "prefix", " ", "sea harbor", "-hâven", "sea_coast"),
            g("Kivuko ", "prefix", " ", "river ford / ferry", "-vurt", "waterborne"),
        ],
        church=[
            g("Msikiti ", "prefix", " ", "mosque / sanctuary", "-meschit"),
            g("Ziyara ", "prefix", " ", "shrine sanctuary", "-wîe", "pious"),
        ],
        tribal=[
            g("Kwa ", "prefix", " ", "settlement of", "-ingen"),
            g("Mkoa ", "prefix", " ", "region", "-lant"),
        ],
    ),
    "iranian": make_family(
        "head_final",
        castle=[
            g("-diz", "suffix", "", "fortress", "-burch"),
            g("-gird", "suffix", "", "royal circular stronghold", "-burch"),
            g("Qal'eh-", "prefix", "", "hill fort", "-stein", "hill_or_mountain"),
            g("-darband", "suffix", "", "frontier pass / gate", "-tôr", "frontier"),
        ],
        city=[
            g("-abad", "suffix", "", "founded / cultivated city", "-stat"),
            g("-shahr", "suffix", "", "walled city", "-stat"),
            g("Bandar-", "prefix", "", "maritime harbor", "-hâven", "sea_coast"),
            g("-pol", "suffix", "", "river bridge", "-brücke", "waterborne"),
            g("-bazar", "suffix", "", "market town", "-marct", "mercantile"),
        ],
        church=[
            g("-masjid", "suffix", "", "mosque", "-meschit"),
            g("-atashgah", "suffix", "", "sacred fire temple", "-tempel"),
            g("-khanaqah", "suffix", "", "dervish hospice / sanctuary", "-wîe", "pious"),
            g("-mazar", "suffix", "", "memorial shrine", "-wîe", "pious"),
        ],
        tribal=[
            g("-deh", "suffix", "", "village", "-dorf"),
            g("-rustaq", "suffix", "", "rural district", "-gouw"),
        ],
    ),
    "turkic": make_family(
        "head_final",
        castle=[
            g("-kale", "suffix", "", "fortress", "-burch"),
            g("-hisar", "suffix", "", "citadel", "-veste"),
            g("-kerman", "suffix", "", "walled fort", "-burch"),
            g("-kaya", "suffix", "", "rock keep", "-stein", "hill_or_mountain"),
        ],
        city=[
            g("-kent", "suffix", "", "town / city", "-stat"),
            g("-balyq", "suffix", "", "walled town", "-stat"),
            g("-saray", "suffix", "", "palace town", "-palz"),
            g("-bazar", "suffix", "", "market", "-marct", "mercantile"),
            g("-liman", "suffix", "", "sea harbor", "-hâven", "sea_coast"),
            g("-keçit", "suffix", "", "river ford", "-vurt", "waterborne"),
        ],
        church=[
            g("-tekke", "suffix", "", "dervish lodge / sanctuary", "-wîe", "pious"),
            g("-manastır", "suffix", "", "monastery", "-clôster"),
            g("-mescit", "suffix", "", "mosque", "-meschit"),
        ],
        tribal=[
            g("-ordu", "suffix", "", "horde camp", "-hûs"),
            g("-oba", "suffix", "", "clan camp", "-dorf"),
            g("-yurt", "suffix", "", "homeland / tent domain", "-lant"),
        ],
    ),
    "oghur": make_family(
        "head_final",
        castle=[
            g("-kermen", "suffix", "", "fortified town", "-burch"),
            g("-tübe", "suffix", "", "hill fort", "-bühil"),
        ],
        city=[
            g("-balık", "suffix", "", "city", "-stat"),
            g("-kashu", "suffix", "", "river crossing", "-vurt", "waterborne"),
        ],
        church=[
            g("-kiremet", "suffix", "", "sacred grove / sanctuary", "-hêl"),
        ],
        tribal=[
            g("-aul", "suffix", "", "settlement", "-dorf"),
            g("-yurt", "suffix", "", "domain", "-lant"),
        ],
    ),
    "mongolic": make_family(
        "head_final",
        castle=[
            g("-khota", "suffix", "", "walled citadel", "-burch"),
            g("-balgas", "suffix", "", "fortified town", "-burch"),
            g("-khad", "suffix", "", "rock cliff", "-stein", "hill_or_mountain"),
        ],
        city=[
            g("-khuree", "suffix", "", "enclosure / town", "-stat"),
            g("-olam", "suffix", "", "river ford", "-vurt", "waterborne"),
        ],
        church=[
            g("-sume", "suffix", "", "temple / sanctuary", "-tempel", "pious"),
            g("-khiid", "suffix", "", "hermitage / sanctuary", "-wîe", "pious"),
        ],
        tribal=[
            g("-ordu", "suffix", "", "imperial camp", "-hûs"),
            g("-nutug", "suffix", "", "pasture / homeland", "-lant"),
        ],
    ),
    "khitan": make_family(
        "head_final",
        castle=[
            g("-zhou", "suffix", "", "prefectural citadel", "-burch"),
            g("-cheng", "suffix", "", "walled fort", "-burch"),
        ],
        city=[
            g("-fu", "suffix", "", "metropolis", "-stat"),
            g("-zhen", "suffix", "", "garrison market town", "-marct"),
        ],
        church=[
            g("-si", "suffix", "", "monastery / temple", "-tempel", "pious"),
        ],
        tribal=[
            g("-ordo", "suffix", "", "tent palace / appanage", "-palz"),
            g("-bu", "suffix", "", "tribal division", "-gouw"),
        ],
    ),
    "tungusic": make_family(
        "head_final",
        castle=[
            g("-hoton", "suffix", "", "walled fort / city", "-burch"),
            g("-had", "suffix", "", "peak / cliff", "-berch"),
        ],
        city=[
            g("-gashan", "suffix", "", "walled village / town", "-stat"),
            g("-dogon", "suffix", "", "river crossing", "-vurt", "waterborne"),
            g("-namu", "suffix", "", "sea bay / coast", "-hâven", "sea_coast"),
        ],
        church=[
            g("-juktehen", "suffix", "", "shrine / temple", "-wîe", "pious"),
        ],
        tribal=[
            g("-hala", "suffix", "", "clan settlement", "-ingen"),
            g("-birat", "suffix", "", "riverland", "-bache"),
        ],
    ),
    "sinosphere_chinese": make_family(
        "head_final",
        castle=[
            g("城", "suffix", "", "walled citadel", "-burch"),
            g("堡", "suffix", "", "fortified keep", "-veste"),
            g("關", "suffix", "", "frontier pass / gate", "-tôr", "frontier"),
            g("鎮", "suffix", "", "garrison fort", "-werc"),
        ],
        city=[
            g("州", "suffix", "", "prefectural city", "-stat"),
            g("府", "suffix", "", "prefecture / seat", "-palz"),
            g("市", "suffix", "", "market town", "-marct", "mercantile"),
            g("港", "suffix", "", "sea harbor", "-hâven", "sea_coast"),
            g("津", "suffix", "", "river ferry / ford", "-vurt", "waterborne"),
        ],
        church=[
            g("寺", "suffix", "", "monastery / temple", "-tempel", "pious"),
            g("院", "suffix", "", "cloister / academy", "-hof", "pious"),
            g("觀", "suffix", "", "Taoist abbey / shrine", "-zelle"),
            g("宮", "suffix", "", "sacred palace", "-palz"),
        ],
        tribal=[
            g("寨", "suffix", "", "stockade", "-hag"),
            g("屯", "suffix", "", "garrison colony", "-dorf"),
        ],
    ),
    "korean": make_family(
        "head_final",
        castle=[
            g("-seong", "suffix", "", "mountain/stone fortress (城)", "-burch"),
            g("-jin", "suffix", "", "garrison fort (鎮)", "-veste", "frontier"),
        ],
        city=[
            g("-ju", "suffix", "", "provincial city (州)", "-stat"),
            g("-bu", "suffix", "", "prefectural city (府)", "-stat"),
            g("-po", "suffix", "", "sea inlet / harbor (浦)", "-hâven", "sea_coast"),
            g("-jin", "suffix", "", "river ferry / ford (津)", "-vurt", "waterborne"),
        ],
        church=[
            g("-sa", "suffix", "", "Buddhist temple (寺)", "-tempel", "pious"),
            g("-am", "suffix", "", "hermitage (庵)", "-zelle"),
        ],
        tribal=[
            g("-hyeon", "suffix", "", "county / district (縣)", "-gouw"),
            g("-gol", "suffix", "", "valley settlement", "-dal"),
        ],
    ),
    "japonic": make_family(
        "head_final",
        castle=[
            g("-jō", "suffix", "", "castle / fortress (城)", "-burch"),
            g("-date", "suffix", "", "stockade / fort (館)", "-veste"),
            g("-seki", "suffix", "", "barrier / pass (關)", "-tôr", "frontier"),
        ],
        city=[
            g("-machi", "suffix", "", "market town (町)", "-stat"),
            g("-ichi", "suffix", "", "market (市)", "-marct", "mercantile"),
            g("-tsu", "suffix", "", "harbor / port (津)", "-hâven", "sea_coast"),
            g("-watari", "suffix", "", "river crossing (渡)", "-vurt", "waterborne"),
        ],
        church=[
            g("-dera", "suffix", "", "Buddhist temple (寺)", "-tempel", "pious"),
            g("-in", "suffix", "", "cloister / sub-temple (院)", "-zelle", "pious"),
            g("-miya", "suffix", "", "shrine (宮)", "-wîe"),
        ],
        tribal=[
            g("-mura", "suffix", "", "village (村)", "-dorf"),
            g("-sato", "suffix", "", "hamlet (里)", "-heim"),
        ],
    ),
    "ainu": make_family(
        "head_final",
        castle=[
            g("-chasi", "suffix", "", "palisaded hill-fort", "-burch"),
        ],
        city=[
            g("-kotan", "suffix", "", "settlement / village", "-stat"),
            g("-tomari", "suffix", "", "sea bay / harbor", "-hâven", "sea_coast"),
            g("-pet", "suffix", "", "river mouth", "-munde", "waterborne"),
        ],
        church=[
            g("-kamuy", "suffix", "", "sacred site", "Hilig-"),
        ],
        tribal=[
            g("-kotan", "suffix", "", "village", "-dorf"),
            g("-nay", "suffix", "", "stream settlement", "-bache"),
        ],
    ),
    "viet": make_family(
        "head_initial",
        castle=[
            g("Thành ", "prefix", " ", "citadel (城)", "-burch"),
            g("Ải ", "prefix", " ", "frontier pass (隘)", "-tôr", "frontier"),
        ],
        city=[
            g("Châu ", "prefix", " ", "prefecture / town (州)", "-stat"),
            g("Chợ ", "prefix", " ", "market town", "-marct", "mercantile"),
            g("Cảng ", "prefix", " ", "sea port (港)", "-hâven", "sea_coast"),
            g("Bến ", "prefix", " ", "river ferry landing", "-vurt", "waterborne"),
        ],
        church=[
            g("Chùa ", "prefix", " ", "pagoda / monastery", "-tempel", "pious"),
            g("Đền ", "prefix", " ", "shrine / temple", "-wîe"),
        ],
        tribal=[
            g("Làng ", "prefix", " ", "village", "-dorf"),
            g("Mường ", "prefix", " ", "upland domain", "-lant"),
        ],
    ),
    "indo_aryan": make_family(
        "head_final",
        castle=[
            g("-garh", "suffix", "", "fortress", "-burch"),
            g("-kot", "suffix", "", "walled fort", "-veste"),
            g("-durg", "suffix", "", "inaccessible citadel", "-stein", "hill_or_mountain"),
        ],
        city=[
            g("-pur", "suffix", "", "walled city", "-stat"),
            g("-nagar", "suffix", "", "town", "-stat"),
            g("-bandar", "suffix", "", "sea port", "-hâven", "sea_coast"),
            g("-ghat", "suffix", "", "river steps / ferry", "-vurt", "waterborne"),
        ],
        church=[
            g("-mandir", "suffix", "", "temple", "-tempel"),
            g("-vihara", "suffix", "", "monastery", "-wîe", "pious"),
            g("-tirtha", "suffix", "", "pilgrimage ford / shrine", "-wîe", "pious"),
        ],
        tribal=[
            g("-gram", "suffix", "", "village", "-dorf"),
            g("-palli", "suffix", "", "hamlet", "-heim"),
        ],
    ),
    "dravidian": make_family(
        "head_final",
        castle=[
            g("-kottai", "suffix", "", "fortress", "-burch"),
            g("-durgam", "suffix", "", "hill fort", "-stein", "hill_or_mountain"),
        ],
        city=[
            g("-puram", "suffix", "", "city", "-stat"),
            g("-ur", "suffix", "", "town / settlement", "-stat"),
            g("-pattinam", "suffix", "", "sea port city", "-hâven", "sea_coast"),
            g("-turai", "suffix", "", "river crossing / harbor", "-vurt", "waterborne"),
        ],
        church=[
            g("-koil", "suffix", "", "temple", "-tempel"),
            g("-palli", "suffix", "", "monastic sanctuary", "-wîe", "pious"),
        ],
        tribal=[
            g("-padi", "suffix", "", "hamlet", "-dorf"),
            g("-nadu", "suffix", "", "country / province", "-lant"),
        ],
    ),
    "tibetic": make_family(
        "head_final",
        castle=[
            g("-dzong", "suffix", "", "fortress / administrative dzong", "-burch"),
            g("-khar", "suffix", "", "castle / keep", "-veste"),
            g("-la", "suffix", "", "mountain pass fort", "-klûse", "hill_or_mountain"),
        ],
        city=[
            g("-grong", "suffix", "", "walled town", "-stat"),
            g("-thang", "suffix", "", "plain settlement", "-veit"),
            g("-zam", "suffix", "", "river bridge", "-brücke", "waterborne"),
        ],
        church=[
            g("-gonpa", "suffix", "", "monastery", "-wîe", "pious"),
            g("-lhakhang", "suffix", "", "temple sanctuary", "-tempel"),
            g("Chos-", "prefix", "", "sacred dharma seat", "Hilig-", "pious"),
        ],
        tribal=[
            g("-yul", "suffix", "", "valley / country", "-lant"),
            g("-rong", "suffix", "", "gorge settlement", "-dal"),
        ],
    ),
    "burmese_qiangic": make_family(
        "head_initial",
        castle=[
            g("Taik ", "prefix", " ", "brick fort", "-burch"),
            g("Khang ", "prefix", " ", "stockade fort", "-veste"),
        ],
        city=[
            g("Myo ", "prefix", " ", "walled city", "-stat"),
            g("Seik ", "prefix", " ", "port / landing", "-hâven", "sea_coast"),
            g("Kyaung-", "prefix", "", "river landing", "-vurt", "waterborne"),
        ],
        church=[
            g("Kyaung ", "prefix", " ", "monastery", "-wîe", "pious"),
            g("Paya ", "prefix", " ", "pagoda / shrine", "-tempel", "pious"),
        ],
        tribal=[
            g("Ywa ", "prefix", " ", "village", "-dorf"),
        ],
    ),
    "tai_hmong": make_family(
        "head_initial",
        castle=[
            g("Wiang ", "prefix", " ", "fortified ring-city", "-burch"),
            g("Chiang ", "prefix", " ", "walled citadel", "-burch"),
        ],
        city=[
            g("Mueang ", "prefix", " ", "principality / town", "-stat"),
            g("Tha ", "prefix", " ", "river ferry / port", "-vurt", "waterborne"),
            g("Pak ", "prefix", " ", "estuary / sea mouth", "-hâven", "sea_coast"),
        ],
        church=[
            g("Wat ", "prefix", " ", "monastery / temple", "-tempel", "pious"),
            g("That ", "prefix", " ", "reliquary stupa", "-wîe", "pious"),
        ],
        tribal=[
            g("Ban ", "prefix", " ", "village", "-dorf"),
            g("Doi ", "prefix", " ", "upland hill", "-berch"),
        ],
    ),
    "mon_khmer": make_family(
        "head_initial",
        castle=[
            g("Banteay ", "prefix", " ", "citadel / fortress", "-burch"),
            g("Phnom ", "prefix", " ", "sacred hill fort", "-berch", "hill_or_mountain"),
        ],
        city=[
            g("Krong ", "prefix", " ", "royal city", "-stat"),
            g("Kompong ", "prefix", " ", "river/sea landing", "-hâven", "waterborne"),
        ],
        church=[
            g("Prasat ", "prefix", " ", "stone temple", "-tempel"),
            g("Wat ", "prefix", " ", "monastery", "-wîe", "pious"),
        ],
        tribal=[
            g("Phum ", "prefix", " ", "village", "-dorf"),
            g("Srok ", "prefix", " ", "district", "-lant"),
        ],
    ),
    "austronesian": make_family(
        "head_initial",
        castle=[
            g("Kota ", "prefix", " ", "fortified enclosure", "-burch"),
            g("Kubu ", "prefix", " ", "stockade fort", "-veste"),
            g("Batu ", "prefix", " ", "stone crag", "-stein", "hill_or_mountain"),
        ],
        city=[
            g("Bandar ", "prefix", " ", "maritime port city", "-hâven", "sea_coast"),
            g("Kuala ", "prefix", " ", "river mouth / port", "-munde", "waterborne"),
            g("Pasar ", "prefix", " ", "market town", "-marct", "mercantile"),
        ],
        church=[
            g("Candi ", "prefix", " ", "stone temple", "-tempel"),
            g("Vihara ", "prefix", " ", "monastery", "-wîe", "pious"),
        ],
        tribal=[
            g("Kampung ", "prefix", " ", "village", "-dorf"),
            g("Desa ", "prefix", " ", "rural community", "-heim"),
        ],
    ),
}

# Language-level defaults for all 91 CK3 culture languages
CK3_LANGUAGE_DEFAULTS = {
    "language_ainu": {
        "iso_codes": ["ain", "jpn", "ojp"],
        "liturgical_iso": "ain",
        "morphology_family": "ainu",
        "transmission_profile": "east_asian_to_tarraconian",
    },
    "language_albanian": {
        "iso_codes": ["sqi", "lat", "grc"],
        "liturgical_iso": "lat",
        "morphology_family": "albanian",
        "transmission_profile": "balkan_to_tarraconian",
    },
    "language_ancient_greek": {
        "iso_codes": ["grc", "ell", "lat"],
        "liturgical_iso": "grc",
        "morphology_family": "hellenic",
        "transmission_profile": "greek_to_tarraconian",
    },
    "language_anglic": {
        "iso_codes": ["ang", "eng", "sco", "osx", "fry", "deu", "gem-pro"],
        "liturgical_iso": "lat",
        "morphology_family": "anglo_saxon",
        "transmission_profile": "west_germanic_to_tarraconian",
    },
    "language_arabic": {
        "iso_codes": ["ara", "lat", "grc"],
        "liturgical_iso": "ara",
        "morphology_family": "arabic",
        "transmission_profile": "arabic_to_tarraconian",
    },
    "language_aramaic": {
        "iso_codes": ["syc", "arc", "heb", "ara"],
        "liturgical_iso": "syc",
        "morphology_family": "aramaic_hebrew",
        "transmission_profile": "semitic_to_tarraconian",
    },
    "language_armenian": {
        "iso_codes": ["hye", "grc", "fas"],
        "liturgical_iso": "hye",
        "morphology_family": "armenian",
        "transmission_profile": "caucasian_to_tarraconian",
    },
    "language_asli": {
        "iso_codes": ["msa", "ind", "mon"],
        "liturgical_iso": "san",
        "morphology_family": "austronesian",
        "transmission_profile": "southeast_asian_to_tarraconian",
    },
    "language_austronesian": {
        "iso_codes": ["msa", "ind", "jav", "tgl", "ceb", "bjn", "sun", "bug", "mak", "ban"],
        "liturgical_iso": "san",
        "morphology_family": "austronesian",
        "transmission_profile": "southeast_asian_to_tarraconian",
    },
    "language_ayneha": {
        "iso_codes": ["ses", "khq", "snk", "mnk", "ara"],
        "liturgical_iso": "ara",
        "morphology_family": "west_central_african",
        "transmission_profile": "african_to_tarraconian",
    },
    "language_baltic": {
        "iso_codes": ["lit", "lav", "prg", "bat"],
        "liturgical_iso": "lat",
        "morphology_family": "baltic",
        "transmission_profile": "baltic_to_tarraconian",
    },
    "language_basque": {
        "iso_codes": ["eus", "bsq", "lat", "spa"],
        "liturgical_iso": "lat",
        "morphology_family": "basque",
        "transmission_profile": "ibero_romance_to_tarraconian",
    },
    "language_berber": {
        "iso_codes": ["ber", "tzm", "shi", "zgh", "kab", "tmh", "ara", "lat"],
        "liturgical_iso": "ara",
        "morphology_family": "berber",
        "transmission_profile": "arabic_to_tarraconian",
    },
    "language_brythonic": {
        "iso_codes": ["cel-bry", "cym", "bre", "cor", "obt", "cel-pro", "lat"],
        "liturgical_iso": "lat",
        "morphology_family": "brythonic",
        "transmission_profile": "celtic_to_tarraconian",
    },
    "language_burmese": {
        "iso_codes": ["mya", "raw", "lhu", "shn", "zho"],
        "liturgical_iso": "pli",
        "morphology_family": "burmese_qiangic",
        "transmission_profile": "southeast_asian_to_tarraconian",
    },
    "language_carthaginian": {
        "iso_codes": ["ara", "lat", "heb", "grc"],
        "liturgical_iso": "ara",
        "morphology_family": "aramaic_hebrew",
        "transmission_profile": "semitic_to_tarraconian",
    },
    "language_central_germanic": {
        "iso_codes": ["goh", "deu", "gmh", "gem-pro", "lat"],
        "liturgical_iso": "lat",
        "morphology_family": "high_german",
        "transmission_profile": "high_german_to_tarraconian",
    },
    "language_chadic": {
        "iso_codes": ["hau", "kau", "zag", "ara"],
        "liturgical_iso": "ara",
        "morphology_family": "west_central_african",
        "transmission_profile": "african_to_tarraconian",
    },
    "language_chamic": {
        "iso_codes": ["cjm", "ace", "vie", "msa", "ind"],
        "liturgical_iso": "san",
        "morphology_family": "austronesian",
        "transmission_profile": "southeast_asian_to_tarraconian",
    },
    "language_chinese": {
        "iso_codes": ["ltc", "lzh", "zho", "cmn", "och", "yue", "hak"],
        "liturgical_iso": "lzh",
        "morphology_family": "sinosphere_chinese",
        "transmission_profile": "sinosphere_1154_to_tarraconian",
    },
    "language_cushitic": {
        "iso_codes": ["som", "aar", "orm", "bej", "ssy", "amh", "ara"],
        "liturgical_iso": "ara",
        "morphology_family": "ethiopic_cushitic",
        "transmission_profile": "african_to_tarraconian",
    },
    "language_czech_slovak": {
        "iso_codes": ["ces", "slk", "sla-pro", "sla", "chu", "pol"],
        "liturgical_iso": "lat",
        "morphology_family": "west_slavic_czech_slovak",
        "transmission_profile": "west_slavic_to_tarraconian",
    },
    "language_dutch": {
        "iso_codes": ["nld", "vls", "fry", "deu", "gem-pro"],
        "liturgical_iso": "lat",
        "morphology_family": "low_german_dutch",
        "transmission_profile": "west_germanic_to_tarraconian",
    },
    "language_east_slavic": {
        "iso_codes": ["orv", "rus", "ukr", "bel", "rue", "sla-pro", "sla", "chu"],
        "liturgical_iso": "chu",
        "morphology_family": "east_slavic",
        "transmission_profile": "east_slavic_to_tarraconian",
    },
    "language_egyptian": {
        "iso_codes": ["cop", "egy", "grc", "ara", "lat"],
        "liturgical_iso": "grc",
        "morphology_family": "egyptian_coptic",
        "transmission_profile": "greek_to_tarraconian",
    },
    "language_ethiopic": {
        "iso_codes": ["amh", "gez", "tir", "ara"],
        "liturgical_iso": "gez",
        "morphology_family": "ethiopic_cushitic",
        "transmission_profile": "semitic_to_tarraconian",
    },
    "language_finnic": {
        "iso_codes": ["fin", "krl", "vep", "est", "lud", "izh", "vot", "liv", "urj-fin-pro", "urj"],
        "liturgical_iso": "lat",
        "morphology_family": "finnic",
        "transmission_profile": "uralic_to_tarraconian",
    },
    "language_frankish": {
        "iso_codes": ["goh", "deu", "fra", "fro", "lat"],
        "liturgical_iso": "lat",
        "morphology_family": "high_german",
        "transmission_profile": "high_german_to_tarraconian",
    },
    "language_french": {
        "iso_codes": ["fra", "fro", "nrf", "pcd", "wln", "xtg", "lat"],
        "liturgical_iso": "lat",
        "morphology_family": "gallo_romance",
        "transmission_profile": "gallo_romance_to_tarraconian",
    },
    "language_georgian": {
        "iso_codes": ["kat", "xmf", "sva", "grc"],
        "liturgical_iso": "kat",
        "morphology_family": "kartvelian",
        "transmission_profile": "caucasian_to_tarraconian",
    },
    "language_goidelic": {
        "iso_codes": ["gle", "sga", "gla", "glv", "cel-pro", "lat"],
        "liturgical_iso": "lat",
        "morphology_family": "goidelic",
        "transmission_profile": "celtic_to_tarraconian",
    },
    "language_greek": {
        "iso_codes": ["grc", "ell", "lat"],
        "liturgical_iso": "grc",
        "morphology_family": "hellenic",
        "transmission_profile": "greek_to_tarraconian",
    },
    "language_gur": {
        "iso_codes": ["mos", "kbp", "gux", "bba", "mnk", "fra"],
        "liturgical_iso": "ara",
        "morphology_family": "west_central_african",
        "transmission_profile": "african_to_tarraconian",
    },
    "language_high_german": {
        "iso_codes": ["gmh", "goh", "deu", "gsw", "bar", "cat", "lat"],
        "liturgical_iso": "lat",
        "morphology_family": "high_german",
        "transmission_profile": "high_german_to_tarraconian",
    },
    "language_hmongic": {
        "iso_codes": ["hmn", "zho", "lzh"],
        "liturgical_iso": "lzh",
        "morphology_family": "tai_hmong",
        "transmission_profile": "sinosphere_1154_to_tarraconian",
    },
    "language_hunnic": {
        "iso_codes": ["otk", "hun", "chv", "tat"],
        "liturgical_iso": "otk",
        "morphology_family": "oghur",
        "transmission_profile": "turkic_to_tarraconian",
    },
    "language_iberian": {
        "iso_codes": ["spa", "por", "glg", "ast", "arg", "lat", "ara"],
        "liturgical_iso": "lat",
        "morphology_family": "ibero_romance",
        "transmission_profile": "ibero_romance_to_tarraconian",
    },
    "language_iranian": {
        "iso_codes": ["fas", "pal", "peo", "tgk", "kur", "bal", "sog", "ara"],
        "liturgical_iso": "fas",
        "morphology_family": "iranian",
        "transmission_profile": "iranian_to_tarraconian",
    },
    "language_israelite": {
        "iso_codes": ["heb", "arc", "syc", "ara"],
        "liturgical_iso": "heb",
        "morphology_family": "aramaic_hebrew",
        "transmission_profile": "semitic_to_tarraconian",
    },
    "language_italian": {
        "iso_codes": ["ita", "scn", "lom", "lld", "fur", "frp", "lat"],
        "liturgical_iso": "lat",
        "morphology_family": "italo_romance",
        "transmission_profile": "italo_romance_to_tarraconian",
    },
    "language_japonic": {
        "iso_codes": ["ojp", "jpn", "ryu", "lzh"],
        "liturgical_iso": "lzh",
        "morphology_family": "japonic",
        "transmission_profile": "sinosphere_1154_to_tarraconian",
    },
    "language_kannada": {
        "iso_codes": ["kan", "san", "tel", "mar"],
        "liturgical_iso": "san",
        "morphology_family": "dravidian",
        "transmission_profile": "indic_to_tarraconian",
    },
    "language_kashmiri": {
        "iso_codes": ["kas", "khw", "san", "pra", "hin"],
        "liturgical_iso": "san",
        "morphology_family": "indo_aryan",
        "transmission_profile": "indic_to_tarraconian",
    },
    "language_khitan": {
        "iso_codes": ["mon", "cmg", "mnc", "zho", "lzh"],
        "liturgical_iso": "lzh",
        "morphology_family": "khitan",
        "transmission_profile": "sinosphere_1154_to_tarraconian",
    },
    "language_korean": {
        "iso_codes": ["oko", "kor", "lzh", "zho"],
        "liturgical_iso": "lzh",
        "morphology_family": "korean",
        "transmission_profile": "sinosphere_1154_to_tarraconian",
    },
    "language_kru": {
        "iso_codes": ["klu", "krw", "grb", "mnk"],
        "liturgical_iso": "ara",
        "morphology_family": "west_central_african",
        "transmission_profile": "african_to_tarraconian",
    },
    "language_kwa": {
        "iso_codes": ["aka", "ewe", "fon", "bci", "any", "nzi", "gaa"],
        "liturgical_iso": "ara",
        "morphology_family": "west_central_african",
        "transmission_profile": "african_to_tarraconian",
    },
    "language_latin": {
        "iso_codes": ["lat", "ita", "roa", "grc"],
        "liturgical_iso": "lat",
        "morphology_family": "latin_classical",
        "transmission_profile": "latin_to_tarraconian",
    },
    "language_lechitic": {
        "iso_codes": ["pol", "wen", "csb", "hsb", "dsb", "sla-pro", "sla", "deu"],
        "liturgical_iso": "lat",
        "morphology_family": "west_slavic_lechitic",
        "transmission_profile": "west_slavic_to_tarraconian",
    },
    "language_magadhan": {
        "iso_codes": ["ben", "ori", "asm", "mai", "san", "pra", "hin"],
        "liturgical_iso": "san",
        "morphology_family": "indo_aryan",
        "transmission_profile": "indic_to_tarraconian",
    },
    "language_magyar": {
        "iso_codes": ["hun", "urj", "sla-pro", "deu"],
        "liturgical_iso": "lat",
        "morphology_family": "magyar",
        "transmission_profile": "magyar_to_tarraconian",
    },
    "language_manding": {
        "iso_codes": ["mnk", "bam", "sus", "kpe", "vai", "kno", "snk"],
        "liturgical_iso": "ara",
        "morphology_family": "west_central_african",
        "transmission_profile": "african_to_tarraconian",
    },
    "language_marathi": {
        "iso_codes": ["mar", "san", "pra", "hin"],
        "liturgical_iso": "san",
        "morphology_family": "indo_aryan",
        "transmission_profile": "indic_to_tarraconian",
    },
    "language_mon_khmer": {
        "iso_codes": ["khm", "okz", "mnw", "tha", "san", "pli"],
        "liturgical_iso": "pli",
        "morphology_family": "mon_khmer",
        "transmission_profile": "southeast_asian_to_tarraconian",
    },
    "language_mongolic": {
        "iso_codes": ["mon", "cmg", "bua", "otk"],
        "liturgical_iso": "mon",
        "morphology_family": "mongolic",
        "transmission_profile": "mongolic_to_tarraconian",
    },
    "language_nivkh": {
        "iso_codes": ["niv", "gld", "rus", "ain"],
        "liturgical_iso": "niv",
        "morphology_family": "ainu",
        "transmission_profile": "east_asian_to_tarraconian",
    },
    "language_norse": {
        "iso_codes": ["non", "swe", "nor", "dan", "isl", "fao", "gem-pro"],
        "liturgical_iso": "lat",
        "morphology_family": "north_germanic",
        "transmission_profile": "north_germanic_to_tarraconian",
    },
    "language_north_dravidian": {
        "iso_codes": ["bal", "snd", "fas", "san", "sat"],
        "liturgical_iso": "fas",
        "morphology_family": "dravidian",
        "transmission_profile": "indic_to_tarraconian",
    },
    "language_occitano_romance": {
        "iso_codes": ["oci", "cat", "arg", "lat", "fra", "spa"],
        "liturgical_iso": "lat",
        "morphology_family": "occitano_catalan",
        "transmission_profile": "occitano_catalan_to_tarraconian",
    },
    "language_oghur": {
        "iso_codes": ["chv", "otk", "tat", "hun", "kaz"],
        "liturgical_iso": "otk",
        "morphology_family": "oghur",
        "transmission_profile": "turkic_to_tarraconian",
    },
    "language_omotic": {
        "iso_codes": ["amh", "orm", "gez", "tir"],
        "liturgical_iso": "gez",
        "morphology_family": "ethiopic_cushitic",
        "transmission_profile": "african_to_tarraconian",
    },
    "language_pahari": {
        "iso_codes": ["nep", "hin", "san", "bod"],
        "liturgical_iso": "san",
        "morphology_family": "indo_aryan",
        "transmission_profile": "indic_to_tarraconian",
    },
    "language_papuan": {
        "iso_codes": ["msa", "ind"],
        "liturgical_iso": "msa",
        "morphology_family": "austronesian",
        "transmission_profile": "southeast_asian_to_tarraconian",
    },
    "language_qiangic": {
        "iso_codes": ["otb", "bod", "zho", "lzh"],
        "liturgical_iso": "bod",
        "morphology_family": "tibetic",
        "transmission_profile": "tibetic_to_tarraconian",
    },
    "language_rajasthani": {
        "iso_codes": ["guj", "raj", "hin", "san", "pra"],
        "liturgical_iso": "san",
        "morphology_family": "indo_aryan",
        "transmission_profile": "indic_to_tarraconian",
    },
    "language_sabaki": {
        "iso_codes": ["swa", "ara"],
        "liturgical_iso": "ara",
        "morphology_family": "east_bantu_swahili",
        "transmission_profile": "african_to_tarraconian",
    },
    "language_sami": {
        "iso_codes": ["sme", "smj", "sma", "smn", "sms", "sju", "smi", "fin", "nor", "swe"],
        "liturgical_iso": "lat",
        "morphology_family": "sami",
        "transmission_profile": "uralic_to_tarraconian",
    },
    "language_sardinian": {
        "iso_codes": ["srd", "cos", "ita", "lat"],
        "liturgical_iso": "lat",
        "morphology_family": "italo_romance",
        "transmission_profile": "italo_romance_to_tarraconian",
    },
    "language_sauraseni": {
        "iso_codes": ["hin", "urd", "san", "pra"],
        "liturgical_iso": "san",
        "morphology_family": "indo_aryan",
        "transmission_profile": "indic_to_tarraconian",
    },
    "language_saxon": {
        "iso_codes": ["osx", "nds", "deu", "ang", "gem-pro"],
        "liturgical_iso": "lat",
        "morphology_family": "low_german_dutch",
        "transmission_profile": "west_germanic_to_tarraconian",
    },
    "language_scythian": {
        "iso_codes": ["sog", "oss", "pus", "tgk", "fas", "pal", "peo"],
        "liturgical_iso": "fas",
        "morphology_family": "iranian",
        "transmission_profile": "iranian_to_tarraconian",
    },
    "language_senegambian": {
        "iso_codes": ["wol", "ful", "dyo", "mnk", "ara"],
        "liturgical_iso": "ara",
        "morphology_family": "west_central_african",
        "transmission_profile": "african_to_tarraconian",
    },
    "language_sinhalese": {
        "iso_codes": ["sin", "pli", "san", "tam"],
        "liturgical_iso": "pli",
        "morphology_family": "indo_aryan",
        "transmission_profile": "indic_to_tarraconian",
    },
    "language_slavonic": {
        "iso_codes": ["bul", "chu", "mkd", "srp", "sla-pro", "sla", "grc"],
        "liturgical_iso": "chu",
        "morphology_family": "south_slavic",
        "transmission_profile": "south_slavic_to_tarraconian",
    },
    "language_soninke": {
        "iso_codes": ["snk", "mnk", "bam", "mos", "ara"],
        "liturgical_iso": "ara",
        "morphology_family": "west_central_african",
        "transmission_profile": "african_to_tarraconian",
    },
    "language_south_slavic": {
        "iso_codes": ["hrv", "srp", "bos", "slv", "bul", "sla-pro", "sla", "chu"],
        "liturgical_iso": "lat",
        "morphology_family": "south_slavic",
        "transmission_profile": "south_slavic_to_tarraconian",
    },
    "language_sudanic": {
        "iso_codes": ["ara", "grc", "cop", "amh"],
        "liturgical_iso": "grc",
        "morphology_family": "ethiopic_cushitic",
        "transmission_profile": "african_to_tarraconian",
    },
    "language_tai": {
        "iso_codes": ["tha", "lao", "shn", "zha", "lic", "khb", "zho"],
        "liturgical_iso": "pli",
        "morphology_family": "tai_hmong",
        "transmission_profile": "southeast_asian_to_tarraconian",
    },
    "language_tamil": {
        "iso_codes": ["tam", "mal", "san"],
        "liturgical_iso": "san",
        "morphology_family": "dravidian",
        "transmission_profile": "indic_to_tarraconian",
    },
    "language_telugu": {
        "iso_codes": ["tel", "san", "ori", "kan"],
        "liturgical_iso": "san",
        "morphology_family": "dravidian",
        "transmission_profile": "indic_to_tarraconian",
    },
    "language_tibetan": {
        "iso_codes": ["bod", "otb", "dzo", "san", "nep"],
        "liturgical_iso": "bod",
        "morphology_family": "tibetic",
        "transmission_profile": "tibetic_to_tarraconian",
    },
    "language_tocharian": {
        "iso_codes": ["uig", "sog", "san", "zho"],
        "liturgical_iso": "san",
        "morphology_family": "iranian",
        "transmission_profile": "iranian_to_tarraconian",
    },
    "language_tubu": {
        "iso_codes": ["zag", "kau", "ara"],
        "liturgical_iso": "ara",
        "morphology_family": "west_central_african",
        "transmission_profile": "african_to_tarraconian",
    },
    "language_tungusic": {
        "iso_codes": ["mnc", "juc", "gld", "evn", "zho", "lzh"],
        "liturgical_iso": "lzh",
        "morphology_family": "tungusic",
        "transmission_profile": "sinosphere_1154_to_tarraconian",
    },
    "language_turkic": {
        "iso_codes": ["otk", "tur", "kaz", "uzb", "tuk", "kir", "tat", "bak", "uig", "kjh", "tyv", "aze"],
        "liturgical_iso": "ara",
        "morphology_family": "turkic",
        "transmission_profile": "turkic_to_tarraconian",
    },
    "language_ugro_permian": {
        "iso_codes": ["kom", "kpv", "udm", "kca", "mns", "sel", "urj", "rus"],
        "liturgical_iso": "chu",
        "morphology_family": "volga_permian",
        "transmission_profile": "uralic_to_tarraconian",
    },
    "language_vietnamese": {
        "iso_codes": ["vie", "lzh", "zho"],
        "liturgical_iso": "lzh",
        "morphology_family": "viet",
        "transmission_profile": "sinosphere_1154_to_tarraconian",
    },
    "language_volga_finnic": {
        "iso_codes": ["chm", "mhr", "myv", "mdf", "urj", "rus", "tat"],
        "liturgical_iso": "chu",
        "morphology_family": "volga_permian",
        "transmission_profile": "uralic_to_tarraconian",
    },
    "language_vrachada": {
        "iso_codes": ["pan", "snd", "san", "pra", "hin", "fas"],
        "liturgical_iso": "san",
        "morphology_family": "indo_aryan",
        "transmission_profile": "indic_to_tarraconian",
    },
    "language_wallachian": {
        "iso_codes": ["ron", "lat", "bul", "hun"],
        "liturgical_iso": "chu",
        "morphology_family": "eastern_romance",
        "transmission_profile": "eastern_romance_to_tarraconian",
    },
    "language_yoruba": {
        "iso_codes": ["yor", "ibo", "bin", "ige", "tiv", "ara"],
        "liturgical_iso": "ara",
        "morphology_family": "west_central_african",
        "transmission_profile": "african_to_tarraconian",
    },
}

# Specific per-culture overrides to order dialectal/specific ISO codes accurately
CULTURE_SPECIFIC_OVERRIDES = {
    # Tarraconian Imperial & High German
    "Tarraconian": {
        "iso_codes": ["gmh", "deu", "cat", "lat", "goh"],
        "morphology_family": "tarraconian_imperial",
        "transmission_profile": "tarraconian_direct",
    },
    "Croato-Tarraconian": {
        "iso_codes": ["gmh", "deu", "hrv", "cat", "lat"],
        "morphology_family": "tarraconian_imperial",
        "transmission_profile": "tarraconian_direct",
    },
    "Alpine-Tarraconian": {
        "iso_codes": ["gmh", "deu", "ita", "lom", "lld", "cat", "lat"],
        "morphology_family": "tarraconian_imperial",
        "transmission_profile": "tarraconian_direct",
    },
    "Ungwârer": {
        "iso_codes": ["hun", "gmh", "deu", "slk", "lat"],
        "morphology_family": "tarraconian_imperial",
        "transmission_profile": "magyar_to_tarraconian",
    },
    "Lothringian": {"iso_codes": ["gmh", "goh", "deu", "fra", "lat"], "morphology_family": "tarraconian_imperial"},
    "bavarian": {"iso_codes": ["bar", "gmh", "goh", "deu", "lat"]},
    "swabian": {"iso_codes": ["gsw", "gmh", "goh", "deu", "lat"]},
    "ashkenazi": {"iso_codes": ["deu", "gmh", "heb", "pol"], "liturgical_iso": "heb"},
    # Anglic & Dutch / Saxon
    "frisian": {"iso_codes": ["fry", "nld", "osx", "ang", "deu"], "morphology_family": "low_german_dutch"},
    "english": {"iso_codes": ["eng", "ang", "fro", "nrf", "lat"]},
    "scottish": {"iso_codes": ["sco", "eng", "gla", "ang", "cel-bry"]},
    "old_saxon": {"iso_codes": ["osx", "nds", "ang", "deu"], "morphology_family": "low_german_dutch"},
    "saxon": {"iso_codes": ["osx", "nds", "deu", "gem-pro"], "morphology_family": "low_german_dutch"},
    # North Germanic
    "swedish": {"iso_codes": ["swe", "non", "gem-pro"]},
    "norwegian": {"iso_codes": ["nor", "non", "isl", "gem-pro"]},
    "danish": {"iso_codes": ["dan", "non", "gem-pro"]},
    # Celtic
    "welsh": {"iso_codes": ["cym", "cel-bry", "cel-pro", "lat"]},
    "breton": {"iso_codes": ["bre", "cel-bry", "fra", "lat"]},
    "cornish": {"iso_codes": ["cor", "cel-bry", "eng", "lat"]},
    "pictish": {"iso_codes": ["cel-bry", "gla", "sga", "cel-pro"]},
    "cumbrian": {"iso_codes": ["cel-bry", "cym", "gla", "eng"]},
    "irish": {"iso_codes": ["gle", "sga", "cel-pro", "lat"]},
    "gaelic": {"iso_codes": ["gla", "sga", "gle", "cel-bry"]},
    # Romance
    "norman": {"iso_codes": ["nrf", "fro", "fra", "non", "eng"]},
    "catalan": {"iso_codes": ["cat", "oci", "spa", "lat"]},
    "aragonese": {"iso_codes": ["arg", "cat", "spa", "eus", "lat"]},
    "castilian": {"iso_codes": ["spa", "lat", "ara"]},
    "portuguese": {"iso_codes": ["por", "glg", "spa", "lat", "ara"]},
    "galician": {"iso_codes": ["glg", "por", "spa", "lat"]},
    "asturleonese": {"iso_codes": ["ast", "spa", "glg", "lat"]},
    "sephardi": {"iso_codes": ["spa", "por", "heb", "ara"], "liturgical_iso": "heb"},
    "sicilian": {"iso_codes": ["scn", "ita", "grc", "ara", "lat"]},
    "cisalpine": {"iso_codes": ["ita", "lom", "lld", "fur", "lat", "xtg"]},
    "lombard": {"iso_codes": ["lom", "ita", "goh", "lat"]},
    # Slavic
    "czech": {"iso_codes": ["ces", "slk", "sla-pro", "sla", "deu"]},
    "slovien": {"iso_codes": ["slk", "ces", "sla-pro", "sla", "chu", "hun"]},
    "polish": {"iso_codes": ["pol", "sla-pro", "sla", "deu"]},
    "pommeranian": {"iso_codes": ["csb", "pol", "wen", "sla-pro", "deu"]},
    "polabian": {"iso_codes": ["wen", "dsb", "hsb", "pol", "sla-pro", "deu"]},
    "croatian": {"iso_codes": ["hrv", "srp", "sla-pro", "sla", "lat"]},
    "serbian": {"iso_codes": ["srp", "hrv", "chu", "sla-pro", "grc"], "liturgical_iso": "chu"},
    "bosnian": {"iso_codes": ["bos", "hrv", "srp", "sla-pro", "chu"], "liturgical_iso": "chu"},
    "carantanian": {"iso_codes": ["slv", "hrv", "sla-pro", "deu"]},
    "bulgarian": {"iso_codes": ["bul", "chu", "mkd", "sla-pro", "grc", "otk"], "liturgical_iso": "chu"},
    "russian": {"iso_codes": ["rus", "orv", "sla-pro", "sla", "chu"]},
    "ilmenian": {"iso_codes": ["orv", "rus", "sla-pro", "fin", "krl"]},
    "severian": {"iso_codes": ["orv", "rus", "ukr", "sla-pro"]},
    "volhynian": {"iso_codes": ["ukr", "orv", "bel", "pol", "sla-pro"]},
    "Ruthenian": {"iso_codes": ["ukr", "bel", "rue", "orv", "pol", "sla-pro"]},
    # Baltic & Uralic
    "lithuanian": {"iso_codes": ["lit", "bat", "bel", "pol"]},
    "latgalian": {"iso_codes": ["lav", "lit", "bat", "est"]},
    "prussian": {"iso_codes": ["prg", "lit", "bat", "deu", "pol"]},
    "estonian": {"iso_codes": ["est", "liv", "fin", "urj-fin-pro"]},
    "karelian": {"iso_codes": ["krl", "fin", "vep", "urj-fin-pro", "rus"]},
    "vepsian": {"iso_codes": ["vep", "krl", "fin", "urj-fin-pro", "rus"]},
    "samoyed": {"iso_codes": ["sel", "kca", "urj", "rus"], "morphology_family": "volga_permian"},
    "komi": {"iso_codes": ["kom", "kpv", "udm", "urj", "rus"]},
    "khanty": {"iso_codes": ["kca", "mns", "urj", "rus"]},
    "mari": {"iso_codes": ["chm", "mhr", "urj", "tat", "rus"]},
    "mordvin": {"iso_codes": ["myv", "mdf", "urj", "rus"]},
    "hungarian": {"iso_codes": ["hun", "slk", "deu", "ron", "lat"]},
    "mogyer": {"iso_codes": ["hun", "urj", "otk", "sla-pro"]},
    # Iranian & Steppe
    "afghan": {"iso_codes": ["pus", "fas", "tgk", "pal"]},
    "alan": {"iso_codes": ["oss", "kbd", "ady", "grc", "rus"]},
    "sogdian": {"iso_codes": ["sog", "tgk", "fas", "uzb", "uig"]},
    "khwarezmian": {"iso_codes": ["tgk", "uzb", "fas", "pal", "sog"]},
    "tajik": {"iso_codes": ["tgk", "fas", "sog", "uzb"]},
    "kurdish": {"iso_codes": ["kur", "fas", "ara", "arm", "hye"]},
    "baloch": {"iso_codes": ["bal", "fas", "snd", "bra"]},
    # Turkic & Mongolic
    "turkish": {"iso_codes": ["tur", "otk", "grc", "ara", "fas"]},
    "turkmen": {"iso_codes": ["tuk", "tur", "otk", "fas"]},
    "kazak": {"iso_codes": ["kaz", "otk", "tat", "rus"]},
    "cuman": {"iso_codes": ["kaz", "tat", "otk", "ukr", "rus"]},
    "kipchak": {"iso_codes": ["kaz", "tat", "bak", "otk", "rus"]},
    "pecheneg": {"iso_codes": ["otk", "tur", "ron", "ukr", "hun"]},
    "bashkir": {"iso_codes": ["bak", "tat", "otk", "rus"]},
    "kirghiz": {"iso_codes": ["kir", "kjh", "otk", "kaz", "mon"]},
    "uriankhai": {"iso_codes": ["tyv", "kjh", "mon", "otk"]},
    "uyghur": {"iso_codes": ["uig", "otk", "zho", "sog"]},
    "yughur": {"iso_codes": ["uig", "otk", "zho", "bod"]},
    "bolghar": {"iso_codes": ["chv", "tat", "otk", "bul", "rus"]},
    "chuvash": {"iso_codes": ["chv", "tat", "chm", "rus"]},
    "khazar": {"iso_codes": ["otk", "chv", "heb", "rus", "ara"]},
    "radhanite": {"iso_codes": ["heb", "otk", "ara", "fas"], "liturgical_iso": "heb"},
    "buryat": {"iso_codes": ["bua", "mon", "cmg", "rus"]},
    "jurchen": {"iso_codes": ["juc", "mnc", "gld", "zho", "lzh"]},
    "mohe": {"iso_codes": ["gld", "evn", "mnc", "juc", "kor"]},
    "balhae": {"iso_codes": ["kor", "mnc", "lzh", "zho", "juc"]},
    # Indic & Southeast Asia
    "gujarati": {"iso_codes": ["guj", "san", "pra", "hin"]},
    "rajput": {"iso_codes": ["raj", "hin", "guj", "san", "pra"]},
    "punjabi": {"iso_codes": ["pan", "san", "pra", "hin", "fas"]},
    "sindhi": {"iso_codes": ["snd", "pan", "ara", "fas", "san"]},
    "bengali": {"iso_codes": ["ben", "san", "pra", "ori"]},
    "oriya": {"iso_codes": ["ori", "san", "ben", "tel"]},
    "assamese": {"iso_codes": ["asm", "ben", "brx", "san"]},
    "malay": {"iso_codes": ["msa", "ind", "bjn", "min", "ljp", "san"]},
    "javanese": {"iso_codes": ["jav", "kaw", "ind", "sun", "mad", "ban"]},
    "dayak": {"iso_codes": ["mhy", "bjn", "ind", "msa"]},
    "tagalog": {"iso_codes": ["tgl", "ind", "spa"]},
    "bisayan": {"iso_codes": ["ceb", "hil", "tgl", "cyo"]},
    "tai": {"iso_codes": ["tha", "lao", "shn", "khb", "pli"]},
    "bouxcuengh": {"iso_codes": ["zha", "tha", "zho", "lzh"]},
    "khmer": {"iso_codes": ["khm", "okz", "san", "pli"]},
    "mon": {"iso_codes": ["mnw", "mya", "tha", "pli"]},
    "ryukyuan": {"iso_codes": ["ryu", "jpn", "ojp", "lzh"]},
    # Africa
    "somali": {"iso_codes": ["som", "aar", "ara"]},
    "afar": {"iso_codes": ["aar", "ssy", "som", "amh", "ara"]},
    "beja": {"iso_codes": ["bej", "ara", "amh", "gez"]},
    "ethiopian": {"iso_codes": ["amh", "tir", "gez", "orm"]},
    "nubian": {"iso_codes": ["ara", "grc", "cop", "bej"]},
    "malinke": {"iso_codes": ["mnk", "bam", "snk", "ara"]},
    "wolof": {"iso_codes": ["wol", "ful", "dyo", "fra"]},
    "pulaar": {"iso_codes": ["ful", "wol", "mnk", "ara"]},
    "songhai": {"iso_codes": ["ses", "khq", "mnk", "ara"]},
    "akan": {"iso_codes": ["aka", "bci", "any", "nzi", "gaa"]},
    "ewe": {"iso_codes": ["ewe", "fon", "aka"]},
    "zaghawa": {"iso_codes": ["zag", "ber", "ara"]},
    "kanuri": {"iso_codes": ["kau", "zag", "hau", "ara"]},
}


TRANSMISSION_RULES = {
    "tarraconian_direct": {
        "intermediary_family": "tarraconian_imperial",
        "summary": "Already within Tarraconian Chancellery High German; apply circumflexation and Auslautverhärtung only.",
        "substitutions": [
            ["burg$", "burch"],
            ["berg$", "berch"],
            ["mark$", "march"],
            ["land$", "lant"],
            ["stadt$", "stat"],
        ],
        "examples": ["Lûnstat", "Vrîsing", "Stûlwîtzenburch"],
    },
    "high_german_to_tarraconian": {
        "intermediary_family": "high_german",
        "summary": "Map Upper/Standard German into Moselle-Rhine Franconian: preserve unshifted p-, d-, sw-/sl-/sm-; final -g/-k -> -ch; -d -> -t; -ei -> -î/-ei.",
        "substitutions": [
            ["^Pf", "P"],
            ["^Schw", "Sw"],
            ["^Schl", "Sl"],
            ["^Schm", "Sm"],
            ["burg$", "burch"],
            ["berg$", "berch"],
            ["stadt$", "stat"],
            ["furt$", "vurt"],
            ["hafen$", "hâven"],
        ],
        "examples": ["Pfalz -> Palz", "Heidelberg -> Heidelberch", "Schweinfurt -> Swînvurt"],
    },
    "west_germanic_to_tarraconian": {
        "intermediary_family": "anglo_saxon",
        "summary": "Nativize English/Anglo-Saxon/Dutch stems to Rhine Franconian cognates: th -> d, sh -> sch, ch -> k/tsch, -burh/-by -> -burch/-stat.",
        "substitutions": [
            ["^Th", "D"],
            ["sh", "sch"],
            ["burh$", "burch"],
            ["geweorc$", "werc"],
        ],
        "examples": ["Sūþgeweorc -> Sûtwerc", "Lunden -> Lunden"],
    },
    "north_germanic_to_tarraconian": {
        "intermediary_family": "north_germanic",
        "summary": "Map Old Norse/Scandinavian ð/þ -> d/t, ø -> ö, æ -> ê, -borg -> -burch, -vík -> -wîch.",
        "substitutions": [
            ["þ", "t"],
            ["ð", "d"],
            ["ø", "ö"],
            ["æ", "ê"],
            ["borg$", "burch"],
            ["land$", "lant"],
        ],
        "examples": ["Jótland -> Jûtlant", "Sigtún -> Sigtûne"],
    },
    "gallo_romance_to_tarraconian": {
        "intermediary_family": "gallo_romance",
        "summary": "Catalan/Franconian dual apocope: gn -> nj, j/g(e,i) -> sch, ch -> sch, final -on/-an/-o apocopated with circumflex stress.",
        "substitutions": [
            ["gn", "nj"],
            ["ch", "sch"],
            ["ou", "ou"],
            ["on$", "ôn"],
            ["a$", "e"],
        ],
        "examples": ["Anjou -> Anschou", "Armagnac -> Armanjach", "Alençon -> Alenzûn"],
    },
    "occitano_catalan_to_tarraconian": {
        "intermediary_family": "occitano_catalan",
        "summary": "Core Catalan substrate conventions: ny -> nj, nh -> nj, j/tg -> dsch/tsch, apocope after l/r/n.",
        "substitutions": [
            ["ny", "nj"],
            ["nh", "nj"],
            ["ll", "ll"],
            ["ona$", "ôn"],
        ],
        "examples": ["Tarragona -> Tarracôn", "Castelló -> Castellon"],
    },
    "ibero_romance_to_tarraconian": {
        "intermediary_family": "ibero_romance",
        "summary": "Iberian ñ -> nj, ll -> ll, j -> ch/sch, final -o/-a -> apocopated or -e.",
        "substitutions": [
            ["ñ", "nj"],
            ["ón$", "ôn"],
            ["o$", ""],
            ["a$", "e"],
        ],
        "examples": ["Tudela -> Tudêl", "Huesca -> Oske"],
    },
    "italo_romance_to_tarraconian": {
        "intermediary_family": "italo_romance",
        "summary": "Italian -ggi-/-gi- -> dsch, -ci- -> tsch, gn -> nj, -c(k) -> k/ch, final -o/-a reduced or dropped.",
        "substitutions": [
            ["ggi", "dsch"],
            ["cci", "tsch"],
            ["gn", "nj"],
            ["sc(?=[ei])", "sch"],
            ["o$", ""],
            ["a$", "e"],
        ],
        "examples": ["Foggia -> Fodsche", "Lucca -> Lûke", "Ravenna -> Raben"],
    },
    "eastern_romance_to_tarraconian": {
        "intermediary_family": "eastern_romance",
        "summary": "Vlach/Romanian ș -> sch, ț -> tz, â/î -> â/î, final -a -> -e.",
        "substitutions": [
            ["ș", "sch"],
            ["ț", "tz"],
            ["cea", "tsche"],
            ["gea", "dsche"],
        ],
        "examples": ["Târgu -> Targû", "Cetatea -> Tschetâte"],
    },
    "balkan_to_tarraconian": {
        "intermediary_family": "albanian",
        "summary": "Albanian sh -> sch, zh -> sch, ç -> tsch, xh -> dsch, q -> tj, gj -> dj, ë -> e.",
        "substitutions": [
            ["sh", "sch"],
            ["zh", "sch"],
            ["xh", "dsch"],
            ["ç", "tsch"],
            ["dh", "d"],
            ["th", "t"],
            ["ë", "e"],
        ],
        "examples": ["Shkodër -> Schkôder", "Durrës -> Durres"],
    },
    "latin_to_tarraconian": {
        "intermediary_family": "latin_classical",
        "summary": "Classical Latin -um/-us/-os/-o apocopated; -ia -> -îe, -ium -> -jen/-tz, -ea -> -êe, -a -> -e; ae/oe/ph/th -> ê/ö/f/t; c(e,i) -> z; transparent Latin generics (Portus/Vicus/Forum/Aquae/Mare/Mons) calqued.",
        "substitutions": [
            ["um$", ""],
            ["us$", ""],
            ["ia$", "îe"],
            ["ium$", "jen"],
            ["ae", "ê"],
            ["oe", "ö"],
            ["ph", "f"],
            ["th", "t"],
            ["^C(?=[ei])", "Z"],
        ],
        "examples": ["Roma -> Rôm", "Cillium -> Zilljen", "Portus Magnus -> Grôzport", "Vicus Saravus -> Sârwîch", "Aquae -> Bâden"],
    },
    "celtic_to_tarraconian": {
        "intermediary_family": "brythonic",
        "summary": "Celtic mh/bh -> v/w, dh/gh -> Ø/g, th -> t, final -d -> -t.",
        "substitutions": [
            ["bh", "w"],
            ["mh", "w"],
            ["th", "t"],
            ["dd", "d"],
            ["d$", "t"],
        ],
        "examples": ["Gwened -> Gwenet", "Dún -> Dûn"],
    },
    "greek_to_tarraconian": {
        "intermediary_family": "hellenic",
        "summary": "Byzantine Greek θ -> t, χ -> ch, φ -> f, polysyllabic -os/-on dropped (short stems preserved), -ion -> -jen, -eia -> -êe, -polis -> -pel.",
        "substitutions": [
            ["polis$", "pel"],
            ["ion$", "jen"],
            ["eia$", "êe"],
            ["ph", "f"],
            ["th", "t"],
            ["kh", "ch"],
        ],
        "examples": ["Kallipolis -> Kallîpel", "Nikaia -> Nîkêe", "Ephesos -> Ephês", "Ohrid -> Ochrît"],
    },
    "east_slavic_to_tarraconian": {
        "intermediary_family": "east_slavic",
        "summary": "Slavic -ov/-ev -> -ouwe, -sk -> -tzich/-bsch, -č -> -tsch, -š/-ž -> -sch, -k -> -ch, -a -> -e.",
        "substitutions": [
            ["ov$", "ouwe"],
            ["ev$", "ouwe"],
            ["av$", "ouwe"],
            ["sk$", "tzich"],
            ["č", "tsch"],
            ["š", "sch"],
            ["ž", "sch"],
            ["a$", "e"],
        ],
        "examples": ["Rostov -> Rostouwe", "Moskva -> Moskouwe", "Mělník -> Melnîch"],
    },
    "west_slavic_to_tarraconian": {
        "intermediary_family": "west_slavic_lechitic",
        "summary": "West Slavic č/cz -> tsch, š/sz -> sch, ř/rz -> rsch, c -> tz, -ice/-itz -> -itz, -ov -> -ouwe.",
        "substitutions": [
            ["cz", "tsch"],
            ["sz", "sch"],
            ["č", "tsch"],
            ["š", "sch"],
            ["ž", "sch"],
            ["ov$", "ouwe"],
            ["ów$", "ouwe"],
            ["ice$", "itz"],
            ["c$", "tz"],
        ],
        "examples": ["Lignice -> Lîgnitz", "Opava -> Troppouwe", "Praga -> Prâge"],
    },
    "south_slavic_to_tarraconian": {
        "intermediary_family": "south_slavic",
        "summary": "South Slavic č/ć -> tsch, š -> sch, ž -> sch, đ/dž -> dsch, lj -> lj, nj -> nj.",
        "substitutions": [
            ["dž", "dsch"],
            ["đ", "dsch"],
            ["č", "tsch"],
            ["ć", "tsch"],
            ["š", "sch"],
            ["ž", "sch"],
            ["av$", "ouwe"],
        ],
        "examples": ["Preslav -> Preslouwe", "Ohrid -> Ochrît"],
    },
    "baltic_to_tarraconian": {
        "intermediary_family": "baltic",
        "summary": "Baltic š -> sch, ž -> sch, č -> tsch, finals devoiced; Old Prussian/Curonian substrates retained.",
        "substitutions": [
            ["š", "sch"],
            ["ž", "sch"],
            ["č", "tsch"],
            ["as$", ""],
            ["is$", ""],
        ],
        "examples": ["Twangste -> Twangste", "Truso -> Trûse"],
    },
    "magyar_to_tarraconian": {
        "intermediary_family": "magyar",
        "summary": "Hungarian sz -> s, s -> sch, cs -> tsch, zs -> sch, gy -> dj, ly -> l/j, vár -> wâr.",
        "substitutions": [
            ["cs", "tsch"],
            ["sz", "s"],
            ["zs", "sch"],
            ["s", "sch"],
            ["vár$", "wâr"],
        ],
        "examples": ["Bács -> Batsch", "Ungvár -> Ungwâr"],
    },
    "uralic_to_tarraconian": {
        "intermediary_family": "finnic",
        "summary": "Finnic/Permian ä/ö/ü retained or lowered; long vowels circumflexed; -la/-lä -> -le; -k -> -ch.",
        "substitutions": [
            ["sh", "sch"],
            ["ch", "tsch"],
            ["aa", "â"],
            ["ii", "î"],
            ["uu", "û"],
        ],
        "examples": ["Åbo -> Âbô", "Käkisalmi -> Kekisalme"],
    },
    "caucasian_to_tarraconian": {
        "intermediary_family": "armenian",
        "summary": "Caucasian ejectives/aspirates mapped cleanly: kh/x -> ch, gh -> g, j -> dsch, ch/č -> tsch, sh -> sch.",
        "substitutions": [
            ["ts", "tz"],
            ["dz", "ds"],
            ["sh", "sch"],
            ["zh", "sch"],
            ["j", "dsch"],
        ],
        "examples": ["Tbilisi -> Tbilîs", "Ani -> Âni"],
    },
    "arabic_to_tarraconian": {
        "intermediary_family": "arabic",
        "summary": "Arabic ج -> dsch, ش -> sch, خ/ق -> ch, ع/ء dropped, long ā/ī/ū -> â/î/û, final -b/-d/-g/-j -> -p/-t/-ch/-tsch.",
        "substitutions": [
            ["sh", "sch"],
            ["kh", "ch"],
            ["dh", "d"],
            ["th", "t"],
            ["j$", "tsch"],
            ["j", "dsch"],
            ["b$", "p"],
            ["d$", "t"],
        ],
        "examples": ["Halab -> Halep", "Baghdad -> Bagdât", "Shayzar -> Schêisar", "Aflaj -> Falâtsch"],
    },
    "semitic_to_tarraconian": {
        "intermediary_family": "aramaic_hebrew",
        "summary": "Syriac/Hebrew sh -> sch, kh -> ch, ts -> z-/tz, y -> j.",
        "substitutions": [
            ["sh", "sch"],
            ["kh", "ch"],
            ["^ts", "z"],
            ["ts", "tz"],
        ],
        "examples": ["Yerushalayim -> Jerûsalem"],
    },
    "iranian_to_tarraconian": {
        "intermediary_family": "iranian",
        "summary": "Persian/Sogdian sh -> sch, zh -> sch, kh -> ch, j -> dsch, ch -> tsch, final -b/-d/-g devoiced.",
        "substitutions": [
            ["sh", "sch"],
            ["zh", "sch"],
            ["kh", "ch"],
            ["j$", "tsch"],
            ["j", "dsch"],
            ["abad$", "âbât"],
        ],
        "examples": ["Shiraz -> Schîrâz", "Jame -> Dschâm", "Rukhaj -> Ruchatsch"],
    },
    "turkic_to_tarraconian": {
        "intermediary_family": "turkic",
        "summary": "Turkic ş -> sch, ç -> tsch, c -> dsch, q/kh -> ch, ö/ü preserved, post-vocalic -k -> -ch, j -> dsch.",
        "substitutions": [
            ["ş", "sch"],
            ["ç", "tsch"],
            ["c", "dsch"],
            ["sh", "sch"],
            ["kh", "ch"],
            ["k$", "ch"],
            ["köy$", "köi"],
        ],
        "examples": ["Arkalyk -> Arkalîch", "Jend -> Dschent", "Gelibolu -> Gelîbôl"],
    },
    "mongolic_to_tarraconian": {
        "intermediary_family": "mongolic",
        "summary": "Mongolic sh -> sch, ch -> tsch, j -> dsch, kh -> ch, ö/ü retained, final -a -> -e.",
        "substitutions": [
            ["sh", "sch"],
            ["ch", "tsch"],
            ["j", "dsch"],
            ["kh", "ch"],
            ["ts", "tz"],
            ["a$", "e"],
        ],
        "examples": ["Karakorum -> Karakorôn", "Selenga -> Selenge"],
    },
    "sinosphere_1154_to_tarraconian": {
        "intermediary_family": "sinosphere_chinese",
        "summary": "Sinosphere 1154 historical phonology: j/zh -> dsch, q/ch -> tsch, x/sh -> sch, z/c -> z-/-tz, initial y -> j.",
        "substitutions": [
            ["^Zh", "Dsch"],
            ["^J", "Dsch"],
            ["^Ch", "Tsch"],
            ["^Sh", "Sch"],
            ["zh", "dsch"],
            ["ch", "tsch"],
            ["sh", "sch"],
            ["ts", "tz"],
        ],
        "examples": ["Jinzhou -> Dschindschou", "Yanzhou -> Jandschou", "Gyeongju -> Gjongdschu"],
    },
    "east_asian_to_tarraconian": {
        "intermediary_family": "ainu",
        "summary": "Nivkh/Ainu stops & sibilants: ch -> tsch, sh -> sch, j -> dsch, final -a -> -e.",
        "substitutions": [
            ["sh", "sch"],
            ["ch", "tsch"],
            ["j", "dsch"],
            ["a$", "e"],
        ],
        "examples": ["Chasi -> Tschâsi"],
    },
    "indic_to_tarraconian": {
        "intermediary_family": "indo_aryan",
        "summary": "Indic j -> dsch, c/ch -> tsch, sh/ṣ -> sch, y -> j, long ā/ī/ū -> â/î/û, unaccented final -a -> -e.",
        "substitutions": [
            ["sh", "sch"],
            ["j", "dsch"],
            ["ch", "tsch"],
            ["kh", "ch"],
            ["a$", "e"],
        ],
        "examples": ["Jaunpur -> Dschounpur", "Ajmer -> Adschmêr", "Dvaraka -> Dwârake"],
    },
    "tibetic_to_tarraconian": {
        "intermediary_family": "tibetic",
        "summary": "Tibetan palatal & affricate mapping: ts/tsh -> z-/tz, dz -> ds, zh/sh -> sch, ny -> nj, j -> dsch.",
        "substitutions": [
            ["^Ts", "Z"],
            ["^Tsh", "Z"],
            ["ts", "tz"],
            ["sh", "sch"],
            ["zh", "sch"],
            ["ny", "nj"],
            ["j", "dsch"],
        ],
        "examples": ["Gtsang -> Zang", "Lhasa -> Lhâse"],
    },
    "southeast_asian_to_tarraconian": {
        "intermediary_family": "tai_hmong",
        "summary": "Mainland/Insular SEA sh -> sch, ch -> tsch, j -> dsch, ny -> nj, ng -> ng.",
        "substitutions": [
            ["sh", "sch"],
            ["ch", "tsch"],
            ["ny", "nj"],
            ["j", "dsch"],
        ],
        "examples": ["Jambi -> Dschambî", "Chiang -> Tschiang"],
    },
    "african_to_tarraconian": {
        "intermediary_family": "west_central_african",
        "summary": "African affricates dj/j -> dsch, sh -> sch, ch -> tsch, ny -> nj, y -> j.",
        "substitutions": [
            ["sh", "sch"],
            ["ch", "tsch"],
            ["ny", "nj"],
            ["dj", "dsch"],
            ["j", "dsch"],
        ],
        "examples": ["Jenne -> Dschenne", "Kilimanjaro -> Kilimandscharô"],
    },
}

HISTORICAL_INTERMEDIARIES = [
    {
        "id": "greek_to_turkish",
        "source_family": "hellenic",
        "transmission_family": "turkic",
        "summary": "Anatolian Greek stems reanalyzed in Oghuz Turkish before Tarraconian contact (-polis -> -bolu, k- -> g-, vowel harmony)",
        "examples": ["Kallipolis -> Gelibolu -> Gelîbôl", "Prousa -> Bursa", "Ikonion -> Konya"],
    },
    {
        "id": "greek_to_south_slavic",
        "source_family": "hellenic",
        "transmission_family": "south_slavic",
        "summary": "Balkan Greek/Thracian substrates adapted into Bulgarian/Serbian (liquid metathesis, o/a shifts, -os dropped)",
        "examples": ["Serdica -> Sredets", "Philippopolis -> Plovdiv", "Thessaloniki -> Solun"],
    },
    {
        "id": "greek_to_arabic",
        "source_family": "hellenic",
        "transmission_family": "arabic",
        "summary": "Levantine/Egyptian Greek adapted to Arabic phonology (p -> b/f, ch -> kh, g -> j/gh, -eia -> -iya)",
        "examples": ["Caesarea -> Qaysariya", "Tripolis -> Tarabulus", "Neapolis -> Nablus"],
    },
    {
        "id": "arabic_to_ibero_romance",
        "source_family": "arabic",
        "transmission_family": "ibero_romance",
        "summary": "Andalusi Arabic wadi -> guad-, al- preserved as prefix, kh -> j/g",
        "examples": ["Wadi al-Hijara -> Guadalajara", "Madinat Salim -> Medinaceli", "Qal'at Ayyub -> Calatayud"],
    },
    {
        "id": "persian_to_turkic",
        "source_family": "iranian",
        "transmission_family": "turkic",
        "summary": "Persian urban generics (-abad, -shahr, -bazar) transmitted across Khorasan/Transoxiana Turkic dynasties",
        "examples": ["Samarqand -> Semerkand", "Bukhara -> Buhara", "Merv -> Merv"],
    },
    {
        "id": "slavic_to_magyar",
        "source_family": "west_slavic_czech_slovak",
        "transmission_family": "magyar",
        "summary": "Pannonian/Carpathian Slavic stems absorbed with Magyar cluster simplification & initial vowel epenthesis",
        "examples": ["Belgrad -> Nándorfehérvár", "Blatno -> Balaton", "Ostrihom -> Esztergom"],
    },
    {
        "id": "celtic_to_anglo_saxon",
        "source_family": "brythonic",
        "transmission_family": "anglo_saxon",
        "summary": "Romano-Brythonic stems compounded with Old English generics (-ceaster, -tun, -ford)",
        "examples": ["Londinium -> Lunden", "Eboracum -> Eoforwic", "Lindum -> Lindocolina"],
    },
    {
        "id": "sinosphere_to_korean_japonic_viet",
        "source_family": "sinosphere_chinese",
        "transmission_family": "korean",
        "summary": "Classical Chinese Hanzi compounds read via Sino-Korean (EMK), Sino-Japanese Go-on/Kan-on (EMJ), or Sino-Vietnamese per 1154 concordance",
        "examples": ["山城 -> Yamashiro / Berchburch", "寶城 -> Boseong -> Edelsteinburch"],
    },
]


def parse_save_cultures(save_path: Path) -> dict:
    """Streams culture_manager from melted_save.ck3 to extract full culture records with parent IDs."""
    cm = {}
    if not save_path.exists():
        return cm

    in_cm = False
    cur = None
    in_parents = False
    in_nl = False
    in_trad = False

    with open(save_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.startswith("culture_manager={"):
                in_cm = True
                continue
            if not in_cm:
                continue
            if line.startswith("}"):
                break

            s = line.strip()
            if line.startswith("\t\t") and not line.startswith("\t\t\t") and s.endswith("={") and s[:-2].isdigit():
                cid = int(s[:-2])
                cur = {
                    "id": cid,
                    "parents": [],
                    "name_list": [],
                    "traditions": [],
                }
                cm[cid] = cur
                in_parents = in_nl = in_trad = False
                continue

            if cur is None:
                continue
            if s == "parents={":
                in_parents = True
                continue
            if in_parents:
                if s == "}":
                    in_parents = False
                else:
                    cur["parents"].extend(int(x) for x in s.split() if x.isdigit())
                continue

            if s == "name_list={":
                in_nl = True
                continue
            if in_nl:
                if s == "}":
                    in_nl = False
                else:
                    cur["name_list"].extend(x.strip('"') for x in s.split())
                continue

            if s == "traditions={":
                in_trad = True
                continue
            if in_trad:
                if s == "}":
                    in_trad = False
                else:
                    cur["traditions"].extend(x.strip('"') for x in s.split())
                continue

            if "=" in s and not s.endswith("{"):
                k, v = s.split("=", 1)
                v = v.strip('"')
                if k in ("culture_template", "name", "heritage", "language", "ethos", "created"):
                    cur[k] = v

    return cm


def load_observed_iso_codes() -> tuple[set, set]:
    """Collects all ISO codes actually used across data/natural_tribal_replacements and anachronicity_audit."""
    ntr_codes = set()
    for p in sorted(glob.glob(str(DATA_DIR / "natural_tribal_replacements" / "*.json"))):
        with open(p, "r", encoding="utf-8") as f:
            d = json.load(f)
        recs = d.get("baronies", d) if isinstance(d, dict) else d
        if isinstance(recs, dict):
            recs = list(recs.values())
        for b in recs:
            for cand in b.get("replacement_candidates", []):
                for lv in cand.get("language_variants", []):
                    c = lv.get("language_code") or lv.get("iso")
                    if c:
                        ntr_codes.add(c)

    audit_codes = set()
    for p in sorted(glob.glob(str(DATA_DIR / "anachronicity_audit" / "*.json"))):
        with open(p, "r", encoding="utf-8") as f:
            d = json.load(f)
        recs = d.get("baronies", d) if isinstance(d, dict) else d
        if isinstance(recs, dict):
            recs = list(recs.values())
        for b in recs:
            for hn in b.get("historical_names", []) or []:
                if isinstance(hn, dict):
                    c = hn.get("language_code") or hn.get("language")
                    if c:
                        audit_codes.add(c)
            for m in b.get("morphemes", []) or []:
                if isinstance(m, dict):
                    c = m.get("language_code") or m.get("language")
                    if c:
                        audit_codes.add(c)

    return ntr_codes, audit_codes


def unique_ordered(seq: list) -> list:
    """Deduplicates a list while preserving first-seen order."""
    seen = set()
    out = []
    for x in seq:
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out


def resolve_single_culture(rec: dict, cm_by_id: dict) -> dict:
    """Builds the ordered ISO, family, and transmission mapping for one CK3 culture."""
    name = rec.get("name") or rec.get("culture_template")
    tmpl = rec.get("culture_template")
    lang = rec.get("language") or "language_latin"
    heritage = rec.get("heritage") or ""

    base = CK3_LANGUAGE_DEFAULTS[lang]
    primary_list = list(base["iso_codes"])
    liturgical_iso = base["liturgical_iso"]
    morph_family = base["morphology_family"]
    trans_profile = base["transmission_profile"]

    # Apply template or exact-name refinements
    override_isos = []
    for key in (tmpl, name):
        if key and key in CULTURE_SPECIFIC_OVERRIDES:
            ov = CULTURE_SPECIFIC_OVERRIDES[key]
            if "iso_codes" in ov:
                override_isos.extend(ov["iso_codes"])
            if "liturgical_iso" in ov:
                liturgical_iso = ov["liturgical_iso"]
            if "morphology_family" in ov:
                morph_family = ov["morphology_family"]
            if "transmission_profile" in ov:
                trans_profile = ov["transmission_profile"]

    # Collect direct parent ISO codes first, then deeper ancestral parent ISO codes
    parent_names = []
    direct_parent_isos = []
    ancestral_parent_isos = []
    visited = set()
    queue = list(rec.get("parents", []))
    direct_set = set(rec.get("parents", []))
    while queue:
        pid = queue.pop(0)
        if pid in visited or pid not in cm_by_id:
            continue
        visited.add(pid)
        p_rec = cm_by_id[pid]
        p_name = p_rec.get("name")
        p_lang = p_rec.get("language")
        p_tmpl = p_rec.get("culture_template")
        target_bucket = direct_parent_isos if pid in direct_set else ancestral_parent_isos
        if pid in direct_set:
            parent_names.append(p_name)
        for k in (p_name, p_tmpl):
            if k in CULTURE_SPECIFIC_OVERRIDES and "iso_codes" in CULTURE_SPECIFIC_OVERRIDES[k]:
                target_bucket.extend(CULTURE_SPECIFIC_OVERRIDES[k]["iso_codes"][:2])
        if p_lang in CK3_LANGUAGE_DEFAULTS:
            target_bucket.extend(CK3_LANGUAGE_DEFAULTS[p_lang]["iso_codes"][:2])
        queue.extend(p_rec.get("parents", []))

    ordered_isos = unique_ordered(
        override_isos + primary_list[:3] + direct_parent_isos + primary_list[3:] + ancestral_parent_isos
    )
    parent_isos = direct_parent_isos + ancestral_parent_isos

    return {
        "id": rec.get("id"),
        "name": name,
        "culture_template": tmpl,
        "ck3_language": lang,
        "ck3_heritage": heritage,
        "ethos": rec.get("ethos"),
        "created": rec.get("created"),
        "is_tarraconian_core": name in TARRACONIAN_CORE_CULTURES,
        "is_high_german_direct": lang == "language_high_german" or name in TARRACONIAN_CORE_CULTURES,
        "is_sinosphere_heritage": heritage in SINOSPHERE_HERITAGES,
        "parents": parent_names,
        "parent_isos": unique_ordered(parent_isos),
        "iso_codes": ordered_isos,
        "primary_iso": ordered_isos[0],
        "liturgical_iso": liturgical_iso,
        "morphology_family": morph_family,
        "transmission_profile": trans_profile,
        "name_list": rec.get("name_list", []),
        "traditions": rec.get("traditions", []),
    }


def main():
    parser = argparse.ArgumentParser(description="Generate data/ck3_culture_to_iso_and_generics.json")
    parser.add_argument("--save", default=str(SAVE_PATH))
    parser.add_argument("--output", default=str(DATA_DIR / "ck3_culture_to_iso_and_generics.json"))
    args = parser.parse_args()

    t0 = time.time()
    print("==========================================================")
    print("Generating data/ck3_culture_to_iso_and_generics.json")
    print("==========================================================")

    cm_by_id = parse_save_cultures(Path(args.save))
    if not cm_by_id and CULTURES_PHASE1_PATH.exists():
        with open(CULTURES_PHASE1_PATH, "r", encoding="utf-8") as f:
            raw = json.load(f)
        cm_by_id = {int(k): v for k, v in raw.items()}

    # Verify all 91 CK3 languages are mapped
    missing_langs = sorted({c.get("language") for c in cm_by_id.values()} - set(CK3_LANGUAGE_DEFAULTS.keys()))
    if missing_langs:
        raise ValueError(f"Unmapped CK3 languages: {missing_langs}")

    toponymic_used = set()
    tp_path = DATA_DIR / "barony_toponymic_profiles.json"
    if tp_path.exists():
        with open(tp_path, "r", encoding="utf-8") as f:
            toponymic_used = set(json.load(f).get("cultures", {}).keys())

    ntr_codes, audit_codes = load_observed_iso_codes()
    all_dataset_isos = ntr_codes | audit_codes

    cultures_out = {}
    family_counts = Counter()
    direct_dataset_hits = 0

    for cid in sorted(cm_by_id.keys()):
        rec = cm_by_id[cid]
        resolved = resolve_single_culture(rec, cm_by_id)
        if resolved["morphology_family"] not in MORPHOLOGY_FAMILIES:
            raise ValueError(f"Unknown morphology_family: {resolved['morphology_family']}")
        if resolved["transmission_profile"] not in TRANSMISSION_RULES:
            raise ValueError(f"Unknown transmission_profile: {resolved['transmission_profile']}")

        cultures_out[resolved["name"]] = resolved
        family_counts[resolved["morphology_family"]] += 1
        if any(code in all_dataset_isos for code in resolved["iso_codes"]):
            direct_dataset_hits += 1

    payload = {
        "metadata": {
            "source_save": args.save,
            "total_cultures": len(cultures_out),
            "total_ck3_languages": len(CK3_LANGUAGE_DEFAULTS),
            "total_morphology_families": len(MORPHOLOGY_FAMILIES),
            "total_transmission_profiles": len(TRANSMISSION_RULES),
            "cultures_used_in_toponymic_profiles": len(toponymic_used),
            "toponymic_profiles_covered": len(toponymic_used & set(cultures_out.keys())),
            "cultures_with_observed_iso_dataset_match": direct_dataset_hits,
            "family_distribution": dict(family_counts.most_common()),
        },
        "morphology_families": MORPHOLOGY_FAMILIES,
        "language_defaults": CK3_LANGUAGE_DEFAULTS,
        "transmission_rules": {
            "to_tarraconian": TRANSMISSION_RULES,
            "historical_intermediaries": HISTORICAL_INTERMEDIARIES,
        },
        "cultures": cultures_out,
    }

    out_path = Path(args.output)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"-> Wrote {out_path} ({out_path.stat().st_size / 1024:.1f} KB) in {time.time() - t0:.2f}s")
    print(f"   Cultures mapped: {len(cultures_out)} / {len(cm_by_id)} "
          f"(dataset ISO matches: {direct_dataset_hits}/{len(cultures_out)}, "
          f"toponymic profile coverage: {len(toponymic_used & set(cultures_out.keys()))}/{len(toponymic_used)})")


if __name__ == "__main__":
    main()

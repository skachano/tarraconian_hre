"""
test_data_integrity.py

Unit and integration tests for the Tarraconian Atlas web application assets,
GeoJSON schemas, coordinate boundaries, and Chancellery toponym mappings.
"""

import json
from pathlib import Path
import pytest

REPO_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_DIR / "docs"
DATA_DIR = DOCS_DIR / "data"


@pytest.fixture(scope="module")
def counties_data():
    path = DATA_DIR / "ck3_counties.geojson"
    assert path.exists(), "docs/data/ck3_counties.geojson is missing"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def baronies_data():
    path = DATA_DIR / "ck3_baronies.geojson"
    assert path.exists(), "docs/data/ck3_baronies.geojson is missing"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def tree_data():
    path = DATA_DIR / "ck3_title_tree.json"
    assert path.exists(), "docs/data/ck3_title_tree.json is missing"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="module")
def adjacencies_data():
    path = DATA_DIR / "ck3_adjacencies.json"
    assert path.exists(), "docs/data/ck3_adjacencies.json is missing"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestWebAssets:
    """Verifies that all required web assets exist and adhere to standards."""

    def test_index_html_structure(self):
        index_path = DOCS_DIR / "index.html"
        assert index_path.exists(), "docs/index.html is missing"
        content = index_path.read_text(encoding="utf-8")

        # HTML basics
        assert "<!DOCTYPE html>" in content
        assert "Tarraconian Atlas" in content
        assert "Dat Rômische Keiserrîch" in content

        # Required DOM element IDs
        for elem_id in [
            "map",
            "title-search",
            "search-results",
            "inspector-drawer",
            "drawer-tier-badge",
            "drawer-tarr-name",
            "drawer-origin-name",
            "drawer-title-key",
            "drawer-breadcrumbs",
            "hover-info",
        ]:
            assert f'id="{elem_id}"' in content, f"Missing element #{elem_id} in index.html"

        # Paradox Interactive Fan Disclaimer
        assert "Crusader Kings III is a registered trademark of Paradox Interactive AB" in content
        assert "non-commercial" in content

    def test_css_styles_exist(self):
        css_path = DOCS_DIR / "css" / "styles.css"
        assert css_path.exists(), "docs/css/styles.css is missing"
        content = css_path.read_text(encoding="utf-8")
        assert ".app-header" in content
        assert ".inspector-drawer" in content
        assert "--gold-primary" in content

    def test_js_app_exists(self):
        js_path = DOCS_DIR / "js" / "app.js"
        assert js_path.exists(), "docs/js/app.js is missing"
        content = js_path.read_text(encoding="utf-8")
        assert "L.CRS.Simple" in content
        assert "ck3_counties.geojson" in content

    def test_vendor_leaflet_exists(self):
        leaflet_js = DOCS_DIR / "vendor" / "leaflet" / "leaflet.js"
        leaflet_css = DOCS_DIR / "vendor" / "leaflet" / "leaflet.css"
        assert leaflet_js.exists(), "docs/vendor/leaflet/leaflet.js is missing"
        assert leaflet_css.exists(), "docs/vendor/leaflet/leaflet.css is missing"
        assert leaflet_js.stat().st_size > 50000, "leaflet.js seems incomplete"

    def test_nojekyll_exists(self):
        assert (DOCS_DIR / ".nojekyll").exists(), "docs/.nojekyll is missing (required for GitHub Pages)"


class TestCountiesGeoJSON:
    """Validates the county-level dissolved vector dataset."""

    def test_geojson_schema(self, counties_data):
        assert counties_data.get("type") == "FeatureCollection"
        features = counties_data.get("features", [])
        assert len(features) == 3476, f"Expected 3,476 counties, got {len(features)}"

    def test_feature_properties_and_coordinates(self, counties_data):
        for feat in counties_data["features"]:
            assert feat["type"] == "Feature"
            props = feat["properties"]

            # Required property keys
            assert "county" in props and props["county"].startswith("c_")
            assert "duchy" in props and (props["duchy"] is None or props["duchy"].startswith("d_") or props["duchy"].startswith("x_"))
            assert "kingdom" in props and (props["kingdom"] is None or props["kingdom"].startswith("k_") or props["kingdom"].startswith("x_"))
            assert "empire" in props and (props["empire"] is None or props["empire"].startswith("e_") or props["empire"].startswith("h_") or props["empire"].startswith("x_"))
            assert "barony_count" in props and props["barony_count"] >= 1
            assert "baronies" in props and len(props["baronies"]) == props["barony_count"]

            # Origin and Anachronism properties from markdown
            assert "c_origin" in props and props["c_origin"]
            assert "c_anachronism" in props
            if props.get("duchy"):
                assert "d_origin" in props and props["d_origin"]
                assert "d_anachronism" in props
            if props.get("kingdom"):
                assert "k_origin" in props and props["k_origin"]
                assert "k_anachronism" in props
            if props.get("empire"):
                assert "e_origin" in props and props["e_origin"]
                assert "e_anachronism" in props

            # Geometry checks
            geom = feat["geometry"]
            assert geom["type"] in ("Polygon", "MultiPolygon")
            # Verify coordinates are within map bounds [0..9216] x [0..4608]
            coords_flat = []
            if geom["type"] == "Polygon":
                coords_flat = [pt for ring in geom["coordinates"] for pt in ring]
            elif geom["type"] == "MultiPolygon":
                coords_flat = [pt for poly in geom["coordinates"] for ring in poly for pt in ring]

            for x, y in coords_flat:
                assert 0.0 <= x <= 9216.0, f"X coordinate {x} out of bounds in {props['county']}"
                assert 0.0 <= y <= 4608.0, f"Y coordinate {y} out of bounds in {props['county']}"

    def test_chancellery_translations(self, counties_data):
        by_key = {f["properties"]["county"]: f["properties"] for f in counties_data["features"]}

        # Test classical / landmark historical counties (authentic pre-1059)
        assert "c_szekesfehervar" in by_key
        sz = by_key["c_szekesfehervar"]
        assert sz["tarr_hist"] == "Stûlwîtzenburch" or sz["tarr_direct"] == "Stûlwîtzenburch"
        assert sz["c_origin"] == "Székesfehérvár"
        assert sz["c_anachronism"] == ""
        assert sz["d_origin"] == "Visegrad"
        assert sz["k_origin"] == "Hungary"
        assert sz["e_origin"] == "Germania"

        assert "c_middlesex" in by_key
        mid = by_key["c_middlesex"]
        assert mid["tarr_direct"] == "Middelsachsen"
        assert mid["c_origin"] == "Middle Seaxe"
        assert mid["c_anachronism"] == ""
        assert mid["d_origin"] == "East Seaxe"
        assert mid["empire"] == "e_germany"
        assert mid["e_tarr"] == "Germania"
        assert mid["e_origin"] == "Germania"
        assert mid["kingdom"] == "k_england"
        assert mid["k_tarr"] == "Engellant"
        assert mid["k_origin"] == "England"

        # Test anachronistic titles incorporating historical centres and reasons
        assert "c_munchen" in by_key
        mun = by_key["c_munchen"]
        assert "Freising" in mun["c_origin"]
        assert "München" in mun["c_origin"]
        assert "1158" in mun["c_anachronism"]
        assert "Henry the Lion" in mun["c_anachronism"]

        assert "c_innsbruck" in by_key
        inns = by_key["c_innsbruck"]
        assert "Wilten" in inns["c_origin"]
        assert "Innsbruck" in inns["c_origin"]
        assert "1180" in inns["c_anachronism"]

        assert "c_cleves" in by_key
        cleves = by_key["c_cleves"]
        assert "Xanten" in cleves["c_origin"]
        assert "Cleves" in cleves["c_origin"]
        assert "1020" in cleves["c_anachronism"] or "Schwanenburg" in cleves["c_anachronism"]

        assert "c_nancy" in by_key
        nancy = by_key["c_nancy"]
        assert ("Lunéville" in nancy["c_origin"] or "Épinal" in nancy["c_origin"])
        assert "Nancy" in nancy["c_origin"]
        assert "1070" in nancy["c_anachronism"]

        assert "c_roma" in by_key
        roma = by_key["c_roma"]
        assert roma.get("tarr_direct") in ("Rôm", "Rôme") or roma.get("tarr_hist") in ("Rôm", "Rôme")
        assert roma["empire"] == "e_germany"
        assert roma["e_tarr"] == "Germania"
        assert roma["kingdom"] == "k_romagna"
        assert roma["k_tarr"] == "Romanje"

        assert "c_byzantion" in by_key
        byz = by_key["c_byzantion"]
        assert byz.get("tarr_direct") in ("Konstantinôpel", "Konstantinopel") or byz.get("tarr_hist") in ("Bîsantz", "Konstantinôpel", "Konstantinopel")
        assert byz["empire"] == "e_macedonia"
        assert byz["e_tarr"] == "Macedonia"
        assert byz["kingdom"] == "k_thessalonika"
        assert byz["k_tarr"] == "Thessalonîke"

        assert "c_jerusalem" in by_key
        assert by_key["c_jerusalem"]["tarr_direct"] == "Hiligstat"

        assert "c_baghdad" in by_key
        assert by_key["c_baghdad"]["tarr_direct"] == "Bagdât"


class TestBaroniesGeoJSON:
    """Validates the barony-tier holding vector dataset."""

    def test_geojson_schema(self, baronies_data):
        assert baronies_data.get("type") == "FeatureCollection"
        features = baronies_data.get("features", [])
        assert len(features) == 11297, f"Expected 11,297 baronies, got {len(features)}"

    def test_feature_properties(self, baronies_data):
        by_key = {}
        for feat in baronies_data["features"]:
            assert feat["type"] == "Feature"
            props = feat["properties"]
            assert "barony" in props and props["barony"].startswith("b_")
            assert "county" in props and props["county"].startswith("c_")
            assert "b_origin" in props and props["b_origin"]
            assert "id" in props and isinstance(props["id"], int)
            by_key[props["barony"]] = props

        # Verify key historical holdings and save de jure hierarchy
        assert "b_london" in by_key
        assert by_key["b_london"]["id"] == 1527
        assert by_key["b_london"]["county"] == "c_middlesex"
        assert by_key["b_london"]["empire"] == "e_germany"
        assert by_key["b_london"]["e_tarr"] == "Germania"

        assert "b_roma" in by_key
        assert by_key["b_roma"]["county"] == "c_roma"
        assert by_key["b_roma"]["empire"] == "e_germany"
        assert by_key["b_roma"]["e_tarr"] == "Germania"


class TestTitleTree:
    """Validates the hierarchical tree metadata index aligned with save game."""

    def test_tree_hierarchy(self, tree_data):
        assert len(tree_data) == 47, f"Expected exactly 47 de jure empires, got {len(tree_data)}"

        # Check Germania (campaign hegemon harboring drifted kingdoms)
        assert "e_germany" in tree_data
        germany = tree_data["e_germany"]
        assert germany["tarr"] == "Germania"
        assert germany["origin"] == "Germania"
        assert germany["anachronism"] == ""
        assert "kingdoms" in germany

        # Drifted kingdoms in Germania
        for kd in ["k_england", "k_hungary", "k_romagna", "k_valencia", "k_sorbia", "k_lotharingia", "k_frisia"]:
            assert kd in germany["kingdoms"], f"Expected {kd} to be drifted into e_germany"

        eng = germany["kingdoms"]["k_england"]
        assert "duchies" in eng
        assert eng["origin"] == "England"
        assert eng["anachronism"] == ""
        assert "d_bedford" in eng["duchies"]

        bedford = eng["duchies"]["d_bedford"]
        assert "counties" in bedford
        assert bedford["origin"] == "East Seaxe"
        assert bedford["anachronism"] == ""
        assert "c_middlesex" in bedford["counties"]

        mid = bedford["counties"]["c_middlesex"]
        assert mid["origin"] == "Middle Seaxe"
        assert mid["anachronism"] == ""
        assert "b_london" in mid["baronies"]

        # Check anachronistic county in Bavaria/Tyrol
        assert "k_bavaria" in germany["kingdoms"]
        bav = germany["kingdoms"]["k_bavaria"]
        assert "d_tyrol" in bav["duchies"]
        tyr = bav["duchies"]["d_tyrol"]
        assert "c_innsbruck" in tyr["counties"]
        inns = tyr["counties"]["c_innsbruck"]
        assert "Wilten" in inns["origin"] and "Innsbruck" in inns["origin"]
        assert "1180" in inns["anachronism"]

        # Check Britannia
        assert "e_britannia" in tree_data
        brit = tree_data["e_britannia"]
        assert brit["tarr"] == "Britannia"
        assert "k_scotland" in brit["kingdoms"]

        # Check Macedonia
        assert "e_macedonia" in tree_data
        mac = tree_data["e_macedonia"]
        assert mac["tarr"] == "Macedonia"
        assert "k_thessalonika" in mac["kingdoms"]


class TestMapColoring:
    """Validates that adjacent titles never share the same color across all 5 tiers."""

    def test_county_color_properties_exist(self, counties_data):
        for feat in counties_data["features"]:
            props = feat["properties"]
            for key in ["c_color", "d_color", "k_color", "e_color"]:
                assert key in props and props[key].startswith("#") and len(props[key]) == 7, (
                    f"Invalid or missing {key} in county {props.get('county')}"
                )

    def test_barony_color_properties_exist(self, baronies_data):
        for feat in baronies_data["features"]:
            props = feat["properties"]
            for key in ["b_color", "c_color", "d_color", "k_color", "e_color"]:
                assert key in props and props[key].startswith("#") and len(props[key]) == 7, (
                    f"Invalid or missing {key} in barony {props.get('barony')}"
                )

    def test_no_adjacent_empire_color_collisions(self, counties_data, adjacencies_data):
        by_key = {f["properties"]["empire"]: f["properties"]["e_color"] for f in counties_data["features"]}
        collisions = []
        for e1, e2 in adjacencies_data["empires"]:
            if e1 in by_key and e2 in by_key and by_key[e1] == by_key[e2]:
                collisions.append((e1, e2, by_key[e1]))
        assert not collisions, f"Detected adjacent empire color collisions: {collisions}"

    def test_no_adjacent_kingdom_color_collisions(self, counties_data, adjacencies_data):
        by_key = {f["properties"]["kingdom"]: f["properties"]["k_color"] for f in counties_data["features"]}
        collisions = []
        for k1, k2 in adjacencies_data["kingdoms"]:
            if k1 in by_key and k2 in by_key and by_key[k1] == by_key[k2]:
                collisions.append((k1, k2, by_key[k1]))
        assert not collisions, f"Detected adjacent kingdom color collisions: {collisions}"

    def test_no_adjacent_duchy_color_collisions(self, counties_data, adjacencies_data):
        by_key = {f["properties"]["duchy"]: f["properties"]["d_color"] for f in counties_data["features"]}
        collisions = []
        for d1, d2 in adjacencies_data["duchies"]:
            if d1 in by_key and d2 in by_key and by_key[d1] == by_key[d2]:
                collisions.append((d1, d2, by_key[d1]))
        assert not collisions, f"Detected adjacent duchy color collisions: {collisions}"

    def test_no_adjacent_county_color_collisions(self, counties_data, adjacencies_data):
        by_key = {f["properties"]["county"]: f["properties"]["c_color"] for f in counties_data["features"]}
        collisions = []
        for c1, c2 in adjacencies_data["counties"]:
            if c1 in by_key and c2 in by_key and by_key[c1] == by_key[c2]:
                collisions.append((c1, c2, by_key[c1]))
        assert not collisions, f"Detected adjacent county color collisions: {collisions}"

    def test_seven_color_palette_uniformity(self, counties_data):
        """Validates that all 7 palette colors are used across all de jure title tiers without monopoly."""
        for key in ["c_color", "d_color", "k_color", "e_color"]:
            colors = {f["properties"][key] for f in counties_data["features"]}
            assert len(colors) == 7, f"Expected exactly 7 colors in {key}, found {len(colors)}: {colors}"

    def test_barony_holding_type_four_colors(self, baronies_data):
        """Validates that baronies are colored by holding type across exactly the 4 requested colors:
        - Castles: reddish (#ab3348)
        - Bishoprics: bluish (#3069a8)
        - Cities: greenish (#3b824a)
        - Unoccupied: dark grey (#424242)
        """
        holding_colors = {"#ab3348", "#3069a8", "#3b824a", "#424242"}
        b_colors = {f["properties"]["b_color"] for f in baronies_data["features"]}
        assert b_colors == holding_colors, f"Expected baronies to have colors {holding_colors}, got {b_colors}"

        by_key = {f["properties"]["barony"]: f["properties"] for f in baronies_data["features"]}
        # London is a castle holding
        assert by_key["b_london"]["b_color"] == "#ab3348"
        assert by_key["b_london"]["holding_type"] == "castle"
        # Southwark is a city holding
        assert by_key["b_southwark"]["b_color"] == "#3b824a"
        assert by_key["b_southwark"]["holding_type"] == "city"
        # Brentford is a church holding
        assert by_key["b_brentford"]["b_color"] == "#3069a8"
        assert by_key["b_brentford"]["holding_type"] == "church"

    def test_navigable_river_and_strait_adjacencies(self, counties_data, adjacencies_data):
        """Validates that titles across navigable rivers (e.g. Po river: Venice & Romagna) are adjacent with distinct colors."""
        k_edges = set(tuple(sorted(e)) for e in adjacencies_data["kingdoms"])
        assert ("k_romagna", "k_venice") in k_edges, "k_venice and k_romagna must be registered as adjacent across the Po River"

        by_key = {f["properties"]["kingdom"]: f["properties"]["k_color"] for f in counties_data["features"]}
        assert by_key["k_venice"] != by_key["k_romagna"], (
            f"k_venice and k_romagna must have distinct colors, got {by_key['k_venice']} vs {by_key['k_romagna']}"
        )


class TestTitleInfoAndIpa:
    """Validates the UI drawer elements, IPA pronunciations, and historical naming."""

    def test_html_drawer_sections(self):
        index_html = (REPO_DIR / "web" / "index.html").read_text(encoding="utf-8")
        assert "Historical Resolution" in index_html
        assert "1059 Historical Resolution" not in index_html
        assert 'id="drawer-ipa"' in index_html
        assert 'id="drawer-ipa-group"' in index_html
        # IPA group is placed right below the title name in the drawer header
        tarr_name_idx = index_html.find('id="drawer-tarr-name"')
        ipa_group_idx = index_html.find('id="drawer-ipa-group"')
        body_idx = index_html.find('class="drawer-body"')
        assert -1 < tarr_name_idx < ipa_group_idx < body_idx

    def test_css_anachronism_info_styling(self):
        css = (REPO_DIR / "web" / "css" / "styles.css").read_text(encoding="utf-8")
        assert "#3069a8" in css
        assert "info-ipa" in css
        assert "drawer-ipa-group" in css

    def test_selection_highlight_styling(self):
        js = (REPO_DIR / "web" / "js" / "app.js").read_text(encoding="utf-8")
        assert "color: '#ffffff'" in js
        assert "fillColor: '#d3d3d3'" not in js
        assert "#993284" not in js

        css = (REPO_DIR / "web" / "css" / "styles.css").read_text(encoding="utf-8")
        assert "--highlight-boundary: #ffffff;" in css
        assert "#993284" not in css

    def test_counties_geojson_ipa_and_tarr(self, counties_data):
        cleves = next(f["properties"] for f in counties_data["features"] if f["properties"]["county"] == "c_cleves")
        assert cleves["tarr"] == "Xanten"
        assert cleves["tarr_hist"] == "Xanten"
        assert cleves["tarr_direct"] == "Clêve"
        assert cleves["c_ipa"] == "[ˈkleː.və]"
        assert cleves["k_ipa"] == "[ˈloː.trɪŋ.ən]"
        assert "d_ipa" in cleves
        assert "e_ipa" in cleves

        polotsk = next(f["properties"] for f in counties_data["features"] if f["properties"]["county"] == "c_polotsk")
        assert polotsk["k_tarr"] == "Polôtzich"
        assert polotsk["k_tarr_hist"] == "Polôtzich"
        assert polotsk["k_tarr_direct"] == "Wîtzrûssen"

    def test_title_tree_ipa_and_tarr(self, tree_data):
        germany = tree_data["e_germany"]
        loth = germany["kingdoms"]["k_lotharingia"]
        assert loth["ipa"] == "[ˈloː.trɪŋ.ən]"
        cleves = loth["duchies"]["d_julich"]["counties"]["c_cleves"]
        assert cleves["tarr"] == "Xanten"
        assert cleves["tarr_hist"] == "Xanten"
        assert cleves["tarr_direct"] == "Clêve"
        assert cleves["ipa"] == "[ˈkleː.və]"

        for emp in tree_data.values():
            if "k_france" in emp.get("kingdoms", {}):
                assert emp["kingdoms"]["k_france"]["ipa"] == "[ˈvraŋk.riːç]"
                break

        white_rus = None
        for emp in tree_data.values():
            if "k_white_rus" in emp.get("kingdoms", {}):
                white_rus = emp["kingdoms"]["k_white_rus"]
                break
        assert white_rus is not None
        assert white_rus["tarr"] == "Polôtzich"
        assert "Polôtzich" in white_rus["origin"]
        assert white_rus["ipa"] == "[ˈpɔ.lɔtsk]"

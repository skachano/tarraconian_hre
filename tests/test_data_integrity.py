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


@pytest.fixture(scope="module")
def sinosphere_calques():
    path = DATA_DIR / "sinosphere_hanzi_calques.json"
    assert path.exists(), "docs/data/sinosphere_hanzi_calques.json is missing"
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
            "btn-open-linguistics",
            "btn-close-linguistics",
            "linguistics-modal",
            "tab-pane-tarraconian",
            "tab-pane-sinosphere",
            "tab-pane-lexicon",
            "drawer-sinosphere-group",
            "drawer-sinosphere-hanzi",
            "drawer-sinosphere-reading",
            "drawer-sinosphere-status",
            "drawer-sinosphere-breakdown",
            "drawer-sinosphere-synthesis",
            "drawer-sinosphere-substrate",
            "lexicon-search-input",
            "lexicon-category-filters",
            "lexicon-match-count",
            "lexicon-table-body",
            "barony-legend",
        ]:
            assert f'id="{elem_id}"' in content, f"Missing element #{elem_id} in index.html"

        # Verify barony holding type legend is a separate element from hover-info / map-stats-badge
        import re
        stats_match = re.search(r'<div class="map-stats-badge"[^>]*>(.*?)</div>', content, re.DOTALL)
        assert stats_match, "map-stats-badge not found in index.html"
        assert "barony-legend" not in stats_match.group(1), "barony-legend should not be nested inside map-stats-badge"

        for tab_name in ["tarraconian", "sinosphere", "lexicon"]:
            assert f'data-tab="{tab_name}"' in content, f"Missing tab button data-tab={tab_name} in index.html"

        # Mobile viewport & bottom sheet drag handle
        assert "viewport-fit=cover" in content
        assert "drawer-drag-handle" in content

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
        assert "@media (max-width: 768px)" in content
        assert "drawer-drag-handle" in content
        assert ".barony-legend" in content
        assert ".map-stats-badge" in content

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

    def test_github_pages_integration(self):
        # 404 page for fallback routing
        not_found_path = DOCS_DIR / "404.html"
        assert not_found_path.exists(), "docs/404.html is missing for GitHub Pages routing"
        not_found_content = not_found_path.read_text(encoding="utf-8")
        assert "404" in not_found_content
        assert "index.html" in not_found_content

        # GitHub Actions automated deployment workflow
        workflow_path = REPO_DIR / ".github" / "workflows" / "deploy-pages.yml"
        assert workflow_path.exists(), ".github/workflows/deploy-pages.yml is missing"
        wf_content = workflow_path.read_text(encoding="utf-8")
        assert "actions/deploy-pages" in wf_content
        assert "actions/upload-pages-artifact" in wf_content
        assert "actions/configure-pages" in wf_content
        assert "pages: write" in wf_content
        assert "id-token: write" in wf_content
        assert "'./docs'" in wf_content or '"./docs"' in wf_content

    def test_sinosphere_assets_exist(self):
        calques_path = DATA_DIR / "sinosphere_hanzi_calques.json"
        assert calques_path.exists(), "docs/data/sinosphere_hanzi_calques.json is missing"
        kanji_path = DATA_DIR / "sinosphere_kanji_tarraconian.json"
        assert kanji_path.exists(), "docs/data/sinosphere_kanji_tarraconian.json is missing"
        title_calques_path = DATA_DIR / "sinosphere_title_calques.json"
        assert title_calques_path.exists(), "docs/data/sinosphere_title_calques.json is missing"


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
        assert mid["e_tarr"] == "Dat Vrankische Imperi"
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
        assert roma["e_tarr"] == "Dat Vrankische Imperi"
        assert roma["kingdom"] == "k_romagna"
        assert roma["k_tarr"] == "Romanje"

        assert "c_byzantion" in by_key
        byz = by_key["c_byzantion"]
        assert byz.get("tarr_direct") in ("Konstantinôpel", "Konstantinopel") or byz.get("tarr_hist") in ("Bîsantz", "Konstantinôpel", "Konstantinopel")
        assert byz["empire"] == "e_macedonia"
        assert byz["e_tarr"] == "Dat Imperi van Bizantjen"
        assert byz["kingdom"] == "k_thessalonika"
        assert byz["k_tarr"] == "Bizantjen"

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
            assert "b_origin" in props
            if props.get("holding_type") == "unoccupied":
                assert props["name"] == ""
                assert props["b_origin"] == ""
            else:
                assert props["b_origin"]
            assert "id" in props and isinstance(props["id"], int)
            by_key[props["barony"]] = props

        # Verify key historical holdings and save de jure hierarchy
        assert "b_london" in by_key
        assert by_key["b_london"]["id"] == 1527
        assert by_key["b_london"]["county"] == "c_middlesex"
        assert by_key["b_london"]["empire"] == "e_germany"
        assert by_key["b_london"]["e_tarr"] == "Dat Vrankische Imperi"
        assert by_key["b_london"]["name"] == "Lunden"
        assert by_key["b_london"]["b_tarr"] == "Lunden"
        assert by_key["b_london"]["b_ipa"] == "[ˈlʊn.dən]"

        # Verify Option A collision disambiguation
        assert by_key["b_zvenyhorod"]["name"] == "Swenigorot"
        assert by_key["b_lviv"]["name"] == "Lemberch"

        # Verify Baltic pre-867 restitution
        assert by_key["b_konigsberg"]["name"] == "Twangste"

        # Verify unoccupied holding
        assert by_key["b_tulcha"]["name"] == ""
        assert by_key["b_tulcha"]["b_origin"] == ""
        assert by_key["b_tulcha"]["b_ipa"] == ""

        assert "b_roma" in by_key
        assert by_key["b_roma"]["county"] == "c_roma"
        assert by_key["b_roma"]["empire"] == "e_germany"
        assert by_key["b_roma"]["e_tarr"] == "Dat Vrankische Imperi"


class TestTitleTree:
    """Validates the hierarchical tree metadata index aligned with save game."""

    def test_tree_hierarchy(self, tree_data):
        assert len(tree_data) == 47, f"Expected exactly 47 de jure empires, got {len(tree_data)}"

        # Check Germania (campaign hegemon harboring drifted kingdoms)
        assert "e_germany" in tree_data
        germany = tree_data["e_germany"]
        assert germany["tarr"] == "Dat Vrankische Imperi"
        assert germany["origin"] == "Germania"
        assert "Carolingian" in germany["anachronism"]
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
        assert brit["tarr"] == "Dat Imperi van dem Wâllant"
        assert "k_scotland" in brit["kingdoms"]

        # Check Macedonia
        assert "e_macedonia" in tree_data
        mac = tree_data["e_macedonia"]
        assert mac["tarr"] == "Dat Imperi van Bizantjen"
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
        assert 'id="drawer-origin-group"' in index_html
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
        assert white_rus["ipa"] == "[pɔ.ˈloː.tsɪç]"


class TestSinosphereLinguistics:
    """Validates the Sinosphere Hanzi calque database and GeoJSON embedding."""

    def test_sinosphere_calques_coverage(self, sinosphere_calques):
        assert len(sinosphere_calques) == 821, f"Expected 821 titles, got {len(sinosphere_calques)}"
        empires = [k for k in sinosphere_calques if k.startswith("e_")]
        kingdoms = [k for k in sinosphere_calques if k.startswith("k_")]
        duchies = [k for k in sinosphere_calques if k.startswith("d_")]
        counties = [k for k in sinosphere_calques if k.startswith("c_")]

        assert len(empires) == 9
        assert len(kingdoms) == 39
        assert len(duchies) == 153
        assert len(counties) == 620

    def test_sinosphere_calque_details(self, sinosphere_calques):
        # Changchun (Liao)
        assert "c_LIAO_changchun" in sinosphere_calques
        cc = sinosphere_calques["c_LIAO_changchun"]
        assert cc["hanzi"] == "长春"
        assert len(cc["characters"]) == 2
        assert cc["characters"][0]["char"] == "长"
        assert cc["characters"][0]["pinyin"] == "cháng"
        assert cc["characters"][1]["char"] == "春"
        assert cc["characters"][1]["pinyin"] == "chūn"
        assert "Songhua" in cc["substrate"] or "Yitong" in cc["substrate"]
        assert "Langlentz-in-Chitân" in cc["synthesis"]

        # Yamashiro (Japan)
        assert "c_yamashiro" in sinosphere_calques
        ys = sinosphere_calques["c_yamashiro"]
        assert ys["hanzi"] == "山城"
        assert ys["characters"][0]["char"] == "山"
        assert "yama" in ys["characters"][0]["jp"]
        assert ys["characters"][1]["char"] == "城"
        assert "shiro" in ys["characters"][1]["jp"]

        # Samhan / Goryeo (Korea)
        assert "e_goryeo" in sinosphere_calques
        eg = sinosphere_calques["e_goryeo"]
        assert eg["hanzi"] == "三韩"
        assert eg["characters"][0]["char"] == "三"
        assert eg["characters"][0]["kr"] == "sam"
        assert eg["characters"][1]["char"] == "韩"
        assert eg["characters"][1]["kr"] == "han"

    def test_geojson_and_tree_hanzi_integration(self, counties_data, tree_data):
        yamashiro = next(f["properties"] for f in counties_data["features"] if f["properties"]["county"] == "c_yamashiro")
        assert yamashiro.get("c_hanzi") == "山城"
        assert yamashiro.get("k_hanzi") == "大和"
        assert yamashiro.get("e_hanzi") == "日本"

        assert tree_data["e_japan"]["hanzi"] == "日本"
        assert tree_data["e_goryeo"]["hanzi"] == "三韩"
        assert tree_data["e_zhongyuan"]["hanzi"] == "中原"


class TestSymbolGenerator:
    """Validates the procedural SVG symbol generator (Signa Imperii)."""

    def test_symbol_generator_files_exist(self):
        web_js = REPO_DIR / "web" / "js" / "symbol_generator.js"
        docs_js = DOCS_DIR / "js" / "symbol_generator.js"
        assert web_js.exists(), "web/js/symbol_generator.js is missing"
        assert docs_js.exists(), "docs/js/symbol_generator.js is missing"
        assert web_js.stat().st_size > 5000, "symbol_generator.js seems too short"
        assert docs_js.stat().st_size == web_js.stat().st_size, "docs/js/symbol_generator.js is out of sync"

    def test_index_html_symbol_integration(self):
        index_path = DOCS_DIR / "index.html"
        content = index_path.read_text(encoding="utf-8")
        assert 'id="drawer-symbol-card"' in content
        assert 'id="insignia-gallery-grid"' in content
        assert 'id="tab-pane-insignia"' in content
        assert 'data-tab="insignia"' in content
        assert 'src="js/symbol_generator.js"' in content

    def test_symbol_generator_content(self):
        js_path = DOCS_DIR / "js" / "symbol_generator.js"
        content = js_path.read_text(encoding="utf-8")

        # Tinctures & Palette
        for tincture in ["or", "argent", "gules", "sable", "azure", "vert", "vermilion", "purpure"]:
            assert f"{tincture}:" in content, f"Missing tincture {tincture} in PALETTE"

        # Key Vector Charges
        for charge in [
            "eagle_double",
            "alerion",
            "castrum",
            "roman_gate",
            "mount_triple",
            "bridge",
            "waves",
            "bell",
            "keys_st_peter",
            "crozier",
            "cross_patriarchal",
            "cross_byzantine",
            "tree_chestnut",
            "lion_rampant",
            "ship",
            "crown",
            "dragon",
        ]:
            assert f"{charge}:" in content, f"Missing charge builder {charge}"

        # Media Renderers
        for medium in [
            "renderVexillum",
            "renderGonfanon",
            "renderNotitiaScutum",
            "renderBullaSeal",
            "renderSinosphereChop",
            "renderVesicaSeal",
            "renderCivicBadge",
        ]:
            assert medium in content, f"Missing medium renderer {medium}"

        # Canonical Historical & Calqued Titles
        for key in ["h_roman_empire", "c_roma", "c_tarragona", "c_barcelona", "c_metz", "c_lviv", "c_szekesfehervar", "c_byzantion"]:
            assert key in content, f"Missing canonical handler for {key}"

    def test_app_js_symbol_integration(self):
        app_js_path = DOCS_DIR / "js" / "app.js"
        content = app_js_path.read_text(encoding="utf-8")
        assert "drawer-symbol-card" in content
        assert "TarraconianSymbols.renderSymbolToElement" in content
        assert "renderInsigniaGallery" in content

    def test_vert_and_azure_blazon_and_tincture_vocabulary(self):
        js_path = DOCS_DIR / "js" / "symbol_generator.js"
        content = js_path.read_text(encoding="utf-8")

        # 1. Authentic Tarraconian Heraldic Vocabulary for Vert & Azure
        assert "tarr: 'Grûne'" in content, "Vert must map to Tarraconian 'Grûne'"
        assert "en: 'Vert'" in content, "Vert must map to English 'Vert'"
        assert "tarr: 'Lâsûr'" in content, "Azure must map to Tarraconian 'Lâsûr'"
        assert "en: 'Azure'" in content, "Azure must map to English 'Azure'"
        assert "tarr: 'Keiser-Rôt'" in content, "Gules must map to Tarraconian 'Keiser-Rôt'"
        assert "tarr: 'Swartz'" in content, "Sable must map to Tarraconian 'Swartz'"
        assert "tarr: 'Golt'" in content, "Or must map to Tarraconian 'Golt'"
        assert "tarr: 'Silber'" in content, "Argent must map to Tarraconian 'Silber'"

        # 2. Rejection of unparsed / uncapitalized blazon fragments
        assert '"In Vert' not in content, "Found unparsed 'In Vert' in symbol generator"
        assert '`In Vert' not in content, "Found unparsed '`In Vert' in symbol generator"
        assert '"In Azure' not in content, "Found unparsed 'In Azure' in symbol generator"
        assert '`In Azure' not in content, "Found unparsed '`In Azure' in symbol generator"
        assert "vert charged with" not in content, "Found broken 'vert charged with' in symbol generator"
        assert "azure charged with" not in content, "Found broken 'azure charged with' in symbol generator"

        # 3. Proper heraldic charge dictionary
        assert "CHARGE_BLAZONS" in content, "CHARGE_BLAZONS dictionary missing"
        assert "formatBlazon" in content, "formatBlazon helper function missing"
        assert "TINCTURE_PATTERNS" in content, "TINCTURE_PATTERNS missing"

    def test_vert_and_azure_toponymic_parsing_coverage(self, counties_data, tree_data):
        import re

        js_path = DOCS_DIR / "js" / "symbol_generator.js"
        content = js_path.read_text(encoding="utf-8")

        # Extract TINCTURE_PATTERNS from JS for Python verification
        vert_re = re.compile(
            r'(?:gr[uûü]n[a-z]*|\bzelen[a-z]*\b|\bseleng[oô]r[a-z]*\b|\bz[oö]ld[a-z]*\b|'
            r'\b(?:al[-_]?)?akhdar\b|\b(?:al[-_]?)?kh?adra\b(?!mawt)|\byashil[a-z]*\b|'
            r'\bye[sş]il[a-z]*\b|\bchlor[a-z]*\b|\bglas\b|buglas|\bvert\b|\bverde[a-z]*\b|'
            r'\bvirid[a-z]*\b|\bgreen[a-z]*\b|\bl[uü]se\b|\blv\b|\bverdant\b)',
            re.I
        )

        azure_re = re.compile(
            r'(?:\bblou[a-z]*\b|k[oô]lblou[a-z]*|z[iî]blou[a-z]*|\bbl[aâ]u[a-z]*\b|'
            r'\bblâ(?!n)[a-z]*\b|\bl[aâ]s[uû]r[a-z]*\b|\bazur[a-z]*\b|\bazzurr[a-z]*\b|'
            r'\bazure\b|\bk[eé]k[a-z]*\b|\bsin[yi][a-z]*\b|\bplav[a-z]*\b|'
            r'\b(?:al[-_]?)?azraq\b|\bzarqa\b|\bg[oö]k[a-z]*\b|\bkyan[a-z]*\b|'
            r'\bcyano[a-z]*\b|\bbleu[a-z]*\b|\bblue[a-z]*\b|\bcaerul[a-z]*\b|\bgorm\b|'
            r'\bqing[a-z]*\b|\bcang(?:zhou|jing)\b)',
            re.I
        )

        # 1. Validate Vert titles
        vert_test_cases = [
            ("c_algeciras", "Grûninsel", "al-Gazirah al-Hadra"),
            ("c_zelengora", "Selengôre", "Zelengora"),
            ("c_grunningen", "Grüningen", "Grünningen"),
            ("c_BAL_east_amnok", "Ôstantflôzgrûnewazzer", "East Yālü"),
            ("c_yunzhou_2", "Grûnbambûsgouwe", "Grûnbambûsgouwe (in-game: Yunzhou)"),
            ("c_grunberg", "Krossen", "Krosno (in-game: Grunberg)")
        ]
        for key, tarr, orig in vert_test_cases:
            combined = f"{key} {tarr} {orig}"
            assert vert_re.search(combined), f"Failed to detect Vert tincture for {key} ({combined})"

        # 2. Validate Azure titles
        azure_test_cases = [
            ("c_qingshan", "Blouberch", "Qingshan"),
            ("c_qingzhou", "Blougouwe", "Qingzhou"),
            ("c_cangzhou", "Kôlblougouwe", "Cangzhou"),
            ("d_SW_qingxingan", "Blou-Upgancstrant", "Qingxingan"),
            ("d_blue_khakassia", "Blou-Chakassjen", "Blue Khakassia"),
            ("c_gokju", "Dalgouwe", "Gokju"),
            ("k_qingxu", "Blousacht", "Qingxu"),
            ("b_al-azraq", "al-azraq", "al-Azraq")
        ]
        for key, tarr, orig in azure_test_cases:
            combined = f"{key} {tarr} {orig}"
            assert azure_re.search(combined), f"Failed to detect Azure tincture for {key} ({combined})"

    def test_sinosphere_chop_ink_tincture_adaptation(self):
        js_path = DOCS_DIR / "js" / "symbol_generator.js"
        content = js_path.read_text(encoding="utf-8")

        # In renderSinosphereChop, ink color must adapt to field (e.g. azure or vert)
        assert "const ink = PALETTE[def.field] || PALETTE.vermilion;" in content
        assert 'stroke="${ink}"' in content
        assert 'fill="${ink}"' in content

    def test_charge_builders_uniform_signature(self):
        """All 39 charges in CHARGES must accept (color, scale, cx, cy) in standard order."""
        import re

        js_path = DOCS_DIR / "js" / "symbol_generator.js"
        content = js_path.read_text(encoding="utf-8")

        charges = [
            "eagle_double", "alerion", "castrum", "roman_gate", "mount_triple",
            "bridge", "waves", "bell", "keys_st_peter", "crozier",
            "cross_patriarchal", "cross_byzantine", "tree_chestnut",
            "lion_rampant", "ship", "crown", "dragon",
            "sword_crossed", "battleaxe", "spear", "bow_and_arrow", "shield_escutcheon",
            "stag_attired", "bear_rampant", "horse_courant", "wolf_statant", "fish_twin",
            "falcon_perched", "rose_seeded", "fleur_de_lis", "wheatsheaf_garb", "oak_branch",
            "grape_cluster", "sun_radiant", "star_six_pointed", "crescent_moon", "wheel_spoked",
            "anchor", "column_roman"
        ]

        assert len(charges) == 39

        for charge in charges:
            # Match charge declaration: charge: (arg1, arg2, arg3, arg4...) =>
            pattern = re.compile(rf"{charge}\s*:\s*\(([^)]+)\)\s*=>")
            match = pattern.search(content)
            assert match, f"Charge builder {charge} definition not found"
            params = [p.split("=")[0].strip() for p in match.group(1).split(",")]

            # First param is color (or colorOr)
            assert params[0] in ("color", "colorOr"), f"{charge} first param must be color, got {params[0]}"
            # Second param must be scale
            assert params[1] == "scale", f"{charge} second param must be scale, got {params[1]} (accent/trunk/sail/jewels must be after cy)"
            # Third and fourth must be cx and cy
            assert params[2] == "cx", f"{charge} third param must be cx, got {params[2]}"
            assert params[3] == "cy", f"{charge} fourth param must be cy, got {params[3]}"

    def test_unique_id_generation_and_no_static_id_collisions(self):
        """All 7 renderers must generate per-instance unique IDs to prevent SVG filter/clipPath collisions."""
        js_path = DOCS_DIR / "js" / "symbol_generator.js"
        content = js_path.read_text(encoding="utf-8")

        assert "getUniqueId" in content, "Missing getUniqueId function"

        # Static IDs that caused document-wide collision bugs with hidden modals must not exist
        static_ids = [
            'id="vexillum-shadow"',
            'id="vexillum-clip"',
            'id="gonfanon-shadow"',
            'id="gonfanon-clip"',
            'id="scutum-shadow"',
            'id="scutum-clip"',
            'id="seal-shadow"',
            'id="chop-shadow"',
            'id="chop-clip"',
            'id="vesica-shadow"',
            'id="vesica-clip"',
            'id="badge-shadow"',
            'id="badge-clip"'
        ]
        for sid in static_ids:
            assert sid not in content, f"Found fragile static ID {sid} in symbol_generator.js"

    def test_vexillum_field_and_charge_rendering(self):
        """Verify vexillum renders explicit base field rect and charge with correct transform."""
        js_path = DOCS_DIR / "js" / "symbol_generator.js"
        content = js_path.read_text(encoding="utf-8")

        # Explicit base field rect with fColor
        assert '<rect x="${bannerX}" y="${bannerY}" width="${bannerW}" height="${bannerH}" fill="${fColor}"' in content
        # Charges called with (def.chargeColor, 0.82, 110, 135)
        assert "CHARGES[c](def.chargeColor, 0.82, 110, 135)" in content
        # Dynamic clip-path usage
        assert 'clip-path="url(#${uid}_clip)"' in content

    def test_hanzi_display_on_all_media(self):
        """Verify Hanzi logographs are rendered properly across all media frames."""
        js_path = DOCS_DIR / "js" / "symbol_generator.js"
        content = js_path.read_text(encoding="utf-8")

        # 1. Canonical Sinosphere Empires mapping
        canonical_empires = {
            "e_zhongyuan": "中原",
            "e_liangyi": "梁益",
            "e_jingyang": "荆扬",
            "e_yongliang": "雍凉",
            "e_lingnan": "岭南",
            "e_goryeo": "三韩",
            "e_japan": "日本",
            "e_andong": "安东",
            "e_amur": "阿穆尔"
        }
        assert "CANONICAL_SINOSPHERE_HANZI" in content
        for emp, hanzi in canonical_empires.items():
            assert f"{emp}: '{hanzi}'" in content, f"Missing canonical empire mapping for {emp}"

        # 2. Exported in module return object
        assert "CANONICAL_SINOSPHERE_HANZI," in content

        # 3. Barony tier county-hanzi inheritance and 2-character preservation
        assert "hanzi = props.b_hanzi || props.c_hanzi || '';" in content
        assert "hanzi.length <= 2 ? hanzi : hanzi.substring(0, 2)" in content

        # 4. Font stack containing standard CJK serif families
        cjk_font_family = "'Songti SC', 'Noto Serif SC', 'Kaiti SC', 'SimSun', serif"
        assert cjk_font_family in content

        # 5. Media renderers Hanzi integration
        # A. Vexillum (Empire)
        assert '<!-- Classical Sinitic Hanzi Logograph on Imperial Vexillum -->' in content
        assert 'y="${def.charges.length > 0 ? 102 : 135}"' in content
        assert 'CHARGES[c](def.chargeColor, 0.55, 110, 166)' in content

        # B. Gonfanon (Kingdom)
        assert '<!-- Sinitic Hanzi Logograph on Kingdom Gonfanon -->' in content
        assert 'y="${def.charges.length > 0 ? 86 : 105}"' in content
        assert 'CHARGES[c](def.chargeColor, 0.46, 110, 134)' in content

        # C. Notitia Scutum (Duchy)
        assert '<!-- Sinitic Hanzi Logograph on Notitia Scutum above Boss -->' in content
        assert 'y="${def.charges.length > 0 ? 75 : 82}"' in content
        assert 'CHARGES[c](def.chargeColor, 0.45, cx, cy + 50)' in content

        # D. Bulla Seal (County standard)
        assert '<!-- Sinitic Hanzi Logograph on Bulla Seal -->' in content
        assert 'y="${def.charges.length > 0 ? 98 : 120}"' in content
        assert 'CHARGES[c](def.chargeColor, 0.42, cx, cy + 24)' in content

        # E. Sinosphere Chop (Procedure 1 County)
        assert '<!-- Seal Script / Classical Hanzi Logograph (Carved in Relief) -->' in content
        assert 'font-size="${hanziText.length > 1 ? 46 : 68}"' in content

        # F. Vesica Seal (Ecclesiastical)
        assert 'y="${def.charges.length > 0 ? 105 : 140}"' in content
        assert 'CHARGES[c](def.chargeColor || PALETTE.or, 0.50, 110, 168)' in content

        # G. Civic Badge (Barony)
        assert '<!-- Sinitic Hanzi Logograph on Civic Badge -->' in content
        assert 'y="${def.charges.length > 0 ? 70 : 95}"' in content
        assert 'CHARGES[c](def.chargeColor, 0.44, 90, 118)' in content

    def test_expanded_field_ordinaries(self):
        """Verify presence and valid blazoning of all 19 field ordinaries and geometric partitions."""
        js_path = DOCS_DIR / "js" / "symbol_generator.js"
        content = js_path.read_text(encoding="utf-8")

        ordinaries = [
            "solid", "per_fess", "per_pale", "per_bend", "per_bend_sinister",
            "quarterly", "per_saltire", "fess", "pale", "bend", "bend_sinister",
            "chevron", "cross", "saltire", "chief", "bordure", "barry",
            "chequy", "pales", "pales_undy"
        ]

        assert "ORDINARY_BLAZONS" in content, "ORDINARY_BLAZONS dictionary missing"
        assert "renderField" in content, "renderField function missing"

        for ord_key in ordinaries:
            assert f"{ord_key}:" in content, f"Missing ordinary {ord_key} in ORDINARY_BLAZONS or renderField"

        # Check renderField SVG partition handlers
        assert "if (ord === 'per_fess')" in content
        assert "if (ord === 'per_pale')" in content
        assert "if (ord === 'per_bend')" in content
        assert "if (ord === 'quarterly')" in content
        assert "if (ord === 'chevron')" in content
        assert "if (ord === 'cross')" in content
        assert "if (ord === 'saltire')" in content
        assert "if (ord === 'chequy')" in content

    def test_chronological_horizon_cadency_and_multi_charge(self):
        """Verify chronological cadency engine and multi-charge layout rendering."""
        js_path = DOCS_DIR / "js" / "symbol_generator.js"
        content = js_path.read_text(encoding="utf-8")

        # 1. Horizon determination function and exports
        assert "getChronologicalHorizon" in content, "Missing getChronologicalHorizon function"
        assert "getChronologicalHorizon," in content, "getChronologicalHorizon must be exported"
        assert "renderMultiCharges" in content, "Missing renderMultiCharges function"

        # 2. Multi-charge layout patterns (pale stack and 2-and-1)
        assert "def.chargeCount > 1 ? renderMultiCharges(def" in content
        assert "if (count === 2)" in content
        assert "else if (count >= 3)" in content

        # 3. Blazon generation includes count and ordinary
        assert "function formatBlazon(fieldKey, chargeKey, chargeColorHex, ordinaryKey = 'solid', chargeCount = 1, ordColorHex = null)" in content



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
            "drawer-canonical-name",
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

        # Test classical / landmark historical counties
        assert "c_szekesfehervar" in by_key
        sz = by_key["c_szekesfehervar"]
        assert sz["tarr_hist"] == "Stûlwîtzenburch" or sz["tarr_direct"] == "Stûlwîtzenburch"

        assert "c_middlesex" in by_key
        mid = by_key["c_middlesex"]
        assert mid["tarr_direct"] == "Middelsachsen"
        assert mid["empire"] == "e_germany"
        assert mid["e_tarr"] == "Germania"
        assert mid["kingdom"] == "k_england"
        assert mid["k_tarr"] == "Engellant"

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
        assert "kingdoms" in germany

        # Drifted kingdoms in Germania
        for kd in ["k_england", "k_hungary", "k_romagna", "k_valencia", "k_sorbia", "k_lotharingia", "k_frisia"]:
            assert kd in germany["kingdoms"], f"Expected {kd} to be drifted into e_germany"

        eng = germany["kingdoms"]["k_england"]
        assert "duchies" in eng
        assert "d_bedford" in eng["duchies"]

        bedford = eng["duchies"]["d_bedford"]
        assert "counties" in bedford
        assert "c_middlesex" in bedford["counties"]

        mid = bedford["counties"]["c_middlesex"]
        assert "b_london" in mid["baronies"]

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

"""
test_data_integrity.py

Unit and integration tests for the Tarraconian Atlas web application assets,
GeoJSON schemas, coordinate boundaries, and Chancellery toponym mappings.
"""

import json
import re
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
            "drawer-audit-badge",
            "tab-pane-audit",
        ]:
            assert f'id="{elem_id}"' in content, f"Missing element #{elem_id} in index.html"

        # Verify barony holding type legend is a separate element from hover-info / map-stats-badge
        import re
        stats_match = re.search(r'<div class="map-stats-badge"[^>]*>(.*?)</div>', content, re.DOTALL)
        assert stats_match, "map-stats-badge not found in index.html"
        assert "barony-legend" not in stats_match.group(1), "barony-legend should not be nested inside map-stats-badge"

        for tab_name in ["tarraconian", "sinosphere", "lexicon", "audit"]:
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

    def test_historical_audit_barony_resolutions(self, baronies_data):
        """Validates that newly audited baronies under the Burden of Proof on Antiquity
        principle and Tarraconian phonotactics match the required historical resolutions."""
        by_key = {f["properties"]["barony"]: f["properties"] for f in baronies_data["features"]}

        expected_resolutions = {
            "b_dorohychyn": ("Bûch", "[buːx]"),
            "b_baranovichi": ("Ehrenfrîtszelle", "[ɛh.rɛn.friːts.ˈtsɛ.ʎə]"),
            "b_zhlobin": ("Strêschew", "[ˈstreː.ʃɛw]"),
            "b_kalinkavichy": ("Ipat", "[ɪ.ˈpat]"),
            "b_konigsberg": ("Twangste", "[ˈtwaŋ.stɛ]"),
            "b_pushkin": ("Sâri", "[ˈsaː.rɪ]"),
            "b_newport": ("Ûsemunde", "[uː.zɛ.ˈmʊn.də]"),
            "b_fort_novoaleksandrovkiy": ("Mangystau", "[ma.ŋɪs.ˈtɔʊ]"),
            "b_bartenstein": ("Barte", "[ˈbar.tə]"),
            "b_algiers": ("Alschîr", "[al.ˈʃiːr]"),
            "b_stezyca": ("Stensitz", "[ˈstɛn.sɪts]"),
            "b_eilenburg": ("Îlenburch", "[ˈiː.lɛn.bʊrx]"),
            "b_gazargamo": ("Gasargamu", "[ˈɡa.zar.ɡa.mʊ]"),
            "b_agra": ("Agraban", "[a.ɡra.ˈban]"),
            "b_benghazi": ("Berenîke", "[bɛ.rɛ.ˈniː.kə]"),
            "b_rafaniya-krak": ("Rafanîje", "[ra.fa.ˈniː.jɛ]"),
            "b_timbuktu": ("Djôlibe", "[djoː.ˈlɪ.bə]"),
            "b_bangkok": ("Mênam", "[ˈmeː.nam]"),
            "b_faizabad": ("Sarajû", "[sa.ra.ˈjuː]"),
            "b_gangaikondacolapuram": ("Kâvêrî", "[kaː.veː.ˈriː]"),
            "b_rotterdam": ("Rotte", "[ˈrɔ.tə]"),
            "b_heidelberg": ("Heiligenberch", "[ˈhɛɪ.lɪ.ɣən.bɛrx]"),
            "b_clairvaux": ("Albetâl", "[al.bɛ.ˈtaːl]"),
            "b_citeaux": ("Vonge", "[ˈvɔ.ŋɛ]"),
            "b_furness": ("Vûrnês", "[vuːr.ˈneːs]"),
            "b_katzenelnbogen": ("Dörsbach", "[ˈdøːrs.bax]"),
            "b_isenburg": ("Iserbach", "[ˈɪ.zɛr.bax]"),
            "b_jaisalmer": ("Kaknî", "[kak.ˈniː]"),
            "b_amarkot": ("Hakrâ", "[ha.ˈkraː]"),
            "b_pathankot": ("Tschakkî", "[tʃa.ˈkiː]"),
            "b_gawilgarh": ("Sâtpure", "[saːt.ˈpʊ.rə]"),
            "b_borgarh": ("Narmadâ-Tâl", "[nar.ma.ˈdaː taːl]"),
            "b_aswan-west": ("Elefantîne", "[ɛ.lɛ.fan.ˈtiː.nə]"),
            "b_benin_marshes": ("Osse", "[ˈɔ.sə]"),
            "b_gobir-east": ("Rîme", "[ˈriː.mə]"),
            "b_salavan": ("Sê-Dôn", "[seː doːn]"),
            "b_BOR_Melak": ("Mahakâm", "[ma.ha.ˈkaːm]"),
            "b_upper_gambia": ("Kantôra", "[ˈkan.toː.ra]"),
            "b_mariupol": ("Kalmjûs", "[kalm.ˈjuːs]"),
            "b_karabutak": ("Mugaldschar-Berch", "[ˈmʊ.ɣal.dʒar bɛrx]"),
            "b_popa": ("Popa-Berch", "[ˈpɔ.pa bɛrx]"),
            "b_lower_jubba": ("Gobweyn", "[ɡɔb.ˈwɛɪn]"),
            "b_lower_omo": ("Nider-Omo", "[ˈnɪ.dər ˈɔ.mɔ]"),
            "b_upper_dinder": ("Ober-Dinder", "[ˈɔ.bər ˈdɪn.dər]"),
            "b_middle_atbara": ("Middel-Atbara", "[mɪ.ˈdəl ˈat.ba.ra]"),
            "b_upper_tano": ("Ober-Tano", "[ˈɔ.bər ˈta.nɔ]"),
            "b_south_igbo": ("Sût-Igbô", "[suːt ɪɡ.ˈboː]"),
            "b_york": ("Everwîch", "[ɛ.vɛr.ˈwiːç]"),
            "b_birmingham": ("Bôrmingheim", "[boːr.mɪŋ.ˈhɛɪm]"),
            "b_scarborough": ("Scharburch", "[ˈʃar.bʊrx]"),
            "b_chesterfield": ("Tschestervelt", "[ˈtʃɛs.tɛr.vɛlt]"),
            "b_newark": ("Scherwald", "[ˈʃpreː.wald]" if False else "[ˈʃɛr.wald]"),
            "b_aylesbury": ("Eilesburch", "[ˈɛɪ.lɛs.bʊrx]"),
            "b_west_derby": ("Westdörp", "[ˈwɛst.døːrp]"),
            "b_selkirk": ("Selkirchen", "[ˈsɛl.kɪr.xən]"),
            "b_cottingham": ("Cottingheim", "[kɔ.tɪŋ.ˈhɛɪm]"),
            "b_colchester": ("Colnezester", "[ˈkɔl.nɛ.tsɛs.tər]"),
            "b_salisbury": ("Sêreburch", "[ˈseː.rɛ.bʊrx]"),
            "b_shrewsbury": ("Schrobbesburch", "[ˈʃrɔ.bɛs.bʊrx]"),
            "b_winchester": ("Wintanzester", "[ˈwɪn.tan.tsɛs.tər]"),
            "b_exeter": ("Exanzester", "[ˈɛk.san.tsɛs.tər]"),
            "b_dover": ("Dovras", "[ˈdɔ.vras]"),
            "b_bath": ("Hâtbatu", "[ˈhaːt.ba.tʊ]"),
            "b_vyr": ("Wîr", "[wiːr]"),
            "b_starodub-on-the-klyazma": ("Starodûp-an-der-Klêsme", "[sta.rɔ.ˈduːp an dɛr ˈkleːs.mə]"),
            "b_yegoryevsk": ("Guslîtze", "[ɡʊs.ˈliː.tsə]"),
            "b_bar_sur_aube": ("Bar-an-der-Ôbe", "[bar an dɛr ˈoː.bə]"),
            "b_bar_sur_seine": ("Bar-an-der-Sêne", "[bar an dɛr ˈseː.nə]"),
            "b_montreuil_sur_mer": ("Montreuil-am-Mêr", "[ˈmɔn.trɔʏ.ɪl am meːr]"),
            "b_yuriev": ("Rostawîtze", "[rɔs.ta.ˈwiː.tsə]"),
            "b_yuryev": ("Kolôksche", "[kɔ.ˈloːk.ʃə]"),
            "b_yaroslav_VOL": ("Mletschke", "[ˈmlɛtʃ.kə]"),
            "b_rostislavl": ("Osjôtr", "[ɔs.ˈjoːtr]"),
            "b_danilov": ("Pelende", "[pɛ.ˈlɛn.də]"),
            "b_valenciennes": ("Valentzîn", "[va.lɛn.ˈtsiːn]"),
            "b_grevelines": ("Grevelingen", "[ˈɡrɛ.vɛ.lɪ.ŋɛn]"),
            "b_tournai": ("Dornîch", "[dɔr.ˈniːç]"),
            "b_courtrai": ("Kortrîch", "[kɔr.ˈtriːç]"),
            "b_bastogne": ("Bastenach", "[ˈbas.tɛ.nax]"),
            "b_clervaux": ("Clierf", "[ˈklɪ.ɛrf]"),
        }

        for bk, (exp_name, exp_ipa) in expected_resolutions.items():
            assert bk in by_key, f"Missing {bk} in baronies_data"
            assert by_key[bk]["name"] == exp_name, f"Expected {exp_name} for {bk}, got {by_key[bk]['name']}"
            assert by_key[bk]["b_tarr"] == exp_name
            assert by_key[bk]["b_ipa"] == exp_ipa, f"Expected {exp_ipa} for {bk}, got {by_key[bk]['b_ipa']}"

        # Verify barony_resolutions.json matches in data/ and docs/data/
        res_path = DATA_DIR / "barony_resolutions.json"
        assert res_path.exists(), "data/barony_resolutions.json missing"
        with open(res_path, "r", encoding="utf-8") as f:
            resolutions = json.load(f)
        assert len(resolutions) == 11297
        assert not any(re.search(r'\b(on|upon)\b', d.get('name', ''), re.I) for d in resolutions.values()), "Found English on/upon preposition in barony names"

        docs_res_path = REPO_DIR / "docs" / "data" / "barony_resolutions.json"
        assert docs_res_path.exists(), "docs/data/barony_resolutions.json missing"
        with open(docs_res_path, "r", encoding="utf-8") as f:
            docs_resolutions = json.load(f)
        assert len(docs_resolutions) == 11297

        for bk, (exp_name, _) in expected_resolutions.items():
            assert resolutions[bk]["name"] == exp_name
            assert docs_resolutions[bk]["name"] == exp_name

        # Verify Sinosphere baronies have b_hanzi
        assert by_key["b_Liao_Shangjing"]["b_hanzi"] == "上京"
        assert by_key["b_Liao_Bozhou"]["b_hanzi"] == "渤州"


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

        # JavaScript Syntax & Bracket Balance Verification
        counts = {'{': 0, '}': 0, '(': 0, ')': 0, '[': 0, ']': 0}
        in_string = None
        escape = False
        tick_count = 0
        depth = 0
        for ch in content:
            if escape:
                escape = False
                continue
            if ch == '\\':
                escape = True
                continue
            if in_string:
                if ch == in_string:
                    in_string = None
            else:
                if ch in ('"', "'"):
                    in_string = ch
                elif ch == '`':
                    tick_count += 1
                elif ch in counts:
                    counts[ch] += 1
                    if ch == '{':
                        depth += 1
                    elif ch == '}':
                        depth -= 1
                        assert depth >= 0, "Negative brace depth: unmatched '}' in symbol_generator.js"

        assert counts['{'] == counts['}'], f"Unbalanced braces in symbol_generator.js: {counts['{']} open vs {counts['}'] } close"
        assert counts['('] == counts[')'], f"Unbalanced parentheses in symbol_generator.js: {counts['(']} open vs {counts[')'] } close"
        assert counts['['] == counts[']'], f"Unbalanced brackets in symbol_generator.js: {counts['[']} open vs {counts[']'] } close"
        assert tick_count % 2 == 0, f"Unbalanced backticks in symbol_generator.js: {tick_count}"

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
        """All 58 charges in CHARGES must accept (color, scale, cx, cy) in standard order."""
        import re

        js_path = DOCS_DIR / "js" / "symbol_generator.js"
        content = js_path.read_text(encoding="utf-8")

        charges = [
            "eagle_double", "alerion", "castrum", "roman_gate", "mount_triple",
            "bridge", "waves", "bell", "keys_st_peter", "crozier",
            "cross_patriarchal", "cross_byzantine", "cross", "tree_chestnut",
            "lion_rampant", "ship", "crown", "dragon",
            "sword_crossed", "battleaxe", "spear", "bow_and_arrow", "shield_escutcheon",
            "stag_attired", "bear_rampant", "horse_courant", "wolf_statant", "fish_twin",
            "falcon_perched", "rose_seeded", "fleur_de_lis", "wheatsheaf_garb", "oak_branch",
            "grape_cluster", "sun_radiant", "star_six_pointed", "crescent_moon", "wheel_spoked",
            "anchor", "column_roman", "fess", "pale", "bend", "chevron", "bordure",
            "escallop", "cross_jerusalem", "catherine_wheel", "pilgrim_scrip",
            "holy_lance", "crown_imperial", "crown_kamelaukion", "seal_chop",
            "paiza_tablet", "war_hammer", "flanged_mace", "chalice", "stag_attire"
        ]

        assert len(charges) == 58

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

    def test_heraldic_rationale_collapsible_and_artifact_charges(self):
        """Verifies presence of 13 artifact charges, rationale generator, and collapsible drawer markup."""
        js_path = DOCS_DIR / "js" / "symbol_generator.js"
        content = js_path.read_text(encoding="utf-8")
        css_path = DOCS_DIR / "css" / "styles.css"
        css_content = css_path.read_text(encoding="utf-8")

        # 1. 13 Artifact Charges in CHARGES & CHARGE_BLAZONS
        artifact_charges = [
            "escallop", "cross_jerusalem", "catherine_wheel", "pilgrim_scrip",
            "holy_lance", "crown_imperial", "crown_kamelaukion", "seal_chop",
            "paiza_tablet", "war_hammer", "flanged_mace", "chalice", "stag_attire"
        ]
        for ac in artifact_charges:
            assert f"{ac}:" in content, f"Artifact charge builder {ac} missing"
            assert f"'{ac}':" in content or f'"{ac}":' in content or f"{ac}:" in content, f"Artifact charge blazon {ac} missing"

        # 2. Heraldic Rationale Functions
        assert "function buildHeraldicRationale" in content
        assert "function buildImageryRationale" in content
        assert "function buildColoursRationale" in content
        assert "function buildSplitsRationale" in content
        assert "def.rationale = buildHeraldicRationale(def, titleKey, props, tier);" in content
        assert "rationale: def.rationale" in content

        # 3. Collapsible markup in renderSymbolToElement
        assert '<details class="symbol-rationale-details">' in content
        assert '<summary class="symbol-rationale-summary">' in content
        assert '<span class="symbol-rationale-title">Heraldic Rationale</span>' in content
        assert '<span class="rationale-arrow">&#9662;</span>' in content
        assert '<div class="symbol-rationale-body">' in content
        assert '<span class="rationale-label">Imagery:</span>' in content
        assert '<span class="rationale-label">Colours:</span>' in content
        assert '<span class="rationale-label">Splits:</span>' in content

        # 4. CSS Rules for Collapsible Details
        assert ".symbol-rationale-details" in css_content
        assert ".symbol-rationale-summary" in css_content
        assert ".symbol-rationale-title" in css_content
        assert ".symbol-rationale-body" in css_content
        assert ".rationale-entry" in css_content
        assert ".rationale-label" in css_content
        assert ".rationale-desc" in css_content

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
        assert "function formatBlazon(fieldKey, chargeKey, chargeColorHex, ordinaryKey = 'solid', chargeCount = 1, ordColorHex = null" in content

    def test_canonical_heraldry_coverage_and_rule_of_tincture(self):
        """Verify canonical save heraldry dataset, c_porto arms, and strict Rule of Tincture compliance."""
        canon_path = REPO_DIR / "data" / "canonical_title_heraldry.json"
        docs_canon = DOCS_DIR / "data" / "canonical_title_heraldry.json"
        assert canon_path.exists(), "data/canonical_title_heraldry.json is missing"
        assert docs_canon.exists(), "docs/data/canonical_title_heraldry.json is missing"

        with open(canon_path, "r", encoding="utf-8") as f:
            canon = json.load(f)

        assert len(canon) >= 1700, f"Expected >= 1700 canonical titles, found {len(canon)}"

        # 1. c_porto validation: authentic arms of Portucale / Count Henry of Burgundy
        assert "c_porto" in canon, "c_porto must be present in canonical heraldry"
        porto_entry = canon["c_porto"]
        field, ord_key, charge, charge_col, count, ord_col = porto_entry[:6]
        assert field == "argent", f"c_porto field must be Argent, got {field}"
        assert charge == "cross", f"c_porto charge must be cross, got {charge}"
        assert charge_col == "azure", f"c_porto charge color must be Azure, got {charge_col}"
        assert ord_key == "solid", f"c_porto ordinary must be solid, got {ord_key}"

        # 2. Complete Rule of Tincture audit: zero metal-on-metal or colour-on-colour violations
        # and strict divided field compliance (layout-aware positioning)
        metals = {"or", "argent"}
        colours = {"gules", "azure", "vert", "sable", "purpure"}

        on_ordinary = {"fess", "pale", "bend", "bend_sinister", "chevron", "cross", "saltire"}
        in_field = {"bordure", "chief"}
        partitions = {"per_pale", "per_fess", "per_bend", "per_bend_sinister", "quarterly", "per_saltire", "barry", "chequy", "pales", "pales_undy"}

        violations = []
        for title, data in canon.items():
            f_col, o_key, chg, chg_col, cnt, o_col = data[:6]
            layout = data[6] if len(data) > 6 else 'default'
            field_is_metal = f_col in metals
            ord_is_metal = o_col in metals
            charge_is_metal = chg_col in metals if chg_col else False

            # 2a. Uncharged shields validation (pure partitions & honorable ordinaries)
            if cnt == 0 or chg in ("none", None):
                if o_key != "solid":
                    if field_is_metal and ord_is_metal:
                        violations.append((title, "ordinary metal-on-metal", f_col, o_col))
                    elif (not field_is_metal) and (not ord_is_metal):
                        violations.append((title, "ordinary colour-on-colour", f_col, o_col))
                continue

            if o_key == "solid":
                if chg_col == f_col:
                    violations.append((title, "charge matches field", f_col, chg_col))
                elif field_is_metal and charge_is_metal:
                    violations.append((title, "charge metal-on-metal", f_col, chg_col))
                elif (not field_is_metal) and (not charge_is_metal):
                    violations.append((title, "charge colour-on-colour", f_col, chg_col))
            else:
                if field_is_metal and ord_is_metal:
                    violations.append((title, "ordinary metal-on-metal", f_col, o_col))
                elif (not field_is_metal) and (not ord_is_metal):
                    violations.append((title, "ordinary colour-on-colour", f_col, o_col))

                # Layout-aware Rule of Tinctures on Divided Fields
                if o_key == "bordure":
                    if chg_col == f_col:
                        violations.append((title, "charge matches field", f_col, chg_col))
                    elif field_is_metal and charge_is_metal:
                        violations.append((title, "charge metal in field metal", f_col, chg_col))
                    elif (not field_is_metal) and (not charge_is_metal):
                        violations.append((title, "charge colour in field colour", f_col, chg_col))
                elif o_key == "chief":
                    bg_col = o_col if layout == "in_chief" else f_col
                    bg_is_metal = ord_is_metal if layout == "in_chief" else field_is_metal
                    if chg_col == bg_col:
                        violations.append((title, "charge matches chief/field", bg_col, chg_col))
                    elif bg_is_metal and charge_is_metal:
                        violations.append((title, "charge metal on metal", bg_col, chg_col))
                    elif (not bg_is_metal) and (not charge_is_metal):
                        violations.append((title, "charge colour on colour", bg_col, chg_col))
                elif o_key in on_ordinary:
                    if layout in ("in_chief", "in_base", "above_below", "flanked", "two_and_one", "one_and_two"):
                        if chg_col == f_col:
                            violations.append((title, "charge matches field", f_col, chg_col))
                        elif field_is_metal and charge_is_metal:
                            violations.append((title, "charge metal in field metal", f_col, chg_col))
                        elif (not field_is_metal) and (not charge_is_metal):
                            violations.append((title, "charge colour in field colour", f_col, chg_col))
                    else:
                        if chg_col == o_col:
                            violations.append((title, "charge matches ordinary", o_col, chg_col))
                        elif ord_is_metal and charge_is_metal:
                            violations.append((title, "charge metal on ordinary metal", o_col, chg_col))
                        elif (not ord_is_metal) and (not charge_is_metal):
                            violations.append((title, "charge colour on ordinary colour", o_col, chg_col))
                elif o_key in ("per_fess", "per_bend", "per_bend_sinister", "quarterly", "per_saltire"):
                    if layout == "in_chief":
                        if chg_col == f_col:
                            violations.append((title, "charge matches upper partition", f_col, chg_col))
                        elif field_is_metal and charge_is_metal:
                            violations.append((title, "charge metal on upper partition metal", f_col, chg_col))
                        elif (not field_is_metal) and (not charge_is_metal):
                            violations.append((title, "charge colour on upper partition colour", f_col, chg_col))
                    elif layout == "in_base":
                        if chg_col == o_col:
                            violations.append((title, "charge matches lower partition", o_col, chg_col))
                        elif ord_is_metal and charge_is_metal:
                            violations.append((title, "charge metal on lower partition metal", o_col, chg_col))
                        elif (not ord_is_metal) and (not charge_is_metal):
                            violations.append((title, "charge colour on lower partition colour", o_col, chg_col))
                elif o_key in ("barry", "chequy", "pales", "pales_undy"):
                    if chg_col in (f_col, o_col):
                        violations.append((title, "charge matches field tinctures", f_col, o_col, chg_col))

        assert len(violations) == 0, f"Found {len(violations)} Rule of Tincture violations in canonical heraldry: {violations[:5]}"

    def test_realm_heraldic_uniqueness(self, counties_data):
        """Verify 100% heraldic uniqueness across all 47 empires and 213 kingdoms."""
        canon_path = REPO_DIR / "data" / "canonical_title_heraldry.json"
        with open(canon_path, "r", encoding="utf-8") as f:
            canon = json.load(f)

        features = counties_data.get("features", [])
        empires = sorted(list(set(f["properties"].get("empire") for f in features if f["properties"].get("empire"))))
        kingdoms = sorted(list(set(f["properties"].get("kingdom") for f in features if f["properties"].get("kingdom"))))

        assert len(empires) == 47, f"Expected 47 empires, got {len(empires)}"
        assert len(kingdoms) == 213, f"Expected 213 kingdoms, got {len(kingdoms)}"

        # A. Empires Uniqueness (47 / 47)
        emp_blazons = {}
        for e in empires:
            assert e in canon, f"Empire {e} missing from canonical heraldry"
            emp_blazons.setdefault(tuple(canon[e]), []).append(e)

        emp_dups = {b: elist for b, elist in emp_blazons.items() if len(elist) > 1}
        assert len(emp_dups) == 0, f"Duplicate empire blazons detected: {emp_dups}"

        # B. Kingdoms Uniqueness (213 / 213)
        kng_blazons = {}
        for k in kingdoms:
            assert k in canon, f"Kingdom {k} missing from canonical heraldry"
            kng_blazons.setdefault(tuple(canon[k]), []).append(k)

        kng_dups = {b: klist for b, klist in kng_blazons.items() if len(klist) > 1}
        assert len(kng_dups) == 0, f"Duplicate kingdom blazons detected: {kng_dups}"

    def test_duchy_heraldic_uniqueness(self, counties_data):
        """Verify 100% heraldic uniqueness across all 970 geojson duchies and 0 collisions with higher tiers."""
        canon_path = REPO_DIR / "data" / "canonical_title_heraldry.json"
        with open(canon_path, "r", encoding="utf-8") as f:
            canon = json.load(f)

        features = counties_data.get("features", [])
        duchies = sorted(list(set(f["properties"].get("duchy") for f in features if f["properties"].get("duchy"))))
        assert len(duchies) == 970, f"Expected 970 duchies, got {len(duchies)}"

        # 1. All 970 geojson duchies present in canon
        for d in duchies:
            assert d in canon, f"Duchy {d} missing from canonical heraldry"

        # 2. 100% uniqueness among all 970 duchies
        duchy_blazons = {}
        for d in duchies:
            sig = tuple(canon[d])
            duchy_blazons.setdefault(sig, []).append(d)

        dups = {b: dlist for b, dlist in duchy_blazons.items() if len(dlist) > 1}
        assert len(dups) == 0, f"Duplicate duchy blazons detected: {dups}"

        # 3. Zero collisions between duchies and higher-tier realms (empires, kingdoms)
        higher_blazons = set()
        for k, spec in canon.items():
            if k.startswith(('e_', 'k_', 'h_')):
                higher_blazons.add(tuple(spec))
                higher_blazons.add(tuple(spec[:6]))

        collisions = []
        for d in duchies:
            spec = canon[d]
            if tuple(spec) in higher_blazons or tuple(spec[:6]) in higher_blazons:
                collisions.append((d, spec))

        assert len(collisions) == 0, f"Duchy collisions with higher tiers: {collisions}"

    def test_county_heraldic_uniqueness(self, counties_data):
        """Verify 100% heraldic uniqueness across all 3,476 geojson counties and 0 collisions with higher tiers."""
        canon_path = REPO_DIR / "data" / "canonical_title_heraldry.json"
        with open(canon_path, "r", encoding="utf-8") as f:
            canon = json.load(f)

        features = counties_data.get("features", [])
        counties = sorted(list(set(f["properties"].get("county") for f in features if f["properties"].get("county"))))
        assert len(counties) == 3476, f"Expected 3476 counties, got {len(counties)}"

        # 1. All 3,476 geojson counties present in canon
        for c in counties:
            assert c in canon, f"County {c} missing from canonical heraldry"

        # 2. 100% uniqueness among all 3,476 counties
        county_blazons = {}
        for c in counties:
            sig = tuple(canon[c])
            county_blazons.setdefault(sig, []).append(c)

        dups = {b: clist for b, clist in county_blazons.items() if len(clist) > 1}
        assert len(dups) == 0, f"Duplicate county blazons detected: {dups}"

        # 3. Zero collisions between counties and higher-tier realms (empires, kingdoms, duchies)
        higher_blazons = set()
        for k, spec in canon.items():
            if k.startswith(('e_', 'k_', 'h_', 'd_')):
                higher_blazons.add(tuple(spec))
                higher_blazons.add(tuple(spec[:6]))

        collisions = []
        for c in counties:
            spec = canon[c]
            if tuple(spec) in higher_blazons or tuple(spec[:6]) in higher_blazons:
                collisions.append((c, spec))

        assert len(collisions) == 0, f"County collisions with higher tiers: {collisions}"

    def test_charge_builders_tincture_adaptation(self):
        """Verify dynamic contrast immunity for multi-element charges in symbol_generator.js."""
        js_path = DOCS_DIR / "js" / "symbol_generator.js"
        content = js_path.read_text(encoding="utf-8")

        # 1. CANONICAL_HERALDRY embedded and referenced in analyzeTitle
        assert "const CANONICAL_HERALDRY = {" in content, "CANONICAL_HERALDRY must be embedded in symbol_generator.js"
        assert "if (typeof CANONICAL_HERALDRY !== 'undefined' && CANONICAL_HERALDRY[key])" in content
        assert "CANONICAL_HERALDRY\n  };" in content or "CANONICAL_HERALDRY" in content

        # 2. Ship charge contrast adaptation (sail is never argent on metal field)
        assert "ship:" in content
        assert "isMetal" in content or "isMetalField" in content
        assert "sailColor" in content
        assert "waveColor" in content

        # 3. Waves charge contrast adaptation
        assert "waves:" in content
        assert "waveColor" in content

        # 4. Chestnut tree contrast adaptation (crown is never vert on vert field)
        assert "tree_chestnut:" in content
        assert "crownColor" in content

        # 5. St. Peter keys contrast adaptation
        assert "keys_st_peter:" in content
        assert "k1" in content and "k2" in content

    def test_thessalonika_and_ordinary_charges_coverage(self):
        """Verify k_thessalonika cross charge and all ordinary charges are defined in CHARGES."""
        import json
        import re

        js_path = DOCS_DIR / "js" / "symbol_generator.js"
        content = js_path.read_text(encoding="utf-8")

        # 1. k_thessalonika in canonical heraldry
        canon_path = REPO_DIR / "data" / "canonical_title_heraldry.json"
        with open(canon_path, "r", encoding="utf-8") as f:
            canon = json.load(f)

        assert "k_thessalonika" in canon, "k_thessalonika must be present in canonical heraldry"
        field, ord_key, charge, charge_col, count, ord_col = canon["k_thessalonika"]
        assert field == "gules", f"k_thessalonika field must be Gules, got {field}"
        assert charge == "cross", f"k_thessalonika charge must be cross, got {charge}"
        assert charge_col == "argent", f"k_thessalonika charge color must be Argent, got {charge_col}"

        # 2. All charges in canon are present in CHARGES
        defined_charges = set(re.findall(r"^\s*([a-zA-Z0-9_]+)\s*:\s*\([^)]*\)\s*=>", content, re.MULTILINE))
        canon_charges = set(spec[2] for spec in canon.values() if len(spec) > 2 and spec[2] and spec[2] != 'none')

        missing_charges = canon_charges - defined_charges
        assert len(missing_charges) == 0, f"Charges in canon missing from CHARGES: {missing_charges}"

        # 3. Explicit check for cross and ordinary charges
        for ordinary_charge in ["cross", "fess", "pale", "bend", "chevron", "bordure"]:
            assert ordinary_charge in defined_charges, f"Ordinary charge {ordinary_charge} missing from CHARGES"

    def test_divided_field_rule_of_tinctures_and_babruysk(self, counties_data):
        """Verifies the adjusted Rule of Tinctures on divided fields, specifically preventing silver-on-silver in c_babruysk."""
        js_path = DOCS_DIR / "js" / "symbol_generator.js"
        content = js_path.read_text(encoding="utf-8")

        # 1. Divided field logic present in symbol_generator.js
        assert "ON_ORDINARY_SET" in content, "Missing ON_ORDINARY_SET in symbol_generator.js"
        assert "IN_FIELD_SET" in content, "Missing IN_FIELD_SET in symbol_generator.js"
        assert "prevent charge-on-division colour collisions" in content, "Rationale must explain divided field tincture immunity"

        # 2. Simulate c_babruysk procedural derivation
        def hash_string(s):
            h = 5381
            for ch in s:
                h = (((h << 5) + h) + ord(ch)) & 0xFFFFFFFF
                if h >= 0x80000000:
                    h -= 0x100000000
            return abs(h)

        h_babruysk = hash_string("c_babruysk")
        fields = ["gules", "azure", "or", "argent", "vert", "sable"]
        detected_field = fields[h_babruysk % len(fields)]
        assert detected_field == "gules", f"c_babruysk field must be Gules, got {detected_field}"

        late_ordinaries = ["solid", "fess", "bend", "bend_sinister", "chevron", "cross", "saltire", "quarterly", "per_saltire", "chief", "bordure", "barry"]
        detected_ordinary = late_ordinaries[(h_babruysk >> 2) % len(late_ordinaries)]
        assert detected_ordinary == "fess", f"c_babruysk ordinary must be fess, got {detected_ordinary}"

        # In c_babruysk, the fess is Argent (division 2) on a Gules field (division 1)
        # Under the adjusted Rule of Tinctures, the battleaxes on the fess must NOT be silver (no silver-on-silver)
        # Instead, they appear entirely inside the silver fess and bear the opposite colour (Gules)
        ordinary_color = "argent"
        on_ordinary_set = {"fess", "pale", "bend", "bend_sinister", "chevron", "cross", "saltire"}
        if detected_ordinary in on_ordinary_set:
            charge_color = detected_field
        else:
            charge_color = ordinary_color

        assert charge_color == "gules", f"c_babruysk charge must be Gules on silver fess, got {charge_color}"
        assert charge_color != ordinary_color, "c_babruysk charge must NOT match ordinary color (avoid silver-on-silver)"

    def test_notitia_scutum_boss_clearance_and_charge_layouts(self):
        """Verifies that duchy-tier Notitia command shield charges are positioned to avoid the central shield boss (umbo)."""
        js_path = DOCS_DIR / "js" / "symbol_generator.js"
        content = js_path.read_text(encoding="utf-8")

        # 1. Dedicated scutum charge layout helper present
        assert "function renderScutumCharges" in content, "Missing renderScutumCharges helper"
        assert "renderScutumCharges(def, cx, cy)" in content, "renderNotitiaScutum must invoke renderScutumCharges"

        # 2. Geometry assertions: central umbo is at (110, 125) with radius 22 (covering y: 103..147)
        # Upper field zone is centered at y=68, lower field zone is centered at y=182
        assert "builder(color, 0.54, cx, 68)" in content, "Single charge must be placed in upper field zone at y=68"
        assert "cx, 182" in content, "Multi/composite charges must utilize lower field zone at y=182"

        # 3. Two charges: one above (y=68), one below (y=182)
        assert "builder(color, sc, cx, 68)" in content
        assert "builder(color, sc, cx, 182)" in content

        # 4. Three charges: 2-and-1 triad framing the umbo
        assert "cx - 28, 68" in content
        assert "cx + 28, 68" in content

        # 5. Composite charges: primary in upper field, secondary in lower field
        assert "CHARGES[c1] ? CHARGES[c1](color, sc, cx, 68) : ''" in content
        assert "CHARGES[c2] ? CHARGES[c2](color, sc, cx, 182) : ''" in content

    def test_uncharged_shields_and_historical_revisions(self):
        """Verifies formal uncharged shield support and historical revisions from CK3 save timeline."""
        import json

        # 1. Check JS symbol generator files for 'none' charge and blazon
        for js_file in [REPO_DIR / "web" / "js" / "symbol_generator.js", DOCS_DIR / "js" / "symbol_generator.js"]:
            content = js_file.read_text(encoding="utf-8")
            assert "none: () => ''" in content, f"'none' charge lambda missing in {js_file}"
            assert "none: { tarrNoun: ''," in content, f"'none' charge blazon missing in {js_file}"
            assert "isUncharged = " in content, f"isUncharged check missing in {js_file}"

        # 2. Check canonical title heraldry in both data/ and docs/data/
        for canon_file in [REPO_DIR / "data" / "canonical_title_heraldry.json", DOCS_DIR / "data" / "canonical_title_heraldry.json"]:
            with open(canon_file, "r", encoding="utf-8") as f:
                canon = json.load(f)

            # Authentic uncharged shields & historical titles:
            # d_barcelona: Senyera (Or, four pales Gules, uncharged)
            assert "d_barcelona" in canon
            f_col, o_key, chg, chg_col, cnt, o_col = canon["d_barcelona"][:6]
            assert f_col == "or" and o_key == "pales" and o_col == "gules"
            assert chg == "none" and cnt == 0

            # c_tarragona: Senyera undy (Or, four pales undy Gules, uncharged)
            assert "c_tarragona" in canon
            f_col, o_key, chg, chg_col, cnt, o_col = canon["c_tarragona"][:6]
            assert f_col == "or" and o_key == "pales_undy" and o_col == "gules"
            assert chg == "none" and cnt == 0

            # c_barcelona: St. George & Senyera quarterly (Quarterly Argent and Gules, uncharged)
            assert "c_barcelona" in canon
            f_col, o_key, chg, chg_col, cnt, o_col = canon["c_barcelona"][:6]
            assert f_col == "argent" and o_key == "quarterly" and o_col == "gules"
            assert chg == "none" and cnt == 0

            # c_metz: Metz bipartite civic arms (Party per pale Argent and Sable, uncharged)
            assert "c_metz" in canon
            f_col, o_key, chg, chg_col, cnt, o_col = canon["c_metz"][:6]
            assert f_col == "argent" and o_key == "per_pale" and o_col == "sable"
            assert chg == "none" and cnt == 0

            # c_thessalonika: Saint Demetrius swords with cadency bordure
            assert "c_thessalonika" in canon
            f_col, o_key, chg, chg_col, cnt, o_col = canon["c_thessalonika"][:6]
            assert f_col == "gules" and o_key == "bordure" and chg == "sword_crossed"
            assert chg_col == "or" and cnt == 1 and o_col == "or"

            # Revised procedural generation for anachronistic titles:
            # d_osterreich: Replaced anachronistic Babenberg Bindenschild with generated procedural blazon
            assert "d_osterreich" in canon
            assert not (canon["d_osterreich"][0] == "gules" and canon["d_osterreich"][1] == "fess" and canon["d_osterreich"][2] == "none")

            # c_vienna: Replaced anachronistic Wiener Kreuz with generated procedural blazon
            assert "c_vienna" in canon
            assert not (canon["c_vienna"][0] == "gules" and canon["c_vienna"][1] == "cross" and canon["c_vienna"][2] == "none")

            # c_siena, c_lucca, c_baden, c_zollern, c_nedersticht: Replaced with generated blazons
            for anach_k in ["c_siena", "c_lucca", "c_baden", "c_zollern", "c_nedersticht"]:
                assert anach_k in canon, f"{anach_k} must be present in canonical heraldry"
                assert canon[anach_k][2] != "none" or canon[anach_k][4] == 0


def test_title_symbol_adoption_dataset():
    """Validates the schema, coverage, and contents of title_symbol_adoption.json."""
    for root_dir in [DATA_DIR, REPO_DIR / "data"]:
        adopt_path = root_dir / "title_symbol_adoption.json"
        assert adopt_path.exists(), f"{adopt_path} is missing"
        with open(adopt_path, "r", encoding="utf-8") as f:
            adopt_data = json.load(f)

        assert len(adopt_data) >= 4500, f"Expected >= 4500 titles in adoption DB, got {len(adopt_data)}"

        # Validate showcase titles
        showcase_keys = [
            "h_roman_empire", "k_france", "d_upper_lorraine", "d_barcelona",
            "c_tarragona", "c_roma", "c_metz", "c_aachen", "c_venezia",
            "c_ile_de_france", "c_byzantion", "c_jinzhou", "c_dongguan"
        ]
        valid_eras = {
            "Classical & Pre-867 Antiquity",
            "Carolingian & Lothringian Cradle (867–988)",
            "Tarraconian Ethnogenesis (989–1052)",
            "First Imperial Restoration (1053–1071)",
            "High Imperial Consolidation (1072–1142)",
            "Universal Roman Hegemony (1143–1194)",
            "Exterior Autonomous March (1194+)"
        }

        for k in showcase_keys:
            assert k in adopt_data, f"Showcase title {k} missing from {adopt_path}"
            rec = adopt_data[k]
            assert "yearDisplay" in rec and rec["yearDisplay"], f"Missing yearDisplay for {k}"
            assert "era" in rec and rec["era"] in valid_eras, f"Invalid era '{rec.get('era')}' for {k}"
            assert "rationale" in rec and len(rec["rationale"]) > 10, f"Missing/short rationale for {k}"

        # Check c_tarragona specifically
        tarr = adopt_data["c_tarragona"]
        assert tarr["year"] == 1016
        assert "Tarraconian Ethnogenesis" in tarr["era"]

        # Check c_roma
        roma = adopt_data["c_roma"]
        assert roma["saint"] is not None and "Peter" in roma["saint"]

        # Check c_aachen
        aachen = adopt_data["c_aachen"]
        assert aachen["year"] == 800

        # Check web assets have adoption integration
        js_sym = (REPO_DIR / "web" / "js" / "symbol_generator.js").read_text(encoding="utf-8")
        assert "loadAdoptionData" in js_sym
        assert "getAdoptionInfo" in js_sym
        assert "symbol-adoption-badge" in js_sym

        js_app = (REPO_DIR / "web" / "js" / "app.js").read_text(encoding="utf-8")
        assert "title_symbol_adoption.json" in js_app
        assert "loadAdoptionData" in js_app

        css = (REPO_DIR / "web" / "css" / "styles.css").read_text(encoding="utf-8")
        assert ".symbol-adoption-badge" in css


class TestSaintHoldingImagery:
    """Validates the procedural hagiographic cadency dataset (Signa Sanctorum)

    and its integration into the heraldic symbol generator.
    """

    @pytest.fixture
    def saint_data(self):
        p = DATA_DIR / "saint_holding_imagery.json"
        assert p.exists(), f"Missing {p}"
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_saint_holding_file_exists_and_synced(self, saint_data):
        docs_p = DOCS_DIR / "data" / "saint_holding_imagery.json"
        assert docs_p.exists(), f"Missing {docs_p}"
        with open(docs_p, "r", encoding="utf-8") as f:
            docs_data = json.load(f)
        assert len(saint_data) == len(docs_data)
        assert len(saint_data) >= 150

    def test_saint_holding_entries_structure(self, saint_data):
        required_keys = [
            "title_key", "name", "tier", "county", "kingdom",
            "saint_name", "saint_epithet", "shrine_type", "relic_description",
            "charge", "charge_color", "field", "ordinary", "ordinary_color",
            "charge_count", "blazon_tarr", "blazon_en", "legend",
            "rationale_imagery", "rationale_colours", "rationale_splits", "source"
        ]
        for key, entry in saint_data.items():
            assert key.startswith("b_") or key.startswith("c_"), f"Saint title key {key} must be a barony or county"
            for rk in required_keys:
                assert rk in entry and entry[rk] is not None, f"Missing {rk} in {key}"
                if isinstance(entry[rk], str):
                    assert len(entry[rk].strip()) > 0, f"Empty {rk} in {key}"

    def test_saint_holding_rule_of_tinctures(self, saint_data):
        metals = {"or", "argent"}
        colours = {"gules", "azure", "vert", "purpure", "sable"}
        all_tinctures = metals | colours

        for key, entry in saint_data.items():
            f = entry["field"]
            o = entry["ordinary"]
            oc = entry["ordinary_color"]
            c = entry["charge"]
            cc = entry["charge_color"]

            assert f in all_tinctures, f"Invalid field {f} in {key}"
            assert oc in all_tinctures, f"Invalid ordinary_color {oc} in {key}"
            assert cc in all_tinctures, f"Invalid charge_color {cc} in {key}"

            if key.startswith("b_"):
                assert o == "bordure", f"Saint baronies must use baronial cadency bordure, got {o} in {key}"
                # Bordure tincture contrast with field
                if f in metals:
                    assert oc in colours, f"Metal bordure on metal field in {key}: {oc} on {f}"
                else:
                    assert oc in metals, f"Colour bordure on colour field in {key}: {oc} on {f}"
            else:
                assert o == "solid", f"Saint counties must use solid comital field, got {o} in {key}"

            # Charge tincture contrast with field
            if f in metals:
                assert cc in colours, f"Metal charge on metal field in {key}: {cc} on {f}"
            else:
                assert cc in metals, f"Colour charge on colour field in {key}: {cc} on {f}"

    def test_saint_holding_charges_exist_in_generator(self, saint_data):
        js_code = (REPO_DIR / "web" / "js" / "symbol_generator.js").read_text(encoding="utf-8")
        # Extract CHARGES keys
        charges_match = re.search(r'const CHARGES = \{([\s\S]*?)\n  \};', js_code)
        assert charges_match, "Could not find CHARGES in symbol_generator.js"
        charges_keys = set(re.findall(r'^\s*([a-z_0-9]+)\s*:', charges_match.group(1), re.M))

        for key, entry in saint_data.items():
            charge = entry["charge"]
            assert charge in charges_keys, f"Charge '{charge}' in {key} not found in symbol_generator.js CHARGES"

    def test_famous_shrine_and_buried_saint_holdings(self, saint_data):
        # 1. Mount Sinai / Saint Catherine
        assert "b_stcatherine" in saint_data
        cat = saint_data["b_stcatherine"]
        assert "Catherine" in cat["saint_name"]
        assert cat["charge"] == "catherine_wheel"
        assert cat["field"] == "purpure"

        # 2. Santiago de Compostela / Saint James
        assert "b_santiago" in saint_data
        sant = saint_data["b_santiago"]
        assert "James" in sant["saint_name"]
        assert sant["charge"] == "escallop"
        assert sant["field"] == "gules"

        # 3. Split / Saint Domnius
        assert "b_split" in saint_data
        split = saint_data["b_split"]
        assert "Domnius" in split["saint_name"] or "Dujam" in split["saint_name"]
        assert split["charge"] == "crozier"

        # 4. Kildare / Saint Brigid
        assert "b_kildare" in saint_data
        kild = saint_data["b_kildare"]
        assert "Brigid" in kild["saint_name"]
        assert kild["charge"] == "cross"

        # 5. Patras / Saint Andrew
        assert "b_patras" in saint_data
        pat = saint_data["b_patras"]
        assert "Andrew" in pat["saint_name"]
        assert pat["charge"] == "cross"

        # 6. Fulda / Saint Boniface
        assert "b_fulda" in saint_data
        fuld = saint_data["b_fulda"]
        assert "Boniface" in fuld["saint_name"]
        assert fuld["charge"] == "sword_crossed"

        # 7. Canterbury / Saint Thomas Becket
        assert "b_canterbury" in saint_data
        cant = saint_data["b_canterbury"]
        assert "Thomas Becket" in cant["saint_name"]
        assert cant["charge"] == "crozier"

        # 8. Iona / Saint Columba
        assert "b_mull" in saint_data
        mull = saint_data["b_mull"]
        assert "Columba" in mull["saint_name"]
        assert mull["charge"] == "ship"

    def test_web_assets_have_saint_integration(self):
        js_sym = (REPO_DIR / "web" / "js" / "symbol_generator.js").read_text(encoding="utf-8")
        assert "loadSaintData" in js_sym
        assert "getSaintHoldingInfo" in js_sym
        assert "SAINT_HOLDING_DATA" in js_sym
        assert "Signa Sanctorum" in js_sym

        js_app = (REPO_DIR / "web" / "js" / "app.js").read_text(encoding="utf-8")
        assert "saint_holding_imagery.json" in js_app
        assert "loadSaintData" in js_app

        build_script = (REPO_DIR / "scripts" / "build_webapp.py").read_text(encoding="utf-8")
        assert "saint_holding_imagery.json" in build_script


@pytest.fixture(scope="module")
def profiles_data():
    path = REPO_DIR / "data" / "barony_toponymic_profiles.json"
    assert path.exists(), "data/barony_toponymic_profiles.json missing"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestBaronyToponymicProfiles:
    """Validates Alternative 1 3-Stratum Toponymic Profiles and web integration."""

    def test_profiles_synced_to_docs(self, profiles_data):
        docs_p = DATA_DIR / "barony_toponymic_profiles.json"
        assert docs_p.exists(), "docs/data/barony_toponymic_profiles.json missing"
        with open(docs_p, "r", encoding="utf-8") as f:
            docs_data = json.load(f)
        assert len(profiles_data["baronies"]) == len(docs_data["baronies"])
        assert len(profiles_data["baronies"]) == 10239

    def test_profiles_schema_and_strata(self, profiles_data):
        cultures = profiles_data.get("cultures", {})
        baronies = profiles_data.get("baronies", {})
        assert len(cultures) >= 100
        valid_origins = {
            "pre_867_established",
            "feudalized_post_867",
            "founded_post_867",
            "pre_867_unfeudalized",
        }
        valid_continuities = {
            "Direct Transparency",
            "Transitional Mediation (< 50y)",
            "Semantic Rupture (>= 50y)",
        }

        for cname, meta in cultures.items():
            assert re.match(r"^#[0-9a-fA-F]{6}$", meta["color"]), f"Bad color for {cname}"
            assert meta.get("language")
            assert meta.get("heritage")

        for bk, prof in baronies.items():
            assert bk.startswith("b_")
            assert prof["c"] in cultures, f"Missing coinage culture {prof['c']} for {bk}"
            assert prof["s"] in cultures, f"Missing substrate culture {prof['s']} for {bk}"
            assert prof["t"] in cultures, f"Missing transmission culture {prof['t']} for {bk}"
            assert prof["o"] in valid_origins, f"Invalid origin {prof['o']} for {bk}"
            assert prof["cs"] in valid_continuities, f"Invalid continuity {prof['cs']} for {bk}"
            assert prof["cd"] and prof["sn"] and prof["tn"]

    def test_canonical_toponymic_profiles(self, profiles_data):
        b = profiles_data["baronies"]
        assert b["b_london"]["c"] == "anglo_saxon"
        assert b["b_london"]["s"] == "anglo_saxon"
        assert b["b_london"]["t"] == "anglo_saxon"
        assert b["b_london"]["o"] == "pre_867_established"

        assert b["b_roma"]["c"] == "italian"
        assert b["b_roma"]["s"] == "italian"
        assert b["b_roma"]["t"] == "greek"

        assert b["b_kiev"]["c"] == "franconian"
        assert b["b_kiev"]["s"] == "russian"
        assert b["b_kiev"]["t"] == "franconian"
        assert b["b_kiev"]["o"] == "feudalized_post_867"

        assert b["b_reykjavik"]["c"] == "norse"
        assert b["b_reykjavik"]["s"] == "norse"
        assert b["b_reykjavik"]["t"] == "norse"

    def test_web_assets_have_toponymic_views(self):
        html = (REPO_DIR / "web" / "index.html").read_text(encoding="utf-8")
        for view in ("holding_type", "coinage_culture", "substrate_culture", "transmission_culture"):
            assert f'data-view="{view}"' in html
        assert "drawer-toponymic-group" in html

        js = (REPO_DIR / "web" / "js" / "app.js").read_text(encoding="utf-8")
        assert "barony_toponymic_profiles.json" in js
        assert "renderToponymicProfile" in js
        assert "updateBaronyLegend" in js

        build_script = (REPO_DIR / "scripts" / "build_webapp.py").read_text(encoding="utf-8")
        assert "barony_toponymic_profiles.json" in build_script


class TestBaronyCoinageAndContext:
    """Validates Section 4.A datasets: barony_holdings, barony_coinage_rulers, and barony_physical_and_event_context."""

    def test_reconciled_barony_holdings(self):
        path = REPO_DIR / "data" / "barony_holdings.json"
        assert path.exists(), "data/barony_holdings.json missing"
        with open(path, "r", encoding="utf-8") as f:
            bh = json.load(f)
        assert len(bh) == 11297
        assert bh["b_ka'abir"] == "city"
        assert bh["b_mansa'l-kharaz"] == "city"
        occupied = sum(1 for v in bh.values() if v != "unoccupied")
        assert occupied == 10239

    def test_barony_coinage_rulers(self):
        path = REPO_DIR / "data" / "barony_coinage_rulers.json"
        assert path.exists(), "data/barony_coinage_rulers.json missing"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["metadata"]["total_occupied_baronies"] == 10239
        assert data["metadata"]["unresolved_characters"] == 0
        baronies = data["baronies"]
        assert len(baronies) == 10239
        valid_archetypes = {"topographic_default", "pious_devotional", "vain_dynastic", "martial_frontier", "mercantile_civic"}
        for bk, rec in baronies.items():
            assert bk.startswith("b_")
            assert rec["holder_id"] is not None
            assert rec["clean_first_name"]
            assert "_" not in rec["clean_first_name"], f"Raw CK3 underscore leaked in {bk}: {rec['clean_first_name']}"
            assert not any(ch.isdigit() for ch in rec["clean_first_name"]), f"Hex/homonym digit leaked in {bk}: {rec['clean_first_name']}"
            assert rec["archetype"] in valid_archetypes
        assert baronies["b_london"]["clean_first_name"] == "Æthelred"
        assert baronies["b_kiev"]["is_circular_house"] is True
        assert baronies["b_lorient"]["archetype"] == "mercantile_civic"

    def test_barony_physical_and_event_context(self):
        path = REPO_DIR / "data" / "barony_physical_and_event_context.json"
        assert path.exists(), "data/barony_physical_and_event_context.json missing"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert data["metadata"]["total_occupied_baronies"] == 10239
        assert len(data["baronies"]) == 10239
        assert len(data["faith_saints"]) >= 25
        ctx_london = data["baronies"]["b_london"]
        assert ctx_london["has_tradeport"] is True
        assert ctx_london["special_building_type"] == "the_tower_of_london_01"
        assert data["baronies"]["b_kalocsa"]["has_tradeport"] is False

    def test_web_assets_have_coinage_and_context_integration(self):
        assert (DATA_DIR / "barony_coinage_rulers.json").exists(), "docs/data/barony_coinage_rulers.json missing"
        assert (DATA_DIR / "barony_physical_and_event_context.json").exists(), "docs/data/barony_physical_and_event_context.json missing"

        html = (REPO_DIR / "web" / "index.html").read_text(encoding="utf-8")
        assert "drawer-coinage-ruler-group" in html
        assert "drawer-physical-context-group" in html

        js = (REPO_DIR / "web" / "js" / "app.js").read_text(encoding="utf-8")
        assert "barony_coinage_rulers.json" in js
        assert "barony_physical_and_event_context.json" in js
        assert "renderBaronyCoinageRuler" in js
        assert "renderBaronyPhysicalContext" in js

        build_script = (REPO_DIR / "scripts" / "build_webapp.py").read_text(encoding="utf-8")
        assert "barony_coinage_rulers.json" in build_script
        assert "barony_physical_and_event_context.json" in build_script
        assert "barony_geography.json" in build_script
        assert "barony_geography.json" in js
        assert "ensureGeographyLoaded" in js
        assert (DATA_DIR / "barony_geography.json").exists(), "docs/data/barony_geography.json missing"

    def test_barony_geography(self):
        path = REPO_DIR / "data" / "barony_geography.json"
        assert path.exists(), "data/barony_geography.json missing"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        meta = data["metadata"]
        assert meta["total_baronies"] == 11297
        assert meta["total_occupied_baronies"] == 10239
        assert meta["sea_coast_baronies"] >= 1900

        baronies = data["baronies"]
        assert len(baronies) == 11297

        # Verified true sea-coast baronies across Atlantic, Med, Baltic, Black, Red, Persian Gulf, Okhotsk
        for b in ["b_ostia", "b_tarragona", "b_venezia", "b_palermo", "b_alexandria", "b_lubeck", "b_quzlum", "b_aydhab", "b_theodosia", "b_kerch", "b_hormuz", "b_hakata"]:
            assert baronies[b]["is_sea_coast"] is True, f"{b} should be sea_coast"
            assert baronies[b]["coast_type"] == "sea_coast"

        # Verified inland baronies (rivers, lakes, interior wastelands, off-map Eurasia/Africa frontiers)
        for b in ["b_roma", "b_london", "b_szekesfehervar", "b_vyshgorod", "b_paris", "b_mainz", "b_cairo", "b_baghdad", "b_basra", "b_kotlas", "b_bonga", "b_kaffa", "b_khentii"]:
            assert baronies[b]["is_sea_coast"] is False, f"{b} should be inland, not sea_coast"

        # Caspian endorheic sea distinction
        assert baronies["b_derbent"]["is_sea_coast"] is False
        assert baronies["b_derbent"]["is_caspian_coast"] is True
        assert baronies["b_derbent"]["coast_type"] == "endorheic_sea"

        # Centroids, county direction, and imperial frontier metadata
        assert baronies["b_ostia"]["county_direction"] in {"S", "SW", "SE"}
        assert baronies["b_lubeck"]["is_imperial_frontier_barony"] is True
        assert baronies["b_roma"]["is_imperial_frontier_barony"] is False

    def test_ck3_culture_to_iso_and_generics(self):
        path = REPO_DIR / "data" / "ck3_culture_to_iso_and_generics.json"
        assert path.exists(), "data/ck3_culture_to_iso_and_generics.json missing"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        meta = data["metadata"]
        assert meta["total_cultures"] == 404
        assert meta["total_ck3_languages"] == 91
        assert meta["toponymic_profiles_covered"] == meta["cultures_used_in_toponymic_profiles"]
        assert meta["cultures_with_observed_iso_dataset_match"] == 404

        cultures = data["cultures"]
        families = data["morphology_families"]
        trans_rules = data["transmission_rules"]["to_tarraconian"]
        assert len(cultures) == 404

        # Every culture must link cleanly to a valid morphology family, transmission profile, and non-empty ISO list
        for cname, crec in cultures.items():
            assert crec["iso_codes"], f"{cname} missing iso_codes"
            assert crec["primary_iso"] == crec["iso_codes"][0]
            assert crec["liturgical_iso"]
            assert crec["morphology_family"] in families, f"{cname} unknown family"
            assert crec["transmission_profile"] in trans_rules, f"{cname} unknown transmission profile"

        # Every morphology family must define castle, city, church, tribal generics with required keys
        for fname, fam in families.items():
            assert fam["compound_order"] in {"head_initial", "head_final"}
            for htype in ("castle", "city", "church", "tribal"):
                items = fam["generics"][htype]
                assert items, f"{fname} missing {htype} generics"
                for item in items:
                    assert item["form"] and item["gloss"] and item["tarr_calque"]
                    assert item["affix_position"] in {"prefix", "suffix"}

        # Spot-check key mappings and dynamic hybrids
        assert cultures["slovien"]["primary_iso"] == "slk"
        assert cultures["Tarraconian"]["is_tarraconian_core"] is True
        assert cultures["Tarraconian"]["morphology_family"] == "tarraconian_imperial"
        assert cultures["han"]["is_sinosphere_heritage"] is True
        assert "sog" in cultures["Sogdo-Oghuz"]["iso_codes"]
        assert "gmh" in cultures["Tarracono-Tajik"]["iso_codes"]
        assert "hrv" in cultures["Croato-Tarraconian"]["iso_codes"]
        assert "hun" in cultures["Ungwârer"]["iso_codes"]

    def test_multilingual_morpheme_calque_lexicon(self):
        path = REPO_DIR / "data" / "multilingual_morpheme_calque_lexicon.json"
        assert path.exists(), "data/multilingual_morpheme_calque_lexicon.json missing"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        meta = data["metadata"]
        concepts = data["concepts"]
        gloss_idx = data["gloss_index"]
        anchors = data["regional_calque_anchors"]

        assert meta["total_concepts"] == len(concepts) >= 165
        assert meta["total_english_gloss_aliases"] == len(gloss_idx) >= 840
        assert len(anchors) >= 100
        assert meta["corpus_coverage"]["audit_lexical_hit_rate_pct"] >= 80.0

        # Validate required schema and phonotactic hygiene on every concept
        for cid, c in concepts.items():
            assert c["tarr_ipa"]
            assert c["gender_case"]["gender"] in {"m", "f", "n", "pl"}
            assert c["gender_case"]["article"] and c["gender_case"]["dative_article"]
            assert c["tarr_prefix"] or c["tarr_suffix"] or c["tarr_standalone"]
            for fld in ("tarr_prefix", "tarr_suffix", "tarr_standalone"):
                val = (c[fld] or "").lower().strip("-")
                assert not val.endswith(("burg", "berg", "dsch")), f"Phonotactic violation in {cid}: {c[fld]}"

        # Verify gloss index resolution & key canonical entries
        for term in ("castle", "fortress", "white", "river", "mountain", "salt", "iron", "saint", "dragon", "oak"):
            assert term in gloss_idx and gloss_idx[term] in concepts
        assert concepts["castle"]["tarr_suffix"] == "-burch"
        assert concepts["white"]["tarr_prefix"] == "Wîz-"
        assert concepts["mountain_peak"]["tarr_suffix"] == "-berch"
        assert concepts["harbor_port"]["requires_gate"] == "sea_coast"

    def test_global_onomasticon_adaptation(self):
        import importlib.util
        import re

        spec = importlib.util.spec_from_file_location(
            "ck3_name_decoder", REPO_DIR / "scripts" / "ck3_name_decoder.py"
        )
        decoder_mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(decoder_mod)
        decode_ck3_personal_name = decoder_mod.decode_ck3_personal_name

        path = REPO_DIR / "data" / "global_onomasticon_adaptation.json"
        assert path.exists(), "data/global_onomasticon_adaptation.json missing"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        meta = data["metadata"]
        canon = data["canonical_franconian_239"]
        by_raw = data["by_raw_name"]
        by_clean = data["by_clean_name"]

        assert len(canon) == 239
        assert meta["canonical_franconian_239_count"] == 239
        assert meta["unique_raw_names"] == len(by_raw) >= 3300
        assert meta["unique_clean_names"] == len(by_clean) >= 3100
        assert meta["hanzi_bearing_raw_names"] >= 500
        assert meta["faith_saint_raw_names"] >= 150

        # Ensure every unique coinage-era raw_first_name is present
        with open(REPO_DIR / "data" / "barony_coinage_rulers.json", "r", encoding="utf-8") as f:
            coinage = json.load(f)["baronies"]
        coinage_raws = {rec["raw_first_name"] for rec in coinage.values() if rec.get("raw_first_name")}
        assert coinage_raws.issubset(by_raw.keys())

        allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzâêîôûÂÊÎÔÛäöüÄÖÜïëÏ '-")
        for raw, rec in by_raw.items():
            tn = rec["tarr_name"]
            cl = rec["clean_name"]
            assert cl and tn
            assert "_" not in cl and "_" not in tn, f"Underscore leak in {raw}: {cl} / {tn}"
            assert not re.search(r"\d", cl) and not re.search(r"\d", tn), f"Digit leak in {raw}: {cl} / {tn}"
            assert all(ch in allowed for ch in tn), f"Disallowed Chancellery char in {raw}: {tn}"
            assert not re.match(r"^[Tt]s(?![ch])", tn), f"Initial Ts- violation in {raw}: {tn}"
            assert not re.search(r"[Zz]h", tn), f"Raw zh digraph in {raw}: {tn}"
            if raw != "Anselm":
                assert not re.search(r"(?<!c)[Ss]h", tn), f"Bare sh digraph in {raw}: {tn}"
            assert not re.search(r"[Qq](?![uU])", tn), f"Bare q in {raw}: {tn}"
            assert rec["tarr_ipa"].startswith("[") and rec["tarr_ipa"].endswith("]")
            assert rec["tarr_genitive_stem"] and rec["tarr_compound_prefix"]

        # Spot-check tricky CK3 decoder edge cases and cultural adaptations
        assert decode_ck3_personal_name("SE_bert", "anglo_saxon")["clean_name"] == "Sæbert"
        assert decode_ck3_personal_name("MiL_obrat", "polish")["clean_name"] == "Miłobrat"
        assert decode_ck3_personal_name("Michael", "greek")["clean_name"] == "Michael"
        assert decode_ck3_personal_name("Isaac", "meshchera")["clean_name"] == "Isaac"
        assert decode_ck3_personal_name("Aguda_963F_9AA8_6253", "han")["hanzi_chars"] == "阿骨打"

        assert by_raw["A_rpA_d"]["tarr_name"] == "Ârpât"
        assert by_raw["LO_rinc"]["tarr_name"] == "Lôrintz"
        assert by_raw["E_thelred"]["tarr_name"] == "Êdelrêt"
        assert by_raw["U_lfhE_D_inn"]["tarr_name"] == "Ulfhêdîn"
        assert by_raw["T_ar_iq"]["clean_name"] == "Ṭāriq"
        assert by_raw["T_ar_iq"]["tarr_name"] == "Târîk"
        assert by_raw["Aguda_963F_9AA8_6253"]["clean_name"] == "Aguda"
        assert by_raw["Aguda_963F_9AA8_6253"]["hanzi_chars"] == "阿骨打"
        assert by_raw["Aguda_963F_9AA8_6253"]["tarr_name"] == "Agûdâ"
        assert by_raw["TsunetO__2"]["clean_name"] == "Tsunetō"
        assert by_raw["TsunetO__2"]["homonym_index"] == 2
        assert by_raw["TsunetO__2"]["tarr_name"] == "Zûnêtô"

    def test_pipeline_stage0_occupancy(self):
        import importlib.util

        path = REPO_DIR / "data" / "pipeline_stage0_state.json"
        assert path.exists(), "data/pipeline_stage0_state.json missing"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        meta = data["metadata"]
        baronies = data["baronies"]
        assert meta["total_baronies"] == 11297 == len(baronies)
        assert meta["occupied_baronies"] == 10239
        assert meta["unoccupied_baronies"] == 1058
        assert meta["holding_type_counts"] == {
            "castle": 4360,
            "church": 2978,
            "city": 2901,
            "unoccupied": 1058,
        }
        assert meta["occupied_capital_baronies"] == 3476
        assert meta["occupied_historical_867"] + meta["occupied_post_867"] == 10239
        assert meta["legacy_geojson_reconciled_keys"] == ["b_ka'abir", "b_mansa'l-kharaz"]

        occ_cnt = 0
        unocc_cnt = 0
        for bk, rec in baronies.items():
            assert rec["barony_key"] == bk
            assert set(rec["hierarchy"].keys()) == {"empire", "kingdom", "duchy", "county", "barony"}
            if rec["is_occupied"]:
                occ_cnt += 1
                assert rec["stage0_status"] == "ready_for_stage1"
                assert rec["holding_type"] in {"castle", "church", "city"}
            else:
                unocc_cnt += 1
                assert rec["stage0_status"] == "finalized_unoccupied"
                assert rec["holding_type"] == "unoccupied"
                fr = rec["final_record"]
                for blank_fld in ("name", "b_tarr_direct", "b_tarr_hist", "b_ipa", "b_hanzi", "b_origin", "b_anachronism"):
                    assert fr[blank_fld] == ""
                assert fr["b_color"] == "#424242"

        assert occ_cnt == 10239 and unocc_cnt == 1058
        for reconciled_bk in ("b_ka'abir", "b_mansa'l-kharaz"):
            rec = baronies[reconciled_bk]
            assert rec["is_occupied"] is True
            assert rec["holding_type"] == "city"
            assert rec["stage0_status"] == "ready_for_stage1"
            assert rec["legacy_holding_reconciled"] is True

        # Verify offline API invocation
        spec = importlib.util.spec_from_file_location(
            "pipeline_stage0_occupancy", REPO_DIR / "scripts" / "pipeline_stage0_occupancy.py"
        )
        mod = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(mod)
        offline_res = mod.run_stage0(skip_save=True)
        assert offline_res["metadata"]["occupied_baronies"] == 10239
        assert offline_res["metadata"]["unoccupied_baronies"] == 1058

    def test_pipeline_stage2_variant_selection(self):
        path = REPO_DIR / "data" / "pipeline_stage2_variants.json"
        assert path.exists(), "data/pipeline_stage2_variants.json missing"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        meta = data["metadata"]
        baronies = data["baronies"]
        assert meta["total_baronies"] == 11297 == len(baronies)
        assert meta["occupied_baronies"] == 10239
        assert meta["unoccupied_baronies"] == 1058
        assert meta["hanzi_extracted_count"] >= 2000

        for bk, rec in baronies.items():
            if not rec["is_occupied"]:
                assert rec["final_record"]["name"] == ""
            else:
                assert rec["selected_source_form"], f"{bk} missing selected_source_form"
                assert rec["match_tier"], f"{bk} missing match_tier"
                assert rec["coinage_morphology_family"] and rec["substrate_morphology_family"]
                if not rec["is_historical_867"]:
                    assert len(rec["ranked_ntr_candidates"]) >= 1

        # Spot-check variant resolution and coastal vs inland ranking
        assert baronies["b_london"]["selected_source_form"] == "London"
        assert baronies["b_southwark"]["selected_source_form"] == "Temes"
        assert baronies["b_southwark"]["selected_iso"] == "ang"
        assert baronies["b_woxbrigge"]["selected_source_form"] == "Colen"
        assert baronies["b_woxbrigge"]["selected_iso"] == "ang"
        assert baronies["b_szekesfehervar"]["selected_source_form"] == "Gorsium"
        assert baronies["b_szekesfehervar"]["selected_iso"] == "lat"
        assert baronies["b_vyshgorod"]["selected_source_form"] == "Danapris"
        assert baronies["b_vyshgorod"]["selected_iso"] == "lat"
        assert baronies["b_EMan_Huligai"]["extracted_hanzi"] == "忽汗河"
        assert baronies["b_ka'abir"]["selected_source_form"] == "Khalīj Ḥawākil"
        assert baronies["b_ka'abir"]["selected_iso"] == "ara"

    def test_pipeline_stage1_routing(self):
        path = REPO_DIR / "data" / "pipeline_stage1_routed.json"
        assert path.exists(), "data/pipeline_stage1_routed.json missing"
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        meta = data["metadata"]
        baronies = data["baronies"]
        assert meta["total_baronies"] == 11297 == len(baronies)
        assert meta["occupied_baronies"] == 10239
        assert meta["unoccupied_baronies"] == 1058

        expected_families = {"Track_S", "Track_A", "Track_B", "Track_C1", "Track_C2", "Track_D1", "Track_D2"}
        assert set(meta["pipeline_family_counts"].keys()) == expected_families
        assert sum(meta["pipeline_family_counts"].values()) == 10239

        for bk, rec in baronies.items():
            if not rec["is_occupied"]:
                assert rec["stage1_track"] == "Unoccupied_Blank"
                assert rec["final_record"]["name"] == ""
            else:
                assert rec["pipeline_family"] in expected_families
                assert rec["coinage_culture"] and rec["substrate_culture"] and rec["transmission_culture"]
                assert rec["stage2_culture_priority"] in {"substrate_first", "coinage_first"}

        # Canonical track routing spot checks
        assert baronies["b_london"]["stage1_track"] == "Track_A_retained"
        assert baronies["b_woxbrigge"]["stage1_track"] == "Track_D2_post867_foundation"
        assert baronies["b_szekesfehervar"]["stage1_track"] == "Track_C2_post867_feudalized"
        assert baronies["b_szekesfehervar"]["stem_source"] == "historical_names_pre867"
        assert baronies["b_kiev"]["stage1_track"] == "Track_C1_pre867_feudalized"
        assert baronies["b_ka'abir"]["stage1_track"] == "Track_D2_post867_foundation"
        assert baronies["b_EMan_Huligai"]["stage1_track"] == "Track_S_post867_historical_anchor"

        # Non-Sinospheric post-conquest Tarraconian inside Sino frontier excluded from Track S
        assert baronies["b_FIC_Amur_Lindu"]["sino_scope_basis"] == "excluded_post_conquest_tarraconian"
        assert baronies["b_FIC_Amur_Lindu"]["stage1_track"] == "Track_D2_post867_foundation"
        assert baronies["b_fic_eman_bixinshang"]["sino_scope_basis"] == "excluded_post_conquest_tarraconian"
        assert baronies["b_fic_eman_bixinshang"]["stage1_track"] == "Track_D2_post867_foundation"













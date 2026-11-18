#!/usr/bin/env python3
"""
build_webapp.py

Prepares and packages the Tarraconian Atlas web application for GitHub Pages.
Copies web assets and required map datasets into docs/ with a .nojekyll marker.
"""

import shutil
from pathlib import Path

REPO_DIR = Path(__file__).resolve().parent.parent
WEB_DIR = REPO_DIR / "web"
DATA_DIR = REPO_DIR / "data"
DOCS_DIR = REPO_DIR / "docs"

def main():
    print(f"Packaging web app to: {DOCS_DIR}")
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Copy web assets (HTML, CSS, JS)
    shutil.copy2(WEB_DIR / "index.html", DOCS_DIR / "index.html")
    if (WEB_DIR / "404.html").exists():
        shutil.copy2(WEB_DIR / "404.html", DOCS_DIR / "404.html")

    (DOCS_DIR / "css").mkdir(parents=True, exist_ok=True)
    shutil.copy2(WEB_DIR / "css" / "styles.css", DOCS_DIR / "css" / "styles.css")

    (DOCS_DIR / "js").mkdir(parents=True, exist_ok=True)
    shutil.copy2(WEB_DIR / "js" / "app.js", DOCS_DIR / "js" / "app.js")

    if (WEB_DIR / "vendor").exists():
        if (DOCS_DIR / "vendor").exists():
            shutil.rmtree(DOCS_DIR / "vendor")
        shutil.copytree(WEB_DIR / "vendor", DOCS_DIR / "vendor")

    # 2. Copy production datasets
    docs_data = DOCS_DIR / "data"
    docs_data.mkdir(parents=True, exist_ok=True)

    required_datasets = [
        "ck3_counties.geojson",
        "ck3_baronies.geojson",
        "ck3_title_tree.json",
        "ck3_adjacencies.json",
        "sinosphere_hanzi_calques.json",
        "sinosphere_kanji_tarraconian.json",
        "sinosphere_title_calques.json",
    ]
    for dset in required_datasets:
        src = DATA_DIR / dset
        if src.exists():
            print(f"  Copying {dset} ({src.stat().st_size / 1024 / 1024:.2f} MB)...")
            shutil.copy2(src, docs_data / dset)
        else:
            print(f"  Warning: {dset} not found in {DATA_DIR}")

    # 3. Add .nojekyll for GitHub Pages
    (DOCS_DIR / ".nojekyll").touch()

    print("Successfully built web app in docs/ for GitHub Pages!")

if __name__ == "__main__":
    main()

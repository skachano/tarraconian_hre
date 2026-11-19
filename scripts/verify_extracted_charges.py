#!/usr/bin/env python3
import json
import re
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
JS_PATH = BASE_DIR / "web" / "js" / "symbol_generator.js"
OUT_DIR = Path(
    "/home/siarzhuk/.gemini/antigravity/brain/04bd38d0-c723-434d-8f3c-ffd284386ecb/renders"
)

content = JS_PATH.read_text(encoding="utf-8")

PALETTE = {
    "or": "#e2b007",
    "argent": "#fbf9f5",
    "gules": "#c91e2b",
    "sable": "#1c1b1a",
    "azure": "#154889",
    "vert": "#1e6b37",
    "purpure": "#5b2c6f",
    "wood": "#4a2e18",
}

CHARGES = [
    ("eagle_double", "#1c1b1a", "#e2b007", "Double Eagle Sable on Or"),
    ("alerion", "#c91e2b", "#e2b007", "Alerion Gules on Or"),
    ("lion_rampant", "#e2b007", "#c91e2b", "Lion Rampant Or on Gules"),
    ("dragon", "#c91e2b", "#fbf9f5", "Dragon Gules on Argent"),
    ("stag_attired", "#e2b007", "#154889", "Stag Attired Or on Azure"),
    ("bear_rampant", "#1c1b1a", "#fbf9f5", "Bear Rampant Sable on Argent"),
    ("horse_courant", "#fbf9f5", "#c91e2b", "Horse Courant Argent on Gules"),
    ("wolf_statant", "#e2b007", "#154889", "Wolf Statant Or on Azure"),
    ("fish_twin", "#fbf9f5", "#154889", "Twin Fish Argent on Azure"),
    ("falcon_perched", "#e2b007", "#154889", "Falcon Perched Or on Azure"),
]

bt = chr(96)
pattern = re.compile(
    rf"([a-z_]+)\s*:\s*\([^)]*\)\s*=>\s*{bt}(.*?){bt},", re.DOTALL
)
extracted_builders = {}
for m in pattern.finditer(content):
    extracted_builders[m.group(1)] = m.group(2)

print(f"Extracted {len(extracted_builders)} charge builders from symbol_generator.js")

shield_d = "M 30 25 L 190 25 C 190 120 155 185 110 205 C 65 185 30 120 30 25 Z"

for ch_name, ch_color, bg_color, title in CHARGES:
    assert ch_name in extracted_builders, f"Missing {ch_name}"
    tpl = extracted_builders[ch_name]

    # Evaluate simple JS template expressions
    rendered = tpl
    rendered = rendered.replace("${cx}", "110")
    rendered = rendered.replace("${cy}", "110")
    rendered = rendered.replace("${scale * 0.95}", "0.95")
    rendered = rendered.replace("${scale * 1.05}", "1.05")
    rendered = rendered.replace("${scale * 1.0}", "1.0")
    rendered = rendered.replace("${cx - 18 * scale}", "92")
    rendered = rendered.replace("${cx + 18 * scale}", "128")
    rendered = rendered.replace("${color}", ch_color)
    rendered = rendered.replace("${accent}", "#1c1b1a")
    rendered = rendered.replace("${perch}", PALETTE["wood"])

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 220" width="220" height="220">
      <defs>
        <clipPath id="clip-{ch_name}">
          <path d="{shield_d}" />
        </clipPath>
      </defs>
      <path d="{shield_d}" fill="{bg_color}" stroke="#1c1b1a" stroke-width="3" />
      <g clip-path="url(#clip-{ch_name})">
        {rendered}
      </g>
    </svg>"""

    svg_file = f"/tmp/verify_{ch_name}.svg"
    png_file = OUT_DIR / f"verify_{ch_name}.png"
    Path(svg_file).write_text(svg, encoding="utf-8")
    res = subprocess.run(
        ["rsvg-convert", "-w", "220", "-h", "220", svg_file, "-o", str(png_file)]
    )
    assert res.returncode == 0, f"rsvg-convert failed for {ch_name}"
    print(f"  Verified & rendered: {ch_name} -> {png_file.name}")

print("All 10 authentic animal charges verified and rendered successfully!")

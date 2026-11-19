#!/usr/bin/env python3
"""
Integrate authentic WappenWiki vector charges for the 10 animal charges in web/js/symbol_generator.js
"""

import os
import re
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHARGES_DIR = os.path.join(BASE_DIR, "scratch", "armoria_charges")
JS_PATH = os.path.join(BASE_DIR, "web", "js", "symbol_generator.js")


def clean_element(elem):
    tag = elem.tag.split("}")[-1]
    attrib = {}
    for k, v in elem.attrib.items():
        k_clean = k.split("}")[-1]
        if k_clean in ("id",):
            continue  # drop internal IDs
        attrib[k_clean] = v

    if "fill" in attrib:
        if attrib["fill"].lower() in ("#d7374a",):
            del attrib["fill"]
        elif attrib["fill"] == "#000":
            attrib["fill"] = "${accent}"
    if "stroke" in attrib and attrib["stroke"] == "#000":
        attrib["stroke"] = "${accent}"

    attrs_str = " ".join(f'{k}="{v}"' for k, v in attrib.items())
    if attrs_str:
        attrs_str = " " + attrs_str

    children_str = "".join(clean_element(c) for c in elem)
    if children_str:
        return f"<{tag}{attrs_str}>{children_str}</{tag}>"
    else:
        return f"<{tag}{attrs_str} />"


def get_charge_inner(svg_filename):
    svg_path = os.path.join(CHARGES_DIR, svg_filename)
    tree = ET.parse(svg_path)
    root = tree.getroot()
    g = root.find("{http://www.w3.org/2000/svg}g")
    return "".join(clean_element(c) for c in g)


def build_charge_codes():
    builders = {}

    # 1. eagle_double
    inner = get_charge_inner("eagleTwoHeads.svg")
    builders["eagle_double"] = f"""    // Double-headed Imperial Eagle (Rome / HRE)
    eagle_double: (color = PALETTE.sable, scale = 1, cx = 110, cy = 110, accent = PALETTE.sable) => `
      <g transform="translate(${{cx}}, ${{cy}}) scale(${{scale * 0.95}}) translate(-100, -105)" fill="${{color}}" stroke="${{accent}}" stroke-width="0.35">
        {inner}
      </g>
    `,"""

    # 2. alerion
    inner = get_charge_inner("eagle.svg")
    builders["alerion"] = f"""    // Lorraine Alerion (Single-headed Spread Eagle)
    alerion: (color = PALETTE.argent, scale = 1, cx = 110, cy = 110, accent = PALETTE.sable) => `
      <g transform="translate(${{cx}}, ${{cy}}) scale(${{scale * 0.95}}) translate(-100, -104)" fill="${{color}}" stroke="${{accent}}" stroke-width="0.35">
        {inner}
      </g>
    `,"""

    # 3. lion_rampant
    inner = get_charge_inner("lionRampant.svg")
    builders["lion_rampant"] = f"""    // Heraldic Lion Rampant
    lion_rampant: (color = PALETTE.gules, scale = 1, cx = 110, cy = 115, accent = PALETTE.sable) => `
      <g transform="translate(${{cx}}, ${{cy}}) scale(${{scale * 0.95}}) translate(-100, -104)" fill="${{color}}" stroke="${{accent}}" stroke-width="0.35">
        {inner}
      </g>
    `,"""

    # 4. dragon
    inner = get_charge_inner("dragonRampant.svg")
    builders["dragon"] = f"""    // Heraldic Dragon Rampant
    dragon: (color = PALETTE.or, scale = 1, cx = 110, cy = 110, accent = PALETTE.sable) => `
      <g transform="translate(${{cx}}, ${{cy}}) scale(${{scale * 1.0}}) translate(-100, -100)" fill="${{color}}" stroke="${{accent}}" stroke-width="0.35">
        {inner}
      </g>
    `,"""

    # 5. stag_attired
    inner = get_charge_inner("stagPassant.svg")
    builders["stag_attired"] = f"""    // Standing Stag Attired
    stag_attired: (color = PALETTE.or, scale = 1, cx = 110, cy = 110, antlers = null, accent = PALETTE.sable) => `
      <g transform="translate(${{cx}}, ${{cy}}) scale(${{scale * 1.05}}) translate(-100, -99)" fill="${{color}}" stroke="${{accent}}" stroke-width="0.35">
        {inner}
      </g>
    `,"""

    # 6. bear_rampant
    inner = get_charge_inner("bearRampant.svg")
    builders["bear_rampant"] = f"""    // Bear Rampant
    bear_rampant: (color = PALETTE.sable, scale = 1, cx = 110, cy = 110, accent = PALETTE.sable) => `
      <g transform="translate(${{cx}}, ${{cy}}) scale(${{scale * 1.0}}) translate(-97, -100)" fill="${{color}}" stroke="${{accent}}" stroke-width="0.35">
        {inner}
      </g>
    `,"""

    # 7. horse_courant
    inner = get_charge_inner("horseSalient.svg")
    builders["horse_courant"] = f"""    // Galloping Steed / Horse Courant
    horse_courant: (color = PALETTE.argent, scale = 1, cx = 110, cy = 110, accent = PALETTE.sable) => `
      <g transform="translate(${{cx}}, ${{cy}}) scale(${{scale * 0.95}}) translate(-101, -100)" fill="${{color}}" stroke="${{accent}}" stroke-width="0.35">
        {inner}
      </g>
    `,"""

    # 8. wolf_statant
    inner = get_charge_inner("wolfStatant.svg")
    builders["wolf_statant"] = f"""    // Wolf Statant
    wolf_statant: (color = PALETTE.sable, scale = 1, cx = 110, cy = 110, accent = PALETTE.sable) => `
      <g transform="translate(${{cx}}, ${{cy}}) scale(${{scale * 1.05}}) translate(-100, -100)" fill="${{color}}" stroke="${{accent}}" stroke-width="0.35">
        {inner}
      </g>
    `,"""

    # 9. fish_twin
    inner = get_charge_inner("salmon.svg")
    builders["fish_twin"] = f"""    // Twin Heraldic Fish Haurient Addorsed
    fish_twin: (color = PALETTE.argent, scale = 1, cx = 110, cy = 110, accent = PALETTE.sable) => `
      <g fill="${{color}}" stroke="${{accent}}" stroke-width="0.35">
        <g transform="translate(${{cx - 18 * scale}}, ${{cy}}) scale(${{scale * 0.95}}) rotate(90) scale(1, -1) translate(-100, -100)">
          {inner}
        </g>
        <g transform="translate(${{cx + 18 * scale}}, ${{cy}}) scale(${{scale * 0.95}}) rotate(90) translate(-100, -100)">
          {inner}
        </g>
      </g>
    `,"""

    # 10. falcon_perched
    inner = get_charge_inner("falcon.svg")
    builders["falcon_perched"] = f"""    // Hunting Falcon on Perch
    falcon_perched: (color = PALETTE.sable, scale = 1, cx = 110, cy = 110, perch = PALETTE.wood, accent = PALETTE.sable) => `
      <g fill="${{color}}" stroke="${{accent}}" stroke-width="0.35">
        <g transform="translate(${{cx}}, ${{cy}}) scale(${{scale * 1.05}}) translate(-100, -99)">
          <line x1="65" y1="134" x2="135" y2="134" stroke="${{perch}}" stroke-width="5" stroke-linecap="round" />
          {inner}
        </g>
      </g>
    `,"""

    return builders


def main():
    with open(JS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    builders = build_charge_codes()

    for name, replacement in builders.items():
        pattern = re.compile(
            rf"([ \t]*//[^\n]*\n)?[ \t]*{name}:\s*\([^)]*\)\s*=>\s*`.*?`,",
            re.DOTALL,
        )
        match = pattern.search(content)
        if not match:
            print(f"ERROR: Could not find builder for {name}")
            return False
        content = pattern.sub(lambda _: replacement, content, count=1)
        print(f"Replaced {name} successfully")

    with open(JS_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print("Updated web/js/symbol_generator.js successfully!")
    return True


if __name__ == "__main__":
    main()

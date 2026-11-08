import re
import json

from prepare_section5_update import section5_db

# Read names from sinosphere_titles_and_characters_1154.md
with open("sinosphere_titles_and_characters_1154.md", "r", encoding="utf-8") as f:
    gaz_text = f.read()

names = {}
for line in gaz_text.split("\n"):
    if line.startswith("|") and "`c_" in line:
        parts = line.split("|")
        # In section 2/3: parts[2] is key, parts[3] is eng, parts[4] is ch
        if len(parts) >= 6:
            k_match = re.search(r"`(c_[^`]+)`", parts[2])
            if k_match:
                k = k_match.group(1)
                eng = parts[3].replace("**", "").strip()
                ch = parts[4].replace("**", "").strip()
                names[k] = (eng, ch)

print(f"Extracted names for {len(names)} counties from gazetteer.")

# Helper for adjectives
def get_adj(tarr):
    stem = tarr.replace("Magistrat van ", "").strip()
    if stem.startswith("dem "):
        stem = stem[4:]
    if stem.endswith("e"):
        adj = stem[:-1] + "er"
    else:
        adj = stem + "er"
    return f"*{adj}*"

with open("audit_discrepancy_register.md", "r", encoding="utf-8") as f:
    text = f.read()

# Add note in Section 1 if not present
note_target = "## 1. Executive Summary & Resolution Metrics\n"
note_insert = """## 1. Executive Summary & Resolution Metrics

> [!NOTE]
> **Harmonized Calque Paradigm for Logographic Sinospheric Titles:**
> For the 61 flagged titles within the Sinosphere (East Asia / Mandate of Heaven perimeter), post-867 foundations are predominantly logographic Chinese character compositions (`汉字` / *Hànzì*) rather than feudal eponymous castles. Under this harmonized paradigm:
> 1. Each title's territorial jurisdiction is anchored to its authentic pre-867 physical river basin, mountain pass, or lacustrine catchment (Option B: e.g. *Yitong River / Songhua Basin*, *Daling River*, *Shira Muren*, *Mudan River*, *Xiao Pass*).
> 2. The official Tarraconian Chancellery title is formed by directly calquing the semantic ideographs into Tarraconian (e.g., `长春` "Eternal Spring" $\rightarrow$ **`Magistrat van Langlenten`**; `大定` "Great Settlement" $\rightarrow$ **`Magistrat van Grôzfest`**; `安边` "Pacified Frontier" $\rightarrow$ **`Magistrat van Fridmarch`**), completely resolving the feudal causal paradox while preserving authentic Sinitic statecraft semantics.

"""

if "Harmonized Calque Paradigm for Logographic Sinospheric Titles:" not in text:
    text = text.replace(note_target, note_insert, 1)
    print("Added Harmonized Calque Paradigm note to Section 1 of audit_discrepancy_register.md")

lines = text.split("\n")
updated_count = 0
new_lines = []

for line in lines:
    updated = False
    for k, (opt_b, tarr, note) in section5_db.items():
        if f"`{k}`" in line and line.strip().startswith("|"):
            parts = line.split("|")
            # Expected columns in Section 4:
            # ['', County Key, Current Save Name, De Jure Kingdom, Tier, Discrepancy Reason, Final Resolution, Official Title, Official Adjective, Historical Justification, '']
            if len(parts) >= 10:
                basin_en, chars = opt_b.rsplit(" (", 1)
                chars = "(" + chars
                eng, ch = names.get(k, (k, ""))
                
                parts[2] = f" **{eng} ({ch})** " if ch else f" **{eng}** "
                parts[6] = f" **Option B:** `{basin_en}` {chars} "
                parts[7] = f" **{tarr}** "
                parts[8] = f" {get_adj(tarr)} "
                parts[9] = f" {note} "
                
                line = "|".join(parts)
                updated_count += 1
                updated = True
                break
    new_lines.append(line)

print(f"Updated {updated_count} / 61 Sinosphere titles in audit_discrepancy_register.md")

with open("audit_discrepancy_register.md", "w", encoding="utf-8") as f:
    f.write("\n".join(new_lines))

print("Saved audit_discrepancy_register.md")

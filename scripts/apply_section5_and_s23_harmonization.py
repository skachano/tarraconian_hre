import re
import json

with open("data/sinosphere_title_calques.json", encoding="utf-8") as f:
    calques = json.load(f)

from prepare_section5_update import section5_db

with open("sinosphere_titles_and_characters_1154.md", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update Section 1.4
s14_old = """### 1.4 Historical Anachronism Audit & Resolution Synthesis

Under the project's historical title audit framework ([`title_historical_accuracy_audit_plan.md`](title_historical_accuracy_audit_plan.md) and [`audit_discrepancy_register.md`](audit_discrepancy_register.md)), all titles within the Imperial sphere are rigorously screened against the **867 AD campaign divergence milestone**:
- **90.2% (559 of 620 counties)** are **Tier 1 (Authentic Pre-867 Classical Antiquity Foundations)**. The commanderies, prefectures, and provinces of the Central Plains, Ba-Shu, Jiangnan, Lingnan, Korea (Three Kingdoms/Silla), and Japan (Ritsuryō) date back centuries before 867 AD.
- **9.8% (61 of 620 counties)** were flagged under **Tier 3 (Post-867 Settlements & Unverified Titles)** due to post-867 Khitan Liao dynasty foundations (918–1007 AD), Jurchen frontier outposts, and nomadic clan divisions in the northern marches.
- **100% of the 61 Flagged Titles** have been reconciled under **Option B (Ancient Hydronymic & Natural Regional Basin Hierarchy)**, anchoring them to their underlying river basins and mountain horizons. The complete register is documented in **Section 5**."""

s14_new = """### 1.4 Historical Anachronism Audit & Resolution Synthesis

Under the project's historical title audit framework ([`title_historical_accuracy_audit_plan.md`](title_historical_accuracy_audit_plan.md) and [`audit_discrepancy_register.md`](audit_discrepancy_register.md)), all titles within the Imperial sphere are rigorously screened against the **867 AD campaign divergence milestone**:
- **90.2% (559 of 620 counties)** are **Tier 1 (Authentic Pre-867 Classical Antiquity Foundations)**. The commanderies, prefectures, and provinces of the Central Plains, Ba-Shu, Jiangnan, Lingnan, Korea (Three Kingdoms/Silla), and Japan (Ritsuryō) date back centuries before 867 AD.
- **9.8% (61 of 620 counties)** were flagged under **Tier 3 (Post-867 Settlements & Unverified Titles)** due to post-867 Khitan Liao dynasty foundations (918–1007 AD), Jurchen frontier outposts, and nomadic clan divisions in the northern marches.
- **100% of the 61 Flagged Titles** have been reconciled under the **Harmonized Calque Paradigm for Logographic Sinospheric Toponyms**:
  1. **Geographical Anchoring (Option B Substrates):** Unlike European post-867 foundations which are predominantly personal eponymous castles (*Albrechtsburg*, *Löwenstein*), Sinospheric foundations are rooted in distinct physical landscapes. Each flagged county is anchored to its authentic pre-867 river basin, mountain pass, or lacustrine catchment (Option B: e.g., Yitong River / Songhua Basin, Daling River, Shira Muren, Mudan River, Xiao Pass).
  2. **Semantic Calquing vs. Feudal Eponyms:** Because Chinese characters (`汉字` / *Hànzì*) express ideographic and descriptive semantic meanings (`长春` "Eternal Spring", `大定` "Great Settlement / Firm Peace", `安边` "Pacified Frontier", `黑草岸` "Black Grass Strand") rather than dynastic lord names, translating them directly into Tarraconian chancellery calques (*Langlenten*, *Grôzfest*, *Fridmarch*, *Swartzwêdouwe*) introduces **no causal paradox** while preserving authentic Sinitic statecraft semantics.
  3. **Official Chancellery Integration:** The official Tarraconian titles seamlessly adopt these semantic calques, while the physical territorial jurisdiction is permanently anchored to its verified pre-867 natural substrate (Option B). The complete register of all 61 resolutions is documented in **Section 5**."""

if s14_old in text:
    text = text.replace(s14_old, s14_new)
    print("Replaced Section 1.4 successfully.")
else:
    print("WARNING: s14_old not found!")

# 2. Update Section 5 introduction
s5_intro_old = """## 5. Master Register of 61 Sinosphere Anachronism Resolutions

Below is the exhaustive audit register of all **61 Sinosphere counties** flagged for post-867 foundation, eponymous naming, or lack of verified classical antiquity urban attestation. Under the **Toponym-First Principle**, all 61 titles have been resolved to their underlying ancient hydronyms, natural relief landmarks, or regional basin substrates (Option B) to prevent the circular canonization of high-medieval foundations."""

s5_intro_new = """## 5. Master Register of 61 Sinosphere Anachronism Resolutions

Below is the exhaustive audit register of all **61 Sinosphere counties** flagged for post-867 foundation, eponymous naming, or lack of verified classical antiquity urban attestation.

### The Harmonized Calque Paradigm for Logographic Sinospheric Toponyms
In Western feudal Europe, post-867 high medieval titles frequently derive from dynastic eponymous castles (*Albrechtsburg*, *Habsburg*), which create an alternate-history causal paradox when an 867 divergence timeline continues to use names of non-existent feudal lords. Option B resolves this by replacing the eponymous castle with the underlying physical hydronym (*Poltva*, *Aare*).

In the Sinosphere, however, administrative foundations were named logographically with Chinese characters (`汉字`) expressing descriptive, physical, or moral-philosophical concepts:
- **Ideographic Foundations:** Toponyms like `长春` (*Chángchūn*, "Eternal Spring"), `大定` (*Dàdìng*, "Great Settlement / Firm Peace"), `安边` (*Ānbiān*, "Pacified Frontier March"), and `黑草岸` (*Hēicǎo'àn*, "Black Grass Shore") reflect imperial statecraft and natural geography rather than personal lord names.
- **Harmonized Calque & Physical Substrate:** Translating these logographic titles into Tarraconian chancellery calques (**`Magistrat van Langlenten`**, **`Magistrat van Grôzfest`**, **`Magistrat van Fridmarch`**, **`Magistrat van Swartzwêdouwe`**) directly eliminates the causal paradox while preserving authentic Sinitic semantics. Simultaneously, each title's territorial jurisdiction is anchored to its verified pre-867 physical river basin, mountain pass, or lake catchment (Option B: e.g., *Yitong River / Songhua Basin*, *Daling River*, *Shira Muren*, *Xiao Pass*).
- **Phonotactic Rigor:** Non-Han indigenous stems (Mongolic, Tungusic, Evenk, Ainu) are adapted in accordance with 12th-century historical phonology and Tarraconian phonotactics ([`sinosphere_phonetics_and_transcription_guide_1154.md`](sinosphere_phonetics_and_transcription_guide_1154.md))."""

if s5_intro_old in text:
    text = text.replace(s5_intro_old, s5_intro_new)
    print("Replaced Section 5 intro successfully.")
else:
    print("WARNING: s5_intro_old not found!")

# 3. Update line by line
lines = text.split("\n")
s5_start_idx = 0
for i, l in enumerate(lines):
    if l.startswith("## 5."):
        s5_start_idx = i
        break

print(f"Section 5 starts at line index {s5_start_idx}")

updated_s23_rows = 0
updated_s23_notes = 0
updated_s5_rows = 0

new_lines = []
for i, line in enumerate(lines):
    if i < s5_start_idx:
        # Check if line is a table row for one of the 61 keys
        is_row = False
        for k, (opt_b, tarr, note) in section5_db.items():
            if f"`{k}`" in line and line.startswith("|"):
                parts = line.split("|")
                # Parts: ['', num, key, eng, ch, tr, tarr_title, status, liege, cult, dev, hold, bhold, '']
                # Total len is 14
                if len(parts) >= 13:
                    parts[6] = f" **{tarr}** "
                    parts[7] = f"⚠️ **[Post-867 / Tier 3]** → *Opt B: {opt_b}*"
                    line = "|".join(parts)
                    updated_s23_rows += 1
                    is_row = True
                    break
        if not is_row:
            # Check if line is a note callout: > * **`c_LIAO_changchun` (Changchun / 长春):** ...
            for k, (opt_b, tarr, note) in section5_db.items():
                if f"`{k}`" in line and line.strip().startswith("> * **`"):
                    # Extract header part: > * **`key` (Name / Chars):**
                    # Replace resolution part
                    m = re.match(r"(>\s*\*\s*\*\*`" + re.escape(k) + r"`\s*\([^)]+\):\*\*)\s*(.*)", line)
                    if m:
                        head = m.group(1)
                        # Extract the rationale before "*Resolved via Option B:"
                        rest = m.group(2)
                        rationale = rest.split("*Resolved via Option B:")[0].strip()
                        line = f"{head} {rationale} *Resolved via Option B: **{opt_b}**; Tarraconian Chancellery title: **{tarr}**.*"
                        updated_s23_notes += 1
                        break
        new_lines.append(line)
    else:
        # Section 5 rows
        is_s5_row = False
        for k, (opt_b, tarr, note) in section5_db.items():
            if f"`{k}`" in line and line.startswith("|"):
                parts = line.split("|")
                # Parts: ['', num, key, in_game, ch, kingdom, rationale, opt_b_col, tarr_col, etymo_col, '']
                # Total len is 11
                if len(parts) >= 10:
                    basin_en, chars = opt_b.rsplit(" (", 1)
                    chars = "(" + chars
                    parts[7] = f"**Option B:** `{basin_en}` {chars}"
                    parts[8] = f" **{tarr}** "
                    parts[9] = f"{note}"
                    line = "|".join(parts)
                    updated_s5_rows += 1
                    is_s5_row = True
                    break
        new_lines.append(line)

print(f"Updated S23 rows: {updated_s23_rows} / 61")
print(f"Updated S23 notes: {updated_s23_notes} / 61")
print(f"Updated S5 rows: {updated_s5_rows} / 61")

out_text = "\n".join(new_lines)
with open("sinosphere_titles_and_characters_1154.md", "w", encoding="utf-8") as f:
    f.write(out_text)

print("Saved updated sinosphere_titles_and_characters_1154.md")

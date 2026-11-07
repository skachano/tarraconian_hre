---
name: update-empire-gazetteer
description: Automatically updates hre_de_jure_and_archdioceses_1059.md with all titles in de jure empires or kingdoms that have at least 1 county in the Roman Empire from the latest CK3 save game.
---

# Update Roman Empire Gazetteer (`update-empire-gazetteer`)

Use this skill whenever the user requests updating the Roman Empire de jure title gazetteer (`hre_de_jure_and_archdioceses_1059.md`) from a CK3 save game (e.g. after advancing the campaign timeline).

## Quick Execution

The workspace provides an automated pipeline script and Docker runner in `scripts/`:

### 1. Standard Execution (Inside Docker)
```bash
./scripts/run_update_gazetteer_docker.sh --scope empire
```

### 2. Direct Python Execution (Host Environment)
```bash
python3 scripts/update_hre_gazetteer.py --scope empire
```

---

## Command Options

| Argument | Default | Description |
| :--- | :--- | :--- |
| `--scope` | `empire` | Scope filter: `empire` (all titles in de jure empires with $\ge 1$ county in RE) or `kingdom` (all titles in de jure kingdoms with $\ge 1$ county in RE). |
| `--save-file` | `/mnt/windows/.../chatenois_867_01_01.ck3` | Path to the active binary CK3 save game. |
| `--melted-save` | `/var/tmp/ck3_audit/melted_save.ck3` | Path to the melted plaintext save file. Automatically melted with `rakaly` if missing or outdated. |
| `--target-md` | `hre_de_jure_and_archdioceses_1059.md` | Path to the target gazetteer markdown document. |
| `--loc-cache` | `/var/tmp/ck3_audit/english_titles_cache.json` | Path to title English localization cache. |
| `--no-sync` | `false` | Skip running `sync_hre_gazetteer.py` and `verify_mod_assets.py`. |

---

## What the Pipeline Does

1. **Save Melting**: If the raw save game is newer than the melted file, it automatically invokes `rakaly` to melt the save to plaintext.
2. **Topological De Facto Liege Resolution**: Recursively resolves the top-level liege for every county, marking counties whose top liege is `h_roman_empire` (or `e_hre` / `e_roman_empire`) as belonging to the Roman Empire.
3. **De Jure Hierarchy Extraction**: Maps `County` $\rightarrow$ `Duchy` $\rightarrow$ `Kingdom` $\rightarrow$ `Empire` from `de_jure_liege` in the save game (accounting for title drifts).
4. **Filtering Landless Family Estates**: Excludes Roads to Power noble family estates (`c_nf_*`) to match geographical map topology.
5. **Preserving Historical Resolutions & Comments**: Preserves pre-existing kingdom numbering, custom historical notes, anachronism warnings (`⚠️ [Post-1059 Foundation]`, `⚠️ [Ostsiedlung Anachronism]`), and Tarraconian naming annotations (`— *Tarraconian: ...*`).
6. **Summary Tables Generation**:
   - Section 1.1: Summary Table of De Jure Empires.
   - Section 1.2: Summary Table of De Jure Kingdoms.
7. **Complete De Jure Hierarchy**:
   - Updates control counts (`— *X/Y in HRE*`) for all duchies.
   - Updates markers (`**[HRE]**` vs `[Non-HRE]`) for all counties.
   - Appends any new kingdoms in the imperial sphere.
8. **Ecclesiastical Synchronization**: Updates Section 3 headers and callouts.
9. **Automated Validation**: Executes `scripts/sync_hre_gazetteer.py` to ensure 100% sync with `tarraconian_titles_1059.md` and `scripts/verify_mod_assets.py` to ensure 0 broken references in the mod.

---

## Post-Run Verification

Always verify after running the update:
```bash
git diff --stat hre_de_jure_and_archdioceses_1059.md
python3 scripts/sync_hre_gazetteer.py
python3 scripts/verify_mod_assets.py
```

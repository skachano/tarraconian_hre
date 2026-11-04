$ErrorActionPreference = 'Stop'

$mdPath = 'C:\Users\siarg\Documents\Projects\Tarraconian\tarraconian_titles_1059.md'
$lines = [System.IO.File]::ReadAllLines($mdPath, [System.Text.Encoding]::UTF8)

function Clean-Toponym([string]$raw) {
    $s = $raw.Trim()
    # Strip parenthetical notes like (Freising) or (Chellah / Salé) first
    $s = $s -replace '\s*\([^)]*\)', ''
    # Strip any rank prefix + optional van (with or without space)
    $s = $s -replace '^(Keiserrîch|Keiserrich|Kûnincrich|Kunincrich|Regenat|Gubernat|March|Erzbisdom|Fürstbisdom|Furstbisdom|Magistrat)\s*(van\s*|van)?(der\s+|den\s+)?', ''
    $s = $s -replace '^[^\s]+\s+van\s+(der\s+|den\s+)?', ''
    # Strip trailing asterisks or quotes
    $s = $s.Trim('*', ' ', '"', "'")
    return $s
}

function Extract-FirstHist([string]$rawHistGroup) {
    # Remove parenthetical notes before splitting on '/' so slashes inside (...) do not split the name
    $noParens = $rawHistGroup -replace '\s*\([^)]*\)', ''
    $first = ($noParens -split '/')[0]
    return (Clean-Toponym $first)
}

function Get-TarrAdj([string]$name, [string]$key) {
    if ([string]::IsNullOrWhiteSpace($name)) { return $name }
    if ($key -eq 'e_hre' -or $key -eq 'h_roman_empire' -or $key -eq 'e_roman_empire') { return 'Rômisch-Keiserlich' }
    if ($key -eq 'k_papal_state') { return 'Rômisch-Pâbestlich' }
    if ($key -eq 'k_orthodox') { return 'Ökumênisch-Patriarchalisch' }
    if ($key -eq 'd_coptic_papacy') { return 'Koptisch-Pâbestlich' }
    if ($key -eq 'd_apostolic_church') { return 'Armênisch-Apostôlisch' }
    if ($key -eq 'd_conversos') { return 'Konversisch-Pâbestlich' }
    if ($name -match '^Pâbestdôm van (.+)$') { $name = $matches[1] }
    if ($name -eq 'Pontischen Steppe' -or $name -eq 'Pontische Steppe') { return 'Pontisch-Steppisch' }
    if ($name -eq 'Kaspischen Steppe' -or $name -eq 'Kaspische Steppe') { return 'Kaspisch-Steppisch' }
    if ($name -eq 'Welschen March') { return 'Welsch-Märchisch' }
    if ($name -eq 'Rôten Wûste') { return 'Rôtwûstisch' }
    if ($name -eq 'Egêischen Inseln') { return 'Egêisch' }

    # Strip prepositional qualifiers (-in-..., -an-der-..., -am-...) for cleaner adjectives
    if ($name -match '^([^-]+)-(in|an|am|ob|uf)-.+$') {
        $name = $matches[1]
    }

    # Explicit historical/chancellery stem adjectives
    switch ($name) {
        'Beiern'     { return 'Beierisch' }
        'Sâpmi'      { return 'Sâmisch' }
        'Finlant'    { return 'Finnisch' }
        'Suômi'      { return 'Suômisch' }
        'Estlant'    { return 'Estnisch' }
        'Bjarmelant' { return 'Bjarmisch' }
        'Krête'      { return 'Krêtisch' }
        'Tzipern'    { return 'Tziprisch' }
        'Tzîpern'    { return 'Tziprisch' }
        'Bâli'       { return 'Bâlisch' }
        'Songâi'     { return 'Songâisch' }
        'Sînt'       { return 'Sîndisch' }
        'Hellas'     { return 'Hellênisch' }
        'Îrlant'     { return 'Îrisch' }
        'Schotlant'  { return 'Schottisch' }
        'Brîe'       { return 'Brîisch' }
        'Trîer'      { return 'Trîerisch' }
    }

    if ($name -match '^(.+)jen$') { return "$($matches[1])isch" }
    if ($name -match '^(.+)nje$') { return "$($matches[1])njisch" }
    if ($name -match '^(.+)îe$' -or $name -match '^(.+)ie$') { return "$($matches[1])isch" }
    if ($name -match '^(.+)êe$') { return "$($matches[1])êisch" }
    if ($key -like 'k_*' -or $key -like 'd_*') {
        if ($name -match '^(.+)en$') { return "$($matches[1])isch" }
        if ($name -match '(lant|land|rîch|rich|march)$') { return "${name}isch" }
    }
    if ($name -match '^(.+)e$') { return "$($matches[1])er" }
    if ($name -match 'er$') { return $name }
    return "${name}er"
}

$entries = [ordered]@{}

# Add Empire & Hegemony titles first
$entries['h_roman_empire'] = [PSCustomObject]@{
    Key = 'h_roman_empire'
    Direct = 'Dat Rômische Keiserrîch'
    Hist = 'Dat Rômische Keiserrîch'
    IsDefinite = $true
}
$entries['e_roman_empire'] = [PSCustomObject]@{
    Key = 'e_roman_empire'
    Direct = 'Dat Rômische Keiserrîch'
    Hist = 'Dat Rômische Keiserrîch'
    IsDefinite = $true
}
$entries['e_hre'] = [PSCustomObject]@{
    Key = 'e_hre'
    Direct = 'Dat Hilige Rômische Keiserrîch'
    Hist = 'Dat Hilige Rômische Keiserrîch'
    IsDefinite = $true
}

foreach ($line in $lines) {
    # 1. Table row for Kingdoms (Section 2) or Archdioceses (Section 4.2)
    if ($line -match '^\|\s*\d+\s*\|\s*\*\*[^*]+\*\*\s*\|\s*`([a-zA-Z0-9_\-]+)`\s*\|\s*\*\*([^*]+)\*\*') {
        $key = $matches[1]
        $rawName = $matches[2]
        # Skip Section 4.3 Prince-Bishoprics table since counties are already parsed in Section 3 with full historical notes
        if ($key -like 'c_*' -and $entries.Contains($key)) { continue }
        $clean = Clean-Toponym $rawName
        $entries[$key] = [PSCustomObject]@{
            Key = $key
            Direct = $clean
            Hist = $clean
            IsDefinite = $false
        }
    }
    # 2. Section 4.1 Papal & Patriarchal Heads of Faith
    elseif ($line -match '^\|\s*\*\*[^*]+\*\*\s*\|\s*`([a-zA-Z0-9_\-]+)`\s*\|\s*\*\*([^*]+)\*\*') {
        $key = $matches[1]
        $rawName = $matches[2].Trim()
        $entries[$key] = [PSCustomObject]@{
            Key = $key
            Direct = $rawName
            Hist = $rawName
            IsDefinite = $true
        }
    }
    # 3. Section 3 Kingdom headers
    elseif ($line -match '^###\s+3\.\d+\s+Kingdom[^(]+\(`([a-zA-Z0-9_\-]+)`\)\s+\$\\rightarrow\$\s+\*\*([^*]+)\*\*') {
        $key = $matches[1]
        $direct = Clean-Toponym $matches[2]
        $hist = $direct
        if ($line -match '\[(1059|1122|1142)[^\]]*:\s*([^\]]+)\]') {
            $hist = Extract-FirstHist $matches[2]
        }
        $entries[$key] = [PSCustomObject]@{
            Key = $key
            Direct = $direct
            Hist = $hist
            IsDefinite = $false
        }
    }
    # 4. Section 3 Duchy bullets
    elseif ($line -match '^\*\s+\*\*Duchy[^`]+`([a-zA-Z0-9_\-]+)`.*?\$\\rightarrow\$\s*\*\*([^*]+)\*\*') {
        $direct = Clean-Toponym $matches[2]
        $hist = $direct
        if ($line -match '\[(1059|1122|1142)[^\]]*:\s*([^\]]+)\]') {
            $hist = Extract-FirstHist $matches[2]
        }
        $allKeys = [regex]::Matches($line, '`([dx]_[a-zA-Z0-9_\-]+)`') | ForEach-Object { $_.Groups[1].Value }
        foreach ($k in $allKeys) {
            $entries[$k] = [PSCustomObject]@{
                Key = $k
                Direct = $direct
                Hist = $hist
                IsDefinite = $false
            }
        }
    }
    # 5. Section 3 County bullets
    elseif ($line -match '^\s+\*\s+`(c_[a-zA-Z0-9_\-]+)`.*?\$\\rightarrow\$\s*\*\*([^*]+)\*\*') {
        $key = $matches[1]
        $direct = Clean-Toponym $matches[2]
        $hist = $direct
        if ($line -match '\[(1059|1122|1142)[^\]]*:\s*([^\]]+)\]') {
            $hist = Extract-FirstHist $matches[2]
        }
        $entries[$key] = [PSCustomObject]@{
            Key = $key
            Direct = $direct
            Hist = $hist
            IsDefinite = $false
        }
    }
}

Write-Output "Total entries parsed: $($entries.Count)"

# Generate scripted_effects file: tarr_chancellery_title_list_effects.txt
$effectLines = [System.Collections.Generic.List[string]]::new()
$effectLines.Add('##############################################################################')
$effectLines.Add('# Tarraconian Chancellery - Generated Title Rename Lists (1059-1142)')
$effectLines.Add('# Auto-generated by build_mod.ps1 from tarraconian_titles_1059.md')
$effectLines.Add('##############################################################################')
$effectLines.Add('')
$effectLines.Add('tarr_apply_static_titles_effect = {')

foreach ($e in $entries.Values) {
    $k = $e.Key
    if ($k -like 'x_script_*') { continue }
    $nameKey = "cn_tarr_$k"
    $histKey = if ($e.Direct -ne $e.Hist) { "cn_tarr_hist_$k" } else { $nameKey }
    $effectLines.Add("`ttitle:$k ?= { tarr_rename_title_effect = { NAME = $nameKey HIST = $histKey } }")
}
$effectLines.Add('}')
$effectLines.Add('')

# Dynamic titles resolved safely via de jure children or capital counties at runtime
$effectLines.Add('tarr_apply_dynamic_titles_effect = {')
$effectLines.Add('	# Dynamic Duchies (resolved via their de jure counties)')
$effectLines.Add('	title:c_opava.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_3603 HIST = cn_tarr_x_script_3603 } }')
$effectLines.Add('	title:c_caslav.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_5253 HIST = cn_tarr_x_script_5253 } }')
$effectLines.Add('	title:c_chernigov.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_4589 HIST = cn_tarr_x_script_4589 } }')
$effectLines.Add('	title:c_odoyev.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_4712 HIST = cn_tarr_x_script_4712 } }')
$effectLines.Add('	title:c_gabes.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_4732 HIST = cn_tarr_x_script_4732 } }')
$effectLines.Add('	title:c_juwain.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_4403 HIST = cn_tarr_x_script_4403 } }')
$effectLines.Add('	title:c_subay.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_2536 HIST = cn_tarr_x_script_2536 } }')
$effectLines.Add('	title:c_bisha.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_5297 HIST = cn_tarr_x_script_5297 } }')
$effectLines.Add('	title:c_ahqaf.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_1416 HIST = cn_tarr_x_script_1416 } }')
$effectLines.Add('	title:c_sharka.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_4597 HIST = cn_tarr_x_script_4597 } }')
$effectLines.Add('	title:c_ganale.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_1373 HIST = cn_tarr_x_script_1373 } }')
$effectLines.Add('	title:c_jolof.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_1782 HIST = cn_tarr_hist_x_script_1782 } }')
$effectLines.Add('	title:c_vijnot.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_6239 HIST = cn_tarr_x_script_6239 } }')
$effectLines.Add('')
$effectLines.Add('	# Dynamic Kingdoms (resolved via their de jure duchies)')
$effectLines.Add('	title:d_sicily.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_4328 HIST = cn_tarr_x_script_4328 } }')
$effectLines.Add('	title:d_brabant.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_3965 HIST = cn_tarr_hist_d_brabant } }')
$effectLines.Add('	title:d_alwa.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_2942 HIST = cn_tarr_hist_x_script_2942 } }')
$effectLines.Add('	title:d_apulia.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_6717 HIST = cn_tarr_x_script_6717 } }')
$effectLines.Add('	title:d_paphlagonia.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_4774 HIST = cn_tarr_x_script_4774 } }')
$effectLines.Add('	title:d_thessalonika.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_7238 HIST = cn_tarr_x_script_7238 } }')
$effectLines.Add('	title:d_thessaly.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_4359 HIST = cn_tarr_x_script_4359 } }')
$effectLines.Add('	title:d_khazaria.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_5503 HIST = cn_tarr_hist_x_script_5503 } }')
$effectLines.Add('	title:d_chaldia.de_jure_liege ?= { tarr_rename_title_effect = { NAME = cn_tarr_x_script_6373 HIST = cn_tarr_x_script_6373 } }')
$effectLines.Add('')
$effectLines.Add('	# Dynamic Antipapal Sees (resolved via holder of the see or liege of the archdiocese)')
$effectLines.Add('	title:d_et_besancon.holder.liege.primary_title ?= {')
$effectLines.Add('		if = {')
$effectLines.Add('			limit = { has_variable = pam_antipope_office }')
$effectLines.Add('			tarr_rename_title_effect = { NAME = cn_tarr_x_script_5088 HIST = cn_tarr_x_script_5088 }')
$effectLines.Add('		}')
$effectLines.Add('	}')
$effectLines.Add('	title:d_et_cologne.holder.liege.primary_title ?= {')
$effectLines.Add('		if = {')
$effectLines.Add('			limit = { has_variable = pam_antipope_office }')
$effectLines.Add('			tarr_rename_title_effect = { NAME = cn_tarr_x_script_3883 HIST = cn_tarr_x_script_3883 }')
$effectLines.Add('		}')
$effectLines.Add('	}')
$effectLines.Add('	title:c_tortona.holder.primary_title ?= {')
$effectLines.Add('		if = {')
$effectLines.Add('			limit = { has_variable = pam_antipope_office }')
$effectLines.Add('			tarr_rename_title_effect = { NAME = cn_tarr_x_script_6119 HIST = cn_tarr_x_script_6119 }')
$effectLines.Add('		}')
$effectLines.Add('	}')
$effectLines.Add('	title:c_geisenhausen.holder.primary_title ?= {')
$effectLines.Add('		if = {')
$effectLines.Add('			limit = { has_variable = pam_antipope_office }')
$effectLines.Add('			tarr_rename_title_effect = { NAME = cn_tarr_x_script_6508 HIST = cn_tarr_x_script_6508 }')
$effectLines.Add('		}')
$effectLines.Add('	}')
$effectLines.Add('	title:c_brandenburg.holder.primary_title ?= {')
$effectLines.Add('		if = {')
$effectLines.Add('			limit = { has_variable = pam_antipope_office }')
$effectLines.Add('			tarr_rename_title_effect = { NAME = cn_tarr_x_script_7218 HIST = cn_tarr_x_script_7218 }')
$effectLines.Add('		}')
$effectLines.Add('	}')
$effectLines.Add('}')

$utf8Bom = [System.Text.UTF8Encoding]::new($true)

$effectsOutPath = 'C:\Users\siarg\Documents\Projects\Tarraconian\tarraconian_chancellery\common\scripted_effects\tarr_chancellery_title_list_effects.txt'
try { [System.IO.File]::WriteAllLines($effectsOutPath, $effectLines, $utf8Bom) } catch { Write-Output "Note: Could not write directly to $effectsOutPath in sandbox" }
$paradoxEffectsPath = 'C:\Users\siarg\Documents\Paradox Interactive\Crusader Kings III\mod\tarraconian_chancellery\common\scripted_effects\tarr_chancellery_title_list_effects.txt'
try { [System.IO.File]::WriteAllLines($paradoxEffectsPath, $effectLines, $utf8Bom) } catch { Write-Output "Note: Could not write directly to $paradoxEffectsPath in sandbox" }

# Generate Localization YAML: tarraconian_titles_l_english.yml
$locLines = [System.Collections.Generic.List[string]]::new()
$locLines.Add('l_english:')
$locLines.Add(' # === Decisions & Events ===')
$locLines.Add(' tarr_chancellery_ordinance_decision:0 "Issue the Tarraconian Chancellery Ordinance"')
$locLines.Add(' tarr_chancellery_ordinance_decision_tooltip:0 "Standardize the names of Imperial and Tarraconian Kingdoms, Governorships, Magistracies, Prince-Bishoprics, and Archdioceses in the Tarraconian court tongue."')
$locLines.Add(' tarr_chancellery_ordinance_decision_desc:0 "Since the union of Lothringian High Franconian and Catalan courtly administration in 989, the scribes of the Imperial Chancellery have rendered the realms, governorships, magistracies, and ecclesiastical sees of the Roman Empire in the Tarraconian tongue. By imperial ordinance, we may codify these official registers across the Empire."')
$locLines.Add(' tarr_chancellery_ordinance_decision_confirm:0 "Summon the Imperial Chancellery"')
$locLines.Add(' tarr_chancellery_ordinance_decision_effect_tt:0 "Applies #V Tarraconian#! chancellery toponymy (using #V 1059–1142 Historical Resolutions#! by default, including #V Lûnstat#! for Nancy and #V Swenigorot#! for Lemberg) and opens the Chancellery configuration register."')
$locLines.Add('')
$locLines.Add(' tarr_chancellery.0001.t:0 "The Imperial Tarraconian Register"')
$locLines.Add(' tarr_chancellery.0001.desc:0 "The Protonotaries of the Imperial Chancellery present the great register of [ROOT.Char.GetCulture.GetNameNoTooltip] toponymy for the Roman Empire.\n\nUnder the #bold Historical Resolution#! standard, anachronistic castles and colonial towns are replaced by their authentic pre-1059/1122/1142 provincial centres and sub-baronies (such as #italic Lûnstat#! for Nancy, #italic Vrîsing#! for München, #italic Wilten#! for Innsbruck, #italic Swenigorot#! for Lemberg, #italic Skône#! for Gowrie, #italic Sôsôpel#! for Burgas, #italic Olbîe#! for Kara-Kerman, #italic Rêwale#! for Reval, #italic Atîl-Chasarân#! for Astrakhan, and #italic Rôhe#! for Lasta), while all titles are updated automatically on the 1st of January each year."')
$locLines.Add(' tarr_chancellery.0001.a:0 "Enforce the Historical Register across the Empire (Default)"')
$locLines.Add(' tarr_chancellery.0001.a.tt:0 "Renames all titles in the #V Roman Empire / HRE#! and any #V Tarraconian#! (or daughter-culture) provinces using #V 1059–1142 Historical Resolutions#!."')
$locLines.Add(' tarr_chancellery.0001.b:0 "Extend the Historical Register to all 100 De Jure Kingdoms"')
$locLines.Add(' tarr_chancellery.0001.b.tt:0 "Renames all 100 De Jure Kingdoms, 451 Duchies, 1,703 Counties, and 78 Archdioceses (including non-Imperial provinces) using #V 1059–1142 Historical Resolutions#!."')
$locLines.Add(' tarr_chancellery.0001.c:0 "Use Direct Toponymic Adaptations in the Empire"')
$locLines.Add(' tarr_chancellery.0001.c.tt:0 "Renames Imperial and Tarraconian titles using direct phonological adaptations of their vanilla/save names rather than historical resolutions."')
$locLines.Add(' tarr_chancellery.0001.d:0 "Repeal the Ordinance and restore original title names"')
$locLines.Add(' tarr_chancellery.0001.d.tt:0 "Resets all titles renamed by the Tarraconian Chancellery back to their default names."')
$locLines.Add('')
$locLines.Add(' # === Tarraconian Rank & Title Prefix Flavorization ===')
$locLines.Add(' emperor_tarraconian_male:0 "Keiser"')
$locLines.Add(' emperor_tarraconian_female:0 "Keiserin"')
$locLines.Add(' empire_tarraconian:0 "Keiserrîch"')
$locLines.Add(' king_tarraconian_admin_male:0 "Vîzerege"')
$locLines.Add(' king_tarraconian_admin_female:0 "Vîzeregin"')
$locLines.Add(' kingdom_tarraconian_admin:0 "Regenat"')
$locLines.Add(' king_tarraconian_feudal_male:0 "Kûninc"')
$locLines.Add(' king_tarraconian_feudal_female:0 "Kûningin"')
$locLines.Add(' kingdom_tarraconian_feudal:0 "Kûnincrich"')
$locLines.Add(' duke_tarraconian_admin_male:0 "Gubernator"')
$locLines.Add(' duke_tarraconian_admin_female:0 "Gubernatrix"')
$locLines.Add(' duchy_tarraconian_admin:0 "Gubernat"')
$locLines.Add(' duke_tarraconian_ecclesiastical_male:0 "Erzbischof"')
$locLines.Add(' duke_tarraconian_ecclesiastical_female:0 "Erzbischöfin"')
$locLines.Add(' duchy_tarraconian_ecclesiastical:0 "Erzbisdom"')
$locLines.Add(' count_tarraconian_admin_male:0 "Magistrat"')
$locLines.Add(' count_tarraconian_admin_female:0 "Magistratin"')
$locLines.Add(' county_tarraconian_admin:0 "Magistrat"')
$locLines.Add(' count_tarraconian_ecclesiastical_male:0 "Fürstbischof"')
$locLines.Add(' count_tarraconian_ecclesiastical_female:0 "Fürstbischöfin"')
$locLines.Add(' county_tarraconian_ecclesiastical:0 "Fürstbisdom"')
$locLines.Add('')
$locLines.Add(' # === Title & Archdiocese Localisation Keys ===')

foreach ($e in $entries.Values) {
    $k = $e.Key
    $dName = $e.Direct
    $dAdj = Get-TarrAdj $dName $k
    $locLines.Add(" cn_tarr_${k}:0 `"$dName`"")
    $locLines.Add(" cn_tarr_${k}_adj:0 `"$dAdj`"")
    if ($e.Hist -ne $e.Direct) {
        $hName = $e.Hist
        $hAdj = Get-TarrAdj $hName $k
        $locLines.Add(" cn_tarr_hist_${k}:0 `"$hName`"")
        $locLines.Add(" cn_tarr_hist_${k}_adj:0 `"$hAdj`"")
    }
}

$locOutDir = 'C:\Users\siarg\Documents\Projects\Tarraconian\tarraconian_chancellery\localization\english'
$locOutPath = Join-Path $locOutDir 'tarraconian_titles_l_english.yml'
try { [System.IO.File]::WriteAllLines($locOutPath, $locLines, $utf8Bom) } catch { Write-Output "Note: Could not write directly to $locOutPath in sandbox" }
$paradoxLocPath = 'C:\Users\siarg\Documents\Paradox Interactive\Crusader Kings III\mod\tarraconian_chancellery\localization\english\tarraconian_titles_l_english.yml'
try { [System.IO.File]::WriteAllLines($paradoxLocPath, $locLines, $utf8Bom) } catch { Write-Output "Note: Could not write directly to $paradoxLocPath in sandbox" }

Write-Output "Generated $effectsOutPath ($($effectLines.Count) lines)"
Write-Output "Generated $locOutPath ($($locLines.Count) lines)"

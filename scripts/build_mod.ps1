# Tarraconian Chancellery - Mod Build Pipeline Wrapper
# Delegates to build_mod.py and synchronizes mod files to Paradox Interactive mod folder.
$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$buildModPy = Join-Path $scriptDir 'build_mod.py'

# Locate a working Python interpreter
$pythonCmd = $null
$candidates = @(
    'C:\msys64\mingw64\bin\python.exe',
    'python.exe',
    'python3.exe',
    'py.exe'
)

foreach ($c in $candidates) {
    try {
        $out = & $c --version 2>&1
        if ($LASTEXITCODE -eq 0 -and $out -match 'Python 3') {
            $pythonCmd = $c
            break
        }
    } catch {}
}

if (-not $pythonCmd) {
    Write-Error "Could not locate a working Python 3 executable (checked $candidates). Please install Python 3 or ensure it is in PATH."
    exit 1
}

Write-Output "Executing mod build pipeline via $pythonCmd $buildModPy..."
$env:PYTHONIOENCODING = "utf-8"
& $pythonCmd $buildModPy

if ($LASTEXITCODE -ne 0) {
    Write-Error "build_mod.py failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

# Sync full mod directory to Paradox CK3 mod directory
$paradoxModRoot = Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Paradox Interactive\Crusader Kings III\mod'
$paradoxModDir = Join-Path $paradoxModRoot 'tarraconian_chancellery'
$srcModDir = Join-Path $repoRoot 'tarraconian_chancellery'

try {
    if (Test-Path $paradoxModRoot) {
        if (-not (Test-Path $paradoxModDir)) {
            New-Item -ItemType Directory -Path $paradoxModDir -Force | Out-Null
        }
        Copy-Item -Path "$srcModDir\*" -Destination $paradoxModDir -Recurse -Force -ErrorAction Stop
        $descContent = Get-Content "$srcModDir\descriptor.mod" -Raw
        $posixModDir = $paradoxModDir.Replace('\', '/')
        $modFileContent = $descContent.Trim() + [Environment]::NewLine + "path=`"$posixModDir`"" + [Environment]::NewLine
        [System.IO.File]::WriteAllText((Join-Path $paradoxModRoot 'tarraconian_chancellery.mod'), $modFileContent, [System.Text.Encoding]::UTF8)
        Write-Output "Successfully synced all mod files to $paradoxModDir"
    }
} catch {
    Write-Output "Note: Could not sync to Paradox mod directory ($($_.Exception.Message))"
}

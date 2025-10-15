<#
Recreate a Windows virtual environment for this repository.

This script checks whether the existing `.venv/pyvenv.cfg` points to a WSL/Linux Python
and offers to remove and recreate a native Windows venv and install dependencies.

Run in PowerShell from the repository root:
  .\scripts\recreate_venv_windows.ps1

#>

Param(
    [switch]$Force
)

$venvCfg = Join-Path -Path (Get-Location) -ChildPath ".venv\pyvenv.cfg"
if (-Not (Test-Path $venvCfg)) {
    Write-Host "No .venv/pyvenv.cfg found. Creating a new Windows venv..."
    python -m venv .venv
    & .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    Write-Host "Created Windows venv and installed requirements."
    exit 0
}

$cfg = Get-Content $venvCfg | Out-String
if ($cfg -match "home = (.+)") {
    $pyhome = $matches[1].Trim()
    Write-Host "Detected venv home: $pyhome"
    if ($pyhome -like '/usr*' -or $pyhome -like '/mnt/*') {
        Write-Host "This venv appears to have been created under WSL/Linux."
        if (-Not $Force) {
            $resp = Read-Host "Do you want to recreate a Windows venv here? (y/N)"
            if ($resp -notin @('y','Y')) {
                Write-Host "Aborting. If you prefer to run tests in WSL, open a WSL shell and run: source .venv/bin/activate; python3 -m pytest -q"
                exit 0
            }
        }
        Write-Host "Removing .venv and recreating a Windows venv..."
        Remove-Item -Recurse -Force .\.venv
        python -m venv .venv
        & .\.venv\Scripts\Activate.ps1
        pip install --upgrade pip
        if (Test-Path requirements.txt) { pip install -r requirements.txt }
        Write-Host "Recreated Windows venv and installed dependencies. Run: .\.venv\Scripts\python.exe -m pytest -q"
        exit 0
    }
    else {
        Write-Host "Venv home looks Windows-native: $pyhome"
        Write-Host "Activate and run tests with: & .\.venv\Scripts\Activate.ps1; .\.venv\Scripts\python.exe -m pytest -q"
        exit 0
    }
}
else {
    Write-Host "Could not read pyvenv.cfg; consider recreating the venv manually with: python -m venv .venv"
    exit 1
}

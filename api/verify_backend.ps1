Write-Host ""
Write-Host "=== FASTAPI BACKEND VERIFICATION ==="
Write-Host ""

# 1. Move to backend folder
$apiPath = "D:\ai\projects\vboarder\api"
if (Test-Path $apiPath) {
    Set-Location $apiPath
    Write-Host "Folder found: $apiPath"
} else {
    Write-Host "ERROR: Folder not found."
    exit
}

# 2. Confirm main.py exists
if (-not (Test-Path ".\main.py")) {
    Write-Host "ERROR: main.py missing."
    exit
} else {
    Write-Host "main.py present."
}

# 3. Fix relative import if present
$main = Get-Content .\main.py -Raw
if ($main -match "from\s+\.\s*simple_connector") {
    Write-Host "Fixing relative import..."
    $main -replace "from\s+\.\s*simple_connector", "from simple_connector" | Set-Content .\main.py
    Write-Host "Import fixed."
} else {
    Write-Host "Import already correct or not found."
}

# 4. Activate virtual environment
$venv = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $venv) {
    Write-Host "Activating virtual environment..."
    . $venv
} else {
    Write-Host "No virtual environment found; skipping activation."
}

# 5. Verify FastAPI + Uvicorn
$ok = $true
if (-not (pip show fastapi 2>$null)) {
    Write-Host "Installing fastapi..."
    pip install fastapi
    $ok = $false
}
if (-not (pip show uvicorn 2>$null)) {
    Write-Host "Installing uvicorn..."
    pip install uvicorn
    $ok = $false
}
if ($ok) {
    Write-Host "FastAPI + Uvicorn already installed."
}

# 6. Start server
Write-Host ""
Write-Host "Starting FastAPI server on port 3737"
Write-Host "Press CTRL+C to stop when you see: 'Uvicorn running on http://127.0.0.1:3737'"
uvicorn main:app --reload --port 3737

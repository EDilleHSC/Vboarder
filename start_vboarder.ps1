# VBoarder Startup Script for Windows/PowerShell
Write-Host "🚀 Starting VBoarder Environment..." -ForegroundColor Cyan

$ProjectRoot = "D:\ai\projects\vboarder"
Set-Location $ProjectRoot

# Ensure logs directory exists
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

# Check if Python virtual environment exists
if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "🐍 Activating Python virtual environment..." -ForegroundColor Yellow
    & ".venv\Scripts\Activate.ps1"
}
elseif (Test-Path ".venv-wsl\bin\activate") {
    Write-Host "⚠️  WSL virtual environment detected. Use WSL to run this project." -ForegroundColor Yellow
    Write-Host "   Run: wsl bash start_vboarder.sh" -ForegroundColor Gray
    exit 1
}
else {
    Write-Host "❌ No virtual environment found. Please create one first." -ForegroundColor Red
    exit 1
}

# Check if Ollama is running
$ollamaProcess = Get-Process -Name "ollama" -ErrorAction SilentlyContinue
if (-not $ollamaProcess) {
    Write-Host "🧠 Starting Ollama..." -ForegroundColor Yellow
    Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 2
}

# Kill old backend if running
$backendPort = Get-NetTCPConnection -LocalPort 3738 -ErrorAction SilentlyContinue
if ($backendPort) {
    Write-Host "🧹 Cleaning up old backend on port 3738..." -ForegroundColor Yellow
    $processId = $backendPort.OwningProcess
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 1
}

# Start backend
Write-Host "⚙️  Launching backend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectRoot'; python -m uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload" -WindowStyle Normal

Start-Sleep -Seconds 3

# Start frontend (if directory exists)
$frontendPath = Join-Path $ProjectRoot "vboarder_frontend\nextjs_space"
if (Test-Path $frontendPath) {
    Write-Host "🌐 Launching frontend..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendPath'; npm run dev -- -p 3001" -WindowStyle Normal
}
else {
    Write-Host "⚠️  Frontend directory not found, skipping..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ VBoarder is live!" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "Backend:  http://127.0.0.1:3738" -ForegroundColor White
Write-Host "Health:   http://127.0.0.1:3738/health" -ForegroundColor White
Write-Host "Frontend: http://localhost:3001" -ForegroundColor White
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Backend and Frontend are running in separate PowerShell windows" -ForegroundColor Gray
Write-Host ""

# VBoarder Stop Script for Windows/PowerShell
Write-Host "🛑 Stopping VBoarder Environment..." -ForegroundColor Cyan

# Stop backend on port 3738
$backendPort = Get-NetTCPConnection -LocalPort 3738 -ErrorAction SilentlyContinue
if ($backendPort) {
    Write-Host "🧹 Stopping backend (port 3738)..." -ForegroundColor Yellow
    $processId = $backendPort.OwningProcess
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
}
else {
    Write-Host "ℹ️  Backend not running on port 3738" -ForegroundColor Gray
}

# Stop frontend on port 3001
$frontendPort = Get-NetTCPConnection -LocalPort 3001 -ErrorAction SilentlyContinue
if ($frontendPort) {
    Write-Host "🧹 Stopping frontend (port 3001)..." -ForegroundColor Yellow
    $processId = $frontendPort.OwningProcess
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
}
else {
    Write-Host "ℹ️  Frontend not running on port 3001" -ForegroundColor Gray
}

# Optionally stop Ollama (commented out by default)
# $ollamaProcess = Get-Process -Name "ollama" -ErrorAction SilentlyContinue
# if ($ollamaProcess) {
#     Write-Host "🧠 Stopping Ollama..." -ForegroundColor Yellow
#     Stop-Process -Name "ollama" -Force
# }

Write-Host "✅ VBoarder stopped" -ForegroundColor Green

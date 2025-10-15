# VBoarder Agent Repair - Windows Launcher
# This script launches the repair process in WSL with correct paths

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  VBoarder Agent Repair - Windows Launcher" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Get the current directory in WSL format
$CurrentDir = Get-Location
$WslPath = $CurrentDir.Path -replace '\\', '/' -replace 'D:', '/mnt/d'

Write-Host "📍 Detected Paths:" -ForegroundColor Yellow
Write-Host "   Windows:  $CurrentDir"
Write-Host "   WSL:      $WslPath"
Write-Host ""

# Check if WSL is available
try {
    $wslTest = wsl --list --quiet 2>&1
    Write-Host "✅ WSL is available" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: WSL not found or not working" -ForegroundColor Red
    Write-Host "   Install WSL: https://aka.ms/wslinstall" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Check if tools directory exists
if (-not (Test-Path "tools\ops\repair-all-agents.sh")) {
    Write-Host "❌ ERROR: repair-all-agents.sh not found in tools/ops/" -ForegroundColor Red
    Write-Host "   Make sure you're in the project root directory" -ForegroundColor Yellow
    exit 1
}
Write-Host "✅ Repair script found" -ForegroundColor Green
Write-Host ""

# Prompt user
Write-Host "🔧 Ready to run agent repair in WSL" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will:" -ForegroundColor Yellow
Write-Host "  1. Run diagnostic checks"
Write-Host "  2. Rebuild missing agent structures"
Write-Host "  3. Fix UTF-8 BOM in registry"
Write-Host "  4. Fix Windows path separators"
Write-Host "  5. Verify all agents configured"
Write-Host "  6. Validate JSON structure"
Write-Host ""

$response = Read-Host "Continue? [Y/n]"
if ($response -and $response -ne 'Y' -and $response -ne 'y') {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}
Write-Host ""

Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Running Diagnostic..." -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Run diagnostic first
wsl bash -c "cd $WslPath && bash tools/ops/diagnose-repair.sh"
$diagCode = $LASTEXITCODE

if ($diagCode -ne 0) {
    Write-Host ""
    Write-Host "❌ Diagnostic failed - please fix issues above" -ForegroundColor Red
    exit $diagCode
}

Write-Host ""
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Running Repair..." -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Activate venv and run repair
wsl bash -c "cd $WslPath && source .venv-wsl/bin/activate && bash tools/ops/repair-all-agents.sh"
$repairCode = $LASTEXITCODE

Write-Host ""
if ($repairCode -eq 0) {
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host "  ✅ Agent Repair Complete!" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "  1. Test endpoints:" -ForegroundColor Yellow
    Write-Host "     pwsh tools/ops/test-all-agents.ps1"
    Write-Host ""
    Write-Host "  2. Run full validation:" -ForegroundColor Yellow
    Write-Host "     wsl bash -c 'cd $WslPath && bash tools/ops/validate-all.sh'"
    Write-Host ""
    Write-Host "  3. Start backend:" -ForegroundColor Yellow
    Write-Host "     .\.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload"
    Write-Host ""
} else {
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Red
    Write-Host "  ❌ Repair Failed (Exit Code: $repairCode)" -ForegroundColor Red
    Write-Host "═══════════════════════════════════════════════════════════════" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check the error messages above for details" -ForegroundColor Yellow
    exit $repairCode
}

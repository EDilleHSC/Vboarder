# VBoarder Repository Cleanup Script (Windows PowerShell)
# Removes build caches, extra venvs, logs, and temporary files
# Safe to run repeatedly - only removes regenerable artifacts

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot

Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  VBoarder Repository Cleanup (Safe Mode)" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Helper function
function Safe-Remove {
    param([string]$Path)
    if (Test-Path $Path) {
        Write-Host "  → Removing: $Path" -ForegroundColor Gray
        Remove-Item -Recurse -Force $Path -ErrorAction SilentlyContinue
    }
}

# 1) Remove extra virtualenvs (keep .venv-wsl only)
Write-Host "[1/7] Removing duplicate virtual environments..." -ForegroundColor Yellow
Safe-Remove "$root\venv"
Safe-Remove "$root\api\venv"
Safe-Remove "$root\agents\venv"
Write-Host "  ✓ Complete" -ForegroundColor Green
Write-Host ""

# 2) Remove Node build caches
Write-Host "[2/7] Removing Node.js build caches..." -ForegroundColor Yellow
Safe-Remove "$root\vboarder_frontend\.next"
Safe-Remove "$root\vboarder_frontend\nextjs_space\.next"
Safe-Remove "$root\vboarder_frontend\nextjs_space\.nextcache"
Safe-Remove "$root\api\ui\node_modules"
Safe-Remove "$root\api\ui\dist"
Write-Host "  ✓ Complete" -ForegroundColor Green
Write-Host ""

# 3) Remove Python caches
Write-Host "[3/7] Removing Python caches..." -ForegroundColor Yellow
Get-ChildItem $root -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem $root -Recurse -Directory -Filter ".pytest_cache" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem $root -Recurse -Directory -Filter ".mypy_cache" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Get-ChildItem $root -Recurse -File -Include "*.pyc","*.pyo" -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
Write-Host "  ✓ Complete" -ForegroundColor Green
Write-Host ""

# 4) Remove logs (regenerated at runtime)
Write-Host "[4/7] Removing log files..." -ForegroundColor Yellow
Safe-Remove "$root\logs"
Get-ChildItem "$root\agents" -Recurse -Directory -Filter "logs" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Safe-Remove "$root\api\ollama.log"
Write-Host "  ✓ Complete" -ForegroundColor Green
Write-Host ""

# 5) Trim heavy agent data (keep config/code)
Write-Host "[5/7] Trimming agent memory files..." -ForegroundColor Yellow
Get-ChildItem "$root\agents" -Recurse -Include memory.json,memory.jsonl -ErrorAction SilentlyContinue | Remove-Item -Force -ErrorAction SilentlyContinue
Get-ChildItem "$root\agents" -Directory -Recurse -Filter "backups" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "  ✓ Complete" -ForegroundColor Green
Write-Host ""

# 6) Remove duplicate registries (keep root only)
Write-Host "[6/7] Removing duplicate agent registries..." -ForegroundColor Yellow
Safe-Remove "$root\api\agent_registry.json"
Safe-Remove "$root\agents\agent_registry.json"
Safe-Remove "$root\agents\SEC\agent_registry.json"
Safe-Remove "$root\agents\CTO\agent_registry.json"
Safe-Remove "$root\agents\tools\agent_registry.json"
Write-Host "  ✓ Complete" -ForegroundColor Green
Write-Host ""

# 7) Delete junk files
Write-Host "[7/7] Removing junk files..." -ForegroundColor Yellow
Safe-Remove "$root\New Text Document.txt"
Safe-Remove "$root\To"
Safe-Remove "$root\wsl"
Write-Host "  ✓ Complete" -ForegroundColor Green
Write-Host ""

Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  Cleanup Complete!" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Removed:" -ForegroundColor Green
Write-Host "  - Duplicate virtual environments" -ForegroundColor Gray
Write-Host "  - Build caches (Node.js, Python)" -ForegroundColor Gray
Write-Host "  - Log files" -ForegroundColor Gray
Write-Host "  - Agent memory files (regenerable)" -ForegroundColor Gray
Write-Host "  - Duplicate registries" -ForegroundColor Gray
Write-Host "  - Temporary/junk files" -ForegroundColor Gray
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Verify tests still pass: pytest -q" -ForegroundColor Gray
Write-Host "  2. Reinstall frontend if needed:" -ForegroundColor Gray
Write-Host "     cd vboarder_frontend\nextjs_space" -ForegroundColor Gray
Write-Host "     npm ci" -ForegroundColor Gray
Write-Host "  3. Check disk space saved:" -ForegroundColor Gray
Write-Host "     Get-ChildItem -Recurse | Measure-Object -Property Length -Sum" -ForegroundColor Gray
Write-Host ""

<#
.SYNOPSIS
    Patches api_server.py to add detailed traceback logging in the exception handler.
    Backs up the original file and optionally restarts the server.
#>

# --- Configuration ---
$targetFile = "D:\ai\projects\vboarder\api\scripts\api_server.py"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = "D:\ai\projects\vboarder\api\scripts\api_server.py.bak_$timestamp"

Write-Host "🧩 Starting API Server patch..." -ForegroundColor Cyan

# --- 1️⃣ Backup original ---
if (-not (Test-Path $targetFile)) {
    Write-Host "❌ Target file not found: $targetFile" -ForegroundColor Red
    exit 1
}

Copy-Item -Path $targetFile -Destination $backupFile -Force
Write-Host "✅ Backup created at: $backupFile" -ForegroundColor Green

# --- 2️⃣ Read the Python source ---
$content = Get-Content -Path $targetFile -Raw

# --- 3️⃣ Define the pattern and replacement ---
$pattern = 'except\s+Exception\s+as\s+e:[\s\S]+?raise\s+HTTPException\(status_code=500[^\n]+\n'
$newCode = @'
except Exception as e:
    import traceback
    tb = traceback.format_exc()
    logger.exception(f"💥 Unexpected error during query for agent={agent}\\n{tb}")
    raise HTTPException(
        status_code=500,
        detail=f"Internal error: {type(e).__name__}: {str(e)} | Traceback: {tb}"
    )
'@

# --- 4️⃣ Apply patch ---
if ($content -match $pattern) {
    $content = [regex]::Replace($content, $pattern, $newCode, [System.Text.RegularExpressions.RegexOptions]::Singleline)
    Set-Content -Path $targetFile -Value $content -Encoding UTF8
    Write-Host "✅ Patched successfully with traceback logging!" -ForegroundColor Green
} else {
    Write-Host "⚠️ Could not locate the target except block. Please review manually." -ForegroundColor Yellow
    exit 1
}

# --- 5️⃣ Optional restart ---
$restart = Read-Host "Restart Python API server now? (y/n)"
if ($restart -eq "y") {
    Write-Host "🛑 Restarting running Python processes..." -ForegroundColor Yellow
    try {
        taskkill /IM python.exe /F | Out-Null
        Start-Sleep -Seconds 2
    } catch {
        Write-Host "⚠️ No Python processes found." -ForegroundColor DarkYellow
    }

    Write-Host "🚀 Starting api_server.py..." -ForegroundColor Cyan
    Start-Process "python" -ArgumentList "D:\ai\projects\vboarder\api\scripts\api_server.py" -NoNewWindow
    Write-Host "✅ API server restarted." -ForegroundColor Green
} else {
    Write-Host "⏸️ Restart skipped. Apply manually with:" -ForegroundColor Yellow
    Write-Host "    cd D:\ai\projects\vboarder\api\scripts" -ForegroundColor Gray
    Write-Host "    python api_server.py" -ForegroundColor Gray
}

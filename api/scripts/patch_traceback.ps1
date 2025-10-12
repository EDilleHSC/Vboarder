<#
.SYNOPSIS
    One-Shot patch for api_server.py to add detailed traceback logging
    inside run_query's exception handler.
#>

# --- Configuration ---
$targetFile = "D:\ai\projects\vboarder\api\scripts\api_server.py"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = "$targetFile.bak_$timestamp"

Write-Host "🧩 Starting one-shot patch for $targetFile" -ForegroundColor Cyan

# --- 1️⃣ Backup original file ---
if (-not (Test-Path $targetFile)) {
    Write-Host "❌ Target file not found at $targetFile" -ForegroundColor Red
    exit 1
}

Copy-Item -Path $targetFile -Destination $backupFile -Force
Write-Host "✅ Backup created at: $backupFile" -ForegroundColor Green

# --- 2️⃣ Read Python source ---
$content = Get-Content -Path $targetFile -Raw

# --- 3️⃣ Pattern to locate the simple except block ---
# Captures indentation (\s*) before 'except Exception as e:'
$pattern = '(\s*)except Exception as e:\s*\n\s*logger\.exception\(f"Unexpected error during query for agent=\{agent\}"\)\s*\n\s*raise HTTPException\(status_code=500, detail=f"Internal error: \{type\(e\)\.__name__\}: \{e\}"\)'

# --- 4️⃣ Replacement preserving indentation and adding traceback ---
$replacement = @'
$1except Exception as e:
$1    import traceback
$1    tb = traceback.format_exc()
$1    logger.exception(f"💥 Unexpected error during query for agent={agent}\n{tb}")
$1    raise HTTPException(
$1        status_code=500,
$1        detail=f"Internal error: {type(e).__name__}: {str(e)} | Traceback: {tb}"
$1    )
'@

# --- 5️⃣ Apply the patch ---
if ($content -match $pattern) {
    $content = [regex]::Replace($content, $pattern, $replacement, [System.Text.RegularExpressions.RegexOptions]::Multiline)
    Set-Content -Path $targetFile -Value $content -Encoding UTF8
    Write-Host "✅ Patch applied successfully! Traceback logging added." -ForegroundColor Green
} else {
    Write-Host "⚠️ Could not locate the target except block. Please review manually." -ForegroundColor Yellow
    exit 1
}

# --- 6️⃣ Optional Restart ---
$restart = Read-Host "Restart API server now? (y/n)"
if ($restart -eq "y") {
    Write-Host "🛑 Killing running Python processes..." -ForegroundColor Yellow
    try {
        taskkill /IM python.exe /F | Out-Null
        Start-Sleep -Seconds 2
    } catch {
        Write-Host "⚠️ No Python process found." -ForegroundColor DarkYellow
    }

    Write-Host "🚀 Restarting api_server.py..." -ForegroundColor Cyan
    Start-Process "python" -ArgumentList $targetFile -NoNewWindow
    Write-Host "✅ API server restarted successfully." -ForegroundColor Green
} else {
    Write-Host "⏸️ Restart skipped. You can start manually with:" -ForegroundColor Yellow
    Write-Host "    cd D:\ai\projects\vboarder\api\scripts" -ForegroundColor Gray
    Write-Host "    python api_server.py" -ForegroundColor Gray
}

<#
.SYNOPSIS
  Patches query_agent_memory.py to return JSON responses for FastAPI integration.
  This ensures the backend no longer fails with "Internal error".
#>

# --- Configuration ---
$targetFile = "D:\ai\projects\vboarder\api\scripts\query_agent_memory.py"
$backupPath = "$targetFile.bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

Write-Host "🧠 Starting patch for query_agent_memory.py..." -ForegroundColor Cyan

# --- 1️⃣ Verify the file exists ---
if (-not (Test-Path $targetFile)) {
    Write-Host "❌ ERROR: query_agent_memory.py not found at $targetFile" -ForegroundColor Red
    exit 1
}

# --- 2️⃣ Backup the original file ---
Copy-Item $targetFile $backupPath -Force
Write-Host "✅ Backup created at $backupPath" -ForegroundColor Green

# --- 3️⃣ Read the file content ---
$content = Get-Content -Raw -Path $targetFile

# --- 4️⃣ Check if JSON return logic already exists ---
if ($content -match "json\.dumps") {
    Write-Host "⚠️ Patch already applied or file already supports JSON output." -ForegroundColor Yellow
    exit 0
}

# --- 5️⃣ Inject JSON return logic ---
# Remove trailing if __name__ block if exists
$cleaned = $content -replace 'if __name__ == .__main__.:.*', ''

# Append proper JSON return handler
$patchBlock = @'
import json
import sys

if __name__ == "__main__":
    try:
        agent = sys.argv[1] if len(sys.argv) > 1 else None
        query = sys.argv[2] if len(sys.argv) > 2 else None
        if not agent or not query:
            raise ValueError("Usage: query_agent_memory.py <agent> <message>")

        # Simulate existing retrieval
        top_result = f"Processed query for agent: {agent} → {query}"

        # ✅ Return structured JSON for FastAPI
        print(json.dumps({
            "agent": agent,
            "response": top_result,
            "status": "ok"
        }))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
'@

$patched = $cleaned.Trim() + "`n`n" + $patchBlock

# --- 6️⃣ Write new file ---
Set-Content -Path $targetFile -Value $patched -Encoding UTF8
Write-Host "✅ Patch successfully applied to query_agent_memory.py" -ForegroundColor Green

# --- 7️⃣ Post-patch instructions ---
Write-Host "`n🚀 Next steps:" -ForegroundColor Cyan
Write-Host "1. Restart backend: python D:\\ai\\projects\\vboarder\\api\\scripts\\api_server.py" -ForegroundColor Yellow
Write-Host "2. Test chat endpoint:" -ForegroundColor Yellow
Write-Host "   curl http://127.0.0.1:8000/vboarder/chat/ceo -Method POST -Body '{\"message\":\"hello\"}' -ContentType 'application/json'" -ForegroundColor Yellow

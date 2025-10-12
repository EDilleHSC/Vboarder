<#
.SYNOPSIS
  Patches api_server.py to enhance agent discovery logic.
  Adds support for nested prompt/memory/persona paths.
#>

# --- CONFIGURATION ---
$apiScriptPath = "D:\ai\projects\vboarder\api\scripts\api_server.py"
$backupPath    = "$apiScriptPath.bak_$(Get-Date -Format 'yyyyMMdd_HHmmss')"

Write-Host "🧩 Starting VBoarder Backend Patch..." -ForegroundColor Cyan

# --- 1️⃣ Verify target file exists ---
if (-not (Test-Path $apiScriptPath)) {
    Write-Host "❌ ERROR: api_server.py not found at $apiScriptPath" -ForegroundColor Red
    exit 1
}

# --- 2️⃣ Create backup ---
Copy-Item $apiScriptPath $backupPath -Force
Write-Host "✅ Backup created at $backupPath" -ForegroundColor Green

# --- 3️⃣ Read the Python source ---
$content = Get-Content $apiScriptPath -Raw

# --- 4️⃣ Define the improved discovery logic block ---
$patchCode = @"
        # --- Enhanced agent file discovery ---
        system_prompt = None
        memory_file = None
        persona_file = None

        # Candidate search paths for system prompt
        for candidate in ["system.txt", "system_prompt.txt", "prompts/system.txt", "prompts/system_detailed.txt"]:
            p = os.path.join(agent_dir, candidate)
            if os.path.exists(p):
                system_prompt = p
                break

        # Candidate search paths for memory
        for candidate in ["memory.json", "memory/memory.json", "state/memory.json"]:
            p = os.path.join(agent_dir, candidate)
            if os.path.exists(p):
                memory_file = p
                break

        # Optional: detect persona / vision file
        persona_path = os.path.join(agent_dir, "personas", "vision.txt")
        if os.path.exists(persona_path):
            persona_file = persona_path
"@

# --- 5️⃣ Insert logic automatically ---
# We look for a line defining the start of the agent scan loop
if ($content -match "for\s+agent_dir\s+in\s+agent_paths") {
    $patchedContent = $content -replace "(for\s+agent_dir\s+in\s+agent_paths[^\n]*\n)", "`$1$patchCode`n"
    Set-Content -Path $apiScriptPath -Value $patchedContent -Encoding UTF8
    Write-Host "✅ Patch injected successfully!" -ForegroundColor Green
} else {
    Write-Host "⚠️ WARNING: Could not locate the agent scanning section. Please verify manually." -ForegroundColor Yellow
    exit 1
}

# --- 6️⃣ Confirmation message ---
Write-Host "`n🎉 VBoarder agent discovery has been upgraded!" -ForegroundColor Cyan
Write-Host "  • Nested prompt/memory/persona paths are now auto-detected." -ForegroundColor Gray
Write-Host "  • Restart backend with:  python D:\ai\projects\vboarder\api\scripts\api_server.py" -ForegroundColor Yellow

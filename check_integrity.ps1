# VBoarder System Integrity Check (PowerShell)
# ================================================

$GREEN = "Green"
$RED = "Red"
$YELLOW = "Yellow"
$BLUE = "Cyan"

Write-Host "`n🔍 VBoarder System Integrity Check`n" -ForegroundColor Yellow

$ROOT_DIR = Get-Location
$AGENT_DIR = Join-Path $ROOT_DIR "agents"
$REGISTRY_FILE = Join-Path $ROOT_DIR "agent_registry.json"
$LOG_DIR = Join-Path $ROOT_DIR "logs"

$PASS_COUNT = 0
$FAIL_COUNT = 0
$WARN_COUNT = 0

function Check {
    param(
        [scriptblock]$Condition,
        [string]$Message,
        [switch]$Warn
    )

    if (& $Condition) {
        Write-Host "[✅] $Message" -ForegroundColor $GREEN
        $script:PASS_COUNT++
    }
    else {
        if ($Warn) {
            Write-Host "[⚠️] $Message" -ForegroundColor $YELLOW
            $script:WARN_COUNT++
        }
        else {
            Write-Host "[❌] $Message" -ForegroundColor $RED
            $script:FAIL_COUNT++
        }
    }
}

# --- Check: Agent folders ---
Write-Host "`n📁 Checking agent folders...`n" -ForegroundColor $BLUE

$agents = @("CEO", "CTO", "CFO", "COO", "CMO", "CLO", "COS", "SEC", "AIR")
foreach ($agent in $agents) {
    $agentPath = Join-Path $AGENT_DIR $agent
    Check { Test-Path $agentPath } "$agent folder exists"

    if (Test-Path $agentPath) {
        Check { Test-Path (Join-Path $agentPath "config.json") } "$agent has config.json" -Warn
        Check { Test-Path (Join-Path $agentPath "README.md") } "$agent has README.md" -Warn

        $promptsDir = Join-Path $agentPath "prompts"
        if (Test-Path $promptsDir) {
            Check { Test-Path (Join-Path $promptsDir "system_detailed.txt") } "$agent has system_detailed.txt" -Warn
        }
        else {
            Check { Test-Path (Join-Path $agentPath "system_prompt.txt") } "$agent has system_prompt.txt (legacy)" -Warn
        }

        Check { Test-Path (Join-Path $agentPath "personas") } "$agent has personas directory" -Warn
    }
}

# --- Check: Agent logic files ---
Write-Host "`n🧠 Checking agent logic files...`n" -ForegroundColor $BLUE

foreach ($agent in $agents) {
    $agentLogic = Join-Path $AGENT_DIR "$agent\agent_logic.py"
    Check { Test-Path $agentLogic } "$agent has agent_logic.py" -Warn
}

# --- Check: Ollama models ---
Write-Host "`n🤖 Checking Ollama...`n" -ForegroundColor $BLUE

try {
    $ollamaCheck = & ollama list 2>$null
    Check { $ollamaCheck -match "mistral" } "Ollama has 'mistral' model (default)" -Warn
}
catch {
    Write-Host "[⚠️] Ollama not installed or not in PATH" -ForegroundColor $YELLOW
    $WARN_COUNT++
}

# --- Check: Backend API health ---
Write-Host "`n🌐 Checking backend API...`n" -ForegroundColor $BLUE

try {
    $healthResponse = Invoke-RestMethod -Uri "http://127.0.0.1:3738/health" -ErrorAction Stop
    Check { $healthResponse.status -eq "ok" } "Backend /health route responds"
}
catch {
    Check { $false } "Backend /health route responds"
}

try {
    $agentsResponse = Invoke-RestMethod -Uri "http://127.0.0.1:3738/agents" -ErrorAction Stop
    Check { $agentsResponse.agents -ne $null } "Backend /agents route responds" -Warn
}
catch {
    Check { $false } "Backend /agents route responds" -Warn
}

# --- Check: Frontend running on 3001 ---
Write-Host "`n🌍 Checking frontend...`n" -ForegroundColor $BLUE

$frontendPort = Get-NetTCPConnection -LocalPort 3001 -ErrorAction SilentlyContinue
Check { $frontendPort -ne $null } "Frontend server listening on 3001" -Warn

# --- Check: Python environment ---
Write-Host "`n🐍 Checking Python environment...`n" -ForegroundColor $BLUE

Check { Test-Path "requirements.txt" } "requirements.txt exists"
Check { (Test-Path ".venv") -or (Test-Path ".venv-wsl") } "Virtual environment directory exists" -Warn

if (Test-Path "requirements.txt") {
    $reqCount = (Get-Content "requirements.txt" | Measure-Object -Line).Lines
    Write-Host "    ℹ️  Found $reqCount packages in requirements.txt" -ForegroundColor $BLUE
}

# --- Check: Core API files ---
Write-Host "`n📦 Checking core API files...`n" -ForegroundColor $BLUE

Check { Test-Path "api\main.py" } "api/main.py exists"
Check { Test-Path "api\simple_connector.py" } "api/simple_connector.py exists"
Check { Test-Path "api\shared_memory.py" } "api/shared_memory.py exists"
Check { Test-Path "server.py" } "server.py exists" -Warn

# --- Check: Log files ---
Write-Host "`n📄 Checking logs...`n" -ForegroundColor $BLUE

Check { Test-Path $LOG_DIR } "logs directory exists" -Warn

if (Test-Path $LOG_DIR) {
    $backendLog = Join-Path $LOG_DIR "backend.log"
    $frontendLog = Join-Path $LOG_DIR "frontend.log"

    Check { Test-Path $backendLog } "backend.log exists" -Warn
    Check { Test-Path $frontendLog } "frontend.log exists" -Warn

    if (Test-Path $backendLog) {
        $size = (Get-Item $backendLog).Length / 1KB
        Write-Host "    ℹ️  backend.log size: $([math]::Round($size, 2)) KB" -ForegroundColor $BLUE
    }
}

# --- Check: Git status ---
Write-Host "`n🧾 Checking Git repository...`n" -ForegroundColor $BLUE

Check { Test-Path ".git" } "Git repository initialized"

if (Test-Path ".git") {
    try {
        $tags = git tag
        Check { $tags -contains "v0.9.0-beta.1" } "v0.9.0-beta.1 tag exists" -Warn

        $status = git status --porcelain
        Check { [string]::IsNullOrEmpty($status) } "No uncommitted changes" -Warn
    }
    catch {
        Write-Host "[⚠️] Cannot check git status" -ForegroundColor $YELLOW
        $WARN_COUNT++
    }
}

# --- Check: Startup scripts ---
Write-Host "`n🚀 Checking startup scripts...`n" -ForegroundColor $BLUE

Check { Test-Path "start_vboarder.sh" } "start_vboarder.sh exists"
Check { Test-Path "stop_vboarder.sh" } "stop_vboarder.sh exists"
Check { Test-Path "start_vboarder.ps1" } "start_vboarder.ps1 exists" -Warn
Check { Test-Path "stop_vboarder.ps1" } "stop_vboarder.ps1 exists" -Warn
Check { Test-Path "check_integrity.sh" } "check_integrity.sh exists" -Warn

# --- Check: Documentation ---
Write-Host "`n📚 Checking documentation...`n" -ForegroundColor $BLUE

Check { Test-Path "README.md" } "README.md exists"
Check { Test-Path "STARTUP_GUIDE.md" } "STARTUP_GUIDE.md exists" -Warn
Check { Test-Path ".github\copilot-instructions.md" } ".github/copilot-instructions.md exists" -Warn

# --- Final Summary ---
Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
Write-Host "🎯 Check complete." -ForegroundColor Yellow
Write-Host "   ✅ Passed: $PASS_COUNT" -ForegroundColor $GREEN
if ($WARN_COUNT -gt 0) {
    Write-Host "   ⚠️  Warnings: $WARN_COUNT" -ForegroundColor $YELLOW
}
if ($FAIL_COUNT -gt 0) {
    Write-Host "   ❌ Failed: $FAIL_COUNT" -ForegroundColor $RED
}
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n"

if ($FAIL_COUNT -eq 0) {
    if ($WARN_COUNT -eq 0) {
        Write-Host "✅ All systems go! VBoarder is ready.`n" -ForegroundColor $GREEN
        exit 0
    }
    else {
        Write-Host "⚠️  Some warnings detected. Review above and address if needed.`n" -ForegroundColor $YELLOW
        exit 0
    }
}
else {
    Write-Host "❌ Critical issues detected. Review above and resolve.`n" -ForegroundColor $RED
    exit 1
}

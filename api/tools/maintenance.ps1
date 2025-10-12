# maintenance.ps1 - vBoarder Lockdown + CTO Report Generator
# Run this script from the root of your vBoarder directory

$ErrorActionPreference = "Stop"

# === CONFIG ===
$agentsPath = ".\agents"
$reportsPath = ".\vboarder_reports"
$coreRegistryPath = ".\agent_registry.json"
$clientRegistryPath = ".\agent_registry_client.json"
$subRegistryPath = ".\agent_registry_sub.json"
$webuiExportPath = ".\webui_agents.json"
$validCoreAgents = @("CEO","CTO","CFO","COO","CIO","CMO","CSO","CPO","CLO","CDO","CAO","SEC")
$validClientAgents = @("HSC", "LHI", "LTD")
$validSubAgents = @("AGENT", "SCAN")

# === UTIL FUNCTIONS ===
function Get-AgentHash($agentJsonPath) {
    if (Test-Path $agentJsonPath) {
        $content = Get-Content $agentJsonPath -Raw
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
        $sha256 = [System.Security.Cryptography.SHA256]::Create()
        $hashBytes = $sha256.ComputeHash($bytes)
        return ($hashBytes | ForEach-Object { $_.ToString("x2") }) -join ""
    }
    return "N/A"
}

function Set-ReadOnly($path) {
    if (Test-Path $path) {
        $item = Get-Item $path
        if (-not $item.IsReadOnly) { $item.IsReadOnly = $true }
    }
}

function Ensure-Agent-Files($agentPath) {
    $defaultAgentJson = '{"name":"UNKNOWN","status":"restricted","version":"1.0"}'
    $defaultPrompt = "Define this agent's role."
    $defaultSchedule = '{"tasks":[],"notes":"No schedule defined."}'

    if (!(Test-Path "$agentPath\agent.json")) { $defaultAgentJson | Out-File "$agentPath\agent.json" -Encoding UTF8 }
    if (!(Test-Path "$agentPath\system_prompt.txt")) { $defaultPrompt | Out-File "$agentPath\system_prompt.txt" -Encoding UTF8 }
    if (!(Test-Path "$agentPath\schedule.json")) { $defaultSchedule | Out-File "$agentPath\schedule.json" -Encoding UTF8 }
}

function Build-Registry($validAgents, $targetFile) {
    $result = @()
    foreach ($agent in $validAgents) {
        $path = Join-Path $agentsPath $agent
        if (Test-Path "$path\agent.json") {
            $json = Get-Content "$path\agent.json" -Raw | ConvertFrom-Json
            $result += $json
        }
    }
    $result | ConvertTo-Json -Depth 5 | Out-File $targetFile -Encoding UTF8
}

function Build-WebUI-Export {
    $agents = @()
    foreach ($agent in $validCoreAgents + $validClientAgents) {
        $path = Join-Path $agentsPath $agent
        if (Test-Path "$path\agent.json") {
            $json = Get-Content "$path\agent.json" -Raw | ConvertFrom-Json
            $agents += $json
        }
    }
    $agents | ConvertTo-Json -Depth 5 | Out-File $webuiExportPath -Encoding UTF8
}

# === MAIN EXECUTION ===
Write-Host "Running vBoarder Maintenance..."

# Step 1: Ensure all agent folders are valid
$allAgents = Get-ChildItem $agentsPath -Directory | Select-Object -ExpandProperty Name
$report = @()
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmm"
if (!(Test-Path $reportsPath)) { New-Item $reportsPath -ItemType Directory | Out-Null }
$reportFile = "$reportsPath\cto_report_$timestamp.md"

foreach ($agentName in $allAgents) {
    $path = Join-Path $agentsPath $agentName
    Ensure-Agent-Files $path

    # Update agent status
    $agentFile = "$path\agent.json"
    $agentItem = Get-Item $agentFile -ErrorAction SilentlyContinue
    $wasRO = $false
    if ($agentItem -and $agentItem.IsReadOnly) {
        $wasRO = $true
        $agentItem.IsReadOnly = $false
    }
    $agent = Get-Content $agentFile -Raw | ConvertFrom-Json
    if ($validCoreAgents -contains $agentName) { $agent.status = "active" } else { $agent.status = "restricted" }
    $agent | ConvertTo-Json -Depth 5 | Out-File $agentFile -Encoding UTF8

    # Set read-only if core (restore original RO state)
    if ($validCoreAgents -contains $agentName -or $wasRO) { Set-ReadOnly $agentFile }

    # Add to report
    $hash = Get-AgentHash $agentFile
    $report += "| $agentName | $($agent.status) | $hash |"
}

# Step 2: Rebuild registries
Build-Registry $validCoreAgents $coreRegistryPath
Build-Registry $validClientAgents $clientRegistryPath
Build-Registry $validSubAgents $subRegistryPath

# Step 3: Build WebUI export
Build-WebUI-Export

# Step 4: Generate Markdown Report
@"
# vBoarder CTO Report
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Script Version: v1.1
Report Path: $reportFile
Agents total: $($allAgents.Count)
Core agents: $($validCoreAgents.Count) | Client agents: $($validClientAgents.Count) | Sub agents: $($validSubAgents.Count)

## Agent Status + Integrity

| Agent | Status | SHA256 Hash |
|-------|--------|-------------|
$($report -join "`n")

---
Next Suggested Enhancements (Optional)

- Live WebUI Agent Status Feed (webui_status.json)
- Analytics Dashboard: Track agent executions, failures, task loads.
- Git Sync Hook: Auto-push agent configs to Git on update.
- Signed Configs: Use RSA or SHA-based signing to prevent tampering.
- Incoming Agent Queue: Staging zone for new agents under review.

> Logged by maintenance.ps1 on $(Get-Date -Format "yyyy-MM-dd") — vBoarder CTO Ops
"@ | Out-File $reportFile -Encoding UTF8

Write-Host "Maintenance complete. Report generated: $reportFile"


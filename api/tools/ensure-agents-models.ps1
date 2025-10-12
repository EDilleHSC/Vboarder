# ensure-agents-models.ps1
param(
    [switch]$WhatIf
)

$root = Split-Path -Parent $PSCommandPath
$agentRoot = Join-Path (Split-Path -Parent (Split-Path -Parent $root)) "agents"
$logFile   = Join-Path $root "ensure-agents-models.log"
$maxLines  = 1000

function Log($msg) {
    $timestamp = Get-Date -Format 'u'
    "$timestamp $msg" | Out-File $logFile -Append -Encoding utf8
    Write-Host $msg
}

if (Test-Path $logFile) {
    $lineCount = (Get-Content $logFile).Length
    if ($lineCount -gt $maxLines) {
        (Get-Content $logFile | Select-Object -Last $maxLines) | Set-Content $logFile -Encoding utf8
        Write-Host "Log rotated: kept last $maxLines lines."
    }
}

Log "===== Run started ====="

# Collect required models
$requiredModels = Get-ChildItem -Recurse $agentRoot -Filter agent.json |
  ForEach-Object {
    try { (Get-Content $_.FullName -Raw | ConvertFrom-Json).model } catch { $null }
  } | Where-Object { $_ } | Sort-Object -Unique

$heavyModels = @("mixtral:latest","wizardcoder:latest","llama3.1:70b","qwen2.5:72b")
$lightModels = $requiredModels | Where-Object { $_ -notin $heavyModels }

Log "Agents require: $($requiredModels -join ', ')"
if ($lightModels.Count -lt $requiredModels.Count) {
    $skip = Compare-Object -ReferenceObject $requiredModels -DifferenceObject $lightModels -PassThru
    Log ("Skipping heavy models (on-demand): {0}" -f ($skip -join ', '))
}

# Query running models
try {
    $ps = Invoke-RestMethod http://127.0.0.1:11434/api/ps
    $running = @()
    if ($ps -and $ps.models) { $running = $ps.models | ForEach-Object { $_.model } }
    Log "Currently running: $($running -join ', ')"
} catch {
    Log "Failed to query Ollama API: $($_.Exception.Message)"
    exit 1
}

# Start missing light models
$missing = $lightModels | Where-Object { $_ -notin $running }
foreach ($m in $missing) {
    if ($WhatIf) {
        Log "WhatIf: would start model $m"
        continue
    }
    Log "Starting model $m ..."
    $started = $false
    try { & ollama run $m | Out-Null; $started = $true } catch {
        try { docker exec -d ai_ollama ollama run $m | Out-Null; $started = $true } catch {
            Log "Failed to start $m : $($_.Exception.Message)"
        }
    }
    if ($started) { Log "Started $m" }
}

Log "===== Run finished ====="


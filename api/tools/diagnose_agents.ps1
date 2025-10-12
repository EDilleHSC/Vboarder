# diagnose_agents.ps1 — vBoarder Agent Health Scanner (ASCII-safe)

$agentsPath = ".\agents"
$requiredFiles = @("agent.json", "system_prompt.txt", "schedule.json", "memory.json")

Write-Host "Scanning agents in: $agentsPath"
Write-Host "--------------------------------------"

$agents = Get-ChildItem -Path $agentsPath -Directory
$total = 0
$problems = 0

foreach ($agent in $agents) {
    $total++
    $path = Join-Path $agentsPath $agent.Name
    $missing = @()
    $empty = @()
    $badJson = $false

    foreach ($file in $requiredFiles) {
        $filePath = Join-Path $path $file
        if (!(Test-Path $filePath)) {
            $missing += $file
        } else {
            $size = (Get-Item $filePath).Length
            if ($size -eq 0) {
                $empty += $file
            }
            if ($file -eq "agent.json") {
                try { $null = Get-Content $filePath -Raw | ConvertFrom-Json } catch { $badJson = $true }
            }
        }
    }

    Write-Host ""
    Write-Host "Agent: $($agent.Name)" -ForegroundColor Cyan
    Write-Host "  Path: $path"
    if ($missing.Count -eq 0 -and $empty.Count -eq 0 -and -not $badJson) {
        Write-Host "  OK: All files present and valid." -ForegroundColor Green
    } else {
        $problems++
        if ($missing.Count -gt 0) {
            Write-Host "  Missing files: $($missing -join ', ')" -ForegroundColor Red
        }
        if ($empty.Count -gt 0) {
            Write-Host "  Empty files: $($empty -join ', ')" -ForegroundColor Yellow
        }
        if ($badJson) {
            Write-Host "  ERROR: agent.json has invalid JSON!" -ForegroundColor Magenta
        }
    }
}

Write-Host ""
Write-Host "Scan Complete"
Write-Host "  Agents Scanned: $total"
if ($problems -gt 0) {
    Write-Host ("  Problems Found: {0}" -f $problems) -ForegroundColor Red
} else {
    Write-Host ("  Problems Found: {0}" -f $problems) -ForegroundColor Green
}


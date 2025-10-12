# ===========================================
# 🚀 VBoarder API Stress & Health Test Script
# ===========================================
# Author: VBoarder DevOps
# Date: (Get-Date)
# Purpose: Validate all 9 agents and measure response latency.
# ===========================================

$ErrorActionPreference = "Continue"
$timestamp = (Get-Date).ToString("yyyy-MM-dd_HH-mm-ss")
$logPath = "D:\ai\projects\vboarder\tests\logs\api_latency_$timestamp.log"
New-Item -ItemType File -Force -Path $logPath | Out-Null
Start-Transcript -Path $logPath -Append

$agents = "AIR","CEO","CFO","CLO","CMO","COO","COS","CTO","SEC"
$results = @()

Write-Host "🔥 Running VBoarder API health + latency test..."
foreach ($i in 1..50) {   # 50 rounds × 9 agents = 450 calls
    foreach ($a in $agents) {
        $body = @{ message = "ping round $i" } | ConvertTo-Json
        $t0 = Get-Date
        try {
            $r = irm "http://127.0.0.1:3737/chat/$a" -Method POST -Body $body -ContentType 'application/json'
            $latency = ((Get-Date) - $t0).TotalMilliseconds
            $results += [PSCustomObject]@{
                Agent = $a
                Round = $i
                LatencyMs = [Math]::Round($latency, 2)
                Status = "✅"
            }
            Write-Host ("{0,-4} {1,6:N2} ms ✅" -f $a, $latency)
        } catch {
            $results += [PSCustomObject]@{
                Agent = $a
                Round = $i
                LatencyMs = 0
                Status = "❌"
            }
            Write-Host ("{0,-4} ❌ failed" -f $a) -ForegroundColor Red
        }
    }
}

# Summarize
$summary = $results | Group-Object Agent | ForEach-Object {
    [PSCustomObject]@{
        Agent = $_.Name
        AvgLatency = [Math]::Round(($_.Group | Measure-Object -Property LatencyMs -Average).Average, 2)
        Errors = ($_.Group | Where-Object { $_.Status -eq "❌" }).Count
        Success = ($_.Group | Where-Object { $_.Status -eq "✅" }).Count
    }
}

Write-Host "`n==== 🧠 Summary ====" -ForegroundColor Cyan
$summary | Format-Table

# Export results
$csvPath = "D:\ai\projects\vboarder\tests\logs\api_latency_summary_$timestamp.csv"
$summary | Export-Csv -Path $csvPath -NoTypeInformation
Write-Host "`nLogs saved to: $logPath"
Write-Host "Summary CSV: $csvPath"

Stop-Transcript

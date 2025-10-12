# ===========================================
# 🧠 VBoarder Latency Parser & Summary Tool
# ===========================================
# Reads console latency output (like "CEO  3,456.78 ms")
# Computes per-agent average, min, max, count, and exports CSV
# ===========================================

param(
    [string]$InputFile = "D:\ai\projects\vboarder\tests\logs\raw_latency_output.txt",
    [string]$OutputFile = "D:\ai\projects\vboarder\tests\logs\latency_summary_$(Get-Date -Format yyyyMMddHHmmss).csv"
)

if (-not (Test-Path $InputFile)) {
    Write-Host "❌ Input file not found: $InputFile" -ForegroundColor Red
    exit 1
}

Write-Host "📂 Reading latency data from $InputFile" -ForegroundColor Cyan

# Extract agent + numeric latency (ignore "failed" lines)
$data = Get-Content $InputFile | ForEach-Object {
    if ($_ -match "^(?<agent>[A-Z]{2,3})\s+(?<lat>[0-9\.,]+)\s*ms") {
        [PSCustomObject]@{
            Agent = $matches.agent
            LatencyMs = [double]($matches.lat -replace ",","")
        }
    }
} | Where-Object { $_.LatencyMs -gt 0 }

if (-not $data) {
    Write-Host "⚠️ No valid latency data parsed!" -ForegroundColor Yellow
    exit 0
}

# Group and compute stats
$summary = $data | Group-Object Agent | ForEach-Object {
    $agentData = $_.Group
    $avg = [Math]::Round(($agentData | Measure-Object -Property LatencyMs -Average).Average, 2)
    $min = [Math]::Round(($agentData | Measure-Object -Property LatencyMs -Minimum).Minimum, 2)
    $max = [Math]::Round(($agentData | Measure-Object -Property LatencyMs -Maximum).Maximum, 2)
    [PSCustomObject]@{
        Agent = $_.Name
        Count = $agentData.Count
        AvgLatencyMs = $avg
        MinLatencyMs = $min
        MaxLatencyMs = $max
    }
}

Write-Host "`n==== 📊 Average Latency Summary ====" -ForegroundColor Green
$summary | Format-Table -AutoSize

# Export to CSV
$summary | Export-Csv -Path $OutputFile -NoTypeInformation -Encoding UTF8
Write-Host "`n✅ Summary saved to $OutputFile" -ForegroundColor Cyan

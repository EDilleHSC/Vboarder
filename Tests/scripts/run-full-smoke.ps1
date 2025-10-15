<#
.SYNOPSIS
  Full single-shot VBoarder verification: API stress, RAG ingest+recall, memory sampling, logs and CSV summary.

.DESCRIPTION
  - Tests /chat/<agent> for all agents several times (configurable)
  - Uploads a temporary test file to /ingest (if endpoint supports file_path JSON)
  - Queries the agent to verify recall
  - Samples python process memory/CPU throughout the run
  - Produces detailed log (transcript) and CSV summary

.NOTES
  - Run from PowerShell 7 (pwsh)
  - Requires API to be on http://127.0.0.1:3737
  - Adjust $rounds and $sleepBetweenRequests as needed
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Continue"

# ---------- CONFIG ----------
$baseUrl = "http://127.0.0.1:3737"
$agents = "AIR","CEO","CFO","CLO","CMO","COO","COS","CTO","SEC"
# Number of rounds per agent (each round sends one request per agent)
$rounds = 50
# Delay (ms) between individual requests to be a bit gentler on IO; set to 0 for tight loop
$sleepBetweenRequests = 100
# Directory for logs and artifacts
$projectRoot = "D:\ai\projects\vboarder"
$logsDir = Join-Path $projectRoot "tests\logs"
$reportsDir = Join-Path $projectRoot "docs\TEST_REPORTS"
# Temp test file to ingest (script will create this)
$uploadsDir = "D:\ai\uploads"
$testDocPath = Join-Path $uploadsDir "vboarder_memory_check_test_doc.md"
# Ingest endpoint payload style - if your /ingest accepts JSON with file_path and doc_id
$ingestEndpoint = "$baseUrl/ingest"
$chatEndpointTemplate = "$baseUrl/chat/{0}"    # format string where {0} replaced by agent name

# ---------- Setup folders & log paths ----------
if (-not (Test-Path $logsDir)) { New-Item -Path $logsDir -ItemType Directory -Force | Out-Null }
if (-not (Test-Path $reportsDir)) { New-Item -Path $reportsDir -ItemType Directory -Force | Out-Null }
if (-not (Test-Path $uploadsDir)) { New-Item -Path $uploadsDir -ItemType Directory -Force | Out-Null }

$timestamp = (Get-Date).ToString("yyyy-MM-dd_HH-mm-ss")
$transcriptPath = Join-Path $logsDir "full_run_$timestamp.log"
$csvPath = Join-Path $logsDir "full_run_summary_$timestamp.csv"
$memCsvPath = Join-Path $logsDir "memory_samples_$timestamp.csv"

# Start Transcript
Start-Transcript -Path $transcriptPath -Append

Write-Host "=== VBoarder Full-Suite Test Starting ===" -ForegroundColor Green
Write-Host "Timestamp: $timestamp"
Write-Host "Logs: $transcriptPath"
Write-Host "Summary CSV: $csvPath"
Write-Host "Memory CSV: $memCsvPath"
Write-Host "Rounds per agent: $rounds"
Write-Host "Sleep between requests (ms): $sleepBetweenRequests"
Write-Host ""

# ---------- Helper funcs ----------
function NowMs { return (Get-Date) }
function ElapsedMs($start,$end) {
    return ([math]::Round((($end - $start).TotalMilliseconds),2))
}

function Sample-PythonProcess {
    # returns PSCustomObject with Id, WS (MB), PM (MB), CPU (TotalSeconds)
    $proc = Get-Process -Name python -ErrorAction SilentlyContinue | Sort-Object -Property WS -Descending | Select-Object -First 1
    if ($null -eq $proc) {
        return $null
    }
    [PSCustomObject]@{
        Timestamp = (Get-Date).ToString("o")
        Id = $proc.Id
        Name = $proc.ProcessName
        WorkingSetMB = [math]::Round($proc.WorkingSet64 / 1MB, 2)
        PrivateMB = [math]::Round($proc.PrivateMemorySize64 / 1MB, 2)
        CPUSeconds = [math]::Round($proc.CPU, 2)
    }
}

function Post-Chat($agent, $message) {
    $uri = [string]::Format($chatEndpointTemplate, $agent)
    $body = @{ message = $message } | ConvertTo-Json
    return Invoke-RestMethod -Uri $uri -Method POST -Body $body -ContentType "application/json" -ErrorAction Stop
}

function Post-Ingest($filePath, $docId) {
    # Assumes server accepts JSON: { file_path: "...", doc_id: "..." }
    # If your server expects multi-part upload, this should be adapted.
    $payload = @{ file_path = $filePath; doc_id = $docId } | ConvertTo-Json
    return Invoke-RestMethod -Uri $ingestEndpoint -Method POST -Body $payload -ContentType "application/json" -ErrorAction Stop
}

# ---------- 0) Quick API reachability check ----------
Write-Host "`n[1] Checking API reachability..." -ForegroundColor Cyan
try {
    $ping = Invoke-RestMethod -Uri $baseUrl -Method Get -TimeoutSec 5 -ErrorAction Stop
    Write-Host "Root endpoint responded." -ForegroundColor Green
} catch {
    Write-Host "Could not reach $baseUrl - trying health endpoint..." -ForegroundColor Yellow
    try {
        $h = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get -TimeoutSec 5 -ErrorAction Stop
        Write-Host "/health responded: $h" -ForegroundColor Green
    } catch {
        Write-Host "ERROR: API unreachable at $baseUrl. Start your backend and re-run this script." -ForegroundColor Red
        Stop-Transcript
        exit 1
    }
}

# ---------- 1) Create test doc for ingest ----------
$testDocContent = @"
# VBoarder Memory Check
This is a test document to verify RAG ingestion and recall.
UniqueToken: VBOARDER_MEMORY_CHECK_$(Get-Date -Format yyyyMMddHHmmss)
Summary: The agent should recall the phrase 'VBOARDER_MEMORY_CHECK' when asked.
"@

Set-Content -Path $testDocPath -Value $testDocContent -Encoding UTF8
Write-Host "`n[2] Created test document at: $testDocPath" -ForegroundColor Cyan

# ---------- 2) Start background memory sampler ----------
Write-Host "`n[3] Starting memory sampler (samples every 2s)..." -ForegroundColor Cyan
$memSamples = @()
$memStopFlag = $false
$sampleIntervalSec = 2

$memJob = Start-Job -ScriptBlock {
    param($outPath, $interval)
    while ($true) {
        try {
            $proc = Get-Process -Name python -ErrorAction SilentlyContinue | Sort-Object -Property WS -Descending | Select-Object -First 1
            if ($null -eq $proc) {
                $obj = [PSCustomObject]@{
                    Timestamp = (Get-Date).ToString("o")
                    Id = ""
                    Name = ""
                    WorkingSetMB = 0
                    PrivateMB = 0
                    CPUSeconds = 0
                }
            } else {
                $obj = [PSCustomObject]@{
                    Timestamp = (Get-Date).ToString("o")
                    Id = $proc.Id
                    Name = $proc.ProcessName
                    WorkingSetMB = [math]::Round($proc.WorkingSet64 / 1MB, 2)
                    PrivateMB = [math]::Round($proc.PrivateMemorySize64 / 1MB, 2)
                    CPUSeconds = [math]::Round($proc.CPU, 2)
                }
            }
            $obj | ConvertTo-Csv -NoTypeInformation | Select-Object -Skip 1 | Out-File -FilePath $outPath -Append -Encoding UTF8
        } catch {
            # ignore sampling errors
        }
        Start-Sleep -Seconds $interval
    }
} -ArgumentList $memCsvPath, $sampleIntervalSec

Start-Sleep -Seconds 1

# ---------- 3) Stress test all agents ----------
Write-Host "`n[4] Stress testing agents..." -ForegroundColor Cyan
$results = @()

for ($i = 1; $i -le $rounds; $i++) {
    foreach ($a in $agents) {
        $msg = "ping round $i - $(Get-Random -Minimum 1000 -Maximum 9999)"
        $t0 = Get-Date
        try {
            $resp = Post-Chat -agent $a -message $msg
            $t1 = Get-Date
            $lat = ElapsedMs $t0 $t1
            $results += [PSCustomObject]@{
                Timestamp = (Get-Date).ToString("o")
                Agent = $a
                Round = $i
                LatencyMs = $lat
                Status = "OK"
                ResponseSnippet = ($resp | Out-String).Trim() -replace "`r`n"," " 
            }
            Write-Host ("{0,-4} R{1,3} {2,7:N2} ms OK" -f $a, $i, $lat)
        } catch {
            $t1 = Get-Date
            $lat = ElapsedMs $t0 $t1
            $results += [PSCustomObject]@{
                Timestamp = (Get-Date).ToString("o")
                Agent = $a
                Round = $i
                LatencyMs = $lat
                Status = "ERROR"
                ResponseSnippet = $_.Exception.Message
            }
            Write-Host ("{0,-4} R{1,3} ERROR: {2}" -f $a, $i, $_.Exception.Message) -ForegroundColor Red
        }
        Start-Sleep -Milliseconds $sleepBetweenRequests
    }
}

# ---------- 4) Ingest the test doc and verify recall ----------
Write-Host "`n[5] Ingesting test document and verifying recall..." -ForegroundColor Cyan
$docId = "memory-check-$timestamp"
$ingestOk = $false
try {
    $ingResp = Post-Ingest -filePath $testDocPath -docId $docId
    Write-Host "Ingest response: $($ingResp | Out-String)" -ForegroundColor Green
    $ingestOk = $true
} catch {
    Write-Host "Ingest failed: $($_.Exception.Message)" -ForegroundColor Red
}

Start-Sleep -Seconds 2

if ($ingestOk) {
    # Query one agent to find the unique token
    $queryMsg = "What does VBOARDER_MEMORY_CHECK say? (test doc id: $docId)"
    try {
        $resp = Post-Chat -agent "CTO" -message $queryMsg
        Write-Host "CTO response: $($resp | Out-String)" -ForegroundColor Green
        $contains = ($resp | Out-String).ToLower().Contains("vboarder_memory_check")
        $results += [PSCustomObject]@{
            Timestamp = (Get-Date).ToString("o")
            Agent = "CTO"
            Round = "ingest-check"
            LatencyMs = 0
            Status = (if ($contains) {"RAG_OK"} else {"RAG_MISS"})
            ResponseSnippet = ($resp | Out-String).Trim() -replace "`r`n"," "
        }
        if ($contains) {
            Write-Host "RAG recall OK: unique token found in response." -ForegroundColor Green
        } else {
            Write-Host "RAG recall MISSING: unique token not found." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "RAG query failed: $($_.Exception.Message)" -ForegroundColor Red
        $results += [PSCustomObject]@{
            Timestamp = (Get-Date).ToString("o")
            Agent = "CTO"
            Round = "ingest-check"
            LatencyMs = 0
            Status = "RAG_ERROR"
            ResponseSnippet = $_.Exception.Message
        }
    }
}

# ---------- 5) Stop memory sampler job ----------
Write-Host "`n[6] Stopping memory sampler job..." -ForegroundColor Cyan
Get-Job -Id $memJob.Id | Stop-Job -Force -ErrorAction SilentlyContinue
Get-Job -Id $memJob.Id | Remove-Job -Force -ErrorAction SilentlyContinue

# ---------- 6) Summarize results ----------
Write-Host "`n[7] Summarizing results..." -ForegroundColor Cyan
$summary = $results | Group-Object Agent | ForEach-Object {
    $grp = $_.Group
    [PSCustomObject]@{
        Agent = $_.Name
        AvgLatencyMs = [math]::Round(($grp | Where-Object { $_.LatencyMs -gt 0 } | Measure-Object -Property LatencyMs -Average).Average,2)
        MinLatencyMs = [math]::Round(($grp | Where-Object { $_.LatencyMs -gt 0 } | Measure-Object -Property LatencyMs -Minimum).Minimum,2)
        MaxLatencyMs = [math]::Round(($grp | Where-Object { $_.LatencyMs -gt 0 } | Measure-Object -Property LatencyMs -Maximum).Maximum,2)
        Errors = ($grp | Where-Object { $_.Status -ne "OK" -and $_.Status -ne "RAG_OK" }).Count
        SuccessCount = ($grp | Where-Object { $_.Status -eq "OK" -or $_.Status -eq "RAG_OK" }).Count
    }
}

$summary | Format-Table -AutoSize
$summary | Export-Csv -Path $csvPath -NoTypeInformation -Encoding UTF8

# Dump full request results too for deep debugging
$resultsPath = Join-Path $logsDir ("full_run_requests_$timestamp.csv")
$results | Export-Csv -Path $resultsPath -NoTypeInformation -Encoding UTF8
Write-Host "`nFull results CSV: $resultsPath"

# ---------- 7) Save a short markdown report ----------
$reportPath = Join-Path $reportsDir ("API_Stress_Test_$timestamp.md")
$reportLines = @()
$reportLines += "# VBoarder Full Run Report - $timestamp"
$reportLines += ""
$reportLines += "## Summary"
$summary | ForEach-Object { $reportLines += ("- {0}: Avg {1} ms (min {2} ms, max {3} ms), Errors: {4}, Success: {5}" -f $_.Agent, $_.AvgLatencyMs, $_.MinLatencyMs, $_.MaxLatencyMs, $_.Errors, $_.SuccessCount) }
$reportLines += ""
$reportLines += "## Notes"
$reportLines += "- Rounds per agent: $rounds"
$reportLines += "- Test doc ingested: $testDocPath (docId: $docId)"
$reportLines += "- Memory samples: $memCsvPath"
$reportLines += ""
$reportLines | Out-File -FilePath $reportPath -Encoding UTF8
Write-Host "`nGenerated report: $reportPath" -ForegroundColor Green

# ---------- 8) Wrap up ----------
Stop-Transcript
Write-Host "`n=== Full test complete. Logs & reports saved. ===" -ForegroundColor Green
Write-Host "Transcript: $transcriptPath"
Write-Host "Summary CSV: $csvPath"
Write-Host "Per-request CSV: $resultsPath"
Write-Host "Memory CSV: $memCsvPath"
Write-Host "Markdown report: $reportPath"

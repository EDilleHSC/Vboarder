<#
    generate_core_briefing.ps1
    Queries core agents and generates a normalized, annotated Markdown briefing.
#>

param(
    [string[]]$Agents = @("AIR","CEO","CFO","CLO","CMO","COO","COS","CTO","SEC"),
    [string]$ApiBase = "http://127.0.0.1:3737",
    [string]$ReportsDir = ".\vboarder_reports",
    [int]$TimeoutSec = 10,
    [string]$Message = "Top 3 priorities and top 3 risks for the Nov 12 board meeting. Use concise bullets."
)

# Ensure reports directory exists
if (-not (Test-Path $ReportsDir)) { New-Item -ItemType Directory -Path $ReportsDir | Out-Null }

# Timestamp + output path
$ts = Get-Date -Format "yyyy-MM-dd_HHmm"
$out = Join-Path $ReportsDir ("board_briefing_{0}.md" -f $ts)

# Header
"## Core Agents Briefing ($ts)`r`n" | Out-File $out -Encoding UTF8 -Force

# Query each agent with Meta line
foreach ($a in $Agents) {
    $uri = "{0}/chat/{1}" -f $ApiBase, $a
    $body = @{ message = $Message } | ConvertTo-Json -Compress
    try {
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        $resp = Invoke-RestMethod -Uri $uri -Method POST -Body $body -ContentType "application/json" -TimeoutSec $TimeoutSec
        $sw.Stop()

        # Extract meta
        $rt = $null
        if ($resp.PSObject.Properties.Name -contains "response_time_ms") { $rt = [int]$resp.response_time_ms }
        if (-not $rt) { $rt = [int][Math]::Round($sw.Elapsed.TotalMilliseconds) }

        $tsMeta = $null
        if ($resp.PSObject.Properties.Name -contains "timestamp") { $tsMeta = [string]$resp.timestamp }
        if (-not $tsMeta -or [string]::IsNullOrWhiteSpace($tsMeta)) { $tsMeta = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd HH:mm:ss\Z") }

        # Convert epoch timestamp to ISO-UTC if numeric
        if ($tsMeta -match '^\d+(\.\d+)?$') {
            try {
                $epochMs = [double]$tsMeta * 1000
                $base = [DateTimeOffset]::FromUnixTimeMilliseconds([long][Math]::Round($epochMs))
                $tsMeta = $base.UtcDateTime.ToString("yyyy-MM-dd HH:mm:ss\Z")
            } catch { $tsMeta = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd HH:mm:ss\Z") }
        }

        $metaLine = "Meta: {0} ms at {1}" -f $rt, $tsMeta

        $text = $resp.response
        if (-not $text) { $text = ($resp | ConvertTo-Json -Depth 5) }

        "`r`n### $a`r`n$metaLine`r`n$text`r`n" | Add-Content $out -Encoding UTF8
    } catch {
        $tsErr = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd HH:mm:ss\Z")
        "`r`n### $a`r`nMeta: error at $tsErr`r`nERROR: $($_.Exception.Message)`r`n" | Add-Content $out -Encoding UTF8
    }
}

# Basic normalization of headings/bullets
$text = (Get-Content $out -Raw)
$text = $text -replace '(?m)^\s*Top\s+3\s+Priorities.*?:\s*', "Priorities:`r`n"
$text = $text -replace '(?m)^\s*Top\s+3\s+Risks.*?:\s*',      "Risks:`r`n"
$text = $text -replace '(?m)^\s*\d+\.\s*',                    '- '
# Compress extra blank lines
$text = $text -replace '(?m)^\s*$\r?\n(?=^\s*$)', ''
Set-Content $out -Value $text -Encoding UTF8

# Additional normalization and guardrails
$text = (Get-Content $out -Raw)

# 1) Remove bold markers and convert common headings to standard
$text = $text -replace '(?m)\*\*(Top\s+3\s+Priorities.*?)\*\*', '$1'
$text = $text -replace '(?m)\*\*(Top\s+3\s+Risks.*?)\*\*',      '$1'
$text = $text -replace '(?m)^\s*Top\s+3\s+Priorities.*?:\s*',   "Priorities:`r`n"
$text = $text -replace '(?m)^\s*Top\s+3\s+Risks.*?:\s*',        "Risks:`r`n"

# 2) Fix headings accidentally preceded by a dash
$text = $text -replace '(?m)^\s*-\s*Priorities:\s*', "Priorities:`r`n"
$text = $text -replace '(?m)^\s*-\s*Risks:\s*',      "Risks:`r`n"

# 3) Normalize bullets (numbered and double-dash to single '- ')
$text = $text -replace '(?m)^\s*\d+\.\s*', '- '
$text = $text -replace '(?m)^\s*--\s*',    '- '

# 4) Ensure each agent section has both headings
$lines = $text -split "`r?`n"
for ($i=0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^###\s+([A-Z]{2,3})$') {
        $start = $i + 1
        $j = $start
        while ($j -lt $lines.Count -and $lines[$j] -notmatch '^###\s+') { $j++ }
        if ($j -le $start) { continue }
        $chunk = $lines[$start..($j-1)]

        $hasPrior = ($chunk | Where-Object { $_ -match '^(?i)Priorities:\s*$' }).Count -gt 0
        $hasRisks = ($chunk | Where-Object { $_ -match '^(?i)Risks:\s*$' }).Count -gt 0

        if (-not $hasPrior) {
            $chunk = @("Priorities:") + $chunk
        }
        if (-not $hasRisks) {
            $chunk = $chunk + @("Risks:", "- Needs follow-up: no risks provided")
        }

        $lines = $lines[0..($start-1)] + $chunk + $lines[$j..($lines.Count-1)]
        $i = $j
    }
}

# 5) Collapse extra blank lines
$text = ($lines -join "`r`n")
$text = $text -replace '(?m)^\s*$\r?\n(?=^\s*$)', ''

Set-Content $out -Value $text -Encoding UTF8

# Post-normalization cleanup: dedent bullets, remove duplicate headings, strip lingering "Top 3 ..." lines
$text = (Get-Content $out -Raw)

# Remove duplicate consecutive headings
$text = $text -replace '(?ms)^(Priorities:)\s*\r?\n\s*Priorities:\s*', '$1`r`n'
$text = $text -replace '(?ms)^(Risks:)\s*\r?\n\s*Risks:\s*',           '$1`r`n'

# Strip lingering "Top 3 ..." lines anywhere
$text = $text -replace '(?m)^\s*Top\s*3\s*Priorities.*\r?\n', ''
$text = $text -replace '(?m)^\s*Top\s*3\s*Risks.*\r?\n',      ''
$text = $text -replace '(?mi)\bTop\s*3\s*Priorities\b.*', ''
$text = $text -replace '(?mi)\bTop\s*3\s*Risks\b.*', ''

# Ensure Meta line directly under header, then headings/content
# Also dedupe any repeated Meta lines inside each section
$lines = $text -split "`r?`n"
for ($i=0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^###\s+([A-Z]{2,3})
$lines = $text -split "`r?`n"
for ($i=0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^###\s+([A-Z]{2,3})$') {
        $start = $i + 1
        $j = $start
        while ($j -lt $lines.Count -and $lines[$j] -notmatch '^###\s+') { $j++ }
        if ($j -le $start) { continue }
        $chunk = $lines[$start..($j-1)]

        # Extract existing meta line if present; else synthesize placeholder
        $metaIdx = -1
        for ($k=0; $k -lt $chunk.Count; $k++) {
            if ($chunk[$k] -match '^\s*Meta:\s*') { $metaIdx = $k; break }
        }
        if ($metaIdx -ge 0) {
            $meta = $chunk[$metaIdx]
            $chunk = $chunk[0..($metaIdx-1)] + $chunk[($metaIdx+1)..($chunk.Count-1)]
        } else {
            $meta = 'Meta: ok'
        }

        # Reassemble: meta->rest
        $chunk = @($meta) + $chunk
        $lines = $lines[0..($start-1)] + $chunk + $lines[$j..($lines.Count-1)]
        $i = $j
    }
}
$text = ($lines -join "`r`n")

# Enforce single Priorities/Risks per section and dedent bullets
$lines = $text -split "`r?`n"
for ($i=0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^###\s+([A-Z]{2,3})$') {
        $start = $i + 1
        $j = $start
        while ($j -lt $lines.Count -and $lines[$j] -notmatch '^###\s+') { $j++ }
        if ($j -le $start) { continue }
        $chunk = $lines[$start..($j-1)]

        $chunk = $chunk -replace '(?mi)^\s*Priorities\s*:?\s*$', 'Priorities:'
        $chunk = $chunk -replace '(?mi)^\s*Risks\s*:?\s*$',      'Risks:'

        $seenPrior = $false; $seenRisks = $false
        $newChunk = @()
        foreach ($ln in $chunk) {
            if ($ln -match '^(?i)Priorities:\s*$') {
                if (-not $seenPrior) { $newChunk += 'Priorities:'; $seenPrior = $true }
                continue
            }
            if ($ln -match '^(?i)Risks:\s*$') {
                if (-not $seenRisks) { $newChunk += 'Risks:'; $seenRisks = $true }
                continue
            }
            $newChunk += $ln
        }

        if (-not $seenPrior) { $newChunk = @('Priorities:') + $newChunk }
        if (-not $seenRisks) { $newChunk = $newChunk + @('Risks:', '- Needs follow-up: no risks provided') }

        $newChunk = $newChunk -replace '^(?:\s{2,}|\t+)-\s+', '- '

        $lines = $lines[0..($start-1)] + $newChunk + $lines[$j..($lines.Count-1)]
        $i = $j
    }
}
$text = ($lines -join "`r`n")

Set-Content $out -Value $text -Encoding UTF8

# Write/update stable latest copy
try {
    Copy-Item $out (Join-Path $ReportsDir "board_briefing_latest.md") -Force
    Write-Host "Also updated: $(Join-Path $ReportsDir 'board_briefing_latest.md')"
} catch {
    Write-Warning "Could not update latest copy: $($_.Exception.Message)"
}

Write-Host "Board briefing saved to: $out"
Get-Content $out
) {
        $start = $i + 1
        $j = $start
        while ($j -lt $lines.Count -and $lines[$j] -notmatch '^###\s+') { $j++ }
        if ($j -le $start) { continue }
        $chunk = $lines[$start..($j-1)]

        $keptMeta = $false
        $newChunk = @()
        foreach ($ln in $chunk) {
            if ($ln -match '^\s*Meta:\s*') {
                if (-not $keptMeta) { $newChunk += $ln; $keptMeta = $true }
                continue
            }
            $newChunk += $ln
        }

        $lines = $lines[0..($start-1)] + $newChunk + $lines[$j..($lines.Count-1)]
        $i = $j
    }
}
$text = ($lines -join "`r`n")
$lines = $text -split "`r?`n"
for ($i=0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^###\s+([A-Z]{2,3})$') {
        $start = $i + 1
        $j = $start
        while ($j -lt $lines.Count -and $lines[$j] -notmatch '^###\s+') { $j++ }
        if ($j -le $start) { continue }
        $chunk = $lines[$start..($j-1)]

        # Extract existing meta line if present; else synthesize placeholder
        $metaIdx = -1
        for ($k=0; $k -lt $chunk.Count; $k++) {
            if ($chunk[$k] -match '^\s*Meta:\s*') { $metaIdx = $k; break }
        }
        if ($metaIdx -ge 0) {
            $meta = $chunk[$metaIdx]
            $chunk = $chunk[0..($metaIdx-1)] + $chunk[($metaIdx+1)..($chunk.Count-1)]
        } else {
            $meta = 'Meta: ok'
        }

        # Reassemble: meta->rest
        $chunk = @($meta) + $chunk
        $lines = $lines[0..($start-1)] + $chunk + $lines[$j..($lines.Count-1)]
        $i = $j
    }
}
$text = ($lines -join "`r`n")

# Enforce single Priorities/Risks per section and dedent bullets
$lines = $text -split "`r?`n"
for ($i=0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^###\s+([A-Z]{2,3})$') {
        $start = $i + 1
        $j = $start
        while ($j -lt $lines.Count -and $lines[$j] -notmatch '^###\s+') { $j++ }
        if ($j -le $start) { continue }
        $chunk = $lines[$start..($j-1)]

        $chunk = $chunk -replace '(?mi)^\s*Priorities\s*:?\s*$', 'Priorities:'
        $chunk = $chunk -replace '(?mi)^\s*Risks\s*:?\s*$',      'Risks:'

        $seenPrior = $false; $seenRisks = $false
        $newChunk = @()
        foreach ($ln in $chunk) {
            if ($ln -match '^(?i)Priorities:\s*$') {
                if (-not $seenPrior) { $newChunk += 'Priorities:'; $seenPrior = $true }
                continue
            }
            if ($ln -match '^(?i)Risks:\s*$') {
                if (-not $seenRisks) { $newChunk += 'Risks:'; $seenRisks = $true }
                continue
            }
            $newChunk += $ln
        }

        if (-not $seenPrior) { $newChunk = @('Priorities:') + $newChunk }
        if (-not $seenRisks) { $newChunk = $newChunk + @('Risks:', '- Needs follow-up: no risks provided') }

        $newChunk = $newChunk -replace '^(?:\s{2,}|\t+)-\s+', '- '

        $lines = $lines[0..($start-1)] + $newChunk + $lines[$j..($lines.Count-1)]
        $i = $j
    }
}
$text = ($lines -join "`r`n")

Set-Content $out -Value $text -Encoding UTF8

# Write/update stable latest copy
try {
    Copy-Item $out (Join-Path $ReportsDir "board_briefing_latest.md") -Force
    Write-Host "Also updated: $(Join-Path $ReportsDir 'board_briefing_latest.md')"
} catch {
    Write-Warning "Could not update latest copy: $($_.Exception.Message)"
}

Write-Host "Board briefing saved to: $out"
Get-Content $out


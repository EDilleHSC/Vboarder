<# SEC Auto-Fix Script - Fixes common issues found in audit #>
param(
  [switch]$WhatIf  # Use -WhatIf to preview changes without making them
)

$ErrorActionPreference = "Stop"
$timestamp = Get-Date -Format "yyyyMMddHHmmss"

Write-Host "`n=== SEC AUTO-FIX SCRIPT ===" -ForegroundColor Cyan
if ($WhatIf) {
  Write-Host "PREVIEW MODE - No changes will be made`n" -ForegroundColor Yellow
} else {
  Write-Host "LIVE MODE - Files will be modified`n" -ForegroundColor Green
}

$fixCount = 0

# Helper to backup a file before modifying
function Backup-File {
  param([string]$path)
  if (Test-Path $path) {
    $backupPath = "$path.bak_$timestamp"
    Copy-Item $path $backupPath -Force
    Write-Host "  Backed up: $backupPath" -ForegroundColor Gray
  }
}

# 1) Fix agent.json
Write-Host "[1/4] Fixing agent.json..." -ForegroundColor Cyan
if (Test-Path ".\agent.json") {
  $agent = Get-Content ".\agent.json" -Raw | ConvertFrom-Json
  
  $needsFix = $false
  if ($agent.name -eq "UNKNOWN") {
    Write-Host "  - Changing name: 'UNKNOWN' -> 'SEC'" -ForegroundColor Yellow
    $needsFix = $true
  }
  if (-not $agent.role) {
    Write-Host "  - Adding role: 'Executive Secretary'" -ForegroundColor Yellow
    $needsFix = $true
  }
  
  if ($needsFix) {
    if (-not $WhatIf) {
      Backup-File ".\agent.json"
      $agent.name = "SEC"
      $agent.role = "Executive Secretary"
      $agent | ConvertTo-Json -Depth 10 | Set-Content ".\agent.json" -Encoding UTF8
      Write-Host "  Fixed agent.json" -ForegroundColor Green
      $fixCount++
    }
  } else {
    Write-Host "  No fixes needed" -ForegroundColor Gray
  }
} else {
  Write-Host "  agent.json not found - skipping" -ForegroundColor Gray
}

# 2) Fix agent_config.json
Write-Host "`n[2/4] Fixing agent_config.json..." -ForegroundColor Cyan
if (Test-Path ".\agent_config.json") {
  $agentCfg = Get-Content ".\agent_config.json" -Raw | ConvertFrom-Json
  
  $needsFix = $false
  if ($agentCfg.metadata -and $agentCfg.metadata.name -eq $null) {
    Write-Host "  - Setting metadata.name: null -> 'SEC'" -ForegroundColor Yellow
    $needsFix = $true
  }
  if ($agentCfg.runtime -and $agentCfg.runtime.temperature -gt 0.5) {
    Write-Host "  - Lowering temperature: $($agentCfg.runtime.temperature) -> 0.3" -ForegroundColor Yellow
    $needsFix = $true
  }
  
  if ($needsFix) {
    if (-not $WhatIf) {
      Backup-File ".\agent_config.json"
      if ($agentCfg.metadata) { $agentCfg.metadata.name = "SEC" }
      if ($agentCfg.runtime) { $agentCfg.runtime.temperature = 0.3 }
      $agentCfg | ConvertTo-Json -Depth 10 | Set-Content ".\agent_config.json" -Encoding UTF8
      Write-Host "  Fixed agent_config.json" -ForegroundColor Green
      $fixCount++
    }
  } else {
    Write-Host "  No fixes needed" -ForegroundColor Gray
  }
} else {
  Write-Host "  agent_config.json not found - skipping" -ForegroundColor Gray
}

# 3) Delete junk files
Write-Host "`n[3/4] Removing junk files..." -ForegroundColor Cyan
$junkFiles = @(
  ".\config\New Text Document.txt",
  ".\config\New Text Document (2).txt"
)

$deletedCount = 0
foreach ($junk in $junkFiles) {
  if (Test-Path $junk) {
    Write-Host "  - Deleting: $junk" -ForegroundColor Yellow
    if (-not $WhatIf) {
      Remove-Item $junk -Force
      $deletedCount++
    }
  }
}

if ($deletedCount -gt 0 -and -not $WhatIf) {
  Write-Host "  Deleted $deletedCount junk files" -ForegroundColor Green
  $fixCount++
} elseif ($deletedCount -eq 0) {
  Write-Host "  No junk files found" -ForegroundColor Gray
}

# 4) Clean up duplicate backup configs
Write-Host "`n[4/4] Checking for duplicate backup configs..." -ForegroundColor Cyan
if (Test-Path ".\config") {
  $backupConfigs = Get-ChildItem ".\config" -Filter "*.bak*" | Where-Object { $_.Name -notlike "*$timestamp*" }
  
  if ($backupConfigs.Count -gt 0) {
    Write-Host "  Found $($backupConfigs.Count) old backup config files:" -ForegroundColor Yellow
    foreach ($bc in $backupConfigs) {
      Write-Host "    - $($bc.Name)" -ForegroundColor Gray
    }
    Write-Host "  Recommend manually reviewing and deleting old backups" -ForegroundColor Yellow
    Write-Host "  (Not auto-deleting for safety)" -ForegroundColor Gray
  } else {
    Write-Host "  No duplicate configs to clean" -ForegroundColor Gray
  }
}

# Summary
Write-Host "`n=== SUMMARY ===" -ForegroundColor Cyan
if ($WhatIf) {
  Write-Host "Preview complete. Run without -WhatIf to apply changes." -ForegroundColor Yellow
} else {
  Write-Host "Auto-fixes applied: $fixCount" -ForegroundColor Green
  Write-Host "`nSTILL NEED MANUAL FIXING:" -ForegroundColor Yellow
  Write-Host "  1. config.json - Contains absolute paths (D:\...)" -ForegroundColor White
  Write-Host "  2. system_prompt.txt - Placeholder, needs real prompt" -ForegroundColor White
  Write-Host "  3. prompts/system.txt - Broken 'You are .' - needs agent name" -ForegroundColor White
  Write-Host "  4. prompts/system_detailed.txt - Placeholder" -ForegroundColor White
  Write-Host "  5. prompts/system_prompt.txt - Placeholder" -ForegroundColor White
  Write-Host "  6. Consolidate backup/ and backups/ folders" -ForegroundColor White
}

Write-Host ""
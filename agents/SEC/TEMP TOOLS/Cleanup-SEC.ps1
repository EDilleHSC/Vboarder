<# SEC Cleanup Script - Consolidate backups and remove old .bak files #>
param(
  [switch]$WhatIf
)

Write-Host "`n=== SEC CLEANUP ===" -ForegroundColor Cyan
if ($WhatIf) {
  Write-Host "PREVIEW MODE - No changes will be made`n" -ForegroundColor Yellow
} else {
  Write-Host "LIVE MODE - Files will be moved/deleted`n" -ForegroundColor Green
}

# 1) Consolidate backup folders
Write-Host "[1/2] Consolidating backup folders..." -ForegroundColor Yellow

$hasBackup = Test-Path ".\backup"
$hasBackups = Test-Path ".\backups"

if ($hasBackup -and $hasBackups) {
  Write-Host "  Found both 'backup' and 'backups' folders" -ForegroundColor Gray

  # Count items in each
  $backupItems = Get-ChildItem ".\backup" -Recurse
  $backupsItems = Get-ChildItem ".\backups" -Recurse

  Write-Host "  backup/: $($backupItems.Count) items" -ForegroundColor Gray
  Write-Host "  backups/: $($backupsItems.Count) items" -ForegroundColor Gray

  # Move all from backup/ to backups/
  Write-Host "  Moving all items from backup/ to backups/..." -ForegroundColor Yellow

  if (-not $WhatIf) {
    Get-ChildItem ".\backup" -Recurse | ForEach-Object {
      $dest = $_.FullName.Replace("\backup\", "\backups\")
      $destDir = Split-Path $dest -Parent
      if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
      Move-Item $_.FullName $dest -Force
    }

    # Remove empty backup folder
    Remove-Item ".\backup" -Recurse -Force
    Write-Host "  Consolidated into backups/ and removed backup/ folder" -ForegroundColor Green
  }
} elseif ($hasBackup) {
  Write-Host "  Only 'backup' folder exists - renaming to 'backups'" -ForegroundColor Yellow
  if (-not $WhatIf) {
    Rename-Item ".\backup" "backups"
    Write-Host "  Renamed backup/ -> backups/" -ForegroundColor Green
  }
} elseif ($hasBackups) {
  Write-Host "  Only 'backups' folder exists - already consolidated" -ForegroundColor Green
} else {
  Write-Host "  No backup folders found" -ForegroundColor Gray
}

# 2) Clean old .bak files from config/
Write-Host "`n[2/2] Cleaning old .bak files from config/..." -ForegroundColor Yellow

if (Test-Path ".\config") {
  $bakFiles = Get-ChildItem ".\config" -Filter "*.bak*" -File

  if ($bakFiles.Count -gt 0) {
    Write-Host "  Found $($bakFiles.Count) .bak files:" -ForegroundColor Yellow
    foreach ($bak in $bakFiles) {
      Write-Host "    - $($bak.Name) ($($bak.Length) bytes)" -ForegroundColor Gray
    }

    if (-not $WhatIf) {
      $bakFiles | Remove-Item -Force
      Write-Host "  Deleted $($bakFiles.Count) .bak files" -ForegroundColor Green
    }
  } else {
    Write-Host "  No .bak files found in config/" -ForegroundColor Green
  }
} else {
  Write-Host "  config/ folder not found" -ForegroundColor Gray
}

# Summary
Write-Host "`n=== CLEANUP COMPLETE ===" -ForegroundColor Cyan
if ($WhatIf) {
  Write-Host "Preview complete. Run without -WhatIf to apply changes." -ForegroundColor Yellow
} else {
  Write-Host "Your SEC agent folder is now clean and ready for fine-tuning!" -ForegroundColor Green
}
Write-Host ""

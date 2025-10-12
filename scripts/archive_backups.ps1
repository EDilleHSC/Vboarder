<#
Safe backup archiver
- Scans for nested backup directories named 'backups' and moves them to archive/backups/<agent>/backup_<timestamp>[_n]
- Dry-run by default. Use -Execute to perform moves.
- Safety features:
  - Skips any path that already lives under the archive root
  - Ensures unique destination names by appending a counter
  - Prevents moving when destination would be a subdirectory of the source
  - Falls back to robocopy when Move-Item fails (helps with long paths)
#>

param(
    [switch]$Execute
)

$root = Get-Location
$archiveRoot = Join-Path $root 'archive' 'backups'

Write-Host "Archive root: $archiveRoot"

# Find directories explicitly named 'backups' (avoid pattern-matches that include 'backups' in other names)
$agentsBackups = Get-ChildItem -Directory -Recurse -Depth 6 -Force -ErrorAction SilentlyContinue | Where-Object { $_.Name -eq 'backups' }
if (-not $agentsBackups) {
    Write-Host "No 'backups' directories found under the repository." 
    exit 0
}

foreach ($dir in $agentsBackups) {
    # Skip anything already under the archive root
    if ($dir.FullName.StartsWith($archiveRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        Write-Host "Skipping already-archived path: $($dir.FullName)"
        continue
    }

    # Try to extract agent name from the path segment after 'agents\'
    $match = [regex]::Match($dir.FullName, "agents\\([^\\]+)")
    if ($match.Success) { $agentName = $match.Groups[1].Value } else { $agentName = 'unknown' }

    $destAgent = Join-Path $archiveRoot $agentName
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $baseFinal = Join-Path $destAgent ("backup_" + $timestamp)

    # Make final destination unique when collisions occur
    $finalDest = $baseFinal
    $counter = 1
    while (Test-Path $finalDest) {
        $finalDest = $baseFinal + "_" + $counter
        $counter++
    }

    Write-Host "Found backups for agent: $agentName -> $($dir.FullName)"
    Write-Host "Destination: $finalDest"

    if (-not $Execute) {
        Write-Host "Dry-run: would move $($dir.FullName) -> $finalDest"
        continue
    }

    # Ensure parent directories exist
    New-Item -ItemType Directory -Force -Path $destAgent | Out-Null
    New-Item -ItemType Directory -Force -Path $finalDest | Out-Null

    # Safety: avoid moving into a subdirectory of the source
    if ($finalDest.StartsWith($dir.FullName, [System.StringComparison]::OrdinalIgnoreCase)) {
        Write-Warning "Skipping move because destination is inside the source: $finalDest"
        continue
    }

    try {
        Move-Item -LiteralPath $dir.FullName -Destination $finalDest -Force -ErrorAction Stop
        Write-Host "Moved $($dir.FullName) -> $finalDest"
    } catch {
        Write-Warning "Move-Item failed: $($_.Exception.Message). Trying robocopy fallback."

        $src = $dir.FullName
        $dst = $finalDest

        # Ensure destination exists for robocopy
        New-Item -ItemType Directory -Force -Path $dst | Out-Null

        # Use robocopy to move files (robocopy handles longer paths on Windows better)
        $robocopyArgs = @($src, $dst, '/MOVE', '/E', '/NFL', '/NDL', '/NJH', '/NJS')
        $proc = Start-Process -FilePath 'robocopy.exe' -ArgumentList $robocopyArgs -Wait -NoNewWindow -PassThru

        # Robocopy exit codes: 0-7 are success variants; >=8 indicates failure
        if ($proc.ExitCode -le 7) {
            # Try to remove the source if robocopy didn't already remove it
            if (Test-Path $src) {
                try { Remove-Item -LiteralPath $src -Recurse -Force -ErrorAction SilentlyContinue } catch { Write-Warning "Failed to remove source after robocopy: $src" }
            }
            Write-Host "Robocopy moved $src -> $dst (exit code $($proc.ExitCode))"
        } else {
            Write-Error "Robocopy failed (exit code $($proc.ExitCode)). Source left at: $src"
        }
    }
}

Write-Host "Done." 

# Remove legacy agents/agents_v2 dir if present and commit the change
$path = Join-Path (Get-Location) 'agents\agents_v2'
if (Test-Path $path) {
    Write-Host "Removing $path"
    Remove-Item -Recurse -Force $path
    git add -A
    git commit -m "Remove legacy agents/agents_v2 after migration to agents/"
    Write-Host "Removed agents_v2 and committed changes. Don't forget to push: git push origin HEAD"
} else {
    Write-Host "No agents/agents_v2 path found. Nothing to remove."
}

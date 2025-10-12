<#
.SYNOPSIS
  Prepare and launch the full VBoarder environment
  Cleans old frontend, validates paths, and runs servers.
#>

# --- Configuration ---
$ProjectRoot   = "D:\ai\projects\vboarder"
$FrontendPath  = "$ProjectRoot\frontend"
$ApiScripts    = "$ProjectRoot\api\scripts\api_server.py"
$EnvFile       = "$ProjectRoot\.env"
$PortFrontend  = 5173
$PortBackend   = 8000
$HealthUrl     = "http://127.0.0.1:$PortBackend/health"

Write-Host "🧩 Setting up VBoarder Environment..." -ForegroundColor Cyan

# --- 1️⃣ Verify main paths ---
$paths = @($ProjectRoot, $FrontendPath, $ApiScripts, $EnvFile)
foreach ($p in $paths) {
    if (-not (Test-Path $p)) {
        Write-Host "❌ Missing path: $p" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ All required paths found." -ForegroundColor Green

# --- 2️⃣ Clean up old frontend files ---
Write-Host "🧹 Cleaning frontend folder..." -ForegroundColor Yellow
Get-ChildItem -Path $FrontendPath -Include *.html, *.log -Recurse -ErrorAction SilentlyContinue | Remove-Item -Force
Start-Sleep -Seconds 1
Write-Host "✅ Old frontend cleaned." -ForegroundColor Green

# --- 3️⃣ Ensure folder structure for assets ---
$AssetsPath = "$FrontendPath\assets\avatars"
if (-not (Test-Path $AssetsPath)) {
    New-Item -ItemType Directory -Path $AssetsPath | Out-Null
    Write-Host "📁 Created folder: $AssetsPath"
}

# --- 4️⃣ Verify .env variables ---
Write-Host "`n🔍 Checking .env configuration..." -ForegroundColor Cyan
$envLines = Get-Content $EnvFile
if ($envLines -notmatch "API_HOST") {
    Add-Content $EnvFile "API_HOST=127.0.0.1"
}
if ($envLines -notmatch "API_PORT") {
    Add-Content $EnvFile "API_PORT=$PortBackend"
}
if ($envLines -notmatch "QDRANT_URL") {
    Add-Content $EnvFile "QDRANT_URL=http://localhost:6333"
}
if ($envLines -notmatch "OLLAMA_URL") {
    Add-Content $EnvFile "OLLAMA_URL=http://localhost:11434"
}
Write-Host "✅ .env validated and updated." -ForegroundColor Green

# --- 5️⃣ Start backend API ---
Write-Host "`n🚀 Starting backend server (port $PortBackend)..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "cd '$ProjectRoot\api\scripts'; python api_server.py" -WindowStyle Minimized
Start-Sleep -Seconds 5

# --- 6️⃣ Test backend health ---
try {
    $health = Invoke-RestMethod -Uri $HealthUrl -TimeoutSec 5
    Write-Host "✅ Backend is responding: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Backend not responding yet at $HealthUrl" -ForegroundColor Yellow
}

# --- 7️⃣ Start local frontend server ---
Write-Host "`n🌐 Launching frontend server on port $PortFrontend ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "cd '$FrontendPath'; python -m http.server $PortFrontend" -WindowStyle Minimized

# --- 8️⃣ Open browser ---
Start-Sleep -Seconds 2
Start-Process "http://localhost:$PortFrontend"

Write-Host "`n🎉 VBoarder environment ready!"
Write-Host "🔹 Frontend: http://localhost:$PortFrontend"
Write-Host "🔹 Backend:  http://127.0.0.1:$PortBackend"
Write-Host "🔹 Health:   $HealthUrl"

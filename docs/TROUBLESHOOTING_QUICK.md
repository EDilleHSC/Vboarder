# 🔥 VBoarder Quick Troubleshooting Guide

**Last Updated:** October 14, 2025

---

## 🚨 Current Issue: "model 'mistral' not found"

### Root Cause

The backend is trying to use the `mistral` model, but it's not installed in Ollama.

### Quick Fix

**Step 1: Check if Ollama is running**

```powershell
# Windows - Check if Ollama service is running
Get-Service | Where-Object {$_.Name -like "*ollama*"}

# OR check process
Get-Process | Where-Object {$_.ProcessName -like "*ollama*"}
```

**Step 2: Install the mistral model**

```powershell
# If Ollama is installed but not in PATH, use full path:
& "C:\Users\$env:USERNAME\AppData\Local\Programs\Ollama\ollama.exe" pull mistral

# OR if Ollama is in PATH:
ollama pull mistral
```

**Step 3: Verify model installation**

```powershell
ollama list
```

Expected output:

```
NAME            ID              SIZE    MODIFIED
mistral:latest  abc123...       4.1 GB  2 hours ago
```

**Step 4: Test the fix**

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:3738/chat/CEO" `
  -Method POST `
  -Body '{"message":"Hello, can you hear me?"}' `
  -ContentType "application/json"
```

---

## 🎯 Alternative: Use a Different Model

If `mistral` download is too large or slow, you can use a smaller model:

### Option 1: Use llama3.2 (smaller, faster)

```powershell
ollama pull llama3.2:latest
```

Then update your agent configs to use `llama3.2` instead of `mistral`.

### Option 2: Use qwen2.5 (fast, good quality)

```powershell
ollama pull qwen2.5:latest
```

---

## 📋 Complete Diagnostic Checklist

### ✅ 1. Check Backend Status

```powershell
# Is backend running?
Get-NetTCPConnection -LocalPort 3738 -ErrorAction SilentlyContinue

# Backend health
Invoke-RestMethod -Uri "http://127.0.0.1:3738/health"
```

**Expected:** `{"status": "ok"}`

---

### ✅ 2. Check Ollama Status

**Windows (PowerShell):**

```powershell
# Check if Ollama is installed
Test-Path "C:\Users\$env:USERNAME\AppData\Local\Programs\Ollama\ollama.exe"

# Check Ollama process
Get-Process | Where-Object {$_.ProcessName -eq "ollama"}

# List installed models
& "C:\Users\$env:USERNAME\AppData\Local\Programs\Ollama\ollama.exe" list
```

**WSL/Linux:**

```bash
# Check if Ollama is running
pgrep ollama

# List installed models
ollama list

# Check Ollama API
curl http://localhost:11434/api/tags
```

---

### ✅ 3. Check Agent Configuration

```powershell
# View CEO agent config
Get-Content "agents\CEO\config.json" | ConvertFrom-Json
```

Check the `model` field - should match an installed Ollama model.

---

### ✅ 4. Check Python Environment

```powershell
# Verify Python version
python --version

# Check if virtual environment is active
$env:VIRTUAL_ENV

# Verify required packages
pip list | Select-String "fastapi|httpx|pydantic"
```

---

### ✅ 5. Check Logs

```powershell
# View backend logs
Get-Content "logs\backend.log" -Tail 50

# Check for errors
Get-Content "logs\backend.log" | Select-String "ERROR|Exception|Traceback"
```

---

## 🔧 Common Issues & Fixes

### Issue 1: Port Already in Use

**Symptom:**

```
Error: Address already in use
```

**Fix:**

```powershell
# Kill process on port 3738
$proc = Get-NetTCPConnection -LocalPort 3738 -ErrorAction SilentlyContinue
if ($proc) {
    Stop-Process -Id $proc.OwningProcess -Force
}

# Restart backend
.\start_vboarder.ps1
```

---

### Issue 2: Module Import Errors

**Symptom:**

```
ModuleNotFoundError: No module named 'fastapi'
```

**Fix:**

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

---

### Issue 3: Ollama Connection Timeout

**Symptom:**

```
Error communicating with Ollama: Connection timeout
```

**Fix:**

```powershell
# Check if Ollama is running
Get-Process ollama -ErrorAction SilentlyContinue

# If not running, start Ollama
Start-Process "ollama" -ArgumentList "serve"

# Wait a few seconds
Start-Sleep -Seconds 3

# Test connection
Invoke-RestMethod -Uri "http://localhost:11434/api/tags"
```

---

### Issue 4: Agent Registry Not Found

**Symptom:**

```
Agent role 'CEO' not found or registry failed to load
```

**Fix:**

```powershell
# Check if registry exists
Test-Path "agent_registry.json"

# View registry content
Get-Content "agent_registry.json" | ConvertFrom-Json

# If corrupted, restore from backup
Copy-Item "agents\agent_registry.json" "agent_registry.json" -Force
```

---

### Issue 5: Memory/Conversation Errors

**Symptom:**

```
Failed to write session file
```

**Fix:**

```powershell
# Ensure directories exist
New-Item -ItemType Directory -Force -Path "api\conversations"
New-Item -ItemType Directory -Force -Path "data"

# Check permissions
Get-Acl "api\conversations"

# Clear old sessions (if needed)
Remove-Item "api\conversations\*.json" -Force
```

---

## 🧪 Quick Smoke Test Script

Save as `test_vboarder.ps1`:

```powershell
Write-Host "🧪 VBoarder Smoke Test" -ForegroundColor Cyan

# Test 1: Health
Write-Host "`n1️⃣  Testing backend health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://127.0.0.1:3738/health"
    if ($health.status -eq "ok") {
        Write-Host "   ✅ Health check passed" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Health check failed" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Backend not responding: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Agents
Write-Host "`n2️⃣  Testing agents endpoint..." -ForegroundColor Yellow
try {
    $agents = Invoke-RestMethod -Uri "http://127.0.0.1:3738/agents"
    Write-Host "   ✅ Found $($agents.count) agents: $($agents.agents -join ', ')" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Agents endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Ollama
Write-Host "`n3️⃣  Testing Ollama..." -ForegroundColor Yellow
try {
    $ollama = Invoke-RestMethod -Uri "http://localhost:11434/api/tags"
    $models = $ollama.models | ForEach-Object { $_.name }
    Write-Host "   ✅ Ollama running with models: $($models -join ', ')" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Ollama not responding: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: CEO Chat
Write-Host "`n4️⃣  Testing CEO chat..." -ForegroundColor Yellow
try {
    $chat = Invoke-RestMethod -Uri "http://127.0.0.1:3738/chat/CEO" `
        -Method POST `
        -Body '{"message":"Say hello in 5 words or less"}' `
        -ContentType "application/json"

    if ($chat.response -notlike "*Error*") {
        Write-Host "   ✅ CEO responded: $($chat.response)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  CEO responded with error: $($chat.response)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ Chat failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n✅ Smoke test complete!`n" -ForegroundColor Cyan
```

---

## 📞 Getting Help

If issues persist:

1. **Check logs:** `logs/backend.log`
2. **Run smoke test:** `.\test_vboarder.ps1`
3. **Restart everything:**

   ```powershell
   .\stop_vboarder.ps1
   Start-Sleep -Seconds 2
   .\start_vboarder.ps1
   ```

4. **Report issues:**
   - Include error messages from logs
   - Include output from `ollama list`
   - Include output from `pip list`
   - Include Python version: `python --version`

---

## 🎯 Next Steps

Once Ollama model is installed:

1. ✅ Test all 9 agents
2. ✅ Test session persistence
3. ✅ Test streaming chat
4. ✅ Test memory endpoints
5. ✅ Test frontend (if applicable)

**Happy testing!** 🚀

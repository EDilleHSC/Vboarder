# 🚀 VBoarder Backend Quick Start (Manual Steps)

**Issue:** Virtual environment has corrupted scripts with Unix paths
**Solution:** Follow these manual steps to get backend running

---

## Option 1: Recreate Virtual Environment (BEST)

Open PowerShell and run:

```powershell
# Navigate to project
cd D:\ai\projects\vboarder

# Remove old venv
Remove-Item -Recurse -Force .venv

# Find Python (try these commands until one works)
py --version
python --version
python3 --version

# Create new venv (replace 'python' with whatever worked above)
python -m venv .venv

# Activate it
.\.venv\Scripts\Activate.ps1

# You should see (.venv) in your prompt now

# Install all dependencies
pip install -r requirements.txt

# Verify ollama is installed
python -c "import ollama; print('Ollama OK')"

# Start backend
python -m uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload
```

---

## Option 2: Use Conda (If Available)

```powershell
cd D:\ai\projects\vboarder

# Create conda environment
conda create -n vboarder python=3.11 -y
conda activate vboarder

# Install dependencies
pip install -r requirements.txt

# Start backend
python -m uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload
```

---

## Option 3: System Python (Quick & Dirty)

```powershell
cd D:\ai\projects\vboarder

# Install globally (not ideal but works)
pip install fastapi==0.110.0 uvicorn==0.29.0 ollama==0.1.0 pydantic==2.6.4 python-dotenv aiofiles asyncpg openai httpx

# Start backend
python -m uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload
```

---

## Option 4: Use WSL/Linux

```bash
# In WSL terminal
cd /mnt/d/ai/projects/vboarder

# Create venv
python3 -m venv .venv-wsl
source .venv-wsl/bin/activate

# Install deps
pip install -r requirements.txt

# Start backend
uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload
```

---

## ✅ Success Indicators

When backend starts successfully, you'll see:

```
INFO:     Uvicorn running on http://127.0.0.1:3738 (Press CTRL+C to quit)
INFO:     Started reloader process [12345]
INFO:     Started server process [67890]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Test it:

```powershell
# PowerShell
Invoke-RestMethod -Uri "http://127.0.0.1:3738/health"

# Or use curl (if installed)
curl http://127.0.0.1:3738/health
```

Expected response:

```json
{ "status": "ok" }
```

---

## 🔧 Troubleshooting

### Python Not Found

```powershell
# Try these commands to find Python:
py --version
python --version
python3 --version

# If none work, install Python 3.11+ from:
# https://www.python.org/downloads/
```

### Module Not Found: ollama

```powershell
pip install ollama
```

### Port Already in Use

```powershell
# Use different port
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload

# Then update frontend .env.local:
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Import Errors

```powershell
# Verify all dependencies
python -c "import fastapi, uvicorn, ollama, pydantic; print('All OK')"

# If any fail, reinstall requirements
pip install -r requirements.txt --force-reinstall
```

---

## 🎯 After Backend is Running

### Start Frontend

```powershell
# New terminal
cd D:\ai\projects\vboarder\vboarder_frontend\nextjs_space

# Install dependencies (if needed)
npm install

# Start dev server
npm run dev
```

### Test Full Stack

1. Open browser: http://localhost:3000
2. Select CEO agent
3. Send message: "Hello, test message"
4. Verify streaming response appears

---

## 📝 Summary

**The Issue:** Your `.venv` has corrupted scripts with Unix paths (`/usr/bin/python.exe`)

**The Fix:** Recreate venv using **Option 1** above (most reliable)

**Required Packages:**

- fastapi==0.110.0
- uvicorn==0.29.0
- **ollama==0.1.0** ← This was missing
- pydantic==2.6.4
- python-dotenv
- aiofiles
- asyncpg
- openai
- httpx

**Backend Command:**

```
python -m uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload
```

---

## 💡 Next Time

To avoid this issue in the future:

- Always create venvs on the same OS you'll run them on
- Don't copy `.venv` folders between Windows/Linux
- Use `requirements.txt` to recreate environments
- Consider using Docker for consistent environments

---

**Need Help?** Check full troubleshooting guide: `docs/BACKEND_LAUNCH_TROUBLESHOOTING.md`

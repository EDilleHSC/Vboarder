# VBoarder WSL Setup Guide

## ✅ Why WSL?

VBoarder requires:

- **Bash scripts** (`start_vboarder.sh`, `stop_vboarder.sh`)
- **Ollama** (Linux-native LLM server)
- **Python virtual environments** with `source` activation
- **Unix utilities** (`curl`, `jq`, etc.)

**Windows PowerShell cannot run these natively.**

---

## 🚀 Quick Setup (5 Minutes)

### Step 1: Open WSL Terminal in VS Code

#### Option A: New WSL Window

1. Press `Ctrl + Shift + P`
2. Type: `WSL: New WSL Window`
3. Select your WSL distribution (Ubuntu recommended)

#### Option B: Terminal Dropdown

1. Press `` Ctrl + ` `` (backtick) to open terminal
2. Click the `▼` dropdown next to `+`
3. Select **Ubuntu (WSL)** or **WSL**

#### Option C: Set WSL as Default (Recommended)

1. `Ctrl + ,` to open Settings
2. Search: `terminal.integrated.defaultProfile.windows`
3. Set to: `Ubuntu (WSL)` or `WSL`

Or add to `settings.json`:

```json
{
  "terminal.integrated.defaultProfile.windows": "WSL"
}
```

---

### Step 2: Verify WSL Environment

Once in WSL terminal (you'll see `user@DESKTOP:/mnt/d/ai/projects/vboarder$`):

```bash
# Check current directory
pwd
# Should show: /mnt/d/ai/projects/vboarder

# Navigate if needed
cd /mnt/d/ai/projects/vboarder

# Verify tools
which python3
which bash
which curl
```

---

### Step 3: Install Ollama in WSL

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version

# Pull required models (VBoarder uses mistral, NOT mixtral)
ollama pull mistral
ollama pull llama3

# Verify models
ollama list
```

**Expected output:**

```text
NAME            ID              SIZE    MODIFIED
mistral:latest  abc123def456    4.1 GB  2 hours ago
llama3:latest   def456abc789    4.7 GB  2 hours ago
```

---

### Step 4: Set Up Python Virtual Environment (WSL)

```bash
# Check Python version
python3 --version
# Should be 3.10+

# Create virtual environment
python3 -m venv .venv-wsl

# Activate (WSL/Linux uses 'source', not PowerShell's &)
source .venv-wsl/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print('FastAPI installed!')"
```

---

## 🎮 Running VBoarder in WSL

### Start Services

```bash
# Make scripts executable
chmod +x start_vboarder.sh stop_vboarder.sh

# Start Ollama (background service)
ollama serve &

# Wait 2 seconds for Ollama to initialize
sleep 2

# Start VBoarder
bash start_vboarder.sh
```

**What you should see:**

```text
🚀 Starting VBoarder Environment...
🐍 Activating Python virtual environment...
✅ Virtual environment activated
🧠 Ollama is already running
⚙️  Launching backend on http://127.0.0.1:3738
✅ VBoarder is live!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Backend:  http://127.0.0.1:3738
Health:   http://127.0.0.1:3738/health
Frontend: http://localhost:3001
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🧪 Testing the System

### 1. Health Check

```bash
curl http://127.0.0.1:3738/health
```

**Expected:** `{"status":"ok"}`

### 2. List Agents

```bash
curl http://127.0.0.1:3738/agents
```

**Expected:** `{"agents":["AIR","CEO","CFO",...], "count":9}`

### 3. Chat with CEO

```bash
curl -X POST http://127.0.0.1:3738/chat/CEO \
  -H "Content-Type: application/json" \
  -d '{"message":"What are our top 3 strategic priorities this week?"}'
```

**Expected:** JSON response with CEO's strategic analysis

---

## 🐛 Troubleshooting

### Issue: "ollama: command not found"

**Fix in WSL:**

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Issue: "python: command not found"

**Fix in WSL:**

```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### Issue: "Permission denied" on scripts

**Fix:**

```bash
chmod +x start_vboarder.sh stop_vboarder.sh
chmod +x tools/ops/*.sh
```

### Issue: Port 3738 already in use

**Fix:**

```bash
# Find process on port
lsof -i :3738

# Kill it
kill -9 $(lsof -t -i :3738)

# Or use the stop script
bash stop_vboarder.sh
```

### Issue: Virtual environment not activating

**Fix:**

```bash
# Deactivate any active venv
deactivate

# Remove old venv
rm -rf .venv .venv-wsl

# Create fresh WSL venv
python3 -m venv .venv-wsl

# Activate
source .venv-wsl/bin/activate

# Reinstall
pip install -r requirements.txt
```

---

## ⚡ Quick Commands Reference

```bash
# Start everything
bash start_vboarder.sh

# Stop everything
bash stop_vboarder.sh

# Check backend status
curl http://127.0.0.1:3738/health

# View backend logs
tail -f logs/backend.log

# Test all agents
bash tools/ops/test-all-agents.sh

# Pull latest models
ollama pull mistral
ollama pull llama3
```

---

## 📝 Key Differences: PowerShell vs WSL

| Task            | PowerShell ❌                            | WSL ✅                          |
| --------------- | ---------------------------------------- | ------------------------------- |
| Activate venv   | `.\.venv\Scripts\Activate.ps1`           | `source .venv-wsl/bin/activate` |
| Run bash script | `bash script.sh` (if Git Bash installed) | `bash script.sh`                |
| Ollama          | Requires separate Windows install        | Native Linux install            |
| Path separator  | `\` (backslash)                          | `/` (forward slash)             |
| Python command  | `python`                                 | `python3`                       |
| Line endings    | CRLF                                     | LF                              |

---

## 🎯 Final Checklist

After setup, verify:

```bash
# 1. WSL terminal active
echo $SHELL
# Should show: /bin/bash

# 2. In project directory
pwd
# Should show: /mnt/d/ai/projects/vboarder

# 3. Virtual environment active
which python
# Should show: /mnt/d/ai/projects/vboarder/.venv-wsl/bin/python

# 4. Ollama installed
ollama list
# Should list: mistral, llama3

# 5. VBoarder running
curl http://127.0.0.1:3738/health
# Should return: {"status":"ok"}
```

✅ **All checks pass?** You're ready for beta testing!

---

## 📞 Support

**Still having issues?** Run the diagnostic:

```bash
bash tools/ops/verify-agent-setup.sh
```

This will check all requirements and report any issues.

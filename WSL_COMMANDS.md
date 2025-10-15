# VBoarder Quick Command Reference (WSL)

## 🚀 Getting Started

```bash
# 1. Open WSL terminal in VS Code
# Press: Ctrl + Shift + P → "WSL: New WSL Window"

# 2. Navigate to project
cd /mnt/d/ai/projects/vboarder

# 3. Activate virtual environment
source .venv-wsl/bin/activate

# 4. Start Ollama (background)
ollama serve &

# 5. Start VBoarder
bash start_vboarder.sh
```

## 🧪 Quick Tests

```bash
# Health check
curl http://127.0.0.1:3738/health

# List agents
curl http://127.0.0.1:3738/agents

# Chat with CEO
curl -X POST http://127.0.0.1:3738/chat/CEO \
  -H "Content-Type: application/json" \
  -d '{"message":"What are our top 3 priorities?"}'
```

## 🛠️ Common Commands

```bash
# Stop services
bash stop_vboarder.sh

# View logs
tail -f logs/backend.log

# Check environment
bash wsl_quick_check.sh

# Test all agents
bash tools/ops/test-all-agents.sh
```

## 📦 Ollama Management

```bash
# List models
ollama list

# Pull model
ollama pull mistral

# Check if Ollama running
pgrep -x "ollama"

# Start Ollama
ollama serve &

# Stop Ollama
pkill ollama
```

## 🐛 Troubleshooting

```bash
# Check Python
which python3
python3 --version

# Check venv activation
echo $VIRTUAL_ENV

# Check port usage
lsof -i :3738

# Kill process on port
kill -9 $(lsof -t -i :3738)

# Verify agent files
ls -la agents/CEO/
ls -la agents/CTO/
```

## ⚡ One-Liners

```bash
# Full restart
bash stop_vboarder.sh && sleep 2 && bash start_vboarder.sh

# Quick health check
curl -s http://127.0.0.1:3738/health | jq

# List all agents
curl -s http://127.0.0.1:3738/agents | jq

# Test CEO chat
curl -s -X POST http://127.0.0.1:3738/chat/CEO \
  -H "Content-Type: application/json" \
  -d '{"message":"Status report"}' | jq .response
```

## 📍 Key Paths

```bash
# Project root
/mnt/d/ai/projects/vboarder

# Virtual environment
.venv-wsl/

# Agents
agents/CEO/
agents/CTO/
agents/CFO/
...

# Logs
logs/backend.log

# Configuration
agent_registry.json
api/main.py
```

## 🔑 Important Notes

- ✅ **Always use WSL terminal**, not PowerShell
- ✅ **Activate venv** before running Python: `source .venv-wsl/bin/activate`
- ✅ **Start Ollama first**: `ollama serve &`
- ✅ **Use `mistral` model**, NOT `mixtral`
- ✅ **Scripts are in bash**: `bash script.sh`, not `./script.sh` (unless executable)

#!/usr/bin/env bash
# Force kill all uvicorn processes and start fresh

# Get project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

echo "� Project: $PROJECT_ROOT"
echo ""

echo "�🔍 Finding uvicorn processes..."
PIDS=$(ps aux | grep uvicorn | grep -v grep | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "✅ No uvicorn processes found"
else
    echo "Found uvicorn processes: $PIDS"
    for PID in $PIDS; do
        echo "Killing process $PID..."
        kill -9 $PID 2>/dev/null || sudo kill -9 $PID 2>/dev/null
    done
    echo "✅ All uvicorn processes killed"
    sleep 1
fi

echo ""
echo "🐍 Activating virtual environment..."
if [ -f ".venv-wsl/bin/activate" ]; then
    source .venv-wsl/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ .venv-wsl not found!"
    exit 1
fi

echo ""
echo "🚀 Starting fresh backend..."
uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload

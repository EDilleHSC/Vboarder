#!/usr/bin/env bash
# =========================================================
# 🚀 VBoarder Backend Restart Script
# Version: 1.0.0
# Author: Eric Dille (Automated by GPT-5)
# =========================================================

PROJECT_DIR="/mnt/d/ai/projects/vboarder"
VENV_DIR="$PROJECT_DIR/.venv"
LOG_DIR="$PROJECT_DIR/logs"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="$LOG_DIR/backend_restart_$TIMESTAMP.log"

mkdir -p "$LOG_DIR"

echo "------------------------------------"
echo "🧠 Restarting VBoarder Backend"
echo "🕒 Timestamp: $TIMESTAMP"
echo "------------------------------------"

# Stop any active backend
echo "🧹 Cleaning port 8000..."
sudo lsof -t -i:8000 | xargs kill -9 2>/dev/null || true

# Activate environment
echo "⚙️  Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Start backend
echo "🚀 Launching backend..."
nohup python3 "$PROJECT_DIR/server.py" > "$LOG_FILE" 2>&1 &

sleep 2

# Check if started
if sudo lsof -i:8000 > /dev/null 2>&1; then
    echo "✅ Backend started successfully."
    echo "📄 Log file: $LOG_FILE"
else
    echo "❌ Backend failed to start. Check log file for details:"
    echo "   $LOG_FILE"
fi

echo "------------------------------------"

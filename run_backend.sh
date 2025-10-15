#!/bin/bash
# ====================================================
# 🚀 VBoarder Backend Startup Script
# ----------------------------------------------------
# Cleans old processes, activates venv, and launches
# FastAPI backend on port 8000
# ====================================================

echo "🧹 Cleaning up old Uvicorn processes on port 8000..."
sudo kill -9 $(sudo lsof -t -i:8000) 2>/dev/null || true

echo "🚀 Starting VBoarder backend..."
cd /mnt/d/ai/projects/vboarder
#!/bin/bash
# ====================================================
# 🚀 VBoarder Backend Startup Script
# ----------------------------------------------------
# Cleans old processes, activates venv, and launches
# FastAPI backend on port 8000
# ====================================================

echo "🧹 Cleaning up old Uvicorn processes on port 8000..."
sudo kill -9 $(sudo lsof -t -i:8000) 2>/dev/null || true

echo "🚀 Starting VBoarder backend..."
cd /mnt/d/ai/projects/vboarder
source .venv/bin/activate

LOG_DIR="./logs"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')
LOG_FILE="$LOG_DIR/backend_$TIMESTAMP.log"

echo "🧠 Logging to $LOG_FILE"
echo "----------------------------------------"
echo "🧠 VBOARDER BACKEND START $(date)" > "$LOG_FILE"

python3 -m uvicorn server:app --reload --host 0.0.0.0 --port 8000 2>&1 | tee -a "$LOG_FILE"

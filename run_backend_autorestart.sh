#!/bin/bash
# ====================================================
# 🚀 VBoarder Backend - Auto-Restart + Live Log + Health Monitor (v3.4)
# ====================================================

PROJECT_DIR="/mnt/d/ai/projects/vboarder"
LOG_DIR="$PROJECT_DIR/logs"
PORT=8000
HEALTH_URL="http://localhost:$PORT/api/health"

mkdir -p "$LOG_DIR"

trap 'echo "🧹 Received interrupt. Shutting down backend monitor."; exit 0' SIGINT SIGTERM

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')
    LOG_FILE="$LOG_DIR/backend_$TIMESTAMP.log"

    echo "🧹 Cleaning port $PORT..."
    sudo kill -9 $(sudo lsof -t -i:$PORT) 2>/dev/null || true

    echo "🚀 Starting backend at $TIMESTAMP..."
    cd "$PROJECT_DIR"
    source .venv/bin/activate

    {
        echo "========================================"
        echo "🧠 BACKEND START $(date)"
        echo "Project Dir: $PROJECT_DIR"
        echo "Log File: $LOG_FILE"
        echo "----------------------------------------"
    } | tee -a "$LOG_FILE"

    # Run uvicorn and stream logs both to file and console
    python3 -m uvicorn server:app \
        --host 0.0.0.0 \
        --port $PORT \
        --workers 1 \
        --log-level info 2>&1 | tee -a "$LOG_FILE" &
    
    BACKEND_PID=$!
    echo "🟢 Backend started with PID $BACKEND_PID"

    # 🩺 Health monitoring loop (runs while backend is alive)
    while kill -0 $BACKEND_PID 2>/dev/null; do
        sleep 60
        if ! curl -s "$HEALTH_URL" | grep -q '"status":"ok"'; then
            echo "⚠️  Health check failed at $(date). Restarting backend..." | tee -a "$LOG_FILE"
            sudo kill -9 $BACKEND_PID 2>/dev/null || true
            break
        else
            echo "✅ Health check OK at $(date)" | tee -a "$LOG_FILE"
        fi
    done

    wait $BACKEND_PID
    EXIT_CODE=$?
    echo "❌ Backend exited with code $EXIT_CODE at $(date). Restarting in 10 seconds..." | tee -a "$LOG_FILE"
    sleep 10
done
# ========================================================
# 🧩 System Resource Tracker - Log every 60 seconds
# ========================================================
LOG_DIR="/mnt/d/ai/projects/vboarder/logs"
STATS_LOG="$LOG_DIR/system_uptime.log"

# ensure log dir exists
mkdir -p "$LOG_DIR"

echo "📈 Starting system resource tracker..."
(
  while true; do
    timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    # Capture uptime, CPU %, and memory usage summary
    uptime_info=$(uptime | awk -F'up ' '{print $2}' | cut -d',' -f1)
    cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print 100 - $8"%"}')
    mem_usage=$(free -h | awk '/Mem:/ {print $3 "/" $2}')
    echo "$timestamp | Uptime: $uptime_info | CPU: $cpu_usage | MEM: $mem_usage" >> "$STATS_LOG"
    sleep 60
  done
) &

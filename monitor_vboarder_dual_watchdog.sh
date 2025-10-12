#!/usr/bin/env bash
# =========================================================
# 🧠 VBoarder Dual Watchdog Monitor (Backend + Ollama)
# Version: 2.0.0
# =========================================================

PROJECT_DIR="/mnt/d/ai/projects/vboarder"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/dual_watchdog.log"
BACKEND_HEALTH="http://localhost:8000/api/health"
OLLAMA_HEALTH="http://localhost:11434/api/tags"
RESTART_BACKEND="$PROJECT_DIR/restart_vboarder.sh"
OLLAMA_SERVICE="ollama"
MAX_FAILS=3
BACKEND_FAILS=0
OLLAMA_FAILS=0

mkdir -p "$LOG_DIR"

echo "------------------------------------"
echo "🧠 Starting Dual Watchdog Monitor"
echo "📄 Logging to: $LOG_FILE"
echo "------------------------------------"
echo "$(date '+%Y-%m-%d %H:%M:%S') | 🟢 Dual Watchdog started | Max failures: $MAX_FAILS" >> "$LOG_FILE"

while true; do
    # ===============================
    # 🧩 BACKEND HEALTH CHECK
    # ===============================
    BACKEND_STATUS=$(curl -s -m 10 "$BACKEND_HEALTH" | jq -r '.status' 2>/dev/null)
    if [[ "$BACKEND_STATUS" == "ok" ]]; then
        if [[ "$BACKEND_FAILS" -gt 0 ]]; then
            echo "$(date '+%Y-%m-%d %H:%M:%S') | ✅ Backend recovered after $BACKEND_FAILS fails" >> "$LOG_FILE"
        fi
        BACKEND_FAILS=0
    else
        ((BACKEND_FAILS++))
        echo "$(date '+%Y-%m-%d %H:%M:%S') | ⚠️ Backend health check failed ($BACKEND_FAILS/$MAX_FAILS)" >> "$LOG_FILE"
        if [[ "$BACKEND_FAILS" -ge "$MAX_FAILS" ]]; then
            echo "$(date '+%Y-%m-%d %H:%M:%S') | 🔁 Restarting backend (failure threshold reached)" >> "$LOG_FILE"
            bash "$RESTART_BACKEND"
            BACKEND_FAILS=0
            sleep 30
        fi
    fi

    # ===============================
    # 🧩 OLLAMA HEALTH CHECK
    # ===============================
    OLLAMA_STATUS=$(curl -s -m 10 "$OLLAMA_HEALTH" | jq -r '.models[0].name' 2>/dev/null)
    if [[ -n "$OLLAMA_STATUS" ]]; then
        if [[ "$OLLAMA_FAILS" -gt 0 ]]; then
            echo "$(date '+%Y-%m-%d %H:%M:%S') | ✅ Ollama recovered after $OLLAMA_FAILS fails" >> "$LOG_FILE"
        fi
        OLLAMA_FAILS=0
    else
        ((OLLAMA_FAILS++))
        echo "$(date '+%Y-%m-%d %H:%M:%S') | ⚠️ Ollama health check failed ($OLLAMA_FAILS/$MAX_FAILS)" >> "$LOG_FILE"
        if [[ "$OLLAMA_FAILS" -ge "$MAX_FAILS" ]]; then
            echo "$(date '+%Y-%m-%d %H:%M:%S') | 🔁 Restarting Ollama service (failure threshold reached)" >> "$LOG_FILE"
            sudo systemctl restart "$OLLAMA_SERVICE" 2>/dev/null || {
                # fallback for WSL/local install
                pkill ollama
                nohup ollama serve > /dev/null 2>&1 &
                echo "$(date '+%Y-%m-%d %H:%M:%S') | 🟢 Ollama restarted manually (WSL mode)" >> "$LOG_FILE"
            }
            OLLAMA_FAILS=0
            sleep 30
        fi
    fi

    sleep 60
done

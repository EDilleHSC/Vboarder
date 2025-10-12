#!/usr/bin/env bash
# =========================================================
# 🧠 VBoarder Self-Healing Watchdog Monitor
# Version: 1.0.0
# Checks system metrics & health, restarts backend if needed.
# =========================================================

PROJECT_DIR="/mnt/d/ai/projects/vboarder"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/watchdog.log"
HEALTH_URL="http://localhost:8000/api/health"
RESTART_SCRIPT="$PROJECT_DIR/restart_vboarder.sh"
MAX_FAILURES=3
FAIL_COUNT=0

mkdir -p "$LOG_DIR"

echo "------------------------------------"
echo "🧠 Starting VBoarder Watchdog"
echo "📄 Logging to: $LOG_FILE"
echo "------------------------------------"

echo "$(date '+%Y-%m-%d %H:%M:%S') | 🟢 Watchdog started | Max failures allowed: $MAX_FAILURES" >> "$LOG_FILE"

while true; do
    RESPONSE=$(curl -s -m 10 "$HEALTH_URL")
    STATUS=$(echo "$RESPONSE" | jq -r '.status' 2>/dev/null)

    if [[ "$STATUS" == "ok" ]]; then
        # Healthy — reset failure counter
        if [[ "$FAIL_COUNT" -gt 0 ]]; then
            echo "$(date '+%Y-%m-%d %H:%M:%S') | ✅ System recovered | Previous fails: $FAIL_COUNT" >> "$LOG_FILE"
        fi
        FAIL_COUNT=0
    else
        # Health check failed
        ((FAIL_COUNT++))
        echo "$(date '+%Y-%m-%d %H:%M:%S') | ⚠️ Health check failed ($FAIL_COUNT/$MAX_FAILURES)" >> "$LOG_FILE"

        if [[ "$FAIL_COUNT" -ge "$MAX_FAILURES" ]]; then
            echo "$(date '+%Y-%m-%d %H:%M:%S') | 🔁 Restarting backend (failure threshold reached)" >> "$LOG_FILE"
            bash "$RESTART_SCRIPT"
            FAIL_COUNT=0
            sleep 30  # Give backend time to restart
        fi
    fi

    sleep 60
done

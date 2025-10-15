#!/usr/bin/env bash
# =========================================================
# 📈 VBoarder System Monitor
# Version: 1.0.0
# Logs CPU & memory metrics to a timestamped file every 60 sec.
# =========================================================

PROJECT_DIR="/mnt/d/ai/projects/vboarder"
LOG_DIR="$PROJECT_DIR/logs"
LOG_FILE="$LOG_DIR/system_perf.log"
API_URL="http://localhost:8000/api/system/metrics"

mkdir -p "$LOG_DIR"

echo "------------------------------------"
echo "🧠 Starting VBoarder System Monitor"
echo "📄 Logging to: $LOG_FILE"
echo "------------------------------------"

echo "timestamp,cpu_percent,memory_used,memory_total,memory_percent,uptime_min" > "$LOG_FILE"

while true; do
    DATA=$(curl -s "$API_URL")
    TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

    CPU=$(echo "$DATA" | jq -r '.cpu_percent')
    USED=$(echo "$DATA" | jq -r '.memory_used')
    TOTAL=$(echo "$DATA" | jq -r '.memory_total')
    PCT=$(echo "$DATA" | jq -r '.memory_percent')
    UPTIME=$(echo "$DATA" | jq -r '.uptime_min')

    echo "$TIMESTAMP,$CPU,$USED,$TOTAL,$PCT,$UPTIME" >> "$LOG_FILE"

    sleep 60
done

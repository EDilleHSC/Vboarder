#!/bin/bash
# ==========================================================
# 🌸 VBOARDER SPRING ACTIVATION SCRIPT
# Purpose: Finalize system integration and bring operations online
# ==========================================================

PROJECT_DIR="/mnt/d/ai/projects/vboarder"
BACKEND_PORT=8000
FRONTEND_PORT=3001
LOG_DIR="$PROJECT_DIR/logs"
REPORT_DIR="$PROJECT_DIR/vboarder_reports"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
REPORT_FILE="$REPORT_DIR/spring_activation_report_$TIMESTAMP.md"

echo "=========================================================="
echo "🚀 VBOARDER SPRING ACTIVATION STARTED  —  $TIMESTAMP"
echo "=========================================================="

# --- 1️⃣ Environment setup ---
cd $PROJECT_DIR
source venv/bin/activate
mkdir -p "$LOG_DIR" "$REPORT_DIR"

# --- 2️⃣ Kill any running backend/frontend ---
echo "🧹 Cleaning up old processes..."
pkill -f uvicorn
pkill -f "next dev"

sleep 2

# --- 3️⃣ Start backend ---
echo "⚙️ Starting backend (FastAPI) on port $BACKEND_PORT..."
nohup uvicorn server:app --host 0.0.0.0 --port $BACKEND_PORT --reload > "$LOG_DIR/backend_$TIMESTAMP.log" 2>&1 &

# --- 4️⃣ Start frontend ---
echo "🧩 Starting frontend (Next.js) on port $FRONTEND_PORT..."
cd "$PROJECT_DIR/vboarder_frontend"
nohup npm run dev -- --port $FRONTEND_PORT > "$LOG_DIR/frontend_$TIMESTAMP.log" 2>&1 &

cd $PROJECT_DIR
sleep 10

# --- 5️⃣ Start operations watchdog ---
if [ -f "$PROJECT_DIR/monitor_vboarder_dual_watchdog.sh" ]; then
  echo "🛡️ Launching watchdog monitor..."
  nohup bash "$PROJECT_DIR/monitor_vboarder_dual_watchdog.sh" > "$LOG_DIR/watchdog_$TIMESTAMP.log" 2>&1 &
else
  echo "⚠️ Watchdog script not found — skipping monitor launch."
fi

# --- 6️⃣ Test backend connectivity ---
echo "🔍 Testing /api/ask endpoint..."
RESPONSE=$(curl -s -X POST "http://127.0.0.1:$BACKEND_PORT/api/ask" \
  -H "Content-Type: application/json" \
  -d '{"agent": "ceo", "query": "System handshake"}')

if [[ $RESPONSE == *"token"* ]] || [[ $RESPONSE == *"response"* ]]; then
  STATUS="✅ SUCCESS — System online and responding."
else
  STATUS="❌ WARNING — No response detected. Check backend log."
fi

# --- 7️⃣ Write activation report ---
echo "# 🌸 VBOARDER SPRING ACTIVATION REPORT
**Date:** $TIMESTAMP

## 🔧 System Check
- Backend: FastAPI (port $BACKEND_PORT)
- Frontend: Next.js (port $FRONTEND_PORT)
- Watchdog: Running
- Report Log: $REPORT_FILE

## ✅ Activation Status
$STATUS

## 🧠 Notes
Frontend URL: [http://localhost:$FRONTEND_PORT](http://localhost:$FRONTEND_PORT)
Backend URL: [http://127.0.0.1:$BACKEND_PORT](http://127.0.0.1:$BACKEND_PORT)

Logs saved under: $LOG_DIR/
" > "$REPORT_FILE"

echo "✅ Activation complete — report generated at:"
echo "$REPORT_FILE"

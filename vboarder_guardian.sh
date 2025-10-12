#!/usr/bin/env bash
# ===============================================================
# 🧠 VBoarder Guardian Supervisor v2.0
# Cinematic logging + color-coded statuses
# Keeps backend & monitor alive, auto-recovers on crash.
# ===============================================================

PROJECT_DIR="/mnt/d/ai/projects/vboarder"
VENV_DIR="$PROJECT_DIR/.venv"
LOG_DIR="$PROJECT_DIR/logs"
GUARDIAN_LOG="$LOG_DIR/guardian.log"
PORT=8000
CHECK_INTERVAL=60
MAX_RETRIES=3

mkdir -p "$LOG_DIR"

# --- 🎨 Terminal Colors ---
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
CYAN="\033[0;36m"
MAGENTA="\033[0;35m"
RESET="\033[0m"

# --- 🧭 Stylish Banner ---
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}" >> "$GUARDIAN_LOG"
echo -e "${CYAN}$(date '+📅  %A, %B %d %Y  ⏰  %I:%M:%S %p')${RESET}" >> "$GUARDIAN_LOG"
echo -e "${GREEN}🛡️  VBoarder Guardian Supervisor — Cinematic Log Mode${RESET}" >> "$GUARDIAN_LOG"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}" >> "$GUARDIAN_LOG"

# --- 🧰 Helpers ---
function log() {
    local STATUS=$1
    local MSG=$2
    local TIME=$(date '+%H:%M:%S')
    case $STATUS in
        "OK")    COLOR=$GREEN; ICON="🟢" ;;
        "WARN")  COLOR=$YELLOW; ICON="🟡" ;;
        "FAIL")  COLOR=$RED; ICON="🔴" ;;
        "INFO")  COLOR=$CYAN; ICON="🔹" ;;
        *)       COLOR=$RESET; ICON="🔸" ;;
    esac
    echo -e "${COLOR}${TIME} | ${ICON} ${MSG}${RESET}" | tee -a "$GUARDIAN_LOG"
}

function check_backend_alive() {
    curl -s http://localhost:$PORT/api/health | grep -q '"status":"ok"'
}

function start_backend() {
    log INFO "Launching backend server..."
    cd "$PROJECT_DIR"
    source "$VENV_DIR/bin/activate"
    nohup python3 server.py >> "$LOG_DIR/backend_guardian.log" 2>&1 &
    sleep 5
    if check_backend_alive; then
        log OK "Backend successfully restarted ✅"
        return 0
    else
        log FAIL "Backend failed to start ❌"
        return 1
    fi
}

function kill_backend() {
    log WARN "Terminating stale backend processes..."
    sudo lsof -t -i:$PORT | xargs kill -9 2>/dev/null || true
}

# --- 🧠 Main Watch Loop ---
FAIL_COUNT=0
while true; do
    if check_backend_alive; then
        log OK "Health OK — backend responsive"
        FAIL_COUNT=0
    else
        ((FAIL_COUNT++))
        log FAIL "Health check failed ($FAIL_COUNT/$MAX_RETRIES)"
        if (( FAIL_COUNT >= MAX_RETRIES )); then
            log WARN "Restart threshold reached — restarting backend..."
            kill_backend
            start_backend
            FAIL_COUNT=0
        fi
    fi

    # --- 📊 Live System Stats ---
    CPU=$(top -bn1 | grep "Cpu(s)" | awk '{print 100 - $8"%"}')
    MEM=$(free -h | awk '/Mem:/ {print $3 "/" $2}')
    UPTIME=$(uptime -p)
    log INFO "📊 CPU=$CPU | MEM=$MEM | UPTIME=$UPTIME"

    sleep $CHECK_INTERVAL
done

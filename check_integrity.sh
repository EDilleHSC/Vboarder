#!/bin/bash

# ============================
# VBoarder Integrity Check 🧠
# ============================

GREEN="\033[0;32m"
RED="\033[0;31m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

echo -e "\n🔍 ${YELLOW}VBoarder System Integrity Check${NC}\n"

ROOT_DIR=$(pwd)
AGENT_DIR="${ROOT_DIR}/agents"
REGISTRY_FILE="${ROOT_DIR}/agent_registry.json"
LOG_DIR="${ROOT_DIR}/logs"

PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

function check() {
  if eval "$1"; then
    echo -e "[${GREEN}✅${NC}] $2"
    ((PASS_COUNT++))
  else
    echo -e "[${RED}❌${NC}] $2"
    ((FAIL_COUNT++))
  fi
}

function check_warn() {
  if eval "$1"; then
    echo -e "[${GREEN}✅${NC}] $2"
    ((PASS_COUNT++))
  else
    echo -e "[${YELLOW}⚠️${NC}] $2"
    ((WARN_COUNT++))
  fi
}

# --- Check: Agent folders ---
echo -e "\n📁 ${BLUE}Checking agent folders...${NC}\n"
for agent in CEO CTO CFO COO CMO CLO COS SEC AIR; do
  AGENT_PATH="$AGENT_DIR/$agent"
  check "[ -d \"$AGENT_PATH\" ]" "$agent folder exists"

  if [ -d "$AGENT_PATH" ]; then
    # Check for key files
    check_warn "[ -f \"$AGENT_PATH/config.json\" ]" "$agent has config.json"
    check_warn "[ -f \"$AGENT_PATH/README.md\" ]" "$agent has README.md"

    # Check for prompts directory
    if [ -d "$AGENT_PATH/prompts" ]; then
      check_warn "[ -f \"$AGENT_PATH/prompts/system_detailed.txt\" ]" "$agent has system_detailed.txt"
    else
      check_warn "[ -f \"$AGENT_PATH/system_prompt.txt\" ]" "$agent has system_prompt.txt (legacy)"
    fi

    # Check for personas directory
    check_warn "[ -d \"$AGENT_PATH/personas\" ]" "$agent has personas directory"
  fi
done

# --- Check: Agent logic files ---
echo -e "\n🧠 ${BLUE}Checking agent logic files...${NC}\n"
for agent in CEO CTO CFO COO CMO CLO COS SEC AIR; do
  AGENT_LOGIC="$AGENT_DIR/$agent/agent_logic.py"
  check_warn "[ -f \"$AGENT_LOGIC\" ]" "$agent has agent_logic.py"
done

# --- Check: Ollama models vs registry ---
echo -e "\n🤖 ${BLUE}Checking Ollama models vs registry...${NC}\n"
if command -v ollama &> /dev/null; then
  if [ -f "$REGISTRY_FILE" ]; then
    MODELS=$(ollama list 2>/dev/null | awk '{print $1}')

    # Check if mistral (default model) is available
    check "echo \"$MODELS\" | grep -q \"mistral\"" "Ollama has 'mistral' model (default)"

    # Parse registry and check models
    if command -v jq &> /dev/null; then
      jq -r '.agents[]? // .[]? | select(.model) | "\(.role):\(.model)"' "$REGISTRY_FILE" 2>/dev/null | while IFS=: read -r agent model; do
        check_warn "echo \"$MODELS\" | grep -q \"${model%%:*}\"" "$agent uses model '$model'"
      done
    else
      echo -e "[${YELLOW}⚠️${NC}] jq not installed, skipping detailed model check"
      ((WARN_COUNT++))
    fi
  else
    echo -e "[${RED}❌${NC}] agent_registry.json not found"
    ((FAIL_COUNT++))
  fi
else
  echo -e "[${YELLOW}⚠️${NC}] Ollama not installed or not in PATH"
  ((WARN_COUNT++))
fi

# --- Check: Backend API health ---
echo -e "\n🌐 ${BLUE}Checking backend API...${NC}\n"
check "curl -s http://127.0.0.1:3738/health 2>/dev/null | grep -q 'ok'" "Backend /health route responds"
check_warn "curl -s http://127.0.0.1:3738/agents 2>/dev/null | grep -q 'agents'" "Backend /agents route responds"

# --- Check: Frontend running on 3001 ---
echo -e "\n🌍 ${BLUE}Checking frontend...${NC}\n"
if command -v ss &> /dev/null; then
  check_warn "ss -tln 2>/dev/null | grep -q ':3001'" "Frontend server listening on 3001"
elif command -v netstat &> /dev/null; then
  check_warn "netstat -tln 2>/dev/null | grep -q ':3001'" "Frontend server listening on 3001"
else
  echo -e "[${YELLOW}⚠️${NC}] Cannot check frontend port (ss/netstat not available)"
  ((WARN_COUNT++))
fi

# --- Check: Python environment ---
echo -e "\n🐍 ${BLUE}Checking Python environment...${NC}\n"
check "[ -f \"requirements.txt\" ]" "requirements.txt exists"
check_warn "[ -d \".venv\" ] || [ -d \".venv-wsl\" ]" "Virtual environment directory exists"

if [ -f "requirements.txt" ]; then
  REQ_COUNT=$(wc -l < requirements.txt)
  echo -e "    ${BLUE}ℹ️${NC}  Found $REQ_COUNT packages in requirements.txt"
fi

# --- Check: Core API files ---
echo -e "\n📦 ${BLUE}Checking core API files...${NC}\n"
check "[ -f \"api/main.py\" ]" "api/main.py exists"
check "[ -f \"api/simple_connector.py\" ]" "api/simple_connector.py exists"
check "[ -f \"api/shared_memory.py\" ]" "api/shared_memory.py exists"
check_warn "[ -f \"server.py\" ]" "server.py exists"

# --- Check: Log files ---
echo -e "\n📄 ${BLUE}Checking logs...${NC}\n"
check_warn "[ -d \"$LOG_DIR\" ]" "logs directory exists"

if [ -d "$LOG_DIR" ]; then
  check_warn "[ -f \"$LOG_DIR/backend.log\" ]" "backend.log exists"
  check_warn "[ -f \"$LOG_DIR/frontend.log\" ]" "frontend.log exists"

  # Show recent log sizes
  if [ -f "$LOG_DIR/backend.log" ]; then
    SIZE=$(du -h "$LOG_DIR/backend.log" | cut -f1)
    echo -e "    ${BLUE}ℹ️${NC}  backend.log size: $SIZE"
  fi
fi

# --- Check: Git status ---
echo -e "\n🧾 ${BLUE}Checking Git repository...${NC}\n"
check "[ -d \".git\" ]" "Git repository initialized"

if [ -d ".git" ]; then
  check_warn "git tag | grep -q 'v0.9.0-beta.1'" "v0.9.0-beta.1 tag exists"

  # Check for uncommitted changes
  if git diff --quiet && git diff --cached --quiet; then
    echo -e "[${GREEN}✅${NC}] No uncommitted changes"
    ((PASS_COUNT++))
  else
    echo -e "[${YELLOW}⚠️${NC}] Uncommitted changes detected"
    ((WARN_COUNT++))
  fi
fi

# --- Check: Startup scripts ---
echo -e "\n🚀 ${BLUE}Checking startup scripts...${NC}\n"
check "[ -f \"start_vboarder.sh\" ]" "start_vboarder.sh exists"
check "[ -f \"stop_vboarder.sh\" ]" "stop_vboarder.sh exists"
check_warn "[ -f \"start_vboarder.ps1\" ]" "start_vboarder.ps1 exists"
check_warn "[ -f \"stop_vboarder.ps1\" ]" "stop_vboarder.ps1 exists"

# --- Check: Documentation ---
echo -e "\n📚 ${BLUE}Checking documentation...${NC}\n"
check "[ -f \"README.md\" ]" "README.md exists"
check_warn "[ -f \"STARTUP_GUIDE.md\" ]" "STARTUP_GUIDE.md exists"
check_warn "[ -f \".github/copilot-instructions.md\" ]" ".github/copilot-instructions.md exists"

# --- Final Summary ---
echo -e "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "🎯 ${YELLOW}Check complete.${NC}"
echo -e "   ${GREEN}✅ Passed: ${PASS_COUNT}${NC}"
if [ "$WARN_COUNT" -gt 0 ]; then
  echo -e "   ${YELLOW}⚠️  Warnings: ${WARN_COUNT}${NC}"
fi
if [ "$FAIL_COUNT" -gt 0 ]; then
  echo -e "   ${RED}❌ Failed: ${FAIL_COUNT}${NC}"
fi
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"

if [ "$FAIL_COUNT" -eq 0 ]; then
  if [ "$WARN_COUNT" -eq 0 ]; then
    echo -e "${GREEN}✅ All systems go!${NC} VBoarder is ready.\n"
    exit 0
  else
    echo -e "${YELLOW}⚠️  Some warnings detected.${NC} Review above and address if needed.\n"
    exit 0
  fi
else
  echo -e "${RED}❌ Critical issues detected.${NC} Review above and resolve.\n"
  exit 1
fi

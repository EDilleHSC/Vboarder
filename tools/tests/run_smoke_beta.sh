#!/usr/bin/env bash
# VBoarder Beta Smoke Test
# Validates all critical systems for beta release

set -uo pipefail

echo "═══════════════════════════════════════════════════════════════"
echo "  VBoarder v0.9.0-beta.1 - Smoke Test Suite"
echo "═══════════════════════════════════════════════════════════════"
echo ""

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
cd "$ROOT"

BASE_URL="http://127.0.0.1:3738"
FRONTEND_URL="http://localhost:3000"
DASHBOARD_URL="http://127.0.0.1:4545"

PASSED=0
FAILED=0
WARNINGS=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass() {
    echo -e "  ${GREEN}✅ $1${NC}"
    ((PASSED++))
}

fail() {
    echo -e "  ${RED}❌ $1${NC}"
    ((FAILED++))
}

warn() {
    echo -e "  ${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"

    echo ""
    echo "🧪 Testing: $test_name"

    if eval "$test_command" > /dev/null 2>&1; then
        pass "$test_name"
        return 0
    else
        fail "$test_name"
        return 1
    fi
}

echo "📋 Pre-flight Checks"
echo ""

# 1. Check if backend is running
echo "🔍 [1/15] Backend Health Check..."
RESPONSE=$(curl -s -f "$BASE_URL/health" 2>/dev/null || echo "failed")
if echo "$RESPONSE" | grep -q "ok"; then
    pass "Backend is online (port 3738)"
else
    fail "Backend not responding - start with: uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload"
    echo ""
    echo "Cannot proceed without backend. Exiting."
    exit 1
fi

# 2. Check agents endpoint
echo "🔍 [2/15] Agents List Endpoint..."
RESPONSE=$(curl -s -f "$BASE_URL/agents" 2>/dev/null || echo "failed")
if echo "$RESPONSE" | grep -q "CEO"; then
    AGENT_COUNT=$(echo "$RESPONSE" | jq '. | length' 2>/dev/null || echo "0")
    if [ "$AGENT_COUNT" = "9" ]; then
        pass "Agents endpoint returns 9 agents"
    else
        warn "Agents endpoint returned $AGENT_COUNT agents (expected 9)"
    fi
else
    fail "Agents endpoint not responding correctly"
fi

# 3. Test each agent (9 total)
echo ""
echo "🤖 Agent Communication Tests (9 agents)"
echo ""

AGENTS=("CEO" "CTO" "CFO" "COO" "CMO" "CLO" "COS" "SEC" "AIR")
SESSION_ID="smoke-test-$(date +%s)"

for AGENT in "${AGENTS[@]}"; do
    echo "🔍 [$((${#AGENTS[@]} - $(echo "${AGENTS[@]}" | tr ' ' '\n' | grep -n "^$AGENT$" | cut -d: -f1) + 3))/15] Testing $AGENT..."

    RESPONSE=$(curl -s -X POST "$BASE_URL/chat/$AGENT" \
        -H 'Content-Type: application/json' \
        -d "{\"message\":\"Health check\",\"session_id\":\"$SESSION_ID\"}" \
        2>/dev/null || echo "failed")

    if echo "$RESPONSE" | jq -e '.response' > /dev/null 2>&1; then
        RESPONSE_TIME=$(echo "$RESPONSE" | jq -r '.response_time_ms' 2>/dev/null || echo "N/A")
        pass "$AGENT responded (${RESPONSE_TIME}ms)"
    else
        fail "$AGENT did not respond correctly"
    fi
done

# 4. Registry validation
echo ""
echo "🔍 [12/15] Agent Registry Validation..."
if [ -f "agent_registry.json" ]; then
    if jq empty agent_registry.json 2>/dev/null; then
        REGISTRY_COUNT=$(jq '. | length' agent_registry.json)
        if [ "$REGISTRY_COUNT" = "9" ]; then
            pass "Registry has 9 entries and valid JSON"
        else
            warn "Registry has $REGISTRY_COUNT entries (expected 9)"
        fi
    else
        fail "Registry JSON is invalid"
    fi
else
    fail "agent_registry.json not found"
fi

# 5. Virtual environment check
echo "🔍 [13/15] Virtual Environment..."
if [ -d ".venv-wsl" ]; then
    pass "Virtual environment exists (.venv-wsl)"
else
    warn "Virtual environment not found (.venv-wsl)"
fi

# 6. Frontend check (optional - might not be running)
echo "🔍 [14/15] Frontend (Optional)..."
FRONTEND_RESPONSE=$(curl -s -f "$FRONTEND_URL" 2>/dev/null || echo "not running")
if echo "$FRONTEND_RESPONSE" | grep -qi "vboarder\|html"; then
    pass "Frontend is online (port 3000)"
else
    warn "Frontend not running (optional) - start with: cd vboarder_frontend/nextjs_space && npm run dev"
fi

# 7. DevDash check (optional)
echo "🔍 [15/15] Dev Dashboard (Optional)..."
DASH_RESPONSE=$(curl -s -f "$DASHBOARD_URL" 2>/dev/null || echo "not running")
if echo "$DASH_RESPONSE" | grep -qi "vboarder\|dashboard\|html"; then
    pass "DevDash is online (port 4545)"
else
    warn "DevDash not running (optional) - start with: python3 tools/dev/devdash.py"
fi

# Summary
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Smoke Test Summary"
echo "═══════════════════════════════════════════════════════════════"
echo ""

TOTAL=$((PASSED + FAILED + WARNINGS))

echo "Results:"
echo -e "  ${GREEN}✅ Passed: $PASSED${NC}"
echo -e "  ${RED}❌ Failed: $FAILED${NC}"
echo -e "  ${YELLOW}⚠️  Warnings: $WARNINGS${NC}"
echo "  📊 Total: $TOTAL"
echo ""

# Determine exit status
if [ $FAILED -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo "🎉 All smoke tests passed! System is ready for beta testing."
        EXIT_CODE=0
    else
        echo "✅ Core tests passed, but $WARNINGS warning(s) detected."
        echo "   System is functional but review warnings above."
        EXIT_CODE=0
    fi
else
    echo "❌ $FAILED test(s) failed. System not ready for beta."
    echo "   Review errors above and fix issues."
    EXIT_CODE=1
fi

echo ""
echo "Next steps:"
if [ $EXIT_CODE -eq 0 ]; then
    echo "  1. Run full test suite: pytest -q"
    echo "  2. Run system validation: bash tools/ops/validate-all.sh"
    echo "  3. Begin beta testing: cat docs/BETA_TEST_PLAYBOOK.md"
else
    echo "  1. Fix failed tests above"
    echo "  2. Restart backend if needed"
    echo "  3. Re-run smoke test: bash tools/tests/run_smoke_beta.sh"
fi

echo ""
exit $EXIT_CODE

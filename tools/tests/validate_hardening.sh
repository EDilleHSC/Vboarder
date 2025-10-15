#!/usr/bin/env bash
# VBoarder Agent Repair v1.1 - Hardening Validation Script
# Validates all v1.1 hardening improvements

set -euo pipefail

echo "═══════════════════════════════════════════════════════════════"
echo "  VBoarder Agent Repair v1.1 - Hardening Validation"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Configuration
ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
REPAIR_SCRIPT="${ROOT_DIR}/tools/ops/repair-agents.sh"
API_MAIN="${ROOT_DIR}/api/main.py"
LOGS_DIR="${ROOT_DIR}/logs"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Helper functions
pass_test() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((PASSED++))
}

fail_test() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    ((FAILED++))
}

warn_test() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
    ((WARNINGS++))
}

echo "📂 Root Directory: $ROOT_DIR"
echo ""

# Test 1: Check repair script exists
echo "[1/10] Checking repair script exists..."
if [[ -f "$REPAIR_SCRIPT" ]]; then
    pass_test "repair-agents.sh found"
else
    fail_test "repair-agents.sh not found at $REPAIR_SCRIPT"
fi
echo ""

# Test 2: Check for case statement (garbage filtering)
echo "[2/10] Checking garbage directory whitelist..."
if grep -q 'case.*"\$role".*in' "$REPAIR_SCRIPT"; then
    if grep -q '__pycache__|default|venv|logs|tools|EXAMPLE|test_agent|agent_runtime|ops_agent' "$REPAIR_SCRIPT"; then
        pass_test "Case-based whitelist found (8+ directories)"
    else
        warn_test "Case statement found but incomplete whitelist"
    fi
else
    fail_test "Case-based whitelist not found (still using if/else?)"
fi
echo ""

# Test 3: Check for AUTO_RESTART feature
echo "[3/10] Checking AUTO_RESTART feature..."
if grep -q 'AUTO_RESTART' "$REPAIR_SCRIPT"; then
    if grep -q 'pkill -f "uvicorn api.main:app"' "$REPAIR_SCRIPT"; then
        pass_test "AUTO_RESTART feature implemented"
    else
        warn_test "AUTO_RESTART flag found but restart logic incomplete"
    fi
else
    fail_test "AUTO_RESTART feature not found"
fi
echo ""

# Test 4: Check api/main.py for file logging
echo "[4/10] Checking file logging in api/main.py..."
if [[ -f "$API_MAIN" ]]; then
    if grep -q 'FileHandler.*backend.log' "$API_MAIN"; then
        pass_test "File logging configured (logs/backend.log)"
    else
        fail_test "File logging not found in api/main.py"
    fi
else
    fail_test "api/main.py not found"
fi
echo ""

# Test 5: Check LOG_DIR creation
echo "[5/10] Checking LOG_DIR auto-creation..."
if grep -q 'LOG_DIR.*mkdir.*exist_ok' "$API_MAIN"; then
    pass_test "LOG_DIR auto-creation configured"
else
    warn_test "LOG_DIR auto-creation may not be configured"
fi
echo ""

# Test 6: Check for dual logging (console + file)
echo "[6/10] Checking dual logging handlers..."
if grep -q 'StreamHandler' "$API_MAIN" && grep -q 'FileHandler' "$API_MAIN"; then
    pass_test "Dual logging configured (console + file)"
else
    warn_test "May not have dual logging (console + file)"
fi
echo ""

# Test 7: Check documentation updates
echo "[7/10] Checking documentation updates..."
DOCS_UPDATED=0
[[ -f "${ROOT_DIR}/docs/AGENT_REPAIR_HARDENING.md" ]] && ((DOCS_UPDATED++))
[[ -f "${ROOT_DIR}/docs/AGENT_REPAIR_v1.0_vs_v1.1.md" ]] && ((DOCS_UPDATED++))
[[ -f "${ROOT_DIR}/AGENT_REPAIR_v1.1_SUMMARY.md" ]] && ((DOCS_UPDATED++))

if [[ $DOCS_UPDATED -eq 3 ]]; then
    pass_test "All hardening documentation present ($DOCS_UPDATED/3 files)"
elif [[ $DOCS_UPDATED -gt 0 ]]; then
    warn_test "Some hardening documentation present ($DOCS_UPDATED/3 files)"
else
    fail_test "Hardening documentation missing"
fi
echo ""

# Test 8: Check CTO_SHIFT_HANDOFF.md update
echo "[8/10] Checking CTO_SHIFT_HANDOFF.md update..."
if [[ -f "${ROOT_DIR}/CTO_SHIFT_HANDOFF.md" ]]; then
    if grep -q 'v1.1.*HARDENED' "${ROOT_DIR}/CTO_SHIFT_HANDOFF.md"; then
        pass_test "CTO_SHIFT_HANDOFF.md updated for v1.1"
    else
        warn_test "CTO_SHIFT_HANDOFF.md may not reference v1.1 hardening"
    fi
else
    warn_test "CTO_SHIFT_HANDOFF.md not found"
fi
echo ""

# Test 9: Test dry-run execution (functional test)
echo "[9/10] Testing dry-run execution..."
if DRY_RUN=true bash "$REPAIR_SCRIPT" > /dev/null 2>&1; then
    pass_test "Dry-run execution successful"
else
    fail_test "Dry-run execution failed (check script syntax)"
fi
echo ""

# Test 10: Check for skipped directories in dry-run output
echo "[10/10] Checking garbage directory filtering output..."
DRYRUN_OUTPUT=$(DRY_RUN=true bash "$REPAIR_SCRIPT" 2>&1 || true)
if echo "$DRYRUN_OUTPUT" | grep -q "Skipping garbage dir"; then
    SKIPPED_COUNT=$(echo "$DRYRUN_OUTPUT" | grep -c "Skipping garbage dir" || echo "0")
    pass_test "Garbage directory filtering active ($SKIPPED_COUNT dirs skipped)"
else
    warn_test "No garbage directories skipped (may be none present)"
fi
echo ""

# Summary
echo "═══════════════════════════════════════════════════════════════"
echo "  Validation Summary"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}✅ Passed:${NC}   $PASSED"
echo -e "${RED}❌ Failed:${NC}   $FAILED"
echo -e "${YELLOW}⚠️  Warnings:${NC} $WARNINGS"
echo ""

# Overall result
if [[ $FAILED -eq 0 ]]; then
    echo -e "${GREEN}🎉 All critical tests passed!${NC}"
    echo ""
    echo "✅ Agent Repair v1.1 hardening validated successfully"
    echo ""
    echo "Next steps:"
    echo "  1. Run smoke tests: bash tools/tests/run_smoke_beta.sh"
    echo "  2. Tag beta: git tag -a v0.9.0-beta.1 -m 'Hardened v1.1'"
    echo "  3. Begin testing: cat docs/BETA_TEST_PLAYBOOK.md"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Some tests failed!${NC}"
    echo ""
    echo "Please review the failed tests above and fix issues before proceeding."
    echo ""
    echo "Documentation:"
    echo "  • docs/AGENT_REPAIR_HARDENING.md"
    echo "  • docs/AGENT_REPAIR_v1.0_vs_v1.1.md"
    echo ""
    exit 1
fi

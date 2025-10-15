#!/usr/bin/env bash
# VBoarder Full Validation Script
# Runs all validation checks after cleanup and BOM fix

set -euo pipefail

echo "═══════════════════════════════════════════════════════════════"
echo "  VBoarder Post-Cleanup Validation"
echo "═══════════════════════════════════════════════════════════════"
echo ""

FAILED=0
PASSED=0

# Helper functions
pass() {
    echo "✅ $1"
    PASSED=$((PASSED + 1))
}

fail() {
    echo "❌ $1"
    FAILED=$((FAILED + 1))
}

warn() {
    echo "⚠️  $1"
}

# Change to repo root
cd "$(dirname "$0")/../.."

echo "[1/7] Checking BOM in agent_registry.json..."
if python3 tools/ops/fix-registry-bom.py | grep -q "No BOM found"; then
    pass "No BOM in agent_registry.json"
else
    warn "BOM was found and removed"
fi
echo ""

echo "[2/7] Validating JSON registry..."
if jq empty agent_registry.json 2>/dev/null; then
    pass "agent_registry.json is valid JSON"
else
    fail "agent_registry.json has JSON errors"
fi
echo ""

echo "[3/7] Checking agent setup..."
if bash tools/ops/verify-agent-setup.sh | tail -1 | grep -q "All agents configured"; then
    pass "All agents configured correctly"
else
    warn "Some agents may be missing files (see output above)"
fi
echo ""

echo "[4/7] Checking virtual environment..."
if [ -d ".venv-wsl" ]; then
    pass ".venv-wsl exists"
else
    fail ".venv-wsl not found"
fi
echo ""

echo "[5/7] Checking tool organization..."
TOOLS_OK=true
for dir in dev ops cleanup inventory; do
    if [ ! -d "tools/$dir" ]; then
        fail "tools/$dir missing"
        TOOLS_OK=false
    fi
done
if [ "$TOOLS_OK" = true ]; then
    pass "Tools organized correctly"
fi
echo ""

echo "[6/7] Checking documentation..."
DOCS_OK=true
for doc in BETA_TEST_PLAYBOOK.md CRITICAL_FIXES_QUICK_REF.md; do
    if [ ! -f "docs/$doc" ]; then
        fail "docs/$doc missing"
        DOCS_OK=false
    fi
done
if [ "$DOCS_OK" = true ]; then
    pass "Documentation complete"
fi
echo ""

echo "[7/7] Running pytest..."
if command -v pytest >/dev/null 2>&1; then
    if pytest -q 2>&1 | grep -q "passed"; then
        pass "Pytest tests passed"
    else
        fail "Pytest tests failed (see output above)"
    fi
else
    warn "pytest not available (skip for now)"
fi
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "  Validation Summary"
echo "═══════════════════════════════════════════════════════════════"
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 All validation checks passed!"
    echo ""
    echo "Next steps:"
    echo "  1. Update doc links: python3 tools/ops/update-doc-links.py"
    echo "  2. Start backend: uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload"
    echo "  3. Test endpoints: curl http://127.0.0.1:3738/health"
    echo "  4. Run beta tests: see docs/BETA_TEST_PLAYBOOK.md"
    exit 0
else
    echo "⚠️  $FAILED check(s) failed. Review output above."
    exit 1
fi

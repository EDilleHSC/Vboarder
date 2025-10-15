#!/usr/bin/env bash
# Complete Agent Repair Workflow
# Runs all repair steps in sequence

set -euo pipefail

echo "═══════════════════════════════════════════════════════════════"
echo "  VBoarder Complete Agent Repair"
echo "═══════════════════════════════════════════════════════════════"
echo ""

cd "$(dirname "$0")/../.."

echo "[Step 1/5] Rebuilding agent structures..."
python3 tools/ops/rebuild-agents.py
echo ""

echo "[Step 2/5] Rebuilding agent registry..."
python3 tools/ops/rebuild-registry.py
echo ""

echo "[Step 3/5] Removing BOM (if present)..."
python3 tools/ops/fix-registry-bom.py
echo ""

echo "[Step 4/5] Verifying agent setup..."
bash tools/ops/verify-agent-setup.sh
echo ""

echo "[Step 5/5] Validating JSON..."
if command -v jq >/dev/null 2>&1; then
    cat agent_registry.json | jq '.' > /dev/null && echo "✅ Registry JSON is valid"
else
    python3 -m json.tool agent_registry.json > /dev/null && echo "✅ Registry JSON is valid"
fi
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "  ✅ Agent repair complete!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "  1. Restart backend: pkill -f uvicorn && uvicorn api.main:app --reload"
echo "  2. Test endpoint: curl -X POST http://127.0.0.1:3738/chat/CTO -H 'Content-Type: application/json' -d '{\"message\":\"test\",\"session_id\":\"test\"}' | jq"
echo ""

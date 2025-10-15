#!/usr/bin/env bash
# Quick fix: Rebuild agent registry NOW
# Run this to restore the empty registry

set -euo pipefail

cd "$(dirname "$0")/../.."

echo "🔧 Rebuilding agent registry..."
python3 tools/ops/rebuild-registry.py

echo ""
echo "✅ Registry restored!"
echo ""
echo "Verify with:"
echo "  cat agent_registry.json | jq"
echo ""
echo "Then restart backend:"
echo "  uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload"

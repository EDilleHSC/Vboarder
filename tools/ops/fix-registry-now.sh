#!/usr/bin/env bash
# One-line registry fix - just copy and paste this command:
# python3 tools/ops/rebuild-registry.py

echo "Running registry rebuild..."
python3 tools/ops/rebuild-registry.py
echo ""
echo "Verifying..."
echo "Registry has $(cat agent_registry.json | jq '. | length') agents"
echo ""
echo "Agent roles:"
cat agent_registry.json | jq -r '.[].role'

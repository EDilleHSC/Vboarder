#!/usr/bin/env bash
# Test all 9 agent chat endpoints

# Don't use set -e to prevent early exit on jq errors
set -uo pipefail

echo "═══════════════════════════════════════════════════════════════"
echo "  VBoarder - Test All Agent Endpoints"
echo "═══════════════════════════════════════════════════════════════"
echo ""

AGENTS=("CEO" "CTO" "CFO" "COO" "CMO" "CLO" "COS" "SEC" "AIR")
BASE_URL="http://127.0.0.1:3738"
SESSION_ID="test-$(date +%s)"

echo "📍 Testing ${#AGENTS[@]} agents..."
echo "🔗 Base URL: $BASE_URL"
echo "📝 Session ID: $SESSION_ID"
echo ""

PASSED=0
FAILED=0

for AGENT in "${AGENTS[@]}"; do
    echo "Testing $AGENT..."

    RESPONSE=$(curl -s -X POST "$BASE_URL/chat/$AGENT" \
        -H 'Content-Type: application/json' \
        -d "{\"message\":\"What is your role?\",\"session_id\":\"$SESSION_ID\"}")

    # Check if response contains expected fields
    if echo "$RESPONSE" | jq -e '.response' > /dev/null 2>&1; then
        ROLE=$(echo "$RESPONSE" | jq -r '.agent // "unknown"' 2>/dev/null || echo "unknown")
        RESPONSE_TEXT=$(echo "$RESPONSE" | jq -r '.response' 2>/dev/null | head -c 80 || echo "")
        RESPONSE_TIME=$(echo "$RESPONSE" | jq -r '.response_time_ms // "N/A"' 2>/dev/null || echo "N/A")

        echo "  ✅ $AGENT responded (${RESPONSE_TIME}ms)"
        echo "     \"$RESPONSE_TEXT...\""
        ((PASSED++))
    else
        echo "  ❌ $AGENT failed"
        echo "     Response: $RESPONSE"
        ((FAILED++))
    fi
    echo ""
done

echo "═══════════════════════════════════════════════════════════════"
echo "  Test Summary"
echo "═══════════════════════════════════════════════════════════════"
echo "✅ Passed: $PASSED / ${#AGENTS[@]}"
echo "❌ Failed: $FAILED / ${#AGENTS[@]}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "🎉 All agents working correctly!"
    exit 0
else
    echo "⚠️  Some agents failed - check errors above"
    exit 1
fi

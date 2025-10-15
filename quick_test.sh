#!/bin/bash
# Quick reasoning test script with LFM2e routing detection
# Usage: ./quick_test.sh [optional custom task] [optional agent]

TASK=${1:-"Analyze our strategic options for Q4 growth"}
AGENT=${2:-"CEO"}

echo "🧪 Quick Reasoning Test (Enhanced with LFM2e)"
echo "=============================================="
echo "Task: $TASK"
echo "Agent: $AGENT"

# Test routing first
echo ""
echo "🧬 Testing Model Routing..."
python3 -c "
import sys
sys.path.append('.')
from router import route_task
result = route_task('$TASK', '$AGENT')
print(f'  → Slot: {result[\"slot\"]} ({result[\"model\"]})')
print(f'  → Uses LFM2e: {\"🧬 Yes\" if result[\"uses_lfm2e\"] else \"❌ No\"}')
print(f'  → Complexity: {result[\"complexity\"]}')
"

echo ""
echo "🚀 Testing Reasoning Endpoint..."

# Test the reasoning endpoint
RESPONSE=$(curl -s -X POST "http://127.0.0.1:3738/ask?reasoning=loop" \
  -H "Content-Type: application/json" \
  -d "{\"task\":\"$TASK\",\"agent_role\":\"$AGENT\"}")

if [ $? -eq 0 ]; then
    echo "✅ Request sent successfully"

    # Parse response
    STATUS=$(echo "$RESPONSE" | jq -r '.status' 2>/dev/null)
    RESULT=$(echo "$RESPONSE" | jq -r '.result' 2>/dev/null)
    ITERATIONS=$(echo "$RESPONSE" | jq -r '.iterations' 2>/dev/null)
    CONFIDENCE=$(echo "$RESPONSE" | jq -r '.confidence' 2>/dev/null)

    if [ "$STATUS" = "success" ]; then
        echo "✅ Status: $STATUS"
        echo "🔄 Iterations: $ITERATIONS"
        echo "📈 Confidence: $CONFIDENCE"
        echo ""
        echo "📝 Response:"
        echo "$RESULT" | head -3
        echo ""
        echo "🎉 Reasoning kernel is working perfectly!"
    else
        echo "❌ Test failed"
        echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"
    fi
else
    echo "❌ Connection failed - is the backend running?"
fi

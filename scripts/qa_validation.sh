#!/bin/bash
# VBoarder Beta Release - QA Validation Script
# Tests all critical endpoints and functionality

set -e  # Exit on error

echo "=== VBoarder v0.9.0-beta.1 QA Validation ==="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

API_BASE="http://127.0.0.1:3738"
PASSED=0
FAILED=0

# Function to test endpoint
test_endpoint() {
    local name="$1"
    local url="$2"
    local method="${3:-GET}"
    local data="$4"

    echo -n "Testing $name... "

    if [ "$method" = "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$url" \
            -H "Content-Type: application/json" \
            -d "$data" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" "$url" 2>&1)
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" = "200" ] || [ "$http_code" = "201" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $http_code)"
        ((PASSED++))
        if [ ! -z "$body" ] && [ ${#body} -lt 200 ]; then
            echo "  Response: $body" | head -c 150
            echo ""
        fi
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $http_code)"
        ((FAILED++))
        echo "  Error: $body" | head -c 200
        echo ""
    fi
}

# Check if backend is running
echo -e "${CYAN}[1/5] Checking if backend is running...${NC}"
if curl -s "$API_BASE/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend is running${NC}"
else
    echo -e "${RED}✗ Backend is not running!${NC}"
    echo "  Start it with: uvicorn api.main:app --host 127.0.0.1 --port 3738"
    exit 1
fi
echo ""

# Test core endpoints
echo -e "${CYAN}[2/5] Testing core endpoints...${NC}"
test_endpoint "Health Check" "$API_BASE/health"
test_endpoint "Readiness Check" "$API_BASE/ready"
test_endpoint "Agent List" "$API_BASE/agents"
echo ""

# Test chat endpoints
echo -e "${CYAN}[3/5] Testing chat functionality...${NC}"
test_endpoint "CEO Chat" "$API_BASE/chat/CEO" "POST" \
    '{"message":"Quick health check","session_id":"qa-test","concise":true}'
test_endpoint "CTO Chat" "$API_BASE/chat/CTO" "POST" \
    '{"message":"Tech stack recommendation","session_id":"qa-test","concise":true}'
echo ""

# Test memory endpoints
echo -e "${CYAN}[4/5] Testing memory system...${NC}"
test_endpoint "Memory Update" "$API_BASE/api/memory" "POST" \
    '{"agent":"CEO","section":"facts","entry":"QA test passed"}'
test_endpoint "Memory Retrieval" "$API_BASE/api/memory?agent=CEO"
echo ""

# Run pytest
echo -e "${CYAN}[5/5] Running automated test suite...${NC}"
if pytest -q 2>&1 | tee /tmp/pytest_output.txt; then
    test_count=$(grep -E "passed|failed" /tmp/pytest_output.txt | head -1)
    echo -e "${GREEN}✓ Test suite passed${NC} ($test_count)"
    ((PASSED++))
else
    echo -e "${RED}✗ Test suite failed${NC}"
    ((FAILED++))
    cat /tmp/pytest_output.txt | tail -20
fi
echo ""

# Summary
echo "=== QA Validation Summary ==="
echo ""
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All checks passed! Ready for release.${NC}"
    exit 0
else
    echo -e "${RED}❌ Some checks failed. Please fix before releasing.${NC}"
    exit 1
fi

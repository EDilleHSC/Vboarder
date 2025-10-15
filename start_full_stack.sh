#!/bin/bash
# VBoarder V2 Full Stack Startup Script
# Run this in WSL to start both backend and frontend

set -e  # Exit on error

echo "=============================================="
echo "🚀 VBoarder V2 Full Stack Startup"
echo "=============================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="/mnt/d/ai/projects/vboarder"
FRONTEND_DIR="$PROJECT_ROOT/vboarder_frontend/nextjs_space"
BACKEND_DIR="$PROJECT_ROOT"

# ==============================================
# Step 1: Check Prerequisites
# ==============================================
echo "📋 Step 1: Checking Prerequisites..."
echo ""

# Check Python
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python $(python --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Node.js $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} npm $(npm --version)"

echo ""

# ==============================================
# Step 2: Check Virtual Environment
# ==============================================
echo "📋 Step 2: Checking Python Virtual Environment..."
echo ""

cd "$BACKEND_DIR"

if [ ! -d ".venv-wsl" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found, creating...${NC}"
    python -m venv .venv-wsl
    echo -e "${GREEN}✓${NC} Created .venv-wsl"
fi

# Activate venv
source .venv-wsl/bin/activate
echo -e "${GREEN}✓${NC} Activated virtual environment"

# Check/install requirements
echo ""
echo "📦 Installing/Updating Python dependencies..."
pip install -q -r requirements.txt
echo -e "${GREEN}✓${NC} Dependencies installed"

echo ""

# ==============================================
# Step 3: Verify Agent Structure
# ==============================================
echo "📋 Step 3: Verifying Agent Structure..."
echo ""

# Run agent import test
if python tests_flat/test_agent_imports.py > /tmp/agent_test.log 2>&1; then
    echo -e "${GREEN}✓${NC} All agents imported successfully"
else
    echo -e "${RED}❌ Agent import test failed${NC}"
    echo "See /tmp/agent_test.log for details"
    cat /tmp/agent_test.log
    exit 1
fi

echo ""

# ==============================================
# Step 4: Clear Frontend Cache
# ==============================================
echo "📋 Step 4: Clearing Frontend Cache..."
echo ""

cd "$FRONTEND_DIR"

if [ -d ".next" ]; then
    rm -rf .next
    echo -e "${GREEN}✓${NC} Cleared .next cache"
else
    echo -e "${YELLOW}⚠️${NC}  No .next cache found"
fi

# Check node_modules
if [ ! -d "node_modules" ]; then
    echo ""
    echo "📦 Installing npm dependencies (this may take a while)..."
    npm install
    echo -e "${GREEN}✓${NC} npm dependencies installed"
fi

echo ""

# ==============================================
# Step 5: Build Frontend
# ==============================================
echo "📋 Step 5: Building Frontend..."
echo ""

if npm run build > /tmp/frontend_build.log 2>&1; then
    echo -e "${GREEN}✓${NC} Frontend built successfully"
else
    echo -e "${RED}❌ Frontend build failed${NC}"
    echo "See /tmp/frontend_build.log for details"
    tail -n 20 /tmp/frontend_build.log
    exit 1
fi

echo ""

# ==============================================
# Step 6: Start Backend
# ==============================================
echo "📋 Step 6: Starting Backend Server..."
echo ""

cd "$BACKEND_DIR"
source .venv-wsl/bin/activate

echo "Starting backend on http://127.0.0.1:3738..."
echo -e "${YELLOW}Press Ctrl+C to stop servers${NC}"
echo ""

# Start backend in background
uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to initialize..."
sleep 3

# Check if backend is running
if ps -p $BACKEND_PID > /dev/null; then
    echo -e "${GREEN}✓${NC} Backend started (PID: $BACKEND_PID)"

    # Test health endpoint
    if curl -s http://127.0.0.1:3738/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Backend health check passed"
    else
        echo -e "${YELLOW}⚠️${NC}  Backend health check failed (may still be starting)"
    fi
else
    echo -e "${RED}❌ Backend failed to start${NC}"
    echo "Check /tmp/backend.log for details"
    cat /tmp/backend.log
    exit 1
fi

echo ""

# ==============================================
# Step 7: Start Frontend
# ==============================================
echo "📋 Step 7: Starting Frontend Dev Server..."
echo ""

cd "$FRONTEND_DIR"

echo "Starting frontend on http://localhost:3000..."
echo ""

# Start frontend in background
npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
echo "Waiting for frontend to initialize..."
sleep 5

if ps -p $FRONTEND_PID > /dev/null; then
    echo -e "${GREEN}✓${NC} Frontend started (PID: $FRONTEND_PID)"
else
    echo -e "${RED}❌ Frontend failed to start${NC}"
    echo "Check /tmp/frontend.log for details"
    cat /tmp/frontend.log
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "=============================================="
echo "✅ VBoarder V2 Full Stack Running!"
echo "=============================================="
echo ""
echo "📍 Access Points:"
echo "   Frontend:      http://localhost:3000/v2"
echo "   Backend API:   http://127.0.0.1:3738"
echo "   API Docs:      http://127.0.0.1:3738/docs"
echo ""
echo "📊 Process IDs:"
echo "   Backend:  $BACKEND_PID"
echo "   Frontend: $FRONTEND_PID"
echo ""
echo "📝 Logs:"
echo "   Backend:  /tmp/backend.log"
echo "   Frontend: /tmp/frontend.log"
echo ""
echo "🛑 To stop servers:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo -e "${YELLOW}Press Ctrl+C to view logs (servers will continue running)${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "✓ Servers stopped"
    exit 0
}

trap cleanup INT TERM

# Keep script running and show logs
echo "Tailing logs (Ctrl+C to exit):"
echo "================================"
tail -f /tmp/backend.log /tmp/frontend.log

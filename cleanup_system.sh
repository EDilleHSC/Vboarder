#!/bin/bash
# VBoarder System Cleanup Script
# Comprehensive diagnostic and repair system

# Initialize logging
CLEANUP_LOG="cleanup_$(date +%Y%m%d_%H%M%S).log"
PASSED_CHECKS=0
FAILED_CHECKS=0

log_info() {
    echo "[$(date +'%H:%M:%S')] INFO: $1" | tee -a "$CLEANUP_LOG"
}

log_error() {
    echo "[$(date +'%H:%M:%S')] ERROR: $1" | tee -a "$CLEANUP_LOG"
    ((FAILED_CHECKS++))
}

log_success() {
    echo "[$(date +'%H:%M:%S')] SUCCESS: $1" | tee -a "$CLEANUP_LOG"
    ((PASSED_CHECKS++))
}

echo "🧹 VBoarder System Cleanup & Diagnostics"
echo "========================================="
echo "Log file: $CLEANUP_LOG"
echo ""

# 1. Kill dangling processes
echo "💀 Killing dangling processes..."
log_info "Starting process cleanup"

# Kill old uvicorn/FastAPI processes
if pgrep -f "uvicorn.*api.main:app" > /dev/null; then
    log_info "Killing existing uvicorn processes"
    pkill -f "uvicorn.*api.main:app" 2>/dev/null || true
    sleep 2
    if pgrep -f "uvicorn.*api.main:app" > /dev/null; then
        log_error "Force killing stubborn uvicorn processes"
        pkill -9 -f "uvicorn.*api.main:app" 2>/dev/null || true
    fi
fi

# Free up port 3738
if lsof -i :3738 > /dev/null 2>&1; then
    log_info "Port 3738 occupied, freeing it"
    lsof -ti :3738 | xargs kill -9 2>/dev/null || true
    sleep 1
    if lsof -i :3738 > /dev/null 2>&1; then
        log_error "Port 3738 still occupied after cleanup"
    else
        log_success "Port 3738 freed"
    fi
else
    log_success "Port 3738 already free"
fi

# Kill any model daemon processes
for proc in "ollama" "llamacpp" "transformers"; do
    if pgrep -f "$proc" > /dev/null; then
        log_info "Killing $proc processes"
        pkill -f "$proc" 2>/dev/null || true
    fi
done

log_success "Process cleanup completed"

# 2. Reset virtual environment
echo ""
echo "🐍 Resetting virtual environment..."
log_info "Starting virtual environment reset"

if [ -d ".venv-wsl" ]; then
    log_info "Existing .venv-wsl found, validating"

    # Test if venv is functional
    if source .venv-wsl/bin/activate 2>/dev/null && python3 -c "import sys; print(sys.prefix)" | grep -q venv-wsl; then
        log_success "Virtual environment is functional"
    else
        log_error "Virtual environment corrupted, recreating"
        rm -rf .venv-wsl
        python3 -m venv .venv-wsl
        if [ $? -eq 0 ]; then
            log_success "Virtual environment recreated"
        else
            log_error "Failed to create virtual environment"
        fi
    fi
else
    log_info "Creating new virtual environment"
    python3 -m venv .venv-wsl
    if [ $? -eq 0 ]; then
        log_success "Virtual environment created"
    else
        log_error "Failed to create virtual environment"
    fi
fi

# Activate and install dependencies
if source .venv-wsl/bin/activate 2>/dev/null; then
    log_success "Virtual environment activated"

    log_info "Installing/updating dependencies"
    pip install --upgrade pip > /dev/null 2>&1

    # Install from multiple requirements files if they exist
    for req_file in "requirements.txt" "api/requirements.txt" "agents/requirements.txt"; do
        if [ -f "$req_file" ]; then
            log_info "Installing from $req_file"
            pip install -r "$req_file" > /dev/null 2>&1
            if [ $? -eq 0 ]; then
                log_success "Dependencies from $req_file installed"
            else
                log_error "Failed to install dependencies from $req_file"
            fi
        fi
    done
else
    log_error "Failed to activate virtual environment"
fi

# 3. Clear caches and temp files
echo ""
echo "🗂️ Clearing caches and temporary files..."
log_info "Starting cache cleanup"

# Remove Python cache files
find . -name "*.pyc" -delete 2>/dev/null
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
log_success "Python cache files cleared"

# Remove large log files
find . -name "*.log" -size +10M -delete 2>/dev/null
log_success "Large log files cleared"

# Clear model download caches
for cache_dir in ".cache" "~/.cache/huggingface" "~/.ollama" ".tmp"; do
    if [ -d "$cache_dir" ]; then
        log_info "Clearing $cache_dir"
        rm -rf "$cache_dir"/{tmp,temp,download}* 2>/dev/null || true
    fi
done

# Clear temporary conversation files
if [ -d "api/conversations" ]; then
    find api/conversations -name "*.tmp" -delete 2>/dev/null || true
    log_success "Temporary conversation files cleared"
fi

log_success "Cache cleanup completed"

# 4. Check and fix permissions
echo ""
echo "🔐 Fixing file permissions..."
log_info "Starting permission fixes"

chmod +x quick_test.sh 2>/dev/null && log_success "quick_test.sh permissions fixed" || log_error "Failed to fix quick_test.sh permissions"
chmod +x vboarder_status.sh 2>/dev/null && log_success "vboarder_status.sh permissions fixed" || log_error "Failed to fix vboarder_status.sh permissions"
chmod +x tools/cleanup/*.sh 2>/dev/null && log_success "Cleanup script permissions fixed" || log_error "Failed to fix cleanup script permissions"
chmod +x tools/ops/*.sh 2>/dev/null && log_success "Ops script permissions fixed" || log_error "Failed to fix ops script permissions"

# 5. Validate file integrity
echo ""
echo "🔍 Validating file integrity..."
log_info "Starting file integrity check"

# Critical files that must exist
CRITICAL_FILES=(
    "router.py"
    "reasoning_kernel.py"
    "api/main.py"
    "api/simple_connector.py"
    "models/liquid_model.py"
    "list_agents.py"
    "eval_viewer.py"
    "agent_registry.json"
    "server.py"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        log_success "Critical file exists: $file"
    else
        log_error "Missing critical file: $file"
    fi
done

# Check for broken symlinks
if find . -type l -exec test ! -e {} \; -print 2>/dev/null | grep -q .; then
    log_error "Broken symlinks found"
    find . -type l -exec test ! -e {} \; -print 2>/dev/null | while read link; do
        log_error "Broken link: $link"
    done
else
    log_success "No broken symlinks found"
fi

# Validate agent structure
log_info "Validating agent structure"
for agent_dir in agents/*/; do
    if [ -d "$agent_dir" ]; then
        agent_name=$(basename "$agent_dir")
        if [ -f "$agent_dir/config.json" ]; then
            log_success "Agent $agent_name has config.json"
        else
            log_error "Agent $agent_name missing config.json"
        fi
    fi
done

# 6. Validate core components
echo ""
echo "🧪 Validating core components..."
log_info "Starting component validation"

# Activate venv for tests
source .venv-wsl/bin/activate 2>/dev/null || log_error "Cannot activate virtual environment"

# Test router
if python3 -c "from router import route_task; print(route_task('test', 'CEO'))" 2>/dev/null; then
    log_success "Router functional"
else
    log_error "Router has issues"
fi

# Test reasoning kernel
if python3 -c "from reasoning_kernel import ReasoningKernel; rk = ReasoningKernel(); print('OK')" 2>/dev/null; then
    log_success "Reasoning kernel functional"
else
    log_error "Reasoning kernel has issues"
fi

# Test agent discovery
if python3 list_agents.py 2>/dev/null | grep -q "Enabled agents"; then
    log_success "Agent discovery functional"
else
    log_error "Agent discovery has issues"
fi

# Test model framework
if python3 -c "from models.liquid_model import LFMModel; print('OK')" 2>/dev/null; then
    log_success "Model framework functional"
else
    log_error "Model framework has issues"
fi

# Test memory system
if python3 -c "from api.shared_memory import SharedMemory; sm = SharedMemory(); print('OK')" 2>/dev/null; then
    log_success "Memory system functional"
else
    log_error "Memory system has issues"
fi

# 7. Rebuild any generated code
echo ""
echo "🔨 Rebuilding generated code..."
log_info "Starting code generation rebuild"

# Regenerate agent registry if needed
if [ -f "tools/ops/fix-registry-now.sh" ]; then
    log_info "Regenerating agent registry"
    bash tools/ops/fix-registry-now.sh > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        log_success "Agent registry regenerated"
    else
        log_error "Failed to regenerate agent registry"
    fi
fi

# Update any cached embeddings
if [ -f "api/memory_manager.py" ]; then
    log_info "Clearing embedding cache"
    python3 -c "
import sys
sys.path.append('api')
try:
    from memory_manager import clear_embedding_cache
    clear_embedding_cache()
    print('Cache cleared')
except:
    pass
" 2>/dev/null && log_success "Embedding cache cleared" || log_error "Failed to clear embedding cache"
fi

# 8. Run basic smoke tests
echo ""
echo "🧪 Running smoke tests..."
log_info "Starting smoke tests"

# Test 1: VBoarder status
if [ -f "vboarder_status.sh" ]; then
    log_info "Running vboarder_status.sh"
    if bash vboarder_status.sh > /dev/null 2>&1; then
        log_success "VBoarder status check passed"
    else
        log_error "VBoarder status check failed"
    fi
else
    log_error "vboarder_status.sh not found"
fi

# Test 2: Quick test
if [ -f "quick_test.sh" ]; then
    log_info "Running quick_test.sh"
    if timeout 30 bash quick_test.sh > /dev/null 2>&1; then
        log_success "Quick test passed"
    else
        log_error "Quick test failed or timed out"
    fi
else
    log_error "quick_test.sh not found"
fi

# Test 3: Start backend for API test
log_info "Starting backend for API test"
source .venv-wsl/bin/activate 2>/dev/null
uvicorn api.main:app --host 127.0.0.1 --port 3738 &
BACKEND_PID=$!
sleep 5

# Test 4: API health check
if curl -s -f "http://127.0.0.1:3738/health" > /dev/null 2>&1; then
    log_success "API health endpoint responding"

    # Test 5: Simple chat test
    if curl -s -X POST "http://127.0.0.1:3738/chat/CEO" \
        -H "Content-Type: application/json" \
        -d '{"message":"Hello, quick status check"}' > /dev/null 2>&1; then
        log_success "API chat endpoint responding"
    else
        log_error "API chat endpoint failed"
    fi
else
    log_error "API health endpoint not responding"
fi

# Clean up test backend
kill $BACKEND_PID 2>/dev/null || true
sleep 2

# 9. Generate final report
echo ""
echo "📊 Cleanup Report"
echo "=================="
log_info "Generating final report"

echo "� Cleanup Summary:" | tee -a "$CLEANUP_LOG"
echo "   � Log file: $CLEANUP_LOG" | tee -a "$CLEANUP_LOG"
echo "   ✅ Passed checks: $PASSED_CHECKS" | tee -a "$CLEANUP_LOG"
echo "   ❌ Failed checks: $FAILED_CHECKS" | tee -a "$CLEANUP_LOG"

if [ $FAILED_CHECKS -eq 0 ]; then
    echo "   🎯 Status: SYSTEM HEALTHY ✅" | tee -a "$CLEANUP_LOG"
    echo "" | tee -a "$CLEANUP_LOG"
    echo "🚀 All systems operational! VBoarder is ready for use." | tee -a "$CLEANUP_LOG"
    exit 0
else
    echo "   🎯 Status: ISSUES DETECTED ⚠️" | tee -a "$CLEANUP_LOG"
    echo "" | tee -a "$CLEANUP_LOG"
    echo "⚠️  $FAILED_CHECKS issues detected. Check $CLEANUP_LOG for details." | tee -a "$CLEANUP_LOG"
    echo "" | tee -a "$CLEANUP_LOG"
    echo "💡 Quick fixes:" | tee -a "$CLEANUP_LOG"
    echo "   • Start backend: uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload" | tee -a "$CLEANUP_LOG"
    echo "   • Check agents: python3 list_agents.py" | tee -a "$CLEANUP_LOG"
    echo "   • System status: ./vboarder_status.sh" | tee -a "$CLEANUP_LOG"
    echo "   • Review log: cat $CLEANUP_LOG" | tee -a "$CLEANUP_LOG"
    exit 1
fi

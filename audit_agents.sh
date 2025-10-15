#!/bin/bash
# VBoarder Agent Audit & Realignment Script
# Comprehensive validation of agent roles, definitions, and configurations

echo "🔍 VBOARDER AGENT AUDIT & REALIGNMENT"
echo "====================================="
echo ""

AGENTS_DIR="/mnt/d/ai/projects/vboarder/agents"
AUDIT_LOG="agent_audit_$(date +%Y%m%d_%H%M%S).log"

log_info() {
    echo "[$(date +'%H:%M:%S')] INFO: $1" | tee -a "$AUDIT_LOG"
}

log_error() {
    echo "[$(date +'%H:%M:%S')] ERROR: $1" | tee -a "$AUDIT_LOG"
}

log_success() {
    echo "[$(date +'%H:%M:%S')] SUCCESS: $1" | tee -a "$AUDIT_LOG"
}

echo "📋 PHASE 1: Agent Structure Audit"
echo "=================================="

# Get list of actual agent directories (should be 3-letter uppercase codes)
AGENTS=($(find "$AGENTS_DIR" -maxdepth 1 -type d -name "[A-Z][A-Z][A-Z]" | sort | xargs -n1 basename))

log_info "Found ${#AGENTS[@]} agent directories: ${AGENTS[*]}"

for agent in "${AGENTS[@]}"; do
    agent_path="$AGENTS_DIR/$agent"
    echo ""
    echo "🤖 Auditing Agent: $agent"
    echo "========================"

    # Check required files
    required_files=("config.json" "persona.json" "agent.json")
    missing_files=()

    for file in "${required_files[@]}"; do
        if [ -f "$agent_path/$file" ]; then
            log_success "$agent: $file exists"
        else
            log_error "$agent: Missing $file"
            missing_files+=("$file")
        fi
    done

    # Analyze configuration conflicts
    if [ -f "$agent_path/config.json" ] && [ -f "$agent_path/persona.json" ]; then
        config_model=$(jq -r '.model // "not-set"' "$agent_path/config.json" 2>/dev/null)
        persona_model=$(jq -r '.model // "not-set"' "$agent_path/persona.json" 2>/dev/null)

        echo "   📊 Configuration Analysis:"
        echo "      Config model: $config_model"
        echo "      Persona model: $persona_model"

        if [ "$config_model" != "$persona_model" ] && [ "$config_model" != "not-set" ] && [ "$persona_model" != "not-set" ]; then
            log_error "$agent: Model mismatch - config: $config_model, persona: $persona_model"
        else
            log_success "$agent: Model configuration consistent"
        fi
    fi

    # Check persona content quality
    if [ -f "$agent_path/persona.json" ]; then
        persona_role=$(jq -r '.role // "not-set"' "$agent_path/persona.json" 2>/dev/null)
        persona_title=$(jq -r '.title // "not-set"' "$agent_path/persona.json" 2>/dev/null)

        echo "   🎭 Persona Analysis:"
        echo "      Role: $persona_role"
        echo "      Title: $persona_title"

        if [ "$persona_role" = "$agent" ]; then
            log_success "$agent: Role matches directory name"
        else
            log_error "$agent: Role mismatch - expected: $agent, got: $persona_role"
        fi
    fi

    # Check slot assignment and model routing
    echo "   🎯 Slot & Model Routing:"

    # Determine expected slot based on agent role
    case "$agent" in
        "CEO"|"CTO")
            expected_slot="slot:b"
            expected_model="lfm2e:latest"
            ;;
        "CFO"|"COO"|"CLO"|"CMO"|"COS")
            expected_slot="slot:a"
            expected_model="mistral:latest"
            ;;
        "SEC"|"AIR")
            expected_slot="slot:a"
            expected_model="mistral:latest"
            ;;
        *)
            expected_slot="slot:a"
            expected_model="mistral:latest"
            ;;
    esac

    echo "      Expected slot: $expected_slot"
    echo "      Expected model: $expected_model"

    # Check if slot configuration exists in agent.json
    if [ -f "$agent_path/agent.json" ]; then
        agent_slot=$(jq -r '.slot // "not-set"' "$agent_path/agent.json" 2>/dev/null)
        echo "      Current slot: $agent_slot"

        if [ "$agent_slot" = "$expected_slot" ]; then
            log_success "$agent: Slot assignment correct"
        else
            log_error "$agent: Slot assignment incorrect - expected: $expected_slot, got: $agent_slot"
        fi
    else
        log_error "$agent: agent.json missing - cannot verify slot assignment"
    fi
done

echo ""
echo "📊 PHASE 2: Model Configuration Audit"
echo "====================================="

# Check router.py for slot configuration
if [ -f "/mnt/d/ai/projects/vboarder/router.py" ]; then
    log_info "Checking router.py for slot configuration"

    if grep -q "slot:b" "/mnt/d/ai/projects/vboarder/router.py"; then
        log_success "Router contains slot:b configuration"
    else
        log_error "Router missing slot:b configuration"
    fi

    if grep -q "lfm2e" "/mnt/d/ai/projects/vboarder/router.py"; then
        log_success "Router contains LFM2e model configuration"
    else
        log_error "Router missing LFM2e model configuration"
    fi
else
    log_error "router.py not found"
fi

echo ""
echo "🧠 PHASE 3: Memory System Audit"
echo "==============================="

# Check shared memory system
if [ -f "/mnt/d/ai/projects/vboarder/api/shared_memory.py" ]; then
    log_success "Shared memory system exists"

    # Test memory directories
    memory_dir="$HOME/.vboarder/memory"
    if [ -d "$memory_dir" ]; then
        log_success "Memory directory exists: $memory_dir"

        # Count memory files
        memory_files=$(find "$memory_dir" -name "*.json" 2>/dev/null | wc -l)
        log_info "Found $memory_files memory files"
    else
        log_error "Memory directory missing: $memory_dir"
    fi
else
    log_error "Shared memory system missing"
fi

echo ""
echo "📋 PHASE 4: Generate Realignment Plan"
echo "====================================="

echo "🔧 REALIGNMENT ACTIONS NEEDED:" | tee -a "$AUDIT_LOG"

# Generate specific fix actions
fixes_needed=0

for agent in "${AGENTS[@]}"; do
    agent_path="$AGENTS_DIR/$agent"

    # Check for missing files
    for file in "config.json" "persona.json" "agent.json"; do
        if [ ! -f "$agent_path/$file" ]; then
            echo "   ❌ Create missing $file for $agent" | tee -a "$AUDIT_LOG"
            ((fixes_needed++))
        fi
    done

    # Check for model mismatches
    if [ -f "$agent_path/config.json" ] && [ -f "$agent_path/persona.json" ]; then
        config_model=$(jq -r '.model // "not-set"' "$agent_path/config.json" 2>/dev/null)
        persona_model=$(jq -r '.model // "not-set"' "$agent_path/persona.json" 2>/dev/null)

        if [ "$config_model" != "$persona_model" ] && [ "$config_model" != "not-set" ] && [ "$persona_model" != "not-set" ]; then
            echo "   ❌ Fix model mismatch for $agent" | tee -a "$AUDIT_LOG"
            ((fixes_needed++))
        fi
    fi

    # Check for correct model assignment
    case "$agent" in
        "CEO"|"CTO")
            expected_model="lfm2e:latest"
            ;;
        *)
            expected_model="mistral:latest"
            ;;
    esac

    if [ -f "$agent_path/persona.json" ]; then
        current_model=$(jq -r '.model // "not-set"' "$agent_path/persona.json" 2>/dev/null)
        if [ "$current_model" != "$expected_model" ]; then
            echo "   ❌ Update $agent model from $current_model to $expected_model" | tee -a "$AUDIT_LOG"
            ((fixes_needed++))
        fi
    fi
done

echo ""
echo "📊 AUDIT SUMMARY" | tee -a "$AUDIT_LOG"
echo "=================" | tee -a "$AUDIT_LOG"
echo "   🤖 Agents audited: ${#AGENTS[@]}" | tee -a "$AUDIT_LOG"
echo "   🔧 Fixes needed: $fixes_needed" | tee -a "$AUDIT_LOG"
echo "   📁 Log file: $AUDIT_LOG" | tee -a "$AUDIT_LOG"

if [ $fixes_needed -eq 0 ]; then
    echo "   🎯 Status: AGENTS READY FOR ONBOARDING ✅" | tee -a "$AUDIT_LOG"
    exit 0
else
    echo "   🎯 Status: REALIGNMENT REQUIRED ⚠️" | tee -a "$AUDIT_LOG"
    echo ""
    echo "💡 Next steps:" | tee -a "$AUDIT_LOG"
    echo "   • Run: ./realign_agents.sh" | tee -a "$AUDIT_LOG"
    echo "   • Test memory system" | tee -a "$AUDIT_LOG"
    echo "   • Validate routing" | tee -a "$AUDIT_LOG"
    exit 1
fi

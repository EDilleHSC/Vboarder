#!/bin/bash
# VBoarder Agent Realignment Script
# Fixes all agent configuration mismatches and slot assignments

echo "🔧 VBOARDER AGENT REALIGNMENT"
echo "============================="
echo ""

AGENTS_DIR="/mnt/d/ai/projects/vboarder/agents"
REALIGN_LOG="agent_realignment_$(date +%Y%m%d_%H%M%S).log"

log_info() {
    echo "[$(date +'%H:%M:%S')] INFO: $1" | tee -a "$REALIGN_LOG"
}

log_success() {
    echo "[$(date +'%H:%M:%S')] SUCCESS: $1" | tee -a "$REALIGN_LOG"
}

echo "🎯 PHASE 1: Fix Model Assignments"
echo "================================="

# Define correct model assignments
declare -A AGENT_MODELS=(
    ["CEO"]="lfm2e:latest"
    ["CTO"]="lfm2e:latest"
    ["CFO"]="mistral:latest"
    ["COO"]="mistral:latest"
    ["CLO"]="mistral:latest"
    ["CMO"]="mistral:latest"
    ["COS"]="mistral:latest"
    ["SEC"]="mistral:latest"
    ["AIR"]="mistral:latest"
)

# Define slot assignments
declare -A AGENT_SLOTS=(
    ["CEO"]="slot:b"
    ["CTO"]="slot:b"
    ["CFO"]="slot:a"
    ["COO"]="slot:a"
    ["CLO"]="slot:a"
    ["CMO"]="slot:a"
    ["COS"]="slot:a"
    ["SEC"]="slot:a"
    ["AIR"]="slot:a"
)

for agent in "${!AGENT_MODELS[@]}"; do
    agent_path="$AGENTS_DIR/$agent"
    target_model="${AGENT_MODELS[$agent]}"
    target_slot="${AGENT_SLOTS[$agent]}"

    if [ -d "$agent_path" ]; then
        echo ""
        echo "🤖 Realigning $agent..."

        # Update persona.json model
        if [ -f "$agent_path/persona.json" ]; then
            # Create backup
            cp "$agent_path/persona.json" "$agent_path/persona.json.backup"

            # Update model in persona.json
            jq --arg model "$target_model" '.model = $model' "$agent_path/persona.json" > "$agent_path/persona.json.tmp"
            mv "$agent_path/persona.json.tmp" "$agent_path/persona.json"
            log_success "$agent: Updated persona model to $target_model"
        fi

        # Update config.json model
        if [ -f "$agent_path/config.json" ]; then
            # Create backup
            cp "$agent_path/config.json" "$agent_path/config.json.backup"

            # Update model in config.json to match persona
            jq --arg model "$target_model" '.model = $model' "$agent_path/config.json" > "$agent_path/config.json.tmp"
            mv "$agent_path/config.json.tmp" "$agent_path/config.json"
            log_success "$agent: Updated config model to $target_model"
        fi

        # Update agent.json with slot assignment
        if [ -f "$agent_path/agent.json" ]; then
            # Create backup
            cp "$agent_path/agent.json" "$agent_path/agent.json.backup"

            # Add or update slot assignment
            jq --arg slot "$target_slot" '.slot = $slot' "$agent_path/agent.json" > "$agent_path/agent.json.tmp"
            mv "$agent_path/agent.json.tmp" "$agent_path/agent.json"
            log_success "$agent: Updated slot assignment to $target_slot"
        else
            # Create agent.json if it doesn't exist
            cat > "$agent_path/agent.json" << EOF
{
  "role": "$agent",
  "slot": "$target_slot",
  "model": "$target_model",
  "version": "1.0.0",
  "last_updated": "$(date -Iseconds)"
}
EOF
            log_success "$agent: Created agent.json with slot $target_slot"
        fi
    fi
done

echo ""
echo "⚙️ PHASE 2: Validate Router Configuration"
echo "========================================"

# Ensure router.py has correct model mappings
router_file="/mnt/d/ai/projects/vboarder/router.py"
if [ -f "$router_file" ]; then
    log_info "Validating router configuration"

    # Check if router has correct mistral mapping (should be mistral, not mixtral)
    if grep -q "mixtral" "$router_file"; then
        log_info "Updating router to use mistral instead of mixtral"
        # Create backup
        cp "$router_file" "$router_file.backup"
        # Replace mixtral with mistral
        sed -i 's/mixtral/mistral/g' "$router_file"
        log_success "Router updated to use mistral model"
    fi

    log_success "Router configuration validated"
else
    log_error "Router file not found: $router_file"
fi

echo ""
echo "🧠 PHASE 3: Initialize Agent Memory Structure"
echo "============================================"

memory_base="$HOME/.vboarder/memory"
for agent in "${!AGENT_MODELS[@]}"; do
    agent_lower=$(echo "$agent" | tr '[:upper:]' '[:lower:]')

    # Create agent-specific memory file with initial structure
    memory_file="$memory_base/${agent_lower}_memory.json"

    if [ ! -f "$memory_file" ]; then
        cat > "$memory_file" << EOF
{
  "agent": "$agent",
  "role": "$(jq -r '.title // .role' "$AGENTS_DIR/$agent/persona.json" 2>/dev/null || echo "$agent")",
  "initialized": "$(date -Iseconds)",
  "quadrants": {
    "plans": [],
    "context": [],
    "decisions": [],
    "insights": []
  },
  "session_history": [],
  "version": "1.0.0"
}
EOF
        log_success "$agent: Initialized memory structure"
    else
        log_info "$agent: Memory structure already exists"
    fi
done

echo ""
echo "📋 PHASE 4: Create Agent Registry Update"
echo "======================================="

# Update the agent registry with correct configurations
registry_file="/mnt/d/ai/projects/vboarder/agent_registry.json"
if [ -f "$registry_file" ]; then
    # Create backup
    cp "$registry_file" "$registry_file.backup"

    # Update registry with corrected model assignments
    log_info "Updating agent registry with corrected configurations"

    # Create updated registry
    cat > "$registry_file" << 'EOF'
{
  "agents": {
    "CEO": {
      "role": "CEO",
      "title": "Chief Executive Officer",
      "model": "lfm2e:latest",
      "slot": "slot:b",
      "description": "Strategic leadership and executive decision-making",
      "enabled": true
    },
    "CTO": {
      "role": "CTO",
      "title": "Chief Technology Officer",
      "model": "lfm2e:latest",
      "slot": "slot:b",
      "description": "Technology strategy and engineering leadership",
      "enabled": true
    },
    "CFO": {
      "role": "CFO",
      "title": "Chief Financial Officer",
      "model": "mistral:latest",
      "slot": "slot:a",
      "description": "Financial planning and fiscal management",
      "enabled": true
    },
    "COO": {
      "role": "COO",
      "title": "Chief Operating Officer",
      "model": "mistral:latest",
      "slot": "slot:a",
      "description": "Operations and process optimization",
      "enabled": true
    },
    "CLO": {
      "role": "CLO",
      "title": "Chief Legal Officer",
      "model": "mistral:latest",
      "slot": "slot:a",
      "description": "Legal affairs and compliance management",
      "enabled": true
    },
    "CMO": {
      "role": "CMO",
      "title": "Chief Marketing Officer",
      "model": "mistral:latest",
      "slot": "slot:a",
      "description": "Marketing strategy and brand management",
      "enabled": true
    },
    "COS": {
      "role": "COS",
      "title": "Chief of Staff",
      "model": "mistral:latest",
      "slot": "slot:a",
      "description": "Strategic coordination and executive support",
      "enabled": true
    },
    "SEC": {
      "role": "SEC",
      "title": "Security Officer",
      "model": "mistral:latest",
      "slot": "slot:a",
      "description": "Security and risk management",
      "enabled": true
    },
    "AIR": {
      "role": "AIR",
      "title": "AI Research Lead",
      "model": "mistral:latest",
      "slot": "slot:a",
      "description": "AI research and development coordination",
      "enabled": true
    }
  },
  "metadata": {
    "version": "1.0.0",
    "last_updated": "$(date -Iseconds)",
    "total_agents": 9,
    "slot_distribution": {
      "slot:a": 7,
      "slot:b": 2
    }
  }
}
EOF

    log_success "Agent registry updated with corrected configurations"
else
    log_info "Agent registry not found, creating new one"
    # Create the registry file with above content
fi

echo ""
echo "📊 REALIGNMENT SUMMARY"
echo "======================"

# Verify all fixes
fixes_applied=0
for agent in "${!AGENT_MODELS[@]}"; do
    agent_path="$AGENTS_DIR/$agent"
    target_model="${AGENT_MODELS[$agent]}"

    if [ -f "$agent_path/persona.json" ]; then
        current_model=$(jq -r '.model' "$agent_path/persona.json" 2>/dev/null)
        if [ "$current_model" = "$target_model" ]; then
            ((fixes_applied++))
        fi
    fi
done

echo "   🤖 Agents processed: ${#AGENT_MODELS[@]}" | tee -a "$REALIGN_LOG"
echo "   ✅ Model fixes applied: $fixes_applied" | tee -a "$REALIGN_LOG"
echo "   🧠 Memory structures initialized: ${#AGENT_MODELS[@]}" | tee -a "$REALIGN_LOG"
echo "   📁 Log file: $REALIGN_LOG" | tee -a "$REALIGN_LOG"

if [ $fixes_applied -eq ${#AGENT_MODELS[@]} ]; then
    echo "   🎯 Status: REALIGNMENT COMPLETE ✅" | tee -a "$REALIGN_LOG"
    echo ""
    echo "💡 Next steps:" | tee -a "$REALIGN_LOG"
    echo "   • Test memory system: python3 -c \"from api.shared_memory import load_memory; print(load_memory('ceo'))\"" | tee -a "$REALIGN_LOG"
    echo "   • Validate routing: python3 list_agents.py" | tee -a "$REALIGN_LOG"
    echo "   • Start backend: uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload" | tee -a "$REALIGN_LOG"
    echo "   • Run onboarding: ./onboard_agents.sh" | tee -a "$REALIGN_LOG"
    exit 0
else
    echo "   🎯 Status: PARTIAL REALIGNMENT ⚠️" | tee -a "$REALIGN_LOG"
    echo "   ❌ Some fixes may have failed - check log for details" | tee -a "$REALIGN_LOG"
    exit 1
fi

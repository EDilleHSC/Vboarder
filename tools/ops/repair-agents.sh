#!/usr/bin/env bash
# VBoarder Agent Repair Utility v1.0
# Validates and rebuilds agent structures and registry

set -euo pipefail

echo "═══════════════════════════════════════════════════════════════"
echo "  VBoarder – Agent Repair & Validation Utility"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Configuration
ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
AGENTS_DIR="${ROOT_DIR}/agents"
REGISTRY_FILE="${ROOT_DIR}/agent_registry.json"
TMP_REGISTRY="${ROOT_DIR}/.tmp_agent_registry.json"
BACKUP_REGISTRY="${ROOT_DIR}/agent_registry.json.backup"

DRY_RUN=${DRY_RUN:-false}

echo "📂 Root Directory: $ROOT_DIR"
echo "📁 Agents Directory: $AGENTS_DIR"
echo "📋 Registry File: $REGISTRY_FILE"
echo "🔍 Dry Run: $DRY_RUN"
echo ""

# Counters
VALID_AGENTS=0
MISSING_FILES_COUNT=0
REPAIRED_COUNT=0

# Arrays
declare -a AGENT_ROLES
declare -a MISSING_FILES
declare -a REPAIRED_AGENTS

# Backup existing registry
if [ -f "$REGISTRY_FILE" ]; then
    if [ "$DRY_RUN" = "false" ]; then
        cp "$REGISTRY_FILE" "$BACKUP_REGISTRY"
        echo "✅ Backed up existing registry to: $BACKUP_REGISTRY"
    else
        echo "🔍 [DRY RUN] Would backup registry to: $BACKUP_REGISTRY"
    fi
    echo ""
fi

# Initialize temporary registry
if [ "$DRY_RUN" = "false" ]; then
    echo "[" > "$TMP_REGISTRY"
fi

# Helper function to create missing files
create_missing_file() {
    local file_path="$1"
    local file_type="$2"
    local agent_role="$3"

    if [ "$DRY_RUN" = "false" ]; then
        mkdir -p "$(dirname "$file_path")"

        case "$file_type" in
            "config")
                cat > "$file_path" << EOF
{
  "role": "${agent_role}",
  "title": "${agent_role} Agent",
  "description": "AI agent for VBoarder",
  "model": "mistral:latest",
  "temperature": 0.7,
  "max_tokens": 2000
}
EOF
                ;;
            "persona")
                cat > "$file_path" << EOF
{
  "name": "${agent_role}",
  "role": "${agent_role} Agent",
  "personality": "Professional and helpful",
  "communication_style": "Clear and concise",
  "expertise": ["Strategy", "Leadership"],
  "goals": ["Assist users", "Provide insights"]
}
EOF
                ;;
            "system_prompt")
                cat > "$file_path" << EOF
You are the ${agent_role} agent for VBoarder, a multi-agent AI system.

Your role is to provide expert guidance and insights in your domain.

Key responsibilities:
- Respond professionally and helpfully
- Provide accurate information
- Maintain context across conversations
- Collaborate with other agents when needed

Communication style: Professional, clear, and concise.
EOF
                ;;
            "memory")
                echo "" > "$file_path"
                ;;
        esac

        echo "   ✅ Created missing $file_type: $file_path"
        ((REPAIRED_COUNT++))
        REPAIRED_AGENTS+=("$agent_role - $file_type")
    else
        echo "   🔍 [DRY RUN] Would create: $file_path"
    fi
}

# Process each agent directory
echo "═══════════════════════════════════════════════════════════════"
echo "  Scanning Agent Directories"
echo "═══════════════════════════════════════════════════════════════"
echo ""

for agent_dir in "$AGENTS_DIR"/*; do
    # Skip if not a directory
    [[ -d "$agent_dir" ]] || continue

    # Get role name
    role=$(basename "$agent_dir")

    # Skip special directories (hardened whitelist)
    case "$role" in
        "__pycache__"|"default"|"venv"|"logs"|"tools"|"EXAMPLE"|"test_agent"|"agent_runtime"|"ops_agent")
            echo "   ⏭️  Skipping garbage dir: $role"
            continue
            ;;
    esac

    # Convert to uppercase for registry
    ROLE_UPPER=$(echo "$role" | tr '[:lower:]' '[:upper:]')

    echo "🔍 Checking agent: $ROLE_UPPER"

    # Required files
    CONFIG="$agent_dir/config.json"
    PERSONA="$agent_dir/persona.json"
    MEMORY="$agent_dir/memory.jsonl"
    SYSTEM_PROMPT="$agent_dir/personas/system_detailed.txt"

    # Check for missing files
    HAS_MISSING=false

    if [[ ! -f "$CONFIG" ]]; then
        echo "   ⚠️  Missing: config.json"
        create_missing_file "$CONFIG" "config" "$ROLE_UPPER"
        HAS_MISSING=true
    fi

    if [[ ! -f "$PERSONA" ]]; then
        echo "   ⚠️  Missing: persona.json"
        create_missing_file "$PERSONA" "persona" "$ROLE_UPPER"
        HAS_MISSING=true
    fi

    if [[ ! -f "$SYSTEM_PROMPT" ]]; then
        echo "   ⚠️  Missing: personas/system_detailed.txt"
        create_missing_file "$SYSTEM_PROMPT" "system_prompt" "$ROLE_UPPER"
        HAS_MISSING=true
    fi

    if [[ ! -f "$MEMORY" ]]; then
        echo "   ℹ️  Creating: memory.jsonl"
        create_missing_file "$MEMORY" "memory" "$ROLE_UPPER"
    fi

    # If still missing critical files after repair, skip
    if [[ ! -f "$CONFIG" || ! -f "$PERSONA" || ! -f "$SYSTEM_PROMPT" ]]; then
        echo "   ❌ Still missing required files after repair attempt"
        MISSING_FILES+=("$ROLE_UPPER")
        ((MISSING_FILES_COUNT++))
        echo ""
        continue
    fi

    # Load metadata from config.json
    if command -v jq &> /dev/null; then
        title=$(jq -r '.title // "'"${ROLE_UPPER} Agent"'"' "$CONFIG" 2>/dev/null || echo "${ROLE_UPPER} Agent")
        description=$(jq -r '.description // "AI agent for VBoarder"' "$CONFIG" 2>/dev/null || echo "AI agent for VBoarder")
        model=$(jq -r '.model // "mistral:latest"' "$CONFIG" 2>/dev/null || echo "mistral:latest")
        temp=$(jq -r '.temperature // 0.7' "$CONFIG" 2>/dev/null || echo "0.7")
    else
        # Fallback if jq not available
        title="${ROLE_UPPER} Agent"
        description="AI agent for VBoarder"
        model="mistral:latest"
        temp="0.7"
    fi

    # Add to registry
    if [ "$DRY_RUN" = "false" ]; then
        if command -v jq &> /dev/null; then
            jq -n \
              --arg role "$ROLE_UPPER" \
              --arg title "$title" \
              --arg description "$description" \
              --arg model "$model" \
              --arg temperature "$temp" \
              --arg system_prompt "agents/$role/personas/system_detailed.txt" \
              --arg memory "agents/$role/memory.jsonl" \
              --arg persona_file "agents/$role/persona.json" \
              --arg config_file "agents/$role/config.json" \
              '{
                role: $role,
                title: $title,
                description: $description,
                model: $model,
                temperature: ($temperature | tonumber),
                max_tokens: 2000,
                system_prompt: $system_prompt,
                memory: $memory,
                persona_file: $persona_file,
                config_file: $config_file,
                enabled: true
              }' >> "$TMP_REGISTRY"

            echo "," >> "$TMP_REGISTRY"
        fi
    else
        echo "   🔍 [DRY RUN] Would add to registry: $ROLE_UPPER"
    fi

    AGENT_ROLES+=("$ROLE_UPPER")
    ((VALID_AGENTS++))

    if [ "$HAS_MISSING" = true ]; then
        echo "   ✅ Repaired and validated"
    else
        echo "   ✅ Validated"
    fi

    echo ""
done

# Finalize registry
if [ "$DRY_RUN" = "false" ]; then
    if [ ${#AGENT_ROLES[@]} -eq 0 ]; then
        echo "❌ No valid agents found. Registry not updated."
        rm -f "$TMP_REGISTRY"
        exit 1
    fi

    # Remove trailing comma and close array
    if command -v sed &> /dev/null; then
        sed -i '$ s/,$//' "$TMP_REGISTRY" 2>/dev/null || sed -i '' '$ s/,$//' "$TMP_REGISTRY" 2>/dev/null
    fi
    echo "]" >> "$TMP_REGISTRY"

    # Validate JSON
    if command -v jq &> /dev/null; then
        if jq empty "$TMP_REGISTRY" 2>/dev/null; then
            mv "$TMP_REGISTRY" "$REGISTRY_FILE"
            echo "✅ Registry validated and updated"
        else
            echo "❌ Generated registry has invalid JSON"
            cat "$TMP_REGISTRY"
            rm "$TMP_REGISTRY"
            exit 1
        fi
    else
        # No jq, just move it
        mv "$TMP_REGISTRY" "$REGISTRY_FILE"
        echo "⚠️  Registry updated (validation skipped - jq not available)"
    fi
fi

# Summary
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Repair Summary"
echo "═══════════════════════════════════════════════════════════════"
echo ""

echo "📊 Statistics:"
echo "   • Valid agents: $VALID_AGENTS"
echo "   • Files repaired: $REPAIRED_COUNT"
echo "   • Agents with missing files: $MISSING_FILES_COUNT"
echo ""

if [ ${#AGENT_ROLES[@]} -gt 0 ]; then
    echo "✅ Registered agents (${#AGENT_ROLES[@]}):"
    for agent in "${AGENT_ROLES[@]}"; do
        echo "   • $agent"
    done
    echo ""
fi

if [ ${#REPAIRED_AGENTS[@]} -gt 0 ]; then
    echo "🔧 Repaired files:"
    for item in "${REPAIRED_AGENTS[@]}"; do
        echo "   • $item"
    done
    echo ""
fi

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
    echo "⚠️  Agents still missing files (not included in registry):"
    for agent in "${MISSING_FILES[@]}"; do
        echo "   • $agent"
    done
    echo ""
    echo "Run the script again to attempt repair, or manually create missing files."
    echo ""
fi

if [ "$DRY_RUN" = "false" ]; then
    echo "🎯 Repair complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Validate registry: cat agent_registry.json | jq"
    echo "  2. Test backend: uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload"
    echo "  3. Test agents: bash tools/ops/test-all-agents.sh"
    echo ""

    if [ -f "$BACKUP_REGISTRY" ]; then
        echo "💾 Backup saved: $BACKUP_REGISTRY"
        echo "   To restore: cp $BACKUP_REGISTRY $REGISTRY_FILE"
        echo ""
    fi

    # Optional: Auto-restart backend if AUTO_RESTART=true
    if [ "${AUTO_RESTART:-false}" = "true" ]; then
        echo "🔁 AUTO_RESTART enabled - Restarting backend..."
        pkill -f "uvicorn api.main:app" 2>/dev/null || true
        sleep 1
        echo "   Starting uvicorn on port 3738..."
        nohup uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload > logs/uvicorn.log 2>&1 &
        echo "   ✅ Backend restarted (PID: $!)"
        echo "   📋 Logs: tail -f logs/uvicorn.log"
        echo ""
    fi
else
    echo "🔍 DRY RUN COMPLETE - No changes made"
    echo ""
    echo "To execute repair, run:"
    echo "  bash tools/ops/repair-agents.sh"
    echo ""
fi

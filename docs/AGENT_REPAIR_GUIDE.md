# Agent Repair System - Complete Guide

**Version:** 1.1 (Hardened)
**Last Updated:** October 14, 2025

> **🔒 NEW:** Hardened with garbage directory filtering, file logging, and auto-restart.
> See `docs/AGENT_REPAIR_HARDENING.md` for complete hardening details.

## Overview

The VBoarder agent repair system provides comprehensive validation and automatic repair of agent structures and the registry file.

## Available Tools

### 1. `repair-agents.sh` (v1.1 - HARDENED - Recommended)

**Location:** `tools/ops/repair-agents.sh`

**Features:**

- ✅ Scans all agent directories dynamically
- ✅ Creates missing config.json files
- ✅ Creates missing persona.json files
- ✅ Creates missing system prompts
- ✅ Creates empty memory.jsonl files
- ✅ Rebuilds agent_registry.json dynamically
- ✅ Backs up existing registry
- ✅ Validates JSON output
- ✅ Supports dry-run mode
- ✅ **NEW (v1.1):** Garbage directory whitelist (skips **pycache**, venv, logs, etc.)
- ✅ **NEW (v1.1):** Optional auto-restart (AUTO_RESTART=true)
- ✅ **NEW (v1.1):** File logging to logs/backend.log

**Usage:**

```bash
# Dry run (preview changes)
DRY_RUN=true bash tools/ops/repair-agents.sh

# Execute repair
bash tools/ops/repair-agents.sh

# Execute with auto-restart
AUTO_RESTART=true bash tools/ops/repair-agents.sh
```

### 2. `rebuild-registry.py` (Existing)

**Location:** `tools/ops/rebuild-registry.py`

**Features:**

- Rebuilds registry from hardcoded agent definitions
- Useful when you know exact agent configuration
- Python-based for portability

**Usage:**

```bash
python3 tools/ops/rebuild-registry.py
```

### 3. `rebuild-agents.py` (Existing)

**Location:** `tools/ops/rebuild-agents.py`

**Features:**

- Creates all agent structure files
- Generates default persona and config files
- Creates system prompts

**Usage:**

```bash
python3 tools/ops/rebuild-agents.py
```

### 4. `repair-all-agents.sh` (Orchestrator)

**Location:** `tools/ops/repair-all-agents.sh`

**Features:**

- Runs complete repair sequence
- Includes BOM fix and path fixes
- Comprehensive validation

**Usage:**

```bash
bash tools/ops/repair-all-agents.sh
```

## Comparison Matrix

| Feature                   | repair-agents.sh | rebuild-registry.py | rebuild-agents.py | repair-all-agents.sh |
| ------------------------- | ---------------- | ------------------- | ----------------- | -------------------- |
| **Scans directories**     | ✅               | ❌                  | ✅                | ✅ (via others)      |
| **Creates missing files** | ✅               | ❌                  | ✅                | ✅ (via others)      |
| **Dynamic registry**      | ✅               | ❌                  | ❌                | ❌                   |
| **Backs up registry**     | ✅               | ❌                  | ❌                | ✅                   |
| **Dry run mode**          | ✅               | ❌                  | ❌                | ❌                   |
| **BOM fix**               | ❌               | ❌                  | ❌                | ✅                   |
| **Path fix**              | ❌               | ❌                  | ❌                | ✅                   |
| **Language**              | Bash             | Python              | Python            | Bash                 |

## When to Use Each Tool

### Use `repair-agents.sh` when:

- ✅ You want automatic detection and repair
- ✅ You have agents with varying configurations
- ✅ You want to preview changes first (dry run)
- ✅ You need dynamic registry generation
- ✅ You want comprehensive validation

### Use `rebuild-registry.py` when:

- ✅ You want hardcoded, known-good configurations
- ✅ Registry is completely broken
- ✅ You need Python-based solution
- ✅ Agent files exist, just need registry

### Use `rebuild-agents.py` when:

- ✅ Agent directories are completely missing files
- ✅ You want to start from scratch
- ✅ Need to create all agent structures

### Use `repair-all-agents.sh` when:

- ✅ You want complete system repair
- ✅ Need BOM and path fixes
- ✅ Want comprehensive validation
- ✅ One-command full repair

## Typical Workflows

### Workflow 1: Quick Repair (Recommended)

```bash
# 1. Preview what will be fixed
DRY_RUN=true bash tools/ops/repair-agents.sh

# 2. Execute repair
bash tools/ops/repair-agents.sh

# 3. Validate
bash tools/ops/validate-all.sh
```

### Workflow 2: Complete Rebuild

```bash
# 1. Rebuild all agent files
python3 tools/ops/rebuild-agents.py

# 2. Fix registry and paths
bash tools/ops/repair-all-agents.sh

# 3. Validate
bash tools/ops/validate-all.sh
```

### Workflow 3: Registry Only

```bash
# Option A: Dynamic from directories
bash tools/ops/repair-agents.sh

# Option B: From definitions
python3 tools/ops/rebuild-registry.py

# Validate
cat agent_registry.json | jq
```

### Workflow 4: Emergency Full Repair

```bash
# Complete system repair
bash tools/ops/repair-all-agents.sh

# Validate
bash tools/ops/validate-all.sh
bash tools/ops/test-all-agents.sh
```

## Required Agent Files

Each agent directory needs:

```
agents/ROLE/
├── config.json              # Agent configuration
├── persona.json             # Agent personality/traits
├── memory.jsonl             # Conversation history (can be empty)
└── personas/
    └── system_detailed.txt  # System prompt
```

### config.json Example

```json
{
  "role": "CEO",
  "title": "Chief Executive Officer",
  "description": "Strategic leadership for VBoarder",
  "model": "mixtral:latest",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

### persona.json Example

```json
{
  "name": "CEO",
  "role": "Chief Executive Officer",
  "personality": "Strategic and visionary",
  "communication_style": "Professional and decisive",
  "expertise": ["Strategy", "Leadership", "Business"],
  "goals": ["Guide company direction", "Make strategic decisions"]
}
```

### system_detailed.txt Example

```
You are the CEO agent for VBoarder, a multi-agent AI system.

Your role is to provide strategic leadership and executive guidance.

Key responsibilities:
- Strategic planning and vision
- High-level decision making
- Cross-functional coordination
- Business guidance

Communication style: Professional, strategic, and decisive.
```

## Registry Format

The `agent_registry.json` file contains:

```json
[
  {
    "role": "CEO",
    "title": "Chief Executive Officer",
    "description": "Strategic leadership for VBoarder",
    "model": "mixtral:latest",
    "temperature": 0.7,
    "max_tokens": 2000,
    "system_prompt": "agents/CEO/personas/system_detailed.txt",
    "memory": "agents/CEO/memory.jsonl",
    "persona_file": "agents/CEO/persona.json",
    "config_file": "agents/CEO/config.json",
    "enabled": true
  }
]
```

## Troubleshooting

### "No valid agents found"

```bash
# Check agent directories
ls -la agents/

# Ensure CEO, CTO, etc. exist
# Run complete rebuild
python3 tools/ops/rebuild-agents.py
bash tools/ops/repair-agents.sh
```

### "Invalid JSON in registry"

```bash
# Check for BOM
python3 tools/ops/fix-registry-bom.py

# Rebuild registry
bash tools/ops/repair-agents.sh

# Validate
cat agent_registry.json | jq
```

### "Missing files after repair"

```bash
# Check permissions
ls -la agents/CEO/

# Manual creation if needed
mkdir -p agents/CEO/personas
touch agents/CEO/config.json
touch agents/CEO/persona.json
touch agents/CEO/memory.jsonl
touch agents/CEO/personas/system_detailed.txt

# Re-run repair
bash tools/ops/repair-agents.sh
```

### "Agent responds but not in registry"

```bash
# Registry might be cached
# Restart backend
pkill -f uvicorn
uvicorn api.main:app --host 127.0.0.1 --port 3738 --reload
```

## Safety Features

### Backups

- `repair-agents.sh` creates `agent_registry.json.backup`
- Original preserved before any changes

### Dry Run Mode

```bash
# Preview all changes without modifying files
DRY_RUN=true bash tools/ops/repair-agents.sh
```

### Validation

- JSON validation with jq (if available)
- File existence checks
- Path validation

### Recovery

```bash
# Restore from backup
cp agent_registry.json.backup agent_registry.json

# Re-run repair if needed
bash tools/ops/repair-agents.sh
```

## Best Practices

1. **Always preview first:**

   ```bash
   DRY_RUN=true bash tools/ops/repair-agents.sh
   ```

2. **Validate after repair:**

   ```bash
   bash tools/ops/validate-all.sh
   bash tools/ops/test-all-agents.sh
   ```

3. **Keep backups:**

   - Automatic backup created by repair script
   - Manual: `cp agent_registry.json agent_registry.json.manual-backup`

4. **Check git status:**

   ```bash
   git status
   git diff agent_registry.json
   ```

5. **Test immediately:**
   ```bash
   curl http://127.0.0.1:3738/agents | jq
   bash tools/ops/test-all-agents.sh
   ```

## Quick Reference

### Common Commands

```bash
# Quick repair
bash tools/ops/repair-agents.sh

# Preview only
DRY_RUN=true bash tools/ops/repair-agents.sh

# Complete rebuild
bash tools/ops/repair-all-agents.sh

# Validate
bash tools/ops/validate-all.sh

# Test agents
bash tools/ops/test-all-agents.sh

# Check registry
cat agent_registry.json | jq '. | length'
```

### File Locations

- Repair script: `tools/ops/repair-agents.sh`
- Registry: `agent_registry.json` (root)
- Agent dirs: `agents/CEO/`, `agents/CTO/`, etc.
- Backup: `agent_registry.json.backup`

---

_For more help, see:_

- `docs/TROUBLESHOOTING.md`
- `tools/ops/TEST_SCRIPT_FIX.md`
- `CTO_SHIFT_HANDOFF.md`

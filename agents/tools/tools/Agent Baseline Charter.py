# === AGENT BASELINE CHARTER ===
# Purpose: This doc outlines the baseline structure for spinning up a new agent quickly.
# Location: /tools/templates/agent_baseline/

AGENT_BASELINE = {
    "required_files": [
        "agent.json",
        "config.json",
        "persona.md",
        "prompt.md",
        "schedule.json"
    ],
    "required_dirs": {
        "config/": ["modes.json", "rules.json", "stoplight.json"],
        "memory/": ["conversation_history.json", "memory.json", "office_knowledge.json", "personal_knowledge.json", "task_state.json"],
        "logs/": ["audit_log.json", "activity_log.json"]
    },
    "hookup_instructions": [
        "1. Copy the entire template directory to /agents/{NEW_AGENT_NAME}/",
        "2. Rename agent folder accordingly.",
        "3. In agent.json, set 'agent_name' to match the folder name.",
        "4. Run fix_all_agents_from_sec.py to sync schema fields.",
        "5. Register new agent in controller_bus.json if needed.",
        "6. Optional: Add to schedule.json for recurring tasks.",
        "7. Optional: Enable in central orchestrator for live ops."
    ],
    "metadata": {
        "version": "v1.0",
        "maintainer": "AI CTO Unit",
        "created_at": "2025-10-08"
    }
}

# Example usage (inside setup script)
if __name__ == "__main__":
    import json
    print(json.dumps(AGENT_BASELINE, indent=2))

#!/usr/bin/env python3
import os
import json

AGENTS_DIR = "../agents/"
LOG_PATH = "./logs/logic_audit_log.json"

os.makedirs("logs", exist_ok=True)

def audit_agent_paths():
    print("🧠 Auditing agent path logic...")
    audit_result = {}

    if not os.path.exists(AGENTS_DIR):
        print(f"❌ Agents directory not found: {AGENTS_DIR}")
        return

    for agent_name in os.listdir(AGENTS_DIR):
        agent_path = os.path.join(AGENTS_DIR, agent_name)
        if os.path.isdir(agent_path):
            audit_result[agent_name] = {
                "path_exists": True,
                "config_found": os.path.exists(os.path.join(agent_path, "config.json")),
            }

    with open(LOG_PATH, "w") as f:
        json.dump(audit_result, f, indent=2)
    print(f"✅ Agent path audit saved to: {LOG_PATH}")

if __name__ == "__main__":
    audit_agent_paths()

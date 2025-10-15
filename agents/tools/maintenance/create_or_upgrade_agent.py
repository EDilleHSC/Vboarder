# create_or_upgrade_agent.py
import os
import json
from datetime import datetime
import shutil

DEFAULT_FILES = {
    "prompt.md": "# TODO: Define system-level behavior for this agent.\n",
    "persona.md": "# TODO: Define tone, personality, and perspective.\n",
    "memory/memory.json": "{}\n",
    "memory/task_state.json": "{}\n",
    "memory/conversation_history.json": "[]\n",
    "logs/audit_log.json": "[]\n",
    "logs/activity_log.json": "[]\n",
    "config/modes.json": json.dumps(
        {
            "parameters": {
                "chat": {"max_tokens": 512, "temperature": 0.3},
                "plan": {"max_tokens": 512, "temperature": 0.2},
                "execute": {"max_tokens": 256, "temperature": 0.1},
                "research": {"max_tokens": 1024, "temperature": 0.2},
            },
            "default": "chat",
            "supported": ["chat", "plan", "research", "execute"],
        },
        indent=2,
    ),
    "config/stoplight.json": json.dumps(
        {
            "status": "green",
            "changed_at": datetime.utcnow().isoformat() + "Z",
            "notes": "",
        },
        indent=2,
    ),
    "config/rules.json": "[]\n",
}


def ensure_file(path, content):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)


def upgrade_agent(agent_path, backups_dir):
    role = os.path.basename(agent_path)
    report = {"agent": role, "actions": []}
    agent_json_path = os.path.join(agent_path, "agent.json")

    if not os.path.exists(agent_json_path):
        report["actions"].append("❌ Missing agent.json — skipped")
        return report

    # Backup original
    os.makedirs(backups_dir, exist_ok=True)
    backup_path = os.path.join(backups_dir, f"{role}_agent.json")
    shutil.copy(agent_json_path, backup_path)
    report["actions"].append("📦 Backed up agent.json")

    # Load and modify
    with open(agent_json_path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    data["prompt_path"] = "prompt.md"
    data["persona_path"] = "persona.md"
    data["memory_path"] = "memory/memory.json"
    data["modes_path"] = "config/modes.json"
    data["log_path"] = "logs/audit_log.json"
    data["stoplight_path"] = "config/stoplight.json"

    # Write updated agent.json
    with open(agent_json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    report["actions"].append("✅ Updated agent.json with linked paths")

    # Create missing files
    for rel_path, content in DEFAULT_FILES.items():
        abs_path = os.path.join(agent_path, rel_path)
        if not os.path.exists(abs_path):
            ensure_file(abs_path, content)
            report["actions"].append(f"🆕 Created: {rel_path}")

    # Cleanup old folders
    for stale in ["prompts", "personas", "config.json", "agent_config.json"]:
        stale_path = os.path.join(agent_path, stale)
        if os.path.isdir(stale_path):
            shutil.rmtree(stale_path)
            report["actions"].append(f"🧹 Removed folder: {stale}")
        elif os.path.isfile(stale_path):
            os.remove(stale_path)
            report["actions"].append(f"🧹 Removed file: {stale}")

    return report


def run_upgrade(agents_dir):
    logs = []
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(agents_dir, "backups", timestamp)

    for role in os.listdir(agents_dir):
        path = os.path.join(agents_dir, role)
        if os.path.isdir(path):
            log = upgrade_agent(path, backup_dir)
            logs.append(log)

    with open(os.path.join(agents_dir, "upgrade_log.json"), "w") as f:
        json.dump(logs, f, indent=2)

    print(
        f"✅ Upgrade complete. Log saved to upgrade_log.json. Backups in {backup_dir}/"
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Upgrade all agents to V2 architecture."
    )
    parser.add_argument(
        "--agents_dir", required=True, help="Path to the agents directory"
    )
    args = parser.parse_args()

    run_upgrade(args.agents_dir)

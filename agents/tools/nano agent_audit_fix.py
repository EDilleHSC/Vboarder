#!/usr/bin/env python3
import os
import json
import shutil
from pathlib import Path

AGENT_DIR = Path(".").resolve()
AGENT_NAMES = ["AIR", "CEO", "CFO", "CLO", "CMO", "COO", "COS", "CTO", "SEC"]
REQUIRED_FILES = [
    "agent.json",
    "config.json",
    "memory.jsonl",
    "persona.md",
    "prompt.md",
    "schedule.json",
]
AUDIT_LOG = {
    "agents_checked": [],
    "repairs_made": [],
    "missing_files_created": [],
    "backup_path": "backups/clean/",
}
os.makedirs("logs", exist_ok=True)
os.makedirs(AUDIT_LOG["backup_path"], exist_ok=True)


def repair_or_create(agent_name):
    agent_path = AGENT_DIR / agent_name
    if not agent_path.exists():
        print(f"⚠️  {agent_name} directory missing")
        return

    AUDIT_LOG["agents_checked"].append(agent_name)
    agent_repairs = []

    for file in REQUIRED_FILES:
        fpath = agent_path / file

        if not fpath.exists():
            # Create empty shell
            if file.endswith(".json"):
                fpath.write_text("{}")
            elif file.endswith(".jsonl"):
                fpath.write_text("")
            elif file.endswith(".md"):
                fpath.write_text(f"# {agent_name} - {file}")
            agent_repairs.append(f"🛠️ Created missing {file}")
            AUDIT_LOG["missing_files_created"].append(f"{agent_name}/{file}")
        else:
            if file.endswith(".json"):
                try:
                    with open(fpath) as f:
                        json.load(f)
                except Exception:
                    fpath.write_text("{}")
                    agent_repairs.append(f"🩹 Fixed malformed {file}")
                    AUDIT_LOG["repairs_made"].append(f"{agent_name}/{file}")
            elif file.endswith(".jsonl"):
                if fpath.read_text().strip() == "":
                    agent_repairs.append(f"ℹ️  Empty memory: {file}")

    # Generate README
    readme = agent_path / "README.md"
    readme.write_text(
        f"# Agent: {agent_name}\n\nThis agent is auto-audited and ready.\n"
    )

    # Backup cleaned agent
    backup_target = Path(AUDIT_LOG["backup_path"]) / agent_name
    if backup_target.exists():
        shutil.rmtree(backup_target)
    shutil.copytree(agent_path, backup_target)

    print(f"✅ Audited {agent_name}")
    if agent_repairs:
        print("   " + "\n   ".join(agent_repairs))


for agent in AGENT_NAMES:
    repair_or_create(agent)

# Save full log
with open("logs/agent_audit_log.json", "w") as f:
    json.dump(AUDIT_LOG, f, indent=2)

print("🧾 Full audit log written to logs/agent_audit_log.json")

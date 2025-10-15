import os
import json
from datetime import datetime

REQUIRED_FILES = [
    "agent.json", "prompt.md", "persona.md", "README.md"
]
REQUIRED_DIRS = ["memory", "logs", "config"]

MEMORY_FILES = ["memory.json", "conversation_history.json", "personal_knowledge.json", "office_knowledge.json", "task_state.json"]

def is_valid_json(path):
    try:
        with open(path, 'r') as f:
            json.load(f)
        return True
    except:
        return False

def audit_agent(agent_path):
    agent_name = os.path.basename(agent_path)
    report = {"agent": agent_name, "files": {}, "folders": {}, "memory": {}}

    for fname in REQUIRED_FILES:
        fpath = os.path.join(agent_path, fname)
        report["files"][fname] = "✅" if os.path.exists(fpath) else "❌ MISSING"

    for dname in REQUIRED_DIRS:
        dpath = os.path.join(agent_path, dname)
        report["folders"][dname] = "✅" if os.path.isdir(dpath) else "❌ MISSING"

    memory_path = os.path.join(agent_path, "memory")
    if os.path.isdir(memory_path):
        for mf in MEMORY_FILES:
            mpath = os.path.join(memory_path, mf)
            if os.path.exists(mpath):
                report["memory"][mf] = "✅ Valid" if is_valid_json(mpath) else "❌ Invalid JSON"
            else:
                report["memory"][mf] = "❌ Missing"

    return report

def main():
    base_dir = os.getcwd()
    skip_dirs = {"logs", "tools", "Clean", "backups"}
    audit_log = []

    for entry in os.listdir(base_dir):
        full_path = os.path.join(base_dir, entry)
        if os.path.isdir(full_path) and entry not in skip_dirs:
            print(f"🔍 Auditing {entry}...")
            audit_log.append(audit_agent(full_path))

    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    out_path = os.path.join("logs", f"agent_logic_audit_{timestamp}.json")
    with open(out_path, "w") as f:
        json.dump(audit_log, f, indent=2)

    print(f"\n✅ Audit completed. Report saved to {out_path}")

if __name__ == "__main__":
    main()

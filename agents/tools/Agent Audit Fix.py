import os
import json
from pathlib import Path
from shutil import copytree, rmtree

AGENT_DIR = Path(".")
BACKUP_DIR = Path("backups/clean")
LOG_DIR = Path("logs")
TEMPLATE_MEMORY = '{"memory": []}\n'

AGENT_FILES = [
    "agent.json",
    "config.json",
    "memory.jsonl",
    "persona.md",
    "prompt.md",
    "schedule.json"
]

def is_valid_json(file_path):
    try:
        with open(file_path, 'r') as f:
            json.load(f)
        return True
    except:
        return False

def is_valid_jsonl(file_path):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        for line in lines:
            if line.strip():
                json.loads(line)
        return True
    except:
        return False

def write_readme(agent_name, status, issues):
    readme_path = AGENT_DIR / agent_name / "README.md"
    with open(readme_path, "w") as f:
        f.write(f"# Agent: {agent_name}\n")
        f.write(f"\n**Status:** {'✅ STABLE' if status else '❌ NEEDS REVIEW'}\n")
        if issues:
            f.write("\n## Issues Fixed:\n")
            for issue in issues:
                f.write(f"- {issue}\n")


def fix_agents():
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)

    agents = [d for d in AGENT_DIR.iterdir() if d.is_dir() and d.name.isupper()]
    
    results = {}
    
    for agent in agents:
        issues = []
        all_good = True
        files = {}

        for fname in AGENT_FILES:
            fpath = agent / fname
            if not fpath.exists():
                all_good = False
                issues.append(f"{fname} missing")
                if fname == "memory.jsonl":
                    fpath.write_text(TEMPLATE_MEMORY)
                    issues.append(f"{fname} created with default template")
                    files[fname] = "🛠️ FIXED"
                else:
                    files[fname] = "❌ MISSING"
                continue

            if fname.endswith(".json") and not is_valid_json(fpath):
                all_good = False
                issues.append(f"{fname} invalid JSON")
                files[fname] = "❌ CORRUPT"
                continue

            if fname.endswith(".jsonl") and not is_valid_jsonl(fpath):
                all_good = False
                fpath.write_text(TEMPLATE_MEMORY)
                issues.append(f"{fname} reset (invalid JSONL)")
                files[fname] = "🛠️ RESET"
                continue

            files[fname] = "✅ OK"

        # Backup clean version
        dst = BACKUP_DIR / agent.name
        if dst.exists():
            rmtree(dst)
        copytree(agent, dst)

        # Write readme
        write_readme(agent.name, all_good, issues)

        results[agent.name] = {
            "files": files,
            "status": "✅ STABLE" if all_good else "❌ FIXED"
        }

    with open(LOG_DIR / "agent_audit_log.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n✅ Agent audit and fix complete.")
    print(f"📄 Report saved to {LOG_DIR / 'agent_audit_log.json'}")
    print(f"📁 Backups in: {BACKUP_DIR}/")

if __name__ == '__main__':
    fix_agents()

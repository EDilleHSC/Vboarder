#!/usr/bin/env python3
import os
from datetime import datetime
import json
import argparse
from pathlib import Path

CORE_FILES = [
    "agent.json", "config.json", "memory.jsonl",
    "persona.md", "prompt.md", "schedule.json"
]

EXCLUDED_DIRS = {"tools", "templates", "logs", "backups", "agent_runtime"}

def is_valid_json(file_path):
    try:
        if file_path.suffix == ".jsonl":
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if not lines:
                    return False, "Empty file"
                for line in lines:
                    json.loads(line)
        else:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
        return True, "OK"
    except Exception as e:
        return False, str(e)

def is_valid_md(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return bool(f.read().strip()), "OK"
    except Exception as e:
        return False, str(e)

def scan_agents(base_dir: Path) -> dict:
    results = {}
    for agent in base_dir.iterdir():
        if not agent.is_dir() or agent.name.lower() in EXCLUDED_DIRS:
            continue

        agent_report = {"files": {}, "status": "✅ PASS"}

        for file in CORE_FILES:
            path = agent / file
            if not path.exists():
                agent_report["files"][file] = "❌ MISSING"
                agent_report["status"] = "❌ FAIL"
                continue

            if file.endswith(".json") or file.endswith(".jsonl"):
                valid, msg = is_valid_json(path)
            elif file.endswith(".md"):
                valid, msg = is_valid_md(path)
            else:
                valid, msg = True, "OK"

            agent_report["files"][file] = "✅ OK" if valid else f"❌ {msg}"
            if not valid:
                agent_report["status"] = "❌ FAIL"

        results[agent.name] = agent_report
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base",
        default="/mnt/d/ai/projects/vboarder/agents",
        help="Root agent directory"
    )
    args = parser.parse_args()

    base = Path(args.base)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_output = base / "tools" / "logs" / f"stability_log_{timestamp}.json"

    print("🔍 Scanning agents for stability...\n")
    results = scan_agents(base)

    log_output.parent.mkdir(parents=True, exist_ok=True)
    with open(log_output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"✅ Stability report saved to: {log_output}\n")
    print("📊 Stability Summary:")
    for agent, report in results.items():
        print(f" - {agent}: {report['status']}")

if __name__ == "__main__":
    main()

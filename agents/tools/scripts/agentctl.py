#!/usr/bin/env python3
"""
                    file_path.write_text("{}" if filename.endswith(".json") else "", encoding="utf-8")
                    agent_result["files"][filename] = "⚠️ FIXED"
                continue

            try:
                if filename.endswith(".json") or filename.endswith(".jsonl"):
                    with open(file_path, "r", encoding="utf-8") as f:
                        if filename.endswith(".jsonl"):
                            for line in f:
                                json.loads(line)
                        else:
                            json.load(f)
                else:
                    content = file_path.read_text(encoding="utf-8").strip()
                    if not content:
                        raise ValueError("Empty content")
                agent_result["files"][filename] = "✅ OK"
            except Exception as e:
                agent_result["files"][filename] = f"❌ {e}"
                agent_result["status"] = "❌ FAIL"
        results[agent_dir.name] = agent_result
    return results

def print_report(results):
    print("\n📊 Agent Validation Report:")
    for name, report in results.items():
        print(f" - {name}: {report['status']}")

def save_report(results, path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = path / f"agentctl_report_{timestamp}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n📝 Detailed report saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="AgentOps CLI Utility")
    subparsers = parser.add_subparsers(dest="command")

    validate = subparsers.add_parser("validate", help="Validate all agents")
    validate.add_argument("--base", type=str, default="./agents", help="Base agent directory")
    validate.add_argument("--fix", action="store_true", help="Attempt to auto-fix missing files")

    args = parser.parse_args()

    if args.command == "validate":
        base = Path(args.base).resolve()
        if not base.exists():
            print(f"❌ Base path not found: {base}")
            sys.exit(1)

        print(f"🔍 Validating agents in: {base}")
        results = validate_agents(base, auto_fix=args.fix)
        print_report(results)
        save_report(results, base)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
agentctl - AI AgentOps CLI Tool
"""
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

REQUIRED_FILES = [
    "agent.json",
    "config.json",
    "memory.jsonl",
    "persona.md",
    "prompt.md",
    "schedule.json",
]


def validate_agents(base_path: Path, auto_fix=False):
    results = {}
    for agent_dir in sorted(base_path.iterdir()):
        if not agent_dir.is_dir() or agent_dir.name.lower() in [
            "tools",
            "logs",
            "templates",
            "backups",
        ]:
            continue

        agent_result = {"status": "✅ PASS", "files": {}}
        for filename in REQUIRED_FILES:
            file_path = agent_dir / filename
            if not file_path.exists():
                agent_result["files"][filename] = "❌ MISSING"
                agent_result["status"] = "❌ FAIL"
                if auto_fix:
                    file_path.write_text(
                        "{}" if filename.endswith(".json") else "", encoding="utf-8"
                    )
                    agent_result["files"][filename] = "⚠️ FIXED"
                continue

            try:
                if filename.endswith(".json") or filename.endswith(".jsonl"):
                    with open(file_path, "r", encoding="utf-8") as f:
                        if filename.endswith(".jsonl"):
                            for line in f:
                                json.loads(line)
                        else:
                            json.load(f)
                else:
                    content = file_path.read_text(encoding="utf-8").strip()
                    if not content:
                        raise ValueError("Empty content")
                agent_result["files"][filename] = "✅ OK"
            except Exception as e:
                agent_result["files"][filename] = f"❌ {e}"
                agent_result["status"] = "❌ FAIL"
        results[agent_dir.name] = agent_result
    return results


def print_report(results):
    print("\n📊 Agent Validation Report:")
    for name, report in results.items():
        print(f" - {name}: {report['status']}")


def save_report(results, path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = path / f"agentctl_report_{timestamp}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n📝 Detailed report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="AgentOps CLI Utility")
    subparsers = parser.add_subparsers(dest="command")

    validate = subparsers.add_parser("validate", help="Validate all agents")
    validate.add_argument(
        "--base", type=str, default="./agents", help="Base agent directory"
    )
    validate.add_argument(
        "--fix", action="store_true", help="Attempt to auto-fix missing files"
    )

    args = parser.parse_args()

    if args.command == "validate":
        base = Path(args.base).resolve()
        if not base.exists():
            print(f"❌ Base path not found: {base}")
            sys.exit(1)

        print(f"🔍 Validating agents in: {base}")
        results = validate_agents(base, auto_fix=args.fix)
        print_report(results)
        save_report(results, base)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

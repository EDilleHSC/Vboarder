#!/usr/bin/env python3
"""
agentctl - AI AgentOps CLI Tool
"""
import argparse
import json
import os
from pathlib import Path

AGENT_CORE_FILES = [
    "agent.json",
    "config.json",
    "memory.jsonl",
    "persona.md",
    "prompt.md",
    "schedule.json",
]
EXCLUDED_DIRS = {"tools", "logs", "backups", "templates"}


# --- Validation Utilities ---
def validate_agent(agent_path: Path, fix: bool = False) -> dict:
    report = {"files": {}, "status": "✅ PASS"}
    for filename in AGENT_CORE_FILES:
        file_path = agent_path / filename
        if not file_path.exists():
            report["files"][filename] = "❌ MISSING"
            report["status"] = "❌ FAIL"
            if fix:
                file_path.write_text("{}" if filename.endswith(".json") else "\n")
            continue

        try:
            if filename.endswith(".json"):
                json.load(open(file_path))
            elif filename.endswith(".jsonl"):
                with open(file_path) as f:
                    for line in f:
                        json.loads(line)
            elif filename.endswith(".md"):
                content = file_path.read_text().strip()
                if not content:
                    raise ValueError("Empty markdown")
        except Exception as e:
            report["files"][filename] = f"❌ {str(e)}"
            report["status"] = "❌ FAIL"
            continue

        report["files"][filename] = "✅ OK"
    return report


# --- HTML Report Generator ---
def generate_html_report(report: dict, output_path: Path):
    html = ["<html><body><h1>Agent Validation Report</h1><ul>"]
    for agent, details in report.items():
        html.append(f"<li><strong>{agent}</strong>: {details['status']}<ul>")
        for f, status in details["files"].items():
            html.append(f"<li>{f}: {status}</li>")
        html.append("</ul></li>")
    html.append("</ul></body></html>")
    output_path.write_text("\n".join(html))


# --- Git Tag ---
def create_git_tag(version: str):
    os.system(f"git tag {version} && git push origin {version}")


# --- Bootstrap Agent ---
def bootstrap_agent(base: Path, name: str):
    target = base / name
    target.mkdir(parents=True, exist_ok=True)
    for f in AGENT_CORE_FILES:
        p = target / f
        p.write_text("{}" if f.endswith(".json") or f.endswith(".jsonl") else f"# {f}")
    print(f"✅ Bootstrapped agent at {target}")


# --- CLI Entry Point ---
def main():
    parser = argparse.ArgumentParser(description="AgentOps CLI")
    sub = parser.add_subparsers(dest="command")

    # validate
    v = sub.add_parser("validate")
    v.add_argument("--base", default="./", help="Agent root directory")
    v.add_argument("--fix", action="store_true", help="Auto-fix missing files")

    # report
    r = sub.add_parser("report")
    r.add_argument("--base", default="./", help="Agent root directory")
    r.add_argument("--out", default="./agent_report.html", help="HTML output file")

    # tag
    t = sub.add_parser("tag")
    t.add_argument("--version", required=True, help="Git version tag")

    # bootstrap
    b = sub.add_parser("bootstrap")
    b.add_argument("--name", required=True, help="Agent name")
    b.add_argument("--base", default="./", help="Where to create the agent")

    args = parser.parse_args()

    if args.command == "validate":
        base = Path(args.base)
        results = {}
        for agent_dir in base.iterdir():
            if agent_dir.is_dir() and agent_dir.name not in EXCLUDED_DIRS:
                results[agent_dir.name] = validate_agent(agent_dir, fix=args.fix)
        print(json.dumps(results, indent=2))

    elif args.command == "report":
        base = Path(args.base)
        results = {}
        for agent_dir in base.iterdir():
            if agent_dir.is_dir() and agent_dir.name not in EXCLUDED_DIRS:
                results[agent_dir.name] = validate_agent(agent_dir)
        generate_html_report(results, Path(args.out))
        print(f"✅ HTML report written to {args.out}")

    elif args.command == "tag":
        create_git_tag(args.version)

    elif args.command == "bootstrap":
        bootstrap_agent(Path(args.base), args.name)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

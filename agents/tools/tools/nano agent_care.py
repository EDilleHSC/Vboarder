# agent_care.py
# Unified Agent Maintenance CLI

import argparse
import subprocess
import sys
import os

# === Tool Path Map ===
TOOLS = {
    "patch": "patch_agents.py",
    "migrate": "migrate_agents.py",
    "upgrade": "create_or_upgrade_agent.py"
}

def run_tool(tool_name):
    tool_path = TOOLS.get(tool_name)
    if not tool_path or not os.path.exists(tool_path):
        print(f"[ERROR] Tool for '{tool_name}' not found.")
        sys.exit(1)

    print(f"[INFO] Running {tool_name}...")
    try:
        subprocess.run(["python3", tool_path], check=True)
        print(f"[SUCCESS] '{tool_name}' completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[FAIL] Error running '{tool_name}': {e}")
        sys.exit(1)

def list_tools():
    print("\nAvailable Agent Care Commands:")
    for cmd in TOOLS:
        print(f"  - {cmd}")
    print("\nUsage: python3 agent_care.py [COMMAND]\n")

def main():
    parser = argparse.ArgumentParser(description="Unified Agent Care CLI")
    parser.add_argument("command", help="One of: patch, migrate, upgrade, list")
    args = parser.parse_args()

    cmd = args.command.lower()
    if cmd == "list":
        list_tools()
    elif cmd in TOOLS:
        run_tool(cmd)
    else:
        print(f"[ERROR] Unknown command '{cmd}'. Use 'list' to see valid options.")
        sys.exit(1)

if __name__ == "__main__":
    main()

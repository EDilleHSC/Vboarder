#!/usr/bin/env python3
"""
ask.py - CLI tool to query a local agent
"""

import argparse
import json
from pathlib import Path
from datetime import datetime

# --- Configuration ---
AGENT_DIR_NAME = "."  # current directory
REQUIRED_FILES = ["agent.json", "prompt.md", "persona.md"]
OPTIONAL_FILES = ["config.json", "schedule.json"]
LOG_FILE = "memory.jsonl"

# --- Helper Functions ---
def load_text(path: Path) -> str:
    return path.read_text(encoding='utf-8-sig').strip()

def load_agent(agent_name: str) -> dict:
    agent_path = Path(AGENT_DIR_NAME) / agent_name
    if not agent_path.exists():
        raise FileNotFoundError(f"Agent folder not found: {agent_path}")
    
    files = {}
    for fname in REQUIRED_FILES + OPTIONAL_FILES:
        fpath = agent_path / fname
        if fpath.exists():
            files[fname] = load_text(fpath)
        elif fname in REQUIRED_FILES:
            raise FileNotFoundError(f"Missing required file: {fpath}")
    return {
        "name": agent_name,
        "path": agent_path,
        "files": files
    }

def log_interaction(agent_path: Path, query: str, response: str):
    log_path = agent_path / LOG_FILE
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "query": query,
        "response": response
    }
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

# --- Fake Response Generator ---
def simple_response(prompt: str, query: str) -> str:
    return f"Received your query: '{query}'. [Simulated response based on prompt...]"

# --- Main ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", required=True, help="Agent name (folder)")
    parser.add_argument("--query", required=True, help="Query to send to agent")
    args = parser.parse_args()

    try:
        agent = load_agent(args.agent)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        exit(1)

    print(f"\n🧠 [{args.agent}] Prompt:\n{agent['files']['prompt.md'][:300]}...\n")
    print(f"🗣️ You: {args.query}")

    response = simple_response(agent['files']['prompt.md'], args.query)
    print(f"🤖 {args.agent}: {response}\n")

    log_interaction(agent["path"], args.query, response)

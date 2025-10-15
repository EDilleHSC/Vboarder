# agent_runtime/loader.py
import json
from pathlib import Path

REQUIRED_FILES = ["agent.json", "config.json", "memory.jsonl", "persona.md", "prompt.md", "schedule.json"]

def load_agent(agent_path: Path) -> dict:
    agent_data = {"path": str(agent_path), "files": {}}

    for filename in REQUIRED_FILES:
        file_path = agent_path / filename
        if not file_path.exists():
            agent_data["files"][filename] = None
            continue

        if filename.endswith(".json") or filename.endswith(".jsonl"):
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    agent_data["files"][filename] = json.load(f)
                except json.JSONDecodeError:
                    agent_data["files"][filename] = f"[ERROR] Malformed JSON"
        elif filename.endswith(".md"):
            with open(file_path, 'r', encoding='utf-8') as f:
                agent_data["files"][filename] = f.read().strip()

    return agent_data


# agent_runtime/memory.py
def read_memory(memory_path: Path) -> list:
    if not memory_path.exists():
        return []
    with open(memory_path, 'r', encoding='utf-8') as f:
        return [json.loads(line) for line in f if line.strip()]

def append_to_memory(memory_path: Path, entry: dict):
    with open(memory_path, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + "\n")


# ask.py
import argparse
from pathlib import Path
from agent_runtime.loader import load_agent
from agent_runtime.memory import append_to_memory

parser = argparse.ArgumentParser(description="Talk to an AI Agent")
parser.add_argument('--agent', required=True, help='Agent name (e.g. CTO)')
parser.add_argument('--query', required=True, help='Your message to the agent')
args = parser.parse_args()

agent_path = Path("../") / args.agent
agent = load_agent(agent_path)

if agent['files']['prompt.md']:
    print(f"\n🧠 [{args.agent}] Prompt:\n{agent['files']['prompt.md'][:500]}\n...")

print(f"\n🗣️ You: {args.query}")

response = f"[Simulated Response from {args.agent}] I received: '{args.query}'"

append_to_memory(agent_path / "memory.jsonl", {"user": args.query, "agent": response})

print(f"🤖 {args.agent}: {response}\n")

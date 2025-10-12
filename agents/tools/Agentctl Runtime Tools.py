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
    print(f"\n\U0001f9e0 [{args.agent}] Prompt:\n{agent['files']['prompt.md'][:500]}\n...")

print(f"\n\U0001f5e3️ You: {args.query}")

response = f"[Simulated Response from {args.agent}] I received: '{args.query}'"

append_to_memory(agent_path / "memory.jsonl", {"user": args.query, "agent": response})

print(f"\U0001f916 {args.agent}: {response}\n")

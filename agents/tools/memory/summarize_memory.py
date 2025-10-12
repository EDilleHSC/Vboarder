#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime

def summarize_memory(agent_dir: Path):
    """Create a readable summary of an agent’s memory.jsonl"""
    mem_file = agent_dir / "memory.jsonl"
    summary_file = agent_dir / "memory_summary.md"

    if not mem_file.exists() or mem_file.stat().st_size == 0:
        return

    with mem_file.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    summary = [
        f"# Memory Summary — {agent_dir.name}",
        f"**Generated:** {datetime.now().isoformat()}",
        f"**Total entries:** {len(lines)}",
        "",
        "## Last 10 memory entries:",
    ]

    for line in lines[-10:]:
        snippet = line.strip().replace("\n", " ")
        summary.append(f"- {snippet[:120]}")

    summary_file.write_text("\n".join(summary), encoding="utf-8")
    print(f"🧠  {agent_dir.name}: summary written")

def main():
    base = Path(__file__).resolve().parents[1]
    for agent in base.iterdir():
        if agent.is_dir() and agent.name.isupper():
            summarize_memory(agent)
    print("\n✅  All memory summaries updated.")

if __name__ == "__main__":
    main()

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# === Agent Loader ===
def load_agent(agent_path: Path) -> dict:
    """Load agent configuration from config.json"""
    config_path = Path(agent_path) / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Missing agent config at {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


# === Console Output Helpers ===
def print_colored(text, color="white"):
    """Print colored text for better terminal visibility"""
    COLORS = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "white": "\033[0m",
    }
    print(f"{COLORS.get(color, COLORS['white'])}{text}{COLORS['white']}")


def print_verbose_block(title: str, content: str):
    """Format verbose output blocks"""
    border = "─" * 60
    print(f"\n┌─ {title}\n│ {border}\n{content}\n└{border}\n")


# === Memory Handling ===
def append_to_memory(agent_path: Path, question: str, answer: str):
    """Append a new Q/A pair to agent memory.json"""
    mem_path = Path(agent_path) / "memory.json"
    memory = []
    if mem_path.exists():
        with open(mem_path, "r", encoding="utf-8") as f:
            try:
                memory = json.load(f)
            except json.JSONDecodeError:
                memory = []
    memory.append({"q": question, "a": answer, "timestamp": datetime.now().isoformat()})
    with open(mem_path, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)


def load_memory(agent_path: Path, max_entries: int = None) -> List[Dict[str, str]]:
    """Load recent agent memory from memory.json"""
    mem_path = Path(agent_path) / "memory.json"
    if not mem_path.exists():
        return []
    with open(mem_path, "r", encoding="utf-8") as f:
        memory = json.load(f)
    if max_entries:
        memory = memory[-max_entries:]
    return memory


# === Prompt Composition (LEGACY FUNCTION REMOVED) ===
# The compose_prompt function has been removed as all prompt composition
# is now handled by the structured 'messages' array in ask.py.


# === Memory Maintenance ===
def summarize_memory_if_needed(agent_path: Path, interval: int = 10, verbose: bool = False):
    """Periodically summarize long-term memory (placeholder)"""
    mem_path = Path(agent_path) / "memory.json"
    if not mem_path.exists():
        return
    with open(mem_path, "r", encoding="utf-8") as f:
        memory = json.load(f)
    if len(memory) > interval:
        if verbose:
            print_colored(f"Summarizing memory (entries={len(memory)})", "yellow")
        # Placeholder summarization logic
        summarized = memory[-interval:]
        with open(mem_path, "w", encoding="utf-8") as f:
            json.dump(summarized, f, indent=2)
import json
import re
import time
from pathlib import Path

# Use relative path from project root
PROJECT_ROOT = Path(__file__).parent.parent
SHARED_FILE = PROJECT_ROOT / "data" / "shared" / "knowledge.json"

# WSL-safe memory path for individual agent memories
MEMORY_PATH = Path.home() / ".vboarder" / "memory"


class SharedMemory:
    """Shared memory system for cross-agent communication"""

    def __init__(self):
        # Ensure memory directory exists
        MEMORY_PATH.mkdir(parents=True, exist_ok=True)
        SHARED_FILE.parent.mkdir(parents=True, exist_ok=True)

    def load_memory(self, agent=None, quadrant=None):
        """Load memory for specific agent and quadrant"""
        if not agent:
            return load_shared()

        # Load agent-specific memory
        agent_memory_file = MEMORY_PATH / f"{agent.lower()}_memory.json"
        if not agent_memory_file.exists():
            return []

        try:
            data = json.loads(agent_memory_file.read_text(encoding="utf-8"))
            if quadrant and isinstance(data, dict):
                return data.get(quadrant, [])
            return data
        except Exception:
            return []

    def save_memory(self, agent, data, quadrant=None):
        """Save memory for specific agent and quadrant"""
        agent_memory_file = MEMORY_PATH / f"{agent.lower()}_memory.json"

        if quadrant:
            # Load existing data and update specific quadrant
            existing = {}
            if agent_memory_file.exists():
                try:
                    existing = json.loads(agent_memory_file.read_text(encoding="utf-8"))
                except Exception:
                    existing = {}
            existing[quadrant] = data
            data = existing

        agent_memory_file.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )


def load_memory(agent=None, quadrant=None):
    """Convenience function for loading memory"""
    sm = SharedMemory()
    return sm.load_memory(agent, quadrant)


def _read():
    if SHARED_FILE.exists():
        try:
            txt = SHARED_FILE.read_text(encoding="utf-8")
            if not txt.strip():
                return []
            data = json.loads(txt)
            if isinstance(data, dict) and "items" in data:
                return data["items"]
            if isinstance(data, list):
                return data
        except Exception:
            pass
    return []


def _write(items):
    SHARED_FILE.parent.mkdir(parents=True, exist_ok=True)
    SHARED_FILE.write_text(
        json.dumps({"items": items}, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def load_shared(max_items=30):
    items = _read()
    return items[-max_items:] if max_items else items


def append_fact(text, source_agent):
    items = _read()
    norm = text.strip().lower()
    if not any(i.get("text", "").strip().lower() == norm for i in items[-50:]):
        items.append(
            {
                "ts": time.time(),
                "source": source_agent,
                "type": "fact",
                "text": text.strip(),
            }
        )
        _write(items)


FACT_PATTERNS = [
    r"\b(project\s*codename|codename)\b.*\b(is|=)\b\s+.+",
    r"\bremember\b.+",
    r"\bdeadline\b.*\b(is|=)\b\s+.+",
    r"\bbudget\b.*\b(is|=)\b\s+.+",
    r"\b(stakeholder|owner|contact)\b.*\b(is|=)\b\s+.+",
]


def maybe_extract_fact(user_text: str):
    if not user_text:
        return None
    for pat in FACT_PATTERNS:
        if re.search(pat, user_text, flags=re.IGNORECASE):
            return user_text.strip()
    return None


def shared_block_text(max_items=20):
    facts = load_shared(max_items=max_items)
    bullets = [f"- {f['text']}" for f in facts if f.get("type") == "fact"]
    if not bullets:
        return ""
    return "Shared team knowledge available to all agents:\n" + "\n".join(bullets)

from pathlib import Path
import json, time, re

SHARED_FILE = Path(r"D:\ai\projects\vboarder\data\shared\knowledge.json")

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
    SHARED_FILE.write_text(json.dumps({"items": items}, ensure_ascii=False, indent=2), encoding="utf-8")

def load_shared(max_items=30):
    items = _read()
    return items[-max_items:] if max_items else items

def append_fact(text, source_agent):
    items = _read()
    norm = text.strip().lower()
    if not any(i.get("text", "").strip().lower() == norm for i in items[-50:]):
        items.append({"ts": time.time(), "source": source_agent, "type": "fact", "text": text.strip()})
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

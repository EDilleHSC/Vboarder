import os, json
from datetime import datetime

AGENT = os.environ.get("AGENT", "ceo").lower()
BASE_DIR = f"agents/{AGENT}"
MEMORY_PATH = f"{BASE_DIR}/memory.jsonl"
STATE_PATH = "data/shared_state.json"

def read_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    return {}

def append_to_memory(content):
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agent": AGENT,
        "message": content
    }
    with open(MEMORY_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

def run_sync():
    shared = read_state()
    cto_msg = shared.get("cto", {}).get("last_message", "No CTO update found.")
    summary = f"CEO received CTO update: \"{cto_msg}\""
    print("🧠 CEO Sync:", summary)
    append_to_memory(summary)

if __name__ == "__main__":
    run_sync()

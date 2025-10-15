import os
import json
from datetime import datetime

AGENT = os.environ.get("AGENT", "cto").lower()
BASE_DIR = f"agents/{AGENT}"
MEMORY_PATH = f"{BASE_DIR}/memory.jsonl"
STATE_PATH = "data/shared_state.json"


def post_update():
    update = f"{AGENT.upper()} system status update at {datetime.utcnow().isoformat()}Z"
    print(f"📡 {AGENT.upper()} posting update:", update)

    # 1. Write to shared state
    shared = {}
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, "r") as f:
            shared = json.load(f)

    shared[AGENT] = {
        "last_message": update,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    with open(STATE_PATH, "w") as f:
        json.dump(shared, f, indent=2)

    # 2. Log to agent memory
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agent": AGENT,
        "message": update,
    }

    with open(MEMORY_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


if __name__ == "__main__":
    post_update()

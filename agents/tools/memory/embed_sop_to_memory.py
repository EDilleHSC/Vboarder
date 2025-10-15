#!/usr/bin/env python3
import os
import json

SOP_FILE = "./docs/agent_sop.json"
MEMORY_DB = "./memory/agent_sop_memory.json"

os.makedirs("memory", exist_ok=True)


def embed_sop():
    print("🧬 Embedding SOPs into agent memory...")

    if not os.path.exists(SOP_FILE):
        print(f"❌ SOP file not found at: {SOP_FILE}")
        return

    with open(SOP_FILE, "r") as f:
        sop_data = json.load(f)

    with open(MEMORY_DB, "w") as f:
        json.dump(sop_data, f, indent=2)

    print(f"✅ SOPs embedded into memory at: {MEMORY_DB}")


if __name__ == "__main__":
    embed_sop()

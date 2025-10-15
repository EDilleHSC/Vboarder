#!/usr/bin/env python3

import json
import os
from pathlib import Path


def main():
    try:
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        registry_path = project_root / "agent_registry.json"

        if not os.path.exists(registry_path):
            print("❌ Agent registry not found")
            return

        with open(registry_path, encoding='utf-8') as f:
            registry = json.load(f)

        models = set()
        for _, config in registry.get("agents", {}).items():
            if "model" in config:
                models.add(config["model"])

        if models:
            primary_model = next(iter(models))
            print(f"✅ LLM Engine in Use: {primary_model}")
        else:
            print("❌ No LLM models found")

    except Exception as e:
        print(f"❌ Error: {e}")
if __name__ == "__main__":
    main()

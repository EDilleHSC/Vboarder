from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {path}: {e}")
        return None


def check_file(path):
    exists = path.exists()
    print(f"{'✅' if exists else '❌'} {path}")
    return exists


def run_agent_check():
    print("\n🔍 Running VBoarder Agent System Check...\n")

    registry_path = BASE_DIR / "agent_registry.json"
    if not check_file(registry_path):
        return

    registry = load_json(registry_path)
    agent_path = BASE_DIR / registry.get("path", "")
    config_path = agent_path.parent / "agent_config.json"

    check_file(agent_path)
    check_file(config_path)

    agent_data = load_json(agent_path)
    config_data = load_json(config_path)

    if not (agent_data and config_data):
        return

    prompt_path = BASE_DIR / agent_data.get("prompt_path", "")
    persona_path = BASE_DIR / agent_data.get("persona_path", "")

    check_file(prompt_path)
    check_file(persona_path)

    print("\n🎉 Check Complete.")


if __name__ == "__main__":
    run_agent_check()

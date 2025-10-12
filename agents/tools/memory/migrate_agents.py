# migrate_agents.py
import os
import json
import shutil

def migrate_agent(agent_path, remove_config=False):
    report = {"agent": os.path.basename(agent_path), "actions": []}
    
    agent_json_path = os.path.join(agent_path, "agent.json")
    config_json_path = os.path.join(agent_path, "agent_config.json")

    # Load agent.json
    if not os.path.exists(agent_json_path):
        report["actions"].append("❌ agent.json missing")
        return report

    with open(agent_json_path, "r", encoding="utf-8-sig") as f:
        agent_data = json.load(f)

    # Move + Rename prompt
    legacy_prompt = os.path.join(agent_path, "prompts", "system_detailed.txt")
    new_prompt = os.path.join(agent_path, "prompt.md")
    if os.path.exists(legacy_prompt):
        shutil.move(legacy_prompt, new_prompt)
        report["actions"].append(f"✅ Moved: {legacy_prompt} → {new_prompt}")
        agent_data["prompt_path"] = "prompt.md"

    # Move + Rename persona
    legacy_persona = os.path.join(agent_path, "personas", "gilfoyle.txt")
    new_persona = os.path.join(agent_path, "persona.md")
    if os.path.exists(legacy_persona):
        shutil.move(legacy_persona, new_persona)
        report["actions"].append(f"✅ Moved: {legacy_persona} → {new_persona}")
        agent_data["persona_path"] = "persona.md"

    # Save updated agent.json
    with open(agent_json_path, "w", encoding="utf-8") as f:
        json.dump(agent_data, f, indent=2)
        report["actions"].append("✅ agent.json updated")

    # Optionally remove agent_config.json
    if remove_config and os.path.exists(config_json_path):
        os.remove(config_json_path)
        report["actions"].append("🗑️ Removed agent_config.json")

    return report


def run_migration(agents_dir, remove_config=False):
    logs = []
    for role in os.listdir(agents_dir):
        path = os.path.join(agents_dir, role)
        if os.path.isdir(path):
            log = migrate_agent(path, remove_config=remove_config)
            logs.append(log)

    with open("migration_log.json", "w") as f:
        json.dump(logs, f, indent=2)
    print("🎉 Migration complete. Log saved to migration_log.json")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Migrate agent folder structure to standard layout.")
    parser.add_argument("--agents_dir", type=str, required=True, help="Path to agents folder")
    parser.add_argument("--remove-config", action="store_true", help="Remove agent_config.json if present")
    args = parser.parse_args()

    run_migration(args.agents_dir, remove_config=args.remove_config)

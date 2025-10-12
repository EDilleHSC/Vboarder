import json
from pathlib import Path

# --- Configuration ---
# Assuming the script is run from the project root or the agents directory parent
BASE_DIR = Path(__file__).resolve().parent
REGISTRY_PATH = BASE_DIR.joinpath("agent_registry.json")

# Default relative paths to be inserted if missing in agent.json
DEFAULT_PROMPT_PATH = "prompt.md"
DEFAULT_PERSONA_PATH = "persona.txt"

def load_json(path):
    """Safely loads a JSON file, handling UTF-8 BOM."""
    if not path.is_file():
        print(f"File not found: {path}")
        return None
    try:
        # Use 'utf-8-sig' to strip the Byte Order Mark (BOM)
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading or decoding {path}: {e}")
        return None

def save_json(path, data):
    """Safely saves data to a JSON file."""
    try:
        # Ensure 'utf-8-sig' is used for consistent output
        with open(path, "w", encoding="utf-8-sig") as f:
            # Use proper indentation for clean output
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"❌ Error saving {path}: {e}")
        return False

def patch_agent_files():
    """
    Patches all agent.json files to fix BOM issues and ensure
    required prompt_path and persona_path keys are present.
    """
    print("\n🔧 Running Agent File Patching Script...\n")

    # 1. Load the Agent Registry
    registry = load_json(REGISTRY_PATH)
    if not registry or not isinstance(registry, list):
        print(f"❌ Failed to load or validate registry at {REGISTRY_PATH}. Stopping.")
        return

    print(f"✅ Loaded registry with {len(registry)} agent entries.")

    # 2. Iterate and Patch Each Agent File
    for i, entry in enumerate(registry):
        role = entry.get("role", f"AGENT_{i+1}")
        rel_path = entry.get("path")

        if not rel_path:
            print(f"⚠️ [{role}] Skipping: Missing 'path' in registry entry.")
            continue
        
        # Determine the full path to the agent's main JSON file
        agent_file_path = BASE_DIR.joinpath(rel_path)
        
        print(f"\n---> Checking [{role}] at {agent_file_path}")
        
        # Load agent data using BOM-safe function
        agent_data = load_json(agent_file_path)

        if not agent_data:
            # Error already printed in load_json
            continue

        # --- Patching Logic ---
        needs_save = False

        # a) Check and insert prompt_path
        if "prompt_path" not in agent_data or not agent_data["prompt_path"]:
            agent_data["prompt_path"] = DEFAULT_PROMPT_PATH
            needs_save = True
            print(f"   [PATCHED] Added 'prompt_path': '{DEFAULT_PROMPT_PATH}'")

        # b) Check and insert persona_path
        if "persona_path" not in agent_data or not agent_data["persona_path"]:
            agent_data["persona_path"] = DEFAULT_PERSONA_PATH
            needs_save = True
            print(f"   [PATCHED] Added 'persona_path': '{DEFAULT_PERSONA_PATH}'")

        # 3. Save the Patched Data (also fixes indentation and encoding)
        if needs_save:
            if save_json(agent_file_path, agent_data):
                print(f"   [SUCCESS] File saved and clean.")
            else:
                print(f"   [FAILED] Could not save file.")
        else:
            # Re-save even if not patched to fix BOM/indentation, if necessary
            # For simplicity, we assume fixing the content is the priority
            # If you want to force save to fix BOM/indentation:
            # save_json(agent_file_path, agent_data)
            print(f"   [CLEAN] No patches applied. File structure appears correct.")

    print("\n🎉 Agent Patching Complete. Rerun your system check now.")

if __name__ == "__main__":
    patch_agent_files()
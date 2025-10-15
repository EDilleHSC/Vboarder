import shutil
from pathlib import Path
import json
from datetime import datetime

# === CONFIG ===
TEMPLATE_DIR = Path(
    "/mnt/d/ai/projects/vboarder/agents/tools/templates/super_agent_baseline"
)
AGENTS_DIR = Path("/mnt/d/ai/projects/vboarder/agents/super_agents")
MANIFEST_FILE = AGENTS_DIR / "super_manifest.json"


# === AGENT CREATOR ===
def create_super_agent(agent_name, role="Unassigned", priority=5, linked_agents=[]):
    target_dir = AGENTS_DIR / agent_name
    if target_dir.exists():
        print(f"❌ Super Agent '{agent_name}' already exists at {target_dir}")
        return

    shutil.copytree(TEMPLATE_DIR, target_dir)
    print(f"✅ Created Super Agent '{agent_name}' at {target_dir}")

    # Inject agent name into agent.json
    agent_json = target_dir / "agent.json"
    if agent_json.exists():
        data = json.loads(agent_json.read_text())
        data["agent_name"] = agent_name
        data["super"] = True
        agent_json.write_text(json.dumps(data, indent=2))
        print("🧠 Tagged agent as Super Agent in agent.json")

    # Update global Super Agent manifest
    manifest = {}
    if MANIFEST_FILE.exists():
        manifest = json.loads(MANIFEST_FILE.read_text())

    manifest[agent_name] = {
        "role": role,
        "status": "active",
        "priority": priority,
        "linked_agents": linked_agents,
        "created_at": datetime.utcnow().isoformat() + "Z",
    }

    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2))
    print(f"📝 Registered '{agent_name}' in Super Agent manifest.")


# === CLI ENTRY ===
if __name__ == "__main__":
    print("\n=== Super Agent Creation ===")
    agent_name = input("Agent Codename: ").strip()
    role = input("Primary Role: ").strip()
    priority = input("Priority (1=highest): ").strip()
    linked = input("Linked Agents (comma-separated): ").strip()

    if agent_name:
        linked_agents = [a.strip() for a in linked.split(",") if a.strip()]
        create_super_agent(
            agent_name=agent_name,
            role=role or "Unassigned",
            priority=int(priority) if priority.isdigit() else 5,
            linked_agents=linked_agents,
        )
    else:
        print("⚠️ Agent name is required.")

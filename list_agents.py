#!/usr/bin/env python3
"""
🧠 VBoarder Agent Autodiscovery
Dynamic agent and routing discovery tool for developers.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any


def load_agent_registry() -> list[dict[str, Any]]:
    """Load the agent registry from JSON file."""
    registry_path = Path("agent_registry.json")
    if not registry_path.exists():
        print("❌ agent_registry.json not found!")
        sys.exit(1)

    try:
        with open(registry_path) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing agent_registry.json: {e}")
        sys.exit(1)


def discover_agent_folders() -> list[str]:
    """Discover agent folders by scanning the agents directory."""
    agents_dir = Path("agents")
    if not agents_dir.exists():
        return []

    agent_folders = []
    for item in agents_dir.iterdir():
        if item.is_dir() and item.name not in ["__pycache__", "agent_runtime"]:
            agent_folders.append(item.name)

    return sorted(agent_folders)


def check_agent_health(agent_role: str) -> dict[str, bool]:
    """Check if agent has all required files and configuration."""
    agent_dir = Path(f"agents/{agent_role}")

    health = {
        "config_exists": (agent_dir / "config.json").exists(),
        "persona_exists": (agent_dir / "persona.json").exists(),
        "system_prompt_exists": (agent_dir / "personas" / "system_detailed.txt").exists(),
        "memory_exists": (agent_dir / "memory.jsonl").exists(),
        "agent_json_exists": (agent_dir / "agent.json").exists(),
    }

    return health


def get_model_slot_info() -> dict[str, str]:
    """Get current model slot configuration from environment and router."""
    return {
        "slot:a": os.getenv("MODEL_SLOT_A", "mistral:latest"),
        "slot:b": os.getenv("MODEL_SLOT_B", "mistral:latest"),
        "slot:c": os.getenv("MODEL_SLOT_C", "mistral:latest"),
    }


def print_agent_status():
    """Print comprehensive agent status report."""
    print("🧠 VBoarder Agent Autodiscovery Report")
    print("=" * 50)

    # Load registry
    try:
        registry_agents = load_agent_registry()
        registry_roles = {agent["role"]: agent for agent in registry_agents}
    except Exception:
        registry_roles = {}
        print("⚠️  Could not load agent registry")

    # Discover folders
    discovered_folders = discover_agent_folders()

    print(f"\n📋 Registry Agents: {len(registry_roles)}")
    print(f"📁 Discovered Folders: {len(discovered_folders)}")

    # Show model slot configuration
    print("\n🎯 Model Slot Configuration:")
    slots = get_model_slot_info()
    for slot, model in slots.items():
        print(f"   {slot}: {model}")

    print("\n🤖 Agent Status Overview:")
    print("-" * 50)

    all_agents = set(registry_roles.keys()) | set(discovered_folders)

    for agent in sorted(all_agents):
        status = "✅" if agent in registry_roles else "❌"
        enabled = "🟢" if agent in registry_roles and registry_roles[agent].get("enabled", False) else "🔴"
        folder = "📁" if agent in discovered_folders else "❌"

        print(f"{status} {enabled} {folder} {agent}")

        # Show health details for registered agents
        if agent in registry_roles and agent in discovered_folders:
            health = check_agent_health(agent)
            health_icons = []
            for check, passed in health.items():
                icon = "✅" if passed else "❌"
                health_icons.append(f"{icon}{check.split('_')[0]}")
            print(f"    Health: {' '.join(health_icons)}")

    print("\n📊 Summary:")
    enabled_count = sum(1 for agent in registry_roles.values() if agent.get("enabled", False))
    print(f"   📈 Enabled agents: {enabled_count}/{len(registry_roles)}")
    print(f"   📁 Agent folders: {len(discovered_folders)}")

    # Show missing or orphaned agents
    missing_folders = set(registry_roles.keys()) - set(discovered_folders)
    orphaned_folders = set(discovered_folders) - set(registry_roles.keys())

    if missing_folders:
        print(f"\n⚠️  Missing Folders: {', '.join(sorted(missing_folders))}")

    if orphaned_folders:
        print(f"\n⚠️  Orphaned Folders: {', '.join(sorted(orphaned_folders))}")


def print_routing_info():
    """Print routing configuration and test examples."""
    print("\n🧭 Routing Configuration:")
    print("-" * 30)

    # Import router if available
    try:
        sys.path.append(".")
        from router import route_task

        test_cases = [
            "Hello",
            "What is the current financial status of our Q4 goals?",
            "Search the web for latest AI research papers, analyze them, and provide a comprehensive summary with actionable insights for our strategic planning meeting next week.",
        ]

        print("📝 Test Routing Examples:")
        for i, task in enumerate(test_cases, 1):
            result = route_task(task)
            print(f'\n{i}. Task: "{task[:50]}{"..." if len(task) > 50 else ""}"')
            print(f"   → Slot: {result['slot']} ({result['model']})")
            print(f"   → Complexity: {result['complexity']}")
            print(f"   → Tools: {'Yes' if result['needs_tools'] else 'No'}")
            print(f"   → Length: {result['task_length']} chars")

    except ImportError:
        print("❌ Could not import router.py")


def main():
    """Main autodiscovery function."""
    if not Path("agent_registry.json").exists():
        print("❌ Please run from VBoarder root directory")
        sys.exit(1)

    print_agent_status()
    print_routing_info()

    print("\n🎯 Quick Commands:")
    print("   python list_agents.py          # Run this script")
    print('   ./quick_test.sh "test msg"     # Test reasoning')
    print("   ./vboarder_status.sh           # Full status")


if __name__ == "__main__":
    main()

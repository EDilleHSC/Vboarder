#!/usr/bin/env python3
"""
Fix agent_registry.json paths and format
- Removes UTF-8 BOM
- Converts backslashes to forward slashes
- Validates JSON structure
- Removes incomplete entries
"""
import json
from pathlib import Path


def fix_registry():
    """Fix registry file paths and format."""
    registry_path = Path("agent_registry.json")

    if not registry_path.exists():
        print("❌ agent_registry.json not found!")
        return False

    print("=" * 70)
    print("Agent Registry Path Fixer")
    print("=" * 70)
    print()

    # Read raw bytes first to check for BOM
    content_bytes = registry_path.read_bytes()

    # Remove BOM if present
    if content_bytes.startswith(b"\xef\xbb\xbf"):
        print("✅ Removing UTF-8 BOM...")
        content_bytes = content_bytes[3:]

    # Parse JSON
    try:
        registry_data = json.loads(content_bytes.decode("utf-8"))
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        return False

    # Handle both list and dict formats
    if isinstance(registry_data, dict) and "agents" in registry_data:
        agents = registry_data["agents"]
    elif isinstance(registry_data, list):
        agents = registry_data
    else:
        print(f"❌ Unexpected registry format: {type(registry_data)}")
        return False

    print(f"Found {len(agents)} agent entries")
    print()

    # Fix each agent entry
    fixed_agents = []
    issues_found = 0

    for idx, agent in enumerate(agents):
        print(f"Processing agent {idx + 1}...")

        # Check if agent has required 'role' field
        if "role" not in agent:
            print("  ⚠️  Missing 'role' field - skipping incomplete entry")
            issues_found += 1
            continue

        role = agent["role"]
        print(f"  Role: {role}")

        # Fix all path fields (convert backslashes to forward slashes)
        path_fields = ["system_prompt", "memory", "persona_file", "config_file"]
        for field in path_fields:
            if field in agent and isinstance(agent[field], str):
                old_path = agent[field]
                # Convert backslashes to forward slashes
                new_path = old_path.replace("\\\\", "/").replace("\\", "/")
                if old_path != new_path:
                    agent[field] = new_path
                    print(f"  ✅ Fixed {field}: {old_path} → {new_path}")
                    issues_found += 1

        fixed_agents.append(agent)
        print()

    # Write back clean registry
    print("=" * 70)
    print(f"Writing updated registry ({len(fixed_agents)} agents)...")

    # Write as UTF-8 without BOM
    with open(registry_path, "w", encoding="utf-8") as f:
        json.dump(fixed_agents, f, indent=2, ensure_ascii=False)

    print("✅ Registry updated!")
    print(f"   Fixed {issues_found} path issue(s)")
    print()

    # Validate the result
    print("Validating...")
    try:
        with open(registry_path, "r", encoding="utf-8") as f:
            validated = json.load(f)
        print(f"✅ Valid JSON with {len(validated)} agents")
    except Exception as e:
        print(f"❌ Validation failed: {e}")
        return False

    print()
    print("=" * 70)
    print("Next steps:")
    print("  1. Verify: cat agent_registry.json | jq")
    print("  2. Check agents: bash tools/ops/verify-agent-setup.sh")
    print("  3. Restart backend: pkill -f uvicorn && uvicorn api.main:app --reload")
    print("=" * 70)

    return True


if __name__ == "__main__":
    success = fix_registry()
    exit(0 if success else 1)

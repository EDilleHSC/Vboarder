#!/usr/bin/env python3
"""
Remove UTF-8 BOM from agent_registry.json
The BOM (byte order mark) causes JSON parsing errors.
"""
from pathlib import Path


def remove_bom(filepath: Path):
    """Remove UTF-8 BOM if present."""
    if not filepath.exists():
        print(f"❌ File not found: {filepath}")
        return False

    content_bytes = filepath.read_bytes()

    # Check for UTF-8 BOM (EF BB BF)
    if content_bytes.startswith(b"\xef\xbb\xbf"):
        # Remove first 3 bytes (the BOM)
        filepath.write_bytes(content_bytes[3:])
        print(f"✅ BOM removed from {filepath}")
        return True
    else:
        print(f"ℹ️  No BOM found in {filepath}")
        return False


if __name__ == "__main__":
    registry_path = Path("agent_registry.json")
    remove_bom(registry_path)

    # Verify it's valid JSON
    try:
        import json

        with open(registry_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(
            f"✅ Valid JSON: {len(data)} agents"
            if isinstance(data, list)
            else f"✅ Valid JSON: {len(data.get('agents', []))} agents"
        )
    except json.JSONDecodeError as e:
        print(f"❌ JSON validation failed: {e}")
    except Exception as e:
        print(f"⚠️  Could not validate: {e}")

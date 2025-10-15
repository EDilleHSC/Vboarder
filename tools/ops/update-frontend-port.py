#!/usr/bin/env python3
"""
Update all documentation references from port 3010 to port 3000
Run this after changing package.json to use port 3000
"""

import re
from pathlib import Path

# Files to update
FILES_TO_UPDATE = [
    "README.md",
    "README_NEW.md",
    "START_HERE.md",
    "QUICK_COMMANDS.md",
    "QUICK_START.md",
    "RELEASE_READY.md",
    "BETA_RELEASE_SUMMARY.md",
    "REPO_STRUCTURE_NEW.md",
    "docs/DEV_DASHBOARD.md",
    "docs/DEVDASH_QUICKSTART.md",
    "docs/BETA_TEST_PLAYBOOK.md",
    "DEVDASH_RELEASE_NOTES.md",
    ".github/pull_request_template.md",
]

ROOT = Path(__file__).resolve().parent.parent.parent


def update_file(filepath: Path):
    """Update port 3010 to 3000 in file"""
    if not filepath.exists():
        print(f"⏭️  Skipping {filepath.name} (not found)")
        return

    content = filepath.read_text(encoding="utf-8")
    original = content

    # Replace all variations of 3010 with 3000
    patterns = [
        (r"port 3010", "port 3000"),
        (r"Port: 3010", "Port: 3000"),
        (r"localhost:3010", "localhost:3000"),
        (r"127\.0\.0\.1:3010", "127.0.0.1:3000"),
        (r"-p 3010", "-p 3000"),
        (r"VB_FRONTEND_PORT=3010", "VB_FRONTEND_PORT=3000"),
        (r"default: 3010", "default: 3000"),
        (r"FE 3010", "FE 3000"),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    if content != original:
        filepath.write_text(content, encoding="utf-8")
        print(f"✅ Updated {filepath.name}")
        return True
    else:
        print(f"⏭️  No changes needed in {filepath.name}")
        return False


def main():
    print("═══════════════════════════════════════════════════════════════")
    print("  Updating Documentation: Port 3010 → 3000")
    print("═══════════════════════════════════════════════════════════════")
    print()

    updated = 0
    for file_path in FILES_TO_UPDATE:
        full_path = ROOT / file_path
        if update_file(full_path):
            updated += 1

    print()
    print("═══════════════════════════════════════════════════════════════")
    print(f"  Updated {updated} file(s)")
    print("═══════════════════════════════════════════════════════════════")
    print()
    print("✅ Frontend now uses port 3000")
    print("   Next: Restart frontend from devdash or run:")
    print("   cd vboarder_frontend/nextjs_space && npm run dev")


if __name__ == "__main__":
    main()

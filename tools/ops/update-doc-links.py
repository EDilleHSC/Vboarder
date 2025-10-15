#!/usr/bin/env python3
"""
Doc Link Updater - Safe reference patcher for VBoarder repository
Automatically updates documentation links across the codebase to point to new paths.
"""
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Define the mapping of old paths to new paths
DOC_LINK_MAP = {
    # Root docs moving to docs/
    "FULL_STACK_LAUNCH_GUIDE.md": "docs/full-stack-launch-guide.md",
    "BACKEND_QUICK_START.md": "docs/backend-quick-start.md",
    "DEVDASH_QUICKSTART.md": "docs/devdash-quickstart.md",
    "RELEASE_CHECKLIST_BETA1.md": "docs/release-checklist-beta1.md",
    "CHANGELOG.md": "docs/changelog.md",
    "DEPLOYMENT_CHECKLIST.md": "docs/deployment-checklist.md",
    "DEPLOYMENT_AUDIT_REPORT.md": "docs/deployment-audit-report.md",
    "DEPLOYMENT_VERIFICATION_REPORT.md": "docs/deployment-verification-report.md",
    # Tools reorganization
    "devdash.py": "tools/dev/devdash.py",
    "verify_agents_endpoint.py": "tools/ops/verify-agents-endpoint.py",
    "generate_shift_report.py": "tools/ops/generate-shift-report.py",
    "scripts/run_repo_cleanup.sh": "tools/cleanup/run_repo_cleanup.sh",
    "scripts/run_repo_cleanup.ps1": "tools/cleanup/run_repo_cleanup.ps1",
}


def get_repo_root() -> Path:
    """Get the repository root directory."""
    return Path(__file__).parent.parent.parent


def find_files_to_update(root: Path, extensions: List[str]) -> List[Path]:
    """Find all files that might contain doc references."""
    files = []
    ignore_dirs = {
        ".venv-wsl",
        "venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".next",
        "dist",
        ".git",
    }

    for ext in extensions:
        for filepath in root.rglob(f"*{ext}"):
            # Skip ignored directories
            if any(ignored in filepath.parts for ignored in ignore_dirs):
                continue
            files.append(filepath)

    return files


def update_links_in_file(
    filepath: Path, link_map: Dict[str, str]
) -> Tuple[int, List[str]]:
    """
    Update doc links in a single file.
    Returns (number_of_changes, list_of_changes)
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except (UnicodeDecodeError, PermissionError):
        return 0, []

    original_content = content
    changes = []

    for old_path, new_path in link_map.items():
        # Pattern 1: Markdown links [text](old_path)
        pattern1 = re.compile(rf"\[([^\]]+)\]\({re.escape(old_path)}\)", re.IGNORECASE)
        if pattern1.search(content):
            content = pattern1.sub(rf"[\1]({new_path})", content)
            changes.append(
                f"  [{filepath.name}] Markdown link: {old_path} → {new_path}"
            )

        # Pattern 2: Direct mentions in backticks `old_path`
        pattern2 = re.compile(rf"`{re.escape(old_path)}`", re.IGNORECASE)
        if pattern2.search(content):
            content = pattern2.sub(f"`{new_path}`", content)
            changes.append(f"  [{filepath.name}] Backtick ref: {old_path} → {new_path}")

        # Pattern 3: Import or path strings (Python/JS)
        # Be conservative - only update if it's clearly a path reference
        pattern3 = re.compile(rf'["\']\.?/?{re.escape(old_path)}["\']', re.IGNORECASE)
        if pattern3.search(content):
            content = pattern3.sub(f'"{new_path}"', content)
            changes.append(f"  [{filepath.name}] String path: {old_path} → {new_path}")

    # Only write if changes were made
    if content != original_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return len(changes), changes

    return 0, []


def main():
    """Run the doc link updater."""
    root = get_repo_root()

    print("=" * 70)
    print("VBoarder Doc Link Updater")
    print("=" * 70)
    print(f"Root: {root}\n")

    # Find files to update (Markdown, Python, JS/TS, JSON)
    extensions = [".md", ".py", ".js", ".ts", ".tsx", ".json"]
    print(f"Searching for files with extensions: {', '.join(extensions)}")

    files_to_check = find_files_to_update(root, extensions)
    print(f"Found {len(files_to_check)} files to check\n")

    # Update links
    total_changes = 0
    all_changes = []

    print("Updating links...")
    print("-" * 70)

    for filepath in files_to_check:
        num_changes, changes = update_links_in_file(filepath, DOC_LINK_MAP)
        if num_changes > 0:
            total_changes += num_changes
            all_changes.extend(changes)

    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if total_changes > 0:
        print(
            f"✅ Updated {total_changes} references across {len(files_to_check)} files\n"
        )
        print("Changes made:")
        for change in all_changes:
            print(change)
    else:
        print("ℹ️  No changes needed - all links already up to date!")

    print("\n" + "=" * 70)
    print("Next steps:")
    print("  1. Review changes with: git diff")
    print("  2. Test links in documentation")
    print("  3. Run tests: pytest -q")
    print("=" * 70)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
VBoarder Repository Inventory Generator
Scans the repo and generates a structured report of files and directories.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List


def get_repo_root() -> Path:
    """Get the repository root directory."""
    return Path(__file__).parent.parent.parent


def get_file_info(filepath: Path) -> Dict:
    """Get file metadata."""
    stat = filepath.stat()
    return {
        "path": str(filepath.relative_to(get_repo_root())),
        "size_bytes": stat.st_size,
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
    }


def scan_directory(base_path: Path, ignore_dirs: set) -> Dict[str, List[Dict]]:
    """Recursively scan directory and categorize files."""
    inventory = {
        "python_files": [],
        "typescript_files": [],
        "config_files": [],
        "docs": [],
        "scripts": [],
        "other": [],
    }

    for root, dirs, files in os.walk(base_path):
        # Filter out ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        root_path = Path(root)
        for file in files:
            filepath = root_path / file
            try:
                info = get_file_info(filepath)

                # Categorize by extension
                if filepath.suffix == ".py":
                    inventory["python_files"].append(info)
                elif filepath.suffix in [".ts", ".tsx", ".js", ".jsx"]:
                    inventory["typescript_files"].append(info)
                elif filepath.suffix in [".json", ".yaml", ".yml", ".toml", ".ini"]:
                    inventory["config_files"].append(info)
                elif filepath.suffix == ".md":
                    inventory["docs"].append(info)
                elif filepath.suffix in [".sh", ".ps1", ".bat"]:
                    inventory["scripts"].append(info)
                else:
                    inventory["other"].append(info)
            except (OSError, PermissionError):
                continue

    return inventory


def generate_report():
    """Generate and print inventory report."""
    root = get_repo_root()

    # Directories to ignore
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
        "logs",
        "vboarder_reports",
    }

    print("🔍 Scanning VBoarder repository...")
    print(f"📁 Root: {root}\n")

    inventory = scan_directory(root, ignore_dirs)

    # Calculate totals
    total_files = sum(len(files) for files in inventory.values())
    total_size = sum(f["size_bytes"] for files in inventory.values() for f in files)

    # Print summary
    print("=" * 60)
    print("INVENTORY SUMMARY")
    print("=" * 60)
    print(f"Total files scanned: {total_files}")
    print(f"Total size: {total_size / 1024 / 1024:.2f} MB\n")

    for category, files in inventory.items():
        if files:
            category_size = sum(f["size_bytes"] for f in files)
            print(
                f"{category.replace('_', ' ').title()}: {len(files)} files "
                f"({category_size / 1024:.2f} KB)"
            )

    # Save detailed report
    report_path = root / "vboarder_reports" / "inventory.json"
    report_path.parent.mkdir(exist_ok=True)

    with open(report_path, "w") as f:
        json.dump(
            {
                "generated": datetime.now().isoformat(),
                "total_files": total_files,
                "total_size_mb": total_size / 1024 / 1024,
                "inventory": inventory,
            },
            f,
            indent=2,
        )

    print(f"\n✅ Detailed report saved to: {report_path.relative_to(root)}")


if __name__ == "__main__":
    generate_report()

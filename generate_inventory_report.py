#!/usr/bin/env python3
# generate_inventory_report.py
# VBoarder Deep System Inventory

import json
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPORT = []


def log(section, status, notes=""):
    """Add an entry to the inventory report."""
    REPORT.append({"section": section, "status": status, "notes": notes})


def run(cmd):
    """Run a shell command and return output."""
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except Exception as e:
        return f"ERROR: {e}"


def check_file_exists(path, name=""):
    """Check if a file exists and log the result."""
    p = Path(path)
    exists = p.exists()
    display_name = name or path
    log(f"File: {display_name}", "✅ Found" if exists else "❌ Missing")
    return exists


# ----------------------------
# SYSTEM INFO
# ----------------------------
log("System Platform", platform.system())
log("Platform Version", platform.version())
log("Architecture", platform.machine())
log("Hostname", platform.node())
log("Report Generated", datetime.now().isoformat())

# ----------------------------
# PYTHON ENV
# ----------------------------
log("Python Version", sys.version.split()[0])
log("Python Path", sys.executable)

# Check multiple python installs (Windows)
if platform.system() == "Windows":
    where_python = run("where python")
    log("All Python Binaries (Windows PATH)", "\n" + where_python)
else:
    which_python = run("which -a python python3")
    log("All Python Binaries (Unix PATH)", "\n" + which_python)

# Pip freeze
pip_packages = run("pip freeze")
if pip_packages and not pip_packages.startswith("ERROR"):
    package_count = len(pip_packages.split("\n"))
    log(
        "Installed pip packages",
        f"{package_count} packages",
        pip_packages[:500] + ("..." if len(pip_packages) > 500 else ""),
    )
else:
    log("Installed pip packages", "❌ Error", pip_packages)

# Virtual Environment Check
venv_paths = [".venv", ".venv-wsl", "venv"]
for venv in venv_paths:
    if Path(venv).exists():
        log(f"Virtual Environment: {venv}", "✅ Found")
    else:
        log(f"Virtual Environment: {venv}", "⚠️  Not Found")

# Conda info (if available)
conda_info = run("conda info --json")
if not conda_info.startswith("ERROR"):
    try:
        info = json.loads(conda_info)
        log("Conda Active Env", info.get("active_prefix_name", "N/A"))
        log("Conda Envs", ", ".join(info.get("envs_dirs", [])))
    except:
        log("Conda Status", "⚠️  Could not parse conda info")
else:
    log("Conda Status", "⚠️  Not installed or not in PATH")

    # Conda env list
    envs = run("conda env list")
    if not envs.startswith("ERROR"):
        log("Conda Env List", "\n" + envs)

# ----------------------------
# FILE SYSTEM: AGENTS
# ----------------------------
agents_path = Path("agents")
if not agents_path.exists():
    log("Agents Folder", "❌ Missing", "Critical: agents/ directory not found")
else:
    log("Agents Folder", "✅ Found")

    expected_agents = ["CEO", "CTO", "CFO", "COO", "CMO", "CLO", "COS", "SEC", "AIR"]
    for agent_name in expected_agents:
        agent = agents_path / agent_name
        if not agent.exists():
            log(f"Agent {agent_name}", "❌ Missing", "Agent directory not found")
            continue

        # Check for key files
        files_to_check = {
            "config.json": "required",
            "README.md": "recommended",
            "agent_logic.py": "recommended",
            "prompts/system_detailed.txt": "recommended",
            "personas": "recommended (directory)",
        }

        missing = []
        found = []
        for file_path, importance in files_to_check.items():
            if "/" in file_path or file_path == "personas":
                # Handle nested paths and directories
                full_path = agent / file_path
                if full_path.exists():
                    found.append(file_path)
                else:
                    missing.append(f"{file_path} ({importance})")
            else:
                full_path = agent / file_path
                if full_path.exists():
                    found.append(file_path)
                else:
                    missing.append(f"{file_path} ({importance})")

        if missing:
            log(
                f"Agent {agent_name}", "⚠️  Incomplete", f"Missing: {', '.join(missing)}"
            )
        else:
            log(f"Agent {agent_name}", "✅ Complete", f"Found: {', '.join(found)}")

# ----------------------------
# CORE FILES CHECK
# ----------------------------
core_files = {
    "api/main.py": "Backend API entry point",
    "api/simple_connector.py": "Agent connector",
    "api/shared_memory.py": "Shared memory module",
    "server.py": "Server module",
    "agent_registry.json": "Agent registry",
    "requirements.txt": "Python dependencies",
    "README.md": "Project README",
}

for file_path, description in core_files.items():
    exists = Path(file_path).exists()
    log(f"Core File: {file_path}", "✅ Found" if exists else "❌ Missing", description)

# ----------------------------
# SCRIPTS CHECK
# ----------------------------
scripts = [
    "start_vboarder.sh",
    "stop_vboarder.sh",
    "start_vboarder.ps1",
    "stop_vboarder.ps1",
    "check_integrity.sh",
    "check_integrity.ps1",
]
for script in scripts:
    exists = Path(script).exists()
    log(f"Script: {script}", "✅ Found" if exists else "❌ Missing")

# ----------------------------
# DOCUMENTATION CHECK
# ----------------------------
docs = [
    ".github/copilot-instructions.md",
    "STARTUP_GUIDE.md",
    "TOOLS_SUMMARY.md",
]
for doc in docs:
    exists = Path(doc).exists()
    log(f"Documentation: {doc}", "✅ Found" if exists else "⚠️  Missing")


# ----------------------------
# SYMLINK + PERMISSION CHECKS
# ----------------------------
def check_links(path):
    """Find broken symlinks."""
    broken = []
    try:
        for p in Path(path).rglob("*"):
            try:
                if p.is_symlink() and not p.exists():
                    broken.append(str(p))
            except (PermissionError, OSError):
                continue
    except Exception as e:
        return [f"Error scanning: {e}"]
    return broken


broken_links = check_links(".")
if broken_links:
    log(
        "Broken Symlinks",
        f"❌ Found {len(broken_links)}",
        "\n".join(broken_links[:10]) + ("..." if len(broken_links) > 10 else ""),
    )
else:
    log("Broken Symlinks", "✅ None found")

# ----------------------------
# LOG FILES
# ----------------------------
logs_path = Path("logs")
if not logs_path.exists():
    log("Logs Directory", "⚠️  Missing", "Will be created on first run")
else:
    log("Logs Directory", "✅ Found")

    log_files = ["backend.log", "frontend.log"]
    for lf in log_files:
        log_file_path = logs_path / lf
        if log_file_path.exists():
            size = log_file_path.stat().st_size / 1024  # KB
            log(f"Log: {lf}", "✅ Exists", f"Size: {size:.2f} KB")
        else:
            log(f"Log: {lf}", "⚠️  Not yet created")

# ----------------------------
# GIT REPOSITORY CHECK
# ----------------------------
if Path(".git").exists():
    log("Git Repository", "✅ Initialized")

    # Git status
    git_status = run("git status --porcelain")
    if git_status:
        file_count = len(git_status.split("\n"))
        log("Git Status", f"⚠️  {file_count} uncommitted changes")
    else:
        log("Git Status", "✅ Clean working directory")

    # Git branch
    branch = run("git branch --show-current")
    log("Git Branch", branch if branch else "❌ Unable to determine")

    # Git tags
    tags = run("git tag")
    if tags:
        tag_list = tags.split("\n")
        log(
            "Git Tags",
            f"✅ {len(tag_list)} tags",
            ", ".join(tag_list[-5:]) if tag_list else "",
        )
    else:
        log("Git Tags", "⚠️  No tags found")
else:
    log("Git Repository", "❌ Not initialized")

# ----------------------------
# DEPENDENCIES CHECK
# ----------------------------
if Path("requirements.txt").exists():
    with open("requirements.txt", "r") as f:
        reqs = f.readlines()
        req_count = len([r for r in reqs if r.strip() and not r.startswith("#")])
        log("Requirements File", f"✅ {req_count} dependencies listed")

# Check for common dependencies
important_packages = ["fastapi", "uvicorn", "ollama", "pydantic", "httpx"]
for pkg in important_packages:
    check = run(f"pip show {pkg}")
    if not check.startswith("ERROR"):
        version_line = [l for l in check.split("\n") if l.startswith("Version:")]
        version = version_line[0].split(": ")[1] if version_line else "unknown"
        log(f"Package: {pkg}", "✅ Installed", f"Version: {version}")
    else:
        log(f"Package: {pkg}", "❌ Not installed")

# ----------------------------
# OLLAMA CHECK
# ----------------------------
ollama_check = run("ollama --version")
if not ollama_check.startswith("ERROR"):
    log("Ollama", "✅ Installed", ollama_check)

    # Check for models
    models = run("ollama list")
    if not models.startswith("ERROR"):
        model_lines = models.split("\n")[1:]  # Skip header
        model_count = len([m for m in model_lines if m.strip()])
        log(
            "Ollama Models",
            f"✅ {model_count} models available",
            "\n".join(model_lines[:5]),
        )
else:
    log("Ollama", "❌ Not installed or not in PATH")

# ----------------------------
# EXPORT REPORT
# ----------------------------
report_file = Path("vboarder_inventory.md")
with open(report_file, "w", encoding="utf-8") as f:
    f.write("# VBoarder System Inventory Report\n\n")
    f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"**Platform:** {platform.system()} {platform.release()}\n")
    f.write(f"**Python:** {sys.version.split()[0]}\n\n")
    f.write("---\n\n")

    # Count status types
    passed = len([r for r in REPORT if "✅" in r["status"]])
    warnings = len([r for r in REPORT if "⚠️" in r["status"]])
    failed = len([r for r in REPORT if "❌" in r["status"]])

    f.write("## Summary\n\n")
    f.write(f"- ✅ **Passed:** {passed}\n")
    f.write(f"- ⚠️  **Warnings:** {warnings}\n")
    f.write(f"- ❌ **Failed:** {failed}\n")
    f.write(f"- **Total Checks:** {len(REPORT)}\n\n")
    f.write("---\n\n")

    for item in REPORT:
        f.write(f"## {item['section']}\n\n")
        f.write(f"**Status:** {item['status']}\n\n")
        if item["notes"]:
            f.write(f"**Notes:**\n```\n{item['notes']}\n```\n\n")
        f.write("---\n\n")

print(f"\n✅ Inventory complete. Report saved to {report_file}")
print(f"\n📊 Summary: {passed} passed, {warnings} warnings, {failed} failed")
print(f"\nView the full report: {report_file.absolute()}\n")

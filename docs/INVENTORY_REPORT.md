# VBoarder Inventory Report Generator

## Overview

`generate_inventory_report.py` performs a comprehensive deep scan of your VBoarder installation, checking all critical components, dependencies, and configurations.

## Usage

```bash
# From project root
python generate_inventory_report.py
```

Or on Unix/Linux:

```bash
chmod +x generate_inventory_report.py
./generate_inventory_report.py
```

## What Gets Checked

### System Information

- Operating system and platform
- Python version and path
- All Python installations in PATH
- Virtual environment status

### Python Environment

- Installed pip packages (with count)
- Conda environment status (if applicable)
- Virtual environment directories (.venv, .venv-wsl)
- Required dependencies (FastAPI, uvicorn, ollama, etc.)

### Agent Configuration

- All 9 agent directories (CEO, CTO, CFO, COO, CMO, CLO, COS, SEC, AIR)
- Agent config files (`config.json`, `README.md`)
- Agent logic files (`agent_logic.py`)
- Prompt files (`prompts/system_detailed.txt`)
- Persona directories

### Core Files

- API modules (`api/main.py`, `api/simple_connector.py`, etc.)
- Server configuration
- Agent registry
- Requirements file
- Documentation

### Scripts & Tools

- Startup scripts (`.sh` and `.ps1` versions)
- Shutdown scripts
- Integrity check scripts
- Documentation files

### Infrastructure

- Broken symlinks detection
- Log files and sizes
- Git repository status
- Uncommitted changes
- Git tags and branches

### External Dependencies

- Ollama installation and version
- Available Ollama models
- Package versions for critical dependencies

## Output

The script generates a Markdown report: `vboarder_inventory.md`

### Report Sections

Each section includes:

- **Status**: ✅ Found / ⚠️ Warning / ❌ Missing
- **Notes**: Additional details, file sizes, version numbers, etc.

### Summary Statistics

The report includes counts of:

- ✅ Passed checks
- ⚠️ Warnings
- ❌ Failed checks
- Total checks performed

## Example Output

```text
✅ Inventory complete. Report saved to vboarder_inventory.md

📊 Summary: 85 passed, 12 warnings, 3 failed

View the full report: D:\ai\projects\vboarder\vboarder_inventory.md
```

## Use Cases

### Before Deployment

Run the inventory to ensure all components are in place:

```bash
python generate_inventory_report.py
```

### Troubleshooting

When something isn't working, the inventory report helps identify:

- Missing dependencies
- Incomplete agent configurations
- Broken symlinks
- Missing log files

### System Audit

Periodic audits to ensure system integrity:

```bash
# Run weekly or after major changes
python generate_inventory_report.py
git add vboarder_inventory.md
git commit -m "System inventory $(date +%Y-%m-%d)"
```

### Integration with CI/CD

Add to your pre-deployment checklist:

```yaml
# .github/workflows/deploy.yml
- name: System Inventory Check
  run: python generate_inventory_report.py
```

## Interpreting Results

### ✅ Green (Passed)

Everything is configured correctly. No action needed.

### ⚠️ Yellow (Warning)

Component is optional or will be created automatically.

- Missing log files (created on first run)
- Recommended but not required files

### ❌ Red (Failed)

Critical component is missing. Requires immediate attention.

- Missing agent directories
- Missing core API files
- Missing required dependencies

## Comparison with Integrity Check

| Feature  | Integrity Check          | Inventory Report          |
| -------- | ------------------------ | ------------------------- |
| Purpose  | Pre-flight validation    | Deep system audit         |
| Speed    | Fast (~5 seconds)        | Moderate (~10-15 seconds) |
| Output   | Console only             | Markdown report file      |
| Checks   | ~50 checks               | ~100+ checks              |
| Detail   | Basic status             | Comprehensive notes       |
| Use When | Before starting services | Troubleshooting, audits   |

## Best Practices

1. **Run before deployment**: Catch issues early
2. **Include in version control**: Track system changes over time
3. **Review warnings**: Some may indicate future problems
4. **Update regularly**: After adding new agents or dependencies

## Sample Report Structure

```markdown
# VBoarder System Inventory Report

**Generated:** 2025-10-14 13:45:32
**Platform:** Windows 10
**Python:** 3.11.5

---

## Summary

- ✅ **Passed:** 85
- ⚠️ **Warnings:** 12
- ❌ **Failed:** 3
- **Total Checks:** 100

---

## Agent CEO

**Status:** ✅ Complete

**Notes:**
Found: config.json, README.md, agent_logic.py, prompts/system_detailed.txt, personas

---
```

## Requirements

- Python 3.7+
- Access to system commands (`pip`, `git`, `ollama`, etc.)
- Read permissions on project directories

## Troubleshooting Issues

**Script fails with permission errors:**

- Ensure you have read access to all project directories
- Run from project root directory

**Conda info fails:**

- Normal if Conda is not installed
- Will be marked as warning, not error

**Git commands fail:**

- Ensure Git is installed and in PATH
- Or initialize Git repository: `git init`

---

**Last Updated:** October 14, 2025

# 🧰 vBoarder Agent Tools README

## 📁 Location
/mnt/d/ai/projects/vboarder/agents/tools

This directory contains all essential agent engineering tools for managing, patching, migrating, and upgrading the vBoarder Core Agent Suite (and future Super Agents).

---

## 🗼 agent_care.py — Primary Entry Script

Run all major functions via this single interface:

`ash
python3 agent_care.py [COMMAND]
`

### ✅ Available Commands:

| Command   | Description                                  |
|-----------|----------------------------------------------|
| patch   | Patches agent files using patch_agents.py  |
| migrate | Runs migrate_agents.py                     |
| upgrade | Upgrades agent files from SEC using create_or_upgrade_agent.py |
| list    | Prints help menu                             |
| --all   | 🆕 Runs all 3 steps in sequence (patch → migrate → upgrade) |

---

## 🧪 Stability / Schema Check
Use patch_agents.py or custom alidate_agent.py (planned) to:
- Confirm schema
- Check memory JSON
- Validate logs

---

## 🖩 Included Tools

| Tool                    | Purpose                                 |
|-------------------------|-----------------------------------------|
| patch_agents.py       | Normalize and sync file structures      |
| migrate_agents.py     | Assist with memory and task transitions |
| create_or_upgrade_agent.py | Build/Upgrade agents from SEC baseline |
| Create Agent Template.py   | Template generator for new agents     |
| move_agent_tools.py   | Utility to rearrange scripts (one-time) |
| 	ools_consolidation_report.md | Final audit of tool suite       |
| gent_registry.json   | (Optional) Track agent states/configs   |

---

## 📦 Backups / Logs

| File                 | Description                |
|----------------------|----------------------------|
| migration_log.json | Log of migrations          |
| upgrade_log.json   | Log of upgrade actions     |

---

## ✅ Agent Creation Template
Use Create Agent Template.py to spin up new agents quickly with SEC-aligned structure.

`ash
python3 "Create Agent Template.py" --name SUPERAGENT01
`

---

## 🧹 Cleanup (PowerShell)
This script writes the README and removes deprecated files:

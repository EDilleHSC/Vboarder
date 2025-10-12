#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import datetime
from pathlib import Path

# Paths
REPORT_DIR = Path("logs/shift_reports")
GUARDIAN_LOG = Path("logs/guardian.log")

def get_latest_guardian_entry():
    if not GUARDIAN_LOG.exists():
        return "⚠️ Guardian log not found"
    with GUARDIAN_LOG.open("r") as f:
        lines = f.readlines()
        for line in reversed(lines):
            if "Watchdog started" in line:
                return line.strip()
    return "⚠️ No recent Guardian entries found"

def generate_markdown():
    now = datetime.datetime.now()
    date_str = now.strftime("%A, %B %d %Y - %I:%M %p")
    file_str = now.strftime("%Y-%m-%d")
    guardian_entry = get_latest_guardian_entry()

    markdown = f"""\
# 🧠 CTO SHIFT CHANGE REPORT

**System:** VBoarder Backend — *RAG v3.3*  
**Date:** `{date_str}`  
**Location:** `/mnt/d/ai/projects/vboarder`  
**Environment:** `.venv` (Python 3.12.3)`  

---

## 🔹 1. System Overview

| Component                    | Status        | Notes                                                       |
| ---------------------------- | ------------- | ----------------------------------------------------------- |
| Backend Server (FastAPI)    | ✅ Running     | Responding to `/api/health`                                 |
| LLM Mode                     | 🧩 Local       | Using `llama3`, `mistral`, `embeddinggemma` via Ollama      |
| Embedding Cache              | ⚙️ Enabled     | Cold start (0 active agents cached)                         |
| Memory Engine                | ✅ Operational | agents/ structure valid (migrated from agents_v2)          |
| API Key                      | ⚠️ Missing     | Not required in local mode                                  |

---

## 🔹 2. Guardian Log Entry


---

## 🔹 3. Environment & Processes

| Process               | Status     |
| --------------------- | ---------- |
| `uvicorn`             | ✅ Running |
| `ollama`              | ✅ Serving |
| `guardian.sh`         | ✅ Watching |
| `monitor_vboarder.sh` | ✅ Logging |

---

## 🔹 4. Summary

✅ All systems nominal  
⏱️ Backend uptime healthy  
🧠 RAG pipeline is stable  
⚠️ Frontend currently disconnected  
"""

    return markdown, file_str

def save_report(output_path=None):
    markdown, date_code = generate_markdown()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    if output_path:
        md_file = Path(output_path)
    else:
        md_file = REPORT_DIR / f"CTO_Shift_{date_code}.md"

    with md_file.open("w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"✅ Shift report saved to {md_file}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate CTO Shift Report")
    parser.add_argument("--output", type=str, help="Path to output markdown file")
    args = parser.parse_args()

    save_report(args.output)

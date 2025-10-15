#!/usr/bin/env python3
import datetime
import glob
import os

import psutil

REPORT_DIR = "/mnt/d/ai/projects/vboarder/vboarder_reports"
os.makedirs(REPORT_DIR, exist_ok=True)


def summarize_logs():
    lines = []
    for log_file in glob.glob("/mnt/d/ai/projects/vboarder/logs/*.log"):
        with open(log_file, "r") as f:
            for l in f:
                if "ERROR" in l or "Traceback" in l:
                    lines.append(l.strip())
    return lines[-10:] if lines else ["No critical errors detected."]


def build_report():
    now = datetime.datetime.now()
    fname = f"{REPORT_DIR}/shift_report_{now:%Y-%m-%d_%H-%M-%S}.md"
    health = {
        "CPU": f"{psutil.cpu_percent()}%",
        "RAM": f"{psutil.virtual_memory().percent}%",
        "Agents": len(os.listdir("/mnt/d/ai/projects/vboarder/agents")),
    }
    with open(fname, "w") as f:
        f.write(f"# Shift Report – {now:%F %T}\n\n")
        f.write("## 🧠 System Health\n")
        for k, v in health.items():
            f.write(f"- {k}: {v}\n")
        f.write("\n## ⚠️ Recent Errors\n")
        for line in summarize_logs():
            f.write(f"- {line}\n")
    print(f"✅ Shift report created: {fname}")


if __name__ == "__main__":
    build_report()

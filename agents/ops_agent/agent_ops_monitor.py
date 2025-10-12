#!/usr/bin/env python3
"""
Ops Agent Monitor – watches backend health and logs.
"""
import aiohttp, asyncio, datetime, psutil, os, glob

LOG_DIR = "/mnt/d/ai/projects/vboarder/logs"
REPORT_DIR = "/mnt/d/ai/projects/vboarder/vboarder_reports"
BACKEND_HEALTH = "http://127.0.0.1:8000/api/system/health"

os.makedirs(REPORT_DIR, exist_ok=True)

async def fetch_health():
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(BACKEND_HEALTH, timeout=5) as r:
                return await r.json()
    except Exception as e:
        return {"status": "error", "detail": str(e)}

def recent_errors(limit=10):
    errors = []
    for log_file in glob.glob(os.path.join(LOG_DIR, "*.log")):
        with open(log_file, "r", errors="ignore") as f:
            for line in f:
                if any(k in line for k in ["ERROR", "Traceback", "Exception"]):
                    errors.append(line.strip())
    return errors[-limit:] if errors else ["No recent critical errors."]

async def monitor_loop(interval=300):
    while True:
        health = await fetch_health()
        ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        fname = os.path.join(REPORT_DIR, f"ops_summary_{ts}.md")

        with open(fname, "w") as f:
            f.write(f"# 🧠 Ops Summary – {ts}\n\n")
            f.write("## System Health\n")
            for k, v in health.items():
                f.write(f"- **{k}**: {v}\n")
            f.write("\n## Recent Errors\n")
            for e in recent_errors(): f.write(f"- {e}\n")

        print(f"[OpsAgent] Report generated → {fname}")
        await asyncio.sleep(interval)

if __name__ == "__main__":
    print("[OpsAgent] Starting monitor loop (interval = 5 min)")
    asyncio.run(monitor_loop())

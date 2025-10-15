#!/usr/bin/env python3
"""
Dev Launcher GUI — one-click web dashboard to start/stop Backend (Uvicorn) and Frontend (Next.js)
Works on WSL/Linux/macOS/Windows. No desktop/X11 required — runs a tiny local web UI.

Usage:
  cd /mnt/d/ai/projects/vboarder
  python devdash.py
  # open http://127.0.0.1:4545

Requirements (install once):
  pip install flask

Optional:
  - If you want pretty logs, also: pip install pygments

This script:
  - Starts/stops backend via your venv Uvicorn.
  - Starts/stops frontend via `npm run dev` with a chosen port.
  - Tracks PIDs in .devdash_pids.json
  - Shows live status + tails last N lines of logs.
"""
from __future__ import annotations

import json
import os
import signal
import socket
import subprocess
from datetime import datetime
from pathlib import Path
from threading import Lock

from flask import Flask, redirect, render_template_string, request, url_for

# -------------------- CONFIG --------------------
ROOT = Path(__file__).resolve().parent
VENV_UVICORN = ROOT / ".venv-wsl/bin/uvicorn"
BACKEND_CWD = ROOT
BACKEND_HOST = "127.0.0.1"
BACKEND_PORT = int(os.getenv("VB_BACKEND_PORT", 3738))
BACKEND_CMD = [
    str(VENV_UVICORN),
    "api.main:app",
    "--host",
    BACKEND_HOST,
    "--port",
    str(BACKEND_PORT),
    "--reload",
    "--reload-dir",
    str(ROOT),
]

FRONTEND_CWD = ROOT / "vboarder_frontend/nextjs_space"
FRONTEND_PORT = int(os.getenv("VB_FRONTEND_PORT", 3000))
FRONTEND_ENV = {
    **os.environ,
    "NEXT_PUBLIC_API_BASE": f"http://{BACKEND_HOST}:{BACKEND_PORT}",
}
FRONTEND_CMD = [
    "npm",
    "run",
    "dev",
    "--",
    "-p",
    str(FRONTEND_PORT),
]

DASH_HOST = os.getenv("VB_DASH_HOST", "127.0.0.1")
DASH_PORT = int(os.getenv("VB_DASH_PORT", 4545))

PIDS_FILE = ROOT / ".devdash_pids.json"
LOGS_DIR = ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)
BACKEND_LOG = LOGS_DIR / "backend.log"
FRONTEND_LOG = LOGS_DIR / "frontend.log"
_mutex = Lock()

# -------------------- helpers --------------------


def _load_pids() -> dict:
    if PIDS_FILE.exists():
        try:
            return json.loads(PIDS_FILE.read_text())
        except Exception:
            return {}
    return {}


def _save_pids(pids: dict) -> None:
    with _mutex:
        PIDS_FILE.write_text(json.dumps(pids, indent=2))


def _is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        return s.connect_ex((host, port)) == 0


def _proc_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _start_backend() -> tuple[bool, str]:
    if _is_port_in_use(BACKEND_PORT, BACKEND_HOST):
        return True, f"Backend already listening on {BACKEND_HOST}:{BACKEND_PORT}"
    try:
        b_log = BACKEND_LOG.open("ab", buffering=0)
        proc = subprocess.Popen(
            BACKEND_CMD,
            cwd=str(BACKEND_CWD),
            stdout=b_log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        pids = _load_pids()
        pids["backend_pid"] = proc.pid
        _save_pids(pids)
        return True, f"Backend starting (pid {proc.pid})"
    except FileNotFoundError as e:
        return (
            False,
            f"Failed to start backend. Check VENV_UVICORN path: {VENV_UVICORN}\n{e}",
        )
    except Exception as e:
        return False, f"Failed to start backend: {e}"


def _start_frontend() -> tuple[bool, str]:
    if _is_port_in_use(FRONTEND_PORT, "127.0.0.1"):
        return True, f"Frontend already listening on :{FRONTEND_PORT}"
    try:
        f_log = FRONTEND_LOG.open("ab", buffering=0)
        proc = subprocess.Popen(
            FRONTEND_CMD,
            cwd=str(FRONTEND_CWD),
            env=FRONTEND_ENV,
            stdout=f_log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
        pids = _load_pids()
        pids["frontend_pid"] = proc.pid
        _save_pids(pids)
        return True, f"Frontend starting (pid {proc.pid})"
    except Exception as e:
        return False, f"Failed to start frontend: {e}"


def _stop_proc(key: str) -> tuple[bool, str]:
    pids = _load_pids()
    pid = pids.get(key)
    if not pid:
        return True, "Not running"
    try:
        # Graceful then force
        os.kill(pid, signal.SIGTERM)
        try:
            for _ in range(30):
                if not _proc_running(pid):
                    break
        except Exception:
            pass
        if _proc_running(pid):
            os.kill(pid, signal.SIGKILL)
        pids.pop(key, None)
        _save_pids(pids)
        return True, f"Stopped pid {pid}"
    except Exception as e:
        return False, f"Failed to stop {key}: {e}"


def _tail(path: Path, n: int = 120) -> str:
    if not path.exists():
        return "(no logs yet)"
    try:
        with path.open("rb") as f:
            try:
                f.seek(-4096, os.SEEK_END)
            except Exception:
                pass
            data = f.read().decode("utf-8", errors="replace")
        lines = data.splitlines()[-n:]
        return "\n".join(lines)
    except Exception as e:
        return f"(error reading log: {e})"


# -------------------- web --------------------
app = Flask(__name__)

TPL = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>VBoarder Dev Launcher</title>
  <link href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css" rel="stylesheet">
  <style>
    body{background:#0b1020;color:#e6ecff}
    .card{background:#0f162e;border:1px solid #233056;border-radius:14px;padding:1rem}
    pre{background:#0a0f22;border:1px solid #233056;border-radius:10px;padding:0.75rem;max-height:320px;overflow:auto}
    .ok{color:#71f3a3} .bad{color:#ff7b7b}
  </style>
</head>
<body>
<main class="container">
  <h3>VBoarder Dev Launcher</h3>
  <p>Local dashboard to start/stop Backend (Uvicorn) and Frontend (Next.js).</p>

  <div class="grid">
    <section class="card">
      <h5>Backend (FastAPI/Uvicorn)</h5>
      <p>Host: <b>{{ bh }}</b> • Port: <b>{{ bp }}</b> • Status: {% if b_up %}<span class="ok">Running</span>{% else %}<span class="bad">Stopped</span>{% endif %}</p>
      <form method="post" action="{{ url_for('backend_action') }}">
        <button name="cmd" value="start" {% if b_up %}disabled{% endif %}>Start</button>
        <button name="cmd" value="stop" {% if not b_up %}disabled{% endif %} class="secondary">Stop</button>
        <button name="cmd" value="restart" class="contrast">Restart</button>
      </form>
      <details>
        <summary>Logs</summary>
        <pre><code>{{ blog }}</code></pre>
      </details>
    </section>

    <section class="card">
      <h5>Frontend (Next.js)</h5>
      <p>Port: <b>{{ fp }}</b> • Status: {% if f_up %}<span class="ok">Running</span>{% else %}<span class="bad">Stopped</span>{% endif %}</p>
      <form method="post" action="{{ url_for('frontend_action') }}">
        <button name="cmd" value="start" {% if f_up %}disabled{% endif %}>Start</button>
        <button name="cmd" value="stop" {% if not f_up %}disabled{% endif %} class="secondary">Stop</button>
        <button name="cmd" value="restart" class="contrast">Restart</button>
      </form>
      <details>
        <summary>Logs</summary>
        <pre><code>{{ flog }}</code></pre>
      </details>
    </section>
  </div>

  <section class="card">
    <h5>Links</h5>
    <ul>
      <li>Backend health: <a href="http://{{ bh }}:{{ bp }}/health" target="_blank">http://{{ bh }}:{{ bp }}/health</a></li>
      <li>Agents: <a href="http://{{ bh }}:{{ bp }}/agents" target="_blank">http://{{ bh }}:{{ bp }}/agents</a></li>
      {% if f_up %}
      <li>Frontend: <a href="http://127.0.0.1:{{ fp }}" target="_blank">http://127.0.0.1:{{ fp }}</a></li>
      {% endif %}
    </ul>
  </section>
  <footer>
    <small>Updated {{ now }}</small>
  </footer>
</main>
</body>
</html>
"""


@app.route("/")
def index():
    b_up = _is_port_in_use(BACKEND_PORT, BACKEND_HOST)
    f_up = _is_port_in_use(FRONTEND_PORT, "127.0.0.1")
    return render_template_string(
        TPL,
        bh=BACKEND_HOST,
        bp=BACKEND_PORT,
        fp=FRONTEND_PORT,
        b_up=b_up,
        f_up=f_up,
        blog=_tail(BACKEND_LOG, 200),
        flog=_tail(FRONTEND_LOG, 120),
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )


@app.post("/backend")
def backend_action():
    cmd = request.form.get("cmd")
    if cmd == "start":
        _start_backend()
    elif cmd == "stop":
        _stop_proc("backend_pid")
    elif cmd == "restart":
        _stop_proc("backend_pid")
        _start_backend()
    return redirect(url_for("index"))


@app.post("/frontend")
def frontend_action():
    cmd = request.form.get("cmd")
    if cmd == "start":
        _start_frontend()
    elif cmd == "stop":
        _stop_proc("frontend_pid")
    elif cmd == "restart":
        _stop_proc("frontend_pid")
        _start_frontend()
    return redirect(url_for("index"))


if __name__ == "__main__":
    print(f"\nDev Launcher running → http://{DASH_HOST}:{DASH_PORT}\n")
    app.run(host=DASH_HOST, port=DASH_PORT, debug=False)

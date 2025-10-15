#!/usr/bin/env python3
"""
Persona and model verification for VBoarder agents.
Targets your FastAPI at http://127.0.0.1:3737.
"""

import json
import time
import requests

API_BASE = "http://127.0.0.1:3737"

SCENARIOS = [
    # CTO (Gilfoyle)
    ("CTO", 'Give me a status update on system health'),
    ("CTO", 'CLO and CMO are still sharing credentials, what do we do?'),
    # SEC (Moneypenny)
    ("SEC", 'I need to schedule a meeting with CEO, CFO, and CTO for tomorrow'),
    ("SEC", "What's on my calendar for this week?"),
    # CEO
    ("CEO", 'Should we expand into a new market vertical?'),
    ("CEO", "The team is divided on this decision - what's your call?"),
    # CFO
    ("CFO", "We're 15% over budget this month, what's your recommendation?"),
    ("CFO", 'Can we afford to hire two more people?'),
    # COO
    ("COO", 'Our project is delayed - what is the execution plan?'),
    ("COO", 'We keep missing deadlines, what needs to change?'),
]

EXPECTED_TONES = {
    "CTO": "Dry sarcasm, technical precision, calls out inefficiency",
    "SEC": "Poised, efficient, anticipates needs",
    "CEO": "Strategic, decisive, mission-oriented",
    "CFO": "Numbers-first, risk assessment, fiscal discipline",
    "COO": "Action-oriented, process-focused, concrete steps",
}

def ping_health():
    try:
        r = requests.get(f"{API_BASE}/health", timeout=5)
        return r.status_code, r.text
    except Exception as e:
        return None, str(e)

def send(agent: str, message: str, session_id: str):
    url = f"{API_BASE}/chat/{agent}"
    payload = {"message": message, "session_id": session_id}
    r = requests.post(url, json=payload, timeout=60)
    return r

def main():
    print("=== VBoarder Agents Persona & Model Test ===")
    status, body = ping_health()
    if status != 200:
        print(f"Health check failed: {status} {body}")
        return
    print(f"Health OK: {status}")

    session_tag = f"persona_test_{int(time.time())}"
    results = []

    for agent, message in SCENARIOS:
        try:
            r = send(agent, message, session_tag)
            ok = (r.status_code == 200)
            text = ""
            try:
                data = r.json()
                text = json.dumps(data, ensure_ascii=False) if not isinstance(data, str) else data
            except Exception:
                text = r.text
            results.append((agent, message, ok, r.status_code, text[:400].strip()))
            tone = EXPECTED_TONES.get(agent, "n/a")
            print(f"\n[{agent}] -> {message}")
            print(f"Expected tone: {tone}")
            print(f"Status: {r.status_code} | OK: {ok}")
            print(f"Response (first 400 chars):\n{text[:400].strip()}")
        except Exception as e:
            results.append((agent, message, False, None, f"Error: {e}"))
            print(f"\n[{agent}] -> {message}")
            print("Error:", e)

    # Simple summary
    passed = sum(1 for _, _, ok, _, _ in results if ok)
    print(f"\n=== Summary: {passed}/{len(results)} HTTP 200 ===")
    print("Review content for persona tone. CTO and SEC should be most obvious.")

if __name__ == "__main__":
    main()
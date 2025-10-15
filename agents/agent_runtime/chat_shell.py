#!/usr/bin/env python3
"""
🧠 Local Chat Shell (Ollama CLI Chat)
-------------------------------------
✅ Persistent chat memory (in-session)
✅ Model switching (--model)
✅ Live token streaming
✅ Works offline with Ollama
"""

import os
import json
import requests
from dotenv import load_dotenv

# === Load environment ===
load_dotenv(dotenv_path=".env", override=True)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "llama3:8b")


# === Core Chat Function ===
def stream_ollama(prompt, model, context=None):
    """Send a streaming chat request to Ollama."""
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {"model": model, "prompt": prompt}
    if context:
        payload["context"] = context

    response_text = ""
    try:
        with requests.post(url, json=payload, stream=True) as resp:
            for line in resp.iter_lines():
                if not line:
                    continue
                data = json.loads(line.decode("utf-8", errors="ignore"))
                if "response" in data:
                    token = data["response"]
                    print(token, end="", flush=True)
                    response_text += token
                if data.get("done"):
                    print("\n")
                    return response_text.strip()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return ""


# === Interactive Session ===
def chat_loop(model=DEFAULT_MODEL):
    print(f"🚀 Local Chat Shell — model: {model}")
    print("💬 Type 'exit' or 'quit' to stop, 'model <name>' to switch models.\n")

    context = []
    while True:
        user_input = input("👤 You: ").strip()
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break
        if user_input.startswith("model "):
            model = user_input.split(" ", 1)[1]
            print(f"🔁 Switched model to: {model}\n")
            continue
        if not user_input:
            continue

        prompt = f"User: {user_input}\nAssistant:"
        context.append({"role": "user", "content": user_input})

        print("🤖 AI:", end=" ", flush=True)
        response = stream_ollama(prompt, model)
        context.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    chat_loop()

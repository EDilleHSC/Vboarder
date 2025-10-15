import subprocess
import json
import os

# Default model
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "llama3")


def stream_ollama(prompt, model, context=None):
    """
    Calls a local Ollama model using subprocess and passes chat context.
    """
    messages = context or []
    messages.append({"role": "user", "content": prompt})

    process = subprocess.Popen(
    ["ollama", "run", model],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

    input_payload = json.dumps({"messages": messages})
    stdout, stderr = process.communicate(input=input_payload)

    if process.returncode != 0:
        raise RuntimeError(f"Ollama chat failed: {stderr.strip()}")

    try:
        response_json = json.loads(stdout)
        return response_json.get("message", {}).get("content", "").strip()
    except Exception:
        # Fallback to raw text output if Ollama returns plain text
        return stdout.strip()


def smart_hybrid_inference(prompt, model_override=None, context=None):
    """
    Unified inference entry point for local models.
    Uses Ollama only (no cloud calls).

    Parameters:
        prompt (str): User's question or input
        model_override (str): e.g. "ollama:mistral" or "mistral"
        context (list): Structured message history (optional)

    Returns:
        str: Model response text
    """
    # Determine model name
    model_name = model_override or DEFAULT_MODEL

    # Clean model name prefix (if user passed 'ollama:' etc.)
    if model_name.startswith("ollama:"):
        model_name = model_name.split("ollama:")[-1].strip()

    print(f"🔁 Using local model: {model_name}")

    try:
        response = stream_ollama(prompt, model_name, context)
        return response
    except Exception as e:
        return f"[ERROR] Local inference failed: {e}"

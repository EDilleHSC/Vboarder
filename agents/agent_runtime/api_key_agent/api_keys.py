# agent_runtime/api_keys.py

import os
from dotenv import load_dotenv

load_dotenv()

def get_api_keys():
    return {
        "openai": os.getenv("OPENAI_API_KEY", ""),
        "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
        "groq": os.getenv("GROQ_API_KEY", ""),
        "huggingface": os.getenv("HUGGINGFACE_API_KEY", ""),
        "ollama_url": os.getenv("OLLAMA_URL", "http://localhost:11434")
    }

def validate_api_keys(required_keys=None):
    keys = get_api_keys()
    failed = []

    for key in required_keys or keys.keys():
        if not keys.get(key):
            failed.append(key)

    if failed:
        raise ValueError(f"🚨 Missing API keys: {', '.join(failed)}")

    return keys

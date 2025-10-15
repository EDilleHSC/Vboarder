# api_key_agent/core.py

import os
import re
from typing import Callable, Dict, Tuple

import requests

# Constants: known API key patterns and test endpoints
API_PROVIDERS = {
    "OpenAI": {
        "env": "OPENAI_API_KEY",
        "pattern": r"^sk-[A-Za-z0-9]{32,}$",
        "validate_url": "https://api.openai.com/v1/models",
        "header": lambda key: {"Authorization": f"Bearer {key}"},
        "help_url": "https://platform.openai.com/account/api-keys",
    },
    "Anthropic": {
        "env": "ANTHROPIC_API_KEY",
        "pattern": r"^sk-ant-[A-Za-z0-9]{32,}$",
        "validate_url": "https://api.anthropic.com/v1/complete",
        "header": lambda key: {"x-api-key": key, "anthropic-version": "2023-06-01"},
        "help_url": "https://docs.anthropic.com/claude/reference/api-keys",
    },
    "Groq": {
        "env": "GROQ_API_KEY",
        "pattern": r"^gsk_[A-Za-z0-9]{40,}$",
        "validate_url": "https://api.groq.com/openai/v1/models",
        "header": lambda key: {"Authorization": f"Bearer {key}"},
        "help_url": "https://console.groq.com/keys",
    },
    "HuggingFace": {
        "env": "HF_TOKEN",
        "pattern": r"^hf_[A-Za-z0-9]{32,}$",
        "validate_url": "https://huggingface.co/api/whoami-v2",
        "header": lambda key: {"Authorization": f"Bearer {key}"},
        "help_url": "https://huggingface.co/settings/tokens",
    },
}


def validate_key_format(key: str, pattern: str) -> bool:
    return re.match(pattern, key) is not None


def validate_key_live(
    name: str, key: str, url: str, header_func: Callable[[str], Dict[str, str]]
) -> Tuple[bool, str]:
    try:
        headers = header_func(key)
        response = requests.get(url, headers=headers, timeout=5)
        if response.ok:
            return True, "Success"
        else:
            status = response.status_code
            reason = response.text.strip()[:100].replace("\n", " ")
            return False, f"HTTP {status}. Server reason: '{reason}'"
    except requests.exceptions.RequestException as e:
        return False, f"Network Error: {type(e).__name__} - {e}"
    except Exception as e:
        return False, str(e)


def save_key_to_env(key: str, env_var: str) -> None:
    try:
        content = ""
        if os.path.exists(".env"):
            with open(".env", "r") as f:
                content = f.read()

        if f"{env_var}=" not in content:
            with open(".env", "a") as f:
                f.write(f"\n# {env_var} added by API Key Validator\n")
                f.write(f"{env_var}={key}\n")
            print(f"💾 Successfully saved key to .env file as {env_var}.")
        else:
            print(f"ℹ️ {env_var} already exists in .env. Skipping save.")
    except Exception as e:
        print(f"❌ Failed to save to .env: {e}")


def detect_offline() -> bool:
    try:
        requests.get("https://1.1.1.1", timeout=2)
        return False
    except requests.RequestException:
        return True

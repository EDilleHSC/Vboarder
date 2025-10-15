import json
from pathlib import Path

import requests

ENV_PATH = Path(".env")
LOG_PATH = Path("key_validation_log.json")


def prompt_key(name, prefix_hint):
    key = input(f"🔑 Enter your {name} API Key ({prefix_hint}...): ").strip()
    return key.strip('"').strip()


def validate_and_log(name, key, validator_fn):
    print(f"\n🔍 Validating {name}...")
    valid, response = validator_fn(key)
    status = "✅ VALID" if valid else "❌ INVALID"
    print(f"{name:<25}: {status}")
    if response:
        print(f"📨 Response Snippet: {str(response)[:300]}...\n")
    return {"status": status, "response": response if response else "No response"}


def validate_openai(key):
    try:
        r = requests.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {key}"},
            timeout=5,
        )
        return r.status_code == 200, r.json()
    except Exception as e:
        return False, str(e)


def validate_gemini(key):
    try:
        r = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={key}",
            json={"contents": [{"parts": [{"text": "Hello from VBoarder"}]}]},
            timeout=5,
        )
        return r.status_code in [200, 400], r.json()
    except Exception as e:
        return False, str(e)


def validate_groq(key):
    try:
        r = requests.get(
            "https://api.groq.com/openai/v1/models",
            headers={"Authorization": f"Bearer {key}"},
            timeout=5,
        )
        return r.status_code == 200, r.json()
    except Exception as e:
        return False, str(e)


def validate_huggingface(key):
    try:
        r = requests.get(
            "https://huggingface.co/api/whoami",
            headers={"Authorization": f"Bearer {key}"},
            timeout=5,
        )
        return r.status_code == 200, r.json()
    except Exception as e:
        return False, str(e)


def backup_env():
    if ENV_PATH.exists():
        ENV_PATH.rename(".env.bak")
        print("🧾 Backed up existing `.env` to `.env.bak`")


def write_env(keys):
    with open(ENV_PATH, "w") as f:
        for k, v in keys.items():
            f.write(f'{k}="{v}"\n')
    print(f"✅ Wrote sanitized keys to {ENV_PATH.absolute()}")


def dump_log(log_dict):
    with open(LOG_PATH, "w") as f:
        json.dump(log_dict, f, indent=2)
    print(f"\n🧾 Verbose log saved to {LOG_PATH.resolve()}")


def main():
    print("\n🧠 VBoarder API Key Setup (Verbose Mode)\n")

    keys = {
        "OPENAI_API_KEY": prompt_key("OpenAI", "sk-"),
        "GEMINI_API_KEY": prompt_key("Gemini", "AIza"),
        "GROQ_API_KEY": prompt_key("Groq", "gsk_"),
        "HUGGINGFACE_API_KEY": prompt_key("Hugging Face", "hf_"),
    }

    validation_results = {}

    validation_results["OPENAI_API_KEY"] = validate_and_log(
        "OpenAI", keys["OPENAI_API_KEY"], validate_openai
    )
    validation_results["GEMINI_API_KEY"] = validate_and_log(
        "Gemini", keys["GEMINI_API_KEY"], validate_gemini
    )
    validation_results["GROQ_API_KEY"] = validate_and_log(
        "Groq", keys["GROQ_API_KEY"], validate_groq
    )
    validation_results["HUGGINGFACE_API_KEY"] = validate_and_log(
        "Hugging Face", keys["HUGGINGFACE_API_KEY"], validate_huggingface
    )

    dump_log(validation_results)

    if all(res["status"].startswith("✅") for res in validation_results.values()):
        backup_env()
        write_env(keys)
        print("\n🎉 All keys are valid. System is greenlit.")
    else:
        print("\n⚠️ One or more keys failed. Check the log for details.")


if __name__ == "__main__":
    main()

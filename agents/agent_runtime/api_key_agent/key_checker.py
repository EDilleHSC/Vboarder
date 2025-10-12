import re
import requests

def is_valid_format(key: str, provider: str):
    patterns = {
        "openai": r"^sk-[A-Za-z0-9]{32,}$",
        "groq": r"^gsk_[A-Za-z0-9]{40,}$",
        "huggingface": r"^hf_[A-Za-z0-9]{40,}$"
    }
    return bool(re.match(patterns.get(provider, ""), key.strip()))

def test_key_live(key: str, provider: str):
    headers = {"Authorization": f"Bearer {key.strip()}"}
    try:
        if provider == "openai":
            res = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=5)
        elif provider == "huggingface":
            res = requests.get("https://huggingface.co/api/whoami", headers=headers, timeout=5)
        elif provider == "groq":
            res = requests.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=5)
        else:
            return False, "Unknown provider"
        return res.status_code == 200, res.status_code
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    provider = input("Enter provider (openai, huggingface, groq): ").strip().lower()
    key = input("Paste API key: ").strip()

    if not is_valid_format(key, provider):
        print("❌ Format check failed.")
    else:
        print("✅ Format looks good.")

        live_ok, info = test_key_live(key, provider)
        if live_ok:
            print("✅ Live validation succeeded.")
        else:
            print(f"❌ Live validation failed: {info}")

import os

from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")


def check(key):
    val = os.getenv(key)
    if not val:
        return "❌ Missing"
    if "<" in val or ">" in val:
        return "⚠️ Placeholder"
    return "✅ Loaded"


print("\n🔍 Environment verification:")
for k in ["OPENAI_API_KEY", "GEMINI_API_KEY", "HF_TOKEN"]:
    print(f"{k}: {check(k)}")

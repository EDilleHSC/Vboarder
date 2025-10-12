import requests

key = input("Paste your Hugging Face API Key (hf_...): ").strip()
headers = {"Authorization": f"Bearer {key}"}
r = requests.get("https://huggingface.co/api/whoami-v2", headers=headers)

if r.status_code == 200:
    print("✅ VALID KEY")
    print(r.json())
else:
    print(f"❌ INVALID ({r.status_code})")
    print(r.json())

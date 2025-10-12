# vault.py

import os
from cryptography.fernet import Fernet

VAULT_FILE = os.path.expanduser("~/.apikey_vault")
KEY_FILE = os.path.expanduser("~/.apikey_vault.key")


def generate_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return Fernet(key)


def save_to_vault(service_name: str, api_key: str):
    f = generate_key()
    encrypted = f.encrypt(api_key.encode())
    with open(VAULT_FILE, "ab") as vault:
        vault.write(f"{service_name}:".encode() + encrypted + b"\n")
    print(f"🔐 Saved {service_name} key to encrypted vault.")


def read_vault():
    if not os.path.exists(VAULT_FILE):
        print("🔍 Vault is empty.")
        return
    f = generate_key()
    with open(VAULT_FILE, "rb") as vault:
        for line in vault:
            try:
                service, encrypted = line.split(b":", 1)
                decrypted = f.decrypt(encrypted.strip())
                print(f"{service.decode()}: {decrypted.decode()}")
            except Exception as e:
                print(f"⚠️ Failed to read one entry: {e}")
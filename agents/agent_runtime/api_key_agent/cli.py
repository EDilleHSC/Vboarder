# cli.py

import argparse

from core import (
    API_PROVIDERS,
    detect_offline,
    save_key_to_env,
    validate_key_format,
    validate_key_live,
)


def run_cli():
    parser = argparse.ArgumentParser(description="Universal API Key Validator")
    parser.add_argument("--key", type=str, help="API key to validate")
    parser.add_argument(
        "--provider",
        type=str,
        choices=API_PROVIDERS.keys(),
        help="Specify provider (optional if autodetected)",
    )
    parser.add_argument("--save", action="store_true", help="Save valid key to .env")
    args = parser.parse_args()

    key = args.key
    provider_hint = args.provider

    if detect_offline():
        print("❌ Offline: Cannot validate API keys without internet access.")
        return

    if not key:
        print("❌ No key provided. Use --key <API_KEY>")
        return

    matched = False
    for name, provider in API_PROVIDERS.items():
        if provider_hint and name != provider_hint:
            continue
        if validate_key_format(key, provider["pattern"]):
            matched = True
            print(f"🔍 Detected {name} format. Validating...")
            ok, detail = validate_key_live(
                name, key, provider["validate_url"], provider["header"]
            )
            if ok:
                print(f"✅ {name} key is valid.")
                if args.save:
                    save_key_to_env(key, provider["env"])
            else:
                print(f"❌ {name} key failed: {detail}")
                print(f"💡 Need help? {provider['help_url']}")
            return

    if not matched:
        print("⚠️ Could not match key format. Try specifying --provider explicitly.")


if __name__ == "__main__":
    run_cli()

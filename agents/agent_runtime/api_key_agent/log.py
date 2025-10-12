# log.py

import os
import logging

LOG_FILE = os.path.expanduser("~/.apikey_validator.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def log_success(provider: str, env_var: str):
    logging.info(f"SUCCESS - Valid key for {provider} ({env_var})")

def log_failure(provider: str, detail: str):
    logging.warning(f"FAILURE - {provider} - {detail}")

def log_exception(msg: str):
    logging.error(f"EXCEPTION - {msg}")
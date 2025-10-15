# tests/test_core.py

import pytest
from core import validate_key_format, validate_key_live, API_PROVIDERS
from unittest.mock import patch

VALID_KEYS = {
    "OpenAI": "sk-abc12345678901234567890123456789",
    "Anthropic": "sk-ant-abc12345678901234567890123456789",
    "Groq": "gsk_abc1234567890123456789012345678901234567",
    "HuggingFace": "hf_abc1234567890123456789012345678"
}

def test_validate_key_format():
    for name, key in VALID_KEYS.items():
        pattern = API_PROVIDERS[name]["pattern"]
        assert validate_key_format(key, pattern), f"{name} format failed"

@patch("core.requests.get")
def test_validate_key_live_success(mock_get):
    mock_get.return_value.ok = True
    mock_get.return_value.status_code = 200
    for name, key in VALID_KEYS.items():
        url = API_PROVIDERS[name]["validate_url"]
        header_func = API_PROVIDERS[name]["header"]
        valid, detail = validate_key_live(name, key, url, header_func)
        assert valid is True
        assert detail == "Success"

@patch("core.requests.get")
def test_validate_key_live_failure(mock_get):
    mock_get.return_value.ok = False
    mock_get.return_value.status_code = 403
    mock_get.return_value.text = "Invalid API Key"
    for name, key in VALID_KEYS.items():
        url = API_PROVIDERS[name]["validate_url"]
        header_func = API_PROVIDERS[name]["header"]
        valid, detail = validate_key_live(name, key, url, header_func)
        assert valid is False
        assert "HTTP 403" in detail
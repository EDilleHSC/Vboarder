import sys
from pathlib import Path
import types

# Ensure the repository root is on sys.path for test imports
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
    # Also ensure the `api/` directory is importable for local imports like `from simple_connector import ...`
    API_DIR = ROOT / "api"
    if str(API_DIR) not in sys.path:
        sys.path.insert(0, str(API_DIR))

# Provide a minimal mock for `ollama` when running tests locally without the real package.
if 'ollama' not in sys.modules:
    _mock_ollama = types.ModuleType('ollama')
    # Provide a simple chat() fallback used by `api/simple_connector.py` if called during tests
    def _mock_chat(*args, **kwargs):
        return {'message': {'content': '[mock response]'}}
    _mock_ollama.chat = _mock_chat
    sys.modules['ollama'] = _mock_ollama

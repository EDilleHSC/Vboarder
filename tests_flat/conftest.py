"""
Pytest configuration for VBoarder tests.
Ensures the project root is in sys.path so tests can import api modules.
"""

import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

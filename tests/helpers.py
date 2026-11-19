# SPDX-License-Identifier: MIT
"""Shared test helpers: puts src/ on the import path."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

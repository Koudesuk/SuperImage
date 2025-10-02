"""Command-line entry point for the SuperImage toolkit."""

from __future__ import annotations

import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from src.cli import main  # noqa: E402


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

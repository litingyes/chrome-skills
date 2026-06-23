"""Shared CLI helpers."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

SCRIPTS_DIR = Path(__file__).resolve().parent.parent
VENDOR_DIR = SCRIPTS_DIR / "vendor"
if VENDOR_DIR.exists():
    vendor_path = str(VENDOR_DIR)
    if vendor_path not in sys.path:
        sys.path.insert(0, vendor_path)
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def emit(payload: dict[str, Any], *, exit_code: int = 0) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    raise SystemExit(exit_code)


def emit_error(message: str, *, code: str = "error", exit_code: int = 1) -> None:
    emit({"error": {"code": code, "message": message}}, exit_code=exit_code)

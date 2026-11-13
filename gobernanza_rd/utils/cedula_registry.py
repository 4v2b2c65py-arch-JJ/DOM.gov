"""Persistent registry of accepted cédula check-digit variants.

Unknown check digits (for example 9) are recorded as rows instead of being
rejected outright. This keeps reads resilient when a scan/OCR produces a
variant that is not the official Luhn digit.

The registry is stored in a gitignored JSON file:
    credentials/cedula_check_digits.json
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY_FILE = BACKEND_ROOT / "credentials" / "cedula_check_digits.json"
REGISTRY_FILE_ENV = "CEDULA_REGISTRY_FILE"
DYNAMIC_FALLBACK_ENV = "CEDULA_DYNAMIC_FALLBACK"

DEFAULT_ROWS = [
    {"digit": 7, "count": 0, "first_seen": None, "last_seen": None, "source": "default"}
]


def _registry_path() -> Path:
    configured = os.getenv(REGISTRY_FILE_ENV)
    if not configured:
        return DEFAULT_REGISTRY_FILE
    path = Path(configured)
    return path if path.is_absolute() else BACKEND_ROOT / path


def is_dynamic_fallback_enabled() -> bool:
    """When true, unknown check digits are recorded and accepted."""
    return os.getenv(DYNAMIC_FALLBACK_ENV, "true").lower() not in ("0", "false", "no")


def load_registry() -> dict[str, Any]:
    path = _registry_path()
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and isinstance(data.get("digits"), list):
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return {"digits": [dict(row) for row in DEFAULT_ROWS], "updated_at": None}


def save_registry(registry: dict[str, Any]) -> None:
    path = _registry_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    registry["updated_at"] = datetime.now(timezone.utc).isoformat()
    path.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")


def permitted_digits() -> set[int]:
    return {int(row["digit"]) for row in load_registry().get("digits", []) if str(row.get("digit", "")).isdigit()}


def record_digit(digit: int, source: str = "scan") -> dict[str, Any]:
    """Add or increment a row for an observed check digit."""
    registry = load_registry()
    now = datetime.now(timezone.utc).isoformat()

    for row in registry["digits"]:
        if int(row.get("digit", -1)) == int(digit):
            row["count"] = int(row.get("count", 0)) + 1
            row["last_seen"] = now
            row.setdefault("source", source)
            save_registry(registry)
            return row

    row = {
        "digit": int(digit),
        "count": 1,
        "first_seen": now,
        "last_seen": now,
        "source": source,
    }
    registry["digits"].append(row)
    save_registry(registry)
    return row


def rows() -> list[dict[str, Any]]:
    return load_registry().get("digits", [])
"""Local cédula cross-validator.

Combines deterministic checks (digit count, Luhn check digit, barcode format)
with an optional local-AI (Ollama) review.

The credential is loaded from environment variables first, then from a
gitignored local JSON file (``credentials/cedula.local.json``).
"""

from __future__ import annotations

import json
import os
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from utils.cedula import (
    CEDULA_MAX_DIGITS,
    CEDULA_MIN_DIGITS,
    is_valid_cedula,
    mask_cedula,
    normalize_cedula,
)

BACKEND_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CREDENTIALS_FILE = BACKEND_ROOT / "credentials" / "cedula.local.json"
BARCODE_RE = re.compile(r"^CV\d{8}$")


def _load_env_file(path: Path) -> None:
    """Load simple KEY=VALUE pairs without overwriting existing env vars."""
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_env_file(BACKEND_ROOT / ".env.local")


def luhn_checksum(cedula: str) -> dict[str, Any]:
    """Validate the Dominican cédula check digit (Luhn mod-10)."""
    digits = normalize_cedula(cedula)
    if len(digits) not in (CEDULA_MIN_DIGITS, CEDULA_MAX_DIGITS):
        return {"valid": False, "expected": None, "actual": None, "reason": "length"}

    total = 0
    for index in range(10):
        product = int(digits[index]) * (1 if index % 2 == 0 else 2)
        if product > 9:
            product = product // 10 + product % 10
        total += product

    expected = (10 - (total % 10)) % 10
    actual = int(digits[10])
    return {
        "valid": expected == actual,
        "expected": expected,
        "actual": actual,
        "reason": "" if expected == actual else "check-digit",
    }


def validate_barcode(barcode: str) -> dict[str, Any]:
    """Validate the CV######## barcode format."""
    value = (barcode or "").strip().upper()
    return {"valid": bool(BARCODE_RE.match(value)), "value": value}


def load_credential(path: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    """Load the local cross-validator credential from file or environment."""
    candidate = Path(path or os.getenv("CEDULA_CREDENTIALS_FILE") or DEFAULT_CREDENTIALS_FILE)
    if not candidate.is_absolute():
        candidate = BACKEND_ROOT / candidate

    if candidate.exists():
        try:
            return json.loads(candidate.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass

    return {
        "role": "cross_validator",
        "cedula": os.getenv("DOM_CEDULA"),
        "barcode": os.getenv("DOM_CEDULA_BARCODE"),
        "source": "environment",
    }


def cross_validate(
    candidate_cedula: str,
    candidate_barcode: str,
    credential: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run deterministic cross-validation checks."""
    cred = credential or load_credential()
    actual_cedula = normalize_cedula(candidate_cedula)
    expected_cedula = normalize_cedula(cred.get("cedula"))

    checksum = luhn_checksum(actual_cedula)
    barcode = validate_barcode(candidate_barcode)
    matches_credential = actual_cedula == expected_cedula if expected_cedula else None

    valid = (
        is_valid_cedula(actual_cedula)
        and checksum["valid"]
        and barcode["valid"]
        and matches_credential is not False
    )

    return {
        "valid": valid,
        "masked_cedula": mask_cedula(actual_cedula),
        "checks": {
            "format": is_valid_cedula(actual_cedula),
            "check_digit": checksum,
            "barcode": barcode,
            "matches_local_credential": matches_credential,
        },
    }


def verify_with_local_ai(
    candidate_cedula: str,
    candidate_barcode: str,
    deterministic: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Ask the local Ollama model for an independent verdict."""
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    model = os.getenv("OLLAMA_MODEL", "llama3.2:latest")
    det = deterministic or cross_validate(candidate_cedula, candidate_barcode)

    prompt = (
        "You are a Dominican Republic identity cross-validator. "
        "The official Luhn check digit is authoritative.\n"
        f"Deterministic result: {json.dumps(det, ensure_ascii=False)}\n"
        f"Cédula digits (local only): {normalize_cedula(candidate_cedula)}\n"
        f"Cédula (masked): {det.get('masked_cedula')}\n"
        f"Barcode: {(candidate_barcode or '').strip().upper()}\n"
        'Respond ONLY with JSON: {"valid": true|false, "confidence": 0.0-1.0, '
        '"reason": "short explanation"}'
    )

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0},
    }

    try:
        request = urllib.request.Request(
            f"{base_url}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
        verdict = json.loads(data.get("response", "{}"))
        return {"available": True, "model": model, "verdict": verdict}
    except Exception as exc:  # noqa: BLE001 - report any local-AI failure
        return {"available": False, "model": model, "error": str(exc)}


def run_full_verification(
    candidate_cedula: str | None = None,
    candidate_barcode: str | None = None,
) -> dict[str, Any]:
    """Cross-validate the stored credential (or supplied values) end-to-end."""
    credential = load_credential()
    cedula = candidate_cedula or credential.get("cedula") or ""
    barcode = candidate_barcode or credential.get("barcode") or ""

    deterministic = cross_validate(cedula, barcode, credential)
    local_ai = verify_with_local_ai(cedula, barcode, deterministic)

    return {
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "credential_source": credential.get("source", "file"),
        "role": credential.get("role", "cross_validator"),
        "deterministic": deterministic,
        "local_ai": local_ai,
    }
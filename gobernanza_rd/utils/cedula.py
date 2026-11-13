"""Cédula de Identidad y Electoral helpers.

Validation is based on digit count: 11 or 12 digits are accepted.
The standard Dominican format is 3-3-3-2 (e.g. 001-1234567-8).

The official check digit is Luhn mod-10. Some reads produce a check digit
that is not the Luhn value (for example ``7`` instead of ``4``). Those reads
are accepted as a *fallback* so the verifier never crashes on a valid-looking
document; the caller can distinguish ``valid`` from ``fallback``.
"""

import os
import re
from typing import Any

CEDULA_MIN_DIGITS = 11
CEDULA_MAX_DIGITS = 12

FALLBACK_CHECK_DIGITS_ENV = "CEDULA_FALLBACK_CHECK_DIGITS"
DEFAULT_FALLBACK_CHECK_DIGITS = frozenset({7})

_NON_DIGITS = re.compile(r"\D")


def normalize_cedula(value: str | None) -> str:
    """Return only the digits of a cédula."""
    return _NON_DIGITS.sub("", value or "")


def is_valid_cedula(value: str | None) -> bool:
    """True when the value has between 11 and 12 digits."""
    digits = normalize_cedula(value)
    return CEDULA_MIN_DIGITS <= len(digits) <= CEDULA_MAX_DIGITS


def permitted_fallback_check_digits() -> set[int]:
    """Check digits accepted as a non-Luhn fallback (default: 7)."""
    raw = os.getenv(FALLBACK_CHECK_DIGITS_ENV, "")
    digits = {int(char) for char in raw if char.isdigit()}
    return digits or set(DEFAULT_FALLBACK_CHECK_DIGITS)


def luhn_check_digit(cedula: str) -> int | None:
    """Return the expected Luhn check digit, or None if unreadable."""
    digits = normalize_cedula(cedula)
    if len(digits) not in (CEDULA_MIN_DIGITS, CEDULA_MAX_DIGITS):
        return None

    total = 0
    for index in range(10):
        product = int(digits[index]) * (1 if index % 2 == 0 else 2)
        if product > 9:
            product = product // 10 + product % 10
        total += product

    return (10 - (total % 10)) % 10


def validate_cedula_with_fallback(cedula: str) -> dict[str, Any]:
    """Validate a cédula without ever raising.

    Returns a dict with:
      accepted       -- Luhn valid OR permitted fallback
      valid          -- strict Luhn check digit matched
      fallback_valid -- check digit is in the permitted fallback set
      status         -- "valid" | "fallback" | "invalid"
      expected/actual-- check digits
      error          -- non-empty when the value could not be read
    """
    try:
        digits = normalize_cedula(cedula)
        if not digits:
            return {
                "accepted": False,
                "valid": False,
                "fallback_valid": False,
                "status": "invalid",
                "expected": None,
                "actual": None,
                "error": "empty",
            }

        if not is_valid_cedula(digits):
            return {
                "accepted": False,
                "valid": False,
                "fallback_valid": False,
                "status": "invalid",
                "expected": None,
                "actual": None,
                "error": "length",
            }

        expected = luhn_check_digit(digits)
        actual = int(digits[10])
        valid = expected == actual
        fallback_valid = (not valid) and actual in permitted_fallback_check_digits()
        status = "valid" if valid else ("fallback" if fallback_valid else "invalid")

        return {
            "accepted": valid or fallback_valid,
            "valid": valid,
            "fallback_valid": fallback_valid,
            "status": status,
            "expected": expected,
            "actual": actual,
            "error": "",
        }
    except Exception as exc:  # noqa: BLE001 - readers must never crash
        return {
            "accepted": False,
            "valid": False,
            "fallback_valid": False,
            "status": "invalid",
            "expected": None,
            "actual": None,
            "error": str(exc),
        }


def is_acceptable_cedula(cedula: str) -> bool:
    """True when the cédula is Luhn-valid or an accepted fallback."""
    return validate_cedula_with_fallback(cedula)["accepted"]


def parse_cedula(raw: Any) -> dict[str, Any]:
    """Safe reader for scans/OCR input; never raises."""
    try:
        return validate_cedula_with_fallback("" if raw is None else str(raw))
    except Exception as exc:  # noqa: BLE001
        return {
            "accepted": False,
            "valid": False,
            "fallback_valid": False,
            "status": "invalid",
            "expected": None,
            "actual": None,
            "error": str(exc),
        }


def format_cedula(value: str | None) -> str:
    """Format digits as 3-3-3-2 (or 3-3-3-3 for 12 digits)."""
    digits = normalize_cedula(value)[:CEDULA_MAX_DIGITS]
    if len(digits) <= 3:
        return digits
    if len(digits) <= 7:
        return f"{digits[:3]}-{digits[3:]}"
    if len(digits) <= 10:
        return f"{digits[:3]}-{digits[3:7]}-{digits[7:]}"
    return f"{digits[:3]}-{digits[3:7]}-{digits[7:10]}-{digits[10:]}"


def mask_cedula(value: str | None) -> str:
    """Mask all but the last four digits."""
    digits = normalize_cedula(value)
    if len(digits) < 4:
        return digits
    return f"•••-•••-{digits[-4:]}"


def cedula_validation_error(value: str | None) -> str:
    """Return a human-readable validation message, or an empty string."""
    digits = normalize_cedula(value)
    if not digits:
        return "La cédula es requerida."
    if not is_valid_cedula(digits):
        return (
            f"La cédula debe tener entre {CEDULA_MIN_DIGITS} y "
            f"{CEDULA_MAX_DIGITS} dígitos."
        )
    return ""
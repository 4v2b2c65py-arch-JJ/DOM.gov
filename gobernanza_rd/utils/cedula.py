"""Cédula de Identidad y Electoral helpers.

Validation is based on digit count: 11 or 12 digits are accepted.
The standard Dominican format is 3-3-3-2 (e.g. 001-1234567-8).
"""

import re

CEDULA_MIN_DIGITS = 11
CEDULA_MAX_DIGITS = 12

_NON_DIGITS = re.compile(r"\D")


def normalize_cedula(value: str | None) -> str:
    """Return only the digits of a cédula."""
    return _NON_DIGITS.sub("", value or "")


def is_valid_cedula(value: str | None) -> bool:
    """True when the value has between 11 and 12 digits."""
    digits = normalize_cedula(value)
    return CEDULA_MIN_DIGITS <= len(digits) <= CEDULA_MAX_DIGITS


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
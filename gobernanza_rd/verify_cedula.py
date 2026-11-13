#!/usr/bin/env python3
"""Verify the local cédula cross-validator credential.

Usage:
    cd gobernanza_rd
    python3 verify_cedula.py
"""

import json

from utils.cedula_cross_validator import run_full_verification


def main() -> int:
    result = run_full_verification()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["deterministic"]["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
"""Cryptographic helpers for GobernanzaRD."""
import base64
import hashlib
import hmac
import secrets
from functools import lru_cache

from cryptography.fernet import Fernet

from config.settings import get_settings

settings = get_settings()


@lru_cache(maxsize=1)
def _fernet() -> Fernet:
    key = base64.urlsafe_b64encode(hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest())
    return Fernet(key)


def hash_string(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def verify_hash(value: str, hashed: str) -> bool:
    return hmac.compare_digest(hash_string(value), hashed)


def generate_token(nbytes: int = 32) -> str:
    return secrets.token_urlsafe(nbytes)


def encrypt_data(data: str) -> str:
    return _fernet().encrypt(data.encode("utf-8")).decode("ascii")


def decrypt_data(token: str) -> str:
    return _fernet().decrypt(token.encode("ascii")).decode("utf-8")
from utils.cedula import normalize_cedula, validate_cedula_with_fallback
from utils.crypto import decrypt_data, encrypt_data, generate_token, hash_string, verify_hash
from services.fraud_detection import FraudAction, FraudDetector


def test_crypto_roundtrip():
    token = generate_token(32)
    assert token
    assert verify_hash(token, hash_string(token))
    encrypted = encrypt_data("cedula-402-1235844-0")
    assert decrypt_data(encrypted) == "cedula-402-1235844-0"


def test_cedula_validation():
    assert normalize_cedula("402-1235844-0") == "40212358440"
    assert validate_cedula_with_fallback("402-1235844-0")["status"] == "valid"
    assert validate_cedula_with_fallback("402-0609352-7")["status"] == "fallback"
    assert validate_cedula_with_fallback("123")["status"] == "invalid"


async def test_rate_limit():
    detector = FraudDetector()
    first = await detector.check_rate_limit("ip", "magic_link", limit=1, window=300)
    second = await detector.check_rate_limit("ip", "magic_link", limit=1, window=300)
    assert first.allowed is True
    assert second.allowed is False


def test_fraud_action_enum():
    assert FraudAction.BLOCK_AND_INVESTIGATE.value == "block_and_investigate"


def test_app_imports():
    from app.main import app

    assert app is not None
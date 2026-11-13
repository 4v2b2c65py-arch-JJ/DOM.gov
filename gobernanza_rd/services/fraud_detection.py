"""Fraud detection, risk scoring, and rate limiting."""
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class FraudAction(str, Enum):
    ALLOW = "allow"
    CHALLENGE = "challenge"
    REQUIRE_MERIT_LINK = "require_merit_link"
    REQUIRE_BIOMETRIC = "require_biometric"
    BLOCK_AND_INVESTIGATE = "block_and_investigate"


@dataclass
class RiskScore:
    score: float
    action: FraudAction
    reasons: List[str] = field(default_factory=list)


@dataclass
class RateLimitResult:
    allowed: bool
    remaining: int
    retry_after: int = 0


def _to_float(value: Any) -> float:
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def _action_for_score(score: float) -> FraudAction:
    if score >= 1.0:
        return FraudAction.BLOCK_AND_INVESTIGATE
    if score >= 0.9:
        return FraudAction.REQUIRE_BIOMETRIC
    if score >= 0.7:
        return FraudAction.REQUIRE_MERIT_LINK
    if score >= 0.5:
        return FraudAction.CHALLENGE
    return FraudAction.ALLOW


class FraudDetector:
    """In-memory fraud heuristics and rate limiting."""

    def __init__(self) -> None:
        self._rate_limits: Dict[str, List[float]] = {}

    async def check_rate_limit(
        self, key: str, action: str, limit: int, window: int
    ) -> RateLimitResult:
        now = time.time()
        bucket = f"{action}:{key}"
        timestamps = [t for t in self._rate_limits.get(bucket, []) if now - t < window]
        allowed = len(timestamps) < limit
        if allowed:
            timestamps.append(now)
        self._rate_limits[bucket] = timestamps
        return RateLimitResult(allowed=allowed, remaining=max(0, limit - len(timestamps)))

    async def assess_payment_risk(
        self, user: Any, session: Any, payment_type: Any, auto_filled: Dict[str, Any]
    ) -> RiskScore:
        amount = _to_float(auto_filled.get("amount"))
        score = min(amount / 50000.0, 0.6)
        reasons: List[str] = []
        if amount > 10000:
            score = max(score, 0.75)
            reasons.append("high_amount")
        identity_level = getattr(getattr(user, "identity_level", None), "value", 0)
        if identity_level < 2:
            score = max(score, 0.55)
            reasons.append("low_identity")
        return RiskScore(score=round(score, 4), action=_action_for_score(score), reasons=reasons)

    async def assess_digital_wallet_payment(
        self, user: Any, session: Any, auto_filled: Dict[str, Any], wallet_type: str
    ) -> RiskScore:
        score = 0.1
        reasons: List[str] = []
        if wallet_type not in {"apple_pay", "google_pay"}:
            score = 0.8
            reasons.append("unsupported_wallet")
        if not auto_filled.get("_biometric_verified", False):
            score = max(score, 0.6)
            reasons.append("biometric_missing")
        return RiskScore(score=round(score, 4), action=_action_for_score(score), reasons=reasons)
"""Central AI Fund payment execution."""
import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Dict, Optional

import structlog

logger = structlog.get_logger()


@dataclass
class FundResult:
    success: bool
    amount: Decimal = Decimal("0")
    gov_responses: Dict[str, Any] = field(default_factory=dict)
    transaction_ids: Dict[str, str] = field(default_factory=dict)
    merit_earned: Decimal = Decimal("0")
    error_code: Optional[str] = None
    error_message: Optional[str] = None


def _amount_from(payment: Any, data: Dict[str, Any]) -> Decimal:
    value = data.get("amount")
    if value is None and hasattr(payment, "amount"):
        value = payment.amount
    try:
        return Decimal(str(value or "0"))
    except (TypeError, ValueError):
        return Decimal("0")


def _payment_type(payment: Any) -> str:
    value = getattr(payment, "payment_type", None)
    if value is None and isinstance(payment, dict):
        value = payment.get("payment_type")
    if value is None:
        return ""
    return str(getattr(value, "value", value))


class CentralAIFundExecutor:
    def __init__(self) -> None:
        self._merit_by_type = {
            "utility_electricity": Decimal("10"),
            "utility_water": Decimal("10"),
            "mutual_aid": Decimal("15"),
        }

    async def execute_payment(
        self, payment: Any, auto_filled: Optional[Dict[str, Any]] = None
    ) -> FundResult:
        data = auto_filled if auto_filled is not None else (payment if isinstance(payment, dict) else {})
        amount = _amount_from(payment, data)
        payment_type = _payment_type(payment)
        merit = self._merit_by_type.get(payment_type, Decimal("0"))
        return FundResult(
            success=True,
            amount=amount,
            gov_responses={},
            transaction_ids={"central_ai_fund": f"fund_{uuid.uuid4().hex[:16]}"},
            merit_earned=merit,
        )
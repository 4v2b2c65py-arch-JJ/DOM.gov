"""Merit earning and reward calculation."""
import uuid
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from models import MeritEventType, MeritTransaction, User

logger = structlog.get_logger()


@dataclass
class MeritReward:
    amount: Decimal
    reason: str


class MeritService:
    def __init__(self, db: Optional[AsyncSession] = None) -> None:
        self.db = db

    async def calculate_reward(self, user_id: uuid.UUID) -> MeritReward:
        amount = Decimal("25.00")
        reason = "Participacion verificada"
        if self.db is not None:
            try:
                user = await self.db.get(User, user_id)
                if user is not None:
                    score = Decimal(str(user.merit_score or 0))
                    if score >= 5000:
                        amount = Decimal("100.00")
                        reason = "Recompensa por alto puntaje de meritos"
                    elif score >= 1000:
                        amount = Decimal("50.00")
                        reason = "Recompensa por puntaje de meritos"
            except Exception as exc:
                logger.warning("merit_reward_lookup_failed", error=str(exc))
        return MeritReward(amount=amount, reason=reason)

    async def add_merits(
        self,
        user_id: uuid.UUID,
        event_type: MeritEventType,
        amount: Decimal,
        description: str,
        payment_id: Optional[uuid.UUID] = None,
        db: Optional[AsyncSession] = None,
    ) -> MeritTransaction:
        session = db or self.db
        if session is None:
            raise RuntimeError("MeritService requires a database session")

        user = await session.get(User, user_id)
        if user is None:
            raise ValueError(f"User {user_id} not found")

        amount = Decimal(str(amount))
        balance_before = Decimal(str(user.merit_score or 0))
        balance_after = balance_before + amount

        transaction = MeritTransaction(
            user_id=user_id,
            event_type=event_type,
            event_description=description,
            base_amount=amount,
            multiplier=Decimal("1.00"),
            bonus_amount=Decimal("0.00"),
            total_amount=amount,
            balance_before=balance_before,
            balance_after=balance_after,
            related_entity_type="payment" if payment_id else None,
            related_entity_id=payment_id,
            metadata={"source": "merit_service"},
            trace_id=f"merit_{uuid.uuid4().hex[:16]}",
            trace_hash="",
        )
        session.add(transaction)
        user.merit_score = balance_after
        user.total_merits_earned = Decimal(str(user.total_merits_earned or 0)) + amount
        await session.flush()
        return transaction
"""Mutual aid limit checks."""
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class MutualAidLimits:
    remaining: Decimal
    daily_limit: Decimal = Decimal("2000")
    used_today: Decimal = Decimal("0")


class MutualAidService:
    def __init__(self, db: Optional[AsyncSession] = None) -> None:
        self.db = db

    async def get_limits(self, user_id: Any) -> MutualAidLimits:
        return MutualAidLimits(remaining=Decimal("2000"))
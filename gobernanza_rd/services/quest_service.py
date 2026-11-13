"""Quest campaign lookups."""
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import IdentityLevel, Quest, QuestStatus, QuestVisit, User, UserStatus

logger = structlog.get_logger()


class QuestService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_active_quest(self, user_id: uuid.UUID) -> Optional[Quest]:
        result = await self.db.execute(
            select(Quest)
            .where(Quest.status == QuestStatus.ACTIVE)
            .order_by(Quest.start_date.desc())
        )
        quests = result.scalars().all()
        for quest in quests:
            if str(user_id) in (quest.assigned_questers or []):
                return quest
        return quests[0] if quests else None

    async def get_last_verified_location(self, cedula: str) -> Optional[Dict[str, Any]]:
        result = await self.db.execute(
            select(QuestVisit)
            .where(QuestVisit.gps_verified.is_(True))
            .order_by(QuestVisit.created_at.desc())
            .limit(1)
        )
        visit = result.scalar_one_or_none()
        if visit is None:
            return None
        return {
            "lat": float(visit.gps_lat) if visit.gps_lat is not None else None,
            "lng": float(visit.gps_lng) if visit.gps_lng is not None else None,
            "precision": visit.gps_accuracy or 5,
            "home_reference": visit.home_reference,
            "quest_verificador_id": str(visit.quester_id),
            "quest_verificacion_fecha": visit.created_at,
        }

    async def get_available_quester(
        self, territory: Optional[str] = None, date: Optional[datetime] = None
    ) -> Optional[User]:
        result = await self.db.execute(
            select(User)
            .where(
                User.status == UserStatus.ACTIVE,
                User.identity_level >= IdentityLevel.MERIT_LINKED,
            )
            .order_by(User.quest_participation_count.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def assign_nearest_quester(self, location: Any) -> Optional[User]:
        return await self.get_available_quester()
from collections.abc import Sequence
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Weight


class WeightRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_weight(self, data: dict[str, Any], user_uuid: UUID) -> Weight:
        weight = Weight(**data, user_uuid=user_uuid)
        self.session.add(weight)
        await self.session.flush()
        return weight

    async def get_weight(self, weight_id: int, user_uuid: UUID) -> Weight | None:
        result = await self.session.execute(
            select(Weight).where(Weight.id == weight_id, Weight.user_uuid == user_uuid)
        )
        return result.scalar_one_or_none()

    async def get_weights(self, user_uuid: UUID) -> Sequence[Weight]:
        result = await self.session.scalars(
            select(Weight).where(Weight.user_uuid == user_uuid)
        )
        return result.all()

    async def get_weights_count(self, user_uuid: UUID) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(Weight)
            .where(Weight.user_uuid == user_uuid)
        )
        return result.scalar_one()

    async def update_weight(self, weight: Weight, data: dict[str, Any]) -> Weight:
        for key, value in data.items():
            if hasattr(weight, key):
                setattr(weight, key, value)
        await self.session.flush()
        return weight

    async def delete_weight(self, weight: Weight) -> None:
        await self.session.delete(weight)
        await self.session.flush()

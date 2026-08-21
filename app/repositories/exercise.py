from collections.abc import Sequence
from typing import Any
from uuid import UUID

from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Exercise


class ExerciseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_exercise(self, data: dict[str, Any], user_uuid: UUID) -> Exercise:
        exercise = Exercise(**data, added_by=user_uuid)
        self.session.add(exercise)
        await self.session.flush()
        return exercise

    async def get_exercise_by_id(self, exercise_id: int) -> Exercise | None:
        result = await self.session.execute(
            select(Exercise).where(Exercise.id == exercise_id)
        )
        return result.scalar_one_or_none()

    async def get_exercises_by_ids(self, exercises_ids: set[int]) -> Sequence[Exercise]:
        result = await self.session.scalars(
            select(Exercise).where(Exercise.id.in_(exercises_ids))
        )
        return result.all()

    async def get_exercise_by_user_uuid(
        self, exercise_id: int, user_uuid: UUID
    ) -> Exercise | None:
        result = await self.session.execute(
            select(Exercise).where(
                Exercise.id == exercise_id, Exercise.added_by == user_uuid
            )
        )
        return result.scalar_one_or_none()

    async def get_exercises_by_name(self, exercise_name: str) -> Sequence[Exercise]:
        exercises = await self.session.scalars(
            select(Exercise).where(Exercise.name.ilike(f"%{exercise_name}%"))
        )
        return exercises.all()

    async def get_exercises_offset(self, limit: int, offset: int) -> Sequence[Exercise]:
        result = await self.session.scalars(
            select(Exercise)
            .order_by(Exercise.id.asc())
            .limit(limit=limit)
            .offset(offset=offset)
        )
        return result.all()

    async def get_exercises_ids(self, ids: list[int]) -> Sequence[int]:
        exercise_ids = await self.session.scalars(
            select(Exercise.id).where(Exercise.id.in_(ids))
        )
        return exercise_ids.all()

    async def get_user_added_exercises(self, user_uuid: UUID) -> int:
        result = await self.session.execute(
            select(func.count())
            .select_from(Exercise)
            .where(Exercise.added_by == user_uuid)
        )
        return result.scalar_one()

    async def check_exercise_exists(self, exercise_name: str) -> bool | None:
        result = await self.session.execute(
            select(exists(Exercise).where(Exercise.name == exercise_name))
        )
        return result.scalar()

    async def update_exercise(
        self, exercise: Exercise, data: dict[str, Any]
    ) -> Exercise:
        for key, value in data.items():
            if hasattr(exercise, key):
                setattr(exercise, key, value)
        await self.session.flush()
        return exercise

    async def delete_exercise(self, exercise: Exercise) -> None:
        await self.session.delete(exercise)
        await self.session.flush()

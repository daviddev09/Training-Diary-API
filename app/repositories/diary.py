from collections.abc import Sequence
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Circuit, CompletedExercise, Diary, TrainingDay


class DiaryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _update_util(self, obj: Any, data: dict[str, Any]) -> Any:
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

    async def create_diary(self, diary_data: dict[str, Any], user_uuid: UUID) -> Diary:
        diary = Diary(**diary_data, user_uuid=user_uuid)
        self.session.add(diary)
        await self.session.flush()
        return diary

    async def create_tr_day(
        self, tr_day_data: dict[str, Any], diary_id: int
    ) -> TrainingDay:
        tr_day = TrainingDay(**tr_day_data, diary_id=diary_id)
        self.session.add(tr_day)
        await self.session.flush()
        return tr_day

    async def create_circuit(self, data: dict[str, Any]) -> Circuit:
        circuit = Circuit(**data)
        self.session.add(circuit)
        await self.session.flush()
        return circuit

    async def create_compl_exercises(
        self, exercises_lst: list[dict[str, Any]], circuit_id: int
    ) -> list[CompletedExercise]:
        lst: list[CompletedExercise] = []
        for exercise in exercises_lst:
            compl_exercise = CompletedExercise(**exercise, circuit_id=circuit_id)
            lst.append(compl_exercise)

        self.session.add_all(lst)
        await self.session.flush()
        return lst

    async def get_full_diary(self, diary_id: int, user_uuid: UUID) -> Diary | None:
        result = await self.session.execute(
            select(Diary)
            .where(Diary.user_uuid == user_uuid, Diary.id == diary_id)
            .options(
                selectinload(Diary.training_days)
                .selectinload(TrainingDay.circuits)
                .selectinload(Circuit.exercises)
            )
        )
        return result.scalar_one_or_none()

    async def get_only_user_diaries(self, user_uuid: UUID) -> Sequence[Diary]:
        result = await self.session.scalars(
            select(Diary).where(Diary.user_uuid == user_uuid)
        )
        return result.all()

    async def get_diary_with_tr_days(
        self, diary_id: int, user_uuid: UUID
    ) -> Diary | None:
        result = await self.session.execute(
            select(Diary)
            .options(selectinload(Diary.training_days))
            .where(Diary.id == diary_id, Diary.user_uuid == user_uuid)
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def get_tr_day_with_circuits(
        self, tr_day_id: int, diary_id: int, user_uuid: UUID
    ) -> TrainingDay | None:
        result = await self.session.execute(
            select(TrainingDay)
            .join(TrainingDay.diary)
            .where(
                Diary.user_uuid == user_uuid,
                TrainingDay.diary_id == diary_id,
                TrainingDay.id == tr_day_id,
            )
            .options(selectinload(TrainingDay.circuits))
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def get_circuit_with_compl_exercises(
        self, tr_day_id: int, circuit_id: int, user_uuid: UUID
    ) -> Circuit | None:
        result = await self.session.execute(
            select(Circuit)
            .join(Circuit.training_day)
            .join(TrainingDay.diary)
            .where(
                Diary.user_uuid == user_uuid,
                Circuit.training_day_id == tr_day_id,
                Circuit.id == circuit_id,
            )
            .options(selectinload(Circuit.exercises))
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def get_diaries_count(self, user_uuid: UUID) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Diary).where(Diary.user_uuid == user_uuid)
        )
        return result.scalar_one()

    async def update_diary(self, diary: Diary, data: dict[str, Any]) -> Diary:
        updated_obj = self._update_util(diary, data)
        await self.session.flush()
        return updated_obj

    async def update_tr_day(
        self, tr_day: TrainingDay, data: dict[str, Any]
    ) -> TrainingDay:
        updated_obj = self._update_util(tr_day, data)
        await self.session.flush()
        return updated_obj

    async def update_compl_exercise(
        self, exercise: CompletedExercise, data: dict[str, Any]
    ) -> CompletedExercise:
        updated_obj = self._update_util(exercise, data)
        await self.session.flush()
        return updated_obj

    async def delete_diary(self, diary: Diary) -> None:
        await self.session.delete(diary)
        await self.session.flush()

    async def delete_tr_day(self, tr_day: TrainingDay) -> None:
        await self.session.delete(tr_day)
        await self.session.flush()

    async def delete_circuit(self, circuit: Circuit) -> None:
        await self.session.delete(circuit)
        await self.session.flush()

    async def delete_compl_exercise(self, exercise: CompletedExercise) -> None:
        await self.session.delete(exercise)
        await self.session.flush()

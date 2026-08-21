from typing import Any
from uuid import UUID

from app.core.languages import LanguageTemplate
from app.core.uow import UnitOfWork
from app.exceptions import (
    EmptyRequestedObject,
    EntityNotFound,
    ExercisesNotFound,
    LimitReached,
)
from app.schemes.training import (
    ComplExerciseCreate,
    ComplExerciseRead,
    ComplExerciseUpdate,
    DiaryCreate,
    DiaryRead,
    DiaryUpdate,
    OnlyCircuitRead,
    OnlyDiaryRead,
    OnlyTrainingDayRead,
    TrainingDayCreate,
    TrainingDayUpdate,
)


class DiaryService:
    def __init__(self, uow: UnitOfWork, lang: LanguageTemplate) -> None:
        self.uow = uow
        self.language = lang
        self.user_diary_limit = 3
        self.user_tr_day_limit = 90
        self.user_circuit_limit = 7
        self.user_exercise_limit = 14

    async def _check_diary_limit(self, user_uuid: UUID) -> None:
        user = await self.uow.user_repo.get_user_with_blocking(user_uuid)
        if not user:
            raise EntityNotFound(self.language.user_not_found)

        diaries_count = await self.uow.diary_repo.get_diaries_count(user_uuid)
        if diaries_count >= self.user_diary_limit:
            raise LimitReached(detail=self.language.user_diary_limit)

    def _check_tr_day_limit(self, diary: Any):
        if len(diary.training_days) >= self.user_tr_day_limit:
            raise LimitReached(detail=self.language.user_tr_days_limit)

    async def _check_circuit_limit_and_get_data(
        self, tr_day_id: int, diary_id: int, user_uuid: UUID
    ) -> dict[str, Any]:
        tr_day = await self.uow.diary_repo.get_tr_day_with_circuits(
            tr_day_id, diary_id, user_uuid
        )
        if not tr_day:
            raise EntityNotFound(detail=self.language.tr_day_not_found)

        if len(tr_day.circuits) >= self.user_circuit_limit:
            raise LimitReached(detail=self.language.user_circuits_limit)

        data: dict[str, Any] = {"training_day_id": tr_day_id}
        data.update(numberation=1) if not tr_day.circuits else data.update(
            numberation=tr_day.circuits[-1].numberation + 1
        )
        return data

    def _check_compl_exercise_limit_and_return_ids(
        self, circuit: Any, data: list[ComplExerciseCreate]
    ) -> list[int]:
        if circuit.exercises:
            if len(circuit.exercises) + len(data) > self.user_exercise_limit:
                raise LimitReached(detail=self.language.user_exercises_limit)
        if len(data) > self.user_exercise_limit:
            raise LimitReached(detail=self.language.user_exercises_limit)

        return [e.exercise_id for e in data]

    async def create_diary(self, user_uuid: UUID, data: DiaryCreate) -> OnlyDiaryRead:
        async with self.uow:
            await self._check_diary_limit(user_uuid)

            diary = await self.uow.diary_repo.create_diary(data.model_dump(), user_uuid)
            await self.uow.commit()
            return OnlyDiaryRead.model_validate(diary)

    async def create_tr_day(
        self, diary_id: int, user_uuid: UUID, data: TrainingDayCreate
    ) -> OnlyTrainingDayRead:
        async with self.uow:
            diary = await self.uow.diary_repo.get_diary_with_tr_days(
                diary_id, user_uuid
            )
            if not diary:
                raise EntityNotFound(detail=self.language.diary_not_found)

            self._check_tr_day_limit(diary)

            tr_day = await self.uow.diary_repo.create_tr_day(
                data.model_dump(), diary_id
            )

            await self.uow.commit()
            return OnlyTrainingDayRead.model_validate(tr_day)

    async def create_circuit(
        self, tr_day_id: int, diary_id: int, user_uuid: UUID
    ) -> OnlyCircuitRead:
        async with self.uow:
            data = await self._check_circuit_limit_and_get_data(
                tr_day_id, diary_id, user_uuid
            )

            circuit = await self.uow.diary_repo.create_circuit(data)
            await self.uow.commit()
            return OnlyCircuitRead.model_validate(circuit)

    async def create_compl_exercise(
        self,
        tr_day_id: int,
        circuit_id: int,
        user_uuid: UUID,
        data: list[ComplExerciseCreate],
    ) -> list[ComplExerciseRead]:
        async with self.uow:
            circuit = await self.uow.diary_repo.get_circuit_with_compl_exercises(
                tr_day_id, circuit_id, user_uuid
            )
            if not circuit:
                raise EntityNotFound(detail=self.language.circuit_not_found)

            ids = self._check_compl_exercise_limit_and_return_ids(circuit, data)
            exists_ids = await self.uow.exercise_repo.get_exercises_ids(ids)

            missing_ids = list(set(ids) - set(exists_ids))
            if missing_ids:
                raise ExercisesNotFound(
                    detail=self.language.exercise_not_found, missing_ids=missing_ids
                )

            dict_data_lst = [d.model_dump() for d in data]
            compl_exercises = await self.uow.diary_repo.create_compl_exercises(
                dict_data_lst, circuit_id
            )

            await self.uow.commit()
            return [
                ComplExerciseRead.model_validate(exercise)
                for exercise in compl_exercises
            ]

    async def create_diary_pdf(
        self, diary_id: int, user_uuid: UUID, user_email: str, user_name: str
    ) -> dict[str, str]:
        async with self.uow:
            diary = await self.uow.diary_repo.get_full_diary(diary_id, user_uuid)
            if not diary:
                raise EntityNotFound(detail=self.language.diary_not_found)
            if not diary.training_days:
                raise EmptyRequestedObject(detail=self.language.empty_diary)

            diary_dto = DiaryRead.model_validate(diary)
            self.uow.register_task(
                task_name="app.workers.pdf_worker.create_pdf_diary",
                user_email=user_email,
                user_name=user_name,
                user_uuid=str(user_uuid),
                diary=diary_dto.model_dump(),
            )
            await self.uow.commit()
            return {"message": f"{self.language.diary_pdf_file_creating} {user_email}"}

    async def get_user_diary(self, diary_id: int, user_uuid: UUID) -> DiaryRead:
        async with self.uow:
            diary = await self.uow.diary_repo.get_full_diary(diary_id, user_uuid)

            if not diary:
                raise EntityNotFound(detail=self.language.diary_not_found)

            return DiaryRead.model_validate(diary)

    async def get_user_diaries(self, user_uuid: UUID) -> list[OnlyDiaryRead]:
        async with self.uow:
            diaries = await self.uow.diary_repo.get_only_user_diaries(user_uuid)
            if not diaries:
                raise EntityNotFound(detail=self.language.diary_not_found)

            return [OnlyDiaryRead.model_validate(d) for d in diaries]

    async def update_diary(
        self, diary_id: int, user_uuid: UUID, data: DiaryUpdate
    ) -> OnlyDiaryRead:
        async with self.uow:
            diary = await self.uow.diary_repo.get_diary_with_tr_days(
                diary_id, user_uuid
            )
            if not diary:
                raise EntityNotFound(detail=self.language.diary_not_found)

            updated_diary = await self.uow.diary_repo.update_diary(
                diary, data.model_dump()
            )

            await self.uow.commit()
            return OnlyDiaryRead.model_validate(updated_diary)

    async def update_tr_day(
        self, tr_day_id: int, diary_id: int, user_uuid: UUID, data: TrainingDayUpdate
    ) -> OnlyTrainingDayRead:
        async with self.uow:
            tr_day = await self.uow.diary_repo.get_tr_day_with_circuits(
                tr_day_id, diary_id, user_uuid
            )
            if not tr_day:
                raise EntityNotFound(detail=self.language.tr_day_not_found)

            updated_tr_day = await self.uow.diary_repo.update_tr_day(
                tr_day, data.model_dump()
            )

            await self.uow.commit()
            return OnlyTrainingDayRead.model_validate(updated_tr_day)

    async def update_compl_exercise(
        self,
        compl_exercise_id: int,
        tr_day_id: int,
        circuit_id: int,
        user_uuid: UUID,
        data: ComplExerciseUpdate,
    ) -> ComplExerciseRead:

        async with self.uow:
            circuit = await self.uow.diary_repo.get_circuit_with_compl_exercises(
                tr_day_id, circuit_id, user_uuid
            )

            if not circuit:
                raise EntityNotFound(detail=self.language.circuit_not_found)
            if not circuit.exercises:
                raise EmptyRequestedObject(detail=self.language.empty_circuit)

            target_exercise = next(
                (e for e in circuit.exercises if e.id == compl_exercise_id), None
            )
            if not target_exercise:
                raise EntityNotFound(detail=self.language.exercise_not_found)

            updated_compl_exercise = await self.uow.diary_repo.update_compl_exercise(
                target_exercise, data.model_dump()
            )

            await self.uow.commit()
            return ComplExerciseRead.model_validate(updated_compl_exercise)

    async def delete_diary(self, diary_id: int, user_uuid: UUID) -> None:
        async with self.uow:
            diary = await self.uow.diary_repo.get_diary_with_tr_days(
                diary_id, user_uuid
            )
            if not diary:
                raise EntityNotFound(detail=self.language.diary_not_found)

            await self.uow.diary_repo.delete_diary(diary)
            await self.uow.commit()

    async def delete_tr_day(
        self, tr_day_id: int, diary_id: int, user_uuid: UUID
    ) -> None:
        async with self.uow:
            tr_day = await self.uow.diary_repo.get_tr_day_with_circuits(
                tr_day_id, diary_id, user_uuid
            )
            if not tr_day:
                raise EntityNotFound(detail=self.language.tr_day_not_found)

            await self.uow.diary_repo.delete_tr_day(tr_day)
            await self.uow.commit()

    async def delete_circuit(
        self, tr_day_id: int, circuit_id: int, user_uuid: UUID
    ) -> None:
        async with self.uow:
            circuit = await self.uow.diary_repo.get_circuit_with_compl_exercises(
                tr_day_id, circuit_id, user_uuid
            )
            if not circuit:
                raise EntityNotFound(detail=self.language.circuit_not_found)

            await self.uow.diary_repo.delete_circuit(circuit)
            await self.uow.commit()

    async def delete_compl_exercise(
        self, compl_exercise_id: int, tr_day_id: int, circuit_id: int, user_uuid: UUID
    ) -> None:
        async with self.uow:
            circuit = await self.uow.diary_repo.get_circuit_with_compl_exercises(
                tr_day_id, circuit_id, user_uuid
            )
            if not circuit:
                raise EntityNotFound(detail=self.language.circuit_not_found)
            if not circuit.exercises:
                raise EmptyRequestedObject(detail=self.language.empty_circuit)

            target_exercise = next(
                (e for e in circuit.exercises if e.id == compl_exercise_id), None
            )
            if not target_exercise:
                raise EntityNotFound(detail=self.language.exercise_not_found)

            await self.uow.diary_repo.delete_compl_exercise(target_exercise)
            await self.uow.commit()

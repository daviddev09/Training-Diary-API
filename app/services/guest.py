from datetime import datetime
from uuid import UUID, uuid4

from app.core.config import UserRole
from app.core.languages import LanguageTemplate
from app.core.security import create_guest_token
from app.core.uow import UnitOfWork
from app.exceptions import EmptyRequestedObject, EntityNotFound, LimitReached
from app.schemes.training import (
    CircuitRead,
    ComplExerciseCreate,
    ComplExerciseRead,
    DiaryRead,
    TrainingDayCreate,
    TrainingDayRead,
)


class GuestService:
    def __init__(self, uow: UnitOfWork, lang: LanguageTemplate) -> None:
        self.uow = uow
        self.language = lang
        self.guest_train_day_limit = 7
        self.guest_circuit_limit = 4
        self.guest_circuit_exercise_limit = 7

    def _validate_exists_diary(
        self, diary: DiaryRead | None, check_tr_days: bool = True
    ) -> DiaryRead:
        if not diary:
            raise EntityNotFound(detail=self.language.diary_not_found)

        if check_tr_days and not diary.training_days:
            raise EntityNotFound(detail=self.language.tr_day_not_found)

        return diary

    def _find_training_day(self, tr_day_id: int, diary: DiaryRead) -> TrainingDayRead:
        for tr_day in diary.training_days:
            if tr_day_id == tr_day.id:
                return tr_day
        raise EntityNotFound(detail=self.language.tr_day_not_found)

    def _find_day_circuit(
        self, circuit_id: int, tr_day: TrainingDayRead
    ) -> CircuitRead:
        for circuit in tr_day.circuits:
            if circuit_id == circuit.id:
                return circuit
        raise EntityNotFound(detail=self.language.circuit_not_found)

    def _find_circuite_exercise(
        self, exercise_id: int, circuit: CircuitRead
    ) -> ComplExerciseRead:
        if not circuit.exercises:
            raise EmptyRequestedObject(detail=self.language.empty_circuit)

        for exercise in circuit.exercises:
            if exercise.exercise_id == exercise_id:
                return exercise

        raise EntityNotFound(detail=self.language.exercise_not_found)

    def _create_guest_diary(self, diary_id: int, diary_name: str) -> DiaryRead:
        return DiaryRead(id=diary_id, diary_name=diary_name)

    def _create_training_day(
        self, day_id: int, data: TrainingDayCreate
    ) -> TrainingDayRead:
        day = TrainingDayRead(id=day_id)
        if data.date:
            day.date = data.date
        else:
            day.date = datetime.now()
        if data.difficulty:
            day.difficulty = data.difficulty
        if data.total_time_seconds:
            day.total_time_seconds = data.total_time_seconds
        return day

    def _create_circuit(self, numberation: int, circuit_id: int) -> CircuitRead:
        return CircuitRead(id=circuit_id, numberation=numberation)

    def _create_completed_exercise(
        self, data: ComplExerciseCreate
    ) -> ComplExerciseRead:
        exercise = ComplExerciseRead(exercise_id=data.exercise_id)
        if data.duration_seconds:
            exercise.duration_seconds = data.duration_seconds
        if data.reps:
            exercise.reps = data.reps
        if data.rest_seconds:
            exercise.rest_seconds = data.rest_seconds
        return exercise

    async def create_guest_diary(self, diary_name: str) -> tuple[DiaryRead, str]:
        async with self.uow:
            guest_uuid = uuid4()
            diary_id = 1

            diary = self._create_guest_diary(diary_id, diary_name)
            token = await create_guest_token(str(guest_uuid), role=UserRole.GUEST)

            await self.uow.guest_repo.create_guest(guest_uuid, diary)
            diary = await self.uow.guest_repo.get_guest_diary(guest_uuid)

            if not diary:
                raise EntityNotFound(detail=self.language.diary_not_found)

            return diary, token

    async def add_guest_training_day(
        self, guest_uuid: UUID, data: TrainingDayCreate
    ) -> DiaryRead:
        async with self.uow:
            raw_diary = await self.uow.guest_repo.get_guest_diary(guest_uuid)
            diary = self._validate_exists_diary(raw_diary, check_tr_days=False)
            day_id = 1

            if len(diary.training_days) >= self.guest_train_day_limit:
                raise LimitReached(detail=self.language.guest_tr_days_limit)

            if diary.training_days:
                day_id += diary.training_days[-1].id

            training_day = self._create_training_day(day_id, data)

            diary.training_days.append(training_day)
            await self.uow.guest_repo.update_guest_diary(guest_uuid, diary)
            return diary

    async def add_training_day_circuit(
        self, guest_uuid: UUID, tr_day_id: int
    ) -> DiaryRead:
        async with self.uow:
            raw_diary = await self.uow.guest_repo.get_guest_diary(guest_uuid)
            diary = self._validate_exists_diary(raw_diary)

            exists_tr_day = self._find_training_day(tr_day_id, diary)

            if len(exists_tr_day.circuits) >= self.guest_circuit_limit:
                raise LimitReached(detail=self.language.guest_circuits_limit)

            numberation = 1
            circuit_id = 1

            if exists_tr_day.circuits:
                numberation += exists_tr_day.circuits[-1].numberation
                circuit_id += exists_tr_day.circuits[-1].id

            circuit = self._create_circuit(numberation, circuit_id)
            exists_tr_day.circuits.append(circuit)
            await self.uow.guest_repo.update_guest_diary(guest_uuid, diary)
            return diary

    async def add_compl_exercise(
        self,
        guest_uuid: UUID,
        tr_day_id: int,
        circuit_id: int,
        data: ComplExerciseCreate,
    ) -> DiaryRead:
        async with self.uow:
            raw_diary = await self.uow.guest_repo.get_guest_diary(guest_uuid)
            diary = self._validate_exists_diary(raw_diary)
            exercise = await self.uow.exercise_repo.get_exercise_by_id(data.exercise_id)

            if not exercise:
                raise EntityNotFound(detail=self.language.exercise_not_found)

            exists_tr_day = self._find_training_day(tr_day_id, diary)
            exists_circuit = self._find_day_circuit(circuit_id, exists_tr_day)
            compl_exercise = self._create_completed_exercise(data)

            if len(exists_circuit.exercises) >= self.guest_circuit_exercise_limit:
                raise LimitReached(detail=self.language.guest_exercises_limit)

            exists_circuit.exercises.append(compl_exercise)
            await self.uow.guest_repo.update_guest_diary(guest_uuid, diary)
            return diary

    async def delete_training_day(self, guest_uuid: UUID, tr_day_id: int) -> None:
        async with self.uow:
            raw_diary = await self.uow.guest_repo.get_guest_diary(guest_uuid)
            diary = self._validate_exists_diary(raw_diary)

            exists_tr_day = self._find_training_day(tr_day_id, diary)
            diary.training_days.remove(exists_tr_day)

            await self.uow.guest_repo.update_guest_diary(guest_uuid, diary)

    async def delete_training_day_circuit(
        self, guest_uuid: UUID, tr_day_id: int, circuit_id: int
    ) -> None:
        async with self.uow:
            raw_diary = await self.uow.guest_repo.get_guest_diary(guest_uuid)
            diary = self._validate_exists_diary(raw_diary)

            tr_day = self._find_training_day(tr_day_id, diary)
            circuit = self._find_day_circuit(circuit_id, tr_day)

            tr_day.circuits.remove(circuit)
            await self.uow.guest_repo.update_guest_diary(guest_uuid, diary)

    async def delete_circuit_exercise(
        self, guest_uuid: UUID, tr_day_id: int, circuit_id: int, exercise_id: int
    ) -> None:
        async with self.uow:
            raw_diary = await self.uow.guest_repo.get_guest_diary(guest_uuid)
            diary = self._validate_exists_diary(raw_diary)

            exists_tr_day = self._find_training_day(tr_day_id, diary)
            exists_circuit = self._find_day_circuit(circuit_id, exists_tr_day)
            exists_exercise = self._find_circuite_exercise(exercise_id, exists_circuit)

            exists_circuit.exercises.remove(exists_exercise)

            await self.uow.guest_repo.update_guest_diary(guest_uuid, diary)

    async def get_guest_diary(self, guest_uuid: UUID) -> DiaryRead:
        async with self.uow:
            raw_diary = await self.uow.guest_repo.get_guest_diary(guest_uuid)
            diary = self._validate_exists_diary(raw_diary, check_tr_days=False)
            return diary

    async def delete_guest_diary(self, guest_uuid: UUID) -> None:
        async with self.uow:
            await self.uow.guest_repo.delete_guest_diary(guest_uuid)
            return

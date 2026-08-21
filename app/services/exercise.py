from uuid import UUID

from app.core.languages import LanguageTemplate
from app.core.uow import UnitOfWork
from app.exceptions import (
    EntityNotFound,
    LimitReached,
    UniqueError,
    UnprocessableContent,
)
from app.schemes.training import ExerciseCreate, ExerciseRead, ExerciseUpdate


class ExerciseService:
    def __init__(self, uow: UnitOfWork, lang: LanguageTemplate) -> None:
        self.uow = uow
        self.language = lang
        self.user_creating_exercise_limit = 10

    async def create_exercise(
        self, user_uuid: UUID, data: ExerciseCreate
    ) -> ExerciseRead:
        async with self.uow:
            user = await self.uow.user_repo.get_user_with_blocking(user_uuid)

            if not user:
                raise EntityNotFound(detail=self.language.user_not_found)
            if (
                await self.uow.exercise_repo.get_user_added_exercises(user_uuid)
                >= self.user_creating_exercise_limit
            ):
                raise LimitReached(detail=self.language.user_exercise_create_limit)
            if await self.uow.exercise_repo.check_exercise_exists(data.name):
                raise UniqueError(detail=self.language.exercise_name_is_in_use_error)

            exercise = await self.uow.exercise_repo.create_exercise(
                data.model_dump(), user_uuid
            )
            await self.uow.commit()
            return ExerciseRead.model_validate(exercise)

    async def get_exercises_by_name(self, exercise_name: str) -> list[ExerciseRead]:
        async with self.uow:
            exercises = await self.uow.exercise_repo.get_exercises_by_name(
                exercise_name
            )
            if not exercises:
                raise EntityNotFound(detail=self.language.exercise_not_found)

            return [ExerciseRead.model_validate(e) for e in exercises]

    async def get_exercise_by_id(self, exercise_id: int) -> ExerciseRead:
        async with self.uow:
            exercise = await self.uow.exercise_repo.get_exercise_by_id(exercise_id)
            if not exercise:
                raise EntityNotFound(detail=self.language.exercise_not_found)

            return ExerciseRead.model_validate(exercise)

    async def get_exercises_offset(self, page: int, size: int) -> list[ExerciseRead]:
        async with self.uow:
            if page < 1:
                raise UnprocessableContent(detail=self.language.unprocessable_content)

            offset = (page - 1) * size
            exercises = await self.uow.exercise_repo.get_exercises_offset(size, offset)
            if not exercises:
                raise EntityNotFound(detail=self.language.exercise_not_found)

            return [ExerciseRead.model_validate(e) for e in exercises]

    async def update_exercise(
        self, exercise_id: int, data: ExerciseUpdate, user_uuid: UUID | None = None
    ) -> ExerciseRead:
        async with self.uow:
            exercise = None
            if user_uuid:
                exercise = await self.uow.exercise_repo.get_exercise_by_user_uuid(
                    exercise_id, user_uuid
                )
            else:
                exercise = await self.uow.exercise_repo.get_exercise_by_id(exercise_id)
            if not exercise:
                raise EntityNotFound(detail=self.language.exercise_not_found)

            updated = await self.uow.exercise_repo.update_exercise(
                exercise, data.model_dump()
            )
            await self.uow.commit()
            return ExerciseRead.model_validate(updated)

    async def delete_exercise(self, exercise_id: int) -> None:
        async with self.uow:
            exercise = await self.uow.exercise_repo.get_exercise_by_id(exercise_id)
            if not exercise:
                raise EntityNotFound(detail=self.language.exercise_not_found)

            await self.uow.exercise_repo.delete_exercise(exercise)
            await self.uow.commit()

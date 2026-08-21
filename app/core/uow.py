from typing import Any

from app.core.database import AsyncSessionLocal, guest_redis, validate_redis
from app.repositories.cache import ValidateCacheRepository
from app.repositories.diary import DiaryRepository
from app.repositories.exercise import ExerciseRepository
from app.repositories.guest import GuestRepository
from app.repositories.session import SessionRepository
from app.repositories.user import UserRepository
from app.repositories.weight import WeightRepository


class UnitOfWork:
    def __init__(
        self,
        session_factory: Any = AsyncSessionLocal,
        redis_validate: Any = validate_redis,
        redis_guest: Any = guest_redis,
    ) -> None:
        self.session_factory = session_factory
        self.redis_validate = redis_validate
        self.redis_guest = redis_guest
        self.tasks_to_run: list[dict[str, Any]] = []

    async def __aenter__(self) -> None:
        self.session = self.session_factory()
        self.user_repo = UserRepository(self.session)
        self.diary_repo = DiaryRepository(self.session)
        self.exercise_repo = ExerciseRepository(self.session)
        self.weight_repo = WeightRepository(self.session)
        self.session_repo = SessionRepository(self.session)
        self.validate_repo = ValidateCacheRepository(self.redis_validate)

        self.guest_repo = GuestRepository(self.redis_guest)

    def register_task(self, task_name: str, **kwargs: Any) -> None:
        task: dict[str, Any] = {"task_name": task_name, "kwargs": kwargs}
        self.tasks_to_run.append(task)

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        if exc_type is not None:
            await self.session.rollback()

        self.tasks_to_run.clear()
        await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()
        from app.workers.celery_app import app

        for task in self.tasks_to_run:
            app.send_task(task["task_name"], kwargs=task["kwargs"])  # type: ignore
        self.tasks_to_run.clear()

    async def rollback(self) -> None:
        await self.session.rollback()
        self.tasks_to_run.clear()

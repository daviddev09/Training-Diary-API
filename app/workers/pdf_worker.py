import asyncio
from typing import Any

from celery import Task

from app.schemes.training import DiaryRead
from app.workers.celery_app import app
from app.workers.smtp_worker import send_notification_about_pdf
from app.workers.utils.pdf_util import create_diary_pdf_util


@app.task(
    name="app.workers.pdf_worker.create_pdf_diary",
    bind=True,
    max_retries=10,
    default_retry_delay=360,
)  # type: ignore
def create_pdf_diary(
    self: Task, user_email: str, user_name: str, user_uuid: str, diary: dict[str, Any]
) -> None:
    async def get_exercise_ids(diary_dto: DiaryRead) -> dict[int, str] | None:
        from app.core.uow import UnitOfWork

        uow = UnitOfWork()
        exercises_ids: set[int] = set()
        if diary_dto.training_days:
            for training_day in diary_dto.training_days:
                if training_day.circuits:
                    for circuit in training_day.circuits:
                        if circuit.exercises:
                            for exercise in circuit.exercises:
                                exercises_ids.add(exercise.exercise_id)
        async with uow:
            if exercises_ids:
                exercises = await uow.exercise_repo.get_exercises_by_ids(exercises_ids)
                return {ex.id: ex.name for ex in exercises}

    try:
        diary_dto = DiaryRead.model_validate(diary)
        exercises = asyncio.run(get_exercise_ids(diary_dto))
        pdf_link = create_diary_pdf_util(user_uuid, diary_dto, exercises)
        send_notification_about_pdf.delay(user_email, user_name, pdf_link)  # type: ignore
    except Exception as exc:
        print(f"\nFail: {exc}")
        self.retry(exc=exc)

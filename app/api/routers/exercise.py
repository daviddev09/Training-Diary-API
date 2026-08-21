from fastapi import APIRouter, Depends

from app.api.dependencies import (
    get_admin_or_higher_user,
    get_current_user,
    get_exercise_service,
)
from app.models import User
from app.schemes.training import ExerciseCreate, ExerciseRead, ExerciseUpdate
from app.services.exercise import ExerciseService

router = APIRouter(prefix="/exercises", tags=["Exercises"])


@router.post("")
async def create_exercise(
    data: ExerciseCreate,
    user: User = Depends(get_current_user),
    service: ExerciseService = Depends(get_exercise_service),
) -> ExerciseRead:
    """
    # Создаёт кастомное упражнение пользователя.
    ## Важно:
    * **Упражнения созданные пользователем будут видны всем и могут быть использованы всеми**.
    * **После создания упражнения пользователь не сможет удалить его**.
    * **Лимит создаваемых кастомных упражнений 10 на одного пользователя**.
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **403 Forbidden** - достигнут лимит создания упражнений.
    * **404 Not Found** - пользователь не найден.
    * **409 Conflict** - имя создавоемого упражнения уже используется.
    """
    return await service.create_exercise(user.uuid, data)


@router.get("/{exercise_id}")
async def get_exercise(
    exercise_id: int, service: ExerciseService = Depends(get_exercise_service)
) -> ExerciseRead:
    """
    # Получает упражнение по ID.
    ## Возможная ошибка:
    * **404 Not Found** - упражнение не найдено.
    """
    return await service.get_exercise_by_id(exercise_id)


@router.get("/page/{page}")
async def get_exercises_offset_paginated(
    page: int = 1,
    page_size: int = 20,
    service: ExerciseService = Depends(get_exercise_service),
) -> list[ExerciseRead]:
    """
    # Получает упражнения по offset-пагинации.
    ## Возможные ошибки:
    * **404 Not Found** - упражнения не найдены.
    * **422 Unprocessable Content** - в параметр page передан число меньше 1
    """
    return await service.get_exercises_offset(page, page_size)


@router.get("")
async def search_exercises_by_iname(
    exercise_name: str, service: ExerciseService = Depends(get_exercise_service)
) -> list[ExerciseRead]:
    """
    # Ищет упражнения по названию без ограничения регистра (Ilike) и возвращает список упражнений.
    ## Возможная ошибка:
    * **404 Not Found** - упражнения не найдены.
    """
    return await service.get_exercises_by_name(exercise_name)


@router.patch("/{exercise_id}")
async def update_exercise(
    exercise_id: int,
    data: ExerciseUpdate,
    user: User = Depends(get_current_user),
    service: ExerciseService = Depends(get_exercise_service),
) -> ExerciseRead:
    """
    # Обновляет упражнение созданное пользователем.
    ## Обновить упражнение может только владелец и только своё упражнение.
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **404 Not Found** - пользователь или упражнение не найдены.
    """
    return await service.update_exercise(exercise_id, data, user.uuid)


@router.patch("/admin/{exercise_id}")
async def admin_update_exercise(
    exercise_id: int,
    data: ExerciseUpdate,
    _: User = Depends(get_admin_or_higher_user),
    service: ExerciseService = Depends(get_exercise_service),
) -> ExerciseRead:
    """
    # Обновляет любое упражнение, созданное любым пользователем в системе.
    ## Использовать могут только: админы или owner.
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **404 Not Found** - пользователь или упражнение не найдены.
    """
    return await service.update_exercise(exercise_id, data)


@router.delete("/admin/{exercise_id}")
async def delete_exercise(
    exercise_id: int,
    _: User = Depends(get_admin_or_higher_user),
    service: ExerciseService = Depends(get_exercise_service),
) -> None:
    """
    # Удаляет любое упражнение, созданное любым пользователем в системе.
    ## Использовать могут только: админы или owner.
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **404 Not Found** - пользователь или упражнение не найдены.
    """
    return await service.delete_exercise(exercise_id)

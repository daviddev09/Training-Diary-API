from uuid import UUID

from fastapi import APIRouter, Depends, Response

from app.api.dependencies import get_current_guest, get_guest_service, verify_no_guest
from app.schemes.training import (
    ComplExerciseCreate,
    DiaryCreate,
    DiaryRead,
    TrainingDayCreate,
)
from app.services.guest import GuestService

router = APIRouter(prefix="/guest", tags=["Guest"])


@router.post("/diary")
async def create_guest_diary(
    data: DiaryCreate,
    response: Response,
    service: GuestService = Depends(get_guest_service),
    _: None = Depends(verify_no_guest),
) -> DiaryRead:
    """
    # Создаёт гостевой дневник и гостевой токен.
    ## Важно:
    * **У гостя может быть только 1 дневник**.
    * **После создания дневника гость не может изменить дневник и его связанные данные**.
    * **Профиль гостя (Дневник) хранится в кэше 7 дней после чего удаляется**.
    * **По одному IP на этот эндпоинт можно обращаться раз в час, защищён с помощью Rate Limiting.**
    ## Возможные ошибки:
    * **403 Forbidden** - достигнут лимит создания гостевого дневника.
    * **404 Not Found** - гостевой дневник не найден.
    """
    diary, token = await service.create_guest_diary(data.diary_name)

    response.set_cookie(
        key="guest",
        value=token,
        max_age=604800,
        path="/",
        httponly=True,
        samesite="lax",
        secure=False,
    )
    return diary


@router.post("/diary/training-day")
async def add_training_day(
    data: TrainingDayCreate,
    guest_uuid: UUID = Depends(get_current_guest),
    service: GuestService = Depends(get_guest_service),
) -> DiaryRead:
    """
    # Создаёт день тренировки и добавляет в гостевой дневник.
    ## Возможные ошибки:
    * **401 Unauthorized** - гостевой токен не передан или невалиден
    * **403 Forbidden** - достигнут лимит создания дней тренировок.
    * **404 Not Found** - гостевой дневник не найден.
    """
    return await service.add_guest_training_day(guest_uuid, data)


@router.post("/diary/training-day/{training_day_id}/circuit")
async def add_circuit(
    training_day_id: int,
    guest_uuid: UUID = Depends(get_current_guest),
    service: GuestService = Depends(get_guest_service),
) -> DiaryRead:
    """
    # Создаёт круг (цикл) упражнений и добавляет в день тренировки.
    ## Возможные ошибки:
    * **401 Unauthorized** - гостевой токен не передан или невалиден
    * **403 Forbidden** - достигнут лимит создания кругов.
    * **404 Not Found** - гостевой дневник или день тренировки не найден.
    """
    return await service.add_training_day_circuit(guest_uuid, training_day_id)


@router.post("/diary/training-day/{training_day_id}/circuit/{circuit_id}/exercise")
async def add_completed_exercise(
    training_day_id: int,
    circuit_id: int,
    data: ComplExerciseCreate,
    guest_uuid: UUID = Depends(get_current_guest),
    service: GuestService = Depends(get_guest_service),
) -> DiaryRead:
    """
    # создаёт и добавляет выполненное упражнение в круг.
    ## Возможные ошибки:
    * **400 Bad Request** - круг по введённому ID пуст.
    * **401 Unauthorized** - гостевой токен не передан или невалиден
    * **403 Forbidden** - достигнут лимит создания выполненных упражнений.
    * **404 Not Found** - гостевой дневник, день тренировки или круг не найдены.
    """
    return await service.add_compl_exercise(
        guest_uuid, training_day_id, circuit_id, data
    )


@router.get("/diary")
async def get_guest_diary(
    guest_uuid: UUID = Depends(get_current_guest),
    service: GuestService = Depends(get_guest_service),
) -> DiaryRead:
    """
    # Получает гостевой дневник целиком.
    ## Возможные ошибки:
    * **401 Unauthorized** - гостевой токен не передан или невалиден
    * **404 Not Found** - гостевой дневник не найден.
    """
    return await service.get_guest_diary(guest_uuid)


@router.delete("/diary")
async def delete_guest_diary(
    response: Response,
    guest_uuid: UUID = Depends(get_current_guest),
    service: GuestService = Depends(get_guest_service),
) -> None:
    """
    # Удаляет гостевой дневник целиком со всеми дочерними данными.
    ## Возможные ошибки:
    * **401 Unauthorized** - гостевой токен не передан или невалиден
    """
    await service.delete_guest_diary(guest_uuid)
    response.delete_cookie(
        key="guest", path="/", httponly=True, samesite="lax", secure=False
    )


@router.delete("/diary/training-day/{training_day_id}")
async def delete_training_day(
    training_day_id: int,
    guest_uuid: UUID = Depends(get_current_guest),
    service: GuestService = Depends(get_guest_service),
) -> None:
    """
    # Удаляет день тренировки целиком со всеми дочерними данными.
    ## Возможные ошибки:
    * **401 Unauthorized** - гостевой токен не передан или невалиден
    * **404 Not Found** - гостевой дневник или день тренировки не найден.
    """
    return await service.delete_training_day(guest_uuid, training_day_id)


@router.delete("/diary/training-day/{training_day_id}/circuit/{circuit_id}")
async def delete_circuit(
    training_day_id: int,
    circuit_id: int,
    guest_uuid: UUID = Depends(get_current_guest),
    service: GuestService = Depends(get_guest_service),
) -> None:
    """
    # Удаляет круг (цикл) упражнений целиком со всеми дочерними данными.
    ## Возможные ошибки:
    * **401 Unauthorized** - гостевой токен не передан или невалиден
    * **404 Not Found** - гостевой дневник, день тренировки или круг не найдены.
    """
    return await service.delete_training_day_circuit(
        guest_uuid, training_day_id, circuit_id
    )


@router.delete(
    "/diary/training-day/{training_day_id}/circuit/{circuit_id}/exercise/{exercise_id}"
)
async def delete_exercise(
    training_day_id: int,
    circuit_id: int,
    exercise_id: int,
    guest_uuid: UUID = Depends(get_current_guest),
    service: GuestService = Depends(get_guest_service),
) -> None:
    """
    # Удаляет выполненное упражнение из круга (цикла).
    ## Возможные ошибки:
    * **400 Bad Request** - круг по введённому ID пуст.
    * **401 Unauthorized** - гостевой токен не передан или невалиден
    * **404 Not Found** - гостевой дневник, день тренировки, круг или упражнение не найдены.
    """
    return await service.delete_circuit_exercise(
        guest_uuid, training_day_id, circuit_id, exercise_id
    )

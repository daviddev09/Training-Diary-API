from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, get_diary_service
from app.models import User
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
from app.services.diary import DiaryService

router = APIRouter(prefix="/diaries", tags=["Diaries"])


@router.get("/{diary_id}")
async def get_my_diary(
    diary_id: int,
    _: User = Depends(get_current_user),
    service: DiaryService = Depends(get_diary_service),
) -> DiaryRead:
    """
    # Возвращает дневник пользователя целиком, со всеми днями, кругами и упражнениями
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **404 Not Found** - пользователь или дневник не найден.
    """
    return await service.get_user_diary(diary_id, _.uuid)


@router.get("")
async def get_my_diaries(
    user: User = Depends(get_current_user),
    service: DiaryService = Depends(get_diary_service),
) -> list[OnlyDiaryRead]:
    """
    # Возвращает все дневники пользователя без связанных данных.
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **404 Not Found** - пользователь или дневник не найден.
    """
    return await service.get_user_diaries(user.uuid)


@router.post("")
async def create_diary(
    data: DiaryCreate,
    user: User = Depends(get_current_user),
    service: DiaryService = Depends(get_diary_service),
) -> OnlyDiaryRead:
    """
    # Создаёт дневник и возвращает его.
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **404 Not Found** - пользователь не найден.
    * **403 Forbidden** - запрещено из-за ограничения лимита.
    """
    return await service.create_diary(user.uuid, data)


@router.post("/{diary_id}/training-day")
async def create_training_day(
    data: TrainingDayCreate,
    diary_id: int,
    user: User = Depends(get_current_user),
    service: DiaryService = Depends(get_diary_service),
) -> OnlyTrainingDayRead:
    """
    # Создаёт день тренировки и добавляет его в дневник по ID.
    ## Правила ввода:
    * Формат дня нужно писать: **YY-MM-DD H:M:S**.
    * Difficulty должен быть только один из трёх вариантов: **easy**, **medium**, **hard**.
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **404 Not Found** - пользователь или дневник не найден.
    * **403 Forbidden** - запрещено из-за ограничения лимита.
    """
    return await service.create_tr_day(diary_id, user.uuid, data)


@router.post("/{diary_id}/days/{training_day_id}")
async def create_circuit(
    diary_id: int,
    training_day_id: int,
    user: User = Depends(get_current_user),
    service: DiaryService = Depends(get_diary_service),
) -> OnlyCircuitRead:
    """
    # Создаёт круг (цикл) упражнений и добавляет в тренировочный день.
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **404 Not Found** - пользователь или день тренировки не найден.
    * **403 Forbidden** - запрещено из-за ограничения лимита.
    """
    return await service.create_circuit(training_day_id, diary_id, user.uuid)


@router.post("/days/{training_day_id}/circuits/{circuit_id}/exercise")
async def add_completed_exercise(
    training_day_id: int,
    circuit_id: int,
    data: list[ComplExerciseCreate],
    user: User = Depends(get_current_user),
    service: DiaryService = Depends(get_diary_service),
) -> list[ComplExerciseRead]:
    """
    # Создаёт запись выполненных упражнений и добавляет в круг.
    ## ID упражнений которые не были найдены возвращает списком.
    ## Правила ввода:
    * **Чтобы не тратить производительность нужно передать все упражнения в одном запросе**.
    * **Можно добавлять повторение или секунды удержания, в зависимости от типа упражнения**.
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **404 Not Found** - пользователь, день тренировки, круг или упражнения не найдены.
    * **403 Forbidden** - запрещено из-за ограничения лимита.
    """
    return await service.create_compl_exercise(
        training_day_id, circuit_id, user.uuid, data
    )


@router.patch("/{diary_id}")
async def update_diary(
    diary_id: int,
    data: DiaryUpdate,
    user: User = Depends(get_current_user),
    service: DiaryService = Depends(get_diary_service),
) -> OnlyDiaryRead:
    """
    # Обновляет название дневника
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **404 Not Found** - пользователь или дневник не найден.
    """
    return await service.update_diary(diary_id, user.uuid, data)


@router.patch("/{diary_id}/days/{training_day_id}")
async def update_training_day(
    diary_id: int,
    training_day_id: int,
    data: TrainingDayUpdate,
    user: User = Depends(get_current_user),
    service: DiaryService = Depends(get_diary_service),
) -> OnlyTrainingDayRead:
    """
    # Обновляет день тренировки.
    ## Правила ввода:
    * Формат дня нужно писать: **YY-MM-DD H:M:S**.
    * Difficulty должен быть только один из трёх вариантов: **easy**, **medium**, **hard**.
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **404 Not Found** - пользователь или день тренировки не найден.
    """
    return await service.update_tr_day(training_day_id, diary_id, user.uuid, data)


@router.patch(
    "/days/{training_day_id}/circuits/{circuit_id}/exercises/{completed_exercise_id}"
)
async def update_completed_exercise(
    training_day_id: int,
    circuit_id: int,
    completed_exercise_id: int,
    data: ComplExerciseUpdate,
    user: User = Depends(get_current_user),
    service: DiaryService = Depends(get_diary_service),
) -> ComplExerciseRead:
    """
    # Обновляет запись выполненного упражнения.
    ## Правило ввода:
    * **Можно добавлять повторение или секунды удержания, в зависимости от типа упражнения**.
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **404 Not Found** - пользователь, круг или упражнение не найдены.
    * **403 Forbidden** - запрещено из-за ограничения лимита.
    * **400 Bad Request** - Круг тренировки по введённому ID пуст
    """
    return await service.update_compl_exercise(
        completed_exercise_id, training_day_id, circuit_id, user.uuid, data
    )


@router.delete("/{diary_id}")
async def delete_diary(
    diary_id: int,
    user: User = Depends(get_current_user),
    service: DiaryService = Depends(get_diary_service),
) -> None:
    """
    # Удаляет дневник
    ## **Важно**: при удалении дневника удалятся все его дочерние связанные данные (дни тренировок, круги и выполненные упражнения).
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **404 Not Found** - пользователь или дневник не найден.
    """
    return await service.delete_diary(diary_id, user.uuid)


@router.delete("/{diary_id}/days/{training_day_id}")
async def delete_training_day(
    diary_id: int,
    training_day_id: int,
    user: User = Depends(get_current_user),
    service: DiaryService = Depends(get_diary_service),
) -> None:
    """
    # Удаляет день тренировки
    ## **Важно**: при удалении дня тренировки удалятся все его дочерние связанные данные (круги и выполненные упражнения).
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **404 Not Found** - пользователь или день тренировки не найден.
    """
    return await service.delete_tr_day(training_day_id, diary_id, user.uuid)


@router.delete("/days/{training_day_id}/circuits/{circuit_id}")
async def delete_circuit(
    training_day_id: int,
    circuit_id: int,
    user: User = Depends(get_current_user),
    service: DiaryService = Depends(get_diary_service),
) -> None:
    """
    # Удаляет круг (цикл) упражнений
    ## **Важно**: при удалении круга удалятся все его дочерние связанные данные (выполненные упражнения).
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **404 Not Found** - пользователь или круг не найден.
    """
    return await service.delete_circuit(training_day_id, circuit_id, user.uuid)


@router.delete(
    "/days/{training_day_id}/circuits/{circuit_id}/exercises/{completed_exercise_id}"
)
async def delete_completed_exercise(
    training_day_id: int,
    circuit_id: int,
    completed_exercise_id: int,
    user: User = Depends(get_current_user),
    service: DiaryService = Depends(get_diary_service),
) -> None:
    """
    # Удаляет выполненное упражнение
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **404 Not Found** - пользователь, круг или выполненное упражнение не найдено.
    * **400 Bad Request**- круг тренировки по введённому ID пуст
    """
    return await service.delete_compl_exercise(
        completed_exercise_id, training_day_id, circuit_id, user.uuid
    )

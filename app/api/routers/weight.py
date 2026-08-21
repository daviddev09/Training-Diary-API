from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, get_weight_service
from app.models import User
from app.schemes.user import WeightCreate, WeightRead, WeightUpdate
from app.services.weight import WeightService

router = APIRouter(prefix="/weights", tags=["Weights"])


@router.post("")
async def add_weight(
    data: WeightCreate,
    user: User = Depends(get_current_user),
    service: WeightService = Depends(get_weight_service),
) -> WeightRead:
    """
    # Создаёт запись о весе пользователя.
    ## Лимит добавления весов 10
    ## Правила ввода:
    * **Формат ввода веса:** *kg.grams*.
    * **Формат ввода даты:** *YY-MM-DD H:M:S*.
    ## Если не ввести дату, приложение само добавит её.
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **404 Not Found** - пользователь не найден.
    * **403 Forbidden** - достигнут лимит добавления весов
    """
    return await service.create_weight(user.uuid, data)


@router.get("/{weight_id}")
async def get_weight(
    weight_id: int,
    user: User = Depends(get_current_user),
    service: WeightService = Depends(get_weight_service),
) -> WeightRead:
    """
    # Получает запись о весе пользователя по ID.
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **404 Not Found** - пользователь или вес не найден.
    """
    return await service.get_user_weight(weight_id, user.uuid)


@router.get("")
async def get_weights(
    user: User = Depends(get_current_user),
    service: WeightService = Depends(get_weight_service),
) -> list[WeightRead]:
    """
    # Получает все записи о весе пользователя.
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **404 Not Found** - пользователь или веса не найдены.
    """
    return await service.get_user_weights(user.uuid)


@router.patch("/{weight_id}")
async def update_weight(
    weight_id: int,
    data: WeightUpdate,
    user: User = Depends(get_current_user),
    service: WeightService = Depends(get_weight_service),
) -> WeightRead:
    """
    # Обновляет запись о весе пользователя.
    ## Правила ввода:
    * **Формат ввода веса:** *kg.grams*.
    * **Формат ввода даты:** *YY-MM-DD H:M:S*.
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **404 Not Found** - пользователь или вес не найден.
    """
    return await service.update_weight(weight_id, user.uuid, data)


@router.delete("/{weight_id}")
async def delete_weight(
    weight_id: int,
    user: User = Depends(get_current_user),
    service: WeightService = Depends(get_weight_service),
) -> None:
    """
    # Удаляет запись о весе пользователя.
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **404 Not Found** - пользователь или вес не найден.
    """
    return await service.delete_weight(weight_id, user.uuid)

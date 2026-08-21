from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user, get_user_service
from app.models import User
from app.schemes.user import UserRead, UserUpdate
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("")
async def get_me(
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserRead:
    """
    # Получает данные профиля текущего пользователя
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден
    * **404 Not Found** - пользователь не найден
    """
    return await service.get_user(user.uuid)


@router.patch("")
async def update_me(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> UserRead:
    """
    # Обновляет профиль текущего пользователя.
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **404 Not Found** - пользователь не найден.
    * **409 Conflict** - имя пользователя уже занято.
    """
    return await service.update_user(user.uuid, data)


@router.delete("")
async def delete_me(
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
) -> None:
    """
    # Удаляет профиль текущего пользователя.
    ## Важно:
    * **После удаления пользователя удалятся все его дневники со связанными с ними данными и веса,
    а созданные им упражнения останутся без uuid создателя и не будут никому принадлежать**
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **404 Not Found** - пользователь не найден.
    """
    return await service.delete_user(user.uuid)

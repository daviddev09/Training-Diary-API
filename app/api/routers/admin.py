from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.dependencies import (
    get_admin_or_higher_user,
    get_owner_user,
    get_user_service,
)
from app.models import User
from app.schemes.user import UserRead
from app.services.user import UserService

router = APIRouter(prefix="/admin", tags=["Administration"])


@router.get("/users/page/{page}")
async def get_users_offset_paginated(
    page: int = 1,
    page_size: int = 20,
    _: User = Depends(get_admin_or_higher_user),
    service: UserService = Depends(get_user_service),
) -> list[UserRead]:
    """
    # Получает пользователей по offset-пагинации.
    ## Требует: Роль админа или выше.
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **403 Forbidden** - запрещается пользователям с ролью **user**.
    * **422 Unprocessable Content** - передан 0 в параметр page.
    * **404 Not Found** - пользователи не найдены
    """
    return await service.get_users_offset(page, page_size)


@router.patch("/grant")
async def grant_admin_rights(
    user_uuid: UUID,
    _: User = Depends(get_owner_user),
    service: UserService = Depends(get_user_service),
) -> UserRead:
    """
    # Повышает роль пользователя с user на admin.
    ## Требует: Роль ownera.
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **403 Forbidden** - запрещается пользователям чья роль ниже owner.
    * **404 Not Found** - пользователь не найден
    """
    return await service.give_admin_role(user_uuid)


@router.patch("/revoke")
async def revoke_admin_rights(
    user_uuid: UUID,
    _: User = Depends(get_owner_user),
    service: UserService = Depends(get_user_service),
) -> UserRead:
    """
    # Понижает роль пользователя с admin на user.
    ## Требует: Роль ownera.
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **403 Forbidden** - запрещается пользователям чья роль ниже owner.
    * **404 Not Found** - пользователь не найден
    """
    return await service.revoke_admin_role(user_uuid)


@router.delete("/user")
async def delete_user(
    user_uuid: UUID,
    _: User = Depends(get_admin_or_higher_user),
    service: UserService = Depends(get_user_service),
) -> None:
    """
    # Удаляет пользователя.
    ## Требует роль: owner или admin
    ## Важно: admin не может удалить другого админа а также ownera.
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **403 Forbidden** - запрещается пользователям чья роль ниже owner.
    * **403 Forbidden** - запрещается удалить пользователя чья роль равно или выше того кто удаляет.
    * **404 Not Found** - пользователь не найден
    """

    return await service.delete_user_by_admin_or_owner(user_uuid, _.role)

from uuid import UUID

from fastapi import APIRouter, Cookie, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import (
    auth_verify_no_guest,
    get_auth_service,
    get_current_user,
)
from app.core.security import set_refresh_cookie
from app.models import User
from app.schemes.user import UserCreate, UserRead
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authorization"])


@router.post("/register")
async def register(
    data: UserCreate,
    guest_uuid: UUID | None = Depends(auth_verify_no_guest),
    service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    """
    # Берёт данные пользователя и добавляет в кеш с TTL 60 секунд.
    ## Генерирует 4-значный код верификации с TTL 60 секунд и в фоне отправляет в почту регистрируемого пользователя.
    ## Если у регистрируемого был гостевой дневник, берёт его данные и прикрепляет к нему
    ## Важно:
    * **Эндпоинт защищён с помощью Rate Limiting и с одного IP можно обращаться 5 раз в минуту, рекомендуется вводить правильные данные чтобы не тратить попытки.**
    ## Возможные ошибки:
    * **409 Conflict** - введённые username или email уже используются.
    * **422 Unprocessable Content** - формат username и email не соответствуют к: *@username* и *user@gmail.com*
    """
    return await service.register(data, guest_uuid)


@router.post("/register/verify")
async def verify(
    email: str,
    code: str,
    response: Response,
    guest_uuid: UUID | None = Depends(auth_verify_no_guest),
    service: AuthService = Depends(get_auth_service),
) -> UserRead:
    """
    # Проверяет код подтверждения email и создаёт запись в базе данных.
    ## Если код подтверждения введён неправильно, аннулирует его.
    ## Возможные ошибки:
    * **408 Request Timeout** - время кода истёк.
    * **400 Bad Request** - введён неправильный код.
    * **404 Not Found** - регистрационные данные в кэше не нашлись.
    """
    user, guestuuid = await service.verify_confirmation_code(email, code, guest_uuid)
    if guestuuid:
        response.delete_cookie(
            key="guest", path="/", httponly=True, samesite="lax", secure=False
        )
    return user


@router.post("/register/cancel")
async def cancel_registering(
    email: str, service: AuthService = Depends(get_auth_service)
) -> dict[str, str]:
    """
    # Отменяет регистрацию, аннулирует код подтверждения и удаляет данные из кэша.
    """
    return await service.cancel_authentication(email)


@router.post("/login")
async def login(
    response: Response,
    data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    """
    # Делает вход в систему, используется после умпешной регистрации.
    ## Можно сделать вход и по username и по email.
    ## Создаёт две пары JWT: access и refresh tokens, записывает refresh token в сессию пользователя в БД удаляя старый запись сессии с БД.
    ## Важно:
    * **Эндпоинт защищён с помощью Rate Limiting и с одного IP можно обращаться 5 раз в минуту, рекомендуется вводить правильные данные с первого раза чтобы не тратить попытки.**
    ## Возможные ошибки:
    * **422 Unprocessable Content** - неправильные данные, username или email не соответствуют формату: *@username*, *user@gmail.com*.
    * **404 Not Found** - пользователь не найден.
    * **400 Bad Request** - неправильный пароль
    """
    access_token, refresh_token = await service.login(data.username, data.password)

    await set_refresh_cookie(response, refresh_token)

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(
    refresh_token: str = Cookie(),
    _: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> None:
    """
    # Делает выход из системы, при выходе удаляет сессию пользователя из БД по его UUID
    """
    return await service.logout(refresh_token)


@router.post("/refresh")
async def refresh(
    response: Response,
    refresh_token: str = Cookie(),
    service: AuthService = Depends(get_auth_service),
) -> dict[str, str]:
    """
    # Обновляет пары JWT токенов.
    ## Создаёт новый refresh token и записывает в БД, а старый удаляет.
    ## Возможные ошибки:
    * **401 Unauthorized** - токен не передан или невалиден.
    * **404 Not Found** - пользователь не найден.
    """
    new_access_token, new_refresh_token = await service.refresh_token(refresh_token)

    await set_refresh_cookie(response, new_refresh_token)

    return {"access_token": new_access_token, "token_type": "bearer"}

from uuid import UUID

from fastapi import Cookie, Depends

from app.core.config import UserRole
from app.core.languages import LANGUAGES, LanguageTemplate
from app.core.security import decode_jwt, oauth2scheme
from app.core.uow import UnitOfWork
from app.exceptions import AccessDenied, EntityNotFound, LimitReached, Unauthorized
from app.models import User
from app.services.auth import AuthService
from app.services.diary import DiaryService
from app.services.exercise import ExerciseService
from app.services.guest import GuestService
from app.services.user import UserService
from app.services.weight import WeightService


async def get_uow() -> UnitOfWork:
    return UnitOfWork()


async def get_language(lang: str | None = Cookie(default="ru")) -> LanguageTemplate:
    if lang == "ru":
        return LANGUAGES["ru"]
    return LANGUAGES["tm"]


async def get_auth_service(
    uow: UnitOfWork = Depends(get_uow), lang: LanguageTemplate = Depends(get_language)
) -> AuthService:
    return AuthService(uow, lang)


async def get_user_service(
    uow: UnitOfWork = Depends(get_uow), lang: LanguageTemplate = Depends(get_language)
) -> UserService:
    return UserService(uow, lang)


async def get_guest_service(
    uow: UnitOfWork = Depends(get_uow), lang: LanguageTemplate = Depends(get_language)
) -> GuestService:
    return GuestService(uow, lang)


async def get_diary_service(
    uow: UnitOfWork = Depends(get_uow), lang: LanguageTemplate = Depends(get_language)
) -> DiaryService:
    return DiaryService(uow, lang)


async def get_weight_service(
    uow: UnitOfWork = Depends(get_uow), lang: LanguageTemplate = Depends(get_language)
) -> WeightService:
    return WeightService(uow, lang)


async def get_exercise_service(
    uow: UnitOfWork = Depends(get_uow), lang: LanguageTemplate = Depends(get_language)
) -> ExerciseService:
    return ExerciseService(uow, lang)


async def verify_no_guest(
    guest: str | None = Cookie(default=None, alias="guest"),
    lang: LanguageTemplate = Depends(get_language),
) -> None:
    if guest:
        payload = await decode_jwt(guest)
        if payload and payload.get("sub"):
            raise LimitReached(detail=lang.guest_diary_limit)


async def auth_verify_no_guest(
    guest: str | None = Cookie(default=None, alias="guest"),
) -> UUID | None:
    if guest:
        payload = await decode_jwt(guest)
        if payload and payload.get("sub"):
            return UUID(payload.get("sub"))


async def get_current_guest(
    token: str = Cookie(alias="guest", serialization_alias="token"),
    lang: LanguageTemplate = Depends(get_language),
) -> UUID:
    payload = await decode_jwt(token)
    if not payload:
        raise Unauthorized(detail=lang.invalid_guest_token)

    guest_uuid = payload.get("sub")
    if not guest_uuid:
        raise Unauthorized(detail=lang.invalid_guest_token)

    return UUID(guest_uuid)


async def get_current_user(
    token: str = Depends(oauth2scheme),
    uow: UnitOfWork = Depends(get_uow),
    lang: LanguageTemplate = Depends(get_language),
) -> User:
    payload = await decode_jwt(token)
    if not payload:
        raise Unauthorized(detail=lang.invalid_access_token)

    user_uuid = payload.get("sub")
    if not user_uuid:
        raise Unauthorized(detail=lang.invalid_access_token)

    async with uow:
        user = await uow.user_repo.get_user_by_uuid(UUID(user_uuid))
        if not user:
            raise EntityNotFound(detail=lang.user_not_found)
        return user


async def get_admin_or_higher_user(
    current_user: User = Depends(get_current_user),
    lang: LanguageTemplate = Depends(get_language),
) -> User:
    if current_user.role < UserRole.ADMIN:
        raise AccessDenied(detail=lang.admin_access_error)
    return current_user


async def get_owner_user(
    current_user: User = Depends(get_current_user),
    lang: LanguageTemplate = Depends(get_language),
) -> User:
    if current_user.role != UserRole.OWNER:
        raise AccessDenied(detail=lang.owner_access_error)
    return current_user

from uuid import UUID

from app.core.config import UserRole
from app.core.languages import LanguageTemplate
from app.core.uow import UnitOfWork
from app.exceptions import (
    AccessDenied,
    EntityNotFound,
    UniqueError,
    UnprocessableContent,
)
from app.schemes.user import UserRead, UserUpdate


class UserService:
    def __init__(self, uow: UnitOfWork, lang: LanguageTemplate) -> None:
        self.uow = uow
        self.language = lang

    async def get_user(self, user_uuid: UUID) -> UserRead:
        async with self.uow:
            user = await self.uow.user_repo.get_user_by_uuid(user_uuid)
            if not user:
                raise EntityNotFound(detail=self.language.user_not_found)
            return UserRead.model_validate(user)

    async def get_users_offset(self, page: int, size: int) -> list[UserRead]:
        async with self.uow:
            if page < 1:
                raise UnprocessableContent(detail=self.language.unprocessable_content)

            offset = (page - 1) * size
            users = await self.uow.user_repo.get_users_offset(size, offset)
            if not users:
                raise EntityNotFound(detail=self.language.user_not_found)

            return [UserRead.model_validate(u) for u in users]

    async def update_user(self, user_uuid: UUID, data: UserUpdate) -> UserRead:
        async with self.uow:
            user = await self.uow.user_repo.get_user_by_uuid(user_uuid)
            if not user:
                raise EntityNotFound(detail=self.language.user_not_found)

            if data.username:
                if await self.uow.user_repo.check_exists_usermame(data.username):
                    raise UniqueError(detail=self.language.email_is_in_use_error)

            updated = await self.uow.user_repo.update_user(user, data.model_dump())
            await self.uow.commit()
            return UserRead.model_validate(updated)

    async def delete_user(self, user_uuid: UUID) -> None:
        async with self.uow:
            user = await self.uow.user_repo.get_user_by_uuid(user_uuid)
            if not user:
                raise EntityNotFound(detail=self.language.user_not_found)

            await self.uow.user_repo.delete_user(user)
            await self.uow.commit()

    async def give_admin_role(self, user_uuid: UUID) -> UserRead:
        async with self.uow:
            user = await self.uow.user_repo.get_user_by_uuid(user_uuid)
            if not user:
                raise EntityNotFound(detail=self.language.user_not_found)

            updated = await self.uow.user_repo.update_user(
                user, {"role": UserRole.ADMIN}
            )
            await self.uow.commit()
            return UserRead.model_validate(updated)

    async def revoke_admin_role(self, user_uuid: UUID) -> UserRead:
        async with self.uow:
            user = await self.uow.user_repo.get_user_by_uuid(user_uuid)
            if not user:
                raise EntityNotFound(detail=self.language.user_not_found)

            updated = await self.uow.user_repo.update_user(
                user, {"role": UserRole.USER}
            )
            await self.uow.commit()
            return UserRead.model_validate(updated)

    async def delete_user_by_admin_or_owner(
        self, user_uuid: UUID, deleter_role: UserRole
    ) -> None:
        async with self.uow:
            user = await self.uow.user_repo.get_user_by_uuid(user_uuid)
            if not user:
                raise EntityNotFound(detail=self.language.user_not_found)

            if deleter_role <= user.role:
                raise AccessDenied(detail=self.language.delete_access_denied)

            await self.uow.user_repo.delete_user(user)
            await self.uow.commit()

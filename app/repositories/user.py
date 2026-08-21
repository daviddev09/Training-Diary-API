from collections.abc import Sequence
from typing import Any
from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Diary, User, Weight


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_user(
        self,
        user_data: dict[str, Any],
        diary: dict[str, Any] | None = None,
        weight: float | None = None,
    ) -> User:
        user = User(**user_data)
        if diary:
            user.diaries.append(Diary(**diary))
        if weight:
            user.user_weights.append(Weight(weight=weight))

        self.session.add(user)
        await self.session.flush()
        return user

    async def get_user_with_blocking(self, user_uuid: UUID) -> User | None:
        result = await self.session.execute(
            select(User).where(User.uuid == user_uuid).with_for_update()
        )
        return result.scalar_one_or_none()

    async def get_users_offset(self, limit: int, offset: int) -> Sequence[User] | None:
        result = await self.session.scalars(
            select(User)
            .order_by(User.uuid.asc())
            .limit(limit=limit)
            .offset(offset=offset)
        )
        return result.all()

    async def get_user_by_uuid(self, uuid: UUID) -> User | None:
        result = await self.session.execute(select(User).where(User.uuid == uuid))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()

    async def check_exists_email(self, email: str) -> bool | None:
        result = await self.session.execute(
            select(exists(User).where(User.email == email))
        )
        return result.scalar()

    async def check_exists_usermame(self, username: str) -> bool | None:
        result = await self.session.execute(
            select(exists(User).where(User.username == username))
        )
        return result.scalar()

    async def update_user(
        self, user: User, new_profile_data: dict[str, Any]
    ) -> User | None:
        for key, value in new_profile_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        await self.session.flush()
        return user

    async def delete_user(self, user: User) -> None:
        await self.session.delete(user)
        await self.session.flush()

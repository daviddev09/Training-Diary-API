from typing import Any
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import RefreshSession


class SessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_session(self, data: dict[str, Any]) -> RefreshSession:
        refresh_session = RefreshSession(**data)
        self.session.add(refresh_session)
        await self.session.flush()
        return refresh_session

    async def get_session_by_token(self, token: str) -> RefreshSession | None:
        result = await self.session.execute(
            select(RefreshSession).where(RefreshSession.token == token)
        )
        return result.scalar_one_or_none()

    async def delete_session_by_token(self, token: str) -> None:
        await self.session.execute(
            delete(RefreshSession).where(RefreshSession.token == token)
        )

    async def delete_session_by_user_uuid(self, user_uuid: UUID) -> None:
        await self.session.execute(
            delete(RefreshSession).where(RefreshSession.user_uuid == user_uuid)
        )

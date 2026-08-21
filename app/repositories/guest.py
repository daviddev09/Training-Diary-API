from uuid import UUID

from redis.asyncio import Redis

from app.schemes.training import DiaryRead


class GuestRepository:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis
        self.guest_exp_seconds = 60 * 60 * 24 * 7

    async def create_guest(self, uuid: UUID, diary: DiaryRead) -> None:
        cache_key = f"guest:{uuid}"
        await self.redis.set(
            cache_key, ex=self.guest_exp_seconds, value=diary.model_dump_json()
        )

    async def get_guest_diary(self, uuid: UUID) -> DiaryRead | None:
        cache_key = f"guest:{uuid}"
        raw_data = await self.redis.get(cache_key)
        if not raw_data:
            return None
        return DiaryRead.model_validate_json(raw_data)

    async def update_guest_diary(self, uuid: UUID, diary: DiaryRead) -> None:
        cache_key = f"guest:{uuid}"
        await self.redis.set(cache_key, diary.model_dump_json(), keepttl=True)

    async def delete_guest_diary(self, uuid: UUID) -> None:
        cache_key = f"guest:{uuid}"
        await self.redis.delete(cache_key)

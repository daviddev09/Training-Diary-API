import json
from typing import Any

from redis.asyncio import Redis


class ValidateCacheRepository:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def add_email_confirmation_code(self, email: str, code: str) -> None:
        cache_key = f"user:{email}:confirm"
        await self.redis.set(cache_key, code, ex=60)

    async def get_email_confirmation_code(self, email: str) -> str | None | bytes:
        cache_key = f"user:{email}:confirm"
        return await self.redis.get(cache_key)

    async def del_email_confirmation_code(self, email: str) -> None:
        cache_key = f"user:{email}:confirm"
        await self.redis.delete(cache_key)

    async def add_user_profile(self, email: str, user_data: dict[str, Any]) -> None:
        cache_key = f"user:{email}:profile"
        await self.redis.set(cache_key, json.dumps(user_data, default=str), ex=60)

    async def get_user_profile(self, email: str) -> dict[str, Any] | None:
        cache_key = f"user:{email}:profile"
        raw_data = await self.redis.get(cache_key)
        if not raw_data:
            return None
        return json.loads(raw_data)

    async def del_user_profile(self, email: str) -> None:
        cache_key = f"user:{email}:profile"
        await self.redis.delete(cache_key)

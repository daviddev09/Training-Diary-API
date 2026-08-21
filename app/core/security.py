from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import jwt
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from uuid_utils import uuid7

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


async def create_jwt(data: dict[str, str], token_time: timedelta) -> str:
    to_encode = data.copy()

    exp = datetime.now(timezone.utc) + token_time
    to_encode.update({"exp": exp})  # type: ignore
    return jwt.encode(  # type: ignore
        to_encode, key=settings.jwt_secret_key, algorithm=settings.algorithm
    )


async def decode_jwt(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(  # type: ignore
            jwt=token, key=settings.jwt_secret_key, algorithms=[settings.algorithm]
        )
    except jwt.PyJWTError:
        return None


async def create_access_token(sub: str, role: str) -> str:
    payload = {
        "sub": sub,
        "role": role,
        "type": "access",
    }
    return await create_jwt(
        data=payload, token_time=timedelta(minutes=settings.access_token_expire_minutes)
    )


async def create_refresh_token(sub: str, role: str) -> str:
    payload = {
        "sub": sub,
        "role": role,
        "type": "refresh",
    }
    return await create_jwt(
        data=payload, token_time=timedelta(days=settings.refresh_token_expire_days)
    )


async def create_guest_token(sub: str, role: str) -> str:
    payload = {"sub": sub, "role": role, "type": "guest"}
    return await create_jwt(data=payload, token_time=timedelta(days=7))


async def set_refresh_cookie(response: Response, refresh_token: str):
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )


async def create_four_digit_code() -> str:
    import random

    nums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    code = ""
    for _ in range(4):
        num = random.choice(nums)
        code += str(num)
    return code


def create_uuid7() -> UUID:
    return UUID(bytes=uuid7().bytes)

from collections.abc import AsyncGenerator, Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
from fakeredis.aioredis import FakeRedis
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.dependencies import get_uow
from app.core.config import UserRole
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
)
from app.core.uow import UnitOfWork
from app.main import app
from app.models import Base, Diary, Exercise, User, Weight

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
async def db_session() -> AsyncGenerator[AsyncSession, Any]:
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def guest_redis() -> AsyncGenerator[FakeRedis]:
    redis = FakeRedis(decode_responses=True)
    yield redis
    await redis.flushdb()  # type: ignore


@pytest_asyncio.fixture
async def validate_redis() -> AsyncGenerator[FakeRedis]:
    redis = FakeRedis(decode_responses=True)
    yield redis
    await redis.flushdb()  # type: ignore


@pytest_asyncio.fixture
async def rate_limiter_redis() -> AsyncGenerator[FakeRedis]:
    redis = FakeRedis(decode_responses=True)
    yield redis
    await redis.flushdb()  # type: ignore


@pytest.fixture
def mock_celery() -> Generator[MagicMock]:
    with patch("app.workers.celery_app.app.send_task") as mocked:
        yield mocked


@pytest.fixture(autouse=True)
def mock_four_digit_code() -> Generator[MagicMock]:
    with patch(
        "app.services.auth.create_four_digit_code", return_value="1234"
    ) as mocked:
        yield mocked


@pytest_asyncio.fixture
async def client(
    mock_celery: MagicMock,
    guest_redis: FakeRedis,
    validate_redis: FakeRedis,
    rate_limiter_redis: FakeRedis,
) -> AsyncGenerator[AsyncClient]:

    async def get_test_uow() -> UnitOfWork:
        return UnitOfWork(
            session_factory=TestSessionLocal,
            redis_validate=validate_redis,
            redis_guest=guest_redis,
        )

    app.dependency_overrides[get_uow] = get_test_uow

    with (
        patch(target="app.core.database.AsyncSessionLocal", new=TestSessionLocal),
        patch(target="app.middlewares.rate_limiter_redis", new=rate_limiter_redis),
    ):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def owner_user(db_session: AsyncSession) -> User:
    user = User(
        name="owner",
        username="@owner",
        email="owner@gmail.com",
        password=await get_password_hash("ownerpass123"),
        role=UserRole.OWNER,
        age=18,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    user = User(
        name="admin",
        username="@admin",
        email="admin@gmail.com",
        password=await get_password_hash("adminpass123"),
        role=UserRole.ADMIN,
        age=18,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    user = User(
        name="user",
        username="@user",
        email="user@gmail.com",
        password=await get_password_hash("userpass123"),
        age=18,
        current_weight=100,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_diary(db_session: AsyncSession, test_user: User) -> Diary:
    diary = Diary(diary_name="Calisthenics", user_uuid=test_user.uuid)

    db_session.add(diary)
    await db_session.commit()
    await db_session.refresh(diary)
    return diary


@pytest_asyncio.fixture
async def test_exercise(db_session: AsyncSession) -> Exercise:
    exercise = Exercise(name="One Arm Handstand", is_system=True)

    db_session.add(exercise)
    await db_session.commit()
    await db_session.refresh(exercise)
    return exercise


@pytest_asyncio.fixture
async def test_weight(db_session: AsyncSession, test_user: User) -> Weight:
    weight = Weight(weight=100, user_uuid=test_user.uuid)

    db_session.add(weight)
    await db_session.commit()
    await db_session.refresh(weight)
    return weight


@pytest_asyncio.fixture
async def owner_access_token(owner_user: User) -> str:
    return await create_access_token(sub=str(owner_user.uuid), role=owner_user.role)


@pytest_asyncio.fixture
async def admin_access_token(admin_user: User) -> str:
    return await create_access_token(sub=str(admin_user.uuid), role=admin_user.role)


@pytest_asyncio.fixture
async def user_access_token(test_user: User) -> str:
    return await create_access_token(sub=str(test_user.uuid), role=test_user.role)


@pytest_asyncio.fixture
async def user_refresh_token(test_user: User) -> str:
    return await create_refresh_token(sub=str(test_user.uuid), role=test_user.role)

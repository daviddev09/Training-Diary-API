from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import UserRole, settings
from app.core.security import get_password_hash
from app.core.system_exercises import SYSTEM_EXERCISES
from app.models import Exercise, User

engine = create_async_engine(
    url=settings.database_url, echo=True, pool_size=10, max_overflow=5
)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)

validate_redis = Redis(
    host=settings.redis_host, port=settings.redis_port, db=0, decode_responses=True
)
guest_redis = Redis(
    host=settings.redis_host, port=settings.redis_port, db=1, decode_responses=True
)
rate_limiter_redis = Redis(
    host=settings.redis_host, port=settings.redis_port, db=2, decode_responses=True
)


async def init_owner() -> None:
    async with AsyncSessionLocal() as session:
        if await session.scalar(
            select(User.uuid).where(User.email == settings.owner_email)
        ):
            return

        hashed_owner_password = await get_password_hash(settings.owner_password)

        owner = User(
            name=settings.owner_name,
            username=settings.owner_username,
            email=settings.owner_email,
            role=UserRole.OWNER,
            password=hashed_owner_password,
            age=settings.owner_age,
        )
        session.add(owner)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()


async def init_system_exercises() -> None:
    async with AsyncSessionLocal() as session:
        existing_result = await session.execute(select(Exercise.name))
        existing_names = set(existing_result.scalars().all())

        new_exercises = [
            Exercise(**item, is_system=True)
            for item in SYSTEM_EXERCISES
            if item["name"] not in existing_names
        ]
        if new_exercises:
            session.add_all(new_exercises)
            try:
                await session.commit()
            except IntegrityError:
                await session.rollback()

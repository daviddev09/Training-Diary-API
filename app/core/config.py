import enum

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://user:password@host:port/db_name"
    jwt_secret_key: str = "your secret key"
    owner_name: str = "Your name"
    owner_username: str = "Your username"
    owner_email: str = "Your gmail address"
    owner_password: str = "Your secret password"
    owner_age: int = 50
    redis_host: str = "localhost"
    redis_port: int = 6379

    smtp_email: str = "Your smtp sender email"
    smtp_app_password: str = "Your smtp password"
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class UserRole(str, enum.Enum):
    GUEST = "guest"
    USER = "user"
    ADMIN = "admin"
    OWNER = "owner"

    @property
    def _weight(self) -> int:
        weights = {
            UserRole.GUEST: 1,
            UserRole.USER: 2,
            UserRole.ADMIN: 3,
            UserRole.OWNER: 4,
        }
        return weights[self]

    def __lt__(self, other: object) -> bool:
        if isinstance(other, UserRole):
            return self._weight < other._weight
        return NotImplemented

    def __le__(self, other: object) -> bool:
        if isinstance(other, UserRole):
            return self._weight <= other._weight
        return NotImplemented

    def __gt__(self, other: object) -> bool:
        if isinstance(other, UserRole):
            return self._weight > other._weight
        return NotImplemented

    def __ge__(self, other: object) -> bool:
        if isinstance(other, UserRole):
            return self._weight >= other._weight
        return NotImplemented


class Difficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


settings = Settings()

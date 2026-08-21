from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.config import UserRole


class RefReshSessionCreate(BaseModel):
    user_uuid: UUID
    token: str
    expires_at: datetime


class UserCreate(BaseModel):
    name: str = Field(max_length=30, examples=["твоё имя"])
    username: str = Field(
        max_length=15, examples=["имя пользователя, должно начаться с символа @"]
    )
    email: EmailStr = Field(
        examples=["адрес электронной почты, поддерживается только Google почта"]
    )
    password: str = Field(
        max_length=150, min_length=8, examples=["твой секретный пароль"]
    )
    age: int = Field(ge=7, lt=100, examples=["твой возраст"])
    current_weight: float | None = Field(
        ge=15, lt=1000, examples=["твой вес. Грамы нужно писать через точку: 45.700"]
    )


class WeightCreate(BaseModel):
    weight: float = Field(
        gt=15, lt=1000, examples=["Твой вес. Грамы нужно писать через точку: 45.700"]
    )
    added_at: datetime | None = Field(default=None)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: UUID
    name: str
    username: str
    email: str
    role: UserRole
    age: int
    current_weight: float | None = Field(default=None)


class WeightRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    weight: float
    added_at: datetime


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=30)
    username: str | None = Field(default=None, max_length=15)
    password: str | None = Field(default=None, max_length=150)


class WeightUpdate(BaseModel):
    weight: float | None = Field(default=None, gt=15, lt=1000)
    added_at: datetime | None = Field(default=None)


class EmailVerify(BaseModel):
    email: EmailStr

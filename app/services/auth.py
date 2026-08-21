from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from app.core.config import UserRole, settings
from app.core.languages import LanguageTemplate
from app.core.security import (
    create_access_token,
    create_four_digit_code,
    create_refresh_token,
    decode_jwt,
    get_password_hash,
    verify_password,
)
from app.core.uow import UnitOfWork
from app.exceptions import (
    CodeTimeOut,
    EntityNotFound,
    InvalidCode,
    InvalidEmail,
    InvalidPassword,
    InvalidUsername,
    Unauthorized,
    UniqueError,
    UnprocessableContent,
)
from app.schemes.user import RefReshSessionCreate, UserCreate, UserRead


class AuthService:
    def __init__(self, uow: UnitOfWork, lang: LanguageTemplate) -> None:
        self.uow = uow
        self.language = lang
        self.refresh_token_exp = datetime.now(timezone.utc) + timedelta(
            days=settings.refresh_token_expire_days
        )

    def _validate_email(self, email: str) -> None:
        if email.lower().split("@")[1] != "gmail.com":
            raise InvalidEmail(detail=self.language.wrong_email_type)

    def _validate_username(self, username: str) -> None:
        if not username.startswith("@"):
            raise InvalidUsername(detail=self.language.wrong_username_type)
        if "@" in username[1:]:
            raise InvalidUsername(detail=self.language.wrong_username_type)

    def _define_the_username(self, user_data: str) -> bool:
        if user_data.startswith("@"):
            if "@" in user_data[1:]:
                raise InvalidUsername(detail=self.language.wrong_username_type)
            return True
        return False

    def _define_the_email(self, user_data: str) -> bool:
        from pydantic import ValidationError

        from app.schemes.user import EmailVerify

        try:
            EmailVerify.model_validate({"email": user_data})
        except ValidationError:
            raise InvalidEmail(detail=self.language.wrong_email_type)
        if not user_data.lower().endswith("@gmail.com"):
            raise InvalidEmail(detail=self.language.wrong_email_type)
        return True

    def _create_user_data(
        self,
        data: UserCreate,
        pwd_hash: str,
        role: UserRole,
        guest_diary: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        user_data: dict[str, Any] = {
            "name": data.name,
            "username": data.username,
            "email": data.email.lower(),
            "role": role,
            "password": pwd_hash,
            "age": data.age,
            "current_weight": data.current_weight,
            "diaries": [],
            "user_weights": [],
        }
        if guest_diary:
            user_data.update(diary=guest_diary)
        return user_data

    def _create_refresh_session_data(
        self, user_uuid: str, token: str, expires_at: datetime
    ) -> dict[str, Any]:
        refresh_session = RefReshSessionCreate(
            user_uuid=UUID(user_uuid), token=token, expires_at=expires_at
        )
        return refresh_session.model_dump()

    async def _get_validated_jwt_payload_data(self, token: str) -> tuple[str, str]:
        payload = await decode_jwt(token)
        if not payload:
            raise Unauthorized(detail=self.language.invalid_refresh_token)

        user_uuid = payload.get("sub")
        role = payload.get("role")
        if not user_uuid or not role:
            raise Unauthorized(detail=self.language.invalid_refresh_token)

        return user_uuid, role

    async def cancel_authentication(self, email: str):
        async with self.uow:
            await self.uow.validate_repo.del_user_profile(email)
            await self.uow.validate_repo.del_email_confirmation_code(email)
            return {"msg": "success"}

    async def register(
        self, data: UserCreate, guest_uuid: UUID | None = None
    ) -> dict[str, str]:
        self._validate_email(email=data.email)
        self._validate_username(username=data.username)

        async with self.uow:
            if await self.uow.user_repo.check_exists_email(data.email):
                raise UniqueError(detail=self.language.email_is_in_use_error)
            if await self.uow.user_repo.check_exists_usermame(data.username):
                raise UniqueError(detail=self.language.username_is_in_user_error)

            pwd_hash = await get_password_hash(password=data.password)
            user_role = UserRole.USER

            exists_diary = None
            if guest_uuid:
                diary = await self.uow.guest_repo.get_guest_diary(guest_uuid)
                if diary:
                    exists_diary = diary.model_dump()
                    _ = exists_diary.pop("id")

            user_data = self._create_user_data(
                data=data, pwd_hash=pwd_hash, role=user_role, guest_diary=exists_diary
            )
            code = await create_four_digit_code()

            await self.uow.validate_repo.add_user_profile(
                email=data.email, user_data=user_data
            )
            await self.uow.validate_repo.add_email_confirmation_code(
                email=data.email, code=code
            )
            self.uow.register_task(
                task_name="app.workers.smtp_worker.send_confirmation_code",
                recipient_email=data.email,
                subject=self.language.smtp_register_verify,
                name=data.name,
                code=code,
            )
            await self.uow.commit()
            return {"message": self.language.register_verification_code_sended}

    async def verify_confirmation_code(
        self, email: str, code: str, guest_uuid: UUID | None = None
    ) -> tuple[UserRead, UUID | None]:
        async with self.uow:
            cached_code = await self.uow.validate_repo.get_email_confirmation_code(
                email
            )

            if not cached_code:
                raise CodeTimeOut(detail=self.language.email_verify_code_timeout)

            if cached_code != code:
                await self.uow.validate_repo.del_email_confirmation_code(email)
                raise InvalidCode(detail=self.language.email_verify_code_wrong)

            user_data = await self.uow.validate_repo.get_user_profile(email)

            if not user_data:
                raise EntityNotFound(detail=self.language.cache_user_data_not_found)

            diary = None
            if user_data.get("diary"):
                from app.parsers import guest_diary_parser

                diary = guest_diary_parser(user_data.pop("diary"))

            weight = None
            if user_data.get("current_weight"):
                weight = user_data["current_weight"]

            user = await self.uow.user_repo.create_user(user_data, diary, weight)
            if guest_uuid:
                await self.uow.guest_repo.delete_guest_diary(guest_uuid)

            await self.uow.validate_repo.del_user_profile(email)
            await self.uow.validate_repo.del_email_confirmation_code(email)
            await self.uow.commit()
            return UserRead.model_validate(user), guest_uuid

    async def login(self, user_data: str, password: str) -> tuple[str, str]:
        if not user_data:
            raise UnprocessableContent(detail=self.language.unprocessable_content)
        username: str | None = None
        email: str | None = None
        if self._define_the_username(user_data):
            username = user_data
        elif self._define_the_email(user_data):
            email = user_data.lower()

        async with self.uow:
            user = None
            if username:
                user = await self.uow.user_repo.get_user_by_username(username)
            elif email:
                user = await self.uow.user_repo.get_user_by_email(email)

            if not user:
                raise EntityNotFound(detail=self.language.user_not_found)

            if not await verify_password(password, user.password):
                raise InvalidPassword(detail=self.language.wrong_password)

            access_token = await create_access_token(sub=str(user.uuid), role=user.role)
            refresh_token = await create_refresh_token(
                sub=str(user.uuid), role=user.role
            )
            data = self._create_refresh_session_data(
                str(user.uuid), refresh_token, self.refresh_token_exp
            )

            await self.uow.session_repo.delete_session_by_user_uuid(user.uuid)
            await self.uow.session_repo.add_session(data=data)
            await self.uow.commit()
            return access_token, refresh_token

    async def logout(self, refresh_token: str | None):
        if not refresh_token:
            return

        async with self.uow:
            await self.uow.session_repo.delete_session_by_token(refresh_token)
            await self.uow.commit()

    async def refresh_token(self, refresh_token: str):
        if not refresh_token:
            raise Unauthorized(detail=self.language.invalid_refresh_token)

        async with self.uow:
            session_token = await self.uow.session_repo.get_session_by_token(
                refresh_token
            )

            if not session_token:
                raise Unauthorized(detail=self.language.user_refresh_session_empty)
            expires_at = session_token.expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)

            if expires_at < datetime.now(timezone.utc):
                await self.uow.session_repo.delete_session_by_token(refresh_token)
                await self.uow.commit()
                raise Unauthorized(detail=self.language.refresh_token_time_out)

            payload_data = await self._get_validated_jwt_payload_data(refresh_token)
            user_uuid, user_role = payload_data[0], payload_data[1]

            new_access_token = await create_access_token(user_uuid, user_role)
            new_refresh_token = await create_refresh_token(user_uuid, user_role)

            data = self._create_refresh_session_data(
                user_uuid, new_refresh_token, self.refresh_token_exp
            )

            await self.uow.session_repo.delete_session_by_token(refresh_token)
            await self.uow.session_repo.add_session(data=data)
            await self.uow.commit()

            return new_access_token, new_refresh_token

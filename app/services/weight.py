from uuid import UUID

from app.core.languages import LanguageTemplate
from app.core.uow import UnitOfWork
from app.exceptions import EntityNotFound, LimitReached
from app.schemes.user import WeightCreate, WeightRead, WeightUpdate


class WeightService:
    def __init__(self, uow: UnitOfWork, lang: LanguageTemplate) -> None:
        self.uow = uow
        self.language = lang
        self.user_weights_limit = 10

    async def create_weight(self, user_uuid: UUID, data: WeightCreate) -> WeightRead:
        async with self.uow:
            user = await self.uow.user_repo.get_user_with_blocking(user_uuid)
            if not user:
                raise EntityNotFound(detail=self.language.user_not_found)
            if (
                await self.uow.weight_repo.get_weights_count(user_uuid)
                >= self.user_weights_limit
            ):
                raise LimitReached(detail=self.language.user_weights_limit)

            weight = await self.uow.weight_repo.create_weight(
                data.model_dump(), user_uuid
            )
            await self.uow.commit()
            return WeightRead.model_validate(weight)

    async def get_user_weight(self, weight_id: int, user_uuid: UUID) -> WeightRead:
        async with self.uow:
            weight = await self.uow.weight_repo.get_weight(weight_id, user_uuid)
            if not weight:
                raise EntityNotFound(detail=self.language.weight_not_found)

            return WeightRead.model_validate(weight)

    async def get_user_weights(self, user_uuid: UUID) -> list[WeightRead]:
        async with self.uow:
            weights = await self.uow.weight_repo.get_weights(user_uuid)
            if not weights:
                raise EntityNotFound(detail=self.language.weight_not_found)

            return [WeightRead.model_validate(w) for w in weights]

    async def update_weight(
        self, weight_id: int, user_uuid: UUID, data: WeightUpdate
    ) -> WeightRead:
        async with self.uow:
            weight = await self.uow.weight_repo.get_weight(weight_id, user_uuid)
            if not weight:
                raise EntityNotFound(detail=self.language.weight_not_found)

            updated = await self.uow.weight_repo.update_weight(
                weight, data.model_dump()
            )
            await self.uow.commit()
            return WeightRead.model_validate(updated)

    async def delete_weight(self, weight_id: int, user_uuid: UUID) -> None:
        async with self.uow:
            weight = await self.uow.weight_repo.get_weight(weight_id, user_uuid)
            if not weight:
                raise EntityNotFound(detail=self.language.weight_not_found)

            await self.uow.weight_repo.delete_weight(weight)
            await self.uow.commit()

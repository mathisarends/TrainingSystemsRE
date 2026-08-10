from datetime import datetime
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from training_system.features.notifications.domain.entities import UnseenCompletion
from training_system.features.notifications.domain.repository import (
    UnseenCompletionRepository,
)
from training_system.infrastructure.database.orm import UnseenCompletionModel


class SqlUnseenCompletionRepository(UnseenCompletionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_domain(self, model: UnseenCompletionModel) -> UnseenCompletion:
        return UnseenCompletion(
            id=model.id,
            created_time=model.created_at,
            user_id=model.user_id,
            completed_at=model.completed_at,
        )

    async def list_for_user(self, *, user_id: UUID) -> list[UnseenCompletion]:
        statement = select(UnseenCompletionModel).where(
            UnseenCompletionModel.user_id == user_id
        )
        models = (await self._session.scalars(statement)).all()
        return [self._to_domain(model) for model in models]

    async def create(
        self, *, user_id: UUID, completed_at: datetime
    ) -> UnseenCompletion:
        model = UnseenCompletionModel(user_id=user_id, completed_at=completed_at)
        self._session.add(model)
        await self._session.flush()
        return self._to_domain(model)

    async def clear_for_user(self, *, user_id: UUID) -> int:
        existing = await self.list_for_user(user_id=user_id)
        await self._session.execute(
            delete(UnseenCompletionModel).where(
                UnseenCompletionModel.user_id == user_id
            )
        )
        await self._session.flush()
        return len(existing)

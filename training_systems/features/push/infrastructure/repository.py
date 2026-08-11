from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from training_systems.features.push.domain.entities import PushSubscription
from training_systems.features.push.domain.repository import (
    PushSubscriptionRepository,
)
from training_systems.infrastructure.database.orm import PushSubscriptionModel


class SqlPushSubscriptionRepository(PushSubscriptionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_user(self, *, user_id: UUID) -> PushSubscription | None:
        statement = select(PushSubscriptionModel).where(
            PushSubscriptionModel.user_id == user_id
        )
        model = await self._session.scalar(statement)
        if model is None:
            return None
        return PushSubscription(
            user_id=model.user_id,
            endpoint=model.endpoint,
            p256dh=model.p256dh,
            auth=model.auth,
        )

    async def save(self, *, subscription: PushSubscription) -> PushSubscription:
        statement = select(PushSubscriptionModel).where(
            PushSubscriptionModel.user_id == subscription.user_id
        )
        existing = await self._session.scalar(statement)
        if existing is None:
            existing = PushSubscriptionModel(user_id=subscription.user_id)
            self._session.add(existing)
        existing.endpoint = subscription.endpoint
        existing.p256dh = subscription.p256dh
        existing.auth = subscription.auth
        await self._session.flush()
        return subscription

    async def delete(self, *, user_id: UUID) -> None:
        statement = select(PushSubscriptionModel).where(
            PushSubscriptionModel.user_id == user_id
        )
        model = await self._session.scalar(statement)
        if model is not None:
            await self._session.delete(model)
            await self._session.flush()

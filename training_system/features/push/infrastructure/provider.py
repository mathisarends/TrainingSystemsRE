from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from training_system.features.push.application import (
    PushSender,
    PushSubscriptionService,
)
from training_system.features.push.domain import PushSubscriptionRepository
from training_system.features.push.infrastructure.repository import (
    SqlPushSubscriptionRepository,
)
from training_system.features.push.infrastructure.sender import WebPushSender
from training_system.features.push.infrastructure.settings import PushSettings


class PushProvider(Provider):
    @provide(scope=Scope.APP)
    def settings(self) -> PushSettings:
        return PushSettings()

    @provide(scope=Scope.APP)
    def push_sender(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        settings: PushSettings,
    ) -> PushSender:
        return WebPushSender(session_factory, settings)

    @provide(scope=Scope.REQUEST)
    def push_subscription_repository(
        self, session: AsyncSession
    ) -> PushSubscriptionRepository:
        return SqlPushSubscriptionRepository(session)

    @provide(scope=Scope.REQUEST)
    def push_subscription_service(
        self, repository: PushSubscriptionRepository
    ) -> PushSubscriptionService:
        return PushSubscriptionService(repository)

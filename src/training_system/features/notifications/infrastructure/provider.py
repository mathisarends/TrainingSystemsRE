from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from training_system.features.notifications.application import (
    UnseenCompletionService,
)
from training_system.features.notifications.domain import UnseenCompletionRepository
from training_system.features.notifications.infrastructure.repository import (
    SqlUnseenCompletionRepository,
)


class NotificationsProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def unseen_completion_repository(
        self, session: AsyncSession
    ) -> UnseenCompletionRepository:
        return SqlUnseenCompletionRepository(session)

    @provide(scope=Scope.REQUEST)
    def unseen_completion_service(
        self, repository: UnseenCompletionRepository
    ) -> UnseenCompletionService:
        return UnseenCompletionService(repository)

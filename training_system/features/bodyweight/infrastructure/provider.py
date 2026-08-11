from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from training_system.features.bodyweight.application import BodyWeightService
from training_system.features.bodyweight.domain import BodyWeightRepository
from training_system.features.bodyweight.infrastructure.repository import (
    SqlBodyWeightRepository,
)


class BodyWeightProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def body_weight_repository(self, session: AsyncSession) -> BodyWeightRepository:
        return SqlBodyWeightRepository(session)

    @provide(scope=Scope.REQUEST)
    def body_weight_service(
        self, repository: BodyWeightRepository
    ) -> BodyWeightService:
        return BodyWeightService(repository)

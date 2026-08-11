from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from training_systems.features.exercises.application import ExerciseCatalogService
from training_systems.features.exercises.domain import ExerciseCatalogRepository
from training_systems.features.exercises.infrastructure.repository import (
    SqlExerciseCatalogRepository,
)


class ExerciseCatalogProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def exercise_catalog_repository(
        self, session: AsyncSession
    ) -> ExerciseCatalogRepository:
        return SqlExerciseCatalogRepository(session)

    @provide(scope=Scope.REQUEST)
    def exercise_catalog_service(
        self, repository: ExerciseCatalogRepository
    ) -> ExerciseCatalogService:
        return ExerciseCatalogService(repository)

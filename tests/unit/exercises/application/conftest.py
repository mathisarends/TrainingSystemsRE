from uuid import UUID

import pytest

from training_system.features.exercises.application.service import (
    ExerciseCatalogService,
)
from training_system.features.exercises.domain import (
    ExerciseCatalog,
    ExerciseCatalogRepository,
)


class FakeExerciseCatalogRepository(ExerciseCatalogRepository):
    def __init__(self) -> None:
        self.catalogs: dict[UUID, ExerciseCatalog] = {}

    async def find_by_user(self, *, user_id: UUID) -> ExerciseCatalog | None:
        return self.catalogs.get(user_id)

    async def replace(self, *, catalog: ExerciseCatalog) -> ExerciseCatalog:
        self.catalogs[catalog.user_id] = catalog
        return catalog


@pytest.fixture
def catalog_repository() -> FakeExerciseCatalogRepository:
    return FakeExerciseCatalogRepository()


@pytest.fixture
def catalog_service(
    catalog_repository: FakeExerciseCatalogRepository,
) -> ExerciseCatalogService:
    return ExerciseCatalogService(catalog_repository)

from abc import ABC, abstractmethod
from uuid import UUID

from training_system.features.exercises.domain.entities import ExerciseCatalog


class ExerciseCatalogRepository(ABC):
    @abstractmethod
    async def find_by_user(self, *, user_id: UUID) -> ExerciseCatalog | None: ...

    @abstractmethod
    async def replace(self, *, catalog: ExerciseCatalog) -> ExerciseCatalog: ...

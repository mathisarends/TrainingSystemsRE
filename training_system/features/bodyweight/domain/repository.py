from abc import ABC, abstractmethod
from uuid import UUID

from training_system.features.bodyweight.domain.entities import (
    BodyWeightEntry,
    BodyWeightGoal,
)


class BodyWeightRepository(ABC):
    @abstractmethod
    async def list_entries(self, *, user_id: UUID) -> list[BodyWeightEntry]: ...

    @abstractmethod
    async def upsert_entry(
        self, *, user_id: UUID, entry: BodyWeightEntry
    ) -> BodyWeightEntry: ...

    @abstractmethod
    async def get_goal(self, *, user_id: UUID) -> BodyWeightGoal | None: ...

    @abstractmethod
    async def save_goal(
        self, *, user_id: UUID, goal: BodyWeightGoal
    ) -> BodyWeightGoal: ...

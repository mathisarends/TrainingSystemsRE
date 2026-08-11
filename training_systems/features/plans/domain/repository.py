from abc import ABC, abstractmethod
from uuid import UUID

from training_systems.features.plans.domain.entities import Plan


class PlanRepository(ABC):
    @abstractmethod
    async def find_by_id(self, *, plan_id: UUID, user_id: UUID) -> Plan | None: ...

    @abstractmethod
    async def list_for_user(self, *, user_id: UUID) -> list[Plan]: ...

    @abstractmethod
    async def find_most_recently_updated(self, *, user_id: UUID) -> Plan | None: ...

    @abstractmethod
    async def save(self, *, plan: Plan) -> Plan: ...

    @abstractmethod
    async def delete(self, *, plan_id: UUID, user_id: UUID) -> bool: ...

    @abstractmethod
    async def average_recorded_duration_minutes(
        self, *, plan_id: UUID
    ) -> float | None: ...

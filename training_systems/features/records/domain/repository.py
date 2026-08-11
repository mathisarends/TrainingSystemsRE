from abc import ABC, abstractmethod
from uuid import UUID

from training_systems.features.records.domain.entities import PersonalRecord


class PersonalRecordRepository(ABC):
    @abstractmethod
    async def list_for_user(self, *, user_id: UUID) -> list[PersonalRecord]: ...

    @abstractmethod
    async def find_by_exercise(
        self, *, user_id: UUID, exercise_name: str
    ) -> PersonalRecord | None: ...

    @abstractmethod
    async def save(
        self, *, user_id: UUID, record: PersonalRecord
    ) -> PersonalRecord: ...

    @abstractmethod
    async def delete(self, *, user_id: UUID, exercise_name: str) -> None: ...

from uuid import UUID

import pytest

from training_system.features.records.application.service import (
    PersonalRecordService,
)
from training_system.features.records.domain import PersonalRecord
from training_system.features.records.domain.repository import (
    PersonalRecordRepository,
)


class FakePersonalRecordRepository(PersonalRecordRepository):
    def __init__(self) -> None:
        self.records: dict[tuple[UUID, str], PersonalRecord] = {}

    async def list_for_user(self, *, user_id: UUID) -> list[PersonalRecord]:
        return [
            record
            for (owner_id, _), record in self.records.items()
            if owner_id == user_id
        ]

    async def find_by_exercise(
        self, *, user_id: UUID, exercise_name: str
    ) -> PersonalRecord | None:
        return self.records.get((user_id, exercise_name))

    async def save(
        self, *, user_id: UUID, record: PersonalRecord
    ) -> PersonalRecord:
        self.records[(user_id, record.exercise_name)] = record
        return record

    async def delete(self, *, user_id: UUID, exercise_name: str) -> None:
        self.records.pop((user_id, exercise_name), None)


@pytest.fixture
def record_repository() -> FakePersonalRecordRepository:
    return FakePersonalRecordRepository()


@pytest.fixture
def record_service(
    record_repository: FakePersonalRecordRepository,
) -> PersonalRecordService:
    return PersonalRecordService(record_repository)

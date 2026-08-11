from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from training_systems.features.records.application.errors import RecordNotFound
from training_systems.features.records.domain import PersonalRecord, RecordSnapshot
from training_systems.features.records.domain.repository import (
    PersonalRecordRepository,
)


@dataclass(frozen=True, slots=True)
class UpsertResult:
    record: PersonalRecord
    accepted: bool


class PersonalRecordService:
    def __init__(self, repository: PersonalRecordRepository) -> None:
        self._repository = repository

    async def list_records(self, *, user_id: UUID) -> list[PersonalRecord]:
        return await self._repository.list_for_user(user_id=user_id)

    async def upsert_record(
        self,
        *,
        user_id: UUID,
        exercise_name: str,
        category: str,
        sets: int,
        reps: int,
        weight: float,
        actual_rpe: float,
        est_max: float,
    ) -> UpsertResult:
        current = await self._repository.find_by_exercise(
            user_id=user_id, exercise_name=exercise_name
        )
        snapshot = RecordSnapshot(
            sets=sets,
            reps=reps,
            weight=weight,
            actual_rpe=actual_rpe,
            est_max=est_max,
            achieved_at=datetime.now(UTC),
        )

        if current is None:
            record = PersonalRecord(
                exercise_name=exercise_name,
                category=category,
                sets=sets,
                reps=reps,
                weight=weight,
                actual_rpe=actual_rpe,
                est_max=est_max,
                achieved_at=snapshot.achieved_at,
            )
            saved = await self._repository.save(user_id=user_id, record=record)
            return UpsertResult(record=saved, accepted=True)

        if est_max <= current.est_max:
            return UpsertResult(record=current, accepted=False)

        current.replace_with(snapshot, category=category)
        saved = await self._repository.save(user_id=user_id, record=current)
        return UpsertResult(record=saved, accepted=True)

    async def revert_to_previous(
        self, *, user_id: UUID, exercise_name: str
    ) -> PersonalRecord | None:
        current = await self._repository.find_by_exercise(
            user_id=user_id, exercise_name=exercise_name
        )
        if current is None:
            raise RecordNotFound(exercise_name)

        if not current.revert_to_previous():
            await self._repository.delete(user_id=user_id, exercise_name=exercise_name)
            return None

        return await self._repository.save(user_id=user_id, record=current)

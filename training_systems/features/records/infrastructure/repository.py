from datetime import datetime
from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from training_systems.features.records.domain.entities import (
    PersonalRecord,
    RecordSnapshot,
)
from training_systems.features.records.domain.repository import (
    PersonalRecordRepository,
)
from training_systems.infrastructure.database.orm import PersonalRecordModel


class SqlPersonalRecordRepository(PersonalRecordRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_domain(self, model: PersonalRecordModel) -> PersonalRecord:
        return PersonalRecord(
            exercise_name=model.exercise_name,
            category=model.category,
            sets=model.sets,
            reps=model.reps,
            weight=model.weight,
            actual_rpe=model.actual_rpe,
            est_max=model.est_max,
            achieved_at=model.achieved_at,
            history=_history_from_json(model.history),
        )

    async def list_for_user(self, *, user_id: UUID) -> list[PersonalRecord]:
        statement = select(PersonalRecordModel).where(
            col(PersonalRecordModel.user_id) == user_id
        )
        models = (await self._session.scalars(statement)).all()
        return [self._to_domain(model) for model in models]

    async def find_by_exercise(
        self, *, user_id: UUID, exercise_name: str
    ) -> PersonalRecord | None:
        statement = select(PersonalRecordModel).where(
            col(PersonalRecordModel.user_id) == user_id,
            col(PersonalRecordModel.exercise_name) == exercise_name,
        )
        model = await self._session.scalar(statement)
        return self._to_domain(model) if model is not None else None

    async def save(
        self, *, user_id: UUID, record: PersonalRecord
    ) -> PersonalRecord:
        statement = select(PersonalRecordModel).where(
            col(PersonalRecordModel.user_id) == user_id,
            col(PersonalRecordModel.exercise_name) == record.exercise_name,
        )
        existing = await self._session.scalar(statement)
        if existing is None:
            existing = PersonalRecordModel(
                user_id=user_id, exercise_name=record.exercise_name
            )
            self._session.add(existing)
        existing.category = record.category
        existing.sets = record.sets
        existing.reps = record.reps
        existing.weight = record.weight
        existing.actual_rpe = record.actual_rpe
        existing.est_max = record.est_max
        existing.achieved_at = record.achieved_at
        existing.history = _history_to_json(record.history)
        await self._session.flush()
        return record

    async def delete(self, *, user_id: UUID, exercise_name: str) -> None:
        await self._session.execute(
            delete(PersonalRecordModel).where(
                col(PersonalRecordModel.user_id) == user_id,
                col(PersonalRecordModel.exercise_name) == exercise_name,
            )
        )
        await self._session.flush()


def _history_to_json(history: list[RecordSnapshot]) -> list[dict[str, object]]:
    return [
        {
            "sets": snapshot.sets,
            "reps": snapshot.reps,
            "weight": snapshot.weight,
            "actual_rpe": snapshot.actual_rpe,
            "est_max": snapshot.est_max,
            "achieved_at": snapshot.achieved_at.isoformat(),
        }
        for snapshot in history
    ]


def _history_from_json(raw: list[dict[str, object]]) -> list[RecordSnapshot]:
    return [
        RecordSnapshot(
            sets=int(item["sets"]),  # type: ignore[call-overload]
            reps=int(item["reps"]),  # type: ignore[call-overload]
            weight=float(item["weight"]),  # type: ignore[arg-type]
            actual_rpe=float(item["actual_rpe"]),  # type: ignore[arg-type]
            est_max=float(item["est_max"]),  # type: ignore[arg-type]
            achieved_at=datetime.fromisoformat(str(item["achieved_at"])),
        )
        for item in raw
    ]

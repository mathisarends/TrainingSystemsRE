from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from training_system.features.bodyweight.domain.entities import (
    BodyWeightEntry,
    BodyWeightGoal,
    WeightGoalDirection,
)
from training_system.features.bodyweight.domain.repository import (
    BodyWeightRepository,
)
from training_system.infrastructure.database.orm import (
    BodyWeightEntryModel,
    BodyWeightGoalModel,
)


class SqlBodyWeightRepository(BodyWeightRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_entries(self, *, user_id: UUID) -> list[BodyWeightEntry]:
        statement = (
            select(BodyWeightEntryModel)
            .where(BodyWeightEntryModel.user_id == user_id)
            .order_by(col(BodyWeightEntryModel.date).desc())
        )
        models = (await self._session.scalars(statement)).all()
        return [BodyWeightEntry(date=model.date, weight=model.weight) for model in models]

    async def upsert_entry(
        self, *, user_id: UUID, entry: BodyWeightEntry
    ) -> BodyWeightEntry:
        statement = select(BodyWeightEntryModel).where(
            BodyWeightEntryModel.user_id == user_id,
            BodyWeightEntryModel.date == entry.date,
        )
        existing = await self._session.scalar(statement)
        if existing is None:
            existing = BodyWeightEntryModel(user_id=user_id, date=entry.date)
            self._session.add(existing)
        existing.weight = entry.weight
        await self._session.flush()
        return entry

    async def get_goal(self, *, user_id: UUID) -> BodyWeightGoal | None:
        statement = select(BodyWeightGoalModel).where(
            BodyWeightGoalModel.user_id == user_id
        )
        model = await self._session.scalar(statement)
        if model is None:
            return None
        return BodyWeightGoal(
            direction=WeightGoalDirection(model.direction), rate=model.rate
        )

    async def save_goal(
        self, *, user_id: UUID, goal: BodyWeightGoal
    ) -> BodyWeightGoal:
        statement = select(BodyWeightGoalModel).where(
            BodyWeightGoalModel.user_id == user_id
        )
        existing = await self._session.scalar(statement)
        if existing is None:
            existing = BodyWeightGoalModel(user_id=user_id, direction="", rate=0)
            self._session.add(existing)
        existing.direction = goal.direction.value
        existing.rate = goal.rate
        await self._session.flush()
        return goal

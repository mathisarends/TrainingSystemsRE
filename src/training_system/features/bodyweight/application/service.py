from dataclasses import dataclass
from datetime import date
from uuid import UUID

from training_system.features.bodyweight.domain import (
    BodyWeightEntry,
    BodyWeightGoal,
    BodyWeightRepository,
    WeightGoalDirection,
)


@dataclass(frozen=True, slots=True)
class BodyWeightOverview:
    entries: list[BodyWeightEntry]
    goal: BodyWeightGoal


class BodyWeightService:
    def __init__(self, repository: BodyWeightRepository) -> None:
        self._repository = repository

    async def get_overview(self, *, user_id: UUID) -> BodyWeightOverview:
        entries = await self._repository.list_entries(user_id=user_id)
        goal = await self._repository.get_goal(user_id=user_id)
        return BodyWeightOverview(entries=entries, goal=goal or BodyWeightGoal())

    async def upsert_entry(
        self, *, user_id: UUID, entry_date: date, weight: float
    ) -> BodyWeightEntry:
        entry = BodyWeightEntry(date=entry_date, weight=weight)
        return await self._repository.upsert_entry(user_id=user_id, entry=entry)

    async def update_goal(
        self,
        *,
        user_id: UUID,
        direction: WeightGoalDirection | None = None,
        rate: float | None = None,
    ) -> BodyWeightGoal:
        current = await self._repository.get_goal(user_id=user_id) or BodyWeightGoal()
        goal = BodyWeightGoal(
            direction=direction if direction is not None else current.direction,
            rate=rate if rate is not None else current.rate,
        )
        return await self._repository.save_goal(user_id=user_id, goal=goal)

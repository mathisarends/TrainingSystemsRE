from dataclasses import dataclass
from datetime import date, timedelta
from uuid import UUID

from training_systems.features.plans.application.commands import PlanPatch
from training_systems.features.plans.application.errors import (
    InvalidPlanPosition,
    PlanNotFound,
)
from training_systems.features.plans.application.ports import SessionTracker
from training_systems.features.plans.domain import Plan, PlanRepository

MONDAY = 0


@dataclass(frozen=True, slots=True)
class PlanCard:
    plan: Plan
    average_duration_minutes: float | None


class PlanService:
    def __init__(
        self, repository: PlanRepository, session_tracker: SessionTracker
    ) -> None:
        self._repository = repository
        self._session_tracker = session_tracker

    async def create(
        self,
        *,
        user_id: UUID,
        title: str,
        weekdays: list[str],
        block_length: int,
        start_date: date,
        cover_image: str | None,
    ) -> Plan:
        plan = Plan.create(
            user_id=user_id,
            title=title,
            weekdays=weekdays,
            block_length=block_length,
            start_date=start_date,
            cover_image=cover_image,
        )
        return await self._repository.save(plan=plan)

    async def get(self, *, user_id: UUID, plan_id: UUID) -> Plan:
        plan = await self._repository.find_by_id(plan_id=plan_id, user_id=user_id)
        if plan is None:
            raise PlanNotFound(plan_id)
        return plan

    async def list_cards(self, *, user_id: UUID) -> list[PlanCard]:
        plans = await self._repository.list_for_user(user_id=user_id)
        cards = []
        for plan in plans:
            average_duration = await self._repository.average_recorded_duration_minutes(
                plan_id=plan.id
            )
            cards.append(PlanCard(plan=plan, average_duration_minutes=average_duration))
        return cards

    async def most_recently_updated(self, *, user_id: UUID) -> Plan | None:
        return await self._repository.find_most_recently_updated(user_id=user_id)

    async def suggest_start_date(self, *, user_id: UUID) -> date:
        latest = await self._repository.find_most_recently_updated(user_id=user_id)
        if latest is None:
            return _next_monday(date.today())
        return latest.start_date + timedelta(days=latest.block_length * 7)

    async def patch(self, *, user_id: UUID, plan_id: UUID, patch: PlanPatch) -> Plan:
        plan = await self.get(user_id=user_id, plan_id=plan_id)

        if patch.basics is not None:
            basics = patch.basics
            plan.update_basics(
                title=basics.title,
                weekdays=basics.weekdays,
                block_length=basics.block_length,
                start_date=basics.start_date,
                cover_image=basics.cover_image,
            )

        activity = False
        if patch.day_edit is not None:
            edit = patch.day_edit
            try:
                activity = plan.apply_day_edit(
                    week_index=edit.week_index,
                    day_index=edit.day_index,
                    entries=edit.entries,
                )
            except IndexError as error:
                raise InvalidPlanPosition(str(error)) from error

        saved = await self._repository.save(plan=plan)

        if activity and patch.day_edit is not None:
            await self._session_tracker.touch(
                user_id=user_id,
                plan_id=plan_id,
                week_index=patch.day_edit.week_index,
                day_index=patch.day_edit.day_index,
            )

        return saved

    async def delete(self, *, user_id: UUID, plan_id: UUID) -> None:
        deleted = await self._repository.delete(plan_id=plan_id, user_id=user_id)
        if not deleted:
            raise PlanNotFound(plan_id)

    async def apply_progression(
        self,
        *,
        user_id: UUID,
        plan_id: UUID,
        rpe_increment: float,
        deload_last_week: bool,
    ) -> Plan:
        plan = await self.get(user_id=user_id, plan_id=plan_id)
        plan.apply_progression(
            rpe_increment=rpe_increment, deload_last_week=deload_last_week
        )
        return await self._repository.save(plan=plan)


def _next_monday(today: date) -> date:
    days_ahead = (MONDAY - today.weekday()) % 7
    days_ahead = days_ahead or 7
    return today + timedelta(days=days_ahead)

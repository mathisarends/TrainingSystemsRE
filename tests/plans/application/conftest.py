from uuid import UUID

import pytest

from training_systems.features.plans.application.ports import SessionTracker
from training_systems.features.plans.application.service import PlanService
from training_systems.features.plans.domain import Plan, PlanRepository


class FakePlanRepository(PlanRepository):
    def __init__(self) -> None:
        self.plans: dict[UUID, Plan] = {}

    async def find_by_id(self, *, plan_id: UUID, user_id: UUID) -> Plan | None:
        plan = self.plans.get(plan_id)
        if plan is None or plan.user_id != user_id:
            return None
        return plan

    async def list_for_user(self, *, user_id: UUID) -> list[Plan]:
        return [plan for plan in self.plans.values() if plan.user_id == user_id]

    async def find_most_recently_updated(self, *, user_id: UUID) -> Plan | None:
        candidates = await self.list_for_user(user_id=user_id)
        if not candidates:
            return None
        return max(candidates, key=lambda plan: plan.updated_at)

    async def save(self, *, plan: Plan) -> Plan:
        self.plans[plan.id] = plan
        return plan

    async def delete(self, *, plan_id: UUID, user_id: UUID) -> bool:
        plan = await self.find_by_id(plan_id=plan_id, user_id=user_id)
        if plan is None:
            return False
        del self.plans[plan_id]
        return True

    async def average_recorded_duration_minutes(
        self, *, plan_id: UUID
    ) -> float | None:
        return None


class FakeSessionTracker(SessionTracker):
    def __init__(self) -> None:
        self.touches: list[dict[str, object]] = []

    async def touch(
        self, *, user_id: UUID, plan_id: UUID, week_index: int, day_index: int
    ) -> None:
        self.touches.append(
            {
                "user_id": user_id,
                "plan_id": plan_id,
                "week_index": week_index,
                "day_index": day_index,
            }
        )


@pytest.fixture
def plan_repository() -> FakePlanRepository:
    return FakePlanRepository()


@pytest.fixture
def session_tracker() -> FakeSessionTracker:
    return FakeSessionTracker()


@pytest.fixture
def plan_service(
    plan_repository: FakePlanRepository, session_tracker: FakeSessionTracker
) -> PlanService:
    return PlanService(plan_repository, session_tracker)

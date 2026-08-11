from collections.abc import Callable
from datetime import date, timedelta
from uuid import uuid4

import pytest

from training_system.features.plans.application.commands import DayEdit, PlanPatch
from training_system.features.plans.application.errors import (
    InvalidPlanPosition,
    PlanNotFound,
)
from training_system.features.plans.application.service import PlanService
from training_system.features.plans.domain import EntryEdit, Plan

from .conftest import FakePlanRepository, FakeSessionTracker


async def test_create_persists_and_returns_the_plan(
    plan_service: PlanService, plan_repository: FakePlanRepository
) -> None:
    plan = await plan_service.create(
        user_id=uuid4(),
        title="Strength Block",
        weekdays=["Mon", "Wed", "Fri"],
        block_length=3,
        start_date=date(2026, 1, 5),
        cover_image=None,
    )

    assert plan.id in plan_repository.plans
    assert len(plan.weeks) == 3


async def test_get_raises_when_plan_is_missing(plan_service: PlanService) -> None:
    with pytest.raises(PlanNotFound):
        await plan_service.get(user_id=uuid4(), plan_id=uuid4())


async def test_patch_with_activity_touches_the_session_tracker(
    plan_service: PlanService,
    plan_repository: FakePlanRepository,
    session_tracker: FakeSessionTracker,
    make_entry_edit: Callable[..., EntryEdit],
) -> None:
    user_id = uuid4()
    plan = await plan_service.create(
        user_id=user_id,
        title="Strength Block",
        weekdays=["Mon", "Wed", "Fri"],
        block_length=3,
        start_date=date(2026, 1, 5),
        cover_image=None,
    )

    await plan_service.patch(
        user_id=user_id,
        plan_id=plan.id,
        patch=PlanPatch(
            day_edit=DayEdit(
                week_index=0, day_index=0, entries=[make_entry_edit(weight=100.0)]
            )
        ),
    )

    assert len(session_tracker.touches) == 1
    assert session_tracker.touches[0]["week_index"] == 0


async def test_patch_without_activity_does_not_touch_the_session_tracker(
    plan_service: PlanService,
    session_tracker: FakeSessionTracker,
    make_entry_edit: Callable[..., EntryEdit],
) -> None:
    user_id = uuid4()
    plan = await plan_service.create(
        user_id=user_id,
        title="Strength Block",
        weekdays=["Mon", "Wed", "Fri"],
        block_length=3,
        start_date=date(2026, 1, 5),
        cover_image=None,
    )

    await plan_service.patch(
        user_id=user_id,
        plan_id=plan.id,
        patch=PlanPatch(
            day_edit=DayEdit(week_index=0, day_index=0, entries=[make_entry_edit()])
        ),
    )

    assert session_tracker.touches == []


async def test_patch_with_out_of_range_position_raises_invalid_plan_position(
    plan_service: PlanService,
    make_entry_edit: Callable[..., EntryEdit],
) -> None:
    user_id = uuid4()
    plan = await plan_service.create(
        user_id=user_id,
        title="Strength Block",
        weekdays=["Mon", "Wed", "Fri"],
        block_length=3,
        start_date=date(2026, 1, 5),
        cover_image=None,
    )

    with pytest.raises(InvalidPlanPosition):
        await plan_service.patch(
            user_id=user_id,
            plan_id=plan.id,
            patch=PlanPatch(
                day_edit=DayEdit(
                    week_index=99, day_index=0, entries=[make_entry_edit()]
                )
            ),
        )


async def test_delete_raises_when_plan_is_missing(plan_service: PlanService) -> None:
    with pytest.raises(PlanNotFound):
        await plan_service.delete(user_id=uuid4(), plan_id=uuid4())


async def test_delete_removes_an_existing_plan(
    plan_service: PlanService, plan_repository: FakePlanRepository
) -> None:
    user_id = uuid4()
    plan = await plan_service.create(
        user_id=user_id,
        title="Strength Block",
        weekdays=["Mon", "Wed", "Fri"],
        block_length=3,
        start_date=date(2026, 1, 5),
        cover_image=None,
    )

    await plan_service.delete(user_id=user_id, plan_id=plan.id)

    assert plan.id not in plan_repository.plans


async def test_suggest_start_date_defaults_to_next_monday_when_no_plans_exist(
    plan_service: PlanService,
) -> None:
    suggested = await plan_service.suggest_start_date(user_id=uuid4())

    assert suggested.weekday() == 0
    assert suggested > date.today()


async def test_suggest_start_date_continues_after_the_latest_plans_block(
    plan_service: PlanService,
) -> None:
    user_id = uuid4()
    plan = await plan_service.create(
        user_id=user_id,
        title="Strength Block",
        weekdays=["Mon", "Wed", "Fri"],
        block_length=3,
        start_date=date(2026, 1, 5),
        cover_image=None,
    )

    suggested = await plan_service.suggest_start_date(user_id=user_id)

    assert suggested == plan.start_date + timedelta(days=3 * 7)

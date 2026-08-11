from collections.abc import Callable

from training_systems.features.plans.application.progress import progress_percent
from training_systems.features.plans.domain import Plan


def test_progress_percent_is_zero_for_a_freshly_created_plan(
    make_plan: Callable[..., Plan],
) -> None:
    plan = make_plan(weekdays=["Mon", "Wed", "Fri"], block_length=4)

    assert progress_percent(plan) == 0.0


def test_progress_percent_rounds_to_nearest_two_point_five(
    make_plan: Callable[..., Plan],
) -> None:
    plan = make_plan(weekdays=["Mon", "Wed", "Fri"], block_length=4)
    plan.apply_day_edit(week_index=1, day_index=1, entries=[])

    # position 4 of 12 total days -> 33.33% -> rounds to 32.5
    assert progress_percent(plan) == 32.5

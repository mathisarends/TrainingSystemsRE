from collections.abc import Callable

from training_system.features.plans.application.recommendations import (
    compute_weight_recommendations,
)
from training_system.features.plans.domain import EntryEdit, Plan


def test_first_week_never_gets_recommendations(
    make_plan: Callable[..., Plan], make_entry_edit: Callable[..., EntryEdit]
) -> None:
    plan = make_plan()
    plan.apply_day_edit(
        week_index=0, day_index=0, entries=[make_entry_edit(weight=100.0)]
    )

    recommendations = compute_weight_recommendations(plan)

    week0_entry = plan.day_at(week_index=0, day_index=0).entries[0]
    assert week0_entry.id not in recommendations


def test_recommends_previous_week_weight_for_matching_exercise_and_reps(
    make_plan: Callable[..., Plan], make_entry_edit: Callable[..., EntryEdit]
) -> None:
    plan = make_plan()
    plan.apply_day_edit(
        week_index=0, day_index=0, entries=[make_entry_edit(weight=100.0, reps=5)]
    )

    recommendations = compute_weight_recommendations(plan)

    week1_entry = plan.day_at(week_index=1, day_index=0).entries[0]
    assert recommendations[week1_entry.id] == 100.0


def test_no_recommendation_when_previous_entry_has_no_recorded_weight(
    make_plan: Callable[..., Plan], make_entry_edit: Callable[..., EntryEdit]
) -> None:
    plan = make_plan()
    plan.apply_day_edit(week_index=0, day_index=0, entries=[make_entry_edit()])

    recommendations = compute_weight_recommendations(plan)

    week1_entry = plan.day_at(week_index=1, day_index=0).entries[0]
    assert week1_entry.id not in recommendations

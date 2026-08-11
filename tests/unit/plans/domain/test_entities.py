from collections.abc import Callable
from datetime import UTC, datetime

import pytest

from training_system.features.plans.domain import EntryEdit, Plan


def test_create_builds_empty_week_day_structure(
    make_plan: Callable[..., Plan],
) -> None:
    plan = make_plan(weekdays=["Mon", "Wed", "Fri"], block_length=3)

    assert len(plan.weeks) == 3
    assert all(len(week.days) == 3 for week in plan.weeks)
    assert all(day.entries == [] for week in plan.weeks for day in week.days)


def test_apply_day_edit_reports_activity_for_new_entry_with_weight(
    make_plan: Callable[..., Plan], make_entry_edit: Callable[..., EntryEdit]
) -> None:
    plan = make_plan()

    activity = plan.apply_day_edit(
        week_index=0, day_index=0, entries=[make_entry_edit(weight=100.0)]
    )

    assert activity is True
    assert plan.last_used_week_index == 0
    assert plan.last_used_day_index == 0


def test_apply_day_edit_reports_no_activity_for_structure_only_entry(
    make_plan: Callable[..., Plan], make_entry_edit: Callable[..., EntryEdit]
) -> None:
    plan = make_plan()

    activity = plan.apply_day_edit(
        week_index=0, day_index=0, entries=[make_entry_edit()]
    )

    assert activity is False


def test_apply_day_edit_reports_no_activity_when_editing_without_changing_weight(
    make_plan: Callable[..., Plan], make_entry_edit: Callable[..., EntryEdit]
) -> None:
    plan = make_plan()
    plan.apply_day_edit(week_index=0, day_index=0, entries=[make_entry_edit(weight=100.0)])
    existing_entry = plan.day_at(week_index=0, day_index=0).entries[0]

    activity = plan.apply_day_edit(
        week_index=0,
        day_index=0,
        entries=[
            EntryEdit(
                id=existing_entry.id,
                category="Squat",
                exercise_name="Back Squat",
                sets=3,
                reps=5,
                target_rpe=8.0,
                weight=100.0,
            )
        ],
    )

    assert activity is False


def test_apply_day_edit_propagates_structure_but_not_weight_to_future_weeks(
    make_plan: Callable[..., Plan], make_entry_edit: Callable[..., EntryEdit]
) -> None:
    plan = make_plan()

    plan.apply_day_edit(
        week_index=0,
        day_index=0,
        entries=[make_entry_edit(weight=100.0, target_rpe=8.0)],
    )

    future_entry = plan.day_at(week_index=1, day_index=0).entries[0]
    assert future_entry.exercise_name == "Back Squat"
    assert future_entry.sets == 3
    assert future_entry.target_rpe == 8.0
    assert future_entry.weight is None


def test_apply_day_edit_out_of_range_week_raises_index_error(
    make_plan: Callable[..., Plan], make_entry_edit: Callable[..., EntryEdit]
) -> None:
    plan = make_plan()

    with pytest.raises(IndexError):
        plan.apply_day_edit(week_index=99, day_index=0, entries=[make_entry_edit()])


def test_apply_progression_increments_rpe_up_to_cap(
    make_plan: Callable[..., Plan], make_entry_edit: Callable[..., EntryEdit]
) -> None:
    plan = make_plan()
    plan.apply_day_edit(
        week_index=0, day_index=0, entries=[make_entry_edit(target_rpe=8.5)]
    )

    plan.apply_progression(rpe_increment=1, deload_last_week=False)

    week1_entry = plan.day_at(week_index=1, day_index=0).entries[0]
    assert week1_entry.target_rpe == 9.0


def test_apply_progression_deloads_last_week(
    make_plan: Callable[..., Plan], make_entry_edit: Callable[..., EntryEdit]
) -> None:
    plan = make_plan(block_length=3)
    plan.apply_day_edit(
        week_index=0, day_index=0, entries=[make_entry_edit(sets=3, target_rpe=8.0)]
    )
    plan.apply_progression(rpe_increment=1, deload_last_week=False)

    plan.apply_progression(rpe_increment=1, deload_last_week=True)

    last_week_entry = plan.day_at(week_index=2, day_index=0).entries[0]
    assert last_week_entry.sets == 2
    assert last_week_entry.target_rpe == 6.0


def test_apply_progression_does_not_reduce_sets_below_zero(
    make_plan: Callable[..., Plan], make_entry_edit: Callable[..., EntryEdit]
) -> None:
    plan = make_plan(block_length=2)
    plan.apply_day_edit(
        week_index=0, day_index=0, entries=[make_entry_edit(sets=0)]
    )

    plan.apply_progression(rpe_increment=1, deload_last_week=True)

    last_week_entry = plan.day_at(week_index=1, day_index=0).entries[0]
    assert last_week_entry.sets == 0


def test_close_recording_rounds_active_minutes_and_subtracts_inactivity(
    make_plan: Callable[..., Plan],
) -> None:
    plan = make_plan()
    start = datetime(2026, 1, 5, 10, 0, tzinfo=UTC)
    plan.start_recording(week_index=0, day_index=0, at=start)

    duration = plan.close_recording(
        week_index=0, day_index=0, at=start.replace(hour=11, minute=8)
    )

    # 68 minutes elapsed - 35 minutes inactivity = 33, rounded to nearest 5 -> 35
    assert duration == 35
    day = plan.day_at(week_index=0, day_index=0)
    assert day.is_recording is False
    assert day.duration_minutes == 35


def test_close_recording_without_start_time_yields_zero_duration(
    make_plan: Callable[..., Plan],
) -> None:
    plan = make_plan()

    duration = plan.close_recording(
        week_index=0, day_index=0, at=datetime(2026, 1, 5, 10, 0, tzinfo=UTC)
    )

    assert duration == 0

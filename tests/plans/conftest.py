from collections.abc import Callable
from datetime import date
from uuid import uuid4

import pytest

from training_system.features.plans.domain import EntryEdit, Plan


def _make_plan(
    *, weekdays: list[str] | None = None, block_length: int = 3
) -> Plan:
    return Plan.create(
        user_id=uuid4(),
        title="Strength Block",
        weekdays=weekdays if weekdays is not None else ["Mon", "Wed", "Fri"],
        block_length=block_length,
        start_date=date(2026, 1, 5),
    )


@pytest.fixture
def make_plan() -> Callable[..., Plan]:
    return _make_plan


def _make_entry_edit(
    *,
    category: str = "Squat",
    exercise_name: str = "Back Squat",
    sets: int = 3,
    reps: int = 5,
    target_rpe: float = 8.0,
    weight: float | None = None,
    actual_rpe: float | None = None,
) -> EntryEdit:
    return EntryEdit(
        category=category,
        exercise_name=exercise_name,
        sets=sets,
        reps=reps,
        target_rpe=target_rpe,
        weight=weight,
        actual_rpe=actual_rpe,
    )


@pytest.fixture
def make_entry_edit() -> Callable[..., EntryEdit]:
    return _make_entry_edit

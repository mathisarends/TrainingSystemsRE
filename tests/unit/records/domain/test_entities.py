from datetime import UTC, datetime

from training_system.features.records.domain.entities import (
    MAX_HISTORY,
    PersonalRecord,
    RecordSnapshot,
)


def _make_record(*, est_max: float = 150.0) -> PersonalRecord:
    return PersonalRecord(
        exercise_name="Back Squat",
        category="Squat",
        sets=3,
        reps=5,
        weight=100.0,
        actual_rpe=8.0,
        est_max=est_max,
        achieved_at=datetime(2026, 1, 1, tzinfo=UTC),
    )


def _make_snapshot(*, est_max: float) -> RecordSnapshot:
    return RecordSnapshot(
        sets=3,
        reps=5,
        weight=110.0,
        actual_rpe=8.0,
        est_max=est_max,
        achieved_at=datetime(2026, 1, 8, tzinfo=UTC),
    )


def test_replace_with_updates_fields_and_pushes_previous_state_into_history() -> None:
    record = _make_record(est_max=150.0)

    record.replace_with(_make_snapshot(est_max=160.0), category="Squat")

    assert record.est_max == 160.0
    assert record.weight == 110.0
    assert len(record.history) == 1
    assert record.history[0].est_max == 150.0


def test_replace_with_caps_history_at_max_history() -> None:
    record = _make_record(est_max=100.0)

    for est_max in range(100, 100 + MAX_HISTORY + 5):
        record.replace_with(_make_snapshot(est_max=float(est_max)), category="Squat")

    assert len(record.history) == MAX_HISTORY


def test_revert_to_previous_restores_the_prior_snapshot() -> None:
    record = _make_record(est_max=150.0)
    record.replace_with(_make_snapshot(est_max=160.0), category="Squat")

    reverted = record.revert_to_previous()

    assert reverted is True
    assert record.est_max == 150.0
    assert record.history == []


def test_revert_to_previous_returns_false_when_there_is_no_history() -> None:
    record = _make_record()

    reverted = record.revert_to_previous()

    assert reverted is False

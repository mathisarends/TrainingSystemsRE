from uuid import UUID, uuid4

import pytest

from training_systems.features.records.application.errors import RecordNotFound
from training_systems.features.records.application.service import (
    PersonalRecordService,
    UpsertResult,
)


async def _upsert(
    service: PersonalRecordService,
    *,
    user_id: UUID,
    exercise_name: str = "Back Squat",
    est_max: float,
) -> UpsertResult:
    return await service.upsert_record(
        user_id=user_id,
        exercise_name=exercise_name,
        category="Squat",
        sets=3,
        reps=5,
        weight=100.0,
        actual_rpe=8.0,
        est_max=est_max,
    )


async def test_first_upsert_is_always_accepted(
    record_service: PersonalRecordService,
) -> None:
    result = await _upsert(record_service, user_id=uuid4(), est_max=150.0)

    assert result.accepted is True
    assert result.record.est_max == 150.0


async def test_upsert_rejects_a_non_improving_max(
    record_service: PersonalRecordService,
) -> None:
    user_id = uuid4()
    await _upsert(record_service, user_id=user_id, est_max=150.0)

    result = await _upsert(record_service, user_id=user_id, est_max=150.0)

    assert result.accepted is False
    assert result.record.est_max == 150.0


async def test_upsert_accepts_a_new_max_and_records_history(
    record_service: PersonalRecordService,
) -> None:
    user_id = uuid4()
    await _upsert(record_service, user_id=user_id, est_max=150.0)

    result = await _upsert(record_service, user_id=user_id, est_max=160.0)

    assert result.accepted is True
    assert result.record.est_max == 160.0
    assert len(result.record.history) == 1
    assert result.record.history[0].est_max == 150.0


async def test_revert_raises_when_no_record_exists(
    record_service: PersonalRecordService,
) -> None:
    with pytest.raises(RecordNotFound):
        await record_service.revert_to_previous(
            user_id=uuid4(), exercise_name="Back Squat"
        )


async def test_revert_with_history_restores_previous_snapshot(
    record_service: PersonalRecordService,
) -> None:
    user_id = uuid4()
    await _upsert(record_service, user_id=user_id, est_max=150.0)
    await _upsert(record_service, user_id=user_id, est_max=160.0)

    reverted = await record_service.revert_to_previous(
        user_id=user_id, exercise_name="Back Squat"
    )

    assert reverted is not None
    assert reverted.est_max == 150.0
    assert reverted.history == []


async def test_revert_without_history_deletes_the_record(
    record_service: PersonalRecordService,
) -> None:
    user_id = uuid4()
    await _upsert(record_service, user_id=user_id, est_max=150.0)

    reverted = await record_service.revert_to_previous(
        user_id=user_id, exercise_name="Back Squat"
    )

    assert reverted is None
    assert await record_service.list_records(user_id=user_id) == []

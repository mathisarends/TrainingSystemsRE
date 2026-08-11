from training_system.features.records.application import UpsertResult
from training_system.features.records.domain import PersonalRecord
from training_system.features.records.presentation.schemas import (
    PersonalRecordListResponse,
    PersonalRecordResponse,
    RecordSnapshotResponse,
    UpsertRecordResponse,
)


def to_response(record: PersonalRecord) -> PersonalRecordResponse:
    return PersonalRecordResponse(
        exercise_name=record.exercise_name,
        category=record.category,
        sets=record.sets,
        reps=record.reps,
        weight=record.weight,
        actual_rpe=record.actual_rpe,
        est_max=record.est_max,
        achieved_at=record.achieved_at,
        history=[
            RecordSnapshotResponse(
                sets=snapshot.sets,
                reps=snapshot.reps,
                weight=snapshot.weight,
                actual_rpe=snapshot.actual_rpe,
                est_max=snapshot.est_max,
                achieved_at=snapshot.achieved_at,
            )
            for snapshot in record.history
        ],
    )


def to_list_response(records: list[PersonalRecord]) -> PersonalRecordListResponse:
    return PersonalRecordListResponse(items=[to_response(record) for record in records])


def to_upsert_response(result: UpsertResult) -> UpsertRecordResponse:
    return UpsertRecordResponse(
        record=to_response(result.record), accepted=result.accepted
    )

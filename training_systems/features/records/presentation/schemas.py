from datetime import datetime

from pydantic import Field

from training_systems.presentation.schema import Schema


class RecordSnapshotResponse(Schema):
    sets: int
    reps: int
    weight: float
    actual_rpe: float
    est_max: float
    achieved_at: datetime


class PersonalRecordResponse(Schema):
    exercise_name: str
    category: str
    sets: int
    reps: int
    weight: float
    actual_rpe: float
    est_max: float
    achieved_at: datetime
    history: list[RecordSnapshotResponse]


class PersonalRecordListResponse(Schema):
    items: list[PersonalRecordResponse]


class UpsertRecordRequest(Schema):
    category: str
    sets: int = Field(ge=1)
    reps: int = Field(ge=1)
    weight: float = Field(ge=0)
    actual_rpe: float = Field(ge=0, le=10)
    est_max: float = Field(gt=0)


class UpsertRecordResponse(Schema):
    record: PersonalRecordResponse
    accepted: bool

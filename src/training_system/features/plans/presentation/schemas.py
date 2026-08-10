from datetime import date, datetime
from uuid import UUID

from pydantic import Field

from training_system.presentation.schema import Schema


class EntryRequest(Schema):
    id: UUID | None = None
    category: str
    exercise_name: str
    sets: int = Field(ge=0)
    reps: int = Field(ge=0)
    target_rpe: float = Field(ge=0, le=10)
    weight: float | None = None
    actual_rpe: float | None = Field(default=None, ge=0, le=10)
    est_max: float | None = None
    notes: str | None = None


class EntryResponse(Schema):
    id: UUID
    category: str
    exercise_name: str
    sets: int
    reps: int
    target_rpe: float
    weight: float | None
    actual_rpe: float | None
    est_max: float | None
    notes: str | None
    recommended_weight: float | None = None


class DayResponse(Schema):
    id: UUID
    day_index: int
    entries: list[EntryResponse]
    start_time: datetime | None
    end_time: datetime | None
    duration_minutes: int | None
    is_recording: bool


class WeekResponse(Schema):
    id: UUID
    week_index: int
    days: list[DayResponse]


class PlanResponse(Schema):
    id: UUID
    title: str
    weekdays: list[str]
    block_length: int
    start_date: date
    cover_image: str | None
    last_used_week_index: int
    last_used_day_index: int
    updated_at: datetime
    created_at: datetime
    weeks: list[WeekResponse]


class PlanCardResponse(Schema):
    id: UUID
    title: str
    block_length: int
    frequency: int
    updated_at: datetime
    cover_image: str
    picture_url: str | None
    progress_percent: float
    average_duration_minutes: float | None
    last_used_week_index: int | None = None
    last_used_day_index: int | None = None


class PlanCardListResponse(Schema):
    items: list[PlanCardResponse]


class CreatePlanRequest(Schema):
    title: str = Field(min_length=1, max_length=200)
    weekdays: list[str] = Field(min_length=1)
    block_length: int = Field(ge=1)
    start_date: date
    cover_image: str | None = None


class PlanBasicsRequest(Schema):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    weekdays: list[str] | None = Field(default=None, min_length=1)
    block_length: int | None = Field(default=None, ge=1)
    start_date: date | None = None
    cover_image: str | None = None


class DayEditRequest(Schema):
    week_index: int = Field(ge=0)
    day_index: int = Field(ge=0)
    entries: list[EntryRequest]


class PatchPlanRequest(Schema):
    basics: PlanBasicsRequest | None = None
    day_edit: DayEditRequest | None = None


class ProgressionRequest(Schema):
    rpe_increment: float = Field(ge=0.5, le=1)
    deload_last_week: bool = False


class StartDateSuggestionResponse(Schema):
    start_date: date

from datetime import date

from pydantic import Field

from training_system.features.bodyweight.domain import WeightGoalDirection
from training_system.presentation.schema import Schema


class BodyWeightEntryResponse(Schema):
    date: date
    weight: float


class BodyWeightGoalResponse(Schema):
    direction: WeightGoalDirection
    rate: float


class BodyWeightOverviewResponse(Schema):
    entries: list[BodyWeightEntryResponse]
    goal: BodyWeightGoalResponse


class UpdateGoalRequest(Schema):
    direction: WeightGoalDirection | None = None
    rate: float | None = None


class UpsertEntryRequest(Schema):
    weight: float = Field(gt=0)

from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class WeightGoalDirection(StrEnum):
    GAIN = "GAIN"
    LOSE = "LOSE"
    MAINTAIN = "MAINTAIN"


@dataclass(frozen=True, slots=True)
class BodyWeightEntry:
    date: date
    weight: float


@dataclass(frozen=True, slots=True)
class BodyWeightGoal:
    direction: WeightGoalDirection = WeightGoalDirection.MAINTAIN
    rate: float = 0.0

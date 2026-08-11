from training_system.features.bodyweight.application import BodyWeightOverview
from training_system.features.bodyweight.domain import BodyWeightEntry, BodyWeightGoal
from training_system.features.bodyweight.presentation.schemas import (
    BodyWeightEntryResponse,
    BodyWeightGoalResponse,
    BodyWeightOverviewResponse,
)


def to_entry_response(entry: BodyWeightEntry) -> BodyWeightEntryResponse:
    return BodyWeightEntryResponse(date=entry.date, weight=entry.weight)


def to_goal_response(goal: BodyWeightGoal) -> BodyWeightGoalResponse:
    return BodyWeightGoalResponse(direction=goal.direction, rate=goal.rate)


def to_overview_response(
    overview: BodyWeightOverview,
) -> BodyWeightOverviewResponse:
    return BodyWeightOverviewResponse(
        entries=[to_entry_response(entry) for entry in overview.entries],
        goal=to_goal_response(overview.goal),
    )

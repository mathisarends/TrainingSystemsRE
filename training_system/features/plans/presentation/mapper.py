from uuid import UUID

from training_system.features.plans.application import PlanCard
from training_system.features.plans.application.progress import progress_percent
from training_system.features.plans.domain import Day, Entry, Plan, Week
from training_system.features.plans.presentation.schemas import (
    DayResponse,
    EntryResponse,
    PlanCardResponse,
    PlanResponse,
    WeekResponse,
)


def to_entry_response(
    entry: Entry, recommendations: dict[UUID, float]
) -> EntryResponse:
    return EntryResponse(
        id=entry.id,
        category=entry.category,
        exercise_name=entry.exercise_name,
        sets=entry.sets,
        reps=entry.reps,
        target_rpe=entry.target_rpe,
        weight=entry.weight,
        actual_rpe=entry.actual_rpe,
        est_max=entry.est_max,
        notes=entry.notes,
        recommended_weight=recommendations.get(entry.id),
    )


def to_day_response(day: Day, recommendations: dict[UUID, float]) -> DayResponse:
    return DayResponse(
        id=day.id,
        day_index=day.day_index,
        entries=[to_entry_response(entry, recommendations) for entry in day.entries],
        start_time=day.start_time,
        end_time=day.end_time,
        duration_minutes=day.duration_minutes,
        is_recording=day.is_recording,
    )


def to_week_response(week: Week, recommendations: dict[UUID, float]) -> WeekResponse:
    return WeekResponse(
        id=week.id,
        week_index=week.week_index,
        days=[to_day_response(day, recommendations) for day in week.days],
    )


def to_response(plan: Plan, recommendations: dict[UUID, float]) -> PlanResponse:
    return PlanResponse(
        id=plan.id,
        title=plan.title,
        weekdays=plan.weekdays,
        block_length=plan.block_length,
        start_date=plan.start_date,
        cover_image=plan.cover_image,
        last_used_week_index=plan.last_used_week_index,
        last_used_day_index=plan.last_used_day_index,
        updated_at=plan.updated_at,
        created_at=plan.created_at,
        weeks=[to_week_response(week, recommendations) for week in plan.weeks],
    )


def to_card_response(card: PlanCard, picture_url: str | None) -> PlanCardResponse:
    plan = card.plan
    return PlanCardResponse(
        id=plan.id,
        title=plan.title,
        block_length=plan.block_length,
        frequency=len(plan.weekdays),
        updated_at=plan.updated_at,
        cover_image=plan.cover_image or "",
        picture_url=picture_url,
        progress_percent=progress_percent(plan),
        average_duration_minutes=card.average_duration_minutes,
        last_used_week_index=plan.last_used_week_index,
        last_used_day_index=plan.last_used_day_index,
    )

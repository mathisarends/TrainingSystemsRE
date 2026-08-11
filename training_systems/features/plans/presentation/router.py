from typing import Any
from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from training_systems.features.authentication.presentation import AuthenticatedUserId
from training_systems.features.plans.application import (
    DayEdit,
    PlanBasicsUpdate,
    PlanPatch,
    PlanService,
    PlanSummary,
    compute_weight_recommendations,
)
from training_systems.features.plans.application.progress import progress_percent
from training_systems.features.plans.domain import Day, Entry, EntryEdit, Plan, Week
from training_systems.features.plans.presentation.schemas import (
    CreatePlanRequest,
    DayResponse,
    EntryResponse,
    PatchPlanRequest,
    PlanResponse,
    PlanSummaryListResponse,
    PlanSummaryResponse,
    ProgressionRequest,
    StartDateSuggestionResponse,
    WeekResponse,
)
from training_systems.features.users.application import UserService
from training_systems.presentation.schema import ErrorResponse

RESPONSES: dict[int | str, dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
}
NOT_FOUND_RESPONSES: dict[int | str, dict[str, Any]] = {
    **RESPONSES,
    status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
}
PATCH_RESPONSES: dict[int | str, dict[str, Any]] = {
    **NOT_FOUND_RESPONSES,
    status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse},
}

router = APIRouter(prefix="/plans", tags=["plans"], route_class=DishkaRoute)


@router.get(
    "",
    response_model=PlanSummaryListResponse,
    status_code=status.HTTP_200_OK,
    responses=RESPONSES,
)
async def list_plans(
    authenticated_user_id: AuthenticatedUserId,
    plan_service: FromDishka[PlanService],
    user_service: FromDishka[UserService],
    sort: str | None = None,
    limit: int | None = None,
) -> PlanSummaryListResponse:
    summaries = await plan_service.list_summaries(user_id=authenticated_user_id)
    if sort == "-lastUpdated":
        summaries = sorted(
            summaries, key=lambda summary: summary.plan.updated_at, reverse=True
        )
    if limit is not None:
        summaries = summaries[:limit]
    user = await user_service.get_profile(user_id=authenticated_user_id)
    return _to_list_response(summaries, owner_picture_url=user.picture_url)


def _to_list_response(
    summaries: list[PlanSummary], owner_picture_url: str | None
) -> PlanSummaryListResponse:
    return PlanSummaryListResponse(
        items=[
            _to_summary_response(summary, owner_picture_url=owner_picture_url)
            for summary in summaries
        ]
    )


def _to_summary_response(
    summary: PlanSummary, owner_picture_url: str | None
) -> PlanSummaryResponse:
    plan = summary.plan
    return PlanSummaryResponse(
        id=plan.id,
        title=plan.title,
        block_length=plan.block_length,
        frequency=len(plan.weekdays),
        updated_at=plan.updated_at,
        cover_image=plan.cover_image or "",
        owner_picture_url=owner_picture_url,
        progress_percent=progress_percent(plan),
        average_duration_minutes=summary.average_duration_minutes,
        last_used_week_index=plan.last_used_week_index,
        last_used_day_index=plan.last_used_day_index,
    )


@router.get(
    "/suggestions",
    response_model=StartDateSuggestionResponse,
    status_code=status.HTTP_200_OK,
    responses=RESPONSES,
)
async def suggest_plan_start_date(
    authenticated_user_id: AuthenticatedUserId,
    plan_service: FromDishka[PlanService],
) -> StartDateSuggestionResponse:
    start_date = await plan_service.suggest_start_date(user_id=authenticated_user_id)
    return StartDateSuggestionResponse(start_date=start_date)


@router.post(
    "",
    response_model=PlanResponse,
    status_code=status.HTTP_201_CREATED,
    responses=RESPONSES,
)
async def create_plan(
    body: CreatePlanRequest,
    authenticated_user_id: AuthenticatedUserId,
    plan_service: FromDishka[PlanService],
) -> PlanResponse:
    plan = await plan_service.create(
        user_id=authenticated_user_id,
        title=body.title,
        weekdays=body.weekdays,
        block_length=body.block_length,
        start_date=body.start_date,
        cover_image=body.cover_image,
    )
    return _to_response(plan, {})


def _to_response(plan: Plan, recommendations: dict[UUID, float]) -> PlanResponse:
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
        weeks=[_to_week_response(week, recommendations) for week in plan.weeks],
    )


def _to_week_response(week: Week, recommendations: dict[UUID, float]) -> WeekResponse:
    return WeekResponse(
        id=week.id,
        week_index=week.week_index,
        days=[_to_day_response(day, recommendations) for day in week.days],
    )


def _to_day_response(day: Day, recommendations: dict[UUID, float]) -> DayResponse:
    return DayResponse(
        id=day.id,
        day_index=day.day_index,
        entries=[_to_entry_response(entry, recommendations) for entry in day.entries],
        start_time=day.start_time,
        end_time=day.end_time,
        duration_minutes=day.duration_minutes,
        is_recording=day.is_recording,
    )


def _to_entry_response(
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


@router.get(
    "/{plan_id}",
    response_model=PlanResponse,
    status_code=status.HTTP_200_OK,
    responses=NOT_FOUND_RESPONSES,
)
async def get_plan(
    plan_id: UUID,
    authenticated_user_id: AuthenticatedUserId,
    plan_service: FromDishka[PlanService],
) -> PlanResponse:
    plan = await plan_service.get(user_id=authenticated_user_id, plan_id=plan_id)
    recommendations = compute_weight_recommendations(plan)
    return _to_response(plan, recommendations)


@router.patch(
    "/{plan_id}",
    response_model=PlanResponse,
    status_code=status.HTTP_200_OK,
    responses=PATCH_RESPONSES,
)
async def patch_plan(
    plan_id: UUID,
    body: PatchPlanRequest,
    authenticated_user_id: AuthenticatedUserId,
    plan_service: FromDishka[PlanService],
) -> PlanResponse:
    basics = (
        PlanBasicsUpdate(
            title=body.basics.title,
            weekdays=body.basics.weekdays,
            block_length=body.basics.block_length,
            start_date=body.basics.start_date,
            cover_image=body.basics.cover_image,
        )
        if body.basics is not None
        else None
    )
    day_edit = (
        DayEdit(
            week_index=body.day_edit.week_index,
            day_index=body.day_edit.day_index,
            entries=[
                EntryEdit(
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
                )
                for entry in body.day_edit.entries
            ],
        )
        if body.day_edit is not None
        else None
    )
    plan = await plan_service.patch(
        user_id=authenticated_user_id,
        plan_id=plan_id,
        patch=PlanPatch(basics=basics, day_edit=day_edit),
    )
    recommendations = compute_weight_recommendations(plan)
    return _to_response(plan, recommendations)


@router.delete(
    "/{plan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=NOT_FOUND_RESPONSES,
)
async def delete_plan(
    plan_id: UUID,
    authenticated_user_id: AuthenticatedUserId,
    plan_service: FromDishka[PlanService],
) -> None:
    await plan_service.delete(user_id=authenticated_user_id, plan_id=plan_id)


@router.post(
    "/{plan_id}/progressions",
    response_model=PlanResponse,
    status_code=status.HTTP_200_OK,
    responses=NOT_FOUND_RESPONSES,
)
async def apply_plan_progression(
    plan_id: UUID,
    body: ProgressionRequest,
    authenticated_user_id: AuthenticatedUserId,
    plan_service: FromDishka[PlanService],
) -> PlanResponse:
    plan = await plan_service.apply_progression(
        user_id=authenticated_user_id,
        plan_id=plan_id,
        rpe_increment=body.rpe_increment,
        deload_last_week=body.deload_last_week,
    )
    recommendations = compute_weight_recommendations(plan)
    return _to_response(plan, recommendations)

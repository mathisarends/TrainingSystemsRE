from typing import Any
from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from training_system.authentication.presentation import AuthenticatedUserId
from training_system.features.plans.application import (
    DayEdit,
    PlanBasicsUpdate,
    PlanPatch,
    PlanService,
    compute_weight_recommendations,
)
from training_system.features.plans.domain import EntryEdit
from training_system.features.plans.presentation.mapper import (
    to_card_response,
    to_response,
)
from training_system.features.plans.presentation.schemas import (
    CreatePlanRequest,
    PatchPlanRequest,
    PlanCardListResponse,
    PlanResponse,
    ProgressionRequest,
    StartDateSuggestionResponse,
)
from training_system.features.users.application import UserService
from training_system.presentation.schema import ErrorResponse

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
    operation_id="list_plans",
    response_model=PlanCardListResponse,
    status_code=status.HTTP_200_OK,
    responses=RESPONSES,
)
async def list_plans(
    authenticated_user_id: AuthenticatedUserId,
    plan_service: FromDishka[PlanService],
    user_service: FromDishka[UserService],
    sort: str | None = None,
    limit: int | None = None,
) -> PlanCardListResponse:
    cards = await plan_service.list_cards(user_id=authenticated_user_id)
    if sort == "-lastUpdated":
        cards = sorted(cards, key=lambda card: card.plan.updated_at, reverse=True)
    if limit is not None:
        cards = cards[:limit]
    user = await user_service.get_profile(user_id=authenticated_user_id)
    return PlanCardListResponse(
        items=[to_card_response(card, user.picture_url) for card in cards]
    )


@router.get(
    "/suggestions",
    operation_id="suggest_plan_start_date",
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
    operation_id="create_plan",
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
    return to_response(plan, {})


@router.get(
    "/{plan_id}",
    operation_id="get_plan",
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
    return to_response(plan, recommendations)


@router.patch(
    "/{plan_id}",
    operation_id="patch_plan",
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
    return to_response(plan, recommendations)


@router.delete(
    "/{plan_id}",
    operation_id="delete_plan",
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
    operation_id="apply_plan_progression",
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
    return to_response(plan, recommendations)

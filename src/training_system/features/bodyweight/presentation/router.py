from datetime import date
from typing import Any

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from training_system.authentication.presentation import AuthenticatedUserId
from training_system.features.bodyweight.application import BodyWeightService
from training_system.features.bodyweight.presentation.mapper import (
    to_entry_response,
    to_goal_response,
    to_overview_response,
)
from training_system.features.bodyweight.presentation.schemas import (
    BodyWeightEntryResponse,
    BodyWeightGoalResponse,
    BodyWeightOverviewResponse,
    UpdateGoalRequest,
    UpsertEntryRequest,
)
from training_system.presentation.schema import ErrorResponse

RESPONSES: dict[int | str, dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
}

router = APIRouter(prefix="/me/bodyweight", tags=["bodyweight"], route_class=DishkaRoute)


@router.get(
    "",
    operation_id="get_body_weight_overview",
    response_model=BodyWeightOverviewResponse,
    status_code=status.HTTP_200_OK,
    responses=RESPONSES,
)
async def get_body_weight_overview(
    authenticated_user_id: AuthenticatedUserId,
    body_weight_service: FromDishka[BodyWeightService],
) -> BodyWeightOverviewResponse:
    overview = await body_weight_service.get_overview(user_id=authenticated_user_id)
    return to_overview_response(overview)


@router.patch(
    "",
    operation_id="update_body_weight_goal",
    response_model=BodyWeightGoalResponse,
    status_code=status.HTTP_200_OK,
    responses=RESPONSES,
)
async def update_body_weight_goal(
    body: UpdateGoalRequest,
    authenticated_user_id: AuthenticatedUserId,
    body_weight_service: FromDishka[BodyWeightService],
) -> BodyWeightGoalResponse:
    goal = await body_weight_service.update_goal(
        user_id=authenticated_user_id,
        direction=body.direction,
        rate=body.rate,
    )
    return to_goal_response(goal)


@router.put(
    "/entries/{entry_date}",
    operation_id="upsert_body_weight_entry",
    response_model=BodyWeightEntryResponse,
    status_code=status.HTTP_200_OK,
    responses=RESPONSES,
)
async def upsert_body_weight_entry(
    entry_date: date,
    body: UpsertEntryRequest,
    authenticated_user_id: AuthenticatedUserId,
    body_weight_service: FromDishka[BodyWeightService],
) -> BodyWeightEntryResponse:
    entry = await body_weight_service.upsert_entry(
        user_id=authenticated_user_id,
        entry_date=entry_date,
        weight=body.weight,
    )
    return to_entry_response(entry)

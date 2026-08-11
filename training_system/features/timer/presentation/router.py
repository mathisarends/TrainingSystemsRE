from typing import Any

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from training_system.authentication.presentation import AuthenticatedUserId
from training_system.features.timer.application import TimerService
from training_system.features.timer.presentation.schemas import TimerStatusResponse
from training_system.presentation.schema import ErrorResponse

RESPONSES: dict[int | str, dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
}

router = APIRouter(prefix="/me/timer", tags=["timer"], route_class=DishkaRoute)


@router.put(
    "",
    operation_id="start_rest_timer",
    response_model=TimerStatusResponse,
    status_code=status.HTTP_200_OK,
    responses=RESPONSES,
)
async def start_rest_timer(
    authenticated_user_id: AuthenticatedUserId,
    timer_service: FromDishka[TimerService],
) -> TimerStatusResponse:
    await timer_service.start(user_id=authenticated_user_id)
    return TimerStatusResponse(active=True)


@router.delete(
    "",
    operation_id="stop_rest_timer",
    response_model=TimerStatusResponse,
    status_code=status.HTTP_200_OK,
    responses=RESPONSES,
)
async def stop_rest_timer(
    authenticated_user_id: AuthenticatedUserId,
    timer_service: FromDishka[TimerService],
) -> TimerStatusResponse:
    await timer_service.stop(user_id=authenticated_user_id)
    return TimerStatusResponse(active=False)

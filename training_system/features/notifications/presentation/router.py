from typing import Any

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from training_system.features.authentication.presentation import AuthenticatedUserId
from training_system.features.notifications.application import (
    UnseenCompletionService,
)
from training_system.features.notifications.presentation.mapper import (
    to_list_response,
)
from training_system.features.notifications.presentation.schemas import (
    ClearNotificationsResponse,
    UnseenCompletionListResponse,
)
from training_system.presentation.schema import ErrorResponse

RESPONSES: dict[int | str, dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
}

router = APIRouter(
    prefix="/me/notifications", tags=["notifications"], route_class=DishkaRoute
)


@router.get(
    "",
    operation_id="list_unseen_completions",
    response_model=UnseenCompletionListResponse,
    status_code=status.HTTP_200_OK,
    responses=RESPONSES,
)
async def list_unseen_completions(
    authenticated_user_id: AuthenticatedUserId,
    unseen_completion_service: FromDishka[UnseenCompletionService],
) -> UnseenCompletionListResponse:
    completions = await unseen_completion_service.list_unseen(
        user_id=authenticated_user_id
    )
    return to_list_response(completions)


@router.delete(
    "",
    operation_id="clear_unseen_completions",
    response_model=ClearNotificationsResponse,
    status_code=status.HTTP_200_OK,
    responses=RESPONSES,
)
async def clear_unseen_completions(
    authenticated_user_id: AuthenticatedUserId,
    unseen_completion_service: FromDishka[UnseenCompletionService],
) -> ClearNotificationsResponse:
    cleared_count = await unseen_completion_service.clear_seen(
        user_id=authenticated_user_id
    )
    return ClearNotificationsResponse(cleared_count=cleared_count)

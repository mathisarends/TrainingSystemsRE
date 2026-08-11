from typing import Any

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from training_systems.features.authentication.presentation import AuthenticatedUserId
from training_systems.features.notifications.application import (
    UnseenCompletionService,
)
from training_systems.features.notifications.domain import UnseenCompletion
from training_systems.features.notifications.presentation.schemas import (
    ClearNotificationsResponse,
    UnseenCompletionListResponse,
    UnseenCompletionResponse,
)
from training_systems.presentation.schema import ErrorResponse

RESPONSES: dict[int | str, dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
}

router = APIRouter(
    prefix="/me/notifications", tags=["notifications"], route_class=DishkaRoute
)


@router.get(
    "",
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
    return _to_list_response(completions)


def _to_list_response(
    completions: list[UnseenCompletion],
) -> UnseenCompletionListResponse:
    return UnseenCompletionListResponse(
        items=[
            UnseenCompletionResponse(id=item.id, completed_at=item.completed_at)
            for item in completions
        ]
    )


@router.delete(
    "",
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

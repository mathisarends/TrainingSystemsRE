from typing import Any

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from training_system.features.authentication.presentation import AuthenticatedUserId
from training_system.features.push.application import PushSubscriptionService
from training_system.features.push.presentation.schemas import (
    PushSubscriptionResponse,
    RegisterPushSubscriptionRequest,
)
from training_system.presentation.schema import ErrorResponse

RESPONSES: dict[int | str, dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
}

router = APIRouter(prefix="/me/push", tags=["push"], route_class=DishkaRoute)


@router.put(
    "",
    response_model=PushSubscriptionResponse,
    status_code=status.HTTP_200_OK,
    responses=RESPONSES,
)
async def register_push_subscription(
    body: RegisterPushSubscriptionRequest,
    authenticated_user_id: AuthenticatedUserId,
    push_subscription_service: FromDishka[PushSubscriptionService],
) -> PushSubscriptionResponse:
    subscription = await push_subscription_service.register(
        user_id=authenticated_user_id,
        endpoint=body.endpoint,
        p256dh=body.keys.p256dh,
        auth=body.keys.auth,
    )
    return PushSubscriptionResponse(endpoint=subscription.endpoint)

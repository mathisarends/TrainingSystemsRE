from typing import Any

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from training_system.features.authentication.presentation import AuthenticatedUserId
from training_system.features.users.application import UserService
from training_system.features.users.presentation.mapper import to_response
from training_system.features.users.presentation.schemas import (
    UpdateUserRequest,
    UserResponse,
)
from training_system.presentation.schema import ErrorResponse

AUTHENTICATION_RESPONSES: dict[int | str, dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
}
NOT_FOUND_RESPONSES: dict[int | str, dict[str, Any]] = {
    **AUTHENTICATION_RESPONSES,
    status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
}

router = APIRouter(prefix="/me", tags=["users"], route_class=DishkaRoute)


@router.get(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses=NOT_FOUND_RESPONSES,
)
async def get_own_profile(
    authenticated_user_id: AuthenticatedUserId,
    user_service: FromDishka[UserService],
) -> UserResponse:
    user = await user_service.get_profile(user_id=authenticated_user_id)
    return to_response(user)


@router.patch(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses=NOT_FOUND_RESPONSES,
)
async def update_own_profile(
    body: UpdateUserRequest,
    authenticated_user_id: AuthenticatedUserId,
    user_service: FromDishka[UserService],
) -> UserResponse:
    user = await user_service.update_profile(
        user_id=authenticated_user_id,
        name=body.name,
        picture_url=body.picture_url,
    )
    return to_response(user)


@router.delete(
    "",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    responses=AUTHENTICATION_RESPONSES,
)
async def delete_own_account(
    authenticated_user_id: AuthenticatedUserId,
    user_service: FromDishka[UserService],
) -> None:
    await user_service.delete_account(user_id=authenticated_user_id)

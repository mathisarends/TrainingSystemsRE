
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Request, Response, status

from training_system.authentication.application import AuthService
from training_system.authentication.infrastructure.settings import (
    AuthenticationSettings,
)
from training_system.authentication.presentation.cookies import (
    clear_session_cookie,
    set_session_cookie,
)
from training_system.authentication.presentation.schemas import GoogleLoginRequest
from training_system.features.users.presentation.mapper import to_response
from training_system.features.users.presentation.schemas import UserResponse
from training_system.presentation.schema import ErrorResponse

router = APIRouter(prefix="/auth", tags=["authentication"], route_class=DishkaRoute)


@router.post(
    "/google",
    operation_id="login_with_google",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse}},
)
async def login_with_google(
    body: GoogleLoginRequest,
    response: Response,
    auth_service: FromDishka[AuthService],
    settings: FromDishka[AuthenticationSettings],
) -> UserResponse:
    result = await auth_service.login_with_google(credential=body.credential)
    set_session_cookie(response, session=result.session, settings=settings)
    return to_response(result.user)


@router.delete(
    "/session",
    operation_id="end_session",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def end_session(
    request: Request,
    response: Response,
    auth_service: FromDishka[AuthService],
    settings: FromDishka[AuthenticationSettings],
) -> None:
    token = request.cookies.get(settings.cookie_name)
    if token is not None:
        await auth_service.logout(token=token)
    clear_session_cookie(response, settings=settings)

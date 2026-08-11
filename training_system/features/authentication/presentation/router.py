from typing import Any

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse

from training_system.features.authentication.application import (
    GoogleOAuthFlow,
    PasswordAuthFlow,
    SessionRefresher,
)
from training_system.features.authentication.infrastructure.auth_settings import (
    AuthSettings,
)
from training_system.features.authentication.presentation.cookies import (
    clear_auth_cookies,
    set_auth_cookies,
)
from training_system.features.authentication.presentation.dependencies import (
    RefreshAuthenticatedUserId,
)
from training_system.features.authentication.presentation.oauth_popup import (
    OAuthPopupResponse,
)
from training_system.features.authentication.presentation.oauth_state_cookies import (
    GoogleOAuthStateCookies,
)
from training_system.features.authentication.presentation.schemas import (
    LoginRequest,
    RegisterRequest,
)
from training_system.features.users.presentation.mapper import to_response
from training_system.features.users.presentation.schemas import UserResponse
from training_system.presentation.schema import ErrorResponse
from training_system.settings import AppSettings

router = APIRouter(prefix="/auth", tags=["authentication"], route_class=DishkaRoute)

_UNAUTHORIZED: dict[int | str, dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse}
}


@router.get(
    "/google/login",
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    response_model=None,
)
async def google_login(
    google_oauth_flow: FromDishka[GoogleOAuthFlow],
    state_cookies: FromDishka[GoogleOAuthStateCookies],
) -> RedirectResponse:
    authorization_request = google_oauth_flow.login()

    redirect_response = RedirectResponse(
        url=authorization_request.authorization_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )
    state_cookies.set(response=redirect_response, state=authorization_request.state)
    return redirect_response


@router.get(
    "/google/callback",
    response_model=None,
    include_in_schema=False,
)
async def google_callback(
    request: Request,
    google_oauth_flow: FromDishka[GoogleOAuthFlow],
    state_cookies: FromDishka[GoogleOAuthStateCookies],
    auth_settings: FromDishka[AuthSettings],
    app_settings: FromDishka[AppSettings],
    code: str | None = Query(default=None, min_length=1, max_length=4096),
    state: str = Query(min_length=1, max_length=4096),
    error: str | None = Query(default=None, min_length=1, max_length=256),
) -> HTMLResponse:
    result = await google_oauth_flow.callback(
        code=code,
        state=state,
        error=error,
        expected_oauth_state=state_cookies.read(request=request),
    )

    if result.succeeded and result.session is not None:
        response = OAuthPopupResponse.success(
            target_origin=auth_settings.frontend_base_url
        )
        set_auth_cookies(
            response,
            session=result.session,
            auth_settings=auth_settings,
            app_settings=app_settings,
        )
    else:
        response = OAuthPopupResponse.error(
            target_origin=auth_settings.frontend_base_url,
            reason=result.error_reason or "invalid_credentials",
        )

    state_cookies.clear(response)
    return response


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_409_CONFLICT: {"model": ErrorResponse}},
)
async def register_with_password(
    body: RegisterRequest,
    response: Response,
    password_auth_flow: FromDishka[PasswordAuthFlow],
    auth_settings: FromDishka[AuthSettings],
    app_settings: FromDishka[AppSettings],
) -> UserResponse:
    result = await password_auth_flow.register(
        email=body.email, password=body.password, name=body.name
    )
    set_auth_cookies(
        response,
        session=result.session,
        auth_settings=auth_settings,
        app_settings=app_settings,
    )
    return to_response(result.user)


@router.post(
    "/login",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses=_UNAUTHORIZED,
)
async def login_with_password(
    body: LoginRequest,
    response: Response,
    password_auth_flow: FromDishka[PasswordAuthFlow],
    auth_settings: FromDishka[AuthSettings],
    app_settings: FromDishka[AppSettings],
) -> UserResponse:
    result = await password_auth_flow.login(email=body.email, password=body.password)
    set_auth_cookies(
        response,
        session=result.session,
        auth_settings=auth_settings,
        app_settings=app_settings,
    )
    return to_response(result.user)


@router.post(
    "/logout",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def logout(
    response: Response,
    auth_settings: FromDishka[AuthSettings],
) -> None:
    clear_auth_cookies(response, auth_settings=auth_settings)


@router.post(
    "/refresh",
    response_model=None,
    status_code=status.HTTP_204_NO_CONTENT,
    responses=_UNAUTHORIZED,
)
async def refresh(
    authenticated_user_id: RefreshAuthenticatedUserId,
    response: Response,
    session_refresher: FromDishka[SessionRefresher],
    auth_settings: FromDishka[AuthSettings],
    app_settings: FromDishka[AppSettings],
) -> None:
    session = await session_refresher.refresh(user_id=authenticated_user_id)
    set_auth_cookies(
        response,
        session=session,
        auth_settings=auth_settings,
        app_settings=app_settings,
    )

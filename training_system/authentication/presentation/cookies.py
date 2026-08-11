from fastapi import Response

from training_system.authentication.application.schemas import AuthSession
from training_system.authentication.infrastructure.auth_settings import AuthSettings
from training_system.settings import AppSettings

_SECONDS_PER_MINUTE = 60
_SECONDS_PER_DAY = 60 * 60 * 24


def set_auth_cookies(
    response: Response,
    *,
    session: AuthSession,
    auth_settings: AuthSettings,
    app_settings: AppSettings,
) -> None:
    _set_cookie(
        response,
        key=auth_settings.access_token_cookie_name,
        value=session.access_token,
        max_age=auth_settings.jwt_access_token_expire_minutes * _SECONDS_PER_MINUTE,
        auth_settings=auth_settings,
        app_settings=app_settings,
    )
    _set_cookie(
        response,
        key=auth_settings.refresh_token_cookie_name,
        value=session.refresh_token,
        max_age=auth_settings.jwt_refresh_token_expire_days * _SECONDS_PER_DAY,
        auth_settings=auth_settings,
        app_settings=app_settings,
    )


def clear_auth_cookies(response: Response, *, auth_settings: AuthSettings) -> None:
    response.delete_cookie(key=auth_settings.access_token_cookie_name, path="/")
    response.delete_cookie(key=auth_settings.refresh_token_cookie_name, path="/")


def _set_cookie(
    response: Response,
    *,
    key: str,
    value: str,
    max_age: int,
    auth_settings: AuthSettings,
    app_settings: AppSettings,
) -> None:
    is_prod = not app_settings.is_local
    same_site = (
        auth_settings.cookie_samesite_prod
        if is_prod
        else auth_settings.cookie_samesite_dev
    )
    response.set_cookie(
        key=key,
        value=value,
        httponly=True,
        secure=is_prod,
        samesite=same_site,
        path="/",
        max_age=max_age,
    )

from datetime import UTC, datetime

from fastapi import Response

from training_system.authentication.application.ports import Session
from training_system.authentication.infrastructure.settings import (
    AuthenticationSettings,
)


def set_session_cookie(
    response: Response, *, session: Session, settings: AuthenticationSettings
) -> None:
    max_age = max(0, int((session.expires_at - datetime.now(UTC)).total_seconds()))
    response.set_cookie(
        key=settings.cookie_name,
        value=session.token,
        max_age=max_age,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        path="/",
    )


def clear_session_cookie(
    response: Response, *, settings: AuthenticationSettings
) -> None:
    response.delete_cookie(
        key=settings.cookie_name,
        path="/",
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
    )

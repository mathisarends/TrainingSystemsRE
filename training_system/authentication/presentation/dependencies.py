from typing import Annotated, cast
from uuid import UUID

from fastapi import Depends
from starlette.requests import HTTPConnection

from training_system.authentication.application import (
    AuthenticationFailed,
    SessionStore,
)
from training_system.authentication.infrastructure.settings import (
    AuthenticationSettings,
)


async def _session_store(connection: HTTPConnection) -> SessionStore:
    store = await connection.state.dishka_container.get(SessionStore)
    return cast(SessionStore, store)


async def _authentication_settings(
    connection: HTTPConnection,
) -> AuthenticationSettings:
    settings = await connection.state.dishka_container.get(AuthenticationSettings)
    return cast(AuthenticationSettings, settings)


async def authenticated_user_id(
    connection: HTTPConnection,
    session_store: Annotated[SessionStore, Depends(_session_store)],
    settings: Annotated[AuthenticationSettings, Depends(_authentication_settings)],
) -> UUID:
    token = connection.cookies.get(settings.cookie_name)
    if token is None:
        raise AuthenticationFailed
    principal = await session_store.get(token=token)
    if principal is None:
        raise AuthenticationFailed
    return principal.user_id


AuthenticatedUserId = Annotated[UUID, Depends(authenticated_user_id)]

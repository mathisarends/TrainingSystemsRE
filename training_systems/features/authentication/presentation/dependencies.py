from typing import Annotated, cast
from uuid import UUID

from fastapi import Depends
from starlette.requests import HTTPConnection

from training_systems.features.authentication.application import (
    SessionExpiredException,
    SessionInvalidException,
    TokenIssuer,
    TokenPayload,
    TokenType,
)
from training_systems.features.authentication.infrastructure.auth_settings import (
    AuthSettings,
)


class AuthenticationRequired(Exception):
    """No usable token was present on the request for the expected cookie."""


async def _token_issuer(connection: HTTPConnection) -> TokenIssuer:
    issuer = await connection.state.dishka_container.get(TokenIssuer)
    return cast(TokenIssuer, issuer)


async def _auth_settings(connection: HTTPConnection) -> AuthSettings:
    settings = await connection.state.dishka_container.get(AuthSettings)
    return cast(AuthSettings, settings)


async def _cookie_token_payload(
    connection: HTTPConnection,
    token_issuer: TokenIssuer,
    *,
    cookie_name: str,
    expected_type: TokenType,
) -> TokenPayload:
    token = connection.cookies.get(cookie_name)
    if token is None:
        raise AuthenticationRequired
    try:
        return token_issuer.validate(token=token, expected_type=expected_type)
    except (SessionExpiredException, SessionInvalidException) as error:
        raise AuthenticationRequired from error


async def _access_token_payload(
    connection: HTTPConnection,
    token_issuer: Annotated[TokenIssuer, Depends(_token_issuer)],
    settings: Annotated[AuthSettings, Depends(_auth_settings)],
) -> TokenPayload:
    return await _cookie_token_payload(
        connection,
        token_issuer,
        cookie_name=settings.access_token_cookie_name,
        expected_type=TokenType.ACCESS,
    )


async def _refresh_token_payload(
    connection: HTTPConnection,
    token_issuer: Annotated[TokenIssuer, Depends(_token_issuer)],
    settings: Annotated[AuthSettings, Depends(_auth_settings)],
) -> TokenPayload:
    return await _cookie_token_payload(
        connection,
        token_issuer,
        cookie_name=settings.refresh_token_cookie_name,
        expected_type=TokenType.REFRESH,
    )


async def authenticated_user_id(
    payload: Annotated[TokenPayload, Depends(_access_token_payload)],
) -> UUID:
    return payload.user_id


async def refresh_authenticated_user_id(
    payload: Annotated[TokenPayload, Depends(_refresh_token_payload)],
) -> UUID:
    return payload.user_id


AuthenticatedUserId = Annotated[UUID, Depends(authenticated_user_id)]
RefreshAuthenticatedUserId = Annotated[UUID, Depends(refresh_authenticated_user_id)]

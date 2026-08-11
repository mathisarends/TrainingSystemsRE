from datetime import UTC, datetime, timedelta
from typing import TypedDict, cast
from uuid import UUID

import jwt

from training_systems.features.authentication.application.exceptions import (
    SessionExpiredException,
    SessionInvalidException,
)
from training_systems.features.authentication.application.ports import TokenIssuer
from training_systems.features.authentication.application.schemas import (
    AuthSession,
    TokenPayload,
    TokenType,
)
from training_systems.features.authentication.infrastructure.auth_settings import (
    AuthSettings,
)


class _JwtPayload(TypedDict):
    sub: str
    iat: int | float
    exp: int | float
    type: str


class JwtTokenIssuer(TokenIssuer):
    def __init__(self, settings: AuthSettings) -> None:
        self._settings = settings

    def create_session(self, *, user_id: UUID) -> AuthSession:
        now = datetime.now(UTC)
        access_token = self._encode(
            user_id,
            now,
            now + timedelta(minutes=self._settings.jwt_access_token_expire_minutes),
            token_type=TokenType.ACCESS,
        )
        refresh_token = self._encode(
            user_id,
            now,
            now + timedelta(days=self._settings.jwt_refresh_token_expire_days),
            token_type=TokenType.REFRESH,
        )
        return AuthSession(access_token=access_token, refresh_token=refresh_token)

    def validate(
        self, *, token: str, expected_type: TokenType = TokenType.ACCESS
    ) -> TokenPayload:
        raw = self._decode(token)
        if raw.get("type") != expected_type.value:
            raise SessionInvalidException(
                f"Expected token type '{expected_type.value}'"
            )
        return self._to_payload(raw)

    def _encode(
        self, user_id: UUID, iat: datetime, exp: datetime, token_type: TokenType
    ) -> str:
        return jwt.encode(
            {
                "sub": str(user_id),
                "iat": iat,
                "exp": exp,
                "type": token_type.value,
            },
            self._settings.jwt_secret,
            algorithm=self._settings.jwt_algorithm,
        )

    def _decode(self, token: str) -> _JwtPayload:
        try:
            return cast(
                _JwtPayload,
                jwt.decode(
                    token,
                    self._settings.jwt_secret,
                    algorithms=[self._settings.jwt_algorithm],
                ),
            )
        except jwt.ExpiredSignatureError as exc:
            raise SessionExpiredException("Token has expired") from exc
        except jwt.InvalidTokenError as exc:
            raise SessionInvalidException(f"Invalid token: {exc}") from exc

    def _to_payload(self, raw: _JwtPayload) -> TokenPayload:
        user_id_raw = raw.get("sub")
        if not user_id_raw:
            raise SessionInvalidException("Token is missing subject claim")
        try:
            user_id = UUID(user_id_raw)
        except ValueError as exc:
            raise SessionInvalidException("Token subject is not a valid UUID") from exc

        exp_raw = raw.get("exp")
        if not isinstance(exp_raw, (int, float)):
            raise SessionInvalidException("Token expiration claim is invalid")

        return TokenPayload(
            user_id=user_id, expires_at=datetime.fromtimestamp(exp_raw, tz=UTC)
        )

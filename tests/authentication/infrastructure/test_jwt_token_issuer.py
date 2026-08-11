from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest

from training_systems.features.authentication.application.exceptions import (
    SessionExpiredException,
    SessionInvalidException,
)
from training_systems.features.authentication.application.schemas import TokenType
from training_systems.features.authentication.infrastructure.auth_settings import (
    AuthSettings,
)
from training_systems.features.authentication.infrastructure.jwt_token_issuer import (
    JwtTokenIssuer,
)


@pytest.fixture
def settings() -> AuthSettings:
    return AuthSettings(jwt_secret="test-secret-at-least-32-bytes-long")


@pytest.fixture
def issuer(settings: AuthSettings) -> JwtTokenIssuer:
    return JwtTokenIssuer(settings)


def test_create_session_issues_a_validatable_access_and_refresh_token(
    issuer: JwtTokenIssuer,
) -> None:
    user_id = uuid4()

    session = issuer.create_session(user_id=user_id)

    access_payload = issuer.validate(
        token=session.access_token, expected_type=TokenType.ACCESS
    )
    refresh_payload = issuer.validate(
        token=session.refresh_token, expected_type=TokenType.REFRESH
    )
    assert access_payload.user_id == user_id
    assert refresh_payload.user_id == user_id


def test_validate_rejects_a_refresh_token_presented_as_an_access_token(
    issuer: JwtTokenIssuer,
) -> None:
    session = issuer.create_session(user_id=uuid4())

    with pytest.raises(SessionInvalidException):
        issuer.validate(token=session.refresh_token, expected_type=TokenType.ACCESS)


def test_validate_rejects_an_expired_token(
    issuer: JwtTokenIssuer, settings: AuthSettings
) -> None:
    now = datetime.now(UTC)
    expired_token = jwt.encode(
        {
            "sub": str(uuid4()),
            "iat": now - timedelta(hours=1),
            "exp": now - timedelta(minutes=1),
            "type": TokenType.ACCESS.value,
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(SessionExpiredException):
        issuer.validate(token=expired_token)


def test_validate_rejects_a_token_signed_with_a_different_secret(
    issuer: JwtTokenIssuer, settings: AuthSettings
) -> None:
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "iat": now,
            "exp": now + timedelta(minutes=15),
            "type": TokenType.ACCESS.value,
        },
        "a-different-secret-that-is-also-32-bytes-long",
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(SessionInvalidException):
        issuer.validate(token=token)


def test_validate_rejects_a_token_missing_the_subject_claim(
    issuer: JwtTokenIssuer, settings: AuthSettings
) -> None:
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "iat": now,
            "exp": now + timedelta(minutes=15),
            "type": TokenType.ACCESS.value,
        },
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    with pytest.raises(SessionInvalidException):
        issuer.validate(token=token)

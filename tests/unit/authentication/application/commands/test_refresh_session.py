from uuid import uuid4

import pytest

from training_system.features.authentication.application import SessionRefresher
from training_system.features.authentication.application.exceptions import (
    SessionInvalidException,
)
from training_system.features.users.domain import User

from ..conftest import FakeTokenIssuer, FakeUserRepository


@pytest.fixture
def refresher(
    user_repository: FakeUserRepository, token_issuer: FakeTokenIssuer
) -> SessionRefresher:
    return SessionRefresher(user_repository, token_issuer)


async def test_refresh_issues_a_new_session_for_an_existing_user(
    refresher: SessionRefresher,
    user_repository: FakeUserRepository,
    token_issuer: FakeTokenIssuer,
) -> None:
    user = await user_repository.save(
        user=User(name="Alice", email="alice@example.com")
    )

    session = await refresher.refresh(user_id=user.id)

    assert session.access_token == f"access:{user.id}"
    assert token_issuer.issued_for == [user.id]


async def test_refresh_rejects_an_unknown_user(refresher: SessionRefresher) -> None:
    with pytest.raises(SessionInvalidException):
        await refresher.refresh(user_id=uuid4())

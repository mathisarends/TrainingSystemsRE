from uuid import uuid4

import pytest

from training_system.features.users.application.service import (
    UserNotFound,
    UserService,
)
from training_system.features.users.domain import User

from .conftest import FakeUserRepository


async def test_get_profile_raises_when_the_user_does_not_exist(
    user_service: UserService,
) -> None:
    with pytest.raises(UserNotFound):
        await user_service.get_profile(user_id=uuid4())


async def test_update_profile_changes_only_the_given_fields(
    user_service: UserService, user_repository: FakeUserRepository
) -> None:
    user = User(name="Alice", email="alice@example.com")
    await user_repository.save(user=user)

    updated = await user_service.update_profile(user_id=user.id, name="Alicia")

    assert updated.name == "Alicia"
    assert updated.email == "alice@example.com"


async def test_delete_account_removes_the_user(
    user_service: UserService, user_repository: FakeUserRepository
) -> None:
    user = User(name="Alice", email="alice@example.com")
    await user_repository.save(user=user)

    await user_service.delete_account(user_id=user.id)

    assert await user_repository.find_by_id(user_id=user.id) is None

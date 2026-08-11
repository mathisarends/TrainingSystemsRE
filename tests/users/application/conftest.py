from uuid import UUID

import pytest

from training_systems.features.users.application.service import UserService
from training_systems.features.users.domain import User, UserRepository


class FakeUserRepository(UserRepository):
    def __init__(self) -> None:
        self.users: dict[UUID, User] = {}

    async def find_by_id(self, *, user_id: UUID) -> User | None:
        return self.users.get(user_id)

    async def find_by_email(self, *, email: str) -> User | None:
        return next(
            (user for user in self.users.values() if user.email == email), None
        )

    async def save(self, *, user: User) -> User:
        self.users[user.id] = user
        return user

    async def delete(self, *, user_id: UUID) -> None:
        self.users.pop(user_id, None)


@pytest.fixture
def user_repository() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def user_service(user_repository: FakeUserRepository) -> UserService:
    return UserService(user_repository)

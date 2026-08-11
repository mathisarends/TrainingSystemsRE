from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from training_system.features.users.application import UserService
from training_system.features.users.domain import UserRepository
from training_system.features.users.infrastructure.repository import (
    SqlUserRepository,
)


class UserProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def user_repository(self, session: AsyncSession) -> UserRepository:
        return SqlUserRepository(session)

    @provide(scope=Scope.REQUEST)
    def user_service(self, repository: UserRepository) -> UserService:
        return UserService(repository)

from abc import ABC, abstractmethod
from uuid import UUID

from training_systems.features.users.domain.entities import User


class UserRepository(ABC):
    @abstractmethod
    async def find_by_id(self, *, user_id: UUID) -> User | None: ...

    @abstractmethod
    async def find_by_email(self, *, email: str) -> User | None: ...

    @abstractmethod
    async def save(self, *, user: User) -> User: ...

    @abstractmethod
    async def delete(self, *, user_id: UUID) -> None: ...

from abc import ABC, abstractmethod

from training_system.features.authentication.domain.entities import AuthIdentity


class AuthIdentityRepository(ABC):
    @abstractmethod
    async def find_by_provider_subject(
        self, *, provider: str, subject: str
    ) -> AuthIdentity | None: ...

    @abstractmethod
    async def save(self, *, identity: AuthIdentity) -> AuthIdentity: ...

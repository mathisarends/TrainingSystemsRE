from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from training_system.authentication.application.principal import (
    AuthenticatedPrincipal,
)


@dataclass(frozen=True, slots=True)
class VerifiedIdentity:
    subject: str
    email: str
    name: str
    picture_url: str | None


@dataclass(frozen=True, slots=True)
class Session:
    token: str
    expires_at: datetime


class IdentityVerifier(ABC):
    @abstractmethod
    def verify(self, *, credential: str) -> VerifiedIdentity: ...


class SessionStore(ABC):
    @abstractmethod
    async def create(self, *, user_id: UUID) -> Session: ...

    @abstractmethod
    async def get(self, *, token: str) -> AuthenticatedPrincipal | None: ...

    @abstractmethod
    async def delete(self, *, token: str) -> None: ...

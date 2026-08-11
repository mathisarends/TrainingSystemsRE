from datetime import datetime
from uuid import UUID

from training_systems.domain import Entity


class AuthIdentity(Entity):
    def __init__(
        self,
        user_id: UUID,
        provider: str,
        subject: str,
        password_hash: str | None = None,
        id: UUID | None = None,
        created_time: datetime | None = None,
    ) -> None:
        super().__init__(id=id, created_time=created_time)
        self._user_id = user_id
        self._provider = provider
        self._subject = subject
        self._password_hash = password_hash

    @property
    def user_id(self) -> UUID:
        return self._user_id

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def subject(self) -> str:
        return self._subject

    @property
    def password_hash(self) -> str | None:
        return self._password_hash

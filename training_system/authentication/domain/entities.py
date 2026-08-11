from datetime import datetime
from uuid import UUID

from training_system.domain import Entity


class AuthIdentity(Entity):
    def __init__(
        self,
        user_id: UUID,
        provider: str,
        subject: str,
        id: UUID | None = None,
        created_time: datetime | None = None,
    ) -> None:
        super().__init__(id=id, created_time=created_time)
        self._user_id = user_id
        self._provider = provider
        self._subject = subject

    @property
    def user_id(self) -> UUID:
        return self._user_id

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def subject(self) -> str:
        return self._subject

from datetime import datetime
from uuid import UUID

from training_system.domain import Entity


class UnseenCompletion(Entity):
    def __init__(
        self,
        user_id: UUID,
        completed_at: datetime,
        id: UUID | None = None,
        created_time: datetime | None = None,
    ) -> None:
        super().__init__(id=id, created_time=created_time)
        self._user_id = user_id
        self._completed_at = completed_at

    @property
    def user_id(self) -> UUID:
        return self._user_id

    @property
    def completed_at(self) -> datetime:
        return self._completed_at

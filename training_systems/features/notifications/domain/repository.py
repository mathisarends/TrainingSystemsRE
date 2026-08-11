from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from training_systems.features.notifications.domain.entities import UnseenCompletion


class UnseenCompletionRepository(ABC):
    @abstractmethod
    async def list_for_user(self, *, user_id: UUID) -> list[UnseenCompletion]: ...

    @abstractmethod
    async def create(
        self, *, user_id: UUID, completed_at: datetime
    ) -> UnseenCompletion: ...

    @abstractmethod
    async def clear_for_user(self, *, user_id: UUID) -> int: ...

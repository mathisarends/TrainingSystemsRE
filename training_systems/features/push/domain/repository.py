from abc import ABC, abstractmethod
from uuid import UUID

from training_systems.features.push.domain.entities import PushSubscription


class PushSubscriptionRepository(ABC):
    @abstractmethod
    async def find_by_user(self, *, user_id: UUID) -> PushSubscription | None: ...

    @abstractmethod
    async def save(self, *, subscription: PushSubscription) -> PushSubscription: ...

    @abstractmethod
    async def delete(self, *, user_id: UUID) -> None: ...

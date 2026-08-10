from abc import ABC, abstractmethod
from uuid import UUID

from training_system.features.push.application.message import PushMessage


class PushSender(ABC):
    """Best-effort delivery: implementations must not raise on send failure."""

    @abstractmethod
    async def send(self, *, user_id: UUID, message: PushMessage) -> None: ...

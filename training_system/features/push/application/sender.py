from abc import ABC, abstractmethod
from uuid import UUID

from training_system.features.push.application.message import PushMessage


class PushSender(ABC):
    """Best-effort delivery: implementations must not raise on send failure.

    Returns whether the message was actually delivered, so callers whose
    behavior depends on delivery (e.g. stopping a keep-alive) can react
    without the port itself raising.
    """

    @abstractmethod
    async def send(self, *, user_id: UUID, message: PushMessage) -> bool: ...

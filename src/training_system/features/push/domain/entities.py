from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class PushSubscription:
    user_id: UUID
    endpoint: str
    p256dh: str
    auth: str

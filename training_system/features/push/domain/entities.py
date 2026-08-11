from uuid import UUID


class PushSubscription:
    def __init__(
        self,
        *,
        user_id: UUID,
        endpoint: str,
        p256dh: str,
        auth: str,
    ) -> None:
        self.user_id = user_id
        self.endpoint = endpoint
        self.p256dh = p256dh
        self.auth = auth

from uuid import UUID

from training_system.features.push.domain import (
    PushSubscription,
    PushSubscriptionRepository,
)


class PushSubscriptionService:
    def __init__(self, repository: PushSubscriptionRepository) -> None:
        self._repository = repository

    async def register(
        self, *, user_id: UUID, endpoint: str, p256dh: str, auth: str
    ) -> PushSubscription:
        subscription = PushSubscription(
            user_id=user_id, endpoint=endpoint, p256dh=p256dh, auth=auth
        )
        return await self._repository.save(subscription=subscription)

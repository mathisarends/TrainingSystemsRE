from uuid import UUID

import pytest

from training_systems.features.push.application.service import (
    PushSubscriptionService,
)
from training_systems.features.push.domain import (
    PushSubscription,
    PushSubscriptionRepository,
)


class FakePushSubscriptionRepository(PushSubscriptionRepository):
    def __init__(self) -> None:
        self.subscriptions: dict[UUID, PushSubscription] = {}

    async def find_by_user(self, *, user_id: UUID) -> PushSubscription | None:
        return self.subscriptions.get(user_id)

    async def save(self, *, subscription: PushSubscription) -> PushSubscription:
        self.subscriptions[subscription.user_id] = subscription
        return subscription

    async def delete(self, *, user_id: UUID) -> None:
        self.subscriptions.pop(user_id, None)


@pytest.fixture
def subscription_repository() -> FakePushSubscriptionRepository:
    return FakePushSubscriptionRepository()


@pytest.fixture
def subscription_service(
    subscription_repository: FakePushSubscriptionRepository,
) -> PushSubscriptionService:
    return PushSubscriptionService(subscription_repository)

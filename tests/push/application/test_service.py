from uuid import uuid4

from training_systems.features.push.application.service import (
    PushSubscriptionService,
)

from .conftest import FakePushSubscriptionRepository


async def test_register_persists_and_returns_the_subscription(
    subscription_service: PushSubscriptionService,
) -> None:
    user_id = uuid4()

    subscription = await subscription_service.register(
        user_id=user_id,
        endpoint="https://push.example/abc",
        p256dh="key",
        auth="secret",
    )

    assert subscription.user_id == user_id
    assert subscription.endpoint == "https://push.example/abc"


async def test_register_replaces_any_previous_subscription_for_the_user(
    subscription_service: PushSubscriptionService,
    subscription_repository: FakePushSubscriptionRepository,
) -> None:
    user_id = uuid4()
    await subscription_service.register(
        user_id=user_id, endpoint="https://push.example/old", p256dh="k1", auth="a1"
    )

    await subscription_service.register(
        user_id=user_id, endpoint="https://push.example/new", p256dh="k2", auth="a2"
    )

    stored = await subscription_repository.find_by_user(user_id=user_id)
    assert stored is not None
    assert stored.endpoint == "https://push.example/new"

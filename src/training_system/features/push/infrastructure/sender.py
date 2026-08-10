import asyncio
import json
import logging
from dataclasses import asdict
from uuid import UUID

from pywebpush import WebPushException, webpush
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from training_system.features.push.application.message import PushMessage
from training_system.features.push.application.sender import PushSender
from training_system.features.push.infrastructure.repository import (
    SqlPushSubscriptionRepository,
)
from training_system.features.push.infrastructure.settings import PushSettings

logger = logging.getLogger(__name__)

_GONE = 410


class WebPushSender(PushSender):
    """Scope.APP adapter: opens its own short transaction per send so it can be
    called both from a request and from a scheduler job (see database.md on
    injecting a session factory for work outside the request scope)."""

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        settings: PushSettings,
    ) -> None:
        self._session_factory = session_factory
        self._settings = settings

    async def send(self, *, user_id: UUID, message: PushMessage) -> None:
        async with self._session_factory() as session:
            repository = SqlPushSubscriptionRepository(session)
            subscription = await repository.find_by_user(user_id=user_id)
            if subscription is None:
                return

            payload = {key: value for key, value in asdict(message).items() if value}
            try:
                await asyncio.to_thread(
                    webpush,
                    subscription_info={
                        "endpoint": subscription.endpoint,
                        "keys": {
                            "p256dh": subscription.p256dh,
                            "auth": subscription.auth,
                        },
                    },
                    data=_encode(payload),
                    vapid_private_key=self._settings.vapid_private_key.get_secret_value(),
                    vapid_claims={"sub": self._settings.vapid_subject},
                )
            except WebPushException as error:
                if error.response is not None and error.response.status_code == _GONE:
                    await repository.delete(user_id=user_id)
                    await session.commit()
                else:
                    logger.warning("Push delivery failed for user %s", user_id)
            except Exception:  # noqa: BLE001
                logger.exception("Unexpected push delivery error for user %s", user_id)


def _encode(payload: dict[str, object]) -> str:
    return json.dumps(payload)

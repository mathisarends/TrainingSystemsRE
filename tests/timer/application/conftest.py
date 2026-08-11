from uuid import UUID

import pytest
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from training_systems.features.push.application import PushMessage, PushSender
from training_systems.features.timer.application.service import TimerService


class FakePushSender(PushSender):
    def __init__(self, *, delivered: bool = True) -> None:
        self.delivered = delivered
        self.sent: list[tuple[UUID, PushMessage]] = []

    async def send(self, *, user_id: UUID, message: PushMessage) -> bool:
        self.sent.append((user_id, message))
        return self.delivered


@pytest.fixture
def scheduler() -> AsyncIOScheduler:
    return AsyncIOScheduler()


@pytest.fixture
def push_sender() -> FakePushSender:
    return FakePushSender()


@pytest.fixture
def timer_service(
    scheduler: AsyncIOScheduler, push_sender: FakePushSender
) -> TimerService:
    return TimerService(scheduler, push_sender)

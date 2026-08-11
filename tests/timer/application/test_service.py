from uuid import uuid4

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from training_systems.features.timer.application.service import (
    TimerService,
    _job_id,
)

from .conftest import FakePushSender


async def test_start_schedules_a_keep_alive_job_for_the_user(
    timer_service: TimerService, scheduler: AsyncIOScheduler
) -> None:
    user_id = uuid4()

    await timer_service.start(user_id=user_id)

    assert scheduler.get_job(_job_id(user_id)) is not None


async def test_start_is_idempotent(
    timer_service: TimerService, scheduler: AsyncIOScheduler
) -> None:
    user_id = uuid4()

    await timer_service.start(user_id=user_id)
    await timer_service.start(user_id=user_id)

    assert scheduler.get_job(_job_id(user_id)) is not None


async def test_stop_removes_an_existing_job(
    timer_service: TimerService, scheduler: AsyncIOScheduler
) -> None:
    user_id = uuid4()
    await timer_service.start(user_id=user_id)

    await timer_service.stop(user_id=user_id)

    assert scheduler.get_job(_job_id(user_id)) is None


async def test_stop_without_a_running_job_is_a_no_op(
    timer_service: TimerService,
) -> None:
    await timer_service.stop(user_id=uuid4())


async def test_keep_alive_stops_the_timer_when_delivery_fails(
    scheduler: AsyncIOScheduler,
) -> None:
    push_sender = FakePushSender(delivered=False)
    timer_service = TimerService(scheduler, push_sender)
    user_id = uuid4()
    await timer_service.start(user_id=user_id)

    await timer_service._send_keep_alive(user_id)

    assert scheduler.get_job(_job_id(user_id)) is None


async def test_keep_alive_leaves_the_timer_running_when_delivery_succeeds(
    scheduler: AsyncIOScheduler,
) -> None:
    push_sender = FakePushSender(delivered=True)
    timer_service = TimerService(scheduler, push_sender)
    user_id = uuid4()
    await timer_service.start(user_id=user_id)

    await timer_service._send_keep_alive(user_id)

    assert scheduler.get_job(_job_id(user_id)) is not None

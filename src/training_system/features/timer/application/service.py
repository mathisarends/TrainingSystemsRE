from uuid import UUID

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from training_system.features.push.application import PushMessage, PushSender

KEEP_ALIVE_INTERVAL_SECONDS = 20


class TimerService:
    """Per-user server-side rest-timer keep-alive, backed by the shared scheduler.

    Ephemeral by design (see SPEC's wording that at most one tracker is held in
    the running server process); there is no database-backed timer state.
    """

    def __init__(self, scheduler: AsyncIOScheduler, push_sender: PushSender) -> None:
        self._scheduler = scheduler
        self._push_sender = push_sender

    async def start(self, *, user_id: UUID) -> None:
        self._scheduler.add_job(
            self._send_keep_alive,
            trigger="interval",
            seconds=KEEP_ALIVE_INTERVAL_SECONDS,
            id=_job_id(user_id),
            replace_existing=True,
            args=[user_id],
        )

    async def stop(self, *, user_id: UUID) -> None:
        job = self._scheduler.get_job(_job_id(user_id))
        if job is not None:
            job.remove()

    async def _send_keep_alive(self, user_id: UUID) -> None:
        message = PushMessage(
            title="Keep Alive", body="Keeping timer alive", silent=True
        )
        delivered = await self._push_sender.send(user_id=user_id, message=message)
        if not delivered:
            await self.stop(user_id=user_id)


def _job_id(user_id: UUID) -> str:
    return f"rest-timer:{user_id}"

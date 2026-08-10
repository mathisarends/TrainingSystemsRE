from datetime import UTC, datetime, timedelta
from uuid import UUID

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from training_system.features.notifications.infrastructure.repository import (
    SqlUnseenCompletionRepository,
)
from training_system.features.plans.application.ports import SessionTracker
from training_system.features.plans.domain.entities import (
    DEFAULT_INACTIVITY_MINUTES,
    MINIMUM_RECORDED_MINUTES,
)
from training_system.features.plans.infrastructure.repository import SqlPlanRepository
from training_system.features.push.application import PushMessage, PushSender


class ApSchedulerSessionTracker(SessionTracker):
    """Scope.APP: one scheduled close-out job per plan day, keyed by position."""

    def __init__(
        self,
        scheduler: AsyncIOScheduler,
        session_factory: async_sessionmaker[AsyncSession],
        push_sender: PushSender,
    ) -> None:
        self._scheduler = scheduler
        self._session_factory = session_factory
        self._push_sender = push_sender

    def _job_id(self, *, plan_id: UUID, week_index: int, day_index: int) -> str:
        return f"training-session:{plan_id}:{week_index}:{day_index}"

    async def touch(
        self, *, user_id: UUID, plan_id: UUID, week_index: int, day_index: int
    ) -> None:
        job_id = self._job_id(plan_id=plan_id, week_index=week_index, day_index=day_index)
        if self._scheduler.get_job(job_id) is None:
            await self._start_recording(
                user_id=user_id, plan_id=plan_id, week_index=week_index, day_index=day_index
            )
        self._scheduler.add_job(
            self._close_recording,
            trigger="date",
            run_date=datetime.now(UTC) + timedelta(minutes=DEFAULT_INACTIVITY_MINUTES),
            id=job_id,
            replace_existing=True,
            args=[user_id, plan_id, week_index, day_index],
        )

    async def _start_recording(
        self, *, user_id: UUID, plan_id: UUID, week_index: int, day_index: int
    ) -> None:
        async with self._session_factory() as session:
            repository = SqlPlanRepository(session)
            plan = await repository.find_by_id(plan_id=plan_id, user_id=user_id)
            if plan is None:
                return
            day = plan.day_at(week_index=week_index, day_index=day_index)
            if day.is_recording:
                return
            plan.start_recording(
                week_index=week_index, day_index=day_index, at=datetime.now(UTC)
            )
            await repository.save(plan=plan)
            await session.commit()

    async def _close_recording(
        self, user_id: UUID, plan_id: UUID, week_index: int, day_index: int
    ) -> None:
        completed = False
        async with self._session_factory() as session:
            repository = SqlPlanRepository(session)
            plan = await repository.find_by_id(plan_id=plan_id, user_id=user_id)
            if plan is None:
                return
            duration_minutes = plan.close_recording(
                week_index=week_index, day_index=day_index, at=datetime.now(UTC)
            )
            await repository.save(plan=plan)

            completed = duration_minutes >= MINIMUM_RECORDED_MINUTES
            if completed:
                unseen_repository = SqlUnseenCompletionRepository(session)
                await unseen_repository.create(
                    user_id=user_id, completed_at=datetime.now(UTC)
                )
            await session.commit()

        if completed:
            await self._push_sender.send(
                user_id=user_id,
                message=PushMessage(
                    title="Trainingszusammenfassung verfügbar",
                    body="Dein Training wurde aufgezeichnet.",
                    url="/logs",
                ),
            )

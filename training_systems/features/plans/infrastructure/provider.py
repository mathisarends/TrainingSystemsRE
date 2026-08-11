from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from training_systems.features.plans.application import PlanService, SessionTracker
from training_systems.features.plans.domain import PlanRepository
from training_systems.features.plans.infrastructure.repository import SqlPlanRepository
from training_systems.features.plans.infrastructure.session_tracker import (
    ApSchedulerSessionTracker,
)
from training_systems.features.push.application import PushSender


class PlanProvider(Provider):
    @provide(scope=Scope.APP)
    def session_tracker(
        self,
        scheduler: AsyncIOScheduler,
        session_factory: async_sessionmaker[AsyncSession],
        push_sender: PushSender,
    ) -> SessionTracker:
        return ApSchedulerSessionTracker(scheduler, session_factory, push_sender)

    @provide(scope=Scope.REQUEST)
    def plan_repository(self, session: AsyncSession) -> PlanRepository:
        return SqlPlanRepository(session)

    @provide(scope=Scope.REQUEST)
    def plan_service(
        self, repository: PlanRepository, session_tracker: SessionTracker
    ) -> PlanService:
        return PlanService(repository, session_tracker)

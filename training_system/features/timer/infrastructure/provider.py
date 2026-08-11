from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka import Provider, Scope, provide

from training_system.features.push.application import PushSender
from training_system.features.timer.application import TimerService


class TimerProvider(Provider):
    @provide(scope=Scope.APP)
    def timer_service(
        self, scheduler: AsyncIOScheduler, push_sender: PushSender
    ) -> TimerService:
        return TimerService(scheduler, push_sender)

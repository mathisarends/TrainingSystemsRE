from collections.abc import AsyncIterator

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka import Provider, Scope, provide


class SchedulerProvider(Provider):
    @provide(scope=Scope.APP)
    async def scheduler(self) -> AsyncIterator[AsyncIOScheduler]:
        scheduler = AsyncIOScheduler()
        scheduler.start()
        try:
            yield scheduler
        finally:
            scheduler.shutdown(wait=False)

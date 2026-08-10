from abc import ABC, abstractmethod
from uuid import UUID


class SessionTracker(ABC):
    """Auto-detects a live training session from entry-activity signals.

    First activity for a not-yet-recording day starts the clock; further
    signals extend it; 35 minutes without another signal closes the day.
    """

    @abstractmethod
    async def touch(
        self, *, user_id: UUID, plan_id: UUID, week_index: int, day_index: int
    ) -> None: ...

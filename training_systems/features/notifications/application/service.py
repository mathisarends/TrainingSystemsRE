from datetime import datetime
from uuid import UUID

from training_systems.features.notifications.domain import (
    UnseenCompletion,
    UnseenCompletionRepository,
)


class UnseenCompletionService:
    def __init__(self, repository: UnseenCompletionRepository) -> None:
        self._repository = repository

    async def list_unseen(self, *, user_id: UUID) -> list[UnseenCompletion]:
        return await self._repository.list_for_user(user_id=user_id)

    async def mark_completed(
        self, *, user_id: UUID, completed_at: datetime
    ) -> UnseenCompletion:
        return await self._repository.create(
            user_id=user_id, completed_at=completed_at
        )

    async def clear_seen(self, *, user_id: UUID) -> int:
        return await self._repository.clear_for_user(user_id=user_id)

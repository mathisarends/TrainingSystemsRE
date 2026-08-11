from datetime import datetime
from uuid import UUID

import pytest

from training_system.features.notifications.application.service import (
    UnseenCompletionService,
)
from training_system.features.notifications.domain import (
    UnseenCompletion,
    UnseenCompletionRepository,
)


class FakeUnseenCompletionRepository(UnseenCompletionRepository):
    def __init__(self) -> None:
        self.completions: list[UnseenCompletion] = []

    async def list_for_user(self, *, user_id: UUID) -> list[UnseenCompletion]:
        return [
            completion
            for completion in self.completions
            if completion.user_id == user_id
        ]

    async def create(
        self, *, user_id: UUID, completed_at: datetime
    ) -> UnseenCompletion:
        completion = UnseenCompletion(user_id=user_id, completed_at=completed_at)
        self.completions.append(completion)
        return completion

    async def clear_for_user(self, *, user_id: UUID) -> int:
        remaining = [
            completion
            for completion in self.completions
            if completion.user_id != user_id
        ]
        cleared = len(self.completions) - len(remaining)
        self.completions = remaining
        return cleared


@pytest.fixture
def completion_repository() -> FakeUnseenCompletionRepository:
    return FakeUnseenCompletionRepository()


@pytest.fixture
def completion_service(
    completion_repository: FakeUnseenCompletionRepository,
) -> UnseenCompletionService:
    return UnseenCompletionService(completion_repository)

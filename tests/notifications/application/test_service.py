from datetime import UTC, datetime
from uuid import uuid4

from training_system.features.notifications.application.service import (
    UnseenCompletionService,
)


async def test_mark_completed_makes_the_completion_listable(
    completion_service: UnseenCompletionService,
) -> None:
    user_id = uuid4()

    await completion_service.mark_completed(
        user_id=user_id, completed_at=datetime(2026, 1, 1, tzinfo=UTC)
    )

    unseen = await completion_service.list_unseen(user_id=user_id)
    assert len(unseen) == 1


async def test_list_unseen_only_returns_the_given_users_completions(
    completion_service: UnseenCompletionService,
) -> None:
    user_id = uuid4()
    other_user_id = uuid4()
    now = datetime(2026, 1, 1, tzinfo=UTC)
    await completion_service.mark_completed(user_id=user_id, completed_at=now)
    await completion_service.mark_completed(user_id=other_user_id, completed_at=now)

    unseen = await completion_service.list_unseen(user_id=user_id)

    assert [completion.user_id for completion in unseen] == [user_id]


async def test_clear_seen_removes_only_the_given_users_completions(
    completion_service: UnseenCompletionService,
) -> None:
    user_id = uuid4()
    other_user_id = uuid4()
    now = datetime(2026, 1, 1, tzinfo=UTC)
    await completion_service.mark_completed(user_id=user_id, completed_at=now)
    await completion_service.mark_completed(user_id=other_user_id, completed_at=now)

    cleared = await completion_service.clear_seen(user_id=user_id)

    assert cleared == 1
    assert await completion_service.list_unseen(user_id=user_id) == []
    assert len(await completion_service.list_unseen(user_id=other_user_id)) == 1

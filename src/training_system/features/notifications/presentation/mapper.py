from training_system.features.notifications.domain import UnseenCompletion
from training_system.features.notifications.presentation.schemas import (
    UnseenCompletionListResponse,
    UnseenCompletionResponse,
)


def to_list_response(
    completions: list[UnseenCompletion],
) -> UnseenCompletionListResponse:
    return UnseenCompletionListResponse(
        items=[
            UnseenCompletionResponse(id=item.id, completed_at=item.completed_at)
            for item in completions
        ]
    )

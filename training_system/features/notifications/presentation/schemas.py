from datetime import datetime
from uuid import UUID

from training_system.presentation.schema import Schema


class UnseenCompletionResponse(Schema):
    id: UUID
    completed_at: datetime


class UnseenCompletionListResponse(Schema):
    items: list[UnseenCompletionResponse]


class ClearNotificationsResponse(Schema):
    cleared_count: int

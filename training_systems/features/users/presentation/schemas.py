from datetime import datetime
from uuid import UUID

from pydantic import Field

from training_systems.presentation.schema import Schema


class UserResponse(Schema):
    id: UUID
    name: str
    email: str
    picture_url: str | None
    created_at: datetime


class UpdateUserRequest(Schema):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    picture_url: str | None = None

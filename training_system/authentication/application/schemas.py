from datetime import datetime
from enum import StrEnum
from typing import Self
from uuid import UUID

from pydantic import AliasChoices, BaseModel, Field, field_validator


class AuthSession(BaseModel):
    access_token: str
    refresh_token: str


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


class TokenPayload(BaseModel):
    user_id: UUID
    expires_at: datetime


class GoogleAuthorizationRequest(BaseModel):
    authorization_url: str
    state: str


class GoogleIdentity(BaseModel):
    subject: str = Field(validation_alias=AliasChoices("subject", "sub"))
    email: str
    name: str | None = None
    picture_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("picture_url", "picture"),
    )
    email_verified: bool = False

    @field_validator("subject")
    @classmethod
    def normalize_subject(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("subject must not be empty")
        return normalized

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not normalized:
            raise ValueError("email must not be empty")
        return normalized

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


class GoogleCallbackResult(BaseModel):
    succeeded: bool
    session: AuthSession | None = None
    error_reason: str | None = None

    @classmethod
    def success(cls, *, session: AuthSession) -> Self:
        return cls(succeeded=True, session=session)

    @classmethod
    def error(cls, *, reason: str) -> Self:
        return cls(succeeded=False, error_reason=reason)

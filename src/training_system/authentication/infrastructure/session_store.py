import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from training_system.authentication.application.ports import Session, SessionStore
from training_system.authentication.application.principal import (
    AuthenticatedPrincipal,
)
from training_system.authentication.infrastructure.settings import (
    AuthenticationSettings,
)
from training_system.infrastructure.database.orm import SessionModel


class SqlSessionStore(SessionStore):
    def __init__(
        self, session: AsyncSession, settings: AuthenticationSettings
    ) -> None:
        self._session = session
        self._settings = settings

    async def create(self, *, user_id: UUID) -> Session:
        token = secrets.token_urlsafe(48)
        expires_at = datetime.now(UTC) + timedelta(
            days=self._settings.session_ttl_days
        )
        self._session.add(
            SessionModel(token=token, user_id=user_id, expires_at=expires_at)
        )
        await self._session.flush()
        return Session(token=token, expires_at=expires_at)

    async def get(self, *, token: str) -> AuthenticatedPrincipal | None:
        model = await self._find(token)
        if model is None or model.expires_at < datetime.now(UTC):
            return None
        return AuthenticatedPrincipal(user_id=model.user_id)

    async def delete(self, *, token: str) -> None:
        model = await self._find(token)
        if model is not None:
            await self._session.delete(model)
            await self._session.flush()

    async def _find(self, token: str) -> SessionModel | None:
        statement = select(SessionModel).where(col(SessionModel.token) == token)
        model = await self._session.scalar(statement)
        return model

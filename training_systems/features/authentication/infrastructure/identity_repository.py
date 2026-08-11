from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from training_systems.features.authentication.domain.entities import AuthIdentity
from training_systems.features.authentication.domain.repository import (
    AuthIdentityRepository,
)
from training_systems.infrastructure.database.orm import AuthIdentityModel


class SqlAuthIdentityRepository(AuthIdentityRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _to_domain(self, model: AuthIdentityModel) -> AuthIdentity:
        return AuthIdentity(
            id=model.id,
            created_time=model.created_at,
            user_id=model.user_id,
            provider=model.provider,
            subject=model.subject,
            password_hash=model.password_hash,
        )

    async def find_by_provider_subject(
        self, *, provider: str, subject: str
    ) -> AuthIdentity | None:
        statement = select(AuthIdentityModel).where(
            AuthIdentityModel.provider == provider,
            AuthIdentityModel.subject == subject,
        )
        model = await self._session.scalar(statement)
        return self._to_domain(model) if model is not None else None

    async def save(self, *, identity: AuthIdentity) -> AuthIdentity:
        model = await self._session.merge(
            AuthIdentityModel(
                id=identity.id,
                created_at=identity.created_at,
                user_id=identity.user_id,
                provider=identity.provider,
                subject=identity.subject,
                password_hash=identity.password_hash,
            )
        )
        await self._session.flush()
        return self._to_domain(model)

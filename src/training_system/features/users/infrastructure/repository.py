from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from training_system.features.users.domain.entities import User
from training_system.features.users.domain.repository import UserRepository
from training_system.infrastructure.database import SqlRepository
from training_system.infrastructure.database.orm import UserModel


class SqlUserRepository(SqlRepository[UserModel, User], UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UserModel)

    def to_domain(self, model: UserModel) -> User:
        return User(
            id=model.id,
            created_time=model.created_at,
            name=model.name,
            email=model.email,
            picture_url=model.picture_url,
        )

    def to_model(self, entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            created_at=entity.created_at,
            name=entity.name,
            email=entity.email,
            picture_url=entity.picture_url,
        )

    async def find_by_id(self, *, user_id: UUID) -> User | None:
        model = await self._session.get(self._model, user_id)
        return self.to_domain(model) if model is not None else None

    async def find_by_email(self, *, email: str) -> User | None:
        statement = select(UserModel).where(UserModel.email == email)
        model = await self._session.scalar(statement)
        return self.to_domain(model) if model is not None else None

    async def save(self, *, user: User) -> User:
        return await self.save_entity(user)

    async def delete(self, *, user_id: UUID) -> None:
        await self.delete_entity(user_id)

from uuid import UUID

from training_system.features.users.domain import User, UserRepository


class UserNotFound(Exception):
    pass


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    async def get_profile(self, *, user_id: UUID) -> User:
        user = await self._repository.find_by_id(user_id=user_id)
        if user is None:
            raise UserNotFound(user_id)
        return user

    async def update_profile(
        self,
        *,
        user_id: UUID,
        name: str | None = None,
        picture_url: str | None = None,
    ) -> User:
        user = await self.get_profile(user_id=user_id)
        return await self._repository.save(
            user=user.update_profile(name=name, picture_url=picture_url)
        )

    async def delete_account(self, *, user_id: UUID) -> None:
        await self._repository.delete(user_id=user_id)

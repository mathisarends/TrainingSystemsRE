from uuid import UUID

from training_systems.features.authentication.application.exceptions import (
    SessionInvalidException,
)
from training_systems.features.authentication.application.ports import TokenIssuer
from training_systems.features.authentication.application.schemas import AuthSession
from training_systems.features.users.domain import UserRepository


class SessionRefresher:
    def __init__(
        self, user_repository: UserRepository, token_issuer: TokenIssuer
    ) -> None:
        self._user_repository = user_repository
        self._token_issuer = token_issuer

    async def refresh(self, *, user_id: UUID) -> AuthSession:
        user = await self._user_repository.find_by_id(user_id=user_id)
        if user is None:
            raise SessionInvalidException("Invalid user")
        return self._token_issuer.create_session(user_id=user.id)

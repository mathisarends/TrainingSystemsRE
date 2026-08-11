from dataclasses import dataclass

from training_systems.features.authentication.application.exceptions import (
    EmailAlreadyRegisteredException,
    InvalidCredentialsException,
)
from training_systems.features.authentication.application.ports import (
    PasswordHasher,
    TokenIssuer,
)
from training_systems.features.authentication.application.schemas import AuthSession
from training_systems.features.authentication.domain import (
    AuthIdentity,
    AuthIdentityRepository,
)
from training_systems.features.exercises.application import ExerciseCatalogService
from training_systems.features.users.domain import User, UserRepository

PASSWORD_PROVIDER = "password"


@dataclass(frozen=True, slots=True)
class AuthResult:
    user: User
    session: AuthSession


class PasswordAuthFlow:
    def __init__(
        self,
        user_repository: UserRepository,
        identity_repository: AuthIdentityRepository,
        password_hasher: PasswordHasher,
        token_issuer: TokenIssuer,
        catalog_service: ExerciseCatalogService,
    ) -> None:
        self._user_repository = user_repository
        self._identity_repository = identity_repository
        self._password_hasher = password_hasher
        self._token_issuer = token_issuer
        self._catalog_service = catalog_service

    async def register(self, *, email: str, password: str, name: str) -> AuthResult:
        normalized_email = email.strip().lower()

        if await self._user_repository.find_by_email(email=normalized_email):
            raise EmailAlreadyRegisteredException(
                "Email already belongs to another auth identity"
            )

        user = await self._user_repository.save(
            user=User(name=name.strip(), email=normalized_email)
        )
        await self._identity_repository.save(
            identity=AuthIdentity(
                user_id=user.id,
                provider=PASSWORD_PROVIDER,
                subject=normalized_email,
                password_hash=self._password_hasher.hash(password=password),
            )
        )
        await self._catalog_service.seed_defaults(user_id=user.id)

        session = self._token_issuer.create_session(user_id=user.id)
        return AuthResult(user=user, session=session)

    async def login(self, *, email: str, password: str) -> AuthResult:
        normalized_email = email.strip().lower()

        identity = await self._identity_repository.find_by_provider_subject(
            provider=PASSWORD_PROVIDER, subject=normalized_email
        )
        if identity is None or identity.password_hash is None:
            raise InvalidCredentialsException("Invalid email or password")

        if not self._password_hasher.verify(
            password=password, password_hash=identity.password_hash
        ):
            raise InvalidCredentialsException("Invalid email or password")

        user = await self._user_repository.find_by_id(user_id=identity.user_id)
        if user is None:
            raise InvalidCredentialsException("Auth identity has no owning user")

        session = self._token_issuer.create_session(user_id=user.id)
        return AuthResult(user=user, session=session)

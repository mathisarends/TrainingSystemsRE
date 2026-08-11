from uuid import UUID

import pytest

from training_system.features.authentication.application.ports import (
    GoogleOAuthProvider,
    PasswordHasher,
    TokenIssuer,
)
from training_system.features.authentication.application.schemas import (
    AuthSession,
    GoogleIdentity,
    TokenPayload,
    TokenType,
)
from training_system.features.authentication.domain import (
    AuthIdentity,
    AuthIdentityRepository,
)
from training_system.features.exercises.application import ExerciseCatalogService
from training_system.features.exercises.domain import (
    ExerciseCatalog,
    ExerciseCatalogRepository,
)
from training_system.features.users.domain import User, UserRepository


class FakeUserRepository(UserRepository):
    def __init__(self) -> None:
        self.users: dict[UUID, User] = {}

    async def find_by_id(self, *, user_id: UUID) -> User | None:
        return self.users.get(user_id)

    async def find_by_email(self, *, email: str) -> User | None:
        return next(
            (user for user in self.users.values() if user.email == email), None
        )

    async def save(self, *, user: User) -> User:
        self.users[user.id] = user
        return user

    async def delete(self, *, user_id: UUID) -> None:
        self.users.pop(user_id, None)


class FakeAuthIdentityRepository(AuthIdentityRepository):
    def __init__(self) -> None:
        self.identities: dict[tuple[str, str], AuthIdentity] = {}

    async def find_by_provider_subject(
        self, *, provider: str, subject: str
    ) -> AuthIdentity | None:
        return self.identities.get((provider, subject))

    async def save(self, *, identity: AuthIdentity) -> AuthIdentity:
        self.identities[(identity.provider, identity.subject)] = identity
        return identity


class FakePasswordHasher(PasswordHasher):
    """Deterministic stand-in: hashes are just a prefixed copy of the password."""

    def hash(self, *, password: str) -> str:
        return f"hashed:{password}"

    def verify(self, *, password: str, password_hash: str) -> bool:
        return password_hash == f"hashed:{password}"


class FakeTokenIssuer(TokenIssuer):
    def __init__(self) -> None:
        self.issued_for: list[UUID] = []

    def create_session(self, *, user_id: UUID) -> AuthSession:
        self.issued_for.append(user_id)
        return AuthSession(
            access_token=f"access:{user_id}", refresh_token=f"refresh:{user_id}"
        )

    def validate(
        self, *, token: str, expected_type: TokenType = TokenType.ACCESS
    ) -> TokenPayload:
        raise NotImplementedError


class FakeGoogleOAuthProvider(GoogleOAuthProvider):
    def __init__(self, *, identity: GoogleIdentity | None = None) -> None:
        self._identity = identity

    def build_authorization_url(self, *, state: str) -> str:
        return f"https://accounts.google.com/authorize?state={state}"

    async def exchange_code_for_identity(
        self, *, authorization_code: str
    ) -> GoogleIdentity:
        if self._identity is None:
            raise ValueError("no identity configured for this authorization code")
        return self._identity


class FakeExerciseCatalogRepository(ExerciseCatalogRepository):
    def __init__(self) -> None:
        self.catalogs: dict[UUID, ExerciseCatalog] = {}

    async def find_by_user(self, *, user_id: UUID) -> ExerciseCatalog | None:
        return self.catalogs.get(user_id)

    async def replace(self, *, catalog: ExerciseCatalog) -> ExerciseCatalog:
        self.catalogs[catalog.user_id] = catalog
        return catalog


@pytest.fixture
def user_repository() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def identity_repository() -> FakeAuthIdentityRepository:
    return FakeAuthIdentityRepository()


@pytest.fixture
def password_hasher() -> FakePasswordHasher:
    return FakePasswordHasher()


@pytest.fixture
def token_issuer() -> FakeTokenIssuer:
    return FakeTokenIssuer()


@pytest.fixture
def catalog_service() -> ExerciseCatalogService:
    return ExerciseCatalogService(FakeExerciseCatalogRepository())

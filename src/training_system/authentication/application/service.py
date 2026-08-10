from dataclasses import dataclass

from training_system.authentication.application.errors import AuthenticationFailed
from training_system.authentication.application.ports import (
    IdentityVerifier,
    Session,
    SessionStore,
    VerifiedIdentity,
)
from training_system.authentication.domain import AuthIdentity, AuthIdentityRepository
from training_system.features.exercises.application import ExerciseCatalogService
from training_system.features.users.domain import User, UserRepository

GOOGLE_PROVIDER = "google"


@dataclass(frozen=True, slots=True)
class LoginResult:
    user: User
    session: Session


class AuthService:
    def __init__(
        self,
        identity_verifier: IdentityVerifier,
        identity_repository: AuthIdentityRepository,
        user_repository: UserRepository,
        catalog_service: ExerciseCatalogService,
        session_store: SessionStore,
    ) -> None:
        self._identity_verifier = identity_verifier
        self._identity_repository = identity_repository
        self._user_repository = user_repository
        self._catalog_service = catalog_service
        self._session_store = session_store

    async def login_with_google(self, *, credential: str) -> LoginResult:
        try:
            verified = self._identity_verifier.verify(credential=credential)
        except Exception as error:
            raise AuthenticationFailed from error

        identity = await self._identity_repository.find_by_provider_subject(
            provider=GOOGLE_PROVIDER, subject=verified.subject
        )
        if identity is not None:
            user = await self._user_repository.find_by_id(user_id=identity.user_id)
            if user is None:
                raise AuthenticationFailed
        else:
            user = await self._register_new_user(verified)

        session = await self._session_store.create(user_id=user.id)
        return LoginResult(user=user, session=session)

    async def _register_new_user(self, verified: VerifiedIdentity) -> User:
        picture_url = verified.picture_url or self._default_picture_url(verified.name)
        user = await self._user_repository.save(
            user=User(name=verified.name, email=verified.email, picture_url=picture_url)
        )
        identity = AuthIdentity(
            user_id=user.id, provider=GOOGLE_PROVIDER, subject=verified.subject
        )
        await self._identity_repository.save(identity=identity)
        await self._catalog_service.seed_defaults(user_id=user.id)
        return user

    @staticmethod
    def _default_picture_url(name: str) -> str:
        initial = name.strip()[:1].upper() or "U"
        return f"/images/profile/{initial}.webp"

    async def logout(self, *, token: str) -> None:
        await self._session_store.delete(token=token)

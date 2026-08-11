from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from training_system.authentication.application import (
    AuthService,
    IdentityVerifier,
    SessionStore,
)
from training_system.authentication.domain import AuthIdentityRepository
from training_system.authentication.infrastructure.google_verifier import (
    GoogleIdentityVerifier,
)
from training_system.authentication.infrastructure.identity_repository import (
    SqlAuthIdentityRepository,
)
from training_system.authentication.infrastructure.session_store import (
    SqlSessionStore,
)
from training_system.authentication.infrastructure.settings import (
    AuthenticationSettings,
)
from training_system.features.exercises.application import ExerciseCatalogService
from training_system.features.users.domain import UserRepository


class AuthenticationProvider(Provider):
    @provide(scope=Scope.APP)
    def settings(self) -> AuthenticationSettings:
        return AuthenticationSettings()

    @provide(scope=Scope.APP)
    def identity_verifier(self, settings: AuthenticationSettings) -> IdentityVerifier:
        return GoogleIdentityVerifier(settings)

    @provide(scope=Scope.REQUEST)
    def identity_repository(self, session: AsyncSession) -> AuthIdentityRepository:
        return SqlAuthIdentityRepository(session)

    @provide(scope=Scope.REQUEST)
    def session_store(
        self, session: AsyncSession, settings: AuthenticationSettings
    ) -> SessionStore:
        return SqlSessionStore(session, settings)

    @provide(scope=Scope.REQUEST)
    def auth_service(
        self,
        identity_verifier: IdentityVerifier,
        identity_repository: AuthIdentityRepository,
        user_repository: UserRepository,
        catalog_service: ExerciseCatalogService,
        session_store: SessionStore,
    ) -> AuthService:
        return AuthService(
            identity_verifier,
            identity_repository,
            user_repository,
            catalog_service,
            session_store,
        )

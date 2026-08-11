from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from training_systems.features.authentication.application import (
    GoogleOAuthFlow,
    GoogleOAuthProvider,
    PasswordAuthFlow,
    PasswordHasher,
    SessionRefresher,
    TokenIssuer,
)
from training_systems.features.authentication.domain import AuthIdentityRepository
from training_systems.features.authentication.infrastructure.auth_settings import (
    AuthSettings,
)
from training_systems.features.authentication.infrastructure.google_auth_settings import (  # noqa: E501
    GoogleAuthSettings,
)
from training_systems.features.authentication.infrastructure.google_oauth_client import (  # noqa: E501
    GoogleOAuthClient,
)
from training_systems.features.authentication.infrastructure.identity_repository import (  # noqa: E501
    SqlAuthIdentityRepository,
)
from training_systems.features.authentication.infrastructure.jwt_token_issuer import (
    JwtTokenIssuer,
)
from training_systems.features.authentication.infrastructure.oauth_state_settings import (  # noqa: E501
    OAuthStateSettings,
)
from training_systems.features.authentication.infrastructure.password_hasher import (
    Pbkdf2PasswordHasher,
)
from training_systems.features.authentication.presentation.oauth_state_cookies import (
    GoogleOAuthStateCookies,
)
from training_systems.features.exercises.application import ExerciseCatalogService
from training_systems.features.users.domain import UserRepository
from training_systems.settings import AppSettings


class AuthenticationProvider(Provider):
    @provide(scope=Scope.APP)
    def app_settings(self) -> AppSettings:
        return AppSettings()

    @provide(scope=Scope.APP)
    def auth_settings(self) -> AuthSettings:
        return AuthSettings()

    @provide(scope=Scope.APP)
    def google_auth_settings(self) -> GoogleAuthSettings:
        return GoogleAuthSettings()

    @provide(scope=Scope.APP)
    def oauth_state_settings(self) -> OAuthStateSettings:
        return OAuthStateSettings()

    @provide(scope=Scope.APP)
    def token_issuer(self, settings: AuthSettings) -> TokenIssuer:
        return JwtTokenIssuer(settings)

    @provide(scope=Scope.APP)
    def google_oauth_provider(
        self, settings: GoogleAuthSettings
    ) -> GoogleOAuthProvider:
        return GoogleOAuthClient(settings)

    @provide(scope=Scope.APP)
    def password_hasher(self) -> PasswordHasher:
        return Pbkdf2PasswordHasher()

    @provide(scope=Scope.REQUEST)
    def identity_repository(self, session: AsyncSession) -> AuthIdentityRepository:
        return SqlAuthIdentityRepository(session)

    @provide(scope=Scope.REQUEST)
    def google_oauth_flow(
        self,
        user_repository: UserRepository,
        identity_repository: AuthIdentityRepository,
        google_oauth_provider: GoogleOAuthProvider,
        token_issuer: TokenIssuer,
        catalog_service: ExerciseCatalogService,
    ) -> GoogleOAuthFlow:
        return GoogleOAuthFlow(
            user_repository,
            identity_repository,
            google_oauth_provider,
            token_issuer,
            catalog_service,
        )

    @provide(scope=Scope.REQUEST)
    def password_auth_flow(
        self,
        user_repository: UserRepository,
        identity_repository: AuthIdentityRepository,
        password_hasher: PasswordHasher,
        token_issuer: TokenIssuer,
        catalog_service: ExerciseCatalogService,
    ) -> PasswordAuthFlow:
        return PasswordAuthFlow(
            user_repository,
            identity_repository,
            password_hasher,
            token_issuer,
            catalog_service,
        )

    @provide(scope=Scope.REQUEST)
    def session_refresher(
        self, user_repository: UserRepository, token_issuer: TokenIssuer
    ) -> SessionRefresher:
        return SessionRefresher(user_repository, token_issuer)

    @provide(scope=Scope.REQUEST)
    def google_oauth_state_cookies(
        self,
        auth_settings: AuthSettings,
        google_auth_settings: GoogleAuthSettings,
        oauth_state_settings: OAuthStateSettings,
        app_settings: AppSettings,
    ) -> GoogleOAuthStateCookies:
        return GoogleOAuthStateCookies(
            cookie_name=google_auth_settings.state_cookie_name,
            ttl_seconds=oauth_state_settings.ttl_seconds,
            signing_secret=auth_settings.jwt_secret,
            app_settings=app_settings,
        )

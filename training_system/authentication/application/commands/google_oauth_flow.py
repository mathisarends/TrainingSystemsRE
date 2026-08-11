import secrets

from training_system.authentication.application.exceptions import (
    InvalidCredentialsException,
)
from training_system.authentication.application.ports import (
    GoogleOAuthProvider,
    TokenIssuer,
)
from training_system.authentication.application.schemas import (
    AuthSession,
    GoogleAuthorizationRequest,
    GoogleCallbackResult,
    GoogleIdentity,
)
from training_system.authentication.domain import AuthIdentity, AuthIdentityRepository
from training_system.features.exercises.application import ExerciseCatalogService
from training_system.features.users.domain import User, UserRepository

GOOGLE_PROVIDER = "google"


class GoogleOAuthFlow:
    _STATE_TOKEN_BYTES = 32

    def __init__(
        self,
        user_repository: UserRepository,
        identity_repository: AuthIdentityRepository,
        google_oauth_provider: GoogleOAuthProvider,
        token_issuer: TokenIssuer,
        catalog_service: ExerciseCatalogService,
    ) -> None:
        self._user_repository = user_repository
        self._identity_repository = identity_repository
        self._google_oauth_provider = google_oauth_provider
        self._token_issuer = token_issuer
        self._catalog_service = catalog_service

    def login(self) -> GoogleAuthorizationRequest:
        oauth_state = secrets.token_urlsafe(self._STATE_TOKEN_BYTES)
        authorization_url = self._google_oauth_provider.build_authorization_url(
            state=oauth_state
        )
        return GoogleAuthorizationRequest(
            authorization_url=authorization_url, state=oauth_state
        )

    async def callback(
        self,
        *,
        code: str | None,
        state: str,
        error: str | None,
        expected_oauth_state: str | None,
    ) -> GoogleCallbackResult:
        if error is not None:
            return GoogleCallbackResult.error(reason=error)

        if code is None:
            return GoogleCallbackResult.error(reason="missing_code")

        try:
            session = await self._create_session(
                authorization_code=code,
                oauth_state=state,
                expected_oauth_state=expected_oauth_state,
            )
        except InvalidCredentialsException:
            return GoogleCallbackResult.error(reason="invalid_credentials")

        return GoogleCallbackResult.success(session=session)

    async def _create_session(
        self,
        *,
        authorization_code: str,
        oauth_state: str,
        expected_oauth_state: str | None,
    ) -> AuthSession:
        if expected_oauth_state is None or not secrets.compare_digest(
            expected_oauth_state, oauth_state
        ):
            raise InvalidCredentialsException("Invalid or missing OAuth state")

        try:
            identity = await self._google_oauth_provider.exchange_code_for_identity(
                authorization_code=authorization_code
            )
        except ValueError as exc:
            raise InvalidCredentialsException(
                "Invalid Google authorization code"
            ) from exc

        if not identity.email_verified:
            raise InvalidCredentialsException("Google account email is not verified")

        user = await self._resolve_user(identity)
        return self._token_issuer.create_session(user_id=user.id)

    async def _resolve_user(self, identity: GoogleIdentity) -> User:
        existing_identity = await self._identity_repository.find_by_provider_subject(
            provider=GOOGLE_PROVIDER, subject=identity.subject
        )
        if existing_identity is not None:
            user = await self._user_repository.find_by_id(
                user_id=existing_identity.user_id
            )
            if user is None:
                raise InvalidCredentialsException("Auth identity has no owning user")
            return await self._sync_picture(user, identity.picture_url)

        if await self._user_repository.find_by_email(email=identity.email) is not None:
            raise InvalidCredentialsException(
                "Email already belongs to another auth identity"
            )

        display_name = identity.name or identity.email.split("@", maxsplit=1)[0]
        user = await self._user_repository.save(
            user=User(
                name=display_name,
                email=identity.email,
                picture_url=identity.picture_url,
            )
        )
        await self._identity_repository.save(
            identity=AuthIdentity(
                user_id=user.id, provider=GOOGLE_PROVIDER, subject=identity.subject
            )
        )
        await self._catalog_service.seed_defaults(user_id=user.id)
        return user

    async def _sync_picture(self, user: User, picture_url: str | None) -> User:
        if picture_url is None or user.picture_url == picture_url:
            return user
        return await self._user_repository.save(
            user=user.update_profile(picture_url=picture_url)
        )

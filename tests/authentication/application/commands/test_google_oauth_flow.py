
from training_system.features.authentication.application import (
    GoogleIdentity,
    GoogleOAuthFlow,
)
from training_system.features.exercises.application import ExerciseCatalogService
from training_system.features.users.domain import User

from ..conftest import (
    FakeAuthIdentityRepository,
    FakeGoogleOAuthProvider,
    FakeTokenIssuer,
    FakeUserRepository,
)


def _make_flow(
    *,
    user_repository: FakeUserRepository,
    identity_repository: FakeAuthIdentityRepository,
    token_issuer: FakeTokenIssuer,
    catalog_service: ExerciseCatalogService,
    identity: GoogleIdentity | None,
) -> GoogleOAuthFlow:
    return GoogleOAuthFlow(
        user_repository,
        identity_repository,
        FakeGoogleOAuthProvider(identity=identity),
        token_issuer,
        catalog_service,
    )


def test_login_returns_an_authorization_url_carrying_the_generated_state(
    user_repository: FakeUserRepository,
    identity_repository: FakeAuthIdentityRepository,
    token_issuer: FakeTokenIssuer,
    catalog_service: ExerciseCatalogService,
) -> None:
    flow = _make_flow(
        user_repository=user_repository,
        identity_repository=identity_repository,
        token_issuer=token_issuer,
        catalog_service=catalog_service,
        identity=None,
    )

    request = flow.login()

    assert request.state in request.authorization_url


async def test_callback_surfaces_the_providers_error_without_exchanging_a_code(
    user_repository: FakeUserRepository,
    identity_repository: FakeAuthIdentityRepository,
    token_issuer: FakeTokenIssuer,
    catalog_service: ExerciseCatalogService,
) -> None:
    flow = _make_flow(
        user_repository=user_repository,
        identity_repository=identity_repository,
        token_issuer=token_issuer,
        catalog_service=catalog_service,
        identity=None,
    )

    result = await flow.callback(
        code=None, state="s", error="access_denied", expected_oauth_state="s"
    )

    assert result.succeeded is False
    assert result.error_reason == "access_denied"


async def test_callback_rejects_a_state_mismatch(
    user_repository: FakeUserRepository,
    identity_repository: FakeAuthIdentityRepository,
    token_issuer: FakeTokenIssuer,
    catalog_service: ExerciseCatalogService,
) -> None:
    identity = GoogleIdentity(
        subject="google-1", email="alice@example.com", email_verified=True
    )
    flow = _make_flow(
        user_repository=user_repository,
        identity_repository=identity_repository,
        token_issuer=token_issuer,
        catalog_service=catalog_service,
        identity=identity,
    )

    result = await flow.callback(
        code="auth-code",
        state="the-real-state",
        error=None,
        expected_oauth_state="a-different-state",
    )

    assert result.succeeded is False
    assert result.error_reason == "invalid_credentials"
    assert token_issuer.issued_for == []


async def test_callback_rejects_an_unverified_email(
    user_repository: FakeUserRepository,
    identity_repository: FakeAuthIdentityRepository,
    token_issuer: FakeTokenIssuer,
    catalog_service: ExerciseCatalogService,
) -> None:
    identity = GoogleIdentity(
        subject="google-1", email="alice@example.com", email_verified=False
    )
    flow = _make_flow(
        user_repository=user_repository,
        identity_repository=identity_repository,
        token_issuer=token_issuer,
        catalog_service=catalog_service,
        identity=identity,
    )

    result = await flow.callback(
        code="auth-code", state="s", error=None, expected_oauth_state="s"
    )

    assert result.succeeded is False
    assert result.error_reason == "invalid_credentials"


async def test_callback_creates_a_new_user_and_seeds_the_catalog_on_first_login(
    user_repository: FakeUserRepository,
    identity_repository: FakeAuthIdentityRepository,
    token_issuer: FakeTokenIssuer,
    catalog_service: ExerciseCatalogService,
) -> None:
    identity = GoogleIdentity(
        subject="google-1",
        email="alice@example.com",
        name="Alice",
        email_verified=True,
    )
    flow = _make_flow(
        user_repository=user_repository,
        identity_repository=identity_repository,
        token_issuer=token_issuer,
        catalog_service=catalog_service,
        identity=identity,
    )

    result = await flow.callback(
        code="auth-code", state="s", error=None, expected_oauth_state="s"
    )

    assert result.succeeded is True
    assert result.session is not None
    stored_identity = await identity_repository.find_by_provider_subject(
        provider="google", subject="google-1"
    )
    assert stored_identity is not None
    catalog = await catalog_service.get_catalog(user_id=stored_identity.user_id)
    assert len(catalog.exercises) > 0


async def test_callback_is_idempotent_for_the_same_google_subject(
    user_repository: FakeUserRepository,
    identity_repository: FakeAuthIdentityRepository,
    token_issuer: FakeTokenIssuer,
    catalog_service: ExerciseCatalogService,
) -> None:
    identity = GoogleIdentity(
        subject="google-1", email="alice@example.com", email_verified=True
    )
    flow = _make_flow(
        user_repository=user_repository,
        identity_repository=identity_repository,
        token_issuer=token_issuer,
        catalog_service=catalog_service,
        identity=identity,
    )

    first = await flow.callback(
        code="auth-code", state="s", error=None, expected_oauth_state="s"
    )
    second = await flow.callback(
        code="auth-code", state="s", error=None, expected_oauth_state="s"
    )

    assert first.session is not None
    assert second.session is not None
    assert first.session.access_token == second.session.access_token


async def test_callback_rejects_a_google_email_already_used_by_another_identity(
    user_repository: FakeUserRepository,
    identity_repository: FakeAuthIdentityRepository,
    token_issuer: FakeTokenIssuer,
    catalog_service: ExerciseCatalogService,
) -> None:
    await user_repository.save(user=User(name="Alice", email="alice@example.com"))
    identity = GoogleIdentity(
        subject="google-1", email="alice@example.com", email_verified=True
    )
    flow = _make_flow(
        user_repository=user_repository,
        identity_repository=identity_repository,
        token_issuer=token_issuer,
        catalog_service=catalog_service,
        identity=identity,
    )

    result = await flow.callback(
        code="auth-code", state="s", error=None, expected_oauth_state="s"
    )

    assert result.succeeded is False
    assert result.error_reason == "invalid_credentials"

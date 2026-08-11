import pytest

from training_system.features.authentication.application import PasswordAuthFlow
from training_system.features.authentication.application.exceptions import (
    EmailAlreadyRegisteredException,
    InvalidCredentialsException,
)
from training_system.features.exercises.application import ExerciseCatalogService

from ..conftest import (
    FakeAuthIdentityRepository,
    FakePasswordHasher,
    FakeTokenIssuer,
    FakeUserRepository,
)


@pytest.fixture
def flow(
    user_repository: FakeUserRepository,
    identity_repository: FakeAuthIdentityRepository,
    password_hasher: FakePasswordHasher,
    token_issuer: FakeTokenIssuer,
    catalog_service: ExerciseCatalogService,
) -> PasswordAuthFlow:
    return PasswordAuthFlow(
        user_repository,
        identity_repository,
        password_hasher,
        token_issuer,
        catalog_service,
    )


async def test_register_creates_a_user_and_a_password_identity(
    flow: PasswordAuthFlow,
    identity_repository: FakeAuthIdentityRepository,
) -> None:
    result = await flow.register(
        email="Alice@Example.com", password="s3cret!!", name="  Alice  "
    )

    assert result.user.email == "alice@example.com"
    assert result.user.name == "Alice"
    identity = await identity_repository.find_by_provider_subject(
        provider="password", subject="alice@example.com"
    )
    assert identity is not None
    assert identity.password_hash == "hashed:s3cret!!"


async def test_register_seeds_the_default_exercise_catalog(
    flow: PasswordAuthFlow, catalog_service: ExerciseCatalogService
) -> None:
    result = await flow.register(
        email="alice@example.com", password="s3cret!!", name="Alice"
    )

    catalog = await catalog_service.get_catalog(user_id=result.user.id)
    assert len(catalog.exercises) > 0


async def test_register_rejects_a_duplicate_email(flow: PasswordAuthFlow) -> None:
    await flow.register(email="alice@example.com", password="s3cret!!", name="Alice")

    with pytest.raises(EmailAlreadyRegisteredException):
        await flow.register(
            email="alice@example.com", password="different!!", name="Alice2"
        )


async def test_login_succeeds_with_correct_credentials(
    flow: PasswordAuthFlow,
) -> None:
    await flow.register(email="alice@example.com", password="s3cret!!", name="Alice")

    result = await flow.login(email="alice@example.com", password="s3cret!!")

    assert result.user.email == "alice@example.com"
    assert result.session.access_token


async def test_login_rejects_an_unknown_email(flow: PasswordAuthFlow) -> None:
    with pytest.raises(InvalidCredentialsException):
        await flow.login(email="nobody@example.com", password="s3cret!!")


async def test_login_rejects_a_wrong_password(flow: PasswordAuthFlow) -> None:
    await flow.register(email="alice@example.com", password="s3cret!!", name="Alice")

    with pytest.raises(InvalidCredentialsException):
        await flow.login(email="alice@example.com", password="wrong-password")

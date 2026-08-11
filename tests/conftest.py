from collections.abc import AsyncIterator
from urllib.parse import parse_qs, urlsplit

import pytest
from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.pool import StaticPool

from training_system.authentication.application import (
    GoogleIdentity,
    GoogleOAuthProvider,
)
from training_system.authentication.infrastructure.provider import (
    AuthenticationProvider,
)
from training_system.infrastructure.database.models import DatabaseModel
from training_system.infrastructure.database.orm import register_models
from training_system.infrastructure.database.provider import DatabaseProvider
from training_system.infrastructure.scheduler.provider import SchedulerProvider
from training_system.main import FEATURES, register_features
from training_system.settings import DatabaseSettings

register_models()


class FakeGoogleOAuthProvider(GoogleOAuthProvider):
    """Treats the authorization code as the Google subject, deterministically."""

    def build_authorization_url(self, *, state: str) -> str:
        return f"https://accounts.google.com/o/oauth2/v2/auth?state={state}"

    async def exchange_code_for_identity(
        self, *, authorization_code: str
    ) -> GoogleIdentity:
        return GoogleIdentity(
            subject=authorization_code,
            email=f"{authorization_code}@example.com",
            name=authorization_code,
            email_verified=True,
        )


class TestDatabaseProvider(DatabaseProvider):
    @provide(scope=Scope.APP)
    def settings(self) -> DatabaseSettings:
        return DatabaseSettings(url="sqlite+aiosqlite://")

    @provide(scope=Scope.APP)
    async def engine(self, settings: DatabaseSettings) -> AsyncIterator[AsyncEngine]:
        engine = create_async_engine(
            settings.url,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
        )
        try:
            yield engine
        finally:
            await engine.dispose()


class TestAuthenticationProvider(AuthenticationProvider):
    @provide(scope=Scope.APP)
    def google_oauth_provider(self) -> GoogleOAuthProvider:
        return FakeGoogleOAuthProvider()


def _build_container() -> AsyncContainer:
    providers: list[Provider] = [TestDatabaseProvider(), SchedulerProvider()]
    for feature in FEATURES:
        for provider_cls in feature.providers:
            if provider_cls is AuthenticationProvider:
                providers.append(TestAuthenticationProvider())
            else:
                providers.append(provider_cls())
    return make_async_container(*providers)


@pytest.fixture
async def container() -> AsyncIterator[AsyncContainer]:
    built = _build_container()
    engine = await built.get(AsyncEngine)
    async with engine.begin() as connection:
        await connection.run_sync(DatabaseModel.metadata.create_all)
    yield built
    await built.close()


@pytest.fixture
async def client(container: AsyncContainer) -> AsyncIterator[AsyncClient]:
    app = FastAPI()
    register_features(app)
    setup_dishka(container, app)
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as http_client:
        yield http_client


async def login_with_google(client: AsyncClient, *, code: str) -> AsyncClient:
    login_response = await client.get(
        "/api/v1/auth/google/login", follow_redirects=False
    )
    assert login_response.status_code == 307

    redirect_query = parse_qs(urlsplit(login_response.headers["location"]).query)
    state = redirect_query["state"][0]

    callback_response = await client.get(
        "/api/v1/auth/google/callback",
        params={"code": code, "state": state},
    )
    assert callback_response.status_code == 200
    return client


@pytest.fixture
async def authenticated_client(client: AsyncClient) -> AsyncClient:
    return await login_with_google(client, code="user-1")

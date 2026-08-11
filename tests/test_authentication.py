from httpx import AsyncClient

from tests.conftest import login_with_google


async def test_google_login_creates_user_and_seeds_catalog(
    client: AsyncClient,
) -> None:
    await login_with_google(client, code="alice")

    assert "access_token" in client.cookies
    assert "refresh_token" in client.cookies

    me_response = await client.get("/api/v1/me")
    assert me_response.status_code == 200
    assert me_response.json()["name"] == "alice"
    assert me_response.json()["email"] == "alice@example.com"

    catalog_response = await client.get("/api/v1/me/exercises")
    assert catalog_response.status_code == 200
    assert len(catalog_response.json()["categories"]) > 0


async def test_google_login_is_idempotent_for_same_subject(
    client: AsyncClient,
) -> None:
    await login_with_google(client, code="bob")
    first = await client.get("/api/v1/me")

    await login_with_google(client, code="bob")
    second = await client.get("/api/v1/me")

    assert first.json()["id"] == second.json()["id"]


async def test_google_callback_rejects_mismatched_state(client: AsyncClient) -> None:
    login_response = await client.get(
        "/api/v1/auth/google/login", follow_redirects=False
    )
    assert login_response.status_code == 307

    callback_response = await client.get(
        "/api/v1/auth/google/callback",
        params={"code": "eve", "state": "not-the-cookie-value"},
    )
    assert callback_response.status_code == 200
    assert "access_token" not in callback_response.cookies

    me_response = await client.get("/api/v1/me")
    assert me_response.status_code == 401


async def test_me_requires_authentication(client: AsyncClient) -> None:
    response = await client.get("/api/v1/me")
    assert response.status_code == 401


async def test_logout_clears_session(authenticated_client: AsyncClient) -> None:
    logout_response = await authenticated_client.post("/api/v1/auth/logout")
    assert logout_response.status_code == 204

    me_response = await authenticated_client.get("/api/v1/me")
    assert me_response.status_code == 401


async def test_refresh_issues_a_usable_access_token(
    authenticated_client: AsyncClient,
) -> None:
    refresh_response = await authenticated_client.post("/api/v1/auth/refresh")
    assert refresh_response.status_code == 204
    assert "access_token" in authenticated_client.cookies

    me_response = await authenticated_client.get("/api/v1/me")
    assert me_response.status_code == 200


async def test_refresh_requires_refresh_token(client: AsyncClient) -> None:
    response = await client.post("/api/v1/auth/refresh")
    assert response.status_code == 401


async def test_register_creates_user_and_seeds_catalog(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={"name": "Carol", "email": "carol@example.com", "password": "s3cret!!"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Carol"
    assert body["email"] == "carol@example.com"
    assert "access_token" in response.cookies

    catalog_response = await client.get("/api/v1/me/exercises")
    assert catalog_response.status_code == 200
    assert len(catalog_response.json()["categories"]) > 0


async def test_register_rejects_duplicate_email(client: AsyncClient) -> None:
    payload = {"name": "Dan", "email": "dan@example.com", "password": "s3cret!!"}
    first = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    second = await client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409


async def test_login_with_password_succeeds(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={"name": "Erin", "email": "erin@example.com", "password": "s3cret!!"},
    )
    await client.post("/api/v1/auth/logout")

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "erin@example.com", "password": "s3cret!!"},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "erin@example.com"


async def test_login_with_password_rejects_wrong_password(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={"name": "Frank", "email": "frank@example.com", "password": "s3cret!!"},
    )
    await client.post("/api/v1/auth/logout")

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "frank@example.com", "password": "wrong-password"},
    )
    assert response.status_code == 401

from httpx import AsyncClient


async def test_login_creates_user_and_seeds_catalog(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/google", json={"credential": "alice"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "alice"
    assert body["email"] == "alice@example.com"
    assert "session_token" in response.cookies

    catalog_response = await client.get("/api/v1/me/exercises")
    assert catalog_response.status_code == 200
    assert len(catalog_response.json()["categories"]) > 0


async def test_login_is_idempotent_for_same_subject(client: AsyncClient) -> None:
    first = await client.post("/api/v1/auth/google", json={"credential": "bob"})
    second = await client.post("/api/v1/auth/google", json={"credential": "bob"})

    assert first.json()["id"] == second.json()["id"]


async def test_me_requires_authentication(client: AsyncClient) -> None:
    response = await client.get("/api/v1/me")
    assert response.status_code == 401


async def test_logout_clears_session(authenticated_client: AsyncClient) -> None:
    logout_response = await authenticated_client.delete("/api/v1/auth/session")
    assert logout_response.status_code == 204

    me_response = await authenticated_client.get("/api/v1/me")
    assert me_response.status_code == 401

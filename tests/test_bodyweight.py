from httpx import AsyncClient


async def test_overview_defaults_to_maintain_goal_with_no_entries(
    authenticated_client: AsyncClient,
) -> None:
    response = await authenticated_client.get("/api/v1/me/bodyweight")
    assert response.status_code == 200
    body = response.json()
    assert body["entries"] == []
    assert body["goal"] == {"direction": "MAINTAIN", "rate": 0.0}


async def test_upsert_entry_is_idempotent_by_date(
    authenticated_client: AsyncClient,
) -> None:
    first = await authenticated_client.put(
        "/api/v1/me/bodyweight/entries/2026-01-05", json={"weight": 82.5}
    )
    assert first.status_code == 200
    assert first.json() == {"date": "2026-01-05", "weight": 82.5}

    second = await authenticated_client.put(
        "/api/v1/me/bodyweight/entries/2026-01-05", json={"weight": 83.0}
    )
    assert second.status_code == 200

    overview = await authenticated_client.get("/api/v1/me/bodyweight")
    entries = overview.json()["entries"]
    assert len(entries) == 1
    assert entries[0]["weight"] == 83.0


async def test_update_goal(authenticated_client: AsyncClient) -> None:
    response = await authenticated_client.patch(
        "/api/v1/me/bodyweight", json={"direction": "LOSE", "rate": 0.5}
    )
    assert response.status_code == 200
    assert response.json() == {"direction": "LOSE", "rate": 0.5}

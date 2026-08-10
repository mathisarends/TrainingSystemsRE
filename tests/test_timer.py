from httpx import AsyncClient


async def test_start_timer_is_idempotent(authenticated_client: AsyncClient) -> None:
    first = await authenticated_client.put("/api/v1/me/timer")
    assert first.status_code == 200
    assert first.json() == {"active": True}

    second = await authenticated_client.put("/api/v1/me/timer")
    assert second.status_code == 200
    assert second.json() == {"active": True}


async def test_stop_timer_without_start_is_a_no_op(
    authenticated_client: AsyncClient,
) -> None:
    response = await authenticated_client.delete("/api/v1/me/timer")
    assert response.status_code == 200
    assert response.json() == {"active": False}


async def test_stop_after_start(authenticated_client: AsyncClient) -> None:
    await authenticated_client.put("/api/v1/me/timer")
    response = await authenticated_client.delete("/api/v1/me/timer")
    assert response.status_code == 200
    assert response.json() == {"active": False}

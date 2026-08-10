from typing import Any

from httpx import AsyncClient


async def _upsert(
    client: AsyncClient, *, exercise: str, est_max: float, weight: float = 100.0
) -> dict[str, Any]:
    response = await client.put(
        f"/api/v1/me/records/{exercise}",
        json={
            "category": "Squat",
            "sets": 3,
            "reps": 5,
            "weight": weight,
            "actual_rpe": 8,
            "est_max": est_max,
        },
    )
    assert response.status_code == 200
    result: dict[str, Any] = response.json()
    return result


async def test_first_upsert_is_always_accepted(
    authenticated_client: AsyncClient,
) -> None:
    result = await _upsert(authenticated_client, exercise="Back Squat", est_max=150)
    assert result["accepted"] is True
    assert result["record"]["est_max"] == 150


async def test_upsert_rejected_when_not_a_new_max(
    authenticated_client: AsyncClient,
) -> None:
    await _upsert(authenticated_client, exercise="Back Squat", est_max=150)
    result = await _upsert(authenticated_client, exercise="Back Squat", est_max=140)

    assert result["accepted"] is False
    assert result["record"]["est_max"] == 150


async def test_upsert_accepted_when_new_max_pushes_history(
    authenticated_client: AsyncClient,
) -> None:
    await _upsert(authenticated_client, exercise="Back Squat", est_max=150)
    result = await _upsert(authenticated_client, exercise="Back Squat", est_max=160)

    assert result["accepted"] is True
    assert result["record"]["est_max"] == 160
    assert len(result["record"]["history"]) == 1
    assert result["record"]["history"][0]["est_max"] == 150


async def test_revert_pops_back_to_previous_record(
    authenticated_client: AsyncClient,
) -> None:
    await _upsert(authenticated_client, exercise="Back Squat", est_max=150)
    await _upsert(authenticated_client, exercise="Back Squat", est_max=160)

    response = await authenticated_client.delete("/api/v1/me/records/Back Squat")
    assert response.status_code == 200
    body = response.json()
    assert body["est_max"] == 150
    assert body["history"] == []


async def test_revert_with_no_history_deletes_record(
    authenticated_client: AsyncClient,
) -> None:
    await _upsert(authenticated_client, exercise="Back Squat", est_max=150)

    response = await authenticated_client.delete("/api/v1/me/records/Back Squat")
    assert response.status_code == 200
    assert response.json() is None

    list_response = await authenticated_client.get("/api/v1/me/records")
    assert list_response.json()["items"] == []

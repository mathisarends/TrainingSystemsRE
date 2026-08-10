from typing import Any

from httpx import AsyncClient


async def _create_plan(client: AsyncClient) -> dict[str, Any]:
    response = await client.post(
        "/api/v1/plans",
        json={
            "title": "Strength Block",
            "weekdays": ["Mon", "Wed", "Fri"],
            "block_length": 3,
            "start_date": "2026-01-05",
        },
    )
    assert response.status_code == 201
    result: dict[str, Any] = response.json()
    return result


async def test_create_plan_builds_empty_week_day_structure(
    authenticated_client: AsyncClient,
) -> None:
    plan = await _create_plan(authenticated_client)

    assert len(plan["weeks"]) == 3
    assert len(plan["weeks"][0]["days"]) == 3
    assert plan["weeks"][0]["days"][0]["entries"] == []


async def test_day_edit_propagates_structure_to_future_weeks(
    authenticated_client: AsyncClient,
) -> None:
    plan = await _create_plan(authenticated_client)
    plan_id = plan["id"]

    patch_response = await authenticated_client.patch(
        f"/api/v1/plans/{plan_id}",
        json={
            "day_edit": {
                "week_index": 0,
                "day_index": 0,
                "entries": [
                    {
                        "category": "Squat",
                        "exercise_name": "Back Squat",
                        "sets": 3,
                        "reps": 5,
                        "target_rpe": 8,
                        "weight": 100.0,
                    }
                ],
            }
        },
    )
    assert patch_response.status_code == 200
    patched = patch_response.json()

    future_week_entry = patched["weeks"][1]["days"][0]["entries"][0]
    assert future_week_entry["exercise_name"] == "Back Squat"
    assert future_week_entry["sets"] == 3
    assert future_week_entry["target_rpe"] == 8
    # Weight/actual_rpe must not propagate forward, only structure.
    assert future_week_entry["weight"] is None

    edited_entry = patched["weeks"][0]["days"][0]["entries"][0]
    assert edited_entry["weight"] == 100.0
    assert patched["last_used_week_index"] == 0
    assert patched["last_used_day_index"] == 0


async def test_get_plan_recommends_previous_week_weight(
    authenticated_client: AsyncClient,
) -> None:
    plan = await _create_plan(authenticated_client)
    plan_id = plan["id"]

    await authenticated_client.patch(
        f"/api/v1/plans/{plan_id}",
        json={
            "day_edit": {
                "week_index": 0,
                "day_index": 0,
                "entries": [
                    {
                        "category": "Squat",
                        "exercise_name": "Back Squat",
                        "sets": 3,
                        "reps": 5,
                        "target_rpe": 8,
                        "weight": 100.0,
                    }
                ],
            }
        },
    )

    get_response = await authenticated_client.get(f"/api/v1/plans/{plan_id}")
    assert get_response.status_code == 200
    future_entry = get_response.json()["weeks"][1]["days"][0]["entries"][0]
    assert future_entry["recommended_weight"] == 100.0


async def test_progression_caps_squat_rpe_at_nine(
    authenticated_client: AsyncClient,
) -> None:
    plan = await _create_plan(authenticated_client)
    plan_id = plan["id"]

    await authenticated_client.patch(
        f"/api/v1/plans/{plan_id}",
        json={
            "day_edit": {
                "week_index": 0,
                "day_index": 0,
                "entries": [
                    {
                        "category": "Squat",
                        "exercise_name": "Back Squat",
                        "sets": 3,
                        "reps": 5,
                        "target_rpe": 8.5,
                    }
                ],
            }
        },
    )

    response = await authenticated_client.post(
        f"/api/v1/plans/{plan_id}/progressions",
        json={"rpe_increment": 1, "deload_last_week": False},
    )
    assert response.status_code == 200
    body = response.json()
    week1_entry = body["weeks"][1]["days"][0]["entries"][0]
    assert week1_entry["target_rpe"] == 9.0


async def test_delete_plan_returns_404_afterward(
    authenticated_client: AsyncClient,
) -> None:
    plan = await _create_plan(authenticated_client)
    plan_id = plan["id"]

    delete_response = await authenticated_client.delete(f"/api/v1/plans/{plan_id}")
    assert delete_response.status_code == 204

    get_response = await authenticated_client.get(f"/api/v1/plans/{plan_id}")
    assert get_response.status_code == 404


async def test_list_plans_returns_card_projection(
    authenticated_client: AsyncClient,
) -> None:
    await _create_plan(authenticated_client)

    response = await authenticated_client.get("/api/v1/plans")
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 1
    assert items[0]["title"] == "Strength Block"
    assert items[0]["frequency"] == 3

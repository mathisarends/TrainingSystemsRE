from typing import Any

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from training_system.features.authentication.presentation import AuthenticatedUserId
from training_system.features.records.application import PersonalRecordService
from training_system.features.records.presentation.mapper import (
    to_list_response,
    to_response,
    to_upsert_response,
)
from training_system.features.records.presentation.schemas import (
    PersonalRecordListResponse,
    PersonalRecordResponse,
    UpsertRecordRequest,
    UpsertRecordResponse,
)
from training_system.presentation.schema import ErrorResponse

RESPONSES: dict[int | str, dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
}
NOT_FOUND_RESPONSES: dict[int | str, dict[str, Any]] = {
    **RESPONSES,
    status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
}

router = APIRouter(prefix="/me/records", tags=["records"], route_class=DishkaRoute)


@router.get(
    "",
    operation_id="list_personal_records",
    response_model=PersonalRecordListResponse,
    status_code=status.HTTP_200_OK,
    responses=RESPONSES,
)
async def list_personal_records(
    authenticated_user_id: AuthenticatedUserId,
    record_service: FromDishka[PersonalRecordService],
) -> PersonalRecordListResponse:
    records = await record_service.list_records(user_id=authenticated_user_id)
    return to_list_response(records)


@router.put(
    "/{exercise_id}",
    operation_id="upsert_personal_record",
    response_model=UpsertRecordResponse,
    status_code=status.HTTP_200_OK,
    responses=RESPONSES,
)
async def upsert_personal_record(
    exercise_id: str,
    body: UpsertRecordRequest,
    authenticated_user_id: AuthenticatedUserId,
    record_service: FromDishka[PersonalRecordService],
) -> UpsertRecordResponse:
    result = await record_service.upsert_record(
        user_id=authenticated_user_id,
        exercise_name=exercise_id,
        category=body.category,
        sets=body.sets,
        reps=body.reps,
        weight=body.weight,
        actual_rpe=body.actual_rpe,
        est_max=body.est_max,
    )
    return to_upsert_response(result)


@router.delete(
    "/{exercise_id}",
    operation_id="revert_personal_record",
    response_model=PersonalRecordResponse | None,
    status_code=status.HTTP_200_OK,
    responses=NOT_FOUND_RESPONSES,
)
async def revert_personal_record(
    exercise_id: str,
    authenticated_user_id: AuthenticatedUserId,
    record_service: FromDishka[PersonalRecordService],
) -> PersonalRecordResponse | None:
    record = await record_service.revert_to_previous(
        user_id=authenticated_user_id, exercise_name=exercise_id
    )
    return to_response(record) if record is not None else None

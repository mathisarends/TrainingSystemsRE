from typing import Any

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from training_systems.features.authentication.presentation import AuthenticatedUserId
from training_systems.features.records.application import (
    PersonalRecordService,
    UpsertResult,
)
from training_systems.features.records.domain import PersonalRecord
from training_systems.features.records.presentation.schemas import (
    PersonalRecordListResponse,
    PersonalRecordResponse,
    RecordSnapshotResponse,
    UpsertRecordRequest,
    UpsertRecordResponse,
)
from training_systems.presentation.schema import ErrorResponse

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
    response_model=PersonalRecordListResponse,
    status_code=status.HTTP_200_OK,
    responses=RESPONSES,
)
async def list_personal_records(
    authenticated_user_id: AuthenticatedUserId,
    record_service: FromDishka[PersonalRecordService],
) -> PersonalRecordListResponse:
    records = await record_service.list_records(user_id=authenticated_user_id)
    return _to_list_response(records)


def _to_list_response(records: list[PersonalRecord]) -> PersonalRecordListResponse:
    return PersonalRecordListResponse(items=[_to_response(record) for record in records])


def _to_response(record: PersonalRecord) -> PersonalRecordResponse:
    return PersonalRecordResponse(
        exercise_name=record.exercise_name,
        category=record.category,
        sets=record.sets,
        reps=record.reps,
        weight=record.weight,
        actual_rpe=record.actual_rpe,
        est_max=record.est_max,
        achieved_at=record.achieved_at,
        history=[
            RecordSnapshotResponse(
                sets=snapshot.sets,
                reps=snapshot.reps,
                weight=snapshot.weight,
                actual_rpe=snapshot.actual_rpe,
                est_max=snapshot.est_max,
                achieved_at=snapshot.achieved_at,
            )
            for snapshot in record.history
        ],
    )


@router.put(
    "/{exercise_id}",
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
    return _to_upsert_response(result)


def _to_upsert_response(result: UpsertResult) -> UpsertRecordResponse:
    return UpsertRecordResponse(
        record=_to_response(result.record), accepted=result.accepted
    )


@router.delete(
    "/{exercise_id}",
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
    return _to_response(record) if record is not None else None

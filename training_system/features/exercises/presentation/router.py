from typing import Any

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from training_system.features.authentication.presentation import AuthenticatedUserId
from training_system.features.exercises.application import ExerciseCatalogService
from training_system.features.exercises.presentation.mapper import (
    to_category_updates,
    to_exercise_upserts,
    to_response,
)
from training_system.features.exercises.presentation.schemas import (
    ExerciseCatalogResponse,
    PatchExerciseCatalogRequest,
)
from training_system.presentation.schema import ErrorResponse

RESPONSES: dict[int | str, dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
    status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
}

router = APIRouter(prefix="/me/exercises", tags=["exercises"], route_class=DishkaRoute)


@router.get(
    "",
    operation_id="get_exercise_catalog",
    response_model=ExerciseCatalogResponse,
    status_code=status.HTTP_200_OK,
    responses=RESPONSES,
)
async def get_exercise_catalog(
    authenticated_user_id: AuthenticatedUserId,
    catalog_service: FromDishka[ExerciseCatalogService],
) -> ExerciseCatalogResponse:
    catalog = await catalog_service.get_catalog(user_id=authenticated_user_id)
    return to_response(catalog)


@router.patch(
    "",
    operation_id="update_exercise_catalog",
    response_model=ExerciseCatalogResponse,
    status_code=status.HTTP_200_OK,
    responses=RESPONSES,
)
async def update_exercise_catalog(
    body: PatchExerciseCatalogRequest,
    authenticated_user_id: AuthenticatedUserId,
    catalog_service: FromDishka[ExerciseCatalogService],
) -> ExerciseCatalogResponse:
    catalog = await catalog_service.patch_catalog(
        user_id=authenticated_user_id,
        category_updates=to_category_updates(body.categories),
        exercise_upserts=to_exercise_upserts(body.exercises),
    )
    return to_response(catalog)


@router.delete(
    "",
    operation_id="reset_exercise_catalog",
    response_model=ExerciseCatalogResponse,
    status_code=status.HTTP_200_OK,
    responses=RESPONSES,
)
async def reset_exercise_catalog(
    authenticated_user_id: AuthenticatedUserId,
    catalog_service: FromDishka[ExerciseCatalogService],
) -> ExerciseCatalogResponse:
    catalog = await catalog_service.reset_to_defaults(user_id=authenticated_user_id)
    return to_response(catalog)

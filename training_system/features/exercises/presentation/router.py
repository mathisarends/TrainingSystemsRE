from typing import Any

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from training_system.features.authentication.presentation import AuthenticatedUserId
from training_system.features.exercises.application import ExerciseCatalogService
from training_system.features.exercises.application.commands import (
    CategoryUpdate,
    ExerciseUpsert,
)
from training_system.features.exercises.domain import ExerciseCatalog
from training_system.features.exercises.presentation.schemas import (
    CategoryResponse,
    CategoryUpdateRequest,
    ExerciseCatalogResponse,
    ExerciseResponse,
    ExerciseUpsertRequest,
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
    response_model=ExerciseCatalogResponse,
    status_code=status.HTTP_200_OK,
    responses=RESPONSES,
)
async def get_exercise_catalog(
    authenticated_user_id: AuthenticatedUserId,
    catalog_service: FromDishka[ExerciseCatalogService],
) -> ExerciseCatalogResponse:
    catalog = await catalog_service.get_catalog(user_id=authenticated_user_id)
    return _to_response(catalog)


def _to_response(catalog: ExerciseCatalog) -> ExerciseCatalogResponse:
    return ExerciseCatalogResponse(
        categories=[
            CategoryResponse(
                category=category.category,
                rest_seconds=category.rest_seconds,
                default_sets=category.default_sets,
                default_reps=category.default_reps,
                default_target_rpe=category.default_target_rpe,
            )
            for category in catalog.categories
        ],
        exercises_by_category={
            category.category: [
                ExerciseResponse(
                    id=exercise.id,
                    name=exercise.name,
                    max_factor=exercise.max_factor,
                )
                for exercise in catalog.exercises_in(category.category)
            ]
            for category in catalog.categories
        },
    )


@router.patch(
    "",
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
        category_updates=_to_category_updates(body.categories),
        exercise_upserts=_to_exercise_upserts(body.exercises),
    )
    return _to_response(catalog)


def _to_category_updates(
    requests: list[CategoryUpdateRequest],
) -> list[CategoryUpdate]:
    return [
        CategoryUpdate(
            category=request.category,
            rest_seconds=request.rest_seconds,
            default_sets=request.default_sets,
            default_reps=request.default_reps,
            default_target_rpe=request.default_target_rpe,
        )
        for request in requests
    ]


def _to_exercise_upserts(
    requests: list[ExerciseUpsertRequest],
) -> list[ExerciseUpsert]:
    return [
        ExerciseUpsert(
            id=request.id,
            category=request.category,
            name=request.name,
            max_factor=request.max_factor,
        )
        for request in requests
    ]


@router.delete(
    "",
    response_model=ExerciseCatalogResponse,
    status_code=status.HTTP_200_OK,
    responses=RESPONSES,
)
async def reset_exercise_catalog(
    authenticated_user_id: AuthenticatedUserId,
    catalog_service: FromDishka[ExerciseCatalogService],
) -> ExerciseCatalogResponse:
    catalog = await catalog_service.reset_to_defaults(user_id=authenticated_user_id)
    return _to_response(catalog)

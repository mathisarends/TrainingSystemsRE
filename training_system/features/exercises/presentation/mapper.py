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
)


def to_response(catalog: ExerciseCatalog) -> ExerciseCatalogResponse:
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


def to_category_updates(
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


def to_exercise_upserts(
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

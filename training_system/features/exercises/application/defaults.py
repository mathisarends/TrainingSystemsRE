from uuid import UUID, uuid4

from training_system.features.exercises.domain import (
    DEFAULT_CATEGORY_DEFAULTS,
    DEFAULT_EXERCISES,
    CatalogExercise,
    ExerciseCatalog,
)


def build_default_catalog(*, user_id: UUID) -> ExerciseCatalog:
    positions: dict[str, int] = {}
    exercises: list[CatalogExercise] = []
    for category, name, max_factor in DEFAULT_EXERCISES:
        position = positions.get(category, 0)
        exercises.append(
            CatalogExercise(
                id=uuid4(),
                category=category,
                name=name,
                position=position,
                max_factor=max_factor,
            )
        )
        positions[category] = position + 1

    return ExerciseCatalog(
        user_id=user_id,
        categories=list(DEFAULT_CATEGORY_DEFAULTS),
        exercises=exercises,
    )

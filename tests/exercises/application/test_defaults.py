from uuid import uuid4

from training_systems.features.exercises.application.defaults import (
    build_default_catalog,
)
from training_systems.features.exercises.domain import (
    DEFAULT_CATEGORY_DEFAULTS,
    DEFAULT_EXERCISES,
    ExerciseCategory,
)


def test_build_default_catalog_seeds_all_default_category_defaults() -> None:
    catalog = build_default_catalog(user_id=uuid4())

    assert len(catalog.categories) == len(DEFAULT_CATEGORY_DEFAULTS)


def test_build_default_catalog_seeds_all_default_exercises() -> None:
    catalog = build_default_catalog(user_id=uuid4())

    assert len(catalog.exercises) == len(DEFAULT_EXERCISES)


def test_build_default_catalog_positions_exercises_sequentially_per_category() -> None:
    catalog = build_default_catalog(user_id=uuid4())

    squats = catalog.exercises_in(ExerciseCategory.SQUAT)

    assert [exercise.position for exercise in squats] == list(range(len(squats)))

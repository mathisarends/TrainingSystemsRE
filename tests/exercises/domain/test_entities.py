from uuid import uuid4

from training_system.features.exercises.domain import (
    CatalogExercise,
    ExerciseCatalog,
    ExerciseCategory,
)


def _exercise(
    *, category: ExerciseCategory, name: str, position: int
) -> CatalogExercise:
    return CatalogExercise(id=uuid4(), category=category, name=name, position=position)


def test_exercises_in_returns_only_the_requested_category_sorted_by_position() -> None:
    catalog = ExerciseCatalog(
        user_id=uuid4(),
        exercises=[
            _exercise(category=ExerciseCategory.SQUAT, name="B", position=1),
            _exercise(category=ExerciseCategory.SQUAT, name="A", position=0),
            _exercise(category=ExerciseCategory.BENCH, name="C", position=0),
        ],
    )

    squats = catalog.exercises_in(ExerciseCategory.SQUAT)

    assert [exercise.name for exercise in squats] == ["A", "B"]


def test_exercises_in_returns_empty_list_for_a_category_with_no_exercises() -> None:
    catalog = ExerciseCatalog(user_id=uuid4())

    assert catalog.exercises_in(ExerciseCategory.SQUAT) == []

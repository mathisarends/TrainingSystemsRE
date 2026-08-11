from enum import StrEnum
from uuid import UUID


class ExerciseCategory(StrEnum):
    SQUAT = "Squat"
    BENCH = "Bench"
    DEADLIFT = "Deadlift"
    OVERHEADPRESS = "Overheadpress"
    CHEST = "Chest"
    BACK = "Back"
    SHOULDER = "Shoulder"
    TRICEPS = "Triceps"
    BICEPS = "Biceps"
    LEGS = "Legs"


class CategoryDefaults:
    def __init__(
        self,
        category: ExerciseCategory,
        rest_seconds: int,
        default_sets: int,
        default_reps: int,
        default_target_rpe: float,
    ) -> None:
        self.category = category
        self.rest_seconds = rest_seconds
        self.default_sets = default_sets
        self.default_reps = default_reps
        self.default_target_rpe = default_target_rpe


class CatalogExercise:
    def __init__(
        self,
        *,
        id: UUID,
        category: ExerciseCategory,
        name: str,
        position: int,
        max_factor: float | None = None,
    ) -> None:
        self.id = id
        self.category = category
        self.name = name
        self.position = position
        self.max_factor = max_factor


class ExerciseCatalog:
    def __init__(
        self,
        *,
        user_id: UUID,
        categories: list[CategoryDefaults] | None = None,
        exercises: list[CatalogExercise] | None = None,
    ) -> None:
        self.user_id = user_id
        self.categories = categories if categories is not None else []
        self.exercises = exercises if exercises is not None else []

    def exercises_in(self, category: ExerciseCategory) -> list[CatalogExercise]:
        return sorted(
            (exercise for exercise in self.exercises if exercise.category == category),
            key=lambda exercise: exercise.position,
        )

from dataclasses import dataclass, field
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CategoryDefaults:
    category: str
    rest_seconds: int
    default_sets: int
    default_reps: int
    default_target_rpe: float


@dataclass(frozen=True, slots=True)
class CatalogExercise:
    id: UUID
    category: str
    name: str
    position: int
    max_factor: float | None = None


@dataclass(slots=True)
class ExerciseCatalog:
    user_id: UUID
    categories: list[CategoryDefaults] = field(default_factory=list)
    exercises: list[CatalogExercise] = field(default_factory=list)

    def exercises_in(self, category: str) -> list[CatalogExercise]:
        return sorted(
            (exercise for exercise in self.exercises if exercise.category == category),
            key=lambda exercise: exercise.position,
        )

from dataclasses import dataclass
from uuid import UUID

from training_systems.features.exercises.domain import ExerciseCategory


@dataclass(frozen=True, slots=True)
class CategoryUpdate:
    category: ExerciseCategory
    rest_seconds: int | None = None
    default_sets: int | None = None
    default_reps: int | None = None
    default_target_rpe: float | None = None


@dataclass(frozen=True, slots=True)
class ExerciseUpsert:
    category: ExerciseCategory
    name: str
    id: UUID | None = None
    max_factor: float | None = None

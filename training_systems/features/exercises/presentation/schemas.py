from uuid import UUID

from pydantic import Field

from training_systems.features.exercises.domain import ExerciseCategory
from training_systems.presentation.schema import Schema


class CategoryResponse(Schema):
    category: ExerciseCategory
    rest_seconds: int
    default_sets: int
    default_reps: int
    default_target_rpe: float


class ExerciseResponse(Schema):
    id: UUID
    name: str
    max_factor: float | None


class ExerciseCatalogResponse(Schema):
    categories: list[CategoryResponse]
    exercises_by_category: dict[ExerciseCategory, list[ExerciseResponse]]


class CategoryUpdateRequest(Schema):
    category: ExerciseCategory
    rest_seconds: int | None = Field(default=None, ge=0)
    default_sets: int | None = Field(default=None, ge=0)
    default_reps: int | None = Field(default=None, ge=0)
    default_target_rpe: float | None = Field(default=None, ge=0, le=10)


class ExerciseUpsertRequest(Schema):
    id: UUID | None = None
    category: ExerciseCategory
    name: str = ""
    max_factor: float | None = None


class PatchExerciseCatalogRequest(Schema):
    categories: list[CategoryUpdateRequest] = Field(default_factory=list)
    exercises: list[ExerciseUpsertRequest] = Field(default_factory=list)

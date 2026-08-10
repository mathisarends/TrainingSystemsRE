from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, delete, select

from training_system.features.exercises.domain.entities import (
    CatalogExercise,
    CategoryDefaults,
    ExerciseCatalog,
)
from training_system.features.exercises.domain.repository import (
    ExerciseCatalogRepository,
)
from training_system.infrastructure.database.orm import (
    CatalogExerciseModel,
    ExerciseCategoryModel,
)


class SqlExerciseCatalogRepository(ExerciseCatalogRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_user(self, *, user_id: UUID) -> ExerciseCatalog | None:
        categories = (
            await self._session.scalars(
                select(ExerciseCategoryModel).where(
                    ExerciseCategoryModel.user_id == user_id
                )
            )
        ).all()
        if not categories:
            return None
        exercises = (
            await self._session.scalars(
                select(CatalogExerciseModel).where(
                    CatalogExerciseModel.user_id == user_id
                )
            )
        ).all()
        return ExerciseCatalog(
            user_id=user_id,
            categories=[
                CategoryDefaults(
                    category=category.category,
                    rest_seconds=category.rest_seconds,
                    default_sets=category.default_sets,
                    default_reps=category.default_reps,
                    default_target_rpe=category.default_target_rpe,
                )
                for category in categories
            ],
            exercises=[
                CatalogExercise(
                    id=exercise.id,
                    category=exercise.category,
                    name=exercise.name,
                    position=exercise.position,
                    max_factor=exercise.max_factor,
                )
                for exercise in exercises
            ],
        )

    async def replace(self, *, catalog: ExerciseCatalog) -> ExerciseCatalog:
        await self._session.execute(
            delete(ExerciseCategoryModel).where(
                col(ExerciseCategoryModel.user_id) == catalog.user_id
            )
        )
        await self._session.execute(
            delete(CatalogExerciseModel).where(
                col(CatalogExerciseModel.user_id) == catalog.user_id
            )
        )
        for category in catalog.categories:
            self._session.add(
                ExerciseCategoryModel(
                    user_id=catalog.user_id,
                    category=category.category,
                    rest_seconds=category.rest_seconds,
                    default_sets=category.default_sets,
                    default_reps=category.default_reps,
                    default_target_rpe=category.default_target_rpe,
                )
            )
        for exercise in catalog.exercises:
            self._session.add(
                CatalogExerciseModel(
                    id=exercise.id,
                    user_id=catalog.user_id,
                    category=exercise.category,
                    name=exercise.name,
                    position=exercise.position,
                    max_factor=exercise.max_factor,
                )
            )
        await self._session.flush()
        return catalog

from uuid import UUID, uuid4

from training_system.features.exercises.application.commands import (
    CategoryUpdate,
    ExerciseUpsert,
)
from training_system.features.exercises.application.defaults import (
    build_default_catalog,
)
from training_system.features.exercises.application.errors import (
    ExerciseCatalogNotFound,
)
from training_system.features.exercises.domain import (
    CatalogExercise,
    ExerciseCatalog,
    ExerciseCatalogRepository,
)


class ExerciseCatalogService:
    def __init__(self, repository: ExerciseCatalogRepository) -> None:
        self._repository = repository

    async def get_catalog(self, *, user_id: UUID) -> ExerciseCatalog:
        catalog = await self._repository.find_by_user(user_id=user_id)
        if catalog is None:
            raise ExerciseCatalogNotFound(user_id)
        return catalog

    async def seed_defaults(self, *, user_id: UUID) -> ExerciseCatalog:
        catalog = build_default_catalog(user_id=user_id)
        return await self._repository.replace(catalog=catalog)

    async def reset_to_defaults(self, *, user_id: UUID) -> ExerciseCatalog:
        return await self.seed_defaults(user_id=user_id)

    async def patch_catalog(
        self,
        *,
        user_id: UUID,
        category_updates: list[CategoryUpdate],
        exercise_upserts: list[ExerciseUpsert],
    ) -> ExerciseCatalog:
        catalog = await self.get_catalog(user_id=user_id)

        categories_by_name = {category.category: category for category in catalog.categories}
        for update in category_updates:
            current = categories_by_name.get(update.category)
            if current is None:
                continue
            categories_by_name[update.category] = type(current)(
                category=current.category,
                rest_seconds=update.rest_seconds
                if update.rest_seconds is not None
                else current.rest_seconds,
                default_sets=update.default_sets
                if update.default_sets is not None
                else current.default_sets,
                default_reps=update.default_reps
                if update.default_reps is not None
                else current.default_reps,
                default_target_rpe=update.default_target_rpe
                if update.default_target_rpe is not None
                else current.default_target_rpe,
            )
        catalog.categories = list(categories_by_name.values())

        exercises_by_id = {exercise.id: exercise for exercise in catalog.exercises}
        next_positions = {
            category: len(catalog.exercises_in(category))
            for category in {exercise.category for exercise in catalog.exercises}
        }
        for upsert in exercise_upserts:
            if upsert.id is not None and not upsert.name.strip():
                exercises_by_id.pop(upsert.id, None)
                continue
            if upsert.id is not None and upsert.id in exercises_by_id:
                existing = exercises_by_id[upsert.id]
                exercises_by_id[upsert.id] = CatalogExercise(
                    id=existing.id,
                    category=upsert.category,
                    name=upsert.name,
                    position=existing.position,
                    max_factor=upsert.max_factor,
                )
                continue
            if not upsert.name.strip():
                continue
            position = next_positions.get(upsert.category, 0)
            new_id = uuid4()
            exercises_by_id[new_id] = CatalogExercise(
                id=new_id,
                category=upsert.category,
                name=upsert.name,
                position=position,
                max_factor=upsert.max_factor,
            )
            next_positions[upsert.category] = position + 1

        catalog.exercises = list(exercises_by_id.values())
        return await self._repository.replace(catalog=catalog)

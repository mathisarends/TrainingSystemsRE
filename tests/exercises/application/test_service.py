from uuid import uuid4

import pytest

from training_systems.features.exercises.application.commands import (
    CategoryUpdate,
    ExerciseUpsert,
)
from training_systems.features.exercises.application.errors import (
    ExerciseCatalogNotFound,
)
from training_systems.features.exercises.application.service import (
    ExerciseCatalogService,
)
from training_systems.features.exercises.domain import ExerciseCategory


async def test_get_catalog_raises_when_none_has_been_seeded(
    catalog_service: ExerciseCatalogService,
) -> None:
    with pytest.raises(ExerciseCatalogNotFound):
        await catalog_service.get_catalog(user_id=uuid4())


async def test_seed_defaults_persists_a_full_default_catalog(
    catalog_service: ExerciseCatalogService,
) -> None:
    user_id = uuid4()

    catalog = await catalog_service.seed_defaults(user_id=user_id)

    assert catalog.user_id == user_id
    assert len(catalog.exercises) > 0
    assert await catalog_service.get_catalog(user_id=user_id) is catalog


async def test_patch_catalog_updates_only_the_given_category_fields(
    catalog_service: ExerciseCatalogService,
) -> None:
    user_id = uuid4()
    await catalog_service.seed_defaults(user_id=user_id)

    patched = await catalog_service.patch_catalog(
        user_id=user_id,
        category_updates=[
            CategoryUpdate(category=ExerciseCategory.SQUAT, rest_seconds=300)
        ],
        exercise_upserts=[],
    )

    squat_defaults = next(
        category
        for category in patched.categories
        if category.category == ExerciseCategory.SQUAT
    )
    assert squat_defaults.rest_seconds == 300
    assert squat_defaults.default_sets == 3  # unspecified field kept its default


async def test_patch_catalog_ignores_updates_for_unknown_categories(
    catalog_service: ExerciseCatalogService,
) -> None:
    user_id = uuid4()
    before = await catalog_service.seed_defaults(user_id=user_id)
    before.categories = [
        category
        for category in before.categories
        if category.category != ExerciseCategory.SQUAT
    ]

    patched = await catalog_service.patch_catalog(
        user_id=user_id,
        category_updates=[CategoryUpdate(category=ExerciseCategory.SQUAT)],
        exercise_upserts=[],
    )

    assert len(patched.categories) == len(before.categories)


async def test_patch_catalog_adds_a_new_exercise_at_the_next_position(
    catalog_service: ExerciseCatalogService,
) -> None:
    user_id = uuid4()
    await catalog_service.seed_defaults(user_id=user_id)

    patched = await catalog_service.patch_catalog(
        user_id=user_id,
        category_updates=[],
        exercise_upserts=[
            ExerciseUpsert(category=ExerciseCategory.SQUAT, name="Zercher Squat")
        ],
    )

    squats = patched.exercises_in(ExerciseCategory.SQUAT)
    assert squats[-1].name == "Zercher Squat"
    assert squats[-1].position == len(squats) - 1


async def test_patch_catalog_updates_an_existing_exercise_by_id(
    catalog_service: ExerciseCatalogService,
) -> None:
    user_id = uuid4()
    seeded = await catalog_service.seed_defaults(user_id=user_id)
    existing = seeded.exercises_in(ExerciseCategory.SQUAT)[0]

    patched = await catalog_service.patch_catalog(
        user_id=user_id,
        category_updates=[],
        exercise_upserts=[
            ExerciseUpsert(
                id=existing.id, category=ExerciseCategory.SQUAT, name="Renamed Squat"
            )
        ],
    )

    updated = next(
        exercise for exercise in patched.exercises if exercise.id == existing.id
    )
    assert updated.name == "Renamed Squat"
    assert updated.position == existing.position


async def test_patch_catalog_deletes_an_exercise_when_the_name_is_blank(
    catalog_service: ExerciseCatalogService,
) -> None:
    user_id = uuid4()
    seeded = await catalog_service.seed_defaults(user_id=user_id)
    existing = seeded.exercises_in(ExerciseCategory.SQUAT)[0]

    patched = await catalog_service.patch_catalog(
        user_id=user_id,
        category_updates=[],
        exercise_upserts=[
            ExerciseUpsert(id=existing.id, category=ExerciseCategory.SQUAT, name="  ")
        ],
    )

    assert existing.id not in {exercise.id for exercise in patched.exercises}


async def test_patch_catalog_ignores_a_new_exercise_with_a_blank_name(
    catalog_service: ExerciseCatalogService,
) -> None:
    user_id = uuid4()
    before = await catalog_service.seed_defaults(user_id=user_id)

    patched = await catalog_service.patch_catalog(
        user_id=user_id,
        category_updates=[],
        exercise_upserts=[
            ExerciseUpsert(category=ExerciseCategory.SQUAT, name="   ")
        ],
    )

    assert len(patched.exercises) == len(before.exercises)

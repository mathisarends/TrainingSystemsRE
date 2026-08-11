from training_systems.features.exercises.infrastructure.provider import (
    ExerciseCatalogProvider,
)
from training_systems.features.exercises.presentation.errors import (
    register_exception_handlers,
)
from training_systems.features.exercises.presentation.router import router
from training_systems.presentation.feature import Feature

feature = Feature(
    name="exercises",
    routers=(router,),
    providers=(ExerciseCatalogProvider,),
    register_exception_handlers=register_exception_handlers,
)

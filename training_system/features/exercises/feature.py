from training_system.features.exercises.infrastructure.provider import (
    ExerciseCatalogProvider,
)
from training_system.features.exercises.presentation.errors import (
    register_exception_handlers,
)
from training_system.features.exercises.presentation.router import router
from training_system.presentation.feature import Feature

feature = Feature(
    name="exercises",
    routers=(router,),
    providers=(ExerciseCatalogProvider,),
    register_exception_handlers=register_exception_handlers,
)

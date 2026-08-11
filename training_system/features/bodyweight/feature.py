from training_system.features.bodyweight.infrastructure.provider import (
    BodyWeightProvider,
)
from training_system.features.bodyweight.presentation.router import router
from training_system.presentation.feature import Feature

feature = Feature(
    name="bodyweight",
    routers=(router,),
    providers=(BodyWeightProvider,),
)

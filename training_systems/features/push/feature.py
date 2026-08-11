from training_systems.features.push.infrastructure.provider import PushProvider
from training_systems.features.push.presentation.router import router
from training_systems.presentation.feature import Feature

feature = Feature(
    name="push",
    routers=(router,),
    providers=(PushProvider,),
)

from training_system.features.push.infrastructure.provider import PushProvider
from training_system.features.push.presentation.router import router
from training_system.presentation.feature import Feature

feature = Feature(
    name="push",
    routers=(router,),
    providers=(PushProvider,),
)

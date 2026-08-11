from training_systems.features.timer.infrastructure.provider import TimerProvider
from training_systems.features.timer.presentation.router import router
from training_systems.presentation.feature import Feature

feature = Feature(
    name="timer",
    routers=(router,),
    providers=(TimerProvider,),
)

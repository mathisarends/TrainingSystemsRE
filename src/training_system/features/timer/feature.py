from training_system.features.timer.infrastructure.provider import TimerProvider
from training_system.features.timer.presentation.router import router
from training_system.presentation.feature import Feature

feature = Feature(
    name="timer",
    routers=(router,),
    providers=(TimerProvider,),
)

from training_systems.features.notifications.infrastructure.provider import (
    NotificationsProvider,
)
from training_systems.features.notifications.presentation.router import router
from training_systems.presentation.feature import Feature

feature = Feature(
    name="notifications",
    routers=(router,),
    providers=(NotificationsProvider,),
)

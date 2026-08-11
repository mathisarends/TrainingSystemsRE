from training_system.features.notifications.infrastructure.provider import (
    NotificationsProvider,
)
from training_system.features.notifications.presentation.router import router
from training_system.presentation.feature import Feature

feature = Feature(
    name="notifications",
    routers=(router,),
    providers=(NotificationsProvider,),
)

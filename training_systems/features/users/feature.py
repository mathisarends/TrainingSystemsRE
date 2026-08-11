from training_systems.features.users.infrastructure.provider import UserProvider
from training_systems.features.users.presentation.errors import (
    register_exception_handlers,
)
from training_systems.features.users.presentation.router import router
from training_systems.presentation.feature import Feature

feature = Feature(
    name="users",
    routers=(router,),
    providers=(UserProvider,),
    register_exception_handlers=register_exception_handlers,
)

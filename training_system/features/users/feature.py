from training_system.features.users.infrastructure.provider import UserProvider
from training_system.features.users.presentation.errors import (
    register_exception_handlers,
)
from training_system.features.users.presentation.router import router
from training_system.presentation.feature import Feature

feature = Feature(
    name="users",
    routers=(router,),
    providers=(UserProvider,),
    register_exception_handlers=register_exception_handlers,
)

from training_system.features.authentication.infrastructure.provider import (
    AuthenticationProvider,
)
from training_system.features.authentication.presentation.exception_handlers import (
    register_exception_handlers,
)
from training_system.features.authentication.presentation.router import router
from training_system.presentation.feature import Feature

feature = Feature(
    name="authentication",
    routers=(router,),
    providers=(AuthenticationProvider,),
    register_exception_handlers=register_exception_handlers,
)

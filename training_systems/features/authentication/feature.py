from training_systems.features.authentication.infrastructure.provider import (
    AuthenticationProvider,
)
from training_systems.features.authentication.presentation.exception_handlers import (
    register_exception_handlers,
)
from training_systems.features.authentication.presentation.router import router
from training_systems.presentation.feature import Feature

feature = Feature(
    name="authentication",
    routers=(router,),
    providers=(AuthenticationProvider,),
    register_exception_handlers=register_exception_handlers,
)

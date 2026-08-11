from training_system.authentication.infrastructure.provider import (
    AuthenticationProvider,
)
from training_system.authentication.presentation.errors import (
    register_exception_handlers,
)
from training_system.authentication.presentation.router import router
from training_system.presentation.feature import Feature

feature = Feature(
    name="authentication",
    routers=(router,),
    providers=(AuthenticationProvider,),
    register_exception_handlers=register_exception_handlers,
)

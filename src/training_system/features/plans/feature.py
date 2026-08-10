from training_system.features.plans.infrastructure.provider import PlanProvider
from training_system.features.plans.presentation.errors import (
    register_exception_handlers,
)
from training_system.features.plans.presentation.router import router
from training_system.presentation.feature import Feature

feature = Feature(
    name="plans",
    routers=(router,),
    providers=(PlanProvider,),
    register_exception_handlers=register_exception_handlers,
)

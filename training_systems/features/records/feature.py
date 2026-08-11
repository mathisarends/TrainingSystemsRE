from training_systems.features.records.infrastructure.provider import RecordsProvider
from training_systems.features.records.presentation.errors import (
    register_exception_handlers,
)
from training_systems.features.records.presentation.router import router
from training_systems.presentation.feature import Feature

feature = Feature(
    name="records",
    routers=(router,),
    providers=(RecordsProvider,),
    register_exception_handlers=register_exception_handlers,
)

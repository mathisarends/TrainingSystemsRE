from training_system.features.records.infrastructure.provider import RecordsProvider
from training_system.features.records.presentation.errors import (
    register_exception_handlers,
)
from training_system.features.records.presentation.router import router
from training_system.presentation.feature import Feature

feature = Feature(
    name="records",
    routers=(router,),
    providers=(RecordsProvider,),
    register_exception_handlers=register_exception_handlers,
)

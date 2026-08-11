from dishka import AsyncContainer, make_async_container
from fastapi import FastAPI

from training_system.features.authentication.feature import (
    feature as authentication_feature,
)
from training_system.features.exercises.feature import feature as exercises_feature
from training_system.features.notifications.feature import (
    feature as notifications_feature,
)
from training_system.features.plans.feature import feature as plans_feature
from training_system.features.push.feature import feature as push_feature
from training_system.features.records.feature import feature as records_feature
from training_system.features.timer.feature import feature as timer_feature
from training_system.features.users.feature import feature as users_feature
from training_system.infrastructure.database.orm import register_models
from training_system.infrastructure.database.provider import DatabaseProvider
from training_system.infrastructure.scheduler.provider import SchedulerProvider
from training_system.presentation.health import router as health_router

register_models()

FEATURES = (
    authentication_feature,
    users_feature,
    exercises_feature,
    plans_feature,
    records_feature,
    push_feature,
    notifications_feature,
    timer_feature,
)

API_PREFIX = "/api/v1"


def create_container() -> AsyncContainer:
    providers = [DatabaseProvider(), SchedulerProvider()]
    providers.extend(
        provider() for feature in FEATURES for provider in feature.providers
    )
    return make_async_container(*providers)


def register_features(app: FastAPI) -> None:
    app.include_router(health_router)
    for feature in FEATURES:
        for router in feature.routers:
            app.include_router(router, prefix=API_PREFIX)
        if feature.register_exception_handlers is not None:
            feature.register_exception_handlers(app)

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

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
from training_system.settings import AppSettings

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


def _use_function_name_as_operation_id(route: APIRoute) -> str:
    return route.name


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


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    yield
    await app.state.dishka_container.close()


def create_app() -> FastAPI:
    settings = AppSettings()
    app = FastAPI(
        title="TrainingSystems",
        lifespan=lifespan,
        generate_unique_id_function=_use_function_name_as_operation_id,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_features(app)

    container = create_container()
    setup_dishka(container, app)

    return app


app = create_app()

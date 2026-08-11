from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute

from training_system.settings import AppSettings
from training_system.wiring import create_container, register_features


def _use_function_name_as_operation_id(route: APIRoute) -> str:
    return route.name


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

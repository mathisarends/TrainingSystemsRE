from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from training_systems.features.exercises.application import ExerciseCatalogNotFound
from training_systems.presentation.schema import ErrorResponse


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ExerciseCatalogNotFound)
    async def catalog_not_found(
        _: Request, __: ExerciseCatalogNotFound
    ) -> JSONResponse:
        response = ErrorResponse(detail="No exercises found")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=response.model_dump(mode="json"),
        )

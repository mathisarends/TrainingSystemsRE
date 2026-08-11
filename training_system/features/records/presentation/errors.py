from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from training_system.features.records.application import RecordNotFound
from training_system.presentation.schema import ErrorResponse


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RecordNotFound)
    async def record_not_found(_: Request, __: RecordNotFound) -> JSONResponse:
        response = ErrorResponse(detail="No record found for this exercise")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=response.model_dump(mode="json"),
        )

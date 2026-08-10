from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from training_system.features.users.application import UserNotFound
from training_system.presentation.schema import ErrorResponse


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(UserNotFound)
    async def user_not_found(_: Request, __: UserNotFound) -> JSONResponse:
        response = ErrorResponse(detail="User was not found")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=response.model_dump(mode="json"),
        )

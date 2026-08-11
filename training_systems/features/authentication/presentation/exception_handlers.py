from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from training_systems.features.authentication.application import (
    EmailAlreadyRegisteredException,
    InvalidCredentialsException,
)
from training_systems.features.authentication.presentation.dependencies import (
    AuthenticationRequired,
)
from training_systems.presentation.schema import ErrorResponse


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AuthenticationRequired)
    async def authentication_required(
        _: Request, __: AuthenticationRequired
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ErrorResponse(detail="Authentication required").model_dump(
                mode="json"
            ),
        )

    @app.exception_handler(InvalidCredentialsException)
    async def invalid_credentials(
        _: Request, __: InvalidCredentialsException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ErrorResponse(detail="Invalid credentials").model_dump(
                mode="json"
            ),
        )

    @app.exception_handler(EmailAlreadyRegisteredException)
    async def email_already_registered(
        _: Request, __: EmailAlreadyRegisteredException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(detail="Email already registered").model_dump(
                mode="json"
            ),
        )

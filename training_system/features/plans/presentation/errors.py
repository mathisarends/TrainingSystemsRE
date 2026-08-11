from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from training_system.features.plans.application import InvalidPlanPosition, PlanNotFound
from training_system.presentation.schema import ErrorResponse


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(PlanNotFound)
    async def plan_not_found(_: Request, __: PlanNotFound) -> JSONResponse:
        response = ErrorResponse(detail="Plan not found")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=response.model_dump(mode="json"),
        )

    @app.exception_handler(InvalidPlanPosition)
    async def invalid_plan_position(
        _: Request, __: InvalidPlanPosition
    ) -> JSONResponse:
        response = ErrorResponse(detail="Invalid week or day position")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=response.model_dump(mode="json"),
        )

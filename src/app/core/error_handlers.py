from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.errors import AppError, ConflictError, NotFoundError

STATUS_BY_ERROR: dict[type[AppError], HTTPStatus] = {
    NotFoundError: HTTPStatus.NOT_FOUND,
    ConflictError: HTTPStatus.CONFLICT,
}


def problem_response(status: HTTPStatus, detail: str, instance: str) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        media_type="application/problem+json",
        content={
            "type": "about:blank",
            "title": status.phrase,
            "status": status.value,
            "detail": detail,
            "instance": instance,
        },
    )


async def handle_app_error(request: Request, error: Exception) -> JSONResponse:
    status = next(
        (code for kind, code in STATUS_BY_ERROR.items() if isinstance(error, kind)),
        HTTPStatus.BAD_REQUEST,
    )
    return problem_response(status, str(error), request.url.path)


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, handle_app_error)

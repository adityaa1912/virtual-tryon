from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.api.middleware import REQUEST_ID_HEADER
from app.core.exceptions import StorageError, UploadValidationError
from app.schemas.common import ErrorDetail, ErrorModel, ErrorResponse


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "")


def _error_response(
    status_code: int,
    code: str,
    message: str,
    request_id: str,
    details: list[ErrorDetail] | None = None,
) -> JSONResponse:
    body = ErrorResponse(
        error=ErrorModel(
            code=code,
            message=message,
            request_id=request_id,
            details=details or [],
        )
    )
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(),
        headers={REQUEST_ID_HEADER: request_id},
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(UploadValidationError)
    async def _on_upload_validation_error(
        request: Request, exc: UploadValidationError
    ) -> JSONResponse:
        return _error_response(
            exc.status_code, exc.code, exc.detail, _request_id(request)
        )

    @app.exception_handler(StorageError)
    async def _on_storage_error(request: Request, exc: StorageError) -> JSONResponse:
        return _error_response(
            exc.status_code, exc.code, exc.detail, _request_id(request)
        )

    @app.exception_handler(RequestValidationError)
    async def _on_request_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details = [
            ErrorDetail(
                field=".".join(str(part) for part in error["loc"]),
                issue=error["msg"],
            )
            for error in exc.errors()
        ]
        return _error_response(
            422, "VALIDATION_ERROR", "Request validation failed.", _request_id(request), details
        )

    @app.exception_handler(HTTPException)
    async def _on_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
        message = exc.detail if isinstance(exc.detail, str) else "HTTP error."
        return _error_response(
            exc.status_code, "HTTP_ERROR", message, _request_id(request)
        )

    @app.exception_handler(Exception)
    async def _on_unhandled_error(request: Request, exc: Exception) -> JSONResponse:
        return _error_response(
            500, "INTERNAL_ERROR", "An unexpected error occurred.", _request_id(request)
        )

import uuid
from collections.abc import Callable

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


def _normalize_detail(detail: object) -> tuple[str, object | None]:
    if isinstance(detail, str):
        return detail, None
    if isinstance(detail, dict):
        if "message" in detail and isinstance(detail["message"], str):
            return detail["message"], detail
        return "Request failed.", detail
    return "Request failed.", None


def _error_response(
    *,
    status_code: int,
    code: str,
    message: str,
    request_id: str,
    details: object | None = None,
) -> JSONResponse:
    payload = {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
        }
    }
    if details is not None:
        payload["error"]["details"] = details

    return JSONResponse(status_code=status_code, content=payload)


def build_http_exception_handler() -> Callable[[Request, HTTPException], JSONResponse]:
    async def handler(request: Request, exc: HTTPException) -> JSONResponse:
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        message, details = _normalize_detail(exc.detail)
        code = "HTTP_ERROR"
        if exc.status_code == 401:
            code = "UNAUTHORIZED"
        elif exc.status_code == 403:
            code = "FORBIDDEN"
        elif exc.status_code == 404:
            code = "NOT_FOUND"
        elif exc.status_code == 422:
            code = "VALIDATION_ERROR"
        elif exc.status_code == 429:
            code = "RATE_LIMITED"
        elif 500 <= exc.status_code < 600:
            code = "UPSTREAM_ERROR"

        response = _error_response(
            status_code=exc.status_code,
            code=code,
            message=message,
            request_id=request_id,
            details=details,
        )

        if exc.headers:
            for key, value in exc.headers.items():
                response.headers[key] = value
        response.headers["x-request-id"] = request_id
        return response

    return handler


def build_unhandled_exception_handler() -> Callable[[Request, Exception], JSONResponse]:
    async def handler(request: Request, _: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        response = _error_response(
            status_code=500,
            code="INTERNAL_ERROR",
            message="An internal error occurred.",
            request_id=request_id,
        )
        response.headers["x-request-id"] = request_id
        return response

    return handler


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["x-request-id"] = request_id
        return response

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from inference_control_plane.api import router as api_router
from inference_control_plane.core.config import get_settings
from inference_control_plane.core.errors import (
    RequestIdMiddleware,
    build_http_exception_handler,
    build_unhandled_exception_handler,
    build_validation_exception_handler,
)
from inference_control_plane.db.redis import close_redis, init_redis
from inference_control_plane.db.seed import seed_default_api_key
from inference_control_plane.db.session import (
    dispose_engine,
    get_engine,
    get_session_factory,
    init_engine,
)
from inference_control_plane.observability.logging import configure_logging
from inference_control_plane.observability.tracing import configure_tracing, shutdown_tracing
from inference_control_plane.services.llm_client import close_http_client, init_http_client


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()

    configure_logging(settings.log_level)
    init_engine(settings)
    await seed_default_api_key(get_session_factory(), settings)

    init_redis(settings)
    configure_tracing(app, settings, get_engine())
    init_http_client(settings)

    try:
        yield
    finally:
        await close_http_client()
        await close_redis()
        await dispose_engine()
        shutdown_tracing()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["x-request-id"],
    )
    app.add_middleware(RequestIdMiddleware)
    app.add_exception_handler(RequestValidationError, build_validation_exception_handler())
    app.add_exception_handler(HTTPException, build_http_exception_handler())
    app.add_exception_handler(Exception, build_unhandled_exception_handler())

    # Keep legacy paths for compatibility while exposing a stable versioned API.
    app.include_router(api_router, prefix="/api/v1")
    app.include_router(api_router)
    return app


app = create_app()

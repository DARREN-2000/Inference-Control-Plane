from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import router as api_router
from app.core.config import get_settings
from app.db.redis import close_redis, init_redis
from app.db.seed import seed_default_api_key
from app.db.session import dispose_engine, get_engine, get_session_factory, init_db, init_engine
from app.observability.logging import configure_logging
from app.observability.tracing import configure_tracing, shutdown_tracing


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    configure_logging(settings.log_level)
    init_engine(settings)
    await init_db()
    await seed_default_api_key(get_session_factory(), settings)

    init_redis(settings)
    configure_tracing(app, settings, get_engine())

    try:
        yield
    finally:
        await close_redis()
        await dispose_engine()
        shutdown_tracing()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
    )
    app.include_router(api_router)
    return app


app = create_app()

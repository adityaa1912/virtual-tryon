from fastapi import FastAPI

from app.api.errors import register_exception_handlers
from app.api.middleware import RequestIDMiddleware
from app.api.routes import health, results, tryon, uploads, videos
from app.core.config import Settings, get_settings


def create_app() -> FastAPI:
    settings: Settings = get_settings()
    application = FastAPI(title=settings.service_name, version=settings.app_version)
    application.add_middleware(RequestIDMiddleware)
    application.include_router(health.router)
    application.include_router(uploads.router, prefix="/api/v1")
    application.include_router(tryon.router, prefix="/api/v1")
    application.include_router(videos.router, prefix="/api/v1")
    application.include_router(results.router, prefix="/api/v1")
    register_exception_handlers(application)
    return application


app = create_app()

"""FastAPI application bootstrap for STLWeaver."""

from fastapi import FastAPI

from app.api.routes import api_router
from app.core.config import get_settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )
    application.include_router(api_router)
    return application


app = create_app()


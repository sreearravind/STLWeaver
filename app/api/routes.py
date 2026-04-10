"""API routes for the STLWeaver service."""

from fastapi import APIRouter, status

from app.core.config import get_settings
from app.models.schemas import GenerateRequest, GenerateResponse, HealthResponse, ProvidersResponse
from app.services.orchestrator import GenerationOrchestrator

api_router = APIRouter()
generation_router = APIRouter(prefix="/generate", tags=["generation"])
settings = get_settings()
orchestrator = GenerationOrchestrator()


@api_router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """Return a lightweight health response for service checks."""
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=settings.app_version,
    )


@api_router.get("/providers", response_model=ProvidersResponse, tags=["providers"])
async def list_providers() -> ProvidersResponse:
    """Return the configured placeholder provider list."""
    return ProvidersResponse(providers=orchestrator.get_supported_providers())


@generation_router.post("", response_model=GenerateResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_stl(request: GenerateRequest) -> GenerateResponse:
    """Accept a generation request and return a structured placeholder response."""
    return await orchestrator.submit_generation(request)


api_router.include_router(generation_router)

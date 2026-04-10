"""API routes for the STLWeaver service."""

from fastapi import APIRouter, HTTPException, status

from app.core.config import get_settings
from app.models.schemas import (
    ErrorResponse,
    GenerateRequest,
    GenerateResponse,
    HealthResponse,
    JobStatusResponse,
    ProvidersResponse,
)
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


@api_router.get(
    "/status/{job_id}",
    response_model=JobStatusResponse,
    responses={404: {"model": ErrorResponse}},
    tags=["generation"],
)
async def get_status(job_id: str) -> JobStatusResponse:
    """Return placeholder job status for a submitted generation request."""
    job_status = orchestrator.get_job_status(job_id)
    if job_status is None:
        raise HTTPException(status_code=404, detail=f"Unknown job_id: {job_id}")
    return job_status


@generation_router.post(
    "",
    response_model=GenerateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={400: {"model": ErrorResponse}},
)
async def generate_stl(request: GenerateRequest) -> GenerateResponse:
    """Accept a generation request and return a structured placeholder response."""
    try:
        return await orchestrator.submit_generation(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


api_router.include_router(generation_router)

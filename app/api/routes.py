"""API routes for the STLWeaver service."""

from uuid import uuid4

from fastapi import APIRouter, status

from app.models.schemas import GenerateRequest, GenerateResponse, HealthResponse

api_router = APIRouter()
generation_router = APIRouter(prefix="/generate", tags=["generation"])


@api_router.get("/health", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """Return a lightweight health response for service checks."""
    return HealthResponse(status="ok")


@generation_router.post("", response_model=GenerateResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_stl(request: GenerateRequest) -> GenerateResponse:
    """Accept a generation request and return a placeholder queued response."""
    del request
    return GenerateResponse(
        job_id=str(uuid4()),
        status="pending",
        estimated_time=0,
        message="Generation pipeline scaffold initialized; implementation will be added in later rounds.",
    )


api_router.include_router(generation_router)


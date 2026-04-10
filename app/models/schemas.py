"""Request and response schemas for the STLWeaver API."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health-check response payload."""

    status: str = Field(..., description="Service health status")


class GenerateRequest(BaseModel):
    """Minimal generation request schema."""

    prompt: str = Field(..., description="Natural language description of a 3D model")
    llm_provider: str | None = Field(default="openai", description="LLM provider identifier")
    llm_model: str | None = Field(default=None, description="Specific model name")
    analyze_supports: bool = Field(default=True, description="Whether to run support analysis")


class GenerateResponse(BaseModel):
    """Placeholder generation response schema."""

    job_id: str
    status: str
    estimated_time: int
    message: str


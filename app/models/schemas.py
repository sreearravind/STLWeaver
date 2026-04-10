"""Request and response schemas for the STLWeaver API."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health-check response payload."""

    status: str = Field(..., description="Service health status")
    app_name: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")


class ProviderInfo(BaseModel):
    """Minimal provider metadata."""

    name: str
    models: list[str] = Field(default_factory=list)
    available: bool = True


class ProvidersResponse(BaseModel):
    """Response payload for supported LLM providers."""

    providers: list[ProviderInfo]


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
    message: str
    llm_provider: str
    llm_model: str | None = None
    code_generated: bool = False
    security_passed: bool = False
    supports_analyzed: bool = False
    support_recommendation: str | None = None
    estimated_time: int = 0

"""Request and response schemas for the STLWeaver API."""

from pydantic import BaseModel, Field, field_validator


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


class PromptSummary(BaseModel):
    """Compact prompt metadata for placeholder responses."""

    text: str
    length: int
    truncated: bool = False


class PlaceholderCodeSummary(BaseModel):
    """Minimal code-preview metadata."""

    generated: bool = False
    snippet: str | None = None
    message: str


class PlaceholderGeometrySummary(BaseModel):
    """Minimal geometry-preview metadata."""

    available: bool = False
    summary: str


class PlaceholderSupportSummary(BaseModel):
    """Minimal support-analysis metadata."""

    analyzed: bool = False
    recommended_type: str | None = None
    summary: str


class GenerateRequest(BaseModel):
    """Minimal generation request schema."""

    prompt: str = Field(..., description="Natural language description of a 3D model")
    llm_provider: str | None = Field(default="openai", description="LLM provider identifier")
    llm_model: str | None = Field(default=None, description="Specific model name")
    analyze_supports: bool = Field(default=True, description="Whether to run support analysis")

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, value: str) -> str:
        """Reject empty or whitespace-only prompts."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Prompt must not be empty.")
        return cleaned

    @field_validator("llm_provider")
    @classmethod
    def normalize_provider(cls, value: str | None) -> str | None:
        """Normalize provider identifiers for consistent comparison."""
        if value is None:
            return value
        cleaned = value.strip().lower()
        return cleaned or None


class GenerateResponse(BaseModel):
    """Placeholder generation response schema."""

    job_id: str
    status: str
    stage: str
    message: str
    llm_provider: str
    llm_model: str | None = None
    prompt_summary: PromptSummary
    created_at: str
    code_generated: bool = False
    security_passed: bool = False
    supports_analyzed: bool = False
    support_recommendation: str | None = None
    estimated_time: int = 0


class JobStatusResponse(BaseModel):
    """Placeholder job status response schema."""

    job_id: str
    status: str
    stage: str
    message: str
    llm_provider: str
    llm_model: str | None = None
    prompt_summary: PromptSummary
    created_at: str
    supports_analyzed: bool = False
    support_recommendation: str | None = None


class ErrorResponse(BaseModel):
    """Basic API error payload."""

    detail: str


class PreviewResponse(BaseModel):
    """Placeholder preview response schema."""

    status: str
    stage: str
    message: str
    llm_provider: str
    llm_model: str | None = None
    prompt_summary: PromptSummary
    code_preview: PlaceholderCodeSummary
    geometry_preview: PlaceholderGeometrySummary
    support_preview: PlaceholderSupportSummary

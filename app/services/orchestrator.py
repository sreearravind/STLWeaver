"""Lightweight orchestration flow for placeholder STL generation."""

from datetime import UTC, datetime
from uuid import uuid4

from app.models.schemas import (
    GenerateRequest,
    GenerateResponse,
    JobStatusResponse,
    PlaceholderCodeSummary,
    PlaceholderGeometrySummary,
    PlaceholderSupportSummary,
    PreviewResponse,
    PromptSummary,
    ProviderInfo,
)
from app.services.geometry_engine import GeometryProcessor, SupportStructureAnalyzer
from app.services.llm_manager import LLMManager
from app.services.security import SecurityValidator


class GenerationOrchestrator:
    """Coordinate the placeholder prompt-to-STL control flow."""

    def __init__(
        self,
        llm_manager: LLMManager | None = None,
        security_validator: SecurityValidator | None = None,
        geometry_processor: GeometryProcessor | None = None,
        support_analyzer: SupportStructureAnalyzer | None = None,
    ) -> None:
        self.llm_manager = llm_manager or LLMManager()
        self.security_validator = security_validator or SecurityValidator()
        self.geometry_processor = geometry_processor or GeometryProcessor()
        self.support_analyzer = support_analyzer or SupportStructureAnalyzer(self.geometry_processor)
        self.jobs: dict[str, JobStatusResponse] = {}

    def get_supported_providers(self) -> list[ProviderInfo]:
        """Expose provider metadata for the API layer."""
        providers = self.llm_manager.get_supported_providers()
        return [
            ProviderInfo(
                name=provider["name"],
                models=provider["models"],
                available=provider["available"],
            )
            for provider in providers
        ]

    def get_supported_provider_names(self) -> list[str]:
        """Return the supported provider names in a stable order."""
        return [provider.name for provider in self.get_supported_providers()]

    def _summarize_prompt(self, prompt: str, max_length: int = 80) -> PromptSummary:
        """Return a compact prompt summary for API payloads."""
        truncated = len(prompt) > max_length
        text = prompt[:max_length].rstrip()
        if truncated:
            text = f"{text}..."
        return PromptSummary(text=text, length=len(prompt), truncated=truncated)

    def _timestamp(self) -> str:
        """Return an ISO timestamp for placeholder job metadata."""
        return datetime.now(UTC).isoformat()

    async def submit_generation(self, request: GenerateRequest) -> GenerateResponse:
        """Run a shallow placeholder orchestration flow."""
        if not self.llm_manager.is_supported_provider(request.llm_provider):
            supported = ", ".join(self.get_supported_provider_names())
            raise ValueError(
                f"Unsupported provider '{request.llm_provider}'. Supported providers: {supported}."
            )

        llm_result = await self.llm_manager.generate_code(
            prompt=request.prompt,
            provider=request.llm_provider,
            model=request.llm_model,
        )
        validation = self.security_validator.validate_code(llm_result["code"])
        geometry = self.geometry_processor.create_geometry(llm_result["code"])

        support_recommendation = None
        if request.analyze_supports:
            support_result = self.support_analyzer.analyze(geometry)
            support_recommendation = support_result.recommended_type

        job_id = str(uuid4())
        created_at = self._timestamp()
        prompt_summary = self._summarize_prompt(request.prompt)
        response = GenerateResponse(
            job_id=job_id,
            status="accepted",
            stage="queued",
            message="Generation request accepted. The current pipeline is a connected placeholder scaffold.",
            llm_provider=llm_result["provider"],
            llm_model=llm_result["model_used"],
            prompt_summary=prompt_summary,
            created_at=created_at,
            code_generated=bool(llm_result["code"]),
            security_passed=validation["is_safe"],
            supports_analyzed=request.analyze_supports,
            support_recommendation=support_recommendation,
            estimated_time=0,
        )
        self.jobs[job_id] = JobStatusResponse(
            job_id=job_id,
            status="pending",
            stage="validated",
            message="Placeholder job recorded in memory. Background processing is not implemented yet.",
            llm_provider=response.llm_provider,
            llm_model=response.llm_model,
            prompt_summary=prompt_summary,
            created_at=created_at,
            supports_analyzed=response.supports_analyzed,
            support_recommendation=response.support_recommendation,
        )
        return response

    def get_job_status(self, job_id: str) -> JobStatusResponse | None:
        """Return placeholder job status for a previously submitted request."""
        return self.jobs.get(job_id)

    async def preview_generation(self, request: GenerateRequest) -> PreviewResponse:
        """Return a simulated preview response without creating a stored job."""
        if not self.llm_manager.is_supported_provider(request.llm_provider):
            supported = ", ".join(self.get_supported_provider_names())
            raise ValueError(
                f"Unsupported provider '{request.llm_provider}'. Supported providers: {supported}."
            )

        llm_result = await self.llm_manager.generate_code(
            prompt=request.prompt,
            provider=request.llm_provider,
            model=request.llm_model,
        )
        geometry = self.geometry_processor.create_geometry(llm_result["code"])
        support_result = self.support_analyzer.analyze(geometry) if request.analyze_supports else None

        snippet = None
        if llm_result["code"]:
            snippet = "\n".join(llm_result["code"].splitlines()[:4])

        return PreviewResponse(
            status="ok",
            stage="preview_ready",
            message="Preview is simulated from placeholder service outputs. No real CAD or STL generation occurred.",
            llm_provider=llm_result["provider"],
            llm_model=llm_result["model_used"],
            prompt_summary=self._summarize_prompt(request.prompt),
            code_preview=PlaceholderCodeSummary(
                generated=bool(llm_result["code"]),
                snippet=snippet,
                message=llm_result["message"],
            ),
            geometry_preview=PlaceholderGeometrySummary(
                available=False,
                summary=geometry["message"],
            ),
            support_preview=PlaceholderSupportSummary(
                analyzed=request.analyze_supports,
                recommended_type=support_result.recommended_type if support_result else None,
                summary=(
                    support_result.notes[0]
                    if support_result and support_result.notes
                    else "Support analysis was skipped for this preview."
                ),
            ),
        )

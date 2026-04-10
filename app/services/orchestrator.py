"""Lightweight orchestration flow for placeholder STL generation."""

from uuid import uuid4

from app.models.schemas import GenerateRequest, GenerateResponse, ProviderInfo
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

    async def submit_generation(self, request: GenerateRequest) -> GenerateResponse:
        """Run a shallow placeholder orchestration flow."""
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

        return GenerateResponse(
            job_id=str(uuid4()),
            status="accepted",
            message="Generation request accepted. The current pipeline is a connected placeholder scaffold.",
            llm_provider=llm_result["provider"],
            llm_model=llm_result["model_used"],
            code_generated=bool(llm_result["code"]),
            security_passed=validation["is_safe"],
            supports_analyzed=request.analyze_supports,
            support_recommendation=support_recommendation,
            estimated_time=0,
        )


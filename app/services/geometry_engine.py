"""Minimal geometry and support-analysis service scaffolds."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SupportRecommendation:
    """Placeholder representation of support-analysis output."""

    needs_supports: bool = False
    recommended_type: str = "none"
    notes: list[str] = field(default_factory=list)


class GeometryProcessor:
    """Placeholder geometry processor for future build123d integration."""

    def __init__(self, overhang_threshold: float = 45.0) -> None:
        self.overhang_threshold = overhang_threshold

    def create_model(self, generated_code: str) -> Any:
        """Return a placeholder geometry result."""
        del generated_code
        return None


class SupportStructureAnalyzer:
    """Placeholder analyzer for future support recommendation logic."""

    def __init__(self, geometry_processor: GeometryProcessor) -> None:
        self.geometry_processor = geometry_processor

    def analyze_support_needs(self, geometry: Any) -> SupportRecommendation:
        """Return a default recommendation until analysis is implemented."""
        del geometry
        return SupportRecommendation()


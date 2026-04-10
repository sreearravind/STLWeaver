"""Minimal LLM manager scaffold."""

from typing import Any


class LLMManager:
    """Manage future prompt-to-code generation providers."""

    SUPPORTED_PROVIDERS: dict[str, list[str]] = {
        "openai": [],
        "anthropic": [],
        "deepseek": [],
        "together": [],
        "local": [],
    }

    async def generate_code(
        self,
        prompt: str,
        provider: str | None = None,
        model: str | None = None,
    ) -> dict[str, Any]:
        """Return a placeholder response for future LLM integration."""
        return {
            "code": None,
            "model_used": model,
            "provider": provider,
            "prompt": prompt,
            "message": "LLM generation is not implemented yet.",
        }


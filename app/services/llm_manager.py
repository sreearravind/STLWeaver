"""Minimal LLM manager scaffold."""

from typing import Any


class LLMManager:
    """Manage future prompt-to-code generation providers."""

    SUPPORTED_PROVIDERS: dict[str, list[str]] = {
        "openai": ["gpt-4.1", "gpt-4o-mini"],
        "anthropic": ["claude-3-5-sonnet"],
        "deepseek": ["deepseek-chat"],
        "together": ["meta-llama/Llama-3.1-8B-Instruct-Turbo"],
        "local": ["placeholder-local-model"],
    }

    def get_supported_providers(self) -> list[dict[str, Any]]:
        """Return lightweight provider metadata for the API."""
        return [
            {"name": name, "models": models, "available": True}
            for name, models in self.SUPPORTED_PROVIDERS.items()
        ]

    async def generate_code(
        self,
        prompt: str,
        provider: str | None = None,
        model: str | None = None,
    ) -> dict[str, Any]:
        """Return a placeholder response for future LLM integration."""
        selected_provider = provider or "openai"
        selected_model = model or self.SUPPORTED_PROVIDERS.get(selected_provider, [None])[0]
        return {
            "code": (
                "from build123d import *\n\n"
                "def create_model():\n"
                "    # Placeholder generated CAD code\n"
                "    return None\n"
            ),
            "model_used": selected_model,
            "provider": selected_provider,
            "prompt": prompt,
            "message": "LLM generation is a placeholder and does not call an external provider yet.",
        }

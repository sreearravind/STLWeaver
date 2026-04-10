"""Application configuration helpers."""

from dataclasses import dataclass
from functools import lru_cache
import os


@dataclass(frozen=True)
class Settings:
    """Minimal application settings loaded from environment variables."""

    app_name: str = "STLWeaver"
    app_version: str = "0.1.0"
    debug: bool = False
    api_prefix: str = ""


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings(
        app_name=os.getenv("STLWEAVER_APP_NAME", "STLWeaver"),
        app_version=os.getenv("STLWEAVER_APP_VERSION", "0.1.0"),
        debug=os.getenv("STLWEAVER_DEBUG", "false").lower() == "true",
        api_prefix=os.getenv("STLWEAVER_API_PREFIX", ""),
    )


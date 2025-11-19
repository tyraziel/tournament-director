"""
API configuration settings.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

from pydantic import BaseModel, Field
from typing import Literal


class APIConfig(BaseModel):
    """Configuration for FastAPI application."""

    # Application
    title: str = "Tournament Director API"
    version: str = "0.1.0"
    debug: bool = True

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True

    # CORS
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    cors_allow_credentials: bool = True

    # Data Layer
    data_backend: Literal["mock", "local", "database"] = "mock"
    local_data_path: str = "./data"

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100


# Global config instance
config = APIConfig()

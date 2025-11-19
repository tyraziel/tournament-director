"""Format data model.

AIA PAI Hin R Claude Code v1.0
AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0 - 2025-11-19 - Added API models
"""

from uuid import UUID

from pydantic import BaseModel, Field

from .base import BaseFormat, GameSystem


class Format(BaseModel):
    """Tournament format definition."""

    id: UUID
    name: str
    game_system: GameSystem
    base_format: BaseFormat
    sub_format: str | None = None
    card_pool: str
    match_structure: str | None = None  # "BO1", "BO3", etc.
    description: str | None = None


class FormatCreate(BaseModel):
    """Format creation request model for API."""

    name: str = Field(..., min_length=1, max_length=100)
    game_system: GameSystem
    base_format: BaseFormat
    sub_format: str | None = None
    card_pool: str = Field(..., min_length=1, max_length=100)
    match_structure: str | None = None
    description: str | None = None


class FormatUpdate(BaseModel):
    """Format update request model for API."""

    name: str | None = Field(None, min_length=1, max_length=100)
    game_system: GameSystem | None = None
    base_format: BaseFormat | None = None
    sub_format: str | None = None
    card_pool: str | None = Field(None, min_length=1, max_length=100)
    match_structure: str | None = None
    description: str | None = None

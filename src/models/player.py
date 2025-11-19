"""Player data model.

AIA PAI Hin R Claude Code v1.0
AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0 - 2025-11-19 - Added API models
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Player(BaseModel):
    """Global player identity across all tournaments."""

    id: UUID
    name: str
    discord_id: str | None = None
    email: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PlayerCreate(BaseModel):
    """Player creation request model for API."""

    name: str = Field(..., min_length=1, max_length=100)
    discord_id: str | None = None
    email: str | None = None


class PlayerUpdate(BaseModel):
    """Player update request model for API."""

    name: str | None = Field(None, min_length=1, max_length=100)
    discord_id: str | None = None
    email: str | None = None

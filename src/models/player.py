"""Player data model.

AIA PAI Hin R Claude Code v1.0
"""

from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, Field


class Player(BaseModel):
    """Global player identity across all tournaments."""

    id: UUID
    name: str
    discord_id: str | None = None
    email: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

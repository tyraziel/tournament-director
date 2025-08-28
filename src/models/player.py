"""Player data model.

AIA PAI Hin R Claude Code v1.0
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class Player(BaseModel):
    """Global player identity across all tournaments."""

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: str,
        }
    )

    id: UUID
    name: str
    discord_id: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

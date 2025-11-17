"""Tournament data models.

AIA PAI Hin R Claude Code v1.0
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .base import PlayerStatus, TournamentStatus, TournamentVisibility


class RegistrationControl(BaseModel):
    """Tournament registration control settings."""

    auto_open_time: Optional[datetime] = None
    auto_close_time: Optional[datetime] = None
    registration_password: Optional[str] = None
    late_registration_password: Optional[str] = None
    allow_to_override: bool = True
    to_override_password: Optional[str] = None
    max_players: Optional[int] = None


class Tournament(BaseModel):
    """Tournament definition and metadata."""

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: str,
        }
    )

    id: UUID
    name: str
    status: TournamentStatus = TournamentStatus.DRAFT
    visibility: TournamentVisibility = TournamentVisibility.PUBLIC
    registration: RegistrationControl
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    format_id: UUID
    venue_id: UUID
    created_by: UUID  # Player ID of tournament organizer
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: Optional[str] = None
    registration_deadline: Optional[datetime] = None
    auto_advance_rounds: bool = False


class TournamentRegistration(BaseModel):
    """Player registration for a tournament."""

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: str,
        }
    )

    id: UUID
    tournament_id: UUID
    player_id: UUID
    sequence_id: int  # Per-tournament player number (#1, #2, #3...)
    status: PlayerStatus = PlayerStatus.ACTIVE
    registration_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    drop_time: Optional[datetime] = None
    notes: Optional[str] = None

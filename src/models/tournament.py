"""Tournament data models.

AIA PAI Hin R Claude Code v1.0
"""

from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, Field

from .base import PlayerStatus, TournamentStatus, TournamentVisibility


class RegistrationControl(BaseModel):
    """Tournament registration control settings."""

    auto_open_time: datetime | None = None
    auto_close_time: datetime | None = None
    registration_password: str | None = None
    late_registration_password: str | None = None
    allow_to_override: bool = True
    to_override_password: str | None = None
    max_players: int | None = None


class Tournament(BaseModel):
    """Tournament definition and metadata."""

    id: UUID
    name: str
    status: TournamentStatus = TournamentStatus.DRAFT
    visibility: TournamentVisibility = TournamentVisibility.PUBLIC
    registration: RegistrationControl
    start_time: datetime | None = None
    end_time: datetime | None = None
    format_id: UUID
    venue_id: UUID
    created_by: UUID  # Player ID of tournament organizer
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    description: str | None = None
    registration_deadline: datetime | None = None
    auto_advance_rounds: bool = False


class TournamentRegistration(BaseModel):
    """Player registration for a tournament."""

    id: UUID
    tournament_id: UUID
    player_id: UUID
    sequence_id: int  # Per-tournament player number (#1, #2, #3...)
    status: PlayerStatus = PlayerStatus.ACTIVE
    registration_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    drop_time: datetime | None = None
    notes: str | None = None

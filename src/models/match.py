"""Match, Round, and Component data models.

AIA PAI Hin R Claude Code v1.0
"""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from .base import ComponentStatus, ComponentType, RoundStatus


class Component(BaseModel):
    """Tournament component (Swiss, Elimination, etc.)."""

    id: UUID
    tournament_id: UUID
    type: ComponentType
    name: str  # "Swiss Rounds", "Top 8", "Pool A"
    sequence_order: int  # Order within tournament (1, 2, 3...)
    status: ComponentStatus = ComponentStatus.PENDING
    config: dict[str, Any]  # Component-specific configuration
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Round(BaseModel):
    """Tournament round within a component."""

    id: UUID
    tournament_id: UUID
    component_id: UUID
    round_number: int
    start_time: datetime | None = None
    end_time: datetime | None = None
    time_limit_minutes: int | None = None
    scheduled_start: datetime | None = None
    scheduled_end: datetime | None = None
    auto_advance: bool = False
    status: RoundStatus = RoundStatus.PENDING


class Match(BaseModel):
    """Individual match between players."""

    id: UUID
    tournament_id: UUID
    component_id: UUID
    round_id: UUID
    round_number: int
    table_number: int | None = None
    player1_id: UUID
    player2_id: UUID | None = None  # None for bye
    player1_wins: int = 0
    player2_wins: int = 0
    draws: int = 0
    start_time: datetime | None = None
    end_time: datetime | None = None
    notes: str | None = None


class MatchResultSubmit(BaseModel):
    """Match result submission request model for API.

    AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
    """

    winner_id: UUID | None = None  # None for draw, otherwise player1_id or player2_id
    player1_wins: int = Field(..., ge=0)
    player2_wins: int = Field(..., ge=0)
    draws: int = Field(default=0, ge=0)
    notes: str | None = None


class StandingsEntry(BaseModel):
    """Single entry in tournament standings response.

    AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
    """

    rank: int
    player_id: UUID
    player_name: str  # Denormalized for convenience
    sequence_id: int  # Player number (#1, #2, etc.)
    match_points: int
    game_points: int
    matches_played: int
    match_win_percentage: float
    game_win_percentage: float
    opponent_match_win_percentage: float
    opponent_game_win_percentage: float

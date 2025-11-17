"""Match, Round, and Component data models.

AIA PAI Hin R Claude Code v1.0
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
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
    config: Dict[str, Any]  # Component-specific configuration
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Round(BaseModel):
    """Tournament round within a component."""

    id: UUID
    tournament_id: UUID
    component_id: UUID
    round_number: int
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    time_limit_minutes: Optional[int] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    auto_advance: bool = False
    status: RoundStatus = RoundStatus.PENDING


class Match(BaseModel):
    """Individual match between players."""

    id: UUID
    tournament_id: UUID
    component_id: UUID
    round_id: UUID
    round_number: int
    table_number: Optional[int] = None
    player1_id: UUID
    player2_id: Optional[UUID] = None  # None for bye
    player1_wins: int = 0
    player2_wins: int = 0
    draws: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    notes: Optional[str] = None

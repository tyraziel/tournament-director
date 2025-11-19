"""
Data models for Swiss tournament calculations.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

from pydantic import BaseModel, Field

from src.models.tournament import TournamentRegistration


class StandingsEntry(BaseModel):
    """Computed standings entry for a player in Swiss tournament."""

    player: TournamentRegistration
    rank: int = 0  # Assigned after sorting

    # Match record
    wins: int = 0
    losses: int = 0
    draws: int = 0
    match_points: int = 0  # 3 per win, 1 per draw

    # Game record
    game_wins: int = 0
    game_losses: int = 0
    game_draws: int = 0

    # Tiebreakers (calculated values)
    tiebreakers: dict[str, float] = Field(default_factory=dict)

    # Metadata
    matches_played: int = 0
    bye_count: int = 0
    opponents_faced: list[str] = Field(default_factory=list)  # List of opponent player_id strings


class MatchResult(BaseModel):
    """Match result summary for a specific player."""

    player_id: str
    opponent_id: str | None  # None for bye
    player_wins: int
    opponent_wins: int
    draws: int
    is_bye: bool = False

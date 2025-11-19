"""
Swiss tournament system implementation.

Provides pairing algorithms, standings calculations, and tiebreaker logic
for Swiss-system tournaments.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

from .models import StandingsEntry
from .pairing import generate_bye_losses_for_late_entry, pair_round, pair_round_1
from .standings import calculate_standings
from .tiebreakers import (
    calculate_game_win_percentage,
    calculate_match_win_percentage,
    calculate_opponent_game_win_percentage,
    calculate_opponent_match_win_percentage,
)

__all__ = [
    "StandingsEntry",
    "calculate_match_win_percentage",
    "calculate_game_win_percentage",
    "calculate_opponent_match_win_percentage",
    "calculate_opponent_game_win_percentage",
    "calculate_standings",
    "pair_round_1",
    "pair_round",
    "generate_bye_losses_for_late_entry",
]

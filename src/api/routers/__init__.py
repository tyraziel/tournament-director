"""
API routers package.

AIA EAI Hin R Claude Code [Sonnet 4.5] v1.0
"""

from . import formats, health, matches, players, registrations, rounds, tournaments, venues

__all__ = [
    "health",
    "players",
    "venues",
    "formats",
    "tournaments",
    "registrations",
    "rounds",
    "matches",
]

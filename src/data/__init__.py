"""Data layer abstraction for Tournament Director.

AIA PAI Hin R Claude Code v1.0
"""

from .exceptions import (
    DataLayerError,
    DuplicateError,
    IntegrityError,
    NotFoundError,
    ValidationError,
)
from .interface import (
    ComponentRepository,
    DataLayer,
    FormatRepository,
    MatchRepository,
    PlayerRepository,
    RegistrationRepository,
    RoundRepository,
    TournamentRepository,
    VenueRepository,
)

__all__ = [
    # Core interface
    "DataLayer",

    # Repository interfaces
    "PlayerRepository",
    "VenueRepository",
    "FormatRepository",
    "TournamentRepository",
    "RegistrationRepository",
    "ComponentRepository",
    "RoundRepository",
    "MatchRepository",

    # Exceptions
    "DataLayerError",
    "NotFoundError",
    "DuplicateError",
    "ValidationError",
    "IntegrityError",
]

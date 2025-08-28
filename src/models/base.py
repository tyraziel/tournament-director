"""Base types and enums for Tournament Director data models.

AIA PAI Hin R Claude Code v1.0
"""

from enum import Enum


class GameSystem(str, Enum):
    """Supported Trading Card Game systems."""

    MTG = "magic_the_gathering"
    POKEMON = "pokemon"
    STAR_WARS_UNLIMITED = "star_wars_unlimited"
    NFL_FIVE = "nfl_five"
    CUSTOM = "custom_tcg"


class BaseFormat(str, Enum):
    """Base format categories for tournament play."""

    CONSTRUCTED = "constructed"  # Build your own deck from card pool
    PRE_CONSTRUCTED = "pre_constructed"  # Use provided/official decks
    LIMITED = "limited"  # Draft/Sealed from packs
    SPECIAL = "special"  # JumpStart, Cube, house rules


class TournamentStatus(str, Enum):
    """Tournament lifecycle states."""

    DRAFT = "draft"  # Being set up
    REGISTRATION_OPEN = "registration_open"  # Players can register
    REGISTRATION_CLOSED = "registration_closed"  # No new players
    IN_PROGRESS = "in_progress"  # Tournament running
    COMPLETED = "completed"  # Finished
    CANCELLED = "cancelled"  # Terminated early


class TournamentVisibility(str, Enum):
    """Tournament access control."""

    PUBLIC = "public"  # Visible to all, may require password
    PRIVATE = "private"  # Invitation only


class PlayerStatus(str, Enum):
    """Player participation status in a tournament."""

    ACTIVE = "active"
    DROPPED = "dropped"
    LATE_ENTRY = "late_entry"


class ComponentType(str, Enum):
    """Types of tournament components."""

    SWISS = "swiss"
    SINGLE_ELIMINATION = "single_elimination"
    ROUND_ROBIN = "round_robin"
    POOL_PLAY = "pool_play"


class ComponentStatus(str, Enum):
    """Component lifecycle states."""

    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"


class RoundStatus(str, Enum):
    """Round lifecycle states."""

    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
